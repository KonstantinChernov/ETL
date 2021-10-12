import logging
from datetime import datetime
from time import sleep

from config import STORAGE, LIMIT, FETCH_DELAY
from utils.dataclasses_etl import FilmWork, FilmWorkPerson, FilmWorkGenre, Genre, Person
from utils.decorators import coroutine
from utils.es_utils import ElasticSearchConnector
from utils.pg_utils import PostgresConnector
from state import State

state = State(STORAGE)


def produce(table: str):
    """
    Функция собирает id измененных сущностей в таблице БД, затем передает в enricher
    для дальнейшего поиска id связанных кинопроизведений, либо ищет id изменившихся
    кинопроизведений и передает в merger для сбора дополнительной информации по ним.

    :param consumer: enricher или loader
    :param table: таблица в БД в которой ведется поиск
    """
    last_crawl_time = state.get_state(f"last_{table}_crawl_time")
    if not last_crawl_time:
        last_crawl_time = datetime(1900, 1, 1, 0, 0, 0, 0)
        state.set_state(f"last_{table}_crawl_time",
                        datetime.strftime(last_crawl_time, '%Y-%m-%dT%H:%M:%S.%f'))
    else:
        last_crawl_time = datetime.strptime(last_crawl_time, '%Y-%m-%dT%H:%M:%S.%f')
    pg = PostgresConnector()
    offset = 0
    while True:
        data_chunk = pg.query(f"SELECT id, updated_at "
                              f"FROM content.{table} "
                              f"WHERE updated_at > %s "
                              f"ORDER BY updated_at OFFSET %s LIMIT %s; ", (last_crawl_time, offset, LIMIT))
        if not data_chunk:
            break
        logging.info(f"got changed data in '{table}' table")
        new_last_crawl_time = data_chunk[-1][-1]
        state.set_state(f"last_{table}_crawl_time",
                        datetime.strftime(new_last_crawl_time, '%Y-%m-%dT%H:%M:%S.%f'))

        film_loader = load('film_work')
        film_merger = merge_film(film_loader)

        if table == 'film_work':
            film_merger.send([item[0] for item in data_chunk])
        else:

            enricher = enrich(film_merger, table)
            enricher.send([item[0] for item in data_chunk])

            loader = load(table)
            if table == 'genre':
                merger = merge_genre(loader)
            elif table == 'person':
                merger = merge_person(loader)
            else:
                logging.error(f"No '{table}' table")
                return
            merger.send([item[0] for item in data_chunk])
        offset += len(data_chunk)


@coroutine
def enrich(merger, table: str):
    """
    Корутина принимает список id измененных объектов и собирает id кинопроизведений,
    которых коснулись эти изменения. Id Кинопроизведений пачками передаются в merger
    для сбора всей информации по кинопроизведениям.

    :param merger: Корутина для сбора всех данных о кинопроизведении по id
    :param table: таблица в БД из которой взяты измененные id
    """
    while True:
        ids: list = (yield)
        pg = PostgresConnector()
        offset = 0
        while True:
            data_chunk = pg.query(f"SELECT DISTINCT fw.id, updated_at "
                                  f"FROM content.film_work fw "
                                  f"LEFT JOIN content.{table}_film_work rel "
                                  f"ON rel.film_work_id = fw.id "
                                  f"WHERE rel.{table}_id IN %s "
                                  f"ORDER BY updated_at OFFSET %s LIMIT %s; ", (tuple(ids), offset, LIMIT))
            if not data_chunk:
                break
            logging.info(f"enrich data from producer")
            merger.send([item[0] for item in data_chunk])
            offset += len(data_chunk)


