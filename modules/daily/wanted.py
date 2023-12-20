from common import image
from modules.baas import home
from modules.daily import special_entrust

x = {
}
entrust_position = {
    'cn': {'gjgl': (950, 270), 'smtl': (950, 415), 'jt': (950, 550)},
    'jp': {'gjgl': (950, 200), 'smtl': (950, 310), 'jt': (950, 420)},
    'intl': {'gjgl': (950, 200), 'smtl': (950, 310), 'jt': (950, 420)},
}


def start(self):
    # 回到首页
    home.go_home(self)
    # 选择委托
    special_entrust.choose_entrust(self, entrust_position)
    # 回到首页
    home.go_home(self)
