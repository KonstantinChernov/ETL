import uuid
from dataclasses import dataclass
from datetime import datetime, date

from typing import List


@dataclass
class FilmWorkPerson:
    id: uuid.UUID
    name: str


@dataclass
class FilmWorkGenre:
    id: uuid.UUID
    name: str


@dataclass
class FilmWork:
    id: uuid.UUID
    rating: float
    type: str
    title: str
    description: str
    genres_names: List[str]
    directors_names: List[str]
    actors_names: List[str]
    writers_names: List[str]
    genres: List[FilmWorkGenre]
    directors: List[FilmWorkPerson]
    actors: List[FilmWorkPerson]
    writers: List[FilmWorkPerson]


@dataclass
class Genre:
    id: uuid.UUID
    name: str
    description: str


@dataclass
class Person:
    id: uuid.UUID
    full_name: str
    roles: List[str]
    birth_date: date
    film_ids: List[uuid.UUID]

