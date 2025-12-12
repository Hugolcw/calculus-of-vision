from manim import *
import numpy as np

# 导入 V12 统一工具模块
from utils import (
    SubtitleManager,
    safer_text,
    make_highlight_rect,
    default_axis_config,
    apply_wave_effect,
    get_quality_config,
    COLOR_CONTINUOUS,
    COLOR_DISCRETE,
    COLOR_DIFF,
    COLOR_SMOOTH,
    BG_COLOR,
)


# =============================================================================
# Scene 0：开场谜题（V12 扩充版）
# =============================================================================
class Scene0Intro(Scene):
    """
    第一部分：开场谜题 + 设问
    V12 扩充内容：
    - 动态噪声生成过程（8s）
    - 边缘检测预览（5s）
    - 悬念过渡（2.9s）
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)  # 使用统一字幕管理器

        # ====================================================================
        # Part 1: 清晰图展示（约3秒）
        # ====================================================================
        clean = self._make_gradient_card()
        clean.scale(0.9)
        clean.move_to(ORIGIN)
        
        title_clean = safer_text("清晰图", font_size=26, color=WHITE).next_to(clean, DOWN, buff=0.25)
        clean_group = VGroup(clean, title_clean)

        self.play(FadeIn(clean_group, shift=UP * 0.3), run_time=1.2)
        self.wait(0.8)
        
        hud.show("在连续世界里，图像是平滑的渐变。", wait_after=1.0)

        # ====================================================================
        # Part 2: 动态噪声生成过程（+8s）- V12 扩充内容
        # ====================================================================
        hud.show("但在数字世界，噪声无处不在。", wait_after=0.8)
        
        # 创建噪声图框架
        noisy_card = self._make_noisy_card_frame()
        noisy_card.scale(0.9)
        noisy_card.move_to(ORIGIN)
        title_noisy = safer_text("噪声图", font_size=26, color=WHITE).next_to(noisy_card, DOWN, buff=0.25)
        noisy_group = VGroup(noisy_card, title_noisy)
        
        # 与清晰图同位置叠放噪声框架（不立刻移除清晰图，作为“被污染”的背景）
        noisy_group.move_to(clean_group)
        self.play(FadeIn(noisy_group, shift=UP * 0.1), run_time=0.8)
        self.wait(0.3)
        
        # 动态生成噪声点（真正的“污染”过程：清晰图逐渐变暗，噪声逐渐覆盖）
        rng = np.random.default_rng(42)
        noise_dots = VGroup()
        num_noise_points = 160
        
        # 创建噪声点列表（预先生成所有点，但逐个显示）
        noise_positions = []
        for _ in range(num_noise_points):
            x = rng.uniform(-2.6, 2.6)
            y = rng.uniform(-1.4, 1.4)
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

        self.play(
            LaggedStart(
                *animations,
                lag_ratio=0.12,
                run_time=2.8,
                rate_func=smooth
            )
        )
        # 结束时，清晰图保留淡淡的“幽灵”感，噪声完全覆盖
        self.wait(0.8)
        
        hud.show("噪声掩盖了图像的结构。", wait_after=1.2)

        # ====================================================================
        # Part 3: 边缘检测预览（+5s）- V12 扩充内容
        # ====================================================================
        hud.show("但数学可以帮我们从噪声中提取结构。", wait_after=1.0)
        
        # 创建边缘检测预览（基于渐变图的 Sobel 近似）：从噪声中“浮现”真实感更强的边缘
        edge_preview = self._create_edge_preview_from_gradient()
        edge_preview.set_opacity(0)  # 初始不可见
        
        # 从噪声中逐渐“提取”边缘：线条渐显、线宽渐增
        for line in edge_preview:
            line.set_stroke(width=0, opacity=0)
        self.play(
            LaggedStart(
                *[
                    line.animate.set_opacity(0.8).set_stroke(width=line.stroke_width or 3.5)
                    for line in edge_preview
                ],
                lag_ratio=0.12,
                run_time=3.0,
                rate_func=smooth
            )
        )
        self.wait(0.6)
        
        # 高亮边缘检测结果，突出“提取”成功
        edge_highlight = make_highlight_rect(
            edge_preview,
            color=COLOR_DIFF,
            buff=0.2,
            corner_radius=0.1,
            stroke_width=3
        )
        self.play(Create(edge_highlight), run_time=0.6)
        self.wait(0.5)
        
        hud.show("这就是边缘检测的力量。", wait_after=0.8)
        
        # 保留边缘结果用于后续对比，不立即淡出
        edge_result = edge_preview.copy()
        edge_result_highlight = edge_highlight.copy()

        # ====================================================================
        # Part 4: 问题提出（约4秒）
        # ====================================================================
        # 将清晰图、噪声图、边缘结果三屏并排展示，形成“污染→提取”完整对比
        clean_final = self._make_gradient_card()
        noisy_final = self._make_noisy_card()
        edge_final = edge_result.copy()
        edge_final_highlight = edge_result_highlight.copy()
        pair = VGroup(clean_final, noisy_final, edge_final).arrange(RIGHT, buff=1.0).scale(0.9)
        title_clean_final = safer_text("清晰图", font_size=26, color=WHITE).next_to(clean_final, DOWN, buff=0.25)
        title_noisy_final = safer_text("噪声图", font_size=26, color=WHITE).next_to(noisy_final, DOWN, buff=0.25)
        title_edge_final = safer_text("提取的边缘", font_size=26, color=COLOR_DIFF).next_to(edge_final, DOWN, buff=0.25)
        pair_group = VGroup(pair, title_clean_final, title_noisy_final, title_edge_final, edge_final_highlight)
        
        # 替换当前画面，保留噪声与边缘结果用于对比
        self.play(
            ReplacementTransform(VGroup(noisy_group, noise_dots, edge_preview, edge_highlight), pair_group),
            run_time=1.2
        )
        
        hud.show("在噪声里，仅凭数学，如何找到清晰的轮廓？", wait_after=1.5)

        # ====================================================================
        # Part 5: 悬念过渡（+2.9s）- V12 扩充内容
        # ====================================================================
        # 居中问题文本（定格有画面承载）
        question = safer_text("数学能让机器看见吗？", font_size=34, color=YELLOW_C)
        question_bg = BackgroundRectangle(
            question,
            fill_opacity=0.7,
            color=BLACK,
            buff=0.28,
            corner_radius=0.08
        )
        question_group = VGroup(question_bg, question).move_to(ORIGIN + UP * 1.6)
        self.add_fixed_in_frame_mobjects(question_group)
        self.play(FadeIn(question_group, scale=0.9), run_time=0.8)
        self.wait(0.8)
        
        # 思考视觉元素（粒子效果）
        # 总时长约 2.9 秒（符合 V12 方案要求）
        thinking_particles = self._create_thinking_particles(question_group)
        self.play(
            LaggedStart(
                *[FadeIn(particle, scale=0.3) for particle in thinking_particles],
                lag_ratio=0.08,
                run_time=1.2
            )
        )
        self.wait(0.7)
        
        # 粒子逐渐消失
        self.play(
            LaggedStart(
                *[FadeOut(particle, shift=UP * 0.3) for particle in thinking_particles],
                lag_ratio=0.06,
                run_time=1.0
            )
        )
        self.wait(0.5)
        
        self.play(FadeOut(question_group, shift=UP * 0.2), run_time=0.6)

        # ====================================================================
        # Part 6: 收尾
        # ====================================================================
        hud.clear()
        self.play(FadeOut(pair_group), run_time=0.8)
        self.wait(0.4)

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
                line = Line(
                    start=np.array([x, y - dy * 0.25, 0]),
                    end=np.array([x, y + dy * 0.25, 0]),
                    color=COLOR_DIFF,
                    stroke_width=2.5,
                    stroke_opacity=0.3 + 0.7 * strength,  # 强度映射到透明度
                )
                edge_lines.add(line)

        return edge_lines

    def _create_thinking_particles(self, question_group):
        """
        创建思考视觉元素（粒子效果）
        在问题文本周围创建思考的粒子，形成"思考"的视觉氛围
        """
        particles = VGroup()
        num_particles = 16
        
        # 在问题文本周围创建粒子（圆形分布）
        center = question_group.get_center()
        radius = 1.6
        
        # 主要粒子：均匀分布在圆周上
        for i in range(num_particles):
            angle = 2 * PI * i / num_particles
            offset = radius * (np.array([np.cos(angle), np.sin(angle), 0]))
            pos = center + offset
            
            # 创建小圆点粒子，大小略有变化
            size_variation = 0.02 * np.sin(i * 0.5)  # 轻微大小变化
            particle = Dot(
                point=pos,
                radius=0.08 + size_variation,
                color=YELLOW_C,
                fill_opacity=0.6 + 0.2 * np.sin(i)  # 透明度变化
            )
            particles.add(particle)
        
        # 添加一些随机位置的额外粒子（增加动感和真实感）
        rng = np.random.default_rng(123)
        for _ in range(10):
            angle = rng.uniform(0, 2 * PI)
            r = rng.uniform(1.3, 1.9)
            offset = r * (np.array([np.cos(angle), np.sin(angle), 0]))
            pos = center + offset
            
            particle = Dot(
                point=pos,
                radius=0.05 + rng.uniform(0, 0.03),
                color=YELLOW_C,
                fill_opacity=rng.uniform(0.3, 0.6)
            )
            particles.add(particle)
        
        # 添加一些问号形状的粒子（强化"思考"主题）
        question_particles = VGroup()
        for i in range(3):
            angle = 2 * PI * i / 3 + PI / 6
            offset = 1.8 * (np.array([np.cos(angle), np.sin(angle), 0]))
            pos = center + offset
            
            # 创建小问号
            q_mark = MathTex("?", font_size=20, color=YELLOW_C).move_to(pos)
            question_particles.add(q_mark)
        
        particles.add(question_particles)
        
        return particles


# 运行示例：
# manim -pql sobel_v12_full.py Scene0Intro
if __name__ == "__main__":
    pass


# =============================================================================
# Full video wrapper：串联各分场景（便于一次渲染）
# =============================================================================
class FullSobelVideo(ThreeDScene):
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

    def _create_thinking_particles(self, *args, **kwargs):
        return Scene0Intro._create_thinking_particles(self, *args, **kwargs)

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
# Scene 1：连续→离散（V12 扩充版）
# =============================================================================
class Scene1Discrete(Scene):
    """
    第二部分：连续→离散，失去极限，提出“如何找回导数”
    V12 扩充内容：
    - 多切点展示 + 动态切线
    - 渐进采样（5→11→21 点）
    - Δx 逐步放大（0.1 → 0.5 → 1.0），强化“失去极限”
    - 聚焦三点，对比 Δx=1 的约束，提出困境
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        # 统一坐标轴样式
        axes_config = default_axis_config(stroke_opacity=0.9, stroke_width=2, stroke_color=GREY_B)
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 5, 1],
            x_length=11,
            y_length=4.5,
            axis_config=axes_config,
            tips=False,
        )
        def f(x): return 2 + np.sin(0.5 * x) + 0.5 * np.sin(x)
        curve = axes.plot(f, x_range=[0, 10], color=COLOR_CONTINUOUS, stroke_width=4)

        # 坐标与连续曲线
        self.play(Create(axes), run_time=1.0)
        self.play(Create(curve), run_time=1.2)
        hud.show("在连续世界里，导数是切线的斜率。", wait_after=0.8)

        # 多切点展示（静态切线 3 处）
        tangent_points = [2, 5, 8]
        tangents = VGroup()
        for tx in tangent_points:
            dx = 0.01
            dy = (f(tx + dx) - f(tx - dx)) / (2 * dx)
            line = Line(
                axes.c2p(tx - 1.2, f(tx) - dy * 1.2),
                axes.c2p(tx + 1.2, f(tx) + dy * 1.2),
                color=COLOR_DIFF,
                stroke_width=3,
            )
            dot = Dot(axes.c2p(tx, f(tx)), color=COLOR_DIFF, radius=0.08)
            tangents.add(line, dot)
        self.play(LaggedStart(*[Create(t) for t in tangents], lag_ratio=0.2, run_time=1.8))
        self.wait(0.6)
        self.play(FadeOut(tangents, shift=DOWN * 0.2), run_time=0.8)

        # 动态切线演示
        t = ValueTracker(2.0)
        def tangent():
            x = t.get_value(); dx = 0.01
            dy = (f(x + dx) - f(x - dx)) / (2 * dx)
            return Line(
                axes.c2p(x - 1.5, f(x) - dy * 1.5),
                axes.c2p(x + 1.5, f(x) + dy * 1.5),
                color=COLOR_DIFF,
                stroke_width=3,
            )
        tan_line = always_redraw(tangent)
        tan_dot = always_redraw(lambda: Dot(axes.c2p(t.get_value(), f(t.get_value())), color=COLOR_DIFF, radius=0.08))
        slope_text = always_redraw(lambda: MathTex(
            rf"f'({t.get_value():.1f}) \approx {((f(t.get_value()+0.01)-f(t.get_value()-0.01))/0.02):.2f}",
            font_size=28, color=COLOR_DIFF
        ).to_edge(UR, buff=0.8))

        self.add(tan_line, tan_dot, slope_text)
        self.play(t.animate.set_value(8), run_time=2.8, rate_func=smooth)
        self.wait(0.6)

        # 渐进采样：5 → 11 → 21 点
        hud.show("但在数字世界，Δx 无法趋近 0，切线消失。", wait_after=1.0)
        samples_group = VGroup()
        piecewise_lines = []
        for n in [5, 11, 21]:
            xs = np.linspace(0, 10, n)
            stems = VGroup()
            for x in xs:
                y = f(x)
                stem = Line(axes.c2p(x, 0), axes.c2p(x, y), color=COLOR_DISCRETE, stroke_width=3)
                dot = Dot(axes.c2p(x, y), color=COLOR_DISCRETE, radius=0.07)
                stems.add(stem, dot)
            samples_group.add(stems)
            poly = VMobject(color=COLOR_DISCRETE, stroke_width=2.5, stroke_opacity=0.9)
            poly.set_points_as_corners([axes.c2p(x, f(x)) for x in xs])
            piecewise_lines.append(poly)

        # 清空切线，展示采样
        self.play(FadeOut(VGroup(tan_line, tan_dot, slope_text)), run_time=0.6)
        self.play(
            curve.animate.set_opacity(0.15),
            FadeIn(samples_group[0], lag_ratio=0.05, run_time=1.2),
            Create(piecewise_lines[0]),
            run_time=1.2,
        )
        self.wait(0.5)
        # 采样密度提升
        self.play(
            Transform(samples_group[0], samples_group[1]),
            Transform(piecewise_lines[0], piecewise_lines[1]),
            run_time=0.9
        )
        self.wait(0.3)
        self.play(
            Transform(samples_group[0], samples_group[2]),
            Transform(piecewise_lines[0], piecewise_lines[2]),
            run_time=0.9
        )
        self.wait(0.6)

        # 像素桶可视化：每个像素是长度为 1 的量化区间
        hud.show("每个像素是一个桶，函数被量化成分段的近似。", wait_after=0.8)
        pixel_bins = VGroup()
        width = axes.c2p(1, 0)[0] - axes.c2p(0, 0)[0]
        height = axes.c2p(0, 5)[1] - axes.c2p(0, 0)[1]
        for k in range(10):
            rect = Rectangle(
                width=abs(width),
                height=abs(height),
                stroke_width=1.2,
                stroke_color=COLOR_SMOOTH,
                fill_color=COLOR_SMOOTH,
                fill_opacity=0.12
            ).move_to(axes.c2p(k + 0.5, 2.5))
            pixel_bins.add(rect)
        self.play(FadeIn(pixel_bins, lag_ratio=0.1, run_time=1.0))
        self.wait(0.4)

        # Δx 逐步放大：0.1 → 0.5 → 1.0 （用水平小段表示）
        hud.show("最小步长受限，Δx 无法继续变小。", wait_after=0.8)
        focus_x = 5.0
        base_y = -0.5
        dx_values = [0.1, 0.5, 1.0]
        dx_lines = VGroup()
        dx_labels = VGroup()
        for dx in dx_values:
            line = Line(axes.c2p(focus_x - dx, base_y), axes.c2p(focus_x + dx, base_y),
                        color=COLOR_DIFF, stroke_width=3)
            label = MathTex(rf"\Delta x = {dx}", font_size=26, color=COLOR_DIFF).next_to(line, DOWN, buff=0.25)
            dx_lines.add(line); dx_labels.add(label)
        self.play(LaggedStart(*[Create(line) for line in dx_lines], lag_ratio=0.2, run_time=1.2))
        self.play(LaggedStart(*[FadeIn(lbl) for lbl in dx_labels], lag_ratio=0.2, run_time=1.0))
        self.wait(0.6)

        # 聚焦三个相邻采样点（Δx=1），高亮困境
        xs_full = np.linspace(0, 10, 21)
        mid = len(xs_full) // 2
        idxs = [mid - 1, mid, mid + 1]
        dots_focus = VGroup(*[samples_group[0][2 * i + 1] for i in idxs])
        box = make_highlight_rect(dots_focus, color=YELLOW_C, buff=0.3, corner_radius=0.12, stroke_width=3)
        dx_line_1 = Line(
            axes.c2p(xs_full[idxs[0]], base_y - 0.3),
            axes.c2p(xs_full[idxs[2]], base_y - 0.3),
            color=COLOR_DIFF, stroke_width=3,
        )
        dx_label_1 = MathTex(r"\Delta x = 1", font_size=30, color=COLOR_DIFF)
        dx_label_1_bg = BackgroundRectangle(dx_label_1, fill_opacity=0.7, color=BLACK, buff=0.2, corner_radius=0.08)
        dx_label_1_group = VGroup(dx_label_1_bg, dx_label_1).next_to(dx_line_1, DOWN, buff=0.25, aligned_edge=ORIGIN)

        hud.show("最小步长是 1 个像素，我们失去了极限。", wait_after=1.2)
        self.play(Create(box), Create(dx_line_1), FadeIn(dx_label_1_group), run_time=1.2)

        # 离散斜率（割线）对比：只能用 Δx=1 的割线近似斜率
        x_left, x_mid, x_right = xs_full[idxs[0]], xs_full[idxs[1]], xs_full[idxs[2]]
        p_left = axes.c2p(x_left, f(x_left))
        p_mid = axes.c2p(x_mid, f(x_mid))
        p_right = axes.c2p(x_right, f(x_right))
        secant = Line(p_left, p_right, color=COLOR_DIFF, stroke_width=3.2)
        secant_label = MathTex(
            rf"\frac{{\Delta y}}{{\Delta x}} \approx { (f(x_right)-f(x_left))/(x_right-x_left):.2f}",
            font_size=28, color=COLOR_DIFF
        )
        secant_label_bg = BackgroundRectangle(secant_label, fill_opacity=0.7, color=BLACK, buff=0.2, corner_radius=0.08)
        secant_label_group = VGroup(secant_label_bg, secant_label).next_to(secant, UP, buff=0.25, aligned_edge=ORIGIN)
        self.play(Create(secant), FadeIn(secant_label_group, shift=UP * 0.1), run_time=1.0)
        hud.show("只能做割线估计，无法逼近真正的切线。", wait_after=1.0)

        # 放大特写 + 提问
        question = safer_text("如何在离散像素里找回导数？", font_size=30, color=YELLOW_C)
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
        self.wait(1.6)

        # 收尾
        hud.clear()
        self.play(FadeOut(VGroup(cluster, q_group)), run_time=1.0)
        self.wait(0.3)



