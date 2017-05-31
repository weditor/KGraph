from rest_framework.pagination import BasePagination, LimitOffsetPagination, _get_count
from rest_framework.filters import BaseFilterBackend
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import Http404
from mongoengine.errors import NotUniqueError, MultipleObjectsReturned, DoesNotExist


def get_object_or_404(queryset, *args, **kwargs):
    try:
        return queryset.get(*args, **kwargs)
    except (TypeError, MultipleObjectsReturned, DoesNotExist):
        raise Http404


class KgModelViewSet(ModelViewSet):

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class MongoFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_fields = getattr(view, 'filter_fields')
        query_kw = {k: v for k, v in request.query_params.items() if k in filter_fields}

        return queryset.filter(**query_kw)


class ManyQuerySetLimitOffsetPagination(LimitOffsetPagination):

    def paginate_queryset(self, querysets, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        # self.count = sum(_get_count(qs) for qs in querysets)
        self.request = request

        # if self.count == 0 or self.offset > self.count:
        #     return []

        self.count = 0
        limit = self.limit
        result = []
        for qs in querysets:
            qs_count = _get_count(qs)
            if self.offset >= self.count+qs_count:
                continue
            elif self.offset < self.count+qs_count and limit > 0:
                start = max(self.offset, self.count) - self.count
                end = min(start+limit, qs_count)
                result.extend(qs[start: end])
                limit -= (end-start)
                self.count += qs_count

        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True
        return result


