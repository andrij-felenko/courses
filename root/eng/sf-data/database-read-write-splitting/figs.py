# -*- coding: utf-8 -*-
"""Генератор схем для статті про database-read-write-splitting (розподіл читання й запису в базах даних)."""

import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_rw_splitting_topologies():
    """Порівняння трьох фундаментальних топологій маршрутизації читання й запису."""
    w, h = 960, 480
    body = []

    # Заголовок
    body.append(text(w / 2, 28, "Архітектурні топології розподілу читання й запису (Read-Write Splitting)", size=16, bold=True))

    # Секція 1: Маршрутизація на рівні застосунку
    box1 = rect(25, 55, 285, 380, fill="#fdfefe", stroke="#3498db", sw=1.5, rx=8)
    head1 = text(167, 80, "1. На рівні застосунку", size=13, bold=True, color="#2980b9")
    sub1 = text(167, 98, "(Dynamic DataSource / ORM)", size=11, color=MUTED)

    app1, _, _ = textbox(167, 140, "Застосунок (App Instance)\n[Context / @Transactional]\nВизначає: Writer чи Reader", size=11, pad=8, fill="#ebf5fb", stroke="#3498db")
    p1, _, _ = textbox(105, 235, "Пул Primary\n(TCP)", size=10, pad=6, fill="#fef9e7", stroke="#f39c12")
    p2, _, _ = textbox(230, 235, "Пул Replicas\n(TCP)", size=10, pad=6, fill="#eafaf1", stroke="#27ae60")
    
    db_w1, _, _ = textbox(105, 340, "Primary DB\n(INSERT / UPDATE)", size=10, pad=6, fill="#fef9e7", stroke="#d35400")
    db_r1, _, _ = textbox(230, 340, "Replica DBs\n(SELECT)", size=10, pad=6, fill="#eafaf1", stroke="#27ae60")

    body.extend([box1, head1, sub1, app1, p1, p2, db_w1, db_r1])
    body.append(arrow(140, 168, 115, 212, color=LINE))
    body.append(arrow(195, 168, 220, 212, color=LINE))
    body.append(arrow(105, 258, 105, 318, color=LINE))
    body.append(arrow(230, 258, 230, 318, color=LINE))

    note1 = mtext(167, 395, ["+ Нульовий мережевий оверхед", "+ Повний бізнес-контекст сесії", "- Множення пулів з'єднань", "- Прив'язка до стеку/мови"], size=10, color=INK, lh=1.25)
    body.append(note1)

    # Секція 2: Маршрутизація на рівні проксі
    box2 = rect(335, 55, 290, 380, fill="#fdfefe", stroke="#8e44ad", sw=1.5, rx=8)
    head2 = text(480, 80, "2. На рівні проксі СКБД", size=13, bold=True, color="#8e44ad")
    sub2 = text(480, 98, "(ProxySQL / Envoy / MaxScale)", size=11, color=MUTED)

    app2, _, _ = textbox(480, 135, "Застосунок A, B, C\nЄдине підключення до проксі", size=11, pad=8, fill="#f4f6f8", stroke="#7f8c8d")
    proxy, _, _ = textbox(480, 215, "SQL Proxy (AST Parser)\nАналіз SQL, транзакцій,\nLSN, стану з'єднань", size=11, pad=8, fill="#f4ecf7", stroke="#8e44ad")

    db_w2, _, _ = textbox(410, 340, "Primary DB\n(RW Hostgroup)", size=10, pad=6, fill="#fef9e7", stroke="#d35400")
    db_r2, _, _ = textbox(550, 340, "Replica DBs\n(RO Hostgroup)", size=10, pad=6, fill="#eafaf1", stroke="#27ae60")

    body.extend([box2, head2, sub2, app2, proxy, db_w2, db_r2])
    body.append(arrow(480, 160, 480, 188, color=LINE))
    body.append(arrow(445, 245, 415, 318, color=LINE))
    body.append(arrow(515, 245, 545, 318, color=LINE))

    note2 = mtext(480, 395, ["+ Прозоро для будь-якої мови", "+ Централізований пул з'єднань", "- Додатковий мережевий хоп (RTT)", "- Витік стану сесій (SET @var)"], size=10, color=INK, lh=1.25)
    body.append(note2)

    # Секція 3: Розумний драйвер / Cloud-Native
    box3 = rect(650, 55, 285, 380, fill="#fdfefe", stroke="#27ae60", sw=1.5, rx=8)
    head3 = text(792, 80, "3. Розумний драйвер / Cloud", size=13, bold=True, color="#27ae60")
    sub3 = text(792, 98, "(Aurora Smart Driver / Mesh)", size=11, color=MUTED)

    app3, _, _ = textbox(792, 140, "Застосунок + Smart Driver\nОпитування топології кластера\nLSN-Aware балансування", size=11, pad=8, fill="#eafaf1", stroke="#27ae60")
    
    db_w3, _, _ = textbox(730, 260, "Primary Node\n(Обчислення)", size=10, pad=6, fill="#fef9e7", stroke="#d35400")
    db_r3, _, _ = textbox(855, 260, "Replica Nodes\n(Обчислення)", size=10, pad=6, fill="#eafaf1", stroke="#27ae60")

    storage, _, _ = textbox(792, 345, "Спільний шар сховища (Shared Storage Engine)\nРозподілений Log Store / Zero-Copy реплікація", size=10, pad=6, fill="#fdfefe", stroke="#16a085")

    body.extend([box3, head3, sub3, app3, db_w3, db_r3, storage])
    body.append(arrow(760, 172, 735, 238, color=LINE))
    body.append(arrow(825, 172, 850, 238, color=LINE))
    body.append(arrow(730, 282, 765, 328, color="#16a085"))
    body.append(arrow(855, 282, 820, 328, color="#16a085"))

    note3 = mtext(792, 400, ["+ Швидке перемикання топології", "+ Мінімальний лаг реплікації", "- Прив'язка до хмарного вендора", "- Складність конфігурації"], size=10, color=INK, lh=1.25)
    body.append(note3)

    # Загальний підпис знизу
    body.append(text(w / 2, 462, "Порівняння рівнів впровадження маршрутизації: компроміс між латентністю, ізоляцією та складністю управління", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'rw-splitting-topologies.svg'), w, h, *body)


