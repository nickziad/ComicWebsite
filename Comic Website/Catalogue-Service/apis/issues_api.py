from flask import request

from flask_restx import Resource, Api, Namespace

from models import insert_issue, get_issue, get_comic
from pathlib import Path
import os
ITEM_FOLDER = os.environ.get("ITEM_FOLDER", "/items")

ns = Namespace("Issue","Gets a comic")

@ns.route("/<int:id>")
class Issue(Resource):
    def get(self,id):
        issue = get_issue(id)
        #since issue is gonna be a row from the database, we convert it to a dict so it fits json format. This also happens when getting comics.
        return dict(issue), 200

@ns.route("/<int:series_id>/<int:issue_number>/<int:page>")
class getIssuePage(Resource):
    def get(self,series_id,issue_number, page):
        comic = get_comic(series_id)

        path_to_series = comic['path_to_series']
        print(path_to_series)
        base_path = ITEM_FOLDER
        
        path_to_issue = Path(base_path) /path_to_series / "Issues" / str(issue_number)
        print(page)
        file_count = len(list(path_to_issue.glob('*.jpg')))
        print(file_count)

        img_path = f"{path_to_series}/Issues/{str(issue_number)}/page{str(page)}.jpg"
        data = {
            "series_id": series_id,
            "issue_number": issue_number,
            "page": page,
            "img_path": img_path,
            "issues_count": file_count
        }
        return data, 200

@ns.route("")
class Issues(Resource):  
    def post(self):
        series_id = request.form['series_id']
        issue_file = request.files['issue']
        owner_id = request.form['owner_id']
        succes,result = insert_issue(series_id, issue_file,owner_id)
        if succes:
            return {"status": "ok", "result": result}, 201
        else:
            return {"status": "bad", "result": result}, 400
        
