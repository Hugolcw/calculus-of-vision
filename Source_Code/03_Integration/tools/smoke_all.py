"""
批量冒烟测试：扫描指定脚本并按场景列表逐个低质量渲染，便于 CI 或本地一次跑完。

用法（在 03_Integration 下执行）:
    python tools/smoke_all.py --file sobel_v15_full.py --scene FullSobelVideo
    # 或多文件多场景
    python tools/smoke_all.py --file sobel_v14_full.py --scene FullSobelVideo --scene Scene0Intro

参数：
    --file   可多次指定，默认自动匹配 sobel_v*.py
    --scene  可多次指定，若未指定场景则默认只跑 FullSobelVideo（若存在）
    --quality pql/pqh 等，默认 pql
    --timeout 每个任务超时秒数，默认 120

实现：调用本目录的 smoke_render.py 逐个执行，任一失败返回非零。
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_one(file: Path, scene: str, quality: str, timeout: int) -> int:
    cmd = [
        sys.executable,
        str(Path(__file__).parent / "smoke_render.py"),
        str(file),
        scene,
        "--quality",
        quality,
        "--timeout",
        str(timeout),
    ]
    print(f"[run] {' '.join(cmd)}")
    return subprocess.call(cmd)


def main():
    parser = argparse.ArgumentParser(description="批量冒烟测试（低质量渲染）")
    parser.add_argument("--file", action="append", help="Manim 源文件，可多次指定")
    parser.add_argument("--scene", action="append", help="场景名，可多次指定")
    parser.add_argument("--quality", default="pql", help="manim 质量，默认 pql")
    parser.add_argument("--timeout", type=int, default=120, help="每个任务超时时间（秒）")
    args = parser.parse_args()

    files = args.file
    if not files:
        files = [str(p) for p in Path(".").glob("sobel_v*.py")]
    scenes = args.scene or ["FullSobelVideo"]

    failures = 0
    for f in files:
        fpath = Path(f)
        if not fpath.exists():
            print(f"[skip] 文件不存在: {fpath}")
            continue
        for scene in scenes:
            rc = run_one(fpath, scene, args.quality, args.timeout)
            if rc != 0:
                print(f"[fail] {fpath}:{scene} 退出码 {rc}")
                failures += 1
            else:
                print(f"[ok] {fpath}:{scene}")

    if failures:
        print(f"总计失败 {failures} 项")
        sys.exit(1)
    print("全部通过")


if __name__ == "__main__":
    main()