def fig_replication_lag_and_anomalies():
    """Часова діаграма аномалії Read-Your-Own-Writes через реплікаційний лаг."""
    w, h = 960, 480
    body = []

    body.append(text(w / 2, 28, "Хронологія аномалії Read-Your-Own-Writes через асинхронний реплікаційний лаг", size=16, bold=True))

    # Вертикальні лінії часових осей (lifelines)
    roles = [
        ("Клієнт / Браузер", 140),
        ("Маршрутизатор (Router)", 380),
        ("Primary (Writer)", 620),
        ("Replica (Reader)", 840)
    ]

    for title, x in roles:
        body.append(rect(x - 85, 55, 170, 34, fill="#f4f6f8", stroke="#7f8c8d", sw=1.2, rx=4))
        body.append(text(x, 76, title, size=11, bold=True, color=INK))
        body.append(line(x, 90, x, 420, color="#bdc3c7", sw=1.2, dash="4,4"))

    # Подія 1: Запис профілю
    y1 = 120
    body.append(arrow(140, y1, 380, y1, color="#d35400"))
    body.append(text(260, y1 - 8, "1. POST /profile (avatar='new.png')", size=10, color="#d35400", bold=True))

    y2 = 145
    body.append(arrow(380, y2, 620, y2, color="#d35400"))
    body.append(text(500, y2 - 8, "2. UPDATE users SET ...", size=10, color="#d35400"))

    # Фіксація на Primary
    y3 = 175
    body.append(rect(610, y3 - 10, 20, 30, fill="#fef9e7", stroke="#d35400", sw=1.5, rx=3))
    body.append(text(640, y3 + 5, "COMMIT (WAL LSN: 5040)", size=10, bold=True, color="#d35400", anchor="start"))

    y4 = 210
    body.append(arrow(620, y4, 380, y4, color="#27ae60"))
    body.append(text(500, y4 - 8, "3. OK (Commit Success)", size=10, color="#27ae60"))

    body.append(arrow(380, y4 + 15, 140, y4 + 15, color="#27ae60"))
    body.append(text(260, y4 + 7, "4. 200 OK (Redirect to /profile)", size=10, color="#27ae60", bold=True))

    # Асинхронна реплікація з лагом
    y_rep_start = 185
    y_rep_end = 360
    body.append(arrow(620, y_rep_start, 840, y_rep_end, color="#95a5a6", sw=1.5))
    body.append(text(760, 270, "Асинхронний WAL стрим (T_lag = 180 мс)", size=10, color="#7f8c8d", italic=True))

    # Подія 2: Миттєве читання клієнтом
    y5 = 270
    body.append(arrow(140, y5, 380, y5, color="#2980b9"))
    body.append(text(260, y5 - 8, "5. GET /profile (Запит свіжого стану)", size=10, color="#2980b9", bold=True))

    y6 = 295
    body.append(arrow(380, y6, 840, y6, color="#2980b9"))
    body.append(text(610, y6 - 8, "6. SELECT avatar FROM users WHERE id=10", size=10, color="#2980b9"))

    # Читання старої версії на репліці
    y7 = 325
    body.append(rect(830, y7 - 10, 20, 25, fill="#fadbd8", stroke="#c0392b", sw=1.5, rx=3))
    body.append(text(840, y7 + 25, "LSN: 5010 < 5040 (Старий стан)", size=9, color="#c0392b", bold=True, anchor="middle"))

    y8 = 365
    body.append(arrow(840, y8, 380, y8, color="#c0392b"))
    body.append(text(610, y8 - 8, "7. avatar='old.png' (Застарілі дані)", size=10, color="#c0392b"))

    body.append(arrow(380, y8 + 15, 140, y8 + 15, color="#c0392b"))
    body.append(text(260, y8 + 7, "8. Користувач бачить старий аватар (Аномалія!)", size=10, color="#c0392b", bold=True))

    # Подія replaying завершена
    body.append(rect(830, 400, 20, 15, fill="#eafaf1", stroke="#27ae60", sw=1.2, rx=2))
    body.append(text(840, 428, "LSN = 5040 (Дані свіжі)", size=9, color="#27ae60", anchor="middle"))

    # Підпис
    body.append(text(w / 2, 460, "Асинхронний лаг реплікації породжує порушення причинної узгодженості: читання після запису повертає застарілий знімок", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'replication-lag-and-anomalies.svg'), w, h, *body)


