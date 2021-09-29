from dataclasses import asdict
from typing import List

from elasticsearch import Elasticsearch

from utils.decorators import backoff

from config import ELASTICSEARCH_HOST, ELASTICSEARCH_PORT
from utils.dataclasses_etl import FilmWork

INDEX_NAME = "film_work"

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
INDEX_MAPPINGS = {
    "dynamic": "strict",
    "properties": {
        "id": {
            "type": "keyword"
        },
        "rating": {
            "type": "float"
        },
        "type": {
            "type": "keyword"
        },
        "title": {
            "type": "text",
            "analyzer": "ru_en",
            "fields": {
                "raw": {
                    "type": "keyword"
                }
            }
        },
        "description": {
            "type": "text",
            "analyzer": "ru_en"
        },
        "genres": {
            "type": "text",
            "analyzer": "ru_en"
        },
        "directors_names": {
            "type": "text",
            "analyzer": "ru_en"
        },
        "actors_names": {
            "type": "text",
            "analyzer": "ru_en"
        },
        "writers_names": {
            "type": "text",
            "analyzer": "ru_en"
        },
        "directors": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "id": {
                    "type": "keyword"
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en"
                }
            }
        },
        "actors": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "id": {
                    "type": "keyword"
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en"
                }
            }
        },
        "writers": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "id": {
                    "type": "keyword"
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en"
                }
            }
        }
    }
}


class ElasticSearchConnector:
    def __init__(self):
        self.es = self.connect()

    @backoff()
    def connect(self) -> Elasticsearch:
        return Elasticsearch(host=ELASTICSEARCH_HOST, port=ELASTICSEARCH_PORT)

    @backoff()
    def create_index(self):
        """Функция создает индекс для кинопроизведений в elasticSearch."""
        self.es.indices.create(index=INDEX_NAME, settings=INDEX_SETTINGS, mappings=INDEX_MAPPINGS, ignore=400)

    @backoff()
    def bulk_update(self, docs: List[FilmWork]):
        """Функция загружает пачками кинопроизведения в индекс elasticSearch."""
        index_exists = self.es.indices.exists(index=INDEX_NAME)
        if not index_exists:
            self.create_index()
        if docs:
            body = []
            for doc in docs:
                body.append({'index': {'_index': INDEX_NAME,
                                       '_id': doc.id}})
                body.append(asdict(doc))
            self.es.bulk(body=body)
