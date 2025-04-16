import os
import logging
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from executor import BaseExecutor
import time
import random
import signal
import sys

class TransferExecutor(BaseExecutor):
    def __init__(self, rpc, operator_sk, erc20_address, erc721_address, erc20_abi, erc721_abi, wallets, slack=None):
        super().__init__(rpc, operator_sk)

        self.w3 = Web3(Web3.HTTPProvider(rpc))
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        self.erc20 = self.w3.eth.contract(address=Web3.to_checksum_address(erc20_address), abi=erc20_abi)
        self.erc721 = self.w3.eth.contract(address=Web3.to_checksum_address(erc721_address), abi=erc721_abi)

        self.wallets = [self.create_wallet(wallet) for wallet in wallets]

        self.slack = slack

    def create_wallet(self, wallet):
        return self.w3.eth.account.from_key(wallet['private_key'])

    def execute(self, data):
        import concurrent.futures

        def transfer(wallet, index, max_workers):
            account = wallet
            to = self.wallets[:max_workers][(index + 1) % max_workers]
        
            random_value = random.randint(1, 3)
            #self.logger.info(f"Random value: {random_value}")
            try:
                signed = None

                if random_value == 1:
                    signed = self.w3.eth.account.sign_transaction({
                        'from': account.address,
                        'to': to.address,
                        'value': self.w3.to_wei(data['amount_native'], 'ether'),
                        'gas': 23000,
                        'gasPrice': self.w3.to_wei('35', 'gwei'),
                        'nonce': self.w3.eth.get_transaction_count(account.address),
                        'chainId': self.w3.eth.chain_id,
                    }, account._private_key)

                if random_value == 2:
                    tx = self.erc20.functions.transfer(to.address, self.w3.to_wei(data['amount_erc20'], 'ether')).build_transaction({
                        'from': account.address,                    
                        'gas': 150000,
                        'gasPrice': self.w3.to_wei('35', 'gwei'),
                        'nonce': self.w3.eth.get_transaction_count(account.address),
                        'chainId': self.w3.eth.chain_id,
                    })
                    signed = self.w3.eth.account.sign_transaction(tx, account._private_key)

                elif random_value == 3:
                    tx = self.erc721.functions.mint().build_transaction({
                        'from': account.address,                    
                        'gas': 100000,
                        'gasPrice': self.w3.to_wei('35', 'gwei'),
                        'nonce': self.w3.eth.get_transaction_count(account.address),
                        'chainId': self.w3.eth.chain_id,
                    })
                    signed = self.w3.eth.account.sign_transaction(tx, account._private_key)

                if signed is None:
                    tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
                    tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
                    return {
                        "transfer_type": random_value,
                        "from": account.address,
                        "to": to.address,
                        "amount": data['amount_native'] if random_value == 1 else data['amount_erc20'] if random_value == 2 else 1,
                        "tx_hash": tx_hash.hex(),
                        "status": tx_receipt['status'],
                    }
            except Exception as e:
                self.logger.error(f"Error during transfer: {e}")
                
                return {
                    "transfer_type": random_value,
                    "from": account.address,
                    "to": to.address,
                    "amount": data['amount_native'] if random_value == 1 else data['amount_erc20'] if random_value == 2 else 1,
                    "status": 0,
                }

        tx_number = 0
        max_workers = len(self.wallets)

        slack_title = "Bots activity"
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.logger.warning(f"Transfer execution started at {start_time}")

        try:
            while True:
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

                    futures = [executor.submit(transfer, wallet, index, max_workers) for index, wallet in enumerate(self.wallets[:max_workers])]
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            result = future.result()
                            self.logger.info(f"Transfer result: {result}")

                            if result['status'] == 1:
                                tx_number += 1
                            else:
                                raise Exception(f"Transaction failed {result}")
                        except Exception as e:
                            self.logger.error(f"{e}")
                            max_workers -= 1

                            if max_workers <= 0:
                                self.logger.error("All workers failed. Exiting.")

                                if self.slack:
                                    self.slack.send_message(slack_title, f"All workers failed. Exiting. Total transactions: {tx_number}", is_success=False)
                                    
                                sys.exit(1)
                    
                    elapsed_time = time.time() - time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
                    self.logger.warning(f"Complete {tx_number} txs. Elapsed time: {elapsed_time:.3f} seconds")

        except KeyboardInterrupt:
            self.logger.warning(f"Transfer execution interrupted by user. Total transactions: {tx_number}")

            if self.slack:
                self.slack.send_message(slack_title, f"Transfer execution interrupted by user. Total transactions: {tx_number}")

            sys.exit(0)

        