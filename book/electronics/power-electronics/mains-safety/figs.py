# -*- coding: utf-8 -*-
"""Фігури до теми «Безпека з мережею».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

HOT  = "#fbeee6"   # заливка «гарячого» боку
WARN = "#e0a32e"   # рамки рубежів (бурштин)
WARNFILL = "#fdf3d8"


# ── 1. Рубежі захисту між розеткою і платою ──────────────────────────────────
def fig_defense_layers():
    W, H = 880, 300
    f = [text(W / 2, 30, "Рубежі захисту між розеткою і платою", size=17, bold=True)]

    # п'ять рамок у ряд: розетка → запобіжник → варистор │ ізоляція → логіка
    boxes = [
        ("розетка",        "~230 В",                 POS,  HOT),
        ("запобіжник",     "рве при\nнадструмі",     WARN, WARNFILL),
        ("варистор (MOV)", "зрізає кидки\nнапруги",  WARN, WARNFILL),
        ("ізоляція",       "оптопара /\nтрансформатор", NEG, "#eaf0fd"),
        ("логіка",         "3.3 В,\nбезпечно",       FIELD, "#eef6ef"),
    ]
    bw, bh, gap = 140, 110, 28
    total = len(boxes) * bw + (len(boxes) - 1) * gap
    x0 = (W - total) / 2
    cy = 150
    centers = []
    for i, (title, sub, col, fl) in enumerate(boxes):
        x = x0 + i * (bw + gap)
        f.append(rect(x, cy - bh / 2, bw, bh, fill=fl, stroke=col, sw=2, rx=10))
        f.append(text(x + bw / 2, cy - 18, title, size=12.5, bold=True, color=col))
        f.append(mtext(x + bw / 2, cy + 6, sub, size=10.5, color=INK, lh=1.3))
        centers.append(x + bw / 2)
        if i:
            f.append(arrow(centers[i - 1] + bw / 2 + 3, cy, x - 3, cy, color=MUTED, sw=2))

    # бар'єр ізоляції між варистором і ізоляцією (між боксами 2 і 3)
    bx = (x0 + 2 * (bw + gap) + bw + x0 + 3 * (bw + gap)) / 2
    f.append(line(bx, cy - bh / 2 - 26, bx, cy + bh / 2 + 26, color=INK, sw=1.4, dash="5 4"))
    left_mid = (centers[0] + centers[2]) / 2
    right_mid = (centers[3] + centers[4]) / 2
    f.append(text(left_mid, cy + bh / 2 + 40, "бік мережі — небезпечно", size=11, bold=True, color=POS))
    f.append(text(right_mid, cy + bh / 2 + 40, "бік логіки — безпечно", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG, "defense-layers.svg"), W, H, *f)


# ── 2. Запобіжник vs варистор: різні біди — різні рубежі ─────────────────────
def fig_mov_fuse():
    W, H = 760, 300
    f = [text(W / 2, 30, "Дві біди — два рубежі: запобіжник по струму, варистор по напрузі", size=15.5, bold=True)]

    # ліва панель: запобіжник проти надструму
    f.append(rect(40, 60, 320, 210, fill=BG, stroke="#c9d3dc", sw=1.6, rx=10))
    f.append(text(200, 84, "запобіжник — проти НАДСТРУМУ", size=12.5, bold=True, color=POS))
    f.append(line(70, 150, 130, 150, color=INK, sw=2))
    f.append(rect(130, 140, 90, 20, fill=BG, stroke=INK, sw=1.6, rx=3))
    f.append(text(175, 154, "плавка", size=9, color=INK))
    f.append(line(220, 150, 290, 150, color=INK, sw=2))
    f.append(arrow(175, 182, 175, 162, color=POS, sw=2))
    f.append(text(175, 200, "забагато струму → згоряє → розрив", size=9.5, bold=True, color=POS))
    f.append(mtext(200, 228, "ловить коротке замикання\nі перевантаження", size=10, color=INK, lh=1.3))

    # права панель: варистор проти перенапруги
    f.append(rect(400, 60, 320, 210, fill=BG, stroke="#c9d3dc", sw=1.6, rx=10))
    f.append(text(560, 84, "варистор — проти ПЕРЕНАПРУГИ", size=12.5, bold=True, color=NEG))
    f.append(text(530, 108, "фаза", size=9.5, color=POS))
    f.append(line(530, 114, 530, 140, color=INK, sw=2))
    f.append(rect(516, 140, 28, 50, fill=BG, stroke=INK, sw=1.6, rx=2))
    f.append(line(508, 194, 552, 148, color=INK, sw=1.6))   # риска варистора
    f.append(text(560, 168, "MOV", size=10, bold=True, color=INK, anchor="start"))
    f.append(line(530, 190, 530, 214, color=INK, sw=2))
    f.append(text(530, 230, "нейтраль", size=9.5, color=INK))
    f.append(mtext(650, 150, "кидок 1000+ В →\nопір падає →\nпоглинає", size=9, color=NEG, lh=1.35))
    f.append(text(560, 250, "ловить блискавку й сплески", size=10, color=INK))

    render(os.path.join(IMG, "mov-fuse.svg"), W, H, *f)


# ── 3. Правило однієї руки: не дати струму шляху крізь серце ──────────────────
def fig_one_hand():
    W, H = 760, 320
    f = [text(W / 2, 30, "Правило однієї руки: не дати струму шляху крізь серце", size=16, bold=True)]

    def person(x0, two_hands, ok):
        col = POS if not ok else FIELD
        f.append(rect(x0, 60, 320, 248, fill=BG, stroke=col, sw=2, rx=12))
        label = "ОБИДВІ руки → струм крізь серце" if two_hands else "ОДНА рука → кола крізь тіло нема"
        f.append(text(x0 + 160, 84, label, size=12, bold=True, color=col))
        cx = x0 + 160
        head, hy = cx, 112
        f.append(circle(head, hy, 15, fill="#fde7c8", stroke="#b5732e", sw=1.8))   # голова
        f.append(rect(cx - 22, 128, 44, 80, fill="#fde7c8", stroke="#b5732e", sw=1.8, rx=10))  # тулуб
        f.append(text(cx, 174, "♥", size=15, color=POS))                            # серце
        # ноги
        f.append(line(cx, 208, cx - 14, 262, color="#b5732e", sw=5))
        f.append(line(cx, 208, cx + 14, 262, color="#b5732e", sw=5))
        # ліва рука завжди тягнеться до фази
        f.append(line(cx - 22, 142, cx - 52, 188, color="#b5732e", sw=5))
        f.append(circle(cx - 52, 194, 8, fill="none", stroke=POS, sw=2))            # вузол «фаза»
        f.append(text(cx - 58, 216, "фаза", size=9, bold=True, color=POS))
        if two_hands:
            # права рука до землі → коло рука-рука крізь серце
            f.append(line(cx + 22, 142, cx + 52, 188, color="#b5732e", sw=5))
            f.append(circle(cx + 52, 194, 8, fill="none", stroke=NEG, sw=2))
            f.append(text(cx + 58, 216, "земля", size=9, bold=True, color=NEG))
            f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" '
                     'fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="4 3"/>'
                     % (cx - 52, 194, cx - 14, 168, cx + 14, 168, cx + 52, 194, POS))
            f.append(text(cx, 240, "рука→рука крізь грудну клітку", size=10, bold=True, color=POS))
        else:
            # права рука за спину
            f.append(line(cx + 22, 150, cx + 40, 176, color="#b5732e", sw=5))
            f.append(text(cx + 70, 168, "рука за спиною", size=9, bold=True, color=FIELD, anchor="middle"))
            f.append(text(cx, 240, "торкнувся — кола крізь тіло нема", size=10, bold=True, color=FIELD))

    person(40, True, False)
    person(400, False, True)
    render(os.path.join(IMG, "one-hand.svg"), W, H, *f)


if __name__ == "__main__":
    fig_defense_layers()
    fig_mov_fuse()
    fig_one_hand()
    print("OK: 3 figures ->", IMG)
