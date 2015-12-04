from mongoengine import *

class ScenarioDeviceState(EmbeddedDocument):
        device = ReferenceField('Device')
        state = IntField()

class Scenario(Document):
	name = StringField(required=True)
	room = ReferenceField('Room')
	deviceStates = ListField(EmbeddedDocumentField('ScenarioDeviceState'))

	meta = {'allow_inheritance': True}

