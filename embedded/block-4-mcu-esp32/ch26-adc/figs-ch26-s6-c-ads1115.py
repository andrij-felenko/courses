# -*- coding: utf-8 -*-
"""
Фігури для вставки 🔌 «Зовнішній АЦП ADS1115-класу: 16 біт, PGA, диференційні входи»
Тема §4.8.6, файл ch26-s6-c-ads1115.md

Рис. 4.8.6c.1 — внутрішній тракт сигналу (block diagram)
Рис. 4.8.6c.2 — підключення до ESP32, несиметричний vs диференційний режим

Запуск: python figs-ch26-s6-c-ads1115.py
Вивід:  ./img/fig-26-8c-1-block-diagram.svg
        ./img/fig-26-8c-2-wiring-modes.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.8.6c.1 — Внутрішній тракт сигналу ADS1115
# ─────────────────────────────────────────────────────────────────────────────
def fig1_block_diagram():
    W, H = 900, 360

    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Усередині ADS1115-класу: тракт сигналу", 16, INK, "middle", bold=True))
    frags.append(text(W / 2, 47, "MUX бере пару входів → PGA підсилює → дельта-сигма ядро дає 16-бітний код → I²C віддає МК", 10, MUTED, "middle"))

    # ── Блоки тракту (зліва направо) ──────────────────────────────────────
    # Входи A0–A3
    bx_in = 42
    frags.append(textbox(bx_in, 150, "A0\nA1\nA2\nA3", size=13, pad=10, fill="#eaf4fd", stroke=NEG, bold=True)[0])
    frags.append(text(bx_in, 222, "4 аналогових\nвходи", size=9, color=MUTED, anchor="middle"))

    # MUX
    bx_mux = 185
    tb, tw, th = textbox(bx_mux, 150, "Вхідний\nMUX", size=13, pad=12, fill=FILL, stroke=LINE)
    frags.append(tb)
    frags.append(text(bx_mux, 150 + th / 2 + 14, "вибирає пару\nвходів", size=9, color=MUTED, anchor="middle"))

    # PGA
    bx_pga = 345
    tb2, tw2, th2 = textbox(bx_pga, 150, "PGA\n×1…×16", size=13, pad=12, fill="#fff3e0", stroke="#e67e22")
    frags.append(tb2)
    frags.append(text(bx_pga, 150 + th2 / 2 + 14, "програмоване\nпідсилення", size=9, color=MUTED, anchor="middle"))

    # Дельта-сигма
    bx_ds = 530
    tb3, tw3, th3 = textbox(bx_ds, 150, "ΔΣ модулятор\n+ цифр. фільтр", size=12, pad=12, fill="#eef6ef", stroke=FIELD)
    frags.append(tb3)
    frags.append(text(bx_ds, 150 + th3 / 2 + 14, "16-бітний код\n(повільно, точно)", size=9, color=MUTED, anchor="middle"))

    # Регістри + I²C
    bx_i2c = 730
    tb4, tw4, th4 = textbox(bx_i2c, 150, "Регістри\n+ I²C логіка", size=13, pad=12, fill="#f4eafb", stroke=MUTED)
    frags.append(tb4)
    frags.append(text(bx_i2c, 150 + th4 / 2 + 14, "SDA / SCL / ADDR", size=9, color=MUTED, anchor="middle"))

    # Стрілки тракту
    for x1, x2 in [(bx_in + 32, bx_mux - 42), (bx_mux + 42, bx_pga - 42),
                   (bx_pga + 42, bx_ds - 56), (bx_ds + 56, bx_i2c - 46)]:
        frags.append(arrow(x1, 150, x2, 150))

    # Стрілка виходу I²C → МК
    frags.append(arrow(bx_i2c + 46, 150, bx_i2c + 90, 150))
    frags.append(text(bx_i2c + 96, 154, "→ МК", size=12, color=INK))

    # ── Допоміжні відгалуження ──────────────────────────────────────────────
    # Внутрішній Vref (знизу від PGA)
    vref_y = 248
    frags.append(line(bx_pga, 150 + th2 / 2, bx_pga, vref_y - 5))
    tb_vref, _, _ = textbox(bx_pga, vref_y + 20, "Внутрішній\nVref (точний)", size=10, pad=8,
                             fill="#fffde7", stroke=GOLD if False else "#b7950b")
    frags.append(tb_vref)
    frags.append(text(bx_pga, vref_y + 54, "не залежить від VDD", size=9, color=MUTED, anchor="middle"))

    # ALERT/RDY (зверху від блоку регістрів)
    alert_y = 60
    frags.append(line(bx_i2c, 150 - th4 / 2, bx_i2c, alert_y + 8))
    tb_alert, _, _ = textbox(bx_i2c, alert_y - 4, "ALERT/RDY", size=11, pad=8,
                              fill="#fdecea", stroke=POS)
    frags.append(tb_alert)
    frags.append(text(bx_i2c, alert_y + 20, "переривання / готовність", size=9, color=MUTED, anchor="middle"))

    # Живлення (зверху зліва)
    tb_pwr, _, _ = textbox(85, 60, "VDD / GND\n2.0–5.5 В", size=11, pad=8, fill=FILL, stroke=LINE)
    frags.append(tb_pwr)

    # ── Нижня примітка ──────────────────────────────────────────────────────
    frags.append(rect(60, 310, W - 120, 36, fill="#f0f4ff", stroke=MUTED, sw=1.0, rx=6))
    frags.append(text(W / 2, 332, "На відміну від SAR §4.8.8: вимір диференційний (MUX бере пару), "
                      "підсилення — ДО квантування, опорна — внутрішня й точна.", size=9.5, color=INK, anchor="middle"))

    render(os.path.join(OUT, "fig-26-8c-1-block-diagram.svg"), W, H, *frags,
           title=None)
    print("wrote fig-26-8c-1-block-diagram.svg")


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.8.6c.2 — Підключення до ESP32, несиметричний vs диференційний режим
# ─────────────────────────────────────────────────────────────────────────────
def fig2_wiring_modes():
    W, H = 900, 400

    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Підключення по I²C і два режими входу", 16, INK, "middle", bold=True))
    frags.append(text(W / 2, 47, "несиметричний (сигнал відносно GND) і диференційний (різниця двох точок — давить синфазний шум)", 10, MUTED, "middle"))

    # ── Ліва частина: ESP32 і ADS1115 ──────────────────────────────────────
    # ESP32 блок
    esp_x, esp_y = 110, 150
    tb_esp, tw_esp, th_esp = textbox(esp_x, esp_y, "ESP32\nМК", size=14, pad=14, fill="#eaf4fd", stroke=NEG, bold=True)
    frags.append(tb_esp)

    # ADS1115 блок
    ads_x, ads_y = 310, 150
    tb_ads, tw_ads, th_ads = textbox(ads_x, ads_y, "ADS1115\nАЦП", size=14, pad=14, fill="#fff3e0", stroke="#e67e22", bold=True)
    frags.append(tb_ads)

    # I²C шина (SDA + SCL) — горизонтальна лінія з підтяжками
    bus_y = 130
    x_left = esp_x + tw_esp / 2
    x_right = ads_x - tw_ads / 2
    frags.append(line(x_left, bus_y, x_right, bus_y, MUTED, sw=1.5, dash="4,3"))
    frags.append(text((x_left + x_right) / 2, bus_y - 10, "SDA / SCL (спільна I²C шина, підтяжки 4.7 кОм)", size=9, color=INK, anchor="middle"))

    frags.append(arrow(esp_x + tw_esp / 2, esp_y - 5, esp_x + tw_esp / 2, bus_y + 3, MUTED, sw=1.2))
    frags.append(arrow(ads_x - tw_ads / 2, bus_y + 3, ads_x - tw_ads / 2, ads_y - 5, MUTED, sw=1.2))

    # VDD/GND
    frags.append(line(esp_x, esp_y + th_esp / 2 + 5, esp_x, esp_y + th_esp / 2 + 20, LINE, sw=1.5))
    frags.append(line(ads_x, ads_y + th_ads / 2 + 5, ads_x, ads_y + th_ads / 2 + 20, LINE, sw=1.5))
    frags.append(line(esp_x, esp_y + th_esp / 2 + 20, ads_x, ads_y + th_ads / 2 + 20, LINE, sw=1.5))
    frags.append(text((esp_x + ads_x) / 2, esp_y + th_esp / 2 + 35, "VDD / GND (2.0–5.5 В)", size=9, color=MUTED, anchor="middle"))

    # ADDR → GND (адреса 0x48)
    frags.append(text(ads_x, ads_y + th_ads / 2 + 56, "ADDR → GND → адреса 0x48", size=9, color="#27ae60", anchor="middle"))

    # ALERT/RDY → GPIO переривання
    alert_y2 = esp_y - 44
    frags.append(line(ads_x - 10, ads_y - th_ads / 2 - 5, ads_x - 10, alert_y2 + 5, POS, sw=1.3))
    frags.append(line(ads_x - 10, alert_y2 + 5, esp_x + 10, alert_y2 + 5, POS, sw=1.3))
    frags.append(line(esp_x + 10, alert_y2 + 5, esp_x + 10, esp_y - th_esp / 2 - 5, POS, sw=1.3))
    frags.append(text((esp_x + ads_x) / 2, alert_y2 - 6, "ALERT/RDY → GPIO переривання МК", size=9, color=POS, anchor="middle"))

    # ── Права частина: два режими входів ────────────────────────────────────
    # Заголовок правої частини
    right_x = 540
    frags.append(text(right_x + 145, 80, "Два режими входу:", size=12, color=INK, anchor="middle", bold=True))

    # Рамка «(а) несиметричний»
    frags.append(rect(right_x, 96, 290, 120, fill="#f0f8ff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(right_x + 145, 114, "(а) Несиметричний", size=11, color=NEG, anchor="middle", bold=True))
    frags.append(text(right_x + 145, 132, "сигнал на A0, GND — земля", size=10, color=INK, anchor="middle"))
    # Схема: давач → A0 і GND
    tb_src_a, _, _ = textbox(right_x + 55, 176, "Давач\n(напруга)", size=10, pad=7, fill=FILL, stroke=LINE)
    frags.append(tb_src_a)
    frags.append(arrow(right_x + 93, 164, right_x + 150, 164, INK, sw=1.5))
    frags.append(text(right_x + 162, 161, "A0", size=11, color=NEG, bold=True))
    frags.append(text(right_x + 55, 196, "GND", size=10, color=MUTED, anchor="middle"))
    frags.append(text(right_x + 145, 208, "як вбудований АЦП (§4.8.1)", size=9, color=MUTED, anchor="middle"))

    # Рамка «(б) диференційний»
    frags.append(rect(right_x, 228, 290, 140, fill="#eef6ef", stroke=FIELD, sw=2.0, rx=8))
    frags.append(text(right_x + 145, 246, "(б) Диференційний", size=11, color=FIELD, anchor="middle", bold=True))
    frags.append(text(right_x + 145, 263, "тензоміст / шунт між A0–A1", size=10, color=INK, anchor="middle"))
    # Схема: міст → A0, A1
    tb_bridge, _, _ = textbox(right_x + 55, 300, "Міст /\nшунт", size=10, pad=7, fill="#eef6ef", stroke=FIELD)
    frags.append(tb_bridge)
    frags.append(arrow(right_x + 93, 292, right_x + 148, 285, FIELD, sw=1.5))
    frags.append(arrow(right_x + 93, 308, right_x + 148, 315, FIELD, sw=1.5))
    frags.append(text(right_x + 162, 282, "A0 (+)", size=11, color=POS, bold=True))
    frags.append(text(right_x + 162, 319, "A1 (−)", size=11, color=NEG, bold=True))
    frags.append(text(right_x + 145, 354, "РІЗНИЦЯ A0−A1, давить синфазний шум (r09)", size=9, color=FIELD, anchor="middle"))

    # ── Нижня примітка ──────────────────────────────────────────────────────
    frags.append(rect(30, 358, W - 60, 32, fill="#fdecea", stroke=POS, sw=1.0, rx=6))
    frags.append(text(W / 2, 377, "Засторога: вхід ≤ VDD; PGA ×16 (FSR ±0.256 В) — вужча лінійка за живлення; "
                      "перевищиш — код насититься (§4.8.3).", size=9, color=POS, anchor="middle"))

    render(os.path.join(OUT, "fig-26-8c-2-wiring-modes.svg"), W, H, *frags,
           title=None)
    print("wrote fig-26-8c-2-wiring-modes.svg")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig1_block_diagram()
    fig2_wiring_modes()
