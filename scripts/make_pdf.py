#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把作文正文生成 A4 PDF（零第三方依赖，用本机 Edge / Chrome 无头打印）。

用法：
  python make_pdf.py --title "成长里的温暖" --lang zh --input draft.txt --output "成长里的温暖.pdf"

原理：生成带 @page 样式的 HTML，交给浏览器 --headless --print-to-pdf 输出 PDF。
中文字体由系统字体（宋体 / 黑体 / Times New Roman）直接渲染，无需安装 PDF 库或字体包。
"""
import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/microsoft-edge",
]

CSS_ZH = """
@page { size: A4; margin: 2.54cm 3.17cm; }
html, body { margin: 0; padding: 0; }
body { font-family: "SimSun", "宋体", "NSimSun", serif; font-size: 12pt;
       line-height: 1.5; color: #000; }
h1 { font-family: "SimHei", "黑体", sans-serif; font-size: 16pt; font-weight: bold;
     text-align: center; margin: 0 0 12pt 0; }
p.body { text-indent: 2em; text-align: justify; margin: 0; page-break-inside: avoid; }
p.count { text-align: right; font-size: 10.5pt; margin: 12pt 0 0 0; text-indent: 0; }
"""

CSS_EN = """
@page { size: A4; margin: 2.54cm 3.17cm; }
html, body { margin: 0; padding: 0; }
body { font-family: "Times New Roman", Times, serif; font-size: 12pt;
       line-height: 1.5; color: #000; }
h1 { font-size: 14pt; font-weight: bold; text-align: center; margin: 0 0 12pt 0; }
p.body { text-indent: 0; text-align: left; margin: 0; page-break-inside: avoid; }
p.count { text-align: right; font-size: 10.5pt; margin: 12pt 0 0 0; text-indent: 0; }
"""


def find_browser():
    for p in BROWSERS:
        if Path(p).exists():
            return p
    for name in ("msedge", "google-chrome", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    return None


def safe_stem(title):
    return re.sub(r'[\\/:*?"<>|\r\n]', "_", title).strip()[:60] or "作文"


def core_body_en(text):
    """词数统计排除称呼与落款，与 check_writing.py / make_docx.py 一致。"""
    kept, skip_tail = [], False
    for ln in text.splitlines():
        s = ln.strip()
        if not s or skip_tail:
            continue
        if re.match(r"^(Dear|Yours|Sincerely|From)\b", s, re.I) and not s.endswith((".", "!", "?")):
            if re.match(r"^Yours", s, re.I):
                skip_tail = True
            continue
        kept.append(s)
    return "\n".join(kept)


def build_html(title, lines, lang, note):
    css = CSS_ZH if lang == "zh" else CSS_EN
    parts = [
        "<!DOCTYPE html>", '<html lang="zh-CN">' if lang == "zh" else '<html lang="en">',
        "<head>", '<meta charset="utf-8">',
        "<title>" + html.escape(title) + "</title>",
        "<style>" + css + "</style>", "</head><body>",
        "<h1>" + html.escape(title.strip("《》")) + "</h1>",
    ]
    for line in lines:
        parts.append('<p class="body">' + html.escape(line) + "</p>")
    parts.append('<p class="count">' + html.escape(note) + "</p>")
    parts.append("</body></html>")
    return "\n".join(parts)


def render_pdf(browser, html_path, tmp_pdf, profile):
    base = [
        browser, "--disable-gpu", "--no-sandbox", "--no-first-run",
        "--disable-extensions", "--disable-background-networking",
        "--no-pdf-header-footer", "--print-to-pdf-no-header",
        "--virtual-time-budget=3000",
        f"--user-data-dir={profile}",
        f"--print-to-pdf={tmp_pdf}",
    ]
    for flag in ("--headless=new", "--headless"):
        if tmp_pdf.exists():
            tmp_pdf.unlink()
        try:
            subprocess.run(base[:1] + [flag] + base[1:] + [html_path.as_uri()],
                           capture_output=True, text=True, timeout=90)
        except (subprocess.TimeoutExpired, OSError):
            continue
        if tmp_pdf.exists() and tmp_pdf.stat().st_size > 1000:
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description="生成北京六年级作文 PDF")
    ap.add_argument("--title", required=True, help="作文题目")
    ap.add_argument("--lang", choices=["zh", "en"], required=True)
    ap.add_argument("--input", required=True, help="UTF-8 纯文本正文文件")
    ap.add_argument("--output", default="", help="输出 .pdf 路径")
    ap.add_argument("--no-count", action="store_true", help="不附字数统计行")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.exists():
        sys.exit(f"找不到正文文件：{src}")
    raw = src.read_text(encoding="utf-8-sig")
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    norm = lambda s: s.strip("《》\"'“” ").replace(" ", "")
    if lines and norm(lines[0]) == norm(args.title):
        lines = lines[1:]
    if not lines:
        sys.exit("正文为空")

    browser = find_browser()
    if not browser:
        sys.exit("未找到 Edge / Chrome，无法生成 PDF。请安装浏览器，或改用 make_docx.py 输出 Word。")

    out = Path(args.output) if args.output else Path.cwd() / (safe_stem(args.title) + ".pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(lines)
    if args.lang == "zh":
        count = len(re.findall(r"[\u4e00-\u9fff]", body))
        note = f"（全文 {count} 字）"
    else:
        count = len(re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", core_body_en(body)))
        note = f"({count} words, 不含称呼与落款)"
    if args.no_count:
        note = ""

    with tempfile.TemporaryDirectory(prefix="wb_pdf_") as td:
        tmp = Path(td)
        html_path = tmp / "essay.html"
        html_path.write_text(build_html(args.title, lines, args.lang, note), encoding="utf-8")
        tmp_pdf = tmp / "out.pdf"
        if not render_pdf(browser, html_path, tmp_pdf, tmp / "profile"):
            sys.exit("浏览器打印 PDF 失败；可重试一次，或检查浏览器是否被策略禁用无头模式。")
        shutil.copyfile(tmp_pdf, out)

    print(f"OK: {out}")
    print(f"题目：{args.title}｜语言：{'语文' if args.lang == 'zh' else '英语'}｜统计：{note or '未附'}｜段落：{len(lines)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
