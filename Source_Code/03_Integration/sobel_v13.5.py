from manim import *
import numpy as np

# 导入 V13 强大的基础设施
from utils_v13 import (
    SubtitleManager,
    safer_text,
    make_highlight_rect,
    default_axis_config,
    get_quality_config,
    PALETTE,
    SAFE_RECT,
    SUBTITLE_Y,
    LEFT_COL, RIGHT_COL,
    SmartBox,
    FocusArrow,
    NeonLine,
    BaseScene,
    BaseThreeDScene,
    BG_COLOR,
)

# =============================================================================
# V14 全局节奏控制器
# =============================================================================
# 慢节奏因子：所有 wait 时间翻倍，营造“娓娓道来”的质感
WAIT_FACTOR = 2.0 

def slow_wait(scene, time):
    scene.wait(time * WAIT_FACTOR)

# =============================================================================
# Scene 0: 直觉与混沌 (Intuition & Chaos)
# =============================================================================
class Scene0Intro(BaseScene):
    """
    极简主义开场：只有噪声与秩序的对抗。
    去除了 V12 的粒子特效，专注于红线从混沌中生长的过程。
    """
    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        # 1. 混沌引入 (Chaos)
        # 使用高清噪声图 (ImageMobject) 替代 V12 的圆点堆砌，质感提升
        noise_arr = np.random.rand(128, 128) * 0.8 + 0.1
        noise_img = ImageMobject(noise_arr).scale(6).set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        
        hud.show("对于人眼，世界是清晰的轮廓...", wait_after=0.5)
        slow_wait(self, 1.5)
        
        self.play(FadeIn(noise_img, run_time=3.0))
        hud.show("但在机器眼中，世界只是一团跳动的数值混沌。", wait_after=1.0)
        slow_wait(self, 2.0)

        # 2. 秩序生长 (Order)
        # 红色边缘线缓慢生长，象征算法的力量
        lines = VGroup()
        for x in np.linspace(-3, 3, 15):
            line = NeonLine.create(
                start=[x, -2, 0], end=[x, 2, 0], 
                color=PALETTE["EDGE"], stroke_width=3
            )
            lines.add(line)
        
        hud.show("我们的任务：在混沌中提取秩序。", wait_after=0.5)
        
        # 极慢速生长，配合背景变暗
        self.play(
            noise_img.animate.set_opacity(0.2),
            LaggedStart(
                *[Create(l, run_time=4.0, rate_func=linear) for l in lines],
                lag_ratio=0.1
            ),
            run_time=5.0
        )
        slow_wait(self, 1.0)

        # 3. 设问 (The Question)
        q_text = safer_text("如何在离散的像素海洋中，教会机器‘看见’边界？", font_size=32, color=PALETTE["HIGHLIGHT"])
        self.play(FadeOut(lines), FadeOut(noise_img))
        self.play(Write(q_text), run_time=2.0)
        slow_wait(self, 2.0)
        
        self.clear_scene()

# =============================================================================
# Scene 1: 失去极限 (The Lost Limit)
# =============================================================================
class Scene1Discrete(BaseScene):
    """
    不仅展示离散，更强调“困境”。
    合并了 V13 的 Scene 1 和 Scene 1.5，叙事更紧凑。
    """
    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        # 1. 理想回顾
        axes = Axes(x_range=[0, 6, 1], y_range=[0, 4, 1], x_length=8, y_length=5, axis_config=default_axis_config())
        graph = axes.plot(lambda x: 2 + np.sin(x), color=PALETTE["MATH_FUNC"], stroke_width=4)
        
        hud.show("在数学理想国，导数是切线的斜率。", wait_after=0.5)
        self.add_to_math_group(axes, graph)
        self.play(Create(axes), Create(graph), run_time=2.0)
        
        # 动态切线 (使用单一信源 ValueTracker)
        t = ValueTracker(1.5)
        tangent = always_redraw(lambda: axes.get_secant_slope_group(
            x=t.get_value(), graph=graph, dx=0.01, secant_line_color=PALETTE["MATH_ERROR"], secant_line_length=3
        ))
        self.add(tangent)
        self.play(t.animate.set_value(4.5), run_time=3.0)
        slow_wait(self, 1.0)

        # 2. 现实打击
        hud.show("微积分的前提：Δx 必须无限趋近于 0。", wait_after=1.0)
        
        # 像素化过程
        pixel_grid = VGroup(*[
            Square(side_length=0.5).move_to(axes.c2p(x, 2)) 
            for x in np.arange(0.5, 5.5, 0.5)
        ]).set_stroke(opacity=0.3)
        
        self.play(FadeIn(pixel_grid), graph.animate.set_opacity(0.3))
        hud.show("但在数字图像中，像素锁死了最小距离。", wait_after=1.5)
        
        # 3. 困境可视化
        # 放大展示 Δx=1
        dx_arrow = DoubleArrow(
            axes.c2p(2, 1), axes.c2p(3, 1), color=PALETTE["HIGHLIGHT"], buff=0
        )
        dx_label = MathTex(r"\Delta x_{min} = 1", color=PALETTE["HIGHLIGHT"]).next_to(dx_arrow, DOWN)
        
        self.play(Create(dx_arrow), Write(dx_label))
        hud.show("我们失去了极限，也就失去了导数。", wait_after=2.0)
        
        self.clear_scene()

