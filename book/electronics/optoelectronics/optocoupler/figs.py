# -*- coding: utf-8 -*-
"""Фігури до вставки «Фототранзисторна оптопара: розрахунок обох боків і старіння».
PC817 — лише приклад; підписи узагальнені на клас фототранзисторних оптопар.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_calc():
    """Розрахунок обох боків: вхід — як світлодіод, вихід — як ключ у насиченні."""
    W, H = 860, 430
    f = []

    # ── корпус DIP-4 ліворуч ──
    cx, cy, cw, ch = 70, 96, 150, 132
    f.append(rect(cx, cy, cw, ch, fill="#2b2b2b", stroke=INK, sw=2, rx=8))
    f.append(circle(cx + 16, cy + 16, 5, fill=BG, stroke=MUTED, sw=1.4))
    f.append(text(cx + cw / 2, cy + 58, "оптопара", size=14, color="#e8e8e8", bold=True))
    f.append(text(cx + cw / 2, cy + 78, "DIP-4", size=11, color="#bdbdbd"))
    # виводи входу (ліворуч)
    f.append(line(cx, cy + 30, cx - 26, cy + 30, color=INK, sw=2))
    f.append(text(cx - 30, cy + 34, "анод", size=11, color=POS, anchor="end", bold=True))
    f.append(line(cx, cy + 80, cx - 26, cy + 80, color=INK, sw=2))
    f.append(text(cx - 30, cy + 84, "катод", size=11, color=NEG, anchor="end", bold=True))
    # виводи виходу (праворуч)
    f.append(line(cx + cw, cy + 30, cx + cw + 26, cy + 30, color=INK, sw=2))
    f.append(text(cx + cw + 30, cy + 34, "колектор", size=11, color=INK, anchor="start", bold=True))
    f.append(line(cx + cw, cy + 80, cx + cw + 26, cy + 80, color=INK, sw=2))
    f.append(text(cx + cw + 30, cy + 84, "емітер", size=11, color=INK, anchor="start", bold=True))
    f.append(text(cx + cw / 2, cy + 150, "крапка/зріз = вивід 1", size=10, color=MUTED, italic=True))

    # ── панель ВХІД ──
    px, py, pw, ph = 300, 72, 250, 318
    f.append(rect(px, py, pw, ph, fill=BG, stroke="#c9d3dc", sw=1.4))
    icx = px + pw / 2
    f.append(text(icx, py + 26, "ВХІД — як світлодіод", size=13, color=INK, bold=True))
    f.append(text(icx, py + 52, "U_F ≈ 1.2 В,  хочемо I_F = 10 мА", size=11, color=INK))
    f.append(text(icx, py + 90, "R1 = (3.3 − 1.2) / 10 мА", size=13, color=FIELD, bold=True))
    f.append(text(icx, py + 112, "≈ 210 Ом  →  220 Ом", size=13, color=FIELD, bold=True))
    f.append(text(icx, py + 156, "той самий обмежувальний", size=10, color=MUTED))
    f.append(text(icx, py + 172, "резистор, що в звичайного", size=10, color=MUTED))
    f.append(text(icx, py + 188, "світлодіода", size=10, color=MUTED))
    f.append(text(icx, py + 232, "запас: реальний I_F беруть", size=11, color="#9c6a16"))
    f.append(text(icx, py + 248, "більшим за теоретичний —", size=11, color="#9c6a16"))
    f.append(text(icx, py + 264, "бо CTR падає з роками", size=11, color="#9c6a16"))

    # ── панель ВИХІД ──
    qx, qy, qw, qh = 580, 72, 250, 318
    f.append(rect(qx, qy, qw, qh, fill=BG, stroke="#c9d3dc", sw=1.4))
    ocx = qx + qw / 2
    f.append(text(ocx, qy + 26, "ВИХІД — ключ у насиченні", size=13, color=INK, bold=True))
    f.append(text(ocx, qy + 52, "CTR_min = 80 %  (нижчий ранг)", size=11, color=INK))
    f.append(text(ocx, qy + 78, "I_C(гарант.) = 0.8 · 10 мА = 8 мА", size=11, color=POS, bold=True))
    f.append(text(ocx, qy + 116, "R_C при вих. 5 В:", size=11, color=INK))
    f.append(text(ocx, qy + 138, "R_C > 5 В / 8 мА ≈ 620 Ом", size=12, color=FIELD, bold=True))
    f.append(text(ocx, qy + 160, "→ беремо 1 кОм (з запасом)", size=12, color=FIELD, bold=True))
    f.append(text(ocx, qy + 204, "на R_C падає майже все →", size=11, color=MUTED))
    f.append(text(ocx, qy + 220, "транзистор насичений →", size=11, color=MUTED))
    f.append(text(ocx, qy + 236, "чіткий логічний 0", size=11, color=MUTED))
    f.append(text(ocx, qy + 274, "інверсія: світлодіод горить → 0", size=11, color="#7a4e8a", bold=True))

    f.append(text(W / 2, H - 22,
                  "Дві землі — два окремі розрахунки: вхід рахують як світлодіод, вихід — як ключ-транзистор.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "both-sides-calc.svg"), W, H, *f,
           title="Фототранзисторна оптопара: обидва боки в числах")


def fig_ranks():
    """Ранги CTR за літерою, канали в корпусі й швидкі цифрові родичі."""
    W, H = 860, 400
    f = []

    # ── ліва панель: ранги CTR ──
    lx, ly, lw, lh = 40, 56, 380, 180
    f.append(rect(lx, ly, lw, lh, fill=BG, stroke="#c9d3dc", sw=1.4))
    f.append(text(lx + lw / 2, ly - 8, "ранг CTR — літера в назві", size=12, color=INK, bold=True))
    ranks = [("ранг A", "80…160 %", 26.7, FIELD),
             ("ранг B", "130…260 %", 43.3, "#b5732e"),
             ("ранг C", "200…400 %", 66.7, NEG),
             ("ранг D", "300…600 %", 100.0, "#7a4e8a")]
    ry = ly + 36
    for name, rng, bw, col in ranks:
        f.append(text(lx + 30, ry, name, size=12, color=col, anchor="start", bold=True))
        f.append(text(lx + 160, ry, rng, size=11, color=INK, anchor="start"))
        f.append(rect(lx + 260, ry - 12, bw, 14, fill=col, stroke="none", sw=0, rx=0))
        ry += 32
    f.append(text(lx + lw / 2, ly + lh - 12, "без літери — увесь діапазон 50…600 %",
                  size=10, color=MUTED, italic=True))

    # ── права панель: канали в корпусі ──
    rx, ry0, rw, rh = 440, 56, 380, 180
    f.append(rect(rx, ry0, rw, rh, fill=BG, stroke="#c9d3dc", sw=1.4))
    f.append(text(rx + rw / 2, ry0 - 8, "скільки каналів у корпусі", size=12, color=INK, bold=True))
    pkgs = [("1 канал", "напр. PC817"), ("2 канали", "напр. PC827"), ("4 канали", "напр. PC847")]
    bx = rx + 30
    for chans, ex in pkgs:
        f.append(rect(bx, ry0 + 40, 90, 70, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=8))
        f.append(text(bx + 45, ry0 + 74, chans, size=12, color=INK, bold=True))
        f.append(text(bx + 45, ry0 + 96, ex, size=9, color=MUTED))
        bx += 120
    f.append(text(rx + rw / 2, ry0 + rh - 12, "однакова комірка, більше пар у корпусі",
                  size=10, color=MUTED, italic=True))

    # ── нижня панель: швидкі цифрові ──
    bx0, by0, bw0, bh0 = 40, 256, 780, 120
    f.append(rect(bx0, by0, bw0, bh0, fill=BG, stroke="#c9d3dc", sw=1.4))
    bcx = bx0 + bw0 / 2
    f.append(text(bcx, by0 - 8, "коли фототранзистора замало — швидкі цифрові", size=12, color=INK, bold=True))
    f.append(text(bcx, by0 + 28, "фототранзисторна оптопара: смуга ~десятки кГц (повільна)", size=11, color=INK))
    f.append(text(bcx, by0 + 56, "потрібні сотні кБіт/Мбіт → 6N137 / TLP-клас:", size=11, color=FIELD, bold=True))
    f.append(text(bcx, by0 + 78, "усередині фотодіод + підсилювач-формувач, логічний вихід, мегагерци",
                  size=10, color=MUTED))
    f.append(text(bcx, by0 + 102, "для зв'язку (ізольований UART / SPI) беруть саме їх, а не фототранзисторну",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "ctr-ranks.svg"), W, H, *f,
           title="Ранги CTR, канали в корпусі й швидкі родичі")


if __name__ == "__main__":
    fig_calc()
    fig_ranks()
    print("OK: both-sides-calc.svg, ctr-ranks.svg")
