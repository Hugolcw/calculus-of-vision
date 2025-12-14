from manim import *
import numpy as np

# 导入 V14 统一工具模块（继承 V13 所有功能 + V14 新增功能）
from utils_v14 import (
    # V13 基础功能（全部继承）
    SubtitleManager,
    safer_text,
    make_highlight_rect,
    default_axis_config,
    get_quality_config,
    PALETTE,  # V13: 语义化色彩系统
    SAFE_RECT,  # V13: 安全区常量
    SUBTITLE_Y,  # V13: 字幕Y坐标
    Z_LAYERS,  # V13: Z轴分层
    LEFT_COL, RIGHT_COL, GUTTER,  # V13: 布局网格
    SmartBox,  # V13: 智能组件
    FocusArrow,  # V13: 智能组件
    NeonLine,  # V13: 智能组件
    BaseScene,  # V13: 基类
    BaseThreeDScene,  # V13: 3D场景基类
    # 向后兼容：保留旧的颜色常量（映射到PALETTE）
    COLOR_CONTINUOUS,
    COLOR_DISCRETE,
    COLOR_DIFF,
    COLOR_SMOOTH,
    BG_COLOR,
    # V14 新增功能
    NarrativeHelper,  # V14: 叙事工具类
    PacingController,  # V14: 节奏控制器
    MinimalismHelper,  # V14: 极简主义辅助工具
    # V14 便捷函数
    slow_wait,  # 慢速等待
    slow_play,  # 慢速播放
    ask_question,  # 设问
    show_conflict,  # 展示困境
    show_solution,  # 展示解决
    show_validation,  # 展示验证
)
# V14 增强：导入安全检查函数
from utils_v13 import ensure_safe_bounds


