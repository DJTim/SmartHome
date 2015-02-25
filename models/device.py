from mongoengine import *

class Device(Document):
	name = StringField(required=True)
	room = ReferenceField('Room')
	meta = {'allow_inheritance': True}

class KakuDevice(Device):
	type = StringField()
	state = IntField()
	rcid = IntField()
	rc = IntField()

class IRDevice(Device):
	commands = ListField(EmbeddedDocumentField('IRCommand'))

class IRCommand(EmbeddedDocument):
	command = StringField()

class HTTPDevice(Device):
	commands = ListField(EmbeddedDocumentField('HTTPCommand'))

class HTTPCommand(EmbeddedDocument):
	command = StringField()
	type = StringField()

class EnergyMonitor(Device):
	mesurements = ListField(EmbeddedDocumentField('Mesurement'))
	currentUseDay = IntField()
	currentUseWeek = IntField()
	currentUseMonth = IntField()
	currentUseYear = IntField()

class Mesurement(EmbeddedDocument):
	dateTime = DateTimeField()
	power = IntField()