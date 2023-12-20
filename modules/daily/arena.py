import time

from common import ocr, color, stage, image
from modules.baas import home

finish_seconds = 55


def to_arena(self):
    pos = {
        'home_student': (1200, 573),  # 首页->业务区
        'home_bus': (1080, 570),  # 首页->竞技场
    }
    home.to_menu(self, 'arena_menu', pos)


def do_fight(self):
    # 到达作战对手页面
    pos = {
        'arena_menu': (769, 251),  # 竞技场->点击对手
    }
    image.detect(self, 'arena_war-force', pos)
    # 到达编队页面
    pos = {
        'arena_war-force': (646, 571),  # 作战对手->编队
    }
    image.detect(self, 'fight_edit-attack-force', pos)


def start(self):
    # 回到首页
    home.go_home(self)

    to_arena(self)

    # 开始战斗
    start_fight(self)

    # 回到首页
    home.go_home(self)


def get_prize(self):
    self.logger.warning("开始领取每日奖励")
    if color.check_rgb_similar(self, (320, 400, 321, 401)):
        # 领取时间奖励
        self.click(353, 385)
        # 关闭奖励
        stage.close_prize_info(self)
    if color.check_rgb_similar(self, (330, 480, 331, 481)):
        # 领取挑战奖励
        self.click(348, 465)
        # 关闭奖励
        stage.close_prize_info(self)


def start_fight(self, wait=False):
    # 检查余票
    time.sleep(0.5)
    if image.compare_image(self, 'arena_0-5', 0):
        self.logger.error("入场券不足")
        get_prize(self)
        return
    # 检测已有冷却
    if wait or not image.compare_image(self, 'arena_cd', 0):
        self.finish_seconds = finish_seconds
        return
    # 选择对手
    choose_enemy(self)
    do_fight(self)
    # 检查跳过是否勾选
    image.compare_image(self, 'arena_skip', 999, 20, False, self.click, (1125, 599, False), 1)

    # 出击 直到 编队页面消失
    image.compare_image(self, 'fight_edit-attack-force', threshold=10, mis_fu=self.click, mis_argv=(1163, 658), rate=1,
                        n=True)
    # 等到ID出现 一直点击页面关闭晋升弹窗
    image.detect(self, 'arena_id', cl=(1235, 82))
    start_fight(self, True)


def choose_enemy(self):
    less_level = int(self.tc['config']['less_level'])
    # 识别自己等级
    try:
        area = image.get_box(self, 'arena_my-lv')
        my_lv = float(ocr.screenshot_get_text(self, area, self.ocrNum))
    except Exception:
        my_lv = 100
    refresh = 0
    while True:
        # 超出最大次数,敌人预期等级-1
        if refresh > self.tc['config']['max_refresh']:
            less_level -= 1
            refresh = 0
            continue
        # 识别对手等级
        try:
            area = image.get_box(self, 'arena_enemy-lv')
            enemy_lv = float(ocr.screenshot_get_text(self, area, self.ocrNum))
        except Exception:
            enemy_lv = 0
        self.logger.info("我的等级{0} 对手等级 {1}".format(my_lv, enemy_lv))
        if enemy_lv + less_level <= my_lv:
            break
        # 更换对手
        self.logger.warning("开始更换对手")
        self.double_click(1158, 145)
        refresh += 1
