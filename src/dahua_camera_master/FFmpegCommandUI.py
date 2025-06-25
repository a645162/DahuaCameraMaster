
from PySide6 import QtCore, QtWidgets


class Ui_FFmpegWindow:
    def setupUi(self, FFmpegWindow):
        FFmpegWindow.setObjectName("FFmpegWindow")
        FFmpegWindow.resize(700, 600)
        FFmpegWindow.setWindowTitle("FFmpeg 命令生成器(FFmpeg Command Generator)")

        self.centralwidget = QtWidgets.QWidget(FFmpegWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 主布局
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setSpacing(10)

        # RTSP URL显示区域
        self.url_groupBox = QtWidgets.QGroupBox("RTSP URL")
        self.url_layout = QtWidgets.QVBoxLayout(self.url_groupBox)

        self.rtsp_url_edit = QtWidgets.QTextEdit()
        self.rtsp_url_edit.setMaximumHeight(60)
        self.rtsp_url_edit.setReadOnly(True)
        self.rtsp_url_edit.setStyleSheet(
            "font-family: Consolas, monospace; font-size: 10px;"
        )
        self.url_layout.addWidget(self.rtsp_url_edit)

        self.main_layout.addWidget(self.url_groupBox)

        # 功能选择区域
        self.function_groupBox = QtWidgets.QGroupBox("功能选择(Function Selection)")
        self.function_layout = QtWidgets.QVBoxLayout(self.function_groupBox)

        # 功能选择按钮组
        self.function_button_group = QtWidgets.QButtonGroup()

        self.record_fixed_radio = QtWidgets.QRadioButton(
            "录制固定时长视频(Record Fixed Duration)"
        )
        self.record_fixed_radio.setChecked(True)
        self.function_button_group.addButton(self.record_fixed_radio, 0)
        self.function_layout.addWidget(self.record_fixed_radio)

        self.record_segment_radio = QtWidgets.QRadioButton(
            "按时间分段保存(Time Segment Recording)"
        )
        self.function_button_group.addButton(self.record_segment_radio, 1)
        self.function_layout.addWidget(self.record_segment_radio)

        self.capture_image_radio = QtWidgets.QRadioButton("截取图片(Capture Image)")
        self.function_button_group.addButton(self.capture_image_radio, 2)
        self.function_layout.addWidget(self.capture_image_radio)

        self.main_layout.addWidget(self.function_groupBox)

        # 参数配置区域 - 使用堆叠窗口
        self.params_stackedWidget = QtWidgets.QStackedWidget()

        # 固定时长录制参数页面
        self.fixed_params_widget = QtWidgets.QWidget()
        self.fixed_params_layout = QtWidgets.QFormLayout(self.fixed_params_widget)

        # 录制时长选择
        self.duration_layout = QtWidgets.QHBoxLayout()

        self.unlimited_duration_checkBox = QtWidgets.QCheckBox("无限期录制(Unlimited)")
        self.duration_layout.addWidget(self.unlimited_duration_checkBox)

        self.duration_spinBox = QtWidgets.QSpinBox()
        self.duration_spinBox.setMinimum(1)
        self.duration_spinBox.setMaximum(86400)  # 最大24小时
        self.duration_spinBox.setValue(60)
        self.duration_spinBox.setSuffix(" 秒")
        self.duration_layout.addWidget(self.duration_spinBox)

        self.fixed_params_layout.addRow("录制时长(Duration):", self.duration_layout)

        self.output_file_edit = QtWidgets.QLineEdit()
        self.output_file_edit.setText("output.mp4")
        self.fixed_params_layout.addRow("输出文件(Output File):", self.output_file_edit)

        self.params_stackedWidget.addWidget(self.fixed_params_widget)

        # 分段录制参数页面
        self.segment_params_widget = QtWidgets.QWidget()
        self.segment_params_layout = QtWidgets.QFormLayout(self.segment_params_widget)

        self.segment_time_spinBox = QtWidgets.QSpinBox()
        self.segment_time_spinBox.setMinimum(10)
        self.segment_time_spinBox.setMaximum(3600)
        self.segment_time_spinBox.setValue(60)
        self.segment_time_spinBox.setSuffix(" 秒")
        self.segment_params_layout.addRow(
            "分段时长(Segment Time):", self.segment_time_spinBox
        )

        self.output_dir_edit = QtWidgets.QLineEdit()
        self.output_dir_edit.setText("./recordings/")
        self.segment_params_layout.addRow(
            "输出目录(Output Directory):", self.output_dir_edit
        )

        self.select_dir_btn = QtWidgets.QPushButton("选择目录(Select Directory)")
        self.segment_params_layout.addRow("", self.select_dir_btn)

        self.params_stackedWidget.addWidget(self.segment_params_widget)

        # 截图参数页面
        self.capture_params_widget = QtWidgets.QWidget()
        self.capture_params_layout = QtWidgets.QFormLayout(self.capture_params_widget)

        self.capture_time_edit = QtWidgets.QLineEdit()
        self.capture_time_edit.setText("00:00:05")
        self.capture_time_edit.setPlaceholderText("HH:MM:SS格式")
        self.capture_params_layout.addRow(
            "截取时间点(Capture Time):", self.capture_time_edit
        )

        self.image_file_edit = QtWidgets.QLineEdit()
        self.image_file_edit.setText("capture.jpg")
        self.capture_params_layout.addRow(
            "输出图片(Output Image):", self.image_file_edit
        )

        self.params_stackedWidget.addWidget(self.capture_params_widget)

        self.main_layout.addWidget(self.params_stackedWidget)

        # 高级选项区域
        self.advanced_groupBox = QtWidgets.QGroupBox("高级选项(Advanced Options)")
        self.advanced_layout = QtWidgets.QFormLayout(self.advanced_groupBox)

        self.transport_comboBox = QtWidgets.QComboBox()
        self.transport_comboBox.addItem("TCP")
        self.transport_comboBox.addItem("UDP")
        self.transport_comboBox.setCurrentIndex(0)
        self.advanced_layout.addRow("传输协议(Transport):", self.transport_comboBox)

        # 编码模式选择
        self.encoding_mode_layout = QtWidgets.QVBoxLayout()

        self.copy_mode_radio = QtWidgets.QRadioButton("直接复制流(Stream Copy) - 推荐")
        self.copy_mode_radio.setChecked(True)
        self.encoding_mode_layout.addWidget(self.copy_mode_radio)

        self.encode_mode_radio = QtWidgets.QRadioButton("重新编码(Re-encode)")
        self.encoding_mode_layout.addWidget(self.encode_mode_radio)

        self.advanced_layout.addRow(
            "编码模式(Encoding Mode):", self.encoding_mode_layout
        )

        # 编码器选择（仅在重新编码时启用）
        self.encoder_comboBox = QtWidgets.QComboBox()
        self.encoder_comboBox.addItem("libx264 (软件编码 CPU)", "libx264")
        self.encoder_comboBox.addItem("h264_nvenc (NVIDIA GPU)", "h264_nvenc")
        self.encoder_comboBox.addItem("h264_amf (AMD GPU)", "h264_amf")
        self.encoder_comboBox.addItem("h264_qsv (Intel QSV)", "h264_qsv")
        self.encoder_comboBox.addItem("libx265 (H.265软件编码)", "libx265")
        self.encoder_comboBox.addItem("hevc_nvenc (H.265 NVIDIA)", "hevc_nvenc")
        self.encoder_comboBox.addItem("hevc_amf (H.265 AMD)", "hevc_amf")
        self.encoder_comboBox.addItem("hevc_qsv (H.265 Intel)", "hevc_qsv")
        self.encoder_comboBox.setEnabled(False)
        self.advanced_layout.addRow("视频编码器(Video Encoder):", self.encoder_comboBox)

        # 编码质量预设
        self.preset_comboBox = QtWidgets.QComboBox()
        self.preset_comboBox.addItem("ultrafast (最快速度)", "ultrafast")
        self.preset_comboBox.addItem("superfast (超快速度)", "superfast")
        self.preset_comboBox.addItem("veryfast (很快速度)", "veryfast")
        self.preset_comboBox.addItem("faster (快速度)", "faster")
        self.preset_comboBox.addItem("fast (快速)", "fast")
        self.preset_comboBox.addItem("medium (中等) - 默认", "medium")
        self.preset_comboBox.addItem("slow (慢速)", "slow")
        self.preset_comboBox.addItem("slower (更慢)", "slower")
        self.preset_comboBox.addItem("veryslow (最慢)", "veryslow")
        self.preset_comboBox.setCurrentIndex(5)  # 默认medium
        self.preset_comboBox.setEnabled(False)
        self.advanced_layout.addRow("编码预设(Encoding Preset):", self.preset_comboBox)

        # CRF质量控制
        self.crf_layout = QtWidgets.QHBoxLayout()

        self.crf_spinBox = QtWidgets.QSpinBox()
        self.crf_spinBox.setMinimum(0)
        self.crf_spinBox.setMaximum(51)
        self.crf_spinBox.setValue(23)
        self.crf_spinBox.setEnabled(False)
        self.crf_layout.addWidget(self.crf_spinBox)

        self.crf_label = QtWidgets.QLabel("(0=无损, 23=默认, 51=最差)")
        self.crf_label.setStyleSheet("color: gray; font-size: 10px;")
        self.crf_layout.addWidget(self.crf_label)

        self.advanced_layout.addRow("视频质量CRF:", self.crf_layout)

        # 音频编码器
        self.audio_encoder_comboBox = QtWidgets.QComboBox()
        self.audio_encoder_comboBox.addItem("aac (推荐)", "aac")
        self.audio_encoder_comboBox.addItem("mp3", "mp3")
        self.audio_encoder_comboBox.addItem("copy (复制原始)", "copy")
        self.audio_encoder_comboBox.addItem("禁用音频", "none")
        self.audio_encoder_comboBox.setEnabled(False)
        self.advanced_layout.addRow(
            "音频编码器(Audio Encoder):", self.audio_encoder_comboBox
        )

        self.wallclock_checkBox = QtWidgets.QCheckBox("使用系统时间戳")
        self.wallclock_checkBox.setChecked(True)
        self.advanced_layout.addRow("时间戳(Timestamp):", self.wallclock_checkBox)

        self.main_layout.addWidget(self.advanced_groupBox)

        # 命令生成和操作区域
        self.command_groupBox = QtWidgets.QGroupBox(
            "生成的FFmpeg命令(Generated FFmpeg Command)"
        )
        self.command_layout = QtWidgets.QVBoxLayout(self.command_groupBox)

        # 按钮区域
        self.button_layout = QtWidgets.QHBoxLayout()

        self.generate_btn = QtWidgets.QPushButton("生成命令(Generate Command)")
        self.generate_btn.setMinimumSize(QtCore.QSize(120, 35))
        self.button_layout.addWidget(self.generate_btn)

        self.copy_cmd_btn = QtWidgets.QPushButton("复制命令(Copy Command)")
        self.copy_cmd_btn.setMinimumSize(QtCore.QSize(120, 35))
        self.copy_cmd_btn.setEnabled(False)
        self.button_layout.addWidget(self.copy_cmd_btn)

        self.save_script_btn = QtWidgets.QPushButton("保存脚本(Save Script)")
        self.save_script_btn.setMinimumSize(QtCore.QSize(120, 35))
        self.save_script_btn.setEnabled(False)
        self.button_layout.addWidget(self.save_script_btn)

        self.button_layout.addStretch()

        self.command_layout.addLayout(self.button_layout)

        # 命令显示区域
        self.command_text = QtWidgets.QTextEdit()
        self.command_text.setMaximumHeight(120)
        self.command_text.setReadOnly(True)
        self.command_text.setStyleSheet(
            "font-family: Consolas, monospace; font-size: 11px; background-color: #f0f0f0;"
        )
        self.command_layout.addWidget(self.command_text)

        self.main_layout.addWidget(self.command_groupBox)

        # 说明区域
        self.help_groupBox = QtWidgets.QGroupBox("使用说明(Help)")
        self.help_layout = QtWidgets.QVBoxLayout(self.help_groupBox)

        self.help_text = QtWidgets.QTextEdit()
        self.help_text.setMaximumHeight(80)
        self.help_text.setReadOnly(True)
        self.help_text.setStyleSheet("font-size: 10px; color: #666;")
        self.help_text.setText(
            "1. 固定时长录制：录制指定时间长度的视频文件\n"
            "2. 分段录制：将长时间录制分割成多个文件，适合监控场景\n"
            "3. 截取图片：从视频流中截取单帧图片\n"
            "注意：运行前请确保已安装FFmpeg并添加到系统环境变量"
        )
        self.help_layout.addWidget(self.help_text)

        self.main_layout.addWidget(self.help_groupBox)

        FFmpegWindow.setCentralWidget(self.centralwidget)

        # 状态栏
        self.statusbar = QtWidgets.QStatusBar(FFmpegWindow)
        self.statusbar.setObjectName("statusbar")
        FFmpegWindow.setStatusBar(self.statusbar)
