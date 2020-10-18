import logging

from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

log = logging.getLogger(__name__)


class PreviewMixin(object):
    img_height = 80

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(PreviewMixin, self).get_readonly_fields(request, obj)
        if "preview" not in readonly_fields:
            readonly_fields += ("preview",)
        return readonly_fields

    def preview(self, obj):
        img_url = static("images/not_found_image.jpg")
        if obj.id:
            try:
                img_url = self.get_image_url(obj)
            except Exception as e:
                log.info(e)
        return mark_safe(
            '<a href="{img_url}">'
            '<image src="{img_url}" height="{img_height}"/>'
            "</a>".format(img_url=img_url, img_height=self.img_height)
        )

    preview.short_description = _("Preview")

    def get_image_url(self, obj):
        return obj.image.url
