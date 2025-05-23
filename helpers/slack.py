import requests
import json
import logging
from library import Singleton


class SlackNotifier(metaclass=Singleton):
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_message(self, title, message, is_success=True):
        attachments = [{
            "color": "#36a64f" if is_success else "#ff0000",
            "title": "Success" if is_success else "Failed",
            "text": message,
            "footer": "Benchmarks Bot",
        }]
        
        payload = {
            "text": f"*{title}*",
            "attachments": attachments,
        }
        response = requests.post(self.webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        
        if response.status_code != 200:
            logging.warning(f"Request to Slack returned an error code {response.status_code}, with error: {response.text}")

