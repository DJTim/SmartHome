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

class OldKakuDevice(Device):
    state = IntField()
    rcid = IntField()
    rc = StringField()

class IRCommand(EmbeddedDocument):
    command = StringField()

class HTTPCommand(EmbeddedDocument):
    command = StringField()
    type = StringField()

class Measurement(EmbeddedDocument):
    dateTime = DateTimeField()
    power = IntField()

class IRDevice(Device):
	commands = ListField(EmbeddedDocumentField('IRCommand'))

class HTTPDevice(Device):
	commands = ListField(EmbeddedDocumentField('HTTPCommand'))

class EnergyMonitor(Device):
	measurements = ListField(EmbeddedDocumentField('Measurement'))
	currentUseDay = IntField()
	currentUseWeek = IntField()
	currentUseMonth = IntField()
	currentUseYear = IntField()
