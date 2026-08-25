# -*- coding: utf-8 -*-
"""Фігури до теми «Багато читачів, один письменник» (Readers-Writer Lock).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольори ролей (палітра svgkit)
READ_COL  = "#1b7340"    # спільне читання (зелений / безпечний паралелізм)
WRITE_COL = "#c0392b"    # ексклюзивний запис (червоний / виключний доступ)
WAIT_COL  = "#d35400"    # очікування в черзі (помаранчевий)
BLOCK_COL = "#7f8c8d"    # заблокований стан (сірий)
WARN      = "#caa24a"    # рамка-висновок

def boxlabel(f, x, y, w, h, s, fill=FILL, stroke=LINE, tcol=INK, size=12, sw=1.5):
    """Прямокутник із підписом по центру (fitbox якщо кілька рядків)."""
    if "\n" in s:
        f.append(fitbox(x, y, w, h, s.split("\n"), size=size, fill=fill,
                        stroke=stroke, sw=sw, color=tcol, bold=True, pad=6))
        return
    f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=6))
    fs = fit_font(s, w - 12, size, bold=True)
    f.append(text(x + w / 2, y + h / 2 + fs * 0.35, s, size=fs, color=tcol, bold=True))

def note(f, cx, y, w, lines, fill="#fff6e0", stroke=WARN, size=11):
    """Рамка-висновок унизу фігури."""
    f.append(fitbox(cx - w / 2, y, w, 18 + size * 1.3 * len(lines), lines,
                    size=size, fill=fill, stroke=stroke))

# ── 1. Порівняння: Звичайний м'ютекс проти RWLock ────────────────────────────
def fig_rwlock_concept():
    W, H = 880, 430
    f = []
    f.append(text(W / 2, 28, "Звичайний м'ютекс проти замка читачів-письменника (RWLock)", size=16, bold=True))
    f.append(text(W / 2, 48, "М'ютекс штучно вишиковує паралельних читачів у чергу; RWLock дозволяє їм читати одночасно", size=11, color=MUTED, italic=True))

    # Секція 1: Звичайний м'ютекс
    f.append(rect(30, 70, 820, 150, fill="#fcfcfc", stroke="#d0d7de", sw=1.2, rx=8))
    f.append(text(50, 95, "Звичайний м'ютекс (Mutex): суворе взаємне виключення", size=13, color=POS, bold=True, anchor="start"))

    # Потік 1
    f.append(text(45, 130, "Потік R1 (читач)", size=11, color=INK, anchor="start"))
    boxlabel(f, 180, 115, 180, 30, "Читання пам'яті (захоплено)", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11)

    # Потік 2
    f.append(text(45, 165, "Потік R2 (читач)", size=11, color=INK, anchor="start"))
    boxlabel(f, 180, 150, 180, 30, "Заблокований (чекає R1)", fill="#f2f4f8", stroke=BLOCK_COL, tcol=MUTED, size=11)
    boxlabel(f, 380, 150, 180, 30, "Читання пам'яті (захоплено)", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11)

    # Потік 3
    f.append(text(45, 200, "Потік R3 (читач)", size=11, color=INK, anchor="start"))
    boxlabel(f, 180, 185, 380, 30, "Заблокований (чекає черги R1 і R2)", fill="#f2f4f8", stroke=BLOCK_COL, tcol=MUTED, size=11)
    boxlabel(f, 580, 185, 180, 30, "Читання пам'яті", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11)

    # Секція 2: RWLock
    f.append(rect(30, 235, 820, 145, fill="#fcfcfc", stroke="#d0d7de", sw=1.2, rx=8))
    f.append(text(50, 260, "Замок читачів-письменника (RWLock): спільний режим для читання", size=13, color=READ_COL, bold=True, anchor="start"))

    f.append(text(45, 290, "Потік R1 (читач)", size=11, color=INK, anchor="start"))
    boxlabel(f, 180, 275, 280, 26, "Спільне читання пам'яті (Shared)", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11)

    f.append(text(45, 320, "Потік R2 (читач)", size=11, color=INK, anchor="start"))
    boxlabel(f, 180, 305, 280, 26, "Спільне читання пам'яті (Shared)", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11)

    f.append(text(45, 350, "Потік R3 (читач)", size=11, color=INK, anchor="start"))
    boxlabel(f, 180, 335, 280, 26, "Спільне читання пам'яті (Shared)", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11)

    # Письменник W1
    f.append(text(480, 320, "Письменник W1 (чекає завершення R1, R2, R3)", size=11, color=WAIT_COL, bold=True, anchor="start"))
    boxlabel(f, 480, 335, 280, 26, "Ексклюзивний запис (Exclusive)", fill="#fdecea", stroke=WRITE_COL, tcol=WRITE_COL, size=11)

    note(f, W / 2, 390, 800, [
        "Висновок: читання без змін стану безпечне для паралельного виконання.",
        "RWLock дає паралелізм читачам, але зберігає суворе виключення для письменника."
    ], size=10)

    render(os.path.join(IMG, "rwlock-concept.svg"), W, H, *f)

# ── 2. Голодування письменника (Writer Starvation) ───────────────────────────
def fig_writer_starvation():
    W, H = 880, 400
    f = []
    f.append(text(W / 2, 28, "Голодування письменника за пріоритету читачів (Reader Preference)", size=16, bold=True))
    f.append(text(W / 2, 48, "Поки хоч один читач утримує замок, нові читачі заходять без черги — письменник чекає нескінченно", size=11, color=MUTED, italic=True))

    # Вісь часу
    f.append(line(160, 310, 840, 310, color=LINE, sw=1.5))
    f.append(arrow(830, 310, 845, 310, color=LINE, sw=1.5))
    f.append(text(840, 325, "Час (t)", size=11, color=INK, anchor="end"))

    # Читач 1
    f.append(text(40, 85, "Читач 1", size=12, color=INK, anchor="start", bold=True))
    boxlabel(f, 170, 70, 200, 30, "Читає", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11)

    # Читач 2
    f.append(text(40, 130, "Читач 2", size=12, color=INK, anchor="start", bold=True))
    boxlabel(f, 300, 115, 220, 30, "Читає (перекриває Читача 1)", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11)

    # Читач 3
    f.append(text(40, 175, "Читач 3", size=12, color=INK, anchor="start", bold=True))
    boxlabel(f, 460, 160, 220, 30, "Читає (перекриває Читача 2)", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11)

    # Читач 4
    f.append(text(40, 220, "Читач 4", size=12, color=INK, anchor="start", bold=True))
    boxlabel(f, 620, 205, 200, 30, "Читає (ланцюг триває)", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11)

    # Письменник
    f.append(text(40, 270, "Письменник W", size=12, color=WRITE_COL, anchor="start", bold=True))
    f.append(line(240, 60, 240, 290, color=POS, sw=1.2, dash="3,3"))
    f.append(text(245, 255, "Запит на запис", size=10, color=POS, anchor="start", bold=True))
    boxlabel(f, 240, 260, 580, 30, "ГОЛОДУВАННЯ: лічильник активних читачів ніколи не падає до 0", fill="#fdecea", stroke=WRITE_COL, tcol=WRITE_COL, size=11)

    note(f, W / 2, 345, 820, [
        "Небезпека: за неперервного потоку читачів сума активних читачів завжди більша за нуль.",
        "Письменник не отримує доступу, доки не зміниться політика на користь черги або письменників."
    ], size=10)

    render(os.path.join(IMG, "writer-starvation.svg"), W, H, *f)

# ── 3. Порівняння трьох політик планування RWLock ────────────────────────────
def fig_policies_timeline():
    W, H = 880, 460
    f = []
    f.append(text(W / 2, 26, "Три політики доступу в RWLock", size=16, bold=True))
    f.append(text(W / 2, 46, "Пріоритет читачів, пріоритет письменників та фазова справедливість (FIFO)", size=11, color=MUTED, italic=True))

    # 1. Пріоритет читачів
    f.append(rect(30, 65, 820, 95, fill="#fcfcfc", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(45, 85, "1. Пріоритет читачів (Read-preferring): максимум паралелізму читання", size=12, color=READ_COL, bold=True, anchor="start"))
    boxlabel(f, 200, 100, 150, 26, "Читачі R1, R2", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=10)
    boxlabel(f, 320, 118, 150, 26, "Читач R3 (заходить)", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=10)
    boxlabel(f, 440, 100, 150, 26, "Читач R4 (заходить)", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=10)
    boxlabel(f, 250, 72, 330, 22, "Письменник W1 (голодує в очікуванні)", fill="#fdecea", stroke=WRITE_COL, tcol=WRITE_COL, size=10)
    boxlabel(f, 610, 100, 140, 26, "W1 нарешті пише", fill="#fdecea", stroke=WRITE_COL, tcol=WRITE_COL, size=10)

    # 2. Пріоритет письменників
    f.append(rect(30, 175, 820, 95, fill="#fcfcfc", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(45, 195, "2. Пріоритет письменників (Write-preferring): захист від застарівання даних", size=12, color=WRITE_COL, bold=True, anchor="start"))
    boxlabel(f, 200, 210, 140, 26, "Активні R1, R2", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=10)
    f.append(line(345, 185, 345, 255, color=POS, sw=1.5, dash="3,3"))
    f.append(text(348, 192, "Прийшов W1: бар'єр", size=9, color=POS, anchor="start", bold=True))
    boxlabel(f, 355, 210, 130, 26, "W1 пише монопольно", fill="#fdecea", stroke=WRITE_COL, tcol=WRITE_COL, size=10)
    boxlabel(f, 355, 238, 130, 22, "R3, R4 чекають у черзі", fill="#f2f4f8", stroke=BLOCK_COL, tcol=MUTED, size=9)
    boxlabel(f, 500, 210, 160, 26, "R3, R4 читають разом", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=10)

    # 3. Фазова справедливість (Phase-fair / FIFO)
    f.append(rect(30, 285, 820, 95, fill="#fcfcfc", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(45, 305, "3. Фазова справедливість (Phase-fair / FIFO): чергування груп читачів і письменника", size=12, color=FIELD, bold=True, anchor="start"))
    boxlabel(f, 200, 320, 140, 26, "Фаза 1: R1, R2 читають", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=10)
    boxlabel(f, 355, 320, 140, 26, "Фаза 2: W1 пише", fill="#fdecea", stroke=WRITE_COL, tcol=WRITE_COL, size=10)
    boxlabel(f, 510, 320, 160, 26, "Фаза 3: R3, R4 читають разом", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=10)
    boxlabel(f, 685, 320, 140, 26, "Фаза 4: W2 пише", fill="#fdecea", stroke=WRITE_COL, tcol=WRITE_COL, size=10)

    note(f, W / 2, 405, 820, [
        "Вибір політики визначає гарантії: пріоритет письменників запобігає затримці оновлень,",
        "а фазова справедливість гарантує передбачуваний час очікування для обох сторін."
    ], size=10)

    render(os.path.join(IMG, "policies-timeline.svg"), W, H, *f)

# ── 4. Пастка апгрейду: дедлок під час переходу з читання на запис ────────────
def fig_upgrade_deadlock():
    W, H = 880, 390
    f = []
    f.append(text(W / 2, 28, "Пастка підвищення блокування (Lock Upgrading Deadlock)", size=16, bold=True))
    f.append(text(W / 2, 48, "Чому пряме перетворення блокування читача на блокування запису призводить до мертвої петлі", size=11, color=MUTED, italic=True))

    # Ліва колонка: Потік 1
    f.append(rect(60, 75, 340, 220, fill="#fcfcfc", stroke=READ_COL, sw=1.5, rx=8))
    f.append(text(230, 100, "Потік A (Reader 1)", size=13, color=READ_COL, bold=True))
    boxlabel(f, 85, 120, 290, 32, "1. Тримає Shared Read Lock", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11)
    boxlabel(f, 85, 175, 290, 32, "3. Бажає оновити запис (upgrade)", fill="#fff3cd", stroke=WARN, tcol=INK, size=11)
    boxlabel(f, 85, 230, 290, 45, "Чекає, поки Потік B\nвідпустить свій Read Lock", fill="#fdecea", stroke=POS, tcol=POS, size=11)

    # Права колонка: Потік 2
    f.append(rect(480, 75, 340, 220, fill="#fcfcfc", stroke=READ_COL, sw=1.5, rx=8))
    f.append(text(650, 100, "Потік B (Reader 2)", size=13, color=READ_COL, bold=True))
    boxlabel(f, 505, 120, 290, 32, "2. Тримає Shared Read Lock", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11)
    boxlabel(f, 505, 175, 290, 32, "4. Бажає оновити запис (upgrade)", fill="#fff3cd", stroke=WARN, tcol=INK, size=11)
    boxlabel(f, 505, 230, 290, 45, "Чекає, поки Потік A\nвідпустить свій Read Lock", fill="#fdecea", stroke=POS, tcol=POS, size=11)

    # Стрілки взаємного блокування
    f.append(arrow(375, 245, 505, 245, color=POS, sw=2))
    f.append(arrow(505, 260, 375, 260, color=POS, sw=2))
    f.append(text(440, 235, "ДЕДЛОК", size=12, color=POS, bold=True))

    note(f, W / 2, 325, 800, [
        "Правило архітектури: безпечного атомарного «апгрейду» блокування з читання на запис не існує.",
        "Щоб писати, читач зобов'язаний відпустити Read Lock і заново запросити Write Lock."
    ], size=10)

    render(os.path.join(IMG, "upgrade-deadlock.svg"), W, H, *f)

# ── 5. Автомат станів атомарного RWLock ──────────────────────────────────────
def fig_rwlock_state_machine():
    W, H = 880, 420
    f = []
    f.append(text(W / 2, 28, "Автомат станів атомарного Readers-Writer Lock", size=16, bold=True))
    f.append(text(W / 2, 48, "Як одне 32-бітне атомарне слово кодує вільний стан, читачів і чергу запису", size=11, color=MUTED, italic=True))

    # Стан 1: Вільний
    boxlabel(f, 80, 160, 180, 70, "ВІЛЬНИЙ (UNLOCKED)\nreaders = 0\nwriter_active = 0", fill="#f8f9fa", stroke=FIELD, tcol=INK, size=11, sw=2)

    # Стан 2: Читання
    boxlabel(f, 350, 80, 210, 70, "СПІЛЬНЕ ЧИТАННЯ (SHARED)\nreaders = N (N > 0)\nwriter_active = 0", fill="#d4edda", stroke=READ_COL, tcol=READ_COL, size=11, sw=2)

    # Стан 3: Очікування запису
    boxlabel(f, 620, 160, 210, 70, "ОЧІКУВАННЯ ЗАПИСУ\nreaders = N (падає до 0)\nwriters_waiting > 0", fill="#fff3cd", stroke=WAIT_COL, tcol=INK, size=11, sw=2)

    # Стан 4: Ексклюзивний запис
    boxlabel(f, 350, 260, 210, 70, "ЕКСКЛЮЗИВНИЙ ЗАПИС\nreaders = 0\nwriter_active = 1", fill="#fdecea", stroke=WRITE_COL, tcol=WRITE_COL, size=11, sw=2)

    # Переходи (стрілки)
    # Вільний -> Читання
    f.append(arrow(210, 160, 350, 120, color=READ_COL, sw=1.6))
    f.append(text(240, 130, "+1 читач (CAS)", size=10, color=READ_COL, bold=True))

    # Читання -> Вільний
    f.append(arrow(350, 140, 240, 180, color=MUTED, sw=1.4))
    f.append(text(300, 175, "останній reader_unlock", size=9, color=MUTED))

    # Читання -> Очікування запису
    f.append(arrow(560, 120, 650, 160, color=WAIT_COL, sw=1.6))
    f.append(text(640, 130, "write_lock() чекає", size=10, color=WAIT_COL, bold=True))

    # Очікування запису -> Ексклюзивний запис
    f.append(arrow(670, 230, 560, 280, color=WRITE_COL, sw=1.6))
    f.append(text(660, 275, "readers == 0 (сигнал)", size=10, color=WRITE_COL, bold=True))

    # Вільний -> Ексклюзивний запис
    f.append(arrow(220, 220, 350, 280, color=WRITE_COL, sw=1.6))
    f.append(text(230, 270, "write_lock() (CAS)", size=10, color=WRITE_COL, bold=True))

    # Ексклюзивний запис -> Вільний
    f.append(arrow(350, 290, 170, 230, color=FIELD, sw=1.6))
    f.append(text(210, 310, "write_unlock()", size=10, color=FIELD, bold=True))

    note(f, W / 2, 365, 820, [
        "Атомарний стан контролює всі переходи: атомарний інкремент для читачів,",
        "встановлення прапорця письменника і пробудження потоків через системний виклик futex."
    ], size=10)

    render(os.path.join(IMG, "rwlock-state-machine.svg"), W, H, *f)

# ── 6. Проблема масштабування: Cache Line Bouncing на багатьох ядрах ─────────
def fig_cache_line_bouncing():
    W, H = 880, 420
    f = []
    f.append(text(W / 2, 28, "Ціна спільних лічильників: Cache Line Bouncing на багатьох ядрах", size=16, bold=True))
    f.append(text(W / 2, 48, "Кожен атомарний read_lock() інвалідує спільний рядок кешу на всіх інших процесорних ядрах", size=11, color=MUTED, italic=True))

    # Ліва частина: Звичайний RWLock (проблема)
    f.append(rect(40, 75, 380, 245, fill="#fcfcfc", stroke=POS, sw=1.2, rx=8))
    f.append(text(230, 98, "Централізований RWLock", size=13, color=POS, bold=True))

    boxlabel(f, 90, 120, 120, 35, "Ядро 0\nfetch_add()", fill="#fdecea", stroke=POS, size=10)
    boxlabel(f, 270, 120, 120, 35, "Ядро 1\nfetch_add()", fill="#fdecea", stroke=POS, size=10)
    boxlabel(f, 90, 180, 120, 35, "Ядро 2\nfetch_add()", fill="#fdecea", stroke=POS, size=10)
    boxlabel(f, 270, 180, 120, 35, "Ядро 3\nfetch_add()", fill="#fdecea", stroke=POS, size=10)

    # Спільний рядок кешу
    boxlabel(f, 100, 245, 260, 40, "Спільний рядок кешу (atomic reader_count)\nІнвалідація L1/L2 через шину MESI!", fill="#fff3cd", stroke=WARN, tcol=INK, size=10)

    # Права частина: Per-CPU RWLock / Big Reader Lock (вирішення)
    f.append(rect(460, 75, 380, 245, fill="#fcfcfc", stroke=FIELD, sw=1.2, rx=8))
    f.append(text(650, 98, "Розподілений (Per-CPU) RWLock", size=13, color=FIELD, bold=True))

    boxlabel(f, 490, 120, 140, 35, "Ядро 0\nlocal_count_0++", fill="#d4edda", stroke=FIELD, size=10)
    boxlabel(f, 670, 120, 140, 35, "Ядро 1\nlocal_count_1++", fill="#d4edda", stroke=FIELD, size=10)
    boxlabel(f, 490, 180, 140, 35, "Ядро 2\nlocal_count_2++", fill="#d4edda", stroke=FIELD, size=10)
    boxlabel(f, 670, 180, 140, 35, "Ядро 3\nlocal_count_3++", fill="#d4edda", stroke=FIELD, size=10)

    boxlabel(f, 490, 245, 320, 40, "Читачі пишуть лише у свій локальний рядок!\nПисьменник підсумовує всі ядра (повільний write, миттєвий read)", fill="#e9f7ef", stroke=FIELD, tcol=INK, size=10)

    note(f, W / 2, 355, 800, [
        "На 32–128 ядрах звичайний RWLock втрачає швидкість через апаратні конфлікти кешу.",
        "Для систем із домінуванням читання застосовують розподілені Per-CPU замки або RCU."
    ], size=10)

    render(os.path.join(IMG, "cache-line-bouncing.svg"), W, H, *f)

if __name__ == "__main__":
    fig_rwlock_concept()
    fig_writer_starvation()
    fig_policies_timeline()
    fig_upgrade_deadlock()
    fig_rwlock_state_machine()
    fig_cache_line_bouncing()
    print("Згенеровано 6 фігур у ./img/")
