"""
Utils包初始化模块
导出常用的工具函数和类
"""

# 系统工具
# 浏览器配置工具
from .browser_config import (
    BrowserConfigThread,
    BrowserConfigurationHelper,
)

# DPI工具
from .dpi_utils import (
    DPIManager,
    configure_application_dpi,
    get_dpi_manager,
    get_dpi_scale_factor,
    get_system_dpi,
    set_dpi_awareness,
    set_window_dpi,
    setup_qt_dpi_settings,
)

# 注册表工具
from .registry_utils import (
    configure_ie_registry,
    get_registry_configs,
)
from .system_utils import is_admin

__all__ = [
    # 系统工具
    "is_admin",
    # DPI工具
    "set_dpi_awareness",
    "set_window_dpi",
    "setup_qt_dpi_settings",
    "configure_application_dpi",
    "get_system_dpi",
    "get_dpi_scale_factor",
    "get_dpi_manager",
    "DPIManager",
    # 注册表工具
    "configure_ie_registry",
    "get_registry_configs",
    # 浏览器配置工具
    "BrowserConfigThread",
    "BrowserConfigurationHelper",
]
