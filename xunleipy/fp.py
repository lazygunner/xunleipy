# -*- coding: utf-8 -*-
import os
import random
import base64

import js2py
from .utils import get_random_ua


def __get_random_screen_resolution():
    return random.choice([
        '1080*1920',
        '960*1620',
        '800*600',
        '540*720',
    ])


def _get_random_fp_raw():
    '''
        生成随机的原始指纹列表
    '''
    fp_list = []
    fp_list.append(get_random_ua())  # ua
    fp_list.append('zh-CN')  # language
    fp_list.append('24')  # color depth
    fp_list.append(__get_random_screen_resolution())
    fp_list.append('-480')  # time zone offsite
    fp_list.append('true')  # session storage
    fp_list.append('true')  # local storage
    fp_list.append('true')  # indexed db
    fp_list.append('')  # add behavior
    fp_list.append('function')  # open database
    fp_list.append('')  # cpu class
    fp_list.append('MacIntel')  # platform
    fp_list.append('')  # do not track
    fp_list.append(
        'Widevine Content Decryption Module::Enables Widevine \
        licenses for playback of HTML audio/video content. \
        (version: 1.4.8.962)::application/x-ppapi-widevine-cdm~;'
    )  # plugin string

    return fp_list


def get_fp_raw():
    '''
        生成fp_raw_str
    '''
    fp_file_path = os.path.expanduser('~/.xunleipy_fp')
    fp_list = []
    try:
        with open(fp_file_path, 'r') as fp_file:
            fp_str = fp_file.readline()
            if len(fp_str) > 0:
                fp_list = fp_str.split('###')
    except IOError:
        pass

    if len(fp_list) < 14:
        fp_list = _get_random_fp_raw()
        fp_str = '###'.join(fp_list)
        with open(fp_file_path, 'w') as fp_file:
            fp_file.write(fp_str)

    fp_raw = base64.b64encode(fp_str.strip())
    return fp_raw


