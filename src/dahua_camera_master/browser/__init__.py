"""
Browser包初始化模块
导出浏览器相关的类和函数
"""

# IE浏览器窗口
# 浏览器工厂
from .browser_factory import (
    BrowserFactory,
    create_browser_app,
    main_browser_standalone,
)
from .ie_browser_window import IEBrowserWindow, main

# IE COM组件
from .ie_com_widget import IEComWidget, NavigationState

__all__ = [
    # 重构后的版本（推荐使用）
    "IEBrowserWindow",
    "main",
    # 浏览器工厂
    "BrowserFactory",
    "create_browser_app",
    "main_browser_standalone",
    # IE COM组件
    "IEComWidget",
    "NavigationState",
]
