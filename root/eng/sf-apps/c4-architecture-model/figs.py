# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра для C4 діаграм
SYS_BG   = "#dbeafe"   # Світло-синій для власної системи
SYS_BD   = "#1e40af"   # Темно-синій контур
EXT_BG   = "#f3f4f6"   # Нейтральний сірий для зовнішніх систем
EXT_BD   = "#4b5563"   # Сірий контур
PER_BG   = "#dcfce7"   # Світло-зелений для людей / персон
PER_BD   = "#15803d"   # Зелений контур
DB_BG    = "#fef3c7"   # Світло-жовтий для баз даних / сховищ
DB_BD    = "#b45309"   # Жовто-коричневий контур
CMP_BG   = "#ede9fe"   # Світло-фіолетовий для компонентів
CMP_BD   = "#6d28d9"   # Фіолетовий контур
NODE_BG  = "#f8fafc"   # Майже білий для вузлів розгортання
NODE_BD  = "#64748b"   # Сіро-блакитний контур

def c4_box(cx, cy, w, h, title, type_label, desc="", tech="", fill=SYS_BG, stroke=SYS_BD, rx=8):
    """Стандартизована C4 коробка: Назва, [Тип: Технологія], Опис."""
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=rx)
    
    # Заголовок
    sub_tag = f"[{type_label}]" if not tech else f"[{type_label}: {tech}]"
    
    if desc:
        out += text(cx, cy - h/2 + 20, title, size=13, color=INK, bold=True)
        out += text(cx, cy - h/2 + 36, sub_tag, size=10, color=MUTED, italic=True)
        # Опис (до 2 рядків)
        desc_lines = desc.split("\n")
        out += mtext(cx, cy - h/2 + 54, desc_lines, size=10, color=INK, lh=1.25)
    else:
        out += text(cx, cy - 8, title, size=13, color=INK, bold=True)
        out += text(cx, cy + 10, sub_tag, size=10, color=MUTED, italic=True)
        
    return out

def c4_person(cx, cy, label, role="Користувач", w=130, h=70):
    """Символ персони (людина) з головою та тілом."""
    out = circle(cx, cy - h/2 - 12, 13, fill=PER_BG, stroke=PER_BD, sw=1.8)
    out += c4_box(cx, cy + 4, w, h, label, "Person", role, fill=PER_BG, stroke=PER_BD, rx=10)
    return out

def c4_db(cx, cy, w, h, title, tech="База даних", desc="", fill=DB_BG, stroke=DB_BD):
    """Коробка сховища даних (із верхнім еліпсом-маркером циліндра)."""
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=6)
    # Декоративні лінії циліндра зверху
    out += line(x, y + 10, x + w, y + 10, color=stroke, sw=1.2)
    
    sub_tag = f"[Container: {tech}]"
    if desc:
        out += text(cx, cy - h/2 + 25, title, size=12.5, color=INK, bold=True)
        out += text(cx, cy - h/2 + 40, sub_tag, size=9.5, color=MUTED, italic=True)
        desc_lines = desc.split("\n")
        out += mtext(cx, cy - h/2 + 56, desc_lines, size=9.5, color=INK, lh=1.25)
    else:
        out += text(cx, cy - 3, title, size=12.5, color=INK, bold=True)
        out += text(cx, cy + 13, sub_tag, size=9.5, color=MUTED, italic=True)
    return out

def c4_edge(x1, y1, x2, y2, verb="", proto="", lx=None, ly=None, color=LINE, sw=1.6):
    """Зв'язок C4: стрілка з дієсловом дії та протоколом."""
    out = arrow(x1, y1, x2, y2, color=color, sw=sw)
    if verb and lx is not None and ly is not None:
        out += text(lx, ly - 6, verb, size=10, color=INK, bold=True)
        if proto:
            out += text(lx, ly + 8, f"[{proto}]", size=9, color=MUTED, italic=True)
    return out


