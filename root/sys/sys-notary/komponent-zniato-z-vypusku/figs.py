# -*- coding: utf-8 -*-
"""figs.py — генератор ілюстрацій для теми komponent-zniato-z-vypusku (sys-notary).
Генерує 2 SVG-схеми в ./img/ за допомогою спільного svgkit.
"""
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(SCRIPT_DIR, "img"), exist_ok=True)


# ── Фігура 1: Хронологія життєвого циклу компонента, PCN/PDN та вікон LTB/LTS ────
def fig_component_lifecycle_pcn_timeline():
    W, H = 1000, 600
    P = []
    P.append(text(W / 2, 26, "Хронологія життєвого циклу компонента, сповіщень PCN/PDN та критичних вікон LTB/LTS", size=15, bold=True))

    # 1. Верхній блок: Фази життєвого циклу (Introduction -> Growth -> Maturity -> Saturation -> Decline -> EOL)
    stages = [
        ("1. Впровадження\n(Introduction)", "• Перший випуск\n• Низькі обсяги\n• Висока ціна\n• Дитячі помилки", "#eff6ff", "#2563eb"),
        ("2. Зростання\n(Growth)", "• Нарощування серії\n• Зниження собівартості\n• Розширення ланцюгів\n• Стабільні поставки", "#f0fdf4", "#16a34a"),
        ("3. Зрілість\n(Maturity)", "• Пік виробництва\n• Оптимальна ціна\n• Мінімальні ризики\n• Базовий вибір для BOM", "#f0fdf4", "#15803d"),
        ("4. Насичення\n(Saturation)", "• Уповільнення попиту\n• Поява нових чіпів\n• Оновлення ревізій\n• Перші сигнали PCN", "#fefce8", "#ca8a04"),
        ("5. Спад / EOL\n(Decline & Phase-out)", "• Згортання ліній\n• Зростання Lead Time\n• Сповіщення PDN/EOL\n• Останні замовлення", "#fff1f2", "#e11d48")
    ]

    sw = 175
    gap = 18
    x0 = 20
    y0 = 55
    sh = 135

    for i, (stitle, sdesc, fill_c, strk_c) in enumerate(stages):
        sx = x0 + i * (sw + gap)
        P.append(rect(sx, y0, sw, sh, fill=fill_c, stroke=strk_c, sw=1.8, rx=6))
        P.append(mtext(sx + sw / 2, y0 + 22, stitle, size=11, bold=True, color=strk_c, lh=1.2))
        P.append(mtext(sx + 10, y0 + 60, sdesc, size=9, color=INK, anchor="start", lh=1.3))
        if i < len(stages) - 1:
            P.append(arrow(sx + sw + 2, y0 + sh / 2, sx + sw + gap - 4, y0 + sh / 2, color="#64748b", sw=1.8))

    # 2. Середній блок: Часова шкала та вікна сповіщень (PCN -> LTB -> LTS -> Grey Market)
    P.append(rect(20, 210, 960, 190, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    P.append(text(500, 232, "КРИТИЧНІ ЧАСОВІ ВІКНА ТА ДЕДЛАЙНИ ПІСЛЯ СПОВІЩЕННЯ JEDEC J-STD-048", size=12, bold=True, color="#1e293b"))

    # Основна горизонтальна вісь часу
    axis_y = 300
    P.append(line(50, axis_y, 930, axis_y, color="#334155", sw=2.5))
    P.append(arrow(925, axis_y, 955, axis_y, color="#334155", sw=2.5))
    P.append(text(950, axis_y + 20, "Час t", size=10, bold=True, color="#334155"))

    # Мітки часу на осі
    # Точка 1: PDN / EOL Notification (T0)
    P.append(circle(140, axis_y, 6, fill="#e11d48", stroke="#881337", sw=2))
    P.append(line(140, axis_y - 45, 140, axis_y + 45, color="#e11d48", sw=1.5, dash="4,3"))
    P.append(text(140, axis_y - 52, "T0: Випуск PDN", size=10, bold=True, color="#e11d48"))
    P.append(text(140, axis_y + 60, "JEDEC J-STD-048", size=9, color="#64748b"))

    # Вікно 1: LTB Window (Last Time Buy, 6..12 міс)
    P.append(rect(140, axis_y - 25, 260, 50, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=4))
    P.append(text(270, axis_y - 5, "Вікно LTB (Last Time Buy)", size=10, bold=True, color="#b91c1c"))
    P.append(text(270, axis_y + 14, "6–12 місяців (NCNR фіксація)", size=9, color="#991b1b"))

    # Точка 2: LTB Date (Дедлайн замовлення)
    P.append(circle(400, axis_y, 6, fill="#ef4444", stroke="#991b1b", sw=2))
    P.append(line(400, axis_y - 45, 400, axis_y + 45, color="#ef4444", sw=1.5, dash="4,3"))
    P.append(text(400, axis_y - 52, "T_LTB: Дедлайн замовлення", size=10, bold=True, color="#b91c1c"))
    P.append(text(400, axis_y + 60, "Стоп прийому PO", size=9, color="#64748b"))

    # Вікно 2: LTS Window (Last Time Ship, до 12..18 міс)
    P.append(rect(400, axis_y - 25, 230, 50, fill="#fef3c7", stroke="#f59e0b", sw=1.5, rx=4))
    P.append(text(515, axis_y - 5, "Вікно LTS (Last Time Ship)", size=10, bold=True, color="#b45309"))
    P.append(text(515, axis_y + 14, "Відвантаження залишків фабів", size=9, color="#92400e"))

    # Точка 3: LTS Date (Фінальне відвантаження)
    P.append(circle(630, axis_y, 6, fill="#f59e0b", stroke="#b45309", sw=2))
    P.append(line(630, axis_y - 45, 630, axis_y + 45, color="#f59e0b", sw=1.5, dash="4,3"))
    P.append(text(630, axis_y - 52, "T_LTS: Останній випуск", size=10, bold=True, color="#b45309"))
    P.append(text(630, axis_y + 60, "Зупинка ліній чіпа", size=9, color="#64748b"))

    # Вікно 3: Пост-EOL та брокерський ринок
    P.append(rect(630, axis_y - 25, 270, 50, fill="#f3e8ff", stroke="#a855f7", sw=1.5, rx=4))
    P.append(text(765, axis_y - 5, "Пост-EOL: Буфер або Брокери", size=10, bold=True, color="#6b21a8"))
    P.append(text(765, axis_y + 14, "Високі ризики контрафакту та цін", size=9, color="#581c87"))

    # 3. Нижній блок: Три оперативні фази реагування інженерної команди
    b_y = 418
    bw = 305
    bh = 165
    bgap = 22

    # Фаза 1: Аудит
    P.append(rect(20, b_y, bw, bh, fill="#f0f9ff", stroke="#0284c7", sw=1.6, rx=6))
    P.append(text(20 + bw / 2, b_y + 22, "1. АУДИТ ТА ОЦІНКА ПОТРЕБИ", size=11, bold=True, color="#0369a1"))
    t1 = (
        "• Звірка поточного залишку BOM на складі.\n"
        "• Прогнозування річного випуску виробів.\n"
        "• Оцінка резерву на гарантійний ремонт.\n"
        "• Розрахунок дефіциту та бюджету LTB."
    )
    P.append(mtext(32, b_y + 46, t1, size=9, color=INK, anchor="start", lh=1.35))

    # Фаза 2: Логістика та збереження
    P.append(rect(20 + bw + bgap, b_y, bw, bh, fill="#fefce8", stroke="#ca8a04", sw=1.6, rx=6))
    P.append(text(20 + bw + bgap + bw / 2, b_y + 22, "2. NCNR ТА ДОВГОТРИВАЛЕ ЗБЕРІГАННЯ", size=11, bold=True, color="#a16207"))
    t2 = (
        "• Оформлення NCNR-контрактів із заводом.\n"
        "• Пакування за стандартом IPC/J-STD-033 (MSL).\n"
        "• Сухе зберігання в азоті (N2, RH < 5%).\n"
        "• Контроль деградації паяності (J-STD-002)."
    )
    P.append(mtext(20 + bw + bgap + 12, b_y + 46, t2, size=9, color=INK, anchor="start", lh=1.35))

    # Фаза 3: Заміна або редизайн
    P.append(rect(20 + (bw + bgap) * 2, b_y, bw, bh, fill="#fdf2f8", stroke="#db2777", sw=1.6, rx=6))
    P.append(text(20 + (bw + bgap) * 2 + bw / 2, b_y + 22, "3. ДЕЛЬТА-ВАЛІДАЦІЯ ТА РЕДИЗАЙН", size=11, bold=True, color="#be185d"))
    t3 = (
        "• Пошук аналогів за критеріями FFF (Pin-to-Pin).\n"
        "• Лабораторна Delta-кваліфікація (JESD47).\n"
        "• Оновлення схемотехніки / перерозведення PCB.\n"
        "• Повторна сертифікація EMC/Safety за потреби."
    )
    P.append(mtext(20 + (bw + bgap) * 2 + 12, b_y + 46, t3, size=9, color=INK, anchor="start", lh=1.35))

    render(os.path.join(SCRIPT_DIR, "img", "component-lifecycle-pcn-timeline.svg"), W, H, *P)


# ── Фігура 2: Дерево прийняття рішень для оцінки FFF-еквівалентності ─────────────
def fig_fff_equivalence_decision_tree():
    W, H = 1000, 620
    P = []
    P.append(text(W / 2, 26, "Дерево прийняття рішень для оцінки FFF-еквівалентності та обсягу кваліфікації заміни", size=15, bold=True))

    # Вхідний вузол: Аналіз альтернативного компонента
    P.append(rect(340, 50, 320, 48, fill="#eff6ff", stroke="#2563eb", sw=1.8, rx=6))
    P.append(text(500, 72, "ВХІД: Оцінка чіпа-кандидата на заміну", size=11, bold=True, color="#1d4ed8"))
    P.append(text(500, 88, "Аналіз даташиту, errata-sheet та моделей", size=9, color="#1e40af"))

    # Стрілка вниз до Рівня 1 (Form)
    P.append(arrow(500, 98, 500, 125, color="#334155", sw=1.8))

    # РІВЕНЬ 1: FORM (Форма, Корпус, Термопад, Виводи)
    P.append(rect(320, 125, 360, 62, fill="#f8fafc", stroke="#475569", sw=1.6, rx=6))
    P.append(text(500, 146, "1. ОЦІНКА ФОРМИ (FORM EQUIVALENCE)", size=11, bold=True, color="#0f172a"))
    P.append(text(500, 163, "Корпус, крок виводів, Exposed Pad, висота і маса?", size=9, color="#334155"))
    P.append(text(500, 178, "Чи підходить на наявний посадковий майданчик PCB?", size=9, color="#64748b"))

    # Розгалуження Рівня 1:
    # НІ -> Редизайн PCB або інтерпозер
    P.append(arrow(320, 156, 170, 156, color="#dc2626", sw=1.8))
    P.append(text(245, 146, "НІ (Невідповідність)", size=9, bold=True, color="#dc2626"))
    P.append(rect(20, 125, 150, 62, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=5))
    P.append(text(95, 146, "РЕДИЗАЙН PCB", size=10, bold=True, color="#991b1b"))
    P.append(text(95, 163, "Нове трасування або", size=9, color="#7f1d1d"))
    P.append(text(95, 176, "дочірня плата-адаптер", size=9, color="#7f1d1d"))

    # ТАК -> Стрілка до Рівня 2 (Fit)
    P.append(arrow(500, 187, 500, 220, color="#16a34a", sw=1.8))
    P.append(text(525, 205, "ТАК", size=9, bold=True, color="#16a34a"))

    # РІВЕНЬ 2: FIT (Цокольовка, Напруги живлення, Рівні I/O)
    P.append(rect(320, 220, 360, 62, fill="#f8fafc", stroke="#475569", sw=1.6, rx=6))
    P.append(text(500, 241, "2. ОЦІНКА ПОСАДКИ (FIT EQUIVALENCE)", size=11, bold=True, color="#0f172a"))
    P.append(text(500, 258, "Цокольовка (Pinout), VDD, допустимі струми I/O,", size=9, color="#334155"))
    P.append(text(500, 273, "полярність Enable та вимоги до ESR конденсаторів?", size=9, color="#64748b"))

    # Розгалуження Рівня 2:
    # НІ -> Доопрацювання схеми / обв'язки
    P.append(arrow(680, 251, 830, 251, color="#d97706", sw=1.8))
    P.append(text(755, 241, "НІ (Частково)", size=9, bold=True, color="#d97706"))
    P.append(rect(830, 220, 150, 62, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=5))
    P.append(text(905, 241, "ЗМІНА ОБВ'ЯЗКИ", size=10, bold=True, color="#92400e"))
    P.append(text(905, 258, "Дільники напруг, LDO,", size=9, color="#78350f"))
    P.append(text(905, 271, "інвертори сигналів", size=9, color="#78350f"))

    # ТАК -> Стрілка до Рівня 3 (Function)
    P.append(arrow(500, 282, 500, 315, color="#16a34a", sw=1.8))
    P.append(text(525, 300, "ТАК", size=9, bold=True, color="#16a34a"))

    # РІВЕНЬ 3: FUNCTION (Динамічні таймінги, Регістри, Errata, Тепло)
    P.append(rect(320, 315, 360, 62, fill="#f8fafc", stroke="#475569", sw=1.6, rx=6))
    P.append(text(500, 336, "3. ОЦІНКА ФУНКЦІЇ (FUNCTION EQUIVALENCE)", size=11, bold=True, color="#0f172a"))
    P.append(text(500, 353, "Часові діаграми, регістрове відображення, пропускна", size=9, color="#334155"))
    P.append(text(500, 368, "здатність, Errata, тепловий опір theta_JA?", size=9, color="#64748b"))

    # Розгалуження Рівня 3:
    # НІ -> Патч прошивки HAL / обмеження режимів
    P.append(arrow(320, 346, 170, 346, color="#9333ea", sw=1.8))
    P.append(text(245, 336, "НІ (Програмно)", size=9, bold=True, color="#9333ea"))
    P.append(rect(20, 315, 150, 62, fill="#faf5ff", stroke="#9333ea", sw=1.5, rx=5))
    P.append(text(95, 336, "АДАПТАЦІЯ HAL", size=10, bold=True, color="#6b21a8"))
    P.append(text(95, 353, "Патч прошивки, зміна", size=9, color="#581c87"))
    P.append(text(95, 366, "таймінгів SPI/I2C/CAN", size=9, color="#581c87"))

    # ТАК -> Стрілка до Прямої заміни (Drop-in)
    P.append(arrow(500, 377, 500, 410, color="#16a34a", sw=1.8))
    P.append(text(525, 395, "ТАК", size=9, bold=True, color="#16a34a"))

    # Вузол 4: ПОВНА ПРЯМА ЗАМІНА (DROP-IN COMPATIBLE)
    P.append(rect(300, 410, 400, 48, fill="#f0fdf4", stroke="#16a34a", sw=2, rx=6))
    P.append(text(500, 430, "ПРЯМА ЗАМІНА 1:1 (DROP-IN EQUIVALENT)", size=11, bold=True, color="#15803d"))
    P.append(text(500, 447, "Повна FFF сумісність: допуск до дельта-кваліфікації", size=9, color="#166534"))

    # Стрілка вниз до матриці дельта-кваліфікації
    P.append(arrow(500, 458, 500, 480, color="#16a34a", sw=1.8))

    # Нижній блок: Матриця обсягу обов'язкової Дельта-кваліфікації
    P.append(rect(20, 480, 960, 125, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    P.append(text(500, 502, "ПРОГРАМА ОБОВ'ЯЗКОВОЇ ДЕЛЬТА-КВАЛІФІКАЦІЇ ЗАМІНИ (DELTA QUALIFICATION PLAN)", size=11, bold=True, color="#1e293b"))

    cols = [
        ("1. Параметричні тести", "• Споживання IDDq у спокої\n• Рівні витоків на портах I/O\n• Швидкість наростання Slew-Rate\n• Вольт-амперні характеристики", "#eff6ff", "#0284c7"),
        ("2. Стрес-випробування", "• Термоцикли: -40..+85 °C\n• Тривалий прогін під Burn-in\n• Вібраційні навантаження\n• Тест паяності та змочування", "#f0fdf4", "#16a34a"),
        ("3. ЕМС та безпека", "• Емісія випромінювання CISPR 32\n• Стійкість до ESD (IEC 61000-4-2)\n• Стійкість до EFT наносекундних пачок\n• Аудит файлу технічного досьє", "#faf5ff", "#9333ea")
    ]

    cw = 300
    cgap = 20
    cx0 = 35
    cy0 = 515

    for i, (ctitle, cdesc, cfill, cstrk) in enumerate(cols):
        ccx = cx0 + i * (cw + cgap)
        P.append(rect(ccx, cy0, cw, 78, fill=cfill, stroke=cstrk, sw=1.2, rx=5))
        P.append(text(ccx + cw / 2, cy0 + 18, ctitle, size=10, bold=True, color=cstrk))
        P.append(mtext(ccx + 10, cy0 + 35, cdesc, size=9, color=INK, anchor="start", lh=1.3))

    render(os.path.join(SCRIPT_DIR, "img", "fff-equivalence-decision-tree.svg"), W, H, *P)


if __name__ == "__main__":
    fig_component_lifecycle_pcn_timeline()
    fig_fff_equivalence_decision_tree()
    print("Фігури успішно згенеровано.")
