from urllib.parse import urljoin

from requests import Session


class BaseUrlSession(Session):
    """A simple wrapper to use a single base-url for calls made through this session."""

    base_url = None

    def __init__(self, base_url=None):
        self.base_url = base_url
        super(BaseUrlSession, self).__init__()

    def request(self, method, url, *args, **kwargs):
        url = self.get_absolute_url(url)
        return super(BaseUrlSession, self).request(method, url, *args, **kwargs)

    def get_absolute_url(self, url):
        if not url.startswith("http"):
            url = urljoin(self.base_url, url)
        return url
