import json
from gevent import monkey; monkey.patch_all()
from zmq import green as zmq
import bottle
import subprocess
from bottle import jinja2_template as template, static_file, request, app
from bottle import redirect
from bottle.ext import mongoengine

from models.room import *
from models.scenario import *
from models.device import *

#bottle and mongoengine init
app = bottle.Bottle()
plugin = mongoengine.Plugin(db='test',alias='test_db')
app.install(plugin)

#zmq and socket init. Pub Sub pattern
ctx = zmq.Context()
roomspubsocket = ctx.socket(zmq.PUB)
roomspubsocket.bind('inproc://roomspub')

def kaku(rc, id, type, state):
	if state == "on":
		state = "1"
	if state == "off":
		state = "0"
	subprocess.Popen(["sudo", "./kaku/kaku", rc, id, type[:1], state])

@app.route('/')
def index():
    return template('index.html')

@app.route('/<filename:re:.*\.html>')
def server_static(filename):
    return static_file(filename, root='static/')

@app.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='static/js')

@app.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/css')

@app.route('/<id>/on')
def kaku_on(id):
    kaku("8631674", id, "s", "on")

@app.route('/<id>/off')
def kaku_off(id):
    kaku("8631674", id, "s", "off")

@app.route('/<id>/<dim>')
def kaku_off(id, dim):
    kaku("8631674", id, "d", dim)

#Get all rooms
@app.route('/api/rooms', method='GET')
def getRooms(db):
    rooms = Room.objects
    if rooms:
        return rooms.to_json()
    return HTTPError(404, "No rooms found")

#Add or update a room
@app.route('/api/rooms', method='PUT')
def putRoom(db):
    data = request.body.readline()
    if not data:
        return HTTPError(400, 'No data received')
    try:
        room = Room.from_json(data)
        room.save()
        return {'status': 'ok'}
    except ValidationError as ve:
        return HTTPError(400, str(ve))

#Get room
@app.route('/api/rooms/<roomID>', method='GET')
def getRoomData(id, db):
    room = Room.objects.get(pk = id)
    if not room:
        return HTTPError(404, 'No room with id %s' % id)
    return room.to_json()

#Delere room
@app.route('/api/rooms/<roomID>', method='DELETE')
def deleteRoom(id, db):
    room = Room.objects.get(pk = id)
    if not room:
        return HTTPError(404, 'No room with id %s' % id)
    room.delete()
    return {'status': 'ok'}

#Get devices of room
@app.route('/api/rooms/<roomID>/devices', method='GET')
def getRoomDevices(id, db):
    devices = Device.objects.get(room = id)
    if not devices:
        return HTTPError(404, 'Room with id %s has no devices' % id)
    return devices.to_json()

#Get scenarios of room
@app.route('/api/rooms/<roomID>/scenarios', method='GET')
def getRoomScenarios(id, db):
    scenarios = Scenario.objects.get(room = id)
    if not scenarios:
        return HTTPError(404, 'Room with id %s has no scenarios' % id)
    return scenarios.to_json()


#Get all devices
@app.route('/api/devices', method='GET')
def getDevices(db):
    devices = Device.objects
    if devices:
        return devices.to_json()
    return HTTPError(404, "No devices found")

#Add or update device
@app.route('/api/devices', method='PUT')
def putDevice(db):
    data = request.body.readline()
    if not data:
        return HTTPError(400, 'No data received')
    try: #maybe has to change, not sure
        device = Device.from_json(data)
        device.save()
        return {'status': 'ok'}
    except ValidationError as ve:
        return HTTPError(400, str(ve))

#Get device
@app.route('/api/devices/<deviceID>', method='GET')
def getDeviceData(id, db):
    device = Device.objects.get(pk = id)
    if not device:
        return HTTPError(404, 'No device with id %s' % id)
    return device.to_json()

#Delete device
@app.route('/api/devices/<deviceID>', method='DELETE')
def deleteDevice(id, db):
    device = Device.objects.get(pk = id)
    if not device:
        return HTTPError(404, 'No device with id %s' % id)
    device.delete()
    return {'status': 'ok'}

#Change state of device, execute command, put data
@app.route('/api/devices/<deviceID>', method='PUT')
def putDeviceData(id, db):
    global roomspubsocket
  
    device = Device.objects.get(pk = id)
    if not device:
        return HTTPError(404, 'No device with id %s' % id)
    
    data = request.body.readline()
    if not data:
        return HTTPError(400, 'No data received')
    
    entity = json.loads(data)
    
    if entity.has_key('state'): #TODO Change to correct Model and communicate to different HW
        kaku(light["rc"], light["rcid"], light["type"], entity['state'])
        db['rooms'].update(
            { '_id': roomid, 'lights.name': lightid },
            { '$set': { 'lights.$.state' : entity['state'] } })
        
        roomspubsocket.send_json(device.to_json())
        return {'status': 'ok'}


#Get all scenario's
@app.route('/api/scenarios', method='GET')
def getScenarios(db):
    scenarios = Scenario.objects
    if scenarios:
        return scenarios.to_json()
    return HTTPError(404, "No scenarios found")

#Add or update scenario
@app.route('/api/scenarios', method='PUT')
def putScenario(db):
    data = request.body.readline()
    if not data:
        return HTTPError(400, 'No data received')
    try: #maybe has to change, not sure
        scenario = Scenario.from_json(data)
        scenario.save()
        return {'status': 'ok'}
    except ValidationError as ve:
        return HTTPError(400, str(ve))

#Get scenario
@app.route('/api/scenarios/<scenarioID>', method='GET')
def getScenarioData(id, db):
    scenario = Scenario.objects.get(pk = id)
    if not scenario:
        return HTTPError(404, 'No scenario with id %s' % id)
    return scenario.to_json()

#Delete scenario
@app.route('/api/scenarios/<scenarioID>', method='DELETE')
def deleteScenario(id, db):
    scenario = Scenario.objects.get(pk = id)
    if not scenario:
        return HTTPError(404, 'No scenario with id %s' % id)
    scenario.delete()
    return {'status': 'ok'}

#Execute scenario
@app.route('/api/scenarios/<scenarioID>', method='PUT')
def putDeviceData(id, db):
    scenario = Scenario.objects.get(pk = id)
    if not scenario:
        return HTTPError(404, 'No scenario with id %s' % id)
    
    data = request.body.readline()
    if not data:
        return HTTPError(400, 'No data received')
    
    entity = json.loads(data)
    
    if entity.has_key('state'):
        #TODO Add scenario logic
        return {'status': 'ok'}

#Listen to server (PUB - SUB)
@app.route('/api/listen', method='GET')
def listen():
    roomssubsocket = ctx.socket(zmq.SUB)
    roomssubsocket.setsockopt(zmq.SUBSCRIBE, '')
    roomssubsocket.connect('inproc://roomspub')
    
    #fix disconnecting clients
    rfile = app.request.environ['wsgi.input'].rfile

    poll = zmq.Poller()
    poll.register(roomssubsocket, zmq.POLLIN)
    poll.register(rfile, zmq.POLLIN)
    
    events = dict(poll.poll())
    
    if rfile.fileno() in events:
        return
    
    data = roomssubsocket.recv_json()
    return data

app.run(host='192.168.2.215', port=8080, debug=False, server="gevent")
