from rest_framework import mixins
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action

from ..constants import DELIVERY_COMPANIES
from ..models import Order
from ..models import Recipient, ProductVariantOrder


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = [
            "first_name",
            "second_name",
            "phone",
            "email",
        ]


class ProductVariantOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantOrder
        fields = ["product_variant", "qty"]


class OrderSerializer(serializers.ModelSerializer):
    recipient = RecipientSerializer()
    second_recipient = RecipientSerializer(allow_null=True)
    products = ProductVariantOrderSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = [
            "id",
            "recipient",
            "second_recipient",
            "payment_type",
            "delivery_company",
            "delivery_type",
            "branch",
            "region",
            "city",
            "comment",
            "dont_call",
            "products",
        ]

    def create(self, validated_data):
        validated_data["recipient"] = self.create_recipient(validated_data.pop("recipient"))
        validated_data["second_recipient"] = self.create_recipient(
            validated_data.pop("second_recipient", None)
        )
        products = [
            ProductVariantOrder(**product_data)
            for product_data in validated_data.pop("products")
        ]
        order = super(OrderSerializer, self).create(validated_data)
        order.productvariantorder_set.set(products)
        return order

    @staticmethod
    def create_recipient(recipient_data):
        if recipient_data:
            phone = recipient_data.pop("phone")
            return Recipient.create_recipient(phone, recipient_data)
        return None


class OrderViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False)
    def companies(self):
        DELIVERY_COMPANIES
