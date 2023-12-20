import time

from common import image, color, stage
from modules.baas import home
from modules.exp.normal_task import exp_normal_task
from modules.scan import main_story

position = {
    1: (1126, 200), 2: (1126, 313), 3: (1126, 424), 4: (1128, 540), 5: (1127, 655)
}


def start(self):
    if self.game_server != 'cn':
        return self.logger.critical('外服此功能待开发...')
    # 回到首页
    home.go_home(self)
    to_activity_page(self)
    # 开图
    if self.tc['exp']['enable']:
        start_exp(self)
    # 扫荡
    if self.tc['scan']['enable']:
        start_scan(self)
    # 回到首页
    home.go_home(self)


def start_scan(self):
    to_tab(self, 'task')
    stage_list = self.tc['scan']['stage']
    stage_list = sorted(stage_list, key=lambda x: int(x.split(',')[1]))
    for task in stage_list:
        gq, count = task.split(',')
        gq = int(gq)
        stage.screen_swipe(self, gq, 5, reset=False)
        if gq >= 6:
            gq -= 5
        self.click(*position[gq])
        # 确认扫荡
        rst = stage.confirm_scan(self, gq, count, 99)
        if rst == 'return':
            return
        to_activity_page(self)


def to_tab(self, t):
    """
    到指定tab页面
    @param self:
    @param t:
    """
    tabs = {
        'story': ((832, 103, 833, 104), (77, 55, 40)),
        'task': ((1002, 103, 1003, 104), (77, 55, 40)),
        'challenge': ((1190, 103, 1191, 104), (77, 55, 40))
    }
    tab = tabs[t]
    color.wait_rgb_similar(self, tab[0], tab[1], mis_fu=self.click, mis_argv=(tab[0][0] - 100, tab[0][1]))


def to_activity_page(self):
    """
    到活动页面
    @param self:
    """
    pos = {
        'summer_vacation_title': (1191, 198, 20),  # 首页活动入口
        'momo_talk_menu': (1205, 42),
        'summer_vacation_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516),
        'summer_vacation_guide': (1184, 156),
        'normal_task_task-info': (1084, 142),
        'summer_vacation_game': (59, 40),
        'summer_vacation_mhd-menu': (1233, 11),
    }
    image.detect(self, 'summer_vacation_menu', pos)


def start_exp(self):
    """
    开始开图
    @param self:
    """
    tabs = ['story', 'task', 'challenge']
    for tab in tabs:
        to_activity_page(self)
        do_exp(self, tab)


def do_exp(self, tab):
    """
    执行开图
    @param self:
    @return:
    """
    to_tab(self, 'task')
    to_activity_page(self)
    to_tab(self, tab)
    state = calc_need_fight_stage(self)
    if state is None:
        self.logger.critical("本区域没有需要开图的任务关卡...")
        return
    # 支线和主线点击不同位置
    pos = {
        'main_story_main-lv-start-task': (943, 532),
        'main_story_side-lv-start-task': (640, 511),
    }
    image.detect(self, ('momo_talk_menu', 'normal_task_force-edit', 'summer_vacation_skip', 'momo_talk_confirm-skip'),
                 pos)
    # 跳过剧情
    skip_story(self)
    # 选择部队
    exp_normal_task.to_formation_edit_i(self, self.tc['exp']['force'], (0, 0))
    # 开始战斗
    time.sleep(1)
    # 出击
    image.compare_image(self, 'normal_task_edit-force', threshold=10, mis_fu=self.click, mis_argv=(1163, 658), rate=1,
                        n=True)
    main_story.auto_fight(self)
    # 等待战斗结束
    possible = {
        'main_story_fight-confirm': (1168, 659),  # 战斗通过
        'main_story_fight-fail': (647, 655),  # 战斗失败
        'summer_vacation_fight-confirm': (642, 665),  # 第一次确认
        'normal_task_prize-confirm': (776, 655),  # 第二次奖励确认
        'summer_vacation_game-unlock': (518, 497),  # 小游戏解锁
        'momo_talk_menu': (1205, 42),
        'summer_vacation_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516),
    }
    image.detect(self, 'summer_vacation_menu', possible)
    do_exp(self, tab)


def skip_story(self):
    """
    跳过剧情到部队编辑界面
    """
    pos = {
        'momo_talk_menu': (1205, 42),
        'summer_vacation_skip': (1212, 116),
        'momo_talk_confirm-skip': (770, 516),
    }
    image.detect(self, 'normal_task_force-edit', pos)


def wait_task_info(self, open_info=True):
    """
    等待任务信息加载
    @param open_info: 打开任务信息
    @param self:
    """
    if open_info:
        image.detect(self, ('normal_task_task-info', 'normal_task_side-quest'), cl=(1082, 190))
    else:
        image.compare_image(self, 'normal_task_task-info', 10)


def calc_need_fight_stage(self):
    """
    查找需要战斗的关卡
    @param self:
    @return:
    """
    wait_task_info(self)
    while True:
        # 等待任务信息加载
        task_state = check_task_state(self)
        self.logger.info("当前关卡状态为:{0}".format(task_state))
        if task_state == 'sss':
            # 点击下一关
            self.logger.warn("不满足战斗条件,查找下一关")
            self.click(1172, 358)
            continue
        elif task_state is None:
            return None
        return task_state
    return None


def check_task_state(self):
    """
    检查任务当前类型
    @param self:
    @return:
    """
    # 等待任务信息弹窗加载
    wait_task_info(self, False)
    time.sleep(1)
    # 三星
    if image.compare_image(self, 'normal_task_sss', 0):
        return 'sss'
    # 没关卡了
    if image.compare_image(self, 'summer_vacation_menu', 0):
        return None
    return 'no-sss'
