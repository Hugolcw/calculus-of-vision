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

# 字幕样式配置
SUBTITLE_FONT_SIZE = 28
TITLE_FONT_SIZE = 36
SUBTITLE_COLOR = WHITE
SUBTITLE_BG_OPACITY = 0.7

# LaTeX模板配置
TEX_TEMPLATE = TexTemplate()
TEX_TEMPLATE.add_to_preamble(r"\usepackage{amsmath}")


# ============================================================================
# 字幕管理系统 (Subtitle Manager)
# ============================================================================

class SubtitleManager:
    """字幕管理器：管理字幕的显示和切换，实现3B1B风格"""
    
    def __init__(self, scene):
        self.scene = scene
        self.current_subtitle = None
        self.current_bg = None
    
    def create_subtitle(self, text, color=SUBTITLE_COLOR, font_size=SUBTITLE_FONT_SIZE):
        """创建字幕对象（带背景）"""
        # 尝试使用中文字体，如果失败则使用默认字体
        try:
            subtitle = Text(text, font_size=font_size, color=color, font="SimHei")
        except:
            subtitle = Text(text, font_size=font_size, color=color)
        subtitle.to_edge(DOWN, buff=0.5)
        bg = BackgroundRectangle(
            subtitle, 
            color=BLACK, 
            fill_opacity=SUBTITLE_BG_OPACITY, 
            buff=0.2,  # 【审美优化】增加 buff，避免"窒息感"
            stroke_width=0,
            corner_radius=0.05  # 【审美优化】添加圆角
        )
        return subtitle, bg
    
    def show(self, text, duration=None, color=SUBTITLE_COLOR, wait_after=0.8, fade_in=True):
        """
        显示字幕
        
        参数:
        - text: 字幕文本
        - duration: 字幕显示的时长（None则根据文本长度自动计算）
        - color: 字幕颜色
        - wait_after: 字幕显示后的等待时间
        - fade_in: 是否淡入（False则直接显示）
        """
        # 计算显示时长
        if duration is None:
            # 根据文本长度计算：每个字符约0.12秒，最小2秒，最大6秒
            duration = max(2, min(len(text) * 0.12, 6))
        
        # 创建字幕
        subtitle, bg = self.create_subtitle(text, color)
        
        if self.current_subtitle is None:
            # 第一次显示
            if fade_in:
                self.scene.play(
                    FadeIn(bg, shift=UP*0.3),
                    Write(subtitle, run_time=duration),
                    run_time=max(duration, 0.8)
                )
            else:
                self.scene.add(bg, subtitle)
                self.scene.play(Write(subtitle, run_time=duration))
        else:
            # 切换字幕（平滑过渡）
            self.scene.play(
                ReplacementTransform(self.current_bg, bg, run_time=0.6),
                ReplacementTransform(self.current_subtitle, subtitle, run_time=0.6),
                run_time=0.6
            )
            # 新字幕的写入动画（如果需要）
            if duration > 0.6:
                self.scene.play(Write(subtitle), run_time=duration - 0.6)
        
        self.current_subtitle = subtitle
        self.current_bg = bg
        
        # 等待时间
        if wait_after > 0:
            self.scene.wait(wait_after)
    
    def clear(self, fade_out=True):
        """清除字幕"""
        if self.current_subtitle:
            if fade_out:
                self.scene.play(
                    FadeOut(self.current_subtitle, shift=DOWN*0.3),
                    FadeOut(self.current_bg, shift=DOWN*0.3),
                    run_time=0.5
                )
            else:
                self.scene.remove(self.current_subtitle, self.current_bg)
            self.current_subtitle = None
            self.current_bg = None


# ============================================================================
# 工具函数 (Helper Functions)
# ============================================================================

def create_title(text, color=WHITE, font_size=TITLE_FONT_SIZE):
    """创建场景标题"""
    # 尝试使用中文字体，如果失败则使用默认字体
    try:
        title = Text(text, font_size=font_size, color=color, font="SimHei")
    except:
        title = Text(text, font_size=font_size, color=color)
    title.to_edge(UP, buff=0.6)
    bg = BackgroundRectangle(
        title,
        color=BLACK,
        fill_opacity=0.8,
        buff=0.2,  # 【审美优化】增加 buff
        stroke_width=0,
        corner_radius=0.05  # 【审美优化】添加圆角
    )
    return VGroup(bg, title)


def calculate_text_duration(text, base_speed=0.12):
    """
    根据文本长度计算动画时长
    
    参数:
    - text: 文本内容
    - base_speed: 每个字符的基础速度（秒/字符）
    
    返回: 建议的动画时长（秒）
    """
    base_time = len(text) * base_speed
    # 复杂概念需要更多时间
    complex_keywords = ["导数", "泰勒", "算子", "卷积", "离散", "连续", "微积分"]
    complexity_bonus = sum(1 for keyword in complex_keywords if keyword in text) * 0.3
    final_time = base_time + complexity_bonus
    return max(1.5, min(final_time, 5))


# ============================================================================
# 主场景类
# ============================================================================

