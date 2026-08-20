# -*- coding: utf-8 -*-
"""Фігури до теми «Дивергенція варпів та банківські конфлікти GPU»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Серіалізація гілок під час дивергенції варпу ─────────────────────────
def warp_divergence_mask():
    W, H = 1060, 580
    f = []

    # Заголовок та загальна рамка
    f.append(text(W / 2, 32, "Серіалізація виконання гілок під час дивергенції варпу", size=16, bold=True))

    # Спільний початок
    f.append(rect(60, 60, 940, 70, fill="#eaf7ef", stroke=FIELD, sw=2.0, rx=8))
    f.append(text(160, 95, "Спільний шлях (PC: 0x010)", size=14, bold=True, color=FIELD))
    f.append(text(160, 115, "Маска активності: 0xFFFFFFFF", size=12, color=MUTED))
    f.append(fitbox(360, 74, 620, 42, "Усі 32 доріжки (Lane 0 .. 31) виконують спільні команди паралельно (100% темп)", size=13, fill=BG, stroke=FIELD, sw=1.4))

    f.append(arrow(530, 130, 530, 160))
    f.append(circle(530, 172, 14, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(530, 177, "?", size=15, bold=True, color=POS))
    f.append(text(530, 202, "Умова: if (threadIdx.x < 16)", size=13, bold=True, color=INK))

    # Розгалуження на дві гілки
    # Гілка THEN (Lanes 0..15)
    f.append(line(530, 186, 280, 230, color=LINE, sw=1.8))
    f.append(arrow(280, 230, 280, 250, color=LINE, sw=1.8))

    f.append(rect(60, 250, 440, 150, fill="#fbfbfc", stroke=POS, sw=2.0, rx=8))
    f.append(text(280, 275, "Фаза 1: Гілка THEN (PC: 0x020)", size=14, bold=True, color=POS))
    f.append(fitbox(80, 290, 190, 44, "Lanes 0 .. 15:\nАКТИВНІ (обчислюють)", size=12, fill="#eaf7ef", stroke=FIELD, sw=1.8))
    f.append(fitbox(290, 290, 190, 44, "Lanes 16 .. 31:\nЗАМАСКОВАНІ (чекають)", size=12, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(280, 360, "Маска: 0x0000FFFF (активні 16 з 32 потоків)", size=12, bold=True, color=MUTED))
    f.append(text(280, 382, "Корисна пропускна здатність = 50%", size=12, color=POS))

    # Гілка ELSE (Lanes 16..31)
    f.append(line(530, 186, 780, 230, color=LINE, sw=1.8))
    f.append(arrow(780, 230, 780, 250, color=LINE, sw=1.8))

    f.append(rect(560, 250, 440, 150, fill="#fbfbfc", stroke=POS, sw=2.0, rx=8))
    f.append(text(780, 275, "Фаза 2: Гілка ELSE (PC: 0x080)", size=14, bold=True, color=POS))
    f.append(fitbox(580, 290, 190, 44, "Lanes 0 .. 15:\nЗАМАСКОВАНІ (чекають)", size=12, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(fitbox(790, 290, 190, 44, "Lanes 16 .. 31:\nАКТИВНІ (обчислюють)", size=12, fill="#eaf7ef", stroke=FIELD, sw=1.8))
    f.append(text(780, 360, "Маска: 0xFFFF0000 (активні 16 з 32 потоків)", size=12, bold=True, color=MUTED))
    f.append(text(780, 382, "Корисна пропускна здатність = 50%", size=12, color=POS))

    # Злиття у точку реконвергенції
    f.append(line(280, 400, 280, 440, color=LINE, sw=1.8))
    f.append(line(280, 440, 530, 465, color=LINE, sw=1.8))
    f.append(line(780, 400, 780, 440, color=LINE, sw=1.8))
    f.append(line(780, 440, 530, 465, color=LINE, sw=1.8))
    f.append(arrow(530, 465, 530, 485, color=LINE, sw=1.8))

    f.append(rect(60, 485, 940, 70, fill="#eaf7ef", stroke=FIELD, sw=2.0, rx=8))
    f.append(text(180, 520, "Точка реконвергенції (PC: 0x100)", size=14, bold=True, color=FIELD))
    f.append(text(180, 540, "Маска активності: 0xFFFFFFFF", size=12, color=MUTED))
    f.append(fitbox(380, 499, 600, 42, "Варп знову об'єднаний: сумарний час виконання = Час(THEN) + Час(ELSE)", size=13, fill=BG, stroke=FIELD, sw=1.4))

    render(os.path.join(OUT, 'warp-divergence-mask.svg'), W, H, *f)


# ── 2. Класичний SIMT-стек проти Volta ITS ──────────────────────────────────
def simt_stack_vs_its():
    W, H = 1080, 560
    f = []

    f.append(text(W / 2, 32, "Апаратне керування розгалуженнями: SIMT-стек проти Volta ITS", size=16, bold=True))

    # Ліва панель: SIMT-стек (Pre-Volta)
    f.append(rect(40, 60, 480, 470, fill="#fbfbfc", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(280, 92, "Класичний SIMT-стек (Pascal / Kepler)", size=15, bold=True, color=INK))

    f.append(fitbox(65, 115, 430, 48, "Один Program Counter (PC) на весь варп\n+ Апаратний стек масок активності", size=13, fill="#eef2f7", stroke=MUTED, sw=1.5))

    f.append(rect(80, 185, 400, 180, fill=BG, stroke=LINE, sw=1.8, rx=6))
    f.append(text(280, 210, "Стек викликів і реконвергенції", size=13, bold=True, color=MUTED))
    f.append(fitbox(100, 225, 360, 36, "Вершина: [PC: 0x020, ActiveMask: 0x0000FFFF]", size=12, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(fitbox(100, 270, 360, 36, "Наступний: [PC: 0x080, ActiveMask: 0xFFFF0000]", size=12, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(fitbox(100, 315, 360, 36, "База: [ReconvPC: 0x100, TargetMask: 0xFFFFFFFF]", size=12, fill="#eaf7ef", stroke=FIELD, sw=1.6))

    f.append(fitbox(65, 385, 430, 65, "Жорсткий порядок вичерпання стека:\nпоки гілка A не завершиться, гілка B не отримає жодного такту.\nНеявний варп-синхронізм працював автоматично.", size=12, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(280, 485, "Ризик: глухий кут (Deadlock) при блокуваннях усередині гілок", size=12, color=POS, bold=True))

    # Права панель: Independent Thread Scheduling (Volta+)
    f.append(rect(560, 60, 480, 470, fill="#fbfbfc", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(800, 92, "Volta ITS (Volta / Ampere / Hopper)", size=15, bold=True, color=FIELD))

    f.append(fitbox(585, 115, 430, 48, "Окремий PC і стек для кожного з 32 потоків\n+ Апаратні бар'єри конвергенції (WARP.SYNC)", size=13, fill="#eaf7ef", stroke=FIELD, sw=1.8))

    # Сітка станів потоків
    f.append(rect(585, 185, 430, 180, fill=BG, stroke=LINE, sw=1.8, rx=6))
    f.append(text(800, 210, "Незалежний стан потоків варпу", size=13, bold=True, color=MUTED))
    f.append(fitbox(605, 225, 185, 36, "Потік 0: PC 0x024", size=12, fill="#eaf7ef", stroke=FIELD, sw=1.5))
    f.append(fitbox(810, 225, 185, 36, "Потік 1: PC 0x024", size=12, fill="#eaf7ef", stroke=FIELD, sw=1.5))
    f.append(fitbox(605, 270, 185, 36, "Потік 16: PC 0x088", size=12, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(fitbox(810, 270, 185, 36, "Потік 17: PC 0x090", size=12, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(fitbox(605, 315, 390, 36, "Планувальник вільно чергує інструкції різних гілок", size=12, fill="#f4f6f8", stroke=MUTED, sw=1.5))

    f.append(fitbox(585, 385, 430, 65, "Потоки можуть чергуватися на рівні інструкцій.\nСпільні змінні без __syncwarp() ламаються:\nвимагає явних бар'єрів та масок збіжності.", size=12, fill="#eaf7ef", stroke=FIELD, sw=1.8))
    f.append(text(800, 485, "Перевага: відсутність блокувань, чесний lock-free прогрес", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, 'simt-stack-vs-its.svg'), W, H, *f)


# ── 3. Архітектура 32 банків спільної пам'яті та конфлікти ─────────────────
def shared_memory_banks():
    W, H = 1120, 620
    f = []

    f.append(text(W / 2, 30, "Організація 32 банків спільної пам'яті (Shared Memory)", size=16, bold=True))

    # Випадок 1: Ідеальний безконфліктний доступ
    f.append(rect(40, 60, 320, 520, fill="#fbfbfc", stroke=FIELD, sw=2.0, rx=8))
    f.append(text(200, 90, "1. Безконфліктний доступ", size=14, bold=True, color=FIELD))
    f.append(fitbox(55, 108, 290, 46, "32 потоки → 32 різні банки\n(лінійне або переставлене)", size=12, fill="#eaf7ef", stroke=FIELD, sw=1.5))

    for i, (th, bk, addr) in enumerate([(0, 0, 0), (1, 1, 4), (2, 2, 8), (3, 3, 12), ("...", "...", "..."), (31, 31, 124)]):
        y = 175 + i * 46
        f.append(fitbox(60, y, 90, 36, "Потік %s" % th, size=11, fill="#eef2f7", stroke=MUTED, sw=1.2))
        f.append(arrow(155, y + 18, 195, y + 18, color=FIELD, sw=1.8))
        f.append(fitbox(200, y, 140, 36, "Банк %s (Адр %s)" % (bk, addr), size=11, fill="#eaf7ef", stroke=FIELD, sw=1.5))

    f.append(fitbox(55, 480, 290, 75, "Усі 32 запити обслуговуються\nпаралельно за 1 такт пам'яті.\nПропускна здатність = 100%.", size=13, fill="#eaf7ef", stroke=FIELD, sw=1.8))

    # Випадок 2: Трансляція (Broadcast)
    f.append(rect(400, 60, 320, 520, fill="#fbfbfc", stroke=NEG, sw=2.0, rx=8))
    f.append(text(560, 90, "2. Трансляція (Broadcast)", size=14, bold=True, color=NEG))
    f.append(fitbox(415, 108, 290, 46, "Кілька потоків читають\nОДНАКОВУ адресу в банку", size=12, fill="#eaf0fd", stroke=NEG, sw=1.5))

    for i, (th, bk, addr) in enumerate([(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), ("...", 0, 0), (31, 0, 0)]):
        y = 175 + i * 46
        f.append(fitbox(420, y, 90, 36, "Потік %s" % th, size=11, fill="#eef2f7", stroke=MUTED, sw=1.2))
        f.append(arrow(515, y + 18, 555, 313, color=NEG, sw=1.6))

    f.append(fitbox(560, 295, 145, 36, "Банк 0 (Адр 0)", size=11, fill="#eaf0fd", stroke=NEG, sw=2.0))

    f.append(fitbox(415, 480, 290, 75, "Апаратний механізм широкомовлення:\nодне слово розсилається всім за 1 такт.\nБанківського конфлікту НЕМАЄ.", size=12, fill="#eaf0fd", stroke=NEG, sw=1.8))

    # Випадок 3: 4-кратний банківський конфлікт
    f.append(rect(760, 60, 320, 520, fill="#fbfbfc", stroke=POS, sw=2.0, rx=8))
    f.append(text(920, 90, "3. Банківський конфлікт (4-way)", size=14, bold=True, color=POS))
    f.append(fitbox(775, 108, 290, 46, "Потоки звертаються до\nРІЗНИХ адрес в одному банку", size=12, fill="#fdecea", stroke=POS, sw=1.5))

    for i, (th, bk, addr, col, cycle) in enumerate([
        (0, 0, 0, POS, "Такт 1"),
        (8, 0, 128, POS, "Такт 2"),
        (16, 0, 256, POS, "Такт 3"),
        (24, 0, 384, POS, "Такт 4")
    ]):
        y = 175 + i * 65
        f.append(fitbox(780, y, 80, 44, "Потік %d\n(%s)" % (th, cycle), size=11, fill="#fdecea", stroke=col, sw=1.5))
        f.append(arrow(865, y + 22, 905, 290, color=POS, sw=1.6))

    f.append(fitbox(910, 268, 155, 44, "Банк 0\n(4 різні адреси!)", size=11, fill="#fdecea", stroke=POS, sw=2.2))

    f.append(fitbox(775, 480, 290, 75, "Серіалізація пам'яті:\n4 послідовні цикли шини.\nПропускна здатність падає в 4 рази.", size=12, fill="#fdecea", stroke=POS, sw=2.0))

    render(os.path.join(OUT, 'shared-memory-banks.svg'), W, H, *f)


# ── 4. Транспонування матриці: без паддингу проти [32][33] ──────────────────
def matrix_transpose_banks():
    W, H = 1080, 560
    f = []

    f.append(text(W / 2, 32, "Усунення банківських конфліктів у транспонуванні матриці", size=16, bold=True))

    # Ліва частина: tile[32][32] (32-кратний конфлікт)
    f.append(rect(40, 60, 480, 470, fill="#fbfbfc", stroke=POS, sw=2.0, rx=10))
    f.append(text(280, 92, "tile[32][32] — 32-кратний банківський конфлікт", size=14, bold=True, color=POS))

    f.append(fitbox(65, 115, 430, 55, "Запис рядків (conflict-free): Потік i пише в tile[y][i] → Банк i (1 такт).\nЗчитування стовпців: Потік i читає tile[i][x] → усі в Банк x!", size=12, fill="#fdecea", stroke=POS, sw=1.6))

    # Спрощена матриця банків 4x4
    f.append(text(280, 195, "Розподіл елементів по банках (рядок за рядком):", size=12, bold=True, color=MUTED))
    for r in range(4):
        for c in range(4):
            x = 120 + c * 80
            y = 215 + r * 42
            is_col0 = (c == 0)
            bg = "#fdecea" if is_col0 else "#eef2f7"
            bd = POS if is_col0 else MUTED
            f.append(fitbox(x, y, 70, 34, "B%d" % c, size=12, fill=bg, stroke=bd, sw=2.0 if is_col0 else 1.0))

    f.append(text(280, 400, "Стовпчик 0 (виділено): усі 32 елементи лежать у Банку 0!", size=12, bold=True, color=POS))
    f.append(fitbox(65, 425, 430, 80, "Результат: 32 послідовні такти пам'яті на одне читання стовпчика.\nШвидкість доступу падає у 32 рази (ефективність 3.1%).", size=13, fill="#fdecea", stroke=POS, sw=2.0))

    # Права частина: tile[32][33] (Паддинг +1)
    f.append(rect(560, 60, 480, 470, fill="#fbfbfc", stroke=FIELD, sw=2.0, rx=10))
    f.append(text(800, 92, "tile[32][33] — Паддинг +1 (Zero Bank Conflicts)", size=14, bold=True, color=FIELD))

    f.append(fitbox(585, 115, 430, 55, "Крок рядка стає 33 замість 32: gcd(33, 32) = 1.\nКожен наступний рядок зміщує початок на 1 банк праворуч.", size=12, fill="#eaf7ef", stroke=FIELD, sw=1.8))

    # Спрощена матриця банків з паддингом
    f.append(text(800, 195, "Розподіл елементів по банках зі зсувом (+1 на рядок):", size=12, bold=True, color=MUTED))
    for r in range(4):
        for c in range(4):
            x = 640 + c * 80
            y = 215 + r * 42
            bk = (r * 1 + c) % 4
            is_col0 = (c == 0)
            bg = "#eaf7ef" if is_col0 else "#f4f6f8"
            bd = FIELD if is_col0 else MUTED
            f.append(fitbox(x, y, 70, 34, "B%d" % bk, size=12, fill=bg, stroke=bd, sw=2.0 if is_col0 else 1.0))

    f.append(text(800, 400, "Стовпчик 0: елементи потрапляють у Банки 0, 1, 2, 3... (всі різні!)", size=12, bold=True, color=FIELD))
    f.append(fitbox(585, 425, 430, 80, "Результат: усі 32 потоки зчитують стовпчик за 1 такт пам'яті.\nБанківські конфлікти повністю ліквідовано (ефективність 100%).", size=13, fill="#eaf7ef", stroke=FIELD, sw=2.0))

    render(os.path.join(OUT, 'matrix-transpose-banks.svg'), W, H, *f)


if __name__ == '__main__':
    warp_divergence_mask()
    simt_stack_vs_its()
    shared_memory_banks()
    matrix_transpose_banks()
    print("ok:", sorted(os.listdir(OUT)))
