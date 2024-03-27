import json
import sys
import time
from datetime import datetime, timedelta

import cv2
import numpy as np
import uiautomator2 as u2
from cnocr import CnOcr
from uiautomator2 import Device

from common import stage, process, config, log, encrypt
from modules.activity import summer_vacation, spa_227, new_year, cherry_blossoms, nun_magician
from modules.attack import exchange_meeting, special_entrust, wanted, arena, normal_task, hard_task
from modules.baas import restart, fhx, env_check, delete_friend
from modules.daily import group, cafe, schedule, make
from modules.exp.hard_task import exp_hard_task
from modules.exp.normal_task import exp_normal_task
from modules.reward import work_task, mailbox
from modules.shop import shop, buy_ap
from modules.story import momo_talk, main_story
from modules.task import challenge_hard_task

func_dict = {
    # 活动
    'spa_227': spa_227.start,
    'summer_vacation': summer_vacation.start,
    'new_year': new_year.start,
    'cherry_blossoms': cherry_blossoms.start,
    'nun_magician': nun_magician.start,
    # 出击
    'arena': arena.start,
    'exchange_meeting': exchange_meeting.start,
    'hard_task': hard_task.start,
    'normal_task': normal_task.start,
    'special_entrust': special_entrust.start,
    'wanted': wanted.start,
    # baas
    'env_check': env_check.start,
    'fhx': fhx.start,
    'restart': restart.start,
    'delete_friend': delete_friend.start,
    # 每日
    'cafe': cafe.start,
    'group': group.start,
    'make': make.start,
    'schedule': schedule.start,
    # 开图
    'exp_hard_task': exp_hard_task.start,
    'exp_normal_task': exp_normal_task.start,
    # 收获
    'mailbox': mailbox.start,
    'work_task': work_task.start,
    # 商店
    'buy_ap': buy_ap.start,
    'shop': shop.start,
    # 剧情
    'main_story': main_story.start,
    'momo_talk': momo_talk.start,
    # 任务
    'challenge_hard_task': challenge_hard_task.start,
}


