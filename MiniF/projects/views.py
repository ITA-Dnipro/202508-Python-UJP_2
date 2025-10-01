from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
)
from .documents import StartupDocument
from .serializers import StartupDocumentSerializer


class StartupProjectView(DocumentViewSet):
    """Search endpoint for startup projects."""

    document = StartupDocument
    serializer_class = StartupDocumentSerializer
    lookup_field = 'id'

    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]
    search_fields = (
        'startup_name',
        'title',
        'description',
    )
    filter_fields = {
        'status': 'status',
        'startup_name': 'startup_name',
    }
    ordering_fields = {
        'startup_name': 'startup_name.raw',
        'title': 'title',
    }
    ordering = ('startup_name.raw',)
