# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Накопичувач збирача й холодний старт»."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_cold_start_dilemma():
    """Фігура 1: Пастка нульового заряду — бар'єр напруги CMOS проти мікрозбирача."""
    w, h = 880, 380
    f = []

    # Фон
    f.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0))

    # Лівий блок: Джерело мікроенергії
    bx1, by1, bw1, bh1 = 30, 40, 240, 300
    f.append(rect(bx1, by1, bw1, bh1, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(bx1 + bw1 / 2, by1 + 28, "Джерело збирання", size=15, bold=True, color=INK))
    f.append(text(bx1 + bw1 / 2, by1 + 48, "(TEG / Термоелемент / RF)", size=12, color=MUTED, italic=True))

    f.append(textbox(bx1 + bw1 / 2, by1 + 110, "Вхідна напруга:\n20 – 100 мВ", size=13, fill="#fef3c7", stroke="#d97706", bold=True, min_w=190)[0])
    f.append(textbox(bx1 + bw1 / 2, by1 + 185, "Потужність:\n10 – 50 мкВт", size=13, fill="#fef3c7", stroke="#d97706", bold=True, min_w=190)[0])
    f.append(textbox(bx1 + bw1 / 2, by1 + 255, "Початковий заряд C:\n0.00 В (розряджений)", size=12, fill="#fee2e2", stroke="#ef4444", color=POS, bold=True, min_w=190)[0])

    # Середній блок: Бар'єр CMOS
    bx2, by2, bw2, bh2 = 320, 40, 240, 300
    f.append(rect(bx2, by2, bw2, bh2, fill="#fef2f2", stroke="#f87171", sw=1.5, rx=8))
    f.append(text(bx2 + bw2 / 2, by2 + 28, "Кремнієвий бар'єр", size=15, bold=True, color=POS))
    f.append(text(bx2 + bw2 / 2, by2 + 48, "(Стандартні CMOS DC-DC)", size=12, color=MUTED, italic=True))

    f.append(textbox(bx2 + bw2 / 2, by2 + 110, "Поріг затвора MOSFET:\nV_th ≈ 0.40 – 0.70 В", size=13, fill="#fee2e2", stroke="#ef4444", bold=True, min_w=200)[0])
    f.append(textbox(bx2 + bw2 / 2, by2 + 185, "Логіка ШІМ та драйвери:\nV_dd ≥ 1.20 – 1.80 В", size=13, fill="#fee2e2", stroke="#ef4444", bold=True, min_w=200)[0])
    f.append(textbox(bx2 + bw2 / 2, by2 + 255, "СТАН: ЗАБЛОКОВАНО\nКлючі вимкнені, такту нема", size=12, fill="#ffffff", stroke="#dc2626", color=POS, bold=True, min_w=200)[0])

    # Правий блок: Рішення — Холодний старт на збідненому JFET
    bx3, by3, bw3, bh3 = 610, 40, 240, 300
    f.append(rect(bx3, by3, bw3, bh3, fill="#f0fdf4", stroke="#4ade80", sw=1.5, rx=8))
    f.append(text(bx3 + bw3 / 2, by3 + 28, "Холодний старт", size=15, bold=True, color=FIELD))
    f.append(text(bx3 + bw3 / 2, by3 + 48, "(Normally-on JFET + Тр-р)", size=12, color=MUTED, italic=True))

    f.append(textbox(bx3 + bw3 / 2, by3 + 110, "Канал відкритий при V_GS=0\nСтрум тече від 20 мВ", size=13, fill="#dcfce7", stroke="#22c55e", bold=True, min_w=190)[0])
    f.append(textbox(bx3 + bw3 / 2, by3 + 185, "Автотрансформатор 1:N\nПідйом до 2.0 В у C_aux", size=13, fill="#dcfce7", stroke="#22c55e", bold=True, min_w=190)[0])
    f.append(textbox(bx3 + bw3 / 2, by3 + 255, "Пробудження CMOS\nПеремикання на main boost", size=12, fill="#ffffff", stroke="#16a34a", color=FIELD, bold=True, min_w=190)[0])

    # Стрілки між блоками
    f.append(arrow(bx1 + bw1 + 5, 140, bx2 - 5, 140, color=POS, sw=2))
    f.append(arrow(bx2 + bw2 + 5, 180, bx3 - 5, 180, color=FIELD, sw=2))

    render(os.path.join(IMG_DIR, "cold-start-dilemma.svg"), w, h, "".join(f))


def fig_meissner_jfet_oscillator():
    """Фігура 2: Схемотехніка автогенератора Мейснера на JFET та етапи його роботи."""
    w, h = 940, 420
    f = []

    # Фон
    f.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0))

    # Ліва половина: Принципова схема
    sx, sy, sw_box, sh_box = 20, 20, 470, 380
    f.append(rect(sx, sy, sw_box, sh_box, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(sx + sw_box / 2, sy + 25, "Схема релаксаційного JFET-автогенератора", size=14, bold=True, color=INK))

    # Джерело V_in
    f.append(textbox(sx + 45, sy + 130, "V_in\n(20 мВ)", size=12, fill="#fef3c7", stroke="#d97706", bold=True, min_w=60)[0])
    f.append(line(sx + 75, sy + 130, sx + 115, sy + 130, color=LINE, sw=1.8))

    # Трансформатор / Котушки
    f.append(rect(sx + 115, sy + 70, 75, 160, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=4))
    f.append(text(sx + 152, sy + 95, "Тр-р 1:N", size=12, bold=True, color=INK))
    f.append(text(sx + 152, sy + 115, "L_p : L_s", size=11, color=MUTED))
    f.append(circle(sx + 130, sy + 140, 3, fill=POS, stroke=POS))
    f.append(circle(sx + 175, sy + 140, 3, fill=POS, stroke=POS))
    f.append(text(sx + 152, sy + 160, "1 : 50", size=12, bold=True, color=FIELD))

    # JFET транзистор (Depletion N-JFET)
    f.append(rect(sx + 235, sy + 120, 55, 75, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=4))
    f.append(text(sx + 262, sy + 145, "JFET", size=12, bold=True, color=INK))
    f.append(text(sx + 262, sy + 165, "N-канал", size=10, color=MUTED))
    f.append(text(sx + 262, sy + 180, "(Збіднений)", size=9, color=POS))

    # З'єднання первинної обмотки до стоку D
    f.append(line(sx + 190, sy + 130, sx + 235, sy + 130, color=LINE, sw=1.8))
    # Витік S на землю
    f.append(line(sx + 262, sy + 195, sx + 262, sy + 290, color=LINE, sw=1.8))
    f.append(line(sx + 242, sy + 290, sx + 282, sy + 290, color=LINE, sw=2))
    f.append(line(sx + 249, sy + 294, sx + 275, sy + 294, color=LINE, sw=1.5))
    f.append(line(sx + 256, sy + 298, sx + 268, sy + 298, color=LINE, sw=1))

    # Зворотний зв'язок: вторинна обмотка -> C_g -> Затвор G
    f.append(line(sx + 152, sy + 230, sx + 152, sy + 270, color=LINE, sw=1.8))
    f.append(line(sx + 152, sy + 270, sx + 210, sy + 270, color=LINE, sw=1.8))
    # C_g конденсатор
    f.append(textbox(sx + 215, sy + 240, "C_gate", size=10, fill="#ffffff", stroke="#64748b", min_w=40)[0])
    f.append(line(sx + 215, sy + 225, sx + 215, sy + 160, color=LINE, sw=1.8))
    f.append(line(sx + 215, sy + 160, sx + 235, sy + 160, color=LINE, sw=1.8))

    # Діод Шотткі на виході вторинної обмотки
    f.append(line(sx + 190, sy + 85, sx + 310, sy + 85, color=LINE, sw=1.8))
    f.append(textbox(sx + 335, sy + 85, "Діод Schottky", size=10, fill="#ffffff", stroke="#ef4444", min_w=65)[0])
    f.append(line(sx + 370, sy + 85, sx + 415, sy + 85, color=LINE, sw=1.8))
    f.append(line(sx + 415, sy + 85, sx + 415, sy + 150, color=LINE, sw=1.8))

    # Накопичувальний C_aux
    f.append(textbox(sx + 415, sy + 190, "C_aux\n(1–10 мкФ)", size=11, fill="#dcfce7", stroke="#22c55e", bold=True, min_w=60)[0])
    f.append(line(sx + 415, sy + 225, sx + 415, sy + 290, color=LINE, sw=1.8))
    f.append(line(sx + 400, sy + 290, sx + 430, sy + 290, color=LINE, sw=2))

    # Вихід V_aux
    f.append(arrow(sx + 370, sy + 65, sx + 440, sy + 65, color=FIELD, sw=2))
    f.append(text(sx + 405, sy + 50, "V_aux → 2.0 В", size=11, bold=True, color=FIELD))

    # Права половина: Фази автоколивань
    px, py, pw, ph = 510, 20, 410, 380
    f.append(rect(px, py, pw, ph, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(px + pw / 2, py + 25, "4 Фази автоколивань генератора", size=14, bold=True, color=INK))

    phases = [
        ("1. Початковий струм", "V_GS=0 → канал відкритий, струм у первинній L_p наростає від 20 мВ.", "#f8fafc", "#94a3b8"),
        ("2. Прямий додатний зв'язок", "Трансформатор наводить +V на затворі, лавиноподібно відкриваючи JFET.", "#fef3c7", "#d97706"),
        ("3. Насичення та відсічка", "di/dt падає, полярність L_s змінюється на різко негативну (-V_p), JFET миттєво запирається.", "#fee2e2", "#ef4444"),
        ("4. Flyback-викид у C_aux", "Магнітна енергія вторинної обмотки через діод заряджає шину V_aux до 2 В.", "#f0fdf4", "#22c55e"),
    ]

    for i, (title, desc, fill_c, strk_c) in enumerate(phases):
        item_y = py + 55 + i * 76
        f.append(rect(px + 15, item_y, pw - 30, 66, fill=fill_c, stroke=strk_c, sw=1.2, rx=6))
        f.append(text(px + 25, item_y + 20, title, size=12, bold=True, color=INK, anchor="start"))
        f.append(fitbox(px + 25, item_y + 28, pw - 50, 32, desc, size=11, color=MUTED, fill=fill_c, stroke=fill_c))

    render(os.path.join(IMG_DIR, "meissner-jfet-oscillator.svg"), w, h, "".join(f))


def fig_storage_technologies_comparison():
    """Фігура 3: Порівняльна матриця накопичувачів енергії мікрозбирачів."""
    w, h = 840, 380
    f = []

    # Заголовок
    f.append(text(w / 2, 25, "Порівняння накопичувачів для мікроенергетичних систем", size=16, bold=True, color=INK))

    # 3 колонки: EDLC Суперконденсатор, Танталовий/Керамічний MLCC, Твердотільна мікробатарея
    cols = [
        {
            "x": 30, "w": 240, "title": "Суперконденсатор EDLC", "sub": "Подвійний шар (іонний)",
            "header_bg": "#fef3c7", "header_stroke": "#f59e0b",
            "items": [
                ("Ємність", "0.01 – 10 Ф (Дуже велика)", FIELD),
                ("Струм витоку", "1 – 50 мкА (Високий!)", POS),
                ("Внутрішній ESR", "0.1 – 5 Ом (Низький)", FIELD),
                ("Ресурс циклів", "> 1 000 000 циклів", FIELD),
                ("Саморозряд", "Дні / тижні", POS),
                ("Краще для", "Потужні імпульси > 100 мА", INK),
            ]
        },
        {
            "x": 300, "w": 240, "title": "MLCC / Тантал / Плівка", "sub": "Твердий діелектрик",
            "header_bg": "#f0fdf4", "header_stroke": "#22c55e",
            "items": [
                ("Ємність", "10 – 470 мкФ (Помірна)", MUTED),
                ("Струм витоку", "< 1 – 10 нА (Мізерний)", FIELD),
                ("Внутрішній ESR", "< 0.05 Ом (Наднизький)", FIELD),
                ("Ресурс циклів", "Необмежений (∞)", FIELD),
                ("Саморозряд", "Місяці / роки", FIELD),
                ("Краще для", "Мікропотужний збір < 50 мкВт", FIELD),
            ]
        },
        {
            "x": 570, "w": 240, "title": "Твердотільна батарея", "sub": "Тонкоплівковий LiPON / LIC",
            "header_bg": "#eff6ff", "header_stroke": "#3b82f6",
            "items": [
                ("Ємність", "0.1 – 5 мА·год (Висока енергія)", FIELD),
                ("Струм витоку", "5 – 50 нА (Дуже низький)", FIELD),
                ("Внутрішній ESR", "50 – 500 Ом (Високий)", POS),
                ("Ресурс циклів", "5 000 – 10 000 циклів", MUTED),
                ("Саморозряд", "Роки", FIELD),
                ("Краще для", "Компактне тривале живлення", INK),
            ]
        }
    ]

    for col in cols:
        cx, cw = col["x"], col["w"]
        # Рамка всієї колонки
        f.append(rect(cx, 45, cw, 315, fill="#f8fafc", stroke="#e2e8f0", sw=1.5, rx=8))
        # Заголовок колонки
        f.append(rect(cx, 45, cw, 55, fill=col["header_bg"], stroke=col["header_stroke"], sw=1.5, rx=8))
        f.append(text(cx + cw / 2, 70, col["title"], size=13, bold=True, color=INK))
        f.append(text(cx + cw / 2, 88, col["sub"], size=11, color=MUTED, italic=True))

        # Рядки параметрів
        for r_idx, (p_name, p_val, p_col) in enumerate(col["items"]):
            ry = 110 + r_idx * 40
            f.append(rect(cx + 8, ry, cw - 16, 34, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
            f.append(text(cx + 16, ry + 21, p_name + ":", size=11, bold=True, color=MUTED, anchor="start"))
            f.append(text(cx + cw - 16, ry + 21, p_val, size=11, bold=True, color=p_col, anchor="end"))

    render(os.path.join(IMG_DIR, "storage-technologies-comparison.svg"), w, h, "".join(f))


def fig_hysteretic_power_path():
    """Фігура 4: Гістерезисне керування живленням (Voltage Supervisor & Power Path)."""
    w, h = 900, 400
    f = []

    # Фон
    f.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0))

    # Лівий блок: Схема супервізора та ключа Power Path
    sx, sy, sw_b, sh_b = 20, 20, 420, 360
    f.append(rect(sx, sy, sw_b, sh_b, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(sx + sw_b / 2, sy + 25, "Схема гістерезисного Power Path", size=14, bold=True, color=INK))

    # Накопичувач C_store
    f.append(textbox(sx + 60, sy + 90, "C_storage\n(Накопичувач)", size=11, fill="#dcfce7", stroke="#22c55e", bold=True, min_w=85)[0])
    f.append(line(sx + 105, sy + 90, sx + 150, sy + 90, color=LINE, sw=2))

    # Ключ Power Path (PMOS)
    f.append(rect(sx + 150, sy + 65, 80, 50, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=6))
    f.append(text(sx + 190, sy + 88, "PMOS Ключ", size=11, bold=True, color=INK))
    f.append(text(sx + 190, sy + 104, "I_off < 1 нА", size=10, color=POS))

    # Вихід до навантаження (MCU + Radio)
    f.append(arrow(sx + 230, sy + 90, sx + 295, sy + 90, color=FIELD, sw=2))
    f.append(textbox(sx + 345, sy + 90, "V_MCU\n(Навантаження)", size=11, fill="#eff6ff", stroke="#3b82f6", bold=True, min_w=85)[0])

    # Нанопотужний супервізор напруги
    f.append(rect(sx + 60, sy + 180, 300, 150, fill="#ffffff", stroke="#64748b", sw=1.5, rx=8))
    f.append(text(sx + 210, sy + 205, "Nano-Power Supervisor (I_q < 50 нА)", size=12, bold=True, color=INK))

    f.append(textbox(sx + 130, sy + 255, "V_high = 3.3 В\n(Поріг увімкнення)", size=11, fill="#fef3c7", stroke="#d97706", bold=True, min_w=115)[0])
    f.append(textbox(sx + 280, sy + 255, "V_low = 2.0 В\n(Поріг вимкнення)", size=11, fill="#fee2e2", stroke="#ef4444", bold=True, min_w=115)[0])

    # Зв'язок від накопичувача до супервізора
    f.append(line(sx + 105, sy + 90, sx + 105, sy + 180, color=LINE, sw=1.5, dash="4,3"))
    # Керуючий вихід до PMOS ключа
    f.append(arrow(sx + 190, sy + 180, sx + 190, sy + 115, color=POS, sw=1.8))
    f.append(text(sx + 235, sy + 150, "Power Good", size=10, bold=True, color=FIELD))

    # Права половина: Часова діаграма V_store та струму навантаження
    gx, gy, gw, gh = 460, 20, 420, 360
    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(gx + gw / 2, gy + 25, "Енергетичні цикли накопичувача", size=14, bold=True, color=INK))

    # Осі графіка
    f.append(line(gx + 40, gy + 175, gx + gw - 20, gy + 175, color="#94a3b8", sw=1.5))  # вісь t
    f.append(line(gx + 40, gy + 175, gx + 40, gy + 50, color="#94a3b8", sw=1.5))       # вісь V

    f.append(text(gx + 40, gy + 42, "V_store", size=11, bold=True, color=INK))
    f.append(text(gx + gw - 15, gy + 190, "Час t", size=11, color=MUTED))

    # Рівні V_high та V_low
    f.append(line(gx + 40, gy + 65, gx + gw - 20, gy + 65, color="#f59e0b", sw=1, dash="4,4"))
    f.append(text(gx + 25, gy + 69, "3.3 В", size=10, color="#d97706", bold=True))
    f.append(text(gx + gw - 50, gy + 60, "V_high", size=10, color="#d97706", bold=True))

    f.append(line(gx + 40, gy + 125, gx + gw - 20, gy + 125, color="#ef4444", sw=1, dash="4,4"))
    f.append(text(gx + 25, gy + 129, "2.0 В", size=10, color="#dc2626", bold=True))
    f.append(text(gx + gw - 50, gy + 120, "V_low", size=10, color="#dc2626", bold=True))

    # Крива заряду/розряду V_store
    # Старт від 0 до V_high (повільний заряд мікрострумом)
    f.append(line(gx + 40, gy + 175, gx + 150, gy + 65, color=FIELD, sw=2.5))
    # Стрімкий розряд при роботі MCU (імпульс 20 мА)
    f.append(line(gx + 150, gy + 65, gx + 170, gy + 125, color=POS, sw=2.5))
    # Повторний заряд
    f.append(line(gx + 170, gy + 125, gx + 270, gy + 65, color=FIELD, sw=2.5))
    # Повторний розряд
    f.append(line(gx + 270, gy + 65, gx + 290, gy + 125, color=POS, sw=2.5))
    # Повторний заряд
    f.append(line(gx + 290, gy + 125, gx + 385, gy + 65, color=FIELD, sw=2.5))

    # Підписи під графіком
    f.append(textbox(gx + 105, gy + 235, "Фаза накопичення\n(I_in ≈ 20 мкА,\nMCU вимкнено)", size=10, fill="#f0fdf4", stroke="#22c55e", min_w=110)[0])
    f.append(textbox(gx + 225, gy + 235, "Імпульс передачі\n(I_load = 25 мА,\n15 мс активності)", size=10, fill="#fee2e2", stroke="#ef4444", min_w=110)[0])
    f.append(textbox(gx + 345, gy + 235, "Цикл повторюється\nз корисним запасом\nE = ½C(V_h² - V_l²)", size=10, fill="#eff6ff", stroke="#3b82f6", min_w=110)[0])

    # Нижній висновок
    f.append(rect(gx + 15, gy + 300, gw - 30, 42, fill="#f8fafc", stroke="#94a3b8", sw=1, rx=4))
    f.append(text(gx + gw / 2, gy + 325, "Гістерезис захищає від зациклення Brownout Reset", size=11, bold=True, color=INK))

    render(os.path.join(IMG_DIR, "hysteretic-power-path.svg"), w, h, "".join(f))


if __name__ == "__main__":
    fig_cold_start_dilemma()
    fig_meissner_jfet_oscillator()
    fig_storage_technologies_comparison()
    fig_hysteretic_power_path()
    print("Всі 4 фігури успішно згенеровано у img/!")