def fig_lsn_causal_routing_flow():
    """Блок-схема причинної маршрутизації за допомогою токенів LSN / GTID."""
    w, h = 960, 480
    body = []

    body.append(text(w / 2, 28, "Алгоритм сесійної маршрутизації за токенами узгодженості (LSN / GTID Routing)", size=16, bold=True))

    # Вхідні блоки
    b_write, _, _ = textbox(150, 90, "Клієнт виконує запис:\nUPDATE / INSERT\n(Фіксація транзакції)", size=11, pad=8, fill="#fef9e7", stroke="#d35400")
    b_token, _, _ = textbox(440, 90, "Primary фіксує WAL\nПовертає токен LSN:\nL_commit = 0/48A9F10", size=11, pad=8, fill="#ebf5fb", stroke="#2980b9")
    b_session, _, _ = textbox(770, 90, "Сесія клієнта зберігає:\nRequired_LSN = L_commit\nWindow_Expire = now() + 2s", size=11, pad=8, fill="#f4f6f8", stroke="#7f8c8d")

    body.extend([b_write, b_token, b_session])
    body.append(arrow(240, 90, 330, 90, color=LINE))
    body.append(arrow(550, 90, 645, 90, color=LINE))

    # Перехід до наступного читання
    b_read, _, _ = textbox(770, 185, "Новий запит читання: SELECT\nКлієнт передає токен Required_LSN", size=11, pad=8, fill="#eafaf1", stroke="#27ae60")
    body.append(b_read)
    body.append(arrow(770, 130, 770, 155, color=LINE))

    # Блок перевірки умов
    b_cond, _, _ = textbox(440, 255, "Маршрутизатор опитує репліку:\nОтримує Replica_Replay_LSN\nПорівняння: Replica_LSN >= Required_LSN?", size=11, pad=10, fill="#fefde8", stroke="#f39c12")
    body.append(b_cond)
    body.append(arrow(670, 185, 480, 220, color=LINE))

    # Гілка ТАК (Репліка свіжа)
    b_yes, _, _ = textbox(160, 360, "Гілка ТАК (Репліка наздогнала):\nМаршрутизувати SELECT на Репліку\nЗняти навантаження з Primary", size=11, pad=8, fill="#eafaf1", stroke="#27ae60")
    body.append(b_yes)
    body.append(arrow(360, 275, 235, 330, color="#27ae60", sw=2))
    body.append(text(310, 295, "ТАК (LSN >= Req)", size=10, bold=True, color="#27ae60"))

    # Гілка НІ (Репліка відстає)
    b_no, _, _ = textbox(740, 360, "Гілка НІ (Репліка відстає):\n1. Очікувати WAIT_LSN (до 20 мс)\n2. Якщо таймаут -> Спрямувати на Primary", size=11, pad=8, fill="#fadbd8", stroke="#c0392b")
    body.append(b_no)
    body.append(arrow(520, 275, 650, 330, color="#c0392b", sw=2))
    body.append(text(595, 295, "НІ (LSN < Req)", size=10, bold=True, color="#c0392b"))

    # Підсумок знизу
    body.append(text(w / 2, 455, "Точне відстеження LSN гарантує Read-Your-Own-Writes без сліпого спрямування 100% читань на Primary", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'lsn-causal-routing-flow.svg'), w, h, *body)


