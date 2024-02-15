from displayio import release_displays

release_displays()

import displayio
import busio
import board
import dotclockframebuffer
from framebufferio import FramebufferDisplay

# --------------------------Custom imports-----------------------
import vectorio
import math
from jepler_udecimal import Decimal
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_qualia.graphics import Graphics, Displays
import time

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

#bitmap = displayio.OnDiskBitmap("/round-display-ruler-720p.bmp")
bitmap = displayio.OnDiskBitmap("/Meterface.bmp")

fb = dotclockframebuffer.DotClockFramebuffer(**tft_pins, **tft_timings)

# Original code
#display = FramebufferDisplay(fb, auto_refresh=False)

#Graphics code ----WORKS 15/2 05:26----
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

# Needle center
pointer_pal = displayio.Palette(6)
pointer_pal[0] = 0xff0000  # Red
pointer_pal[1] = 0x000000  # Black
pointer_pal[2] = 0x0000ff  # Blue
pointer_pal[3] = 0xffffff  # White
pointer_pal[4] = 0xE3DAC9  # Off-White 1
pointer_pal[5] = 0xF8F4E3  # Off-White 2

pointer_hub = vectorio.Circle(pixel_shader=pointer_pal, radius=20, x=0, y=0)
pointer_hub.x = graphics.display.width // 2
pointer_hub.y = graphics.display.height // 2

#---------------------------------Indicator needle------------------------------
needle_width = 4
needle_length = 194


# For square needle
min_points = [(needle_width,0), (needle_width,-needle_length), (-needle_width,-needle_length), (-needle_width,0)]
#needle = vectorio.Polygon(pixel_shader=pointer_pal, points=min_points, x=0, y=0)

# For pointy needle
#min_points = [(0, -needle_length), (needle_width, 0), (-needle_width, 0)]

# Rotation angle in degrees and radians
rotation_degrees = 135
rotation_radians = math.radians(rotation_degrees)

# Modified function to rotate a point and ensure integer coordinates
def rotate_point(x, y, theta):
    x_new = x * math.cos(theta) - y * math.sin(theta)
    y_new = x * math.sin(theta) + y * math.cos(theta)
    return (int(round(x_new)), int(round(y_new)))  # Ensure integer coordinates

# Rotate each point
rotated_min_points = [rotate_point(x, y, rotation_radians) for x, y in min_points]

def rpm_to_angle(rpm, max_rpm=10000, base_angle=135, total_angle_range=270):
    proportion_of_max = rpm / max_rpm
    angle_from_base = proportion_of_max * total_angle_range
    return base_angle + angle_from_base

def rotate_needle(rpm):
    angle_degrees = rpm_to_angle(rpm)
    angle_radians = math.radians(angle_degrees)
    rotated_min_points = [rotate_point(x, y, angle_radians - math.radians(0)) for x, y in min_points]
    needle.points = rotated_min_points

# Create the rotated needle polygon with integer coordinates
needle = vectorio.Polygon(pixel_shader=pointer_pal, points=rotated_min_points, x=0, y=0)

# Center the base of the needle at the middle of the display
needle.x = graphics.display.width // 2
needle.y = graphics.display.height // 2

# Set the needle color to white
needle.color_index = 5
pointer_hub.color_index = 1

group.append(needle)
group.append(pointer_hub)

rpm = 0
direction = 1  # Start with increasing RPM
max_rpm = 10000
increment = 100

# Loop forever so you can enjoy your image
while True:
    rotate_needle(rpm)
    rpm += direction * increment  # Adjust RPM based on the direction

    # Reverse direction at limits
    if rpm >= max_rpm or rpm <= 0:
        direction *= -1  # Reverse direction

    time.sleep(0.01)  # Add delay to see the needle move
