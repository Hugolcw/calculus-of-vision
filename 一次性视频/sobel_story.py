from manim import *
import numpy as np

class SobelStory(ThreeDScene):
    def construct(self):
        # --- 1. 影院级环境设置 (Cinematic Setup) ---
        self.camera.background_color = "#111111"
        self.set_camera_orientation(phi=70 * DEGREES, theta=-30 * DEGREES, zoom=0.7)
        self.begin_ambient_camera_rotation(rate=0.03) # 缓慢旋转，制造空间感

        # --- 2. 构建数学地形 (The Terrain) ---
        def func(u, v):
            # Sigmoid 组合函数：模拟图像光强
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

        surface = Surface(
            lambda u, v: axes_3d.c2p(u, v, func(u, v)), 
            u_range=[0, 10], v_range=[0, 10],
            resolution=(48, 48),
            should_make_jagged=False
        )
        surface.set_style(fill_opacity=0.7, stroke_color=BLUE_C, stroke_width=0.8)
        surface.set_fill_by_checkerboard(BLUE_E, BLUE_D, opacity=0.7)

        # --- 3. 辉光扫描器与箭头 ---
        scanner = Square(side_length=1.5).set_stroke(WHITE, width=3)
        scanner_glow = Square(side_length=1.5).set_stroke(RED, width=15, opacity=0.3)
        scanner_group = VGroup(scanner_glow, scanner).rotate(PI/2, axis=RIGHT)
        
        arrow = Arrow3D(start=ORIGIN, end=UP, color=YELLOW, thickness=0.04)

        # --- 4. 信息增强层 (Info Layer) - 关键升级 ---
        self.add_fixed_in_frame_mobjects() # 开启 HUD 模式

        # [区域 A] 理论核心 (右上角)
        # 展示 Sobel 算子矩阵和导数公式，增加学术感
        matrix_tex = MathTex(
            r"K_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}"
        ).scale(0.6).to_corner(UR, buff=0.5)
        
        formula_tex = MathTex(
            r"G_x \approx \frac{\partial f}{\partial x}"
        ).scale(0.7).next_to(matrix_tex, DOWN, buff=0.3)
        
        theory_group = VGroup(matrix_tex, formula_tex).set_color(BLUE_B)
        self.add_fixed_in_frame_mobjects(theory_group)

        # [区域 B] 动态解说词 (左上角)
        # 用来讲述当前发生的事情，类似于字幕
        narrative_box = VGroup() # 占位符
        
        def update_narrative(text_str, subtext_str=""):
            # 清除旧的
            self.remove(narrative_box)
            narrative_box.submobjects = []
            
            # 创建新的
            title = Text(text_str, font_size=32, weight=BOLD).to_corner(UL, buff=0.5).set_color(YELLOW)
            subtitle = Text(subtext_str, font_size=24, color=GREY_A).next_to(title, DOWN, aligned_edge=LEFT)
            
            narrative_box.add(title, subtitle)
            self.add_fixed_in_frame_mobjects(narrative_box)

        # 初始化第一句解说
        update_narrative("Phase 1: Input Image", "Visualizing Pixel Intensity as Height")

        # [区域 C] 实时检测警告 (屏幕中心下方)
        warning_text = Text("EDGE DETECTED", font_size=48, color=RED, weight=BOLD)
        warning_text.to_edge(DOWN, buff=1)
        warning_bg = SurroundingRectangle(warning_text, color=RED, fill_opacity=0.2, buff=0.2)
        warning_group = VGroup(warning_bg, warning_text)
        # 初始隐藏
        warning_group.set_opacity(0) 
        self.add_fixed_in_frame_mobjects(warning_group)

        # --- 5. 动画驱动 ---
        x_tracker = ValueTracker(1)
        
        def update_scene(mob):
            u = x_tracker.get_value()
            z = func(u, 5)
            point = axes_3d.c2p(u, 5, z)
            
            # 移动扫描器
            scanner_group.move_to(axes_3d.c2p(u, 5, z + 0.1))
            
            # 移动箭头
            deriv = get_derivative(u)
            arrow.put_start_and_end_on(point, point + np.array([deriv, 0, 0]))
            
            # 逻辑判断：状态切换
            if abs(deriv) > 1.2:
                # 触发边缘警告
                arrow.set_color(RED)
                scanner_glow.set_color(RED)
                warning_group.set_opacity(1) # 显示警告
            else:
                # 平坦区域
                arrow.set_color(YELLOW)
                scanner_glow.set_color(YELLOW)
                warning_group.set_opacity(0) # 隐藏警告

            # 动态更新解说词 (根据位置硬编码 narrative)
            # 这是一种简单的状态机写法
            if u < 2.5:
                update_narrative("Phase 1: Scanning", "Searching for pixel intensity changes...")
            elif 2.5 <= u < 4.5:
                update_narrative("Phase 2: Rising Edge", "Gradient > 0 (Light Intensity Increases)")
            elif 4.5 <= u < 7.5:
                update_narrative("Phase 3: Plateau", "Gradient ≈ 0 (No Change in Intensity)")
            elif u >= 7.5:
                update_narrative("Phase 4: Falling Edge", "Gradient < 0 (Light Intensity Decreases)")

        scanner_group.add_updater(update_scene)

        # --- 6. 开始演出 ---
        self.add(axes_3d, surface, scanner_group, arrow)
        
        # 缓慢扫描，让观众看清楚字
        self.play(
            x_tracker.animate.set_value(9),
            run_time=10,
            rate_func=linear
        )
        
        self.wait()