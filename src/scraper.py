import urllib
import requests


class Scraper():
    def __init__(self, url_endpoint: str) -> None:
        self.url_endpoint = url_endpoint

    def scrape(self, **kwargs):
        url = self.url_endpoint
        if kwargs is not None and len(kwargs) > 0:
            querystring = urllib.parse.urlencode(kwargs)
            if len(querystring) >= 1:
                url += '?' + querystring

        print(url)
        return requests.get(url)
