import os
from library import Singleton

class Config(metaclass=Singleton):
    def __init__(self):
        self.rpc = os.environ.get('RPC_ENDPOINT')
        self.operator_sk = os.environ.get('PRIVATE_KEY')
        self.erc20_address = os.environ.get('ERC20_ADDRESS')
        self.erc721_address = os.environ.get('ERC721_ADDRESS')
        self.erc20_abi = os.path.join(os.path.dirname(__file__), 'abis', 'erc20.json')
        self.erc721_abi = os.path.join(os.path.dirname(__file__), 'abis', 'erc721.json')