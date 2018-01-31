from hw_models import *
from hardware import *
from triggers import check_triggers
from threading import Thread, Event, Timer, current_thread
from time import sleep
from datetime import datetime, timedelta
import schedule
import functools
from utils.utils import time_in_range

poll_sensor_interval = 5
monitor_sensor_interval = 10
monitor_action_interval = 2

pump_daemons = {}
fan_daemons = {}

light_jobs = {}
kill_schedule_daemon_event = Event()

#################################################################
#					Scheduling
#################################################################

#catch errors
def catch_exceptions(job_func, cancel_on_failure=False):
    @functools.wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            return job_func(*args, **kwargs)
        except:
            import traceback
            print(traceback.format_exc())
            if cancel_on_failure:
                return schedule.CancelJob
    return wrapper

#job threader
def schedule_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

#check the schedule
def schedule_daemon(stop_event):
	while not stop_event.is_set():
		schedule.run_pending()
		sleep(1)
	print '            schdule daemon ending for'

#start the scheduler
def spawn_schedule_daemon():
	print 'starting job scheduler'
	daemon = Thread(target = schedule_daemon, name = 'job scheduler', args = (kill_schedule_daemon_event,))
	daemon.setDaemon(True)
	daemon.start()

#kill the scheduler
def kill_schedule_daemon():
	print 'killing scheduler'
	kill_schedule_daemon_event.set()

#################################################################
#					Schedule Lights
#################################################################

#@catch_exceptions(cancel_on_failure=False)
def lights_on(light):
	print '!!!!!!!!! turning', light.name, 'on'
	gpio_out(light.gpio_pin, True)
	light.group.light_status = True
	light.group.save()

#@catch_exceptions(cancel_on_failure=False)
def lights_off(light):
	print '!!!!!!!!! turning', light.name, 'off'
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















