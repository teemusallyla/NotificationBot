

import requests


class NotificationBot:

    def __init__(self, webhook_url):
        self.webhook_url = webhook_url


    def post_notification(self, content):

        data = {
            "content": content
        }

        requests.post(self.webhook_url, data=data)



if __name__ == "__main__":

    with open("webhook_url.txt") as f:
        webhook_url = f.read()

    bot = NotificationBot(webhook_url)

    bot.post_notification("test notification")
    
