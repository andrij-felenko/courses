# -*- coding: utf-8 -*-
"""
Фігури для компонентної вставки 🔌 Потенціометр (ch26-s1-c-potentiometer.md).
Розділ 26, вставка 1c. Нумерація: Рис. 4.8.1c.1, Рис. 4.8.1c.2.

Запуск:
    python figs-ch26-s1-c-potentiometer.py
Вивід → ./img/fig-26-1c-*.svg
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


def save(name, svg_str):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg_str)
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.8.1c.1 — Подільник із рухомою точкою + лінійний vs логарифмічний taper
# ─────────────────────────────────────────────────────────────────────────────
def fig1c1_divider_taper():
    W, H = 840, 420
    # Збираємо SVG вручну через render()
    frags = []

    # ── ЛІВА ПАНЕЛЬ: схема подільника ────────────────────────────────────────
    # Центр лівої панелі
    LP_CX = 230

    # Вертикальна доріжка резистора
    track_x = LP_CX
    track_top = 70     # Vcc вузол
    track_bot = 350    # GND вузол

    # Три положення повзунка (0%, 50%, 100% — знизу вгору)
    positions = [
        (0,   "0%",  "0 В",   0.00),
        (50,  "50%", "1.65 В", 0.50),
        (100, "100%","3.3 В",  1.00),
    ]

    # --- Резистивна доріжка (прямокутник із заокругленнями) ---
    frags.append(rect(track_x - 14, track_top + 10, 28, track_bot - track_top - 20,
                      fill="#e8e8e8", stroke=INK, sw=2, rx=4))

    # Vcc вузол зверху
    tb1, w1, h1 = textbox(track_x, track_top - 16, "3.3 В (Vcc)", size=12,
                          fill="#fdecea", stroke=POS, sw=2, color=POS, bold=True)
    frags.append(tb1)
    frags.append(line(track_x, track_top - 16 + h1 / 2, track_x, track_top + 10, POS, 2))
    # + маркер на вузлі Vcc
    frags.append(circle(track_x, track_top + 10, 5, POS, POS, 0))

    # GND вузол знизу
    tb2, w2, h2 = textbox(track_x, track_bot + 18, "GND", size=12,
                          fill="#eaf0fd", stroke=NEG, sw=2, color=NEG, bold=True)
    frags.append(tb2)
    frags.append(line(track_x, track_bot - 10, track_x, track_bot + 18 - h2 / 2, NEG, 2))
    frags.append(circle(track_x, track_bot - 10, 5, NEG, NEG, 0))

    # Підпис доріжки
    frags.append(text(track_x - 26, (track_top + track_bot) / 2, "R", size=14,
                      color=INK, anchor="end", bold=True))

    # --- Три положення повзунка ---
    wiper_colors = [NEG, FIELD, POS]
    for i, (pct, pct_str, v_str, frac) in enumerate(positions):
        wy = track_bot - frac * (track_bot - track_top - 20) - 10

        # R_bot і R_top підписи (тільки для 50%)
        if pct == 50:
            frags.append(line(track_x + 26, wy, track_x + 26, track_bot - 10,
                              MUTED, 1.5, dash="4,3"))
            frags.append(text(track_x + 36, (wy + track_bot - 10) / 2 + 5,
                              "R_bot", size=10, color=MUTED, anchor="start"))
            frags.append(line(track_x + 26, track_top + 10, track_x + 26, wy,
                              MUTED, 1.5, dash="4,3"))
            frags.append(text(track_x + 36, (track_top + 10 + wy) / 2 + 5,
                              "R_top", size=10, color=MUTED, anchor="start"))

        # Стрілка-повзунок
        arrow_len = 34
        col = wiper_colors[i]
        # горизонтальна стрілка ліворуч від доріжки
        wx_start = track_x - 14 - arrow_len
        frags.append(line(wx_start, wy, track_x - 14, wy, col, 2.5))
        # трикутна голівка
        pts = f"{track_x - 14},{wy} {wx_start + 10},{wy - 6} {wx_start + 10},{wy + 6}"
        frags.append(f'<polygon points="{pts}" fill="{col}" stroke="{col}" stroke-width="1"/>')

        # Вивід wiper → ADC (горизонтальна лінія праворуч)
        frags.append(line(track_x + 14, wy, track_x + 14 + 40, wy, col, 1.8, dash="5,3"))

        # Підпис положення і напруги
        tb, tw, th = textbox(track_x + 14 + 40 + tw_val(pct_str, v_str),
                             wy, f"{pct_str}  →  {v_str}", size=11,
                             fill="#f4f6f8", stroke=col, sw=1.5, color=col)
        frags.append(tb)
        # Дротик до рамки
        frags.append(line(track_x + 14 + 40, wy,
                          track_x + 14 + 40 + tw_val(pct_str, v_str) - tw / 2 - 2,
                          wy, col, 1.5))

    # Формула ратіометрична
    tb_f, wf, hf = textbox(LP_CX, 390,
                           "Vwiper = Vcc · R_bot / R", size=12,
                           fill="#fff6e0", stroke="#b8860b", sw=1.8, color=INK)
    frags.append(tb_f)

    # Заголовок лівої панелі
    frags.append(text(LP_CX, 30, "Схема подільника", size=14, color=INK,
                      anchor="middle", bold=True))

    # ── ПРАВА ПАНЕЛЬ: графік taper ───────────────────────────────────────────
    RP_X0 = 500    # відступ лівого краю графіка
    RP_W  = 290    # ширина графіка
    RP_Y0 = 340    # низ (Vwiper=0)
    RP_Y1 = 80     # верх (Vwiper=Vcc)
    RP_XR = RP_X0 + RP_W

    # Осі
    frags.append(arrow(RP_X0, RP_Y0, RP_X0, RP_Y1 - 10, INK, 1.8))
    frags.append(arrow(RP_X0, RP_Y0, RP_XR + 14, RP_Y0, INK, 1.8))

    frags.append(text(RP_X0, RP_Y1 - 16, "Vwiper", size=11, color=INK,
                      anchor="middle", bold=True))
    frags.append(text(RP_X0 - 32, RP_Y0 + 4, "0", size=10, color=MUTED, anchor="end"))
    frags.append(text(RP_X0 - 32, RP_Y1 + 4, "Vcc", size=10, color=POS, anchor="end",
                      bold=False))
    frags.append(text(RP_XR + 18, RP_Y0 + 14, "кут →", size=11, color=INK,
                      anchor="start", bold=True))
    frags.append(text(RP_X0 - 2, RP_Y0 + 14, "0%", size=10, color=MUTED, anchor="middle"))
    frags.append(text(RP_XR + 2, RP_Y0 + 14, "100%", size=10, color=MUTED,
                      anchor="middle"))

    # Мітки по осі Y
    for frac, lbl in [(0.5, "Vcc/2"), (1.0, "Vcc")]:
        yy = RP_Y0 + (RP_Y1 - RP_Y0) * frac
        frags.append(line(RP_X0 - 4, yy, RP_X0 + 4, yy, MUTED, 1.2))
        frags.append(text(RP_X0 - 8, yy + 4, lbl, size=9, color=MUTED, anchor="end"))

    # Крива: лінійний taper
    lin_pts = []
    for i in range(101):
        x = RP_X0 + RP_W * i / 100
        y = RP_Y0 + (RP_Y1 - RP_Y0) * i / 100
        lin_pts.append((x, y))
    frags.append(_polyline(lin_pts, FIELD, 2.5))

    # Крива: логарифмічний taper (аудіо A)
    log_pts = []
    for i in range(101):
        t = i / 100
        # типова апроксимація audio-A taper: log-подібна
        if t <= 0:
            v = 0
        else:
            v = t ** 2.5
        x = RP_X0 + RP_W * t
        y = RP_Y0 + (RP_Y1 - RP_Y0) * v
        log_pts.append((x, y))
    frags.append(_polyline(log_pts, POS, 2.5, dash="7,4"))

    # Легенда
    # Лінійний
    leg_x = RP_X0 + 14
    leg_y = RP_Y0 - 70
    frags.append(line(leg_x, leg_y, leg_x + 28, leg_y, FIELD, 2.5))
    frags.append(text(leg_x + 34, leg_y + 4, "лінійний (B) — для виміру кута",
                      size=11, color=FIELD, anchor="start"))
    # Логарифмічний
    frags.append(line(leg_x, leg_y + 20, leg_x + 28, leg_y + 20, POS, 2.5, "7,4"))
    frags.append(text(leg_x + 34, leg_y + 24, "логарифмічний (A) — для гучності",
                      size=11, color=POS, anchor="start"))

    # Заголовок правої панелі
    frags.append(text((RP_X0 + RP_XR) / 2, 30, "Залежність Vwiper від кута (taper)",
                      size=14, color=INK, anchor="middle", bold=True))

    # Розподільник між панелями
    frags.append(line(RP_X0 - 30, 50, RP_X0 - 30, H - 20, MUTED, 1.2, dash="5,4"))

    return render(os.path.join(OUT, "fig-26-1c-1-divider-taper.svg"), W, H, *frags,
                  title="Рис. 4.8.1c.1. Потенціометр = подільник напруги з рухомою точкою")


def tw_val(pct_str, v_str):
    """Оціночна половина ширини textbox для позиціювання."""
    return max(text_width(f"{pct_str}  →  {v_str}", 11) / 2 + 12, 60)


def _polyline(pts, color=INK, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{coords}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{d}/>')


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.8.1c.2 — Практична схема підключення поту до ESP32
# ─────────────────────────────────────────────────────────────────────────────
def fig1c2_wiring():
    W, H = 780, 400
    frags = []

    # ── Потенціометр ─────────────────────────────────────────────────────────
    POT_X = 260     # центр символу поту
    POT_Y = 200     # центр по вертикалі

    track_top = POT_Y - 90
    track_bot = POT_Y + 90
    track_x   = POT_X

    # Резистивна доріжка
    frags.append(rect(track_x - 16, track_top, 32, track_bot - track_top,
                      fill="#e8e8e8", stroke=INK, sw=2.5, rx=5))

    # Підписи ніжок
    # Вивід 1 (верх → Vcc)
    frags.append(line(track_x, track_top, track_x, track_top - 28, POS, 2.5))
    frags.append(circle(track_x, track_top - 28, 5, POS, POS, 0))

    # Вивід 3 (низ → GND)
    frags.append(line(track_x, track_bot, track_x, track_bot + 28, NEG, 2.5))
    frags.append(circle(track_x, track_bot + 28, 5, NEG, NEG, 0))

    # Повзунок (середній, W) — горизонтальна стрілка праворуч від центру
    wiper_y = POT_Y
    arr_len = 42
    pts_w = (f"{track_x + 16},{wiper_y} "
             f"{track_x + 16 + arr_len - 10},{wiper_y - 7} "
             f"{track_x + 16 + arr_len - 10},{wiper_y + 7}")
    frags.append(f'<polygon points="{pts_w}" fill="{FIELD}" stroke="{FIELD}" '
                 f'stroke-width="1.5"/>')
    frags.append(line(track_x + 16 + arr_len - 10, wiper_y,
                      track_x + 16 + arr_len + 90, wiper_y, FIELD, 2.5))

    # Підпис W / wiper
    frags.append(text(track_x - 28, wiper_y + 4, "W", size=13, color=FIELD,
                      anchor="end", bold=True))

    # ── Шина 3.3 В ───────────────────────────────────────────────────────────
    bus_y_vcc = track_top - 28
    frags.append(line(track_x, bus_y_vcc, 80, bus_y_vcc, POS, 2.5))
    tb_vcc, _, _ = textbox(44, bus_y_vcc, "3.3 В", size=13,
                           fill="#fdecea", stroke=POS, sw=2, color=POS, bold=True)
    frags.append(tb_vcc)

    # ── Шина GND ─────────────────────────────────────────────────────────────
    bus_y_gnd = track_bot + 28
    frags.append(line(track_x, bus_y_gnd, 80, bus_y_gnd, NEG, 2.5))
    tb_gnd, _, _ = textbox(44, bus_y_gnd, "GND", size=13,
                           fill="#eaf0fd", stroke=NEG, sw=2, color=NEG, bold=True)
    frags.append(tb_gnd)

    # ── ESP32 ────────────────────────────────────────────────────────────────
    esp_x = 520
    esp_y = 130
    esp_w = 180
    esp_h = 140
    frags.append(rect(esp_x, esp_y, esp_w, esp_h,
                      fill="#f0f4ff", stroke="#1a3a80", sw=2.5, rx=10))
    frags.append(text(esp_x + esp_w / 2, esp_y + 28, "ESP32", size=16,
                      color="#1a3a80", anchor="middle", bold=True))
    frags.append(text(esp_x + esp_w / 2, esp_y + 48, "DevKitC", size=11,
                      color=MUTED, anchor="middle"))

    # ADC-ніжка (ліворуч від блоку ESP32)
    adc_pin_y = esp_y + 80
    frags.append(line(esp_x, adc_pin_y, esp_x - 20, adc_pin_y, FIELD, 2.5))
    frags.append(circle(esp_x - 20, adc_pin_y, 5, FIELD, FIELD, 0))

    # Дріт від wiper до ADC-ніжки
    wiper_end_x = track_x + 16 + arr_len + 90
    frags.append(line(wiper_end_x, wiper_y, esp_x - 20, wiper_y, FIELD, 2.5))
    frags.append(line(esp_x - 20, wiper_y, esp_x - 20, adc_pin_y, FIELD, 2.5))

    # Підпис ADC-ніжки
    tb_adc, _, _ = textbox(esp_x + esp_w / 2, adc_pin_y + 30,
                           "GPIO34 / ADC1\nWi-Fi-safe", size=11,
                           fill="#eeffee", stroke=FIELD, sw=1.8, color=FIELD)
    frags.append(tb_adc)

    # ── Конденсатор (опційно, пунктир) ───────────────────────────────────────
    cap_x = wiper_end_x + 20
    cap_top = wiper_y
    cap_bot = bus_y_gnd
    frags.append(line(cap_x, cap_top, cap_x, cap_top + (cap_bot - cap_top) / 2 - 5,
                      MUTED, 1.5, dash="4,3"))
    # пластини конденсатора
    frags.append(line(cap_x - 10, cap_top + (cap_bot - cap_top) / 2 - 5,
                      cap_x + 10, cap_top + (cap_bot - cap_top) / 2 - 5, MUTED, 2.5))
    frags.append(line(cap_x - 10, cap_top + (cap_bot - cap_top) / 2 + 3,
                      cap_x + 10, cap_top + (cap_bot - cap_top) / 2 + 3, MUTED, 2.5))
    frags.append(line(cap_x, cap_top + (cap_bot - cap_top) / 2 + 3,
                      cap_x, cap_bot, MUTED, 1.5, dash="4,3"))
    frags.append(line(cap_x, cap_bot, track_x, cap_bot, MUTED, 1.5, dash="4,3"))
    # підпис
    tb_cap, _, _ = textbox(cap_x + 50, cap_top + (cap_bot - cap_top) / 2,
                           "100 нФ\n(фільтр шуму)", size=10,
                           fill="#f8f8f8", stroke=MUTED, sw=1.2, color=MUTED)
    frags.append(tb_cap)

    # ── Анотаційна стрілка (поворот → аналогRead) ────────────────────────────
    ann_y = 360
    tb_ann, _, _ = textbox(W / 2, ann_y,
                           "крутиш ручку → Vwiper 0…3.3 В → analogRead → 0…4095",
                           size=12, fill="#fff6e0", stroke="#b8860b", sw=1.8, color=INK)
    frags.append(tb_ann)

    # Заголовок
    frags.append(text(W / 2, 30,
                      "Рис. 4.8.1c.2. Підключення поту до ESP32",
                      size=14, color=INK, anchor="middle", bold=True))
    frags.append(text(W / 2, 50,
                      "кінці на 3.3 В і GND, повзунок (W) → ADC1-ніжка",
                      size=11, color=MUTED, anchor="middle"))

    return render(os.path.join(OUT, "fig-26-1c-2-wiring.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig1c1_divider_taper()
    fig1c2_wiring()
    print("done.")
