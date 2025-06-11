# -*- coding: utf-8 -*-

from PySide6 import QtCore, QtWidgets
from AspectRatioVideoWidget import AspectRatioVideoWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        MainWindow.setMinimumSize(QtCore.QSize(640, 480))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 主水平布局
        self.main_layout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.main_layout.setObjectName("main_layout")

        # 左侧垂直布局（视频+控制）
        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_layout.setObjectName("left_layout")

        # 使用自定义的比例控制视频组件
        self.video_widget = AspectRatioVideoWidget()
        self.video_widget.setObjectName("video_widget")

        # 获取视频显示控件的引用（保持兼容性）
        self.PlayWnd = self.video_widget.get_video_widget()
        self.PlayWnd.setText("实时预览（RealPlay）")

        # 获取比例控制组件的引用（保持兼容性）
        self.aspect_comboBox = self.video_widget.aspect_combo
        self.resolution_label = self.video_widget.size_label

        self.left_layout.addWidget(self.video_widget)

        # 登录控制区域
        self.login_frame = QtWidgets.QFrame()
        self.login_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.login_frame.setMaximumHeight(120)
        self.login_layout = QtWidgets.QGridLayout(self.login_frame)

        # 第一行：IP和端口
        self.IP_label = QtWidgets.QLabel("IP地址(IP)")
        self.login_layout.addWidget(self.IP_label, 0, 0)
        self.IP_lineEdit = QtWidgets.QLineEdit()
        self.IP_lineEdit.setText("192.168.1.108")
        self.login_layout.addWidget(self.IP_lineEdit, 0, 1)

        self.Port_label = QtWidgets.QLabel("端口(Port)")
        self.login_layout.addWidget(self.Port_label, 0, 2)
        self.Port_lineEdit = QtWidgets.QLineEdit()
        self.Port_lineEdit.setText("37777")
        self.login_layout.addWidget(self.Port_lineEdit, 0, 3)

        self.Channel_label = QtWidgets.QLabel("通道(Channel)")
        self.login_layout.addWidget(self.Channel_label, 0, 4)
        self.Channel_comboBox = QtWidgets.QComboBox()
        self.login_layout.addWidget(self.Channel_comboBox, 0, 5)

        # 第二行：用户名和密码
        self.Name_label = QtWidgets.QLabel("用户名(Name)")
        self.login_layout.addWidget(self.Name_label, 1, 0)
        self.Name_lineEdit = QtWidgets.QLineEdit()
        self.Name_lineEdit.setText("admin")
        self.login_layout.addWidget(self.Name_lineEdit, 1, 1)

        self.Pwd_label = QtWidgets.QLabel("密码(PWD)")
        self.login_layout.addWidget(self.Pwd_label, 1, 2)
        self.Pwd_lineEdit = QtWidgets.QLineEdit()
        self.Pwd_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.Pwd_lineEdit.setText("admin123")
        self.login_layout.addWidget(self.Pwd_lineEdit, 1, 3)

        # 第三行：码流和按钮
        self.label_5 = QtWidgets.QLabel("码流(Stream)")
        self.login_layout.addWidget(self.label_5, 2, 0)
        self.StreamTyp_comboBox = QtWidgets.QComboBox()
        self.StreamTyp_comboBox.setEnabled(False)
        self.StreamTyp_comboBox.addItem("主码流(MainStream)")
        self.StreamTyp_comboBox.addItem("辅码流(ExtraStream)")
        self.login_layout.addWidget(self.StreamTyp_comboBox, 2, 1)

        # 渲染模式选择
        self.render_mode_label = QtWidgets.QLabel("渲染模式(Render)")
        self.login_layout.addWidget(self.render_mode_label, 2, 2)
        self.render_mode_comboBox = QtWidgets.QComboBox()
        self.render_mode_comboBox.setEnabled(False)
        # self.render_mode_comboBox.addItem("回调模式(CallBack)")
        self.login_layout.addWidget(self.render_mode_comboBox, 2, 3)

        self.login_btn = QtWidgets.QPushButton("登录(Login)")
        self.login_btn.setMinimumSize(QtCore.QSize(100, 30))
        self.login_layout.addWidget(self.login_btn, 2, 4)

        self.play_btn = QtWidgets.QPushButton("预览(Play)")
        self.play_btn.setMinimumSize(QtCore.QSize(100, 30))
        self.play_btn.setEnabled(False)
        self.login_layout.addWidget(self.play_btn, 2, 5)

        self.left_layout.addWidget(self.login_frame)
        self.main_layout.addLayout(self.left_layout, 3)

        # 右侧控制区域 - 分为两列
        self.right_layout = QtWidgets.QHBoxLayout()
        self.right_layout.setSpacing(10)

        # 第一列：相机控制区域 - 分为三个功能组
        self.camera_control_widget = QtWidgets.QWidget()
        self.camera_control_widget.setMinimumSize(QtCore.QSize(220, 400))
        self.camera_control_widget.setMaximumWidth(250)
        self.camera_control_layout = QtWidgets.QVBoxLayout(self.camera_control_widget)
        self.camera_control_layout.setSpacing(8)

        # 第一组：云台控制 (PTZ Control)
        self.ptz_groupBox = QtWidgets.QGroupBox("云台控制(PTZ Control)")
        self.ptz_groupBox.setEnabled(False)
        self.ptz_layout = QtWidgets.QVBoxLayout(self.ptz_groupBox)

        # 方向控制区域
        self.direction_frame = QtWidgets.QFrame()
        self.direction_layout = QtWidgets.QGridLayout(self.direction_frame)

        # 方向按钮
        button_size = QtCore.QSize(45, 45)
        self.ptz_up_btn = QtWidgets.QPushButton("↑")
        self.ptz_up_btn.setMinimumSize(button_size)
        self.direction_layout.addWidget(self.ptz_up_btn, 0, 1)

        self.ptz_left_btn = QtWidgets.QPushButton("←")
        self.ptz_left_btn.setMinimumSize(button_size)
        self.direction_layout.addWidget(self.ptz_left_btn, 1, 0)

        self.ptz_right_btn = QtWidgets.QPushButton("→")
        self.ptz_right_btn.setMinimumSize(button_size)
        self.direction_layout.addWidget(self.ptz_right_btn, 1, 2)

        self.ptz_down_btn = QtWidgets.QPushButton("↓")
        self.ptz_down_btn.setMinimumSize(button_size)
        self.direction_layout.addWidget(self.ptz_down_btn, 2, 1)

        self.ptz_layout.addWidget(self.direction_frame)

        # 速度控制
        self.speed_frame = QtWidgets.QFrame()
        self.speed_layout = QtWidgets.QHBoxLayout(self.speed_frame)
        self.ptz_speed_label = QtWidgets.QLabel("速度(Speed)")
        self.speed_layout.addWidget(self.ptz_speed_label)
        self.ptz_speed_spinBox = QtWidgets.QSpinBox()
        self.ptz_speed_spinBox.setMinimum(1)
        self.ptz_speed_spinBox.setMaximum(8)
        self.ptz_speed_spinBox.setValue(4)
        self.speed_layout.addWidget(self.ptz_speed_spinBox)
        self.speed_layout.addStretch()
        self.ptz_layout.addWidget(self.speed_frame)

        self.camera_control_layout.addWidget(self.ptz_groupBox)

        # 第二组：相机控制 (Camera Control)
        self.camera_groupBox = QtWidgets.QGroupBox("相机控制(Camera Control)")
        self.camera_groupBox.setEnabled(False)
        self.camera_layout = QtWidgets.QVBoxLayout(self.camera_groupBox)

        # 变倍控制
        self.zoom_frame = QtWidgets.QFrame()
        self.zoom_layout = QtWidgets.QHBoxLayout(self.zoom_frame)
        self.zoom_label = QtWidgets.QLabel("变倍(Zoom)")
        self.zoom_layout.addWidget(self.zoom_label)
        self.zoom_add_btn = QtWidgets.QPushButton("+")
        self.zoom_add_btn.setMinimumSize(QtCore.QSize(35, 28))
        self.zoom_layout.addWidget(self.zoom_add_btn)
        self.zoom_dec_btn = QtWidgets.QPushButton("-")
        self.zoom_dec_btn.setMinimumSize(QtCore.QSize(35, 28))
        self.zoom_layout.addWidget(self.zoom_dec_btn)
        self.zoom_layout.addStretch()
        self.camera_layout.addWidget(self.zoom_frame)

        # 聚焦控制
        self.focus_frame = QtWidgets.QFrame()
        self.focus_layout = QtWidgets.QHBoxLayout(self.focus_frame)
        self.focus_label = QtWidgets.QLabel("聚焦(Focus)")
        self.focus_layout.addWidget(self.focus_label)
        self.focus_add_btn = QtWidgets.QPushButton("+")
        self.focus_add_btn.setMinimumSize(QtCore.QSize(35, 28))
        self.focus_layout.addWidget(self.focus_add_btn)
        self.focus_dec_btn = QtWidgets.QPushButton("-")
        self.focus_dec_btn.setMinimumSize(QtCore.QSize(35, 28))
        self.focus_layout.addWidget(self.focus_dec_btn)
        self.focus_layout.addStretch()
        self.camera_layout.addWidget(self.focus_frame)

        self.camera_control_layout.addWidget(self.camera_groupBox)

        # 第三组：录制与抓拍 (Record & Capture)
        self.record_groupBox = QtWidgets.QGroupBox("录制与抓拍(Record & Capture)")
        self.record_groupBox.setEnabled(False)
        self.record_layout = QtWidgets.QVBoxLayout(self.record_groupBox)

        # 抓拍按钮
        self.capture_btn = QtWidgets.QPushButton("抓拍(Capture)")
        self.capture_btn.setMinimumSize(QtCore.QSize(100, 32))
        self.capture_btn.setEnabled(False)
        self.record_layout.addWidget(self.capture_btn)

        # 录制按钮
        self.record_btn = QtWidgets.QPushButton("开始录制(Start Record)")
        self.record_btn.setMinimumSize(QtCore.QSize(100, 32))
        self.record_btn.setEnabled(False)
        self.record_layout.addWidget(self.record_btn)

        # 录制状态标签
        self.record_status_label = QtWidgets.QLabel("录制状态: 停止")
        self.record_status_label.setStyleSheet(
            "color: red; font-weight: bold; font-size: 11px;"
        )
        self.record_layout.addWidget(self.record_status_label)

        # 录制时间标签
        self.record_time_label = QtWidgets.QLabel("录制时间: 00:00:00")
        self.record_time_label.setStyleSheet("font-size: 11px;")
        self.record_layout.addWidget(self.record_time_label)

        # 保存路径显示
        self.save_path_label = QtWidgets.QLabel("保存路径:")
        self.save_path_label.setStyleSheet("font-size: 11px;")
        self.record_layout.addWidget(self.save_path_label)

        self.save_path_edit = QtWidgets.QLineEdit()
        self.save_path_edit.setText("")
        self.save_path_edit.setReadOnly(True)
        self.save_path_edit.setMaximumHeight(25)
        self.record_layout.addWidget(self.save_path_edit)

        # 选择保存路径按钮
        self.select_path_btn = QtWidgets.QPushButton("选择路径(Select Path)")
        self.select_path_btn.setMinimumSize(QtCore.QSize(100, 28))
        self.record_layout.addWidget(self.select_path_btn)

        self.camera_control_layout.addWidget(self.record_groupBox)
        self.camera_control_layout.addStretch()

        # 添加相机控制区域到右侧第一列
        self.right_layout.addWidget(self.camera_control_widget)

        # 第二列：系统设置区域
        self.system_groupBox = QtWidgets.QGroupBox("系统设置(System Settings)")
        self.system_groupBox.setEnabled(True)
        self.system_groupBox.setMinimumSize(QtCore.QSize(220, 400))
        self.system_groupBox.setMaximumWidth(250)

        self.system_layout = QtWidgets.QVBoxLayout(self.system_groupBox)

        # 时间同步区域
        self.time_groupBox = QtWidgets.QGroupBox("时间同步(Time Sync)")
        self.time_layout = QtWidgets.QVBoxLayout(self.time_groupBox)

        # 时间显示和编辑
        self.time_edit_layout = QtWidgets.QHBoxLayout()
        self.time_label = QtWidgets.QLabel("设备时间:")
        self.time_edit_layout.addWidget(self.time_label)

        self.device_time_edit = QtWidgets.QDateTimeEdit()
        self.device_time_edit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.device_time_edit.setMinimumWidth(150)
        self.time_edit_layout.addWidget(self.device_time_edit)

        self.time_layout.addLayout(self.time_edit_layout)

        # 时间操作按钮（调整为垂直布局以适应窄列）
        self.time_btn_layout = QtWidgets.QVBoxLayout()

        self.get_time_btn = QtWidgets.QPushButton("获取时间(Get)")
        self.get_time_btn.setMinimumSize(QtCore.QSize(100, 30))
        self.get_time_btn.setEnabled(False)
        self.time_btn_layout.addWidget(self.get_time_btn)

        self.set_time_btn = QtWidgets.QPushButton("设置时间(Set)")
        self.set_time_btn.setMinimumSize(QtCore.QSize(100, 30))
        self.set_time_btn.setEnabled(False)
        self.time_btn_layout.addWidget(self.set_time_btn)

        self.sync_time_btn = QtWidgets.QPushButton("同步PC时间(Sync)")
        self.sync_time_btn.setMinimumSize(QtCore.QSize(100, 30))
        self.sync_time_btn.setEnabled(False)
        self.time_btn_layout.addWidget(self.sync_time_btn)

        self.time_layout.addLayout(self.time_btn_layout)
        self.system_layout.addWidget(self.time_groupBox)

        # 设备操作区域
        self.operation_groupBox = QtWidgets.QGroupBox("设备操作(Device Operation)")
        self.operation_layout = QtWidgets.QVBoxLayout(self.operation_groupBox)

        # 重启按钮
        self.restart_btn = QtWidgets.QPushButton("设备重启(Restart)")
        self.restart_btn.setMinimumSize(QtCore.QSize(100, 35))
        self.restart_btn.setEnabled(False)
        self.operation_layout.addWidget(self.restart_btn)

        # 日志控制按钮（调整为垂直布局）
        self.log_btn_layout = QtWidgets.QVBoxLayout()

        self.open_log_btn = QtWidgets.QPushButton("开启日志(Open Log)")
        self.open_log_btn.setMinimumSize(QtCore.QSize(100, 30))
        self.log_btn_layout.addWidget(self.open_log_btn)

        self.close_log_btn = QtWidgets.QPushButton("关闭日志(Close Log)")
        self.close_log_btn.setMinimumSize(QtCore.QSize(100, 30))
        self.log_btn_layout.addWidget(self.close_log_btn)

        self.operation_layout.addLayout(self.log_btn_layout)
        self.system_layout.addWidget(self.operation_groupBox)

        # RTSP URL生成区域
        self.rtsp_groupBox = QtWidgets.QGroupBox("RTSP URL生成(RTSP URL Generator)")
        self.rtsp_layout = QtWidgets.QVBoxLayout(self.rtsp_groupBox)

        # RTSP端口设置
        self.rtsp_port_layout = QtWidgets.QHBoxLayout()
        self.rtsp_port_label = QtWidgets.QLabel("RTSP端口:")
        self.rtsp_port_layout.addWidget(self.rtsp_port_label)

        self.rtsp_port_edit = QtWidgets.QLineEdit()
        self.rtsp_port_edit.setText("554")
        self.rtsp_port_edit.setMaximumWidth(60)
        self.rtsp_port_layout.addWidget(self.rtsp_port_edit)

        self.rtsp_port_layout.addStretch()
        self.rtsp_layout.addLayout(self.rtsp_port_layout)

        # 传输协议选择
        self.protocol_layout = QtWidgets.QHBoxLayout()
        self.protocol_label = QtWidgets.QLabel("传输协议:")
        self.protocol_layout.addWidget(self.protocol_label)

        self.protocol_comboBox = QtWidgets.QComboBox()
        self.protocol_comboBox.addItem("TCP")
        self.protocol_comboBox.addItem("UDP")
        self.protocol_comboBox.setCurrentIndex(0)  # 默认TCP
        self.protocol_comboBox.setMaximumWidth(80)
        self.protocol_layout.addWidget(self.protocol_comboBox)

        self.protocol_layout.addStretch()
        self.rtsp_layout.addLayout(self.protocol_layout)

        # 生成URL按钮
        self.generate_url_btn = QtWidgets.QPushButton("生成RTSP URL(Generate)")
        self.generate_url_btn.setMinimumSize(QtCore.QSize(100, 30))
        self.rtsp_layout.addWidget(self.generate_url_btn)

        # URL显示区域
        self.rtsp_url_label = QtWidgets.QLabel("RTSP URL:")
        self.rtsp_url_label.setStyleSheet("font-size: 11px;")
        self.rtsp_layout.addWidget(self.rtsp_url_label)

        self.rtsp_url_edit = QtWidgets.QTextEdit()
        self.rtsp_url_edit.setMaximumHeight(60)
        self.rtsp_url_edit.setReadOnly(True)
        self.rtsp_url_edit.setStyleSheet(
            "font-size: 10px; font-family: Consolas, monospace;"
        )
        self.rtsp_layout.addWidget(self.rtsp_url_edit)

        # 第一行按钮：复制URL
        self.copy_url_btn = QtWidgets.QPushButton("复制URL(Copy)")
        self.copy_url_btn.setMinimumSize(QtCore.QSize(100, 30))
        self.rtsp_layout.addWidget(self.copy_url_btn)

        # 第二行按钮：FFmpeg工具
        self.ffmpeg_generator_btn = QtWidgets.QPushButton(
            "FFmpeg命令生成器(FFmpeg Command Generator)"
        )
        self.ffmpeg_generator_btn.setMinimumSize(QtCore.QSize(200, 30))
        self.rtsp_layout.addWidget(self.ffmpeg_generator_btn)

        self.system_layout.addWidget(self.rtsp_groupBox)
        self.system_layout.addStretch()

        # 添加系统设置组到右侧第二列
        self.right_layout.addWidget(self.system_groupBox)

        # 将右侧布局添加到主布局
        self.main_layout.addLayout(self.right_layout, 1)

        # 底部报警监听区域
        self.alarm_groupBox = QtWidgets.QGroupBox("报警监听(Alarm Listen)")
        self.alarm_groupBox.setMaximumHeight(300)
        self.alarm_layout = QtWidgets.QVBoxLayout(self.alarm_groupBox)

        # 报警控制按钮区域
        self.alarm_control_layout = QtWidgets.QHBoxLayout()

        self.start_alarm_btn = QtWidgets.QPushButton("开始监听(Start Listen)")
        self.start_alarm_btn.setMinimumSize(QtCore.QSize(120, 35))
        self.start_alarm_btn.setEnabled(False)
        self.alarm_control_layout.addWidget(self.start_alarm_btn)

        self.stop_alarm_btn = QtWidgets.QPushButton("停止监听(Stop Listen)")
        self.stop_alarm_btn.setMinimumSize(QtCore.QSize(120, 35))
        self.stop_alarm_btn.setEnabled(False)
        self.alarm_control_layout.addWidget(self.stop_alarm_btn)

        self.clear_alarm_btn = QtWidgets.QPushButton("清空记录(Clear)")
        self.clear_alarm_btn.setMinimumSize(QtCore.QSize(100, 35))
        self.alarm_control_layout.addWidget(self.clear_alarm_btn)

        self.alarm_control_layout.addStretch()

        # 报警记录数量显示
        self.alarm_count_label = QtWidgets.QLabel("报警记录: 0")
        self.alarm_count_label.setStyleSheet("font-weight: bold; color: blue;")
        self.alarm_control_layout.addWidget(self.alarm_count_label)

        self.alarm_layout.addLayout(self.alarm_control_layout)

        # 报警列表表格
        self.alarm_tableWidget = QtWidgets.QTableWidget()
        self.alarm_tableWidget.setColumnCount(5)
        self.alarm_tableWidget.setRowCount(0)

        # 设置表头
        alarm_headers = [
            "序号(No.)",
            "时间(Time)",
            "通道(Channel)",
            "报警类型(Alarm Type)",
            "状态(Status)",
        ]

        for i, header in enumerate(alarm_headers):
            item = QtWidgets.QTableWidgetItem(header)
            self.alarm_tableWidget.setHorizontalHeaderItem(i, item)

        # 设置表格属性
        self.alarm_tableWidget.horizontalHeader().setDefaultSectionSize(150)
        self.alarm_tableWidget.horizontalHeader().setMinimumSectionSize(80)
        self.alarm_tableWidget.verticalHeader().setVisible(False)
        self.alarm_tableWidget.setAlternatingRowColors(True)
        self.alarm_tableWidget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        self.alarm_tableWidget.setMaximumHeight(200)

        self.alarm_layout.addWidget(self.alarm_tableWidget)

        # 将报警监听区域添加到主垂直布局
        self.left_layout.addWidget(self.alarm_groupBox)

        MainWindow.setCentralWidget(self.centralwidget)

        # 状态栏
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(
            _translate("MainWindow", "实时预览与云台控制(RealPlay & PTZ)")
        )
        self.PlayWnd.setText(_translate("MainWindow", "实时预览（RealPlay）"))