# =============================================================================
# Scene 2: 桥梁与巧合 (The Bridge)
# =============================================================================
class Scene2Taylor(BaseScene):
    """
    用视觉化的“融合”代替“爆炸”，展现泰勒误差抵消的优雅。
    """
    def construct(self):
        self.camera.background_color = BG_COLOR
        hud = SubtitleManager(self)

        # 1. 引入泰勒
        hud.show("既然后退不了(像素限制)，我们就同时向左和向右看。", wait_after=1.0)
        
        tex_fwd = MathTex(r"f(x+1) \approx f(x) + f'(x) + \frac{1}{2}f''(x)").shift(UP)
        tex_bwd = MathTex(r"f(x-1) \approx f(x) - f'(x) + \frac{1}{2}f''(x)").shift(DOWN)
        
        self.add_to_math_group(tex_fwd, tex_bwd)
        self.play(Write(tex_fwd), run_time=2.0)
        slow_wait(self, 0.5)
        self.play(Write(tex_bwd), run_time=2.0)
        
        # 2. 视觉融合 (Visual Fusion)
        # 高亮误差项
        err_fwd = tex_fwd.get_part_by_tex("f''(x)")
        err_bwd = tex_bwd.get_part_by_tex("f''(x)")
        
        box_fwd = SmartBox.create(err_fwd, color=PALETTE["MATH_ERROR"])
        box_bwd = SmartBox.create(err_bwd, color=PALETTE["MATH_ERROR"])
        
        self.play(Create(box_fwd), Create(box_bwd))
        hud.show("注意这两项误差：大小相等，符号相同。", wait_after=1.0)
        
        # 3. 相减抵消
        # 创造一个减号
        minus = MathTex("-", font_size=80).move_to(ORIGIN)
        line = Line(LEFT*4, RIGHT*4).move_to(DOWN*2)
        result = MathTex(r"f'(x) \approx \frac{f(x+1) - f(x-1)}{2}", color=PALETTE["HIGHLIGHT"]).next_to(line, DOWN)
        
        self.play(FadeIn(minus), Create(line))
        
        # 误差项飞向中间“湮灭”
        self.play(
            err_fwd.animate.move_to(minus),
            err_bwd.animate.move_to(minus),
            box_fwd.animate.move_to(minus).set_opacity(0),
            box_bwd.animate.move_to(minus).set_opacity(0),
            run_time=2.0
        )
        self.play(Flash(minus, color=PALETTE["MATH_ERROR"], flash_radius=0.5))
        self.remove(err_fwd, err_bwd, minus)
        
        hud.show("相减之后，误差奇迹般地消失了。", wait_after=1.5)
        self.play(Write(result), run_time=2.0)
        
        # 4. 导出算子
        kernel = IntegerMatrix([[-1, 0, 1]]).set_color(PALETTE["EDGE"]).next_to(result, DOWN, buff=1)
        hud.show("这就是中心差分，也是 Sobel 的一半灵魂。", wait_after=1.0)
        self.play(TransformFromCopy(result, kernel))
        
        slow_wait(self, 2.0)
        self.clear_scene()

