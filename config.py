import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

DEFAULT_SECRET_KEY = "e645e0943762193135c7566e173e647ec70686d8e1b6bd4a581195bc4e57a6ff"
DEFAULT_MYSQL_ROOT_PASSWORD = ""

class Config():
    SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)

class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD", DEFAULT_MYSQL_ROOT_PASSWORD)
    SQLALCHEMY_DATABASE_URI = f"mysql://root:{quote(MYSQL_ROOT_PASSWORD)}@localhost/tournament_db"

class ProductionConfig(Config):
    DEBUG = False
    
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}