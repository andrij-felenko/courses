# -*- coding: utf-8 -*-
# Фігури для вставки «hist-gated-latch.md» (історія переходу до гейтування).
# svgkit імпортуємо, не переписуємо (§5 AUTHORING). Вивід — у ./img/ з префіксом hist-.
# Після запуску: python ../../../../scripts/svgcheck.py . --min-font 8
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def tube(cx, cy, r=15):
    """Схематична триодна лампа: коло + маленькі позначки електродів."""
    d = circle(cx, cy, r, fill="#fff8e7", stroke=LINE, sw=1.6)
    d += line(cx - r * 0.5, cy + r * 0.4, cx + r * 0.5, cy + r * 0.4, color=LINE, sw=1.4)  # катод
    d += line(cx - r * 0.5, cy - r * 0.1, cx + r * 0.5, cy - r * 0.1, color=MUTED, sw=1.2, dash="2,2")  # сітка
    d += line(cx - r * 0.4, cy - r * 0.55, cx + r * 0.4, cy - r * 0.55, color=LINE, sw=1.4)  # анод
    return d


def cap(cx, cy, horiz=True, gap=7, plate=16):
    """Конденсатор — дві пластини."""
    if horiz:
        d = line(cx - gap, cy - plate / 2, cx - gap, cy + plate / 2, color=POS, sw=2.2)
        d += line(cx + gap, cy - plate / 2, cx + gap, cy + plate / 2, color=POS, sw=2.2)
    else:
        d = line(cx - plate / 2, cy - gap, cx + plate / 2, cy - gap, color=POS, sw=2.2)
        d += line(cx - plate / 2, cy + gap, cx + plate / 2, cy + gap, color=POS, sw=2.2)
    return d


def resistor(cx, cy, horiz=True, L=26, w=8):
    """Резистор — прямокутник (європейський символ)."""
    if horiz:
        return rect(cx - L / 2, cy - w / 2, L, w, fill="#eef3ff", stroke=NEG, sw=1.8, rx=2)
    return rect(cx - w / 2, cy - L / 2, w, L, fill="#eef3ff", stroke=NEG, sw=1.8, rx=2)


# ── Фігура 1: та сама топологія, різна зв'язка — астабільний ↔ бістабільний ──
def fig_cap_vs_res():
    W, H = 720, 340
    p = []
    p.append(text(W / 2, 28, "Одна топологія, одна деталь-різниця", size=16, bold=True))

    def cell(x0, title, coupling, subtitle, col):
        pp = []
        cx1, cx2 = x0 + 70, x0 + 210
        cy = 150
        # дві лампи
        pp.append(tube(cx1, cy))
        pp.append(tube(cx2, cy))
        pp.append(text(cx1, cy + 34, "лампа", size=10, color=MUTED))
        pp.append(text(cx2, cy + 34, "лампа", size=10, color=MUTED))
        # живлення згори
        pp.append(line(cx1, 78, cx2, 78, color=LINE, sw=1.4))
        pp.append(line(cx1, 78, cx1, cy - 15, color=LINE, sw=1.4))
        pp.append(line(cx2, 78, cx2, cy - 15, color=LINE, sw=1.4))
        pp.append(text((cx1 + cx2) / 2, 72, "+B", size=11, color=POS, bold=True))
        # перехресна зв'язка вихід↔сітка (два плеча)
        midy1, midy2 = 210, 250
        if coupling == "cap":
            pp.append(line(cx1 + 15, cy, cx1 + 15, midy1, color=POS, sw=1.8))
            pp.append(line(cx1 + 15, midy1, cx2, midy1, color=POS, sw=1.8))
            pp.append(cap((cx1 + 15 + cx2) / 2, midy1, horiz=False))
            pp.append(line(cx2, midy1, cx2, cy + 15, color=POS, sw=1.8))
            pp.append(line(cx2 + 15, cy, cx2 + 15, midy2, color=POS, sw=1.8))
            pp.append(line(cx2 + 15, midy2, cx1 - 20, midy2, color=POS, sw=1.8))
            pp.append(cap((cx2 + 15 + cx1 - 20) / 2, midy2, horiz=False))
            pp.append(line(cx1 - 20, midy2, cx1 - 20, cy, color=POS, sw=1.8))
            pp.append(line(cx1 - 20, cy, cx1 - 15, cy, color=POS, sw=1.8))
        else:
            pp.append(line(cx1 + 15, cy, cx1 + 15, midy1, color=NEG, sw=1.8))
            pp.append(line(cx1 + 15, midy1, cx2, midy1, color=NEG, sw=1.8))
            pp.append(resistor((cx1 + 15 + cx2) / 2, midy1))
            pp.append(line(cx2, midy1, cx2, cy + 15, color=NEG, sw=1.8))
            pp.append(line(cx2 + 15, cy, cx2 + 15, midy2, color=NEG, sw=1.8))
            pp.append(line(cx2 + 15, midy2, cx1 - 20, midy2, color=NEG, sw=1.8))
            pp.append(resistor((cx2 + 15 + cx1 - 20) / 2, midy2))
            pp.append(line(cx1 - 20, midy2, cx1 - 20, cy, color=NEG, sw=1.8))
            pp.append(line(cx1 - 20, cy, cx1 - 15, cy, color=NEG, sw=1.8))
        pp.append(text(x0 + 140, 58, title, size=14, bold=True, color=col))
        pp.append(text(x0 + 140, 290, subtitle, size=12, color=col, bold=True))
        return pp

    p += cell(30, "Мультивібратор Абрагама–Блоха",
              "cap", "зв'язка — конденсатори → сам собою хитається", POS)
    p += cell(380, "Тригер Екклза–Джордана",
              "res", "зв'язка — резистори → застигає у стані", NEG)
    # роздільник
    p.append(line(370, 50, 370, 300, color="#d0d5db", sw=1, dash="5,5"))
    p.append(fitbox(150, 312, 420, 22,
                    "Конденсатор → резистор: коливання перетворюється на ПАМ'ЯТЬ",
                    size=12, fill="#f4f6f8", stroke=MUTED))
    render(os.path.join(OUT, 'hist-cap-vs-res.svg'), W, H, *p)


