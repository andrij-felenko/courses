# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Часова шкала RPO, RTO та WRT ──────────────────────────────────────
def fig_rpo_rto_timeline():
    W, H = 960, 460
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Часова шкала аварійного відновлення: метрики RPO, RTO, WRT та MTD", size=15, color=INK, bold=True, anchor="start"))
    
    axis_y = 220.0
    p.append(line(40, axis_y, W - 40, axis_y, color=LINE, sw=2.0))
    p.append(arrow(W - 70, axis_y, W - 30, axis_y, color=LINE, sw=2.0))
    p.append(text(W - 40, axis_y - 12, "Час (t) →", size=13, color=INK, bold=True, anchor="end"))
    
    t_backup = 130.0
    t_disaster = 360.0
    t_detect = 470.0
    t_rto = 670.0
    t_wrt = 870.0
    
    p.append(rect(t_backup, 60, t_disaster - t_backup, 135, fill="#fef2f2", stroke="#f87171", sw=1.2, rx=4))
    p.append(text((t_backup + t_disaster) / 2, 82, "Вікно втрати даних (RPO)", size=12.5, color="#dc2626", bold=True))
    p.append(mtext((t_backup + t_disaster) / 2, 104, ["Транзакції, не зафіксовані", "у віддаленому сховищі"], size=11, color=INK, lh=1.35))
    
    p.append(rect(t_disaster, 60, t_rto - t_disaster, 135, fill="#fffbeb", stroke="#f59e0b", sw=1.2, rx=4))
    p.append(text((t_disaster + t_rto) / 2, 82, "Час відновлення (RTO)", size=12.5, color="#d97706", bold=True))
    p.append(mtext((t_disaster + t_rto) / 2, 104, ["Діагностика, failover,", "підйом вузлів, реплікація"], size=11, color=INK, lh=1.35))
    
    p.append(rect(t_rto, 60, t_wrt - t_rto, 135, fill="#eff6ff", stroke="#60a5fa", sw=1.2, rx=4))
    p.append(text((t_rto + t_wrt) / 2, 82, "Вивірка даних (WRT)", size=12.5, color="#2563eb", bold=True))
    p.append(mtext((t_rto + t_wrt) / 2, 104, ["Перевірка цілісності,", "прогін пропущених черг"], size=11, color=INK, lh=1.35))
    
    events = [
        (t_backup, "Остання точка бекапу", "Синхронізація / знімок", "#16a34a"),
        (t_disaster, "Катастрофа", "Падіння ЦОД / аварія", "#dc2626"),
        (t_detect, "Оголошення DR", "Рішення про перемикання", "#d97706"),
        (t_rto, "Сервіс відновлено", "Підйом серверів і БД", "#2563eb"),
        (t_wrt, "Повний робочий стан", "Завершення вивірки", "#059669"),
    ]
    
    for tx, title_ev, desc_ev, col in events:
        p.append(line(tx, 60, tx, axis_y + 35, color=col, sw=1.5, dash="2 2"))
        p.append(circle(tx, axis_y, 4.5, fill=col, stroke="#ffffff", sw=1.5))
        p.append(text(tx, axis_y + 50, title_ev, size=11, color=col, bold=True))
        p.append(text(tx, axis_y + 65, desc_ev, size=10, color=MUTED))
        
    bracket_y1 = axis_y + 90
    p.append(line(t_backup, bracket_y1, t_disaster, bracket_y1, color="#dc2626", sw=1.8))
    p.append(circle(t_backup, bracket_y1, 3.0, fill="#dc2626"))
    p.append(circle(t_disaster, bracket_y1, 3.0, fill="#dc2626"))
    p.append(text((t_backup + t_disaster) / 2, bracket_y1 + 18, "RPO (Recovery Point Objective)", size=11.5, color="#dc2626", bold=True))
    
    p.append(line(t_disaster, bracket_y1, t_rto, bracket_y1, color="#d97706", sw=1.8))
    p.append(circle(t_rto, bracket_y1, 3.0, fill="#d97706"))
    p.append(text((t_disaster + t_rto) / 2, bracket_y1 + 18, "RTO (Recovery Time Objective)", size=11.5, color="#d97706", bold=True))
    
    bracket_y2 = axis_y + 135
    p.append(line(t_disaster, bracket_y2, t_wrt, bracket_y2, color="#059669", sw=2.0))
    p.append(circle(t_disaster, bracket_y2, 3.5, fill="#059669"))
    p.append(circle(t_wrt, bracket_y2, 3.5, fill="#059669"))
    p.append(text((t_disaster + t_wrt) / 2, bracket_y2 + 18, "MTD = RTO + WRT (Maximum Tolerable Downtime)", size=12, color="#059669", bold=True))
    
    render(os.path.join(OUT, "rpo-rto-timeline.svg"), W, H, *p)

