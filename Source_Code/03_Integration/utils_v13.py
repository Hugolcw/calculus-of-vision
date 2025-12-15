"""
V13 统一工具模块
基于 V12，新增：
- 语义化色彩系统（PALETTE）
- 全局布局引擎（SAFE_RECT, SUBTITLE_Y, Z_LAYERS）
- 智能组件工厂（SmartBox, FocusArrow, NeonLine）
- BaseScene 基类（生命周期管理）
"""

from manim import *
import numpy as np
from typing import Optional, Literal
import textwrap
import re

# =============================================================================
# V13 模块一：语义化色彩系统 (Semantic Palette)
# =============================================================================

# V13 新增：语义化色彩字典（解决 #1, #6, #14, #16）
PALETTE = {
    "BG_MAIN": "#0F1115",       # 深炭灰，解决 #1
    "MATH_FUNC": "#3498DB",     # 逻辑蓝 (函数本体)
    "MATH_ERROR": "#F1C40F",    # 琥珀金 (替代刺眼红)，解决 #6, #14
    "DIFF_FWD": "#E67E22",      # 前向色 (橙)，解决 #16
    "DIFF_BWD": "#E74C3C",      # 后向色 (柔和红)
    "DIFF_CTR": "#2ECC71",      # 中心色 (柔和绿)
    "HIGHLIGHT": "#FFFFFF",     # 绝对焦点
    "EDGE": "#F1C40F",          # 边缘检测（琥珀金，替代红色）
}

# 向后兼容：保留旧的颜色常量（映射到PALETTE）
COLOR_CONTINUOUS = PALETTE["MATH_FUNC"]  # 理想数学、连续世界
COLOR_DISCRETE = YELLOW_C                # 工程采样、离散世界（保持原色）
COLOR_DIFF = PALETTE["MATH_ERROR"]       # 微分/变化/高频/边缘（改为琥珀金）
COLOR_SMOOTH = TEAL_C                    # 平滑/保持/低频（保持原色）
COLOR_GHOST = GREY_B                     # 过去的影子（半透明元素）
BG_COLOR = PALETTE["BG_MAIN"]            # 深色背景

# =============================================================================
# V13 模块二：全局布局引擎 (Layout Engine)
# =============================================================================

# 安全区常量
SAFE_RECT = {"width": 13, "height": 7}
# 字幕Y坐标
SUBTITLE_Y = -3.2
# Z轴分层
Z_LAYERS = {
    "Z_BG": -10,
    "Z_CONTENT": 0,
    "Z_FLOAT": 10,
    "Z_UI": 100,
}

# 布局网格系统
LEFT_COL = -3.5
RIGHT_COL = 3.5
GUTTER = 1.0

# 字幕样式配置
SUBTITLE_FONT_SIZE = 28
TITLE_FONT_SIZE = 36
SUBTITLE_COLOR = WHITE
SUBTITLE_BG_OPACITY = 0.75
SUBTITLE_BG_BUFF = 0.22
SUBTITLE_CORNER_RADIUS = 0.06

# 透明度配置
OPACITY_GHOST = 0.2


