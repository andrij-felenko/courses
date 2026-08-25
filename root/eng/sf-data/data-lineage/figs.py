# -*- coding: utf-8 -*-
"""Генератор фігур для теми Data Lineage."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_granularity_spectrum():
    """Фігура 1: Рівні гранулярності Data Lineage від системного до рядкового."""
    w, h = 900, 440
    frags = []

    levels = [
        ("1. Системний", "Сервіси, черги, сховища", "#eef2f7", "#3b82f6"),
        ("2. Табличний", "Джерела, таблиці, вітрини", "#ecfdf5", "#10b981"),
        ("3. Стовпчиковий", "Формули, проекції, вирази", "#fffbeb", "#f59e0b"),
        ("4. Рядковий", "Конкретні рядки (Provenance)", "#fef2f2", "#ef4444"),
    ]

    card_w = 195
    card_h = 300
    y_top = 65

    for i, (title_lvl, subtitle, bg_col, border_col) in enumerate(levels):
        x_left = 30 + i * 215
        frags.append(rect(x_left, y_top, card_w, card_h, fill=bg_col, stroke=border_col, sw=2, rx=8))
        frags.append(textbox(x_left + card_w / 2, y_top + 30, title_lvl, size=12, bold=True, color=INK, fill=BG, stroke=border_col)[0])
        frags.append(text(x_left + card_w / 2, y_top + 65, subtitle, size=10, color=MUTED, anchor="middle"))

        if i == 0:
            b1 = textbox(x_left + card_w / 2, y_top + 110, "Сервіс оплат\n(Billing API)", size=10, fill=BG, stroke=LINE)[0]
            b2 = textbox(x_left + card_w / 2, y_top + 180, "Топік Kafka\norders.events", size=10, fill=BG, stroke=LINE)[0]
            b3 = textbox(x_left + card_w / 2, y_top + 250, "DWH Сховище\n(Snowflake)", size=10, fill=BG, stroke=LINE)[0]
            frags.extend([b1, b2, b3])
            frags.append(arrow(x_left + card_w / 2, y_top + 135, x_left + card_w / 2, y_top + 158, color=LINE))
            frags.append(arrow(x_left + card_w / 2, y_top + 205, x_left + card_w / 2, y_top + 228, color=LINE))
        elif i == 1:
            t1 = textbox(x_left + card_w / 2, y_top + 110, "raw.orders", size=10, fill=BG, stroke=LINE)[0]
            t2 = textbox(x_left + card_w / 2, y_top + 175, "ref.fx_rates", size=10, fill=BG, stroke=LINE)[0]
            t3 = textbox(x_left + card_w / 2, y_top + 250, "mart.daily_revenue", size=10, fill=BG, stroke=LINE)[0]
            frags.extend([t1, t2, t3])
            frags.append(arrow(x_left + card_w / 2, y_top + 128, x_left + card_w / 2 - 20, y_top + 230, color=LINE))
            frags.append(arrow(x_left + card_w / 2, y_top + 193, x_left + card_w / 2 + 20, y_top + 230, color=LINE))
        elif i == 2:
            c1 = textbox(x_left + card_w / 2, y_top + 105, "orders.amount\n(UAH)", size=9, fill=BG, stroke=LINE)[0]
            c2 = textbox(x_left + card_w / 2, y_top + 165, "fx.rate_usd\n(float)", size=9, fill=BG, stroke=LINE)[0]
            expr = textbox(x_left + card_w / 2, y_top + 220, "amount / rate", size=9, fill="#ffffff", stroke=FIELD, bold=True)[0]
            c3 = textbox(x_left + card_w / 2, y_top + 270, "revenue.usd_total", size=9, fill=BG, stroke=LINE)[0]
            frags.extend([c1, c2, expr, c3])
            frags.append(arrow(x_left + card_w / 2, y_top + 128, x_left + card_w / 2, y_top + 205, color=LINE))
            frags.append(arrow(x_left + card_w / 2, y_top + 185, x_left + card_w / 2, y_top + 205, color=LINE))
            frags.append(arrow(x_left + card_w / 2, y_top + 235, x_left + card_w / 2, y_top + 255, color=LINE))
        elif i == 3:
            r1 = textbox(x_left + card_w / 2, y_top + 110, "Рядок #48102\n(order_id=981)", size=9, fill=BG, stroke=LINE)[0]
            r2 = textbox(x_left + card_w / 2, y_top + 180, "Рядок #120\n(USD=41.2)", size=9, fill=BG, stroke=LINE)[0]
            r3 = textbox(x_left + card_w / 2, y_top + 250, "Кортеж #8841\n(Why-provenance)", size=9, fill=BG, stroke=LINE)[0]
            frags.extend([r1, r2, r3])
            frags.append(arrow(x_left + card_w / 2, y_top + 135, x_left + card_w / 2, y_top + 230, color=LINE))
            frags.append(arrow(x_left + card_w / 2, y_top + 200, x_left + card_w / 2, y_top + 230, color=LINE))

    frags.append(arrow(50, 395, 850, 395, color=LINE, sw=2))
    frags.append(text(450, 418, "Зростання точності та обчислювальної складності збору метаданих →", size=11, bold=True, anchor="middle", color=INK))

    render(os.path.join(IMG_DIR, "lineage-granularity-spectrum.svg"), w, h, *frags, title="Спектр гранулярності Data Lineage")


def fig_bipartite_dag():
    """Фігура 2: Двочастковий граф (Bipartite DAG): Вузли-Дані та Вузли-Трансформації."""
    w, h = 880, 460
    frags = []

    frags.append(rect(40, 50, 24, 16, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=3))
    frags.append(text(72, 63, "Набір даних (Dataset)", size=11, anchor="start"))
    frags.append(rect(240, 50, 24, 16, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(272, 63, "Завдання / Запит (Job / Process)", size=11, anchor="start"))

    frags.append(rect(460, 45, 180, 30, fill="#f3f4f6", stroke=MUTED, sw=1, rx=4))
    frags.append(arrow(620, 60, 480, 60, color=POS, sw=2))
    frags.append(text(550, 56, "Upstream (Root Cause)", size=10, bold=True, color=POS, anchor="middle"))

    frags.append(rect(660, 45, 180, 30, fill="#f3f4f6", stroke=MUTED, sw=1, rx=4))
    frags.append(arrow(680, 60, 820, 60, color=NEG, sw=2))
    frags.append(text(750, 56, "Downstream (Impact)", size=10, bold=True, color=NEG, anchor="middle"))

    d_raw_orders, _, _ = textbox(110, 150, "raw_orders\n(PostgreSQL)", size=11, fill="#e0f2fe", stroke="#0284c7", rx=4)
    d_fx, _, _ = textbox(110, 260, "fx_rates\n(External API)", size=11, fill="#e0f2fe", stroke="#0284c7", rx=4)
    d_users, _, _ = textbox(110, 370, "crm_users\n(Kafka Topic)", size=11, fill="#e0f2fe", stroke="#0284c7", rx=4)
    frags.extend([d_raw_orders, d_fx, d_users])

    j_ingest, _, _ = textbox(300, 200, "dbt: stg_orders\n(SQL Clean & Join)", size=10, fill="#fef3c7", stroke="#d97706", rx=12)
    j_dim_user, _, _ = textbox(300, 370, "Spark: user_enrich\n(Streaming job)", size=10, fill="#fef3c7", stroke="#d97706", rx=12)
    frags.extend([j_ingest, j_dim_user])

    frags.append(arrow(180, 150, 230, 190, color=LINE))
    frags.append(arrow(180, 260, 230, 210, color=LINE))
    frags.append(arrow(180, 370, 220, 370, color=LINE))

    d_stg_orders, _, _ = textbox(490, 200, "stg_orders_clean\n(Parquet / Lake)", size=11, fill="#e0f2fe", stroke="#0284c7", rx=4)
    d_dim_customers, _, _ = textbox(490, 370, "dim_customers\n(Iceberg Table)", size=11, fill="#e0f2fe", stroke="#0284c7", rx=4)
    frags.extend([d_stg_orders, d_dim_customers])

    frags.append(arrow(370, 200, 420, 200, color=LINE))
    frags.append(arrow(375, 370, 420, 370, color=LINE))

    j_agg, _, _ = textbox(660, 280, "dbt: fct_revenue_monthly\n(Aggregation & Grouping)", size=10, fill="#fef3c7", stroke="#d97706", rx=12)
    frags.append(j_agg)

    frags.append(arrow(560, 215, 595, 265, color=LINE))
    frags.append(arrow(560, 355, 595, 295, color=LINE))

    d_mart, _, _ = textbox(810, 220, "fct_monthly_revenue\n(Datamart Table)", size=10, fill="#e0f2fe", stroke="#0284c7", rx=4)
    d_bi, _, _ = textbox(810, 340, "Executive Dashboard\n(BI Metrics Sheet)", size=10, fill="#f0fdf4", stroke="#16a34a", rx=4)
    frags.extend([d_mart, d_bi])

    frags.append(arrow(725, 265, 755, 235, color=LINE))
    frags.append(arrow(725, 295, 755, 330, color=LINE))

    render(os.path.join(IMG_DIR, "lineage-bipartite-dag.svg"), w, h, *frags, title="Двочастковий граф Data Lineage (Dataset ↔ Job)")


def fig_capture_methods():
    """Фігура 3: Порівняння способів збору Lineage: статичний аналіз, рантайм-інструментація, аудит логів."""
    w, h = 860, 420
    frags = []

    methods = [
        ("Статичний аналіз коду", "Парсинг SQL AST, аналіз репозиторіїв", [
            "• Працює до виконання запиту (CI/CD)",
            "• Дешевий аналіз всього каталогу",
            "• Не бачить динамічного SQL і UDF",
            "• Не фіксує обсяг та збої виконання"
        ], "#eff6ff", "#3b82f6"),
        ("Рантайм-інструментація", "Слухачі Spark, Trino, OpenLineage", [
            "• Фіксує реальні фізичні плани виконання",
            "• Знає точні партиції, рядки та байти",
            "• Відстежує статус запуску та помилки",
            "• Потребує інтеграції в кожен рушій"
        ], "#f0fdf4", "#16a34a"),
        ("Аналіз логів і журналу", "Скрапінг query_history у сховищах", [
            "• Не вимагає модифікації коду пайплайнів",
            "• Охоплює Ad-hoc запити аналітиків",
            "• Затримка обробки (polling логів)",
            "• Важко розібрати сесійні змінні"
        ], "#fefce8", "#ca8a04"),
    ]

    col_w = 250
    col_h = 310
    y_start = 75

    for idx, (m_title, m_sub, bullets, bg_col, border_col) in enumerate(methods):
        x_start = 35 + idx * 270
        frags.append(rect(x_start, y_start, col_w, col_h, fill=bg_col, stroke=border_col, sw=2, rx=8))
        frags.append(textbox(x_start + col_w / 2, y_start + 30, m_title, size=12, bold=True, fill=BG, stroke=border_col)[0])
        frags.append(text(x_start + col_w / 2, y_start + 65, m_sub, size=10, color=MUTED, anchor="middle"))

        frags.append(line(x_start + 15, y_start + 85, x_start + col_w - 15, y_start + 85, color=border_col, sw=1, dash="4,4"))

        for b_idx, bullet in enumerate(bullets):
            frags.append(text(x_start + 15, y_start + 120 + b_idx * 42, bullet, size=10, anchor="start", color=INK))

    render(os.path.join(IMG_DIR, "static-vs-runtime-extraction.svg"), w, h, *frags, title="Методи збору Data Lineage: компроміси та охоплення")


def fig_column_level_lineage():
    """Фігура 4: Стовпчиковий Lineage: прямі (трансформаційні) та непрямі (керуючі) залежності."""
    w, h = 880, 440
    frags = []

    frags.append(rect(40, 80, 220, 280, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(textbox(150, 105, "Таблиця raw.orders", size=11, bold=True, fill="#e2e8f0", stroke=LINE)[0])

    c_ord_id, _, _ = textbox(150, 150, "order_id (PK)", size=10, fill=BG, stroke=LINE)
    c_amt, _, _ = textbox(150, 205, "amount (UAH)", size=10, fill="#fef08a", stroke="#ca8a04", bold=True)
    c_status, _, _ = textbox(150, 260, "status ('PAID')", size=10, fill="#fed7aa", stroke="#ea580c", bold=True)
    c_cur, _, _ = textbox(150, 315, "currency_code", size=10, fill=BG, stroke=LINE)
    frags.extend([c_ord_id, c_amt, c_status, c_cur])

    frags.append(rect(40, 375, 220, 50, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    c_fx_rate, _, _ = textbox(150, 400, "fx.usd_rate (float)", size=10, fill="#fef08a", stroke="#ca8a04", bold=True)
    frags.append(c_fx_rate)

    sql_text = (
        "SELECT\n"
        "  o.order_id,\n"
        "  SUM(o.amount / fx.usd_rate) AS usd_revenue\n"
        "FROM raw.orders o\n"
        "JOIN fx ON o.currency = fx.code\n"
        "WHERE o.status = 'PAID'\n"
        "GROUP BY o.order_id"
    )
    frags.append(rect(310, 120, 270, 230, fill="#1e293b", stroke=LINE, sw=2, rx=6))
    frags.append(text(445, 145, "Трансформація (SQL Query AST)", size=11, color="#38bdf8", bold=True, anchor="middle"))
    frags.append(mtext(325, 180, sql_text, size=10, color="#f1f5f9", anchor="start", lh=1.4))

    frags.append(rect(630, 110, 220, 220, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(textbox(740, 135, "mart.fct_revenue", size=11, bold=True, fill="#e2e8f0", stroke=LINE)[0])

    c_out_id, _, _ = textbox(740, 185, "order_id", size=10, fill=BG, stroke=LINE)
    c_out_usd, _, _ = textbox(740, 255, "usd_revenue", size=10, fill="#86efac", stroke="#16a34a", bold=True)
    frags.extend([c_out_id, c_out_usd])

    frags.append(arrow(215, 205, 310, 215, color="#16a34a", sw=2))
    frags.append(arrow(215, 400, 310, 290, color="#16a34a", sw=2))
    frags.append(arrow(580, 240, 680, 255, color="#16a34a", sw=2))

    frags.append(arrow(215, 260, 310, 265, color="#ea580c", sw=2))

    frags.append(line(320, 380, 370, 380, color="#16a34a", sw=2))
    frags.append(text(380, 384, "Пряма трансформаційна залежність (Direct Data Flow)", size=10, anchor="start", color=INK))

    frags.append(line(320, 410, 370, 410, color="#ea580c", sw=2, dash="4,4"))
    frags.append(text(380, 414, "Непряма залежність за керуванням (Control/Predicate Flow у WHERE/JOIN)", size=10, anchor="start", color=INK))

    render(os.path.join(IMG_DIR, "column-level-lineage-flow.svg"), w, h, *frags, title="Стовпчиковий Lineage: прямі та непрямі потоки залежностей")


if __name__ == "__main__":
    fig_granularity_spectrum()
    fig_bipartite_dag()
    fig_capture_methods()
    fig_column_level_lineage()
    print("Всі 4 фігури успішно згенеровано.")
