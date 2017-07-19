from flask import Flask, abort, render_template, url_for, redirect, send_file, request
from app import app
from hw_models import *
from hardware import gpio_setup_out, gpio_out, get_temp
from glob import glob
from os.path import basename

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
			gpio_pin = int(request.form['pin'])
			gpio_setup_out(gpio_pin)
			instance = Pump.create(name = request.form['name'], gpio_pin = gpio_pin)
			
		elif model == 'fan':
			gpio_pin = int(request.form['pin'])
			gpio_setup_out(gpio_pin)
			instance = Fan.create(name = request.form['name'], gpio_pin = gpio_pin)

	elif op == "ass":
		instance.group = HardwareGroup.get(HardwareGroup.id == request.form['group'])

	elif op == "del":
		if model == 'hwg':
			#TODO!
			for soil_therm in SoilThermometer.select().where(SoilThermometer.group == instance.id):
				soil_therm.group = None
				soil_therm.save()
			for soil_hygro in SoilHygrometer.select().where(SoilHygrometer.group == instance.id):
				soil_hygro.group = None
				soil_hygro.save()						
			for pump in Pump.select().where(Pump.group == instance.id):
				pump.group = None
				pump.save()
			for fan in Fan.select().where(Fan.group == instance.id):
				fan.group = None
				fan.save()
		if model == 'pmp' or model == 'fan':
			gpio_out(instance.gpio_pin, False)
		instance.delete_instance()
	elif op == "rem":
		if model == 'pmp' or model == 'fan':
			gpio_out(instance.gpio_pin, False)
		instance.group = None
	else:
		print "nothing"
		
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
