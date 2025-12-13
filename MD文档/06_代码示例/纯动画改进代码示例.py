"""
纯动画版本改进代码示例
这些代码片段展示了如何修改各个场景，添加字幕、标题和延长等待时间
"""

from manim import *
import numpy as np

# ============================================================================
# 场景标题和字幕辅助函数
# ============================================================================

def create_scene_title(text, color=WHITE, font_size=36):
    """创建场景标题"""
    title = Text(text, font_size=font_size, color=color)
    title.to_edge(UP, buff=0.5)
    # 添加半透明背景提高可读性
    bg = BackgroundRectangle(title, color=BLACK, fill_opacity=0.7, buff=0.1)
    return VGroup(bg, title)

def create_subtitle(text, color=WHITE, font_size=28, position=DOWN):
    """创建字幕"""
    subtitle = Text(text, font_size=font_size, color=color)
    if position == DOWN:
        subtitle.to_edge(DOWN, buff=0.5)
    elif position == UP:
        subtitle.to_edge(UP, buff=1.5)  # 在标题下方
    # 添加半透明背景
    bg = BackgroundRectangle(subtitle, color=BLACK, fill_opacity=0.7, buff=0.1)
    return VGroup(bg, subtitle)

# ============================================================================
# Scene 1 改进示例
# ============================================================================

def setup_scene_1_discrete_improved(self):
    """Scene 1 改进版：添加标题和字幕"""
    
    # ===== 添加场景标题 =====
    scene_title = create_scene_title("数学理想：连续世界", COLOR_CONTINUOUS)
    self.play(FadeIn(scene_title), run_time=0.5)
    
    # Act 1: 理想展示 - 连续函数（原代码）
    axes = Axes(
        x_range=[-1, 11, 1],
        y_range=[-1, 5, 1],
        x_length=12,
        y_length=5,
        axis_config={"stroke_opacity": 0.5, "stroke_width": 1},
        tips=False
    )
    
    def continuous_func(x):
        return 2 + np.sin(x * 0.5) + 0.5 * np.sin(x)
    
    func_continuous = axes.plot(
        continuous_func,
        x_range=[0, 10],
        color=COLOR_CONTINUOUS,
        stroke_width=3
    )
    
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
    
    slope_text = always_redraw(lambda: DecimalNumber(
        (continuous_func(tangent_tracker.get_value() + 0.01) - 
         continuous_func(tangent_tracker.get_value() - 0.01)) / 0.02,
        num_decimal_places=2,
        color=COLOR_DIFF
    ).next_to(tangent_line, UP))
    
    # ===== 添加说明字幕 =====
    subtitle1 = create_subtitle("连续函数：Δx → 0", COLOR_CONTINUOUS)
    
    # 播放动画（延长时间）
    self.play(
        Create(axes), 
        Create(func_continuous), 
        FadeIn(subtitle1),
        run_time=1.5,  # 从1秒增加到1.5秒
        rate_func=smooth
    )
    self.add(tangent_line, slope_text)
    self.play(tangent_tracker.animate.set_value(8), run_time=2.5, rate_func=smooth)  # 从2秒增加到2.5秒
    self.wait(1)  # 从0秒增加到1秒，让观众理解
    
    # Act 2: 幽灵变换 - 离散采样
    # ===== 切换字幕 =====
    subtitle2 = create_subtitle("工程现实：离散采样", COLOR_DISCRETE)
    
    ghost_graph = func_continuous.copy()
    ghost_graph.set_stroke(color=COLOR_CONTINUOUS, width=3, opacity=1)
    
    num_samples = 10
    x_samples = np.linspace(0, 10, num_samples)
    discrete_stems = VGroup()
    
    for x in x_samples:
        y = continuous_func(x)
        start_point = axes.c2p(x, 0)
        end_point = axes.c2p(x, y)
        stem = Line(start_point, end_point, color=COLOR_DISCRETE, stroke_width=2.5)
        dot = Dot(end_point, color=COLOR_DISCRETE, radius=0.05)
        discrete_stems.add(stem, dot)
    
    # ===== 添加视觉引导：箭头指向采样点 =====
    # 可选：在第一个和最后一个采样点添加箭头
    first_arrow = Arrow(
        axes.c2p(0, continuous_func(0)) + UP * 0.5,
        axes.c2p(0, continuous_func(0)),
        color=COLOR_DISCRETE,
        buff=0
    )
    last_arrow = Arrow(
        axes.c2p(10, continuous_func(10)) + UP * 0.5,
        axes.c2p(10, continuous_func(10)),
        color=COLOR_DISCRETE,
        buff=0
    )
    sample_arrows = VGroup(first_arrow, last_arrow)
    
    self.add(ghost_graph)
    
    self.play(
        FadeOut(subtitle1),
        FadeIn(subtitle2),
        func_continuous.animate.set_opacity(0),
        ghost_graph.animate.set_stroke(color=COLOR_GHOST, width=1, opacity=OPACITY_GHOST),
        Create(discrete_stems),
        Create(sample_arrows),  # 新增
        run_time=2.5  # 从2秒增加到2.5秒
    )
    self.wait(1.5)  # 从0.5秒增加到1.5秒
    self.play(FadeOut(sample_arrows))  # 箭头淡出
    
    # Act 3: 聚焦困境
    focus_point = axes.c2p(5, continuous_func(5))
    scene_group = VGroup(axes, func_continuous, ghost_graph, discrete_stems, tangent_line, slope_text)
    
    question_mark = MathTex("?", font_size=72, color=YELLOW).move_to(UP * 1.5)
    
    # ===== 添加问题说明 =====
    problem_text = create_subtitle("在离散世界中，如何找回导数？", YELLOW)
    # 调整位置，避免与问号重叠
    problem_text[1].next_to(question_mark, DOWN, buff=0.8)
    
    self.play(
        scene_group.animate.scale(2.5, about_point=focus_point).shift(ORIGIN - focus_point),
        Write(question_mark),
        FadeIn(problem_text),
        run_time=2.5  # 从2秒增加到2.5秒
    )
    self.wait(2.5)  # 从1秒增加到2.5秒，让观众思考
    
    # 清理
    self.play(
        FadeOut(scene_group),
        FadeOut(question_mark),
        FadeOut(scene_title),
        FadeOut(subtitle2),
        FadeOut(problem_text),
        run_time=1.5  # 从1秒增加到1.5秒
    )

