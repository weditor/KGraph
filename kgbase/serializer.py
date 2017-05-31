from rest_framework_mongoengine.serializers import DynamicDocumentSerializer, DocumentSerializer
from rest_framework import serializers
from .models import *
from .common import get_object_or_404


class EntitySerializer(DynamicDocumentSerializer):
    class Meta:
        model = Entity
        fields = '__all__'


class TypeSerializer(DynamicDocumentSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class PropertySerializer(DynamicDocumentSerializer):
    class Meta:
        model = Property
        fields = '__all__'


class RelationSerializer(serializers.Serializer):
    one = serializers.CharField()
    two = serializers.CharField()
    property = serializers.CharField()

    def create(self, validated_data):
        prop = get_object_or_404(Property, pk=validated_data['property'])

