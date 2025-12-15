"""
V15 统一工具模块
基于 V14，新增/覆写：
- 默认坐标轴弱化 (default_axis_config stroke_opacity=0.3，仅 v15)
- 层级添加便捷器 add_background / add_active（仅在 v15 注入 BaseScene）

沿用 V14 核心理念：
- 叙事优先：建立"提出问题-受挫-解决"的完整叙事链
- 节奏控制：实现 3B1B 风格的"呼吸法则"
- 极简主义：删除装饰性动画，降低饱和度
"""

from utils_v13 import *
import textwrap
import re

# =============================================================================
# V15 覆写：默认坐标轴配置更弱化（不影响 v14）
# =============================================================================
def default_axis_config(
    stroke_opacity: float = 0.3,
    stroke_width: float = 1.0,
    stroke_color: str = GREY_C,
) -> dict:
    """
    影院风格的坐标轴默认配置：轻量背景线条，减弱平面感。
    仅在 v15 生效；v14 仍使用原始默认值，保持版本隔离。
    """
    return {
        "stroke_opacity": stroke_opacity,
        "stroke_width": stroke_width,
        "stroke_color": stroke_color,
    }

# =============================================================================
# V14 Pro：影院级智能字幕管理器（覆盖 utils_v13 中的版本）
# =============================================================================

class SubtitleManager:
    """
    V14 Pro: 影院级智能字幕管理器

    特性：
    1. 语义断行：优先在标点符号处换行，保持语意连贯。
    2. 视觉一致性：锁定字号，不到万不得已不缩放。
    3. 电影感背景：宽幅半透明背景条，避免“字多少框就多宽”的跳动感。
    """

    def __init__(self, scene: Scene):
        self.scene = scene
        self.current_subtitle: Optional[Mobject] = None
        self.current_bg: Optional[Mobject] = None

    def _smart_break_text(self, text: str, max_chars: int = 24) -> str:
        """
        核心算法：语义断句
        优先在中部附近（30%-70%）的标点处分行，保证语义完整。
        """
        if len(text) <= max_chars:
            return text

        mid = len(text) // 2
        search_range = range(int(len(text) * 0.3), int(len(text) * 0.7))

        best_split_idx = -1
        min_dist_to_mid = float("inf")

        # 优先级：逗号 > 其他标点
        punctuations = ["，", "：", "；", ",", ":", ";", "。", "！", "!", "？", "?"]

        for i in search_range:
            char = text[i]
            if char in punctuations:
                dist = abs(i - mid)
                if dist < min_dist_to_mid:
                    min_dist_to_mid = dist
                    best_split_idx = i + 1  # 在标点后换行

        if best_split_idx != -1:
            return text[:best_split_idx] + "\n" + text[best_split_idx:]

        # 无标点时，尝试在空格处分行（英文句子）
        if " " in text:
            words = text.split(" ")
            acc = []
            current = ""
            for w in words:
                if len(current) + len(w) + 1 <= max_chars:
                    current = (current + " " + w).strip()
                else:
                    acc.append(current)
                    current = w
            if current:
                acc.append(current)
            if len(acc) >= 2:
                return "\n".join(acc[:2])

        # 兜底：正中间硬分
        return text[:mid] + "\n" + text[mid:]

    def _calculate_duration(self, text: str) -> float:
        """基础阅读时间：每字 0.25 秒，最小 3 秒；复杂概念补偿 +1 秒。"""
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
        font_size: float = 28,  # 锁定标准电影字号
        wait_after: float = None,
        fade_in: bool = True,
    ):
        # 1) 语义排版
        formatted_text = self._smart_break_text(text)

        # 2) 创建文本对象（多行自动居中），line_spacing 适度增加呼吸感
        try:
            subtitle = Text(formatted_text, font_size=font_size, color=color, font="SimHei", line_spacing=1.2)
        except Exception:
            subtitle = Text(formatted_text, font_size=font_size, color=color, line_spacing=1.2)

        # 3) 轻度安全缩放（仅当确实超宽时，且尽量少缩）
        max_w = SAFE_RECT["width"] - 1.0  # 留出左右边距
        if subtitle.width > max_w:
            scale_factor = max_w / subtitle.width
            scale_factor = max(0.85, scale_factor)  # 不低于 0.85，保持一致观感
            subtitle.scale(scale_factor)

        # 4) 底部对齐：字幕从底部向上长，视线固定在底部
        subtitle.move_to(ORIGIN)
        subtitle.to_edge(DOWN, buff=0.5)

        # 5) 影院感背景条（宽幅稳定）
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

        # 6) 动画
        if fade_in:
            self.scene.play(FadeIn(group, shift=UP * 0.1), run_time=0.5)
        else:
            self.scene.add(group)

        self.current_subtitle = subtitle
        self.current_bg = bg

        # 7) 等待时间：默认使用节奏控制
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
                self.scene.play(FadeOut(group), run_time=0.3)
            else:
                self.scene.remove(group)
            self.current_subtitle = None
            self.current_bg = None

