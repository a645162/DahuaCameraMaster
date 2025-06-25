
import socket
import struct
import sys
import time

# from NetSDK.SDK_Callback import fSearchDevicesCBEx, fSearchDevicesCB
from ctypes import POINTER, c_void_p, cast, sizeof
from queue import Queue
from typing import Dict, List

from config_manager import ConfigManager
from DahuaCamMain import DahuaCamWindow
from device_search_ui import Ui_DeviceSearchWindow
from init_device_dialog_ui import Ui_InitDeviceDialog
from ip_config_window import IPConfigWindow
from NetSDK.NetSDK import NetClient
from NetSDK.SDK_Enum import EM_SEND_SEARCH_TYPE
from NetSDK.SDK_Struct import (
    C_LLONG,
    CB_FUNCTYPE,
    DEVICE_IP_SEARCH_INFO,
    DEVICE_IP_SEARCH_INFO_IP,
    DEVICE_NET_INFO_EX,
    DEVICE_NET_INFO_EX2,
    NET_IN_INIT_DEVICE_ACCOUNT,
    NET_IN_STARTSERACH_DEVICE,
    NET_OUT_INIT_DEVICE_ACCOUNT,
    NET_OUT_STARTSERACH_DEVICE,
)
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
)

# from ctypes import *

# 全局设备队列
device_queue = Queue(maxsize=0)
nUpdateNum = 0


class DeviceUpdateThread(QThread):
    """设备更新线程"""

    device_found = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        global nUpdateNum
        while self.running:
            if not device_queue.empty():
                device_info = device_queue.get()
                self.device_found.emit(device_info)
                device_queue.task_done()
                nUpdateNum += 1
                if nUpdateNum % 10 == 0:
                    nUpdateNum = 0
                    time.sleep(0.1)
            else:
                time.sleep(0.1)

    def stop(self):
        self.running = False


@CB_FUNCTYPE(None, C_LLONG, POINTER(DEVICE_NET_INFO_EX2), c_void_p)
def search_device_callback(lSearchHandle, pDevNetInfo, pUserData):
    """设备搜索回调函数"""
    try:
        buf = cast(pDevNetInfo, POINTER(DEVICE_NET_INFO_EX2)).contents
        if buf.stuDevInfo.iIPVersion == 4:
            device_info = [
                buf.stuDevInfo.byInitStatus,
                buf.stuDevInfo.iIPVersion,
                buf.stuDevInfo.szIP,
                buf.stuDevInfo.nPort,
                buf.stuDevInfo.szSubmask,
                buf.stuDevInfo.szGateway,
                buf.stuDevInfo.szMac,
                buf.stuDevInfo.szDeviceType,
                buf.stuDevInfo.szDetailType,
                buf.stuDevInfo.nHttpPort,
                buf.stuDevInfo.byPwdResetWay,
                buf.szLocalIP,
            ]
            device_queue.put(device_info)
    except Exception as e:
        print(f"设备搜索回调错误: {e}")


@CB_FUNCTYPE(None, POINTER(DEVICE_NET_INFO_EX), c_void_p)
def search_device_byip_callback(pDevNetInfo, pUserData):
    """IP搜索回调函数"""
    try:
        buf = cast(pDevNetInfo, POINTER(DEVICE_NET_INFO_EX)).contents
        if buf.iIPVersion == 4:
            device_info = [
                buf.byInitStatus,
                buf.iIPVersion,
                buf.szIP,
                buf.nPort,
                buf.szSubmask,
                buf.szGateway,
                buf.szMac,
                buf.szDeviceType,
                buf.szDetailType,
                buf.nHttpPort,
                buf.byPwdResetWay,
                None,
            ]
            device_queue.put(device_info)
    except Exception as e:
        print(f"IP搜索回调错误: {e}")


