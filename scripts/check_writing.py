#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北京六年级作文成稿自检（语文 / 英语）。

用法：
  python check_writing.py --lang zh --input draft.txt --min 450
  python check_writing.py --lang en --input draft.txt --min-words 50 --min-sentences 5
  python check_writing.py --lang en --input draft.txt --require "museum,plane,grandparents"

输出 RESULT 为 PASS / WARN / FAIL；FAIL 项必须修订后重跑。
"""
import argparse
import re
import sys
from pathlib import Path

HAN = r"[\u4e00-\u9fff]"

ADULT_TONE = [
    "岁月静好", "氤氲", "旖旎", "斑驳", "镌刻", "潸然", "婆娑", "缱绻", "韶华",
    "浮生", "惊艳了时光", "温柔了岁月", "静谧", "呢喃", "阑珊", "荏苒", "皎洁的月光",
    "不忘初心", "砥砺前行", "谱写华章", "赋能", "格局", "闭环", "洗礼", "升华",
    "人生的真谛", "生命的意义", "在这一刻我顿悟", "灵魂", "诗和远方",
]
NET_WORDS = [
    "yyds", "绝绝子", "破防了", "拿捏", "栓Q", "emo", "躺平", "内卷",
    "泰裤辣", "尊嘟", "666", "笑死", "太顶了",
]
CLICHE_OPEN = [
    "光阴似箭", "日月如梭", "白驹过隙", "记忆的长河", "翻开记忆的相册",
    "往事如烟", "时光荏苒", "岁月如梭", "在记忆的星空",
]

GENERIC_SCHOOL_PREFIX = {
    "我们", "我校", "本校", "这所", "那所", "全", "我们这所", "乡村", "山里",
    "我们這個", "整个", "附近", "新的", "旧的",
}
GENERIC_PERSON = {
    "语文", "数学", "英语", "体育", "美术", "音乐", "科学", "班", "班主任",
    "我的", "我们", "那位", "这位", "新来的", "代课", "位", "小", "老", "好",
}

EN_ADVANCED = [
    r"\balthough\b", r"\bhowever\b", r"\bwhich\b", r"\bwhom\b",
    r"\bhave been\b", r"\bhas been\b", r"\bhad been\b", r"\bwould\b",
    r"\bif I were\b", r"\bnot only\b", r"\bdespite\b",
]
PAST_MARKERS = ["went", "saw", "had", "did", "was", "were", "visited", "played",
                "got", "took", "made", "ate", "bought", "yesterday", "last "]
FUTURE_MARKERS = ["will ", "am going to", "is going to", "are going to",
                  "tomorrow", "next ", "plan"]


def report():
    return {"FAIL": [], "WARN": [], "INFO": []}


def add(rep, level, msg):
    rep[level].append(msg)


def strip_title(text, title):
    """若正文首行就是题目，去掉后再统计，避免字数虚高。"""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return "", []
    first = lines[0].strip("《》\"'“” ")
    t = (title or "").strip("《》\"'“” ")
    if t and first == t:
        return "\n".join(lines[1:]), lines[1:]
    if not t and len(first) <= 20 and not re.search(r"[。！？,.!?]", first):
        # 未提供 title 时把短首行视作题目
        return "\n".join(lines[1:]), lines[1:]
    return "\n".join(lines), lines


def check_school_names(rep, text):
    hits = []
    for m in re.finditer(HAN + r"{2,8}(?:附属小学|实验小学|小学|中学|学校|学院)", text):
        frag = m.group(0)
        prefix = re.match(HAN + r"{2,8}", frag).group(0)
        # 去掉"学校/小学"等后缀后剩下的专名部分
        stem = re.sub(r"(?:附属小学|实验小学|小学|中学|学校|学院)$", "", prefix)
        if stem in GENERIC_SCHOOL_PREFIX or not stem:
            continue
        hits.append(frag)
    if hits:
        add(rep, "WARN", "疑似真实校名，需改为泛称： " + "、".join(sorted(set(hits))[:5]))
    for m in re.finditer(r"\b[A-Z][a-zA-Z]+ Primary School\b", text):
        add(rep, "WARN", "英文中出现疑似真实校名： " + m.group(0))


def check_zh(rep, body, lines, args):
    han_count = len(re.findall(HAN, body))
    total_chars = len(re.sub(r"\s", "", body))
    para = len(lines)
    add(rep, "INFO", f"汉字数 {han_count}（含标点共 {total_chars} 字符），段落 {para} 段")

    if han_count < args.min:
        add(rep, "FAIL", f"汉字数 {han_count} < 要求 {args.min}，需补足具体细节而非加套话")
    if args.max and han_count > args.max:
        add(rep, "WARN", f"汉字数 {han_count} > 上限 {args.max}，详略可能失衡")
    if para < 3:
        add(rep, "FAIL", f"仅 {para} 段，六年级要求分段表述，建议 5–7 段")
    elif para > 9:
        add(rep, "WARN", f"共 {para} 段，段落偏碎，可合并相邻段")

    if not args.title:
        add(rep, "INFO", "未指定 --title，已按首行推断题目；统计不含该行")

    for w in NET_WORDS:
        if w.lower() in body.lower():
            add(rep, "FAIL", f"出现网络用语「{w}」，须替换为生活化表达")
    found_tone = [w for w in ADULT_TONE if w in body]
    if found_tone:
        add(rep, "WARN", "成人腔/空话词，建议换成具体细节： " + "、".join(found_tone[:8]))
    found_cliche = [w for w in CLICHE_OPEN if w in body[:80]]
    if found_cliche:
        add(rep, "FAIL", "开头用了套话，改为直接进场景： " + "、".join(found_cliche))

    check_school_names(rep, body)
    names = []
    for m in re.finditer(HAN + r"{1,2}(?:老师|校长)", body):
        frag = m.group(0)
        stem = re.sub(r"(?:老师|校长)$", "", frag)
        if stem in GENERIC_PERSON:
            continue
        names.append(frag)
    if names:
        add(rep, "WARN", "出现疑似师生真实姓名，请确认是化名或改用称谓： " + "、".join(sorted(set(names))[:5]))

    bad_punct = re.findall(r"[,;:?!\"']", body)
    if bad_punct:
        add(rep, "FAIL", f"中文正文混入英文标点 {len(bad_punct)} 处，改用全角标点")
    if "。。" in body or "！！" in body or "………" in body:
        add(rep, "WARN", "存在重复标点")
    long_sentences = [s for s in re.split(r"[。！？]", body) if len(re.findall(HAN, s)) > 60]
    if long_sentences:
        add(rep, "WARN", f"有 {len(long_sentences)} 句超过 60 字，建议拆成短句")


def core_body_en(body):
    """统计时排除无句末标点的称呼行与落款行。"""
    kept, skip_tail = [], False
    for ln in body.splitlines():
        s = ln.strip()
        if not s or skip_tail:
            continue
        if re.match(r"^(Dear|Yours|Sincerely|From)\b", s, re.I) and not s.endswith((".", "!", "?")):
            if re.match(r"^Yours", s, re.I):
                skip_tail = True  # 其后为署名
            continue
        kept.append(s)
    return "\n".join(kept)


def check_en(rep, body, lines, args):
    core = core_body_en(body)
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", core)
    sentences = [s.strip() for s in re.split(r"[.!?]+", core) if s.strip()]
    word_count, sent_count = len(words), len(sentences)
    add(rep, "INFO", f"词数 {word_count}，句数 {sent_count}，平均句长 "
                     f"{(word_count / sent_count if sent_count else 0):.1f} 词（不含称呼与落款）")

    if word_count < args.min_words:
        add(rep, "FAIL", f"词数 {word_count} < 要求 {args.min_words}")
    if sent_count < args.min_sentences:
        add(rep, "FAIL", f"句数 {sent_count} < 要求 {args.min_sentences}")
    if sent_count and word_count / sent_count > 18:
        add(rep, "WARN", "平均句长偏长，小学阶段宜用 8–16 词的简单句")
    if word_count > (args.min_words or 30) * 3:
        add(rep, "WARN", "词数远超题目下限，注意别写成中学篇幅")

    lower = core.lower()
    has_past = any(k in lower for k in PAST_MARKERS)
    has_future = any(k in lower for k in FUTURE_MARKERS)
    if has_past and has_future:
        add(rep, "WARN", "同时出现过去时与将来时标志词，须确认题目允许分段叙述，否则统一时态")
    for pat in EN_ADVANCED:
        if re.search(pat, lower):
            add(rep, "WARN", f"出现超纲结构 / 高级表达：{pat}，建议改用小学句型")
    if re.search(HAN, core):
        add(rep, "WARN", "英文正文中出现汉字，检查是否混入中文注释")

    bad_starts = []
    for s in sentences:
        first = re.search(r"[A-Za-z]", s)
        if first and first.group(0).islower() and not s.lstrip().startswith("Dear"):
            bad_starts.append(s[:20])
    if bad_starts:
        add(rep, "WARN", "部分句子首字母疑似未大写： " + " / ".join(bad_starts[:3]))
    if not core.rstrip().endswith((".", "!", "?", '"')):
        add(rep, "WARN", "正文末尾缺少句末标点")
    check_school_names(rep, body)
    add(rep, "INFO", "人工复核：三单 -s、时态一致、名词单复数、a/an、拼写、"
                     "信息点是否逐条覆盖、有无真实姓名、应用文称呼与落款")


def check_requirements(rep, body, args):
    if not args.require:
        return
    missing = [k.strip() for k in args.require.split(",")
               if k.strip() and k.strip().lower() not in body.lower()]
    if missing:
        add(rep, "FAIL", "题目信息点/关键词未覆盖： " + "、".join(missing))
    else:
        add(rep, "INFO", "必需关键词已全部覆盖")


def main():
    ap = argparse.ArgumentParser(description="北京六年级作文成稿自检")
    ap.add_argument("--lang", choices=["zh", "en"], required=True)
    ap.add_argument("--input", required=True, help="UTF-8 纯文本正文文件")
    ap.add_argument("--title", default="", help="作文题目，用于排除首行")
    ap.add_argument("--min", type=int, default=400, help="语文最少汉字数")
    ap.add_argument("--max", type=int, default=0, help="语文汉字数上限，可选")
    ap.add_argument("--min-words", type=int, default=30, help="英语最少词数")
    ap.add_argument("--min-sentences", type=int, default=5, help="英语最少句数")
    ap.add_argument("--require", default="", help="必须出现的信息点关键词，逗号分隔")
    args = ap.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"找不到文件：{path}")
        return 2
    raw = path.read_text(encoding="utf-8-sig")
    body, lines = strip_title(raw, args.title)
    if not body.strip():
        print("正文为空")
        return 2

    rep = report()
    if args.lang == "zh":
        check_zh(rep, body, lines, args)
    else:
        check_en(rep, body, lines, args)
    check_requirements(rep, body, args)

    for level in ("INFO", "WARN", "FAIL"):
        for msg in rep[level]:
            print(f"[{level}] {msg}")
    result = "FAIL" if rep["FAIL"] else ("WARN" if rep["WARN"] else "PASS")
    print(f"RESULT: {result}")
    return 1 if result == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
