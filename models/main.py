from mongoengine import *
from room import *
from scenario import *
from device import *

import datetime

connect('testMongoEngine')


tim = Room(name = 'Tim').save()

leftLight = KakuDevice(name = 'LeftLight', room = tim, type = 'dim', state = 0, rc = 888888, rcid = 0).save()

energyMeasurement = Mesurement(dateTime = datetime.datetime.now, power = 100)
energy = EnergyMonitor(name = 'energy', room = tim, mesurements = [energyMeasurement]).save()

sLeftLightState = ScenarioDeviceState(device = leftLight, state = 1)
sLeftLightOn = Scenario(name = 'LeftLightOn', room = tim, deviceStates = [sLeftLightState]).save()


for room in Room.objects:
	print room.name
	print 'Devices:'
	for device in room.devices:
		print device.name
		print device._cls
	print 'Scenarios:'
	for scenario in room.scenarios:
		print scenario.name



#ROOM name
#DEVICE name, room, (device specific options)
#SCENARIO name, room, deviceState[]
	#DEVICESTATE device, state