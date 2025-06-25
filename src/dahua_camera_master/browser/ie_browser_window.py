"""
IE浏览器窗口主模块
重构后的IE浏览器窗口实现
"""

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
from PySide6.QtAxContainer import QAxWidget
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

from dahua_camera_master.utils.browser_config import (
    BrowserConfigThread,
    BrowserConfigurationHelper,
)
from dahua_camera_master.utils.dpi_utils import (
    set_dpi_awareness,
    set_window_dpi,
    setup_qt_dpi_settings,
)


class IEBrowserWindow(QMainWindow):
    """优化的IE浏览器窗口"""

    def __init__(self, default_url: str = ""):
        super().__init__()
        self.default_url = default_url
        self.browser: Optional[QAxWidget] = None
        self.url_input: Optional[QLineEdit] = None
        self.status_bar: Optional[QStatusBar] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.config_thread: Optional[BrowserConfigThread] = None
        self.browser_config_helper: Optional[BrowserConfigurationHelper] = None
        self.error_timer: Optional[QTimer] = None

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

            # 创建浏览器组件
            self.browser = QAxWidget("{8856F961-340A-11D0-A96B-00C04FD705A2}")

            # 连接事件
            if hasattr(self.browser, "exception"):
                self.browser.exception.connect(self._handle_browser_exception)

            # 添加到布局
            self.centralWidget().layout().addWidget(self.browser, 1)

            # 强制设置浏览器DPI
            self._set_browser_dpi()

            # 创建配置助手
            self.browser_config_helper = BrowserConfigurationHelper(self.browser)

            # 配置浏览器
            self._configure_browser_sync()

            # 异步配置注册表
            self._configure_browser_async()

            # 延迟导航
            if self.default_url:
                QTimer.singleShot(1500, lambda: self._navigate_to_url(self.default_url))

            self._hide_progress("浏览器初始化完成")

        except Exception as e:
            self._hide_progress(f"浏览器初始化失败: {str(e)}")
            self.logger.error(f"浏览器初始化失败: {e}")
            self._show_error_message("初始化失败", f"无法创建IE浏览器组件:\n{str(e)}")

    def _set_browser_dpi(self):
        """设置浏览器组件DPI"""
        try:
            if self.browser and sys.platform == "win32":
                # 获取浏览器控件的窗口句柄
                hwnd = int(self.browser.winId())
                if hwnd:
                    set_window_dpi(hwnd)

        except Exception as e:
            self.logger.warning(f"浏览器DPI设置失败: {e}")

    def _configure_browser_sync(self):
        """同步配置浏览器属性"""
        if not self.browser_config_helper:
            return

        try:
            success = self.browser_config_helper.configure_sync_properties()
            if success:
                # 连接文档完成事件
                try:
                    if hasattr(self.browser, "DocumentComplete"):
                        self.browser.DocumentComplete.connect(
                            self._on_document_complete
                        )
                    else:
                        # 备用方法：设置定时器定期注入脚本
                        self._setup_error_suppression_timer()
                except Exception as e:
                    self.logger.warning(f"连接文档完成事件失败: {e}")
                    self._setup_error_suppression_timer()

        except Exception as e:
            self.logger.warning(f"浏览器同步配置失败: {e}")

    def _setup_error_suppression_timer(self):
        """设置错误抑制定时器"""
        self.error_timer = QTimer()
        self.error_timer.timeout.connect(self._inject_error_suppression)
        self.error_timer.start(5000)  # 每5秒执行一次

    def _inject_error_suppression(self):
        """注入错误抑制脚本"""
        if self.browser_config_helper:
            self.browser_config_helper.inject_error_suppression_script()

    def _configure_browser_async(self):
        """异步配置浏览器注册表"""
        if self.config_thread and self.config_thread.isRunning():
            return

        self.config_thread = BrowserConfigThread(self.browser)
        self.config_thread.config_finished.connect(self._on_config_finished)
        self.config_thread.start()

    def _on_config_finished(self, success: bool, message: str):
        """配置完成回调"""
        self.logger.info(f"异步配置完成: {message}")

    def _handle_browser_exception(self, code, source, desc, help_file):
        """处理浏览器异常"""
        self.logger.warning(f"浏览器异常已忽略: {desc}")

    def _on_navigate_clicked(self):
        """处理导航按钮点击"""
        url = self.url_input.text().strip()
        if not url:
            self._show_warning("请输入有效的网址")
            self.url_input.setFocus()
            return

        self._navigate_to_url(url)

    def _navigate_to_url(self, url: str):
        """导航到指定URL"""
        if not self.browser:
            self._show_warning("浏览器组件未初始化")
            return

        # 格式化URL
        formatted_url = self._format_url(url)
        self.logger.info(f"导航到: {formatted_url}")

        self._show_progress(f"正在加载 {formatted_url}...")

        # 更新地址栏
        if self.url_input.text() != formatted_url:
            self.url_input.setText(formatted_url)

        try:
            # 尝试导航
            success = self._try_navigate(formatted_url)

            if success:
                QTimer.singleShot(3000, lambda: self._hide_progress("页面加载完成"))
            else:
                self._hide_progress("导航失败")
                self._show_warning("无法访问该网址，请检查网络连接和URL格式")

        except Exception as e:
            self._hide_progress(f"导航失败: {str(e)}")
            self.logger.error(f"导航失败: {e}")

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

    def _try_navigate(self, url: str) -> bool:
        """尝试多种导航方法"""
        methods = [
            lambda: self.browser.dynamicCall(
                "Navigate2(QVariant,QVariant,QVariant,QVariant,QVariant)",
                url,
                0,
                "",
                "",
                "",
            ),
            lambda: self.browser.dynamicCall("Navigate(QString)", url),
            lambda: self._delayed_navigate(url),
        ]

        for i, method in enumerate(methods):
            try:
                method()
                self.logger.info(f"导航方法 {i + 1} 成功")
                return True
            except Exception as e:
                self.logger.warning(f"导航方法 {i + 1} 失败: {e}")

        return False

    def _delayed_navigate(self, url: str):
        """延迟导航方法"""
        self.browser.dynamicCall("Refresh()")
        QTimer.singleShot(
            500, lambda: self.browser.dynamicCall("Navigate(QString)", url)
        )

    def _refresh_page(self):
        """刷新当前页面"""
        if self.browser:
            try:
                self.browser.dynamicCall("Refresh()")
                self._show_progress("正在刷新...")
                QTimer.singleShot(2000, lambda: self._hide_progress("刷新完成"))
            except Exception as e:
                self.logger.error(f"刷新失败: {e}")

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
        if self.config_thread and self.config_thread.isRunning():
            self.config_thread.quit()
            self.config_thread.wait()

        if self.error_timer:
            self.error_timer.stop()

        event.accept()

    def _on_document_complete(self, disp, url):
        """文档加载完成事件处理"""
        try:
            if self.browser_config_helper:
                script = self.browser_config_helper.get_document_complete_script()

                # 尝试执行脚本
                try:
                    document = self.browser.dynamicCall("Document")
                    if document:
                        document.dynamicCall(
                            "execScript(QString,QString)", script, "JavaScript"
                        )
                except Exception:
                    pass

        except Exception as e:
            self.logger.warning(f"文档完成事件处理失败: {e}")


def main():
    """主函数"""
    # 在创建QApplication之前设置DPI
    set_dpi_awareness()

    # 设置Qt的高DPI设置
    setup_qt_dpi_settings()

    app = QApplication(sys.argv)

    # 禁用高DPI缩放
    app.setAttribute(Qt.AA_DisableHighDpiScaling, True)
    app.setAttribute(Qt.AA_Use96Dpi, True)

    app.setApplicationName("IE浏览器")
    app.setApplicationVersion("1.0")

    # 创建并显示窗口
    window = IEBrowserWindow("192.168.1.1")
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
