import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import os.path
from tornado.options import define, options

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

class VisualHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('page.html',page="visualization", user=self.current_user,page_link="http://localhost:5006/daily_what_happened_since")

class PredictionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('page.html',page="prediction", user=self.current_user,page_link="http://localhost:5006/knn-prediction")

class RegimeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('page.html',page="regime", user=self.current_user,page_link="http://localhost:5006/regime_shift")


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

        (r'/logout', LogoutHandler)
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000 )
    tornado.ioloop.IOLoop.instance().start()
