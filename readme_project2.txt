# 1. To populate dictionary DB # 
################################

    # ONE TIME ACTIVITY #

    #1. Run dictionary.py from terminal (python dictionary.py)
    #2. This will insert words from /usr/share/dict/words to dictionary.db
    #3. We will be validating all input guess words against this db to check if it is a valid word


# 2. To populate answers DB # 
#############################

    # ONE TIME ACTIVITY #

    #1. Run answers.sh from terminal(sh answers.sh).
    #2. This will generate answers.json which has all the answers from nytimes wordle script
    #3. Next run answers.py from terminal, which will parse answers.json content and populate answers.db


# 3. Word validation microservice #
###################################

    #1. Word validation microservice source code is wordvalidation.py
    #2. URI for this API is /api/word/{word}
    #3. This is a GET API and guess word is passed as a path parameter
    #4. This microservice check if a guess is a valid five-letter word from the dictionary.db
    #5. It returns a status and a string message indicating if its a valid word(status 1) or not valid(status 0)

# 4. Answer checking microservice #
###################################

    #1. Answer checking microservice source code is answerchecking.py
    #2. URI for this API is /api/answer/{guess}
    #3. This is a GET API and a valid 5-letter guess word is passed as a path parameter
    #4. This microservice check if the guess word is matching with the answer of the day
    #5. If the guess matches with whole answer word it returns a string "Guessed word is correct"
    #6. If it doesn't matches it returns 3 strings indicating the letters in the correct spot, letters in the wrong spot and letters not in the word

# 5. play.py #
###############
    #1. This api calls both microservices.
    #2. API uri is /api/play/{word}
    #3. It takes guess word as path parameter
    #4. Returns message from validation 

# 6. Procfile #
###############
    #1. Command to run foreman: foreman start