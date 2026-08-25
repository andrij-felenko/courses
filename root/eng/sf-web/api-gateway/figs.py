# -*- coding: utf-8 -*-
"""Фігури теми «API-шлюз». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"

# ── 1. direct-vs-gateway: прямий доступ клієнтів проти єдиної брами ────────
def fig_direct_vs_gateway():
    W, H = 1000, 420
    f = []

    # Ліва половина: Прямі з'єднання (n * m заплутаність)
    f.append(rect(20, 20, 460, 375, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(250, 48, "Прямий доступ: клієнти знають про всі сервіси", size=14, bold=True, color=POS))

    # Клієнти зліва
    clients_y = [110, 200, 290]
    c_labels = ["Мобільний\nзастосунок", "Веб-браузер\n(SPA)", "Сторонній\nпартнер"]
    for y, lbl in zip(clients_y, c_labels):
        b, _, _ = textbox(90, y, lbl, size=12, bold=True, min_w=110, pad=8, fill=FILL, stroke=LINE)
        f.append(b)

    # Внутрішні мікросервіси зліва
    services_y = [90, 160, 230, 300, 360]
    s_labels = ["Сервіс користувачів (:8081)", "Сервіс замовлень (:8082)", "Сервіс платежів (:8083)", "Сервіс товарів (:8084)", "Сервіс сповіщень (:8085)"]
    for y, lbl in zip(services_y, s_labels):
        b, _, _ = textbox(370, y, lbl, size=11, min_w=170, pad=6, fill=RED_F, stroke=POS)
        f.append(b)

    # Павутиння стрілок
    for cy in clients_y:
        for sy in [90, 160, 230, 300, 360]:
            f.append(line(150, cy, 275, sy, color="#e74c3c", sw=1, dash="3,3"))

    f.append(text(250, 385, "✗ 15 WAN-з'єднань, TLS і токени в кожному сервісі", size=11, color=POS, italic=True))

    # Права половина: Через API-шлюз (одні вхідні двері)
    f.append(rect(520, 20, 460, 375, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(750, 48, "API-шлюз: єдина точка входу на периметрі", size=14, bold=True, color=FIELD))

    # Клієнти справа
    for y, lbl in zip(clients_y, c_labels):
        b, _, _ = textbox(580, y, lbl, size=12, bold=True, min_w=100, pad=8, fill=FILL, stroke=LINE)
        f.append(b)

    # Шлюз по центру правої половини
    gw_box, _, _ = textbox(740, 200, "API-ШЛЮЗ\n(Edge Gateway)\n\n• TLS / WAF\n• JWT-автентифікація\n• Rate limiting\n• Маршрутизація",
                           size=11, bold=True, min_w=125, pad=10, fill=BLUE_F, stroke=NEG, sw=1.8)
    f.append(gw_box)

    # Внутрішні мікросервіси справа
    for y, lbl in zip(services_y, s_labels):
        b, _, _ = textbox(900, y, lbl.split(" (")[0], size=11, min_w=130, pad=6, fill=GREEN_F, stroke=FIELD)
        f.append(b)

    # Вхідні стрілки до шлюзу
    for cy in clients_y:
        f.append(arrow(635, cy, 672, 200, color=NEG, sw=1.5))

    # Вихідні стрілки від шлюзу
    for sy in services_y:
        f.append(arrow(808, 200, 830, sy, color=FIELD, sw=1.3))

    f.append(text(750, 385, "✓ 1 публічна IP, TLS на краю, чиста приватна мережа", size=11, color=FIELD, italic=True))

    render(out("direct-vs-gateway.svg"), W, H, *f,
           title="Пряме підключення клієнтів проти архітектури з API-шлюзом")


# ── 2. gateway-pipeline: внутрішній конвеєр обробки запиту ──────────────────
def fig_gateway_pipeline():
    W, H = 1000, 260
    f = []

    f.append(rect(10, 10, 980, 240, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 36, "Конвеєр фільтрів API-шлюзу (Request Processing Pipeline)", size=14, bold=True))

    stages = [
        ("1. Вхідний слухач", "TCP / TLS\nHTTP/1.1, HTTP/2, gRPC\nALPN узгодження", 90),
        ("2. Ліміт запитів", "Token Bucket\nRate Limit за IP/Tenant\n429 Too Many Requests", 270),
        ("3. Автентифікація", "Валідація JWT/OAuth2\nОчищення X-User-Id\nВпорскування Claims", 450),
        ("4. Маршрутизатор", "Зіставлення path/headers\nПереписування URL\nВибір Upstream Cluster", 630),
        ("5. Стійкість та виклик", "Circuit Breaker\nТаймаути й ретраї\nПул з'єднань (Keep-Alive)", 810)
    ]

    for title, desc, cx in stages:
        f.append(rect(cx - 80, 60, 160, 130, fill=FILL, stroke=LINE, sw=1.2, rx=6))
        f.append(text(cx, 82, title, size=12, bold=True, color=INK))
        f.append(line(cx - 70, 92, cx + 70, 92, color=MUTED, sw=0.8))
        f.append(mtext(cx, 115, desc.split("\n"), size=10.5, color=INK, lh=1.35))

    # Стрілки між фільтрами
    for i in range(len(stages) - 1):
        x1 = stages[i][2] + 80
        x2 = stages[i+1][2] - 80
        f.append(arrow(x1, 125, x2, 125, color=NEG, sw=1.8))

    # Стрілка на вході та виході
    f.append(arrow(20, 125, stages[0][2] - 80, 125, color=POS, sw=2))
    f.append(text(35, 110, "Клієнт", size=11, bold=True, color=POS, anchor="start"))

    f.append(arrow(stages[-1][2] + 80, 125, 965, 125, color=FIELD, sw=2))
    f.append(text(965, 110, "Бекенд", size=11, bold=True, color=FIELD, anchor="end"))

    f.append(text(500, 222, "Кожен фільтр може перервати запит (401, 403, 429, 503) або збагатити його заголовками перед наступним кроком",
                  size=11, color=MUTED, italic=True))

    render(out("gateway-pipeline.svg"), W, H, *f,
           title="Послідовність фільтрів під час проходження запиту крізь API-шлюз")


# ── 3. north-south-vs-east-west: Північ-Південь проти Схід-Захід ─────────────
def fig_north_south_vs_east_west():
    W, H = 960, 380
    f = []

    # Недовірена публічна зона (Зовнішній інтернет)
    f.append(rect(20, 20, 920, 80, fill="#fdf2e9", stroke="#e67e22", sw=1.2, rx=8))
    f.append(text(50, 45, "ПУБЛІЧНИЙ ІНТЕРНЕТ (Недовірена зона, глобальний WAN)", size=12, bold=True, color="#d35400", anchor="start"))
    f.append(textbox(200, 70, "Мобільний клієнт", size=11, pad=6, fill=FILL)[0])
    f.append(textbox(480, 70, "Веб-браузер (SPA)", size=11, pad=6, fill=FILL)[0])
    f.append(textbox(760, 70, "Сторонній API-партнер", size=11, pad=6, fill=FILL)[0])

    # Стрілка Північ-Південь
    f.append(arrow(480, 100, 480, 135, color=POS, sw=2.5))
    f.append(text(500, 120, "Північ-Південь (North-South): публічний TLS, автентифікація, ліміти", size=11, bold=True, color=POS, anchor="start"))

    # Межа периметра — API Gateway
    f.append(rect(160, 140, 640, 50, fill=BLUE_F, stroke=NEG, sw=1.8, rx=6))
    f.append(text(480, 168, "API-ШЛЮЗ (Периметр кластера / Ingress Edge)", size=13, bold=True, color=NEG))

    # Стрілка проходу через шлюз
    f.append(arrow(480, 190, 480, 225, color=FIELD, sw=2.5))

    # Довірена внутрішня зона (VPC / Kubernetes Cluster)
    f.append(rect(20, 230, 920, 135, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=8))
    f.append(text(50, 252, "ПРИВАТНИЙ КЛАСТЕР / СЕРВІСНА СІТКА (Trusted Mesh / VPC)", size=12, bold=True, color=FIELD, anchor="start"))

    # Сервіси всередині
    s1, _, _ = textbox(180, 295, "Сервіс Auth\n(Pod + Sidecar)", size=11, pad=8, fill=FILL, stroke=LINE)
    s2, _, _ = textbox(480, 295, "Сервіс Замовлень\n(Pod + Sidecar)", size=11, pad=8, fill=FILL, stroke=LINE)
    s3, _, _ = textbox(780, 295, "Сервіс Платежів\n(Pod + Sidecar)", size=11, pad=8, fill=FILL, stroke=LINE)
    f.append(s1); f.append(s2); f.append(s3)

    # Схід-Захід трафік між сервісами
    f.append(arrow(260, 295, 390, 295, color="#8e44ad", sw=1.8))
    f.append(arrow(390, 305, 260, 305, color="#8e44ad", sw=1.8))
    f.append(arrow(570, 295, 690, 295, color="#8e44ad", sw=1.8))
    f.append(arrow(690, 305, 570, 305, color="#8e44ad", sw=1.8))

    f.append(text(480, 350, "Схід-Захід (East-West): взаємний mTLS, внутрішній RBAC, балансування через Service Mesh (Envoy sidecars)",
                  size=11, bold=True, color="#8e44ad"))

    render(out("north-south-vs-east-west.svg"), W, H, *f,
           title="Розподіл трафіку: Північ-Південь (API-шлюз) проти Схід-Захід (Service Mesh)")


# ── 4. aggregation-vs-esb: Агрегація на шлюзі проти пастки ESB ──────────────
def fig_aggregation_vs_esb():
    W, H = 980, 360
    f = []

    # Ліворуч: Розумний Scatter-Gather (легка агрегація)
    f.append(rect(20, 20, 450, 320, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(245, 48, "Легка агрегація (Scatter-Gather)", size=13, bold=True, color=FIELD))

    f.append(textbox(75, 160, "Клієнт\n(1 HTTP GET)", size=11, pad=8, fill=FILL)[0])
    f.append(arrow(125, 160, 175, 160, color=LINE, sw=1.5))

    f.append(textbox(245, 160, "Шлюз\n(Паралельні запити\nі склеювання JSON)", size=11, pad=8, fill=BLUE_F, stroke=NEG)[0])

    f.append(arrow(315, 140, 365, 100, color=FIELD, sw=1.4))
    f.append(arrow(315, 160, 365, 160, color=FIELD, sw=1.4))
    f.append(arrow(315, 180, 365, 220, color=FIELD, sw=1.4))

    f.append(textbox(415, 100, "Сервіс A", size=10.5, pad=6, fill=FILL)[0])
    f.append(textbox(415, 160, "Сервіс B", size=10.5, pad=6, fill=FILL)[0])
    f.append(textbox(415, 220, "Сервіс C", size=10.5, pad=6, fill=FILL)[0])

    f.append(text(245, 280, "✓ «Розумні вузли, прості труби»", size=11, bold=True, color=FIELD))
    f.append(text(245, 305, "Шлюз лише збирає DTO, без бізнес-правил", size=10.5, color=MUTED, italic=True))

    # Праворуч: Антипатерн «Розумна шина / Монолітний ESB»
    f.append(rect(510, 20, 450, 320, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(735, 48, "Антипатерн: Перевантажений ESB", size=13, bold=True, color=POS))

    f.append(textbox(565, 160, "Клієнт", size=11, pad=8, fill=FILL)[0])
    f.append(arrow(605, 160, 650, 160, color=LINE, sw=1.5))

    f.append(textbox(735, 160, "Шлюз-Монстр (ESB)\n• Бізнес-оркестрація\n• Складна валідація\n• SQL/транзакції\n• Перетворення схем",
                     size=10.5, pad=8, fill=RED_F, stroke=POS, bold=True)[0])

    f.append(arrow(820, 140, 865, 100, color=POS, sw=1.4))
    f.append(arrow(820, 160, 865, 160, color=POS, sw=1.4))
    f.append(arrow(820, 180, 865, 220, color=POS, sw=1.4))

    f.append(textbox(910, 100, "Сервіс A", size=10.5, pad=6, fill=FILL)[0])
    f.append(textbox(910, 160, "Сервіс B", size=10.5, pad=6, fill=FILL)[0])
    f.append(textbox(910, 220, "Сервіс C", size=10.5, pad=6, fill=FILL)[0])

    f.append(text(735, 280, "✗ «Дурні вузли, надрозумна труба»", size=11, bold=True, color=POS))
    f.append(text(735, 305, "Вузьке місце команд, єдина точка відмови", size=10.5, color=POS, italic=True))

    render(out("aggregation-vs-esb.svg"), W, H, *f,
           title="Легка агрегація на шлюзі проти антипатерну роздутої шини підприємства (ESB)")


if __name__ == "__main__":
    fig_direct_vs_gateway()
    fig_gateway_pipeline()
    fig_north_south_vs_east_west()
    fig_aggregation_vs_esb()
    print("OK: generated 4 figures for api-gateway")
