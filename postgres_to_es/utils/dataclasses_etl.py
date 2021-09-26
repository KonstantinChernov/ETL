import uuid
from dataclasses import dataclass
from datetime import datetime

from typing import List


@dataclass
class Person:
    id: uuid.UUID
    name: datetime


@dataclass
class FilmWork:
    id: uuid.UUID
    rating: float
    type: str
    title: str
    description: str
    genres: list
    directors_names: List[str]
    actors_names: List[str]
    writers_names: List[str]
    directors: List[Person]
    actors: List[Person]
    writers: List[Person]
