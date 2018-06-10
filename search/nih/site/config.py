import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    QUERY_KEY = "QUERY_KEY"
    SEARCH_URL = "https://[SEARCH_SERVICE_NAME].search.windows.net"
    KEY_PHRASE_KEY = "KEY_PHRASE_KEY"
    KEY_PHRASE_URL = "https://[LOCATION].api.cognitive.microsoft.com/text/analytics/v2.0/keyPhrases"
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SECRET-KEY'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False