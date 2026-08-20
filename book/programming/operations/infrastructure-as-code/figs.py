# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Контур узгодження стану (IaC Reconciliation Loop) ─────────────────
def fig_iac_reconciliation_loop():
    W, H = 1000, 560
    p = []
    
    # Фон та заголовок
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 40, "Контур узгодження стану інфраструктури (Reconciliation Loop)", size=16, color=INK, bold=True))
    
    bw, bh = 220, 110
    
    # Блок 1: Бажаний стан у Git (зліва вгорі)
    x1, y1 = 40, 75
    p.append(rect(x1, y1, bw, bh, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    p.append(text(x1 + bw / 2, y1 + 24, "1. Бажаний стан (Desired)", size=13, color="#2563eb", bold=True))
    p.append(mtext(x1 + bw / 2, y1 + 50, [
        "Декларативний код у Git",
        "HCL / YAML / TypeScript",
        "Версійована схема ресурсів"
    ], size=11, color=INK, lh=1.35))
    
    # Блок 2: Реальний стан хмари (праворуч вгорі)
    x2, y2 = 740, 75
    p.append(rect(x2, y2, bw, bh, fill="#fdf2f8", stroke="#db2777", sw=1.6, rx=6))
    p.append(text(x2 + bw / 2, y2 + 24, "2. Актуальний стан хмари", size=13, color="#db2777", bold=True))
    p.append(mtext(x2 + bw / 2, y2 + 50, [
        "Cloud API (AWS, GCP, Azure)",
        "Фізичні ресурси (VPC, DB)",
        "Опитування через Refresh"
    ], size=11, color=INK, lh=1.35))
    
    # Блок 3: Рушій звірки та планування (центр)
    x3, y3 = 360, 195
    bw_mid, bh_mid = 280, 125
    p.append(rect(x3, y3, bw_mid, bh_mid, fill="#f8fafc", stroke="#475569", sw=1.8, rx=8))
    p.append(text(x3 + bw_mid / 2, y3 + 24, "3. Рушій планування (Plan)", size=14, color="#1e293b", bold=True))
    p.append(mtext(x3 + bw_mid / 2, y3 + 52, [
        "Звірка: Desired vs State vs Real",
        "Обчислення дифу (Diff Engine)",
        "Побудова графа залежностей (DAG)",
        "План дій: Create, Update, Replace"
    ], size=11, color=INK, lh=1.35))
    
    # Блок 4: Блокування та безпека (зліва внизу)
    x4, y4 = 40, 395
    p.append(rect(x4, y4, bw, bh, fill="#fffbeb", stroke="#d97706", sw=1.6, rx=6))
    p.append(text(x4 + bw / 2, y4 + 24, "4. Блокування стану", size=13, color="#d97706", bold=True))
    p.append(mtext(x4 + bw / 2, y4 + 50, [
        "Distributed State Lock",
        "Захист від гонитви (Race)",
        "Блокування у DynamoDB / S3"
    ], size=11, color=INK, lh=1.35))
    
    # Блок 5: Виконання змін (Apply) (праворуч внизу)
    x5, y5 = 740, 395
    p.append(rect(x5, y5, bw, bh, fill="#f0fdf4", stroke="#16a34a", sw=1.6, rx=6))
    p.append(text(x5 + bw / 2, y5 + 24, "5. Виконання (Apply)", size=13, color="#16a34a", bold=True))
    p.append(mtext(x5 + bw / 2, y5 + 50, [
        "CRUD-виклики до Cloud API",
        "Паралелізм за рівнями DAG",
        "Атомарний запис нового стану"
    ], size=11, color=INK, lh=1.35))
    
    # Зв'язки і стрілки
    # 1 -> 3
    p.append(arrow(x1 + bw, y1 + bh / 2, x3, y3 + 30, color=LINE, sw=1.8))
    p.append(text(x1 + bw + 45, y1 + bh / 2 + 15, "Опис цілі", size=11, color=MUTED))
    
    # 2 -> 3
    p.append(arrow(x2, y2 + bh / 2, x3 + bw_mid, y3 + 30, color=LINE, sw=1.8))
    p.append(text(x2 - 45, y2 + bh / 2 + 15, "Телеметрія API", size=11, color=MUTED))
    
    # 3 -> 4
    p.append(arrow(x3 + 30, y3 + bh_mid, x4 + bw / 2, y4, color=LINE, sw=1.8))
    p.append(text(x4 + bw / 2 + 65, y4 - 20, "Захоплення локу", size=11, color=MUTED))
    
    # 4 -> 5
    p.append(arrow(x4 + bw, y4 + bh / 2, x5, y5 + bh / 2, color=LINE, sw=1.8))
    p.append(text((x4 + bw + x5) / 2, y4 + bh / 2 - 12, "Дозвіл на мутацію за планом дій", size=11, color=MUTED))
    
    # 5 -> 2 (Зворотний зв'язок)
    p.append(arrow(x5 + bw / 2, y5, x2 + bw / 2, y2 + bh, color="#16a34a", sw=2.0))
    p.append(text(x5 + bw / 2 + 80, (y5 + y2 + bh) / 2, "Мутація інфраструктури", size=11, color="#16a34a"))
    
    render(os.path.join(OUT, "iac-reconciliation-loop.svg"), W, H, *p)


# ── Фіг. 2: Декларативний проти імперативного підходу ─────────────────────────
def fig_declarative_vs_imperative():
    W, H = 1000, 520
    p = []
    
    # Фон та заголовок
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Імперативний скриптинг проти Декларативного контуру", size=16, color=INK, bold=True))
    
    # Ліва колонка: Імперативний
    col_w = 440
    lx = 40
    p.append(rect(lx, 70, col_w, 420, fill="#fff5f5", stroke="#e03131", sw=1.6, rx=8))
    p.append(text(lx + col_w / 2, 98, "ІМПЕРАТИВНИЙ ПІДХІД (Як робити)", size=14, color="#c92a2a", bold=True))
    
    # Кроки імперативного
    steps_imp = [
        ("1. aws ec2 create-vpc --cidr 10.0.0.0/16", "#ffffff"),
        ("2. aws ec2 create-subnet --vpc-id $VPC_ID", "#ffffff"),
        ("3. [АВАРІЯ МЕРЕЖІ: таймаут на кроці 3]", "#ffe3e3"),
        ("4. Повторний запуск: помилка «VpcAlreadyExists»", "#ffe3e3"),
        ("5. Підсумок: завислі ресурси, напівробочий стан", "#ffe3e3")
    ]
    sy = 125
    for txt, bg in steps_imp:
        p.append(rect(lx + 20, sy, col_w - 40, 48, fill=bg, stroke="#adb5bd", sw=1.0, rx=4))
        p.append(text(lx + 35, sy + 28, txt, size=11, color=INK, anchor="start"))
        sy += 58
    
    p.append(text(lx + col_w / 2, 445, "• Порядок жорстко зафіксований у коді", size=11.5, color="#c92a2a", bold=True))
    p.append(text(lx + col_w / 2, 468, "• Немає ідемпотентності та авто-відкату", size=11.5, color="#c92a2a", bold=True))
    
    # Права колонка: Декларативний
    rx_col = 520
    p.append(rect(rx_col, 70, col_w, 420, fill="#f0fdf4", stroke="#2f9e44", sw=1.6, rx=8))
    p.append(text(rx_col + col_w / 2, 98, "ДЕКЛАРАТИВНИЙ ПІДХІД (Що отримати)", size=14, color="#2b8a3e", bold=True))
    
    # Кроки декларативного
    steps_dec = [
        ("1. resource \"vpc\" { cidr = \"10.0.0.0/16\" }", "#ffffff"),
        ("2. resource \"subnet\" { vpc_id = vpc.id }", "#ffffff"),
        ("3. Рушій будує DAG та вираховує мінімальний Diff", "#ffffff"),
        ("4. Аварія? Повторний запуск просто доробляє Diff", "#dcfce7"),
        ("5. Підсумок: гарантована збіжність до цілі (Idempotency)", "#dcfce7")
    ]
    sy = 125
    for txt, bg in steps_dec:
        p.append(rect(rx_col + 20, sy, col_w - 40, 48, fill=bg, stroke="#adb5bd", sw=1.0, rx=4))
        p.append(text(rx_col + 35, sy + 28, txt, size=11, color=INK, anchor="start"))
        sy += 58
        
    p.append(text(rx_col + col_w / 2, 445, "• Рушій сам визначає правильний порядок дій", size=11.5, color="#2b8a3e", bold=True))
    p.append(text(rx_col + col_w / 2, 468, "• Повний контроль за станом та безпечне злиття", size=11.5, color="#2b8a3e", bold=True))
    
    render(os.path.join(OUT, "declarative-vs-imperative.svg"), W, H, *p)


# ── Фіг. 3: Дрейф конфігурації та автоматичне зцілення ────────────────────────
def fig_state_drift_and_remediation():
    W, H = 1000, 500
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Дрейф конфігурації (Configuration Drift) та відновлення стану", size=16, color=INK, bold=True))
    
    cw, ch = 260, 380
    
    # Стан А: Узгоджений (Синхронізація)
    x_a = 40
    p.append(rect(x_a, 70, cw, ch, fill="#f8fafc", stroke="#64748b", sw=1.4, rx=8))
    p.append(text(x_a + cw / 2, 98, "1. Синхронний стан", size=13, color="#1e293b", bold=True))
    
    p.append(rect(x_a + 20, 120, cw - 40, 65, fill="#eff6ff", stroke="#3b82f6", sw=1.0, rx=4))
    p.append(text(x_a + cw / 2, 145, "Git: port = 443", size=12, color="#1e3a8a", bold=True))
    p.append(text(x_a + cw / 2, 168, "Вимога безпеки", size=10.5, color=MUTED))
    
    p.append(rect(x_a + 20, 200, cw - 40, 65, fill="#f1f5f9", stroke="#64748b", sw=1.0, rx=4))
    p.append(text(x_a + cw / 2, 225, "State: port = 443", size=12, color="#334155", bold=True))
    p.append(text(x_a + cw / 2, 248, "Останній відомий зліпок", size=10.5, color=MUTED))
    
    p.append(rect(x_a + 20, 280, cw - 40, 65, fill="#ecfdf5", stroke="#10b981", sw=1.0, rx=4))
    p.append(text(x_a + cw / 2, 305, "Cloud: port = 443", size=12, color="#065f46", bold=True))
    p.append(text(x_a + cw / 2, 328, "Реальна інфраструктура", size=10.5, color=MUTED))
    
    p.append(text(x_a + cw / 2, 415, "✓ Повна відповідність", size=12, color="#16a34a", bold=True))
    
    # Стан Б: Дрейф (Ручні зміни ClickOps)
    x_b = 370
    p.append(rect(x_b, 70, cw, ch, fill="#fffbeb", stroke="#d97706", sw=1.4, rx=8))
    p.append(text(x_b + cw / 2, 98, "2. Виникнення дрейфу", size=13, color="#b45309", bold=True))
    
    p.append(rect(x_b + 20, 120, cw - 40, 65, fill="#eff6ff", stroke="#3b82f6", sw=1.0, rx=4))
    p.append(text(x_b + cw / 2, 145, "Git: port = 443", size=12, color="#1e3a8a", bold=True))
    p.append(text(x_b + cw / 2, 168, "Код не змінювався", size=10.5, color=MUTED))
    
    p.append(rect(x_b + 20, 200, cw - 40, 65, fill="#f1f5f9", stroke="#64748b", sw=1.0, rx=4))
    p.append(text(x_b + cw / 2, 225, "State: port = 443", size=12, color="#334155", bold=True))
    p.append(text(x_b + cw / 2, 248, "Стейт не знає про мутацію", size=10.5, color=MUTED))
    
    p.append(rect(x_b + 20, 280, cw - 40, 65, fill="#fef2f2", stroke="#ef4444", sw=1.4, rx=4))
    p.append(text(x_b + cw / 2, 305, "Cloud: port = 22 (0.0.0.0/0)", size=11.5, color="#b91c1c", bold=True))
    p.append(text(x_b + cw / 2, 328, "Ручна правка в консолі!", size=10.5, color="#b91c1c"))
    
    p.append(text(x_b + cw / 2, 415, "⚠ Дрейф безпеки (Drift)", size=12, color="#b45309", bold=True))
    
    # Стан В: Зцілення (Reconciliation / GitOps)
    x_c = 700
    p.append(rect(x_c, 70, cw, ch, fill="#f0fdf4", stroke="#16a34a", sw=1.4, rx=8))
    p.append(text(x_c + cw / 2, 98, "3. Авто-виправлення", size=13, color="#15803d", bold=True))
    
    p.append(rect(x_c + 20, 120, cw - 40, 65, fill="#eff6ff", stroke="#3b82f6", sw=1.0, rx=4))
    p.append(text(x_c + cw / 2, 145, "Git: port = 443", size=12, color="#1e3a8a", bold=True))
    p.append(text(x_c + cw / 2, 168, "Еталонне джерело правди", size=10.5, color=MUTED))
    
    p.append(rect(x_c + 20, 200, cw - 40, 65, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=4))
    p.append(text(x_c + cw / 2, 225, "Plan: Diff detected!", size=12, color="#92400e", bold=True))
    p.append(text(x_c + cw / 2, 248, "Виявлено невідповідність", size=10.5, color=MUTED))
    
    p.append(rect(x_c + 20, 280, cw - 40, 65, fill="#ecfdf5", stroke="#10b981", sw=1.0, rx=4))
    p.append(text(x_c + cw / 2, 305, "Apply: Відкат до port = 443", size=11.5, color="#065f46", bold=True))
    p.append(text(x_c + cw / 2, 328, "Хмару повернено до норми", size=10.5, color=MUTED))
    
    p.append(text(x_c + cw / 2, 415, "✓ Самозцілення (Self-healing)", size=12, color="#16a34a", bold=True))
    
    # Стрілки між стадіями
    p.append(arrow(x_a + cw, 230, x_b, 230, color="#d97706", sw=2.0))
    p.append(arrow(x_b + cw, 230, x_c, 230, color="#16a34a", sw=2.0))
    
    render(os.path.join(OUT, "state-drift-and-remediation.svg"), W, H, *p)


# ── Фіг. 4: Мутабельна проти Імутабельної інфраструктури ───────────────────────
def fig_immutable_vs_mutable():
    W, H = 1000, 520
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Мутабельна проти Імутабельної інфраструктури (Pets vs Cattle)", size=16, color=INK, bold=True))
    
    col_w = 440
    
    # Ліворуч: Мутабельна
    lx = 40
    p.append(rect(lx, 70, col_w, 420, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=8))
    p.append(text(lx + col_w / 2, 98, "МУТАБЕЛЬНА («Домашні улюбленці» / Pets)", size=13.5, color="#334155", bold=True))
    
    m_steps = [
        ("1. Базовий сервер розгортається один раз (v1.0)", "#ffffff"),
        ("2. Оновлення: SSH / Ansible накочує патчі наживо", "#ffffff"),
        ("3. Накопичення артефактів, сміття, тимчасових ліб", "#fff1f2"),
        ("4. Непомітний дрейф конфігурацій («Сніжинки»)", "#fff1f2"),
        ("5. Сервер унікальний: страшно перезавантажити чи видалити", "#ffe4e6")
    ]
    sy = 125
    for txt, bg in m_steps:
        p.append(rect(lx + 20, sy, col_w - 40, 48, fill=bg, stroke="#cbd5e1", sw=1.0, rx=4))
        p.append(text(lx + 35, sy + 28, txt, size=11, color=INK, anchor="start"))
        sy += 58
        
    p.append(text(lx + col_w / 2, 445, "• Модифікація ресурсів на місці (In-place)", size=11.5, color="#991b1b", bold=True))
    p.append(text(lx + col_w / 2, 468, "• Висока ймовірність невідтворюваних збоїв", size=11.5, color="#991b1b", bold=True))
    
    # Праворуч: Імутабельна
    rx_col = 520
    p.append(rect(rx_col, 70, col_w, 420, fill="#f0fdf4", stroke="#16a34a", sw=1.6, rx=8))
    p.append(text(rx_col + col_w / 2, 98, "ІМУТАБЕЛЬНА («Змінне стадо» / Cattle)", size=13.5, color="#15803d", bold=True))
    
    im_steps = [
        ("1. Збірка незмінного образу (Golden Image / AMI / OCI)", "#ffffff"),
        ("2. Розгортання абсолютно однакових екземплярів (v1.0)", "#ffffff"),
        ("3. Потрібне оновлення? Збирається новий образ v1.1", "#dcfce7"),
        ("4. Підняття нових серверів v1.1 поруч зі старими v1.0", "#dcfce7"),
        ("5. Знищення старих серверів (Blue/Green або Rolling)", "#dcfce7")
    ]
    sy = 125
    for txt, bg in im_steps:
        p.append(rect(rx_col + 20, sy, col_w - 40, 48, fill=bg, stroke="#cbd5e1", sw=1.0, rx=4))
        p.append(text(rx_col + 35, sy + 28, txt, size=11, color=INK, anchor="start"))
        sy += 58
        
    p.append(text(rx_col + col_w / 2, 445, "• Ресурси ніколи не змінюються на місці", size=11.5, color="#166534", bold=True))
    p.append(text(rx_col + col_w / 2, 468, "• 100% відтворюваність та безпечний відкат", size=11.5, color="#166534", bold=True))
    
    render(os.path.join(OUT, "immutable-vs-mutable-infrastructure.svg"), W, H, *p)


if __name__ == "__main__":
    fig_iac_reconciliation_loop()
    fig_declarative_vs_imperative()
    fig_state_drift_and_remediation()
    fig_immutable_vs_mutable()
    print("Всі фігури згенеровано успішно.")
