from mongoengine import *

class Room(Document):
	name = StringField(required=True)