# ============================================================================
# Scene 2 改进示例
# ============================================================================

def setup_scene_2_taylor_improved(self):
    """Scene 2 改进版：增强可视化和字幕"""
    
    # ===== 添加场景标题 =====
    scene_title = create_scene_title("数学桥梁：泰勒展开", WHITE)
    self.play(FadeIn(scene_title), run_time=0.5)
    
    # Act 1: 分步揭示泰勒公式
    taylor_forward = MathTex(
        "f(x+1)", "\\approx", "f(x)", "+", "f'(x)", "+", "\\frac{1}{2}f''(x)",
        substrings_to_isolate=["f(x)", "f'(x)", "f''(x)"],
        font_size=48
    ).shift(UP * 2)
    
    taylor_backward = MathTex(
        "f(x-1)", "\\approx", "f(x)", "-", "f'(x)", "+", "\\frac{1}{2}f''(x)",
        substrings_to_isolate=["f(x)", "f'(x)", "f''(x)"],
        font_size=48
    ).next_to(taylor_forward, DOWN, buff=0.8)
    
    # ===== 添加公式说明标签 =====
    forward_label = Text("向前一步：f(x+1)", font_size=24, color=BLUE_C)
    forward_label.next_to(taylor_forward, LEFT, buff=0.8)
    forward_label_bg = BackgroundRectangle(forward_label, color=BLACK, fill_opacity=0.7, buff=0.1)
    forward_label_group = VGroup(forward_label_bg, forward_label)
    
    backward_label = Text("向后一步：f(x-1)", font_size=24, color=RED_C)
    backward_label.next_to(taylor_backward, LEFT, buff=0.8)
    backward_label_bg = BackgroundRectangle(backward_label, color=BLACK, fill_opacity=0.7, buff=0.1)
    backward_label_group = VGroup(backward_label_bg, backward_label)
    
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
        Write(taylor_forward[0:2]), 
        FadeIn(forward_label_group),
        run_time=1.5  # 从1秒增加到1.5秒
    )
    self.play(
        Write(taylor_forward[2:]), 
        LaggedStart(*[Write(parabolas[i]) for i in range(2)], lag_ratio=0.3),
        run_time=2.5  # 从2秒增加到2.5秒
    )
    self.wait(1.5)  # 从0.5秒增加到1.5秒，让观众阅读公式
    
    self.play(
        Write(taylor_backward[0:2]),
        FadeIn(backward_label_group),
        run_time=1.5  # 从1秒增加到1.5秒
    )
    self.play(
        Write(taylor_backward[2:]), 
        run_time=2.5  # 从2秒增加到2.5秒
    )
    self.wait(2)  # 从1秒增加到2秒
    
    # Act 2: 视觉对撞 - 抵消相同项
    try:
        f_x_forward_part = taylor_forward.get_part_by_tex("f(x)")
        f_x_backward_part = taylor_backward.get_part_by_tex("f(x)")
    except:
        f_x_forward_part = taylor_forward[2] if len(taylor_forward) > 2 else taylor_forward
        f_x_backward_part = taylor_backward[2] if len(taylor_backward) > 2 else taylor_backward
    
    try:
        f_double_forward_part = taylor_forward.get_part_by_tex("f''(x)")
        f_double_backward_part = taylor_backward.get_part_by_tex("f''(x)")
    except:
        f_double_forward_part = taylor_forward[-1] if len(taylor_forward) > 0 else taylor_forward
        f_double_backward_part = taylor_backward[-1] if len(taylor_backward) > 0 else taylor_backward
    
    # ===== 增强"消消乐"效果：添加箭头连接相同项 =====
    # 创建箭头从f(x)项指向另一个f(x)项
    arrow_fx_start = f_x_forward_part.get_center() + LEFT * 0.5
    arrow_fx_end = f_x_backward_part.get_center() + LEFT * 0.5
    arrow_fx = Arrow(arrow_fx_start, arrow_fx_end, color=COLOR_DIFF, buff=0.1, stroke_width=3)
    
    # 添加"相同"标签
    same_label = Text("相同项", font_size=20, color=COLOR_DIFF)
    same_label.next_to(arrow_fx, LEFT, buff=0.2)
    same_label_bg = BackgroundRectangle(same_label, color=BLACK, fill_opacity=0.7, buff=0.05)
    same_label_group = VGroup(same_label_bg, same_label)
    
    f_x_forward_rect = SurroundingRectangle(f_x_forward_part, color=COLOR_DIFF, buff=0.15, corner_radius=0.08)
    f_x_backward_rect = SurroundingRectangle(f_x_backward_part, color=COLOR_DIFF, buff=0.15, corner_radius=0.08)
    
    # ===== 添加说明字幕 =====
    cancel_subtitle = create_subtitle("相同的项会相互抵消", COLOR_DIFF)
    
    self.play(
        Create(f_x_forward_rect),
        Create(f_x_backward_rect),
        Create(arrow_fx),
        FadeIn(same_label_group),
        FadeIn(cancel_subtitle),
        run_time=1)  # 从0.5秒增加到1秒
    self.wait(2)  # 从0.5秒增加到2秒，让观众理解
    
    self.play(
        FadeOut(f_x_forward_rect),
        FadeOut(f_x_backward_rect),
        FadeOut(arrow_fx),
        FadeOut(same_label_group),
        f_x_forward_part.animate.set_opacity(0),
        f_x_backward_part.animate.set_opacity(0),
        run_time=1.5  # 从1秒增加到1.5秒
    )
    
    # 同样处理 f''(x) 项
    arrow_fdouble_start = f_double_forward_part.get_center() + LEFT * 0.5
    arrow_fdouble_end = f_double_backward_part.get_center() + LEFT * 0.5
    arrow_fdouble = Arrow(arrow_fdouble_start, arrow_fdouble_end, color=COLOR_DIFF, buff=0.1, stroke_width=3)
    
    f_double_prime_forward_rect = SurroundingRectangle(f_double_forward_part, color=COLOR_DIFF, buff=0.15, corner_radius=0.08)
    f_double_prime_backward_rect = SurroundingRectangle(f_double_backward_part, color=COLOR_DIFF, buff=0.15, corner_radius=0.08)
    
    self.play(
        Create(f_double_prime_forward_rect),
        Create(f_double_prime_backward_rect),
        Create(arrow_fdouble),
        run_time=1)  # 从0.5秒增加到1秒
    self.wait(2)  # 从0.5秒增加到2秒
    self.play(
        FadeOut(f_double_prime_forward_rect),
        FadeOut(f_double_prime_backward_rect),
        FadeOut(arrow_fdouble),
        f_double_forward_part.animate.set_opacity(0),
        f_double_backward_part.animate.set_opacity(0),
        run_time=1.5  # 从1秒增加到1.5秒
    )
    
    # Act 3: 算子结晶 - 形成差分公式
    diff_formula = MathTex(
        "f'(x)", "\\approx", "\\frac{f(x+1) - f(x-1)}{2}",
        font_size=48
    ).move_to(ORIGIN)
    
    # ===== 添加结论字幕 =====
    conclusion_subtitle = create_subtitle("中心差分：系数 [-1, 0, 1]", YELLOW)
    
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
        FadeOut(forward_label_group),
        FadeOut(backward_label_group),
        FadeOut(cancel_subtitle),
        FadeIn(conclusion_subtitle),
        run_time=2.5  # 从2秒增加到2.5秒
    )
    self.wait(2)  # 从1秒增加到2秒
    
    coefficient_text = MathTex("[-1, 0, 1]", font_size=36).next_to(diff_formula, DOWN)
    self.play(Write(coefficient_text), run_time=1.5)  # 从1秒增加到1.5秒
    self.play(
        FadeOut(coefficient_text, shift=DOWN * 0.2),
        GrowFromCenter(kernel_x),
        kernel_x.animate.scale(1.5).to_edge(DOWN),
        run_time=2,  # 从1.5秒增加到2秒
        rate_func=smooth
    )
    self.wait(2)  # 从1秒增加到2秒
    
    # 清理
    self.play(
        FadeOut(VGroup(diff_formula, coefficient_text, kernel_x)),
        FadeOut(scene_title),
        FadeOut(conclusion_subtitle),
        run_time=1.5  # 从1秒增加到1.5秒
    )


# ============================================================================
# 使用说明
# ============================================================================

"""
使用方法：
1. 将这些改进函数复制到 sobel_complete.py
2. 在 SobelUniverse 类中替换原有的 setup_scene_1_discrete 和 setup_scene_2_taylor 方法
3. 按照相同模式改进其他场景（Scene 3, 3.5, 4, 5）
4. 全局增加 wait 时间（一般翻倍）
5. 测试渲染：manim -pql sobel_complete.py SobelUniverse
6. 最终渲染：manim -pqh sobel_complete.py SobelUniverse

关键改进点：
- 添加场景标题（create_scene_title）
- 添加字幕说明（create_subtitle）
- 延长所有 wait 时间（翻倍）
- 延长关键动画时长（增加0.5-1秒）
- 增强视觉引导（箭头、标注）
- 添加半透明背景提高字幕可读性
"""

