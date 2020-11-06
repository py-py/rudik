from pyrudik.common.sessions import BaseUrlSession
from django.conf import settings
from memoize import memoize


class NovaPoshtaSession(BaseUrlSession):
    def __init__(self, api_key):
        self.api_key = api_key
        super(NovaPoshtaSession, self).__init__(base_url="https://api.novaposhta.ua/v2.0/json/")

    def request(self, method, url, *args, **kwargs):
        kwargs["json"]["apiKey"] = self.api_key
        response = super(NovaPoshtaSession, self).request(method, url, *args, **kwargs)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])


class NovaPoshtaClient:
    def __init__(self):
        self.session = NovaPoshtaSession(api_key=settings.NOVAPOSTA_TOKEN)

    def __repr__(self):
        # we use this simple name for memoize
        return self.__class__.__name__.upper()

    @memoize(timeout=24 * 3600)
    def list_regions(self):
        payload = {"modelName": "Address", "calledMethod": "getAreas", "methodProperties": {}}
        return self.session.post("", json=payload)

    @memoize(timeout=24 * 3600)
    def list_cities(self):
        payload = {"modelName": "Address", "calledMethod": "getCities", "methodProperties": {}}
        return self.session.post("", json=payload)

    def list_region_cities(self, region_id):
        data = self.list_cities()
        return [item for item in data if item["Area"] == region_id]

    @memoize(timeout=24 * 3600)
    def list_terminals(self, city_id):
        payload = {
            "modelName": "AddressGeneral",
            "calledMethod": "getWarehouses",
            "methodProperties": {"CityRef": city_id},
        }
        data = self.session.post("", json=payload)
        return [item for item in data if self.is_filtered_branch(item)]

    @staticmethod
    def is_filtered_branch(terminal):
        terminal_id = int(terminal["Number"])
        # 0-2999 - branches
        # 5000-5999 - terminal with online payment
        return 0 <= terminal_id <= 2999

    @memoize(timeout=24 * 3600)
    def get_terminal_info(self, terminal_id):
        branch_payload = {
            "modelName": "AddressGeneral",
            "calledMethod": "getWarehouses",
            "methodProperties": {"Ref": terminal_id},
        }
        return self.session.post("", json=branch_payload)[0]
