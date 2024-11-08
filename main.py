import os
import json
import logging
import argparse

from generator import WalletGenerator
from executor import TransferExecutor, Bootstrapper
from helpers import load_abi


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
            executor = TransferExecutor(os.environ.get('RPC_ENDPOINT'),
                                        os.environ.get('PRIVATE_KEY'),
                                        os.environ.get('ERC20_ADDRESS'),
                                        os.environ.get('ERC721_ADDRESS'),
                                        load_abi(f"{os.path.dirname(__file__)}/abis/erc20.json"),
                                        load_abi(f"{os.path.dirname(__file__)}/abis/erc721.json"),
                                        wallets[:args.number],
                                        args.tx)
            executor.execute({'type': 'native', 'amount': 0.01})
    
    logging.info(f"Action {args.action} completed")