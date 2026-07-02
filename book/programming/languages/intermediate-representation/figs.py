# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODE_BG = "#0f1b14"   # темна заливка код-блоків у фігурах
CODE_FG = "#eaf6ee"
IR_BG   = "#2a230f"   # проміжний код
IR_FG   = "#f0dca0"
ASM_BG  = "#13202a"
ASM_FG  = "#7fe0a0"


def codebox(x, y, w, h, s, fg=CODE_FG, bg=CODE_BG, size=12, rx=8):
    """Темна рамка з моноширинним рядком, вирівняним ліворуч (для коду у фігурах)."""
    out = rect(x, y, w, h, fill=bg, stroke="#0a120d", sw=1.4, rx=rx)
    out += ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', monospace" '
            'font-size="%d" fill="%s" text-anchor="start" font-weight="700">%s</text>'
            % (x + 14, y + h / 2 + size * 0.35, size, fg, esc(s)))
    return out


def codebox_lines(x, y, w, h, lines, fg=CODE_FG, bg=CODE_BG, size=11.5, rx=8):
    """Темна рамка з кількома моноширинними рядками (список)."""
    out = rect(x, y, w, h, fill=bg, stroke="#0a120d", sw=1.4, rx=rx)
    ty = y + 18
    for ln in lines:
        out += ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', monospace" '
                'font-size="%d" fill="%s" text-anchor="start">%s</text>'
                % (x + 14, ty, size, fg, esc(ln)))
        ty += size * 1.5
    return out


# ── nm-vs-nplusm: чому потрібне спільне проміжне подання ───────────────────────
# Ідея: ліворуч — кожна мова окремо перекладається в кожне ядро (N×M стрілок,
# каша); праворуч — усе сходиться в спільне IR, звідти в кожне ядро (N+M).
def fig_nm_vs_nplusm():
    W, H = 820, 470
    p = []
    langs = ["C", "C++", "Rust", "Swift"]
    cores = ["ARM", "RISC-V", "Xtensa", "AVR"]

    # ── ліва схема: без IR ──
    p.append(text(200, 60, "БЕЗ спільного IR", size=13, color=POS, bold=True))
    p.append(text(200, 78, "окремий перекладач на КОЖНУ пару", size=10, color=MUTED, italic=True))
    lx_lang, lx_core = 70, 330
    ly0, dy = 110, 68
    lpos, cpos = {}, {}
    for i, l in enumerate(langs):
        b, bw, bh = textbox(lx_lang, ly0 + i * dy, l, size=11, bold=True, fill="#eef6ef", stroke=FIELD, color=FIELD, min_w=64)
        p.append(b); lpos[i] = (lx_lang + bw / 2, ly0 + i * dy)
    for j, c in enumerate(cores):
        b, bw, bh = textbox(lx_core, ly0 + j * dy, c, size=11, bold=True, fill="#eef4ff", stroke=NEG, color=NEG, min_w=76)
        p.append(b); cpos[j] = (lx_core - bw / 2, ly0 + j * dy)
    for i in range(len(langs)):
        for j in range(len(cores)):
            x1, y1 = lpos[i]; x2, y2 = cpos[j]
            p.append(line(x1, y1, x2, y2, color=POS, sw=0.8))
    p.append(text(200, ly0 + 3 * dy + 54, "N × M перекладачів", size=12, color=POS, bold=True))

    # ── розділювач ──
    p.append(line(W / 2, 96, W / 2, H - 40, color="#d0d4d8", sw=1.4, dash="5 4"))

    # ── права схема: з IR ──
    p.append(text(W / 2 + 200, 60, "ЗІ спільним IR", size=13, color=FIELD, bold=True))
    p.append(text(W / 2 + 200, 78, "фронт на мову + бек на ядро", size=10, color=MUTED, italic=True))
    rx_lang = W / 2 + 60
    rx_ir = W / 2 + 210
    rx_core = W / 2 + 340
    rpos, rcpos = {}, {}
    for i, l in enumerate(langs):
        b, bw, bh = textbox(rx_lang, ly0 + i * dy, l, size=11, bold=True, fill="#eef6ef", stroke=FIELD, color=FIELD, min_w=60)
        p.append(b); rpos[i] = (rx_lang + bw / 2, ly0 + i * dy)
    for j, c in enumerate(cores):
        b, bw, bh = textbox(rx_core, ly0 + j * dy, c, size=11, bold=True, fill="#eef4ff", stroke=NEG, color=NEG, min_w=72)
        p.append(b); rcpos[j] = (rx_core - bw / 2, ly0 + j * dy)
    # центральний вузол IR
    iry = ly0 + 1.5 * dy
    ib, ibw, ibh = textbox(rx_ir, iry, "IR", size=18, bold=True, fill=IR_BG, stroke="#b8860b", color=IR_FG, min_w=70)
    for i in range(len(langs)):
        x1, y1 = rpos[i]
        p.append(line(x1, y1, rx_ir - ibw / 2, iry, color=FIELD, sw=1.3))
    for j in range(len(cores)):
        x2, y2 = rcpos[j]
        p.append(line(rx_ir + ibw / 2, iry, x2, y2, color=NEG, sw=1.3))
    p.append(ib)
    p.append(text(W / 2 + 200, ly0 + 3 * dy + 54, "N + M частин", size=12, color=FIELD, bold=True))

    p.append(text(W / 2, H - 18, "IR — спільне русло: додав мову — пиши лише фронт; додав ядро — лише бек",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "nm-vs-nplusm.svg"), W, H, *p,
           title="Навіщо IR: N×M перекладачів чи N+M частин")


