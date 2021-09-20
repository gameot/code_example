from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from house.models import Amenity, RequiredVerification
from .serializers import AmenityListSerializer, AmenitySerializer
from ..base.serializers import MultiSerializerViewSetMixin


class AmenityViewSet(CreateModelMixin, ListModelMixin, MultiSerializerViewSetMixin, GenericViewSet):
    http_method_names = ('get', 'post')
    permission_classes = [IsAuthenticated]
    serializer_class = AmenityListSerializer
    serializer_action_classes = {
        'create': AmenitySerializer,
        'batch_create': AmenitySerializer,
    }

    def get_queryset(self, for_house=False, for_house_space=False):
        on_verification = RequiredVerification.amenities.filter(user=self.request.user)
        on_verification = on_verification.values_list('object_id', flat=True)

        queryset = Amenity.active.all()
        if for_house:
            queryset = queryset.filter(is_available_for_house=True)
        if for_house_space:
            queryset = queryset.filter(is_available_for_house_space=True)
        queryset = queryset.union(Amenity.objects.filter(id__in=on_verification).select_related('category'))
        queryset = queryset.order_by('category__order', 'title')
        return queryset

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset().make_hierarchy(), many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        url_path='for_house',
        url_name='for_house_list',
    )
    def list_for_house(self, request, *args, **kwargs):
        queryset = self.get_queryset(for_data=True)
        serializer = self.get_serializer(queryset.make_hierarchy(), many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        url_path='for_house_space',
        url_name='for_house_space_list',
    )
    def list_for_house_space(self, request, *args, **kwargs):
        queryset = self.get_queryset(for_house_space=True)
        serializer = self.get_serializer(queryset.make_hierarchy(), many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=AmenitySerializer(many=True))
    @action(
        detail=False,
        methods=('post', ),
        url_path='batch_create',
        url_name='batch_create',
    )
    def batch_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
