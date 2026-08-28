# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Декларація відповідності й технічний файл»."""
import sys, os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_doc_vs_technical_file():
    """Фігура 1: DoC (публічна верхівка) проти Технічного файлу (підводний масив інженерних доказів)."""
    w, h = 960, 520
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Анатомія сертифікаційного досьє: Публічна декларація та Технічний файл", size=16, bold=True))

    # Верхня зона: Публічна Декларація відповідності (DoC)
    frags.append(rect(40, 55, 880, 150, fill="#edf4fc", stroke="#2457d6", sw=2, rx=8))
    frags.append(text(60, 80, "ПУБЛІЧНИЙ РІВЕНЬ: Декларація відповідності (EU Declaration of Conformity — DoC)", size=14, color="#2457d6", anchor="start", bold=True))
    frags.append(text(60, 100, "1–2 сторінки • Юридично обов'язковий документ під одноосібну відповідальність керівника", size=12, color=MUTED, anchor="start"))

    # Блоки всередині DoC
    b_w = 200
    b_h = 75
    frags.append(fitbox(55, 115, b_w, b_h, "Ідентифікація виробу\nМодель, тип, артикул,\nсерійний номер/партія,\nфото та опис призначення", size=11, fill="#ffffff", stroke="#2457d6"))
    frags.append(fitbox(270, 115, b_w, b_h, "Виробник / Представник\nЮридична назва компанії,\nофіційна адреса в ЄС,\nзаява про відповідальність", size=11, fill="#ffffff", stroke="#2457d6"))
    frags.append(fitbox(485, 115, b_w, b_h, "Директиви та Стандарти\nПерелік (RED, LVD, EMC, RoHS)\nта точні версії стандартів\n(EN 300 328, EN 62368-1)", size=11, fill="#ffffff", stroke="#2457d6"))
    frags.append(fitbox(700, 115, b_w, b_h, "Підпис і Нотифікація\nСертифікат Notified Body (якщо є),\nПІБ, посада (CEO/CTO),\nдата, місце та підпис", size=11, fill="#ffffff", stroke="#2457d6"))

    # Лінія розділу ("Ватерлінія")
    frags.append(line(40, 225, 920, 225, color="#c0392b", sw=2, dash="6,4"))
    frags.append(text(w / 2, 220, "▼  DoC спирається на внутрішній інженерний масив доказів  ▼", size=12, color="#c0392b", bold=True))

    # Нижня зона: Технічний файл (Technical Documentation File)
    frags.append(rect(40, 245, 880, 255, fill="#f8fafc", stroke="#334155", sw=2, rx=8))
    frags.append(text(60, 270, "ВНУТРІШНІЙ РІВЕНЬ: Технічний файл (Technical Documentation File — TDF)", size=14, color="#1e293b", anchor="start", bold=True))
    frags.append(text(60, 290, "50–300+ сторінок • Конфіденційне досьє інженерних розрахунків, схем, протоколів випробувань та оцінки ризиків", size=12, color=MUTED, anchor="start"))

    # 4 стовпці технічного файлу
    c_w = 200
    c_h = 175
    y_pos = 305

    c1_txt = "1. Схеми й Архітектура\n• Принципові схеми (SCH)\n• Топологія плат (Gerber)\n• Специфікація BOM\n• Блок-схеми та опис роботи\n• Версії прошивки/HW"
    frags.append(fitbox(55, y_pos, c_w, c_h, c1_txt, size=11, fill="#ffffff", stroke="#94a3b8"))

    c2_txt = "2. Оцінка ризиків\n• Матриця ризиків (ISO 12100)\n• Електробезпека (EN 62368-1)\n• Тепловий розгін батареї\n• Вплив випромінення (SAR)\n• Заходи зниження ризиків"
    frags.append(fitbox(270, y_pos, c_w, c_h, c2_txt, size=11, fill="#ffffff", stroke="#94a3b8"))

    c3_txt = "3. Протоколи випробувань\n• Лабораторія ISO 17025\n• Радіоспектр (RED 3.2)\n• ЕМС завади й стійкість (3.1b)\n• Електробезпека (3.1a)\n• Хім. склад RoHS (EN 63000)"
    frags.append(fitbox(485, y_pos, c_w, c_h, c3_txt, size=11, fill="#ffffff", stroke="#94a3b8"))

    c4_txt = "4. Експлуатація та контроль\n• Інструкція користувача\n• Попередження безпеки\n• Креслення маркування CE\n• Журнал змін (ECO)\n• Процедури контролю якості"
    frags.append(fitbox(700, y_pos, c_w, c_h, c4_txt, size=11, fill="#ffffff", stroke="#94a3b8"))

    render(os.path.join(IMG_DIR, "doc-vs-technical-file.svg"), w, h, *frags)


