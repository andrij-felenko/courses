# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=11, pad=8, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Архітектурне розмежування L4 та L7 ────────────────────────────
def fig_l4_vs_l7_architecture():
    W, H = 1040, 530
    frags = []

    frags.append(text(520, 28, "Порівняння архітектури балансування на 4-му (L4) та 7-му (L7) рівнях OSI", size=15, bold=True))

    # Секція L4 (Транспортний рівень)
    frags.append(rect(20, 55, 485, 455, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(262, 82, "L4: Балансування транспортного рівня (TCP / UDP)", size=13, bold=True, color=NEG))

    frags.append(box(85, 145, "Клієнт\n(IP: 198.51.100.2)\nSrcPort: 54321", size=10, fill="#ffffff", stroke=MUTED, min_w=115))
    frags.append(arrow(145, 145, 175, 145, color=NEG, sw=1.5))

    frags.append(box(265, 145, "L4 Балансувальник (VIP)\nСелекція за 5-tuple:\n(SrcIP, SrcPort, DstIP, DstPort, Proto)\nБез розшифрування TLS", size=10, bold=True, fill="#e8f0ff", stroke=NEG, min_w=175))

    frags.append(arrow(355, 145, 385, 145, color=NEG, sw=1.5))
    frags.append(box(440, 145, "Бекенд A\n(IP: 10.0.1.10)\nТермінація\nTCP / TLS", size=9, fill="#ffffff", stroke=MUTED, min_w=95))

    # Пояснення L4 характеристик
    frags.append(rect(35, 215, 455, 275, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    frags.append(text(262, 238, "Ключові властивості L4:", size=11, bold=True, color=INK))
    frags.append(mtext(262, 265, [
        "• Семантична сліпота: балансувальник не знає про HTTP, куки, URI чи заголовки.",
        "• Маршрутизація з'єднань: усе TCP-з'єднання цілком закріплюється за одним бекендом.",
        "• Продуктивність: мільйони пакетів за секунду (Mpps) при мінімальному CPU.",
        "• Робота з пакетами: трансляція адрес (NAT) або пряма підміна MAC-адрес (DSR).",
        "• Протокол TLS: наскрізне шифрування між клієнтом і бекендом (Pass-through)."
    ], size=10, color=INK, lh=1.5))

    # Секція L7 (Прикладний рівень)
    frags.append(rect(535, 55, 485, 455, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(777, 82, "L7: Балансування прикладного рівня (HTTP / gRPC / TLS)", size=13, bold=True, color=POS))

    frags.append(box(595, 145, "Клієнт\nTCP Con 1\nTLS Handshake", size=10, fill="#ffffff", stroke=MUTED, min_w=105))
    frags.append(arrow(650, 145, 680, 145, color=POS, sw=1.5))

    frags.append(box(775, 145, "L7 Проксі (Envoy/NGINX)\nТермінація TLS + розбір HTTP\n/api/orders -> Бекенд A\n/static/* -> Бекенд B", size=10, bold=True, fill="#fff5f5", stroke=POS, min_w=180))

    frags.append(arrow(867, 130, 895, 120, color=POS, sw=1.5))
    frags.append(box(955, 115, "Бекенд A (/api)\nTCP Con 2", size=9, fill="#ffffff", stroke=MUTED, min_w=100))

    frags.append(arrow(867, 160, 895, 170, color=POS, sw=1.5))
    frags.append(box(955, 175, "Бекенд B (Статика)\nTCP Con 3", size=9, fill="#ffffff", stroke=MUTED, min_w=100))

    # Пояснення L7 характеристик
    frags.append(rect(550, 215, 455, 275, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    frags.append(text(777, 238, "Ключові властивості L7:", size=11, bold=True, color=INK))
    frags.append(mtext(777, 265, [
        "• Семантична обізнаність: аналіз URI, методів, заголовків, Cookie, JWT-токенів.",
        "• Два окремих TCP-стеки: з'єднання клієнт ⟷ проксі та проксі ⟷ бекенд.",
        "• Розумна маршрутизація: розщеплення запитів з одного клієнтського TCP-потоку.",
        "• Розширені можливості: повтор запитів (retries), канареечні релізи, кешування, gRPC.",
        "• Витрати ресурсів: значне споживання пам'яті під буфери та CPU під TLS/парсинг."
    ], size=10, color=INK, lh=1.5))

    return render(os.path.join(IMG, 'l4-vs-l7-architecture.svg'), W, H, *frags)


# ── Фігура 2: Пастка мультиплексування HTTP/2 на 4-му рівні ────────────────
def fig_http2_multiplexing_l4_trap():
    W, H = 1040, 500
    frags = []

    frags.append(text(520, 28, "Пастка мультиплексування HTTP/2 та gRPC: чому L4 ламає розподіл навантаження", size=15, bold=True))

    # Ліва частина: L4 з HTTP/2 (Проблема)
    frags.append(rect(20, 55, 485, 425, fill="#fffaf9", stroke=POS, sw=1.2, rx=6))
    frags.append(text(262, 82, "1. Спроба балансувати HTTP/2 через L4 (Збій розподілу)", size=12, bold=True, color=POS))

    frags.append(box(105, 140, "1 Клієнт (gRPC / HTTP/2)\n100 паралельних запитів\nв 1 TCP-з'єднанні", size=9, fill="#ffffff", stroke=MUTED, min_w=150))
    frags.append(arrow(182, 140, 218, 140, color=POS, sw=1.5))

    frags.append(box(285, 140, "L4 Балансувальник\nБачить 1 TCP потік\n-> Шле на 1 сервер", size=9, bold=True, fill="#fff5f5", stroke=POS, min_w=125))

    frags.append(arrow(350, 140, 385, 140, color=POS, sw=1.5))

    frags.append(box(440, 140, "Сервер A: 100 req\nCPU: 100% (Колапс!)", size=9, bold=True, fill="#fdecea", stroke=POS, min_w=100))
    frags.append(box(440, 220, "Сервер B: 0 req\nCPU: 1% (Простоює)", size=9, fill="#ffffff", stroke=MUTED, min_w=100))
    frags.append(box(440, 290, "Сервер C: 0 req\nCPU: 1% (Простоює)", size=9, fill="#ffffff", stroke=MUTED, min_w=100))

    frags.append(rect(35, 360, 455, 105, fill="#ffffff", stroke=POS, sw=1, rx=4))
    frags.append(mtext(262, 380, [
        "Наслідок: L4 не розуміє мультиплексовані фрейми всередині TCP.",
        "Усі 100 запитів летять в один сервер, руйнуючи горизонтальне масштабування.",
        "Сервери B і C залишаються порожніми, а сервер A падає від OOM або таймаутів."
    ], size=9, color=POS, lh=1.4))

    # Права частина: L7 з HTTP/2 (Правильне рішення)
    frags.append(rect(535, 55, 485, 425, fill="#f9fcf9", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(777, 82, "2. Балансування HTTP/2 через L7 (Коректний розподіл)", size=12, bold=True, color=FIELD))

    frags.append(box(620, 140, "1 Клієнт (gRPC / HTTP/2)\n100 паралельних запитів\nв 1 TCP-з'єднанні", size=9, fill="#ffffff", stroke=MUTED, min_w=150))
    frags.append(arrow(697, 140, 733, 140, color=FIELD, sw=1.5))

    frags.append(box(805, 140, "L7 Проксі (Envoy)\nТермінує TCP, демультиплексує\n100 потоків на рівні кадрів", size=9, bold=True, fill="#eafaf0", stroke=FIELD, min_w=135))

    frags.append(arrow(875, 130, 905, 130, color=FIELD, sw=1.5))
    frags.append(arrow(875, 145, 905, 210, color=FIELD, sw=1.5))
    frags.append(arrow(875, 155, 905, 280, color=FIELD, sw=1.5))

    frags.append(box(960, 140, "Сервер A: 33 req\nCPU: 33% (Норма)", size=9, fill="#ffffff", stroke=FIELD, min_w=100))
    frags.append(box(960, 220, "Сервер B: 33 req\nCPU: 33% (Норма)", size=9, fill="#ffffff", stroke=FIELD, min_w=100))
    frags.append(box(960, 290, "Сервер C: 34 req\nCPU: 34% (Норма)", size=9, fill="#ffffff", stroke=FIELD, min_w=100))

    frags.append(rect(550, 360, 455, 105, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    frags.append(mtext(777, 380, [
        "Результат: L7 розбирає HTTP/2 потоки (Streams) і розподіляє кожен запит окремо.",
        "Пул бекендів навантажується рівномірно, хвостова затримка (p99) мінімізується.",
        "Ефективне використання ресурсів усього парку машин без перекосів."
    ], size=9, color=FIELD, lh=1.4))

    return render(os.path.join(IMG, 'http2-multiplexing-l4-trap.svg'), W, H, *frags)


# ── Фігура 3: Дворівнева архітектура (L4 Edge + L7 Fleet) ───────────────────
def fig_two_tier_edge_load_balancing():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 28, "Дворівнева архітектура балансування: масштабування межі (L4) та логіки (L7)", size=15, bold=True))

    # Рівень 0: Клієнти та Anycast
    frags.append(box(120, 110, "Клієнти в Інтернеті\nМільйони підключень\n(Єдина Anycast IP)", size=10, fill="#ffffff", stroke=MUTED, min_w=150))
    frags.append(arrow(200, 110, 250, 110, color=MUTED, sw=1.5))

    # Рівень 1: L4 Edge Tier
    frags.append(rect(265, 55, 225, 440, fill="#f0f4ff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(377, 82, "Рівень 1: L4 Межа (Edge)", size=12, bold=True, color=NEG))

    frags.append(box(377, 130, "BGP Router (ECMP)\nРозподіл за 5-tuple хешем", size=9, fill="#ffffff", stroke=MUTED, min_w=190))
    frags.append(arrow(377, 155, 377, 185, color=NEG, sw=1.5))

    frags.append(box(377, 220, "L4 Вузли (Katran / Maglev)\nКонсистентне хешування\nПакетна швидкість (Mpps)\nІнкапсуляція (GRE / IPIP)", size=10, bold=True, fill="#e8f0ff", stroke=NEG, min_w=195))

    frags.append(rect(280, 310, 195, 170, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(377, 330, [
        "Функції L4 Edge:",
        "• Поглинання DDoS-атак",
        "• Anycast-маршрутизація",
        "• Захист від втрати сесій",
        "  при падінні L7 вузлів",
        "• Stateless або мін. стан"
    ], size=9, color=INK, lh=1.4))

    frags.append(arrow(490, 220, 525, 220, color=NEG, sw=1.5))

    # Рівень 2: L7 Fleet Tier
    frags.append(rect(535, 55, 225, 440, fill="#fffaf5", stroke="#d35400", sw=1.2, rx=6))
    frags.append(text(647, 82, "Рівень 2: L7 Пул (Proxies)", size=12, bold=True, color="#d35400"))

    frags.append(box(647, 130, "L7 Proxy 1 (Envoy)\nTLS, WAF, Routing", size=9, fill="#ffffff", stroke=MUTED, min_w=180))
    frags.append(box(647, 190, "L7 Proxy 2 (Envoy)\nTLS, WAF, Routing", size=9, fill="#ffffff", stroke=MUTED, min_w=180))
    frags.append(box(647, 250, "L7 Proxy 3 (Envoy)\nTLS, WAF, Routing", size=9, fill="#ffffff", stroke=MUTED, min_w=180))

    frags.append(rect(550, 310, 195, 170, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(647, 330, [
        "Функції L7 Fleet:",
        "• Термінація TLS/HTTPS",
        "• Авторизація (JWT/mTLS)",
        "• Path-based routing",
        "• Retry, Circuit Breaking",
        "• Автомасштабування (HPA)"
    ], size=9, color=INK, lh=1.4))

    frags.append(arrow(760, 190, 795, 190, color="#d35400", sw=1.5))

    # Рівень 3: Мікросервіси
    frags.append(rect(805, 55, 175, 440, fill="#fcfdfe", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(892, 82, "Рівень 3: Сервіси", size=12, bold=True, color=FIELD))

    frags.append(box(892, 130, "Auth Service\n(gRPC / HTTP)", size=9, fill="#ffffff", stroke=FIELD, min_w=145))
    frags.append(box(892, 200, "Order Service\n(Бізнес-логіка)", size=9, fill="#ffffff", stroke=FIELD, min_w=145))
    frags.append(box(892, 270, "Payment Service\n(Транзакції)", size=9, fill="#ffffff", stroke=FIELD, min_w=145))
    frags.append(box(892, 340, "Media Storage\n(Статика)", size=9, fill="#ffffff", stroke=FIELD, min_w=145))

    return render(os.path.join(IMG, 'two-tier-edge-load-balancing.svg'), W, H, *frags)


# ── Фігура 4: Пряма відповідь сервера (Direct Server Return, DSR) ────────────
def fig_direct_server_return():
    W, H = 980, 480
    frags = []

    frags.append(text(490, 28, "Пряма відповідь сервера (Direct Server Return, DSR): асиметричний обхід вузьких місць", size=15, bold=True))

    # Клієнт
    frags.append(box(110, 140, "Клієнт\nIP: 198.51.100.2\nШле GET-запит (~1 КБ)", size=10, fill="#ffffff", stroke=MUTED, min_w=145))

    # L4 Балансувальник DSR
    frags.append(box(490, 140, "L4 Балансувальник (VIP)\nПідміняє лише MAC-адресу\n(IP-заголовки незмінні: Dst=VIP)\nНавантаження лише на Ingress", size=10, bold=True, fill="#e8f0ff", stroke=NEG, min_w=245))

    # Бекенд
    frags.append(box(850, 140, "Бекенд-вузол (Real Server)\nIP: 10.0.1.50\nVIP налаштовано на lo:0 (no ARP)\nФормує відповідь (~10 МБ)", size=10, bold=True, fill="#eafaf0", stroke=FIELD, min_w=200))

    # Маршрутизатор за замовчуванням (Default Gateway / Router)
    frags.append(box(490, 360, "Мережевий комутатор / Шлюз (Internet Gateway)\nПрямий транзит трафіку в Інтернет", size=10, fill="#ffffff", stroke=MUTED, min_w=280))

    # Кроки зі стрілками
    # Крок 1: Клієнт -> L4
    frags.append(arrow(185, 140, 360, 140, color=NEG, sw=1.8))
    frags.append(text(272, 125, "1. Малий запит (1 КБ)", size=10, bold=True, color=NEG))
    frags.append(text(272, 160, "Src: 198.51.100.2, Dst: VIP", size=9, color=MUTED))

    # Крок 2: L4 -> Бекенд
    frags.append(arrow(620, 140, 740, 140, color=NEG, sw=1.8))
    frags.append(text(680, 125, "2. MAC Rewrite / IPIP", size=10, bold=True, color=NEG))
    frags.append(text(680, 160, "Dst IP все ще VIP!", size=9, color=MUTED))

    # Крок 3: Бекенд -> Шлюз (початок зворотної прямої відповіді)
    frags.append(arrow(850, 195, 630, 340, color=FIELD, sw=2))
    frags.append(text(775, 275, "3. Велика відповідь (10 МБ)", size=10, bold=True, color=FIELD))
    frags.append(text(775, 295, "Src: VIP, Dst: 198.51.100.2", size=9, color=FIELD))

    # Крок 4: Шлюз -> Клієнт
    frags.append(arrow(350, 360, 110, 195, color=FIELD, sw=2))
    frags.append(text(205, 305, "4. Пряма доставка клієнту", size=10, bold=True, color=FIELD))
    frags.append(text(205, 325, "В обхід L4 балансувальника!", size=9, bold=True, color=POS))

    # Пояснювальний блок унизу
    frags.append(rect(40, 415, 900, 50, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    frags.append(text(490, 445, "Ефект DSR: вихідний потік у 10–100 разів більший за вхідний. L4-балансувальник не є вузьким місцем для гігабітів трафіку.", size=10, bold=True, color=INK))

    return render(os.path.join(IMG, 'direct-server-return.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_l4_vs_l7_architecture()
    fig_http2_multiplexing_l4_trap()
    fig_two_tier_edge_load_balancing()
    fig_direct_server_return()
    print("All figures generated successfully.")
