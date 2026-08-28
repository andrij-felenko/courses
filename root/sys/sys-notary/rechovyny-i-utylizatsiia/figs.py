# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра
ROHS_COL  = "#2563eb"   # Синій — RoHS
REACH_COL = "#7c3aed"   # Фіолетовий — REACH
WEEE_COL  = "#059669"   # Зелений — WEEE / Екологія
GOOD      = FIELD       # Зелений — Відповідність
WARN_COL  = "#dc2626"   # Червоний — Заборона / Токсичність
ALERT_COL = "#d97706"   # Помаранчевий — Попередження / Ліміт
CARD_BG   = "#ffffff"
ROW_BG    = "#f8fafc"


# ── Фігура 1: Гомогенні матеріали в електроніці (RoHS) ─────────────────────────

def fig_rohs_homogeneous_materials():
    W, H = 840, 450
    p = []

    # Загальне тло
    p.append(rect(15, 15, 810, 420, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(35, 38, "Концепція «гомогенного матеріалу» в електронному вузлі (RoHS)",
                  size=14, color=INK, bold=True, anchor="start"))
    p.append(text(35, 56, "Ліміти концентрації 10 заборонених речовин діють для кожного шару окремо, а не для плати чи чіпа загалом",
                  size=10.5, color=MUTED, anchor="start"))

    # Ліва колонка: Розбір корпусу мікросхеми (IC Package)
    p.append(rect(35, 75, 370, 275, fill=CARD_BG, stroke=ROHS_COL, sw=1.6, rx=6))
    p.append(rect(35, 75, 370, 28, fill=ROHS_COL, stroke=ROHS_COL, sw=1.6, rx=6))
    p.append(text(220, 94, "Корпус мікросхеми (IC Package)", size=12, color="#ffffff", bold=True))

    layers_ic = [
        ("Епоксидний компаунд (Molding):", "Бром PBB/PBDE, фталати < 0.1%", WARN_COL),
        ("Кремнієвий кристал (Silicon Die):", "Чистий Si / легування (без лімітованих)", GOOD),
        ("Епоксид монтажу кристала (Die Attach):", "Срібло + епоксид, Pb < 0.1%", WARN_COL),
        ("Дротяні розварки (Gold/Cu Wires):", "Золото Au або мідь Cu (без заборон)", GOOD),
        ("Мідний вивідний каркас (Leadframe):", "Мідний сплав Cu, Pb < 0.1%", WARN_COL),
        ("Покриття виводів (Lead Finish):", "Матове олово Sn (без свинцю Pb < 0.1%)", ALERT_COL),
    ]
    y_ic = 124
    for title, desc, col in layers_ic:
        p.append(rect(45, y_ic - 13, 350, 32, fill=ROW_BG, stroke="#e2e8f0", sw=1.0, rx=4))
        p.append(circle(56, y_ic + 3, 4.0, fill=col, stroke=col, sw=1.0))
        p.append(text(68, y_ic, title, size=10.5, color=INK, bold=True, anchor="start"))
        p.append(text(68, y_ic + 13, desc, size=9.5, color=MUTED, anchor="start"))
        y_ic += 38

    # Права колонка: Розбір друкованої плати та паяного з'єднання (PCB & Solder)
    p.append(rect(435, 75, 370, 275, fill=CARD_BG, stroke=ROHS_COL, sw=1.6, rx=6))
    p.append(rect(435, 75, 370, 28, fill=ROHS_COL, stroke=ROHS_COL, sw=1.6, rx=6))
    p.append(text(620, 94, "Друкована плата та пайка (PCB & Joint)", size=12, color="#ffffff", bold=True))

    layers_pcb = [
        ("Склотекстоліт FR4 (Dielectric):", "Тетрабромбісфенол А (TBBA) / без галогенів", WARN_COL),
        ("Мідна фольга (Copper Foil):", "Електролітична мідь (Cu > 99.9%)", GOOD),
        ("Паяльна маска (Soldermask):", "Полімерний шар, фталати, Cd < 0.01%", WARN_COL),
        ("Фінішне покриття (ENIG / HASL):", "Безсвинцеве покриття Ni/Au або Sn", ALERT_COL),
        ("Паяний шов (Solder Joint):", "Сплав SAC305 (Sn96.5 Ag3.0 Cu0.5, Pb < 0.1%)", WARN_COL),
        ("Маркування шовкографією (Legend):", "Фарба без важких металів (Pb, Cd, Cr VI)", GOOD),
    ]
    y_pcb = 124
    for title, desc, col in layers_pcb:
        p.append(rect(445, y_pcb - 13, 350, 32, fill=ROW_BG, stroke="#e2e8f0", sw=1.0, rx=4))
        p.append(circle(456, y_pcb + 3, 4.0, fill=col, stroke=col, sw=1.0))
        p.append(text(468, y_pcb, title, size=10.5, color=INK, bold=True, anchor="start"))
        p.append(text(468, y_pcb + 13, desc, size=9.5, color=MUTED, anchor="start"))
        y_pcb += 38

    # Нижня плашка: Визначення гомогенного матеріалу
    b_rule = fitbox(35, 360, 770, 60,
                    "Гомогенний матеріал — речовина однорідного складу, яку не можна механічно розділити (розкрутити, розрізати,\n"
                    "розтерти) на окремі матеріали. Перевірка 10 речовин (Pb, Hg, Cd, Cr VI, PBB, PBDE, 4 фталати) проводиться для КОЖНОГО шару!",
                    size=10.5, fill="#eff6ff", stroke=ROHS_COL, color=INK)
    p.append(b_rule)

    render(os.path.join(OUT, "rohs-homogeneous-materials.svg"), W, H, *p,
           title="Гомогенні матеріали в електронному вузлі за директивою RoHS")


# ── Фігура 2: Принцип OAOA у регламенті REACH ──────────────────────────────────

def fig_reach_oaoa_principle():
    W, H = 840, 430
    p = []

    p.append(rect(15, 15, 810, 400, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(35, 38, "Принцип «Once An Article, Always An Article» (OAOA) у регламенті REACH",
                  size=14, color=INK, bold=True, anchor="start"))
    p.append(text(35, 56, "Рішення Суду ЄС (C-106/14): ліміт SVHC 0.1% w/w розраховується для кожної складової деталі окремо",
                  size=10.5, color=MUTED, anchor="start"))

    # Лівий блок: Хибний підхід (розмивання маси)
    p.append(rect(35, 75, 370, 245, fill=CARD_BG, stroke=WARN_COL, sw=1.6, rx=6))
    p.append(rect(35, 75, 370, 28, fill="#fee2e2", stroke=WARN_COL, sw=1.6, rx=6))
    p.append(text(220, 94, "ХИБНО: Розмивання маси виробу", size=12, color=WARN_COL, bold=True))

    p.append(text(48, 122, "Готовий прилад у зборі (вага 1000 г)", size=11, color=INK, bold=True, anchor="start"))
    p.append(text(48, 140, "• Усередині встановлено гумове кільце ущільнювача (1 г)", size=10, color=MUTED, anchor="start"))
    p.append(text(48, 156, "• Кільце містить 15 мг пластифікатора DEHP (1.5% w/w)", size=10, color=MUTED, anchor="start"))

    b_math_bad = rect(48, 172, 344, 46, fill="#fef2f2", stroke=WARN_COL, sw=1.0, rx=4)
    p.append(b_math_bad)
    p.append(text(220, 190, "Концентрація на весь прилад: 15 мг / 1000 г = 0.0015%", size=10.5, color=INK, bold=True))
    p.append(text(220, 206, "0.0015% < 0.1%  →  виробник помилково не декларує", size=10, color=WARN_COL))

    p.append(text(220, 242, "✖ ПОРУШЕННЯ ЗАКОНУ ЄС (ШТРАФ ТА ВІДКЛИКАННЯ)", size=10.5, color=WARN_COL, bold=True))
    p.append(text(220, 260, "Заборонено розчиняти токсичну речовину у вазі корпусу чи рами", size=10, color=MUTED))

    # Правий блок: Законний підхід OAOA
    p.append(rect(435, 75, 370, 245, fill=CARD_BG, stroke=REACH_COL, sw=1.6, rx=6))
    p.append(rect(435, 75, 370, 28, fill="#ede9fe", stroke=REACH_COL, sw=1.6, rx=6))
    p.append(text(620, 94, "ЗАКОННО: Принцип OAOA (C-106/14)", size=12, color=REACH_COL, bold=True))

    p.append(text(448, 122, "Оцінка кожної деталі як окремого виробу", size=11, color=INK, bold=True, anchor="start"))
    p.append(text(448, 140, "• Гумове кільце зберігає статус «виробу» (Article) у зборі", size=10, color=MUTED, anchor="start"))
    p.append(text(448, 156, "• Вага кільця = 1.0 г, вага DEHP = 15 мг", size=10, color=MUTED, anchor="start"))

    b_math_good = rect(448, 172, 344, 46, fill="#f5f3ff", stroke=REACH_COL, sw=1.0, rx=4)
    p.append(b_math_good)
    p.append(text(620, 190, "Концентрація у виробі: 15 мг / 1.0 г = 1.5% w/w", size=10.5, color=INK, bold=True))
    p.append(text(620, 206, "1.5% > 0.1%  →  активуються зобов'язання REACH та SCIP", size=10, color=REACH_COL, bold=True))

    p.append(text(620, 242, "✓ ПОВНИЙ ЮРИДИЧНИЙ КОМПЛАЄНС", size=10.5, color=GOOD, bold=True))
    p.append(text(620, 260, "Повідомлення клієнтів (Art. 33) + обов'язкове досьє в базі SCIP", size=10, color=MUTED))

    # Нижній висновок
    b_rule = fitbox(35, 330, 770, 70,
                    "Судове правило ЄС: якщо деталь була виробом до монтажу (гвинт, ущільнювач, чіп, кабель), вона залишається виробом\n"
                    "і всередині складного приладу. Ліміт концентрації SVHC 0.1% w/w рахується за власною масою деталі.\n"
                    "Перевищення 0.1% вимагає негайного інформування клієнтів (Art. 33) та подання досьє до бази даних ECHA SCIP.",
                    size=10.5, fill="#fbfbfe", stroke=REACH_COL, color=INK)
    p.append(b_rule)

    render(os.path.join(OUT, "reach-oaoa-principle.svg"), W, H, *p,
           title="Принцип Once An Article Always An Article у регламенті REACH")


# ── Фігура 3: Знак WEEE та замкнений цикл EPR ──────────────────────────────────

def fig_weee_mark_and_epr_loop():
    W, H = 840, 450
    p = []

    p.append(rect(15, 15, 810, 420, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(35, 38, "Маркування WEEE (EN 50419) та розширена відповідальність виробника (EPR)",
                  size=14, color=INK, bold=True, anchor="start"))
    p.append(text(35, 56, "Виробник фінансово та організаційно забезпечує збирання й переробку відходів власного обладнання",
                  size=10.5, color=MUTED, anchor="start"))

    # Лівий блок: Маркування WEEE за EN 50419
    p.append(rect(35, 75, 260, 260, fill=CARD_BG, stroke=WEEE_COL, sw=1.6, rx=6))
    p.append(rect(35, 75, 260, 28, fill=WEEE_COL, stroke=WEEE_COL, sw=1.6, rx=6))
    p.append(text(165, 94, "Знак перекресленого смітника", size=12, color="#ffffff", bold=True))

    cx, cy = 165, 150
    # Контейнер
    p.append(rect(cx - 24, cy - 15, 48, 44, fill="#ffffff", stroke=INK, sw=2.2, rx=3))
    p.append(line(cx - 14, cy - 8, cx - 14, cy + 22, color=INK, sw=1.8))
    p.append(line(cx, cy - 8, cx, cy + 22, color=INK, sw=1.8))
    p.append(line(cx + 14, cy - 8, cx + 14, cy + 22, color=INK, sw=1.8))
    # Кришка
    p.append(line(cx - 28, cy - 18, cx + 28, cy - 18, color=INK, sw=2.4))
    p.append(rect(cx - 8, cy - 24, 16, 6, fill="#ffffff", stroke=INK, sw=2.0, rx=1))
    # Колеса
    p.append(circle(cx - 18, cy + 34, 5, fill="#ffffff", stroke=INK, sw=2.0))
    p.append(circle(cx + 18, cy + 34, 5, fill="#ffffff", stroke=INK, sw=2.0))
    # Хрест (заборона викидання в загальне сміття)
    p.append(line(cx - 30, cy - 26, cx + 30, cy + 36, color=WARN_COL, sw=3.2))
    p.append(line(cx + 30, cy - 26, cx - 30, cy + 36, color=WARN_COL, sw=3.2))
    # Суцільна чорна смуга знизу (EN 50419 — випуск після 13.08.2005)
    p.append(rect(cx - 28, cy + 46, 56, 7, fill=INK, stroke=INK, sw=1.0))

    p.append(text(165, 230, "Вимоги до маркування:", size=10.5, color=INK, bold=True))
    p.append(text(165, 248, "• Висота знака: не менше 7 мм", size=10, color=MUTED))
    p.append(text(165, 264, "• Чорна смуга: товщина h > 0.3a", size=10, color=MUTED))
    p.append(text(165, 280, "• Стійкість до стирання водою/спиртом", size=10, color=MUTED))
    p.append(text(165, 304, "Заборонено викидати у побутовий смітник!", size=9.5, color=WARN_COL, bold=True))

    # Правий блок: Замкнений цикл EPR (Extended Producer Responsibility)
    p.append(rect(310, 75, 495, 260, fill=CARD_BG, stroke=WEEE_COL, sw=1.6, rx=6))
    p.append(rect(310, 75, 495, 28, fill=WEEE_COL, stroke=WEEE_COL, sw=1.6, rx=6))
    p.append(text(557, 94, "Замкнений життєвий цикл та обов'язки EPR", size=12, color="#ffffff", bold=True))

    steps_epr = [
        ("1. Реєстрація виробника", "Національний реєстр кожної країни ЄС (stiftung ear, ADEME) + фінансова гарантія"),
        ("2. Еко-внески (Eco-fees)", "Оплата внесків операторам PRO пропорційно масі обладнання, виведеного на ринок"),
        ("3. Роздільне збирання", "Муніципальні та комерційні пункти приймання відходів електроніки від споживачів"),
        ("4. Переробка та афінаж", "Вилучення акумуляторів, конденсаторів; рециклінг металів (Cu, Au, Sn) та полімерів"),
        ("5. Щорічна звітність", "Підтвердження виконання нормативів рециклінгу (55–85% маси) державним органам"),
    ]
    y_epr = 124
    for title, desc in steps_epr:
        p.append(rect(320, y_epr - 13, 475, 34, fill=ROW_BG, stroke="#e2e8f0", sw=1.0, rx=4))
        p.append(circle(332, y_epr + 3, 4.5, fill=WEEE_COL, stroke=WEEE_COL, sw=1.0))
        p.append(text(344, y_epr, title, size=10.5, color=INK, bold=True, anchor="start"))
        p.append(text(344, y_epr + 13, desc, size=9.5, color=MUTED, anchor="start"))
        y_epr += 40

    # Нижній висновок
    b_rule = fitbox(35, 345, 770, 75,
                    "EPR переносить фінансовий тягар утилізації з муніципалітетів на виробника або імпортера.\n"
                    "Перед продажем у будь-якій країні ЄС виробник реєструється в національному реєстрі (EAR, ADEME тощо),\n"
                    "сплачує еко-внески операторам PRO та щорічно звітує про масу виведеного на ринок і зібраного обладнання.",
                    size=10.5, fill="#ecfdf5", stroke=WEEE_COL, color=INK)
    p.append(b_rule)

    render(os.path.join(OUT, "weee-mark-and-epr-loop.svg"), W, H, *p,
           title="Маркування WEEE та замкнений цикл розширеної відповідальності виробника EPR")


# ── Фігура 4: Конвеєр комплаєнсу за EN IEC 63000:2018 ──────────────────────────

def fig_compliance_verification_flow():
    W, H = 840, 430
    p = []

    p.append(rect(15, 15, 810, 400, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(35, 38, "Конвеєр оцінки відповідності матеріалів за стандартом EN IEC 63000:2018",
                  size=14, color=INK, bold=True, anchor="start"))
    p.append(text(35, 56, "Гармонізований стандарт для підтвердження дотримання директиви RoHS та нанесення маркування CE",
                  size=10.5, color=MUTED, anchor="start"))

    stages = [
        ("Етап 1: Ризики", "Оцінка ризиків:", "Класифікація BOM за типами:\nнизький, середній або високий\nризик наявності токсинів"),
        ("Етап 2: Декларації", "Документи від постачальника:", "Збір сертифікатів CoC\nта FMD за стандартами\nIPC-1752A / IEC 62474"),
        ("Етап 3: Лабораторія", "Аналітичний контроль:", "Експрес-скринінг XRF\nта мокра хімія ICP / GC-MS\nдля деталей високого ризику"),
        ("Етап 4: Техфайл", "Юридичне оформлення:", "Складання Technical File,\nпідписання EU DoC\nта нанесення знака CE"),
    ]

    x_step = 195
    for i, (head, sub, desc) in enumerate(stages):
        x0 = 35 + i * x_step
        p.append(rect(x0, 75, 180, 235, fill=CARD_BG, stroke=ROHS_COL, sw=1.5, rx=6))
        p.append(rect(x0, 75, 180, 28, fill=ROHS_COL, stroke=ROHS_COL, sw=1.5, rx=6))
        p.append(text(x0 + 90, 94, head, size=11, color="#ffffff", bold=True))

        p.append(text(x0 + 90, 122, sub, size=10, color=INK, bold=True))
        b_sub = fitbox(x0 + 10, 135, 160, 90, desc, size=9.5, fill=ROW_BG, stroke="#e2e8f0", color=MUTED)
        p.append(b_sub)

        # Номер кроку
        p.append(circle(x0 + 90, 265, 12, fill="#eff6ff", stroke=ROHS_COL, sw=1.4))
        p.append(text(x0 + 90, 270, str(i + 1), size=11, color=ROHS_COL, bold=True))

        # Стрілка переходу між етапами (розташована на вільному проміжку)
        if i < 3:
            p.append(arrow(x0 + 182, 190, x0 + 193, 190, color=ROHS_COL, sw=1.8))

    # Нижній висновок
    b_rule = fitbox(35, 325, 770, 75,
                    "EN IEC 63000:2018 не вимагає тестувати кожен резистор у лабораторії, якщо постачальник має високу надійність\n"
                    "та надав повне розкриття складу (FMD). Лабораторні випробування (XRF-скринінг та мокра хімія ICP-OES / GC-MS)\n"
                    "проводяться цільово для компонентів з високим оціненим ризиком наявності заборонених речовин.",
                    size=10.5, fill="#f0f9ff", stroke=ROHS_COL, color=INK)
    p.append(b_rule)

    render(os.path.join(OUT, "compliance-verification-flow.svg"), W, H, *p,
           title="Конвеєр оцінки відповідності матеріалів за стандартом EN IEC 63000")


if __name__ == "__main__":
    fig_rohs_homogeneous_materials()
    fig_reach_oaoa_principle()
    fig_weee_mark_and_epr_loop()
    fig_compliance_verification_flow()
    print("All 4 figures generated successfully in ./img/")
