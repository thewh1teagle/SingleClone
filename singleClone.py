#!/usr/bin/env python3

import re
import requests
import json
import argparse
import os
import pathlib
import base64

def list_all_files(user, repo, directory, ref='main'):
    files = []
    res = requests.get(f'https://api.github.com/repos/{user}/{repo}/git/trees/{branch}?recursive=1').json()
    breakpoint()
    for item in res['tree']:
        if item['type'] == 'blob': #  and item['path'].startswith(directory):
            files.append(item)
    return files

def get_path(url: str):
    if 'http' in url:
        return '/' + '/'.join(url.split('/')[3:])
    else:
        return url[ url.find('/'): ]

def repo_info(user, repo, branch, path):
    url = f'https://api.github.com/repos/{user}/{repo}/contents/{path}?ref={branch}'
    res = requests.get(url,
        headers={
            'accept': 'application/vnd.github.v3.raw',
            # 'authorization': f'token {token}', # If you are want to read "public" only, then you can ignore this line.
        }
    )
    return res.json()

def parse_url(url):
    pattern = "^[/]([^/]+)[/]([^/]+)[/]tree[/]([^/]+)[/](.*)"
    
    path = get_path(url)
    user, repo, branch, path = re.findall(pattern, path)[0]
    return {'user': user, 'repo': repo, 'branch': branch, 'path': path}



def download_file(user, repo, ref, path) -> bytes:
    url = f'https://api.github.com/repos/{user}/{repo}/contents/{path}'
    res = requests.get(url).json()
    return base64.b64decode(res['content'])

if __name__ == '__main__':
    url = "https://github.com/torvalds/linux/tree/master/Documentation/ABI/obsolete"
    user, repo, branch, path = parse_url(url).values()

    root_path = pathlib.Path(repo) / path
    # info = repo_info(user, repo, branch, path)
    # print(info)
    files = list_all_files(user, repo, '/')
    for f in files:
        path = pathlib.Path(repo) / f['path'] 
        if root_path in (pathlib.Path(repo) / f['path']).parents:
            os.makedirs(f'{repo}/{path}', exist_ok=True)
            content = download_file(user, repo, branch, f['path'])
            with open(path, 'wb') as f:
                f.write(content)

