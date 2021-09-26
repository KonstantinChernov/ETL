FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY ./requirements ./requirements
COPY entrypoint.sh .
RUN pip install --upgrade pip && pip install -r requirements/dev.txt --no-cache-dir && chmod ugo+x entrypoint.sh

COPY . /code

ENTRYPOINT ["sh", "/code/entrypoint.sh"]