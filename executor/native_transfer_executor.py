import os
import logging

from executor import BaseExecutor

class NativeTransferExecutor(BaseExecutor):
    def __init__(self, rpc, operator_sk, amount):
        super().__init__(rpc, operator_sk)
        self.amount = amount

    def execute(self, data):
        self.logger.info(f"Sending {self.amount} to {data['to']}")

        tx = self.w3.eth.send_transaction({
            'from': self.operator.address,
            'to': data['to'],
            'value': self.w3.to_wei(self.amount, 'ether')
        })
        tx_receipt=self.w3.eth.wait_for_transaction_receipt(tx)
        self.logger.info(f"Transaction hash: {tx_receipt['transactionHash'].hex()} Status {tx_receipt['status']}")
        return tx