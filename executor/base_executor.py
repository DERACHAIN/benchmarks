import os
import logging

from library import Singleton
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware, SignAndSendRawMiddlewareBuilder


class BaseExecutor(metaclass=Singleton):
    def __init__(self, rpc, operator_sk) -> None:
        self.w3 = Web3(Web3.HTTPProvider(rpc))
        self.operator = self.w3.eth.account.from_key(operator_sk)
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(self.operator), layer=0)
        self.w3.eth.default_account = self.operator.address

        self.logger = logging.getLogger(__name__)

    def execute(self, data):
        raise NotImplementedError("execute() method must be implemented in child classes")