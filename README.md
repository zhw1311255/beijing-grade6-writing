# beijing-grade6-writing｜北京六年级语文 + 英语作文技能

一个 WorkBuddy 用户级 Skill：按**人教版（统编版）语文**和**北京版英语**教材，写北京小学六年级的作文 / 书面表达。对话里先给参考范文与思路说明，再按需生成 **Word 或 PDF 其中一种**文件（也可以只要文字、不出文件）。

> 定位是**参考范文**，鼓励孩子换成自己的真实经历重写，不要照抄上交。语文、英语都遵守卷面硬约束：**不得出现真实校名和师生姓名**。
> 教材版本（人教版 / 北京版）与考试口径（北京各区期末、毕业考、小升初）是两件事，已分别处理。

仓库地址：<https://github.com/zhw1311255/beijing-grade6-writing>

---

## 一、最快的方式：把下面这段话发给 WorkBuddy

把整段复制给对方的 WorkBuddy（Agent 模式），它会自动下载并装好：

```
帮我安装一个 WorkBuddy 技能，仓库地址：https://github.com/zhw1311255/beijing-grade6-writing

请按下面做：
1. 用 git clone 或下载 ZIP 把仓库内容取到临时目录；如果网络不通，我会把 zip 放到工作区，你用本地文件即可。
2. 目标目录是 ~/.workbuddy/skills/beijing-grade6-writing/
   （Windows 即 %USERPROFILE%\.workbuddy\skills\beijing-grade6-writing）。
   仓库根目录本身就是技能根目录，请把 SKILL.md、references/、scripts/ 直接放在这个目录下，
   不要多套一层仓库文件夹。
3. 如果目标目录已存在，先告诉我，不要直接覆盖。
4. 装完检查：目录下有 SKILL.md，且开头有 name 和 description；
   运行 python scripts/check_writing.py --help 确认脚本可用。
5. 不要修改或删除我的其他技能。
6. 完成后告诉我安装路径，提醒我新开一个对话才会加载，再给我 3 条使用示例。
```

一句话简版（同样能触发，细节让 AI 自己判断）：

```
从 https://github.com/zhw1311255/beijing-grade6-writing 安装 beijing-grade6-writing 技能到 ~/.workbuddy/skills/，装完告诉我怎么用。
```

> 说明：这个技能**没有上架技能市场**，所以直接说"安装 beijing-grade6-writing"在市场里搜不到；必须带上仓库地址，或用下面的手动方式。

---

## 二、手动安装（三选一）

Skill 本质就是一个含 `SKILL.md` 的文件夹，放进用户级技能目录就生效，不需要编译、不需要注册。

### 方式 A：一行命令（推荐）

**Windows PowerShell**

```powershell
git clone https://github.com/zhw1311255/beijing-grade6-writing.git "$HOME\.workbuddy\skills\beijing-grade6-writing"
```

**macOS / Linux / Git Bash**

```bash
git clone https://github.com/zhw1311255/beijing-grade6-writing.git ~/.workbuddy/skills/beijing-grade6-writing
```

仓库根目录就是技能根目录，`SKILL.md` 直接在最外层，clone 完即可用，不用再挪文件。

### 方式 B：下载 ZIP

在仓库页面点 **Code → Download ZIP**（或把别人发你的 `beijing-grade6-writing.zip` 存下来），解压后把**里面那一层**文件夹整个放进技能目录。

⚠️ GitHub 下载的 ZIP 解压后是 `beijing-grade6-writing-main/`，里面才是 `SKILL.md`。不要把它连同外层一起塞进去，也不要出现
`skills/beijing-grade6-writing-main/SKILL.md` 这种多套一层的结构。正确结果是：

```
~/.workbuddy/skills/beijing-grade6-writing/SKILL.md
~/.workbuddy/skills/beijing-grade6-writing/references/
~/.workbuddy/skills/beijing-grade6-writing/scripts/
```

### 方式 C：项目级安装（只在某个项目里用）

把同一个文件夹放到 `项目目录/.workbuddy/skills/beijing-grade6-writing/`，只对该项目生效，适合团队成员共享。

### 装完自检

```bash
python ~/.workbuddy/skills/beijing-grade6-writing/scripts/check_writing.py --help
```

