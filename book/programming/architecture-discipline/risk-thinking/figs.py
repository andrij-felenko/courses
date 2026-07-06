# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: експозиція = ймовірність × втрата (три панелі-площі) ──────────
def fig_exposure():
    W, H = 940, 470
    els = []
    els.append(text(W / 2, 30, "Експозиція = ймовірність × втрата: важить ПЛОЩА, не висота й не ширина", size=16, bold=True))

    # три окремі панелі-квадранти; у кожній прямокутник ризику від спільного кута
    panels = [
        (60,  "A: ймовірна\nдрібниця",   0.85, 0.20, NEG,   "#eaf0fd", "0.85 × 0.2"),
        (350, "B: рідкісна\nкатастрофа", 0.15, 0.95, POS,   "#fdecea", "0.15 × 0.95"),
        (640, "C: середній\nризик",       0.50, 0.55, FIELD, "#eafaf0", "0.5 × 0.55"),
    ]
    px = 210          # сторона квадранта в пікселях
    base_y = 360      # низ квадранта (вісь втрати=0 / ймовірності=0)

    for x0, label, p, loss, color, fillc, formula in panels:
        # рамка-квадрант
        els.append(rect(x0, base_y - px, px, px, fill=BG, stroke="#d0d0d0", sw=1, rx=2))
        # осі всередині
        els.append(line(x0, base_y, x0 + px, base_y, color=MUTED, sw=1))   # X втрата
        els.append(line(x0, base_y, x0, base_y - px, color=MUTED, sw=1))   # Y ймовірність
        # прямокутник експозиції (від лівого-нижнього кута)
        w = loss * px
        h = p * px
        els.append(rect(x0, base_y - h, w, h, fill=fillc, stroke=color, sw=2, rx=2))
        # підпис ризику — НАД квадрантом, у власній рамці
        b, bw, bh = textbox(x0 + px / 2, base_y - px - 34, label, size=13, bold=True,
                            min_w=170, fill=BG, stroke=color, color=color)
        els.append(b)
        # формула площі — під квадрантом
        els.append(text(x0 + px / 2, base_y + 24, "площа = " + formula, size=12, color=INK, bold=True))

    # осьові підписи (лише під першою панеллю, щоб не дублювати)
    els.append(text(60 + px / 2, base_y + 44, "ширина = втрата · висота = ймовірність", size=11, color=MUTED, italic=True))

    els.append(text(W / 2, H - 20, "площа A ≈ площа B: часта дрібниця й рідкісна катастрофа важать майже порівну — рангує лише добуток",
                    size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'exposure.svg'), W, H, *els)


# ── Фігура 2: чотири клітини знання про ризик ───────────────────────────────
def fig_known_unknowns():
    W, H = 900, 540
    els = []
    els.append(text(W / 2, 30, "Що ми знаємо про власне незнання: чотири клітини", size=16, bold=True))

    # сітка 2×2
    gx, gy = 190, 90               # лівий-верхній кут поля клітин
    cw, ch = 300, 175             # розмір клітини
    gap = 16

    # осьові підписи (поза сіткою)
    els.append(text(gx + cw / 2, gy - 28, "усвідомлюємо", size=13, bold=True, color=MUTED))
    els.append(text(gx + cw + gap + cw / 2, gy - 28, "НЕ усвідомлюємо", size=13, bold=True, color=MUTED))
    els.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
               'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">знаємо</text>'
               % (gx - 32, gy + ch / 2, FONT, MUTED, gx - 32, gy + ch / 2))
    els.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
               'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">НЕ знаємо</text>'
               % (gx - 32, gy + ch + gap + ch / 2, FONT, MUTED, gx - 32, gy + ch + gap + ch / 2))

    cells = [
        (0, 0, "Відоме відоме", "факти, на які спираємось.\nПросто робимо.", "#eafaf0", FIELD),
        (1, 0, "Відоме невідоме", "названий ризик.\nЙого В РЕЄСТР —\nмоніторити й гасити.", "#eaf0fd", NEG),
        (0, 1, "Невідоме відоме", "мовчазне знання команди,\nне вимовлене вголос.\nВитягти рев'ю.", "#fff8e1", "#b8860b"),
        (1, 1, "Невідоме невідоме", "чого й уявити не можемо.\nПроти нього — лише\nзапас і зворотність.", "#fdecea", POS),
    ]
    for col, row, title, body, fillc, strokec in cells:
        x = gx + col * (cw + gap)
        y = gy + row * (ch + gap)
        els.append(rect(x, y, cw, ch, fill=fillc, stroke=strokec, sw=2, rx=8))
        els.append(text(x + cw / 2, y + 32, title, size=15, bold=True, color=strokec))
        els.append(mtext(x + cw / 2, y + 66, body, size=12.5, color=INK, lh=1.32))

    els.append(text(W / 2, H - 20, "інженерна пара «known/unknown unknowns» — з аерокосмічної практики кінця 1960-х (unk-unks)",
                    size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'known-unknowns.svg'), W, H, *els)