# =============================================================================
# V14 模块一：叙事工具类 (Narrative Helper)
# =============================================================================

class NarrativeHelper:
    """
    V14 新增：叙事辅助工具
    帮助构建"提出问题-受挫-解决"的完整叙事链
    """
    
    @staticmethod
    def ask_question(scene, text, wait_after=2.0, font_size=32):
        """
        设问：引发思考
        
        参数:
        - scene: 场景对象
        - text: 问题文本
        - wait_after: 问题显示后的等待时间
        - font_size: 字号
        
        返回: 问题文本对象
        """
        question = safer_text(
            text, 
            font_size=font_size, 
            color=PALETTE["HIGHLIGHT"]
        )
        scene.add_to_math_group(question)
        scene.play(Write(question), run_time=2.0)
        PacingController.slow_wait(scene, wait_after)
        return question
    
    @staticmethod
    def show_conflict(scene, text, visual_element, wait_after=2.0):
        """
        困境：展示困难
        
        参数:
        - scene: 场景对象
        - text: 困境描述文本
        - visual_element: 视觉元素（展示困境）
        - wait_after: 显示后的等待时间
        """
        hud = SubtitleManager(scene)
        hud.show(text, wait_after=1.0)
        scene.play(Create(visual_element), run_time=2.0)
        PacingController.slow_wait(scene, wait_after)
    
    @staticmethod
    def show_solution(scene, text, solution_element, wait_after=3.0):
        """
        解决：展示方法
        
        参数:
        - scene: 场景对象
        - text: 解决方案描述文本
        - solution_element: 解决方案的视觉元素
        - wait_after: 显示后的等待时间
        """
        hud = SubtitleManager(scene)
        hud.show(text, wait_after=1.0)
        scene.play(Write(solution_element), run_time=3.0)
        PacingController.slow_wait(scene, wait_after)
    
    @staticmethod
    def show_validation(scene, text, validation_element, wait_after=2.0):
        """
        验证：展示结果
        
        参数:
        - scene: 场景对象
        - text: 验证描述文本
        - validation_element: 验证结果的视觉元素
        - wait_after: 显示后的等待时间
        """
        hud = SubtitleManager(scene)
        hud.show(text, wait_after=1.0)
        scene.play(Create(validation_element), run_time=2.0)
        PacingController.slow_wait(scene, wait_after)


# =============================================================================
# V14 模块二：节奏控制器 (Pacing Controller)
# =============================================================================

class PacingController:
    """
    V14 新增：节奏控制器
    强制执行 3B1B 风格的"呼吸法则"
    """
    
    # 节奏因子：所有 wait 时间翻倍
    WAIT_FACTOR = 2.0
    
    # 慢动作因子：核心动画 run_time 翻倍
    SLOW_MOTION_FACTOR = 2.0
    
    @staticmethod
    def slow_wait(scene, time):
        """
        慢速等待（强制执行 3 秒法则）
        
        参数:
        - scene: 场景对象
        - time: 基础等待时间（实际等待时间 = time * WAIT_FACTOR）
        """
        scene.wait(time * PacingController.WAIT_FACTOR)
    
    @staticmethod
    def slow_play(scene, animation, base_run_time=1.0):
        """
        慢速播放（强制执行慢动作规则）
        
        参数:
        - scene: 场景对象
        - animation: 动画对象
        - base_run_time: 基础动画时长（实际时长 = base_run_time * SLOW_MOTION_FACTOR）
        """
        run_time = base_run_time * PacingController.SLOW_MOTION_FACTOR
        scene.play(animation, run_time=run_time)
    
    @staticmethod
    def step_by_step_write(scene, formula_parts, wait_between=0.5):
        """
        分步呈现公式（跟着人说话的语速去写公式）
        
        参数:
        - scene: 场景对象
        - formula_parts: 公式部分列表
        - wait_between: 每个部分之间的等待时间
        """
        for i, part in enumerate(formula_parts):
            scene.play(Write(part), run_time=2.0)
            if i < len(formula_parts) - 1:
                PacingController.slow_wait(scene, wait_between)
    
    @staticmethod
    def enforce_3_second_rule(scene, after_formula=True, after_complex_visual=True):
        """
        强制执行 3 秒法则
        
        参数:
        - scene: 场景对象
        - after_formula: 公式推导后是否等待 3 秒
        - after_complex_visual: 复杂图形变化后是否等待 2 秒
        """
        if after_formula:
            PacingController.slow_wait(scene, 3.0)
        if after_complex_visual:
            PacingController.slow_wait(scene, 2.0)


