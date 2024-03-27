import json
import sys
import time
import unittest

import cv2
import numpy as np
import uiautomator2 as u2
from cnocr import CnOcr

from common import color, image, encrypt
from common import stage, config, log
from modules.attack import normal_task, arena
from modules.baas import home, delete_friend
from modules.daily import cafe, schedule, group, make
from modules.exp.normal_task import exp_normal_task
from modules.reward import work_task
from modules.shop import shop
from modules.story import main_story, momo_talk
from common import stage, process, config, log, encrypt
from modules.activity import summer_vacation, spa_227, new_year, cherry_blossoms, nun_magician
from modules.attack import exchange_meeting, special_entrust, wanted, arena, normal_task, hard_task
from modules.baas import restart, fhx, env_check
from modules.daily import group, cafe, schedule, make
from modules.exp.hard_task import exp_hard_task
from modules.exp.normal_task import exp_normal_task
from modules.reward import work_task, mailbox
from modules.shop import shop, buy_ap
from modules.story import momo_talk, main_story
from modules.task import challenge_hard_task


class TestBaas(unittest.TestCase):

    def load_config(self):
        filepath = config.config_filepath(self.con)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.bc = data
        self.game_server = self.calc_game_server()

    def log_title(self, msg):
        self.logger.info(log.title(msg))

    def setUp(self) -> None:
        self.flag_run = True
        self.click_time = 0.0
        self.latest_img_array = None
        self.con = '02_wz'
        self.test = True
        self.load_config()

        self.logger = log.create_logger(self.con, False)
        self.d = u2.connect(self.bc['baas']['base']['serial'])
        self.ocr = CnOcr()
        self.ocrEN = CnOcr(det_model_name='en_PP-OCRv3_det', rec_model_name='en_PP-OCRv3')
        self.ocrNum = CnOcr(det_model_name='number-densenet_lite_136-fc', rec_model_name='number-densenet_lite_136-fc')
        self.file_path = "../assets/images"

    def swipe(self, fx, fy, tx, ty, duration=None):
        self.logger.info("swipe %s %s %s %s duration:%s", fx, fy, tx, ty, duration)
        self.d.swipe(fx, fy, tx, ty, duration=duration)

    def click(self, x, y, wait=True, count=1, rate=0):
        if wait:
            stage.wait_loading(self)
        for i in range(count):
            self.logger.info("click x:%s y:%s", x, y)
            if rate > 0:
                time.sleep(rate)
            self.d.click(x, y)

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
            self.d.click(x, y)

    def double_click(self, x, y, wait=True, count=1, rate=0):
        if wait:
            stage.wait_loading(self)
        for i in range(count):
            self.logger.info("double_click x:%s y:%s", x, y)
            if rate > 0:
                time.sleep(rate)
            self.d.double_click(x, y)

    def test_color(self):
        color.check_rgb(self, (183, 125), (232, 68, 0))
        # color.check_rgb(self, (1075, 680), (250, 236, 74))

    def calc_game_server(self):
        pkg = self.bc['baas']['base']['package']
        if pkg == 'com.nexon.bluearchive':
            return 'intl'
        elif pkg == 'com.YostarJP.BlueArchive':
            return 'jp'
        else:
            return 'cn'

    def ss_task_lv(self, base, lv, region):
        gs = 'cn'
        box = (191, 199, 265, 224) if gs == 'cn' else (146, 199, 215, 227)
        d = "{0}/{1}".format(self.file_path, base)
        f = "../assets/images/{0}/{1}/{2}-{3}.png".format(gs, base, region, lv)
        image.screenshot_cut_old(self, '', d, f, box=box)
        self.click(1167, 355)
        time.sleep(0.5)

    def test_gen_normal_task(self):
        base = 'normal_task'
        for region in range(4, 16):
            max = 6
            # if region in [6, 9, 12, 15, 18]:
            #     max = 7
            for lv in range(1, max):
                self.ss_task_lv(base, lv, region)

    def test_gen_hard_task(self):
        base = 'hard_task'
        for region in range(4, 7):
            for lv in range(1, 4):
                self.ss_task_lv(base, lv, region)

    def get_screenshot_array(self):
        return cv2.cvtColor(np.array(self.d.screenshot()), cv2.COLOR_RGB2BGR)

    def test_exp_task(self):
        """
        测试运行关卡-开图
        """
        task = 'exp_hard_task'
        # task = 'exp_hard_task'
        levels = [
            # '6-1', '6-1-box', '6-2', '6-2-box', '6-3', '6-3-box',
            # '10-1',
            # '10-2-task',
            # '10-3-task',
            # '16-1',
            '17-3',
            # '7-1-box',
            # '6-2', '6-2-box', '6-3', '6-3-box',

            # '10-1', '10-1-box', '10-2', '10-2-box', '10-3', '10-3-box',

            # '6-1', '6-2', '6-3', '6-4', '6-5',
            # '7-1', '7-2', '7-3', '7-4', '7-5',
            # '8-1', '8-2', '8-3', '8-4', '8-5',
            # '9-1', '9-2', '9-3', '9-4', '9-5',
            # '10-1', '10-2', '10-3', '10-4', '10-5',
            # '11-1', '11-2', '11-3', '11-4', '11-5',
            # '12-1', '12-2', '12-3', '12-4', '12-5',
            # '13-1', '13-2', '13-3', '13-4', '13-5',
            # '14-1', '14-2', '14-3', '14-4', '14-5',
            # '15-1', '15-2', '15-3', '15-4', '15-5',
            # '16-1', '16-2', '16-3', '16-4', '16-5',
        ]
        # 回到首页
        home.go_home(self)
        for lv in levels:
            lv_data = lv.split('-')
            region = int(lv_data[0])
            lv_index = int(lv_data[1])
            self.tc = self.bc[task]
            self.tc['task'] = task
            # 选择任务模式
            normal_task.to_choose_region(self)
            normal_task.change_task(self)
            self.stage_data = exp_normal_task.get_stage_data(self, region)
            normal_task.choose_region(self, region)
            exp_normal_task.wait_task_info(self, True)
            self.click(1172, 358, False, lv_index - 1, 1)
            time.sleep(1)
            exp_normal_task.start_fight(self, region, lv)

    def test_ss(self):
        """
        测试资源截图生成图片资源
        """
        assets = [
            # 'summer_vacation_title',
            # 'summer_vacation_skip',
            # 'summer_vacation_guide',
            # 'summer_vacation_menu',
            # 'summer_vacation_mhd-menu',
            # 'summer_vacation_enter',
            # 'summer_vacation_fight-confirm',
            # 'summer_vacation_game-unlock',

            # 'make_menu',
            # 'make_receive',
            # 'make_start-make',
            # 'make_confirm-start',
            # 'make_immediately',
            # 'make_workshop',
            # 'make_start',
            # 'make_list',
            # 'make_choose-node',
            # 'make_confirm-acc',
            # 'make_first-stage-start',

            # 'home_store-error',
            # 'home_cafe-lock',
            # 'home_bus',
            # 'home_bus1',
            # 'home_student',
            # 'home_setting',
            # 'home_black',
            # 'home_new-players',

            # 'wanted_menu',
            # 'wanted_stage-list'
            # 'wanted_buy-ticket'
            # 'wanted_task-info-window'
            # 'special_entrust_menu'
            # 'exchange_meeting_menu'
            # 'exchange_meeting_stage-list'
            # 'exchange_meeting_no-ticket'

            # 'restart_news',
            # 'restart_menu',
            # 'restart_maintain',
            # 'restart_update',
            # 'home_news'
            # 'home_news-intl',

            # 'arena_id',
            # 'arena_cd',

            # 'arena_0-5',
            # 'arena_war-force',
            # 'arena_skip',
            # 'arena_attack',
            # 'arena_menu',
            # 'arena_edit-force',
            # 'arena_ap-limited',

            # 'fight_edit-attack-force',
            # 'fight_start-task',
            # 'fight_tasking',
            # 'fight_pass-confirm',
            # 'fight_task-finish-confirm',
            # 'fight_prize-confirm',
            # 'fight_force-edit',
            # 'fight_attack',
            # 'fight_skip-fight',
            # 'fight_auto-over',
            # 'fight_fighting-task-info',
            # 'fight_confirm',
            # 'fight_prize-confirm2',
            # 'fight_force-attack',
            # 'fight_fail',

            #
            # 'cafe_menu',
            # 'cafe_reward-text',
            # 'cafe_0.0',
            # 'cafe_students-arrived',
            # 'cafe_get-reward',
            # 'cafe_invite-status',
            # 'cafe_inc-fav',
            # 'cafe_give-gift',
            # 'cafe_inv-fav-level',
            # 'cafe_inv-fav-sort',
            # 'cafe_inv-sel-level',
            # 'cafe_inv-fav-sort',
            # 'cafe_inv-confirm',
            # 'cafe_need-storage',

            # 'tutor_dept_entry',
            # 'tutor_dept_title',

            # 'group_menu',
            # 'group_guide',
            # 'group_sign-up-confirm',

            # 'mailbox_menu',
            # 'mailbox_limited',

            # 'momo_talk_no-chat',
            # 'momo_talk_sort-field',
            # 'momo_talk_sort-direction',
            # 'momo_talk_sort-field-newest',
            # 'momo_talk_sort-field-newest2',
            # 'momo_talk_sort-field-unread',
            # 'momo_talk_menu',
            # 'momo_talk_skip',
            # 'momo_talk_confirm-skip',
            # 'momo_talk_student',
            # 'momo_talk_unread',
            # 'momo_talk_reply',
            # 'momo_talk_likable',
            # 'momo_talk_begin-relationship',

            # 'work_task_menu',
            # 'work_task_receive',

            # 'shop_menu',
            # 'shop_choose-buy',
            # 'shop_buy-confirm1',
            # 'shop_buy-confirm2',
            # 'shop_refresh-confirm',
            # 'shop_buy3',
            # 'shop_buy2',
            # 'shop_buy1',

            # 'schedule_menu',
            # 'schedule_surplus',
            # 'schedule_course-info',
            'schedule_limited',
            # 'schedule_course-pop',
            # 'schedule_course-report',

            # 'normal_task_menu',
            # 'normal_task_choose-region',
            # 'normal_task_task-info',
            # 'normal_task_task-info-window',
            # 'normal_task_task-info-notice',
            # 'normal_task_scan-confirm',
            # 'normal_task_scan-skip',
            # 'normal_task_buy-ap-window',
            # 'normal_task_buy-hard-count',
            # 'normal_task_fight-task',
            # 'normal_task_force-edit',
            # 'normal_task_fight-skip',
            # 'normal_task_auto-over',
            # 'normal_task_sss',
            # 'normal_task_force-4',
            # 'normal_task_force-3',
            # 'normal_task_force-2',
            # 'normal_task_force-1',
            # 'normal_task_task-scan',
            # 'normal_task_15-1',
            # 'normal_task_15-2',
            # 'normal_task_15-3',
            # 'normal_task_15-4',
            # 'normal_task_15-5',
            # 'normal_task_side-quest',
            # 'normal_task_attack',
            # 'normal_task_prize-confirm',
            # 'normal_task_no-pass',
            # 'nor2mal_task_move-force-confirm',
            # 'normal_task_end-turn',
            # 'normal_task_task-finish',
            # 'normal_task_box',
            # 'normal_task_get-box',
            # 'normal_task_fight-task-info',

            # 'buy_ap_notice',
            # 'buy_ap_confirm',
            # 'buy_ap_limited',
            # 'buy_ap_buy20',
            # 'buy_ap_buy19',
            # 'buy_ap_buy18',
            # 'buy_ap_buy17',
            # 'buy_ap_buy16',
            # 'buy_ap_buy15',
            # 'buy_ap_buy14',
            # 'buy_ap_buy13',
            # 'buy_ap_buy12',
            # 'buy_ap_buy11',
            # 'buy_ap_buy10',
            # 'buy_ap_buy9',
            # 'buy_ap_buy8',
            # 'buy_ap_buy7',
            # 'buy_ap_buy6',
            # 'buy_ap_buy5',
            # 'buy_ap_buy4',
            # 'buy_ap_buy3',
            # 'buy_ap_buy2',
            # 'buy_ap_buy1',

            # 'main_story_menu',
            # 'main_story_menu1',
            # 'main_story_go-main-story',
            # 'main_story_story',
            # 'main_story_choose-plot',
            # 'main_story_clearance',
            # 'main_story_current-clearance',
            # 'main_story_plot-info',
            # 'main_story_skip-menu',
            # 'main_story_first-lock',
            # 'main_story_plot-fight',
            # 'main_story_join-chapter',
            # 'main_story_plot-attack',
            # 'main_story_fight-parse',
            # 'main_story_fight-confirm',
            # 'main_story_fight-fail',
            # 'main_story_auto',
            # 'main_story_three-times',
            # 'main_story_get-prize',
            # 'cm_activity-menu'

            # 'spa_227_entrance',
            # 'spa_227_menu',
            # 'spa_227_unlock',
            # 'spa_227_guide',

            # 'new_year_entrance',
            # 'new_year_menu',
            # 'new_year_guide',

            # 'new_year_entrance',
            # 'cherry_blossoms_menu',
            # 'new_year_guide',

            # 'nun_magician_menu'

            # 'delete_friend_sysmenu',
            # 'delete_friend_fri-manage',
            # 'delete_friend_menu',
            # 'delete_friend_del-fri',
            # 'delete_friend_del-notice',
        ]
        stage.wait_loading(self)
        print("开始截图...")
        for asset in assets:
            print(asset)
            base, file = asset.rsplit('_', 1)
            d = "{0}/{1}/{2}/".format(self.file_path, self.game_server, base)
            f = "../assets/images/{0}/{1}/{2}.png".format(self.game_server, base, file)
            image.screenshot_cut_old(self, asset, d, f)
        time.sleep(1)
        print("开始校验")
        stage.wait_loading(self)
        for i in range(2):
            for asset in assets:
                assert image.compare_image(self, asset, 0)
        assert True

    def test_all_ss(self):
        self.to_server_all(self.test_ss, ())

    def test_all_single_task(self):
        self.ttt = 'delete_friend'
        self.to_server_all(delete_friend.start, (self,))

    def to_server_all(self, fu, argv):
        # servers = ['1_cn', '1_jp', '1_intl']
        servers = ['1_jp']
        for server in servers:
            self.con = server
            self.load_config()
            if hasattr(self, 'ttt'):
                self.tc = self.bc[self.ttt]
                self.tc['task'] = self.ttt
            pkg = self.bc['baas']['base']['package']
            if server == '1_intl':
                self.d.app_start(pkg, 'com.nexon.bluearchive.MxUnityPlayerActivity')
            else:
                self.d.app_start(pkg)
            print('{0} 切换服务器成功...'.format(server))
            time.sleep(0.5)
            fu(*argv)

    def test_image(self):
        image_data1 = cv2.imdecode(
            np.fromfile('../assets/images/cn/arena/skip.png', dtype=np.uint8), -1)
        image_data2 = cv2.imdecode(
            np.fromfile('../assets/images/cn/arena/skip2.png', dtype=np.uint8), -1)
        image.compare_image_data(self, image_data1, image_data2)
        pass

    def test_loading(self):
        while True:
            stage.wait_loading(self)
            time.sleep(1)
            print("\t\t\t\ntest_loading...\n")

    def exit(self, msg):
        """
        退出程序
        @param msg: 失败消息
        """
        self.logger.critical(msg)
        if hasattr(self, 'processes_task') and encrypt.md5(self.con) in self.processes_task:
            del self.processes_task[encrypt.md5(self.con)]
        sys.exit(1)
