import sqlite3
from datetime import datetime

import click
from flask import current_app, g

'''
Every service has the same db.py, with a little bit of custom edits to make sure their db.py works for them. 
This is the db.py that has comments on all functions. The functions here do the same as the other ones.
'''
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
'''
3 custom query types were made. Relieves models.py functions from having to get_db etc. Now they just call query, execute, update depending on their needs
'''

#numbero uno. query. It's for basic stuff like select. Doesn't edit database. The last parameter is to tell if it needs to fetch 1 or all. Default False.
#Returns 1 or all rows.
def query(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

#numbero dos. execute. This doesn't execute like the cartels, but it does edit the database through db.execute. Return the lastrow that it edited. Used for insert
def execute(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    
    lastrow = cur.lastrowid
    cur.close()
    return lastrow

#numbero tres <- I think?. update. This is actually nearly exactly the same as execute, but it returns rowcount.
#I couldn't for the life of me, make this work in execute where it would return rowcount, hence why a new one was made.
def update(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()

    rowcount = cur.rowcount
    cur.close()
    return rowcount

#init_db. Specifically for catalogue.sql
def init_db():
    db = get_db()

    with current_app.open_resource('catalogue.sql') as f:
        db.executescript(f.read().decode('utf8'))

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)