import pygame 
from pygame.locals import * # for event MOUSE variables
import os 
import RPi.GPIO as GPIO
import sys
import time
import board
import adafruit_sht31d
import json
import math
import textwrap

os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
os.putenv('SDL_FBDEV', '/dev/fb0') 
os.putenv('SDL_MOUSEDRV', 'TSLIB') # Track mouse clicks on piTFT 
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

GPIO.setmode(GPIO.BCM)

Running = True
dirpath = "/home/pi/final_project/"

# Quit button 
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
def gpio27_callback(channel):
    global Running
    Running = False
    # sys.exit()
GPIO.add_event_detect(27,GPIO.FALLING,callback=gpio27_callback)

# Setup GPIOs
GPIO.setup(19, GPIO.OUT) # GPIO 19 for controlling the pump
GPIO.setup(13, GPIO.OUT) # GPIO 13 for controlling buzzer
GPIO.setup(26, GPIO.IN) # GPIO 26 for reading soil moisture sensor
GPIO.setup(6, GPIO.IN) # GPIO 6 for reading water level sensor
GPIO.output(19,GPIO.HIGH)
GPIO.output(13,GPIO.LOW)
buzzer = GPIO.PWM(13,1000)
# pump = GPIO.PWM(19, 1000)

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()
sensor = adafruit_sht31d.SHT31D(i2c)

# Pygame
pygame.init()
pygame.mouse.set_visible(False)
size = width, height = 320, 240
black = 0, 0, 0
white = 255, 255, 255
gold= 252,233,79
red=225,48,48
green=118,238,198
blue=99,184,255
darkg=0,100,0
screen = pygame.display.set_mode(size)
my_font = pygame.font.Font(None,20)

#import photos

# temperature in celsuis
desire_temp_min = 15
desire_temp_max = 40

# relative humidity in Percentage
desire_humi_min = 20
desire_humi_max = 50

#Sunlight
desire_sunlight = "unknown"

# water level output text and color
water_level_output = "No"
water_level_color  = green

# temperature color
temp_color = green

# Humidity color
humi_color = green

# Soil Dryness Check (Inch)
Soil_Dryness_Check = 1.5

# Intro
introduction = "none"

init = True
init_menu = 1
working = 2
select_plant = 3
display_plant = 4


page = 1

max_page_num = 1
num_plant = 1

reset_timer = 60*60*6* 10  # 6 hours interval between waterings, 10 because time.sleep is 0.1
# reset_timer = 5
watering_time = 20 # 10 seconds of watering
timer = 0

water_time = watering_time
pump_flag = 0 

FSM_state = init_menu

f = open(dirpath+'plants.json')
data = json.load(f)
plant_info = data['Plants']
num_plant = len(plant_info)


start_menu_buttons = { 'Start':(160,160)}
# select_plant_buttons = {"Satin Pothos":(70,50), 'plant2':(160,50),'plant3':(250,50),'plant4':(70,100), 'plant5':(160,100),'plant6':(250,100),'plant7':(70,150), 'plant8':(160,150),'plant9':(250,150)}


select_plant_buttons = {(70,50):'Satin Pothos', (160,50):'plant2',(250,50):'plant3',(70,100):'plant4', (160,100):'plant5',(250,100):'plant6',(70,150):'plant7', (160,150):'plant8',(250,150):'plant9'}
for i in range(num_plant):
    select_plant_buttons[list(select_plant_buttons)[i]] = list(plant_info)[i]


selected_plant = "plant1"
display_plant_buttons = {'Back':(80,200),'Confirm':(240,200)}

