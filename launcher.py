#!/usr/bin/env python3
import os
import subprocess
import sys
import traceback
import urllib.request

windows_git_repo_https = 'https://gitee.com/baas-pro/baas-windows.git'
macos_m_git_repo_https = 'https://gitee.com/baas-pro/baas-macos-m.git'


def git_clone_and_pull():
    print("检查是否已安装: {0}".format('baas'))
    repository_url = windows_git_repo_https if os.name == 'nt' else macos_m_git_repo_https
    directory = resource_path("baas")
    if not os.path.isdir(directory):
        print(f"未找到目录 {directory}，正在克隆仓库...")
        directory = resource_path("")
        subprocess.run(['git', 'clone', repository_url, 'baas'], cwd=directory, check=True)
        print("baas 下载完成...")
    else:
        git_pull(directory)
        print("baas 更新完成...")


def command_exists(command):
    """Check if a command is available on the system."""
    try:
        print("检查是否已安装: {0}".format(command))
        subprocess.run([command, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_homebrew():
    """Install Homebrew on macOS systems."""
    print("正在安装 Homebrew...")
    subprocess.run('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
                   shell=True, check=True)


def install_git_on_windows():
    """Download and install Git on Windows."""
    download_url = 'https://gitee.com/baas-pro/baas-windows/releases/download/git/Git-2.43.0-64-bit.exe'
    git_file_path = 'Git-Installer.exe'

    # 检查 Git 安装程序是否已下载
    if not os.path.exists(git_file_path):
        print("正在下载 Git 安装程序...")
        urllib.request.urlretrieve(download_url, git_file_path)
    else:
        print("Git 安装程序已存在，跳过下载。")

    print("正在安装 Git，请稍候...")
    try:
        # 使用'/VERYSILENT'参数使安装器在后台运行，不显示界面，并且不需要用户干预
        subprocess.run([git_file_path, '/VERYSILENT'], check=True)
    except Exception as e:
        stack_trace = traceback.format_exc()  # 获取堆栈跟踪信息
        print("\n发生异常: {0}".format(e))
        print("堆栈跟踪:\n{0}".format(stack_trace))
        print("安装失败: 如果提示没有权限,拒绝访问. 请以管理员运行启动器!!!")

    print("Git安装完成。请关闭此命令提示符窗口，并在新的命令提示符窗口中重新Launcher脚本。")
    wait()
    sys.exit(0)


def install_git():
    """Provide instructions to install Git or attempt to install it using Homebrew on macOS."""
    if os.name == 'nt':  # Windows
        print("未检测到 Git，正在开始下载git...")
        install_git_on_windows()
    else:  # macOS
        if not command_exists('brew'):
            install_homebrew()
        print("正在尝试使用 Homebrew 安装 Git...")
        subprocess.run(['brew', 'install', 'git'], check=True)


def git_pull(directory):
    """Run git pull in a specific directory."""
    print(f"在目录 {directory} 中执行 'git pull origin main' 命令...")
    subprocess.run(['git', 'pull', 'origin', 'main'], cwd=directory, check=True)


def start_baas():
    if os.name == 'nt':  # Windows
        start_baas_windows()
    else:
        start_baas_macos()


# 启动baas.exe程序
def start_baas_windows():
    local_path = resource_path("baas")
    baas_exe_path = os.path.join(local_path, "baas.exe")

    # 确保 baas.exe 存在
    if not os.path.isfile(baas_exe_path):
        print(f"发生错误：未找到 {baas_exe_path}")
        return

    # 启动 baas.exe
    print("正在启动 baas.exe...")
    subprocess.Popen(baas_exe_path, cwd=local_path)


# 启动 baas.app 程序（macOS）
def start_baas_macos():
    local_path = resource_path("baas")
    baas_app_path = os.path.join(local_path, "baas.app")
    if not os.path.isdir(baas_app_path):
        print(f"发生错误：未找到 {baas_app_path}")
        return
    print("正在启动 baas.app...\n")
    subprocess.run(['open', baas_app_path], cwd=local_path)


def resource_path(relative_path):
    if hasattr(sys, 'frozen'):
        base = os.path.dirname(sys.executable)
    else:
        # 在开发环境中，直接返回脚本所在目录
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def main():
    try:
        print("Baas启动器")
        # 检查 Git 是否安装
        if not command_exists('git'):
            install_git()

        # 执行 git pull 命令
        git_clone_and_pull()

        # 启动Baas
        start_baas()
    except Exception as e:
        stack_trace = traceback.format_exc()  # 获取堆栈跟踪信息
        print("\n发生异常: {0}".format(e))
        print("堆栈跟踪:\n{0}".format(stack_trace))
        wait()


def wait():
    # 等待用户按键后退出
    input("\n按任意键退出...")


if __name__ == '__main__':
    main()
