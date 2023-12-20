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

module_cache = {}


def import_module(self, module_name):
    game_server = self.game_server
    # 从cn中导入模块并复制字典以避免直接修改原始数据
    cn_position = __import__(f'assets.position.cn.{module_name}', fromlist=['x']).x.copy()
    if game_server == 'cn':
        return cn_position
    try:
        # 尝试从指定服务器中导入模块
        cu_position = __import__(f'assets.position.{game_server}.{module_name}', fromlist=['x']).x
        # 创建一个新的合并字典，包含cn和特定服务器的键值对
        # 这里不直接修改cn_positions，而是使用合并字典
        return {**cn_position, **cu_position}
    except ImportError:
        # 如果指定服务器的模块不存在，则使用cn的副本
        return cn_position


def get_box(self, name):
    module, name = name.rsplit("_", 1)
    key = '{0}_{1}'.format(self.game_server, module)
    if key not in module_cache:
        module_cache[key] = import_module(self, module)
        return module_cache[key][name]
    return module_cache[key][name]
