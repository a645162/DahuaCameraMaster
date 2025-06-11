# -*- coding: utf-8 -*-

import sys
import subprocess
import random
import re
from typing import List, Dict, Optional
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QApplication,
)
from ip_config_ui import Ui_IPConfigWindow


class NetworkAdapterThread(QThread):
    """网络适配器检测线程"""
    
    adapters_found = Signal(list)
    
    def run(self):
        """获取网络适配器列表"""
        try:
            adapters = self.get_network_adapters()
            self.adapters_found.emit(adapters)
        except Exception as e:
            print(f"获取网络适配器失败: {e}")
            self.adapters_found.emit([])
    
    def get_network_adapters(self) -> List[Dict[str, str]]:
        """获取所有以太网适配器"""
        adapters = []
        try:
            # 使用wmic获取网络适配器信息
            cmd = 'wmic path win32_networkadapter where "NetConnectionID is not null AND AdapterTypeID=0" get NetConnectionID,Name,MACAddress /format:csv'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='gbk')
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # 跳过标题行
                    if line.strip() and ',' in line:
                        parts = line.split(',')
                        if len(parts) >= 4:
                            mac = parts[1].strip() if parts[1].strip() else "未知"
                            name = parts[2].strip() if parts[2].strip() else "未知"
                            connection_id = parts[3].strip() if parts[3].strip() else "未知"
                            
                            if connection_id != "未知" and "以太网" in connection_id:
                                adapters.append({
                                    'name': name,
                                    'connection_id': connection_id,
                                    'mac': mac,
                                    'display_name': f"{connection_id} ({name[:30]}...)" if len(name) > 30 else f"{connection_id} ({name})"
                                })
            
            # 如果没有找到适配器，添加默认的以太网连接
            if not adapters:
                adapters.append({
                    'name': "默认以太网适配器",
                    'connection_id': "以太网",
                    'mac': "未知",
                    'display_name': "以太网 (默认适配器)"
                })
                
        except Exception as e:
            print(f"获取网络适配器错误: {e}")
            # 添加默认适配器
            adapters.append({
                'name': "默认以太网适配器",
                'connection_id': "以太网",
                'mac': "未知",
                'display_name': "以太网 (默认适配器)"
            })
            
        return adapters


class IPConfigThread(QThread):
    """IP配置线程"""
    
    config_finished = Signal(bool, str)
    
    def __init__(self, adapter_name: str, ip: str, subnet: str, gateway: str, dns: str, is_dhcp: bool = False):
        super().__init__()
        self.adapter_name = adapter_name
        self.ip = ip
        self.subnet = subnet
        self.gateway = gateway
        self.dns = dns
        self.is_dhcp = is_dhcp
    
    def run(self):
        """执行IP配置"""
        try:
            if self.is_dhcp:
                success, message = self.set_dhcp()
            else:
                success, message = self.set_static_ip()
            
            self.config_finished.emit(success, message)
        except Exception as e:
            self.config_finished.emit(False, f"配置过程出错: {str(e)}")
    
    def set_static_ip(self) -> tuple[bool, str]:
        """设置静态IP"""
        try:
            # 设置IP地址和子网掩码
            cmd_ip = f'netsh interface ip set address name="{self.adapter_name}" static {self.ip} {self.subnet} {self.gateway}'
            result_ip = subprocess.run(cmd_ip, shell=True, capture_output=True, text=True, encoding='gbk')
            
            if result_ip.returncode != 0:
                return False, f"设置IP失败: {result_ip.stderr}"
            
            # 设置DNS
            cmd_dns = f'netsh interface ip set dns name="{self.adapter_name}" static {self.dns}'
            result_dns = subprocess.run(cmd_dns, shell=True, capture_output=True, text=True, encoding='gbk')
            
            if result_dns.returncode != 0:
                return False, f"设置DNS失败: {result_dns.stderr}"
            
            return True, "IP配置设置成功"
            
        except Exception as e:
            return False, f"设置静态IP错误: {str(e)}"
    
    def set_dhcp(self) -> tuple[bool, str]:
        """恢复DHCP"""
        try:
            # 设置为DHCP获取IP
            cmd_ip = f'netsh interface ip set address name="{self.adapter_name}" dhcp'
            result_ip = subprocess.run(cmd_ip, shell=True, capture_output=True, text=True, encoding='gbk')
            
            if result_ip.returncode != 0:
                return False, f"恢复DHCP失败: {result_ip.stderr}"
            
            # 设置为DHCP获取DNS
            cmd_dns = f'netsh interface ip set dns name="{self.adapter_name}" dhcp'
            result_dns = subprocess.run(cmd_dns, shell=True, capture_output=True, text=True, encoding='gbk')
            
            if result_dns.returncode != 0:
                return False, f"恢复DNS DHCP失败: {result_dns.stderr}"
            
            return True, "已成功恢复为DHCP自动获取"
            
        except Exception as e:
            return False, f"恢复DHCP错误: {str(e)}"


