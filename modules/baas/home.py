import time

from common import image, stage
from common.color import detect_rgb_one_time
from modules.baas import restart


def is_home(self):
    """
    是否为首页
    """
    return image.compare_image(self, 'home_student', 0)


def go_home(self):
    """
    回到首页
    """
    self.logger.warning("开始回到首页")
    app = self.d.app_current()
    if app['package'] != self.bc['baas']['base']['package']:
        # 启动游戏
        return restart.start(self)
    # 返回首页
    if recursion_click_house(self):
        return
    # 返回首页失败启动游戏
    restart.start(self)


def to_menu(self, end, pos, cl=None):
    possible = {
        'home_news': (1142, 104),  # 公告
        'home_news-intl': (1226, 54),  # 国际服公告
        'home_store-error': (641, 501),  # 商店错误弹窗
    }
    possible.update(pos)
    image.detect(self, end, possible, cl=cl)


def click_house_under(self):
    self.double_click(1166, 66, False)


def recursion_click_house(self):
    """
    递归点击首页按钮，如果返回False则返回首页失败，反之返回首页成功
    """
    pos = {
        'home_news-intl': (1226, 54),  # 国际服公告
        'home_store-error': (6421, 501),  # 商店错误弹窗
    }
    rst = image.detect(self, 'home_student', pos, cl=(1233, 11), retry=100)
    if rst is None:
        self.logger.info("多次返回首页失败! 开始重启")
        return False
    # 在首页先点击右上角
    self.click(1233, 11, False)
    # 和妹子互动
    self.double_click(851, 262, False)
    return True
