import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

gpio_num_scheme = GPIO.BCM

SPI_PORT = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

w1_base_dir = '/sys/bus/w1/devices/'


def gpio_setup_out(pin):
	GPIO.setMode(gpio_num_scheme)
	GPIO.setup(pin, GPIO.OUT)


def gpio_out(pin, on):
	if on:
		GPIO.output(pin, GPIO.HIGH)
	else:
		GPIO.output(pin, GPIO.LOW)


def get_temp(address):
	file = open(w1_base_dir + address + '/w1_slave', 'r')
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

def cleanup():
	# cleanup GPIO
	GPIO.cleanup()

if __name__ == '__main__':
	print 'running as main'
	print get_temp('28-0000071d1378')

