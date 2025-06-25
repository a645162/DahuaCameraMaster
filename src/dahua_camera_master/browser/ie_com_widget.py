"""
IE COM组件封装类
提供IE WebBrowser控件的完整功能封装
"""

import logging
from enum import Enum
from typing import Any, Optional

from PySide6.QtAxContainer import QAxWidget
from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget


class NavigationState(Enum):
    """导航状态枚举"""

    READY = "ready"
    NAVIGATING = "navigating"
    COMPLETE = "complete"
    ERROR = "error"


class IEComWidget(QWidget):
    """
    IE COM组件封装类
    提供完整的WebBrowser控件功能
    """

    # 信号定义
    navigation_started = Signal(str)  # 导航开始
    navigation_completed = Signal(str)  # 导航完成
    navigation_error = Signal(str, str)  # 导航错误 (url, error_msg)
    document_ready = Signal()  # 文档就绪
    progress_changed = Signal(int)  # 进度变化 (0-100)
    status_changed = Signal(str)  # 状态变化
    title_changed = Signal(str)  # 标题变化

    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化IE COM组件

        Args:
            parent: 父窗口
        """
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)
        self._browser: Optional[QAxWidget] = None
        self._current_url: str = ""
        self._state: NavigationState = NavigationState.READY
        self._error_suppression_timer: Optional[QTimer] = None

        self._init_ui()
        self._init_browser()

    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def _init_browser(self):
        """初始化浏览器组件"""
        try:
            # 创建IE WebBrowser控件
            self._browser = QAxWidget("{8856F961-340A-11D0-A96B-00C04FD705A2}")

            # 连接事件
            self._connect_events()

            # 配置浏览器属性
            self._configure_browser()

            # 添加到布局
            self.layout().addWidget(self._browser)

            # 启动错误抑制
            self._setup_error_suppression()

            self.logger.info("IE COM组件初始化完成")

        except Exception as e:
            self.logger.error(f"IE COM组件初始化失败: {e}")
            raise

    def _connect_events(self):
        """连接浏览器事件"""
        if not self._browser:
            return

        try:
            # 导航相关事件
            if hasattr(self._browser, "BeforeNavigate2"):
                self._browser.BeforeNavigate2.connect(self._on_before_navigate)

            if hasattr(self._browser, "NavigateComplete2"):
                self._browser.NavigateComplete2.connect(self._on_navigate_complete)

            if hasattr(self._browser, "DocumentComplete"):
                self._browser.DocumentComplete.connect(self._on_document_complete)

            # 进度事件
            if hasattr(self._browser, "ProgressChange"):
                self._browser.ProgressChange.connect(self._on_progress_change)

            # 状态事件
            if hasattr(self._browser, "StatusTextChange"):
                self._browser.StatusTextChange.connect(self._on_status_change)

            # 标题事件
            if hasattr(self._browser, "TitleChange"):
                self._browser.TitleChange.connect(self._on_title_change)

            # 错误事件
            if hasattr(self._browser, "NavigateError"):
                self._browser.NavigateError.connect(self._on_navigate_error)

            # 异常处理
            if hasattr(self._browser, "exception"):
                self._browser.exception.connect(self._on_browser_exception)

        except Exception as e:
            self.logger.warning(f"连接浏览器事件失败: {e}")

    def _configure_browser(self):
        """配置浏览器属性"""
        if not self._browser:
            return

        try:
            # 基本配置
            properties = {
                "Silent": True,  # 禁用脚本错误对话框
                "ScriptErrorsSuppressed": True,  # 抑制脚本错误
                "ScriptDebugEnabled": False,  # 禁用脚本调试
                "RegisterAsBrowser": True,  # 注册为浏览器
                "RegisterAsDropTarget": True,  # 支持拖放
                "Border3D": False,  # 禁用3D边框
                "Offline": False,  # 在线模式
                "TheaterMode": False,  # 禁用剧院模式
                "AddressBar": False,  # 隐藏地址栏
                "StatusBar": False,  # 隐藏状态栏
                "ToolBar": False,  # 隐藏工具栏
                "MenuBar": False,  # 隐藏菜单栏
            }

            for prop, value in properties.items():
                try:
                    self._browser.dynamicCall(f"put_{prop}(bool)", value)
                except Exception as e:
                    self.logger.debug(f"设置属性 {prop} 失败: {e}")

        except Exception as e:
            self.logger.warning(f"配置浏览器属性失败: {e}")

    def _setup_error_suppression(self):
        """设置错误抑制"""
        try:
            self._error_suppression_timer = QTimer()
            self._error_suppression_timer.timeout.connect(self._inject_error_suppression)
            self._error_suppression_timer.start(5000)  # 每5秒执行一次
        except Exception as e:
            self.logger.warning(f"设置错误抑制失败: {e}")

    def _inject_error_suppression(self):
        """注入错误抑制脚本"""
        try:
            script = """
            window.onerror = function(msg, url, line) {
                return true;
            };
            if (typeof window.addEventListener !== 'undefined') {
                window.addEventListener('error', function(e) {
                    e.preventDefault();
                    return false;
                }, true);
            }
            """
            self.execute_script(script)
        except Exception:
            pass

    # 事件处理方法
    def _on_before_navigate(self, disp, url, flags, target_frame, post_data, headers, cancel):
        """导航开始前事件"""
        try:
            url_str = str(url) if url else ""
            self._current_url = url_str
            self._state = NavigationState.NAVIGATING
            self.navigation_started.emit(url_str)
            self.logger.debug(f"开始导航: {url_str}")
        except Exception as e:
            self.logger.warning(f"处理导航开始事件失败: {e}")

    def _on_navigate_complete(self, disp, url):
        """导航完成事件"""
        try:
            url_str = str(url) if url else ""
            self._current_url = url_str
            self._state = NavigationState.COMPLETE
            self.navigation_completed.emit(url_str)
            self.logger.debug(f"导航完成: {url_str}")
        except Exception as e:
            self.logger.warning(f"处理导航完成事件失败: {e}")

    def _on_document_complete(self, disp, url):
        """文档完成事件"""
        try:
            self._state = NavigationState.READY
            self.document_ready.emit()
            self._inject_error_suppression()  # 注入错误抑制脚本
            self.logger.debug(f"文档加载完成: {url}")
        except Exception as e:
            self.logger.warning(f"处理文档完成事件失败: {e}")

    def _on_progress_change(self, progress, progress_max):
        """进度变化事件"""
        try:
            if progress_max > 0:
                percentage = int((progress / progress_max) * 100)
                self.progress_changed.emit(percentage)
        except Exception as e:
            self.logger.warning(f"处理进度变化事件失败: {e}")

    def _on_status_change(self, text):
        """状态变化事件"""
        try:
            status_text = str(text) if text else ""
            self.status_changed.emit(status_text)
        except Exception as e:
            self.logger.warning(f"处理状态变化事件失败: {e}")

    def _on_title_change(self, text):
        """标题变化事件"""
        try:
            title_text = str(text) if text else ""
            self.title_changed.emit(title_text)
        except Exception as e:
            self.logger.warning(f"处理标题变化事件失败: {e}")

    def _on_navigate_error(self, disp, url, target_frame, status_code, cancel):
        """导航错误事件"""
        try:
            url_str = str(url) if url else ""
            error_msg = f"HTTP错误: {status_code}"
            self._state = NavigationState.ERROR
            self.navigation_error.emit(url_str, error_msg)
            self.logger.warning(f"导航错误: {url_str} - {error_msg}")
        except Exception as e:
            self.logger.warning(f"处理导航错误事件失败: {e}")

    def _on_browser_exception(self, code, source, desc, help_file):
        """浏览器异常事件"""
        try:
            error_msg = f"异常: {desc}"
            self.logger.debug(f"浏览器异常已忽略: {error_msg}")
        except Exception as e:
            self.logger.warning(f"处理浏览器异常事件失败: {e}")

    # 公共API方法
    def navigate(self, url: str) -> bool:
        """
        导航到指定URL

        Args:
            url: 目标URL

        Returns:
            bool: 是否成功启动导航
        """
        if not self._browser:
            self.logger.error("浏览器组件未初始化")
            return False

        try:
            # 格式化URL
            formatted_url = self._format_url(url)
            self.logger.info(f"导航到: {formatted_url}")

            # 尝试多种导航方法
            methods = [
                lambda: self._browser.dynamicCall(
                    "Navigate2(QVariant,QVariant,QVariant,QVariant,QVariant)",
                    formatted_url,
                    0,
                    "",
                    "",
                    "",
                ),
                lambda: self._browser.dynamicCall("Navigate(QString)", formatted_url),
            ]

            for i, method in enumerate(methods):
                try:
                    method()
                    self.logger.debug(f"导航方法 {i + 1} 成功")
                    return True
                except Exception as e:
                    self.logger.debug(f"导航方法 {i + 1} 失败: {e}")

            return False

        except Exception as e:
            self.logger.error(f"导航失败: {e}")
            return False

    def refresh(self) -> bool:
        """
        刷新当前页面

        Returns:
            bool: 是否成功
        """
        if not self._browser:
            return False

        try:
            self._browser.dynamicCall("Refresh()")
            return True
        except Exception as e:
            self.logger.error(f"刷新失败: {e}")
            return False

    def stop(self) -> bool:
        """
        停止加载

        Returns:
            bool: 是否成功
        """
        if not self._browser:
            return False

        try:
            self._browser.dynamicCall("Stop()")
            return True
        except Exception as e:
            self.logger.error(f"停止加载失败: {e}")
            return False

    def go_back(self) -> bool:
        """
        后退

        Returns:
            bool: 是否成功
        """
        if not self._browser:
            return False

        try:
            self._browser.dynamicCall("GoBack()")
            return True
        except Exception as e:
            self.logger.error(f"后退失败: {e}")
            return False

    def go_forward(self) -> bool:
        """
        前进

        Returns:
            bool: 是否成功
        """
        if not self._browser:
            return False

        try:
            self._browser.dynamicCall("GoForward()")
            return True
        except Exception as e:
            self.logger.error(f"前进失败: {e}")
            return False

    def go_home(self) -> bool:
        """
        跳转到主页

        Returns:
            bool: 是否成功
        """
        if not self._browser:
            return False

        try:
            self._browser.dynamicCall("GoHome()")
            return True
        except Exception as e:
            self.logger.error(f"跳转主页失败: {e}")
            return False

    def execute_script(self, script: str) -> Any:
        """
        执行JavaScript脚本

        Args:
            script: JavaScript代码

        Returns:
            脚本执行结果
        """
        if not self._browser:
            return None

        try:
            document = self._browser.dynamicCall("Document")
            if document:
                return document.dynamicCall("execScript(QString,QString)", script, "JavaScript")
        except Exception as e:
            self.logger.warning(f"执行脚本失败: {e}")

        return None

    def get_document(self) -> Any:
        """
        获取文档对象

        Returns:
            文档对象
        """
        if not self._browser:
            return None

        try:
            return self._browser.dynamicCall("Document")
        except Exception as e:
            self.logger.warning(f"获取文档对象失败: {e}")
            return None

    def get_element_by_id(self, element_id: str) -> Any:
        """
        通过ID获取元素

        Args:
            element_id: 元素ID

        Returns:
            元素对象
        """
        try:
            document = self.get_document()
            if document:
                return document.dynamicCall("getElementById(QString)", element_id)
        except Exception as e:
            self.logger.warning(f"获取元素失败: {e}")

        return None

    def set_element_value(self, element_id: str, value: str) -> bool:
        """
        设置元素值

        Args:
            element_id: 元素ID
            value: 要设置的值

        Returns:
            bool: 是否成功
        """
        try:
            element = self.get_element_by_id(element_id)
            if element:
                element.dynamicCall("put_value(QString)", value)
                return True
        except Exception as e:
            self.logger.warning(f"设置元素值失败: {e}")

        return False

    def click_element(self, element_id: str) -> bool:
        """
        点击元素

        Args:
            element_id: 元素ID

        Returns:
            bool: 是否成功
        """
        try:
            element = self.get_element_by_id(element_id)
            if element:
                element.dynamicCall("click()")
                return True
        except Exception as e:
            self.logger.warning(f"点击元素失败: {e}")

        return False

    def _format_url(self, url: str) -> str:
        """格式化URL"""
        url = url.strip()
        if not url:
            return ""

        if not url.startswith(("http://", "https://", "ftp://", "file://")):
            if "." in url:
                url = "http://" + url

        return url

    # 属性获取方法
    @property
    def current_url(self) -> str:
        """获取当前URL"""
        return self._current_url

    @property
    def state(self) -> NavigationState:
        """获取当前状态"""
        return self._state

    @property
    def title(self) -> str:
        """获取页面标题"""
        if not self._browser:
            return ""

        try:
            document = self.get_document()
            if document:
                return str(document.dynamicCall("title"))
        except Exception:
            pass

        return ""

    @property
    def can_go_back(self) -> bool:
        """是否可以后退"""
        if not self._browser:
            return False

        try:
            history = self._browser.dynamicCall("Application.History")
            if history:
                return history.dynamicCall("Length") > 1
        except Exception:
            pass

        return False

    @property
    def can_go_forward(self) -> bool:
        """是否可以前进"""
        # IE WebBrowser控件没有直接的方法检查是否可以前进
        # 这里返回False，实际使用时可以尝试调用go_forward()
        return False

    def cleanup(self):
        """清理资源"""
        try:
            if self._error_suppression_timer:
                self._error_suppression_timer.stop()
                self._error_suppression_timer = None

            if self._browser:
                self._browser = None

        except Exception as e:
            self.logger.warning(f"清理资源失败: {e}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.cleanup()
        super().closeEvent(event)


if __name__ == "__main__":
    """
    IE COM组件独立测试
    演示IE COM组件的基本功能
    """
    import os
    import sys

    # 添加src目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, "..", "..", "..")
    src_dir = os.path.abspath(src_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    from PySide6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    class IEComTestWindow(QMainWindow):
        """IE COM组件测试窗口"""

        def __init__(self):
            super().__init__()
            self.ie_widget = None
            self.url_input = None

            self._init_ui()
            self._init_ie_widget()

        def _init_ui(self):
            """初始化界面"""
            self.setWindowTitle("IE COM组件测试")
            self.setGeometry(150, 150, 1000, 700)

            # 创建中央控件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)

            # 创建简单的工具栏
            toolbar_layout = QHBoxLayout()

            # URL输入
            toolbar_layout.addWidget(QLabel("测试地址:"))
            self.url_input = QLineEdit()
            self.url_input.setText("http://192.168.1.1")
            self.url_input.returnPressed.connect(self._on_navigate)
            toolbar_layout.addWidget(self.url_input, 1)

            # 基本按钮
            nav_btn = QPushButton("跳转")
            nav_btn.clicked.connect(self._on_navigate)
            toolbar_layout.addWidget(nav_btn)

            refresh_btn = QPushButton("刷新")
            refresh_btn.clicked.connect(self._on_refresh)
            toolbar_layout.addWidget(refresh_btn)

            test_btn = QPushButton("测试脚本")
            test_btn.clicked.connect(self._on_test_script)
            toolbar_layout.addWidget(test_btn)

            main_layout.addLayout(toolbar_layout)

        def _init_ie_widget(self):
            """初始化IE组件"""
            try:
                self.ie_widget = IEComWidget()

                # 连接主要信号
                self.ie_widget.navigation_started.connect(lambda url: print(f"🚀 开始导航: {url}"))
                self.ie_widget.navigation_completed.connect(lambda url: print(f"✅ 导航完成: {url}"))
                self.ie_widget.navigation_error.connect(lambda url, error: print(f"❌ 导航错误: {url} - {error}"))
                self.ie_widget.document_ready.connect(lambda: print("📄 文档就绪"))
                self.ie_widget.progress_changed.connect(lambda progress: print(f"📊 加载进度: {progress}%"))
                self.ie_widget.title_changed.connect(lambda title: self.setWindowTitle(f"IE COM测试 - {title}"))

                # 添加到布局
                self.centralWidget().layout().addWidget(self.ie_widget, 1)

                print("✅ IE COM组件初始化成功")

            except Exception as e:
                print(f"❌ IE COM组件初始化失败: {e}")

        def _on_navigate(self):
            """导航按钮点击"""
            if self.ie_widget:
                url = self.url_input.text().strip()
                if url:
                    print(f"🌐 尝试导航到: {url}")
                    success = self.ie_widget.navigate(url)
                    print(f"导航启动: {'成功' if success else '失败'}")

        def _on_refresh(self):
            """刷新按钮点击"""
            if self.ie_widget:
                print("🔄 执行页面刷新")
                success = self.ie_widget.refresh()
                print(f"刷新: {'成功' if success else '失败'}")

        def _on_test_script(self):
            """测试脚本按钮点击"""
            if self.ie_widget:
                print("🔧 执行测试脚本")
                test_scripts = [
                    "alert('IE COM组件脚本测试成功！');",
                    "console.log('IE COM Widget Test');",
                    "document.title = 'IE COM测试页面';",
                ]

                for i, script in enumerate(test_scripts, 1):
                    try:
                        result = self.ie_widget.execute_script(script)
                        print(f"脚本 {i} 执行结果: {result}")
                    except Exception as e:
                        print(f"脚本 {i} 执行失败: {e}")

        def closeEvent(self, event):
            """关闭事件"""
            print("🔚 关闭IE COM组件测试窗口")
            if self.ie_widget:
                self.ie_widget.cleanup()
            event.accept()

    def main():
        """主函数"""
        print("🚀 启动IE COM组件测试")

        app = QApplication(sys.argv)

        # 创建测试窗口
        window = IEComTestWindow()
        window.show()

        print("✅ IE COM组件测试窗口已启动")
        print("📝 测试说明:")
        print("   - 默认会加载百度首页")
        print("   - 可以输入其他URL进行测试")
        print("   - 点击'测试脚本'按钮执行JavaScript测试")
        print("   - 观察控制台输出查看事件响应")

        return app.exec()

    sys.exit(main())
