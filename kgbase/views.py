from django.shortcuts import render
# from rest_framework.viewsets import ViewSet
from .models import *
from .serializer import *
from rest_framework.response import Response
from .common import *
# Create your views here.


class EntityViewSets(KgModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

    class Meta:
        model = Entity


class TypeViewSets(KgModelViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer

    class Meta:
        model = Type


class PropertyViewSets(KgModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def retrieve(self, request, *args, **kwargs):
        return super(PropertyViewSets, self).retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super(PropertyViewSets, self).list(request, *args, **kwargs)

    class Meta:
        model = Property


class RelationViewSets(KgModelViewSet):
    serializer_class = RelationSerializer
    filter_backends = (MongoFilterBackend, )
    filter_fields = ('one', 'two')
    pagination_class = ManyQuerySetLimitOffsetPagination
    # queryset = RelationBase.objects.all()

    def get_queryset(self):
        return []

    def get_querysets(self):
        return [m.objects.all() for m in get_all_relation_models()]

    def list(self, request, *args, **kwargs):
        querysets = [self.filter_queryset(qs) for qs in self.get_querysets()]

        page = self.paginate_queryset(querysets)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer([], many=True)
        return Response(serializer.data)

