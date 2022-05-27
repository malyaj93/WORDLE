import fileinput
import re
import sqlite3
import datetime

def isascii(s):
    """Check if the characters in string s are in ASCII, U+0-U+7F."""
    #return len(s) == len(s.encode())
    return all(ord(c) < 128 for c in s)

def isValid(s):
    #To check if a string contains special characters
    return bool(re.match('^[a-z]*$',s))
   
def insertAnswers():
            connection = sqlite3.connect("answers.db")
            #print(connection.total_changes)

            cursor = connection.cursor()
            cursor.execute("CREATE TABLE answers (id INTEGER PRIMARY KEY, word TEXT NOT NULL, playingDate timestamp)")
            for line in fileinput.input('answers.json'):
                ansarr = (line[2:len(line)-3].split("\",\""))
            i=1
            dt = datetime.datetime.now()
            for ans in ansarr:
                if(len(ans.rstrip())==5 and isascii(ans) and isValid(ans)):
                    #print(line.rstrip())
                    cursor.execute("INSERT INTO answers VALUES (?, ?, ?)",(i,ans.rstrip(),dt.date()))
                    connection.commit()
                    i=i+1
                    dt=dt+datetime.timedelta(days=1)
            
            rows = cursor.execute("SELECT id, word, playingDate FROM answers").fetchall()
            print(rows)
            
            cursor.close()
            connection.close()


insertAnswers()