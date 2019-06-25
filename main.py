from Cocoa import Cocoa, request
import json

app = Cocoa()


@app.route('/welcome/<username>')
def welcome(username):
    """ just welcome """
    print 'welcome: ', type(request.headers)
    print request.headers
    print request.headers.get('Content-Type')
    return '<h1>Hello {}, this is Cocoa web framework</h1>'.format(username)

@app.route('/json')
def json_ret():
    return {
        'name': 'Cocoa'
    }

@app.route('/static/<file_name>')
def static_file(file_name):
    with open('/tmp/{}'.format(file_name), 'r') as file_handler:
        return file_handler.read()


app.run(host='0.0.0.0', port=8000)
