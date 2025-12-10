from manim import *
import numpy as np

class SobelConvolution3D(ThreeDScene):
    def construct(self):
        # 1. 设置 3b1b 经典的深灰背景
        self.camera.background_color = "#1e1e1e"
        
        # 调整摄像机角度：俯视 + 侧视，更有立体感
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)

        # 2. 创建坐标轴
        axes = ThreeDAxes(
            x_range=[0, 10, 1], 
            y_range=[0, 10, 1], 
            z_range=[0, 6, 1],
            x_length=7,
            y_length=7,
            z_length=4
        ).add_coordinates()

        # 3. 定义函数曲面 (模拟图像光强)
        # 这是一个平滑的 Sigmoid 组合函数，模拟中间亮两边暗的灯条
        def func(u, v):
            val = 10 / (1 + np.exp(-5 * (u - 3.5))) - 10 / (1 + np.exp(-5 * (u - 8.5)))
            return val / 2.5  # 高度适当缩放

        resolution_fa = 24 # 分辨率，越高越卡但越平滑
        surface = Surface(
            lambda u, v: axes.c2p(u, v, func(u, v)),
            u_range=[0, 10],
            v_range=[0, 10],
            resolution=(resolution_fa, resolution_fa),
            should_make_jagged=False
        )
        
        # 【关键】设置材质风格：半透明青色 + 网格线
        surface.set_style(fill_opacity=0.6, stroke_color=BLUE_A, stroke_width=0.5)
        surface.set_fill_by_checkerboard(BLUE_D, BLUE_E, opacity=0.5)

        # 4. 创建扫描框 (红色方框)
        scanner = Square(side_length=2).set_color(RED).set_stroke(width=5)
        scanner.rotate(PI/2, axis=RIGHT) # 躺平
        
        # 5. 创建梯度箭头 (黄色)
        arrow = Arrow3D(start=ORIGIN, end=UP, color=YELLOW)

        # 核心逻辑：每一帧都重新计算箭头的状态
        def update_scanner_components(mob):
            # 获取扫描框当前的中心坐标
            center = scanner.get_center()
            # 反解出对应的轴坐标 u (x)
            u = axes.p2c(center)[0]
            v = 5 # y 固定在中间扫描
            
            # 计算曲面上的点高度
            z_val = func(u, v)
            surface_point = axes.c2p(u, v, z_val)
            
            # 把扫描框贴在曲面上方一点点
            scanner.move_to(axes.c2p(u, v, z_val + 0.1))
            
            # 数值微分计算导数 (Sobel算子的本质)
            delta = 0.01
            deriv = (func(u + delta, v) - func(u - delta, v)) / (2 * delta)
            
            # 设置箭头
            # 起点：曲面上
            # 终点：沿着 x 轴方向延伸，长度由导数决定
            vect = np.array([deriv * 0.8, 0, deriv * 0.8]) # 简单的切向量模拟
            # 归一化后拉长，或者直接用导数做长度
            arrow_end = surface_point + np.array([deriv * 0.5, 0, 0]) 
            
            # 这里做一个简化的视觉效果：箭头向上指代梯度大小
            # 如果想要严谨的切向量，可以用上面的 vect
            mob.put_start_and_end_on(
                surface_point, 
                surface_point + np.array([deriv, 0, 0]) # 红色箭头指向变化方向
            )

        # 绑定更新函数
        arrow.add_updater(update_scanner_components)
        scanner.add_updater(lambda m: m.move_to(axes.c2p(axes.p2c(m.get_center())[0], 5, func(axes.p2c(m.get_center())[0], 5)+0.1)))

        # 6. 组合场景
        self.add(axes, surface, scanner, arrow)
        
        # 初始位置
        scanner.move_to(axes.c2p(1, 5, 0))

        # 动画：从左扫到右
        self.play(
            scanner.animate.move_to(axes.c2p(9, 5, 0)),
            run_time=5,
            rate_func=linear
        )
        self.wait()