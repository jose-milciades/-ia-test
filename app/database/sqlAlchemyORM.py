from flask_sqlalchemy import SQLAlchemy
from app import app
import os

#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:securep@sshere@192.168.0.11:5432/testingRobotLectura"
_port = os.environ.get("PORT_POSTGRESQL")
_password = os.environ.get("PASSWORD_POSTGRESQL")
_user_db = os.environ.get("USER_POSTGRESQL")
_type_db = os.environ.get("TYPE_DB")
_endpoint = os.environ.get("ENDPOINT_TESTING_ROBOT_LECTURA")
_database = os.environ.get("DATABASE_TESTING")

app.config["SQLALCHEMY_DATABASE_URI"] = f'{_type_db}://{_user_db}:{_password}@{_endpoint}:{_port}/{_database}'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

def close_session(db):
    db.session.close()
    db.dispose()