# ── ladder: сходинка форм — текст → AST → IR → асемблер ───────────────────────
# Ідея: IR — це проміжна сходинка між деревом (близько до мови) і асемблером
# (близько до заліза); показати ту саму дію в кожній формі.
def fig_ladder():
    W, H = 720, 470
    p = []
    x0, bw = 60, 600
    rows = [
        ("вихідний код", "близько до людини", "sum = a + b * 2;", CODE_BG, CODE_FG),
        ("AST (дерево)", "структура виразу", "(=  sum  (+ a (* b 2)))", "#1a2230", "#bcd0ff"),
        ("IR (три адреси)", "нейтральне до заліза", None, IR_BG, IR_FG),
        ("асемблер", "команди ядра", None, ASM_BG, ASM_FG),
    ]
    ir_lines = ["t1 = b * 2", "t2 = a + t1", "sum = t2"]
    asm_lines = ["mul  r2, r_b, #2", "add  r3, r_a, r2", "str  r3, [sum]"]
    y = 66
    bh1, bh3 = 46, 78
    gap = 30
    for i, (lab, sub, code, bg, fg) in enumerate(rows):
        h = bh3 if code is None else bh1
        p.append(text(x0, y - 8, lab, size=12, color=INK, anchor="start", bold=True))
        p.append(text(x0 + bw, y - 8, sub, size=10, color=MUTED, anchor="end", italic=True))
        if code is not None:
            p.append(codebox(x0, y, bw, h, code, size=12.5, bg=bg, fg=fg))
        elif i == 2:
            p.append(codebox_lines(x0, y, bw, h, ir_lines, bg=bg, fg=fg, size=12))
        else:
            p.append(codebox_lines(x0, y, bw, h, asm_lines, bg=bg, fg=fg, size=12))
        ny = y + h + gap
        if i < len(rows) - 1:
            ax = x0 + bw / 2
            p.append(arrow(ax, y + h + 2, ax, ny - 6, color=INK, sw=2.0))
            lbl = ["парсер ↓", "кодоген IR ↓", "кодоген ядра ↓"][i]
            p.append(text(ax + 14, y + h + gap / 2 + 4, lbl, size=10, color=MUTED, anchor="start", bold=True))
        y = ny
    # виноски збоку
    p.append(text(x0, y + 6, "чим нижче — тим менше «мови», тим більше «заліза»; IR посередині: без обох",
                  size=10.5, color=INK, bold=True, anchor="start"))
    render(os.path.join(OUT, "ladder.svg"), W, H, *p,
           title="Сходинка форм: текст → дерево → IR → асемблер")


