# coding: utf-8
try:
    import requests
    import json
except ImportError:
    pass


class Client(object):

    def __init__(self, url, token, verify_ssl=True):
        self._url = url
        self._token = token
        self._verify_ssl = verify_ssl

    def call(self, resource_path, arguments):
        url = '%s/%s' % (self._url, resource_path)
        print(url)
        u_a = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36"
        res = requests.get(url, params=arguments, verify=self._verify_ssl, headers={'Authorization': 'Basic %s' % self._token,"USER-AGENT":u_a,'Accept':"application/json"})
        res.raise_for_status()
        return res.json()
