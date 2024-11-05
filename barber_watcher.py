

import requests
import json
import datetime
import time
from discord_notifications import NotificationBot



class BarberWatcher:

    def __init__(self, api_url, seen_slots_fn=None, notification_bot=None):
        self.api_url = api_url
        self.seen_slots_fn = seen_slots_fn
        self.notification_bot = notification_bot
        
        self.seen_slots = []
        self.load_seen_slots()


    def load_seen_slots(self):
        if self.seen_slots_fn is None:
            return
        try:
            with open(self.seen_slots_fn) as f:
                self.seen_slots = json.load(f)
        except FileNotFoundError:
            pass


    def save_seen_slots(self):
        if self.seen_slots_fn is None:
            return
        
        with open(self.seen_slots_fn, "w+") as f:
            json.dump(self.seen_slots, f, indent=4)

    def post_notification(self, notification_txt):

        if self.notification_bot is None:
            return

        self.notification_bot.post_notification(notification_txt)


    def get_barber_times(self):

        weeks_to_look_for = 3
        dt = datetime.timedelta(weeks=1)
        today = datetime.datetime.today()

        payload = {
            "noDiscounts": True,
            "services": [
                {
                    "duration": 45,
                     "hideFromWebReservation": False,
                     "serviceId": 104,
                     "additionalServices": [],
                     "name":"Parturileikkaus"
                }
            ],
            "weekStart": today.isoformat(),
            "strategy": "fair",
            "users": [{"id":"606da0e2d85be333827c89c2"}],
            "onlySameUser": True,
            "maxTimeInterval": 15
        }

        headers = {
            "content-type": "application/json"

        }

        for i in range(weeks_to_look_for):
            payload["weekStart"] = (today + 3*dt).isoformat()
            resp = requests.post(self.api_url, data=json.dumps(payload), headers=headers)
            events = resp.json()
            for event in events:
                for timeslot in event:
                    start_time = timeslot["clientStart"]
                    
                    if start_time not in self.seen_slots:
                        notification_txt = "Uusi parturiaika: " + start_time
                        self.post_notification(notification_txt)
                        self.seen_slots.append(start_time)
                        self.save_seen_slots()
                        
                        

        return resp

    def watch_barber_times(self):
        wait_time = 5 * 60
        print("Watching...")

        while True:
            self.get_barber_times()
            time.sleep(wait_time)


def run_watcher():
    
    with open("barber_api_url.txt") as f:
        api_url = f.read()

    with open("webhook_url.txt") as f:
        webhook_url = f.read()

    notification_bot = NotificationBot(webhook_url)

    watcher = BarberWatcher(api_url, "parturiajat.json", notification_bot)
    watcher.watch_barber_times()


if __name__ == "__main__":
    run_watcher()
