import os
import json
import logging
import argparse
import signal
import sys
import multiprocessing

from generator import WalletGenerator
from executor import TransferExecutor, Bootstrapper
from helpers import load_abi, SlackNotifier
from config import Config
from server import Server, Monitor

# Set up signal handler
def signal_handler(sig, frame):
    print('\nProcess terminated by user')
    sys.exit(0)

def monitor_process(wallets, config: Config):
    # set process group the same as main process
    os.setpgid(0, os.getppid())

    numerical_level = getattr(logging, config.log_level, logging.INFO)
    logging.basicConfig(level=numerical_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    monitor = Monitor(wallets, config)
    monitor.run()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    glb_config = Config()
    
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    numerical_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numerical_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    #signal.signal(signal.SIGINT, signal_handler)

    slack = SlackNotifier(os.environ.get('SLACK_WEBHOOK_URL')) if os.environ.get('SLACK_WEBHOOK_URL') else None    
    
    parser = argparse.ArgumentParser(description='Benchmark bot.')    
    parser.add_argument('-a', '--action', type=str, help="Actions: generate_wallets | bootstrap | transfer")
    parser.add_argument('-t', '--type', type=str, help="Actions: native | erc20", default='native')
    parser.add_argument('-b', '--balance', type=float, help="Initial balance of wallets", default=10)
    parser.add_argument('-n', '--number', type=int, help="Number of wallets", default=100)
    parser.add_argument('--amount-native', type=float, help="Amount native", default=1)
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

            if len(wallets) == 0:
                logging.error("No wallets found in wallets.json")
                sys.exit(1)

            wallet_numbers = int(args.number) if args.number < len(wallets) and args.number > 0 else len(wallets)
                
            executor = TransferExecutor(os.environ.get('RPC_ENDPOINT'),
                                        os.environ.get('PRIVATE_KEY'),
                                        os.environ.get('ERC20_ADDRESS'),
                                        os.environ.get('ERC721_ADDRESS'),
                                        load_abi(f"{os.path.dirname(__file__)}/abis/erc20.json"),
                                        load_abi(f"{os.path.dirname(__file__)}/abis/erc721.json"),
                                        wallets[:wallet_numbers],
                                        )
            
            executor.execute(args.amount_native, args.amount_erc20)

    elif args.action == 'server':
        with open('wallets.json') as file:
            wallets = json.load(file)

            if len(wallets) == 0:
                logging.error("No wallets found in wallets.json")
                sys.exit(1)

            wallet_numbers = int(args.number) if args.number < len(wallets) and args.number > 0 else len(wallets)

            # set process group
            os.setpgid(0, 0)

            # spawn monitoring process
            monitor = multiprocessing.Process(target=monitor_process, args=(wallets[:wallet_numbers], glb_config))
            monitor.start()
            logging.warning(f"Monitoring process started with PID {monitor.pid}")
            
            server = Server(wallets[:wallet_numbers], glb_config)            
            server.run()

    else:
        logging.error(f"Unknown action: {args.action}")
        sys.exit(1)
    
    logging.info(f"Action {args.action} completed")