"""
Lightweight facade package for the Sobel project.

This mirrors the architecture guide by gathering the stable interfaces from
the legacy utils_v15 module into a package-style namespace. Code can import
from `manim_lib` without referencing versioned filenames, easing future
refactors toward a full shared library.
"""

from .core import (
    BaseScene,
    BaseThreeDScene,
    NarrativeHelper,
    PacingController,
    MinimalismHelper,
    LayerManager,
    slow_wait,
    slow_play,
    ask_question,
    show_conflict,
    show_solution,
    show_validation,
)
from .layout import (
    ensure_safe_bounds,
    SAFE_RECT,
    SUBTITLE_Y,
    Z_LAYERS,
    LEFT_COL,
    RIGHT_COL,
    GUTTER,
    default_axis_config,
)
from .style import (
    PALETTE,
    COLOR_CONTINUOUS,
    COLOR_DISCRETE,
    COLOR_DIFF,
    COLOR_SMOOTH,
    BG_COLOR,
)
from .components import (
    SubtitleManager,
    SmartBox,
    FocusArrow,
    NeonLine,
)
from .utils import (
    safer_text,
    make_highlight_rect,
    get_quality_config,
    apply_wave_effect,
    default_matrix_style,
    gradient_color,
    lagged_fade_in,
    wiggle_effect,
    QUALITY_CONFIG,
    DEFAULT_QUALITY,
    Quality,
    SUBTITLE_FONT_SIZE,
    TITLE_FONT_SIZE,
    SUBTITLE_COLOR,
    SUBTITLE_BG_OPACITY,
    SUBTITLE_BG_BUFF,
    SUBTITLE_CORNER_RADIUS,
    OPACITY_GHOST,
)

__all__ = [
    # core
    "BaseScene",
    "BaseThreeDScene",
    "NarrativeHelper",
    "PacingController",
    "MinimalismHelper",
    "LayerManager",
    "slow_wait",
    "slow_play",
    "ask_question",
    "show_conflict",
    "show_solution",
    "show_validation",
    # layout
    "ensure_safe_bounds",
    "SAFE_RECT",
    "SUBTITLE_Y",
    "Z_LAYERS",
    "LEFT_COL",
    "RIGHT_COL",
    "GUTTER",
    "default_axis_config",
    # style
    "PALETTE",
    "COLOR_CONTINUOUS",
    "COLOR_DISCRETE",
    "COLOR_DIFF",
    "COLOR_SMOOTH",
    "BG_COLOR",
    # components
    "SubtitleManager",
    "SmartBox",
    "FocusArrow",
    "NeonLine",
    # utils
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
    "MathTexSafe",
    "safe_mathtex",
]

# 项目版本标识（与 pyproject 同步维护）
__version__ = "0.1.0"