# ── tac-cfg: три-адресний код і граф керування (basic blocks) ─────────────────
# Ідея: IR ріже програму на прості лінійні блоки, зв'язані стрілками переходів —
# це граф потоку керування (CFG), над яким і працює оптимізатор.
def fig_tac_cfg():
    W, H = 760, 460
    p = []
    p.append(text(W / 2, 54, "if (x > 0)  y = x;  else  y = -x;   z = y + 1;",
                  size=13, color=INK, bold=True))
    p.append(text(W / 2, 74, "той самий фрагмент — як граф простих блоків IR", size=10, color=MUTED, italic=True))

    # блок-умова (вершина)
    top = ["t1 = x > 0", "br t1, B1, B2"]
    p.append(codebox_lines(280, 100, 200, 56, top, bg=IR_BG, fg=IR_FG, size=11.5))
    p.append(text(380, 96, "B0", size=11, color="#b8860b", bold=True, anchor="middle"))

    # дві гілки
    b1 = ["y = x", "jmp B3"]
    b2 = ["y = 0 - x", "jmp B3"]
    p.append(codebox_lines(90, 210, 200, 56, b1, bg=IR_BG, fg=IR_FG, size=11.5))
    p.append(text(190, 206, "B1  (then)", size=11, color=FIELD, bold=True, anchor="middle"))
    p.append(codebox_lines(470, 210, 200, 56, b2, bg=IR_BG, fg=IR_FG, size=11.5))
    p.append(text(570, 206, "B2  (else)", size=11, color=NEG, bold=True, anchor="middle"))

    # блок-злиття
    b3 = ["z = y + 1", "ret z"]
    p.append(codebox_lines(280, 340, 200, 56, b3, bg=IR_BG, fg=IR_FG, size=11.5))
    p.append(text(380, 336, "B3  (злиття)", size=11, color=POS, bold=True, anchor="middle"))

    # стрілки переходів
    p.append(arrow(340, 156, 200, 204, color=FIELD, sw=1.8)); p.append(text(250, 178, "t1≠0", size=9, color=FIELD, bold=True))
    p.append(arrow(420, 156, 560, 204, color=NEG, sw=1.8)); p.append(text(512, 178, "t1=0", size=9, color=NEG, bold=True))
    p.append(arrow(200, 266, 330, 336, color=INK, sw=1.8))
    p.append(arrow(560, 266, 430, 336, color=INK, sw=1.8))

    p.append(text(W / 2, H - 16, "кожен блок — рівний ланцюжок «одна дія на рядок»; стрілки — можливі переходи",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "tac-cfg.svg"), W, H, *p,
           title="Три адреси й граф керування: з чого зроблене IR")


