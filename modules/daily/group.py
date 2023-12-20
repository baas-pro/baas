from common import image
from modules.baas import home


def start(self):
    # 回到首页
    home.go_home(self)
    to_group(self)
    home.go_home(self)


def to_group(self):
    pos = {
        'home_student': (578, 648),  # 首页->小组
        'group_sign-up-confirm': (644, 491),  # 签到奖励
    }
    home.to_menu(self, 'group_menu', pos)
