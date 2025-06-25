"""
简单的DPI工具测试脚本
验证DPI工具模块是否正常工作
"""

import sys
import os

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "..", "src")
src_dir = os.path.abspath(src_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 现在可以导入DPI工具
from dahua_camera_master.utils.dpi_utils import (
    get_system_dpi,
    get_dpi_scale_factor,
    get_dpi_manager,
    configure_application_dpi,
)


def test_dpi_tools():
    """测试DPI工具功能"""
    print("=== DPI工具测试 ===")

    # 测试基本DPI信息获取
    print(f"系统DPI: {get_system_dpi()}")
    print(f"DPI缩放因子: {get_dpi_scale_factor()}")

    # 测试DPI管理器
    manager = get_dpi_manager()
    status = manager.get_status()
    print("DPI管理器状态:")
    for key, value in status.items():
        print(f"  {key}: {value}")

    # 测试配置功能
    print("\n配置DPI设置...")
    configure_application_dpi()

    # 再次检查状态
    new_status = manager.get_status()
    print("配置后的状态:")
    for key, value in new_status.items():
        print(f"  {key}: {value}")

    print("\n=== DPI工具测试完成 ===")


if __name__ == "__main__":
    test_dpi_tools()
