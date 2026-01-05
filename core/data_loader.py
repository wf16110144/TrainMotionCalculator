# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
# ... 后续代码不变
# # core/data_loader.py
import pandas as pd

class ExcelDataLoader:
    """Excel数据加载器：读取分段数据、默认参数"""
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.segment_data = None  # 分段速度-加速度数据
        self.default_params = None  # 默认参数
        self.load_all_data()

    def load_segment_data(self):
        """加载speed工作表：分段速度-加速度数据"""
        df = pd.read_excel(
            self.excel_path,
            sheet_name="speed",
            usecols="A:C",
            header=0,
            dtype={"speed_low_kmh": float, "speed_high_kmh": float, "acc_cm_s2": float}
        )
        df.columns = ["speed_low_kmh", "speed_high_kmh", "acc_cm_s2"]
        df = df.dropna().sort_values("speed_low_kmh").reset_index(drop=True)
        
        # 数据校验
        if df.empty:
            raise ValueError("speed工作表无有效数据")
        if (df["speed_low_kmh"] >= df["speed_high_kmh"]).any():
            raise ValueError("存在速度下限≥上限的分段")
        return df

    def load_default_params(self):
        """加载config工作表：默认参数"""
        df = pd.read_excel(
            self.excel_path,
            sheet_name="config",
            usecols="A:B",
            header=0,
            dtype={"param_name": str, "param_value": float}
        )
        df.columns = ["param_name", "param_value"]
        df = df.dropna()
        param_dict = dict(zip(df["param_name"], df["param_value"]))
        
        # 必须参数（可扩展）
        required_params = [
            "init_speed_kmh", "target_speed_kmh",  # 加速参数
            "constant_speed_kmh", "constant_time_s",  # 匀速参数
            "decel_acc_cm_s2", "coast_speed_kmh",    # 减速/滑行参数
            "traction_switch_delay_s", "brake_build_time_s"  # 牵引切换、制动建立时间
        ]
        missing = [p for p in required_params if p not in param_dict]
        if missing:
            raise ValueError(f"缺少必要参数：{','.join(missing)}")
        return param_dict

    def load_all_data(self):
        """一次性加载所有数据"""
        self.segment_data = self.load_segment_data()
        self.default_params = self.load_default_params()