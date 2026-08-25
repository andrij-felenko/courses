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


# ── 1. Трикутник системних ресурсів ──────────────────────────────────────────
def fig_resource_triangle():
    W, H = 1040, 580
    p = []

    # Заголовок
    p.append(fitbox(270, 20, 500, 42, "Трикутник локалізації навантаження: CPU, Ядро та Очікування",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    # Вершина 1 (Ліворуч угорі): CPU-bound (User Space)
    p.append(fitbox(40, 90, 290, 240,
                    "1. ПРОЦЕСОР: User Space (%usr)\n\n"
                    "Симптоми:\n"
                    "• 100% завантаження ядра процесора\n"
                    "• Стан процесу R (Running)\n"
                    "• Мінімальні добровільні перемикання\n\n"
                    "Типові першопричини:\n"
                    "• Неефективні алгоритми O(N²)\n"
                    "• Нескінченні або щільні обчислювальні цикли\n"
                    "• Парсинг JSON / серіалізація даних\n"
                    "• Промахи кешів L1/L2/L3 (низький IPC)\n\n"
                    "Ключові інструменти:\n"
                    "perf top -p <PID>, perf record -g",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.8, color=INK))

    # Вершина 2 (Праворуч угорі): Kernel-bound (System Time)
    p.append(fitbox(710, 90, 290, 240,
                    "2. ЯДРО: System Space (%sys)\n\n"
                    "Симптоми:\n"
                    "• Високий %sys (> 30–50% CPU)\n"
                    "• Шторм перемикань контексту\n"
                    "• Зростання системних викликів\n\n"
                    "Типові першопричини:\n"
                    "• Небуферизований I/O (write по 1 байту)\n"
                    "• Конфлікти синхронізації (futex lock)\n"
                    "• Шторм сторінкових збоїв (minflt)\n"
                    "• Часті алокації та ремапінг (mmap/brk)\n\n"
                    "Ключові інструменти:\n"
                    "strace -c -p <PID>, pidstat -w -p <PID>",
                    size=11, fill=COOL, stroke=NEG, sw=1.8, color=INK))

    # Вершина 3 (Центр унизу): I/O & Wait-bound (Очікування)
    p.append(fitbox(375, 300, 290, 240,
                    "3. ОЧІКУВАННЯ: I/O та блокування\n\n"
                    "Симптоми:\n"
                    "• %CPU низький або високий %wa (iowait)\n"
                    "• Стан процесу D (Uninterruptible Sleep)\n"
                    "• Або стан S (Interruptible Sleep)\n\n"
                    "Типові першопричини:\n"
                    "• Синхронні дискові операції (fsync / O_SYNC)\n"
                    "• Перевантаження черги диска (await >> 5 мс)\n"
                    "• Блокуючі читання із порожніх сокетів\n"
                    "• Major page faults (підкачка з диска)\n\n"
                    "Ключові інструменти:\n"
                    "vmstat 1, iostat -xz 1, pidstat -d",
                    size=11, fill=WARM, stroke=POS, sw=1.8, color=INK))

    # З'єднувальні лінії трикутника
    p.append(line(330, 210, 710, 210, color=LINE, sw=1.6, dash="4 4"))
    p.append(line(240, 330, 375, 380, color=LINE, sw=1.6, dash="4 4"))
    p.append(line(800, 330, 665, 380, color=LINE, sw=1.6, dash="4 4"))

    # Центральний маркер
    p.append(textbox(520, 190, "Головне діагностичне запитання:\nДЕ ЗГОРАЄ ЧАС ВІДГУКУ?",
                     size=12, fill="#ffffff", stroke=INK, sw=1.5, bold=True)[0])

    render(os.path.join(OUT, "resource-triangle.svg"), W, H, *p,
           title="Трикутник системних ресурсів: CPU, Ядро та Очікування")


# ── 2. Ієрархія експрес-діагностики Top-Down ─────────────────────────────────
def fig_top_down_diagnostic_flow():
    W, H = 1060, 560
    p = []

    p.append(fitbox(280, 20, 500, 40, "Методологія Top-Down: звуження пошуку від системи до коду",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    # Рівень 1: Система (vmstat / iostat)
    p.append(fitbox(60, 85, 940, 85,
                    "РІВЕНЬ 1: Загальний стан операційної системи (System-Wide Overview)\n"
                    "Команди: vmstat 1  |  iostat -xz 1  |  cat /proc/loadavg\n"
                    "Що перевіряємо: співвідношення us/sy/wa/id, довжину черги готових задач (r), кількість заблокованих (b), насичення дисків (%util, await).",
                    size=11, fill=PALE, stroke=LINE, sw=1.5, color=INK))

    p.append(arrow(530, 170, 530, 195, color=LINE, sw=2.0))

    # Рівень 2: Конкретний процес (pidstat)
    p.append(fitbox(60, 195, 940, 85,
                    "РІВЕНЬ 2: Локалізація навантаження процесу (Process-Level Breakdown)\n"
                    "Команди: pidstat -u -d -w -r 1 -p <PID>\n"
                    "Що перевіряємо: %usr vs %system, дисковий I/O (kB_rd/s, kB_wr/s), сторінкові збої (minflt, majflt), перемикання контексту (cswch/s, nvcswch/s).",
                    size=11, fill=COOL, stroke=NEG, sw=1.5, color=INK))

    p.append(arrow(530, 280, 530, 305, color=LINE, sw=2.0))

    # Рівень 3: Межа простору ядра (strace -c)
    p.append(fitbox(60, 305, 940, 85,
                    "РІВЕНЬ 3: Інспекція системних викликів (Syscall Boundary Inspection)\n"
                    "Команди: strace -c -p <PID>  |  strace -T -e trace=write,futex,read -p <PID>\n"
                    "Що перевіряємо: сумарний час у системних викликах, шторми 1-байтних операцій, зависання на futex_wait, epoll_wait, nanosleep чи fsync.",
                    size=11, fill=WARM, stroke=POS, sw=1.5, color=INK))

    p.append(arrow(530, 390, 530, 415, color=LINE, sw=2.0))

    # Рівень 4: Інструкції та стеки (perf top)
    p.append(fitbox(60, 415, 940, 95,
                    "РІВЕНЬ 4: Профілювання гарячих функцій коду (CPU Sampling & Hotspots)\n"
                    "Команди: perf top -p <PID>  |  perf record -F 99 -g -p <PID> -- sleep 10  |  perf report\n"
                    "Що перевіряємо: точні адреси та імена функцій у коді застосунку або бібліотеках, які споживають більшість процесорних тактів.",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.8, color=INK))

    render(os.path.join(OUT, "top-down-diagnostic-flow.svg"), W, H, *p,
           title="Ієрархія експрес-діагностики: від системи до інструкцій")


# ── 3. Механіка системного виклику: шторм vs буферизація ─────────────────────
def fig_syscall_storm_vs_buffered_io():
    W, H = 1040, 540
    p = []

    p.append(fitbox(260, 20, 520, 40, "Шторм системних викликів проти буферизованого виведення",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    # Ліва половина: Небуферизований шторм (1 байт)
    p.append(fitbox(40, 80, 460, 420,
                    "НЕБУФЕРИЗОВАНИЙ I/O: 1 МБ по 1 байту\n"
                    "(1 000 000 системних викликів write)\n\n"
                    "Простір користувача (Ring 3):\n"
                    "write(fd, &byte, 1)  × 1 000 000 разів\n\n"
                    "Ціна кожного виклику:\n"
                    "• Інструкція `syscall` (перемикання CPU в Ring 0)\n"
                    "• Збереження регістрів у стек ядра (pt_regs)\n"
                    "• Перемикання таблиць сторінок MMU (KPTI)\n"
                    "• Прохід через VFS, перевірка прав і дескриптора\n"
                    "• Блокування inode / файлового блоку\n"
                    "• Повернення в Ring 3 (`sysret`)\n\n"
                    "НАСЛІДОК ДЛЯ СИСТЕМИ:\n"
                    "• %sys підскакує до 85–95%\n"
                    "• Процесор витрачає такти на службові переходи\n"
                    "• Час виконання операції: 450–700 мс\n"
                    "• Продуктивність падає у 50–100 разів!",
                    size=11, fill=WARM, stroke=POS, sw=1.8, color=INK))

    # Права половина: Буферизований вивід (64 КіБ)
    p.append(fitbox(540, 80, 460, 420,
                    "БУФЕРИЗОВАНИЙ I/O: 1 МБ блоками по 64 КіБ\n"
                    "(лише 16 системних викликів write)\n\n"
                    "Простір користувача (Ring 3):\n"
                    "Буфер у пам'яті накопичує дані швидко і дешево.\n"
                    "write(fd, buf, 65536)  × 16 разів\n\n"
                    "Ефективність виконання:\n"
                    "• Лише 16 переходів між Ring 3 та Ring 0\n"
                    "• Нульові накладні витрати на перемикання контексту\n"
                    "• Ядро копіює дані суцільним вектором у Page Cache\n"
                    "• Конвеєр процесора працює без зупинок\n\n"
                    "НАСЛІДОК ДЛЯ СИСТЕМИ:\n"
                    "• %sys становить менше 1%\n"
                    "• Процесор вільний для корисної роботи\n"
                    "• Час виконання операції: 2–4 мс\n"
                    "• Максимальна пропускна здатність шини пам'яті!",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.8, color=INK))

    render(os.path.join(OUT, "syscall-storm-vs-buffered-io.svg"), W, H, *p,
           title="Порівняння небуферизованого шторму системних викликів та буферизованого виведення")


if __name__ == "__main__":
    fig_resource_triangle()
    fig_top_down_diagnostic_flow()
    fig_syscall_storm_vs_buffered_io()
    print("Усі 3 фігури успішно згенеровано в img/")
