import os
import psycopg2
import psycopg2.extras

class MyDB(object):
	_db_connection = None
	db_cur = None

	_dbName = os.environ['DB_NAME']
	_dbUser = os.environ['DB_USER']
	_dbHost = os.environ['DB_HOST']
	_dbPassword = os.environ['DB_PASSWORD']


	def __init__(self):
		try:
			self._db_connection = psycopg2.connect("dbname="+ self._dbName + " user="+ self._dbUser + " host="+ self._dbHost + " password="+ self._dbPassword)
		except:
			print "I am unable to connect to the database"
		self.db_cur = self._db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
		self.db_cur.execute("CREATE TABLE IF NOT EXISTS tweets (id serial PRIMARY KEY, content text, is_doubleheader boolean, game_num int, game_id text, game_start timestamp, time_tweeted timestamp default now());")


	def finish_query(self):
		self._db_connection.commit()
		self.db_cur.close()
		self._db_connection.close()

	# def __del__(self):
	# 	self._db_cur.close()
	# 	self._db_connection.close()
