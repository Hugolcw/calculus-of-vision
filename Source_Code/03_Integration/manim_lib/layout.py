"""
布局与空间辅助（去版本化）。
包含安全区常量、网格、以及基于 v15 热修的安全边界守护
（使用 .width/.height，避免 get_bounding_box 依赖）。
"""

from manim import Mobject, GREY_C
import numpy as np

# 安全区与布局常量
SAFE_RECT = {"width": 13, "height": 7}
SUBTITLE_Y = -3.2
Z_LAYERS = {
    "Z_BG": -10,
    "Z_CONTENT": 0,
    "Z_FLOAT": 10,
    "Z_UI": 100,
}
LEFT_COL = -3.5
RIGHT_COL = 3.5
GUTTER = 1.0


def default_axis_config(
    stroke_opacity: float = 0.8,
    stroke_width: float = 1.0,
    stroke_color: str = GREY_C,
) -> dict:
    """影院风格坐标轴默认配置：轻量线条，降低视觉负担。"""
    return {
        "stroke_opacity": stroke_opacity,
        "stroke_width": stroke_width,
        "stroke_color": stroke_color,
    }


def ensure_safe_bounds(mobject: Mobject, conservative: bool = False, scale_factor: float = 0.95):
    """确保物体落在 SAFE_RECT 内，使用 .width/.height 以兼容新版 Manim。"""
    safe_w = SAFE_RECT.get("width", 13.0)
    safe_h = SAFE_RECT.get("height", 7.0)

    if conservative:
        safe_w *= 0.9
        safe_h *= 0.9

    current_w = mobject.width
    current_h = mobject.height
    if current_w == 0 or current_h == 0:
        return mobject

    scale_x = safe_w / current_w if current_w > safe_w else 1.0
    scale_y = safe_h / current_h if current_h > safe_h else 1.0
    min_scale = min(scale_x, scale_y)

    if min_scale < 1.0:
        mobject.scale(min_scale * scale_factor)

    return mobject


__all__ = [
    "ensure_safe_bounds",
    "SAFE_RECT",
    "SUBTITLE_Y",
    "Z_LAYERS",
    "LEFT_COL",
    "RIGHT_COL",
    "GUTTER",
    "default_axis_config",
]

