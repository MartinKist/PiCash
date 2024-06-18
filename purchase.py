import json

from item import Item
# from logger import logger
from base import HasID


class Purchase(HasID):
    def __init__(self, purchases_dir) -> None:
        super().__init__()

        self.purchases_dir = purchases_dir
        self.items = {}
        self.active = True

    def add_item(self, item: Item):
        assert self.active
        try:
            self.items[item] += 1
        except KeyError:
            self.items[item] = 1

    def remove_item(self, item: Item):
        assert self.active
        if item in self.items and self.items[item] > 0:
            self.items[item] -= 1

    @property
    def total(self):
        return sum(item.price * amount for item, amount in self.items.items())

    @property
    def data(self):
        return {"id": self.id, "items": {item.name: amount for item, amount in self.items.items()}, "total": self.total}

    def archive(self):
        self.active = False

    def dump(self):
        with open(f"{self.purchases_dir}/{self.id}.json", "w", encoding="utf-8") as file:
            json.dump(self.data, file)


if __name__ == "__main__":
    b = Item("Bier", 3.5)
    c = Item("Kwas", 4.2)
    a = Purchase()
    a.add_item(b)
    a.add_item(b)
    a.add_item(c)
    a.remove_item(b)
    print(a.total)
    print(a.items)
    print(a.id)
    b = Purchase()
    print(b.id)
    a.archive()
    print(a == b)
