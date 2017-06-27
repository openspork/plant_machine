from flask import Flask, abort, render_template, url_for, redirect, send_file, request
from app import app
from hw_models import *
import uuid
from hardware import gpio_setup_out

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
			instance = HardwareGroup.create(name = request.form['name'])
		elif model == 'sth':
			instance = SoilThermometer.create(name = request.form['name'], address = request.form['addr'], pump_threshold = request.form['pmp_thresh'], fan_threshold = request.form['fan_thresh'])
		elif model == 'shy':
			Sinstance = SoilHygrometer.create(name = request.form['name'], channel = request.form['chan'], pump_threshold = request.form['pmp_thresh'], fan_threshold = request.form['fan_thresh'])
		elif model == 'pmp':
			gpio_pin = request.form['pin']
			instance = Pump.create(name = request.form['name'], gpio_pin = gpio_pin)
			gpio_setup_out(gpio_pin)
		elif model == 'fan':
			gpio_pin = request.form['pin']
			instance = Fan.create(name = request.form['name'], gpio_pin = gpio_pin)
			gpio_setup_out(gpio_pin)

	elif op == "ass":
		instance.group = HardwareGroup.get(HardwareGroup.id == request.form['group'])

	elif op == "del":
		instance.delete_instance()
	elif op == "rem":
		instance.group = None
	else:
		print "nothing"
		
	instance.save()

	return redirect(url_for('index'))


@app.route('/')
def index():

	return render_template('index.html', HardwareGroup = HardwareGroup, SoilThermometer = SoilThermometer, SoilHygrometer = SoilHygrometer, Pump = Pump, Fan = Fan)