class Baas:
    ocr: CnOcr
    ocrEN: CnOcr
    ocrNum: CnOcr
    d: Device
    bc: dict  # baas config BA配置
    tc: dict  # task config 任务配置
    game_server: str  # 游戏区服
    next_task: str

    def __init__(self, con, processes_task):
        self.flag_run = True
        self.click_time = 0.0
        self.latest_img_array = None
        self.con = con
        if processes_task is None:
            return
        self.logger = log.create_logger(con)
        self.load_config()
        self.game_server = self.calc_game_server()
        self.connect_serial()
        self.init_ocr()
        env_check.check_resolution(self)
        env_check.check_fhx(self)
        self.processes_task = processes_task
        self.next_task = ''
        self.stage_data = {}

    def log_title(self, msg):
        self.logger.info(log.title(msg))

    def init_ocr(self):
        try:
            self.log_title("开始初始化OCR")
            self.ocrEN = CnOcr(det_model_name='en_PP-OCRv2_det', rec_model_name='en_PP-OCRv3')
            if self.game_server == 'cn':
                self.ocr = CnOcr()
            else:
                self.ocr = self.ocrEN
            self.ocrNum = CnOcr(det_model_name='number-densenet_lite_136-fc',
                                rec_model_name='number-densenet_lite_136-fc')
        except Exception as e:
            self.logger.critical(
                r"解决方法1: 删除 C:\Users\你的用户名\AppData\Roaming\cnocr\2.2 目录 重新运行脚本会重新下载(可能要用梯子上网)")
            self.logger.critical(
                r"解决方法2-1: 到QQ群下载《异常问题文件下载/2.2.7z》 压缩包,解压到 C:\Users\你的用户名\AppData\Roaming\cnocr\2.2 目录里面")
            self.logger.critical(
                r"解决方法2-2: 到QQ群下载《异常问题文件下载/1.2.zip》 压缩包,解压到 C:\Users\你的用户名\AppData\Roaming\cnstd\1.2 目录里面")
            self.exit("OCR初始化失败:{0}".format(e))

    def connect_serial(self):
        serial = self.bc['baas']['base']['serial']
        try:
            self.log_title("开始连接模拟器:{0}".format(serial))
            self.d = u2.connect(serial)
            ta = self.d.info
            self.logger.info("模拟器连接成功:{0}".format(self.d.device_info['udid']))
        except Exception as e:
            self.logger.critical("模拟器连接失败，必须打开模拟器! 然后设置对应模拟器端口 Baas->Baas设置->模拟器Serial")
            self.logger.critical("如果模拟器多开，ADB端口会不一样。点击模拟器问题诊断->查看ADB调试端口")
            self.logger.critical(
                "如果报错HTTPSConnectionPool(host='github.com',port=443): Max retries exceeded with url..."
                "到QQ群下载《异常问题文件下载/atx-agent_0.10.0_linux_386》 复制到 C:\\Users\你的用户名\.uiautomator2\cache\\atx-agent_0.10.0_linux_386.tar.gz-1f8cdf3239 目录里面")
            self.exit(e)

    def click(self, x, y, wait=True, count=1, rate=0):
        if wait:
            stage.wait_loading(self)
        for i in range(count):
            self.logger.info("click (%s,%s)", x, y)
            if rate > 0:
                time.sleep(rate)
            self.d.click(x, y)

    def get_screenshot_array(self):
        return cv2.cvtColor(np.array(self.d.screenshot()), cv2.COLOR_RGB2BGR)

    def click_condition(self, x, y, cond, fn, fn_args, wait=True, rate=0):
        """
        条件点击，直到不满足条件为止
        @param x: x坐标
        @param y: y坐标
        @param cond: true 或 false 
        @param fn: 要执行的函数，需要返回bool
        @param fn_args: 执行函数的参数
        @param wait: 是否需要等待加载
        @param rate: 每次点击等待时间
        """
        if wait:
            stage.wait_loading(self)
        self.click(x, y, False)
        while cond != fn(self, *fn_args):
            time.sleep(rate)
            self.click(x, y, False)

    def double_click(self, x, y, wait=True, count=1, rate=0):
        if wait:
            stage.wait_loading(self)
        for i in range(count):
            self.logger.info("double_click (%s,%s)", x, y)
            if rate > 0:
                time.sleep(rate)
            self.d.double_click(x, y)

    def swipe(self, fx, fy, tx, ty, duration=None):
        self.logger.info("swipe %s %s %s %s duration:%s", fx, fy, tx, ty, duration)
        self.d.swipe(fx, fy, tx, ty, duration=duration)

    def exit(self, msg):
        """
        退出程序
        @param msg: 失败消息
        """
        self.logger.critical(msg)
        if hasattr(self, 'processes_task') and encrypt.md5(self.con) in self.processes_task:
            del self.processes_task[encrypt.md5(self.con)]
        sys.exit(1)

    def check_close_game(self):
        if not self.bc['baas']['close_game']['enable']:
            return False
        app = self.d.app_current()
        if app['package'] != self.bc['baas']['base']['package']:
            return True
        wait = self.task_schedule(None)['waiting'][0]
        next_time = datetime.strptime(wait['next'], "%Y-%m-%d %H:%M:%S")
        if next_time >= datetime.now() + timedelta(seconds=600):
            self.logger.warning(
                "当前已开启 无任务时 关闭游戏开关，节约电脑资源. 如需关闭到:Baas->Baas设置->禁用 关闭游戏设置")
            restart.only_stop(self)
            return True
        return False

    def dashboard(self):
        # 使用字典将字符串映射到对应的函数
        suffix = "</br>【Baas】是一款完全免费开源的自动化脚本，如遇收费请立即退款！</br>项目开源地址: " \
                 "https://github.com/baas-pro/baas</br>QQ交流群:621628600 "
        self.log_title("⭐️ BA启动 ⭐️")
        no_task = False
        first = True
        while True:
            fn, tc = self.get_task()
            if fn is None:
                if not no_task:
                    self.log_title("🎉🎉🎉 任务全部执行成功 🎉🎉🎉" + suffix)
                no_task = True
                if self.check_close_game():
                    time.sleep(57)
                time.sleep(3)
                continue
            if first:
                env_check.check_resolution(self)
                env_check.check_fhx(self)
                first = False
            no_task = False
            # 从字典中获取函数并执行
            if fn in func_dict:
                self.processes_task[encrypt.md5(self.con)] = fn
                self.tc = tc
                self.tc['task'] = fn
                self.finish_seconds = 0
                self.log_title("开始执行【" + tc['base']['text'] + "】")
                func_dict[fn](self)
                self.finish_task(fn)
                self.log_title("执行完成【" + tc['base']['text'] + "】")
                del self.processes_task[encrypt.md5(self.con)]
            else:
                self.exit(f"函数不存在:{fn}")

    def config_path(self):
        return config.config_filepath(self.con)

    def load_config(self):
        with open(self.config_path(), 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.bc = data

    def calc_game_server(self):
        pkg = self.bc['baas']['base']['package']
        if pkg == 'com.nexon.bluearchive':
            return 'intl'
        elif pkg == 'com.YostarJP.BlueArchive':
            return 'jp'
        else:
            return 'cn'

    def save_config(self):
        with open(self.config_path(), 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.bc, indent=4, ensure_ascii=False, sort_keys=False))

    def get_task(self):
        self.load_config()
        queue = []
        if hasattr(self, 'next_task') and self.next_task != '':
            nt = self.next_task
            self.next_task = ''
            self.log_title("执行关联任务【{0}】".format(self.bc[nt]['base']['text']))
            return nt, self.bc[nt]
        for ba_task, con in self.bc.items():
            if ba_task == 'baas':
                continue
            if con['base']['next'] == '':
                con['base']['next'] = datetime.now().strftime('%Y-%m-%d 00:00:00')
            try:
                next_time = datetime.strptime(con['base']['next'], "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                next_time = datetime.now() - timedelta(days=1)
                con['base']['next'] = datetime.now().strftime('%Y-%m-%d 00:00:00')
            try:
                end_time = datetime.strptime(con['base']['end'], "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                end_time = datetime.now() + timedelta(days=1)
                con['base']['end'] = ''
            # 超出截止时间
            if not con['base']['enable'] or (con['base']['end'] != '' and end_time < datetime.now()):
                continue
            # 时间未到
            if next_time >= datetime.now():
                continue
            task = {'index': con['base']['index'], 'next': con['base']['next'], 'task': ba_task, 'con': con}
            queue.append(task)
        queue.sort(key=lambda x: (x['index'], datetime.strptime(x['next'], "%Y-%m-%d %H:%M:%S")))
        if len(queue) > 0:
            return queue[0]['task'], queue[0]['con']
        return None, None

    def task_schedule(self, run_task):
        self.load_config()
        running = []
        waiting = []
        queue = []
        closed = []
        for ba_task, con in self.bc.items():
            if ba_task == 'baas':
                continue
            if con['base']['next'] == '':
                con['base']['next'] = datetime.now().strftime('%Y-%m-%d 00:00:00')
            try:
                next_time = datetime.strptime(con['base']['next'], "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                next_time = datetime.now() - timedelta(days=1)
                con['base']['next'] = datetime.now().strftime('%Y-%m-%d 00:00:00')
            try:
                end_time = datetime.strptime(con['base']['end'], "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                end_time = datetime.now() + timedelta(days=1)
                con['base']['end'] = ''
            # 被关闭的功能
            task = {'next': con['base']['next'], 'task': ba_task, 'text': con['base']['text'],
                    'index': con['base']['index']}
            # 正在运行中的任务
            if run_task is not None and run_task == ba_task:
                running.append(task)
                continue
            if not con['base']['enable'] or (
                    con['base']['end'] != '' and end_time < datetime.now()):
                closed.append(task)
                continue
            # 时间未到
            if next_time > datetime.now():
                waiting.append(task)
                continue
            # 队列中
            queue.append(task)

        waiting.sort(key=lambda x: (datetime.strptime(x['next'], "%Y-%m-%d %H:%M:%S"), x['index'],))
        queue.sort(key=lambda x: (x['index'], datetime.strptime(x['next'], "%Y-%m-%d %H:%M:%S")))
        return {'running': running, 'waiting': waiting, 'queue': queue, 'closed': closed,
                'run_state': process.m.state_process(self.con)}

    def find_exec_task(self):
        """
        查找关联任务立刻执行
        """
        if 'link_task' in self.tc['base']:
            self.next_task = self.tc['base']['link_task']

    def finish_task(self, fn):
        self.load_config()
        # 获取当前日期时间
        now = datetime.now()
        if self.finish_seconds > 0:
            future = now + timedelta(seconds=self.finish_seconds)
        else:
            # 计算下次执行时间
            if 'interval' in self.tc['base'] and self.tc['base']['interval'] > 0:
                future = now + timedelta(seconds=self.tc['base']['interval'])
            else:
                future = now + timedelta(days=1)
                # 别问我为什么要写5点 :)
                future = datetime(future.year, future.month, future.day, 5, 0)
        # 将datetime对象转成字符串
        self.bc[fn]['base']['next'] = future.strftime("%Y-%m-%d %H:%M:%S")
        # 完成任务
        if 'task' in self.tc:
            del self.tc["task"]
        self.save_config()
        # 查找关联任务立刻执行
        self.find_exec_task()
