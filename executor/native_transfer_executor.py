import os
import logging
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from executor import BaseExecutor
import time

class NativeTransferExecutor(BaseExecutor):
    def __init__(self, rpc, operator_sk, wallets, total_tx=10**5):
        super().__init__(rpc, operator_sk)
        self.w3 = Web3(Web3.HTTPProvider(rpc))
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.wallets = [self.create_wallet(wallet) for wallet in wallets]
        self.total_tx = total_tx

    def create_wallet(self, wallet):
        return self.w3.eth.account.from_key(wallet['private_key'])

    def execute(self, data):
        self.amount = data['amount']

        import concurrent.futures

        def transfer(wallet, index):
            account = self.wallets[index]
            to = self.wallets[(index + 1) % len(self.wallets)]
            #self.logger.info(f"Transfer {self.amount} from {account.address} to {to.address}")
            #account = self.w3.eth.account.from_key(wallet['private_key'])
            #self.logger.info(f"Account: {account.address} with nonce {self.w3.eth.get_transaction_count(account.address)}")

            signed = self.w3.eth.account.sign_transaction({
                'from': account.address,
                'to': to.address,
                'value': self.w3.to_wei(self.amount, 'ether'),
                'gas': 23000,
                'gasPrice': self.w3.to_wei('50', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'chainId': self.w3.eth.chain_id,
            }, account._private_key)

            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return f"Transfer {self.amount} from {account.address} to {to.address} with tx hash {tx_hash.hex()} status {tx_receipt['status']}"

        tx_number = self.total_tx
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.logger.warning(f"Transfer execution started at {start_time}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.wallets)) as executor:
            while self.total_tx > 0:
                self.logger.warning(f"Total transactions remained: {self.total_tx}")
                if tx_number - self.total_tx > 0:
                    elapsed_time = time.time() - time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
                    self.logger.warning(f"Complete {len(self.wallets)} tx. Elapsed time: {elapsed_time:.3f} seconds")
                    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

                futures = [executor.submit(transfer, wallet, index) for index, wallet in enumerate(self.wallets)]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        #self.logger.info(f"Transfer result: {result}")
                        self.total_tx -= 1
                    except Exception as e:
                        self.logger.error(f"Transfer failed: {e}")
                        self.total_tx -= 1
        end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        elapsed_time = time.time() - time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
        self.logger.warning(f"Transfer execution ended at {end_time}")
        self.logger.warning(f"Complete {tx_number} tx in {elapsed_time:.3f} seconds")
