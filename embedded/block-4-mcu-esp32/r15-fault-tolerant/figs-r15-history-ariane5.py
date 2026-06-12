# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історії Ariane 5, рейс 501 — Розділ 4.15.
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Фігури:
  fig-r15-0-1-sri-obc-chain.svg   — архітектура навігації: два SRI → шина → OBC → сопла
  fig-r15-0-2-int16-overflow.svg  — числова вісь: діапазон int16 і переповнення BH
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.0.1 — Ланцюг навігації та керування Ariane 5
# Два ІДЕНТИЧНІ SRI (активний + резервний) → спільна шина → OBC → сопла.
# Висновок: однаковий софт = спільна вада → обидва падають одночасно.
# ══════════════════════════════════════════════════════════════════════════════
def fig_sri_obc_chain():
    W, H = 820, 400
    frags = []

    # ── Заголовок ─────────────────────────────────────────────────────────
    frags.append(text(W / 2, 32, "Ланцюг навігації та керування — Ariane 5 (рейс 501)",
                      size=15, bold=True, color=INK))
    frags.append(text(W / 2, 52,
                      "Два SRI крутять ІДЕНТИЧНИЙ софт — одна вада валить обох одночасно",
                      size=11, color=MUTED))

    # ── SRI активний ──────────────────────────────────────────────────────
    sri_a_cx = 130
    sri_a_cy = 160
    tb_a, aw, ah = textbox(sri_a_cx, sri_a_cy,
                           "SRI\n(активний)\nфлайт-код v2.6",
                           size=12, fill="#fdecea", stroke=POS, sw=2.5, pad=12,
                           bold=False)
    frags.append(tb_a)
    # Мітка «той самий код»
    frags.append(text(sri_a_cx, sri_a_cy + ah / 2 + 13,
                      "▲ той самий код", size=10, color=POS))

    # ── SRI резервний ─────────────────────────────────────────────────────
    sri_b_cx = 130
    sri_b_cy = 290
    tb_b, bw, bh = textbox(sri_b_cx, sri_b_cy,
                           "SRI\n(гарячий резерв)\nфлайт-код v2.6",
                           size=12, fill="#fdecea", stroke=POS, sw=2.5, pad=12,
                           bold=False)
    frags.append(tb_b)
    frags.append(text(sri_b_cx, sri_b_cy + bh / 2 + 13,
                      "▲ той самий код", size=10, color=POS))

    # ── Дужка "однакова вада" між двома SRI ──────────────────────────────
    brace_x = sri_a_cx + aw / 2 + 12
    y_top = sri_a_cy - ah / 2 + 4
    y_bot = sri_b_cy + bh / 2 - 4
    frags.append(line(brace_x, y_top, brace_x + 12, y_top, color=POS, sw=1.5))
    frags.append(line(brace_x + 12, y_top, brace_x + 12, y_bot, color=POS, sw=1.5))
    frags.append(line(brace_x, y_bot, brace_x + 12, y_bot, color=POS, sw=1.5))
    mid_y = (y_top + y_bot) / 2
    frags.append(line(brace_x + 12, mid_y, brace_x + 26, mid_y, color=POS, sw=1.5))
    tb_cm, _, _ = textbox(brace_x + 26 + 68, mid_y,
                          "Спільна вада\n(common-mode fault):\nпадають обидва",
                          size=10, fill="#fdecea", stroke=POS, pad=7)
    frags.append(tb_cm)

    # ── Шина даних ────────────────────────────────────────────────────────
    bus_x_left = 370
    bus_x_right = 440
    bus_y_top = 130
    bus_y_bot = 320
    bus_fill = "#e8edf5"
    frags.append(rect(bus_x_left, bus_y_top, bus_x_right - bus_x_left,
                      bus_y_bot - bus_y_top, fill=bus_fill, stroke=NEG, sw=2, rx=4))
    frags.append(text((bus_x_left + bus_x_right) / 2, (bus_y_top + bus_y_bot) / 2 + 5,
                      "Шина\nданих", size=12, bold=True, color=NEG))

    # Стрілки SRI → шина
    frags.append(arrow(sri_a_cx + aw / 2, sri_a_cy, bus_x_left, sri_a_cy, color=INK, sw=1.8))
    frags.append(arrow(sri_b_cx + bw / 2, sri_b_cy, bus_x_left, sri_b_cy, color=INK, sw=1.8))

    # ── OBC ───────────────────────────────────────────────────────────────
    obc_cx = 580
    obc_cy = 225
    tb_obc, ow, oh = textbox(obc_cx, obc_cy,
                             "OBC\n(бортовий\nкомп'ютер)",
                             size=13, fill="#eaf0fd", stroke=NEG, sw=2.5, pad=14, bold=True)
    frags.append(tb_obc)

    # Стрілка шина → OBC
    frags.append(arrow(bus_x_right, obc_cy, obc_cx - ow / 2, obc_cy, color=NEG, sw=2))

    # ── Гідравліка сопел ──────────────────────────────────────────────────
    noz_cx = 740
    noz_cy = 165
    tb_noz1, nw1, nh1 = textbox(noz_cx, noz_cy,
                                "Гідроприводи\nbustери (SRB)\nсопла",
                                size=11, fill="#e8f5e9", stroke=FIELD, sw=2, pad=10)
    frags.append(tb_noz1)

    noz2_cy = 285
    tb_noz2, nw2, nh2 = textbox(noz_cx, noz2_cy,
                                "Гідроприводи\nмаршовий\nдвигун (Vulcain)",
                                size=11, fill="#e8f5e9", stroke=FIELD, sw=2, pad=10)
    frags.append(tb_noz2)

    # Стрілки OBC → сопла
    frags.append(arrow(obc_cx + ow / 2, obc_cy - 20, noz_cx - nw1 / 2, noz_cy, color=FIELD, sw=1.8))
    frags.append(arrow(obc_cx + ow / 2, obc_cy + 20, noz_cx - nw2 / 2, noz2_cy, color=FIELD, sw=1.8))

    # ── Виноска: «що сталося» ─────────────────────────────────────────────
    note_y = H - 42
    tb_note, _, _ = textbox(W / 2, note_y,
                            "Обидва SRI відмовили з однієї причини (overflow BH). "
                            "OBC прийняв діагностичний код за дані → різке відхилення сопел.",
                            size=11, fill="#fff8dc", stroke="#c0392b", pad=8)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r15-0-1-sri-obc-chain.svg"), W, H, *frags)
    print("  fig-r15-0-1-sri-obc-chain.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.0.2 — Переповнення int16: BH Ariane 5 далеко за межею
# Горизонтальна числова вісь: діапазон int16 [−32768; 32767],
# значення BH Ariane 5 (≈38000) і типове значення Ariane 4 (≈7000) у межах.
# ══════════════════════════════════════════════════════════════════════════════
def fig_int16_overflow():
    W, H = 820, 360
    frags = []

    # ── Заголовок ─────────────────────────────────────────────────────────
    frags.append(text(W / 2, 32, "Переповнення, що знищило ракету: float64 → int16",
                      size=15, bold=True, color=INK))
    frags.append(text(W / 2, 52,
                      "Горизонтальний зсув BH вискочив за межу 16-бітного цілого → Operand Error → зупинка SRI",
                      size=11, color=MUTED))

    # ── Числова вісь ──────────────────────────────────────────────────────
    ax_y = 195          # y вісі
    ax_x0 = 60          # початок (крайній лівий)
    ax_x1 = 700         # кінець видимої частини (до «обриву»)
    frags.append(line(ax_x0, ax_y, ax_x1, ax_y, color=INK, sw=2))
    # стрілка праворуч
    frags.append(arrow(ax_x1 - 2, ax_y, ax_x1 + 30, ax_y, color=INK, sw=2))

    # Масштабування: відображаємо від -36000 до +42000 (total ~78000) на відрізок 640px
    V_MIN = -36000
    V_MAX = 42000
    V_RANGE = V_MAX - V_MIN
    PX_RANGE = ax_x1 - ax_x0

    def val_to_x(v):
        return ax_x0 + (v - V_MIN) / V_RANGE * PX_RANGE

    # ── Діапазон int16 [−32768; 32767] — виділена зона ──────────────────
    x_neg = val_to_x(-32768)
    x_pos = val_to_x(32767)
    zone_y = ax_y - 30
    zone_h = 60
    frags.append(rect(x_neg, zone_y, x_pos - x_neg, zone_h,
                      fill="#e8f5e9", stroke=FIELD, sw=2, rx=4))
    frags.append(text((x_neg + x_pos) / 2, ax_y + 4,
                      "безпечний діапазон int16", size=11, color=FIELD, bold=True))

    # Мітки меж
    tick_h = 10
    for xv, lbl in [(x_neg, "−32768"), (x_pos, "32767")]:
        frags.append(line(xv, ax_y - tick_h, xv, ax_y + tick_h, color=INK, sw=1.8))
        frags.append(text(xv, ax_y + tick_h + 16, lbl, size=11, color=INK))

    # Нуль
    x_zero = val_to_x(0)
    frags.append(line(x_zero, ax_y - 6, x_zero, ax_y + 6, color=MUTED, sw=1.2))
    frags.append(text(x_zero, ax_y + 20, "0", size=10, color=MUTED))

    # ── Значення Ariane 4 ≈ 7000 (у межах) ──────────────────────────────
    x_a4 = val_to_x(7000)
    dot_r = 7
    frags.append(circle(x_a4, ax_y, dot_r, fill=FIELD, stroke=FIELD, sw=2))
    frags.append(text(x_a4, ax_y - 20, "BH Ariane 4", size=11, color=FIELD))
    frags.append(text(x_a4, ax_y - 36, "≈ 7 000", size=10, color=FIELD))

    # ── «Стіна» — межа 32767 з позначкою обриву ─────────────────────────
    wall_x = x_pos
    # Зигзаг «обриву» праворуч від wall_x
    zz_y = ax_y
    zz_w = 18
    zig_pts = [
        (wall_x, zz_y - 22),
        (wall_x + zz_w, zz_y - 8),
        (wall_x, zz_y + 8),
        (wall_x + zz_w, zz_y + 22),
    ]
    for i in range(len(zig_pts) - 1):
        x1, y1 = zig_pts[i]
        x2, y2 = zig_pts[i + 1]
        frags.append(line(x1, y1, x2, y2, color=POS, sw=2.5))

    # ── Значення Ariane 5 ≈ 38000 (ЗА межею) ────────────────────────────
    x_a5 = val_to_x(38000)
    frags.append(circle(x_a5, ax_y, dot_r, fill=POS, stroke=POS, sw=2))
    frags.append(text(x_a5, ax_y - 20, "BH Ariane 5", size=11, color=POS, bold=True))
    frags.append(text(x_a5, ax_y - 36, "≈ 38 000", size=11, color=POS, bold=True))

    # Стрілка «вийшов за межу»
    frags.append(arrow(x_pos + 4, ax_y - 56, x_a5 - dot_r - 2, ax_y - 8, color=POS, sw=1.8))
    tb_over, _, _ = textbox(x_pos + 50, ax_y - 78,
                            "Operand Error!\nSRI зупинено",
                            size=11, fill="#fdecea", stroke=POS, sw=2, pad=7)
    frags.append(tb_over)

    # ── Стрілка «float64 → int16» з точкою обриву ────────────────────────
    conv_y = ax_y + 70
    frags.append(arrow(val_to_x(38000), conv_y, x_pos + 24, conv_y, color=POS, sw=2))
    tb_conv, _, _ = textbox((val_to_x(38000) + x_pos + 24) / 2, conv_y + 22,
                            "float64 → int16: вийшло за [−32768; 32767]",
                            size=11, fill="#fdecea", stroke=POS, pad=7)
    frags.append(tb_conv)

    # ── Легенда ───────────────────────────────────────────────────────────
    leg_y = H - 42
    tb_leg, _, _ = textbox(W / 2, leg_y,
                           "Ariane 4 — повільніший старт, BH у нормі. "
                           "Ariane 5 — потужніший, горизонтальна швидкість у 5× більша → BH виходить за 32767.",
                           size=11, fill="#f4f6f8", stroke=MUTED, pad=8)
    frags.append(tb_leg)

    render(os.path.join(OUT, "fig-r15-0-2-int16-overflow.svg"), W, H, *frags)
    print("  fig-r15-0-2-int16-overflow.svg — OK")


if __name__ == "__main__":
    print("Генерація фігур для r15-history-ariane5 …")
    fig_sri_obc_chain()
    fig_int16_overflow()
    print("Готово.")
