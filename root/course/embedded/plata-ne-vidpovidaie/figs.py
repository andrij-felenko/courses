# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Плата не відповідає: дерево пошуку».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Три фази оживлення плати ─────────────────────────────────────────────
def fig_bringup_phases():
    W, H = 840, 370
    el = []
    el.append(text(W/2, 26, "Три фази оживлення плати (Bring-up Sequence)", size=17, bold=True))

    pw, ph = 240, 240
    y0 = 60

    # Фаза 0
    x0 = 30
    el.append(rect(x0, y0, pw, ph, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    el.append(rect(x0, y0, pw, 38, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=8))
    el.append(text(x0 + pw/2, y0 + 24, "Фаза 0: Холодні перевірки", size=13, bold=True, color=INK))
    
    items0 = [
        "• Огляд під мікроскопом",
        "• Спайки ніжок (solder bridges)",
        "• Орієнтація ключа Pin 1",
        "• Полярність діодів і танталу",
        "• Опір рейок живлення до GND",
        "• Тест діодним падінням (ESD)"
    ]
    for i, it in enumerate(items0):
        el.append(text(x0 + 14, y0 + 68 + i * 26, it, size=11, anchor="start", color=INK))

    # Стрілка 0 -> 1
    el.append(arrow(x0 + pw + 4, y0 + ph/2, x0 + pw + 36, y0 + ph/2, color=LINE, sw=2.0))
    el.append(text(x0 + pw + 20, y0 + ph/2 - 10, "R_GND > 100 Ω", size=9, color=MUTED, anchor="middle"))

    # Фаза 1
    x1 = 300
    el.append(rect(x1, y0, pw, ph, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    el.append(rect(x1, y0, pw, 38, fill="#fef3c7", stroke=LINE, sw=1.5, rx=8))
    el.append(text(x1 + pw/2, y0 + 24, "Фаза 1: Перше живлення", size=13, bold=True, color=INK))

    items1 = [
        "• БЖ з лімітом струму (50–100 мА)",
        "• Контроль режиму CC / CV",
        "• Осцилограма рейок LDO / DC-DC",
        "• Відсутність дзвону та пульсацій",
        "• Черговість рейок (Sequencing)",
        "• Тепловізор або тест спиртом"
    ]
    for i, it in enumerate(items1):
        el.append(text(x1 + 14, y0 + 68 + i * 26, it, size=11, anchor="start", color=INK))

    # Стрілка 1 -> 2
    el.append(arrow(x1 + pw + 4, y0 + ph/2, x1 + pw + 36, y0 + ph/2, color=LINE, sw=2.0))
    el.append(text(x1 + pw + 20, y0 + ph/2 - 10, "Напруги OK", size=9, color=MUTED, anchor="middle"))

    # Фаза 2
    x2 = 570
    el.append(rect(x2, y0, pw, ph, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    el.append(rect(x2, y0, pw, 38, fill="#dcfce7", stroke=LINE, sw=1.5, rx=8))
    el.append(text(x2 + pw/2, y0 + 24, "Фаза 2: Пульс MCU і SWD", size=13, bold=True, color=INK))

    items2 = [
        "• Рівень лінії ресету (NRST > 2.8V)",
        "• Стан конфігурації BOOT0 / BOOT1",
        "• Напруга внутрішнього ядра VCAP",
        "• Тактування кварцу (щуп 10x / MCO)",
        "• Лінії SWDIO / SWCLK / VREF",
        "• Контакт відлагоджувача з ядром"
    ]
    for i, it in enumerate(items2):
        el.append(text(x2 + 14, y0 + 68 + i * 26, it, size=11, anchor="start", color=INK))

    # Нижня підказка
    note = (
        "Головне правило безпечного запуску: жоден наступний крок не виконується,\n"
        "доки попередній не підтверджено прямим вимірюванням."
    )
    el.append(fitbox(30, 312, 780, 44, note, size=11.5, fill="#eff6ff", stroke=NEG))

    render(os.path.join(IMG, "bringup-phases.svg"), W, H, *el)


# ── 2. Холодні перевірки: візуальні пастки та вимірювання рейок ─────────────
def fig_cold_check_zones():
    W, H = 840, 430
    el = []
    el.append(text(W/2, 26, "Холодні перевірки: типові монтажні пастки та продзвонка", size=17, bold=True))

    col_w = 250
    y0 = 60
    h_box = 345

    # Колонка 1: Мікроскоп і QFP/QFN
    x1 = 25
    el.append(rect(x1, y0, col_w, h_box, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    el.append(rect(x1, y0, col_w, 32, fill="#f1f5f9", stroke=LINE, sw=1.4, rx=6))
    el.append(text(x1 + col_w/2, y0 + 20, "1. Мікроскоп: виводи й ключ", size=12, bold=True))

    # Схематичний чип QFP
    cx, cy = x1 + col_w/2, y0 + 95
    el.append(rect(cx - 32, cy - 32, 64, 64, fill="#1e293b", stroke=LINE, sw=1.5, rx=3))
    el.append(circle(cx - 22, cy - 22, 3, fill="#f8fafc", stroke="#f8fafc", sw=1))
    el.append(text(cx, cy + 4, "MCU", size=11, color="#f8fafc", bold=True))
    el.append(text(cx - 22, cy - 36, "Ключ (Pin 1)", size=9.5, color=POS, bold=True))

    # Виводи збоку і місток припою
    for offset in (-18, -9, 0, 9, 18):
        el.append(line(cx + 32, cy + offset, cx + 44, cy + offset, color=LINE, sw=1.8))
        el.append(line(cx - 44, cy + offset, cx - 32, cy + offset, color=LINE, sw=1.8))
    # Спайка
    el.append(rect(cx + 35, cy - 2, 7, 13, fill=POS, stroke=POS, sw=1))
    el.append(text(cx + 48, cy + 18, "Спайка", size=9.5, color=POS, anchor="start", bold=True))

    note1 = (
        "• Неправильний кут Pin 1 =\n"
        "  миттєва загибель чіпа при старті.\n"
        "• Мости припою між виводами\n"
        "  0.5 мм кроку в QFN / QFP.\n"
        "• Tombstone («надгробок»):\n"
        "  відрив SMD 0402 одним кінцем."
    )
    el.append(fitbox(x1 + 10, y0 + 180, col_w - 20, 145, note1, size=10.5, fill="#f8fafc", stroke=MUTED))

    # Колонка 2: Полярність компонентів
    x2 = 295
    el.append(rect(x2, y0, col_w, h_box, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    el.append(rect(x2, y0, col_w, 32, fill="#f1f5f9", stroke=LINE, sw=1.4, rx=6))
    el.append(text(x2 + col_w/2, y0 + 20, "2. Полярність: пастка танталу", size=12, bold=True))

    # Порівняння Тантал vs Алюміній
    tx = x2 + col_w/2
    # Тантал
    el.append(rect(tx - 65, y0 + 52, 60, 30, fill="#d97706", stroke=LINE, sw=1.2, rx=2))
    el.append(rect(tx - 65, y0 + 52, 14, 30, fill="#fef08a", stroke=LINE, sw=1.0, rx=1))
    el.append(text(tx - 58, y0 + 71, "+", size=12, bold=True, color="#854d0e"))
    el.append(text(tx - 30, y0 + 71, "Тантал", size=10, color="#ffffff", bold=True))
    el.append(text(tx - 35, y0 + 96, "Смужка = АНОД (+)", size=9.5, color=POS, bold=True))

    # Електроліт
    el.append(circle(tx + 45, y0 + 67, 16, fill="#94a3b8", stroke=LINE, sw=1.2))
    el.append(rect(tx + 29, y0 + 51, 10, 32, fill="#334155", stroke="none"))
    el.append(text(tx + 34, y0 + 71, "−", size=12, bold=True, color="#ffffff"))
    el.append(text(tx + 45, y0 + 96, "Смужка = КАТОД (−)", size=9.5, color=NEG, bold=True))

    note2 = (
        "• Тантал: смуга на корпусі — це\n"
        "  плюс (+). Переполюсовка танталу\n"
        "  веде до пробою з полум'ям.\n"
        "• Алюмінієвий електроліт:\n"
        "  смуга на корпусі — це мінус (−).\n"
        "• Діоди: смуга катода (K) має\n"
        "  дивитися в бік вищого потенціалу."
    )
    el.append(fitbox(x2 + 10, y0 + 180, col_w - 20, 145, note2, size=10.5, fill="#f8fafc", stroke=MUTED))

    # Колонка 3: Опори рейок живлення
    x3 = 565
    el.append(rect(x3, y0, col_w, h_box, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    el.append(rect(x3, y0, col_w, 32, fill="#f1f5f9", stroke=LINE, sw=1.4, rx=6))
    el.append(text(x3 + col_w/2, y0 + 20, "3. Продзвонка рейок на GND", size=12, bold=True))

    # Мультиметр
    mx = x3 + col_w/2
    el.append(rect(mx - 45, y0 + 46, 90, 48, fill="#fbbf24", stroke=LINE, sw=1.5, rx=5))
    el.append(rect(mx - 36, y0 + 52, 72, 20, fill="#ecfccb", stroke=LINE, sw=1.0, rx=2))
    el.append(text(mx, y0 + 66, "0.482 V / >10k", size=10, bold=True, color="#1e293b"))
    el.append(circle(mx, y0 + 84, 4, fill="#1e293b", stroke=LINE, sw=1))

    note3 = (
        "• Опір < 1–2 Ом = тверде КЗ\n"
        "  (металевий місток, пробитий TVS).\n"
        "• Зростаючий опір від 0 до сотен кОм =\n"
        "  нормальний заряд ємностей MLCC.\n"
        "• Низький опір ядер (1.0V) = 15–50 Ом\n"
        "  для FPGA/MPU є нормою, але для\n"
        "  MCU 3.3V це дефект кристала.\n"
        "• Diode mode: падіння 0.3–0.6 В\n"
        "  підтверджує цілісність ESD-діодів."
    )
    el.append(fitbox(x3 + 10, y0 + 106, col_w - 20, 220, note3, size=10, fill="#f8fafc", stroke=MUTED))

    render(os.path.join(IMG, "cold-check-zones.svg"), W, H, *el)


# ── 3. Осцилограма на шині живлення: норма проти самозбудження ───────────────
def fig_power_rail_oscilloscope():
    W, H = 820, 400
    el = []
    el.append(text(W/2, 26, "Осцилографічний контроль шини 3.3V: норма проти самозбудження", size=17, bold=True))

    def scope_screen(x0, y0, w, h, title, is_good):
        out = rect(x0, y0, w, h, fill="#0f172a", stroke=LINE, sw=2, rx=6)
        # сітка
        for gx in range(1, 6):
            out += line(x0 + gx * (w/6), y0, x0 + gx * (w/6), y0 + h, color="#1e293b", sw=1, dash="2,4")
        for gy in range(1, 5):
            out += line(x0, y0 + gy * (h/5), x0 + w, y0 + gy * (h/5), color="#1e293b", sw=1, dash="2,4")
        
        # Лінія сигналу
        pts = []
        mid_y = y0 + h * 0.38
        if is_good:
            import random
            random.seed(42)
            for i in range(0, int(w)):
                noise = (random.random() - 0.5) * 3
                pts.append((x0 + i, mid_y + noise))
            out += '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (
                " ".join("%.1f,%.1f" % (x, y) for x, y in pts), FIELD)
            out += text(x0 + 14, y0 + 24, "3.32 V DC (Чистий вихід LDO)", size=11, color=FIELD, anchor="start", bold=True)
            out += text(x0 + 14, y0 + 40, "Пульсації < 5 мВ", size=10, color="#94a3b8", anchor="start")
        else:
            import math
            for i in range(0, int(w)):
                osc = math.sin(i * 0.18) * 32 + (math.sin(i * 0.04) * 6)
                pts.append((x0 + i, mid_y + osc))
            out += '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (
                " ".join("%.1f,%.1f" % (x, y) for x, y in pts), POS)
            out += text(x0 + 14, y0 + 24, "Генерація LDO (Самозбудження петлі)", size=11, color=POS, anchor="start", bold=True)
            out += text(x0 + 14, y0 + 40, "V_pp = 650 мВ @ 850 кГц (Мультиметр покаже 3.3V!)", size=10, color="#fca5a5", anchor="start")

        out += text(x0 + w/2, y0 + h + 22, title, size=12, bold=True, color=INK)
        return out

    el.append(scope_screen(40, 60, 350, 200, "Стабільне живлення: конденсатори підібрані вірно", True))
    el.append(scope_screen(430, 60, 350, 200, "Нестабільне живлення: невідповідний ESR кераміки", False))

    note = (
        "Пастка цифрового вольтметра: звичайний мультиметр вимірює постійну напругу інтегруванням (DC AVG)\n"
        "і покаже ідеальні 3.30 В навіть тоді, коли стабілізатор генерує розмах 1 В на мегагерцових частотах.\n"
        "Мікроконтролер при цьому безперервно скидається внутрішнім супервізором Brown-out Detector."
    )
    el.append(fitbox(40, 305, 740, 68, note, size=11.5, fill="#fffbeb", stroke="#f59e0b"))

    render(os.path.join(IMG, "power-rail-oscilloscope.svg"), W, H, *el)


# ── 4. Вплив щупа осцилографа на кварцовий резонатор ─────────────────────────
def fig_crystal_probing_impact():
    W, H = 840, 420
    el = []
    el.append(text(W/2, 26, "Вплив щупа осцилографа на генератор Пірса (Pierce Oscillator)", size=17, bold=True))

    box_w = 360
    y0 = 60
    bh = 225

    # Ліва схема: Щуп 1X (Зрив коливань)
    x1 = 40
    el.append(rect(x1, y0, box_w, bh, fill="#ffffff", stroke=POS, sw=1.6, rx=6))
    el.append(rect(x1, y0, box_w, 32, fill="#fee2e2", stroke=POS, sw=1.6, rx=6))
    el.append(text(x1 + box_w/2, y0 + 20, "Щуп 1X: Смерть генерації (Зрив)", size=12, bold=True, color=POS))

    # Схематичний інвертор та кварц
    ix, iy = x1 + 80, y0 + 95
    el.append(rect(ix - 20, iy - 20, 40, 40, fill="#f1f5f9", stroke=LINE, sw=1.5))
    el.append(text(ix, iy + 4, "INV", size=10, bold=True))

    # Кварц угорі
    el.append(line(ix - 20, iy, ix - 35, iy, color=LINE, sw=1.5))
    el.append(line(ix - 35, iy, ix - 35, iy - 40, color=LINE, sw=1.5))
    el.append(line(ix - 35, iy - 40, ix - 15, iy - 40, color=LINE, sw=1.5))
    el.append(rect(ix - 15, iy - 48, 30, 16, fill="#cbd5e1", stroke=LINE, sw=1.2))
    el.append(line(ix + 15, iy - 40, ix + 35, iy - 40, color=LINE, sw=1.5))
    el.append(line(ix + 35, iy - 40, ix + 35, iy, color=LINE, sw=1.5))
    el.append(line(ix + 35, iy, ix + 20, iy, color=LINE, sw=1.5))
    el.append(text(ix, iy - 40 + 4, "XTAL", size=9, bold=True))

    # Конденсатори C1, C2
    el.append(line(ix - 35, iy, ix - 35, iy + 25, color=LINE, sw=1.5))
    el.append(line(ix - 45, iy + 25, ix - 25, iy + 25, color=LINE, sw=1.5))
    el.append(line(ix - 45, iy + 30, ix - 25, iy + 30, color=LINE, sw=1.5))
    el.append(text(ix - 35, iy + 48, "C₁=12пФ", size=9.5, anchor="middle"))

    el.append(line(ix + 35, iy, ix + 35, iy + 25, color=LINE, sw=1.5))
    el.append(line(ix + 25, iy + 25, ix + 45, iy + 25, color=LINE, sw=1.5))
    el.append(line(ix + 25, iy + 30, ix + 45, iy + 30, color=LINE, sw=1.5))
    el.append(text(ix + 35, iy + 48, "C₂=12пФ", size=9.5, anchor="middle"))

    # Підключення щупа 1X
    px = ix + 120
    el.append(line(ix + 35, iy, px, iy, color=POS, sw=2.0, dash="3,3"))
    el.append(circle(px, iy, 4, fill=POS, stroke=POS, sw=1))
    el.append(rect(px + 8, iy - 28, 110, 56, fill="#fff1f2", stroke=POS, sw=1.4, rx=4))
    el.append(text(px + 63, iy - 12, "Щуп 1X", size=11, bold=True, color=POS))
    el.append(text(px + 63, iy + 4, "C_щупа ≈ 100 пФ!", size=10, bold=True, color=POS))
    el.append(text(px + 63, iy + 18, "R_вх = 1 МОм", size=9.5, color=MUTED))

    el.append(text(x1 + box_w/2, y0 + 195, "Ємність щупа (100 пФ) ≫ C₂ (12 пФ) → зрив коливань", size=9.5, color=POS, bold=True))

    # Права схема: Безпечні методи вимірювання
    x2 = 440
    el.append(rect(x2, y0, box_w, bh, fill="#ffffff", stroke=FIELD, sw=1.6, rx=6))
    el.append(rect(x2, y0, box_w, 32, fill="#dcfce7", stroke=FIELD, sw=1.6, rx=6))
    el.append(text(x2 + box_w/2, y0 + 20, "Безпечні методи контролю тактування", size=12, bold=True, color=FIELD))

    safe_methods = [
        "1. Дільник щупа 1:10 (10X):",
        "   Ємність щупа падає до 10–13 пФ (генерація зберігається).",
        "2. Активний FET-пробник:",
        "   Паразитна ємність < 0.8 пФ, опір > 1 МОм на 100 МГц.",
        "3. Вивід MCO (Microcontroller Clock Output):",
        "   Прошивка конфігурує буферизований цифровий пін для HSE."
    ]
    for i, sm in enumerate(safe_methods):
        bold = i in (0, 2, 4)
        col = INK if bold else "#334155"
        el.append(text(x2 + 14, y0 + 55 + i * 24, sm, size=10, anchor="start", bold=bold, color=col))

    note4 = (
        "Діагностичне правило: якщо при торканні щупом 1x генерація на OSC_OUT зникає — це НЕ ознака мертвого кварцу.\n"
        "Щуп вніс ємність, що перевищує розрахункову навантажувальну ємність контуру в 8–10 разів.\n"
        "Для достовірної оцінки використовуйте тільки дільник 1:10 на виводі OSC_OUT або буферизований пін MCO."
    )
    el.append(fitbox(40, 310, 760, 78, note4, size=11, fill="#f8fafc", stroke=LINE))

    render(os.path.join(IMG, "crystal-probing-impact.svg"), W, H, *el)


# ── 5. Дерево пошуку несправностей під час першого старту ────────────────────
def fig_troubleshooting_tree():
    W, H = 840, 500
    el = []
    el.append(text(W/2, 26, "Дерево пошуку несправностей під час першого ввімкнення", size=17, bold=True))

    # Корінь
    rx, ry = W/2, 65
    el.append(rect(rx - 160, ry - 18, 320, 36, fill="#1e293b", stroke=LINE, sw=1.5, rx=6))
    el.append(text(rx, ry + 5, "Подача живлення через БЖ (CC = 100 мА)", size=12, color="#ffffff", bold=True))

    # Три головні гілки
    # Гілка 1: Струм у ліміті CC (Ліворуч)
    b1_x = 140
    b1_y = 150
    el.append(line(rx, ry + 18, b1_x, b1_y - 20, color=LINE, sw=1.5))
    el.append(rect(b1_x - 110, b1_y - 20, 220, 40, fill="#fee2e2", stroke=POS, sw=1.5, rx=5))
    el.append(text(b1_x, b1_y - 4, "Струм б'є в ліміт (CC)", size=11, bold=True, color=POS))
    el.append(text(b1_x, b1_y + 12, "Напруга просіла до ~0.2–1.0 В", size=9.5, color=POS))

    # Дія 1
    el.append(arrow(b1_x, b1_y + 20, b1_x, b1_y + 60, color=POS, sw=1.5))
    el.append(rect(b1_x - 115, b1_y + 60, 230, 110, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    el.append(text(b1_x, b1_y + 78, "Тепловізор або тест спиртом", size=11, bold=True, color=POS))
    items_d1 = [
        "• Шукати гарячий чіп / MLCC",
        "• Перевірити полярність танталу",
        "• Демонтувати LDO / супресор",
        "• Оглянути спайки ніжок QFN"
    ]
    for i, it in enumerate(items_d1):
        el.append(text(b1_x - 100, b1_y + 100 + i * 16, it, size=9.5, anchor="start", color=INK))

    # Гілка 2: Струм = 0 мА (Центр)
    b2_x = 420
    b2_y = 150
    el.append(line(rx, ry + 18, b2_x, b2_y - 20, color=LINE, sw=1.5))
    el.append(rect(b2_x - 100, b2_y - 20, 200, 40, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=5))
    el.append(text(b2_x, b2_y - 4, "Струм 0 мА (Обрив)", size=11, bold=True, color="#d97706"))
    el.append(text(b2_x, b2_y + 12, "Схема взагалі не бере струм", size=9.5, color="#d97706"))

    # Дія 2
    el.append(arrow(b2_x, b2_y + 20, b2_x, b2_y + 60, color="#d97706", sw=1.5))
    el.append(rect(b2_x - 105, b2_y + 60, 210, 110, fill="#ffffff", stroke="#d97706", sw=1.2, rx=4))
    el.append(text(b2_x, b2_y + 78, "Перевірка вхідного кола", size=11, bold=True, color="#d97706"))
    items_d2 = [
        "• Самозвідний фюз (PTC / Fuse)",
        "• Захисний діод від переполюсовки",
        "• Кнопка / джампер живлення",
        "• Падіння на вході LDO / DC-DC"
    ]
    for i, it in enumerate(items_d2):
        el.append(text(b2_x - 90, b2_y + 100 + i * 16, it, size=9.5, anchor="start", color=INK))

    # Гілка 3: Струм у нормі (15–40 мА), але MCU мовчить (Праворуч)
    b3_x = 700
    b3_y = 150
    el.append(line(rx, ry + 18, b3_x, b3_y - 20, color=LINE, sw=1.5))
    el.append(rect(b3_x - 110, b3_y - 20, 220, 40, fill="#dbeafe", stroke=NEG, sw=1.5, rx=5))
    el.append(text(b3_x, b3_y - 4, "Струм 15–40 мА (Норма)", size=11, bold=True, color=NEG))
    el.append(text(b3_x, b3_y + 12, "Напруги 3.3V OK, але SWD німий", size=9.5, color=NEG))

    # Дія 3: Вкладене розгалуження
    el.append(arrow(b3_x, b3_y + 20, b3_x, b3_y + 60, color=NEG, sw=1.5))
    el.append(rect(b3_x - 115, b3_y + 60, 230, 240, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    el.append(text(b3_x, b3_y + 78, "Покрокова діагностика MCU", size=11, bold=True, color=NEG))

    steps3 = [
        "1. Лінія NRST: V > 2.8 В?",
        "   Ні → кнопка замкнена / C_rst КЗ",
        "2. Ядро VCAP / VDD_CORE = 1.2V?",
        "   Ні → непропай VCAP / збій LDO",
        "3. BOOT0 притягнутий до GND?",
        "   Ні → чіп завис у системному ROM",
        "4. Спільний GND із ST-Link / J-Link?",
        "   Ні → відсутня спільна опора сигналів",
        "5. Знизити SWD clock до 100 кГц:",
        "   Режим 'Connect under Reset'"
    ]
    for i, st in enumerate(steps3):
        bold = "Ні →" not in st and ("1." in st or "2." in st or "3." in st or "4." in st or "5." in st)
        col = NEG if bold else ("#b91c1c" if "Ні →" in st else INK)
        el.append(text(b3_x - 102, b3_y + 98 + i * 15, st, size=9, anchor="start", bold=bold, color=col))

    # Загальний підсумок знизу
    note_tree = (
        "Золоте правило діагностики: 95% випадків мовчання плати викликані відсутністю спільної землі з відлагоджувачем,\n"
        "затиснутою лінією NRST, перевернутим танталовим конденсатором або плаваючим піном BOOT0."
    )
    el.append(fitbox(25, 430, 790, 52, note_tree, size=11, fill="#eff6ff", stroke=NEG))

    render(os.path.join(IMG, "troubleshooting-tree.svg"), W, H, *el)


if __name__ == "__main__":
    fig_bringup_phases()
    fig_cold_check_zones()
    fig_power_rail_oscilloscope()
    fig_crystal_probing_impact()
    fig_troubleshooting_tree()
    print("OK: 5 figures ->", IMG)
