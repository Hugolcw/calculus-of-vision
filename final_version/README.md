# Sobel Universe - 完整实现版

这是根据文档规范实现的完整视频代码，包含所有5个场景的完整实现。

## 文件说明

- `sobel_complete.py`: 完整的视频实现，包含6个场景（含新增Scene 3.5）
- `时长估算.md`: 各场景的详细时长估算
- `脚本文档.md`: 符合作业要求的脚本文档（创作思路、作品意义、素材来源）
- `说明.md`: 组员名单和文件说明
- `提交指南.md`: 作业提交要求和操作步骤
- `旁白与剪辑指南.md`: 旁白脚本、录制建议和剪辑注意事项
- `专家意见汇总.md`: 代码审查建议和优化方案

## 场景结构

### Scene 1: 离散现实 (Discrete Reality)

- 展示连续函数的理想状态
- 演示采样过程，使用"幽灵"效果保留连续曲线
- 聚焦到离散采样点，引出问题

### Scene 2: 泰勒桥梁 (The Taylor Bridge)

- 展示泰勒展开公式
- 演示项的对撞和抵消过程
- 推导出中心差分公式
- 提取系数 [-1, 0, 1]

### Scene 3.5: 噪声的战争 (The War on Noise) - 新增

- **现实的残酷**: 展示理想信号 vs 带噪声的真实信号
- **直接求导的灾难**: 展示噪声被差分放大，导数变成锯齿状
- **高斯护盾**: 展示高斯平滑的效果，解释为什么需要平滑
- 为Sobel算子的平滑部分提供理论支撑

### Scene 3: 算子解构 (Operator Anatomy)

- 展示微分向量和平滑向量
- 演示外积运算过程
- 生成最终的3x3 Sobel矩阵
- 高亮矩阵结构
- **卷积可分离性**: 展示计算效率对比（3+3 vs 3×3）

### Scene 4: 维度跃迁 (Dimensional Leap)

- 2D阶段: 显示图像和扫描线，生成波形图
- 维度切换: 从2D转换为3D地形
- 全息扫描: Sobel算子在3D地形上扫描
- **像素级放大镜**: 暂停扫描，放大到3×3像素格子，显示RGB数值和卷积计算过程
- 特征图生成: 显示边缘检测结果

### Scene 5: Outro - 知行合一

- 快速回顾关键元素
- 展示核心哲学思想
- 版权声明和工具说明

## 使用方法

### 环境要求

- **Python**: 3.8+
- **Manim Community Edition**: v0.17.0+ (推荐最新版本)
  - 不同版本的 `ThreeDScene` 相机参数 (`phi`, `theta`) 行为可能略有不同
- **LaTeX**: TeX Live 或 MiKTeX
  - 如果渲染时出现 LaTeX 错误，请安装完整的 TeX 发行版
  - Windows 推荐使用 MiKTeX
  - Linux/Mac 推荐使用 TeX Live

### 安装依赖

```bash
pip install manim numpy
```

**注意**: 如果遇到 LaTeX 相关错误，请确保已安装并配置好 LaTeX 环境。

### 渲染视频

```bash
# 低质量预览 (快速调试)
manim -pql sobel_complete.py SobelUniverse

# 高质量渲染 (最终版本)
manim -pqh sobel_complete.py SobelUniverse
```

### 参数说明

- `-p`: 渲染后自动预览
- `-ql`: Quality Low (低质量，快速)
- `-qm`: Quality Medium (中等质量)
- `-qh`: Quality High (高质量)

## 设计原则

### 颜色语义

- `COLOR_CONTINUOUS` (BLUE): 理想数学
- `COLOR_DISCRETE` (YELLOW): 工程采样
- `COLOR_DIFF` (RED): 微分/变化/高频
- `COLOR_SMOOTH` (TEAL): 平滑/保持/低频
- `COLOR_GHOST` (GREY): 过去的影子

### 性能优化

Scene 4 必须对图像进行降采样 (`[::10, ::10]`)，否则渲染会非常慢或卡死。

### 调试技巧

在 `construct()` 方法中，可以注释掉已完成的部分，只渲染当前正在开发的场景：

```python
def construct(self):
    # self.setup_scene_1_discrete()
    # self.transition_1_2()
    # self.setup_scene_2_taylor()
    self.setup_scene_3_matrices()  # 只渲染这个场景
```

## 视频时长

- **纯动画时长**: 约 127.5秒（2分8秒）
- **含旁白预计**: 约 6-7分钟
- **符合作业要求**: ≤ 8分钟 ✅

## 注意事项

1. **Scene 4 的性能**: 务必进行降采样，建议分辨率不超过 20x20
2. **MathTex 索引**: 如果公式动画不工作，可能需要使用 `index_labels()` 调试索引
3. **坐标系对齐**: Scene 4 中需要确保2D图像和3D地形的坐标系对齐
4. **LaTeX 渲染**: 某些复杂的LaTeX公式可能需要调整
5. **Scene 3.5**: 使用固定随机种子（seed=42）确保噪声信号可重复

## 自定义图片

如果想要在Scene 4中使用真实图片，可以修改 `setup_scene_4_vision()` 方法：

```python
# 将图片路径替换为你的图片路径
image_data = get_downsampled_array("path/to/your/image.png", rate=10)
```

## 问题反馈

如果遇到问题，请检查：

1. Manim版本是否兼容
2. LaTeX是否安装并配置正确
3. 降采样是否已正确应用
4. 坐标系是否对齐

## 版权声明

本代码遵循项目要求，所有动画均为编程生成，使用Manim Community Edition制作。
