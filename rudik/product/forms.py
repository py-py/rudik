from django import forms
from django.db.models import Count
from django.db.models import F
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import ProductVariant


class ProductVariantModelForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = "__all__"

    def clean(self):
        qs = self.cleaned_data["configurations"]
        duplicates = [
            config
            for config in qs.values(type_name=F("type__name")).annotate(count=Count("type_name"))
            if config["count"] > 1
        ]
        if duplicates:
            names = ", ".join(d["type_name"] for d in duplicates)
            error = _("Forbidden to select the same configuration types: {}.").format(names)
            raise ValidationError({"configurations": error})
