INDEX_FILM_NAME = "film"

INDEX_FILM_MAPPINGS = {
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
        "genres_names": {
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
        "genres": {
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
