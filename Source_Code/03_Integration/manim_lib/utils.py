"""
通用工具函数，已去版本化并自包含。
"""

from typing import Optional, Literal
import numpy as np
import textwrap
import re
import sys
from manim import (
    Text,
    SurroundingRectangle,
    Matrix,
    Scene,
    Mobject,
    MathTex as _OriginalMathTex,
    interpolate_color,
    LaggedStart,
    FadeIn,
    ApplyWave,
    Wiggle,
    UP,
    smooth,
    YELLOW_C,
    TEAL_C,
    GREY_C,
)

from manim_lib.layout import SAFE_RECT

# =============================================================================
# 文本与样式工具
# =============================================================================

def safer_text(s: str, font_size: float = 30, color= "WHITE") -> Text:
    # Emoji 在多数 Linux 环境下字体缺失，给出警告，避免“空白/透明”渲染
    if re.search(r'[\U0001F300-\U0001FAFF]', s):
        print("[warn] 检测到 Emoji，Linux 默认字体可能无法渲染，建议改用文字或几何图形替代。", file=sys.stderr)
    try:
        return Text(s, font_size=font_size, color=color, font="SimHei")
    except Exception:
        return Text(s, font_size=font_size, color=color)


def make_highlight_rect(
    mobject: Mobject,
    color=YELLOW_C,
    buff: float = 0.4,
    corner_radius: float = 0.15,
    stroke_width: float = 3.5,
) -> SurroundingRectangle:
    return SurroundingRectangle(
        mobject,
        color=color,
        buff=buff,
        stroke_width=stroke_width,
        corner_radius=corner_radius,
    )


# =============================================================================
# 质量配置
# =============================================================================
Quality = Literal["low", "med", "high"]
QUALITY_CONFIG = {
    "low": {"surface_resolution": (20, 20), "grid_size": 8, "stroke_width": 2.0, "pixel_count": 100},
    "med": {"surface_resolution": (30, 30), "grid_size": 12, "stroke_width": 3.0, "pixel_count": 200},
    "high": {"surface_resolution": (40, 40), "grid_size": 16, "stroke_width": 3.5, "pixel_count": 300},
}
DEFAULT_QUALITY: Quality = "med"

SUBTITLE_FONT_SIZE = 28
TITLE_FONT_SIZE = 36
SUBTITLE_COLOR = "WHITE"
SUBTITLE_BG_OPACITY = 0.75
SUBTITLE_BG_BUFF = 0.22
SUBTITLE_CORNER_RADIUS = 0.06
OPACITY_GHOST = 0.2


def get_quality_config(quality: Quality = DEFAULT_QUALITY) -> dict:
    return QUALITY_CONFIG.get(quality, QUALITY_CONFIG[DEFAULT_QUALITY])


# =============================================================================
# 颜色 / 矩阵工具
# =============================================================================
def default_matrix_style(matrix: Matrix, gradient_colors: Optional[list] = None) -> Matrix:
    if gradient_colors:
        matrix.set_color_by_gradient(*gradient_colors)
    return matrix


def gradient_color(start_color, end_color, alpha: float):
    return interpolate_color(start_color, end_color, alpha)


# =============================================================================
# 动效助手
# =============================================================================
def lagged_fade_in(
    scene: Scene,
    mobjects: list,
    lag_ratio: float = 0.3,
    shift: np.ndarray = UP * 0.3,
    scale: float = 0.8,
    run_time: float = 2.5,
) -> None:
    scene.play(
        LaggedStart(
            *[FadeIn(mobj, shift=shift, scale=scale) for mobj in mobjects],
            lag_ratio=lag_ratio,
            run_time=run_time,
            rate_func=smooth,
        )
    )


def apply_wave_effect(scene: Scene, mobject: Mobject, amplitude: float = 0.2, run_time: float = 0.6) -> None:
    scene.play(ApplyWave(mobject, amplitude=amplitude), run_time=run_time)


def wiggle_effect(scene: Scene, mobject: Mobject, scale_value: float = 1.05, run_time: float = 1.0) -> None:
    scene.play(Wiggle(mobject, scale_value=scale_value), run_time=run_time)


# =============================================================================
# 安全 MathTex 工具：防止中文/Emoji 直接进 MathTex 触发 LaTeX 报错
# =============================================================================
def _contains_cjk_or_emoji(s: str) -> bool:
    return bool(re.search(r'[\u4e00-\u9fff]', s) or re.search(r'[\U0001F300-\U0001FAFF]', s))


def safe_mathtex(*tex_strings: str, **kwargs):
    """
    封装 MathTex：在调用前检测中文/Emoji，提前抛错并给出指引。
    用法：
        safe_mathtex("x^2", r"= y^2")  # 安全
        safe_mathtex("\\text{中文}")   # 会抛错，提示改用 Text 组合。
    """
    for s in tex_strings:
        if _contains_cjk_or_emoji(s):
            raise ValueError(
                "检测到中文或 Emoji 传入 MathTex。请改用 Text 渲染中文，或用 VGroup 组合 Text 与 MathTex。"
            )
    return _OriginalMathTex(*tex_strings, **kwargs)


def MathTexSafe(*tex_strings: str, **kwargs):
    """MathTex 的安全别名，便于旧代码替换。"""
    return safe_mathtex(*tex_strings, **kwargs)


__all__ = [
    "safer_text",
    "make_highlight_rect",
    "get_quality_config",
    "apply_wave_effect",
    "default_matrix_style",
    "gradient_color",
    "lagged_fade_in",
    "wiggle_effect",
    "QUALITY_CONFIG",
    "DEFAULT_QUALITY",
    "Quality",
    "SUBTITLE_FONT_SIZE",
    "TITLE_FONT_SIZE",
    "SUBTITLE_COLOR",
    "SUBTITLE_BG_OPACITY",
    "SUBTITLE_BG_BUFF",
    "SUBTITLE_CORNER_RADIUS",
    "OPACITY_GHOST",
    "safe_mathtex",
    "MathTexSafe",
]

