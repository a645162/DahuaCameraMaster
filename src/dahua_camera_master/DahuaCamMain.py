# coding=utf-8
import sys
import os
import time
from datetime import datetime
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PySide6.QtCore import QTimer, Signal, QDateTime, QDate, QTime, QSize
from PySide6.QtGui import QPixmap
from ctypes import sizeof, POINTER, cast, c_char

# from ctypes import *


from DahuaCamUI import Ui_MainWindow
from config_manager import ConfigManager
from NetSDK.NetSDK import NetClient
from NetSDK.SDK_Callback import (
    fDisConnect,
    fHaveReConnect,
    CB_FUNCTYPE,
    fDecCBFun,
    fRealDataCallBackEx2,
)
from NetSDK.SDK_Enum import (
    SDK_RealPlayType,
    EM_LOGIN_SPAC_CAP_TYPE,
    SDK_PTZ_ControlType,
    EM_DEV_CFG_TYPE,
    EM_REALDATA_FLAG,
    SDK_ALARM_TYPE,
)
from NetSDK.SDK_Struct import (
    C_LLONG,
    NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY,
    NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY,
    SNAP_PARAMS,
    C_DWORD,
    C_LDWORD,
    c_ubyte,
    c_uint,
    c_int,
    c_long,
    NET_TIME,
    LOG_SET_PRINT_INFO,
    sys_platform,
    PLAY_FRAME_INFO,
    ALARM_MOTIONDETECT_INFO,
)

# 添加必要的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# 判断当前py文件所在目录，设置base_dir
if os.path.basename(current_dir) == "src":
    # 如果当前目录就是src，则base_dir是src的父目录
    base_dir = parent_dir
else:
    # 如果当前目录不是src，则base_dir就是当前目录的父目录
    base_dir = parent_dir

# 确保使用绝对路径
base_dir = os.path.abspath(base_dir)
current_dir = os.path.abspath(current_dir)
parent_dir = os.path.abspath(parent_dir)

sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# 全局变量保存窗口引用
g_window_instance = None


# 报警信息类
class AlarmInfo:
    def __init__(self):
        self.time_str = ""
        self.channel_str = ""
        self.alarm_type = ""
        self.status_str = ""

    def get_motion_alarm_info(self, alarm_info):
        """获取动检报警信息"""
        self.time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.channel_str = str(alarm_info.nChannelID)
        self.alarm_type = "动检事件(VideoMotion)"
        if alarm_info.nEventAction == 0:
            self.status_str = "脉冲(Pulse)"
        elif alarm_info.nEventAction == 1:
            self.status_str = "开始(Start)"
        elif alarm_info.nEventAction == 2:
            self.status_str = "结束(Stop)"
        else:
            self.status_str = "未知(Unknown)"


# 抓拍回调函数
@CB_FUNCTYPE(None, C_LLONG, POINTER(c_ubyte), c_uint, c_uint, C_DWORD, C_LDWORD)
def CaptureCallBack(lLoginID, pBuf, RevLen, EncodeType, CmdSerial, dwUser):
    """抓拍回调函数"""
    if lLoginID == 0 or g_window_instance is None:
        return

    print("Enter CaptureCallBack")
    try:
        # 直接使用全局窗口引用
        g_window_instance.capture_signal.emit(pBuf, RevLen, EncodeType)
    except Exception as e:
        print(f"抓拍回调错误: {e}")


# 报警回调函数
@CB_FUNCTYPE(
    None,
    c_long,
    C_LLONG,
    POINTER(c_char),
    C_DWORD,
    POINTER(c_char),
    c_long,
    c_int,
    c_long,
    C_LDWORD,
)
def AlarmCallback(
    lCommand,
    lLoginID,
    pBuf,
    dwBufLen,
    pchDVRIP,
    nDVRPort,
    bAlarmAckFlag,
    nEventID,
    dwUser,
):
    """报警回调函数"""
    if lLoginID == 0 or g_window_instance is None:
        return

    try:
        if lCommand == SDK_ALARM_TYPE.EVENT_MOTIONDETECT:
            print("收到动检报警")
            alarm_info = cast(pBuf, POINTER(ALARM_MOTIONDETECT_INFO)).contents
            show_info = AlarmInfo()
            show_info.get_motion_alarm_info(alarm_info)
            # 通过信号发送到主线程
            g_window_instance.alarm_signal.emit(lCommand, show_info)
    except Exception as e:
        print(f"报警回调错误: {e}")


