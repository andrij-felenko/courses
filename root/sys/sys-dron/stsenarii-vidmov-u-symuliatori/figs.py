# -*- coding: utf-8 -*-
"""Генератор SVG-діаграм для теми «Сценарії відмов у симуляторі»."""

import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def build_failure_matrix():
    """Матриця сценаріїв відмов: домен, аномалія, рівень інжекції, детекція та реакція."""
    w, h = 980, 560
    elems = []

    # Фон
    elems.append(rect(0, 0, w, h, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=0))

    # Заголовок матриці
    elems.append(rect(20, 15, 940, 45, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    elems.append(text(490, 43, "Матриця сценаріїв відмов: від інжекції аномалії до Failsafe-дії", size=15, color=INK, bold=True))

    # Заголовки колонок
    cols = [
        (30, 160, "Домен відмови", "#e2e8f0"),
        (205, 180, "Тип аномалії", "#fee2e2"),
        (400, 170, "Точка інжекції", "#e0e7ff"),
        (585, 180, "Механізм детекції", "#fef3c7"),
        (780, 170, "Реакція Failsafe", "#dcfce7"),
    ]

    for x, cw, title, bg_col in cols:
        elems.append(rect(x, 75, cw, 34, fill=bg_col, stroke="#94a3b8", sw=1.0, rx=4))
        elems.append(text(x + cw / 2.0, 97, title, size=12, color=INK, bold=True))

    # Рядки матриці
    rows = [
        (
            "Радіозв'язок\nта телеметрія",
            "Обрив RC / GCS,\nвтрата 90% пакетів,\nстрибки джитеру >500ms",
            "MAVLink Proxy / UDP\n(дроп пакетів, затримка,\nвтрата HEARTBEAT)",
            "Таймаут лінка (Watchdog),\nковзне вікно Link Quality,\nлічильник втрат кадрів",
            "Таймаут-пауза (Loiter),\nповернення додому (RTL),\nаварійна автопосадка",
            "#f8fafc",
        ),
        (
            "Навігаційні\nсенсори (GNSS/Mag)",
            "Глушіння (Jamming),\nспуфінг координат,\nаномалія магнітометра",
            "HAL Sensor Driver /\nHIL_SENSOR & GPS_RAW_INT\n(шум, зсув, високий HDOP)",
            "Брама нев'язок EKF (NIS),\nтест на узгодженість швидкості,\nскидання курсу (Yaw Reset)",
            "Перехід у Dead Reckoning,\nутримання висоти (Altitude),\nавтопосадка за потоком",
            "#ffffff",
        ),
        (
            "Силова\nустановка (ESC/Мотор)",
            "Згорання ESC,\nвідмова 1 мотора,\nасиметрія тяги (пропелер)",
            "SITL Physics Engine /\nBody Wrench / PWM Cut\n(обнулення тяги ротора)",
            "Телеметрія DShot (eRPM),\nспостерігач нев'язок моментів,\nтривале насичення інтеграла",
            "Аварійний плоский спін (Flat Spin),\nперерахунок матриці мікшування,\nаварійний керований спуск",
            "#f8fafc",
        ),
        (
            "Аеродинаміка\nта сервоприводи",
            "Заклинювання елерона,\nзасмічення трубки Піто,\nобмерзання датчика швидкості",
            "HIL_ACTUATOR_CONTROLS /\nDynamic Pressure Scaling\n(фіксація кута, нульовий тиск)",
            "Синтетичний оцінювач вітру,\nмонітор відхилення від траєкторії,\nдетектор звалювання (Stall)",
            "Синтетична швидкість за GNSS,\nкомпенсація залишку кермами,\nвикид рятувального парашута",
            "#ffffff",
        ),
    ]

    y_start = 120
    row_h = 98

    for i, (dom, anom, inj, det, act, rbg) in enumerate(rows):
        y = y_start + i * (row_h + 8)

        # Фонова смуга
        elems.append(rect(20, y, 940, row_h, fill=rbg, stroke="#cbd5e1", sw=1.0, rx=4))

        # 5 колонок
        col_data = [
            (30, 160, dom, INK, True),
            (205, 180, anom, POS, False),
            (400, 170, inj, NEG, False),
            (585, 180, det, "#b45309", False),
            (780, 170, act, FIELD, True),
        ]

        for x, cw, text_block, col, is_b in col_data:
            lines = text_block.split("\n")
            total_lines = len(lines)
            line_spacing = 16
            start_ty = y + (row_h - (total_lines - 1) * line_spacing) / 2.0 + 4

            for line_idx, line in enumerate(lines):
                cur_y = start_ty + line_idx * line_spacing
                elems.append(text(x + cw / 2.0, cur_y, line, size=11, color=col, bold=is_b))

    return render(os.path.join(IMG_DIR, "failure-scenarios-matrix.svg"), w, h, *elems)


def build_failsafe_statechart():
    """Блок-схема та ієрархія переходів Failsafe автопілота при виникненні аномалій."""
    w, h = 980, 580
    elems = []

    # Фон
    elems.append(rect(0, 0, w, h, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=0))

    # Заголовок
    elems.append(rect(20, 15, 940, 42, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    elems.append(text(490, 42, "Дерево прийняття рішень та драбина Failsafe-переходів у польотному стеку", size=15, color=INK, bold=True))

    # Рівень 0: Штатний політ
    elems.append(rect(40, 80, 240, 60, fill="#ecfdf5", stroke=FIELD, sw=2.0, rx=6))
    elems.append(text(160, 105, "Штатний політ (Mission / PosCtl)", size=12, color=FIELD, bold=True))
    elems.append(text(160, 125, "Всі давачі та лінки в нормі", size=10, color=MUTED))

    # Стрілка вниз до блоку моніторингу
    elems.append(arrow(160, 140, 160, 180, color=LINE, sw=1.8))

    # Блок діагностики та фільтрів
    elems.append(rect(40, 185, 240, 80, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    elems.append(text(160, 210, "Підсистема моніторингу здоров'я", size=12, color=NEG, bold=True))
    elems.append(text(160, 232, "• Брама інновацій EKF2 (NIS)", size=10, color=INK))
    elems.append(text(160, 250, "• Watchdog каналів зв'язку", size=10, color=INK))

    # Стрілки від моніторингу до різних рівнів Failsafe
    # 1. До Loiter / Hold
    elems.append(arrow(280, 205, 365, 125, color=LINE, sw=1.8))

    # 2. До EKF Dead Reckoning / AltHold
    elems.append(arrow(280, 225, 365, 225, color=LINE, sw=1.8))

    # 3. До RTL / Land
    elems.append(arrow(280, 245, 365, 320, color=LINE, sw=1.8))

    # 4. До Emergency / Termination
    elems.append(arrow(160, 265, 160, 420, color=POS, sw=2.2))
    elems.append(text(180, 345, "Критична відмова", size=10, color=POS, bold=True, anchor="start"))

    # Блоки реакцій
    # Рівень 1: Тимчасовий дебаунс і Loiter
    elems.append(rect(375, 85, 265, 70, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=6))
    elems.append(text(507, 108, "Рівень 1: Затримка та зависання (Loiter)", size=11, color="#b45309", bold=True))
    elems.append(text(507, 126, "Обрив RC/GCS < COM_RC_LOSS_T", size=10, color=INK))
    elems.append(text(507, 142, "Очікування відновлення пакетів", size=9, color=MUTED))

    # Рівень 2: Деградація навігації (Dead Reckoning / AltHold)
    elems.append(rect(375, 185, 265, 70, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=6))
    elems.append(text(507, 208, "Рівень 2: Деградація навігації", size=11, color="#b45309", bold=True))
    elems.append(text(507, 226, "Втрата GNSS -> барометр + IMU", size=10, color=INK))
    elems.append(text(507, 242, "Заборона автоматичних траєкторій", size=9, color=MUTED))

    # Рівень 3: Повернення додому або посадка (RTL / Land)
    elems.append(rect(375, 285, 265, 70, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    elems.append(text(507, 308, "Рівень 3: Автоповернення або посадка", size=11, color=POS, bold=True))
    elems.append(text(507, 326, "Сплив таймауту лінка / низька батарея", size=10, color=INK))
    elems.append(text(507, 342, "Траєкторія до Home / Rally Point", size=9, color=MUTED))

    # Стрілки від рівнів до кінцевих дій
    # Loiter -> RTL (якщо таймаут минув)
    elems.append(line(640, 120, 690, 120, color=LINE, sw=1.5))
    elems.append(line(690, 120, 690, 305, color=LINE, sw=1.5))
    elems.append(arrow(690, 305, 645, 305, color=LINE, sw=1.8))
    elems.append(text(725, 210, "Таймаут вичерпано", size=9, color=MUTED, anchor="middle"))

    # Навігаційна деградація -> Land
    elems.append(line(640, 220, 690, 220, color=LINE, sw=1.5))
    elems.append(line(690, 220, 690, 335, color=LINE, sw=1.5))
    elems.append(arrow(690, 335, 645, 335, color=LINE, sw=1.8))

    # Рівень 4: Аварійні та термінальні дії
    elems.append(rect(140, 425, 800, 130, fill="#fef2f2", stroke=POS, sw=2.0, rx=6))
    elems.append(text(540, 450, "Рівень 4: Критичні відмови та керована термінація (Emergency / Termination)", size=13, color=POS, bold=True))

    # Три колонки термінальних дій
    sub_w = 240
    # Дія А: Втрата мотора
    elems.append(rect(160, 465, sub_w, 75, fill="#ffffff", stroke="#fca5a5", sw=1.0, rx=4))
    elems.append(text(160 + sub_w / 2.0, 487, "Відмова мотора / ESC", size=11, color=POS, bold=True))
    elems.append(text(160 + sub_w / 2.0, 506, "Жертва Yaw -> керований спін", size=9, color=INK))
    elems.append(text(160 + sub_w / 2.0, 524, "Зниження на збережених роторах", size=9, color=MUTED))

    # Дія Б: Викид парашута
    elems.append(rect(420, 465, sub_w, 75, fill="#ffffff", stroke="#fca5a5", sw=1.0, rx=4))
    elems.append(text(420 + sub_w / 2.0, 487, "Викид парашута", size=11, color=POS, bold=True))
    elems.append(text(420 + sub_w / 2.0, 506, "GPIO / піропатрон / серво", size=9, color=INK))
    elems.append(text(420 + sub_w / 2.0, 524, "Миттєве глушіння всіх ESC", size=9, color=MUTED))

    # Дія В: Роззброєння / Kill Switch
    elems.append(rect(680, 465, sub_w, 75, fill="#ffffff", stroke="#fca5a5", sw=1.0, rx=4))
    elems.append(text(680 + sub_w / 2.0, 487, "Примусове роззброєння (Kill)", size=11, color=POS, bold=True))
    elems.append(text(680 + sub_w / 2.0, 506, "Порушення межі Geofence", size=9, color=INK))
    elems.append(text(680 + sub_w / 2.0, 524, "Повне знеструмлення виходів PWM", size=9, color=MUTED))

    return render(os.path.join(IMG_DIR, "failsafe-transitions-statechart.svg"), w, h, *elems)


if __name__ == "__main__":
    os.makedirs(IMG_DIR, exist_ok=True)
    build_failure_matrix()
    build_failsafe_statechart()
    print("Фігури успішно згенеровано у:", IMG_DIR)
