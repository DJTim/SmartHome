from mongoengine import *

class Scenario(Document):
	name = StringField(required=True)
	room = ReferenceField('Room')
	deviceStates = ListField(EmbeddedDocumentField('ScenarioDeviceState'))

	meta = {'allow_inheritance': True}

class ScenarioDeviceState(EmbeddedDocument):
	device = ReferenceField('Device')
	state = IntField()