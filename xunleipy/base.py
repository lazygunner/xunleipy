from __future__ import absolute_import, unicode_literals
from time import time, sleep

import requests

from .utils import get_password_hash


DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0)\
    Gecko/20100101 Firefox/32.0'
DEFAULT_REFERER = 'http://i.vod.xunlei.com/resource_assistant'


class XunLei(object):

    def __init__(
            self,
            username=None,
            password=None,
            user_agent=DEFAULT_USER_AGENT,
            referer=DEFAULT_REFERER):

        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.headers['User-Agent'] = user_agent
        self.session.headers['Referer'] = referer
        self.user_id = None
        self.is_login = False
        self.session_id = None
        self.lsession_id = None

    def _current_timestamp(self):
        return int(time() * 1000)

    def login(self):
        login_url = 'http://login.xunlei.com/sec2login/'

        username = self.username
        try_time = 0
        while try_time < 3:
            check_url = 'http://login.xunlei.com/check?u=%s&cachetime=%d'
            # get verify_code from check url
            cache_time = self._current_timestamp()
            check_url = check_url % (username, cache_time)
            r = self.session.get(check_url)

            # check_result is like '0:!kuv', but we auctually only need '!kuv'
            verify_code_tmp = r.cookies.get('check_result', '').split(':')
            if len(verify_code_tmp) == 2 and verify_code_tmp[0] == '0':
                verify_code = verify_code_tmp[1]
                break
            else:
                print 'verify_code:', r.cookies.get('check_result', '')
                verify_code = ''
                try_time += 1
                sleep(10)

        password_hash = get_password_hash(self.password, verify_code)
        data = {
            'login_enable': 1,
            'login_hour': 720,
            'u': username,
            'p': password_hash,
            'verifycode': verify_code
        }
        r = self.session.post(login_url, data=data)

        user_id = r.cookies.get('userid')
        if user_id:
            # login success
            self.user_id = user_id
            self.is_login = True
        else:
            # login failed
            print 'login failed'
            pass

        return self.is_login
