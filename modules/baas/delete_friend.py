import time

from common import image
from modules.baas import home


def start(self):
    if self.game_server != 'cn':
        self.logger.error("当前功能仅国服支持")
        return

    home.go_home(self)

    to_friend_manage(self)
    delete_friend(self)

    home.go_home(self)


def to_friend_manage(self):
    pos = {
        'home_student': (1225, 40),  # 首页-> 右上角
        'delete_friend_sysmenu': (535, 465),  # 系统菜单 -> 好友
        'delete_friend_fri-manage': (535, 465)  # 好友管理 -> 好友列表
    }
    home.to_menu(self, 'delete_friend_menu', pos)


def delete_friend(self):
    if not image.compare_image(self, 'delete_friend_del-fri', 0):
        self.logger.warning("没有需要删除的好友")
        return
    # 点击删除好友
    self.click(1125, 260)
    image.detect(self, 'delete_friend_del-notice')
    # 点击确认
    self.click(772, 500)
    time.sleep(0.5)
    return delete_friend(self)
