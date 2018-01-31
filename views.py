from flask import Flask, abort, render_template, url_for, redirect, send_file, request, send_from_directory
from app import app
from hw_models import *
from hardware import get_temp
from daemons import spawn_pump_daemon, kill_pump_daemon, spawn_fan_daemon, kill_fan_daemon, spawn_light_daemon, kill_light_daemon
from glob import glob
from os.path import basename
from datetime import timedelta

@app.route('/<op>/<model>', methods=['POST'])
@app.route('/<op>/<model>/<id>', methods=['POST'])
def update(op, model, id = None):
	print op, model, id

	#if we have an ID, select
	if id:
		if model == 'hwg':
			instance = HardwareGroup.get(HardwareGroup.id == id)
		elif model == 'shy':
			instance = SoilHygrometer.get(SoilHygrometer.id == id)
		elif model == 'sth':
			instance = SoilThermometer.get(SoilThermometer.id == id)
		elif model == 'pmp':
			instance = Pump.get(Pump.id == id)		
		elif model == 'fan':
			instance = Fan.get(Fan.id == id)
		elif model == 'lgt':
			instance = Light.get(Light.id == id)

	#handle operation:
	if op == "add":
		print "ADDING"
		if model == 'hwg':
			instance = HardwareGroup.create(
				name = request.form['name'],
				pump_temp_threshold = request.form['pmp_temp_thresh'],
				pump_moist_threshold = request.form['pmp_moist_thresh'],
				fan_temp_threshold = request.form['fan_temp_thresh'],
				fan_moist_threshold = request.form['fan_moist_thresh'],
				light_start_time = request.form['lgt_start_time'],
				light_stop_time = request.form['lgt_stop_time']
			)

		elif model == 'sth':
			instance = SoilThermometer.create(name = request.form['name'], address = request.form['addr'])
		elif model == 'shy':
			instance = SoilHygrometer.create(name = request.form['name'], channel = request.form['chan'])
		elif model == 'pmp':
			instance = Pump.create(name = request.form['name'], gpio_pin = int(request.form['pin']), run_time = 1, sleep_time = 1)
		elif model == 'fan':
			instance = Fan.create(name = request.form['name'], gpio_pin = int(request.form['pin']), run_time = 1, sleep_time = 1)
		elif model == 'lgt':
			instance = Light.create(name = request.form['name'], gpio_pin = int(request.form['pin']), run_time = 1, sleep_time = 1)

	elif op == "ass":
		instance.group = HardwareGroup.get(HardwareGroup.id == request.form['group'])
		if model == 'pmp':
			spawn_pump_daemon(instance.id)
		elif model == 'fan':
			spawn_fan_daemon(instance.id)
		elif model == 'lgt':
			spawn_light_daemon(instance, instance.group)

	elif op == "del":
		if model == 'hwg':					
			for pump in Pump.select().where(Pump.group == instance.id):
				kill_pump_daemon(pump.id)
			for fan in Fan.select().where(Fan.group == instance.id):
				kill_fan_daemon(fan.id)
			for light in Light.select().where(Light.group == instance.id):
				kill_light_daemon(light)
		#if instance is active kill associated daemon
		elif model == 'pmp':
			if instance.group:
				kill_pump_daemon(instance.id)
		elif model == 'fan':
			if instance.group:
				kill_fan_daemon(instance.id)
		elif model == 'lgt':
			if instance.group:
				kill_light_daemon(instance)
		instance.delete_instance()

	elif op == "rem":
		if model == 'pmp':
			kill_pump_daemon(instance.id)
		elif model == 'fan':
			kill_fan_daemon(instance.id)
		elif model == 'lgt':
			kill_light_daemon(instance)
		instance.group = None
		
	instance.save()
	return redirect(url_for('index'))

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/hw_groups')
def hw_groups():
	hw_groups = HardwareGroup.select()
	return render_template('hw_groups.html', hw_groups = hw_groups)

@app.route('/unass_resources')
def unass_resources():
	hw_groups = HardwareGroup.select()
	soil_thermometers = SoilThermometer.select().where(SoilThermometer.group == None)
	soil_hygrometers = SoilHygrometer.select().where(SoilHygrometer.group == None)
	pumps = Pump.select().where(Pump.group == None)
	fans = Fan.select().where(Fan.group == None)
	lights = Light.select().where(Light.group == None)
	return render_template('unass_resources.html', hw_groups = hw_groups, soil_thermometers = soil_thermometers, soil_hygrometers = soil_hygrometers, pumps = pumps, fans = fans, lights = lights)

@app.route('/add_resources')
def add_resources():
	addresses = []
	raw_addresses = glob('/sys/bus/w1/devices/28*')
	for raw_address in raw_addresses:
		address = basename(raw_address)
		address_and_temp = (address, get_temp(address))
		addresses.append(address_and_temp)

	return render_template('add_resources.html', addresses = addresses)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')
