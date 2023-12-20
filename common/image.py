import importlib
import os
import time

import cv2
import numpy as np
from skimage.metrics import structural_similarity

from common import stage, position, config
from common.position import get_box
import os
import sys

import cv2
import numpy as np

from modules.activity import tutor_dept, summer_vacation
from modules.baas import home, restart, cm
# 图片资源数据 image assets data
from modules.daily import arena, cafe, wanted, special_entrust, shop, schedule, make, group, buy_ap
from modules.reward import mailbox, momo_talk, work_task
from modules.scan import hard_task, normal_task, main_story


def screenshot_cut_old(self, name, ss_path=None, ss_file='', box=None):
    if box is None:
        box = get_box(self, name)
    # 创建目录
    if ss_path is None:
        ss_path = config.get_runtime_path()
    if not os.path.exists(ss_path):
        os.makedirs(ss_path)
    ss_img = screenshot_cut(self, box, 0, False)
    cv2.imwrite(ss_file, ss_img)


def screenshot_cut(self, area, before_wait=0, need_loading=True, ss=None):
    """
    截图并裁剪图片
    @param self:
    @param area: 剪切区域
    @param before_wait: 前置等待时间
    @param need_loading: 等待加载
    @param ss: screenshot截图数据
    @return: 图片对象
    """
    if before_wait > 0:
        time.sleep(before_wait)
    # 检查文字前，等待加载完成
    if need_loading:
        stage.wait_loading(self)
    if len(area) == 0:
        return self.get_screenshot_array()
    else:
        if ss is None:
            self.latest_img_array = self.get_screenshot_array()
            return self.latest_img_array[area[1]:area[3], area[0]:area[2], :]
        else:
            return ss[area[1]:area[3], area[0]:area[2], :]


def save_img_to_disk(image_array, name):
    debug_dir = config.get_debug_dir()
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir, exist_ok=True)
    cv2.imwrite(config.get_debug_file(name), image_array)


def compare_image(self, name, retry=999, threshold=3, nl=False, mis_fu=None, mis_argv=None, rate=None, n=False,
                  box=None, ss=None, compare_mode=None, cl=None):
    """
    对图片坐标内的图片和资源图片是否匹配
    @param self:
    @param name: 资源名称
    @param retry: 重试次数
    @param threshold: 匹配程度0为完全匹配
    @param nl: need_loading 等待加载
    @param mis_fu: 不匹配时执行函数
    @param mis_argv: 不匹配时执行函数参数
    @param rate: 重试频率
    @param n: not识别结果取反
    @param box: 强制指定box坐标
    @param ss: screenshot截图数据
    @param compare_mode: 强制制定匹配模式
    @param cl: click事件坐标
    @return: 是否匹配
    """
    if rate is None:
        rate = self.bc['baas']['base']['ss_rate']
    if nl:
        stage.wait_loading(self)
    if box is None:
        box = get_box(self, name)
    ss_img = screenshot_cut(self, box, 0, False, ss=ss)
    if self.bc['baas']['base']['debug']:
        save_img_to_disk(ss_img, name)
    res_img = get_img_data(self, name)
    # 检查图片宽度是否一样
    height1, width1 = ss_img.shape[:2]
    height2, width2 = res_img.shape[:2]
    if width1 != width2 or height1 != height2:
        self.exit(f"Image dimensions do not match (get {width1}x{height1} => target{width2}x{height2}) name:{name}")
    # 对比图片
    compare = compare_image_data(self, ss_img, res_img, threshold, name, n)
    if not compare and retry > 0:
        if 100 < retry < 989 and retry % 10 == 0:
            self.logger.warning('当前图片识别模式:{0} 如果一直卡识别可以打开Baas设置更换识别模式'.format(
                self.bc['baas']['base']['compare_mode']))
        if mis_fu is not None:
            mis_fu(*mis_argv)
            time.sleep(rate)
        if cl is not None:
            self.click(*cl, False)
        return compare_image(self, name, retry - 1, threshold, nl, mis_fu, mis_argv, rate, n, box, ss, compare_mode, cl)
    return compare


