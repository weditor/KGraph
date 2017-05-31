from django.db import models
import mongoengine
from rest_framework_mongoengine.serializers import DynamicDocumentSerializer
from collections import defaultdict
# Create your models here.

DB_ALIAS = 'kgbase'


_relation_models = defaultdict(dict)


class BaseMixin:
    meta = {'db_alias': DB_ALIAS}


class NumberValue(mongoengine.Document, BaseMixin):
    value = mongoengine.FloatField(primary_key=True)

    def __str__(self):
        return str(self.value)


class StringValue(mongoengine.Document, BaseMixin):
    value = mongoengine.StringField()

    def __str__(self):
        return self.value


class RelationBase(mongoengine.Document):
    property = mongoengine.ObjectIdField()
    one = mongoengine.GenericReferenceField()
    two = mongoengine.GenericReferenceField()

    meta = {'abstract': True}


class Type(mongoengine.DynamicDocument, BaseMixin):
    name = mongoengine.StringField()

    def __str__(self):
        return self.name


class Property(mongoengine.Document, BaseMixin):
    name = mongoengine.StringField()
    domains = mongoengine.ListField(mongoengine.StringField())
    ranges = mongoengine.ListField(mongoengine.StringField())

    def get_relation_cls(self):
        if not getattr(self, 'id', None):
            raise Exception('Property has not save yet!')
        if 'model' not in _relation_models[str(self.id)]:
            _relation_models[str(self.id)]['model'] = type('Relation%s' % str(self.id), (RelationBase, BaseMixin), {})
        return _relation_models[str(self.id)]['model']

    def get_relation_serializer(self):
        if not getattr(self, 'id', None):
            raise Exception('Property has not save yet!')
        if 'serializer' not in _relation_models[str(self.id)]:
            _relation_models[str(self.id)]['serializer'] = \
                type('Relation%sSerializer' % str(self.id), (DynamicDocumentSerializer, ),
                     {'Meta': type('Meta', (object, ), {'model': self.get_relation_cls(), 'fields': '__all__'})})
        return _relation_models[str(self.id)]['serializer']

    def __str__(self):
        return self.name


class Entity(mongoengine.Document, BaseMixin):
    name = mongoengine.StringField()
    description = mongoengine.StringField()

    def __str__(self):
        return self.name


# DB_ALIAS = 'kgbase'
# mongoengine.register_connection('kgbase', name='kgbase')
mongoengine.register_connection(DB_ALIAS, name=DB_ALIAS)


for prop in Property.objects.all():
    # print(prop)
    prop.get_relation_cls()
    prop.get_relation_serializer()


def get_all_relation_models():
    return [value['model'] for value in _relation_models.values()]
