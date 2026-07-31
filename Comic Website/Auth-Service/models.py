from db import execute,query
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

#It tries to register user. It returns a tuple (boolean, result). The boolean is used to know whether there was success or not.
def register_user(username, email, password):

    try:
        execute("INSERT INTO users (username, email, password_hash) VALUES (?,?,?)",
                (username, email, generate_password_hash(password)),
                )
        return True, None
    except sqlite3.IntegrityError:
        return False, 'User already registered'

#checks if the user exists. It returns a tuple (boolean, result). The boolean is used to know whether there was success or not.
def login_user(email, password):

    user = query(
            'SELECT * FROM users WHERE email = ?', (email,),True
        )

    if user is None:
        return False,'Incorrect email.'
 
    elif not check_password_hash(user['password_hash'], password):
        return False,'Invalid password'
    
    return True, user
