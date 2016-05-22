from __future__ import absolute_import, unicode_literals
from time import time, sleep

import requests
from requests.exceptions import ConnectionError
from six.moves.urllib.parse import unquote

from .rk import RClient
from .rsa_lib import rsa_encrypt_password


DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0)\
    Gecko/20100101 Firefox/32.0'
DEFAULT_REFERER = 'http://i.vod.xunlei.com/resource_assistant'


class XunLei(object):

    def __init__(self,
                 username=None,
                 password=None,
                 rk_username=None,
                 rk_password=None,
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
        if rk_username and rk_password:
            self.rk_client = RClient(rk_username, rk_password)
        else:
            self.rk_client = None

    def _current_timestamp(self):
        return int(time() * 1000)

    def _crack_verify_code(self):
        url = 'http://verify2.xunlei.com/image?t=MVA&cachetime=%s' % self._current_timestamp()
        r = self.session.get(url, stream=True)
        if r.status_code == 200:
            image = r.content
            if self.rk_client:
                verify_code_dict = self.rk_client.rk_create(image, 3040)
                if verify_code_dict:
                    verify_code = verify_code_dict.get('Result', '')
                else:
                    print ('rk failed ', verify_code_dict)
                    return None
            else:
                print ('need login ruokuai account')
                return None
        else:
            print ('get verify code error')
            return None

        return verify_code

    def login(self):
        login_url = 'http://login.xunlei.com/sec2login/'

        username = self.username
        business_type = 113
        try_time = 0
        while try_time < 3:
            check_url = 'http://login.xunlei.com/check?u=%s&cachetime=%d&business_type=%s'
            # get verify_code from check url
            cache_time = self._current_timestamp()
            check_url = check_url % (username, cache_time, business_type)
            r = self.session.get(check_url)

            # get n, e for RSA encryption
            check_n = unquote(r.cookies.get('check_n', ''))
            check_e = r.cookies.get('check_e', '')

            # check_result is like '0:!kuv', but we auctually only need '!kuv'
            verify_code_tmp = r.cookies.get('check_result', '').split(':')
            if len(verify_code_tmp) == 2 and verify_code_tmp[0] == '0':
                verify_code = verify_code_tmp[1]
                break
            else:
                print ('verify_code:', r.cookies.get('check_result', ''))
                verify_code = self._crack_verify_code()
                if verify_code:
                    break
                try_time += 1
                sleep(10)

        encrypted_password = rsa_encrypt_password(
            self.password, verify_code, check_n, check_e
        )
        data = {
            'login_enable': 0,
            'u': username,
            'p': encrypted_password,
            'n': check_n,
            'e': check_e,
            'verifycode': verify_code,
            'business_type': business_type,
            'v': 100,
        }

        try_count = 0

        while try_count < 3:
            try:
                rsp = self.session.post(login_url, data=data)
                break
            except ConnectionError:
                try_count += 1
                print ('Connection error. retry ' + str(try_count))
                sleep(3)
        user_id = rsp.cookies.get('userid')
        if user_id:
            # login success
            self.user_id = user_id
            self.is_login = True
        else:
            # login failed
            print ('login failed')
            pass

        return self.is_login
