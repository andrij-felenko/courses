# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми «Аналіз ерозії архітектури: граф залежностей».
Використовує спільну бібліотеку svgkit зі scripts/.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_architecture_drift_spectrum():
    """Ілюстрація спектра ерозії: запланована чиста архітектура проти фактичної еродованої."""
    w, h = 900, 430
    frags = []

    # Заголовки двох колонок
    b1, _, _ = textbox(215, 30, "Запланована архітектура (DAG)", size=14, bold=True, fill="#eaf7ed", stroke=FIELD)
    b2, _, _ = textbox(660, 30, "Фактична еродована архітектура", size=14, bold=True, fill="#fdecea", stroke=POS)
    frags.extend([b1, b2])

    # Розділювач колонок
    frags.append(line(440, 15, 440, 410, color=MUTED, sw=1.2, dash="4,4"))

    # ЛІВА КОЛОНКА: Чистий DAG
    l1, _, _ = textbox(215, 80, "Presentation (UI / API Gateway)", size=12, fill="#f0f4f8", stroke=NEG, bold=True, min_w=260)
    l2, _, _ = textbox(215, 160, "Application Services", size=12, fill="#f0f4f8", stroke=NEG, min_w=260)
    l3, _, _ = textbox(215, 240, "Domain Core (Сутності та правила)", size=12, fill="#f0f4f8", stroke=FIELD, bold=True, min_w=260)
    l4, _, _ = textbox(215, 320, "Infrastructure (БД / Мережа / Черги)", size=12, fill="#f0f4f8", stroke=MUTED, min_w=260)
    frags.extend([l1, l2, l3, l4])

    # Чисті стрілки вниз
    frags.append(arrow(215, 100, 215, 140, color=FIELD, sw=2))
    frags.append(arrow(215, 180, 215, 220, color=FIELD, sw=2))
    frags.append(arrow(215, 260, 215, 300, color=FIELD, sw=2))

    t_clean, _, _ = textbox(215, 385, "Ієрархія без циклів · Односпрямований потік", size=11, fill="#ffffff", stroke=FIELD, color=FIELD, bold=True)
    frags.append(t_clean)

    # ПРАВА КОЛОНКА: Еродована архітектура
    r1, _, _ = textbox(660, 80, "Presentation (UI / API Gateway)", size=12, fill="#fdecea", stroke=POS, bold=True, min_w=250)
    r2, _, _ = textbox(660, 160, "Application Services", size=12, fill="#fdecea", stroke=POS, min_w=250)
    r3, _, _ = textbox(660, 240, "Domain Core", size=12, fill="#fdecea", stroke=POS, bold=True, min_w=250)
    r4, _, _ = textbox(660, 320, "Infrastructure (БД / Драйвери)", size=12, fill="#fdecea", stroke=POS, min_w=250)
    frags.extend([r1, r2, r3, r4])

    # Штатна стрілка вниз
    frags.append(arrow(660, 100, 660, 140, color=MUTED, sw=1.5))
    frags.append(arrow(660, 180, 660, 220, color=MUTED, sw=1.5))

    # Порушення 1: Простріл шару Presentation -> Infrastructure в обхід Domain (обводимо справа)
    frags.append(line(790, 80, 865, 80, color=POS, sw=1.8, dash="3,3"))
    frags.append(line(865, 80, 865, 320, color=POS, sw=1.8, dash="3,3"))
    frags.append(arrow(865, 320, 790, 320, color=POS, sw=1.8))
    tag_skip, _, _ = textbox(810, 200, "Простріл шару\n(Layer Bypass)", size=10, fill="#ffffff", stroke=POS, color=POS, bold=True)
    frags.append(tag_skip)

    # Порушення 2: Зворотна залежність Domain -> Infrastructure (порушення DIP)
    frags.append(arrow(640, 260, 640, 300, color=POS, sw=2))

    # Порушення 3: Циклічна залежність Domain -> Application (Back-edge, обводимо зліва)
    frags.append(line(530, 240, 465, 240, color=POS, sw=1.8, dash="3,3"))
    frags.append(line(465, 240, 465, 160, color=POS, sw=1.8, dash="3,3"))
    frags.append(arrow(465, 160, 530, 160, color=POS, sw=1.8))
    tag_cycle, _, _ = textbox(500, 200, "Зворотний цикл\n(Back-edge)", size=10, fill="#ffffff", stroke=POS, color=POS, bold=True)
    frags.append(tag_cycle)

    t_eroded, _, _ = textbox(660, 385, "Цикли · Несанкціоноване зчеплення · Розрив меж", size=11, fill="#ffffff", stroke=POS, color=POS, bold=True)
    frags.append(t_eroded)

    render(os.path.join(IMG_DIR, "architecture-drift-spectrum.svg"), w, h, *frags)


