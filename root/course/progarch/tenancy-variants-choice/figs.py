# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"

def fig_tenancy_models_overview():
    """Візуальне порівняння трьох чистих моделей мультиарендності:
    Pool (спільна БД/схема), Schema-per-Tenant (окремі схеми) та Silo (виділені БД)."""
    W, H = 1040, 480
    f = []

    # Три колонки під моделі
    models = [
        (40,  "1. Pool (Спільна схема)",
         "Спільна БД · Спільна схема",
         [("Таблиця devices", "tenant_id | device_id | name"),
          ("Таблиця telemetry", "tenant_id | timestamp | val")],
         "Найнижчий TCO · Швидкий старт\nВисокий ризик cross-tenant витоку\nШумний сусід у БД",
         BLUE_T, NEG),
        (370, "2. Schema-per-Tenant",
         "Спільна БД · Окремі схеми",
         [("Схема tenant_101", "devices | telemetry"),
          ("Схема tenant_102", "devices | telemetry")],
         "Логічна межа на рівні ДБЖ\nСкладні міграції (10к схем!)\nСпільні ресурси CPU/IOPS",
         AMBER_T, AMBER),
        (700, "3. Silo (Виділена БД)",
         "Окремі бази / Інстанси",
         [("База db_tenant_101", "Повний стек таблиць"),
          ("База db_tenant_102", "Повний стек таблиць")],
         "Максимальна ізоляція й безпека\nНульовий вплив шумного сусіда\nНайвищий TCO · Флот баз",
         GREEN_T, FIELD),
    ]

    for x, title, sub, tables, props, tint, stroke_col in models:
        # Заголовок моделі
        f.append(fitbox(x, 40, 300, 48, title, size=15, bold=True, fill=tint, stroke=stroke_col))
        f.append(text(x + 150, 102, sub, size=12, color=MUTED))

        # БД Контейнер
        f.append(rect(x, 115, 300, 210, fill=BG, stroke=stroke_col, sw=1.8, rx=6))
        
        # Вміст таблиць / схем
        for i, (tname, tdesc) in enumerate(tables):
            ty = 135 + i * 85
            f.append(fitbox(x + 15, ty, 270, 32, tname, size=13, bold=True, fill=NEUT, stroke=INK))
            f.append(fitbox(x + 15, ty + 34, 270, 32, tdesc, size=11, fill=BG, stroke="#c8ced6"))

        # Характеристики нижче
        f.append(fitbox(x, 340, 300, 110, props, size=12, fill=tint, stroke=stroke_col))

    render(os.path.join(OUT, 'tenancy-models-overview.svg'), W, H, *f,
           title="Три основні моделі мультиарендності БД")

