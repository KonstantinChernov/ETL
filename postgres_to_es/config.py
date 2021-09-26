from pydantic import BaseModel
from environ import environ
from state import JsonFileStorage

env = environ.Env()
env.read_env()


class PostgresDsnSettings(BaseModel):
    host: str
    port: int


class PostgresSettings(BaseModel):
    dsn: PostgresDsnSettings
    fetch_delay: float
    limit: int


class ElasticDsnSettings(BaseModel):
    host: str
    port: int


class ElasticSettings(BaseModel):
    dsn: ElasticDsnSettings


class Config(BaseModel):
    film_work_pg: PostgresSettings
    film_work_es: ElasticSettings
    state_file_path: str


config = Config.parse_file("config.json")

POSTGRES_DSL = {"dbname": env.str('POSTGRES_DB'),
                "user": env.str('POSTGRES_USER'),
                "password": env.str('POSTGRES_PASSWORD'),
                "host": config.film_work_pg.dsn.host,
                "port": config.film_work_pg.dsn.port}

LIMIT = config.film_work_pg.limit
FETCH_DELAY = config.film_work_pg.fetch_delay

ELASTICSEARCH_HOST = config.film_work_es.dsn.host
ELASTICSEARCH_PORT = config.film_work_es.dsn.port

STATE_FILE_PATH = config.state_file_path
STORAGE = JsonFileStorage(STATE_FILE_PATH)
