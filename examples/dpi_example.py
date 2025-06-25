"""
DPI工具使用示例
演示如何在应用程序中使用DPI相关功能
"""

from dahua_camera_master.utils.dpi_utils import (
    configure_application_dpi,
    get_dpi_manager,
    get_system_dpi,
    get_dpi_scale_factor,
    DPIManager,
)


def example_basic_dpi_setup():
    """基本DPI设置示例"""
    print("=== 基本DPI设置示例 ===")

    # 方法1: 使用便捷函数
    configure_application_dpi()

    print(f"系统DPI: {get_system_dpi()}")
    print(f"缩放因子: {get_dpi_scale_factor()}")


def example_dpi_manager():
    """DPI管理器使用示例"""
    print("\n=== DPI管理器使用示例 ===")

    # 获取全局DPI管理器
    dpi_manager = get_dpi_manager()

    # 配置DPI设置
    dpi_manager.configure(force_100_percent=True)

    # 获取状态信息
    status = dpi_manager.get_status()
    print("DPI状态信息:")
    for key, value in status.items():
        print(f"  {key}: {value}")


def example_custom_dpi_manager():
    """自定义DPI管理器示例"""
    print("\n=== 自定义DPI管理器示例 ===")

    # 创建新的DPI管理器实例
    custom_manager = DPIManager()

    # 配置为不强制100%缩放
    custom_manager.configure(force_100_percent=False)

    status = custom_manager.get_status()
    print("自定义DPI管理器状态:")
    for key, value in status.items():
        print(f"  {key}: {value}")


def example_qt_application():
    """Qt应用程序DPI设置示例"""
    print("\n=== Qt应用程序DPI设置示例 ===")

    # 这是在创建QApplication之前应该做的事情
    from dahua_camera_master.utils.dpi_utils import (
        setup_qt_dpi_settings,
        set_dpi_awareness,
    )

    # 1. 设置Qt环境变量
    setup_qt_dpi_settings()
    print("Qt DPI环境变量已设置")

    # 2. 设置系统DPI感知
    set_dpi_awareness()
    print("系统DPI感知已设置")

    # 3. 现在可以创建QApplication
    print("现在可以安全地创建QApplication了")


if __name__ == "__main__":
    # 运行所有示例
    example_basic_dpi_setup()
    example_dpi_manager()
    example_custom_dpi_manager()
    example_qt_application()

    print("\n=== DPI工具使用示例完成 ===")