# =============================================================================
# Scene 0：直觉与混沌（V14 叙事重构版）
# =============================================================================
class Scene0Intro(BaseThreeDScene):
    """
    第一部分：直觉与混沌
    V14 改进内容：
    - 叙事重构：使用"设问-困境-解决"模板
    - 节奏控制：慢动作展示，3秒法则
    - 极简主义：删除粒子特效，降低背景饱和度
    - 继承 V13 所有技术优势
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        # ====================================================================
        # V14 叙事重构 Part 1: 设问（Intuition）
        # ====================================================================
        # V14 新文案：用"人话"引发思考
        question = ask_question(
            self,
            "If you were to draw the outline of this image, how would you do it?",
            wait_after=2.0
        )
        
        # 展示清晰图（低饱和度背景）
        clean = self._make_gradient_card()
        clean.scale(0.9)
        clean.move_to(ORIGIN)
        # V14 极简主义：降低背景饱和度
        clean = MinimalismHelper.create_background_element(clean, opacity=0.3)
        
        title_clean = safer_text("Clean Image", font_size=26, color=GREY_C).next_to(clean, DOWN, buff=0.25)
        clean_group = VGroup(clean, title_clean)
        self.add_to_math_group(clean_group)

        # V14 节奏控制：慢动作展示
        slow_play(self, FadeIn(clean_group, shift=UP * 0.3), base_run_time=1.2)
        slow_wait(self, 1.0)
        
        # V14 新文案：解释人眼的能力
        hud.show("Your eyes can automatically ignore these noise points and see the underlying lines.", wait_after=1.0)
        slow_wait(self, 1.5)

        # ====================================================================
        # V14 叙事重构 Part 2: 困境（Conflict）
        # ====================================================================
        # V14 新文案：展示机器的困境
        hud.show("But for a computer, every noise point is a dramatic numerical jump.", wait_after=1.0)
        slow_wait(self, 1.0)
        
        # 创建噪声图框架
        noisy_card = self._make_noisy_card_frame()
        noisy_card.scale(0.9)
        noisy_card.move_to(ORIGIN)
        title_noisy = safer_text("Noisy Image", font_size=26, color=WHITE).next_to(noisy_card, DOWN, buff=0.25)
        noisy_group = VGroup(noisy_card, title_noisy)
        
        # 与清晰图同位置叠放噪声框架
        noisy_group.move_to(clean_group)
        # V14 节奏控制：慢动作展示噪声
        slow_play(self, FadeIn(noisy_group, shift=UP * 0.1), base_run_time=0.8)
        slow_wait(self, 0.5)
        
        # 动态生成噪声点（真正的“污染”过程：清晰图逐渐变暗，噪声逐渐覆盖）
        rng = np.random.default_rng(42)
        noise_dots = VGroup()
        num_noise_points = 160
        
        # 创建噪声点列表（预先生成所有点，但逐个显示）
        # 修复：噪声点范围缩至90%，避免溢出卡片框
        noise_positions = []
        for _ in range(num_noise_points):
            x = rng.uniform(-2.34, 2.34)  # 缩至90%: -2.6*0.9 ~ 2.6*0.9
            y = rng.uniform(-1.26, 1.26)  # 缩至90%: -1.4*0.9 ~ 1.4*0.9
            val = rng.uniform(0, 1)
            noise_positions.append((x, y, val))
        
        # 分批显示噪声点（每批显示多个点，加快速度）
        # 使用 LaggedStart 让噪声点更自然地出现
        batch_size = 10
        all_batch_dots = []
        
        for i in range(0, num_noise_points, batch_size):
            batch_dots = VGroup()
            for j in range(i, min(i + batch_size, num_noise_points)):
                x, y, val = noise_positions[j]
                dot = Dot(
                    point=np.array([x, y, 0]),
                    radius=0.055,
                    color=interpolate_color(BLACK, WHITE, val),
                    stroke_width=0,
                )
                batch_dots.add(dot)
            
            all_batch_dots.append(batch_dots)
            noise_dots.add(*batch_dots)
        
        # 使用 LaggedStart 批量显示，更流畅，同时逐步降低清晰图的不透明度，制造“污染”感
        steps = len(all_batch_dots)
        animations = []
        for idx, batch in enumerate(all_batch_dots):
            # 清晰图逐步淡出，噪声逐步浮现
            fade_clean = clean_group.animate.set_opacity(max(0.15, 1 - 0.85 * (idx + 1) / steps))
            animations.append(
                LaggedStart(
                    FadeIn(batch, scale=0.3),
                    fade_clean,
                    lag_ratio=0.0,
                    run_time=0.45
                )
            )

        # V14 节奏控制：慢动作展示噪声生成过程
        self.play(
            LaggedStart(
                *animations,
                lag_ratio=0.12,
                run_time=2.8 * PacingController.SLOW_MOTION_FACTOR,  # 慢动作
                rate_func=smooth
            )
        )
        # V14 节奏控制：3秒法则
        slow_wait(self, 1.5)
        
        # V14 新文案：强化困境
        hud.show("Noise obscures the structure of the image.", wait_after=1.2)
        slow_wait(self, 1.5)

        # ====================================================================
        # V14 叙事重构 Part 3: 解决（Solution）
        # ====================================================================
        # V14 新文案：提出核心问题
        hud.show("How can a machine distinguish between 'real edges' and 'random noise'?", wait_after=1.5)
        slow_wait(self, 2.0)
        
        # 创建边缘检测预览（基于渐变图的 Sobel 近似）：从噪声中“浮现”真实感更强的边缘
        edge_preview = self._create_edge_preview_from_gradient()
        edge_preview.set_opacity(0)  # 初始不可见
        
        # 从噪声中逐渐"提取"边缘：线条渐显、线宽渐增
        # V13: 使用语义化色彩系统（PALETTE["EDGE"]）
        for line in edge_preview:
            line.set_stroke(width=0, opacity=0)
            # 使用语义化边缘颜色（琥珀金）
            line.set_color(PALETTE["EDGE"])
        # V14 节奏控制：慢动作展示边缘提取
        self.play(
            LaggedStart(
                *[
                    Succession(
                        line.animate.set_opacity(0.6).set_stroke(width=2.5),
                        line.animate.set_opacity(0.85).set_stroke(width=line.stroke_width or 3.2)
                    )
                    for line in edge_preview
                ],
                lag_ratio=0.12,
                run_time=3.0 * PacingController.SLOW_MOTION_FACTOR,  # 慢动作
                rate_func=smooth
            )
        )
        # V14 节奏控制：3秒法则
        slow_wait(self, 2.0)
        
        # V14 极简主义：静态高亮框（不闪烁、不呼吸）
        edge_highlight = MinimalismHelper.create_static_highlight(
            edge_preview,
            color=PALETTE["EDGE"]
        )
        slow_play(self, Create(edge_highlight), base_run_time=0.6)
        slow_wait(self, 1.0)
        
        # V14 新文案：验证解决方案
        hud.show("This is the power of edge detection.", wait_after=1.0)
        slow_wait(self, 2.0)
        
        # 保留边缘结果用于后续对比，不立即淡出
        edge_result = edge_preview.copy()
        edge_result_highlight = edge_highlight.copy()

        # ====================================================================
        # Part 4: 问题提出（约4秒）
        # ====================================================================
        # V13: 使用布局引擎，确保在安全区内
        clean_final = self._make_gradient_card()
        noisy_final = self._make_noisy_card()
        edge_final = edge_result.copy()
        edge_final_highlight = edge_result_highlight.copy()
        # 左侧主图（清晰图+噪声图），右侧状态灯（边缘结果）
        # 使用 SAFE_RECT 约束，确保不超出安全区
        left_pair = VGroup(clean_final, noisy_final).arrange(DOWN, buff=0.4).scale(0.75)
        right_status = VGroup(edge_final.scale(0.7), edge_final_highlight.scale(0.7))
        right_status.arrange(DOWN, buff=0.15)
        pair = VGroup(left_pair, right_status).arrange(RIGHT, buff=0.8).move_to(ORIGIN)
        # V14 增强：确保在安全区内（使用新的安全检查函数）
        ensure_safe_bounds(pair)
        title_clean_final = safer_text("Clean Image", font_size=22, color=WHITE).next_to(clean_final, DOWN, buff=0.2)
        title_noisy_final = safer_text("Noisy Image", font_size=22, color=WHITE).next_to(noisy_final, DOWN, buff=0.2)
        title_edge_final = safer_text("Extracted Edges", font_size=22, color=PALETTE["EDGE"]).next_to(edge_final, DOWN, buff=0.2)
        pair_group = VGroup(pair, title_clean_final, title_noisy_final, title_edge_final)
        
        # 替换当前画面，保留噪声与边缘结果用于对比
        # 修复：先淡出旧图，等待，再淡入新图，避免转场穿帮
        slow_play(self, FadeOut(VGroup(noisy_group, noise_dots, edge_preview, edge_highlight)), base_run_time=0.6)
        slow_wait(self, 0.2)  # V14 节奏控制：所有等待时间使用 slow_wait
        slow_play(self, FadeIn(pair_group), base_run_time=0.8)
        
        # V14 叙事重构：核心问题（静态展示，删除粒子特效）
        # V14 极简主义：删除粒子特效，使用静态问题文本
        core_question = safer_text(
            "Can mathematics make machines see?", 
            font_size=34, 
            color=PALETTE["HIGHLIGHT"]
        )
        # V14 增强：确保问题文本在安全区域内
        ensure_safe_bounds(core_question)
        question_bg = BackgroundRectangle(
            core_question,
            fill_opacity=0.7,
            color=BLACK,
            buff=0.28,
            corner_radius=0.08
        )
        question_group = VGroup(question_bg, core_question).move_to(ORIGIN + UP * 1.6)
        # V14 增强：确保整个问题组在安全区域内
        ensure_safe_bounds(question_group)
        self.add_fixed_in_frame_mobjects(question_group)
        self.add_to_math_group(question_group)
        
        # V14 节奏控制：慢动作展示问题
        slow_play(self, FadeIn(question_group, scale=0.9), base_run_time=0.8)
        # V14 节奏控制：3秒法则（让观众思考）
        slow_wait(self, 3.0)
        
        # V14 极简主义：删除粒子特效，直接淡出问题
        slow_play(self, FadeOut(question_group, shift=UP * 0.2), base_run_time=0.6)

        # ====================================================================
        # Part 6: 收尾
        # ====================================================================
        # V13: 使用生命周期管理
        self.add_to_math_group(pair_group)
        hud.clear()
        self.clear_scene(fade_out=True, run_time=0.8 * PacingController.SLOW_MOTION_FACTOR)  # V14 节奏控制：慢动作
        slow_wait(self, 0.4)  # V14 节奏控制：所有等待时间使用 slow_wait

    def _make_gradient_card(self):
        """创建清晰渐变图"""
        card = RoundedRectangle(
            width=5.5,
            height=3.2,
            corner_radius=0.2,
            stroke_width=2.2,
            stroke_color=GREY_B
        )
        bars = VGroup()
        for i in range(18):
            bar = Rectangle(
                width=5.5 / 18,
                height=3.2,
                stroke_width=0,
                fill_opacity=1,
                fill_color=interpolate_color(BLACK, WHITE, i / 17),
            )
            bar.move_to(card.get_left() + RIGHT * (i + 0.5) * (5.5 / 18))
            bars.add(bar)
        group = VGroup(card, bars)
        return group

    def _make_noisy_card_frame(self):
        """创建噪声图框架（不含噪声点）"""
        card = RoundedRectangle(
            width=5.5,
            height=3.2,
            corner_radius=0.2,
            stroke_width=2.2,
            stroke_color=GREY_B
        )
        return card

    def _make_noisy_card(self):
        """创建完整的噪声图（包含所有噪声点）"""
        card = RoundedRectangle(
            width=5.5,
            height=3.2,
            corner_radius=0.2,
            stroke_width=2.2,
            stroke_color=GREY_B
        )
        dots = VGroup()
        rng = np.random.default_rng(42)
        for _ in range(160):
            x = rng.uniform(-2.6, 2.6)
            y = rng.uniform(-1.4, 1.4)
            val = rng.uniform(0, 1)
            dot = Dot(
                point=np.array([x, y, 0]),
                radius=0.055,
                color=interpolate_color(BLACK, WHITE, val),
                stroke_width=0,
            )
            dots.add(dot)
        group = VGroup(card, dots)
        return group

    def _create_edge_preview_from_gradient(self, grid_w: int = 18, grid_h: int = 10):
        """
        基于清晰渐变图，使用简化的 Sobel 核计算水平梯度，生成更真实的边缘预览。
        仅做近似演示：采样网格 -> 计算梯度 -> 用短线段/小块呈现边缘强度。
        """
        # 采样清晰图的强度（与渐变卡条数一致，保持审美）
        # 强度随 x 递增（模拟横向渐变），y 维度保持平滑
        intensities = np.zeros((grid_h, grid_w))
        for i in range(grid_h):
            for j in range(grid_w):
                intensities[i, j] = j / (grid_w - 1)

        # Sobel 水平核（检测垂直边缘）
        sobel_x = np.array([[-1, 0, 1],
                            [-2, 0, 2],
                            [-1, 0, 1]])

        # 计算梯度图
        grad = np.zeros_like(intensities)
        for i in range(1, grid_h - 1):
            for j in range(1, grid_w - 1):
                patch = intensities[i - 1:i + 2, j - 1:j + 2]
                gx = np.sum(patch * sobel_x)
                grad[i, j] = abs(gx)

        # 归一化梯度用于视觉映射
        max_val = grad.max() if grad.max() > 0 else 1.0
        grad_norm = grad / max_val

        # 将梯度转为边缘可视化：在对应位置绘制短线段，透明度/亮度按梯度强度
        edge_lines = VGroup()
        width = 5.5
        height = 3.2
        x0, y0 = -width / 2, -height / 2
        dx = width / grid_w
        dy = height / grid_h

        for i in range(1, grid_h - 1):
            for j in range(1, grid_w - 1):
                strength = grad_norm[i, j]
                if strength < 0.08:
                    continue  # 弱边缘忽略，保持画面干净
                x = x0 + (j + 0.5) * dx
                y = y0 + (grid_h - 1 - i + 0.5) * dy  # 上下翻转以匹配视觉
                # 短竖线，代表垂直边缘
                # V13: 使用语义化边缘颜色
                line = Line(
                    start=np.array([x, y - dy * 0.25, 0]),
                    end=np.array([x, y + dy * 0.25, 0]),
                    color=PALETTE["EDGE"],
                    stroke_width=2.5,
                    stroke_opacity=0.3 + 0.7 * strength,  # 强度映射到透明度
                )
                edge_lines.add(line)

        return edge_lines

    # V14 极简主义：已删除 _create_thinking_particles 方法（不再使用粒子特效）


# 运行示例：
# manim -pql sobel_v12_full.py Scene0Intro
if __name__ == "__main__":
    pass


# =============================================================================
# Full video wrapper：串联各分场景（便于一次渲染）
# =============================================================================
class FullSobelVideo(BaseThreeDScene):
    """
    一次性串联全部分场景。
    由于各分场景内部用到的私有 helper 方法定义在各类中，
    这里提供轻量包装器把相关 helper 委托回对应类，避免 AttributeError。
    """

    # --- helper proxies for Scene0Intro ---
    def _make_gradient_card(self):
        return Scene0Intro._make_gradient_card(self)

    def _make_noisy_card_frame(self):
        return Scene0Intro._make_noisy_card_frame(self)

    def _make_noisy_card(self):
        return Scene0Intro._make_noisy_card(self)

    def _create_edge_preview_from_gradient(self, *args, **kwargs):
        return Scene0Intro._create_edge_preview_from_gradient(self, *args, **kwargs)

    # V14 极简主义：已删除 _create_thinking_particles 方法（不再使用粒子特效）

    # --- helper proxies for Scene4_5Applications ---
    def _make_road_pair(self):
        return Scene4_5Applications._make_road_pair(self)

    def _make_text_pair(self):
        return Scene4_5Applications._make_text_pair(self)

    def _make_face_pair(self):
        return Scene4_5Applications._make_face_pair(self)

    def _make_building_pair(self):
        return Scene4_5Applications._make_building_pair(self)

    def _make_threshold_triplet(self):
        return Scene4_5Applications._make_threshold_triplet(self)

    def construct(self):
        # 0. 开场
        Scene0Intro.construct(self)
        # 1. 连续→离散
        Scene1Discrete.construct(self)
        # 1.5 极限困境
        Scene1_5Limits.construct(self)
        # 2. 泰勒抵消
        Scene2Taylor.construct(self)
        # 2.5 差分对比
        Scene2_5Comparison.construct(self)
        # 3. Sobel 诞生
        Scene3SobelConstruct.construct(self)
        # 3.5 卷积可视化
        Scene3_5Convolution.construct(self)
        # 4.2 多尺度对比
        Scene4_2MultiScale.construct(self)
        # 4. 3D 扫描
        Scene4Vision.construct(self)
        # 4.6 真实图像流程
        Scene4_6RealImage.construct(self)
        # 4.5 应用对照
        Scene4_5Applications.construct(self)
        # 5. 收尾
        Scene5Outro.construct(self)


# =============================================================================
# Scene 1：失去极限（V14 叙事重构版）
# =============================================================================
class Scene1Discrete(BaseScene):
    """
    第二部分：失去极限
    V14 改进内容：
    - 叙事重构：展示"困境"（微积分撞上像素的颗粒感）
    - 节奏控制：慢动作展示，3秒法则
    - 极简主义：降低背景元素饱和度
    - 继承 V12/V13 的数学可视化优势
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        # V14 极简主义：低饱和度坐标轴
        axes_config = MinimalismHelper.create_focus_axes(stroke_opacity=0.3)
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 5, 1],
            x_length=11,
            y_length=4.5,
            axis_config=axes_config,
            tips=False,
        ).shift(UP * 0.5)
        self.add_to_math_group(axes)
        
        def f(x): return 2 + np.sin(0.5 * x) + 0.5 * np.sin(x)
        # V14 极简主义：曲线作为背景元素（低饱和度）
        curve = axes.plot(f, x_range=[0, 10], color=PALETTE["MATH_FUNC"], stroke_width=4)
        curve = MinimalismHelper.create_background_element(curve, opacity=0.3)
        self.add_to_math_group(curve)

        # V14 节奏控制：慢动作展示
        slow_play(self, Create(axes), base_run_time=1.0)
        slow_play(self, Create(curve), base_run_time=1.2)
        
        # V14 新文案：回顾理想
        hud.show("In the mathematical ideal, the derivative is the slope of the tangent line.", wait_after=1.0)
        slow_wait(self, 1.5)

        # 多切点展示（静态切线 3 处）
        tangent_points = [2, 5, 8]
        tangents = VGroup()
        for tx in tangent_points:
            dx = 0.01
            dy = (f(tx + dx) - f(tx - dx)) / (2 * dx)
            # V13: 使用语义化颜色
            line = Line(
                axes.c2p(tx - 1.2, f(tx) - dy * 1.2),
                axes.c2p(tx + 1.2, f(tx) + dy * 1.2),
                color=PALETTE["MATH_ERROR"],
                stroke_width=3,
            )
            dot = Dot(axes.c2p(tx, f(tx)), color=PALETTE["MATH_ERROR"], radius=0.08)
            tangents.add(line, dot)
        # V14 节奏控制：慢动作展示
        self.play(LaggedStart(*[Create(t) for t in tangents], lag_ratio=0.2, run_time=1.8 * PacingController.SLOW_MOTION_FACTOR))
        slow_wait(self, 1.0)
        slow_play(self, FadeOut(tangents, shift=DOWN * 0.2), base_run_time=0.8)

        # 动态切线演示
        t = ValueTracker(2.0)
        def tangent():
            x = t.get_value(); dx = 0.01
            dy = (f(x + dx) - f(x - dx)) / (2 * dx)
            # V13: 使用语义化颜色
            return Line(
                axes.c2p(x - 1.5, f(x) - dy * 1.5),
                axes.c2p(x + 1.5, f(x) + dy * 1.5),
                color=PALETTE["MATH_ERROR"],
                stroke_width=3,
            )
        tan_line = always_redraw(tangent)
        tan_dot = always_redraw(lambda: Dot(axes.c2p(t.get_value(), f(t.get_value())), color=PALETTE["MATH_ERROR"], radius=0.08))
        slope_text = always_redraw(lambda: MathTex(
            rf"f'({t.get_value():.1f}) \approx {((f(t.get_value()+0.01)-f(t.get_value()-0.01))/0.02):.2f}",
            font_size=28, color=PALETTE["MATH_ERROR"]
        ).to_edge(UR, buff=0.8))

        self.add(tan_line, tan_dot, slope_text)
        # V14 节奏控制：慢动作展示动态切线
        self.play(t.animate.set_value(8), run_time=2.8 * PacingController.SLOW_MOTION_FACTOR, rate_func=smooth)
        slow_wait(self, 1.0)

        # V14 叙事重构：展示困境
        # V14 新文案：强化困境描述
        hud.show("Calculus tells us that the derivative is the slope. But in the pixel world, we hit a physical barrier: pixels are discrete.", wait_after=1.5)
        slow_wait(self, 1.0)
        
        # 渐进采样：5 → 11 → 21 点
        hud.show("We can't approach infinity—the smallest step size is 1.", wait_after=1.0)
        samples_group = VGroup()
        piecewise_lines = []
        for n in [5, 11, 21]:
            xs = np.linspace(0, 10, n)
            stems = VGroup()
            for x in xs:
                y = f(x)
                # V13: 使用语义化颜色
                stem = Line(axes.c2p(x, 0), axes.c2p(x, y), color=YELLOW_C, stroke_width=3)
                dot = Dot(axes.c2p(x, y), color=YELLOW_C, radius=0.07)
                stems.add(stem, dot)
            samples_group.add(stems)
            # V13: 使用语义化颜色
            poly = VMobject(color=YELLOW_C, stroke_width=2.5, stroke_opacity=0.9)
            poly.set_points_as_corners([axes.c2p(x, f(x)) for x in xs])
            piecewise_lines.append(poly)

        # 清空切线，展示采样
        slow_play(self, FadeOut(VGroup(tan_line, tan_dot, slope_text)), base_run_time=0.6)
        self.play(
            curve.animate.set_opacity(0.15),
            FadeIn(samples_group[0], lag_ratio=0.05, run_time=1.2 * PacingController.SLOW_MOTION_FACTOR),  # V14 节奏控制：慢动作
            Create(piecewise_lines[0]),
            run_time=1.2 * PacingController.SLOW_MOTION_FACTOR,  # V14 节奏控制：慢动作
        )
        slow_wait(self, 0.5)  # V14 节奏控制：所有等待时间使用 slow_wait
        # 采样密度提升
        self.play(
            Transform(samples_group[0], samples_group[1]),
            Transform(piecewise_lines[0], piecewise_lines[1]),
            run_time=0.9 * PacingController.SLOW_MOTION_FACTOR  # V14 节奏控制：慢动作
        )
        slow_wait(self, 0.3)  # V14 节奏控制：所有等待时间使用 slow_wait
        self.play(
            Transform(samples_group[0], samples_group[2]),
            Transform(piecewise_lines[0], piecewise_lines[2]),
            run_time=0.9
        )
        slow_wait(self, 0.6)  # V14 节奏控制：所有等待时间使用 slow_wait

        # 像素桶可视化：每个像素是长度为 1 的量化区间
        hud.show("Each pixel is a bucket, and the function gets quantized into piecewise approximations.", wait_after=0.8)
        pixel_bins = VGroup()
        width = axes.c2p(1, 0)[0] - axes.c2p(0, 0)[0]
        height = axes.c2p(0, 5)[1] - axes.c2p(0, 0)[1]
        for k in range(10):
            rect = Rectangle(
                width=abs(width),
                height=abs(height),
                stroke_width=1.2,
                # V13: 使用语义化颜色
                stroke_color=PALETTE["MATH_FUNC"],
                fill_color=PALETTE["MATH_FUNC"],
                fill_opacity=0.12
            ).move_to(axes.c2p(k + 0.5, 2.5))
            pixel_bins.add(rect)
        slow_play(self, FadeIn(pixel_bins, lag_ratio=0.1), base_run_time=1.0)
        slow_wait(self, 0.4)  # V14 节奏控制：所有等待时间使用 slow_wait

        # Δx 逐步放大：0.1 → 0.5 → 1.0 （用水平小段表示）
        hud.show("The minimum step size is constrained; Δx can't get any smaller.", wait_after=0.8)
        focus_x = 5.0
        base_y = -0.5
        dx_values = [0.1, 0.5, 1.0]
        dx_lines = VGroup()
        dx_labels = VGroup()
        for dx in dx_values:
            line = Line(axes.c2p(focus_x - dx, base_y), axes.c2p(focus_x + dx, base_y),
                        color=PALETTE["MATH_ERROR"], stroke_width=3)
            label = MathTex(rf"\Delta x = {dx}", font_size=26, color=PALETTE["MATH_ERROR"]).next_to(line, DOWN, buff=0.25)
            dx_lines.add(line); dx_labels.add(label)
        # V14 节奏控制：慢动作展示
        self.play(LaggedStart(*[Create(line) for line in dx_lines], lag_ratio=0.2, run_time=1.2 * PacingController.SLOW_MOTION_FACTOR))
        self.play(LaggedStart(*[FadeIn(lbl) for lbl in dx_labels], lag_ratio=0.2, run_time=1.0 * PacingController.SLOW_MOTION_FACTOR))
        # V14 节奏控制：复杂图形变化后必须等待2秒
        slow_wait(self, 2.0)

        # 聚焦三个相邻采样点（Δx=1），高亮困境
        xs_full = np.linspace(0, 10, 21)
        mid = len(xs_full) // 2
        idxs = [mid - 1, mid, mid + 1]
        dots_focus = VGroup(*[samples_group[0][2 * i + 1] for i in idxs])
        # V13: 使用智能组件 SmartBox
        box = SmartBox.create(dots_focus, content_type="dots", color=PALETTE["HIGHLIGHT"], stroke_width=3)
        dx_line_1 = Line(
            axes.c2p(xs_full[idxs[0]], base_y - 0.3),
            axes.c2p(xs_full[idxs[2]], base_y - 0.3),
            color=PALETTE["MATH_ERROR"], stroke_width=3,
        )
        dx_label_1 = MathTex(r"\Delta x = 1", font_size=30, color=PALETTE["MATH_ERROR"])
        dx_label_1_bg = BackgroundRectangle(dx_label_1, fill_opacity=0.7, color=BLACK, buff=0.2, corner_radius=0.08)
        dx_label_1_group = VGroup(dx_label_1_bg, dx_label_1).next_to(dx_line_1, DOWN, buff=0.25, aligned_edge=ORIGIN)

        hud.show("The minimum step size is 1 pixel—we've lost the limit.", wait_after=1.2)
        slow_play(self, Create(box), base_run_time=1.2)
        slow_play(self, Create(dx_line_1), base_run_time=1.2)
        slow_play(self, FadeIn(dx_label_1_group), base_run_time=1.2)
        # V14 节奏控制：复杂图形变化后必须等待2秒
        slow_wait(self, 2.0)

        # 离散斜率（割线）对比：只能用 Δx=1 的割线近似斜率
        x_left, x_mid, x_right = xs_full[idxs[0]], xs_full[idxs[1]], xs_full[idxs[2]]
        p_left = axes.c2p(x_left, f(x_left))
        p_mid = axes.c2p(x_mid, f(x_mid))
        p_right = axes.c2p(x_right, f(x_right))
        secant = Line(p_left, p_right, color=PALETTE["MATH_ERROR"], stroke_width=3.2)
        secant_label = MathTex(
            rf"\frac{{\Delta y}}{{\Delta x}} \approx { (f(x_right)-f(x_left))/(x_right-x_left):.2f}",
            font_size=28, color=PALETTE["MATH_ERROR"]
        )
        secant_label_bg = BackgroundRectangle(secant_label, fill_opacity=0.7, color=BLACK, buff=0.2, corner_radius=0.08)
        secant_label_group = VGroup(secant_label_bg, secant_label).next_to(secant, UP, buff=0.25, aligned_edge=ORIGIN)
        slow_play(self, Create(secant), base_run_time=1.0)
        slow_play(self, FadeIn(secant_label_group, shift=UP * 0.1), base_run_time=1.0)
        # V14 节奏控制：复杂图形变化后必须等待2秒
        slow_wait(self, 2.0)
        hud.show("We can only make secant estimates; we can't approach the true tangent.", wait_after=1.0)
        slow_wait(self, 1.5)

        # V13: 使用语义化颜色
        question = safer_text("How do we recover the derivative in discrete pixels?", font_size=30, color=PALETTE["HIGHLIGHT"])
        q_bg = BackgroundRectangle(question, fill_opacity=0.7, color=BLACK, buff=0.25, corner_radius=0.08)
        q_group = VGroup(q_bg, question)
        q_group.arrange(DOWN, buff=0.0, aligned_edge=ORIGIN).to_edge(UP, buff=0.6)
        self.add_fixed_in_frame_mobjects(q_group)

        cluster = VGroup(axes, curve, samples_group[0], box, dx_line_1, dx_label_1, dx_lines, dx_labels)
        focus_point = axes.c2p(xs_full[mid], f(xs_full[mid]))
        self.play(
            cluster.animate.scale(2.0, about_point=focus_point).shift(ORIGIN - focus_point),
            FadeIn(q_group, shift=UP * 0.2),
            run_time=1.8,
            rate_func=smooth,
        )
        slow_wait(self, 1.6)  # V14 节奏控制：所有等待时间使用 slow_wait

        # V13: 使用生命周期管理
        self.add_to_math_group(cluster, q_group)
        hud.clear()
        self.clear_scene(fade_out=True, run_time=1.0)
        slow_wait(self, 0.3)  # V14 节奏控制：所有等待时间使用 slow_wait



