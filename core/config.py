import os
from dotenv import load_dotenv
from pathlib import Path

class Settings:
    PROJECT_NAME: str = "demo_fastapi"
    PROJECT_VERSION: str = "1.0.0"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    ROOT_DIR = BASE_DIR[:BASE_DIR.find(PROJECT_NAME)+len(PROJECT_NAME)]

    env_path = Path(ROOT_DIR,'.env')
    load_dotenv(dotenv_path=env_path, encoding='utf-8')

    SQL_USER: str = os.getenv("SQL_USER")
    SQL_PASSWORD: str = os.getenv("SQL_PASSWORD")
    SQL_SERVER: str = os.getenv("SQL_SERVER")
    SQL_PORT: str = os.getenv("SQL_PORT")
    SQL_DB: str = os.getenv("SQL_DB")
    SQL_DATABASE_URL = "mysql://{0}:{1}@{2}:{3}/{4}?charset=utf8".format(SQL_USER, SQL_PASSWORD, SQL_SERVER, SQL_PORT, SQL_DB)

    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: str = os.getenv("REDIS_PORT")
    REDIS_URI: str = "redis://{0}:{1}/0".format(REDIS_HOST, REDIS_PORT)  # redis

    SECRET_KEY: str = os.getenv("SECRET_KEY")  # new
    ALGORITHM = "HS256"  # new
    ACCESS_TOKEN_EXPIRE_MINUTES = 60  # in mins  #new
    GLOBAL_ENCODING: str = 'utf-8'  # 全局编码


settings = Settings()

