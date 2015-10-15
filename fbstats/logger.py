import logging
import sys
import os
from os.path import join as joinpath

from . import globals


class Logger():

	def __init__(self, job=False):
		self._log = logging.getLogger('fbstats')

		if job:
			logfh = logging.FileHandler(joinpath(globals.data_dir, globals.log_filename))
			logfh.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
			logfh.setLevel(logging.INFO)
			self._log.addHandler(logfh)
			self._log.setLevel(logging.INFO)
		else:
			logst = logging.StreamHandler(sys.stdout)
			logst.setLevel(logging.DEBUG)
			self._log.addHandler(logst)
			self._log.setLevel(logging.DEBUG)


	def info(self, msg):
		self._log.info(msg)


	def warning(self, msg):
		self._log.warning(msg)


	def error(self, msg):
		self._log.error(msg)


if (len(sys.argv) > 1 and sys.argv[1] == 'job'):
	log = Logger(True)
else:
	log = Logger()

