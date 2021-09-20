from rest_framework import serializers

from house.models import Amenity, RequiredVerification
from smp_api.base.serializers import LangJSONField


class AmenitySerializer(serializers.ModelSerializer):
    title = LangJSONField()
    abbreviation = LangJSONField()

    class Meta:
        ref_name = 'Amenity SMP'
        model = Amenity
        fields = ('id', 'title', 'abbreviation')

    def create(self, validated_data):
        instance = super().create(validated_data)
        RequiredVerification(
            content_object=instance,
            user=self.context['request'].user,
        ).save()
        return instance


class AmenityListSerializer(serializers.Serializer):
    category = LangJSONField()
    amenities = AmenitySerializer(many=True)

    class Meta:
        ref_name = 'Amenity List SMP'


class SimpleAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        ref_name = 'Simple amenity SMP'
        model = Amenity
        fields = ('id',)
