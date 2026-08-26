# -*- coding: utf-8 -*-
"""Фігури для статті «Де ламається насправді: роз'єм, дріт, пайка, гвинт» (de-lamaietsia-naspravdi).
Генерує SVG у ./img/ за допомогою svgkit.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "scripts"))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from svgkit import (
    render, text, mtext, rect, line, arrow, circle, fitbox,
    INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG
)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

# Кольорова палітра для механічних та фізичних вузлів
CLR_FAIL = "#b91c1c"      # Червоний: руйнування / відмова
CLR_WARN = "#d97706"      # Бурштиновий: контактні проблеми / зсув
CLR_OK   = "#047857"      # Зелений: правильний монтаж / фіксація
CLR_BLUE = "#1d4ed8"      # Синій: кремній / плата / термомеханіка
CLR_PURP = "#6d28d9"      # Фіолетовий: кріплення / гвинти
CARD_BG  = "#ffffff"
HDR_BG   = "#f8fafc"


def fig_failure_distribution():
    """1. failure-distribution.svg — Статистика та природа польових поломок електроніки."""
    W, H = 840, 480
    parts = []

    # Загальна рамка
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Розподіл причин польових відмов електроніки (Interconnect & Hardware Failures)", size=15, color=INK, bold=True))

    cards = [
        ("40%", "Роз'єми, кабелі, джгути", CLR_FAIL, "#fee2e2", [
            "• Втома міді у точці вигину (без Strain Relief)",
            "• Фретінг-корозія контактів (мікровібрації)",
            "• Перетирання ізоляції об гострі крайки корпусу",
            "• Виривання контактних гнізд і паяних пінів"
        ]),
        ("30%", "Паяні з'єднання та плата", CLR_WARN, "#fef3c7", [
            "• Термічна втома безсвинцевого припою SAC305",
            "• Тріщини кераміки MLCC (Flex Cracking при вигині)",
            "• Злам пайки важких дроселів та електролітів",
            "• Розтріскування перехідних отворів (Vias Z-axis)"
        ]),
        ("15%", "Гвинти, стійки, механіка", CLR_PURP, "#ede9fe", [
            "• Саморозкручування різьби від поперечної вібрації",
            "• Руйнування пластикових бонок при перетяжці",
            "• Втрата зусилля затиску (просідання шайб Гровера)",
            "• Втомне руйнування кронштейнів та розгерметизація"
        ]),
        ("15%", "Кремній та активні чипи", CLR_BLUE, "#dbeafe", [
            "• Електростатичний розряд (ESD по відкритих лініях)",
            "• Електричне перенапруження (EOS) та пробій затвора",
            "• Перегрів кристала (Thermal Runaway / сухий термоінтерфейс)",
            "• Деградація затворів (NBTI/HCI) після років роботи"
        ])
    ]

    card_w = 190
    card_h = 280
    start_x = 25
    gap_x = 10
    start_y = 65

    for i, (pct, title, clr, bg_hdr, items) in enumerate(cards):
        cx = start_x + i * (card_w + gap_x)
        # Фон картки
        parts.append(rect(cx, start_y, card_w, card_h, fill=CARD_BG, stroke=clr, sw=1.5, rx=8))
        # Шапка картки
        parts.append(rect(cx, start_y, card_w, 46, fill=bg_hdr, stroke=clr, sw=1.5, rx=8))
        parts.append(text(cx + card_w / 2, start_y + 22, pct, size=18, color=clr, bold=True))
        parts.append(text(cx + card_w / 2, start_y + 38, title, size=10, color=INK, bold=True))

        for j, itm in enumerate(items):
            # Текст елементів
            parts.append(text(cx + 8, start_y + 68 + j * 50, itm, size=9.5, color=INK, anchor="start"))

    # Підсумковий висновок внизу
    bx, by, bw, bh = 25, 360, W - 50, 95
    parts.append(rect(bx, by, bw, bh, fill="#ffffff", stroke="#0f172a", sw=1.5, rx=8))
    parts.append(rect(bx, by, bw, 26, fill="#0f172a", stroke="#0f172a", sw=1.5, rx=8))
    parts.append(text(bx + bw / 2, by + 18, "Ключовий інженерний висновок: 85% відмов лежать за межами мікроконтролера", size=12, color="#ffffff", bold=True))

    sum_lines = [
        "• Кремній практично не має рухомих частин і відмовляє рідко, якщо дотримано напруги та температури.",
        "• Головні вороги надійності — механічні напруження, знакозмінний вигин, терморозширення (CTE) та вібраційне послаблення.",
        "• Надійність приладу в полі визначається якістю кабельного вводу, геометрією плати біля гвинтів та фіксацією різьби."
    ]
    for k, sln in enumerate(sum_lines):
        parts.append(text(bx + 15, by + 45 + k * 17, sln, size=10, color=INK, anchor="start"))

    return render(out("failure-distribution.svg"), W, H, *parts)


def fig_cable_strain_fretting():
    """2. cable-strain-fretting.svg — Фізика втоми кабелів та фретінг-корозія контактів."""
    W, H = 840, 500
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Механіка кабельних вводів: концентрація напружень та фретінг-корозія", size=15, color=INK, bold=True))

    # Ліва панель: Розвантаження натягу (Strain Relief)
    pw = 390
    ph = 415
    lx = 22
    ly = 60
    parts.append(rect(lx, ly, pw, ph, fill=CARD_BG, stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(rect(lx, ly, pw, 32, fill="#e2e8f0", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(lx + pw / 2, ly + 21, "1. Втома мідних жил та розвантаження натягу (Strain Relief)", size=12, color=INK, bold=True))

    # Небезпечний випадок
    parts.append(rect(lx + 15, ly + 45, pw - 30, 160, fill="#fef2f2", stroke=CLR_FAIL, sw=1.2, rx=6))
    parts.append(text(lx + 25, ly + 65, "НЕПРАВИЛЬНО: Жорсткий вигин без демпфера", size=11, color=CLR_FAIL, bold=True, anchor="start"))
    parts.append(text(lx + 25, ly + 85, "• Кабель вільно згинається об гострий отвір корпусу / край плати", size=10, color=INK, anchor="start"))
    parts.append(text(lx + 25, ly + 103, "• Радіус вигину R < 2·D (критична концентрація напружень)", size=10, color=INK, anchor="start"))
    parts.append(text(lx + 25, ly + 121, "• Знакозмінний вигин створює наклеп міді (робота дислокацій)", size=10, color=INK, anchor="start"))
    parts.append(text(lx + 25, ly + 139, "• Результат: злам жили за 10 000–50 000 циклів просто біля пайки", size=10, color=CLR_FAIL, bold=True, anchor="start"))
    parts.append(text(lx + 25, ly + 157, "• Немає фіксації зовнішньої оболонки -> натяг рве паяні піни", size=10, color=INK, anchor="start"))
    parts.append(text(lx + 25, ly + 175, "• Вібрація джгута передається безпосередньо на роз'єм", size=10, color=INK, anchor="start"))

    # Правильний випадок
    parts.append(rect(lx + 15, ly + 220, pw - 30, 175, fill="#f0fdf4", stroke=CLR_OK, sw=1.2, rx=6))
    parts.append(text(lx + 25, ly + 240, "ПРАВИЛЬНО: Багаторівневий Strain Relief", size=11, color=CLR_OK, bold=True, anchor="start"))
    parts.append(text(lx + 25, ly + 260, "• Еластична конічна гільза (Grommet/Boot) обмежує радіус R > 6·D", size=10, color=INK, anchor="start"))
    parts.append(text(lx + 25, ly + 278, "• Механічний цанговий кабельний ввід (Cable Gland IP67/68)", size=10, color=INK, anchor="start"))
    parts.append(text(lx + 25, ly + 296, "• Зовнішня оболонка затиснута хомутом до шасі корпусу", size=10, color=INK, anchor="start"))
    parts.append(text(lx + 25, ly + 314, "• Вільна сервісна петля (Service Loop) перед платою знімає натяг", size=10, color=INK, anchor="start"))
    parts.append(text(lx + 25, ly + 332, "• Багатожильний дріт підвищеної гнучкості (Class 5/6, силікон)", size=10, color=CLR_OK, bold=True, anchor="start"))
    parts.append(text(lx + 25, ly + 350, "• Ресурс вигину зростає у 50–100 разів (> 1 000 000 циклів)", size=10, color=INK, anchor="start"))

    # Права панель: Фретінг-корозія (Fretting Corrosion)
    rx = 428
    ry = 60
    parts.append(rect(rx, ry, pw, ph, fill=CARD_BG, stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(rect(rx, ry, pw, 32, fill="#e2e8f0", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(rx + pw / 2, ry + 21, "2. Контактна фретінг-корозія (Fretting Corrosion)", size=12, color=INK, bold=True))

    steps = [
        ("Етап 1: Мікровібрація (1–100 мкм)", CLR_WARN, [
            "Вібрація або циклічне нагрівання викликають",
            "мікропереміщення штиря відносно гнізда роз'єму."
        ]),
        ("Етап 2: Стирання та окиснення", CLR_WARN, [
            "Тертя зриває м'який пасивний шар олова (Sn).",
            "Оголений метал миттєво окиснюється киснем у SnO2."
        ]),
        ("Етап 3: Накопичення оксидного порошку", CLR_FAIL, [
            "SnO2 — твердий абразивний діелектрик. Накопичується",
            "в зоні контакту, розклинюючи контактні пружини."
        ]),
        ("Етап 4: Плаваючий контакт (Contact Bounce)", CLR_FAIL, [
            "Опір зростає з 10 мОм до > 100 Ом і стрибає.",
            "Прошивка ловить фантомні падіння шин I2C/SPI або скидання."
        ])
    ]

    for k, (stitle, sclr, slines) in enumerate(steps):
        sy = ry + 45 + k * 85
        parts.append(rect(rx + 15, sy, pw - 30, 75, fill="#fffbeb", stroke=sclr, sw=1.2, rx=6))
        parts.append(text(rx + 25, sy + 18, stitle, size=11, color=sclr, bold=True, anchor="start"))
        for m, ln in enumerate(slines):
            parts.append(text(rx + 25, sy + 36 + m * 16, ln, size=9.5, color=INK, anchor="start"))

    return render(out("cable-strain-fretting.svg"), W, H, *parts)


def fig_solder_fatigue_mlcc():
    """3. solder-fatigue-mlcc.svg — Термічна втома пайки SAC305 та Flex Cracking MLCC."""
    W, H = 840, 520
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Руйнування на друкованій платі: втома припою SAC305 та вигин MLCC", size=15, color=INK, bold=True))

    pw = 390
    ph = 435
    lx = 22
    ly = 60

    # Ліва панель: Втома припою SAC305
    parts.append(rect(lx, ly, pw, ph, fill=CARD_BG, stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(rect(lx, ly, pw, 32, fill="#e2e8f0", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(lx + pw / 2, ly + 21, "1. Термічна втома SAC305 (CTE Mismatch)", size=12, color=INK, bold=True))

    solder_blocks = [
        ("Фізичний механізм різниці КТР (CTE)", CLR_BLUE, [
            "• Текстоліт FR-4 розширюється з коефіцієнтом 14–17 ppm/°C.",
            "• Керамічний чип / кремній має КТР лише 3–7 ppm/°C.",
            "• При зміні температури (ΔT) виникає потужний зсув пайки:",
            "  ΔL = L · (CTE_pcb − CTE_chip) · ΔT"
        ]),
        ("Чому SAC305 ламається швидше за Sn63Pb37", CLR_WARN, [
            "• Безсвинцевий SAC305 (Sn96.5 Ag3.0 Cu0.5) значно жорсткіший.",
            "• Модуль пружності E = 50 ГПа проти 32 ГПа у свинцевого.",
            "• Інтерметаліди (Cu6Sn5, Ni3Sn4) утворюють крихкий шар.",
            "• Припой не розвантажує напруження пластично, а накопичує тріщини."
        ]),
        ("Інженерний захист паяних з'єднань", CLR_OK, [
            "• Зниження ΔT за рахунок тепловідводу й правильного корпусу.",
            "• Підливка компаунду Underfill під великі BGA/QFN чипи.",
            "• Спеціальні виводи (Gull-wing) замість жорстких плоских паянь.",
            "• Фіксація силіконом (RTV Staking) важких конденсаторів і дроселів."
        ])
    ]

    for k, (btitle, bclr, blines) in enumerate(solder_blocks):
        by = ly + 45 + k * 125
        parts.append(rect(lx + 15, by, pw - 30, 115, fill="#f8fafc", stroke=bclr, sw=1.2, rx=6))
        parts.append(text(lx + 25, by + 18, btitle, size=11, color=bclr, bold=True, anchor="start"))
        for m, ln in enumerate(blines):
            parts.append(text(lx + 25, by + 37 + m * 17, ln, size=9.5, color=INK, anchor="start"))

    # Права панель: Flex Cracking MLCC
    rx = 428
    ry = 60
    parts.append(rect(rx, ry, pw, ph, fill=CARD_BG, stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(rect(rx, ry, pw, 32, fill="#e2e8f0", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(rx + pw / 2, ry + 21, "2. Тріщини кераміки MLCC (Flex Cracking)", size=12, color=INK, bold=True))

    mlcc_blocks = [
        ("Крихкість кераміки BaTiO3 та вигин плати", CLR_FAIL, [
            "• Кераміка титанату барію має високу міцність на стиск,",
            "  але вкрай низьку міцність на розтяг (< 100 МПа).",
            "• При вигині плати паяний шов тягне зовнішній шар кераміки.",
            "• Виникає характерна тріщина під кутом 45° від паяльної галтелі."
        ]),
        ("Катастрофічний режим відмови: КЗ живлення", CLR_FAIL, [
            "• Тріщина перетинає внутрішні протилежні електроди.",
            "• Волога з повітря проникає в тріщину -> дендритний ріст.",
            "• Конденсатор перетворюється на резистор 1–10 Ом, гріється,",
            "  спричиняє вигоряння плати або коротке замикання батареї."
        ]),
        ("Правила топології PCB проти Flex Cracking", CLR_OK, [
            "• Орієнтація: розташовувати MLCC паралельно осі вигину плати.",
            "• Відстань > 5–10 мм від отворів гвинтів, роз'ємів і ліній скрайбування.",
            "• Використання Soft-Termination (полімерні еластичні виводи).",
            "• Розвантажувальні фрезеровані пази (Slots) біля зон механічного тиску."
        ])
    ]

    for k, (mtitle, mclr, mlines) in enumerate(mlcc_blocks):
        my = ry + 45 + k * 125
        parts.append(rect(rx + 15, my, pw - 30, 115, fill="#f8fafc", stroke=mclr, sw=1.2, rx=6))
        parts.append(text(rx + 25, my + 18, mtitle, size=11, color=mclr, bold=True, anchor="start"))
        for m, ln in enumerate(mlines):
            parts.append(text(rx + 25, my + 37 + m * 17, ln, size=9.5, color=INK, anchor="start"))

    return render(out("solder-fatigue-mlcc.svg"), W, H, *parts)


def fig_fastener_locking():
    """4. fastener-locking.svg — Механіка вібраційного розкручування гвинтів та методи фіксації."""
    W, H = 840, 520
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    parts.append(text(W / 2, 38, "Вібраційна стійкість кріплень: тест Юнкера та ефективні фіксатори різьби", size=15, color=INK, bold=True))

    pw = 390
    ph = 435
    lx = 22
    ly = 60

    # Ліва панель: Чому гвинти розкручуються
    parts.append(rect(lx, ly, pw, ph, fill=CARD_BG, stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(rect(lx, ly, pw, 32, fill="#fee2e2", stroke=CLR_FAIL, sw=1.5, rx=8))
    parts.append(text(lx + pw / 2, ly + 21, "1. Механізм саморозкручування (Тест Юнкера)", size=12, color=CLR_FAIL, bold=True))

    left_items = [
        ("Поперечна вібрація обнуляє тертя", CLR_FAIL, [
            "• При осьовому навантаженні тертя в різьбі утримує гвинт.",
            "• Але поперечний зсув (Transverse slip) викликає мікроковзання",
            "  витків по похилій площині різьби.",
            "• Коефіцієнт тертя миттєво падає до нуля: гвинт обертається назад."
        ]),
        ("Міф про пружинну шайбу Гровера (Split Washer)", CLR_FAIL, [
            "• Шайба Гровера сплющується при 5–10% номінального моменту.",
            "• При динамічному навантаженні вона працює як плоска пружина",
            "  з нульовим запасом ходу, а гострі крайки зрізають метал опорної поверхні.",
            "• За стандартом DIN 127 визнана застарілою і неефективною."
        ]),
        ("Наслідки ослаблення попереднього натягу", CLR_FAIL, [
            "• Втрата притиску плати до радіатора -> перегрів силових ключів.",
            "• Ударні вібрації плати об корпус -> зрізання доріжок і пайки.",
            "• Випадання гвинта всередину корпусу -> металеве КЗ по живленню."
        ])
    ]

    for k, (ltitle, lclr, llines) in enumerate(left_items):
        ly_pos = ly + 45 + k * 125
        parts.append(rect(lx + 15, ly_pos, pw - 30, 115, fill="#fef2f2", stroke=lclr, sw=1.2, rx=6))
        parts.append(text(lx + 25, ly_pos + 18, ltitle, size=11, color=lclr, bold=True, anchor="start"))
        for m, ln in enumerate(llines):
            parts.append(text(lx + 25, ly_pos + 37 + m * 17, ln, size=9.5, color=INK, anchor="start"))

    # Права панель: Надійні методи фіксації
    rx = 428
    ry = 60
    parts.append(rect(rx, ry, pw, ph, fill=CARD_BG, stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(rect(rx, ry, pw, 32, fill="#d1fae5", stroke=CLR_OK, sw=1.5, rx=8))
    parts.append(text(rx + pw / 2, ry + 21, "2. Надійні інженерні методи фіксації різьби", size=12, color=CLR_OK, bold=True))

    right_items = [
        ("Анаеробні фіксатори різьби (Threadlocker Loctite 243/270)", CLR_OK, [
            "• Рідкий мономер заповнює 100% зазору між витками різьби.",
            "• Полімеризується без кисню при контакті з іонами металу.",
            "• Створює суцільний термореактивний пластиковий замок.",
            "• Запобігає саморозкручуванню та герметизує різьбу від корозії."
        ]),
        ("Клинові шайби Nord-Lock", CLR_OK, [
            "• Пара шайб із кутом клина α, більшим за кут підйому різьби β.",
            "• Будь-яка спроба розкручування призводить до клинового ефекту",
            "  і ЗБІЛЬШЕННЯ зусилля затиску (Wedge-locking principle)."
        ]),
        ("Самоконтрасні гайки (Nyloc) та тарілчасті шайби", CLR_OK, [
            "• Нейлонове кільце створює постійний радіальний натяг на витках.",
            "• Тарілчасті пружини Бельвіля (Belleville Washers) компенсують",
            "  теплове розширення та температурне просідання матеріалів."
        ])
    ]

    for k, (rtitle, rclr, rlines) in enumerate(right_items):
        ry_pos = ry + 45 + k * 125
        parts.append(rect(rx + 15, ry_pos, pw - 30, 115, fill="#f0fdf4", stroke=rclr, sw=1.2, rx=6))
        parts.append(text(rx + 25, ry_pos + 18, rtitle, size=11, color=rclr, bold=True, anchor="start"))
        for m, ln in enumerate(rlines):
            parts.append(text(rx + 25, ry_pos + 37 + m * 17, ln, size=9.5, color=INK, anchor="start"))

    return render(out("fastener-locking.svg"), W, H, *parts)


def main():
    funcs = [
        fig_failure_distribution,
        fig_cable_strain_fretting,
        fig_solder_fatigue_mlcc,
        fig_fastener_locking,
    ]
    for func in funcs:
        p = func()
        print("Generated: %s" % p)


if __name__ == "__main__":
    main()