def fig_layered_violations_matrix():
    """Матриця та схема трьох типів архітектурних порушень у шаровій системі."""
    w, h = 920, 440
    frags = []

    # Чотири шари горизонтально з ширшими проміжками
    # Layer 3: Presentation
    l3 = rect(25, 45, 185, 250, fill="#f8fafc", stroke=NEG, sw=1.8)
    t3 = text(117, 70, "Presentation Layer", size=12, color=NEG, bold=True)
    m3_1, _, _ = textbox(117, 110, "HTTP REST API", size=11, fill="#ffffff", min_w=145)
    m3_2, _, _ = textbox(117, 165, "gRPC Gateways", size=11, fill="#ffffff", min_w=145)
    m3_3, _, _ = textbox(117, 220, "CLI Controllers", size=11, fill="#ffffff", min_w=145)
    frags.extend([l3, t3, m3_1, m3_2, m3_3])

    # Layer 2: Application
    l2 = rect(235, 45, 185, 250, fill="#f8fafc", stroke=INK, sw=1.5)
    t2 = text(327, 70, "Application Layer", size=12, color=INK, bold=True)
    m2_1, _, _ = textbox(327, 110, "OrderService", size=11, fill="#ffffff", min_w=145)
    m2_2, _, _ = textbox(327, 165, "PaymentWorkflow", size=11, fill="#ffffff", min_w=145)
    m2_3, _, _ = textbox(327, 220, "EventHandlers", size=11, fill="#ffffff", min_w=145)
    frags.extend([l2, t2, m2_1, m2_2, m2_3])

    # Layer 1: Domain
    l1 = rect(500, 45, 185, 250, fill="#eaf7ed", stroke=FIELD, sw=2)
    t1 = text(592, 70, "Domain Core (Чистий)", size=12, color=FIELD, bold=True)
    m1_1, _, _ = textbox(592, 110, "Order Entity", size=11, fill="#ffffff", stroke=FIELD, min_w=145)
    m1_2, _, _ = textbox(592, 165, "PriceCalculator", size=11, fill="#ffffff", stroke=FIELD, min_w=145)
    m1_3, _, _ = textbox(592, 220, "BillingPolicy", size=11, fill="#ffffff", stroke=FIELD, min_w=145)
    frags.extend([l1, t1, m1_1, m1_2, m1_3])

    # Layer 0: Infrastructure
    l0 = rect(710, 45, 185, 250, fill="#f8fafc", stroke=MUTED, sw=1.5)
    t0 = text(802, 70, "Infrastructure", size=12, color=MUTED, bold=True)
    m0_1, _, _ = textbox(802, 110, "PostgresRepo", size=11, fill="#ffffff", min_w=145)
    m0_2, _, _ = textbox(802, 165, "KafkaProducer", size=11, fill="#ffffff", min_w=145)
    m0_3, _, _ = textbox(802, 220, "RedisCache", size=11, fill="#ffffff", min_w=145)
    frags.extend([l0, t0, m0_1, m0_2, m0_3])

    # Дозволені стрілки (зелені)
    frags.append(arrow(190, 110, 255, 110, color=FIELD, sw=2))  # Presentation -> Application
    frags.append(arrow(400, 110, 520, 110, color=FIELD, sw=2))  # Application -> Domain
    frags.append(arrow(400, 220, 730, 220, color=FIELD, sw=1.8))  # Application -> Infrastructure

    # Порушення 1: Простріл шару (Presentation -> PostgresRepo прямо, під усіма блоками)
    frags.append(line(117, 245, 117, 340, color=POS, sw=2, dash="3,3"))
    frags.append(line(117, 340, 802, 340, color=POS, sw=2, dash="3,3"))
    frags.append(arrow(802, 340, 802, 245, color=POS, sw=2))
    tag1, _, _ = textbox(460, 365, "Порушення 1: Простріл шару (Layer Bypass) — Presentation прямо в PostgresRepo", size=10, fill="#ffffff", stroke=POS, color=POS, bold=True)
    frags.append(tag1)

    # Порушення 2: Пряме зчеплення (Domain -> PostgresRepo прямо)
    frags.append(arrow(665, 110, 730, 110, color=POS, sw=2))
    frags.append(text(697, 95, "Порушення 2: DIP", size=9, color=POS, bold=True))

    # Порушення 3: Зворотний виклик (Domain -> OrderService цикл у проміжку між l2 та l1)
    frags.append(line(592, 140, 592, 160, color=POS, sw=1.8, dash="3,3"))
    frags.append(line(592, 160, 327, 160, color=POS, sw=1.8, dash="3,3"))
    frags.append(arrow(327, 160, 327, 135, color=POS, sw=1.8))
    frags.append(text(460, 152, "Порушення 3: Цикл (Back-edge)", size=9, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "layered-violations-matrix.svg"), w, h, *frags)


