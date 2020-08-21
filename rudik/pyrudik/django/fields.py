import re

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .widgets import ColorWidget

COLOR_RE = re.compile("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
color_validator = RegexValidator(COLOR_RE, _("Enter a valid color."), "invalid")


class ColorField(models.CharField):

    default_validators = [color_validator]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 18)
        if kwargs.get("null"):
            kwargs.setdefault("blank", True)
            kwargs.setdefault("default", None)
        elif kwargs.get("blank"):
            kwargs.setdefault("default", "")
        else:
            kwargs.setdefault("default", "#FFFFFF")
        super(ColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs["widget"] = ColorWidget(attrs={"default": self.get_default()})
        return super(ColorField, self).formfield(**kwargs)
