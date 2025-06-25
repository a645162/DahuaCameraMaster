"""
系统工具模块
包含管理员权限检查等系统相关功能
DPI相关功能已移至 dpi_utils.py 模块
"""

import ctypes
import sys


def is_admin() -> bool:
    """检查是否有管理员权限"""
    try:
        if sys.platform == "win32":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        return False
    except Exception:
        return False
