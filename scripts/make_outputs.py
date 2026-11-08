#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""作文文件生成入口：按需只出一种格式（默认 Word），明确要求时才出两种。

用法：
  python make_outputs.py --title "成长里的温暖" --lang zh --input draft.txt                  # 仅 Word（默认）
  python make_outputs.py --title "成长里的温暖" --lang zh --input draft.txt --format pdf    # 仅 PDF
  python make_outputs.py --title "成长里的温暖" --lang zh --input draft.txt --format both   # 两种都要

依赖：make_docx.py 需要 python-docx；make_pdf.py 需要本机 Edge 或 Chrome（无需额外安装）。
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

TARGETS = {
    "docx": [("make_docx.py", "docx")],
    "pdf": [("make_pdf.py", "pdf")],
    "both": [("make_docx.py", "docx"), ("make_pdf.py", "pdf")],
}


def safe_stem(title):
    return re.sub(r'[\\/:*?"<>|\r\n]', "_", title).strip()[:60] or "作文"


def main():
    ap = argparse.ArgumentParser(description="按需生成作文文件（默认仅 Word）")
    ap.add_argument("--title", required=True, help="作文题目")
    ap.add_argument("--lang", choices=["zh", "en"], required=True)
    ap.add_argument("--input", required=True, help="UTF-8 纯文本正文文件")
    ap.add_argument("--output-dir", default=".", help="输出目录，默认当前目录")
    ap.add_argument("--name", default="", help="输出文件名（不含扩展名），默认用题目")
    ap.add_argument("--format", choices=["docx", "pdf", "both"], default="docx",
                    help="交付格式：docx（默认，仅 Word）/ pdf（仅 PDF）/ both（两种都要）")
    args = ap.parse_args()

    src = Path(args.input).resolve()
    if not src.exists():
        sys.exit(f"找不到正文文件：{src}")
    outdir = Path(args.output_dir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    stem = args.name or safe_stem(args.title)

    common = ["--title", args.title, "--lang", args.lang, "--input", str(src)]
    produced, failed = [], []
    for script, ext in TARGETS[args.format]:
        out = outdir / f"{stem}.{ext}"
        cmd = [sys.executable, str(HERE / script)] + common + ["--output", str(out)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.stdout.strip():
            print(proc.stdout.strip())
        if proc.returncode == 0 and out.exists() and out.stat().st_size > 0:
            produced.append(out)
        else:
            failed.append(ext)
            print(f"[FAIL] {ext} 生成失败：{(proc.stderr or proc.stdout).strip()}", file=sys.stderr)

    print("---")
    print(f"交付格式：{args.format}｜成功 {len(produced)} 个文件："
          + ("、".join(p.name for p in produced) or "无"))
    if failed:
        print("失败格式：" + "、".join(failed))
        if "docx" in failed:
            print("提示：python-docx 未安装时执行 pip install python-docx")
        if "pdf" in failed:
            print("提示：确认本机已安装 Edge 或 Chrome，且允许无头模式")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
