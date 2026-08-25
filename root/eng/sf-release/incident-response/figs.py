# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Життєвий цикл інциденту (State Machine) ─────────────────────────
def fig_incident_lifecycle():
    W, H = 960, 430
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    stages = [
        ("1. Виявлення", "Спрацьовування SLO-алерту\nТаймер MTTA (≤5 хв)\nАвтоперевірка сигналу", "#fee2e2", "#dc2626"),
        ("2. Тріаж і виклик", "Оцінка тяжкості (SEV-1..4)\nПейджинг чергових\nЕскалація на ліда", "#ffedd5", "#ea580c"),
        ("3. Мобілізація", "Призначення командира (IC)\nВідкриття каналу й мосту\nРозподіл обов'язків", "#fef9c3", "#ca8a04"),
        ("4. Пом'якшення", "Пріоритет: зупинити збій\nВідкіт / Прапорці / Shedding\nФіксація доказів", "#dbeafe", "#2563eb"),
        ("5. Стабілізація", "Контроль відновлення SLI\nПеріод витримки (soak)\nПідтвердження норми", "#e0e7ff", "#4f46e5"),
        ("6. Закриття й огляд", "Оголошення All-Clear\nЗняття тимчасових правок\nБезвинний постмортем", "#dcfce7", "#16a34a"),
    ]
    
    box_w = 142.0
    box_h = 125.0
    gap = 14.0
    start_x = 22.0
    y_pos = 65.0
    
    # Горизонтальна часова вісь
    axis_y = 230.0
    p.append(line(24, axis_y, W - 35, axis_y, color=LINE, sw=1.6))
    p.append(arrow(W - 65, axis_y, W - 25, axis_y, color=LINE, sw=1.8))
    p.append(text(W - 40, axis_y - 10, "Час інциденту →", size=12, color=INK, bold=True, anchor="end"))
    
    for i, (title_text, desc_text, bg_col, stroke_col) in enumerate(stages):
        x = start_x + i * (box_w + gap)
        
        p.append(rect(x, y_pos, box_w, box_h, fill=bg_col, stroke=stroke_col, sw=1.6, rx=6))
        p.append(text(x + box_w / 2, y_pos + 24, title_text, size=12.5, color=stroke_col, bold=True))
        
        lines = desc_text.split("\n")
        p.append(mtext(x + box_w / 2, y_pos + 52, lines, size=10.5, color=INK, lh=1.35))
        
        cx = x + box_w / 2
        p.append(line(cx, y_pos + box_h, cx, axis_y, color=stroke_col, sw=1.2, dash="3 3"))
        p.append(circle(cx, axis_y, 4.0, fill=stroke_col, stroke="#ffffff", sw=1.5))
        
        if i < len(stages) - 1:
            next_x = start_x + (i + 1) * (box_w + gap)
            p.append(arrow(x + box_w + 2, y_pos + box_h / 2, next_x - 2, y_pos + box_h / 2, color=LINE, sw=1.3))
            
    # Нижня інформаційна панель
    panel_y = 265.0
    panel_h = 140.0
    p.append(rect(22, panel_y, W - 44, panel_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(38, panel_y + 24, "Ключові інваріанти управління інцидентом на кожному кроці:", size=12.5, color=INK, bold=True, anchor="start"))
    
    rows = [
        ("Операційний темп (Cadence):", "Командир синхронізує статус кожні 10-15 хв; фіксує поточні гіпотези та призначає виконавців", NEG),
        ("Пріоритет пом'якшення:", "Спочатку відновлюємо доступність користувачам (rollback, traffic shedding), глибокий дебаг — після", POS),
        ("Єдине джерело правди:", "Один канал Slack (#inc-YYYYMMDD-slug) та один голосовий міст; сторонні обговорення заборонені", FIELD),
        ("Перехід до навчання:", "Інцидент завершується не закриттям тікета, а постмортемом і впровадженням системних запобіжників", MUTED),
    ]
    
    ry = panel_y + 48
    for label_txt, desc_txt, col in rows:
        p.append(circle(44, ry, 3.5, fill=col, stroke=col, sw=1.0))
        p.append(text(56, ry + 4, label_txt, size=11.5, color=INK, bold=True, anchor="start"))
        p.append(text(255, ry + 4, desc_txt, size=11.5, color=MUTED, anchor="start"))
        ry += 22
        
    render(os.path.join(OUT, "incident-lifecycle-state-machine.svg"), W, H, *p)

# ── Фіг. 2: Ієрархія командної структури (ICS) ──────────────────────────────
def fig_incident_command_hierarchy():
    W, H = 960, 460
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # 1. Incident Commander (Верхній центральний блок)
    ic_w, ic_h = 320.0, 80.0
    ic_x = (W - ic_w) / 2
    ic_y = 35.0
    p.append(rect(ic_x, ic_y, ic_w, ic_h, fill="#eff6ff", stroke="#2563eb", sw=1.8, rx=8))
    p.append(text(ic_x + ic_w / 2, ic_y + 26, "Командир інциденту (Incident Commander)", size=13, color="#1d4ed8", bold=True))
    p.append(mtext(ic_x + ic_w / 2, ic_y + 50, ["Ухвалює рішення, веде темп, делегує завдання", "Сам код НЕ пише і в терміналі НЕ дебажить"], size=11, color=INK, lh=1.3))
    
    # 2. Три ролі середнього рівня
    mid_y = 175.0
    m_box_w = 260.0
    m_box_h = 95.0
    
    # Ліворуч: Operations / Tech Lead
    ops_x = 45.0
    p.append(rect(ops_x, mid_y, m_box_w, m_box_h, fill="#fef2f2", stroke="#dc2626", sw=1.6, rx=6))
    p.append(text(ops_x + m_box_w / 2, mid_y + 24, "Технічний координатор (Ops Lead)", size=12.5, color="#b91c1c", bold=True))
    p.append(mtext(ops_x + m_box_w / 2, mid_y + 48, ["Керує інженерними діями", "Координує відкоти та конфігурації", "Розподіляє задачі між експертами"], size=10.5, color=INK, lh=1.3))
    
    # Центр: Scribe / Timeline Keeper
    scr_x = (W - m_box_w) / 2
    p.append(rect(scr_x, mid_y, m_box_w, m_box_h, fill="#f5f3ff", stroke="#7c3aed", sw=1.6, rx=6))
    p.append(text(scr_x + m_box_w / 2, mid_y + 24, "Хронікер / Скрайб (Scribe)", size=12.5, color="#6d28d9", bold=True))
    p.append(mtext(scr_x + m_box_w / 2, mid_y + 48, ["Фіксує хронологію подій та рішень", "Зберігає графіки метрик і логи", "Готує основу для постмортему"], size=10.5, color=INK, lh=1.3))
    
    # Праворуч: Comms Lead
    com_x = W - m_box_w - 45.0
    p.append(rect(com_x, mid_y, m_box_w, m_box_h, fill="#ecfdf5", stroke="#059669", sw=1.6, rx=6))
    p.append(text(com_x + m_box_w / 2, mid_y + 24, "Координатор комунікацій (Comms)", size=12.5, color="#047857", bold=True))
    p.append(mtext(com_x + m_box_w / 2, mid_y + 48, ["Оновлює публічну StatusPage", "Інформує підтримку та менеджмент", "Захищає команду від відволікань"], size=10.5, color=INK, lh=1.3))
    
    # Зв'язки від IC до середнього рівня
    ic_cx = ic_x + ic_w / 2
    ic_bottom = ic_y + ic_h
    p.append(arrow(ic_cx, ic_bottom, ops_x + m_box_w / 2, mid_y - 2, color="#2563eb", sw=1.5))
    p.append(arrow(ic_cx, ic_bottom, scr_x + m_box_w / 2, mid_y - 2, color="#2563eb", sw=1.5))
    p.append(arrow(ic_cx, ic_bottom, com_x + m_box_w / 2, mid_y - 2, color="#2563eb", sw=1.5))
    
    # 3. Нижній рівень: Профільні експерти (SMEs)
    sme_y = 330.0
    sme_box_w = 200.0
    sme_box_h = 90.0
    gap_sme = 22.0
    start_sme_x = (W - (4 * sme_box_w + 3 * gap_sme)) / 2
    
    smes = [
        ("Бази даних (DBA)", "Блокування, реплікація,\nпули з'єднань, I/O", "#fff7ed", "#ea580c"),
        ("Платформа / K8s", "Поди, автоскейл, ноди,\nмаршрутизація Ingress", "#f0fdf4", "#16a34a"),
        ("Сервісна логіка", "Помилки релізу, баги,\nсторонні API, черги", "#fdf2f8", "#db2777"),
        ("Мережа та безпека", "Firewall, DNS, TLS,\nDDoS-атаки, CDN", "#f8fafc", "#475569")
    ]
    
    for j, (sme_title, sme_desc, bg_c, str_c) in enumerate(smes):
        sx = start_sme_x + j * (sme_box_w + gap_sme)
        p.append(rect(sx, sme_y, sme_box_w, sme_box_h, fill=bg_c, stroke=str_c, sw=1.4, rx=6))
        p.append(text(sx + sme_box_w / 2, sme_y + 24, sme_title, size=11.5, color=str_c, bold=True))
        lines = sme_desc.split("\n")
        p.append(mtext(sx + sme_box_w / 2, sme_y + 48, lines, size=10, color=INK, lh=1.35))
        
        # Стрілка від Ops Lead до SME
        p.append(arrow(ops_x + m_box_w / 2, mid_y + m_box_h, sx + sme_box_w / 2, sme_y - 2, color="#dc2626", sw=1.2))
        
    render(os.path.join(OUT, "incident-command-hierarchy.svg"), W, H, *p)

# ── Фіг. 3: Пом'якшення проти пошуку першопричини ────────────────────────────
def fig_mitigation_vs_root_cause():
    W, H = 960, 440
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Верхня доріжка: Екстрене реагування (Пом'якшення)
    top_y = 35.0
    p.append(rect(24, top_y, W - 48, 175, fill="#f0fdf4", stroke="#86efac", sw=1.4, rx=6))
    p.append(text(42, top_y + 24, "Доріжка 1: Негайне пом'якшення («Зупинити кровотечу» під час інциденту)", size=13, color="#15803d", bold=True, anchor="start"))
    
    actions_top = [
        ("Відкіт деплою", "Повернення на стабільну\nверсію бінарника/образу", "#ffffff", "#16a34a"),
        ("Прапорці функцій", "Миттєве вимкнення збійної\nфічі без перезапуску коду", "#ffffff", "#16a34a"),
        ("Скидання навантаження", "Traffic shedding, ліміти,\nвідсікання некритичних фонів", "#ffffff", "#16a34a"),
        ("Ізоляція / Failover", "Перемикання на резервний\nрегіон або репліку БД", "#ffffff", "#16a34a"),
    ]
    
    bx_w = 205.0
    bx_h = 95.0
    gap = 18.0
    bx_x = 42.0
    bx_y = top_y + 52.0
    
    for title_txt, desc_txt, bg_c, str_c in actions_top:
        p.append(rect(bx_x, bx_y, bx_w, bx_h, fill=bg_c, stroke=str_c, sw=1.3, rx=6))
        p.append(text(bx_x + bx_w / 2, bx_y + 24, title_txt, size=12, color=str_c, bold=True))
        lines = desc_txt.split("\n")
        p.append(mtext(bx_x + bx_w / 2, bx_y + 48, lines, size=10.5, color=INK, lh=1.35))
        bx_x += bx_w + gap
        
    # Нижня доріжка: Форензика та аналіз (Пошук першопричини)
    bot_y = 230.0
    p.append(rect(24, bot_y, W - 48, 175, fill="#eff6ff", stroke="#93c5fd", sw=1.4, rx=6))
    p.append(text(42, bot_y + 24, "Доріжка 2: Збереження доказів і форензика (Аналіз першопричини)", size=13, color="#1d4ed8", bold=True, anchor="start"))
    
    actions_bot = [
        ("Дампи пам'яті / Core", "Збереження heap-дампа збійного\nпроцесу перед перезапуском", "#ffffff", "#2563eb"),
        ("Ізоляція вузла", "Вилучення поди з балансувальника\nбез знищення контейнера", "#ffffff", "#2563eb"),
        ("Зрізи телеметрії", "Експорт детальних трейсів,\nлогів і графіка черг", "#ffffff", "#2563eb"),
        ("Безвинний постмортем", "Аналіз системних факторів\nта впровадження запобіжників", "#ffffff", "#2563eb"),
    ]
    
    bx_x = 42.0
    bx_y = bot_y + 52.0
    for title_txt, desc_txt, bg_c, str_c in actions_bot:
        p.append(rect(bx_x, bx_y, bx_w, bx_h, fill=bg_c, stroke=str_c, sw=1.3, rx=6))
        p.append(text(bx_x + bx_w / 2, bx_y + 24, title_txt, size=12, color=str_c, bold=True))
        lines = desc_txt.split("\n")
        p.append(mtext(bx_x + bx_w / 2, bx_y + 48, lines, size=10.5, color=INK, lh=1.35))
        bx_x += bx_w + gap
        
    render(os.path.join(OUT, "mitigation-vs-root-cause.svg"), W, H, *p)

# ── Фіг. 4: Хронологія та метрики інциденту ──────────────────────────────────
def fig_incident_metrics_timeline():
    W, H = 960, 390
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Заголовок
    p.append(text(30, 38, "Структура часу інциденту: від зародження дефекту до повного одужання", size=13, color=INK, bold=True, anchor="start"))
    
    # Головна часова шкала
    axis_y = 140.0
    axis_x0 = 40.0
    axis_x1 = W - 50.0
    p.append(line(axis_x0, axis_y, axis_x1, axis_y, color=LINE, sw=2.0))
    p.append(arrow(axis_x1 - 30, axis_y, axis_x1, axis_y, color=LINE, sw=2.2))
    p.append(text(axis_x1, axis_y - 12, "Час →", size=12, color=INK, bold=True, anchor="end"))
    
    # Точки часу
    pts = [
        (60.0, "T0: Початок збою", "Реліз з багом / аварія"),
        (220.0, "T1: Детекція", "Спрацював алерт"),
        (370.0, "T2: Реакція", "Черговий підтвердив (ACK)"),
        (560.0, "T3: Діагноз", "Знайдено вектор пом'якшення"),
        (740.0, "T4: Пом'якшення", "SLI в нормі (Mitigated)"),
        (880.0, "T5: Закриття", "Повний фікс (Resolved)")
    ]
    
    for px, label_t, desc_t in pts:
        p.append(circle(px, axis_y, 5.0, fill=POS if px < 740 else FIELD, stroke="#ffffff", sw=1.5))
        p.append(text(px, axis_y + 22, label_t, size=11, color=INK, bold=True))
        p.append(text(px, axis_y + 38, desc_t, size=9.5, color=MUTED))
        p.append(line(px, axis_y - 15, px, axis_y + 10, color=MUTED, sw=1.0, dash="2 2"))
        
    # Інтервали (MTTD, MTTA, MTTI, MTTM)
    intervals = [
        (60.0, 220.0, 85.0, "MTTD (Виявлення)", "#dc2626"),
        (220.0, 370.0, 65.0, "MTTA (Реакція)", "#ea580c"),
        (370.0, 560.0, 85.0, "MTTI (Локалізація)", "#2563eb"),
        (560.0, 740.0, 65.0, "MTTM (Пом'якшення)", "#16a34a"),
    ]
    
    for x1, x2, iy, label_iv, col in intervals:
        p.append(line(x1, iy, x2, iy, color=col, sw=2.0))
        p.append(line(x1, iy - 6, x1, iy + 6, color=col, sw=2.0))
        p.append(line(x2, iy - 6, x2, iy + 6, color=col, sw=2.0))
        p.append(text((x1 + x2) / 2, iy - 10, label_iv, size=11, color=col, bold=True))
        
    # Великий інтервал MTTM (Customer Outage) і MTTR
    p.append(line(60.0, 195.0, 740.0, 195.0, color="#dc2626", sw=1.8, dash="4 3"))
    p.append(line(60.0, 190.0, 60.0, 200.0, color="#dc2626", sw=1.8))
    p.append(line(740.0, 190.0, 740.0, 200.0, color="#dc2626", sw=1.8))
    p.append(text(400.0, 212.0, "Час впливу на користувачів (Customer Impact Duration) = MTTD + MTTA + MTTI + MTTM", size=11.5, color="#dc2626", bold=True))
    
    # Нижня довідкова панель
    panel_y = 235.0
    panel_h = 130.0
    p.append(rect(24, panel_y, W - 48, panel_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(38, panel_y + 24, "Метрики ефективності процесу реагування:", size=12.5, color=INK, bold=True, anchor="start"))
    
    met_rows = [
        ("MTTD (Mean Time to Detect):", "Швидкість спрацьовування моніторингу; зменшується за рахунок якісних SLO-алертів", "#dc2626"),
        ("MTTA (Mean Time to Acknowledge):", "Час до взяття інциденту черговим інженером; ціль: ≤5 хв для SEV-1", "#ea580c"),
        ("MTTM (Mean Time to Mitigate):", "Час до повернення сервісу до працездатного стану; головна ціль екстреного реагування", "#16a34a"),
        ("MTBF (Mean Time Between Failures):", "Середній час між аваріями; зростає завдяки системним діям за підсумками постмортемів", "#2563eb")
    ]
    
    ry = panel_y + 48
    for lbl, desc, col in met_rows:
        p.append(circle(44, ry, 3.5, fill=col, stroke=col, sw=1.0))
        p.append(text(56, ry + 4, lbl, size=11.5, color=INK, bold=True, anchor="start"))
        p.append(text(310, ry + 4, desc, size=11.5, color=MUTED, anchor="start"))
        ry += 20
        
    render(os.path.join(OUT, "incident-metrics-timeline.svg"), W, H, *p)

if __name__ == "__main__":
    fig_incident_lifecycle()
    fig_incident_command_hierarchy()
    fig_mitigation_vs_root_cause()
    fig_incident_metrics_timeline()
    print("Figures generated successfully.")