def compare_image_data(self, ss_img, res_img, threshold=3, name='', n=False):
    """
    对比两个图片数据是否相同
    """
    compare_mode = self.bc['baas']['base']['compare_mode']
    if res_img.shape[0] < 7 or res_img.shape[1] < 7:
        compare_mode = 'mse'
    if 'mse' == compare_mode:
        # 计算差异值
        diff = cv2.absdiff(ss_img, res_img)
        # 计算MSE（Mean Squared Error）
        mse = np.mean(diff ** 2)
        compare = mse <= threshold
        if n:
            compare = not compare
        self.logger.info("compare_image %s MSE:%.2f Result:%s", name, mse, compare)
    else:
        # ssim 对比
        # 转换图片到灰度
        ss_gray = cv2.cvtColor(ss_img, cv2.COLOR_BGR2GRAY)
        res_gray = cv2.cvtColor(res_img, cv2.COLOR_BGR2GRAY)
        # 计算SSIM（Structural Similarity Index）
        ssim = structural_similarity(ss_gray, res_gray)
        if threshold == 3:
            threshold = 0.7
        elif threshold <= 1:
            threshold = 0.9
        elif threshold < 3:
            threshold = 0.8
        elif threshold > 3:
            threshold = 0.6
        compare = ssim >= threshold
        if n:
            compare = not compare
        self.logger.info("compare_image %s SSIM:%.2f Result:%s", name, ssim, compare)
    return compare


def detect(self, end, possibles=None, cl=None, pre_func=None, pre_argv=None, retry=999, ss_rate=None):
    """
    图片探索 执行对应事件
    @param self:
    @param end: 结束出现的位置 可以是str 或 或 tuple(str,str...) tuple(str,int) 或 tuple( tuple(str,int),tuple(str,int)... )
    @param possibles: possible  图片可能会出现的位置 字典{图片资源名称:(坐标或函数,阈值)} 阀值可以缺省
    @param cl: click location 点击位置，先点击位置
    @return: 图片资源名称
    @param pre_func: 前置函数
    @param pre_argv: 前置函数参数
    """
    if ss_rate is None:
        ss_rate = self.bc['baas']['base']['ss_rate']
    if cl is not None:
        self.click(cl[0], cl[1])
        time.sleep(ss_rate)
    i = 1
    while True:
        if i >= retry:
            return None
        self.logger.info("开始第 {0} 次图片检索 end:{1}".format(i, end))
        i += 1
        if i > 10 and i % 10 == 0:
            self.logger.warning('当前图片识别模式:{0} 如果一直卡识别可以打开Baas设置更换识别模式'.format(
                self.bc['baas']['base']['compare_mode']))
        stage.wait_loading(self)
        self.latest_img_array = self.get_screenshot_array()  # 每次公用一张截图
        if pre_func is not None:
            res = pre_func(*pre_argv)
            if not res:
                pass
            elif res[0] == 'end':
                return res[1]
            elif res[0] == 'click':
                time.sleep(ss_rate)
                continue

        # region 结束图片可能会出现的位置
        if type(end) is str:
            if compare_image(self, end, 0, 3, nl=False, ss=self.latest_img_array):
                return end
        else:
            for asset in end:
                if type(asset) is str:
                    asset = (asset, 3)
                threshold = asset[1]
                if compare_image(self, asset[0], 0, threshold, nl=False, ss=self.latest_img_array):
                    return asset[0]
        # endregion
        # region 资源图片可能会出现的位置
        if possibles is not None:
            for asset, obj in possibles.items():
                threshold = 3
                if len(obj) >= 3:
                    threshold = obj[2]
                if compare_image(self, asset, 0, threshold, nl=False, ss=self.latest_img_array):
                    if type(obj[0]) is int:
                        # 坐标版本
                        self.click(obj[0], obj[1], False)
                        time.sleep(ss_rate)
                    else:
                        # 函数版本 如果对应函数范围直接为True,退出整个逻辑
                        if obj[0](*obj[1]):
                            return asset
                    break
        # endregion
        if cl is not None:
            self.click(cl[0], cl[1])
        time.sleep(ss_rate)


loaded_images = {}


def get_img_data(self, key):
    """
    获取图片数据，如果图片尚未加载，则加载图片
    @param self: self
    @param key: 图片资源的key
    @return: 图片数据
    """
    ck = f'{self.game_server}_{key}'
    if ck in loaded_images:
        return loaded_images[ck]
    base_path = ''
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    if hasattr(self, 'test'):
        assets_dir = os.path.join(base_path, '../assets/images', self.game_server)
    else:
        assets_dir = os.path.join(base_path, 'assets/images', self.game_server)
    # 根据key得到模块名和文件名部分
    module_name, file_name = key.rsplit('_', 1)
    file_path = os.path.join(assets_dir, module_name, f'{file_name}.png')
    # 检查文件是否存在
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"图片文件 {file_path} 不存在")
    # 加载图片文件
    image_data = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    loaded_images[ck] = image_data
    return loaded_images[ck]


def find_img(self, img, name, x_add=0, y_add=0):
    template = get_img_data(self, name)
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    locations = np.where(result >= threshold)
    seen = set()
    for pt in zip(*locations[::-1]):
        center_pt = (int(pt[0] + template.shape[1] / 2 + x_add), int(pt[1] + template.shape[0] / 2 + y_add))
        seen.add(center_pt)
    return list(seen)
