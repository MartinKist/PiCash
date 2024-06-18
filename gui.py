import framebuf
from hw_drivers.lcd_3inch5 import lcd, DisplayArea
import asyncio


class Colors:
    RED = 0x07E0
    GREEN = 0x001F
    BLUE = 0xF800
    WHITE = 0xFFFF
    BLACK = 0x0000
    GREY = 0x7BEF


class Button:
    def __init__(
        self,
        coords: tuple,
        text: str,
        bg_color: int = Colors.GREY,
        text_color: int = Colors.BLACK,
        callback=lambda: None,
    ) -> None:
        self.coords = coords
        self.text = text
        self.callback = callback

        self.bg_color = bg_color
        self.text_color = text_color
        self.width = coords[2] - coords[0] - 1
        self.height = coords[3] - coords[1] - 1

        self.display_area = DisplayArea(self.coords)

        self._pressed = False

        self.draw()

    def draw(self, text_color: Colors = None, bg_color: Colors = None):
        if text_color is None:
            text_color = self.text_color
        if bg_color is None:
            bg_color = self.bg_color

        self.display_area.fill(bg_color)
        self.display_area.text(self.text, 0, 0, text_color)
        lcd.update_area(self.display_area)

    def press(self):
        self._pressed = True
        self.draw(Colors.BLACK, Colors.WHITE)

    def check_released(self):
        if self._pressed:
            self._pressed = False
            self.callback()
            print(self.text)
            self.draw()

    def check_pressed(self, x, y):
        if not self._pressed and (
            self.coords[0] < x < self.coords[2] and self.coords[1] < y < self.coords[3]
        ):
            self.press()


class ButtonBoard:
    def __init__(self, coords: tuple, x: int, y: int) -> None:
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
        b = Button(self.positon_to_coords(position), text, callback=callback)
        self.buttons[position] = b
        return b


class PurchaseViewer:
    def __init__(self, coords: tuple) -> None:
        self.coords = coords
        self.submit_button = Button(
            (self.coords[0], self.coords[3] - 60, self.coords[2], self.coords[3]),
            "Submit",
            callback=self.on_submit,
            bg_color=Colors.RED,
        )
        self.submit_button.draw()

        self.width = coords[2] - coords[0] + 1
        self.height = coords[3] - coords[1] + 1

        #self.draw()

    def on_submit(self):
        print("submit")

    def draw(self):
        buf = bytearray(self.width * self.height * 2)
        fbuf = framebuf.FrameBuffer(buf, self.width, self.height, framebuf.RGB565)
        fbuf.fill(Colors.WHITE)
        lcd.update_area(*self.coords, buf)


class GUI:
    def __init__(self) -> None:
        self.buttons = set()
        self.bb = ButtonBoard((0, 0, 280, 320), 3, 4)
        self.pv = PurchaseViewer((280, 0, 481, 321))

    def add_button(self, text: str, callback=lambda: None, position: tuple = None):
        button = self.bb.add_button(text, callback, position)
        self.buttons.add(button)

    def run(self):
        while True:
            x, y, state = lcd.touch_input()
            #print(x, y, state)
            if state == "pressed":
                for btn in self.buttons:
                    btn.check_pressed(x, y)
            elif state == "released":
                for btn in self.buttons:
                    btn.check_released()

