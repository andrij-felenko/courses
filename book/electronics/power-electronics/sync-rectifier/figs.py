# -*- coding: utf-8 -*-
"""Фігури для статті «Синхронний випрямляч».
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── diode-vs-channel: фіксований бар'єр Vf проти омічного падіння I·Rds ─────────
# Ідея (серце теми): діод тримає майже сталі ~0.4 В при будь-якому струмі —
# горизонтальна лінія; канал MOSFET падає I·Rds — пряма з нуля. Нижче точки
# перетину виграє MOSFET; вона лежить дуже далеко, бо Rds — одиниці міліом.

def fig_diode_vs_channel():
    W, H = 700, 380
    L, R = 90, 620            # межі осей по x
    T, B = 70, 300            # верх/низ поля
    Imax = 12.0               # А
    Vmax = 0.6                # В
    Vf = 0.40                 # фіксоване падіння Шотткі
    Rds = 0.005               # Rds(on), Ом → 5 мОм

    def px(i): return L + (i / Imax) * (R - L)
    def py(v): return B - (v / Vmax) * (B - T)

    p = []
    # осі
    p.append(line(L, T, L, B, color=INK, sw=2))
    p.append(line(L, B, R, B, color=INK, sw=2))
    # риски й підписи осі x (струм)
    for i in range(0, int(Imax) + 1, 2):
        x = px(i)
        p.append(line(x, B, x, B + 5, color=INK, sw=1.2))
        p.append(text(x, B + 22, "%d" % i, size=12, color=MUTED))
    p.append(text((L + R) / 2, B + 44, "струм навантаження, А", size=12, color=INK, italic=True))
    # риски й підписи осі y (падіння)
    for v in (0.0, 0.2, 0.4, 0.6):
        y = py(v)
        p.append(line(L - 5, y, L, y, color=INK, sw=1.2))
        p.append(text(L - 12, y + 4, "%.1f" % v, size=11, color=MUTED, anchor="end"))
    p.append(text(L - 12, T - 18, "падіння, В", size=12, color=INK, italic=True, anchor="start"))

    # діод: горизонталь на Vf (фіксований бар'єр)
    p.append(line(px(0), py(Vf), px(Imax), py(Vf), color=POS, sw=2.6))
    p.append(text(px(Imax) - 4, py(Vf) - 10, "діод: Vf ≈ 0.4 В (фіксовано)",
                  size=12, color=POS, anchor="end", bold=True))

    # MOSFET: пряма I·Rds з нуля (омічне падіння)
    p.append(line(px(0), py(0), px(Imax), py(Imax * Rds), color=FIELD, sw=2.6))
    p.append(text(px(Imax) - 4, py(Imax * Rds) - 10, "MOSFET: I·Rds(on)",
                  size=12, color=FIELD, anchor="end", bold=True))

    # затінити зону, де MOSFET виграє (нижче його прямої, під Vf)
    p.append(text(px(7.0), py(0.12), "тут MOSFET падає менше",
                  size=11, color=FIELD))

    render(os.path.join(OUT, "diode-vs-channel.svg"), W, H, *p,
           title="Фіксований бар'єр діода проти омічного падіння каналу")


# ── loss-compare: ті самі ампери, але втрати — діод палить, MOSFET майже ні ─────
# Ідея: на низькому Vвих/великому струмі (1−D≈1) діод губить Vf·I·(1−D), а
# MOSFET — I²·Rds·(1−D); стовпчики показують різницю в разах і підсумковий ККД.

def fig_loss_compare():
    W, H = 700, 460
    # геометрія стовпчиків
    base_y = 320
    top_y = 90
    Pmax = 3.6                # Вт — найвищий стовпчик
    P_diode = 0.4 * 10 * 0.9  # = 3.6 Вт
    P_mos = 10 ** 2 * 0.005 * 0.9  # = 0.45 Вт

    def bar_h(p): return (p / Pmax) * (base_y - top_y)

    p = []
    # підзаголовок-умова
    p.append(text(W / 2, 50, "buck 12 В → 1.2 В, 10 А (D = 0.1 → нижній елемент проводить 90 % циклу)",
                  size=12, color=MUTED, italic=True))
    # базова лінія
    p.append(line(120, base_y, 620, base_y, color=INK, sw=1.6))

    # стовпчик діода
    dx, dw = 200, 120
    dh = bar_h(P_diode)
    p.append(rect(dx, base_y - dh, dw, dh, fill="#fbe9e7", stroke=POS, sw=2, rx=4))
    p.append(text(dx + dw / 2, base_y - dh - 12, "3.6 Вт", size=14, color=POS, bold=True))
    p.append(text(dx + dw / 2, base_y + 22, "Асинхронний", size=12, color=POS, bold=True))
    p.append(text(dx + dw / 2, base_y + 40, "(діод Шотткі)", size=11, color=MUTED))
    p.append(text(dx + dw / 2, base_y + 58, "Vf·I·(1−D)", size=11, color=INK))

    # стовпчик MOSFET
    mx, mw = 420, 120
    mh = bar_h(P_mos)
    p.append(rect(mx, base_y - mh, mw, mh, fill="#eef8ef", stroke=FIELD, sw=2, rx=4))
    p.append(text(mx + mw / 2, base_y - mh - 12, "0.45 Вт", size=14, color=FIELD, bold=True))
    p.append(text(mx + mw / 2, base_y + 22, "Синхронний", size=12, color=FIELD, bold=True))
    p.append(text(mx + mw / 2, base_y + 40, "(нижній MOSFET)", size=11, color=MUTED))
    p.append(text(mx + mw / 2, base_y + 58, "I²·Rds·(1−D)", size=11, color=INK))

    # «×8 менше» між ними
    p.append(text(W / 2, 200, "×8", size=24, color=INK, bold=True))
    p.append(text(W / 2, 224, "менше", size=11, color=MUTED))

    # підсумкові ККД
    e1, _, _ = textbox(dx + dw / 2, base_y + 90, "ККД ≈ 77 %", size=13, bold=True,
                       color=POS, fill="#fbe9e7", stroke=POS, sw=1.6)
    p.append(e1)
    e2, _, _ = textbox(mx + mw / 2, base_y + 90, "ККД ≈ 96 %", size=13, bold=True,
                       color=FIELD, fill="#eef8ef", stroke=FIELD, sw=1.6)
    p.append(e2)

    render(os.path.join(OUT, "loss-compare.svg"), W, H, *p,
           title="Втрати на нижньому елементі: діод проти MOSFET")


# ── dead-time: пауза, коли вимкнені обидва ключі, рятує від наскрізного струму ──
# Ідея: затвори перемикаються не миттєво; якщо перекрити фази ВКЛ, обидва канали
# на мить відкриті — наскрізний струм. Драйвер лишає «мертвий час», коли струм
# котушки веде паразитний body-діод нижнього MOSFET (з його ~0.7 В).

def fig_dead_time():
    W, H = 720, 360
    L, R = 90, 660
    p = []

    # дві доріжки: верхній і нижній затвори
    y_hi, y_lo = 110, 240
    lvl, lab_x = 46, 60       # висота «імпульсу», підпис зліва
    p.append(text(lab_x, y_hi - lvl / 2, "верхній", size=12, color=INK, anchor="start", bold=True))
    p.append(text(lab_x, y_lo - lvl / 2, "нижній", size=12, color=INK, anchor="start", bold=True))

    span = R - L
    # часові межі (у частках): верхній ВКЛ [0..0.40], нижній ВКЛ [0.46..0.94]
    # між ними дві паузи — мертвий час
    def X(f): return L + f * span

    def pulse(y, f0, f1, color):
        x0, x1 = X(f0), X(f1)
        return [
            line(x0, y, x0, y - lvl, color=color, sw=2.4),
            line(x0, y - lvl, x1, y - lvl, color=color, sw=2.4),
            line(x1, y - lvl, x1, y, color=color, sw=2.4),
        ]

    # базові лінії доріжок
    p.append(line(L, y_hi, R, y_hi, color=MUTED, sw=1.2))
    p.append(line(L, y_lo, R, y_lo, color=MUTED, sw=1.2))

    p += pulse(y_hi, 0.04, 0.40, POS)
    p += pulse(y_lo, 0.46, 0.92, NEG)

    # дві зони мертвого часу (вертикальні смуги)
    for f0, f1, _ in [(0.40, 0.46, "a"), (0.92, 0.98, "b")]:
        x0, x1 = X(f0), X(f1)
        p.append(rect(x0, y_hi - lvl - 6, x1 - x0, (y_lo) - (y_hi - lvl) + 12,
                      fill="#fdf6e3", stroke="#d8c98a", sw=1.2, rx=3))

    # підпис мертвого часу
    xc = (X(0.40) + X(0.46)) / 2
    p.append(text(xc, y_lo + 40, "мертвий час", size=11, color="#a9831a", bold=True))
    p.append(text(xc, y_lo + 56, "обидва ВИМКНені", size=10, color=MUTED))
    p.append(line(xc, y_lo + 28, xc, y_lo + 6, color="#a9831a", sw=1.2))

    # стрілка-небезпека: що було б без паузи (перекриття)
    p.append(text(W / 2, H - 36, "без паузи обидва канали на мить відкриті → наскрізний струм (shoot-through)",
                  size=11, color=POS, italic=True))
    # у мертвий час струм веде body-діод нижнього ключа
    p.append(text(W / 2, H - 18, "у паузу струм котушки веде body-діод нижнього MOSFET (~0.7 В)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "dead-time.svg"), W, H, *p,
           title="Мертвий час: пауза між двома ключами проти наскрізного струму")


if __name__ == "__main__":
    fig_diode_vs_channel()
    fig_loss_compare()
    fig_dead_time()
    print("OK: figures written to", OUT)
