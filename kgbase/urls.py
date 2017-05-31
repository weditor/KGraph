from django.conf.urls import url, include
from rest_framework import routers
from .views import *


route = routers.DefaultRouter()
# route.get_default_base_name()
route.register('entity', EntityViewSets, 'entity')
route.register('type', TypeViewSets, 'type')
route.register('property', PropertyViewSets, 'property')
route.register('relation', RelationViewSets, 'relation')


urlpatterns = [
    url(r'', include(route.urls)),
]
