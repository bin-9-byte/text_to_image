import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, scrolledtext
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import tempfile
# 导入重构后的模块，复用核心功能
from text_to_image import create_text_image

class TextToImageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文字转图片工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 存储用户设置
        self.settings = {
            "width": 800,
            "height": 600,
            "font_path": "",
            "font_size": 40,
            "text_color": (0, 0, 0),
            "bg_color": (255, 255, 255),
            "horizontal_align": "center",
            "vertical_align": "center",
            "padding": 20,
            "text": ""
        }
        
        # 临时文件用于预览
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        
        # 绑定窗口关闭事件，用于清理临时文件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 创建初始页面
        self.create_size_selection_page()

    def create_size_selection_page(self):
        """创建图片大小选择页面"""
        self.clear_frame()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="选择图片尺寸", font=("Arial", 16)).pack(pady=20)
        
        # 预设尺寸
        sizes = [
            ("小 (400x300)", 400, 300),
            ("中 (800x600)", 800, 600),
            ("大 (1200x900)", 1200, 900),
            ("正方形 (600x600)", 600, 600),
            ("宽屏 (1920x1080)", 1920, 1080)
        ]
        
        size_frame = ttk.Frame(frame)
        size_frame.pack(fill=tk.X, pady=10)
        
        for name, w, h in sizes:
            ttk.Button(
                size_frame, 
                text=name,
                command=lambda w=w, h=h: self.set_size_and_continue(w, h)
            ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 自定义尺寸
        ttk.Label(frame, text="或自定义尺寸:").pack(anchor=tk.W, pady=10)
        
        custom_frame = ttk.Frame(frame)
        custom_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(custom_frame, text="宽度:").pack(side=tk.LEFT, padx=5)
        width_entry = ttk.Entry(custom_frame, width=10)
        width_entry.pack(side=tk.LEFT, padx=5)
        width_entry.insert(0, "800")
        
        ttk.Label(custom_frame, text="高度:").pack(side=tk.LEFT, padx=5)
        height_entry = ttk.Entry(custom_frame, width=10)
        height_entry.pack(side=tk.LEFT, padx=5)
        height_entry.insert(0, "600")
        
        ttk.Button(
            custom_frame,
            text="确认",
            command=lambda: self.set_size_and_continue(
                int(width_entry.get()), 
                int(height_entry.get())
            )
        ).pack(side=tk.LEFT, padx=10)

    def set_size_and_continue(self, width, height):
        """设置尺寸并进入编辑页面"""
        self.settings["width"] = width
        self.settings["height"] = height
        self.create_editor_page()

    def create_editor_page(self):
        """创建编辑页面"""
        self.clear_frame()
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="设置", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 文字输入
        ttk.Label(control_frame, text="输入文字:").pack(anchor=tk.W, pady=5)
        self.text_input = scrolledtext.ScrolledText(control_frame, width=30, height=10)
        self.text_input.pack(fill=tk.X, pady=5)
        self.text_input.bind("<KeyRelease>", self.update_preview)
        
        # 字体选择
        ttk.Label(control_frame, text="选择字体:").pack(anchor=tk.W, pady=5)
        font_frame = ttk.Frame(control_frame)
        font_frame.pack(fill=tk.X, pady=5)
        
        self.font_path_var = tk.StringVar()
        ttk.Entry(font_frame, textvariable=self.font_path_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(font_frame, text="浏览", command=self.choose_font).pack(side=tk.LEFT)
        
        # 字体大小
        ttk.Label(control_frame, text="字体大小:").pack(anchor=tk.W, pady=5)
        self.font_size_var = tk.IntVar(value=self.settings["font_size"])
        ttk.Scale(
            control_frame,
            from_=10,
            to=100,
            variable=self.font_size_var,
            command=lambda v: self.update_font_size(int(float(v)))
        ).pack(fill=tk.X, pady=5)
        ttk.Label(control_frame, textvariable=self.font_size_var).pack()
        
        # 文字颜色
        ttk.Label(control_frame, text="文字颜色:").pack(anchor=tk.W, pady=5)
        self.text_color_var = tk.StringVar(value="#000000")
        color_frame = ttk.Frame(control_frame)
        color_frame.pack(fill=tk.X, pady=5)
        ttk.Entry(color_frame, textvariable=self.text_color_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(color_frame, text="选择", command=lambda: self.choose_color("text")).pack(side=tk.LEFT)
        
        # 背景颜色
        ttk.Label(control_frame, text="背景颜色:").pack(anchor=tk.W, pady=5)
        self.bg_color_var = tk.StringVar(value="#FFFFFF")
        bg_frame = ttk.Frame(control_frame)
        bg_frame.pack(fill=tk.X, pady=5)
        ttk.Entry(bg_frame, textvariable=self.bg_color_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(bg_frame, text="选择", command=lambda: self.choose_color("bg")).pack(side=tk.LEFT)
        
        # 水平对齐
        ttk.Label(control_frame, text="水平对齐:").pack(anchor=tk.W, pady=5)
        self.horizontal_align_var = tk.StringVar(value=self.settings["horizontal_align"])
        ttk.Combobox(
            control_frame,
            textvariable=self.horizontal_align_var,
            values=["left", "center", "right"],
            state="readonly"
        ).pack(fill=tk.X, pady=5)
        self.horizontal_align_var.trace_add("write", lambda *args: self.update_preview())
        
        # 垂直对齐
        ttk.Label(control_frame, text="垂直对齐:").pack(anchor=tk.W, pady=5)
        self.vertical_align_var = tk.StringVar(value=self.settings["vertical_align"])
        ttk.Combobox(
            control_frame,
            textvariable=self.vertical_align_var,
            values=["top", "center", "bottom"],
            state="readonly"
        ).pack(fill=tk.X, pady=5)
        self.vertical_align_var.trace_add("write", lambda *args: self.update_preview())
        
        # 边距
        ttk.Label(control_frame, text="边距:").pack(anchor=tk.W, pady=5)
        self.padding_var = tk.IntVar(value=self.settings["padding"])
        ttk.Scale(
            control_frame,
            from_=0,
            to=100,
            variable=self.padding_var,
            command=lambda v: self.update_padding(int(float(v)))
        ).pack(fill=tk.X, pady=5)
        ttk.Label(control_frame, textvariable=self.padding_var).pack()
        
        # 按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(
            button_frame,
            text="返回",
            command=self.create_size_selection_page
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="保存图片",
            command=self.save_image
        ).pack(side=tk.LEFT, padx=5)
        
        # 右侧预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="预览", padding="10")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_canvas = tk.Canvas(preview_frame, bg="#f0f0f0")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        h_scroll = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        v_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        self.preview_canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始预览
        self.update_preview()

    def choose_font(self):
        """选择字体文件"""
        font_path = filedialog.askopenfilename(
            filetypes=[("字体文件", "*.ttf *.otf")]
        )
        if font_path:
            self.font_path_var.set(font_path)
            self.update_preview()

    def choose_color(self, color_type):
        """选择颜色"""
        color = colorchooser.askcolor()[1]
        if color:
            if color_type == "text":
                self.text_color_var.set(color)
            else:
                self.bg_color_var.set(color)
            self.update_preview()

    def update_font_size(self, value):
        """更新字体大小"""
        self.font_size_var.set(value)
        self.update_preview()

    def update_padding(self, value):
        """更新边距"""
        self.padding_var.set(value)
        self.update_preview()

    def update_preview(self, event=None):
        """更新预览图"""
        # 更新设置
        self.settings["text"] = self.text_input.get("1.0", tk.END).rstrip("\n")
        self.settings["font_path"] = self.font_path_var.get()
        self.settings["font_size"] = self.font_size_var.get()
        self.settings["text_color"] = self.hex_to_rgb(self.text_color_var.get())
        self.settings["bg_color"] = self.hex_to_rgb(self.bg_color_var.get())
        self.settings["horizontal_align"] = self.horizontal_align_var.get()
        self.settings["vertical_align"] = self.vertical_align_var.get()
        self.settings["padding"] = self.padding_var.get()
        
        # 生成预览图
        try:
            self.create_text_image(self.temp_file)
            
            # 显示预览图
            img = Image.open(self.temp_file)
            # 调整预览大小以适应窗口，但保持比例
            canvas_width = self.preview_canvas.winfo_width() or 600
            canvas_height = self.preview_canvas.winfo_height() or 400
            
            img.thumbnail((canvas_width - 40, canvas_height - 40))
            photo = ImageTk.PhotoImage(img)
            
            self.preview_canvas.delete("all")
            self.preview_image = photo  # 保持引用
            self.preview_canvas.create_image(
                canvas_width//2, canvas_height//2, 
                image=photo, anchor=tk.CENTER
            )
            self.preview_canvas.config(scrollregion=self.preview_canvas.bbox("all"))
        except Exception as e:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(
                50, 50, 
                text=f"预览错误: {str(e)}", 
                anchor=tk.NW, 
                fill="red"
            )

    def save_image(self):
        """保存图片"""
        output_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG图片", "*.png"), ("JPG图片", "*.jpg"), ("所有文件", "*.*")]
        )
        if output_path:
            try:
                self.create_text_image(output_path)
                messagebox.showinfo("成功", f"图片已保存至: {output_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存图片失败: {str(e)}")

    def create_text_image(self, output_path):
        """创建文字图片（复用text_to_image模块的功能）"""
        # 直接调用模块中的函数，消除代码重复
        try:
            create_text_image(
                text=self.settings["text"],
                font_path=self.settings["font_path"],
                output_path=output_path,
                font_size=self.settings["font_size"],
                text_color=self.settings["text_color"],
                bg_color=self.settings["bg_color"],
                width=self.settings["width"],
                height=self.settings["height"],
                horizontal_align=self.settings["horizontal_align"],
                vertical_align=self.settings["vertical_align"],
                padding=self.settings["padding"]
            )
        except Exception as e:
            # 重新抛出异常，让调用者处理
            raise Exception(f"创建图片失败: {str(e)}")

    def hex_to_rgb(self, hex_color):
        """将十六进制颜色转换为RGB元组"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def clear_frame(self):
        """清空当前窗口内容"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def on_closing(self):
        """窗口关闭时清理资源"""
        # 尝试删除临时文件
        try:
            if os.path.exists(self.temp_file):
                os.unlink(self.temp_file)
        except:
            pass
        # 关闭窗口
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToImageGUI(root)
    root.mainloop()