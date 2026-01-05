# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
# ... 后续代码不变
# main.py
import tkinter as tk
from ui.main_gui import MotionGUIMain

if __name__ == "__main__":
    # 解决matplotlib中文显示问题
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 中文黑体
    plt.rcParams["axes.unicode_minus"] = False  # 负号显示

    root = tk.Tk()
    app = MotionGUIMain(root)
    root.mainloop()