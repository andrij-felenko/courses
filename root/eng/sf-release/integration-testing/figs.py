# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

HOT  = "#fdecea"
COLD = "#eef4ff"
GRN  = "#eafaf1"
AMB  = "#fff8e1"

# ── Фігура 1: Піраміда перевірок у вбудованих системах ───────────────────────
def fig_testing_pyramid():
    W, H = 1080, 520
    frags = []

    # Три яруси піраміди
    # Ярус 1: Стенди HIL (Вершина)
    hil_box, hw, hh = textbox(440, 110,
                              ["Фізичний кремній: стенди HIL",
                               "Реальні плати, кероване живлення, реле, логічні аналізатори",
                               "Час: 10–60 с/тест · Охоплення: кремній, таймінги, електрика"],
                              size=13, bold=False, fill="#fdecea", stroke=POS, sw=2, pad=12, min_w=580)
    frags.append(hil_box)

    # Ярус 2: Емуляція та симуляція (Середина)
    sim_box, sw_b, sh = textbox(440, 230,
                                ["Емуляція та симуляція: Renode, QEMU, Arm FVP",
                                 "Цільовий бінарник ARM/RISC-V, віртуальна периферія та датчики",
                                 "Час: 50–500 мс/тест · Охоплення: регістри, переривання, драйвери"],
                                size=13, bold=False, fill=AMB, stroke="#b8860b", sw=2, pad=12, min_w=680)
    frags.append(sim_box)

    # Ярус 3: Хостові юніт-тести (Основа)
    host_box, how, hoh = textbox(440, 360,
                                 ["Хостові модульні тести (x86 / Native)",
                                  "Чиста бізнес-логіка, кінцеві автомати, моки HAL, ASan / UBSan",
                                  "Час: < 1 мс/тест · Охоплення: алгоритми, парсери, обробка помилок"],
                                 size=13, bold=False, fill=COLD, stroke=NEG, sw=2, pad=12, min_w=780)
    frags.append(host_box)

    # Вертикальні стрілки осей праворуч
    # Вісь точності заліза (вгору)
    frags.append(arrow(890, 420, 890, 70, color=POS, sw=2.2))
    frags.append(text(890, 52, "Апаратна точність та реалізм", size=12, bold=True, color=POS))
    frags.append(text(890, 440, "Абстрактні припущення", size=11, color=MUTED))

    # Вісь швидкості та спостережуваності (вниз)
    frags.append(arrow(990, 70, 990, 420, color=NEG, sw=2.2))
    frags.append(text(990, 52, "Швидкість і спостережуваність", size=12, bold=True, color=NEG))
    frags.append(text(990, 440, "Детермінізм, ASan, швидкий зворотний зв'язок", size=11, color=MUTED))

    # З'єднувальні мітки
    frags.append(text(W / 2, 490,
                      "Основа піраміди дає миттєву діагностику логіки; вершина підтверджує фізичну поведінку кремнію.",
                      size=14, bold=True, color=INK))

    render(os.path.join(IMG, 'testing-pyramid.svg'), W, H, *frags,
           title="Піраміда тестування у вбудованих системах")


