# -*- coding: utf-8 -*-
"""
Фігури до математичної вставки «Семпл-холд зблизька: charge injection і перетікання між каналами»
(ch26-s7-m-sample-hold.md).

Дві фігури:
  fig-26-7m-1-charge-injection.svg  — механізм і формула charge injection
  fig-26-7m-2-crosstalk-settle.svg  — закон згасання crosstalk, правило «перший відлік — геть»

Залежності: тільки стандартна бібліотека Python + спільний svgkit.
Запуск: python figs-ch26-s7-m-sample-hold.py
Вивід: ./img/
"""

import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


def save_svg(name, w, h, *frags, title=None):
    path = os.path.join(OUT, name)
    render(path, w, h, *frags, title=title)
    print("wrote", name)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.7m.1 — Charge injection: механізм і формула
# ═══════════════════════════════════════════════════════════════════════════════

def fig_charge_injection():
    """
    Ліва панель: схема S/H (ключ + C_H), у мить розмикання
    заряд Q_inj з каналу ключа перетікає на C_H.
    Права панель: часовий графік V(C_H) — стрибок ΔV_inj у мить розмикання.
    Висновок: зсув сталий, обернено пропорційний C_H.
    viewBox ~ 720×300.
    """
    W, H = 720, 310
    frags = []

    # ── ЛІВА ПАНЕЛЬ: схема S/H ──────────────────────────────────────────────

    # Пін → ключ → вузол → C_H → земля; вузол → АЦП (правий край)
    panel_cx = 190   # центр лівої панелі

    # Заголовок лівої панелі
    tb1, _, _ = textbox(panel_cx, 26, "Схема Sample-Hold", size=13, bold=True,
                        fill=FILL, stroke=MUTED)
    frags.append(tb1)

    # Вхідний провід
    frags.append(line(40, 120, 120, 120, color=INK, sw=2.0))
    # Підпис Vin
    frags.append(text(30, 124, "Vin", size=13, color=NEG, anchor="middle", bold=True))

    # Ключ (розімкнений): коло-перемичка ліво, дужка кут, коло-перемичка право
    frags.append(circle(120, 120, 4, fill=INK, stroke=INK, sw=1))
    # провід ключа під кутом (розімкнений)
    frags.append(line(120, 120, 162, 100, color=INK, sw=2.0))
    frags.append(circle(166, 120, 4, fill=INK, stroke=INK, sw=1))
    # Підпис "ключ (key) — розімкнений"
    frags.append(text(143, 89, "ключ OFF", size=11, color=MUTED, anchor="middle"))

    # Провід від правого кола ключа до вузла
    frags.append(line(166, 120, 230, 120, color=INK, sw=2.0))

    # Вузол (junction point)
    frags.append(circle(230, 120, 4, fill=INK, stroke=INK, sw=1))

    # Вертикальний провід донизу → конденсатор C_H
    frags.append(line(230, 120, 230, 155, color=INK, sw=2.0))
    # Конденсатор: дві горизонтальні пластини
    frags.append(line(205, 155, 255, 155, color=INK, sw=3.0))
    frags.append(line(205, 165, 255, 165, color=INK, sw=3.0))
    # Провід до землі
    frags.append(line(230, 165, 230, 190, color=INK, sw=2.0))
    # Земля (три лінії)
    frags.append(line(215, 190, 245, 190, color=INK, sw=2.5))
    frags.append(line(220, 197, 240, 197, color=INK, sw=2.0))
    frags.append(line(225, 203, 235, 203, color=INK, sw=1.5))
    # Підпис C_H
    frags.append(text(265, 162, "C_H", size=13, color=FIELD, anchor="start", bold=True))

    # Провід від вузла до виходу (→ АЦП)
    frags.append(line(230, 120, 310, 120, color=INK, sw=2.0))
    tb_adc, _, _ = textbox(338, 120, "→ АЦП", size=12, fill=FILL, stroke=MUTED)
    frags.append(tb_adc)

    # Стрілка Q_inj: від ключа вниз на C_H (червона — заряд)
    frags.append(arrow(143, 120, 224, 152, color=POS, sw=2.2))
    tb_q, _, _ = textbox(100, 162, "Q_inj", size=12, fill="#fdecea", stroke=POS,
                         color=POS, bold=True)
    frags.append(tb_q)
    frags.append(text(100, 182, "заряд каналу ключа", size=10, color=MUTED, anchor="middle"))

    # Рамка формули
    tb_f, _, _ = textbox(panel_cx, 240,
                         "ΔV = Q_inj / C_H",
                         size=13, bold=True, fill="#fdecea", stroke=POS, color=POS)
    frags.append(tb_f)
    frags.append(text(panel_cx, 271, "більший C_H → менший зсув", size=11,
                      color=MUTED, anchor="middle"))

    # Вертикальний роздільник
    frags.append(line(390, 50, 390, 280, color=MUTED, sw=1.0, dash="4,4"))

    # ── ПРАВА ПАНЕЛЬ: часовий графік V(C_H) ─────────────────────────────────

    panel_rx = 390   # ліво правої панелі
    gox = 430        # початок осі X
    goy = 220        # початок осі Y (низ графіка)
    gw  = 240        # ширина графіка
    gh  = 130        # висота графіка

    # Вісь часу
    frags.append(arrow(gox, goy, gox + gw + 20, goy, color=INK, sw=1.6))
    # Вісь напруги
    frags.append(arrow(gox, goy, gox, goy - gh - 15, color=INK, sw=1.6))

    frags.append(text(gox + gw + 24, goy + 4, "t", size=13, color=INK,
                      anchor="start", italic=True))
    frags.append(text(gox - 12, goy - gh - 18, "V(C_H)", size=11, color=INK, anchor="end"))

    # Момент розмикання
    t_switch_x = gox + 90   # x-координата моменту розмикання

    # Горизонтальна лінія до розмикання (базовий рівень)
    y_base = goy - 55
    frags.append(line(gox, y_base, t_switch_x, y_base, color=NEG, sw=2.4))

    # Вертикальний стрибок угору (ΔV_inj)
    y_shifted = y_base - 46
    frags.append(line(t_switch_x, y_base, t_switch_x, y_shifted, color=POS, sw=2.0))

    # Горизонтальна лінія після стрибку (утриманий рівень)
    frags.append(line(t_switch_x, y_shifted, gox + gw, y_shifted, color=POS, sw=2.4))

    # Підпис моменту розмикання
    frags.append(line(t_switch_x, goy, t_switch_x, goy + 6, color=INK, sw=1.4))
    frags.append(text(t_switch_x, goy + 18, "key OFF", size=11, color=MUTED, anchor="middle"))

    # Дужка-позначення ΔV_inj
    frags.append(line(t_switch_x + 14, y_base, t_switch_x + 14, y_shifted, color=POS, sw=1.6))
    frags.append(line(t_switch_x + 9, y_base, t_switch_x + 19, y_base, color=POS, sw=1.4))
    frags.append(line(t_switch_x + 9, y_shifted, t_switch_x + 19, y_shifted, color=POS, sw=1.4))
    tb_dv, _, _ = textbox(t_switch_x + 50, (y_base + y_shifted) // 2,
                          "ΔV_inj", size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)
    frags.append(tb_dv)

    # Підписи рівнів
    frags.append(text(gox - 8, y_base + 4, "Vin", size=11, color=NEG, anchor="end"))
    frags.append(text(gox - 8, y_shifted + 4, "Vin+ΔV", size=10, color=POS, anchor="end"))

    # Заголовок правої панелі
    tb2, _, _ = textbox(555, 26, "V(C_H): стрибок у мить розмикання", size=12, bold=True,
                        fill=FILL, stroke=MUTED)
    frags.append(tb2)

    # Підсумок внизу
    tb_sum, _, _ = textbox(W // 2, 292,
                           "Зсув СТАЛИЙ — відтворюваний, знімається калібруванням (§4.8.6)",
                           size=11, fill=FILL, stroke=MUTED, color=INK)
    frags.append(tb_sum)

    save_svg("fig-26-7m-1-charge-injection.svg", W, H, *frags)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.7m.2 — Crosstalk: згасання хвоста і правило «перший відлік — геть»
