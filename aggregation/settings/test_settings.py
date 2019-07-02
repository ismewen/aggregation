from .settings import *

TESTING = True
LIVESERVER_PORT = 8943
LIVESERVER_TIMEOUT = 10
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI',
                                    'mysql+pymysql://root:ismewen@localhost/test_clouster_admin>')
