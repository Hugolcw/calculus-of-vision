from manim import *
import numpy as np

# 导入 V12 统一工具模块
from utils import (
    SubtitleManager,
    safer_text,
    make_highlight_rect,
    default_axis_config,
    apply_wave_effect,
    COLOR_CONTINUOUS,
    COLOR_DISCRETE,
    COLOR_DIFF,
    COLOR_SMOOTH,
    BG_COLOR,
)


# =============================================================================
# Scene 0：开场谜题
# =============================================================================
class Scene0Intro(Scene):
    """第一部分：开场谜题 + 设问"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)  # 使用统一字幕管理器

        # 画面：清晰图 vs 噪声图
        clean = self._make_gradient_card()
        noisy = self._make_noisy_card()
        pair = VGroup(clean, noisy).arrange(RIGHT, buff=1.2).scale(0.9)
        title = safer_text("清晰图", font_size=26, color=WHITE).next_to(clean, DOWN, buff=0.25)
        title2 = safer_text("噪声图", font_size=26, color=WHITE).next_to(noisy, DOWN, buff=0.25)
        pair_group = VGroup(pair, title, title2)

        self.play(FadeIn(pair_group, shift=UP * 0.3), run_time=1.2)
        # 使用自动时长计算，wait_after 参数控制额外等待
        hud.show("在噪声里，仅凭数学，如何找到清晰的轮廓？", wait_after=1.5)

        # 居中问题文本（定格有画面承载）
        question = safer_text("数学能让机器看见吗？", font_size=34, color=YELLOW_C)
        question_bg = BackgroundRectangle(question, fill_opacity=0.7, color=BLACK, buff=0.28, corner_radius=0.08)
        question_group = VGroup(question_bg, question).move_to(ORIGIN + UP * 1.6)
        self.add_fixed_in_frame_mobjects(question_group)
        self.play(FadeIn(question_group, scale=0.9), run_time=0.8)
        self.wait(1.6)
        self.play(FadeOut(question_group, shift=UP * 0.2), run_time=0.6)

        hud.clear()
        self.play(FadeOut(pair_group), run_time=0.8)
        self.wait(0.4)

    def _make_gradient_card(self):
        card = RoundedRectangle(width=5.5, height=3.2, corner_radius=0.2, stroke_width=2.2, stroke_color=GREY_B)
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

    def _make_noisy_card(self):
        card = RoundedRectangle(width=5.5, height=3.2, corner_radius=0.2, stroke_width=2.2, stroke_color=GREY_B)
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


# =============================================================================
# Scene 1：连续→离散
# =============================================================================
class Scene1Discrete(Scene):
    """第二部分：连续→离散，失去极限，提出"如何找回导数" """

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)  # 使用统一字幕管理器

        # 坐标与连续曲线（使用统一样式配置）
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

        self.play(Create(axes), run_time=1.0)
        self.play(Create(curve), run_time=1.2)
        # 使用自动时长计算
        hud.show("在连续世界里，导数是切线的斜率。", wait_after=0.8)

        # 动态切线
        t = ValueTracker(2.0)

        def tangent():
            x = t.get_value()
            y = f(x)
            dx = 0.01
            dy = (f(x + dx) - f(x - dx)) / (2 * dx)
            return Line(
                axes.c2p(x - 1.5, y - dy * 1.5),
                axes.c2p(x + 1.5, y + dy * 1.5),
                color=COLOR_DIFF,
                stroke_width=3,
            )

        tan_line = always_redraw(tangent)
        tan_dot = always_redraw(lambda: Dot(axes.c2p(t.get_value(), f(t.get_value())), color=COLOR_DIFF, radius=0.08))

        self.add(tan_line, tan_dot)
        self.play(t.animate.set_value(8), run_time=2.8, rate_func=smooth)
        self.wait(0.6)

        # 采样：连续变离散，切线淡出，幽灵曲线
        hud.show("但在数字世界，Δx 无法趋近 0，切线消失。", wait_after=1.2)

        ghosts = curve.copy().set_stroke(color=GREY_B, opacity=0.25, width=2)
        samples = VGroup()
        xs = np.linspace(0, 10, 11)
        for x in xs:
            y = f(x)
            stem = Line(axes.c2p(x, 0), axes.c2p(x, y), color=COLOR_DISCRETE, stroke_width=3)
            dot = Dot(axes.c2p(x, y), color=COLOR_DISCRETE, radius=0.07)
            samples.add(stem, dot)

        self.play(
            curve.animate.set_opacity(0),
            FadeIn(ghosts),
            FadeIn(samples, lag_ratio=0.05, run_time=1.5),
            FadeOut(tan_line, shift=DOWN * 0.2),
            FadeOut(tan_dot, shift=DOWN * 0.2),
            run_time=1.6,
        )

        # 聚焦三点，Δx=1 约束（使用统一高亮框样式）
        focus_idx = len(xs) // 2
        focus_pts = [focus_idx - 1, focus_idx, focus_idx + 1]
        highlights = VGroup(*[samples[2 * i + 1] for i in focus_pts])  # 取 dot
        box = make_highlight_rect(highlights, color=YELLOW_C, buff=0.3, corner_radius=0.12, stroke_width=3)
        dx_line = Line(
            axes.c2p(xs[focus_idx - 1], -0.4),
            axes.c2p(xs[focus_idx], -0.4),
            color=COLOR_DIFF,
            stroke_width=3,
        )
        dx_label = MathTex(r"\Delta x = 1", font_size=30, color=COLOR_DIFF).next_to(dx_line, DOWN, buff=0.2)

        hud.show("最小步长是 1 个像素，我们失去了极限。", wait_after=1.2)
        self.play(Create(box), Create(dx_line), FadeIn(dx_label), run_time=1.2)

        # 放大特写（放大物体，不动相机），并显示困境问号
        question = safer_text("如何在离散像素里找回导数？", font_size=30, color=YELLOW_C)
        q_bg = BackgroundRectangle(question, fill_opacity=0.7, color=BLACK, buff=0.25, corner_radius=0.08)
        q_group = VGroup(q_bg, question).to_edge(UP, buff=0.6)
        self.add_fixed_in_frame_mobjects(q_group)

        cluster = VGroup(axes, ghosts, samples, box, dx_line, dx_label)
        focus_point = axes.c2p(xs[focus_idx], f(xs[focus_idx]))
        self.play(
            cluster.animate.scale(2.0, about_point=focus_point).shift(ORIGIN - focus_point),
            FadeIn(q_group, shift=UP * 0.2),
            run_time=1.8,
            rate_func=smooth,
        )
        self.wait(1.8)

        # 收尾
        hud.clear()
        self.play(FadeOut(VGroup(cluster, q_group)), run_time=1.0)
        self.wait(0.3)


# =============================================================================
# Scene 2：泰勒抵消 → 中心差分
# =============================================================================
class Scene2Taylor(Scene):
    """第三部分：泰勒抵消 → 中心差分（V12 几何化修复）"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)  # 使用统一字幕管理器

        hud.show("前向与后向的斜率各有偏差，如何消掉误差？", wait_after=0.8)

        # 函数与切线（使用统一样式配置）
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

        # ====================================================================
        # 【V12 核心修复】在公式展示前，先绘制几何误差向量
        # ====================================================================
        # 泰勒展开的几何意义：
        # f(x+1) = f(x) + f'(x) + (1/2)f''(x) + ...
        # f(x-1) = f(x) - f'(x) + (1/2)f''(x) + ...
        # 
        # f(x) 常数项误差：在 x0+1 和 x0-1 处，用水平线表示"基准偏移"（相对于 x0 的值）
        # f''(x) 二阶项误差：从线性近似到实际值的剩余偏差（主要由二次项贡献）
        
        g_prime_x0 = 0.6 + 0.8 * x0  # g'(x0) = 0.6 + 0.8*x
        linear_approx_forward = y0 + g_prime_x0 * dx  # 线性近似在 x0+1 的值
        linear_approx_backward = y0 - g_prime_x0 * dx  # 线性近似在 x0-1 的值
        actual_forward = g(x0 + dx)
        actual_backward = g(x0 - dx)
        
        # f(x) 常数项误差：用水平线从 x0 的 y0 延伸到 x0+1 和 x0-1（表示"基准"）
        # 简化表示：在 x0+1 和 x0-1 处绘制水平误差标记
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
        
        # f''(x) 二阶项误差：从线性近似值到实际值的偏差（垂直误差线）
        # 这是二次项导致的额外偏差
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
        
        # 先显示误差向量
        self.play(
            Create(fx_error_forward),
            Create(fx_error_backward),
            run_time=1.0
        )
        self.wait(0.5)
        
        self.play(
            Create(fdd_error_forward),
            Create(fdd_error_backward),
            run_time=0.8
        )
        self.wait(0.4)

        # 泰勒展开文字+公式
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

        # ====================================================================
        # 【V12 核心修复】几何抵消动画：符号飞向误差向量位置并爆炸消失
        # ====================================================================
        fx_forward = right_tex.get_part_by_tex("f(x)")
        fx_backward = left_tex.get_part_by_tex("f(x)")
        fdd_forward = right_tex.get_part_by_tex("f''(x)")
        fdd_backward = left_tex.get_part_by_tex("f''(x)")

        # 高亮 f(x) 项
        fx_rect1 = make_highlight_rect(fx_forward, color=COLOR_SMOOTH, buff=0.1, corner_radius=0.08, stroke_width=2.5)
        fx_rect2 = make_highlight_rect(fx_backward, color=COLOR_SMOOTH, buff=0.1, corner_radius=0.08, stroke_width=2.5)

        self.play(Create(fx_rect1), Create(fx_rect2), run_time=0.8)
        self.wait(0.3)
        
        # f(x) 符号飞向几何误差线位置并爆炸消失
        # 创建符号的副本用于动画（保持原符号半透明）
        fx_forward_copy = fx_forward.copy().set_opacity(1)
        fx_backward_copy = fx_backward.copy().set_opacity(1)
        
        # 误差线中心位置（用于符号飞向的目标点）
        fx_error_forward_center = fx_error_forward.get_center()
        fx_error_backward_center = fx_error_backward.get_center()
        
        self.add(fx_forward_copy, fx_backward_copy)
        
        # 符号缩小并飞向误差线位置
        self.play(
            FadeOut(fx_rect1), FadeOut(fx_rect2),
            fx_forward.animate.set_opacity(0.25),
            fx_backward.animate.set_opacity(0.25),
            fx_forward_copy.animate.scale(0.5).move_to(fx_error_forward_center),
            fx_backward_copy.animate.scale(0.5).move_to(fx_error_backward_center),
            run_time=1.0,
            rate_func=smooth
        )
        
        # 在误差线位置触发 ApplyWave 爆炸消失
        error_group_fx = VGroup(fx_error_forward, fx_error_backward, fx_forward_copy, fx_backward_copy)
        apply_wave_effect(self, error_group_fx, amplitude=0.3, run_time=0.6)
        self.play(
            FadeOut(error_group_fx),
            run_time=0.4
        )
        self.wait(0.5)

        # 同样处理 f''(x) 项
        fdd_rect1 = make_highlight_rect(fdd_forward, color=COLOR_SMOOTH, buff=0.1, corner_radius=0.08, stroke_width=2.5)
        fdd_rect2 = make_highlight_rect(fdd_backward, color=COLOR_SMOOTH, buff=0.1, corner_radius=0.08, stroke_width=2.5)

        self.play(Create(fdd_rect1), Create(fdd_rect2), run_time=0.8)
        self.wait(0.3)
        
        # f''(x) 符号飞向几何误差箭头位置
        fdd_forward_copy = fdd_forward.copy().set_opacity(1)
        fdd_backward_copy = fdd_backward.copy().set_opacity(1)
        
        fdd_error_forward_center = fdd_error_forward.get_center()
        fdd_error_backward_center = fdd_error_backward.get_center()
        
        self.add(fdd_forward_copy, fdd_backward_copy)
        
        self.play(
            FadeOut(fdd_rect1), FadeOut(fdd_rect2),
            fdd_forward.animate.set_opacity(0.25),
            fdd_backward.animate.set_opacity(0.25),
            fdd_forward_copy.animate.scale(0.5).move_to(fdd_error_forward_center),
            fdd_backward_copy.animate.scale(0.5).move_to(fdd_error_backward_center),
            run_time=1.0,
            rate_func=smooth
        )
        
        # 在误差箭头位置触发 ApplyWave 爆炸消失
        error_group_fdd = VGroup(fdd_error_forward, fdd_error_backward, fdd_forward_copy, fdd_backward_copy)
        apply_wave_effect(self, error_group_fdd, amplitude=0.3, run_time=0.6)
        self.play(
            FadeOut(error_group_fdd),
            run_time=0.4
        )
        self.wait(0.6)

        # 中心差分结果
        diff_tex = MathTex(
            r"f'(x) \approx \dfrac{f(x+1) - f(x-1)}{2}",
            font_size=40,
            color=WHITE,
        ).move_to(RIGHT * 2.8 + DOWN * 0.3)

        self.play(TransformMatchingTex(VGroup(right_tex, left_tex), diff_tex), run_time=1.8)
        self.wait(0.8)

        # 【专家建议】高亮保留的 f'(x) 项，强调它是唯一幸存的结果
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
        
        # 保持高亮，淡出其他元素
        self.play(
            FadeOut(f_prime_highlight),
            run_time=0.6
        )
        self.wait(0.5)

        # 定格展示，防遮挡：字幕在下，公式在右侧
        hud.show("中心差分：用三点近似导数，误差仅剩二阶。", wait_after=1.5)
        self.wait(0.6)

        self.play(FadeOut(VGroup(axes, graph, forward_line, backward_line, fwd_label, bwd_label, diff_tex, coeff)),
                  run_time=1.0)
        hud.clear()
        self.wait(0.3)


