from hw_models import *

def check_soil_thermometers(group_id):
	group = HardwareGroup.get(HardwareGroup.id == group_id)
	pump_triggered = False
	fan_triggered = False
	#handle therm sensors
	for soil_therm in group.soil_thermometers.select():
		#handle pumps
		print '        PUMP MONITOR: processing THERM:"', soil_therm.name, '" curr reading:', soil_therm.curr_reading, 'pump thresh:', group.pump_temp_threshold
		if (soil_therm.curr_reading > group.pump_temp_threshold):
			#print '        therm past pump threshold'
			pump_triggered = True
		#handle fans
		print '        FAN MONITOR: processing THERM:"', soil_therm.name, '" curr reading:', soil_therm.curr_reading, 'fan thresh:', group.fan_temp_threshold
		if (soil_therm.curr_reading > group.fan_temp_threshold):
			#print '        therm past fan threshold'
			fan_triggered = True
	return pump_triggered, fan_triggered


def check_soil_hygrometers(group_id):
	group = HardwareGroup.get(HardwareGroup.id == group_id)

	pump_triggered = False
	fan_triggered = False
	#handle moisture sensors
	for soil_hygro in group.soil_hygrometers.select():
		#handle pumps
		print '        PUMP MONITOR: processing HYGRO:"', soil_hygro.name, '" curr reading:', soil_hygro.curr_reading, 'pump thresh:', group.pump_temp_threshold
		if (soil_hygro.curr_reading > group.pump_temp_threshold):
			#print '        hygro past pump threshold'
			pump_triggered = True
		#handle fans
		print '        FAN MONITOR processing HYGRO:"', soil_hygro.name, '" curr reading:', soil_hygro.curr_reading, 'fan thresh:', group.fan_temp_threshold
		if (soil_hygro.curr_reading > group.fan_temp_threshold):
			#print '        hygro past fan threshold'
			fan_triggered = True
	return pump_triggered, fan_triggered

def check_triggers(group_id):
	group = HardwareGroup.get(HardwareGroup.id == group_id)
	print '\n\n        checking triggers for:', group.name, '\n'
	
	therm_trigger_results = check_soil_thermometers(group)
	hygro_trigger_results = check_soil_hygrometers(group)

	if therm_trigger_results[0] or hygro_trigger_results[0]: #we need to pump
		print '        pump needs to be on'
		if not group.pump_status: #if not already pumping, start
			print '            pump off, starting'
			group.pump_status = True
			group.save()
	else: #we do not need to pump
		print '        pump needs to be off'
		if group.pump_status: #if already pumping, stop
			print '            pump on, stopping'
			group.pump_status = False
			group.save()
	
	if therm_trigger_results[1] or hygro_trigger_results[1]: #we need to fan
		print '        fan needs to be on'
		if not group.fan_status: #if not already fanning, start
			print '            fan off, starting'
			group.fan_status = True
			group.save()
	else: #we do not need to fan
		print '        fan needs to be off'
		if group.fan_status: #if already fanning, stop
			print '            pump on, stopping'
			group.fan_status = False
			group.save()

	



