import time
import os
import threading
from datetime import datetime
import board
import adafruit_dht
import sqlite3
from exif import Image

picture_path = "/home/pi/Desktop/garden-monitor-new/static/images"
database_path = "/home/pi/Desktop/garden-monitor-new/data.db"
image_name = "image"

get_number = lambda path: int(os.path.splitext(os.path.split(path)[1])[0][len(image_name):])
#get number of image file then add 1
#counter = int(os.path.splitext(max(os.listdir(picture_path), key=get_number))[0][len(image_name):]) + 1
sensor = adafruit_dht.DHT11(board.D4)

running = True
take_measurement = True
take_picture = True

#connect to database, return connection
def initialize_db():
	try:
		database = sqlite3.connect(database_path)
	except sqlite3.Error as error:
		print(error.args[0])
	return database

#take and store image via command line
def store_picture(path):
	if os.path.exists(path) == False:
		os.mkdir(path)
	
	counter = int(os.path.splitext(max(os.listdir(picture_path), key=get_number))[0][len(image_name):]) + 1
	
	filename = path + "/" + image_name + (str)(counter) + ".jpg"

	data = "fswebcam " + filename
	os.system(data)

	#write exif data
	file = open(filename, "rb")
	exiftags = Image(file)
	exiftags.datetime = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
	file.close()
	new_file = open(filename, "wb")
	new_file.write(exiftags.get_file())
	new_file.close()
	
# use DHT11
def find_temp():
	working = False
	while not working:
		try:
			temperature = sensor.temperature
			if temperature != None:
				working = True
		except RuntimeError as error:
			print("Error " + error.args[0])
	return (temperature * 9 / 5) + 32
	
def find_humidity():
	working = False
	while not working:
		try:
			humidity = sensor.humidity
			if humidity != None:
				working = True
		except RuntimeError as error:
			print("Error " + error.args[0])
	return humidity
	
#read humidity and tempurature and store in the database
def store_data(database):
	temperature = find_temp()
	humidity = find_humidity()
	
	sql_command = "INSERT INTO data (humidity, temperature, time) VALUES (%s, %s, datetime('now'));" % (temperature, humidity)
	
	try:
		cursor = database.cursor()
		cursor.execute(sql_command)
		database.commit()
	except sqlite3.Error as error:
		print(error.args[0])
		
#handle timing
def control_loop():
	global take_measurement
	global take_picture
	while running:
		time.sleep(300)
		take_measurement = True
		time.sleep(300)
		take_measurement = True
		take_picture = True
		
#responsible for calling functions
def function_loop(database):
	global take_measurement
	global take_picture
	while running:
		if take_measurement == True:
			store_data(database)
			take_measurement = False
		if take_picture == True:
			store_picture(picture_path)
			take_picture = False
		time.sleep(1)
			
#start the program
def initialize_all():
	database = initialize_db()
	
	YourMomThread = threading.Thread(target=control_loop)
	
	YourMomThread.start()
	function_loop(database)
	
	print('::Closing the Datbase')
	database.close()
	
initialize_all()
