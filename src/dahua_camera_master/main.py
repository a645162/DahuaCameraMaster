#!/usr/bin/env python3

import os
import sys

# 添加当前目录和父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

from device_search_window import DeviceSearchWindow
from PySide6.QtWidgets import QApplication


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置应用程序信息
    app.setApplicationName("大华摄像机管理器")
    app.setApplicationDisplayName("DahuaCameraMaster")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DahuaCameraMaster")

    # 创建并显示主窗口
    window = DeviceSearchWindow()
    window.show()

    # 运行应用程序
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
