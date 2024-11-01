from library import Singleton
from eth_account import Account
import json

class WalletGenerator(metaclass=Singleton):
    def __init__(self):
        self.wallets = []

#     def generate_ethereum_wallets(self, num_wallets):
#         wallets = []
#         for _ in range(num_wallets):
#             account = Account.create()
#             wallets.append({
#                 'address': account.address,
#                 'private_key': account.key.hex()
#             })
#         return wallets
    
#     def save_wallets_to_file(self, wallets, filename='wallets.json'):
#         with open(filename, 'w') as file:
#             json.dump(wallets, file, indent=4)

#     def generate_wallets(self):
#         num_wallets = int(input("Enter the number of Ethereum wallets to generate: "))
#         wallets = self.generate_ethereum_wallets(num_wallets)
#         self.save_wallets_to_file(wallets)
#         print(f"{num_wallets} Ethereum wallets have been generated and saved to wallets.json")