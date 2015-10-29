from unittest import TestCase, main as ut_main
from os.path import exists, realpath, dirpath
from StringIO import StringIO
import sys
import os


class TestAccess(TestCase):
	db_name 		= 'test.db'
	app_secret_filename 	= 'app.secret'
	app_secret_filepath 	= joinpath(dirpath(realpath(__file__)), TestAccess.app_secret_filename)


	def setUp(self):
		if exists(self.db_name):
			os.remove(self.db_name)


	def tearDown(self):
		if exists(self.db_name):
			os.remove(self.db_name)


	def test_get_token(self):
		app_id = None
		app_secret = None

		if not exists(app_secret_filepath):
			self.fail('This test expects a file named %s in the same directory as the test class file with client_id \
					on the first line and client_secret on the second line.')

		with open(self.app_secret, 'r') as f:
			lines = f.read().split('\n')
			app_id = lines[0].strip()
			app_secret = lines[1].strip()

		dbm = DBManager(self.db_name)
		dbm.connect()

		fba = FBAccess()

		oldstdin = sys.stdin
		sys.stdin = StringIO(app_id + os.linesep + app_secret)

		token = fba.get_token()

		sys.stdin = oldstdin

		self.assertTrue(token is not None and len(token) > 0)

		#test token by making a call to fb
		#test db record data, record count = 1
		#request again
		#test if same token and db status


if __name__ == '__main__':
	ut_main()