def fig_session_state_and_transaction_pinning():
    """Скінченний автомат стану підключення: блокування сесії на Primary під час транзакцій та змін оточення."""
    w, h = 960, 480
    body = []

    body.append(text(w / 2, 28, "Скінченний автомат стану сесії та прив'язки з'єднань (Connection Pinning State Machine)", size=16, bold=True))

    # Стан 1: Вільний розімкнений стан (Autocommit RO)
    s1, _, _ = textbox(170, 160, "СТАН: РОЗІМКНЕНИЙ (Unpinned)\n• autocommit = 1\n• Немає відкритих транзакцій\n• Немає тимчасових таблиць\nМаршрут: SELECT -> Репліка, W -> Primary", size=11, pad=10, fill="#eafaf1", stroke="#27ae60")
    
    # Стан 2: Прив'язаний до Primary (Pinned by Transaction)
    s2, _, _ = textbox(750, 160, "СТАН: ТРАНЗАКЦІЙНИЙ (Pinned)\n• BEGIN / START TRANSACTION\n• autocommit = 0\n• SELECT ... FOR UPDATE\nМаршрут: 100% запитів -> ТІЛЬКИ Primary", size=11, pad=10, fill="#fadbd8", stroke="#c0392b")

    # Стан 3: Забруднений стан сесії (Polluted Session State)
    s3, _, _ = textbox(460, 340, "СТАН: СЕСІЙНО-МОДИФІКОВАНИЙ (Stateful Dirty)\n• Виконано: SET @my_var = 123\n• Створено: CREATE TEMPORARY TABLE\n• Змінено: SET time_zone / sql_mode\nМаршрут: З'єднання НЕ МОЖНА повертати в спільний пул!", size=11, pad=10, fill="#fefde8", stroke="#d4ac0d")

    body.extend([s1, s2, s3])

    # Переходи між 1 та 2
    body.append(arrow(315, 140, 580, 140, color="#c0392b", sw=2))
    body.append(text(447, 128, "BEGIN / START TRANSACTION (Прив'язка до Primary)", size=10, bold=True, color="#c0392b"))

    body.append(arrow(580, 180, 315, 180, color="#27ae60", sw=2))
    body.append(text(447, 198, "COMMIT / ROLLBACK (Повернення в розімкнений стан)", size=10, bold=True, color="#27ae60"))

    # Перехід до 3
    body.append(arrow(210, 225, 360, 295, color="#d4ac0d", sw=1.8))
    body.append(text(240, 275, "SET @var / CREATE TEMP", size=10, color="#b7950b"))

    body.append(arrow(710, 225, 560, 295, color="#d4ac0d", sw=1.8))
    body.append(text(670, 275, "Модифікація сесії в транзакції", size=10, color="#b7950b"))

    # Очищення зі стану 3
    body.append(arrow(360, 340, 180, 230, color="#2980b9", sw=1.8))
    body.append(text(210, 320, "RESET CONNECTION / DISCARD", size=10, color="#2980b9"))

    # Підпис знизу
    body.append(text(w / 2, 455, "Маршрутизатор зобов'язаний жорстко контролювати стан сесії, щоб уникнути витоку конфіденційних даних та порушення транзакційності", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'session-state-and-transaction-pinning.svg'), w, h, *body)


def main():
    fig_rw_splitting_topologies()
    fig_replication_lag_and_anomalies()
    fig_lsn_causal_routing_flow()
    fig_session_state_and_transaction_pinning()
    print("Усі фігури успішно згенеровано в img/")


if __name__ == '__main__':
    main()
