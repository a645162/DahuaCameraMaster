import json
import os
from typing import Any, Dict, Optional


class ConfigManager:
    """配置管理类，负责保存和加载设备配置信息"""

    def __init__(self, config_file: str = "camera_configs.json"):
        self.config_file = config_file
        self.configs = {}
        self.load_configs()

    def load_configs(self):
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, encoding="utf-8") as f:
                    self.configs = json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.configs = {}

    def save_configs(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.configs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def get_device_config(self, ip: str) -> Optional[Dict[str, Any]]:
        """获取指定IP的设备配置"""
        return self.configs.get(ip)

    def save_device_config(
        self, ip: str, port: int, username: str, password: str, **kwargs
    ):
        """保存设备配置"""
        config = {
            "ip": ip,
            "port": port,
            "username": username,
            "password": password,
            "last_login": True,
        }
        # 添加其他参数
        config.update(kwargs)

        self.configs[ip] = config
        self.save_configs()

    def remove_device_config(self, ip: str):
        """删除设备配置"""
        if ip in self.configs:
            del self.configs[ip]
            self.save_configs()

    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取所有配置"""
        return self.configs.copy()

    def update_device_config(self, ip: str, **kwargs):
        """更新设备配置"""
        if ip in self.configs:
            self.configs[ip].update(kwargs)
            self.save_configs()
