"""
IE COM组件使用示例
演示如何使用独立的IE COM组件
"""

import os
import sys

# 添加src目录到Python路径
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, "..", "src")
    src_dir = os.path.abspath(src_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from dahua_camera_master.browser.ie_com_widget import IEComWidget
from dahua_camera_master.utils.dpi_utils import configure_application_dpi


class IEComExampleWindow(QMainWindow):
    """IE COM组件示例窗口"""

    def __init__(self):
        super().__init__()
        self.ie_widget = None
        self.url_input = None
        self.status_bar = None

        self._init_ui()
        self._init_ie_widget()

    def _init_ui(self):
        """初始化界面"""
        self.setWindowTitle("IE COM组件示例")
        self.setGeometry(200, 200, 1000, 700)

        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 创建工具栏
        toolbar_layout = QHBoxLayout()

        # URL输入
        toolbar_layout.addWidget(QLabel("地址:"))
        self.url_input = QLineEdit()
        self.url_input.setText("http://192.168.1.1")
        self.url_input.returnPressed.connect(self._on_navigate)
        toolbar_layout.addWidget(self.url_input, 1)

        # 按钮
        nav_btn = QPushButton("跳转")
        nav_btn.clicked.connect(self._on_navigate)
        toolbar_layout.addWidget(nav_btn)

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self._on_refresh)
        toolbar_layout.addWidget(refresh_btn)

        back_btn = QPushButton("后退")
        back_btn.clicked.connect(self._on_back)
        toolbar_layout.addWidget(back_btn)

        forward_btn = QPushButton("前进")
        forward_btn.clicked.connect(self._on_forward)
        toolbar_layout.addWidget(forward_btn)

        stop_btn = QPushButton("停止")
        stop_btn.clicked.connect(self._on_stop)
        toolbar_layout.addWidget(stop_btn)

        # 测试按钮
        test_btn = QPushButton("测试脚本")
        test_btn.clicked.connect(self._on_test_script)
        toolbar_layout.addWidget(test_btn)

        main_layout.addLayout(toolbar_layout)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def _init_ie_widget(self):
        """初始化IE组件"""
        try:
            self.ie_widget = IEComWidget()

            # 连接信号
            self.ie_widget.navigation_started.connect(self._on_navigation_started)
            self.ie_widget.navigation_completed.connect(self._on_navigation_completed)
            self.ie_widget.navigation_error.connect(self._on_navigation_error)
            self.ie_widget.document_ready.connect(self._on_document_ready)
            self.ie_widget.progress_changed.connect(self._on_progress_changed)
            self.ie_widget.status_changed.connect(self._on_status_changed)
            self.ie_widget.title_changed.connect(self._on_title_changed)

            # 添加到布局
            self.centralWidget().layout().addWidget(self.ie_widget, 1)

            print("IE COM组件初始化成功")

        except Exception as e:
            print(f"IE COM组件初始化失败: {e}")

    def _on_navigate(self):
        """导航按钮点击"""
        if self.ie_widget:
            url = self.url_input.text().strip()
            if url:
                success = self.ie_widget.navigate(url)
                print(f"导航到 {url}: {'成功' if success else '失败'}")

    def _on_refresh(self):
        """刷新按钮点击"""
        if self.ie_widget:
            success = self.ie_widget.refresh()
            print(f"刷新: {'成功' if success else '失败'}")

    def _on_back(self):
        """后退按钮点击"""
        if self.ie_widget:
            success = self.ie_widget.go_back()
            print(f"后退: {'成功' if success else '失败'}")

    def _on_forward(self):
        """前进按钮点击"""
        if self.ie_widget:
            success = self.ie_widget.go_forward()
            print(f"前进: {'成功' if success else '失败'}")

    def _on_stop(self):
        """停止按钮点击"""
        if self.ie_widget:
            success = self.ie_widget.stop()
            print(f"停止: {'成功' if success else '失败'}")

    def _on_test_script(self):
        """测试脚本按钮点击"""
        if self.ie_widget:
            script = "alert('Hello from IE COM Widget!');"
            result = self.ie_widget.execute_script(script)
            print(f"执行脚本结果: {result}")

    # 信号处理方法
    def _on_navigation_started(self, url):
        """导航开始"""
        print(f"开始导航: {url}")
        self.status_bar.showMessage(f"正在加载: {url}")

    def _on_navigation_completed(self, url):
        """导航完成"""
        print(f"导航完成: {url}")
        self.status_bar.showMessage(f"加载完成: {url}")

    def _on_navigation_error(self, url, error):
        """导航错误"""
        print(f"导航错误: {url} - {error}")
        self.status_bar.showMessage(f"加载失败: {error}")

    def _on_document_ready(self):
        """文档就绪"""
        print("文档就绪")
        if self.ie_widget:
            title = self.ie_widget.title
            if title:
                self.setWindowTitle(f"IE COM示例 - {title}")

    def _on_progress_changed(self, progress):
        """进度变化"""
        print(f"加载进度: {progress}%")

    def _on_status_changed(self, status):
        """状态变化"""
        if status:
            print(f"状态: {status}")

    def _on_title_changed(self, title):
        """标题变化"""
        if title:
            print(f"标题: {title}")
            self.setWindowTitle(f"IE COM示例 - {title}")

    def closeEvent(self, event):
        """关闭事件"""
        if self.ie_widget:
            self.ie_widget.cleanup()
        event.accept()


def main():
    """主函数"""
    # 配置DPI
    configure_application_dpi()

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DisableHighDpiScaling, True)
    app.setAttribute(Qt.AA_Use96Dpi, True)

    window = IEComExampleWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