# ── Фігура 3: чотири відповіді на ризик, розкладені за експозицією ──────────
def fig_responses():
    W, H = 940, 470
    els = []
    els.append(text(W / 2, 30, "Один ризик — чотири відповіді; яку обрати, диктує експозиція", size=16, bold=True))

    # центр: сам ризик
    cx = W / 2
    br, wr, hr = textbox(cx, 96, "РИЗИК\n(ймовірність × втрата)", size=14, bold=True,
                         min_w=250, fill="#f7f7f7", stroke=INK)
    els.append(br)

    # чотири гілки вниз, у власні рамки з великим кроком
    row_y = 250
    cells = [
        (150, "Уникнути", "прибрати причину:\nінший шлях, де ризику нема", "#eafaf0", FIELD),
        (383, "Зменшити", "збити ймовірність або втрату:\nтест, шов, надлишок", "#eaf0fd", NEG),
        (616, "Передати", "віддати тому, хто впорається:\nстрахування, SLA, хмара", "#fff8e1", "#b8860b"),
        (849, "Прийняти", "лишити свідомо + запас;\nдешевше, ніж боротися", "#fdecea", POS),
    ]
    for bx, title, body, fillc, strokec in cells:
        b, bw, bh = textbox(bx, row_y, title, size=14, bold=True, min_w=170,
                            fill=fillc, stroke=strokec, color=strokec)
        els.append(b)
        els.append(mtext(bx, row_y + 58, body, size=12, color=INK, lh=1.3))
        els.append(arrow(cx, 96 + hr / 2, bx, row_y - bh / 2))

    els.append(text(W / 2, H - 44, "мала експозиція → прийняти й записати; велика → уникнути чи зменшити, поки дешево;",
                    size=12, color=INK))
    els.append(text(W / 2, H - 22, "не своя компетенція → передати. «Нічого не робити» — теж вибір, лише коли він свідомий",
                    size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'responses.svg'), W, H, *els)


# ── Фігура 4: два варіанти як стоси ризиків, порівняння сумарної експозиції ──
def fig_exposure_decision():
    W, H = 940, 620
    els = []
    els.append(text(W / 2, 30, "Сумарна експозиція = стос ризиків-прямокутників; порівнюємо два шляхи", size=16, bold=True))

    # вісь-масштаб: 1 одиниця експозиції = SCALE пікселів висоти
    base_y = 540          # низ стосів (експозиція = 0)
    scale = 16.0          # px на одиницю експозиції (макс стос ~25 → ~400 px)
    col_w = 190           # ширина колонки-стосу

    # сегменти кожного варіанта: (підпис, експозиція, колір-заливка, колір-обведення)
    mono = [
        ("вузьке місце\n0.5×20 = 10.0", 10.0, "#fdecea", POS),
        ("точка відмови\n0.2×15 = 3.0",  3.0, "#eaf0fd", NEG),
        ("міграції\n0.3×8 = 2.4",        2.4, "#eafaf0", FIELD),
        ("звіти\n0.4×5 = 2.0",           2.0, "#fff8e1", "#b8860b"),
    ]
    cache = [
        ("неузгодженість\n0.6×12 = 7.2", 7.2, "#fdecea", POS),
        ("інвалідація\n0.5×10 = 5.0",    5.0, "#fdecea", POS),
        ("крива навчання\n0.6×8 = 4.8",  4.8, "#fff8e1", "#b8860b"),
        ("вузьке місце\n0.15×20 = 3.0",  3.0, "#eaf0fd", NEG),
        ("розгортання\n0.5×5 = 2.5",     2.5, "#eafaf0", FIELD),
        ("вузол кешу\n0.4×6 = 2.4",      2.4, "#eafaf0", FIELD),
    ]

    def draw_stack(cx, title, segs):
        total = sum(e for _, e, _, _ in segs)
        x0 = cx - col_w / 2
        y = base_y
        for label, e, fillc, strokec in segs:
            h = e * scale
            y -= h
            els.append(rect(x0, y, col_w, h, fill=fillc, stroke=strokec, sw=1.5, rx=2))
            # підпис у власну рамку — праворуч від сегмента, щоб не лягав на лінії
            b, bw, bh = textbox(cx, y + h / 2, label, size=10.5, min_w=col_w - 16,
                                fill=BG, stroke=strokec, color=INK, pad=5)
            els.append(b)
        # підсумкова висота стосу — вісь зверху
        top = base_y - total * scale
        els.append(line(x0 - 12, top, x0 + col_w + 12, top, color=INK, sw=2, dash="5 4"))
        b2, _, _ = textbox(cx, top - 24, "Σ = %.1f" % total, size=15, bold=True,
                           min_w=120, fill=BG, stroke=INK, color=INK)
        els.append(b2)
        # назва варіанта під колонкою
        els.append(text(cx, base_y + 26, title, size=15, bold=True))

    draw_stack(255, "Варіант M — моноліт", mono)
    draw_stack(690, "Варіант P — кеш",    cache)

    # спільна вісь-підпис ліворуч
    els.append('<text x="40" y="%.1f" font-family="%s" font-size="12" fill="%s" '
               'text-anchor="middle" font-style="italic" transform="rotate(-90 40 %.1f)">'
               'експозиція, людино-дні (вище = гірше)</text>'
               % (base_y - 180, FONT, MUTED, base_y - 180))

    els.append(text(W / 2, H - 22, "кеш збиває головну скелю моноліта (тонкий сегмент вузького місця), "
                    "та власні ризики переважують — за грубими числами моноліт легший",
                    size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'exposure-decision.svg'), W, H, *els)


if __name__ == '__main__':
    fig_exposure()
    fig_known_unknowns()
    fig_responses()
    fig_exposure_decision()
    print("figs done")
