# -*- encoding:utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import logging

from six.moves.urllib.parse import quote

from .base import XunLei
from .utils import resolve_url

REMOTE_BASE_URL = 'http://homecloud.yuancheng.xunlei.com/'
DEFAULT_V = 2
DEFAULT_CT = 0

logger = logging.getLogger(__name__)


class ListType:
    downloading = 0
    finished = 1
    recycle = 2
    failed = 3


class XunLeiRemote(XunLei):

    def __init__(self,
                 username,
                 password,
                 rk_username=None,
                 rk_password=None):
        super(XunLeiRemote, self).__init__(
            username, password, rk_username, rk_password
        )
        if not self.is_login:
            self.login()
        self.pid = ''

    def _request(self, method, url, **kwargs):
        url = REMOTE_BASE_URL + url

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

        if data['rtn'] != 0:
            print('request for %s failed, code:%s', url, data['rtn'])

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

    def get_remote_peer_list(self):
        '''
        listPeer 返回列表
        {
            "rtn":0,
            "peerList": [{
                "category": "",
                "status": 0,
                "name": "GUNNER_HOME",
                "vodPort": 43566,
                "company": "XUNLEI_MIPS_BE_MIPS32",
                "pid": "8498352EB4F5208X0001",
                "lastLoginTime": 1412053233,
                "accesscode": "",
                "localIP": "",
                "location": "\u6d59\u6c5f\u7701  \u8054\u901a",
                "online": 1,
                "path_list": "C:/",
                "type": 30,
                "deviceVersion": 22083310
            }]
        }
        '''

        params = {
            'type': 0,
            'v': DEFAULT_V,
            'ct': 2
        }
        res = self._get('listPeer', params=params)
        return res['peerList']

    def get_default_task_list(self):
        peer_list = self.get_remote_peer_list()
        if len(peer_list) == 0:
            return []
        default_peer = peer_list[0]
        self.pid = default_peer['pid']
        return self.get_remote_task_list(self.pid)

    def get_remote_task_list(
            self, peer_id, list_type=ListType.downloading, pos=0, number=10):
        '''
        list 返回列表
        {
            "recycleNum": 0,
            "serverFailNum": 0,
            "rtn": 0,
            "completeNum": 34,
            "sync": 0,
            "tasks": [{
                "failCode": 15414,
                "vipChannel": {
                    "available": 0,
                    "failCode": 0,
                    "opened": 0,
                    "type": 0,
                    "dlBytes": 0,
                    "speed": 0
                },
                "name": "Blablaba",
                "url": "magnet:?xt=urn:btih:5DF6B321CCBDEBE1D52E8E15CBFC6F002",
                "speed": 0,
                "lixianChannel": {
                    "failCode": 0,
                    "serverProgress": 0,
                    "dlBytes": 0,
                    "state": 0,
                    "serverSpeed": 0,
                    "speed": 0
                },
                "downTime": 0,
                "subList": [],
                "createTime": 1412217010,
                "state": 8,
                "remainTime": 0,
                "progress": 0,
                "path": "/tmp/thunder/volumes/C:/TDDOWNLOAD/",
                "type": 2,
                "id": "39",
                "completeTime": 0,
                "size": 0
            },
            ...
            ]
        }
        '''

        params = {
            'pid': peer_id,
            'type': list_type,
            'pos': pos,
            'number': number,
            'needUrl': 1,
            'v': DEFAULT_V,
            'ct': DEFAULT_CT
        }
        res = self._get('list', params=params)
        return res['tasks']

    def check_url(self, pid, url_list):
        '''
        urlCheck 返回数据
        {
            "rtn": 0,
            "taskInfo": {
                "failCode": 0,
                "name": ".HDTVrip.1024X576.mkv",
                "url": "ed2k://|file|%E6%B0%",
                "type": 1,
                "id": "0",
                "size": 505005442
            }
        }
        '''
        task_list = []
        for url in url_list:
            params = {
                'pid': pid,
                'url': url,
                'type': 1,
                'v': DEFAULT_V,
                'ct': DEFAULT_CT
            }
            res = self._get('urlCheck', params=params)

            if res['rtn'] == 0:
                task_info = res['taskInfo']
                task_list.append({
                    'url': task_info['url'],
                    'name': task_info['name'],
                    'filesize': task_info['size'],
                    'gcid': '',
                    'cid': ''
                })
            else:
                print(
                    'url [%s] check failed, code:%s.',
                    url,
                    task_info['failCode']
                )

        return task_list

    def add_urls_to_remote(self, pid, path='C:/TDDOWNLOAD/', url_list=[]):
        task_list = []
        for url in url_list:
            task = resolve_url(url)
            if task == {}:
                logger.info('Invalid URL:%s', url)
                continue
            else:
                task_list.append(task)
        return self.add_tasks_to_remote(pid, path, task_list)

    def add_tasks_to_remote(self, pid, path='C:/TDDOWNLOAD/', task_list=[]):
        '''
        post data:
        {
            "path":"C:/TDDOWNLOAD/",
            "tasks":[{
                "url":"ed2k://|file|%E6%B0%B8%E6%81%92.Forever...",
                "name":"永恒.Forever.S01E02.中英字幕.WEB-HR.mkv",
                "gcid":"",
                "cid":"",
                "filesize":512807020
            }]
        }

        return data:
        {
            "tasks": [{
                "name": "\u6c38\u6052.Fore76.x264.mkv",
                "url": "ed2k://|file|%E6%B0%B8%E6%81%92",
                "result": 202,
                "taskid": "48",
                "msg": "repeate_taskid:48",
                "id": 1
            }],
            "rtn": 0
        }
        '''

        if len(task_list) == 0:
            return []

        params = {
            'pid': pid,
            'v': DEFAULT_V,
            'ct': DEFAULT_CT,
        }

        data = {
            'path': path,
            'tasks': task_list
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = json.dumps(data)
        data = quote(data)
        data = 'json=' + data

        res = self._post(
            'createTask',
            params=params,
            data=data,
            headers=headers
        )

        return res

    def delete_tasks_by_task_infos(self, pid, task_infos, recycle=True,
                                   del_file=True):

        if len(task_infos) == 0:
            return []

        del_tasks = []
        for t in task_infos:
            del_tasks.append(t['id'] + '_' + str(t['state']))
        del_tasks_string = ','.join(del_tasks)
        params = {
            'pid': pid,
            'tasks': del_tasks_string,
            'recycleTask': 1 if recycle else 0,
            'deleteFile': 'true' if del_file else 'false'
        }

        res = self._get('del', params=params)

        return res

    def delete_all_tasks_in_recycle(self, pid):
        params = {
            'pid': pid,
            'tasks': '-1_64',
            'recycleTask': 0,
            'deleteFile': 'true'
        }

        res = self._get('del', params=params)

        return res
