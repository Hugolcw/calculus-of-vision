from manim import *
import numpy as np

class SobelMagnumOpus(ThreeDScene):
    def construct(self):
        # === 0. 教授级审美设置 ===
        self.camera.background_color = "#0B0F19" # 深邃蓝黑，比纯黑更有质感
        # 初始视角：上帝视角（俯视），看清矩阵
        self.set_camera_orientation(phi=0, theta=-90*DEGREES, zoom=0.65)

        # === 1. 定义数学内核 ===
        def func(u, v):
            # 经典的双 Sigmoid 阶跃
            val = 10 / (1 + np.exp(-5 * (u - 3.5))) - 10 / (1 + np.exp(-5 * (u - 8.5)))
            return val / 2.5

        def get_derivative(u):
            delta = 0.01 
            return (func(u + delta, 5) - func(u - delta, 5)) / (2 * delta)

        # === 2. 第一章：数字的本质 (The Grid) ===
        # 我们不再用 IntegerMatrix，而是手动构建一个 grid，
        # 这样它们既是数字，又是 3D 空间里的地基。
        
        grid_group = VGroup()
        val_trackers = [] # 存储数值以便后续变色
        
        for y in range(10):
            for x in range(10):
                val = int(func(x, y) * 2.5 + 0.5)
                # 数字对象
                num = Integer(val).scale(0.5).set_color(GREY_B)
                # 放在 3D 空间的 xy 平面上
                num.move_to(np.array([x, y, 0]))
                grid_group.add(num)
                
                # 如果是边缘处 (3,4 和 8,9)，稍微高亮一下，埋个伏笔
                if 2 < x < 5 or 7 < x < 10:
                    num.set_color(BLUE_C)

        # 调整 grid 位置，使其居中
        grid_group.center()
        
        # 标题
        title = Tex(r"\textbf{Chapter 1: The Raw Data}", font_size=48).to_edge(UP, buff=1)
        subtitle = Text("A grid of intensity values", font="Monospace", font_size=24, color=GREY).next_to(title, DOWN)
        
        self.add(grid_group)
        self.play(Write(title), FadeIn(subtitle))
        self.wait(1)

        # === 3. 第二章：维度的升华 (The Lift) ===
        
        # 变换标题
        self.play(
            Transform(title, Tex(r"\textbf{Chapter 2: Intensity as Height}", font_size=48).to_edge(UP, buff=1)),
            FadeOut(subtitle)
        )

        # 创建 3D 曲面
        axes = ThreeDAxes(
            x_range=[0, 10, 1], y_range=[0, 10, 1], z_range=[0, 6, 2],
            x_length=7, y_length=7, z_length=3.5,
            axis_config={"include_tip": False, "stroke_opacity": 0} # 隐藏轴线，只留地形
        ).move_to(grid_group.get_center()).shift(IN * 0.1) # 稍微往下一点，包住数字

        surface = Surface(
            lambda u, v: axes.c2p(u, v, func(u, v)), 
            u_range=[0, 10], v_range=[0, 10],
            resolution=(50, 50),
            should_make_jagged=False
        )
        surface.set_style(fill_opacity=0.6, stroke_color=BLUE_A, stroke_width=0.5)
        surface.set_fill_by_checkerboard(BLUE_E, BLUE_D, opacity=0.6)
        # 把它移到跟 Grid 对齐的位置 (Manim 的 Surface 默认不在原点，需要对齐)
        surface.match_x(grid_group).match_y(grid_group)

        # 核心镜头运动：从 2D 俯视 旋转到 3D 侧视
        # 这是一个 "Aha!" 时刻：数字还在底下，山峰升起来了
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=0.8, run_time=3)
        self.play(Create(surface), run_time=2)
        self.wait(1)

        # === 4. 第三章：微观机制 (The Mechanism) ===
        # 真正的科普：解释 [-1, 0, 1] 到底在干什么
        
        self.play(
            Transform(title, Tex(r"\textbf{Chapter 3: The Sobel Mechanism}", font_size=48).to_edge(UP, buff=1))
        )

        # 创建一个可视化的 Kernel (悬浮在空中的三个格子)
        #   [-1]  [ 0]  [ 1]
        kernel_box = VGroup()
        k_vals = [-1, 0, 1]
        for i, k in enumerate(k_vals):
            box = Square(side_length=1).set_stroke(YELLOW, 2).set_fill(BLACK, 0.5)
            txt = Integer(k).set_color(YELLOW).scale(0.8)
            g = VGroup(box, txt).move_to(np.array([i-1, 0, 0])) # 排列成行
            kernel_box.add(g)
        
        # 将 kernel 放到 3D 空间里合适的位置 (比如 x=3.5 的边缘处)
        # 我们要手动计算一下位置
        sample_u = 3.5 
        sample_z = func(sample_u, 5)
        pos_center = axes.c2p(sample_u, 5, sample_z + 1.5) # 悬浮在地形上方
        
        kernel_box.rotate(PI/2, axis=RIGHT).move_to(pos_center)
        
        # 添加连线：展示 Kernel 如何"吸取"下面像素的值
        lines = VGroup()
        offsets = [-1, 0, 1] # 对应 x-1, x, x+1
        points_on_surface = []
        
        for i, off in enumerate(offsets):
            # 地面上的点
            p_surf = axes.c2p(sample_u + off*0.2, 5, func(sample_u + off*0.2, 5)) 
            points_on_surface.append(p_surf)
            # 连线
            line = DashedLine(start=kernel_box[i].get_center(), end=p_surf, color=YELLOW_A)
            lines.add(line)

        self.play(FadeIn(kernel_box), Create(lines))
        
        # 动态公式：展示计算过程
        # (-1 * Low) + (1 * High) = Big Number
        calc_text = MathTex(
            r"(-1 \cdot \text{Low}) + (0 \cdot \text{Mid}) + (1 \cdot \text{High}) \approx \text{Slope}",
            color=YELLOW
        ).to_edge(DOWN, buff=1).add_background_rectangle()
        
        self.add_fixed_in_frame_mobjects(calc_text)
        self.play(Write(calc_text))
        self.wait(3)
        
        # 收起教学道具
        self.play(
            FadeOut(kernel_box), FadeOut(lines), FadeOut(calc_text), 
            FadeOut(title) # 隐藏标题，进入纯净扫描模式
        )

        # === 5. 终章：全景扫描 (The Synthesis) ===
        
        # 开启环境旋转
        self.begin_ambient_camera_rotation(rate=0.03)

        # 5.1 扫描器 (Neon Style)
        scanner = Square(side_length=1.5).set_stroke(WHITE, 4)
        glow = Square(side_length=1.5).set_stroke(TEAL, 15, opacity=0.3)
        scanner_grp = VGroup(glow, scanner).rotate(PI/2, axis=RIGHT)
        
        # 5.2 箭头 (Vector)
        arrow = Arrow3D(start=ORIGIN, end=UP, color=TEAL, thickness=0.04)
        
        # 5.3 底部宽幅示波器 (Cinema Scope)
        # 不再是小盒子，而是横跨底部的 HUD
        hud_bg = Rectangle(width=14, height=2.5, color=BLACK, fill_opacity=0.8).to_edge(DOWN, buff=0)
        hud_axes = Axes(
            x_range=[0, 10, 10], y_range=[-3, 3, 6], # 简化刻度
            x_length=13, y_length=2,
            axis_config={"include_tip": False, "stroke_opacity": 0.3}
        ).move_to(hud_bg)
        
        hud_label = Text("COMPUTED GRADIENT (DERIVATIVE)", font="Monospace", font_size=18, color=TEAL).next_to(hud_bg, UP, aligned_edge=LEFT)
        
        self.add_fixed_in_frame_mobjects(hud_bg, hud_axes, hud_label)
        self.play(FadeIn(hud_bg), Create(hud_axes), Write(hud_label))

        # 5.4 联动动画
        x_tracker = ValueTracker(0)
        
        def update_scan(mob):
            u = x_tracker.get_value()
            z = func(u, 5)
            # 3D 扫描框位置
            pos = axes.c2p(u, 5, z+0.1)
            scanner_grp.move_to(pos)
            
            # 箭头
            deriv = get_derivative(u)
            p_start = axes.c2p(u, 5, z)
            p_end = p_start + np.array([deriv * 0.6, 0, 0])
            arrow.put_start_and_end_on(p_start, p_end)
            
            # 颜色反馈：根据导数大小变色
            # 用 interpolate_color 实现平滑渐变，而不是突变
            color = interpolate_color(TEAL, RED, np.clip(abs(deriv)/1.5, 0, 1))
            
            scanner[0].set_color(color) # Core
            glow.set_color(color)       # Glow
            arrow.set_color(color)

        scanner_grp.add_updater(update_scan)
        
        # 示波器曲线
        trace = always_redraw(lambda: hud_axes.plot(
            lambda x: get_derivative(x),
            x_range=[0, x_tracker.get_value()],
            color=scanner[0].get_color(), # 颜色同步！
            stroke_width=3
        ))
        
        # 示波器光点
        dot = always_redraw(lambda: Dot(
            point=hud_axes.c2p(x_tracker.get_value(), get_derivative(x_tracker.get_value())),
            color=WHITE, radius=0.08
        ).set_glow_factor(1.5))

        self.add_fixed_in_frame_mobjects(trace, dot)
        self.add(scanner_grp, arrow)

        # 执行顺滑扫描
        self.play(
            x_tracker.animate.set_value(10),
            run_time=12,
            rate_func=linear
        )
        
        self.wait(2)