import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw
import time

# Set up GPIO for D/C (Data/Command) and RST (Reset) pins
GPIO.setmode(GPIO.BCM)
DC = 24  # Change this to your specific pin
RST = 25  # Change this to your specific pin
GPIO.setup(DC, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(RST, GPIO.OUT, initial=GPIO.HIGH)

# Create an SPI object
spi = spidev.SpiDev()
spi.open(0, 0)  # Set the SPI bus and device
spi.max_speed_hz = 1000000 
spi.mode = 0b00


# SH1106 display settings
WIDTH = 128
HEIGHT = 64
BLACK = 0
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

# Function to clear the screen and draw a rectangle
def clear_screen():
    #global image
    #draw.rectangle((0, 0, WIDTH, HEIGHT), outline=BLACK, fill=BLACK)
    # Draw a rectangle on the screen
    rectangle_x1 = 20
    rectangle_y1 = 10
    rectangle_x2 = 150
    rectangle_y2 = 55
    draw.rectangle([rectangle_x1, rectangle_y1, rectangle_x2, rectangle_y2], outline=1, fill=1)
    
    image_data = list(image.tobytes())
    send_data(image_data)

# Function to send data to the display
def send_data(data):
    data_slice = [[], [], [], [], [], [], [], []]
    GPIO.output(DC, 0)
    for p in range(0, 8):
        data_set = []
        for c in range(0, 128):
            by = 0x00
            for b in range(0, 8):
                by = by >> 1 | (image.getpixel((c, p * 8 + b)) & 0x80)
            data_set.append(by)
        data_slice[p] = data_set
    spi.xfer([0xAF]) 
    for p in range(0, 8):
        GPIO.output(DC, 0)
        spi.xfer([0xB0 + p, 0x02, 0x10])  # Set column and page address
        GPIO.output(DC, 1)
        spi.xfer(data[p * 128 : (p + 1) * 128])  # Send the image data

# Set up SH1106 display configuration
display_config = [
    0xAE,  # Display off
    0x00,  # Set lower column start address
    0x10,  # Set higher column start address
    0xB0,  # Set page start address
    0x81,  # Set contrast control
    0xCF,  # Contrast value
    0xA1,  # Segment remap
    0xA6,  # Normal display
    0xA8,  # Multiplex ratio
    0x3F,  # Duty = 1/64
    0xC8,  # COM scan direction
    0xD3,  # Display offset
    0x00,  # No offset
    0xD5,  # Set display clock divide ratio/oscillator frequency
    0x80,
    0xD9,  # Set pre-charge period
    0xF1,
    0xDA,  # Set COM pins hardware configuration
    0x12,
    0xDB,  # Set VCOMH Deselect Level
    0x40,
    0xA4,  # Entire display on
    0xAF,  # Display on
    0x81,
0xa6,
0xae,
0xc0,
0xa0,
0x00,
0x10,
0xB0
]

# Initialize the display
GPIO.output(RST, 0)
time.sleep(0.1)
GPIO.output(RST, 1)
time.sleep(0.1)

# Send the configuration data to the display (set D/C low for commands)
GPIO.output(DC, 0)
for command in display_config:
    spi.xfer([command])

# Keep the program running
try:
    while True:
        time.sleep(1)
        clear_screen()  # Clear the screen and draw a rectangle after 1 second
except:
    print("Program termination reason: ")
    
spi.close()
GPIO.cleanup()
