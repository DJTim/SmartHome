import json
from gevent import monkey; monkey.patch_all()
from zmq import green as zmq
import bottle
import subprocess
from bottle import jinja2_template as template, static_file, request, app
from bottle import redirect
from pymongo import Connection

#mongoDB init
connection = Connection('localhost', 27017)
db = connection.domotica

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

@bottle.route('/')
def index():
    return template('index.html')

@bottle.route('/<filename:re:.*\.html>')
def server_static(filename):
    return static_file(filename, root='static/')

@bottle.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='static/js')

@bottle.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/css')

@bottle.route('/<id>/on')
def kaku_on(id):
    kaku("8631674", id, "s", "on")

@bottle.route('/<id>/off')
def kaku_off(id):
    kaku("8631674", id, "s", "off")

@bottle.route('/<id>/<dim>')
def kaku_off(id, dim):
    kaku("8631674", id, "d", dim)
    
#Save new and updated room
@bottle.route('/api/rooms/', method='PUT')
def put_document():
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    entity = json.loads(data)
    if not entity.has_key('_id'):
        abort(400, 'No _id specified')
    try:
        db['rooms'].save(entity)
    except ValidationError as ve:
        abort(400, str(ve))
     
#Get room based on name
@bottle.route('/api/rooms/<id>', method='GET')
def get_document(id):
    entity = db['rooms'].find_one({'_id':id})
    if not entity:
        abort(404, 'No document with id %s' % id)
    return entity

#Change the state of a light inside a room
@bottle.route('/api/<roomid>/<lightid>', method='PUT')
def update_document(roomid, lightid):
    global roomspubsocket
	
    room = db['rooms'].find_one({'_id':roomid})
    if not room:
        abort(404, 'No document with id %s' % id)
    
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    
    entity = json.loads(data)
    
    light = next((item for item in room["lights"] if item["name"] == lightid), None)
    
    if entity.has_key('state'):
    	kaku(light["rc"], light["rcid"], light["type"], entity['state'])
    	db['rooms'].update(
   			{ '_id': roomid, 'lights.name': lightid },
   			{ '$set': { 'lights.$.state' : entity['state'] } }
		)
    
    roomspubsocket.send_json(db['rooms'].find_one({'_id':roomid}))
    return {'status': 'ok'}

#Listen for room updates
@bottle.route('/api/rooms/listen')
def listen():
    roomssubsocket = ctx.socket(zmq.SUB)
    roomssubsocket.setsockopt(zmq.SUBSCRIBE, '')
    roomssubsocket.connect('inproc://roomspub')
    
    #fix disconnecting clients
    rfile = bottle.request.environ['wsgi.input'].rfile

    poll = zmq.Poller()
    poll.register(roomssubsocket, zmq.POLLIN)
    poll.register(rfile, zmq.POLLIN)
    
    events = dict(poll.poll())
    
    if rfile.fileno() in events:
        return
    
    room = roomssubsocket.recv_json()
    return room

bottle.run(host='192.168.2.215', port=8080, debug=False, server="gevent")
