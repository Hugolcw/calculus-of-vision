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

# V13 新增：安全区常量（解决 #1, #22）
SAFE_RECT = {"width": 13, "height": 7}  # 安全区域尺寸

# V13 新增：字幕Y坐标（解决 #2, #8, #24）
SUBTITLE_Y = -3.2  # 字幕固定Y坐标，避免遮挡

# V13 新增：Z轴分层管理（解决 #2, #8, #24）
Z_LAYERS = {
    "Z_BG": -10,        # 网格
    "Z_CONTENT": 0,     # 图表
    "Z_FLOAT": 10,      # 悬浮标注
    "Z_UI": 100,        # 字幕 (永远在最上层)
}

# V13 新增：布局网格系统（解决 #26）
LEFT_COL = -3.5   # 左侧列（图像区域）
RIGHT_COL = 3.5   # 右侧列（算式区域）
GUTTER = 1.0      # 中间隔离带

# 字幕样式配置
SUBTITLE_FONT_SIZE = 28
TITLE_FONT_SIZE = 36
SUBTITLE_COLOR = WHITE
SUBTITLE_BG_OPACITY = 0.75     # 与 V11 保持一致
SUBTITLE_BG_BUFF = 0.22        # 字幕背景内边距
SUBTITLE_CORNER_RADIUS = 0.06  # 字幕背景圆角

# 透明度配置
OPACITY_GHOST = 0.2            # 幽灵元素透明度

# 质量预设（控制渲染成本）
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

# 默认质量档位
DEFAULT_QUALITY: Quality = "med"


# =============================================================================
# 字幕管理系统（融合 V11 fixed_in_frame + V10 自动时长）
# =============================================================================

class SubtitleManager:
    """
    字幕管理器：固定在屏幕底部，不随场景移动
    融合 V11 的 fixed_in_frame_mobjects 稳定性和 V10 的自动时长计算
    """
    
    def __init__(self, scene: Scene):
        self.scene = scene
        self.current_subtitle: Optional[Text] = None
        self.current_bg: Optional[BackgroundRectangle] = None
    
    def _calculate_auto_duration(self, text: str) -> float:
        """
        自动计算字幕显示时长（基于文本长度 + 关键词复杂度）
        每个字符约 0.12 秒，最小 2 秒，最大 6 秒
        """
        base_time = len(text) * 0.12
        # 复杂概念需要更多时间
        complex_keywords = ["导数", "泰勒", "算子", "卷积", "离散", "连续", "微积分", "误差", "抵消"]
        complexity_bonus = sum(1 for keyword in complex_keywords if keyword in text) * 0.3
        final_time = base_time + complexity_bonus
        return max(2.0, min(final_time, 6.0))
    
    def show(
        self,
        text: str,
        duration: Optional[float] = None,
        color: str = SUBTITLE_COLOR,
        font_size: float = SUBTITLE_FONT_SIZE,
        wait_after: float = 0.8,
        fade_in: bool = True
    ):
        """
        显示字幕（固定在屏幕底部）
        
        参数:
        - text: 字幕文本
        - duration: 字幕显示时长（None 则自动计算）
        - color: 字幕颜色
        - font_size: 字号
        - wait_after: 字幕显示后的等待时间
        - fade_in: 是否淡入（False 则直接显示）
        """
        # 计算显示时长
        if duration is None:
            duration = self._calculate_auto_duration(text)
        
        # 清除旧字幕
        self.clear(fade_out=True)
        
        # 创建字幕（使用 SimHei 字体，失败则回退）
        try:
            subtitle = Text(text, font_size=font_size, color=color, font="SimHei")
        except Exception:
            subtitle = Text(text, font_size=font_size, color=color)
        
        # V13 修复：使用固定Y坐标，避免遮挡
        subtitle.move_to(ORIGIN + DOWN * 3.2)  # 对应 SUBTITLE_Y = -3.2
        
        # 创建字幕背景（半透明、圆角）
        bg = BackgroundRectangle(
            subtitle,
            color=BLACK,
            fill_opacity=SUBTITLE_BG_OPACITY,
            buff=SUBTITLE_BG_BUFF,
            stroke_width=0,
            corner_radius=SUBTITLE_CORNER_RADIUS,
        )
        
        group = VGroup(bg, subtitle)
        
        # 使用 fixed_in_frame_mobjects 确保字幕不随相机移动（V11 方案）
        self.scene.add_fixed_in_frame_mobjects(group)
        
        # 淡入动画
        if fade_in:
            self.scene.play(
                FadeIn(group, shift=UP * 0.2),
                run_time=0.6
            )
        else:
            self.scene.add(group)
        
        # 保存引用
        self.current_subtitle = subtitle
        self.current_bg = bg
        
        # 等待时间
        if wait_after > 0:
            self.scene.wait(wait_after)
    
    def clear(self, fade_out: bool = True):
        """清除字幕"""
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
    """
    安全的文本创建函数（SimHei 字体兜底）
    与 V11 保持一致
    """
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
    """
    创建高亮框（统一样式：圆角、合适间距、柔和颜色）
    符合审美指南要求
    """
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
    """
    默认坐标轴配置（辅助元素降亮度，符合审美指南）
    """
    return {
        "stroke_opacity": stroke_opacity,
        "stroke_width": stroke_width,
        "stroke_color": stroke_color,
    }


def default_matrix_style(
    matrix: Matrix,
    gradient_colors: Optional[list] = None
) -> Matrix:
    """
    默认矩阵样式（支持渐变配色）
    """
    if gradient_colors:
        matrix.set_color_by_gradient(*gradient_colors)
    return matrix