class DahuaCamWindow(QMainWindow, Ui_MainWindow):
    # 添加信号用于线程安全的UI更新
    capture_signal = Signal(object, int, int)
    alarm_signal = Signal(int, object)  # 报警信号

    def __init__(self, parent=None):
        super(DahuaCamWindow, self).__init__(parent)
        self.setupUi(self)

        # 设置全局窗口引用
        global g_window_instance
        g_window_instance = self

        # 连接信号
        self.capture_signal.connect(self.handle_capture_callback)
        self.alarm_signal.connect(self.handle_alarm_callback)

        # 配置管理器
        self.config_manager = ConfigManager()

        # 界面初始化
        self._init_ui()

        # NetSDK用到的相关变量和回调
        self.loginID = 0
        self.playID = 0
        self.recordID = 0  # 录制ID
        self.freePort = c_int()  # PlaySDK端口
        self.is_recording = False  # 录制状态
        self.record_start_time = None  # 录制开始时间
        self.is_alarm_listening = False  # 报警监听状态
        self.alarm_count = 0  # 报警记录数量
        self.m_DisConnectCallBack = fDisConnect(self.DisConnectCallBack)
        self.m_ReConnectCallBack = fHaveReConnect(self.ReConnectCallBack)

        # PlaySDK模式专用回调：解码回调 - 获取YUV数据
        self.m_DecodingCallBack = fDecCBFun(self.DecodingCallBack)

        # PlaySDK模式专用回调：拉流回调 - 获取原始流数据并输入到PlaySDK
        self.m_RealDataCallBack = fRealDataCallBackEx2(self.RealDataCallBack)

        # 录制时间更新定时器
        self.record_timer = QTimer()
        self.record_timer.timeout.connect(self.update_record_time)

        # 获取NetSDK对象并初始化
        self.sdk = NetClient()
        self.sdk.InitEx(self.m_DisConnectCallBack)
        self.sdk.SetAutoReconnect(self.m_ReConnectCallBack)

        # 设置报警回调
        self.sdk.SetDVRMessCallBackEx1(AlarmCallback, 0)

        # 创建保存目录
        self.setup_default_save_path()
        self.create_save_directory()

    def setup_default_save_path(self):
        """设置默认保存路径"""
        # 在base_dir下创建capture目录（绝对路径）
        default_capture_dir = os.path.join(base_dir, "capture")
        default_capture_dir = os.path.abspath(default_capture_dir)

        # 如果界面上的保存路径为空或不存在，设置默认路径
        current_save_path = ""
        if hasattr(self, "save_path_edit"):
            current_save_path = self.save_path_edit.text().strip()

        if not current_save_path:
            if hasattr(self, "save_path_edit"):
                self.save_path_edit.setText(default_capture_dir)

        # 确保默认目录存在
        try:
            os.makedirs(default_capture_dir, exist_ok=True)
            print(f"默认保存目录设置为: {default_capture_dir}")
        except Exception as e:
            print(f"创建默认保存目录失败: {e}")
            # 如果创建失败，使用当前目录下的capture文件夹作为备用
            fallback_dir = os.path.join(current_dir, "capture")
            fallback_dir = os.path.abspath(fallback_dir)
            try:
                os.makedirs(fallback_dir, exist_ok=True)
                if hasattr(self, "save_path_edit"):
                    self.save_path_edit.setText(fallback_dir)
                print(f"使用备用保存目录: {fallback_dir}")
            except Exception as e2:
                print(f"创建备用目录也失败: {e2}")

    def _init_ui(self):
        """初始化界面和信号槽连接"""
        # 设置窗口属性
        self.setWindowTitle("实时预览与云台控制(RealPlay & PTZ)-离线(OffLine)")

        # 初始化渲染模式选择
        self.render_mode_comboBox.addItem("回调模式(CallBack)")
        if sys_platform == "windows":
            self.render_mode_comboBox.addItem("PlaySDK模式(PlaySDK-Windows独有)")

        # 连接登录和预览按钮的点击事件
        self.login_btn.clicked.connect(self.login_btn_onclick)
        self.play_btn.clicked.connect(self.play_btn_onclick)

        # 连接文本框变化事件，用于实时保存配置
        self.IP_lineEdit.textChanged.connect(self.on_config_changed)
        self.Port_lineEdit.textChanged.connect(self.on_config_changed)
        self.Name_lineEdit.textChanged.connect(self.on_config_changed)
        self.Pwd_lineEdit.textChanged.connect(self.on_config_changed)

        # 连接抓拍和录制按钮事件
        self.capture_btn.clicked.connect(self.capture_picture)
        self.record_btn.clicked.connect(self.toggle_record)
        self.select_path_btn.clicked.connect(self.select_save_path)

        # 连接设备控制按钮事件
        self.get_time_btn.clicked.connect(self.get_device_time)
        self.set_time_btn.clicked.connect(self.set_device_time)
        self.sync_time_btn.clicked.connect(self.sync_pc_time)
        self.restart_btn.clicked.connect(self.restart_device)
        self.open_log_btn.clicked.connect(self.open_log)
        self.close_log_btn.clicked.connect(self.close_log)

        # 连接报警监听按钮事件
        self.start_alarm_btn.clicked.connect(self.start_alarm_listen)
        self.stop_alarm_btn.clicked.connect(self.stop_alarm_listen)
        self.clear_alarm_btn.clicked.connect(self.clear_alarm_records)

        # 连接RTSP URL生成按钮事件
        self.generate_url_btn.clicked.connect(self.generate_rtsp_url)
        self.copy_url_btn.clicked.connect(self.copy_rtsp_url)
        self.ffmpeg_generator_btn.clicked.connect(self.open_ffmpeg_generator)

        # 连接视频比例控制事件（使用自定义组件的信号）
        self.video_widget.aspect_mode_changed.connect(self.on_aspect_ratio_changed)

        # FFmpeg窗口引用
        self.ffmpeg_window = None

        # --- PTZ控制事件连接 ---
        # 参考Demo/PTZ_Control_pyqt5的实现方式，使用mousePressEvent和mouseReleaseEvent

        # 方向控制按钮
        self.ptz_up_btn.mousePressEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.UP_CONTROL, False
        )
        self.ptz_up_btn.mouseReleaseEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.UP_CONTROL, True
        )

        self.ptz_down_btn.mousePressEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.DOWN_CONTROL, False
        )
        self.ptz_down_btn.mouseReleaseEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.DOWN_CONTROL, True
        )

        self.ptz_left_btn.mousePressEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.LEFT_CONTROL, False
        )
        self.ptz_left_btn.mouseReleaseEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.LEFT_CONTROL, True
        )

        self.ptz_right_btn.mousePressEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.RIGHT_CONTROL, False
        )
        self.ptz_right_btn.mouseReleaseEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.RIGHT_CONTROL, True
        )

        # 变倍控制按钮
        self.zoom_add_btn.mousePressEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.ZOOM_ADD_CONTROL, False
        )
        self.zoom_add_btn.mouseReleaseEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.ZOOM_ADD_CONTROL, True
        )

        self.zoom_dec_btn.mousePressEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.ZOOM_DEC_CONTROL, False
        )
        self.zoom_dec_btn.mouseReleaseEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.ZOOM_DEC_CONTROL, True
        )

        # 聚焦控制按钮
        self.focus_add_btn.mousePressEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.FOCUS_ADD_CONTROL, False
        )
        self.focus_add_btn.mouseReleaseEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.FOCUS_ADD_CONTROL, True
        )

        self.focus_dec_btn.mousePressEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.FOCUS_DEC_CONTROL, False
        )
        self.focus_dec_btn.mouseReleaseEvent = lambda event: self.ptz_control(
            SDK_PTZ_ControlType.FOCUS_DEC_CONTROL, True
        )

    def login_btn_onclick(self):
        """登录/登出按钮点击事件"""
        if not self.loginID:
            # 执行登录
            ip = self.IP_lineEdit.text()
            try:
                port = int(self.Port_lineEdit.text())
            except ValueError:
                error_msg = "端口必须是数字！"
                print(f"登录错误: {error_msg}")
                QMessageBox.warning(self, "提示", error_msg)
                return

            username = self.Name_lineEdit.text()
            password = self.Pwd_lineEdit.text()

            if not all([ip, username, password]):
                error_msg = "请填写完整的登录信息！"
                print(f"登录错误: {error_msg}")
                QMessageBox.warning(self, "提示", error_msg)
                return

            print(f"尝试登录设备: {ip}:{port}, 用户名: {username}")

            stuInParam = NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY()
            stuInParam.dwSize = sizeof(NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY)
            stuInParam.szIP = ip.encode()
            stuInParam.nPort = port
            stuInParam.szUserName = username.encode()
            stuInParam.szPassword = password.encode()
            stuInParam.emSpecCap = EM_LOGIN_SPAC_CAP_TYPE.TCP

            stuOutParam = NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY()
            stuOutParam.dwSize = sizeof(NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY)

            self.loginID, device_info, error_msg = self.sdk.LoginWithHighLevelSecurity(
                stuInParam, stuOutParam
            )

            if self.loginID != 0:
                success_msg = f"登录成功 - {ip}:{port}, 通道数: {device_info.nChanNum}"
                print(success_msg)
                self.setWindowTitle("实时预览与云台控制(RealPlay & PTZ)-在线(OnLine)")
                self.login_btn.setText("登出(Logout)")
                self.play_btn.setEnabled(True)

                # 启用相机控制相关的组
                self.ptz_groupBox.setEnabled(True)
                self.camera_groupBox.setEnabled(True)
                self.record_groupBox.setEnabled(True)
                self.capture_btn.setEnabled(True)
                self.record_btn.setEnabled(True)

                # 设备相关的功能需要登录后才能使用
                self.get_time_btn.setEnabled(True)
                self.set_time_btn.setEnabled(True)
                self.sync_time_btn.setEnabled(True)
                self.restart_btn.setEnabled(True)
                self.start_alarm_btn.setEnabled(True)

                # 填充通道列表
                self.Channel_comboBox.clear()
                for i in range(int(device_info.nChanNum)):
                    self.Channel_comboBox.addItem(str(i))
                self.StreamTyp_comboBox.setEnabled(True)
                self.render_mode_comboBox.setEnabled(True)

                # 保存成功登录的配置
                self.save_login_config(ip, port, username, password)

                self.statusbar.showMessage(f"登录成功 - {ip}:{port}")
            else:
                print(f"登录失败: {error_msg}")
                QMessageBox.warning(self, "登录失败", error_msg)
                self.statusbar.showMessage("登录失败")
        else:
            # 执行登出
            print("开始登出...")
            if self.playID:
                print("停止预览...")
                self.stop_preview()

            result = self.sdk.Logout(self.loginID)
            if result:
                print("登出成功")
                self.setWindowTitle("实时预览与云台控制(RealPlay & PTZ)-离线(OffLine)")
                self.login_btn.setText("登录(Login)")
                self.loginID = 0
                self.play_btn.setEnabled(False)

                # 禁用相机控制相关的组
                self.ptz_groupBox.setEnabled(False)
                self.camera_groupBox.setEnabled(False)
                self.record_groupBox.setEnabled(False)
                self.capture_btn.setEnabled(False)
                self.record_btn.setEnabled(False)

                # 设备相关的功能在登出后禁用
                self.get_time_btn.setEnabled(False)
                self.set_time_btn.setEnabled(False)
                self.sync_time_btn.setEnabled(False)
                self.restart_btn.setEnabled(False)
                self.start_alarm_btn.setEnabled(False)
                self.stop_alarm_btn.setEnabled(False)

                self.Channel_comboBox.clear()
                self.StreamTyp_comboBox.setEnabled(False)
                self.render_mode_comboBox.setEnabled(False)

                # 停止录制（如果正在录制）
                if self.is_recording:
                    self.stop_record()

                # 停止报警监听（如果正在监听）
                if self.is_alarm_listening:
                    self.stop_alarm_listen()

                self.statusbar.showMessage("已登出")
            else:
                error_msg = "登出失败"
                print(error_msg)
                self.statusbar.showMessage(error_msg)

    def play_btn_onclick(self):
        """预览/停止按钮点击事件"""
        if not self.playID:
            # 开始预览
            self.start_preview()
        else:
            # 停止预览
            self.stop_preview()

    def start_preview(self):
        """开始预览"""
        channel = self.Channel_comboBox.currentIndex()
        if self.StreamTyp_comboBox.currentIndex() == 0:
            stream_type = SDK_RealPlayType.Realplay
        else:
            stream_type = SDK_RealPlayType.Realplay_1

        render_mode = self.render_mode_comboBox.currentIndex()
        print(
            f"开始预览 - 通道: {channel}, 流类型: {stream_type}, 渲染模式: {render_mode}"
        )

        try:
            if render_mode == 0:
                # CallBack模式（回调渲染）- 索引0
                print("使用CallBack回调渲染模式")
                self.playID = self.sdk.RealPlayEx(
                    self.loginID, channel, int(self.PlayWnd.winId()), stream_type
                )

                if self.playID != 0:
                    print(f"CallBack预览启动成功 - PlayID: {self.playID}")
                    self.play_btn.setText("停止(Stop)")
                    self.StreamTyp_comboBox.setEnabled(False)
                    self.render_mode_comboBox.setEnabled(False)
                    self.statusbar.showMessage("CallBack预览已开始")
                else:
                    error_msg = self.sdk.GetLastErrorMessage()
                    print(f"CallBack预览失败: {error_msg}")
                    QMessageBox.warning(self, "预览失败", error_msg)
            else:
                # PlaySDK模式 (Windows独有) - 索引1
                print("使用PlaySDK渲染模式")
                result, self.freePort = self.sdk.GetFreePort()
                if not result:
                    error_msg = "获取PlaySDK端口失败"
                    print(error_msg)
                    QMessageBox.warning(self, "预览失败", error_msg)
                    return

                self.sdk.OpenStream(self.freePort)
                self.sdk.Play(self.freePort, int(self.PlayWnd.winId()))

                self.playID = self.sdk.RealPlayEx(self.loginID, channel, 0, stream_type)
                if self.playID != 0:
                    print(
                        f"PlaySDK预览启动成功 - PlayID: {self.playID}, Port: {self.freePort.value}"
                    )
                    self.play_btn.setText("停止(Stop)")
                    self.StreamTyp_comboBox.setEnabled(False)
                    self.render_mode_comboBox.setEnabled(False)
                    self.statusbar.showMessage("PlaySDK预览已开始")

                    # 设置数据回调和解码回调
                    self.sdk.SetRealDataCallBackEx2(
                        self.playID,
                        self.m_RealDataCallBack,
                        None,
                        EM_REALDATA_FLAG.RAW_DATA,
                    )
                    self.sdk.SetDecCallBack(self.freePort, self.m_DecodingCallBack)
                else:
                    error_msg = self.sdk.GetLastErrorMessage()
                    print(f"PlaySDK预览失败: {error_msg}")
                    # 清理PlaySDK资源
                    self.sdk.Stop(self.freePort)
                    self.sdk.CloseStream(self.freePort)
                    self.sdk.ReleasePort(self.freePort)
                    QMessageBox.warning(self, "预览失败", error_msg)

        except Exception as e:
            error_msg = f"预览异常：{str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def stop_preview(self):
        """停止预览"""
        # 停止预览前，先停止录制（如果正在录制）
        if self.is_recording:
            print("停止预览前先停止录制...")
            self.stop_record()

        # 停止预览
        print("停止预览...")
        result = self.sdk.StopRealPlayEx(self.playID)
        if result:
            print("预览停止成功")
            self.play_btn.setText("预览(Play)")

            # 如果使用了PlaySDK模式，需要清理PlaySDK资源
            render_mode = self.render_mode_comboBox.currentIndex()
            if render_mode == 1 and sys_platform == "windows":
                print("清理PlaySDK资源...")
                self.sdk.SetDecCallBack(self.freePort, None)
                self.sdk.Stop(self.freePort)
                self.sdk.CloseStream(self.freePort)
                self.sdk.ReleasePort(self.freePort)

            self.playID = 0
            self.PlayWnd.repaint()
            self.StreamTyp_comboBox.setEnabled(True)
            self.render_mode_comboBox.setEnabled(True)
            self.statusbar.showMessage("预览已停止")
        else:
            error_msg = "停止预览失败"
            print(error_msg)
            self.statusbar.showMessage(error_msg)

    def RealDataCallBack(
        self, lRealHandle, dwDataType, pBuffer, dwBufSize, param, dwUser
    ):
        """
        拉流回调函数 - 仅在PlaySDK模式下使用
        作用：获取摄像头的原始视频流数据，并将其输入到PlaySDK进行解码
        流程：摄像头 -> SDK -> 此回调 -> PlaySDK解码器 -> DecodingCallBack -> 显示
        """
        if lRealHandle == self.playID:
            # 将原始流数据输入到PlaySDK进行解码显示
            self.sdk.InputData(self.freePort, pBuffer, dwBufSize)

            # 可选：保存原始流数据到文件
            # data_buffer = cast(pBuffer, POINTER(c_ubyte * dwBufSize)).contents
            # with open('./data.dav', 'ab+') as data_file:
            #     data_file.write(data_buffer)

    def DecodingCallBack(self, nPort, pBuf, nSize, pFrameInfo, pUserData, nReserved2):
        """
        PlaySDK解码回调函数 - 仅在PlaySDK模式下使用
        作用：获取PlaySDK解码后的YUV数据，可以进行进一步处理
        流程：RealDataCallBack -> PlaySDK解码器 -> 此回调 -> 可获取YUV数据
        """
        # 这里可以获取解码后的YUV数据进行处理
        # data = cast(pBuf, POINTER(c_ubyte * nSize)).contents
        # info = pFrameInfo.contents
        # if info.nType == 3:  # YUV数据
        #     # 可以在这里处理YUV数据转RGB等操作
        #     # 例如：图像处理、AI分析、格式转换等
        #     pass
        # 注意：此回调在PlaySDK内部线程中执行，不要进行耗时操作
        pass

    def create_save_directory(self):
        """创建保存目录"""
        save_path = self.save_path_edit.text()
        if not save_path.strip():
            return False, "保存路径不能为空"

        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)
                print(f"创建保存目录: {save_path}")

            # 验证目录是否可写
            if not os.access(save_path, os.W_OK):
                return False, f"目录不可写: {save_path}"

            return True, "目录验证成功"
        except Exception as e:
            error_msg = f"创建/验证保存目录失败: {e}"
            print(error_msg)
            return False, error_msg

    def verify_save_directory(self):
        """验证保存目录，如果不存在则提示用户"""
        success, message = self.create_save_directory()
        if not success:
            print(f"保存目录验证失败: {message}")
            QMessageBox.warning(self, "目录错误", f"{message}\n请检查保存路径设置。")
            return False
        return True

    def select_save_path(self):
        """选择保存路径"""
        current_path = self.save_path_edit.text()
        selected_path = QFileDialog.getExistingDirectory(
            self, "选择保存路径", current_path
        )
        if selected_path:
            self.save_path_edit.setText(selected_path)
            self.create_save_directory()

    def capture_picture(self):
        """抓拍图片"""
        if not self.loginID:
            error_msg = "请先登录设备！"
            print(f"抓拍错误: {error_msg}")
            QMessageBox.warning(self, "警告", error_msg)
            return

        # 检查是否在预览状态 - 抓拍通常需要预览状态
        if not self.playID:
            error_msg = "请先开始预览！"
            print(f"抓拍错误: {error_msg}")
            QMessageBox.warning(self, "警告", error_msg)
            return

        # 检查保存目录
        if not self.verify_save_directory():
            return

        try:
            print("开始抓拍...")
            # 设置抓拍回调 - 简化参数传递
            dwUser = 0  # 简化为0，使用全局变量引用
            self.sdk.SetSnapRevCallBack(CaptureCallBack, dwUser)

            # 获取当前通道
            channel = self.Channel_comboBox.currentIndex()

            # 设置抓拍参数
            snap_params = SNAP_PARAMS()
            snap_params.Channel = channel
            snap_params.Quality = 1  # 抓拍质量
            snap_params.mode = 0  # 抓拍模式

            print(f"抓拍参数 - 通道: {channel}, 质量: {snap_params.Quality}")

            # 执行抓拍
            result = self.sdk.SnapPictureEx(self.loginID, snap_params)
            if result:
                success_msg = f"抓拍请求已发送 - 通道: {channel}"
                print(success_msg)
                self.statusbar.showMessage("抓拍请求已发送...")
            else:
                error_msg = self.sdk.GetLastErrorMessage()
                print(f"抓拍失败: {error_msg}")
                QMessageBox.warning(self, "抓拍失败", f"错误: {error_msg}")

        except Exception as e:
            error_msg = f"抓拍过程出错: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def handle_capture_callback(self, pBuf, RevLen, EncodeType):
        """处理抓拍回调 - 在主线程中安全执行"""
        try:
            print(f"处理抓拍回调 - 数据长度: {RevLen}, 编码类型: {EncodeType}")

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ip = self.IP_lineEdit.text().replace(".", "_")
            channel = self.Channel_comboBox.currentIndex()
            filename = f"capture_{ip}_ch{channel}_{timestamp}.jpg"

            # 获取保存路径
            save_path = self.save_path_edit.text().strip()
            if not save_path:
                # 如果保存路径为空，使用默认路径
                save_path = os.path.join(base_dir, "capture")
                save_path = os.path.abspath(save_path)
                self.save_path_edit.setText(save_path)
                print(f"使用默认保存路径: {save_path}")
            else:
                # 确保路径是绝对路径
                save_path = os.path.abspath(save_path)

            full_path = os.path.join(save_path, filename)
            full_path = os.path.abspath(full_path)  # 确保完整路径是绝对路径

            print(f"保存抓拍图片到: {full_path}")

            # 确保保存目录存在
            os.makedirs(save_path, exist_ok=True)

            # 保存图片数据 - 使用更安全的方式
            pic_buf = cast(pBuf, POINTER(c_ubyte * RevLen)).contents
            with open(full_path, "wb") as f:
                f.write(pic_buf)

            success_msg = f"抓拍成功: {filename}"
            print(success_msg)
            self.statusbar.showMessage(success_msg)

            # 可选：在界面上显示缩略图
            try:
                pixmap = QPixmap(full_path)
                if not pixmap.isNull() and hasattr(self, "PlayWnd"):
                    # 在视频窗口的某个角落显示抓拍成功的提示
                    pass
            except Exception:
                pass

            QMessageBox.information(self, "抓拍成功", f"图片已保存到:\n{full_path}")

        except Exception as e:
            error_msg = f"处理抓拍回调失败: {e}"
            print(error_msg)
            self.statusbar.showMessage("抓拍保存失败")
            QMessageBox.warning(self, "抓拍失败", f"保存图片失败: {str(e)}")

    def toggle_record(self):
        """切换录制状态"""
        if not self.loginID:
            error_msg = "请先登录设备！"
            print(f"录制错误: {error_msg}")
            QMessageBox.warning(self, "警告", error_msg)
            return

        # 检查是否在预览状态
        if not self.playID:
            error_msg = "请先开始预览！录制功能需要在预览状态下使用。"
            print(f"录制错误: {error_msg}")
            QMessageBox.warning(self, "警告", error_msg)
            return

        if not self.is_recording:
            self.start_record()
        else:
            self.stop_record()

    def start_record(self):
        """开始录制"""
        # 检查是否在预览状态
        if not self.playID:
            error_msg = "请先开始预览！"
            print(f"录制错误: {error_msg}")
            QMessageBox.warning(self, "警告", error_msg)
            return

        # 检查保存目录
        if not self.verify_save_directory():
            return

        try:
            print("开始录制...")
            # 生成录制文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ip = self.IP_lineEdit.text().replace(".", "_")
            channel = self.Channel_comboBox.currentIndex()
            filename = f"record_{ip}_ch{channel}_{timestamp}.dav"

            # 获取保存路径
            save_path = self.save_path_edit.text().strip()
            if not save_path:
                # 如果保存路径为空，使用默认路径
                save_path = os.path.join(base_dir, "capture")
                save_path = os.path.abspath(save_path)
                self.save_path_edit.setText(save_path)
                print(f"使用默认保存路径: {save_path}")
            else:
                # 确保路径是绝对路径
                save_path = os.path.abspath(save_path)

            full_path = os.path.join(save_path, filename)
            full_path = os.path.abspath(full_path)

            print(f"录制文件路径: {full_path}")
            print(f"使用预览ID进行录制: {self.playID}")

            # 确保保存目录存在
            os.makedirs(save_path, exist_ok=True)

            # 使用预览ID开始保存视频流 - 直接保存当前预览的流
            self.recordID = self.sdk.StartSaveRealData(
                self.playID, full_path.encode(), None, None
            )

            if self.recordID != 0:
                print(f"录制启动成功 - RecordID: {self.recordID}")
                self.is_recording = True
                self.record_start_time = time.time()
                self.record_btn.setText("停止录制(Stop Record)")
                self.record_status_label.setText("录制状态: 录制中")
                self.record_status_label.setStyleSheet(
                    "color: green; font-weight: bold;"
                )

                # 启动计时器
                self.record_timer.start(1000)  # 每秒更新一次

                success_msg = f"开始录制预览流: {filename}"
                print(success_msg)
                self.statusbar.showMessage(success_msg)
            else:
                error_msg = self.sdk.GetLastErrorMessage()
                print(f"开始录制失败: {error_msg}")
                QMessageBox.warning(self, "录制失败", f"开始录制失败: {error_msg}")

        except Exception as e:
            error_msg = f"录制过程出错: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def stop_record(self):
        """停止录制"""
        try:
            print("停止录制...")
            if self.recordID != 0:
                result = self.sdk.StopSaveRealData(self.recordID)
                if result:
                    print("录制停止成功")
                    self.is_recording = False
                    self.recordID = 0
                    self.record_btn.setText("开始录制(Start Record)")
                    self.record_status_label.setText("录制状态: 停止")
                    self.record_status_label.setStyleSheet(
                        "color: red; font-weight: bold;"
                    )

                    # 停止计时器
                    self.record_timer.stop()
                    self.record_time_label.setText("录制时间: 00:00:00")

                    self.statusbar.showMessage("录制已停止")
                    QMessageBox.information(self, "录制完成", "视频录制已完成并保存")
                else:
                    error_msg = self.sdk.GetLastErrorMessage()
                    print(f"停止录制失败: {error_msg}")
                    QMessageBox.warning(self, "停止录制失败", f"错误: {error_msg}")

        except Exception as e:
            error_msg = f"停止录制过程出错: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def update_record_time(self):
        """更新录制时间显示"""
        if self.is_recording and self.record_start_time:
            elapsed = int(time.time() - self.record_start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.record_time_label.setText(f"录制时间: {time_str}")

    def ptz_control(self, command, stop=False):
        """
        调用 PTZControlEx2 实现云台控制.
        :param command: SDK_PTZ_ControlType 枚举中的一个命令.
        :param stop: True 表示停止动作, False 表示开始动作.
        """
        if not self.loginID:
            QMessageBox.warning(self, "警告", "请先登录设备！")
            return

        try:
            channel = self.Channel_comboBox.currentIndex()
            speed = self.ptz_speed_spinBox.value()

            # 根据文档，dwStop 为 True 时表示停止，为 False 时表示开始
            # param1, param2, param3 在这里分别对应命令、速度等
            # 对于基础方向控制，param2 是速度
            self.sdk.PTZControlEx2(self.loginID, channel, command, 0, speed, 0, stop)
        except Exception as e:
            print(f"PTZ控制异常: {e}")

    def on_aspect_ratio_changed(self, index):
        """视频比例改变事件"""
        mode_name = "16:9 固定比例" if index == 0 else "自适应模式"
        print(f"视频比例模式切换到: {mode_name}")
        self.statusbar.showMessage(f"视频比例: {mode_name}")

        # 获取当前视频控件尺寸
        video_size = self.PlayWnd.size()
        print(f"当前视频控件尺寸: {video_size.width()}x{video_size.height()}")

    def resizeEvent(self, event):
        """窗口大小改变事件，确保视频区域正确更新"""
        super().resizeEvent(event)
        if hasattr(self, "PlayWnd"):
            self.PlayWnd.repaint()

    def DisConnectCallBack(self, lLoginID, pchDVRIP, nDVRPort, dwUser):
        """断线回调函数"""
        print(
            f"设备断线回调 - LoginID: {lLoginID}, IP: {pchDVRIP.decode()}, Port: {nDVRPort}"
        )
        self.setWindowTitle("实时预览与云台控制(RealPlay & PTZ)-离线(OffLine)")
        self.statusbar.showMessage("设备连接断开")

    def ReConnectCallBack(self, lLoginID, pchDVRIP, nDVRPort, dwUser):
        """断线重连回调函数"""
        print(
            f"设备重连回调 - LoginID: {lLoginID}, IP: {pchDVRIP.decode()}, Port: {nDVRPort}"
        )
        self.setWindowTitle("实时预览与云台控制(RealPlay & PTZ)-在线(OnLine)")
        self.statusbar.showMessage("设备重新连接")

    def closeEvent(self, event):
        """关闭窗口事件，清理资源"""
        try:
            # 清除全局引用
            global g_window_instance
            g_window_instance = None

            # 停止录制
            if self.is_recording:
                self.stop_record()

            # 停止预览和登出
            if self.loginID:
                if self.playID:
                    self.sdk.StopRealPlayEx(self.playID)
                self.sdk.Logout(self.loginID)

            # 停止计时器
            if self.record_timer.isActive():
                self.record_timer.stop()

            self.sdk.Cleanup()
        except Exception as e:
            print(f"清理资源时出错: {e}")
        event.accept()

    def on_config_changed(self):
        """配置信息改变时的处理"""
        # 可以在这里添加实时保存逻辑，但为了避免频繁保存，
        # 我们只在成功登录时保存配置
        pass

    def save_login_config(self, ip: str, port: int, username: str, password: str):
        """保存登录配置"""
        try:
            self.config_manager.save_device_config(
                ip=ip,
                port=port,
                username=username,
                password=password,
                device_type="camera",
            )
            print(f"已保存设备配置: {ip}")
        except Exception as e:
            print(f"保存配置失败: {e}")

    def load_saved_config(self, ip: str):
        """加载保存的配置"""
        try:
            config = self.config_manager.get_device_config(ip)
            if config:
                self.IP_lineEdit.setText(config.get("ip", ""))
                self.Port_lineEdit.setText(str(config.get("port", 37777)))
                self.Name_lineEdit.setText(config.get("username", ""))
                self.Pwd_lineEdit.setText(config.get("password", ""))
                return True
            return False
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False

    def get_device_time(self):
        """获取设备时间"""
        if not self.loginID:
            error_msg = "请先登录设备！"
            print(f"获取时间错误: {error_msg}")
            QMessageBox.warning(self, "警告", error_msg)
            return

        try:
            print("开始获取设备时间...")
            device_time = NET_TIME()
            result = self.sdk.GetDevConfig(
                self.loginID,
                int(EM_DEV_CFG_TYPE.TIMECFG),
                -1,
                device_time,
                sizeof(NET_TIME),
            )

            if result:
                # 将设备时间显示在界面上
                qt_datetime = QDateTime(
                    QDate(device_time.dwYear, device_time.dwMonth, device_time.dwDay),
                    QTime(
                        device_time.dwHour, device_time.dwMinute, device_time.dwSecond
                    ),
                )
                self.device_time_edit.setDateTime(qt_datetime)
                success_msg = (
                    f"获取设备时间成功: {qt_datetime.toString('yyyy-MM-dd hh:mm:ss')}"
                )
                print(success_msg)
                self.statusbar.showMessage(success_msg)
            else:
                error_msg = self.sdk.GetLastErrorMessage()
                print(f"获取时间失败: {error_msg}")
                QMessageBox.warning(self, "获取时间失败", f"错误: {error_msg}")

        except Exception as e:
            error_msg = f"获取时间过程出错: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def set_device_time(self):
        """设置设备时间"""
        if not self.loginID:
            error_msg = "请先登录设备！"
            print(f"设置时间错误: {error_msg}")
            QMessageBox.warning(self, "警告", error_msg)
            return

        try:
            print("开始设置设备时间...")
            # 获取界面上的时间
            qt_datetime = self.device_time_edit.dateTime()
            qt_date = qt_datetime.date()
            qt_time = qt_datetime.time()

            # 构造设备时间结构
            device_time = NET_TIME()
            device_time.dwYear = qt_date.year()
            device_time.dwMonth = qt_date.month()
            device_time.dwDay = qt_date.day()
            device_time.dwHour = qt_time.hour()
            device_time.dwMinute = qt_time.minute()
            device_time.dwSecond = qt_time.second()

            print(f"设置时间为: {qt_datetime.toString('yyyy-MM-dd hh:mm:ss')}")

            # 设置设备时间
            result = self.sdk.SetDevConfig(
                self.loginID,
                int(EM_DEV_CFG_TYPE.TIMECFG),
                -1,
                device_time,
                sizeof(NET_TIME),
            )

            if result:
                success_msg = (
                    f"设置设备时间成功: {qt_datetime.toString('yyyy-MM-dd hh:mm:ss')}"
                )
                print(success_msg)
                self.statusbar.showMessage(success_msg)
                QMessageBox.information(self, "设置成功", "设备时间设置成功")
            else:
                error_msg = self.sdk.GetLastErrorMessage()
                print(f"设置时间失败: {error_msg}")
                QMessageBox.warning(self, "设置时间失败", f"错误: {error_msg}")

        except Exception as e:
            error_msg = f"设置时间过程出错: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def sync_pc_time(self):
        """同步PC时间到设备"""
        if not self.loginID:
            error_msg = "请先登录设备！"
            print(f"同步时间错误: {error_msg}")
            QMessageBox.warning(self, "警告", error_msg)
            return

        try:
            print("开始同步PC时间到设备...")
            # 获取当前PC时间
            current_time = QDateTime.currentDateTime()
            self.device_time_edit.setDateTime(current_time)

            print(f"PC当前时间: {current_time.toString('yyyy-MM-dd hh:mm:ss')}")

            # 设置设备时间
            self.set_device_time()

        except Exception as e:
            error_msg = f"同步时间过程出错: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def restart_device(self):
        """重启设备"""
        if not self.loginID:
            error_msg = "请先登录设备！"
            print(f"重启设备错误: {error_msg}")
            QMessageBox.warning(self, "警告", error_msg)
            return

        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认重启",
            "确定要重启设备吗？设备重启后需要重新连接。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                print("发送设备重启命令...")
                result = self.sdk.RebootDev(self.loginID)
                if result:
                    print("重启命令发送成功")
                    QMessageBox.information(
                        self, "重启成功", "设备重启命令发送成功，设备正在重启..."
                    )
                    self.statusbar.showMessage("设备重启中...")

                    # 断开连接
                    if self.playID:
                        print("停止预览...")
                        self.sdk.StopRealPlayEx(self.playID)
                        self.playID = 0
                        self.play_btn.setText("预览(Play)")
                        self.PlayWnd.repaint()

                    # 停止录制
                    if self.is_recording:
                        print("停止录制...")
                        self.stop_record()

                else:
                    error_msg = self.sdk.GetLastErrorMessage()
                    print(f"重启失败: {error_msg}")
                    QMessageBox.warning(self, "重启失败", f"错误: {error_msg}")

            except Exception as e:
                error_msg = f"重启过程出错: {str(e)}"
                print(error_msg)
                QMessageBox.warning(self, "错误", error_msg)

    def open_log(self):
        """开启SDK日志"""
        try:
            print("开启SDK日志...")
            log_info = LOG_SET_PRINT_INFO()
            log_info.dwSize = sizeof(LOG_SET_PRINT_INFO)
            log_info.bSetFilePath = 1

            # 设置日志文件路径
            log_path = os.path.join(base_dir, "sdk_log.log")
            log_path = os.path.abspath(log_path)
            print(f"日志文件路径: {log_path}")

            log_info.szLogFilePath = log_path.encode("gbk")

            result = self.sdk.LogOpen(log_info)
            if result:
                success_msg = f"SDK日志已开启: {log_path}"
                print(success_msg)
                self.statusbar.showMessage("SDK日志已开启")
                QMessageBox.information(
                    self, "日志开启", f"SDK日志已开启，保存路径:\n{log_path}"
                )
            else:
                error_msg = self.sdk.GetLastErrorMessage()
                print(f"开启日志失败: {error_msg}")
                QMessageBox.warning(self, "开启日志失败", f"错误: {error_msg}")

        except Exception as e:
            error_msg = f"开启日志过程出错: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def close_log(self):
        """关闭SDK日志"""
        try:
            print("关闭SDK日志...")
            result = self.sdk.LogClose()
            if result:
                print("SDK日志已关闭")
                self.statusbar.showMessage("SDK日志已关闭")
                QMessageBox.information(self, "日志关闭", "SDK日志已关闭")
            else:
                error_msg = self.sdk.GetLastErrorMessage()
                print(f"关闭日志失败: {error_msg}")
                QMessageBox.warning(self, "关闭日志失败", f"错误: {error_msg}")

        except Exception as e:
            error_msg = f"关闭日志过程出错: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def start_alarm_listen(self):
        """开始报警监听"""
        if not self.loginID:
            error_msg = "请先登录设备！"
            print(f"报警监听错误: {error_msg}")
            QMessageBox.warning(self, "警告", error_msg)
            return

        try:
            print("开始报警监听...")
            result = self.sdk.StartListenEx(self.loginID)
            if result:
                self.is_alarm_listening = True
                self.start_alarm_btn.setEnabled(False)
                self.stop_alarm_btn.setEnabled(True)

                success_msg = "报警监听已开启"
                print(success_msg)
                self.statusbar.showMessage(success_msg)
                QMessageBox.information(
                    self, "监听成功", "报警监听已开启，系统将实时显示报警信息"
                )
            else:
                error_msg = self.sdk.GetLastErrorMessage()
                print(f"开启报警监听失败: {error_msg}")
                QMessageBox.warning(self, "监听失败", f"开启报警监听失败: {error_msg}")

        except Exception as e:
            error_msg = f"报警监听过程出错: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def stop_alarm_listen(self):
        """停止报警监听"""
        if not self.loginID:
            return

        try:
            print("停止报警监听...")
            result = self.sdk.StopListen(self.loginID)
            if result:
                self.is_alarm_listening = False
                self.start_alarm_btn.setEnabled(True)
                self.stop_alarm_btn.setEnabled(False)

                success_msg = "报警监听已停止"
                print(success_msg)
                self.statusbar.showMessage(success_msg)
            else:
                error_msg = self.sdk.GetLastErrorMessage()
                print(f"停止报警监听失败: {error_msg}")

        except Exception as e:
            error_msg = f"停止报警监听过程出错: {str(e)}"
            print(error_msg)

    def clear_alarm_records(self):
        """清空报警记录"""
        try:
            self.alarm_tableWidget.setRowCount(0)
            self.alarm_count = 0
            self.alarm_count_label.setText("报警记录: 0")
            self.statusbar.showMessage("报警记录已清空")
            print("报警记录已清空")
        except Exception as e:
            print(f"清空报警记录失败: {e}")

    def handle_alarm_callback(self, lCommand, alarm_info):
        """处理报警回调 - 在主线程中安全执行"""
        try:
            if lCommand == SDK_ALARM_TYPE.EVENT_MOTIONDETECT:
                print(f"处理动检报警: {alarm_info.channel_str}")

                # 限制记录数量，超过500条自动清空
                if self.alarm_count >= 500:
                    self.clear_alarm_records()

                # 添加新记录到表格
                row = self.alarm_tableWidget.rowCount()
                self.alarm_tableWidget.setRowCount(row + 1)

                # 填充数据
                items = [
                    str(row + 1),  # 序号
                    alarm_info.time_str,  # 时间
                    alarm_info.channel_str,  # 通道
                    alarm_info.alarm_type,  # 报警类型
                    alarm_info.status_str,  # 状态
                ]

                for col, item_text in enumerate(items):
                    item = QtWidgets.QTableWidgetItem(item_text)
                    self.alarm_tableWidget.setItem(row, col, item)

                # 更新计数
                self.alarm_count += 1
                self.alarm_count_label.setText(f"报警记录: {self.alarm_count}")

                # 滚动到最新记录
                self.alarm_tableWidget.scrollToBottom()

                # 更新状态栏
                self.statusbar.showMessage(
                    f"收到报警: 通道{alarm_info.channel_str} - {alarm_info.status_str}"
                )

        except Exception as e:
            print(f"处理报警回调失败: {e}")

    def generate_rtsp_url(self):
        """生成RTSP URL"""
        try:
            # 获取登录信息
            ip = self.IP_lineEdit.text().strip()
            username = self.Name_lineEdit.text().strip()
            password = self.Pwd_lineEdit.text().strip()
            rtsp_port = self.rtsp_port_edit.text().strip()

            if not all([ip, username, password]):
                QMessageBox.warning(self, "警告", "请先填写IP地址、用户名和密码信息！")
                return

            # 获取当前选择的通道和码流类型
            try:
                channel = self.Channel_comboBox.currentIndex() + 1  # 通道号从1开始
            except Exception:
                channel = 1  # 默认通道1

            # 获取码流类型 (0: 主码流, 1: 辅码流)
            try:
                subtype = self.StreamTyp_comboBox.currentIndex()  # 0: 主码流, 1: 辅码流
            except Exception:
                subtype = 0  # 默认主码流

            # 获取传输协议
            try:
                protocol_index = self.protocol_comboBox.currentIndex()  # 0: TCP, 1: UDP
                protocol = "tcp" if protocol_index == 0 else "udp"
            except Exception:
                protocol = "tcp"  # 默认TCP

            # 处理端口号
            if not rtsp_port or rtsp_port == "554":
                # 默认端口554可以省略
                port_part = ""
            else:
                port_part = f":{rtsp_port}"

            # 生成RTSP URL
            base_url = f"rtsp://{username}:{password}@{ip}{port_part}/cam/realmonitor?channel={channel}&subtype={subtype}"

            # 添加传输协议标识
            if protocol == "udp":
                rtsp_url = f"{base_url}?udp"  # UDP协议在URL最后加上?udp
            else:
                # TCP是默认协议，不需要额外标识
                rtsp_url = base_url

            # 显示生成的URL
            self.rtsp_url_edit.setText(rtsp_url)

            # 生成说明信息
            stream_type = "主码流" if subtype == 0 else "辅码流"
            protocol_type = "TCP" if protocol == "tcp" else "UDP"
            info_text = (
                f"已生成 通道{channel} {stream_type} {protocol_type}协议 的RTSP URL"
            )

            print(f"生成RTSP URL: {rtsp_url}")
            self.statusbar.showMessage(info_text)

        except Exception as e:
            error_msg = f"生成RTSP URL失败: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def copy_rtsp_url(self):
        """复制RTSP URL到剪贴板"""
        try:
            rtsp_url = self.rtsp_url_edit.toPlainText().strip()
            if not rtsp_url:
                QMessageBox.warning(self, "警告", "请先生成RTSP URL！")
                return

            # 复制到剪贴板
            clipboard = QApplication.clipboard()
            clipboard.setText(rtsp_url)

            print(f"已复制RTSP URL到剪贴板: {rtsp_url}")
            self.statusbar.showMessage("RTSP URL已复制到剪贴板")
            QMessageBox.information(self, "复制成功", "RTSP URL已复制到剪贴板")

        except Exception as e:
            error_msg = f"复制RTSP URL失败: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def open_ffmpeg_generator(self):
        """打开FFmpeg命令生成器窗口"""
        try:
            # 获取当前生成的RTSP URL
            rtsp_url = self.rtsp_url_edit.toPlainText().strip()

            if not rtsp_url:
                # 如果没有生成URL，提示用户先生成
                reply = QMessageBox.question(
                    self,
                    "提示",
                    "尚未生成RTSP URL，是否先生成URL？\n点击'是'生成URL，点击'否'打开空白的FFmpeg工具。",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes,
                )

                if reply == QMessageBox.Yes:
                    # 尝试生成URL
                    self.generate_rtsp_url()
                    rtsp_url = self.rtsp_url_edit.toPlainText().strip()

            # 导入FFmpeg窗口类
            from FFmpegCommandWindow import FFmpegCommandWindow

            # 如果窗口已存在，先关闭
            if self.ffmpeg_window is not None:
                self.ffmpeg_window.close()
                self.ffmpeg_window = None

            # 创建新的FFmpeg窗口
            self.ffmpeg_window = FFmpegCommandWindow(rtsp_url, self)
            self.ffmpeg_window.show()

            print(f"打开FFmpeg命令生成器，RTSP URL: {rtsp_url}")
            self.statusbar.showMessage("FFmpeg命令生成器已打开")

        except ImportError as e:
            error_msg = f"无法导入FFmpeg窗口模块: {str(e)}"
            print(error_msg)
            QMessageBox.warning(
                self,
                "模块错误",
                "FFmpeg命令生成器模块加载失败，请检查相关文件是否存在。",
            )
        except Exception as e:
            error_msg = f"打开FFmpeg命令生成器失败: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用程序信息
    app.setApplicationName("大华摄像头PTZ控制")
    app.setApplicationVersion("1.0")

    # 打印路径信息用于调试
    print(f"当前目录: {current_dir}")
    print(f"父目录: {parent_dir}")
    print(f"基础目录: {base_dir}")
    print(f"默认保存路径: {os.path.join(base_dir, 'capture')}")

    window = DahuaCamWindow()
    window.show()

    sys.exit(app.exec())
