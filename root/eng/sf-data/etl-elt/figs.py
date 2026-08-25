# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Топологія обчислень та потоків даних: ETL проти ELT ────────────
def fig_etl_vs_elt_topology():
    W, H = 880, 520
    parts = []

    # Заголовки панелей
    parts.append(text(440, 28, "Топологія обчислень: винесення трансформації назовні чи всередину", size=16, bold=True))
    
    # ── Верхня половина: Класичний ETL ──
    y_etl = 135
    parts.append(rect(20, 55, 840, 205, fill="#fcfcfd", stroke="#d0d5dd", sw=1.2, rx=8))
    parts.append(text(40, 80, "ETL (Extract -> Transform -> Load)", size=14, bold=True, color=POS, anchor="start"))
    parts.append(text(840, 80, "Трансформація в проміжному шарі до запису в сховище", size=12, color=MUTED, anchor="end"))

    # Блоки ETL
    s1, w_s1, h_s1 = textbox(110, y_etl, "Джерела даних\nOLTP, API, логи", size=12, fill="#ffffff", stroke=LINE, sw=1.4, min_w=140)
    parts.append(s1)

    t_box, w_tb, h_tb = textbox(410, y_etl, "Проміжний обчислювач\n(Spark, Flink, сервіс)\nОчищення, агрегація", size=12, fill="#fdecea", stroke=POS, sw=1.8, min_w=190)
    parts.append(t_box)

    w_box, w_wb, h_wb = textbox(720, y_etl, "Цільове сховище\n(DWH, Data Marts)\nЛише готова схема", size=12, fill="#ffffff", stroke=LINE, sw=1.4, min_w=160)
    parts.append(w_box)

    # Стрілки ETL
    parts.append(arrow(110 + w_s1/2, y_etl, 410 - w_tb/2, y_etl, color=POS, sw=2))
    parts.append(text((110 + w_s1/2 + 410 - w_tb/2)/2, y_etl - 16, "1. Видобування (E)", size=11, color=POS, bold=True))
    parts.append(text((110 + w_s1/2 + 410 - w_tb/2)/2, y_etl + 18, "сирі батчі", size=10, color=MUTED))

    parts.append(arrow(410 + w_tb/2, y_etl, 720 - w_wb/2, y_etl, color=POS, sw=2))
    parts.append(text((410 + w_tb/2 + 720 - w_wb/2)/2, y_etl - 16, "3. Завантаження (L)", size=11, color=POS, bold=True))
    parts.append(text((410 + w_tb/2 + 720 - w_wb/2)/2, y_etl + 18, "готова схема", size=10, color=MUTED))

    parts.append(text(410, y_etl + 62, "2. Трансформація (T) у пам'яті middleware — вузьке місце RAM", size=11, color=POS, italic=True))

    # ── Нижня половина: Сучасний ELT ──
    y_elt = 385
    parts.append(rect(20, 275, 840, 225, fill="#fcfcfd", stroke="#d0d5dd", sw=1.2, rx=8))
    parts.append(text(40, 300, "ELT (Extract -> Load -> Transform)", size=14, bold=True, color=FIELD, anchor="start"))
    parts.append(text(840, 300, "Швидке скидання сирих даних та обробка рушієм сховища", size=12, color=MUTED, anchor="end"))

    # Блоки ELT
    s2, w_s2, h_s2 = textbox(110, y_elt, "Джерела даних\nOLTP, CDC, події", size=12, fill="#ffffff", stroke=LINE, sw=1.4, min_w=140)
    parts.append(s2)

    # Велика зона сховища/лейкхаусу
    parts.append(rect(260, 325, 580, 160, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(550, 345, "Хмарне сховище / Lakehouse (розподілені обчислення + об'єктне сховище)", size=11, bold=True, color=FIELD))

    raw_box, w_rb, h_rb = textbox(380, y_elt + 20, "Сирий шар (Bronze)\nНезмінні JSON/Parquet\nПовна історія", size=11, fill="#ffffff", stroke=LINE, sw=1.4, min_w=160)
    parts.append(raw_box)

    gold_box, w_gb, h_gb = textbox(720, y_elt + 20, "Очищений шар (Gold)\nВітрини даних, агрегати\ndbt / SQL-моделі", size=11, fill="#ffffff", stroke=FIELD, sw=1.8, min_w=170)
    parts.append(gold_box)

    # Стрілки ELT
    parts.append(arrow(110 + w_s2/2, y_elt, 380 - w_rb/2, y_elt + 20, color=FIELD, sw=2))
    parts.append(text((110 + w_s2/2 + 380 - w_rb/2)/2 - 10, y_elt - 6, "1. E + 2. L", size=11, color=FIELD, bold=True))
    parts.append(text((110 + w_s2/2 + 380 - w_rb/2)/2 - 10, y_elt + 12, "прямий потік", size=10, color=MUTED))

    parts.append(arrow(380 + w_rb/2, y_elt + 20, 720 - w_gb/2, y_elt + 20, color=FIELD, sw=2.2))
    parts.append(text((380 + w_rb/2 + 720 - w_gb/2)/2, y_elt - 4, "3. Трансформація (T)", size=11, color=FIELD, bold=True))
    parts.append(text((380 + w_rb/2 + 720 - w_gb/2)/2, y_elt + 14, "розподілений SQL", size=10, color=FIELD))

    render(os.path.join(IMG, "etl-vs-elt-topology.svg"), W, H, *parts,
           title="Порівняння топологій ETL та ELT")


# ── Фігура 2: Збереження контексту та еволюція схем ───────────────────────────
def fig_schema_evolution_replay():
    W, H = 860, 440
    parts = []

    parts.append(text(430, 26, "Еволюція схеми джерела: втрата інформації в ETL проти відтворюваності в ELT", size=15, bold=True))

    # Ліва колонка: ETL при зміні схеми
    x_l = 225
    parts.append(rect(25, 55, 395, 365, fill="#fdfbfb", stroke=POS, sw=1.3, rx=6))
    parts.append(text(x_l, 82, "ETL: Жорстка фільтрація на вході", size=13, bold=True, color=POS))

    e1, _, _ = textbox(x_l, 130, "Джерело додає нове поле:\n{id, sum, client_tier}", size=11, fill="#ffffff", stroke=LINE, sw=1.2, min_w=240)
    parts.append(e1)

    e2, _, _ = textbox(x_l, 215, "Конвеєр ETL (старий код):\nпропускає лише {id, sum},\nполе client_tier відкинуто!", size=11, fill="#fdecea", stroke=POS, sw=1.5, min_w=240)
    parts.append(e2)
    parts.append(arrow(x_l, 155, x_l, 185, color=POS, sw=1.6))

    e3, _, _ = textbox(x_l, 305, "Сховище DWH:\nісторія за пів року без tier.\nВідновити неможливо!", size=11, fill="#ffffff", stroke=POS, sw=1.4, min_w=240)
    parts.append(e3)
    parts.append(arrow(x_l, 245, x_l, 275, color=POS, sw=1.6))

    parts.append(text(x_l, 385, "Непоправна втрата історичного контексту", size=11, color=POS, bold=True))

    # Права колонка: ELT при зміні схеми
    x_r = 635
    parts.append(rect(440, 55, 395, 365, fill="#fbfdfb", stroke=FIELD, sw=1.3, rx=6))
    parts.append(text(x_r, 82, "ELT: Сирий шар та відкладена проекція", size=13, bold=True, color=FIELD))

    l1, _, _ = textbox(x_r, 130, "Джерело додає нове поле:\n{id, sum, client_tier}", size=11, fill="#ffffff", stroke=LINE, sw=1.2, min_w=240)
    parts.append(l1)

    l2, _, _ = textbox(x_r, 215, "Сирий шар Bronze (Lakehouse):\nзаписано повний JSON/рядки\nв незмінному вигляді", size=11, fill="#eafaf1", stroke=FIELD, sw=1.5, min_w=240)
    parts.append(l2)
    parts.append(arrow(x_r, 155, x_r, 185, color=FIELD, sw=1.6))

    l3, _, _ = textbox(x_r, 305, "SQL-модель (dbt / View):\nдодаємо client_tier у запит і\nперераховуємо всю історію!", size=11, fill="#ffffff", stroke=FIELD, sw=1.4, min_w=240)
    parts.append(l3)
    parts.append(arrow(x_r, 245, x_r, 275, color=FIELD, sw=1.6))

    parts.append(text(x_r, 385, "Повна відтворюваність (Zero Data Loss)", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "schema-evolution-replay.svg"), W, H, *parts,
           title="Поведінка схем і відтворюваність даних")


# ── Фігура 3: Межа безпеки та гібридний патерн EtLT ──────────────────────────
def fig_privacy_etlt_boundary():
    W, H = 880, 420
    parts = []

    parts.append(text(440, 26, "Гібридний патерн EtLT: ізоляція персональних даних (PII) на межі довіри", size=15, bold=True))

    # Зона 1: Контур джерела / Небезпечний периметр
    parts.append(rect(20, 55, 340, 335, fill="#fdfbf7", stroke="#e67e22", sw=1.4, rx=8))
    parts.append(text(190, 80, "Периметр джерела (PII, сирий доступ)", size=12, bold=True, color="#d35400"))

    b_src, _, _ = textbox(190, 140, "Операційна база\nПаспорти, телефони, email\nСекретні ключі", size=11, fill="#ffffff", stroke=LINE, sw=1.2, min_w=220)
    parts.append(b_src)

    b_light, _, _ = textbox(190, 265, "Легкий шлюз (t)\nМаскування: email -> hash\nШифрування / Токенізація", size=11, fill="#fdecea", stroke=POS, sw=1.6, min_w=220)
    parts.append(b_light)
    parts.append(arrow(150, 175, 150, 225, color=POS, sw=1.8))
    parts.append(text(160, 202, "E (Extract)", size=10, color=MUTED, anchor="start"))

    # Межа довіри (Trust boundary)
    parts.append(line(400, 55, 400, 390, color=POS, sw=2, dash="6 4"))
    parts.append(mtext(400, 408, ["Межа регуляторної довіри (GDPR / HIPAA)"], size=10, color=POS, bold=True))

    # Зона 2: Хмарне аналітичне сховище
    parts.append(rect(440, 55, 420, 335, fill="#f4fbf7", stroke=FIELD, sw=1.4, rx=8))
    parts.append(text(650, 80, "Аналітичний периметр (Знеособлені дані)", size=12, bold=True, color=FIELD))

    b_load, _, _ = textbox(650, 140, "Завантаження в Lakehouse (L)\nОчищені від PII сирі події\nБезпечне довге зберігання", size=11, fill="#ffffff", stroke=LINE, sw=1.2, min_w=240)
    parts.append(b_load)

    b_heavy, _, _ = textbox(650, 265, "Важка аналітика (T)\nSQL-джойни, когортний аналіз\nМашинне навчання, вітрини", size=11, fill="#eafaf1", stroke=FIELD, sw=1.8, min_w=240)
    parts.append(b_heavy)
    parts.append(arrow(600, 175, 600, 225, color=FIELD, sw=1.8))
    parts.append(text(610, 202, "T (Heavy Transform)", size=10, color=FIELD, anchor="start"))

    # Перехід крізь межу довіри
    parts.append(arrow(300, 140, 530, 140, color="#d35400", sw=2))
    parts.append(text(415, 125, "L (Load без PII)", size=11, bold=True, color="#d35400"))

    render(os.path.join(IMG, "privacy-etlt-boundary.svg"), W, H, *parts,
           title="Гібридна модель EtLT та межі приватності")


# ── Фігура 4: Затримка проти накладних витрат обчислень ───────────────────────
def fig_pipeline_latency_throughput():
    W, H = 840, 440
    parts = []

    ox, oy = 110, 360
    ax_w, ax_h = 660, 280

    parts.append(text(440, 26, "Компроміс розміру порції (Batch Size): затримка доставки проти накладних витрат", size=15, bold=True))

    # Осі
    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    parts.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))

    parts.append(text(ox + ax_w, oy + 28, "Розмір порції / Інтервал запуску (W) →", size=12, color=MUTED, anchor="end"))
    parts.append(mtext(ox - 16, oy - ax_h + 10, ["Питомі витрати /", "Затримка даних"], size=12, color=MUTED, anchor="end"))

    x0 = ox + 20
    xe = ox + ax_w - 40

    # 1. Крива затримки (росте лінійно з розміром вікна)
    parts.append('<path d="M%.0f %.0f L %.0f %.0f" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (x0, oy - 30, xe, oy - 240, POS))
    parts.append(text(xe - 10, oy - 250, "Затримка доступності даних (Latency ~ W)", size=12, color=POS, bold=True, anchor="end"))

    # 2. Крива накладних витрат на запис (спадає як 1/W — амортизація відкриття файлів/транзакцій)
    parts.append('<path d="M%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (x0, oy - 250, x0 + 80, oy - 60, xe, oy - 35, NEG))
    parts.append(text(x0 + 160, oy - 110, "Накладні витрати I/O на 1 запис (~ 1/W)", size=12, color=NEG, bold=True, anchor="start"))

    # 3. Сумарна функція вартості
    parts.append('<path d="M%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="2.8" stroke-dasharray="5 3"/>'
                 % (x0, oy - 260, x0 + 180, oy - 30, xe, oy - 230, FIELD))
    parts.append(text(xe - 10, oy - 215, "Сумарна ціна обробки й затримки", size=12, color=FIELD, bold=True, anchor="end"))

    # Оптимальна точка (мікробатч)
    opt_x = x0 + 195
    opt_y = oy - 98
    parts.append(circle(opt_x, opt_y, 5, fill=FIELD, stroke=INK, sw=1.5))
    parts.append(line(opt_x, opt_y, opt_x, oy, color=MUTED, sw=1.4, dash="4 4"))
    parts.append(mtext(opt_x, oy + 20, ["Оптимум", "мікробатчу"], size=11, bold=True, color=FIELD))

    render(os.path.join(IMG, "pipeline-latency-throughput.svg"), W, H, *parts,
           title="Залежність затримки та вартості від розміру батчу")


if __name__ == "__main__":
    fig_etl_vs_elt_topology()
    fig_schema_evolution_replay()
    fig_privacy_etlt_boundary()
    fig_pipeline_latency_throughput()
    print("All figures successfully generated in", IMG)
