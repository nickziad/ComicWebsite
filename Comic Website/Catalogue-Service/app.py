from flask import Flask
from flask_restx import Api
from apis.comic_api import ns as comic_ns
from apis.issues_api import ns as issue_ns
import os
import db as db_module

'''
This is the catalogue service. Its job is to take care of everything cataloguing. Whenever another service needs comic related, this is the guy. 
Need all comics for some page? This is your guy.
Wanna upload some comics or issues? If you ask properly, this is your guy. 

It has 2 API's. One for literal comic related stuff, like adding comics or series. The other is for Issues of comics.
Could put it in one, but looks nicer and less clamped.
'''
def initiate_app():
    app = Flask(__name__)
    api = Api(app)
    app.config.from_mapping(
        SECRET_KEY="it_is_secret",
        DATABASE=os.path.join(app.instance_path, 'catalogue.db'),
    )
    
    api.add_namespace(comic_ns,"/Comic")
    api.add_namespace(issue_ns,"/Issue")
    print(app.url_map)
    db_module.init_app(app)
    return app

if __name__ == "__main__":
    app = initiate_app()
    app.run(host="0.0.0.0", port =5002)

def get_comics(publisher=None):
    
    if publisher:
        comics = query("""
                    SELECT s.title, s.front_page, publisher_name, s.id
                    FROM comic_series AS s
                    INNER JOIN publishers AS p ON s.publisher_id = p.id WHERE p.publisher_name = ? """, [publisher])
    else:
        comics = query("""
                    SELECT s.title, s.front_page, publisher_name, s.id
                    FROM comic_series AS s
                    INNER JOIN publishers AS p ON s.publisher_id = p.id""")
    return comics