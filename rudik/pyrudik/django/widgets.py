from django import forms
from django.conf import settings


class ColorWidget(forms.Widget):

    template_name = "fields/colorfield.html"

    class Media:
        if settings.DEBUG:
            js = [
                "colorfield/js/jscolor.js",
                "colorfield/js/colorfield.js",
            ]
        else:
            js = [
                "colorfield/js/jscolor.min.js",
                "colorfield/js/colorfield.js",
            ]
