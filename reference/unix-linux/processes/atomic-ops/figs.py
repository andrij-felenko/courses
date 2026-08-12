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


def fig_cache_locking_mesi():
    W, H = 1200, 560
    p = []

    # Заголовок лівого блоку: Bus Lock
    p.append(rect(40, 40, 540, 480, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(310, 75, "Шинне блокування (Bus Lock / #LOCK)", size=16, bold=True, color=POS))
    p.append(text(310, 98, "Незрівняний доступ або незакешована пам'ять", size=13, color=MUTED))

    # Компоненти лівого блоку
    p.append(fitbox(70, 130, 220, 60, "Ядро CPU 0\n(виконує LOCK INC)", size=14, fill=RED_FILL, stroke=POS, bold=True))
    p.append(fitbox(330, 130, 220, 60, "Ядро CPU 1\n(ЗАБЛОКОВАНО)", size=14, fill=GREY_FILL, stroke=MUTED))

    # Системна шина пам'яті (червона лінія з блокуванням)
    p.append(rect(70, 240, 480, 50, fill=RED_FILL, stroke=POS, sw=2, rx=6))
    p.append(text(310, 270, "Апаратний сигнал #LOCK активний (Системна шина RAM)", size=14, color=POS, bold=True))

    p.append(arrow(180, 190, 180, 240, color=POS, sw=2))
    p.append(line(440, 190, 440, 240, color=MUTED, sw=2, dash="4,4"))

    # Системна RAM
    p.append(fitbox(170, 340, 280, 60, "Оперативна пам'ять (RAM)\nДоступ усіх інших ядер заморожено", size=14, fill=WARM_FILL, stroke=MUTED))
    p.append(arrow(310, 290, 310, 340, color=POS, sw=2))

    p.append(text(310, 445, "Високі накладні витрати: блокується весь шинний контролер", size=12, color=POS, italic=True))
    p.append(text(310, 470, "Усі інші процесори чекають на звільнення шини", size=12, color=MUTED))

    # Заголовок правого блоку: Cache Lock (MESI)
    p.append(rect(620, 40, 540, 480, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(890, 75, "Кеш-блокування (Cache Lock / MESI)", size=16, bold=True, color=FIELD))
    p.append(text(890, 98, "Вирівняні дані в кеші L1/L2", size=13, color=MUTED))

    # Компоненти правого блоку
    p.append(fitbox(650, 130, 220, 60, "Ядро CPU 0\n(виконує LOCK INC)", size=14, fill=GREEN_FILL, stroke=FIELD, bold=True))
    p.append(fitbox(910, 130, 220, 60, "Ядро CPU 1\n(вільно виконує інші задачі)", size=14, fill=BLUE_FILL, stroke=NEG))

    # L1/L2 кеш лінії
    p.append(fitbox(650, 230, 220, 70, "Кеш L1/L2 (CPU 0)\nСтан MESI: Exclusive/Modified\nУтримується Cache Line Lock", size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(910, 230, 220, 70, "Кеш L1/L2 (CPU 1)\nСтан MESI: Invalid (I)\nОтримано сповіщення Invalidate", size=13, fill=GREY_FILL, stroke=MUTED))

    p.append(arrow(760, 190, 760, 230, color=FIELD, sw=2))
    p.append(arrow(1020, 190, 1020, 230, color=NEG, sw=1.5))

    # Сигнальна лінія між кешами (Inter-connect)
    p.append(line(870, 265, 910, 265, color=POS, sw=2, dash="3,3"))
    p.append(text(890, 255, "Invalidate", size=11, color=POS, bold=True))

    # Системна RAM
    p.append(fitbox(750, 350, 280, 50, "Оперативна пам'ять (RAM)\nНе блокується для інших ядер", size=14, fill=BG, stroke=LINE))
    p.append(text(890, 445, "Низька затримка: операція в межах кеш-лінії L1 (декілька тактів)", size=12, color=FIELD, italic=True))
    p.append(text(890, 470, "Шина пам'яті залишається вільною для паралельних операцій", size=12, color=MUTED))

    render(os.path.join(IMG, 'cache-locking-mesi.svg'), W, H, *p,
           title="Когерентність кешів та блокування ліній пам'яті (MESI)")


def fig_ll_sc_monitor():
    W, H = 1100, 580
    p = []

    # Заголовок
    p.append(text(550, 35, "Механізм інструкцій Load-Linked / Store-Conditional (LL/SC)", size=17, bold=True))

    # Крок 1
    p.append(rect(40, 70, 1020, 140, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(fitbox(60, 90, 140, 40, "Крок 1: LL", size=14, fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(text(570, 110, "Ядро читає значення інструкцією LL (LDREX / lr.w) та активує Exclusive Monitor", size=14, bold=True))

    p.append(fitbox(90, 145, 280, 50, "Процесорне ядро 0\nВиконує LL [addr]", size=13, fill=FILL, stroke=LINE))
    p.append(arrow(370, 170, 450, 170, color=NEG, sw=1.8))
    p.append(fitbox(450, 145, 300, 50, "Апаратний монітор (Exclusive Monitor)\nСтан: EXCLUSIVE (Адреса записана)", size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(750, 170, 830, 170, color=NEG, sw=1.8))
    p.append(fitbox(830, 145, 200, 50, "Комірка RAM\n[addr] = 42", size=13, fill=WARM_FILL, stroke=MUTED))

    # Сценарії розвитку (Гілкування)
    # Гілка А: Успіх (Store-Conditional)
    p.append(rect(40, 230, 490, 310, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(285, 255, "Сценарій А: Успішний запис (без втручання)", size=15, bold=True, color=FIELD))

    p.append(fitbox(60, 280, 450, 45, "Жодне інше ядро не записувало за адресою [addr]\nExclusive Monitor залишається у стані EXCLUSIVE", size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(285, 325, 285, 355, color=FIELD, sw=1.8))

    p.append(fitbox(60, 355, 450, 60, "Ядро 0 виконує SC (STREX / sc.w [addr], new_val)\nМонітор підтверджує право запису", size=13, fill=FILL, stroke=LINE))
    p.append(arrow(285, 415, 285, 445, color=FIELD, sw=1.8))

    p.append(fitbox(60, 445, 450, 65, "Результат: SC повертає 0 (УСПІХ)\nЗначення в [addr] атомарно оновлено до new_val\nЦикл зупиняється", size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Гілка Б: Помилка та повтор (Conflict / Retry)
    p.append(rect(570, 230, 490, 310, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(815, 255, "Сценарій Б: Конфлікт та повтор циклу", size=15, bold=True, color=POS))

    p.append(fitbox(590, 280, 450, 45, "Інше ядро або переривання змінило дані [addr]\nExclusive Monitor скинуто у стан INVALID!", size=13, fill=RED_FILL, stroke=POS))
    p.append(arrow(815, 325, 815, 355, color=POS, sw=1.8))

    p.append(fitbox(590, 355, 450, 60, "Ядро 0 виконує SC (STREX / sc.w [addr], new_val)\nМонітор ВІДХИЛЯЄ запис", size=13, fill=FILL, stroke=LINE))
    p.append(arrow(815, 415, 815, 445, color=POS, sw=1.8))

    p.append(fitbox(590, 445, 450, 65, "Результат: SC повертає ПОМИЛКУ (1)\nЗапис скасовано, значення [addr] не змінилося\nПрограма повторює цикл спроб з LL", size=13, fill=RED_FILL, stroke=POS, bold=True))

    render(os.path.join(IMG, 'll-sc-monitor.svg'), W, H, *p,
           title="Механізм інструкцій Load-Linked / Store-Conditional (LL/SC)")


if __name__ == '__main__':
    fig_cache_locking_mesi()
    fig_ll_sc_monitor()
    print("SVGs successfully generated!")
