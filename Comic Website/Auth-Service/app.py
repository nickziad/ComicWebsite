from flask import request, Flask
import os
from models import register_user, login_user
from flask_jwt_extended import create_access_token, get_jwt_identity,jwt_required,JWTManager
from db import init_app
import requests

'''
This is the authentication service. This is the boring, but important guy. It registers and logs users in, and when a user logs in a JWT token is created.
This is essential to make users able to register their own comics under their id.

This fella also reaches out to the user service when a registration happens. This runs on a no shit protocol. If either creation of user or registration fails, 
the whole operation shutsdown.
'''
USER_BADD = "http://user-service:5004"

def initiate_app():
    app = Flask(__name__)
    app.config.from_mapping(
            SECRET_KEY="it_is_secret",
            JWT_SECRET_KEY = "Pepsi Max",
            DATABASE=os.path.join(app.instance_path, 'auth.db')
        )

    JWTManager(app)
    init_app(app)

    #only uses post because we're adding to the database. Not getting anything
    @app.route("/register", methods=["POST"])
    def register():
        
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if not username:
            return {"status": "bad", "error": 'Username is required.'} 
        elif not password:
            return {"status": "bad", "error":'password is required.'}
        elif not email:
            return {"status": "bad", "error":'email is required'}
        
        success, result = register_user(username, email, password) 
        if success:
            url = f"{USER_BADD}/Add/{username}"
            received = requests.post(url)
            if received.status_code == 201:
                return {"status": "ok"},201
        else:
            return {"status": "bad", "error": result},400

    #This doesn't add anything to the database, but post is still used because when logging in, you submit a form.
    @app.route("/login", methods=["POST"])
    def login():
        email = request.form["email"]
        password = request.form["password"]
        success, result = login_user(email,password)
        if success:
            #if successful, a jwt token is created and together with user_id it is sent in json form with status code.
            token = create_access_token(identity=str(result['id']))
            user_id = result['id']
            return {"token": token, "user_id": user_id}, 200
        else:
            #whoops! something went wrong. Don't worry, you get json format of the error and a status code
            return {"error": result}, 400

    #logs out
    @app.route('/logout')
    def logout():
        return {"status": "ok"}

    return app

if __name__ == "__main__":
    app = initiate_app()
    app.run(host="0.0.0.0", port =5003)