# =============================================================================
# Scene 1.5：极限的困境（多步 Δx 试验 + 像素约束）
# =============================================================================
class Scene1_5Limits(Scene):
    """
    补足 P0 扩充：展示 Δx 逐步变小的数值实验、像素网格约束、连续 vs 离散对比
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("尝试把 Δx 变小：能否逼近理想导数？", wait_after=0.8)

        axes_config = default_axis_config(stroke_opacity=0.9, stroke_width=2, stroke_color=GREY_B)
        axes = Axes(
            x_range=[0, 4, 0.5],
            y_range=[0, 6, 1],
            x_length=7,
            y_length=4.2,
            axis_config=axes_config,
            tips=False,
        ).to_edge(LEFT, buff=0.8)

        def f(x): return 2 + np.sin(1.2 * x) + 0.6 * np.sin(0.5 * x + 0.3)

        curve = axes.plot(f, x_range=[0, 4], color=COLOR_CONTINUOUS, stroke_width=4)
        self.play(Create(axes), Create(curve), run_time=1.2)

        # 多个 Δx 近似斜率并排显示
        dx_values = [1.0, 0.5, 0.25, 0.125]
        approx_labels = VGroup()
        slopes = []
        x0 = 2.0
        for dx in dx_values:
            s = (f(x0 + dx) - f(x0 - dx)) / (2 * dx)
            slopes.append(s)
            label = MathTex(
                rf"\Delta x = {dx:.3g},\; f'(x_0)\approx {s:.2f}",
                font_size=26,
                color=WHITE
            )
            approx_labels.add(label)

        approx_labels.arrange(DOWN, buff=0.35, aligned_edge=LEFT).to_edge(RIGHT, buff=0.8)
        x0_dot = Dot(axes.c2p(x0, f(x0)), color=COLOR_DIFF, radius=0.08)
        self.play(FadeIn(x0_dot, scale=0.8), run_time=0.6)
        self.play(FadeIn(approx_labels, shift=UP * 0.2), run_time=1.4)
        self.wait(1.0)

        hud.show("斜率在收敛，但像素世界有硬约束。", wait_after=1.2)

        # 像素网格展示 + 最小单位高亮
        grid = VGroup()
        grid_rows, grid_cols = 6, 10
        for i in range(grid_rows):
            for j in range(grid_cols):
                sq = Square(side_length=0.35, stroke_width=0.5, stroke_color=GREY_B, fill_opacity=0.05)
                sq.move_to(RIGHT * (j - grid_cols / 2) * 0.35 + UP * (grid_rows / 2 - i) * 0.35 + RIGHT * 3.2)
                grid.add(sq)
        min_cell = grid[(grid_rows // 2) * grid_cols + grid_cols // 2].copy()
        min_cell.set_fill(COLOR_DISCRETE, opacity=0.35).set_stroke(COLOR_DISCRETE, width=2.2)
        # 使用 Text/safer_text 渲染中文，避免 MathTex 的 Unicode/字体问题
        min_label = safer_text("最小像素单位", font_size=26, color=COLOR_DISCRETE).next_to(min_cell, DOWN, buff=0.25)
        self.play(FadeIn(grid, lag_ratio=0.02, run_time=1.4))
        self.play(Create(min_cell), FadeIn(min_label, shift=UP * 0.1), run_time=0.9)
        self.wait(0.6)

        hud.show("在数字图像里，Δx 最小就是 1 像素。", wait_after=1.2)

        # 连续 vs 离散对比卡片
        continuous_card = RoundedRectangle(width=4.2, height=2.2, corner_radius=0.15, stroke_width=2.2, stroke_color=GREY_B)
        discrete_card = continuous_card.copy()
        cont_label = VGroup(
            safer_text("连续世界：", font_size=26, color=COLOR_CONTINUOUS),
            MathTex(r"\Delta x \to 0", font_size=26, color=COLOR_CONTINUOUS),
        ).arrange(RIGHT, buff=0.18).move_to(continuous_card.get_center())
        disc_label = VGroup(
            safer_text("离散世界：", font_size=26, color=COLOR_DISCRETE),
            MathTex(r"\Delta x = 1", font_size=26, color=COLOR_DISCRETE),
        ).arrange(RIGHT, buff=0.18).move_to(discrete_card.get_center())
        cont_group = VGroup(continuous_card, cont_label)
        disc_group = VGroup(discrete_card, disc_label)
        pair = VGroup(cont_group, disc_group).arrange(RIGHT, buff=0.6).to_edge(DOWN, buff=0.7)
        self.play(FadeIn(pair, shift=UP * 0.2), run_time=1.0)
        self.wait(1.4)

        # 物理约束提示：对 Δx=0.125 打上限制符号
        pixel_limit = Tex(r"\text{Pixel Limit}", font_size=26, color=YELLOW_C)
        pixel_limit_bg = BackgroundRectangle(pixel_limit, fill_opacity=0.7, color=BLACK, buff=0.2, corner_radius=0.08)
        pixel_limit_group = VGroup(pixel_limit_bg, pixel_limit).next_to(approx_labels[-1], DOWN, buff=0.3)
        cross = Cross(approx_labels[-1], stroke_color=COLOR_DIFF, stroke_width=4)
        self.play(Create(cross), FadeIn(pixel_limit_group, shift=UP * 0.2), run_time=0.8)
        apply_wave_effect(self, pixel_limit_group, amplitude=0.25, run_time=0.6)

        hud.show("结论：需要新的方法，在像素里重建“导数”。", wait_after=1.5)

        self.play(FadeOut(VGroup(axes, curve, x0_dot, approx_labels, grid, min_cell, min_label, pair)), run_time=1.0)
        hud.clear()
        self.wait(0.4)

# =============================================================================
# Scene 2：泰勒抵消 → 中心差分
# =============================================================================
class Scene2Taylor(Scene):
    """
    第三部分：泰勒抵消 → 中心差分
    采用 V12 几何化修复：先展示几何误差，再做符号飞向/爆炸，最后突出中心差分
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("前向与后向的斜率各有偏差，如何消掉误差？", wait_after=0.8)

        # 坐标轴与函数（统一样式）
        axes_config = default_axis_config(stroke_opacity=0.9, stroke_width=2, stroke_color=GREY_B)
        axes = Axes(
            x_range=[-1, 3, 1],
            y_range=[-1, 3, 1],
            x_length=6,
            y_length=3.5,
            axis_config=axes_config,
            tips=False,
        ).to_edge(LEFT, buff=0.8)

        def g(x): return 1 + 0.6 * x + 0.4 * x**2

        graph = axes.plot(g, x_range=[-0.8, 2.5], color=COLOR_CONTINUOUS, stroke_width=4)
        self.play(Create(axes), Create(graph), run_time=1.2)
        self.wait(0.3)

        # 前向/后向斜率标注
        x0 = 1.0
        dx = 1.0
        y0 = g(x0)
        forward_pt = axes.c2p(x0 + dx, g(x0 + dx))
        backward_pt = axes.c2p(x0 - dx, g(x0 - dx))
        center_pt = axes.c2p(x0, y0)

        forward_line = Line(center_pt, forward_pt, color=COLOR_DIFF, stroke_width=3)
        backward_line = Line(center_pt, backward_pt, color=COLOR_DIFF, stroke_width=3)

        fwd_label = MathTex("f'(x)_{+}", font_size=28, color=COLOR_DIFF).next_to(forward_line, UP, buff=0.2)
        bwd_label = MathTex("f'(x)_{-}", font_size=28, color=COLOR_DIFF).next_to(backward_line, DOWN, buff=0.2)

        self.play(Create(forward_line), Write(fwd_label), run_time=1.0)
        self.play(Create(backward_line), Write(bwd_label), run_time=1.0)
        self.wait(0.5)

        hud.show("前向与后向各有系统误差：奇偶阶项混在一起。", wait_after=1.0)

        # --------------------------------------------------------------------
        # 几何误差向量（V12 修复核心）
        # --------------------------------------------------------------------
        g_prime_x0 = 0.6 + 0.8 * x0
        linear_approx_forward = y0 + g_prime_x0 * dx
        linear_approx_backward = y0 - g_prime_x0 * dx
        actual_forward = g(x0 + dx)
        actual_backward = g(x0 - dx)

        # f(x) 常数项误差（基准偏移）
        fx_error_forward = Line(
            axes.c2p(x0 + dx, y0 - 0.1),
            axes.c2p(x0 + dx, y0 + 0.1),
            color=COLOR_SMOOTH,
            stroke_width=5,
        )
        fx_error_backward = Line(
            axes.c2p(x0 - dx, y0 - 0.1),
            axes.c2p(x0 - dx, y0 + 0.1),
            color=COLOR_SMOOTH,
            stroke_width=5,
        )

        # f''(x) 二阶项误差（线性近似与真实值的偏差）
        fdd_error_forward = Line(
            axes.c2p(x0 + dx, linear_approx_forward),
            axes.c2p(x0 + dx, actual_forward),
            color=COLOR_SMOOTH,
            stroke_width=4,
        )
        fdd_error_backward = Line(
            axes.c2p(x0 - dx, linear_approx_backward),
            axes.c2p(x0 - dx, actual_backward),
            color=COLOR_SMOOTH,
            stroke_width=4,
        )

        self.play(Create(fx_error_forward), Create(fx_error_backward), run_time=1.0)
        self.wait(0.5)
        self.play(Create(fdd_error_forward), Create(fdd_error_backward), run_time=0.8)
        self.wait(0.4)

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
        right_tex.to_edge(UP, buff=1.2).shift(RIGHT * 2.3)
        left_tex.next_to(right_tex, DOWN, buff=0.6, aligned_edge=LEFT)

        self.play(Write(right_tex), run_time=1.2)
        self.play(Write(left_tex), run_time=1.2)
        self.wait(0.4)

        hud.show("右减左：偶数阶互相抵消，留下更纯净的一阶导。", wait_after=1.2)

        # --------------------------------------------------------------------
        # 几何抵消动画：符号飞向误差线并爆炸
        # --------------------------------------------------------------------
        fx_forward = right_tex.get_part_by_tex("f(x)")
        fx_backward = left_tex.get_part_by_tex("f(x)")
        fdd_forward = right_tex.get_part_by_tex("f''(x)")
        fdd_backward = left_tex.get_part_by_tex("f''(x)")

        # 高亮 f(x)
        fx_rect1 = make_highlight_rect(fx_forward, color=COLOR_SMOOTH, buff=0.1, corner_radius=0.08, stroke_width=2.5)
        fx_rect2 = make_highlight_rect(fx_backward, color=COLOR_SMOOTH, buff=0.1, corner_radius=0.08, stroke_width=2.5)
        self.play(Create(fx_rect1), Create(fx_rect2), run_time=0.8)
        self.wait(0.3)

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

        error_group_fx = VGroup(fx_error_forward, fx_error_backward, fx_forward_copy, fx_backward_copy)
        apply_wave_effect(self, error_group_fx, amplitude=0.3, run_time=0.6)
        self.play(FadeOut(error_group_fx), run_time=0.4)
        self.wait(0.5)

        # 高亮 f''(x)
        fdd_rect1 = make_highlight_rect(fdd_forward, color=COLOR_SMOOTH, buff=0.1, corner_radius=0.08, stroke_width=2.5)
        fdd_rect2 = make_highlight_rect(fdd_backward, color=COLOR_SMOOTH, buff=0.1, corner_radius=0.08, stroke_width=2.5)
        self.play(Create(fdd_rect1), Create(fdd_rect2), run_time=0.8)
        self.wait(0.3)

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

        error_group_fdd = VGroup(fdd_error_forward, fdd_error_backward)
        apply_wave_effect(self, error_group_fdd, amplitude=0.3, run_time=0.6)
        self.play(FadeOut(error_group_fdd), FadeOut(VGroup(fdd_forward_copy, fdd_backward_copy)), run_time=0.4)
        self.wait(0.6)

        # 中心差分结果
        diff_tex = MathTex(
            r"f'(x) \approx \dfrac{f(x+1) - f(x-1)}{2}",
            font_size=40,
            color=WHITE,
        ).move_to(RIGHT * 2.8 + DOWN * 0.3)

        self.play(TransformMatchingTex(VGroup(right_tex, left_tex), diff_tex), run_time=1.8)
        self.wait(0.8)

        # 高亮唯一幸存的一阶导
        f_prime_part = diff_tex.get_part_by_tex("f'(x)")
        f_prime_highlight = make_highlight_rect(
            f_prime_part,
            color=COLOR_DIFF,
            buff=0.15,
            corner_radius=0.1,
            stroke_width=4
        )
        coeff = MathTex(r"[-1,\;0,\;1]", font_size=36, color=YELLOW_C).next_to(diff_tex, DOWN, buff=0.5)
        self.play(Write(coeff), Create(f_prime_highlight), run_time=1.2)
        self.wait(1.0)

        self.play(FadeOut(f_prime_highlight), run_time=0.6)
        hud.show("中心差分：用三点近似导数，误差仅剩二阶。", wait_after=1.5)
        self.wait(0.6)

        self.play(FadeOut(VGroup(
            axes, graph, forward_line, backward_line, fwd_label, bwd_label,
            diff_tex, coeff
        )), run_time=1.0)
        hud.clear()
        self.wait(0.3)


