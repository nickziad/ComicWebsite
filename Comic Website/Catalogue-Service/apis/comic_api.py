from flask import request
from flask_restx import Resource, Api, Namespace

from models import get_comic, delete_comic, insert_series,get_comics, get_user_added_comics

ns = Namespace("Comic","Gets a comic")

#url is: http://127.0.0.1:5002/Comic
@ns.route("")
class Comics(Resource):
    def get(self):
        publisher = request.args.get("publisher")
        comics = get_comics(publisher)
    
        if not comics:
            return {},200
        
        #we're getting ALL comics, and since what is fetched is rows from a database, it must be converted to a dictionary to fit json format.
        comics_json = [dict(row) for row in comics]

        return comics_json, 200

    def post(self):
        title = request.form['title']
        front_page = request.files['front_page']
        is_active = request.form['is_active']
        publisher = request.form['publisher']
        category = request.form['category']
        owner_id = request.form['owner_id']
        
        print(front_page.filename)
        succes,result = insert_series(title, front_page, is_active, publisher, category, owner_id)
        if succes:
            return {"status": "ok", "result": result}, 201
        else:
            return {"status": "bad", "result": result}, 400

#url is: http://127.0.0.1:5002/Comic/id
@ns.route('/<int:id>')
class Comic(Resource):
    def get(self, id): 
        comic = get_comic(id)
        return dict(comic), 200
    
    def delete(self, id):
        deleted = delete_comic(id)
        
        return deleted, 200

@ns.route('/user/comics/<int:id>')
class UserComics(Resource):
    def get(self, id):
        print("Im here")
        comics = get_user_added_comics(id)
        if not comics:
            return [],200
        
        comics_json = [dict(row) for row in comics]
        
        return comics_json,200
    

