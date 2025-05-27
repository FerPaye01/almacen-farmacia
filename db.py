# db.py
from flask_mysqldb import MySQL

def init_mysql(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'aea_farmacia'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    return MySQL(app)
