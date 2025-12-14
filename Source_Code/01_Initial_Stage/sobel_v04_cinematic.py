from manim import *
import numpy as np

class SobelCinematic(ThreeDScene):
    def construct(self):
        # --- 1. 影院级环境设置 ---
        self.camera.background_color = "#111111" # 更深邃的黑
        
        # 初始视角：稍微低一点，仰视更有压迫感
        self.set_camera_orientation(phi=75 * DEGREES, theta=-30 * DEGREES, zoom=0.6)
        
        # 开启环境光旋转（关键！让 3D 活起来的灵魂）
        # 摄像机会非常缓慢地自动旋转，产生视差立体感
        self.begin_ambient_camera_rotation(rate=0.05) 

        # --- 2. 高精度数学曲面 ---
        def func(u, v):
            val = 10 / (1 + np.exp(-5 * (u - 3.5))) - 10 / (1 + np.exp(-5 * (u - 8.5)))
            return val / 2.5
        
        def get_derivative(u):
            delta = 0.01 
            return (func(u + delta, 5) - func(u - delta, 5)) / (2 * delta)

        axes_3d = ThreeDAxes(
            x_range=[0, 10, 1], y_range=[0, 10, 1], z_range=[0, 6, 2],
            x_length=8, y_length=8, z_length=4,
            axis_config={"stroke_color": GREY_C, "stroke_width": 2}
        ).add_coordinates(font_size=20)

        # 提高分辨率到 48x48 (你的显卡跑得动)，让曲面丝般顺滑
        surface = Surface(
            lambda u, v: axes_3d.c2p(u, v, func(u, v)), 
            u_range=[0, 10], v_range=[0, 10],
            resolution=(48, 48), # 高分辨率
            should_make_jagged=False
        )
        
        # 3b1b 风格配色：深蓝 + 青色网格
        # fill_opacity=0.7 让它更有实体感，不再像幽灵
        surface.set_style(fill_opacity=0.7, stroke_color=BLUE_C, stroke_width=0.8)
        surface.set_fill_by_checkerboard(BLUE_E, BLUE_D, opacity=0.7)

        # --- 3. 制作“辉光”扫描器 (The Neon Scanner) ---
        # 原理：叠加三层方框，内层亮白，外层红且透明，模拟光晕
        def create_neon_box():
            box_group = VGroup()
            # 核心层：细，亮白
            core = Square(side_length=1.5).set_stroke(WHITE, width=2)
            # 内发光层：稍粗，红色，半透明
            glow1 = Square(side_length=1.5).set_stroke(RED, width=8, opacity=0.5)
            # 外发光层：很粗，红色，很透明
            glow2 = Square(side_length=1.5).set_stroke(RED, width=20, opacity=0.2)
            
            box_group.add(glow2, glow1, core)
            box_group.rotate(PI/2, axis=RIGHT)
            return box_group

        scanner = create_neon_box()
        
        # 箭头也加粗一点
        arrow = Arrow3D(start=ORIGIN, end=UP, color=YELLOW, thickness=0.03)

        # --- 4. HUD 仪表盘 (保持简洁) ---
        # 3b1b 风格通常不喜欢太复杂的 HUD，我们把字体做精细点
        title_tex = Tex(r"\textbf{Sobel Gradient Scan}", font_size=40).to_corner(UL).set_color(BLUE_B)
        val_tex = MathTex(r"f'(x) =", font_size=36).next_to(title_tex, DOWN, aligned_edge=LEFT)
        num_decimal = DecimalNumber(0, num_decimal_places=2, font_size=36, color=YELLOW).next_to(val_tex, RIGHT)
        
        self.add_fixed_in_frame_mobjects(title_tex, val_tex, num_decimal)

        # --- 5. 动画驱动 (使用平滑曲线) ---
        x_tracker = ValueTracker(1)
        
        def update_scene(mob):
            u = x_tracker.get_value()
            v = 5
            z = func(u, v)
            
            # 更新扫描器位置
            scanner.move_to(axes_3d.c2p(u, v, z + 0.1))
            
            # 更新箭头
            deriv = get_derivative(u)
            pt_start = axes_3d.c2p(u, v, z)
            pt_end = pt_start + np.array([deriv, 0, 0])
            arrow.put_start_and_end_on(pt_start, pt_end)
            
            # 颜色动态变化 (辉光也跟着变色)
            if abs(deriv) > 1.0:
                arrow.set_color(RED)
                scanner[0].set_color(RED) # 外发光
                scanner[1].set_color(RED)
            else:
                arrow.set_color(YELLOW)
                scanner[0].set_color(YELLOW)
                scanner[1].set_color(YELLOW)

        scanner.add_updater(update_scene)
        num_decimal.add_updater(lambda m: m.set_value(get_derivative(x_tracker.get_value())))

        # --- 6. 演出开始 ---
        self.add(axes_3d, surface, scanner, arrow)
        
        # 关键优化：使用 smooth (缓入缓出) 替代 linear
        # 这样扫描框启动和停止时会很柔和，像真实的机器臂
        self.play(
            x_tracker.animate.set_value(9),
            run_time=8,
            rate_func=smooth 
        )
        
        # 扫描结束后，镜头拉近看一眼细节 (Focus)
        self.move_camera(phi=60*DEGREES, theta=-60*DEGREES, zoom=1.2, run_time=3)
        
        self.wait()