# -*- coding: utf-8 -*-
"""
Фігури для вставки r13-s4-c-wake-hw.md
«Залізні будильники: RTC з alarm-виходом, load switch, кнопка-защіпка живлення»

Рис. 4.13.4c.1 — родина зовнішніх помічників сну: де кожен сидить у колі живлення.
Рис. 4.13.4c.2 — схема soft-latch: P-MOSFET, кнопка, HOLD, KEY-READ.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Розширена палітра ────────────────────────────────────────────────────────
ORANGE  = "#e67e22"
LORANGE = "#fdf2e9"
PURPLE  = "#7d3c98"
LPURPLE = "#f5eef8"
TEAL    = "#1a7a73"
LTEAL   = "#e8f8f7"
DGREY   = "#555555"
LGREY   = "#f0f0f0"


# ════════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.4c.1 — Родина зовнішніх помічників сну
# ════════════════════════════════════════════════════════════════════════════════
def fig1_family():
    W, H = 860, 500
    frags = []

    frags.append(text(W // 2, 28, "Три зовнішні помічники сну ESP32", size=17, bold=True))

    # ── Батарея (ліворуч) ────────────────────────────────────────────────────
    bat_cx, bat_cy = 90, 250
    bat_w, bat_h = 100, 180

    # Корпус батарейки
    frags.append(rect(bat_cx - bat_w // 2, bat_cy - bat_h // 2, bat_w, bat_h,
                      fill="#eafaf1", stroke=FIELD, sw=2.5, rx=8))
    frags.append(text(bat_cx, bat_cy - bat_h // 2 - 14, "Батарея", size=13,
                      bold=True, color=FIELD))
    # + і - полюси
    frags.append(plus(bat_cx, bat_cy - 36, r=11))
    frags.append(minus(bat_cx, bat_cy + 36, r=11))

    # Головна шина живлення (горизонтальна)
    bus_y_top = 120
    bus_y_bot = 380
    bus_x0 = bat_cx + bat_w // 2  # від правого краю батарейки
    bus_x1 = 750

    # Плюсова шина (зверху)
    frags.append(line(bus_x0, bus_y_top, bus_x1, bus_y_top,
                      color=POS, sw=2.5))
    frags.append(text(bus_x0 + 20, bus_y_top - 10, "+VCC", size=12,
                      color=POS, bold=True, anchor="start"))

    # Мінусова шина (знизу)
    frags.append(line(bus_x0, bus_y_bot, bus_x1, bus_y_bot,
                      color=NEG, sw=2.5))
    frags.append(text(bus_x0 + 20, bus_y_bot + 18, "GND (спільна)", size=12,
                      color=NEG, bold=True, anchor="start"))

    # Батарея з'єднана з шинами
    frags.append(line(bat_cx, bat_cy - bat_h // 2, bat_cx, bus_y_top,
                      color=POS, sw=2.0))
    frags.append(line(bat_cx + bat_w // 2, bus_y_top, bat_cx, bus_y_top,
                      color=POS, sw=2.0))
    frags.append(line(bat_cx, bat_cy + bat_h // 2, bat_cx, bus_y_bot,
                      color=NEG, sw=2.0))
    frags.append(line(bat_cx + bat_w // 2, bus_y_bot, bat_cx, bus_y_bot,
                      color=NEG, sw=2.0))

    # ── ESP32 (праворуч, основне навантаження) ───────────────────────────────
    esp_x, esp_y, esp_w, esp_h = 620, 185, 160, 130
    frags.append(rect(esp_x, esp_y, esp_w, esp_h,
                      fill="#eaf3fb", stroke=NEG, sw=2.5, rx=10))
    tb, tw, th = textbox(esp_x + esp_w // 2, esp_y + esp_h // 2,
                         "ESP32\n(навантаження)", size=14, bold=True,
                         fill="#eaf3fb", stroke="#eaf3fb", pad=6)
    frags.append(tb)

    # Живлення ESP32 з плюсової шини
    esp_pwr_x = esp_x + esp_w // 2
    frags.append(line(esp_pwr_x, bus_y_top, esp_pwr_x, esp_y,
                      color=POS, sw=2.0))
    # GND ESP32
    frags.append(line(esp_pwr_x, esp_y + esp_h, esp_pwr_x, bus_y_bot,
                      color=NEG, sw=2.0))

    # ── Сходинка 1: RTC (зверху, будить wake-піном) ──────────────────────────
    rtc_cx = 280
    rtc_box, rtc_w, rtc_h = textbox(rtc_cx, 80,
                                     "RTC\n(DS3231/PCF8563)\n~1–2 мкА",
                                     size=12, bold=False,
                                     fill=LORANGE, stroke=ORANGE, sw=2.0,
                                     pad=10)
    frags.append(rtc_box)

    # RTC живиться від шини (тонкою лінією, спільне живлення)
    frags.append(line(rtc_cx, 80 + rtc_h // 2 + 2, rtc_cx, bus_y_top,
                      color=POS, sw=1.5, dash="5,3"))
    frags.append(text(rtc_cx + 8, bus_y_top - 6, "VCC (тонкий)",
                      size=9, color=MUTED, anchor="start"))

    # Стрілка alarm INT → wake-пін ESP32
    wake_x = esp_x
    wake_y = esp_y + 35
    frags.append(arrow(rtc_cx + rtc_w // 2, 80, wake_x, wake_y,
                       color=ORANGE, sw=2.0))
    frags.append(text((rtc_cx + rtc_w // 2 + wake_x) // 2, 60,
                      "INT/alarm → wake GPIO", size=11,
                      color=ORANGE, bold=True))
    frags.append(text((rtc_cx + rtc_w // 2 + wake_x) // 2, 76,
                      "«розбуди о 06:00»", size=10, color=MUTED, italic=True))

    # ── Сходинка 2: Load switch (у плюсовій шині перед «вузлом») ────────────
    # Показуємо load switch між шиною і «давачем»
    lsw_cx = 480
    lsw_bus_x = lsw_cx
    lsw_top = 120   # рівень шини
    lsw_bot = 200   # нижче — вхід давача

    # Символ ключа (прямокутник + «розрив» у шині)
    lsw_box, lsw_bw, lsw_bh = textbox(lsw_cx, (lsw_top + lsw_bot) // 2,
                                        "Load\nSwitch",
                                        size=12, bold=True,
                                        fill="#f0f8e8", stroke=FIELD, sw=2.0,
                                        pad=10)
    frags.append(lsw_box)

    # Лінія від шини до load switch
    lsw_top_edge = (lsw_top + lsw_bot) // 2 - lsw_bh // 2
    lsw_bot_edge = (lsw_top + lsw_bot) // 2 + lsw_bh // 2
    frags.append(line(lsw_bus_x, bus_y_top, lsw_bus_x, lsw_top_edge,
                      color=POS, sw=2.0))

    # Давач під load switch
    sensor_cx, sensor_cy = lsw_cx, 320
    sensor_box, sw2, sh2 = textbox(sensor_cx, sensor_cy,
                                    "Давач / SD /\nрадіо-модуль",
                                    size=11, bold=False,
                                    fill=LGREY, stroke=DGREY, sw=1.5, pad=8)
    frags.append(sensor_box)

    # Вихід load switch → давач
    frags.append(arrow(lsw_bus_x, lsw_bot_edge, sensor_cx, sensor_cy - sh2 // 2,
                       color=FIELD, sw=2.0))

    # GND давача
    frags.append(line(sensor_cx, sensor_cy + sh2 // 2, sensor_cx, bus_y_bot,
                      color=NEG, sw=1.5))

    # Керуючий EN з GPIO (мала стрілочка збоку)
    en_src_x = esp_x + 20
    en_src_y = esp_y + esp_h
    frags.append(arrow(en_src_x, en_src_y + 5,
                       lsw_cx + lsw_bw // 2 + 4, (lsw_top + lsw_bot) // 2,
                       color=FIELD, sw=1.5))
    frags.append(text(en_src_x - 5, en_src_y + 22, "EN",
                      size=10, color=FIELD, bold=True, anchor="start"))

    # ── Сходинка 3: Soft-latch (кнопка + P-MOSFET між батарейкою і ESP32) ──
    # Показуємо вставку між батарейкою і основною шиною
    sl_cx = 200
    sl_top_y = 120     # на шині
    sl_bat_y = bus_y_top  # сама шина

    sl_box, sl_bw, sl_bh = textbox(sl_cx, sl_bat_y,
                                    "P-MOSFET\n(soft-latch)",
                                    size=12, bold=True,
                                    fill=LPURPLE, stroke=PURPLE, sw=2.0,
                                    pad=10)
    frags.append(sl_box)

    # Кнопка зліва знизу (символічна)
    btn_cx, btn_cy = sl_cx - 45, 200
    btn_box, btn_bw, btn_bh = textbox(btn_cx, btn_cy, "Кнопка",
                                       size=11, bold=False,
                                       fill="#f9ecff", stroke=PURPLE, sw=1.5,
                                       pad=7)
    frags.append(btn_box)

    # Кнопка → затвор MOSFET
    frags.append(arrow(btn_cx + btn_bw // 2, btn_cy,
                       sl_cx - sl_bw // 2, sl_bat_y,
                       color=PURPLE, sw=1.5))

    # HOLD-лінія від ESP32 (замикає) — штрихова
    frags.append(line(esp_x + 5, esp_y + 15, sl_cx + sl_bw // 2, sl_bat_y,
                      color=PURPLE, sw=1.5, dash="6,3"))
    frags.append(text(esp_x + 5, esp_y + 5, "HOLD",
                      size=9, color=PURPLE, anchor="start"))

    # Примітка: земля спільна
    frags.append(text(W // 2, H - 22,
                      "Земля (GND) спільна для всіх трьох — керують лише плюсовою шиною.",
                      size=11, color=MUTED, italic=True))

    # Легенда (три сходинки)
    legend_items = [
        (ORANGE, "RTC: будить за розкладом (alarm INT → wake GPIO)"),
        (FIELD,  "Load switch: відрізає живлення вузла (EN від GPIO)"),
        (PURPLE, "Soft-latch: P-MOSFET + кнопка = пристрій вимикає себе"),
    ]
    lx = 30
    for i, (col, lbl) in enumerate(legend_items):
        ly = H - 110 + i * 22
        frags.append(rect(lx, ly - 9, 14, 14, fill=col, stroke=col, sw=0, rx=3))
        frags.append(text(lx + 20, ly + 2, lbl, size=11, color=col, anchor="start"))

    path = os.path.join(OUT, "fig-r13-4c-1-family.svg")
    render(path, W, H, *frags, title=None)
    print("  OK", path)


# ════════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.4c.2 — Схема soft-latch (кнопка-защіпка)
# ════════════════════════════════════════════════════════════════════════════════
def fig2_soft_latch():
    W, H = 780, 460
    frags = []

    frags.append(text(W // 2, 28, "Кнопка-защіпка (soft-latch): схема роботи",
                      size=17, bold=True))

    # ── Батарея (ліворуч) ────────────────────────────────────────────────────
    bat_cx, bat_cy = 80, 230
    bat_w, bat_h = 90, 160
    frags.append(rect(bat_cx - bat_w // 2, bat_cy - bat_h // 2, bat_w, bat_h,
                      fill="#eafaf1", stroke=FIELD, sw=2.0, rx=8))
    frags.append(text(bat_cx, bat_cy - bat_h // 2 - 12,
                      "Батарея", size=12, bold=True, color=FIELD))
    frags.append(plus(bat_cx, bat_cy - 30, r=10))
    frags.append(minus(bat_cx, bat_cy + 30, r=10))

    # Шини
    bus_y = 100   # плюс зверху
    gnd_y = 380   # земля знизу
    bus_x0 = bat_cx + bat_w // 2
    bus_x1 = 700

    frags.append(line(bus_x0, bus_y, bus_x1, bus_y, color=POS, sw=2.5))
    frags.append(line(bus_x0, gnd_y, bus_x1, gnd_y, color=NEG, sw=2.5))
    frags.append(text(bus_x0 + 12, bus_y - 10, "+VBAT", size=12,
                      color=POS, bold=True, anchor="start"))
    frags.append(text(bus_x0 + 12, gnd_y + 18, "GND", size=12,
                      color=NEG, bold=True, anchor="start"))

    # Батарея → шини
    frags.append(line(bat_cx, bat_cy - bat_h // 2, bat_cx, bus_y, color=POS, sw=2.0))
    frags.append(line(bat_cx + bat_w // 2, bus_y, bat_cx, bus_y, color=POS, sw=2.0))
    frags.append(line(bat_cx, bat_cy + bat_h // 2, bat_cx, gnd_y, color=NEG, sw=2.0))
    frags.append(line(bat_cx + bat_w // 2, gnd_y, bat_cx, gnd_y, color=NEG, sw=2.0))

    # ── P-MOSFET (high-side ключ між шиною і ESP32) ──────────────────────────
    mosfet_cx = 310
    mosfet_cy = 230

    # Символ P-MOSFET: прямокутник із підписом
    mos_box, mos_bw, mos_bh = textbox(mosfet_cx, mosfet_cy,
                                       "P-MOSFET\n(high-side)",
                                       size=13, bold=True,
                                       fill=LPURPLE, stroke=PURPLE, sw=2.5,
                                       pad=12)
    frags.append(mos_box)

    # Витік (source) → плюсова шина
    frags.append(line(mosfet_cx, mosfet_cy - mos_bh // 2, mosfet_cx, bus_y,
                      color=POS, sw=2.0))
    frags.append(text(mosfet_cx + 5, (mosfet_cy - mos_bh // 2 + bus_y) // 2,
                      "S (витік)", size=10, color=PURPLE, anchor="start"))

    # Стік (drain) → ESP32
    drain_y = mosfet_cy + mos_bh // 2

    # ── ESP32 (навантаження) ─────────────────────────────────────────────────
    esp_cx = 560
    esp_cy = 230
    esp_box, esp_bw, esp_bh = textbox(esp_cx, esp_cy,
                                       "ESP32\n(навантаження)",
                                       size=14, bold=True,
                                       fill="#eaf3fb", stroke=NEG, sw=2.5,
                                       pad=14)
    frags.append(esp_box)

    # З'єднання стік MOSFET → VOUT → VCC ESP32
    vout_x = (mosfet_cx + esp_cx - esp_bw // 2) // 2
    vout_y = (mosfet_cy + drain_y + (mosfet_cy - mos_bh // 2)) // 2
    vout_y = 315

    frags.append(line(mosfet_cx, drain_y, mosfet_cx, vout_y, color=POS, sw=2.0))
    frags.append(line(mosfet_cx, vout_y, esp_cx - esp_bw // 2, vout_y, color=POS, sw=2.0))
    frags.append(arrow(esp_cx - esp_bw // 2, vout_y, esp_cx - esp_bw // 2, esp_cy,
                       color=POS, sw=2.0))
    frags.append(text(mosfet_cx + 8, vout_y + 14, "VOUT → VCC",
                      size=11, color=POS, bold=True, anchor="start"))
    frags.append(text(mosfet_cx + 5, drain_y + 14, "D (стік)",
                      size=10, color=PURPLE, anchor="start"))

    # GND ESP32
    frags.append(line(esp_cx, esp_cy + esp_bh // 2, esp_cx, gnd_y,
                      color=NEG, sw=2.0))

    # ── Кнопка (зліва від затвора MOSFET) ────────────────────────────────────
    btn_cx, btn_cy = 175, 170
    btn_box, btn_bw, btn_bh = textbox(btn_cx, btn_cy,
                                       "Кнопка",
                                       size=12, bold=True,
                                       fill="#f9ecff", stroke=PURPLE, sw=2.0,
                                       pad=10)
    frags.append(btn_box)

    # Один бік кнопки → шина (+VCC)
    frags.append(line(btn_cx, btn_cy - btn_bh // 2, btn_cx, bus_y,
                      color=POS, sw=1.8))

    # Інший бік кнопки → затвор (через діод/резистор)
    gate_x = mosfet_cx - mos_bw // 2
    gate_y = mosfet_cy
    frags.append(arrow(btn_cx + btn_bw // 2, btn_cy, gate_x, gate_y,
                       color=PURPLE, sw=1.8))
    frags.append(text((btn_cx + btn_bw // 2 + gate_x) // 2,
                      (btn_cy + gate_y) // 2 - 10,
                      "START: затвор G", size=10, color=PURPLE, italic=True))

    # Підтяжка затвора до VCC (резистор — штрихова лінія)
    frags.append(line(gate_x, gate_y, gate_x, bus_y,
                      color=POS, sw=1.5, dash="5,3"))
    frags.append(text(gate_x - 5, (gate_y + bus_y) // 2,
                      "R\n(підтяжка)", size=10, color=MUTED, anchor="end"))

    # ── HOLD-лінія (GPIO ESP32 → затвор MOSFET) ──────────────────────────────
    hold_y = mosfet_cy + 30
    hold_esp_x = esp_cx - esp_bw // 2
    hold_gate_x = gate_x

    frags.append(line(hold_esp_x, hold_y, hold_gate_x, hold_y,
                      color=PURPLE, sw=2.0, dash="8,4"))
    frags.append(arrow(hold_gate_x, hold_y, hold_gate_x, gate_y + 5,
                       color=PURPLE, sw=2.0))

    # Позначення HOLD
    hold_mid_x = (hold_esp_x + hold_gate_x) // 2
    frags.append(rect(hold_mid_x - 55, hold_y - 18, 110, 24,
                      fill="#f5eef8", stroke=PURPLE, sw=1.5, rx=5))
    frags.append(text(hold_mid_x, hold_y - 2,
                      "HOLD = HIGH (latch)", size=11, color=PURPLE, bold=True))

    # ── KEY-READ-лінія (кнопка → GPIO ESP32 як вхід) ─────────────────────────
    key_y = esp_cy + 20
    frags.append(line(btn_cx + btn_bw // 2, btn_cy + btn_bh // 4,
                      hold_esp_x + 10, key_y,
                      color=ORANGE, sw=1.5, dash="5,3"))
    frags.append(text(btn_cx + btn_bw // 2 + 8, btn_cy + btn_bh // 4 + 12,
                      "KEY-READ →", size=10, color=ORANGE, italic=True, anchor="start"))

    # ── Анотація «вимкнути» ───────────────────────────────────────────────────
    ann_box, ann_bw, ann_bh = textbox(esp_cx, gnd_y - 55,
                                       "Знімає HOLD → LOW\n→ MOSFET закрито\n→ струм = 0",
                                       size=11, bold=False,
                                       fill="#fdecea", stroke=POS, sw=1.5,
                                       pad=8)
    frags.append(ann_box)
    frags.append(arrow(esp_cx, gnd_y - 55 - ann_bh // 2 - 6,
                       esp_cx, gnd_y - 55 - ann_bh // 2 - 14,
                       color=POS, sw=1.5))

    # ── Примітка знизу ───────────────────────────────────────────────────────
    frags.append(text(W // 2, H - 18,
                      "Перший рядок setup(): HOLD=HIGH — інакше МК згасне, "
                      "поки кнопку відпускають.",
                      size=11, color=MUTED, italic=True))

    path = os.path.join(OUT, "fig-r13-4c-2-soft-latch.svg")
    render(path, W, H, *frags, title=None)
    print("  OK", path)


# ── Запуск ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating figures for r13-s4-c-wake-hw ...")
    fig1_family()
    fig2_soft_latch()
    print("Done.")
