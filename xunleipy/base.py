from __future__ import absolute_import, unicode_literals
from time import time, sleep

import requests
from requests.exceptions import ConnectionError
from six.moves.urllib.parse import unquote

from .rk import RClient
from .rsa_lib import rsa_encrypt_password
from .utils import _md5
from .fp import fp_sign


DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0)\
    Gecko/20100101 Firefox/32.0'
DEFAULT_REFERER = 'http://i.xunlei.com/login/?r_d=1&use_cdn=0&timestamp=' + str(time() * 1000) + '&refurl=http%3A%2F%2Fyuancheng.xunlei.com%2Flogin.html'
XUNLEI_LOGIN_VERSION = 101
DEVICE_ID = 'wdi10.c9b1132a641dc557242aecc6f21fcc20d902f3b01972e9ff8e8529c782188bb7'

FP_RAW = "TW96aWxsYS81LjAgKE1hY2ludG9zaDsgSW50ZWwgTWFjIE9TIFggMTBfMTJfMykgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzU2LjAuMjkyNC44NyBTYWZhcmkvNTM3LjM2IyMjemgtQ04jIyMyNCMjIzkwMHgxNDQwIyMjLTQ4MCMjI3RydWUjIyN0cnVlIyMjdHJ1ZSMjI3VuZGVmaW5lZCMjI2Z1bmN0aW9uIyMjIyMjTWFjSW50ZWwjIyMjIyNTaG9ja3dhdmUgRmxhc2g6OlNob2Nrd2F2ZSBGbGFzaCAyNS4wIHIwOjphcHBsaWNhdGlvbi94LXNob2Nrd2F2ZS1mbGFzaH5zd2YsYXBwbGljYXRpb24vZnV0dXJlc3BsYXNofnNwbDtOYXRpdmUgQ2xpZW50Ojo6OmFwcGxpY2F0aW9uL3gtbmFjbH4sYXBwbGljYXRpb24veC1wbmFjbH4sYXBwbGljYXRpb24veC1wcGFwaS12eXNvcn47V2lkZXZpbmUgQ29udGVudCBEZWNyeXB0aW9uIE1vZHVsZTo6RW5hYmxlcyBXaWRldmluZSBsaWNlbnNlcyBmb3IgcGxheWJhY2sgb2YgSFRNTCBhdWRpby92aWRlbyBjb250ZW50LiAodmVyc2lvbjogMS40LjguOTYyKTo6YXBwbGljYXRpb24veC1wcGFwaS13aWRldmluZS1jZG1+O0Nocm9tZSBQREYgVmlld2VyOjo6OmFwcGxpY2F0aW9uL3BkZn5wZGY7Q2hyb21lIFBERiBWaWV3ZXI6OlBvcnRhYmxlIERvY3VtZW50IEZvcm1hdDo6YXBwbGljYXRpb24veC1nb29nbGUtY2hyb21lLXBkZn5wZGYjIyNmMzUyMWQxNzUxZDQ0NDJhZGI0NTcxZjgyNzgwZGFhYQ=="


class XunLei(object):

    def __init__(self,
                 username=None,
                 password=None,
                 rk_username=None,
                 rk_password=None,
                 user_agent=DEFAULT_USER_AGENT,
                 referer=DEFAULT_REFERER,
                 proxy=None):

        self.username = username
        self.password = password
        self.session = requests.session()
        self.session.headers['User-Agent'] = user_agent
        self.session.headers['Referer'] = referer
        self.user_id = None
        self.is_login = False
        self.session_id = None
        self.lsession_id = None
        self.device_id = None
        self.v = XUNLEI_LOGIN_VERSION
        if rk_username and rk_password:
            self.rk_client = RClient(rk_username, rk_password)
        else:
            self.rk_client = None

        if proxy:
            self.proxies = {'http': proxy}
            self.session.proxies = self.proxies

    def _current_timestamp(self):
        return int(time() * 1000)

    def _crack_verify_code(self):
        url = 'http://verify1.xunlei.com/image?t=MVA&cachetime=%s' % (self._current_timestamp() * 1000)
        try_count = 0
        while try_count < 3:
            try:
                r = self.session.get(
                    url, stream=True, cookies={
                #        'deviceid': DEVICE_ID,
                        '_x_t_': '0',
                    }
                )
                break
            except ConnectionError:
                try_count += 1
                print ('Check url connection error. retry ' + str(try_count))
                sleep(3)
        if try_count == 3:
            return None

        if r.status_code == 200:
            image = r.content
            if self.rk_client:
                verify_code_dict = self.rk_client.rk_create(image, 3040)
                if verify_code_dict:
                    if 'Error' in verify_code_dict.keys():
                        print (verify_code_dict['Error'])
                        return None
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

    def _get_csrf_token(self, device_id):
        return _md5(device_id[:32])

    def _get_signed_fp(self, fp_raw):
        return fp_sign(fp_raw)

    def _get_device_id(self):
        fp = _md5(FP_RAW)
        fp_sign = self._get_signed_fp(FP_RAW)
        import pdb;pdb.set_trace()
        rsp = self.session.post(
            'https://login.xunlei.com/risk?cmd=report',
            data={
                'xl_fp_raw': FP_RAW,
                'xl_fp': fp,
                'xl_fp_sign': fp_sign,
                'cachetime': self._current_timestamp() * 1000
            }
        )
        device_id = rsp.cookies.get('deviceid')
        return device_id

    def login(self):
        login_url = 'https://login.xunlei.com/sec2login/'
        login_url1 = 'https://login3.xunlei.com/sec2login/'

        username = self.username
        business_type = "113"
        try_time = 0

        cache_time = self._current_timestamp() * 1000
        verify_code = '----'
        while try_time < 3:
            sleep(3)
            device_id = self._get_device_id()
            if not device_id:
                print ('device id is null')
                continue

            check_url = 'https://login.xunlei.com/check?u=%s&cachetime=%d&business_type=%s&v=%s&csrf_token=' + self._get_csrf_token(device_id)
            # get verify_code from check url
            check_url = check_url % (username, cache_time, business_type, self.v)
            try_count = 0

            while try_count < 3:
                try:
                    r = self.session.get(check_url)
                    break
                except ConnectionError:
                    try_count += 1
                    print ('Connection error. retry ' + str(try_count))
                    sleep(3)

            if try_count == 3:
                try_time += 1
                print ('Get check code failed!')
                sleep(10)
                continue

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

        if try_time == 3:
            print ('Get check_n failed!Login Failed')
            return False

        if check_n:
            encrypted_password = rsa_encrypt_password(
                self.password, verify_code, check_n, check_e
            )
        else:
            encrypted_password = self.password

        data = {
            'login_enable': '0',
            'u': username,
            'p': encrypted_password,
            'verifycode': verify_code,
            'business_type': business_type,
            'v': self.v,
            'cachetime': cache_time,
        }

        if check_n:
            data['n'] = check_n
            data['e'] = check_e

        try_count = 0

        while try_count < 3:
            try:
                self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded'
#                rsp = self.session.post(login_url, data=data)
                rsp = self.session.post(
                    login_url + '?csrf_token=' + self._get_csrf_token(device_id),
                    data=data,
                    cookies={
                        'accessmode': '10000',
                        'verify_type': 'MVA'
                    }
                )
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
            print ('login success')
        else:
            # login failed
            print ('login failed')
            if 'limit' in rsp.content:
                print ('ip limit! change ip')
            if rsp.cookies.get('blogresult') == "22":
                print ('login enviroment invalid')
            pass

        return self.is_login
