"""
注册表配置工具模块
用于IE浏览器相关的注册表设置
"""

import logging
from typing import List, Tuple


def configure_ie_registry() -> Tuple[bool, str]:
    """
    配置IE注册表设置

    Returns:
        Tuple[bool, str]: (成功状态, 消息)
    """
    try:
        import winreg

        # 配置多个IE功能控制项
        registry_configs = [
            # 浏览器仿真模式
            (
                r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_BROWSER_EMULATION",
                "python.exe",
                11001,
            ),
            # 禁用脚本错误对话框
            (
                r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_DISABLE_SCRIPT_DEBUGGER",
                "python.exe",
                1,
            ),
            # 禁用脚本调试
            (
                r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_SCRIPTDEBUGGER_ERRORDIALOG",
                "python.exe",
                0,
            ),
            # 启用GPU渲染
            (
                r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_GPU_RENDERING",
                "python.exe",
                1,
            ),
            # 禁用安全带
            (
                r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_SECURITYBAND",
                "python.exe",
                0,
            ),
            # 启用现代DOM
            (
                r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_NINPUT_LEGACYMODE",
                "python.exe",
                0,
            ),
            # 禁用信息栏
            (
                r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_LOCALMACHINE_LOCKDOWN",
                "python.exe",
                0,
            ),
        ]

        success_count = 0
        for key_path, value_name, value_data in registry_configs:
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                winreg.CloseKey(key)
                success_count += 1
            except Exception:
                # 如果键不存在，尝试创建
                try:
                    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                    winreg.CloseKey(key)
                    success_count += 1
                except Exception:
                    logging.warning(f"无法设置注册表项: {key_path}")

        message = f"成功配置 {success_count}/{len(registry_configs)} 个注册表项"
        logging.info(message)
        return True, message

    except Exception as e:
        error_msg = f"注册表设置失败: {e}"
        logging.warning(error_msg)
        return False, error_msg


def get_registry_configs() -> List[Tuple[str, str, int]]:
    """
    获取IE注册表配置项列表

    Returns:
        List[Tuple[str, str, int]]: (键路径, 值名称, 值数据) 的列表
    """
    return [
        # 浏览器仿真模式
        (
            r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_BROWSER_EMULATION",
            "python.exe",
            11001,
        ),
        # 禁用脚本错误对话框
        (
            r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_DISABLE_SCRIPT_DEBUGGER",
            "python.exe",
            1,
        ),
        # 禁用脚本调试
        (
            r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_SCRIPTDEBUGGER_ERRORDIALOG",
            "python.exe",
            0,
        ),
        # 启用GPU渲染
        (
            r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_GPU_RENDERING",
            "python.exe",
            1,
        ),
        # 禁用安全带
        (
            r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_SECURITYBAND",
            "python.exe",
            0,
        ),
        # 启用现代DOM
        (
            r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_NINPUT_LEGACYMODE",
            "python.exe",
            0,
        ),
        # 禁用信息栏
        (
            r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_LOCALMACHINE_LOCKDOWN",
            "python.exe",
            0,
        ),
    ]
