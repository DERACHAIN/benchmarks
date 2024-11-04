import os
import logging
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from executor import BaseExecutor

class NativeTransferExecutor(BaseExecutor):
    def __init__(self, rpc, operator_sk, wallets, total_tx=10**5):
        super().__init__(rpc, operator_sk)
        self.w3 = Web3(Web3.HTTPProvider(rpc))
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.wallets = wallets
        self.total_tx = total_tx

    def execute(self, data):
        self.amount = data['amount']

        import concurrent.futures

        def transfer(wallet, index):
            to = self.wallets[(index + 1) % len(self.wallets)]['address']
            self.logger.info(f"Transfer {self.amount} from {wallet['address']} to {to}")

            account = self.w3.eth.account.from_key(wallet['private_key'])
            #self.logger.info(f"Account: {account.address} with nonce {self.w3.eth.get_transaction_count(account.address)}")

            signed = self.w3.eth.account.sign_transaction({
                'from': wallet['address'],
                'to': to,
                'value': self.w3.to_wei(self.amount, 'ether'),
                'gas': 21000,
                'gasPrice': self.w3.to_wei('50', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'chainId': self.w3.eth.chain_id,
            }, account._private_key)

            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            return f"Transfer {self.amount} from {wallet['address']} to {to} with tx hash {tx_hash.hex()}"

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.wallets)) as executor:
            if self.total_tx > 0:
                self.logger.warning(f"Total transactions remained: {self.total_tx}")
                futures = [executor.submit(transfer, wallet, index) for index, wallet in enumerate(self.wallets)]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        self.logger.info(f"Transfer result: {result}")
                        self.total_tx -= 1
                    except Exception as e:
                        self.logger.error(f"Transfer failed: {e}")
                        self.total_tx -= 1