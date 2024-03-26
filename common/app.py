import webbrowser
from common import config

version = 'v2.4.2'


def open_baas():
    ac = config.get_app_config()
    webbrowser.open_new('http://localhost:{0}?v={1}'.format(ac['port'], version))


def open_github():
    webbrowser.open_new('https://github.com/baas-pro/baas')


def open_bilibili():
    webbrowser.open_new('https://www.bilibili.com/video/BV1Dx4y1Z7nW')
