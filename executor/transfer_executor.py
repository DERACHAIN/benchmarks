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
    def __init__(self, rpc, operator_sk, erc20_address, erc721_address, erc20_abi, erc721_abi, wallets, max_workers=10):
        super().__init__(rpc, operator_sk)

        self.erc20 = self.w3.eth.contract(address=Web3.to_checksum_address(erc20_address), abi=erc20_abi)
        self.erc721 = self.w3.eth.contract(address=Web3.to_checksum_address(erc721_address), abi=erc721_abi)

        self.wallets = [self.create_wallet(wallet) for wallet in wallets]
        self.max_workers = max_workers

    def create_wallet(self, wallet):
        return self.w3.eth.account.from_key(wallet['private_key'])

    def execute(self, amount_native, amount_erc20, start_index=0):
        import concurrent.futures

        def transfer(wallet, index):
            account = wallet
            to = self.wallets[(index + 1) % len(self.wallets)]
        
            random_value = random.randint(1, 3)
            #self.logger.info(f"Random value: {random_value}")
            try:
                signed = None

                if random_value == 1:
                    signed = self.w3.eth.account.sign_transaction({
                        'from': account.address,
                        'to': to.address,
                        'value': self.w3.to_wei(amount_native, 'ether'),
                        'gas': 23000,
                        'gasPrice': self.w3.to_wei('35', 'gwei'),
                        'nonce': self.w3.eth.get_transaction_count(account.address),
                        'chainId': self.w3.eth.chain_id,
                    }, account._private_key)

                if random_value == 2:
                    tx = self.erc20.functions.transfer(to.address, self.w3.to_wei(amount_erc20, 'ether')).build_transaction({
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

                if signed is not None:
                    tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
                    tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
                    return {
                        "transfer_type": random_value,
                        "from": account.address,
                        "to": to.address,
                        "amount": amount_native if random_value == 1 else amount_erc20 if random_value == 2 else 1,
                        "tx_hash": tx_hash.hex(),
                        "status": tx_receipt['status'],
                    }
                else:
                    raise Exception("Transaction signing failed")
            except Exception as e:
                self.logger.error(f"Error during transfer: {e}")
                
                return {
                    "transfer_type": random_value,
                    "from": account.address,
                    "to": to.address,
                    "amount": amount_native if random_value == 1 else amount_erc20 if random_value == 2 else 1,
                    "status": 0,
                }

        number_success = 0
        number_failed = 0

        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.logger.warning(f"Transfer execution started at {start_time}")        

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            from_index = start_index if start_index < len(self.wallets)-1 else 0
            to_index = from_index + self.max_workers if from_index + self.max_workers < len(self.wallets)-1 else len(self.wallets)-1

            futures = [executor.submit(transfer, wallet, index) for index, wallet in enumerate(self.wallets[from_index:to_index])]

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    self.logger.info(f"Transfer result: {result}")

                    if result['status'] == 1:
                        number_success += 1
                    else:
                        raise Exception(f"Transaction failed {result}")
                except Exception as e:
                    self.logger.info(f"{e}")
                    number_failed += 1                            

            if number_failed > number_success:
                self.logger.error(f"Number failed {number_failed} > number success {number_success}.")
                                
        elapsed_time = time.time() - time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
        self.logger.warning(f"Total {self.max_workers} txs. Number success {number_success}. Number failed {number_failed}. Elapsed time: {elapsed_time:.3f} seconds")

        return number_success, number_failed

        