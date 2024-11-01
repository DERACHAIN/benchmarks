import os
import logging

from executor import BaseExecutor

class NativeTransferExecutor(BaseExecutor):
    def __init__(self, rpc, operator_sk, wallets):
        super().__init__(rpc, operator_sk)
        self.wallets = wallets

    def execute(self, data):
        self.amount = data['amount']

        import concurrent.futures

        def transfer(wallet, index):
            to = self.wallets[(index + 1) % len(self.wallets)]['address']

            tx = self.w3.eth.send_transaction({
                'from': wallet['address'],
                'to': to,
                'value': self.w3.to_wei(self.amount, 'ether')
            })
            signed = self.w3.eth.account.sign_transaction(tx, wallet['private_key'])
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            
            return f"Transfer {self.amount} from {wallet['address']} to {to} with tx hash {tx_hash.hex()}"

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.wallets)) as executor:
            futures = [executor.submit(transfer, wallet, index) for index, wallet in enumerate(self.wallets)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    self.logger.info(f"Transfer result: {result}")
                except Exception as e:
                    self.logger.error(f"Transfer failed: {e}")