def fig_blast_radius_noisy_neighbor():
    """Порівняння радіуса вибуху та впливу шумного сусіда у Pool та Silo моделях."""
    W, H = 1000, 440
    f = []

    # Ліва частина: Pool — один важезний запит валив усьому
    f.append(fitbox(50, 40, 420, 44, "Pool (Спільна схема): Спільний ресурс", size=15, bold=True, fill=RED_T, stroke=POS))
    f.append(rect(50, 100, 420, 240, fill=BG, stroke=POS, sw=1.8, rx=6))

    f.append(fitbox(70, 120, 170, 60, "Орендар A (Heavy)\nDROP INDEX / SELECT *", size=13, bold=True, fill=RED_T, stroke=POS))
    f.append(fitbox(280, 120, 170, 60, "Орендар B (Legit)\nЗвичайний API запит", size=13, fill=NEUT, stroke=INK))

    f.append(arrow(155, 180, 210, 220, color=POS, sw=2))
    f.append(arrow(365, 180, 290, 220, color=MUTED, sw=2))

    f.append(fitbox(150, 220, 220, 70, "Спільний CPU / Pool\n100% CPU Lock!", size=14, bold=True, fill=RED_T, stroke=POS))
    f.append(fitbox(50, 355, 420, 60, "Наслідок: Запит Орендаря B падає по 504 Timeout!\nРадіус вибуху = УСІ орендарі системи", size=12, bold=True, fill=RED_T, stroke=POS))

    # Права частина: Silo — перегородка (Bulkhead) захищає
    f.append(fitbox(530, 40, 420, 44, "Silo (Виділені бази): Ізоляція ресурсів", size=15, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(rect(530, 100, 420, 240, fill=BG, stroke=FIELD, sw=1.8, rx=6))

    f.append(fitbox(550, 120, 170, 60, "Орендар A (Heavy)\nDROP INDEX / SELECT *", size=13, bold=True, fill=RED_T, stroke=POS))
    f.append(fitbox(760, 120, 170, 60, "Орендар B (Legit)\nЗвичайний API запит", size=13, fill=GREEN_T, stroke=FIELD))

    f.append(arrow(635, 180, 635, 220, color=POS, sw=2))
    f.append(arrow(845, 180, 845, 220, color=FIELD, sw=2))

    f.append(fitbox(550, 220, 170, 70, "База DB_A\n100% CPU Lock", size=13, bold=True, fill=RED_T, stroke=POS))
    f.append(fitbox(760, 220, 170, 70, "База DB_B\n0% Впливу (ОК)", size=13, bold=True, fill=GREEN_T, stroke=FIELD))

    f.append(line(735, 110, 735, 320, color=FIELD, sw=2.5, dash="6 4"))
    f.append(text(735, 332, "Захисна перегородка (Bulkhead)", size=11, color=FIELD))

    f.append(fitbox(530, 355, 420, 60, "Наслідок: Орендар B працює ідеально без затримок.\nРадіус вибуху = ЛИШЕ проблемний Орендар A", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    render(os.path.join(OUT, 'blast-radius-noisy-neighbor.svg'), W, H, *f,
           title="Радіус вибуху та шумний сусід: Pool проти Silo")

def fig_tenant_context_flow():
    """Потік виконання запиту з прокиданням контексту орендаря від HTTP до RLS у БД."""
    W, H = 1020, 380
    f = []

    steps = [
        (40,  "1. HTTP Запит", "Header: X-Tenant-ID: t_101\nHost: t101.dh.io", BLUE_T, NEG),
        (280, "2. API Gateway / Auth", "Автентифікація JWT\nПеревірка Tenant Active", NEUT, INK),
        (520, "3. Backend Service", "Context Injection:\nWithTenant(ctx, 't_101')", AMBER_T, AMBER),
        (760, "4. Database (RLS)", "SET LOCAL app.tenant='t_101'\nSELECT * WHERE tenant_id...", GREEN_T, FIELD),
    ]

    for i, (x, title, desc, tint, stroke_col) in enumerate(steps):
        f.append(fitbox(x, 80, 220, 50, title, size=14, bold=True, fill=tint, stroke=stroke_col))
        f.append(fitbox(x, 140, 220, 110, desc, size=12, fill=BG, stroke=stroke_col))

        if i < len(steps) - 1:
            next_x = steps[i+1][0]
            f.append(arrow(x + 220, 195, next_x, 195, sw=2, color=INK))

    # Нижній банер з принципом безпеки
    f.append(fitbox(40, 280, 940, 60,
                    "Правило безпеки: Контекст орендаря витягується з криптографічно підписаного токена,\n"
                    "прокидається в потоці/контексті мови та ПРИМУСОВО встановлюється в сесії БД перед виконанням SQL.",
                    size=13, bold=True, fill=AMBER_T, stroke=AMBER))

    render(os.path.join(OUT, 'tenant-context-flow.svg'), W, H, *f,
           title="Потік прокидання контексту орендаря")

def fig_hybrid_tenancy_tiering():
    """Архітектура гібридної мультиарендності (Tiered Multi-tenancy)."""
    W, H = 1000, 420
    f = []

    # Джерело запитів
    f.append(fitbox(40, 150, 180, 100, "Вхідний потік\nтрафіку\n(API Router)", size=14, bold=True, fill=NEUT, stroke=INK))

    # Маршрутизація за рівнем підписки (Tier Router)
    f.append(arrow(220, 200, 310, 200, sw=2))

    f.append(fitbox(310, 130, 200, 140, "Tier Router\n\nПеревірка Entitlements\nта Плану Орендаря", size=14, bold=True, fill=AMBER_T, stroke=AMBER))

    # Гілка 1: Standard / Freemium (Pool)
    f.append(arrow(510, 170, 640, 110, sw=2, color=NEG))
    f.append(fitbox(640, 60, 320, 100, "Standard / Freemium Tier (90% орендарів)\n\nСпільний кластер БД (Pool)\nМаксимальна щільність · Низький TCO", size=13, bold=True, fill=BLUE_T, stroke=NEG))

    # Гілка 2: Enterprise / B2B (Silo)
    f.append(arrow(510, 230, 640, 290, sw=2, color=FIELD))
    f.append(fitbox(640, 240, 320, 120, "Enterprise / B2B Tier (10% орендарів)\n\nВиділені бази даних (Silo)\nГарантований SLA · Data Residency\nІзольований шумний сусід", size=13, bold=True, fill=GREEN_T, stroke=FIELD))

    render(os.path.join(OUT, 'hybrid-tenancy-tiering.svg'), W, H, *f,
           title="Гібридна модель мультиарендності")

if __name__ == '__main__':
    fig_tenancy_models_overview()
    fig_blast_radius_noisy_neighbor()
    fig_tenant_context_flow()
    fig_hybrid_tenancy_tiering()
    print("Figures successfully generated in", OUT)
