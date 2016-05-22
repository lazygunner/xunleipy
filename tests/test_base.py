import unittest

from httmock import urlmatch, HTTMock, response

from xunleipy.base import XunLei

@urlmatch(netloc=r'(.*\.)?xunlei\.com')
def xunlei_mock(url, request):
    headers = {}
    if url.path == '/check':
        headers = {
            'Set-Cookie': 'check_result=0:!tst;check_n=asdf;check_e=asd'
        }
    elif url.path == '/sec2login/':
        headers = {
            'Set-Cookie': 'userid=test1234;'
        }

    content = {'message': 'test login'}
    return response(200, content, headers, None, 5, request)

class LoginTest(unittest.TestCase):
    def test_login_success(self):
        with HTTMock(xunlei_mock):
            u = 'testname'
            p = 'testpass'
            xl = XunLei(u, p)
            is_login = xl.login()

            self.assertTrue(is_login)
            self.assertEqual(xl.user_id, 'test1234')


if __name__ == '__main__':
    unittest.main()
