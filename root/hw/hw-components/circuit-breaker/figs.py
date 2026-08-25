# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми circuit-breaker (Автомат захисту)."""
import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_mcb_anatomy():
    """Фігура 1: Внутрішня будова та кінематика модульного автоматичного вимикача (MCB)."""
    w, h = 900, 520
    frags = []

    # Заголовок
    frags.append(text(w / 2, 26, "Внутрішня будова модульного автоматичного вимикача (MCB)", size=16, bold=True))

    # Корпус автомата
    frags.append(rect(30, 50, 840, 450, fill="#f8fafc", stroke="#64748b", sw=2, rx=12))

    # ── Ліва зона: Струмовий тракт і розчіплювачі ──
    # Вхідна клема
    frags.append(textbox(150, 90, "Верхня вхідна клема (живлення)\nГвинтовий затискач дроту", size=11, pad=6, fill="#e2e8f0", stroke="#475569", sw=1.2)[0])
    frags.append(line(150, 115, 150, 140, color=POS, sw=3))

    # Біметалева пластина (прямокутник розчіплювача)
    frags.append(rect(50, 140, 200, 115, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(150, 162, "Тепловий розчіплювач", size=12, bold=True, color=POS))
    frags.append(text(150, 182, "Біметалева пластина (Інвар + Латунь)", size=10.5, bold=True, color="#991b1b"))
    frags.append(text(150, 200, "Прогин від нагріву струмом I²R", size=10, color="#7f1d1d"))
    frags.append(text(150, 218, "Калібрувальний гвинт уставки", size=10, color=MUTED))
    frags.append(text(150, 238, "Захист від тривалого перевантаження", size=9.5, bold=True, color=POS))

    frags.append(line(150, 255, 150, 280, color=POS, sw=3))

    # Електромагнітний соленоїд
    frags.append(rect(50, 280, 200, 115, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(150, 302, "Електромагнітний розчіплювач", size=11, bold=True, color=NEG))
    frags.append(text(150, 322, "Соленоїдна котушка + шток", size=10.5, bold=True, color="#1e40af"))
    frags.append(text(150, 340, "Електродинамічне втягування плунжера", size=10, color="#1e3a8a"))
    frags.append(text(150, 358, "Прямий удар по контактному важелю", size=10, color=MUTED))
    frags.append(text(150, 378, "Миттєве відсікання КЗ (< 3 мс)", size=9.5, bold=True, color=NEG))

    frags.append(line(150, 395, 150, 420, color=POS, sw=3))

    # Гнучкий мідний провідник
    frags.append(textbox(150, 455, "Гнучкий мідний джгут (косичка)\nСтрум на рухомий контакт", size=10, pad=5, fill="#ffffff", stroke="#94a3b8", sw=1)[0])

    # ── Центральна зона: Механізм замка та важіль ──
    frags.append(rect(280, 75, 270, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(415, 100, "Кінематичний механізм", size=13, bold=True, color="#0f172a"))
    frags.append(text(415, 118, "Механізм вільного розчеплення (Trip-Free)", size=10, color=MUTED))

    # Важіль керування
    frags.append(rect(350, 135, 130, 45, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=6))
    frags.append(text(415, 155, "Рукоятка (ON / OFF)", size=11, bold=True, color="#0f172a"))
    frags.append(text(415, 170, "Ручне зведення / вимкнення", size=9.5, color=MUTED))

    # Вузол зведення
    frags.append(textbox(415, 225, "Важільна система з мертвою точкою\n(Over-center toggle linkage)", size=10.5, pad=6, fill="#f8fafc", stroke="#64748b", sw=1.2)[0])

    # Спускова рейка
    frags.append(textbox(415, 305, "Спускова рейка / собачка замка\nСпрацьовує від біметалу або штока соленоїда", size=10, pad=6, fill="#fef3c7", stroke="#d97706", sw=1.2)[0])

    # Силова пружина
    frags.append(textbox(415, 385, "Силова пружина розмикання\nМиттєвий розрив силових контактів", size=10, pad=6, fill="#fee2e2", stroke=POS, sw=1.2)[0])

    # Індикатор положення
    frags.append(textbox(415, 450, "Віконце індикації контактів:\nЧервоний = Замкнено / Зелений = Розімкнено", size=9.5, pad=4, fill="#f0fdf4", stroke=FIELD, sw=1)[0])

    # ── Права зона: Силові контакти та дугогасна камера ──
    frags.append(rect(580, 75, 270, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(715, 100, "Дугогасний тракт", size=13, bold=True, color="#0f172a"))

    # Контактна група
    frags.append(rect(600, 120, 230, 85, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=6))
    frags.append(text(715, 140, "Силова контактна група", size=11, bold=True, color="#b45309"))
    frags.append(text(715, 160, "Рухомий + Нерухомий контакти", size=10.5, color="#78350f"))
    frags.append(text(715, 180, "Накладки зі сплаву Ag-C / Ag-Ni", size=10, color=MUTED))

    # Дугогасні роги
    frags.append(textbox(715, 240, "Дугогасні роги (Arc Runners)\nМагнітне видування дуги F = I × B", size=10.5, pad=6, fill="#fef2f2", stroke=POS, sw=1.2)[0])

    # Деіонна камера
    frags.append(rect(600, 280, 230, 115, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(715, 302, "Деіонна дугогасна камера", size=11, bold=True, color="#1e293b"))
    frags.append(text(715, 322, "Пакет сталевих пластин (De-ion)", size=10, color="#334155"))
    frags.append(text(715, 342, "Поділ на 10-15 мікродуг", size=10, color="#334155"))
    frags.append(text(715, 362, "Підйом напруги V_arc > V_джерела", size=9.5, bold=True, color=POS))
    frags.append(text(715, 380, "Інтенсивне охолодження й деіонізація", size=9, color=MUTED))

    # Вихідний газовідвід і нижня клема
    frags.append(textbox(715, 440, "Газовідвідний дефлектор (іскрогасник)\nВикид деіонізованих газів назовні", size=9.5, pad=4, fill="#f1f5f9", stroke="#94a3b8", sw=1)[0])

    out_path = os.path.join(IMG_DIR, "mcb-internal-anatomy.svg")
    render(out_path, w, h, *frags)
    print(f"Згенеровано {out_path}")


def fig_trip_curves():
    """Фігура 2: Час-струмові характеристики спрацьовування типів B, C, D (IEC/EN 60898-1)."""
    w, h = 900, 520
    frags = []

    frags.append(text(w / 2, 26, "Час-струмові характеристики спрацьовування за стандартом IEC/EN 60898-1", size=16, bold=True))

    ox, oy = 85, 440
    gw, gh = 780, 370

    # Сітка та фон графіка
    frags.append(rect(ox, oy - gh, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))

    # Горизонтальні лінії часу
    y_1h = oy - gh + 35
    y_1m = oy - gh + 130
    y_1s = oy - gh + 230
    y_10ms = oy - gh + 330

    frags.append(line(ox, y_1h, ox + gw, y_1h, color="#e2e8f0", sw=1, dash="4,4"))
    frags.append(line(ox, y_1m, ox + gw, y_1m, color="#e2e8f0", sw=1, dash="4,4"))
    frags.append(line(ox, y_1s, ox + gw, y_1s, color="#e2e8f0", sw=1, dash="4,4"))
    frags.append(line(ox, y_10ms, ox + gw, y_10ms, color="#e2e8f0", sw=1, dash="4,4"))

    frags.append(text(ox - 10, y_1h + 4, "1 год", size=11, color="#64748b", anchor="end"))
    frags.append(text(ox - 10, y_1m + 4, "1 хв", size=11, color="#64748b", anchor="end"))
    frags.append(text(ox - 10, y_1s + 4, "1 с", size=11, color="#64748b", anchor="end"))
    frags.append(text(ox - 10, y_10ms + 4, "10 мс", size=11, color="#64748b", anchor="end"))

    # Вертикальні лінії кратності струму
    x_1 = ox + 45
    x_1_13 = ox + 75
    x_1_45 = ox + 115
    x_3 = ox + 175
    x_5 = ox + 265
    x_10 = ox + 385
    x_20 = ox + 505

    frags.append(line(x_1, oy - gh, x_1, oy, color="#e2e8f0", sw=1, dash="4,4"))
    frags.append(line(x_1_13, oy - gh, x_1_13, oy, color="#fde68a", sw=1.5))
    frags.append(line(x_1_45, oy - gh, x_1_45, oy, color="#fca5a5", sw=1.5))
    frags.append(line(x_3, oy - gh, x_3, oy, color="#cbd5e1", sw=1, dash="4,4"))
    frags.append(line(x_5, oy - gh, x_5, oy, color="#cbd5e1", sw=1, dash="4,4"))
    frags.append(line(x_10, oy - gh, x_10, oy, color="#cbd5e1", sw=1, dash="4,4"))
    frags.append(line(x_20, oy - gh, x_20, oy, color="#cbd5e1", sw=1, dash="4,4"))

    frags.append(text(x_1, oy + 20, "1 · I_n", size=10, color="#64748b"))
    frags.append(text(x_1_13, oy + 36, "1.13 I_n", size=9.5, bold=True, color="#b45309"))
    frags.append(text(x_1_45, oy + 20, "1.45 I_n", size=9.5, bold=True, color=POS))
    frags.append(text(x_3, oy + 20, "3 · I_n", size=10, color="#64748b"))
    frags.append(text(x_5, oy + 20, "5 · I_n", size=10, color="#64748b"))
    frags.append(text(x_10, oy + 20, "10 · I_n", size=10, color="#64748b"))
    frags.append(text(x_20, oy + 20, "20 · I_n", size=10, color="#64748b"))

    # Позначення теплової зони зверху
    frags.append(rect(ox + 40, oy - gh + 15, 120, 50, fill="#fef3c7", stroke="#f59e0b", sw=1.2, rx=6))
    frags.append(text(ox + 100, oy - gh + 35, "Теплова зона", size=11, bold=True, color="#92400e"))
    frags.append(text(ox + 100, oy - gh + 52, "t ∝ 1/I² (біметал)", size=10, color="#b45309"))

    # Зони миттєвого відсікання (Тип B, C, D)
    box_top = y_1s + 10
    box_h = oy - box_top - 15

    # Тип B (3..5 In)
    frags.append(rect(x_3, box_top, x_5 - x_3, box_h, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text((x_3 + x_5) / 2, box_top + 25, "Тип B", size=12, bold=True, color=NEG))
    frags.append(text((x_3 + x_5) / 2, box_top + 45, "3–5 · I_n", size=10.5, bold=True, color="#1e40af"))
    frags.append(text((x_3 + x_5) / 2, box_top + 70, "Обігрівачі, плити,\nдовгі лінії", size=9, color="#1e3a8a"))

    # Тип C (5..10 In)
    frags.append(rect(x_5, box_top, x_10 - x_5, box_h, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text((x_5 + x_10) / 2, box_top + 25, "Тип C", size=12, bold=True, color=FIELD))
    frags.append(text((x_5 + x_10) / 2, box_top + 45, "5–10 · I_n", size=10.5, bold=True, color="#065f46"))
    frags.append(text((x_5 + x_10) / 2, box_top + 70, "Розетки, освітлення,\nдрібні мотори", size=9, color="#064e3b"))

    # Тип D (10..20 In)
    frags.append(rect(x_10, box_top, x_20 - x_10, box_h, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text((x_10 + x_20) / 2, box_top + 25, "Тип D", size=12, bold=True, color=POS))
    frags.append(text((x_10 + x_20) / 2, box_top + 45, "10–20 · I_n", size=10.5, bold=True, color="#991b1b"))
    frags.append(text((x_10 + x_20) / 2, box_top + 70, "Двигуни, компресори,\nтрансформатори", size=9, color="#7f1d1d"))

    # Панель пояснень праворуч
    panel_x = ox + 530
    frags.append(rect(panel_x, oy - gh + 15, 235, 335, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=8))
    frags.append(text(panel_x + 117, oy - gh + 38, "Критерії спрацьовування", size=12, bold=True, color="#0f172a"))

    frags.append(textbox(panel_x + 117, oy - gh + 95, "Тепловий розчіплювач:\n• 1.13 · I_n: струм нерозчеплення\n  (не вимикається t ≥ 1 год)\n• 1.45 · I_n: струм розчеплення\n  (вимикається t < 1 год)", size=9.5, pad=5, fill="#ffffff", stroke="#cbd5e1", sw=1)[0])

    frags.append(textbox(panel_x + 117, oy - gh + 195, "Електромагнітне відсікання:\n• Швидкість: t < 10–20 мс\n• B: 3–5 In (активне навантаження)\n• C: 5–10 In (універсальний)\n• D: 10–20 In (важкий пуск)", size=9.5, pad=5, fill="#eff6ff", stroke=NEG, sw=1)[0])

    frags.append(textbox(panel_x + 117, oy - gh + 295, "Тестове перевантаження 2.55 In:\nЧас відключення: 1 с ... 60 с\n(калібрована точка стандарту)", size=9.5, pad=5, fill="#fffbeb", stroke="#d97706", sw=1)[0])

    out_path = os.path.join(IMG_DIR, "trip-curves-iec60898.svg")
    render(out_path, w, h, *frags)
    print(f"Згенеровано {out_path}")


def fig_deion_arc():
    """Фігура 3: Фізика та електродинаміка гасіння дуги в деіонній решітці."""
    w, h = 900, 480
    frags = []

    frags.append(text(w / 2, 26, "Електродинаміка та механізм гасіння електричної дуги в деіонній камері", size=16, bold=True))

    col_w = 265
    gap = 25
    x0 = 30

    # Блок 1: Виникнення дуги та сила видування
    x1 = x0
    frags.append(rect(x1, 55, col_w, 395, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(rect(x1 + 10, 65, col_w - 20, 32, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=4))
    frags.append(text(x1 + col_w / 2, 86, "1. Електродинамічне видування", size=12, bold=True, color="#991b1b"))

    frags.append(textbox(x1 + col_w / 2, 130, "Розмикання контактів під струмом:\nСпалахує плазмовий шнур дуги\n(T = 6 000 ... 20 000 K)", size=10.5, pad=6, fill="#ffffff", stroke="#cbd5e1", sw=1)[0])
    frags.append(textbox(x1 + col_w / 2, 210, "Сила Лоренца:\nF = I · L × B\nКонтур петлі струму виштовхує\nдугу від контактів на роги", size=10.5, bold=True, pad=6, fill="#fef2f2", stroke=POS, sw=1.2)[0])
    frags.append(textbox(x1 + col_w / 2, 295, "Дугогасні роги (Arc Runners):\nРозширення проміжку дуги,\nзбільшення опору плазми", size=10, pad=6, fill="#eff6ff", stroke=NEG, sw=1)[0])
    frags.append(textbox(x1 + col_w / 2, 380, "Феромагнітне затягування:\nСталеві пластини притягують\nдугу всередину решітки", size=10, pad=5, fill="#f8fafc", stroke="#64748b", sw=1)[0])

    # Блок 2: Поділ дуги в решітці
    x2 = x1 + col_w + gap
    frags.append(rect(x2, 55, col_w, 395, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(rect(x2 + 10, 65, col_w - 20, 32, fill="#fef3c7", stroke="#fde68a", sw=1, rx=4))
    frags.append(text(x2 + col_w / 2, 86, "2. Поділ на мікродуги (De-ion)", size=12, bold=True, color="#92400e"))

    frags.append(textbox(x2 + col_w / 2, 130, "Пакет сталевих пластин:\n10–15 пластин із V-подібним вирізом\nтовщиною 0.8–1.2 мм", size=10.5, pad=6, fill="#ffffff", stroke="#cbd5e1", sw=1)[0])
    frags.append(textbox(x2 + col_w / 2, 210, "Стрибок спаду напруги:\nV_arc = ∑ (V_кат + V_ан + E·d)\nКожна пластина дає ΔV ≈ 20–25 В", size=10.5, bold=True, pad=6, fill="#fffbeb", stroke="#d97706", sw=1.2)[0])
    frags.append(textbox(x2 + col_w / 2, 295, "Сумарна напруга дуги:\nV_arc = N · ΔV ≈ 250–350 В\nНапруга дуги перевищує\nнапругу мережі живлення!", size=10.5, bold=True, pad=6, fill="#fef2f2", stroke=POS, sw=1.5)[0])
    frags.append(textbox(x2 + col_w / 2, 380, "Примусове зменшення струму:\ndi/dt = (V_grid - V_arc) / L < 0", size=10, bold=True, pad=5, fill="#ecfdf5", stroke=FIELD, sw=1)[0])

    # Блок 3: Охолодження та деіонізація
    x3 = x2 + col_w + gap
    frags.append(rect(x3, 55, col_w, 395, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(rect(x3 + 10, 65, col_w - 20, 32, fill="#ecfdf5", stroke="#a7f3d0", sw=1, rx=4))
    frags.append(text(x3 + col_w / 2, 86, "3. Деіонізація та згасання", size=12, bold=True, color="#065f46"))

    frags.append(textbox(x3 + col_w / 2, 130, "Кондуктивне охолодження:\nВеличезна теплоємність і площа\nметалевих пластин відбирають тепло", size=10.5, pad=6, fill="#ffffff", stroke="#cbd5e1", sw=1)[0])
    frags.append(textbox(x3 + col_w / 2, 210, "Рекомбінація носіїв:\nТемпература плазми різко падає,\nіони рекомбінують з електронами,\nопір каналу злітає до мегаомів", size=10, pad=6, fill="#f0fdf4", stroke=FIELD, sw=1.2)[0])
    frags.append(textbox(x3 + col_w / 2, 295, "Газогенеруючі стінки:\nПоліамід виділяє охолоджуючий\nгаз під дією УФ-випромінювання дуги", size=10, pad=6, fill="#eff6ff", stroke=NEG, sw=1)[0])
    frags.append(textbox(x3 + col_w / 2, 380, "Повне гасіння дуги:\nСтрум розірвано за 2–5 мс\nдо природного переходу через нуль!", size=10, bold=True, pad=5, fill="#f0fdf4", stroke=FIELD, sw=1.5)[0])

    out_path = os.path.join(IMG_DIR, "deion-arc-suppression.svg")
    render(out_path, w, h, *frags)
    print(f"Згенеровано {out_path}")


def fig_current_limiting():
    """Фігура 4: Динаміка обмеження струму короткого замикання (Клас 3 за EN 60898)."""
    w, h = 900, 480
    frags = []

    frags.append(text(w / 2, 26, "Динаміка струмообмеження класу 3 при короткому замиканні", size=16, bold=True))

    ox, oy = 75, 410
    gw, gh = 520, 340

    # Фон графіка
    frags.append(rect(ox, oy - gh, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))

    # Горизонтальна вісь часу
    frags.append(line(ox, oy - gh / 2, ox + gw, oy - gh / 2, color="#94a3b8", sw=1.5))
    # Вертикальна вісь струму
    frags.append(line(ox + 40, oy - gh, ox + 40, oy, color="#94a3b8", sw=1.5))

    frags.append(text(ox + 35, oy - gh / 2 + 16, "0", size=11, color="#64748b", anchor="end"))
    frags.append(text(ox + gw - 15, oy - gh / 2 + 18, "t (мс)", size=11, color="#64748b"))
    frags.append(text(ox + 45, oy - gh + 18, "I (кА)", size=11, color="#64748b"))

    # Опис очікуваного струму зверху
    frags.append(rect(ox + 80, oy - gh + 25, 400, 50, fill="#fef2f2", stroke=POS, sw=1.2, rx=6))
    frags.append(text(ox + 280, oy - gh + 44, "Очікуваний струм КЗ без обмеження (Prospective I_peak ≈ 10 кА)", size=10.5, bold=True, color="#991b1b"))
    frags.append(text(ox + 280, oy - gh + 62, "Пік на 5 мс, природне гасіння при переході через нуль на 10 мс", size=9.5, color="#7f1d1d"))

    # Опис обмеженого струму нижче
    frags.append(rect(ox + 80, oy - gh + 90, 400, 50, fill="#eff6ff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(ox + 280, oy - gh + 109, "Обмежений струм автомата Класу 3 (I_limited ≈ 2.5 кА)", size=10.5, bold=True, color=NEG))
    frags.append(text(ox + 280, oy - gh + 127, "Відсікання дугою за 2–3 мс — інтеграл I²t знижено в 10–20 разів!", size=9.5, color="#1e40af"))

    # Часові позначки знизу (поза текстовими блоками)
    frags.append(line(ox + 100, oy - gh / 2 - 10, ox + 100, oy - gh / 2 + 10, color="#64748b", sw=1.5))
    frags.append(text(ox + 100, oy - gh / 2 + 25, "0 мс (КЗ)", size=9.5, color="#64748b"))

    frags.append(line(ox + 200, oy - gh / 2 - 10, ox + 200, oy - gh / 2 + 10, color=NEG, sw=1.5))
    frags.append(text(ox + 200, oy - gh / 2 + 25, "2.5 мс (Розмикання)", size=9.5, color=NEG))

    frags.append(line(ox + 350, oy - gh / 2 - 10, ox + 350, oy - gh / 2 + 10, color=FIELD, sw=1.5))
    frags.append(text(ox + 350, oy - gh / 2 + 25, "6 мс (Гасіння)", size=9.5, color=FIELD))

    # Права панель: Класифікація
    px = ox + gw + 20
    pw = 260
    frags.append(rect(px, oy - gh, pw, gh, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(px + pw / 2, oy - gh + 25, "Класифікація струмообмеження", size=12, bold=True, color="#0f172a"))

    frags.append(textbox(px + pw / 2, oy - gh + 80, "Клас 1 (Без обмеження):\nГасіння дуги під час переходу\nзмінного струму через нуль (~10 мс).\nМаксимальне теплове навантаження.", size=9.5, pad=5, fill="#ffffff", stroke="#cbd5e1", sw=1)[0])

    frags.append(textbox(px + pw / 2, oy - gh + 170, "Клас 2 (Середнє обмеження):\nПроміжне обмеження енергії I²t.\nЧас відключення 6–8 мс.", size=9.5, pad=5, fill="#ffffff", stroke="#cbd5e1", sw=1)[0])

    frags.append(textbox(px + pw / 2, oy - gh + 265, "Клас 3 (Найвище обмеження):\nНадшвидке розходження контактів,\nвисока напруга дуги V_arc > V_grid.\nОбмеження пікового струму за 2–4 мс.\nОбов'язковий для сучасних мереж.", size=9.5, bold=True, pad=6, fill="#f0fdf4", stroke=FIELD, sw=1.2)[0])

    out_path = os.path.join(IMG_DIR, "current-limiting-dynamics.svg")
    render(out_path, w, h, *frags)
    print(f"Згенеровано {out_path}")


def fig_efuse_block():
    """Фігура 5: Архітектура та функціональні блоки твердотілого e-Fuse."""
    w, h = 900, 500
    frags = []

    frags.append(text(w / 2, 26, "Функціональна архітектура твердотілого електронного запобіжника (e-Fuse)", size=16, bold=True))

    # Корпус ІМС e-Fuse
    frags.append(rect(30, 50, 840, 425, fill="#f8fafc", stroke="#0f172a", sw=2, rx=12))
    frags.append(text(450, 75, "Інтегральна схема e-Fuse (Monolithic Solid-State Power Switch)", size=13, bold=True, color="#0f172a"))

    # Вхід V_IN та вихід V_OUT
    frags.append(textbox(100, 130, "V_IN (Вхід живлення)\n3.3 В ... 48 В DC", size=11, pad=6, fill="#fee2e2", stroke=POS, sw=1.5)[0])
    frags.append(line(165, 130, 235, 130, color=POS, sw=3))

    # Силовий N-MOSFET
    frags.append(rect(235, 95, 190, 70, fill="#ffffff", stroke=POS, sw=2, rx=8))
    frags.append(text(330, 120, "Силовий N-MOSFET", size=12, bold=True, color=POS))
    frags.append(text(330, 138, "Низький R_DS(on) (1–10 мОм)", size=10, color="#991b1b"))
    frags.append(text(330, 153, "Керування затвором V_GS", size=9.5, color=MUTED))

    frags.append(line(425, 130, 495, 130, color=POS, sw=3))

    # SenseFET / Струмовимірювальний блок
    frags.append(rect(495, 95, 180, 70, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(585, 120, "Датчик струму (SenseFET)", size=11, bold=True, color=NEG))
    frags.append(text(585, 138, "Співвідношення 1:1000", size=10, color="#1e40af"))
    frags.append(text(585, 153, "Без втрат на зовнішньому шунті", size=9.5, color=MUTED))

    frags.append(line(675, 130, 735, 130, color=POS, sw=3))

    frags.append(textbox(795, 130, "V_OUT (Навантаження)\nПлавний пуск / Захист", size=11, pad=6, fill="#ecfdf5", stroke=FIELD, sw=1.5)[0])

    # Керуючі вузли (середня лінія)
    frags.append(textbox(170, 240, "Зарядна помпа (Charge Pump)\nФормування V_gate > V_in\nдля повного відкриття N-MOSFET", size=10, pad=6, fill="#ffffff", stroke="#94a3b8", sw=1.2)[0])
    frags.append(textbox(450, 240, "Швидкий компаратор КЗ\nВідсікання затвора за < 500 нс\nпри жорсткому короткому замиканні", size=10, bold=True, pad=6, fill="#fee2e2", stroke=POS, sw=1.5)[0])
    frags.append(textbox(730, 240, "Активне регулювання струму\n(Current Limit Amplifier)\nФіксація струму при перевантаженні", size=10, pad=6, fill="#fffbeb", stroke="#d97706", sw=1.2)[0])

    # Нижня лінія допоміжних блоків
    frags.append(textbox(170, 360, "Керування наростанням dV/dt\n(Soft-Start / Inrush Control)\nЗаряд ємностей навантаження\nбез пускових надструмів", size=9.5, pad=6, fill="#f0fdf4", stroke=FIELD, sw=1.2)[0])
    frags.append(textbox(450, 360, "Термодатчик кристала (TSD)\nВимкнення при T_j > 165 °C\nз гістерезисом 20 °C\n(Захист від перегріву SOA)", size=9.5, pad=6, fill="#fef2f2", stroke=POS, sw=1.2)[0])
    frags.append(textbox(730, 360, "Контролер аварійних станів\n• Latch-off: блокування до скидання\n• Auto-retry: цикл перезапуску\nВивід статусу FAULT / ALERT", size=9.5, pad=6, fill="#eff6ff", stroke=NEG, sw=1.2)[0])

    # Зовнішні виводи налаштування знизу
    frags.append(textbox(450, 445, "Зовнішні виводи налаштування: R_ILIM (поріг струму), C_SS (час пуску), EN (увімкнення), FLT (статус)", size=10, pad=4, fill="#f1f5f9", stroke="#64748b", sw=1)[0])

    out_path = os.path.join(IMG_DIR, "efuse-internal-block.svg")
    render(out_path, w, h, *frags)
    print(f"Згенеровано {out_path}")


def main():
    fig_mcb_anatomy()
    fig_trip_curves()
    fig_deion_arc()
    fig_current_limiting()
    fig_efuse_block()
    print("Усі фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
