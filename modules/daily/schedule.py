import time

from common import ocr, color, image, stage
from modules.baas import home

schedule_position = {
    'cn': {
        1: (908, 182), 2: (908, 285), 3: (908, 397), 4: (908, 502), 5: (908, 606),
        6: (908, 606),
    },
    'intl': {
        1: (908, 182), 2: (908, 285), 3: (908, 397), 4: (908, 502), 5: (908, 606),
        6: (908, 285), 7: (908, 397), 8: (908, 502), 9: (908, 606),
    },
    'jp': {
        1: (908, 182), 2: (908, 285), 3: (908, 397), 4: (908, 502), 5: (908, 606),
        6: (908, 182), 7: (908, 285), 8: (908, 397), 9: (908, 502), 10: (908, 606),
    }
}
curse_position = {
    1: (300, 210), 2: (640, 210), 3: (990, 210),
    4: (300, 360), 5: (640, 360), 6: (990, 360),
    7: (300, 516), 8: (640, 516), 9: (990, 516),
}


def to_schedule(self):
    pos = {
        'home_student': (212, 656),  # 首页->日程
        'schedule_choose-course': (59, 36),  # 选择课程 -> 日程
    }
    home.to_menu(self, 'schedule_menu', pos)


def start(self):
    # 回到首页
    home.go_home(self)

    to_schedule(self)

    # 检查余票
    if image.compare_image(self, 'schedule_surplus', 0):
        self.logger.warning("当前持有日程券为0")
        return home.go_home(self)
    # 选择课程
    choose_course(self)
    # 回到首页
    home.go_home(self)


def choose_course(self):
    for tk in self.tc['config']:
        # 点击学院
        to_college(self, tk['schedule'])
        # 学习课程
        if learn_course(self, tk['schedule'], tk['stage']):
            break
        # 回到日程菜单
        pos = {
            'schedule_course-info': (1137, 118),  # 全部日程 -> 选择课程表
            'schedule_choose-course': (59, 36),  # 选择课程 -> 日程
        }
        home.to_menu(self, 'schedule_menu', pos)


def to_college(self, college):
    stage.screen_swipe(self, college, 5)
    to_course_info(self, college)


def to_course_info(self, college):
    pos = {
        'schedule_menu': schedule_position[self.game_server][college],  # 日程 -> 选择课程
        'schedule_choose-course': (1174, 666)  # 选择课程 -> 全部课程
    }
    image.detect(self, 'schedule_course-info', pos)


def start_course(self, course_x):
    pos = {
        'schedule_choose-course': (1174, 666),  # 选择课程 -> 全部课程
        'schedule_course-info': course_x,  # 全部日程 -> 选择课程
    }
    image.detect(self, 'schedule_course-pop', pos)
    # 开始日程
    self.click(640, 546, False)
    time.sleep(2)


def learn_course(self, schedule, courses):
    self.logger.warning("开始检查课程...")
    for c in courses:
        # 检查课程是否可用
        area = (curse_position[c][0], curse_position[c][1], curse_position[c][0] + 1, curse_position[c][1] + 1)
        if not color.check_rgb_similar(self, area, (255, 255, 255)):
            self.logger.error("课程状态不可用")
            continue
        # 点击课程
        self.logger.warning("开始学习课程...")
        start_course(self, curse_position[c])

        if image.compare_image(self, 'schedule_limited', 0):
            self.logger.error("没有门票了")
            return True
        # 等待日程报告
        image.compare_image(self, 'schedule_course-report', cl=(774, 141))
        # 确认报告
        pos = {
            'schedule_course-report': (641, 550)  # 日程报告
        }
        image.detect(self, 'schedule_course-info', pos, cl=(774, 141))
