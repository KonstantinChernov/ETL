from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import FilmWork


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    @staticmethod
    def get_role_aggregation(role):
        return ArrayAgg('persons__full_name',
                        distinct=True,
                        filter=Q(filmworkperson__role=role))

    def get_queryset(self):
        qs = self.model.objects.prefetch_related('genres', 'persons').all().values(
            'id',
            'title',
            'description',
            'creation_date',
            'rating',
            'type',
        )
        qs = qs.annotate(genres=ArrayAgg('genres__name', distinct=True))
        qs = qs.annotate(actors=self.get_role_aggregation('actor'))
        qs = qs.annotate(writers=self.get_role_aggregation('writer'))
        qs = qs.annotate(directors=self.get_role_aggregation('director'))
        return qs

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    model = FilmWork
    http_method_names = ['get']
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )
        return {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            "results": list(queryset)
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    model = FilmWork
    http_method_names = ['get']

    def get_context_data(self, **kwargs):
        return kwargs['object']
