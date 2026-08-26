# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def path(d, stroke=LINE, sw=1.5, fill="none", dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"{d_attr}/>'


# ── Figure 1: Дилема мікроватного живлення ────────────────────────────────────
def fig_micro_watt_dilemma():
    W, H = 940, 460
    p = []

    # Заголовки двох колонок
    p.append(text(235, 30, "Пряме підключення (Неможливе)", size=14, bold=True, color=POS))
    p.append(text(705, 30, "Розділення в часі: буферизація та спалах", size=14, bold=True, color=FIELD))

    # Ліва колонка - Неможливість
    p.append(rect(25, 50, 420, 390, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    
    p.append(rect(45, 75, 170, 70, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(130, 102, "Джерело збору", size=12, bold=True))
    p.append(text(130, 124, "P_in = 20 мкВт (10 мкА @ 2 В)", size=10, color=MUTED))

    p.append(arrow(215, 110, 265, 110, color=LINE, sw=1.5))

    p.append(rect(265, 75, 160, 70, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(345, 102, "Навантаження (MCU)", size=12, bold=True))
    p.append(text(345, 124, "P_act = 45 мВт (15 мА @ 3 В)", size=10, color=POS))

    p.append(rect(45, 175, 380, 245, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(235, 202, "Фізичний колапс шини живлення", size=12, bold=True, color=POS))
    
    collapse_lines = [
        "1. Внутрішній опір джерела R_src = 2..10 кОм",
        "2. Спроба взяти 15 мА просаджує напругу до нуля",
        "3. U_out = U_oc - I_load * R_src -> 0.05 В",
        "4. Мікроконтролер застрягає в нескінченному Brown-out",
        "5. Класичний сон не рятує: I_sleep > I_harvest"
    ]
    for idx, cl in enumerate(collapse_lines):
        p.append(text(65, 235 + idx * 34, cl, size=11, anchor="start", color=INK))

    # Права колонка - Буферизація
    p.append(rect(495, 50, 420, 390, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))

    # Блок Фаза 1
    p.append(rect(515, 75, 380, 155, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(705, 98, "Фаза 1: Накопичення заряду (T_acc = 10..60 с)", size=12, bold=True, color=FIELD))
    p.append(text(535, 125, "• Навантаження ізольоване ключем нановольтового PMIC", size=11, anchor="start"))
    p.append(text(535, 152, "• Струм спокою PMIC I_q < 300 нА (менше за I_harvest)", size=11, anchor="start"))
    p.append(text(535, 179, "• Енергія повільно накопичується в іоністорі", size=11, anchor="start"))
    p.append(text(535, 206, "• Напруга зростає: V_cap піднімається від 2.0 В до 3.3 В", size=11, anchor="start", color=MUTED))

    # Блок Фаза 2
    p.append(rect(515, 250, 380, 170, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(705, 273, "Фаза 2: Спалах активності (T_burst = 10..30 мс)", size=12, bold=True, color=FIELD))
    p.append(text(535, 300, "• Супервізор фіксує V_cap >= 3.3 В -> сигнал Power Good", size=11, anchor="start"))
    p.append(text(535, 327, "• Ключ вмикає живлення: MCU виконує вимірювання та радіо", size=11, anchor="start"))
    p.append(text(535, 354, "• Пікова потужність 50 мВт береться з ємності іоністора", size=11, anchor="start"))
    p.append(text(535, 381, "• При падінні до 2.0 В ключ розмикається до наступного циклу", size=11, anchor="start", color=MUTED))

    render(os.path.join(OUT, "micro-watt-dilemma.svg"), W, H, *p)


# ── Figure 2: Фізичні джерела мікроенергії ──────────────────────────────────
def fig_harvesting_sources_matrix():
    W, H = 940, 480
    p = []

    p.append(text(470, 28, "Порівняння фізичних джерел збору мікроенергії", size=15, bold=True))

    cards = [
        ("Термоелектричні (TEG)", 30, NEG, [
            ("Фізика", "Ефект Зеєбека на p-n термопарах Bi2Te3"),
            ("Вхідна дія", "Різниця температур deltaT = 3..5 °C"),
            ("Вихідна ЕРС", "20..120 мВ (наднапруга вниз)"),
            ("Внутрішній опір", "Низький: R_teg = 2..8 Ом"),
            ("Потужність", "10..50 мкВт"),
            ("Вимога PMIC", "Холодний старт від 100 мВ, MPPT = 50% Voc")
        ]),
        ("П'єзоелектричні (PZT)", 335, POS, [
            ("Фізика", "Прямий п'єзоефект на консольній балці"),
            ("Вхідна дія", "Вібрація верстатів / двигунів 50..120 Гц"),
            ("Вихідна ЕРС", "5..30 В (змінний струм AC)"),
            ("Внутрішній опір", "Високий ємнісний: 20..100 кОм"),
            ("Потужність", "10..100 мкВт"),
            ("Вимога PMIC", "Синхронний AC/DC випрямляч, Buck-ступінь")
        ]),
        ("Indoor фотовольтаїка", 640, FIELD, [
            ("Фізика", "Фотоефект в аморфному кремнії (a-Si) / DSSC"),
            ("Вхідна дія", "Штучне світло офісу (200..500 люкс)"),
            ("Вихідна ЕРС", "1.5..2.5 В (постійний струм DC)"),
            ("Внутрішній опір", "Нелінійна ВАХ, I_sc = 5..25 мкА"),
            ("Потужність", "5..20 мкВт / см2"),
            ("Вимога PMIC", "Апаратний FOCV MPPT = 75..80% Voc")
        ])
    ]

    for title_text, x, color_accent, rows in cards:
        p.append(rect(x, 50, 270, 410, fill="#f8fafc", stroke=color_accent, sw=1.5, rx=8))
        p.append(rect(x + 10, 60, 250, 36, fill="#ffffff", stroke=color_accent, sw=1, rx=6))
        p.append(text(x + 135, 83, title_text, size=12, bold=True, color=color_accent))

        for idx, (label, val) in enumerate(rows):
            y_pos = 118 + idx * 56
            p.append(rect(x + 10, y_pos, 250, 48, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
            p.append(text(x + 20, y_pos + 18, label + ":", size=10, bold=True, color=MUTED, anchor="start"))
            p.append(text(x + 20, y_pos + 36, val, size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "harvesting-sources-matrix.svg"), W, H, *p)


# ── Figure 3: Архітектура наноекономічного PMIC ─────────────────────────────
def fig_eh_pmic_architecture():
    W, H = 940, 500
    p = []

    p.append(text(470, 26, "Внутрішня структура наноекономічного PMIC (BQ25570 / ADP5091)", size=15, bold=True))

    # Зовнішній контур PMIC
    p.append(rect(180, 50, 580, 430, fill="#f8fafc", stroke=LINE, sw=1.8, rx=10))
    p.append(text(470, 75, "EH PMIC (Власний струм спокою I_q < 300 нА)", size=13, bold=True, color=NEG))

    # Джерело зліва
    p.append(rect(20, 180, 120, 100, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(80, 215, "Джерело збору", size=11, bold=True))
    p.append(text(80, 235, "TEG / Solar / PZT", size=10, color=MUTED))
    p.append(text(80, 255, "U_in = 0.1..2.0 В", size=10, color=FIELD))

    p.append(arrow(140, 230, 210, 230, color=FIELD, sw=2))
    p.append(text(175, 220, "VIN", size=10, bold=True))

    # Блоки всередині PMIC
    # 1. Холодний старт
    p.append(rect(210, 110, 240, 80, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(330, 135, "Холодний старт (Cold-Start)", size=11, bold=True, color=POS))
    p.append(text(330, 155, "Автогенератор від 100..330 мВ", size=10, color=MUTED))
    p.append(text(330, 173, "ККД ~ 15..25% до U_stor = 1.8 В", size=9, color=INK))

    # 2. Головний Boost + MPPT
    p.append(rect(210, 210, 240, 110, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(330, 235, "Головний Boost-перетворювач", size=11, bold=True, color=NEG))
    p.append(text(330, 255, "Синхронний ключ (ККД 80..90%)", size=10, color=INK))
    p.append(text(330, 275, "FOCV MPPT (семплування 16 с)", size=10, color=MUTED))
    p.append(text(330, 295, "Опорний конденсатор VREF_SAMP", size=9, color=FIELD))

    # 3. Супервізор напруги
    p.append(rect(210, 340, 240, 115, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(330, 365, "Нановольтовий супервізор", size=11, bold=True))
    p.append(text(330, 387, "V_OV = 3.6 В (Захист від перезаряду)", size=9, color=POS))
    p.append(text(330, 407, "V_OK_HYST: Увімк 3.3 В / Вимк 2.0 В", size=9, color=FIELD))
    p.append(text(330, 427, "Компаратори зі струмом < 50 нА", size=9, color=MUTED))

    # 4. Внутрішня шина V_STOR та лічильник
    p.append(rect(485, 110, 245, 180, fill="#eff6ff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(607, 135, "Керування накопичувачем", size=11, bold=True, color=NEG))
    p.append(text(607, 158, "Шина V_STOR (2.0..3.6 В)", size=10, color=INK))
    p.append(text(607, 180, "Ключ захисту батареї / іоністора", size=9, color=MUTED))

    # 5. Вихідний Buck / Load Switch
    p.append(rect(485, 310, 245, 145, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(607, 335, "Вихідний Buck / Ключ навантаження", size=11, bold=True, color=FIELD))
    p.append(text(607, 358, "Стабілізована шина V_OUT (3.0 В / 1.8 В)", size=9, color=INK))
    p.append(text(607, 380, "Керується сигналом VBAT_OK", size=9, color=MUTED))
    p.append(text(607, 402, "I_q_buck < 150 нА", size=9, color=FIELD))

    # З'єднання до Накопичувача вгорі праворуч
    p.append(rect(800, 110, 120, 90, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(860, 145, "Іоністор", size=11, bold=True))
    p.append(text(860, 165, "0.047..0.22 Ф", size=10, color=NEG))
    p.append(text(860, 183, "Буфер енергії", size=9, color=MUTED))

    p.append(arrow(730, 155, 800, 155, color=NEG, sw=2))
    p.append(text(765, 145, "VBAT", size=10, bold=True))

    # З'єднання до Навантаження внизу праворуч
    p.append(rect(800, 330, 120, 110, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(860, 360, "MCU + Давачі", size=11, bold=True))
    p.append(text(860, 380, "BLE / Sub-GHz", size=10, color=FIELD))
    p.append(text(860, 400, "V_OUT = 3.0 В", size=9, color=INK))
    p.append(text(860, 420, "VBAT_OK прапорець", size=9, color=POS))

    p.append(arrow(730, 375, 800, 375, color=FIELD, sw=2))
    p.append(text(765, 365, "VOUT", size=10, bold=True))

    p.append(arrow(730, 420, 800, 420, color=POS, sw=1.5))
    p.append(text(765, 410, "VBAT_OK", size=9, bold=True, color=POS))

    render(os.path.join(OUT, "eh-pmic-architecture.svg"), W, H, *p)


# ── Figure 4: Саморозряд іоністора та асимптотична пастка ─────────────────────
def fig_supercap_leakage_trap():
    W, H = 940, 470
    p = []

    p.append(text(470, 26, "Фізика саморозряду іоністора та асимптотична пастка заряду", size=15, bold=True))

    # Осі графіка зліва
    ox, oy = 80, 400
    gw, gh = 460, 320

    p.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    p.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))

    p.append(text(ox + gw - 20, oy + 25, "Час накопичення t", size=11, bold=True))
    p.append(text(ox - 35, oy - gh + 20, "Напруга V", size=11, bold=True, anchor="middle"))

    # Порогові лінії
    # V_UVLO_high = 3.3V
    y_high = oy - 240
    p.append(line(ox, y_high, ox + gw, y_high, color=FIELD, sw=1.2, dash="5,4"))
    p.append(text(ox - 10, y_high + 4, "3.3 В (V_ON)", size=10, bold=True, color=FIELD, anchor="end"))

    # V_UVLO_low = 2.0V
    y_low = oy - 120
    p.append(line(ox, y_low, ox + gw, y_low, color=POS, sw=1.2, dash="5,4"))
    p.append(text(ox - 10, y_low + 4, "2.0 В (V_OFF)", size=10, bold=True, color=POS, anchor="end"))

    # Крива 1: Ідеальний конденсатор (без витоку)
    p.append(path("M 80 400 Q 200 220 320 160", stroke="#94a3b8", sw=2, fill="none"))
    p.append(text(280, 180, "Ідеальний C (I_leak = 0)", size=10, color="#64748b"))

    # Крива 2: Оптимальний іоністор 0.047 Ф (струм витоку < 1 мкА)
    p.append(path("M 80 400 Q 220 250 420 160", stroke=FIELD, sw=2.5, fill="none"))
    p.append(text(435, 155, "Оптимальний C = 47 мФ (успішний старт)", size=10, bold=True, color=FIELD, anchor="start"))

    # Крива 3: Завеликий іоністор 1.0 Ф (асимптотична пастка I_leak = I_harvest при 2.8 В)
    y_stall = oy - 180
    p.append(line(ox, y_stall, ox + gw, y_stall, color=POS, sw=1, dash="3,3"))
    p.append(text(ox + gw - 10, y_stall - 8, "V_stall = 2.8 В (I_harvest = I_leak)", size=9, bold=True, color=POS, anchor="end"))

    p.append(path("M 80 400 Q 250 250 520 220", stroke=POS, sw=2.5, fill="none"))
    p.append(text(460, 245, "C = 1.0 Ф: Застрягання в пастці", size=10, bold=True, color=POS, anchor="start"))

    # Права панель з поясненням
    p.append(rect(570, 60, 345, 360, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(742, 90, "Рівняння балансу струмів", size=13, bold=True))

    p.append(rect(585, 110, 315, 60, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    p.append(text(742, 135, "C * (dV/dt) = I_harvest - I_leak(V, T) - I_q", size=10, bold=True, color=NEG))
    p.append(text(742, 155, "Коли I_leak(V) -> I_harvest, dV/dt -> 0", size=9, color=POS))

    mechanisms = [
        ("Фарадеївський витік:", "Окисно-відновні реакції на домішках електроліту"),
        ("Діелектрична релаксація:", "Повільний перерозподіл заряду в мікропорах вуглецю"),
        ("Температурний вплив:", "Струм витоку подвоюється кожні +10 °C"),
        ("Правило вибору C:", "I_leak(V_max) <= 0.25 * I_harvest")
    ]

    for idx, (head_txt, desc_txt) in enumerate(mechanisms):
        y_m = 185 + idx * 56
        p.append(text(590, y_m + 16, head_txt, size=10, bold=True, color=INK, anchor="start"))
        p.append(text(590, y_m + 34, desc_txt, size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "supercap-leakage-trap.svg"), W, H, *p)


# ── Figure 5: Парадигма переривчастих обчислень ──────────────────────────────
def fig_intermittent_execution_model():
    W, H = 940, 480
    p = []

    p.append(text(470, 26, "Хронологія переривчастого обчислення (Intermittent Computing) з FRAM", size=15, bold=True))

    # Схема часових інтервалів
    steps = [
        ("1. Накопичення", 40, 160, "#f1f5f9", LINE, "MCU вимкнено\nКонденсатор заряджається\n2.0 В -> 3.3 В"),
        ("2. Старт / Відновлення", 210, 160, "#eff6ff", NEG, "VBAT_OK = HIGH\nВідновлення стану з FRAM\nІніціалізація ядра"),
        ("3. Виконання задачі", 380, 180, "#f0fdf4", FIELD, "Обчислення / сенсор\nТранзакційна зміна даних\nV_cap падає до 2.4 В"),
        ("4. Раннє попередження", 570, 170, "#fffbeb", POS, "Переривання V_warn\nЗбереження чекпоінту\nАтомарний коміт у FRAM"),
        ("5. Знеструмлення", 750, 150, "#fef2f2", POS, "V_cap < 2.0 В\nMCU гасне без втрати даних\nПовернення до кроку 1")
    ]

    for title_txt, x, width, fill_c, stroke_c, desc in steps:
        p.append(rect(x, 60, width, 140, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        p.append(text(x + width/2, 85, title_txt, size=11, bold=True, color=stroke_c))
        
        lines = desc.split("\n")
        for i, l in enumerate(lines):
            p.append(text(x + width/2, 115 + i * 20, l, size=9, color=INK))

    # Нижній графік напруги та стану пам'яті
    gy = 410
    p.append(line(40, gy, 900, gy, color=LINE, sw=1.5))
    p.append(text(890, gy + 20, "Час", size=10, bold=True, anchor="end"))

    # Графік V_cap
    # Заряд 40 -> 210
    p.append(path("M 40 400 L 210 270", stroke=FIELD, sw=2, fill="none"))
    # Робота 210 -> 750
    p.append(path("M 210 270 L 570 330 L 750 400", stroke=POS, sw=2, fill="none"))
    # Наступний заряд 750 -> 900
    p.append(path("M 750 400 L 900 290", stroke=FIELD, sw=2, fill="none"))

    # Рівні
    p.append(line(40, 270, 900, 270, color=FIELD, sw=1, dash="4,3"))
    p.append(text(35, 274, "3.3 В (V_ON)", size=9, bold=True, color=FIELD, anchor="end"))

    p.append(line(40, 330, 900, 330, color="#d97706", sw=1, dash="4,3"))
    p.append(text(35, 334, "2.4 В (V_WARN)", size=9, bold=True, color="#d97706", anchor="end"))

    p.append(line(40, 400, 900, 400, color=POS, sw=1, dash="4,3"))
    p.append(text(35, 404, "2.0 В (V_OFF)", size=9, bold=True, color=POS, anchor="end"))

    # Підписи станів на графіку
    p.append(text(125, 360, "Накопичення", size=10, color=MUTED))
    p.append(text(390, 290, "Активна робота", size=10, bold=True, color=FIELD))
    p.append(text(660, 350, "Чекпоінт у FRAM", size=10, bold=True, color=POS))
    p.append(text(825, 360, "Накопичення #2", size=10, color=MUTED))

    # Рамка про перевагу FRAM
    p.append(rect(40, 435, 860, 35, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
    p.append(text(470, 458, "Енергія запису FRAM: < 1 нДж / байт (Flash: ~ 50 мкДж / байт) | Час запису: < 50 нс без затримок стирання секторів", size=9, color=INK))

    render(os.path.join(OUT, "intermittent-execution-model.svg"), W, H, *p)


if __name__ == "__main__":
    fig_micro_watt_dilemma()
    fig_harvesting_sources_matrix()
    fig_eh_pmic_architecture()
    fig_supercap_leakage_trap()
    fig_intermittent_execution_model()
    print("All figures generated successfully.")
