# -*- coding: utf-8 -*-
import os
import subprocess

def build_exe():
    """打包成EXE文件（适配VS自带Python环境）"""
    # VS自带Python的完整路径（根据你的环境修改）
    python_path = r"C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python39_64\python.exe"
    
    # 打包命令（通过-m参数调用pyinstaller，无需配置PATH）
    cmd = [
        python_path,
        "-m", "PyInstaller",  # 核心修改：用Python解释器调用pyinstaller
        "--onefile",
        "--windowed",
        "--name", "列车运动计算工具",
        # 注释掉图标（可选：有ico文件再取消注释）
        # "--icon", "icon.ico",
        "--add-data", "core;core",
        "--add-data", "ui;ui",
        "--add-data", "speed_data.xlsx;.",
        "--hidden-import", "pandas",
        "--hidden-import", "openpyxl",
        "--hidden-import", "matplotlib",
        "--hidden-import", "tkinter",
        "main.py"
    ]
    
    try:
        # 执行打包命令
        subprocess.run(cmd, check=True, shell=True)
        print("="*50)
        print("打包成功！EXE文件在dist目录下")
        print("="*50)
    except subprocess.CalledProcessError as e:
        print(f"打包失败：{e}")
        print("请检查：1.文件路径是否正确 2.依赖库是否安装 3.无中文/空格路径")

if __name__ == "__main__":
    build_exe()