from flask import Flask, abort, render_template, url_for, redirect, send_file, request
from app import app
from hw_models import *
import uuid

@app.route('/favicon.ico')
def favicon():
	abort(404)

@app.route('/<op>/<model>/<id>', methods=['POST'])
def update(op, model, id):
	print op, model, id
	#define model
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

	#define operation
	if op == "del":
		instance.delete_instance()
	if op == "rem":
		instance.group = None
		instance.save()
	#if op == "ass":
		#assign group

	return redirect(url_for('.index'))

@app.route('/add/<model>', methods=['POST'])
def add(model):
	print 'add', model
	if model == 'hwg':
		HardwareGroup.create(name = request.form['name'])
	elif model == 'sth':
		SoilThermometer.create(name = request.form['name'], address = request.form['addr'])
	elif model == 'shy':
		SoilHygrometer.create(name = request.form['name'], port = request.form['port'], device = request.form['dev'], channel = request.form['chan'])
	elif model == 'pmp':
		Pump.create(name = request.form['name'], gpio_pin = request.form['pin'])
	else:
		print 'done'

	return redirect(url_for('.index'))



	

@app.route('/')
def index():
	#group1 = HardwareGroup.create(name = 'test')
	#pump1 = Pump.create(group = group1, name = "pump1", gpio_pin = 0, curr_state = False)
	#pump2 = Pump.create(group = None, name = "pump2", gpio_pin = 0, curr_state = False)
	#shygr = SoilHygrometer.create(group = None, name = "tomato", port = 0, device = 0, channel = 0, curr_reading = 0)
	#stherm = SoilThermometer.create(group = None, name = "potato", address = 0x00001, curr_reading = 10)


	return render_template('index.html', HardwareGroup = HardwareGroup, SoilThermometer = SoilThermometer, SoilHygrometer = SoilHygrometer, Pump = Pump, Fan = Fan)