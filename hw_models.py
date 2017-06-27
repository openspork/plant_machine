from peewee import *
from app import hw_db
#from hardware import *


class HardwareBase(Model):
	class Meta:
		database = hw_db

class HardwareGroup(HardwareBase):
	name = CharField()

class SoilThermometer(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'soil_thermometers', null = True)
	pump_threshold = IntegerField(null = True)
	fan_threshold = IntegerField(null = True)
	name = CharField()
	address = CharField()
	curr_reading = FloatField(null = True)

class SoilHygrometer(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'soil_hygrometers', null = True)
	pump_threshold = IntegerField(null = True)
	fan_threshold = IntegerField(null = True)
	name = CharField()
	channel = IntegerField()
	curr_reading = FloatField(null = True)

class Pump(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'pumps', null = True)
	name = CharField()
	gpio_pin = IntegerField()
	curr_state = BooleanField(null = True)

class Fan(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'fans', null = True)
	name = CharField()
	gpio_pin = IntegerField()
	curr_state = BooleanField(null = True)

