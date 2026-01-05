# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.data_loader import ExcelDataLoader
from core.motion_calculator import MotionPhaseCalculator
from ui.plotter import MotionPlotter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class MotionGUIMain:
    def __init__(self, root):
        self.root = root
        self.root.title("列车运动阶段计算工具 V1.0")
        self.root.geometry("1300x800")
        self.root.resizable(True, True)
        
        # 美化配置
        self.setup_style()
        
        # 初始化核心对象
        self.data_loader = None
        self.calculator = None
        self.plotter = None
        
        # 创建界面
        self.create_widgets()

    def setup_style(self):
        """设置界面美化样式"""
        # 主色调配置
        self.bg_color = "#f0f5ff"
        self.btn_color = "#409eff"
        self.btn_hover = "#66b1ff"
        self.frame_color = "#ffffff"
        self.text_color = "#303133"
        
        # 全局样式
        self.root.configure(bg=self.bg_color)
        
        # 自定义ttk样式
        style = ttk.Style()
        style.theme_use("clam")
        
        # 框架样式
        style.configure("Custom.TFrame", background=self.frame_color)
        # 按钮样式
        style.configure("Custom.TButton", 
                       font=("微软雅黑", 10),
                       padding=6,
                       background=self.btn_color)
        # 标签样式
        style.configure("Custom.TLabel", 
                       font=("微软雅黑", 10),
                       background=self.frame_color,
                       foreground=self.text_color)
        # 输入框样式
        style.configure("Custom.TEntry", 
                       font=("微软雅黑", 10),
                       padding=5)
        # 表格样式
        style.configure("Custom.Treeview",
                       font=("微软雅黑", 9),
                       rowheight=25,
                       background=self.frame_color)
        style.configure("Custom.Treeview.Heading",
                       font=("微软雅黑", 10, "bold"),
                       background="#e6f7ff",
                       foreground="#1890ff")

    def create_widgets(self):
        """创建美化后的界面组件"""
        # 1. Excel文件选择区域
        excel_frame = ttk.Frame(self.root, style="Custom.TFrame")
        excel_frame.pack(fill="x", padx=20, pady=15)
        excel_frame.configure(relief="groove", borderwidth=1)
        
        ttk.Label(excel_frame, text="Excel配置文件：", style="Custom.TLabel").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.excel_path_var = tk.StringVar(value="")
        self.excel_entry = ttk.Entry(excel_frame, textvariable=self.excel_path_var, width=60, style="Custom.TEntry")
        self.excel_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # 选择文件按钮
        select_btn = ttk.Button(excel_frame, text="选择文件", style="Custom.TButton", command=self.select_excel)
        select_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # 加载配置按钮
        load_btn = ttk.Button(excel_frame, text="加载配置", style="Custom.TButton", command=self._load_excel)
        load_btn.grid(row=0, column=3, padx=10, pady=10)

        # 2. 参数显示区域
        param_frame = ttk.Frame(self.root, style="Custom.TFrame")
        param_frame.pack(fill="x", padx=20, pady=10)
        param_frame.configure(relief="groove", borderwidth=1)
        
        # 参数网格布局
        params = [
            ("初始速度(km/h)：", "init_speed_var"),
            ("加速目标速度(km/h)：", "target_speed_var"),
            ("匀速速度(km/h)：", "constant_speed_var"),
            ("匀速时间(s)：", "constant_time_var"),
            ("减速度(cm/s²)：", "decel_acc_var"),
            ("滑行速度(km/h)：", "coast_speed_var"),
            ("切牵引延迟(s)：", "traction_switch_var"),
            ("制动建立时间(s)：", "brake_build_var")
        ]
        
        # 初始化参数变量
        self.param_vars = {}
        for i, (label_text, var_name) in enumerate(params):
            ttk.Label(param_frame, text=label_text, style="Custom.TLabel").grid(row=i//4, column=(i%4)*2, padx=10, pady=8, sticky="w")
            var = tk.StringVar(value="--")
            self.param_vars[var_name] = var
            ttk.Label(param_frame, textvariable=var, style="Custom.TLabel", foreground="#1890ff").grid(row=i//4, column=(i%4)*2+1, padx=5, pady=8, sticky="w")

        # 3. 计算按钮区域
        btn_frame = ttk.Frame(self.root, style="Custom.TFrame")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        calc_all_btn = ttk.Button(btn_frame, text="计算全阶段", style="Custom.TButton", command=self._calculate_all_phases)
        calc_all_btn.pack(side="left", padx=20, pady=10)
        
        calc_acc_btn = ttk.Button(btn_frame, text="仅计算加速阶段", style="Custom.TButton", command=self._calculate_acc_only)
        calc_acc_btn.pack(side="left", padx=10, pady=10)

        # 4. 结果显示区域
        result_frame = ttk.Frame(self.root, style="Custom.TFrame")
        result_frame.pack(fill="x", padx=20, pady=10)
        result_frame.configure(relief="groove", borderwidth=1)
        
        ttk.Label(result_frame, text="计算结果汇总：", style="Custom.TLabel", font=("微软雅黑", 11, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.total_time_var = tk.StringVar(value="--")
        self.total_dist_var = tk.StringVar(value="--")
        
        ttk.Label(result_frame, text="总耗时(s)：", style="Custom.TLabel").grid(row=0, column=1, padx=20, pady=10, sticky="w")
        ttk.Label(result_frame, textvariable=self.total_time_var, style="Custom.TLabel", font=("微软雅黑", 11, "bold"), foreground="#e6a23c").grid(row=0, column=2, padx=5, pady=10, sticky="w")
        
        ttk.Label(result_frame, text="总距离(m)：", style="Custom.TLabel").grid(row=0, column=3, padx=20, pady=10, sticky="w")
        ttk.Label(result_frame, textvariable=self.total_dist_var, style="Custom.TLabel", font=("微软雅黑", 11, "bold"), foreground="#e6a23c").grid(row=0, column=4, padx=5, pady=10, sticky="w")

        # 5. 阶段详情表格
        table_frame = ttk.Frame(self.root, style="Custom.TFrame")
        table_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(table_frame, text="各阶段详情：", style="Custom.TLabel", font=("微软雅黑", 11, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.phase_tree = ttk.Treeview(table_frame, columns=("phase", "time", "distance"), show="headings", style="Custom.Treeview")
        self.phase_tree.heading("phase", text="阶段名称")
        self.phase_tree.heading("time", text="耗时(s)")
        self.phase_tree.heading("distance", text="距离(m)")
        
        # 设置列宽
        self.phase_tree.column("phase", width=150)
        self.phase_tree.column("time", width=100)
        self.phase_tree.column("distance", width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.phase_tree.yview)
        self.phase_tree.configure(yscrollcommand=scrollbar.set)
        
        self.phase_tree.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        scrollbar.pack(side="right", fill="y", padx=(0,10), pady=5)

        # 6. 绘图区域
        plot_frame = ttk.Frame(self.root, style="Custom.TFrame")
        plot_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ttk.Label(plot_frame, text="速度-距离曲线：", style="Custom.TLabel", font=("微软雅黑", 11, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # 新增：保存曲线按钮
        save_btn = ttk.Button(plot_frame, text="保存曲线", style="Custom.TButton", command=self.save_plot)
        save_btn.pack(anchor="w", padx=10, pady=5)

        # 创建matplotlib画布
        self.fig, self.ax = plt.subplots(figsize=(12, 5), facecolor="white")
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
        self.plotter = MotionPlotter(self.fig, self.ax)

    def select_excel(self):
        """打开文件选择对话框选择Excel文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel配置文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")],
            initialdir=os.getcwd()  # 默认打开当前目录
        )
        if file_path:
            self.excel_path_var.set(file_path)

    def _load_excel(self):
        """加载Excel配置并更新参数显示"""
        excel_path = self.excel_path_var.get().strip()
        if not excel_path:
            messagebox.showwarning("警告", "请先选择Excel配置文件！")
            return
        
        if not os.path.exists(excel_path):
            messagebox.showerror("错误", f"文件不存在：{excel_path}")
            return

        try:
            self.data_loader = ExcelDataLoader(excel_path)
            params = self.data_loader.default_params

            # 更新参数显示
            self.param_vars["init_speed_var"].set(params["init_speed_kmh"])
            self.param_vars["target_speed_var"].set(params["target_speed_kmh"])
            self.param_vars["constant_speed_var"].set(params["constant_speed_kmh"])
            self.param_vars["constant_time_var"].set(params["constant_time_s"])
            self.param_vars["decel_acc_var"].set(params["decel_acc_cm_s2"])
            self.param_vars["coast_speed_var"].set(params["coast_speed_kmh"])
            self.param_vars["traction_switch_var"].set(params["traction_switch_delay_s"])
            self.param_vars["brake_build_var"].set(params["brake_build_time_s"])

            # 初始化计算器
            self.calculator = MotionPhaseCalculator(
                self.data_loader.segment_data,
                self.data_loader.default_params
            )
            
            messagebox.showinfo("成功", "Excel配置加载成功！")
        except Exception as e:
            messagebox.showerror("错误", f"加载失败：{str(e)}")
            self.data_loader = None
            self.calculator = None

    def _calculate_all_phases(self):
        """计算全阶段并绘图"""
        if not self.calculator:
            messagebox.showwarning("警告", "请先加载Excel配置！")
            return

        try:
            all_result = self.calculator.calculate_all_phases()

            # 更新汇总结果
            self.total_time_var.set(all_result["total_time_s"])
            self.total_dist_var.set(all_result["total_distance_m"])

            # 清空表格并填充数据
            for item in self.phase_tree.get_children():
                self.phase_tree.delete(item)
            for phase in all_result["phases"]:
                self.phase_tree.insert("", "end", values=(
                    phase["phase"],
                    phase["time_s"],
                    phase["distance_m"]
                ))

            # 绘制曲线
            self.plotter.plot_all_phases(all_result["all_points"], all_result["phases"])
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")

    def _calculate_acc_only(self):
        """仅计算加速阶段"""
        if not self.calculator:
            messagebox.showwarning("警告", "请先加载Excel配置！")
            return

        try:
            acc_result = self.calculator.calculate_acceleration()

            # 更新汇总结果
            self.total_time_var.set(acc_result["time_s"])
            self.total_dist_var.set(acc_result["distance_m"])

            # 清空表格并填充数据
            for item in self.phase_tree.get_children():
                self.phase_tree.delete(item)
            self.phase_tree.insert("", "end", values=(
                acc_result["phase"],
                acc_result["time_s"],
                acc_result["distance_m"]
            ))

            # 绘制曲线
            self.plotter.plot_all_phases(acc_result["points"], [acc_result])
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")
     # ===================== 新增save_plot方法 =====================
    def save_plot(self):
        """保存速度-距离曲线为图片或PDF"""
        # 导入pandas用于生成时间戳（如果顶部没导入，需补充）
        import pandas as pd
        from tkinter import filedialog, messagebox
        
        # 先判断是否有绘制的曲线（避免空图保存）
        if not hasattr(self, 'fig') or self.ax.lines == []:
            messagebox.showwarning("提示", "请先计算并生成曲线后再保存！")
            return
        
        # 弹出保存对话框
        save_path = filedialog.asksaveasfilename(
            title="保存速度-距离曲线",
            defaultextension=".png",  # 默认保存为PNG
            filetypes=[
                ("PNG高清图片", "*.png"),
                ("JPG图片", "*.jpg"),
                ("PDF文件", "*.pdf"),
                ("SVG矢量图", "*.svg")  # 可选：新增矢量图格式
            ],
            # 自动生成带时间戳的文件名，避免重复
            initialfile=f"列车速度距离曲线_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if save_path:
            try:
                # 保存曲线（高分辨率、无白边）
                self.fig.savefig(
                    save_path,
                    dpi=300,  # 300DPI高清
                    bbox_inches="tight",  # 去除图片边缘白边
                    facecolor="white",  # 背景白色
                    edgecolor="none"  # 无边框
                )
                messagebox.showinfo("保存成功", f"曲线已保存至：\n{save_path}")
            except Exception as e:
                messagebox.showerror("保存失败", f"错误原因：{str(e)}\n请检查路径是否有权限写入")

    # ===================== 方法结束 =====================   

