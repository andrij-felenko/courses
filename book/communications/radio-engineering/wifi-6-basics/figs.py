# -*- coding: utf-8 -*-
import sys
import os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору від book/communications/radio-engineering/wifi-6-basics)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def render(w, h, elements):
    """Скласти підсумковий SVG-документ з оголошенням стрілок."""
    defs = '''<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/>
    </marker>
  </defs>''' % INK
    body = "\n  ".join(elements)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '  %s\n  %s\n</svg>' % (w, h, w, h, defs, body))

def save_svg(filename, content):
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Збережено: %s" % path)


# ── Фігура 1: Порівняння OFDM (Wi-Fi 5) та OFDMA (Wi-Fi 6) ─────────────────────
def fig_ofdma_vs_ofdm():
    W, H = 820, 390
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    # Ліва секція: OFDM (802.11ac / Wi-Fi 5)
    p.append(rect(15, 15, 385, 360, fill="#fff8f6", stroke=POS, sw=1.2, rx=8))
    p.append(text(207, 40, "OFDM (Wi-Fi 5 / 802.11ac)", size=14, color=POS, bold=True))
    p.append(text(207, 60, "Монопольний доступ до усієї смуги 20 МГц", size=11, color=MUTED))

    # Слоти часу для OFDM
    p.append(rect(35, 85, 345, 75, fill="#ffebee", stroke=POS, sw=1.0, rx=4))
    p.append(text(75, 125, "Час T1", size=11, color=POS, bold=True))
    p.append(rect(125, 95, 240, 55, fill="#ffcdd2", stroke=POS, sw=1.2, rx=4))
    p.append(text(245, 128, "Клієнт A (займає всі 20 МГц)", size=12, color=POS, bold=True))

    p.append(rect(35, 170, 345, 75, fill="#e8eaf6", stroke=NEG, sw=1.0, rx=4))
    p.append(text(75, 210, "Час T2", size=11, color=NEG, bold=True))
    p.append(rect(125, 180, 240, 55, fill="#c5cae9", stroke=NEG, sw=1.2, rx=4))
    p.append(text(245, 213, "Клієнт B (чекав завершення T1)", size=12, color=NEG, bold=True))

    p.append(rect(35, 255, 345, 75, fill="#e8f5e9", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(75, 295, "Час T3", size=11, color=FIELD, bold=True))
    p.append(rect(125, 265, 240, 55, fill="#c8e6c9", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(245, 298, "Клієнт C (великий патч завад)", size=12, color=FIELD, bold=True))

    p.append(text(207, 355, "Висока затримка при малій довжині пакетів", size=10, color=POS, bold=True))


    # Права секція: OFDMA (Wi-Fi 6 / 802.11ax)
    p.append(rect(420, 15, 385, 360, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(612, 40, "OFDMA (Wi-Fi 6 / 802.11ax)", size=14, color=FIELD, bold=True))
    p.append(text(612, 60, "Паралельний доступ через Resource Units (RU)", size=11, color=MUTED))

    # Слот часу Час T1 в OFDMA розділений за частотою
    p.append(rect(440, 85, 345, 245, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(475, 205, "Час T1", size=11, color=FIELD, bold=True))

    # Блоки RU у смузі 20 МГц
    p.append(rect(515, 95, 255, 52, fill="#ffcdd2", stroke=POS, sw=1.2, rx=4))
    p.append(text(642, 126, "RU 106: Клієнт A (10 МГц)", size=11, color=POS, bold=True))

    p.append(rect(515, 153, 255, 52, fill="#c5cae9", stroke=NEG, sw=1.2, rx=4))
    p.append(text(642, 184, "RU 52: Клієнт B (5 МГц)", size=11, color=NEG, bold=True))

    p.append(rect(515, 211, 255, 52, fill="#c8e6c9", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(642, 242, "RU 26: Клієнт C (2.5 МГц)", size=11, color=FIELD, bold=True))

    p.append(rect(515, 269, 255, 52, fill="#fff9c4", stroke=INK, sw=1.2, rx=4))
    p.append(text(642, 300, "RU 26: Клієнт D (2.5 МГц)", size=11, color=INK, bold=True))

    p.append(text(612, 355, "Одночасна передача: мінімальна затримка", size=10, color=FIELD, bold=True))

    save_svg("ofdma-vs-ofdm.svg", render(W, H, p))


# ── Фігура 2: Структура розподілу піднесучих та Resource Units (RU) ────────────
def fig_ru_allocation_grid():
    W, H = 820, 380
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    p.append(text(410, 30, "Структура смуги 20 МГц в 802.11ax (256 піднесучих, Δf = 78.125 кГц)", size=14, color=INK, bold=True))
    p.append(text(410, 50, "Поділ каналу на ресурсні блоки (Resource Units — RU)", size=11, color=MUTED))

    # Осі частот
    p.append(line(40, 310, 780, 310, color=INK, sw=1.8))
    p.append(arrow(780, 310, 795, 310, color=INK, sw=1.8))
    p.append(text(795, 330, "f", size=12, color=INK, bold=True))

    # Захисні інтервали краю каналу (Guard Band)
    p.append(rect(40, 80, 35, 210, fill="#e0e0e0", stroke=MUTED, sw=1.0, rx=2))
    p.append(text(57, 185, "Guard", size=10, color=MUTED, anchor="middle"))

    p.append(rect(745, 80, 35, 210, fill="#e0e0e0", stroke=MUTED, sw=1.0, rx=2))
    p.append(text(762, 185, "Guard", size=10, color=MUTED, anchor="middle"))

    # Центральні несучі (DC subcarriers)
    p.append(rect(395, 80, 30, 210, fill="#bdbdbd", stroke=INK, sw=1.0, rx=2))
    p.append(text(410, 185, "DC", size=10, color=INK, bold=True))

    # Варіант A: 9 x RU 26
    p.append(text(215, 98, "Варіант 1: 9 × RU26 (по 26 піднесучих)", size=10, color=POS, bold=True))
    ru26_x = [80, 115, 150, 185, 220, 430, 465, 500, 535]
    for idx, x in enumerate(ru26_x):
        w_box = 30
        p.append(rect(x, 110, w_box, 35, fill="#ffebee", stroke=POS, sw=1.0, rx=3))
        p.append(text(x + w_box/2, 132, f"RU{idx+1}", size=9, color=POS))

    # Варіант B: 4 x RU 52
    p.append(text(215, 163, "Варіант 2: 4 × RU52 (по 52 піднесучих)", size=10, color=NEG, bold=True))
    ru52_x = [80, 150, 430, 500]
    for idx, x in enumerate(ru52_x):
        w_box = 65
        p.append(rect(x, 175, w_box, 35, fill="#e8eaf6", stroke=NEG, sw=1.0, rx=3))
        p.append(text(x + w_box/2, 197, f"RU52 #{idx+1}", size=10, color=NEG))

    # Варіант C: 2 x RU 106
    p.append(text(215, 228, "Варіант 3: 2 × RU106 (по 106 піднесучих)", size=10, color=FIELD, bold=True))
    ru106_x = [80, 430]
    for idx, x in enumerate(ru106_x):
        w_box = 135
        p.append(rect(x, 240, w_box, 35, fill="#e8f5e9", stroke=FIELD, sw=1.0, rx=3))
        p.append(text(x + w_box/2, 262, f"RU106 #{idx+1}", size=10, color=FIELD, bold=True))

    # Повна смуга RU 242 (Один користувач)
    p.append(rect(80, 285, 485, 20, fill="#fff9c4", stroke=INK, sw=1.2, rx=3))
    p.append(text(322, 299, "Повний канал: RU 242 (Single-User 20 МГц)", size=10, color=INK, bold=True))

    # Підписи частот
    p.append(text(40, 330, "-10 МГц", size=10, color=MUTED))
    p.append(text(410, 330, "0 (f_c)", size=10, color=INK, bold=True))
    p.append(text(780, 330, "+10 МГц", size=10, color=MUTED))

    p.append(text(410, 362, "Загалом 242 корисних піднесучих у каналі 20 МГц (234 даних + 8 пілот-сигналів)", size=10, color=MUTED, italic=True))

    save_svg("ru-allocation-grid.svg", render(W, H, p))


# ── Фігура 3: Часова послідовність UL MU-OFDMA та Trigger Frame ────────────────
def fig_trigger_frame_ul_ofdma():
    W, H = 820, 370
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    p.append(text(410, 30, "Синхронізація зворотного каналу UL MU-OFDMA через Trigger Frame", size=14, color=INK, bold=True))
    p.append(text(410, 50, "Точний розклад часу, частоти та потужності передачі від точці доступу (AP)", size=11, color=MUTED))

    # Лінії станцій AP, STA1, STA2, STA3
    y_ap   = 110
    y_sta1 = 175
    y_sta2 = 235
    y_sta3 = 295

    p.append(text(65, y_ap, "Точка доступу (AP)", size=11, color=POS, bold=True))
    p.append(text(65, y_sta1, "Станція STA 1", size=11, color=NEG, bold=True))
    p.append(text(65, y_sta2, "Станція STA 2", size=11, color=FIELD, bold=True))
    p.append(text(65, y_sta3, "Станція STA 3", size=11, color=INK, bold=True))

    # Горизонтальні часові осі (розбиті на сегменти, щоб не перетинати блоки та текст)
    # AP рядок
    p.append(line(125, y_ap, 145, y_ap, color=MUTED, sw=1.0, dash="3,3"))
    p.append(line(285, y_ap, 615, y_ap, color=MUTED, sw=1.0, dash="3,3"))
    p.append(line(765, y_ap, 775, y_ap, color=MUTED, sw=1.0, dash="3,3"))

    # STA1, STA2, STA3 рядки
    for y_s in [y_sta1, y_sta2, y_sta3]:
        p.append(line(125, y_s, 335, y_s, color=MUTED, sw=1.0, dash="3,3"))
        p.append(line(565, y_s, 775, y_s, color=MUTED, sw=1.0, dash="3,3"))

    # Kрок 1: AP надсилає Trigger Frame (TF)
    p.append(rect(150, y_ap - 20, 130, 40, fill="#ffebee", stroke=POS, sw=1.5, rx=5))
    p.append(text(215, y_ap + 5, "Trigger Frame (TF)", size=11, color=POS, bold=True))

    # Смуга SIFS 16 мкс
    p.append(rect(290, 80, 40, 235, fill="#f5f5f5", stroke=MUTED, sw=1.0, rx=2))
    p.append(text(310, 72, "SIFS", size=9, color=MUTED))

    # Крок 2: Одночасна передача HE-TB PPDU від STA1, STA2, STA3 у призначених RU
    p.append(rect(340, y_sta1 - 20, 220, 40, fill="#e8eaf6", stroke=NEG, sw=1.5, rx=5))
    p.append(text(450, y_sta1 + 5, "HE-TB PPDU (RU 106)", size=11, color=NEG, bold=True))

    p.append(rect(340, y_sta2 - 20, 220, 40, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(450, y_sta2 + 5, "HE-TB PPDU (RU 52)", size=11, color=FIELD, bold=True))

    p.append(rect(340, y_sta3 - 20, 220, 40, fill="#fff9c4", stroke=INK, sw=1.5, rx=5))
    p.append(text(450, y_sta3 + 5, "HE-TB PPDU (RU 52)", size=11, color=INK, bold=True))

    # Смуга SIFS 16 мкс
    p.append(rect(570, 80, 40, 235, fill="#f5f5f5", stroke=MUTED, sw=1.0, rx=2))
    p.append(text(590, 72, "SIFS", size=9, color=MUTED))

    # Крок 3: AP надсилає Multi-STA BlockAck (M-BA)
    p.append(rect(620, y_ap - 20, 140, 40, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(690, y_ap + 5, "Multi-STA BlockAck", size=11, color=FIELD, bold=True))

    # Часова вісь знизу
    p.append(arrow(130, 340, 780, 340, color=INK, sw=1.5))
    p.append(text(785, 344, "t", size=12, color=INK, bold=True))

    save_svg("trigger-frame-ul-ofdma.svg", render(W, H, p))


# ── Фігура 4: Просторове повторне використання (Spatial Reuse) та BSS Coloring ──
def fig_bss_coloring_spatial_reuse():
    W, H = 820, 380
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    p.append(text(410, 30, "Механізм Spatial Reuse та BSS Coloring в 802.11ax", size=14, color=INK, bold=True))
    p.append(text(410, 50, "Подолання колізій у перекриваючих мережах (OBSS) через адаптивний поріг OBSS-PD", size=11, color=MUTED))

    # Ліва мережа BSS A (Color 1 - Червона)
    p.append(circle(220, 210, 150, fill="#fff5f5", stroke=POS, sw=1.5))
    p.append(textbox(220, 100, "BSS A (Колір 1)", size=12, color=POS, fill="#ffffff", stroke=POS, bold=True)[0])

    p.append(rect(140, 190, 50, 40, fill="#ffebee", stroke=POS, sw=1.5, rx=4))
    p.append(text(165, 214, "AP A", size=11, color=POS, bold=True))

    p.append(circle(260, 240, 16, fill="#ffcdd2", stroke=POS, sw=1.2))
    p.append(text(260, 244, "STA A", size=9, color=POS, bold=True))

    p.append(arrow(190, 210, 244, 235, color=POS, sw=1.8))
    p.append(text(220, 240, "Передача (Color 1)", size=9, color=POS))

    # Права мережа BSS B (Color 2 - Синя)
    p.append(circle(600, 210, 150, fill="#f0f4fe", stroke=NEG, sw=1.5))
    p.append(textbox(600, 100, "BSS B (Колір 2)", size=12, color=NEG, fill="#ffffff", stroke=NEG, bold=True)[0])

    p.append(rect(630, 190, 50, 40, fill="#e8eaf6", stroke=NEG, sw=1.5, rx=4))
    p.append(text(655, 214, "AP B", size=11, color=NEG, bold=True))

    p.append(circle(530, 240, 16, fill="#c5cae9", stroke=NEG, sw=1.2))
    p.append(text(530, 244, "STA B", size=9, color=NEG, bold=True))

    # Зона перекриття (OBSS)
    p.append(line(370, 60, 370, 360, color=MUTED, sw=1.0, dash="4,4"))
    p.append(text(410, 345, "Зона перекриття каналів (OBSS)", size=10, color=MUTED, italic=True))

    # Сигнал завади від BSS A до AP B (розбитий на 2 сегменти навколо textbox)
    p.append(line(190, 200, 305, 210, color=POS, sw=1.2, dash="3,3"))
    p.append(textbox(390, 215, "Сигнал OBSS (Color 1)\nРівень RSSI < OBSS-PD threshold", size=9, color=POS, fill="#ffffff", stroke=POS)[0])
    p.append(line(475, 220, 530, 225, color=POS, sw=1.2, dash="3,3"))

    # Завдяки BSS Color 2, AP B не блокує свій передавач
    p.append(arrow(630, 210, 546, 235, color=NEG, sw=1.8))
    p.append(textbox(600, 300, "Паралельна передача BSS B!\n(Потужність знижено для захисту STA A)", size=10, color=FIELD, fill="#ffffff", stroke=FIELD, min_w=190)[0])

    save_svg("bss-coloring-spatial-reuse.svg", render(W, H, p))


if __name__ == "__main__":
    fig_ofdma_vs_ofdm()
    fig_ru_allocation_grid()
    fig_trigger_frame_ul_ofdma()
    fig_bss_coloring_spatial_reuse()
