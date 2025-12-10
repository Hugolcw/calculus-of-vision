from manim import *
import numpy as np

# =============================================================================
# 全局配置（与 scene01_02 保持一致）
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
    try:
        return Text(s, font_size=font_size, color=color, font="SimHei")
    except Exception:
        return Text(s, font_size=font_size, color=color)


class Scene2Taylor(Scene):
    """第三部分：泰勒抵消 → 中心差分"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleHUD(self)

        hud.show("前向与后向的斜率各有偏差，如何消掉误差？", wait_time=1.2)

        # 函数与切线
        axes = Axes(
            x_range=[-1, 3, 1],
            y_range=[-1, 3, 1],
            x_length=6,
            y_length=3.5,
            axis_config={"stroke_opacity": 0.9, "stroke_width": 2, "stroke_color": GREY_B},
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

        hud.show("前向与后向各有系统误差：奇偶阶项混在一起。", wait_time=1.4)

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

        hud.show("右减左：偶数阶互相抵消，留下更纯净的一阶导。", wait_time=1.6)

        # 抵消动效
        fx_forward = right_tex.get_part_by_tex("f(x)")
        fx_backward = left_tex.get_part_by_tex("f(x)")
        fdd_forward = right_tex.get_part_by_tex("f''(x)")
        fdd_backward = left_tex.get_part_by_tex("f''(x)")

        fx_rect1 = SurroundingRectangle(fx_forward, color=COLOR_SMOOTH, buff=0.1, corner_radius=0.08)
        fx_rect2 = SurroundingRectangle(fx_backward, color=COLOR_SMOOTH, buff=0.1, corner_radius=0.08)
        fdd_rect1 = SurroundingRectangle(fdd_forward, color=COLOR_SMOOTH, buff=0.1, corner_radius=0.08)
        fdd_rect2 = SurroundingRectangle(fdd_backward, color=COLOR_SMOOTH, buff=0.1, corner_radius=0.08)

        self.play(Create(fx_rect1), Create(fx_rect2), run_time=0.8)
        self.play(FadeOut(fx_rect1), FadeOut(fx_rect2),
                  fx_forward.animate.set_opacity(0.25),
                  fx_backward.animate.set_opacity(0.25),
                  run_time=0.8)

        self.play(Create(fdd_rect1), Create(fdd_rect2), run_time=0.8)
        self.play(FadeOut(fdd_rect1), FadeOut(fdd_rect2),
                  fdd_forward.animate.set_opacity(0.25),
                  fdd_backward.animate.set_opacity(0.25),
                  run_time=0.8)
        self.wait(0.6)

        # 中心差分结果
        diff_tex = MathTex(
            r"f'(x) \approx \dfrac{f(x+1) - f(x-1)}{2}",
            font_size=40,
            color=WHITE,
        ).move_to(RIGHT * 2.8 + DOWN * 0.3)

        self.play(TransformMatchingTex(VGroup(right_tex, left_tex), diff_tex), run_time=1.8)
        self.wait(0.8)

        coeff = MathTex(r"[-1,\;0,\;1]", font_size=36, color=YELLOW_C).next_to(diff_tex, DOWN, buff=0.5)
        self.play(Write(coeff), run_time=1.0)
        self.wait(0.8)

        # 定格展示，防遮挡：字幕在下，公式在右侧
        hud.show("中心差分：用三点近似导数，误差仅剩二阶。", wait_time=2.0)
        self.wait(0.6)

        self.play(FadeOut(VGroup(axes, graph, forward_line, backward_line, fwd_label, bwd_label, diff_tex, coeff)),
                  run_time=1.0)
        hud.clear()
        self.wait(0.3)


class Scene3SobelConstruct(Scene):
    """第四部分：噪声→平滑→微分，Sobel 诞生"""

    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleHUD(self)

        hud.show("直接微分会放大噪声，先看一段“带噪信号”。", wait_time=1.2)

        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-2, 3, 1],
            x_length=10,
            y_length=4,
            axis_config={"stroke_opacity": 0.9, "stroke_width": 2, "stroke_color": GREY_B},
            tips=False,
        ).to_edge(LEFT, buff=0.8)

        def clean(x): return np.sin(x * 0.6)
        rng = np.random.default_rng(1)
        noise = lambda x: 0.35 * rng.normal(0, 1)
        noisy = lambda x: clean(x) + noise(x)

        xs = np.linspace(0, 10, 50)
        noisy_graph = axes.plot(lambda x: noisy(x), x_range=[0, 10], color=COLOR_DISCRETE, stroke_width=3.5)
        clean_graph = axes.plot(lambda x: clean(x), x_range=[0, 10], color=COLOR_CONTINUOUS, stroke_width=3, stroke_opacity=0.4)

        self.play(Create(axes), run_time=0.8)
        self.play(Create(noisy_graph), run_time=1.2)
        self.play(FadeIn(clean_graph), run_time=0.8)
        self.wait(0.4)

        hud.show("套上纯微分核 [-1,0,1]：噪声被一并放大。", wait_time=1.4)

        # 纯微分卷积示意：仅标注，不做真实卷积
        diff_kernel = Matrix([[-1, 0, 1]], bracket_h_buff=0.2, bracket_v_buff=0.2)
        diff_kernel.set_color(COLOR_DIFF).scale(0.9)
        diff_label = safer_text("微分核", font_size=22, color=COLOR_DIFF).next_to(diff_kernel, DOWN, buff=0.2)
        diff_group = VGroup(diff_kernel, diff_label).to_edge(UP, buff=0.7).shift(RIGHT * 3)

        self.play(FadeIn(diff_group, shift=UP * 0.2), run_time=0.8)
        self.wait(0.6)

        # 微分结果（示意波形）
        diff_axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-3, 3, 1],
            x_length=8,
            y_length=3,
            axis_config={"stroke_opacity": 0.9, "stroke_width": 2, "stroke_color": GREY_B},
            tips=False,
        ).to_edge(RIGHT, buff=0.8).shift(DOWN * 0.6)

        def fake_grad(x): return (noisy(x + 0.1) - noisy(x - 0.1)) / 0.2
        grad_graph = diff_axes.plot(lambda x: fake_grad(x), x_range=[0, 10], color=COLOR_DIFF, stroke_width=3.5)

        self.play(Create(diff_axes), Create(grad_graph), run_time=1.2)
        self.wait(0.5)

        hud.show("先平滑，再微分：用 [1,2,1]^T 做低通，再用 [-1,0,1] 做高通。", wait_time=1.8)

        smooth_kernel = Matrix([[1], [2], [1]], bracket_h_buff=0.2, bracket_v_buff=0.2)
        smooth_kernel.set_color(COLOR_SMOOTH).scale(0.9)
        smooth_label = safer_text("平滑核", font_size=22, color=COLOR_SMOOTH).next_to(smooth_kernel, RIGHT, buff=0.25)
        smooth_group = VGroup(smooth_kernel, smooth_label).next_to(diff_group, DOWN, buff=0.6)

        self.play(FadeIn(smooth_group, shift=DOWN * 0.2), run_time=0.8)
        self.wait(0.4)

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

        hud.show("Sobel = 平滑 × 微分：一手抓稳，一手抓变。", wait_time=1.8)
        self.wait(0.6)

        # 高亮矩阵，定格 2s
        rect = SurroundingRectangle(sobel_matrix, color=YELLOW_C, buff=0.2, corner_radius=0.12, stroke_width=3)
        self.play(Create(rect), run_time=0.8)
        self.wait(2.0)

        # 收尾
        self.play(FadeOut(VGroup(axes, noisy_graph, clean_graph, diff_axes, grad_graph, diff_group, smooth_group, eq_group, rect)),
                  run_time=1.0)
        hud.clear()
        self.wait(0.3)


# 用法：
# manim -pql sobel_v11_scene03_04.py Scene2Taylor
# manim -pql sobel_v11_scene03_04.py Scene3SobelConstruct
if __name__ == "__main__":
    pass

