from manim import *
import numpy as np

class SobelMasterclass(ThreeDScene):
    def construct(self):
        # === 全局设置 ===
        self.camera.background_color = "#111111"
        
        # 定义核心数学函数 (用于后续所有章节)
        def func(u, v):
            # 光滑的阶跃信号
            val = 10 / (1 + np.exp(-5 * (u - 3.5))) - 10 / (1 + np.exp(-5 * (u - 8.5)))
            return val / 2.5

        def get_derivative(u):
            delta = 0.01 
            return (func(u + delta, 5) - func(u - delta, 5)) / (2 * delta)

        # ==========================================
        # Chapter 1: The Digital Image (数字矩阵世界)
        # ==========================================
        
        # 1.1 标题开场
        title = Tex(r"\textbf{How Computers See Edges}", font_size=60).to_edge(UP)
        subtitle = Text("From Pixels to Gradients", font="Monospace", font_size=32, color=BLUE).next_to(title, DOWN)
        self.play(Write(title), FadeIn(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # 1.2 创建一个 10x10 的整数矩阵来模拟像素
        # 我们用数值来填充它，模拟中间亮两边暗
        matrix_values = []
        for y in range(10):
            row = []
            for x in range(10):
                # 根据我们的函数采样整数值
                val = int(func(x, y) * 2.5 + 0.5) # 还原到 0-10 范围
                row.append(val)
            matrix_values.append(row)

        # 使用 IntegerMatrix 显示数字
        pixel_matrix = IntegerMatrix(
            matrix_values,
            v_buff=0.5, h_buff=0.5
        ).scale(0.6)
        
        pixel_label = Text("Image Pixel Matrix (Intensity)", font="Monospace", font_size=24, color=GREY).next_to(pixel_matrix, UP)

        self.play(Create(pixel_matrix), Write(pixel_label))
        self.wait(1)

        # 1.3 高亮显示“边缘”所在的列 (第 3,4 列和 8,9 列)
        # Manim 的 Matrix 索引比较特殊，我们需要手动找位置
        highlights = VGroup()
        for i in range(10): # 每一行
            # 左边缘 (3->10)
            rect_left = SurroundingRectangle(pixel_matrix.get_entries()[i*10 + 3], color=YELLOW) 
            rect_right = SurroundingRectangle(pixel_matrix.get_entries()[i*10 + 4], color=YELLOW)
            highlights.add(rect_left, rect_right)

        self.play(ShowPassingFlash(highlights.copy().set_color(YELLOW), run_time=2))
        
        narrative1 = Text("Where is the edge?", font="Monospace", font_size=36, color=YELLOW).to_edge(DOWN)
        self.play(Write(narrative1))
        self.wait(1)
        
        # 清场
        self.play(FadeOut(pixel_matrix), FadeOut(pixel_label), FadeOut(narrative1), FadeOut(highlights))

        # ==========================================
        # Chapter 2: The Dimension Shift (2D -> 3D)
        # ==========================================
        
        # 这是最 3b1b 的部分：旋转视角，数字变成地形
        
        # 2.1 建立 3D 坐标系
        axes_3d = ThreeDAxes(
            x_range=[0, 10, 1], y_range=[0, 10, 1], z_range=[0, 6, 2],
            x_length=7, y_length=7, z_length=3.5,
            axis_config={"include_tip": False, "stroke_color": GREY_C}
        ).add_coordinates(font_size=16)

        # 2.2 建立地形
        surface = Surface(
            lambda u, v: axes_3d.c2p(u, v, func(u, v)), 
            u_range=[0, 10], v_range=[0, 10],
            resolution=(50, 50),
            should_make_jagged=False
        )
        surface.set_style(fill_opacity=0.6, stroke_color=BLUE_C, stroke_width=0.5)
        surface.set_fill_by_checkerboard(BLUE_E, BLUE_D, opacity=0.6)

        # 2.3 动画：先以俯视图(2D)出现，然后旋转成 3D
        self.set_camera_orientation(phi=0, theta=-90*DEGREES, zoom=0.8) # 俯视图
        self.play(Create(axes_3d), FadeIn(surface))
        
        narrative2 = Text("View Intensity as Height", font="Monospace", font_size=32).to_corner(UL)
        self.add_fixed_in_frame_mobjects(narrative2)
        self.play(Write(narrative2))
        self.wait(0.5)

        # 华丽的旋转镜头
        self.move_camera(phi=65 * DEGREES, theta=-45 * DEGREES, zoom=0.7, run_time=3)
        self.begin_ambient_camera_rotation(rate=0.04) # 保持旋转
        
        self.wait(1)
        self.play(FadeOut(narrative2))

        # ==========================================
        # Chapter 3: The Sobel Operator (数学原理)
        # ==========================================

        # 3.1 展示卷积核
        # 我们把卷积核画在屏幕右上角
        kernel_label = Tex(r"Sobel Kernel $K_x$", font_size=36).to_corner(UR).shift(LEFT*1)
        kernel_matrix = MathTex(
            r"\begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}"
        ).next_to(kernel_label, DOWN)
        
        theory_group = VGroup(kernel_label, kernel_matrix).set_color(YELLOW)
        self.add_fixed_in_frame_mobjects(theory_group)
        self.play(FadeIn(theory_group, shift=LEFT))

        # 3.2 解释原理：左 - 右
        explanation = Tex(
            r"Approximates Derivative: \\",
            r"Right - Left", 
            color=BLUE_B
        ).next_to(kernel_matrix, DOWN, buff=0.5).scale(0.8)
        self.add_fixed_in_frame_mobjects(explanation)
        self.play(Write(explanation))
        self.wait(2)
        
        # 清除解释文字，保留矩阵
        self.play(FadeOut(explanation))

        # ==========================================
        # Chapter 4: The Convolution Scan (最终演示)
        # ==========================================

        # 4.1 准备扫描器
        scanner_group = VGroup()
        core = Square(side_length=1.5).set_stroke(YELLOW, width=4)
        glow = Square(side_length=1.5).set_stroke(YELLOW, width=20, opacity=0.2)
        scanner_group.add(glow, core).rotate(PI/2, axis=RIGHT)
        
        arrow = Arrow3D(start=ORIGIN, end=UP, color=YELLOW, thickness=0.05)
        
        # 4.2 准备示波器 (右下角)
        plot_bg = Rectangle(height=3, width=5, fill_color=BLACK, fill_opacity=0.8, stroke_color=GREY).to_corner(DR)
        plot_axes = Axes(
            x_range=[0, 10, 2], y_range=[-3, 3, 1],
            x_length=4.5, y_length=2.5,
            axis_config={"include_tip": False}
        ).move_to(plot_bg.get_center())
        
        plot_label = Text("Derivative Output", font="Monospace", font_size=20).next_to(plot_bg, UP, aligned_edge=RIGHT)
        
        self.add_fixed_in_frame_mobjects(plot_bg, plot_axes, plot_label)
        self.play(FadeIn(plot_bg), Create(plot_axes), Write(plot_label))

        # 4.3 动画逻辑
        x_tracker = ValueTracker(1)
        
        def update_scan(mob):
            u = x_tracker.get_value()
            z = func(u, 5)
            
            # 移动扫描器
            pos = axes_3d.c2p(u, 5, z+0.1)
            scanner_group.move_to(pos)
            
            # 移动箭头
            deriv = get_derivative(u)
            pt_start = axes_3d.c2p(u, 5, z)
            pt_end = pt_start + np.array([deriv*0.8, 0, 0])
            arrow.put_start_and_end_on(pt_start, pt_end)
            
            # 颜色逻辑
            color = RED if abs(deriv) > 1.0 else YELLOW
            core.set_color(color)
            glow.set_color(color)
            arrow.set_color(color)

        scanner_group.add_updater(update_scan)

        # 实时绘制曲线
        graph_curve = always_redraw(lambda: plot_axes.plot(
            lambda x: get_derivative(x),
            x_range=[0, x_tracker.get_value()],
            color=core.get_color(), # 同步颜色
            stroke_width=3
        ))
        
        graph_dot = always_redraw(lambda: Dot(
            point=plot_axes.c2p(x_tracker.get_value(), get_derivative(x_tracker.get_value())),
            color=WHITE, radius=0.06
        ))

        self.add_fixed_in_frame_mobjects(graph_curve, graph_dot)
        self.add(scanner_group, arrow)

        # 4.4 执行扫描
        self.play(
            x_tracker.animate.set_value(9),
            run_time=8,
            rate_func=linear
        )
        
        self.wait(2)
        
        # 4.5 结尾
        end_text = Text("Gradient Magnitude = Edge Strength", font="Monospace", font_size=36, color=WHITE).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(end_text)
        self.play(Write(end_text))
        self.wait(3)