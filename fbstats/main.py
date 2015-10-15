import sys
import os
from os.path import exists

from mutils.system.scheduler import get_scheduler

from . import globals
from .fb import FB
from .action import Action


# add command: schedule [add / remove]
def main():
	check_data_dir()

	action = Action()
	fb = FB()

	action.register("graph(?:\s+(\w+)\s+(\w+))?", fb.render_graph)
	action.register("plot\s+(?P<type>user_posts)\s+(?P<first_name>\w+)\s+(?P<last_name>\w+)", fb.render_plot)
	action.register("plot\s+(?P<type>\w+)(?:\s+(?P<count>\d+))?", fb.render_plot, {'type': str, 'count': int})

	action.register("job", job)

	action.register("photos(?:\s+(?P<cont>\d))?", fb.get_photos, {'cont': int})
	action.register("schedule\s+(?P<action>\w+)(?:\s+(?P<period>\w+))?", schedule)

	if len(sys.argv) > 1:
		try:
			action.do(sys.argv[1:])
		except FBError as fe:
			print(fe.message + '\nexiting...')


def job():
	fb = FB()

	fb.add_job_perid()
	fb.get_friends()
	fb.update_stream()
	fb.get_stream_job()
	fb.clean_duplicates()
	fb.get_likes()
	fb.get_comments()

	
def schedule(action, period=None):
	scheduler = get_scheduler()

	if action == 'add':
		scheduler.schedule(period, 'fbstats job', globals.scheduler_taskname)
		print('schedule created..')

	elif action == 'remove':
		scheduler.delete(globals.scheduler_taskname)
		print('schedule removed..')

	else:
		print('unknown schedule action, use add / remove')


def check_data_dir():
	if not exists(globals.data_dir):
		os.mkdir(globals.data_dir)