# ── Фіг. 2: Порівняння чотирьох стратегій DR ──────────────────────────────────
def fig_dr_strategies_comparison():
    W, H = 960, 480
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Класифікація стратегій аварійного відновлення за ціною та швидкістю", size=15, color=INK, bold=True, anchor="start"))
    
    strategies = [
        ("1. Backup & Restore", "Холодний старт", "RPO: 12-24 год\nRTO: 8-24+ год\nВартість: $",
         "Бекапи у хмарне сховище (S3).\nІнфраструктура створюється з нуля\nчерез IaC лише після аварії.", "#f1f5f9", "#475569"),
        ("2. Pilot Light", "Запальник", "RPO: секунди / хвилини\nRTO: 30-60 хв\nВартість: $$",
         "БД реплікується асинхронно у DR.\nСервери застосунків вимкнені.\nПідйом обчислень за шаблоном.", "#eff6ff", "#2563eb"),
        ("3. Warm Standby", "Теплий резерв", "RPO: мілісекунди\nRTO: 5-15 хв\nВартість: $$$",
         "Зменшений дубль системи постійно\nпрацює у DR. Обробляє мінімум трафіку.\nАвтоскейл до 100% за хвилини.", "#f0fdf4", "#16a34a"),
        ("4. Active-Active", "Гарячий кластер", "RPO: ≈ 0 (синхронно)\nRTO: ≈ 0 (миттєво)\nВартість: $$$$$",
         "Обидва регіони обслуговують трафік.\nГлобальне балансування (GSLB).\nСкладне розв'язання конфліктів.", "#fef2f2", "#dc2626")
    ]
    
    col_w = 214.0
    col_gap = 14.0
    start_x = 28.0
    start_y = 65.0
    box_h = 320.0
    
    for i, (title_st, subtitle_st, metrics_st, desc_st, bg_col, stroke_col) in enumerate(strategies):
        x = start_x + i * (col_w + col_gap)
        
        p.append(rect(x, start_y, col_w, box_h, fill=bg_col, stroke=stroke_col, sw=1.6, rx=6))
        p.append(rect(x, start_y, col_w, 42, fill=stroke_col, stroke=stroke_col, rx=6))
        p.append(text(x + col_w / 2, start_y + 18, title_st, size=12, color="#ffffff", bold=True))
        p.append(text(x + col_w / 2, start_y + 33, subtitle_st, size=10.5, color="#f8fafc"))
        
        p.append(rect(x + 10, start_y + 52, col_w - 20, 68, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
        p.append(mtext(x + col_w / 2, start_y + 68, metrics_st.split("\n"), size=11, color=INK, lh=1.35, bold=True))
        
        desc_lines = desc_st.split("\n")
        p.append(mtext(x + col_w / 2, start_y + 145, desc_lines, size=10.5, color=INK, lh=1.4))
        
        p.append(line(x + 15, start_y + 240, x + col_w - 15, start_y + 240, color="#cbd5e1", sw=1.0))
        readiness_labels = ["Сховище: пасивне", "БД: гаряча, CPU: 0%", "БД: гаряча, CPU: 20%", "БД: Master-Master"]
        p.append(text(x + col_w / 2, start_y + 265, readiness_labels[i], size=10, color=stroke_col, bold=True))
        
    bar_y = 405.0
    p.append(rect(28, bar_y, W - 56, 50, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(line(50, bar_y + 25, W - 60, bar_y + 25, color=LINE, sw=1.5))
    p.append(arrow(W - 90, bar_y + 25, W - 50, bar_y + 25, color=LINE, sw=2.0))
    p.append(text(50, bar_y + 18, "Низька вартість інфраструктури, довгий простій", size=11, color="#475569", bold=True, anchor="start"))
    p.append(text(W - 55, bar_y + 18, "Висока вартість, нульовий простій (Zero-RPO/RTO)", size=11, color="#dc2626", bold=True, anchor="end"))
    
    render(os.path.join(OUT, "dr-strategies-comparison.svg"), W, H, *p)

# ── Фіг. 3: Архітектура Point-in-Time Recovery (PITR) ─────────────────────────
def fig_pitr_wal_replay():
    W, H = 960, 480
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Механізм Point-in-Time Recovery (PITR): відтворення базового знімка та потоку WAL", size=15, color=INK, bold=True, anchor="start"))
    
    p.append(rect(40, 70, 200, 130, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=6))
    p.append(text(140, 95, "Базовий знімок (Base)", size=13, color="#2563eb", bold=True))
    p.append(mtext(140, 120, ["Фізичний знімок файлів БД", "Час: 02:00:00 UTC", "LSN: 0/16000000", "Контрольна сума CRC32: OK"], size=10.5, color=INK, lh=1.35))
    
    p.append(arrow(245, 135, 295, 135, color=LINE, sw=1.8))
    p.append(text(270, 125, "Старт", size=11, color=MUTED, bold=True))
    
    wal_boxes = [
        ("WAL 001", "02:00-06:00\n100k TX", "#f0fdf4", "#16a34a", True),
        ("WAL 002", "06:00-10:00\n120k TX", "#f0fdf4", "#16a34a", True),
        ("WAL 003", "10:00-14:00\n150k TX", "#f0fdf4", "#16a34a", True),
        ("WAL 004", "14:00-14:27:03\n45k TX", "#fef9c3", "#ca8a04", True),
        ("WAL 005 (АВАРІЯ)", "14:27:04: DROP TABLE\nЗнищення даних!", "#fef2f2", "#dc2626", False),
    ]
    
    w_start_x = 300.0
    w_box_w = 118.0
    w_gap = 10.0
    
    for i, (w_title, w_sub, bg_c, strk_c, is_applied) in enumerate(wal_boxes):
        bx = w_start_x + i * (w_box_w + w_gap)
        p.append(rect(bx, 70, w_box_w, 130, fill=bg_c, stroke=strk_c, sw=1.5, rx=5))
        p.append(text(bx + w_box_w / 2, 92, w_title, size=11, color=strk_c, bold=True))
        p.append(mtext(bx + w_box_w / 2, 116, w_sub.split("\n"), size=10, color=INK, lh=1.35))
        
        status_txt = "✓ Відтворено" if is_applied else "✗ ВІДХИЛЕНО"
        status_col = "#16a34a" if is_applied else "#dc2626"
        p.append(rect(bx + 8, 162, w_box_w - 16, 26, fill="#ffffff", stroke=status_col, sw=1.0, rx=3))
        p.append(text(bx + w_box_w / 2, 179, status_txt, size=10, color=status_col, bold=True))
        
        if i < len(wal_boxes) - 1:
            p.append(arrow(bx + w_box_w + 1, 135, bx + w_box_w + w_gap - 1, 135, color=LINE, sw=1.2))
            
    target_x = w_start_x + 3 * (w_box_w + w_gap) + w_box_w
    p.append(line(target_x, 55, target_x, 230, color="#dc2626", sw=2.0, dash="3 3"))
    p.append(circle(target_x, 55, 4.0, fill="#dc2626"))
    p.append(rect(target_x - 130, 235, 260, 48, fill="#fef2f2", stroke="#dc2626", sw=1.4, rx=5))
    p.append(text(target_x, 252, "Цільова точка (Target Time / LSN)", size=11.5, color="#dc2626", bold=True))
    p.append(text(target_x, 270, "14:27:03.999 (за 1 мс до аварії)", size=10.5, color=INK))
    
    res_y = 305.0
    p.append(rect(40, res_y, W - 80, 145, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(60, res_y + 24, "Послідовність роботи координатора PITR:", size=13, color=INK, bold=True, anchor="start"))
    
    steps = [
        ("1. Розгортання знімка:", "Відновлює стан файлів даних на момент 02:00:00 (heap pages, індекси, каталоги метаданих).", "#2563eb"),
        ("2. Потокове читання WAL:", "Послідовно зчитує сегменти WAL із незмінного об'єктного сховища S3/NFS.", "#16a34a"),
        ("3. Верифікація REDO:", "Перевіряє контрольні суми записів і застосовує зміни сторінка за сторінкою (REDO loop).", "#d97706"),
        ("4. Зупинка на мітці:", "Досягає target_time = 14:27:03, зупиняє REDO, фіксує узгоджений стан і відкриває БД на запис.", "#dc2626"),
    ]
    
    sy = res_y + 48
    for label_st, desc_st, col in steps:
        p.append(circle(65, sy, 3.5, fill=col, stroke=col, sw=1.0))
        p.append(text(80, sy + 4, label_st, size=11.5, color=INK, bold=True, anchor="start"))
        p.append(text(270, sy + 4, desc_st, size=11, color=MUTED, anchor="start"))
        sy += 23
        
    render(os.path.join(OUT, "pitr-wal-replay.svg"), W, H, *p)

# ── Фіг. 4: Небезпека Split-Brain та ізоляція вузлів (Fencing / STONITH) ───────
def fig_split_brain_and_fencing():
    W, H = 960, 480
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Небезпека розділення пам'яті (Split-Brain) та механізм кворумної ізоляції (Fencing)", size=15, color=INK, bold=True, anchor="start"))
    
    reg_w = 260.0
    reg_h = 240.0
    p.append(rect(40, 70, reg_w, reg_h, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    p.append(rect(40, 70, reg_w, 36, fill="#2563eb", stroke="#2563eb", rx=6))
    p.append(text(40 + reg_w / 2, 93, "Регіон A (Основний / Isolated)", size=13, color="#ffffff", bold=True))
    
    p.append(rect(60, 120, reg_w - 40, 70, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
    p.append(text(40 + reg_w / 2, 142, "Primary Вузол", size=12, color="#1e40af", bold=True))
    p.append(mtext(40 + reg_w / 2, 164, ["Втратив зв'язок з Регіоном B", "Вважає себе лідером!"], size=10.5, color=INK, lh=1.35))
    
    p.append(rect(60, 205, reg_w - 40, 85, fill="#fef2f2", stroke="#f87171", sw=1.2, rx=4))
    p.append(text(40 + reg_w / 2, 225, "СТАТУС: FENCED (Ізольовано)", size=11, color="#dc2626", bold=True))
    p.append(mtext(40 + reg_w / 2, 246, ["Кворум втрачено (1/3)", "STONITH: живлення вимкнено", "АБО переведено в Read-Only"], size=10, color=INK, lh=1.3))
    
    p.append(rect(W - 40 - reg_w, 70, reg_w, reg_h, fill="#f0fdf4", stroke="#16a34a", sw=1.6, rx=6))
    p.append(rect(W - 40 - reg_w, 70, reg_w, 36, fill="#16a34a", stroke="#16a34a", rx=6))
    p.append(text(W - 40 - reg_w / 2, 93, "Регіон B (DR Standby -> Promoted)", size=13, color="#ffffff", bold=True))
    
    p.append(rect(W - 40 - reg_w + 20, 120, reg_w - 40, 70, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    p.append(text(W - 40 - reg_w / 2, 142, "DR Standby -> Новий Primary", size=12, color="#166534", bold=True))
    p.append(mtext(W - 40 - reg_w / 2, 164, ["Отримав голос арбітра", "Успішний Failover"], size=10.5, color=INK, lh=1.35))
    
    p.append(rect(W - 40 - reg_w + 20, 205, reg_w - 40, 85, fill="#ecfdf5", stroke="#6ee7b7", sw=1.2, rx=4))
    p.append(text(W - 40 - reg_w / 2, 225, "СТАТУС: ACTIVE LEADER", size=11, color="#059669", bold=True))
    p.append(mtext(W - 40 - reg_w / 2, 246, ["Кворум отримано (2/3)", "Оренду лідера подовжено", "Приймає нові транзакції"], size=10, color=INK, lh=1.3))
    
    mid_x = W / 2
    p.append(line(reg_w + 50, 155, W - reg_w - 50, 155, color="#dc2626", sw=2.2, dash="5 4"))
    p.append(rect(mid_x - 70, 138, 140, 34, fill="#fef2f2", stroke="#dc2626", sw=1.4, rx=4))
    p.append(text(mid_x, 159, "Мережевий розрив", size=11.5, color="#dc2626", bold=True))
    
    p.append(rect(mid_x - 110, 220, 220, 90, fill="#faf5ff", stroke="#9333ea", sw=1.5, rx=6))
    p.append(text(mid_x, 244, "Регіон C: Quorum Witness / Арбітр", size=12, color="#7e22ce", bold=True))
    p.append(mtext(mid_x, 268, ["Незалежний вузол кворуму", "Видає оренду лідера (Lease Lock)", "Голосує за промоушн Регіону B"], size=10, color=INK, lh=1.35))
    
    p.append(line(mid_x - 110, 265, reg_w + 40, 265, color="#dc2626", sw=1.5, dash="3 3"))
    p.append(text((mid_x - 110 + reg_w + 40) / 2, 255, "Немає зв'язку", size=10, color="#dc2626", bold=True))
    
    p.append(arrow(mid_x + 110, 265, W - 40 - reg_w, 265, color="#16a34a", sw=1.8))
    p.append(text((mid_x + 110 + W - 40 - reg_w) / 2, 255, "Кворум (2/3)", size=10, color="#16a34a", bold=True))
    
    p.append(rect(40, 330, W - 80, 125, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(60, 354, "Принципи запобігання Split-Brain (розходженню станів):", size=13, color=INK, bold=True, anchor="start"))
    
    rules = [
        ("Непарна кількість голосів:", "Кворум (N/2 + 1) гарантує, що лише один сегмент мережі може зібрати більшість голосів.", "#2563eb"),
        ("Ізоляція старої ноди (Fencing):", "STONITH / відкликання IAM-прав унеможливлює запис даних старим лідером в ізольованому ЦОД.", "#dc2626"),
        ("Оренда з таймаутом (TTL Lease):", "Лідер автоматично втрачає право на запис, якщо не може подовжити оренду в арбітра за T_lease.", "#d97706"),
    ]
    
    ry = 378
    for r_title, r_desc, r_col in rules:
        p.append(circle(65, ry, 3.5, fill=r_col, stroke=r_col, sw=1.0))
        p.append(text(80, ry + 4, r_title, size=11.5, color=INK, bold=True, anchor="start"))
        p.append(text(290, ry + 4, r_desc, size=11, color=MUTED, anchor="start"))
        ry += 22
        
    render(os.path.join(OUT, "split-brain-and-fencing.svg"), W, H, *p)

def main():
    fig_rpo_rto_timeline()
    fig_dr_strategies_comparison()
    fig_pitr_wal_replay()
    fig_split_brain_and_fencing()
    print("All figures generated successfully.")

if __name__ == "__main__":
    main()
