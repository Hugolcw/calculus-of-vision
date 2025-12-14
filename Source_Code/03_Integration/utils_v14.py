"""
V14 统一工具模块
基于 V13，新增：
- 叙事工具类（NarrativeHelper）
- 节奏控制器（PacingController）
- 极简主义辅助工具（MinimalismHelper）

V14 核心理念：
- 叙事优先：建立"提出问题-受挫-解决"的完整叙事链
- 节奏控制：实现 3B1B 风格的"呼吸法则"
- 极简主义：删除装饰性动画，降低饱和度
"""

# 导入 V13 的所有功能
from utils_v13 import *

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
            stroke_width=3.5
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

