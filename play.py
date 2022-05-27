import sqlite3
from fastapi import FastAPI, status
from wordvalidation import validateWord
from answerchecking import checkAnswer
from http.client import HTTPException

app = FastAPI()

@app.get("/api/play/{word}",status_code=status.HTTP_200_OK)
async def play(word):
    recordsCount, message = await validateWord(word)
    if recordsCount >0:
        return await checkAnswer(word)
    else:
        return message