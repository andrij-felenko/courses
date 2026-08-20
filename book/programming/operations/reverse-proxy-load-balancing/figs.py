# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Архітектурне порівняння L4 проти L7 ────────────────────────────
def fig_l4_vs_l7():
    W, H = 1000, 520
    p = []
    
    # Загальний фон і заголовок
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Рівні прийняття рішень: Транспортний балансувальник L4 проти Проксі-сервера L7", size=15, color=INK, bold=True))
    
    # Ліва колонка: L4
    x_l4 = 30
    p.append(rect(x_l4, 65, 450, 430, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(x_l4 + 225, 95, "L4: Пакетна маршрутизація (TCP/UDP)", size=14, color="#0369a1", bold=True))
    
    # Елементи L4
    p.append(textbox(x_l4 + 225, 145, "Клієнтський TCP-пакет\n[IP джерела | Порт | IP призначення | TCP SYN]", size=11, fill="#eff6ff", stroke="#3b82f6")[0])
    
    p.append(arrow(x_l4 + 225, 175, x_l4 + 225, 215, color=LINE, sw=1.8))
    p.append(text(x_l4 + 225, 200, "Аналіз 5-tuple (без розбору HTTP)", size=10, color=MUTED))
    
    p.append(textbox(x_l4 + 225, 255, "L4 Ядро (IPVS / eBPF / DPDK / Maglev)\n• Не перериває TCP-потік (Passthrough)\n• Переписує IP/MAC (DNAT або DSR)\n• Пропускна здатність: >10 млн пак/с", size=11, fill="#f0fdf4", stroke="#16a34a")[0])
    
    p.append(arrow(x_l4 + 225, 305, x_l4 + 225, 345, color=LINE, sw=1.8))
    p.append(text(x_l4 + 225, 330, "Пряма передача сегментів", size=10, color=MUTED))
    
    p.append(textbox(x_l4 + 225, 395, "Бекенд (Цільовий вузол)\nОтримує сирий TCP-потік від клієнта;\nСам виконує TLS-рукостискання", size=11, fill="#ffffff", stroke="#64748b")[0])
    p.append(text(x_l4 + 225, 465, "Перевага: мінімальна затримка (<10 мкс), низький CPU", size=10.5, color="#15803d", bold=True))

    # Права колонка: L7
    x_l7 = 520
    p.append(rect(x_l7, 65, 450, 430, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(x_l7 + 225, 95, "L7: Прикладний проксі (HTTP / gRPC / TLS)", size=14, color="#7c3aed", bold=True))
    
    # Елементи L7
    p.append(textbox(x_l7 + 225, 145, "Клієнтський запит (HTTPS)\n[TLS 1.3 | HTTP GET /api/v2/orders | Cookie | JSON]", size=11, fill="#f5f3ff", stroke="#8b5cf6")[0])
    
    p.append(arrow(x_l7 + 225, 175, x_l7 + 225, 215, color=LINE, sw=1.8))
    p.append(text(x_l7 + 225, 200, "Повна термінація TCP та дешифрування TLS", size=10, color=MUTED))
    
    p.append(textbox(x_l7 + 225, 260, "L7 Зворотний проксі (Envoy / NGINX / HAProxy)\n• Парсинг URL-шляхів, заголовків, кук\n• Термінація TLS, стиснення, кешування\n• Пул гарячих Keep-Alive з'єднань до бекендів", size=11, fill="#fff7ed", stroke="#ea580c")[0])
    
    p.append(arrow(x_l7 + 225, 315, x_l7 + 225, 345, color=LINE, sw=1.8))
    p.append(text(x_l7 + 225, 335, "Маршрутизація за шляхом /api/*", size=10, color=MUTED))
    
    p.append(textbox(x_l7 + 225, 395, "Бекенд (Сервіс замовлень)\nОтримує чистий HTTP/1.1 або gRPC;\nІдентифікує клієнта через X-Forwarded-For", size=11, fill="#ffffff", stroke="#64748b")[0])
    p.append(text(x_l7 + 225, 465, "Перевага: гнучка маршрутизація, захист, інспекція", size=10.5, color="#b45309", bold=True))

    render(os.path.join(OUT, "l4-vs-l7-architecture.svg"), W, H, *p)

# ── Фігура 2: Буферизація повільних клієнтів та протитиск ──────────────────────
def fig_buffering_backpressure():
    W, H = 1000, 480
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Анатомія захисту бекенда: Асинхронна буферизація запитів та наскрізний протитиск", size=15, color=INK, bold=True))
    
    # Клієнт
    x_c = 40
    p.append(rect(x_c, 80, 220, 360, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    p.append(text(x_c + 110, 110, "Повільний клієнт (3G)", size=13, color="#1d4ed8", bold=True))
    p.append(mtext(x_c + 110, 150, [
        "Швидкість віддачі: 25 КБ/с",
        "Втрати пакетів: 4%",
        "Передача тіла 2 МБ: 80 сек",
        "",
        "Якби підключався напряму —",
        "заблокував би робочий",
        "потік бекенда на 80 с"
    ], size=11, color=INK, lh=1.35))
    p.append(rect(x_c + 20, 320, 180, 95, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
    p.append(text(x_c + 110, 345, "TCP Send Buffer", size=11, bold=True, color="#1e40af"))
    p.append(text(x_c + 110, 375, "Вікно прийому: 64 КБ", size=10.5, color=MUTED))
    p.append(text(x_c + 110, 395, "Отримує ACK порціями", size=10.5, color=MUTED))

    # Зворотний проксі
    x_p = 330
    p.append(rect(x_p, 80, 340, 360, fill="#fdf4ff", stroke="#c026d3", sw=1.5, rx=6))
    p.append(text(x_p + 170, 110, "Зворотний проксі (Асинхронний I/O)", size=13, color="#86198f", bold=True))
    
    p.append(textbox(x_p + 170, 160, "1. Подієвий цикл (epoll / kqueue)\nЧитка чанками без блокування потоків", size=11, fill="#ffffff", stroke="#e879f9")[0])
    
    p.append(textbox(x_p + 170, 235, "2. Кільцевий буфер пам'яті\nНакопичення повного HTTP-запиту;\nПри переповненні RAM — скидання на SSD", size=11, fill="#ffffff", stroke="#e879f9")[0])
    
    p.append(textbox(x_p + 170, 320, "3. Протитиск (Backpressure)\nЯкщо клієнт повільно читає відповідь —\nзупинка читання з сокета бекенда\n(TCP ZeroWindow probing)", size=11, fill="#fff1f2", stroke="#f43f5e")[0])
    
    p.append(textbox(x_p + 170, 400, "4. Пул Keep-Alive з'єднань\nЗапит летить у вже відкритий TCP-канал", size=11, fill="#ffffff", stroke="#e879f9")[0])

    # Стрілки зліва
    p.append(arrow(x_c + 225, 175, x_p - 5, 175, color="#2563eb", sw=2.0))
    p.append(text((x_c + 220 + x_p) / 2, 165, "Повільний потік (25 КБ/с)", size=10, color="#1d4ed8"))
    
    p.append(arrow(x_p - 5, 335, x_c + 225, 335, color="#e11d48", sw=2.0))
    p.append(text((x_c + 220 + x_p) / 2, 325, "Зменшення TCP Window", size=10, color="#be123c"))

    # Бекенд
    x_b = 740
    p.append(rect(x_b, 80, 220, 360, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    p.append(text(x_b + 110, 110, "Бекенд застосунку", size=13, color="#15803d", bold=True))
    p.append(mtext(x_b + 110, 150, [
        "Локальна мережа: 10 Гбіт/с",
        "Затримка LAN: < 0.2 мс",
        "Обробка запиту: 4 мс",
        "",
        "Отримує ПОВНІСТЮ",
        "зібраний запит;",
        "Одразу повертає відповідь",
        "й звільняє потік"
    ], size=11, color=INK, lh=1.35))
    
    p.append(rect(x_b + 20, 320, 180, 95, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    p.append(text(x_b + 110, 345, "Пул обробників", size=11, bold=True, color="#166534"))
    p.append(text(x_b + 110, 375, "100% завантаження CPU", size=10.5, color=MUTED))
    p.append(text(x_b + 110, 395, "Нуль часу на очікування I/O", size=10.5, color=MUTED))

    # Стрілки справа
    p.append(arrow(x_p + 345, 235, x_b - 5, 235, color="#16a34a", sw=2.0))
    p.append(text((x_p + 340 + x_b) / 2, 225, "Миттєва передача (4 мс)", size=10, color="#15803d"))
    
    p.append(arrow(x_b - 5, 275, x_p + 345, 275, color="#16a34a", sw=2.0))
    p.append(text((x_p + 340 + x_b) / 2, 265, "Швидка HTTP-відповідь", size=10, color="#15803d"))

    render(os.path.join(OUT, "reverse-proxy-buffering-backpressure.svg"), W, H, *p)

# ── Фігура 3: Алгоритми розподілу навантаження ─────────────────────────────────
def fig_load_balancing_algorithms():
    W, H = 1000, 520
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Математичні моделі балансування: Від найменших з'єднань до P2C та хеш-кільця", size=15, color=INK, bold=True))
    
    # 1. Round Robin / Least Connections (Зліва вгорі)
    x1, y1 = 30, 70
    p.append(rect(x1, y1, 460, 200, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(x1 + 230, 95, "1. Round Robin та Least Connections", size=13, color="#0f172a", bold=True))
    p.append(textbox(x1 + 115, 160, "Round Robin (RR):\nЦиклічний лічильник:\ni = (i + 1) % N\n• Ігнорує вагу запиту", size=10, fill="#ffffff", stroke="#cbd5e1")[0])
    p.append(textbox(x1 + 340, 160, "Least Connections (LC):\nОбирає сервер із:\nmin(активні_з'єднання / вага)\n• Ризик «ефекту отари»", size=10, fill="#ffffff", stroke="#cbd5e1")[0])
    p.append(text(x1 + 230, 245, "Проблема LC: незалежні проксі одночасно обирають один і той самий вузол", size=10, color="#b91c1c"))

    # 2. Power of Two Choices (P2C) (Праворуч вгорі)
    x2, y2 = 510, 70
    p.append(rect(x2, y2, 460, 200, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    p.append(text(x2 + 230, 95, "2. Power of Two Random Choices (P2C)", size=13, color="#1e40af", bold=True))
    
    p.append(textbox(x2 + 230, 145, "Алгоритм P2C (Azar et al.):\n1. Випадково обрати два вузли: A та B з пулу N\n2. Порівняти їхнє навантаження (активні з'єднання або EWMA)\n3. Направити запит вузлу з меншим навантаженням", size=10, fill="#ffffff", stroke="#93c5fd")[0])
    
    p.append(textbox(x2 + 230, 220, "Математичний ефект:\nМаксимальна довжина черги падає з O(ln N / ln ln N) до O(ln ln N / ln 2)!\nПовністю ліквідує синхронізацію між незалежними проксі", size=10, fill="#dbeafe", stroke="#2563eb")[0])

    # 3. Consistent Hashing Ring (Внизу)
    x3, y3 = 30, 290
    p.append(rect(x3, y3, 940, 200, fill="#fdf4ff", stroke="#c026d3", sw=1.5, rx=6))
    p.append(text(x3 + 470, 315, "3. Узгоджене кільцеве хешування (Consistent Hashing з Virtual Nodes)", size=13, color="#86198f", bold=True))
    
    # Кільце та пояснення
    p.append(circle(x3 + 140, 400, 60, fill="#ffffff", stroke="#a855f7", sw=2.0))
    p.append(text(x3 + 140, 395, "Простір хешів", size=10, color=MUTED))
    p.append(text(x3 + 140, 412, "[0 .. 2³² - 1]", size=11, bold=True, color="#7e22ce"))
    
    # Точки на кільці
    p.append(circle(x3 + 140, 340, 6, fill="#2563eb", stroke="#1d4ed8", sw=1.5))
    p.append(text(x3 + 140, 326, "Node1-v1", size=10, bold=True, color="#1e40af"))
    
    p.append(circle(x3 + 200, 400, 6, fill="#16a34a", stroke="#15803d", sw=1.5))
    p.append(text(x3 + 235, 403, "Node2-v1", size=10, bold=True, color="#15803d"))
    
    p.append(circle(x3 + 140, 460, 6, fill="#d97706", stroke="#b45309", sw=1.5))
    p.append(text(x3 + 140, 479, "Node3-v1", size=10, bold=True, color="#b45309"))
    
    p.append(circle(x3 + 80, 400, 6, fill="#2563eb", stroke="#1d4ed8", sw=1.5))
    p.append(text(x3 + 45, 403, "Node1-v2", size=10, bold=True, color="#1e40af"))

    # Опис властивостей кільця
    p.append(textbox(x3 + 580, 400, "Властивості узгодженого хешування:\n• Ключ (User ID / Session Cookie / URL) проектується на кільце хеш-функцією (xxHash)\n• Запит направляється на перший вузол за годинниковою стрілкою (Binary Search у vnodes)\n• Додавання або видалення сервера переміщує лише 1/N частину ключів (замість 100%)\n• Віртуальні ноди (100–256 на фізичний сервер) ліквідують дисперсію та гарантують баланс", size=10, fill="#ffffff", stroke="#e879f9")[0])

    render(os.path.join(OUT, "load-balancing-algorithms-p2c-hashring.svg"), W, H, *p)

# ── Фігура 4: Життєвий цикл стану бекенда, зондування та Drain ────────────────
def fig_health_drain_lifecycle():
    W, H = 1000, 480
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Життєвий цикл бекенда в балансувальнику: Зондування здоров'я, викид та плавний злив (Drain)", size=15, color=INK, bold=True))
    
    bw, bh = 220, 110
    
    # 1. Здоровий (Healthy)
    x1, y1 = 40, 80
    p.append(rect(x1, y1, bw, bh, fill="#f0fdf4", stroke="#16a34a", sw=1.8, rx=6))
    p.append(text(x1 + bw / 2, y1 + 25, "Здоровий (Healthy)", size=13, color="#15803d", bold=True))
    p.append(mtext(x1 + bw / 2, y1 + 52, [
        "100% робочої ваги",
        "Приймає нові запити",
        "Зонд /healthz повертає 200 OK"
    ], size=11, color=INK, lh=1.35))

    # 2. Несправний / Викид (Outlier Ejection)
    x2, y2 = 390, 80
    p.append(rect(x2, y2, bw, bh, fill="#fef2f2", stroke="#ef4444", sw=1.8, rx=6))
    p.append(text(x2 + bw / 2, y2 + 25, "Викинутий (Ejected / Unhealthy)", size=13, color="#b91c1c", bold=True))
    p.append(mtext(x2 + bw / 2, y2 + 52, [
        "Вага = 0 (трафік заблоковано)",
        "Пасивний аутлаєр (5xx помилки)",
        "Або K поспіль провалів зонда"
    ], size=11, color=INK, lh=1.35))

    # 3. Відновлення (Probing / Warmup)
    x3, y3 = 740, 80
    p.append(rect(x3, y3, bw, bh, fill="#eff6ff", stroke="#3b82f6", sw=1.8, rx=6))
    p.append(text(x3 + bw / 2, y3 + 25, "Відновлення (Warmup)", size=13, color="#1d4ed8", bold=True))
    p.append(mtext(x3 + bw / 2, y3 + 52, [
        "M поспіль успішних 200 OK",
        "Поступовий ріст ваги (0→100%)",
        "Захист від перевантаження"
    ], size=11, color=INK, lh=1.35))

    # Стрілки верхнього контуру
    p.append(arrow(x1 + bw + 5, y1 + bh / 2, x2 - 5, y1 + bh / 2, color="#dc2626", sw=1.8))
    p.append(text((x1 + bw + x2) / 2, y1 + bh / 2 - 10, "5xx > Поріг / Таймаут", size=10, color="#b91c1c"))

    p.append(arrow(x2 + bw + 5, y2 + bh / 2, x3 - 5, y2 + bh / 2, color="#2563eb", sw=1.8))
    p.append(text((x2 + bw + x3) / 2, y2 + bh / 2 - 10, "Cooldown вийшов", size=10, color="#1d4ed8"))

    p.append(line(x3 + bw / 2, y3 + bh + 5, x3 + bw / 2, 230, color="#16a34a", sw=1.8))
    p.append(line(x3 + bw / 2, 230, x1 + bw / 2, 230, color="#16a34a", sw=1.8))
    p.append(arrow(x1 + bw / 2, 230, x1 + bw / 2, y1 + bh + 5, color="#16a34a", sw=1.8))
    p.append(text(W / 2, 220, "Успішне прогрівання (Readmission) → Повернення в пул", size=10.5, color="#15803d", bold=True))

    # 4. Плавний злив (Graceful Drain) - Внизу
    x4, y4 = 250, 280
    p.append(rect(x4, y4, 500, 160, fill="#fffbeb", stroke="#d97706", sw=1.8, rx=6))
    p.append(text(x4 + 250, y4 + 28, "Фаза штатного виведення з експлуатації (Connection Draining)", size=13.5, color="#b45309", bold=True))
    p.append(mtext(x4 + 250, y4 + 60, [
        "1. Балансувальник отримує команду SIGTERM / API De-register",
        "2. Встановлює вагу вузла = 0 (нові клієнтські TCP/HTTP сесії не направляються)",
        "3. Очікує завершення існуючих in-flight транзакцій (до спливу drain_timeout)",
        "4. Клієнтам повертається Connection: close для закриття Keep-Alive сокетів",
        "5. Процес бекенда безпечно зупиняється без жодного обірваного запиту (0 помилок 502)"
    ], size=10.5, color=INK, lh=1.4))

    # Стрілка з Healthy в Draining
    p.append(line(x1 + 30, y1 + bh + 5, x1 + 30, 360, color="#d97706", sw=1.8))
    p.append(arrow(x1 + 30, 360, x4 - 5, 360, color="#d97706", sw=1.8))
    p.append(text(135, 350, "Деплой / Рестарт", size=10, color="#b45309"))

    render(os.path.join(OUT, "health-checking-drain-lifecycle.svg"), W, H, *p)

if __name__ == "__main__":
    fig_l4_vs_l7()
    fig_buffering_backpressure()
    fig_load_balancing_algorithms()
    fig_health_drain_lifecycle()
    print("Всі 4 фігури успішно згенеровано у img/")
