from app import app
from hw_models import hw_db
from views  import *
import atexit


def close_db():
	hw_db.close()
	print 'closed db!'

#connects to DB and init tables if not present
def initialize_db():
	hw_db.connect() #connect to db
	print 'opened hw db!'
	hw_db.create_tables([HardwareGroup, SoilHygrometer, SoilThermometer, Pump, Fan], safe = True) #create tables if not present
	atexit.register(close_db) #register exit handler to close db on exit
	
if __name__ == '__main__':

	initialize_db()
	app.run(
		host = "0.0.0.0",
		port = 8080,
		threaded = True,
		debug = True # MUST BE FALSE FOR DEPLOYMENT!!!
	)

