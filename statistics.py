import contextlib
from datetime import date
import json
import logging.config
import sqlite3
from unittest import result
import uuid
from colorama import Cursor
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings


#setting DB path
DATABASE = './var/stats.db'



app = FastAPI(root_path="/api/v1")



#connecting to stats.db
def get_db():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    return cursor


#connecting to sharded DB
def get_shard_db(user_id):

    sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
    sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
    check_db = int(user_id) % 3
    if (check_db == 1):
        #if value is 1 connect to shard_1.db
        connection = sqlite3.connect('shard_1.db', detect_types=sqlite3.PARSE_DECLTYPES)
    elif (check_db == 2):
        #if value is 1 connect to shard_2.db
        connection = sqlite3.connect('shard_2.db', detect_types=sqlite3.PARSE_DECLTYPES)
    else:
        #if value is 1 connect to shard_3.db
        connection = sqlite3.connect('shard_3.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = connection.cursor()
    return cursor


#Fetching game details based on game ID
@app.get("/gamedetails/{game_id}")
def gameDetails(game_id):
    cur = get_db()
    winners = cur.execute("select game_id, finished, guesses from games where game_id = ?", [game_id])
    results = [dict((cur.description[i][0], value) \
        for i, value in enumerate(row)) for row in winners]

    return results


#Fetching top 10 results by wins
@app.get("/topTenByWins")
def topTenByWins():
    cur = get_db()
    topTenWins = cur.execute("SELECT * FROM wins ORDER BY wins DESC LIMIT 10")
    results = [dict((cur.description[i][0], value) \
        for i, value in enumerate(row)) for row in topTenWins]

    return results
    

#fetching top ten users   
@app.get("/topTenByStreak")
def topTenByStreak():
    cur = get_db()
    topTenStreaks = cur.execute("select * from streaks order by streak desc limit 10")
    results = [dict((cur.description[i][0], value) \
        for i, value in enumerate(row)) for row in topTenStreaks]

    return results  
    
#Fetching the user details according the input user_ID
#we will connect to the respective sharded db according to the user ID
@app.get("/userstats/{user_id}")
def userstats(user_id):
    cur=get_shard_db(user_id)

    stats_fetch = cur.execute("SELECT * FROM games WHERE user_id = ? ORDER BY finished ASC", [user_id]).fetchall()

    curstr = 0
    maxstr = 0

    for row in stats_fetch:
        if (int(row[4]) == 1):
            curstr += 1
            
            if(curstr > maxstr):
                maxstr = curstr
            
        else:
            curstr = 0


    #fetching number of games won in 1st Guess
    guess1=cur.execute("SELECT COUNT(guesses) from games where user_id=? AND guesses=1",[user_id])
    guess_1=list()
    for i,row in enumerate(guess1.fetchall()):
        guess_1.append(row[i])
    guess_1=int(guess_1[0])


    #fetching number of games won in 2nd Guess
    guess2=cur.execute("SELECT COUNT(guesses) from games where user_id=? AND guesses=2",[user_id])
    guess_2=list()
    for i,row in enumerate(guess2.fetchall()):
        guess_2.append(row[i])
    guess_2=int(guess_2[0])   


    #fetching number of games won in 3rd Guess
    guess3=cur.execute("SELECT COUNT(guesses) from games where user_id=? AND guesses=3",[user_id])
    guess_3=list()
    for i,row in enumerate(guess3.fetchall()):
        guess_3.append(row[i])
    guess_3=int(guess_3[0])  


    #fetching number of games won in 4th Guess
    guess4=cur.execute("SELECT COUNT(guesses) from games where user_id=? AND guesses=4",[user_id])
    guess_4=list()
    for i,row in enumerate(guess4.fetchall()):
        guess_4.append(row[i])
    guess_4=int(guess_4[0])  

    
    #fetching number of games won in 5th Guess
    guess5=cur.execute("SELECT COUNT(guesses) from games where user_id=? AND guesses=5",[user_id])
    guess_5=list()
    for i,row in enumerate(guess5.fetchall()):
        guess_5.append(row[i])
    guess_5=int(guess_5[0])

    
    #fetching number of games won in 6th Guess
    guess6=cur.execute("SELECT COUNT(guesses) from games where user_id=? AND guesses=6",[user_id])
    guess_6=list()
    for i,row in enumerate(guess6.fetchall()):
        guess_6.append(row[i])
    guess_6=int(guess_6[0]) 


    #fetching number of games lost
    FAIL=cur.execute("SELect COUNT(*) from games where user_id=? and won='0'",[user_id])
    fail_guess=list()
    for i,row in enumerate(FAIL.fetchall()):
        fail_guess.append(row[i])
    fail_guess=int(fail_guess[0])  

    
    #number of games played
    games=cur.execute("SELECT COUNT(*) from games where user_id=?",[user_id])
    g_played=list()
    for i,row in enumerate(games.fetchall()):
        g_played.append(row[i])
    g_played=int(g_played[0])


    #number of games won
    won=cur.execute("SELECT COUNT(*) from games WHERE user_id=? and won='1'",[user_id])
    w_play=list()
    for i,row in enumerate(won.fetchall()):
        w_play.append(row[i])
    w_play=int(w_play[0])

    
    #Won Percentage
    won_percentage = ((w_play/g_played)*100) 

    
    #Calculating average guess (taking the guess which has max value)
    average_guess=[guess_1,guess_2,guess_3,guess_4,guess_5,guess_6]
    max_index = average_guess.index(max(average_guess))
    max_guess = max_index+1

 
    dict_guess=dict({
        "1":guess_1,
        "2":guess_2,
        "3":guess_3,
        "4":guess_4,
        "5":guess_5,
        "6":guess_6,
        "fail":fail_guess})

    return ([{'CurrentStreaks':curstr ,
                "maxStreak":maxstr,
                "guesses":dict_guess,
                "winPercentage": won_percentage,
                "gamesPlayed": g_played,
                "gamesWon": w_play,
                "averageGuesses": max_guess}])