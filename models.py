class Item:
    def __init__(self, name: str, price: float) -> None:
        self.name = name
        self.price = price

    def __repr__(self) -> str:
        return f"{self.name}({self.price}€)"

    def __hash__(self) -> int:
        return hash(self.name)


class Purchase:
    def __init__(self) -> None:
        self.items = {}

    def add_item(self, item: Item):
        try:
            self.items[item] += 1
        except KeyError:
            self.items[item] = 1

    def remove_item(self, item: Item):
        if item in self.items :
            self.items[item] -= 1
            if self.items[item] <= 0:
                del self.items[item]

    def clear(self):
        self.items = {}

    @property
    def total(self):
        return sum(item.price * amount for item, amount in self.items.items())

    @property
    def data(self):
        return {"items": {item.name: amount for item, amount in self.items.items()}, "total": self.total}

    def __bool__(self):
        return self.total > 0