# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=12, pad=8, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Статична маршрутизація проти динамічного реєстру ──────────────
def fig_static_vs_dynamic():
    W, H = 960, 480
    frags = []

    frags.append(text(480, 28, "Статична конфігурація IP проти динамічного виявлення сервісів", size=15, bold=True))

    # Ліва панель: Статична адресація (ламається при динамічних змінах)
    frags.append(rect(30, 50, 435, 410, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(247, 78, "Статична адресація (жорсткі IP / конфіги)", size=13, bold=True, color=POS))

    frags.append(box(120, 160, "Клієнтський\nсервіс A\n(Order)", size=11, bold=True, fill="#ffffff", stroke=MUTED, min_w=110))
    
    frags.append(box(370, 120, "Payment v1\n10.0.1.14:8080\n[АКТИВНИЙ]", size=10, fill="#eafaf0", stroke=FIELD, min_w=120))
    frags.append(box(370, 210, "Payment v2\n10.0.1.29:9041\n[НОВИЙ / ПЕРЕМІЩЕНО]", size=10, fill="#fff3e0", stroke="#e67e22", min_w=120))
    frags.append(box(370, 300, "Payment v3\n10.0.1.55:8080\n[ПАДІННЯ / DEAD]", size=10, fill="#fdecea", stroke=POS, min_w=120))

    # Стрілка клієнта до мертвого вузла
    frags.append(arrow(180, 160, 300, 300, color=POS, sw=2))
    frags.append(text(210, 260, "Запит на старий IP\n(Connection Refused / ETIMEDOUT)", size=10, color=POS, bold=True))

    frags.append(rect(50, 360, 395, 80, fill="#fff5f5", stroke=POS, sw=1, rx=4))
    frags.append(mtext(247, 385, [
        "Проблема: хмарний оркестратор перезапускає вузли,",
        "змінює IP-адреси та динамічні порти. Статичний",
        "конфіг миттєво застаріває і веде до втрати трафіку."
    ], size=10, color=POS))

    # Права панель: Динамічне виявлення через реєстр
    frags.append(rect(495, 50, 435, 410, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(712, 78, "Динамічне виявлення (Service Registry)", size=13, bold=True, color=FIELD))

    frags.append(box(580, 160, "Клієнтський\nсервіс A\n(Order)", size=11, bold=True, fill="#ffffff", stroke=MUTED, min_w=110))
    frags.append(box(712, 270, "Реєстр сервісів\n(Consul / Eureka / etcd)\n{Payment: [10.0.1.29:9041]}", size=11, bold=True, fill="#e8f0ff", stroke=NEG, min_w=180))

    frags.append(box(840, 130, "Payment v2\n10.0.1.29:9041\n[ЗДОРОВИЙ]", size=10, fill="#eafaf0", stroke=FIELD, min_w=120))
    frags.append(box(840, 390, "Payment (new)\n10.0.2.11:8080\n[РЕЄСТРАЦІЯ]", size=10, fill="#eaf0fd", stroke=NEG, min_w=120))

    # Стрілки взаємодії
    frags.append(arrow(840, 360, 780, 305, color=NEG, sw=1.5))
    frags.append(text(840, 335, "1. Register + Heartbeat", size=9, color=NEG))

    frags.append(arrow(580, 200, 640, 250, color=MUTED, sw=1.5))
    frags.append(text(575, 240, "2. Watch / Query", size=9, color=MUTED))

    frags.append(arrow(640, 150, 770, 135, color=FIELD, sw=2))
    frags.append(text(705, 125, "3. Прямий виклик", size=10, color=FIELD, bold=True))

    frags.append(rect(515, 365, 230, 75, fill="#f0fff4", stroke=FIELD, sw=1, rx=4))
    frags.append(mtext(630, 385, [
        "Перевага: екземпляри самі",
        "оголошують координати,",
        "а клієнт отримує актуальний список."
    ], size=10, color=FIELD))

    return render(os.path.join(IMG, 'static-vs-dynamic-routing.svg'), W, H, *frags)


# ── Фігура 2: Клієнтське проти Серверного виявлення ──────────────────────────
def fig_client_vs_server():
    W, H = 980, 490
    frags = []

    frags.append(text(490, 28, "Моделі виявлення: Клієнтська (Client-Side) проти Серверної (Server-Side)", size=15, bold=True))

    # Секція 1: Client-Side Discovery
    frags.append(rect(30, 50, 445, 420, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(252, 75, "1. Клієнтське виявлення (Client-Side Discovery)", size=12, bold=True, color=NEG))

    frags.append(box(120, 180, "Клієнтський сервіс\n[Smart Client SDK]\n• Локальний кеш\n• Алгоритм P2C / RoundRobin", size=10, bold=True, fill="#ffffff", stroke=NEG, min_w=140))
    frags.append(box(252, 330, "Реєстр сервісів\n(Consul / Eureka)\nКаталог інстансів і статусів", size=10, bold=True, fill="#e8f0ff", stroke=NEG, min_w=160))

    frags.append(box(390, 130, "Бекенд-інстанс 1\n10.2.0.15:8080", size=10, fill="#eafaf0", stroke=FIELD, min_w=110))
    frags.append(box(390, 230, "Бекенд-інстанс 2\n10.2.0.18:8080", size=10, fill="#eafaf0", stroke=FIELD, min_w=110))

    # Стрілки
    frags.append(arrow(150, 230, 200, 295, color=NEG, sw=1.5))
    frags.append(text(150, 275, "1. Запит адрес\n(Long Polling)", size=9, color=NEG))

    frags.append(arrow(200, 160, 325, 140, color=FIELD, sw=2))
    frags.append(text(255, 135, "2. Прямий виклик (0 проміжних вузлів)", size=9, color=FIELD, bold=True))

    frags.append(rect(50, 395, 405, 60, fill="#f4f6f8", stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(252, 412, [
        "+ Мінімальна латентність, багатий вибір балансування",
        "− Поліглотна складність: товстий SDK для кожної мови програмування"
    ], size=10, color=INK))

    # Секція 2: Server-Side Discovery
    frags.append(rect(505, 50, 445, 420, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(727, 75, "2. Серверне виявлення (Server-Side / Proxy)", size=12, bold=True, color=FIELD))

    frags.append(box(580, 180, "Клієнтський сервіс\n[Простий HTTP-клієнт]\nЗвертається до VIP:\n`http://payment-svc`", size=10, bold=True, fill="#ffffff", stroke=MUTED, min_w=130))
    
    frags.append(box(730, 180, "Балансувальник / Проксі\n(K8s kube-proxy / ALB / NGINX)\nМаршрутизує запити", size=10, bold=True, fill="#fff3e0", stroke="#e67e22", min_w=140))
    frags.append(box(730, 330, "Реєстр / Control Plane\n(K8s API / EndpointSlice)", size=10, bold=True, fill="#e8f0ff", stroke=NEG, min_w=150))

    frags.append(box(880, 130, "Бекенд-інстанс 1\n10.2.0.15:8080", size=10, fill="#eafaf0", stroke=FIELD, min_w=100))
    frags.append(box(880, 230, "Бекенд-інстанс 2\n10.2.0.18:8080", size=10, fill="#eafaf0", stroke=FIELD, min_w=100))

    # Стрілки
    frags.append(arrow(650, 180, 655, 180, color=MUTED, sw=1.5))
    frags.append(arrow(730, 295, 730, 230, color=NEG, sw=1.5))
    frags.append(text(795, 265, "Оновлення правил", size=9, color=NEG))

    frags.append(arrow(805, 170, 825, 150, color=FIELD, sw=1.8))
    frags.append(arrow(805, 190, 825, 215, color=FIELD, sw=1.8))
    frags.append(text(840, 180, "Hop", size=9, color=FIELD))

    frags.append(rect(525, 395, 405, 60, fill="#f4f6f8", stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(727, 412, [
        "+ Клієнт повністю ізольований від топології (немає прив'язки до SDK)",
        "− Додатковий мережевий перехід (мережева затримка, вузьке місце)"
    ], size=10, color=INK))

    return render(os.path.join(IMG, 'client-vs-server-discovery.svg'), W, H, *frags)


# ── Фігура 3: Життєвий цикл сервісу в реєстрі (Lease & Heartbeat) ─────────────
def fig_registry_lifecycle():
    W, H = 960, 460
    frags = []

    frags.append(text(480, 28, "Життєвий цикл інстанса в реєстрі: Оренда (Lease), Пульс (Heartbeat) та Евікція", size=15, bold=True))

    # Стадія 1: Реєстрація
    frags.append(rect(40, 65, 260, 160, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(170, 90, "1. Реєстрація (Register)", size=12, bold=True, color=NEG))
    frags.append(mtext(170, 125, [
        "Інстанс відправляє дескриптор:",
        "• IP-адреса та TCP-порт",
        "• Теги (v1.2, canary, dc-west)",
        "• Час оренди: TTL = 10 с"
    ], size=10, color=INK))
    frags.append(box(170, 195, "Статус: STARTING / HEALTHY", size=10, fill="#e8f0ff", stroke=NEG, min_w=170))

    # Стадія 2: Підтримання життя (Heartbeat Loop)
    frags.append(rect(350, 65, 260, 160, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(480, 90, "2. Пульс (Heartbeat Loop)", size=12, bold=True, color=FIELD))
    frags.append(mtext(480, 125, [
        "Періодичне оновлення оренди:",
        "• Інтервал T = TTL / 3 (кожні 3.3 с)",
        "• HTTP PUT /v1/agent/check/pass",
        "• Скидання таймера евікції"
    ], size=10, color=INK))
    frags.append(box(480, 195, "Статус: PASSING (в роутингу)", size=10, fill="#eafaf0", stroke=FIELD, min_w=170))

    # Стадія 3: Виявлення збою та видалення (Failure & Eviction)
    frags.append(rect(660, 65, 260, 160, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    frags.append(text(790, 90, "3. Збій та Евікція (Eviction)", size=12, bold=True, color=POS))
    frags.append(mtext(790, 125, [
        "Пропуск пульсу або збій чека:",
        "• Таймер TTL сплив (10 с без пульсу)",
        "• Реєстр маркує вузол CRITICAL",
        "• Видалення зі списку маршрутизації"
    ], size=10, color=INK))
    frags.append(box(790, 195, "Статус: CRITICAL / DEREGISTERED", size=10, fill="#fdecea", stroke=POS, min_w=180))

    # Стрілки переходу станів
    frags.append(arrow(300, 145, 345, 145, color=FIELD, sw=2))
    frags.append(arrow(610, 145, 655, 145, color=POS, sw=2))

    # Нижній блок: Синхронізація клієнтських кешів
    frags.append(rect(40, 260, 880, 175, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(480, 285, "Синхронізація локальних кешів клієнтів (Watch / Streaming Push)", size=13, bold=True, color=INK))

    frags.append(box(180, 355, "Реєстр сервісів\n[Подія: Зміна індексу версії X]", size=10, bold=True, fill="#e8f0ff", stroke=NEG, min_w=180))

    frags.append(box(500, 355, "Блокуючий запит / gRPC Watch\nLong Polling: чекає зміни індексу\nАбо HTTP/2 SSE / xDS Delta", size=10, fill="#ffffff", stroke=MUTED, min_w=200))

    frags.append(box(800, 355, "Клієнтський SDK\nАтомарне оновлення кешу\n(Atomic Pointer Swap)", size=10, bold=True, fill="#eafaf0", stroke=FIELD, min_w=160))

    frags.append(arrow(275, 355, 390, 355, color=NEG, sw=1.5))
    frags.append(arrow(605, 355, 715, 355, color=FIELD, sw=1.5))

    return render(os.path.join(IMG, 'registry-state-machine.svg'), W, H, *frags)


# ── Фігура 4: CAP-теорема у виявленні сервісів (CP проти AP) ──────────────────
def fig_cap_registry_tradeoffs():
    W, H = 960, 460
    frags = []

    frags.append(text(480, 28, "Компроміс CAP у виявленні сервісів: CP-реєстри проти AP-реєстрів", size=15, bold=True))

    # Лівий блок: CP Реєстри
    frags.append(rect(40, 55, 420, 380, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(250, 85, "CP-модель (Consul Raft, etcd, ZooKeeper)", size=13, bold=True, color=NEG))
    frags.append(box(250, 130, "Пріоритет: Сувора узгодженість (Strong Consistency)", size=10, bold=True, fill="#e8f0ff", stroke=NEG, min_w=280))

    frags.append(mtext(250, 185, [
        "Механізм консенсусу (Raft / Paxos):",
        "• Усі записи проходять через лідера кворуму",
        "• Гарантія: немає розбіжностей у топології"
    ], size=10, color=INK))

    frags.append(rect(60, 240, 380, 100, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(text(250, 260, "Поведінка під час мережевого розділення (Partition):", size=10, bold=True, color=POS))
    frags.append(mtext(250, 290, [
        "Вузли у меншості втрачають кворум.",
        "Записи та оновлення статусів БЛОКУЮТЬСЯ.",
        "Реєстр жертвує доступністю заради істини."
    ], size=10, color=POS))

    frags.append(box(250, 390, "Застосування: критичні сервіси, Service Mesh control plane", size=10, fill="#ffffff", stroke=MUTED, min_w=300))

    # Правий блок: AP Реєстри
    frags.append(rect(500, 55, 420, 380, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(710, 85, "AP-модель (Eureka, DNS-SD, Gossip Serf)", size=13, bold=True, color=FIELD))
    frags.append(box(710, 130, "Пріоритет: Постійна доступність (High Availability)", size=10, bold=True, fill="#eafaf0", stroke=FIELD, min_w=280))

    frags.append(mtext(710, 185, [
        "Асинхронна реплікація (Peer-to-Peer / Gossip):",
        "• Будь-який вузол приймає запис і читання",
        "• Гарантія: миттєва відповідь навіть під час аварій"
    ], size=10, color=INK))

    frags.append(rect(520, 240, 380, 100, fill="#f0fff4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(710, 260, "Поведінка під час мережевого розділення (Partition):", size=10, bold=True, color=FIELD))
    frags.append(mtext(710, 290, [
        "Обидва боки продовжують обслуговувати трафік.",
        "Допускаються застарілі або часткові дані (Stale Read).",
        "Краще надіслати запит до мертвого вузла й спробувати знову,",
        "ніж повністю зупинити маршрутизацію."
    ], size=10, color=FIELD))

    frags.append(box(710, 390, "Застосування: високонавантажений роутинг, мікросервісні виклики", size=10, fill="#ffffff", stroke=MUTED, min_w=300))

    return render(os.path.join(IMG, 'cap-registry-tradeoffs.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_static_vs_dynamic()
    fig_client_vs_server()
    fig_registry_lifecycle()
    fig_cap_registry_tradeoffs()
    print("Всі фігури згенеровано успішно.")