# =============================================================================
# Scene 3: 构造 Sobel (Construction)
# =============================================================================
class Scene3Sobel(BaseScene):
    def construct(self):
        hud = SubtitleManager(self)
        
        # 静态展示，极简
        k_smooth = IntegerMatrix([[1], [2], [1]]).set_color(PALETTE["MATH_FUNC"])
        k_diff = IntegerMatrix([[-1, 0, 1]]).set_color(PALETTE["MATH_ERROR"])
        
        group = VGroup(k_smooth, MathTex(r"\times"), k_diff).arrange(RIGHT)
        
        hud.show("Sobel 算子 = 平滑(降噪) × 差分(求导)。", wait_after=0.5)
        self.play(FadeIn(group))
        slow_wait(self, 1.5)
        
        # 合体
        k_final = IntegerMatrix([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]).set_color(PALETTE["HIGHLIGHT"])
        eq = MathTex("=").next_to(group, RIGHT)
        k_final.next_to(eq, RIGHT)
        
        self.play(Write(eq), TransformFromCopy(group, k_final))
        hud.show("一手按住噪声，一手抓取边缘。", wait_after=2.0)
        
        self.clear_scene()

# =============================================================================
# Scene 4: 真实的视界 (The Real Vision) - HD Remaster
# =============================================================================
class Scene4RealImage(BaseScene):
    """
    使用高清 ImageMobject 替代方块拼贴。
    展示真实图像的处理流程。
    """
    def construct(self):
        hud = SubtitleManager(self)
        self.camera.background_color = BG_COLOR
        
        # 1. 生成高清纹理 (128x128)
        size = 128
        xx, yy = np.meshgrid(np.linspace(-3, 3, size), np.linspace(-3, 3, size))
        # 生成一个带有圆环和线条的图案
        img_data = np.zeros((size, size))
        mask_circle = (xx**2 + yy**2 < 2) & (xx**2 + yy**2 > 1.5)
        mask_line = (np.abs(xx - yy) < 0.2)
        img_data[mask_circle | mask_line] = 1.0
        # 加噪
        noise = np.random.normal(0, 0.1, (size, size))
        img_noisy = np.clip(img_data + noise, 0, 1)
        
        # 2. 显示流程
        img_obj = ImageMobject(img_noisy).scale(4).set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        
        hud.show("回到最初的问题：机器现在能看见了吗？", wait_after=1.0)
        self.play(FadeIn(img_obj))
        slow_wait(self, 1.0)
        
        # 3. 扫描线效果 (模拟计算)
        scanner = Line(LEFT*2, RIGHT*2, color=PALETTE["EDGE"]).move_to(UP*2)
        self.play(
            scanner.animate.move_to(DOWN*2),
            run_time=4.0, 
            rate_func=linear
        )
        
        # 4. 结果显现
        # 简单的梯度计算模拟结果
        img_edge_data = np.clip(img_data * 1.5, 0, 1) # 模拟边缘
        img_edge = ImageMobject(img_edge_data).scale(4).set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        img_edge.set_color(PALETTE["EDGE"]) # 给图片着色
        
        self.play(FadeOut(scanner), FadeIn(img_edge))
        hud.show("噪声被过滤，只留下清晰的数学骨架。", wait_after=2.0)
        
        self.clear_scene()

# =============================================================================
# Scene 5: 结语 (Epilogue)
# =============================================================================
class Scene5Credits(BaseScene):
    def construct(self):
        hud = SubtitleManager(self)
        
        quote = safer_text(
            "数学，是我们在混沌世界中唯一的眼睛。", 
            font_size=36, color=PALETTE["HIGHLIGHT"]
        )
        self.play(Write(quote), run_time=3.0)
        slow_wait(self, 2.0)
        self.play(FadeOut(quote))
        
        # V10 风格的演职员表 (致敬初心)
        credits = VGroup(
            safer_text("Project Sobel V14", font_size=32, color=PALETTE["MATH_FUNC"]),
            safer_text("Powered by Manim & Calculus", font_size=24, color=GREY_B),
            safer_text("Dedicated to the beauty of math", font_size=24, color=GREY_B)
        ).arrange(DOWN, buff=0.5)
        
        self.play(LaggedStart(*[FadeIn(c, shift=UP*0.5) for c in credits], lag_ratio=0.3, run_time=3.0))
        slow_wait(self, 3.0)
        
        self.play(FadeOut(credits))

# =============================================================================
# Full Wrapper
# =============================================================================
class FullSobelMasterpiece(BaseScene):
    def construct(self):
        Scene0Intro.construct(self)
        Scene1Discrete.construct(self)
        Scene2Taylor.construct(self)
        Scene3Sobel.construct(self)
        Scene4RealImage.construct(self)
        Scene5Credits.construct(self)

if __name__ == "__main__":
    pass