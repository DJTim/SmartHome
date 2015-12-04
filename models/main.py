from mongoengine import *
from room import *
from scenario import *
from device import *

import datetime

connect('domotica')


#tim = Room(name = 'Tim').save()
#living = Room(name = 'Living').save()
arne = Room(name = 'Arne').save()

bedLight = OldKakuDevice(name = 'BedLight', room = arne, state = 0, rc = 'C', rcid = 1).save()
tvLight = OldKakuDevice(name = 'TVLight', room = arne, state = 0, rc = 'C', rcid = 3).save()

#diningLight = KakuDevice(name = 'DiningLight', room = living, type = 'switch', state = 0, rc = 888888, rcid = 0).save()

#leftLight = KakuDevice(name = 'LeftLight', room = tim, type = 'dim', state = 0, rc = 888888, rcid = 0).save()

#energyMeasurement = Mesurement(dateTime = datetime.datetime.now, power = 100)
#energy = EnergyMonitor(name = 'energy', room = tim, mesurements = [energyMeasurement]).save()

#sLeftLightState = ScenarioDeviceState(device = leftLight, state = 1)
#sLeftLightOn = Scenario(name = 'LeftLightOn', room = tim, deviceStates = [sLeftLightState]).save()


#for room in Room.objects:
#	print room.name
#	print 'Devices:'
#	for device in Device.objects(room = room.id):
#		print device.name
#		print device._cls
#		print device.to_json()
#print 'Scenarios:'
#for scenario in Scenario.objects:
#	print scenario.name
#
#test = Room.objects.get(pk = tim.pk)
#print test.name
#print test.to_json()


#ROOM name
#DEVICE name, room, (device specific options)
#SCENARIO name, room, deviceState[]
	#DEVICESTATE device, state
