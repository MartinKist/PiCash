import json
import os

from models import Purchase

from configuration import Config


DATA_DIR = "/data"


class Session:
    def __init__(self) -> None:
        self.config = Config()
        self.name = self.config.session_name
        self.init_cash = self.config.init_cash

        self.filename = f"{DATA_DIR}/{self.name}.json"

        self.purchases = []

        self.make_dir()

    def make_dir(self):
        try:
            os.mkdir(DATA_DIR)
        except Exception as e:
            pass

    def save_purchase(self, purchase: Purchase):
        self.purchases.append(purchase)
        self.save()

    def save(self):
        with open(self.filename, "w") as file:
            json.dump(self.data, file)

    @property
    def data(self) -> dict:
        return {
            "name": self.name,
            "init_cash": self.init_cash,
            "purchases": [purchase.data for purchase in self.purchases]
        }
    @property
    def total(self):
        return sum(purchase.total for purchase in self.purchases) + self.init_cash