class InitDeviceDialog(QDialog, Ui_InitDeviceDialog):
    """设备初始化对话框"""

    def __init__(self, device_info: List, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.device_info = device_info
        self.setup_dialog()

    def setup_dialog(self):
        """设置对话框信息"""
        # 显示设备信息
        self.ip_value_label.setText(
            self.device_info[2].decode()
            if isinstance(self.device_info[2], bytes)
            else str(self.device_info[2])
        )
        self.mac_value_label.setText(
            self.device_info[6].decode()
            if isinstance(self.device_info[6], bytes)
            else str(self.device_info[6])
        )

        # 设置重置方式
        reset_way = self.device_info[10]
        if reset_way & 1:
            self.reset_method_lineEdit.setText("手机(Phone)")
            self.reset_value_label.setText("手机号:")
        elif (reset_way >> 1) & 1:
            self.reset_method_lineEdit.setText("邮箱(Email)")
            self.reset_value_label.setText("邮箱:")
        else:
            self.reset_method_lineEdit.setText("未知")

    def get_init_data(self):
        """获取初始化数据"""
        return {
            "username": self.username_lineEdit.text(),
            "password": self.password_lineEdit.text(),
            "confirm_password": self.confirm_password_lineEdit.text(),
            "reset_value": self.reset_value_lineEdit.text(),
        }


class DeviceSearchWindow(QMainWindow, Ui_DeviceSearchWindow):
    """设备搜索主窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # 初始化变量
        self.sdk = NetClient()
        self.sdk.InitEx(None, 0)

        self.config_manager = ConfigManager()
        self.device_info_list = []
        self.device_mac_list = []
        self.search_handles = []
        self.camera_windows = []  # 存储摄像机窗口
        self.ip_config_window = None  # IP配置窗口

        # 创建设备更新线程
        self.update_thread = DeviceUpdateThread()
        self.update_thread.device_found.connect(self.update_device_table)
        self.update_thread.start()

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("大华摄像机管理器 - 设备搜索")
        self.statusbar.showMessage("就绪")

        # 调整表格列宽
        self.tableWidget.setColumnWidth(0, 60)  # 序号
        self.tableWidget.setColumnWidth(1, 100)  # 状态
        self.tableWidget.setColumnWidth(3, 120)  # IP地址
        self.tableWidget.setColumnWidth(11, 120)  # 操作

    def connect_signals(self):
        """连接信号槽"""
        self.SearchDeviceButton.clicked.connect(self.search_devices)
        self.SearchByIpButton.clicked.connect(self.search_devices_by_ip)
        self.StopSearchButton.clicked.connect(self.stop_search)
        self.InitButton.clicked.connect(self.init_device)
        self.ConnectButton.clicked.connect(self.connect_device)
        self.IPConfigButton.clicked.connect(self.open_ip_config)

    def get_local_ips(self) -> List[str]:
        """获取本地IP地址列表"""
        try:
            hostname = socket.gethostname()
            ip_list = socket.gethostbyname_ex(hostname)[2]
            return [ip for ip in ip_list if not ip.startswith("127.")]
        except Exception as e:
            print(f"获取本地IP失败: {e}")
            return ["127.0.0.1"]

    def search_devices(self):
        """组播和广播搜索设备"""
        self.clear_device_list()
        self.statusbar.showMessage("正在搜索设备...")

        ip_list = self.get_local_ips()
        success_count = 0

        for ip in ip_list:
            try:
                search_in = NET_IN_STARTSERACH_DEVICE()
                search_in.dwSize = sizeof(NET_IN_STARTSERACH_DEVICE)
                search_in.emSendType = EM_SEND_SEARCH_TYPE.MULTICAST_AND_BROADCAST
                search_in.cbSearchDevices = search_device_callback
                search_in.szLocalIp = ip.encode()

                search_out = NET_OUT_STARTSERACH_DEVICE()
                search_out.dwSize = sizeof(NET_OUT_STARTSERACH_DEVICE)

                handle = self.sdk.StartSearchDevicesEx(search_in, search_out)
                if handle != 0:
                    self.search_handles.append(handle)
                    success_count += 1
            except Exception as e:
                print(f"搜索设备失败: {e}")

        if success_count > 0:
            self.statusbar.showMessage(f"正在搜索... (启动了{success_count}个搜索任务)")
        else:
            self.statusbar.showMessage("搜索启动失败")
            QMessageBox.warning(self, "警告", "搜索设备失败，请检查网络连接")

    def search_devices_by_ip(self):
        """根据IP范围搜索设备"""
        start_ip = self.StartIP_lineEdit.text().strip()
        end_ip = self.EndIP_lineEdit.text().strip()

        if not start_ip or not end_ip:
            QMessageBox.warning(self, "警告", "请输入起始IP和结束IP")
            return

        if not self.validate_ip(start_ip) or not self.validate_ip(end_ip):
            QMessageBox.warning(self, "警告", "IP地址格式不正确")
            return

        self.clear_device_list()
        self.statusbar.showMessage("正在按IP搜索设备...")

        try:
            start_num = struct.unpack("!I", socket.inet_aton(start_ip))[0]
            end_num = struct.unpack("!I", socket.inet_aton(end_ip))[0]

            if end_num - start_num > 255:
                QMessageBox.warning(self, "警告", "IP数量超过最大限制256")
                return

            search_info = DEVICE_IP_SEARCH_INFO()
            search_info.dwSize = sizeof(DEVICE_IP_SEARCH_INFO)
            search_info.nIpNum = end_num - start_num + 1

            for i in range(search_info.nIpNum):
                ip_info = DEVICE_IP_SEARCH_INFO_IP()
                ip_info.IP = socket.inet_ntoa(struct.pack("!I", start_num + i)).encode()
                search_info.szIP[i] = ip_info

            wait_time = int(self.Searchtime_lineEdit.text())
            ip_list = self.get_local_ips()

            for local_ip in ip_list:
                result = self.sdk.SearchDevicesByIPs(
                    search_info,
                    search_device_byip_callback,
                    0,
                    local_ip.encode(),
                    wait_time,
                )
                if result:
                    self.statusbar.showMessage("IP搜索已启动")
                    break
            else:
                self.statusbar.showMessage("IP搜索启动失败")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"搜索失败: {str(e)}")

    def validate_ip(self, ip: str) -> bool:
        """验证IP地址格式"""
        try:
            parts = ip.split(".")
            if len(parts) != 4:
                return False
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            return True
        except Exception:
            return False

    def stop_search(self):
        """停止搜索"""
        for handle in self.search_handles:
            self.sdk.StopSearchDevices(handle)
        self.search_handles.clear()
        self.statusbar.showMessage("搜索已停止")

    def clear_device_list(self):
        """清空设备列表"""
        self.device_info_list.clear()
        self.device_mac_list.clear()
        self.tableWidget.setRowCount(0)

        # 清空队列
        while not device_queue.empty():
            try:
                device_queue.get_nowait()
            except Exception:
                break

    def update_device_table(self, device_info: List):
        """更新设备表格"""
        try:
            # 过滤重复设备
            mac_addr = device_info[6]
            if isinstance(mac_addr, bytes):
                mac_addr = mac_addr.decode()

            if mac_addr in self.device_mac_list:
                return

            if device_info[1] != 4:  # 只显示IPv4设备
                return

            self.device_mac_list.append(mac_addr)
            self.device_info_list.append(device_info)

            row = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(row + 1)

            # 填充表格数据
            items = [
                str(row + 1),  # 序号
                "未初始化" if (device_info[0] & 3) == 1 else "已初始化",  # 状态
                str(device_info[1]),  # IP版本
                (
                    device_info[2].decode()
                    if isinstance(device_info[2], bytes)
                    else str(device_info[2])
                ),  # IP
                str(device_info[3]),  # 端口
                (
                    device_info[4].decode()
                    if isinstance(device_info[4], bytes)
                    else str(device_info[4])
                ),  # 子网掩码
                (
                    device_info[5].decode()
                    if isinstance(device_info[5], bytes)
                    else str(device_info[5])
                ),  # 网关
                mac_addr,  # MAC地址
                (
                    device_info[7].decode()
                    if isinstance(device_info[7], bytes)
                    else str(device_info[7])
                ),  # 设备类型
                (
                    device_info[8].decode()
                    if isinstance(device_info[8], bytes)
                    else str(device_info[8])
                ),  # 详细类型
                str(device_info[9]),  # HTTP端口
            ]

            for col, item_text in enumerate(items):
                item = QTableWidgetItem(item_text)
                self.tableWidget.setItem(row, col, item)

            # 添加操作按钮
            connect_btn = QPushButton("连接")
            connect_btn.clicked.connect(
                lambda checked, r=row: self.connect_device_by_row(r)
            )
            self.tableWidget.setCellWidget(row, 11, connect_btn)

        except Exception as e:
            print(f"更新设备表格失败: {e}")

    def init_device(self):
        """初始化设备"""
        current_row = self.tableWidget.currentRow()
        if current_row < 0 or current_row >= len(self.device_info_list):
            QMessageBox.warning(self, "警告", "请选择要初始化的设备")
            return

        device_info = self.device_info_list[current_row]

        # 检查设备是否已初始化
        if (device_info[0] & 3) != 1:
            QMessageBox.information(self, "提示", "该设备已经初始化")
            return

        # 显示初始化对话框
        dialog = InitDeviceDialog(device_info, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            init_data = dialog.get_init_data()

            # 验证密码
            if init_data["password"] != init_data["confirm_password"]:
                QMessageBox.warning(self, "警告", "确认密码不一致")
                return

            # 执行初始化
            if self.perform_device_init(device_info, init_data):
                QMessageBox.information(self, "成功", "设备初始化成功")

                # 更新表格状态
                status_item = QTableWidgetItem("已初始化")
                self.tableWidget.setItem(current_row, 1, status_item)

                # 更新设备信息
                self.device_info_list[current_row][0] = 2

    def perform_device_init(self, device_info: List, init_data: Dict) -> bool:
        """执行设备初始化"""
        try:
            init_in = NET_IN_INIT_DEVICE_ACCOUNT()
            init_in.dwSize = sizeof(init_in)
            init_in.szMac = (
                device_info[6]
                if isinstance(device_info[6], bytes)
                else device_info[6].encode()
            )
            init_in.szUserName = init_data["username"].encode()
            init_in.szPwd = init_data["password"].encode()
            init_in.byPwdResetWay = device_info[10]

            # 设置重置方式信息
            if device_info[10] & 1:  # 手机
                init_in.szCellPhone = init_data["reset_value"].encode()
            elif (device_info[10] >> 1) & 1:  # 邮箱
                init_in.szMail = init_data["reset_value"].encode()

            init_out = NET_OUT_INIT_DEVICE_ACCOUNT()
            init_out.dwSize = sizeof(init_out)

            # 获取本地IP
            local_ip = device_info[11] if device_info[11] else self.get_local_ips()[0]
            if isinstance(local_ip, bytes):
                local_ip = local_ip.decode()

            result = self.sdk.InitDevAccount(init_in, init_out, 5000, local_ip.encode())

            if not result:
                error_msg = self.sdk.GetLastErrorMessage()
                QMessageBox.warning(self, "初始化失败", f"错误: {error_msg}")
                return False

            return True

        except Exception as e:
            QMessageBox.warning(self, "错误", f"初始化过程出错: {str(e)}")
            return False

    def connect_device(self):
        """连接选中的设备"""
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要连接的设备")
            return

        self.connect_device_by_row(current_row)

    def connect_device_by_row(self, row: int):
        """通过行号连接设备"""
        if row < 0 or row >= len(self.device_info_list):
            return

        device_info = self.device_info_list[row]
        ip = (
            device_info[2].decode()
            if isinstance(device_info[2], bytes)
            else str(device_info[2])
        )
        port = device_info[3]

        # 检查设备是否已初始化
        if (device_info[0] & 3) == 1:
            QMessageBox.warning(self, "警告", "设备未初始化，请先初始化设备")
            return

        # 从配置管理器获取保存的登录信息
        config = self.config_manager.get_device_config(ip)

        # 创建新的摄像机窗口
        camera_window = DahuaCamWindow()

        # 如果有保存的配置，填充到界面
        if config:
            camera_window.IP_lineEdit.setText(ip)
            camera_window.Port_lineEdit.setText(str(port))
            camera_window.Name_lineEdit.setText(config.get("username", ""))
            camera_window.Pwd_lineEdit.setText(config.get("password", ""))
        else:
            # 没有保存的配置，使用默认值
            camera_window.IP_lineEdit.setText(ip)
            camera_window.Port_lineEdit.setText(str(port))

        # 设置窗口标题
        camera_window.setWindowTitle(f"摄像机控制 - {ip}")

        # 显示窗口
        camera_window.show()

        # 保存窗口引用
        self.camera_windows.append(camera_window)

        self.statusbar.showMessage(f"已打开摄像机控制窗口: {ip}")

    def open_ip_config(self):
        """打开IP配置窗口"""
        try:
            # 如果窗口已存在且可见，则激活它
            if self.ip_config_window and self.ip_config_window.isVisible():
                self.ip_config_window.raise_()
                self.ip_config_window.activateWindow()
                return

            # 创建新的IP配置窗口
            self.ip_config_window = IPConfigWindow(self)
            self.ip_config_window.setWindowTitle("网卡IP配置工具")
            self.ip_config_window.show()

            self.statusbar.showMessage("已打开网卡IP配置工具")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开IP配置工具失败: {str(e)}")

    def closeEvent(self, event):
        """关闭事件"""
        # 停止搜索
        self.stop_search()

        # 停止更新线程
        if self.update_thread.isRunning():
            self.update_thread.stop()
            self.update_thread.wait()

        # 关闭所有摄像机窗口
        for window in self.camera_windows:
            if window:
                window.close()

        # 关闭IP配置窗口
        if self.ip_config_window:
            self.ip_config_window.close()

        # 清理SDK
        self.sdk.Cleanup()

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setApplicationName("大华摄像机管理器")
    app.setApplicationVersion("1.0")

    window = DeviceSearchWindow()
    window.show()

    sys.exit(app.exec())
