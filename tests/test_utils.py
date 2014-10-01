# -*- encoding:utf-8 -*-

import unittest

from xunleipy.utils import *

class UtilsTestCase(unittest.TestCase):
    def test_password_hash(self):
        p = '1234abcd!@#$%^&*()_+'
        h = 'dcf69f9a6b1db545af3285659670c655'
        verify_code = '!ZZ3'
        self.assertEqual(get_password_hash(p, verify_code), h)

if __name__ == '__main__':
    unittest.main()
