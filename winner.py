import sqlite3
import uuid
import redis
from pydantic import BaseSettings

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)

sharddb1 = sqlite3.connect('shard_1.db', detect_types=sqlite3.PARSE_DECLTYPES)
sharddb2 = sqlite3.connect('shard_2.db', detect_types=sqlite3.PARSE_DECLTYPES)
sharddb3 = sqlite3.connect('shard_3.db', detect_types=sqlite3.PARSE_DECLTYPES)
user = sqlite3.connect('userShard.db', detect_types=sqlite3.PARSE_DECLTYPES)

r = redis.Redis()

Winner_shard1 = sharddb1.execute("SELECT * FROM wins ORDER BY wins DESC LIMIT 10").fetchall()
Winner_shard2 = sharddb2.execute("SELECT * FROM wins ORDER BY wins DESC LIMIT 10").fetchall()
Winner_shard3 = sharddb3.execute("SELECT * FROM wins ORDER BY wins DESC LIMIT 10").fetchall()

Wins_user = Winner_shard1
Wins_user.extend(Winner_shard2)
Wins_user.extend(Winner_shard3)

topscores = {}

for winner in Wins_user:
    selectUser = user.execute("SELECT username FROM users WHERE user_id = :user_id", [winner[0]])
    user_values = selectUser.fetchall()
    topscores[user_values[0][0]] = int(winner[1])



Streak_shard1 = sharddb1.execute("SELECT * FROM streaks ORDER BY streak DESC LIMIT 10").fetchall()
Streak_shard2 = sharddb2.execute("SELECT * FROM streaks ORDER BY streak DESC LIMIT 10").fetchall()
Streak_shard3 = sharddb3.execute("SELECT * FROM streaks ORDER BY streak DESC LIMIT 10").fetchall()

topStreaks = Streak_shard1
topStreaks.extend(Streak_shard2)
topStreaks.extend(Streak_shard3)

streakscore = {}

for streak in topStreaks:
    selectUser = user.execute("SELECT username FROM users WHERE user_id = :user_id", [streak[0]])
    user_values = selectUser.fetchall()
    streakscore[user_values[0][0]] = int(streak[1])


r.zadd("Top Scores", topscores)
r.zadd("Top Streaks", streakscore)

