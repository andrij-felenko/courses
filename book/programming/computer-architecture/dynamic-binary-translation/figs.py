# -*- coding: utf-8 -*-
"""Генератор фігур SVG для теми «Динамічна бінарна трансляція»."""

import sys
import os

# scripts/ у корені репо (чотири рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_dbt_pipeline():
    """Фігура 1: Архітектура конвеєра DBT — диспетчер, перекладач, IR та кеш трансляцій."""
    w, h = 920, 480
    frags = []

    # Гостьовий двійковий код (ліворуч)
    frags.append(rect(30, 80, 160, 280, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(110, 110, "Гостьовий бінарник", size=15, bold=True))
    frags.append(text(110, 130, "(x86-64 / RISC-V)", size=12, color=MUTED))

    frags.append(fitbox(45, 155, 130, 40, "mov eax, [rbx]\nadd eax, 4", size=12, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(45, 205, 130, 40, "cmp eax, 100\njge .L_loop", size=12, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(45, 255, 130, 40, "call do_work\nret", size=12, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(text(110, 325, "Гостьові адреси (PC)", size=11, color=MUTED))

    # Стрілка від бінарника до декодера
    frags.append(arrow(190, 220, 235, 220, color=LINE, sw=1.8))
    frags.append(text(212, 210, "Байти", size=11, color=MUTED))

    # Ядро DBT (центр)
    frags.append(rect(240, 50, 390, 390, fill="#f0f4f8", stroke="#475569", sw=2, rx=10))
    frags.append(text(435, 80, "Рушій DBT (Рівні трансляції)", size=16, bold=True))

    # Диспетчер
    frags.append(fitbox(260, 105, 350, 50, "Диспетчер виконання (Dispatcher Loop)\nПошук гостьового PC у хеш-таблиці трансляцій", size=13, bold=True, fill="#ffffff", stroke="#3b82f6"))

    # Декодер та IR
    frags.append(fitbox(260, 175, 165, 75, "Декодер базових блоків\nРозбір інструкцій\nдо розгалуження", size=12, fill="#ffffff", stroke=LINE))
    frags.append(arrow(425, 212, 445, 212, color=LINE, sw=1.5))
    frags.append(fitbox(445, 175, 165, 75, "Проміжне представлення\n(IR / TCG micro-ops)\nЛедачі EFLAGS", size=12, fill="#ffffff", stroke=LINE))

    # Стрілка вниз до генераторів
    frags.append(arrow(342, 155, 342, 175, color=POS, sw=1.8))
    frags.append(text(370, 168, "Промах", size=11, color=POS, bold=True))

    frags.append(arrow(527, 250, 527, 280, color=LINE, sw=1.5))

    # Дворівневий JIT
    frags.append(fitbox(260, 280, 165, 80, "Швидкий транслятор\n(Fast Baseline / TCG)\nПряма кодогенерація\nбез оптимізацій", size=12, fill="#e6fffa", stroke=FIELD))
    frags.append(fitbox(445, 280, 165, 80, "Оптимізуючий JIT\n(Hot Traces Optimizer)\nSSA, GVN, усунення\nбар'єрів і прапорців", size=12, fill="#fff7ed", stroke="#ea580c"))

    frags.append(arrow(425, 320, 445, 320, color="#ea580c", sw=1.5))
    frags.append(text(435, 308, "Гаряче", size=10, color="#ea580c", bold=True))

    # Профілювальник
    frags.append(fitbox(260, 380, 350, 45, "Профілювальник і лічильники виконання (Trace Profiler)", size=12, fill="#ffffff", stroke=MUTED))

    # Стрілка з DBT у Кеш коду
    frags.append(arrow(630, 220, 675, 220, color=FIELD, sw=2))
    frags.append(text(652, 210, "Нативний код", size=11, color=FIELD, bold=True))

    # Кеш коду (Code Cache) та Цільовий процесор (праворуч)
    frags.append(rect(680, 80, 210, 340, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(785, 110, "Кеш трансляцій", size=15, bold=True))
    frags.append(text(785, 130, "(Code Cache у RAM)", size=12, color=MUTED))

    frags.append(fitbox(695, 150, 180, 45, "Трансльований блок 1\n(ARM64 ldr / add / cmp)", size=12, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(695, 205, 180, 45, "Трансльований блок 2\n(Зшитий перехід)", size=12, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(695, 260, 180, 45, "Траса суперблоку\n(Оптимізований код)", size=12, fill="#fffbeb", stroke="#d97706"))

    frags.append(fitbox(695, 325, 180, 75, "Господарський процесор\n(Host CPU)\nПряме виконання залізом\nна повній швидкості", size=12, bold=True, fill="#eff6ff", stroke=NEG))

    # Зворотний зв'язок: попадання в кеш
    frags.append(arrow(695, 125, 610, 125, color=FIELD, sw=1.8))
    frags.append(text(652, 115, "Попадання", size=11, color=FIELD, bold=True))

    return render(os.path.join(OUT_DIR, "dbt-pipeline.svg"), w, h, *frags)


def fig_block_chaining():
    """Фігура 2: Пряме зшивання блоків (Direct Block Chaining) проти повернення в диспетчер."""
    w, h = 920, 460
    frags = []

    # Ліва половина: До зшивання (через диспетчер)
    frags.append(rect(30, 45, 410, 385, fill="#fff5f5", stroke="#f87171", sw=1.5, rx=8))
    frags.append(text(235, 75, "Без зшивання: повернення в диспетчер", size=15, bold=True, color=POS))
    frags.append(text(235, 95, "Кожен перехід коштує 40–80 тактів на виклик диспетчера", size=11, color=MUTED))

    frags.append(fitbox(60, 120, 350, 60, "Блок 1 (Host Code у кеші)\n... арифметика ...\njump .L_exit_trampoline", size=12, fill="#ffffff", stroke=LINE))

    frags.append(arrow(235, 180, 235, 215, color=POS, sw=1.8))
    frags.append(text(290, 200, "Вихід із блоку", size=11, color=POS))

    frags.append(fitbox(60, 215, 350, 70, "Трамплін і Диспетчер (Dispatcher)\n1. Зберегти регістри гостя в пам'ять\n2. Знайти адресу Блоку 2 в хеш-таблиці\n3. Відновити регістри й стрибнути в Блок 2", size=12, fill="#ffffff", stroke=POS))

    frags.append(arrow(235, 285, 235, 320, color=POS, sw=1.8))
    frags.append(text(290, 305, "Непрямий стрибок", size=11, color=POS))

    frags.append(fitbox(60, 320, 350, 60, "Блок 2 (Host Code у кеші)\n... продовження виконання ...\njump .L_exit_trampoline", size=12, fill="#ffffff", stroke=LINE))

    frags.append(text(235, 410, "Ціна: промахи передбачення переходу (BTB) + доступ до RAM", size=11, color=POS, bold=True))

    # Права половина: Після зшивання (Direct Block Chaining)
    frags.append(rect(480, 45, 410, 385, fill="#f0fdf4", stroke="#4ade80", sw=1.5, rx=8))
    frags.append(text(685, 75, "Пряме зшивання (Direct Chaining)", size=15, bold=True, color=FIELD))
    frags.append(text(685, 95, "Патчинг вихідної інструкції на прямий стрибок", size=11, color=MUTED))

    frags.append(fitbox(510, 120, 350, 75, "Блок 1 (Host Code у кеші)\n... арифметика ...\nb .L_block_2   // Запатчено прямою адресою!\n(колишній стрибок на трамплін замінено)", size=12, fill="#ffffff", stroke=FIELD))

    # Пряма стрілка переходу
    frags.append(arrow(685, 195, 685, 220, color=FIELD, sw=2.5))
    frags.append(textbox(685, 242, "Прямий нативний перехід\n(1 такт процесора)", size=12, bold=True, fill="#dcfce7", stroke=FIELD)[0])
    frags.append(arrow(685, 265, 685, 290, color=FIELD, sw=2.5))

    frags.append(fitbox(510, 290, 350, 65, "Блок 2 (Host Code у кеші)\n... виконання без зупинки ...\nb .L_block_3   // Наступне зшивання", size=12, fill="#ffffff", stroke=FIELD))

    frags.append(fitbox(510, 370, 350, 45, "Диспетчер більше НЕ викликається!\nКод виконується безперервно всередині Code Cache", size=12, bold=True, fill="#ffffff", stroke="#15803d"))

    return render(os.path.join(OUT_DIR, "block-chaining.svg"), w, h, *frags)


def fig_tso_memory_models():
    """Фігура 3: Порівняння моделей пам'яті TSO (x86) та Weak Ordering (ARM) з апаратним бітом Rosetta."""
    w, h = 920, 460
    frags = []

    # x86 TSO (ліворуч)
    frags.append(rect(30, 45, 265, 385, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(162, 75, "x86 TSO", size=16, bold=True))
    frags.append(text(162, 95, "Строге впорядкування (Total Store Order)", size=11, color=MUTED))

    frags.append(fitbox(45, 115, 235, 65, "Апаратний Store Buffer (FIFO)\nЗаписи потрапляють у пам'ять\nу строгому порядку програми", size=12, fill="#ffffff", stroke=LINE))

    frags.append(fitbox(45, 190, 235, 110, "Заборонені перевпорядкування:\n• Load → Load  (ЗАБОРОНЕНО)\n• Store → Store (ЗАБОРОНЕНО)\n• Load → Store (ЗАБОРОНЕНО)\nДозволено лише:\n• Store → Load (через буфер)", size=11, fill="#eff6ff", stroke=NEG))

    frags.append(fitbox(45, 310, 235, 100, "Наслідок для ПЗ:\nБагатопотоковий код x86\nНЕ використовує бар'єри пам'яті\nдля звичайних load/store", size=12, fill="#ffffff", stroke=LINE))

    # Звичайний ARM64 WMO (центр)
    frags.append(rect(325, 45, 270, 385, fill="#fff7ed", stroke="#f97316", sw=1.5, rx=8))
    frags.append(text(460, 75, "Стандартний ARM64 / RISC-V", size=15, bold=True, color="#ea580c"))
    frags.append(text(460, 95, "Слабка модель (Weak Memory Ordering)", size=11, color=MUTED))

    frags.append(fitbox(340, 115, 240, 65, "Позачерговий конвеєр (OoO)\nЧитання й записи можуть мінятися\nмісцями довільно", size=12, fill="#ffffff", stroke=LINE))

    frags.append(fitbox(340, 190, 240, 110, "Дозволені перевпорядкування:\n• Load → Load  (ДОЗВОЛЕНО)\n• Store → Store (ДОЗВОЛЕНО)\n• Store → Load (ДОЗВОЛЕНО)\n• Load → Store (ДОЗВОЛЕНО)", size=11, fill="#fef2f2", stroke=POS))

    frags.append(fitbox(340, 310, 240, 100, "Програмна емуляція DBT:\nМусить вставляти dmb ish\nабо ldar/stlr на КОЖЕН доступ!\nВтрата 30–50% швидкодії", size=12, bold=True, fill="#ffffff", stroke=POS))

    # Apple Silicon TSO (праворуч)
    frags.append(rect(625, 45, 265, 385, fill="#f0fdf4", stroke="#22c55e", sw=2, rx=8))
    frags.append(text(757, 75, "Apple Silicon (Rosetta 2)", size=16, bold=True, color=FIELD))
    frags.append(text(757, 95, "Апаратний TSO-біт у кремнії M1/M2/M3", size=11, color=MUTED))

    frags.append(fitbox(640, 115, 235, 65, "Регістр конфігурації ядра\nВмикає апаратний режим TSO\nдля потоків емуляції x86", size=12, fill="#ffffff", stroke=FIELD))

    frags.append(fitbox(640, 190, 235, 110, "Апаратна поведінка ядра:\n• Блок Load/Store Queue сам\n  дотримується правил x86 TSO\n• Забороняє некоректні OoO\n  перевпорядкування в залізі", size=11, fill="#dcfce7", stroke=FIELD))

    frags.append(fitbox(640, 310, 235, 100, "Результат Rosetta 2:\nНуль інструкцій dmb ish!\nЗвичайні ldr / str виконуються\nіз швидкістю 90–95% нативу", size=12, bold=True, fill="#ffffff", stroke="#15803d"))

    return render(os.path.join(OUT_DIR, "tso-memory-models.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_dbt_pipeline()
    fig_block_chaining()
    fig_tso_memory_models()
    print("Всі 3 фігури згенеровано успішно.")
