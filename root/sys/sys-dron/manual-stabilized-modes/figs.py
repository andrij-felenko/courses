# -*- coding: utf-8 -*-
"""Фігури до статті «Ручні режими» (basic).
Запуск:  python figs.py   →   ./img/*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Що означає стік у трьох режимах ──────────────────────────────────────
def fig_stick():
    W, H = 760, 430
    f = []
    f.append(text(W / 2, 28, "Той самий рух стіка — три різні смисли", size=17, bold=True))

    col_w = 230
    xs = [30, 30 + col_w + 20, 30 + 2 * (col_w + 20)]
    top = 60
    names = ["РУЧНИЙ (manual)", "КУТ. ШВИДКІСТЬ (rate)", "КУТ (angle)"]
    accents = [POS, INK, FIELD]

    for i, x in enumerate(xs):
        f.append(fitbox(x, top, col_w, 34, names[i], size=13, bold=True,
                        fill="#ffffff", stroke=accents[i], sw=2))

    # Ряд 1: стік відхилено
    y1 = top + 60
    f.append(text(30, y1 - 8, "стік відхилено вперед:", size=12,
                  color=MUTED, anchor="start", italic=True))
    row1 = [
        "серво/мотор\nвідхиляється\nна фіксовану\nвеличину",
        "апарат\nобертається\nз певною\nшвидкістю (°/с)",
        "апарат\nнахиляється\nна певний\nкут (°)",
    ]
    for i, x in enumerate(xs):
        f.append(fitbox(x, y1, col_w, 90, row1[i], size=13, fill=FILL,
                        stroke=accents[i]))

    # Ряд 2: стік відпущено (центр)
    y2 = y1 + 120
    f.append(text(30, y2 - 8, "стік відпущено (центр):", size=12,
                  color=MUTED, anchor="start", italic=True))
    row2 = [
        "керма\nповертаються\nв нейтраль —\nкут «пливе»",
        "обертання\nспиняється,\nапарат ЗАВМИРАЄ\nу поточному куті",
        "апарат САМ\nвирівнюється\nв горизонт\n(кут = 0)",
    ]
    for i, x in enumerate(xs):
        f.append(fitbox(x, y2, col_w, 90, row2[i], size=13, fill=FILL,
                        stroke=accents[i]))

    # нижній рядок: що тримає апарат
    y3 = y2 + 108
    holds = ["тримає ПІЛОТ", "тримає ПІЛОТ", "тримає АВТОПІЛОТ"]
    for i, x in enumerate(xs):
        c = accents[i]
        f.append(fitbox(x, y3, col_w, 30, holds[i], size=12, bold=True,
                        fill="#ffffff", stroke=c, color=c))

    render(os.path.join(IMG, "stick-meaning.svg"), W, H, *f)


# ── 2. Каскад: кут обгортає кутову швидкість ────────────────────────────────
def fig_cascade():
    W, H = 780, 360
    f = []
    f.append(text(W / 2, 26, "Режим кута = зовнішня петля НАВКОЛО режиму швидкості",
                  size=16, bold=True))

    ymid = 200

    # блоки внутрішньої петлі (rate): вузол помилки → PID → мотори
    bx = 300
    # PID rate block
    pid, pw, ph = textbox(bx + 120, ymid, "ПІД\nпо кут. швидкості", size=13,
                          bold=True, fill="#eef2ff", stroke=NEG)
    # мотори
    mot, mw, mh = textbox(bx + 300, ymid, "мотори /\nсерво", size=13,
                          fill=FILL, stroke=INK)

    # сумматор помилки швидкості
    sx = bx + 20
    f.append(circle(sx, ymid, 16, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text(sx, ymid + 5, "−", size=20, color=NEG, bold=True))

    # вхід «ціль швидкості» злива
    f.append(arrow(sx + 16, ymid, bx + 120 - pw / 2, ymid, color=NEG))
    f.append(arrow(bx + 120 + pw / 2, ymid, bx + 300 - mw / 2, ymid))
    f.append(pid)
    f.append(mot)

    # вихід моторів → апарат обертається → гіроскоп
    gy = ymid + 95
    gyro, gw, gh = textbox(bx + 300, gy, "гіроскоп\n(вимір °/с)", size=12,
                           fill=FILL, stroke=MUTED)
    f.append(line(bx + 300, ymid + mh / 2, bx + 300, gy - gh / 2, color=MUTED, sw=1.6))
    f.append(gyro)
    # зворотний зв'язок швидкості до сумматора
    f.append(line(bx + 300 - gw / 2, gy, sx, gy, color=MUTED, sw=1.6, dash="5,4"))
    f.append(arrow(sx, gy, sx, ymid + 16, color=MUTED))
    f.append(text((sx + bx + 300) / 2, gy + 16, "виміряна кут. швидкість",
                  size=11, color=MUTED))

    # рамка навколо внутрішньої петлі
    f.append(rect(bx - 20, ymid - 55, 400, 190, fill="none", stroke=NEG, sw=1.4, rx=10))
    f.append(text(bx + 180, ymid - 42, "ВНУТРІШНЯ ПЕТЛЯ — кутова швидкість (rate)",
                  size=11, color=NEG, bold=True))

    # зовнішня петля (angle)
    ax = 90
    f.append(circle(ax, ymid, 16, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text(ax, ymid + 5, "−", size=20, color=FIELD, bold=True))
    pang, paw, pah = textbox(ax + 95, ymid, "P\nпо куту", size=13, bold=True,
                             fill="#e9f9ef", stroke=FIELD)
    f.append(arrow(ax + 16, ymid, ax + 95 - paw / 2, ymid, color=FIELD))
    f.append(pang)
    # вихід P = ціль швидкості → у внутрішній сумматор
    f.append(arrow(ax + 95 + paw / 2, ymid, sx - 16, ymid, color=FIELD))
    f.append(text((ax + 95 + sx) / 2, ymid - 12, "ціль °/с", size=11,
                  color=FIELD, italic=True))

    # вхід зовнішнього: ціль кута (від стіка)
    f.append(arrow(20, ymid, ax - 16, ymid, color=INK))
    f.append(text(20, ymid - 12, "ціль кута", size=11, anchor="start", bold=True))
    f.append(text(20, ymid + 22, "(стік у angle)", size=10, anchor="start", color=MUTED))

    # зворотний кут: від оцінки орієнтації
    ey = ymid - 105
    est, ew, eh = textbox(ax + 200, ey, "оцінка орієнтації (кут)", size=12,
                          fill=FILL, stroke=MUTED)
    f.append(est)
    f.append(line(ax + 200 - ew / 2, ey, ax, ey, color=MUTED, sw=1.6, dash="5,4"))
    f.append(arrow(ax, ey, ax, ymid - 16, color=MUTED))
    f.append(text(ax - 6, ey + 16, "виміряний кут", size=11, color=MUTED, anchor="start"))

    # підпис: у rate-режимі зовнішньої петлі нема
    f.append(fitbox(40, ymid + 60, 225, 64,
                    "У режимі кут. швидкості\nцієї зеленої петлі НЕМАЄ:\nстік задає ціль °/с напряму,\nу вузол внутрішньої петлі",
                    size=11, fill="#fff8f0", stroke=POS, color=POS))

    render(os.path.join(IMG, "angle-rate-cascade.svg"), W, H, *f)


# ── 3. Драбина режимів: що додає кожен шар і що йому потрібно ────────────────
def fig_ladder():
    W, H = 720, 470
    f = []
    f.append(text(W / 2, 28, "Драбина режимів: кожен шар додає автоматику й нову залежність",
                  size=15, bold=True))

    rungs = [
        ("Ручний (manual)", "стік → напряму на серво/мотор", "нічого (лише приймач)", POS),
        ("Кутова швидкість (rate/acro)", "тримає задану кутову швидкість", "гіроскоп", INK),
        ("Кут (angle/stabilize)", "тримає заданий кут, сам вирівнює", "+ акселерометр (оцінка кута)", FIELD),
        ("Утримання висоти", "сам тримає висоту", "+ барометр", NEG),
        ("Утримання позиції", "сам висить на місці", "+ GNSS (супутники)", "#8e44ad"),
    ]
    x = 40
    w = W - 80
    top = 60
    rh = 68
    gap = 12
    for i, (name, adds, needs, c) in enumerate(rungs):
        y = top + i * (rh + gap)
        f.append(rect(x, y, w, rh, fill="#ffffff", stroke=c, sw=2, rx=8))
        # ліва смуга з номером-рівнем
        f.append(rect(x, y, 46, rh, fill=c, stroke=c, sw=0, rx=8))
        f.append(text(x + 23, y + rh / 2 + 6, str(i), size=20, color="#ffffff", bold=True))
        f.append(text(x + 60, y + 22, name, size=14, color=c, bold=True, anchor="start"))
        f.append(text(x + 60, y + 43, adds, size=12, color=INK, anchor="start"))
        # праворуч: що потрібно
        f.append(text(x + w - 14, y + 43, needs, size=11.5, color=MUTED,
                      anchor="end", italic=True))
        # стрілка «більше автоматики / більше залежностей» униз
        if i < len(rungs) - 1:
            f.append(arrow(x + w - 20, y + rh, x + w - 20, y + rh + gap, color=MUTED))

    # бічна вісь
    f.append(text(20, top + 10, "менше", size=11, color=MUTED, anchor="middle"))
    f.append(text(20, top + 5 * (rh + gap) - 20, "більше", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, "mode-ladder.svg"), W, H, *f)


if __name__ == "__main__":
    fig_stick()
    fig_cascade()
    fig_ladder()
    print("OK figures written to", IMG)
