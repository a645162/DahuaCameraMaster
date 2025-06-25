
from PySide6 import QtCore, QtWidgets


class Ui_InitDeviceDialog:
    def setupUi(self, InitDeviceDialog):
        InitDeviceDialog.setObjectName("InitDeviceDialog")
        InitDeviceDialog.resize(450, 320)
        InitDeviceDialog.setFixedSize(450, 320)

        # 主布局
        self.main_layout = QtWidgets.QVBoxLayout(InitDeviceDialog)

        # 设备信息显示
        self.info_groupBox = QtWidgets.QGroupBox("设备信息(Device Information)")
        self.info_layout = QtWidgets.QGridLayout(self.info_groupBox)

        self.ip_label = QtWidgets.QLabel("IP地址:")
        self.info_layout.addWidget(self.ip_label, 0, 0)
        self.ip_value_label = QtWidgets.QLabel()
        self.ip_value_label.setStyleSheet("font-weight: bold;")
        self.info_layout.addWidget(self.ip_value_label, 0, 1)

        self.mac_label = QtWidgets.QLabel("MAC地址:")
        self.info_layout.addWidget(self.mac_label, 1, 0)
        self.mac_value_label = QtWidgets.QLabel()
        self.mac_value_label.setStyleSheet("font-weight: bold;")
        self.info_layout.addWidget(self.mac_value_label, 1, 1)

        self.main_layout.addWidget(self.info_groupBox)

        # 账号设置
        self.account_groupBox = QtWidgets.QGroupBox("账号设置(Account Settings)")
        self.account_layout = QtWidgets.QGridLayout(self.account_groupBox)

        self.username_label = QtWidgets.QLabel("用户名(Username):")
        self.account_layout.addWidget(self.username_label, 0, 0)
        self.username_lineEdit = QtWidgets.QLineEdit()
        self.username_lineEdit.setPlaceholderText("请输入用户名")
        self.account_layout.addWidget(self.username_lineEdit, 0, 1)

        self.password_label = QtWidgets.QLabel("密码(Password):")
        self.account_layout.addWidget(self.password_label, 1, 0)
        self.password_lineEdit = QtWidgets.QLineEdit()
        self.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.password_lineEdit.setPlaceholderText("请输入密码")
        self.account_layout.addWidget(self.password_lineEdit, 1, 1)

        self.confirm_password_label = QtWidgets.QLabel("确认密码(Confirm Password):")
        self.account_layout.addWidget(self.confirm_password_label, 2, 0)
        self.confirm_password_lineEdit = QtWidgets.QLineEdit()
        self.confirm_password_lineEdit.setEchoMode(
            QtWidgets.QLineEdit.EchoMode.Password
        )
        self.confirm_password_lineEdit.setPlaceholderText("请再次输入密码")
        self.account_layout.addWidget(self.confirm_password_lineEdit, 2, 1)

        self.main_layout.addWidget(self.account_groupBox)

        # 重置方式
        self.reset_groupBox = QtWidgets.QGroupBox("重置方式(Reset Method)")
        self.reset_layout = QtWidgets.QGridLayout(self.reset_groupBox)

        self.reset_method_label = QtWidgets.QLabel("重置方式(Reset Way):")
        self.reset_layout.addWidget(self.reset_method_label, 0, 0)
        self.reset_method_lineEdit = QtWidgets.QLineEdit()
        self.reset_method_lineEdit.setEnabled(False)
        self.reset_layout.addWidget(self.reset_method_lineEdit, 0, 1)

        self.reset_value_label = QtWidgets.QLabel("重置信息:")
        self.reset_layout.addWidget(self.reset_value_label, 1, 0)
        self.reset_value_lineEdit = QtWidgets.QLineEdit()
        self.reset_value_lineEdit.setPlaceholderText("请输入手机号或邮箱")
        self.reset_layout.addWidget(self.reset_value_lineEdit, 1, 1)

        self.main_layout.addWidget(self.reset_groupBox)

        # 按钮区域
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch()

        self.cancel_button = QtWidgets.QPushButton("取消(Cancel)")
        self.cancel_button.setMinimumSize(QtCore.QSize(100, 35))
        self.button_layout.addWidget(self.cancel_button)

        self.ok_button = QtWidgets.QPushButton("确定(OK)")
        self.ok_button.setMinimumSize(QtCore.QSize(100, 35))
        self.ok_button.setDefault(True)
        self.button_layout.addWidget(self.ok_button)

        self.main_layout.addLayout(self.button_layout)

        self.retranslateUi(InitDeviceDialog)

        # 连接信号槽
        self.ok_button.clicked.connect(InitDeviceDialog.accept)
        self.cancel_button.clicked.connect(InitDeviceDialog.reject)

        QtCore.QMetaObject.connectSlotsByName(InitDeviceDialog)

    def retranslateUi(self, InitDeviceDialog):
        _translate = QtCore.QCoreApplication.translate
        InitDeviceDialog.setWindowTitle(
            _translate("InitDeviceDialog", "设备初始化(Device Initialization)")
        )
