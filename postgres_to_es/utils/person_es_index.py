INDEX_PERSON_NAME = "person"

INDEX_PERSON_MAPPINGS = {
    "dynamic": "strict",
    "properties": {
        "id": {
            "type": "keyword"
        },
        "full_name": {
            "type": "text",
            "analyzer": "ru_en",
            "fields": {
                "raw": {
                    "type": "keyword"
                }
            }
        },
        "roles": {
            "type": "text",
            "analyzer": "ru_en"
        },
        "date": {
            "type": "date"
        },
        "film_ids": {
            "type": "keyword",
        },
    }
}

