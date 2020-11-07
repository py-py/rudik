from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..integrations import NovaPoshtaClient


class RegionDeliverySerializer(serializers.Serializer):
    region = serializers.UUIDField()


class CityDeliverySerializer(serializers.Serializer):
    city = serializers.UUIDField()


class DeliveryViewSet(viewsets.GenericViewSet):
    @property
    def client(self):
        return NovaPoshtaClient()

    @action(detail=False)
    def regions(self, request):
        data = [(item["Ref"], item["DescriptionRu"]) for item in self.client.list_regions()]
        return Response(data)

    @action(detail=False, serializer_class=RegionDeliverySerializer)
    def cities(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        region = str(serializer.validated_data["region"])
        data = [
            (item["Ref"], item["DescriptionRu"]) for item in self.client.list_region_cities(region)
        ]
        return Response(data)

    @action(detail=False, serializer_class=CityDeliverySerializer)
    def terminals(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        city = str(serializer.validated_data["city"])
        data = [(item["Ref"], item["DescriptionRu"]) for item in self.client.list_terminals(city)]
        return Response(data)
