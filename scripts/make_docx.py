#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把作文正文生成排版好的 Word 文档（北京六年级语文 / 英语稿纸规格）。

用法：
  python make_docx.py --title "成长里的温暖" --lang zh --input draft.txt --output "成长里的温暖.docx"
  python make_docx.py --title "My Summer Vacation" --lang en --input draft.txt --output "My_Summer_Vacation.docx"

依赖 python-docx（缺失时执行 pip install python-docx）。
"""
import argparse
import re
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt
except ImportError:
    sys.exit("缺少依赖 python-docx，请先运行：pip install python-docx")


def set_font(run, name, size, bold=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = False
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), name)
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)


def set_first_line_chars(paragraph, chars=200):
    """按中文习惯设首行缩进 N 字符（200 = 2 字符）。"""
    ppr = paragraph._p.get_or_add_pPr()
    ind = ppr.find(qn("w:ind"))
    if ind is None:
        ind = OxmlElement("w:ind")
        ppr.append(ind)
    ind.set(qn("w:firstLineChars"), str(chars))


def base_paragraph(paragraph, line_spacing=1.5):
    pf = paragraph.paragraph_format
    pf.line_spacing = line_spacing
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.widow_control = True


def safe_name(title):
    cleaned = re.sub(r'[\\/:*?"<>|\r\n]', "_", title).strip() or "作文"
    return cleaned[:60] + ".docx"


def core_body_en(text):
    """词数统计排除称呼与落款，与 check_writing.py 保持一致。"""
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


def main():
    ap = argparse.ArgumentParser(description="生成北京六年级作文 Word 文档")
    ap.add_argument("--title", required=True, help="作文题目")
    ap.add_argument("--lang", choices=["zh", "en"], required=True)
    ap.add_argument("--input", required=True, help="UTF-8 纯文本正文文件")
    ap.add_argument("--output", default="", help="输出 .docx 路径")
    ap.add_argument("--no-count", action="store_true", help="不附字数统计行")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.exists():
        sys.exit(f"找不到正文文件：{src}")
    raw = src.read_text(encoding="utf-8-sig")

    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    # 若正文首行重复写了题目，去掉以免 Word 里出现两次
    norm = lambda s: s.strip("《》\"'“” ").replace(" ", "")
    if lines and norm(lines[0]) == norm(args.title):
        lines = lines[1:]
    if not lines:
        sys.exit("正文为空")

    out = Path(args.output) if args.output else Path.cwd() / safe_name(args.title)
    out.parent.mkdir(parents=True, exist_ok=True)

    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)  # A4
    sec.top_margin = sec.bottom_margin = Cm(2.54)
    sec.left_margin = sec.right_margin = Cm(3.17)

    zh = args.lang == "zh"
    title_font = "宋体" if zh else "Times New Roman"
    body_font = "宋体" if zh else "Times New Roman"

    p = doc.add_paragraph()
    base_paragraph(p, 1.5)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    set_font(p.add_run(args.title.strip("《》")), title_font, 16 if zh else 14, bold=True)

    for line in lines:
        para = doc.add_paragraph()
        base_paragraph(para, 1.5)
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if zh else WD_ALIGN_PARAGRAPH.LEFT
        if zh:
            set_first_line_chars(para, 200)
        set_font(para.add_run(line), body_font, 12)

    body_text = "\n".join(lines)
    if zh:
        count = len(re.findall(r"[\u4e00-\u9fff]", body_text))
        note = f"（全文 {count} 字）"
    else:
        count = len(re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", core_body_en(body_text)))
        note = f"({count} words, 不含称呼与落款)"
    if not args.no_count:
        tail = doc.add_paragraph()
        base_paragraph(tail, 1.5)
        tail.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        tail.paragraph_format.space_before = Pt(12)
        set_font(tail.add_run(note), body_font, 10.5)

    doc.save(str(out))
    print(f"OK: {out}")
    print(f"题目：{args.title}｜语言：{'语文' if zh else '英语'}｜统计：{note}｜段落：{len(lines)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
