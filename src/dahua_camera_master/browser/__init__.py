"""
Browser包初始化模块
导出浏览器相关的类和函数
"""

# IE浏览器窗口
from .ie_browser_window import IEBrowserWindow, main

# 浏览器工厂
from .browser_factory import (
    BrowserFactory,
    create_browser_app,
    main_browser_standalone,
)

# IE COM浏览器（原始版本，兼容性保留）
from .ie_com import (
    IEBrowserWindow as OriginalIEBrowserWindow,
    set_dpi_awareness as original_set_dpi_awareness,
    is_admin as original_is_admin,
    BrowserConfigThread as OriginalBrowserConfigThread,
    main as original_main,
)

__all__ = [
    # 重构后的版本（推荐使用）
    "IEBrowserWindow",
    "main",
    # 浏览器工厂
    "BrowserFactory",
    "create_browser_app",
    "main_browser_standalone",
    # 原始版本（兼容性保留）
    "OriginalIEBrowserWindow",
    "original_set_dpi_awareness",
    "original_is_admin",
    "OriginalBrowserConfigThread",
    "original_main",
]
