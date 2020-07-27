from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class RudikSite(admin.AdminSite):
    site_header = _("Rudik")
    site_title = _("Rudik Portal")
    index_title = _("Rudik Portal")


rudik_site = RudikSite()
