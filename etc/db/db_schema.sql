-- Создание отдельной схемы для контента:

CREATE SCHEMA IF NOT EXISTS content;

-- Установка расширения для генерации UUID:

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Кинопроизведения:

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    creation_date DATE,
    certificate TEXT,
    file_path TEXT,
    rating FLOAT,
    type VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Жанры кинопроизведений:

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Связь жанров и кинопроизведений:

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
    film_work_id uuid REFERENCES content.film_work(id),
    genre_id uuid REFERENCES content.genre(id),
    created_at TIMESTAMP WITH TIME ZONE
);

-- Участники кинопроизводства:

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
    full_name VARCHAR(255) NOT NULL,
    birth_date DATE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Связь участников и кинопроизведений:

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
    film_work_id uuid REFERENCES content.film_work(id),
    person_id uuid REFERENCES content.person(id),
    role TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE
);

-- Создание индексов:

CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre ON content.genre_film_work (film_work_id, genre_id);
CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_role ON content.person_film_work (film_work_id, person_id, role);

