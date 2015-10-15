import logging
import sys
import os

LOG_FILEPATH = os.path.expanduser('~') + '/.cronlogs/fbstats.log'

class Logger():

	def __init__(self, job=False):
		self._log = logging.getLogger('fbstats')

		if job:
			logfh = logging.FileHandler(LOG_FILEPATH)
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


if (sys.argv[1] == 'job'):
	log = Logger(True)
else:
	log = Logger()