# =============================================================================
# 安全布局辅助函数：ensure_safe_bounds
# =============================================================================
def ensure_safe_bounds(
    mobject: Mobject,
    max_width: Optional[float] = None,
    max_height: Optional[float] = None,
    scale_factor: float = 0.95,
    tolerance_ratio: float = 0.05,
    conservative: bool = False,
) -> Mobject:
    """
    V13+ 公共工具：确保物体整体落在 SAFE_RECT 安全区内，避免出屏和压到字幕。

    设计原则：
    - 先按宽高等比缩放，再做平移修正；
    - 默认略收缩 (scale_factor<1)，给字幕和边缘留出“呼吸空间”；
    - conservative=True 时只做轻度修正，避免镜头中物体跳动过大。
    """
    if mobject is None:
        return mobject

    # 1) 计算目标宽高
    safe_w = SAFE_RECT["width"]
    safe_h = SAFE_RECT["height"]
    if max_width is None:
        max_width = safe_w * scale_factor
    if max_height is None:
        max_height = safe_h * scale_factor

    # 2) 尺寸缩放（等比）
    width = mobject.width
    height = mobject.height
    need_scale = False
    scale = 1.0

    if width > max_width:
        need_scale = True
        scale = min(scale, max_width / max(width, 1e-6))
    if height > max_height:
        need_scale = True
        scale = min(scale, max_height / max(height, 1e-6))

    if need_scale:
        # 保守模式：限制最大缩放量，避免字号突变
        if conservative:
            scale = max(scale, 0.85)
        mobject.scale(scale)

    # 3) 位置修正：把包围盒推回安全区内
    #    安全区中心在 ORIGIN，宽 safe_w，高 safe_h
    half_w = safe_w / 2
    half_h = safe_h / 2
    tol_w = half_w * tolerance_ratio
    tol_h = half_h * tolerance_ratio

    left, right = -half_w + tol_w, half_w - tol_w
    bottom, top = -half_h + tol_h, half_h - tol_h

    # 字幕禁飞区：略高于 SUBTITLE_Y，避免字幕与主体严重重叠
    subtitle_forbidden = SUBTITLE_Y + 0.4

    bbox = mobject.get_bounding_box()
    (x_min, y_min, _), (x_max, y_max, _) = bbox[0], bbox[2]
    dx = 0.0
    dy = 0.0

    if x_min < left:
        dx = left - x_min
    elif x_max > right:
        dx = right - x_max

    if y_min < bottom:
        dy = bottom - y_min
    elif y_max > top:
        dy = top - y_max

    # 额外：若主体压到字幕禁飞区，则整体上抬
    if y_min < subtitle_forbidden:
        dy = max(dy, subtitle_forbidden - y_min)

    if conservative:
        # 保守模式：只做轻微位置修正，避免明显“跳帧”
        dx *= 0.6
        dy *= 0.6

    if abs(dx) > 1e-6 or abs(dy) > 1e-6:
        mobject.shift(np.array([dx, dy, 0.0]))

    return mobject

# 质量预设
Quality = Literal["low", "med", "high"]
QUALITY_CONFIG = {
    "low": {
        "surface_resolution": (20, 20),
        "grid_size": 8,
        "stroke_width": 2.0,
        "pixel_count": 100,
    },
    "med": {
        "surface_resolution": (30, 30),
        "grid_size": 12,
        "stroke_width": 3.0,
        "pixel_count": 200,
    },
    "high": {
        "surface_resolution": (40, 40),
        "grid_size": 16,
        "stroke_width": 3.5,
        "pixel_count": 300,
    },
}
DEFAULT_QUALITY: Quality = "med"

# =============================================================================
# 字幕管理系统（固定在屏幕底部，支持中英文自动换行）
# =============================================================================

