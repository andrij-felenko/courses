# -*- coding: utf-8 -*-
"""Фігури до теми «constinit: ініціалізація до запуску без обіцянки незмінності»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Етапи ініціалізації: безпечна статична зона і небезпечна динамічна ─────
def fig_init_timeline():
    W, H = 1000, 480
    f = []

    # Фонова шкала часу
    f.append(rect(40, 40, 920, 390, fill="#fafbfc", stroke=LINE, sw=1.5))
    f.append(text(500, 70, "ШКАЛА ЧАСУ: ВІД ЗАВАНТАЖЕННЯ БІНАРНИКА ДО MAIN()", size=14, bold=True))

    # Секція 1: Статична ініціалізація (безпечна зона)
    f.append(rect(60, 100, 410, 260, fill="#e8f6ee", stroke=FIELD, sw=2))
    f.append(text(265, 130, "СТАТИЧНА ІНІЦІАЛІЗАЦІЯ (до будь-якого коду)", size=13, color=FIELD, bold=True))
    
    f.append(fitbox(80, 155, 370, 56, "1. Нульова ініціалізація (Zero init)\nОчищення пам'яті (.bss / занулення байтів)", size=12))
    f.append(arrow(265, 215, 265, 235))
    f.append(fitbox(80, 240, 370, 70, "2. Константна ініціалізація (Constant init)\nconstinit, constexpr, сталі вирази (.data)\nГарантовано готова до старту програми", size=12, fill="#d4edda", stroke=FIELD, bold=True))
    
    f.append(text(265, 335, "Імунітет до порядку ініціалізації (без SIOF)", size=11, color=FIELD, bold=True))

    # Розділювач між статичною та динамічною фазами
    f.append(line(490, 95, 490, 370, color=MUTED, sw=1.5, dash="4,4"))

    # Секція 2: Динамічна ініціалізація (зона ризику)
    f.append(rect(510, 100, 430, 260, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(725, 130, "ДИНАМІЧНА ІНІЦІАЛІЗАЦІЯ (час виконання)", size=13, color=POS, bold=True))
    
    f.append(fitbox(530, 155, 390, 60, "3. Динамічні конструктори глобальних об'єктів\nВиклики звичайних функцій, виділення ресурсів", size=12))
    f.append(arrow(725, 220, 725, 240))
    f.append(fitbox(530, 245, 390, 65, "Порядок між одиницями трансляції НЕ визначено!\nРизик звернення до неініціалізованого об'єкта\n(Static Initialization Order Fiasco)", size=12, fill="#f8d7da", stroke=POS, bold=True))
    
    f.append(text(725, 335, "Невизначена поведінка при міжфайлових залежностях", size=11, color=POS, bold=True))

    # Стрілка переходу до main()
    f.append(arrow(470, 385, 530, 385, color=INK, sw=2))
    f.append(fitbox(540, 370, 240, 44, "Виклик функції main()", size=13, bold=True, fill="#eaf0fd", stroke=NEG))

    f.append(mtext(500, 450,
                   ["constinit жорстко прив'язує змінну до фази константної ініціалізації,",
                    "унеможливлюючи відкладення обчислення у динамічну фазу."],
                   size=11, color=MUTED, lh=1.4))

    render(os.path.join(OUT, 'init-timeline.svg'), W, H, *f,
           title="Фази ініціалізації: статична константна зона та динамічна зона ризику")


# ── 2. Проблема SIOF: хаос порядку проти захисту constinit ────────────────────
def fig_siof_breakdown():
    W, H = 1000, 520
    f = []

    # Верхній заголовок
    f.append(text(500, 35, "МІЖФАЙЛОВА ЗАЛЕЖНІСТЬ ГЛОБАЛЬНИХ ОБ'ЄКТІВ", size=14, bold=True))

    # Ліва колонка: Динамічна ініціалізація (Аварія / SIOF)
    f.append(rect(40, 60, 440, 400, fill="#fff5f5", stroke=POS, sw=2))
    f.append(text(260, 90, "БЕЗ constinit: ДИНАМІЧНИЙ ХАОС", size=13, color=POS, bold=True))

    f.append(fitbox(60, 115, 400, 54, "logger.cpp:\nLogger g_logger(\"app.log\"); // динамічний ctor", size=12))
    f.append(fitbox(60, 185, 400, 54, "network.cpp:\nClient g_client(&g_logger); // динамічний ctor", size=12))

    f.append(arrow(260, 245, 260, 275, color=POS))
    f.append(fitbox(60, 280, 400, 66, "Якщо лінкер спочатку ініціалізує network.cpp:\ng_client звертається до g_logger ДО виклику його ctor!", size=12, fill="#f8d7da", stroke=POS, bold=True))
    f.append(arrow(260, 352, 260, 380, color=POS))
    f.append(fitbox(60, 385, 400, 55, "Результат: Падіння програми (SIGSEGV)\nабо читання сміття з пам'яті (UB)", size=12, fill="#fdecea", stroke=POS, bold=True))

    # Права колонка: Захист із constinit
    f.append(rect(520, 60, 440, 400, fill="#f4faf6", stroke=FIELD, sw=2))
    f.append(text(740, 90, "З constinit: ГАРАНТОВАНА ГОТОВНІСТЬ", size=13, color=FIELD, bold=True))

    f.append(fitbox(540, 115, 400, 54, "logger.cpp:\nconstinit Logger g_logger{}; // constexpr ctor", size=12, fill="#d4edda", stroke=FIELD))
    f.append(fitbox(540, 185, 400, 54, "network.cpp:\nClient g_client(&g_logger); // динамічний ctor", size=12))

    f.append(arrow(740, 245, 740, 275, color=FIELD))
    f.append(fitbox(540, 280, 400, 66, "g_logger ВЖЕ ініціалізовано на етапі збірки!\nПорядок динамічної ініціалізації network.cpp байдужий", size=12, fill="#d4edda", stroke=FIELD, bold=True))
    f.append(arrow(740, 352, 740, 380, color=FIELD))
    f.append(fitbox(540, 385, 400, 55, "Результат: 100% передбачуваність,\nбез блокувань, без накладних витрат у main()", size=12, fill="#e8f6ee", stroke=FIELD, bold=True))

    f.append(mtext(500, 490,
                   ["constinit розриває циклічні та невизначені часові залежності між модулями,",
                    "перетворюючи порядок завантаження на несуттєву деталь."],
                   size=11, color=MUTED, lh=1.4))

    render(os.path.join(OUT, 'siof-breakdown.svg'), W, H, *f,
           title="Подолання Static Initialization Order Fiasco за допомогою constinit")


# ── 3. Матриця 2x2: Час ініціалізації проти Мутабельності ─────────────────────
def fig_four_qualifiers_quadrant():
    W, H = 1000, 500
    f = []

    f.append(text(500, 35, "ПРОСТІР МОДИФІКАТОРІВ СТАНУ В C++20", size=14, bold=True))

    # Осі
    # Горизонтальна шапка (Час ініціалізації)
    f.append(rect(240, 60, 340, 40, fill="#eef2f7", stroke=LINE))
    f.append(text(410, 85, "Компіляція / Завантаження (Static)", size=12, bold=True))

    f.append(rect(600, 60, 340, 40, fill="#eef2f7", stroke=LINE))
    f.append(text(770, 85, "Час виконання (Dynamic / Runtime)", size=12, bold=True))

    # Вертикальна шапка (Мутабельність)
    f.append(rect(40, 110, 180, 160, fill="#fbf0f0", stroke=LINE))
    f.append(mtext(130, 180, ["Незмінний", "(Read-Only / const)"], size=12, bold=True))

    f.append(rect(40, 285, 180, 160, fill="#eaf7ed", stroke=LINE))
    f.append(mtext(130, 355, ["Змінний", "(Mutable / Read-Write)"], size=12, bold=True))

    # Квадрант 1: Compile-time + Immutable -> constexpr
    f.append(rect(240, 110, 340, 160, fill="#f8f9fa", stroke=MUTED))
    f.append(text(410, 140, "constexpr", size=15, bold=True, color=INK))
    f.append(mtext(410, 180,
                   ["• Обчислення під час компіляції",
                    "• Незмінне значення (неявний const)",
                    "• Може бути аргументом шаблону"],
                   size=11, color=INK, lh=1.5))

    # Квадрант 2: Runtime + Immutable -> const
    f.append(rect(600, 110, 340, 160, fill="#f8f9fa", stroke=MUTED))
    f.append(text(770, 140, "const", size=15, bold=True, color=INK))
    f.append(mtext(770, 180,
                   ["• Ініціалізація будь-коли (runtime)",
                    "• Заборона модифікації через це ім'я",
                    "• НЕ захищає від SIOF"],
                   size=11, color=INK, lh=1.5))

    # Квадрант 3: Compile-time + Mutable -> constinit (КЛЮЧОВИЙ)
    f.append(rect(240, 285, 340, 160, fill="#e8f6ee", stroke=FIELD, sw=2.5))
    f.append(text(410, 315, "constinit", size=16, bold=True, color=FIELD))
    f.append(mtext(410, 355,
                   ["• Гарантована статична ініціалізація",
                    "• ПОВНІСТЮ МУТАБЕЛЬНИЙ під час роботи!",
                    "• Захист від SIOF для глобального стану"],
                   size=11, color=INK, lh=1.5, bold=True))

    # Квадрант 4: Runtime + Mutable -> Plain static / global
    f.append(rect(600, 285, 340, 160, fill="#fff5f5", stroke=POS))
    f.append(text(770, 315, "Звичайна змінна (без префіксів)", size=14, bold=True, color=POS))
    f.append(mtext(770, 355,
                   ["• Динамічна ініціалізація",
                    "• Змінне значення",
                    "• Вразлива до SIOF між файлами"],
                   size=11, color=INK, lh=1.5))

    f.append(mtext(500, 475,
                   ["constinit заповнює відсутню ланку в мові:",
                    "ініціалізація до запуску для об'єктів, які продовжують змінюватися під час роботи."],
                   size=11, color=MUTED, lh=1.4))

    render(os.path.join(OUT, 'four-qualifiers-quadrant.svg'), W, H, *f,
           title="Порівняння специфікаторів: час ініціалізації проти мутабельності")


# ── 4. thread_local: Динамічний обхід проти прямої адресації ──────────────────
def fig_thread_local_init():
    W, H = 1000, 480
    f = []

    f.append(text(500, 35, "МЕХАНІЗМ ІНІЦІАЛІЗАЦІЇ THREAD_LOCAL ЗМІННИХ", size=14, bold=True))

    # Ліва частина: Динамічний thread_local
    f.append(rect(40, 65, 440, 360, fill="#fff5f5", stroke=POS, sw=1.8))
    f.append(text(260, 95, "ЗВИЧАЙНИЙ thread_local", size=13, color=POS, bold=True))
    f.append(fitbox(60, 120, 400, 50, "thread_local Widget t_w(compute_val());", size=12))

    f.append(arrow(260, 175, 260, 205, color=POS))
    f.append(fitbox(60, 210, 400, 68, "Компілятор генерує приховану функцію-обгортку\nта прапорець ініціалізації для кожного потоку.\nПри КОЖНОМУ зверненні: перевірка if (!inited) init();", size=11))

    f.append(arrow(260, 285, 260, 315, color=POS))
    f.append(fitbox(60, 320, 400, 80, "Накладні витрати: розгалуження при кожному доступі,\nвиклики функцій підтримки TLS у рантаймі,\nризик виклику TLS до завершення конструктора", size=11, fill="#f8d7da", stroke=POS))

    # Права частина: constinit thread_local
    f.append(rect(520, 65, 440, 360, fill="#f4faf6", stroke=FIELD, sw=2))
    f.append(text(740, 95, "constinit thread_local", size=13, color=FIELD, bold=True))
    f.append(fitbox(540, 120, 400, 50, "constinit thread_local State t_s{100, 0};", size=12, fill="#d4edda", stroke=FIELD))

    f.append(arrow(740, 175, 740, 205, color=FIELD))
    f.append(fitbox(540, 210, 400, 68, "Значення формується як готовий образ TLS (.tdata).\nПри створенні потоку образ копіюється апаратно/ОС.\nЖодної функції-обгортки та перевірок!", size=11, fill="#d4edda", stroke=FIELD))

    f.append(arrow(740, 285, 740, 315, color=FIELD))
    f.append(fitbox(540, 320, 400, 80, "Нульові накладні витрати: прямий доступ через\nзсув у регістрі сегмента (%fs / %gs / TP),\nнуль розгалужень, 100% потокобезпечний старт", size=11, fill="#e8f6ee", stroke=FIELD, bold=True))

    f.append(mtext(500, 455,
                   ["constinit thread_local усуває runtime-обгортки TLS і перетворює звернення",
                    "до потоково-локальної змінної на одну інструкцію зміщення пам'яті."],
                   size=11, color=MUTED, lh=1.4))

    render(os.path.join(OUT, 'thread-local-init.svg'), W, H, *f,
           title="Оптимізація thread_local за допомогою constinit: усунення перевірок при доступі")


if __name__ == '__main__':
    fig_init_timeline()
    fig_siof_breakdown()
    fig_four_qualifiers_quadrant()
    fig_thread_local_init()
    print("All figures generated successfully.")
