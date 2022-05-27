from os import stat_result
from datetime import date as date
import httpx

from datetime import date
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings, Field


app = FastAPI()

@app.get("/")
def index():
    return "in game"



# Get new game, using other API in game-state from Project 4
@app.post("/game/new")
def newGame(userId, gameId):
    user_stats = 'http://localhost:9999/api/v1/userStat/' + userId
    response = httpx.get(user_stats)
    user_id = response.json()["user_id"]
    default_date_started = date(2022, 5, 5)
    today = date.today()
    date_idx = (today - default_date_started).days
    
    newgame = 'http://localhost:9999/api/v1/startgame/' + userId + gameId
    params = {"user_id": user_id, "game_id": date_idx}
    gamestate_response = httpx.post(newgame, params=params)
    print(params)
    if (gamestate_response.status_code == 200):
        response = {"status:": "welcome"}
        response.update(params)
        return response
    elif (gamestate_response.status_code == 409):
        response = {"status:": "playing"}
        
        game_status_url = "http://localhost:9999/api/v1/restoreGame/" + str(user_id)
        t = httpx.get(game_status_url)
        response.update(params)
        response.update({"remain: " : t.json()["remaining"]})
        
        guesses = []
        if (len(t.json()) > 1):
            for i in range(1, len(t.json())):
                guesses.append(t.json()[str(i)])
        # Add to the response
        response.update({"guesses": guesses})
        selected_letters = {"correct": [], "present": []}
        if (guesses):
            new_guess = guesses[-1]
            check_answerurl = 'http://localhost:9999/api/answer-checking/answer/check/reach' + new_guess
            u = httpx.get(check_answerurl)
            for i in range(0, 5):
                score_list = u.json()["accuracy"][i]
                if (score_list == 1):
                    selected_letters["present"].append(new_guess[i])
                if (score_list == 2):
                    selected_letters["correct"].append(new_guess[i])
        #toss it on the response object
        response.update({"selected_letters": selected_letters})
        #done
        return response
    
    # return NOW only for testing
    return "passed"

# Make a guess using POST request
@app.post("/game")
def makeGuess(game_id: int, user_guess: str, user_id: str):
    word_validate_url = 'http://127.0.0.1:9999/api/v1//wordlist/checkvalid/' + user_guess
    game_state_check_url = "http://localhost:9999/api/v1/restoreGame/" + str(user_id)

    #make sure that the word is in the word dict
    #check the number of remaining user_guess
    v = httpx.get(word_validate_url)
    g = httpx.get(game_state_check_url)
    guesses = g.json()

    #Record the user_guess and update the number of guesses
    if int(guesses['remaining']) > 0 and v.json()['valid'] is 'true':
        updated_guesses = int(guesses['remaining']) - 1
        game_state_check_url = 'http://127.0.0.1:9999/api/game-state/game-state/newguess'
        params = {"user_id": user_id, "game_id": game_id, "user_guess": user_guess}
        r = httpx.post(game_state_check_url, params=params)
        res = {"remaining": updated_guesses}
        #If the user_guess is correct
        if (r.status_code == 200):
            check_answerurl = 'http://127.0.0.1:9999/api/v1/guess/' + user_guess
            u = httpx.get(check_answerurl)
            selected_letters = {"correct": [], "present": []}
            for i in range(0, 5):
                score_list = u.json()["accuracy"][i]
                if (score_list == 1):
                    selected_letters["present"].append(user_guess[i])
                if (score_list == 2):
                    selected_letters["correct"].append(user_guess[i])
            # User got all 5 selected_letters
            if len(selected_letters['correct']) == 5:
                win_url = 'http://127.0.0.1:9999/api/v1/stats/stats/' 
                guesses = 6 - updated_guesses 
                params = {"user_id": user_id, "game_id": game_id, "finished": date.today(), "guesses": guesses, "won": True} 
                s = httpx.post(win_url, params=params) 
                res.update({"status": "win", "remaining": updated_guesses}) 
                # Get their score
                scoreurl = 'http://localhost:9999/api/v1/userStat/' + user_id
                scores = httpx.get(scoreurl) 
                res.update(scores.json()) 
                return res 
            #Out of guesses
            elif len(selected_letters['correct']) < 5 and updated_guesses == 0:
                return "wrong"
            else:
                res.update({"status": "incorrect", "selected_letters": selected_letters})
                return res
    return "You are out of guesses"