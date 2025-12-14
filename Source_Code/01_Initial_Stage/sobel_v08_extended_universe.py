from manim import *
import numpy as np

class SobelUniverse(ThreeDScene):
    def construct(self):
        # === 0. 全局配置 ===
        self.camera.background_color = "#0e1111" # 曜石黑
        
        # 定义核心数学函数 (用于生成地形)
        def func(u, v):
            # 两个 Sigmoid 形成的平滑台阶
            val = 10 / (1 + np.exp(-5 * (u - 3.5))) - 10 / (1 + np.exp(-5 * (u - 8.5)))
            return val / 2.5 # 高度范围 0 ~ 4

        # 导数函数 (用于计算颜色和曲线)
        def get_derivative(u):
            delta = 0.01 
            return (func(u + delta, 5) - func(u - delta, 5)) / (2 * delta)

        # =========================================================
        # 第一章：微观世界的算术 (The Micro Arithmetic)
        # 解释：卷积核到底是怎么算数的？为什么[-1, 0, 1]能测边缘？
        # =========================================================
        
        # 1.1 铺设 2D 像素网格
        # 我们只关注一个 3x3 的局部，展示计算细节
        grid_title = Tex(r"\textbf{Part I: The Micro Logic}", font_size=48).to_edge(UP, buff=1)
        self.play(Write(grid_title))

        # 创建一个 3x3 的示例像素块 (左暗右亮，模拟边缘)
        # 像素值: [0, 5, 10]
        pixel_vals = [
            [0, 5, 10], 
            [0, 5, 10], 
            [0, 5, 10]
        ]
        
        pixel_group = VGroup()
        for i in range(3):
            for j in range(3):
                # 像素方块
                val = pixel_vals[i][j]
                # 颜色：越亮越白
                color = interpolate_color(BLACK, WHITE, val/10)
                sq = Square(side_length=1.5).set_fill(color, 0.8).set_stroke(GREY, 1)
                sq.move_to(np.array([j - 1, 1 - i, 0]) * 1.5)
                
                # 像素数值
                num = Integer(val).set_color(BLACK if val > 5 else WHITE).move_to(sq)
                pixel_group.add(VGroup(sq, num))
        
        pixel_group.center()
        self.play(FadeIn(pixel_group, scale=0.8))
        self.wait(1)

        # 1.2 引入 Sobel 算子 (透明叠加)
        kernel_vals = [
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ]
        
        kernel_group = VGroup()
        for i in range(3):
            for j in range(3):
                k_val = kernel_vals[i][j]
                # 显示算子权重，用黄色
                txt = Integer(k_val).set_color(YELLOW).scale(1.5)
                txt.move_to(np.array([j - 1, 1 - i, 0]) * 1.5)
                kernel_group.add(txt)
        
        kernel_group.center()
        
        narrative = Text("Overlaying Sobel Kernel...", font="Monospace", font_size=24, color=YELLOW).to_edge(DOWN)
        self.play(Write(narrative))
        self.play(FadeIn(kernel_group, shift=UP))
        self.wait(1)

        # 1.3 演示卷积乘法 (Convolution Animation)
        # 高亮左右两列，展示 "右边 - 左边"
        left_col = VGroup(*[pixel_group[k] for k in [0, 3, 6]])
        right_col = VGroup(*[pixel_group[k] for k in [2, 5, 8]])
        
        self.play(
            pixel_group.animate.set_opacity(0.3), # 像素变暗
            kernel_group.animate.scale(1.2),      # 算子放大
            ReplacementTransform(narrative, Text("Calculating Difference...", font="Monospace", font_size=24, color=YELLOW).to_edge(DOWN))
        )
        
        # 公式推导动画
        math_exp = MathTex(
            r"Sum = (-1 \cdot 0) + (0 \cdot 5) + (1 \cdot 10)",
            color=WHITE
        ).to_edge(DOWN, buff=2)
        
        self.play(Write(math_exp))
        self.wait(1)
        
        result_text = MathTex(r"= 10 \text{ (High Gradient!)}", color=RED).next_to(math_exp, DOWN)
        self.play(Write(result_text))
        self.wait(2)

        # 清场，准备进入宏观世界
        self.play(
            FadeOut(pixel_group), FadeOut(kernel_group), 
            FadeOut(math_exp), FadeOut(result_text), FadeOut(grid_title),
            FadeOut(narrative)
        )

        # =========================================================
        # 第二章：宏观世界的地貌 (The Macro Terrain)
        # 解释：从单纯的数字变成连续的几何结构
        # =========================================================
        
        # 2.1 建立 3D 坐标系
        axes_3d = ThreeDAxes(
            x_range=[0, 10, 1], y_range=[0, 10, 1], z_range=[0, 6, 2],
            x_length=8, y_length=8, z_length=4,
            axis_config={"include_tip": False, "stroke_color": GREY_D}
        ).add_coordinates(font_size=16)

        # 2.2 生成地形 (Smooth Surface)
        # 使用高分辨率，让它看起来像流体
        surface = Surface(
            lambda u, v: axes_3d.c2p(u, v, func(u, v)), 
            u_range=[0, 10], v_range=[0, 10],
            resolution=(64, 64), # 极高画质
            should_make_jagged=False
        )
        # 风格：深空蓝，保留网格作为结构参考
        surface.set_style(fill_opacity=0.7, stroke_color=BLUE_A, stroke_width=0.3)
        surface.set_fill_by_checkerboard(BLUE_E, "#111111", opacity=0.7)

        # 2.3 镜头运动：从黑暗中浮现
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=0.7)
        self.play(Create(axes_3d, run_time=2), FadeIn(surface, run_time=2))
        
        chapter2_title = Tex(r"\textbf{Part II: The Geometry of Intensity}", font_size=40).to_corner(UL)
        self.add_fixed_in_frame_mobjects(chapter2_title)
        self.play(Write(chapter2_title))
        self.wait(1)
        self.play(FadeOut(chapter2_title))

        # =========================================================
        # 第三章：全息扫描 (The Holographic Scan)
        # 解释：解决“笨重方框”问题，使用“全息取景器”
        # =========================================================

        # 3.1 制作“全息取景器” (Holographic Viewfinder)
        # 我们不再画一个封闭的方框，而是画四个“角标 (Corners)”
        # 这样看起来更轻盈、更透气
        def create_viewfinder():
            # 定义一个角标形状
            corner = VMobject()
            corner.set_points_as_corners([UP*0.5, UP+RIGHT, UP+RIGHT*0.5])
            corner.set_color(TEAL).set_stroke(width=4)
            
            # 复制旋转得到四个角
            tl = corner.copy().rotate(0)  # Top Left
            tr = corner.copy().rotate(-PI/2) # Top Right
            br = corner.copy().rotate(-PI)   # Bottom Right
            bl = corner.copy().rotate(-3*PI/2) # Bottom Left
            
            # 组合
            viewfinder = VGroup(tl, tr, br, bl).arrange_in_grid(2, 2, buff=1.0)
            
            # 添加中心准星 (十字)
            cross = VGroup(
                Line(UP*0.2, DOWN*0.2), 
                Line(LEFT*0.2, RIGHT*0.2)
            ).set_stroke(WHITE, 2)
            
            # 添加“激光束” (从取景器垂直到地面的虚线)
            laser = DashedLine(start=ORIGIN, end=DOWN*2, color=TEAL_A)
            
            # 整体打包，并让它“躺平”在 xy 平面
            group = VGroup(viewfinder, cross, laser).rotate(PI/2, axis=RIGHT)
            return group

        scanner = create_viewfinder()
        
        # 3.2 准备 HUD 仪表盘 (底部宽屏)
        # 实时显示导数曲线
        hud_bg = Rectangle(width=12, height=2, color=BLACK, fill_opacity=0.8).to_edge(DOWN)
        hud_axes = Axes(
            x_range=[0, 10, 10], y_range=[-3, 3, 6],
            x_length=11, y_length=1.5,
            axis_config={"include_tip": False, "stroke_opacity": 0.5}
        ).move_to(hud_bg)
        
        hud_label = Text("GRADIENT AMPLITUDE (f'(x))", font="Monospace", font_size=16, color=TEAL).next_to(hud_bg, UP, aligned_edge=LEFT)
        
        self.add_fixed_in_frame_mobjects(hud_bg, hud_axes, hud_label)
        self.play(FadeIn(hud_bg), Create(hud_axes), Write(hud_label))

        # 3.3 动画核心逻辑
        x_tracker = ValueTracker(0)
        
        # 开启环境旋转，增加电影感
        self.begin_ambient_camera_rotation(rate=0.03)

        def update_scan(mob):
            u = x_tracker.get_value()
            z_surface = func(u, 5) # 地形高度
            
            # 1. 移动取景器
            # 让它悬浮在地形上方 0.5 的位置，不要贴死，显得有空间感
            hover_height = z_surface + 1.0
            pos = axes_3d.c2p(u, 5, hover_height)
            mob.move_to(pos)
            
            # 2. 调整激光束长度
            # 激光束始终连着取景器中心和地形表面
            # mob[2] 是我们在 create_viewfinder 里加的 laser
            laser_start = axes_3d.c2p(u, 5, hover_height)
            laser_end = axes_3d.c2p(u, 5, z_surface)
            mob[2].put_start_and_end_on(laser_start, laser_end)
            
            # 3. 颜色逻辑 (根据导数变色)
            deriv = get_derivative(u)
            # 颜色映射：0(Teal) -> High(Red)
            # 使用 sigmoid 函数让颜色变化更灵敏
            intensity = np.clip(abs(deriv)/1.5, 0, 1)
            color = interpolate_color(TEAL, RED, intensity)
            
            mob[0].set_color(color) # 边框变色
            mob[2].set_color(color) # 激光变色

        scanner.add_updater(update_scan)
        
        # 实时绘制曲线
        trace = always_redraw(lambda: hud_axes.plot(
            lambda x: get_derivative(x),
            x_range=[0, x_tracker.get_value()],
            color=scanner[0].get_color(), # 颜色同步
            stroke_width=2
        ))
        
        # 光点
        dot = always_redraw(lambda: Dot(
            point=hud_axes.c2p(x_tracker.get_value(), get_derivative(x_tracker.get_value())),
            color=WHITE, radius=0.05
        ).set_glow_factor(2))

        self.add_fixed_in_frame_mobjects(trace, dot)
        self.add(scanner)

        # 3.4 执行扫描 (慢速，强调细节)
        self.play(
            x_tracker.animate.set_value(10),
            run_time=12,
            rate_func=linear
        )
        
        # 3.5 结尾定格
        final_text = Text("Edge Detected at Max Gradient", font="Monospace", font_size=32, color=WHITE).to_corner(UR, buff=1)
        self.add_fixed_in_frame_mobjects(final_text)
        self.play(Write(final_text))
        
        self.wait(3)