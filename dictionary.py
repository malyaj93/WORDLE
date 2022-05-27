import fileinput
import re
import sqlite3


def isascii(s):
    """Check if the characters in string s are in ASCII, U+0-U+7F."""
    #return len(s) == len(s.encode())
    return all(ord(c) < 128 for c in s)

def isValid(s):
    #To check if a string contains special characters
    return bool(re.match('^[a-z]*$',s))
   
def insertWords():
            connection = sqlite3.connect("dictionary.db")
            #print(connection.total_changes)

            cursor = connection.cursor()
            cursor.execute("CREATE TABLE words (w_id INTEGER, word TEXT, meaning TEXT)")
            i=1
            for line in fileinput.input('/usr/share/dict/words'):
                if(len(line.rstrip())==5 and isascii(line) and isValid(line)):
                    #print(line.rstrip())
                    cursor.execute("INSERT INTO words VALUES (?, ?, '')",(i,line.rstrip()))
                    connection.commit()
                    i=i+1
            
            rows = cursor.execute("SELECT word FROM words").fetchall()
            print(rows)
            
            cursor.close()
            connection.close()


insertWords()
