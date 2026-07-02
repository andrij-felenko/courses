# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODE_BG = "#0f1b14"
CODE_FG = "#eaf6ee"
ASM_BG  = "#13202a"
ASM_FG  = "#7fe0a0"


def codeblock(x, y, w, lines, fg=CODE_FG, bg=CODE_BG, size=12, title=None, tcol="#9fb4a6"):
    """Темна рамка з кількома моноширинними рядками, вирівняними ліворуч."""
    lh = size * 1.5
    top_pad = 14 if title else 10
    h = top_pad + len(lines) * lh + 8
    out = rect(x, y, w, h, fill=bg, stroke="#0a120d", sw=1.4, rx=8)
    ty = y + top_pad
    if title:
        out += ('<text x="%.1f" y="%.1f" font-family="%s" font-size="10" fill="%s" '
                'text-anchor="start" font-weight="700">%s</text>' % (x + 12, ty, FONT, tcol, esc(title)))
        ty += lh
    for ln in lines:
        out += ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', monospace" '
                'font-size="%d" fill="%s" text-anchor="start">%s</text>'
                % (x + 12, ty + size * 0.4, size, fg, esc(ln)))
        ty += lh
    return out, h


# ── as-if: той самий видимий результат, різні законні машинні коди ────────────
def fig_as_if():
    W, H = 860, 360
    p = []
    p.append(text(W / 2, 26, "Правило «наче-так»: результат один, шляхів багато", size=17, bold=True))
    # джерело зверху по центру
    src, sh = codeblock(300, 50, 260, ["int y = 0;", "for (int i=0;i<4;i++)", "    y += 3;", "return y;"],
                        title="ЯК НАПИСАНО (C)")
    p.append(src)
    # три законні виходи знизу
    outs = [
        (30, "«у лоб» (-O0)", ["y=0", "loop i=0..3:", "  y=y+3", "ret y"], ASM_FG),
        (320, "розгорнуто", ["y=0", "y=y+3", "y=y+3", "y=y+3", "y=y+3", "ret y"], ASM_FG),
        (610, "пораховано наперед", ["ret 12"], "#ffd479"),
    ]
    ytop = 220
    for x, lab, lines, fg in outs:
        blk, bh = codeblock(x, ytop, 240, lines, fg=fg, bg=ASM_BG, title=lab, tcol="#7fa8c0")
        p.append(blk)
        p.append(arrow(430, 50 + sh, x + 120, ytop - 4, color=MUTED, sw=1.6))
    p.append(text(W / 2, H - 16,
                  "усі три повертають 12 — компілятор вільний обрати будь-який, аби видимий результат збігся",
                  size=12, color=INK, italic=True))
    render(os.path.join(OUT, "as-if.svg"), W, H, *p, title=None)


# ── каскад: одне перетворення відмикає наступне (fixpoint) ────────────────────
def fig_cascade():
    W, H = 880, 330
    p = []
    p.append(text(W / 2, 26, "Оптимізації живлять одна одну — прохід за проходом", size=17, bold=True))
    stages = [
        (20, "вихід", ["a = 5;", "b = a + 3;", "c = b * 2;", "use(c);", "d = a - 1;  // d не вжито"], CODE_FG, CODE_BG),
        (250, "згортання + поширення", ["a = 5;", "b = 8;", "c = 16;", "use(c);", "d = 4;      // все ще не вжито"], "#bfe3cf", CODE_BG),
        (500, "прибирання мертвого", ["", "", "c = 16;", "use(c);", ""], "#bfe3cf", CODE_BG),
        (720, "лишилось", ["use(16);"], "#ffd479", ASM_BG),
    ]
    ytop = 90
    ys = []
    for x, lab, lines, fg, bg in stages:
        blk, bh = codeblock(x, ytop, 200 if x < 700 else 150, lines, fg=fg, bg=bg, title=lab,
                            tcol="#9fb4a6")
        p.append(blk)
        ys.append((x, x + (200 if x < 700 else 150), bh))
    for i in range(len(ys) - 1):
        p.append(arrow(ys[i][1] + 4, ytop + 55, ys[i + 1][0] - 4, ytop + 55, color=INK, sw=2))
    p.append(text(W / 2, H - 40,
                  "згорнули сталі → відкрилося, що d нікуди не йде → викинули → зайвих обчислень нема",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, H - 18,
                  "компілятор ганяє проходи по колу, доки код перестане мінятися (нерухома точка)",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "cascade.svg"), W, H, *p, title=None)


