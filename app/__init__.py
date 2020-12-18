from flask import Flask
from app.database.DatabaseRobot import DatabaseRobot

app = Flask(__name__)
database_test_robot = DatabaseRobot(DatabaseRobot.endpoint_test, DatabaseRobot.database_robot)

from app import views