import os
import sys
import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPalette, QBrush
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtWidgets import QPushButton, QLabel, QSpacerItem, QSizePolicy

from web import configs

version = 'v2.0.0'


# 使用一个子线程打开浏览器
def open_baas():
    configs.check_config()
    webbrowser.open_new('http://localhost:1117/')


def open_github():
    webbrowser.open_new('https://github.com/baas-pro/baas')


def open_bilibili():
    webbrowser.open_new('https://space.bilibili.com/25881702')


def start():
    # 创建应用实例
    app = QApplication(sys.argv)

    # 创建一个窗口
    window = QWidget()
    window.setWindowTitle('蔚蓝档案-BAAS')
    window.setFixedSize(660, 250)

    base_path = ''
    # 如果我们是在 PyInstaller 打包后的版本中运行，那么改变 base_path 到正确的目录
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    # 创建一个QPixmap对象来加载图片
    pixmap = QPixmap(os.path.join(base_path, 'assets/images/common/fm.jpeg'))

    # 创建一个QPalette对象来设置窗口背景
    palette = QPalette()

    # 使用画笔工具设置背景图片，按比例伸缩填充整个窗口
    brush = QBrush(pixmap.scaled(window.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

    palette.setBrush(QPalette.Window, brush)
    window.setPalette(palette)

    # 创建一个垂直布局器
    layout = QVBoxLayout()
    layout.setSpacing(0)
    lab = QLabel(
        '<!DOCTYPE html> <html> <head> <style> .centered-text { color: #4169E1; text-shadow: 4px 4px 8px #000000; font-size: 13px; font-weight: 600; font-style: italic; } </style> </head> <body> <p align="center"><span class="centered-text">【Baas】是一款完全免费开源的蔚蓝档案自动化脚本，如遇收费请立即退款！</span></p> <p align="center"><span class="centered-text">QQ交流1群：621628600(已满)</span><span class="centered-text">QQ交流2群：441327580(已满)</span><span class="centered-text">QQ交流3群：190361986</span></p></body> </html>')
    lab.setAlignment(Qt.AlignCenter)
    lab.setTextInteractionFlags(Qt.TextSelectableByMouse)
    layout.addWidget(lab)
    spacer = QSpacerItem(20, 200, QSizePolicy.Minimum, QSizePolicy.Fixed)
    layout.addItem(spacer)
    add_btn(layout)

    v = QLabel(f'<span style="color:white;font-weight:bold;font-style: italic;">Version: {version} </span>')
    layout.addWidget(v, 0, Qt.AlignRight)

    layout.setContentsMargins(0, 5, 0, 5)
    window.setLayout(layout)

    # 显示窗口
    window.show()
    # 运行程序
    sys.exit(app.exec())


def add_btn(layout):
    # 创建一个水平布局
    hbox = QHBoxLayout()

    # 创建第一个按钮并添加至水平布局
    btn = get_btn('打开Baas')
    btn.clicked.connect(open_baas)
    btn.setFixedSize(88, 28)
    hbox.addWidget(btn)
    # 添加间隔
    hbox.addSpacing(10)  # 调整这个值来设置按钮之间的间隔大小
    # 创建第二个按钮并添加至水平布局
    btn = get_btn('开源地址')
    btn.clicked.connect(open_github)
    btn.setFixedSize(88, 28)
    hbox.addWidget(btn)
    # 添加间隔
    hbox.addSpacing(10)  # 调整这个值来设置按钮之间的间隔大小
    # 创建第三个按钮并添加至水平布局
    btn = get_btn('B站视频教程')
    btn.clicked.connect(open_bilibili)
    btn.setFixedSize(88, 28)
    hbox.addWidget(btn)

    # 将水平布局居中对齐，并添加到传入的垂直布局中
    hbox.setAlignment(Qt.AlignCenter)
    layout.addLayout(hbox)


def get_btn(text):
    btn = QPushButton(text)
    btn.setStyleSheet("""
    QPushButton {
        background-color: #00B0FF;
        color: white;
        font-weight:bold;
        border-style: solid;
        border-radius: 3px; 
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #40C4FF; 
    }
    QPushButton:pressed {
        background-color: #00B0FF;
    }
""")
    return btn