def fig_red_directive_architecture():
    """Фігура 2: Структура суттєвих вимог Директиви RED 2014/53/EU."""
    w, h = 960, 520
    frags = []

    frags.append(text(w / 2, 28, "Суттєві вимоги Директиви RED 2014/53/EU для бездротових пристроїв", size=16, bold=True))

    # Центральний вузол
    frags.append(rect(340, 200, 280, 95, fill="#edf4fc", stroke="#2457d6", sw=2.5, rx=8))
    frags.append(text(480, 230, "Радіообладнання (RED)", size=15, color="#2457d6", bold=True))
    frags.append(text(480, 252, "Поглинає вимоги LVD та EMC;", size=12, color=INK))
    frags.append(text(480, 272, "Діє без нижньої межі напруги", size=12, color=MUTED))

    # 4 квадранти вимог
    # Квадрант 1: Стаття 3.1(a) Безпека та здоров'я (ліворуч вгорі)
    frags.append(fitbox(40, 65, 270, 130, "Стаття 3.1(a): Здоров'я та Безпека\n• Електробезпека: EN 62368-1 / EN 60950\n• Опромінення людини: EN 62311 (EMF)\n• Питоме поглинання: EN 50663 / EN 62209 (SAR)\n• Захист від опіків, механічних травм,\n  вибуху акумулятора (немає межі 50 В!)", size=11, fill="#fef2f2", stroke="#ef4444"))
    frags.append(arrow(340, 220, 310, 160, color="#ef4444"))

    # Квадрант 2: Стаття 3.1(b) Електромагнітна сумісність (праворуч вгорі)
    frags.append(fitbox(650, 65, 270, 130, "Стаття 3.1(b): ЕМС (Сумісність)\n• Загальні вимоги ЕМС: EN 301 489-1\n• Специфіка для Wi-Fi/BT: EN 301 489-17\n• Специфіка для стільникового зв'язку: EN 301 489-52\n• Кондуктивні та радіаційні емісії,\n  стійкість до ESD, сплесків та полів", size=11, fill="#fefce8", stroke="#eab308"))
    frags.append(arrow(620, 220, 650, 160, color="#eab308"))

    # Квадрант 3: Стаття 3.2 Ефективне використання спектра (ліворуч внизу)
    frags.append(fitbox(40, 310, 270, 140, "Стаття 3.2: Радіоспектр\n• Діапазон 2.4 ГГц: ETSI EN 300 328 (BT, Wi-Fi)\n• Діапазон 5 ГГц: ETSI EN 301 893 (Wi-Fi 5/6)\n• Діапазон до 1 ГГц: ETSI EN 300 220 (SRD, LoRa)\n• Вихідна потужність (EIRP), маска спектра,\n  побічні випромінення (Spurious emissions),\n  робочий цикл (Duty cycle), LBT", size=11, fill="#f0fdf4", stroke="#22c55e"))
    frags.append(arrow(340, 275, 310, 335, color="#22c55e"))

    # Квадрант 4: Стаття 3.3 Кібербезпека та захист мережі (праворуч внизу)
    frags.append(fitbox(650, 310, 270, 140, "Стаття 3.3: Кібербезпека (d/e/f)\n• Безпека IoT: EN 303 645 / IEC 62443-4-2\n• 3.3(d): Захист мережі від перевантажень\n• 3.3(e): Захист персональних даних та приватності\n• 3.3(f): Захист фінансових транзакцій від шахрайства\n• Обов'язкова верифікація прошивки та ключів", size=11, fill="#f5f3ff", stroke="#8b5cf6"))
    frags.append(arrow(620, 275, 650, 335, color="#8b5cf6"))

    # Нижня плашка підсумку
    frags.append(rect(40, 465, 880, 40, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(w / 2, 489, "Виконання гармонізованих стандартів надає презумпцію відповідності кожній окремій статті RED", size=12, color="#0f172a", bold=True))

    render(os.path.join(IMG_DIR, "red-directive-architecture.svg"), w, h, *frags)


def fig_risk_assessment_mitigation():
    """Фігура 3: Трирівнева ієрархія зниження ризиків у технічному файлі."""
    w, h = 960, 440
    frags = []

    frags.append(text(w / 2, 28, "Ієрархія зниження ризиків (ISO 12100 / EN 62368-1) у технічному файлі", size=16, bold=True))

    # Зліва: Виявлені небезпеки
    frags.append(rect(40, 70, 200, 330, fill="#fef2f2", stroke="#ef4444", sw=2, rx=8))
    frags.append(text(140, 100, "1. Виявлення небезпек", size=13, color="#ef4444", bold=True))
    frags.append(line(55, 115, 225, 115, color="#fca5a5", sw=1))
    hazards = [
        "• Електричний удар\n  (пробій ізоляції, висока V)",
        "• Тепловий розгін\n  (Li-ion акумулятор)",
        "• ВЧ-перегрів тканин\n  (перевищення SAR)",
        "• Збій керування\n  (через ЕМС-заваду)",
        "• Програмний збій\n  (зависання у небезпеці)",
        "• Займання пластику\n  (UL94 займання)"
    ]
    for idx, h_txt in enumerate(hazards):
        frags.append(mtext(60, 140 + idx * 43, h_txt.split("\n"), size=11, color="#7f1d1d", anchor="start", lh=1.2))

    # Стрілка переходу
    frags.append(arrow(240, 235, 275, 235, color=LINE, sw=2))

    # Центр: 3 рівні захисту
    frags.append(rect(285, 70, 410, 330, fill="#f8fafc", stroke="#334155", sw=2, rx=8))
    frags.append(text(490, 95, "2. Трирівнева ієрархія захисту", size=13, color="#1e293b", bold=True))

    # Рівень 1: Конструктивна безпека
    frags.append(fitbox(305, 115, 370, 80, "Рівень I: Внутрішньо безпечна конструкція\n• Гальванічна розв'язка, повітряні зазори (Creepage/Clearance)\n• Робота на безпечній наднизькій напрузі (SELV / ES1)\n• Обмеження потужності передавача апаратними атенюаторами", size=11, fill="#eff6ff", stroke="#3b82f6"))

    # Рівень 2: Технічні засоби захисту
    frags.append(fitbox(305, 205, 370, 85, "Рівень II: Апаратний та програмний захист\n• Самовідновні запобіжники (PTC), супресори TVS, NTC-датчики\n• Контролер захисту акумулятора (BMS OVP/UVP/OCP)\n• Апаратний сторожовий таймер (Watchdog), безпечний стан", size=11, fill="#f0fdf4", stroke="#22c55e"))

    # Рівень 3: Інформування про залишковий ризик
    frags.append(fitbox(305, 300, 370, 85, "Рівень III: Інструкції та маркування\n• Піктограми безпеки на корпусі (WEEE, знаки застереження)\n• Обмеження монтажу та мінімальна дистанція до тіла в Manual\n• Заборона відкривання корпуса некваліфікованим персоналом", size=11, fill="#fefce8", stroke="#eab308"))

    # Стрілка переходу
    frags.append(arrow(695, 235, 730, 235, color=LINE, sw=2))

    # Справа: Прийнятний залишковий ризик
    frags.append(rect(740, 70, 180, 330, fill="#ecfdf5", stroke="#10b981", sw=2, rx=8))
    frags.append(text(830, 100, "3. Результат", size=13, color="#065f46", bold=True))
    frags.append(line(755, 115, 905, 115, color="#6ee7b7", sw=1))
    res_lines = [
        "Допустимий",
        "залишковий",
        "ризик",
        "",
        "Всі ризики",
        "переведені у",
        "зелену зону",
        "матриці FMEA.",
        "",
        "Документується",
        "в розділі 5",
        "Технічного",
        "файлу."
    ]
    frags.append(mtext(830, 140, res_lines, size=11, color="#047857", anchor="middle", lh=1.3))

    render(os.path.join(IMG_DIR, "risk-assessment-mitigation.svg"), w, h, *frags)


def fig_compliance_lifecycle_10years():
    """Фігура 4: Життєвий цикл технічного файлу: серійне виробництво та 10-річне архівування."""
    w, h = 960, 450
    frags = []

    frags.append(text(w / 2, 28, "Хронологія збереження Технічного файлу: Правило «10 років від останньої одиниці»", size=16, bold=True))

    # Горизонтальна часова вісь
    frags.append(line(60, 160, 900, 160, color="#475569", sw=3))
    frags.append(arrow(880, 160, 920, 160, color="#475569", sw=3))
    frags.append(text(920, 185, "Час (роки)", size=12, color=MUTED, anchor="end"))

    # Фаза 1: Розробка та сертифікація
    frags.append(line(100, 145, 100, 175, color="#2457d6", sw=2.5))
    frags.append(circle(100, 160, 6, fill="#2457d6", stroke="#ffffff", sw=2))
    frags.append(text(100, 135, "T0: Старт проекту", size=11, color="#2457d6", bold=True))
    frags.append(fitbox(60, 200, 160, 95, "R&D та Тестування\n• Створення схем\n• Тести ISO 17025\n• Оцінка ризиків\n• Формування TDF", size=11, fill="#eff6ff", stroke="#3b82f6"))

    # Фаза 2: Початок продажів (Перша одиниця)
    frags.append(line(240, 145, 240, 175, color="#10b981", sw=2.5))
    frags.append(circle(240, 160, 6, fill="#10b981", stroke="#ffffff", sw=2))
    frags.append(text(240, 135, "T1: Перша одиниця на ринку", size=11, color="#10b981", bold=True))
    frags.append(fitbox(210, 310, 170, 90, "Підписання DoC\n• Нанесення CE-знака\n• Вихід у продаж в ЄС\n• Контроль змін (ECO)\n• Аудит партій", size=11, fill="#ecfdf5", stroke="#10b981"))
    frags.append(line(240, 175, 240, 310, color="#10b981", sw=1.5, dash="4,3"))

    # Фаза 3: Кінець виробництва (Остання одиниця)
    frags.append(line(450, 145, 450, 175, color="#eab308", sw=2.5))
    frags.append(circle(450, 160, 6, fill="#eab308", stroke="#ffffff", sw=2))
    frags.append(text(450, 135, "T2: Остання випущена одиниця", size=11, color="#ca8a04", bold=True))
    frags.append(fitbox(390, 200, 170, 95, "Зняття з виробництва\n(End-of-Life)\nЗ цієї точки стартує\n10-річний лічильник\nархівування TDF!", size=11, fill="#fefce8", stroke="#eab308"))

    # Зона 10-річного архівування
    frags.append(rect(450, 85, 380, 50, fill="#fef2f2", stroke="#ef4444", sw=2, rx=6))
    frags.append(text(640, 107, "ОБОВ'ЯЗКОВИЙ ПЕРІОД ЗБЕРЕЖЕННЯ: 10 РОКІВ", size=12, color="#b91c1c", bold=True))
    frags.append(text(640, 125, "Технічний файл та DoC мають бути доступні органам нагляду (MSA)", size=11, color="#7f1d1d"))

    # Фаза 4: Кінець зобов'язань
    frags.append(line(830, 145, 830, 175, color="#64748b", sw=2.5))
    frags.append(circle(830, 160, 6, fill="#64748b", stroke="#ffffff", sw=2))
    frags.append(text(830, 135, "T2 + 10 років: Фінал архіву", size=11, color="#475569", bold=True))

    # Перевірка ринкового нагляду під час 10 років
    frags.append(fitbox(590, 300, 260, 110, "Запит Ринкового Нагляду (MSA)\n• Митниця або інспекція вимагає TDF\n• Стандартний термін надання: 10 днів\n• Ненадання = презумпція невідповідності,\n  заборона продажу, штрафи та відкликання", size=11, fill="#ffffff", stroke="#ef4444", bold=False))
    frags.append(arrow(670, 160, 670, 300, color="#ef4444", sw=2))

    render(os.path.join(IMG_DIR, "compliance-lifecycle-10years.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_doc_vs_technical_file()
    fig_red_directive_architecture()
    fig_risk_assessment_mitigation()
    fig_compliance_lifecycle_10years()
    print("All figures generated successfully.")
