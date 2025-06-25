# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QApplication

from FFmpegCommandUI import Ui_FFmpegWindow


class FFmpegCommandWindow(QMainWindow, Ui_FFmpegWindow):
    def __init__(self, rtsp_url="", parent=None):
        super(FFmpegCommandWindow, self).__init__(parent)
        self.setupUi(self)

        # 设置传入的RTSP URL
        self.rtsp_url_edit.setText(rtsp_url)

        # 生成的命令
        self.generated_command = ""

        # 初始化界面
        self._init_ui()

    def _init_ui(self):
        """初始化界面和信号连接"""
        # 设置窗口属性
        self.setWindowTitle("FFmpeg 命令生成器 - RTSP视频流处理工具")

        # 连接信号
        self.function_button_group.buttonClicked.connect(self.on_function_changed)
        self.generate_btn.clicked.connect(self.generate_command)
        self.copy_cmd_btn.clicked.connect(self.copy_command)
        self.save_script_btn.clicked.connect(self.save_script)
        self.select_dir_btn.clicked.connect(self.select_output_directory)

        # 连接编码模式变化事件
        self.copy_mode_radio.toggled.connect(self.on_encoding_mode_changed)
        self.encode_mode_radio.toggled.connect(self.on_encoding_mode_changed)

        # 连接无限期录制变化事件
        self.unlimited_duration_checkBox.toggled.connect(
            self.on_unlimited_duration_changed
        )

        # 初始化堆叠窗口
        self.params_stackedWidget.setCurrentIndex(0)

        # 设置默认值
        self.setup_default_values()

    def setup_default_values(self):
        """设置默认值"""
        # 根据当前时间生成默认文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 固定时长录制默认文件名
        self.output_file_edit.setText(f"recording_{timestamp}.mp4")

        # 截图默认文件名
        self.image_file_edit.setText(f"capture_{timestamp}.jpg")

        # 分段录制默认目录
        if (
            not self.output_dir_edit.text()
            or self.output_dir_edit.text() == "./recordings/"
        ):
            default_dir = os.path.join(os.getcwd(), "ffmpeg_recordings")
            self.output_dir_edit.setText(default_dir)

    def on_function_changed(self, button):
        """功能选择改变事件"""
        button_id = self.function_button_group.id(button)
        self.params_stackedWidget.setCurrentIndex(button_id)

        # 更新状态栏
        function_names = ["固定时长录制", "分段录制", "截取图片"]
        self.statusbar.showMessage(f"当前选择: {function_names[button_id]}")

        # 清空之前的命令
        self.command_text.clear()
        self.copy_cmd_btn.setEnabled(False)
        self.save_script_btn.setEnabled(False)

    def on_encoding_mode_changed(self):
        """编码模式改变事件"""
        is_encode_mode = self.encode_mode_radio.isChecked()

        # 启用/禁用编码相关控件
        self.encoder_comboBox.setEnabled(is_encode_mode)
        self.preset_comboBox.setEnabled(is_encode_mode)
        self.crf_spinBox.setEnabled(is_encode_mode)
        self.audio_encoder_comboBox.setEnabled(is_encode_mode)

        # 清空之前的命令
        self.command_text.clear()
        self.copy_cmd_btn.setEnabled(False)
        self.save_script_btn.setEnabled(False)

    def on_unlimited_duration_changed(self, checked):
        """无限期录制改变事件"""
        self.duration_spinBox.setEnabled(not checked)

        # 清空之前的命令
        self.command_text.clear()
        self.copy_cmd_btn.setEnabled(False)
        self.save_script_btn.setEnabled(False)

    def select_output_directory(self):
        """选择输出目录"""
        current_dir = self.output_dir_edit.text()
        selected_dir = QFileDialog.getExistingDirectory(
            self, "选择输出目录", current_dir
        )
        if selected_dir:
            self.output_dir_edit.setText(selected_dir)

    def generate_command(self):
        """生成FFmpeg命令"""
        try:
            rtsp_url = self.rtsp_url_edit.toPlainText().strip()
            if not rtsp_url:
                QMessageBox.warning(self, "警告", "请先提供RTSP URL！")
                return

            # 获取当前选择的功能
            function_id = self.params_stackedWidget.currentIndex()

            if function_id == 0:
                # 固定时长录制
                command = self.generate_fixed_duration_command(rtsp_url)
            elif function_id == 1:
                # 分段录制
                command = self.generate_segment_command(rtsp_url)
            elif function_id == 2:
                # 截取图片
                command = self.generate_capture_command(rtsp_url)
            else:
                QMessageBox.warning(self, "错误", "未知的功能选择！")
                return

            # 显示生成的命令
            self.generated_command = command
            self.command_text.setText(command)

            # 启用复制和保存按钮
            self.copy_cmd_btn.setEnabled(True)
            self.save_script_btn.setEnabled(True)

            self.statusbar.showMessage("FFmpeg命令生成成功")

        except Exception as e:
            error_msg = f"生成命令失败: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def generate_fixed_duration_command(self, rtsp_url):
        """生成固定时长录制命令"""
        output_file = self.output_file_edit.text().strip()
        transport = self.transport_comboBox.currentText().lower()
        copy_mode = self.copy_mode_radio.isChecked()
        unlimited = self.unlimited_duration_checkBox.isChecked()

        if not output_file:
            output_file = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

        # 构建命令
        cmd_parts = ["ffmpeg"]

        # 添加传输协议
        cmd_parts.extend(["-rtsp_transport", transport])

        # 添加输入源
        cmd_parts.extend(["-i", f'"{rtsp_url}"'])

        # 添加录制时长（如果不是无限期）
        if not unlimited:
            duration = self.duration_spinBox.value()
            cmd_parts.extend(["-t", str(duration)])

        # 添加编码选项
        if copy_mode:
            cmd_parts.append("-c copy")
        else:
            # 获取编码器设置
            video_encoder = self.encoder_comboBox.currentData()
            preset = self.preset_comboBox.currentData()
            crf = self.crf_spinBox.value()
            audio_encoder = self.audio_encoder_comboBox.currentData()

            # 视频编码器
            cmd_parts.extend(["-c:v", video_encoder])

            # 添加预设（仅对某些编码器有效）
            if video_encoder in ["libx264", "libx265"]:
                cmd_parts.extend(["-preset", preset])
                cmd_parts.extend(["-crf", str(crf)])
            elif "nvenc" in video_encoder:
                cmd_parts.extend(["-preset", preset])
                cmd_parts.extend(["-cq", str(crf)])
            elif "qsv" in video_encoder:
                cmd_parts.extend(["-preset", preset])

            # 音频编码器
            if audio_encoder == "none":
                cmd_parts.append("-an")  # 禁用音频
            else:
                cmd_parts.extend(["-c:a", audio_encoder])

        # 添加输出文件
        cmd_parts.append(f'"{output_file}"')

        return " ".join(cmd_parts)

    def generate_segment_command(self, rtsp_url):
        """生成分段录制命令"""
        segment_time = self.segment_time_spinBox.value()
        output_dir = self.output_dir_edit.text().strip()
        transport = self.transport_comboBox.currentText().lower()
        copy_mode = self.copy_mode_radio.isChecked()
        use_wallclock = self.wallclock_checkBox.isChecked()

        if not output_dir:
            output_dir = "./ffmpeg_recordings/"

        # 确保输出目录以/结尾
        if not output_dir.endswith("/") and not output_dir.endswith("\\"):
            output_dir += "/"

        # 构建命令
        cmd_parts = ["ffmpeg"]

        # 添加时间戳选项
        if use_wallclock:
            cmd_parts.extend(["-use_wallclock_as_timestamps", "1"])

        # 添加传输协议
        cmd_parts.extend(["-rtsp_transport", transport])

        # 添加输入源
        cmd_parts.extend(["-i", f'"{rtsp_url}"'])

        # 添加编码选项
        if copy_mode:
            cmd_parts.extend(["-vcodec", "copy", "-acodec", "copy"])
        else:
            # 获取编码器设置
            video_encoder = self.encoder_comboBox.currentData()
            preset = self.preset_comboBox.currentData()
            crf = self.crf_spinBox.value()
            audio_encoder = self.audio_encoder_comboBox.currentData()

            # 视频编码器
            cmd_parts.extend(["-vcodec", video_encoder])

            # 添加预设
            if video_encoder in ["libx264", "libx265"]:
                cmd_parts.extend(["-preset", preset])
                cmd_parts.extend(["-crf", str(crf)])
            elif "nvenc" in video_encoder:
                cmd_parts.extend(["-preset", preset])
                cmd_parts.extend(["-cq", str(crf)])

            # 音频编码器
            if audio_encoder == "none":
                cmd_parts.append("-an")
            else:
                cmd_parts.extend(["-acodec", audio_encoder])

        # 添加分段选项
        cmd_parts.extend(["-f", "segment"])
        cmd_parts.extend(["-reset_timestamps", "1"])
        cmd_parts.extend(["-segment_atclocktime", "1"])
        cmd_parts.extend(["-segment_time", str(segment_time)])
        cmd_parts.extend(["-strftime", "1"])

        # 添加输出文件模式
        output_pattern = f'"{output_dir}%Y%m%d%H%M.mp4"'
        cmd_parts.append(output_pattern)

        return " ".join(cmd_parts)

    def generate_capture_command(self, rtsp_url):
        """生成截图命令"""
        capture_time = self.capture_time_edit.text().strip()
        image_file = self.image_file_edit.text().strip()
        transport = self.transport_comboBox.currentText().lower()

        if not capture_time:
            capture_time = "00:00:05"

        if not image_file:
            image_file = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

        # 构建命令
        cmd_parts = ["ffmpeg"]

        # 添加传输协议
        cmd_parts.extend(["-rtsp_transport", transport])

        # 添加输入源
        cmd_parts.extend(["-i", f'"{rtsp_url}"'])

        # 添加截取时间点
        cmd_parts.extend(["-ss", capture_time])

        # 添加截取帧数
        cmd_parts.extend(["-frames:v", "1"])

        # 添加输出文件
        cmd_parts.append(f'"{image_file}"')

        return " ".join(cmd_parts)

    def copy_command(self):
        """复制命令到剪贴板"""
        try:
            if not self.generated_command:
                QMessageBox.warning(self, "警告", "请先生成命令！")
                return

            clipboard = QApplication.clipboard()
            clipboard.setText(self.generated_command)

            self.statusbar.showMessage("命令已复制到剪贴板")
            QMessageBox.information(self, "复制成功", "FFmpeg命令已复制到剪贴板")

        except Exception as e:
            error_msg = f"复制命令失败: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def save_script(self):
        """保存为脚本文件"""
        try:
            if not self.generated_command:
                QMessageBox.warning(self, "警告", "请先生成命令！")
                return

            # 根据系统选择默认扩展名
            if sys.platform.startswith("win"):
                default_name = (
                    f"ffmpeg_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bat"
                )
                file_filter = "批处理文件 (*.bat);;所有文件 (*.*)"
            else:
                default_name = (
                    f"ffmpeg_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sh"
                )
                file_filter = "Shell脚本 (*.sh);;所有文件 (*.*)"

            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存FFmpeg脚本", default_name, file_filter
            )

            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    if sys.platform.startswith("win"):
                        # Windows批处理文件
                        f.write("@echo off\n")
                        f.write("echo 开始执行FFmpeg命令...\n")
                        f.write(f"{self.generated_command}\n")
                        f.write("echo 执行完成！\n")
                        f.write("pause\n")
                    else:
                        # Linux/Mac Shell脚本
                        f.write("#!/bin/bash\n")
                        f.write("echo '开始执行FFmpeg命令...'\n")
                        f.write(f"{self.generated_command}\n")
                        f.write("echo '执行完成！'\n")

                self.statusbar.showMessage(f"脚本已保存: {file_path}")
                QMessageBox.information(
                    self, "保存成功", f"FFmpeg脚本已保存到:\n{file_path}"
                )

        except Exception as e:
            error_msg = f"保存脚本失败: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def set_rtsp_url(self, url):
        """设置RTSP URL"""
        self.rtsp_url_edit.setText(url)
        self.setup_default_values()  # 重新设置默认值
