"""
浏览器工厂模块
提供统一的浏览器创建接口
"""

import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from .ie_browser_window import IEBrowserWindow
from ..utils.dpi_utils import set_dpi_awareness, setup_qt_dpi_settings


class BrowserFactory:
    """浏览器工厂类"""

    @staticmethod
    def create_ie_browser(
        default_url: str = "",
        window_title: str = "IE浏览器",
        window_size: tuple = (1200, 800),
        window_pos: tuple = (100, 100),
    ) -> IEBrowserWindow:
        """
        创建IE浏览器窗口

        Args:
            default_url: 默认加载的URL
            window_title: 窗口标题
            window_size: 窗口大小 (width, height)
            window_pos: 窗口位置 (x, y)

        Returns:
            IEBrowserWindow: 配置好的IE浏览器窗口实例
        """
        window = IEBrowserWindow(default_url)
        window.setWindowTitle(window_title)
        window.setGeometry(window_pos[0], window_pos[1], window_size[0], window_size[1])

        return window

    @staticmethod
    def setup_application() -> QApplication:
        """
        设置并创建QApplication实例

        Returns:
            QApplication: 配置好的应用程序实例
        """
        # 在创建QApplication之前设置DPI
        set_dpi_awareness()

        # 设置Qt的高DPI设置
        setup_qt_dpi_settings()

        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # 禁用高DPI缩放
        app.setAttribute(Qt.AA_DisableHighDpiScaling, True)
        app.setAttribute(Qt.AA_Use96Dpi, True)

        app.setApplicationName("大华相机管理器")
        app.setApplicationVersion("1.0")

        return app


def create_browser_app(default_url: str = "192.168.1.1") -> tuple:
    """
    便捷函数：创建浏览器应用程序

    Args:
        default_url: 默认加载的URL

    Returns:
        tuple: (app, window) - QApplication实例和浏览器窗口实例
    """
    app = BrowserFactory.setup_application()
    window = BrowserFactory.create_ie_browser(
        default_url=default_url,
        window_title="大华相机管理器 - IE浏览器",
    )

    return app, window


def main_browser_standalone(default_url: str = "192.168.1.1") -> int:
    """
    独立运行浏览器的主函数

    Args:
        default_url: 默认加载的URL

    Returns:
        int: 应用程序退出码
    """
    import sys

    try:
        app, window = create_browser_app(default_url)
        window.show()
        return app.exec()
    except Exception as e:
        logging.error(f"启动浏览器失败: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main_browser_standalone())
