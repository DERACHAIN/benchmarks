from web3 import Web3
from eth_account import Account
import json

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

if __name__ == "__main__":
  num_wallets = int(input("Enter the number of Ethereum wallets to generate: "))
  wallets = generate_ethereum_wallets(num_wallets)
  save_wallets_to_file(wallets)
  print(f"{num_wallets} Ethereum wallets have been generated and saved to wallets.json")