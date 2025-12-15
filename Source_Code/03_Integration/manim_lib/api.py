"""
兼容性 API 封装：将容易变动或易误用的 Manim 接口集中管理，便于未来升级。
"""

from typing import Tuple
from manim import Mobject, ThreeDScene


def get_size(mobj: Mobject) -> Tuple[float, float]:
    """
    返回 (width, height)。优先使用属性，在旧版无属性时可扩展为调用方法。
    """
    return mobj.width, mobj.height


def safe_move_camera(scene: ThreeDScene, *, phi=None, theta=None, zoom=None, frame_center=None, **kwargs):
    """
    对 ThreeDScene.move_camera 的薄封装，集中入口便于未来兼容。
    """
    return scene.move_camera(phi=phi, theta=theta, zoom=zoom, frame_center=frame_center, **kwargs)


__all__ = ["get_size", "safe_move_camera"]

