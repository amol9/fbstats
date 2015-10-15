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


	def get_token(self):
		if self._token:
			return self._token

		result = self._db.query("SELECT token, expiry FROM access")
		if len(result) == 0:
			return self.authenticate()
		elif result[0]['expiry'] < int(time()):
			log.error('token expired, need to authenticate..')
			return self.authenticate()
		else:
			self._token = result[0]['token']
			return self._token

	
	def authenticate(self):
		print("Need to authenticate the application...")
		sleep(2)

		webbrowser.open_new_tab('https://www.facebook.com/dialog/oauth?client_id=500614936716977&'+
					'redirect_uri=http://localhost:8080/&'+
					'response_type=code&scope=read_stream,user_photos')

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
			res = urllib.urlopen('https://graph.facebook.com/oauth/access_token?client_id=500614936716977&'+
						'redirect_uri=http://localhost:8080/&'+
						'client_secret=6e3458a3c1512a59b34777b2d4c0dfa1&code=' + code[0])
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

