# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

BLUE_T  = "#eaf0fd"
GREEN_T = "#e7f6ec"
AMBER_T = "#fdf0dd"
RED_T   = "#fdecea"
PURP_T  = "#f3e8ff"
NEUT    = "#eef2f6"

AMBER   = "#e08a1e"
GREEN   = "#2e7d32"
BLUE    = "#1565c0"
RED     = "#c62828"
PURPLE  = "#7b1fa2"


def fig_capstone_context_map():
    """Карта бізнес-контексту та системних меж OmniPay Global:
    актори, регіональні суверенні зони та ядро системи."""
    W, H = 1040, 480
    f = []

    # 1. Зовнішні актори (Ліворуч)
    f.append(fitbox(40, 40, 220, 100, "Торговці & B2B Клієнти\n\n• Web Dashboard\n• Mobile SDK\n• Public REST / gRPC API",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(fitbox(40, 190, 220, 100, "Покупці (End-Users)\n\n• Checkout Widgets\n• Mobile Payment UI\n• Webhooks / Push",
                    size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(fitbox(40, 340, 220, 100, "Фінансові еквайєри\n\n• VISA / Mastercard\n• SWIFT / SEPA Rails\n• Local Banking Networks",
                    size=12, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # Стрілки від акторів до меж
    f.append(arrow(260, 90, 340, 90, color=BLUE, sw=2))
    f.append(arrow(260, 240, 340, 240, color=GREEN, sw=2))
    f.append(arrow(260, 390, 340, 390, color=AMBER, sw=2))

    # 2. Периметр системи OmniPay (Центр)
    f.append(fitbox(340, 40, 380, 400, "Периметр платформи OmniPay Global\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n• Regional Ingress & Edge Router\n• Multi-Tenant Auth & Entitlements\n• Transaction Engine & Ledger\n• Outbox Event Broker & Webhooks",
                    size=12, bold=True, fill=NEUT, stroke=INK, color=INK))

    # 3. Суверенні регіональні зони (Праворуч)
    f.append(fitbox(760, 40, 240, 110, "Зона EU (Frankfurt)\n\n• GDPR Compliance\n• Local PII Vault\n• EU Merchant Partition",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))
    f.append(fitbox(760, 180, 240, 110, "Зона US (N. Virginia)\n\n• CCPA & PCI-DSS Level 1\n• Token Vault & Card Data\n• US Merchant Partition",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(fitbox(760, 320, 240, 120, "Зона APAC (Singapore)\n\n• PDPA Data Sovereignty\n• Local Currency Rails\n• APAC Merchant Partition",
                    size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Стрілки від ядра до регіонів
    f.append(arrow(720, 95, 760, 95, color=PURPLE, sw=2))
    f.append(arrow(720, 235, 760, 235, color=BLUE, sw=2))
    f.append(arrow(720, 380, 760, 380, color=GREEN, sw=2))

    render(os.path.join(OUT, 'capstone-context-map.svg'), W, H, *f,
           title="Карта бізнес-контексту та системних меж OmniPay Global")


def fig_capstone_utility_tree():
    """Дерево корисності (Utility Tree) капстону:
    атрибути якості та зважені сценарії (High/Medium risk)."""
    W, H = 1040, 460
    f = []

    # Корінь дерева
    f.append(fitbox(40, 190, 160, 80, "OmniPay\nUtility Tree", size=13, bold=True, fill=NEUT, stroke=INK))

    # Гілки атрибутів
    # 1. Стійкість та Доступність
    f.append(fitbox(260, 40, 220, 60, "Доступність (Availability)\nSLA 99.99% / Zero Downtime", size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(arrow(200, 210, 260, 70, color=BLUE, sw=2))

    # 2. Продуктивність та Затримка
    f.append(fitbox(260, 140, 220, 60, "Продуктивність (Performance)\np99 < 250ms / 10k RPS", size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(arrow(200, 225, 260, 170, color=GREEN, sw=2))

    # 3. Суверенітет Даних та Безпека
    f.append(fitbox(260, 240, 220, 60, "Суверенітет Даних (Security)\nGDPR / PCI-DSS / Zero Leak", size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))
    f.append(arrow(200, 240, 260, 270, color=PURPLE, sw=2))

    # 4. Модифіковуваність та Кошт
    f.append(fitbox(260, 340, 220, 60, "Змінюваність & Кошт (Cost)\nUnit cost <= $0.0025 / Adapters", size=12, fill=AMBER_T, stroke=AMBER, color=AMBER))
    f.append(arrow(200, 255, 260, 370, color=AMBER, sw=2))

    # Листя — Сценарії з пріоритетами (Важливість, Ризик)
    f.append(fitbox(540, 35, 460, 70, "Сценарій 1: Падіння цілого хмарного регіону -> Автоперемикання за < 30с без втрати транзакцій (RPO=0) [H, H]", size=11, fill=RED_T, stroke=RED, color=RED))
    f.append(arrow(480, 70, 540, 70, color=BLUE, sw=1.5))

    f.append(fitbox(540, 135, 460, 70, "Сценарій 2: Піковий сплеск 50,000 RPS під час Чорної П'ятниці -> Адаптивний сhedding без метастабільності [H, H]", size=11, fill=RED_T, stroke=RED, color=RED))
    f.append(arrow(480, 170, 540, 170, color=GREEN, sw=1.5))

    f.append(fitbox(540, 235, 460, 70, "Сценарій 3: Крос-регіональний запит -> PII не залишає зону EU/US, токенізація на кордоні [H, M]", size=11, fill=PURP_T, stroke=PURPLE, color=PURPLE))
    f.append(arrow(480, 270, 540, 270, color=PURPLE, sw=1.5))

    f.append(fitbox(540, 335, 460, 70, "Сценарій 4: Підключення нового шлюзу еквайрингу за <= 3 дні без рефакторингу грошового ядра [M, M]", size=11, fill=AMBER_T, stroke=AMBER, color=AMBER))
    f.append(arrow(480, 370, 540, 370, color=AMBER, sw=1.5))

    render(os.path.join(OUT, 'capstone-utility-tree.svg'), W, H, *f,
           title="Дерево корисності (Utility Tree) капстону")


def fig_capstone_walking_skeleton():
    """Схема Walking Skeleton: найтонший наскрізний ланцюжок запиту."""
    W, H = 1040, 420
    f = []

    steps = [
        ("1. Client Call", "Mule/Web SDK\n`POST /v1/checkout`", BLUE_T, BLUE, 40),
        ("2. Edge Router", "Auth + Tenant Context\nIdempotency Key Check", GREEN_T, GREEN, 240),
        ("3. Ingest Engine", "Append Transaction Intent\nOutbox Event Write", AMBER_T, AMBER, 440),
        ("4. Ledger Sync", "Regional State Lock\nMulti-Region Reconciler", PURP_T, PURPLE, 640),
        ("5. Notification", "Async Webhook Push\nMerchant ACK (200 OK)", NEUT, INK, 840),
    ]

    for title, desc, bg, stroke, x in steps:
        f.append(fitbox(x, 40, 160, 50, title, size=12, bold=True, fill=bg, stroke=stroke, color=stroke))
        f.append(fitbox(x, 100, 160, 180, desc, size=11, fill=NEUT, stroke=stroke))

    # З'єднувальні стрілки
    f.append(arrow(200, 65, 240, 65, color=BLUE, sw=2))
    f.append(arrow(400, 65, 440, 65, color=GREEN, sw=2))
    f.append(arrow(600, 65, 640, 65, color=AMBER, sw=2))
    f.append(arrow(800, 65, 840, 65, color=PURPLE, sw=2))

    # Нижній інваріант Walking Skeleton
    f.append(fitbox(40, 310, 960, 80, "Наскрізна трасована перевірка (Walking Skeleton):\n"
                                        "• Запит проходить УСІ шари системи від edge-маршрутизатора до асинхронного вебхука.\n"
                                        "• Знімається інтеграційний ризик, фіксується Correlation ID та перевіряються крос-регіональні затримки.",
                    size=12, fill=BG, stroke=INK, color=INK))

    render(os.path.join(OUT, 'capstone-walking-skeleton.svg'), W, H, *f,
           title="Схема Walking Skeleton для капстону")


if __name__ == '__main__':
    fig_capstone_context_map()
    fig_capstone_utility_tree()
    fig_capstone_walking_skeleton()
    print("Capstone figures generated successfully!")
