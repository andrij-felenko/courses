# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Життєвий цикл та автомат станів Failover ──────────────────────────
def fig_failover_state_machine():
    W, H = 960, 480
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Автомат станів та фази перемикання при відмові (Failover Lifecycle)", size=15, color=INK, bold=True, anchor="start"))
    
    # 5 основних блоків процесу
    steps = [
        ("1. Штатний стан", "Лідер утримує ліз у DCS\nРепліки транслюють WAL\nКлієнти пишуть у Primary", "#f0fdf4", "#16a34a", 115),
        ("2. Виявлення збою", "Пропуск heartbeat-сигналів\nВичерпання таймауту лізу\nВтрата кворуму лідера", "#fef2f2", "#dc2626", 295),
        ("3. Ізоляція (Fencing)", "Активація STONITH / IPMI\nАнулювання мережевого VIP\nЗаборона запису старому лідеру", "#fffbeb", "#d97706", 475),
        ("4. Вибори та промоушен", "Порівняння LSN кандидатів\nВибір найсвіжішої репліки\nВиклик pg_promote() / вихід з RO", "#eff6ff", "#2563eb", 655),
        ("5. Перемикання клієнтів", "Оновлення стану в проксі\nПеремаршрутизація трафіку\npg_rewind для старих вузлів", "#faf5ff", "#9333ea", 835)
    ]
    
    box_w = 155.0
    box_h = 175.0
    box_y = 70.0
    
    for i, (title_s, desc_s, bg_c, stroke_c, cx) in enumerate(steps):
        x = cx - box_w / 2
        p.append(rect(x, box_y, box_w, box_h, fill=bg_c, stroke=stroke_c, sw=1.6, rx=6))
        p.append(text(cx, box_y + 24, title_s, size=12, color=stroke_c, bold=True))
        p.append(line(x + 10, box_y + 36, x + box_w - 10, box_y + 36, color=stroke_c, sw=1.0))
        p.append(mtext(cx, box_y + 58, desc_s, size=10.5, color=INK, lh=1.35))
        
        # Стрілка переходу до наступного кроку
        if i < len(steps) - 1:
            next_cx = steps[i+1][4]
            p.append(arrow(cx + box_w / 2 + 2, box_y + box_h / 2, next_cx - box_w / 2 - 4, box_y + box_h / 2, color=LINE, sw=1.8))
            
    # Нижня частина: Часова шкала RTO та втрати даних (RPO)
    axis_y = 350.0
    p.append(rect(30, 275, W - 60, 180, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(50, 300, "Внесок фаз перемикання у загальний час простою (RTO) та ризик втрати даних (RPO)", size=12.5, color=INK, bold=True, anchor="start"))
    
    p.append(line(60, axis_y, W - 60, axis_y, color=LINE, sw=1.8))
    p.append(arrow(W - 90, axis_y, W - 50, axis_y, color=LINE, sw=1.8))
    p.append(text(W - 55, axis_y - 10, "Час (t) →", size=11, color=MUTED, bold=True, anchor="end"))
    
    t_crash = 160.0
    t_detect = 380.0
    t_fence = 520.0
    t_promote = 680.0
    t_routed = 840.0
    
    # Інтервали
    p.append(rect(t_crash, 315, t_detect - t_crash, 25, fill="#fee2e2", stroke="#ef4444", sw=1.0, rx=3))
    p.append(text((t_crash + t_detect)/2, 332, "TTL лізу (Detection)", size=10, color="#dc2626", bold=True))
    
    p.append(rect(t_detect, 315, t_fence - t_detect, 25, fill="#fef3c7", stroke="#f59e0b", sw=1.0, rx=3))
    p.append(text((t_detect + t_fence)/2, 332, "Fencing", size=10, color="#d97706", bold=True))
    
    p.append(rect(t_fence, 315, t_promote - t_fence, 25, fill="#dbeafe", stroke="#3b82f6", sw=1.0, rx=3))
    p.append(text((t_fence + t_promote)/2, 332, "Promotion (LSN catch-up)", size=10, color="#2563eb", bold=True))
    
    p.append(rect(t_promote, 315, t_routed - t_promote, 25, fill="#f3e8ff", stroke="#a855f7", sw=1.0, rx=3))
    p.append(text((t_promote + t_routed)/2, 332, "Client Re-routing", size=10, color="#7e22ce", bold=True))
    
    # Позначки точок
    pts = [
        (t_crash, "Аварія лідера", "#dc2626"),
        (t_detect, "Ліз вичерпано", "#d97706"),
        (t_fence, "Ізольовано", "#d97706"),
        (t_promote, "Новий Primary", "#2563eb"),
        (t_routed, "Трафік переведено", "#16a34a")
    ]
    for tx, lbl, col in pts:
        p.append(line(tx, 310, tx, axis_y + 30, color=col, sw=1.4, dash="2 2"))
        p.append(circle(tx, axis_y, 4, fill=col, stroke="#ffffff", sw=1.2))
        p.append(text(tx, axis_y + 45, lbl, size=10, color=col, bold=True))
        
    # Дужка сумарного RTO
    rto_y = axis_y + 75
    p.append(line(t_crash, rto_y, t_routed, rto_y, color="#1e293b", sw=1.6))
    p.append(circle(t_crash, rto_y, 3, fill="#1e293b"))
    p.append(circle(t_routed, rto_y, 3, fill="#1e293b"))
    p.append(text((t_crash + t_routed)/2, rto_y + 16, "Сумарний RTO (Recovery Time Objective): від падіння до відновлення запису", size=11, color="#1e293b", bold=True))
    
    render(os.path.join(OUT, "ha-failover-state-machine.svg"), W, H, *p)

# ── Фіг. 2: Архітектура Patroni + etcd + HAProxy/PgBouncer ─────────────────────
def fig_patroni_etcd_architecture():
    W, H = 960, 520
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Високодоступний кластер: клієнтський шар, консенсус (etcd) та агенти Patroni", size=15, color=INK, bold=True, anchor="start"))
    
    # Клієнти
    p.append(rect(40, 70, 200, 60, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    p.append(text(140, 95, "Клієнтські застосунки", size=13, color=INK, bold=True))
    p.append(text(140, 115, "JDBC / libpq / пул з'єднань", size=10.5, color=MUTED))
    
    # Балансувальник трафіку / Проксі
    p.append(rect(340, 70, 260, 60, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    p.append(text(470, 95, "HAProxy / PgBouncer", size=13, color="#1d4ed8", bold=True))
    p.append(text(470, 115, "Маршрутизація за HTTP health-check", size=10.5, color=MUTED))
    
    p.append(arrow(240, 100, 335, 100, color=LINE, sw=1.8))
    p.append(text(287, 92, "SQL-запити", size=10, color=MUTED))
    
    # Консенсус etcd
    p.append(rect(680, 60, 240, 170, fill="#faf5ff", stroke="#a855f7", sw=1.5, rx=6))
    p.append(text(800, 85, "DCS Кластер (etcd / Raft)", size=13, color="#7e22ce", bold=True))
    p.append(text(800, 103, "3 або 5 вузлів (Строгий кворум)", size=10, color=MUTED))
    
    etcd_nodes = [(730, 145, "etcd-1"), (800, 145, "etcd-2"), (870, 145, "etcd-3")]
    for ex, ey, elbl in etcd_nodes:
        p.append(circle(ex, ey, 22, fill="#ffffff", stroke="#9333ea", sw=1.2))
        p.append(text(ex, ey + 4, elbl, size=10, color="#7e22ce", bold=True))
    p.append(text(800, 200, "Ключ: /service/batman/leader (TTL=10s)", size=10, color="#6b21a8", bold=True))
    
    # Секція вузлів БД (Primary і Replica)
    # Primary Вузол
    p.append(rect(60, 240, 380, 250, fill="#f0fdf4", stroke="#22c55e", sw=1.8, rx=8))
    p.append(text(250, 268, "Вузол 1: Primary (Лідер кластера)", size=13.5, color="#15803d", bold=True))
    
    p.append(rect(80, 290, 160, 100, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=5))
    p.append(text(160, 315, "PostgreSQL", size=12.5, color="#166534", bold=True))
    p.append(mtext(160, 335, "Read-Write режим\nГенерація WAL (LSN: 0/1A00)\nПорт: 5432", size=10, color=INK, lh=1.3))
    
    p.append(rect(260, 290, 160, 100, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=5))
    p.append(text(340, 315, "Агент Patroni", size=12.5, color="#166534", bold=True))
    p.append(mtext(340, 335, "Heartbeat у DCS\nHTTP /primary → 200 OK\nHTTP /replica → 503", size=10, color=INK, lh=1.3))
    
    p.append(rect(80, 410, 340, 65, fill="#ffffff", stroke="#86efac", sw=1.0, rx=4))
    p.append(mtext(250, 432, "Стан: Утримує ліз у etcd (оновлення кожні 2с)\nПриймає з'єднання від балансувальника", size=10, color=INK, lh=1.35))
    
    # Standby Вузол
    p.append(rect(520, 240, 380, 250, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    p.append(text(710, 268, "Вузол 2: Standby (Синхронна/Асинхронна репліка)", size=13.5, color="#334155", bold=True))
    
    p.append(rect(540, 290, 160, 100, fill="#ffffff", stroke="#64748b", sw=1.2, rx=5))
    p.append(text(620, 315, "PostgreSQL", size=12.5, color="#1e293b", bold=True))
    p.append(mtext(620, 335, "Read-Only режим\nПрогравання WAL-потоку\nПорт: 5432", size=10, color=INK, lh=1.3))
    
    p.append(rect(720, 290, 160, 100, fill="#ffffff", stroke="#64748b", sw=1.2, rx=5))
    p.append(text(800, 315, "Агент Patroni", size=12.5, color="#1e293b", bold=True))
    p.append(mtext(800, 335, "Моніторинг лідера в DCS\nHTTP /primary → 503\nHTTP /replica → 200 OK", size=10, color=INK, lh=1.3))
    
    p.append(rect(540, 410, 340, 65, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(mtext(710, 432, "Стан: Очікує звільнення лізу в etcd\nГотовий до промоушену в разі аварії лідера", size=10, color=INK, lh=1.35))
    
    # Зв'язки
    # Потік реплікації між вузлами
    p.append(arrow(240, 350, 535, 350, color="#16a34a", sw=2.0))
    p.append(text(390, 370, "Потокова реплікація WAL", size=10.5, color="#15803d", bold=True))
    
    # Зв'язок HAProxy -> Вузли
    p.append(arrow(420, 130, 250, 235, color="#2563eb", sw=1.6))
    p.append(text(310, 175, "Трафік запису", size=10, color="#2563eb", bold=True))
    
    p.append(arrow(520, 130, 680, 235, color="#64748b", sw=1.4))
    p.append(text(620, 175, "Трафік читання (опція)", size=10, color=MUTED))
    
    # Зв'язок Patroni -> etcd
    p.append(line(340, 290, 340, 200, color="#9333ea", sw=1.4, dash="2 2"))
    p.append(arrow(340, 200, 675, 170, color="#9333ea", sw=1.4))
    
    p.append(arrow(800, 290, 800, 235, color="#9333ea", sw=1.4))
    
    render(os.path.join(OUT, "patroni-etcd-architecture.svg"), W, H, *p)

# ── Фіг. 3: Розщеплення мозку (Split-Brain) та механізм Fencing (STONITH) ─────
def fig_split_brain_and_fencing():
    W, H = 960, 460
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Анатомія розщеплення мозку (Split-Brain) та ізоляція вузла через Fencing / STONITH", size=15, color=INK, bold=True, anchor="start"))
    
    # Ліва половина: Сценарій катастрофи (Без Fencing)
    p.append(rect(30, 60, 435, 380, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    p.append(text(247, 85, "Аварійний сценарій: Відсутність Fencing (Split-Brain)", size=12.5, color="#b91c1c", bold=True))
    
    p.append(rect(50, 110, 175, 120, fill="#ffffff", stroke="#dc2626", sw=1.2, rx=5))
    p.append(text(137, 132, "Старий Primary", size=11.5, color="#dc2626", bold=True))
    p.append(mtext(137, 154, "Завис / втратив зв'язок\nВважає себе лідером\nПриймає записи клієнтів\nГенерує Timeline 1 (LSN 100)", size=9.5, color=INK, lh=1.3))
    
    p.append(rect(270, 110, 175, 120, fill="#ffffff", stroke="#dc2626", sw=1.2, rx=5))
    p.append(text(357, 132, "Новий Primary", size=11.5, color="#dc2626", bold=True))
    p.append(mtext(357, 154, "Оголосив себе лідером\nПриймає записи клієнтів\nГенерує Timeline 2 (LSN 100)\nНесумісні зміни даних!", size=9.5, color=INK, lh=1.3))
    
    # Мережевий розрив між ними
    p.append(line(230, 150, 265, 150, color="#ef4444", sw=2.0, dash="3 3"))
    p.append(text(247, 142, "⚡", size=16, color="#dc2626"))
    p.append(text(247, 175, "Мережевий\nрозрив", size=9.5, color="#dc2626", bold=True))
    
    p.append(rect(50, 250, 395, 175, fill="#ffffff", stroke="#f87171", sw=1.0, rx=4))
    p.append(text(247, 272, "Катастрофічні наслідки для бізнесу:", size=11, color="#b91c1c", bold=True))
    p.append(mtext(247, 298, "1. Подвійний запис (Dual-Write) у різні вузли за однаковими PK\n2. Розходження журналів WAL/binlog: неможливість автоматичного злиття\n3. Втрата фінансових транзакцій при спробі примирення вузлів\n4. Ручне відновлення через hex-дампи та години простою", size=10, color=INK, lh=1.4))
    
    # Права половина: Сценарій захисту з STONITH / Fencing
    p.append(rect(495, 60, 435, 380, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    p.append(text(712, 85, "Коректний сценарій: Захист через STONITH / Fencing", size=12.5, color="#15803d", bold=True))
    
    p.append(rect(515, 110, 175, 120, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=5))
    p.append(text(602, 132, "Старий Primary", size=11.5, color="#475569", bold=True))
    p.append(mtext(602, 154, "ІЗОЛЬОВАНО (FENCED)\nЖивлення вимкнено через IPMI\nАБО процес вбито через watchdog\nЗапис повністю заблоковано", size=9.5, color="#334155", lh=1.3))
    
    p.append(rect(735, 110, 175, 120, fill="#ffffff", stroke="#16a34a", sw=1.4, rx=5))
    p.append(text(822, 132, "Новий Primary", size=11.5, color="#16a34a", bold=True))
    p.append(mtext(822, 154, "Легітимний єдиний лідер\nОтримав кворум у DCS\nБезпечно приймає записи\nЄдине джерело правди", size=9.5, color=INK, lh=1.3))
    
    # Fencing механізм
    p.append(circle(602, 205, 14, fill="#dc2626", stroke="#ffffff", sw=1.5))
    p.append(text(602, 210, "✕", size=14, color="#ffffff", bold=True))
    
    p.append(rect(515, 250, 395, 175, fill="#ffffff", stroke="#86efac", sw=1.0, rx=4))
    p.append(text(712, 272, "Гарантії цілісності та безперервності:", size=11, color="#15803d", bold=True))
    p.append(mtext(712, 298, "1. Гарантія строго одного активного лідера в будь-який момент\n2. Нульовий ризик суперечливих транзакцій і колізій ідентифікаторів\n3. Детермінована зміна гілки журналу (нова часова шкала Timeline 2)\n4. Старий вузол після відновлення повертається як репліка через pg_rewind", size=10, color=INK, lh=1.4))
    
    render(os.path.join(OUT, "split-brain-and-fencing.svg"), W, H, *p)

if __name__ == "__main__":
    fig_failover_state_machine()
    fig_patroni_etcd_architecture()
    fig_split_brain_and_fencing()
    print("All figures generated successfully.")
