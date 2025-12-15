"""
快速扫描 Manim 脚本中的中文/Emoji 使用是否合规：
- 检查 MathTex/Tex 是否包含中文或 Emoji（应改用 Text/safer_text + VGroup 混排）
- 提醒直接使用 Text 时的 Emoji 可能缺字体

用法（在 03_Integration 下执行）:
    python tools/check_text_safety.py --root .
"""

import argparse
import pathlib
import re
import sys

CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")
EMOJI_PATTERN = re.compile(r"[\U0001F300-\U0001FAFF]")


def has_cjk(s: str) -> bool:
    return bool(CJK_PATTERN.search(s))


def has_emoji(s: str) -> bool:
    return bool(EMOJI_PATTERN.search(s))


def scan_file(path: pathlib.Path):
    issues = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for lineno, line in enumerate(f, 1):
            # 粗匹配 MathTex/Tex 调用中的字符串字面量
            if "MathTex" in line or "Tex(" in line:
                if has_cjk(line) or has_emoji(line):
                    issues.append((lineno, "MathTex/Tex 中包含中文或 Emoji"))
            if "Text(" in line:
                if has_emoji(line):
                    issues.append((lineno, "Text 中包含 Emoji，Linux 可能缺字体导致空白"))
    return issues


def main():
    parser = argparse.ArgumentParser(description="扫描中文/Emoji 使用风险")
    parser.add_argument("--root", default=".", help="扫描起始目录（递归）")
    parser.add_argument(
        "--glob",
        default="sobel_*.py",
        help="匹配的文件模式（默认 sobel_*.py）",
    )
    args = parser.parse_args()

    root = pathlib.Path(args.root)
    files = sorted(root.rglob(args.glob))

    total_issues = 0
    for file in files:
        issues = scan_file(file)
        if issues:
            print(f"[!] {file}")
            for lineno, msg in issues:
                print(f"    L{lineno}: {msg}")
            total_issues += len(issues)

    if total_issues == 0:
        print("✅ 未发现中文/Emoji 违规使用 MathTex/Tex 或 Emoji 风险。")
    else:
        print(f"共发现 {total_issues} 处需要处理。")
        sys.exit(1)


if __name__ == "__main__":
    main()

