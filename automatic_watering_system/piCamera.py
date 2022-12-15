from picamera2 import Picamera2, Preview
import time
from datetime import datetime
picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
picam2.configure(camera_config)
picam2.start()

now = datetime.now()

year = now.strftime("%Y")
month = now.strftime("%m")
day = now.strftime("%d")
time_hour = now.strftime("%H")


picam2.capture_file("/home/pi/final_project/plant_images/" + year +'_' + month +'_' + day + '_' + time_hour + ".jpg")
