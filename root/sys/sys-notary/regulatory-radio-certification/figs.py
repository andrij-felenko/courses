# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. regulatory-domains-comparison ──────────────────────────────────────────
def fig_regulatory_domains():
    W, H = 880, 430
    p = []

    # Заголовок блоків
    col_w = 265
    gap = 20
    x0 = 30

    # 1. FCC (США)
    p.append(fitbox(x0, 40, col_w, 45, "США: FCC\n(Federal Communications Commission)", size=12, fill="#fdecea", stroke=POS, bold=True))
    p.append(fitbox(x0, 95, col_w, 315,
                    "Правова база:\n"
                    "• Title 47 CFR Part 15\n"
                    "  - Part 15B (Ненавмисні випромінювачі)\n"
                    "  - Part 15C §15.247 / §15.249 (ISM)\n"
                    "  - Part 15E (UNII 5/6 ГГц)\n\n"
                    "Процедура допуску:\n"
                    "• SDoC (для ненавмисних випромінювачів)\n"
                    "• Certification через TCB (Telecomm.\n"
                    "  Certification Body) для радіомодулів\n\n"
                    "Обов'язкове маркування:\n"
                    "• FCC ID: [Grantee Code (3–5)][Product Code]\n\n"
                    "Особливість:\n"
                    "Дозволено високу потужність (до 1 Вт cond),\n"
                    "акцент на захист урядових смуг.",
                    size=10, fill=FILL, stroke=LINE))

    # 2. CE RED (ЄС)
    x1 = x0 + col_w + gap
    p.append(fitbox(x1, 40, col_w, 45, "ЄС: CE RED\n(Radio Equipment Directive 2014/53/EU)", size=12, fill="#eaf0fd", stroke=NEG, bold=True))
    p.append(fitbox(x1, 95, col_w, 315,
                    "Правова база:\n"
                    "• Директива RED 2014/53/EU\n"
                    "• ETSI EN 300 328 (2.4 ГГц ISM)\n"
                    "• ETSI EN 300 220 (Sub-GHz SRD)\n"
                    "• ETSI EN 301 489 (Серія EMC)\n"
                    "• EN 62368-1 (Електробезпека LVD)\n\n"
                    "Процедура допуску:\n"
                    "• Module A (Самодекларація виробника DoC)\n"
                    "• Нотифікований орган (Notified Body, NB)\n"
                    "  у разі відхилення від гармонізованих норм\n\n"
                    "Обов'язкове маркування:\n"
                    "• Знак CE (+ 4 цифри NB за наявності)\n\n"
                    "Особливість:\n"
                    "Жорсткий ліміт 100 мВт EIRP, обов'язковий\n"
                    "Duty Cycle або LBT для доступу до ефіру.",
                    size=10, fill=FILL, stroke=LINE))

    # 3. SRRC (Китай)
    x2 = x1 + col_w + gap
    p.append(fitbox(x2, 40, col_w, 45, "Китай: SRRC / CMIIT\n(State Radio Regulatory Commission)", size=12, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(fitbox(x2, 95, col_w, 315,
                    "Правова база:\n"
                    "• Radio Regulation of the PRC\n"
                    "• Регуляторні накази MIIT\n"
                    "• Стандарти GB/T та GB 9254\n\n"
                    "Процедура допуску:\n"
                    "• Обов'язкове тестування зразків\n"
                    "  виключно в акредитованих державних\n"
                    "  лабораторіях на території Китаю\n"
                    "• Самодекларація заборонена\n\n"
                    "Обов'язкове маркування:\n"
                    "• CMIIT ID: [Рік][Тип][Номер дозволу]\n\n"
                    "Особливість:\n"
                    "Унікальні сітки Sub-GHz (470–510 МГц),\n"
                    "заборона неавторизованих шифрів.",
                    size=10, fill=FILL, stroke=LINE))

    render(os.path.join(OUT, "regulatory-domains-comparison.svg"), W, H, *p,
           title="Порівняння регуляторних рамок: FCC (США), CE RED (ЄС) та SRRC (Китай)")


# ── 2. eirp-power-budget-fcc-etsi ─────────────────────────────────────────────
def fig_eirp_power_budget():
    W, H = 880, 420
    p = []

    # Верхня частина: Тракт передавача і формула EIRP
    p.append(rect(40, 45, 800, 115, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(440, 65, "Радіотракт випромінювача: кондуктивна потужність проти випромінюваної (EIRP)", size=12, bold=True))

    # Блоки тракту
    p.append(fitbox(60, 85, 150, 55, "RF Трансивер / PA\nКондуктивна потужність\nP_conducted (дБм)", size=10, fill="#fdecea", stroke=POS))
    p.append(arrow(210, 112, 280, 112, color=LINE, sw=1.5))

    p.append(fitbox(280, 85, 150, 55, "Фідер / Доріжка / Фільтр\nВтрати у тракті\nL_cable (дБ)", size=10, fill="#e2e8f0", stroke=MUTED))
    p.append(arrow(430, 112, 500, 112, color=LINE, sw=1.5))

    p.append(fitbox(500, 85, 140, 55, "Антена виробу\nКоефіцієнт підсилення\nG_antenna (дБі)", size=10, fill="#eaf0fd", stroke=NEG))
    p.append(arrow(640, 112, 700, 112, color=FIELD, sw=2))

    p.append(fitbox(700, 85, 120, 55, "Ефір\nEIRP (дБм / мВт)\nEIRP = P + G − L", size=10, fill="#eef6ef", stroke=FIELD, bold=True))

    # Нижня частина: Порівняння лімітів 2.4 ГГц
    p.append(rect(40, 175, 385, 225, fill=FILL, stroke=POS, sw=1.5, rx=6))
    p.append(text(232, 198, "США: FCC Title 47 Part 15.247 (2.4 ГГц)", size=11.5, color=POS, bold=True))
    p.append(fitbox(55, 212, 355, 175,
                    "• Максимальна кондуктивна потужність: 30 дБм (1.0 Вт)\n"
                    "• Базове підсилення антени: до 6.0 дБі\n"
                    "• Максимальна випромінювана потужність (EIRP):\n"
                    "  30 дБм + 6 дБі = 36 дБм (4.0 Вт EIRP!)\n\n"
                    "Правило де-рейтингу (De-rating rule):\n"
                    "Якщо підсилення антени G > 6 дБі:\n"
                    "  - Point-to-Multipoint: P_cond зменшується на 1 дБ за кожен 1 дБі\n"
                    "  - Point-to-Point: P_cond зменшується на 1 дБ на кожні 3 дБі",
                    size=9.5, fill="#ffffff", stroke=MUTED))

    p.append(rect(455, 175, 385, 225, fill=FILL, stroke=NEG, sw=1.5, rx=6))
    p.append(text(647, 198, "ЄС: ETSI EN 300 328 / RED (2.4 ГГц)", size=11.5, color=NEG, bold=True))
    p.append(fitbox(470, 212, 355, 175,
                    "• Максимальна сумарна потужність: 20 дБм (100 мВт EIRP)\n"
                    "• Кондуктивна потужність НЕ нормується окремо:\n"
                    "  P_conducted = 20 дБм − G_antenna + L_cable\n"
                    "• Якщо антена має підсилення 5 дБі:\n"
                    "  P_conducted повинна бути ≤ 15 дБм (31.6 мВт)\n\n"
                    "Вимога до адаптивності (LBT / CCA):\n"
                    "  - При потужності > 10 дБм EIRP пристрій зобов'язаний\n"
                    "    мати адаптивний механізм доступу до ефіру",
                    size=9.5, fill="#ffffff", stroke=MUTED))

    render(os.path.join(OUT, "eirp-power-budget-fcc-etsi.svg"), W, H, *p,
           title="Бюджет потужності передавача та EIRP на частоті 2.4 ГГц: FCC проти ETSI")


# ── 3. spurious-emissions-spectrum-mask ────────────────────────────────────────
def fig_spurious_emissions():
    W, H = 880, 420
    p = []

    # Вісь частот і потужності
    p.append(line(70, 330, 830, 330, color=LINE, sw=1.5))  # Frequency axis
    p.append(arrow(70, 330, 840, 330, color=LINE, sw=1.5))
    p.append(text(830, 350, "Частота (f)", size=11, color=INK, bold=True))

    p.append(line(90, 350, 90, 45, color=LINE, sw=1.5))    # Power axis
    p.append(arrow(90, 350, 90, 35, color=LINE, sw=1.5))
    p.append(text(85, 30, "Потужність (дБм)", size=11, color=INK, bold=True, anchor="end"))

    # Позначки рівнів потужності
    levels = [(70, "+20 дБм (TX)"), (130, "0 дБм"), (190, "−20 dBc"), (230, "−30 дБм (ETSI >1 ГГц)"), (270, "−41.2 дБм (FCC Restr.)"), (310, "−54 дБм (RX/Standby)")]
    for y_pos, lbl in levels:
        p.append(line(85, y_pos, 820, y_pos, color=MUTED, sw=0.7, dash="2 3"))
        p.append(text(82, y_pos + 4, lbl, size=9.5, color=MUTED, anchor="end"))

    # Спектральний пік (Основна смуга In-Band)
    # Центральна частота f0 = 320 px
    p.append(rect(280, 70, 80, 260, fill="#fdecea", stroke=POS, sw=1.5, rx=3))
    p.append(text(320, 150, "Основна смуга\n(In-Band, f0)\nWi-Fi / LoRa / BLE", size=10, color=POS, bold=True))

    # Позасмугові випромінювання (Band Edges / Out-of-Band)
    p.append(rect(225, 190, 55, 140, fill="#fff2cc", stroke="#d97706", sw=1.2, rx=2))
    p.append(rect(360, 190, 55, 140, fill="#fff2cc", stroke="#d97706", sw=1.2, rx=2))
    p.append(text(252, 230, "Край\nсмуги", size=9.5, color="#b45309", bold=True))
    p.append(text(387, 230, "Край\nсмуги", size=9.5, color="#b45309", bold=True))

    # Друга гармоніка 2*f0 (640 px)
    p.append(rect(615, 235, 50, 95, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=2))
    p.append(text(640, 265, "2-га гармоніка\n(2·f0)", size=9.5, color=NEG, bold=True))

    # Третя гармоніка 3*f0 (760 px)
    p.append(rect(745, 260, 40, 70, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=2))
    p.append(text(765, 285, "3-тя\n(3·f0)", size=9.5, color=NEG, bold=True))

    # Пояснювальні винесення вгорі
    p.append(fitbox(450, 50, 370, 80,
                    "Зони випромінювання та вимірювальні норми:\n"
                    "1. In-Band: корисний сигнал, ліміт EIRP (FCC 30 дБм, ETSI 20 дБм)\n"
                    "2. Out-of-Band (OOB): спадання спектральної маски (−20 dBc)\n"
                    "3. Spurious (Гармоніки): ETSI TX ≤ −30 дБм, RX ≤ −54 дБм\n"
                    "4. FCC Restricted Bands: жорсткий поріг ≤ −41.2 дБм EIRP (500 мкВ/м)",
                    size=9.5, fill="#f8fafc", stroke=LINE))

    render(os.path.join(OUT, "spurious-emissions-spectrum-mask.svg"), W, H, *p,
           title="Спектральна маска та побічні випромінювання (Spurious Emissions)")


# ── 4. modular-approval-pathways ──────────────────────────────────────────────
def fig_modular_approval():
    W, H = 880, 420
    p = []

    # Крок 1: Радіомодуль (OEM Module)
    p.append(rect(30, 45, 240, 350, fill="#f8fafc", stroke=POS, sw=1.5, rx=6))
    p.append(text(150, 68, "Рівень 1: Радіомодуль (OEM)", size=11.5, color=POS, bold=True))

    p.append(fitbox(45, 85, 210, 160,
                    "8 критеріїв Full Modular (KDB 996369):\n"
                    "1. Власне металеве екранування RF\n"
                    "2. Буферизовані входи даних/керування\n"
                    "3. Вбудований стабілізатор живлення\n"
                    "4. Фіксована антена / унікальний роз'єм\n"
                    "5. Тестування Standalone на тестовій платі\n"
                    "6. Постійне маркування FCC ID на кришці\n"
                    "7. Чіткі інструкції з інтеграції в мануалі\n"
                    "8. Відповідність вимогам RF Exposure/SAR",
                    size=9.5, fill="#ffffff", stroke=MUTED))

    p.append(fitbox(45, 260, 210, 115,
                    "Результат для модуля:\n"
                    "• Отримання гранту FCC ID\n"
                    "• Повний звіт RF / EMC / RED\n"
                    "• Виробник несе відповідальність\n"
                    "  за радіопараметри модуля",
                    size=9, fill="#fdecea", stroke=POS))

    # Стрілка переходу
    p.append(arrow(270, 220, 320, 220, color=LINE, sw=2))

    # Крок 2: Інтеграція в кінцевий хост-пристрій
    p.append(rect(320, 45, 270, 350, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(455, 68, "Рівень 2: Кінцевий виріб (Host)", size=11.5, color=INK, bold=True))

    p.append(fitbox(335, 85, 240, 160,
                    "Інтеграція готового модуля в хост:\n"
                    "• Дотримання топології трасування антени\n"
                    "• Перевірка електроживлення та розв'язки\n"
                    "• Оцінка відстані до тіла користувача:\n"
                    "  - > 20 см: мобільний розрахунок MPE\n"
                    "  - < 20 см: портативний пристрій, SAR!\n"
                    "• Оцінка одночасного випромінювання\n"
                    "  (Co-located RF: Wi-Fi + BLE + LTE)",
                    size=9, fill="#ffffff", stroke=MUTED))

    p.append(fitbox(335, 260, 240, 115,
                    "Тестування кінцевого хоста:\n"
                    "• Part 15B (Ненавмисне випромінювання хоста)\n"
                    "• EN 301 489 (EMC системного рівня)\n"
                    "• EN 62368-1 (Електробезпека виробу)",
                    size=9, fill="#eef6ef", stroke=FIELD))

    # Стрілка переходу
    p.append(arrow(590, 220, 640, 220, color=LINE, sw=2))

    # Крок 3: Випуск на ринок та маркування
    p.append(rect(640, 45, 210, 350, fill="#f8fafc", stroke=NEG, sw=1.5, rx=6))
    p.append(text(745, 68, "Рівень 3: Допуск на ринок", size=11.5, color=NEG, bold=True))

    p.append(fitbox(655, 85, 180, 135,
                    "Маркування хоста:\n\n"
                    "«Contains FCC ID: XYZ-123»\n"
                    "«Contains CMIIT ID: ...»\n\n"
                    "Знак CE на корпусі\n"
                    "готового приладу",
                    size=9.5, fill="#ffffff", stroke=MUTED))

    p.append(fitbox(655, 235, 180, 140,
                    "Документація виробника:\n"
                    "• Технічний файл (TCF)\n"
                    "• Підписана EU DoC\n"
                    "• Збереження тест-репортів\n"
                    "  протягом 10 років",
                    size=9, fill="#eaf0fd", stroke=NEG))

    render(os.path.join(OUT, "modular-approval-pathways.svg"), W, H, *p,
           title="Шляхи модульної сертифікації та інтеграції в кінцевий виріб (Host Product)")


if __name__ == "__main__":
    fig_regulatory_domains()
    fig_eirp_power_budget()
    fig_spurious_emissions()
    fig_modular_approval()
    print("All figures generated successfully.")
