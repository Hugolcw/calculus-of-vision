"""
可复用视觉组件（去版本化）。
"""

from typing import Optional
from manim import (
    Scene,
    Text,
    VGroup,
    BackgroundRectangle,
    SurroundingRectangle,
    Arrow,
    Line,
    BLACK,
    GREY_C,
    WHITE,
    FadeIn,
    Create,
    Mobject,
    ORIGIN,
    DOWN,
)

from manim_lib.style import PALETTE
from manim_lib.layout import SAFE_RECT


class SubtitleManager:
    """
    影院级字幕管理器：智能断行、稳定背景条、底部固定。
    """

    def __init__(self, scene: Scene):
        self.scene = scene
        self.current_subtitle: Optional[Mobject] = None
        self.current_bg: Optional[Mobject] = None

    def _smart_break_text(self, text: str, max_chars: int = 24) -> str:
        if len(text) <= max_chars:
            return text
        mid = len(text) // 2
        search_range = range(int(len(text) * 0.3), int(len(text) * 0.7))
        best_split_idx = -1
        min_dist = float("inf")
        puncts = ["，", "：", "；", ",", ":", ";", "。", "！", "!", "？", "?"]
        for i in search_range:
            char = text[i]
            if char in puncts:
                dist = abs(i - mid)
                if dist < min_dist:
                    min_dist = dist
                    best_split_idx = i + 1
        if best_split_idx != -1:
            return text[:best_split_idx] + "\n" + text[best_split_idx:]
        # 兜底：硬分行
        return text[:mid] + "\n" + text[mid:]

    def _calculate_duration(self, text: str) -> float:
        read_time = len(text) * 0.25
        complex_keywords = ["导数", "泰勒", "Δx", "微积分", "derivative", "Taylor", "calculus", "gradient", "edge"]
        if any(k in text for k in complex_keywords):
            read_time += 1.0
        return max(3.0, read_time)

    def show(
        self,
        text: str,
        duration: Optional[float] = None,
        color: str = WHITE,
        font_size: float = 28,
        wait_after: float = None,
        fade_in: bool = True,
    ):
        from manim_lib.core import PacingController  # lazy import to avoid cycle

        formatted = self._smart_break_text(text)
        try:
            subtitle = Text(formatted, font_size=font_size, color=color, font="SimHei", line_spacing=1.2)
        except Exception:
            subtitle = Text(formatted, font_size=font_size, color=color, line_spacing=1.2)

        max_w = SAFE_RECT["width"] - 1.0
        if subtitle.width > max_w:
            scale_factor = max_w / subtitle.width
            scale_factor = max(0.85, scale_factor)
            subtitle.scale(scale_factor)

        subtitle.move_to(ORIGIN)
        subtitle.to_edge(DOWN, buff=0.5)

        bg = BackgroundRectangle(
            subtitle,
            color=BLACK,
            fill_opacity=0.8,
            buff=0.2,
            stroke_width=0,
            corner_radius=0.1,
        )
        if bg.width < 8.0:
            bg.stretch_to_fit_width(8.0)

        group = VGroup(bg, subtitle)
        self.scene.add_fixed_in_frame_mobjects(group)

        if fade_in:
            self.scene.play(FadeIn(group, shift=DOWN * -0.1), run_time=0.5)
        else:
            self.scene.add(group)

        self.current_subtitle = subtitle
        self.current_bg = bg

        if duration is None:
            duration = self._calculate_duration(text)
        if wait_after is None:
            PacingController.slow_wait(self.scene, 0.5)
        else:
            PacingController.slow_wait(self.scene, wait_after)

    def clear(self, fade_out: bool = True):
        if self.current_subtitle and self.current_bg:
            group = VGroup(self.current_bg, self.current_subtitle)
            if fade_out:
                self.scene.play(FadeIn(group, shift=DOWN * 0.0).reverse(), run_time=0.3)  # 简单淡出
            else:
                self.scene.remove(group)
            self.current_subtitle = None
            self.current_bg = None


class SmartBox:
    @staticmethod
    def create(
        mobject: Mobject,
        content_type: str = "text",
        color: str = PALETTE["MATH_ERROR"],
        stroke_width: float = 2.0,
    ) -> SurroundingRectangle:
        buff = 0.15 if content_type == "text" else 0.3
        corner_radius = 0.12 if content_type == "text" else 0.15
        return SurroundingRectangle(
            mobject,
            color=color,
            buff=buff,
            stroke_width=stroke_width,
            corner_radius=corner_radius,
        )


class FocusArrow:
    @staticmethod
    def create(
        start_point,
        end_point,
        color: str = PALETTE["MATH_ERROR"],
        stroke_width: float = 2.5,
        buff: float = 0.1,
    ) -> Arrow:
        return Arrow(start_point, end_point, color=color, stroke_width=stroke_width, buff=buff)


class NeonLine:
    @staticmethod
    def create(
        start,
        end,
        color: str = PALETTE["MATH_ERROR"],
        stroke_width: float = 3.0,
        stroke_opacity: float = 0.8,
    ) -> Line:
        line = Line(start, end, color=color, stroke_width=stroke_width, stroke_opacity=stroke_opacity)
        shadow = Line(
            start,
            end,
            color=BLACK,
            stroke_width=stroke_width + 4,
            stroke_opacity=0.1,
        )
        shadow.move_to(line.get_center() + 0.05 * (DOWN * -1))  # subtle offset
        return VGroup(shadow, line)


__all__ = ["SubtitleManager", "SmartBox", "FocusArrow", "NeonLine"]