# ── Фігура 2: часова шкала звуження вікна запису ────────────────────────────
def fig_timeline():
    W, H = 740, 430
    p = []
    p.append(text(W / 2, 30, "Як звужувалося вікно запису", size=16, bold=True))

    x0, x1 = 70, 690
    axis_y = 70
    p.append(line(x0, axis_y, x1, axis_y, color=LINE, sw=1.6))
    p.append(arrow(x1 - 4, axis_y, x1 + 8, axis_y, color=LINE, sw=1.6))

    # чотири віхи
    marks = [
        (0.06, "1917–19", "Мультивібратор", "Абрагам–Блох", "без стійких станів:", "коливається сам", POS),
        (0.34, "1918–19", "Тригер", "Екклз–Джордан", "два стійкі стани, але", "слухає входи ЗАВЖДИ", MUTED),
        (0.62, "далі", "Гейтована засувка", "(дозвіл/такт)", "вікно запису —", "лише коли EN=1", FIELD),
        (0.90, "синхронна", "Тактована логіка", "(регістри, ЕОМ)", "вікно звужене", "до краю такту", NEG),
    ]
    box_w, box_h = 150, 118
    for frac, when, t1, t2, s1, s2, col in marks:
        mx = x0 + (x1 - x0 - 20) * frac
        p.append(circle(mx, axis_y, 6, fill=col, stroke=col, sw=1))
        p.append(text(mx, axis_y - 16, when, size=12, color=col, bold=True))
        by = axis_y + 40
        bx = mx - box_w / 2
        # утримати рамку в межах полотна
        bx = max(6, min(bx, W - box_w - 6))
        p.append(rect(bx, by, box_w, box_h, fill="#f9fbfd", stroke=col, sw=1.5, rx=8))
        p.append(line(mx, axis_y + 6, mx, by, color=col, sw=1.2, dash="3,3"))
        p.append(text(bx + box_w / 2, by + 24, t1, size=13, bold=True, color=col))
        p.append(text(bx + box_w / 2, by + 43, t2, size=12, color=INK))
        p.append(line(bx + 12, by + 54, bx + box_w - 12, by + 54, color="#e0e4e8", sw=1))
        p.append(text(bx + box_w / 2, by + 74, s1, size=11, color=MUTED))
        p.append(text(bx + box_w / 2, by + 92, s2, size=11, color=MUTED))

    # смуга «ширина вікна» знизу, що звужується
    ry = 320
    p.append(text(W / 2, ry - 8, "ширина вікна, у яке пам'ять слухає вхід", size=12, color=MUTED))
    seg = [
        (x0, x0 + 150, POS, "нескінченне (сам хитається)"),
        (x0 + 165, x0 + 315, MUTED, "увесь час"),
        (x0 + 330, x0 + 445, FIELD, "рівень EN"),
        (x0 + 470, x0 + 500, NEG, "край такту"),
    ]
    for a, b, col, lab in seg:
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="18" rx="4" fill="%s" opacity="0.7"/>'
                 % (a, ry + 6, b - a, col))
    p.append(text((x0 + x0 + 150) / 2, ry + 44, "без стану", size=11, color=POS))
    p.append(text((x0 + 165 + x0 + 315) / 2, ry + 44, "весь час", size=11, color=MUTED))
    p.append(text((x0 + 330 + x0 + 445) / 2, ry + 44, "вікно EN", size=11, color=FIELD))
    p.append(text((x0 + 470 + x0 + 500) / 2, ry + 44, "мить", size=11, color=NEG))
    p.append(arrow(x0 + 40, ry + 66, x0 + 500, ry + 66, color=INK, sw=1.4))
    p.append(text(W / 2, ry + 84, "дисципліна росте →", size=11, color=INK, bold=True))
    render(os.path.join(OUT, 'hist-window-timeline.svg'), W, H, *p)


if __name__ == '__main__':
    fig_cap_vs_res()
    fig_timeline()
    print("hist figs written to", OUT)
