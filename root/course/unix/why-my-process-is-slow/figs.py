# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


# ── 1. Декомпозиція астрономічного часу процесу ──────────────────────────────
def fig_latency_budget_decomposition():
    W, H = 1040, 580
    p = []

    # Корінь
    p.append(fitbox(280, 24, 480, 44, "Астрономічний час операції (Wall-Clock Time)",
                    size=14, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    # Дві основні гілки
    # Ліва гілка: On-CPU
    p.append(line(520, 68, 250, 110, color=LINE, sw=1.8))
    p.append(fitbox(70, 110, 360, 48, "On-CPU: задача на ядрі\n(виконує інструкції, стан TASK_RUNNING)",
                    size=12, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    p.append(line(250, 158, 150, 195, color=FIELD, sw=1.4))
    p.append(line(250, 158, 350, 195, color=FIELD, sw=1.4))

    p.append(fitbox(40, 195, 200, 100,
                    "User Time (%usr)\n\n"
                    "• Код застосунку\n"
                    "• Бібліотеки, парсинг\n"
                    "• Алгоритмічні цикли\n"
                    "• Промахи кеша L1/L3",
                    size=11, fill="#fff", stroke=FIELD, sw=1.4, color=INK))

    p.append(fitbox(260, 195, 200, 100,
                    "System Time (%sys)\n\n"
                    "• Системні виклики\n"
                    "• Менеджмент пам'яті\n"
                    "• Page faults (minflt)\n"
                    "• Обробка мережі/VFS",
                    size=11, fill="#fff", stroke=FIELD, sw=1.4, color=INK))

    # Права гілка: Off-CPU
    p.append(line(520, 68, 770, 110, color=LINE, sw=1.8))
    p.append(fitbox(590, 110, 360, 48, "Off-CPU: задача не на процесорі\n(чекає ядра або зовнішньої події)",
                    size=12, fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))

    p.append(line(770, 158, 550, 195, color=POS, sw=1.4))
    p.append(line(770, 158, 710, 195, color=POS, sw=1.4))
    p.append(line(770, 158, 870, 195, color=POS, sw=1.4))

    p.append(fitbox(480, 195, 150, 150,
                    "Черга планувальника\n(Runqueue Latency)\n\n"
                    "• Готова до роботи\n"
                    "• Але ядра зайняті\n"
                    "• Брак квантів часу\n"
                    "• Перевантаження CPU\n"
                    "• schedstat[1]",
                    size=10, fill="#fff", stroke=POS, sw=1.3, color=INK))

    p.append(fitbox(645, 195, 160, 150,
                    "Очікування I/O та пам'яті\n(TASK_UNINTERRUPTIBLE)\n\n"
                    "• Читання/запис диска\n"
                    "• Major page faults\n"
                    "• Очікування сокетів\n"
                    "• Буфери драйверів\n"
                    "• Свопінг сторінок",
                    size=10, fill="#fff", stroke=POS, sw=1.3, color=INK))

    p.append(fitbox(820, 195, 180, 150,
                    "Синхронізація й квоти\n(TASK_INTERRUPTIBLE)\n\n"
                    "• Блокування м'ютексів\n"
                    "• Очікування futex / каналів\n"
                    "• Замороження cgroups (cpu.max)\n"
                    "• sleep() / таймери\n"
                    "• Добровільні перемикання",
                    size=10, fill="#fff", stroke=POS, sw=1.3, color=INK))

    # Нижній синтез: зв'язок із метриками
    p.append(fitbox(40, 375, 960, 175,
                    "МАТРИЦЯ ДІАГНОСТИКИ СТАНІВ:\n\n"
                    "1. On-CPU (високий %CPU): діагностуємо профілювальником стека (perf record -g, perf top) або лічильником викликів (strace -c).\n"
                    "2. Runqueue Latency (%CPU низький, r у vmstat > кількості ядер): брак обчислювальної потужності або занижений пріоритет (pidstat -w, schedstat).\n"
                    "3. I/O Wait (задача в D, %iowait високий): затримка сховища, брак пропускної здатності диска чи мережі (iostat -xz 1, pidstat -d).\n"
                    "4. Sync / Locks / Sleep (задача в S, %CPU біля нуля): блокування всередині коду чи викликів сервісів (offcputime, pstack, perf sched).",
                    size=11, fill=COOL, stroke=NEG, sw=1.4, color=INK))

    render(os.path.join(OUT, "latency-budget-decomposition.svg"), W, H, *p,
           title="Декомпозиція часу виконання процесу")


# ── 2. Часова шкала та затримки планувальника ──────────────────────────────────
def fig_sched_queue_latency_timeline():
    W, H = 1060, 520
    p = []

    p.append(fitbox(40, 20, 980, 36, "Життєвий цикл операції на часовій шкалі ядра: де виникає затримка",
                    size=13, fill=PALE, stroke=LINE, sw=1.5, color=INK, bold=True))

    # Горизонтальна часова вісь
    y_axis = 140
    p.append(arrow(60, y_axis, 1010, y_axis, color=LINE, sw=2.2))
    p.append(text(1010, y_axis - 12, "Час (Wall-clock)", size=11, color=MUTED, anchor="end", bold=True))

    # Блоки станів уздовж осі
    # 1. Сон (очікування події)
    p.append(rect(80, 80, 140, 48, fill=PALE, stroke=MUTED, sw=1.3, rx=4))
    p.append(text(150, 108, "Off-CPU: Сон (S)\n(чекає сокета)", size=10, color=MUTED))

    # Подія 1: Wakeup
    p.append(circle(220, y_axis, 5, fill=POS, stroke=POS, sw=1.5))
    p.append(line(220, y_axis, 220, 195, color=POS, sw=1.2, dash="3 3"))
    p.append(text(220, 210, "Подія пробудження\n(пакет у сокеті)", size=10, color=POS, bold=True))

    # 2. Runqueue latency (чекає ядра)
    p.append(rect(220, 80, 180, 48, fill=WARM, stroke=POS, sw=1.8, rx=4))
    p.append(text(310, 102, "Затримка в черзі", size=11, color=POS, bold=True))
    p.append(text(310, 118, "(Runqueue Latency)", size=10, color=POS))

    # Подія 2: Context switch onto CPU
    p.append(circle(400, y_axis, 5, fill=FIELD, stroke=FIELD, sw=1.5))
    p.append(line(400, y_axis, 400, 195, color=FIELD, sw=1.2, dash="3 3"))
    p.append(text(400, 210, "Context switch:\nпочаток на ядрі", size=10, color=FIELD, bold=True))

    # 3. On-CPU: User mode
    p.append(rect(400, 80, 160, 48, fill=GREENF, stroke=FIELD, sw=1.8, rx=4))
    p.append(text(480, 102, "On-CPU: User (%usr)", size=11, color=FIELD, bold=True))
    p.append(text(480, 118, "Обробка запиту", size=10, color=FIELD))

    # Подія 3: Syscall read()
    p.append(circle(560, y_axis, 5, fill=NEG, stroke=NEG, sw=1.5))
    p.append(line(560, y_axis, 560, 195, color=NEG, sw=1.2, dash="3 3"))
    p.append(text(560, 210, "Системний виклик\n(read / fsync)", size=10, color=NEG, bold=True))

    # 4. On-CPU: System mode
    p.append(rect(560, 80, 140, 48, fill=COOL, stroke=NEG, sw=1.8, rx=4))
    p.append(text(630, 102, "On-CPU: System (%sys)", size=11, color=NEG, bold=True))
    p.append(text(630, 118, "VFS / драйвер", size=10, color=NEG))

    # Подія 4: Blocked on disk
    p.append(circle(700, y_axis, 5, fill=POS, stroke=POS, sw=1.5))
    p.append(line(700, y_axis, 700, 195, color=POS, sw=1.2, dash="3 3"))
    p.append(text(700, 210, "Добровільне перемикання\n(TASK_UNINTERRUPTIBLE)", size=10, color=POS, bold=True))

    # 5. Off-CPU: I/O wait
    p.append(rect(700, 80, 170, 48, fill=WARM, stroke=POS, sw=1.8, rx=4))
    p.append(text(785, 102, "Off-CPU: I/O Wait (D)", size=11, color=POS, bold=True))
    p.append(text(785, 118, "Очікування диска", size=10, color=POS))

    # Подія 5: DMA interrupt
    p.append(circle(870, y_axis, 5, fill=FIELD, stroke=FIELD, sw=1.5))
    p.append(line(870, y_axis, 870, 195, color=FIELD, sw=1.2, dash="3 3"))
    p.append(text(870, 210, "Переривання DMA:\nдані готові", size=10, color=FIELD, bold=True))

    # 6. Фінал On-CPU
    p.append(rect(870, 80, 110, 48, fill=GREENF, stroke=FIELD, sw=1.8, rx=4))
    p.append(text(925, 102, "On-CPU", size=11, color=FIELD, bold=True))
    p.append(text(925, 118, "Відповідь", size=10, color=FIELD))

    # Пояснювальний блок унизу
    p.append(fitbox(40, 260, 980, 230,
                    "КЛЮЧОВІ ВИСНОВКИ ДЛЯ АНАЛІЗУ ЗАТРИМОК:\n\n"
                    "• Загальний час операції = Час_на_CPU + Час_у_черзі + Час_очікування_I/O + Час_блокувань.\n"
                    "• Стандартні утиліти (top) показують лише On-CPU (%usr, %sys). Якщо операція триває 1000 мс, а CPU спожито лише 20 мс,\n"
                    "  98% затримки знаходиться в Off-CPU фазах, які звичайний CPU-профайлер взагалі не фіксує.\n"
                    "• Затримка в черзі (Runqueue Latency) — це симптом черги планувальника: задача повністю готова бігти, але процесор зайнятий.\n"
                    "• Добровільні перемикання (voluntary_ctxt_switches) свідчать про те, що задача сама поступилася процесором через I/O або м'ютекс.\n"
                    "• Примусові перемикання (nonvoluntary_ctxt_switches) показують, що задачу витіснив таймер ядра або важливіший процес.",
                    size=11, fill=SOFT, stroke=MUTED, sw=1.3, color=INK))

    render(os.path.join(OUT, "sched-queue-latency-timeline.svg"), W, H, *p,
           title="Шкала виконання задачі та місця виникнення затримок")


# ── 3. Дерево систематичної діагностики ────────────────────────────────────────
def fig_diagnostic_tree():
    W, H = 1080, 620
    p = []

    p.append(fitbox(340, 20, 400, 44, "Симптом: процес виконує операцію занадто довго",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    # Розгалуження на 2 головні гілки: CPU високий vs CPU низький
    p.append(line(540, 64, 270, 100, color=LINE, sw=1.8))
    p.append(line(540, 64, 810, 100, color=LINE, sw=1.8))

    # Ліва гілка: CPU високий
    p.append(fitbox(90, 100, 360, 44, "Високий %CPU (CPU-bound вузьке місце)",
                    size=12, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    p.append(line(270, 144, 170, 175, color=FIELD, sw=1.4))
    p.append(line(270, 144, 370, 175, color=FIELD, sw=1.4))

    p.append(fitbox(40, 175, 200, 160,
                    "%usr переважає\n\n"
                    "Причина:\n"
                    "• Неефективний алгоритм\n"
                    "• Гарячі математичні цикли\n"
                    "• Парсинг / десеріалізація\n"
                    "• Промахи L3 кеша\n\n"
                    "Інструменти:\n"
                    "perf top, perf record -g",
                    size=10, fill="#fff", stroke=FIELD, sw=1.3, color=INK))

    p.append(fitbox(260, 175, 200, 160,
                    "%sys переважає\n\n"
                    "Причина:\n"
                    "• Занадто часті системні виклики\n"
                    "• Помилки сторінок (minflt)\n"
                    "• Копіювання буферів сокетів\n"
                    "• Втрати на перемиканні задач\n\n"
                    "Інструменти:\n"
                    "strace -c, perf trace",
                    size=10, fill="#fff", stroke=FIELD, sw=1.3, color=INK))

    # Права гілка: CPU низький (Off-CPU)
    p.append(fitbox(630, 100, 360, 44, "Низький %CPU (Off-CPU вузьке місце)",
                    size=12, fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))

    p.append(line(810, 144, 580, 175, color=POS, sw=1.4))
    p.append(line(810, 144, 760, 175, color=POS, sw=1.4))
    p.append(line(810, 144, 940, 175, color=POS, sw=1.4))

    p.append(fitbox(490, 175, 170, 160,
                    "Черга планувальника\n(r у vmstat > ядер)\n\n"
                    "Причина:\n"
                    "• Конкуренція за ядра\n"
                    "• Низький nice / пріоритет\n"
                    "• Ліміт cgroups (cpu.max)\n\n"
                    "Інструменти:\n"
                    "pidstat -w, /proc/pressure",
                    size=10, fill="#fff", stroke=POS, sw=1.3, color=INK))

    p.append(fitbox(675, 175, 170, 160,
                    "I/O Wait\n(стан D, %wa високий)\n\n"
                    "Причина:\n"
                    "• Повільний диск / SSD\n"
                    "• Major page faults (диск)\n"
                    "• Своп через брак пам'яті\n\n"
                    "Інструменти:\n"
                    "iostat -xz 1, pidstat -d",
                    size=10, fill="#fff", stroke=POS, sw=1.3, color=INK))

    p.append(fitbox(860, 175, 180, 160,
                    "Блокування / Сон\n(стан S, CPU = 0%)\n\n"
                    "Причина:\n"
                    "• Конфлікти м'ютексів / futex\n"
                    "• Очікування мережевої відповіді\n"
                    "• sleep() / таймери пулу\n\n"
                    "Інструменти:\n"
                    "offcputime, pstack, gdb",
                    size=10, fill="#fff", stroke=POS, sw=1.3, color=INK))

    # Нижній синтез: правила перевірки
    p.append(fitbox(40, 365, 1000, 225,
                    "ПРАКТИЧНИЙ АЛГОРИТМ ПОШУКУ ПРИЧИНИ ГАЛЬМУВАННЯ:\n\n"
                    "Крок 1. Загальний стан системи: `vmstat 1` → дивимося на стовпчики `r` (черга задач), `b` (заблоковані на I/O), `us`, `sy`, `wa`.\n"
                    "Крок 2. Звуження до процесу: `pidstat -u -r -d -w -p <PID> 1` → вимірюємо %usr, %system, minflt/s, majflt/s, kB_rd/s, cswch/s.\n"
                    "Крок 3. Перевірка затримки ядра: читаємо `/proc/<PID>/schedstat` та `/proc/pressure/cpu` → чи не простоює задача в черзі планувальника.\n"
                    "Крок 4. Якщо On-CPU переважає: будуємо флеймграф за допомогою `perf record -F 99 -g -p <PID> -- sleep 10` → локалізуємо повільну функцію.\n"
                    "Крок 5. Якщо Off-CPU переважає: запускаємо `offcputime-bpfcc -p <PID> 10` або `perf sched record` → знаходимо стек виклику, де задача засинає.",
                    size=11, fill=COOL, stroke=NEG, sw=1.4, color=INK))

    render(os.path.join(OUT, "diagnostic-tree.svg"), W, H, *p,
           title="Дерево діагностики затримок процесу")


if __name__ == "__main__":
    fig_latency_budget_decomposition()
    fig_sched_queue_latency_timeline()
    fig_diagnostic_tree()
    print("Фігури успішно згенеровано в img/")
