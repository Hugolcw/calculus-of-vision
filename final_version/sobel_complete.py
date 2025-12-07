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
        ghost_graph.set_stroke(color=COLOR_GHOST, width=1, opacity=OPACITY_GHOST)
        
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
        
        self.play(
            self.add(ghost_graph),
            func_continuous.animate.set_opacity(0),
            ghost_graph.animate.set_stroke(opacity=OPACITY_GHOST),
            Create(discrete_stems),
            run_time=2
        )
        self.wait(0.5)
        
        # Act 3: 聚焦困境
        focus_point = axes.c2p(5, continuous_func(5))
        question_mark = Text("?", font_size=72, color=YELLOW).move_to(focus_point + UP * 1.5)
        
        self.play(
            self.camera.frame.animate.scale(0.4).move_to(focus_point),
            Write(question_mark),
            run_time=2
        )
        self.wait(1)
        
        # 清理
        self.play(
            FadeOut(VGroup(axes, func_continuous, ghost_graph, discrete_stems, 
                          tangent_line, slope_text, question_mark)),
            self.camera.frame.animate.scale(2.5).move_to(ORIGIN),
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
    # Scene 3: 算子解构 (Operator Anatomy)
    # ========================================================================
    
    def setup_scene_3_matrices(self):
        """Scene 3: Sobel算子的构造"""
        
        # Act 1: 身份确认 - 展示两个向量
        kernel_x = Matrix([[-1, 0, 1]], element_alignment_corner=ORIGIN)
        kernel_x.set_color(COLOR_DIFF)
        kernel_x_label = Brace(kernel_x, DOWN)
        kernel_x_text = kernel_x_label.get_text("微分\\/高通").set_color(COLOR_DIFF)
        kernel_x_group = VGroup(kernel_x, kernel_x_label, kernel_x_text)
        kernel_x_group.to_edge(LEFT).shift(UP)
        
        kernel_y = Matrix([[1], [2], [1]], element_alignment_corner=ORIGIN)
        kernel_y.set_color(COLOR_SMOOTH)
        kernel_y_label = Brace(kernel_y, RIGHT)
        kernel_y_text = kernel_y_label.get_text("平滑\\/低通").set_color(COLOR_SMOOTH)
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
        
        # 演示广播过程 (简化版: 直接显示结果)
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
        
        # 清理
        self.play(FadeOut(VGroup(kernel_sobel, result_text, center_rect, edge_highlight)), run_time=1)

    def transition_3_4(self):
        """场景3到场景4的过渡"""
        self.wait(0.5)

    # ========================================================================
    # Scene 4: 维度跃迁 (Dimensional Leap)
    # ========================================================================
    
    def setup_scene_4_vision(self):
        """Scene 4: 2D图像转3D地形"""
        
        # 数据准备: 生成测试图像数据
        # 创建一个简单的测试图像: 左暗右亮的边缘
        test_width, test_height = 100, 100
        image_data = np.zeros((test_height, test_width, 3), dtype=np.uint8)
        center_x = test_width // 2
        for y in range(test_height):
            for x in range(test_width):
                # 使用sigmoid创建平滑过渡
                intensity = int(255 / (1 + np.exp(-0.1 * (x - center_x))))
                image_data[y, x] = [intensity, intensity, intensity]
        
        # 降采样 (关键!)
        downsampled = image_data[::10, ::10]  # 100x100 -> 10x10
        height_map = downsampled[:, :, 0] / 255.0  # 归一化到[0,1]
        
        # Act 1: 2D锚定 - 显示图像和扫描线
        # 使用Rectangle模拟图像 (因为ImageMobject可能不支持直接传入numpy数组)
        # 或者创建一个像素网格来模拟图像
        image_rect = Rectangle(
            width=6, height=6,
            fill_color=WHITE,
            fill_opacity=0.8,
            stroke_color=GREY,
            stroke_width=2
        )
        
        # 添加一些视觉元素来表示图像
        # 使用动态shape获取实际尺寸（避免硬编码）
        rows, cols = height_map.shape
        pixel_grid = VGroup()
        pixel_size = 0.5
        spacing = 0.6
        
        for i in range(rows):
            for j in range(cols):
                intensity = height_map[i, j]
                color = interpolate_color(BLACK, WHITE, intensity)
                pixel = Square(side_length=pixel_size, fill_color=color, 
                              fill_opacity=0.8, stroke_width=0.1)
                # 动态计算位置
                pixel.move_to(image_rect.get_left() + 
                             RIGHT * (j * spacing - (cols - 1) * spacing / 2) + 
                             UP * ((rows - 1) * spacing / 2 - i * spacing))
                pixel_grid.add(pixel)
        
        image_2d = VGroup(image_rect, pixel_grid)
        
        scan_line = Line(
            image_rect.get_left() + UP * image_rect.get_height() / 2,
            image_rect.get_right() + UP * image_rect.get_height() / 2,
            color=COLOR_DIFF,
            stroke_width=4
        )
        
        # 波形图坐标轴
        waveform_axes = Axes(
            x_range=[0, 100, 20],
            y_range=[0, 255, 50],
            x_length=6,
            y_length=3,
            tips=False,
            axis_config={"stroke_opacity": 0.5}
        ).next_to(image_2d, RIGHT, buff=1)
        
        # 提取中间行的像素值
        middle_row_idx = test_height // 2
        row_data = image_data[middle_row_idx, :, 0]
        
        # 创建波形图
        waveform_points = [
            waveform_axes.c2p(x, row_data[x]) 
            for x in range(0, test_width, 5)
        ]
        waveform = VMobject().set_points_as_corners(waveform_points)
        waveform.set_stroke(color=COLOR_CONTINUOUS, width=2)
        
        self.set_camera_orientation(phi=0, theta=-90*DEGREES)  # 俯视图
        self.play(
            FadeIn(image_2d),
            Create(scan_line),
            Create(waveform_axes),
            Create(waveform),
            run_time=2
        )
        
        # 扫描线移动
        self.play(
            scan_line.animate.shift(DOWN * image_rect.get_height()),
            run_time=3
        )
        self.wait(1)
        
        # Act 2: 维度切换 - 转换为3D
        # 使用动态尺寸设置坐标轴范围
        rows, cols = height_map.shape
        axes_3d = ThreeDAxes(
            x_range=[0, cols, max(1, cols//5)],
            y_range=[0, rows, max(1, rows//5)],
            z_range=[0, 2, 0.5],
            x_length=8,
            y_length=8,
            z_length=4,
            axis_config={"stroke_opacity": 0.3, "stroke_width": 1}
        )
        
        # 创建3D地形表面
        def terrain_func(u, v):
            i, j = int(v), int(u)
            if 0 <= i < rows and 0 <= j < cols:
                height = height_map[i, j] * 2  # 放大高度
                return axes_3d.c2p(u, v, height)
            return axes_3d.c2p(u, v, 0)
        
        # 使用动态分辨率，匹配降采样后的尺寸
        rows, cols = height_map.shape
        terrain_surface = Surface(
            terrain_func,
            u_range=[0, cols],
            v_range=[0, rows],
            resolution=(cols, rows),  # 动态分辨率，匹配降采样
            should_make_jagged=False
        )
        
        # 使用科技感颜色方案：低处蓝紫色，高处青白色（替代简陋的checkerboard）
        terrain_surface.set_style(
            fill_color=BLUE_D,  # 基础颜色：深蓝
            fill_opacity=0.8,
            stroke_color=TEAL,  # 边框：青色，更有科技感
            stroke_width=0.5
        )
        
        # 尝试使用基于高度的颜色映射（如果Manim版本支持）
        # 如果不支持，至少使用统一的科技感颜色，比checkerboard更专业
        try:
            # 某些Manim版本可能支持 set_fill_by_value
            terrain_surface.set_fill_by_value(
                axes=axes_3d,
                colorscale=[BLUE_E, BLUE_D, TEAL_C, WHITE],  # 从深蓝到白色的渐变
                axis=2
            )
        except:
            # 如果不支持，使用统一的科技蓝色
            pass
        
        # 相机旋转 + 图像转换
        self.play(
            ReplacementTransform(image_2d, terrain_surface),
            FadeOut(scan_line, waveform_axes, waveform),
            self.camera.frame.animate.set_euler_angles(
                phi=75*DEGREES,
                theta=-45*DEGREES
            ),
            run_time=3
        )
        self.add(axes_3d)
        self.wait(1)
        
        # Act 3: 全息扫描 - Sobel算子扫描
        # 扫描框
        scanner = Square(side_length=1.2).set_stroke(TEAL, width=3)
        scanner.rotate(PI/2, axis=RIGHT)
        
        # 扫描器位置追踪
        scan_tracker = ValueTracker(1)
        
        def update_scanner(mob):
            u = scan_tracker.get_value()
            v = rows // 2  # 使用动态中心行
            i, j = int(v), int(u)
            if 0 <= i < rows and 0 <= j < cols:
                z = height_map[i, j] * 2
            else:
                z = 0
            pos = axes_3d.c2p(u, v, z + 0.2)
            mob.move_to(pos)
        
        scanner.add_updater(update_scanner)
        
        self.add(scanner)
        self.play(
            scan_tracker.animate.set_value(cols - 1),  # 使用动态列数
            run_time=5,
            rate_func=linear
        )
        self.wait(1)
        
        # Act 4: 特征图生成 - 显示边缘检测结果
        # 创建边缘检测结果 (使用动态尺寸)
        rows, cols = height_map.shape
        edge_grid = VGroup()
        pixel_size = 0.5
        
        for i in range(rows):
            for j in range(cols):
                # 在边缘处(中间列)设置为白色
                center_col = cols // 2
                if abs(j - center_col) <= 1:  # 中间1-2列
                    color = WHITE
                    opacity = 1.0
                else:
                    color = BLACK
                    opacity = 0.3
                pixel = Square(side_length=pixel_size, fill_color=color, 
                              fill_opacity=opacity, stroke_width=0.1)
                pixel.move_to(axes_3d.c2p(j, i, 0))
                edge_grid.add(pixel)
        
        edge_image = edge_grid.scale(0.8)
        
        self.play(
            FadeOut(terrain_surface, axes_3d, scanner),
            FadeIn(edge_image),
            self.camera.frame.animate.set_euler_angles(phi=0, theta=-90*DEGREES),
            run_time=2
        )
        self.wait(1.5)
        
        # 清理
        self.play(FadeOut(edge_image), run_time=1)

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
