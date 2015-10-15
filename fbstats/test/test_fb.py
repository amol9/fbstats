from unittest import TestCase, main as ut_main
from os.path import realpath, dirname, join as joinpath, exists
import os

from fbstats.fb import FB
from fbstats.dbmanager import DBManager
from fbstats import globals


class TestFB(TestCase):
	db_name = 'test.db'

	def setUp(self):
		if exists(self.db_name):
			os.remove(self.db_name)

		self.create_db()
		#globals.data_dir = '.'
		#globals.db_name = self.db_name


	def create_db(self):
		script_path = joinpath(dirname(realpath(__file__)).rsplit(os.sep, 1)[0], 'sql/create_db.sql')
		dbmgr = DBManager(self.db_name)
		dbmgr.create_db(script_path)


	def test_add_job_period(self):
		FB.__init__ = lambda x : None

		dbmgr = DBManager(self.db_name)
		dbmgr.connect()
		fb = FB()
		fb._db = dbmgr


		fb.add_job_period()
		self.assertEqual(dbmgr.query("SELECT count(*) FROM job_period")[0][0], 20)

		fb.add_job_period()
		self.assertEqual(dbmgr.query("SELECT count(*) FROM job_period")[0][0], 20)


if __name__ == '__main__':
	ut_main()

