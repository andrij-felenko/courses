# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми pokolinnia (Покоління стільникового зв'язку)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_spectrum():
    """Ілюстрація часо-частотного поділу та спектральної структури поколінь."""
    w, h = 900, 490
    frags = []

    frags.append(text(450, 28, "Еволюція фізичного каналу: від фіксованих слотів до гнучкої сітки", size=16, bold=True))

    # Блок 2G GSM / GPRS
    b2_w, b2_h = 400, 185
    b2_x, b2_y = 35, 55
    frags.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(b2_x + 15, b2_y + 24, "2G GSM / GPRS / EDGE (FDMA + TDMA)", size=13, bold=True, anchor="start", color=INK))
    frags.append(text(b2_x + 15, b2_y + 44, "Несуча 200 кГц, кадр 4.615 мс ділиться на 8 слотів по 577 мкс", size=11, color=MUTED, anchor="start"))
    
    slot_w = 40
    slot_h = 48
    start_sx = b2_x + 18
    start_sy = b2_y + 60
    for i in range(8):
        is_tx = (i == 2)
        s_fill = "#fdecea" if is_tx else "#ffffff"
        s_stroke = POS if is_tx else "#94a3b8"
        s_sw = 2.0 if is_tx else 1.0
        frags.append(rect(start_sx + i * (slot_w + 4), start_sy, slot_w, slot_h, fill=s_fill, stroke=s_stroke, sw=s_sw, rx=3))
        frags.append(text(start_sx + i * (slot_w + 4) + slot_w / 2, start_sy + 22, "TS %d" % i, size=11, bold=is_tx, color=POS if is_tx else INK))
        frags.append(text(start_sx + i * (slot_w + 4) + slot_w / 2, start_sy + 38, "577 μs", size=9, color=MUTED))
    
    frags.append(text(start_sx + 2 * (slot_w + 4) + slot_w / 2, start_sy + 68, "Сплеск передачі (TX Burst: струм до 2 А)", size=10, bold=True, color=POS))
    frags.append(text(b2_x + 15, b2_y + 168, "Спектральна ефективність: ~0.1-0.3 біт/с/Гц · Жорсткий таймінг", size=11, color=INK, anchor="start"))

    # Блок 3G UMTS / WCDMA
    b3_w, b3_h = 400, 185
    b3_x, b3_y = 465, 55
    frags.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(b3_x + 15, b3_y + 24, "3G UMTS / HSPA (WCDMA / CDMA)", size=13, bold=True, anchor="start", color=INK))
    frags.append(text(b3_x + 15, b3_y + 44, "Фіксована смуга 5 МГц, пряме розширення спектра кодами OVSF", size=11, color=MUTED, anchor="start"))
    
    frags.append(rect(b3_x + 25, b3_y + 60, 350, 48, fill="#edf2f7", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(b3_x + 200, b3_y + 82, "Спільна радіочастотна смуга 5.0 МГц (3.84 Мчіп/с)", size=11, bold=True, color=INK))
    frags.append(text(b3_x + 200, b3_y + 98, "Одночасний ефір багатьох абонентів, поділ кодами", size=10, color=MUTED))
    frags.append(text(b3_x + 15, b3_y + 142, "«Дихання сот»: радіус соти стискається під високим навантаженням", size=10, color=POS, anchor="start"))
    frags.append(text(b3_x + 15, b3_y + 168, "Спектральна ефективність: ~0.8-1.5 біт/с/Гц · Складне керування потужністю", size=11, color=INK, anchor="start"))

    # Блок 4G LTE
    b4_w, b4_h = 400, 210
    b4_x, b4_y = 35, 255
    frags.append(rect(b4_x, b4_y, b4_w, b4_h, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(b4_x + 15, b4_y + 24, "4G LTE (OFDMA в DL / SC-FDMA в UL)", size=13, bold=True, anchor="start", color=INK))
    frags.append(text(b4_x + 15, b4_y + 44, "Гнучка смуга 1.4-20 МГц, сітка ресурсних блоків (RB = 180 кГц × 0.5 мс)", size=11, color=MUTED, anchor="start"))
    
    grid_x = b4_x + 25
    grid_y = b4_y + 58
    for r in range(3):
        for c in range(4):
            is_hl = (r == 1 and c == 2) or (r == 0 and c == 1)
            cell_fill = "#eaf0fd" if is_hl else "#ffffff"
            cell_stroke = NEG if is_hl else "#cbd5e1"
            frags.append(rect(grid_x + c * 88, grid_y + r * 25, 82, 21, fill=cell_fill, stroke=cell_stroke, sw=1.0, rx=2))
            frags.append(text(grid_x + c * 88 + 41, grid_y + r * 25 + 15, "RB (12 піднес.)", size=9, color=NEG if is_hl else MUTED))
    frags.append(text(b4_x + 15, b4_y + 158, "Cat.1 / Cat.4 / Cat.1bis: виділення смуги динамічно за потребою", size=10, bold=True, color=NEG, anchor="start"))
    frags.append(text(b4_x + 15, b4_y + 188, "Спектральна ефективність: ~2.5-4.0 біт/с/Гц · Тільки IP-пакети", size=11, color=INK, anchor="start"))

    # Блок 5G NR & RedCap
    b5_w, b5_h = 400, 210
    b5_x, b5_y = 465, 255
    frags.append(rect(b5_x, b5_y, b5_w, b5_h, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(b5_x + 15, b5_y + 24, "5G NR & 5G RedCap (3GPP Rel-17)", size=13, bold=True, anchor="start", color=INK))
    frags.append(text(b5_x + 15, b5_y + 44, "Гнучка нумерологія (15, 30, 60 кГц), частини смуги (BWP), RedCap 20 МГц", size=11, color=MUTED, anchor="start"))
    
    frags.append(rect(b5_x + 25, b5_y + 58, 350, 75, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    frags.append(rect(b5_x + 35, b5_y + 68, 140, 55, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(b5_x + 105, b5_y + 92, "RedCap BWP (20 МГц)", size=11, bold=True, color=FIELD))
    frags.append(text(b5_x + 105, b5_y + 110, "1T1R / 1T2R, до 150 Мбіт/с", size=9, color=INK))
    
    frags.append(rect(b5_x + 185, b5_y + 68, 180, 55, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=3))
    frags.append(text(b5_x + 275, b5_y + 92, "Широкий eMBB (до 100 МГц)", size=11, color=MUTED))
    frags.append(text(b5_x + 275, b5_y + 110, "4T4R MIMO, гігабітні потоки", size=9, color=MUTED))
    
    frags.append(text(b5_x + 15, b5_y + 158, "RedCap зменшує складність RF-тракту та пам'яті модема на 50-65%", size=10, bold=True, color=FIELD, anchor="start"))
    frags.append(text(b5_x + 15, b5_y + 188, "Спектральна ефективність: >5.0 біт/с/Гц · Мала затримка (<10 мс)", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT_DIR, "cellular-generations-spectrum.svg"), w, h, *frags)


def fig_power_profiles():
    """Порівняльний профіль струму споживання у часі для 2G, 4G Cat.4 та 4G/5G LPWAN."""
    w, h = 900, 440
    frags = []

    frags.append(text(450, 26, "Профілі споживання струму модема під час циклу передавання даних", size=16, bold=True))

    # Графік 1: 2G GSM (Піки 2A)
    p1_x, p1_y, p1_w, p1_h = 50, 55, 790, 95
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=4))
    frags.append(text(p1_x + 12, p1_y + 20, "2G GSM / GPRS: рідкісні, але катастрофічні піки передавача (2.0 A)", size=12, bold=True, anchor="start", color=POS))
    frags.append(line(p1_x + 40, p1_y + 75, p1_x + 750, p1_y + 75, color="#cbd5e1", sw=1.0))
    for bx in [120, 150, 180, 210, 240]:
        frags.append(line(p1_x + bx, p1_y + 75, p1_x + bx, p1_y + 35, color=POS, sw=2.5))
        frags.append(line(p1_x + bx, p1_y + 35, p1_x + bx + 8, p1_y + 35, color=POS, sw=2.5))
        frags.append(line(p1_x + bx + 8, p1_y + 35, p1_x + bx + 8, p1_y + 75, color=POS, sw=2.5))
    frags.append(text(p1_x + 280, p1_y + 45, "TX Bursts (577 μs, 2 A) — вимагає суперконденсатора на 1000-2200 μF", size=10, bold=True, color=POS, anchor="start"))
    frags.append(text(p1_x + 650, p1_y + 70, "Idle / DRX (~15-25 mA)", size=10, color=MUTED, anchor="start"))

    # Графік 2: 4G LTE Cat.4
    p2_x, p2_y, p2_w, p2_h = 50, 165, 790, 105
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=4))
    frags.append(text(p2_x + 12, p2_y + 20, "4G LTE Cat.4 (без PSM/eDRX): тривале високе споживання, швидке виснаження АКБ", size=12, bold=True, anchor="start", color=NEG))
    frags.append(line(p2_x + 40, p2_y + 85, p2_x + 750, p2_y + 85, color="#cbd5e1", sw=1.0))
    frags.append(rect(p2_x + 80, p2_y + 40, 160, 45, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=2))
    frags.append(text(p2_x + 160, p2_y + 65, "TX + RX Data (150-300 mA)", size=10, bold=True, color=NEG))
    frags.append(rect(p2_x + 240, p2_y + 60, 120, 25, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=2))
    frags.append(text(p2_x + 300, p2_y + 76, "RRC Connected (~50 mA)", size=9, color=MUTED))
    for px in range(370, 720, 40):
        frags.append(line(p2_x + px, p2_y + 85, p2_x + px, p2_y + 68, color=NEG, sw=1.5))
        frags.append(line(p2_x + px, p2_y + 68, p2_x + px + 5, p2_y + 68, color=NEG, sw=1.5))
        frags.append(line(p2_x + px + 5, p2_y + 68, p2_x + px + 5, p2_y + 85, color=NEG, sw=1.5))
    frags.append(text(p2_x + 460, p2_y + 58, "Часте слухання пейджингу DRX 1.28 с (~15-30 mA avg)", size=10, color=INK, anchor="start"))

    # Графік 3: 4G Cat.1bis / 5G RedCap з PSM та eDRX
    p3_x, p3_y, p3_w, p3_h = 50, 285, 790, 130
    frags.append(rect(p3_x, p3_y, p3_w, p3_h, fill="#fafbfc", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(p3_x + 12, p3_y + 20, "Сучасний IoT: 4G Cat.1bis / 5G RedCap з режимами PSM (Power Saving Mode) та eDRX", size=12, bold=True, anchor="start", color=FIELD))
    frags.append(line(p3_x + 40, p3_y + 105, p3_x + 750, p3_y + 105, color="#cbd5e1", sw=1.0))
    frags.append(rect(p3_x + 80, p3_y + 48, 70, 57, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=2))
    frags.append(text(p3_x + 115, p3_y + 72, "TX Data", size=10, bold=True, color=FIELD))
    frags.append(text(p3_x + 115, p3_y + 88, "80-150 mA", size=9, color=INK))
    frags.append(rect(p3_x + 150, p3_y + 75, 60, 30, fill="#f1f5f9", stroke="#94a3b8", sw=1.0, rx=2))
    frags.append(text(p3_x + 180, p3_y + 92, "T3324", size=9, color=MUTED))
    frags.append(rect(p3_x + 210, p3_y + 98, 520, 7, fill="#bbf7d0", stroke=FIELD, sw=1.0, rx=1))
    frags.append(text(p3_x + 450, p3_y + 80, "Глибокий сон PSM: струм < 5 μA (тривалість години/дні без перереєстрації)", size=11, bold=True, color=FIELD))
    frags.append(text(p3_x + 12, p3_y + 122, "Пристрій зберігає IP-сесію в пам'яті ядра мережі, не витрачаючи енергію на радіообмін", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT_DIR, "cellular-power-profiles.svg"), w, h, *frags)


def fig_tradeoff_matrix():
    """Карта компромісів: швидкість vs енергоспоживання та складність для проєктування пристроїв."""
    w, h = 900, 480
    frags = []

    frags.append(text(450, 26, "Вибір технології стільникового зв'язку для вбудованих систем", size=16, bold=True))

    ax_x, ax_y = 90, 410
    ax_w, ax_h = 760, 340
    frags.append(arrow(ax_x, ax_y, ax_x + ax_w, ax_y, color=LINE, sw=1.8))
    frags.append(text(ax_x + ax_w - 10, ax_y + 24, "Пропускна здатність (DL / UL) →", size=11, bold=True, anchor="end"))
    
    frags.append(arrow(ax_x, ax_y, ax_x, ax_y - ax_h, color=LINE, sw=1.8))
    frags.append(text(ax_x - 10, ax_y - ax_h + 15, "Енергоефективність та простота (BOM) ↑", size=11, bold=True, anchor="end"))

    x_steps = [
        (130, "< 200 кбіт/с"),
        (300, "1 - 10 Мбіт/с"),
        (490, "50 - 150 Мбіт/с"),
        (700, "1 - 10 Гбіт/с")
    ]
    for xp, lbl in x_steps:
        frags.append(line(ax_x + xp, ax_y - 5, ax_x + xp, ax_y + 5, color=MUTED, sw=1.0))
        frags.append(text(ax_x + xp, ax_y + 20, lbl, size=10, color=MUTED))

    # Зона 1: LPWAN
    z1_box, _, _ = textbox(ax_x + 120, ax_y - 270, "NB-IoT / LTE-M\nАвтономність: 5-10 років\nОдна антена, PSM/eDRX\nЛічильники, датчики", size=10, fill="#f0fdf4", stroke=FIELD, sw=1.5, bold=True)
    frags.append(z1_box)

    # Зона 2: Sunset
    z2_box, _, _ = textbox(ax_x + 130, ax_y - 90, "2G GSM / 3G UMTS (Sunset)\nВимкнення операторами!\n2A піки струму в 2G\nНе для нових розробок", size=10, fill="#fef2f2", stroke=POS, sw=1.5, bold=True, color=POS)
    frags.append(z2_box)

    # Зона 3: Середній сегмент
    z3_box, _, _ = textbox(ax_x + 400, ax_y - 210, "4G Cat.1bis / 5G RedCap\n«Золота середина» для IoT\n1 антена (Cat.1bis), 1-2 (RedCap)\n10-150 Мбіт/с, голос VoLTE/VoNR\nТрекери, телематика, POS", size=10, fill="#eff6ff", stroke=NEG, sw=2.0, bold=True, color=NEG)
    frags.append(z3_box)

    # Зона 4: Високошвидкісні шлюзи
    z4_box, _, _ = textbox(ax_x + 650, ax_y - 110, "4G Cat.4+ / 5G eMBB\nВисока швидкість (MIMO 2x2, 4x4)\nВисоке енергоспоживання (>2-5 Вт)\nРоутери, промислові шлюзи, VR", size=10, fill="#f8fafc", stroke=MUTED, sw=1.2, color=INK)
    frags.append(z4_box)

    # Стрілка міграції між зонами
    frags.append(arrow(ax_x + 235, ax_y - 120, ax_x + 295, ax_y - 170, color=NEG, sw=1.5))
    frags.append(text(ax_x + 245, ax_y - 150, "Міграція", size=10, bold=True, color=NEG, anchor="end"))

    render(os.path.join(OUT_DIR, "generations-tradeoff-matrix.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_spectrum()
    fig_power_profiles()
    fig_tradeoff_matrix()
    print("SVG генерацію завершено успішно.")
