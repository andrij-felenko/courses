# -*- coding: utf-8 -*-
"""Фігури до теми «Пропускна й втрати».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b9770e"     # бурштинове: середній варіант / адаптив


# ── 1. бітрейт під стелею смуги ───────────────────────────────────────────────
# Ідея: стеля (доступна смуга) падає з відстанню; сталий бітрейт її переростає й
# попадає в зону заторів/втрат; адаптивний повзе під стелею.
def fig_bitrate_vs_bandwidth():
    W, H = 760, 380
    ox, oy = 90, 300
    aw, ah = 600, 230
    p = [text(W / 2, 28, "Бітрейт мусить улізти під стелю смуги", size=16, bold=True)]

    # стеля: спадна пряма від (ox, верх) до (ox+aw, низ)
    cx0, cy0 = ox, oy - ah * 0.86
    cx1, cy1 = ox + aw, oy - ah * 0.18
    def ceil_y(t):                       # t у [0..1]
        return cy0 + (cy1 - cy0) * t

    # зона заторів/втрат — між сталим бітрейтом і стелею, де стеля нижча
    set_y = oy - ah * 0.50               # сталий бітрейт (горизонталь)
    # точка, де стеля опускається під сталий бітрейт
    tcross = (set_y - cy0) / (cy1 - cy0)
    xcross = ox + aw * tcross
    p.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fdecea" stroke="none"/>'
             % (xcross, set_y, ox + aw, set_y, ox + aw, ceil_y(1.0)))

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 22, "відстань · завади →", size=11, color=MUTED, anchor="end"))
    p.append(text(ox + 4, oy - ah - 2, "↑ біт/с", size=11, color=MUTED, anchor="start"))

    # стеля смуги
    p.append(line(cx0, cy0, cx1, cy1, color=NEG, sw=2.8))
    p.append(text(cx0 + 40, cy0 - 8, "стеля = доступна смуга", size=11, color=NEG, anchor="start", bold=True))

    # сталий бітрейт
    p.append(line(ox, set_y, ox + aw, set_y, color=POS, sw=2.2))
    p.append(text(ox + 8, set_y - 8, "сталий бітрейт", size=10.5, color=POS, anchor="start", bold=True))
    p.append(circle(xcross, set_y, 5, fill=POS, stroke=INK, sw=1))
    p.append(text(xcross + 8, set_y - 12, "бітрейт переріс смугу", size=10, color=POS, anchor="start", bold=True))
    p.append(text((xcross + ox + aw) / 2, set_y + 32, "затори · втрати", size=12, color=POS, bold=True))

    # адаптивний — повзе трохи нижче стелі
    ax0, ay0 = ox, ceil_y(0.0) + 22
    ax1, ay1 = ox + aw, ceil_y(1.0) + 14
    p.append(line(ax0, ay0, ax1, ay1, color=FIELD, sw=2.4))
    p.append(text(ox + aw * 0.30, ceil_y(0.30) + 40, "адаптивний (повзе під стелею)",
                  size=10.5, color="#15803d", anchor="start", bold=True))

    render(os.path.join(IMG, "bitrate-vs-bandwidth.svg"), W, H, *p)


# ── 2. коли пакет зникає: причини + три відповіді ─────────────────────────────
# Ідея: чотири причини згори, потік пакетів із дірою посередині, три відповіді
# знизу — кожна за свою плату (смуга / затримка / якість).
def fig_packet_loss():
    W, H = 760, 430
    p = [text(W / 2, 28, "Коли пакет зникає", size=16, bold=True)]

    # причини
    causes = ["зіткнення", "слабкий сигнал", "затор у каналі", "переповнений буфер"]
    bw, gap = 156, 14
    x0 = (W - (len(causes) * bw + (len(causes) - 1) * gap)) / 2
    for i, c in enumerate(causes):
        x = x0 + i * (bw + gap)
        p.append(fitbox(x, 56, bw, 32, c, size=10.5, fill="#fdecea", stroke=POS, sw=1.2, color=POS, bold=True))

    # потік пакетів із дірою
    py = 130
    labels = ["#1", "#2", "", "#4", "#5", "#6"]
    px0 = 250
    for i, lab in enumerate(labels):
        x = px0 + i * 60
        if lab:
            p.append(rect(x, py, 46, 30, fill="#eef4ff", stroke=NEG, sw=1.6, rx=5))
            p.append(text(x + 23, py + 20, lab, size=10, color=NEG))
        else:
            p.append('<rect x="%.1f" y="%.1f" width="46" height="30" rx="5" fill="none" '
                     'stroke="%s" stroke-width="1.6" stroke-dasharray="4 3"/>' % (x, py, POS))
            p.append(text(x + 23, py + 21, "✗", size=15, color=POS, bold=True))
            p.append(text(x + 23, py + 46, "загублено", size=9, color=POS, bold=True))
    p.append(text(px0, py + 64, "→ збій у картинці, доки не прийде I-кадр",
                  size=10, color=MUTED, anchor="start"))

    # три відповіді
    answers = [
        ("FEC — надлишок", FIELD, "#eafaf0",
         ["шлемо зайві пакети,", "приймач сам відновить", "загублене"], "плата: смуга"),
        ("ARQ — перепит", AMBER, "#fdf6e3",
         ["просимо надіслати", "пакет ще раз", "(зворотний запит)"], "плата: затримка"),
        ("Терпіти", POS, "#fdecea",
         ["лишаємо збій,", "ловимо наступний", "I-кадр"], "плата: якість"),
    ]
    cw, cgap = 224, 20
    cx0 = (W - (3 * cw + 2 * cgap)) / 2
    cy, ch = 250, 150
    for i, (title, col, fill, body, plata) in enumerate(answers):
        x = cx0 + i * (cw + cgap)
        p.append(rect(x, cy, cw, ch, fill=fill, stroke=col, sw=1.8, rx=11))
        p.append(text(x + cw / 2, cy + 26, title, size=11.5, color=col, bold=True))
        for j, ln in enumerate(body):
            p.append(text(x + 22, cy + 54 + j * 22, ln, size=10, color=INK, anchor="start"))
        p.append(text(x + 22, cy + ch - 18, plata, size=10.5, color=col, anchor="start", bold=True))

    render(os.path.join(IMG, "packet-loss.svg"), W, H, *p)


# ── 3. джитер і буфер ─────────────────────────────────────────────────────────
# Ідея: рівний посил → нерівний прихід (джитер) → буфер → знов рівне відтворення.
def fig_jitter_buffer():
    W, H = 760, 360
    p = [text(W / 2, 28, "Буфер згладжує нерівний прихід", size=16, bold=True)]

    def packets(y, xs, color):
        for x in xs:
            p.append(rect(x, y, 16, 24, fill=color, stroke=INK, sw=1, rx=3))

    lab_x = 56
    # надіслано рівно
    p.append(text(lab_x, 92, "Надіслано (рівно):", size=10.5, color=INK, anchor="start", bold=True))
    even = [250 + i * 64 for i in range(8)]
    packets(80, even, NEG)

    # прийшло нерівно
    p.append(text(lab_x, 162, "Прийшло (джитер):", size=10.5, color=INK, anchor="start", bold=True))
    fracs = [0.00, 0.04, 0.20, 0.30, 0.49, 0.64, 0.76, 0.96]
    jit = [250 + f * (7 * 64) for f in fracs]
    packets(150, jit, AMBER)
    p.append(text(250 + 7 * 64 + 24, 165, "нерівно!", size=9.5, color=AMBER, anchor="start", bold=True))

    # буфер
    p.append(rect(360, 198, 240, 40, fill=FILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(480, 223, "БУФЕР тримає кілька пакетів", size=10, color="#15803d", bold=True))
    p.append(arrow(480, 176, 480, 196, color=MUTED, sw=1.4))
    p.append(arrow(480, 240, 480, 262, color=MUTED, sw=1.4))

    # відтворення знов рівне
    p.append(text(lab_x, 284, "Відтворення (рівно):", size=10.5, color=INK, anchor="start", bold=True))
    packets(272, even, FIELD)

    p.append(text(W / 2, 330, "Буфер всотує нерівність — на виході знов гладкий потік; ціна — кілька кадрів затримки.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "jitter-buffer.svg"), W, H, *p)


# ── 4. глибина буфера — компроміс «гладко ↔ миттєво» ──────────────────────────
# Ідея: шкала від малого буфера (мала затримка) до великого (гладкість); три
# місії на ній — гонка, стрім, хмара.
def fig_buffer_tradeoff():
    W, H = 760, 360
    p = [text(W / 2, 28, "Глибина буфера: гладко чи миттєво", size=16, bold=True)]

    bx0, bx1, by = 110, 650, 150
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="28" rx="14" fill="#e8edf3" '
             'stroke="%s" stroke-width="1.2"/>' % (bx0, by, bx1 - bx0, INK))
    p.append(text(bx0, by - 14, "малий буфер", size=10.5, color=POS, anchor="start", bold=True))
    p.append(text(bx1, by - 14, "великий буфер", size=10.5, color=NEG, anchor="end", bold=True))
    p.append(text(bx0 + 40, by + 52, "← менша затримка", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(bx1 - 40, by + 52, "більша гладкість →", size=9.5, color=NEG, anchor="end", bold=True))

    missions = [
        (0.12, POS, "Гонка / FPV", "крихітний буфер", "мінімум лагу, ризик смикання"),
        (0.50, AMBER, "Перегляд / стрім", "середній буфер", "гладко, лаг терпимо"),
        (0.88, NEG, "Хмара / запис", "великий буфер", "дуже гладко, лаг байдужий"),
    ]
    for t, col, title, sub, note in missions:
        mx = bx0 + t * (bx1 - bx0)
        p.append(circle(mx, by + 14, 8, fill=col, stroke=INK, sw=1.3))
        p.append(line(mx, by + 22, mx, by + 80, color=col, sw=1.2))
        cw, ch = 220, 92
        cxx = min(max(mx - cw / 2, 16), W - cw - 16)
        p.append(rect(cxx, by + 80, cw, ch, fill=FILL, stroke=col, sw=1.7, rx=11))
        p.append(text(cxx + cw / 2, by + 104, title, size=11, color=col, bold=True))
        p.append(text(cxx + cw / 2, by + 128, sub, size=10, color=INK))
        p.append(text(cxx + cw / 2, by + 150, note, size=9, color=MUTED))

    p.append(text(W / 2, H - 18, "Той самий компроміс «якість ↔ бітрейт ↔ затримка» — буфер просто інший бік ручки «затримка».",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "buffer-tradeoff.svg"), W, H, *p)


if __name__ == "__main__":
    fig_bitrate_vs_bandwidth()
    fig_packet_loss()
    fig_jitter_buffer()
    fig_buffer_tradeoff()
    print("OK: figures written to", IMG)
