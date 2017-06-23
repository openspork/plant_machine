import RPi.GPIO as GPIO

gpio_num_scheme = GPIO.BCM

def gpio_setup_out(pin):
	GPIO.setMode(gpio_num_scheme)
	GPIO.setup(pin, GPIO.OUT)

def gpio_out(pin, on)
	if on:
		GPIO.output(pin,GPIO.HIGH)
	else:
		GPIO.output(pin,GPIO.LOW)

def cleanup():
	#cleanup GPIO
	GPIO.cleanup()

