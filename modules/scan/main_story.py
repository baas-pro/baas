import time

import cv2
import numpy as np

from common import color, stage, image
from modules.baas import home

story_position = {
    1: (350, 345), 2: (950, 345)
}


def start(self):
    if self.game_server != 'cn':
        return self.logger.critical('外服此功能待开发...')
    # 回到首页
    home.go_home(self)
    # 点击业务区
    self.double_click(1195, 576)
    # 等待业务区页面加载
    image.compare_image(self, 'home_bus', mis_fu=self.click, mis_argv=(1195, 576))

    # 点击故事
    self.click(1093, 273)
    image.compare_image(self, 'main_story_story')

    # 点击主线故事
    self.click(248, 355)
    image.compare_image(self, 'main_story_menu')

    # 选择故事
    select_story(self)

    # 开始剧情
    start_admission(self)

    # 回到首页
    home.go_home(self)


def skip_polt(self):
    """
    跳过剧情
    @param self:
    @return:
    """
    while True:
        # 等待菜单出现
        image.compare_image(self, 'cm_skip-menu')
        # 点击菜单
        self.click(1204, 40, False)
        # 点击>>
        self.click(1210, 120, False, 1, 1)
        # 等待跳过加载
        if image.compare_image(self, 'cm_confirm', 3):
            # 点击跳过
            self.click(770, 521, False)
            return


def start_admission(self):
    # 检查是否通关
    if image.compare_image(self, 'main_story_clearance', 0, 10):
        return
    # 检查是否通关
    if image.compare_image(self, 'main_story_current-clearance', 0, 10):
        return
    # 查看第一个是否锁住了
    if image.compare_image(self, 'main_story_first-lock', 10, 20):
        # 锁住了点第二个任务
        self.click(1114, 339, False)
    else:
        self.click(1114, 237, False)
    # 等待剧情信息加载
    image.compare_image(self, 'main_story_plot-info')

    is_fight = image.compare_image(self, 'main_story_plot-fight', 0, 10)

    # 进入剧情
    self.click(641, 516, False)
    # 跳过剧情
    skip_polt(self)

    if is_fight:
        # 等待部队出击页面加载
        image.compare_image(self, 'main_story_plot-attack')
        time.sleep(3)
        # 点击出击
        self.click(1158, 655, False)
        auto_fight(self)
        # 跳过剧情
        skip_polt(self)

    # 关闭获得奖励
    stage.close_prize_info(self)
    time.sleep(2)
    # 再次递归
    return start_admission(self)


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
    time.sleep(8)
    change_acc_auto(self)
    self.logger.warning("检查自动释放技能完成")


def select_story(self):
    """
    选择故事
    @param self:
    @return:
    """
    story = self.tc['config']['story']
    quotient = (story - 1) // 2
    self.click(1246, 335, False, quotient, 0.5)
    zb = 1 if story % 2 == 1 else 2
    image.compare_image(self, 'main_story_choose-plot', mis_fu=self.click, mis_argv=(*story_position[zb], False))