# =============================================================================
# Scene 1.5：极限的困境（V13 升级版 - 单一信源驱动）
# =============================================================================
class Scene1_5Limits(BaseScene):
    """
    补足：失去极限的数值实验（V14 叙事重构版）
    V14 改进内容：
    - 节奏控制：慢动作展示
    - 极简主义：降低背景饱和度
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        # V14 叙事重构：设问
        hud.show("When calculus' 'infinite subdivision' collides with pixels' 'graininess', does the derivative still exist?", wait_after=1.5)
        slow_wait(self, 1.0)

        # V14 极简主义：低饱和度坐标轴
        axes_config = MinimalismHelper.create_focus_axes(stroke_opacity=0.3)
        axes = Axes(
            x_range=[0, 4, 0.5],
            y_range=[0, 6, 1],
            x_length=7,
            y_length=4.2,
            axis_config=axes_config,
            tips=False,
        ).to_edge(LEFT, buff=0.8)

        def f(x): return 2 + np.sin(1.2 * x) + 0.6 * np.sin(0.5 * x + 0.3)

        # V14 极简主义：背景曲线低饱和度
        curve = axes.plot(f, x_range=[0, 4], color=PALETTE["MATH_FUNC"], stroke_width=4)
        curve = MinimalismHelper.create_background_element(curve, opacity=0.3)
        self.add_to_math_group(axes, curve)
        
        # V14 节奏控制：慢动作展示
        slow_play(self, Create(axes), base_run_time=1.2)
        slow_play(self, Create(curve), base_run_time=1.2)

        # 多个 Δx 近似斜率并排显示
        # 修复：只保留一行公式，数值随ValueTracker滚动更新，避免公式堆砌
        dx_values = [1.0, 0.5, 0.25, 0.125]
        slopes = []
        x0 = 2.0
        for dx in dx_values:
            s = (f(x0 + dx) - f(x0 - dx)) / (2 * dx)
            slopes.append(s)
        
        # V13: 单一信源驱动（解决 #10）
        dx_tracker = ValueTracker(0)
        approx_label = always_redraw(lambda: MathTex(
            rf"\Delta x = {dx_values[int(dx_tracker.get_value())]:.3g},\; f'(x_0)\approx {slopes[int(dx_tracker.get_value())]:.2f}",
            font_size=28,
            color=WHITE
        ).to_edge(RIGHT, buff=0.8).shift(UP * 1.5))
        self.add_to_math_group(approx_label)
        # V13: 使用语义化颜色
        x0_dot = Dot(axes.c2p(x0, f(x0)), color=PALETTE["MATH_ERROR"], radius=0.08)
        self.add_to_math_group(x0_dot)
        slow_play(self, FadeIn(x0_dot, scale=0.8), base_run_time=0.6)
        # V14 节奏控制：慢动作展示
        for i in range(len(dx_values)):
            self.play(dx_tracker.animate.set_value(i), run_time=0.8 * PacingController.SLOW_MOTION_FACTOR)
            if i < len(dx_values) - 1:
                slow_wait(self, 0.5)
        slow_wait(self, 1.0)

        # V14 叙事重构：困境
        hud.show("The slope is converging, but the pixel world has hard constraints.", wait_after=1.5)
        slow_wait(self, 1.0)

        # 像素网格展示 + 最小单位高亮
        grid = VGroup()
        grid_rows, grid_cols = 6, 10
        for i in range(grid_rows):
            for j in range(grid_cols):
                sq = Square(side_length=0.35, stroke_width=0.5, stroke_color=GREY_B, fill_opacity=0.05)
                sq.move_to(RIGHT * (j - grid_cols / 2) * 0.35 + UP * (grid_rows / 2 - i) * 0.35 + RIGHT * 3.2)
                grid.add(sq)
        min_cell = grid[(grid_rows // 2) * grid_cols + grid_cols // 2].copy()
        # V13: 使用语义化颜色
        min_cell.set_fill(YELLOW_C, opacity=0.35).set_stroke(YELLOW_C, width=2.2)
        min_label = safer_text("Minimum Pixel Unit", font_size=26, color=YELLOW_C).next_to(min_cell, DOWN, buff=0.25)
        self.add_to_math_group(grid, min_cell, min_label)
        # V14 节奏控制：慢动作展示
        slow_play(self, FadeIn(grid, lag_ratio=0.02), base_run_time=1.4)
        slow_play(self, Create(min_cell), base_run_time=0.9)
        slow_play(self, FadeIn(min_label, shift=UP * 0.1), base_run_time=0.9)
        slow_wait(self, 1.0)

        # V14 叙事重构：困境强化
        hud.show("In digital images, Δx is at minimum 1 pixel.", wait_after=1.5)
        slow_wait(self, 1.5)

        # 连续 vs 离散对比卡片
        continuous_card = RoundedRectangle(width=4.2, height=2.2, corner_radius=0.15, stroke_width=2.2, stroke_color=GREY_B)
        discrete_card = continuous_card.copy()
        # V13: 使用语义化颜色
        cont_label = VGroup(
            safer_text("Continuous World: ", font_size=26, color=PALETTE["MATH_FUNC"]),
            MathTex(r"\Delta x \to 0", font_size=26, color=PALETTE["MATH_FUNC"]),
        ).arrange(RIGHT, buff=0.18).move_to(continuous_card.get_center())
        disc_label = VGroup(
            safer_text("Discrete World: ", font_size=26, color=YELLOW_C),
            MathTex(r"\Delta x = 1", font_size=26, color=YELLOW_C),
        ).arrange(RIGHT, buff=0.18).move_to(discrete_card.get_center())
        cont_group = VGroup(continuous_card, cont_label)
        disc_group = VGroup(discrete_card, disc_label)
        pair = VGroup(cont_group, disc_group).arrange(RIGHT, buff=0.6).to_edge(DOWN, buff=0.7)
        # V13: 添加到数学组（在定义之后）
        self.add_to_math_group(pair)
        slow_play(self, FadeIn(pair, shift=UP * 0.2), base_run_time=1.0)
        slow_wait(self, 2.0)

        # V14 极简主义：删除 apply_wave_effect，使用静态展示
        pixel_limit = safer_text("Pixel Limit", font_size=24, color=PALETTE["HIGHLIGHT"])
        pixel_limit_bg = BackgroundRectangle(pixel_limit, fill_opacity=0.5, color=BLACK, buff=0.15, corner_radius=0.06)
        pixel_limit_group = VGroup(pixel_limit_bg, pixel_limit).next_to(approx_label, DOWN, buff=0.4)
        focus_arrow = FocusArrow.create(
            pixel_limit_group.get_left() + LEFT * 0.3,
            approx_label.get_right() + RIGHT * 0.1,
            color=PALETTE["HIGHLIGHT"],
            stroke_width=2.5,
            buff=0.1
        )
        cross = Cross(approx_label, stroke_color=PALETTE["MATH_ERROR"], stroke_width=3)
        self.add_to_math_group(pixel_limit_group, focus_arrow, cross)
        slow_play(self, Create(cross), base_run_time=0.8)
        slow_play(self, FadeIn(pixel_limit_group, shift=UP * 0.2), base_run_time=0.8)
        slow_play(self, Create(focus_arrow), base_run_time=0.8)
        # V14 极简主义：删除 apply_wave_effect
        slow_wait(self, 2.0)

        # V14 叙事重构：结论
        hud.show("Conclusion: we need a new approach to reconstruct the derivative in pixels.", wait_after=1.5)
        slow_wait(self, 2.0)

        # V13: 使用生命周期管理，确保完全清除
        hud.clear()
        self.clear_scene(fade_out=True, run_time=1.0)
        slow_wait(self, 0.4)  # V14 节奏控制：所有等待时间使用 slow_wait

# =============================================================================
# Scene 2：泰勒抵消 → 中心差分（V13 升级版）
# =============================================================================
class Scene2Taylor(BaseScene):
    """
    第三部分：桥梁与巧合（V14 叙事重构版）
    V14 改进内容：
    - 叙事重构：解释"为什么"要用泰勒（数学上的巧合）
    - 节奏控制：慢动作展示误差抵消，3秒法则
    - 极简主义：删除爆炸特效，使用静态展示
    - 继承 V12 的几何误差可视化优势
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        # V14 叙事重构：设问
        # V14 新文案：解释"为什么"要用泰勒
        hud.show("Since we can't approach infinity, we settle for the next best thing: estimate using neighboring points. This is called 'finite differences'.", wait_after=1.5)
        slow_wait(self, 1.0)
        
        # V14 叙事重构：困境
        hud.show("But directly subtracting introduces error.", wait_after=1.0)
        slow_wait(self, 1.0)

        # V14 极简主义：低饱和度坐标轴
        axes_config = MinimalismHelper.create_focus_axes(stroke_opacity=0.3)
        axes = Axes(
            x_range=[-1, 3, 1],
            y_range=[-1, 3, 1],
            x_length=6,
            y_length=3.5,
            axis_config=axes_config,
            tips=False,
        ).to_edge(LEFT, buff=0.8)

        def g(x): return 1 + 0.6 * x + 0.4 * x**2

        # V14 极简主义：背景函数低饱和度
        graph = axes.plot(g, x_range=[-0.8, 2.5], color=PALETTE["MATH_FUNC"], stroke_width=4)
        graph = MinimalismHelper.create_background_element(graph, opacity=0.3)
        self.add_to_math_group(axes, graph)
        
        # V14 节奏控制：慢动作展示
        slow_play(self, Create(axes), base_run_time=1.2)
        slow_play(self, Create(graph), base_run_time=1.2)
        slow_wait(self, 0.5)

        # 前向/后向斜率标注
        x0 = 1.0
        dx = 1.0
        y0 = g(x0)
        forward_pt = axes.c2p(x0 + dx, g(x0 + dx))
        backward_pt = axes.c2p(x0 - dx, g(x0 - dx))
        center_pt = axes.c2p(x0, y0)

        # V13: 使用语义化颜色
        forward_line = Line(center_pt, forward_pt, color=PALETTE["MATH_ERROR"], stroke_width=3)
        backward_line = Line(center_pt, backward_pt, color=PALETTE["MATH_ERROR"], stroke_width=3)
        self.add_to_math_group(forward_line, backward_line)

        fwd_label = MathTex("f'(x)_{+}", font_size=28, color=PALETTE["MATH_ERROR"]).next_to(forward_line, UP, buff=0.2)
        bwd_label = MathTex("f'(x)_{-}", font_size=28, color=PALETTE["MATH_ERROR"]).next_to(backward_line, DOWN, buff=0.2)
        self.add_to_math_group(fwd_label, bwd_label)

        # V14 节奏控制：慢动作展示
        slow_play(self, Create(forward_line), base_run_time=1.0)
        slow_play(self, Write(fwd_label), base_run_time=1.0)
        slow_wait(self, 0.5)
        slow_play(self, Create(backward_line), base_run_time=1.0)
        slow_play(self, Write(bwd_label), base_run_time=1.0)
        slow_wait(self, 1.0)

        # V14 叙事重构：展示困境
        hud.show("Forward and backward differences each have systematic errors: odd and even order terms get mixed together.", wait_after=1.5)
        slow_wait(self, 1.0)

        # --------------------------------------------------------------------
        # 几何误差向量（V12 修复核心）
        # --------------------------------------------------------------------
        g_prime_x0 = 0.6 + 0.8 * x0
        linear_approx_forward = y0 + g_prime_x0 * dx
        linear_approx_backward = y0 - g_prime_x0 * dx
        actual_forward = g(x0 + dx)
        actual_backward = g(x0 - dx)

        # V13: 使用 NeonLine 智能组件（解决 #14）
        fx_error_forward = NeonLine.create(
            axes.c2p(x0 + dx, y0 - 0.1),
            axes.c2p(x0 + dx, y0 + 0.1),
            color=PALETTE["MATH_ERROR"],
            stroke_width=6.5
        )
        fx_error_backward = NeonLine.create(
            axes.c2p(x0 - dx, y0 - 0.1),
            axes.c2p(x0 - dx, y0 + 0.1),
            color=PALETTE["MATH_ERROR"],
            stroke_width=6.5
        )

        # f''(x) 二阶项误差（线性近似与真实值的偏差）
        fdd_error_forward = NeonLine.create(
            axes.c2p(x0 + dx, linear_approx_forward),
            axes.c2p(x0 + dx, actual_forward),
            color=PALETTE["MATH_ERROR"],
            stroke_width=5.5
        )
        fdd_error_backward = NeonLine.create(
            axes.c2p(x0 - dx, linear_approx_backward),
            axes.c2p(x0 - dx, actual_backward),
            color=PALETTE["MATH_ERROR"],
            stroke_width=5.5
        )
        self.add_to_math_group(fx_error_forward, fx_error_backward, fdd_error_forward, fdd_error_backward)

        # V13: NeonLine 返回 VGroup，需要分别处理
        fx_error_forward_group = fx_error_forward
        fx_error_backward_group = fx_error_backward
        fdd_error_forward_group = fdd_error_forward
        fdd_error_backward_group = fdd_error_backward
        
        # V14 节奏控制：慢动作展示误差
        slow_play(self, Create(fx_error_forward_group), base_run_time=1.0)
        slow_play(self, Create(fx_error_backward_group), base_run_time=1.0)
        # V14 节奏控制：复杂图形变化后必须等待2秒
        slow_wait(self, 2.0)
        slow_play(self, Create(fdd_error_forward_group), base_run_time=0.8)
        slow_play(self, Create(fdd_error_backward_group), base_run_time=0.8)
        # V14 节奏控制：复杂图形变化后必须等待2秒
        slow_wait(self, 2.0)
        
        # 提取实际的 Line 对象用于后续操作
        fx_error_forward = fx_error_forward_group[1] if isinstance(fx_error_forward_group, VGroup) else fx_error_forward_group
        fx_error_backward = fx_error_backward_group[1] if isinstance(fx_error_backward_group, VGroup) else fx_error_backward_group
        fdd_error_forward = fdd_error_forward_group[1] if isinstance(fdd_error_forward_group, VGroup) else fdd_error_forward_group
        fdd_error_backward = fdd_error_backward_group[1] if isinstance(fdd_error_backward_group, VGroup) else fdd_error_backward_group
        slow_wait(self, 0.4)  # V14 节奏控制：所有等待时间使用 slow_wait

        # 泰勒展开公式
        right_tex = MathTex(
            r"f(x+1) \approx f(x) + f'(x) + \tfrac{1}{2}f''(x)",
            font_size=32,
            color=WHITE,
        )
        left_tex = MathTex(
            r"f(x-1) \approx f(x) - f'(x) + \tfrac{1}{2}f''(x)",
            font_size=32,
            color=WHITE,
        )
        # V14 增强：定位后再检查，使用保守模式（避免过度调整）
        right_tex.to_edge(UP, buff=1.2).shift(RIGHT * 2.3)
        left_tex.next_to(right_tex, DOWN, buff=0.6, aligned_edge=LEFT)
        # V14 增强：只在定位后检查一次，使用保守模式
        ensure_safe_bounds(right_tex, conservative=True, scale_factor=0.98)
        ensure_safe_bounds(left_tex, conservative=True, scale_factor=0.98)

        # V14 叙事重构：解决（展示巧合）
        # V14 新文案：解释"为什么"误差能抵消
        hud.show("Here's a mathematical coincidence: if we look at both the point to the left and the point to the right (using Taylor expansion)...", wait_after=1.5)
        slow_wait(self, 1.0)
        
        # V14 节奏控制：分步呈现公式（按照文档要求：先写右边，停顿，再写左边）
        # 文档要求：慢慢写出右边，停顿给观众读的时间，再慢慢写出左边
        # V14 节奏控制：分步呈现公式（按照文档要求：先写右边，停顿，再写左边）
        # 文档要求：慢慢写出右边，停顿给观众读的时间，再慢慢写出左边
        self.play(Write(right_tex), run_time=2.5 * PacingController.SLOW_MOTION_FACTOR)  # 慢慢写出右边
        slow_wait(self, 1.0)  # 停顿，给观众读的时间
        self.play(Write(left_tex), run_time=2.5 * PacingController.SLOW_MOTION_FACTOR)  # 慢慢写出左边
        # V14 节奏控制：3秒法则（核心公式推导后必须等待3秒）
        slow_wait(self, 3.0)  # 让观众看清楚公式的每一项

        # V14 新文案：解释误差抵消
        hud.show("You'll find that their errors point in opposite directions.", wait_after=1.5)
        slow_wait(self, 1.0)

        # --------------------------------------------------------------------
        # 几何抵消动画：符号飞向误差线并爆炸
        # --------------------------------------------------------------------
        fx_forward = right_tex.get_part_by_tex("f(x)")
        fx_backward = left_tex.get_part_by_tex("f(x)")
        fdd_forward = right_tex.get_part_by_tex("f''(x)")
        fdd_backward = left_tex.get_part_by_tex("f''(x)")

        # V14 极简主义：静态高亮框（不闪烁、不呼吸）
        fx_rect1 = MinimalismHelper.create_static_highlight(fx_forward, color=PALETTE["MATH_FUNC"])
        fx_rect2 = MinimalismHelper.create_static_highlight(fx_backward, color=PALETTE["MATH_FUNC"])
        self.add_to_math_group(right_tex, left_tex, fx_rect1, fx_rect2)
        slow_play(self, Create(fx_rect1), base_run_time=0.8)
        slow_play(self, Create(fx_rect2), base_run_time=0.8)
        slow_wait(self, 1.0)  # 让观众看清楚高亮的部分

        fx_forward_copy = fx_forward.copy().set_opacity(1)
        fx_backward_copy = fx_backward.copy().set_opacity(1)
        center_pt = axes.c2p(x0, y0)
        self.add(fx_forward_copy, fx_backward_copy)

        self.play(
            FadeOut(fx_rect1), FadeOut(fx_rect2),
            fx_forward.animate.set_opacity(0.25),
            fx_backward.animate.set_opacity(0.25),
            fx_forward_copy.animate.scale(0.5).move_to(center_pt),
            fx_backward_copy.animate.scale(0.5).move_to(center_pt),
            run_time=1.0,
            rate_func=smooth
        )

        # V14 极简主义：删除爆炸特效，使用静态展示
        # V14 新文案：展示误差抵消
        hud.show("If we add them together... something magical happens: the errors cancel each other out.", wait_after=1.5)
        slow_wait(self, 1.0)
        
        # V14 极简主义：静态展示抵消过程（不闪烁，不爆炸）
        error_group_fx = VGroup(fx_error_forward_group, fx_error_backward_group, fx_forward_copy, fx_backward_copy)
        # 静态展示：误差项逐渐变淡消失
        self.play(
            error_group_fx.animate.set_opacity(0),
            run_time=2.0 * PacingController.SLOW_MOTION_FACTOR,
            rate_func=smooth
        )
        # V14 节奏控制：复杂图形变化后必须等待2秒
        slow_wait(self, 2.0)

        # V14 极简主义：静态高亮框（不闪烁、不呼吸）
        fdd_rect1 = MinimalismHelper.create_static_highlight(fdd_forward, color=PALETTE["MATH_FUNC"])
        fdd_rect2 = MinimalismHelper.create_static_highlight(fdd_backward, color=PALETTE["MATH_FUNC"])
        self.add_to_math_group(fdd_rect1, fdd_rect2)
        slow_play(self, Create(fdd_rect1), base_run_time=0.8)
        slow_play(self, Create(fdd_rect2), base_run_time=0.8)
        slow_wait(self, 1.0)  # 让观众看清楚高亮的部分

        fdd_forward_copy = fdd_forward.copy().set_opacity(1)
        fdd_backward_copy = fdd_backward.copy().set_opacity(1)
        self.add(fdd_forward_copy, fdd_backward_copy)

        self.play(
            FadeOut(fdd_rect1), FadeOut(fdd_rect2),
            fdd_forward.animate.set_opacity(0.25),
            fdd_backward.animate.set_opacity(0.25),
            fdd_forward_copy.animate.scale(0.01).move_to(fdd_error_forward.get_center()),
            fdd_backward_copy.animate.scale(0.01).move_to(fdd_error_backward.get_center()),
            run_time=1.0,
            rate_func=smooth
        )

        # V14 极简主义：删除爆炸特效，使用静态展示
        error_group_fdd = VGroup(fdd_error_forward_group, fdd_error_backward_group)
        # 静态展示：二阶误差项逐渐变淡消失
        self.play(
            error_group_fdd.animate.set_opacity(0),
            FadeOut(VGroup(fdd_forward_copy, fdd_backward_copy)),
            run_time=2.0 * PacingController.SLOW_MOTION_FACTOR,
            rate_func=smooth
        )
        # V14 节奏控制：复杂图形变化后必须等待2秒
        slow_wait(self, 2.0)

        # 中心差分结果
        diff_tex = MathTex(
            r"f'(x) \approx \dfrac{f(x+1) - f(x-1)}{2}",
            font_size=40,
            color=WHITE,
        ).move_to(RIGHT * 2.8 + DOWN * 0.3)
        # V14 增强：确保公式在安全区域内（保守模式，避免过度缩放）
        ensure_safe_bounds(diff_tex, conservative=True, scale_factor=0.98)

        # V14 节奏控制：慢动作展示结果
        self.play(TransformMatchingTex(VGroup(right_tex, left_tex), diff_tex), run_time=1.8 * PacingController.SLOW_MOTION_FACTOR)
        # V14 节奏控制：3秒法则
        slow_wait(self, 3.0)

        # V14 极简主义：静态高亮框（不闪烁、不呼吸）
        f_prime_part = diff_tex.get_part_by_tex("f'(x)")
        f_prime_highlight = MinimalismHelper.create_static_highlight(
            f_prime_part,
            color=PALETTE["MATH_ERROR"]
        )
        coeff = MathTex(r"[-1,\;0,\;1]", font_size=36, color=PALETTE["HIGHLIGHT"]).next_to(diff_tex, DOWN, buff=0.5)
        self.add_to_math_group(diff_tex, coeff, f_prime_highlight)
        
        # V14 节奏控制：慢动作展示
        slow_play(self, Write(coeff), base_run_time=1.2)
        slow_play(self, Create(f_prime_highlight), base_run_time=1.2)
        # V14 节奏控制：核心公式推导完成后必须等待3秒
        slow_wait(self, 3.0)

        # V14 叙事重构：验证
        # V14 新文案：导出算子
        hud.show("This is the central difference method, and it's half the soul of Sobel.", wait_after=1.5)
        slow_wait(self, 2.0)
        
        slow_play(self, FadeOut(f_prime_highlight), base_run_time=0.6)

        # V13: 使用生命周期管理
        hud.clear()
        self.clear_scene(fade_out=True, run_time=1.0)
        slow_wait(self, 0.3)  # V14 节奏控制：所有等待时间使用 slow_wait


