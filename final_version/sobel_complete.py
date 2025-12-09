from manim import *
import numpy as np

# ============================================================================
# 全局配置与语义定义 (Config & Semantics)
# ============================================================================

# 颜色语义池
COLOR_CONTINUOUS = BLUE_C      # 理想数学
COLOR_DISCRETE = YELLOW_C      # 工程采样
COLOR_DIFF = RED_C             # 微分/变化/高频
COLOR_SMOOTH = TEAL_C          # 平滑/保持/低频
COLOR_GHOST = GREY_B           # 过去的影子
OPACITY_GHOST = 0.2            # 幽灵透明度

# LaTeX模板配置
TEX_TEMPLATE = TexTemplate()
TEX_TEMPLATE.add_to_preamble(r"\usepackage{amsmath}")


# ============================================================================
# 工具函数 (Helper Functions)
# ============================================================================

def get_downsampled_array(image_path, rate=10):
    """
    加载图片并降采样，防止Scene 4渲染爆炸
    """
    try:
        # 尝试使用ImageMobject加载
        img = ImageMobject(image_path)
        pixel_array = img.get_pixel_array()
        # 降采样: 每rate个像素取1个
        downsampled = pixel_array[::rate, ::rate]
        return downsampled
    except:
        # 如果图片不存在，生成一个测试图像
        # 创建一个简单的测试图像: 左暗右亮的边缘
        width, height = 200, 200
        arr = np.zeros((height, width, 3), dtype=np.uint8)
        # 中间部分为白色，两边为黑色
        center_x = width // 2
        for y in range(height):
            for x in range(width):
                # 使用sigmoid创建平滑过渡
                intensity = int(255 / (1 + np.exp(-0.1 * (x - center_x))))
                arr[y, x] = [intensity, intensity, intensity]
        return arr[::rate, ::rate]


# ============================================================================
# 主场景类
# ============================================================================

