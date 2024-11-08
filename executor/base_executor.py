import os
import logging

from library import Singleton
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware, SignAndSendRawMiddlewareBuilder


class BaseExecutor(metaclass=Singleton):
    def __init__(self, rpc, operator_sk, erc20_address, erc721_address, erc20_abi, erc721_abi) -> None:
        self.logger = logging.getLogger(__name__)

        self.w3 = Web3(Web3.HTTPProvider(rpc))
        self.operator = self.w3.eth.account.from_key(operator_sk)
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(self.operator), layer=0)
        self.w3.eth.default_account = self.operator.address

        self.erc20 = self.w3.eth.contract(address=Web3.toChecksumAddress(erc20_address), abi=erc20_abi)
        self.erc721 = self.w3.eth.contract(address=Web3.toChecksumAddress(erc721_address), abi=erc721_abi)

    def execute(self, data):
        raise NotImplementedError("execute() method must be implemented in child classes")