# ── Фігура 2: Сліпа зона хостових моків проти реального кремнію ──────────────
def fig_host_vs_silicon_gap():
    W, H = 1080, 500
    frags = []

    # Ліва панель: Хостовий тест із моком
    frags.append(rect(40, 70, 470, 370, fill="#f9fbfe", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(275, 95, "Хостовий запуск (x86 + Мок HAL)", size=15, bold=True, color=NEG))

    b1, _, _ = textbox(275, 150, ["Функція викликає HAL_SPI_Transmit_DMA()", "Буфер лежить на локальному стеку"],
                       size=12, fill=COLD, stroke=NEG, pad=8, min_w=410)
    frags.append(b1)

    b2, _, _ = textbox(275, 230, ["Мок миттєво копіює байти й повертає HAL_OK", "Стек валідний, виконання завершується успішно"],
                       size=12, fill=GRN, stroke=FIELD, pad=8, min_w=410)
    frags.append(b2)

    b3, _, _ = textbox(275, 310, ["Результат: ТЕСТ ЗЕЛЕНИЙ (< 1 мс)", "Ілюзія повної працездатності"],
                       size=13, bold=True, fill="#eafaf1", stroke=FIELD, pad=8, min_w=410)
    frags.append(b3)
    frags.append(arrow(275, 180, 275, 205, color=NEG, sw=1.8))
    frags.append(arrow(275, 260, 275, 285, color=FIELD, sw=1.8))

    # Права панель: Реальний кремній
    frags.append(rect(570, 70, 470, 370, fill="#fdfaf9", stroke=POS, sw=1.8, rx=8))
    frags.append(text(805, 95, "Реальний чип (Cortex-M7 + Контролер DMA)", size=15, bold=True, color=POS))

    c1, _, _ = textbox(805, 150, ["Контролер DMA запускається асинхронно", "Процесор виходить із функції та звільняє стек"],
                       size=12, fill=AMB, stroke="#b8860b", pad=8, min_w=410)
    frags.append(c1)

    c2, _, _ = textbox(805, 230, ["Інша задача перезаписує пам'ять стека;", "D-Cache не скинуто у SRAM перед транзакцією"],
                       size=12, fill=HOT, stroke=POS, pad=8, min_w=410)
    frags.append(c2)

    c3, _, _ = textbox(805, 310, ["Результат: Пошкодження даних або HardFault", "Асинхронний збій під час передачі по шині SPI"],
                       size=13, bold=True, fill="#fdecea", stroke=POS, pad=8, min_w=410)
    frags.append(c3)
    frags.append(arrow(805, 180, 805, 205, color=POS, sw=1.8))
    frags.append(arrow(805, 260, 805, 285, color=POS, sw=1.8))

    frags.append(text(W / 2, 470,
                      "Мок не враховує асинхронний час роботи шини, кеш-когерентність і реальний життєвий цикл пам'яті.",
                      size=14, bold=True, color=INK))

    render(os.path.join(IMG, 'host-vs-silicon-gap.svg'), W, H, *frags,
           title="Сліпа зона хостових моків проти поведінки кремнію")


# ── Фігура 3: Архітектура стенду Hardware-in-the-Loop (HIL) ───────────────────
def fig_hil_architecture():
    W, H = 1080, 530
    frags = []

    # Керівний комп'ютер (Хост тестування)
    host, _, _ = textbox(180, 240,
                         ["Керівний хост (CI / Pytest)",
                          "• Запуск тестових сценаріїв",
                          "• Прошивання бінарника (ELF)",
                          "• Аналіз телеметрії та звіт"],
                         size=12, bold=False, fill=COLD, stroke=NEG, sw=2, pad=12, min_w=240)
    frags.append(host)

    # Блоки обладнання посередині
    pwr, _, _ = textbox(540, 110,
                        ["Кероване джерело живлення",
                         "Просідання напруги, brownout, 3.3 В / 5 В"],
                        size=11, fill=AMB, stroke="#b8860b", pad=8, min_w=290)
    frags.append(pwr)

    dbg, _, _ = textbox(540, 200,
                        ["Апаратний налагоджувач (SWD / JTAG)",
                         "Прошивання Flash, контроль RTT / ITM"],
                        size=11, fill=AMB, stroke="#b8860b", pad=8, min_w=290)
    frags.append(dbg)

    rel, _, _ = textbox(540, 290,
                        ["Матриця реле й інжекції відмов",
                         "Розрив ліній, КЗ на GND, імітація брязкоту"],
                        size=11, fill=HOT, stroke=POS, pad=8, min_w=290)
    frags.append(rel)

    bus, _, _ = textbox(540, 380,
                        ["Аналізатор протоколів (CAN / SPI / I2C)",
                         "Захоплення пакетів, валідація CRC і таймінгів"],
                        size=11, fill=GRN, stroke=FIELD, pad=8, min_w=290)
    frags.append(bus)

    # Цільовий пристрій під тестом (DUT)
    dut, _, _ = textbox(910, 240,
                        ["Цільовий пристрій (DUT)",
                          "• Реальний мікроконтролер",
                          "• Сенсори та трансивери",
                          "• Робоча друкована плата"],
                        size=12, bold=False, fill="#fdecea", stroke=POS, sw=2.2, pad=12, min_w=240)
    frags.append(dut)

    # Стрілки керування та зв'язку
    frags.append(arrow(310, 190, 385, 120, color=NEG, sw=1.6))
    frags.append(arrow(310, 225, 385, 200, color=NEG, sw=1.6))
    frags.append(arrow(310, 260, 385, 290, color=NEG, sw=1.6))
    frags.append(arrow(310, 290, 385, 370, color=NEG, sw=1.6))

    frags.append(arrow(695, 120, 780, 190, color=POS, sw=1.6))
    frags.append(arrow(695, 200, 780, 225, color=POS, sw=1.6))
    frags.append(arrow(695, 290, 780, 260, color=POS, sw=1.6))
    frags.append(arrow(695, 370, 780, 290, color=FIELD, sw=1.6))

    frags.append(text(W / 2, 485,
                      "Керівний комп'ютер повністю контролює фізичне середовище, шини даних та живлення цільового чипа.",
                      size=14, bold=True, color=INK))

    render(os.path.join(IMG, 'hil-architecture.svg'), W, H, *frags,
           title="Апаратна архітектура автоматизованого стенду HIL")


# ── Фігура 4: Зворотний зв'язок та ескалація дефектів донизу ──────────────────
def fig_defect_shift_down():
    W, H = 1080, 480
    frags = []

    # Крок 1: Виявлення на HIL
    s1, _, _ = textbox(170, 210,
                       ["1. Збій на HIL",
                        "Помилка CRC на шині SPI",
                        "під час зміни живлення"],
                       size=12, fill=HOT, stroke=POS, sw=1.8, pad=10, min_w=220)
    frags.append(s1)

    # Крок 2: Відтворення в Renode
    s2, _, _ = textbox(450, 210,
                       ["2. Модель у Renode",
                        "Додано емуляцію затримки",
                        "відповіді датчика"],
                       size=12, fill=AMB, stroke="#b8860b", sw=1.8, pad=10, min_w=220)
    frags.append(s2)

    # Крок 3: Модульний тест на хості
    s3, _, _ = textbox(730, 210,
                       ["3. Тест на хості",
                        "Мок емулює таймаут",
                        "і перевіряє відновлення"],
                       size=12, fill=COLD, stroke=NEG, sw=1.8, pad=10, min_w=220)
    frags.append(s3)

    # Крок 4: Швидкий захист у CI
    s4, _, _ = textbox(960, 210,
                       ["4. Захист у CI",
                        "Перевірка за < 1 с",
                        "на кожен комміт"],
                       size=12, fill=GRN, stroke=FIELD, sw=1.8, pad=10, min_w=170)
    frags.append(s4)

    # Стрілки переходу
    frags.append(arrow(290, 210, 330, 210, color=POS, sw=2))
    frags.append(arrow(570, 210, 610, 210, color="#b8860b", sw=2))
    frags.append(arrow(850, 210, 865, 210, color=NEG, sw=2))

    # Нижній блок висновку
    frags.append(rect(140, 340, 800, 70, fill="#f8fafc", stroke=FIELD, sw=1.6, rx=6))
    frags.append(text(540, 370,
                      "Правило: кожен дефект із HIL спускають до рівня симуляції та хостового моку,",
                      size=13, bold=True, color=INK))
    frags.append(text(540, 392,
                      "щоб регресія ловилася за мілісекунди на машині розробника, не чекаючи залізного стенду.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'defect-shift-down.svg'), W, H, *frags,
           title="Ескалація дефектів донизу: перенесення знань із HIL на хост")


if __name__ == '__main__':
    fig_testing_pyramid()
    fig_host_vs_silicon_gap()
    fig_hil_architecture()
    fig_defect_shift_down()
    print("All figures generated successfully.")
