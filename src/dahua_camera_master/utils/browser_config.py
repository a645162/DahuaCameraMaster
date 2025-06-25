"""
浏览器配置模块
包含浏览器配置线程和相关工具函数
"""

import logging
from PySide6.QtCore import QThread, Signal
from PySide6.QtAxContainer import QAxWidget

from ..utils.system_utils import is_admin
from ..utils.registry_utils import configure_ie_registry


class BrowserConfigThread(QThread):
    """浏览器配置线程，避免阻塞UI"""

    config_finished = Signal(bool, str)

    def __init__(self, browser_widget: QAxWidget):
        super().__init__()
        self.browser = browser_widget

    def run(self):
        try:
            # 检查是否有管理员权限
            if is_admin():
                success, message = configure_ie_registry()
                self.config_finished.emit(success, message)
            else:
                self.config_finished.emit(True, "跳过注册表配置（需要管理员权限）")
        except Exception as e:
            self.config_finished.emit(False, f"配置失败: {str(e)}")


class BrowserConfigurationHelper:
    """浏览器配置辅助类"""

    def __init__(self, browser_widget: QAxWidget):
        self.browser = browser_widget
        self.logger = logging.getLogger(__name__)

    def configure_sync_properties(self) -> bool:
        """同步配置浏览器属性"""
        if not self.browser:
            return False

        try:
            # 显示管理员权限状态
            admin_status = "有管理员权限" if is_admin() else "无管理员权限"
            self.logger.info(f"当前权限状态: {admin_status}")

            # 完整的错误抑制配置
            error_suppression_configs = [
                ("Silent", True),
                ("ScriptErrorsSuppressed", True),
            ]

            # 如果没有管理员权限，使用更多的客户端配置来补偿
            if not is_admin():
                error_suppression_configs.extend(
                    [
                        ("ScriptDebugEnabled", False),
                        ("DisableScriptDebuggerException", True),
                    ]
                )

            for prop, value in error_suppression_configs:
                try:
                    self.browser.setProperty(prop, value)
                    # 尝试多种方法设置属性
                    for method_prefix in ["put_", "set", ""]:
                        try:
                            if method_prefix == "":
                                self.browser.dynamicCall(
                                    f"{prop}({type(value).__name__.lower()})", value
                                )
                            else:
                                self.browser.dynamicCall(
                                    f"{method_prefix}{prop}({type(value).__name__.lower()})",
                                    value,
                                )
                            break
                        except Exception:
                            continue
                except Exception as e:
                    self.logger.warning(f"设置属性 {prop} 失败: {e}")

            # 高级配置
            self._apply_advanced_configs()

            self.logger.info("浏览器同步配置完成")
            return True

        except Exception as e:
            self.logger.warning(f"浏览器同步配置失败: {e}")
            return False

    def _apply_advanced_configs(self):
        """应用高级配置"""
        advanced_configs = [
            ("put_RegisterAsBrowser(bool)", True),
            ("put_RegisterAsDropTarget(bool)", True),
            ("put_Border3D(bool)", False),
            ("put_Offline(bool)", False),
            ("put_TheaterMode(bool)", False),
            ("put_AddressBar(bool)", False),
            ("put_StatusBar(bool)", False),
            ("put_ToolBar(bool)", False),
            ("put_MenuBar(bool)", False),
        ]

        for method, value in advanced_configs:
            try:
                self.browser.dynamicCall(method, value)
            except Exception as e:
                self.logger.warning(f"调用方法 {method} 失败: {e}")

    def inject_error_suppression_script(self) -> bool:
        """注入错误抑制脚本"""
        try:
            if not self.browser:
                return False

            script = """
            try {
                window.onerror = function() { return true; };
                window.addEventListener('error', function(e) { 
                    e.preventDefault(); 
                    e.stopPropagation(); 
                    return false; 
                }, true);
                if (window.console) {
                    window.console.error = function() {};
                    window.console.warn = function() {};
                }
            } catch(e) {}
            """

            document = self.browser.dynamicCall("Document")
            if document:
                try:
                    document.dynamicCall(
                        "execScript(QString,QString)", script, "JavaScript"
                    )
                    return True
                except Exception:
                    pass
            return False
        except Exception:
            return False

    def get_document_complete_script(self) -> str:
        """获取文档完成时要执行的脚本"""
        return """
        window.onerror = function(msg, url, line, col, error) {
            return true; // 阻止默认错误处理
        };
        
        window.addEventListener('error', function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }, true);
        
        // 禁用控制台错误
        if (window.console && window.console.error) {
            window.console.error = function() {};
        }
        """
