# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, **kw):
    """textbox повертає (body,w,h) — беремо лише SVG."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body


# ── 1. Дві мови зливаються в один стандарт ──────────────────────────────────
def one_standard():
    W, H = 760, 300
    frags = []
    frags.append(text(W / 2, 30, "Було: дві мови  →  Стало: один стандарт", size=17, bold=True))

    # ліва пара — дві розділені мови
    frags.append(box(150, 105, ["Verilog", "опис схеми"], size=14, min_w=170,
                     fill="#eaf0fd", stroke=NEG, bold=True))
    frags.append(box(150, 195, ["мова верифікації", "(Vera · OpenVera · e)", "перевірка"],
                     size=13, min_w=170, fill="#fdecea", stroke=POS))

    # стрілки до центру
    frags.append(arrow(245, 105, 400, 135))
    frags.append(arrow(245, 195, 400, 165))

    # правий блок — єдиний стандарт
    frags.append(box(560, 150, ["SystemVerilog", "IEEE 1800", "опис  +  перевірка"],
                     size=15, min_w=250, fill="#eafaf0", stroke=FIELD, bold=True))

    frags.append(text(W / 2, 285, "Verilog не зник — став підмножиною SystemVerilog",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, 'one-standard.svg'), W, H, *frags)


# ── 2. Три блоки-наміри always_* ────────────────────────────────────────────
def always_intent():
    W, H = 780, 320
    frags = []
    frags.append(text(W / 2, 30, "Оголоси намір — машина перевірить опис", size=17, bold=True))

    cols = [
        (150, "always_comb", "комбінаційна\nмережа вентилів", "без пам'яті", NEG, "#eaf0fd"),
        (390, "always_ff", "банк тригерів\nпо фронту такту", "пам'ять стану", FIELD, "#eafaf0"),
        (630, "always_latch", "прозора\nзасувка", "рідко, свідомо", POS, "#fdecea"),
    ]
    for cx, kw, what, note, col, fill in cols:
        frags.append(box(cx, 90, kw, size=15, min_w=200, fill=fill, stroke=col, bold=True))
        frags.append(arrow(cx, 118, cx, 150))
        frags.append(box(cx, 190, what, size=13, min_w=200, fill=FILL, stroke=LINE))
        frags.append(text(cx, 250, note, size=12, color=MUTED, italic=True))

    frags.append(box(W / 2, 293, "розійшлися опис і намір  →  інструмент СВАРИТЬСЯ (напр. зайва засувка в always_comb)",
                     size=12, min_w=W - 60, fill="#fff8e1", stroke="#e0a800"))
    render(os.path.join(IMG, 'always-intent.svg'), W, H, *frags)


# ── 3. Межа синтезу: залізо проти симулятора ────────────────────────────────
def synth_vs_verify():
    W, H = 780, 340
    frags = []
    frags.append(text(W / 2, 30, "Межа синтезу: що стане кремнієм, а що ні", size=17, bold=True))

    # вертикальна межа
    frags.append(line(W / 2, 52, W / 2, H - 18, color=POS, sw=2.5, dash="8 5"))
    frags.append(text(W / 2, 66, "межа синтезу", size=12, color=POS, bold=True))

    # ліва половина — синтезовне
    frags.append(text(200, 95, "Синтезовна підмножина", size=14, bold=True, color=FIELD))
    frags.append(box(200, 150, ["logic · bit", "always_ff · always_comb",
                                 "enum · struct packed"], size=13, min_w=280,
                     fill="#eafaf0", stroke=FIELD))
    frags.append(arrow(200, 190, 200, 228))
    frags.append(box(200, 265, ["СИНТЕЗАТОР  →", "реальна схема у FPGA"], size=13,
                     min_w=280, fill=FILL, stroke=LINE, bold=True))

    # права половина — верифікаційне
    frags.append(text(580, 95, "Засоби перевірки", size=14, bold=True, color=NEG))
    frags.append(box(580, 150, ["класи · об'єкти", "динамічні масиви · черги",
                                 "assertions · випадкові входи"], size=13, min_w=280,
                     fill="#eaf0fd", stroke=NEG))
    frags.append(arrow(580, 190, 580, 228))
    frags.append(box(580, 265, ["живе в СИМУЛЯТОРІ", "у кремній НЕ потрапляє"], size=13,
                     min_w=280, fill=FILL, stroke=LINE, bold=True))

    render(os.path.join(IMG, 'synth-vs-verify.svg'), W, H, *frags)


# ── 4. Два дарунки 2002-го: опис + перевірка → SystemVerilog ─────────────────
def two_gifts():
    W, H = 780, 320
    frags = []
    frags.append(text(W / 2, 30, "SystemVerilog зібрано з ДВОХ дарунків (2002)", size=17, bold=True))

    # ліворуч — Co-Design → опис
    frags.append(box(160, 105, ["Co-Design Automation", "(стартап)"], size=13, min_w=230,
                     fill="#eaf0fd", stroke=NEG, bold=True))
    frags.append(arrow(160, 133, 160, 168))
    frags.append(box(160, 205, ["Superlog", "частина: ОПИС заліза", "сучасні типи, синтез"],
                     size=13, min_w=230, fill=FILL, stroke=NEG))

    # праворуч — Synopsys → перевірка
    frags.append(box(620, 105, ["Synopsys"], size=13, min_w=230,
                     fill="#fdecea", stroke=POS, bold=True))
    frags.append(arrow(620, 133, 620, 168))
    frags.append(box(620, 205, ["OpenVera (на базі Vera)", "частина: ПЕРЕВІРКА",
                                 "тести · твердження · покриття"],
                     size=13, min_w=230, fill=FILL, stroke=POS))

    # обидві половини сходяться в центр-низ
    frags.append(arrow(275, 205, 400, 262))
    frags.append(arrow(505, 205, 400, 262))
    frags.append(box(400, 285, ["Accellera  →  SystemVerilog", "опис  +  перевірка"],
                     size=14, min_w=330, fill="#eafaf0", stroke=FIELD, bold=True))
    render(os.path.join(IMG, 'two-gifts.svg'), W, H, *frags)


# ── 5. Часова смуга: від Verilog до єдиного IEEE 1800 ────────────────────────
def sv_timeline():
    W, H = 900, 300
    frags = []
    frags.append(text(W / 2, 30, "Від Verilog до єдиного стандарту SystemVerilog", size=17, bold=True))

    x0, x1 = 60, W - 60
    axis_y = 150
    frags.append(line(x0, axis_y, x1, axis_y, color=LINE, sw=2))

    # (рік, підпис-угорі|None, підпис-унизу|None, колір крапки)
    marks = [
        (1995, None, "Verilog\nIEEE 1364", NEG),
        (1997, "Co-Design\nзасновано", None, NEG),
        (1999, None, "Мурбі\nприєднався", NEG),
        (2002, "Superlog →\nAccellera; вер. 3.0", None, FIELD),
        (2003, None, "вер. 3.1\n+верифікація", FIELD),
        (2005, "IEEE 1800", None, FIELD),
        (2009, None, "ЗЛИТТЯ:\n1364 → 1800", POS),
        (2017, "ревізії\n2012·2017·2023", None, MUTED),
    ]
    # рівні проміжки за порядком подій (не пропорційно рокам) — щоб підписи не тіснилися
    n = len(marks)
    for i, (yr, top, bot, col) in enumerate(marks):
        x = x0 + (x1 - x0) * i / (n - 1)
        big = col == POS
        frags.append(circle(x, axis_y, 7 if big else 5, fill=col, stroke=col))
        frags.append(text(x, axis_y + 26, str(yr), size=12, bold=big, color=col))
        if top:
            frags.append(line(x, axis_y - 8, x, axis_y - 34, color=col, sw=1.2))
            frags.append(mtext(x, axis_y - 48, top, size=11, color=INK))
        if bot:
            frags.append(line(x, axis_y + 34, x, axis_y + 46, color=col, sw=1.2))
            frags.append(mtext(x, axis_y + 60, bot, size=11, color=INK, bold=big))

    frags.append(text(W / 2, H - 12,
                      "2009: старший Verilog став ПІДМНОЖИНОЮ молодшого SystemVerilog",
                      size=12, color=POS, italic=True, bold=True))
    render(os.path.join(IMG, 'sv-timeline.svg'), W, H, *frags)


if __name__ == '__main__':
    one_standard()
    always_intent()
    synth_vs_verify()
    two_gifts()
    sv_timeline()
    print("figs done:", os.listdir(IMG))
