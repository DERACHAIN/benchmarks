import requests
import json
from library import Singleton

class SlackNotifier(metaclass=Singleton):
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_message(self, message):
        payload = {
            "text": message
        }
        response = requests.post(self.webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        
        if response.status_code != 200:
            raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")

