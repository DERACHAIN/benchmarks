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
    parser.add_argument('-b', '--balance', type=float, help="Initial balance of wallets", default=10)
    parser.add_argument('-n', '--number', type=int, help="Number of wallets", default=100)
    parser.add_argument('-t', '--tx', type=int, help="Number of tx", default=10**6)

    args = parser.parse_args()

    if args.action == 'generate_wallets':
        wg = WalletGenerator()
        wg.generate_wallets()
    elif args.action == 'bootstrap':        
        bootstrapper = Bootstrapper(os.environ.get('RPC_ENDPOINT'), os.environ.get('PRIVATE_KEY'), args.balance)
        with open('wallets.json') as file:
            wallets = json.load(file)
            for wallet in wallets:
                bootstrapper.execute({'to': wallet['address']})
    elif args.action == 'native_transfer':        
        with open('wallets.json') as file:
            wallets = json.load(file)
            executor = NativeTransferExecutor(os.environ.get('RPC_ENDPOINT'), os.environ.get('PRIVATE_KEY'), wallets[:args.number], args.tx)
            executor.execute({'amount': 0.01})
    
    logging.info(f"Action {args.action} completed")