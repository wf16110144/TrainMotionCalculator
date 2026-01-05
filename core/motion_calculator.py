# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
# ... 后续代码不变
# # core/motion_calculator.py
import math

class MotionPhaseCalculator:
    """各运动阶段计算类：加速、匀速、减速、牵引切换、制动建立"""
    def __init__(self, segment_data, default_params):
        self.segment_data = segment_data  # 分段加速度数据
        self.params = default_params      # 默认参数

    # ---------------------- 1. 加速阶段 ----------------------
    def calculate_acceleration(self):
        """
        计算加速阶段：从初始速度到目标速度
        返回：阶段时间、阶段距离、速度-距离点
        """
        init_speed = self.params["init_speed_kmh"]
        target_speed = self.params["target_speed_kmh"]
        
        v_init = init_speed / 3.6
        v_target = target_speed / 3.6
        if v_target <= v_init:
            raise ValueError("加速目标速度需大于初始速度")

        total_time = 0.0
        total_dist = 0.0
        current_v = v_init
        points = [(current_v * 3.6, total_dist)]  # (速度km/h, 距离m)

        # 分段加速计算
        for _, row in self.segment_data.iterrows():
            seg_low = row["speed_low_kmh"] / 3.6
            seg_high = row["speed_high_kmh"] / 3.6
            acc = row["acc_cm_s2"] / 100

            if current_v >= seg_high:
                continue

            # 目标速度在当前分段
            if v_target <= seg_high:
                delta_t = (v_target - current_v) / acc
                delta_s = current_v * delta_t + 0.5 * acc * delta_t**2
                total_time += delta_t
                total_dist += delta_s
                current_v = v_target
                points.append((current_v * 3.6, total_dist))
                break
            # 完整分段
            else:
                delta_t = (seg_high - current_v) / acc
                delta_s = current_v * delta_t + 0.5 * acc * delta_t**2
                total_time += delta_t
                total_dist += delta_s
                current_v = seg_high
                points.append((current_v * 3.6, total_dist))

        return {
            "phase": "加速",
            "time_s": round(total_time, 3),
            "distance_m": round(total_dist, 3),
            "points": points
        }

    # ---------------------- 2. 牵引切换阶段 ----------------------
    def calculate_traction_switch(self, prev_phase_end_v, prev_phase_end_s):
        """
        计算切牵引阶段（无加速度，仅耗时）
        :param prev_phase_end_v: 上一阶段结束速度(km/h)
        :param prev_phase_end_s: 上一阶段结束距离(m)
        """
        switch_delay = self.params["traction_switch_delay_s"]
        # 切牵引阶段速度不变，距离不变，仅耗时
        points = [
            (prev_phase_end_v, prev_phase_end_s),
            (prev_phase_end_v, prev_phase_end_s)
        ]
        return {
            "phase": "切牵引",
            "time_s": round(switch_delay, 3),
            "distance_m": 0.0,
            "points": points
        }

    # ---------------------- 3. 匀速阶段 ----------------------
    def calculate_constant_speed(self, prev_phase_end_v, prev_phase_end_s):
        """
        计算匀速阶段
        :param prev_phase_end_v: 上一阶段结束速度(km/h)
        :param prev_phase_end_s: 上一阶段结束距离(m)
        """
        const_speed = self.params["constant_speed_kmh"]
        const_time = self.params["constant_time_s"]
        
        if const_speed <= 0:
            raise ValueError("匀速速度需大于0")
        
        v_const = const_speed / 3.6
        # 匀速阶段：距离=速度×时间
        delta_s = v_const * const_time
        total_dist = prev_phase_end_s + delta_s
        
        points = [
            (prev_phase_end_v, prev_phase_end_s),
            (const_speed, total_dist)
        ]
        return {
            "phase": "匀速",
            "time_s": round(const_time, 3),
            "distance_m": round(delta_s, 3),
            "points": points
        }

    # ---------------------- 4. 制动建立阶段 ----------------------
    def calculate_brake_build(self, prev_phase_end_v, prev_phase_end_s):
        """
        计算制动建立阶段（无减速度，仅耗时）
        :param prev_phase_end_v: 上一阶段结束速度(km/h)
        :param prev_phase_end_s: 上一阶段结束距离(m)
        """
        brake_build_time = self.params["brake_build_time_s"]
        # 制动建立阶段速度/距离不变，仅耗时
        points = [
            (prev_phase_end_v, prev_phase_end_s),
            (prev_phase_end_v, prev_phase_end_s)
        ]
        return {
            "phase": "制动建立",
            "time_s": round(brake_build_time, 3),
            "distance_m": 0.0,
            "points": points
        }

    # ---------------------- 5. 减速阶段 ----------------------
    def calculate_deceleration(self, prev_phase_end_v, prev_phase_end_s):
        """
        计算减速阶段
        :param prev_phase_end_v: 上一阶段结束速度(km/h)
        :param prev_phase_end_s: 上一阶段结束距离(m)
        """
        target_speed = self.params["coast_speed_kmh"]
        decel_acc = self.params["decel_acc_cm_s2"] / 100  # 转为m/s?，负数
        
        v_init = prev_phase_end_v / 3.6
        v_target = target_speed / 3.6
        if decel_acc >= 0:
            raise ValueError("减速度需为负数（cm/s?）")
        if v_target >= v_init:
            raise ValueError("减速目标速度需小于初始速度")

        # 减速时间：t=(v末 - v初)/加速度
        delta_t = (v_target - v_init) / decel_acc
        # 减速距离：s=v初×t + 0.5×a×t?
        delta_s = v_init * delta_t + 0.5 * decel_acc * delta_t**2
        total_dist = prev_phase_end_s + delta_s

        points = [
            (prev_phase_end_v, prev_phase_end_s),
            (target_speed, total_dist)
        ]
        return {
            "phase": "减速",
            "time_s": round(delta_t, 3),
            "distance_m": round(delta_s, 3),
            "points": points
        }

    # ---------------------- 6. 全阶段汇总 ----------------------
    def calculate_all_phases(self):
        """按顺序计算所有阶段，返回汇总结果"""
        phases = []
        
        # 1. 加速阶段
        acc_result = self.calculate_acceleration()
        phases.append(acc_result)
        last_v = acc_result["points"][-1][0]
        last_s = acc_result["points"][-1][1]

        # 2. 切牵引阶段
        switch_result = self.calculate_traction_switch(last_v, last_s)
        phases.append(switch_result)
        # 切牵引后速度/距离不变
        last_v = switch_result["points"][-1][0]
        last_s = switch_result["points"][-1][1]

        # 3. 匀速阶段
        const_result = self.calculate_constant_speed(last_v, last_s)
        phases.append(const_result)
        last_v = const_result["points"][-1][0]
        last_s = const_result["points"][-1][1]

        # 4. 制动建立阶段
        brake_result = self.calculate_brake_build(last_v, last_s)
        phases.append(brake_result)
        last_v = brake_result["points"][-1][0]
        last_s = brake_result["points"][-1][1]

        # 5. 减速阶段
        decel_result = self.calculate_deceleration(last_v, last_s)
        phases.append(decel_result)

        # 汇总总时间、总距离
        total_time = sum([p["time_s"] for p in phases])
        total_dist = sum([p["distance_m"] for p in phases])

        return {
            "phases": phases,
            "total_time_s": round(total_time, 3),
            "total_distance_m": round(total_dist, 3),
            # 合并所有阶段的点用于绘图
            "all_points": [p for phase in phases for p in phase["points"]]
        }