# =============================================================================
# Scene 3：Sobel 诞生
# =============================================================================
class Scene3SobelConstruct(Scene):
    """第四部分：噪声→平滑→微分，Sobel 诞生（V12 局部卷积直觉修复）"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)  # 使用统一字幕管理器

        hud.show("直接微分会放大噪声，先看一段\"带噪信号\"。", wait_after=0.8)

        # 使用统一样式配置
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

        # 纯微分卷积示意：仅标注，不做真实卷积
        diff_kernel = Matrix([[-1, 0, 1]], bracket_h_buff=0.2, bracket_v_buff=0.2)
        diff_kernel.set_color(COLOR_DIFF).scale(0.9)
        diff_label = safer_text("微分核", font_size=22, color=COLOR_DIFF).next_to(diff_kernel, DOWN, buff=0.2)
        diff_group = VGroup(diff_kernel, diff_label).to_edge(UP, buff=0.7).shift(RIGHT * 3)

        self.play(FadeIn(diff_group, shift=UP * 0.2), run_time=0.8)
        self.wait(0.6)

        # 微分结果（示意波形）
        diff_axes_config = default_axis_config(stroke_opacity=0.9, stroke_width=2, stroke_color=GREY_B)
        diff_axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-3, 3, 1],
            x_length=8,
            y_length=3,
            axis_config=diff_axes_config,
            tips=False,
        ).to_edge(RIGHT, buff=0.8).shift(DOWN * 0.6)

        # 【V12 核心修复 I】放大 fake_grad 振幅（×1.5），突出抖动的灾难性
        def fake_grad(x): return 1.5 * (noisy(x + 0.1) - noisy(x - 0.1)) / 0.2
        grad_graph = diff_axes.plot(lambda x: fake_grad(x), x_range=[0, 10], color=COLOR_DIFF, stroke_width=3.5)

        self.play(Create(diff_axes), Create(grad_graph), run_time=1.2)
        # 【V12 核心修复 I】应用抖动效果，强调噪声被放大
        apply_wave_effect(self, grad_graph, amplitude=0.4, run_time=0.8)
        self.wait(0.5)

        hud.show("先平滑，再微分：用 [1,2,1]^T 做低通，再用 [-1,0,1] 做高通。", wait_after=1.4)

        smooth_kernel = Matrix([[1], [2], [1]], bracket_h_buff=0.2, bracket_v_buff=0.2)
        smooth_kernel.set_color(COLOR_SMOOTH).scale(0.9)
        smooth_label = safer_text("平滑核", font_size=22, color=COLOR_SMOOTH).next_to(smooth_kernel, RIGHT, buff=0.25)
        smooth_group = VGroup(smooth_kernel, smooth_label).next_to(diff_group, DOWN, buff=0.6)

        self.play(FadeIn(smooth_group, shift=DOWN * 0.2), run_time=0.8)
        self.wait(0.4)

        # ====================================================================
        # 【V12 核心修复 II】局部卷积直觉：平滑窗口滑过，局部拉平曲线
        # ====================================================================
        hud.show("平滑核滑过信号：窗口内的点被加权平均拉平。", wait_after=1.2)
        
        # 创建平滑后的曲线（初始与 noisy_graph 相同，后续逐渐向 clean_graph 收敛）
        def smoothed_func(x, window_center, blend_factor):
            """
            模拟平滑核 [1,2,1] 的局部加权平均
            window_center: 窗口中心位置
            blend_factor: 混合因子（0=noisy, 1=clean）
            """
            window_width = 1.0  # 窗口宽度（对应 3 个采样点）
            dist = abs(x - window_center)
            
            if dist <= window_width:
                # 窗口内：按权重向 clean_graph 插值（距离窗口中心越近，权重越大）
                # 权重函数：中心点权重 2，两侧权重 1（归一化后）
                if dist < 0.1:
                    weight = 0.5  # 中心权重最高
                elif dist < 0.5:
                    weight = 0.3  # 中等权重
                else:
                    weight = 0.1  # 边缘权重低
                
                # 混合因子：窗口内更倾向于 clean，窗口外保持 noisy
                local_blend = blend_factor * weight
                return (1 - local_blend) * noisy(x) + local_blend * clean(x)
            else:
                # 窗口外：保持 noisy（或已处理过的平滑值）
                # 这里简化：窗口外保持原 noisy 值
                return noisy(x)
        
        # 创建平滑曲线的动态更新函数
        window_tracker = ValueTracker(0.5)  # 窗口中心位置
        blend_tracker = ValueTracker(0.0)  # 混合因子（0=noisy, 1=clean）
        
        def update_smoothed_graph(mob):
            """根据窗口位置和混合因子更新平滑曲线"""
            window_center = window_tracker.get_value()
            blend = blend_tracker.get_value()
            
            # 重新绘制曲线（仅更新窗口内部分）
            new_graph = axes.plot(
                lambda x: smoothed_func(x, window_center, blend),
                x_range=[0, 10],
                color=COLOR_SMOOTH,
                stroke_width=3.5,
            )
            mob.become(new_graph)
        
        smoothed_graph = axes.plot(
            lambda x: smoothed_func(x, window_tracker.get_value(), blend_tracker.get_value()),
            x_range=[0, 10],
            color=COLOR_SMOOTH,
            stroke_width=3.5,
        )
        
        # 创建滑动窗口可视化（矩形框，高亮当前处理区域）
        window_rect = Rectangle(
            width=1.0 * axes.x_axis.unit_size,  # 窗口宽度对应 1 个单位
            height=axes.y_length,
            stroke_color=COLOR_SMOOTH,
            stroke_width=3,
            fill_color=COLOR_SMOOTH,
            fill_opacity=0.15,
        )
        
        def update_window_rect(mob):
            """更新窗口位置"""
            window_center = window_tracker.get_value()
            center_pos = axes.c2p(window_center, 0)
            mob.move_to(center_pos)
        
        window_rect.add_updater(update_window_rect)
        self.add(smoothed_graph, window_rect)
        
        # 平滑窗口滑动动画（窗口内曲线逐渐向 clean_graph 收敛）
        # 阶段 1：窗口缓慢滑动，窗口内的点逐渐拉平
        smoothed_graph.add_updater(update_smoothed_graph)
        
        # 先让窗口滑动，同时混合因子逐渐增加（窗口内点向 clean 收敛）
        self.play(
            window_tracker.animate.set_value(9.5),
            blend_tracker.animate.set_value(1.0),
            run_time=4.0,
            rate_func=smooth
        )
        self.wait(0.8)
        
        # 移除更新器，保持最终状态
        smoothed_graph.remove_updater(update_smoothed_graph)
        window_rect.remove_updater(update_window_rect)
        
        # 展示平滑效果：对比 noisy 和 smoothed
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
        self.play(Transform(VGroup(smooth_kernel, diff_kernel), VGroup(eq_group[0], eq_group[2])), run_time=0.001)  # 确保引用
        self.wait(0.8)

        hud.show("Sobel = 平滑 × 微分：一手抓稳，一手抓变。", wait_after=1.4)
        self.wait(0.6)

        # 高亮矩阵，定格 2s（使用统一高亮框样式）
        rect = make_highlight_rect(
            sobel_matrix,
            color=YELLOW_C,
            buff=0.2,
            corner_radius=0.12,
            stroke_width=3
        )
        self.play(Create(rect), run_time=0.8)
        self.wait(2.0)

        # 收尾
        self.play(FadeOut(VGroup(axes, noisy_graph, clean_graph, smoothed_graph, diff_axes, grad_graph, diff_group, smooth_group, eq_group, rect)),
                  run_time=1.0)
        hud.clear()
        self.wait(0.3)


# =============================================================================
# Scene 4：3D 扫描（Sobel 在地形上滑窗）
# =============================================================================
class Scene4Vision(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)  # 使用统一字幕管理器

        hud.show("把亮度映射为高度，图像变成 3D 地形。", wait_after=1.8)

        rows, cols = 30, 30

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
            resolution=(26, 26),
            should_make_jagged=False,
        )
        surface.set_style(
            fill_opacity=0.8,
            stroke_color=COLOR_CONTINUOUS,
            stroke_width=0.8,
            fill_color=COLOR_CONTINUOUS,
        )

        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        self.play(FadeIn(axes3d), FadeIn(surface), run_time=2.6)
        self.wait(1.0)

        hud.show("用滑动窗口扫描：窗口颜色随梯度大小而变。", wait_after=1.8)

        # 扫描器
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
# Scene 4.5：应用对照（道路 + 文本）
# =============================================================================
class Scene4_5Applications(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)  # 使用统一字幕管理器

        hud.show("看看现实画面：左侧原图，右侧边缘提取。", wait_after=1.6)

        # 道路示例
        road_raw, road_edge = self._make_road_pair()
        text_raw, text_edge = self._make_text_pair()

        road_group = VGroup(road_raw, road_edge).arrange(RIGHT, buff=0.6)
        text_group = VGroup(text_raw, text_edge).arrange(RIGHT, buff=0.6)

        pair = VGroup(road_group, text_group).arrange(DOWN, buff=0.8)
        pair.move_to(ORIGIN)

        self.play(FadeIn(pair, shift=UP * 0.2), run_time=1.6)
        self.wait(3.0)

        hud.show("Sobel 把结构凸显出来：道路边界、文字笔画更清晰。", wait_after=2.0)
        self.wait(2.0)

        self.play(FadeOut(pair), run_time=1.0)
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


# =============================================================================
# Scene 5：总结与片尾
# =============================================================================
class Scene5Outro(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)  # 使用统一字幕管理器

        hud.show("从连续导数到离散差分，从噪声到轮廓，我们看见了什么。", wait_after=2.0)

        # 回顾元素
        step1 = safer_text("连续 → 离散", font_size=26, color=WHITE)
        step2 = MathTex(r"f'(x) \approx \dfrac{f(x+1)-f(x-1)}{2}", font_size=32, color=WHITE)
        step3 = IntegerMatrix([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]).scale(0.6).set_color_by_gradient(COLOR_DIFF, GOLD_C, COLOR_SMOOTH)
        step4 = safer_text("边缘检测 / 结构提取", font_size=26, color=WHITE)

        recap = VGroup(step1, step2, step3, step4).arrange(DOWN, buff=0.6, aligned_edge=LEFT).to_edge(LEFT, buff=0.8)
        self.play(FadeIn(recap, shift=UP * 0.2), run_time=1.8)
        self.wait(3.0)

        hud.show("知行合一：数学理想 Δx→0，工程现实 pixel=1。", wait_after=2.0)
        self.wait(2.0)

        # 哲学文本
        philosophy = safer_text("让机器在嘈杂世界里，找到最清晰的边界。", font_size=32, color=YELLOW_C)
        phil_bg = BackgroundRectangle(philosophy, fill_opacity=0.7, color=BLACK, buff=0.3, corner_radius=0.08)
        phil_group = VGroup(phil_bg, philosophy).move_to(ORIGIN)
        # 爆发式显现 + 弹性
        self.play(
            Succession(
                phil_group.animate.scale(1.1).set_opacity(0),
                phil_group.animate.scale(1.0).set_opacity(1),
                run_time=0.8,
                rate_func=rate_functions.ease_out_back,
            )
        )
        self.wait(3.0)

        # 片尾声明
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
# manim -pql sobel_v11_full.py Scene0Intro
# manim -pql sobel_v11_full.py Scene1Discrete
# manim -pql sobel_v11_full.py Scene2Taylor
# manim -pql sobel_v11_full.py Scene3SobelConstruct
# manim -pql sobel_v11_full.py Scene4Vision
# manim -pql sobel_v11_full.py Scene4_5Applications
# manim -pql sobel_v11_full.py Scene5Outro
if __name__ == "__main__":
    pass

