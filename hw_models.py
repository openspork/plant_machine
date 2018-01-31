from peewee import *
from app import hw_db
#from hardware import *

class HardwareBase(Model):
	class Meta:
		database = hw_db

class HardwareGroup(HardwareBase):
	name = CharField()

	pump_temp_threshold = IntegerField()
	pump_moist_threshold = IntegerField()
	pump_status = BooleanField(null = True)

	fan_temp_threshold = IntegerField()
	fan_moist_threshold = IntegerField()
	fan_status = BooleanField(null = True)

	light_start_time = TimeField()
	light_stop_time = TimeField()
	light_status = BooleanField(null = True)

class SoilThermometer(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'soil_thermometers', null = True)
	name = CharField()
	address = CharField()
	curr_reading = FloatField(null = True)

class SoilHygrometer(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'soil_hygrometers', null = True)
	name = CharField()
	channel = IntegerField()
	curr_reading = FloatField(null = True)

class Pump(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'pumps', null = True)
	name = CharField()
	gpio_pin = IntegerField()
	run_time = IntegerField()

class Fan(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'fans', null = True)
	name = CharField()
	gpio_pin = IntegerField()
	run_time = IntegerField()

class Light(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'lights', null = True)
	name = CharField()
	gpio_pin = IntegerField()

