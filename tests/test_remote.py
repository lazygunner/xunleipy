import unittest
import json

from httmock import urlmatch, HTTMock, response
from six.moves.urllib.parse import unquote

from xunleipy.remote import XunLeiRemote


@urlmatch(netloc=r'(.*\.)?xunlei\.com')
def xunlei_mock(url, request):

    headers = {}
    content = {}
    if url.path == '/check':
        headers = {
            'Set-Cookie': 'check_result=0:!tst;'
        }
    elif url.path == '/sec2login/':
        headers = {
            'Set-Cookie': 'userid=test1234;'
        }
    elif url.path == '/createTask':
        body = request.body
        body = unquote(body)[5:]
        task_list = json.loads(body)['tasks']
        tasks = []
        for task in task_list:
            tasks.append({
                'name': task['name'],
                'url': task['url'],
                'taskid': 1,
                'result': 0,
                'msg': '',
                'id': 1
            })
        content = {
            'rtn': 0,
            'tasks': tasks
        }
    elif url.path == '/del':
        content = {
            'rtn': 0,
            'tasks': [
                {'msg': '', 'id': '50', 'result': 0},
                {'msg': '', 'id': '51', 'result': 0}
            ]
        }

    return response(200, content, headers, None, 5, request)


class LoginTest(unittest.TestCase):

    def test_create_task_success(self):
        with HTTMock(xunlei_mock):
            u = 'testname'
            p = 'testpass'
            xlr = XunLeiRemote(u, p)

            res = xlr.add_tasks_to_remote(
                "8498352EB4F5208X0001",
                task_list=[{
                    'url': 'ed2k://|file|=cu6wpmujve4rbsv4xdqd2r5ogkmgksgo|/',
                    'gcid': '',
                    'cid': '',
                    'name': '.WEB-HR.AAC.1024x576.x264.mkv',
                    'filesize': 514276262
                }]
            )

            data = res
            self.assertEqual(data['rtn'], 0)
            self.assertTrue('taskid' in data['tasks'][0])

    def test_create_tasks_by_urls_success(self):
        with HTTMock(xunlei_mock):
            u = 'testname'
            p = 'testpass'
            xlr = XunLeiRemote(u, p)
            url_list = [
                    'ed2k://|file|=cu6wpmujve4rbsv4xdqd2r5ogkmgksgo|1234|as/',
                    'movietrailers.apple.com/movies/wb/prisoners/prisoners-tlr1_h720p.mov'  # NOQA
                ]

            res = xlr.add_urls_to_remote(
                "8498352EB4F5208X0001",
                url_list=url_list
            )

            data = res
            self.assertEqual(data['rtn'], 0)
            self.assertTrue('taskid' in data['tasks'][0])
            for task in data['tasks']:
                self.assertTrue(task['url'] in url_list)


class DeleteTestCase(unittest.TestCase):

    def test_delete_tasks_by_task_infos(self):
        with HTTMock(xunlei_mock):
            u = 'testname'
            p = 'testpass'
            xlr = XunLeiRemote(u, p)
            res = xlr.delete_tasks_by_task_infos(xlr.pid, [])

            for data in res:
                self.assertTrue('result' in data)
                self.assertEqual(data['result'], 0)

    def test_delete_all_tasks_in_recycle(self):
        with HTTMock(xunlei_mock):
            u = 'testname'
            p = 'testpass'
            xlr = XunLeiRemote(u, p)
            res = xlr.delete_all_tasks_in_recycle(xlr.pid)

            self.assertEqual(res['rtn'], 0)
            self.assertTrue('tasks' in res)

            for data in res['tasks']:
                self.assertTrue('result' in data)
                self.assertEqual(data['result'], 0)


if __name__ == '__main__':
    unittest.main()
