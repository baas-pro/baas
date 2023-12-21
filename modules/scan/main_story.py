import time

import cv2
import numpy as np

from common import color, stage, image
from modules.baas import home
from modules.reward import momo_talk

story_position = {
    1: (350, 345), 2: (950, 345)
}


def to_main_story(self):
    pos = {
        'home_student': (1200, 573),  # 首页->业务区
        'home_bus': (1111, 286),  # 业务区->故事
        'main_story_story': (248, 355),  # 故事->主线故事
    }
    home.to_menu(self, 'main_story_menu', pos)


def to_choose_story(self):
    pos = {
        'fight_fail': (647, 655)
    }
    image.detect(self, 'main_story_choose-plot', pos)


def start(self):
    if self.game_server != 'cn':
        return self.logger.critical('外服此功能待开发...')
    # 回到首页
    home.go_home(self)

    # 到主线故事
    to_main_story(self)

    # 选择故事
    select_story(self)

    # 开始剧情
    start_admission(self)

    # 回到首页
    home.go_home(self)


def check_finish(self):
    ends = (
        'main_story_clearance',  # 检查是否通关
        'main_story_current-clearance'  # 检查是否通关
    )
    return image.detect(self, ends, retry=3)


def start_admission(self):
    if check_finish(self) is not None:
        self.logger.error("剧情已经完成了")
        return

    # 查看第一个是否锁住了
    cl = (1114, 237)
    if image.compare_image(self, 'main_story_first-lock', 10, 20):
        # 锁住了点第二个任务
        cl = (1114, 339)
    # 等待剧情信息加载
    image.detect(self, 'main_story_plot-info', cl=cl, ss_rate=2)

    is_fight = image.compare_image(self, 'main_story_plot-fight', 0, 10)

    # 进入剧情
    self.click(641, 516, False)
    # 跳过剧情
    momo_talk.skip_plot(self)

    if is_fight:
        # 等待部队出击加载
        image.detect(self, 'fight_force-attack')
        # 点击出击,直到没有部队出击
        image.compare_image(self, 'fight_force-attack', mis_fu=self.click, mis_argv=(1163, 658), rate=1, n=True)
        auto_fight(self)
        time.sleep(30)
        # 跳过剧情
        end = skip_main_story_plot(self)
        # 作战失败
        if end == 'fight_fail':
            to_choose_story(self)
            return start_admission(self)
    else:
        # 关闭获得奖励
        stage.close_prize_info(self)
    time.sleep(3)
    # 再次递归
    return start_admission(self)


def skip_main_story_plot(self):
    pos = {
        'fight_pass-confirm': (1170, 666),  # 剧情通关
        'momo_talk_begin-relationship': (920, 568),
        'momo_talk_menu': (1205, 42),
        'momo_talk_skip': (1212, 116),
        'main_story_get-prize': (644, 634),  # 确认奖励
    }
    # 剧情这里有三种情况
    # 1. 打完架 -> 直接结束(要确认奖励) -> main_story_choose-plot
    # 2. 打完架 -> 进入剧情(要跳过剧情) -> momo_talk_confirm-skip
    # 3. 打完架 -> 作战失败(要重新开始) -> fight_fail
    ends = ('momo_talk_confirm-skip', 'fight_fail', 'main_story_choose-plot')
    end = image.detect(self, ends, pos)
    if end == 'fight_fail':
        return end
    elif end == 'momo_talk_confirm-skip':
        # 确认跳过
        self.click(770, 516, False)
        stage.close_prize_info(self, 15)


def change_acc_auto(self):  # 战斗时开启3倍速和auto
    img1 = cv2.cvtColor(np.array(self.d.screenshot()), cv2.COLOR_RGB2BGR)
    auto_r_ave = int(img1[677][1171][0]) // 2 + int(img1[677][1246][0]) // 2
    if 190 <= auto_r_ave <= 230:
        self.logger.info("CHANGE MANUAL to auto")
        self.click(1215, 678)
    elif 0 <= auto_r_ave <= 60:
        self.logger.info("AUTO")
    else:
        self.logger.warning("can't identify auto button")
    acc_r_ave = int(img1[625][1196][0]) // 3 + int(img1[625][1215][0]) // 3 + int(img1[625][1230][0]) // 3
    if 250 <= acc_r_ave <= 260:
        self.logger.info("CHANGE acceleration phase from 2 to 3")
        self.click(1215, 625)
    elif 0 <= acc_r_ave <= 60:
        self.logger.info("ACCELERATION phase 3")
    elif 140 <= acc_r_ave <= 180:
        self.logger.info("CHANGE acceleration phase from 1 to 3")
        self.click(1215, 625, count=2)
    else:
        self.logger.warning("CAN'T DETECT acceleration BUTTON")


def auto_fight(self):
    time.sleep(3)
    stage.wait_loading(self)
    time.sleep(10)
    change_acc_auto(self)
    self.logger.warning("检查自动释放技能完成")


def select_story(self):
    """
    选择故事
    @param self:
    @return:
    """
    self.double_click(36, 361, False)
    time.sleep(0.5)
    story = self.tc['config']['story']
    quotient = (story - 1) // 2
    self.click(1246, 335, False, quotient, 0.5)
    zb = 1 if story % 2 == 1 else 2
    image.compare_image(self, 'main_story_choose-plot', mis_fu=self.click, mis_argv=(*story_position[zb], False))
