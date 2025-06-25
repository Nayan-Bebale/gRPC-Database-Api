from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .userdata import UserData
from .modeldata import ModelData
from .serverdata import ServerData