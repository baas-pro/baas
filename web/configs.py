import os
import shutil
import traceback

from flask import Blueprint
from flask import request

from common import config, process

configs = Blueprint('configs', __name__)


@configs.route('/configs', methods=['GET'])
def config_list():
    config_dir = config.config_dir()
    con_list = sorted([os.path.splitext(f)[0] for f in os.listdir(config_dir) if f.endswith('.json')])
    cl = []
    for con in con_list:
        cl.append({'name': con, 'state': process.m.state_process(con)})
    return {'data': {'list': cl}, 'code': 200}, 200


def check_config():
    config_dir = config.config_dir()
    # 如果目录不存在，则创建它
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
        source_file = config.get_froze_path('web/static/baas.json')
        # 目标文件的完整路径
        destination_file = os.path.join(config_dir, 'baas.json')
        # 复制文件
        shutil.copy(source_file, destination_file)


@configs.route('/menus', methods=['GET'])
def menus_list():
    menus = [
        {
            'name': 'Baas',
            'text': 'Baas',
            'child': [
                {'name': 'baas', 'text': 'Baas设置'},
                {'name': 'restart', 'text': '重启设置'},
                {'name': 'env_check', 'text': '环境检查'},
                {'name': 'fhx', 'text': '反和谐'},
            ]
        },
        {
            'name': 'daily',
            'text': '每日',
            'child': [
                {'name': 'group', 'text': '小组'},
                {'name': 'make', 'text': '制造'},
                {'name': 'schedule', 'text': '日程'},
                {'name': 'cafe', 'text': '咖啡厅'}
            ]
        },
        {
            'name': 'shop',
            'text': '商店',
            'child': [
                {'name': 'shop', 'text': '商店购买'},
                {'name': 'buy_ap', 'text': '购买体力'},
            ]
        },
        {
            'name': 'scan',
            'text': '出击',
            'child': [
                {'name': 'special_entrust', 'text': '特殊委托'},
                {'name': 'wanted', 'text': '通缉悬赏'},
                {'name': 'arena', 'text': '战术对抗赛'},
                {'name': 'normal_task', 'text': '普通关卡-扫荡'},
                {'name': 'hard_task', 'text': '困难关卡-扫荡'},
            ]
        },
        {
            'name': 'exp',
            'text': '开图',
            'child': [
                {'name': 'exp_normal_task', 'text': '普通关卡-开图'},
                {'name': 'exp_hard_task', 'text': '困难关卡-开图'},
            ]
        },
        {
            'name': 'story',
            'text': '剧情',
            'child': [
                {'name': 'main_story', 'text': '主线剧情'},
            ]
        },
        {
            'name': 'reward',
            'text': '收获',
            'child': [
                {'name': 'mailbox', 'text': '领取邮箱'},
                {'name': 'momo_talk', 'text': 'MomoTalk'},
                {'name': 'work_task', 'text': '工作任务'},
            ]
        },
        {
            'name': 'activity',
            'text': '活动',
            'child': [
                # {'name': 'tutor_dept', 'text': '补习部签到'},
                {'name': 'summer_vacation', 'text': '日奈会长'},
            ]
        }
    ]
    return {'data': {'list': menus}, 'code': 200}, 200


@configs.route('/configs/<string:con>/<string:fn>', methods=['GET'])
def config_detail(con, fn):
    data = config.load_ba_config(con)
    if fn not in data:
        return {'msg': '配置不存在', 'code': 500}, 500
    return {'data': data[fn], 'code': 200}, 200


@configs.route('/configs/<string:con>/<string:fn>', methods=['POST'])
def save_config(con, fn):
    data = config.load_ba_config(con)
    if fn not in data:
        return {'msg': '配置不存在', 'code': 500}, 500
    data[fn] = request.get_json()
    config.save_ba_config(con, data)
    return {'data': data[fn], 'code': 200}, 200


# 处理所有Exception类型的错误
@configs.errorhandler(Exception)
def handle_exception(e):
    full_traceback_info = traceback.format_exc()
    return {'msg': full_traceback_info, 'code': 500}, 500
