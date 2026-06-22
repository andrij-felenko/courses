# -*- coding: utf-8 -*-
"""figs.py — фігури до теми «Бюджет батареї» та її вставок.
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Імена файлів — slug-only, без номерів (§2, §5 AUTHORING)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

ACT = "#c0392b"   # активний сплеск (червоний)
SLP = "#2457d6"   # сон (синій)


# ── log-шкала струму (спільна для двох профілів сон/сплеск) ──────────────────
def _log_axis(parts, x0, y_top, y_bot, x_right, decades):
    """decades — список (мітка, степінь10) знизу вгору. Повертає y(степінь)."""
    import math
    lo = decades[0][1]
    hi = decades[-1][1]
    span = hi - lo

    def y_of(p):
        return y_bot - (p - lo) / span * (y_bot - y_top)

    parts.append(line(x0, y_top, x0, y_bot, color=LINE, sw=1.5))
    parts.append(line(x0, y_bot, x_right, y_bot, color=LINE, sw=1.5))
    for label, p in decades:
        y = y_of(p)
        parts.append(line(x0 - 5, y, x0, y, color=MUTED, sw=1.0))
        parts.append(line(x0, y, x_right, y, color=MUTED, sw=0.5, dash="3,4"))
        parts.append(text(x0 - 8, y + 4, label, size=10, color=MUTED, anchor="end"))
    return y_of


# ── Фігура (стаття 1): час життя = ємність ÷ середній струм ──────────────────
# Ліворуч — аналогія резервуару (ємність = об'єм, середній струм = витік).
# Праворуч — обернена задача: щоб CR2032 прожила рік, середній струм ≤ ~25 мкА.
def fig_budget_formula():
    W, H = 760, 380
    parts = []

    # ── резервуар ліворуч ──
    parts.append(rect(125, 70, 140, 200, fill="#dbeafe", stroke=SLP, sw=2.5, rx=4))
    parts.append(rect(127, 140, 136, 128, fill=SLP, sw=0.0, rx=2, stroke="none"))
    box, _, _ = textbox(195, 205, "C = 220 мА·год\n(CR2032)", size=12,
                        fill="#dbeafe", stroke=SLP, color=SLP, bold=True)
    parts.append(box)
    parts.append(rect(265, 220, 55, 20, fill="#e67e22", stroke="#e67e22", sw=0.0, rx=4))
    parts.append(arrow(320, 230, 350, 230, color="#e67e22", sw=3.0))
    parts.append(text(335, 254, "I_сер [мА]", size=12, color="#e67e22", bold=True))
    parts.append(text(335, 270, "витік", size=11, color="#e67e22"))
    box, _, _ = textbox(195, 305, "t [год] = C [мА·год] / I_сер [мА]", size=14,
                        fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)
    parts.append(box)
    box, _, _ = textbox(195, 350, "вирішує СЕРЕДНІЙ струм — не піковий", size=12,
                        fill="#fef9e7", stroke="#f39c12")
    parts.append(box)

    # ── обернена задача праворуч ──
    parts.append(line(400, 55, 400, 350, color=MUTED, sw=1.0, dash="6,4"))
    parts.append(text(575, 65, "Обернена задача:", size=14, bold=True))

    def row(y, label, value, vfill, vstroke, vcol, vbold=False):
        parts.append(rect(430, y, 145, 44, fill="#f0f0f0", stroke=MUTED, sw=1.5))
        b, _, _ = textbox(502.5, y + 22, label, size=13, fill="#f0f0f0",
                          stroke="none", color=INK, bold=True)
        parts.append(b)
        b, _, _ = textbox(670.5, y + 22, value, size=12, fill=vfill,
                          stroke=vstroke, color=vcol, bold=vbold, min_w=175)
        parts.append(b)

    row(90, "Мета:", "прожити 1 рік = 8760 год", "#f0f0f0", LINE, INK)
    row(152, "Батарея:", "CR2032 = 220 мА·год", "#d6eaf8", SLP, SLP)
    row(214, "Стеля струму:", "220 / 8760 ≈ 25 мкА", "#fdecea", ACT, ACT, True)
    box, _, _ = textbox(575, 285, "бюджет ≈ 25 мкА середнього\n→ мікроамперна дисципліна",
                        size=13, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)
    parts.append(box)
    box, _, _ = textbox(575, 345, "ESP32 у передачі = 150–250 мА\n→ у ~6000 разів більше бюджету",
                        size=11, fill="#fdecea", stroke=ACT, color=INK)
    parts.append(box)

    render("img/budget-formula.svg", W, H, *parts,
           title="Час життя = ємність ÷ середній струм")


# ── Фігура (стаття 2): профіль струму — пік проти сну ────────────────────────
# Довге плато сну (синє) і вузькі піки передачі (червоні). Пунктир — середній
# струм: він стоїть значно вище плато, бо площа під піком (заряд) домінує.
def fig_pulse_vs_average():
    W, H = 720, 360
    parts = []
    decades = [("1 мкА", 0), ("10 мкА", 1), ("100 мкА", 2),
               ("1 мА", 3), ("10 мА", 4), ("100 мА", 5)]
    y_of = _log_axis(parts, 70, 50, 270, 660, decades)

    y_sleep = y_of(1)            # 10 мкА
    y_peak = y_of(5.2)           # ~160 мА (трохи вище 100 мА)
    y_avg = y_of(3.43)           # ≈ 2.7 мА

    # два цикли: сон-пік-сон-пік-сон
    xs = [70, 261.8, 315.8, 507.6, 561.7, 660]
    parts.append(line(xs[0], y_sleep, xs[1], y_sleep, color=SLP, sw=2.5))
    parts.append(line(xs[1], y_sleep, xs[1], y_peak, color=ACT, sw=1.8))
    parts.append(line(xs[1], y_peak, xs[2], y_peak, color=ACT, sw=3.0))
    parts.append(line(xs[2], y_peak, xs[2], y_sleep, color=ACT, sw=1.8))
    parts.append(line(xs[2], y_sleep, xs[3], y_sleep, color=SLP, sw=2.5))
    parts.append(line(xs[3], y_sleep, xs[3], y_peak, color=ACT, sw=1.8))
    parts.append(line(xs[3], y_peak, xs[4], y_peak, color=ACT, sw=3.0))
    parts.append(line(xs[4], y_peak, xs[4], y_sleep, color=ACT, sw=1.8))
    parts.append(line(xs[4], y_sleep, xs[5], y_sleep, color=SLP, sw=2.5))
    parts.append(rect(xs[1], y_peak, xs[2] - xs[1], y_sleep - y_peak,
                      fill="#fdecea", stroke="none", sw=0.0, rx=0))
    parts.append(rect(xs[3], y_peak, xs[4] - xs[3], y_sleep - y_peak,
                      fill="#fdecea", stroke="none", sw=0.0, rx=0))

    parts.append(line(70, y_avg, 660, y_avg, color=FIELD, sw=2.2, dash="10,5"))
    parts.append(text(666, y_avg + 4, "I_сер", size=12, color=FIELD, anchor="start", bold=True))
    parts.append(text(666, y_avg + 18, "≈ 2.7 мА", size=11, color=FIELD, anchor="start"))

    parts.append(text(94, y_sleep - 10, "сон  10 мкА", size=11, color=SLP, anchor="start", bold=True))
    parts.append(text(288.8, y_peak - 14, "TX 160 мА", size=11, color=ACT, bold=True))
    parts.append(text(288.8, y_peak - 28, "2 с / 60 с", size=10, color=ACT))

    box, _, _ = textbox(360, 335,
                        "площа під піком (заряд) домінує — навіть рідкісний пік задирає середнє",
                        size=11, fill="#eafaf1", stroke=FIELD)
    parts.append(box)
    parts.append(text(14, 160, "струм (лог. шкала)", size=11, color=MUTED,
                      anchor="middle"))
    parts[-1] = parts[-1].replace("<text ", '<text transform="rotate(-90,14,160)" ')

    render("img/pulse-vs-average.svg", W, H, *parts,
           title="Вирішує середній струм: площа під піком, а не висота")


# ── Фігура (математика 1): паспортна ємність → ефективна ─────────────────────
def fig_effective_capacity():
    W, H = 640, 400
    parts = []
    # повний стовпчик
    parts.append(rect(50, 70, 100, 260, fill="#dbeafe", stroke="#4a90d9", sw=2.0, rx=4))
    parts.append(text(100, 58, "Q_паспорт", size=13, color="#4a90d9", bold=True))
    parts.append(text(100, 42, "3000 мА·год", size=12, color="#4a90d9"))
    # відрахування
    parts.append(rect(50, 70, 100, 52, fill="#fde68a", stroke="#e67e22", sw=1.5, rx=2))
    parts.append(text(100, 101, "−t°C (×k_temp)", size=10, color="#e67e22"))
    parts.append(rect(50, 122, 100, 31.2, fill="#fecaca", stroke="#e74c3c", sw=1.5, rx=2))
    parts.append(text(100, 142.6, "−хвіст (×k_use)", size=10, color="#e74c3c"))
    parts.append(rect(50, 153.2, 100, 2.6, fill="#e9d5ff", stroke="#8e44ad", sw=1.5, rx=2))
    parts.append(text(100, 159.5, "−саморозряд", size=10, color="#8e44ad"))
    parts.append(rect(50, 155.8, 100, 174.2, fill="#bbf7d0", stroke=FIELD, sw=1.5, rx=2))
    # підсумковий стовпчик
    parts.append(rect(480, 155.8, 100, 174.2, fill="#bbf7d0", stroke=FIELD, sw=2.5, rx=4))
    parts.append(text(530, 143.8, "Q_eff", size=13, color=FIELD, bold=True))
    parts.append(text(530, 127.8, "≈ 2040 мА·год", size=12, color=FIELD))
    parts.append(line(158, 242.9, 472, 242.9, color=FIELD, sw=2.0))
    parts[-1] = parts[-1].replace("/>", ' marker-end="url(#arrow)"/>')
    parts.append(line(40, 330, 590, 330, color=MUTED, sw=1.0))
    # легенда
    leg = [("#fde68a", "#e67e22", "−температура (×k_temp = 0.80): −600 мА·год", 70),
           ("#fecaca", "#e74c3c", "−хвіст під відсічкою (×k_use = 0.85): −255 мА·год", 96),
           ("#e9d5ff", "#8e44ad", "−саморозряд за строк служби: −30 мА·год", 122),
           ("#bbf7d0", FIELD, "= Q_eff ≈ 2040 мА·год (у бюджет)", 148)]
    for fill, st, label, y in leg:
        parts.append(rect(230, y, 16, 16, fill=fill, stroke=st, sw=1.5, rx=3))
        parts.append(text(254, y + 12, label, size=11, color=INK, anchor="start"))
    box, _, _ = textbox(320, 378,
                        "у бюджет часу життя підставляють Q_eff — а не цифру з наклейки",
                        size=11, fill="#f0fdf4", stroke=FIELD)
    parts.append(box)
    render("img/effective-capacity.svg", W, H, *parts,
           title="Від паспортної ємності до реально доступної")


# ── Фігура (математика 2): чому вирішує середній струм, а не сон ─────────────
def fig_duty_current():
    W, H = 720, 400
    parts = []
    decades = [("1 мкА", 0), ("10 мкА", 1), ("100 мкА", 2),
               ("1 мА", 3), ("10 мА", 4), ("100 мА", 5)]
    y_of = _log_axis(parts, 80, 50, 300, 640, decades)
    y_sleep = y_of(1.08)        # ≈ 12 мкА
    y_peak = y_of(5.11)         # ≈ 130 мА
    y_avg = y_of(2.74)          # ≈ 554 мкА
    xs = [80, 279.7, 323.5, 523.1, 567.0, 640]
    parts.append(line(xs[0], y_sleep, xs[1], y_sleep, color=SLP, sw=2.5))
    parts.append(line(xs[1], y_sleep, xs[1], y_peak, color=ACT, sw=2.0))
    parts.append(line(xs[1], y_peak, xs[2], y_peak, color=ACT, sw=3.0))
    parts.append(line(xs[2], y_peak, xs[2], y_sleep, color=ACT, sw=2.0))
    parts.append(line(xs[2], y_sleep, xs[3], y_sleep, color=SLP, sw=2.5))
    parts.append(line(xs[3], y_sleep, xs[3], y_peak, color=ACT, sw=2.0))
    parts.append(line(xs[3], y_peak, xs[4], y_peak, color=ACT, sw=3.0))
    parts.append(line(xs[4], y_peak, xs[4], y_sleep, color=ACT, sw=2.0))
    parts.append(line(xs[4], y_sleep, xs[5], y_sleep, color=SLP, sw=2.5))
    parts.append(line(80, y_avg, 640, y_avg, color=FIELD, sw=2.0, dash="8,5"))
    parts.append(text(644, y_avg + 4, "I_avg", size=11, color=FIELD, anchor="start", bold=True))
    parts.append(text(644, y_avg + 17, "≈ 554 мкА", size=10, color=FIELD, anchor="start"))
    parts.append(text(110, y_sleep - 9, "сон ≈ 12 мкА", size=11, color=SLP, anchor="start", bold=True))
    parts.append(text(301.6, y_peak - 11, "130 мА", size=11, color=ACT, bold=True))
    parts.append(text(301.6, y_peak - 24, "0.25 с", size=10, color=ACT))
    parts.append(text(360, 322, "час (2 цикли по 60 с; активний сплеск збільшено для наочності)",
                      size=10, color=MUTED))
    parts.append(text(16, 175, "струм (лог. шкала)", size=11, color=MUTED, anchor="middle"))
    parts[-1] = parts[-1].replace("<text ", '<text transform="rotate(-90,16,175)" ')
    box, _, _ = textbox(259.9, 245, "542 з 554 мкА дає\nсам сплеск передачі",
                        size=10, fill="#f0fdf4", stroke=FIELD)
    parts.append(box)
    box, _, _ = textbox(360, 378,
                        "перший важіль економії — рідші й коротші виходи в радіо, а не глибший сон",
                        size=11, fill="#f0fdf4", stroke=FIELD)
    parts.append(box)
    render("img/duty-current.svg", W, H, *parts,
           title="Чому вирішує середній струм, а не сон")


# ── Фігура (історія 1): дві лінії до імпланта, одна стіна — батарея ──────────
def fig_pacemaker_two_lines():
    W, H = 860, 430
    parts = []
    y_eu, y_us, y_ax = 130, 280, 382

    def t_x(year):  # 1932..1972 → 60..780
        return 60 + (year - 1932) / (1972 - 1932) * (780 - 60)

    parts.append(line(60, y_eu, 780, y_eu, color=SLP, sw=2.5, dash="8,4"))
    parts.append(line(60, y_us, 780, y_us, color=ACT, sw=2.5, dash="8,4"))
    parts.append(line(60, y_ax, 810, y_ax, color=MUTED, sw=1.5))
    parts[-1] = parts[-1].replace("/>", ' marker-end="url(#arrow)"/>')
    for yr in (1932, 1950, 1956, 1958, 1960, 1968, 1972):
        x = t_x(yr)
        parts.append(line(x, y_ax - 5, x, y_ax + 5, color=MUTED, sw=1.0))
        parts.append(text(x, y_ax + 18, str(yr), size=10, color=MUTED))

    b, _, _ = textbox(58, 130, "Європа\n(Швеція)", size=11, fill="#dbeafe",
                      stroke=SLP, color=SLP, bold=True)
    parts.append(b)
    b, _, _ = textbox(58, 280, "США\n(Буффало)", size=11, fill="#fdecea",
                      stroke=ACT, color=ACT, bold=True)
    parts.append(b)

    def node(x, y, col, lines, ny, big=False):
        r = 8 if big else 5
        parts.append(circle(x, y, r, fill="#fff" if big else col, stroke=col, sw=2.5 if big else 1.5))
        b, _, _ = textbox(x, ny, "\n".join(lines), size=9, fill="#dbeafe" if col == SLP else "#fdecea",
                          stroke=col, color=col)
        parts.append(b)

    # Європа
    node(t_x(1932), y_eu, SLP, ["Hyman 1932", "«pacemaker»", "(термін)"], 70)
    node(t_x(1957), y_eu, SLP, ["Баккен 1957", "носимий", "(транзистор, батарея)"], 80)
    node(t_x(1958), y_eu, SLP, ["Елмквіст+Сеннінг", "8.10.1958", "перший ІМПЛАНТ", "(~3 год → заміни)"], 175, big=True)
    # США
    node(t_x(1956), y_us, ACT, ["Ґрейтбатч 1956", "«не той резистор»", "генератор імпульсів"], 330)
    node(t_x(1958), y_us, ACT, ["1958", "собака"], 235)
    node(t_x(1960), y_us, ACT, ["Чардак+Ґейдж 1960", "перший", "довготривалий", "(Medtronic)"], 225, big=True)

    # арка батареї
    parts.append(line(535, y_eu, 726.7, 205, color=FIELD, sw=2.0))
    parts.append(line(576.7, y_us, 726.7, 205, color=FIELD, sw=2.0))
    parts.append(rect(712.7, 185, 28, 40, fill="#d1fae5", stroke=FIELD, sw=2.5, rx=4))
    parts.append(rect(720.7, 180, 12, 7, fill="#d1fae5", stroke=FIELD, sw=1.5, rx=2))
    b, _, _ = textbox(728.7, 262, "1968–1972\nлітій-йодна комірка\nртуть ~2 роки → Li ~10 років\n(Catalyst Research Corp)",
                      size=9, fill="#d1fae5", stroke=FIELD, color=FIELD, bold=True)
    parts.append(b)

    box, _, _ = textbox(430, 410,
                        "два «перші»: Швеція 1958 — перший імплант; США 1960 — перший довготривалий. Переміг той, хто здолав батарею.",
                        size=10, fill="#f0fdf4", stroke=FIELD)
    parts.append(box)

    render("img/pacemaker-two-lines.svg", W, H, *parts,
           title="Дві незалежні лінії — одна стіна: батарея")


# ── Фігура (історія 2): роки життя = ємність ÷ струм, два важелі ─────────────
def fig_pacemaker_battery():
    W, H = 720, 410
    parts = []
    b, _, _ = textbox(360, 165, "роки ≈ ємність (мА·год)\n──────────────────────\nсередній струм (мкА)",
                      size=14, fill="#f8f8f8", stroke=INK, color=INK, bold=True)
    parts.append(b)
    parts.append(line(360, 130, 360, 70, color=FIELD, sw=2.5))
    parts[-1] = parts[-1].replace("/>", ' marker-end="url(#arrow)"/>')
    b, _, _ = textbox(360, 50, "краща хімія:\nртуть → літій-йод\n(герметичність, малий саморозряд)",
                      size=11, fill="#d1fae5", stroke=FIELD, color=FIELD)
    parts.append(b)
    parts.append(line(360, 200, 360, 260, color=SLP, sw=2.5))
    parts[-1] = parts[-1].replace("/>", ' marker-end="url(#arrow)"/>')
    b, _, _ = textbox(360, 290, "ощадніша схема:\nКМОН, майже завжди мовчить,\nзрідка б'є — режим сну й скважність",
                      size=11, fill="#dbeafe", stroke=SLP, color=SLP)
    parts.append(b)
    # стовпчики ресурсу
    parts.append(rect(84, 200, 52, 20, fill="#e5e7eb", stroke=MUTED, sw=2.0, rx=4))
    parts.append(text(110, 190, "~2 р.", size=11, color=MUTED, bold=True))
    parts.append(text(110, 236, "ртуть", size=10, color=MUTED))
    parts.append(rect(174, 120, 52, 100, fill="#d1fae5", stroke=FIELD, sw=2.0, rx=4))
    parts.append(text(200, 110, "~10 р.", size=11, color=FIELD, bold=True))
    parts.append(text(200, 236, "літій-йод", size=10, color=FIELD))
    parts.append(text(155, 252, "ресурс батареї", size=10, color=MUTED))
    box, _, _ = textbox(360, 388,
                        "перемогу 1970-х дала ПАРА: більший чисельник × менший знаменник",
                        size=11, fill="#f0fdf4", stroke=FIELD)
    parts.append(box)
    render("img/pacemaker-battery.svg", W, H, *parts,
           title="Роки життя = ємність ÷ струм: два важелі кардіостимулятора")


if __name__ == "__main__":
    fig_budget_formula()
    fig_pulse_vs_average()
    fig_effective_capacity()
    fig_duty_current()
    fig_pacemaker_two_lines()
    fig_pacemaker_battery()
    print("OK: budget-formula, pulse-vs-average, effective-capacity, "
          "duty-current, pacemaker-two-lines, pacemaker-battery")
