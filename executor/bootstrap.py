import os
import logging

from executor import BaseExecutor

class Bootstrapper(BaseExecutor):
    def __init__(self, rpc, operator_sk):
        super().__init__(rpc, operator_sk)

    def execute(self, data):
        self.logger.info(f"Bootstrapping {data}")
        if data['type'] == 'native':
            return self.fund_native(data['to'], data['amount'])
        elif data['type'] == 'erc20':
            return self.fund(data)
            
    def fund_native(self, to, amount):
        self.logger.info(f"Sending {amount} to {to}")

        tx = self.w3.eth.send_transaction({
            'from': self.operator.address,
            'to': to,
            'value': self.w3.to_wei(self.amount, 'ether')
        })
        tx_receipt=self.w3.eth.wait_for_transaction_receipt(tx)
        self.logger.info(f"Transaction hash: {tx_receipt['transactionHash'].hex()} Status {tx_receipt['status']}")
        return tx
    
    def fund_erc20(self, to, amount):
        self.logger.info(f"Sending {amount} to {to}")

        tx = self.erc20_contract.functions.transfer(to, amount).transact({'from': self.operator.address})