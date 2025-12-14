from manim import *
import numpy as np

class SobelFinal(ThreeDScene):
    def construct(self):
        # --- 1. 极致的影院氛围 ---
        self.camera.background_color = "#0f0f0f" # 极黑背景，让光效更亮
        
        # 摄像机位姿：稍微拉远，留出空间给 HUD
        self.set_camera_orientation(phi=65 * DEGREES, theta=-40 * DEGREES, zoom=0.7)
        
        # 开启极慢的呼吸感旋转，模拟电影镜头
        self.begin_ambient_camera_rotation(rate=0.02) 

        # --- 2. 数学模型 ---
        def func(u, v):
            # 两个 Sigmoid 形成的脉冲
            val = 10 / (1 + np.exp(-5 * (u - 3.5))) - 10 / (1 + np.exp(-5 * (u - 8.5)))
            return val / 2.5
        
        def get_derivative(u):
            delta = 0.01 
            return (func(u + delta, 5) - func(u - delta, 5)) / (2 * delta)

        # --- 3. 3D 世界构建 ---
        # 坐标轴：颜色淡一点，不要抢戏
        axes_3d = ThreeDAxes(
            x_range=[0, 10, 1], y_range=[0, 10, 1], z_range=[0, 6, 2],
            x_length=7, y_length=7, z_length=3.5,
            axis_config={"stroke_color": GREY_D, "stroke_width": 1, "include_tip": False}
        ).add_coordinates(font_size=16)

        # 地形曲面：高精度 + 丝滑材质
        surface = Surface(
            lambda u, v: axes_3d.c2p(u, v, func(u, v)), 
            u_range=[0, 10], v_range=[0, 10],
            resolution=(50, 50), # 极高分辨率
            should_make_jagged=False
        )
        
        # 风格：深蓝幽灵色，高透明度，让原本的 Grid 线作为骨架
        surface.set_style(fill_opacity=0.3, stroke_color=BLUE_C, stroke_width=0.5)
        surface.set_fill_by_checkerboard(BLUE_E, BLUE_D, opacity=0.3)

        # --- 4. 辉光扫描器 (Neon Bloom Scanner) ---
        # 使用多层叠加模拟光晕，而不是简单的线条
        scanner_group = VGroup()
        # 核心亮线
        core = Square(side_length=1.5).set_stroke(YELLOW_A, width=4)
        # 外层光晕 (由于 Manim 渲染限制，我们用半透明粗线模拟)
        glow = Square(side_length=1.5).set_stroke(YELLOW, width=20, opacity=0.15)
        
        scanner_group.add(glow, core).rotate(PI/2, axis=RIGHT)
        
        arrow = Arrow3D(start=ORIGIN, end=UP, color=YELLOW, thickness=0.05)

        # --- 5. 钢铁侠 HUD 面板 (The Dashboard) ---
        self.add_fixed_in_frame_mobjects() # 开启 HUD 层

        # [左上角] 理论公式区
        title = Tex(r"\textbf{Sobel Edge Detection}", font_size=40, color=WHITE).to_corner(UL, buff=0.5)
        matrix = MathTex(
            r"\begin{bmatrix} -1 & 0 & 1 \end{bmatrix} * I \approx \frac{\partial I}{\partial x}",
            color=BLUE_B, font_size=32
        ).next_to(title, DOWN, aligned_edge=LEFT)
        
        # [右下角] 实时示波器 (Real-time Oscilloscope)
        # 这是一个半透明的黑底面板，看起来很高级
        plot_bg = Rectangle(height=3.5, width=5, fill_color="#000000", fill_opacity=0.8, stroke_color=GREY, stroke_width=1)
        plot_bg.to_corner(DR, buff=0.5)
        
        plot_axes = Axes(
            x_range=[0, 10, 2], y_range=[-3, 3, 1],
            x_length=4.5, y_length=2.5,
            axis_config={"include_tip": False, "font_size": 16, "stroke_opacity": 0.5}
        ).move_to(plot_bg.get_center())
        
        plot_label = Text("Derivative (Gradient)", font_size=20, color=GREY_B).next_to(plot_bg, UP, aligned_edge=RIGHT)
        
        # [中下方] 状态指示器 (Status Indicator)
        # 只有简单的文字，没有大色块
        status_text = Text("STATUS: SCANNING...", font="Monospace", font_size=24, color=YELLOW)
        status_text.to_edge(DOWN, buff=1.0) # 放在底部中间

        # 打包 HUD
        hud_group = VGroup(title, matrix, plot_bg, plot_axes, plot_label, status_text)
        self.add_fixed_in_frame_mobjects(hud_group)

        # --- 6. 动画核心逻辑 ---
        x_tracker = ValueTracker(1)
        
        def update_scene(mob):
            # 获取当前 x
            u = x_tracker.get_value()
            z = func(u, 5)
            
            # 1. 移动扫描器
            pos_3d = axes_3d.c2p(u, 5, z + 0.1)
            scanner_group.move_to(pos_3d)
            
            # 2. 移动箭头
            deriv = get_derivative(u)
            pt_start = axes_3d.c2p(u, 5, z)
            pt_end = pt_start + np.array([deriv * 0.8, 0, 0]) # 箭头长度缩放
            arrow.put_start_and_end_on(pt_start, pt_end)
            
            # 3. 颜色与状态逻辑 (阈值判定)
            threshold = 1.0
            if abs(deriv) > threshold:
                # 触发警报色
                target_color = RED
                status_str = "STATUS: EDGE DETECTED!"
                # 如果导数为负，显示下降沿
                if deriv < -threshold:
                    status_str += " (FALLING)"
                else:
                    status_str += " (RISING)"
            else:
                # 平常色
                target_color = YELLOW
                status_str = "STATUS: SCANNING..."
            
            # 应用颜色
            core.set_color(target_color)
            glow.set_color(target_color)
            arrow.set_color(target_color)
            
            # 应用文字 (重新创建 Text 对象比较耗资源，但最简单)
            # 优化：我们直接修改 text 内容和颜色，如果不方便直接修改，用 Variable 更稳
            status_text.become(
                Text(status_str, font="Monospace", font_size=24, color=target_color)
                .move_to(status_text.get_center())
            )

        scanner_group.add_updater(update_scene)

        # --- 7. 2D 曲线的实时绘制 (Oscilloscope Trace) ---
        # 这就是你要的“数据证据”
        graph_curve = always_redraw(lambda: plot_axes.plot(
            lambda x: get_derivative(x),
            x_range=[0, x_tracker.get_value()], # 只画到当前进度
            color=status_text.get_color(), # 颜色跟状态同步！
            stroke_width=3
        ))
        
        # 曲线头部的光点
        graph_dot = always_redraw(lambda: Dot(
            point=plot_axes.c2p(x_tracker.get_value(), get_derivative(x_tracker.get_value())),
            color=WHITE,
            radius=0.06
        ).set_glow_factor(2)) # 发光点

        self.add_fixed_in_frame_mobjects(graph_curve, graph_dot)

        # --- 8. 开始演出 ---
        self.add(axes_3d, surface, scanner_group, arrow)
        
        # 使用 smooth 曲线，且时间稍微长一点，展示细节
        self.play(
            x_tracker.animate.set_value(9),
            run_time=12,
            rate_func=lambda t: smooth(t, inflection=10.0) # 自定义平滑度
        )
        self.wait(1)