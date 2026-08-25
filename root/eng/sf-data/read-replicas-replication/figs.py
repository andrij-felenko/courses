# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Архітектурна топологія реплік читання та маршрутизації ─────────────
def fig_read_replica_architecture_topology():
    W, H = 1000, 560
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Архітектурна топологія реплік читання: розділення потоків запису та читання", size=15, color=INK, bold=True, anchor="start"))

    # Клієнтський шар / Застосунок
    p.append(rect(40, 70, 240, 130, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(160, 95, "Шар застосунку (App Layer)", size=13, color=INK, bold=True))
    p.append(rect(55, 115, 210, 32, fill="#e2e8f0", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(160, 135, "Пул запису (Write Pool)", size=11, color="#b91c1c", bold=True))
    p.append(rect(55, 155, 210, 32, fill="#e2e8f0", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(160, 175, "Пул читання (Read Pool)", size=11, color="#1d4ed8", bold=True))

    # Маршрутизатор / DB Proxy
    p.append(rect(360, 70, 260, 130, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    p.append(text(490, 95, "Маршрутизатор / DB Proxy", size=13, color="#1e40af", bold=True))
    p.append(mtext(490, 120, ["Lag-Aware Балансувальник", "(ProxySQL / PgBouncer / RDS Proxy)", "Перевірка LSN / GTID токенів"], size=11, color=INK, lh=1.35))

    # Стрілки від застосунку до проксі
    p.append(arrow(280, 131, 355, 131, color="#b91c1c", sw=2.0))
    p.append(text(318, 122, "INSERT / UPDATE", size=9.5, color="#b91c1c", bold=True))

    p.append(arrow(280, 171, 355, 171, color="#1d4ed8", sw=2.0))
    p.append(text(318, 162, "SELECT", size=9.5, color="#1d4ed8", bold=True))

    # Первинний вузол (Primary)
    p.append(rect(700, 70, 260, 190, fill="#fef2f2", stroke="#ef4444", sw=1.8, rx=6))
    p.append(text(830, 95, "Первинний вузол (Primary / Leader)", size=12.5, color="#b91c1c", bold=True))
    p.append(rect(715, 115, 230, 35, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=4))
    p.append(text(830, 136, "Рушій транзакцій (ACID MVCC)", size=11, color=INK))
    p.append(rect(715, 155, 230, 45, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=4))
    p.append(mtext(830, 173, ["Генератор журналу", "WAL / Binary Log (LSN / GTID)"], size=10.5, color=INK, lh=1.3))
    p.append(rect(715, 205, 230, 40, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=4))
    p.append(text(830, 229, "Дискове сховище (Data Files)", size=11, color=INK))

    # Стрілка від маршрутизатора до Primary
    p.append(arrow(620, 135, 695, 135, color="#b91c1c", sw=2.5))
    p.append(text(658, 125, "Запис", size=11, color="#b91c1c", bold=True))

    # Потік реплікації (Streaming replication)
    p.append(arrow(830, 260, 830, 320, color="#d97706", sw=2.2))
    p.append(text(815, 290, "Асинхронний потік WAL / Binlog (TCP)", size=11, color="#b45309", bold=True, anchor="end"))

    # Репліки читання (Read Replicas)
    rep_w = 260
    rep_h = 180
    y_rep = 330

    # Репліка 1
    p.append(rect(40, y_rep, rep_w, rep_h, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    p.append(text(40 + rep_w/2, y_rep + 25, "Репліка читання 1 (OLTP)", size=12.5, color="#15803d", bold=True))
    p.append(rect(55, y_rep + 45, rep_w - 30, 35, fill="#dcfce7", stroke="#86efac", sw=1, rx=4))
    p.append(text(40 + rep_w/2, y_rep + 66, "Apply Process (WAL Receiver)", size=10.5, color=INK))
    p.append(rect(55, y_rep + 85, rep_w - 30, 35, fill="#dcfce7", stroke="#86efac", sw=1, rx=4))
    p.append(text(40 + rep_w/2, y_rep + 106, "Read-Only Buffer Pool", size=10.5, color=INK))
    p.append(text(40 + rep_w/2, y_rep + 145, "Лаг: 12 мс (Статус: OK)", size=11, color="#15803d", bold=True))

    # Репліка 2
    p.append(rect(360, y_rep, rep_w, rep_h, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    p.append(text(360 + rep_w/2, y_rep + 25, "Репліка читання 2 (OLTP)", size=12.5, color="#15803d", bold=True))
    p.append(rect(375, y_rep + 45, rep_w - 30, 35, fill="#dcfce7", stroke="#86efac", sw=1, rx=4))
    p.append(text(360 + rep_w/2, y_rep + 66, "Apply Process (WAL Receiver)", size=10.5, color=INK))
    p.append(rect(375, y_rep + 85, rep_w - 30, 35, fill="#dcfce7", stroke="#86efac", sw=1, rx=4))
    p.append(text(360 + rep_w/2, y_rep + 106, "Read-Only Buffer Pool", size=10.5, color=INK))
    p.append(text(360 + rep_w/2, y_rep + 145, "Лаг: 18 мс (Статус: OK)", size=11, color="#15803d", bold=True))

    # Репліка 3 (Аналітика / Звіти)
    p.append(rect(680, y_rep, rep_w, rep_h, fill="#faf5ff", stroke="#a855f7", sw=1.5, rx=6))
    p.append(text(680 + rep_w/2, y_rep + 25, "Спеціалізована репліка (OLAP)", size=12.5, color="#7e22ce", bold=True))
    p.append(rect(695, y_rep + 45, rep_w - 30, 35, fill="#f3e8ff", stroke="#d8b4fe", sw=1, rx=4))
    p.append(text(680 + rep_w/2, y_rep + 66, "Важкі аналітичні скани / BI", size=10.5, color=INK))
    p.append(rect(695, y_rep + 85, rep_w - 30, 35, fill="#f3e8ff", stroke="#d8b4fe", sw=1, rx=4))
    p.append(text(680 + rep_w/2, y_rep + 106, "Ізольовані індекси / пам'ять", size=10.5, color=INK))
    p.append(text(680 + rep_w/2, y_rep + 145, "Ізольована від OLTP-трафіку", size=11, color="#7e22ce", bold=True))

    # Зв'язки реплікації до реплік 1, 2, 3
    p.append('<path d="M 830 260 L 830 320 L 170 320 L 170 330" stroke="#d97706" stroke-width="1.8" fill="none"/>')
    p.append('<path d="M 490 320 L 490 330" stroke="#d97706" stroke-width="1.8" fill="none"/>')
    p.append(circle(830, 320, 3, fill="#d97706"))
    p.append(circle(490, 320, 3, fill="#d97706"))
    p.append(circle(170, 320, 3, fill="#d97706"))

    # Стрілки маршрутизації читання від проксі до реплік 1 і 2
    p.append(arrow(450, 200, 180, y_rep, color="#1d4ed8", sw=1.8))
    p.append(arrow(490, 200, 490, y_rep, color="#1d4ed8", sw=1.8))
    p.append(text(280, 250, "Балансування читання", size=10.5, color="#1d4ed8", bold=True))

    render(os.path.join(OUT, "read-replica-architecture-topology.svg"), W, H, *p)

# ── Фіг. 2: Аномалії реплікаційного лагу та порушення узгодженості ─────────────
def fig_replication_lag_anomalies_timeline():
    W, H = 960, 520
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Аномалії реплікаційного лагу: Read-Your-Own-Writes та Monotonic Reads", size=15, color=INK, bold=True, anchor="start"))

    # Лінії життя акторів
    x_client = 140.0
    x_primary = 420.0
    x_rep1 = 680.0
    x_rep2 = 870.0

    actors = [
        (x_client, "Клієнт (Браузер)", "#3b82f6"),
        (x_primary, "Primary (Лідер)", "#ef4444"),
        (x_rep1, "Репліка 1 (Лаг 50мс)", "#22c55e"),
        (x_rep2, "Репліка 2 (Лаг 800мс)", "#f59e0b")
    ]

    for ax, name, col in actors:
        p.append(rect(ax - 65, 60, 130, 32, fill=col, stroke=col, sw=1, rx=4))
        p.append(text(ax, 80, name, size=11, color="#ffffff", bold=True))
        p.append(line(ax, 95, ax, H - 40, color="#cbd5e1", sw=1.5, dash="4 4"))

    # Сценарій 1: Read-Your-Own-Writes Anomaly
    p.append(rect(30, 110, W - 60, 175, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(50, 130, "Аномалія 1: Порушення читання власних записів (Read-Your-Own-Writes)", size=12, color="#b91c1c", bold=True, anchor="start"))

    t1_y = 150
    p.append(arrow(x_client, t1_y, x_primary, t1_y + 15, color="#b91c1c", sw=1.8))
    p.append(text((x_client + x_primary)/2, t1_y + 6, "1. UPDATE users SET name='Олена'", size=10, color="#b91c1c", bold=True))

    t2_y = t1_y + 30
    p.append(rect(x_primary - 4, t2_y - 10, 8, 20, fill="#ef4444"))
    p.append(arrow(x_primary, t2_y + 10, x_client, t2_y + 20, color="#15803d", sw=1.8))
    p.append(text((x_client + x_primary)/2, t2_y + 12, "2. Commit OK (200 OK)", size=10, color="#15803d", bold=True))

    t3_y = t2_y + 35
    p.append(arrow(x_client, t3_y, x_rep1, t3_y + 20, color="#1d4ed8", sw=1.8))
    p.append(text(x_client + 160, t3_y + 8, "3. Редирект на профіль: SELECT name", size=10, color="#1d4ed8", bold=True))

    t4_y = t3_y + 35
    p.append(arrow(x_rep1, t4_y, x_client, t4_y + 15, color="#dc2626", sw=1.8))
    p.append(text((x_client + x_rep1)/2, t4_y + 6, "4. Результат: name='Марія' (Застарілі дані! Лаг WAL)", size=10, color="#dc2626", bold=True))

    # Сценарій 2: Monotonic Reads Violation
    p.append(rect(30, 305, W - 60, 185, fill="#fffbeb", stroke="#fde68a", sw=1.2, rx=6))
    p.append(text(50, 325, "Аномалія 2: Порушення монотонного читання (Ефект «подорожі назад у часі»)", size=12, color="#b45309", bold=True, anchor="start"))

    m1_y = 345
    p.append(arrow(x_client, m1_y, x_rep1, m1_y + 15, color="#1d4ed8", sw=1.8))
    p.append(text((x_client + x_rep1)/2 - 50, m1_y + 6, "1. Запит 1: SELECT comment_count", size=10, color="#1d4ed8", bold=True))

    m2_y = m1_y + 30
    p.append(arrow(x_rep1, m2_y, x_client, m2_y + 15, color="#15803d", sw=1.8))
    p.append(text((x_client + x_rep1)/2 - 50, m2_y + 6, "2. Відповідь: 5 коментарів (Репліка 1 наздогнала стан)", size=10, color="#15803d", bold=True))

    m3_y = m2_y + 35
    p.append(arrow(x_client, m3_y, x_rep2, m3_y + 25, color="#1d4ed8", sw=1.8))
    p.append(text((x_client + x_rep2)/2 - 80, m3_y + 12, "3. Оновлення сторінки (F5) → Запит потрапляє на Репліку 2", size=10, color="#1d4ed8", bold=True))

    m4_y = m3_y + 40
    p.append(arrow(x_rep2, m4_y, x_client, m4_y + 20, color="#dc2626", sw=1.8))
    p.append(text((x_client + x_rep2)/2 - 80, m4_y + 8, "4. Відповідь: 3 коментарі (Коментарі «зникли» через вищий лаг)", size=10, color="#dc2626", bold=True))

    render(os.path.join(OUT, "replication-lag-anomalies-timeline.svg"), W, H, *p)

# ── Фіг. 3: Маршрутизація з каузальними маркерами LSN / GTID ───────────────────
def fig_lsn_causal_token_routing():
    W, H = 960, 480
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Сесійні гарантії через маркери журналу: маршрутизація на основі LSN / GTID", size=15, color=INK, bold=True, anchor="start"))

    # Блок клієнта
    p.append(rect(40, 80, 220, 360, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    p.append(text(150, 110, "Клієнт / Сесія", size=13, color=INK, bold=True))
    p.append(rect(55, 140, 190, 70, fill="#e2e8f0", stroke="#cbd5e1", sw=1, rx=4))
    p.append(mtext(150, 160, ["1. Мутація стану", "POST /order/submit", "Отримання LSN токена"], size=10.5, color=INK, lh=1.35))
    p.append(rect(55, 230, 190, 60, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=4))
    p.append(mtext(150, 250, ["Сесійний маркер:", "Session_LSN = 0/16B3A40"], size=10.5, color="#b91c1c", bold=True, lh=1.35))
    p.append(rect(55, 310, 190, 110, fill="#dbeafe", stroke="#93c5fd", sw=1, rx=4))
    p.append(mtext(150, 335, ["2. Наступне читання", "GET /order/status", "Заголовок:", "X-Required-LSN: 0/16B3A40"], size=10.5, color="#1e40af", lh=1.35))

    # Розумний маршрутизатор
    p.append(rect(310, 80, 280, 360, fill="#eff6ff", stroke="#3b82f6", sw=1.8, rx=6))
    p.append(text(450, 110, "Lag-Aware Router / Proxy", size=13, color="#1e40af", bold=True))
    p.append(rect(325, 140, 250, 80, fill="#ffffff", stroke="#93c5fd", sw=1, rx=4))
    p.append(mtext(450, 165, ["Опитування стану реплік:", "Репліка A: Applied LSN = 0/16B3800", "Репліка B: Applied LSN = 0/16B3B20"], size=10.5, color=INK, lh=1.35))

    p.append(rect(325, 240, 250, 180, fill="#ffffff", stroke="#93c5fd", sw=1, rx=4))
    p.append(text(450, 265, "Логіка маршрутизації читання:", size=11, color="#1e40af", bold=True))
    p.append(mtext(450, 295, [
        "IF Replica.Applied_LSN ≥ Session_LSN:",
        "  → Маршрутизувати на Репліку B (OK)",
        "ELSE IF Replica відстає:",
        "  → Зачекати replay до timeout",
        "  → АБО перенаправити на Primary"
    ], size=10.5, color=INK, lh=1.35))

    # Цільові бази даних
    p.append(rect(640, 80, 280, 100, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    p.append(text(780, 105, "Primary (Лідер)", size=12.5, color="#b91c1c", bold=True))
    p.append(text(780, 130, "Current LSN = 0/16B3C00", size=11, color=INK))
    p.append(text(780, 155, "Завжди містить найсвіжіший стан", size=10, color=MUTED))

    p.append(rect(640, 210, 280, 105, fill="#fef2f2", stroke="#f87171", sw=1.5, rx=6))
    p.append(text(780, 235, "Репліка A (Відстає)", size=12.5, color="#dc2626", bold=True))
    p.append(text(780, 260, "Applied LSN = 0/16B3800 (< 0/16B3A40)", size=10.5, color="#dc2626", bold=True))
    p.append(text(780, 285, "ВІДХИЛЕНО: спричинить stale read", size=10, color="#dc2626"))

    p.append(rect(640, 335, 280, 105, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    p.append(text(780, 360, "Репліка B (Свіжа)", size=12.5, color="#15803d", bold=True))
    p.append(text(780, 385, "Applied LSN = 0/16B3B20 (≥ 0/16B3A40)", size=10.5, color="#15803d", bold=True))
    p.append(text(780, 410, "ДОЗВОЛЕНО: дані гарантовано актуальні", size=10, color="#15803d"))

    # Стрілки між компонентами
    p.append(arrow(260, 365, 310, 365, color="#1e40af", sw=2.0))
    p.append(arrow(575, 385, 640, 385, color="#15803d", sw=2.2))
    p.append(text(605, 375, "SELECT", size=10, color="#15803d", bold=True))

    render(os.path.join(OUT, "lsn-causal-token-routing.svg"), W, H, *p)

# ── Фіг. 4: Каскадні та спеціалізовані топології реплікації ────────────────────
def fig_cascading_and_specialized_topologies():
    W, H = 1000, 520
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Топології реплікації: каскадне дерево (Relay Tree) та спеціалізовані вузли", size=15, color=INK, bold=True, anchor="start"))

    # Primary
    p.append(rect(380, 65, 240, 80, fill="#fef2f2", stroke="#ef4444", sw=1.8, rx=6))
    p.append(text(500, 92, "Primary (Лідер)", size=13, color="#b91c1c", bold=True))
    p.append(text(500, 115, "Тільки мутації + 2 прямих потоки WAL", size=10.5, color=INK))

    # Ліва гілка: Каскадний вузол (Relay / Intermediate Standby)
    p.append(rect(140, 190, 260, 85, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    p.append(text(270, 215, "Каскадний вузол (Relay Standby)", size=12, color="#1d4ed8", bold=True))
    p.append(mtext(270, 240, ["Приймає 1 потік від Primary,", "роздає WAL на 8 локальних реплік"], size=10.5, color=INK, lh=1.3))

    # Права гілка: Міжрегіональний вузол (Cross-Region Standby)
    p.append(rect(600, 190, 260, 85, fill="#fdf4ff", stroke="#c084fc", sw=1.5, rx=6))
    p.append(text(730, 215, "Міжрегіональний шлюз (Cross-Region)", size=12, color="#7e22ce", bold=True))
    p.append(mtext(730, 240, ["Стиснення трафіку через WAN,", "локальний пул реплік у ЄС/США"], size=10.5, color=INK, lh=1.3))

    # Стрілки від Primary до проміжних вузлів
    p.append(arrow(430, 145, 280, 190, color="#b45309", sw=2.0))
    p.append(text(340, 160, "WAN Stream 1", size=10, color="#b45309", bold=True))

    p.append(arrow(570, 145, 720, 190, color="#b45309", sw=2.0))
    p.append(text(660, 160, "WAN Stream 2", size=10, color="#b45309", bold=True))

    # Листові репліки читання (Leaf Read Replicas) під Relay
    for i, offset_x in enumerate([40, 170, 300]):
        p.append(rect(offset_x, 340, 115, 75, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=5))
        p.append(text(offset_x + 57.5, 365, f"OLTP Read {i+1}", size=11, color="#15803d", bold=True))
        p.append(text(offset_x + 57.5, 390, "Локальний ЦОД", size=9.5, color=MUTED))
        p.append(arrow(270, 275, offset_x + 57.5, 340, color="#15803d", sw=1.5))

    # Спеціалізовані вузли під Cross-Region / Окремі
    # 1. Відкладена репліка (Delayed Standby)
    p.append(rect(460, 340, 160, 120, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=5))
    p.append(text(540, 365, "Відкладена репліка", size=11.5, color="#b45309", bold=True))
    p.append(text(540, 385, "(Time-Delayed)", size=10.5, color="#b45309", bold=True))
    p.append(mtext(540, 410, ["Затримка apply: 4 год", "Захист від DROP TABLE", "та руйнівних DDL"], size=9.5, color=INK, lh=1.3))

    # 2. Аналітична репліка (Analytics / OLAP)
    p.append(rect(650, 340, 150, 120, fill="#faf5ff", stroke="#a855f7", sw=1.5, rx=5))
    p.append(text(725, 365, "Аналітична репліка", size=11.5, color="#7e22ce", bold=True))
    p.append(text(725, 385, "(OLAP / BI)", size=10.5, color="#7e22ce", bold=True))
    p.append(mtext(725, 410, ["Кастомні індекси,", "великий work_mem,", "довгі важкі звіти"], size=9.5, color=INK, lh=1.3))

    # 3. Репліка для бекапів (Backup Standby)
    p.append(rect(830, 340, 140, 120, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=5))
    p.append(text(900, 365, "Репліка бекапів", size=11.5, color="#334155", bold=True))
    p.append(text(900, 385, "(Backup Node)", size=10.5, color="#334155", bold=True))
    p.append(mtext(900, 410, ["Зняття pg_dump,", "pg_basebackup,", "нуль I/O на Primary"], size=9.5, color=INK, lh=1.3))

    p.append(arrow(730, 275, 540, 340, color="#b45309", sw=1.5))
    p.append(arrow(730, 275, 725, 340, color="#7e22ce", sw=1.5))
    p.append(arrow(730, 275, 900, 340, color="#334155", sw=1.5))

    render(os.path.join(OUT, "cascading-and-specialized-topologies.svg"), W, H, *p)

if __name__ == "__main__":
    fig_read_replica_architecture_topology()
    fig_replication_lag_anomalies_timeline()
    fig_lsn_causal_token_routing()
    fig_cascading_and_specialized_topologies()
    print("All figures generated successfully.")
