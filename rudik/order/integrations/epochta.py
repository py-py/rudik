import hashlib

from django.conf import settings
from memoize import memoize
from requests import HTTPError

from pyrudik.common.sessions import BaseUrlSession


class EPochtaSession(BaseUrlSession):
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key
        super(EPochtaSession, self).__init__(base_url="http://api.atompark.com/api/sms/3.0/")

    def update_params(self, url, params):
        params["test"] = 1  # TODO: temporary parameter
        params["action"] = url
        params["version"] = "3.0"
        params["key"] = self.public_key
        sorted_values = [params[key] for key in sorted(params)]
        sorted_values.append(self.private_key)
        raw = "".join(map(str, sorted_values))
        params["sum"] = hashlib.md5(raw.encode()).hexdigest()

    def request(self, method, url, *args, **kwargs):
        params = kwargs.setdefault("params", {})
        self.update_params(url, params)
        response = super(EPochtaSession, self).request(method, url, *args, **kwargs)
        response.raise_for_status()
        data = response.json()
        if data["result"] == "false":
            raise HTTPError(response.text, response=response)
        return data


class EPochtaClient:
    def __init__(self):
        self.session = EPochtaSession(
            settings.EPOSHTA_PUBLIC_TOKEN, settings.EPOSHTA_PRIVATE_TOKEN
        )

    def __repr__(self):
        # we use this simple name for memoize
        return self.__class__.__name__.upper()

    @memoize(timeout=60)
    def get_balance(self):
        params = {"currency": "UAH"}
        return self.session.post("getUserBalance", params=params)

    def send_sms(self, phone, text):
        params = {"phone": phone, "text": text}
        return self.session.post("sendSMS", params=params)

    def get_campaign_info(self, campaign_id):
        params = {"id": campaign_id}
        return self.session.post("getCampaignInfo", params=params)