def fig_tarjan_scc_cycles():
    """Ілюстрація роботи алгоритму Тар'яна: виявлення сильно зв'язаних компонентів та конденсація графа."""
    w, h = 920, 380
    frags = []

    # Ліва частина: заголовок
    frags.append(text(270, 25, "Вихідний граф сервісів (з циклами)", size=13, bold=True))

    # Вузли
    # S1 (вхідний)
    s1, _, _ = textbox(60, 110, "Gateway\n[dfn=1, low=1]", size=10, fill="#eaf0fd", stroke=NEG, bold=True)

    # SCC 1: S2, S3, S4 (Order, Inventory, Billing)
    frags.append(rect(125, 55, 360, 160, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    frags.append(text(305, 75, "Компонента SCC #1 (Цикл 3 вузлів)", size=10, color=POS, bold=True))
    s2, _, _ = textbox(195, 135, "OrderService\n[dfn=2, low=2]", size=10, fill="#ffffff", stroke=POS)
    s3, _, _ = textbox(315, 115, "Inventory\n[dfn=3, low=2]", size=10, fill="#ffffff", stroke=POS)
    s4, _, _ = textbox(420, 160, "Billing\n[dfn=4, low=2]", size=10, fill="#ffffff", stroke=POS)

    # SCC 2: S5, S6 (Notify, Email)
    frags.append(rect(125, 235, 320, 110, fill="#fef7e0", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(285, 255, "Компонента SCC #2 (Цикл 2 вузлів)", size=10, color="#d97706", bold=True))
    s5, _, _ = textbox(200, 295, "Notify [dfn=5, low=5]", size=10, fill="#ffffff", stroke="#d97706")
    s6, _, _ = textbox(360, 295, "Email [dfn=6, low=5]", size=10, fill="#ffffff", stroke="#d97706")

    frags.extend([s1, s2, s3, s4, s5, s6])

    # Ребра графа
    frags.append(arrow(105, 110, 145, 135, color=INK, sw=1.8))  # S1 -> S2

    # Цикл SCC 1: S2 -> S3 -> S4 -> S2
    frags.append(arrow(245, 125, 275, 120, color=POS, sw=2))  # S2 -> S3
    frags.append(arrow(355, 130, 385, 145, color=POS, sw=2))  # S3 -> S4
    frags.append(line(420, 185, 420, 195, color=POS, sw=2))  # S4 back to S2
    frags.append(line(420, 195, 195, 195, color=POS, sw=2))
    frags.append(arrow(195, 195, 195, 160, color=POS, sw=2))

    # Міжкомпонентне ребро: S2 -> S5
    frags.append(arrow(195, 160, 195, 270, color=INK, sw=1.8))

    # Цикл SCC 2: S5 <-> S6
    frags.append(arrow(260, 285, 305, 285, color="#d97706", sw=1.8))
    frags.append(arrow(305, 305, 260, 305, color="#d97706", sw=1.8))

    # Стрілка переходу від графа до конденсації
    frags.append(arrow(505, 180, 565, 180, color=FIELD, sw=3))
    tag_tarjan, _, _ = textbox(535, 145, "Тар'ян O(V+E)\nКонденсація", size=10, fill="#eaf7ed", stroke=FIELD, color=FIELD, bold=True)
    frags.append(tag_tarjan)

    # Права частина: Сконденсований DAG мета-вузлів
    frags.append(rect(585, 30, 310, 320, fill="#f8fafc", stroke=FIELD, sw=1.5))
    frags.append(text(740, 55, "Ациклічний мета-DAG (Condensation)", size=12, color=FIELD, bold=True))

    m_c1, _, _ = textbox(740, 105, "Вузол {Gateway}", size=11, fill="#eaf0fd", stroke=NEG, bold=True, min_w=180)
    m_c2, _, _ = textbox(740, 185, "Мета-вузол {Order, Inv, Bill}\n[Розмір SCC = 3]", size=11, fill="#fdecea", stroke=POS, bold=True, min_w=220)
    m_c3, _, _ = textbox(740, 275, "Мета-вузол {Notify, Email}\n[Розмір SCC = 2]", size=11, fill="#fef7e0", stroke="#d97706", bold=True, min_w=220)
    frags.extend([m_c1, m_c2, m_c3])

    frags.append(arrow(740, 125, 740, 160, color=INK, sw=2))
    frags.append(arrow(740, 215, 740, 250, color=INK, sw=2))

    render(os.path.join(IMG_DIR, "tarjan-scc-cycles.svg"), w, h, *frags)


def fig_main_sequence_balance():
    """Метрична площина Роберта Мартіна: Абстрактність A проти Нестабільності I."""
    w, h = 780, 440
    frags = []

    # Рамка графіка
    ox, oy = 100, 350
    gw, gh = 520, 280

    # Осі
    frags.append(line(ox, oy, ox + gw + 40, oy, color=INK, sw=2))  # X
    frags.append(line(ox, oy, ox, oy - gh - 30, color=INK, sw=2))  # Y

    # Підписи осей
    frags.append(text(ox + gw + 45, oy + 5, "I (Нестабільність)", size=12, anchor="start", bold=True))
    frags.append(text(ox - 10, oy - gh - 35, "A (Абстрактність)", size=12, anchor="end", bold=True))

    # Розмітки 0 і 1
    frags.append(text(ox, oy + 20, "0.0", size=11, color=MUTED))
    frags.append(text(ox + gw, oy + 20, "1.0", size=11, color=MUTED))
    frags.append(text(ox - 15, oy, "0.0", size=11, color=MUTED))
    frags.append(text(ox - 15, oy - gh, "1.0", size=11, color=MUTED))

    # Зона болю (Zone of Pain): низька A, низька I (лівий нижній кут)
    zp = rect(ox + 1, oy - 90, 90, 89, fill="#fdecea", stroke=POS, sw=1.2, rx=4)
    zp_t = mtext(ox + 45, oy - 55, ["Зона болю", "(Zone of Pain)", "Жорсткість"], size=9, color=POS, bold=True)
    frags.extend([zp, zp_t])

    # Зона марності (Zone of Uselessness): висока A, висока I (правий верхній кут)
    zu = rect(ox + gw - 90, oy - gh, 89, 90, fill="#fef7e0", stroke="#d97706", sw=1.2, rx=4)
    zu_t = mtext(ox + gw - 45, oy - gh + 35, ["Зона марності", "(Uselessness)", "Зайва абстракція"], size=9, color="#d97706", bold=True)
    frags.extend([zu, zu_t])

    # Головна послідовність (Main Sequence line): A + I = 1
    frags.append(line(ox, oy - gh, ox + gw, oy, color=FIELD, sw=3))
    t_ms, _, _ = textbox(ox + gw / 2 + 30, oy - gh / 2 - 30, "Головна послідовність (A + I = 1)", size=11, fill="#eaf7ed", stroke=FIELD, color=FIELD, bold=True)
    frags.append(t_ms)

    # Приклади модулів на площині
    # 1. Збалансований доменний модуль
    frags.append(circle(ox + 140, oy - gh + 140, 7, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(ox + 155, oy - gh + 145, "Domain Core (A=0.6, I=0.3, D=0.1)", size=10, anchor="start", bold=True))

    # 2. Модуль у зоні болю (еродований монолітний сервіс)
    frags.append(circle(ox + 45, oy - 25, 7, fill=POS, stroke=INK, sw=1.5))
    frags.append(text(ox + 60, oy - 20, "Legacy GodService (A=0.05, I=0.08, D=0.87)", size=10, anchor="start", color=POS, bold=True))

    # 3. Марна абстракція
    frags.append(circle(ox + gw - 45, oy - gh + 30, 7, fill="#d97706", stroke=INK, sw=1.5))
    frags.append(text(ox + gw - 170, oy - gh + 15, "Unused Interfaces (A=0.9, I=0.85, D=0.75)", size=10, anchor="end", color="#d97706", bold=True))

    # Відстань D стрілкою
    frags.append(line(ox + 45, oy - 25, ox + 155, oy - 135, color=POS, sw=1.5, dash="3,3"))
    frags.append(text(ox + 120, oy - 70, "Відхилення D = |A+I-1|", size=10, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "main-sequence-balance.svg"), w, h, *frags)


def fig_ci_ratchet_pipeline():
    """Конвеєр CI/CD з механізмом архітектурного храповика (Baseline Ratchet)."""
    w, h = 900, 360
    frags = []

    # Крок 1: Git PR / Комбіт
    s1, _, _ = textbox(110, 100, "Git Pull Request\n(Зміна коду / імпортів)", size=11, fill="#f0f4f8", stroke=NEG, bold=True, min_w=170)
    # Крок 2: Екстрактор графа залежностей
    s2, _, _ = textbox(320, 100, "Екстрактор графа\n(Парсер AST / Protobuf)", size=11, fill="#f0f4f8", stroke=NEG, bold=True, min_w=170)
    # Крок 3: Графовий валідатор правил
    s3, _, _ = textbox(550, 100, "Dependency Checker\n(Перевірка правил & SCC)", size=11, fill="#f0f4f8", stroke=FIELD, bold=True, min_w=190)
    # Крок 4: Храповик базового рівня
    s4, _, _ = textbox(770, 100, "Архітектурний\nхраповик (Baseline)", size=11, fill="#fef7e0", stroke="#d97706", bold=True, min_w=160)

    frags.extend([s1, s2, s3, s4])

    frags.append(arrow(195, 100, 235, 100, color=INK, sw=2))
    frags.append(arrow(405, 100, 455, 100, color=INK, sw=2))
    frags.append(arrow(645, 100, 690, 100, color=INK, sw=2))

    # Розгалуження рішення храповика
    # Гілка 1: Нові порушення > 0 -> FAIL PR
    frags.append(line(770, 140, 770, 230, color=POS, sw=2))
    frags.append(arrow(770, 230, 610, 230, color=POS, sw=2))
    fail_box, _, _ = textbox(480, 230, "БЛОКУВАННЯ PR (Fail Build)\nВиявлено нові ерозійні ребра", size=11, fill="#fdecea", stroke=POS, color=POS, bold=True, min_w=240)
    frags.append(fail_box)

    # Гілка 2: Нових порушень немає -> PASS & Оновлення Baseline
    frags.append(line(770, 60, 770, 30, color=FIELD, sw=2))
    frags.append(line(770, 30, 320, 30, color=FIELD, sw=2))
    frags.append(arrow(320, 30, 320, 60, color=FIELD, sw=2))
    pass_box, _, _ = textbox(545, 30, "ПРОЙДЕНО (Pass): борг зменшився -> оновити baseline.json", size=10, fill="#eaf7ed", stroke=FIELD, color=FIELD, bold=True, min_w=320)
    frags.append(pass_box)

    # Підсумок під схемою
    t_summary, _, _ = textbox(450, 310, "Принцип храповика: архітектурний борг може лише зменшуватися, поява будь-якого нового порушення ламає збірку", size=11, fill="#f8fafc", stroke=MUTED, color=INK)
    frags.append(t_summary)

    render(os.path.join(IMG_DIR, "ci-ratchet-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_architecture_drift_spectrum()
    fig_layered_violations_matrix()
    fig_tarjan_scc_cycles()
    fig_main_sequence_balance()
    fig_ci_ratchet_pipeline()
    print("Усі фігури згенеровано успішно.")
