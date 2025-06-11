# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QFrame,
)
from PySide6.QtCore import Qt, QTimer, Signal


class AspectRatioVideoWidget(QWidget):
    """支持比例控制的视频显示组件"""

    # 比例模式改变信号
    aspect_mode_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.aspect_mode = 0  # 0: 16:9, 1: 自适应
        self.min_width = 640
        self.min_height = 360
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        self.setObjectName("AspectRatioVideoWidget")

        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)

        # 控制区域
        self.control_frame = QFrame()
        self.control_frame.setMaximumHeight(35)
        self.control_layout = QHBoxLayout(self.control_frame)
        self.control_layout.setContentsMargins(5, 5, 5, 5)

        # 比例选择
        self.aspect_label = QLabel("画面比例:")
        self.control_layout.addWidget(self.aspect_label)

        self.aspect_combo = QComboBox()
        self.aspect_combo.addItem("16:9 固定比例")
        self.aspect_combo.addItem("自适应(Auto)")
        self.aspect_combo.setMaximumWidth(150)
        self.aspect_combo.currentIndexChanged.connect(self.on_aspect_changed)
        self.control_layout.addWidget(self.aspect_combo)

        self.control_layout.addStretch()

        # 尺寸显示
        self.size_label = QLabel("控件尺寸: --")
        self.size_label.setStyleSheet("color: gray; font-size: 11px;")
        self.control_layout.addWidget(self.size_label)

        self.main_layout.addWidget(self.control_frame)

        # 视频显示容器
        self.video_container = QFrame()
        self.video_container.setStyleSheet("background-color: rgb(64, 64, 64);")
        self.video_container_layout = QHBoxLayout(self.video_container)
        self.video_container_layout.setContentsMargins(0, 0, 0, 0)

        # 视频显示控件
        self.video_widget = QLabel()
        self.video_widget.setStyleSheet("background-color: rgb(180, 180, 180);")
        self.video_widget.setAlignment(Qt.AlignCenter)
        self.video_widget.setText("视频显示区域")
        self.video_widget.setMinimumSize(self.min_width, self.min_height)

        self.video_container_layout.addWidget(self.video_widget)
        self.main_layout.addWidget(self.video_container)

        # 设置初始比例
        self.apply_aspect_ratio()

    def on_aspect_changed(self, index):
        """比例模式改变"""
        self.aspect_mode = index
        self.apply_aspect_ratio()
        self.aspect_mode_changed.emit(index)

    def apply_aspect_ratio(self):
        """应用比例设置"""
        if self.aspect_mode == 0:
            # 16:9 固定比例模式
            self.set_16_9_mode()
        else:
            # 自适应模式
            self.set_adaptive_mode()

    def set_16_9_mode(self):
        """设置16:9固定比例模式"""
        # 获取容器可用空间
        container_size = self.video_container.size()
        available_width = max(container_size.width() - 20, self.min_width)
        available_height = max(container_size.height() - 20, self.min_height)

        # 计算16:9比例下的最佳尺寸
        width_by_height = int(available_height * 16 / 9)
        height_by_width = int(available_width * 9 / 16)

        if width_by_height <= available_width:
            # 以高度为准
            target_width = width_by_height
            target_height = available_height
        else:
            # 以宽度为准
            target_width = available_width
            target_height = height_by_width

        # 确保最小尺寸
        if target_width < self.min_width:
            target_width = self.min_width
            target_height = int(self.min_width * 9 / 16)
        if target_height < self.min_height:
            target_height = self.min_height
            target_width = int(self.min_height * 16 / 9)

        # 设置固定尺寸
        self.video_widget.setFixedSize(target_width, target_height)
        self.size_label.setText(f"控件尺寸: {target_width}x{target_height} (16:9)")

        print(f"16:9模式 - 设置视频控件尺寸: {target_width}x{target_height}")

    def set_adaptive_mode(self):
        """设置自适应模式"""
        # 移除固定尺寸限制
        self.video_widget.setMinimumSize(self.min_width, self.min_height)
        self.video_widget.setMaximumSize(16777215, 16777215)  # Qt的最大尺寸

        # 更新尺寸显示
        current_size = self.video_widget.size()
        if current_size.width() > 0 and current_size.height() > 0:
            ratio = current_size.width() / current_size.height()
            self.size_label.setText(
                f"控件尺寸: {current_size.width()}x{current_size.height()} (比例: {ratio:.2f}:1)"
            )
        else:
            self.size_label.setText("控件尺寸: 自适应模式")

        print(f"自适应模式 - 视频控件尺寸跟随容器")

    def resizeEvent(self, event):
        """尺寸改变事件"""
        super().resizeEvent(event)

        # 延迟重新计算比例，确保布局完成
        if self.aspect_mode == 0:  # 16:9模式
            QTimer.singleShot(10, self.set_16_9_mode)
        else:  # 自适应模式
            QTimer.singleShot(10, self.update_adaptive_size_display)

    def update_adaptive_size_display(self):
        """更新自适应模式的尺寸显示"""
        if self.aspect_mode == 1:
            current_size = self.video_widget.size()
            if current_size.width() > 0 and current_size.height() > 0:
                ratio = current_size.width() / current_size.height()
                self.size_label.setText(
                    f"控件尺寸: {current_size.width()}x{current_size.height()} (比例: {ratio:.2f}:1)"
                )

    def get_video_widget(self):
        """获取视频显示控件"""
        return self.video_widget

    def get_aspect_mode(self):
        """获取当前比例模式"""
        return self.aspect_mode

    def set_aspect_mode(self, mode):
        """设置比例模式"""
        self.aspect_combo.setCurrentIndex(mode)

    def set_minimum_video_size(self, width, height):
        """设置视频控件的最小尺寸"""
        self.min_width = width
        self.min_height = height
        self.video_widget.setMinimumSize(width, height)
        if self.aspect_mode == 0:
            self.apply_aspect_ratio()