# =============================================================================
# Scene 2.5：差分对比（V13 升级版 - 语义化差分颜色）
# =============================================================================
class Scene2_5Comparison(BaseScene):
    """
    差分对比（V14 叙事重构版）
    V14 改进内容：
    - 节奏控制：慢动作展示
    - 极简主义：降低背景饱和度
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        # V14 叙事重构：设问
        hud.show("Three types of differences: forward, backward, and central—which has the smallest error?", wait_after=1.5)
        slow_wait(self, 1.0)

        # V14 极简主义：低饱和度坐标轴
        axes_config = MinimalismHelper.create_focus_axes(stroke_opacity=0.3)
        x_rng = [0, 8, 1]
        y_rng = [0, 6, 1]
        def f(x): return 2 + 0.8 * np.sin(0.8 * x) + 0.6 * np.sin(0.3 * x + 0.5)

        # 三列坐标轴
        axes_forward = Axes(x_range=x_rng, y_range=y_rng, x_length=5.2, y_length=3.2, axis_config=axes_config, tips=False)
        axes_backward = axes_forward.copy()
        axes_center = axes_forward.copy()
        axes_group = VGroup(axes_forward, axes_backward, axes_center).arrange(RIGHT, buff=0.7).to_edge(UP, buff=0.6)

        # V13: 使用语义化差分颜色（解决 #16）
        labels = VGroup(
            safer_text("Forward", font_size=24, color=PALETTE["DIFF_FWD"]),
            safer_text("Backward", font_size=24, color=PALETTE["DIFF_BWD"]),
            safer_text("Central", font_size=24, color=PALETTE["DIFF_CTR"]),
        )
        self.add_to_math_group(axes_group, labels)
        labels.arrange(RIGHT, buff=2.5).next_to(axes_group, UP, buff=0.25)

        # V14 节奏控制：慢动作展示
        slow_play(self, FadeIn(VGroup(axes_group, labels), shift=UP * 0.2), base_run_time=1.2)

        x0s = np.linspace(1, 7, 7)
        dx = 1.0

        forward_points = []
        backward_points = []
        center_points = []
        for x0 in x0s:
            fwd = (f(x0 + dx) - f(x0)) / dx
            bwd = (f(x0) - f(x0 - dx)) / dx
            cen = (f(x0 + dx) - f(x0 - dx)) / (2 * dx)
            forward_points.append((x0, fwd))
            backward_points.append((x0, bwd))
            center_points.append((x0, cen))

        def scatter(points, ax, color):
            dots = VGroup()
            for x, y in points:
                dots.add(Dot(ax.c2p(x, y), color=color, radius=0.06))
            return dots

        # V13: 使用语义化差分颜色
        forward_dots = scatter(forward_points, axes_forward, PALETTE["DIFF_FWD"])
        backward_dots = scatter(backward_points, axes_backward, PALETTE["DIFF_BWD"])
        center_dots = scatter(center_points, axes_center, PALETTE["DIFF_CTR"])
        self.add_to_math_group(forward_dots, backward_dots, center_dots)

        # V14 节奏控制：慢动作展示
        self.play(
            FadeIn(forward_dots, lag_ratio=0.05),
            FadeIn(backward_dots, lag_ratio=0.05),
            FadeIn(center_dots, lag_ratio=0.05),
            run_time=1.6 * PacingController.SLOW_MOTION_FACTOR
        )
        slow_wait(self, 1.5)

        # V14 叙事重构：验证
        hud.show("Central difference uses information from both sides, giving it a higher order of accuracy.", wait_after=1.5)
        slow_wait(self, 2.0)

        # 误差热力条（示意）
        def error_bar(val, max_val=1.2):
            alpha = np.clip(abs(val) / max_val, 0, 1)
            # V13: 使用语义化颜色
            color = interpolate_color(ManimColor(PALETTE["MATH_FUNC"]), ManimColor(PALETTE["MATH_ERROR"]), alpha)
            bar = Rectangle(width=0.25, height=1.1 * alpha, fill_opacity=0.8, fill_color=color, stroke_width=0)
            return bar

        bars_fwd = VGroup(*[error_bar(fwd[1]) for fwd in forward_points]).arrange(RIGHT, buff=0.05)
        bars_bwd = VGroup(*[error_bar(bwd[1]) for bwd in backward_points]).arrange(RIGHT, buff=0.05)
        bars_cen = VGroup(*[error_bar(cen[1]) for cen in center_points]).arrange(RIGHT, buff=0.05)
        heatmap = VGroup(bars_fwd, bars_bwd, bars_cen).arrange(DOWN, buff=0.3).to_edge(DOWN, buff=0.9)

        heat_labels = VGroup(
            safer_text("Error Intensity (Illustration)", font_size=24, color=WHITE).next_to(heatmap, UP, buff=0.25),
            safer_text("Red = High Error, Blue-Green = Low Error", font_size=20, color=GREY_B).next_to(heatmap, DOWN, buff=0.2),
        )

        slow_play(self, FadeIn(VGroup(heatmap, heat_labels), shift=UP * 0.2), base_run_time=1.0)
        slow_wait(self, 1.0)  # V14 节奏控制：所有等待时间使用 slow_wait

        hud.show("Central difference is the 'coolest'—it has the lowest error.", wait_after=1.2)

        # 实际函数上三条差分曲线对比
        axes_real = Axes(
            x_range=x_rng, y_range=[-3, 3, 1],
            x_length=10,
            y_length=3,
            axis_config=axes_config,
            tips=False,
        ).to_edge(DOWN, buff=0.35)
        # V13: 使用语义化差分颜色
        fwd_graph = axes_real.plot(lambda x: (f(x + dx) - f(x)) / dx, x_range=[1, 7], color=PALETTE["DIFF_FWD"], stroke_width=2.5, stroke_opacity=0.8)
        bwd_graph = axes_real.plot(lambda x: (f(x) - f(x - dx)) / dx, x_range=[1, 7], color=PALETTE["DIFF_BWD"], stroke_width=2.5, stroke_opacity=0.65)
        cen_graph = axes_real.plot(lambda x: (f(x + dx) - f(x - dx)) / (2 * dx), x_range=[1, 7], color=PALETTE["DIFF_CTR"], stroke_width=3.2)
        legend = VGroup(
            safer_text("Forward", font_size=20, color=PALETTE["DIFF_FWD"]),
            safer_text("Backward", font_size=20, color=PALETTE["DIFF_BWD"]),
            safer_text("Central", font_size=20, color=PALETTE["DIFF_CTR"]),
        )
        legend.arrange(RIGHT, buff=0.6).to_corner(UR, buff=0.2)
        self.add_to_math_group(axes_real, fwd_graph, bwd_graph, cen_graph, legend)

        # V14 节奏控制：慢动作展示
        slow_play(self, Create(axes_real), base_run_time=1.0)
        slow_play(self, FadeIn(legend, shift=UP * 0.1), base_run_time=1.0)
        slow_play(self, Create(fwd_graph), base_run_time=0.8)
        slow_play(self, Create(bwd_graph), base_run_time=0.8)
        slow_play(self, Create(cen_graph), base_run_time=0.8)
        # V14 节奏控制：复杂图形变化后必须等待2秒
        slow_wait(self, 2.0)

        hud.show("Conclusion: central difference = low error, symmetric sampling.", wait_after=1.4)

        # V13: 使用生命周期管理
        hud.clear()
        self.clear_scene(fade_out=True, run_time=1.2)
        slow_wait(self, 0.4)  # V14 节奏控制：所有等待时间使用 slow_wait

# =============================================================================
# Scene 3：Sobel 诞生（V13 升级版 - 布局网格）
# =============================================================================
class Scene3SobelConstruct(BaseScene):
    """
    第四部分：构造 Sobel（V14 叙事重构版）
    V14 改进内容：
    - 叙事重构：解释 Sobel 的构造逻辑（平滑×微分）
    - 节奏控制：慢动作展示窗口滑动
    - 极简主义：删除 apply_wave_effect，使用静态展示
    - 继承 V12 的局部卷积直觉优势
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        # V14 叙事重构：设问
        # V14 新文案：解释 Sobel 的构造逻辑
        hud.show("Now we have two tools: smoothing (to deal with noise) and central difference (to calculate slope).", wait_after=1.5)
        slow_wait(self, 1.0)

        # V14 极简主义：低饱和度坐标轴
        axes_config = MinimalismHelper.create_focus_axes(stroke_opacity=0.3)
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-2, 3, 1],
            x_length=10,
            y_length=4,
            axis_config=axes_config,
            tips=False,
        ).to_edge(LEFT, buff=0.8)

        def clean(x): return np.sin(x * 0.6)
        rng = np.random.default_rng(1)
        noise = lambda x: 0.35 * rng.normal(0, 1)
        noisy = lambda x: clean(x) + noise(x)

        # V14 极简主义：噪声图作为背景（低饱和度）
        noisy_graph = axes.plot(lambda x: noisy(x), x_range=[0, 10], color=PALETTE["MATH_ERROR"], stroke_width=3.5)
        noisy_graph = MinimalismHelper.create_background_element(noisy_graph, opacity=0.3)
        clean_graph = axes.plot(lambda x: clean(x), x_range=[0, 10], color=PALETTE["MATH_FUNC"], stroke_width=3)
        clean_graph = MinimalismHelper.create_background_element(clean_graph, opacity=0.3)
        self.add_to_math_group(axes, noisy_graph, clean_graph)

        # V14 节奏控制：慢动作展示
        slow_play(self, Create(axes), base_run_time=0.8)
        slow_play(self, Create(noisy_graph), base_run_time=1.2)
        slow_play(self, FadeIn(clean_graph), base_run_time=0.8)
        slow_wait(self, 1.0)

        # V14 叙事重构：困境
        hud.show("Direct differentiation amplifies noise.", wait_after=1.0)
        slow_wait(self, 1.0)

        # V13: 使用布局网格（LEFT_COL, RIGHT_COL）
        diff_kernel = Matrix([[-1, 0, 1]], bracket_h_buff=0.2, bracket_v_buff=0.2)
        diff_kernel.set_color(PALETTE["MATH_ERROR"]).scale(0.9)
        diff_label = safer_text("Differentiation Kernel", font_size=22, color=PALETTE["MATH_ERROR"]).next_to(diff_kernel, DOWN, buff=0.2)
        diff_group = VGroup(diff_kernel, diff_label).move_to(RIGHT_COL + UP * 1.5)
        self.add_to_math_group(diff_group)

        slow_play(self, FadeIn(diff_group, shift=UP * 0.2), base_run_time=0.8)
        slow_wait(self, 0.6)  # V14 节奏控制：所有等待时间使用 slow_wait

        # 微分结果示意
        diff_axes_config = default_axis_config(stroke_opacity=0.9, stroke_width=2, stroke_color=GREY_B)
        diff_axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-3, 3, 1],
            x_length=8,
            y_length=3,
            axis_config=diff_axes_config,
            tips=False,
        ).to_edge(RIGHT, buff=0.8).shift(DOWN * 0.6)

        def fake_grad(x): return 1.5 * (noisy(x + 0.1) - noisy(x - 0.1)) / 0.2

        # V14 极简主义：删除 apply_wave_effect，使用静态展示
        grad_graph = diff_axes.plot(lambda x: fake_grad(x), x_range=[0, 10], color=PALETTE["MATH_ERROR"], stroke_width=3.5)
        self.add_to_math_group(diff_axes, grad_graph)
        
        # V14 节奏控制：慢动作展示
        slow_play(self, Create(diff_axes), base_run_time=1.2)
        slow_play(self, Create(grad_graph), base_run_time=1.2)
        # V14 极简主义：删除 apply_wave_effect，静态展示噪声放大效果
        slow_wait(self, 2.0)  # 让观众看清楚噪声被放大

        # V14 叙事重构：解决
        # V14 新文案：解释解决方案
        hud.show("Smooth first, then differentiate: use [1,2,1]^T for low-pass filtering, then [-1,0,1] for high-pass.", wait_after=1.5)
        slow_wait(self, 1.0)

        # V13: 使用布局网格
        smooth_kernel = Matrix([[1], [2], [1]], bracket_h_buff=0.2, bracket_v_buff=0.2)
        smooth_kernel.set_color(PALETTE["MATH_FUNC"]).scale(0.9)
        smooth_label = safer_text("Smoothing Kernel", font_size=22, color=PALETTE["MATH_FUNC"]).next_to(smooth_kernel, RIGHT, buff=0.25)
        smooth_group = VGroup(smooth_kernel, smooth_label).move_to(RIGHT_COL + UP * 0.3)
        self.add_to_math_group(smooth_group)

        slow_play(self, FadeIn(smooth_group, shift=DOWN * 0.2), base_run_time=0.8)
        slow_wait(self, 0.4)  # V14 节奏控制：所有等待时间使用 slow_wait

        # ------------------------------------------------------------
        # 窗口滑动可视化（V12 核心修复：局部卷积直觉）
        # ------------------------------------------------------------
        hud.show("The smoothing kernel slides over the signal: points within the window get weighted and averaged, flattening out.", wait_after=1.2)

        def smoothed_func(x, window_center):
            """
            模拟平滑核 [1,2,1] 的局部加权平均
            window_center: 窗口中心位置
            """
            window_width = 1.0
            dist = abs(x - window_center)

            if dist <= window_width:
                # 三角形权重，线性衰减，近似 [1,2,1] 的局部平均
                w = window_width * 0.5
                local_blend = np.clip(1 - dist / w, 0, 1)
                return (1 - local_blend) * noisy(x) + local_blend * clean(x)
            else:
                return noisy(x)

        window_tracker = ValueTracker(0.5)

        # V13: 使用语义化颜色
        smoothed_graph = axes.plot(
            lambda x: smoothed_func(x, window_tracker.get_value()),
            x_range=[0, 10],
            color=PALETTE["MATH_FUNC"],
            stroke_width=3.5,
        )

        window_rect = Rectangle(
            width=1.0 * axes.x_axis.unit_size,
            height=axes.y_length,
            stroke_color=PALETTE["MATH_FUNC"],
            stroke_width=3,
            fill_color=PALETTE["MATH_FUNC"],
            fill_opacity=0.15,
        )
        self.add_to_math_group(smoothed_graph, window_rect)

        def update_window_rect(mob):
            window_center = window_tracker.get_value()
            center_pos = axes.c2p(window_center, 0)
            mob.move_to(center_pos)

        window_rect.add_updater(update_window_rect)
        self.add(smoothed_graph, window_rect)

        target_window = 9.5
        target_graph = axes.plot(
            lambda x: smoothed_func(x, target_window),
            x_range=[0, 10],
            color=PALETTE["MATH_FUNC"],
            stroke_width=3.5,
        )
        # V14 节奏控制：慢动作展示窗口滑动（核心动画至少 3-4 秒）
        self.play(
            window_tracker.animate.set_value(target_window),
            Transform(smoothed_graph, target_graph),
            run_time=4.0 * PacingController.SLOW_MOTION_FACTOR,  # 慢动作
            rate_func=smooth
        )
        # V14 节奏控制：3秒法则
        slow_wait(self, 2.0)

        window_rect.remove_updater(update_window_rect)

        # V14 叙事重构：验证
        hud.show("After smoothing, noise is suppressed, and the signal structure becomes clearer.", wait_after=1.5)
        slow_wait(self, 1.5)
        self.play(
            noisy_graph.animate.set_opacity(0.3),
            FadeOut(window_rect),
            run_time=0.8
        )
        slow_wait(self, 0.6)  # V14 节奏控制：所有等待时间使用 slow_wait

        # 外积生成 Sobel
        multiply = MathTex(r"\times", font_size=44, color=WHITE)
        equal = MathTex(r"=", font_size=44, color=WHITE)
        sobel_values = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        sobel_matrix = IntegerMatrix(sobel_values, element_alignment_corner=ORIGIN).scale(0.9)
        # V13: 使用语义化颜色渐变
        sobel_matrix.set_color_by_gradient(PALETTE["MATH_ERROR"], PALETTE["HIGHLIGHT"], PALETTE["MATH_FUNC"])

        # V13: 使用布局网格（LEFT_COL, RIGHT_COL）
        eq_group = VGroup(
            smooth_kernel.copy(),
            multiply,
            diff_kernel.copy(),
            equal,
            sobel_matrix
        ).arrange(RIGHT, buff=0.3).move_to(RIGHT_COL + UP * 0.5)
        self.add_to_math_group(eq_group)

        # V14 节奏控制：慢动作展示
        slow_play(self, Write(multiply), base_run_time=1.4)
        slow_play(self, Write(equal), base_run_time=1.4)
        slow_play(self, FadeIn(sobel_matrix, shift=RIGHT * 0.2), base_run_time=1.4)
        self.play(Transform(VGroup(smooth_kernel, diff_kernel), VGroup(eq_group[0], eq_group[2])), run_time=0.001)
        slow_wait(self, 1.5)

        # V14 叙事重构：验证
        # V14 新文案：解释 Sobel 的本质
        hud.show("The Sobel operator isn't really a new invention—it just cleverly packages these two actions into a single 3×3 box.", wait_after=1.5)
        slow_wait(self, 1.0)
        hud.show("One hand suppresses noise, the other extracts edges.", wait_after=2.0)
        slow_wait(self, 2.0)

        # V14 极简主义：静态高亮框（不闪烁、不呼吸）
        rect = MinimalismHelper.create_static_highlight(
            sobel_matrix,
            color=PALETTE["HIGHLIGHT"]
        )
        self.add_to_math_group(rect)
        slow_play(self, Create(rect), base_run_time=0.8)
        # V14 节奏控制：3秒法则（让观众思考）
        slow_wait(self, 3.0)

        self.play(FadeOut(VGroup(
            axes, noisy_graph, clean_graph, smoothed_graph,
            diff_axes, grad_graph, diff_group, smooth_group, eq_group, rect
        )), run_time=1.0)
        hud.clear()
        slow_wait(self, 0.3)  # V14 节奏控制：所有等待时间使用 slow_wait


