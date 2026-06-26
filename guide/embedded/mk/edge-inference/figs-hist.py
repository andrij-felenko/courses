# -*- coding: utf-8 -*-
"""Фігура до вставки hist-tinyml-frameworks.md теми «Інференс на пристрої».
Окремий генератор (головний figs.py пишуть паралельно інші вставки) —
відповідає лише за two-camps.svg. Запуск: python figs-hist.py → ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── [hist] Дві команди сходяться: ручний порт → uTensor + TFLM → злиття ───────
def fig_two_camps():
    """Як народилася бібліотека інференсу. Ліворуч — ручний порт до 2017;
    праворуч дві гілки (Arm/uTensor компілює граф наперед, Google/TFLM
    інтерпретує на чипі), що зливаються у спільний рушій у травні 2019."""
    W, H = 780, 430
    els = []

    # --- Ліворуч: ручний порт (до 2017) ---
    els.append(text(140, 64, "До 2017", size=13, bold=True, color=MUTED))
    b0, _, _ = textbox(140, 110, "навчена модель", size=12, fill="#eef2f7", stroke=NEG, min_w=170)
    els.append(b0)
    h0, _, _ = textbox(140, 185, "інженер вписує\nграф у C руками", size=11, fill="#fdf3f2", stroke=POS, min_w=180)
    els.append(h0)
    h1, _, _ = textbox(140, 268, "крихкий ручний\nпорт під КОЖНУ\nмодель", size=11, fill=BG, stroke=LINE, min_w=180)
    els.append(h1)
    els.append(arrow(140, 132, 140, 162))
    els.append(arrow(140, 212, 140, 236))

    # роздільна вертикаль
    els.append(line(258, 56, 258, 360, color=MUTED, sw=1, dash="4,4"))

    # --- Праворуч: дві гілки 2017-2019 → злиття ---
    arm_x, goo_x = 405, 615
    mid = (arm_x + goo_x) / 2
    els.append(text(mid, 64, "2017 – 2019", size=13, bold=True, color=MUTED))

    # гілка Arm / uTensor
    a0, _, _ = textbox(arm_x, 110, "Arm\nuTensor (2017)", size=12, bold=True, fill="#f0f7f0", stroke=FIELD, min_w=165)
    els.append(a0)
    a1, _, _ = textbox(arm_x, 185, "КОМПІЛЮЄ граф\nу C++ наперед", size=11, fill=BG, stroke=FIELD, min_w=165)
    els.append(a1)
    els.append(arrow(arm_x, 134, arm_x, 162))

    # гілка Google / TFLite Micro
    g0, _, _ = textbox(goo_x, 110, "Google\nTFLite Micro (бер. 2019)", size=12, bold=True, fill="#eef2f7", stroke=NEG, min_w=165)
    els.append(g0)
    g1, _, _ = textbox(goo_x, 185, "ІНТЕРПРЕТУЄ граф\nна чипі на льоту", size=11, fill=BG, stroke=NEG, min_w=165)
    els.append(g1)
    els.append(arrow(goo_x, 134, goo_x, 162))

    # злиття в один блок
    merge_y = 288
    m, mw, mh = textbox(mid, merge_y, "TFLite Micro — один рушій (трав. 2019)",
                        size=12, bold=True, fill="#e8f1ff", stroke=NEG, sw=2.0, min_w=340)
    els.append(m)
    els.append(arrow(arm_x, 210, mid - 70, merge_y - mh / 2))
    els.append(arrow(goo_x, 210, mid + 70, merge_y - mh / 2))
    els.append(text(mid, merge_y + mh / 2 + 22,
                    "основа — інтерпретатор Google; досвід Arm улився всередину",
                    size=11, color=MUTED))

    els.append(text(W / 2, H - 14,
                    "Дві команди йшли до одного з різних боків — від заліза й від хмари — і зустрілися посередині.",
                    size=12, color=MUTED))
    render(os.path.join(IMG, "two-camps.svg"), W, H, *els,
           title="Як народилася бібліотека інференсу: від ручного порту до спільного рушія")


if __name__ == "__main__":
    fig_two_camps()
    print("OK: two-camps.svg у", IMG)
