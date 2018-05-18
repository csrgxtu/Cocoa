from Cocoa import Cocoa, request


app = Cocoa()


@app.route('/welcome/<username>')
def welcome(username):
    """ just welcome """
    print request.headers
    return '<h1>Hello {}, this is Cocoa web framework</h1>'.format(username)


app.run(host='0.0.0.0', port=8000)
