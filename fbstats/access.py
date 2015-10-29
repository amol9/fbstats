import urllib
from time import time, sleep
import webbrowser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import urlparse
from threading import Thread

from logger import log


class FBHTTPRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		
		if len(self.path) > 6 and self.path[2:6] == 'code':
			#print 'starting thread'
			#Thread(target=FBHTTPRequestHandler.process_code, args=(self.path,)).start()
			print 'processing code..'
			self.process_code(self.path)
		else:
			self.wfile.write('authenticated')
		#self.wfile.write(response)
	
	
class FBAccessException(Exception):
	pass


class FBAccess():
	def __init__(self, db):
		self._db = db
		self._token = None
		self._expiry = None


	def prompt_app_details(self):
		print('enter app details:')
		self._client_id = raw_input('app id: ')
		self._client_secret = raw_input('app secret: ')

		self._db.update('access', {'client_id': self._client_id, 'client_secret': self._client_secret})
		self._db.commit()


	def read_app_details(self):
		result = self._db.query("SELECT client_id, client_secret FROM access")

		if len(result) == 0 or result[0]['client_id'] == None or result[0]['client_secret'] == None:
			self.prompt_app_details()
		else:
			self._client_id = result[0]['client_id']
			self._client_secret = result[0]['client_secret']


	def get_token(self):
		if self._token:
			return self._token

		result = self._db.query("SELECT token, expiry FROM access")

		if len(result) == 0:
			log.error('need to authenticate..')
			self.authenticate()
		elif result[0]['expiry'] < int(time()):
			log.error('token expired, need to authenticate..')
			self.authenticate()
		else:
			self._token = result[0]['token']
			return self._token

	
	def authenticate(self):
		self.read_app_details()
		print('a browser tab will now open for authenticating the app..')

		sleep(2)

		webbrowser.open_new_tab('https://www.facebook.com/dialog/oauth?client_id=%s&'+
					'redirect_uri=http://localhost:8080/&'+
					'response_type=code&scope=read_stream,user_photos'%self._client_id)

		code = self.run_server()

		if not self._token:
			raise FBAccessException('authentication failed')

		self._db.query("DELETE FROM access");
		self._db.insert('access', (self._token, self._expiry))
		self._db.commit()

		return self._token


	def process_code(self, path):
		code = urlparse.parse_qs(path[2:]).get('code', None)
		
		try:
			res = urllib.urlopen('https://graph.facebook.com/oauth/access_token?client_id=%s&'+
						'redirect_uri=http://localhost:8080/&'+
						'client_secret=%s&code=%s'%(self._client_id, self._client_secret, code[0]))
		except Exception as e:
			print e.message

		print res.getcode()
		r = res.read()
		print r
		open('newat', 'w').write(r)

		token = None
		try:
			data = urlparse.parse_qs(r)
			self._token = data['access_token'][0]
			self._expiry = int(data['expires'][0])

			self._expiry += int(time())

			print 'token: %s, expiry: %s'%(self._token, self._expiry)
		except Exception as e:
			print e.message


	def run_server(self):
		FBHTTPRequestHandler.process_code = self.process_code
		httpd = HTTPServer(('', 8080), FBHTTPRequestHandler)
		httpd.handle_request()
		#httpd.handle_request()
		

	token = property(get_token)

