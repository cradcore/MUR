# Sorrow446

import os
import re
from random import randint
import time
import hashlib
import requests
from api.exceptions import IneligibleError


class Client:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
        })
        self.series = False
        self.private_key = None
        self.public_key = None

    def set_cookies(self, cookies):
        self.session.cookies.update(cookies)

    def get_issue_id(self, url):
        r = self.session.get(url)
        regex = r'digital_comic_id: "(([0-9]+))"'
        return re.search(regex, r.text).group(1)

    def make_call(self, epoint, params=None):
        r = self.session.get(self.base+epoint, params=params)
        r.raise_for_status()
        return r

    def get_comic_meta(self, id):
        self.session.headers.update({'Referer': 'https://read.marvel.com/'})
        r = self.make_call('issue/v1/digitalcomics/'+id+'?')
        return r.json()['data']['results'][0]['issue_meta']

    def get_comic(self, id):
        params = {'rand': randint(10000, 99999)}
        r = self.make_call('asset/v1/digitalcomics/'+id+'?', params=params)
        j = r.json()['data']['results'][0]
        if not j['auth_state']['subscriber']:
            raise IneligibleError('Marvel Unlimited subscription required.')
        urls = [url['assets']['source'] for url in j['pages']]
        return urls

    def set_series(self, wholeSeries):
        self.series = wholeSeries
        if wholeSeries:
            self.base = 'https://gateway.marvel.com/'
        else:
            self.base = 'https://read-api.marvel.com/'

    def is_series(self):
        return self.series

    def set_keys(self, private_key, public_key):
        self.private_key = private_key
        self.public_key = public_key

    def has_keys(self):
        return self.private_key != None and self.public_key != None

    def get_api_params(self):
        timestamp = int(time.time())
        strToHash = "%d%s%s" % (timestamp, self.private_key, self.public_key)
        md5Hash = hashlib.md5(strToHash.encode()).hexdigest()
        return {'ts': timestamp, 'apikey': self.public_key, 'hash': md5Hash}

    def parse_series(self, id):
        if not self.is_series():
            print("Cannot parse series when API object is set to issue mode")
            return None
        r = self.make_call('v1/public/series/' + id + '?', self.get_api_params())
        items = r.json()['data']['results'][0]['comics']['items']
        ids = []
        for item in items:
            if "(Variant)" not in item['name']:
                uri = item['resourceURI']
                ids.append(uri.split('/')[-1])
        return ids

    def get_issue_url_from_id(self, id):
        if not self.is_series():
            print("Cannot retrieve issue URL from ID without dev keys")
            return None
        r = self.make_call('v1/public/comics/' + id + '?', self.get_api_params())
        urls = r.json()['data']['results'][0]['urls']
        for url in urls:
            if "detail" in url['type']:
                return self.sanitize_url(url['url'])
        return None

    def sanitize_url(self, url):
        if '?' in url:
            url = url.split('?')[0]
        if 'www' not in url and 'http' in url:
            index = url.index("://") + 3
            url = url[ : index] + "www." + url[index :]
        if 'https' not in url and 'http' in url:
            url = 'https' + url[4 : ]
        return url