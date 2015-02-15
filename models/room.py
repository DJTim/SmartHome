from mongoengine import *

class Room(Document):
	name = StringField(required=True)
	devices = ListField(ReferenceField('Device'))
	scenarios = ListField(ReferenceField('Scenario'))