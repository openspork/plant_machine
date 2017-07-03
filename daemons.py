from hw_models import *
from hardware import *
from threading import Thread
import time

poll_interval = 5
monitor_interval = 15

def init_hw():
	print 'hw init'
	for group in HardwareGroup.select():
		group.pump_status = False
		group.fan_status = False

	gpio_set_mode()
	for pump in Pump.select():
		gpio_setup_out(pump.gpio_pin)
	for fan in Fan.select():
		gpio_setup_out(fan.gpio_pin)

def check_therm():
	for soil_therm in SoilThermometer.select():
		soil_therm.curr_reading = get_temp(soil_therm.address)[1]
		soil_therm.save()

def check_hygro():
	for soil_hygro in SoilHygrometer.select():
		soil_hygro.curr_reading = get_moisture(soil_hygro.channel)
		soil_hygro.save()

def poller():
	while True:
		check_therm()
		check_hygro()
		time.sleep(poll_interval)	

def start_poller():
	thread = Thread(target = poller, name = 'poller')
	thread.setDaemon(True)
	thread.start()

def check_triggers():
	print '\nchecking triggers:\n'
	for group in HardwareGroup.select():
		print '    processing group', group.name
		#handle therm sensors
		for soil_therm in group.soil_thermometers.select():
			#handle pumps
			print '        processing therm', soil_therm.name, ': curr reading: ', soil_therm.curr_reading, 'pump thresh: ', group.pump_temp_threshold
			if (soil_therm.curr_reading > group.pump_temp_threshold):
				print '        therm past pump threshold'
				if not group.pump_status:
					print '        not yet pumping'
					for pump in group.pumps:
						print '            starting pumping\n'
						gpio_out(pump.gpio_pin, True)
						group.pump_status = True
						group.save()
				else:
					print '            pumps already started\n'
			elif (soil_therm.curr_reading <= group.pump_temp_threshold):
				print '        therm below threshold'
				if group.pump_status:
					print '        still pumping'
					for pump in group.pumps:
						print '            stopping pumping\n'
						gpio_out(pump.gpio_pin, False)
						group.pump_status = False
						group.save()
				else:
					print '            pumps already stopped\n'
			#handle fans
			print '        processing therm', soil_therm.name, ': curr reading: ', soil_therm.curr_reading, 'fan thresh: ', group.fan_temp_threshold
			if (soil_therm.curr_reading > group.fan_temp_threshold):
				print '        therm past fan threshold'
				if not group.fan_status:
					print '        not yet fanning'
					for fan in group.fans:
						print '            starting fanning\n'
						gpio_out(fan.gpio_pin, True)
						group.fan_status = True
						group.save()
				else:
					print '            fans already started\n'
			elif (soil_therm.curr_reading <= group.fan_temp_threshold):
				print '        therm below threshold'
				if group.fan_status:
					print '        still fanning'
					for fan in group.fans:
						print '            stopping fanning\n'
						gpio_out(fan.gpio_pin, False)
						group.fan_status = False
						group.save()
				else:
					print '            fans already stopped\n'

		#handle moisture sensors
		for soil_hygro in group.soil_hygrometers.select():
			#handle pumps
			print '        processing hygro', soil_hygro.name, ': curr reading: ', soil_hygro.curr_reading, 'pump thresh: ', group.pump_temp_threshold
			if (soil_hygro.curr_reading > group.pump_temp_threshold):
				print '        hygro past pump threshold'
				if not group.pump_status:
					print '        not yet pumping'
					for pump in group.pumps:
						print '            starting pumping\n'
						gpio_out(pump.gpio_pin, True)
						group.pump_status = True
						group.save()
				else:
					print '            pumps already started\n'
			elif (soil_hygro.curr_reading <= group.pump_temp_threshold):
				print '        hygro below threshold'
				if group.pump_status:
					print '        still pumping'
					for pump in group.pumps:
						print '            stopping pumping\n'
						gpio_out(pump.gpio_pin, False)
						group.pump_status = False
						group.save()
				else:
					print '            pumps already stopped\n'
			#handle fans
			print '        processing hygro', soil_hygro.name, ': curr reading: ', soil_hygro.curr_reading, 'fan thresh: ', group.fan_temp_threshold
			if (soil_hygro.curr_reading > group.fan_temp_threshold):
				print '        hygro past fan threshold'
				if not group.fan_status:
					print '        not yet fanning'
					for fan in group.fans:
						print '            starting fanning\n'
						gpio_out(fan.gpio_pin, True)
						group.fan_status = True
						group.save()
				else:
					print '            fans already started\n'
			elif (soil_hygro.curr_reading <= group.fan_temp_threshold):
				print '        hygro below threshold'
				if group.fan_status:
					print '        still fanning'
					for fan in group.fans:
						print '            stopping fanning\n'
						gpio_out(fan.gpio_pin, False)
						group.fan_status = False
						group.save()
				else:
					print '            fans already stopped\n'

def monitor():
	while True:
		check_triggers()
		time.sleep(monitor_interval)

def start_monitor():
	init_hw()
	thread = Thread(target = monitor, name = 'monitor')
	thread.setDaemon(True)
	thread.start()