from hw_models import *
from hardware import *
from triggers import check_triggers
from threading import Thread, Event, Timer, current_thread
from time import sleep
from datetime import datetime, timedelta
from utils.utils import time_in_range
from scheduler.scheduler import schedule

#frequency at which sensors are updated
poll_sensor_interval = 5

#frequency at which pump / fan daemons check instructions
monitor_action_interval = 10

pump_jobs = {}
fan_daemons = {}

light_jobs = {}

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
		spawn_pump_daemon(pump)
	for fan in Fan.select().where(Fan.group != None):
		spawn_fan_daemon(fan.id)
	for light in Light.select().where(Light.group != None):
		spawn_light_daemon(light, light.group)

#################################################################
#					Schedule Lights
#################################################################

#@catch_exceptions(cancel_on_failure=False)
def lights_on(light):
	gpio_out(light.gpio_pin, True)
	light.group.light_status = True
	light.group.save()

#@catch_exceptions(cancel_on_failure=False)
def lights_off(light):
	gpio_out(light.gpio_pin, False)
	light.group.light_status = False
	light.group.save()

def spawn_light_daemon(light, group):
	print '        scheduling light: ', light.name
	start_time = group.light_start_time
	stop_time = group.light_stop_time

	start_job = schedule.every().day.at(start_time.strftime('%H:%M')).do(lights_on, light)
	stop_job = schedule.every().day.at(stop_time.strftime('%H:%M')).do(lights_off, light)

	#store the jobs in dict as a tuple
	light_jobs[light.id] = (start_job, stop_job)

	#prepare the job
	gpio_setup_out(light.gpio_pin)

	#turn on light & update status if currently needs to be on
	current_time = datetime.now().time()
	if time_in_range(start_time, stop_time, current_time):
		gpio_out(light.gpio_pin, True)
		light.group.light_status = True
		light.group.save()
	else:
		light.group.light_status = False
		light.group.save()

def kill_light_daemon(light):
	print '        unscheduling light: ', light.name
	jobs = light_jobs[light.id]
	for job in jobs:
		schedule.cancel_job(job)
	light_jobs.pop(light.id)
	#clear light status if no more lights
	if Light.select().where(Light.group == light.group).count() == 1:
		light.group.light_status = None
		light.group.save()

#################################################################
#				Poll & Monitor Sensors
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
	check_therm()
	check_hygro()
	for group in HardwareGroup.select():
		check_triggers(group)

def start_sensor_poller():
	schedule.every(poll_sensor_interval).seconds.do(sensor_poller)

#################################################################
#					Monitor Pumps for Action
#################################################################

def pump_monitor(pump):
	#if we need to pump
	if pump.group.pump_status:
		#pump for run time percent until the next check
		gpio_out(pump.gpio_pin, True)
		sleep(monitor_action_interval * pump.run_time / 100)
		gpio_out(pump.gpio_pin, False)

def spawn_pump_daemon(pump):
	print '        spawning daemon for ', pump.name
	gpio_setup_out(pump.gpio_pin)
	job = schedule.every(monitor_action_interval).seconds.do(pump_monitor, pump)
	pump_jobs[pump.id] = job

def kill_pump_daemon(pump):
	print 'killing daemon for ', pump.name
	job = pump_jobs[pump.id]
	schedule.cancel_job(job)
	gpio_out(pump.gpio_pin, False)

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

















