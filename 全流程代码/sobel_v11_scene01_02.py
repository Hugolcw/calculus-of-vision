from manim import *
import numpy as np

# =============================================================================
# 全局配置
# =============================================================================
COLOR_CONTINUOUS = BLUE_C
COLOR_DISCRETE = YELLOW_C
COLOR_DIFF = RED_C
COLOR_SMOOTH = TEAL_C
BG_COLOR = "#0e1111"
SUBTITLE_FONT_SIZE = 28
TITLE_FONT_SIZE = 36
SUBTITLE_BG_OPACITY = 0.75


class SubtitleHUD:
    """固定在屏幕底部的字幕，不随场景移动。"""

    def __init__(self, scene: Scene):
        self.scene = scene
        self.mobj = None
        self.bg = None

    def show(self, text: str, color=WHITE, wait_time: float = 1.0, font_size=SUBTITLE_FONT_SIZE):
        self.clear()
        try:
            subtitle = Text(text, font_size=font_size, color=color, font="SimHei")
        except Exception:
            subtitle = Text(text, font_size=font_size, color=color)
        subtitle.to_edge(DOWN, buff=0.45)
        bg = BackgroundRectangle(
            subtitle,
            color=BLACK,
            fill_opacity=SUBTITLE_BG_OPACITY,
            buff=0.22,
            stroke_width=0,
            corner_radius=0.06,
        )
        group = VGroup(bg, subtitle)
        self.scene.add_fixed_in_frame_mobjects(group)
        self.scene.play(FadeIn(group, shift=UP * 0.2), run_time=0.6)
        self.mobj, self.bg = subtitle, bg
        if wait_time > 0:
            self.scene.wait(wait_time)

    def clear(self):
        if self.mobj:
            self.scene.play(
                FadeOut(VGroup(self.bg, self.mobj), shift=DOWN * 0.2),
                run_time=0.4,
            )
        self.mobj = None
        self.bg = None


def safer_text(s: str, font_size=30, color=WHITE):
    """中文安全 Text 封装。"""
    try:
        return Text(s, font_size=font_size, color=color, font="SimHei")
    except Exception:
        return Text(s, font_size=font_size, color=color)


class Scene0Intro(Scene):
    """第一部分：开场谜题 + 设问"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleHUD(self)

        # 画面：清晰图 vs 噪声图
        clean = self._make_gradient_card()
        noisy = self._make_noisy_card()
        pair = VGroup(clean, noisy).arrange(RIGHT, buff=1.2).scale(0.9)

        title = safer_text("清晰图", font_size=26, color=WHITE).next_to(clean, DOWN, buff=0.25)
        title2 = safer_text("噪声图", font_size=26, color=WHITE).next_to(noisy, DOWN, buff=0.25)
        pair_group = VGroup(pair, title, title2)

        self.play(FadeIn(pair_group, shift=UP * 0.3), run_time=1.2)
        hud.show("在噪声里，仅凭数学，如何找到清晰的轮廓？", wait_time=2.0)

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


class Scene1Discrete(Scene):
    """第二部分：连续→离散，失去极限，提出“如何找回导数”"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleHUD(self)

        # 坐标与连续曲线
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 5, 1],
            x_length=11,
            y_length=4.5,
            axis_config={"stroke_opacity": 0.9, "stroke_width": 2, "stroke_color": GREY_B},
            tips=False,
        )
        def f(x): return 2 + np.sin(0.5 * x) + 0.5 * np.sin(x)
        curve = axes.plot(f, x_range=[0, 10], color=COLOR_CONTINUOUS, stroke_width=4)

        self.play(Create(axes), run_time=1.0)
        self.play(Create(curve), run_time=1.2)
        hud.show("在连续世界里，导数是切线的斜率。", wait_time=1.2)

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
        hud.show("但在数字世界，Δx 无法趋近 0，切线消失。", wait_time=1.6)

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

        # 聚焦三点，Δx=1 约束
        focus_idx = len(xs) // 2
        focus_pts = [focus_idx - 1, focus_idx, focus_idx + 1]
        highlights = VGroup(*[samples[2 * i + 1] for i in focus_pts])  # 取 dot
        box = SurroundingRectangle(highlights, color=YELLOW_C, buff=0.3, stroke_width=3, corner_radius=0.12)
        dx_line = Line(
            axes.c2p(xs[focus_idx - 1], -0.4),
            axes.c2p(xs[focus_idx], -0.4),
            color=COLOR_DIFF,
            stroke_width=3,
        )
        dx_label = MathTex(r"\Delta x = 1", font_size=30, color=COLOR_DIFF).next_to(dx_line, DOWN, buff=0.2)

        hud.show("最小步长是 1 个像素，我们失去了极限。", wait_time=1.6)
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


# 便于测试：manim -pql sobel_v11_scene01_02.py Scene0Intro
if __name__ == "__main__":
    pass

