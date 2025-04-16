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
    #logging.basicConfig(filename='logs.txt', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    numerical_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numerical_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description='Benchmark bot.')    
    parser.add_argument('-a', '--action', type=str, help="Actions: generate_wallets | bootstrap | transfer")
    parser.add_argument('-t', '--type', type=str, help="Actions: native | erc20", default='native')
    parser.add_argument('-b', '--balance', type=float, help="Initial balance of wallets", default=10)
    parser.add_argument('-n', '--number', type=int, help="Number of wallets", default=100)
    parser.add_argument('-tx', '--tx', type=int, help="Number of tx", default=10**6)

    args = parser.parse_args()

    if args.action == 'generate_wallets':
        wg = WalletGenerator()
        wg.generate_wallets(int(args.number))
    elif args.action == 'bootstrap':        
        bootstrapper = Bootstrapper(os.environ.get('RPC_ENDPOINT'), 
                                    os.environ.get('PRIVATE_KEY'),
                                    os.environ.get('ERC20_ADDRESS'),
                                    load_abi(f"{os.path.dirname(__file__)}/abis/erc20.json"),
                                    )
        with open('wallets.json') as file:
            wallets = json.load(file)
            for wallet in wallets:
                bootstrapper.execute({'type': args.type, 'to': wallet['address'], 'amount': args.balance})
    elif args.action == 'transfer':        
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
            executor.execute({'amount_native': 0.01, 'amount_erc20': 10})
    
    logging.info(f"Action {args.action} completed")