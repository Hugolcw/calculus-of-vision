"""
简易冒烟测试封装：以低质量快速跑指定场景，捕获常见崩溃。

用法（在 03_Integration 下执行）:
    python tools/smoke_render.py sobel_v15_full.py FullSobelVideo
    # 仅低质量预览，超时自动中断（默认 120s）

参数：
    file        Manim 源文件
    scene       场景类名
    --quality   manim 质量标识，默认 pql
    --timeout   超时时间秒，默认 120

说明：
    - 使用 subprocess 调用 manim，质量低、禁用缓存，便于快速发现导入/资源/MathTex 报错。
    - 不做并行，避免占满显存；如需批量可自行编排循环。
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_smoke(file: Path, scene: str, quality: str, timeout: int) -> int:
    cmd = [
        "manim",
        f"-{quality}",
        "--disable_caching",
        "--write_to_movie",
        str(file),
        scene,
    ]
    print(f"[run] {' '.join(cmd)} (timeout {timeout}s)")
    try:
        proc = subprocess.run(cmd, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"[timeout] {file}:{scene} 超时 {timeout}s")
        return 124
    return proc.returncode


def main():
    parser = argparse.ArgumentParser(description="Manim 场景低质量冒烟测试")
    parser.add_argument("file", help="Manim 源文件，如 sobel_v15_full.py")
    parser.add_argument("scene", help="场景类名，如 FullSobelVideo")
    parser.add_argument("--quality", default="pql", help="manim 质量标识，默认 pql")
    parser.add_argument("--timeout", type=int, default=120, help="超时时间（秒）")
    args = parser.parse_args()

    file = Path(args.file)
    if not file.exists():
        print(f"[error] 文件不存在: {file}")
        sys.exit(1)

    rc = run_smoke(file, args.scene, args.quality, args.timeout)
    if rc == 0:
        print("[ok] 渲染成功")
    else:
        print(f"[fail] 渲染失败，退出码 {rc}")
    sys.exit(rc)


if __name__ == "__main__":
    main()

