from dataclasses import asdict
from typing import List

from elasticsearch import Elasticsearch

from utils.decorators import backoff

from config import ELASTICSEARCH_HOST, ELASTICSEARCH_PORT
from utils.dataclasses_etl import FilmWork
from utils.film_es_index import INDEX_FILM_MAPPINGS, INDEX_FILM_NAME
from utils.genre_es_index import INDEX_GENRE_NAME, INDEX_GENRE_MAPPINGS
from utils.person_es_index import INDEX_PERSON_NAME, INDEX_PERSON_MAPPINGS

INDEX_SETTINGS = {
    "index": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "refresh_interval": "1s",
    "analysis": {
        "filter": {
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_"
            },
            "english_stemmer": {
                "type": "stemmer",
                "language": "english"
            },
            "english_possessive_stemmer": {
                "type": "stemmer",
                "language": "possessive_english"
            },
            "russian_stop": {
                "type": "stop",
                "stopwords": "_russian_"
            },
            "russian_stemmer": {
                "type": "stemmer",
                "language": "russian"
            }
        }
    }
}


class ElasticSearchConnector:
    index_map = {
        "film_work": (INDEX_FILM_NAME, INDEX_FILM_MAPPINGS),
        "genre": (INDEX_GENRE_NAME, INDEX_GENRE_MAPPINGS),
        "person": (INDEX_PERSON_NAME, INDEX_PERSON_MAPPINGS),
    }

    def __init__(self):
        self.es = self.connect()

    @backoff()
    def connect(self) -> Elasticsearch:
        return Elasticsearch(host=ELASTICSEARCH_HOST, port=ELASTICSEARCH_PORT)

    @backoff()
    def create_index(self, index: str):
        """Функция создает индекс для кинопроизведений в elasticSearch."""
        self.es.indices.create(index=self.index_map[index][0],
                               mappings=self.index_map[index][1],
                               settings=INDEX_SETTINGS,
                               ignore=400)

    @backoff()
    def bulk_update(self, docs: List[FilmWork], table: str):
        """Функция загружает пачками кинопроизведения в индекс elasticSearch."""
        index_exists = self.es.indices.exists(index=self.index_map[table][0])
        if not index_exists:
            self.create_index(table)
        if docs:
            body = []
            for doc in docs:
                body.append({'index': {'_index': self.index_map[table][0],
                                       '_id': doc.id}})
                body.append(asdict(doc))
            self.es.bulk(body=body)
