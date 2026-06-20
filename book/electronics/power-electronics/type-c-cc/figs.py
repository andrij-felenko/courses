# -*- coding: utf-8 -*-
"""Фігури для вставки comp-cc-resistors (резистори CC у USB-C).
Імпортує svgkit зі scripts/ (НЕ копіює). Вивід — у ./img/.
Запуск:  python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_decode():
    """Шкала напруги на CC, яку міряє sink, з трьома порогами декодування."""
    W, H = 720, 300
    parts = []
    # вісь
    x0, x1, y = 90, 640, 150
    vmax = 1.8
    def vx(v):
        return x0 + (x1 - x0) * (v / vmax)
    parts.append(line(x0, y, x1 + 14, y, color=INK, sw=2))
    parts.append(arrow(x1, y, x1 + 22, y, color=INK))
    # зони
    zones = [
        (0.00, 0.20, "#eceff1", "нема\nпристрою"),
        (0.20, 0.66, "#e3f0fb", "Default\n0.5 / 0.9 A"),
        (0.66, 1.23, "#fdf2e0", "1.5 A"),
        (1.23, vmax, "#fdecea", "3.0 A\n(15 Вт)"),
    ]
    for a, b, col, lab in zones:
        xa, xb = vx(a), vx(b)
        parts.append(rect(xa, y - 30, xb - xa, 30, fill=col, stroke=LINE, sw=1.2, rx=0))
        parts.append(mtext((xa + xb) / 2, y - 46, lab, size=12, color=INK))
    # пороги
    for v in (0.20, 0.66, 1.23):
        parts.append(line(vx(v), y - 34, vx(v), y + 10, color=POS, sw=1.8, dash="4 3"))
        parts.append(text(vx(v), y + 26, ("%.2f В" % v), size=12, color=POS, bold=True))
    parts.append(text(x1 + 22, y + 26, "→ В", size=12, color=MUTED))
    # підпис осі
    parts.append(text((x0 + x1) / 2, y + 64,
                      "напруга на активному CC (вхід sink, через його Rd)", size=12, color=MUTED))
    # пояснення
    box, w, h = textbox(W / 2, 250,
                        ["Sink читає одну напругу й потрапляє в одну зону.",
                         "Жодних команд: рівень уже стоїть на лінії."],
                        size=12.5, fill="#f4f6f8")
    parts.append(box)
    render(os.path.join(IMG, "cc-decode.svg"), W, H, *parts,
           title="Що бачить пристрій на лінії CC")


def fig_pins():
    """Два піни CC: активний несе дільник, другий стає VCONN; розрізнення Rd / Ra."""
    W, H = 720, 340
    parts = []
    # рамка sink
    sx, sy, sw_, sh = 470, 70, 200, 220
    parts.append(rect(sx, sy, sw_, sh, fill="#f0f7f0", stroke=FIELD, sw=2))
    parts.append(text(sx + sw_ / 2, sy + 24, "пристрій (sink)", size=13, bold=True, color=FIELD))
    # рамка source
    px, py = 50, 70
    parts.append(rect(px, py, 170, sh, fill="#fbf3f3", stroke=POS, sw=2))
    parts.append(text(px + 85, py + 24, "джерело (source)", size=13, bold=True, color=POS))

    # CC1 — активна лінія: Rp ... Rd
    yc1 = 150
    parts.append(line(px + 170, yc1, sx, yc1, color=INK, sw=2))
    parts.append(text((px + 170 + sx) / 2, yc1 - 12, "CC1  (з'єднана наскрізь у штекері)", size=11, color=INK))
    b, w, h = textbox(px + 130, yc1, "Rp", size=12, fill="#fdecea", stroke=POS); parts.append(b)
    b, w, h = textbox(sx + 40, yc1, "Rd 5.1k", size=12, fill="#eaf3ea", stroke=FIELD); parts.append(b)

    # CC2 — другий пін: стає VCONN; у кабелі — Ra
    yc2 = 245
    parts.append(line(px + 170, yc2, sx, yc2, color=MUTED, sw=2, dash="5 4"))
    parts.append(text((px + 170 + sx) / 2, yc2 - 12, "CC2  →  VCONN (живить кабель)", size=11, color=MUTED))
    b, w, h = textbox(sx + 48, yc2, "Ra 0.8–1.2k\n(e-marker)", size=11, fill="#eef1f4", stroke=MUTED); parts.append(b)

    # підказка про розрізнення
    box, w, h = textbox(W / 2, 318,
                        "Source розрізняє за опором: Rd (5.1k) = пристрій · Ra (0.8–1.2k) = кабель · нічого = відкрито.",
                        size=12, fill="#f4f6f8")
    parts.append(box)
    render(os.path.join(IMG, "cc-pins.svg"), W, H, *parts,
           title="Два піни CC: котрий ожив — і ким він став")


if __name__ == "__main__":
    fig_decode()
    fig_pins()
    print("done")
