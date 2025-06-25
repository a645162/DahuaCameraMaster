
from PySide6 import QtCore, QtWidgets


class Ui_IPConfigWindow:
    def setupUi(self, IPConfigWindow):
        IPConfigWindow.setObjectName("IPConfigWindow")
        IPConfigWindow.resize(420, 480)
        IPConfigWindow.setMinimumSize(QtCore.QSize(400, 450))
        # 移除最大尺寸限制，允许最大化

        self.centralwidget = QtWidgets.QWidget(IPConfigWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 主垂直布局
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(12)

        # 标题
        self.title_label = QtWidgets.QLabel("网卡IP配置工具")
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #2c3e50; padding: 8px;"
        )
        self.title_label.setMaximumHeight(35)
        self.main_layout.addWidget(self.title_label)

        # 网卡选择区域
        self.adapter_groupBox = QtWidgets.QGroupBox("网卡选择")
        self.adapter_groupBox.setMaximumHeight(80)
        self.adapter_layout = QtWidgets.QHBoxLayout(self.adapter_groupBox)
        self.adapter_layout.setSpacing(8)

        self.adapter_comboBox = QtWidgets.QComboBox()
        self.adapter_comboBox.setMinimumHeight(28)
        self.adapter_layout.addWidget(self.adapter_comboBox)

        self.refresh_adapter_button = QtWidgets.QPushButton("刷新")
        self.refresh_adapter_button.setFixedSize(60, 28)
        self.adapter_layout.addWidget(self.refresh_adapter_button)

        self.main_layout.addWidget(self.adapter_groupBox)

        # IP配置区域
        self.config_groupBox = QtWidgets.QGroupBox("IP配置")
        self.config_groupBox.setMaximumHeight(150)
        self.config_layout = QtWidgets.QFormLayout(self.config_groupBox)
        self.config_layout.setSpacing(8)
        self.config_layout.setHorizontalSpacing(10)

        # IP地址
        self.ip_label = QtWidgets.QLabel("IP地址:")
        self.ip_label.setFixedWidth(80)
        self.ip_lineEdit = QtWidgets.QLineEdit()
        self.ip_lineEdit.setPlaceholderText("192.168.1.100")
        self.ip_lineEdit.setFixedHeight(26)
        self.config_layout.addRow(self.ip_label, self.ip_lineEdit)

        # 子网掩码
        self.subnet_label = QtWidgets.QLabel("子网掩码:")
        self.subnet_label.setFixedWidth(80)
        self.subnet_lineEdit = QtWidgets.QLineEdit()
        self.subnet_lineEdit.setText("255.255.255.0")
        self.subnet_lineEdit.setFixedHeight(26)
        self.config_layout.addRow(self.subnet_label, self.subnet_lineEdit)

        # 网关
        self.gateway_label = QtWidgets.QLabel("默认网关:")
        self.gateway_label.setFixedWidth(80)
        self.gateway_lineEdit = QtWidgets.QLineEdit()
        self.gateway_lineEdit.setText("192.168.1.1")
        self.gateway_lineEdit.setFixedHeight(26)
        self.config_layout.addRow(self.gateway_label, self.gateway_lineEdit)

        # DNS
        self.dns_label = QtWidgets.QLabel("DNS服务器:")
        self.dns_label.setFixedWidth(80)
        self.dns_lineEdit = QtWidgets.QLineEdit()
        self.dns_lineEdit.setText("192.168.1.1")
        self.dns_lineEdit.setFixedHeight(26)
        self.config_layout.addRow(self.dns_label, self.dns_lineEdit)

        self.main_layout.addWidget(self.config_groupBox)

        # 快速设置区域
        self.quick_groupBox = QtWidgets.QGroupBox("快速设置")
        self.quick_groupBox.setMaximumHeight(60)
        self.quick_layout = QtWidgets.QHBoxLayout(self.quick_groupBox)
        self.quick_layout.setSpacing(8)

        self.auto_ip_button = QtWidgets.QPushButton("自动分配IP (192.168.1.x)")
        self.auto_ip_button.setFixedHeight(30)
        self.auto_ip_button.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; border: none; border-radius: 3px; } QPushButton:hover { background-color: #2980b9; }"
        )
        self.quick_layout.addWidget(self.auto_ip_button)

        self.main_layout.addWidget(self.quick_groupBox)

        # 添加弹性空间
        self.main_layout.addStretch()

        # 按钮区域
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setSpacing(8)

        self.apply_button = QtWidgets.QPushButton("应用配置")
        self.apply_button.setFixedHeight(35)
        self.apply_button.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; border: none; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #229954; }"
        )
        self.button_layout.addWidget(self.apply_button)

        self.dhcp_button = QtWidgets.QPushButton("恢复DHCP")
        self.dhcp_button.setFixedHeight(35)
        self.dhcp_button.setStyleSheet(
            "QPushButton { background-color: #f39c12; color: white; border: none; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #e67e22; }"
        )
        self.button_layout.addWidget(self.dhcp_button)

        self.cancel_button = QtWidgets.QPushButton("取消")
        self.cancel_button.setFixedHeight(35)
        self.cancel_button.setStyleSheet(
            "QPushButton { background-color: #95a5a6; color: white; border: none; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #7f8c8d; }"
        )
        self.button_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(self.button_layout)

        # 状态显示区域
        self.status_label = QtWidgets.QLabel("就绪")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFixedHeight(25)
        self.status_label.setStyleSheet(
            "color: #7f8c8d; font-style: italic; font-size: 11px; padding: 3px;"
        )
        self.main_layout.addWidget(self.status_label)

        IPConfigWindow.setCentralWidget(self.centralwidget)

        # 状态栏
        self.statusbar = QtWidgets.QStatusBar(IPConfigWindow)
        IPConfigWindow.setStatusBar(self.statusbar)

        self.retranslateUi(IPConfigWindow)
        QtCore.QMetaObject.connectSlotsByName(IPConfigWindow)

    def retranslateUi(self, IPConfigWindow):
        _translate = QtCore.QCoreApplication.translate
        IPConfigWindow.setWindowTitle(_translate("IPConfigWindow", "网卡IP配置工具"))
