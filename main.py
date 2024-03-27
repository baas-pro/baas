import logging
import multiprocessing
import os
import sys
import threading
import time

import requests
from flask import Flask

import launcher
from common import process, config, app
from web.baas import baas
from web.configs import configs, check_config

is_exit = False


def run_flask():
    global is_exit
    f = Flask(__name__, static_folder='web/static', static_url_path='/static')
    f.register_blueprint(baas)
    f.register_blueprint(configs)
    ac = config.get_app_config()
    try:
        f.run(debug=False, port=ac['port'], host='0.0.0.0')
    except UnicodeDecodeError as e:
        # Handle decoding errors specifically
        is_exit = True
        print("服务启动失败", e)
        for i in range(3):
            print(
                "电脑设备名称不能有中文或特殊符号，点击Win开始->设置->系统->关于->重命名这台电脑！使用纯英文命名然后重启电脑！")
        sys.exit(-1)
    except Exception as e:
        is_exit = True
        print("服务启动失败: ", str(e))
        sys.exit(-1)


def check_flask_startup():
    global is_exit
    check_config()
    time.sleep(1)
    ac = config.get_app_config()
    url = f"http://127.0.0.1:{ac['port']}/ping"
    for i in range(3):
        if is_exit:
            return
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                launcher.print_title("启动成功", "")
                app.open_baas()
                break
            if i == 2:
                launcher.print_title("启动失败",
                                     f"Baas启动失败...当前运行端口为:{ac['port']}\n如果端口冲突可以打开configs/app.txt 修改port 为 7111 或 7112依次类推")
        except Exception as e:
            if i == 2:
                launcher.print_title("启动失败",
                                     f"Baas启动失败...当前运行端口为:{ac['port']}\n如果端口冲突可以打开configs/app.txt 修改port 为 7111 或 7112依次类推")
            print(e)
        time.sleep(1)


def check_source():
    """
    windows平台检查启动来源
    """
    if hasattr(sys, 'frozen') and sys.platform != 'darwin':
        source_arg_value = next((arg.split('=')[1] for arg in sys.argv if arg.startswith('source=')), None)
        if source_arg_value != "launcher":
            print("必须从启动器Baas_Windows.exe启动Baas脚本")
            print("如果你是第一次遇到这个错误，请从QQ群重新下载最新启动器覆盖原来的启动器。")
            print("不需要重新下载和安装Baas")
            launcher.wait()
            sys.exit(1)


if __name__ == '__main__':
    main_process_pid = os.getpid()
    multiprocessing.freeze_support()

    process.manager = multiprocessing.Manager()
    process.processes_task = process.manager.dict()

    if os.getpid() == main_process_pid:
        check_source()

        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        check_thread = threading.Thread(target=check_flask_startup)
        check_thread.daemon = True
        check_thread.start()

        run_flask()
