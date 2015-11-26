# -*- coding: utf-8 -*-
import hashlib
from multiprocessing.dummy import Pool as ThreadPool  # 多线程并行库
from baseClass import SettingClass, HttpBaseClass
from worker import PageWorker  # 引入控制台

class ImageContainer(object):
    def __init__(self, save_path=''):
        self.save_path = save_path
        self.container = {}
        self.md5 = hashlib.md5()
        self.thread_pool = ThreadPool(SettingClass.MAXTHREAD)
        return

    def set_save_path(self, save_path):
        self.save_path = save_path
        return

    def add(self, href):
        self.container[href] = self.create_image(href)
        return self.get_filename(href)

    def delete(self, href):
        del self.container[href]
        return

    def get_filename(self, href):
        image = self.container.get(href)
        if image:
            return image['filename']
        return ''

    def download(self, image):
        filename = image['filename']
        href = image['href']
        content = HttpBaseClass.get_http_content(url=href, timeout=SettingClass.WAITFOR_PIC)
        if not content:
            return
        with open(self.save_path + '/' + filename, 'wb') as image:
            image.write(content)
        self.delete(href)
        return

    def start_download(self):
        argv = {'func': self.download,  # 所有待存入数据库中的数据都应当是list
            'iterable': self.container, }
        PageWorker.control_center(self.thread_pool.map, argv, self.container)
        return

    def create_image(self, href):
        image = {'filename': self.get_filename(href), 'href': self.remove_http(href)}
        return image

    def remove_http(self, href):
        if href[:5] == 'https':
            href = 'http' + href[5:]
        return href

    def get_filename(self, href):
        filename = self.md5(href) + '.jpg'
        return filename

    def hash(self, string):
        self.md5.update(str(string))
        return self.md5.hexdigest()
