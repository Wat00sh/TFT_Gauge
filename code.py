from displayio import release_displays

release_displays()

import displayio
import busio
import board
import dotclockframebuffer
from framebufferio import FramebufferDisplay

# --------------------------Custom imports-----------------------
import terminalio
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


#Meter face
#bitmap = displayio.OnDiskBitmap("/Meterface.bmp")

graphics = Graphics(Displays.ROUND28, default_bg=None, auto_refresh=True)



#--------------------------------------------LUT--------------------------------------------
needle_position_lookup = {}
def load_lookup_table(filename="needle_positions_lut.txt"):
    try:
        with open(filename, "r") as file:
            for line in file:
                parts = line.strip().split(": ")
                rpm = int(parts[0])
                position = eval(parts[1])
                needle_position_lookup[rpm] = position
        print("Lookup table loaded successfully.")
    except Exception as e:
        print(f"Failed to load lookup table: {e}")

# Load the lookup-table
load_lookup_table()

# Create a TileGrid to hold the bitmap
#tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)


# Center the image
#tile_grid.x -= (bitmap.width - graphics.display.width) // 2
#tile_grid.y -= (bitmap.height - graphics.display.height) // 2

# Create a Group to hold the TileGrid
group = displayio.Group()

# Add the TileGrid to the Group
#group.append(tile_grid)

# Add the Group to the Display
graphics.display.root_group = group


#---------------------------------Needle hub------------------------------
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


#-------------------------------------Needle with LUT---------------------------
# Initialize the needle with placeholder points (these will be updated immediately in the loop)
needle_points = [(0, 0), (0, 0), (0, 0), (0, 0)]  # Initial placeholder points
needle = vectorio.Polygon(pixel_shader=pointer_pal, points=needle_points, x=0, y=0)

def rotate_needle_lookup(rpm):
    # Find the closest RPM key in the LUT
    closest_rpm = min(needle_position_lookup.keys(), key=lambda k: abs(k - rpm))
    if closest_rpm in needle_position_lookup:
        needle_points = needle_position_lookup[closest_rpm]
        needle.points = needle_points
    else:
        print(f"RPM value {rpm} not in lookup table, closest found was {closest_rpm}.")


# Center the base of the needle at the middle of the display
needle.x = graphics.display.width // 2
needle.y = graphics.display.height // 2

# Set the needle color to white
needle.color_index = 5
pointer_hub.color_index = 1

group.append(needle)
#group.append(pointer_hub)

#-----------------------------------------RPM as stack--------------------------------
def init_pixels():
    # Palette for the pixel colors
    palette = displayio.Palette(2)
    palette[0] = 0x000000
    palette[1] = 0xE3DAC9

     # Construct the bitmap
    bitmap = displayio.Bitmap(graphics.display.width, graphics.display.height, 2)
    # Tile grid for individual pixels
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    # add the tile grid
    group.append(tile_grid)

    return bitmap


def turn_on_off(bitmap):
    # Turn all "y" pixels on for each "x" pixel, then pause
    for x in range(0, 240):
        for y in range(230, 250):
            bitmap[x, y] = 1
        time.sleep(0.005)  # Pause after updating an entire row of "y" pixels


    # Turn all "y" pixels off for each "x" pixel in the opposite order, then pause
    for x in range(239, -1, -1):  # Iterate over "x" pixels in reverse order
        for y in range(249, 229, -1):  # Iterate over "y" pixels, but ordering doesn't change the effect
            bitmap[x, y] = 0
        time.sleep(0.005)  # Pause after updating an entire row of "y" pixels


def draw_clockwise_arc(bitmap, palette_index, start_x, start_y, inner_radius, arc_width, start_angle, sweep_angle):
    # Assuming a specific configuration based on your description
    center_x = start_x  # This might need adjustment
    center_y = start_y - inner_radius - arc_width  # Adjust based on geometry
    radius = inner_radius + arc_width

    for angle in range(sweep_angle + 1):
        rad_angle = math.radians(start_angle + angle)  # Adjust for clockwise sweep
        for r in range(inner_radius, radius):
            x = int(center_x + r * math.cos(rad_angle))
            y = int(center_y + r * math.sin(rad_angle))

            # Check bounds
            if 0 <= x < 480 and 0 <= y < 480:
                bitmap[x, y] = palette_index


# Example parameters
start_x, start_y = 480, 480  # Start at bottom-right corner
inner_radius = 460 - 480  # Inner radius of the arc
arc_width = 20  # Width of the arc
start_angle = -90  # Start from the bottom, moving clockwise
sweep_angle = 270  # Sweep angle

# Draw the arc
#draw_clockwise_arc(bitmap, 1, center_x, center_y, radius, start_angle, sweep_angle, arc_width)


#-----------------------------------------RPM as text---------------------------------
# Initialize the text label for RPM display
rpm_text = "RPM: 0"  # Initial text
font = terminalio.FONT  # Use the built-in font
color = 0xFFFFFF  # White color

# Create the text label
rpm_label = label.Label(font=font, text=rpm_text, color=color)

# Position the label
rpm_label.x = 190  # Adjust x position as needed
rpm_label.y = 200  # Adjust y position as needed

# Add the label to the display group
#group.append(rpm_label)


#---------------------------------------Main loop-----------------------------------
rpm = 0
direction = 1  # Start with increasing RPM
max_rpm = 10000
increment = 50

bitmap = init_pixels()
while True:
    #rotate_needle_lookup(rpm)
    #rpm += direction * increment  # Adjust RPM based on the direction
    #if rpm > max_rpm:
    #    rpm = max_rpm
    #    direction *= -1  # Reverse direction
    #elif rpm < 0:
    #    rpm = 0
    #    direction *= -1  # Reverse direction

    #rpm_label.text = f"RPM: {rpm}"
    #turn_on_off(bitmap)
    draw_clockwise_arc(bitmap, 1, start_x, start_y, inner_radius, arc_width, start_angle, sweep_angle)

