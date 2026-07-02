# -*- coding: utf-8 -*-
"""Фігури вставки «proj-pi-fixed-point» теми «І-складова». Запуск: python figs_proj_fixed_point.py
svgkit імпортуємо зі scripts/ (не переписуємо). Окремий файл, щоб не чіпати figs.py статті."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def bitbar(x, y, w, h, label, sub, fill, stroke, color=INK):
    """Смуга-«слово» певної розрядності з підписом усередині й приміткою знизу."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=5)
    out += text(x + w / 2, y + h / 2 + 5, label, size=13, color=color, bold=True)
    if sub:
        out += text(x + w / 2, y + h + 16, sub, size=10.5, color=MUTED)
    return out


# ── 1: розрядність доданка проти ширини накопичувача ──────────────────────────
def fig_accumulator_width():
    W, H = 720, 360
    p = []
    p.append(text(W / 2, 26, "Чому накопичувач мусить бути ширшим за все інше", size=17, bold=True))

    # верхній ряд: множники доданка e·Ki·Δt, кожен зі своєю розрядністю
    y1 = 74
    bh = 40
    x = 70
    p.append(text(x, y1 - 14, "доданок за один такт:", size=12, color=MUTED, anchor="start"))
    e_w, ki_w, dt_w = 96, 116, 120
    gap = 30
    xe = x
    p.append(bitbar(xe, y1, e_w, bh, "e  (16 біт)", "помилка", "#eaf0fd", NEG, NEG))
    xk = xe + e_w + gap
    p.append(text(xe + e_w + gap / 2, y1 + bh / 2 + 6, "×", size=20, color=INK))
    p.append(bitbar(xk, y1, ki_w, bh, "Ki  (Q16)", "коефіцієнт", "#eafaf0", FIELD, FIELD))
    xd = xk + ki_w + gap
    p.append(text(xk + ki_w + gap / 2, y1 + bh / 2 + 6, "×", size=20, color=INK))
    p.append(bitbar(xd, y1, dt_w, bh, "Δt  (Q16, с)", "крок часу", "#fdf3e6", "#b8791f", "#8a5a12"))

    # стрілка вниз до широкого добутку
    midx = (xe + xd + dt_w) / 2
    y2 = 172
    p.append(arrow(midx, y1 + bh + 22, midx, y2 - 8, color=MUTED, sw=1.6))
    p.append(text(midx + 12, (y1 + bh + 22 + y2 - 8) / 2 + 4, "розрядності складаються", size=11, color=MUTED, anchor="start"))

    # добуток — широке 64-бітне слово
    prod_x, prod_w = 150, 420
    p.append(bitbar(prod_x, y2, prod_w, 44, "e · Ki · Δt  →  до ~48 біт", "один доданок уже переростає 32 біти", "#fdecea", POS, POS))

    # накопичувач — ще ширший, 64 біт
    y3 = 268
    p.append(arrow(midx, y2 + 44 + 18, midx, y3 - 8, color=MUTED, sw=1.6))
    p.append(text(midx + 12, (y2 + 44 + 18 + y3 - 8) / 2 + 4, "+ тисячі доданків за секунди", size=11, color=MUTED, anchor="start"))
    acc_x, acc_w = 96, 528
    p.append(bitbar(acc_x, y3, acc_w, 46, "накопичувач I  —  64 біти (int64_t)", "", "#eafaf0", FIELD, FIELD))
    p.append(text(W / 2, y3 + 46 + 22,
                  "у вихід повертаємо лише наприкінці: (Ki·I) зсунути назад і затиснути",
                  size=11.5, color=INK))

    render(os.path.join(OUT, "fp-accumulator-width.svg"), W, H, *p)


# ── 2: доданок тоне під 1 LSB — і накопичувач застигає, не досягши нуля ────────
def fig_integrator_stall():
    W, H = 720, 340
    p = []
    p.append(text(W / 2, 26, "Пастка: крихітний доданок тоне під молодшим бітом", size=17, bold=True))

    colw = 330
    lx, rx = 44, 386
    top = 58
    boxh = 236

    # ліва панель — наївно (зсув доданка перед додаванням)
    p.append(rect(lx, top, colw, boxh, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    p.append(text(lx + colw / 2, top + 24, "Наївно: масштабуємо доданок ОДРАЗУ", size=12.5, bold=True, color=POS))
    p.append(text(lx + colw / 2, top + 46, "inc = (e·Ki·Δt) >> 16", size=12, color=INK))

    # маленький доданок vs 1 LSB
    base_y = top + 92
    lsb_x = lx + 30
    p.append(text(lsb_x, base_y - 14, "1 LSB накопичувача", size=10.5, color=MUTED, anchor="start"))
    p.append(rect(lsb_x, base_y, 40, 26, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=3))
    p.append(text(lsb_x + 20, base_y + 17, "1", size=12, color=INK, bold=True))
    p.append(text(lsb_x + 60, base_y + 17, ">", size=16, color=POS, bold=True, anchor="start"))
    p.append(rect(lsb_x + 86, base_y + 8, 40, 10, fill="#fbe4e1", stroke=POS, sw=1.2, rx=2))
    p.append(text(lsb_x + 86 + 44, base_y + 17, "inc = 0.4  →  0", size=11.5, color=POS, anchor="start", bold=True))

    p.append(text(lx + colw / 2, base_y + 66, "доданок < 1 → цілочислово стає 0", size=11.5, color=INK))
    p.append(text(lx + colw / 2, base_y + 88, "накопичувач НЕ росте", size=12, color=POS, bold=True))
    p.append(text(lx + colw / 2, base_y + 116, "зсув застигає — I мертвий за малих e", size=11, color=MUTED))

    # права панель — правильно (копимо в широкому, зсуваємо наприкінці)
    p.append(rect(rx, top, colw, boxh, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(rx + colw / 2, top + 24, "Правильно: копимо БЕЗ зсуву", size=12.5, bold=True, color=FIELD))
    p.append(text(rx + colw / 2, top + 46, "I += e·Δt   (широкий, повний масштаб)", size=11.5, color=INK))

    by = top + 92
    p.append(text(rx + colw / 2, by, "кожен крок додає повне e·Δt —", size=11.5, color=INK))
    p.append(text(rx + colw / 2, by + 20, "молодші біти НЕ втрачаються", size=12, color=FIELD, bold=True))

    # стосик крихітних доданків, що складаються у щось помітне
    sx = rx + 40
    sy = by + 44
    acc = 0
    for i in range(6):
        p.append(rect(sx + i * 34, sy, 30, 12, fill="#d6f0e0", stroke=FIELD, sw=1.1, rx=2))
    p.append(text(rx + colw / 2, sy + 40, "0.4 + 0.4 + 0.4 + …  →  накопичується", size=11, color=INK))
    p.append(text(rx + colw / 2, sy + 62, "зсув робимо ЛИШЕ у вихід: (Ki·I) >> 16", size=11, color=MUTED))

    render(os.path.join(OUT, "fp-integrator-stall.svg"), W, H, *p)


if __name__ == "__main__":
    fig_accumulator_width()
    fig_integrator_stall()
    print("OK: figures written to", OUT)