get_fp_sign = js2py.eval_js(
    '''
    function xl_al(xl) {
    function i(a, b) {
        a[b >> 5] |= 128 << b % 32,
        a[(b + 64 >>> 9 << 4) + 14] = b;
        for (var c = 1732584193, d = -271733879, e = -1732584194, f = 271733878, g = 0; a.length > g; g += 16) {
            var h = c
              , i = d
              , j = e
              , o = f;
            c = k(c, d, e, f, a[g + 0], 7, -680876936),
            f = k(f, c, d, e, a[g + 1], 12, -389564586),
            e = k(e, f, c, d, a[g + 2], 17, 606105819),
            d = k(d, e, f, c, a[g + 3], 22, -1044525330),
            c = k(c, d, e, f, a[g + 4], 7, -176418897),
            f = k(f, c, d, e, a[g + 5], 12, 1200080426),
            e = k(e, f, c, d, a[g + 6], 17, -1473231341),
            d = k(d, e, f, c, a[g + 7], 22, -45705983),
            c = k(c, d, e, f, a[g + 8], 7, 1770035416),
            f = k(f, c, d, e, a[g + 9], 12, -1958414417),
            e = k(e, f, c, d, a[g + 10], 17, -42063),
            d = k(d, e, f, c, a[g + 11], 22, -1990404162),
            c = k(c, d, e, f, a[g + 12], 7, 1804603682),
            f = k(f, c, d, e, a[g + 13], 12, -40341101),
            e = k(e, f, c, d, a[g + 14], 17, -1502002290),
            d = k(d, e, f, c, a[g + 15], 22, 1236535329),
            c = l(c, d, e, f, a[g + 1], 5, -165796510),
            f = l(f, c, d, e, a[g + 6], 9, -1069501632),
            e = l(e, f, c, d, a[g + 11], 14, 643717713),
            d = l(d, e, f, c, a[g + 0], 20, -373897302),
            c = l(c, d, e, f, a[g + 5], 5, -701558691),
            f = l(f, c, d, e, a[g + 10], 9, 38016083),
            e = l(e, f, c, d, a[g + 15], 14, -660478335),
            d = l(d, e, f, c, a[g + 4], 20, -405537848),
            c = l(c, d, e, f, a[g + 9], 5, 568446438),
            f = l(f, c, d, e, a[g + 14], 9, -1019803690),
            e = l(e, f, c, d, a[g + 3], 14, -187363961),
            d = l(d, e, f, c, a[g + 8], 20, 1163531501),
            c = l(c, d, e, f, a[g + 13], 5, -1444681467),
            f = l(f, c, d, e, a[g + 2], 9, -51403784),
            e = l(e, f, c, d, a[g + 7], 14, 1735328473),
            d = l(d, e, f, c, a[g + 12], 20, -1926607734),
            c = m(c, d, e, f, a[g + 5], 4, -378558),
            f = m(f, c, d, e, a[g + 8], 11, -2022574463),
            e = m(e, f, c, d, a[g + 11], 16, 1839030562),
            d = m(d, e, f, c, a[g + 14], 23, -35309556),
            c = m(c, d, e, f, a[g + 1], 4, -1530992060),
            f = m(f, c, d, e, a[g + 4], 11, 1272893353),
            e = m(e, f, c, d, a[g + 7], 16, -155497632),
            d = m(d, e, f, c, a[g + 10], 23, -1094730640),
            c = m(c, d, e, f, a[g + 13], 4, 681279174),
            f = m(f, c, d, e, a[g + 0], 11, -358537222),
            e = m(e, f, c, d, a[g + 3], 16, -722521979),
            d = m(d, e, f, c, a[g + 6], 23, 76029189),
            c = m(c, d, e, f, a[g + 9], 4, -640364487),
            f = m(f, c, d, e, a[g + 12], 11, -421815835),
            e = m(e, f, c, d, a[g + 15], 16, 530742520),
            d = m(d, e, f, c, a[g + 2], 23, -995338651),
            c = n(c, d, e, f, a[g + 0], 6, -198630844),
            f = n(f, c, d, e, a[g + 7], 10, 1126891415),
            e = n(e, f, c, d, a[g + 14], 15, -1416354905),
            d = n(d, e, f, c, a[g + 5], 21, -57434055),
            c = n(c, d, e, f, a[g + 12], 6, 1700485571),
            f = n(f, c, d, e, a[g + 3], 10, -1894986606),
            e = n(e, f, c, d, a[g + 10], 15, -1051523),
            d = n(d, e, f, c, a[g + 1], 21, -2054922799),
            c = n(c, d, e, f, a[g + 8], 6, 1873313359),
            f = n(f, c, d, e, a[g + 15], 10, -30611744),
            e = n(e, f, c, d, a[g + 6], 15, -1560198380),
            d = n(d, e, f, c, a[g + 13], 21, 1309151649),
            c = n(c, d, e, f, a[g + 4], 6, -145523070),
            f = n(f, c, d, e, a[g + 11], 10, -1120210379),
            e = n(e, f, c, d, a[g + 2], 15, 718787259),
            d = n(d, e, f, c, a[g + 9], 21, -343485551),
            c = p(c, h),
            d = p(d, i),
            e = p(e, j),
            f = p(f, o)
        }
        return [c, d, e, f]
    }
    function j(a, b, c, d, e, f) {
        return p(q(p(p(b, a), p(d, f)), e), c)
    }
    function k(a, b, c, d, e, f, g) {
        return j(b & c | ~b & d, a, b, e, f, g)
    }
    function l(a, b, c, d, e, f, g) {
        return j(b & d | c & ~d, a, b, e, f, g)
    }
    function m(a, b, c, d, e, f, g) {
        return j(b ^ c ^ d, a, b, e, f, g)
    }
    function n(a, b, c, d, e, f, g) {
        return j(c ^ (b | ~d), a, b, e, f, g)
    }
    function p(a, b) {
        var c = (a & 65535) + (b & 65535)
          , d = (a >> 16) + (b >> 16) + (c >> 16);
        return d << 16 | c & 65535
    }
    function q(a, b) {
        return a << b | a >>> 32 - b
    }
    function r(a) {
        for (var b = [], d = (1 << c) - 1, e = 0; a.length * c > e; e += c)
            b[e >> 5] |= (a.charCodeAt(e / c) & d) << e % 32;
        return b
    }
    function t(b) {
        for (var c = a ? "0123456789ABCDEF" : "0123456789abcdef", d = "", e = 0; b.length * 4 > e; e++)
            d += c.charAt(b[e >> 2] >> e % 4 * 8 + 4 & 15) + c.charAt(b[e >> 2] >> e % 4 * 8 & 15);
        return d
    }
    var a = 0
      , c = 8
      , xa = "cbfefxb006y81z"
      , xc = xa + xl;
    return t(i(r(xc), xc.length * c))
}

'''
)
