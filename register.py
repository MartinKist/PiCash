from session import Session
from models import Item, Purchase
from gui import Display, ButtonBoard, PurchaseViewer, Button, Colors

from configuration import Config


class Register:
    def __init__(self) -> None:
        self.config = Config()
        self.display = Display()
        self.session = Session()
        self.purchase = Purchase()

        self.bb = ButtonBoard((0, 0, 280, 256), 2, 4)
        self.pv = PurchaseViewer((280, 0, 480, 256), self.item_remove_cb)

        self.submit_purchase_btn = Button((280, 256, 480, 320), "", bg_color=Colors.YELLOW, text_size=2, callback=self.on_submit)
        self.display.add_button(self.submit_purchase_btn)       

        self.reset_purchase_btn = Button((205, 256, 280, 320), "x", bg_color=Colors.RED, callback=self.on_reset, text_size=4)
        self.display.add_button(self.reset_purchase_btn)
        self.reset_purchase_btn.draw()

        self.info_view = Button((0, 256, 205, 321), "")

        for item in self.config.items:
            self.bb.add_button(item.name, self.item_add_cb(item))

        self.update()

    def on_reset(self):
        self.purchase.clear()
        self.update()

    def item_add_cb(self, item: Item):
        def callback():
            self.purchase.add_item(item)
            self.update()
        return callback

    def item_remove_cb(self, item: Item):
        def callback():
            self.purchase.remove_item(item)
            self.update()
        return callback

    def on_submit(self):
        if self.purchase:
            self.session.save_purchase(self.purchase)
            self.purchase = Purchase()
            self.update()

    def set_info_text(self):
        self.info_view.text = [
            f"Kassenstand: {self.session.total:.2f} EURO",
            f"Kunden bedient: {len(self.session.purchases)}",
        ]
        self.info_view.draw()

    def set_submit_text(self):
        self.submit_purchase_btn.text = f"{self.purchase.total:.2f} EURO"
        self.submit_purchase_btn.draw()

    def update(self):
        self.set_info_text()
        self.set_submit_text()
        self.pv.update(self.purchase)

    def run(self):
        self.display.run()
