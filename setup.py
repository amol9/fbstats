import ez_setup
ez_setup.use_setuptools()

import platform
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
from os.path import join as joinpath, realpath, dirname

from fbstats.version import __version__
from fbstats import globals


entry_points = {}
entry_points['console_scripts'] = ['fbstats=fbstats.main:main']
if platform.system() == 'Windows':
	entry_points['gui_scripts'] = ['fbstats=fbstats.main:main']


class FBStatsInstall(install):

	def run(self):
		install.run(self)
		dbmgr = DBManager(joinpath(globals.data_dir, globals.db_name))
		dbmgr.create_db()


setup(	
	name			= 'fbstats',
	version			= __version__,
	description		= 'A command line utility to collect data from your facebook feed.',
	author			= 'Amol Umrale',
	author_email 		= 'babaiscool@gmail.com',
	url			= 'http://pypi.python.org/pypi/fbstats/',
	packages		= find_packages(),
	include_package_data	= True,
	scripts			= ['ez_setup.py'],
	entry_points 		= entry_points,
	install_requires	= ['mutils'],
	cmdclass		= FBStatsInstall,
	classifiers		= [
					'Development Status :: 4 - Beta',
					'Environment :: Console',
					'License :: OSI Approved :: MIT License',
					'Natural Language :: English',
					'Operating System :: POSIX :: Linux',
					'Programming Language :: Python :: 2.7',
					'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
				]
)