# =============================================================================
# Scene 2.5：差分对比（前向/后向/中心）
# =============================================================================
class Scene2_5Comparison(Scene):
    """
    P0 扩充：三种差分并排、误差可视化、真实函数对比
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("三种差分：前向、后向、中心 —— 谁的误差更小？", wait_after=1.0)

        axes_config = default_axis_config(stroke_opacity=0.9, stroke_width=2, stroke_color=GREY_B)
        x_rng = [0, 8, 1]
        y_rng = [0, 6, 1]
        def f(x): return 2 + 0.8 * np.sin(0.8 * x) + 0.6 * np.sin(0.3 * x + 0.5)

        # 三列坐标轴
        axes_forward = Axes(x_range=x_rng, y_range=y_rng, x_length=5.2, y_length=3.2, axis_config=axes_config, tips=False)
        axes_backward = axes_forward.copy()
        axes_center = axes_forward.copy()
        axes_group = VGroup(axes_forward, axes_backward, axes_center).arrange(RIGHT, buff=0.7).to_edge(UP, buff=0.6)

        labels = VGroup(
            safer_text("前向差分", font_size=24, color=COLOR_DIFF),
            safer_text("后向差分", font_size=24, color=COLOR_DIFF),
            safer_text("中心差分", font_size=24, color=COLOR_DIFF),
        )
        labels.arrange(RIGHT, buff=2.5).next_to(axes_group, UP, buff=0.25)

        self.play(FadeIn(VGroup(axes_group, labels), shift=UP * 0.2), run_time=1.2)

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

        forward_dots = scatter(forward_points, axes_forward, COLOR_DISCRETE)
        backward_dots = scatter(backward_points, axes_backward, COLOR_DISCRETE)
        center_dots = scatter(center_points, axes_center, COLOR_DISCRETE)

        self.play(
            FadeIn(forward_dots, lag_ratio=0.05),
            FadeIn(backward_dots, lag_ratio=0.05),
            FadeIn(center_dots, lag_ratio=0.05),
            run_time=1.6
        )
        self.wait(0.6)

        hud.show("中心差分利用两侧信息，误差阶更高。", wait_after=1.2)

        # 误差热力条（示意）
        def error_bar(val, max_val=1.2):
            alpha = np.clip(abs(val) / max_val, 0, 1)
            color = interpolate_color(COLOR_SMOOTH, COLOR_DIFF, alpha)
            bar = Rectangle(width=0.25, height=1.1 * alpha, fill_opacity=0.8, fill_color=color, stroke_width=0)
            return bar

        bars_fwd = VGroup(*[error_bar(fwd[1]) for fwd in forward_points]).arrange(RIGHT, buff=0.05)
        bars_bwd = VGroup(*[error_bar(bwd[1]) for bwd in backward_points]).arrange(RIGHT, buff=0.05)
        bars_cen = VGroup(*[error_bar(cen[1]) for cen in center_points]).arrange(RIGHT, buff=0.05)
        heatmap = VGroup(bars_fwd, bars_bwd, bars_cen).arrange(DOWN, buff=0.3).to_edge(DOWN, buff=0.9)

        heat_labels = VGroup(
            safer_text("误差强度（示意）", font_size=24, color=WHITE).next_to(heatmap, UP, buff=0.25),
            safer_text("红 = 误差大，蓝绿 = 误差小", font_size=20, color=GREY_B).next_to(heatmap, DOWN, buff=0.2),
        )

        self.play(FadeIn(VGroup(heatmap, heat_labels), shift=UP * 0.2), run_time=1.0)
        self.wait(1.0)

        hud.show("中心差分最“冷”，误差最低。", wait_after=1.2)

        # 实际函数上三条差分曲线对比
        axes_real = Axes(
            x_range=x_rng, y_range=[-3, 3, 1],
            x_length=10,
            y_length=3,
            axis_config=axes_config,
            tips=False,
        ).to_edge(DOWN, buff=0.35)
        fwd_graph = axes_real.plot(lambda x: (f(x + dx) - f(x)) / dx, x_range=[1, 7], color=COLOR_DISCRETE, stroke_width=2.5, stroke_opacity=0.8)
        bwd_graph = axes_real.plot(lambda x: (f(x) - f(x - dx)) / dx, x_range=[1, 7], color=COLOR_DIFF, stroke_width=2.5, stroke_opacity=0.65)
        cen_graph = axes_real.plot(lambda x: (f(x + dx) - f(x - dx)) / (2 * dx), x_range=[1, 7], color=COLOR_SMOOTH, stroke_width=3.2)
        legend = VGroup(
            safer_text("前向", font_size=20, color=COLOR_DISCRETE),
            safer_text("后向", font_size=20, color=COLOR_DIFF),
            safer_text("中心", font_size=20, color=COLOR_SMOOTH),
        ).arrange(RIGHT, buff=0.6).next_to(axes_real, UP, buff=0.2)

        self.play(Create(axes_real), FadeIn(legend, shift=UP * 0.1), run_time=1.0)
        self.play(Create(fwd_graph), run_time=0.8)
        self.play(Create(bwd_graph), run_time=0.8)
        self.play(Create(cen_graph), run_time=0.8)
        self.wait(0.8)

        hud.show("结论：中心差分 = 低误差、对称采样。", wait_after=1.4)

        self.play(FadeOut(VGroup(
            axes_group, labels, forward_dots, backward_dots, center_dots,
            heatmap, heat_labels, axes_real, fwd_graph, bwd_graph, cen_graph, legend
        )), run_time=1.2)
        hud.clear()
        self.wait(0.4)

# =============================================================================
# Scene 3：Sobel 诞生
# =============================================================================
class Scene3SobelConstruct(Scene):
    """
    第四部分：噪声→平滑→微分，Sobel 诞生
    采用 V12 局部卷积直觉修复：窗口滑动、fake_grad 放大、ApplyWave 强调
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("直接微分会放大噪声，先看一段“带噪信号”。", wait_after=0.8)

        axes_config = default_axis_config(stroke_opacity=0.9, stroke_width=2, stroke_color=GREY_B)
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

        noisy_graph = axes.plot(lambda x: noisy(x), x_range=[0, 10], color=COLOR_DISCRETE, stroke_width=3.5)
        clean_graph = axes.plot(lambda x: clean(x), x_range=[0, 10], color=COLOR_CONTINUOUS, stroke_width=3, stroke_opacity=0.4)

        self.play(Create(axes), run_time=0.8)
        self.play(Create(noisy_graph), run_time=1.2)
        self.play(FadeIn(clean_graph), run_time=0.8)
        self.wait(0.4)

        hud.show("套上纯微分核 [-1,0,1]：噪声被一并放大。", wait_after=1.0)

        diff_kernel = Matrix([[-1, 0, 1]], bracket_h_buff=0.2, bracket_v_buff=0.2)
        diff_kernel.set_color(COLOR_DIFF).scale(0.9)
        diff_label = safer_text("微分核", font_size=22, color=COLOR_DIFF).next_to(diff_kernel, DOWN, buff=0.2)
        diff_group = VGroup(diff_kernel, diff_label).to_edge(UP, buff=0.7).shift(RIGHT * 3)

        self.play(FadeIn(diff_group, shift=UP * 0.2), run_time=0.8)
        self.wait(0.6)

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

        grad_graph = diff_axes.plot(lambda x: fake_grad(x), x_range=[0, 10], color=COLOR_DIFF, stroke_width=3.5)
        self.play(Create(diff_axes), Create(grad_graph), run_time=1.2)
        apply_wave_effect(self, grad_graph, amplitude=0.4, run_time=0.8)
        self.wait(0.5)

        hud.show("先平滑，再微分：用 [1,2,1]^T 做低通，再用 [-1,0,1] 做高通。", wait_after=1.4)

        smooth_kernel = Matrix([[1], [2], [1]], bracket_h_buff=0.2, bracket_v_buff=0.2)
        smooth_kernel.set_color(COLOR_SMOOTH).scale(0.9)
        smooth_label = safer_text("平滑核", font_size=22, color=COLOR_SMOOTH).next_to(smooth_kernel, RIGHT, buff=0.25)
        smooth_group = VGroup(smooth_kernel, smooth_label).next_to(diff_group, DOWN, buff=0.6)

        self.play(FadeIn(smooth_group, shift=DOWN * 0.2), run_time=0.8)
        self.wait(0.4)

        # ------------------------------------------------------------
        # 窗口滑动可视化（V12 核心修复：局部卷积直觉）
        # ------------------------------------------------------------
        hud.show("平滑核滑过信号：窗口内的点被加权平均拉平。", wait_after=1.2)

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

        smoothed_graph = axes.plot(
            lambda x: smoothed_func(x, window_tracker.get_value()),
            x_range=[0, 10],
            color=COLOR_SMOOTH,
            stroke_width=3.5,
        )

        window_rect = Rectangle(
            width=1.0 * axes.x_axis.unit_size,
            height=axes.y_length,
            stroke_color=COLOR_SMOOTH,
            stroke_width=3,
            fill_color=COLOR_SMOOTH,
            fill_opacity=0.15,
        )

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
            color=COLOR_SMOOTH,
            stroke_width=3.5,
        )
        self.play(
            window_tracker.animate.set_value(target_window),
            Transform(smoothed_graph, target_graph),
            run_time=4.0,
            rate_func=smooth
        )
        self.wait(0.8)

        window_rect.remove_updater(update_window_rect)

        hud.show("平滑后，噪声被抑制，信号结构更清晰。", wait_after=1.2)
        self.play(
            noisy_graph.animate.set_opacity(0.3),
            FadeOut(window_rect),
            run_time=0.8
        )
        self.wait(0.6)

        # 外积生成 Sobel
        multiply = MathTex(r"\times", font_size=44, color=WHITE)
        equal = MathTex(r"=", font_size=44, color=WHITE)
        sobel_values = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        sobel_matrix = IntegerMatrix(sobel_values, element_alignment_corner=ORIGIN).scale(0.9)
        sobel_matrix.set_color_by_gradient(COLOR_DIFF, GOLD_C, COLOR_SMOOTH)

        eq_group = VGroup(
            smooth_kernel.copy(),
            multiply,
            diff_kernel.copy(),
            equal,
            sobel_matrix
        ).arrange(RIGHT, buff=0.3).to_edge(DOWN, buff=0.8)

        self.play(Write(multiply), Write(equal), FadeIn(sobel_matrix, shift=RIGHT * 0.2), run_time=1.4)
        self.play(Transform(VGroup(smooth_kernel, diff_kernel), VGroup(eq_group[0], eq_group[2])), run_time=0.001)
        self.wait(0.8)

        hud.show("Sobel = 平滑 × 微分：一手抓稳，一手抓变。", wait_after=1.4)
        self.wait(0.6)

        rect = make_highlight_rect(
            sobel_matrix,
            color=YELLOW_C,
            buff=0.2,
            corner_radius=0.12,
            stroke_width=3
        )
        self.play(Create(rect), run_time=0.8)
        self.wait(2.0)

        self.play(FadeOut(VGroup(
            axes, noisy_graph, clean_graph, smoothed_graph,
            diff_axes, grad_graph, diff_group, smooth_group, eq_group, rect
        )), run_time=1.0)
        hud.clear()
        self.wait(0.3)


