import threading
import time
from collections import defaultdict

import cv2
import numpy as np

from common import stage, ocr, image, position, color
from modules.baas import home

preset_position = {
    1: (808, 263), 2: (808, 393), 3: (808, 533), 4: (812, 393), 5: (812, 523)
}
fav_sort_position = {
    'cn': [(703, 149), (640, 270), (640, 343)],
    'intl': [(703, 149), (532, 319), (638, 392)],
    'jp': [(703, 149), (532, 319), (638, 392)],
}


def to_cafe(self):
    pos = {
        'home_student': (89, 653),  # 首页 -> 咖啡厅
        'cafe_students-arrived': (922, 189),  # 学生到访
        'cafe_inc-fav': (641, 537, 50)  # 好感提升
    }
    home.to_menu(self, 'cafe_menu', pos, cl=(923, 186))


def start(self):
    # 回到首页
    home.go_home(self)
    # 进入咖啡厅
    to_cafe(self)
    # 领取收益
    get_cafe_money(self)
    # 邀请妹子
    invite_girl(self)
    # 初始化窗口
    init_window(self)
    # 和妹子互动
    if self.tc['config']['interact_type'] == 'clear_furniture':
        empty_furniture_click_girl(self)
    else:
        drag_gift_click_girl(self)
    # 回到首页
    home.go_home(self)


def match(self, img):
    res = []
    for i in range(1, 4):
        template = image.get_img_data(self, "cafe_happy-face" + str(i))
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        locations = np.where(result >= threshold)
        for pt in zip(*locations[::-1]):
            res.append([pt[0] + template.shape[1] / 2, pt[1] + template.shape[0] / 2 + 58])
    return res


def to_gift(self):
    pos = {
        'cafe_menu': (164, 640),
        'cafe_inc-fav': (641, 537, 50)  # 好感提升
    }
    image.detect(self, 'cafe_give-gift', pos)


def shot(self):
    time.sleep(1)
    self.latest_img_array = self.get_screenshot_array()


def drag_gift_click_girl(self):
    self.d().pinch_in()
    self.d.swipe(709, 558, 709, 209, duration=0.5)
    for i in range(0, 5):
        to_gift(self)
        t1 = threading.Thread(target=shot, args=(self,))
        t1.start()
        self.d.click(131, 660)
        self.d.swipe(131, 660, 1280, 660, duration=0.5)
        t1.join()
        res = match(self, self.latest_img_array)
        self.click(1237, 573)
        for j in range(0, len(res)):
            self.click(res[j][0], min(res[j][1], 591), wait=False)

        to_cafe(self)
        if i != 4:
            self.click(68, 636)
            time.sleep(1)
            self.click(1169, 90)
            time.sleep(1)


def empty_furniture_click_girl(self):
    preset = self.tc['config']['blank_preset']
    load_preset(self, preset)
    # 收起菜单
    time.sleep(0.2)
    self.double_click(555, 622, False)
    i = 3
    while i > 0:
        click_girl_plus(self, i)
        if ocr.screenshot_check_text(self, '好感等级提升', (473, 593, 757, 644), 3):
            # 关闭好感窗口,重新开始
            self.double_click(651, 285, False)
            time.sleep(0.5)
            i = 3
            continue
        i -= 1
    # 暂开菜单
    self.click(57, 624, False)
    # 恢复玩家原有预设
    recover_preset(self, preset)


def recover_preset(self, preset):
    # 恢复玩家原有预设
    open_preset_window(self, preset)
    self.click(*preset_position[preset], False)
    confirm_load_preset(self)


def load_preset(self, preset):
    open_preset_window(self, preset)
    # 保存当前配置到配置中预设
    save_preset(self, preset)
    # 点击全部收纳
    self.click(455, 642, False, 1, 0.5)
    # 等待确认加载
    ocr.screenshot_check_text(self, '确认', (732, 482, 803, 518))
    # 确认收纳
    self.click(769, 498, False)


def open_preset_window(self, preset):
    # 等待右下角预设
    ocr.screenshot_check_text(self, '预设', (326, 656, 366, 677))
    # 点击右下角预设
    self.click(360, 640)
    # 等待预设弹窗加载
    ocr.screenshot_check_text(self, '预设', (604, 127, 678, 157))
    stage.screen_swipe(self, preset, 3, reset=False, f=(933, 586, 933, 50, 0.1))


