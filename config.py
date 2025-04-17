import os
from library import Singleton
from helpers import load_abi

class Config(metaclass=Singleton):
    def __init__(self):
        self.log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
        self.rpc = os.environ.get('RPC_ENDPOINT')
        self.operator_sk = os.environ.get('PRIVATE_KEY')
        self.erc20_address = os.environ.get('ERC20_ADDRESS')
        self.erc721_address = os.environ.get('ERC721_ADDRESS')
        self.erc20_abi = load_abi(f"{os.path.dirname(__file__)}/abis/erc20.json")
        self.erc721_abi = load_abi(f"{os.path.dirname(__file__)}/abis/erc721.json")
        self.slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        self.native_balance_threshold = float(os.environ.get('NATIVE_BALANCE_THRESHOLD', 10))
        self.erc20_balance_threshold = float(os.environ.get('ERC20_BALANCE_THRESHOLD', 100))