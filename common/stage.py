import time

import cv2
import numpy as np

from common import ocr, image
from common.color import judge_rgb_range
from modules.baas import home


def confirm_scan(self, stage, ct, max_count):
    self.logger.warning("开始扫荡第 {0} 关".format(stage))
    ends = (
        'wanted_task-info-window',
        'normal_task_task-info-window'
    )
    image.detect(self, ends)
    is_max = type(ct) == str and ct == 'max'
    # 等关卡加载
    if is_max or int(ct) >= max_count:
        if self.game_server == 'cn':
            # 长按
            self.double_click(1034, 299, False)
            self.double_click(1034, 299, False)
            self.d.long_click(1034, 299, 5)
        else:
            # 点击max
            self.click(1078, 301, False)
    else:
        # 扫荡指定次数
        self.click(1034, 299, False, int(ct) - 1, 0.6)
    # 点击开始扫荡
    self.click(938, 403, False)
    ends = (
        'wanted_buy-ticket',  # 通缉悬赏没票了
        'normal_task_buy-hard-count',  # 困难次数不足
        'normal_task_buy-ap-window',  # 购买体力弹窗
        'normal_task_task-info-notice'  # 确认扫荡通知
    )
    end = image.detect(self, ends)
    # 通缉悬赏没票了
    if end == 'wanted_buy-ticket':
        self.click(56, 38, 0, 3)
        return 'continue'
    elif end == 'normal_task_buy-ap-window':
        return 'return'
    if end != 'normal_task_task-info-notice':
        return
    # 确认扫荡
    start_scan(self)
    return 'nothing'


def start_scan(self):
    pos = {
        'normal_task_task-info-notice': (770, 500),  # 确认扫荡->确认
        'normal_task_scan-skip': (647, 506),  # 跳过
    }
    image.detect(self, 'normal_task_scan-confirm', pos)
    # 确认扫荡结果
    self.click(643, 586)
    # 关闭任务弹窗
    home.click_house_under(self)


def close_prize_info(self, ap_check=False, mail_check=False):
    """
    关闭奖励道具结算页面
    """
    text_box = {
        'intl': ('TOUCH', '因超出持有上限'),  # todo 不知道叫啥,还没遇到
        'cn': ('点击继续', '因超出持有上限')
    }
    text_box['jp'] = text_box['intl']
    tb = text_box[self.game_server]
    # 点击继续
    if ocr.screenshot_check_text(self, tb[0], (577, 614, 704, 648), 1):
        self.click(640, 635)
        time.sleep(0.5)
        return
    # 因超出持有上限
    if ap_check and ocr.screenshot_check_text(self, tb[1], (532, 282, 724, 314), 1):
        self.click(650, 501)
        return
    # 以上道具的库存已满
    if mail_check and image.compare_image(self, 'mailbox_limited', 0):
        self.click(642, 527)
        return
    return close_prize_info(self, ap_check, mail_check)


def wait_loading(self):
    """
    检查是否加载中，
    """
    t_start = time.time()
    while 1:
        self.latest_img_array = cv2.cvtColor(np.array(self.d.screenshot()), cv2.COLOR_RGB2BGR)
        if not judge_rgb_range(self.latest_img_array, 937, 648, 200, 255, 200, 255, 200, 255) or not \
                judge_rgb_range(self.latest_img_array, 919, 636, 200, 255, 200, 255, 200, 255):
            loading_pos = [[929, 664], [941, 660], [979, 662], [1077, 665], [1199, 665]]
            rgb_loading = [[200, 255, 200, 255, 200, 255], [200, 255, 200, 255, 200, 255],
                           [200, 255, 200, 255, 200, 255], [200, 255, 200, 255, 200, 255],
                           [255, 255, 255, 255, 255, 255]]
            t = len(loading_pos)
            for i in range(0, t):
                if not judge_rgb_range(self.latest_img_array, loading_pos[i][0], loading_pos[i][1], rgb_loading[i][0],
                                       rgb_loading[i][1], rgb_loading[i][2], rgb_loading[i][3],
                                       rgb_loading[i][4], rgb_loading[i][5]):
                    break
            else:
                t_load = time.time() - t_start
                self.logger.info(f"Now Loading : {t_load:.0f} seconds")
                if t_load > 20:
                    self.logger.warning("LOADING TOO LONG add screenshot interval to 1")
                    self.screenshot_interval = 1
                time.sleep(self.screenshot_interval)
                continue

        return True


# 定义内部转换函数处理单个字符串
def convert_string(s):
    # 数据处理
    s = s.lower().replace(' ', '').replace('—', '-').replace('_', '-')
    # 根据英文破折号分割字符串
    parts = s.split('-')

    # 转换为整数或保留
    region = int(parts[0])
    stage = int(parts[1])
    count = parts[2] if parts[2] == 'max' else int(parts[2])

    # 返回字典结果
    return {'region': region, 'stage': stage, 'count': count}


# 定义一个函数，用于处理字符串列表，移除空格，并且将中文破折号和下划线替换成英文破折号
def stage_convert(stage_list):
    # 使用列表推导式处理每个字符串
    return [convert_string(s) for s in stage_list]


def screen_swipe(self, stage, threshold1, threshold2=999, reset=True, f=(911, 650, 911, 40, 0.55)):
    if reset:
        # 先保证回到最开始
        self.swipe(911, 199, 911, 600, 0.1)
        self.swipe(911, 199, 911, 600, 0.1)
    if stage > threshold1:
        time.sleep(0.5)
        self.swipe(*f)
    if stage > threshold2:
        time.sleep(0.5)
        self.swipe(*f)
    time.sleep(0.5)
