import json
import os.path

from purchase import Purchase
from base import HasID
from item import Item


SESSION_DIR = "./data/sessions"


class Session:
    def __init__(self) -> None:
        if os.path.exists(SESSION_DIR):
            self.id = max(int(s_id) for s_id in os.listdir(SESSION_DIR)) + 1
        else:
            self.id = 0

        self.dir = f"{SESSION_DIR}/{self.id}"
        self.purchases_dir = f"{self.dir}/purchases"
        self.create_directories()

        self.purchases = set()

    def create_directories(self):
        if not os.path.exists(self.purchases_dir):
            os.makedirs(self.purchases_dir)

    def new_purchase(self):
        p = Purchase(self.purchases_dir)
        self.purchases.add(p)
        return p

    @property
    def total(self):
        return sum(purchase.total for purchase in self.purchases)


if __name__ == "__main__":
    a = Session()
    p = Purchase()
    p.add_item(Item("Kwas", 8.8))
    p.add_item(Item("Bier", 3))
    p2 = Purchase()
    p2.add_item(Item("k", 4))
    a.add_purchase(p)
    a.add_purchase(p2)