import json
import bottle
import subprocess
from bottle import jinja2_template as template, static_file, request, app
from bottle import redirect
from pymongo import Connection

connection = Connection('localhost', 27017)
db = connection.domotica

def kaku(rc, id, state):
	if state == "on":
		state = "15"
	if state == "off":
		state = "0"
	subprocess.Popen(["sudo", "./kaku/kaku", rc, id, state])

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
    kaku("8631674", id, "15")

@bottle.route('/<id>/off')
def kaku_off(id):
    kaku("8631674", id, "0")

@bottle.route('/<id>/<dim>')
def kaku_off(id, dim):
    kaku("8631674", id, dim)
    
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
     
@bottle.route('/api/rooms/<id>', method='GET')
def get_document(id):
    entity = db['rooms'].find_one({'_id':id})
    if not entity:
        abort(404, 'No document with id %s' % id)
    return entity
    
@bottle.route('/api/<roomid>/<lightid>', method='PUT')
def update_document(roomid, lightid):
    room = db['rooms'].find_one({'_id':roomid})
    if not room:
        abort(404, 'No document with id %s' % id)
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    entity = json.loads(data)
    light = next((item for item in room["lights"] if item["name"] == lightid), None)
    if entity.has_key('state'):
    	kaku(light["rc"], light["rcid"], entity['state'])
    	db['rooms'].update(
   			{ '_id': roomid, 'lights.name': lightid },
   			{ '$set': { 'lights.$.state' : entity['state'] } }
		)
    return entity

bottle.run(host='192.168.2.215', port=8080, debug=False)
