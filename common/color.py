import json
import math
import time

import numpy as np

from common import image, config


def init_rgb(self):
    data = json.load(open(config.get_froze_path('assets/file/rgb_feature/rgb_feature.json')))
    self.rgb_feature = data["rgb_feature"]


def color_distance(rgb1, rgb2):
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def wait_rgb_similar(self, area, rgb, retry=999, threshold=20, rate=0.1, mis_fu=None, mis_argv=None):
    """
    等待相似颜色出现
    """
    compare = check_rgb_similar(self, area, rgb)
    if not compare and retry > 0:
        if mis_fu is not None:
            mis_fu(*mis_argv)
            time.sleep(rate)
        time.sleep(rate)
        return wait_rgb_similar(self, area, rgb, retry - 1, threshold)
    return compare


def check_rgb(self, area, target_rgb, threshold=100):
    """
    判断颜色是否相近，用来判断按钮是否可以点击
    """
    sa = np.array(self.d.screenshot())
    # 直接用 RGB 格式的色彩值
    sa_rgb = sa[area[1]][area[0]]
    get_rgb = (sa_rgb[0], sa_rgb[1], sa_rgb[2])
    dist = color_distance(target_rgb, get_rgb)
    result = dist <= threshold
    self.logger.info("check_rgb area:%s target_rgb:%s get_rgb:%s color_dist:%.2F result:%s", area, target_rgb, get_rgb,
                     dist, result)
    return result


def check_rgb_similar(self, area=(1090, 683, 1091, 684), rgb2=(75, 238, 249), threshold=20):
    """
    判断颜色是否相近，用来判断按钮是否可以点击
    """
    self.latest_img_array = self.get_screenshot_array()
    img = image.screenshot_cut(self, area, need_loading=False, ss=self.latest_img_array)
    rgb1 = img[0][0][0], img[0][0][1], img[0][0][2]
    dist = color_distance(rgb1=rgb1, rgb2=rgb2)
    result = dist <= threshold
    self.logger.info("check_rgb_similar area:%s target_rgb:%s get_rgb:%s color_dist: %s result:%s", area, rgb2, rgb1,
                     dist, result)
    return result


def common_rgb_detect_method(self, click, possible_los, ends):
    t_start = time.time()
    t_total = 0
    while t_total <= 60:
        if not self.flag_run:
            return False
        res = detect_rgb_one_time(self, click, possible_los, ends)
        if not res:
            time.sleep(self.screenshot_interval)
            continue
        elif res[0] == "end":
            return res[1]
        elif res[0] == "click":
            time.sleep(self.screenshot_interval)
            continue
        t_total = time.time() - t_start
    self.logger.critical("Wait Too Long")
    return False


def detect_rgb_one_time(self, click, possible_los, ends):
    """
    到指定页面的通用方法
    @param click: 出现位置对应点击坐标
    @param possible_los: 可能出现的位置
    @param ends: 结束位置
    关联的参数: self.rgb_feature储存位置的特征rgb
    """
    self.latest_img_array = self.get_screenshot_array()
    for i in range(0, len(ends)):
        for j in range(0, len(self.rgb_feature[ends[i]][0])):
            if not judge_rgb_range(self.latest_img_array,
                                   self.rgb_feature[ends[i]][0][j][0],
                                   self.rgb_feature[ends[i]][0][j][1],
                                   self.rgb_feature[ends[i]][1][j][0],
                                   self.rgb_feature[ends[i]][1][j][1],
                                   self.rgb_feature[ends[i]][1][j][2],
                                   self.rgb_feature[ends[i]][1][j][3],
                                   self.rgb_feature[ends[i]][1][j][4],
                                   self.rgb_feature[ends[i]][1][j][5]):
                break
        else:
            self.logger.info("end : " + ends[i])  # 出现end中的任意一个，返回对应的位置字符串
            return "end", ends[i]
    for i in range(0, len(possible_los)):  # 可能的图标
        for j in range(0, len(self.rgb_feature[possible_los[i]])):  # 每个图标多个，判断rgb
            if not judge_rgb_range(self.latest_img_array,
                                   self.rgb_feature[possible_los[i]][0][j][0],
                                   self.rgb_feature[possible_los[i]][0][j][1],
                                   self.rgb_feature[possible_los[i]][1][j][0],
                                   self.rgb_feature[possible_los[i]][1][j][1],
                                   self.rgb_feature[possible_los[i]][1][j][2],
                                   self.rgb_feature[possible_los[i]][1][j][3],
                                   self.rgb_feature[possible_los[i]][1][j][4],
                                   self.rgb_feature[possible_los[i]][1][j][5]):
                break
        else:
            self.logger.info("position : " + possible_los[i])
            self.click(click[i][0], click[i][1])  # 出现possible_los中的任意一个，点击对应的click坐标
            return "click", True
    return False


def judge_rgb_range(shot_array, x, y, r_min, r_max, g_min, g_max, b_min, b_max):
    if r_min <= shot_array[y][x][2] <= r_max and \
            g_min <= shot_array[y][x][1] <= g_max and \
            b_min <= shot_array[y][x][0] <= b_max:
        return True
    return False


def check_sweep_availability(img):
    """
    检查是否可以扫荡
    三个灰色星星 no-pass
    一个黄色星星 pass
    三个黄色个星星 sss
    """
    if judge_rgb_range(img, 211, 369, 192, 212, 192, 212, 192, 212) and \
            judge_rgb_range(img, 211, 402, 192, 212, 192, 212, 192, 212) and \
            judge_rgb_range(img, 211, 436, 192, 212, 192, 212, 192, 212):
        return "no-pass"
    if judge_rgb_range(img, 211, 368, 225, 255, 200, 255, 20, 60) or \
            judge_rgb_range(img, 211, 404, 225, 255, 200, 255, 20, 60) or \
            judge_rgb_range(img, 211, 434, 225, 255, 200, 255, 20, 60):
        return "pass"
    if judge_rgb_range(img, 211, 368, 225, 255, 200, 255, 20, 60) and \
            judge_rgb_range(img, 211, 404, 225, 255, 200, 255, 20, 60) and \
            judge_rgb_range(img, 211, 434, 225, 255, 200, 255, 20, 60):
        return "sss"