class SubtitleManager:
    """
    字幕管理器：固定在屏幕底部，不随场景移动
    支持中英文关键词时长补偿与智能换行
    """

    def __init__(self, scene: Scene):
        self.scene = scene
        self.current_subtitle: Optional[Text] = None
        self.current_bg: Optional[BackgroundRectangle] = None

    def _calculate_auto_duration(self, text: str) -> float:
        """
        自动计算字幕显示时长（基于文本长度 + 关键词复杂度）
        基础阅读时间：每字 0.25秒，最小 2.5秒
        支持中英文关键词识别
        """
        read_time = len(text) * 0.25
        complex_keywords_zh = ["导数", "泰勒", "算子", "卷积", "离散", "连续", "微积分", "误差", "抵消", "Δx"]
        complex_keywords_en = ["derivative", "Taylor", "operator", "convolution", "discrete", "continuous",
                               "calculus", "error", "cancel", "gradient", "edge detection", "Sobel"]
        if any(x in text for x in complex_keywords_zh + complex_keywords_en):
            read_time += 1.0
        return max(2.5, read_time)

    def _wrap_text_to_fit_width(self, text: str, max_width: float, font_size: float) -> str:
        """
        智能换行：支持中英文混合文本
        """
        char_width_zh = font_size * 0.55
        char_width_en = font_size * 0.3
        avg_char_width = (char_width_zh + char_width_en) / 2
        max_chars_per_line = int(max_width / avg_char_width)
        if len(text) <= max_chars_per_line:
            return text
        if max_chars_per_line <= 0:
            max_chars_per_line = max(10, len(text) // 2)
        # 纯英文用 textwrap
        if re.match(r'^[a-zA-Z0-9\s\.,!?;:()\-"\'-]+$', text):
            return "\n".join(textwrap.wrap(text, width=max_chars_per_line))
        # 中文/混合：按标点/空格分割
        lines = []
        current_line = ""
        segments = re.split(r'([，。！？；：、\s\.\,\!\?\;\:\(\)\-]+)', text)
        for segment in segments:
            if not segment:
                continue
            test_line = current_line + segment
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                if len(segment) > max_chars_per_line:
                    if re.search(r'\s', segment):
                        words = re.split(r'(\s+)', segment)
                        temp_line = ""
                        for word in words:
                            if len(temp_line + word) <= max_chars_per_line:
                                temp_line += word
                            else:
                                if temp_line:
                                    lines.append(temp_line.strip())
                                temp_line = word
                        current_line = temp_line
                    else:
                        for i in range(0, len(segment), max_chars_per_line):
                            lines.append(segment[i:i + max_chars_per_line])
                        current_line = ""
                else:
                    current_line = segment
        if current_line:
            lines.append(current_line.strip())
        result = "\n".join(lines) if lines else text
        max_lines = 3
        if result.count('\n') >= max_lines:
            lines_list = result.split('\n')
            if len(lines_list) > max_lines:
                adjusted_chars = int(len(text) / max_lines) + 2
                return self._wrap_text_to_fit_width(text, max_width, font_size)
        return result

    def show(
        self,
        text: str,
        duration: Optional[float] = None,
        color: str = SUBTITLE_COLOR,
        font_size: float = SUBTITLE_FONT_SIZE,
        wait_after: float = 0.8,
        fade_in: bool = True
    ):
        if duration is None:
            duration = self._calculate_auto_duration(text)
        self.clear(fade_out=True)
        max_subtitle_width = SAFE_RECT["width"] - 1.0
        wrapped_text = self._wrap_text_to_fit_width(text, max_subtitle_width, font_size)
        try:
            subtitle = Text(wrapped_text, font_size=font_size, color=color, font="SimHei")
        except Exception:
            subtitle = Text(wrapped_text, font_size=font_size, color=color)
        if subtitle.width > max_subtitle_width:
            scale_factor = max_subtitle_width / subtitle.width
            scale_factor = max(0.75, scale_factor)
            subtitle.scale(scale_factor)
        subtitle.move_to(ORIGIN + DOWN * 3.2)
        bg = BackgroundRectangle(
            subtitle,
            color=BLACK,
            fill_opacity=SUBTITLE_BG_OPACITY,
            buff=SUBTITLE_BG_BUFF,
            stroke_width=0,
            corner_radius=SUBTITLE_CORNER_RADIUS,
        )
        group = VGroup(bg, subtitle)
        self.scene.add_fixed_in_frame_mobjects(group)
        if fade_in:
            self.scene.play(FadeIn(group, shift=UP * 0.2), run_time=0.6)
        else:
            self.scene.add(group)
        self.current_subtitle = subtitle
        self.current_bg = bg
        if wait_after > 0:
            self.scene.wait(wait_after)

    def clear(self, fade_out: bool = True):
        if self.current_subtitle and self.current_bg:
            if fade_out:
                self.scene.play(
                    FadeOut(VGroup(self.current_bg, self.current_subtitle), shift=DOWN * 0.2),
                    run_time=0.4
                )
            else:
                self.scene.remove(self.current_bg, self.current_subtitle)
            self.current_subtitle = None
            self.current_bg = None

# =============================================================================
# 文本工具函数
# =============================================================================

def safer_text(s: str, font_size: float = 30, color: str = WHITE) -> Text:
    try:
        return Text(s, font_size=font_size, color=color, font="SimHei")
    except Exception:
        return Text(s, font_size=font_size, color=color)

# =============================================================================
# 样式工具函数
# =============================================================================

def make_highlight_rect(
    mobject: Mobject,
    color: str = YELLOW_C,
    buff: float = 0.4,
    corner_radius: float = 0.15,
    stroke_width: float = 3.5
) -> SurroundingRectangle:
    return SurroundingRectangle(
        mobject,
        color=color,
        buff=buff,
        stroke_width=stroke_width,
        corner_radius=corner_radius
    )

def default_axis_config(
    stroke_opacity: float = 0.4,
    stroke_width: float = 1.0,
    stroke_color: str = GREY_C
) -> dict:
    return {
        "stroke_opacity": stroke_opacity,
        "stroke_width": stroke_width,
        "stroke_color": stroke_color,
    }

def default_matrix_style(
    matrix: Matrix,
    gradient_colors: Optional[list] = None
) -> Matrix:
    if gradient_colors:
        matrix.set_color_by_gradient(*gradient_colors)
    return matrix

def gradient_color(start_color: str, end_color: str, alpha: float) -> str:
    return interpolate_color(start_color, end_color, alpha)

# =============================================================================
# 质量工具
# =============================================================================

def get_quality_config(quality: Quality = DEFAULT_QUALITY) -> dict:
    return QUALITY_CONFIG.get(quality, QUALITY_CONFIG[DEFAULT_QUALITY])

# =============================================================================
# 动效助手
# =============================================================================

def lagged_fade_in(
    scene: Scene,
    mobjects: list,
    lag_ratio: float = 0.3,
    shift: np.ndarray = UP * 0.3,
    scale: float = 0.8,
    run_time: float = 2.5
) -> None:
    scene.play(
        LaggedStart(
            *[FadeIn(mobj, shift=shift, scale=scale) for mobj in mobjects],
            lag_ratio=lag_ratio,
            run_time=run_time,
            rate_func=smooth
        )
    )

def apply_wave_effect(
    scene: Scene,
    mobject: Mobject,
    amplitude: float = 0.2,
    run_time: float = 0.6
) -> None:
    scene.play(ApplyWave(mobject, amplitude=amplitude), run_time=run_time)

def wiggle_effect(
    scene: Scene,
    mobject: Mobject,
    scale_value: float = 1.05,
    run_time: float = 1.0
) -> None:
    scene.play(Wiggle(mobject, scale_value=scale_value), run_time=run_time)

# =============================================================================
# 智能组件工厂
# =============================================================================

class SmartBox:
    @staticmethod
    def create(
        mobject: Mobject,
        content_type: str = "text",
        color: str = PALETTE["MATH_ERROR"],
        stroke_width: float = 2.0  # 影院风格：更细的线条
    ) -> SurroundingRectangle:
        buff = 0.15 if content_type == "text" else 0.3
        corner_radius = 0.12 if content_type == "text" else 0.15
        return SurroundingRectangle(
            mobject,
            color=color,
            buff=buff,
            stroke_width=stroke_width,
            corner_radius=corner_radius
        )

class FocusArrow:
    @staticmethod
    def create(
        start_point: np.ndarray,
        end_point: np.ndarray,
        color: str = PALETTE["MATH_ERROR"],
        stroke_width: float = 2.5,
        buff: float = 0.1
    ) -> Arrow:
        return Arrow(
            start_point,
            end_point,
            color=color,
            stroke_width=stroke_width,
            buff=buff
        )

class NeonLine:
    @staticmethod
    def create(
        start: np.ndarray,
        end: np.ndarray,
        color: str = PALETTE["MATH_ERROR"],
        stroke_width: float = 3.0,       # 更细
        stroke_opacity: float = 0.8      # 更柔和
    ) -> Line:
        line = Line(start, end, color=color, stroke_width=stroke_width, stroke_opacity=stroke_opacity)
        shadow = Line(
            start, end,
            color=BLACK,
            stroke_width=stroke_width + 4,   # 更宽但更淡的晕影
            stroke_opacity=0.1
        )
        shadow.move_to(line.get_center() + 0.05 * RIGHT + 0.05 * UP)
        return VGroup(shadow, line)

# =============================================================================
# BaseScene / BaseThreeDScene
# =============================================================================

class BaseScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.math_group = VGroup()
        self.ui_group = VGroup()

    def clear_scene(self, fade_out: bool = True, run_time: float = 1.0):
        if fade_out:
            self.play(
                FadeOut(self.math_group),
                FadeOut(self.ui_group),
                run_time=run_time
            )
        else:
            self.remove(self.math_group, self.ui_group)
        self.math_group = VGroup()
        self.ui_group = VGroup()

    def add_to_math_group(self, *mobjects):
        self.math_group.add(*mobjects)
        self.add(*mobjects)

    def add_to_ui_group(self, *mobjects):
        self.ui_group.add(*mobjects)
        self.add(*mobjects)

class BaseThreeDScene(ThreeDScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.math_group = VGroup()
        self.ui_group = VGroup()

    def clear_scene(self, fade_out: bool = True, run_time: float = 1.0):
        if fade_out:
            self.play(
                FadeOut(self.math_group),
                FadeOut(self.ui_group),
                run_time=run_time
            )
        else:
            self.remove(self.math_group, self.ui_group)
        self.math_group = VGroup()
        self.ui_group = VGroup()

    def add_to_math_group(self, *mobjects):
        self.math_group.add(*mobjects)
        self.add(*mobjects)

    def add_to_ui_group(self, *mobjects):
        self.ui_group.add(*mobjects)
        self.add(*mobjects)


