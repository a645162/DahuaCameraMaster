"""
IE浏览器窗口主模块
重构后的IE浏览器窗口实现
"""

import argparse
import logging
import os
import sys
from typing import Optional

# 添加src目录到Python路径，以便正确导入dahua_camera_master包
if __name__ == "__main__":
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取src目录（向上三级目录）
    src_dir = os.path.join(current_dir, "..", "..", "..")
    src_dir = os.path.abspath(src_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from dahua_camera_master.browser.ie_com_widget import IEComWidget
from dahua_camera_master.utils.dpi_utils import (
    set_dpi_awareness,
    setup_qt_dpi_settings,
)


class IEBrowserWindow(QMainWindow):
    """优化的IE浏览器窗口"""

    def __init__(self, default_url: str = ""):
        super().__init__()
        self.default_url = default_url
        self.browser: Optional[IEComWidget] = None
        self.url_input: Optional[QLineEdit] = None
        self.status_bar: Optional[QStatusBar] = None
        self.progress_bar: Optional[QProgressBar] = None

        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

        self._init_ui()
        self._init_browser()

    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("IE浏览器 - PySide6")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中央控件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)

        # 创建工具栏
        self._create_toolbar(main_layout)

        # 创建状态栏
        self._create_status_bar()

        self.logger.info("UI初始化完成")

    def _create_toolbar(self, parent_layout: QVBoxLayout):
        """创建工具栏"""
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        # URL输入框
        url_label = QLabel("地址:")
        toolbar_layout.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入网址 (例: www.baidu.com)")
        self.url_input.setText(self.default_url)
        self.url_input.returnPressed.connect(self._on_navigate_clicked)
        self.url_input.setMinimumHeight(30)
        toolbar_layout.addWidget(self.url_input, 1)

        # 导航按钮
        nav_button = QPushButton("跳转")
        nav_button.setMinimumHeight(30)
        nav_button.setMinimumWidth(80)
        nav_button.clicked.connect(self._on_navigate_clicked)
        nav_button.setDefault(True)
        toolbar_layout.addWidget(nav_button)

        # 刷新按钮
        refresh_button = QPushButton("刷新")
        refresh_button.setMinimumHeight(30)
        refresh_button.setMinimumWidth(60)
        refresh_button.clicked.connect(self._refresh_page)
        toolbar_layout.addWidget(refresh_button)

        parent_layout.addLayout(toolbar_layout)

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.status_bar.showMessage("就绪")

    def _init_browser(self):
        """初始化浏览器组件"""
        try:
            self._show_progress("正在初始化浏览器...")

            # 创建IE COM组件
            self.browser = IEComWidget(self)

            # 连接信号
            self.browser.navigation_started.connect(lambda url: self._show_progress(f"正在加载 {url}..."))
            self.browser.navigation_completed.connect(lambda url: self._hide_progress("页面加载完成"))
            self.browser.navigation_error.connect(self._on_navigation_error)
            self.browser.document_ready.connect(lambda: self._hide_progress("文档加载完成"))
            self.browser.progress_changed.connect(self._on_progress_changed)
            self.browser.status_changed.connect(self._on_status_changed)
            self.browser.title_changed.connect(self._on_title_changed)

            # 添加到布局
            self.centralWidget().layout().addWidget(self.browser, 1)

            # 延迟导航
            if self.default_url:
                QTimer.singleShot(1500, lambda: self._navigate_to_url(self.default_url))

            self._hide_progress("浏览器初始化完成")

        except Exception as e:
            self._hide_progress(f"浏览器初始化失败: {str(e)}")
            self.logger.error(f"浏览器初始化失败: {e}")
            self._show_error_message("初始化失败", f"无法创建IE浏览器组件:\n{str(e)}")

    def _on_navigation_error(self, url: str, error_msg: str):
        """处理导航错误"""
        self._hide_progress(f"导航失败: {error_msg}")
        self.logger.error(f"导航错误: {url} - {error_msg}")
        self._show_warning(f"无法访问 {url}: {error_msg}")

    def _on_progress_changed(self, progress: int):
        """处理进度变化"""
        if self.progress_bar.isVisible():
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(progress)

    def _on_status_changed(self, status: str):
        """处理状态变化"""
        if status and not self.progress_bar.isVisible():
            self.status_bar.showMessage(status)

    def _on_title_changed(self, title: str):
        """处理标题变化"""
        if title:
            self.setWindowTitle(f"IE浏览器 - {title}")

    def _navigate_to_url(self, url: str):
        """导航到指定URL"""
        if not self.browser:
            self._show_warning("浏览器组件未初始化")
            return

        # 格式化URL
        formatted_url = self._format_url(url)
        self.logger.info(f"导航到: {formatted_url}")

        # 更新地址栏
        if self.url_input.text() != formatted_url:
            self.url_input.setText(formatted_url)

        # 使用IEComWidget的navigate方法
        success = self.browser.navigate(formatted_url)
        if not success:
            self._show_warning("导航失败，请检查网络连接和URL格式")

    def _on_navigate_clicked(self):
        """处理导航按钮点击"""
        url = self.url_input.text().strip()
        if not url:
            self._show_warning("请输入有效的网址")
            self.url_input.setFocus()
            return

        self._navigate_to_url(url)

    def _format_url(self, url: str) -> str:
        """格式化URL"""
        url = url.strip()
        if not url:
            return ""

        if not url.startswith(("http://", "https://", "ftp://")):
            # 简单的URL检测
            if "." in url and not url.startswith("file://"):
                url = "http://" + url

        return url

    def _refresh_page(self):
        """刷新当前页面"""
        if self.browser:
            success = self.browser.refresh()
            if success:
                self._show_progress("正在刷新...")
                QTimer.singleShot(2000, lambda: self._hide_progress("刷新完成"))
            else:
                self._show_warning("刷新失败")

    def _show_progress(self, message: str):
        """显示进度"""
        self.status_bar.showMessage(message)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 无限进度

    def _hide_progress(self, message: str = "就绪"):
        """隐藏进度"""
        self.status_bar.showMessage(message)
        self.progress_bar.setVisible(False)

    def _show_warning(self, message: str):
        """显示警告"""
        self.status_bar.showMessage(f"警告: {message}", 3000)
        self.logger.warning(message)

    def _show_error_message(self, title: str, message: str):
        """显示错误对话框"""
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.browser:
            self.browser.cleanup()
        event.accept()


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="IE浏览器窗口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python ie_browser_window.py --url http://192.168.1.1
  python ie_browser_window.py --url http://192.168.1.100 --low-dpi
  python ie_browser_window.py --help
        """,
    )

    parser.add_argument("--url", default="192.168.1.1", help="默认加载的URL地址 (默认: 192.168.1.1)")

    parser.add_argument("--low-dpi", action="store_true", help="使用低DPI模式（禁用高DPI缩放）")

    args = parser.parse_args()

    # 条件性设置DPI
    if args.low_dpi:
        # 在创建QApplication之前设置DPI
        set_dpi_awareness()
        # 设置Qt的高DPI设置
        setup_qt_dpi_settings()

    app = QApplication(sys.argv)

    # 条件性应用DPI设置
    if args.low_dpi:
        # 禁用高DPI缩放
        app.setAttribute(Qt.AA_DisableHighDpiScaling, True)
        app.setAttribute(Qt.AA_Use96Dpi, True)

    app.setApplicationName("IE浏览器")
    app.setApplicationVersion("1.0")

    # 创建并显示窗口，使用命令行指定的URL
    window = IEBrowserWindow(args.url)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
