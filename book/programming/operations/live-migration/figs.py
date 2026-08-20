# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Порівняння Pre-Copy та Post-Copy міграції ─────────────────────────
def fig_pre_copy_vs_post_copy():
    W, H = 960, 540
    p = []
    
    # Загальний фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    col_w = 440.0
    panel_h = 490.0
    top_y = 25.0
    
    # ── Ліва колонка: Pre-Copy (Попереднє копіювання) ──────────────────────────
    left_x = 25.0
    p.append(rect(left_x, top_y, col_w, panel_h, fill="#f8fafc", stroke="#3b82f6", sw=1.6, rx=6))
    p.append(text(left_x + col_w / 2, top_y + 26, "Ітеративне Pre-Copy (Попереднє копіювання)", size=13, color="#1d4ed8", bold=True))
    
    steps_pre = [
        ("Ітерація 0: Повний дамп пам'яті", "Передача всієї RAM по мережі\nГість продовжує працювати на вузлі-джерелі\nСторінки записуються в бітову маску (dirty tracking)", "#eff6ff", "#2563eb"),
        ("Ітерації 1..N: Передача брудних сторінок", "Повторне надсилання лише змінених сторінок\nГість далі генерує нові модифікації\nПеревірка умови збіжності: V_dirty ≤ V_threshold", "#f0fdf4", "#16a34a"),
        ("Зупинка і досилання (Stop-and-Copy)", "Пауза vCPU гостя на джерелі (Downtime 20-50 мс)\nДосилання залишку брудних сторінок\nСеріалізація і передача стану пристроїв (VMCS, vAPIC)", "#fef2f2", "#dc2626"),
        ("Активація на цільовому вузлі", "Десеріалізація регістрів vCPU і пристроїв\nЗапуск vCPU на цільовому вузлі\nРозсилка Gratuitous ARP для перемикання мережі", "#faf5ff", "#7c3aed")
    ]
    
    sy = top_y + 46
    bh = 84
    gap = 14
    for i, (title_txt, desc_txt, bg_c, stroke_c) in enumerate(steps_pre):
        y = sy + i * (bh + gap)
        p.append(rect(left_x + 16, y, col_w - 32, bh, fill=bg_c, stroke=stroke_c, sw=1.3, rx=5))
        p.append(text(left_x + col_w / 2, y + 20, title_txt, size=12, color=stroke_c, bold=True))
        lines = desc_txt.split("\n")
        p.append(mtext(left_x + col_w / 2, y + 42, lines, size=10.5, color=INK, lh=1.35))
        if i < len(steps_pre) - 1:
            p.append(arrow(left_x + col_w / 2, y + bh + 1, left_x + col_w / 2, y + bh + gap - 1, color="#64748b", sw=1.4))
            
    p.append(rect(left_x + 16, top_y + panel_h - 48, col_w - 32, 38, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(left_x + col_w / 2, top_y + panel_h - 25, "Властивість: Безпечний відкат при збої, але ризик незабіжності", size=10.5, color="#1e293b", bold=True))
    
    # ── Права колонка: Post-Copy (Перенесення після копіювання) ────────────────
    right_x = 495.0
    p.append(rect(right_x, top_y, col_w, panel_h, fill="#f8fafc", stroke="#059669", sw=1.6, rx=6))
    p.append(text(right_x + col_w / 2, top_y + 26, "Post-Copy (Перенесення після копіювання)", size=13, color="#047857", bold=True))
    
    steps_post = [
        ("Миттєва зупинка на джерелі", "Коротка початкова пауза vCPU на джерелі\nСеріалізація та передача стану vCPU і пристроїв\nПам'ять залишається на вузлі-джерелі", "#fef2f2", "#dc2626"),
        ("Негайний старт на цілі (з порожньою RAM)", "Реєстрація діапазонів пам'яті через userfaultfd\nЗапуск vCPU на цільовому вузлі\nРозсилка Gratuitous ARP на початку процесу", "#eff6ff", "#2563eb"),
        ("Сторінкові збої на вимогу (On-Demand Faults)", "vCPU звертається до відсутньої сторінки → Page Fault\nuserfaultfd перехоплює збій у QEMU\nЗапит сторінки через мережу з джерела (високий пріоритет)", "#fffbeb", "#d97706"),
        ("Фонова докачка залишку пам'яті", "Фоновий потік послідовно передає холодні сторінки\nВикористання ioctl(UFFDIO_COPY) для вставки сторінок\nГарантоване завершення рівно за один повний прохід", "#f0fdf4", "#16a34a")
    ]
    
    for i, (title_txt, desc_txt, bg_c, stroke_c) in enumerate(steps_post):
        y = sy + i * (bh + gap)
        p.append(rect(right_x + 16, y, col_w - 32, bh, fill=bg_c, stroke=stroke_c, sw=1.3, rx=5))
        p.append(text(right_x + col_w / 2, y + 20, title_txt, size=12, color=stroke_c, bold=True))
        lines = desc_txt.split("\n")
        p.append(mtext(right_x + col_w / 2, y + 42, lines, size=10.5, color=INK, lh=1.35))
        if i < len(steps_post) - 1:
            p.append(arrow(right_x + col_w / 2, y + bh + 1, right_x + col_w / 2, y + bh + gap - 1, color="#64748b", sw=1.4))
            
    p.append(rect(right_x + 16, top_y + panel_h - 48, col_w - 32, 38, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(text(right_x + col_w / 2, top_y + panel_h - 25, "Властивість: Гарантована збіжність, але збій мережі вбиває ВМ", size=10.5, color="#1e293b", bold=True))
    
    render(os.path.join(OUT, "pre-copy-vs-post-copy.svg"), W, H, *p)

# ── Фіг. 2: Апаратне відстеження брудних сторінок ──────────────────────────────
def fig_dirty_page_tracking():
    W, H = 960, 480
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    col_w = 440.0
    panel_h = 430.0
    top_y = 25.0
    
    # ── Ліва секція: Захист від запису (EPT Write-Protection) ──────────────────
    left_x = 25.0
    p.append(rect(left_x, top_y, col_w, panel_h, fill="#fffaf5", stroke="#ea580c", sw=1.5, rx=6))
    p.append(text(left_x + col_w / 2, top_y + 24, "Програмний метод: EPT/NPT Write Protection", size=13, color="#c2410c", bold=True))
    
    steps_wp = [
        ("1. Скидання біта W у таблицях EPT", "Гіпервізор знімає дозвіл на запис у PTE (Write=0)", "#ffffff", "#ea580c"),
        ("2. Спроба запису гостьовим vCPU", "Інструкція гостя викликає апаратне виключення EPT Violation", "#ffffff", "#ea580c"),
        ("3. Дорогий вихід у корінь (VM-Exit)", "Процесор перериває гостя, зберігає стан і перемикається в KVM", "#fef2f2", "#dc2626"),
        ("4. Встановлення біта в Dirty Bitmap", "KVM позначає сторінку як брудну у виділеній бітовій масці", "#ffffff", "#ea580c"),
        ("5. Відновлення Write=1 та VM-Entry", "KVM дозволяє запис та повертає керування гостю (~1500 тактів)", "#f0fdf4", "#16a34a"),
    ]
    
    sy = top_y + 44
    bh = 58
    gap = 12
    for i, (title_t, desc_t, bg_c, stroke_c) in enumerate(steps_wp):
        y = sy + i * (bh + gap)
        p.append(rect(left_x + 16, y, col_w - 32, bh, fill=bg_c, stroke=stroke_c, sw=1.2, rx=5))
        p.append(text(left_x + 28, y + 19, title_t, size=11.5, color=stroke_c, bold=True, anchor="start"))
        p.append(text(left_x + 28, y + 42, desc_t, size=10, color=INK, anchor="start"))
        if i < len(steps_wp) - 1:
            p.append(arrow(left_x + col_w / 2, y + bh + 1, left_x + col_w / 2, y + bh + gap - 1, color="#9a3412", sw=1.3))
            
    p.append(text(left_x + col_w / 2, top_y + panel_h - 18, "Ціна: Десятки тисяч VM-Exit на секунду деградують продуктивність", size=10, color="#9a3412", bold=True))
    
    # ── Права секція: Intel PML (Page Modification Logging) ────────────────────
    right_x = 495.0
    p.append(rect(right_x, top_y, col_w, panel_h, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    p.append(text(right_x + col_w / 2, top_y + 24, "Апаратний метод: Intel PML (Page Modification Logging)", size=13, color="#15803d", bold=True))
    
    steps_pml = [
        ("1. Активація біта PML у VMCS", "Гіпервізор виділяє 4 КБ буфер у пам'яті для PML (512 записів)", "#ffffff", "#16a34a"),
        ("2. Запис гостя в пам'ять (Write)", "Гість модифікує сторінку без переривання виконання", "#ffffff", "#16a34a"),
        ("3. Апаратне логування мікрокодом (0 тактів)", "Процесор сам записує GPA у буфер PML без виходу VM-Exit!", "#ecfdf5", "#059669"),
        ("4. Заповнення 512 записів буфера", "Лише після 512 модифікованих сторінок виникає PML Full VM-Exit", "#eff6ff", "#2563eb"),
        ("5. Пакетне копіювання в Dirty Bitmap", "KVM зчитує одразу 512 сторінок за один системний перехід", "#ffffff", "#16a34a"),
    ]
    
    for i, (title_t, desc_t, bg_c, stroke_c) in enumerate(steps_pml):
        y = sy + i * (bh + gap)
        p.append(rect(right_x + 16, y, col_w - 32, bh, fill=bg_c, stroke=stroke_c, sw=1.2, rx=5))
        p.append(text(right_x + 28, y + 19, title_t, size=11.5, color=stroke_c, bold=True, anchor="start"))
        p.append(text(right_x + 28, y + 42, desc_t, size=10, color=INK, anchor="start"))
        if i < len(steps_pml) - 1:
            p.append(arrow(right_x + col_w / 2, y + bh + 1, right_x + col_w / 2, y + bh + gap - 1, color="#15803d", sw=1.3))
            
    p.append(text(right_x + col_w / 2, top_y + panel_h - 18, "Зиск: Зменшення кількості VM-Exit у сотні разів під час міграції", size=10, color="#15803d", bold=True))
    
    render(os.path.join(OUT, "dirty-page-tracking-hardware.svg"), W, H, *p)

# ── Фіг. 3: Мережеве перемикання та Gratuitous ARP ────────────────────────────
def fig_network_handover():
    W, H = 960, 480
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Верхня частина: Комутатор мережі та FDB
    sw_x, sw_y, sw_w, sw_h = 320.0, 35.0, 320.0, 105.0
    p.append(rect(sw_x, sw_y, sw_w, sw_h, fill="#f8fafc", stroke="#475569", sw=1.6, rx=6))
    p.append(text(sw_x + sw_w / 2, sw_y + 24, "L2 Комутатор (ToR Switch / OVS)", size=13, color="#1e293b", bold=True))
    p.append(text(sw_x + sw_w / 2, sw_y + 48, "Таблиця комутації (Forwarding Database - FDB):", size=11, color=MUTED))
    p.append(rect(sw_x + 20, sw_y + 60, sw_w - 40, 32, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(sw_x + sw_w / 2, sw_y + 80, "MAC AA:BB:CC:DD:EE:FF  ➔  Порт 2 (Оновлено)", size=11, color="#16a34a", bold=True))
    
    # Клієнт зліва вгорі
    cl_x, cl_y, cl_w, cl_h = 30.0, 45.0, 220.0, 85.0
    p.append(rect(cl_x, cl_y, cl_w, cl_h, fill="#eff6ff", stroke="#3b82f6", sw=1.4, rx=6))
    p.append(text(cl_x + cl_w / 2, cl_y + 24, "Клієнтський застосунок", size=12, color="#1d4ed8", bold=True))
    p.append(mtext(cl_x + cl_w / 2, cl_y + 46, ["Активна TCP-сесія до 10.0.0.50", "Seq: 420910, Ack: 88120"], size=10.5, color=INK, lh=1.35))
    
    # Зв'язок Клієнт ➔ Світч
    p.append(arrow(cl_x + cl_w, cl_y + cl_h / 2, sw_x, sw_y + sw_h / 2, color="#3b82f6", sw=1.6))
    p.append(text(cl_x + cl_w + 35, cl_y + cl_h / 2 - 10, "TCP-пакети", size=10, color="#1d4ed8", bold=True))
    
    # Вузол-джерело (Host A)
    src_x, src_y, host_w, host_h = 60.0, 220.0, 380.0, 220.0
    p.append(rect(src_x, src_y, host_w, host_h, fill="#fff5f5", stroke="#dc2626", sw=1.5, rx=6))
    p.append(text(src_x + host_w / 2, src_y + 26, "Хост A (Джерело) — Порт 1 комутатора", size=12.5, color="#b91c1c", bold=True))
    
    p.append(rect(src_x + 20, src_y + 45, host_w - 40, 110, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=5))
    p.append(text(src_x + host_w / 2, src_y + 70, "ВМ зупинено (vCPU Paused)", size=12, color="#dc2626", bold=True))
    p.append(mtext(src_x + host_w / 2, src_y + 94, ["Пам'ять заморожена / звільняється", "virtio-net дескриптори закриті", "Старі пакети більше не приймаються"], size=10.5, color=INK, lh=1.35))
    
    p.append(line(sw_x + 60, sw_y + sw_h, src_x + host_w / 2, src_y, color="#94a3b8", sw=1.4, dash="4 4"))
    p.append(text(src_x + host_w / 2 + 10, src_y - 20, "Старий маршрут (відключено)", size=10, color=MUTED))
    
    # Вузол-приймач (Host B)
    dst_x, dst_y = 520.0, 220.0
    p.append(rect(dst_x, dst_y, host_w, host_h, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    p.append(text(dst_x + host_w / 2, dst_y + 26, "Хост B (Ціль) — Порт 2 комутатора", size=12.5, color="#15803d", bold=True))
    
    p.append(rect(dst_x + 20, dst_y + 45, host_w - 40, 110, fill="#ffffff", stroke="#86efac", sw=1.2, rx=5))
    p.append(text(dst_x + host_w / 2, dst_y + 70, "ВМ відновлено (vCPU Running)", size=12, color="#16a34a", bold=True))
    p.append(mtext(dst_x + host_w / 2, dst_y + 94, ["IP: 10.0.0.50, MAC: AA:BB:CC:DD:EE:FF", "TCP стек збережено в ядрі гостя", "Обробка вхідних пакетів без рестарту"], size=10.5, color=INK, lh=1.35))
    
    # GARP широкомовне сповіщення (зелена стрілка вгору-ліворуч)
    p.append(arrow(dst_x + 90, dst_y, sw_x + sw_w - 40, sw_y + sw_h, color="#16a34a", sw=2.0))
    p.append(rect(dst_x - 40, dst_y - 65, 180, 36, fill="#ffffff", stroke="#86efac", sw=1.0, rx=4))
    p.append(text(dst_x + 50, dst_y - 48, "1. Gratuitous ARP (Broadcast)", size=10, color="#15803d", bold=True))
    p.append(text(dst_x + 50, dst_y - 34, "«MAC AA:BB:.. на Порту 2»", size=9.5, color="#15803d"))
    
    # Новий маршрут трафіку (синя стрілка вниз-праворуч)
    p.append(arrow(sw_x + sw_w - 10, sw_y + sw_h, dst_x + 260, dst_y, color="#2563eb", sw=2.0))
    p.append(rect(dst_x + 210, dst_y - 60, 150, 34, fill="#ffffff", stroke="#93c5fd", sw=1.0, rx=4))
    p.append(text(dst_x + 285, dst_y - 44, "2. Новий потік TCP", size=10.5, color="#1d4ed8", bold=True))
    p.append(text(dst_x + 285, dst_y - 30, "Пакет скеровано на Порт 2", size=9, color="#1d4ed8"))
    
    # Нижня плашка пояснення
    p.append(rect(30, 420, W - 60, 40, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(W / 2, 444, "Клієнт не розриває TCP: затримка switchover (30-80 мс) менша за таймаут повтору TCP RTO (200 мс)", size=11, color="#1e293b", bold=True))
    
    render(os.path.join(OUT, "migration-network-handover.svg"), W, H, *p)

# ── Фіг. 4: Збіжність та Auto-Converge тротлінг ────────────────────────────────
def fig_convergence_and_throttling():
    W, H = 960, 480
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    col_w = 440.0
    panel_h = 430.0
    top_y = 25.0
    
    # Лівий графік: Незабіжна міграція (D > B)
    left_x = 25.0
    p.append(rect(left_x, top_y, col_w, panel_h, fill="#fff5f5", stroke="#ef4444", sw=1.5, rx=6))
    p.append(text(left_x + col_w / 2, top_y + 26, "Сценарій А: Незабіжність (Швидкість запису > Мережа)", size=12.5, color="#b91c1c", bold=True))
    
    # Осі графіка зліва
    gx, gy, gw, gh = left_x + 50, top_y + 60, col_w - 80, 240
    p.append(line(gx, gy + gh, gx + gw, gy + gh, color=LINE, sw=1.5))
    p.append(line(gx, gy, gx, gy + gh, color=LINE, sw=1.5))
    p.append(text(gx + gw, gy + gh + 20, "Ітерації міграції →", size=10.5, color=INK, anchor="end"))
    p.append(text(gx - 10, gy + 15, "RAM (ГБ)", size=10.5, color=INK, anchor="end"))
    
    # Початковий рівень пам'яті
    p.append(line(gx, gy + 40, gx + gw, gy + 40, color="#94a3b8", sw=1.2, dash="3 3"))
    p.append(text(gx - 8, gy + 44, "64 ГБ", size=10, color=MUTED, anchor="end"))
    
    # Поріг простою (Downtime threshold)
    thresh_y = gy + gh - 30
    p.append(line(gx, thresh_y, gx + gw, thresh_y, color="#16a34a", sw=1.4, dash="4 3"))
    p.append(text(gx + gw - 10, thresh_y - 8, "Поріг Stop-and-Copy (500 МБ)", size=10, color="#16a34a", bold=True, anchor="end"))
    
    # Крива залишку брудних сторінок (стагнує на високому рівні)
    pts_div = [(gx, gy + 40), (gx + 60, gy + 110), (gx + 120, gy + 125), (gx + 180, gy + 120), (gx + 240, gy + 130), (gx + gw - 20, gy + 125)]
    for i in range(len(pts_div) - 1):
        p.append(line(pts_div[i][0], pts_div[i][1], pts_div[i+1][0], pts_div[i+1][1], color="#dc2626", sw=2.2))
        p.append(circle(pts_div[i][0], pts_div[i][1], 3.5, fill="#dc2626", stroke="#ffffff", sw=1.0))
    p.append(circle(pts_div[-1][0], pts_div[-1][1], 3.5, fill="#dc2626", stroke="#ffffff", sw=1.0))
    
    p.append(rect(left_x + 20, top_y + 320, col_w - 40, 85, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=5))
    p.append(text(left_x + col_w / 2, top_y + 342, "Нескінченний цикл міграції:", size=11, color="#dc2626", bold=True))
    p.append(mtext(left_x + col_w / 2, top_y + 364, ["Брудна пам'ять генерується швидше, ніж надсилається", "Мережа 10 Гбіт/с (1.1 ГБ/с) проти Запису 1.8 ГБ/с", "Міграція зависає, споживаючи ресурси мережі"], size=10, color=INK, lh=1.35))
    
    # Правий графік: Auto-converge тротлінг
    right_x = 495.0
    p.append(rect(right_x, top_y, col_w, panel_h, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    p.append(text(right_x + col_w / 2, top_y + 26, "Сценарій Б: Auto-Converge (vCPU Throttling)", size=12.5, color="#15803d", bold=True))
    
    # Осі графіка справа
    gx2, gy2, gw2, gh2 = right_x + 50, top_y + 60, col_w - 80, 240
    p.append(line(gx2, gy2 + gh2, gx2 + gw2, gy2 + gh2, color=LINE, sw=1.5))
    p.append(line(gx2, gy2, gx2, gy2 + gh2, color=LINE, sw=1.5))
    p.append(text(gx2 + gw2, gy2 + gh2 + 20, "Ітерації міграції →", size=10.5, color=INK, anchor="end"))
    p.append(text(gx2 - 10, gy2 + 15, "RAM (ГБ)", size=10.5, color=INK, anchor="end"))
    
    p.append(line(gx2, gy2 + 40, gx2 + gw2, gy2 + 40, color="#94a3b8", sw=1.2, dash="3 3"))
    p.append(text(gx2 - 8, gy2 + 44, "64 ГБ", size=10, color=MUTED, anchor="end"))
    
    p.append(line(gx2, thresh_y, gx2 + gw2, thresh_y, color="#16a34a", sw=1.4, dash="4 3"))
    p.append(text(gx2 + gw2 - 10, thresh_y - 8, "Поріг Stop-and-Copy (500 МБ)", size=10, color="#16a34a", bold=True, anchor="end"))
    
    # Крива збіжності з тротлінгом
    pts_conv = [(gx2, gy2 + 40), (gx2 + 60, gy2 + 110), (gx2 + 120, gy2 + 140), (gx2 + 180, gy2 + 180), (gx2 + 240, gy2 + 225), (gx2 + 290, thresh_y + 5)]
    for i in range(len(pts_conv) - 1):
        p.append(line(pts_conv[i][0], pts_conv[i][1], pts_conv[i+1][0], pts_conv[i+1][1], color="#16a34a", sw=2.2))
        p.append(circle(pts_conv[i][0], pts_conv[i][1], 3.5, fill="#16a34a", stroke="#ffffff", sw=1.0))
    p.append(circle(pts_conv[-1][0], pts_conv[-1][1], 4.5, fill="#dc2626", stroke="#ffffff", sw=1.2))
    
    # Анотація тротлінгу
    p.append(rect(gx2 + 90, gy2 + 80, 140, 36, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=4))
    p.append(text(gx2 + 160, gy2 + 98, "vCPU Throttle +20%..70%", size=9.5, color="#b45309", bold=True))
    p.append(arrow(gx2 + 160, gy2 + 116, gx2 + 150, gy2 + 155, color="#d97706", sw=1.2))
    
    p.append(rect(right_x + 20, top_y + 320, col_w - 40, 85, fill="#ffffff", stroke="#86efac", sw=1.2, rx=5))
    p.append(text(right_x + col_w / 2, top_y + 342, "Примусова штучна збіжність:", size=11, color="#15803d", bold=True))
    p.append(mtext(right_x + col_w / 2, top_y + 364, ["Гіпервізор штучно уповільнює виконання інструкцій гостя", "Швидкість модифікації пам'яті падає нижче пропускної здатності", "Обсяг залишку падає нижче порогу → безпечний Stop-and-Copy"], size=10, color=INK, lh=1.35))
    
    render(os.path.join(OUT, "convergence-and-throttling.svg"), W, H, *p)

def main():
    fig_pre_copy_vs_post_copy()
    fig_dirty_page_tracking()
    fig_network_handover()
    fig_convergence_and_throttling()
    print("All figures generated successfully.")

if __name__ == "__main__":
    main()
