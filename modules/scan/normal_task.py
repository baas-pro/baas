import time

from common import ocr, color, stage, image
from modules.baas import home
from modules.scan import hard_task

normal_position = {
    1: (1120, 240), 2: (1120, 340), 3: (1120, 440), 4: (1120, 540), 5: (1120, 616), 6: (1120, 569)
}


def to_choose_region(self):
    pos = {
        'home_student': (1200, 573),  # 首页->业务区
        'normal_task_menu': (816, 263),  # 业务区->任务
    }
    home.to_menu(self, 'normal_task_choose-region', pos)


def open_task_info_window(self, task_x):
    pos = {
        'normal_task_choose-region': task_x
    }
    image.detect(self, 'normal_task_task-info-window', pos)


def start(self):
    # 回到首页
    home.go_home(self)
    # 到选择区域页面
    to_choose_region(self)

    change_task(self)
    # 开始扫荡
    start_scan(self)

    # 回到首页
    home.go_home(self)


def change_task(self):
    # 困难任务
    if 'hard_task' in self.tc['task']:
        while not color.check_rgb(self, (1000, 150), (198, 66, 66)):
            self.click(1062, 154)
            time.sleep(self.bc['baas']['base']['ss_rate'])
        return
    # 普通任务
    while not color.check_rgb(self, (700, 150), (44, 65, 86)):
        self.click(803, 156)
        time.sleep(self.bc['baas']['base']['ss_rate'])


def start_scan(self):
    for tk in stage.stage_convert(self.tc['scan']['stage']):
        # 选择区域
        choose_region(self, tk['region'])
        if self.tc['task'] == 'hard_task':
            # 点击入场
            open_task_info_window(self, hard_task.hard_position[tk['stage']])
        else:
            # 不是国服需要重置关卡顺序
            stage.screen_swipe(self, tk['stage'], 7, reset=self.game_server != 'cn')
            # 点击入场
            open_task_info_window(self, normal_position[tk['stage']])
        # 确认扫荡
        rst = stage.confirm_scan(self, tk['stage'], tk['count'], 99)
        if rst == 'return':
            return


def choose_region(self, region):
    try:
        cu_region = int(ocr.screenshot_get_text(self, (122, 178, 163, 208), self.ocrNum))
    except Exception as e:
        cu_region = 0
    if cu_region == region:
        return
    if cu_region > region:
        self.click(40, 360, False, cu_region - region, 0.1)
    else:
        self.click(1245, 360, False, region - cu_region, 0.1)
    return choose_region(self, region)
