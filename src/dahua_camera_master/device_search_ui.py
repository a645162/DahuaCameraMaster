
from PySide6 import QtCore, QtWidgets


class Ui_DeviceSearchWindow:
    def setupUi(self, DeviceSearchWindow):
        DeviceSearchWindow.setObjectName("DeviceSearchWindow")
        DeviceSearchWindow.resize(900, 700)
        DeviceSearchWindow.setMinimumSize(QtCore.QSize(800, 600))

        self.centralwidget = QtWidgets.QWidget(DeviceSearchWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 主垂直布局
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setObjectName("main_layout")

        # 设备列表区域
        self.devicelist_groupBox = QtWidgets.QGroupBox("设备列表(Device List)")
        self.devicelist_groupBox.setMinimumHeight(350)

        self.devicelist_layout = QtWidgets.QVBoxLayout(self.devicelist_groupBox)

        # 设备表格
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setColumnCount(12)
        self.tableWidget.setRowCount(0)

        # 设置表头
        headers = [
            "序号(No.)",
            "状态(Status)",
            "IP版本(IP Version)",
            "IP地址(IP Address)",
            "端口(Port)",
            "子网掩码(Subnet Mask)",
            "网关(Gateway)",
            "物理地址(Mac Address)",
            "设备类型(Device Type)",
            "详细类型(Detail Type)",
            "Http(Http)",
            "操作(Action)",
        ]

        for i, header in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(header)
            self.tableWidget.setHorizontalHeaderItem(i, item)

        self.tableWidget.horizontalHeader().setDefaultSectionSize(120)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(80)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tableWidget.setAlternatingRowColors(True)

        self.devicelist_layout.addWidget(self.tableWidget)
        self.main_layout.addWidget(self.devicelist_groupBox)

        # 控制区域水平布局
        self.control_layout = QtWidgets.QHBoxLayout()

        # 搜索设备区域
        self.search_groupBox = QtWidgets.QGroupBox("搜索设备(Search Devices)")
        self.search_groupBox.setMaximumWidth(350)

        self.search_layout = QtWidgets.QVBoxLayout(self.search_groupBox)

        # 组播和广播搜索按钮
        self.SearchDeviceButton = QtWidgets.QPushButton(
            "组播和广播搜索(Multicast and Broadcast)"
        )
        self.SearchDeviceButton.setMinimumHeight(40)
        self.search_layout.addWidget(self.SearchDeviceButton)

        # 搜索时间设置
        self.time_layout = QtWidgets.QHBoxLayout()
        self.Searchtime_label = QtWidgets.QLabel("搜索时间ms(Time:ms):")
        self.Searchtime_lineEdit = QtWidgets.QLineEdit("3000")
        self.Searchtime_lineEdit.setMaximumWidth(100)
        self.time_layout.addWidget(self.Searchtime_label)
        self.time_layout.addWidget(self.Searchtime_lineEdit)
        self.time_layout.addStretch()
        self.search_layout.addLayout(self.time_layout)

        self.control_layout.addWidget(self.search_groupBox)

        # 单播搜索区域
        self.unicast_groupBox = QtWidgets.QGroupBox("单播搜索(Unicast)")
        self.unicast_groupBox.setMaximumWidth(350)

        self.unicast_layout = QtWidgets.QVBoxLayout(self.unicast_groupBox)

        # IP范围设置
        self.ip_layout = QtWidgets.QGridLayout()

        self.StartIP_label = QtWidgets.QLabel("起始IP地址(Start IP)")
        self.ip_layout.addWidget(self.StartIP_label, 0, 0)
        self.StartIP_lineEdit = QtWidgets.QLineEdit()
        self.StartIP_lineEdit.setPlaceholderText("192.168.1.100")
        self.ip_layout.addWidget(self.StartIP_lineEdit, 0, 1)

        self.EndIP_label = QtWidgets.QLabel("结束IP地址(End IP)")
        self.ip_layout.addWidget(self.EndIP_label, 1, 0)
        self.EndIP_lineEdit = QtWidgets.QLineEdit()
        self.EndIP_lineEdit.setPlaceholderText("192.168.1.200")
        self.ip_layout.addWidget(self.EndIP_lineEdit, 1, 1)

        self.unicast_layout.addLayout(self.ip_layout)

        # 点对点搜索按钮
        self.SearchByIpButton = QtWidgets.QPushButton(
            "点对点搜索(Point to Point Search)"
        )
        self.SearchByIpButton.setMinimumHeight(40)
        self.unicast_layout.addWidget(self.SearchByIpButton)

        self.control_layout.addWidget(self.unicast_groupBox)

        # 操作区域
        self.operation_groupBox = QtWidgets.QGroupBox("操作设备(Operate Devices)")

        self.operation_layout = QtWidgets.QVBoxLayout(self.operation_groupBox)

        # 初始化按钮
        self.InitButton = QtWidgets.QPushButton("初始化设备(Initialize Device)")
        self.InitButton.setMinimumHeight(40)
        self.operation_layout.addWidget(self.InitButton)

        # 连接摄像机按钮
        self.ConnectButton = QtWidgets.QPushButton("连接摄像机(Connect Camera)")
        self.ConnectButton.setMinimumHeight(40)
        self.operation_layout.addWidget(self.ConnectButton)

        # 停止搜索按钮
        self.StopSearchButton = QtWidgets.QPushButton("停止搜索(Stop Search)")
        self.StopSearchButton.setMinimumHeight(40)
        self.operation_layout.addWidget(self.StopSearchButton)

        # IP配置按钮
        self.IPConfigButton = QtWidgets.QPushButton("网卡IP配置(Network Config)")
        self.IPConfigButton.setMinimumHeight(40)
        self.IPConfigButton.setStyleSheet(
            "QPushButton { background-color: #e74c3c; color: white; font-weight: bold; border: none; border-radius: 3px; } QPushButton:hover { background-color: #c0392b; }"
        )
        self.operation_layout.addWidget(self.IPConfigButton)

        self.control_layout.addWidget(self.operation_groupBox)

        self.main_layout.addLayout(self.control_layout)

        DeviceSearchWindow.setCentralWidget(self.centralwidget)

        # 菜单栏
        self.menubar = QtWidgets.QMenuBar(DeviceSearchWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 23))
        DeviceSearchWindow.setMenuBar(self.menubar)

        # 状态栏
        self.statusbar = QtWidgets.QStatusBar(DeviceSearchWindow)
        DeviceSearchWindow.setStatusBar(self.statusbar)

        self.retranslateUi(DeviceSearchWindow)
        QtCore.QMetaObject.connectSlotsByName(DeviceSearchWindow)

    def retranslateUi(self, DeviceSearchWindow):
        _translate = QtCore.QCoreApplication.translate
        DeviceSearchWindow.setWindowTitle(
            _translate("DeviceSearchWindow", "大华摄像机管理器 - 设备搜索")
        )
