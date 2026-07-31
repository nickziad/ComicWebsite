from db import query, execute


def create_user(username):
    user = execute("""
        INSERT INTO user_profile (username) VALUES (?)
        """, [username])
    return user

def get_username(id):
    username = query("""
    SELECT username FROM users WHERE id =?
    """,[id],True)

    return username

def get_user(id):
    user = query("""
    SELECT * FROM user_profile WHERE user_id =?
    """,[id],True)

    if user:
        return True,user
    else:
        return False,"user doesn't exist"
    
def get_userID(username):

    user_row = query("SELECT id FROM users WHERE username = ?", [username],True)
    return user_row

def get_profile(id):
    profile = query("""
    SELECT bio, profile_picture, user_id 
    FROM user_profile WHERE user_id = ?
    """,[id],True)

    return profile


def delete_user(id):
    success = execute("""
                      DELETE FROM user_profile WHERE id = ?""",[id,])
    return success