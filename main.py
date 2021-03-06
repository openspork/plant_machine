from app import app
from hw_models import hw_db
from views  import *
import atexit
from daemons import init_hw, start_sensor_poller
from hardware import cleanup_hw, get_therm_addresses
from scheduler.scheduler import spawn_schedule_daemon

#connects to DB and init tables if not present
def init_db():
	hw_db.connect() #connect to db
	print('opened hw db!')
	hw_db.create_tables([HardwareGroup, SoilHygrometer, SoilThermometer, Pump, Fan, Light], safe = True) #create tables if not present
	
def term():
	hw_db.close()
	print('closed db!')
	cleanup_hw()

def init():
	atexit.register(term) #register exit handler to close db on exit
	init_db() #open db
	init_hw()

	start_sensor_poller()
	spawn_schedule_daemon()


if __name__ == '__main__':
	init()

	app.run(
		host = "0.0.0.0",
		port = 8080,
		threaded = True,
		debug = True # MUST BE FALSE FOR DEPLOYMENT!!!
	)