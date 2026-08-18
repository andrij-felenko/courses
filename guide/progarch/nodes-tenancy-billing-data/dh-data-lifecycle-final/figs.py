# -*- coding: utf-8 -*-
"""Фігури до кроку «Архітектура оренди та життєвого циклу даних DH»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

RED_FILL = "#fdecea"
GREEN_FILL = "#eafaf0"
BLUE_FILL = "#e6eefb"
AMBER_FILL = "#fff4e0"
AMBER = "#c77800"
GRAY_FILL = "#f0f0f2"


def fig_tenancy_pipeline():
    """Наскрізний контекст орендаря: від API Gateway до БД, Kafka та пошуку."""
    W, H = 1200, 560
    frags = []

    # Заголовок / колонки
    frags.append(text(140, 45, "ВХІДНИЙ ЗАПИТ", size=13.5, bold=True, color=MUTED))
    frags.append(text(460, 45, "НАСКРІЗНИЙ КОНТЕКСТ", size=13.5, bold=True, color=INK))
    frags.append(text(920, 45, "ІЗОЛЯЦІЯ В РЕСУРСАХ", size=13.5, bold=True, color=MUTED))

    # Клієнтський запит
    req_b, req_w, req_h = textbox(140, 160, "HTTP / gRPC Запит\nHeader: X-Tenant-ID: tnt_84f9\nBearer Token (JWT)",
                                  size=12.5, bold=True, fill=BLUE_FILL, stroke=NEG, sw=2, color=INK, min_w=200)
    frags.append(req_b)

    # Gateway / Auth PDP
    gw_b, gw_w, gw_h = textbox(460, 160, "API Gateway / Auth PDP\n1. Перевірка підпису JWT\n2. Витяг tenant_id & roles\n3. Формування TenantContext",
                               size=12.5, bold=True, fill=AMBER_FILL, stroke=AMBER, sw=2, color=INK, min_w=280)
    frags.append(gw_b)
    frags.append(arrow(140 + req_w / 2 + 6, 160, 460 - gw_w / 2 - 6, 160, color=INK, sw=2))

    # Ресурси праворуч (БД, Kafka, Пошук, Кеш квот)
    res_nodes = [
        ("PostgreSQL (RLS)\nSET LOCAL app.current_tenant = 'tnt_84f9';\nWHERE tenant_id = current_tenant", 110, GREEN_FILL, FIELD),
        ("Kafka Telemetry Ingest\nPartition Key = tenant_id\n(Чесний bulkhead по партиціях)", 230, BLUE_FILL, NEG),
        ("OpenSearch / Elasticsearch\nFilter: { term: { tenant_id: 'tnt_84f9' } }\nІзольований пошуковий індекс", 350, AMBER_FILL, AMBER),
        ("Redis Entitlements Cache\nKey: tenant:tnt_84f9:quota:video_stream\nМиттєвий перевіряч прав", 470, GRAY_FILL, MUTED)
    ]

    gw_right_x = 460 + gw_w / 2
    for title, y_pos, fill, col in res_nodes:
        rb, rw, rh = textbox(920, y_pos, title, size=11.5, bold=True, fill=fill, stroke=col, sw=1.8, color=INK, min_w=340)
        frags.append(arrow(gw_right_x + 6, 160, 920 - rw / 2 - 6, y_pos, color=MUTED, sw=1.6))
        frags.append(rb)

    # Нижнє пояснення
    frags.append(rect(60, 500, W - 120, 44, fill="#f7f9fb", stroke=MUTED, sw=1.5, rx=6))
    frags.append(text(W / 2, 526, "Гарантія безпеки: жоден запит до БД чи Kafka не виконується без явно прокинутого TenantContext",
                      size=12, bold=True, color=INK))

    render(os.path.join(IMG, "tenancy-pipeline.svg"), W, H, *frags,
           title="Наскрізна прокидка контексту орендаря у DH")


def fig_data_lifecycle_tiers():
    """Яруси даних телеметрії: від гарячого ingest до архіву S3, надгробків та GDPR purge."""
    W, H = 1200, 520
    frags = []

    # 4 етапи життєвого циклу
    stages = [
        ("1. ГАРЯЧИЙ ЯРУС", "0–7 днів", "Kafka / TimescaleDB / Redis\n100% сирих вимірів (1 с)\nВисока частота читання", BLUE_FILL, NEG, 160),
        ("2. ТЕПЛИЙ ЯРУС", "7–90 днів", "PostgreSQL / ClickHouse\nГодинні та денні агругати\nГрафіки та аналітика", GREEN_FILL, FIELD, 440),
        ("3. ХОЛОДНИЙ ЯРУС", "90 днів – 3 роки", "S3 Parquet / Glacier\nСтиснуті батчі (ZSTD)\nCrypto-shredding ключем", AMBER_FILL, AMBER, 740),
        ("4. НАДГРОБОК І PURGE", "Після видалення", "Soft delete -> Tombstone (30 дн)\nХард-пурж S3 об'єктів\nКриптографічне затирання", RED_FILL, "#c0392b", 1040),
    ]

    sb_list = []
    for head, sub, body, fill, col, x_pos in stages:
        frags.append(text(x_pos, 55, head, size=13, bold=True, color=col))
        frags.append(text(x_pos, 75, sub, size=11.5, bold=True, color=MUTED))
        sb, sw, sh = textbox(x_pos, 220, body, size=12, bold=True, fill=fill, stroke=col, sw=2, color=INK, min_w=220)
        sb_list.append((x_pos, sw, sh))
        frags.append(sb)

    # Стрілки між ярусами
    for i in range(len(sb_list) - 1):
        x1 = sb_list[i][0] + sb_list[i][1] / 2
        x2 = sb_list[i+1][0] - sb_list[i+1][1] / 2
        frags.append(arrow(x1 + 4, 220, x2 - 4, 220, color=INK, sw=2.2))

    # Нижня лінійка стиснення та ціни
    frags.append(rect(60, 390, W - 120, 95, fill="#f8f9fa", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(W / 2, 420, "ТРАНСФОРМАЦІЯ ОБСЯГУ ТА ВАРТОСТІ ЗБЕРІГАННЯ", size=13, bold=True, color=INK))
    
    frags.append(text(160, 460, "100% обсягу ($$$)", size=12, bold=True, color=NEG))
    frags.append(text(440, 460, "5% обсягу ($$)", size=12, bold=True, color=FIELD))
    frags.append(text(740, 460, "0.5% обсягу ($)", size=12, bold=True, color=AMBER))
    frags.append(text(1040, 460, "0% обсягу (Purged)", size=12, bold=True, color="#c0392b"))

    render(os.path.join(IMG, "data-lifecycle-tiers.svg"), W, H, *frags,
           title="Яруси даних телеметрії та їх утилізація")


def fig_decommissioning_cascade():
    """Каскад ліквідації орендаря: від відклику прав до затирання ключів і пуржу."""
    W, H = 1200, 580
    frags = []

    frags.append(text(W / 2, 40, "КАСКАД ЛІКВІДАЦІЇ ОРЕНДАРЯ (TENANT DECOMMISSIONING CASCADE)", size=14, bold=True, color=INK))

    steps = [
        ("Крок 1: Revoke Entitlements", "API Gateway миттєво блокує вхідний трафік орендаря", AMBER_FILL, AMBER, 110),
        ("Крок 2: Final Ledger & Invoice", "Фінальне згортання спожитку та виставлення рахунку в Stripe", BLUE_FILL, NEG, 190),
        ("Крок 3: Tombstone Tagging", "Позначення deleted_at у OLTP БД для всіх об'єктів дому", GRAY_FILL, MUTED, 270),
        ("Крок 4: Crypto-Shredding", "Знищення KMS-ключа орендаря: зашифровані S3-архіви стають сміттям", RED_FILL, "#c0392b", 350),
        ("Крок 5: Async Purge GC", "Фоновий фонограма-робітник видаляє бакети S3 та партиції TSDB", RED_FILL, "#c0392b", 430),
        ("Крок 6: Immutable Audit Record", "Запис події ліквідації в незмінний аудит-лог (без PII)", GREEN_FILL, FIELD, 510),
    ]

    for title, desc, fill, col, y in steps:
        sb, sw, sh = textbox(280, y, title, size=12.5, bold=True, fill=fill, stroke=col, sw=2, color=col, min_w=280)
        frags.append(sb)
        db, dw, dh = textbox(780, y, desc, size=12, bold=False, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK, min_w=580)
        frags.append(db)
        frags.append(arrow(280 + sw / 2 + 6, y, 780 - dw / 2 - 6, y, color=col, sw=1.8))

    render(os.path.join(IMG, "decommissioning-cascade.svg"), W, H, *frags,
           title="Послідовність каскадного видалення орендаря")


if __name__ == "__main__":
    fig_tenancy_pipeline()
    fig_data_lifecycle_tiers()
    fig_decommissioning_cascade()
    print("Figures generated successfully.")
