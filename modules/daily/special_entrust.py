import time

from common import ocr, stage, image
from modules.baas import home

entrust_position = {
    'cn': {'jdfy': (962, 270), 'xyhs': (962, 410)},
    'jp': {'jdfy': (950, 200), 'xyhs': (950, 310)},
    'intl': {'jdfy': (950, 200), 'xyhs': (950, 310)},
}
wanted_lv_position = {
    1: (1116, 185), 2: (1116, 285), 3: (1116, 385), 4: (1116, 485), 5: (1116, 585),
    6: (1116, 330), 7: (1116, 430), 8: (1116, 530), 9: (1116, 630),
}
se_lv_position = {
    'cn': {
        1: (1116, 185), 2: (1116, 285), 3: (1116, 385), 4: (1116, 485), 5: (1116, 585), 6: (1116, 666),
        7: (1116, 427), 8: (1116, 526), 9: (1116, 630),
    },
    'jp': {
        1: (1116, 185), 2: (1116, 285), 3: (1116, 385), 4: (1116, 485), 5: (1116, 585), 6: (1116, 666),
        7: (1116, 185), 8: (1116, 285), 9: (1116, 385), 10: (1116, 485), 11: (1116, 585), 12: (1116, 666),
        13: (1116, 625),
    },
    'intl': {
        1: (1116, 185), 2: (1116, 285), 3: (1116, 385), 4: (1116, 485), 5: (1116, 585), 6: (1116, 330),
        7: (1116, 185), 8: (1116, 285), 9: (1116, 385), 10: (1116, 485), 11: (1116, 585), 12: (1116, 666),
    }
}
fns = {
    'special_entrust': ['jdfy', 'xyhs'],
    'wanted': ['gjgl', 'smtl', 'jt']
}


def to_menu(self):
    # 等待加载
    if self.tc['task'] == 'special_entrust':
        to_special(self)
    else:
        to_wanted(self)


def to_wanted(self):
    pos = {
        'home_student': (1200, 573),  # 首页->业务区
        'normal_task_menu': (745, 450),  # 业务区->通缉悬赏
        'normal_task_task-info-window': (60, 40),  # 任务信息->关闭
        'wanted_stage-list': (60, 40)  # 关卡列表->返回
    }
    home.to_menu(self, 'wanted_menu', pos)


def to_special(self):
    pos = {
        'home_student': (1200, 573),  # 首页->业务区
        'normal_task_menu': (730, 537),  # 业务区->特殊委托
        'normal_task_task-info-window': (60, 40),  # 任务信息->关闭
        'wanted_stage-list': (60, 40)  # 关卡列表->返回
    }
    home.to_menu(self, 'special_entrust_menu', pos)


def start(self):
    # 回到首页
    home.go_home(self)
    # 选择委托
    choose_entrust(self, entrust_position)
    # 回到首页
    home.go_home(self)


def choose_entrust(self, position):
    for fn in fns[self.tc['task']]:
        tk = self.tc[fn]
        if not tk['enable']:
            continue
        # 等待加载
        to_menu(self)
        # 选择委托
        self.click(*position[self.game_server][fn])
        # 等待加载 关卡列表
        image.compare_image(self, 'wanted_stage-list')
        # 滑动屏幕
        stage.screen_swipe(self, tk['stage'], 6, 12)
        # 点击关卡
        self.click(*get_lv_position(self, tk['stage']))
        # 确认扫荡
        rst = stage.confirm_scan(self, tk['stage'], tk['count'], 9)
        if rst == 'return':
            return


def get_lv_position(self, lv):
    if self.tc['task'] == 'special_entrust':
        return se_lv_position[self.game_server][lv]
    return wanted_lv_position[lv]
