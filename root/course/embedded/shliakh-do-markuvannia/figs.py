# -*- coding: utf-8 -*-
"""Генератор фігур для теми «Шлях до маркування»."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_compliance_funnel():
    """Фігура 1: Воронка сертифікаційного шляху — від столу до нанесення знака."""
    w, h = 880, 260
    frags = []

    # 5 послідовних блоків конвеєра
    stages = [
        ("1. Стіл розробника", "Передвипробування (Pre-compliance)\nЗонди H/E-поля, LISN, спектр\nВиявлення викидів до камери"),
        ("2. План і модуль", "Вибір шляху сертифікації\nПовторне використання FCC/RED ID\nМатриця випробувань і режимів"),
        ("3. Акредитована лаба", "Виміри в безлунній камері\nЕмісія, імунітет, ESD, радіо\nОфіційні протоколи (Test Reports)"),
        ("4. Технічний файл", "Формування досьє (TCF)\nBOM, схеми, аналіз ризиків\nДекларація відповідності (DoC)"),
        ("5. Маркування", "Нанесення CE, FCC ID, UKCA\nШильдик, інструкція, коробка\nПраво легального продажу"),
    ]

    bx_w = 152
    bx_h = 100
    gap = 22
    start_x = 20
    top_y = 60

    for i, (title, desc) in enumerate(stages):
        x = start_x + i * (bx_w + gap)
        # Рамка етапу
        fill_col = "#f4f8fa" if i < 2 else ("#edf5ed" if i == 2 else "#fef8f0" if i == 3 else "#eef7ee")
        stroke_col = "#2457d6" if i < 2 else ("#27ae60" if i == 2 else "#d97706" if i == 3 else "#16a34a")
        
        frags.append(rect(x, top_y, bx_w, bx_h, fill=fill_col, stroke=stroke_col, sw=1.5, rx=6))
        frags.append(text(x + bx_w / 2, top_y + 22, title, size=13, bold=True, color=INK))
        
        # Опис
        desc_lines = desc.split("\n")
        frags.append(mtext(x + bx_w / 2, top_y + 44, desc_lines, size=10, color=MUTED, lh=1.35))
        
        # Стрілка переходу
        if i < len(stages) - 1:
            arr_x1 = x + bx_w + 3
            arr_x2 = x + bx_w + gap - 3
            frags.append(arrow(arr_x1, top_y + bx_h / 2, arr_x2, top_y + bx_h / 2, color=LINE, sw=1.8))

    # Нижній банер ціни помилки
    banner_y = 190
    frags.append(rect(start_x, banner_y, w - 2 * start_x, 50, fill="#fdf2f2", stroke="#e0b4b4", sw=1.2, rx=6))
    frags.append(text(start_x + 20, banner_y + 22, "Ціна виправлення дефекту:", size=12, bold=True, color=POS, anchor="start"))
    frags.append(text(start_x + 220, banner_y + 22, "На столі: $0 і заміна конденсатора", size=11, color=INK, anchor="start"))
    frags.append(text(start_x + 530, banner_y + 22, "У камері: $2500/день + місяць черги", size=11, color=POS, bold=True, anchor="start"))
    frags.append(text(start_x + 20, banner_y + 40, "Мета маршруту — заходити в лабораторію лише за формальним протоколом, без сюрпризів.", size=10.5, italic=True, color=MUTED, anchor="start"))

    render(os.path.join(IMG_DIR, "compliance-funnel.svg"), w, h, *frags)


def fig_test_chamber_setup():
    """Фігура 2: Архітектура безлунної камери для випробувань на випромінювання (EMC/Radio)."""
    w, h = 860, 360
    frags = []

    # Стіни екранованої камери
    ch_x, ch_y, ch_w, ch_h = 30, 45, 570, 290
    frags.append(rect(ch_x, ch_y, ch_w, ch_h, fill="#f8fafc", stroke="#475569", sw=2.5, rx=8))
    frags.append(text(ch_x + 20, ch_y + 24, "Екранована безлунна камера (SAC / Semi-Anechoic Chamber)", size=12, bold=True, color="#334155", anchor="start"))

    # Пірамідальні поглиначі (схематично зверху й з боків)
    for px in range(ch_x + 10, ch_x + ch_w - 20, 25):
        frags.append(f'<polygon points="{px},{ch_y+5} {px+12},{ch_y+20} {px+24},{ch_y+5}" fill="#64748b"/>')
    for py in range(ch_y + 35, ch_y + ch_h - 20, 25):
        frags.append(f'<polygon points="{ch_x+5},{py} {ch_x+20},{py+12} {ch_x+5},{py+24}" fill="#64748b"/>')

    # Металева підлога (земляний полігон)
    floor_y = ch_y + ch_h - 25
    frags.append(rect(ch_x + 10, floor_y, ch_w - 20, 15, fill="#cbd5e1", stroke="#94a3b8", sw=1.2, rx=2))
    frags.append(text(ch_x + ch_w / 2, floor_y + 11, "Суцільний металевий полігон землі (Ground Reference Plane)", size=10, color="#475569"))

    # Поворотний стіл з EUT
    table_cx = ch_x + 110
    table_top = floor_y - 70
    frags.append(rect(table_cx - 45, table_top, 90, 70, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(table_cx, table_top + 45, "Стіл 0.8 м / 1.5 м", size=9.5, color="#92400e"))
    frags.append(text(table_cx, table_top + 60, "(обертання 0–360°)", size=9, color="#92400e"))

    # Сам пристрій (EUT)
    frags.append(rect(table_cx - 28, table_top - 32, 56, 32, fill="#fee2e2", stroke="#dc2626", sw=1.8, rx=3))
    frags.append(text(table_cx, table_top - 18, "EUT", size=11, bold=True, color="#991b1b"))
    frags.append(text(table_cx, table_top - 6, "Виріб", size=9, color="#991b1b"))

    # Вимірювальна антена на щоглі
    ant_cx = ch_x + 470
    mast_top = ch_y + 60
    # Щогла (лінія або прямокутник без накладки)
    frags.append(rect(ant_cx - 4, mast_top, 8, floor_y - mast_top, fill="#cbd5e1", stroke="#64748b", sw=1.2, rx=1))
    # Рухома каретка антени
    ant_y = mast_top + 60
    frags.append(rect(ant_cx - 18, ant_y - 10, 36, 20, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=3))
    # Вуса антени (логоперіодична/біконічна)
    frags.append(line(ant_cx - 45, ant_y - 20, ant_cx - 18, ant_y, color="#1e40af", sw=2.5))
    frags.append(line(ant_cx - 45, ant_y + 20, ant_cx - 18, ant_y, color="#1e40af", sw=2.5))
    frags.append(line(ant_cx - 32, ant_y - 12, ant_cx - 14, ant_y, color="#1e40af", sw=2))
    frags.append(line(ant_cx - 32, ant_y + 12, ant_cx - 14, ant_y, color="#1e40af", sw=2))
    frags.append(text(ant_cx + 25, ant_y - 18, "Антена", size=11, bold=True, color="#1e40af", anchor="start"))
    frags.append(text(ant_cx + 25, ant_y - 4, "h: 1–4 м", size=10, color="#1e40af", anchor="start"))

    # Стрілка зміни висоти антени
    frags.append(arrow(ant_cx + 40, ant_y + 12, ant_cx + 40, ant_y + 36, color="#2563eb", sw=1.5))
    frags.append(arrow(ant_cx + 40, ant_y + 36, ant_cx + 40, ant_y + 12, color="#2563eb", sw=1.5))

    # Розмірна лінія дистанції 3 м / 10 м
    dist_y = table_top - 50
    frags.append(line(table_cx, dist_y, ant_cx, dist_y, color="#475569", sw=1.2, dash="4,4"))
    frags.append(line(table_cx, dist_y - 6, table_cx, dist_y + 6, color="#475569", sw=1.5))
    frags.append(line(ant_cx, dist_y - 6, ant_cx, dist_y + 6, color="#475569", sw=1.5))
    frags.append(text((table_cx + ant_cx) / 2, dist_y - 8, "Нормована відстань: 3 м або 10 м", size=11, bold=True, color="#334155"))

    # Зовнішня вимірювальна кімната
    room_x, room_y, room_w, room_h = 630, 45, 200, 290
    frags.append(rect(room_x, room_y, room_w, room_h, fill="#f1f5f9", stroke="#334155", sw=2, rx=6))
    frags.append(text(room_x + room_w / 2, room_y + 24, "Кімната оператора", size=12, bold=True, color="#0f172a"))

    # Прилад: EMI Receiver / Спектроаналізатор
    frags.append(rect(room_x + 20, room_y + 55, room_w - 40, 75, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=4))
    frags.append(text(room_x + room_w / 2, room_y + 78, "EMI Receiver", size=12, bold=True, color="#38bdf8"))
    frags.append(text(room_x + room_w / 2, room_y + 96, "Квазіпіковий детектор (QP)", size=9.5, color="#94a3b8"))
    frags.append(text(room_x + room_w / 2, room_y + 112, "CISPR 16-1-1 смуги", size=9, color="#94a3b8"))

    # Кабель від антени крізь стіну камери
    frags.append(line(ant_cx, ant_y + 10, ant_cx, floor_y - 5, color="#2563eb", sw=2))
    frags.append(line(ant_cx, floor_y - 5, ch_x + ch_w, floor_y - 5, color="#2563eb", sw=2))
    frags.append(line(ch_x + ch_w, floor_y - 5, room_x + 20, room_y + 90, color="#2563eb", sw=2, dash="3,3"))
    frags.append(text(room_x + room_w / 2, room_y + 160, "Кабель 50 Ом N-type", size=10, color=MUTED))

    # Автоматизована станція керування
    frags.append(rect(room_x + 20, room_y + 190, room_w - 40, 75, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    frags.append(text(room_x + room_w / 2, room_y + 215, "ПО сканування спектра", size=11, bold=True, color="#334155"))
    frags.append(text(room_x + room_w / 2, room_y + 235, "Синхронізація кута столу,", size=9.5, color=MUTED))
    frags.append(text(room_x + room_w / 2, room_y + 250, "висоти й поляризації антени", size=9.5, color=MUTED))

    render(os.path.join(IMG_DIR, "test-chamber-setup.svg"), w, h, *frags)


def fig_marking_grid_and_label():
    """Фігура 3: Анатомія сертифікаційного маркування та шильдика виробу."""
    w, h = 860, 310
    frags = []

    # Ліва половина: Геометрія знака CE
    ce_box_x, ce_box_y, ce_box_w, ce_box_h = 25, 45, 340, 240
    frags.append(rect(ce_box_x, ce_box_y, ce_box_w, ce_box_h, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(ce_box_x + 15, ce_box_y + 22, "Геометрична сітка знака CE (≥ 5 мм)", size=12, bold=True, color=INK, anchor="start"))

    # Кола сітки CE (два кола, що перетинаються за стандартом)
    c1_x, c1_y = ce_box_x + 105, ce_box_y + 125
    c2_x, c2_y = ce_box_x + 215, ce_box_y + 125
    r_ce = 55

    # Допоміжні сітки
    frags.append(f'<circle cx="{c1_x:.1f}" cy="{c1_y:.1f}" r="{r_ce:.1f}" fill="none" stroke="#93c5fd" stroke-width="1.2" stroke-dasharray="3,3"/>')
    frags.append(f'<circle cx="{c1_x:.1f}" cy="{c1_y:.1f}" r="{r_ce * 0.68:.1f}" fill="none" stroke="#93c5fd" stroke-width="1" stroke-dasharray="2,2"/>')
    frags.append(f'<circle cx="{c2_x:.1f}" cy="{c2_y:.1f}" r="{r_ce:.1f}" fill="none" stroke="#93c5fd" stroke-width="1.2" stroke-dasharray="3,3"/>')
    frags.append(f'<circle cx="{c2_x:.1f}" cy="{c2_y:.1f}" r="{r_ce * 0.68:.1f}" fill="none" stroke="#93c5fd" stroke-width="1" stroke-dasharray="2,2"/>')

    # Символ C і E товстими лініями
    frags.append(f'<path d="M {c1_x+38} {c1_y-40} A 55 55 0 1 0 {c1_x+38} {c1_y+40} L {c1_x+26} {c1_y+28} A 38 38 0 1 1 {c1_x+26} {c1_y-28} Z" fill="#1e3a8a"/>')
    frags.append(f'<path d="M {c2_x+38} {c2_y-40} A 55 55 0 1 0 {c2_x+38} {c2_y+40} L {c2_x+26} {c2_y+28} A 38 38 0 1 1 {c2_x+26} {c2_y-28} Z" fill="#1e3a8a"/>')
    # Середня перемичка E (мусить дотикатися внутрішнього кола)
    frags.append(rect(c2_x - 38, c2_y - 6, 28, 12, fill="#1e3a8a", stroke="none"))

    # Пояснення відстані
    frags.append(text(ce_box_x + ce_box_w / 2, ce_box_y + 205, "Відстань між C та E строго фіксована:", size=10, bold=True, color="#1e3a8a"))
    frags.append(text(ce_box_x + ce_box_w / 2, ce_box_y + 222, "внутрішнє півколо C торкається зовнішнього півкола E", size=9.5, color=MUTED))

    # Права половина: Реальний шильдик готового виробу (Device Nameplate)
    lbl_x, lbl_y, lbl_w, lbl_h = 390, 45, 445, 240
    frags.append(rect(lbl_x, lbl_y, lbl_w, lbl_h, fill="#18181b", stroke="#27272a", sw=2, rx=8))

    # Заголовок шильдика
    frags.append(text(lbl_x + 20, lbl_y + 28, "ACME IOT SENSOR NODE", size=13, bold=True, color="#ffffff", anchor="start"))
    frags.append(text(lbl_x + lbl_w - 20, lbl_y + 28, "Model: SN-500W", size=11, color="#a1a1aa", anchor="end"))
    frags.append(line(lbl_x + 20, lbl_y + 38, lbl_x + lbl_w - 20, lbl_y + 38, color="#3f3f46", sw=1))

    # Електричні параметри
    frags.append(text(lbl_x + 20, lbl_y + 58, "Ratings: 12-24 V ⎓ 0.5 A Max  |  IP67  |  Temp: -20°C..+60°C", size=10, color="#d4d4d8", anchor="start"))
    frags.append(text(lbl_x + 20, lbl_y + 76, "Contains FCC ID: 2ACME-SN500  |  IC: 12345-SN500", size=10, color="#d4d4d8", anchor="start"))
    frags.append(text(lbl_x + 20, lbl_y + 94, "CAN ICES-003(B) / NMB-003(B)", size=9.5, color="#a1a1aa", anchor="start"))

    # Знаки відповідності (CE, UKCA, FCC, WEEE)
    # Знак CE
    frags.append(rect(lbl_x + 25, lbl_y + 115, 65, 45, fill="#27272a", stroke="#3f3f46", sw=1, rx=4))
    frags.append(text(lbl_x + 57, lbl_y + 144, "CE", size=22, bold=True, color="#ffffff"))

    # Знак UKCA
    frags.append(rect(lbl_x + 105, lbl_y + 115, 65, 45, fill="#27272a", stroke="#3f3f46", sw=1, rx=4))
    frags.append(text(lbl_x + 137, lbl_y + 143, "UKCA", size=14, bold=True, color="#ffffff"))

    # Знак FCC
    frags.append(rect(lbl_x + 185, lbl_y + 115, 65, 45, fill="#27272a", stroke="#3f3f46", sw=1, rx=4))
    frags.append(text(lbl_x + 217, lbl_y + 144, "FC", size=20, bold=True, color="#ffffff"))

    # Знак WEEE (перекреслений бак)
    frags.append(rect(lbl_x + 265, lbl_y + 115, 55, 45, fill="#27272a", stroke="#3f3f46", sw=1, rx=4))
    frags.append(rect(lbl_x + 280, lbl_y + 125, 25, 25, fill="none", stroke="#ffffff", sw=1.5, rx=2))
    frags.append(line(lbl_x + 276, lbl_y + 122, lbl_x + 309, lbl_y + 153, color="#ef4444", sw=2))
    frags.append(line(lbl_x + 309, lbl_y + 122, lbl_x + 276, lbl_y + 153, color="#ef4444", sw=2))

    # Виробник і серійний номер
    frags.append(line(lbl_x + 20, lbl_y + 175, lbl_x + lbl_w - 20, lbl_y + 175, color="#3f3f46", sw=1))
    frags.append(text(lbl_x + 20, lbl_y + 195, "ACME Embedded Systems Ltd., Tech Park 12, Kyiv, Ukraine", size=9.5, color="#a1a1aa", anchor="start"))
    frags.append(text(lbl_x + 20, lbl_y + 212, "S/N: AC2026-0800194  |  Made in Ukraine  |  DOM: 08/2026", size=9.5, bold=True, color="#e4e4e7", anchor="start"))

    render(os.path.join(IMG_DIR, "marking-grid-and-label.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_compliance_funnel()
    fig_test_chamber_setup()
    fig_marking_grid_and_label()
    print("All figures generated successfully.")
