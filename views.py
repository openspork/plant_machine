from flask import Flask, abort, render_template, url_for, redirect, send_file, request
from app import app
from hw_models import *
import uuid

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
			instance = SoilThermometer.create(name = request.form['name'], address = request.form['addr'])
		elif model == 'shy':
			Sinstance = SoilHygrometer.create(name = request.form['name'], port = request.form['port'], device = request.form['dev'], channel = request.form['chan'])
		elif model == 'pmp':
			instance = Pump.create(name = request.form['name'], gpio_pin = request.form['pin'])
		elif model == 'fan':
			instance = Fan.create(name = request.form['name'], gpio_pin = request.form['pin'])

	elif op == "del":
		instance.delete_instance()
	elif op == "rem":
		instance.group = None
	else:
		print "nothing"
		instance.save()
	#if op == "ass":
		#assign group

	return redirect(url_for('.index'))


@app.route('/')
def index():

	return render_template('index.html', HardwareGroup = HardwareGroup, SoilThermometer = SoilThermometer, SoilHygrometer = SoilHygrometer, Pump = Pump, Fan = Fan)


