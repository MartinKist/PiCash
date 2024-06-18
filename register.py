from session import Session
from item import Item
from purchase import Purchase
import json
from gui import GUI


class Register:
    def __init__(self) -> None:
        self.items = {}

        self.session = Session()
        self.purchase = self.session.new_purchase()

        self.gui = GUI()

    def load_items(self):
        with open("config/items.json", encoding="utf-8") as file:
            self.items = json.load(file)

    def item_add_cb(self, item: Item):
        def callback():
            self.purchase.add_item(item)
            print(item.name)       
        return callback

    def run(self):
        self.load_items()
        for item in self.items:
            self.gui.add_button(item.name, self.item_add_cb(item))

        self.gui.run()


if __name__ == "__main__":
    r = Register()
    r.run()
