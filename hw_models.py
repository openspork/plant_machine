from peewee import *
from app import hw_db
#from hardware import *


class HardwareBase(Model):
	class Meta:
		database = hw_db

class HardwareGroup(HardwareBase):
	name = CharField()

class SoilHygrometer(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'soil_hygrometers', null = True)
	name = CharField()
	port = IntegerField()
	device = IntegerField()
	channel = IntegerField()
	curr_reading = FloatField(null = True)

	def init_hw(self):
		print ('initializing soil hygrometer at port: ' + str(self.port) + " device: " + str(self.device) + " channel: " + str(self.channel))

class SoilThermometer(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'soil_thermometers', null = True)
	name = CharField()
	address = CharField()
	curr_reading = FloatField(null = True)

	def init_hw(self):
		print ('initializing soil thermometer at address : ' + str(self.address))

class Pump(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'pumps', null = True)
	name = CharField()
	gpio_pin = IntegerField()
	curr_state = BooleanField(null = True)

	def init_hw(self):
		print ('initializing pump at GPIO : ' + str(self.gpio_pin))

class Fan(HardwareBase):
	group = ForeignKeyField(HardwareGroup, related_name = 'fans', null = True)
	name = CharField()
	gpio_pin = IntegerField()
	curr_state = BooleanField(null = True)

	def init_hw(self):
		print ('initializing fan at GPIO : ' + str(self.gpio_pin))