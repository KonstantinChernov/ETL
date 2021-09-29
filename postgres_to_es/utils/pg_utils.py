import psycopg2
from psycopg2.extras import DictCursor

from config import POSTGRES_DSL
from utils.decorators import backoff


class PostgresConnector:

    def __init__(self):
        self.connection = self.connect()
        self.cursor = self.connection.cursor()

    @backoff()
    def connect(self):
        return psycopg2.connect(**POSTGRES_DSL, cursor_factory=DictCursor)

    @backoff()
    def query(self, sql: str, args: tuple) -> list:
        """Функция для декорированного запроса к БД."""
        with self.connection as connection, connection.cursor() as cur:
            cur.execute(sql, args)
            rows = cur.fetchall()
        return rows
