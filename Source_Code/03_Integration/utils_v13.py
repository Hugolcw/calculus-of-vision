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
    V14 增强：支持自动换行和宽度检查，防止字幕超出屏幕
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
        # 基础阅读时间：每字 0.25秒
        read_time = len(text) * 0.25
        
        # 认知负荷补偿（复杂概念需要更多时间）
        # 中文关键词
        complex_keywords_zh = ["导数", "泰勒", "算子", "卷积", "离散", "连续", "微积分", "误差", "抵消", "Δx"]
        # 英文关键词
        complex_keywords_en = ["derivative", "Taylor", "operator", "convolution", "discrete", "continuous", 
                              "calculus", "error", "cancel", "gradient", "edge detection", "Sobel"]
        
        if any(x in text for x in complex_keywords_zh + complex_keywords_en):
            read_time += 1.0
        
        # 最小停留 2.5秒
        return max(2.5, read_time)
    
    def _wrap_text_to_fit_width(self, text: str, max_width: float, font_size: float) -> str:
        """
        智能换行：支持中英文混合文本
        
        参数:
        - text: 原始文本
        - max_width: 最大宽度（Manim 单位）
        - font_size: 字号
        
        返回: 换行后的文本（用 \n 分隔）
        """
        # 估算每行字符数（基于字符宽度）
        # 中文字符宽度约为 font_size * 0.55
        # 英文字符宽度约为 font_size * 0.3
        char_width_zh = font_size * 0.55
        char_width_en = font_size * 0.3
        
        # 计算每行大约能容纳的字符数（使用保守估算）
        # 假设文本是中文和英文混合，取平均值
        avg_char_width = (char_width_zh + char_width_en) / 2
        max_chars_per_line = int(max_width / avg_char_width)
        
        # 如果文本本身就不长，不需要换行
        if len(text) <= max_chars_per_line:
            return text
        
        if max_chars_per_line <= 0:
            max_chars_per_line = max(10, len(text) // 2)  # 最小行宽
        
        # 对于纯英文文本，使用 textwrap（效果更好）
        # 支持英文标点符号，包括单引号和双引号
        if re.match(r'^[a-zA-Z0-9\s\.,!?;:()\-"\']+$', text):
            return "\n".join(textwrap.wrap(text, width=max_chars_per_line))
        
        # 对于中文或中英文混合，使用智能分割
        lines = []
        current_line = ""
        
        # 按标点符号和空格分割（保留分隔符）
        # 支持中英文标点：，。！？；：、\s 和英文标点
        segments = re.split(r'([，。！？；：、\s\.\,\!\?\;\:\(\)\-]+)', text)
        
        for segment in segments:
            if not segment:
                continue
            
            # 如果当前行加上新段落后不超过限制
            test_line = current_line + segment
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                # 需要换行
                if current_line:
                    lines.append(current_line.strip())
                
                # 如果单个段落就超过限制，尝试在段落内换行
                if len(segment) > max_chars_per_line:
                    # 对于长段落，尝试在合适的位置分割
                    # 优先在空格处分割（英文单词）
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
                        # 对于没有空格的长段落（如长中文句子），强制分割
                        for i in range(0, len(segment), max_chars_per_line):
                            lines.append(segment[i:i + max_chars_per_line])
                        current_line = ""
                else:
                    current_line = segment
        
        if current_line:
            lines.append(current_line.strip())
        
        result = "\n".join(lines) if lines else text
        
        # 限制最大行数，避免过度换行导致字幕区域占用过大
        max_lines = 3
        if result.count('\n') >= max_lines:
            lines_list = result.split('\n')
            if len(lines_list) > max_lines:
                # 如果行数过多，适当增加每行字符数并重新换行
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
        """
        显示字幕（固定在屏幕底部，自动换行防止超出屏幕）
        
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
        
        # V14 增强：自动换行以适应安全区域宽度
        # 字幕最大宽度 = 安全区域宽度 - 左右边距
        max_subtitle_width = SAFE_RECT["width"] - 1.0  # 留出左右边距
        wrapped_text = self._wrap_text_to_fit_width(text, max_subtitle_width, font_size)
        
        # 创建字幕（使用 SimHei 字体，失败则回退）
        try:
            subtitle = Text(wrapped_text, font_size=font_size, color=color, font="SimHei")
        except Exception:
            subtitle = Text(wrapped_text, font_size=font_size, color=color)
        
        # V14 增强：安全缩放逻辑（核心修复）
        # 如果换行后依然超宽，自动缩小字号
        if subtitle.width > max_subtitle_width:
            scale_factor = max_subtitle_width / subtitle.width
            # 最小缩放比例为 0.75，保证可读性
            scale_factor = max(0.75, scale_factor)
            subtitle.scale(scale_factor)
        
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


def ensure_safe_bounds(
    mobject: Mobject, 
    max_width: Optional[float] = None, 
    max_height: Optional[float] = None, 
    scale_factor: float = 0.98,
    tolerance: float = 0.1,
    conservative: bool = True
) -> Mobject:
    """
    V14 新增：确保对象在安全区域内，防止超出屏幕（保守策略）
    
    参数:
    - mobject: 要检查的对象
    - max_width: 最大宽度（None 则使用 SAFE_RECT["width"]）
    - max_height: 最大高度（None 则使用 SAFE_RECT["height"]）
    - scale_factor: 缩放因子（0.98 表示留 2% 边距，更保守）
    - tolerance: 容差比例（只有超出这个比例时才调整，默认 10%）
    - conservative: 保守模式（True 时只在明显超出时才缩放，避免过度缩小）
    
    返回: 调整后的对象
    """
    if max_width is None:
        max_width = SAFE_RECT["width"] * scale_factor
    if max_height is None:
        max_height = SAFE_RECT["height"] * scale_factor
    
    # 保守策略：只有在明显超出时才缩放（避免过度缩小影响可读性）
    width_ratio = mobject.width / max_width
    height_ratio = mobject.height / max_height
    
    if conservative:
        # 保守模式：只有超出 5% 以上才缩放，且最小缩放比例为 0.85（保证可读性）
        min_scale = 0.85
        if width_ratio > 1.05:  # 超出 5%
            scale_w = max(min_scale, max_width / mobject.width)
            mobject.scale(scale_w)
            # 重新计算比例
            width_ratio = mobject.width / max_width
        
        if height_ratio > 1.05:  # 超出 5%
            scale_h = max(min_scale, max_height / mobject.height)
            mobject.scale(scale_h)
    else:
        # 标准模式：超出就缩放
        if mobject.width > max_width:
            scale_w = max_width / mobject.width
            mobject.scale(scale_w)
        
        if mobject.height > max_height:
            scale_h = max_height / mobject.height
            mobject.scale(scale_h)
    
    # 检查位置是否超出边界（使用更大的边界，允许轻微超出）
    margin = 0.3  # 允许轻微超出 0.3 单位
    left_bound = -SAFE_RECT["width"] / 2 - margin
    right_bound = SAFE_RECT["width"] / 2 + margin
    top_bound = SAFE_RECT["height"] / 2 + margin
    bottom_bound = -SAFE_RECT["height"] / 2 - margin
    
    # 获取边界框（使用 get_bounding_box 或手动计算）
    try:
        # 尝试使用 get_bounding_box（如果可用）
        bbox = mobject.get_bounding_box()
        min_x, min_y, _ = bbox[0]
        max_x, max_y, _ = bbox[1]
    except AttributeError:
        # 回退方案：使用 get_critical_point 估算
        center = mobject.get_center()
        half_width = mobject.width / 2
        half_height = mobject.height / 2
        min_x = center[0] - half_width
        max_x = center[0] + half_width
        min_y = center[1] - half_height
        max_y = center[1] + half_height
    
    # 保守的位置调整：只在明显超出时才移动（避免破坏原有布局）
    position_tolerance = 0.2  # 允许轻微超出 0.2 单位
    
    # 如果明显超出左边界（超出容差），向右移动
    if min_x < left_bound - position_tolerance:
        shift_amount = left_bound - min_x + 0.1
        mobject.shift(RIGHT * shift_amount)
        # 重新计算边界
        center = mobject.get_center()
        half_width = mobject.width / 2
        max_x = center[0] + half_width
    
    # 如果明显超出右边界（超出容差），向左移动
    if max_x > right_bound + position_tolerance:
        shift_amount = max_x - right_bound + 0.1
        mobject.shift(LEFT * shift_amount)
        # 重新计算边界
        center = mobject.get_center()
        half_width = mobject.width / 2
        min_x = center[0] - half_width
    
    # 如果明显超出上边界（超出容差），向下移动
    if max_y > top_bound + position_tolerance:
        shift_amount = max_y - top_bound + 0.1
        mobject.shift(DOWN * shift_amount)
        # 重新计算边界
        center = mobject.get_center()
        half_height = mobject.height / 2
        min_y = center[1] - half_height
    
    # 如果明显超出下边界（超出容差），向上移动（但要避免与字幕重叠）
    if min_y < bottom_bound - position_tolerance:
        # 字幕在 -3.2，所以下边界应该高于 -3.5
        safe_bottom = max(bottom_bound, SUBTITLE_Y + 0.5)
        if min_y < safe_bottom - position_tolerance:
            shift_amount = safe_bottom - min_y + 0.1
            mobject.shift(UP * shift_amount)
    
    return mobject


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

