import time

from common import image


def only_start(self):
    # 重启应用
    pkg = self.bc['baas']['base']['package']
    self.log_title("开始打开BA")
    self.d.app_stop(pkg)
    try:
        if self.game_server == 'intl':
            self.d.app_start(pkg, 'com.nexon.bluearchive.MxUnityPlayerActivity')
        else:
            self.d.app_start(pkg)
    except Exception as e:
        self.logger.critical("启动游戏失败,默认为国服官包。如果你是其他服务器，请点击菜单Baas->Baas设置 选择对应游戏服务器！")
        self.exit(e)
    # 强制等待
    time.sleep(8)


def start(self):
    only_start(self)
    start_fn = {
        'cn': start_cn,
        'intl': start_intl,
        'jp': start_cn
    }
    start_fn[self.game_server](self)


def start_cn(self):
    pos = {
        'restart_menu': (624, 373),  # 首页菜单
        'restart_maintain': (640, 500),  # 维护
        'restart_update': (769, 501),  # 更新
        'home_news': (1142, 104),  # 公告
    }
    image.detect(self, 'home_student', pos, cl=(1233, 11))


def start_intl(self):
    pos = {
        'restart_menu': (624, 373),  # 首页菜单
        'restart_update': (769, 501),  # 更新
        'restart_news': (1232, 42),  # 重启公告新闻
        'home_news': (1142, 104),  # 公告
        'home_news-intl': (1226, 54),  # 国际服公告
    }
    end = image.detect(self, ('home_student', 'restart_maintain'), pos, cl=(1233, 11))
    if end == 'restart_maintain':
        self.click(640, 500)
        self.logger.info("游戏维护中,1分钟后重启游戏")
        time.sleep(60)
        return start_intl(self)