# ── 1. Ієрархія масштабів C4 ────────────────────────────────────────────────
def fig_hierarchy_zoom():
    W, H = 840, 480
    p = []
    p.append(text(W / 2, 28, "Ієрархічні рівні деталізації моделі C4", size=16, bold=True))
    p.append(text(W / 2, 48, "Принцип поступового наближення (zoom in) від бізнес-оточення до коду", size=11, color=MUTED, italic=True))

    levels = [
        ("1. Контекст (Context)", "Для кого система і з чим вона межує?", "Люди, бізнес-системи,\nзовнішні інтеграції", SYS_BG, SYS_BD),
        ("2. Контейнери (Containers)", "Які розгортальні вузли утворюють систему?", "Сервіси, клієнти, бази даних,\nброкери повідомлень", CMP_BG, CMP_BD),
        ("3. Компоненти (Components)", "Як влаштований конкретний контейнер?", "Контролери, сервіси логіки,\nрепозиторії, адаптери", PER_BG, PER_BD),
        ("4. Код (Code)", "Яка точна реалізація окремого компонента?", "Класи, структури, інтерфейси,\nпатерни проектування", DB_BG, DB_BD),
    ]

    card_w = 185
    card_h = 240
    start_x = 50
    spacing = 195

    for i, (title, question, details, fill, stroke) in enumerate(levels):
        cx = start_x + i * spacing + card_w / 2
        cy = 190
        
        # Рамка рівня
        p.append(rect(start_x + i * spacing, cy - card_h/2, card_w, card_h, fill=fill, stroke=stroke, sw=2, rx=10))
        
        # Рівень номер
        p.append(circle(cx, cy - card_h/2 + 26, 15, fill="#ffffff", stroke=stroke, sw=2))
        p.append(text(cx, cy - card_h/2 + 31, f"L{i+1}", size=12, color=stroke, bold=True))
        
        # Заголовок
        p.append(text(cx, cy - card_h/2 + 62, title.split(" ")[1], size=13, color=INK, bold=True))
        p.append(text(cx, cy - card_h/2 + 78, f"({title.split('(')[1]}", size=10, color=MUTED))
        
        # Лінія розділу
        p.append(line(cx - 75, cy - card_h/2 + 92, cx + 75, cy - card_h/2 + 92, color=stroke, sw=1, dash="3,3"))
        
        # Ключове питання
        p.append(text(cx, cy - card_h/2 + 112, "Ключове питання:", size=10, color=MUTED, bold=True))
        q_lines = question.split(" ")
        mid = len(q_lines) // 2
        q1 = " ".join(q_lines[:mid])
        q2 = " ".join(q_lines[mid:])
        p.append(text(cx, cy - card_h/2 + 128, q1, size=10, color=INK))
        p.append(text(cx, cy - card_h/2 + 142, q2, size=10, color=INK))
        
        # Лінія розділу
        p.append(line(cx - 75, cy - card_h/2 + 158, cx + 75, cy - card_h/2 + 158, color=stroke, sw=1, dash="3,3"))
        
        # Будівельні блоки
        p.append(text(cx, cy - card_h/2 + 176, "Елементи моделі:", size=10, color=MUTED, bold=True))
        p.append(mtext(cx, cy - card_h/2 + 192, details.split("\n"), size=9.5, color=INK, lh=1.25))

        # Стрілка наближення до наступного рівня
        if i < 3:
            arrow_x1 = start_x + (i + 1) * spacing - 10
            arrow_x2 = start_x + (i + 1) * spacing + 10
            p.append(arrow(arrow_x1, cy, arrow_x2, cy, color=LINE, sw=2))
            p.append(text((arrow_x1 + arrow_x2) / 2, cy - 12, "zoom", size=9, color=MUTED, italic=True))

    # Нижній банер про цільову аудиторію
    p.append(rect(50, 345, 740, 95, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(W / 2, 368, "Розподіл цільової аудиторії за рівнями:", size=12, bold=True))
    p.append(text(140, 395, "L1: Бізнес, керівники, всі інженери", size=10, color=SYS_BD, bold=True))
    p.append(text(335, 395, "L2: Архітектори, розробники, DevOps/SRE", size=10, color=CMP_BD, bold=True))
    p.append(text(535, 395, "L3: Команда розробки сервісу", size=10, color=PER_BD, bold=True))
    p.append(text(710, 395, "L4: Автор модуля / IDE", size=10, color=DB_BD, bold=True))
    p.append(text(W / 2, 422, "Правило C4: кожна діаграма розрахована на конкретну аудиторію та відповідає на одне запитання.", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "c4-hierarchy-zoom.svg"), W, H, *p)


# ── 2. Рівень 1: System Context ─────────────────────────────────────────────
def fig_context_diagram():
    W, H = 840, 480
    p = []
    p.append(text(W / 2, 28, "Рівень 1 (Context): Платіжна платформа у бізнес-оточенні", size=16, bold=True))
    p.append(text(W / 2, 48, "Окреслює систему як чорну скриньку, користувачів і суміжні зовнішні системи", size=11, color=MUTED, italic=True))

    # Центральна система
    cs_x, cs_y = W / 2, 240
    p.append(c4_box(cs_x, cs_y, 220, 110, "Платіжна платформа", "Software System",
                    "Обробляє платежі, керує\nгаманцями та транзакціями",
                    fill=SYS_BG, stroke=SYS_BD, rx=8))

    # Персона 1: Покупець (ліворуч зверху)
    p1_x, p1_y = 120, 150
    p.append(c4_person(p1_x, p1_y, "Покупець", "Здійснює онлайн-покупки\nта переказує кошти", w=150, h=75))
    p.append(c4_edge(p1_x + 75, p1_y + 15, cs_x - 110, cs_y - 20, "Оплачує замовлення", "HTTPS", lx=245, ly=165))

    # Персона 2: Мерчант (ліворуч знизу)
    p2_x, p2_y = 120, 330
    p.append(c4_person(p2_x, p2_y, "Мерчант / Торговець", "Переглядає звіти,\nкерує виплатами", w=150, h=75))
    p.append(c4_edge(p2_x + 75, p2_y - 5, cs_x - 110, cs_y + 25, "Отримує аналітику та звіти", "HTTPS", lx=245, ly=300))

    # Зовнішня система 1: Банківський шлюз (праворуч зверху)
    e1_x, e1_y = 710, 140
    p.append(c4_box(e1_x, e1_y, 170, 85, "Банківський еквайринг", "External System",
                    "Проводить кліринг карток\nVisa / Mastercard", fill=EXT_BG, stroke=EXT_BD))
    p.append(c4_edge(cs_x + 110, cs_y - 30, e1_x - 85, e1_y + 10, "Створює транзакції", "ISO 8583 / TLS", lx=575, ly=165))

    # Зовнішня система 2: Сервіс антифроду (праворуч по центру)
    e2_x, e2_y = 710, 245
    p.append(c4_box(e2_x, e2_y, 170, 85, "Зовнішній антифрод", "External System",
                    "Оцінює скоринг ризику\nшахрайських операцій", fill=EXT_BG, stroke=EXT_BD))
    p.append(c4_edge(cs_x + 110, cs_y, e2_x - 85, e2_y, "Запитує скоринг ризику", "REST / HTTPS", lx=575, ly=230))

    # Зовнішня система 3: Шлюз сповіщень (праворуч знизу)
    e3_x, e3_y = 710, 350
    p.append(c4_box(e3_x, e3_y, 170, 85, "Шлюз сповіщень", "External System",
                    "Доставляє SMS, Email\nта Push-повідомлення", fill=EXT_BG, stroke=EXT_BD))
    p.append(c4_edge(cs_x + 110, cs_y + 30, e3_x - 85, e3_y - 10, "Надсилає квитанції", "gRPC / TLS", lx=575, ly=310))

    # Підпис межі
    p.append(text(W / 2, 445, "Межа системи (System Boundary): усередині — наш продукт, ззовні — клієнти та сторонні партнери.", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "c4-context-diagram.svg"), W, H, *p)


# ── 3. Рівень 2: Containers ─────────────────────────────────────────────────
def fig_container_diagram():
    W, H = 880, 520
    p = []
    p.append(text(W / 2, 26, "Рівень 2 (Containers): Архітектура розподіленої платформи", size=16, bold=True))
    p.append(text(W / 2, 44, "Показує розгортальні процеси (контейнери), протоколи взаємодії та сховища даних", size=11, color=MUTED, italic=True))

    # Зовнішні актори ліворуч
    p.append(c4_person(75, 140, "Покупець", "Клієнт сервісу", w=120, h=65))
    p.append(c4_person(75, 330, "Мерчант", "Кабінет аналітики", w=120, h=65))

    # Межа системи
    bx, by, bw, bh = 160, 65, 545, 425
    p.append(rect(bx, by, bw, bh, fill="#fbfcff", stroke=SYS_BD, sw=1.6, rx=12))
    p.append(text(bx + 16, by + 20, "Платіжна платформа [Software System Boundary]", size=11, color=SYS_BD, bold=True, anchor="start"))

    # Контейнери верхнього рівня (клієнти)
    p.append(c4_box(255, 135, 140, 70, "Web-кабінет", "Container", "SPA інтерфейс", "React / TS", fill=SYS_BG, stroke=SYS_BD))
    p.append(c4_box(435, 135, 140, 70, "Мобільний додаток", "Container", "iOS / Android", "Kotlin / Swift", fill=SYS_BG, stroke=SYS_BD))

    # Середній рівень: Gateway та Payment Service
    p.append(c4_box(345, 255, 150, 75, "API Gateway", "Container", "Auth, rate limit, routing", "Envoy / Go", fill=SYS_BG, stroke=SYS_BD))
    p.append(c4_box(575, 255, 150, 75, "Payment Service", "Container", "Оркестрація транзакцій", "Go / Gin", fill=CMP_BG, stroke=CMP_BD))

    # Нижній рівень: Ledger Service та Kafka
    p.append(c4_box(345, 395, 150, 75, "Ledger Service", "Container", "Бухгалтерський баланс", "C++20", fill=CMP_BG, stroke=CMP_BD))
    p.append(c4_box(575, 395, 150, 75, "Подієва шина", "Container", "Черга подій транзакцій", "Apache Kafka", fill=DB_BG, stroke=DB_BD))

    # Сховище праворуч
    p.append(c4_db(785, 255, 140, 75, "Платіжна БД", "PostgreSQL", "Транзакції та outbox", fill=DB_BG, stroke=DB_BD))
    p.append(c4_box(785, 135, 140, 70, "Банківський шлюз", "External System", "Кліринг карток", fill=EXT_BG, stroke=EXT_BD))

    # Стрілки від людей до клієнтів
    p.append(c4_edge(135, 130, 185, 130, "HTTPS", "", lx=155, ly=120))
    p.append(c4_edge(135, 330, 185, 155, "HTTPS", "", lx=150, ly=240))

    # Стрілки від клієнтів до Gateway
    p.append(c4_edge(285, 170, 315, 218, "REST / JSON", "", lx=275, ly=202))
    p.append(c4_edge(405, 170, 375, 218, "REST / JSON", "", lx=420, ly=202))

    # Стрілки від Gateway до сервісів
    p.append(c4_edge(420, 255, 500, 255, "Створює платіж", "gRPC", lx=460, ly=242))
    p.append(c4_edge(345, 293, 345, 357, "Запитує баланс", "gRPC", lx=390, ly=328))

    # Стрілки від Payment Service до БД, шини, банку
    p.append(c4_edge(650, 255, 715, 255, "Записує", "SQL/TCP", lx=682, ly=242))
    p.append(c4_edge(575, 293, 575, 357, "Публікує подію", "Kafka/TCP", lx=630, ly=328))
    p.append(c4_edge(500, 395, 420, 395, "Споживає події", "Kafka/TCP", lx=460, ly=382))
    p.append(c4_edge(650, 225, 720, 160, "Списання", "ISO 8583", lx=665, ly=180))

    p.append(text(W / 2, 505, "Контейнер у C4 — це окремо виконуваний процес або сховище даних, а не лише Docker-образ.", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "c4-container-diagram.svg"), W, H, *p)


# ── 4. Рівень 3: Components ─────────────────────────────────────────────────
def fig_component_diagram():
    W, H = 880, 540
    p = []
    p.append(text(W / 2, 26, "Рівень 3 (Components): Внутрішня будова Payment Service", size=16, bold=True))
    p.append(text(W / 2, 44, "Декомпозиція контейнера на функціональні компоненти з чистими інтерфейсами", size=11, color=MUTED, italic=True))

    # Зовнішні елементи
    p.append(c4_box(80, 150, 120, 70, "API Gateway", "Container", "Маршрутизує виклик", "Envoy", fill=SYS_BG, stroke=SYS_BD))
    p.append(c4_db(80, 370, 120, 75, "Платіжна БД", "PostgreSQL", "Таблиці outbox і transactions", fill=DB_BG, stroke=DB_BD))

    # Рамка контейнера Payment Service
    bx, by, bw, bh = 170, 60, 520, 440
    p.append(rect(bx, by, bw, bh, fill="#faf5ff", stroke=CMP_BD, sw=1.6, rx=12))
    p.append(text(bx + 16, by + 20, "Payment Service [Container: Go / Gin]", size=11, color=CMP_BD, bold=True, anchor="start"))

    # Компоненти всередині:
    # 1. Payment Controller (вхідна точка)
    p.append(c4_box(290, 130, 160, 75, "Payment Controller", "Component", "Приймає gRPC запити,\nвалідує DTO схеми", "gRPC Handler", fill=CMP_BG, stroke=CMP_BD))

    # 2. Idempotency Guard
    p.append(c4_box(530, 130, 160, 75, "Idempotency Guard", "Component", "Перевіряє ключ повтору,\nблокує дублікати", "Redis Lock / Memory", fill=CMP_BG, stroke=CMP_BD))

    # 3. Payment Orchestrator (Core Domain Service)
    p.append(c4_box(290, 270, 170, 85, "Payment Orchestrator", "Component", "Керує життєвим циклом\nплатежу та сагою станів", "Domain State Machine", fill=PER_BG, stroke=PER_BD))

    # 4. Fraud Detection Client
    p.append(c4_box(530, 270, 160, 75, "Fraud Client Adapter", "Component", "Формує запит оцінки ризику\nдо зовнішнього API", "HTTP Client", fill=CMP_BG, stroke=CMP_BD))

    # 5. Outbox Event Publisher
    p.append(c4_box(290, 410, 160, 75, "Outbox Publisher", "Component", "Атомарно фіксує подію\nв таблицю outbox", "Transactional Outbox", fill=CMP_BG, stroke=CMP_BD))

    # 6. Bank Gateway Adapter
    p.append(c4_box(530, 410, 160, 75, "Bank Gateway Adapter", "Component", "Шифрує та надсилає пакет\nдо банку-еквайра", "ISO 8583 Adapter", fill=CMP_BG, stroke=CMP_BD))

    # Зв'язки між компонентами
    p.append(c4_edge(140, 150, 210, 135, "gRPC виклик", "TLS", lx=175, ly=130))
    p.append(c4_edge(370, 130, 450, 130, "Перевіряє ключ", "Go method", lx=410, ly=115))
    p.append(c4_edge(290, 168, 290, 227, "Передає команду", "In-memory", lx=335, ly=198))
    p.append(c4_edge(375, 270, 450, 270, "Запитує скоринг", "Go interface", lx=410, ly=255))
    p.append(c4_edge(290, 313, 290, 372, "Зберігає подію", "In-memory", lx=335, ly=345))
    p.append(c4_edge(375, 305, 455, 380, "Ініціює списання", "Go interface", lx=425, ly=335))
    
    # Зв'язки назовні
    p.append(c4_edge(210, 410, 140, 390, "Атомарний запис", "SQL/TCP", lx=175, ly=380))

    # Зовнішні сервіси праворуч
    p.append(c4_box(790, 270, 130, 70, "Антифрод API", "External System", "Скоринг ризику", fill=EXT_BG, stroke=EXT_BD))
    p.append(c4_box(790, 410, 130, 70, "Банківський шлюз", "External System", "Кліринг транзакцій", fill=EXT_BG, stroke=EXT_BD))
    p.append(c4_edge(610, 270, 725, 270, "POST /v1/evaluate", "HTTPS", lx=668, ly=255))
    p.append(c4_edge(610, 410, 725, 410, "AuthorizeTx", "ISO 8583", lx=668, ly=395))

    p.append(text(W / 2, 520, "Компоненти — це модулі з чітко окресленими обов'язками всередині кодової бази контейнера.", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "c4-component-diagram.svg"), W, H, *p)


# ── 5. Діаграма розгортання (Deployment) ────────────────────────────────────
def fig_deployment_diagram():
    W, H = 880, 520
    p = []
    p.append(text(W / 2, 26, "Діаграма розгортання: Відображення C4 контейнерів на хмарні вузли", size=16, bold=True))
    p.append(text(W / 2, 44, "Показує, в яких саме інфраструктурних середовищах і вузлах виконуються контейнери", size=11, color=MUTED, italic=True))

    # Вузол AWS Region
    p.append(rect(40, 60, 800, 420, fill="#f8fafc", stroke=NODE_BD, sw=1.8, rx=14))
    p.append(text(55, 82, "Хмарне середовище [Deployment Environment: AWS Production eu-central-1]", size=12, color=NODE_BD, bold=True, anchor="start"))

    # Підвузол 1: CDN / Edge
    p.append(rect(60, 105, 210, 170, fill="#ffffff", stroke="#94a3b8", sw=1.4, rx=10))
    p.append(text(75, 125, "AWS CloudFront CDN", size=10.5, color=MUTED, bold=True, anchor="start"))
    p.append(c4_box(165, 195, 170, 75, "Web SPA Assets", "Container Instance", "Статичні бандли JS/CSS", "AWS S3 + CDN", fill=SYS_BG, stroke=SYS_BD))

    # Підвузол 2: EKS Kubernetes Cluster
    p.append(rect(300, 105, 520, 200, fill="#ffffff", stroke=SYS_BD, sw=1.5, rx=10))
    p.append(text(315, 125, "Kubernetes Cluster [EKS Multi-AZ]", size=11, color=SYS_BD, bold=True, anchor="start"))

    # Поди всередині EKS
    p.append(c4_box(410, 185, 170, 75, "API Gateway Pod", "Container Instance", "3 репліки за Envoy Ingress", "Envoy / HPA", fill=SYS_BG, stroke=SYS_BD))
    p.append(c4_box(630, 185, 180, 75, "Payment Service Pod", "Container Instance", "5 реплік мікросервісу", "Go / Kubernetes Pod", fill=CMP_BG, stroke=CMP_BD))
    p.append(c4_box(630, 270, 180, 60, "Ledger Service Pod", "Container Instance", "2 репліки розрахунків", "C++ / Pod", fill=CMP_BG, stroke=CMP_BD))

    # Підвузол 3: Managed Data Services (AWS RDS & MSK)
    p.append(rect(60, 325, 760, 140, fill="#ffffff", stroke=DB_BD, sw=1.5, rx=10))
    p.append(text(75, 345, "Managed Data & Messaging Tier [VPC Private Subnet]", size=11, color=DB_BD, bold=True, anchor="start"))

    p.append(c4_db(180, 405, 190, 65, "AWS RDS PostgreSQL", "Managed DB", "Multi-AZ Master-Replica", fill=DB_BG, stroke=DB_BD))
    p.append(c4_db(440, 405, 190, 65, "AWS ElastiCache Redis", "Cluster Mode", "3 Master + 3 Replica вузли", fill=DB_BG, stroke=DB_BD))
    p.append(c4_box(700, 405, 190, 65, "AWS Managed Kafka (MSK)", "Kafka Cluster", "3 брокери через 3 AZ", "Apache Kafka 3.x", fill=DB_BG, stroke=DB_BD))

    # Стрілки розгортання
    p.append(c4_edge(495, 185, 540, 185, "gRPC", "ClusterIP", lx=518, ly=173))
    p.append(c4_edge(630, 223, 630, 240, "", "", lx=0, ly=0))
    p.append(c4_edge(580, 223, 275, 372, "TLS Connection", "SQL", lx=420, ly=300))
    p.append(c4_edge(630, 223, 480, 372, "TCP Cache", "RESP", lx=560, ly=310))
    p.append(c4_edge(680, 223, 700, 372, "Events", "Kafka Wire", lx=705, ly=300))

    p.append(text(W / 2, 500, "Deployment diagram у C4 пов'язує логічні контейнери із фізичною топологією хмари чи серверів.", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "c4-deployment-mapping.svg"), W, H, *p)


# ── 6. Динамічна діаграма (Dynamic Diagram) ─────────────────────────────────
def fig_dynamic_saga():
    W, H = 880, 520
    p = []
    p.append(text(W / 2, 26, "Динамічна діаграма: Сценарій обробки транзакції (Payment Saga)", size=16, bold=True))
    p.append(text(W / 2, 44, "Послідовність кроків у часі для конкретного бізнес-сценарію між контейнерами", size=11, color=MUTED, italic=True))

    # Контейнери-учасники сценарію (зверху у стовпчиках)
    nodes = [
        ("Web SPA", 90),
        ("API Gateway", 240),
        ("Payment Service", 400),
        ("PostgreSQL (Outbox)", 570),
        ("Bank Gateway", 720),
        ("Kafka Broker", 820),
    ]

    for title, nx in nodes:
        p.append(rect(nx - 45, 65, 90, 36, fill=SYS_BG if "SPA" in title or "Gateway" in title else (DB_BG if "Postgre" in title or "Kafka" in title else (EXT_BG if "Bank" in title else CMP_BG)), stroke=LINE, sw=1.5, rx=6))
        p.append(text(nx, 88, title, size=10, bold=True))
        # Лінія життя
        p.append(line(nx, 105, nx, 460, color="#cbd5e1", sw=1.5, dash="4,4"))

    steps = [
        (1, 90, 240, 130, "1. POST /v1/payments", "JSON / HTTPS"),
        (2, 240, 400, 175, "2. ProcessPayment()", "gRPC / Protobuf"),
        (3, 400, 570, 220, "3. INSERT Payment(PENDING) & Outbox", "SQL Transaction"),
        (4, 400, 720, 275, "4. AuthorizeTransaction()", "ISO 8583 / TLS"),
        (5, 720, 400, 325, "5. HTTP 200 OK (AUTH_APPROVED)", "ISO Response"),
        (6, 400, 570, 375, "6. UPDATE Payment(SUCCESS)", "SQL Transaction"),
        (7, 570, 820, 420, "7. Publish event: PaymentCompleted", "Kafka CDC / Outbox"),
    ]

    for num, x1, x2, y, label, proto in steps:
        p.append(arrow(x1, y, x2, y, color=SYS_BD if num in (1,2) else (POS if num==4 else (FIELD if num in (5,6,7) else LINE)), sw=2))
        mx = (x1 + x2) / 2
        p.append(rect(mx - 95, y - 16, 190, 26, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
        p.append(text(mx, y - 4, label, size=9.5, color=INK, bold=True))
        p.append(text(mx, y + 8, f"[{proto}]", size=9.5, color=MUTED, italic=True))

    p.append(text(W / 2, 495, "Динамічна діаграма C4 показує нумерований ланцюжок взаємодій для одного сценарію.", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "c4-dynamic-saga.svg"), W, H, *p)


if __name__ == "__main__":
    fig_hierarchy_zoom()
    fig_context_diagram()
    fig_container_diagram()
    fig_component_diagram()
    fig_deployment_diagram()
    fig_dynamic_saga()
    print("All C4 diagrams generated successfully.")
