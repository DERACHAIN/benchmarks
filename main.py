import os
import json
import logging
import argparse

from generator import WalletGenerator
from executor import TransferExecutor, Bootstrapper
from helpers import load_abi, SlackNotifier
import signal
import sys

# Set up signal handler
def signal_handler(sig, frame):
    print('\nProcess terminated by user')
    sys.exit(0)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    #logging.basicConfig(filename='logs.txt', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    numerical_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numerical_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    signal.signal(signal.SIGINT, signal_handler)
    slack = SlackNotifier(os.environ.get('SLACK_WEBHOOK_URL')) if os.environ.get('SLACK_WEBHOOK_URL') else None
    
    parser = argparse.ArgumentParser(description='Benchmark bot.')    
    parser.add_argument('-a', '--action', type=str, help="Actions: generate_wallets | bootstrap | transfer")
    parser.add_argument('-t', '--type', type=str, help="Actions: native | erc20", default='native')
    parser.add_argument('-b', '--balance', type=float, help="Initial balance of wallets", default=10)
    parser.add_argument('-n', '--number', type=int, help="Number of wallets", default=100)
    parser.add_argument('--amount-native', type=float, help="Amount native", default=0.1)
    parser.add_argument('--amount-erc20', type=float, help="Amount ERC20", default=10)

    args = parser.parse_args()

    if args.action == 'generate_wallets':
        wg = WalletGenerator()
        wg.generate_wallets(int(args.number))
    elif args.action == 'bootstrap':        
        with open('wallets.json') as file:
            wallets = json.load(file)
            bootstrapper = Bootstrapper(os.environ.get('RPC_ENDPOINT'), 
                                    os.environ.get('PRIVATE_KEY'),
                                    os.environ.get('ERC20_ADDRESS'),
                                    load_abi(f"{os.path.dirname(__file__)}/abis/erc20.json"),
                                    wallets,
                                    slack)
        
            bootstrapper.execute({'type': args.type, 'amount': args.balance})

    elif args.action == 'transfer':    
        with open('wallets.json') as file:
            wallets = json.load(file)

            logging.info(f"amount native {args.amount_native}")
            logging.info(f"amount erc20 {args.amount_erc20}")

            wallet_numbers = int(args.number) if args.number < len(wallets) and args.number > 0 else len(wallets)
                
            executor = TransferExecutor(os.environ.get('RPC_ENDPOINT'),
                                        os.environ.get('PRIVATE_KEY'),
                                        os.environ.get('ERC20_ADDRESS'),
                                        os.environ.get('ERC721_ADDRESS'),
                                        load_abi(f"{os.path.dirname(__file__)}/abis/erc20.json"),
                                        load_abi(f"{os.path.dirname(__file__)}/abis/erc721.json"),
                                        wallets[:wallet_numbers],
                                        slack)
            
            executor.execute({'amount_native': args.amount_native, 'amount_erc20': args.amount_erc20})
    
    logging.info(f"Action {args.action} completed")