def create_blank_preset(self, preset):
    # 把当前配置保存到空白预设
    save_preset(self, preset)
    # 点击全部收纳
    self.click(455, 642, False, 1, 0.5)
    # 等待确认加载
    ocr.screenshot_check_text(self, '确认', (732, 482, 803, 518))
    # 确认收纳
    self.click(769, 498, False)
    # 重新打开预设
    open_preset_window(self, preset)
    # 保存预设
    save_preset(self, preset)
    # 等待加载
    ocr.screenshot_check_text(self, '制造工坊', (732, 482, 803, 518), 0, 0, False)
    # 点击确认
    self.click(769, 498, False)


def save_preset(self, preset):
    area = preset_position[preset]
    # 点击保存当前配置
    self.click(area[0] - 250, area[1], False)
    # 确认加载预设
    confirm_load_preset(self)


def confirm_load_preset(self):
    # 等待加载
    ocr.screenshot_check_text(self, '确认', (732, 482, 803, 518))
    # 确认加载
    self.click(771, 500, False)
    # 等待预设弹窗加载
    ocr.screenshot_check_text(self, '预设', (604, 127, 678, 157))
    # 关闭预设
    self.double_click(934, 146, False)


def init_window(self):
    self.d().pinch_in()
    if self.game_server == 'cn':
        # 拖到最左边
        self.swipe(392, 564, 983, 82)


def to_invitation_ticket(self):
    possible = {
        'cafe_menu': (838, 647),
    }
    return image.detect(self, 'cafe_invitation-ticket', possible)


def do_invite_girl(self):
    possible = {
        'cafe_invitation-ticket': (787, 221),
        'cafe_inv-confirm': (706, 497),
    }
    return image.detect(self, 'cafe_menu', possible)


def invite_girl(self):
    if not image.compare_image(self, 'cafe_invite-status', 0):
        self.logger.warning("当前不可邀请学生")
        return
    # 达到页面
    to_invitation_ticket(self)
    set_fav_sort(self)
    do_invite_girl(self)


def set_fav_sort(self):
    """
    设置好感度排序
    :param self:
    """
    if not image.compare_image(self, 'cafe_inv-fav-level', 0):
        for p in fav_sort_position[self.game_server]:
            self.click(*p, False)
            time.sleep(0.5)
    # 检查好感度升序排序
    image.compare_image(self, 'cafe_inv-fav-sort', mis_fu=self.click, mis_argv=(814, 151, False), rate=0.5)


def get_cafe_money(self):
    # 查看是否需要领取体力
    if not self.tc['config']['receive_ap']:
        self.logger.warning("当前设置为: 不领取体力")
        return
    pos = {
        'cafe_reward-text': (1152, 664),
    }
    rst = image.detect(self, ('cafe_0.0', 'cafe_get-reward'), pos)
    if rst == 'cafe_0.0':
        self.logger.warning("没有可以体力领取")
        return
    # 点击领取
    self.click(641, 516)
    # 关闭获得奖励
    stage.close_prize_info(self, True)
    home.click_house_under(self)
    home.click_house_under(self)


def click_girl_plus(self, i):
    if i % 2 == 0:
        self.swipe(327, 512, 1027, 125)
    else:
        self.swipe(1008, 516, 300, 150)
    time.sleep(0.5)
    before = self.d.screenshot()
    time.sleep(1)
    after = self.d.screenshot()
    # 将图像转换为numpy数组以便进行数学操作
    img1_data = np.array(before)
    img2_data = np.array(after)

    diff_pixels_coords = np.where(img1_data != img2_data)
    # 创建一个映射，键是每个像素点所在的50px区块的坐标，值是该区块中所有不同像素点的列表
    blocks = defaultdict(list)

    for p in zip(*diff_pixels_coords):
        x = int(p[1])
        y = int(p[0])
        # 计算此像素所在的区块坐标
        block_coord = (y // 50, x // 50)
        blocks[block_coord].append((y, x))

    # 对于每个区块，保留中间的像素点
    finial = []
    for block_coord, pixels in blocks.items():
        # 将像素列表按照Y和X排序
        pixels.sort()
        # 取出中间的像素
        mid_pixel = pixels[len(pixels) // 2]
        # 将坐标变换回原图尺寸
        center_coord = (mid_pixel[0] * 1 + 0.5, mid_pixel[1] * 1 + 0.5)
        # 防止溢出到功能按钮
        x = int(center_coord[1])
        y = int(center_coord[0])
        if y < 70 or \
                (y < 130 and x < 320) or (y < 130 and x > 1170) or \
                (y > 570 and x < 100) or (y > 570 and x > 770):
            continue
        finial.append(center_coord)
    # 打乱坐标
    np.random.shuffle(finial)
    for p in finial:
        self.click(int(p[1]), int(p[0]), False)
