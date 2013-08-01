from bottle import route, template, static_file, view
from bottle import get, post, request, run
#from bottlehaml import haml_template
from subprocess import call
#from os import sys
#import subprocess
#run(reloader=True)
import config
import sys

@post('/confirm')
def confirm_form():
   if(config.write_params(request.forms)):
      return template('confirm', config.exe)
   else:
      return template('failed to write parameters to file: {{fn}}',fn=config.sim_input_file)

@post('/execute')
def execute():
    # student - need to use popen here and repeatedly read from the pipe and display
    try:
        retcode = call(config.sim_exe)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal", -retcode
            return template('job terminated by signal: {{x}}', x=-retcode)
        else:
            print >>sys.stderr, "Child returned", retcode
            return "completed successfully"

    except OSError, e:
        print >>sys.stderr, "Execution failed:", e
        return "failed to start job"
   
@route('/')
@get('/login')
def login_form():
    return '''<form method="POST" action="/login">
                <input name="user"     type="text" />
                <input name="password" type="password" />
                <input type="submit" />
              </form>'''

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')

@post('/login')
def login_submit():
    user     = request.forms.get('user')
    password = request.forms.get('password')
    if check_login(user, password):
        #config.params['user'] = user
        # ignore blockmap and blockorder from read_namelist()
        params,_,_ = config.read_namelist()
        return template('start', params)
        #return haml_template('start', config.read_namelist())
    else:
        return "<p>Login failed</p>"

def check_login(user, password):
	if user == config.user and password == config.password:
		return 1
	else:
		return 0

run(host='localhost', port=8080)
