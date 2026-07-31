from flask_restx import Namespace, Resource
from models import *

ns = Namespace("Profile","Profile of the user")

@ns.route("/Add/<string:username>/")
class AddUser(Resource):
    def post(self,username):
        user_id = create_user(username)
        if user_id:
            print("Im here")
            return {"Id": user_id}, 201
        else:
            return {}, 400

@ns.route("/<int:id>")
class User(Resource):
    def get(self, id):
        success,result = get_user(id)
        if success:
            return dict(result), 200
        else:
            return result, 400