# ── обрій: що «бачить» оптимізація — вузьке вічко → цикл → уся функція ─────────
def fig_scope():
    W, H = 820, 380
    p = []
    p.append(text(W / 2, 26, "Обрій оптимізації: що вона взагалі здатна побачити", size=17, bold=True))
    rows = [
        ("Вічко (peephole)", "кілька сусідніх команд", "прибрати load одразу за store", "#eef6ef", FIELD),
        ("Базовий блок", "прямий шматок без розгалужень", "згортання, поширення в межах блоку", "#eef6ef", FIELD),
        ("Цикл", "тіло + межа циклу", "виніс інваріанта, розгортання", "#fff4e0", "#d08a1a"),
        ("Уся функція (global)", "усі шляхи виконання разом", "аналіз живучості, розподіл регістрів", "#eef4ff", NEG),
        ("Уся програма (LTO)", "усі файли на лінкуванні", "інлайн між файлами, глобальне прибирання", "#fdecf0", POS),
    ]
    y = 55
    rh = 58
    for name, sees, gives, fill, col in rows:
        p.append(fitbox(30, y, 220, rh, name, size=13, fill=fill, stroke=col, sw=2, bold=True, color=col))
        p.append(fitbox(265, y, 250, rh, sees, size=11, fill=BG, stroke=MUTED, sw=1.2, color=INK))
        p.append(fitbox(530, y, 260, rh, gives, size=11, fill=BG, stroke=MUTED, sw=1.2, color=INK))
        y += rh + 8
    p.append(text(140, H - 14, "ширший обрій → більше нагод, але дорожчий аналіз", size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "scope.svg"), W, H, *p, title=None)


