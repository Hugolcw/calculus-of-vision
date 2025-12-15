"""
样式系统：语义化配色与背景色。
源自 V13+ 设计，去版本化，便于工程复用。
"""

# 语义化色彩字典
PALETTE = {
    "BG_MAIN": "#0F1115",       # 深炭灰
    "MATH_FUNC": "#3498DB",     # 逻辑蓝（函数本体）
    "MATH_ERROR": "#F1C40F",    # 琥珀金（高频/边缘）
    "DIFF_FWD": "#E67E22",      # 前向色
    "DIFF_BWD": "#E74C3C",      # 后向色
    "DIFF_CTR": "#2ECC71",      # 中心色
    "HIGHLIGHT": "#FFFFFF",     # 绝对焦点
    "EDGE": "#F1C40F",          # 边缘检测
}

# 向后兼容的颜色常量
COLOR_CONTINUOUS = PALETTE["MATH_FUNC"]   # 理想数学、连续世界
COLOR_DISCRETE = "#FFE066"                # 工程采样、离散世界（保留原暖黄调）
COLOR_DIFF = PALETTE["MATH_ERROR"]        # 微分/变化/高频/边缘
COLOR_SMOOTH = "#2AA198"                  # 平滑/保持/低频（柔和青色）
BG_COLOR = PALETTE["BG_MAIN"]             # 深色背景

__all__ = [
    "PALETTE",
    "COLOR_CONTINUOUS",
    "COLOR_DISCRETE",
    "COLOR_DIFF",
    "COLOR_SMOOTH",
    "BG_COLOR",
]

