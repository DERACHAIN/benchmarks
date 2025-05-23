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


RETRY_BASE_INTERVAL = 15*60  # 15 mins

class Server(BaseExecutor):
    def __init__(self, wallets, config: Config):
        super().__init__(config.rpc, config.operator_sk)

        self.slack = SlackNotifier(config.slack_webhook_url) if config.slack_webhook_url else None

        self.executor = TransferExecutor(
            config.rpc,
            config.operator_sk,
            config.erc20_address,
            config.erc721_address,
            config.erc20_abi,
            config.erc721_abi,
            wallets,
            config.max_workers,
        )

        self.max_workers = config.max_workers


    async def execute(self, amount_native, amount_erc20):
        logging.warning("Starting execution...")

        tx_number = 0
        slack_title = "Execution"

        backoff_factor = 0
        is_alert = False
        next_alert_time = 0

        start_index = 0

        try:
            while True:
                start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                logging.warning(f"Transfer execution started at {start_time} with {self.max_workers} workers and process wallets #{start_index * self.max_workers} to #{(start_index +1) * self.max_workers - 1}")

                number_success, number_failed = self.executor.execute(amount_native, amount_erc20, start_index * self.max_workers)
                tx_number += number_success

                if number_failed > number_success:

                    if not is_alert:
                        is_alert = True
                        next_alert_time = time.time() + RETRY_BASE_INTERVAL

                        self.slack.send_message(slack_title, f"Number failed {number_failed} > number success {number_success}. Retry at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_alert_time))}", is_success=False)

                    elif time.time() > next_alert_time:
                        backoff_factor += 1
                        next_alert_time = time.time() + RETRY_BASE_INTERVAL * (2**backoff_factor)

                        self.slack.send_message(slack_title, f"Number failed {number_failed} > number success {number_success}. Retry at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_alert_time))}", is_success=False)

                    logging.error(f"Number failed {number_failed} > number success {number_success}. Retry at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_alert_time))}")

                    await asyncio.sleep(RETRY_BASE_INTERVAL * (2**backoff_factor))
                else:
                    if is_alert:
                        is_alert = False
                        next_alert_time = 0
                        backoff_factor = 0

                        self.slack.send_message(slack_title, f"Execution is back to normal")
                    

                    elapsed_time = time.time() - time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
                    logging.warning(f"Total {tx_number} txs. Number success {number_success}. Number failed {number_failed}. Elapsed time: {elapsed_time:.3f} seconds")

                start_index = start_index + 1 if (start_index + 1) * self.max_workers < len(self.executor.wallets) else 0

        except KeyboardInterrupt:
            logging.warning(f"Execution server interrupted by user. Total transactions: {tx_number}")

            if self.slack:
                self.slack.send_message(slack_title, f"Execution server interrupted by user. Total transactions: {tx_number}")

            sys.exit(0)
        
    def run(self, amount_native=0.1, amount_erc20=10):
        logging.warning("Starting server...")


        slack_title = "Server"
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        logging.warning(f"Benchmarks server started at {start_time}")
        self.slack.send_message(slack_title, f"Benchmarks server started at {start_time}")

        asyncio.run(self.execute(amount_native, amount_erc20))