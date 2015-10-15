import urllib
import re
import json
import sys
from dbmanager import DBManager
from time import time, sleep, timezone
from datetime import timedelta, datetime
import os
from subprocess import Popen, PIPE
from collections import namedtuple
from os.path import join as joinpath, dirname, realpath, exists, split as splitpath

from graph import Graph
from logger import log
from action import Action
from access import FBAccess, FBAccessException


PlotInfo = namedtuple('PlotInfo', ['query', 'title', 'x'])

class FBError(Exception):
	pass


class FB():
	def __init__(self):
		dir_path = dirname(realpath(__file__))
		db_path = joinpath(splitpath(dir_path)[0], 'data', '1.db')

		if not exists(db_path):
			log.error('db file not found')
			raise FBError

		self._db = DBManager(db_path)
		self._db.connect()

		self._types = "(type = 46 OR type = 80 OR type = 128 OR type = 247 OR type = 308 OR type = 60)"
		self._fql_limit = 20

		try:
			fbaccess = FBAccess(self._db)
			self._access_token = fbaccess.token
		except FBAccessException as fbae:
			raise FBError(fbae.message)


	def __del__(self):
		self._db.disconnect()


	def do_fql(self, query):
		if self._fql_limit == 0:
			log.error('FQL call limit exceeded')
			raise FBError
		self._fql_limit -= 1

		query_url = 'https://graph.facebook.com/fql?' + urllib.urlencode({'q' : query, 'access_token' : self._access_token})
		log.info(query_url)
	
		try:	
			response = urllib.urlopen(query_url)
			log.info(response.getcode())
		except Exception as e:
			log.error(e.strerror)
			raise FBError

		try:
			data = response.read()
			jdata = json.loads(data)
			log.info('record count = %d'%len(jdata['data']))
		except Exception as e:
			log.error(e.strerror)
			log.info(data)
			raise FBError
		return jdata


	def get_friends(self):
		friends_query = """SELECT uid, first_name, middle_name, last_name, sex, relationship_status, pic, 
				significant_other_id, age_range, birthday_date, current_location, friend_count, 
				hometown_location FROM user WHERE uid IN (SELECT uid2 FROM friend WHERE uid1=me()) OR uid=me()"""

		jdata = self.do_fql(friends_query)

		users = self._db.query("SELECT * FROM user WHERE deleted = 0")
		user_ids = [i['id'] for i in users]

		for record in jdata['data']:
			for k in record:
				if (record[k] == ''):
					record[k] = None
			if (record['friend_count'] != None):
				record['friend_count'] = int(record['friend_count'])
			if (record['sex'] != None):
				record['sex'] = record['sex'][0]
			if (record['hometown_location'] != None):
				record['hometown_location'] = record['hometown_location']['name']
			if (record['current_location'] != None):
				record['current_location'] = record['current_location']['name']
			if (record['age_range'] != None):
				record['age_range'] = str(record['age_range']['min'])

			if record['uid'] in user_ids:
				user = [u for u in users if u['id'] == record['uid']][0]
				update_values = {}

				for key in record.keys():
					if key in ['uid']:
						continue
					if record[key] != user[key.encode()]:
						update_values[key.encode()] = record[key]

				if len(update_values) > 0:
					self._db.update('user', update_values, "id = \'%s\'"%record['uid'])
					print update_values
					print 'u ',; sys.stdout.flush()
					#raw_input()

				user_ids.remove(record['uid'])
			else:
				self._db.insert('user', (record['uid'], record['first_name'], record['middle_name'],
					record['last_name'], record['sex'], record['relationship_status'], record['pic'], 
					record['significant_other_id'], record['age_range'], record['birthday_date'], 
					record['current_location'], record['friend_count'], record['hometown_location'],
					0))
				log.info('new friend: %s %s'%(record['first_name'], record['last_name']))

		for user_id in user_ids:
			self._db.update('user', {'deleted': 1}, "id = \'%s\'"%user_id)
			user = [u for u in users if u['id'] == user_id][0]
			log.info('deleted friend: %s %s'%(user['first_name'], user['last_name']))

		self._db.commit()
		
	def get_stream(self, start_time=None, end_time=None, cont=False):
		def db_insert(jdata):
			for record in jdata['data']:
				for k in record:
					if (record[k] == ''):
						record[k] = None

				self._db.insert('stream', (record['post_id'], record['actor_id'], record['created_time'], 
					record['type'], record['like_info']['like_count'], record['comment_info']['comment_count'], 
					1 if record['is_popular'] else 0, record['message'], record['share_count'], 
					record['permalink'], None, None, None, 0, 0, 0))	#last 3: updated(remove), update_likes, update_comments

				self._db.commit()
				print '.',; sys.stdout.flush()

		if not (start_time and end_time):
			if cont:
				if os.path.exists('./end_time'):
					end_time = int(open('./end_time', 'r').read().strip())
				else:
					end_time = int(time()) #+ int(timedelta(days=-6).total_seconds())
			else:
				end_time = int(time()) #+ int(timedelta(days=-6).total_seconds())
			start_time = end_time + int(timedelta(hours=-12).total_seconds())

		
		stream_query = """SELECT post_id, actor_id, created_time, type, like_info, comment_info, 
				is_popular, message, share_count, permalink FROM stream WHERE source_id """ 
		source_clause =	"IN (SELECT uid2 FROM friend WHERE uid1=me())"
		limit_clause = ' LIMIT 500'
		time_clause = ' AND created_time > %d AND created_time < %d'%(start_time, end_time)

		jdata = self.do_fql(stream_query + source_clause + time_clause)
		db_insert(jdata)

		source_clause = "= me()"

		jdata = self.do_fql(stream_query + source_clause + time_clause)				
		db_insert(jdata)

		if cont: open('end_time', 'w').write(str(start_time))


	def update_stream(self):
		post_ids_query = "SELECT post_id, like_count, comment_count, share_count FROM stream WHERE created_time > %d AND %s"\
				%(int(time()) + timedelta(days=-4).total_seconds(), self._types)
		result = self._db.query(post_ids_query)

		rc = len(result)
		while(rc > 0):
			post_ids = ''
			for i in range(len(result)-rc, len(result)-rc+20 if rc>20 else len(result)):
				post_ids += "'%s',"%result[i]['post_id']
			rc -= 20
			post_ids = post_ids.rstrip(',')

			stream_query = "SELECT post_id, like_info, comment_info, share_count FROM stream WHERE post_id IN (%s)"%(post_ids)
			
			jdata = self.do_fql(stream_query)

			def result_find(post_id):
				for row in result:
					if row['post_id'] == post_id:
						return row
			
			for record in jdata['data']:
				post_id = record['post_id']
				like_count = record['like_info']['like_count']
				comment_count = record['comment_info']['comment_count']
				share_count = record['share_count']

				row = result_find(post_id)
				likes_changed = row['like_count'] != like_count 
				comments_changed = row['comment_count'] != comment_count

				if likes_changed or comments_changed:
					update_query = """UPDATE stream SET like_count = %d, comment_count = %d, share_count = %d, 
							update_likes = %d, update_comments = %d WHERE post_id = '%s'"""\
							%(like_count, comment_count, share_count, 1 if likes_changed else 0, 1 if comments_changed else 0, post_id)
					self._db.query(update_query)
					print('.'),; sys.stdout.flush()
			self._db.commit()
		

	def get_comments(self):
		while(True):
			post_ids_query2 = "SELECT post_id FROM stream LIMIT 30"
			post_ids_query = """SELECT post_id FROM stream WHERE (post_id NOT IN 
					(SELECT DISTINCT post_id FROM comment) OR update_comments = 1) AND comment_count > 0 AND 
					%s LIMIT 20"""%(self._types)
			result = self._db.query(post_ids_query)
			if len(result) == 0:
				return

			post_ids = ''
			for row in result:
				post_ids += "'%s',"%row['post_id']
			post_ids = post_ids.rstrip(',')
			
			like_query = "SELECT post_fbid, post_id, fromid FROM comment WHERE post_id IN (%s)"%post_ids 	#AND user_id IN (SELECT uid2 FROM friend WHERE uid1=me())"%post_ids
			
			jdata = self.do_fql(like_query)

			for record in jdata['data']:
				self._db.insert('comment', (record['post_fbid'], record['post_id'], record['fromid']))
				print '.',; sys.stdout.flush()

			self._db.query("UPDATE stream SET update_comments = 0 WHERE post_id in (%s)"%(post_ids))
			self._db.commit()


	def get_likes(self):
		while(True):
			post_ids_query = """SELECT post_id FROM stream WHERE (post_id NOT IN 
					(SELECT DISTINCT post_id FROM like) OR update_likes = 1) AND like_count > 0 AND 
					%s LIMIT 20"""%(self._types)
			result = self._db.query(post_ids_query)
			if len(result) == 0:
				return

			post_ids = ''
			for row in result:
				post_ids += "'%s',"%row['post_id']
			post_ids = post_ids.rstrip(',')
			
			like_query = "SELECT post_id, user_id FROM like WHERE post_id IN (%s)"%post_ids 	#AND user_id IN (SELECT uid2 FROM friend WHERE uid1=me())"%post_ids
			
			jdata = self.do_fql(like_query)

			for record in jdata['data']:
				self._db.insert('like', (record['post_id'], record['user_id']))

				print '.',; sys.stdout.flush()

			self._db.query("UPDATE stream SET update_likes = 0 WHERE post_id in (%s)"%(post_ids))
			self._db.commit()

		
	def clean_duplicates(self):
		delete_dup_query = None
		with open(joinpath(dirname(realpath(__file__)), 'clean_stream.sql'), 'r') as f:
			delete_dup_query = f.read()

		self._db.executescript(delete_dup_query)
		

	def render_graph(self, start=None, end=None):
		drop_temp_tables = "drop table likejoin; drop table result;"

		filter_self_likes = True
		filter_self_comments = True

		time_period_clause = ""
		if start and end:
			time_period_clause = "AND s.created_time BETWEEN %d AND %d"%(self.get_timestamp(start), self.get_timestamp(end))

		likejoin_query = """CREATE TEMP TABLE likejoin AS 
				SELECT s.source_id AS user1, l.user_id AS user2 FROM stream AS s 
				JOIN like AS l 
				ON s.post_id = l.post_id %s WHERE (l.user_id IN (SELECT id FROM user WHERE deleted = 0)
				AND s.source_id IN (SELECT id FROM user WHERE deleted = 0)) %s"""\
				%("AND s.source_id <> l.user_id" if filter_self_likes else "", time_period_clause) 
		
		commentjoin_query = """INSERT INTO likejoin 
				SELECT s.source_id AS user1, c.user_id AS user2 FROM stream AS s 
				JOIN comment AS c 
				ON s.post_id = c.post_id %s WHERE (c.user_id IN (SELECT id FROM user WHERE deleted = 0)
				AND s.source_id IN (SELECT id FROM user WHERE deleted = 0)) %s"""\
				%("AND s.source_id <> c.user_id" if filter_self_comments else "", time_period_clause) 

		result_query = """CREATE TEMP TABLE result AS 
				SELECT min(t1.user1, t1.user2) AS fuser1, max(t1.user1, t1.user2) AS fuser2,
				t1.c+coalesce(t2.c, 0) AS count 
				FROM 
				(SELECT *, count(user1) AS c FROM likejoin GROUP BY user1, user2) AS t1 
				LEFT JOIN 
				(SELECT *, count(user1) AS c FROM likejoin GROUP BY user1, user2) AS t2 
				ON t1.user2 = t2.user1 AND t1.user1 = t2.user2 AND t1.user1 <> t1.user2 
				GROUP BY fuser1, fuser2"""

		users_query= """SELECT id, first_name, last_name FROM user WHERE id IN 
				(SELECT fuser1 FROM result UNION SELECT fuser2 FROM result)"""

		self._db.query(likejoin_query);
		self._db.query(commentjoin_query);
		self._db.query(result_query);

		min_max_count = self._db.query("SELECT min(count) as min_count, max(count) as max_count FROM result")[0]

		g = Graph(min_max_count['min_count'], min_max_count['max_count'])

		users = self._db.query(users_query)
		for user in users:
			g.add_node(str(user['id']), str(user['first_name'] + '.' + user['last_name'][0]))

		likes = self._db.query("select * from result;")
		for like in likes:
			g.add_edge(str(like['fuser1']), str(like['fuser2']), like['count'])

		g.render(label='test123')

	
	def render_plot(self, type, count=10, first_name=None, last_name=None):
		plots = {}
		plots['top_posts'] = PlotInfo(query = """SELECT s.count, u.first_name || '.' || substr(u.last_name, 1, 1) AS name FROM 
				(SELECT count(*) AS count, source_id FROM stream WHERE %s GROUP BY source_id) AS s JOIN user AS u 
				ON s.source_id = u.id WHERE u.deleted = 0 ORDER BY s.count DESC LIMIT %d"""%(self._types, count),\
				title = 'Top %d Posts'%(count), x = 'name')

		plots['top_likes'] = PlotInfo(query = """SELECT s.count, u.first_name || '.' || substr(u.last_name, 1, 1) AS name FROM 
				(SELECT sum(like_count) AS count, source_id FROM stream WHERE %s GROUP BY source_id) AS s JOIN user AS u 
				ON s.source_id = u.id WHERE u.deleted = 0 ORDER BY s.count DESC LIMIT %d"""%(self._types, count),\
				title = 'Top %d Likes'%(count), x = 'name')

		plots['user_posts'] = PlotInfo(query = """select count(post_id) as count , strftime("%%m/%%d", datetime(created_time, 'unixepoch')) as day 
					from stream where source_id in (select id from user
					where first_name = '%s' and last_name = '%s') and %s group by day"""%(first_name, last_name, self._types),\
					title = 'Timeline: %s %s'%(first_name, last_name), x = 'day')


		result = self._db.query(plots[type].query)
		data = ''
		count = len(result)
		for row in result:
			data += '%s %s\n'%(row['count'], row[plots[type].x])

		plot_filepath = joinpath(dirname(realpath(__file__)), 'plot.gp')
		plot = Popen(["gnuplot", "-e",  "title='%s'"%(plots[type].title), "-e",\
					"size = '%d, %d'"%(count*60, int(count*60/1.6)), plot_filepath],\
					stdin=PIPE)
		plot.communicate(data)

		
	def add_job_period(self, start=None, end=None):
		if start and end:
			start_timestamp = (datetime.strptime(start, '%d%b%Y') - datetime(1970, 1, 1)).total_seconds() 
			end_timestamp = (datetime.strptime(end, '%d%b%Y') - datetime(1970, 1, 1)).total_seconds() 
		else:
			start_timestamp = self._db.query("SELECT MAX(end_time) FROM job_period")[0][0]
			end_timestamp = start_timestamp + int(timedelta(days=31).total_seconds())
			print start_timestamp, end_timestamp

		while start_timestamp < end_timestamp:
			self._db.insert('job_period', (start_timestamp, start_timestamp + timedelta(hours=12).total_seconds(), 0))
			print('.'),; sys.stdout.flush()
			start_timestamp += timedelta(hours=12).total_seconds()
		self._db.commit()

	
	def get_stream_job(self):
		time_periods_query = "SELECT * FROM job_period WHERE end_time <= %d AND get_count < 2"%(int(time()) - timezone)
		time_periods = self._db.query(time_periods_query)
		
		for tp in time_periods:
			self.get_stream(tp['start_time'], tp['end_time'])
			self._db.query("UPDATE job_period SET get_count = %d WHERE end_time = %d"%(tp['get_count'] + 1, tp['end_time']))
			self._db.commit()

	
	def check_internet(self):
		ping = Popen(['ping', '-c', '1', 'facebook.com'], stdout=PIPE)
		log.info(ping.stdout.read())
		if ping.wait() != 0:
			router = Popen(['router', 'connect'], stdout=PIPE)
			log.info(router.stdout.read())			

	
	def get_timestamp(self, date_string):
		return (datetime.strptime(date_string, '%d%b%Y') - datetime(1970, 1, 1)).total_seconds()


	def get_photos(self, start_time=None, end_time=None, cont=False):
		def db_insert(jdata):
			for record in jdata['data']:
				for k in record:
					if (record[k] == ''):
						record[k] = None

				self._db.insert('photo', (record['pid'], record['aid'], record['caption'], 
					record['comment_info']['comment_count'], record['like_info']['like_count'], record['created'], 
					record['link'], record['owner'], record['place_id'], record['src_big'], 0, 0))

				self._db.commit()
				print '.',; sys.stdout.flush()

		if not (start_time and end_time):
			if cont:
				if os.path.exists('./end_time'):
					end_time = int(open('./end_time', 'r').read().strip())
				else:
					end_time = int(time()) #+ int(timedelta(days=-6).total_seconds())
			else:
				end_time = int(time()) #+ int(timedelta(days=-6).total_seconds())
			start_time = end_time + int(timedelta(hours=-12).total_seconds())

		
		stream_query = """SELECT pid, aid, caption, comment_info, like_info, created, 
				link, owner, place_id, src_big FROM photo WHERE owner """ 
		source_clause =	"IN (SELECT uid2 FROM friend WHERE uid1=me())"
		limit_clause = ' LIMIT 500'
		time_clause = ' AND created > %d AND created < %d'%(start_time, end_time)

		jdata = self.do_fql(stream_query + source_clause) # + time_clause)
		db_insert(jdata)

		source_clause = "= me()"

		jdata = self.do_fql(stream_query + source_clause) # + time_clause)				
		db_insert(jdata)

		if cont: open('end_time', 'w').write(str(start_time))