# =============================================================================
# Scene 3.5：卷积可视化（滑动窗口 + 结果填充）
# =============================================================================
class Scene3_5Convolution(Scene):
    """
    P0 扩充：8x8 小图 + Sobel 核滑动，实时显示局部卷积值并填充结果矩阵
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("卷积 = 滑动窗口的加权求和。看看 Sobel 如何工作。", wait_after=1.0)

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
        kernel_matrix = IntegerMatrix(sobel_kernel.tolist()).set_color_by_gradient(COLOR_DIFF, GOLD_C, COLOR_SMOOTH).scale(0.7)
        kernel_label = safer_text("Sobel 核", font_size=24, color=COLOR_DIFF).next_to(kernel_matrix, DOWN, buff=0.2)
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
        result_label = safer_text("卷积结果", font_size=24, color=COLOR_SMOOTH).next_to(result_full, UP, buff=0.25)

        self.play(
            FadeIn(image_full, shift=UP * 0.2),
            FadeIn(kernel_group, shift=UP * 0.2),
            FadeIn(VGroup(result_full, result_label), shift=UP * 0.2),
            run_time=1.4
        )
        self.wait(0.6)

        hud.show("窗口逐行扫描，每一步计算 G = 核 · 局部补丁。", wait_after=1.0)

        # 滑动窗口框
        window = Square(side_length=cell * 3, stroke_color=COLOR_SMOOTH, stroke_width=3, fill_color=COLOR_SMOOTH, fill_opacity=0.12)

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
                alpha = np.clip(abs(conv_val) / 4.0, 0, 1)
                color = interpolate_color(COLOR_SMOOTH, COLOR_DIFF, alpha)

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
            color=COLOR_DIFF
        ).next_to(window, UP, buff=0.2))
        self.add(readout)

        for step, (pos, conv_val, cell_rect) in enumerate(animations):
            conv_tracker.set_value(conv_val)
            self.play(window.animate.move_to(image_full.get_center() + pos), run_time=0.25, rate_func=smooth)
            self.play(FadeIn(cell_rect, scale=0.3), run_time=0.15)
        self.wait(0.6)

        hud.show("卷积结果逐步填充：红=强边缘，蓝绿=弱。", wait_after=1.2)
        self.wait(0.6)

        self.play(FadeOut(VGroup(window, readout)), run_time=0.6)
        self.play(FadeOut(VGroup(image_full, kernel_group, result_full, result_label, fill_group)), run_time=1.0)
        hud.clear()
        self.wait(0.4)


# =============================================================================
# Scene 4.2：多尺度边缘（3x3 / 5x5 / 7x7 对比）
# =============================================================================
class Scene4_2MultiScale(Scene):
    """
    多尺度 Sobel 对比：展示 3x3 / 5x5 / 7x7 核的检测差异，并做融合示意
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("尺度决定细节：小核抓细纹，大核抓粗轮廓。", wait_after=1.0)

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
            label = Tex(rf"\text{{Sobel }}{k}", font_size=22, color=COLOR_DIFF).next_to(res_img, DOWN, buff=0.2)
            results.append(VGroup(res_img, label))

        grid = VGroup(
            VGroup(raw_img, safer_text("原图", font_size=22, color=WHITE).next_to(raw_img, DOWN, buff=0.2)),
            *results
        ).arrange(RIGHT, buff=0.6).scale(0.95).move_to(ORIGIN)

        self.play(FadeIn(grid, shift=UP * 0.2), run_time=1.6)
        self.wait(1.0)

        hud.show("3×3 抓细节，7×7 更平滑、边缘更粗。", wait_after=1.4)

        fused_vals = 0.4 * convolve(img_vals, kernels["3×3"]) + 0.35 * convolve(img_vals, kernels["5×5"]) + 0.25 * convolve(img_vals, kernels["7×7"])
        fused_img = make_image(fused_vals)
        fused_label = safer_text("多尺度融合", font_size=24, color=COLOR_SMOOTH).next_to(fused_img, DOWN, buff=0.2)
        fused_group = VGroup(fused_img, fused_label).to_edge(DOWN, buff=0.6)

        self.play(FadeIn(fused_group, shift=UP * 0.2), run_time=1.0)
        self.wait(1.0)

        hud.show("融合多尺度：既留细节，也保轮廓。", wait_after=1.2)

        self.play(FadeOut(VGroup(grid, fused_group)), run_time=1.0)
        hud.clear()
        self.wait(0.3)

