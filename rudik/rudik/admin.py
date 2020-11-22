import logging

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from requests import HTTPError

from order.integrations import EPochtaClient

log = logging.getLogger(__name__)


class RudikSite(admin.AdminSite):
    site_header = _("Rudik")
    site_title = _("Rudik Portal")
    index_title = _("Admin Portal")
    index_template = "rudik/admin/index.html"

    def index(self, request, extra_context=None):
        epochta_client = EPochtaClient()
        try:
            balance = epochta_client.get_balance()
        except HTTPError as e:
            log.exception(e)
            balance = {}
        response = super(RudikSite, self).index(request, extra_context=extra_context)
        response.context_data.update(
            {
                "epochta_balance": balance.get("balance_currency"),
                "epochta_currency": balance.get("currency"),
            }
        )
        return response


rudik_site = RudikSite()
