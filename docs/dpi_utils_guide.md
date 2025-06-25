# DPI工具模块使用指南

## 概述

`dpi_utils.py` 模块提供了一套完整的DPI管理工具，专门用于处理Windows高DPI显示器下的应用程序显示问题。

## 主要功能

### 基础DPI函数

```python
from dahua_camera_master.utils.dpi_utils import (
    set_dpi_awareness,
    setup_qt_dpi_settings,
    configure_application_dpi,
)

# 快速配置（推荐）
configure_application_dpi()

# 或者分步配置
setup_qt_dpi_settings()  # 设置Qt环境变量
set_dpi_awareness()       # 设置系统DPI感知
```

### DPI信息获取

```python
from dahua_camera_master.utils.dpi_utils import (
    get_system_dpi,
    get_dpi_scale_factor,
)

dpi = get_system_dpi()           # 获取系统DPI值
scale = get_dpi_scale_factor()   # 获取缩放因子
```

### DPI管理器

```python
from dahua_camera_master.utils.dpi_utils import get_dpi_manager, DPIManager

# 使用全局管理器
manager = get_dpi_manager()
manager.configure(force_100_percent=True)
status = manager.get_status()

# 创建自定义管理器
custom_manager = DPIManager()
custom_manager.configure(force_100_percent=False)
```

### 窗口DPI设置

```python
from dahua_camera_master.utils.dpi_utils import set_window_dpi

# 为特定窗口设置DPI
hwnd = int(widget.winId())  # 获取窗口句柄
set_window_dpi(hwnd)
```

## 在Qt应用程序中使用

### 推荐的初始化顺序

```python
from PySide6.QtWidgets import QApplication
from dahua_camera_master.utils.dpi_utils import configure_application_dpi

# 1. 在创建QApplication之前配置DPI
configure_application_dpi()

# 2. 创建QApplication
app = QApplication([])

# 3. 设置额外的Qt属性（可选）
app.setAttribute(Qt.AA_DisableHighDpiScaling, True)
app.setAttribute(Qt.AA_Use96Dpi, True)
```

### 在浏览器工厂中使用

```python
from dahua_camera_master.utils.dpi_utils import configure_application_dpi

def create_browser_app(default_url: str = "192.168.1.1"):
    # 使用新的DPI配置函数
    configure_application_dpi()
    
    app = QApplication.instance() or QApplication([])
    # ... 其他代码
```

## 向后兼容性

为了保持向后兼容性，原有的导入方式仍然可用：

```python
# 这些导入方式仍然有效
from dahua_camera_master.utils import set_dpi_awareness, setup_qt_dpi_settings
from dahua_camera_master.utils.system_utils import set_dpi_awareness
```

## API参考

### configure_application_dpi()

为应用程序配置完整的DPI设置，包括Qt环境变量和系统DPI感知。

### DPIManager类

提供高级DPI管理功能：

- `configure(force_100_percent=True)`: 配置DPI设置
- `get_status()`: 获取当前DPI状态信息
- `is_configured`: 检查是否已配置

### 环境变量设置

自动设置以下Qt环境变量：

- `QT_AUTO_SCREEN_SCALE_FACTOR=0`
- `QT_SCALE_FACTOR=1`
- `QT_SCREEN_SCALE_FACTORS=1`
- `QT_DPI_OVERRIDE=96`
- `QT_DEVICE_PIXEL_RATIO=1`

## 示例

运行 `examples/dpi_example.py` 查看完整的使用示例。

## 注意事项

1. **调用时机**：DPI配置必须在创建QApplication之前调用
2. **Windows特定**：大部分功能仅在Windows平台上有效
3. **日志记录**：所有操作都会记录到日志中，便于调试
4. **错误处理**：所有函数都包含适当的错误处理，失败时不会崩溃

## 迁移指南

如果你之前使用的是 `system_utils` 中的DPI函数：

```python
# 旧代码
from dahua_camera_master.utils.system_utils import set_dpi_awareness, setup_qt_dpi_settings

# 新代码（推荐）
from dahua_camera_master.utils.dpi_utils import configure_application_dpi

# 或者保持兼容性
from dahua_camera_master.utils import set_dpi_awareness, setup_qt_dpi_settings
```
