# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GREEN = FIELD
RED = POS
BLUE = NEG


def transistor(cx, cy, active):
    """Спрощений ключ вниз: коло-стан + вертикальний «дріт» до спільної шини зверху.
    active=True — тягне лінію в 0 (замкнений на землю)."""
    col = RED if active else MUTED
    body = circle(cx, cy, 16, fill="#fdecea" if active else FILL, stroke=col, sw=2)
    body += text(cx, cy + 5, "0" if active else "Z", size=15, color=col, bold=True)
    return body, col


# ── Фігура 1: спільна лінія — будь-який нуль перемагає ───────────────────────
def fig_wired():
    W, H = 720, 380
    els = []
    railY = 90                 # спільна лінія
    railX0, railX1 = 90, 630
    # пул-ап згори
    els.append(line(660, 40, 660, railY, color=RED, sw=2))
    els.append(text(660, 32, "+3.3 В", size=13, color=RED, bold=True))
    els.append(rect(650, railY - 6, 20, 46, fill="#fdecea", stroke=RED, sw=2))
    els.append(text(690, railY + 22, "R", size=13, color=RED, bold=True))
    els.append(text(690, railY + 40, "пул-ап", size=11, color=MUTED))
    els.append(line(660, railY + 40, 660, railY, color=RED, sw=2))
    # спільна лінія
    els.append(line(railX0, railY, 650, railY, color=INK, sw=3))
    els.append(text(railX0 - 4, railY - 12, "спільна лінія (шина)", size=13, anchor="start", bold=True))
    # три виходи: два «Z», один тягне «0»
    states = [(150, False), (330, True), (510, False)]
    any_low = any(s[1] for s in states)
    for cx, active in states:
        els.append(line(cx, railY, cx, 190, color=(RED if active else MUTED), sw=2.5))
        t, col = transistor(cx, 210, active)
        els.append(t)
        # земля
        els.append(line(cx, 226, cx, 250, color=col, sw=2))
        for i, wg in enumerate((26, 18, 10)):
            els.append(line(cx - wg, 250 + i * 6, cx + wg, 250 + i * 6, color=col, sw=2))
        lbl = "тягне 0" if active else "відпустив (Z)"
        els.append(text(cx, 300, "вихід %d" % ((cx - 150) // 180 + 1), size=12, bold=True))
        els.append(text(cx, 318, lbl, size=12, color=(RED if active else MUTED)))
    # підсумок стану лінії
    res = "0" if any_low else "1"
    rc = RED if any_low else GREEN
    els.append(circle(railX0 - 30, railY, 15, fill=("#fdecea" if any_low else "#eafaf1"), stroke=rc, sw=2.5))
    els.append(text(railX0 - 30, railY + 5, res, size=16, color=rc, bold=True))
    box = fitbox(200, 345, 320, 28,
                 "Один вихід у 0 — і вся лінія 0. Високо лише коли ВСІ відпустили.",
                 size=12, fill="#eafaf1", stroke=GREEN)
    els.append(box)
    render(os.path.join(OUT, 'wired-line.svg'), W, H, *els,
           title="Відкритий колектор: тягнути вниз можна, штовхати вгору — ні")


# ── Фігура 2: та сама лінія — і АБО, і І (подвійність) ───────────────────────
def fig_duality():
    W, H = 720, 340
    els = []
    cx = 360
    # центральний дріт
    els.append(rect(cx - 70, 70, 140, 44, fill=FILL, stroke=INK, sw=2))
    els.append(text(cx, 90, "один фізичний дріт", size=13, bold=True))
    els.append(text(cx, 108, "правило: нуль перемагає", size=12, color=MUTED))
    # ліва інтерпретація — активний нуль → АБО
    lx = 155
    els.append(rect(lx - 110, 165, 220, 120, fill="#eaf0fd", stroke=BLUE, sw=2, rx=8))
    els.append(text(lx, 190, "дивимось як «активний 0»", size=13, color=BLUE, bold=True))
    els.append(text(lx, 214, "0 = «так, я прошу»", size=12, color=INK))
    els.append(text(lx, 236, "лінія активна, якщо", size=12, color=INK))
    els.append(text(lx, 254, "ХОЧ ОДИН просить", size=13, color=BLUE, bold=True))
    els.append(text(lx, 276, "це монтажне АБО", size=13, color=BLUE, bold=True))
    # права інтерпретація — активна одиниця → І
    rx = 565
    els.append(rect(rx - 110, 165, 220, 120, fill="#eafaf1", stroke=GREEN, sw=2, rx=8))
    els.append(text(rx, 190, "дивимось як «активна 1»", size=13, color=GREEN, bold=True))
    els.append(text(rx, 214, "1 = «усе гаразд»", size=12, color=INK))
    els.append(text(rx, 236, "лінія висока, лише якщо", size=12, color=INK))
    els.append(text(rx, 254, "ВСІ відпустили", size=13, color=GREEN, bold=True))
    els.append(text(rx, 276, "це монтажне І", size=13, color=GREEN, bold=True))
    # стрілки від дроту
    els.append(arrow(cx - 60, 114, lx + 40, 165, color=BLUE, sw=2))
    els.append(arrow(cx + 60, 114, rx - 40, 165, color=GREEN, sw=2))
    els.append(text(cx, 315, "Логіка не в залізі, а в тім, який рівень ти назвав «активним».",
                    size=12, color=MUTED))
    render(os.path.join(OUT, 'wired-duality.svg'), W, H, *els,
           title="Той самий дріт — і АБО, і І (залежно від назви активного рівня)")


# ── Фігура 3: спільне переривання ───────────────────────────────────────────
def fig_irq():
    W, H = 720, 350
    els = []
    railY = 250
    # пул-ап
    els.append(text(70, 60, "+3.3 В", size=12, color=RED, bold=True))
    els.append(line(70, 66, 70, 110, color=RED, sw=2))
    els.append(rect(60, 110, 20, 40, fill="#fdecea", stroke=RED, sw=2))
    els.append(line(70, 150, 70, railY, color=RED, sw=2))
    # лінія IRQ до МК
    els.append(line(70, railY, 560, railY, color=INK, sw=3))
    els.append(text(80, railY + 22, "спільна лінія IRQ (активна в 0)", size=13, anchor="start", bold=True))
    # три давачі
    devs = [(180, True, "давач А"), (300, False, "давач Б"), (420, True, "давач В")]
    for x, act, name in devs:
        col = RED if act else MUTED
        els.append(rect(x - 45, 90, 90, 50, fill=FILL, stroke=col, sw=2, rx=6))
        els.append(text(x, 112, name, size=12, bold=True))
        els.append(text(x, 130, "просить" if act else "мовчить", size=11, color=col))
        els.append(line(x, 140, x, railY, color=col, sw=2))
        els.append(circle(x, railY, 4, fill=col, stroke=col))
    # МК
    els.append(rect(590, 200, 110, 100, fill="#eaf0fd", stroke=BLUE, sw=2, rx=8))
    els.append(text(645, 228, "МК", size=15, bold=True, color=BLUE))
    els.append(text(645, 250, "бачить: 0", size=12, color=RED))
    els.append(text(645, 270, "опитує всіх,", size=11))
    els.append(text(645, 286, "хто винен", size=11))
    els.append(arrow(560, railY, 590, 250, color=INK, sw=2))
    box = fitbox(150, 315, 340, 26,
                 "Одна ніжка МК на багато джерел; ISR перебирає їх і чистить кожне.",
                 size=12, fill="#eafaf1", stroke=GREEN)
    els.append(box)
    render(os.path.join(OUT, 'wired-irq.svg'), W, H, *els,
           title="Багато джерел — одна ніжка переривання")


# ── Історична нитка: як трюк виріс із дрібної економії у фундамент шин ────────
def fig_hist_thread():
    W, H = 760, 470
    els = []
    # Крок 1 — вихід без верхнього ключа (економія транзистора)
    x1 = 130
    els.append(rect(x1 - 100, 60, 200, 96, fill=FILL, stroke=INK, sw=2, rx=8))
    els.append(text(x1, 84, "КРОК 1 · дешевина", size=13, bold=True))
    els.append(text(x1, 106, "вихід без верхнього", size=12, color=INK))
    els.append(text(x1, 124, "ключа (відкритий", size=12, color=INK))
    els.append(text(x1, 142, "колектор / стік)", size=12, color=INK))
    # Крок 2 — дріт-вентиль
    x2 = 380
    els.append(rect(x2 - 100, 60, 200, 96, fill="#eaf0fd", stroke=BLUE, sw=2, rx=8))
    els.append(text(x2, 84, "КРОК 2 · вентиль", size=13, bold=True, color=BLUE))
    els.append(text(x2, 106, "кілька виходів + дріт", size=12, color=INK))
    els.append(text(x2, 124, "+ підтяжка = «АБО»", size=12, color=INK))
    els.append(text(x2, 142, "без жодного корпуса", size=12, color=INK))
    # Крок 3 — спільна шина
    x3 = 630
    els.append(rect(x3 - 100, 60, 200, 96, fill="#eafaf1", stroke=GREEN, sw=2, rx=8))
    els.append(text(x3, 84, "КРОК 3 · шина", size=13, bold=True, color=GREEN))
    els.append(text(x3, 106, "той самий дріт", size=12, color=INK))
    els.append(text(x3, 124, "розтягнуто повз", size=12, color=INK))
    els.append(text(x3, 142, "багато пристроїв", size=12, color=INK))
    els.append(arrow(x1 + 100, 108, x2 - 100, 108, color=INK, sw=2.2))
    els.append(arrow(x2 + 100, 108, x3 - 100, 108, color=INK, sw=2.2))
    # Дві класичні реалізації кроку 3
    yb = 250
    xl = 250
    els.append(rect(xl - 150, yb, 300, 150, fill=BG, stroke=GREEN, sw=2, rx=10))
    els.append(text(xl, yb + 26, "IEEE-488 / GPIB (HP)", size=14, bold=True, color=GREEN))
    els.append(text(xl, yb + 46, "ідея 1965 · стандарт 1975", size=11, color=MUTED))
    els.append(text(xl, yb + 72, "NRFD/NDAC — відкриті", size=12, color=INK))
    els.append(text(xl, yb + 90, "колектори, монтажне «АБО»", size=12, color=INK))
    els.append(text(xl, yb + 116, "чекаємо на найповільніший", size=12, color=INK, bold=True))
    els.append(text(xl, yb + 134, "прилад — без арбітра", size=12, color=INK, bold=True))
    xr = 560
    els.append(rect(xr - 150, yb, 300, 150, fill=BG, stroke=RED, sw=2, rx=10))
    els.append(text(xr, yb + 26, "лінія IRQ 6502 (1975)", size=14, bold=True, color=RED))
    els.append(text(xr, yb + 46, "багато джерел — одна ніжка", size=11, color=MUTED))
    els.append(text(xr, yb + 72, "відкриті стоки на спільній", size=12, color=INK))
    els.append(text(xr, yb + 90, "лінії, активній у 0", size=12, color=INK))
    els.append(text(xr, yb + 116, "рівнева, бо кілька прохань", size=12, color=INK, bold=True))
    els.append(text(xr, yb + 134, "зливаються в один нуль", size=12, color=INK, bold=True))
    els.append(arrow(x3 - 40, 156, xl + 60, yb, color=GREEN, sw=2))
    els.append(arrow(x3 + 20, 156, xr - 40, yb, color=RED, sw=2))
    els.append(text(W / 2, 445,
                    "Один прийом, три сходинки: економія транзистора → вентиль дротом → спільна шина.",
                    size=12, color=MUTED))
    render(os.path.join(OUT, 'hist-thread.svg'), W, H, *els,
           title="Від дефіциту транзисторів до шинних стандартів")


# ── Родовід логічних сімей: RTL → DTL → TTL і де визрів відкритий колектор ────
def fig_hist_families():
    W, H = 720, 300
    els = []
    y = 120
    boxes = [
        (150, "RTL", "резисторно-\nтранзисторна", "логіка на резисторах,\nтранзистор лише підсилює", MUTED),
        (360, "DTL", "діод-\nтранзисторна", "«І» на діодах,\nтранзистор інвертує", BLUE),
        (570, "TTL", "транзисторно-\nтранзисторна", "і логіка, і підсилення —\nна транзисторах", GREEN),
    ]
    for x, tag, name, desc, col in boxes:
        els.append(rect(x - 85, y - 45, 170, 150, fill=FILL, stroke=col, sw=2, rx=8))
        els.append(text(x, y - 22, tag, size=20, bold=True, color=col))
        for i, ln in enumerate(name.split("\n")):
            els.append(text(x, y + 2 + i * 16, ln, size=12, color=INK, bold=True))
        for i, ln in enumerate(desc.split("\n")):
            els.append(text(x, y + 44 + i * 15, ln, size=11, color=MUTED))
    els.append(arrow(150 + 85, y + 15, 360 - 85, y + 15, color=INK, sw=2.2))
    els.append(arrow(360 + 85, y + 15, 570 - 85, y + 15, color=INK, sw=2.2))
    els.append(text(255, y - 60, "менше струму, швидше", size=11, color=MUTED))
    els.append(text(465, y - 60, "ще швидше, ощадливіше", size=11, color=MUTED))
    box = fitbox(120, 240, 480, 34,
                 "У кожній сім'ї вихід-інвертор природно давав «голий» нижній ключ — відкритий колектор.",
                 size=12, fill="#eafaf1", stroke=GREEN)
    els.append(box)
    render(os.path.join(OUT, 'hist-families.svg'), W, H, *els,
           title="Родовід ранньої логіки: RTL → DTL → TTL")


if __name__ == '__main__':
    fig_wired()
    fig_duality()
    fig_irq()
    fig_hist_thread()
    fig_hist_families()
    print("ok")