while Running:

    if FSM_state == init_menu:  
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if(event.type is MOUSEBUTTONDOWN):
                pos = pygame.mouse.get_pos()
            elif(event.type is MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                x,y = pos
                if(x>150 and x < 170 and y > 150 and y < 170):
                    FSM_state = select_plant
        screen.fill(black)
        for my_text, text_pos in start_menu_buttons.items():
            text_surface = my_font.render(my_text, True, white)
            rect = text_surface.get_rect(center=text_pos)
            screen.blit(text_surface,rect) 
        sys_font = pygame.font.Font(None,40)
        text_surface = sys_font.render("Automatic Water System", True, white)
        rect = text_surface.get_rect(center=(160,80))
        screen.blit(text_surface,rect) 

    if FSM_state == select_plant:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if(event.type is MOUSEBUTTONDOWN):
                pos = pygame.mouse.get_pos()
            elif(event.type is MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                x,y = pos
                if( x > 150 and x < 170 and y > 190 and y < 210 and init == False):
                    FSM_state = working
                if(x>50 and x<90 and y > 30 and y < 70 and num_plant >= 1):
                    selected_plant = list(select_plant_buttons.values())[0]
                    FSM_state = display_plant
                elif(x>140 and x<180 and y > 30 and y < 70 and num_plant >= 2):
                    selected_plant = list(select_plant_buttons.values())[1]
                    FSM_state = display_plant
                elif(x>230 and x<270 and y > 30 and y < 70 and num_plant >= 3):
                    selected_plant = list(select_plant_buttons.values())[2]
                    FSM_state = display_plant
                elif(x>50 and x<90 and y > 80 and y < 120 and num_plant >= 4):
                    selected_plant = list(select_plant_buttons.values())[3]
                    FSM_state = display_plant
                elif(x>140 and x<180 and y > 80 and y < 120 and num_plant >= 5):
                    selected_plant = list(select_plant_buttons.values())[4]
                    FSM_state = display_plant
                elif(x>230 and x<270 and y > 80 and y < 120 and num_plant >= 6):
                    selected_plant = list(select_plant_buttons.values())[5]
                    FSM_state = display_plant
                if(FSM_state == display_plant):
                    desire_temp_min = int(plant_info[selected_plant]['Temp Min'])
                    desire_temp_max = int(plant_info[selected_plant]['Temp Max'])
                    desire_humi_min = int(plant_info[selected_plant]['Humidity Min'])
                    desire_humi_max = int(plant_info[selected_plant]['Humidity Max'])
                    desire_sunlight = plant_info[selected_plant]['Sunlight']
                    introduction      = plant_info[selected_plant]['intro']

                
                
        # num_plant = len(select_plant_buttons)
        screen.fill(black)
        plant_idx = 0
        my_font_plant = pygame.font.Font(None,15)
        for text_pos, my_text in select_plant_buttons.items():
            if plant_idx < num_plant:
                text_surface = my_font_plant.render(my_text, True, white)
                rect = text_surface.get_rect(center=text_pos)
                screen.blit(text_surface,rect) 
            plant_idx += 1

        if init == False:
            text_surface = my_font.render("Back", True, white)
            rect = text_surface.get_rect(center=(160,200))
            screen.blit(text_surface,rect) 

    if FSM_state == display_plant:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if(event.type is MOUSEBUTTONDOWN):
                pos = pygame.mouse.get_pos()
            elif(event.type is MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                x,y = pos
                if(y> 180 and x < 100 and x > 20): # back
                    FSM_state = select_plant
                if(y> 180 and x > 200 and x < 280): # confirm
                    init = False
                    GPIO.output(13,GPIO.LOW)
                    FSM_state = working
                    timer = 0

        screen.fill(black)
        potted_plant=pygame.image.load("/home/pi/final_project/" + selected_plant +".bmp")
        potted_plant = pygame.transform.scale(potted_plant,(130,130))
        potted_plantrect = potted_plant.get_rect()
        potted_plantrect = potted_plantrect.move(0,0)
        screen.blit(potted_plant, potted_plantrect)
        for my_text, text_pos in display_plant_buttons.items():
            button_color = green
            if my_text == "Back":
                button_color = red
            text_surface = my_font.render(my_text, True, button_color)
            rect = text_surface.get_rect(center=text_pos)
            screen.blit(text_surface,rect) 
        intro = my_font.render("Introduction:", True, white)
        intro_rect = intro.get_rect(center=[200,15])
        screen.blit(intro,intro_rect)


        col = 30
        intro_list = textwrap.wrap(introduction,28)
        intro_font = pygame.font.Font(None,17)
        for i in range(len(intro_list)):
            intro_disp = intro_font.render(intro_list[i], True, white)
            intro_disp_rect = intro_disp.get_rect(center=[220,col])
            screen.blit(intro_disp,intro_disp_rect)
            col += 10


                

    if FSM_state == working:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                GPIO.cleanup()
                sys.exit()
            if(event.type is MOUSEBUTTONDOWN):  
                pos = pygame.mouse.get_pos()
            elif(event.type is MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                x,y = pos

                if(y>180 and y<210 and x > 140 and x < 170):
                    FSM_state = select_plant

        
        if GPIO.input(26) == GPIO.LOW:
            GPIO.output(19,GPIO.HIGH)
        else:  
            if timer > 0:
                timer -= 1
                GPIO.output(19,GPIO.HIGH)
            else:
                if water_time > 0:
                    water_time -= 1
                    GPIO.output(19,GPIO.LOW)
                    time.sleep(1)
                    GPIO.output(19,GPIO.HIGH)
                else: 
                    timer = reset_timer
                    water_time = watering_time
        
        

        # Temperature Check
        buzzer.stop()
        if(sensor.temperature < desire_temp_min or sensor.temperature > desire_temp_max):
            GPIO.output(13,GPIO.HIGH)
            buzzer.start(50)
            temp_color = red
        else:
            GPIO.output(13,GPIO.LOW)
            temp_color = green

        # Humidity Check
        if(sensor.relative_humidity < desire_humi_min or sensor.relative_humidity > desire_humi_max):
            humi_color = red
        else:
            GPIO.output(13,GPIO.LOW)
            humi_color = green

        # Water Level Check
        if( GPIO.input(6) == GPIO.LOW ):
            water_level_output = "Yes"
            water_level_color = red
        else:
            water_level_output = "No"
            water_level_color = green
        
        screen.fill(black)
        potted_plant=pygame.image.load("/home/pi/final_project/"+selected_plant+".bmp")
        potted_plant = pygame.transform.scale(potted_plant,(105,105))
        potted_plantrect = potted_plant.get_rect()
        potted_plantrect = potted_plantrect.move(105,50)
        screen.blit(potted_plant, potted_plantrect)

        sunlight=pygame.image.load("/home/pi/final_project/sunlight.bmp")
        sunlight = pygame.transform.scale(sunlight,(30,30))
        sunlightrect = sunlight.get_rect()
        sunlightrect = sunlightrect.move(60,20)
        screen.blit(sunlight, sunlightrect)

        humidity=pygame.image.load("/home/pi/final_project/humidity.bmp")
        humidity = pygame.transform.scale(humidity,(30,30))
        humidityrect = humidity.get_rect()
        humidityrect = humidityrect.move(70,90)
        screen.blit(humidity, humidityrect)

        humidity2=pygame.image.load("/home/pi/final_project/humidity.bmp")
        humidity2 = pygame.transform.scale(humidity2,(30,30))
        humidityrect2 = humidity2.get_rect()
        humidityrect2 = humidityrect2.move(285,20)
        screen.blit(humidity2, humidityrect2)

        temperature=pygame.image.load("/home/pi/final_project/temp.bmp")
        temperature = pygame.transform.scale(temperature,(30,30))
        temperaturerect = temperature.get_rect()
        temperaturerect = temperaturerect.move(70,170)
        screen.blit(temperature, temperaturerect)

        temperature2=pygame.image.load("/home/pi/final_project/temp.bmp")
        temperature2 = pygame.transform.scale(temperature2,(30,30))
        temperaturerect2 = temperature2.get_rect()
        temperaturerect2 = temperaturerect2.move(285,120)
        screen.blit(temperature2, temperaturerect2)

        #draw line
        pygame.draw.lines(screen,gold,False,[[105,0],[105,240]],2)
        pygame.draw.lines(screen,green,False,[[210,0],[210,240]],2)
        pygame.draw.lines(screen,white,False,[[0,15],[105,15]],2)
        pygame.draw.lines(screen,white,False,[[0,90],[105,90]],2)
        pygame.draw.lines(screen,white,False,[[0,170],[105,170]],2)
        pygame.draw.lines(screen,white,False,[[210,15],[320,15]],2)
        pygame.draw.lines(screen,white,False,[[210,120],[320,120]],2)
        pygame.draw.lines(screen,white,False,[[210,200],[320,200]],2)


        # Text Print
        #plant name
        text_surface = my_font.render("Satin Pothos", True, darkg)
        rect = text_surface.get_rect(center=[160,20])
        screen.blit(text_surface,rect)
        #switch Plant
        text_surface = my_font.render("Switch Plant", True, blue)
        rect = text_surface.get_rect(center=[160,200])
        screen.blit(text_surface,rect)
        #goal text
        text_surface = my_font.render("Goal", True, gold)
        rect = text_surface.get_rect(center=[30,10])
        screen.blit(text_surface,rect)
        #Light
        text_surface = my_font.render("Sunlight", True, white)
        rect = text_surface.get_rect(center=[30,30])
        screen.blit(text_surface,rect)
        #light parameter
        font_light = pygame.font.Font(None,17)
        text_surface = font_light.render(desire_sunlight, True, gold)
        rect = text_surface.get_rect(center=[48,60])
        screen.blit(text_surface,rect)
        #humidity level
        text_surface = my_font.render("Humidity", True, white)
        rect = text_surface.get_rect(center=[30,100])
        screen.blit(text_surface,rect)
        #humidity paratmeter 1
        text_surface = my_font.render(str(desire_humi_min) + " ~ " + str(desire_humi_max) +"%", True,gold)
        rect = text_surface.get_rect(center=[40,140])
        screen.blit(text_surface,rect)
        #Room Temp
        text_surface = my_font.render("Temp(C)", True, white)
        rect = text_surface.get_rect(center=[30,180])
        screen.blit(text_surface,rect)
        #Room Temp parameter 1
        text_surface = my_font.render(str(desire_temp_min) + " ~ " + str(desire_temp_max) + " C", True, gold)
        rect = text_surface.get_rect(center=[40,210])
        screen.blit(text_surface,rect)
        #Current Situation
        text_surface = my_font.render("Current Status", True, green)
        rect = text_surface.get_rect(center=[265,10])
        screen.blit(text_surface,rect)
        #Current Humidity
        text_surface = my_font.render("Humidity", True, white)
        rect = text_surface.get_rect(center=[250,30])
        screen.blit(text_surface,rect)
        #humidity paratmeter 2
        text_surface = my_font.render(str(round(sensor.relative_humidity,1)) + "%", True,humi_color)
        rect = text_surface.get_rect(center=[260,90])
        screen.blit(text_surface,rect)
        #Current Temp
        text_surface = my_font.render("Temp(C)", True, white)
        rect = text_surface.get_rect(center=[250,130])
        screen.blit(text_surface,rect)
        #Room Temp parameter 1
        text_surface = my_font.render(str(round(sensor.temperature,1)) + " C", True, temp_color)
        rect = text_surface.get_rect(center=[260,170])
        screen.blit(text_surface,rect)
        #Water Level
        text_surface = my_font.render("Adding water?", True, white)
        rect = text_surface.get_rect(center=[265,210])
        screen.blit(text_surface,rect)
        #Yes or No for water level
        text_surface = my_font.render(water_level_output, True, water_level_color)
        rect = text_surface.get_rect(center=[265,230])
        screen.blit(text_surface,rect)

    pygame.display.flip()
    time.sleep(0.1)
GPIO.cleanup()
