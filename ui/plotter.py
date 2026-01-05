# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
plt.rcParams["font.sans-serif"] = ["微软雅黑", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.facecolor"] = "white"

class MotionPlotter:
    """运动曲线绘制类（美化版）"""
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax

    def plot_all_phases(self, all_points, phase_results):
        """绘制美化后的速度-距离曲线"""
        # 清空画布
        self.ax.clear()

        # 定义美化的颜色方案
        phase_colors = {
            "加速": "#409eff",
            "切牵引": "#94d82d",
            "匀速": "#e6a23c",
            "制动建立": "#f56c6c",
            "减速": "#67c23a"
        }
        
        # 逐阶段绘制曲线
        for phase in phase_results:
            phase_points = phase["points"]
            x = [p[1] for p in phase_points]
            y = [p[0] for p in phase_points]
            
            # 绘制带样式的曲线
            self.ax.plot(
                x, y,
                color=phase_colors[phase["phase"]],
                linewidth=3,
                marker="o",
                markersize=6,
                markerfacecolor="white",
                markeredgecolor=phase_colors[phase["phase"]],
                markeredgewidth=2,
                label=f"{phase['phase']}（耗时：{phase['time_s']}s，距离：{phase['distance_m']}m）"
            )

        # 美化坐标轴和网格
        self.ax.set_xlabel("距离 (m)", fontsize=12, fontweight="bold", labelpad=10)
        self.ax.set_ylabel("速度 (km/h)", fontsize=12, fontweight="bold", labelpad=10)
        self.ax.set_title("列车全阶段速度-距离曲线", fontsize=14, fontweight="bold", pad=20)
        
        # 网格样式
        self.ax.grid(True, alpha=0.3, linestyle="--", linewidth=1)
        self.ax.set_axisbelow(True)
        
        # 坐标轴样式
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_color("#e5e9f0")
        self.ax.spines["bottom"].set_color("#e5e9f0")
        
        # 图例美化
        self.ax.legend(
            loc="best",
            frameon=True,
            fancybox=True,
            shadow=True,
            framealpha=0.9,
            fontsize=10
        )
        
        # 调整布局
        self.fig.tight_layout()
        
        # 刷新画布
        self.canvas = self.fig.canvas
        self.canvas.draw()