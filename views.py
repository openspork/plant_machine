from flask import Flask, abort, render_template, url_for, redirect, send_file, request
from app import app
from hw_models import *
from hardware import get_temp
from daemons import spawn_pump_daemon, kill_pump_daemon, spawn_fan_daemon, kill_fan_daemon
from glob import glob
from os.path import basename
from datetime import timedelta

@app.route('/favicon.ico')
def favicon():
	abort(404)

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

	#handle operation:
	if op == "add":
		if model == 'hwg':
			instance = HardwareGroup.create(
				name = request.form['name'],
				pump_temp_threshold = request.form['pmp_temp_thresh'],
				pump_moist_threshold = request.form['pmp_moist_thresh'],
				fan_temp_threshold = request.form['fan_temp_thresh'],
				fan_moist_threshold = request.form['fan_moist_thresh'])
		elif model == 'sth':
			instance = SoilThermometer.create(name = request.form['name'], address = request.form['addr'])
		elif model == 'shy':
			instance = SoilHygrometer.create(name = request.form['name'], channel = request.form['chan'])
		elif model == 'pmp':
			instance = Pump.create(name = request.form['name'], gpio_pin = int(request.form['pin']), run_time = 1, sleep_time = 1)
		elif model == 'fan':
			instance = Fan.create(name = request.form['name'], gpio_pin = int(request.form['pin']), run_time = 1, sleep_time = 1)

	elif op == "ass":
		instance.group = HardwareGroup.get(HardwareGroup.id == request.form['group'])
		if model == 'pmp':
			spawn_pump_daemon(instance.id)
		elif model == 'fan':
			print 'spawn fan daemon placeholder'
			spawn_fan_daemon(instance.id)

	elif op == "del":
		if model == 'hwg':
			for soil_therm in SoilThermometer.select().where(SoilThermometer.group == instance.id):
				soil_therm.group = None
				soil_therm.save()
			for soil_hygro in SoilHygrometer.select().where(SoilHygrometer.group == instance.id):
				soil_hygro.group = None
				soil_hygro.save()						
			for pump in Pump.select().where(Pump.group == instance.id):
				kill_pump_daemon(pump.id)
				pump.group = None
				pump.save()
			for fan in Fan.select().where(Fan.group == instance.id):
				kill_fan_daemon(fan.id)
				fan.group = None
				fan.save()
		elif model == 'pmp':
			#if pump is active, kill daemon
			if instance.group:
				kill_pump_daemon(instance.id)
		elif model == 'fan':
			#if fan is active, kill daemon
			if instance.group:
				kill_fan_daemon(instance.id)
		instance.delete_instance()
	elif op == "rem":
		if model == 'pmp':
			kill_pump_daemon(instance.id)
			instance.group.pump_status = False
		elif model == 'fan':
			kill_fan_daemon(instance.id)
			instance.group.fan_status = False
		instance.group = None
		
	instance.save()

	return redirect(url_for('index'))

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/hw_groups')
def hw_groups():
	return render_template('hw_groups.html', HardwareGroup = HardwareGroup, SoilThermometer = SoilThermometer, SoilHygrometer = SoilHygrometer, Pump = Pump, Fan = Fan)

@app.route('/unass_resources')
def unass_resources():
	return render_template('unass_resources.html', HardwareGroup = HardwareGroup, SoilThermometer = SoilThermometer, SoilHygrometer = SoilHygrometer, Pump = Pump, Fan = Fan)

@app.route('/add_resources')
def add_resources():
	addresses = []
	raw_addresses = glob('/sys/bus/w1/devices/28*')
	for raw_address in raw_addresses:
		address = basename(raw_address)
		address_and_temp = (address, get_temp(address))
		addresses.append(address_and_temp)

	return render_template('add_resources.html', addresses = addresses)
