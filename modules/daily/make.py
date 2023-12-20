import time

from fuzzywuzzy import fuzz

from common import ocr, stage, color, image
from modules.baas import home

make_position = {
    1: (975, 279), 2: (975, 410), 3: (975, 551)
}
priority_position = {
    1: (174, 552), 2: (303, 527), 3: (414, 473), 4: (505, 388), 5: (569, 275)
}


def start(self):
    if self.game_server != 'cn':
        return self.logger.critical('外服此功能待开发...')
    # 回到首页
    home.go_home(self)
    # 去制造页面
    image.detect(self, 'make_menu', {'home_student': (701, 645)})
    # 开始制造
    init_make(self)
    # 回到首页
    home.go_home(self)


def init_make(self):
    """
    初始化制造
    @param self:
    @return:
    """
    pos = {
        'make_receive': (receive_prize, (self,)),  # 立即领取
        'make_immediately': (make_immediately, (self,)),  # 立即加速
    }
    state = image.detect(self, 'make_start-make', pos)
    if state == 'make_start-make':
        start_make(self)


def start_make(self):
    for i in range(self.tc['config']['count']):
        # 点击制造 -> 全部查看
        image.detect(self, 'make_view-all', cl=(975, 264))
        # 选择石头
        if not choose_tone(self):
            break
        # 第一阶段启动 -> 等待制造页面加载
        image.detect(self, (('make_workshop', 30),), cl=(1114, 653))

        # 选择物品
        choose_item(self)

        # 点击选择节点 -> 开始制造
        self.click(1121, 650, False)
        image.detect(self, 'make_start-make2')

        # 点击开始制造 -> 菜单
        image.detect(self, 'make_menu', cl=(1116, 652))
        # 立即加速
        make_immediately(self)


def use_acc(self):
    """
    使用加速券
    @param self:
    """
    # 点击使用加速 -> 弹出立即完成
    self.click(1128, 278, False)
    image.detect(self, 'make_confirm-acc')
    # 点击确认
    self.click(771, 478, False)


def receive_prize(self):
    """
    领取奖励
    @param self:
    """
    # 点击领取
    self.click(1122, 275)
    # 关闭奖励
    stage.close_prize_info(self)


def make_immediately(self):
    """
    立即加速
    @param self:
    @return:
    """
    if 'use_acc_ticket' in self.tc['config'] and not self.tc['config']['use_acc_ticket']:
        self.logger.error("当前配置为不使用加速券...")
        return True
    use_acc(self)
    receive_prize(self)


def choose_item(self):
    """
    根据优先级选择制造物品
    @param self:
    @return:
    """
    time.sleep(3)
    self.click(445, 552, False)
    # 选择优先级最高物品
    check_index = get_high_priority(self)
    # 选择最高优先级物品
    self.click(*priority_position[check_index + 1])
    return check_index


def get_high_priority(self):
    """
    计算优先级最高的物品
    @param self:
    @return: 优先级最高索引
    """
    # 遍历查看所有物品
    items = []
    for i, position in priority_position.items():
        self.click(*position, False)
        item = ocr.screenshot_get_text(self, (720, 204, 1134, 269))
        items.append(item)
    # 计算优先级最高的物品
    check_item = None
    check_index = 0
    for i, item in enumerate(items):
        for priority in self.tc['config']['priority']:
            ratio = fuzz.ratio(item, priority)
            if ratio < 80:
                continue
            if not check_item or \
                    self.tc['config']['priority'].index(priority) < self.tc['config']['priority'].index(check_item):
                check_item = priority
                check_index = i
    return check_index


def choose_tone(self):
    """
    选择石头
    @param self:
    @return:
    """
    # 点击拱心石
    time.sleep(1)
    self.click(908, 199, False)
    time.sleep(1)
    # 检查是否满足
    if color.check_rgb_similar(self, (995, 631, 996, 632), (61, 219, 250)):
        return True
    # 点击拱心石碎片
    self.click(769, 200, False, 10)
    time.sleep(1)
    return color.check_rgb_similar(self, (995, 631, 996, 632), (61, 219, 250))
