from drf_yasg import openapi
from rest_framework.fields import JSONField


class LangJSONField(JSONField):
    class Meta:
        swagger_schema_fields = {
            'type': openapi.TYPE_OBJECT,
            'description': 'String with a language code in the JSON format. \nFor example {"en": "Line", "ru": "Линия"}',
        }


class MultiSerializerViewSetMixin(object):
    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()
