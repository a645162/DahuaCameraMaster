#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
大华摄像机管理器 - 主启动文件
DahuaCameraMaster - Main Entry Point

这是应用程序的外部启动入口，用于启动src目录中的内部main模块。
This is the external entry point that launches the internal main module in src directory.
"""

import sys
import os


def main():
    """启动应用程序的主函数"""
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(current_dir, "src")

        # 检查src目录是否存在
        if not os.path.exists(src_dir):
            print("错误：找不到src目录")
            print("Error: src directory not found")
            return 1

        # 检查内部main.py是否存在
        internal_main = os.path.join(src_dir, "main.py")
        if not os.path.exists(internal_main):
            print("错误：找不到src/main.py文件")
            print("Error: src/main.py not found")
            return 1

        # 添加src目录到Python路径
        sys.path.insert(0, src_dir)
        sys.path.insert(0, current_dir)

        # 导入并运行内部main模块
        from src import main as internal_main

        return internal_main.main()

    except ImportError as e:
        print(f"导入错误：{e}")
        print(f"Import Error: {e}")
        print("请确保所有依赖项已正确安装")
        print("Please ensure all dependencies are properly installed")
        return 1
    except Exception as e:
        print(f"运行错误：{e}")
        print(f"Runtime Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
