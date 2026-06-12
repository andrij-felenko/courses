# -*- coding: utf-8 -*-
"""
Фігури для вставки 4.8.2m — «Шум квантування: ±½ LSB і звідки SNR = 6.02·N + 1.76 дБ».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

fig-26-2-m-1-error-distribution.svg
  Ліворуч: рівномірний розподіл помилки [−½ LSB, +½ LSB] з позначеними
  ±½q (пунктир) і σ = q/√12 ≈ 0.29·q (вужча пара ліній всередині).
  Праворуч: три стовпчики для ESP32 — ½ LSB ≈ 0.40 мВ, σ ≈ 0.23 мВ, q ≈ 0.806 мВ.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.2m.1 — розподіл помилки квантування: пік ½q і діюче σ = q/√12
# ═══════════════════════════════════════════════════════════════════════════════
def fig_error_distribution():
    W, H = 760, 380

    frags = []

    # ─────────────────────────────────────────────────────────────────
    # ЛІВА ПАНЕЛЬ: рівномірний розподіл p(e)
    # ─────────────────────────────────────────────────────────────────
    # Область: x від 60..380, y від 40..320
    LX, RX = 70, 370
    TY, BY = 55, 310
    GW = RX - LX   # 300
    GH = BY - TY   # 255

    # Нормована висота «полиці» = 1/q  (показуємо умовно, висота 1.0 = GH·0.72)
    shelf_h = GH * 0.72
    shelf_y = BY - shelf_h

    # Центр по e = 0
    ex0 = (LX + RX) / 2   # 220

    # Значення ±½q по x
    q_px = GW * 0.80       # ширина між ±½q у пікселях
    xL = ex0 - q_px / 2   # −½q
    xR = ex0 + q_px / 2   # +½q

    # σ = q/√12 ≈ 0.289q → ширина ±σ = 0.289·q_px
    sigma_px = q_px / math.sqrt(12) * 2   # відстань між −σ і +σ
    xsL = ex0 - sigma_px / 2
    xsR = ex0 + sigma_px / 2

    # ── Фон панелі ──
    frags.append(rect(LX - 8, TY - 10, GW + 16, GH + 20,
                      fill="#f8f9fb", stroke=MUTED, sw=1.0, rx=8))

    # ── Вісь Y (щільність) ──
    frags.append(arrow(ex0 - q_px / 2 - 30, BY + 5,
                       ex0 - q_px / 2 - 30, TY - 12, color=INK, sw=1.6))
    frags.append(text(ex0 - q_px / 2 - 30, TY - 20,
                      "p(e)", size=12, color=INK, anchor="middle"))

    # ── Вісь e (горизонталь) ──
    frags.append(arrow(LX - 15, BY, RX + 15, BY, color=INK, sw=1.6))
    frags.append(text(RX + 22, BY + 4, "e", size=13, color=INK,
                      anchor="middle", italic=True))

    # ── Позначка 0 на вісі e ──
    frags.append(line(ex0, BY - 4, ex0, BY + 4, color=INK, sw=1.2))
    frags.append(text(ex0, BY + 16, "0", size=11, color=INK, anchor="middle"))

    # ── Рівномірна «полиця» ──
    # Горизонтальна верхня лінія
    frags.append(line(xL, shelf_y, xR, shelf_y, color=NEG, sw=2.6))
    # Ліва вертикаль полиці
    frags.append(line(xL, BY, xL, shelf_y, color=NEG, sw=2.0))
    # Права вертикаль полиці
    frags.append(line(xR, BY, xR, shelf_y, color=NEG, sw=2.0))
    # Заливка під полицею
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                 'fill="#dde8fb" fill-opacity="0.55" rx="0"/>'
                 % (xL, shelf_y, q_px, shelf_h))

    # Підпис 1/q на полиці
    tb_1q, _, _ = textbox(ex0, shelf_y - 14, "1/q", size=11,
                           fill="#eef2fc", stroke=NEG, sw=1.0, pad=5)
    frags.append(tb_1q)

    # ── Пунктирні межі ±½q ──
    for xv, label, anchor in [(xL, "−½q", "end"), (xR, "+½q", "start")]:
        frags.append(line(xv, TY, xv, BY, color=MUTED, sw=1.2, dash="5 3"))
        dx = -6 if anchor == "end" else 6
        frags.append(text(xv + dx, TY + 14, label, size=11,
                          color=MUTED, anchor=anchor))

    # ── Лінії ±σ (вужча пара, темно-зелена) ──
    sigma_color = FIELD   # "#27ae60"
    for xv, label, anchor in [(xsL, "−σ", "end"), (xsR, "+σ", "start")]:
        frags.append(line(xv, BY, xv, shelf_y + 8, color=sigma_color, sw=2.2))
        dx = -5 if anchor == "end" else 5
        frags.append(text(xv + dx, BY + 16, label, size=10,
                          color=sigma_color, anchor=anchor))

    # Двостороння стрілка ±σ
    frags.append(line(xsL + 2, BY - 18, xsR - 2, BY - 18,
                      color=sigma_color, sw=1.4))
    frags.append(line(xsL + 2, BY - 22, xsL + 2, BY - 14,
                      color=sigma_color, sw=1.4))
    frags.append(line(xsR - 2, BY - 22, xsR - 2, BY - 14,
                      color=sigma_color, sw=1.4))

    # Підпис σ = q/√12 у рамці
    tb_sigma, _, _ = textbox(ex0, BY - 36,
                              "σ = q/√12 ≈ 0.29·q",
                              size=11, fill="#edf7ef", stroke=sigma_color, sw=1.2, pad=6)
    frags.append(tb_sigma)

    # Позначки ±½q на вісі x
    for xv, label in [(xL, "−½q"), (xR, "+½q")]:
        frags.append(line(xv, BY - 4, xv, BY + 4, color=MUTED, sw=1.2))
        frags.append(text(xv, BY + 26, label, size=9, color=MUTED, anchor="middle"))

    # ── Підпис лівої панелі ──
    tb_title, _, _ = textbox(ex0, TY - 2,
                              "Розподіл помилки квантування",
                              size=12, fill=BG, stroke=INK, sw=0.8, pad=6, bold=True)
    frags.append(tb_title)

    # Підпис «рівномірний (uniform)» під «полицею»
    frags.append(text(ex0, shelf_y + shelf_h / 2 + 4,
                      "рівномірний (uniform)", size=10, color=NEG, anchor="middle", italic=True))

    # ─────────────────────────────────────────────────────────────────
    # ПРАВА ПАНЕЛЬ: три стовпчики для ESP32 12 біт
    # ─────────────────────────────────────────────────────────────────
    # q = 3.3/4095 ≈ 0.806 мВ; ½q ≈ 0.403 мВ; σ ≈ 0.233 мВ
    BX = 420   # ліво правої панелі
    EX = W - 30
    PW = EX - BX
    PH = GH
    PTY = TY
    PBY = BY

    # Фон
    frags.append(rect(BX - 8, PTY - 10, PW + 16, PH + 20,
                      fill="#f8f9fb", stroke=MUTED, sw=1.0, rx=8))

    # Дані для ESP32 (відносно q=1.0)
    q_val    = 0.806   # мВ
    half_q   = 0.403   # мВ
    sigma_v  = q_val / math.sqrt(12)   # ≈ 0.233 мВ

    bars = [
        (half_q,  "½ LSB\n(пік)",    "≈ 0.40 мВ", POS,  "#fdecea"),
        (sigma_v, "σ = q/√12\n(RMS)", "≈ 0.23 мВ", FIELD, "#edf7ef"),
        (q_val,   "q = LSB\n(крок)", "≈ 0.81 мВ", NEG,  "#dde8fb"),
    ]

    max_val = q_val
    n_bars  = len(bars)
    bar_w   = 58
    gap     = (PW - n_bars * bar_w) / (n_bars + 1)
    max_bar_h = PH * 0.70

    # Вісь Y (значення мВ)
    ax_x = BX + 6
    frags.append(arrow(ax_x, PBY + 5, ax_x, PTY - 8, color=INK, sw=1.4))
    frags.append(text(ax_x, PTY - 18, "мВ", size=11, color=INK, anchor="middle"))

    # Горизонтальні лінії сітки (0, 0.4, 0.8)
    for tick_v, tick_label in [(0, "0"), (0.4, "0.4"), (0.8, "0.8")]:
        ty_grid = PBY - (tick_v / max_val) * max_bar_h
        frags.append(line(ax_x - 3, ty_grid, EX, ty_grid,
                          color=MUTED, sw=0.7, dash="3 3"))
        frags.append(text(ax_x - 6, ty_grid + 4, tick_label, size=9,
                          color=MUTED, anchor="end"))

    for i, (val, top_label, num_label, color, fill_c) in enumerate(bars):
        bx = BX + gap + i * (bar_w + gap)
        bh = (val / max_val) * max_bar_h
        by_top = PBY - bh

        # Стовпчик
        frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                     'rx="4" fill="%s" stroke="%s" stroke-width="1.8"/>'
                     % (bx, by_top, bar_w, bh, fill_c, color))

        # Числовий підпис над стовпчиком
        tb_num, _, _ = textbox(bx + bar_w / 2, by_top - 16,
                               num_label, size=10,
                               fill=fill_c, stroke=color, sw=1.0, pad=4)
        frags.append(tb_num)

        # Підпис під стовпчиком (назва)
        lines_label = top_label.split("\n")
        for li, ll in enumerate(lines_label):
            frags.append(text(bx + bar_w / 2,
                              PBY + 18 + li * 14,
                              ll, size=10, color=color, anchor="middle"))

    # ── Підпис правої панелі ──
    tb_r, _, _ = textbox((BX + EX) / 2, PTY - 2,
                          "ESP32: q ≈ 0.806 мВ (12 біт, 3.3 В)",
                          size=12, fill=BG, stroke=INK, sw=0.8, pad=6, bold=True)
    frags.append(tb_r)

    # Підпис-порівняння під панеллю
    frags.append(text((BX + EX) / 2, PBY + 52,
                      "σ ≈ 0.58 · ½q — діюче значення вдвічі менше за пік",
                      size=10, color=MUTED, anchor="middle"))

    # ── Підпис рисунка ──
    frags.append(text(W // 2, H - 12,
                      "Рис. 4.8.2m.1. Ліворуч: рівномірний розподіл помилки квантування — «полиця» 1/q над e; "
                      "±½q — пунктиром, σ = q/√12 — вужчою зеленою парою. "
                      "Праворуч: для ESP32 12 біт, пік ½q ≈ 0.40 мВ >> діюче σ ≈ 0.23 мВ.",
                      size=9, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "fig-26-2-m-1-error-distribution.svg"), W, H, *frags,
           title=None)
    print("fig-26-2-m-1-error-distribution.svg — OK")


if __name__ == "__main__":
    fig_error_distribution()
