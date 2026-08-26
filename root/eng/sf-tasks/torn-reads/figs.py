# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"


def fig_torn_read_bus_split():
    W, H = 1180, 620
    p = []

    # Заголовок фігури
    p.append(text(590, 32, "Апаратний механізм розривного читання (Torn Read) на 32-бітній шині", size=16, bold=True))

    # Лівий блок: Ядро-Письменник (Core 0)
    p.append(rect(30, 65, 340, 525, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(200, 95, "Ядро 0: Письменник (Writer)", size=15, bold=True, color=POS))
    p.append(text(200, 118, "Запис 64-бітного значення 0x00000001_FFFFFFFF", size=12, color=MUTED))

    p.append(fitbox(50, 145, 300, 75, "Початковий стан пам'яті:\n0x00000000_00000000\nЦільове: 0x00000001_FFFFFFFF", size=12, fill=FILL, stroke=LINE))

    p.append(fitbox(50, 255, 300, 80, "Крок 1 (Шинна транзакція 1):\nЗапис молодших 32 бітів (Low 32)\nSTR W1, [addr] -> 0xFFFFFFFF", size=12, fill=RED_FILL, stroke=POS, bold=True))
    p.append(arrow(200, 335, 200, 375, color=POS, sw=2))

    p.append(fitbox(50, 375, 300, 65, "ПАУЗА / ПЕРЕМИКАННЯ ШИНИ:\nШина перехоплюється Ядром 1\nСтарше слово ще НЕ записане!", size=12, fill=WARM_FILL, stroke=POS))
    p.append(arrow(200, 440, 200, 475, color=POS, sw=2))

    p.append(fitbox(50, 475, 300, 85, "Крок 2 (Шинна транзакція 2):\nЗапис старших 32 бітів (High 32)\nSTR W2, [addr+4] -> 0x00000001\n(Запізнілий запис)", size=12, fill=RED_FILL, stroke=POS))

    # Центральний блок: Фізична пам'ять / Шина даних 32-bit
    p.append(rect(400, 65, 380, 525, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(590, 95, "Фізична пам'ять (RAM / L1-L2)", size=15, bold=True, color=INK))
    p.append(text(590, 118, "Ширина апаратної шини даних — 32 біти (4 байти)", size=12, color=MUTED))

    # Стан 1
    p.append(fitbox(420, 145, 340, 75, "Стан 0 (До запису):\n[addr+4] = 0x00000000 (High)\n[addr+0] = 0x00000000 (Low)", size=12, fill=GREY_FILL, stroke=MUTED))

    # Стан 2 (Розривний стан)
    p.append(rect(420, 255, 340, 185, fill=RED_FILL, stroke=POS, sw=2, rx=6))
    p.append(text(590, 280, "РОЗРИВНИЙ СТАН ПАМ'ЯТІ (Torn State)", size=13, bold=True, color=POS))
    p.append(fitbox(435, 295, 310, 55, "[addr+4] = 0x00000000 (СТАРЕ High)\n[addr+0] = 0xFFFFFFFF (НОВЕ Low)", size=12, fill=BG, stroke=POS, bold=True))
    p.append(text(590, 375, "Сумарне значення в комірці:", size=12, bold=True, color=POS))
    p.append(text(590, 398, "0x00000000_FFFFFFFF = 4 294 967 295", size=13, bold=True, color=POS))
    p.append(text(590, 423, "Фантомне число: лічильник стрибнув угору!", size=11, color=POS, italic=True))

    # Стан 3
    p.append(fitbox(420, 475, 340, 85, "Стан 2 (Після завершення кроку 2):\n[addr+4] = 0x00000001 (High)\n[addr+0] = 0xFFFFFFFF (Low)\nПовне коректне значення: 8 589 934 591", size=12, fill=GREEN_FILL, stroke=FIELD))

    # Правий блок: Ядро-Читач (Core 1)
    p.append(rect(810, 65, 340, 525, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(980, 95, "Ядро 1: Читач (Reader)", size=15, bold=True, color=NEG))
    p.append(text(980, 118, "Зчитування 64-бітного значення uint64_t", size=12, color=MUTED))

    # Стрілка читання під час розривного стану
    p.append(fitbox(830, 255, 300, 75, "Цикл читання 1:\nЗчитування молодших 32 бітів\nLDR R0, [addr] -> 0xFFFFFFFF\n(Отримано нові дані)", size=12, fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(arrow(830, 290, 760, 290, color=NEG, sw=1.8))

    p.append(arrow(980, 330, 980, 360, color=NEG, sw=2))

    p.append(fitbox(830, 360, 300, 75, "Цикл читання 2:\nЗчитування старших 32 бітів\nLDR R1, [addr+4] -> 0x00000000\n(Отримано старі дані)", size=12, fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(arrow(830, 395, 760, 335, color=NEG, sw=1.8))

    p.append(arrow(980, 435, 980, 465, color=POS, sw=2))

    p.append(fitbox(830, 465, 300, 95, "РЕЗУЛЬТАТ РОЗРИВНОГО ЧИТАННЯ:\nРегістри: R1:R0 = 0x00000000_FFFFFFFF\nЗначення: 4 294 967 295\nКрах логіки: значення пошкоджено!", size=12, fill=RED_FILL, stroke=POS, bold=True))

    render(os.path.join(IMG, 'torn-read-bus-split.svg'), W, H, *p,
           title="Апаратний механізм розривного читання (Torn Read) на 32-бітній шині")


def fig_unaligned_cache_line_split():
    W, H = 1180, 580
    p = []

    p.append(text(590, 30, "Невирівняний доступ до пам'яті через межу кеш-ліній (Split Lock)", size=16, bold=True))

    # Верхній блок: Дві суміжні лінії кешу L1 (по 64 байти)
    p.append(rect(40, 55, 1100, 235, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(590, 78, "Розподіл 64-байтових ліній кешу L1 у фізичній пам'яті", size=14, bold=True))

    # Лінія кешу N
    p.append(rect(60, 100, 500, 110, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=6))
    p.append(text(310, 125, "Кеш-лінія N (Адреса 0x...00 — 0x...3F, 64 байти)", size=13, bold=True, color=FIELD))
    p.append(rect(80, 145, 390, 50, fill=BG, stroke=MUTED, sw=1))
    p.append(text(275, 175, "Байти 0 .. 59 (Вирівняна частина)", size=12, color=MUTED))
    p.append(rect(480, 145, 70, 50, fill=RED_FILL, stroke=POS, sw=1.8))
    p.append(text(515, 175, "60..63", size=11, bold=True, color=POS))

    # Лінія кешу N+1
    p.append(rect(620, 100, 500, 110, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=6))
    p.append(text(870, 125, "Кеш-лінія N+1 (Адреса 0x...40 — 0x...7F, 64 байти)", size=13, bold=True, color=NEG))
    p.append(rect(630, 145, 70, 50, fill=RED_FILL, stroke=POS, sw=1.8))
    p.append(text(665, 175, "64..67", size=11, bold=True, color=POS))
    p.append(rect(710, 145, 390, 50, fill=BG, stroke=MUTED, sw=1))
    p.append(text(905, 175, "Байти 68 .. 127 (Вирівняна частина)", size=12, color=MUTED))

    # Межа між лініями у зазорі (560..620)
    p.append(line(590, 95, 590, 215, color=POS, sw=2, dash="4,4"))
    p.append(text(590, 230, "Межа кеш-лінії (64 байти)", size=12, bold=True, color=POS))

    # Невирівняна 64-бітна змінна — виділена рамка внизу зони 480..700
    p.append(rect(470, 245, 240, 35, fill=RED_FILL, stroke=POS, sw=1.8, rx=4))
    p.append(text(590, 267, "Невирівняна 64-бітна змінна (8 байтів)", size=12, bold=True, color=POS))

    # Стрілки від 60..63 та 64..67 до змінної
    p.append(arrow(515, 195, 515, 245, color=POS, sw=1.5))
    p.append(arrow(665, 195, 665, 245, color=POS, sw=1.5))

    # Нижні блоки: Наслідки для неатомарного та атомарного доступу
    # Лівий нижній блок: Неатомарний доступ
    p.append(rect(40, 310, 530, 245, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(305, 335, "А. Звичайний неатомарний доступ (Torn Read)", size=14, bold=True, color=POS))
    p.append(fitbox(60, 355, 490, 45, "Процесор змушений виконати ДВІ окремі операції читання кешу:\n1. Читання кеш-лінії N -> 2. Читання кеш-лінії N+1", size=12, fill=FILL, stroke=LINE))
    p.append(fitbox(60, 410, 490, 60, "Апаратна вразливість:\nЯкщо інше ядро оновлює лінію N+1 між цими двома тактами,\nчитач отримує пошкоджені розірвані дані (Torn Read)", size=12, fill=RED_FILL, stroke=POS, bold=True))
    p.append(fitbox(60, 480, 490, 55, "Результат: Втрата когерентності на рівні змінної,\nвиникнення прихованих пошкоджень пам'яті під навантаженням", size=12, fill=WARM_FILL, stroke=MUTED))

    # Правий нижній блок: Атомарний Split Lock
    p.append(rect(610, 310, 530, 245, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(875, 335, "Б. Атомарний Split Lock (LOCK CMPXCHG)", size=14, bold=True, color=POS))
    p.append(fitbox(630, 355, 490, 45, "Кеш-блокування (Cache Lock) неможливе:\nMESI працює лише в межах однієї лінії", size=12, fill=FILL, stroke=LINE))
    p.append(fitbox(630, 410, 490, 60, "Апаратне блокування шини (Bus Lock / Split Lock):\nПроцесор активує сигнал #LOCK на системній шині,\nзаморожуючи пам'ять для ВСІХ ядер на ~250-400 нс", size=12, fill=RED_FILL, stroke=POS, bold=True))
    p.append(fitbox(630, 480, 490, 55, "Результат: Катастрофічне падіння пропускної здатності CPU,\nризик відмови у системному обслуговуванні (DoS)", size=12, fill=WARM_FILL, stroke=POS))

    render(os.path.join(IMG, 'unaligned-cache-line-split.svg'), W, H, *p,
           title="Невирівняний доступ до пам'яті через межу кеш-ліній (Split Lock)")


if __name__ == '__main__':
    fig_torn_read_bus_split()
    fig_unaligned_cache_line_split()
    print("SVGs successfully generated!")
