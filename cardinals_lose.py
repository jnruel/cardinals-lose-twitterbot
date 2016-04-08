import twitter
import urllib2
import xmltodict
import datetime
import time
import dateutil.parser
from pytz import timezone
import os
import os.path
import psycopg2
from random import randint
from db import MyDB

class CardinalsLose(object):
	_environment 	= os.environ['ENVIRONMENT']

	AUXILIARY_VERBS = ['were', 'have been']
	ADVERBS			= ['positively', 'absolutely', 'completely', 'indubitably', 'totally']

	AVERAGE_LOSS	= ['defeated', 'demolished', 'beaten', 'foiled', 'ousted', 'bested', 'tamed', 'subdued', 'overpowered', 'thwarted', 'humbled', 'discouraged', 'eighty-sixed', 'dismayed', 'overwhelmed', 'shut up', 'overthrown', 'taken down', 'wrecked', 'rejected']
	MAJOR_LOSS 		= ['annihilated', 'destroyed', 'demoralized', 'crippled', 'broken', 'disheartened', 'crushed', 'crippled', 'put down', 'gutted']
	SHUTOUT			= ['shut out', 'blanked', 'silenced']

	_date = None
	_xml_data = None

	def __init__(self, days_ago = None):
		if days_ago is None:
			self._date = datetime.datetime.now(timezone('America/Chicago'))
		else:
			self._date = datetime.datetime.now(timezone('America/Chicago'))-datetime.timedelta(days_ago)

		self._xml_data = self.__getXMLData(self.__createURLFromDate(self._date))


	def __twitter_connect(self):
		consumerKey = os.environ['TWITTER_CONSUMER_KEY']
		consumerSecret = os.environ['TWITTER_CONSUMER_SECRET']
		accessTokenKey = os.environ['TWITTER_ACCESS_TOKEN_KEY']
		accessTokenSecret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

		api = twitter.Api(consumer_key=consumerKey, consumer_secret=consumerSecret, access_token_key=accessTokenKey, access_token_secret=accessTokenSecret)

		return api

	def __parse_date(self, day):
		year 	= day.strftime('%Y')
		month 	= day.strftime('%m')
		day 	= day.strftime('%d')
		return str(year) + str(month) + str(day)


	def __createURLFromDate(self, day):
		year 	= day.strftime('%Y')
		month 	= day.strftime('%m')
		day 	= day.strftime('%d')

		return "http://gd2.mlb.com/components/game/mlb/year_"+ year +"/month_"+ month +"/day_"+ day +"/epg.xml"

	def __getXMLData(self, url):
		urlExists = False
		try:
		    file = urllib2.urlopen(url)
		    urlExists = True
		    data = file.read()
		    parsedData = xmltodict.parse(data, process_namespaces=True)
		    file.close()
		except urllib2.HTTPError, err:
			urlExists = False
		   	if err.code == 404:
		   		print "Page not found!"
		   	elif err.code == 403:
		   		print "Access denied!"
		   	else:
		   		print "Something happened! Error code", err.code
		except urllib2.URLError, err:
			print "Some other error happened:", err.reason

		if urlExists == True:
			# urlExists
			if 'epg' in parsedData:
				if 'game' in parsedData['epg']:
					return parsedData
		else:
			print "no xml data"
			return False


	def __checkIfDoubleHeader(self, day):
		isDoubleHeader = False
		# xml_data = self.getXMLData(self.__createURLFromDate(day))
		if self._xml_data != False:
			if len(self._xml_data['epg']['game'])>20:
				print "only one game probably"
			else:
				for game in self._xml_data['epg']['game']:
					if game['@double_header_sw'] == "Y" or game['@double_header_sw'] == "S":
						if game['@home_team_name'] == "Cardinals" or game['@away_team_name'] == "Cardinals":
							isDoubleHeader = True
		return isDoubleHeader

	def __do_play(self, day):
		do_play = False
		for game in self._xml_data['epg']['game']:
			if game['@home_team_name'] == "Cardinals" or game['@away_team_name'] == "Cardinals":
				do_play = True
			# else:
			# 	# print "Cardinals don't play today"
		return do_play



	def __get_game(self, day, game_num):

		# xml_data = self.getXMLData(self.__createURLFromDate(day))
		cardinals_game = False
		# print date
		if self._xml_data != False:
			if len(self._xml_data['epg']['game'])>20:
				game = self._xml_data['epg']['game']
				print "only one game I think"
				if game['@home_team_name'] == self._date or game['@away_team_name'] == "Cardinals":
					if game['@game_nbr'] == str(game_num):
						cardinals_game = game
						print "returning Cardinals game " + str(game_num)

			else:
				for game in self._xml_data['epg']['game']:
					if game['@home_team_name'] == "Cardinals" or game['@away_team_name'] == "Cardinals":
						if game['@game_nbr'] == str(game_num):
							cardinals_game = game
							print "Cardinals play on this date"

		return cardinals_game


	def __didCardinalsLose(self, game):
		cardinalsLose = False
		if game['@status'] == "Final" or game['@status'] == "Game Over" or game['@status'] == "Completed Early":
			if game['@home_team_name'] == "Cardinals":
				if int(game['@home_team_runs']) < int(game['@away_team_runs']):
					print "Cardinals Lost!"
					cardinalsLose = True
				else:
					print "Cardinals won :("
			elif game['@away_team_name'] == "Cardinals":
				if int(game['@away_team_runs']) < int(game['@home_team_runs']):
					print "Cardinals Lost!"
					cardinalsLose = True
				else:
					print "Cardinals won :("
		elif game['@status'] == "In Progress":
			print "Cardinals are playing and could still conceivably lose today"
		elif game['@status'] == "Postponed":
			print "Game was potponed"
		elif game['@status'] == "Warmup" or game['@status'] == "Preview":
			print "Cardinals game is scheduled to start at " + str((dateutil.parser.parse(game['@start'])).replace(tzinfo = dateutil.tz.tzutc()))
		else:
			print "not sure what the status of the game is"


		return cardinalsLose
		# if cardinalsLose:
		# 	# init_tweet(cardinalsGame)
		# 	return True
		# else:
		# 	return False

	def __did_tweet(self, day, game):
		db = MyDB()
		db.db_cur.execute("SELECT * FROM tweets;")
		tweets_list = db.db_cur.fetchall()
		db.finish_query()

		# if checkIfDoubleHeader(getXMLData(createURLFromDate(day))):

		tweeted = False
		if self.__didCardinalsLose(game):
			for entry in tweets_list:
				if entry['game_id'] == game['@id']:
				# if self.__parse_date(entry['game_start']) == self.__parse_date(day):
					tweeted = True

		if tweeted:
			print "there was already a tweet for this game"
		else:
			print "No tweet yet"

		return tweeted

	def __rand_from_list(self, word_list):
		return word_list[randint(0, len(word_list)-1)]

	def __compose_tweet(self, game):
		cardinalsHome = False
		opponent = ""
		opponent_runs = 0
		cardinals_runs = 0

		if game['@home_team_name'] == "Cardinals":
			cardinalsHome = True
			opponent = game['@away_team_name'].replace(" ", "")
			opponent_runs = int(game['@away_team_runs'])
			cardinals_runs = int(game['@home_team_runs'])
		else:
			opponent = game['@home_team_name'].replace(" ", "")
			opponent_runs = int(game['@home_team_runs'])
			cardinals_runs = int(game['@away_team_runs'])

		if cardinals_runs == 0 and opponent_runs - cardinals_runs >= 3:
			tweet = "The @Cardinals " + self.__rand_from_list(self.AUXILIARY_VERBS) + " " + self.__rand_from_list(self.ADVERBS) + " " + self.__rand_from_list(self.MAJOR_LOSS) + " " + str(opponent_runs) + "-" + str(cardinals_runs) + " by the @" + str(opponent) + "! #CardinalsLose"
		elif cardinals_runs == 0:
			tweet = "The @Cardinals " + self.__rand_from_list(self.AUXILIARY_VERBS) + " " + self.__rand_from_list(self.SHUTOUT) + " " + str(opponent_runs) + "-" + str(cardinals_runs) + " by the @" + str(opponent) + "! #CardinalsLose"
		elif opponent_runs - cardinals_runs >= 3:
			tweet = "The @Cardinals " + self.__rand_from_list(self.AUXILIARY_VERBS) + " " + self.__rand_from_list(self.MAJOR_LOSS) + " " + str(opponent_runs) + "-" + str(cardinals_runs) + " by the @" + str(opponent) + "! #CardinalsLose"
		else:
			tweet = "The @Cardinals " + self.__rand_from_list(self.AUXILIARY_VERBS) + " " + self.__rand_from_list(self.AVERAGE_LOSS) + " " + str(opponent_runs) + "-" + str(cardinals_runs) + " by the @" + str(opponent) + "! #CardinalsLose"



		# tweet = "Cardinals lost " + str(opponent_runs) + "-" + str(cardinals_runs) + " to the " + str(opponent)
		print tweet
		return tweet


	def __init_tweet(self, game):
		content 		= self.__compose_tweet(game)
		is_doubleheader = self.__checkIfDoubleHeader(self._date)
		game_num		= game['@game_nbr']
		game_id			= str(game['@id'])
		game_start		= dateutil.parser.parse(game['@start']).replace(tzinfo = dateutil.tz.tzutc())
		# new_time 		= game_start.replace(tzinfo = dateutil.tz.tzutc())

		time_tweeted 	= datetime.datetime.now(timezone('America/Chicago'))-datetime.timedelta(hours=5)

		if self._environment == 'production':
			db = MyDB()
			db.db_cur.execute("INSERT INTO tweets (content, is_doubleheader, game_num, game_id, game_start, time_tweeted) VALUES (%s, %s, %s, %s, %s, %s)", (content, is_doubleheader, game_num, game_id,game_start, time_tweeted))
			db.finish_query()

			twitter = self.__twitter_connect()
			twitter.PostUpdate(content)



	# check today and yesterday, in case it missed yesterday's game for whatever reason
	def go(self):
		print '___CHECK DAY___'
		if self._xml_data:
			if self.__do_play(self._date):
				if self._environment == "local":
					print "local debug"

				if not self.__checkIfDoubleHeader(self._date):
					print "**** Checking game from " + str(self._date) + " ****"
					game_today = self.__get_game(self._date, 1)
					if self.__didCardinalsLose(game_today):
						if not self.__did_tweet(self._date, game_today):
							self.__init_tweet(game_today)
				else:
					game_one = self.__get_game(self._date, 1)
					game_two = self.__get_game(self._date, 2)

					print "**** Checking game 1, start time of: " + str(dateutil.parser.parse(game_one['@start']).replace(tzinfo = dateutil.tz.tzutc())) + " ****"
					if self.__didCardinalsLose(game_one):
						if not self.__did_tweet(self._date, game_one):
							self.__init_tweet(game_one)

					print "**** Checking game 2, start time of: " + str(dateutil.parser.parse(game_two['@start']).replace(tzinfo = dateutil.tz.tzutc())) + " ****"
					if self.__didCardinalsLose(game_two):
						if not self.__did_tweet(self._date, game_two):
							self.__init_tweet(game_two)
			else:
				print "Cardinals don't play on this date"
		else:
			print "xml was not gotten"
		print "******"



	def test(self):
		self.__do_play(self._date)
