from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import FilmWork, FilmWorkPerson, FilmWorkGenre, Genre, Person


class FilmWorkPersonInline(admin.TabularInline):
    model = FilmWorkPerson
    extra = 0
    fields = ("film_work", "person", "role")
    raw_id_fields = ("film_work", "person")


class FilmWorkGenreInline(admin.TabularInline):
    model = FilmWorkGenre
    extra = 0
    fields = ("genre",)
    raw_id_fields = ("film_work", "genre")


class GenreFilmWorkListFilter(admin.SimpleListFilter):
    title = _('genre')
    parameter_name = 'genre'

    def lookups(self, request, model_admin):
        return ((genre.name, genre.name) for genre in Genre.objects.all())

    def queryset(self, request, queryset):
        if self.value():
            genre = Genre.objects.get(name=self.value())
            return genre.filmwork_set.all()
        return queryset


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'creation_date', 'rating')
    list_filter = ('type', 'creation_date', 'rating', GenreFilmWorkListFilter)
    search_fields = ('title', 'description', 'id')
    fields = (
        'title', 'type', 'description', 'creation_date', 'certificate',
        'file_path', 'rating'
    )
    inlines = (
        FilmWorkPersonInline, FilmWorkGenreInline
    )

    def save_related(self, request, form, formsets, change):
        pass
        # for formset in formsets:
        #     self.save_formset(request, form, formset, change=change)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'id')
    fields = (
        'name', 'description'
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date')
    search_fields = ('full_name', 'birth_date', 'id')
    fields = ('full_name', 'birth_date', 'id')

    inlines = (
        FilmWorkPersonInline,
    )
