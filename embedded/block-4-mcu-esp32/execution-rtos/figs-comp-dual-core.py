# -*- coding: utf-8 -*-
"""
Фігури для вставки ch27-s5-c-dual-core.md
«Два ядра ESP32 на практиці: PRO/APP і прив'язка задач»
Дві фігури:
  fig-27-5c-1-core-map.svg     — карта за умовчанням: що реально на кожному ядрі
  fig-27-5c-2-affinity-table.svg — таблиця-шпаргалка coreID для xTaskCreatePinnedToCore
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра (приведена до спільного стилю курсу)
C0   = "#1f47b5"   # Ядро 0 — синій
C1   = "#1f8a3b"   # Ядро 1 — зелений
WARN = "#c0271e"   # попередження / акцент
GOLD = "#b07a10"   # застереження
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LRED  = "#fbecec"
LAMB  = "#fff6e0"
LGOLD = "#fdf4db"
GREY  = "#8a8a8a"
INK2  = "#1b1b1b"


def fig1_core_map():
    """Карта за умовчанням: що реально осідає на кожному ядрі ESP32."""
    W, H = 860, 530
    parts = []

    # --- Заголовок ---
    parts.append(text(W / 2, 34, "ESP32: що реально на якому ядрі (за умовчанням)", size=18, bold=True))
    parts.append(text(W / 2, 56, "наївна модель «системне=0, ваше=1» — неповна; справжня картина тонша",
                      size=11, color=MUTED, italic=True))

    # --- Колонка Ядро 0 ---
    col0_x, col_w = 60, 340
    col1_x = 460
    col_y0 = 80
    col_h = 280

    # Рамка Ядро 0
    parts.append(rect(col0_x, col_y0, col_w, col_h, fill=LBLUE, stroke=C0, sw=2.2, rx=12))
    parts.append(text(col0_x + col_w / 2, col_y0 + 28, "Ядро 0 (PRO_CPU)", size=14, color=C0, bold=True))
    parts.append(text(col0_x + col_w / 2, col_y0 + 46, "Xtensa LX6 / LX7", size=10, color=MUTED))

    tasks0 = [
        ("Wi-Fi / BT-стек", C0),
        ("ipc0 (міжядерні виклики)", C0),
        ("esp_timer / Tmr Svc", C0),
        ("обробники подій", MUTED),
        ("IDLE0", MUTED),
    ]
    for i, (name, col) in enumerate(tasks0):
        ty = col_y0 + 72 + i * 36
        parts.append(fitbox(col0_x + 14, ty, col_w - 28, 28, name,
                            fill="#ffffff", stroke=col, sw=1.4, rx=5, color=col, bold=(col != MUTED)))

    # --- Колонка Ядро 1 ---
    parts.append(rect(col1_x, col_y0, col_w, col_h, fill=LGRN, stroke=C1, sw=2.2, rx=12))
    parts.append(text(col1_x + col_w / 2, col_y0 + 28, "Ядро 1 (APP_CPU)", size=14, color=C1, bold=True))
    parts.append(text(col1_x + col_w / 2, col_y0 + 46, "Xtensa LX6 / LX7", size=10, color=MUTED))

    tasks1 = [
        ("loopTask: setup() + loop() [пріор. 1]", C1),
        ("ваші незакріплені задачі *", C1),
        ("IDLE1", MUTED),
    ]
    for i, (name, col) in enumerate(tasks1):
        ty = col_y0 + 72 + i * 36
        parts.append(fitbox(col1_x + 14, ty, col_w - 28, 28, name,
                            fill="#ffffff", stroke=col, sw=1.4, rx=5, color=col, bold=(col != MUTED)))

    # --- Виноски ---
    note_y = col_y0 + col_h + 22

    # Виноска 1: xTaskCreate без Pinned
    box1, bw1, bh1 = textbox(W / 2 - 12, note_y + 32,
        "* незакріплена xTaskCreate → ядро творця (зазвичай Ядро 1),\n  а НЕ автобаланс між ядрами",
        size=12, fill=LAMB, stroke=GOLD, sw=1.6, color=INK2, pad=10, rx=8)
    parts.append(box1)

    # Виноска 2: ISR/драйвер прилипає
    box2, bw2, bh2 = textbox(W / 2 - 12, note_y + 32 + bh1 + 16,
        "ISR/драйвер прилипає до ядра, де викликали install:\nWire.begin(), attachInterrupt(), ledcSetup() тощо",
        size=12, fill=LRED, stroke=WARN, sw=1.6, color=INK2, pad=10, rx=8)
    parts.append(box2)

    path = os.path.join(OUT, "fig-27-5c-1-core-map.svg")
    render(path, W, H, *parts)
    print("wrote fig-27-5c-1-core-map.svg")


def fig2_affinity_table():
    """Таблиця-шпаргалка: останній аргумент coreID у xTaskCreatePinnedToCore."""
    W, H = 820, 400
    parts = []

    parts.append(text(W / 2, 34, "Вибір ядра: останній аргумент xTaskCreatePinnedToCore", size=17, bold=True))
    parts.append(text(W / 2, 56, "три значення — три стратегії; перевіряй через xPortGetCoreID() всередині задачі",
                      size=11, color=MUTED, italic=True))

    # Заголовки стовпців
    COL = [70, 240, 430, 660]  # x-початок кожного стовпця
    CW  = [160, 180, 220, 130]  # ширини
    HDR_Y = 80
    ROW_H = 64
    ROWS = 3

    headers = ["coreID", "Де виконується", "Коли використовувати", "Застереження"]
    hcolors = [INK, INK, INK, WARN]
    for j, (hdr, hcol) in enumerate(zip(headers, hcolors)):
        parts.append(fitbox(COL[j], HDR_Y, CW[j], 32, hdr,
                            fill=FILL, stroke=LINE, sw=1.5, rx=4, color=hcol, bold=True))

    rows = [
        ("1", "Ядро 1 (APP)", "Тайм-критичне; окремо від\nрадіо-стека (Wi-Fi/BT)", C1,
         "безпечно для\nбільшості задач"),
        ("0", "Ядро 0 (PRO)", "Лише свідомо і обережно;\nпоруч із Wi-Fi/BT-стеком", WARN,
         "може давити\nрадіо-стек!"),
        ("tskNO_\nAFFINITY", "Планувальник\nобере вільніше", "Для задач, байдужих\nдо конкретного ядра", C0,
         "на S2/C3 (1 ядро)\n= ядро 0 (§4.1.7)"),
    ]

    fill_bg = [LGRN, LRED, LBLUE]
    stroke_c = [C1, WARN, C0]

    for i, (val, where, when, col, warn) in enumerate(rows):
        ry = HDR_Y + 32 + 6 + i * (ROW_H + 4)
        # coreID
        parts.append(fitbox(COL[0], ry, CW[0], ROW_H, val,
                            fill=fill_bg[i], stroke=stroke_c[i], sw=1.8, rx=6, color=col, bold=True))
        # де виконується
        parts.append(fitbox(COL[1], ry, CW[1], ROW_H, where,
                            fill="#fbfcff", stroke=LINE, sw=1.2, rx=5, color=INK))
        # коли
        parts.append(fitbox(COL[2], ry, CW[2], ROW_H, when,
                            fill="#fbfcff", stroke=LINE, sw=1.2, rx=5, color=INK))
        # застереження
        parts.append(fitbox(COL[3], ry, CW[3], ROW_H, warn,
                            fill=LGOLD, stroke=GOLD, sw=1.3, rx=5, color=GOLD, bold=True))

    # Підказка внизу
    bottom_y = HDR_Y + 32 + 6 + ROWS * (ROW_H + 4) + 16
    box, bw, bh = textbox(W / 2, bottom_y + 22,
        "Завжди підтверджуй розміщення: xPortGetCoreID() всередині задачі\nповерне 0 або 1 — саме звідки вона насправді біжить.",
        size=12, fill=LAMB, stroke=GOLD, sw=1.6, color=INK2, pad=10, rx=8)
    parts.append(box)

    path = os.path.join(OUT, "fig-27-5c-2-affinity-table.svg")
    render(path, W, H, *parts)
    print("wrote fig-27-5c-2-affinity-table.svg")


if __name__ == "__main__":
    fig1_core_map()
    fig2_affinity_table()