# =============================================================================
# Scene 3.5：卷积可视化（滑动窗口 + 结果填充）
# =============================================================================
class Scene3_5Convolution(BaseScene):
    """
    卷积可视化（V14 叙事重构版）
    V14 改进内容：
    - 节奏控制：慢动作展示卷积过程
    - 极简主义：静态展示，删除装饰性动画
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        # V14 叙事重构：设问
        hud.show("Convolution equals a sliding window's weighted sum. Let's see how Sobel works.", wait_after=1.5)
        slow_wait(self, 1.0)

        size = 8
        # 简单梯度图像（左暗右亮） + 一条亮线制造边缘
        image_vals = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                image_vals[i, j] = j / (size - 1)
                if j == size // 2:
                    image_vals[i, j] += 0.35
        image_vals = np.clip(image_vals, 0, 1)

        cell = 0.42
        image_group = VGroup()
        for i in range(size):
            for j in range(size):
                val = image_vals[i, j]
                sq = Square(side_length=cell, stroke_width=0, fill_opacity=1)
                sq.set_fill(interpolate_color(BLACK, WHITE, val))
                sq.move_to(RIGHT * (j - size / 2) * cell + UP * (size / 2 - i) * cell)
                image_group.add(sq)
        image_box = SurroundingRectangle(image_group, color=GREY_B, stroke_width=2)
        image_full = VGroup(image_box, image_group).to_edge(LEFT, buff=0.8)

        # Sobel 核
        sobel_kernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        # V13: 使用语义化颜色
        kernel_matrix = IntegerMatrix(sobel_kernel.tolist()).set_color_by_gradient(PALETTE["MATH_ERROR"], PALETTE["HIGHLIGHT"], PALETTE["MATH_FUNC"]).scale(0.7)
        kernel_label = safer_text("Sobel Kernel", font_size=24, color=PALETTE["MATH_ERROR"]).next_to(kernel_matrix, DOWN, buff=0.2)
        kernel_group = VGroup(kernel_matrix, kernel_label).next_to(image_full, RIGHT, buff=0.9)

        # 结果矩阵占位
        result_group = VGroup()
        for i in range(size):
            for j in range(size):
                sq = Square(side_length=cell, stroke_width=1, stroke_color=GREY_B, fill_opacity=0.08)
                sq.move_to(RIGHT * (j - size / 2) * cell + UP * (size / 2 - i) * cell)
                result_group.add(sq)
        result_box = SurroundingRectangle(result_group, color=GREY_B, stroke_width=2)
        result_full = VGroup(result_box, result_group).to_edge(RIGHT, buff=0.8)
        result_label = safer_text("Convolution Result", font_size=24, color=PALETTE["MATH_FUNC"]).next_to(result_full, UP, buff=0.25)
        
        # V13: 添加到数学组（在定义之后）
        self.add_to_math_group(image_full, kernel_group, result_full, result_label)

        self.play(
            FadeIn(image_full, shift=UP * 0.2),
            FadeIn(kernel_group, shift=UP * 0.2),
            FadeIn(VGroup(result_full, result_label), shift=UP * 0.2),
            run_time=1.4
        )
        slow_wait(self, 0.6)  # V14 节奏控制：所有等待时间使用 slow_wait

        hud.show("The window scans row by row, computing G = kernel · local patch at each step.", wait_after=1.0)

        # 滑动窗口框
        # V13: 使用语义化颜色
        window = Square(side_length=cell * 3, stroke_color=PALETTE["MATH_FUNC"], stroke_width=3, fill_color=PALETTE["MATH_FUNC"], fill_opacity=0.12)
        self.add_to_math_group(window)

        def window_pos(i, j):
            return RIGHT * ((j - 1) - size / 2 + 0.5) * cell + UP * ((size / 2 - i + 1) - 0.5) * cell

        # 结果填充函数
        result_values = np.zeros_like(image_vals)
        fill_group = VGroup()

        animations = []
        for i in range(1, size - 1):
            for j in range(1, size - 1):
                patch = image_vals[i - 1:i + 2, j - 1:j + 2]
                conv_val = float(np.sum(patch * sobel_kernel))
                result_values[i, j] = conv_val
                # V13: 使用语义化颜色
                alpha = np.clip(abs(conv_val) / 4.0, 0, 1)
                color = interpolate_color(ManimColor(PALETTE["MATH_FUNC"]), ManimColor(PALETTE["MATH_ERROR"]), alpha)

                cell_rect = Square(side_length=cell, stroke_width=0, fill_opacity=0.9)
                cell_rect.set_fill(color)
                cell_rect.move_to(result_group[(i * size) + j].get_center())
                fill_group.add(cell_rect)

                pos = window_pos(i, j)
                animations.append((
                    pos,
                    conv_val,
                    cell_rect
                ))

        # 逐步播放扫描和填充（窗口旁实时显示局部卷积值）
        conv_tracker = ValueTracker(0.0)
        readout = always_redraw(lambda: DecimalNumber(
            conv_tracker.get_value(),
            num_decimal_places=2,
            font_size=26,
            color=PALETTE["MATH_ERROR"]
        ).next_to(window, UP, buff=0.2))
        self.add_to_math_group(readout)

        for step, (pos, conv_val, cell_rect) in enumerate(animations):
            conv_tracker.set_value(conv_val)
            self.play(window.animate.move_to(image_full.get_center() + pos), run_time=0.25, rate_func=smooth)
            self.play(FadeIn(cell_rect, scale=0.3), run_time=0.15)
        slow_wait(self, 0.6)  # V14 节奏控制：所有等待时间使用 slow_wait

        hud.show("The convolution result fills in gradually: red = strong edges, blue-green = weak.", wait_after=1.2)
        slow_wait(self, 0.6)  # V14 节奏控制：所有等待时间使用 slow_wait

        # V13: 使用生命周期管理
        hud.clear()
        self.clear_scene(fade_out=True, run_time=1.0)
        slow_wait(self, 0.4)  # V14 节奏控制：所有等待时间使用 slow_wait


# =============================================================================
# Scene 4.2：多尺度边缘（3x3 / 5x5 / 7x7 对比）
# =============================================================================
class Scene4_2MultiScale(BaseScene):
    """
    多尺度边缘（V14 叙事重构版）
    V14 改进内容：
    - 节奏控制：慢动作展示
    - 极简主义：降低背景饱和度
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        # V14 叙事重构：设问
        hud.show("Scale determines detail: small kernels catch fine lines, large kernels catch coarse outlines.", wait_after=1.5)
        slow_wait(self, 1.0)

        # 构造简单 10x10 图：水平粗条 + 竖直细条
        size = 10
        cell = 0.24
        img_vals = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                img_vals[i, j] = j / (size - 1) * 0.6
        for j in range(size):  # 粗横条
            for i in [4, 5]:
                img_vals[i, j] += 0.35
        for i in range(size):  # 细竖条
            img_vals[i, size // 2] += 0.25
        img_vals = np.clip(img_vals, 0, 1)

        def make_image(vals, with_box=True):
            g = VGroup()
            rows, cols = vals.shape
            for i in range(rows):
                for j in range(cols):
                    sq = Square(side_length=cell, stroke_width=0, fill_opacity=1)
                    sq.set_fill(interpolate_color(BLACK, WHITE, vals[i, j]))
                    sq.move_to(RIGHT * (j - cols / 2) * cell + UP * (rows / 2 - i) * cell)
                    g.add(sq)
            if with_box:
                box = SurroundingRectangle(g, color=GREY_B, stroke_width=2)
                return VGroup(box, g)
            return g

        raw_img = make_image(img_vals)

        kernels = {
            "3×3": np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]),
            "5×5": np.array([
                [-2, -1, 0, 1, 2],
                [-3, -2, 0, 2, 3],
                [-4, -3, 0, 3, 4],
                [-3, -2, 0, 2, 3],
                [-2, -1, 0, 1, 2],
            ]),
            "7×7": np.array([
                [-3, -2, -1, 0, 1, 2, 3],
                [-4, -3, -2, 0, 2, 3, 4],
                [-5, -4, -3, 0, 3, 4, 5],
                [-6, -5, -4, 0, 4, 5, 6],
                [-5, -4, -3, 0, 3, 4, 5],
                [-4, -3, -2, 0, 2, 3, 4],
                [-3, -2, -1, 0, 1, 2, 3],
            ]),
        }

        def convolve(vals, kernel):
            h, w = vals.shape
            kh, kw = kernel.shape
            pad = kh // 2
            padded = np.pad(vals, pad, mode="edge")
            out = np.zeros_like(vals)
            for i in range(h):
                for j in range(w):
                    patch = padded[i:i + kh, j:j + kw]
                    out[i, j] = np.sum(patch * kernel)
            m = np.max(np.abs(out)) or 1.0
            out = (out / m + 1) / 2  # 归一化 0-1
            return out

        results = []
        for k in ["3×3", "5×5", "7×7"]:
            vals = convolve(img_vals, kernels[k])
            res_img = make_image(vals)
            # V13: 使用语义化颜色
            label = safer_text(f"Sobel {k}", font_size=22, color=PALETTE["MATH_ERROR"]).next_to(res_img, DOWN, buff=0.2)
            results.append(VGroup(res_img, label))

        grid = VGroup(
            VGroup(raw_img, safer_text("Original", font_size=22, color=WHITE).next_to(raw_img, DOWN, buff=0.2)),
            *results
        ).arrange(RIGHT, buff=0.6).scale(0.95).move_to(ORIGIN)

        self.play(FadeIn(grid, shift=UP * 0.2), run_time=1.6)
        slow_wait(self, 1.0)  # V14 节奏控制：所有等待时间使用 slow_wait

        hud.show("3×3 catches details, 7×7 is smoother with thicker edges.", wait_after=1.4)

        fused_vals = 0.4 * convolve(img_vals, kernels["3×3"]) + 0.35 * convolve(img_vals, kernels["5×5"]) + 0.25 * convolve(img_vals, kernels["7×7"])
        fused_img = make_image(fused_vals)
        # V13: 使用语义化颜色
        fused_label = safer_text("Multi-Scale Fusion", font_size=24, color=PALETTE["MATH_FUNC"]).next_to(fused_img, DOWN, buff=0.2)
        fused_group = VGroup(fused_img, fused_label).to_edge(DOWN, buff=0.6)
        # V13: 添加到数学组（在定义之后）
        self.add_to_math_group(grid, fused_group)

        self.play(FadeIn(fused_group, shift=UP * 0.2), run_time=1.0)
        slow_wait(self, 1.0)  # V14 节奏控制：所有等待时间使用 slow_wait

        hud.show("Fusing multiple scales: we preserve both detail and outline.", wait_after=1.2)

        # V13: 使用生命周期管理
        hud.clear()
        self.clear_scene(fade_out=True, run_time=1.0)
        slow_wait(self, 0.3)  # V14 节奏控制：所有等待时间使用 slow_wait

