from unittest import TestCase, main as ut_main
from os.path import exists, dirname, realpath, join as joinpath
import os

from fbstats.dbmanager import DBManager


class TestDBManager(TestCase):
	db_name = 'test.db'

	def setUp(self):
		if exists(self.db_name):
			os.remove(self.db_name)


	def tearDown(self):
		if exists(self.db_name):
			os.remove(self.db_name)


	def test_create_db(self):
		script_path = joinpath(dirname(realpath(__file__)).rsplit(os.sep, 1)[0], 'sql/create_db.sql')
		dbmgr = DBManager(self.db_name)
		dbmgr.create_db(script_path)

		select_query = "SELECT count(*) FROM "

		self.assertEqual(dbmgr.query(select_query + "stream")[0][0], 0)
		self.assertEqual(dbmgr.query(select_query + "user")[0][0], 0)
		self.assertEqual(dbmgr.query(select_query + "device")[0][0], 0)
		self.assertEqual(dbmgr.query(select_query + "like")[0][0], 0)
		self.assertEqual(dbmgr.query(select_query + "comment")[0][0], 0)
		self.assertEqual(dbmgr.query(select_query + "job_period")[0][0], 0)
		self.assertEqual(dbmgr.query(select_query + "photo")[0][0], 0)
		self.assertEqual(dbmgr.query(select_query + "access")[0][0], 0)


if __name__ == '__main__':
	ut_main()

