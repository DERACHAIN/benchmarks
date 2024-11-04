import os
import json
import logging
import argparse

from generator import WalletGenerator
from executor import NativeTransferExecutor, Bootstrapper


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(filename='logs.txt', level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description='Benchmark bot.')    
    parser.add_argument('-a', '--action', type=str, help="Actions: generate_wallets | bootstrap | native_transfer")

    args = parser.parse_args()

    if args.action == 'generate_wallets':
        wg = WalletGenerator()
        wg.generate_wallets()
    elif args.action == 'bootstrap':
        bootstrapper = Bootstrapper(os.environ.get('RPC_ENDPOINT'), os.environ.get('PRIVATE_KEY'), 10)
        with open('wallets.json') as file:
            wallets = json.load(file)
            for wallet in wallets:
                bootstrapper.execute({'to': wallet['address']})
    elif args.action == 'native_transfer':        
        with open('wallets.json') as file:
            wallets = json.load(file)
            executor = NativeTransferExecutor(os.environ.get('RPC_ENDPOINT'), os.environ.get('PRIVATE_KEY'), wallets[:1000], 10**6)
            executor.execute({'amount': 0.01})