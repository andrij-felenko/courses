# -*- coding: utf-8 -*-
"""
figs.py — генератор SVG-фігур для теми dh-macro-choice
(DH: Макроархітектурний вибір системи Digital Homes)
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')

def build_fig1():
    """Фігура 1: dh-modular-monolith-arch.svg
    Архітектура модульного моноліту Digital Homes (cloud-core):
    модулі всередині єдиного процесу, контракти, шина подій та ізольовані схеми СУБД.
    """
    frags = []
    
    # Заголовок / контур моноліта
    frags.append(rect(10, 10, 840, 500, fill="#f8fafc", stroke="#334155", sw=2, rx=12))
    frags.append(text(430, 38, "Єдиний деплоймент-модуль: cloud-core (Модульний моноліт DH)", size=17, bold=True, color="#0f172a"))
    frags.append(line(30, 48, 830, 48, color="#cbd5e1", sw=1.2))

    # Клієнти / Ingress зверху
    frags.append(rect(240, 62, 380, 40, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(text(430, 87, "Клієнти (Mobile / Web / Hub API) → Load Balancer", size=13, bold=True, color="#0369a1"))
    frags.append(arrow(430, 102, 430, 122, color="#0284c7", sw=2))

    # Публічна точка входу (API Controllers / Gateways in-process)
    frags.append(rect(180, 122, 500, 34, fill="#f1f5f9", stroke="#475569", sw=1.2, rx=4))
    frags.append(text(430, 143, "Застосункові маршрутизатори (HTTP / gRPC Ingress)", size=12, color="#334155"))
    frags.append(arrow(430, 156, 430, 176, color="#475569", sw=1.5))

    # Внутрішня шина подій (In-Memory EventBus)
    frags.append(rect(60, 176, 740, 36, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(430, 198, "Внутрішньопроцесна шина подій (In-Memory EventBus)", size=13, bold=True, color="#92400e"))

    # 4 основні модулі в ряд
    modules = [
        ("DeviceRegistry", "Пристрої та Shadow", "#dbeafe", "#1d4ed8"),
        ("AutomationEngine", "Двигун правил", "#dcfce7", "#15803d"),
        ("TelemetryIngest", "Інжест метрик", "#e0e7ff", "#4338ca"),
        ("UserBilling", "Користувачі й Білінг", "#fce7f3", "#be185d")
    ]

    mod_w = 175
    mod_gap = 15
    start_x = 55
    y_mod = 236

    for i, (name, desc, bg_c, border_c) in enumerate(modules):
        x = start_x + i * (mod_w + mod_gap)
        # Модульний прямокутник
        frags.append(rect(x, y_mod, mod_w, 130, fill=bg_c, stroke=border_c, sw=1.8, rx=8))
        frags.append(text(x + mod_w/2, y_mod + 24, name, size=13, bold=True, color=border_c))
        frags.append(text(x + mod_w/2, y_mod + 42, desc, size=11, color="#334155"))
        frags.append(line(x + 10, y_mod + 52, x + mod_w - 10, y_mod + 52, color=border_c, sw=1))
        
        # Публічний контракт
        frags.append(rect(x + 10, y_mod + 58, mod_w - 20, 24, fill="#ffffff", stroke=border_c, sw=1, rx=3))
        frags.append(text(x + mod_w/2, y_mod + 74, "Public Contract API", size=10, bold=True, color=border_c))
        
        # Внутрішній код
        frags.append(text(x + mod_w/2, y_mod + 98, "Internal Domain Logic", size=10, italic=True, color="#475569"))
        frags.append(text(x + mod_w/2, y_mod + 116, "Private Repositories", size=10, italic=True, color="#475569"))

        # Стрілка зв'язку з шиною
        frags.append(line(x + mod_w/2, 212, x + mod_w/2, y_mod, color="#d97706", sw=1.5, dash="3,3"))

        # Стрілка вниз до СУБД
        frags.append(arrow(x + mod_w/2, y_mod + 130, x + mod_w/2, 400, color="#475569", sw=1.5))

    # Схема СУБД внизу (Логічна ізоляція)
    frags.append(rect(40, 400, 780, 90, fill="#f1f5f9", stroke="#0f172a", sw=1.8, rx=8))
    frags.append(text(430, 422, "Спільний кластер PostgreSQL (Логічна ізоляція схем)", size=14, bold=True, color="#0f172a"))
    
    schemas = [
        ("schema: devices", 55, 434),
        ("schema: automation", 245, 434),
        ("schema: telemetry", 435, 434),
        ("schema: billing", 625, 434)
    ]
    for sch_name, sx, sy in schemas:
        frags.append(rect(sx, sy, 175, 42, fill="#ffffff", stroke="#64748b", sw=1.2, rx=4))
        frags.append(text(sx + 87.5, sy + 25, sch_name, size=12, bold=True, color="#334155"))

    # Позначення про заборону крос-foreign-keys
    frags.append(text(430, 484, "Заборонено: міжсхемні SQL JOIN та зовнішні ключі (Foreign Keys)", size=11, bold=True, color="#c0392b"))

    render(os.path.join(IMG_DIR, 'dh-modular-monolith-arch.svg'), 860, 520, *frags)

def build_fig2():
    """Фігура 2: extraction-triggers.svg
    Дерево прийняття рішень: коли виносити модуль з моноліту DH у мікросервіс.
    """
    frags = []

    frags.append(rect(10, 10, 820, 420, fill="#ffffff", stroke="#334155", sw=1.5, rx=10))
    frags.append(text(420, 36, "Дерево прийняття рішення: Коли виносити модуль DH у сервіс", size=16, bold=True, color="#0f172a"))

    # Вхідний вузол
    box1, w1, h1 = textbox(420, 80, "Потреба у зміні / масштабуванні модуля DH", size=13, bold=True, fill="#e2e8f0", stroke="#334155")
    frags.append(box1)

    # Три перевірки-критерії в ряд
    y_crit = 180
    crits = [
        ("1. Асиметрія ресурсів", "Важке CPU/Video/RAM?\nБлокує ядро моноліту?", 160),
        ("2. Асиметрія масштабу", "100k+ подій/сек?\nПотрібна інша СУБД?", 420),
        ("3. Ізоляція команд", "Окрема команда >8 осіб?\nНезалежний реліз?", 680)
    ]

    for title, desc, cx in crits:
        frags.append(arrow(420, 105, cx, y_crit - 30, color="#475569", sw=1.5))
        bx, bw, bh = textbox(cx, y_crit, f"{title}\n{desc}", size=11, fill="#f8fafc", stroke="#0284c7", sw=1.5)
        frags.append(bx)

        # Результат НІ (Лишаємо в моноліті)
        frags.append(arrow(cx, y_crit + 30, cx - 40, y_crit + 100, color="#27ae60", sw=1.5))
        frags.append(text(cx - 50, y_crit + 60, "НІ", size=11, bold=True, color="#27ae60"))
        res_no, _, _ = textbox(cx - 50, y_crit + 120, "Лишаємо в\ncloud-core", size=11, fill="#dcfce7", stroke="#15803d", color="#15803d")
        frags.append(res_no)

        # Результат ТАК (Виносимо в окремий сервіс)
        frags.append(arrow(cx, y_crit + 30, cx + 40, y_crit + 100, color="#c0392b", sw=1.5))
        frags.append(text(cx + 50, y_crit + 60, "ТАК", size=11, bold=True, color="#c0392b"))
        res_yes, _, _ = textbox(cx + 50, y_crit + 120, "Виносимо в\nокремий сервіс", size=11, fill="#fee2e2", stroke="#b91c1c", color="#b91c1c")
        frags.append(res_yes)

    # Приклади знизу
    frags.append(line(30, 340, 810, 340, color="#cbd5e1", sw=1))
    frags.append(text(420, 365, "Приклади у Digital Homes:", size=13, bold=True, color="#0f172a"))
    frags.append(text(210, 395, "✓ Video Ingest (RTSP/Transcode) → Окремий сервіс", size=11, bold=True, color="#b91c1c"))
    frags.append(text(630, 395, "✓ DeviceRegistry / Automation → У модульному моноліті", size=11, bold=True, color="#15803d"))

    render(os.path.join(IMG_DIR, 'extraction-triggers.svg'), 840, 440, *frags)

def build_fig3():
    """Фігура 3: tradeoff-spectrum.svg
    Матриця компромісів та спектр макроархітектур для DH.
    """
    frags = []

    frags.append(rect(10, 10, 820, 460, fill="#ffffff", stroke="#334155", sw=1.5, rx=10))
    frags.append(text(420, 36, "Спектр макроархітектур та компроміси для Digital Homes", size=16, bold=True, color="#0f172a"))

    # Спектральна вісь
    frags.append(line(50, 70, 790, 70, color="#94a3b8", sw=3))
    
    architectures = [
        ("Неструктурований\nмоноліт", 130, "#ef4444"),
        ("Модульний\nмоноліт (DH v3)", 350, "#10b981"),
        ("Сервісно-орієнтована\n(SOA / 3-5 сервісів)", 570, "#3b82f6"),
        ("12+ Дрібних\nмікросервісів", 730, "#f59e0b")
    ]

    for name, pos_x, col in architectures:
        frags.append(circle(pos_x, 70, 8, fill=col, stroke="#ffffff", sw=2))
        frags.append(mtext(pos_x, 92, name, size=11, bold=True, color="#0f172a"))

    # Позначка вибору DH
    frags.append(rect(240, 52, 220, 36, fill="none", stroke="#10b981", sw=2.5, rx=6))
    frags.append(text(350, 44, "★ ОПТИМУМ ДЛЯ DH", size=10, bold=True, color="#047857"))

    # Матриця компромісів
    y_table = 160
    headers = ["Вимір компромісу", "Неструктурований", "Модульний моноліт", "Мікросервіси"]
    col_w = [220, 180, 200, 180]
    col_x = [40, 260, 440, 640]

    # Шапка таблиці
    frags.append(rect(30, y_table, 780, 32, fill="#0f172a", stroke="#0f172a", sw=1, rx=4))
    for i, h_text in enumerate(headers):
        align = "left" if i == 0 else "center"
        tx = col_x[i] if i == 0 else col_x[i] + col_w[i]/2
        frags.append(text(tx, y_table + 21, h_text, size=12, bold=True, color="#ffffff", anchor=align))

    rows = [
        ("Мережева затримка (IPC)", "Низька (2-50 нс)", "Низька (2-50 нс)", "Висока (5-150 мс)"),
        ("Транзакційна консистентність", "Сувора ACID", "Сувора ACID", "Кінцева (Saga/Outbox)"),
        ("Операційна складність", "Мінімальна", "Низька (1 binary)", "Критична (K8s/Mesh)"),
        ("Швидкість розробки (12 осіб)", "Швидка спочатку", "Максимальна", "Повільна (інфра-такс)"),
        ("Чіткість доменних меж", "Відсутня (Хаос)", "Висока (Контракти)", "Жорстка (Мережева)")
    ]

    for r_idx, row in enumerate(rows):
        ry = y_table + 32 + r_idx * 50
        bg_r = "#f8fafc" if r_idx % 2 == 0 else "#ffffff"
        frags.append(rect(30, ry, 780, 50, fill=bg_r, stroke="#e2e8f0", sw=1, rx=0))
        
        for c_idx, val in enumerate(row):
            align = "left" if c_idx == 0 else "center"
            tx = col_x[c_idx] if c_idx == 0 else col_x[c_idx] + col_w[c_idx]/2
            
            # Підсвічування колонки Модульний моноліт
            font_c = "#0f172a"
            is_bold = False
            if c_idx == 2:
                font_c = "#047857"
                is_bold = True

            frags.append(text(tx, ry + 30, val, size=11, color=font_c, bold=is_bold, anchor=align))

    render(os.path.join(IMG_DIR, 'tradeoff-spectrum.svg'), 840, 480, *frags)

def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    build_fig1()
    build_fig2()
    build_fig3()
    print("Figures generated successfully in img/")

if __name__ == "__main__":
    main()
