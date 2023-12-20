import traceback
from multiprocessing import Process

from common import log, encrypt
from common.baas import Baas


def baas_dashboard(con, pt):
    b = None
    try:
        b = Baas(con, pt)
        b.dashboard()
    except Exception as e:
        if b is not None:
            logger = b.logger
        else:
            logger = log.create_logger(con)
        stack_trace = traceback.format_exc()  # 获取堆栈跟踪信息
        logger.critical("Exception occurred: {0}".format(e))
        logger.critical("Stack trace:\n{0}".format(stack_trace))
    # 主进程运行中的任务


manager = None
processes_task = None


class Main:
    def __init__(self):
        self.processes = {}  # 存储所有的进程

    def start_process(self, con):
        """
        启动进程
        @param con: 配置文件名称
        """
        # 如果对应的进程没有运行，则启动它
        if encrypt.md5(con) not in self.processes or not self.processes[encrypt.md5(con)].is_alive():
            self.processes[encrypt.md5(con)] = Process(target=baas_dashboard, args=(con, processes_task))
            self.processes[encrypt.md5(con)].start()

    def stop_process(self, con):
        """
        停止进程
        @param con: 配置文件名称
        """
        if encrypt.md5(con) in self.processes and self.processes[encrypt.md5(con)].is_alive():
            # 请求终止baas进程
            self.processes[encrypt.md5(con)].terminate()
            # 等待进程实际结束
            self.processes[encrypt.md5(con)].join()
            log.create_logger(con).info("停止运行")
            if encrypt.md5(con) in processes_task:
                del processes_task[encrypt.md5(con)]

    def state_process(self, con):
        """
        获取进程执行状态
        @param con: 配置文件名称
        """
        if encrypt.md5(con) in self.processes:
            return self.processes[encrypt.md5(con)].is_alive()
        else:
            return False

    def run_task(self, con):
        """
        获取进程执行中的任务
        @param con: 配置文件名称
        """
        if encrypt.md5(con) in processes_task:
            return processes_task[encrypt.md5(con)]
        return None


m = Main()