能打印出参数说明就说明 Python 与脚本正常。**装完请新开一个对话**再使用——当前会话可能已缓存技能列表，不会立刻识别新技能。

---

## 三、装完之后怎么说话（使用提示词示例）

| 想做的事 | 直接说 |
| --- | --- |
| 语文，默认给 Word | `写一篇人教版六上《有你，真好》，450 字` |
| 只要文字，不出文件 | `不用文件，直接给我文字，写一篇《家乡的风俗》` |
| 只要 PDF | `给我 PDF 就行，写一篇《插上科学的翅膀飞》，450 字` |
| 明确两种格式都要 | `写一篇《难忘小学生活》，Word 和 PDF 都要` |
| 英语，北京版单元 | `北京版英语 Unit 1 的暑假小作文，不少于 5 句` |
| 英语，只要文字 | `My Summer Vacation，50 词左右，只要文字不要文件` |
| 语文英语都要 | `语文英语各写一篇，都要 Word` |
| 带孩子真实素材 | `写一篇《那一刻，我长大了》，用我给的素材：帮妈妈照顾发烧的妹妹，450 字` |

**默认规则**：只说"写一篇作文" → 正文 + 1 个 `.docx`；说"PDF" → 正文 + 1 个 `.pdf`；说"不用文件" → 只有正文；只有明确说"两种都要"才出两个文件。

默认值：语文 450 字 / 5–7 段 / 记叙文；英语 6–8 句 / 50–60 词 / 简单句为主 / 时态统一。题目有明确要求时一律以题目为准。

---

## 四、环境与依赖

| 用途 | 依赖 |
| --- | --- |
| 只出正文 | 无，纯文本 |
| 生成 Word | Python 3 + `python-docx`（`pip install python-docx`） |
| 生成 PDF | Python 3 + 本机 **Edge 或 Chrome**（脚本自动查找，Windows / macOS / Linux 路径都覆盖）；**无需任何第三方 PDF 库或字体包**，中文由系统字体渲染 |
| 字数/句数/禁真实姓名自检 | `scripts/check_writing.py`，无依赖 |

PDF 走浏览器无头打印 HTML，输出的是可复制、可检索的文字 PDF（含嵌入字体子集），不是图片。

脚本也可以单独用：

```bash
python scripts/make_outputs.py --title "成长里的温暖" --lang zh --input draft.txt --output-dir ./作文
# 加 --format pdf 只出 PDF；--format both 出两种
```

---

## 五、目录结构

```
beijing-grade6-writing/
├── SKILL.md                     # 技能入口：触发规则、交付规则、工作流
├── references/
│   ├── chinese.md               # 人教版六上/六下单元习作 + 北京卷面口径
│   ├── english.md               # 北京版单元话题 + 小升初书面表达要求
│   └── playbook.md              # 写法手册：开头结尾、细节描写、常见扣分点
└── scripts/
    ├── check_writing.py         # 成稿自检（字数、句数、真实姓名、成人腔等）
    ├── make_docx.py             # A4 稿纸 Word（中文首行缩进 2 字符）
    ├── make_pdf.py              # A4 稿纸 PDF（浏览器无头打印）
    └── make_outputs.py          # 按需入口：--format docx|pdf|both，默认 docx
```

`README.md` 只是仓库说明，不属于技能本体；克隆后留在目录里不影响技能加载。

---

## 六、常见问题

**Q：装了却没反应？**
新开一个对话再试；并确认 `SKILL.md` 直接位于 `skills/beijing-grade6-writing/` 下，没有多套一层文件夹。

**Q：生成 Word 报 `No module named 'docx'`？**
执行 `pip install python-docx`。或者先说"只要文字 / 给我 PDF"，PDF 不需要这个库。

**Q：生成 PDF 失败？**
确认本机装了 Edge 或 Chrome。Linux 无图形界面时也支持 `chromium` / `google-chrome` 的命令行版本。

**Q：教材版本不对？**
语文固定人教版（统编版），英语固定北京版，考试口径按北京。用户给出课本原题或单元名时，一律以用户给的为准，不会擅自换成别的版本。

**Q：能给别人用吗？**
仓库是公开的，直接把链接发过去即可；也可以直接把 `beijing-grade6-writing.zip` 发给对方手动解压。