class SobelUniverse(ThreeDScene):
    def construct(self):
        # 全局设置
        self.camera.background_color = "#0e1111"
        
        # 按顺序调度各个场景
        self.setup_scene_1_discrete()
        self.transition_1_2()
        self.setup_scene_2_taylor()
        self.transition_2_3()
        self.setup_scene_3_5_noise()  # 新增：噪声的战争
        self.transition_3_5_to_3()
        self.setup_scene_3_matrices()
        self.transition_3_4()
        self.setup_scene_4_vision()
        self.transition_4_5()
        self.setup_scene_5_outro()

    # ========================================================================
    # Scene 1: 离散现实 (Discrete Reality)
    # ========================================================================
    
    def setup_scene_1_discrete(self):
        """Scene 1: 从连续到离散的视觉对比"""
        
        # Act 1: 理想展示 - 连续函数
        axes = Axes(
            x_range=[-1, 11, 1],
            y_range=[-1, 5, 1],
            x_length=12,
            y_length=5,
            axis_config={"stroke_opacity": 0.5, "stroke_width": 1},
            tips=False
        )
        
        # 正弦组合函数: f(x) = 2 + sin(x) + 0.5*sin(2*x)
        def continuous_func(x):
            return 2 + np.sin(x * 0.5) + 0.5 * np.sin(x)
        
        func_continuous = axes.plot(
            continuous_func,
            x_range=[0, 10],
            color=COLOR_CONTINUOUS,
            stroke_width=3
        )
        
        # 切线追踪器
        tangent_tracker = ValueTracker(5)
        
        def get_tangent():
            x = tangent_tracker.get_value()
            y = continuous_func(x)
            dx = 0.01
            dy = (continuous_func(x + dx) - continuous_func(x - dx)) / (2 * dx)
            point = axes.c2p(x, y)
            line = Line(
                axes.c2p(x - 1, y - dy),
                axes.c2p(x + 1, y + dy),
                color=COLOR_DIFF,
                stroke_width=2
            )
            return line
        
        tangent_line = always_redraw(get_tangent)
        
        # 斜率显示
        slope_text = always_redraw(lambda: DecimalNumber(
            (continuous_func(tangent_tracker.get_value() + 0.01) - 
             continuous_func(tangent_tracker.get_value() - 0.01)) / 0.02,
            num_decimal_places=2,
            color=COLOR_DIFF
        ).next_to(tangent_line, UP))
        
        # 播放动画
        self.play(Create(axes), Create(func_continuous), run_time=1)
        self.add(tangent_line, slope_text)
        self.play(tangent_tracker.animate.set_value(8), run_time=2)
        
        # Act 2: 幽灵变换 - 离散采样
        ghost_graph = func_continuous.copy()
        # 初始状态：让幽灵线完全重合，且不透明，这样添加时肉眼看不出变化
        ghost_graph.set_stroke(color=COLOR_CONTINUOUS, width=3, opacity=1)
        
        # 创建离散采样点
        num_samples = 10
        x_samples = np.linspace(0, 10, num_samples)
        discrete_stems = VGroup()
        
        for x in x_samples:
            y = continuous_func(x)
            start_point = axes.c2p(x, 0)
            end_point = axes.c2p(x, y)
            stem = Line(start_point, end_point, color=COLOR_DISCRETE, stroke_width=3)
            dot = Dot(end_point, color=COLOR_DISCRETE, radius=0.08)
            discrete_stems.add(stem, dot)
        
        # 【关键修复】先添加物体，再播放动画
        self.add(ghost_graph) 
        
        self.play(
            # 原函数变透明消失
            func_continuous.animate.set_opacity(0),
            # 幽灵线变成灰色虚影
            ghost_graph.animate.set_stroke(color=COLOR_GHOST, width=1, opacity=OPACITY_GHOST),
            # 采样杆生长出来
            Create(discrete_stems),
            run_time=2
        )
        self.wait(0.5)
        
        # ==========================================
        # Act 3: 聚焦困境 (修复版)
        # ==========================================
        focus_point = axes.c2p(5, continuous_func(5))
        
        # 1. 把场景里的所有东西打个包
        scene_group = VGroup(axes, func_continuous, ghost_graph, discrete_stems, tangent_line, slope_text)
        
        # 2. 问号直接生成在屏幕中心上方
        question_mark = Text("?", font_size=72, color=YELLOW).move_to(UP * 1.5)
        
        self.play(
            # 【核心修复】：不要动相机(self.camera.frame)，改为动物体(scene_group)
            # 以 focus_point 为中心放大 2.5 倍，并移到屏幕中心
            scene_group.animate.scale(2.5, about_point=focus_point).shift(ORIGIN - focus_point),
            Write(question_mark),
            run_time=2
        )
        self.wait(1)
        
        # 清理
        self.play(
            FadeOut(scene_group),
            FadeOut(question_mark),
            run_time=1
        )
    def transition_1_2(self):
        """场景1到场景2的过渡"""
        self.wait(0.5)

    # ========================================================================
    # Scene 2: 泰勒桥梁 (The Taylor Bridge)
    # ========================================================================
    
    def setup_scene_2_taylor(self):
        """Scene 2: 泰勒展开推导中心差分"""
        
        # Act 1: 分步揭示泰勒公式
        # 前向展开: f(x+1)
        taylor_forward = MathTex(
            "f(x+1)", "\\approx", "f(x)", "+", "f'(x)", "+", "\\frac{1}{2}f''(x)",
            substrings_to_isolate=["f(x)", "f'(x)", "f''(x)"],
            font_size=48
        ).shift(UP * 2)
        
        # 后向展开: f(x-1)
        taylor_backward = MathTex(
            "f(x-1)", "\\approx", "f(x)", "-", "f'(x)", "+", "\\frac{1}{2}f''(x)",
            substrings_to_isolate=["f(x)", "f'(x)", "f''(x)"],
            font_size=48
        ).next_to(taylor_forward, DOWN, buff=0.8)
        
        # 抛物线辅助说明
        axes = Axes(x_range=[-1, 3, 1], y_range=[-1, 3, 1], 
                   x_length=4, y_length=3, tips=False)
        parabolas = VGroup()
        for offset, color in [(1, BLUE), (-1, RED)]:
            parabola = axes.plot(
                lambda x: 1 + 0.5 * (x - offset) ** 2,
                x_range=[-0.5, 2.5],
                color=color,
                stroke_width=2
            ).set_stroke(opacity=0.5)
            parabolas.add(parabola)
        
        self.play(
            Write(taylor_forward[0:2]), run_time=1
        )
        self.play(
            Write(taylor_forward[2:]), 
            LaggedStart(*[Write(parabolas[i]) for i in range(2)], lag_ratio=0.3),
            run_time=2
        )
        self.wait(0.5)
        
        self.play(
            Write(taylor_backward[0:2]), run_time=1
        )
        self.play(
            Write(taylor_backward[2:]), run_time=2
        )
        self.wait(1)
        
        # Act 2: 视觉对撞 - 抵消相同项
        # 使用 get_part_by_tex 来可靠地查找公式部分（避免LaTeX索引陷阱）
        # 如果找不到，则尝试通过索引查找（向后兼容）
        try:
            f_x_forward_part = taylor_forward.get_part_by_tex("f(x)")
            f_x_backward_part = taylor_backward.get_part_by_tex("f(x)")
        except:
            # 如果 get_part_by_tex 不支持，使用索引（需要调试时确认）
            f_x_forward_part = taylor_forward[2] if len(taylor_forward) > 2 else taylor_forward
            f_x_backward_part = taylor_backward[2] if len(taylor_backward) > 2 else taylor_backward
        
        try:
            f_double_forward_part = taylor_forward.get_part_by_tex("f''(x)")
            f_double_backward_part = taylor_backward.get_part_by_tex("f''(x)")
        except:
            # 如果找不到，尝试查找包含 f'' 的部分
            f_double_forward_part = taylor_forward[-1] if len(taylor_forward) > 0 else taylor_forward
            f_double_backward_part = taylor_backward[-1] if len(taylor_backward) > 0 else taylor_backward
        
        # 创建高亮框来标记相同项
        f_x_forward_rect = SurroundingRectangle(f_x_forward_part, color=COLOR_DIFF, buff=0.1)
        f_x_backward_rect = SurroundingRectangle(f_x_backward_part, color=COLOR_DIFF, buff=0.1)
        
        self.play(
            Create(f_x_forward_rect),
            Create(f_x_backward_rect),
            run_time=0.5
        )
        self.wait(0.5)
        
        self.play(
            FadeOut(f_x_forward_rect),
            FadeOut(f_x_backward_rect),
            f_x_forward_part.animate.set_opacity(0),
            f_x_backward_part.animate.set_opacity(0),
            run_time=1
        )
        
        # 同样处理 f''(x) 项
        f_double_prime_forward_rect = SurroundingRectangle(f_double_forward_part, color=COLOR_DIFF, buff=0.1)
        f_double_prime_backward_rect = SurroundingRectangle(f_double_backward_part, color=COLOR_DIFF, buff=0.1)
        
        self.play(
            Create(f_double_prime_forward_rect),
            Create(f_double_prime_backward_rect),
            run_time=0.5
        )
        self.wait(0.5)
        self.play(
            FadeOut(f_double_prime_forward_rect),
            FadeOut(f_double_prime_backward_rect),
            f_double_forward_part.animate.set_opacity(0),
            f_double_backward_part.animate.set_opacity(0),
            run_time=1
        )
        
        # Act 3: 算子结晶 - 形成差分公式
        # 计算 f(x+1) - f(x-1)
        diff_formula = MathTex(
            "f'(x)", "\\approx", "\\frac{f(x+1) - f(x-1)}{2}",
            font_size=48
        ).move_to(ORIGIN)
        
        # 提取系数
        kernel_x = VGroup(
            Integer(-1, color=COLOR_DIFF),
            Integer(0, color=WHITE),
            Integer(1, color=COLOR_DIFF)
        ).arrange(RIGHT, buff=0.5)
        
        self.play(
            TransformMatchingTex(
                VGroup(taylor_forward, taylor_backward),
                diff_formula
            ),
            FadeOut(parabolas),
            run_time=2
        )
        self.wait(1)
        
        # 系数飞出
        coefficient_text = MathTex("[-1, 0, 1]", font_size=36).next_to(diff_formula, DOWN)
        self.play(Write(coefficient_text), run_time=1)
        self.play(
            Transform(coefficient_text, kernel_x.scale(1.5).to_edge(DOWN)),
            run_time=1.5
        )
        self.wait(1)
        
        # 清理
        self.play(FadeOut(VGroup(diff_formula, coefficient_text, kernel_x)), run_time=1)

    def transition_2_3(self):
        """场景2到场景3的过渡"""
        self.wait(0.5)

    # ========================================================================
    # Scene 3.5: 噪声的战争 (The War on Noise) - 新增
    # ========================================================================
    
    def setup_scene_3_5_noise(self):
        """Scene 3.5: 噪声的战争 - 为什么需要平滑"""
        
        # Act 1: 现实的残酷 - 展示带噪声的信号
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-2, 4, 1],
            x_length=10,
            y_length=4,
            axis_config={"stroke_opacity": 0.5, "stroke_width": 1},
            tips=False
        )
        
        # 理想信号
        def clean_signal(x):
            return 1 + np.sin(x * 0.8)
        
        clean_graph = axes.plot(
            clean_signal,
            x_range=[0, 10],
            color=COLOR_CONTINUOUS,
            stroke_width=3
        )
        clean_label = Text("理想信号", font_size=24, color=COLOR_CONTINUOUS).to_corner(UL, buff=0.5)
        
        # 生成带噪声的信号（固定随机种子以保证可重复）
        np.random.seed(42)
        x_noisy = np.linspace(0, 10, 50)
        # 先生成所有噪声值
        noise_values = 0.4 * np.random.normal(0, 1, len(x_noisy))
        y_noisy = [clean_signal(x) + noise for x, noise in zip(x_noisy, noise_values)]
        noisy_points = VGroup()
        for x, y in zip(x_noisy, y_noisy):
            point = Dot(axes.c2p(x, y), color=COLOR_DIFF, radius=0.04)
            noisy_points.add(point)
        
        noisy_label = Text("真实信号（含噪声）", font_size=24, color=COLOR_DIFF).next_to(clean_label, DOWN, aligned_edge=LEFT)
        
        self.play(
            Create(axes),
            Create(clean_graph),
            Write(clean_label),
            run_time=1
        )
        self.wait(0.5)
        
        self.play(
            Create(noisy_points),
            Write(noisy_label),
            run_time=1.5
        )
        self.wait(1)
        
        # Act 2: 直接求导的灾难
        # 对噪声信号求差分
        diff_points = VGroup()
        for i in range(len(x_noisy) - 1):
            x_mid = (x_noisy[i] + x_noisy[i+1]) / 2
            dy = (y_noisy[i+1] - y_noisy[i]) / (x_noisy[i+1] - x_noisy[i])
            # 放大导数以便可视化
            dy_scaled = dy * 2
            start_point = axes.c2p(x_mid, 0)
            end_point = axes.c2p(x_mid, dy_scaled)
            diff_line = Line(start_point, end_point, color=RED, stroke_width=2)
            diff_points.add(diff_line)
        
        disaster_text = Text("直接求导：噪声被放大！", font_size=32, color=RED).move_to(ORIGIN + DOWN * 2.5)
        
        self.play(
            FadeOut(clean_graph, clean_label),
            axes.animate.shift(UP * 1.5),
            noisy_points.animate.shift(UP * 1.5),
            noisy_label.animate.shift(UP * 1.5),
            run_time=1
        )
        
        # 创建新的坐标轴用于显示导数
        axes_diff = Axes(
            x_range=[0, 10, 1],
            y_range=[-3, 3, 1],
            x_length=10,
            y_length=3,
            axis_config={"stroke_opacity": 0.5, "stroke_width": 1},
            tips=False
        ).shift(DOWN * 1.5)
        
        self.play(
            Create(axes_diff),
            Create(diff_points),
            Write(disaster_text),
            run_time=2
        )
        self.wait(1.5)
        
        # Act 3: 高斯护盾
        # 展示高斯滤波的效果
        self.play(
            FadeOut(diff_points, disaster_text, axes_diff),
            axes.animate.shift(DOWN * 1.5),
            noisy_points.animate.shift(DOWN * 1.5),
            noisy_label.animate.shift(DOWN * 1.5),
            run_time=1
        )
        
        # 高斯平滑后的信号（预计算）
        def gaussian_smooth(x):
            # 简单的移动平均模拟高斯平滑
            window = 0.5
            total = 0
            count = 0
            for i, xi in enumerate(x_noisy):
                if abs(xi - x) < window:
                    weight = np.exp(-((xi - x) / (window/2)) ** 2)
                    total += y_noisy[i] * weight
                    count += weight
            return total / count if count > 0 else clean_signal(x)
        
        smoothed_graph = axes.plot(
            gaussian_smooth,
            x_range=[0, 10],
            color=COLOR_SMOOTH,
            stroke_width=3
        )
        
        gaussian_label = Text("高斯平滑后", font_size=24, color=COLOR_SMOOTH).next_to(noisy_label, DOWN, aligned_edge=LEFT)
        
        # 高斯函数可视化
        gaussian_axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 1.2, 0.2],
            x_length=3,
            y_length=2,
            axis_config={"stroke_opacity": 0.5},
            tips=False
        ).to_corner(UR, buff=0.5)
        
        gaussian_func = gaussian_axes.plot(
            lambda x: np.exp(-x**2 / 2),
            x_range=[-3, 3],
            color=COLOR_SMOOTH,
            stroke_width=3
        )
        gaussian_title = Text("高斯函数", font_size=20, color=COLOR_SMOOTH).next_to(gaussian_axes, UP, buff=0.2)
        
        self.play(
            Create(smoothed_graph),
            Write(gaussian_label),
            Create(gaussian_axes),
            Create(gaussian_func),
            Write(gaussian_title),
            run_time=2
        )
        self.wait(1.5)
        
        shield_text = Text("在求导的利刃出鞘之前，\n我们需要高斯的盾牌来过滤杂音", 
                          font_size=28, color=WHITE).move_to(ORIGIN + DOWN * 2)
        self.play(Write(shield_text), run_time=2)
        self.wait(1.5)
        
        # 清理
        self.play(
            FadeOut(VGroup(axes, clean_graph, noisy_points, noisy_label, smoothed_graph, 
                          gaussian_label, gaussian_axes, gaussian_func, gaussian_title, shield_text)),
            run_time=1
        )
    
    def transition_3_5_to_3(self):
        """Scene 3.5到Scene 3的过渡"""
        self.wait(0.5)

    # ========================================================================
    # Scene 3: 算子解构 (Operator Anatomy)
    # ========================================================================
    
    def setup_scene_3_matrices(self):
        """Scene 3: Sobel算子的构造 (修复中文LaTeX报错版)"""
        
        # Act 1: 身份确认 - 展示两个向量
        kernel_x = Matrix([[-1, 0, 1]], element_alignment_corner=ORIGIN)
        kernel_x.set_color(COLOR_DIFF)
        kernel_x_label = Brace(kernel_x, DOWN)
        
        # 【修复 1】：使用 Text 而不是 get_text (避免 LaTeX 编译中文)
        kernel_x_text = Text("微分/高通", font_size=24, color=COLOR_DIFF).next_to(kernel_x_label, DOWN)
        
        kernel_x_group = VGroup(kernel_x, kernel_x_label, kernel_x_text)
        kernel_x_group.to_edge(LEFT).shift(UP)
        
        kernel_y = Matrix([[1], [2], [1]], element_alignment_corner=ORIGIN)
        kernel_y.set_color(COLOR_SMOOTH)
        kernel_y_label = Brace(kernel_y, RIGHT)
        
        # 【修复 2】：使用 Text 而不是 get_text
        kernel_y_text = Text("平滑/低通", font_size=24, color=COLOR_SMOOTH).next_to(kernel_y_label, RIGHT)
        
        kernel_y_group = VGroup(kernel_y, kernel_y_label, kernel_y_text)
        kernel_y_group.to_edge(UP)
        
        self.play(
            FadeIn(kernel_x_group, shift=RIGHT),
            run_time=1
        )
        self.play(
            FadeIn(kernel_y_group, shift=DOWN),
            run_time=1
        )
        self.wait(1)
        
        # Act 2: 外积演示 - 矩阵聚变
        # 计算外积: [-1,0,1] × [1,2,1]^T
        sobel_matrix_values = [
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ]
        
        kernel_sobel = IntegerMatrix(
            sobel_matrix_values,
            element_alignment_corner=ORIGIN
        ).scale(0.8)
        
        # 移动两个向量到中心，准备合并
        self.play(
            kernel_x_group.animate.move_to(ORIGIN + LEFT * 2),
            kernel_y_group.animate.move_to(ORIGIN + UP * 2),
            run_time=2
        )
        
        # 演示广播过程
        multiplication_sign = MathTex("\\times", font_size=48).move_to(ORIGIN)
        self.play(Write(multiplication_sign), run_time=0.5)
        self.wait(0.5)
        
        # 变换为最终矩阵
        result_text = MathTex("=", font_size=48).next_to(multiplication_sign, RIGHT, buff=0.5)
        kernel_sobel.next_to(result_text, RIGHT, buff=0.5)
        
        # 颜色融合效果
        kernel_sobel.set_color_by_gradient(COLOR_DIFF, GOLD, COLOR_SMOOTH)
        
        self.play(
            Write(result_text),
            Transform(
                VGroup(kernel_x_group, kernel_y_group, multiplication_sign),
                kernel_sobel
            ),
            run_time=2
        )
        self.wait(1)
        
        # Act 3: 结构高亮
        # 高亮边缘和中心
        center_rect = SurroundingRectangle(
            kernel_sobel.get_entries()[4],  # 中心元素 (0)
            color=YELLOW,
            buff=0.1
        )
        edge_highlight = VGroup()
        edge_indices = [0, 2, 6, 8]  # 四个角
        for idx in edge_indices:
            rect = SurroundingRectangle(
                kernel_sobel.get_entries()[idx],
                color=RED,
                buff=0.1
            )
            edge_highlight.add(rect)
        
        self.play(
            ShowPassingFlash(center_rect, time_width=0.5),
            ShowPassingFlash(edge_highlight, time_width=0.5),
            run_time=2
        )
        self.wait(1)
        
        # Act 4: 卷积可分离性 - 计算效率说明
        efficiency_title = Text("卷积的可分离性", font_size=32, color=WHITE).move_to(ORIGIN + UP * 2.5)
        
        # 展示计算效率对比
        method1 = VGroup(
            MathTex("3", color=GREEN, font_size=36),
            MathTex("+", color=WHITE, font_size=36),
            MathTex("3", color=GREEN, font_size=36),
            MathTex("=", color=WHITE, font_size=36),
            MathTex("6", color=GREEN, font_size=48)
        ).arrange(RIGHT, buff=0.3)
        method1_label = Text("分离卷积", font_size=24, color=GREEN).next_to(method1, DOWN, buff=0.3)
        method1_group = VGroup(method1, method1_label)
        
        method2 = VGroup(
            MathTex("3", color=RED, font_size=36),
            MathTex("\\times", color=WHITE, font_size=36),
            MathTex("3", color=RED, font_size=36),
            MathTex("=", color=WHITE, font_size=36),
            MathTex("9", color=RED, font_size=48)
        ).arrange(RIGHT, buff=0.3)
        method2_label = Text("直接矩阵", font_size=24, color=RED).next_to(method2, DOWN, buff=0.3)
        method2_group = VGroup(method2, method2_label)
        
        efficiency_comparison = VGroup(method1_group, method2_group).arrange(RIGHT, buff=2)
        efficiency_comparison.move_to(ORIGIN)
        
        vs_text = Text("vs", font_size=28, color=WHITE)
        vs_text.move_to(efficiency_comparison.get_center())
        
        self.play(
            Write(efficiency_title),
            run_time=0.5
        )
        self.wait(0.5)
        
        self.play(
            FadeIn(method1_group, shift=LEFT),
            FadeIn(method2_group, shift=RIGHT),
            Write(vs_text),
            run_time=1.5
        )
        self.wait(1)
        
        explanation_text = Text("横向的试探，纵向的抚慰，\n交织成了Sobel的视觉逻辑", 
                              font_size=24, color=TEAL).move_to(ORIGIN + DOWN * 2)
        self.play(Write(explanation_text), run_time=2)
        self.wait(1.5)
        
        # 清理
        self.play(
            FadeOut(VGroup(kernel_sobel, result_text, center_rect, edge_highlight,
                          efficiency_title, method1_group, method2_group, vs_text, explanation_text)),
            run_time=1
        )

    def transition_3_4(self):
        """场景3到场景4的过渡"""
        self.wait(0.5)

    # ========================================================================
    # Scene 4: 维度跃迁 (Dimensional Leap)
    # ========================================================================
    
    def setup_scene_4_vision(self):
        """Scene 4: 维度跃迁 + 全息扫描 + 实时示波器 (专家优化版)"""
        
        # --- 1. 数据与坐标系准备 ---
        # 使用更大的网格以保证视觉密度，但又不会卡死
        rows, cols = 20, 20
        
        # 统一的高度计算函数（避免坐标系不一致）
        def get_height_data(x, y):
            # 归一化坐标
            u, v = x / cols, y / rows
            # 两个 Sigmoid 叠加形成"台阶" (边缘)
            val = 1 / (1 + np.exp(-15 * (u - 0.3))) + 1 / (1 + np.exp(-15 * (u - 0.7)))
            # 让中间凹陷一点，增加地形复杂度
            return val * 0.5
        
        # 创建 3D 坐标轴 (作为所有物体的父坐标系)
        axes_3d = ThreeDAxes(
            x_range=[0, cols, 5],
            y_range=[0, rows, 5],
            z_range=[0, 2, 1],
            x_length=8,
            y_length=8,
            z_length=3,
            axis_config={"include_tip": False, "stroke_opacity": 0.3}
        )
        
        # --- 2. Act 1: 2D 像素网格 ---
        pixel_grid = VGroup()
        pixel_size = 0.4
        
        # 使用 axes_3d 的坐标系来定位，确保后续对齐
        for i in range(rows):
            for j in range(cols):
                h = get_height_data(j, i)
                color = interpolate_color(BLACK, WHITE, h)
                # 关键：直接用 axes_3d.c2p 确保位置绝对匹配
                pos = axes_3d.c2p(j, i, 0)
                pixel = Square(side_length=pixel_size, stroke_width=0)
                pixel.set_fill(color, opacity=1)
                pixel.move_to(pos)
                pixel_grid.add(pixel)
        
        # 【关键修复】整体居中，保持相对位置不变
        world_group = VGroup(axes_3d, pixel_grid).center()
        
        self.set_camera_orientation(phi=0, theta=-90*DEGREES)
        self.play(FadeIn(pixel_grid, lag_ratio=0.01), run_time=1.5)
        self.wait(0.5)
        
        # --- 3. Act 2: 维度升华 (修复变形撕裂问题) ---
        # 先旋转摄像机，进入 3D 视角
        self.move_camera(phi=60*DEGREES, theta=-45*DEGREES, run_time=2.5)
        
        # 生成高精细度曲面（使用统一的高度函数）
        terrain_surface = Surface(
            lambda u, v: axes_3d.c2p(u, v, get_height_data(u, v) * 3),  # 高度夸张化 * 3
            u_range=[0, cols-1],
            v_range=[0, rows-1],
            resolution=(40, 40),  # 更高分辨率，更平滑
            should_make_jagged=False
        )
        terrain_surface.set_style(
            fill_opacity=0.6,
            stroke_color=BLUE_A,
            stroke_width=0.5,
            fill_color=BLUE_E
        )
        
        # 此时 axes_3d 已经被 center() 移动过了，Surface 生成时是基于原始 axes 的
        # 所以 Surface 也需要应用同样的 shift
        surface_center_offset = world_group.get_center()
        terrain_surface.shift(surface_center_offset)
        
        # 使用 Cross Dissolve 替代 ReplacementTransform（避免撕裂）
        self.play(
            FadeIn(axes_3d),
            FadeIn(terrain_surface),
            pixel_grid.animate.set_opacity(0.1),  # 2D 像素变暗作为地基
            run_time=2
        )
        self.wait(1)
        
        # --- 4. Act 3: 全息扫描系统 (Holographic Scanner) ---
        
        # 4.1 制作"全息取景框" (四个角标)
        scanner_corners = VGroup()
        w, h = 1.2, 1.2
        corner_len = 0.3
        # 左上，右上，右下，左下
        pts = [
            [[-w/2, h/2 - corner_len, 0], [-w/2, h/2, 0], [-w/2 + corner_len, h/2, 0]],
            [[w/2 - corner_len, h/2, 0], [w/2, h/2, 0], [w/2, h/2 - corner_len, 0]],
            [[w/2, -h/2 + corner_len, 0], [w/2, -h/2, 0], [w/2 - corner_len, -h/2, 0]],
            [[-w/2 + corner_len, -h/2, 0], [-w/2, -h/2, 0], [-w/2, -h/2 + corner_len, 0]],
        ]
        for p_list in pts:
            corner = VMobject().set_points_as_corners([np.array(p) for p in p_list])
            scanner_corners.add(corner)
        
        scanner_box = scanner_corners.set_color(TEAL).set_stroke(width=4)
        # 添加激光束 (Laser Beam)
        laser = DashedLine(start=ORIGIN + UP*0.5, end=ORIGIN + DOWN*2, color=TEAL, stroke_width=2)
        scanner = VGroup(scanner_box, laser).rotate(PI/2, axis=RIGHT)  # 躺平
        
        # 4.2 制作 HUD 示波器 (悬浮在右侧)
        hud_bg = Rectangle(width=5, height=3, color=BLUE_E, fill_opacity=0.8).set_stroke(width=0)
        hud_bg.to_corner(DR, buff=0.5)
        
        hud_axes = Axes(
            x_range=[0, cols, 5],
            y_range=[-2, 2, 1],
            x_length=4.5,
            y_length=2,
            axis_config={"include_tip": False, "font_size": 16}
        ).move_to(hud_bg)
        
        hud_label = Text("GRADIENT (d/dx)", font_size=20, color=TEAL).next_to(hud_bg, UP, aligned_edge=LEFT)
        hud_group = VGroup(hud_bg, hud_axes, hud_label)
        
        self.add_fixed_in_frame_mobjects(hud_group)  # 固定在屏幕上
        self.play(FadeIn(hud_group))
        
        # --- 5. 动画驱动逻辑 ---
        scan_tracker = ValueTracker(0)
        
        def update_scanner(mob):
            u = scan_tracker.get_value()
            v = rows / 2  # 扫描中间行
            
            # 使用统一的高度函数计算精确高度
            z_math = get_height_data(u, v) * 3
            
            # 移动扫描器 (悬浮在地形上方 1.0 处)
            # 使用 axes_3d 的坐标系变换，加上偏移量
            base_pos = axes_3d.c2p(u, v, z_math + 1.0)
            pos_3d = base_pos + surface_center_offset
            mob.move_to(pos_3d)
            
            # 激光束伸缩：连接取景器和地面
            ground_pos = axes_3d.c2p(u, v, z_math) + surface_center_offset
            mob[1].put_start_and_end_on(pos_3d, ground_pos)
            
            # 颜色逻辑：导数越大，越红
            delta = 0.1
            deriv = (get_height_data(u + delta, v) - get_height_data(u - delta, v)) / (2 * delta)
            
            if abs(deriv) > 0.02:  # 阈值
                mob[0].set_color(RED)
                mob[1].set_color(RED)
            else:
                mob[0].set_color(TEAL)
                mob[1].set_color(TEAL)
        
        scanner.add_updater(update_scanner)
        self.add(scanner)
        
        # 示波器曲线 (动态绘制)
        def get_derivative_func(x):
            """计算x位置的导数"""
            delta = 0.1
            return (get_height_data(x + delta, rows/2) - get_height_data(x - delta, rows/2)) / (2 * delta) * 5
        
        graph = always_redraw(lambda: hud_axes.plot(
            get_derivative_func,
            x_range=[0, scan_tracker.get_value() + 0.1],
            color=scanner[0].get_color()  # 颜色同步
        ))
        
        # 示波器光点
        graph_dot = always_redraw(lambda: Dot(
            point=hud_axes.c2p(scan_tracker.get_value(), get_derivative_func(scan_tracker.get_value())),
            color=WHITE,
            radius=0.08
        ).set_glow_factor(2))
        
        self.add_fixed_in_frame_mobjects(graph, graph_dot)
        
        # --- 6. 执行扫描（前半段）---
        # 扫描到约1/3处暂停，进行像素级放大
        pause_position = cols * 0.35  # 在第一个边缘附近暂停
        
        self.play(
            scan_tracker.animate.set_value(pause_position),
            run_time=3,
            rate_func=linear
        )
        
        # --- 6.5. 像素级放大镜（新增）---
        # 暂停扫描，放大到3x3像素格子
        pause_u = pause_position
        pause_v = rows / 2
        
        # 创建放大镜效果
        zoom_factor = 8
        pixel_magnifier = VGroup()
        
        # 创建3x3像素网格的放大视图
        mag_axes = Axes(
            x_range=[-1.5, 1.5, 0.5],
            y_range=[-1.5, 1.5, 0.5],
            x_length=3,
            y_length=3,
            axis_config={"stroke_opacity": 0.3, "include_tip": False},
            tips=False
        ).to_corner(UL, buff=1)
        
        # 计算3x3区域的像素值
        pixel_values = []
        for di in [-1, 0, 1]:
            row_values = []
            for dj in [-1, 0, 1]:
                u_val = pause_u + dj
                v_val = pause_v + di
                if 0 <= u_val < cols and 0 <= v_val < rows:
                    h = get_height_data(u_val, v_val)
                    intensity = int(h * 255)
                    row_values.append(intensity)
                else:
                    row_values.append(0)
            pixel_values.append(row_values)
        
        # 绘制3x3像素格子
        pixel_squares = VGroup()
        pixel_labels = VGroup()
        for i, di in enumerate([-1, 0, 1]):
            for j, dj in enumerate([-1, 0, 1]):
                x_pos = (j - 1) * 0.8
                y_pos = (1 - i) * 0.8
                intensity = pixel_values[i][j]
                color_val = intensity / 255.0
                color = interpolate_color(BLACK, WHITE, color_val)
                
                square = Square(side_length=0.7, stroke_width=2, stroke_color=WHITE)
                square.set_fill(color, opacity=1)
                square.move_to(mag_axes.c2p(x_pos, y_pos))
                pixel_squares.add(square)
                
                # 添加数值标签
                label = Text(str(intensity), font_size=16, color=WHITE if intensity < 128 else BLACK)
                label.move_to(square.get_center())
                pixel_labels.add(label)
        
        # 显示卷积计算过程
        calc_text = VGroup(
            MathTex("(-1) \\times " + str(pixel_values[1][0]), font_size=24, color=COLOR_DIFF),
            MathTex("+", font_size=24, color=WHITE),
            MathTex("0 \\times " + str(pixel_values[1][1]), font_size=24, color=WHITE),
            MathTex("+", font_size=24, color=WHITE),
            MathTex("1 \\times " + str(pixel_values[1][2]), font_size=24, color=COLOR_DIFF),
            MathTex("=", font_size=24, color=WHITE),
        ).arrange(RIGHT, buff=0.2)
        
        result_value = -pixel_values[1][0] + pixel_values[1][2]
        result_text = MathTex(str(result_value), font_size=32, color=GREEN)
        calc_group = VGroup(calc_text, result_text).arrange(RIGHT, buff=0.3)
        calc_group.next_to(mag_axes, DOWN, buff=0.5)
        
        magnifier_title = Text("像素级放大镜", font_size=24, color=TEAL).next_to(mag_axes, UP, buff=0.3)
        
        # 把所有放大镜元素打包
        magnifier_group = VGroup(
            mag_axes, pixel_squares, pixel_labels, 
            magnifier_title, calc_group
        )
        
        explanation_voice = Text("让我们放大看看，\nSobel算子是如何在像素层面工作的", 
                                font_size=20, color=WHITE).next_to(calc_group, DOWN, buff=0.5)
        
        # 把所有放大镜元素打包（先不包含calc_group和explanation_voice，它们需要单独动画）
        magnifier_base = VGroup(
            mag_axes, pixel_squares, pixel_labels, magnifier_title
        )
        
        # 关键：将它们固定在相机帧上，这样它们永远是正对屏幕的 2D UI
        self.add_fixed_in_frame_mobjects(magnifier_base, calc_group, explanation_voice)
        
        # 暂停扫描，显示放大镜
        scanner.remove_updater(update_scanner)
        
        # 初始设为透明
        magnifier_base.set_opacity(0)
        calc_group.set_opacity(0)
        explanation_voice.set_opacity(0)
        
        # 动画逻辑：让背景变暗，突出前景UI
        self.play(
            # 让背景的 3D 元素变暗，突出前景 UI
            terrain_surface.animate.set_opacity(0.2),
            axes_3d.animate.set_opacity(0.1),
            pixel_grid.animate.set_opacity(0.05),
            scanner.animate.set_opacity(0.3),
            hud_group.animate.set_opacity(0.3),
            graph.animate.set_opacity(0.3),
            graph_dot.animate.set_opacity(0.3),
            
            # 淡入基础UI
            magnifier_base.animate.set_opacity(1),
            run_time=1.5
        )
        self.wait(0.5)
        
        self.play(
            calc_group.animate.set_opacity(1),
            run_time=2
        )
        self.wait(1.5)
        
        self.play(
            explanation_voice.animate.set_opacity(1),
            run_time=2
        )
        self.wait(1)
        
        # 退出放大镜时
        self.play(
            magnifier_base.animate.set_opacity(0),
            calc_group.animate.set_opacity(0),
            explanation_voice.animate.set_opacity(0),
            # 恢复背景亮度
            terrain_surface.animate.set_opacity(0.6),
            axes_3d.animate.set_opacity(0.3),
            pixel_grid.animate.set_opacity(0.1),
            scanner.animate.set_opacity(1),
            hud_group.animate.set_opacity(1),
            graph.animate.set_opacity(1),
            graph_dot.animate.set_opacity(1),
            run_time=1
        )
        
        # 记得移除固定对象，防止污染后续场景
        self.remove_fixed_in_frame_mobjects(magnifier_base, calc_group, explanation_voice)
        self.remove(magnifier_base, calc_group, explanation_voice)
        
        scanner.add_updater(update_scanner)
        
        # --- 6. 执行扫描（后半段）---
        self.play(
            scan_tracker.animate.set_value(cols-1),
            run_time=5,
            rate_func=linear
        )
        
        # 收尾
        scanner.remove_updater(update_scanner)
        self.wait(1)
        
        # Act 4: 结果输出
        # 镜头拉回
        self.move_camera(phi=0, theta=-90*DEGREES, run_time=2)
        
        edge_text = Text("Edges Detected", font_size=48, color=WHITE).move_to(ORIGIN)
        self.play(
            FadeOut(terrain_surface),
            FadeOut(axes_3d),
            FadeOut(pixel_grid),
            FadeOut(scanner),
            FadeOut(hud_group),
            FadeOut(graph),
            FadeOut(graph_dot),
            FadeIn(edge_text),
            run_time=2
        )
        self.wait(1)
        
        # 清理
        self.play(FadeOut(edge_text), run_time=1)

    def transition_4_5(self):
        """场景4到场景5的过渡"""
        self.wait(0.5)

    # ========================================================================
    # Scene 5: Outro - 知行合一
    # ========================================================================
    
    def setup_scene_5_outro(self):
        """Scene 5: 回顾与版权声明"""
        
        # Act 1: 时光倒流 - 快速回顾
        recap_elements = VGroup()
        
        # 泰勒公式
        taylor_recap = MathTex(
            "f'(x) \\approx \\frac{f(x+1) - f(x-1)}{2}",
            font_size=36
        ).shift(UP * 2)
        
        # Sobel矩阵
        sobel_recap = IntegerMatrix(
            [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
            element_alignment_corner=ORIGIN
        ).scale(0.6)
        
        # 正弦波
        axes_recap = Axes(x_range=[0, 10, 1], y_range=[-1, 3, 1],
                         x_length=4, y_length=2, tips=False)
        wave_recap = axes_recap.plot(
            lambda x: 1 + np.sin(x * 0.5),
            x_range=[0, 10],
            color=BLUE
        )
        
        recap_elements.add(taylor_recap, sobel_recap, VGroup(axes_recap, wave_recap))
        recap_elements.arrange(RIGHT, buff=1)
        
        self.play(
            LaggedStart(
                *[FadeIn(elem, shift=UP) for elem in recap_elements],
                lag_ratio=0.2
            ),
            run_time=2
        )
        self.wait(1)
        
        # 快速倒放效果
        self.play(
            LaggedStart(
                *[FadeOut(elem, shift=DOWN) for elem in recap_elements],
                lag_ratio=0.1
            ),
            run_time=1
        )
        
        # Act 2: 旁白升华
        philosophy_text = Text(
            "知行合一\n从数学理想 到 工程现实",
            font_size=48,
            color=WHITE
        )
        self.play(Write(philosophy_text), run_time=2)
        self.wait(2)
        self.play(FadeOut(philosophy_text), run_time=1)
        
        # Act 3: 版权页
        credits_text = VGroup(
            Text("Project Sobel", font_size=36, color=BLUE),
            Text("Visuals: Manim Community Edition", font_size=24, color=GREY),
            Text("Code: Python 3.10 + Manim", font_size=24, color=GREY),
            Text("", font_size=12),
            Text("原创声明: 本视频所有动画均为编程生成", 
                 font_size=28, color=WHITE, weight=BOLD)
        ).arrange(DOWN, buff=0.5)
        
        self.play(
            LaggedStart(
                *[Write(text) for text in credits_text],
                lag_ratio=0.3
            ),
            run_time=3
        )
        self.wait(3)
        
        # 最终淡出
        self.play(FadeOut(credits_text), run_time=2)