# ═══════════════════════════════════════════════════════════════════════════════

def fig_crosstalk_settle():
    """
    Часовий графік після перемикання каналу A → Б:
    - крива V(C_H): від V_A до V_Б по e^(−t/τ)
    - вертикальні пунктири на t=1τ, 3τ, 7τ з підписами залишку
    - ±½ LSB смужка довкола V_Б
    - перший «холостий» відлік позначений хрестиком (відкидаємо),
      наступні — в зеленій зоні (беремо)
    - підпис формули V_resid = ΔV_крок · e^(−t/τ)
    viewBox ~ 760×340.
    """
    W, H = 760, 340
    frags = []

    # ── Осьова сітка ────────────────────────────────────────────────────────
    gox = 70     # ліво осі
    goy = 255    # низ осі Y
    gw  = 620    # ширина
    gh  = 175    # висота (від V_Б до V_А)

    # Τ у пікселях
    tau_px = gw / 9.0   # вісь показує 0..9τ

    def tx(tau_units):
        return gox + tau_units * tau_px

    # V_A і V_Б у пікселях (від goy вгору)
    y_VA = goy - gh        # верх = старий канал А
    y_VB = goy - 30        # низ = новий канал Б (ціль)

    # Крива e^(−t/τ) від V_A до V_Б
    n_pts = 300
    curve_pts = []
    for i in range(n_pts + 1):
        t_u = 9.0 * i / n_pts   # в одиницях τ
        frac = math.exp(-t_u)   # exp(-t/τ)
        y = y_VB + frac * (y_VA - y_VB)
        curve_pts.append((tx(t_u), y))

    # Малюємо криву (хвіст — червоний до 3τ, потім зелений)
    # Розбиваємо на дві частини: 0..3τ (хвіст) і 3τ..9τ (в нормі)
    split_u = 3.0
    split_i = int(split_u / 9.0 * n_pts)

    pts_tail = curve_pts[:split_i + 1]
    pts_ok   = curve_pts[split_i:]

    # червоний хвіст
    pts_str_t = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts_tail)
    frags.append(f'<polyline points="{pts_str_t}" fill="none" stroke="{POS}" '
                 f'stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>')

    # зелений (у зоні)
    pts_str_ok = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts_ok)
    frags.append(f'<polyline points="{pts_str_ok}" fill="none" stroke="{FIELD}" '
                 f'stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>')

    # ── Осі ─────────────────────────────────────────────────────────────────
    frags.append(arrow(gox, goy, gox + gw + 20, goy, color=INK, sw=1.6))
    frags.append(arrow(gox, goy, gox, y_VA - 15, color=INK, sw=1.6))

    frags.append(text(gox + gw + 24, goy + 4, "t", size=14, color=INK,
                      anchor="start", italic=True))
    frags.append(text(gox - 12, y_VA - 18, "V(C_H)", size=11, color=INK, anchor="end"))

    # Горизонтальні лінії-рівні V_А і V_Б (пунктир)
    frags.append(line(gox, y_VA, gox + gw, y_VA, color=NEG, sw=1.2, dash="5,4"))
    frags.append(line(gox, y_VB, gox + gw, y_VB, color=FIELD, sw=1.2, dash="5,4"))

    frags.append(text(gox - 8, y_VA + 4, "V_A", size=12, color=NEG, anchor="end", bold=True))
    frags.append(text(gox - 8, y_VB + 4, "V_Б", size=12, color=FIELD, anchor="end", bold=True))

    # ── ±½ LSB смужка навколо V_Б ───────────────────────────────────────────
    lsb_half_px = 9   # ½ LSB у пікселях (ілюстративно)
    # Напівпрозора заливка
    frags.append(f'<rect x="{gox}" y="{y_VB - lsb_half_px}" '
                 f'width="{gw}" height="{2 * lsb_half_px}" '
                 f'fill="{FIELD}" fill-opacity="0.18" stroke="none"/>')
    # Межі смужки
    frags.append(line(gox, y_VB - lsb_half_px, gox + gw, y_VB - lsb_half_px,
                      color=FIELD, sw=1.0, dash="3,3"))
    frags.append(line(gox, y_VB + lsb_half_px, gox + gw, y_VB + lsb_half_px,
                      color=FIELD, sw=1.0, dash="3,3"))
    tb_lsb, _, _ = textbox(gox + gw - 40, y_VB - lsb_half_px - 14,
                            "±½ LSB", size=10, fill=FILL, stroke=FIELD, color=FIELD)
    frags.append(tb_lsb)

    # ── Мітки перемикання і відліків ────────────────────────────────────────

    # t=0: момент перемикання
    frags.append(line(gox, goy, gox, goy + 6, color=INK, sw=1.4))
    frags.append(text(gox, goy + 18, "0", size=11, color=INK, anchor="middle"))
    frags.append(text(gox, goy + 30, "перемикання\nА → Б", size=10, color=MUTED, anchor="middle"))

    # Вертикальні пунктири на 1τ, 3τ, 7τ
    tau_marks = [
        (1.0, math.exp(-1.0),   "≈37%"),
        (3.0, math.exp(-3.0),   "≈5%"),
        (7.0, math.exp(-7.0),   "<0.1%"),
    ]

    for tau_u, frac, pct_lbl in tau_marks:
        xm = tx(tau_u)
        y_curve = y_VB + frac * (y_VA - y_VB)
        frags.append(line(xm, goy, xm, y_curve, color=MUTED, sw=1.2, dash="4,4"))
        frags.append(line(xm, goy, xm, goy + 6, color=INK, sw=1.4))
        frags.append(text(xm, goy + 18, f"{tau_u:.0f}τ", size=11, color=MUTED, anchor="middle"))
        # Підпис залишку
        tb_pct, _, _ = textbox(xm + 28, y_curve - 8, pct_lbl, size=10,
                               fill=FILL, stroke=MUTED, color=MUTED)
        frags.append(tb_pct)
        # Крапка на кривій
        frags.append(circle(xm, y_curve, 4, fill=MUTED, stroke=MUTED, sw=1))

    # ── Відліки (холостий і нормальні) ───────────────────────────────────────

    # Перший відлік (холостий) — хрестик на 1τ (ще у хвості)
    x_discard = tx(1.0)
    y_discard  = y_VB + math.exp(-1.0) * (y_VA - y_VB)
    # Хрестик (×)
    d = 9
    frags.append(line(x_discard - d, y_discard - d, x_discard + d, y_discard + d,
                      color=POS, sw=2.4))
    frags.append(line(x_discard - d, y_discard + d, x_discard + d, y_discard - d,
                      color=POS, sw=2.4))
    tb_disc, _, _ = textbox(x_discard, y_discard - 26,
                            "відкидаємо", size=11, fill="#fdecea", stroke=POS, color=POS)
    frags.append(tb_disc)

    # Нормальні відліки — кружки (4τ, 5τ, 6τ)
    for tau_u in [4.0, 5.5, 7.0]:
        xok = tx(tau_u)
        yok = y_VB + math.exp(-tau_u) * (y_VA - y_VB)
        frags.append(circle(xok, yok, 6, fill=FIELD, stroke=FIELD, sw=1))

    tb_ok, _, _ = textbox(tx(5.5), y_VB - 28,
                          "беремо (в зеленій зоні)", size=11,
                          fill="#e8f6ee", stroke=FIELD, color=FIELD)
    frags.append(tb_ok)

    # ── Формула V_resid у рамці ───────────────────────────────────────────────
    tb_form, _, _ = textbox(W // 2, 22,
                            "V_resid = ΔV_крок · e^(−t/τ)    τ = (R_on + R_дж) · C_H",
                            size=13, bold=True, fill=FILL, stroke=INK, color=INK)
    frags.append(tb_form)

    # Підпис вісь часу
    frags.append(text(gox + gw // 2, goy + 44,
                      "перший відлік ловить хвіст → відкидаємо; решта — у зеленій зоні",
                      size=11, color=INK, anchor="middle"))

    save_svg("fig-26-7m-2-crosstalk-settle.svg", W, H, *frags)


# ── Точка входу ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_charge_injection()
    fig_crosstalk_settle()
    print("done.")