@coroutine
def merge_film(loader):
    """
    Корутина принимает список id кинопроизведений и собирает данные по каждому произведению из БД
    Трансформирует их в удобный формат и передает в loader для загрузки в elasticSearch.

    :param loader: Корутина для загрузки данных в elasticSearch
    """
    while True:
        pg = PostgresConnector()
        film_ids: list = (yield)
        films_from_pg = pg.query(f'''
            SELECT
                fw.id, 
                fw.rating, 
                fw.type, 
                fw.title, 
                fw.description, 
                ARRAY_AGG(DISTINCT g.name) AS genres_names,
                ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director') AS directors_names,
                ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor') AS actors_names,
                ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer') AS writers_names, 
                JSON_AGG(DISTINCT jsonb_build_object('id', g.id, 'name', g.name)) AS genres,
                JSON_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
                FILTER (WHERE pfw.role = 'director') AS directors,
                JSON_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
                FILTER (WHERE pfw.role = 'actor') AS actors,
                JSON_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) 
                FILTER (WHERE pfw.role = 'writer') AS writers
            FROM content.film_work fw
            LEFT OUTER JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT OUTER JOIN content.person p ON p.id = pfw.person_id
            LEFT OUTER JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT OUTER JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN %s
            GROUP BY fw.id, fw.title, fw.description, fw.rating;
            ''', (tuple(film_ids),))
        films_to_update_in_es = [FilmWork(
            id=film[0],
            rating=film[1],
            type=film[2],
            title=film[3],
            description=film[4],
            genres_names=film[5],
            directors_names=film[6],
            actors_names=film[7],
            writers_names=film[8],
            genres=[FilmWorkGenre(**person) for person in film[9]] if film[9] else [],
            directors=[FilmWorkPerson(**person) for person in film[10]] if film[10] else [],
            actors=[FilmWorkPerson(**person) for person in film[11]] if film[11] else [],
            writers=[FilmWorkPerson(**person) for person in film[12]] if film[12] else [])
            for film in films_from_pg]

        loader.send(films_to_update_in_es)
        logging.info(f"merge data")


@coroutine
def merge_genre(loader):
    """
    Корутина принимает список id жанров, собирает данные по каждому жанру из БД
    Трансформирует их в удобный формат и передает в loader для загрузки в elasticSearch.

    :param loader: Корутина для загрузки данных в elasticSearch
    """
    while True:
        pg = PostgresConnector()
        genres_ids: list = (yield)
        genres_from_pg = pg.query(f'''
            SELECT DISTINCT id, name, description
            FROM content.genre g
            WHERE g.id IN %s
            ''', (tuple(genres_ids),))
        genres_to_update_in_es = [Genre(
            id=genre[0],
            name=genre[1],
            description=genre[2])
            for genre in genres_from_pg]

        loader.send(genres_to_update_in_es)
        logging.info(f"merge data")


@coroutine
def merge_person(loader):
    """
    Корутина принимает список id персоналий, собирает данные по каждой персоналии из БД
    Трансформирует их в удобный формат и передает в loader для загрузки в elasticSearch.

    :param loader: Корутина для загрузки данных в elasticSearch
    """
    while True:
        pg = PostgresConnector()
        person_ids: list = (yield)
        person_from_pg = pg.query(f'''
            SELECT DISTINCT
            p.id, 
            p.full_name, 
            ARRAY_AGG(DISTINCT pfw.role) AS roles,
            p.birth_date, 
            ARRAY_AGG(DISTINCT pfw.film_work_id::text) AS film_ids
            FROM content.person p
            LEFT OUTER JOIN content.person_film_work pfw ON p.id = pfw.person_id
            WHERE p.id IN %s
            GROUP BY p.id;
            ''', (tuple(person_ids),))
        person_to_update_in_es = [Person(
            id=person[0],
            full_name=person[1],
            roles=person[2],
            birth_date=person[3],
            film_ids=person[4])
            for person in person_from_pg]

        loader.send(person_to_update_in_es)
        logging.info(f"merge data")


@coroutine
def load(table: str):
    """Корутина принимает порции данных с кинопроизведениями и сохраняет в elasticSearch."""
    while True:
        objects: list = (yield)
        es = ElasticSearchConnector()
        es.bulk_update(objects, table)
        logging.info(f"load data to elasticSearch")


def start():
    tables = ['film_work', 'genre', 'person']
    while True:
        for table in tables:
            produce(table)
            sleep(FETCH_DELAY)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    start()
