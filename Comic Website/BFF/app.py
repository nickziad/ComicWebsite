from flask import Flask
from flask_restx import Api
from webApplication import ns as webApplication
from flask_jwt_extended import JWTManager

'''
This is the BFF's app. This is where the service gets initiated and for scaling, there is potential of making other api's that work with mobile phones etc.
This is essentially the reason for choosing BFF. Plus because it makes more sense that Frontend and backend don't communicate directly. 
'''

def initiate_app():
    app = Flask(__name__)
    api = Api(app)
    app.config.from_mapping(
        SECRET_KEY="it_is_secret",
        JWT_SECRET_KEY = "Pepsi Max", #<- very secret key!
        JWT_TOKEN_LOCATION = ["headers"]
    )

    api.add_namespace(webApplication,"/")
    JWTManager(app)
    return app

if __name__ == "__main__":
    app = initiate_app()
    app.run(host="0.0.0.0", port =5001)
