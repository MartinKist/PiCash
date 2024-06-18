class Item:
    def __init__(self, name: str, price: float) -> None:
        self.name = name
        self.price = price

    def __repr__(self) -> str:
        return f"{self.name}({self.price}€)"

    def __hash__(self) -> int:
        return hash(self.name)