# ── ssa-phi: одне присвоєння на ім'я і φ на злитті ────────────────────────────
# Ідея: у SSA кожне ім'я записують РІВНО раз (y1, y2…); там, де шляхи сходяться,
# φ-функція вибирає, яке значення прийшло — і залежності стають явними.
def fig_ssa_phi():
    W, H = 720, 420
    p = []
    p.append(text(W / 2, 52, "SSA: кожне ім'я — записане рівно один раз", size=13, color=INK, bold=True))

    # умова
    p.append(codebox(255, 84, 210, 34, "br  x>0, then, else", bg=IR_BG, fg=IR_FG, size=11.5))

    # дві гілки — різні номери одного y
    p.append(codebox(90, 176, 200, 34, "y1 = x", bg=IR_BG, fg=IR_FG, size=12))
    p.append(text(190, 168, "then", size=10, color=FIELD, bold=True))
    p.append(codebox(430, 176, 200, 34, "y2 = 0 - x", bg=IR_BG, fg=IR_FG, size=12))
    p.append(text(530, 168, "else", size=10, color=NEG, bold=True))

    # злиття з φ
    phi_lines = ["y3 = φ(y1, y2)", "z1 = y3 + 1"]
    p.append(codebox_lines(255, 280, 210, 56, phi_lines, bg="#2c1030", fg="#f0c8ff", size=12.5))
    p.append(text(360, 274, "злиття", size=10, color=POS, bold=True))

    # стрілки
    p.append(arrow(300, 118, 190, 170, color=FIELD, sw=1.8))
    p.append(arrow(420, 118, 530, 170, color=NEG, sw=1.8))
    p.append(arrow(190, 210, 300, 274, color=INK, sw=1.8))
    p.append(arrow(530, 210, 420, 274, color=INK, sw=1.8))

    # пояснення φ
    p.append(rect(60, 350, 600, 46, fill="#fdf0ff", stroke="#a020c0", sw=1.4, rx=10))
    p.append(text(360, 372, "φ вибирає, ЯКЕ значення прийшло: з гілки then → y1, з else → y2.",
                  size=11, color=INK, bold=True))
    p.append(text(360, 388, "Це не машинна команда — підказка компілятору, звідки взялося ім'я.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "ssa-phi.svg"), W, H, *p,
           title="SSA і φ-функція: одне присвоєння, явні залежності")


# ── hist-timeline: дві мрії, три десятиліття ──────────────────────────────────
# Ідея: зверху лінія часу з трьома віхами — 1958 (UNCOL: ідея є, реалізації нема),
# 1988 (SSA: назва й φ), 1991 (ефективний алгоритм). Показати прірву в 30 років
# між мрією про спільну проміжну мову та зрілим інструментом навколо неї.
def fig_hist_timeline():
    W, H = 820, 340
    p = []
    p.append(text(W / 2, 30, "Дві мрії про проміжну форму — і прірва між ними",
                  size=15, color=INK, bold=True))

    # вісь часу
    ax_y = 150
    p.append(line(70, ax_y, W - 60, ax_y, color=INK, sw=2.2))
    for yr, xf in [("1958", 70), ("1988", 560), ("1991", 700)]:
        x = xf
        p.append(line(x, ax_y - 6, x, ax_y + 6, color=INK, sw=2.0))
        p.append(text(x, ax_y + 26, yr, size=12, color=MUTED, bold=True))

    # віха 1958 — UNCOL (мрія без реалізації)
    b1, w1, h1 = textbox(155, 88, "UNCOL\nмрія є,\nреалізації нема",
                         size=11, bold=True, fill="#2a230f", stroke="#b8860b",
                         color=IR_FG, min_w=140)
    p.append(b1)
    p.append(arrow(130, 88 + h1 / 2 + 2, 78, ax_y - 8, color="#b8860b", sw=1.6))

    # віха 1988 — SSA: назва й φ
    b2, w2, h2 = textbox(560, 96, "SSA: назва\nй φ-функція",
                         size=11, bold=True, fill="#2c1030", stroke="#a020c0",
                         color="#f0c8ff", min_w=140)
    p.append(b2)
    p.append(arrow(560, 96 + h2 / 2 + 2, 560, ax_y - 8, color="#a020c0", sw=1.6))

    # віха 1991 — ефективний алгоритм
    b3, w3, h3 = textbox(700, 232, "ефективний\nалгоритм\n(dominance\nfrontiers)",
                         size=10.5, bold=True, fill="#13202a", stroke=FIELD,
                         color=ASM_FG, min_w=150)
    p.append(b3)
    p.append(arrow(700, ax_y + 8, 700, 200, color=FIELD, sw=1.6))

    # дуга прірви 1958→1988
    p.append(line(78, ax_y - 20, 560, ax_y - 20, color=MUTED, sw=1.2, dash="4 4"))
    p.append(text(319, ax_y - 26, "≈ 30 років", size=11, color=MUTED, bold=True, italic=True))

    p.append(text(W / 2, H - 20,
                  "спільна проміжна мова — стара мрія; практичну міць їй дала аж форма SSA",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title=None)


# ── hist-ssa-lineage: родовід SSA ─────────────────────────────────────────────
# Ідея: SSA не впала з неба — це ланцюг ідей: розставляння псевдоприсвоєнь на
# злиттях (Shapiro-Saint 1970) → φ у обході дерева домінування (Reif 1978) →
# birthpoints (1986) → назва «SSA» й φ (Rosen-Wegman-Zadeck 1988) →
# швидка побудова через dominance frontiers (Cytron та ін. 1991).
def fig_hist_ssa_lineage():
    W, H = 760, 470
    p = []
    p.append(text(W / 2, 30, "Родовід SSA: ланцюг ідей, не один винахід",
                  size=15, color=INK, bold=True))

    steps = [
        ("1970", "Shapiro · Saint", "де ставити псевдо-\nприсвоєння на злиттях", FILL, INK, LINE),
        ("1978", "Reif", "φ-розстановка обходом\nдерева домінування", FILL, INK, LINE),
        ("1986", "birthpoints", "«місця народження»\nзмінних + переіменування", "#eef6ef", INK, FIELD),
        ("1988", "Rosen · Wegman · Zadeck", "НАЗВА «SSA» і φ-функція\n(колишня «phony function»)", "#2c1030", "#f0c8ff", "#a020c0"),
        ("1991", "Cytron · Ferrante · RWZ", "швидка побудова через\ndominance frontiers", "#13202a", ASM_FG, FIELD),
    ]
    x0 = 120
    y = 78
    dy = 76
    for i, (yr, who, what, bg, fg, st) in enumerate(steps):
        # рік — ліворуч
        p.append(text(x0 - 44, y + 4, yr, size=13, color=MUTED, bold=True, anchor="middle"))
        # рамка-крок
        b, bw, bh = textbox(x0 + 240, y, what, size=11, bold=False,
                            fill=bg, stroke=st, color=fg, min_w=300)
        p.append(b)
        # автор — над рамкою, ліворуч від тексту
        p.append(text(x0 + 90, y - bh / 2 - 8, who, size=11.5, color=st if st != LINE else INK,
                      bold=True, anchor="start"))
        # стрілка вниз до наступного
        if i < len(steps) - 1:
            p.append(arrow(x0 + 240, y + bh / 2 + 2, x0 + 240, y + dy - bh / 2 - 2,
                           color=INK, sw=1.8))
        y += dy

    render(os.path.join(OUT, "hist-ssa-lineage.svg"), W, H, *p,
           title=None)


if __name__ == "__main__":
    fig_nm_vs_nplusm()
    fig_ladder()
    fig_tac_cfg()
    fig_ssa_phi()
    fig_hist_timeline()
    fig_hist_ssa_lineage()
    print("OK: figures written to", OUT)
