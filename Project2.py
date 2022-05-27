from fastapi import FastAPI, HTTPException, status
import sqlite3
import json
import random


# Will try to do this later in a .sql script
# How to insert json into sql db without python?
def create_db():
    connect = sqlite3.connect("./var/wordle.db")
    cur = connect.cursor()
    cur.execute("PRAGMA foreign_keys=ON;")
    cur.execute("BEGIN TRANSACTION;")
    cur.execute("DROP TABLE IF EXISTS Words;")
    # cur.execute("CREATE TABLE IF NOT EXISTS Words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT);")
    cur.execute("CREATE TABLE IF NOT EXISTS Words (word TEXT);")
    words = json.load(open('answers.json'))

    for word in words:
        cur.execute("INSERT INTO Words(word) VALUES(?)", (word,))

    return cur

app = FastAPI()
cursor = create_db()

@app.get("/")
async def root():
    return {"message": "Wordle Online"}


# @app.get("/wordlist")
# async def root():
#     cursor.execute("SELECT * FROM Words")
#     result = cursor.fetchall()
#     print(len(result))
#     return [{'id':row[0], 'word':row[1]} for row in result]

# Check if a guess is a 5-letter word
@app.get("/wordlist/checkvalid/{word}")
async def checkvalid(word):
    return (word.isalpha() and len(word) == 5) 

# Add possible guesses
@app.get("/wordlist/addword/{word}", status_code=status.HTTP_201_CREATED)
async def read_item(word):
    cursor.execute("SELECT * FROM Words")
    result = cursor.fetchall()
    # row = [row for row in result if row[0] == word]

    # if row != None: 
    if word in result:
        raise HTTPException(status_code=404, detail="Word already exists!") 
    cursor.execute("INSERT INTO Words VALUES(?)", (word,))
    return {"word added": word}
    
# Remove possible guesses
@app.get("/wordlist/removeword/{word}")
async def read_item(word):
    cursor.execute("SELECT * FROM Words")
    result = cursor.fetchall()
    # row = [row for row in result if row[1] == word]

    # if row != None: 
    if word in result:
        cursor.execute("DELETE FROM Words WHERE word=?", (word,))
        return {"word removed": word}
    raise HTTPException(status_code=404, detail="Word not exist!") 
    

    

@app.get("/guess/{word}")
async def guess(word):
    
    '''TODO: how to check answer without storing at server'''

    cursor.execute("SELECT * FROM Words")
    result = cursor.fetchall()
    word_list = list(res[0] for res in result)
    answer = word_list[0]

    guess = word
    result = {}
    for a, g in zip(answer, guess):
        if(a == g) : result[g] = "green"
        elif(g in answer) : result[g] = "yellow"
        else : result[g] = "gray"
        print (a, g, result[g])
    return {"guess_result": result}

