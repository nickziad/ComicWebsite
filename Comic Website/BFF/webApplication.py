import requests
from flask import request
from flask_restx import Resource, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity

'''
This is the web application api in BFF service. The API has multiple routes, depending on what the frontend needs.
It consists of global variables in the beginning, which are the base urls of the other services. Since this is BFF, it needs to know.
'''

CATALOGUE_BADD = "http://catalogue-service:5002" #<- change to docker service
AUTH_BADD = "http://auth-service:5003" #<- change to docker service
USER_BADD = "http://user-service:5004" # <- change to docker service

ns = Namespace("bff","Gets a comic")

#url is: http://127.0.0.1:5001/bff/Comic/id
@ns.route("/Comic/<int:id>")
class Comic(Resource):
    def get(self,id):
        url = f"{CATALOGUE_BADD}/Comic/{id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return 400
#url is: http://127.0.0.1:5001/bff/Issue/id
@ns.route("/Issue/<int:id>")
class Issue(Resource):
    def get(self,id):
        url = f"{CATALOGUE_BADD}/Issue/{id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error:" "Couldn't fetch it"}, 400

#url is: http://127.0.0.1:5001/bff/Upload/issue
'''
We need owner_id to know who uploaded the issue/comic. the jwt token comes from when somebody logs in through auth-service.
New data is then made with the exact same data, but owner_id is added and the token is acquired through get_jwt_identity.
The same logic goes with Upload/Comic. owner_id could be sent by the frontend, but everybody be saying don't trust the frontend so here we are.
'''
@ns.route("/Upload/issue")
class UploadIssue(Resource):
    @jwt_required()
    def post(self):
        url = f"{CATALOGUE_BADD}/Issue"
        data = {
            "series_id": request.form['series_id'],
            "owner_id": get_jwt_identity()
        }
        file = request.files["issue"]
        files = {'issue': (file.filename, file.stream, file.mimetype)}

        response = requests.post(url, data=data, files=files)
        if response.status_code == 201:
            return response.json(), response.status_code
        else:
            return {"error code from post:": response.status_code}, 400

#url is: http://127.0.0.1:5001/bff/Upload/comic
@ns.route("/Upload/comic")
class UploadComic(Resource):
    @jwt_required()
    def post(self):
        url = f"{CATALOGUE_BADD}/Comic"
        data = {
            "title": request.form['title'],
            "publisher": request.form['publisher'],
            "category": request.form["category"],
            "is_active": request.form["is_active"],
            "owner_id": get_jwt_identity()
        }
        file = request.files["front_page"]
        files = {'front_page': (file.filename, file.stream, file.mimetype)}

        response = requests.post(url, data=data,files = files)
        if response.status_code == 201:
           return response.json(), 200
        else:
            return response.json(), 400
        
#url is: http://127.0.0.1:5001/bff/login
@ns.route("/login")
class login(Resource):
    def post(self):
        url = f'{AUTH_BADD}/login'
        response = requests.post(url, data=request.form)
        if response.status_code == 200:
            return response.json(), 200
        else:
            return 400
        
#url is: http://127.0.0.1:5001/bff/register
@ns.route("/register")
class register(Resource):
    def post(self):
        url = f'{AUTH_BADD}/register'
        response = requests.post(url, data=request.form)
        if response.status_code == 201:
            return response.json(), 201
        else:
            return {}, 400

#url is: http://127.0.0.1:5001/bff/Comics
@ns.route("/Comics")
class Comics(Resource):
    def get(self):
        url = f"{CATALOGUE_BADD}/Comic"
        response = requests.get(url,params={"publisher": request.args.get("publisher")})
        if response.status_code == 200:
            return response.json(), response.status_code
        else:
            return response.status_code,500
        
@ns.route("/profile/<int:id>")
class Profile(Resource):
    def get(self, id):
        url = f"{USER_BADD}/{id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json(), response.status_code
        else:
            return response.status_code,400
        
@ns.route("/profile/comics/<int:id>")
class UserComics(Resource):
    def get(self, id):
        url = f"{CATALOGUE_BADD}/Comic/user/comics/{id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json(), 200
        else:
            return response.status_code, 400
        
@ns.route("/Issue/read/<int:series_id>/<int:issue_number>/<int:page>")
class displayPage(Resource):
    def get(self,series_id, issue_number, page):
        url = f"{CATALOGUE_BADD}/Issue/{series_id}/{issue_number}/{page}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json(), 200
        else:
            return {}, 400