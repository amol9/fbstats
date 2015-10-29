import sys
import os
from os.path import exists

from mutils.system.scheduler import get_scheduler, PlatformError, FrequencyError
from redcmd import subcmd, CommandLine, CommandLineError, CommandError

from . import globals
from .fb import FB
from .action import Action


@subcmd
def job():
	'''Run fbstats as a job.'''

	fb = FB()

	fb.add_job_perid()
	fb.get_friends()
	fb.update_stream()
	fb.get_stream_job()
	fb.clean_duplicates()
	fb.get_likes()
	fb.get_comments()


@subcmd
def schedule(self):
	'Commands to schedule fb stats collection.'
	pass


@subcmd(parent='schedule')
def add(frequency):
	'''Add schedule.
	frequency: time frequency for changing wallpaper'''

	scheduler = get_scheduler()

	try:
		scheduler.schedule(frequency, 'fbstats job', globals.scheduler_taskname)
		print('schedule created..')

	except (PlatformError, FrequencyError) as e:
		print(e)
		raise CommandError()

	add.__extrahelp__ = Scheduler.frequency_help + os.linesep
	add.__extrahelp__ += 'If schedule already exists, it\'ll be overwritten'


@subcmd(parent='schedule')
def remove():
	'Remove schedule.'

	try:
		scheduler = get_scheduler()
		scheduler.remove()
		print('schedule removed..')

	except (PlatformError, FrequencyError) as e:
		print(e)
		raise CommandError()
	

@subcmd
def plot():
	'Commands to plot various charts.'
	pass


@subcmd(parent='plot')
def likes(count=10):
	'''Plot top users by likes count.
	count: number of users to plot'''

	pass


@subcmd(parent='plot')
def posts(count=10):
	'''Plot top users by posts count.
	count: number of users to plot'''

	pass

@subcmd(parent='plot')
def timeline(first_name, last_name):
	'''Plot a user's timeline in terms of posts count.
	first_name:	first name of the user
	last_name:	last name of the user'''

	pass


@subcmd(parent='plot')
def graph(start_date, end_date):
	'''Plot a graph of users connected by count of their likes and comments.
	start_date: 	start date of posts
	end_date: 	end date of posts
	
	Date must be of the form: ddmmmyyyy, e.g. 26jan2015.'''

	fb = FB()
	fb.render_graph(start=start_date, end=end_date)


@subcmd
def setapp():
	'Set app id and app secret.'

	db_path = joinpath(globals.data_dir, globals.db_name)
	db = DBManager(db_path)
	db.connect()

	fba = FBAccess(db)
	fba.prompt_app_details()
	db.disconnect()


def check_data_dir():
	if not exists(globals.data_dir):
		os.mkdir(globals.data_dir)


def main():
	check_data_dir()

	action.register("plot\s+(?P<type>user_posts)\s+(?P<first_name>\w+)\s+(?P<last_name>\w+)", fb.render_plot)
	action.register("plot\s+(?P<type>\w+)(?:\s+(?P<count>\d+))?", fb.render_plot, {'type': str, 'count': int})

	commandline = CommandLine()
	try:
		commandline.execute()
	except CommandLineError as e:
		print(e)

