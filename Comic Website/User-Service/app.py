from flask import Flask
from flask_restx import Api
import os
import db as db_module
from profile_api import ns as users_ns

def initiate_app():
    app = Flask(__name__)
    api = Api(app)
    app.config.from_mapping(
        SECRET_KEY = "This is secret",
        DATABASE = os.path.join(app.instance_path, "users.db")
    )

    api.add_namespace(users_ns,"/")
    db_module.init_app(app)
    return app

if __name__ == "__main__": 
    app = initiate_app()
    app.run(host="0.0.0.0",port=5004)
