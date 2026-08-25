# -*- coding: utf-8 -*-
"""Фігури до статті «Шифратор (енкодер)». Чистий Python, без залежностей."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_vs_decoder():
    """Дешифратор розгортає число у вісім ліній; шифратор згортає назад."""
    W, H = 760, 360
    frags = []
    frags.append(text(W / 2, 26, "Дві дзеркальні операції", size=17, bold=True))

    # ── Лівий блок: дешифратор (код → позиція) ──
    bx, by, bw, bh = 230, 70, 110, 230
    frags.append(rect(bx, by, bw, bh, fill="#eef4ff"))
    frags.append(text(bx + bw / 2, by + 24, "дешифратор", size=14, bold=True))
    frags.append(text(bx + bw / 2, by + 44, "код → позиція", size=11, color=MUTED))
    # вхід: число 3 (три біти)
    frags.append(text(bx - 78, by + 95, "вхід 011 = 3", size=12, bold=True, color=NEG))
    for i in range(3):
        yy = by + 110 + i * 18
        frags.append(line(bx - 30, yy, bx, yy, color=NEG, sw=1.6))
    # виходи: 8 ліній, активна третя
    for k in range(8):
        yy = by + 36 + k * 24
        active = (k == 3)
        col = POS if active else MUTED
        sw = 2.4 if active else 1.2
        frags.append(line(bx + bw, yy, bx + bw + 36, yy, color=col, sw=sw))
        frags.append(text(bx + bw + 52, yy + 4, "%d" % k, size=11,
                          color=col, bold=active))

    # ── Стрілки напряму ──
    frags.append(arrow(bx - 44, by + 150, bx - 44, by + 110, color=NEG))
    frags.append(text(bx - 44, by + 168, "число", size=10, color=MUTED))

    # ── Правий блок: шифратор (позиція → код) ──
    cx, cy, cw, ch = 500, 70, 110, 230
    frags.append(rect(cx, cy, cw, ch, fill="#eafaf0"))
    frags.append(text(cx + cw / 2, cy + 24, "шифратор", size=14, bold=True))
    frags.append(text(cx + cw / 2, cy + 44, "позиція → код", size=11, color=MUTED))
    # входи: 8 ліній, активна третя
    for k in range(8):
        yy = cy + 36 + k * 24
        active = (k == 3)
        col = POS if active else MUTED
        sw = 2.4 if active else 1.2
        frags.append(line(cx - 36, yy, cx, yy, color=col, sw=sw))
        frags.append(text(cx - 52, yy + 4, "%d" % k, size=11,
                          color=col, bold=active))
    # вихід: число 3
    frags.append(text(cx + cw + 80, cy + 95, "вихід 011 = 3", size=12,
                      bold=True, color=FIELD))
    for i in range(3):
        yy = cy + 110 + i * 18
        frags.append(line(cx + cw, yy, cx + cw + 30, yy, color=FIELD, sw=1.6))

    return render(os.path.join(IMG, 'encoder-vs-decoder.svg'), W, H, *frags)


def fig_priority():
    """Голий шифратор бреше на двох активних; пріоритетний бере найстарший."""
    W, H = 760, 320
    frags = []
    frags.append(text(W / 2, 26, "Що буде, коли активні два входи", size=17, bold=True))

    def block(ox, label, sub, out_code, out_color, note):
        f = []
        bw, bh = 120, 200
        by = 64
        f.append(rect(ox, by, bw, bh, fill="#f4f6f8"))
        f.append(text(ox + bw / 2, by + 22, label, size=14, bold=True))
        f.append(text(ox + bw / 2, by + 40, sub, size=10, color=MUTED))
        # 8 входів, активні D1 і D4
        for k in range(8):
            yy = by + 58 + k * 16
            active = (k == 1 or k == 4)
            col = POS if active else MUTED
            sw = 2.4 if active else 1.1
            f.append(line(ox - 30, yy, ox, yy, color=col, sw=sw))
            f.append(text(ox - 44, yy + 4, "D%d" % k, size=10,
                          color=col, bold=active))
        # вихід
        f.append(line(ox + bw, by + 100, ox + bw + 30, by + 100,
                      color=out_color, sw=2.2))
        f.append(text(ox + bw + 64, by + 96, out_code, size=15,
                      bold=True, color=out_color))
        f.append(text(ox + bw + 64, by + 116, note, size=10, color=MUTED))
        return f

    frags += block(150, "голий", "просте АБО",
                   "5", POS, "якої не")
    frags.append(text(214, 300, "D1 і D4 → 101 = 5 (фантом)", size=11, color=POS))

    frags += block(480, "пріоритетний", "старший виграє",
                   "4", FIELD, "= D4")
    frags.append(text(544, 300, "D4 «затуляє» D1 → 4", size=11, color=FIELD))

    return render(os.path.join(IMG, 'priority.svg'), W, H, *frags)


def fig_pinout():
    """Розпіновка DIP-16 корпусу 74148: рискою позначено активні-низькі."""
    W, H = 620, 470
    frags = []
    frags.append(text(W / 2, 26, "Розпіновка 74148 у корпусі DIP-16", size=17, bold=True))

    # ── Корпус ──
    bx, by, bw, bh = 250, 60, 120, 380
    frags.append(rect(bx, by, bw, bh, fill="#eef1f5"))
    frags.append(text(bx + bw / 2, by + bh / 2 - 6, "74148", size=15, bold=True))
    frags.append(text(bx + bw / 2, by + bh / 2 + 12, "8 → 3", size=11, color=MUTED))
    # виїмка-ключ угорі
    frags.append(('<path d="M %.1f %.1f A 10 10 0 0 0 %.1f %.1f" '
                  'fill="none" stroke="%s" stroke-width="1.5"/>'
                  % (bx + bw / 2 - 10, by, bx + bw / 2 + 10, by, LINE)))

    # ліва колонка (pin 1..8 згори вниз), права (16..9 згори вниз)
    left = [("1", "I4", True), ("2", "I5", True), ("3", "I6", True), ("4", "I7", True),
            ("5", "EI", True), ("6", "A2", True), ("7", "A1", True), ("8", "GND", False)]
    right = [("16", "Vcc", False), ("15", "EO", True), ("14", "GS", True),
             ("13", "I3", True), ("12", "I2", True), ("11", "I1", True),
             ("10", "I0", True), ("9", "A0", True)]

    def pin_color(name):
        if name in ("Vcc", "GND"):
            return MUTED
        if name.startswith("I"):
            return POS
        if name in ("A0", "A1", "A2"):
            return FIELD
        return NEG  # EI, EO, GS — службові

    n = len(left)
    for i in range(n):
        yy = by + 34 + i * 46
        pin, name, act = left[i]
        col = pin_color(name)
        # ніжка
        frags.append(line(bx - 24, yy, bx, yy, color=LINE, sw=2))
        frags.append(circle(bx - 24, yy, 3, fill=BG, stroke=LINE, sw=1.2))
        frags.append(text(bx - 30, yy + 4, pin, size=10, color=MUTED, anchor="end"))
        # підпис із рискою активності-низької
        lbl = name
        frags.append(text(bx + 8, yy + 4, lbl, size=12, color=col,
                          bold=True, anchor="start"))
        if act:  # надрискова лінія = активний-низький
            w = text_width(lbl, 12, True)
            frags.append(line(bx + 8, yy - 8, bx + 8 + w, yy - 8, color=col, sw=1.4))

    for i in range(len(right)):
        yy = by + 34 + i * 46
        pin, name, act = right[i]
        col = pin_color(name)
        frags.append(line(bx + bw, yy, bx + bw + 24, yy, color=LINE, sw=2))
        frags.append(circle(bx + bw + 24, yy, 3, fill=BG, stroke=LINE, sw=1.2))
        frags.append(text(bx + bw + 30, yy + 4, pin, size=10, color=MUTED, anchor="start"))
        lbl = name
        tw = text_width(lbl, 12, True)
        frags.append(text(bx + bw - 8, yy + 4, lbl, size=12, color=col,
                          bold=True, anchor="end"))
        if act:
            frags.append(line(bx + bw - 8 - tw, yy - 8, bx + bw - 8, yy - 8, color=col, sw=1.4))

    # ── Легенда ──
    ly = by + bh + 4
    frags.append(text(60, ly, "надриска = активний-низький (діє нулем)", size=10,
                      color=MUTED, anchor="start"))
    frags.append(text(60, ly + 16, "червоне — входи I0…I7 · зелене — код A0…A2 · синє — служба EI/EO/GS",
                      size=10, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, 'pinout-74148.svg'), W, H, *frags)


def fig_cascade():
    """Два 74148 у каскад: EO старшого гасить молодший, дає 16→4."""
    W, H = 720, 440
    frags = []
    frags.append(text(W / 2, 26, "Каскад: два 74148 роблять шифратор 16 → 4", size=16, bold=True))

    def chip(ox, oy, title, sub, ins):
        f = []
        bw, bh = 150, 150
        f.append(rect(ox, oy, bw, bh, fill="#eef1f5"))
        f.append(text(ox + bw / 2, oy + 24, title, size=13, bold=True))
        f.append(text(ox + bw / 2, oy + 42, sub, size=10, color=MUTED))
        # входи зліва
        f.append(text(ox - 8, oy + 78, ins, size=11, color=POS,
                      anchor="end", bold=True))
        for k in range(3):
            yy = oy + 66 + k * 12
            f.append(line(ox - 34, yy, ox, yy, color=POS, sw=1.6))
        # EI зверху, EO знизу, A-код справа
        f.append(text(ox + bw / 2, oy - 6, "EI", size=10, color=NEG, bold=True))
        f.append(line(ox + bw / 2, oy - 2, ox + bw / 2, oy, color=NEG, sw=1.6))
        f.append(text(ox + bw / 2, oy + bh + 16, "EO", size=10, color=NEG, bold=True))
        f.append(line(ox + bw / 2, oy + bh, ox + bw / 2, oy + bh + 4, color=NEG, sw=1.6))
        f.append(text(ox + bw + 40, oy + 78, "A2 A1 A0", size=10, color=FIELD, bold=True))
        for k in range(3):
            yy = oy + 66 + k * 12
            f.append(line(ox + bw, yy, ox + bw + 30, yy, color=FIELD, sw=1.6))
        return f

    hx, hy = 120, 66
    lx, ly = 120, 256
    frags += chip(hx, hy, "старший 74148", "входи 15…8", "I15..I8")
    frags += chip(lx, ly, "молодший 74148", "входи 7…0", "I7..I0")

    # EO старшого → EI молодшого (з підписом)
    frags.append(arrow(hx + 75, hy + 150 + 4, lx + 75, ly - 6, color=NEG, sw=2))
    frags.append(text(hx + 210, (hy + 150 + ly) / 2 + 6,
                      "EO=0 лише коли старший мовчить", size=10, color=NEG))
    frags.append(text(hx + 210, (hy + 150 + ly) / 2 + 22,
                      "→ дозволяє молодший", size=10, color=MUTED))
    # EI старшого прив'язаний до 0 (завжди дозволений)
    frags.append(text(hx + 75, hy - 20, "EI=0 (завжди ввімкнений)", size=9, color=MUTED))

    # старший біт A3 = GS старшого (позначаємо окремою лінією від правого краю)
    frags.append(text(hx + 240, hy + 134, "A3 = GS старшого", size=10,
                      color=FIELD, bold=True))
    frags.append(line(hx + 150, hy + 118, hx + 180, hy + 118, color=FIELD, sw=1.6))

    frags.append(text(W / 2, H - 14,
                      "молодші 3 біти — від активного чипа; A3 відрізняє половини",
                      size=10, color=MUTED))
    return render(os.path.join(IMG, 'cascade-74148.svg'), W, H, *frags)


if __name__ == "__main__":
    p1 = fig_vs_decoder()
    p2 = fig_priority()
    p3 = fig_pinout()
    p4 = fig_cascade()
    print("OK:", os.path.basename(p1), os.path.basename(p2),
          os.path.basename(p3), os.path.basename(p4))
