"""
DPI工具模块
专门处理Windows DPI相关设置和配置
"""

import sys
import os
import logging
import ctypes
from typing import Optional


def set_dpi_awareness():
    """
    设置DPI感知，强制100%缩放

    在Windows上设置进程的DPI感知模式，确保应用程序在高DPI显示器上
    以100%缩放显示，避免模糊问题。
    """
    try:
        # Windows DPI 感知设置
        if sys.platform == "win32":
            # 设置进程DPI感知
            try:
                # Windows 10 版本 1703 及更高版本
                ctypes.windll.shcore.SetProcessDpiAwareness(
                    0
                )  # 0 = DPI_AWARENESS_UNAWARE
                logging.debug("使用 SetProcessDpiAwareness 设置DPI感知")
            except Exception:
                try:
                    # 较旧的Windows版本
                    ctypes.windll.user32.SetProcessDPIAware()
                    logging.debug("使用 SetProcessDPIAware 设置DPI感知")
                except Exception:
                    logging.warning("无法设置基本DPI感知")

            # 设置DPI缩放覆盖
            try:
                # 设置DPI感知上下文
                ctypes.windll.user32.SetProcessDpiAwarenessContext(
                    -1
                )  # DPI_AWARENESS_CONTEXT_UNAWARE
                logging.debug("使用 SetProcessDpiAwarenessContext 设置DPI感知")
            except Exception:
                logging.debug("无法设置DPI感知上下文")

        logging.info("DPI感知设置完成")

    except Exception as e:
        logging.warning(f"DPI设置失败: {e}")


def set_window_dpi(hwnd: int):
    """
    设置指定窗口的DPI

    Args:
        hwnd: 窗口句柄
    """
    try:
        if hwnd and sys.platform == "win32":
            # 设置窗口的DPI感知
            try:
                ctypes.windll.user32.SetWindowDpiAwarenessContext(hwnd, -1)
                logging.debug(f"为窗口 {hwnd} 设置DPI感知上下文")
            except Exception as e:
                logging.debug(f"无法为窗口 {hwnd} 设置DPI感知上下文: {e}")

            # 强制重绘窗口
            try:
                ctypes.windll.user32.InvalidateRect(hwnd, None, True)
                ctypes.windll.user32.UpdateWindow(hwnd)
                logging.debug(f"窗口 {hwnd} 重绘完成")
            except Exception as e:
                logging.debug(f"窗口 {hwnd} 重绘失败: {e}")

        logging.info("窗口DPI设置完成")

    except Exception as e:
        logging.warning(f"窗口DPI设置失败: {e}")


def setup_qt_dpi_settings():
    """
    设置Qt的DPI相关环境变量

    配置Qt应用程序的DPI处理方式，确保在高DPI显示器上
    正确显示而不进行自动缩放。
    """
    try:
        # 设置Qt的高DPI设置
        dpi_env_vars = {
            "QT_AUTO_SCREEN_SCALE_FACTOR": "0",
            "QT_SCALE_FACTOR": "1",
            "QT_SCREEN_SCALE_FACTORS": "1",
            "QT_DPI_OVERRIDE": "96",
            "QT_DEVICE_PIXEL_RATIO": "1",
        }

        for key, value in dpi_env_vars.items():
            os.environ[key] = value
            logging.debug(f"设置环境变量: {key}={value}")

        logging.info("Qt DPI环境变量设置完成")

    except Exception as e:
        logging.warning(f"Qt DPI环境变量设置失败: {e}")


def get_system_dpi() -> Optional[int]:
    """
    获取系统DPI设置

    Returns:
        int: 系统DPI值，如果获取失败返回None
    """
    try:
        if sys.platform == "win32":
            # 获取主显示器的DPI
            hdc = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
            ctypes.windll.user32.ReleaseDC(0, hdc)
            logging.debug(f"系统DPI: {dpi}")
            return dpi
        return None
    except Exception as e:
        logging.warning(f"获取系统DPI失败: {e}")
        return None


def get_dpi_scale_factor() -> float:
    """
    获取DPI缩放因子

    Returns:
        float: DPI缩放因子 (1.0 = 100%, 1.25 = 125%, 等等)
    """
    try:
        dpi = get_system_dpi()
        if dpi:
            # 标准DPI是96
            scale_factor = dpi / 96.0
            logging.debug(f"DPI缩放因子: {scale_factor}")
            return scale_factor
        return 1.0
    except Exception as e:
        logging.warning(f"获取DPI缩放因子失败: {e}")
        return 1.0


def configure_application_dpi():
    """
    为应用程序配置完整的DPI设置

    这是一个便捷函数，执行所有必要的DPI配置步骤。
    应该在创建QApplication之前调用。
    """
    try:
        logging.info("开始配置应用程序DPI设置")

        # 1. 设置Qt环境变量
        setup_qt_dpi_settings()

        # 2. 设置系统DPI感知
        set_dpi_awareness()

        # 3. 记录当前DPI信息
        dpi = get_system_dpi()
        scale_factor = get_dpi_scale_factor()

        logging.info(f"DPI配置完成 - 系统DPI: {dpi}, 缩放因子: {scale_factor}")

    except Exception as e:
        logging.error(f"DPI配置失败: {e}")


class DPIManager:
    """DPI管理器类，提供更高级的DPI管理功能"""

    def __init__(self):
        self.original_dpi = None
        self.is_configured = False

    def configure(self, force_100_percent: bool = True):
        """
        配置DPI设置

        Args:
            force_100_percent: 是否强制100%缩放
        """
        try:
            if self.is_configured:
                logging.debug("DPI已经配置过，跳过重复配置")
                return

            self.original_dpi = get_system_dpi()

            if force_100_percent:
                configure_application_dpi()
            else:
                # 只设置基本的DPI感知
                set_dpi_awareness()

            self.is_configured = True
            logging.info("DPI管理器配置完成")

        except Exception as e:
            logging.error(f"DPI管理器配置失败: {e}")

    def get_status(self) -> dict:
        """
        获取DPI状态信息

        Returns:
            dict: 包含DPI相关信息的字典
        """
        return {
            "is_configured": self.is_configured,
            "original_dpi": self.original_dpi,
            "current_dpi": get_system_dpi(),
            "scale_factor": get_dpi_scale_factor(),
        }


# 创建全局DPI管理器实例
dpi_manager = DPIManager()


def get_dpi_manager() -> DPIManager:
    """
    获取全局DPI管理器实例

    Returns:
        DPIManager: 全局DPI管理器实例
    """
    return dpi_manager
