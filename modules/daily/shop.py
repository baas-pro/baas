import time

from common import ocr, stage, image, color
from modules.baas import home

shop_position = {
    'general': (150, 150), 'arena': (150, 380)
}

goods_position = {
    1: (650, 200), 2: (805, 200), 3: (960, 200), 4: (1110, 200),
    5: (650, 460), 6: (805, 460), 7: (960, 460), 8: (1110, 460),
    9: (650, 160), 10: (805, 160), 11: (960, 160), 12: (1110, 160),
    13: (650, 420), 14: (805, 420), 15: (960, 420), 16: (1110, 420),
}


def start(self):
    if self.game_server != 'cn':
        return self.logger.critical('外服此功能待开发...')
    # 回到首页
    home.go_home(self)
    # 点击商店
    self.double_click(821, 651)
    # 等待商店页面加载
    image.compare_image(self, 'shop_menu')
    # 购买商品
    buy_goods(self)
    # 回到首页
    home.go_home(self)


def refresh_shop(self, shop):
    """
    刷新商店
    """
    need_count = shop['count']
    purchased_count = 4 - calc_surplus_count(self)
    # 次数已满
    if need_count <= purchased_count:
        # 关闭购买弹窗
        home.click_house_under(self)
        return False
    # 点击购买
    self.click(765, 460, False)
    return True


def calc_surplus_count(self):
    """
    计算剩余购买次数,这里必须用图片匹配才能精准,用文字识别小数字必出bug
    """
    self.click(945, 659, False)
    # 等待确认购买加载
    if not image.compare_image(self, 'shop_confirm', 10):
        # 未能加载还剩0次
        return 0
    for i in range(3, 0, -1):
        if image.compare_image(self, 'shop_buy{0}'.format(i), 0):
            return i
    return 0


def buy_goods(self):
    """
    刷新并购买商品
    """
    time.sleep(0.5)
    for shop in self.tc['config']:
        if not shop['enable']:
            continue
        self.double_click(*shop_position[shop['shop']], False)
        start_buy(self, shop)
        while refresh_shop(self, shop):
            start_buy(self, shop)


def start_buy(self, shop):
    """
    开始购买商品
    """
    # 选择商品
    choose_goods(self, shop['goods'])

    if not ocr.screenshot_check_text(self, '选择购买', (1116, 645, 1213, 676), 0):
        self.logger.info("没有选中道具")
        return

    # 检查是否可以购买
    if not color.check_rgb_similar(self, (1108, 657, 1109, 658), (68, 229, 249)):
        self.logger.info("货币不足，无法购买")
        return

    # 点击选择购买
    self.click(1164, 660, False)

    # 等待确认购买页面
    color.wait_rgb_similar(self, (700, 500, 701, 501), (75, 233, 246))

    # 确认购买
    self.click(700, 500, False)

    # 关闭获得奖励
    stage.close_prize_info(self, True)


def choose_goods(self, goods):
    # todo 商品渲染需要时间...
    time.sleep(0.5)
    goods = sorted(goods)
    self.logger.warning("开始点击所需商品")
    swipe = False
    for g in goods:
        if g > 8 and not swipe:
            stage.screen_swipe(self, g, 8, reset=False, f=(933, 605, 933, 0, 0.1))
            swipe = True
        # 点击商品,防止太快点不到
        time.sleep(0.2)
        self.click(*goods_position[g], False)