class SobelUniverse(ThreeDScene):
    def construct(self):
        # 全局设置
        self.camera.background_color = "#0e1111"
        
        # ====================================================================
        # 第一阶段：Scene 0 - 引言与背景
        # ====================================================================
        self.setup_scene_0_intro()
        
        # ====================================================================
        # 第二阶段：Scene 1 - 连续与离散的对比（扩展版）
        # ====================================================================
        self.transition_0_1()
        self.setup_scene_1_discrete()
        
        # ====================================================================
        # 第三阶段：Scene 2 - 泰勒展开推导（扩展版）
        # ====================================================================
        self.transition_1_2()
        self.setup_scene_2_taylor()
        
        # ====================================================================
        # 第四阶段：Scene 3 - Sobel算子构造（扩展版）
        # ====================================================================
        self.transition_2_3()
        self.setup_scene_3_matrices()
        
        # ====================================================================
        # 第五阶段：Scene 4 - 3D可视化应用（扩展版）
        # ====================================================================
        self.transition_3_4()
        self.setup_scene_4_vision()
        
        # ====================================================================
        # 第六阶段：Scene 4.5 - 实际应用案例（新增）
        # ====================================================================
        self.transition_4_4_5()
        self.setup_scene_4_5_applications()
        
        # ====================================================================
        # 第七阶段：Scene 5 - 总结与升华（扩展版）
        # ====================================================================
        self.transition_4_5_5()
        self.setup_scene_5_outro()
        
        # 第七阶段结束，等待检查
        self.wait(2)
    
    # ========================================================================
    # Scene 0: 引言与背景 (Introduction & Background)
    # ========================================================================
    
    def setup_scene_0_intro(self):
        """Scene 0: 引言与背景 - 建立主题，激发兴趣"""
        
        subtitle_mgr = SubtitleManager(self)
        
        # ====================================================================
        # Part 1: 开场问题（约15秒）
        # ====================================================================
        
        # 开场字幕
        subtitle_mgr.show(
            "你有没有想过，机器是如何'看见'图像的？",
            duration=3.5,
            wait_after=1.0
        )
        
        # 【审美优化】快速展示实际应用（蒙太奇效果）
        # 使用相对排版，统一对齐
        # 应用1：自动驾驶
        car_icon = Text("🚗", font_size=72)
        car_label = Text("自动驾驶", font_size=24, color=BLUE_C)
        car_group = VGroup(car_icon, car_label)
        car_group.arrange(DOWN, buff=0.4, aligned_edge=ORIGIN)  # 【审美优化】相对排版
        
        # 应用2：人脸识别
        face_icon = Text("👤", font_size=72)
        face_label = Text("人脸识别", font_size=24, color=GREEN_C)
        face_group = VGroup(face_icon, face_label)
        face_group.arrange(DOWN, buff=0.4, aligned_edge=ORIGIN)
        
        # 应用3：医疗影像
        medical_icon = Text("🏥", font_size=72)
        medical_label = Text("医疗影像", font_size=24, color=RED_C)
        medical_group = VGroup(medical_icon, medical_label)
        medical_group.arrange(DOWN, buff=0.4, aligned_edge=ORIGIN)
        
        # 【审美优化】使用相对排版，统一对齐
        apps_group = VGroup(car_group, face_group, medical_group)
        apps_group.arrange(RIGHT, buff=1.5, aligned_edge=ORIGIN)  # 统一对齐，增加间距
        apps_group.move_to(UP * 1)
        
        # 【审美优化】添加缓动，使用 LaggedStart
        self.play(
            LaggedStart(
                FadeIn(car_group, shift=UP*0.3, scale=0.6),
                FadeIn(face_group, shift=UP*0.3, scale=0.6),
                FadeIn(medical_group, shift=UP*0.3, scale=0.6),
                lag_ratio=0.35,  # 略微增加延迟
                run_time=2.5,
                rate_func=smooth  # 添加缓动
            )
        )
        self.wait(1)
        
        # 【审美优化】淡出时添加缓动
        self.play(
            FadeOut(apps_group, shift=DOWN*0.3, scale=0.7),
            run_time=1.2,
            rate_func=smooth
        )
        self.wait(0.5)
        
        # ====================================================================
        # Part 2: 核心概念引入（约20秒）
        # ====================================================================
        
        # 展示边缘检测的概念
        subtitle_mgr.show(
            "今天，我们将探索一个看似简单的问题：如何检测图像的边缘？",
            duration=4.5,
            wait_after=1.0
        )
        
        # 【审美优化】创建模拟图像（矩形区域）
        # 辅助元素降低亮度和透明度
        image_width = 6
        image_height = 4
        image_bg = Rectangle(
            width=image_width,
            height=image_height,
            color=GREY_D,
            fill_opacity=0.25,  # 降低不透明度
            stroke_width=1.5,  # 降低线宽
            stroke_opacity=0.6  # 降低描边不透明度
        ).move_to(ORIGIN + UP * 0.5)
        
        # 创建边缘（一条明显的边界）- 主角，保持高亮
        edge_line = Line(
            image_bg.get_left() + UP * image_height/2,
            image_bg.get_left() + DOWN * image_height/2,
            color=WHITE,
            stroke_width=5.5  # 略微降低，但仍然突出
        ).shift(RIGHT * 2)
        
        # 左侧暗区 - 辅助元素
        dark_region = Rectangle(
            width=2,
            height=image_height,
            color=BLACK,
            fill_opacity=0.7  # 略微降低不透明度
        ).align_to(image_bg, LEFT).align_to(image_bg, UP)
        
        # 右侧亮区 - 辅助元素
        light_region = Rectangle(
            width=4,
            height=image_height,
            color=WHITE,
            fill_opacity=0.25  # 降低不透明度
        ).align_to(image_bg, RIGHT).align_to(image_bg, UP)
        
        image_group = VGroup(image_bg, dark_region, light_region, edge_line)
        
        # 【审美优化】添加缓动
        self.play(
            FadeIn(image_group, scale=0.85),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(0.5)
        
        # 【审美优化】高亮框：增加 buff 和圆角，使用柔和色
        edge_highlight = SurroundingRectangle(
            edge_line,
            color=YELLOW_C,  # 使用柔和色（YELLOW_C 而不是 YELLOW）
            buff=0.4,  # 增加内间距，避免"窒息感"
            stroke_width=3.5,  # 略微降低线宽
            corner_radius=0.15  # 增加圆角，更柔和
        )
        
        self.play(
            Create(edge_highlight),
            edge_line.animate.set_color(YELLOW_C),  # 使用柔和色
            run_time=1,
            rate_func=smooth  # 添加缓动
        )
        self.wait(1)
        
        # 【审美优化】移除时添加缓动
        self.play(
            FadeOut(image_group, shift=DOWN*0.2),
            FadeOut(edge_highlight, shift=DOWN*0.2),
            run_time=1.2,
            rate_func=smooth
        )
        
        subtitle_mgr.show(
            "这背后，隐藏着微积分的深刻智慧",
            duration=3.5,
            wait_after=1.0
        )
        
        # ====================================================================
        # Part 3: 主题预告（约15秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "从数学的理想世界，到工程的实际应用",
            duration=4.0,
            wait_after=1.5
        )
        
        # 【审美优化】快速预览关键场景（蒙太奇）
        # 使用相对排版，统一对齐
        # 预览1：连续函数
        preview_axes = Axes(
            x_range=[0, 3, 1],
            y_range=[0, 2, 1],
            x_length=2,
            y_length=1.5,
            axis_config={
                "stroke_opacity": 0.3,  # 降低透明度
                "stroke_width": 0.8,  # 降低线宽
                "stroke_color": GREY_C  # 降低亮度
            },
            tips=False
        ).scale(0.6)
        preview_curve = preview_axes.plot(
            lambda x: 1 + 0.5 * np.sin(x),
            color=COLOR_CONTINUOUS,
            stroke_width=2.5  # 主角更粗
        )
        preview1 = VGroup(preview_axes, preview_curve)
        preview1_label = Text("连续", font_size=20, color=COLOR_CONTINUOUS)
        preview1_group = VGroup(preview1, preview1_label)
        preview1_group.arrange(DOWN, buff=0.3, aligned_edge=ORIGIN)  # 【审美优化】相对排版
        
        # 预览2：离散采样
        preview2_axes = Axes(
            x_range=[0, 3, 1],
            y_range=[0, 2, 1],
            x_length=2,
            y_length=1.5,
            axis_config={
                "stroke_opacity": 0.3,
                "stroke_width": 0.8,
                "stroke_color": GREY_C
            },
            tips=False
        ).scale(0.6)
        preview2_points = VGroup()
        for x in [0.5, 1.0, 1.5, 2.0, 2.5]:
            y = 1 + 0.5 * np.sin(x)
            dot = Dot(
                preview2_axes.c2p(x, y), 
                color=COLOR_DISCRETE, 
                radius=0.06,  # 【审美优化】略微增大，但保持适中
                fill_opacity=0.9  # 略微降低透明度
            )
            preview2_points.add(dot)
        preview2 = VGroup(preview2_axes, preview2_points)
        preview2_label = Text("离散", font_size=20, color=COLOR_DISCRETE)
        preview2_group = VGroup(preview2, preview2_label)
        preview2_group.arrange(DOWN, buff=0.3, aligned_edge=ORIGIN)  # 【审美优化】相对排版
        
        # 预览3：Sobel矩阵
        sobel_preview = IntegerMatrix(
            [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
            element_alignment_corner=ORIGIN
        ).scale(0.4)
        preview3_label = Text("Sobel", font_size=20, color=GOLD_C)  # 【审美优化】使用柔和色
        preview3_group = VGroup(sobel_preview, preview3_label)
        preview3_group.arrange(DOWN, buff=0.3, aligned_edge=ORIGIN)  # 【审美优化】相对排版
        
        # 【审美优化】使用相对排版，统一对齐
        previews = VGroup(preview1_group, preview2_group, preview3_group)
        previews.arrange(RIGHT, buff=1.2, aligned_edge=ORIGIN)  # 统一对齐，增加间距
        previews.move_to(ORIGIN + UP * 0.5)
        
        # 【审美优化】添加缓动，使用 LaggedStart
        self.play(
            LaggedStart(
                FadeIn(preview1_group, shift=UP*0.3, scale=0.7),
                FadeIn(preview2_group, shift=UP*0.3, scale=0.7),
                FadeIn(preview3_group, shift=UP*0.3, scale=0.7),
                lag_ratio=0.25,  # 略微增加延迟
                run_time=2.5,
                rate_func=smooth  # 添加缓动
            )
        )
        self.wait(2)
        
        # 【审美优化】淡出时添加缓动
        self.play(
            FadeOut(previews, shift=DOWN*0.3, scale=0.7),
            run_time=1.2,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 4: 背景知识铺垫（约30秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "在数学分析中，导数告诉我们函数的变化率",
            duration=4.5,
            wait_after=1.0
        )
        
        # 展示导数的直观例子
        # 例子1：速度（位移的导数）
        # 【审美优化】辅助元素降透明度、降亮度
        example_axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 4, 1],
            x_length=6,
            y_length=4,
            axis_config={
                "stroke_opacity": 0.4,  # 降低透明度
                "stroke_width": 1,  # 降低线宽
                "stroke_color": GREY_C  # 使用灰色，降低亮度
            },
            tips=False
        )
        example_axes_labels = example_axes.get_axis_labels(
            Text("时间", font_size=24, color=GREY_C),  # 标签也用灰色
            Text("位移", font_size=24, color=GREY_C)
        )
        
        # 位移曲线（主角，保持高亮）
        position_curve = example_axes.plot(
            lambda x: 2 * x - 0.2 * x**2,
            color=COLOR_CONTINUOUS,  # 使用语义颜色
            stroke_width=3.5,  # 主角更粗
            x_range=[0, 5]
        )
        
        # 在某个点画切线（导数）
        tangent_x = 2
        tangent_y = 2 * tangent_x - 0.2 * tangent_x**2
        tangent_slope = 2 - 0.4 * tangent_x  # 导数：2 - 0.4x
        tangent_point = example_axes.c2p(tangent_x, tangent_y)
        tangent_line = Line(
            example_axes.c2p(tangent_x - 1, tangent_y - tangent_slope),
            example_axes.c2p(tangent_x + 1, tangent_y + tangent_slope),
            color=COLOR_DIFF,  # 使用语义颜色（微分）
            stroke_width=2.5,
            stroke_opacity=0.9  # 略微降低透明度，但不影响可见性
        )
        
        # 速度标注（使用 MathTex）
        velocity_label = MathTex(
            "v = \\frac{ds}{dt}",
            font_size=32,
            color=COLOR_DIFF  # 使用语义颜色
        ).move_to(example_axes.c2p(4, 3.5))
        
        example_group = VGroup(
            example_axes,
            example_axes_labels,
            position_curve,
            tangent_line,
            velocity_label
        )
        
        # 【审美优化】添加缓动函数，分步揭示
        self.play(
            Create(example_axes),
            Write(example_axes_labels),
            run_time=1,
            rate_func=smooth  # 添加缓动
        )
        self.play(
            Create(position_curve),
            run_time=1.5,
            rate_func=smooth
        )
        self.play(
            Create(tangent_line),
            Write(velocity_label),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(1.5)
        
        # 【审美优化】淡出时添加缓动
        self.play(
            FadeOut(example_group, shift=DOWN*0.2),
            run_time=1.2,
            rate_func=smooth
        )
        
        subtitle_mgr.show(
            "但在数字图像中，一切都是离散的像素",
            duration=4.0,
            wait_after=1.0
        )
        
        # 展示像素化过程
        # 连续图像（用平滑渐变表示）
        continuous_img_width = 5
        continuous_img_height = 3
        continuous_img = Rectangle(
            width=continuous_img_width,
            height=continuous_img_height,
            fill_opacity=0,
            stroke_width=2,
            stroke_color=WHITE
        ).move_to(LEFT * 2.5)
        
        # 创建渐变效果（用多个矩形模拟）
        gradient_rects = VGroup()
        num_gradients = 20
        for i in range(num_gradients):
            rect = Rectangle(
                width=continuous_img_width / num_gradients,
                height=continuous_img_height,
                fill_opacity=1,
                stroke_width=0
            )
            intensity = i / num_gradients
            rect.set_color(interpolate_color(BLACK, WHITE, intensity))
            rect.move_to(
                continuous_img.get_left() + 
                RIGHT * (continuous_img_width / num_gradients) * (i + 0.5)
            )
            gradient_rects.add(rect)
        
        continuous_img_group = VGroup(continuous_img, gradient_rects)
        continuous_label = Text("连续图像", font_size=24).next_to(continuous_img, DOWN, buff=0.3)
        
        # 离散像素（用网格表示）
        pixel_grid_size = 8
        pixel_img_width = 5
        pixel_img_height = 3
        pixel_grid = VGroup()
        
        for i in range(pixel_grid_size):
            for j in range(pixel_grid_size):
                pixel = Square(
                    side_length=pixel_img_width / pixel_grid_size,
                    fill_opacity=1,
                    stroke_width=0.5,
                    stroke_color=GREY_D
                )
                # 计算像素位置
                x_pos = -pixel_img_width/2 + (j + 0.5) * pixel_img_width / pixel_grid_size
                y_pos = pixel_img_height/2 - (i + 0.5) * pixel_img_height / pixel_grid_size
                pixel.move_to(RIGHT * 2.5 + RIGHT * x_pos + UP * y_pos)
                
                # 计算颜色（基于位置）
                intensity = j / pixel_grid_size
                pixel.set_color(interpolate_color(BLACK, WHITE, intensity))
                pixel_grid.add(pixel)
        
        discrete_img_group = pixel_grid
        discrete_label = Text("离散像素", font_size=24).next_to(discrete_img_group, DOWN, buff=0.3)
        
        # 【审美优化】箭头使用柔和色，降低线宽
        arrow = Arrow(
            continuous_img.get_right() + RIGHT * 0.3,
            discrete_img_group.get_left() + LEFT * 0.3,
            color=YELLOW_C,  # 使用柔和色
            stroke_width=2.5,  # 降低线宽
            buff=0,
            stroke_opacity=0.9
        )
        
        # 【审美优化】添加缓动，分步揭示
        self.play(
            FadeIn(continuous_img_group, shift=UP*0.3),
            Write(continuous_label),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(0.5)
        
        self.play(
            Create(arrow),
            run_time=1,
            rate_func=smooth
        )
        
        self.play(
            FadeIn(discrete_img_group, shift=DOWN*0.3),
            Write(discrete_label),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(2)
        
        # 【审美优化】清理时添加缓动
        self.play(
            FadeOut(continuous_img_group, shift=DOWN*0.2),
            FadeOut(continuous_label, shift=DOWN*0.2),
            FadeOut(arrow, shift=DOWN*0.2),
            FadeOut(discrete_img_group, shift=DOWN*0.2),
            FadeOut(discrete_label, shift=DOWN*0.2),
            run_time=1.5,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 5: 过渡到下一场景（约5秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "让我们从数学的理想世界开始",
            duration=3.5,
            wait_after=1.5
        )
        
        # 清理字幕
        subtitle_mgr.clear()
        
        # 场景结束
        self.wait(1)


    # ========================================================================
    # Scene 1: 连续与离散的对比（扩展版）
    # ========================================================================
    
    def transition_0_1(self):
        """Scene 0 到 Scene 1 的过渡"""
        self.wait(0.5)
    
    def setup_scene_1_discrete(self):
        """Scene 1: 从连续到离散的视觉对比（扩展版，约40秒）"""
        
        subtitle_mgr = SubtitleManager(self)
        
        # ====================================================================
        # Part 1: 导数的直观理解（约10秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "在连续世界中，导数是切线的斜率",
            duration=3.5,
            wait_after=1.0
        )
        
        # 【审美优化】创建坐标轴（辅助元素降亮度）
        axes = Axes(
            x_range=[-1, 11, 1],
            y_range=[-1, 5, 1],
            x_length=12,
            y_length=5,
            axis_config={
                "stroke_opacity": 0.4,  # 【审美优化】降低透明度
                "stroke_width": 1,  # 【审美优化】降低线宽
                "stroke_color": GREY_C  # 【审美优化】降低亮度
            },
            tips=False
        )
        
        # 正弦组合函数: f(x) = 2 + sin(x) + 0.5*sin(2*x)
        # 【重要】定义在外层，确保所有内部作用域可以访问
        def continuous_func(x):
            return 2 + np.sin(x * 0.5) + 0.5 * np.sin(x)
        
        # 【审美优化】主角：连续函数曲线（保持高亮）
        func_continuous = axes.plot(
            continuous_func,
            x_range=[0, 10],
            color=COLOR_CONTINUOUS,
            stroke_width=3.5  # 更粗，突出主角
        )
        
        # 创建坐标轴标签（辅助元素降亮度）
        axes_labels = axes.get_axis_labels(
            MathTex("x", font_size=24, color=GREY_C),
            MathTex("f(x)", font_size=24, color=GREY_C)
        )
        
        # 【审美优化】同步展示：字幕出现时，画面也出现
        self.play(
            Create(axes),
            Write(axes_labels),
            Create(func_continuous),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.8)
        
        # 展示多个切线的例子
        # 切线1：在 x=3 处
        tangent_points = [3, 5, 7]
        tangent_lines_group = VGroup()
        
        for tx in tangent_points:
            ty = continuous_func(tx)
            dx = 0.01
            dy = (continuous_func(tx + dx) - continuous_func(tx - dx)) / (2 * dx)
            tangent_line = Line(
                axes.c2p(tx - 1.5, ty - dy * 1.5),
                axes.c2p(tx + 1.5, ty + dy * 1.5),
                color=COLOR_DIFF,
                stroke_width=2.5,
                stroke_opacity=0.8
            )
            # 添加切点标记
            tangent_dot = Dot(
                axes.c2p(tx, ty),
                color=COLOR_DIFF,
                radius=0.08,
                fill_opacity=0.9
            )
            tangent_lines_group.add(tangent_line, tangent_dot)
        
        subtitle_mgr.show(
            "它告诉我们函数在每一点的瞬时变化率",
            duration=4.0,
            wait_after=1.0
        )
        
        # 【审美优化】逐步展示切线，使用 LaggedStart
        self.play(
            LaggedStart(
                *[Create(tangent_lines_group[i]) for i in range(len(tangent_lines_group))],
                lag_ratio=0.2,
                run_time=2.5,
                rate_func=smooth
            )
        )
        self.wait(1.5)
        
        # 淡出切线，准备下一步
        self.play(
            FadeOut(tangent_lines_group, shift=DOWN*0.2),
            run_time=1,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 2: 动态切线演示（约5秒）
        # ====================================================================
        
        # 创建动态切线追踪器
        tangent_tracker = ValueTracker(2)
        
        def get_tangent():
            x = tangent_tracker.get_value()
            y = continuous_func(x)
            dx = 0.01
            dy = (continuous_func(x + dx) - continuous_func(x - dx)) / (2 * dx)
            line = Line(
                axes.c2p(x - 1.5, y - dy * 1.5),
                axes.c2p(x + 1.5, y + dy * 1.5),
                color=COLOR_DIFF,
                stroke_width=2.5
            )
            return line
        
        tangent_line = always_redraw(get_tangent)
        
        # 斜率显示
        slope_text = always_redraw(lambda: MathTex(
            f"f'({tangent_tracker.get_value():.1f}) = {((continuous_func(tangent_tracker.get_value() + 0.01) - continuous_func(tangent_tracker.get_value() - 0.01)) / 0.02):.2f}",
            font_size=28,
            color=COLOR_DIFF
        ).next_to(tangent_line, UP, buff=0.4))
        
        # 切点标记
        tangent_dot_dynamic = always_redraw(lambda: Dot(
            axes.c2p(tangent_tracker.get_value(), continuous_func(tangent_tracker.get_value())),
            color=COLOR_DIFF,
            radius=0.08,
            fill_opacity=0.9
        ))
        
        self.add(tangent_line, slope_text, tangent_dot_dynamic)
        
        # 【审美优化】切线滑动动画，配合字幕
        subtitle_mgr.show(
            "当切线沿着曲线滑动时，斜率在变化",
            duration=3.5,
            wait_after=0.5
        )
        
        self.play(
            tangent_tracker.animate.set_value(8),
            run_time=3,
            rate_func=smooth
        )
        self.wait(1)
        
        # ====================================================================
        # Part 3: 采样定理引入（约10秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "但现实世界是离散的",
            duration=2.5,
            wait_after=1.0
        )
        
        # Act 2: 幽灵变换 - 离散采样
        ghost_graph = func_continuous.copy()
        ghost_graph.set_stroke(color=COLOR_CONTINUOUS, width=3, opacity=1)
        
        # 创建离散采样点
        num_samples = 10
        x_samples = np.linspace(0, 10, num_samples)
        discrete_stems = VGroup()
        
        # 【审美优化】采样点和线的样式优化
        for x in x_samples:
            y = continuous_func(x)
            start_point = axes.c2p(x, 0)
            end_point = axes.c2p(x, y)
            stem = Line(
                start_point, 
                end_point, 
                color=COLOR_DISCRETE, 
                stroke_width=2.5,
                stroke_opacity=0.9  # 略微降低透明度
            )
            dot = Dot(
                end_point, 
                color=COLOR_DISCRETE, 
                radius=0.06,  # 略微增大
                fill_opacity=0.9  # 降低透明度
            )
            discrete_stems.add(stem, dot)
        
        # 【关键修复】先添加物体，再播放动画
        self.add(ghost_graph)
        
        subtitle_mgr.show(
            "连续曲线被采样成离散的点",
            duration=3.5,
            wait_after=0.5
        )
        
        # 【审美优化】同步展示采样过程
        self.play(
            func_continuous.animate.set_opacity(0),
            ghost_graph.animate.set_stroke(
                color=COLOR_GHOST, 
                width=1, 
                opacity=OPACITY_GHOST
            ),
            LaggedStart(
                *[Create(discrete_stems[i]) for i in range(len(discrete_stems))],
                lag_ratio=0.05,  # 快速连续出现
                run_time=2,
                rate_func=smooth
            ),
            run_time=2.5,
            rate_func=smooth
        )
        self.wait(1)
        
        # 展示不同采样率的效果对比
        subtitle_mgr.show(
            "奈奎斯特定理告诉我们，采样频率必须足够高",
            duration=4.5,
            wait_after=1.0
        )
        
        # 【审美优化】创建三个不同采样率的对比
        sampling_comparison = VGroup()
        sample_rates = [5, 10, 20]  # 不同采样点数
        
        # 需要先定义 continuous_func，确保在所有作用域可用
        def continuous_func_local(x):
            return 2 + np.sin(x * 0.5) + 0.5 * np.sin(x)
        
        for idx, n_samples in enumerate(sample_rates):
            x_samples_comp = np.linspace(0, 10, n_samples)
            comparison_axes = Axes(
                x_range=[0, 10, 2],
                y_range=[-1, 5, 2],
                x_length=3,
                y_length=2,
                axis_config={
                    "stroke_opacity": 0.3,  # 【审美优化】降低透明度
                    "stroke_width": 0.8,  # 【审美优化】降低线宽
                    "stroke_color": GREY_C  # 【审美优化】降低亮度
                },
                tips=False
            ).scale(0.8)
            
            # 离散点
            comparison_points = VGroup()
            for x in x_samples_comp:
                y = continuous_func_local(x)  # 使用本地函数
                dot = Dot(
                    comparison_axes.c2p(x, y),
                    color=COLOR_DISCRETE,
                    radius=0.04,  # 【审美优化】适中大小
                    fill_opacity=0.9  # 【审美优化】略微降低透明度
                )
                comparison_points.add(dot)
            
            # 采样率标签
            rate_label = Text(
                f"{n_samples}点",
                font_size=18,
                color=GREY_C  # 【审美优化】使用灰色
            ).next_to(comparison_axes, DOWN, buff=0.3)  # 【审美优化】增加间距
            
            comparison_group = VGroup(comparison_axes, comparison_points, rate_label)
            sampling_comparison.add(comparison_group)
        
        # 【审美优化】使用相对排版
        sampling_comparison.arrange(RIGHT, buff=0.8, aligned_edge=ORIGIN)
        sampling_comparison.move_to(ORIGIN + DOWN * 1)
        
        # 淡出当前场景，展示对比
        self.play(
            FadeOut(VGroup(axes, axes_labels, ghost_graph, discrete_stems, tangent_line, slope_text, tangent_dot_dynamic), shift=UP*0.3),
            run_time=1,
            rate_func=smooth
        )
        
        # 【审美优化】逐步展示不同采样率
        self.play(
            LaggedStart(
                *[FadeIn(sampling_comparison[i], shift=UP*0.3, scale=0.7) for i in range(len(sampling_comparison))],
                lag_ratio=0.3,
                run_time=2.5,
                rate_func=smooth
            )
        )
        self.wait(2)
        
        # 淡出对比
        self.play(
            FadeOut(sampling_comparison, shift=DOWN*0.3),
            run_time=1,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 4: 问题深化（约10秒）
        # ====================================================================
        
        # 重新创建主要场景
        # 【注意】确保 continuous_func 可用
        axes = Axes(
            x_range=[-1, 11, 1],
            y_range=[-1, 5, 1],
            x_length=12,
            y_length=5,
            axis_config={
                "stroke_opacity": 0.4,  # 【审美优化】降低透明度
                "stroke_width": 1,  # 【审美优化】降低线宽
                "stroke_color": GREY_C  # 【审美优化】降低亮度
            },
            tips=False
        )
        
        ghost_graph = axes.plot(
            continuous_func,  # 使用外层的 continuous_func
            x_range=[0, 10],
            color=COLOR_GHOST,
            stroke_width=1,
            stroke_opacity=OPACITY_GHOST
        )
        
        num_samples = 10
        x_samples = np.linspace(0, 10, num_samples)
        discrete_stems = VGroup()
        
        for x in x_samples:
            y = continuous_func(x)  # 使用外层的 continuous_func
            start_point = axes.c2p(x, 0)
            end_point = axes.c2p(x, y)
            stem = Line(start_point, end_point, color=COLOR_DISCRETE, stroke_width=2.5, stroke_opacity=0.9)
            dot = Dot(end_point, color=COLOR_DISCRETE, radius=0.06, fill_opacity=0.9)
            discrete_stems.add(stem, dot)
        
        scene_group = VGroup(axes, ghost_graph, discrete_stems)
        
        subtitle_mgr.show(
            "在离散世界中，最小的距离是1个像素",
            duration=3.5,
            wait_after=1.0
        )
        
        # 展示场景
        self.play(
            FadeIn(scene_group, scale=0.8),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(0.5)
        
        # 聚焦到三个相邻采样点
        focus_point = axes.c2p(5, continuous_func(5))
        focus_index = 5  # 中间点的索引
        
        # 高亮三个相邻点
        highlight_stems = VGroup()
        highlight_dots = VGroup()
        for i in [focus_index-1, focus_index, focus_index+1]:
            x = x_samples[i]
            y = continuous_func(x)
            start_point = axes.c2p(x, 0)
            end_point = axes.c2p(x, y)
            stem = Line(start_point, end_point, color=YELLOW_C, stroke_width=3, stroke_opacity=0.9)
            dot = Dot(end_point, color=YELLOW_C, radius=0.1, fill_opacity=0.9)
            highlight_stems.add(stem)
            highlight_dots.add(dot)
        
        # 【审美优化】高亮框
        focus_rect = SurroundingRectangle(
            highlight_dots,
            color=YELLOW_C,
            buff=0.4,
            stroke_width=3,
            corner_radius=0.15
        )
        
        self.play(
            Create(highlight_stems),
            Create(highlight_dots),
            Create(focus_rect),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(1)
        
        subtitle_mgr.show(
            "我们无法取极限 Δx → 0",
            duration=3.0,
            wait_after=1.0
        )
        
        # 显示 Δx = 1 的约束
        # 计算相邻两点间的距离
        x1 = x_samples[focus_index]
        x2 = x_samples[focus_index + 1]
        delta_x_line = Line(
            axes.c2p(x1, -0.5),
            axes.c2p(x2, -0.5),
            color=RED_C,
            stroke_width=3
        )
        
        delta_x_label = MathTex(
            "\\Delta x = 1",
            font_size=28,
            color=RED_C
        ).next_to(delta_x_line, DOWN, buff=0.3)
        
        delta_x_arrow1 = Arrow(
            axes.c2p(x1, -0.5) + UP*0.1,
            axes.c2p(x1, -0.5),
            color=RED_C,
            stroke_width=2,
            buff=0,
            max_tip_length_to_length_ratio=0.2
        )
        
        delta_x_arrow2 = Arrow(
            axes.c2p(x2, -0.5) + UP*0.1,
            axes.c2p(x2, -0.5),
            color=RED_C,
            stroke_width=2,
            buff=0,
            max_tip_length_to_length_ratio=0.2
        )
        
        delta_x_group = VGroup(delta_x_line, delta_x_label, delta_x_arrow1, delta_x_arrow2)
        
        self.play(
            Create(delta_x_group),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(2)
        
        # ====================================================================
        # Part 5: 聚焦困境（约5秒）
        # ====================================================================
        
        # 放大聚焦
        question_mark = MathTex(
            "?",
            font_size=72,
            color=YELLOW_C  # 【审美优化】使用柔和色
        ).move_to(UP * 1.5)
        
        subtitle_mgr.show(
            "在离散世界中，如何找回导数？",
            duration=3.5,
            wait_after=1.5
        )
        
        # 【核心修复】不要动相机，改为动物体
        full_scene = VGroup(
            scene_group, 
            highlight_stems, 
            highlight_dots, 
            focus_rect, 
            delta_x_group
        )
        
        self.play(
            full_scene.animate.scale(2.2, about_point=focus_point).shift(ORIGIN - focus_point),
            FadeIn(question_mark, shift=UP*0.3, scale=0.7),
            run_time=2.5,
            rate_func=smooth
        )
        self.wait(2)
        
        # 清理
        self.play(
            FadeOut(full_scene, shift=DOWN*0.3),
            FadeOut(question_mark, shift=UP*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # 清理字幕
        subtitle_mgr.clear()
        
        # 场景结束
        self.wait(1)

    # ========================================================================
    # Scene 2: 泰勒展开推导（扩展版）
    # ========================================================================
    
    def transition_1_2(self):
        """Scene 1 到 Scene 2 的过渡"""
        self.wait(0.5)
    
    def setup_scene_2_taylor(self):
        """Scene 2: 泰勒展开推导中心差分（扩展版，约70秒）"""
        
        subtitle_mgr = SubtitleManager(self)
        
        # ====================================================================
        # Part 1: 泰勒公式的直观理解（约15秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "泰勒公式告诉我们，任何光滑函数都可以用多项式近似",
            duration=4.5,
            wait_after=1.0
        )
        
        # 【审美优化】展示几个函数的泰勒近似
        # 创建三个函数的对比展示
        taylor_examples = VGroup()
        example_functions = [
            ("\\sin(x)", lambda x: np.sin(x), BLUE_C),
            ("\\cos(x)", lambda x: np.cos(x), GREEN_C),
            ("e^x", lambda x: np.exp(x) * 0.3, RED_C)  # 缩放以便可视化
        ]
        
        for idx, (func_label, func, color) in enumerate(example_functions):
            # 创建小的坐标轴
            example_axes = Axes(
                x_range=[-2, 2, 1],
                y_range=[-1.5, 1.5, 1],
                x_length=2.5,
                y_length=2,
                axis_config={
                    "stroke_opacity": 0.3,  # 【审美优化】降低透明度
                    "stroke_width": 0.8,
                    "stroke_color": GREY_C
                },
                tips=False
            ).scale(0.6)
            
            # 绘制函数
            func_graph = example_axes.plot(
                func,
                x_range=[-2, 2],
                color=color,
                stroke_width=2.5  # 【审美优化】主角更粗
            )
            
            # 函数标签
            label = MathTex(
                func_label,
                font_size=20,
                color=color
            ).next_to(example_axes, DOWN, buff=0.3)
            
            example_group = VGroup(example_axes, func_graph, label)
            taylor_examples.add(example_group)
        
        # 【审美优化】使用相对排版
        taylor_examples.arrange(RIGHT, buff=1.0, aligned_edge=ORIGIN)
        taylor_examples.move_to(ORIGIN)
        
        # 【审美优化】同步展示：字幕和画面一起出现
        self.play(
            LaggedStart(
                *[FadeIn(taylor_examples[i], shift=UP*0.3, scale=0.7) for i in range(len(taylor_examples))],
                lag_ratio=0.3,
                run_time=2.5,
                rate_func=smooth
            )
        )
        self.wait(2)
        
        subtitle_mgr.show(
            "在 x 附近，函数值可以用各阶导数表示",
            duration=4.0,
            wait_after=1.0
        )
        
        # 淡出示例
        self.play(
            FadeOut(taylor_examples, shift=DOWN*0.3),
            run_time=1.2,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 2: 详细的展开过程（约15秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "让我们详细展开 f(x+1)",
            duration=3.0,
            wait_after=1.0
        )
        
        # 创建辅助坐标系（用于可视化说明）
        # 【审美优化】辅助元素降亮度
        axes = Axes(
            x_range=[-1, 3, 1],
            y_range=[-1, 3, 1],
            x_length=4,
            y_length=3,
            axis_config={
                "stroke_opacity": 0.3,  # 【审美优化】降低透明度
                "stroke_width": 0.8,
                "stroke_color": GREY_C
            },
            tips=False
        ).scale(0.7).to_edge(LEFT, buff=1)
        
        # 抛物线辅助说明（前向）
        parabola_forward = axes.plot(
            lambda x: 1 + 0.5 * (x - 1) ** 2,
            x_range=[-0.5, 2.5],
            color=COLOR_CONTINUOUS,
            stroke_width=2,
            stroke_opacity=0.6  # 【审美优化】降低透明度
        )
        
        # 前向展开公式
        # 【审美优化】分步揭示公式
        taylor_forward_parts = [
            MathTex("f(x+1)", font_size=36, color=COLOR_CONTINUOUS),
            MathTex("\\approx", font_size=36, color=WHITE),
            MathTex("f(x)", font_size=36, color=GREY_C),
            MathTex("+", font_size=36, color=WHITE),
            MathTex("f'(x)", font_size=36, color=COLOR_DIFF),
            MathTex("+", font_size=36, color=WHITE),
            MathTex("\\frac{1}{2}f''(x)", font_size=36, color=GREY_C),
        ]
        
        # 【审美优化】使用相对排版
        taylor_forward = VGroup(*taylor_forward_parts)
        taylor_forward.arrange(RIGHT, buff=0.3, aligned_edge=ORIGIN)
        taylor_forward.move_to(ORIGIN + UP * 1.5)
        
        # 逐步展示公式
        self.play(
            Create(axes),
            Create(parabola_forward),
            run_time=1,
            rate_func=smooth
        )
        
        # 分步写出公式（逐项出现）
        self.play(
            Write(taylor_forward_parts[0]),  # f(x+1)
            run_time=1,
            rate_func=smooth
        )
        self.wait(0.3)
        
        self.play(
            Write(taylor_forward_parts[1]),  # ≈
            run_time=0.5,
            rate_func=smooth
        )
        self.wait(0.3)
        
        # 解释每一项
        self.play(
            Write(taylor_forward_parts[2]),  # f(x)
            run_time=0.8,
            rate_func=smooth
        )
        
        # 标注 f(x)：当前点的函数值
        f_x_label = Text("当前点的函数值", font_size=20, color=GREY_C)
        f_x_label.next_to(taylor_forward_parts[2], DOWN, buff=0.4, aligned_edge=ORIGIN)
        f_x_label_bg = BackgroundRectangle(f_x_label, color=BLACK, fill_opacity=0.7, buff=0.1)
        f_x_label_group = VGroup(f_x_label_bg, f_x_label)
        
        self.play(
            FadeIn(f_x_label_group, shift=UP*0.2),
            run_time=0.8,
            rate_func=smooth
        )
        self.wait(1)
        self.play(
            FadeOut(f_x_label_group, shift=DOWN*0.2),
            run_time=0.5,
            rate_func=smooth
        )
        
        self.play(
            Write(taylor_forward_parts[3]),  # +
            run_time=0.3,
            rate_func=smooth
        )
        self.wait(0.2)
        
        self.play(
            Write(taylor_forward_parts[4]),  # f'(x)
            run_time=0.8,
            rate_func=smooth
        )
        
        # 标注 f'(x)：一阶导数，线性项
        f_prime_label = Text("一阶导数，线性项", font_size=20, color=COLOR_DIFF)
        f_prime_label.next_to(taylor_forward_parts[4], DOWN, buff=0.4, aligned_edge=ORIGIN)
        f_prime_label_bg = BackgroundRectangle(f_prime_label, color=BLACK, fill_opacity=0.7, buff=0.1)
        f_prime_label_group = VGroup(f_prime_label_bg, f_prime_label)
        
        self.play(
            FadeIn(f_prime_label_group, shift=UP*0.2),
            run_time=0.8,
            rate_func=smooth
        )
        self.wait(1)
        self.play(
            FadeOut(f_prime_label_group, shift=DOWN*0.2),
            run_time=0.5,
            rate_func=smooth
        )
        
        self.play(
            Write(taylor_forward_parts[5]),  # +
            run_time=0.3,
            rate_func=smooth
        )
        self.wait(0.2)
        
        self.play(
            Write(taylor_forward_parts[6]),  # 1/2 f''(x)
            run_time=1,
            rate_func=smooth
        )
        
        # 标注 f''(x)：二阶导数，二次项
        f_double_label = Text("二阶导数，二次项", font_size=20, color=GREY_C)
        f_double_label.next_to(taylor_forward_parts[6], DOWN, buff=0.4, aligned_edge=ORIGIN)
        f_double_label_bg = BackgroundRectangle(f_double_label, color=BLACK, fill_opacity=0.7, buff=0.1)
        f_double_label_group = VGroup(f_double_label_bg, f_double_label)
        
        self.play(
            FadeIn(f_double_label_group, shift=UP*0.2),
            run_time=0.8,
            rate_func=smooth
        )
        self.wait(1.5)
        self.play(
            FadeOut(f_double_label_group, shift=DOWN*0.2),
            run_time=0.5,
            rate_func=smooth
        )
        
        subtitle_mgr.show(
            "类似地，我们可以展开 f(x-1)",
            duration=3.5,
            wait_after=1.0
        )
        
        # 后向展开公式
        taylor_backward_parts = [
            MathTex("f(x-1)", font_size=36, color=COLOR_CONTINUOUS),
            MathTex("\\approx", font_size=36, color=WHITE),
            MathTex("f(x)", font_size=36, color=GREY_C),
            MathTex("-", font_size=36, color=WHITE),
            MathTex("f'(x)", font_size=36, color=COLOR_DIFF),
            MathTex("+", font_size=36, color=WHITE),
            MathTex("\\frac{1}{2}f''(x)", font_size=36, color=GREY_C),
        ]
        
        taylor_backward = VGroup(*taylor_backward_parts)
        taylor_backward.arrange(RIGHT, buff=0.3, aligned_edge=ORIGIN)
        taylor_backward.move_to(ORIGIN + DOWN * 1.5)
        
        # 后向抛物线
        parabola_backward = axes.plot(
            lambda x: 1 + 0.5 * (x + 1) ** 2,
            x_range=[-2.5, 0.5],
            color=RED_C,
            stroke_width=2,
            stroke_opacity=0.6
        )
        
        # 【审美优化】逐步展示后向公式
        self.play(
            Create(parabola_backward),
            run_time=0.8,
            rate_func=smooth
        )
        
        # 快速写出后向公式（因为是类似的）
        self.play(
            LaggedStart(
                *[Write(part) for part in taylor_backward_parts],
                lag_ratio=0.15,
                run_time=3,
                rate_func=smooth
            )
        )
        self.wait(1.5)
        
        # ====================================================================
        # Part 3: 抵消过程的详细说明（约15秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "当我们计算 f(x+1) - f(x-1) 时",
            duration=3.5,
            wait_after=1.0
        )
        
        # 展示相减过程
        # 先创建减法公式
        subtraction_formula = MathTex(
            "f(x+1)", "-", "f(x-1)",
            font_size=40,
            color=WHITE
        ).move_to(ORIGIN + UP * 2)
        
        self.play(
            FadeOut(axes),
            FadeOut(parabola_forward),
            FadeOut(parabola_backward),
            run_time=1,
            rate_func=smooth
        )
        
        # 【修复】直接淡出，然后淡入减法公式（避免 TransformMatchingTex 问题）
        self.play(
            FadeOut(taylor_forward, shift=UP*0.3),
            FadeOut(taylor_backward, shift=DOWN*0.3),
            run_time=1,
            rate_func=smooth
        )
        
        self.play(
            FadeIn(subtraction_formula, shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(1)
        
        # 重新显示两个公式（用于展示抵消）
        # 【重要】使用 get_part_by_tex 来可靠地查找公式部分
        taylor_forward_full = MathTex(
            "f(x+1)", "\\approx", "f(x)", "+", "f'(x)", "+", "\\frac{1}{2}f''(x)",
            substrings_to_isolate=["f(x)", "f'(x)", "f''(x)"],
            font_size=36
        ).move_to(ORIGIN + UP * 1.5)
        
        taylor_backward_full = MathTex(
            "f(x-1)", "\\approx", "f(x)", "-", "f'(x)", "+", "\\frac{1}{2}f''(x)",
            substrings_to_isolate=["f(x)", "f'(x)", "f''(x)"],
            font_size=36
        ).move_to(ORIGIN + DOWN * 0.5)
        
        # 减号
        minus_sign = MathTex("-", font_size=40, color=WHITE).move_to(ORIGIN)
        
        # 淡入两个公式
        self.play(
            FadeOut(subtraction_formula, shift=UP*0.3),
            FadeIn(taylor_forward_full, shift=UP*0.3),
            FadeIn(minus_sign, shift=UP*0.3),
            FadeIn(taylor_backward_full, shift=UP*0.3),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.8)
        
        subtitle_mgr.show(
            "相同的项会相互抵消",
            duration=3.0,
            wait_after=0.8
        )
        
        # 找到相同的项
        try:
            f_x_forward_part = taylor_forward_full.get_part_by_tex("f(x)")
            f_x_backward_part = taylor_backward_full.get_part_by_tex("f(x)")
        except:
            # 如果 get_part_by_tex 不支持，使用索引（向后兼容）
            f_x_forward_part = taylor_forward_full[2] if len(taylor_forward_full) > 2 else taylor_forward_full
            f_x_backward_part = taylor_backward_full[2] if len(taylor_backward_full) > 2 else taylor_backward_full
        
        try:
            f_double_forward_part = taylor_forward_full.get_part_by_tex("f''(x)")
            f_double_backward_part = taylor_backward_full.get_part_by_tex("f''(x)")
        except:
            f_double_forward_part = taylor_forward_full[-1] if len(taylor_forward_full) > 0 else taylor_forward_full
            f_double_backward_part = taylor_backward_full[-1] if len(taylor_backward_full) > 0 else taylor_backward_full
        
        # 【审美优化】高亮框：增加 buff 和圆角，使用柔和色
        f_x_forward_rect = SurroundingRectangle(
            f_x_forward_part, 
            color=COLOR_DIFF,  # 【审美优化】使用语义颜色
            buff=0.2,  # 【审美优化】增加内间距
            corner_radius=0.1  # 【审美优化】增加圆角
        )
        f_x_backward_rect = SurroundingRectangle(
            f_x_backward_part, 
            color=COLOR_DIFF,
            buff=0.2,
            corner_radius=0.1
        )
        
        # 【审美优化】添加箭头连接相同项
        arrow_fx = Arrow(
            f_x_forward_part.get_bottom() + DOWN*0.3,
            f_x_backward_part.get_top() + UP*0.3,
            color=COLOR_DIFF,
            stroke_width=2.5,
            buff=0.1,
            stroke_opacity=0.8
        )
        
        # 相同标签
        same_label_fx = Text(
            "相同",
            font_size=24,  # 【审美优化】增加到24pt，确保可读性
            color=COLOR_DIFF
        ).next_to(arrow_fx, LEFT, buff=0.3)  # 【审美优化】增加间距
        same_label_fx_bg = BackgroundRectangle(
            same_label_fx, 
            color=BLACK, 
            fill_opacity=0.7, 
            buff=0.1
        )
        same_label_fx_group = VGroup(same_label_fx_bg, same_label_fx)
        
        # 【审美优化】同步展示：高亮和箭头一起出现
        self.play(
            Create(f_x_forward_rect),
            Create(f_x_backward_rect),
            Create(arrow_fx),
            FadeIn(same_label_fx_group, shift=RIGHT*0.2),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(1.5)  # 【审美优化】增加停顿，让观众理解
        
        # 消失动画
        self.play(
            FadeOut(f_x_forward_rect),
            FadeOut(f_x_backward_rect),
            FadeOut(arrow_fx),
            FadeOut(same_label_fx_group),
            f_x_forward_part.animate.set_opacity(0.3),  # 【审美优化】不完全消失，保持可读性
            f_x_backward_part.animate.set_opacity(0.3),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(0.5)
        
        # 同样处理 f''(x) 项
        f_double_prime_forward_rect = SurroundingRectangle(
            f_double_forward_part, 
            color=COLOR_DIFF,
            buff=0.2,
            corner_radius=0.1
        )
        f_double_prime_backward_rect = SurroundingRectangle(
            f_double_backward_part, 
            color=COLOR_DIFF,
            buff=0.2,
            corner_radius=0.1
        )
        
        arrow_fdouble = Arrow(
            f_double_forward_part.get_bottom() + DOWN*0.3,
            f_double_backward_part.get_top() + UP*0.3,
            color=COLOR_DIFF,
            stroke_width=2.5,
            buff=0.1,
            stroke_opacity=0.8
        )
        
        # 【修复】重新创建标签组（不能直接 copy，位置不对）
        same_label_fdouble = Text(
            "相同",
            font_size=24,
            color=COLOR_DIFF
        ).next_to(arrow_fdouble, LEFT, buff=0.3)
        same_label_fdouble_bg = BackgroundRectangle(
            same_label_fdouble,
            color=BLACK,
            fill_opacity=0.7,
            buff=0.1
        )
        same_label_fdouble_group = VGroup(same_label_fdouble_bg, same_label_fdouble)
        
        self.play(
            Create(f_double_prime_forward_rect),
            Create(f_double_prime_backward_rect),
            Create(arrow_fdouble),
            FadeIn(same_label_fdouble_group, shift=RIGHT*0.2),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(1.5)
        
        self.play(
            FadeOut(f_double_prime_forward_rect),
            FadeOut(f_double_prime_backward_rect),
            FadeOut(arrow_fdouble),
            FadeOut(same_label_fdouble_group),
            f_double_forward_part.animate.set_opacity(0.3),
            f_double_backward_part.animate.set_opacity(0.3),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(1)
        
        # ====================================================================
        # Part 4: 形成差分公式（约10秒）
        # ====================================================================
        
        # Act 3: 算子结晶 - 形成差分公式
        diff_formula = MathTex(
            "f'(x)", "\\approx", "\\frac{f(x+1) - f(x-1)}{2}",
            font_size=42,
            color=WHITE
        ).move_to(ORIGIN)
        
        # 【审美优化】使用 TransformMatchingTex，更平滑的变形
        self.play(
            TransformMatchingTex(
                VGroup(taylor_forward_full, minus_sign, taylor_backward_full),
                diff_formula
            ),
            run_time=2.5,
            rate_func=smooth
        )
        self.wait(1.5)
        
        # ====================================================================
        # Part 5: 系数提取（约5秒）
        # ====================================================================
        
        # 提取系数
        coefficient_text = MathTex(
            "[-1, 0, 1]",
            font_size=32,
            color=YELLOW_C  # 【审美优化】使用柔和色
        ).next_to(diff_formula, DOWN, buff=0.6)
        
        self.play(
            Write(coefficient_text),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(1)
        
        # 系数实体化
        kernel_x = VGroup(
            Integer(-1, color=COLOR_DIFF),
            Integer(0, color=WHITE),
            Integer(1, color=COLOR_DIFF)
        ).arrange(RIGHT, buff=0.6, aligned_edge=ORIGIN)  # 【审美优化】使用相对排版，增加间距
        
        self.play(
            FadeOut(coefficient_text, shift=DOWN*0.3),
            GrowFromCenter(kernel_x),
            run_time=1.2,
            rate_func=smooth
        )
        
        self.play(
            kernel_x.animate.scale(1.4).to_edge(DOWN, buff=0.8),
            run_time=1.5,
            rate_func=smooth
        )
        
        subtitle_mgr.show(
            "这就是中心差分：系数 [-1, 0, 1]",
            duration=3.5,
            wait_after=1.5
        )
        
        self.wait(1)
        
        # ====================================================================
        # Part 6: 误差分析（约10秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "中心差分法只保留了线性项",
            duration=3.5,
            wait_after=1.0
        )
        
        # 展示误差项
        error_explanation = VGroup()
        
        # 误差公式
        # 创建中文标签
        error_label = Text("误差", font_size=32, color=GREY_C)
        # 创建数学公式部分
        error_math = MathTex("= O(\\Delta x^2)", font_size=32, color=GREY_C)

        # 组合在一起
        error_formula = VGroup(error_label, error_math).arrange(RIGHT, buff=0.2)
        error_formula.move_to(ORIGIN + UP * 1)
        
        error_text = Text(
            "高阶项被忽略，误差为二次项",
            font_size=24,
            color=GREY_C
        ).next_to(error_formula, DOWN, buff=0.6)  # 【审美优化】增加间距
        
        # 【审美优化】添加背景
        error_text_bg = BackgroundRectangle(
            error_text,
            color=BLACK,
            fill_opacity=0.7,
            buff=0.15,
            corner_radius=0.05
        )
        
        error_explanation.add(error_formula, error_text_bg, error_text)
        
        self.play(
            diff_formula.animate.scale(0.8).shift(UP * 0.8),
            kernel_x.animate.scale(0.9).shift(UP * 0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        self.play(
            Write(error_formula),
            FadeIn(error_text_bg, shift=UP*0.2),
            Write(error_text),
            run_time=2,
            rate_func=smooth
        )
        self.wait(1.5)
        
        subtitle_mgr.show(
            "但误差很小，足以满足工程应用",
            duration=3.5,
            wait_after=1.5
        )
        
        self.wait(1)
        
        # 清理
        self.play(
            FadeOut(VGroup(diff_formula, coefficient_text, kernel_x, error_explanation), shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # 清理字幕
        subtitle_mgr.clear()
        
        # 场景结束
        self.wait(1)

    # ========================================================================
    # Scene 3: Sobel算子构造（扩展版）
    # ========================================================================
    
    def transition_2_3(self):
        """Scene 2 到 Scene 3 的过渡"""
        self.wait(0.5)
    
    def setup_scene_3_matrices(self):
        """Scene 3: Sobel算子的构造（扩展版，约50秒）"""
        
        subtitle_mgr = SubtitleManager(self)
        
        # ====================================================================
        # Part 1: 高斯平滑的数学原理（约10秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "高斯平滑通过加权平均来减少噪声",
            duration=4.0,
            wait_after=1.0
        )
        
        # 【审美优化】展示高斯核的形状和权重分布
        # 创建高斯函数可视化
        gaussian_axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 1.2, 0.2],
            x_length=6,
            y_length=3,
            axis_config={
                "stroke_opacity": 0.4,  # 【审美优化】降低透明度
                "stroke_width": 1,
                "stroke_color": GREY_C
            },
            tips=False
        )
        
        # 高斯函数：G(x) = exp(-x²/2)
        gaussian_func = gaussian_axes.plot(
            lambda x: np.exp(-x**2 / 2),
            x_range=[-3, 3],
            color=COLOR_SMOOTH,
            stroke_width=3.5  # 【审美优化】主角更粗
        )
        
        # 高斯函数标签
        gaussian_label = MathTex(
            "G(x) = e^{-\\frac{x^2}{2}}",
            font_size=32,
            color=COLOR_SMOOTH
        ).next_to(gaussian_axes, UP, buff=0.4)
        
        # 展示连续高斯函数
        self.play(
            Create(gaussian_axes),
            Create(gaussian_func),
            Write(gaussian_label),
            run_time=2,
            rate_func=smooth
        )
        self.wait(1)
        
        subtitle_mgr.show(
            "权重 [1, 2, 1] 是高斯分布的离散近似",
            duration=4.0,
            wait_after=1.0
        )
        
        # 展示离散权重
        # 创建权重向量
        # 【修复】使用正确的 Matrix 语法（注意：Matrix 需要嵌套列表）
        weight_matrix = Matrix(
            [[1, 2, 1]],
            element_alignment_corner=ORIGIN,
            bracket_v_buff=0.2,
            bracket_h_buff=0.1
        )
        weight_matrix.set_color(COLOR_SMOOTH)  # 【审美优化】使用语义颜色
        
        weight_label = Text(
            "离散权重",
            font_size=24,
            color=COLOR_SMOOTH
        ).next_to(weight_matrix, DOWN, buff=0.5)  # 【审美优化】增加间距
        weight_bg = BackgroundRectangle(
            weight_label,
            color=BLACK,
            fill_opacity=0.7,
            buff=0.15,
            corner_radius=0.05
        )
        weight_label_group = VGroup(weight_bg, weight_label)
        
        weight_group = VGroup(weight_matrix, weight_label_group)
        weight_group.next_to(gaussian_axes, RIGHT, buff=1.0)
        
        # 【审美优化】同步展示：连续和离散一起出现
        self.play(
            FadeIn(weight_group, shift=LEFT*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(2)
        
        # 在连续函数上标注对应的离散点
        # 标注三个点：-1, 0, 1
        gaussian_points = VGroup()
        for x_val in [-1, 0, 1]:
            y_val = np.exp(-x_val**2 / 2)
            point = Dot(
                gaussian_axes.c2p(x_val, y_val),
                color=COLOR_SMOOTH,
                radius=0.08,
                fill_opacity=0.9
            )
            # 添加标签
            label = MathTex(
                f"{x_val}",
                font_size=20,
                color=GREY_C
            ).next_to(point, DOWN, buff=0.15)
            gaussian_points.add(point, label)
        
        self.play(
            LaggedStart(
                *[Create(gaussian_points[i]) for i in range(len(gaussian_points))],
                lag_ratio=0.2,
                run_time=2,
                rate_func=smooth
            )
        )
        self.wait(1.5)
        
        # 淡出
        self.play(
            FadeOut(VGroup(gaussian_axes, gaussian_func, gaussian_label, weight_group, gaussian_points), shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 2: 展示两个向量（约5秒）
        # ====================================================================
        
        # Act 1: 身份确认 - 展示两个向量
        # 【审美优化】使用语义颜色和相对排版
        kernel_x = Matrix(
            [[-1, 0, 1]], 
            element_alignment_corner=ORIGIN,
            bracket_v_buff=0.2,
            bracket_h_buff=0.1
        )
        kernel_x.set_color(COLOR_DIFF)
        kernel_x_label = Brace(kernel_x, DOWN, buff=0.2)  # 【审美优化】增加 buff
        kernel_x_text = Text(
            "微分/高通",
            font_size=24,
            color=COLOR_DIFF
        ).next_to(kernel_x_label, DOWN, buff=0.3)  # 【审美优化】增加间距
        
        kernel_x_group = VGroup(kernel_x, kernel_x_label, kernel_x_text)
        kernel_x_group.to_edge(LEFT, buff=1.0).shift(UP * 1)  # 【审美优化】增加边距
        
        kernel_y = Matrix(
            [[1], [2], [1]], 
            element_alignment_corner=ORIGIN,
            bracket_v_buff=0.1,
            bracket_h_buff=0.1
        )
        kernel_y.set_color(COLOR_SMOOTH)
        kernel_y_label = Brace(kernel_y, RIGHT, buff=0.2)  # 【审美优化】增加 buff
        kernel_y_text = Text(
            "平滑/低通",
            font_size=24,
            color=COLOR_SMOOTH
        ).next_to(kernel_y_label, RIGHT, buff=0.3)  # 【审美优化】增加间距
        
        kernel_y_group = VGroup(kernel_y, kernel_y_label, kernel_y_text)
        kernel_y_group.to_edge(UP, buff=1.0)  # 【审美优化】增加边距
        
        subtitle_mgr.show(
            "Sobel算子由两个向量组成：微分和平滑",
            duration=4.0,
            wait_after=1.0
        )
        
        self.play(
            FadeIn(kernel_x_group, shift=RIGHT*0.5),
            run_time=1.5,
            rate_func=smooth
        )
        self.play(
            FadeIn(kernel_y_group, shift=DOWN*0.5),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(1)
        
        # ====================================================================
        # Part 3: 卷积操作的详细演示（约10秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "Sobel算子通过卷积运算处理图像",
            duration=3.5,
            wait_after=1.0
        )
        
        # 创建3×3窗口可视化
        # 【审美优化】创建一个简单的像素网格演示
        grid_size = 3
        pixel_size = 0.8
        convolution_demo = VGroup()
        
        # 创建像素网格
        pixel_grid = VGroup()
        pixel_values = np.array([
            [100, 150, 100],
            [120, 140, 120],
            [110, 145, 110]
        ])
        
        for i in range(grid_size):
            for j in range(grid_size):
                pixel = Square(
                    side_length=pixel_size,
                    fill_opacity=0.8,
                    stroke_width=1.5,
                    stroke_color=GREY_C,
                    fill_color=interpolate_color(BLACK, WHITE, pixel_values[i, j] / 255)
                )
                pixel.move_to(RIGHT * (j - 1) * pixel_size + UP * (1 - i) * pixel_size)
                
                # 像素值标签（辅助元素降亮度）
                value_label = Text(
                    str(pixel_values[i, j]),
                    font_size=16,
                    color=GREY_C
                ).move_to(pixel.get_center())
                
                pixel_grid.add(pixel, value_label)
        
        convolution_demo.add(pixel_grid)
        convolution_demo.move_to(ORIGIN + RIGHT * 2)
        
        # 创建卷积核标签
        kernel_demo_label = Text(
            "3×3窗口",
            font_size=20,
            color=YELLOW_C
        ).next_to(convolution_demo, UP, buff=0.4)
        kernel_demo_label_bg = BackgroundRectangle(
            kernel_demo_label,
            color=BLACK,
            fill_opacity=0.7,
            buff=0.1,
            corner_radius=0.05
        )
        kernel_demo_label_group = VGroup(kernel_demo_label_bg, kernel_demo_label)
        convolution_demo.add(kernel_demo_label_group)
        
        # 【审美优化】同步展示：向量和卷积演示一起出现
        self.play(
            FadeIn(convolution_demo, shift=LEFT*0.3, scale=0.8),
            run_time=2,
            rate_func=smooth
        )
        self.wait(1)
        
        subtitle_mgr.show(
            "每个像素的新值，是周围9个像素的加权和",
            duration=4.5,
            wait_after=1.0
        )
        
        # 高亮整个3×3窗口
        # 【审美优化】高亮框
        highlight_rect = SurroundingRectangle(
            pixel_grid,  # 高亮整个像素网格
            color=YELLOW_C,
            buff=0.15,  # 【审美优化】增加 buff
            corner_radius=0.1,  # 【审美优化】增加圆角
            stroke_width=3
        )
        
        self.play(
            Create(highlight_rect),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(2)
        
        # 淡出演示
        self.play(
            FadeOut(convolution_demo),
            FadeOut(highlight_rect),
            run_time=1,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 4: 外积演示（约10秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "通过外积运算，我们可以组合这两个向量",
            duration=4.0,
            wait_after=1.0
        )
        
        # 移动两个向量到中心，准备合并
        self.play(
            kernel_x_group.animate.move_to(ORIGIN + LEFT * 2.5),
            kernel_y_group.animate.move_to(ORIGIN + UP * 2),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)
        
        # 演示外积过程
        multiplication_sign = MathTex(
            "\\times",
            font_size=48,
            color=WHITE
        )
        
        # 【审美优化】使用相对排版
        equation_left = VGroup(kernel_x_group, multiplication_sign, kernel_y_group)
        equation_left.arrange(RIGHT, buff=0.8, aligned_edge=ORIGIN)  # 【审美优化】增加间距
        equation_left.move_to(ORIGIN + UP * 0.5)
        
        self.play(
            Write(multiplication_sign),
            run_time=0.8,
            rate_func=smooth
        )
        self.wait(1)
        
        # 计算外积结果
        sobel_matrix_values = [
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ]
        
        kernel_sobel = IntegerMatrix(
            sobel_matrix_values,
            element_alignment_corner=ORIGIN
        ).scale(0.9)  # 【审美优化】稍微放大
        
        # 设置颜色（混合两种颜色）
        # 【审美优化】使用语义颜色，但这里用渐变更美观
        kernel_sobel.set_color_by_gradient(COLOR_DIFF, GOLD_C, COLOR_SMOOTH)
        
        result_text = MathTex("=", font_size=48, color=WHITE)
        
        # 【审美优化】使用相对排版
        equation_full = VGroup(equation_left, result_text, kernel_sobel)
        equation_full.arrange(RIGHT, buff=0.6, aligned_edge=ORIGIN)
        equation_full.move_to(ORIGIN)
        
        self.play(
            Write(result_text),
            FadeIn(kernel_sobel, shift=RIGHT*0.3),
            run_time=2,
            rate_func=smooth
        )
        self.wait(1.5)
        
        # ====================================================================
        # Part 5: 可分离性的实际意义（约10秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "可分离性让计算更高效",
            duration=3.0,
            wait_after=1.0
        )
        
        # 展示计算量对比
        # 分离前：3×3 = 9 次乘法
        non_separable = VGroup()
        non_sep_label = Text(
            "分离前：3×3 = 9次乘法",
            font_size=24,
            color=RED_C
        )
        non_sep_example = MathTex(
            "3 \\times 3 = 9",
            font_size=32,
            color=RED_C
        ).next_to(non_sep_label, DOWN, buff=0.4)
        non_separable.add(non_sep_label, non_sep_example)
        non_separable.move_to(ORIGIN + LEFT * 2.5)
        
        # 分离后：3 + 3 = 6 次乘法
        separable = VGroup()
        sep_label = Text(
            "分离后：3 + 3 = 6次乘法",
            font_size=24,
            color=COLOR_SMOOTH
        )
        sep_example = MathTex(
            "3 + 3 = 6",
            font_size=32,
            color=COLOR_SMOOTH
        ).next_to(sep_label, DOWN, buff=0.4)
        separable.add(sep_label, sep_example)
        separable.move_to(ORIGIN + RIGHT * 2.5)
        
        # 箭头
        arrow_sep = Arrow(
            non_separable.get_right() + RIGHT * 0.3,
            separable.get_left() + LEFT * 0.3,
            color=YELLOW_C,
            stroke_width=3,
            buff=0
        )
        
        # 【审美优化】先淡出当前场景
        self.play(
            kernel_x_group.animate.scale(0.7).move_to(ORIGIN + LEFT * 3 + UP * 1),
            kernel_y_group.animate.scale(0.7).move_to(ORIGIN + LEFT * 3 + DOWN * 1),
            multiplication_sign.animate.scale(0.7).move_to(ORIGIN + LEFT * 3),
            result_text.animate.scale(0.7).move_to(ORIGIN + LEFT * 1),
            kernel_sobel.animate.scale(0.7).move_to(ORIGIN + LEFT * 0.5),
            run_time=1.5,
            rate_func=smooth
        )
        
        # 【审美优化】同步展示：分离前后对比
        self.play(
            FadeIn(non_separable, shift=UP*0.3),
            FadeIn(arrow_sep, shift=DOWN*0.3),
            FadeIn(separable, shift=UP*0.3),
            run_time=2,
            rate_func=smooth
        )
        self.wait(1.5)
        
        subtitle_mgr.show(
            "从 9 次乘法减少到 6 次",
            duration=3.0,
            wait_after=1.5
        )
        
        # 高亮效率提升
        efficiency_text = Text(
            "效率提升 33%",
            font_size=28,
            color=YELLOW_C
        ).move_to(ORIGIN + DOWN * 2)
        efficiency_bg = BackgroundRectangle(
            efficiency_text,
            color=BLACK,
            fill_opacity=0.7,
            buff=0.2,
            corner_radius=0.1
        )
        efficiency_group = VGroup(efficiency_bg, efficiency_text)
        
        self.play(
            FadeIn(efficiency_group, shift=UP*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(2)
        
        # ====================================================================
        # Part 6: 矩阵高亮（约5秒）
        # ====================================================================
        
        # 回到完整矩阵，高亮结构
        self.play(
            FadeOut(non_separable),
            FadeOut(separable),
            FadeOut(arrow_sep),
            FadeOut(efficiency_group),
            run_time=1,
            rate_func=smooth
        )
        
        # 恢复矩阵显示
        self.play(
            kernel_x_group.animate.scale(1/0.7).move_to(ORIGIN + LEFT * 2.5),
            kernel_y_group.animate.scale(1/0.7).move_to(ORIGIN + UP * 2),
            multiplication_sign.animate.scale(1/0.7).move_to(equation_left[1].get_center()),
            result_text.animate.scale(1/0.7).move_to(ORIGIN + RIGHT * 0.5),
            kernel_sobel.animate.scale(1/0.7).move_to(ORIGIN + RIGHT * 2),
            run_time=1.5,
            rate_func=smooth
        )
        
        subtitle_mgr.show(
            "这就是完整的Sobel算子：一手抓变化，一手抓平稳",
            duration=4.5,
            wait_after=2.0
        )
        
        # 【审美优化】高亮框显示矩阵结构
        sobel_rect = SurroundingRectangle(
            kernel_sobel,
            color=YELLOW_C,
            buff=0.3,  # 【审美优化】增加 buff
            corner_radius=0.15,  # 【审美优化】增加圆角
            stroke_width=3
        )
        
        self.play(
            Create(sobel_rect),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(2)
        
        # 清理
        self.play(
            FadeOut(VGroup(
                kernel_x_group, kernel_y_group, multiplication_sign,
                result_text, kernel_sobel, sobel_rect
            ), shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # 清理字幕
        subtitle_mgr.clear()
        
        # 场景结束
        self.wait(1)

    # ========================================================================
    # Scene 4: 3D可视化应用（扩展版）
    # ========================================================================
    
    def transition_3_4(self):
        """Scene 3 到 Scene 4 的过渡"""
        self.wait(0.5)
    
    def setup_scene_4_vision(self):
        """Scene 4: 3D可视化与应用（扩展版，约75秒）"""
        
        subtitle_mgr = SubtitleManager(self)
        
        # ====================================================================
        # Part 1: 2D到3D的维度转换（约20秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "让我们将图像转换为3D地形",
            duration=3.5,
            wait_after=1.0
        )
        
        # 【关键修复】使用统一的坐标系
        rows, cols = 20, 20
        
        # 统一的高度计算函数（避免坐标系不一致）
        def get_height_data(x, y):
            # 归一化坐标
            u, v = x / cols, y / rows
            # 两个 Sigmoid 叠加形成"台阶" (边缘)
            val = 1 / (1 + np.exp(-15 * (u - 0.3))) + 1 / (1 + np.exp(-15 * (u - 0.7)))
            # 让中间凹陷一点，增加地形复杂度
            return val * 0.5
        
        # 创建 3D 坐标轴（辅助元素降亮度）
        axes_3d = ThreeDAxes(
            x_range=[0, cols, 5],
            y_range=[0, rows, 5],
            z_range=[0, 2, 1],
            x_length=8,
            y_length=8,
            z_length=3,
            axis_config={
                "include_tip": False,
                "stroke_opacity": 0.3,  # 【审美优化】降低透明度
                "stroke_width": 1,
                "stroke_color": GREY_C  # 【审美优化】降低亮度
            }
        )
        
        # Act 1: 2D 像素网格
        pixel_grid = VGroup()
        pixel_size = 0.4
        
        # 使用 axes_3d 的坐标系来定位，确保后续对齐
        for i in range(rows):
            for j in range(cols):
                h = get_height_data(j, i)
                color = interpolate_color(BLACK, WHITE, h)
                # 关键：直接用 axes_3d.c2p 确保位置绝对匹配
                pos = axes_3d.c2p(j, i, 0)
                pixel = Square(
                    side_length=pixel_size,
                    stroke_width=0,
                    fill_opacity=1
                )
                pixel.set_fill(color)
                pixel.move_to(pos)
                pixel_grid.add(pixel)
        
        # 【关键修复】整体居中，保持相对位置不变
        world_group = VGroup(axes_3d, pixel_grid).center()
        
        # 【审美优化】同步展示：字幕和画面一起出现
        self.set_camera_orientation(phi=0, theta=-90*DEGREES)
        self.play(
            FadeIn(pixel_grid, lag_ratio=0.01),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(1)
        
        subtitle_mgr.show(
            "亮度映射为高度，形成3D地形",
            duration=3.5,
            wait_after=1.0
        )
        
        # Act 2: 维度升华
        # 【审美优化】先旋转摄像机，进入 3D 视角
        self.move_camera(
            phi=60*DEGREES,
            theta=-45*DEGREES,
            run_time=2.5,
            rate_func=smooth
        )
        
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
            stroke_color=COLOR_CONTINUOUS,  # 【审美优化】使用语义颜色
            stroke_width=0.5,
            fill_color=COLOR_CONTINUOUS
        )
        
        # 此时 axes_3d 已经被 center() 移动过了，Surface 生成时是基于原始 axes 的
        # 所以 Surface 也需要应用同样的 shift
        surface_center_offset = world_group.get_center()
        terrain_surface.shift(surface_center_offset)
        
        # 【关键修复】使用 Cross Dissolve 替代 ReplacementTransform（避免撕裂）
        self.play(
            FadeIn(axes_3d),
            FadeIn(terrain_surface),
            pixel_grid.animate.set_opacity(OPACITY_GHOST),  # 【审美优化】2D 像素变暗作为地基
            run_time=2,
            rate_func=smooth
        )
        self.wait(1.5)
        
        # ====================================================================
        # Part 2: 全息扫描演示（约15秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "Sobel算子在地形上扫描，实时计算导数",
            duration=4.0,
            wait_after=1.0
        )
        
        # 制作"全息取景框"（四个角标）
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
        
        scanner_box = scanner_corners.set_color(COLOR_SMOOTH).set_stroke(width=4)  # 【审美优化】使用语义颜色
        # 添加激光束
        laser = DashedLine(
            start=ORIGIN + UP*0.5,
            end=ORIGIN + DOWN*2,
            color=COLOR_SMOOTH,  # 【审美优化】使用语义颜色
            stroke_width=2
        )
        scanner = VGroup(scanner_box, laser).rotate(PI/2, axis=RIGHT)  # 躺平
        
        # 制作 HUD 示波器（悬浮在右侧）
        hud_bg = Rectangle(
            width=5,
            height=3,
            color=COLOR_CONTINUOUS,  # 【审美优化】使用语义颜色
            fill_opacity=0.8
        ).set_stroke(width=0)
        hud_bg.to_corner(DR, buff=0.5)
        
        hud_axes = Axes(
            x_range=[0, cols, 5],
            y_range=[-2, 2, 1],
            x_length=4.5,
            y_length=2,
            axis_config={
                "include_tip": False,
                "stroke_opacity": 0.4,  # 【审美优化】降低透明度
                "stroke_width": 1,
                "stroke_color": GREY_C,
                "font_size": 16
            }
        ).move_to(hud_bg)
        
        hud_label = Text(
            "GRADIENT (d/dx)",
            font_size=20,
            color=COLOR_SMOOTH  # 【审美优化】使用语义颜色
        ).next_to(hud_bg, UP, aligned_edge=LEFT)
        hud_group = VGroup(hud_bg, hud_axes, hud_label)
        
        self.add_fixed_in_frame_mobjects(hud_group)  # 固定在屏幕上
        self.play(
            FadeIn(hud_group, shift=LEFT*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # 动画驱动逻辑
        scan_tracker = ValueTracker(0)
        
        def update_scanner(mob):
            u = scan_tracker.get_value()
            v = rows / 2  # 扫描中间行
            
            # 使用统一的高度函数计算精确高度
            z_math = get_height_data(u, v) * 3
            
            # 移动扫描器（悬浮在地形上方 1.0 处）
            base_pos = axes_3d.c2p(u, v, z_math + 1.0)
            pos_3d = base_pos + surface_center_offset
            mob.move_to(pos_3d)
            
            # 激光束伸缩：连接取景器和地面
            ground_pos = axes_3d.c2p(u, v, z_math) + surface_center_offset
            mob[1].put_start_and_end_on(pos_3d, ground_pos)
            
            # 颜色逻辑：导数越大，越红（使用语义颜色）
            delta = 0.1
            deriv = (get_height_data(u + delta, v) - get_height_data(u - delta, v)) / (2 * delta)
            
            if abs(deriv) > 0.02:  # 阈值
                mob[0].set_color(COLOR_DIFF)  # 【审美优化】使用语义颜色
                mob[1].set_color(COLOR_DIFF)
            else:
                mob[0].set_color(COLOR_SMOOTH)
                mob[1].set_color(COLOR_SMOOTH)
        
        scanner.add_updater(update_scanner)
        self.add(scanner)
        
        # 示波器曲线（动态绘制）
        def get_derivative_func(x):
            """计算x位置的导数"""
            delta = 0.1
            return (get_height_data(x + delta, rows/2) - get_height_data(x - delta, rows/2)) / (2 * delta) * 5
        
        graph = always_redraw(lambda: hud_axes.plot(
            get_derivative_func,
            x_range=[0, scan_tracker.get_value() + 0.1],
            color=scanner[0].get_color(),  # 颜色同步
            stroke_width=2.5  # 【审美优化】主角更粗
        ))
        
        # 示波器光点
        graph_dot = always_redraw(lambda: Dot(
            point=hud_axes.c2p(scan_tracker.get_value(), get_derivative_func(scan_tracker.get_value())),
            color=WHITE,
            radius=0.08,
            fill_opacity=0.9
        ))
        
        self.add_fixed_in_frame_mobjects(graph, graph_dot)
        
        # 【审美优化】扫描动画，配合字幕
        self.play(
            scan_tracker.animate.set_value(cols - 1),
            run_time=8,
            rate_func=smooth
        )
        self.wait(2)
        
        # 淡出扫描器
        scanner.remove_updater(update_scanner)
        self.play(
            FadeOut(scanner),
            FadeOut(hud_group),
            FadeOut(graph),
            FadeOut(graph_dot),
            run_time=1.5,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 3: 多张图像的展示（约15秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "让我们看看不同图像的边缘检测效果",
            duration=4.0,
            wait_after=1.0
        )
        
        # 淡出3D场景，回到2D
        self.move_camera(
            phi=0,
            theta=-90*DEGREES,
            run_time=2,
            rate_func=smooth
        )
        
        self.play(
            FadeOut(VGroup(axes_3d, terrain_surface, pixel_grid), shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # 创建不同类型的图像示例（简化版，用网格模拟）
        image_types = [
            ("建筑图像", "垂直边缘多", lambda x, y: 0.5 + 0.5 * np.sign(np.sin(x * 0.3))),
            ("人脸图像", "复杂边缘", lambda x, y: 0.5 + 0.3 * np.sin(x * 0.2) * np.cos(y * 0.2)),
            ("文字图像", "清晰边缘", lambda x, y: 0.3 if (x < 0.4 or x > 0.6) else 0.8)
        ]
        
        image_demos = VGroup()
        
        for idx, (title, desc, func) in enumerate(image_types):
            # 创建小的图像网格
            demo_size = 8
            demo_grid = VGroup()
            for i in range(demo_size):
                for j in range(demo_size):
                    x_norm = j / demo_size
                    y_norm = i / demo_size
                    intensity = func(x_norm * 10, y_norm * 10)
                    color = interpolate_color(BLACK, WHITE, intensity)
                    pixel = Square(
                        side_length=0.15,
                        fill_opacity=1,
                        stroke_width=0
                    )
                    pixel.set_fill(color)
                    pixel.move_to(RIGHT * (j - demo_size/2) * 0.15 + UP * (demo_size/2 - i) * 0.15)
                    demo_grid.add(pixel)
            
            # 标题和描述
            title_text = Text(
                title,
                font_size=18,
                color=WHITE
            )
            desc_text = Text(
                desc,
                font_size=14,
                color=GREY_C  # 【审美优化】降低亮度
            ).next_to(title_text, DOWN, buff=0.2)
            
            demo_group = VGroup(demo_grid, title_text, desc_text)
            demo_group.arrange(DOWN, buff=0.3, aligned_edge=ORIGIN)
            image_demos.add(demo_group)
        
        # 【审美优化】使用相对排版
        image_demos.arrange(RIGHT, buff=1.2, aligned_edge=ORIGIN)
        image_demos.move_to(ORIGIN)
        
        # 【审美优化】同步展示：多张图像一起出现
        self.play(
            LaggedStart(
                *[FadeIn(image_demos[i], shift=UP*0.3, scale=0.8) for i in range(len(image_demos))],
                lag_ratio=0.3,
                run_time=3,
                rate_func=smooth
            )
        )
        self.wait(2)
        
        subtitle_mgr.show(
            "每种图像都有不同的边缘特征",
            duration=3.5,
            wait_after=1.5
        )
        
        self.wait(1)
        
        # 淡出
        self.play(
            FadeOut(image_demos, shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 4: 参数调整的演示（约15秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "我们可以调整Sobel算子的阈值",
            duration=3.5,
            wait_after=1.0
        )
        
        # 创建阈值对比演示
        threshold_demo = VGroup()
        thresholds = [0.3, 0.6, 0.9]
        threshold_labels = ["低阈值", "中阈值", "高阈值"]
        
        for idx, (thresh, label) in enumerate(zip(thresholds, threshold_labels)):
            # 创建简化的边缘检测结果（用网格模拟）
            demo_size = 8
            edge_grid = VGroup()
            for i in range(demo_size):
                for j in range(demo_size):
                    # 模拟边缘检测结果（简化）
                    edge_strength = abs(np.sin(j * 0.5)) * abs(np.cos(i * 0.5))
                    if edge_strength > thresh:
                        color = WHITE
                        opacity = 1
                    else:
                        color = BLACK
                        opacity = 0.1
                    
                    pixel = Square(
                        side_length=0.15,
                        fill_opacity=opacity,
                        stroke_width=0
                    )
                    pixel.set_fill(color)
                    pixel.move_to(RIGHT * (j - demo_size/2) * 0.15 + UP * (demo_size/2 - i) * 0.15)
                    edge_grid.add(pixel)
            
            # 标签
            thresh_label = Text(
                label,
                font_size=18,
                color=WHITE
            )
            thresh_value = Text(
                f"阈值: {thresh}",
                font_size=14,
                color=GREY_C  # 【审美优化】降低亮度
            ).next_to(thresh_label, DOWN, buff=0.2)
            
            thresh_group = VGroup(edge_grid, thresh_label, thresh_value)
            thresh_group.arrange(DOWN, buff=0.3, aligned_edge=ORIGIN)
            threshold_demo.add(thresh_group)
        
        # 【审美优化】使用相对排版
        threshold_demo.arrange(RIGHT, buff=1.0, aligned_edge=ORIGIN)
        threshold_demo.move_to(ORIGIN)
        
        # 【审美优化】同步展示：不同阈值结果一起出现
        self.play(
            LaggedStart(
                *[FadeIn(threshold_demo[i], shift=UP*0.3, scale=0.8) for i in range(len(threshold_demo))],
                lag_ratio=0.3,
                run_time=3,
                rate_func=smooth
            )
        )
        self.wait(2)
        
        subtitle_mgr.show(
            "阈值越高，检测到的边缘越少，但越准确",
            duration=4.0,
            wait_after=1.5
        )
        
        self.wait(1)
        
        # 淡出
        self.play(
            FadeOut(threshold_demo, shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 5: 与其他方法对比（约10秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "Sobel算子只是边缘检测方法之一",
            duration=3.5,
            wait_after=1.0
        )
        
        # 创建方法对比演示
        method_comparison = VGroup()
        methods = [
            ("Sobel", COLOR_DIFF),
            ("Canny", COLOR_SMOOTH),
            ("Prewitt", COLOR_CONTINUOUS)
        ]
        
        for method_name, color in methods:
            # 创建简化的边缘检测结果（用网格模拟）
            demo_size = 8
            method_grid = VGroup()
            for i in range(demo_size):
                for j in range(demo_size):
                    # 模拟不同方法的边缘检测结果（简化）
                    edge_strength = abs(np.sin(j * 0.5)) * abs(np.cos(i * 0.5))
                    if edge_strength > 0.5:
                        pixel_color = color  # 【审美优化】使用不同颜色区分方法
                        opacity = 0.9
                    else:
                        pixel_color = BLACK
                        opacity = 0.1
                    
                    pixel = Square(
                        side_length=0.15,
                        fill_opacity=opacity,
                        stroke_width=0
                    )
                    pixel.set_fill(pixel_color)
                    pixel.move_to(RIGHT * (j - demo_size/2) * 0.15 + UP * (demo_size/2 - i) * 0.15)
                    method_grid.add(pixel)
            
            # 标签
            method_label = Text(
                method_name,
                font_size=20,
                color=color  # 【审美优化】使用语义颜色
            )
            
            method_group = VGroup(method_grid, method_label)
            method_group.arrange(DOWN, buff=0.4, aligned_edge=ORIGIN)
            method_comparison.add(method_group)
        
        # 【审美优化】使用相对排版
        method_comparison.arrange(RIGHT, buff=1.2, aligned_edge=ORIGIN)
        method_comparison.move_to(ORIGIN)
        
        # 【审美优化】同步展示：不同方法一起出现
        self.play(
            LaggedStart(
                *[FadeIn(method_comparison[i], shift=UP*0.3, scale=0.8) for i in range(len(method_comparison))],
                lag_ratio=0.3,
                run_time=2.5,
                rate_func=smooth
            )
        )
        self.wait(2)
        
        subtitle_mgr.show(
            "每种方法都有其适用场景",
            duration=3.5,
            wait_after=2.0
        )
        
        self.wait(1)
        
        # 清理
        self.play(
            FadeOut(method_comparison, shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # 清理字幕
        subtitle_mgr.clear()
        
        # 场景结束
        self.wait(1)

    # ========================================================================
    # Scene 4.5: 实际应用案例（新增）
    # ========================================================================
    
    def transition_4_4_5(self):
        """Scene 4 到 Scene 4.5 的过渡"""
        self.wait(0.5)
    
    def setup_scene_4_5_applications(self):
        """Scene 4.5: 实际应用案例（约60秒）"""
        
        subtitle_mgr = SubtitleManager(self)
        
        # ====================================================================
        # Part 1: 自动驾驶（约20秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "在自动驾驶中，边缘检测用于识别道路边界",
            duration=4.5,
            wait_after=1.0
        )
        
        # 创建道路场景模拟（避免重叠：使用相对排版）
        road_demo = VGroup()
        
        # 道路图像（简化模拟）
        road_size = 10
        road_grid = VGroup()
        for i in range(road_size):
            for j in range(road_size):
                # 模拟道路：中间是道路（亮），两侧是边界（暗）
                road_center = road_size / 2
                dist_from_center = abs(j - road_center)
                
                if dist_from_center < 2:
                    # 道路区域（灰色）
                    intensity = 0.6
                elif dist_from_center < 3:
                    # 边界区域（白色，高边缘）
                    intensity = 1.0
                else:
                    # 背景区域（黑色）
                    intensity = 0.2
                
                color = interpolate_color(BLACK, WHITE, intensity)
                pixel = Square(
                    side_length=0.12,
                    fill_opacity=1,
                    stroke_width=0
                )
                pixel.set_fill(color)
                pixel.move_to(RIGHT * (j - road_size/2) * 0.12 + UP * (road_size/2 - i) * 0.12)
                road_grid.add(pixel)
        
        # 道路标签
        road_label = Text(
            "道路图像",
            font_size=22,
            color=WHITE
        )
        
        # 边缘检测结果（简化模拟）
        edge_size = 10
        edge_grid = VGroup()
        for i in range(edge_size):
            for j in range(edge_size):
                # 在边界处显示边缘
                road_center = edge_size / 2
                dist_from_center = abs(j - road_center)
                
                if 2.5 < dist_from_center < 3.5:
                    # 边缘区域（白色）
                    edge_color = COLOR_DIFF  # 【审美优化】使用语义颜色
                    opacity = 0.9
                else:
                    # 非边缘区域（黑色）
                    edge_color = BLACK
                    opacity = 0.1
                
                pixel = Square(
                    side_length=0.12,
                    fill_opacity=opacity,
                    stroke_width=0
                )
                pixel.set_fill(edge_color)
                pixel.move_to(RIGHT * (j - edge_size/2) * 0.12 + UP * (edge_size/2 - i) * 0.12)
                edge_grid.add(pixel)
        
        # 边缘标签
        edge_label = Text(
            "边缘检测结果",
            font_size=22,
            color=COLOR_DIFF  # 【审美优化】使用语义颜色
        )
        
        # 【避免重叠】使用相对排版：左图像+右图像，上下排列标签
        road_group = VGroup(road_grid, road_label)
        road_group.arrange(DOWN, buff=0.4, aligned_edge=ORIGIN)  # 【审美优化】增加buff
        
        edge_group = VGroup(edge_grid, edge_label)
        edge_group.arrange(DOWN, buff=0.4, aligned_edge=ORIGIN)
        
        # 【避免重叠】两个组并排，整体居中，留出底部空间给字幕
        road_demo = VGroup(road_group, edge_group)
        road_demo.arrange(RIGHT, buff=1.5, aligned_edge=ORIGIN)  # 【审美优化】增加间距
        road_demo.move_to(ORIGIN + UP * 0.3)  # 【避免重叠】稍微上移，给字幕留空间
        
        # 【审美优化】同步展示
        self.play(
            LaggedStart(
                FadeIn(road_group, shift=UP*0.3, scale=0.8),
                FadeIn(edge_group, shift=UP*0.3, scale=0.8),
                lag_ratio=0.4,
                run_time=2.5,
                rate_func=smooth
            )
        )
        self.wait(2)
        
        subtitle_mgr.show(
            "帮助车辆理解周围环境",
            duration=3.5,
            wait_after=1.5
        )
        
        self.wait(1)
        
        # 淡出
        self.play(
            FadeOut(road_demo, shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 2: 医疗影像（约20秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "在医疗影像中，边缘检测用于识别病变区域",
            duration=4.5,
            wait_after=1.0
        )
        
        # 创建医疗影像场景模拟（避免重叠：使用相对排版）
        medical_demo = VGroup()
        
        # X光片图像（简化模拟）
        xray_size = 10
        xray_grid = VGroup()
        for i in range(xray_size):
            for j in range(xray_size):
                # 模拟X光片：背景较暗，骨骼较亮，病变区域有特殊边缘
                center_x, center_y = xray_size/2, xray_size/2
                dist = np.sqrt((j - center_x)**2 + (i - center_y)**2)
                
                # 骨骼区域（环形）
                if 2 < dist < 4:
                    intensity = 0.8  # 骨骼（亮）
                elif 3.5 < dist < 4.5:
                    intensity = 0.4  # 病变边缘（暗边缘）
                elif dist < 2:
                    intensity = 0.5  # 内部区域
                else:
                    intensity = 0.3  # 背景（暗）
                
                color = interpolate_color(BLACK, WHITE, intensity)
                pixel = Square(
                    side_length=0.12,
                    fill_opacity=1,
                    stroke_width=0
                )
                pixel.set_fill(color)
                pixel.move_to(RIGHT * (j - xray_size/2) * 0.12 + UP * (xray_size/2 - i) * 0.12)
                xray_grid.add(pixel)
        
        # X光片标签
        xray_label = Text(
            "X光片图像",
            font_size=22,
            color=WHITE
        )
        
        # 边缘检测结果（突出病变边缘）
        medical_edge_size = 10
        medical_edge_grid = VGroup()
        for i in range(medical_edge_size):
            for j in range(medical_edge_size):
                center_x, center_y = medical_edge_size/2, medical_edge_size/2
                dist = np.sqrt((j - center_x)**2 + (i - center_y)**2)
                
                # 在病变边缘处显示
                if 3.5 < dist < 4.5:
                    # 病变边缘（红色高亮）
                    edge_color = COLOR_DIFF  # 【审美优化】使用语义颜色
                    opacity = 0.95
                else:
                    edge_color = BLACK
                    opacity = 0.1
                
                pixel = Square(
                    side_length=0.12,
                    fill_opacity=opacity,
                    stroke_width=0
                )
                pixel.set_fill(edge_color)
                pixel.move_to(RIGHT * (j - medical_edge_size/2) * 0.12 + UP * (medical_edge_size/2 - i) * 0.12)
                medical_edge_grid.add(pixel)
        
        # 边缘标签
        medical_edge_label = Text(
            "病变区域识别",
            font_size=22,
            color=COLOR_DIFF  # 【审美优化】使用语义颜色
        )
        
        # 【避免重叠】使用相对排版
        xray_group = VGroup(xray_grid, xray_label)
        xray_group.arrange(DOWN, buff=0.4, aligned_edge=ORIGIN)
        
        medical_edge_group = VGroup(medical_edge_grid, medical_edge_label)
        medical_edge_group.arrange(DOWN, buff=0.4, aligned_edge=ORIGIN)
        
        # 【避免重叠】两个组并排，整体居中，留出底部空间给字幕
        medical_demo = VGroup(xray_group, medical_edge_group)
        medical_demo.arrange(RIGHT, buff=1.5, aligned_edge=ORIGIN)  # 【审美优化】增加间距
        medical_demo.move_to(ORIGIN + UP * 0.3)  # 【避免重叠】稍微上移
        
        # 【审美优化】同步展示
        self.play(
            LaggedStart(
                FadeIn(xray_group, shift=UP*0.3, scale=0.8),
                FadeIn(medical_edge_group, shift=UP*0.3, scale=0.8),
                lag_ratio=0.4,
                run_time=2.5,
                rate_func=smooth
            )
        )
        self.wait(2)
        
        subtitle_mgr.show(
            "辅助医生进行诊断",
            duration=3.5,
            wait_after=1.5
        )
        
        self.wait(1)
        
        # 淡出
        self.play(
            FadeOut(medical_demo, shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 3: 机器人视觉（约20秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "在机器人视觉中，边缘检测用于物体识别",
            duration=4.5,
            wait_after=1.0
        )
        
        # 创建机器人视觉场景模拟（避免重叠：使用相对排版）
        robot_demo = VGroup()
        
        # 物体图像（简化模拟）
        object_size = 10
        object_grid = VGroup()
        for i in range(object_size):
            for j in range(object_size):
                # 模拟物体：一个方形的物体
                center_x, center_y = object_size/2, object_size/2
                
                # 创建一个方形物体
                if 2 <= i <= 7 and 2 <= j <= 7:
                    if i == 2 or i == 7 or j == 2 or j == 7:
                        # 物体边缘（亮）
                        intensity = 0.9
                    else:
                        # 物体内部（中等）
                        intensity = 0.6
                else:
                    # 背景（暗）
                    intensity = 0.2
                
                color = interpolate_color(BLACK, WHITE, intensity)
                pixel = Square(
                    side_length=0.12,
                    fill_opacity=1,
                    stroke_width=0
                )
                pixel.set_fill(color)
                pixel.move_to(RIGHT * (j - object_size/2) * 0.12 + UP * (object_size/2 - i) * 0.12)
                object_grid.add(pixel)
        
        # 物体标签
        object_label = Text(
            "物体图像",
            font_size=22,
            color=WHITE
        )
        
        # 边缘检测结果（提取物体轮廓）
        robot_edge_size = 10
        robot_edge_grid = VGroup()
        for i in range(robot_edge_size):
            for j in range(robot_edge_size):
                # 在物体边缘处显示
                if (i == 2 or i == 7 or j == 2 or j == 7) and (2 <= i <= 7 and 2 <= j <= 7):
                    # 物体轮廓（青色高亮）
                    edge_color = COLOR_SMOOTH  # 【审美优化】使用语义颜色
                    opacity = 0.95
                else:
                    edge_color = BLACK
                    opacity = 0.1
                
                pixel = Square(
                    side_length=0.12,
                    fill_opacity=opacity,
                    stroke_width=0
                )
                pixel.set_fill(edge_color)
                pixel.move_to(RIGHT * (j - robot_edge_size/2) * 0.12 + UP * (robot_edge_size/2 - i) * 0.12)
                robot_edge_grid.add(pixel)
        
        # 边缘标签
        robot_edge_label = Text(
            "物体轮廓提取",
            font_size=22,
            color=COLOR_SMOOTH  # 【审美优化】使用语义颜色
        )
        
        # 【避免重叠】使用相对排版
        object_group = VGroup(object_grid, object_label)
        object_group.arrange(DOWN, buff=0.4, aligned_edge=ORIGIN)
        
        robot_edge_group = VGroup(robot_edge_grid, robot_edge_label)
        robot_edge_group.arrange(DOWN, buff=0.4, aligned_edge=ORIGIN)
        
        # 【避免重叠】两个组并排，整体居中，留出底部空间给字幕
        robot_demo = VGroup(object_group, robot_edge_group)
        robot_demo.arrange(RIGHT, buff=1.5, aligned_edge=ORIGIN)  # 【审美优化】增加间距
        robot_demo.move_to(ORIGIN + UP * 0.3)  # 【避免重叠】稍微上移
        
        # 【审美优化】同步展示
        self.play(
            LaggedStart(
                FadeIn(object_group, shift=UP*0.3, scale=0.8),
                FadeIn(robot_edge_group, shift=UP*0.3, scale=0.8),
                lag_ratio=0.4,
                run_time=2.5,
                rate_func=smooth
            )
        )
        self.wait(2)
        
        subtitle_mgr.show(
            "帮助机器人理解物体的形状",
            duration=3.5,
            wait_after=1.5
        )
        
        self.wait(1)
        
        # 清理
        self.play(
            FadeOut(robot_demo, shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # 清理字幕
        subtitle_mgr.clear()
        
        # 场景结束
        self.wait(1)

    # ========================================================================
    # Scene 5: 总结与升华（扩展版）
    # ========================================================================
    
    def transition_4_5_5(self):
        """Scene 4.5 到 Scene 5 的过渡"""
        self.wait(0.5)
    
    def setup_scene_5_outro(self):
        """Scene 5: 总结与升华（扩展版，约60秒）"""
        
        subtitle_mgr = SubtitleManager(self)
        
        # ====================================================================
        # Part 1: 完整回顾（约15秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "让我们回顾整个旅程",
            duration=3.5,
            wait_after=1.0
        )
        
        # 创建回顾元素（避免重叠：使用相对排版）
        recap_elements = VGroup()
        
        # 1. 连续 → 离散
        continuous_label = Text(
            "连续",
            font_size=20,
            color=COLOR_CONTINUOUS  # 【审美优化】使用语义颜色
        )
        arrow1 = Arrow(
            start=RIGHT * 0.3,
            end=LEFT * 0.3,
            color=WHITE,
            stroke_width=2,
            buff=0.1
        )
        discrete_label = Text(
            "离散",
            font_size=20,
            color=COLOR_DISCRETE  # 【审美优化】使用语义颜色
        )
        step1 = VGroup(continuous_label, arrow1, discrete_label)
        step1.arrange(RIGHT, buff=0.2, aligned_edge=ORIGIN)
        
        # 2. 泰勒展开
        taylor_formula = MathTex(
            "f'(x) \\approx \\frac{f(x+1) - f(x-1)}{2}",
            font_size=24,
            color=WHITE
        )
        
        # 3. Sobel算子
        sobel_matrix = IntegerMatrix(
            [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
            element_alignment_corner=ORIGIN,
            bracket_h_buff=0.2,
            bracket_v_buff=0.2
        ).scale(0.5)
        sobel_matrix.set_color(COLOR_DIFF)  # 【审美优化】使用语义颜色
        
        # 4. 边缘检测应用
        edge_icon = VGroup()
        # 创建一个简单的边缘检测图标（简化）
        for i in range(3):
            line = Line(
                start=LEFT * 0.5 + UP * (i - 1) * 0.3,
                end=RIGHT * 0.5 + UP * (i - 1) * 0.3,
                color=COLOR_SMOOTH,  # 【审美优化】使用语义颜色
                stroke_width=3
            )
            edge_icon.add(line)
        
        # 【避免重叠】将所有步骤并排排列，整体居中，留出底部空间给字幕
        recap_elements.add(step1, taylor_formula, sobel_matrix, edge_icon)
        recap_elements.arrange(RIGHT, buff=0.8, aligned_edge=ORIGIN)  # 【审美优化】增加间距
        recap_elements.move_to(ORIGIN + UP * 0.5)  # 【避免重叠】稍微上移，给字幕留空间
        
        # 【审美优化】同步展示：所有元素一起出现
        self.play(
            LaggedStart(
                *[FadeIn(elem, shift=UP*0.3, scale=0.8) for elem in recap_elements],
                lag_ratio=0.3,
                run_time=3,
                rate_func=smooth
            )
        )
        self.wait(2)
        
        # 快速倒放效果
        self.play(
            LaggedStart(
                *[FadeOut(elem, shift=DOWN*0.3) for elem in recap_elements],
                lag_ratio=0.2,
                run_time=2,
                rate_func=smooth
            )
        )
        self.wait(1)
        
        # ====================================================================
        # Part 2: 核心思想的深化（约15秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "从数学的理想世界（Δx → 0）",
            duration=4.0,
            wait_after=1.0
        )
        
        # 展示连续函数的导数
        continuous_axes = Axes(
            x_range=[-1, 5, 1],
            y_range=[-1, 3, 1],
            x_length=6,
            y_length=3,
            axis_config={
                "stroke_opacity": 0.4,  # 【审美优化】降低透明度
                "stroke_width": 1,
                "stroke_color": GREY_C,
                "include_tip": False
            },
            tips=False
        )
        
        # 连续函数
        def continuous_func(x):
            return 0.5 * x ** 2 - x + 1
        
        continuous_graph = continuous_axes.plot(
            continuous_func,
            x_range=[-0.5, 4.5],
            color=COLOR_CONTINUOUS,  # 【审美优化】使用语义颜色
            stroke_width=3
        )
        
        # 切线（导数）
        x_point = 2
        y_point = continuous_func(x_point)
        slope = x_point - 1  # f'(x) = x - 1
        
        tangent_line = Line(
            start=continuous_axes.c2p(x_point - 1, y_point - slope),
            end=continuous_axes.c2p(x_point + 1, y_point + slope),
            color=COLOR_DIFF,  # 【审美优化】使用语义颜色
            stroke_width=2.5
        )
        
        tangent_point = Dot(
            point=continuous_axes.c2p(x_point, y_point),
            color=COLOR_DIFF,
            radius=0.08
        )
        
        # 标签
        continuous_label_2 = Text(
            "连续导数",
            font_size=18,
            color=COLOR_CONTINUOUS
        ).next_to(continuous_axes, UP, buff=0.3)
        
        continuous_group = VGroup(continuous_axes, continuous_graph, tangent_line, tangent_point, continuous_label_2)
        continuous_group.move_to(ORIGIN + UP * 0.3)  # 【避免重叠】稍微上移
        
        # 【审美优化】同步展示
        self.play(
            Create(continuous_axes),
            Create(continuous_graph),
            run_time=1.5,
            rate_func=smooth
        )
        self.play(
            Create(tangent_line),
            Create(tangent_point),
            Write(continuous_label_2),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(1.5)
        
        # 淡出连续函数
        self.play(
            FadeOut(continuous_group, shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        subtitle_mgr.show(
            "到工程的实际应用（pixel = 1）",
            duration=4.0,
            wait_after=1.0
        )
        
        # 展示离散图像的边缘检测
        discrete_demo = VGroup()
        
        # 离散像素网格
        pixel_size = 8
        pixel_grid = VGroup()
        for i in range(pixel_size):
            for j in range(pixel_size):
                # 模拟一个简单的边缘
                if j < pixel_size / 2:
                    intensity = 0.3
                else:
                    intensity = 0.8
                
                color = interpolate_color(BLACK, WHITE, intensity)
                pixel = Square(
                    side_length=0.15,
                    fill_opacity=1,
                    stroke_width=0.5,
                    stroke_color=GREY_D
                )
                pixel.set_fill(color)
                pixel.move_to(RIGHT * (j - pixel_size/2) * 0.15 + UP * (pixel_size/2 - i) * 0.15)
                pixel_grid.add(pixel)
        
        # 边缘检测结果（简化的边缘）
        edge_grid = VGroup()
        for i in range(pixel_size):
            for j in range(pixel_size):
                # 在边缘处显示
                if abs(j - pixel_size / 2) < 0.5:
                    edge_color = COLOR_DIFF  # 【审美优化】使用语义颜色
                    opacity = 0.9
                else:
                    edge_color = BLACK
                    opacity = 0.1
                
                pixel = Square(
                    side_length=0.15,
                    fill_opacity=opacity,
                    stroke_width=0
                )
                pixel.set_fill(edge_color)
                pixel.move_to(RIGHT * (j - pixel_size/2) * 0.15 + UP * (pixel_size/2 - i) * 0.15)
                edge_grid.add(pixel)
        
        # 标签
        discrete_label_2 = Text(
            "离散边缘检测",
            font_size=18,
            color=COLOR_DISCRETE
        )
        
        edge_label_2 = Text(
            "Sobel算子结果",
            font_size=18,
            color=COLOR_DIFF
        )
        
        # 【避免重叠】使用相对排版
        discrete_group = VGroup(pixel_grid, discrete_label_2)
        discrete_group.arrange(DOWN, buff=0.3, aligned_edge=ORIGIN)
        
        edge_group_2 = VGroup(edge_grid, edge_label_2)
        edge_group_2.arrange(DOWN, buff=0.3, aligned_edge=ORIGIN)
        
        discrete_demo = VGroup(discrete_group, edge_group_2)
        discrete_demo.arrange(RIGHT, buff=1.0, aligned_edge=ORIGIN)  # 【审美优化】增加间距
        discrete_demo.move_to(ORIGIN + UP * 0.3)  # 【避免重叠】稍微上移
        
        # 【审美优化】同步展示
        self.play(
            LaggedStart(
                FadeIn(discrete_group, shift=UP*0.3, scale=0.8),
                FadeIn(edge_group_2, shift=UP*0.3, scale=0.8),
                lag_ratio=0.4,
                run_time=2.5,
                rate_func=smooth
            )
        )
        self.wait(2)
        
        subtitle_mgr.show(
            "我们看到了数学与现实的美妙连接",
            duration=4.5,
            wait_after=1.5
        )
        
        self.wait(1)
        
        # 淡出
        self.play(
            FadeOut(discrete_demo, shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 3: 启发与展望（约10秒）
        # ====================================================================
        
        subtitle_mgr.show(
            "这只是一个开始",
            duration=3.0,
            wait_after=1.0
        )
        
        # 展示更多应用方向（简化图标）
        applications = VGroup()
        
        # 应用1：深度学习
        dl_icon = VGroup()
        for i in range(3):
            circle = Circle(
                radius=0.15,
                color=COLOR_CONTINUOUS,  # 【审美优化】使用语义颜色
                stroke_width=2
            ).move_to(RIGHT * (i - 1) * 0.4)
            dl_icon.add(circle)
        dl_label = Text("深度学习", font_size=16, color=WHITE)
        dl_group = VGroup(dl_icon, dl_label)
        dl_group.arrange(DOWN, buff=0.2, aligned_edge=ORIGIN)
        
        # 应用2：计算机视觉
        cv_icon = VGroup()
        for i in range(3):
            square = Square(
                side_length=0.25,
                color=COLOR_SMOOTH,  # 【审美优化】使用语义颜色
                stroke_width=2
            ).move_to(RIGHT * (i - 1) * 0.4)
            cv_icon.add(square)
        cv_label = Text("计算机视觉", font_size=16, color=WHITE)
        cv_group = VGroup(cv_icon, cv_label)
        cv_group.arrange(DOWN, buff=0.2, aligned_edge=ORIGIN)
        
        # 应用3：图像处理
        ip_icon = VGroup()
        for i in range(3):
            line = Line(
                start=UP * 0.2 + RIGHT * (i - 1) * 0.4,
                end=DOWN * 0.2 + RIGHT * (i - 1) * 0.4,
                color=COLOR_DIFF,  # 【审美优化】使用语义颜色
                stroke_width=2.5
            )
            ip_icon.add(line)
        ip_label = Text("图像处理", font_size=16, color=WHITE)
        ip_group = VGroup(ip_icon, ip_label)
        ip_group.arrange(DOWN, buff=0.2, aligned_edge=ORIGIN)
        
        # 【避免重叠】使用相对排版
        applications.add(dl_group, cv_group, ip_group)
        applications.arrange(RIGHT, buff=1.2, aligned_edge=ORIGIN)  # 【审美优化】增加间距
        applications.move_to(ORIGIN + UP * 0.3)  # 【避免重叠】稍微上移
        
        # 【审美优化】同步展示
        self.play(
            LaggedStart(
                *[FadeIn(app, shift=UP*0.3, scale=0.8) for app in applications],
                lag_ratio=0.3,
                run_time=2.5,
                rate_func=smooth
            )
        )
        self.wait(1.5)
        
        subtitle_mgr.show(
            "数学工具在工程应用中还有无限可能",
            duration=4.5,
            wait_after=2.0
        )
        
        self.wait(1)
        
        # 淡出应用图标
        self.play(
            FadeOut(applications, shift=DOWN*0.3),
            run_time=1.5,
            rate_func=smooth
        )
        
        # ====================================================================
        # Part 4: 结尾升华（约20秒）
        # ====================================================================
        # 核心思想文本
        try:
            philosophy_text = Text(
                "知行合一\n从数学理想 到 工程现实",
                font_size=36,
                color=WHITE,
                font="SimHei"
            )
        except:
            # Fallback if SimHei causes an issue (though usually it just warns)
            philosophy_text = Text(
                "知行合一\n从数学理想 到 工程现实",
                font_size=36,
                color=WHITE
            )
        philosophy_text.move_to(ORIGIN)  # 【避免重叠】居中，字幕在底部
        
        # 【审美优化】文字逐字显示
        self.play(
            Write(philosophy_text),
            run_time=3,
            rate_func=smooth
        )
        self.wait(2.5)
        
        self.play(
            FadeOut(philosophy_text, shift=UP*0.3),
            run_time=2,
            rate_func=smooth
        )
        
        # 版权页（避免重叠：使用相对排版）
        credits_text = VGroup(
            Text(
                "Project Sobel",
                font_size=32,
                color=COLOR_CONTINUOUS  # 【审美优化】使用语义颜色
            ),
            Text(
                "Visuals: Manim Community Edition",
                font_size=20,
                color=GREY_C  # 【审美优化】降低亮度
            ),
            Text(
                "Code: Python 3.10 + Manim",
                font_size=20,
                color=GREY_C  # 【审美优化】降低亮度
            ),
            Text("", font_size=12),  # 空行作为间距
            Text(
                "原创声明: 本视频所有动画均为编程生成",
                font_size=24,
                color=WHITE
            )
        )
        credits_text.arrange(DOWN, buff=0.4, aligned_edge=ORIGIN)  # 【审美优化】增加间距
        credits_text.move_to(ORIGIN)  # 【避免重叠】居中，字幕在底部
        
        # 【审美优化】逐行显示
        self.play(
            LaggedStart(
                *[Write(text) for text in credits_text if text.get_text()],  # 跳过空行
                lag_ratio=0.4,
                run_time=3,
                rate_func=smooth
            )
        )
        self.wait(3)
        
        # 清理字幕（在最后淡出前清理）
        subtitle_mgr.clear()
        
        # 最终淡出
        self.play(
            FadeOut(credits_text, shift=DOWN*0.3),
            run_time=2,
            rate_func=smooth
        )
        
        # 场景结束
        self.wait(1)


# ============================================================================
# 测试场景（用于快速预览）
# ============================================================================

if __name__ == "__main__":
    # 可以直接测试 Scene 0、Scene 1、Scene 2、Scene 3、Scene 4、Scene 4.5 和 Scene 5
    pass

