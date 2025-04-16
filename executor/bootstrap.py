import os
import logging
from web3 import Web3

from executor import BaseExecutor

class Bootstrapper(BaseExecutor):
    def __init__(self, rpc, operator_sk, erc20_address, erc20_abi, wallets, slack=None):
        super().__init__(rpc, operator_sk)
        self.erc20 = self.w3.eth.contract(address=Web3.to_checksum_address(erc20_address), abi=erc20_abi)

        self.wallets = wallets
        self.slack = slack

    def execute(self, data):
        self.logger.info(f"Bootstrapping {data}")
        if data['type'] == 'native':
            return self.fund_native(data['amount'])
        elif data['type'] == 'erc20':
            return self.fund_erc20(data['amount'])
        
        if self.slack:
            self.slack.send_message(f"Bootstrapping {data['type']} with amount {data['amount']} has completed.")
            
    def fund_native(self, amount):
        for to in self.wallets:
            self.logger.info(f"Sending {amount} to {to['address']}")

            tx = self.w3.eth.send_transaction({
                'from': self.operator.address,
                'to': to['address'],
                'value': self.w3.to_wei(amount, 'ether')
            })
            tx_receipt=self.w3.eth.wait_for_transaction_receipt(tx)
            self.logger.info(f"Transaction hash: 0x{tx_receipt['transactionHash'].hex()} Status {tx_receipt['status']}")
        
    
    def fund_erc20(self, amount):
        for to in self.wallets:
            self.logger.info(f"Sending {amount} to {to['address']}")

            tx = self.erc20.functions.transfer(to['address'], self.w3.to_wei(amount, 'ether')).transact()
            tx_receipt=self.w3.eth.wait_for_transaction_receipt(tx)
            self.logger.info(f"Transaction hash: 0x{tx_receipt['transactionHash'].hex()} Status {tx_receipt['status']}")            