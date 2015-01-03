import bottle
import subprocess
from bottle import jinja2_template as template, static_file, request, app
from bottle import redirect

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
    subprocess.call(["sudo", "./kaku/kaku", "8631674", id, "15"])

@bottle.route('/<id>/off')
def kaku_off(id):
    subprocess.call(["sudo", "./kaku/kaku", "8631674", id, "0"])

@bottle.route('/<id>/<dim>')
def kaku_off(id, dim):
    subprocess.Popen(["sudo", "./kaku/kaku", "8631674", id, dim])

bottle.run(host='192.168.2.215', port=8080, debug=False)