def gradient_color(start_color: str, end_color: str, alpha: float) -> str:
    """
    颜色插值工具（用于平滑过渡）
    
    参数:
    - start_color: 起始颜色
    - end_color: 结束颜色
    - alpha: 插值系数（0-1）
    
    返回: 插值后的颜色
    """
    return interpolate_color(start_color, end_color, alpha)


# =============================================================================
# 质量预设工具
# =============================================================================

def get_quality_config(quality: Quality = DEFAULT_QUALITY) -> dict:
    """获取质量配置"""
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
    """
    批量淡入动画（统一缓动 smooth）
    """
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
    """
    ApplyWave 动效包装（用于几何抵消、爆炸等效果）
    符合方案要求的常用动效
    """
    scene.play(ApplyWave(mobject, amplitude=amplitude), run_time=run_time)


def wiggle_effect(
    scene: Scene,
    mobject: Mobject,
    scale_value: float = 1.05,
    run_time: float = 1.0
) -> None:
    """
    Wiggle 动效包装（用于强调、抖动效果）
    符合方案要求的常用动效
    """
    scene.play(Wiggle(mobject, scale_value=scale_value), run_time=run_time)


# =============================================================================
# V13 模块三：智能组件工厂 (Smart Components)
# =============================================================================

class SmartBox:
    """
    V13 新增：智能高亮框（解决 #12）
    自动计算 Padding，统一圆角，根据内容类型自适应
    """
    
    @staticmethod
    def create(
        mobject: Mobject,
        content_type: str = "text",  # "text" 或 "image"
        color: str = PALETTE["MATH_ERROR"],
        stroke_width: float = 3.5
    ) -> SurroundingRectangle:
        """
        创建智能高亮框
        
        参数:
        - mobject: 要框选的对象
        - content_type: 内容类型（"text"=0.15, "image"=0.3）
        - color: 框颜色
        - stroke_width: 线宽
        """
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
    """
    V13 新增：焦点箭头（解决 #9）
    替代黑框，从侧面指入，带呼吸效果
    """
    
    @staticmethod
    def create(
        start_point: np.ndarray,
        end_point: np.ndarray,
        color: str = PALETTE["MATH_ERROR"],
        stroke_width: float = 2.5,
        buff: float = 0.1
    ) -> Arrow:
        """
        创建焦点箭头
        
        参数:
        - start_point: 起始点
        - end_point: 终点
        - color: 箭头颜色
        - stroke_width: 线宽
        - buff: 缓冲距离
        """
        return Arrow(
            start_point,
            end_point,
            color=color,
            stroke_width=stroke_width,
            buff=buff
        )
    
    @staticmethod
    def create_breathing_effect(scene: Scene, arrow: Arrow, run_time: float = 1.0):
        """
        添加呼吸效果（轻微缩放动画）
        """
        scene.play(
            arrow.animate.scale(1.1),
            arrow.animate.scale(1.0),
            run_time=run_time,
            rate_func=there_and_back
        )


class NeonLine:
    """
    V13 新增：霓虹线（解决 #14）
    自带 stroke_width=4 和微弱 shadow
    """
    
    @staticmethod
    def create(
        start: np.ndarray,
        end: np.ndarray,
        color: str = PALETTE["MATH_ERROR"],
        stroke_width: float = 4.0,
        stroke_opacity: float = 0.9
    ) -> Line:
        """
        创建霓虹线
        
        参数:
        - start: 起始点
        - end: 终点
        - color: 线条颜色
        - stroke_width: 线宽（默认4.0）
        - stroke_opacity: 透明度
        """
        line = Line(start, end, color=color, stroke_width=stroke_width, stroke_opacity=stroke_opacity)
        # 添加微弱阴影效果（通过叠加半透明线条实现）
        shadow = Line(start, end, color=BLACK, stroke_width=stroke_width + 1, stroke_opacity=0.2)
        shadow.move_to(line.get_center() + 0.05 * RIGHT + 0.05 * UP)
        return VGroup(shadow, line)


# =============================================================================
# V13 模块四：BaseScene 基类 (Lifecycle Management)
# =============================================================================

class BaseScene(Scene):
    """
    V13 新增：基础场景类（解决 #13, #22）
    提供生命周期管理和组管理功能
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 组管理：所有数学对象和UI对象分别管理
        self.math_group = VGroup()  # 所有数学对象
        self.ui_group = VGroup()    # 所有UI对象
    
    def clear_scene(self, fade_out: bool = True, run_time: float = 1.0):
        """
        清除场景（解决 #13, #22）
        转场时显式清除所有对象，避免残留
        """
        if fade_out:
            self.play(
                FadeOut(self.math_group),
                FadeOut(self.ui_group),
                run_time=run_time
            )
        else:
            self.remove(self.math_group, self.ui_group)
        # 清空组
        self.math_group = VGroup()
        self.ui_group = VGroup()
    
    def add_to_math_group(self, *mobjects):
        """添加对象到数学组"""
        self.math_group.add(*mobjects)
        self.add(*mobjects)
    
    def add_to_ui_group(self, *mobjects):
        """添加对象到UI组"""
        self.ui_group.add(*mobjects)
        self.add(*mobjects)


class BaseThreeDScene(ThreeDScene):
    """
    V13 新增：3D场景基类
    继承 BaseScene 的生命周期管理功能
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.math_group = VGroup()
        self.ui_group = VGroup()
    
    def clear_scene(self, fade_out: bool = True, run_time: float = 1.0):
        """清除场景"""
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
        """添加对象到数学组"""
        self.math_group.add(*mobjects)
        self.add(*mobjects)
    
    def add_to_ui_group(self, *mobjects):
        """添加对象到UI组"""
        self.ui_group.add(*mobjects)
        self.add(*mobjects)

