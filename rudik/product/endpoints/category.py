from rest_framework import serializers
from rest_framework import viewsets
from rest_framework_recursive.fields import RecursiveField

from ..models import Category
from ..models import CategoryImage


class CategoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryImage
        fields = ["image", "is_default"]


class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True)
    images = CategoryImageSerializer(many=True)

    class Meta:
        model = Category
        fields = ["id", "name", "children", "images"]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super(CategoryViewSet, self).get_queryset()
        if self.action == "list":
            return Category.objects.root_nodes()
        return queryset
