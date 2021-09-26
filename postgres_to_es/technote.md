## Как запустить проект:

После клонирования проекта локально необходимо запустить команду:
```
docker-compose up
```

Для наполнения БД тестовыми данными выполните команду:
```
docker-compose exec movies-admin-web python3 load_data.py
```

Для проведения оставшейся миграции для приложения movies необходимо выполнить команду:
```
docker-compose exec movies-admin-web python3 manage.py migrate movies --fake
```