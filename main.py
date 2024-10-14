import os
from web3 import Web3
from eth_account import Account
from web3.middleware.signing import construct_sign_and_send_raw_middleware
import json
import logging

def generate_ethereum_wallets(num_wallets):
    wallets = []
    for _ in range(num_wallets):
        account = Account.create()
        wallets.append({
        'address': account.address,
        'private_key': account.key.hex()
        })
    return wallets

def save_wallets_to_file(wallets, filename='wallets.json'):
    with open(filename, 'w') as file:
        json.dump(wallets, file, indent=4)

def generate_wallets():
    num_wallets = int(input("Enter the number of Ethereum wallets to generate: "))
    wallets = generate_ethereum_wallets(num_wallets)
    save_wallets_to_file(wallets)
    print(f"{num_wallets} Ethereum wallets have been generated and saved to wallets.json")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    w3 = Web3(Web3.HTTPProvider(os.environ.get('RPC_ENDPOINT')))
    operator = w3.eth.account.from_key(os.environ.get('PRIVATE_KEY'))
    #w3.middleware_onion.add(construct_sign_and_send_raw_middleware(operator))
    #w3.eth.default_account = operator.address

    print(f"Operator address: {operator.address}")

    #generate_wallets()