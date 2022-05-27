from datetime import date
from itertools import count
import json
import sqlite3
import redis
import uuid

from typing import List
from pydantic import BaseModel, Field, BaseSettings
from fastapi import Depends, FastAPI, Request


#setting DB path
DATABASE = './userShard.db'

#setting up the redis client
redisClient = redis.Redis(db=1)

#setting up FastAPI with root path
app = FastAPI(root_path="/api/v1")


#connecting to stats.db
def get_db():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    return cursor

    
#connecting to sharded DB
def get_shard_db(shard_num):

    sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
    sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
    
    if shard_num==1:
        #if value is 1 connect to shard_1.db
        connection = sqlite3.connect('shard_1.db', detect_types=sqlite3.PARSE_DECLTYPES)
        print("connected to shard 1")
    elif shard_num==2:
        #if value is 2 connect to shard_2.db
        connection = sqlite3.connect('shard_2.db', detect_types=sqlite3.PARSE_DECLTYPES)
        print("connected to shard 2")
    else:
        #if value is 0 connect to shard_3.db
        connection = sqlite3.connect('shard_3.db', detect_types=sqlite3.PARSE_DECLTYPES)
        print("connected to shard 3")

    return connection


#1st API in which we are checking if there is any record with the given userID and gameID
#if NOT then creating a new dictionary with the structure and saving in redis
@app.get('/startgame/{userId}/{gameId}')
def startGame(userId, gameId):


    #creating new dictionary with a structure
    states = dict()
    states.update(
        {
            "userId":"", 
            'gameId':"", 
            'gameState':"", 
            'guessRemaining':"6",
            'guesses':{
                'guess1':"",
                'guess2':"",
                'guess3':"",
                'guess4':"",
                'guess5':"",
                'guess6':""
            }
                
        })

    #updating userId and gameId in the dictionary
    states.update({'userId': userId, 'gameId': gameId})

    #fetching the UUID from stats.db
    fetchuuid = get_db()
    get_uuid = fetchuuid.execute("select * from users where user_id = ?", [userId]).fetchall()
    shard_num = 0

    #determining the shard number based on the UUID
    for row in get_uuid:
        shard_num = int(uuid.UUID(row[2])) % 3 + 1
    

    #connecting to the sharded DB
    fetchConnection = get_shard_db(shard_num)
    fetchShardCursor = fetchConnection.cursor()
    fetchShardCursor.execute("SELECT user_id, game_id from games where user_id = ? AND game_id = ?", [userId, gameId])
    startGame = fetchShardCursor.fetchone()


    #if there is any data in the result i.e. if any record exist the the DB, then we will return "Game already played"
    if startGame:
        return "You have already played the game"
    else:

        #updating the game state
        states.update({'gameState': 'New'})
        json_states = json.dumps(states)
        redisClient.set("states", json_states)
        return "This is a new game"



#2nd API - in this we are changing the game state, word guessed and the number of guesses remaining
@app.get('/updateGuess/{guessWord}')
def updateGuess(guessWord):
    
    gameStates = json.loads(redisClient.get("states").decode('utf-8'))
    

    if(6 - int(gameStates.get('guessRemaining')) == 0):
        gameStates['guesses']['guess1'] = guessWord
    elif(6 - int(gameStates.get('guessRemaining')) == 1):
        gameStates['guesses']['guess2'] = guessWord
    elif(6 - int(gameStates.get('guessRemaining')) == 2):
        gameStates['guesses']['guess3'] = guessWord
    elif(6 - int(gameStates.get('guessRemaining')) == 3):
        gameStates['guesses']['guess4'] = guessWord
    elif(6 - int(gameStates.get('guessRemaining')) == 4):
        gameStates['guesses']['guess5'] = guessWord
    elif(6 - int(gameStates.get('guessRemaining')) == 5):
        gameStates['guesses']['guess6'] = guessWord


    #calling the function to change the number of guesses remaining
    gameStates = updateGuessRemaining(gameStates)

    #changing the game state
    if(int(gameStates.get('guessRemaining')) in range(1,6)):
        gameStates.update({'gameState': 'Ongoing'})
    else:
        gameStates.update({'gameState': 'Finished'})
        
    json_states = json.dumps(gameStates)

    redisClient.set("states", json_states)

    redisClient.bgsave()

    return gameStates
            
    

#restoring the current game in the cache
@app.get('/restoreGame/{userId}')
def restoreGame(userId):
    allGames = json.loads(redisClient.get("states").decode('utf-8'))
    restoreGame = allGames[userId]
    return "Current game state -> " + restoreGame


#function to update the number of remaining guesses
def updateGuessRemaining(states):

    if(int(states.get('guessRemaining')) > 0):
        states.update({'guessRemaining': int(states['guessRemaining'])  - 1})
        return states

    else:
        return "You only have 6 tries"