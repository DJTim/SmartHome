import json
from gevent import monkey; monkey.patch_all()
from zmq import green as zmq
import bottle
import subprocess
from bottle import jinja2_template as template, static_file, request, app
from bottle import redirect, HTTPError
from bottle.ext import mongoengine

from models.room import *
from models.scenario import *
from models.device import *

deviceClasses = {'KakuDevice' : KakuDevice, 'IRDevice' : IRDevice, 'HTTPDevice' : HTTPDevice, 'EnergyMonitor' : EnergyMonitor}

#bottle and mongoengine init
app = bottle.Bottle()
plugin = mongoengine.Plugin(db='test_db')
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
def getRoomData(roomID, db):
    room = Room.objects.get(pk = roomID)
    if not room:
        return HTTPError(404, 'No room with id %s' % roomID)
    return room.to_json()

#Delere room
@app.route('/api/rooms/<roomID>', method='DELETE')
def deleteRoom(roomID, db):
    room = Room.objects.get(pk = roomID)
    if not room:
        return HTTPError(404, 'No room with id %s' % roomID)
    room.delete()
    return {'status': 'ok'}

#Get devices of room
@app.route('/api/rooms/<roomID>/devices', method='GET')
def getRoomDevices(roomID, db):
    devices = Device.objects.get(room = roomID)
    if not devices:
        return HTTPError(404, 'Room with id %s has no devices' % roomID)
    return devices.to_json()

#Get scenarios of room
@app.route('/api/rooms/<roomID>/scenarios', method='GET')
def getRoomScenarios(roomID, db):
    scenarios = Scenario.objects.get(room = roomID)
    if not scenarios:
        return HTTPError(404, 'Room with id %s has no scenarios' % roomID)
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
    global deviceClasses
    data = request.body.readline()
    if not data:
        return HTTPError(400, 'No data received')
    try:
        entity = json.loads(data)
        device = deviceClasses[entity['cls']].from_json(json.dumps(entity['device']))
        device.save()
        return {'status': 'ok'}
    except ValidationError as ve:
        return HTTPError(400, str(ve))

#Get device
@app.route('/api/devices/<deviceID>', method='GET')
def getDeviceData(deviceID, db):
    device = Device.objects.get(pk = deviceID)
    if not device:
        return HTTPError(404, 'No device with id %s' % deviceID)
    return device.to_json()

#Delete device
@app.route('/api/devices/<deviceID>', method='DELETE')
def deleteDevice(deviceID, db):
    device = Device.objects.get(pk = deviceID)
    if not device:
        return HTTPError(404, 'No device with id %s' % deviceID)
    device.delete()
    return {'status': 'ok'}

#Change state of device, execute command, put data
@app.route('/api/devices/<deviceID>', method='PUT')
def putDeviceData(deviceID, db):
    global roomspubsocket
  
    device = Device.objects.get(pk = deviceID)
    if not device:
        return HTTPError(404, 'No device with id %s' % deviceID)
    
    data = request.body.readline()
    if not data:
        return HTTPError(400, 'No data received')
    
    entity = json.loads(data)

    #TODO Move to Model class or separate py to communicate with hardware
    def updateKaku():
        device.state = entity['state']
        device.save()
        kaku(device.rc, device.rcid, device.type, device.state)

    def updateIRDevice():
        #TODO
        print "IRDevice"

    def updateHTTPDevice():
        #TODO
        print "HTTPDevice"

    def updateEnergyMonitor():
        measurement = Mesurement(dateTime = datetime.datetime.now, power = entity['power'])
        #TODO Update average
        device.measurements.append(measurement)
        device.save()
        device.reload()

    deviceComm = {"KakuDevice": updateKaku, "IRDevice": updateIRDevice, "HTTPDevice": updateHTTPDevice, "EnergyMonitor": updateEnergyMonitor}
    #END Block

    try:
        deviceComm[device.__class__.__name__]()
        roomspubsocket.send_json(device.to_json())
        return {'status': 'ok'}
    except ValidationError as ve:
        return HTTPError(400, str(ve))

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
def getScenarioData(scenarioID, db):
    scenario = Scenario.objects.get(pk = scenarioID)
    if not scenario:
        return HTTPError(404, 'No scenario with id %s' % scenarioID)
    return scenario.to_json()

#Delete scenario
@app.route('/api/scenarios/<scenarioID>', method='DELETE')
def deleteScenario(scenarioID, db):
    scenario = Scenario.objects.get(pk = scenarioID)
    if not scenario:
        return HTTPError(404, 'No scenario with id %s' % scenarioID)
    scenario.delete()
    return {'status': 'ok'}

#Execute scenario
@app.route('/api/scenarios/<scenarioID>', method='PUT')
def putDeviceData(scenarioID, db):
    scenario = Scenario.objects.get(pk = scenarioID)
    if not scenario:
        return HTTPError(404, 'No scenario with id %s' % scenarioID)
    
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

app.run(host='0.0.0.0', port=8080, debug=False, server="gevent")
