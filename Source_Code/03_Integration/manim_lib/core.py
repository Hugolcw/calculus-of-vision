"""
核心场景抽象与叙事辅助（去版本化）。
"""

from typing import Optional, List
from manim import (
    Scene,
    ThreeDScene,
    VGroup,
    FadeOut,
    Write,
    Create,
    Mobject,
)

from manim_lib.style import PALETTE, BG_COLOR
from manim_lib.components import SubtitleManager, SmartBox
from manim_lib.layout import default_axis_config


# =============================================================================
# 基础场景
# =============================================================================
class BaseScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.math_group = VGroup()
        self.ui_group = VGroup()

    def clear_scene(self, fade_out: bool = True, run_time: float = 1.0):
        if fade_out:
            self.play(FadeOut(self.math_group), FadeOut(self.ui_group), run_time=run_time)
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

    # V15 增强：便捷分层添加
    def add_background(self, mobject: Mobject, opacity: float = 0.2):
        from manim_lib.core import LayerManager  # local import to avoid cycle

        LayerManager.to_background(mobject, opacity=opacity)
        self.add(mobject)
        return mobject

    def add_active(self, mobject: Mobject, layer: int = None):
        from manim_lib.core import LayerManager  # local import to avoid cycle

        target_layer = LayerManager.L_ACTIVE if layer is None else layer
        LayerManager.set_layer(mobject, target_layer)
        mobject.set_opacity(1.0)
        self.add(mobject)
        return mobject


