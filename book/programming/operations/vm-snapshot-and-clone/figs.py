# -*- coding: utf-8 -*-
import sys, os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Анатомія стану ВМ та рівні узгодженості знімків ──────────────────
def fig_vm_snapshot_components():
    W, H = 960, 480
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Заголовок
    p.append(text(W / 2, 38, "Анатомія стану віртуальної машини та рівні збереження знімка", size=16, color="#0f172a", bold=True))
    
    # Ліва частина: Три складові стану віртуальної машини
    box_w = 420.0
    p.append(rect(30, 60, box_w, 390, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(30 + box_w / 2, 85, "Повний стан запущеної ВМ (Runtime State)", size=13, color="#1e293b", bold=True))
    
    # 1. vCPU & Device State
    p.append(rect(45, 105, box_w - 30, 85, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=4))
    p.append(text(45 + (box_w - 30) / 2, 125, "1. Стан віртуальних процесорів та пристроїв", size=12, color="#1d4ed8", bold=True))
    p.append(mtext(45 + (box_w - 30) / 2, 145, [
        "Регістри vCPU: RIP, RSP, CR0/CR3/CR4, MSR, EFLAGS",
        "Стан емульованих пристроїв: vAPIC, virtio-кільця, таймери TSC"
    ], size=10, color="#1e40af", lh=1.3))
    
    # 2. RAM State
    p.append(rect(45, 205, box_w - 30, 95, fill="#fef2f2", stroke="#ef4444", sw=1.2, rx=4))
    p.append(text(45 + (box_w - 30) / 2, 225, "2. Оперативна пам'ять гостя (Guest RAM)", size=12, color="#b91c1c", bold=True))
    p.append(mtext(45 + (box_w - 30) / 2, 245, [
        "Сторінки фізичної пам'яті гостя (GPA) в адресному просторі хоста",
        "Брудні кеші сторінок ОС (Page Cache), буфери транзакцій СУБД",
        "Активні TCP-з'єднання, стеки потоків виконання, змінні ядра"
    ], size=10, color="#991b1b", lh=1.3))
    
    # 3. Disk Storage State
    p.append(rect(45, 315, box_w - 30, 115, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=4))
    p.append(text(45 + (box_w - 30) / 2, 335, "3. Блокове сховище (Virtual Disk Image)", size=12, color="#15803d", bold=True))
    p.append(mtext(45 + (box_w - 30) / 2, 355, [
        "Фіксовані сектори/кластери віртуального диска (LBA)",
        "Журнал файлової системи (ext4 jbd2 / XFS log / NTFS journal)",
        "Незмінні дані, записані на постійний носій до моменту знімка"
    ], size=10, color="#166534", lh=1.3))
    
    # Права частина: Три рівні узгодженості знімків
    rx = 480.0
    rw = 450.0
    p.append(rect(rx, 60, rw, 390, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(rx + rw / 2, 85, "Рівні узгодженості та збереження (Snapshot Levels)", size=13, color="#1e293b", bold=True))
    
    # Рівень А: Crash-consistent
    p.append(rect(rx + 15, 105, rw - 30, 95, fill="#fff7ed", stroke="#f97316", sw=1.2, rx=4))
    p.append(text(rx + (rw - 30) / 2 + 15, 125, "А. Краш-узгоджений знімок диска (Crash-Consistent)", size=11, color="#c2410c", bold=True))
    p.append(mtext(rx + (rw - 30) / 2 + 15, 145, [
        "• Фіксує виключно стан диска (Блок 3); пам'ять і vCPU ігноруються.",
        "• Аналог раптового вимкнення живлення сервера з розетки.",
        "• Потребує відтворення журналу файлової системи (Journal Replay)."
    ], size=10, color="#9a3412", lh=1.3))
    
    # Рівень Б: FS / App-consistent (Quiesced)
    p.append(rect(rx + 15, 215, rw - 30, 105, fill="#f0fdf4", stroke="#16a34a", sw=1.2, rx=4))
    p.append(text(rx + (rw - 30) / 2 + 15, 235, "Б. Узгоджений із гостем знімок (Quiesced / FS-Consistent)", size=11, color="#15803d", bold=True))
    p.append(mtext(rx + (rw - 30) / 2 + 15, 255, [
        "• QEMU Guest Agent / VSS тимчасово заморожує I/O (FIFREEZE ioctl).",
        "• Брудні системні буфери та кеші скидаються на диск перед знімком.",
        "• Суперблок чистий; гарантується цілісність файлових систем і БД."
    ], size=10, color="#166534", lh=1.3))
    
    # Рівень В: Live Snapshot with RAM
    p.append(rect(rx + 15, 335, rw - 30, 100, fill="#fdf4ff", stroke="#c026d3", sw=1.2, rx=4))
    p.append(text(rx + (rw - 30) / 2 + 15, 355, "В. Живий знімок із пам'яттю (Live Memory Snapshot)", size=11, color="#86198f", bold=True))
    p.append(mtext(rx + (rw - 30) / 2 + 15, 375, [
        "• Зберігає всі три складові: vCPU (1) + RAM (2) + Диск (3).",
        "• Відновлення повертає ВМ у точну мілісекунду роботи без перезавантаження.",
        "• Зберігаються всі активні сокети, дескриптори та процеси в пам'яті."
    ], size=10, color="#701a75", lh=1.3))
    
    render(os.path.join(OUT, "vm-snapshot-components.svg"), W, H, *p)


# ── Фіг. 2: Порівняння механік Copy-on-Write та Redirect-on-Write ────────────
def fig_cow_vs_row():
    W, H = 960, 430
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Порівняння блокових механік: Copy-on-Write проти Redirect-on-Write", size=16, color="#0f172a", bold=True))
    
    col_w = 430.0
    col_h = 345.0
    
    # Ліва колонка: Класичний Copy-on-Write (In-Place + Delta Store)
    x1 = 35.0
    y1 = 60.0
    p.append(rect(x1, y1, col_w, col_h, fill="#fef2f2", stroke="#fca5a5", sw=1.4, rx=6))
    p.append(text(x1 + col_w / 2, y1 + 25, "Класичний Copy-on-Write (LVM / Сховища)", size=13, color="#991b1b", bold=True))
    
    p.append(rect(x1 + 15, y1 + 45, col_w - 30, 48, fill="#ffffff", stroke="#ef4444", sw=1.2, rx=4))
    p.append(mtext(x1 + col_w / 2, y1 + 62, [
        "Запит: Запис нових даних у блок #4 основного тому",
        "Штраф першого запису: 1 читання + 2 записи (I/O Amplication = 3)"
    ], size=10, color="#7f1d1d", lh=1.2, bold=False))
    
    # Схема CoW кроків
    # Крок 1: Читання старого блоку
    p.append(rect(x1 + 25, y1 + 105, 110, 50, fill="#fee2e2", stroke="#ef4444", sw=1.0, rx=4))
    p.append(mtext(x1 + 80, y1 + 125, ["1. Читання", "Блок #4 (старий)"], size=10, color="#991b1b", lh=1.2))
    p.append(arrow(x1 + 140, y1 + 130, x1 + 180, y1 + 130, color="#ef4444", sw=1.5))
    
    # Крок 2: Запис старого блоку в дельта-сховище
    p.append(rect(x1 + 185, y1 + 105, 110, 50, fill="#fee2e2", stroke="#ef4444", sw=1.0, rx=4))
    p.append(mtext(x1 + 240, y1 + 125, ["2. Запис у знімок", "Дельта-пул #4"], size=10, color="#991b1b", lh=1.2))
    p.append(arrow(x1 + 300, y1 + 130, x1 + 340, y1 + 130, color="#ef4444", sw=1.5))
    
    # Крок 3: Перезапис на місці
    p.append(rect(x1 + 345, y1 + 105, 70, 50, fill="#fee2e2", stroke="#ef4444", sw=1.0, rx=4))
    p.append(mtext(x1 + 380, y1 + 125, ["3. Запис", "Блок #4"], size=10, color="#991b1b", lh=1.2))
    
    # Нижні томи CoW
    p.append(rect(x1 + 25, y1 + 180, 175, 140, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(x1 + 112, y1 + 200, "Основний том (Live Volume)", size=11, color="#334155", bold=True))
    p.append(rect(x1 + 35, y1 + 215, 155, 25, fill="#e2e8f0", stroke="#cbd5e1", sw=1.0, rx=2))
    p.append(text(x1 + 112, y1 + 232, "Блок 1 (незмінний)", size=10, color="#475569"))
    p.append(rect(x1 + 35, y1 + 245, 155, 25, fill="#fca5a5", stroke="#ef4444", sw=1.2, rx=2))
    p.append(text(x1 + 112, y1 + 262, "Блок 4 (новий вміст D')", size=10, color="#991b1b", bold=True))
    p.append(rect(x1 + 35, y1 + 275, 155, 25, fill="#e2e8f0", stroke="#cbd5e1", sw=1.0, rx=2))
    p.append(text(x1 + 112, y1 + 292, "Блок 8 (незмінний)", size=10, color="#475569"))
    
    p.append(rect(x1 + 225, y1 + 180, 185, 140, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(x1 + 317, y1 + 200, "Дельта-пул знімка (Snap Delta)", size=11, color="#334155", bold=True))
    p.append(rect(x1 + 235, y1 + 215, 165, 25, fill="#fed7aa", stroke="#f97316", sw=1.2, rx=2))
    p.append(text(x1 + 317, y1 + 232, "Блок 4 (витіснений старий D)", size=10, color="#9a3412", bold=True))
    p.append(rect(x1 + 235, y1 + 245, 165, 55, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=2))
    p.append(mtext(x1 + 317, y1 + 270, ["Вільний простір дельти", "(заповнюється при записах)"], size=9, color="#64748b", lh=1.2))

    # Права колонка: Redirect-on-Write / QCOW2 Overlay
    x2 = 495.0
    y2 = 60.0
    p.append(rect(x2, y2, col_w, col_h, fill="#f0fdf4", stroke="#86efac", sw=1.4, rx=6))
    p.append(text(x2 + col_w / 2, y2 + 25, "Redirect-on-Write (QCOW2 / VHDX / Overlay)", size=13, color="#166534", bold=True))
    
    p.append(rect(x2 + 15, y2 + 45, col_w - 30, 48, fill="#ffffff", stroke="#22c55e", sw=1.2, rx=4))
    p.append(mtext(x2 + col_w / 2, y2 + 62, [
        "Запит: Запис нових даних у блок #4",
        "Штраф першого запису: 1 прямий запис + оновлення покажчика L2"
    ], size=10, color="#14532d", lh=1.2, bold=False))
    
    # Схема RoW кроків
    p.append(rect(x2 + 25, y2 + 105, 175, 50, fill="#dcfce7", stroke="#22c55e", sw=1.0, rx=4))
    p.append(mtext(x2 + 112, y2 + 125, ["1. Прямий запис у дельту", "Новий кластер #4 (D')"], size=10, color="#15803d", lh=1.2))
    p.append(arrow(x2 + 205, y2 + 130, x2 + 235, y2 + 130, color="#22c55e", sw=1.5))
    
    p.append(rect(x2 + 240, y2 + 105, 165, 50, fill="#dcfce7", stroke="#22c55e", sw=1.0, rx=4))
    p.append(mtext(x2 + 322, y2 + 125, ["2. Оновлення метаданих", "L2 Table: #4 -> Delta Offset"], size=10, color="#15803d", lh=1.2))
    
    # Нижні томи RoW
    p.append(rect(x2 + 25, y2 + 180, 175, 140, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(x2 + 112, y2 + 200, "Базовий образ (Read-Only)", size=11, color="#334155", bold=True))
    p.append(rect(x2 + 35, y2 + 215, 155, 25, fill="#e2e8f0", stroke="#cbd5e1", sw=1.0, rx=2))
    p.append(text(x2 + 112, y2 + 232, "Блок 1 (незмінний)", size=10, color="#475569"))
    p.append(rect(x2 + 35, y2 + 245, 155, 25, fill="#e2e8f0", stroke="#cbd5e1", sw=1.0, rx=2))
    p.append(text(x2 + 112, y2 + 262, "Блок 4 (оригінальний D)", size=10, color="#475569"))
    p.append(rect(x2 + 35, y2 + 275, 155, 25, fill="#e2e8f0", stroke="#cbd5e1", sw=1.0, rx=2))
    p.append(text(x2 + 112, y2 + 292, "Блок 8 (незмінний)", size=10, color="#475569"))
    
    p.append(rect(x2 + 225, y2 + 180, 185, 140, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(x2 + 317, y2 + 200, "Активний оверлей (Read-Write)", size=11, color="#334155", bold=True))
    p.append(rect(x2 + 235, y2 + 215, 165, 25, fill="#bbf7d0", stroke="#16a34a", sw=1.2, rx=2))
    p.append(text(x2 + 317, y2 + 232, "Блок 4 (модифікований D')", size=10, color="#166534", bold=True))
    p.append(rect(x2 + 235, y2 + 245, 165, 55, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=2))
    p.append(mtext(x2 + 317, y2 + 270, ["Незадіяні блоки відсилають", "до базового образу"], size=9, color="#64748b", lh=1.2))

    render(os.path.join(OUT, "cow-vs-row-block-allocation.svg"), W, H, *p)


# ── Фіг. 3: Розв'язання читання вздовж ланцюжка шарів (Backing Chain) ─────────
def fig_backing_chain():
    W, H = 960, 420
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Ієрархія шарів знімків: каскадний пошук блоків (Backing Chain Traversal)", size=16, color="#0f172a", bold=True))
    
    # 4 Шари дисків зліва направо
    layers = [
        ("Активний оверлей", "active.qcow2 (R/W)", "#dcfce7", "#16a34a", [
            ("Кластер 0", "D0'' (найновіший)", True),
            ("Кластер 1", "не виділено (пропуск)", False),
            ("Кластер 2", "не виділено (пропуск)", False),
            ("Кластер 3", "D3' (модифікований)", True)
        ]),
        ("Знімок 2 (Snapshot 2)", "snap2.qcow2 (R/O)", "#eff6ff", "#3b82f6", [
            ("Кластер 0", "D0' (стара версія)", False),
            ("Кластер 1", "D1' (модифікований)", True),
            ("Кластер 2", "не виділено (пропуск)", False),
            ("Кластер 3", "не виділено (пропуск)", False)
        ]),
        ("Знімок 1 (Snapshot 1)", "snap1.qcow2 (R/O)", "#fdf4ff", "#a855f7", [
            ("Кластер 0", "не виділено (пропуск)", False),
            ("Кластер 1", "не виділено (пропуск)", False),
            ("Кластер 2", "D2' (модифікований)", True),
            ("Кластер 3", "не виділено (пропуск)", False)
        ]),
        ("Базовий образ (Base)", "base.qcow2 (R/O)", "#f1f5f9", "#64748b", [
            ("Кластер 0", "D0 (початковий)", False),
            ("Кластер 1", "D1 (початковий)", False),
            ("Кластер 2", "D2 (початковий)", False),
            ("Кластер 3", "D3 (початковий)", False)
        ])
    ]
    
    x_start = 35.0
    w_box = 200.0
    gap = 25.0
    
    for i, (title, filename, fill_c, stroke_c, clusters) in enumerate(layers):
        x = x_start + i * (w_box + gap)
        y = 65.0
        
        # Рамка шару
        p.append(rect(x, y, w_box, 330, fill=fill_c, stroke=stroke_c, sw=1.4, rx=6))
        p.append(text(x + w_box / 2, y + 24, title, size=12, color="#0f172a", bold=True))
        p.append(text(x + w_box / 2, y + 42, filename, size=10, color="#475569", italic=True))
        
        # Кластери
        cy = y + 55.0
        for cname, cval, is_hit in clusters:
            bg_c = "#ffffff" if not is_hit else "#fef08a"
            border_c = "#cbd5e1" if not is_hit else "#ca8a04"
            p.append(rect(x + 10, cy, w_box - 20, 52, fill=bg_c, stroke=border_c, sw=1.2, rx=4))
            p.append(text(x + 20, cy + 20, cname, size=11, color="#1e293b", bold=True, anchor="start"))
            p.append(text(x + 20, cy + 38, cval, size=10, color="#334155" if not is_hit else "#854d0e", anchor="start"))
            cy += 65.0
            
        # Стрілка backing_file до наступного шару
        if i < len(layers) - 1:
            arr_x1 = x + w_box
            arr_x2 = arr_x1 + gap
            p.append(arrow(arr_x1, y + 165, arr_x2, y + 165, color="#64748b", sw=1.5))
            p.append(text(arr_x1 + gap / 2, y + 155, "backing", size=9, color="#64748b"))

    render(os.path.join(OUT, "backing-file-chain-traversal.svg"), W, H, *p)


# ── Фіг. 4: Зв'язані клони проти повних клонів ─────────────────────────────────
def fig_linked_vs_full_clone():
    W, H = 960, 440
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Порівняння архітектури клонування: зв'язані клони проти повних", size=16, color="#0f172a", bold=True))
    
    col_w = 430.0
    col_h = 360.0
    
    # Ліва колонка: Зв'язані клони (Linked Clones)
    x1 = 35.0
    y1 = 60.0
    p.append(rect(x1, y1, col_w, col_h, fill="#eff6ff", stroke="#93c5fd", sw=1.4, rx=6))
    p.append(text(x1 + col_w / 2, y1 + 25, "Зв'язані клони (Linked Clones / Thin Provisioning)", size=13, color="#1e40af", bold=True))
    
    # Спільний золотий образ
    p.append(rect(x1 + 100, y1 + 45, col_w - 200, 60, fill="#fef08a", stroke="#ca8a04", sw=1.4, rx=6))
    p.append(text(x1 + col_w / 2, y1 + 70, "Золотий еталонний образ", size=11, color="#854d0e", bold=True))
    p.append(text(x1 + col_w / 2, y1 + 90, "Base-Golden.qcow2 (Read-Only 50 ГБ)", size=10, color="#a16207"))
    
    # Стрілки від бази до 3 клонів
    p.append(arrow(x1 + 140, y1 + 105, x1 + 75, y1 + 155, color="#3b82f6", sw=1.5))
    p.append(arrow(x1 + col_w / 2, y1 + 105, x1 + col_w / 2, y1 + 155, color="#3b82f6", sw=1.5))
    p.append(arrow(x1 + col_w - 140, y1 + 105, x1 + col_w - 75, y1 + 155, color="#3b82f6", sw=1.5))
    
    # 3 Оверлеї клонів
    for idx, cx in enumerate([x1 + 20, x1 + 155, x1 + 290]):
        p.append(rect(cx, y1 + 160, 120, 110, fill="#ffffff", stroke="#3b82f6", sw=1.2, rx=4))
        p.append(text(cx + 60, y1 + 182, "Клон #%d" % (idx + 1), size=11, color="#1d4ed8", bold=True))
        p.append(text(cx + 60, y1 + 202, "delta-%d.qcow2" % (idx + 1), size=9, color="#64748b", italic=True))
        p.append(rect(cx + 10, y1 + 215, 100, 40, fill="#dbeafe", stroke="#93c5fd", sw=1.0, rx=2))
        p.append(mtext(cx + 60, y1 + 232, ["Тільки дельта", "1.2 ГБ змін"], size=9, color="#1e40af", lh=1.2))
        
    p.append(rect(x1 + 20, y1 + 285, col_w - 40, 60, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(mtext(x1 + col_w / 2, y1 + 305, [
        "Плюси: Миттєве створення (O(1)), спільне використання дискового кешу хоста.",
        "Ризики: Пошкодження базового образу знищує всі залежні клони."
    ], size=10, color="#334155", lh=1.3))

    # Права колонка: Повні клони (Full Clones)
    x2 = 495.0
    y2 = 60.0
    p.append(rect(x2, y2, col_w, col_h, fill="#f0fdf4", stroke="#86efac", sw=1.4, rx=6))
    p.append(text(x2 + col_w / 2, y2 + 25, "Повні автономні клони (Full / Deep Clones)", size=13, color="#166534", bold=True))
    
    # Вихідний шаблон
    p.append(rect(x2 + 100, y2 + 45, col_w - 200, 60, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=6))
    p.append(text(x2 + col_w / 2, y2 + 70, "Початковий шаблон ВМ", size=11, color="#1e293b", bold=True))
    p.append(text(x2 + col_w / 2, y2 + 90, "Template.qcow2 (50 ГБ)", size=10, color="#475569"))
    
    # Стрілки копіювання блоків
    p.append(arrow(x2 + 140, y2 + 105, x2 + 110, y2 + 155, color="#16a34a", sw=1.5))
    p.append(arrow(x2 + col_w - 140, y2 + 105, x2 + col_w - 110, y2 + 155, color="#16a34a", sw=1.5))
    
    # 2 Повні незалежні копії
    for idx, cx in enumerate([x2 + 35, x2 + 225]):
        p.append(rect(cx, y2 + 160, 170, 110, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=4))
        p.append(text(cx + 85, y2 + 182, "Повний клон #%d" % (idx + 1), size=11, color="#15803d", bold=True))
        p.append(text(cx + 85, y2 + 202, "vm-%d-disk.raw (50 ГБ)" % (idx + 1), size=9, color="#64748b", italic=True))
        p.append(rect(cx + 10, y2 + 215, 150, 40, fill="#dcfce7", stroke="#86efac", sw=1.0, rx=2))
        p.append(mtext(cx + 85, y2 + 232, ["Повна незалежна", "копія всіх секторів"], size=9, color="#14532d", lh=1.2))
        
    p.append(rect(x2 + 20, y2 + 285, col_w - 40, 60, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(mtext(x2 + col_w / 2, y2 + 305, [
        "Плюси: Повна ізоляція, нульові накладні витрати ланцюжка шарів.",
        "Мінуси: Час копіювання O(N), 100% витрати дискового простору на кожну ВМ."
    ], size=10, color="#334155", lh=1.3))

    render(os.path.join(OUT, "linked-vs-full-clone.svg"), W, H, *p)


# ── Фіг. 5: Консолідація та злиття знімків (Block Commit проти Block Stream) ───
def fig_snapshot_consolidation():
    W, H = 960, 440
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Механіка консолідації шарів: Block Commit проти Block Stream", size=16, color="#0f172a", bold=True))
    
    col_w = 430.0
    col_h = 360.0
    
    # Ліва колонка: Block Commit (Злиття зверху вниз / в основу)
    x1 = 35.0
    y1 = 60.0
    p.append(rect(x1, y1, col_w, col_h, fill="#fff7ed", stroke="#fdba74", sw=1.4, rx=6))
    p.append(text(x1 + col_w / 2, y1 + 25, "Block Commit (Злиття дельт у базовий шар)", size=13, color="#c2410c", bold=True))
    
    # Схема шарів Commit
    p.append(rect(x1 + 30, y1 + 50, col_w - 60, 50, fill="#ffffff", stroke="#f97316", sw=1.2, rx=4))
    p.append(text(x1 + col_w / 2, y1 + 70, "Активний оверлей: snap2.qcow2 (R/W)", size=11, color="#9a3412", bold=True))
    p.append(text(x1 + col_w / 2, y1 + 88, "Містить останні зміни під час роботи гостя", size=9, color="#64748b"))
    
    p.append(arrow(x1 + col_w / 2, y1 + 105, x1 + col_w / 2, y1 + 145, color="#ea580c", sw=2.0))
    p.append(text(x1 + col_w / 2 + 75, y1 + 128, "Перенесення дельт", size=10, color="#c2410c", bold=True))
    
    p.append(rect(x1 + 30, y1 + 150, col_w - 60, 50, fill="#ffffff", stroke="#f97316", sw=1.2, rx=4))
    p.append(text(x1 + col_w / 2, y1 + 170, "Проміжний знімок: snap1.qcow2 (R/O)", size=11, color="#9a3412", bold=True))
    
    p.append(arrow(x1 + col_w / 2, y1 + 205, x1 + col_w / 2, y1 + 245, color="#ea580c", sw=2.0))
    p.append(text(x1 + col_w / 2 + 75, y1 + 228, "Запис у базу", size=10, color="#c2410c", bold=True))
    
    p.append(rect(x1 + 30, y1 + 250, col_w - 60, 50, fill="#fed7aa", stroke="#ea580c", sw=1.4, rx=4))
    p.append(text(x1 + col_w / 2, y1 + 272, "Базовий образ: base.qcow2 (Final Base)", size=11, color="#7c2d12", bold=True))
    p.append(text(x1 + col_w / 2, y1 + 290, "Отримує всі накопичені кластери знімків", size=9, color="#7c2d12"))
    
    p.append(text(x1 + col_w / 2, y1 + 335, "Результат: snap1 і snap2 видаляються; base стає активним", size=10, color="#9a3412", bold=True))

    # Права колонка: Block Stream (Підтягування знизу вгору / Flattening)
    x2 = 495.0
    y2 = 60.0
    p.append(rect(x2, y2, col_w, col_h, fill="#f5f3ff", stroke="#c4b5fd", sw=1.4, rx=6))
    p.append(text(x2 + col_w / 2, y2 + 25, "Block Stream (Підтягування бази в оверлей)", size=13, color="#6d28d9", bold=True))
    
    # Схема шарів Stream
    p.append(rect(x2 + 30, y2 + 50, col_w - 60, 50, fill="#ddd6fe", stroke="#7c3aed", sw=1.4, rx=4))
    p.append(text(x2 + col_w / 2, y2 + 72, "Активний оверлей: active.qcow2 (Target)", size=11, color="#4c1d95", bold=True))
    p.append(text(x2 + col_w / 2, y2 + 90, "Стає повністю автономним повним диском", size=9, color="#5b21b6"))
    
    p.append(arrow(x2 + col_w / 2, y2 + 145, x2 + col_w / 2, y2 + 105, color="#7c3aed", sw=2.0))
    p.append(text(x2 + col_w / 2 + 75, y2 + 128, "Копіювання кластерів", size=10, color="#6d28d9", bold=True))
    
    p.append(rect(x2 + 30, y2 + 150, col_w - 60, 50, fill="#ffffff", stroke="#8b5cf6", sw=1.2, rx=4))
    p.append(text(x2 + col_w / 2, y2 + 170, "Проміжний знімок: snap1.qcow2 (R/O)", size=11, color="#5b21b6", bold=True))
    
    p.append(arrow(x2 + col_w / 2, y2 + 245, x2 + col_w / 2, y2 + 205, color="#7c3aed", sw=2.0))
    p.append(text(x2 + col_w / 2 + 75, y2 + 228, "Читання з бази", size=10, color="#6d28d9", bold=True))
    
    p.append(rect(x2 + 30, y2 + 250, col_w - 60, 50, fill="#ffffff", stroke="#8b5cf6", sw=1.2, rx=4))
    p.append(text(x2 + col_w / 2, y2 + 270, "Базовий образ: base.qcow2 (Source Base)", size=11, color="#5b21b6", bold=True))
    p.append(text(x2 + col_w / 2, y2 + 288, "Незмінний; відв'язується після завершення", size=9, color="#64748b"))
    
    p.append(text(x2 + col_w / 2, y2 + 335, "Результат: active відв'язується від backing-файлів і працює соло", size=10, color="#5b21b6", bold=True))

    render(os.path.join(OUT, "snapshot-consolidation-merge.svg"), W, H, *p)


if __name__ == "__main__":
    fig_vm_snapshot_components()
    fig_cow_vs_row()
    fig_backing_chain()
    fig_linked_vs_full_clone()
    fig_snapshot_consolidation()
    print("Figures generated successfully.")
