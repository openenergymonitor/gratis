# Copyright 2013 Pervasive Displays, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language
# governing permissions and limitations under the License.


import sys
import os
import Image
import ImageDraw
import ImageFont
from datetime import datetime
import time
from EPD import EPD
import smbus
import urllib2
import RPi.GPIO as GPIO


URL="emoncms.org"
API="c0c644bb3f86eab9e308668b5bef6b51"
powerID="78793"
kwhID="74684"

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GREEN_led=12
BLUE_led=5
RED_led=6

# LOW when pressed 
LEFT_button=19
RIGHT_button=16

GPIO.setup(GREEN_led, GPIO.OUT) 
GPIO.setup(BLUE_led, GPIO.OUT) 
GPIO.setup(RED_led, GPIO.OUT)

GPIO.setup(LEFT_button,GPIO.IN, pull_up_down=GPIO.PUD_UP)   
GPIO.setup(RIGHT_button,GPIO.IN, pull_up_down= GPIO.PUD_UP) 





GPIO.output(RED_led,True) 
time.sleep(1)
GPIO.output(RED_led,False) 
GPIO.output(GREEN_led,True)
time.sleep(1)
GPIO.output(GREEN_led,False)
GPIO.output(BLUE_led,True)
time.sleep(1)
GPIO.output(BLUE_led,False)


bus = smbus.SMBus(1)
addr_temp = 0x49

WHITE = 1
BLACK = 0

# fonts are in different places on Raspbian/Angstrom so search
possible_fonts = [
    '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf',            # Debian B.B
#    '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf',   # Debian B.B
    '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono-Bold.ttf',   # R.Pi
    '/usr/share/fonts/truetype/freefont/FreeMono.ttf',                # R.Pi
#    '/usr/share/fonts/truetype/LiberationMono-Bold.ttf',              # B.B
#    '/usr/share/fonts/truetype/DejaVuSansMono-Bold.ttf'               # B.B
]

now = datetime.today()


FONT_FILE = ''
for f in possible_fonts:
    if os.path.exists(f):
        FONT_FILE = f
        break

if '' == FONT_FILE:
    raise 'no font file found'

CLOCK_FONT_SIZE = 80

# date

if (now.month in [1, 2,  9, 10, 11, 12]):
	DATE_FONT_SIZE  = 26
	DATE_X = 5
elif (now.month in [3, 4, 8]):
	DATE_FONT_SIZE  = 28
        DATE_X = 15
else: 
	DATE_FONT_SIZE  = 32
	DATE_X = 24

DATE_Y=50

# day of week

if (now.weekday() in [1]): # Tuesday
	WEEKDAY_FONT_SIZE  = 44
	WEEKDAY_X = 40

elif (now.weekday() in [2]): # Wednesday
	WEEKDAY_FONT_SIZE  = 44
	WEEKDAY_X = 13

elif (now.weekday() in [3, 5]): # Thursday, Saturday
	WEEKDAY_FONT_SIZE  = 44
	WEEKDAY_X = 30

else:
	WEEKDAY_FONT_SIZE  = 48 # The rest
	WEEKDAY_X = 45

WEEKDAY_Y = 3

# temperature
TEMP_FONT_SIZE = 70
TEMP_X = 45
TEMP_Y = 100

# time
X_OFFSET = 10
Y_OFFSET = 95
COLON_SIZE = 5
COLON_GAP = 10


def get_temp():
#	results = bus.read_i2c_block_data(addr_temp,0)
#	Temp = results[0] << 8 | results[1]
#	Temp = Temp >> 5
	Temp = 200
	Temp = float(Temp/10)
	return Temp


def main(argv):
    """main program - draw HH:MM clock on 2.70" size panel"""

    epd = EPD()

    print('panel = {p:s} {w:d} x {h:d}  version={v:s}  cog={g:d}'.format(p=epd.panel, w=epd.width, h=epd.height, v=epd.version, g=epd.cog))

    if 'EPD 2.7' != epd.panel:
        print('incorrect panel size')
        sys.exit(1)

    epd.clear()

    demo(epd)


def demo(epd):
    """simple partial update demo - draw draw a clock"""

    # initially set all white background
    image = Image.new('1', epd.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)
    width, height = image.size

    clock_font = ImageFont.truetype(FONT_FILE, CLOCK_FONT_SIZE)
    date_font = ImageFont.truetype(FONT_FILE, DATE_FONT_SIZE)
    weekday_font = ImageFont.truetype(FONT_FILE, WEEKDAY_FONT_SIZE)
    temp_font = ImageFont.truetype(FONT_FILE, TEMP_FONT_SIZE)

    # clear the display buffer
    draw.rectangle((0, 0, width, height), fill=WHITE, outline=WHITE)
    previous_day = 0

    first_start = True

    epd.display(image)
    epd.update()
    while True:
        string=urllib2.urlopen("http://"+URL+"/feed/value.json?id="+powerID+"?api="+API).read()
        power = int(string[1:-1])

        string=urllib2.urlopen("http://"+URL+"/feed/value.json?id="+kwhID+"?api="+API).read()
        kwh=string[1:-1]

        print power
        
        while True:
        	draw.text((10, 3), 'POWER NOW:', fill=BLACK, font=date_font)
        	temp_str = str(power)+"W"
        	draw.text((45, 35), temp_str, fill=BLACK, font=temp_font)

        	draw.text((10,95), 'ENERGY TODAY:', fill=BLACK, font=date_font)
        	#temp_str = str(kwh)+"KWh"
        	temp_str="{0:.1f}".format(float(kwh))+"Kwh"
        	draw.text((20, 125), temp_str, fill=BLACK, font=date_font)

        	draw.line([(5,160),(259,160)], fill=BLACK)

        	if (GPIO.input(RIGHT_button) == 0):
        		GPIO.output(RED_led,True)
        	else:
        		GPIO.output(RED_led,False)

        	if (GPIO.input(LEFT_button) == 0):
        		GPIO.output(GREEN_led,True)
        	else:
        		GPIO.output(GREEN_led,False)





        	
        
	        epd.display(image)
	        epd.partial_update()
	        #if now.day != previous_day:
	        #    epd.update()
	        #else:
	            
	            #epd.update()

        



# main
if "__main__" == __name__:
    if len(sys.argv) < 1:
        sys.exit('usage: {p:s}'.format(p=sys.argv[0]))

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit('interrupted')
        pass
