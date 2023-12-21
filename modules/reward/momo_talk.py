import time

from common import stage, ocr, image, color
from modules.baas import home


def to_momo_talk(self):
    pos = {
        'home_student': (171, 148),  # 首页->桃信
        'momo_talk_student': (177, 271),  # 学生页面 -> 未读消息
    }
    home.to_menu(self, 'momo_talk_unread', pos)


def start(self):
    # 回到首页
    home.go_home(self)

    # 查看可以互动的学生
    if not color.check_rgb(self, (183, 125), (232, 68, 0)):
        self.logger.warning("没有可以互动的学生")
        return

    to_momo_talk(self)

    # 查看排序
    check_sort(self)

    # 查看第一个学生是否可以聊天
    time.sleep(0.5)
    if not color.check_rgb(self, (657, 259), (251, 71, 25)):
        home.go_home(self)
        self.logger.info("没有可以互动的学生")
        return

    # 点击第一个学生
    self.click(471, 251)
    # 开始聊天
    start_chat(self)
    # 重新桃信
    start(self)


def check_sort(self):
    """
    检查排序
    :param self:
    """
    set_unread_sort(self)
    image.compare_image(self, 'momo_talk_sort-direction', mis_fu=self.click, mis_argv=(625, 180, False), rate=0.5)


def set_unread_sort(self):
    """
    设置未读排序
    :param self:
    """
    sd = {
        'cn': [(509, 175, False), (449, 293, False), (451, 370, False)],
        'intl': [(509, 175, False), (560, 294, False), (445, 422, False)],
        'jp': [(509, 175, False), (554, 296, False), (449, 442, False)]
    }
    if not image.compare_image(self, 'momo_talk_sort-field', 0):
        position = sd[self.game_server]
        for p in position:
            self.click(*p)
            time.sleep(0.5)


def start_chat(self):
    """
    开始聊天
    :param self:
    """
    self.mm_i = 0
    while self.mm_i < 5:
        self.latest_img_array = self.get_screenshot_array()
        # 检测回复
        rst = image.find_img(self, self.latest_img_array, 'momo_talk_reply', y_add=62)
        if len(rst) > 0:
            self.logger.warning("开始回消息... ")
            self.mm_i = 0
            for r in rst:
                self.click(*r, False)
            continue
        # 检测好感故事
        rst = image.find_img(self, self.latest_img_array, 'momo_talk_likable', y_add=62)
        if len(rst) > 0:
            self.logger.warning("开始好感故事...")
            self.mm_i = 0
            for r in rst:
                self.click(*r, False)
            begin_relationship(self)
            continue
        # 检查文字是否发生变动
        check_message(self)
        # 三种情况都不满足等待0.5秒
        time.sleep(1)


def check_message(self):
    """
    检查文字是否发生变动
    :param self:
    :return:
    """
    cu_ss = image.screenshot_cut(self, (769, 181, 807, 620))
    if not hasattr(self, 'mm_prev') or image.compare_image_data(self, cu_ss, self.mm_prev, 1):
        self.mm_i += 1
        self.logger.warning(f"当前聊天内容未发生变化...{self.mm_i}")
    self.mm_prev = cu_ss


def begin_relationship(self):
    """
    开始好感故事
    :param self:
    """
    skip_plot(self)
    # 关闭奖励
    stage.close_prize_info(self, True)


def skip_plot(self):
    pos = {
        'fight_pass-confirm': (1170, 666),  # 剧情通关
        'momo_talk_begin-relationship': (920, 568),
        'momo_talk_menu': (1205, 42),
        'momo_talk_skip': (1212, 116)
    }
    end = image.detect(self, ('momo_talk_confirm-skip', 'fight_fail'), pos)
    if end == 'fight_fail':
        return end
    # 确认跳过
    self.click(770, 516, False)
