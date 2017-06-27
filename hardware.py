import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

mcp1 = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(0, 0))
#below not implemented in hardware
#mcp2 = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(0, 1)) 

def gpio_set_mode():
	GPIO.setmode(GPIO.BCM)

def gpio_setup_out(pin):
	print 'setting gpio pin for output', pin
	GPIO.setup(pin, GPIO.OUT)

def gpio_out(pin, on):
	if on:
		GPIO.output(pin, GPIO.HIGH)
		print 'gpio pin high', pin
	else:
		GPIO.output(pin, GPIO.LOW)
		print 'gpio pin low', pin

def get_temp(address):
	file = open('/sys/bus/w1/devices/' + address + '/w1_slave', 'r')
	data = file.readlines()
	file.close()
	while data[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		data = read_temp_raw()
	equals_pos = data[1].find('t=')
	if equals_pos != -1:
		temp_string = data[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

#only supports dev1 currently
def get_moisture(channel):
	return mcp1.read_adc(channel)

def cleanup_hw():
	print 'cleaning up hw'
	GPIO.cleanup()

if __name__ == '__main__':
	print 'running as main, testing'
	print get_temp('28-0000071d1378')
	print get_moisture(0)