class IPConfigWindow(QMainWindow, Ui_IPConfigWindow):
    """IP配置主窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.adapters = []
        self.current_adapter = None
        
        self.init_ui()
        self.connect_signals()
        self.load_adapters()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("网卡IP配置工具")
        self.statusbar.showMessage("就绪")
        
        # 设置窗口图标和样式
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
        """)
    
    def connect_signals(self):
        """连接信号槽"""
        self.refresh_adapter_button.clicked.connect(self.load_adapters)
        self.adapter_comboBox.currentTextChanged.connect(self.on_adapter_changed)
        self.auto_ip_button.clicked.connect(self.auto_assign_ip)
        self.apply_button.clicked.connect(self.apply_config)
        self.dhcp_button.clicked.connect(self.restore_dhcp)
        self.cancel_button.clicked.connect(self.close)
    
    def load_adapters(self):
        """加载网络适配器列表"""
        self.status_label.setText("正在扫描网络适配器...")
        self.statusbar.showMessage("正在扫描网络适配器...")
        
        self.adapter_thread = NetworkAdapterThread()
        self.adapter_thread.adapters_found.connect(self.on_adapters_loaded)
        self.adapter_thread.start()
    
    def on_adapters_loaded(self, adapters: List[Dict[str, str]]):
        """适配器加载完成"""
        self.adapters = adapters
        self.adapter_comboBox.clear()
        
        if adapters:
            for adapter in adapters:
                self.adapter_comboBox.addItem(adapter['display_name'])
            
            self.status_label.setText(f"找到 {len(adapters)} 个以太网适配器")
            self.statusbar.showMessage(f"找到 {len(adapters)} 个以太网适配器")
        else:
            self.adapter_comboBox.addItem("未找到以太网适配器")
            self.status_label.setText("未找到以太网适配器")
            self.statusbar.showMessage("未找到以太网适配器")
    
    def on_adapter_changed(self, text: str):
        """适配器选择改变"""
        if self.adapters:
            for adapter in self.adapters:
                if adapter['display_name'] == text:
                    self.current_adapter = adapter
                    self.status_label.setText(f"已选择: {adapter['connection_id']}")
                    break
    
    def auto_assign_ip(self):
        """自动分配IP地址"""
        # 生成192.168.1.x网段的随机IP（排除192.168.1.108）
        while True:
            ip_suffix = random.randint(2, 254)
            if ip_suffix != 108:  # 排除192.168.1.108
                break
        
        auto_ip = f"192.168.1.{ip_suffix}"
        self.ip_lineEdit.setText(auto_ip)
        self.subnet_lineEdit.setText("255.255.255.0")
        self.gateway_lineEdit.setText("192.168.1.1")
        self.dns_lineEdit.setText("192.168.1.1")
        
        self.status_label.setText(f"已自动分配IP: {auto_ip}")
        QMessageBox.information(self, "自动分配", f"已自动分配IP地址: {auto_ip}")
    
    def validate_ip(self, ip: str) -> bool:
        """验证IP地址格式"""
        pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(pattern, ip)
        if not match:
            return False
        
        for group in match.groups():
            if not (0 <= int(group) <= 255):
                return False
        return True
    
    def validate_config(self) -> tuple[bool, str]:
        """验证配置参数"""
        if not self.current_adapter:
            return False, "请选择网络适配器"
        
        ip = self.ip_lineEdit.text().strip()
        subnet = self.subnet_lineEdit.text().strip()
        gateway = self.gateway_lineEdit.text().strip()
        dns = self.dns_lineEdit.text().strip()
        
        if not ip or not subnet or not gateway or not dns:
            return False, "请填写完整的网络配置信息"
        
        if not self.validate_ip(ip):
            return False, "IP地址格式不正确"
        
        if not self.validate_ip(subnet):
            return False, "子网掩码格式不正确"
        
        if not self.validate_ip(gateway):
            return False, "网关地址格式不正确"
        
        if not self.validate_ip(dns):
            return False, "DNS服务器地址格式不正确"
        
        # 检查是否为192.168.1.108
        if ip == "192.168.1.108":
            return False, "不能使用192.168.1.108作为IP地址"
        
        return True, "配置验证通过"
    
    def apply_config(self):
        """应用配置"""
        valid, message = self.validate_config()
        if not valid:
            QMessageBox.warning(self, "配置错误", message)
            return
        
        # 确认对话框
        reply = QMessageBox.question(
            self, 
            "确认配置", 
            f"即将为网卡 '{self.current_adapter['connection_id']}' 配置以下网络设置:\n\n"
            f"IP地址: {self.ip_lineEdit.text()}\n"
            f"子网掩码: {self.subnet_lineEdit.text()}\n"
            f"默认网关: {self.gateway_lineEdit.text()}\n"
            f"DNS服务器: {self.dns_lineEdit.text()}\n\n"
            f"确定要应用这些设置吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.status_label.setText("正在配置网络设置...")
        self.statusbar.showMessage("正在配置网络设置...")
        self.apply_button.setEnabled(False)
        
        # 启动配置线程
        self.config_thread = IPConfigThread(
            self.current_adapter['connection_id'],
            self.ip_lineEdit.text().strip(),
            self.subnet_lineEdit.text().strip(),
            self.gateway_lineEdit.text().strip(),
            self.dns_lineEdit.text().strip()
        )
        self.config_thread.config_finished.connect(self.on_config_finished)
        self.config_thread.start()
    
    def restore_dhcp(self):
        """恢复DHCP"""
        if not self.current_adapter:
            QMessageBox.warning(self, "错误", "请选择网络适配器")
            return
        
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认恢复DHCP",
            f"即将为网卡 '{self.current_adapter['connection_id']}' 恢复DHCP自动获取IP地址。\n\n"
            f"确定要继续吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.status_label.setText("正在恢复DHCP设置...")
        self.statusbar.showMessage("正在恢复DHCP设置...")
        self.dhcp_button.setEnabled(False)
        
        # 启动DHCP恢复线程
        self.config_thread = IPConfigThread(
            self.current_adapter['connection_id'],
            "", "", "", "",
            is_dhcp=True
        )
        self.config_thread.config_finished.connect(self.on_dhcp_finished)
        self.config_thread.start()
    
    def on_config_finished(self, success: bool, message: str):
        """配置完成"""
        self.apply_button.setEnabled(True)
        
        if success:
            self.status_label.setText("配置成功")
            self.statusbar.showMessage("网络配置已成功应用")
            QMessageBox.information(self, "配置成功", message)
        else:
            self.status_label.setText("配置失败")
            self.statusbar.showMessage("网络配置失败")
            QMessageBox.critical(self, "配置失败", message)
    
    def on_dhcp_finished(self, success: bool, message: str):
        """DHCP恢复完成"""
        self.dhcp_button.setEnabled(True)
        
        if success:
            self.status_label.setText("DHCP恢复成功")
            self.statusbar.showMessage("已成功恢复DHCP")
            QMessageBox.information(self, "DHCP恢复成功", message)
            
            # 清空静态IP配置
            self.ip_lineEdit.clear()
            self.subnet_lineEdit.setText("255.255.255.0")
            self.gateway_lineEdit.setText("192.168.1.1")
            self.dns_lineEdit.setText("192.168.1.1")
        else:
            self.status_label.setText("DHCP恢复失败")
            self.statusbar.showMessage("DHCP恢复失败")
            QMessageBox.critical(self, "DHCP恢复失败", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setApplicationName("网卡IP配置工具")
    app.setApplicationVersion("1.0")
    
    window = IPConfigWindow()
    window.show()
    
    sys.exit(app.exec())