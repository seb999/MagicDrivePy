import spidev, time, sys
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

# Initialization of GPIO
GPIO.setmode(GPIO.BCM)
A0 = 24  # Change this to your specific pin
RESN = 25 

GPIO.setup(A0, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(RESN, GPIO.OUT, initial=GPIO.HIGH)

# Initialization of the SPI interface
spi = spidev.SpiDev()
spi.open(0, 0)  # bus = 0, device = 0
spi.max_speed_hz = 1000000  # Define the transfer speed (7629 to 125000000)
spi.mode = 0b00  # Define the data and clock pin sequencing
# spi.bits_per_word = 8

# Initialize the display image and draw object
# Display dimensions
WIDTH = 128
HEIGHT = 64
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

# Function to write text on the OLED
def write_text(text, font_file, position):
    # Load a font
    try:
        font = ImageFont.truetype(font_file, size=16)
    except IOError:
        font = ImageFont.load_default()

    # Draw text on the image
    draw.text(position, text, font=font, fill=1)

    # Display the updated image on the OLED
    display_img(image)
    
# Function for displaying a PIL image
def display_img(image):
    data_slice = [[], [], [], [], [], [], [], []]
    GPIO.output(A0, 0)
    for p in range(0, 8):
        data_set = []
        for c in range(0, 128):
            by = 0x00
            for b in range(0, 8):
                by = by >> 1 | (image.getpixel((c, p * 8 + b)) & 0x80)
            data_set.append(by)
        data_slice[p] = data_set
    spi.xfer([0xAF])  # Activate the display (0xAE to turn it off)
    for p in range(0, 8):
        GPIO.output(A0, 0)
        spi.xfer([0xB0 + p, 0x02, 0x10])  # Initialize column address
        GPIO.output(A0, 1)
        spi.xfer(data_slice[p])  # Transfer one slice of 128x8 pixels

# Application of a reset pulse to the SH1106 circuit
GPIO.output(RESN, 0)
time.sleep(0.1)
GPIO.output(RESN, 1)
time.sleep(0.1)

try:
    # Example of writing text on the display
    text = "AAAaaaa111"
    font_file = "marlboro.ttf"  # Provide the path to a TrueType font file
    position = (10, 10)  # Adjust the position as needed
    write_text(text, font_file, position)
        
    # while True:
    file = input("filename : ")  # Open the file, in Python 2.x: raw_inpRPi.pngut
    img = Image.open(file).convert('1')  # Open and convert to black and white
    display_img(img)
except:
    print("Program termination reason: ", sys.exc_info())

spi.close()
GPIO.cleanup()
