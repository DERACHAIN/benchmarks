import os
from web3 import Web3
from eth_account import Account
#from web3.middleware.signing import construct_sign_and_send_raw_middleware
import json
import logging

from generator import WalletGenerator
from executor import NativeTransferExecutor, Bootstrapper

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    # create wallets
    #generate_wallets()
    #wg = WalletGenerator()
    #wg.generate_wallets()

    # bootstrap
    bootstrapper = Bootstrapper(os.environ.get('RPC_ENDPOINT'), os.environ.get('PRIVATE_KEY'), 1)
    # with open('wallets.json') as file:
    #     wallets = json.load(file)
    #     for wallet in wallets:
    #         bootstrapper.execute({'to': wallet['address']})

    # native transfer
    with open('wallets.json') as file:
        wallets = json.load(file)
        executor = NativeTransferExecutor(os.environ.get('RPC_ENDPOINT'), os.environ.get('PRIVATE_KEY'), wallets[:300], 10000)
        executor.execute({'amount': 0.01})