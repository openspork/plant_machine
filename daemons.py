from hw_models import *
from hardware import *
import threading
import time

poll_interval = 10

def init_hw():
	print 'hw init'
	gpio_set_mode()
	for pump in Pump.select():
		gpio_setup_out(pump.gpio_pin)
	for fan in Fan.select():
		gpio_setup_out(fan.gpio_pin)

def check_therm():
	for soil_therm in SoilThermometer.select().where(SoilThermometer.group):
		temp = get_temp(soil_therm.address)[1]
		soil_therm.curr_reading = temp
		soil_therm.save()

		if temp > soil_therm.pump_threshold:
			print 'turning on pumps for group', soil_therm.group.name
			for pump in soil_therm.group.pumps:
				gpio_out(pump.gpio_pin, True)
				print 'pump on:', pump.name
		else:
			for pump in soil_therm.group.pumps:
				gpio_out(pump.gpio_pin, False)
				print 'pump off:', pump.name

		if temp > soil_therm.fan_threshold:
			print 'turning on fans for group', soil_therm.group.name
			for fan in soil_therm.group.fans:
				gpio_out(fan.gpio_pin, True)
				print 'fan on:', fan.name
		else:
			for fan in soil_therm.group.fans:
				gpio_out(fan.gpio_pin, False)
				print 'fan off:', fan.name

def check_hygro():
	for soil_hygro in SoilHygrometer.select().where(SoilHygrometer.group):
		moisture = get_moisture(soil_hygro.channel)
		soil_hygro.curr_reading = moisture
		soil_hygro.save()

		if moisture > soil_hygro.pump_threshold:
			print 'turning on pumps for group', soil_hygro.group.name
			for pump in soil_hygro.group.pumps:
				gpio_out(pump.gpio_pin, True)
				print 'pump on', pump.name
		else:
			for pump in soil_hygro.group.pumps:
				gpio_out(pump.gpio_pin, False)
				print 'pump off', pump.name

		if moisture > soil_hygro.fan_threshold:
			print 'turning on fans for group', soil_hygro.group.name
			for fan in soil_hygro.group.fans:
				gpio_out(fan.gpio_pin, True)
				print 'fan on', fan.name
		else:
			for fan in soil_hygro.group.fans:
				gpio_out(fan.gpio_pin, False)
				print 'fan off', fan.name

#polling daemon
class poller(threading.Thread):
	def __init__(self):
		print 'poller init'
		init_hw()
		threading.Thread.__init__ (self)

	def run(self):
		while True:
			check_therm()
			check_hygro()
			time.sleep(poll_interval)












