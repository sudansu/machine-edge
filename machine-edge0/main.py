import os.path

import tornado.ioloop
import tornado.web

class _index(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html')
		
class _login(tornado.web.RequestHandler):
	def get(self):
		self.render('login.html')

def makeApp():
	return tornado.web.Application(
		handlers = [(r'/', _index),(r'/login', _login)],
		template_path = os.path.join(os.path.dirname(__file__),'template'),
		static_path = os.path.join(os.path.dirname(__file__),'static'),
		debug = True)

if __name__ == '__main__':
	app = makeApp()
	app.listen(8000)
	tornado.ioloop.IOLoop.current().start()