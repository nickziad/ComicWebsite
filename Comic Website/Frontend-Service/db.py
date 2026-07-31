import sqlite3
from datetime import datetime

import click
from flask import current_app, g

'''
Every service has the same db.py, with a little bit of custom edits to make sure their db.py works for them. 
The catalogue-service's db.py has comments on all functions. The functions there do the same as the ones here.
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

def query(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    
    lastrow = cur.lastrowid
    cur.close()
    return lastrow

def update(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()

    rowcount = cur.rowcount
    cur.close()
    return rowcount

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
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
