import redis
import sqlite3
def Shard1_Topten():
    con = sqlite3.connect('shard_1.db')
    cur = con.execute("SELECT user_id,streak FROM streaks ORDER BY streak DESC LIMIT 10")
    tuples = cur.fetchall()
    dictionary = {}
    print(tuples)
    for i in tuples:
        dictionary[i[0]]= i[1]
    return dictionary

def Shard2_Topten():
    con = sqlite3.connect('shard_2.db')
    cur = con.execute("SELECT user_id,streak FROM streaks ORDER BY streak DESC LIMIT 10")
    tuples = cur.fetchall()
    dictionary = {}
    print(tuples)
    for i in tuples:
        dictionary[i[0]]= i[1]
    return dictionary

def Shard3_Topten():
    con = sqlite3.connect('shard_3.db')
    cur = con.execute("SELECT user_id,streak FROM streaks ORDER BY streak DESC LIMIT 10")
    tuples = cur.fetchall()
    dictionary = {}
    print(tuples)
    for i in tuples:
        dictionary[i[0]]= i[1]
    return dictionary