from common import stage, color, image
from modules.baas import home


def start(self):
    # 回到首页
    home.go_home(self)
    pos = {
        'home_student': (1144, 37),  # 首页->点击邮箱
    }
    home.to_menu(self, 'mailbox_menu', pos)

    if color.check_rgb_similar(self):
        self.logger.warning("开始领取奖励")
        # 点击一键领取
        self.click(1136, 669)
        # 关闭获得奖励
        stage.close_prize_info(self, False, True)
    else:
        self.logger.info("没有需要领取的奖励")
    # 回到首页
    home.go_home(self)
