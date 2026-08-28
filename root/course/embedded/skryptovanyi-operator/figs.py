# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Скриптований оператор: пакетні команди, стенд, регресія»."""

import os
import sys

# 4 рівні вгору до кореня репо -> scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_rc_injection_paths():
    """Фігура 1: Три шляхи емуляції дій оператора: Virtual Joystick, RC Override та апаратний генератор."""
    w, h = 880, 430
    f = []

    # Заголовок зверху
    f.append(text(w / 2, 28, "Шляхи емуляції та інжекції команд оператора", size=16, bold=True))

    # Стовпець 1: Джерела команд (ліворуч)
    f.append(fitbox(30, 60, 220, 95, "Скрипт високого рівня\n(Python / C++)\nНормалізовані осі (-1000..+1000)", size=13, fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(30, 180, 220, 95, "Скрипт низького рівня\n(Пакетний генератор)\nСирі мікросекунди (1000..2000 мкс)", size=13, fill="#fdf3e7", stroke="#d35400"))
    f.append(fitbox(30, 300, 220, 95, "Апаратний генератор\n(Тестовий МК: RP2040 / STM32)\nФізичний сигнал SBUS / PPM", size=13, fill="#fdecea", stroke=POS))

    # Стовпець 2: Протоколи / Інтерфейси (посередині)
    f.append(fitbox(310, 60, 220, 95, "MANUAL_CONTROL (msg #69)\nТелеметрійний лінк (UDP/UART)\nЕмуляція USB HID джойстика", size=12, fill=FILL, stroke=LINE))
    f.append(fitbox(310, 180, 220, 95, "RC_CHANNELS_OVERRIDE (msg #70)\nПрямий запис у канали 1..18\nТаймаут скидання RC_OVERRIDE_TIME", size=12, fill=FILL, stroke=LINE))
    f.append(fitbox(310, 300, 220, 95, "Апаратний UART RC-вхід\nІнвертований SBUS 100 kbaud\nDMA-буфер апаратного порту", size=12, fill=FILL, stroke=LINE))

    # Стовпець 3: Обробка в автопілоті (праворуч)
    f.append(fitbox(590, 60, 260, 95, "Контур експоненти та мертвих зон\n(Stick Expo, Deadzones, Deflection Limits)\nВизначення бажаних кутів/швидкості", size=12, fill="#e8f8f5", stroke=FIELD))
    f.append(fitbox(590, 180, 260, 95, "Таблиця каналів автопілота\n(RC Input Buffer)\nПеремикання тумблерів режимів і ручок", size=12, fill="#e8f8f5", stroke=FIELD))
    f.append(fitbox(590, 300, 260, 95, "Апаратний декодер та Failsafe\nПеревірка втрати кадрів (Frame Loss)\nАктивація апаратного захисту", size=12, fill="#e8f8f5", stroke=FIELD))

    # Стрілки між стовпцями
    f.append(arrow(250, 107, 310, 107, color=NEG))
    f.append(arrow(530, 107, 590, 107, color=FIELD))

    f.append(arrow(250, 227, 310, 227, color="#d35400"))
    f.append(arrow(530, 227, 590, 227, color=FIELD))

    f.append(arrow(250, 347, 310, 347, color=POS))
    f.append(arrow(530, 347, 590, 347, color=FIELD))

    render(os.path.join(IMG, "rc-injection-paths.svg"), w, h, *f)


def fig_harness_architecture():
    """Фігура 2: Архітектура автоматизованого тестового стенда (HIL / SITL)."""
    w, h = 900, 460
    f = []

    f.append(text(w / 2, 26, "Топологія автоматизованого тестового стенда з інжекцією завад", size=16, bold=True))

    # Лівий блок: Оркестратор
    f.append(fitbox(30, 60, 240, 360, "ТЕСТОВИЙ ОРКЕСТРАТОР\n(CI / Batch Runner)\n\n• Виконання тест-сьютів\n• Генератор сценаріїв польоту\n• Контролер таймаутів (Deadlines)\n• Збір логів та артефактів\n• Асерти інваріантів стану", size=13, fill="#eaf0fd", stroke=NEG))

    # Центральний верхній блок: Проксі завад
    f.append(fitbox(330, 60, 240, 160, "ПРОКСІ ЗАНЕСЕННЯ ЗАВАД\n(Fault Injection Proxy)\n\n• Штучна втрата пакетів (0..100%)\n• Джитер та буфер затримки\n• Псування CRC та бітові помилки\n• Симуляція обриву лінка", size=12, fill="#fdecea", stroke=POS))

    # Правий блок: Цільова система
    f.append(fitbox(630, 60, 240, 360, "ЦІЛЬОВА СИСТЕМА\n(SITL / HIL Target)\n\n• Стек автопілота (PX4 / ArduPilot)\n• Фізичний рушій або плата\n• Моделювання давачів (IMU/GPS)\n• Логіка Failsafe та режимів\n• MAVLink потік телеметрії", size=13, fill="#e8f8f5", stroke=FIELD))

    # Центральний нижній блок: Аналізатор траєкторій
    f.append(fitbox(330, 260, 240, 160, "АНАЛІЗАТОР ТРАЄКТОРІЙ\n(Golden Run Comparator)\n\n• Запис стану S(t) на 100 Гц\n• Динамічне вирівнювання DTW\n• Перевірка коридорів допусків\n• Розрахунок RMSE та овершуту", size=12, fill="#fdf3e7", stroke="#d35400"))

    # Стрілки взаємодії
    # Оркестратор -> Проксі (команди)
    f.append(arrow(270, 110, 330, 110, color=NEG))
    f.append(text(300, 100, "Команди", size=10, color=NEG))

    # Проксі -> Цільова система (кадри із завадами)
    f.append(arrow(570, 110, 630, 110, color=POS))
    f.append(text(600, 100, "Завади", size=10, color=POS))

    # Цільова система -> Аналізатор (потік телеметрії)
    f.append(arrow(630, 340, 570, 340, color=FIELD))
    f.append(text(600, 330, "Телеметрія", size=10, color=FIELD))

    # Аналізатор -> Оркестратор (вердикт)
    f.append(arrow(330, 340, 270, 340, color="#d35400"))
    f.append(text(300, 330, "Вердикт", size=10, color="#d35400"))

    render(os.path.join(IMG, "harness-architecture.svg"), w, h, *f)


def fig_failsafe_timeline():
    """Фігура 3: Часова шкала сценарію відмови зв'язку та активації Failsafe."""
    w, h = 880, 380
    f = []

    f.append(text(w / 2, 26, "Часова шкала тесту регресії: обрив зв'язку та активація Failsafe", size=16, bold=True))

    # Вісь часу
    y_axis = 220
    x_start, x_end = 80, 800
    f.append(line(x_start, y_axis, x_end, y_axis, color=LINE, sw=2))
    f.append(arrow(x_end - 10, y_axis, x_end + 30, y_axis, color=LINE, sw=2))
    f.append(text(x_end + 45, y_axis + 4, "t (c)", size=12, bold=True))

    # Ключові часові мітки
    times = [
        (100, "0.0 c", "Старт тесту"),
        (280, "2.0 c", "Обрив RC-пакетів"),
        (480, "3.5 c", "Таймаут (1.5 c)"),
        (680, "5.0 c", "Відновлення лінка"),
        (780, "6.0 c", "Завершення")
    ]

    for tx, tlabel, desc in times:
        f.append(line(tx, y_axis - 8, tx, y_axis + 8, color=LINE, sw=1.5))
        f.append(text(tx, y_axis + 26, tlabel, size=11, bold=True))
        f.append(text(tx, y_axis + 42, desc, size=10, color=MUTED))

    # Фази тесту (верхні блоки)
    # Фаза 1: 0..2 с (Керування)
    f.append(rect(100, 70, 180, 110, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(190, 95, "ФАЗА 1: КЕРУВАННЯ", size=11, bold=True, color=NEG))
    f.append(text(190, 118, "Режим: GUIDED / ALT_HOLD", size=10))
    f.append(text(190, 134, "Потік RC-override: 50 Гц", size=10))
    f.append(text(190, 150, "Стабільний набір висоти", size=10))

    # Фаза 2: 2..3.5 с (Очікування таймауту)
    f.append(rect(280, 70, 200, 110, fill="#fdf3e7", stroke="#d35400", sw=1.5))
    f.append(text(380, 95, "ФАЗА 2: ВТРАТА ЛІНКА", size=11, bold=True, color="#d35400"))
    f.append(text(380, 118, "Обрив генерації пакетів", size=10))
    f.append(text(380, 134, "Автопілот утримує стан", size=10))
    f.append(text(380, 150, "Таймер FS_THR_TIMEOUT", size=10))

    # Фаза 3: 3.5..5 с (Спрацювання Failsafe)
    f.append(rect(480, 70, 200, 110, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(580, 95, "ФАЗА 3: FAILSAFE (RTL)", size=11, bold=True, color=POS))
    f.append(text(580, 118, "Автоперемикання в RTL", size=10))
    f.append(text(580, 134, "STATUSTEXT: Failsafe on", size=10))
    f.append(text(580, 150, "Початок повернення", size=10))

    # Фаза 4: 5..6 с (Відновлення)
    f.append(rect(680, 70, 100, 110, fill="#e8f8f5", stroke=FIELD, sw=1.5))
    f.append(text(730, 95, "ФАЗА 4", size=11, bold=True, color=FIELD))
    f.append(text(730, 118, "Відновлення", size=10))
    f.append(text(730, 134, "Перехоплення", size=10))
    f.append(text(730, 150, "Асерти", size=10))

    # Нижня стрічка інваріантів
    f.append(fitbox(100, 290, 680, 60, "Ключові перевірки тесту (Asserts):\n1) Спрацювання Failsafe рівно через 1.50 ± 0.05 с  |  2) Зміна режиму на RTL/LAND\n3) Наявність статусного повідомлення в черзі  |  4) Відсутність стрибка газу (Throttle Spike)", size=11, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "failsafe-timeline.svg"), w, h, *f)


def fig_golden_run_dtw():
    """Фігура 4: Динамічне вирівнювання часових шкал (DTW) та коридор допусків."""
    w, h = 880, 420
    f = []

    f.append(text(w / 2, 26, "Порівняння з еталоном: Коридор допусків та нелінійне вирівнювання (DTW)", size=16, bold=True))

    # Лівий графік: Коридор і траєкторії
    gx, gy, gw, gh = 60, 65, 460, 310
    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke=LINE, sw=1.5))

    # Сітка графіка
    for i in range(1, 5):
        f.append(line(gx, gy + i * gh / 5, gx + gw, gy + i * gh / 5, color="#e0e0e0", sw=1, dash="4,4"))
        f.append(line(gx + i * gw / 5, gy, gx + i * gw / 5, gy + gh, color="#e0e0e0", sw=1, dash="4,4"))

    # Підписи осей
    f.append(text(gx + gw / 2, gy + gh + 25, "Час / Дистанція маневру (t)", size=11))
    f.append(text(gx - 25, gy + gh / 2, "Висота Z (м)", size=11, anchor="middle"))

    # Коридор допуску (світло-зелена смуга)
    corridor_pts = [
        (80, 280), (140, 240), (200, 170), (280, 130), (360, 110), (440, 105), (500, 105)
    ]
    # Верхня межа
    top_pts = [(x, y - 25) for x, y in corridor_pts]
    # Нижня межа
    bot_pts = [(x, y + 25) for x, y in corridor_pts]

    poly_pts = " ".join(["%.1f,%.1f" % pt for pt in top_pts] + ["%.1f,%.1f" % pt for pt in reversed(bot_pts)])
    f.append('<polygon points="%s" fill="#e8f8f5" stroke="#a3e4d7" stroke-width="1"/>' % poly_pts)

    # Еталонна крива (зелена, жирна)
    ref_svg = " ".join(["%.1f,%.1f" % pt for pt in corridor_pts])
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (ref_svg, FIELD))

    # Фактична крива із затримкою фази (синя)
    act_pts = [
        (80, 285), (150, 260), (220, 190), (300, 140), (380, 115), (450, 108), (500, 106)
    ]
    act_svg = " ".join(["%.1f,%.1f" % pt for pt in act_pts])
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (act_svg, NEG))

    # Зв'язки DTW (пунктирні лінії між відповідними фазами)
    for p_ref, p_act in zip(corridor_pts[1:-1], act_pts[1:-1]):
        f.append(line(p_ref[0], p_ref[1], p_act[0], p_act[1], color=POS, sw=1.5, dash="3,3"))

    # Легенда графіка
    f.append(line(80, gy + 20, 110, gy + 20, color=FIELD, sw=3))
    f.append(text(120, gy + 24, "Еталон (Golden Run)", size=10, anchor="start"))

    f.append(line(240, gy + 20, 270, gy + 20, color=NEG, sw=2.5))
    f.append(text(280, gy + 24, "Фактичний прогін", size=10, anchor="start"))

    f.append(line(370, gy + 20, 400, gy + 20, color=POS, sw=1.5, dash="3,3"))
    f.append(text(410, gy + 24, "DTW-зв'язок", size=10, anchor="start"))

    # Правий інформаційний блок
    f.append(fitbox(550, 65, 300, 310, "МЕТРИКИ РЕГРЕСІЇ ТРАЄКТОРІЇ\n\n1. Наївна різниця (Point-to-Point):\n   • Помилкова фіксація відхилення\n     через зсув фази на 120 мс.\n\n2. Вирівнювання DTW (Dynamic Warping):\n   • Зіставлення однакових фаз підйому\n   • DTW RMSE: 0.18 м (< 0.50 м — PASS)\n\n3. Коридор допусків (Envelope):\n   • Макс. просторовий викид: 0.24 м\n   • Овершут кута крену: 1.8° (< 3.0°)\n   • Час встановлення: 4.2 c (± 5%)\n\nВЕРДИКТ: REGRESSION PASS", size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "golden-run-dtw.svg"), w, h, *f)


def main():
    fig_rc_injection_paths()
    fig_harness_architecture()
    fig_failsafe_timeline()
    fig_golden_run_dtw()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
