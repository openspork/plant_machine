from flask import Flask, abort, render_template, url_for, redirect, send_file, request, send_from_directory
from app import app
from hw_models import *
from hardware import get_therm_addresses, get_temp
from daemons import spawn_pump_daemon, kill_pump_daemon, spawn_fan_daemon, kill_fan_daemon, spawn_light_daemon, kill_light_daemon
from datetime import datetime

#from datetime import timedelta

@app.route('/<op>/<model>', methods = ['POST'])
@app.route('/<op>/<model>/<id>', methods = ['POST'])
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
	if op == "upd":
		print "EDITING"
		if model == 'hwg':
			instance.name = request.form['hwg_name']
			instance.pump_temp_threshold = request.form['pmp_temp_thresh']
			instance.pump_moist_threshold = request.form['pmp_moist_thresh']
			instance.fan_temp_threshold = request.form['fan_temp_thresh']
			instance.fan_moist_threshold = request.form['fan_moist_thresh']
			instance.light_start_time = datetime.strptime(request.form['lgt_start_time'], '%H:%M').time()
			instance.light_stop_time = datetime.strptime(request.form['lgt_stop_time'], '%H:%M').time()
			instance.save()

			for pump in instance.pumps:
				kill_pump_daemon(pump)
				spawn_pump_daemon(pump)
			for fan in instance.fans:
				kill_fan_daemon(fan)
				spawn_fan_daemon(fan)
			for light in instance.lights:
				kill_light_daemon(light)
				spawn_light_daemon(light, instance)

	elif op == "add":
		print "ADDING"
		if model == 'hwg':
			instance = HardwareGroup.create(
				hwg_name = request.form['name'],
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
			instance = Pump.create(name = request.form['name'], gpio_pin = int(request.form['pin']), run_time = 100)
		elif model == 'fan':
			instance = Fan.create(name = request.form['name'], gpio_pin = int(request.form['pin']), run_time = 100)
		elif model == 'lgt':
			instance = Light.create(name = request.form['name'], gpio_pin = int(request.form['pin']))
		instance.save()

	elif op == "ass":
		instance.group = HardwareGroup.get(HardwareGroup.id == request.form['group'])
		if model == 'pmp':
			spawn_pump_daemon(instance)
		elif model == 'fan':
			spawn_fan_daemon(instance)
		elif model == 'lgt':
			spawn_light_daemon(instance, instance.group)
		instance.save()

	elif op == "del":
		if model == 'hwg':					
			for pump in Pump.select().where(Pump.group == instance.id):
				kill_pump_daemon(pump)
				pump.group = None
			for fan in Fan.select().where(Fan.group == instance.id):
				fan.group = None
				kill_fan_daemon(fan)
			for light in Light.select().where(Light.group == instance.id):
				light.group = None
				kill_light_daemon(light)
		#if instance is active kill associated daemon
		elif model == 'pmp':
			if instance.group:
				kill_pump_daemon(instance)
		elif model == 'fan':
			if instance.group:
				kill_fan_daemon(instance)
		elif model == 'lgt':
			if instance.group:
				kill_light_daemon(instance)
		instance.delete_instance()

	elif op == "rem":
		if model == 'pmp':
			kill_pump_daemon(instance)
		elif model == 'fan':
			kill_fan_daemon(instance)
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
	return render_template(
		'unass_resources.html',
		hw_groups = hw_groups,
		soil_thermometers = soil_thermometers,
		soil_hygrometers = soil_hygrometers,
		pumps = pumps,
		fans = fans,
		lights = lights)

@app.route('/add_resources')
def add_resources(query = False):
	addresses_and_temps = []
	for address in get_therm_addresses():
		if query:
			address_and_temp = (address, get_temp(address))
		else:
			address_and_temp = (address, None)
		addresses_and_temps.append(address_and_temp)	

	return render_template('add_resources.html', addresses = addresses_and_temps)

@app.route('/add_resources/query')
def add_resources_query():
	return add_resources(query = True)

@app.route('/add_resources/query_hw', methods = ['POST'])
def query_hw():
	redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')
