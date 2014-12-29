
def _md5(s):
    import hashlib
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def get_password_hash(password, verify_code):
    return _md5(_md5(_md5(password)) + verify_code.upper())


def resolve_url(url):
    from six.moves.urllib.parse import urlsplit
    url_data = urlsplit(url)
    url_dict = dict(url_data._asdict())
    task_dict = {}
    scheme = url_dict['scheme']
    if scheme == 'ed2k':
        contents = url_dict['netloc'].split('|')
        if len(contents) < 5:
            return task_dict
        else:
            task_dict['url'] = url
            task_dict['name'] = contents[2]
            task_dict['filesize'] = contents[3]
            task_dict['gcid'] = ''
            task_dict['cid'] = ''
    elif scheme in ['http', 'https']:
        path = url_dict['path']
        contents = path.split('/')
        if len(path) < 2 or path == '/':
            return {}
        else:
            task_dict['url'] = url
            task_dict['name'] = contents[-1]
            task_dict['filesize'] = 0
            task_dict['gcid'] = ''
            task_dict['cid'] = ''

    return task_dict
