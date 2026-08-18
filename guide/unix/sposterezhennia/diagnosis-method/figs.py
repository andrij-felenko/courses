# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми «Метод діагностики: від симптому до причини».

Фігури:
1. use-method-framework.svg — Матриця та структура методології USE (Ресурси x Утилізація, Насичення, Помилки).
2. top-down-diagnostic-tree.svg — Ієрархічне дерево діагностики: від системного скринінгу до eBPF.
3. procfs-process-passport.svg — Карта неінвазивної діагностики процесу через вузли /proc/[pid]/.
"""

import os
import sys

# Підключаємо спільний модуль svgkit (4 рівні вгору до scripts/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


def fig_use_method():
    W, H = 1000, 540
    p = []

    # Заголовок та підзаголовок
    p.append(fitbox(200, 15, 600, 36, "Методологія USE: тріада перевірки апаратних та системних ресурсів",
                    size=15, fill=PALE, stroke=INK, sw=1.8, color=INK, bold=True))
    p.append(text(W / 2, 68, "Для кожного фізичного або віртуального ресурсу перевіряються три ортогональні виміри",
                  size=12, color=MUTED, italic=True))

    resources = [
        ("Процесор (CPU)", "Ядра, планувальник, черги runqueue"),
        ("Пам'ять (RAM)", "Фізичні сторінки, Swap, алокатори"),
        ("Дисковий I/O", "Блокові пристрої, NVMe/SATA, VFS"),
        ("Мережа (Network)", "Інтерфейси, черги qdisc, сокети"),
        ("Ресурси ядра", "Таблиця дескрипторів, futex, IPC")
    ]

    rx = 30
    rw = 230
    ry_start = 90
    rh = 68
    r_gap = 10

    p.append(fitbox(rx, ry_start - 24, rw, 22, "Системні ресурси",
                    size=12, fill="#e8edf3", stroke=LINE, sw=1.5, bold=True))

    for i, (title, desc) in enumerate(resources):
        cur_y = ry_start + i * (rh + r_gap)
        p.append(fitbox(rx, cur_y, rw, rh, f"{title}\n{desc}",
                        size=11, fill=PALE, stroke=LINE, sw=1.4))
        p.append(arrow(rx + rw, cur_y + rh / 2, rx + rw + 25, cur_y + rh / 2, color=LINE, sw=1.5))

    cols = [
        ("Utilization (Утилізація)",
         "Частка часу або місткості,\nпротягом якої ресурс зайнятий\nкорисною роботою\n\n"
         "Метрики:\n• %usr + %sys у mpstat\n• %util у iostat\n• Used RAM у free\n• Throughput (B/s)",
         GREENF, FIELD),
        ("Saturation (Насичення)",
         "Обсяг відкладеної роботи,\nяка стоїть у черзі через брак\nпропускної здатності\n\n"
         "Метрики:\n• runqueue (r) у vmstat\n• aqu-sz у iostat\n• si/so (свопінг)\n• PSI pressure (avg10)",
         "#fef9e7", "#d4ac0d"),
        ("Errors (Помилки)",
         "Кількість збоїв, відкинутих\nзапитів, ретрансмітів чи\nапаратних переривань\n\n"
         "Метрики:\n• majflt у pidstat\n• dropped/overruns у ip\n• I/O errors у dmesg\n• TCP retransmits",
         WARM, POS)
    ]

    cx_start = 295
    cw = 220
    c_gap = 12

    for j, (header, body_txt, fill_c, stroke_c) in enumerate(cols):
        cur_x = cx_start + j * (cw + c_gap)
        p.append(fitbox(cur_x, ry_start - 24, cw, 22, header.split()[0],
                        size=12, fill=fill_c, stroke=stroke_c, sw=1.5, bold=True))
        p.append(fitbox(cur_x, ry_start, cw, 250, f"{header}\n\n{body_txt}",
                        size=11, fill=fill_c, stroke=stroke_c, sw=1.5))

    panel_y = 360
    panel_w = 684
    p.append(rect(cx_start, panel_y, panel_w, 155, fill="#f8f9fa", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(cx_start + panel_w / 2, panel_y + 22, "Зіставлення з методом RED для прикладних сервісів", size=13, bold=True, color=INK))

    red_items = [
        ("Rate (Частота)", "Кількість запитів на секунду\n(RPS / QPS застосунку)", "#2980b9"),
        ("Errors (Помилки)", "Кількість невдалих відповідей\n(HTTP 5xx, failed RPC)", POS),
        ("Duration (Тривалість)", "Гістограма латентності відгуку\n(квантилі p50, p95, p99)", "#8e44ad")
    ]
    for k, (rtitle, rdesc, rcol) in enumerate(red_items):
        item_x = cx_start + 12 + k * 224
        p.append(fitbox(item_x, panel_y + 36, 212, 105, f"{rtitle}\n\n{rdesc}",
                        size=11, fill="#ffffff", stroke=rcol, sw=1.4))

    return render(os.path.join(OUT, "use-method-framework.svg"), W, H, *p)


def fig_diagnostic_tree():
    W, H = 1020, 540
    p = []

    p.append(fitbox(210, 14, 600, 36, "Низхідний маршрут локалізації проблеми (Top-Down Workflow)",
                    size=15, fill=PALE, stroke=INK, sw=1.8, color=INK, bold=True))
    p.append(text(W / 2, 66, "Від загального стану ОС до конкретного системного виклику або інструкції процесора",
                  size=12, color=MUTED, italic=True))

    stages = [
        ("1. Системний скринінг (System-Wide Triage)",
         "Мета: Визначити вузький ресурсний домен\n"
         "Інструменти: top, vmstat 1, iostat -xz 1, sar, PSI (/proc/pressure)\n"
         "Критерій: Сплеск черги r > nproc, блокування b > 0, %util > 90%, PSI avg10 > 10%",
         COOL, "#2980b9"),
        ("2. Ізоляція процесу (Process Introspection)",
         "Мета: Знайти винний PID та розібрати його паспорт\n"
         "Інструменти: pidstat -u -r -d -w, /proc/[pid]/{status,stat,wchan,stack,fd}\n"
         "Критерій: Співвідношення %usr/%sys, cswch проти nvcswch, функція wchan",
         GREENF, FIELD),
        ("3. Трасування межі з ядром (Boundary Tracing)",
         "Мета: Перехопити системні виклики та відкриті ресурси\n"
         "Інструменти: strace -c -T -p [PID], perf trace, lsof -p [PID], ss -tpie\n"
         "Критерій: Завислі syscalls (futex, read, epoll_wait), помилки ETIMEDOUT / EACCES",
         "#fef9e7", "#d4ac0d"),
        ("4. Глибоке профілювання (Deep Profiling & eBPF)",
         "Мета: Локалізувати гарячий стек або причину тривалого сну\n"
         "Інструменти: perf record (On-CPU), offcputime / bpftrace (Off-CPU), flamegraph\n"
         "Критерій: Вершина флеймграфа, точки перемикання контексту sched_switch",
         WARM, POS)
    ]

    bx = 50
    bw = 920
    bh = 86
    gap = 22
    start_y = 85

    for idx, (stitle, sbody, sfill, sstroke) in enumerate(stages):
        cur_y = start_y + idx * (bh + gap)
        
        # Бейдж зліва
        p.append(fitbox(bx, cur_y, 50, bh, f"L{idx+1}", size=15, fill=sstroke, stroke=sstroke, color="#ffffff", bold=True))
        # Основний блок
        p.append(fitbox(bx + 60, cur_y, bw - 60, bh, f"{stitle}\n{sbody}", size=11, fill=sfill, stroke=sstroke, sw=1.5))
        
        if idx < len(stages) - 1:
            arrow_x = bx + bw / 2
            arrow_y1 = cur_y + bh
            arrow_y2 = arrow_y1 + gap
            p.append(arrow(arrow_x, arrow_y1, arrow_x, arrow_y2, color=MUTED, sw=1.8))

    return render(os.path.join(OUT, "top-down-diagnostic-tree.svg"), W, H, *p)


def fig_procfs_passport():
    W, H = 1020, 540
    p = []

    p.append(fitbox(210, 14, 600, 36, "Паспорт процесу в /proc/[pid]/: неінвазивна діагностика без зупинки",
                    size=15, fill=PALE, stroke=INK, sw=1.8, color=INK, bold=True))
    p.append(text(W / 2, 66, "Зчитування структур ядра task_struct без накладних витрат ptrace",
                  size=12, color=MUTED, italic=True))

    cx, cy = W / 2, 115
    p.append(fitbox(cx - 130, cy - 22, 260, 44, "/proc/[pid]/\n(task_struct у пам'яті ядра)",
                    size=13, fill="#2c3e50", stroke=LINE, color="#ffffff", bold=True))

    cards = [
        ("/proc/[pid]/status",
         "Стан процесу та перемикання:\n• State: R (running), S (sleeping), D (disk wait)\n• Threads: кількість ниток у групі задач\n• voluntary_ctxt_switches: добровільний сон\n• nonvoluntary_ctxt_switches: витіснення CPU",
         50, 185, 280, 145, COOL, "#2980b9"),
        
        ("/proc/[pid]/wchan та stack",
         "Сплячий стек та канал ядра:\n• wchan: назва функції сну (futex_wait, epoll)\n• stack: повний стек ядра сплячого потоку\n  (дозволяє бачити точку очікування\n   без підключення GDB чи зупинки коду)",
         365, 185, 290, 145, WARM, POS),
        
        ("/proc/[pid]/stat",
         "Метрики часу та пам'яті:\n• utime / stime: тактів у user / system mode\n• minflt / majflt: незначні / значні збої RAM\n• priority / nice: пріоритети планувальника\n• vsize / rss: розміри пам'яті процесу",
         690, 185, 280, 145, GREENF, FIELD),
        
        ("/proc/[pid]/fd/ та fdinfo/",
         "Дескриптори та позиції:\n• fd/*: символьні посилання на відкриті файли/сокети\n• fdinfo/*: поточна позиція pos, прапорці flags,\n  події epoll та налаштування дескриптора",
         150, 360, 340, 145, "#fef9e7", "#d4ac0d"),
        
        ("/proc/[pid]/smaps_rollup",
         "Реальне використання пам'яті:\n• PSS (Proportional Set Size): чесна пам'ять\n• RssAnon / RssFile: анонімний vs файловий кеш\n• Referenced: сторінки, що реально читаються",
         530, 360, 340, 145, "#f4ecf7", "#8e44ad")
    ]

    for title, desc, bx, by, bw, bh, bfill, bstroke in cards:
        card_cx = bx + bw / 2
        card_cy = by
        p.append(arrow(cx, cy + 22, card_cx, card_cy, color=MUTED, sw=1.5))
        p.append(fitbox(bx, by, bw, bh, f"{title}\n\n{desc}",
                        size=11, fill=bfill, stroke=bstroke, sw=1.4))

    return render(os.path.join(OUT, "procfs-process-passport.svg"), W, H, *p)


def main():
    print("Генерація SVG-ілюстрацій для diagnosis-method...")
    fig_use_method()
    print("  + use-method-framework.svg")
    fig_diagnostic_tree()
    print("  + top-down-diagnostic-tree.svg")
    fig_procfs_passport()
    print("  + procfs-process-passport.svg")
    print("Готово.")


if __name__ == "__main__":
    main()
