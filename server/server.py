import asyncio
from library import Singleton

class Server(metaclass=Singleton):
    def __init__(self, config):
        self.config = config

    async def start(self):
        print("Starting server...")

    def run(self):
        asyncio.run(self.start())