# =============================================================================
# Scene 4：3D 扫描（Sobel 在地形上滑窗）
# =============================================================================
class Scene4Vision(ThreeDScene):
    """第五部分：3D 扫描，颜色随梯度大小变化"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("把亮度映射为高度，图像变成 3D 地形。", wait_after=1.8)

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
        surface.set_style(
            fill_opacity=0.8,
            stroke_color=COLOR_CONTINUOUS,
            stroke_width=q["stroke_width"] * 0.35,
            fill_color=COLOR_CONTINUOUS,
        )

        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        self.play(FadeIn(axes3d), FadeIn(surface), run_time=2.6)
        self.wait(1.0)

        hud.show("用滑动窗口扫描：窗口颜色随梯度大小而变。", wait_after=1.8)

        scan_tracker = ValueTracker(2)
        box_w, box_h = 1.4, 1.4
        scanner = RoundedRectangle(width=box_w, height=box_h, corner_radius=0.08, stroke_width=4, stroke_color=COLOR_SMOOTH)
        scanner.rotate(PI / 2, axis=RIGHT)

        laser = Line(ORIGIN, ORIGIN + DOWN * 1.2, color=COLOR_SMOOTH, stroke_width=3)
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
            delta = 0.1
            deriv = (height(u + delta, v) - height(u - delta, v)) / (2 * delta)
            T_min, T_max = 0.02, 0.4
            alpha = np.clip((abs(deriv) - T_min) / (T_max - T_min), 0, 1)
            new_color = interpolate_color(COLOR_SMOOTH, COLOR_DIFF, alpha)
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
            delta = 0.1
            return (height(x + delta, rows / 2) - height(x - delta, rows / 2)) / (2 * delta)

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
        self.wait(3.0)

        scanner_group.remove_updater(update_scanner)
        self.play(FadeOut(scanner_group), FadeOut(hud_group), FadeOut(graph), FadeOut(dot), run_time=1.4)
        hud.clear()
        self.play(FadeOut(VGroup(axes3d, surface)), run_time=1.2)
        self.wait(0.6)


# =============================================================================
# Scene 4.6：真实图像处理（灰度→SobelX/Y→幅值→阈值）
# =============================================================================
class Scene4_6RealImage(Scene):
    """
    真实图像处理链路示意（不加载外部文件，用合成矩阵代替）：
    原图 -> 灰度 -> Sobel X/Y -> 梯度幅值 -> 阈值
    """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("真实流程：原图 → 灰度 → Sobel X/Y → 梯度幅值 → 阈值。", wait_after=1.2)

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

        gx_img = make_image(gx, box_color=COLOR_DIFF)
        gy_img = make_image(gy, box_color=COLOR_DIFF)
        mag_img = make_image(grad_mag, box_color=COLOR_SMOOTH)

        # 阈值可调
        thresh = ValueTracker(0.35)
        def make_thresholded():
            vals = (grad_mag > thresh.get_value()).astype(float)
            return make_image(vals, box_color=YELLOW_C)
        edge_img = always_redraw(make_thresholded)

        # 布局：原图/灰度/SobelX/Y/幅值/阈值 六格
        row1 = VGroup(
            VGroup(raw_img, safer_text("原图", font_size=20, color=WHITE).next_to(raw_img, DOWN, buff=0.15)),
            VGroup(gray_img, safer_text("灰度", font_size=20, color=WHITE).next_to(gray_img, DOWN, buff=0.15)),
            VGroup(gx_img, safer_text("Sobel X", font_size=20, color=COLOR_DIFF).next_to(gx_img, DOWN, buff=0.15))
        ).arrange(RIGHT, buff=0.5)
        row2 = VGroup(
            VGroup(gy_img, safer_text("Sobel Y", font_size=20, color=COLOR_DIFF).next_to(gy_img, DOWN, buff=0.15)),
            VGroup(mag_img, safer_text("|G|", font_size=20, color=COLOR_SMOOTH).next_to(mag_img, DOWN, buff=0.15)),
            VGroup(edge_img, safer_text("阈值边缘", font_size=20, color=YELLOW_C).next_to(edge_img, DOWN, buff=0.15))
        ).arrange(RIGHT, buff=0.5)
        grid = VGroup(row1, row2).arrange(DOWN, buff=0.6).scale(0.9).move_to(ORIGIN)

        self.play(FadeIn(grid, shift=UP * 0.2), run_time=1.8)
        self.wait(1.0)

        hud.show("调阈值：过低=噪声，过高=断裂。", wait_after=1.2)
        self.play(thresh.animate.set_value(0.15), run_time=1.6)
        self.wait(0.4)
        self.play(thresh.animate.set_value(0.55), run_time=1.6)
        self.wait(0.4)
        self.play(thresh.animate.set_value(0.35), run_time=1.0)
        self.wait(0.6)

        self.play(FadeOut(grid), run_time=1.0)
        hud.clear()
        self.wait(0.4)


# =============================================================================
# Scene 4.5：应用对照（道路 + 文本）
# =============================================================================
class Scene4_5Applications(Scene):
    """第 4.5 部分：简单的应用对照示例"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("看看现实画面：左侧原图，右侧边缘提取。", wait_after=1.6)

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
        self.wait(2.4)

        hud.show("Sobel 把结构凸显：道路边界、笔画、人脸轮廓、建筑窗格。", wait_after=2.0)
        self.wait(1.6)

        # 阈值/对比度影响示意（建筑例子三档阈值）
        thresh_triplet = self._make_threshold_triplet()
        thresh_triplet.to_edge(DOWN, buff=0.4)
        thresh_title = safer_text("阈值影响：低/中/高", font_size=24, color=WHITE).next_to(thresh_triplet, UP, buff=0.25)
        self.play(FadeIn(VGroup(thresh_triplet, thresh_title), shift=UP * 0.2), run_time=1.0)
        self.wait(1.4)

        self.play(FadeOut(VGroup(grid, thresh_triplet, thresh_title)), run_time=1.0)
        hud.clear()
        self.wait(0.6)

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
        raw_label = safer_text("道路原图", font_size=20).next_to(raw_group, DOWN, buff=0.25)
        raw_all = VGroup(raw_group, raw_label).arrange(DOWN, buff=0.2)

        edge = VGroup()
        for i in range(size):
            for j in range(size):
                dist = abs(j - size / 2)
                if 2.4 < dist < 3.2:
                    color = COLOR_DIFF
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
        edge_label = safer_text("道路边缘", font_size=20).next_to(edge_group, DOWN, buff=0.25)
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
         raw_label = safer_text("文字原图", font_size=20).next_to(raw_group, DOWN, buff=0.25)
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
                    color = COLOR_DIFF
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
        edge_label = safer_text("文字边缘", font_size=20).next_to(edge_group, DOWN, buff=0.25)
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
        raw_label = safer_text("人脸原图", font_size=20).next_to(raw_group, DOWN, buff=0.25)
        raw_all = VGroup(raw_group, raw_label).arrange(DOWN, buff=0.2)

        edge = VGroup()
        for i in range(size):
            for j in range(size):
                on_edge = (
                    (i in [1, 6] or j in [1, 6]) or
                    (i == 2 and j in [2, 5]) or
                    (i == 5 and 2 <= j <= 5)
                )
                color = COLOR_DIFF if on_edge else BLACK
                op = 0.95 if on_edge else 0.08
                sq = Square(side_length=0.2, stroke_width=0, fill_opacity=op)
                sq.set_fill(color)
                sq.move_to(RIGHT * (j - size / 2) * 0.2 + UP * (size / 2 - i) * 0.2)
                edge.add(sq)
        edge_box = SurroundingRectangle(edge, color=GREY_B, stroke_width=2)
        edge_group = VGroup(edge_box, edge)
        edge_label = safer_text("人脸边缘", font_size=20).next_to(edge_group, DOWN, buff=0.25)
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
        raw_label = safer_text("建筑原图", font_size=20).next_to(raw_group, DOWN, buff=0.25)
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
                color = COLOR_DIFF if on_edge else BLACK
                op = 0.95 if on_edge else 0.08
                sq = Square(side_length=cell, stroke_width=0, fill_opacity=op)
                sq.set_fill(color)
                sq.move_to(RIGHT * (j - size / 2) * cell + UP * (size / 2 - i) * cell)
                edge.add(sq)
        edge_box = SurroundingRectangle(edge, color=GREY_B, stroke_width=2)
        edge_group = VGroup(edge_box, edge)
        edge_label = safer_text("建筑边缘", font_size=20).next_to(edge_group, DOWN, buff=0.25)
        edge_all = VGroup(edge_group, edge_label).arrange(DOWN, buff=0.2)
        # 额外返回 intensities 供阈值演示
        edge_all.intensities = intensities
        return raw_all, edge_all

    def _make_threshold_triplet(self):
        # 使用建筑 intensities 做三档阈值效果
        _, edge_all = self._make_building_pair()
        intensities = edge_all.intensities
        thresholds = [0.2, 0.45, 0.7]
        labels = ["低阈值", "中阈值", "高阈值"]
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
                    color = COLOR_DIFF if on_edge else BLACK
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
class Scene5Outro(Scene):
    """第六部分：回顾与片尾"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        hud.show("从连续导数到离散差分，从噪声到轮廓，我们看见了什么。", wait_after=2.0)

        step1 = safer_text("连续 → 离散", font_size=26, color=WHITE)
        step2 = MathTex(r"f'(x) \approx \dfrac{f(x+1)-f(x-1)}{2}", font_size=32, color=WHITE)
        step3 = IntegerMatrix([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]).scale(0.6).set_color_by_gradient(COLOR_DIFF, GOLD_C, COLOR_SMOOTH)
        step4 = safer_text("边缘检测 / 结构提取", font_size=26, color=WHITE)

        recap = VGroup(step1, step2, step3, step4).arrange(DOWN, buff=0.6, aligned_edge=LEFT).to_edge(LEFT, buff=0.8)
        self.play(FadeIn(recap, shift=UP * 0.2), run_time=1.8)
        self.wait(3.0)

        hud.show("知行合一：数学理想 Δx→0，工程现实 pixel=1。", wait_after=2.0)
        self.wait(2.0)

        philosophy = safer_text("让机器在嘈杂世界里，找到最清晰的边界。", font_size=32, color=YELLOW_C)
        phil_bg = BackgroundRectangle(philosophy, fill_opacity=0.7, color=BLACK, buff=0.3, corner_radius=0.08)
        phil_group = VGroup(phil_bg, philosophy).move_to(ORIGIN)
        self.play(
            Succession(
                phil_group.animate.scale(1.1).set_opacity(0),
                phil_group.animate.scale(1.0).set_opacity(1),
                run_time=0.8,
                rate_func=rate_functions.ease_out_back,
            )
        )
        self.wait(3.0)

        credits = VGroup(
            safer_text("Project Sobel", font_size=30, color=COLOR_CONTINUOUS),
            safer_text("Visuals: Manim Community Edition", font_size=20, color=GREY_B),
            safer_text("Code: Python 3.10 + Manim", font_size=20, color=GREY_B),
            safer_text("原创声明：本视频所有动画均为编程生成，素材来源已在文档列出。", font_size=22, color=WHITE),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT).to_edge(DOWN, buff=1.0).shift(RIGHT * 0.5)
        self.play(LaggedStart(*[FadeIn(line, shift=UP * 0.2) for line in credits], lag_ratio=0.2, run_time=2.2))
        self.wait(4.0)

        self.play(FadeOut(VGroup(recap, phil_group, credits)), run_time=1.6)
        hud.clear()
        self.wait(0.8)


# 运行示例：
# manim -pql sobel_v12_full.py Scene0Intro
# manim -pql sobel_v12_full.py Scene1Discrete
# manim -pql sobel_v12_full.py Scene2Taylor
# manim -pql sobel_v12_full.py Scene3SobelConstruct
# manim -pql sobel_v12_full.py Scene4Vision
# manim -pql sobel_v12_full.py Scene4_5Applications
# manim -pql sobel_v12_full.py Scene5Outro
if __name__ == "__main__":
    pass