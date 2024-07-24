import framebuf
from hw_drivers.lcd_3inch5 import lcd, DisplayArea

from singleton import Singleton
from models import Purchase, Item


class Colors:
    RED = 0x07E0
    GREEN = 0x001F
    BLUE = 0xF800
    WHITE = 0xFFFF
    BLACK = 0x0000
    GREY = 0x7BEF
    YELLOW = 0xffc0

class Button:
    def __init__(
        self,
        coords: tuple,
        text: str,
        bg_color: int = Colors.GREY,
        text_color: int = Colors.BLACK,
        text_size: int = 1,
        callback=lambda: None,
    ) -> None:

        self._needs_redraw = True
        self._pressed = False

        self.coords = coords
        self.width = coords[2] - coords[0] - 1
        self.height = coords[3] - coords[1] - 1

        self.callback = callback

        self.bg_color = bg_color
        self.text_color = text_color
        self.text = text
        self.text_size = text_size

        self.display_area = DisplayArea(self.coords)

    def draw(self, text_color: Colors = None, bg_color: Colors = None, force = True):
        if self._needs_redraw or force:
            if text_color is None:
                text_color = self.text_color
            if bg_color is None:
                bg_color = self.bg_color

            self.display_area.fill(bg_color)

            if isinstance(self.text, str):
                self.text = [self.text]
            margin = self.text_size * 5
            for i, ln in enumerate(self.text):
                self.display_area.large_text(ln, margin, margin + i * 10 * self.text_size, self.text_size, c=text_color)

            lcd.update_area(self.display_area)
            self._needs_redraw = False

    def press(self):
        self._pressed = True
        self.draw(Colors.BLACK, Colors.WHITE, force=True)

    def check_released(self):
        if self._pressed:
            self._pressed = False
            self.callback()

            self.draw(force=True)

    def check_pressed(self, x, y):
        if not self._pressed and (
            self.coords[0] < x < self.coords[2] and self.coords[1] < y < self.coords[3]
        ):
            self.press()

    def __setattr__(self, name: str, value) -> None:
        if name in ("text", "bg_color", "text_color"):
            try:
                if  getattr(self, name) != value:
                    self._needs_redraw = True
            except AttributeError:
                pass
        super().__setattr__(name, value)


class ButtonBoard:
    def __init__(self, coords: tuple, x: int, y: int) -> None:
        self.display = Display()
        self.coords = coords

        self.buttons = {}
        self.x = x
        self.y = y
        self.width = coords[2] - coords[0]
        self.height = coords[3] - coords[1]

        self.btn_width = int(self.width / x)
        self.btn_height = int(self.height / y)

        self.buffer = bytearray(self.btn_height * self.btn_width * 2)

    def positon_to_coords(self, position: tuple):
        x, y = position
        return (
            self.coords[0] + x * self.btn_width,
            self.coords[1] + y * self.btn_height,
            self.coords[0] + (x + 1) * self.btn_width + 1,
            self.coords[1] + (y + 1) * self.btn_height + 1,
        )

    def get_free_positon(self):
        for y in range(self.y):
            for x in range(self.x):
                if (x, y) not in self.buttons:
                    return x, y
        else:
            raise IndexError

    def add_button(self, text: str, callback=lambda: None, position: tuple = None):
        if position is None:
            position = self.get_free_positon()
        b = Button(self.positon_to_coords(position), text, callback=callback, text_size=2)
        self.buttons[position] = b
        self.display.add_button(b)
        return b


class PurchaseViewer:
    def __init__(self, coords: tuple, item_remove_cb, rows: int = 4) -> None:
        self.display = Display()
        self.coords = coords
        self.rows = rows
        self.item_remove_cb = item_remove_cb

        # some geometry
        self.width = coords[2] - coords[0] + 1
        self.height = coords[3] - coords[1] + 1
        self.btn_height = self.height // rows

        self.item_buttons = []
        for i in range(self.rows):
            btn = Button(
                (self.coords[0], i * self.btn_height, self.coords[2], (i+1)*self.btn_height),
                "",
                bg_color=Colors.WHITE,
                text_size=2
            )
            self.item_buttons.append(btn)
            self.display.add_button(btn)

    def clear_button(self, btn):
        btn.text = ""
        btn.bg_color = Colors.WHITE
        btn.callback = lambda: None
        btn.draw()

    def update(self, purchase: Purchase):
        items = list(purchase.items.items())
        for i, btn in enumerate(self.item_buttons):
            if i < len(items):
                item, amount = items[i]
                btn.text = [f"{amount}x {item.name}", f"{amount*item.price:.2f} EURO"]
                btn.bg_color = Colors.GREY
                btn.callback = self.item_remove_cb(item)
                btn.draw()
            else:
                self.clear_button(btn)




class Display(Singleton):
    def __init__(self) -> None:
        self.buttons = set()
        
    def add_button(self, button: Button):
        self.buttons.add(button)

    def run(self):
        #lcd.fill_area((0, 0, 480, 320), Colors.WHITE)
        for button in self.buttons:
            button.draw()

        while True:
            x, y, state = lcd.touch_input()
            if state == "pressed":
                for btn in self.buttons:
                    btn.check_pressed(x, y)
            elif state == "released":
                for btn in self.buttons:
                    btn.check_released()