# =============================================================================
# Scene 4：3D 扫描（Sobel 在地形上滑窗）
# =============================================================================
class Scene4Vision(BaseThreeDScene):
    """
    3D 扫描可视化（V14 叙事重构版）
    V14 改进内容：
    - 节奏控制：慢动作展示扫描过程
    - 极简主义：降低背景饱和度
    """
    """第五部分：3D 扫描，颜色随梯度大小变化"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("Map brightness to height, and the image becomes a 3D terrain.", wait_after=1.8)

        q = get_quality_config()
        rows = cols = q["grid_size"]

        def height(u, v):
            u_n, v_n = u / cols, v / rows
            ridge = 1 / (1 + np.exp(-12 * (u_n - 0.35))) + 1 / (1 + np.exp(-12 * (u_n - 0.65)))
            bump = 0.25 * np.exp(-30 * ((u_n - 0.5)**2 + (v_n - 0.5)**2))
            return 0.6 * ridge + bump

        axes3d = ThreeDAxes(
            x_range=[0, cols, 5],
            y_range=[0, rows, 5],
            z_range=[0, 2.5, 0.5],
            x_length=7.5,
            y_length=7.5,
            z_length=3,
            axis_config={"include_tip": False, "stroke_opacity": 0.85, "stroke_width": 2, "stroke_color": GREY_B},
        )

        surface = Surface(
            lambda u, v: axes3d.c2p(u, v, height(u, v) * 2.2),
            u_range=[0, cols - 1],
            v_range=[0, rows - 1],
            resolution=q["surface_resolution"],
            should_make_jagged=False,
        )
        # V13: 使用语义化颜色
        surface.set_style(
            fill_opacity=0.8,
            stroke_color=PALETTE["MATH_FUNC"],
            stroke_width=q["stroke_width"] * 0.35,
            fill_color=PALETTE["MATH_FUNC"],
        )
        self.add_to_math_group(axes3d, surface)

        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        self.play(FadeIn(axes3d), FadeIn(surface), run_time=2.6)
        slow_wait(self, 1.0)  # V14 节奏控制：所有等待时间使用 slow_wait

        hud.show("Scan with a sliding window: the window's color changes with gradient magnitude.", wait_after=1.8)

        # V13: 单一信源驱动 - 先定义 get_scan_data 函数
        def get_scan_data(t):
            """统一的扫描数据函数，确保扫描框和示波器数据一致"""
            delta = 0.1
            deriv = (height(t + delta, rows / 2) - height(t - delta, rows / 2)) / (2 * delta)
            return deriv

        scan_tracker = ValueTracker(2)
        box_w, box_h = 1.4, 1.4
        # V13: 使用语义化颜色
        scanner = RoundedRectangle(width=box_w, height=box_h, corner_radius=0.08, stroke_width=4, stroke_color=PALETTE["MATH_FUNC"])
        scanner.rotate(PI / 2, axis=RIGHT)

        laser = Line(ORIGIN, ORIGIN + DOWN * 1.2, color=PALETTE["MATH_FUNC"], stroke_width=3)
        laser.rotate(PI / 2, axis=RIGHT)
        scanner_group = VGroup(scanner, laser)

        def update_scanner(mob):
            u = scan_tracker.get_value()
            v = rows / 2
            z = height(u, v) * 2.2
            pos = axes3d.c2p(u, v, z + 0.8)
            mob.move_to(pos)
            ground = axes3d.c2p(u, v, z)
            mob[1].put_start_and_end_on(pos, ground)
            # V13: 使用统一的get_scan_data函数，确保数据同步
            deriv = get_scan_data(u)
            # V13: 使用语义化颜色
            T_min, T_max = 0.02, 0.4
            alpha = np.clip((abs(deriv) - T_min) / (T_max - T_min), 0, 1)
            new_color = interpolate_color(ManimColor(PALETTE["MATH_FUNC"]), ManimColor(PALETTE["MATH_ERROR"]), alpha)
            mob[0].set_color(new_color)
            mob[1].set_color(new_color)

        scanner_group.add_updater(update_scanner)
        self.add(scanner_group)

        # HUD 示波器
        hud_axes = Axes(
            x_range=[0, cols, 5],
            y_range=[-1.5, 1.5, 0.5],
            x_length=4.5,
            y_length=2.2,
            axis_config={"include_tip": False, "stroke_opacity": 0.8, "stroke_width": 1.5, "stroke_color": GREY_B, "font_size": 16},
        )
        hud_bg = Rectangle(width=5.2, height=3.0, color=BLACK, fill_opacity=0.65, stroke_width=0)
        hud_group = VGroup(hud_bg, hud_axes).to_corner(DR, buff=0.5)
        
        def deriv_func(x):
            return get_scan_data(x)

        graph = always_redraw(lambda: hud_axes.plot(
            deriv_func,
            x_range=[0, scan_tracker.get_value() + 0.001],
            color=scanner_group[0].get_color(),
            stroke_width=3,
        ))
        dot = always_redraw(lambda: Dot(
            hud_axes.c2p(scan_tracker.get_value(), deriv_func(scan_tracker.get_value())),
            color=WHITE,
            radius=0.06,
        ))
        self.add_fixed_in_frame_mobjects(hud_group, graph, dot)

        self.play(scan_tracker.animate.set_value(cols - 2), run_time=12.0, rate_func=smooth)
        slow_wait(self, 3.0)  # V14 节奏控制：所有等待时间使用 slow_wait

        scanner_group.remove_updater(update_scanner)
        # V13: 使用生命周期管理
        self.add_to_math_group(scanner_group, hud_group, graph, dot)
        hud.clear()
        self.clear_scene(fade_out=True, run_time=1.2)
        slow_wait(self, 0.6)  # V14 节奏控制：所有等待时间使用 slow_wait


# =============================================================================
# Scene 4.6：真实图像处理（灰度→SobelX/Y→幅值→阈值）
# =============================================================================
class Scene4_6RealImage(BaseScene):
    """
    真实图像流程（V14 叙事重构版）
    V14 改进内容：
    - 节奏控制：慢动作展示
    - 极简主义：降低背景饱和度
    """
    """
    真实图像处理链路示意（不加载外部文件，用合成矩阵代替）：
    原图 -> 灰度 -> Sobel X/Y -> 梯度幅值 -> 阈值
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("Real pipeline: original image → grayscale → Sobel X/Y → gradient magnitude → threshold.", wait_after=1.2)

        # 合成一张 10x10 “城市”方块图
        size = 10
        cell = 0.22
        base = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                # 背景渐变
                base[i, j] = 0.2 + 0.6 * j / (size - 1)
        # 建筑块
        for i in range(2, 8):
            for j in range(2, 8):
                if (i in [2, 7]) or (j in [2, 7]):
                    base[i, j] = 0.9
                elif (i % 2 == 0 and j % 2 == 0):
                    base[i, j] = 0.65
                else:
                    base[i, j] = 0.4
        base = np.clip(base, 0, 1)

        def make_image(vals, box_color=GREY_B):
            g = VGroup()
            h, w = vals.shape
            for i in range(h):
                for j in range(w):
                    sq = Square(side_length=cell, stroke_width=0, fill_opacity=1)
                    sq.set_fill(interpolate_color(BLACK, WHITE, vals[i, j]))
                    sq.move_to(RIGHT * (j - w / 2) * cell + UP * (h / 2 - i) * cell)
                    g.add(sq)
            box = SurroundingRectangle(g, color=box_color, stroke_width=2)
            return VGroup(box, g)

        raw_img = make_image(base)
        gray_img = raw_img.copy()  # 已是灰度示意

        # Sobel X/Y
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

        def convolve(vals, kernel):
            h, w = vals.shape
            pad = kernel.shape[0] // 2
            padded = np.pad(vals, pad, mode="edge")
            out = np.zeros_like(vals)
            for i in range(h):
                for j in range(w):
                    patch = padded[i:i + kernel.shape[0], j:j + kernel.shape[1]]
                    out[i, j] = np.sum(patch * kernel)
            m = np.max(np.abs(out)) or 1.0
            out = (out / m + 1) / 2
            return out

        gx = convolve(base, sobel_x)
        gy = convolve(base, sobel_y)
        grad_mag = np.sqrt((gx - 0.5) ** 2 + (gy - 0.5) ** 2)
        if np.max(grad_mag) > 0:
            grad_mag /= np.max(grad_mag)

        # V13: 使用语义化颜色
        gx_img = make_image(gx, box_color=PALETTE["MATH_ERROR"])
        gy_img = make_image(gy, box_color=PALETTE["MATH_ERROR"])
        mag_img = make_image(grad_mag, box_color=PALETTE["MATH_FUNC"])

        # 阈值可调
        thresh = ValueTracker(0.35)
        # V13: 使用语义化颜色
        def make_thresholded():
            vals = (grad_mag > thresh.get_value()).astype(float)
            return make_image(vals, box_color=PALETTE["HIGHLIGHT"])
        edge_img = always_redraw(make_thresholded)

        # 布局：原图/灰度/SobelX/Y/幅值/阈值 六格
        row1 = VGroup(
            VGroup(raw_img, safer_text("Original", font_size=20, color=WHITE).next_to(raw_img, DOWN, buff=0.15)),
            VGroup(gray_img, safer_text("Grayscale", font_size=20, color=WHITE).next_to(gray_img, DOWN, buff=0.15)),
            VGroup(gx_img, safer_text("Sobel X", font_size=20, color=PALETTE["MATH_ERROR"]).next_to(gx_img, DOWN, buff=0.15))
        ).arrange(RIGHT, buff=0.5)
        row2 = VGroup(
            VGroup(gy_img, safer_text("Sobel Y", font_size=20, color=PALETTE["MATH_ERROR"]).next_to(gy_img, DOWN, buff=0.15)),
            VGroup(mag_img, safer_text("|G|", font_size=20, color=PALETTE["MATH_FUNC"]).next_to(mag_img, DOWN, buff=0.15)),
            VGroup(edge_img, safer_text("Threshold Edges", font_size=20, color=PALETTE["HIGHLIGHT"]).next_to(edge_img, DOWN, buff=0.15))
        ).arrange(RIGHT, buff=0.5)
        grid = VGroup(row1, row2).arrange(DOWN, buff=0.6).scale(0.9).move_to(ORIGIN)

        self.play(FadeIn(grid, shift=UP * 0.2), run_time=1.8)
        slow_wait(self, 1.0)  # V14 节奏控制：所有等待时间使用 slow_wait

        hud.show("Adjust the threshold: too low = noise, too high = broken edges.", wait_after=1.2)
        self.play(thresh.animate.set_value(0.15), run_time=1.6)
        slow_wait(self, 0.4)  # V14 节奏控制：所有等待时间使用 slow_wait
        self.play(thresh.animate.set_value(0.55), run_time=1.6)
        slow_wait(self, 0.4)  # V14 节奏控制：所有等待时间使用 slow_wait
        self.play(thresh.animate.set_value(0.35), run_time=1.0)
        slow_wait(self, 0.6)  # V14 节奏控制：所有等待时间使用 slow_wait

        # V13: 使用生命周期管理
        self.add_to_math_group(grid)
        hud.clear()
        self.clear_scene(fade_out=True, run_time=1.0)
        slow_wait(self, 0.4)  # V14 节奏控制：所有等待时间使用 slow_wait