# =============================================================================
# V14 模块三：极简主义辅助工具 (Minimalism Helper)
# =============================================================================

class MinimalismHelper:
    """
    V14 新增：极简主义辅助工具
    删除装饰性动画，降低饱和度，实现"静止的力量"
    """
    
    # 背景元素默认透明度（V14 极简主义要求）
    BACKGROUND_OPACITY = 0.3
    
    # 焦点元素默认透明度
    FOCUS_OPACITY = 1.0
    
    @staticmethod
    def create_focus_axes(stroke_opacity=None):
        """
        创建低饱和度的坐标轴（极简主义）
        
        参数:
        - stroke_opacity: 透明度（默认使用 BACKGROUND_OPACITY）
        
        返回: 坐标轴配置字典
        """
        if stroke_opacity is None:
            stroke_opacity = MinimalismHelper.BACKGROUND_OPACITY
        return default_axis_config(
            stroke_opacity=stroke_opacity,
            stroke_width=1.0,
            stroke_color=GREY_C
        )
    
    @staticmethod
    def create_background_element(element, opacity=None):
        """
        创建背景元素（低饱和度）
        
        参数:
        - element: 要设置为背景的元素
        - opacity: 透明度（默认使用 BACKGROUND_OPACITY）
        
        返回: 设置好透明度的元素
        """
        if opacity is None:
            opacity = MinimalismHelper.BACKGROUND_OPACITY
        element.set_opacity(opacity)
        return element
    
    @staticmethod
    def create_focus_element(element, color=None):
        """
        创建焦点元素（高饱和度）
        
        参数:
        - element: 要设置为焦点的元素
        - color: 颜色（默认使用 PALETTE["HIGHLIGHT"]）
        
        返回: 设置好颜色和透明度的元素
        """
        if color is None:
            color = PALETTE["HIGHLIGHT"]
        element.set_color(color)
        element.set_opacity(MinimalismHelper.FOCUS_OPACITY)
        return element
    
    @staticmethod
    def remove_decorative_animations(scene, mobjects):
        """
        移除装饰性动画（V14 极简主义要求）
        
        注意：这个方法主要用于标记，实际删除需要在代码中手动移除
        例如：删除 apply_wave_effect、wiggle_effect 等调用
        
        参数:
        - scene: 场景对象
        - mobjects: 要移除装饰性动画的对象列表
        """
        # 这是一个标记方法，提醒开发者不要使用装饰性动画
        # 实际删除需要在代码中手动完成
        pass
    
    @staticmethod
    def create_static_highlight(mobject, color=None):
        """
        创建静态高亮框（不闪烁、不呼吸）
        
        参数:
        - mobject: 要高亮的对象
        - color: 高亮颜色（默认使用 PALETTE["HIGHLIGHT"]）
        
        返回: 静态高亮框
        """
        if color is None:
            color = PALETTE["HIGHLIGHT"]
        return SmartBox.create(
            mobject,
            content_type="text",
            color=color,
            stroke_width=2.0  # 更细的线条，减少画面噪音
        )


# =============================================================================
# V14 便捷函数（简化常用操作）
# =============================================================================

def slow_wait(scene, time):
    """便捷函数：慢速等待"""
    PacingController.slow_wait(scene, time)

def slow_play(scene, animation, base_run_time=1.0):
    """便捷函数：慢速播放"""
    PacingController.slow_play(scene, animation, base_run_time)

def ask_question(scene, text, wait_after=2.0):
    """便捷函数：设问"""
    return NarrativeHelper.ask_question(scene, text, wait_after)

def show_conflict(scene, text, visual_element, wait_after=2.0):
    """便捷函数：展示困境"""
    NarrativeHelper.show_conflict(scene, text, visual_element, wait_after)

def show_solution(scene, text, solution_element, wait_after=3.0):
    """便捷函数：展示解决"""
    NarrativeHelper.show_solution(scene, text, solution_element, wait_after)

def show_validation(scene, text, validation_element, wait_after=2.0):
    """便捷函数：展示验证"""
    NarrativeHelper.show_validation(scene, text, validation_element, wait_after)


# =============================================================================
# V14.5 模块四：影院级层级管理器 (Cinematic Layer Manager)
# =============================================================================

