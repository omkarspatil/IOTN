import web


urls = (
    '/', 'Index',
    '/login', 'Login',
    '/logout', 'Logout',
)

web.config.debug = False
app = web.application(urls, locals())
session = web.session.Session(app, web.session.DiskStore('sessions'))      

class Index:
    def GET(self):
        print 'session',session
        if session.get('logged_in', False):
            return '<h1>You are logged in</h1><a href="/logout">Logout</a>'
        return '<h1>You are not logged in.</h1><a href="/login">Login now</a>'

class Login:
    def GET(self):
        print 'session',session
        session.logged_in = True
        raise web.seeother('/')

class Logout:
    def GET(self):
        print 'session',session
        session.logged_in = False
        raise web.seeother('/')


if __name__ == '__main__':
    app.run()