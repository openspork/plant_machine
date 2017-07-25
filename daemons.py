from hw_models import *
from hardware import *
from triggers import check_triggers
from threading import Thread, Event
from time import sleep
from datetime import timedelta

poll_sensor_interval = 5
monitor_sensor_interval = 10
monitor_action_interval = 2

pump_daemons = {}
fan_daemons = {}

#################################################################
#					Poll Sensors for Data
#################################################################

def check_therm():
	for soil_therm in SoilThermometer.select():
		soil_therm.curr_reading = get_temp(soil_therm.address)[1]
		soil_therm.save()

def check_hygro():
	for soil_hygro in SoilHygrometer.select():
		soil_hygro.curr_reading = get_moisture(soil_hygro.channel)
		soil_hygro.save()

def sensor_poller():
	while True:
		check_therm()
		check_hygro()
		sleep(poll_sensor_interval)	

def start_sensor_poller():
	sensor_poller_daemon = Thread(target = sensor_poller, name = 'sensor_poller')
	sensor_poller_daemon.setDaemon(True)
	sensor_poller_daemon.start()

#################################################################
#					Monitor Polled Sensor Data
#################################################################

def sensor_monitor():
	while True:
		for group in HardwareGroup.select():
			check_triggers(group.id)
		sleep(monitor_sensor_interval)

def start_sensor_monitor():
	init_hw()
	sensor_monitor_daemon = Thread(target = sensor_monitor, name = 'sensor_monitor')
	sensor_monitor_daemon.setDaemon(True)
	sensor_monitor_daemon.start()

#################################################################
#					Monitor Pumps for Action
#################################################################

def pump_monitor(pump_id, stop_event):
	while not stop_event.is_set():
		pump = Pump.get(Pump.id == pump_id)
		group = pump.group
		#print '            pump daemon running for:', pump.name, 'group:', group.name, 'status:', group.pump_status
		#while the pump's group is pumping
		if pump.group.pump_status:
			#pump for the run time
			gpio_out(pump.gpio_pin, True)
			sleep(pump.run_time)
			#stop for the sleep time
			gpio_out(pump.gpio_pin, False)
			sleep(pump.sleep_time)
		#wait to recheck the group's pumping status
		else:
			sleep(monitor_action_interval)
	print '            pump daemon ending for:', pump.name
	#turn off pin before end
	gpio_out(pump.gpio_pin, False)

def spawn_pump_daemon(pump_id):
	pump = Pump.get(Pump.id == pump_id)
	print '        spawning daemon for ', pump.name
	gpio_setup_out(pump.gpio_pin)
	kill_pump_monitor_daemon_event = Event()
	pump_monitor_daemon = Thread(target = pump_monitor, name = pump.name + '_monitor', args = (pump.id, kill_pump_monitor_daemon_event))
	pump_monitor_daemon.setDaemon(True)
	pump_monitor_daemon.start()
	pump_daemons[pump.id] = kill_pump_monitor_daemon_event

def kill_pump_daemon(pump_id):
	pump = Pump.get(Pump.id == pump_id)
	print 'killing daemon for ', pump.name
	pump_daemons[pump.id].set()

#################################################################
#					Monitor Fans for Action
#################################################################

def fan_monitor(fan_id, stop_event):
	while not stop_event.is_set():
		fan = Fan.get(Fan.id == fan_id)
		group = fan.group
		#print '            fan daemon running for:', fan.name, 'group:', group.name, 'status:', group.fan_status
		#while the fan's group is fanning
		if fan.group.fan_status:
			#fan for the run time
			gpio_out(fan.gpio_pin, True)
			sleep(fan.run_time)
			#stop for the sleep time
			gpio_out(fan.gpio_pin, False)
			sleep(fan.sleep_time)
		#wait to recheck the group's fanning status
		else:
			sleep(monitor_action_interval)
	print '            fan daemon ending for:', fan.name
	#turn off pin before end
	gpio_out(fan.gpio_pin, False)

def spawn_fan_daemon(fan_id):
	fan = Fan.get(Fan.id == fan_id)
	print '        spawning daemon for ', fan.name
	gpio_setup_out(fan.gpio_pin)
	kill_fan_monitor_daemon_event = Event()
	fan_monitor_daemon = Thread(target = fan_monitor, name = fan.name + '_monitor', args = (fan.id, kill_fan_monitor_daemon_event))
	fan_monitor_daemon.setDaemon(True)
	fan_monitor_daemon.start()
	fan_daemons[fan.id] = kill_fan_monitor_daemon_event

def kill_fan_daemon(fan_id):
	fan = Fan.get(Fan.id == fan_id)
	print 'killing daemon for ', fan.name
	fan_daemons[fan.id].set()

#################################################################
#					Init HW for Daemons
#################################################################
def init_hw():
	print 'hw init'
	gpio_set_mode()
	for group in HardwareGroup.select():
		group.pump_status = False
		group.fan_status = False

	for pump in Pump.select().where(Pump.group != None):
		spawn_pump_daemon(pump.id)
	for fan in Fan.select().where(Fan.group != None):
		spawn_fan_daemon(fan.id)















