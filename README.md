## #CardinalsLose
Written to run on a Heroku dyno, to check if the Cardinals lost on the date it is running.

MLB data is from http://gd2.mlb.com/components/.

Example output:

    **** Checking game from 2015-05-30 15:22:32.958976-05:00 ****
    Cardinals play on this date
    Cardinals Lost!
    there was already a tweet for this game
    ******
    **** Checking game from 2015-05-31 15:22:33.037182-05:00 ****
    Cardinals play on this date
    Cardinals won :(
    ******
    Data is being saved into a PostgreSQL database in Heroku, in order to check if there was a tweet already that day.



|  game_num |game_id | game_start | time_tweeted |
| --- | --- | --- | ---|
|         1 | 2015/05/30/lanmlb-slnmlb-1 | 2015-05-30 19:15:00 | 2015-05-31 00:31:05.099297  |
|         1 | 2015/06/01/milmlb-slnmlb-1 | 2015-06-01 20:10:00 | 2015-06-01 22:30:42.540602  |
|         1 | 2015/06/06/slnmlb-lanmlb-1 | 2015-06-06 22:10:00 | 2015-06-07 00:30:21.240826  |
