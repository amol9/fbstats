
# add command: schedule [add / remove]
def main()
	fb = FB()
	action = Action()

	def stream(): 
		for i in range(0, 14): fb.get_stream(cont=True)
	action.register("stream", stream) 
	action.register("ustream", fb.update_stream)
	action.register("likes", fb.get_likes)
	action.register("comments", fb.get_comments)
	action.register("friends", fb.get_friends)
	action.register("clean", fb.clean_duplicates)
	
	def update():
		fb.update_stream(); fb.get_stream(); fb.get_likes(); fb.get_comments()
	action.register("update", update) 
	action.register("graph(?:\s+(\w+)\s+(\w+))?", fb.render_graph)
	action.register("plot\s+(?P<type>user_posts)\s+(?P<first_name>\w+)\s+(?P<last_name>\w+)", fb.render_plot)
	action.register("plot\s+(?P<type>\w+)(?:\s+(?P<count>\d+))?", fb.render_plot, {'type': str, 'count': int})
	action.register("add_job_period(?:\s+(?P<start>\w+)\s+(?P<end>\w+))?", fb.add_job_period, {'start': str, 'end': str})

	def job():
		fb.check_internet(); fb.update_stream(); fb.get_stream_job(); fb.clean_duplicates(); fb.get_likes(); fb.get_comments()
	action.register("job", job)
	action.register("photos(?:\s+(?P<cont>\d))?", fb.get_photos, {'cont': int})

	if len(sys.argv) > 1:
		try:
			action.do(sys.argv[1:])
		except FBError as fe:
			print(fe.message + '\nexiting...')

	