# =============================================================================
# Scene 4.5：应用对照（道路 + 文本）
# =============================================================================
class Scene4_5Applications(BaseScene):
    """
    实际应用（V14 叙事重构版）
    V14 改进内容：
    - 节奏控制：慢动作展示
    - 极简主义：降低背景饱和度
    """
    """第 4.5 部分：简单的应用对照示例"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("Look at real-world images: original on the left, edge extraction on the right.", wait_after=1.6)

        examples = [
            self._make_road_pair(),
            self._make_text_pair(),
            self._make_face_pair(),
            self._make_building_pair(),
        ]
        rows = []
        for raw, edge in examples:
            rows.append(VGroup(raw, edge).arrange(RIGHT, buff=0.6))
        grid = VGroup(*rows).arrange(DOWN, buff=0.7).move_to(ORIGIN)

        self.play(FadeIn(grid, shift=UP * 0.2), run_time=1.6)
        slow_wait(self, 2.4)  # V14 节奏控制：所有等待时间使用 slow_wait

        hud.show("Sobel highlights structure: road boundaries, strokes, facial contours, building windows.", wait_after=2.0)
        slow_wait(self, 1.6)  # V14 节奏控制：所有等待时间使用 slow_wait

        # 阈值/对比度影响示意（建筑例子三档阈值）
        thresh_triplet = self._make_threshold_triplet()
        thresh_triplet.to_edge(DOWN, buff=0.4)
        thresh_title = safer_text("Threshold Impact: Low/Medium/High", font_size=24, color=WHITE).next_to(thresh_triplet, UP, buff=0.25)
        self.play(FadeIn(VGroup(thresh_triplet, thresh_title), shift=UP * 0.2), run_time=1.0)
        slow_wait(self, 1.4)  # V14 节奏控制：所有等待时间使用 slow_wait

        # V13: 使用生命周期管理
        self.add_to_math_group(grid, thresh_triplet, thresh_title)
        hud.clear()
        self.clear_scene(fade_out=True, run_time=1.0)
        slow_wait(self, 0.6)  # V14 节奏控制：所有等待时间使用 slow_wait

    def _make_road_pair(self):
        size = 10
        raw = VGroup()
        for i in range(size):
            for j in range(size):
                dist = abs(j - size / 2)
                if dist < 2:
                    intensity = 0.6
                elif dist < 3:
                    intensity = 1.0
                else:
                    intensity = 0.2
                sq = Square(side_length=0.18, stroke_width=0, fill_opacity=1)
                sq.set_fill(interpolate_color(BLACK, WHITE, intensity))
                sq.move_to(RIGHT * (j - size / 2) * 0.18 + UP * (size / 2 - i) * 0.18)
                raw.add(sq)
        raw_box = SurroundingRectangle(raw, color=GREY_B, stroke_width=2)
        raw_group = VGroup(raw_box, raw)
        raw_label = safer_text("Road Original", font_size=20).next_to(raw_group, DOWN, buff=0.25)
        raw_all = VGroup(raw_group, raw_label).arrange(DOWN, buff=0.2)

        edge = VGroup()
        for i in range(size):
            for j in range(size):
                dist = abs(j - size / 2)
                if 2.4 < dist < 3.2:
                    # V13: 使用语义化颜色
                    color = PALETTE["EDGE"]
                    op = 0.95
                else:
                    color = BLACK
                    op = 0.1
                sq = Square(side_length=0.18, stroke_width=0, fill_opacity=op)
                sq.set_fill(color)
                sq.move_to(RIGHT * (j - size / 2) * 0.18 + UP * (size / 2 - i) * 0.18)
                edge.add(sq)
        edge_box = SurroundingRectangle(edge, color=GREY_B, stroke_width=2)
        edge_group = VGroup(edge_box, edge)
        edge_label = safer_text("Road Edges", font_size=20).next_to(edge_group, DOWN, buff=0.25)
        edge_all = VGroup(edge_group, edge_label).arrange(DOWN, buff=0.2)

        return raw_all, edge_all

    def _make_text_pair(self):
        size = 8
        raw = VGroup()
        for i in range(size):
            for j in range(size):
                if 2 <= j <= 5 and (i in [1, 4, 6] or j in [2, 5]):
                    intensity = 0.9
                else:
                    intensity = 0.15
                sq = Square(side_length=0.2, stroke_width=0, fill_opacity=1)
                sq.set_fill(interpolate_color(BLACK, WHITE, intensity))
                sq.move_to(RIGHT * (j - size / 2) * 0.2 + UP * (size / 2 - i) * 0.2)
                raw.add(sq)
        raw_box = SurroundingRectangle(raw, color=GREY_B, stroke_width=2)
        raw_group = VGroup(raw_box, raw)
        raw_label = safer_text("Text Original", font_size=20).next_to(raw_group, DOWN, buff=0.25)
        raw_all = VGroup(raw_group, raw_label).arrange(DOWN, buff=0.2)

        edge = VGroup()
        for i in range(size):
            for j in range(size):
                on_edge = (
                    (2 <= j <= 5 and i in [1, 6]) or
                    (j in [2, 5] and 1 <= i <= 6) or
                    (2 <= j <= 5 and i in [4])
                )
                if on_edge:
                    # V13: 使用语义化颜色
                    color = PALETTE["EDGE"]
                    op = 0.95
                else:
                    color = BLACK
                    op = 0.1
                sq = Square(side_length=0.2, stroke_width=0, fill_opacity=op)
                sq.set_fill(color)
                sq.move_to(RIGHT * (j - size / 2) * 0.2 + UP * (size / 2 - i) * 0.2)
                edge.add(sq)
        edge_box = SurroundingRectangle(edge, color=GREY_B, stroke_width=2)
        edge_group = VGroup(edge_box, edge)
        edge_label = safer_text("Text Edges", font_size=20).next_to(edge_group, DOWN, buff=0.25)
        edge_all = VGroup(edge_group, edge_label).arrange(DOWN, buff=0.2)

        return raw_all, edge_all

    def _make_face_pair(self):
        size = 8
        raw = VGroup()
        rng = np.random.default_rng(7)
        for i in range(size):
            for j in range(size):
                intensity = 0.25 + 0.15 * rng.normal()
                # 眼睛
                if (i == 2 and j in [2, 5]):
                    intensity = 0.95
                # 嘴
                if i == 5 and 2 <= j <= 5:
                    intensity = 0.8
                # 轮廓
                if i in [1, 6] or j in [1, 6]:
                    intensity = max(intensity, 0.6)
                sq = Square(side_length=0.2, stroke_width=0, fill_opacity=1)
                sq.set_fill(interpolate_color(BLACK, WHITE, np.clip(intensity, 0, 1)))
                sq.move_to(RIGHT * (j - size / 2) * 0.2 + UP * (size / 2 - i) * 0.2)
                raw.add(sq)
        raw_box = SurroundingRectangle(raw, color=GREY_B, stroke_width=2)
        raw_group = VGroup(raw_box, raw)
        raw_label = safer_text("Face Original", font_size=20).next_to(raw_group, DOWN, buff=0.25)
        raw_all = VGroup(raw_group, raw_label).arrange(DOWN, buff=0.2)

        edge = VGroup()
        for i in range(size):
            for j in range(size):
                on_edge = (
                    (i in [1, 6] or j in [1, 6]) or
                    (i == 2 and j in [2, 5]) or
                    (i == 5 and 2 <= j <= 5)
                )
                # V13: 使用语义化颜色
                color = PALETTE["EDGE"] if on_edge else BLACK
                op = 0.95 if on_edge else 0.08
                sq = Square(side_length=0.2, stroke_width=0, fill_opacity=op)
                sq.set_fill(color)
                sq.move_to(RIGHT * (j - size / 2) * 0.2 + UP * (size / 2 - i) * 0.2)
                edge.add(sq)
        edge_box = SurroundingRectangle(edge, color=GREY_B, stroke_width=2)
        edge_group = VGroup(edge_box, edge)
        edge_label = safer_text("Face Edges", font_size=20).next_to(edge_group, DOWN, buff=0.25)
        edge_all = VGroup(edge_group, edge_label).arrange(DOWN, buff=0.2)
        return raw_all, edge_all

    def _make_building_pair(self):
        size = 8
        intensities = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                # 外框
                if i in [1, size-2] or j in [1, size-2]:
                    intensities[i, j] = 0.9
                # 窗
                elif (i % 2 == 0) and (j % 2 == 0):
                    intensities[i, j] = 0.7
                else:
                    intensities[i, j] = 0.2
        raw = VGroup()
        cell = 0.2
        for i in range(size):
            for j in range(size):
                sq = Square(side_length=cell, stroke_width=0, fill_opacity=1)
                sq.set_fill(interpolate_color(BLACK, WHITE, intensities[i, j]))
                sq.move_to(RIGHT * (j - size / 2) * cell + UP * (size / 2 - i) * cell)
                raw.add(sq)
        raw_box = SurroundingRectangle(raw, color=GREY_B, stroke_width=2)
        raw_group = VGroup(raw_box, raw)
        raw_label = safer_text("Building Original", font_size=20).next_to(raw_group, DOWN, buff=0.25)
        raw_all = VGroup(raw_group, raw_label).arrange(DOWN, buff=0.2)

        edge = VGroup()
        for i in range(size):
            for j in range(size):
                if i in [1, size-2] or j in [1, size-2]:
                    on_edge = True
                elif (i % 2 == 0 and j % 2 == 0):
                    on_edge = True
                else:
                    on_edge = False
                # V13: 使用语义化颜色
                color = PALETTE["EDGE"] if on_edge else BLACK
                op = 0.95 if on_edge else 0.08
                sq = Square(side_length=cell, stroke_width=0, fill_opacity=op)
                sq.set_fill(color)
                sq.move_to(RIGHT * (j - size / 2) * cell + UP * (size / 2 - i) * cell)
                edge.add(sq)
        edge_box = SurroundingRectangle(edge, color=GREY_B, stroke_width=2)
        edge_group = VGroup(edge_box, edge)
        edge_label = safer_text("Building Edges", font_size=20).next_to(edge_group, DOWN, buff=0.25)
        edge_all = VGroup(edge_group, edge_label).arrange(DOWN, buff=0.2)
        # 额外返回 intensities 供阈值演示
        edge_all.intensities = intensities
        return raw_all, edge_all

    def _make_threshold_triplet(self):
        # 使用建筑 intensities 做三档阈值效果
        _, edge_all = self._make_building_pair()
        intensities = edge_all.intensities
        thresholds = [0.2, 0.45, 0.7]
        labels = ["Low Threshold", "Medium Threshold", "High Threshold"]
        cell = 0.18
        triplets = VGroup()
        size = intensities.shape[0]
        for t, name in zip(thresholds, labels):
            edge = VGroup()
            for i in range(size):
                for j in range(size):
                    # 简化：若周围强度差超过阈值则为边缘
                    val = intensities[i, j]
                    neigh = []
                    for di, dj in [(1,0),(-1,0),(0,1),(0,-1)]:
                        ni, nj = i+di, j+dj
                        if 0 <= ni < size and 0 <= nj < size:
                            neigh.append(intensities[ni, nj])
                    diff = max(abs(val - n) for n in neigh) if neigh else 0
                    on_edge = diff > t
                    # V13: 使用语义化颜色
                    color = PALETTE["EDGE"] if on_edge else BLACK
                    op = 0.9 if on_edge else 0.05
                    sq = Square(side_length=cell, stroke_width=0, fill_opacity=op)
                    sq.set_fill(color)
                    sq.move_to(RIGHT * (j - size / 2) * cell + UP * (size / 2 - i) * cell)
                    edge.add(sq)
            edge_box = SurroundingRectangle(edge, color=GREY_B, stroke_width=1.8)
            edge_group = VGroup(edge_box, edge)
            edge_label = safer_text(name, font_size=18, color=WHITE).next_to(edge_group, DOWN, buff=0.2)
            triplets.add(VGroup(edge_group, edge_label).arrange(DOWN, buff=0.15))
        triplets.arrange(RIGHT, buff=0.5)
        return triplets


# =============================================================================
# Scene 5：总结与片尾
# =============================================================================
class Scene5Outro(BaseScene):
    """
    结语（V14 叙事重构版）
    V14 改进内容：
    - 叙事重构：升华主题
    - 节奏控制：慢动作展示
    - 极简主义：静态展示
    """
    """第六部分：回顾与片尾"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("From continuous derivatives to discrete differences, from noise to contours—what have we seen?", wait_after=2.0)

        step1 = safer_text("Continuous → Discrete", font_size=26, color=WHITE)
        step2 = MathTex(r"f'(x) \approx \dfrac{f(x+1)-f(x-1)}{2}", font_size=32, color=WHITE)
        # V13: 使用语义化颜色
        step3 = IntegerMatrix([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]).scale(0.6).set_color_by_gradient(PALETTE["MATH_ERROR"], PALETTE["HIGHLIGHT"], PALETTE["MATH_FUNC"])
        step4 = safer_text("Edge Detection / Structure Extraction", font_size=26, color=WHITE)

        recap = VGroup(step1, step2, step3, step4).arrange(DOWN, buff=0.6, aligned_edge=LEFT).to_edge(LEFT, buff=0.8)
        # V13: 添加到数学组（在定义之后）
        self.add_to_math_group(recap)
        self.play(FadeIn(recap, shift=UP * 0.2), run_time=1.8)
        slow_wait(self, 3.0)  # V14 节奏控制：所有等待时间使用 slow_wait

        hud.show("Theory meets practice: mathematical ideal Δx→0, engineering reality pixel=1.", wait_after=2.0)
        slow_wait(self, 2.0)  # V14 节奏控制：所有等待时间使用 slow_wait

        # V13: 使用语义化颜色
        philosophy = safer_text("Let machines find the clearest boundaries in a noisy world.", font_size=32, color=PALETTE["HIGHLIGHT"])
        # V14 增强：确保哲学文本在安全区域内
        ensure_safe_bounds(philosophy)
        phil_bg = BackgroundRectangle(philosophy, fill_opacity=0.7, color=BLACK, buff=0.3, corner_radius=0.08)
        phil_group = VGroup(phil_bg, philosophy).move_to(ORIGIN)
        # V14 增强：确保整个哲学组在安全区域内
        ensure_safe_bounds(phil_group)
        # V13: 添加到数学组（在定义之后）
        self.add_to_math_group(phil_group)
        self.play(
            Succession(
                phil_group.animate.scale(1.1).set_opacity(0),
                phil_group.animate.scale(1.0).set_opacity(1),
                run_time=0.8,
                rate_func=rate_functions.ease_out_back,
            )
        )
        slow_wait(self, 3.0)  # V14 节奏控制：所有等待时间使用 slow_wait

        # 修复：强制演职员表y > -2.0，避免与字幕重叠
        # V13: 使用语义化颜色
        credits = VGroup(
            safer_text("Project Sobel", font_size=30, color=PALETTE["MATH_FUNC"]),
            safer_text("Visuals: Manim Community Edition", font_size=20, color=GREY_B),
            safer_text("Code: Python 3.10 + Manim", font_size=20, color=GREY_B),
            safer_text("Original Statement: All animations in this video are programmatically generated. Source materials are listed in the documentation.", font_size=22, color=WHITE),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        # 确保y坐标 > -2.0，避免进入字幕禁飞区
        credits.move_to(ORIGIN + DOWN * 1.5).shift(RIGHT * 0.5)
        self.play(LaggedStart(*[FadeIn(line, shift=UP * 0.2) for line in credits], lag_ratio=0.2, run_time=2.2))
        slow_wait(self, 4.0)  # V14 节奏控制：所有等待时间使用 slow_wait

        # V13: 使用生命周期管理
        self.add_to_math_group(credits)
        hud.clear()
        self.clear_scene(fade_out=True, run_time=1.6)
        slow_wait(self, 0.8)  # V14 节奏控制：所有等待时间使用 slow_wait


# =============================================================================
# 渲染指令说明
# =============================================================================
"""
V13 版本渲染命令

快速预览（低质量，用于调试）：
    manim -pql sobel_v13_full.py Scene0Intro
    manim -pql sobel_v13_full.py Scene1Discrete
    manim -pql sobel_v13_full.py Scene1_5Limits
    manim -pql sobel_v13_full.py Scene2Taylor
    manim -pql sobel_v13_full.py Scene2_5Comparison
    manim -pql sobel_v13_full.py Scene3SobelConstruct
    manim -pql sobel_v13_full.py Scene3_5Convolution
    manim -pql sobel_v13_full.py Scene4_2MultiScale
    manim -pql sobel_v13_full.py Scene4Vision
    manim -pql sobel_v13_full.py Scene4_6RealImage
    manim -pql sobel_v13_full.py Scene4_5Applications
    manim -pql sobel_v13_full.py Scene5Outro

完整视频（低质量预览）：
    manim -pql sobel_v13_full.py FullSobelVideo

高质量渲染（最终输出）：
    manim -pqh sobel_v13_full.py Scene0Intro
    manim -pqh sobel_v13_full.py FullSobelVideo

参数说明：
    -p : 渲染后自动预览
    -q : 质量等级
        l = low (480p, 15fps) - 快速调试
        m = medium (720p, 30fps) - 平衡选择
        h = high (1080p, 60fps) - 最终输出
        k = 4K (2160p, 60fps) - 超高质量（渲染时间很长）

注意事项：
    1. 首次渲染可能需要较长时间（编译 LaTeX、生成缓存等）
    2. 完整视频渲染时间取决于场景数量和复杂度
    3. 建议先用 -pql 测试单个场景，确认无误后再渲染完整视频
    4. 如果遇到 LaTeX 错误，检查是否在 MathTex 中使用了中文
    5. 如果遇到 AttributeError，检查类继承关系是否正确
"""

if __name__ == "__main__":
    pass