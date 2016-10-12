import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import os.path

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)
class ChartModule(tornado.web.UIModule):
    def render(self):
        divChart = '<div class="bk-root"><div class="plotdiv" id="bdb58f8c-be29-46ac-a764-d3dd720e8f7e"></div></div>'
        with open('bk.js', 'r') as content_file:
            script = content_file.read()
        return self.render_string('modules/chart.html',script=script, div=divChart) 

    # def embedded_javascript(self):
    #     with open('bk.js', 'r') as content_file:
    #         script = content_file.read()
    #     return script

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user =  self.get_secure_cookie("username")
        return user

class LoginHandler(BaseHandler):
    def get(self):
        message = self.get_secure_cookie("message")
        if message == None:
            message = "Welcome to Machine Edge"
        self.clear_cookie("message")
        self.render('login.html',message=message)

    def post(self):
        username = self.get_argument("username")
        pwd = self.get_argument("password")
        if username == "admin" and  pwd == "admin":
            self.set_secure_cookie("username", username)
            self.redirect("/")
        else:#Login Failed
            message = self.set_secure_cookie("message","Login Failed...")
            self.redirect("/login")

class WelcomeHandler(BaseHandler): 
    @tornado.web.authenticated 
    def get(self):
        self.render('index.html',page=None, user=self.current_user)

class VisualHandler(BaseHandler): 
    @tornado.web.authenticated 
    def get(self):
        self.render('visualization.html',page="visualization", title="Chart Title", user=self.current_user)

class PredictionHandler(BaseHandler): 
    @tornado.web.authenticated 
    def get(self):
        self.render('prediction.html',page="prediction", user=self.current_user)

class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("username")
        self.redirect("/login")

if __name__ == "__main__":
    tornado.options.parse_command_line()

    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path":os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "xsrf_cookies": True,
        "login_url": "/login",
        "ui_modules": {"chart":ChartModule}
    }

    application = tornado.web.Application([
        (r'/', WelcomeHandler),
        (r'/login', LoginHandler),
        (r'/visual',VisualHandler),
        (r'/predict',PredictionHandler),
        (r'/logout', LogoutHandler)
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()