class LayerManager:
    """
    V14.5 新增：层级管理器，落实“三明治分层法”

    层级定义：
    - L_BG        : 背景/网格
    - L_PASSIVE   : 非焦点内容
    - L_ACTIVE    : 当前内容
    - L_HIGHLIGHT : 高亮/扫描框/光标
    - L_LABEL     : 标注/箭头
    - L_UI        : HUD/字幕（最高层）
    """

    L_BG        = -10
    L_PASSIVE   = 0
    L_ACTIVE    = 10
    L_HIGHLIGHT = 20
    L_LABEL     = 30
    L_UI        = 100

    @staticmethod
    def set_layer(mobject: Mobject, layer_z: int):
        """强制将物体放置在特定层级（递归作用于所有子物体）。"""
        for mob in mobject.family_members_with_points():
            mob.set_z_index(layer_z)
        return mobject

    @staticmethod
    def to_background(mobject: Mobject, opacity: float = 0.2):
        """一键退居幕后：下沉到背景层并降低不透明度。"""
        LayerManager.set_layer(mobject, LayerManager.L_BG)
        mobject.set_opacity(opacity)
        return mobject

    @staticmethod
    def to_foreground(mobject: Mobject):
        """一键上浮到高亮层。"""
        LayerManager.set_layer(mobject, LayerManager.L_HIGHLIGHT)
        mobject.set_opacity(1.0)
        return mobject

    @staticmethod
    def focus_on(scene: Scene, target_mobjects: list, context_mobjects: list):
        """
        导演级聚焦：目标上浮，背景下沉。
        - target_mobjects: 需要上浮的主体（列表）
        - context_mobjects: 需要虚化的背景（列表）
        """
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
# V15 增强：BaseScene 便捷添加器（锁层级 + 透明度），保证层级不被动画覆盖
# =============================================================================
def _base_add_background(self, mobject: Mobject, opacity: float = 0.2):
    """
    将元素添加为背景：统一弱化并下沉层级，防止 FadeIn/Create 覆盖层级设置。
    """
    LayerManager.to_background(mobject, opacity=opacity)
    self.add(mobject)
    return mobject


def _base_add_active(self, mobject: Mobject, layer: int = LayerManager.L_ACTIVE):
    """
    将元素添加为主动内容：锁定层级并保持不透明，避免动画重置 z_index。
    """
    LayerManager.set_layer(mobject, layer)
    mobject.set_opacity(1.0)
    self.add(mobject)
    return mobject


# 仅在 v15 挂载，保持 v14 隔离
if "BaseScene" in globals():
    setattr(BaseScene, "add_background", _base_add_background)
    setattr(BaseScene, "add_active", _base_add_active)
if "BaseThreeDScene" in globals():
    setattr(BaseThreeDScene, "add_background", _base_add_background)
    setattr(BaseThreeDScene, "add_active", _base_add_active)

# =============================================================================
# V15 核心修复：重写安全边界检查 (Hotfix for V13 Deprecation)
# 专家注释：
# 1. 屏蔽 utils_v13 中导致崩溃的 get_bounding_box() 调用
# 2. 使用 Manim Community 标准的 .width / .height 属性
# 3. 保持原有缩放逻辑，确保视觉输出与设计意图完全一致
# =============================================================================

def ensure_safe_bounds(mobject, conservative: bool = False, scale_factor: float = 0.95):
    """
    [V15 重写版] 确保 Mobject 在 SAFE_RECT 安全区域内。
    修复了 AttributeError: 'Mobject' object has no attribute 'get_bounding_box'
    """
    # 1. 获取安全区尺寸 (从全局变量继承，含默认值兜底)
    safe_w = SAFE_RECT["width"] if "SAFE_RECT" in globals() else 13.0
    safe_h = SAFE_RECT["height"] if "SAFE_RECT" in globals() else 7.0
    
    # 保守模式：进一步收缩安全区，防止贴边
    if conservative:
        safe_w *= 0.9
        safe_h *= 0.9
        
    # 2. 获取对象当前尺寸 (使用新版 API)
    # 专家提示：.width 和 .height 是 Manim Community 中获取包围盒尺寸的标准属性
    current_w = mobject.width
    current_h = mobject.height
    
    # 边界情况处理：防止除零错误 (如空物体)
    if current_w == 0 or current_h == 0:
        return mobject
    
    # 3. 计算缩放比例 (保持长宽比)
    # 只有当物体超出范围时才计算缩放因子，否则保持 1.0
    scale_x = safe_w / current_w if current_w > safe_w else 1.0
    scale_y = safe_h / current_h if current_h > safe_h else 1.0
    
    min_scale = min(scale_x, scale_y)
    
    # 4. 执行缩放 (仅当需要缩小时)
    if min_scale < 1.0:
        mobject.scale(min_scale * scale_factor)
        
    return mobject