# ── FORTRAN як парі: буквальний переклад vs оптимізований нарівні з асемблером ─
def fig_fortran_bet():
    W, H = 860, 400
    p = []
    p.append(text(W / 2, 26, "Парі FORTRAN (1957): переклад мусив не поступитися ручному коду", size=16, bold=True))
    # формула зверху по центру
    src, sh = codeblock(320, 48, 230, ["DO 10 I = 1, N", "   A(I) = B(I) + C*D", "10 CONTINUE"],
                        title="ФОРМУЛА (FORTRAN)")
    p.append(src)
    ytop = 210
    # ліворуч: буквальний повільний
    bad, bh = codeblock(30, ytop, 360,
                        ["кожної ітерації рахувати C*D наново,",
                         "щоразу множити I на розмір,",
                         "щоразу лізти в пам'ять по A,B,C,D",
                         "→ повільно, як боялися замовники"],
                        fg="#ff9e9e", bg=ASM_BG, title="буквально (так НЕ купили б)", tcol="#c88")
    p.append(bad)
    # праворуч: оптимізований швидкий
    good, gh = codeblock(470, ytop, 360,
                         ["C*D порахувати ОДИН раз до циклу,",
                          "адресу вести кроком, без множень,",
                          "гарячі значення тримати в регістрах",
                          "→ нарівні з рукописним асемблером"],
                         fg=ASM_FG, bg=ASM_BG, title="оптимізовано (саме це виграло парі)", tcol="#7fa8c0")
    p.append(good)
    p.append(arrow(400, 48 + sh, 200, ytop - 4, color="#a55", sw=1.8))
    p.append(arrow(470, 48 + sh, 650, ytop - 4, color=POS, sw=2))
    p.append(text(W / 2, H - 16,
                  "замовники брали високорівневу мову лише за швидкий код — тож перший успішний компілятор мусив оптимізувати",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(OUT, "fortran-bet.svg"), W, H, *p, title=None)


# ── народження графа потоку керування: текст → граф (внесок Аллен) ─────────────
def fig_cfg_birth():
    W, H = 880, 440
    p = []
    p.append(text(W / 2, 26, "Зсув, що зробила Аллен: програму бачити не як текст, а як граф", size=16, bold=True))
    # ЛІВОРУЧ: лінійний текст
    src, sh = codeblock(36, 66, 300,
                        ["x = 0;", "if (n > 0)", "    x = f(n);", "while (x < 10)", "    x = x + 1;", "return x;"],
                        title="ЯК ТЕКСТ — питання доводиться вгадувати")
    p.append(src)
    p.append(text(186, 66 + sh + 24, "чи жива x? чи є шлях сюди? — неясно", size=11, color=MUTED, italic=True))

    # ПРАВОРУЧ: граф потоку керування (вузли по 120px завширшки → півширина 60)
    BW = 120
    cx0 = 560            # центральна колона
    cxL = 470            # ліва гілка (x=f(n))
    cxR = 760            # права колона (тіло циклу)
    entry = (cx0, 72)
    cond  = (cx0, 138)
    then  = (cxL, 210)
    loopc = (cx0, 284)
    body  = (cxR, 284)
    exit_ = (cx0, 366)

    def blk(cx, cy, s, col=NEG, fill="#eef4ff"):
        return textbox(cx, cy, s, size=11, fill=fill, stroke=col, sw=1.8, color=col, bold=True, min_w=BW)[0]

    # стрілки спершу (щоб лягли під вузли); half-height рамки ≈ 15
    p.append(arrow(entry[0], entry[1] + 15, cond[0], cond[1] - 15, color=INK, sw=1.6))                 # entry→cond
    p.append(arrow(cond[0] - 30, cond[1] + 15, then[0] + 30, then[1] - 15, color=INK, sw=1.6))         # cond→then (гілка)
    p.append(arrow(cond[0] + 8, cond[1] + 15, loopc[0] + 8, loopc[1] - 15, color=INK, sw=1.6))         # cond→loop (напряму)
    p.append(arrow(then[0] + 30, then[1] + 15, loopc[0] - 30, loopc[1] - 15, color=INK, sw=1.6))       # then→loop
    p.append(arrow(loopc[0] + 60, loopc[1] - 8, body[0] - 60, body[1] - 8, color="#d08a1a", sw=1.8))   # loop→body (верх)
    p.append(arrow(body[0] - 60, body[1] + 8, loopc[0] + 60, loopc[1] + 8, color="#d08a1a", sw=1.8))   # body→loop (низ, назад)
    p.append(arrow(loopc[0], loopc[1] + 15, exit_[0], exit_[1] - 15, color=INK, sw=1.6))               # loop→exit
    # підписи ребер
    p.append(text((loopc[0] + body[0]) / 2, loopc[1] - 14, "тіло", size=9.5, color="#b9791a"))
    p.append(text(cx0 + 40, (cond[1] + loopc[1]) / 2, "хиб.", size=9.5, color=MUTED))

    p.append(blk(*entry, "x = 0"))
    p.append(blk(*cond, "n > 0 ?"))
    p.append(blk(*then, "x = f(n)"))
    p.append(blk(*loopc, "x < 10 ?", col="#d08a1a", fill="#fff4e0"))
    p.append(blk(*body, "x = x+1", col="#d08a1a", fill="#fff4e0"))
    p.append(blk(*exit_, "return x", col=FIELD, fill="#eafaef"))
    p.append(text(cx0, H - 40, "ЯК ГРАФ — усе стає обчислюваним", size=11, color=INK, bold=True))

    p.append(text(W / 2, H - 15,
                  "досяжність, живучість, інваріантність циклу — тепер це чіткі запитання про граф, а не здогади",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(OUT, "cfg-birth.svg"), W, H, *p, title=None)


if __name__ == "__main__":
    fig_as_if()
    fig_cascade()
    fig_scope()
    fig_fortran_bet()
    fig_cfg_birth()
    print("ok")
