import json

from models import Item
from singleton import Singleton


class Config(Singleton):
    session_name = "dummy"
    items = []
    init_cash = 0

    def load_config_file(self, file:str):
        with open(file, "r") as file:
            data = json.load(file)

        self.session_name = data["session_name"]
        self.init_cash = data["init_cash"]
        self.items = [Item(name, price) for name, price in data["items"].items()]
