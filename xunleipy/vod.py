# -*- encoding:utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json

from .base import XunLei

VOD_BASE_URL = 'http://i.vod.xunlei.com/'


class XunLeiVod(XunLei):

    def __init__(self, username, password, rk_username=None, rk_password=None):
        super(XunLeiVod, self).__init__(
            username, password, rk_username, rk_password)
        if not self.is_login:
            self.login()

    def _request(self, method, url, **kwargs):
        url = VOD_BASE_URL + url

        if 'params' not in kwargs:
            kwargs['params'] = {}
        if 'data' not in kwargs:
            kwargs['data'] = {}
        if isinstance(kwargs['data'], dict):
            data = json.dumps(kwargs['data'], ensure_ascii=False)
            data = data.encode('utf-8')
            kwargs['data'] = data

        result = self.session.request(
            method=method,
            url=url,
            **kwargs
            )
        result.raise_for_status()
        data = result.json()

        if 'resp' in data:
            data = data['resp']
        if data['ret'] != 0:
            print data
            print('request for %s failed, code:%s, msg:%s',
                  url, data['ret'], data.get('msg', ''))

        return data

    def _get(self, url, **kwargs):
        return self._request(
            method='get',
            url=url,
            **kwargs
        )

    def _post(self, url, **kwargs):
        return self._request(
            method='post',
            url=url,
            **kwargs
        )

    def add_task_to_vod(self, urls):
        url_list = []
        for i in range(len(urls)):
            url = urls[i]
            if 'ed2k' in url:
                url_tmp = url.split('|')
                if len(url_tmp) > 2:
                    name = url_tmp[2]
                else:
                    name = url
            else:
                name = url

        url_list.append({
            'id': i,
            'url': url,
            'name': name
        })

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        params = {
            'from': 'extlist',
            'platform': 0,
            'userid': self.session.cookies.get('userid'),
            'sessionid': self.session.cookies.get('sessionid')
        }
        data = {
            'urls': url_list
        }

        res = self._post(
            'req_add_record',
            headers=headers,
            params=params,
            data=data
        )

        return res