class BaseThreeDScene(ThreeDScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.math_group = VGroup()
        self.ui_group = VGroup()

    def clear_scene(self, fade_out: bool = True, run_time: float = 1.0):
        if fade_out:
            self.play(FadeOut(self.math_group), FadeOut(self.ui_group), run_time=run_time)
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

    def add_background(self, mobject: Mobject, opacity: float = 0.2):
        from manim_lib.core import LayerManager

        LayerManager.to_background(mobject, opacity=opacity)
        self.add(mobject)
        return mobject

    def add_active(self, mobject: Mobject, layer: int = None):
        from manim_lib.core import LayerManager

        target_layer = LayerManager.L_ACTIVE if layer is None else layer
        LayerManager.set_layer(mobject, target_layer)
        mobject.set_opacity(1.0)
        self.add(mobject)
        return mobject

    # 安全特写：在 3D 场景中优先“放大物体”而非直接推近相机
    def safe_zoom_on(self, mobject: Mobject, scale: float = 2.5, about_point=None, shift_to=ORIGIN):
        """
        3D 场景常见误用：ThreeDCamera 无 frame 属性，直接 self.camera.frame 会报错。
        本方法通过放大物体并平移到视窗中心，模拟“镜头推近”，避免 API 误用。
        """
        target_point = about_point if about_point is not None else mobject.get_center()
        return mobject.animate.scale(scale, about_point=target_point).shift(shift_to - target_point)


# =============================================================================
# 叙事 / 节奏 / 极简辅助
# =============================================================================
class PacingController:
    """统一的节奏控制器，落实“呼吸法则”"""

    WAIT_FACTOR = 2.0
    SLOW_MOTION_FACTOR = 2.0

    @staticmethod
    def slow_wait(scene: Scene, time: float):
        scene.wait(time * PacingController.WAIT_FACTOR)

    @staticmethod
    def slow_play(scene: Scene, animation, base_run_time: float = 1.0):
        run_time = base_run_time * PacingController.SLOW_MOTION_FACTOR
        scene.play(animation, run_time=run_time)

    @staticmethod
    def enforce_3_second_rule(scene: Scene, after_formula=True, after_complex_visual=True):
        if after_formula:
            PacingController.slow_wait(scene, 3.0)
        if after_complex_visual:
            PacingController.slow_wait(scene, 2.0)


class NarrativeHelper:
    """叙事辅助：设问/困境/解决/验证"""

    @staticmethod
    def ask_question(scene: Scene, text: str, wait_after=2.0, font_size=32):
        # 仅需 safer_text + 动画，前置断行交由 safer_text 负责
        from manim_lib.utils import safer_text

        q_obj = safer_text(text, font_size=font_size, color=PALETTE["HIGHLIGHT"])
        scene.add_to_math_group(q_obj)
        scene.play(Write(q_obj), run_time=2.0)
        PacingController.slow_wait(scene, wait_after)
        return q_obj

    @staticmethod
    def show_conflict(scene: Scene, text: str, visual_element, wait_after=2.0):
        hud = SubtitleManager(scene)
        hud.show(text, wait_after=1.0)
        scene.play(Create(visual_element), run_time=2.0)
        PacingController.slow_wait(scene, wait_after)

    @staticmethod
    def show_solution(scene: Scene, text: str, solution_element, wait_after=3.0):
        hud = SubtitleManager(scene)
        hud.show(text, wait_after=1.0)
        scene.play(Write(solution_element), run_time=3.0)
        PacingController.slow_wait(scene, wait_after)

    @staticmethod
    def show_validation(scene: Scene, text: str, validation_element, wait_after=2.0):
        hud = SubtitleManager(scene)
        hud.show(text, wait_after=1.0)
        scene.play(Create(validation_element), run_time=2.0)
        PacingController.slow_wait(scene, wait_after)


class MinimalismHelper:
    """极简主义辅助：低饱和度背景与焦点强化"""

    BACKGROUND_OPACITY = 0.3
    FOCUS_OPACITY = 1.0

    @staticmethod
    def create_focus_axes(stroke_opacity=None):
        if stroke_opacity is None:
            stroke_opacity = MinimalismHelper.BACKGROUND_OPACITY
        return default_axis_config(
            stroke_opacity=stroke_opacity,
            stroke_width=1.0,
            stroke_color=GREY_C,
        )

    @staticmethod
    def create_background_element(element, opacity=None):
        if opacity is None:
            opacity = MinimalismHelper.BACKGROUND_OPACITY
        element.set_opacity(opacity)
        return element

    @staticmethod
    def create_focus_element(element, color=None):
        if color is None:
            color = PALETTE["HIGHLIGHT"]
        element.set_color(color)
        element.set_opacity(MinimalismHelper.FOCUS_OPACITY)
        return element

    @staticmethod
    def create_static_highlight(mobject, color=None):
        if color is None:
            color = PALETTE["HIGHLIGHT"]
        return SmartBox.create(
            mobject,
            content_type="text",
            color=color,
            stroke_width=2.0,
        )


class LayerManager:
    """影院级层级管理"""

    L_BG = -10
    L_PASSIVE = 0
    L_ACTIVE = 10
    L_HIGHLIGHT = 20
    L_LABEL = 30
    L_UI = 100

    @staticmethod
    def set_layer(mobject: Mobject, layer_z: int):
        for mob in mobject.family_members_with_points():
            mob.set_z_index(layer_z)
        return mobject

    @staticmethod
    def to_background(mobject: Mobject, opacity: float = 0.2):
        LayerManager.set_layer(mobject, LayerManager.L_BG)
        mobject.set_opacity(opacity)
        return mobject

    @staticmethod
    def to_foreground(mobject: Mobject):
        LayerManager.set_layer(mobject, LayerManager.L_HIGHLIGHT)
        mobject.set_opacity(1.0)
        return mobject

    @staticmethod
    def focus_on(scene: Scene, target_mobjects: List[Mobject], context_mobjects: List[Mobject]):
        scene.play(
            *[
                mobj.animate.set_opacity(0.15).set_z_index(LayerManager.L_BG)
                for mobj in context_mobjects
            ],
            run_time=1.0,
        )
        for t in target_mobjects:
            LayerManager.to_foreground(t)


# =============================================================================
# Convenience wrappers
# =============================================================================
def slow_wait(scene: Scene, time: float):
    PacingController.slow_wait(scene, time)


def slow_play(scene: Scene, animation, base_run_time: float = 1.0):
    PacingController.slow_play(scene, animation, base_run_time)


def ask_question(scene: Scene, text: str, wait_after: float = 2.0):
    return NarrativeHelper.ask_question(scene, text, wait_after)


def show_conflict(scene: Scene, text: str, visual_element, wait_after: float = 2.0):
    NarrativeHelper.show_conflict(scene, text, visual_element, wait_after)


def show_solution(scene: Scene, text: str, solution_element, wait_after: float = 3.0):
    NarrativeHelper.show_solution(scene, text, solution_element, wait_after)


def show_validation(scene: Scene, text: str, validation_element, wait_after: float = 2.0):
    NarrativeHelper.show_validation(scene, text, validation_element, wait_after)


__all__ = [
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
]

