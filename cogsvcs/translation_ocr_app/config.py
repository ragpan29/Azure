import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    db_name = os.environ.get("DB_NAME")

    if db_name is None:
        sqlAlchCON = None
    else:
        sqlAlchCON = "mssql+pyodbc://{usr}@{server_name}:{pw}@{server_name}.database.windows.net:1433/{db_name}?driver=ODBC+Driver+13+for+SQL+Server".format(
            server_name = server_name,
            db_name = db_name,
            usr = usr,
            pw = pw
        )
    
    COGS_KEY = os.environ.get('COGS_KEY')
    LANGUAGE_URL = os.environ.get('LANGUAGE_URL')

    VISION_KEY = os.environ.get("VISION_KEY")
    VISION_URL = os.environ.get("VISION_URL")

    BLOB_ACCT_NAME = os.environ.get("BLOB_ACCT_NAME")
    BLOB_KEY = os.environ.get("BLOB_KEY")
    BLOB_URL = os.environ.get("BLOB_URL")
    
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'uploads')

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SECRET-KEY'
    SQLALCHEMY_DATABASE_URI = sqlAlchCON or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False