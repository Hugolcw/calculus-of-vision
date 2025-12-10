from manim import *
import numpy as np 

class SobelAdvanced(ThreeDScene):
    def construct(self):
        
        # 1. Setup Initialization
        self.camera.background_color = "#1e1e1e"
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=0.8)
        self.camera.frame_center = np.array([-2, 0, 0])
        
        # 2. Mathematical Model
        def func(u, v):
            val = 10 / (1 + np.exp(-5 * (u - 3.5))) - 10 / (1 + np.exp(-5 * (u - 8.5)))
            return val / 2.5
        
        def get_derivative(u):
            delta = 0.01 
            return (func(u + delta, 5) - func(u - delta, 5)) / (2 * delta)
        
        # 3. Building 3D World
        axes_3d = ThreeDAxes(
            x_range=[0, 10, 1], y_range=[0, 10, 1], z_range=[0, 6, 2],
            x_length=6, y_length=6, z_length=3
        ).add_coordinates().shift(LEFT * 3.5)
        
        surface = Surface(
            lambda u, v: axes_3d.c2p(u, v, func(u, v)), 
            u_range=[0, 10], v_range=[0, 10],
            resolution=(24, 24), 
            should_make_jagged=False
        )
        surface.set_style(fill_opacity=0.4, stroke_color=BLUE_A, stroke_width=0.5)
        surface.set_fill_by_checkerboard(BLUE_D, BLUE_E, opacity=0.4)
        
        scanner = Square(side_length=1.5).set_color(RED).set_stroke(width=4)
        scanner.rotate(PI/2, axis=RIGHT)
        
        arrow = Arrow3D(start=ORIGIN, end=UP, color=YELLOW)
        
        # 4. Building 2D dashboard
        title = Text("Sobel Operator & Derivative", font_size=36).to_corner(UL)
        
        # [FIX 1] 修正 LaTeX 括号：f{x-1} -> f(x-1)
        formula = MathTex(
            r"f'(x) \approx \frac{f(x+1) - f(x-1)}{2}"
        ).scale(0.8).next_to(title, DOWN, buff=0.2).set_color(BLUE)
        
        axes_2d = Axes(
            x_range=[0, 10, 1],
            y_range=[-3, 3, 1],
            x_length=5, y_length=4,
            tips=False
        ).to_edge(RIGHT, buff=1).shift(DOWN * 0.5)
        
        axes_label = axes_2d.get_axis_labels(x_label="x", y_label="Gradient")
        panel_bg = SurroundingRectangle(axes_2d, color=WHITE, buff=0.2, stroke_opacity=0.5)
        
        # [FIX 2] 增加位置参数 UP，否则文字会跑到右边
        x_label = Text("Pos (x): ", font_size=24).next_to(panel_bg, UP, buff=0.5, aligned_edge=LEFT)
        x_num = DecimalNumber(0, num_decimal_places=2, font_size=24).next_to(x_label, RIGHT)
        
        grad_label = Text("Grad (d): ", font_size=24).next_to(x_label, RIGHT, buff=1)
        grad_num = DecimalNumber(0, num_decimal_places=2, font_size=24).next_to(grad_label, RIGHT)
        
        hud_group = VGroup(title, formula, axes_2d, axes_label, panel_bg, x_label, x_num, grad_label, grad_num)
        self.add_fixed_in_frame_mobjects(hud_group)
        
        # 5. Animation Drive Engine
        x_tracker = ValueTracker(1)
        
        # [逻辑核心] 定义更新函数
        def update_3d_elements(mob):
            # 获取当前进度 t
            u = x_tracker.get_value()
            v = 5 
            z = func(u, v) 
            
            # 移动扫描框
            scanner.move_to(axes_3d.c2p(u, v, z + 0.1))
    
            # 计算导数并更新箭头
            deriv = get_derivative(u)
            point = axes_3d.c2p(u, v, z)
            arrow_end = point + np.array([deriv, 0, 0])
            arrow.put_start_and_end_on(point, arrow_end)
            
            # 颜色逻辑
            if abs(deriv) > 1.5:
                arrow.set_color(RED)
            else:
                arrow.set_color(YELLOW)

        # =======================================================
        # [FIX 3 - 重点] 下面的所有代码，必须向左缩进，跳出 update 函数
        # =======================================================
        
        # 绑定 updater (这是在 construct 函数里执行，而不是在 update 函数里递归)
        scanner.add_updater(update_3d_elements)
        
        # 绑定数字的 updater
        x_num.add_updater(lambda m: m.set_value(x_tracker.get_value()))
        grad_num.add_updater(lambda m: m.set_value(get_derivative(x_tracker.get_value())))
        grad_num.add_updater(lambda m: m.set_color(RED if abs(m.get_value()) > 1.5 else WHITE))
        
        # 2D 曲线绘制
        graph_curve = always_redraw(lambda: axes_2d.plot(
            lambda x: get_derivative(x),
            x_range=[0, x_tracker.get_value()],
            color=YELLOW
        ))
        
        # 小红点
        dot_2d = always_redraw(lambda: Dot(
            point=axes_2d.c2p(x_tracker.get_value(), get_derivative(x_tracker.get_value())),
            color=RED,
            radius=0.08
        ))
        
        # 添加 2D 动态元素
        self.add_fixed_in_frame_mobjects(graph_curve, dot_2d)
        
        # 6. Action
        self.add(axes_3d, surface, scanner, arrow)
        
        self.play(
            x_tracker.animate.set_value(9),
            run_time=8,
            rate_func=linear 
        )
        self.wait()