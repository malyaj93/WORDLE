import sqlite3
import random
import traceback
import uuid
import contextlib

from pydantic import BaseModel, Field
from fastapi import Depends, FastAPI, status

NUM_STATS = 1_000_000
NUM_USERS = 100_000
DATABASE = './var/stats.db'

class user(BaseModel):
	user: str
	gameID: int

# gen_uuid function uses to create uuid column in table users and game
def gen_uuid():
	sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
	sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
	con = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
	cur = con.cursor()

	# uuid column  will create in users table
	try:
		cur.execute("ALTER TABLE users ADD COLUMN uuid GUID") 
	except:
		pass
	

	# generating  the key-value pairs: userid and uuid
	user_id_uuid_dict = {}
	# Each user's uuid is generated and inserted into the uuid column by for loop.
	for i in range(NUM_USERS+1):
		# generate uuid
		user_uuid = uuid.uuid4() 
		#insertion to dictionary
		user_id_uuid_dict[i] = user_uuid 
		cur.execute("UPDATE users SET uuid = ? WHERE user_id = ?", [user_uuid, i])
	con.commit()

gen_uuid()

#Creating 3 shard for games table
def shards():
	sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
	sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
	con = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
	cur = con.cursor()

	con_User= sqlite3.connect('userShard.db')
	cur_User= con_User.cursor()
	cur_User.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER, username VARCHAR UNIQUE, uuid VARCHAR PRIMARY KEY)")

	userID = ""

	for i in range(3):
		con_shard = sqlite3.connect('shard_' + str(i+1) + '.db')
		cur_shard = con_shard.cursor()
		cur_shard.execute("CREATE TABLE IF NOT EXISTS games(user_id INTEGER NOT NULL, game_id INTEGER NOT NULL, finished DATE DEFAULT CURRENT_TIMESTAMP, guesses INTEGER, won BOOLEAN, uuid VARCHAR, PRIMARY KEY(user_id, game_id))")
	
	try:
		#Iterate through the user database, compute the shard using the UUID, then retrieve all game entries for that user from the games database and shard into the appropriate shard database. 

		get_info = cur.execute("SELECT * FROM users").fetchall()
		for row in get_info:
			print("User ID: " + str(row[0]))
			print("User UUID: " + str(row[2]))

			#Using the UUID value, get the shard number for this row's user by modulo 3
			shard_num = int(row[2]) % 3 + 1

			print("Shard Number is: " + str(shard_num))

			#Making connection with created shards of db
			con_shard = sqlite3.connect('shard_' + str(shard_num) + '.db', detect_types=sqlite3.PARSE_DECLTYPES)
			cur_shard = con_shard.cursor()

			#Insert row to User Shard
			cur_User.execute("INSERT INTO users VALUES(?, ?, ?)", (str(row[0]), str(row[1]), str(row[2])))
			con_User.commit()
			
			#Retireving user's game data and inserting it in shard DB 
			shard_game = cur.execute("SELECT * FROM games WHERE user_id = ?", (row[0],)).fetchall()
			for game_detail in shard_game:
				print(game_detail, str(row[2])) 
				cur_shard.execute("INSERT INTO games VALUES(?, ?, ?, ?, ?, ?)", (game_detail[0], game_detail[1], game_detail[2], game_detail[3], game_detail[4], str(row[2])))
				con_shard.commit()
			con_shard.close()
		con.close()
		con_User.close()
	except:
		traceback.print_exc()

shards()