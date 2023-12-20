from common import config
from modules.baas import restart


def start(self):
    if self.game_server != 'cn':
        self.logger.error("不是国服,不用反和谐!")
        return
    # 重启游戏
    self.log_title("开始反和谐")
    pkg = self.bc['baas']['base']['package']
    self.logger.warning("开始推送反和谐文件到模拟器中...")
    # 推送文件
    self.d.push(config.get_froze_path('assets/file/LocalizeConfig.txt'), '/sdcard/Android/data/{0}/files/'.format(pkg))
    self.logger.info("反和谐已完成，开始重启游戏")
    restart.start(self)
