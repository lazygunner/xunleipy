# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import random
import base64
import time
import six

import requests
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

    source = fp_str.strip()
    if six.PY3:
        source = source.encode('utf-8')

    fp_raw = base64.b64encode(source)
    return fp_raw


def get_fp_sign(fp_raw):
    rsp = requests.get(
        'https://login.xunlei.com/risk?cmd=algorithm&t=' +
        str(time.time() * 1000)
    )
    sign = ''
    try:
        xl_al = js2py.eval_js(rsp.content)
        sign = xl_al(fp_raw)
    except Exception as e:
        print(e)

    return sign
