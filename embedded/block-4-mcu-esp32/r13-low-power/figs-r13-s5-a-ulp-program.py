# -*- coding: utf-8 -*-
"""
Фігури для вставки r13-s5-a-ulp-program.md
«Програма для ULP: виміряти, порівняти з порогом і не будити ядра»

Рис. 4.13.5a.1 — Часова діаграма: RTC-таймер / ULP-виміри / рішення / стан ядер.
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
LBLUE   = "#d6eaf8"
DGREY   = "#555555"
LGREY   = "#f0f0f0"
SLEEP_FILL = "#dfe6e9"   # серий — ядра сплять
WAKE_FILL  = "#fdecea"   # червоний — ядра активні
ULP_FILL   = "#27ae60"   # зелений — ULP вимір


# ════════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.5a.1 — Часова діаграма ULP+ядра
# ════════════════════════════════════════════════════════════════════════════════
def fig1_ulp_timeline():
    W, H = 900, 460
    frags = []

    # ── Заголовок ────────────────────────────────────────────────────────────
    frags.append(text(W // 2, 28, "ULP + велике ядро: хто коли активний", size=17, bold=True))

    # Координати осі часу
    T_LEFT  = 70    # початок осі x
    T_RIGHT = 855   # кінець осі x
    T_TOP   = 55    # верхній відступ після заголовка

    # ── Вертикальні мітки доріжок (зліва) ───────────────────────────────────
    TRACK_H   = 64   # висота одної доріжки
    TRACK_GAP = 12   # відступ між доріжками

    track_y = {}  # cy кожної доріжки

    tracks = [
        ("rtc",    "RTC-таймер\n(тіки 20 мс)"),
        ("ulp",    "ULP\n(вимір АЦП)"),
        ("decide", "Рішення\nv > поріг?"),
        ("cores",  "Великі ядра\n(струм, мА/мкА)"),
    ]

    for i, (key, label) in enumerate(tracks):
        cy = T_TOP + TRACK_H // 2 + i * (TRACK_H + TRACK_GAP)
        track_y[key] = cy
        # Підпис доріжки
        frags.append(mtext(T_LEFT - 8, cy - 10, label, size=12, color=INK, anchor="end"))
        # Горизонтальна базова лінія доріжки
        frags.append(line(T_LEFT, cy + TRACK_H // 2 - 2, T_RIGHT, cy + TRACK_H // 2 - 2,
                          color="#e0e0e0", sw=1.0))

    # ── Вісь часу (стрілка) ─────────────────────────────────────────────────
    axis_y = T_TOP + len(tracks) * (TRACK_H + TRACK_GAP) + 8
    frags.append(arrow(T_LEFT, axis_y, T_RIGHT + 10, axis_y, color=INK, sw=1.5))
    frags.append(text(T_RIGHT + 18, axis_y + 4, "t", size=14, color=INK, italic=True))
    frags.append(text(T_LEFT, axis_y + 16, "0", size=11, color=MUTED))

    # ── Визначаємо тіки (5 тіків, останній — з перевищенням порогу) ─────────
    TICK_PERIOD = 148   # px між тіками (~20 мс кожен)
    ticks_x = [T_LEFT + 30 + i * TICK_PERIOD for i in range(5)]

    # Мітки тіків на осі
    for i, tx in enumerate(ticks_x):
        frags.append(line(tx, axis_y - 4, tx, axis_y + 4, color=INK, sw=1.2))
        frags.append(text(tx, axis_y + 18, "%d·Δt" % i if i > 0 else "", size=10, color=MUTED))

    frags.append(text(T_LEFT + 8, axis_y + 18, "0", size=10, color=MUTED))

    # ── Доріжка 1: RTC-таймер (пунктирні вертикальні імпульси) ──────────────
    rtc_y    = track_y["rtc"]
    rtc_base = rtc_y + TRACK_H // 2 - 10   # базова лінія
    rtc_top  = rtc_y - TRACK_H // 2 + 14   # верхівка імпульсу

    # Базова лінія RTC
    frags.append(line(T_LEFT, rtc_base, T_RIGHT, rtc_base, color=MUTED, sw=1.2, dash="4,3"))

    for tx in ticks_x:
        # Вертикальний імпульс тіку
        frags.append(line(tx, rtc_base, tx, rtc_top, color=ORANGE, sw=2.0))
        frags.append(line(tx, rtc_top, tx + 8, rtc_top, color=ORANGE, sw=2.0))
        frags.append(line(tx + 8, rtc_top, tx + 8, rtc_base, color=ORANGE, sw=2.0))

    # Підпис «~20 мс» між першими двома тіками
    mid_x = (ticks_x[0] + ticks_x[1]) // 2
    frags.append(line(ticks_x[0] + 8, rtc_top - 16, ticks_x[1], rtc_top - 16,
                      color=ORANGE, sw=1.0))
    frags.append(text(mid_x, rtc_top - 22, "~20 мс", size=10, color=ORANGE))

    # ── Доріжка 2: ULP-вимір (короткий зелений прямокутник на кожен тік) ────
    ulp_y    = track_y["ulp"]
    ulp_base = ulp_y + TRACK_H // 2 - 10
    ulp_top  = ulp_y - TRACK_H // 2 + 16
    ulp_w    = 18   # ширина активного імпульсу ULP (мікросекунди)

    # Базова лінія
    frags.append(line(T_LEFT, ulp_base, T_RIGHT, ulp_base, color=MUTED, sw=1.0, dash="4,3"))

    for tx in ticks_x:
        frags.append(rect(tx, ulp_top, ulp_w, ulp_base - ulp_top,
                          fill=LTEAL, stroke=TEAL, sw=1.5, rx=2))

    # Підпис «~мкс» над першим імпульсом
    frags.append(text(ticks_x[0] + ulp_w // 2, ulp_top - 6, "~мкс", size=10, color=TEAL))

    # ── Доріжка 3: Рішення (ромб або текст «ні» / «так» над відповідним тіком)
    dec_y = track_y["decide"]

    # Для перших 4 тіків — «ні» (v ≤ поріг)
    for tx in ticks_x[:-1]:
        tb_no, _, _ = textbox(tx + ulp_w // 2, dec_y, "ні\n(v ≤ поріг)",
                               size=10, pad=5,
                               fill=LGREY, stroke=MUTED, sw=1.2, color=MUTED)
        frags.append(tb_no)

    # Для останнього тіку — «так» (v > поріг), зеленим
    tx_wake = ticks_x[-1]
    tb, tbw, tbh = textbox(tx_wake + ulp_w // 2, dec_y, "так!\nv > поріг",
                            size=10, pad=5,
                            fill="#eafaf1", stroke=FIELD, sw=2.0, color=FIELD, bold=True)
    frags.append(tb)

    # Стрілка-wakeup від «так» вниз до доріжки ядер
    cores_y = track_y["cores"]
    wakeup_x = tx_wake + ulp_w // 2
    frags.append(arrow(wakeup_x, dec_y + tbh // 2 + 4,
                       wakeup_x, cores_y - TRACK_H // 2 + 10,
                       color=POS, sw=2.0))
    frags.append(text(wakeup_x + 6, dec_y + tbh // 2 + 22,
                      "wakeup_result", size=10, color=POS, anchor="start"))

    # ── Доріжка 4: Великі ядра (довгий сірий «сон», потім сплеск) ───────────
    cores_base = cores_y + TRACK_H // 2 - 10
    cores_top_sleep = cores_y + 8     # низька лінія під час сну
    cores_top_wake  = cores_y - TRACK_H // 2 + 14  # висока під час активності

    # Весь час до пробудження — сплячий рівень (низька сіра лінія)
    frags.append(rect(T_LEFT, cores_top_sleep, tx_wake - T_LEFT, cores_base - cores_top_sleep,
                      fill=SLEEP_FILL, stroke="#b2bec3", sw=1.0, rx=0))
    frags.append(text((T_LEFT + tx_wake) // 2, cores_y + 6,
                      "deep-sleep  (~5 мкА)", size=11, color=DGREY))

    # Сплеск активності після wakeup (від останнього тіку до кінця діаграми)
    wake_start = tx_wake - 4
    wake_end   = T_RIGHT - 10
    frags.append(rect(wake_start, cores_top_wake, wake_end - wake_start,
                      cores_base - cores_top_wake,
                      fill=WAKE_FILL, stroke=POS, sw=1.5, rx=0))
    frags.append(text((wake_start + wake_end) // 2, cores_y - 4,
                      "пробудження (~45 мА)", size=11, color=POS, bold=True))
    frags.append(text((wake_start + wake_end) // 2, cores_y + 12,
                      "читає wakeup_result → знову засинає", size=10, color=DGREY))

    # ── Анотація «середній струм» праворуч ──────────────────────────────────
    ann_x = T_RIGHT - 130
    ann_y = axis_y - 10
    tb2, tb2w, tb2h = textbox(ann_x, ann_y,
                               "Iсер ≈ мкА\n(4 тіки × мкс)\nне мА",
                               size=11, pad=8,
                               fill=LTEAL, stroke=TEAL, sw=1.5, color=TEAL, bold=False)
    frags.append(tb2)  # tb2 is already the svg string from textbox

    # ── Легенда ──────────────────────────────────────────────────────────────
    leg_items = [
        (ORANGE, "RTC-таймер: тік кожні 20 мс"),
        (TEAL,   "ULP: вимір АЦП (~мкс, потім halt)"),
        (FIELD,  "ULP вирішує — будити чи ні"),
        (POS,    "Великі ядра прокидаються тільки на «так»"),
    ]
    lx = T_LEFT
    ly0 = axis_y + 36
    for i, (col, lbl) in enumerate(leg_items):
        ly = ly0 + i * 19
        frags.append(rect(lx, ly - 8, 12, 12, fill=col, stroke=col, sw=0, rx=2))
        frags.append(text(lx + 18, ly + 1, lbl, size=11, color=col, anchor="start"))

    path = os.path.join(OUT, "fig-r13-5a-1-ulp-timeline.svg")
    render(path, W, H, *frags, title=None)
    print("  OK", path)


# ── Запуск ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating figures for r13-s5-a-ulp-program ...")
    fig1_ulp_timeline()
    print("Done.")
