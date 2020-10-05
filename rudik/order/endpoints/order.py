from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.validators import UniqueValidator

from ..constants import DELIVERY_COMPANIES
from ..models import Order
from ..models import OrderItem
from ..models import Recipient


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = [
            "first_name",
            "second_name",
            "phone",
            "email",
        ]

    def __init__(self, *args, **kwargs):
        super(RecipientSerializer, self).__init__(*args, **kwargs)
        self.fields["phone"].validators = [
            validator
            for validator in self.fields["phone"].validators
            if not isinstance(validator, UniqueValidator)
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product_variant", "qty"]

    def validate(self, attrs):
        try:
            item = OrderItem(**attrs)
            item.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    default_error_messages = {"not_unique": _("Object contains not unique values.")}
    recipient = RecipientSerializer()
    second_recipient = RecipientSerializer(allow_null=True)
    items = OrderItemSerializer(many=True, allow_empty=False)

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
            "items",
        ]

    def validate_items(self, items):
        if len(items) != len({item["product_variant"] for item in items}):
            raise self.fail("not_unique")
        return items

    def create(self, validated_data):
        validated_data["recipient"] = self.create_recipient(validated_data.pop("recipient"))
        validated_data["second_recipient"] = self.create_recipient(
            validated_data.pop("second_recipient", None)
        )
        items = validated_data.pop("items")
        with transaction.atomic():
            order = super(OrderSerializer, self).create(validated_data)
            for item_data in items:
                OrderItem.objects.create(order=order, **item_data)
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
        return [
            {"id": company_id, "name": company_name}
            for company_id, company_name in DELIVERY_COMPANIES
        ]
