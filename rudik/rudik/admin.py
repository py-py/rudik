from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from order.integrations import EPochtaClient


class RudikSite(admin.AdminSite):
    site_header = _("Rudik")
    site_title = _("Rudik Portal")
    index_title = _("Admin Portal")
    index_template = "rudik/admin/index.html"

    def index(self, request, extra_context=None):
        epochta_client = EPochtaClient()
        balance = epochta_client.get_balance()
        response = super(RudikSite, self).index(request, extra_context=extra_context)
        response.context_data.update(
            {
                "epochta_balance": balance["balance_currency"],
                "epochta_currency": balance["currency"],
            }
        )
        return response


rudik_site = RudikSite()
