from displayio import release_displays

release_displays()

import displayio
import busio
import board
import dotclockframebuffer
from framebufferio import FramebufferDisplay

# --------------------------Custom imports-----------------------
import vectorio
from math import pi, cos, sin
from jepler_udecimal import Decimal
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_qualia.graphics import Graphics, Displays



tft_pins = dict(board.TFT_PINS)

# --------------------------TFT Timings---------------------------
from tft_config import tft_timings

# --------------------------Init sequence--------------------------
from tft_config import init_sequence


board.I2C().deinit()
i2c = busio.I2C(board.SCL, board.SDA)
tft_io_expander = dict(board.TFT_IO_EXPANDER)
# tft_io_expander['i2c_address'] = 0x38 # uncomment for rev B
dotclockframebuffer.ioexpander_send_init_sequence(i2c, init_sequence, **tft_io_expander)
i2c.deinit()

bitmap = displayio.OnDiskBitmap("/round-display-ruler-720p.bmp")

fb = dotclockframebuffer.DotClockFramebuffer(**tft_pins, **tft_timings)

# Original code
#display = FramebufferDisplay(fb, auto_refresh=False)

#"Graphics" code ----WORKS 15/2 05:26----
graphics = Graphics(Displays.ROUND28, default_bg=None, auto_refresh=True)

# Create a TileGrid to hold the bitmap
tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)

# Center the image
tile_grid.x -= (bitmap.width - graphics.display.width) // 2
tile_grid.y -= (bitmap.height - graphics.display.height) // 2

# Create a Group to hold the TileGrid
group = displayio.Group()

# Add the TileGrid to the Group
group.append(tile_grid)

# Add the Group to the Display
graphics.display.root_group = group

#display.auto_refresh = True

# Loop forever so you can enjoy your image
while True:
    pass
