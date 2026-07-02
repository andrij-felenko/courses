# -*- coding: utf-8 -*-
"""Фігури до статті «Цифровий сигнальний процесор (DSP)».
Одна фігура: фон-нейманівська одна шина проти гарвардського поділу шин у DSP."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def harvard_vs_vonneumann():
    W, H = 760, 400
    frags = []

    # ── Ліва половина: фон-нейманівська машина ─────────────────────────────
    lx = 40
    frags.append(text(lx + 150, 62, "Фон-нейманівська: одна шина", size=15, bold=True))

    # спільна пам'ять (код+дані)
    frags.append(fitbox(lx + 40, 90, 220, 46, "Спільна пам'ять\n(код + дані)",
                        size=13, fill="#eef1f4"))
    # ядро / множник
    frags.append(fitbox(lx + 40, 300, 220, 50, "Ядро + множник",
                        size=13, fill=FILL, bold=True))

    # єдина шина між ними
    frags.append(line(lx + 150, 136, lx + 150, 300, color=INK, sw=3))
    frags.append(fitbox(lx + 95, 200, 110, 30, "1 шина", size=12,
                        fill="#fdecea", stroke=POS))
    # по черзі — інструкція АБО дане
    frags.append(text(lx + 150, 258, "код АБО дане", size=12, color=POS))
    frags.append(text(lx + 150, 276, "(по черзі)", size=11, color=MUTED))
    # ярлик простою
    frags.append(text(lx + 150, 372, "множник частину тактів чекає",
                     size=12, color=POS, bold=True))

    # ── Роздільник ─────────────────────────────────────────────────────────
    frags.append(line(W / 2, 78, W / 2, 350, color=MUTED, sw=1, dash="4,5"))

    # ── Права половина: гарвардський DSP ───────────────────────────────────
    rx = 400
    frags.append(text(rx + 160, 62, "Гарвардська DSP: окремі шини", size=15, bold=True))

    # три банки пам'яті
    frags.append(fitbox(rx + 20, 90, 100, 46, "Пам'ять\nкоду", size=12, fill="#eef1f4"))
    frags.append(fitbox(rx + 150, 90, 90, 46, "Дані X", size=12, fill="#eaf0fd"))
    frags.append(fitbox(rx + 260, 90, 90, 46, "Дані H", size=12, fill="#e9f7ef"))

    # множник унизу
    frags.append(fitbox(rx + 90, 300, 180, 50, "Множник за такт",
                        size=13, fill=FILL, bold=True))

    # три окремі шини — всі активні одночасно
    frags.append(line(rx + 70, 136, rx + 150, 300, color=INK, sw=2.5))
    frags.append(line(rx + 195, 136, rx + 180, 300, color=NEG, sw=2.5))
    frags.append(line(rx + 305, 136, rx + 210, 300, color=FIELD, sw=2.5))
    frags.append(text(rx + 60, 190, "інструкція", size=11, color=INK, anchor="start"))
    frags.append(text(rx + 235, 185, "x[k]", size=11, color=NEG, anchor="start"))
    frags.append(text(rx + 300, 220, "h[k]", size=11, color=FIELD, anchor="start"))

    frags.append(text(rx + 175, 372, "усе приходить за один такт — простою немає",
                     size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, 'harvard-vs-vonneumann.svg'), W, H, *frags)


if __name__ == '__main__':
    harvard_vs_vonneumann()
    print("ok: harvard-vs-vonneumann.svg")
