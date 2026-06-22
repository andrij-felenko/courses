# -*- coding: utf-8 -*-
"""Фігури до вставки «Метод двох навантажень» (тема thevenin-equivalent).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Генерує дві фігури вставки proj-two-load-method.md:
  two-load-method.svg — дві (I,V)-точки на прямій джерела V = Vth − I·Rth;
  two-load-mcu.svg    — блок-схема автомата на МК (два ключі-навантаження + АЦП).
Інші SVG теми (oc-sc, deactivate, …) належать самій статті й тут не чіпаються.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: дві точки задають пряму джерела ────────────────────────────────
def fig_two_load_method():
    W, H = 760, 430
    # межі полотна графіка
    ox, oy = 90, 360          # початок координат (нижній лівий кут осей)
    ax_w, ax_h = 470, 280     # довжина осей
    # числова модель (узгоджена з worked-прикладом): Vth=4.02, Rth=0.318
    Vth, Rth = 4.02, 0.318
    Imax, Vmax = 1.6, 4.4     # масштаб осей
    i1, i2 = 0.390, 1.333     # струми двох навантажень
    v1, v2 = Vth - i1 * Rth, Vth - i2 * Rth

    def px(i):                # струм → екранне x
        return ox + (i / Imax) * ax_w
    def py(v):                # напруга → екранне y
        return oy - (v / Vmax) * ax_h

    P = []
    # осі
    P.append(arrow(ox, oy, ox + ax_w + 24, oy))           # вісь I →
    P.append(arrow(ox, oy, ox, oy - ax_h - 24))           # вісь V ↑
    P.append(text(ox + ax_w + 20, oy + 22, "струм I", size=13, italic=True))
    P.append(text(ox - 8, oy - ax_h - 30, "напруга V", size=13, anchor="middle", bold=True))

    # пряма джерела V = Vth − I·Rth (від I=0 до I=Imax)
    P.append(line(px(0), py(Vth), px(Imax), py(Vth - Imax * Rth),
                  color=POS, sw=2.4, dash="6 4"))

    # точка Vth на осі (екстраполяція до I=0)
    P.append(circle(px(0), py(Vth), 5.5, fill=POS, stroke=POS))
    P.append(text(px(0) + 12, py(Vth) - 10, "Vth (екстрап. до I = 0)",
                  size=11, color=POS, anchor="start", bold=True))

    # дві виміряні точки + пунктири-проєкції на осі
    for (ii, vv, col, lab) in [(i1, v1, NEG, "навантаження R₁"),
                               (i2, v2, FIELD, "навантаження R₂")]:
        P.append(line(px(ii), py(vv), px(ii), oy, color=MUTED, sw=1, dash="3 3"))
        P.append(line(px(ii), py(vv), ox, py(vv), color=MUTED, sw=1, dash="3 3"))
        P.append(circle(px(ii), py(vv), 6, fill=col, stroke=col))
        P.append(text(px(ii) + 10, py(vv) - 9, lab, size=11, color=col, anchor="start", bold=True))

    # підпис нахилу
    mid_i = (i1 + i2) / 2
    P.append(text(px(mid_i) + 64, py(Vth - mid_i * Rth) + 6,
                  "нахил = −Rth", size=12, color=POS, anchor="start", bold=True))

    # бічна панель із формулами
    bx, by, bw, bh = 600, 110, 150, 250
    P.append(rect(bx, by, bw, bh, fill=FILL, stroke=MUTED, sw=1.5, rx=10))
    P.append(text(bx + bw / 2, by + 26, "Дві пари (I, V):", size=12, bold=True))
    P.append(text(bx + 14, by + 54, "V₁ = Vth − I₁·Rth", size=11, anchor="start"))
    P.append(text(bx + 14, by + 76, "V₂ = Vth − I₂·Rth", size=11, anchor="start"))
    P.append(line(bx + 14, by + 92, bx + bw - 14, by + 92, color="#e0e3e6", sw=1.2))
    P.append(text(bx + 14, by + 118, "Rth = (V₁−V₂)/(I₂−I₁)", size=11, color=FIELD, anchor="start", bold=True))
    P.append(text(bx + 14, by + 142, "Vth = V₁ + I₁·Rth", size=11, color=FIELD, anchor="start", bold=True))
    P.append(line(bx + 14, by + 158, bx + bw - 14, by + 158, color="#e0e3e6", sw=1.2))
    P.append(text(bx + 14, by + 184, "Ні відкритих,", size=11, color=MUTED, anchor="start"))
    P.append(text(bx + 14, by + 202, "ні замкнених клем —", size=11, color=MUTED, anchor="start"))
    P.append(text(bx + 14, by + 220, "лише два R.", size=11, color=NEG, anchor="start", bold=True))

    render(os.path.join(IMG, "two-load-method.svg"), W, H, *P,
           title="Метод двох навантажень: дві точки задають пряму джерела")


# ── Фігура 2: автомат на мікроконтролері ─────────────────────────────────────
def fig_two_load_mcu():
    W, H = 860, 410
    P = []
    midy = 195

    # невідоме джерело
    src, sw_, sh_ = "невідоме\nджерело", 120, 84
    sx, sy = 40, midy - sh_ / 2
    P.append(rect(sx, sy, sw_, sh_, fill="#eef2fb", stroke=NEG, sw=2, rx=8))
    P.append(mtext(sx + sw_ / 2, midy - 4, "невідоме\nджерело", size=12, bold=True))

    # клеми
    tx = sx + sw_ + 70
    P.append(line(sx + sw_, midy, tx, midy, color=INK, sw=2))
    P.append(circle(tx, midy, 4, fill=INK, stroke=INK))
    P.append(text((sx + sw_ + tx) / 2, midy - 12, "клеми", size=10, color=MUTED))

    # два ключі-навантаження
    bx, bw, bh = tx + 50, 160, 60
    P.append(rect(bx, midy - 78, bw, bh, fill=BG, stroke=MUTED, sw=1.6, rx=6))
    P.append(text(bx + bw / 2, midy - 52, "R₁ (легке)", size=12, bold=True))
    P.append(text(bx + bw / 2, midy - 34, "ключ 1", size=10, color=MUTED))
    P.append(rect(bx, midy + 18, bw, bh, fill=BG, stroke=MUTED, sw=1.6, rx=6))
    P.append(text(bx + bw / 2, midy + 44, "R₂ (важче)", size=12, bold=True))
    P.append(text(bx + bw / 2, midy + 62, "ключ 2", size=10, color=MUTED))
    P.append(line(tx, midy, bx, midy - 48, color=INK, sw=1.6))
    P.append(line(tx, midy, bx, midy + 48, color=INK, sw=1.6))

    # АЦП + МК
    ax, aw, ah = bx + bw + 56, 150, 84
    ay = midy - ah / 2
    P.append(rect(ax, ay, aw, ah, fill="#eef7f0", stroke=FIELD, sw=2, rx=8))
    P.append(text(ax + aw / 2, midy - 12, "АЦП + МК", size=13, bold=True))
    P.append(mtext(ax + aw / 2, midy + 8, "читає V, керує\nключами, рахує", size=10, color=MUTED))
    P.append(arrow(bx + bw, midy, ax, midy, color=FIELD, sw=1.8))
    P.append(text((bx + bw + ax) / 2, midy - 12, "V", size=12, color=FIELD, bold=True))

    # результат
    rx, rw, rh = ax + aw + 36, 150, 84
    ry = midy - rh / 2
    P.append(rect(rx, ry, rw, rh, fill="#fff8ee", stroke="#e08030", sw=1.6, rx=8))
    P.append(text(rx + rw / 2, midy - 6, "Vth, Rth", size=14, color=POS, bold=True))
    P.append(mtext(rx + rw / 2, midy + 16, "(+ «здоров'я»\nбатареї)", size=10, color=MUTED))
    P.append(arrow(ax + aw, midy, rx, midy, color=INK, sw=2))

    # стрічка пасток унизу
    fy = 332
    P.append(rect(40, fy, W - 80, 56, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    P.append(text(56, fy + 22,
                  "Пастки МК: навантаження мусять давати ДОСИТЬ різні струми (інакше I₂−I₁ тоне в шумі);",
                  size=11, anchor="start"))
    P.append(text(56, fy + 42,
                  "зачекай на встановлення перед читанням; усереднюй АЦП; не коротуй; Rth — знімок (заряд, t°).",
                  size=11, anchor="start"))

    render(os.path.join(IMG, "two-load-mcu.svg"), W, H, *P,
           title="Автомат на МК: два навантаження, АЦП — і еквівалент готовий")


if __name__ == "__main__":
    fig_two_load_method()
    fig_two_load_mcu()
    print("written:", os.listdir(IMG))
