import asyncio
import sys
import logging
import json
import time
import multiprocessing

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware, SignAndSendRawMiddlewareBuilder

from library import Singleton
from helpers import SlackNotifier
from executor import TransferExecutor, BaseExecutor
from config import Config

ALERT_BASE_INTERVAL = 5*60  # 5 mins
MONITOR_INTERVAL = 15

class Monitor(BaseExecutor):
    def __init__(self, wallets, config: Config):
        super().__init__(config.rpc, config.operator_sk)

        self.config = config

        self.erc20 = self.w3.eth.contract(address=Web3.to_checksum_address(config.erc20_address), abi=config.erc20_abi)
        self.erc721 = self.w3.eth.contract(address=Web3.to_checksum_address(config.erc721_address), abi=config.erc721_abi)

        self.wallets = [self.w3.eth.account.from_key(wallet['private_key']) for wallet in wallets]
        self.slack = SlackNotifier(config.slack_webhook_url) if config.slack_webhook_url else None

    def fund_gas(self, to, amount):
        try:
            tx = self.w3.eth.send_transaction({
                'from': self.operator.address,
                'to': to.address,
                'value': self.w3.to_wei(amount, 'ether'),
            })

            receipt = self.w3.eth.wait_for_transaction_receipt(tx)

            return {'tx_hash': tx, 'status': receipt.status}        
        except Exception as e:
            logging.warning(f"Error funding gas: {e}")
            return {'tx_hash': '', 'status': 0}
    
    def fund_erc20(self, to, amount):
        try:
            tx = self.erc20.functions.transfer(to.address, self.w3.to_wei(amount, 'ether')).transact()

            receipt = self.w3.eth.wait_for_transaction_receipt(tx)

            return {'tx_hash': tx, 'status': receipt.status}        
        except Exception as e:
            logging.warning(f"Error funding ERC20: {e}")
            return {'tx_hash': '', 'status': 0}


    def run(self):
        logging.warning("Starting monitor...")

        is_alert_native = False
        next_alert_time_native = 0
        backoff_factor_native = 0

        is_alert_erc20 = False
        next_alert_time_erc20 = 0
        backoff_factor_erc20 = 0

        try:
            while True:
                # wallets fund
                for wallet in self.wallets:

                    if not is_alert_native:
                        balance = self.w3.eth.get_balance(wallet.address)
                        balance_eth = self.w3.from_wei(balance, 'ether')

                        if balance_eth < self.config.native_balance_threshold:
                            logging.warning(f"Wallet {wallet.address} balance: {balance_eth} < threshold {self.config.native_balance_threshold}.")

                            result = self.fund_gas(wallet, self.config.native_balance_threshold)
                            logging.info(f"Funded wallet {wallet.address} with {self.config.native_balance_threshold} DERA. Tx hash: {result['tx_hash']}. Status: {result['status']}")

                    if not is_alert_erc20:
                        balance_erc20 = self.erc20.functions.balanceOf(wallet.address).call()
                        balance_erc20_eth = self.w3.from_wei(balance_erc20, 'ether')

                        if balance_erc20_eth < self.config.erc20_balance_threshold:
                            logging.warning(f"Wallet {wallet.address} ERC20 balance: {balance_erc20_eth} < threshold {self.config.erc20_balance_threshold}.")

                            result = self.fund_erc20(wallet, self.config.erc20_balance_threshold)
                            logging.info(f"Funded wallet {wallet.address} with {self.config.erc20_balance_threshold} ERC20 TOKEN. Tx hash: {result['tx_hash']}. Status: {result['status']}")
                
                # operator fund
                operator_balance = self.w3.eth.get_balance(self.operator.address)
                operator_balance_eth = self.w3.from_wei(operator_balance, 'ether')

                if operator_balance_eth < self.config.native_balance_threshold * len(self.wallets):

                    if not is_alert_native:
                        is_alert_native = True
                        next_alert_time_native = time.time() + ALERT_BASE_INTERVAL

                        self.slack.send_message("Operator DERA-balance", f"Operator balance: {operator_balance_eth} < threshold {self.config.native_balance_threshold * len(self.wallets)} DERA. Should be funded prompty.", is_success=False)

                    elif time.time() > next_alert_time_native:
                        backoff_factor_native += 1
                        next_alert_time_native = time.time() + ALERT_BASE_INTERVAL * (2**backoff_factor_native)

                        self.slack.send_message("Operator DERA-balance", f"Operator balance: {operator_balance_eth} < threshold {self.config.native_balance_threshold * len(self.wallets)} DERA. Should be funded prompty.", is_success=False)

                    logging.warning(f"Operator {self.operator.address} balance: {operator_balance_eth} < threshold {self.config.native_balance_threshold * len(self.wallets)}. Next time alert at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_alert_time_native))}")
                else:
                    if is_alert_native:
                        is_alert_native = False
                        next_alert_time_native = 0
                        backoff_factor_native = 0

                        self.slack.send_message("Operator DERA-balance", f"Operator DERA balance is back to normal")

                # operator erc20 fund
                operator_balance_erc20 = self.erc20.functions.balanceOf(self.operator.address).call()
                operator_balance_erc20_eth = self.w3.from_wei(operator_balance_erc20, 'ether')

                if operator_balance_erc20_eth < self.config.erc20_balance_threshold * len(self.wallets):
                    if not is_alert_erc20:
                        is_alert_erc20 = True
                        next_alert_time_erc20 = time.time() + ALERT_BASE_INTERVAL

                        self.slack.send_message("Operator ERC20-balance", f"Operator ERC20 balance: {operator_balance_erc20_eth} < threshold {self.config.erc20_balance_threshold * len(self.wallets)} ERC20. Should be funded prompty.", is_success=False)

                    elif time.time() > next_alert_time_erc20:
                        backoff_factor_erc20 += 1
                        next_alert_time_erc20 = time.time() + ALERT_BASE_INTERVAL * (2**backoff_factor_erc20)

                        self.slack.send_message("Operator ERC20-balance", f"Operator ERC20 balance: {operator_balance_erc20_eth} < threshold {self.config.erc20_balance_threshold * len(self.wallets)} ERC20. Should be funded prompty.", is_success=False)

                    logging.warning(f"Operator {self.operator.address} ERC20 balance: {operator_balance_erc20_eth} < threshold {self.config.erc20_balance_threshold * len(self.wallets)}. Next time alert at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_alert_time_erc20))}")
                else:
                    if is_alert_erc20:
                        is_alert_erc20 = False
                        next_alert_time_erc20 = 0
                        backoff_factor_erc20 = 0

                        self.slack.send_message("Operator ERC20-balance", f"Operator ERC20 balance is back to normal")                

                time.sleep(MONITOR_INTERVAL)

        except KeyboardInterrupt:
            logging.warning("Monitor interrupted by user")

            if self.slack:
                self.slack.send_message("Monitor", "Monitor server interrupted by user")

            sys.exit(0)