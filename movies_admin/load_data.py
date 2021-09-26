import csv
import os
import sqlite3
from environ import environ

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor


env = environ.Env()
env.read_env()

all_tables = ['film_work', 'genre', 'person', 'genre_film_work', 'person_film_work']


class SQLiteLoader:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def get_data_from_table(self, table: str):
        self.cursor.execute(f"SELECT * FROM {table}")
        for _ in self.cursor.fetchall():
            yield _

    def write_table_to_csv_file(self, table: str):
        if not os.path.isdir("tables"):
            os.mkdir("tables")
        with open(os.path.join("tables", f"{table}.csv"), 'w') as f:
            for entry in self.get_data_from_table(table):
                writer = csv.writer(f, delimiter=",", lineterminator="\r")
                writer.writerow(entry)

    def load_movies(self):
        for table in all_tables:
            self.write_table_to_csv_file(table)


class PostgresSaver:
    def __init__(self, connection: _connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def save_all_data(self):
        self.cursor.execute("""TRUNCATE content.genre_film_work,
                                        content.person_film_work,
                                        content.genre,
                                        content.person,
                                        content.film_work""")
        for table in all_tables:
            with open(os.path.join("tables", f"{table}.csv")) as f:
                copy = f"COPY content.{table} FROM STDIN with csv"
                self.cursor.copy_expert(sql=copy, file=f)


def load_from_sqlite(connection: sqlite3.Connection, pg_connection: _connection):
    """ Основной метод загрузки данных из SQLite в Postgres. """
    postgres_saver = PostgresSaver(pg_connection)
    sqlite_loader = SQLiteLoader(connection)

    sqlite_loader.load_movies()
    postgres_saver.save_all_data()


if __name__ == "__main__":
    dsl = {"dbname": os.environ.get('POSTGRES_DB'),
           "user": os.environ.get('POSTGRES_USER'),
           "password": os.environ.get('POSTGRES_PASSWORD'),
           "host": os.environ.get('POSTGRES_HOST', '127.0.0.1'),
           "port": os.environ.get('POSTGRES_PORT', 5432)}
    with sqlite3.connect("db.sqlite") as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
