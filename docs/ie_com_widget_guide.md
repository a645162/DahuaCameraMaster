# IE COM组件使用指南

## 概述

`IEComWidget` 是一个完全独立的IE WebBrowser COM组件封装类，提供了丰富的浏览器功能和事件处理。

## 主要特性

### 基本功能

- 网页导航（navigate）
- 页面刷新（refresh）
- 停止加载（stop）
- 前进/后退（go_forward/go_back）
- 跳转到主页（go_home）

### 脚本执行

- 执行JavaScript代码（execute_script）
- 获取文档对象（get_document）
- 元素操作（get_element_by_id, set_element_value, click_element）

### 事件监听

- 导航开始/完成/错误
- 文档就绪
- 进度变化
- 状态变化
- 标题变化

## 基本使用

### 1. 创建IE COM组件

```python
from dahua_camera_master.browser.ie_com_widget import IEComWidget

# 创建组件
ie_widget = IEComWidget()

# 添加到布局
layout.addWidget(ie_widget)
```

### 2. 导航到网页

```python
# 基本导航
success = ie_widget.navigate("http://192.168.1.1")

# 检查导航状态
print(f"当前URL: {ie_widget.current_url}")
print(f"当前状态: {ie_widget.state}")
```

### 3. 连接事件信号

```python
# 连接信号
ie_widget.navigation_started.connect(on_navigation_started)
ie_widget.navigation_completed.connect(on_navigation_completed)
ie_widget.navigation_error.connect(on_navigation_error)
ie_widget.document_ready.connect(on_document_ready)
ie_widget.progress_changed.connect(on_progress_changed)
ie_widget.status_changed.connect(on_status_changed)
ie_widget.title_changed.connect(on_title_changed)

# 事件处理函数
def on_navigation_started(url):
    print(f"开始导航: {url}")

def on_navigation_completed(url):
    print(f"导航完成: {url}")

def on_navigation_error(url, error):
    print(f"导航错误: {url} - {error}")
```

### 4. 执行JavaScript

```python
# 执行脚本
script = "document.getElementById('username').value = 'admin';"
result = ie_widget.execute_script(script)

# 元素操作
ie_widget.set_element_value("username", "admin")
ie_widget.set_element_value("password", "password123")
ie_widget.click_element("login_button")
```

### 5. 浏览器控制

```python
# 刷新页面
ie_widget.refresh()

# 停止加载
ie_widget.stop()

# 前进后退
if ie_widget.can_go_back:
    ie_widget.go_back()

ie_widget.go_forward()

# 跳转主页
ie_widget.go_home()
```

## 完整示例

参考 `examples/ie_com_example.py` 查看完整的使用示例。

## 注意事项

1. **依赖要求**: 需要系统安装IE浏览器
2. **权限问题**: 某些操作可能需要管理员权限
3. **错误处理**: 组件内置错误抑制和异常处理
4. **资源清理**: 使用完毕后调用 `cleanup()` 方法清理资源

## API参考

### 导航方法

- `navigate(url: str) -> bool` - 导航到指定URL
- `refresh() -> bool` - 刷新当前页面
- `stop() -> bool` - 停止加载
- `go_back() -> bool` - 后退
- `go_forward() -> bool` - 前进
- `go_home() -> bool` - 跳转到主页

### 脚本方法

- `execute_script(script: str) -> Any` - 执行JavaScript
- `get_document() -> Any` - 获取文档对象
- `get_element_by_id(element_id: str) -> Any` - 获取元素
- `set_element_value(element_id: str, value: str) -> bool` - 设置元素值
- `click_element(element_id: str) -> bool` - 点击元素

### 属性

- `current_url: str` - 当前URL
- `state: NavigationState` - 当前状态
- `title: str` - 页面标题
- `can_go_back: bool` - 是否可以后退
- `can_go_forward: bool` - 是否可以前进

### 信号

- `navigation_started(str)` - 导航开始
- `navigation_completed(str)` - 导航完成
- `navigation_error(str, str)` - 导航错误
- `document_ready()` - 文档就绪
- `progress_changed(int)` - 进度变化
- `status_changed(str)` - 状态变化
- `title_changed(str)` - 标题变化
