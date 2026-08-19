# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. harvard-split-l1.svg ──────────────────────────────────────────────────
# Роздільна Гарвардська ієрархія кешів L1 та виникнення неузгодженості
def fig_harvard_split():
    W, H = 820, 520
    p = []

    # Загальна рамка процесорного ядра
    p.append(rect(20, 20, 780, 290, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(40, 48, "Процесорне ядро (CPU Core)", size=14, color=INK, anchor="start", bold=True))

    # Ліва гілка: Конвеєр виконання і тракт даних
    p.append(rect(45, 75, 330, 95, fill="#eef2ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(210, 102, "Тракт даних та виконання", size=13, color=NEG, bold=True))
    p.append(text(210, 122, "Виконавчі блоки (ALU) + Буфер запису (Store Buffer)", size=11, color=INK))
    p.append(text(210, 140, "Інструкція запису: STR / MOV [addr], data", size=10.5, color=MUTED))

    # Права гілка: Конвеєр вибірки інструкцій
    p.append(rect(445, 75, 330, 95, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(610, 102, "Тракт вибірки інструкцій (Fetch)", size=13, color=POS, bold=True))
    p.append(text(610, 122, "Лічильник (PC) + Передбачувач переходів (BTB)", size=11, color=INK))
    p.append(text(610, 140, "Черга вибірки + Декодери / μop-кеш (DSB)", size=10.5, color=MUTED))

    # Рівень кешів L1: D-Cache та I-Cache
    p.append(rect(45, 205, 330, 80, fill="#e0e7ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(210, 235, "L1 D-Cache (Кеш даних)", size=13, color=NEG, bold=True))
    p.append(text(210, 255, "Читання/Запис, лінія MODIFIED (брудна)", size=11, color=INK))
    p.append(text(210, 272, "Містить НОВИЙ опкод інструкції", size=11, color=FIELD, bold=True))

    p.append(rect(445, 205, 330, 80, fill="#fee2e2", stroke=POS, sw=1.8, rx=6))
    p.append(text(610, 235, "L1 I-Cache (Кеш інструкцій)", size=13, color=POS, bold=True))
    p.append(text(610, 255, "Тільки читання конвеєром вибірки", size=11, color=INK))
    p.append(text(610, 272, "Містить ЗАСТАРІЛИЙ опкод інструкції", size=11, color=POS, bold=True))

    # Стрілки всередині ядра
    p.append(arrow(210, 170, 210, 205, color=NEG, sw=2.0))
    p.append(text(220, 190, "Запис байтів", size=10, color=NEG, anchor="start"))

    p.append(arrow(610, 205, 610, 170, color=POS, sw=2.0))
    p.append(text(620, 190, "Вибірка слів", size=10, color=POS, anchor="start"))

    # Червоний знак розриву когерентності між L1 D і L1 I
    p.append(line(375, 245, 445, 245, color=POS, sw=2.5, dash="4 3"))
    p.append(text(410, 235, "НЕМАЄ", size=10, color=POS, bold=True))
    p.append(text(410, 260, "зв'язку", size=10, color=POS, bold=True))

    # Рівні L2 і системна пам'ять
    p.append(rect(150, 345, 520, 65, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=6))
    p.append(text(410, 372, "Об'єднаний L2 Кеш / L3 Кеш (Unified)", size=13, color=INK, bold=True))
    p.append(text(410, 394, "Точка об'єднання когерентності (Point of Unification / PoU)", size=11, color=MUTED))

    p.append(rect(150, 440, 520, 55, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(410, 468, "Оперативна пам'ять (DRAM / Фізична пам'ять)", size=13, color=INK, bold=True))
    p.append(text(410, 484, "Точка загальної когерентності (Point of Coherency / PoC)", size=10.5, color=MUTED))

    # Стрілки до L2
    p.append(arrow(210, 285, 260, 345, color=NEG, sw=1.8))
    p.append(text(190, 320, "Скидання (Evict/Clean)", size=10, color=NEG, anchor="end"))

    p.append(arrow(560, 345, 610, 285, color=POS, sw=1.8))
    p.append(text(630, 320, "Заповнення промаху (Fill)", size=10, color=POS, anchor="start"))

    # Стрілка між L2 і RAM
    p.append(line(410, 410, 410, 440, color=LINE, sw=1.5, dash="3 3"))

    render(os.path.join(OUT, "harvard-split-l1.svg"), W, H, *p,
           title="Роздільна Гарвардська ієрархія кешів L1: неузгодженість I-Cache та D-Cache")


# ── 2. arm-cache-maintenance-sequence.svg ────────────────────────────────────
# Послідовність програмного скидання та синхронізації кешів в ARM64
def fig_arm_maintenance():
    W, H = 840, 460
    p = []

    # Заголовок зверху
    p.append(text(420, 30, "Послідовність синхронізації коду в архітектурі ARM64", size=14, color=INK, bold=True))

    steps = [
        ("1. Модифікація коду", "STR W0, [X1]", "Запис нових байтів інструкції через тракт даних.", "Оновлює рядок у L1 D-Cache (Dirty).", NEG),
        ("2. Очищення D-Cache", "DC CVAU, X1", "Скидання брудного рядка кешу даних до PoU (L2).", "Дані виштовхуються в спільний L2 кеш.", FIELD),
        ("3. Бар'єр пам'яті", "DSB ISH", "Очікування завершення операції запису та очищення.", "Гарантує завершення шинних транзакцій.", INK),
        ("4. Інвалідація I-Cache", "IC IVAU, X1", "Вилучення застарілого рядка з кешу інструкцій.", "L1 I-Cache відкидає старий опкод.", POS),
        ("5. Бар'єр пам'яті", "DSB ISH", "Очікування завершення інвалідації I-Cache на ядрах.", "Усі кеші інструкцій скинули рядок.", INK),
        ("6. Синхронізація конвеєра", "ISB", "Скидання черги вибірки, декодерів та конвеєра.", "Вимушує новий Fetch з L1 I / L2.", POS),
        ("7. Виконання", "BLR X1", "Перехід на модифіковану адресу та виконання.", "Процесор виконує гарантовано новий код.", FIELD)
    ]

    sy = 65
    row_h = 50
    for i, (title, instr, desc, effect, col) in enumerate(steps):
        y = sy + i * (row_h + 6)
        # Блок кроку
        p.append(rect(40, y, 160, row_h, fill="#f8fafc", stroke=col, sw=1.8, rx=5))
        p.append(text(120, y + 20, title, size=11, color=col, bold=True))
        p.append(text(120, y + 38, instr, size=11.5, color=INK, bold=True))

        # Стрілка переходу
        if i < len(steps) - 1:
            p.append(arrow(120, y + row_h, 120, y + row_h + 6, color=col, sw=1.5))

        # Опис дії
        p.append(rect(215, y, 310, row_h, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
        p.append(text(370, y + 28, desc, size=11, color=INK))

        # Апаратний ефект
        p.append(rect(535, y, 265, row_h, fill="#f8fafc", stroke=LINE, sw=1.2, rx=5))
        p.append(text(667, y + 28, effect, size=10.5, color=MUTED))

    render(os.path.join(OUT, "arm-cache-maintenance-sequence.svg"), W, H, *p,
           title="Послідовність скидання та інвалідації кешів у ARM64")


# ── 3. x86-snoop-vs-arm-software.svg ──────────────────────────────────────────
# Порівняння апаратного снупінгу x86 та програмного керування ARM/RISC-V
def fig_x86_vs_arm():
    W, H = 820, 420
    p = []

    # Ліва колонка: x86 Hardware Snoop
    p.append(rect(30, 25, 365, 365, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(212, 55, "x86 / x86-64: Апаратний снупінг (SMC)", size=13, color=FIELD, bold=True))

    p.append(rect(50, 75, 325, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
    p.append(text(212, 98, "Запис інструкції через D-Cache", size=11.5, color=INK, bold=True))
    p.append(text(212, 118, "Звичайний store: MOV [rip+offset], eax", size=10.5, color=MUTED))

    p.append(arrow(212, 135, 212, 155, color=FIELD, sw=1.6))

    p.append(rect(50, 155, 325, 75, fill="#ffffff", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(212, 178, "Апаратна логіка виявлення SMC", size=11.5, color=FIELD, bold=True))
    p.append(text(212, 198, "Снупінг перевіряє адресу запису в I-Cache,", size=10.5, color=INK))
    p.append(text(212, 214, "черзі вибірки, декодерах та буфері ROB", size=10.5, color=INK))

    p.append(arrow(212, 230, 212, 250, color=FIELD, sw=1.6))

    p.append(rect(50, 250, 325, 65, fill="#ffffff", stroke=POS, sw=1.5, rx=5))
    p.append(text(212, 273, "Апаратне скидання (Machine Clear)", size=11.5, color=POS, bold=True))
    p.append(text(212, 293, "Повне очищення конвеєра та I-Cache лінії.", size=10.5, color=INK))
    p.append(text(212, 307, "Штраф: ~150-300 тактів простою ядра", size=10, color=POS))

    p.append(rect(50, 325, 325, 50, fill="#f8fafc", stroke=LINE, sw=1.2, rx=5))
    p.append(text(212, 345, "Вимога: Серіалізація через CPUID / JMP", size=10.5, color=INK, bold=True))
    p.append(text(212, 362, "Забезпечує безпеку при випереджальній вибірці", size=9.5, color=MUTED))

    # Права колонка: ARM / RISC-V Software Maintenance
    p.append(rect(425, 25, 365, 365, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(607, 55, "ARM / RISC-V: Програмне керування", size=13, color=NEG, bold=True))

    p.append(rect(445, 75, 325, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
    p.append(text(607, 98, "Запис інструкції через D-Cache", size=11.5, color=INK, bold=True))
    p.append(text(607, 118, "Звичайний store: STR W0, [X1]", size=10.5, color=MUTED))

    p.append(arrow(607, 135, 607, 155, color=NEG, sw=1.6))

    p.append(rect(445, 155, 325, 75, fill="#ffffff", stroke=NEG, sw=1.5, rx=5))
    p.append(text(607, 178, "Апаратний снупінг ВІДСУТНІЙ", size=11.5, color=NEG, bold=True))
    p.append(text(607, 198, "L1 I-Cache не знає про зміни в D-Cache.", size=10.5, color=INK))
    p.append(text(607, 214, "Економія кремнію та енергоспоживання ядра.", size=10.5, color=FIELD))

    p.append(arrow(607, 230, 607, 250, color=NEG, sw=1.6))

    p.append(rect(445, 250, 325, 65, fill="#ffffff", stroke=NEG, sw=1.5, rx=5))
    p.append(text(607, 273, "Явні інструкції обслуговування кешу", size=11.5, color=NEG, bold=True))
    p.append(text(607, 293, "DC CVAU + DSB + IC IVAU + DSB + ISB", size=11, color=INK, bold=True))
    p.append(text(607, 307, "RISC-V: FENCE.I / sbi_remote_fence_i()", size=10, color=MUTED))

    p.append(rect(445, 325, 325, 50, fill="#f8fafc", stroke=LINE, sw=1.2, rx=5))
    p.append(text(607, 345, "Передбачуваність: штраф лише при виклику", size=10.5, color=INK, bold=True))
    p.append(text(607, 362, "Швидкий звичайний код без зайвих апаратних перевірок", size=9.5, color=MUTED))

    render(os.path.join(OUT, "x86-snoop-vs-arm-software.svg"), W, H, *p,
           title="Апаратний снупінг x86 проти явного програмного керування ARM/RISC-V")


# ── 4. kernel-text-poke-bp.svg ────────────────────────────────────────────────
# Механізм безпечного багатобайтового латання тексту ядра (text_poke_bp)
def fig_kernel_text_poke():
    W, H = 840, 480
    p = []

    p.append(text(420, 28, "Атомарне латання коду ядра через точку зупину (text_poke_bp)", size=14, color=INK, bold=True))

    stages = [
        ("Фаза 0: Вихідний стан", "5-байтова інструкція: NOP5 (0x0F 0x1F 0x44 0x00 0x00)", "Ядра виконують оригінальний код без зупинок.", "#64748b"),
        ("Фаза 1: Атомарна вставка INT3", "Запис 1 байта: 0xCC (INT3) на початок інструкції", "Якщо інше ядро стрибне сюди — виникне пастка INT3 (обробник виконає новий код).", POS),
        ("Фаза 2: Синхронізація ядер", "Розсилка IPI + sync_core() на всі активні ядра CPU", "Скидання черг вибірки та конвеєрів усіх ядер для гарантії бачення 0xCC.", INK),
        ("Фаза 3: Запис тіла патчу", "Копіювання байтів 2..5 (новий зсув відносного виклику CALL)", "Тіло інструкції змінюється, поки перший байт надійно захищений пасткою 0xCC.", FIELD),
        ("Фаза 4: Повернення першого байта", "Атомарний запис 0xE8 (опкод CALL) замість 0xCC", "Пастку знято; перший байт стає новим опкодом виклику ftrace/kprobe.", NEG),
        ("Фаза 5: Фінальний бар'єр", "Повторний IPI + sync_core() для синхронізації конвеєрів", "Усі ядра виконують новий швидкий прямий виклик CALL без участі обробника пасток.", FIELD)
    ]

    sy = 55
    row_h = 60
    for i, (title, code_str, desc, col) in enumerate(stages):
        y = sy + i * (row_h + 8)
        p.append(rect(35, y, 220, row_h, fill="#f8fafc", stroke=col, sw=1.8, rx=6))
        p.append(text(145, y + 24, title, size=11.5, color=col, bold=True))
        p.append(text(145, y + 46, "Крок " + str(i + 1), size=10.5, color=MUTED))

        if i < len(stages) - 1:
            p.append(arrow(145, y + row_h, 145, y + row_h + 8, color=col, sw=1.5))

        p.append(rect(265, y, 290, row_h, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
        p.append(text(410, y + 24, "Байтовий стан:", size=10, color=MUTED))
        p.append(text(410, y + 44, code_str, size=10.5, color=INK, bold=True))

        p.append(rect(565, y, 240, row_h, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
        lines = []
        words = desc.split(" ")
        cur = ""
        for w in words:
            if len(cur) + len(w) > 34:
                lines.append(cur)
                cur = w
            else:
                cur = cur + " " + w if cur else w
        if cur:
            lines.append(cur)
        ty = y + 22 if len(lines) == 2 else y + 17
        for li, ln in enumerate(lines):
            p.append(text(685, ty + li * 15, ln, size=9.5, color=INK))

    render(os.path.join(OUT, "kernel-text-poke-bp.svg"), W, H, *p,
           title="Безпечне латання інструкцій ядра через механізм text_poke_bp")


if __name__ == "__main__":
    fig_harvard_split()
    fig_arm_maintenance()
    fig_x86_vs_arm()
    fig_kernel_text_poke()
    print("All figures generated successfully.")
