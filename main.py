import os
from web3 import Web3
from eth_account import Account
#from web3.middleware.signing import construct_sign_and_send_raw_middleware
import json
import logging

from generator import WalletGenerator

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    w3 = Web3(Web3.HTTPProvider(os.environ.get('RPC_ENDPOINT')))
    operator = w3.eth.account.from_key(os.environ.get('PRIVATE_KEY'))
    #w3.middleware_onion.add(construct_sign_and_send_raw_middleware(operator))
    #w3.eth.default_account = operator.address

    #print(f"Operator address: {operator.address}")

    #generate_wallets()
    wg = WalletGenerator()
    wg.generate_wallets()