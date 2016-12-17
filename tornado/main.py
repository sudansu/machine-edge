import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import os.path
import sys

def get_bokeh_link(path):
    link = "http://"
    link += bokeh_host + "/"
    link += path
    return link

class WelcomeHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html')
		
class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user =  self.get_secure_cookie("username")
        return user

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('main.html',page=None, user=self.current_user)

class DimRedHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        link = get_bokeh_link("app_deputy") 
        self.render('page.html',page="dimension", user=self.current_user,page_link=link)

class QueryHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        link = get_bokeh_link("app_query") 
        self.render('page.html',page="query", user=self.current_user,page_link=link)

class VisualHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        link = get_bokeh_link("app_explore") 
        self.render('page.html',page="visualization", user=self.current_user,page_link=link)

class PredictionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        link = get_bokeh_link("app_knn") 
        self.render('page.html',page="prediction", user=self.current_user,page_link=link)

class RegimeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        link = get_bokeh_link("app_regime") 
        self.render('page.html',page="regime", user=self.current_user,page_link=link)


class LogoutHandler(BaseHandler):
    # @tornado.web.authenticated
    def get(self):
        self.clear_cookie("username")
        self.redirect("/login")

class LoginHandler(BaseHandler):
    def get(self):
        user =  self.get_secure_cookie("username")
        if user != None:
        	print (user)
        	self.redirect("/main")
        else:
	        message = self.get_secure_cookie("message")
	        if message == None:
	            message = "Welcome to Machine Edge"
	        self.clear_cookie("message")
	        self.render('login.html',message=message)

    def post(self):
        username = self.get_argument("username")
        pwd = self.get_argument("password")
        if username == "jarvis" and  pwd == "ironman":
            self.set_secure_cookie("username", username)
            self.redirect("/main")
        else:#Login Failed
            message = self.set_secure_cookie("message","Login Failed...")
            self.redirect("/login")

def makeApp():
	return tornado.web.Application(
		handlers = [(r'/', _index),(r'/login', _login)],
		template_path = os.path.join(os.path.dirname(__file__),'template'),
		static_path = os.path.join(os.path.dirname(__file__),'static'),
		debug = True)

if __name__ == '__main__':
    # tornado.options.parse_command_line()
    global bokeh_host
    bokeh_host = "localhost:5006"
    if len(sys.argv) == 2:
       bokeh_host = sys.argv[1]
    print ("bokeh_host: ", bokeh_host) 
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "template"),
        "static_path":os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "xsrf_cookies": True,
        "login_url": "/login",
    }

    application = tornado.web.Application([
        (r'/', WelcomeHandler),
        (r'/login', LoginHandler),
        (r'/main', MainHandler),
        (r'/visual',VisualHandler),
        (r'/predict',PredictionHandler),
        (r'/regime',RegimeHandler),
        (r'/query',QueryHandler),
        (r'/dimension',DimRedHandler),
        (r'/logout', LogoutHandler)
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000 )
    tornado.ioloop.IOLoop.instance().start()
