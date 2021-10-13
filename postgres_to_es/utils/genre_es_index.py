INDEX_GENRE_NAME = "genre"

INDEX_GENRE_MAPPINGS = {
    "dynamic": "strict",
    "properties": {
        "id": {
            "type": "keyword"
        },
        "name": {
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
    }
}

