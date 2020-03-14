import requests
import time
import os
from hashlib import md5
from urllib.parse import urlencode
from urllib.parse import urljoin
from multiprocessing import Pool
from config import *

requests.packages.urllib3.disable_warnings()


class JiePai(object):
    def __init__(self):
        self.base_url = 'https://www.toutiao.com/search_content/?'

    def get_page(self, offset):
        params = {
            'aid': '24',
            'app_name': 'web_search',
            'offset': str(offset),
            'format': 'json',
            'keyword': '街拍',
            'autoload': 'true',
            'count': '20',
            'en_qc': '1',
            'cur_tab': '1',
            'from': 'search_tab',
            'pd': 'synthesis',
            'timestamp': str(int(time.time() * 1000))
        }
        headers = {
            'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        url = self.base_url + urlencode(params)
        resp = requests.get(url=url, headers=headers, verify=False)
        try:
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            print(e.args)
            return None

    def get_images(self, json):
        if json.get('data'):
            for item in json.get('data'):
                title = item.get('title')
                images = item.get('image_list')
                if images:
                    for image in images:
                        yield {
                            'title': title,
                            'image': urljoin('http:', image.get('url'))
                        }
                else:
                    yield None

    def save_image(self, item):
        if item:
            if not os.path.exists(item.get('title')):
                os.mkdir(item.get('title'))
            try:
                response = requests.get(url=item.get('image'))
                if response.status_code == 200:
                    file_path = '{0}/{1}.{2}'.format(item.get('title'), md5(response.content), 'jpg')
                    if not os.path.exists(file_path):
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                    else:
                        print('Already Download', file_path)
            except requests.ConnectionError:
                print('Failed to Save Image')

    def main(self, offset):
        json = self.get_page(offset)
        for item in self.get_images(json):
            print(item)
            self.save_image(item)


if __name__ == '__main__':
    jp = JiePai()
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(jp.main, groups)
    pool.close()
    pool.join()
