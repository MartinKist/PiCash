from machine import Pin, SPI, PWM
import framebuf
import time
import asyncio
import gc


LCD_DC = 8
LCD_CS = 9
LCD_SCK = 10
LCD_MOSI = 11
LCD_MISO = 12
LCD_BL = 13
LCD_RST = 15
TP_CS = 16
TP_IRQ = 17

ROTATION = 270



class DisplayArea(framebuf.FrameBuffer):
    mem = {}

    def __init__(self, coords: tuple) -> None:
        self.coords = coords
        self.width = coords[2] - coords[0] - 1
        self.height = coords[3] - coords[1] - 1

        if (self.width, self.height) not in self.__class__.mem:
            self.__class__.mem[(self.width, self.height)] = bytearray(self.width * self.height * 2)

        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)

    @property
    def buffer(self):
        return self.__class__.mem[(self.width, self.height)]

    def __del__(self):
        del self.__class__.mem[(self.width, self.height)]


class LCD_3inch5:
    def __init__(self, rotation):
        self.rotation = rotation  # Set the rotation Angle to 0°, 90°, 180° and 270°

        self.cs = Pin(LCD_CS, Pin.OUT)
        self.rst = Pin(LCD_RST, Pin.OUT)
        self.dc = Pin(LCD_DC, Pin.OUT)

        self.tp_cs = Pin(TP_CS, Pin.OUT)
        self.irq = Pin(TP_IRQ, Pin.IN)

        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.tp_cs(1)
        self.spi = SPI(1, 6_000_000)
        self.spi = SPI(
            1,
            baudrate=40_000_000,
            sck=Pin(LCD_SCK),
            mosi=Pin(LCD_MOSI),
            miso=Pin(LCD_MISO),
        )

        self.pressed = False
        self.x = 0
        self.y = 0
        self.counter = 0

        self.init_display()

    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        # self.spi.write(bytearray([0X00]))
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize dispaly"""
        self.rst(1)
        time.sleep_ms(5)
        self.rst(0)
        time.sleep_ms(10)
        self.rst(1)
        time.sleep_ms(5)
        self.write_cmd(0x21)

        self.write_cmd(0xC2)
        self.write_data(0x33)

        self.write_cmd(0xC5)
        self.write_data(0x00)
        self.write_data(0x1E)
        self.write_data(0x80)

        self.write_cmd(0xB1)
        self.write_data(0xB0)

        self.write_cmd(0xE0)
        self.write_data(0x00)
        self.write_data(0x13)
        self.write_data(0x18)
        self.write_data(0x04)
        self.write_data(0x0F)
        self.write_data(0x06)
        self.write_data(0x3A)
        self.write_data(0x56)
        self.write_data(0x4D)
        self.write_data(0x03)
        self.write_data(0x0A)
        self.write_data(0x06)
        self.write_data(0x30)
        self.write_data(0x3E)
        self.write_data(0x0F)

        self.write_cmd(0xE1)
        self.write_data(0x00)
        self.write_data(0x13)
        self.write_data(0x18)
        self.write_data(0x01)
        self.write_data(0x11)
        self.write_data(0x06)
        self.write_data(0x38)
        self.write_data(0x34)
        self.write_data(0x4D)
        self.write_data(0x06)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x31)
        self.write_data(0x37)
        self.write_data(0x0F)

        self.write_cmd(0x3A)
        self.write_data(0x55)

        self.write_cmd(0x11)
        time.sleep_ms(120)
        self.write_cmd(0x29)

        self.write_cmd(0xB6)
        self.write_data(0x00)
        self.write_data(0x62)

        self.write_cmd(0x36)  # Sets the memory access mode for rotation
        if self.rotation == 0:
            self.write_data(0x88)
        elif self.rotation == 180:
            self.write_data(0x48)
        elif self.rotation == 90:
            self.write_data(0xE8)
        else:
            self.write_data(0x28)

    def update_area(self, area: DisplayArea):
        x_top = area.coords[0]
        y_top = area.coords[1]
        x_bottom = area.coords[2] - 2
        y_bottom = area.coords[3] - 2

        #print("update")
        # Set column address (X direction)
        self.write_cmd(0x2A)
        self.write_data(x_top >> 8)      # High byte of x_top
        self.write_data(x_top & 0xFF)    # Low byte of x_top
        self.write_data(x_bottom >> 8)   # High byte of x_bottom
        self.write_data(x_bottom & 0xFF) # Low byte of x_bottom

        # Set row address (Y direction)
        self.write_cmd(0x2B)
        self.write_data(y_top >> 8)      # High byte of y_top
        self.write_data(y_top & 0xFF)    # Low byte of y_top
        self.write_data(y_bottom >> 8)   # High byte of y_bottom
        self.write_data(y_bottom & 0xFF) # Low byte of y_bottom

        # Write memory
        self.write_cmd(0x2C)

        # SPI write sequence
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(area.buffer)
        self.cs(1)

    def bl_ctrl(self, duty):
        pwm = PWM(Pin(LCD_BL))
        pwm.freq(1000)
        if duty >= 100:
            pwm.duty_u16(65535)
        else:
            pwm.duty_u16(655 * duty)

    def touch_get(self):
        if self.irq() == 0:
            self.spi = SPI(
                1, 4_000_000, sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO)
            )
            self.tp_cs(0)
            X_Point = 0
            Y_Point = 0
            for i in range(0, 3):
                self.spi.write(bytearray([0xD0]))
                Read_date = self.spi.read(2)
                time.sleep_us(10)
                X_Point = X_Point + (((Read_date[0] << 8) + Read_date[1]) >> 3)

                self.spi.write(bytearray([0x90]))
                Read_date = self.spi.read(2)
                Y_Point = Y_Point + (((Read_date[0] << 8) + Read_date[1]) >> 3)

            X_Point = X_Point / 3
            Y_Point = Y_Point / 3

            self.tp_cs(1)
            self.spi = SPI(
                1, 40_000_000, sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO)
            )
            Result_list = [X_Point, Y_Point]
            return Result_list

    @staticmethod
    def calc_x_y(get):
        x = int((get[1]-430)*480/3270)
        if(x>480):
            x = 480
        elif x<0:
            x = 0
        y = 320-int((get[0]-430)*320/3270)
        return x, y

    def reset_touch(self):
        self.pressed = None
        self.x = 0
        self.y = 0

    def touch_input(self):
        while True:
            touch_input = self.touch_get()
            #print(touch_input, self.pressed, self.x, self.y)
            if touch_input is None:
                if self.pressed:
                    x = self.x
                    y = self.y
                    self.pressed = False
                    return x, y, "released"
            else:
                if not self.pressed:
                    x, y = self.calc_x_y(touch_input)
                    
                    if abs(x - self.x) < 3 and abs(y - self.y) < 3:
                        self.counter += 1
                    else:
                        self.counter = 0

                    self.x = x
                    self.y = y

                    if self.counter > 5:
                        self.pressed = True
                        return self.x, self.y, "pressed"

            #await asyncio.sleep(0.01)


lcd = LCD_3inch5(ROTATION)
