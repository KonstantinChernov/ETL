import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(TimeStampedMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)

    class Meta:
        verbose_name = _("genre")
        verbose_name_plural = _("genres")
        db_table = 'content"."genre'

    def __str__(self):
        return self.name


class FilmWorkGenre(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey("FilmWork", on_delete=models.CASCADE)
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        unique_together = ("film_work", "genre")
        indexes = [
            models.Index(fields=("film_work", "genre")),
        ]

    def __str__(self):
        return f"{self.film_work.title} - {self.genre.name}"


class Person(TimeStampedMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(_("full name"), max_length=255)
    birth_date = models.DateField(_("birth date"), blank=True, null=True)

    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("persons")
        db_table = 'content"."person'

    def __str__(self):
        return f"{self.full_name}"


class FilmWorkPerson(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey("FilmWork", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    role = models.CharField(_("role"), max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        unique_together = ("film_work", "person", "role")
        indexes = [
            models.Index(fields=("film_work", "person", "role")),
        ]

    def __str__(self):
        return f"{self.film_work.title} - {self.person.full_name} - {self.role}"


class FilmWorkType(models.TextChoices):
    MOVIE = "movie", _("movie")
    TV_SHOW = "tv_show", _("TV Show")


class FilmWork(TimeStampedMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)
    creation_date = models.DateField(_("creation date"), blank=True, null=True)
    certificate = models.TextField(_("certificate"), blank=True, null=True)
    file_path = models.FileField(_("file"), upload_to="film_works/", blank=True, null=True)
    rating = models.FloatField(_("rating"), validators=[MinValueValidator(0)], blank=True, null=True)
    type = models.CharField(_("type"), max_length=20, choices=FilmWorkType.choices)
    genres = models.ManyToManyField(Genre, through="FilmWorkGenre")
    persons = models.ManyToManyField(Person, through="FilmWorkPerson")

    class Meta:
        verbose_name = _("film work")
        verbose_name_plural = _("film works")
        db_table = 'content"."film_work'

    def __str__(self):
        return self.title

    @property
    def get_genres(self) -> list:
        return list(self.genres.all().values_list('name', flat=True))
