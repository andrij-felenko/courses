# -*- coding: utf-8 -*-
"""Фігури теми «Стратегії віялового розсилання (Fan-Out Strategies)». Вивід — ./img/*.svg"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"
GRAY_F  = "#f8f9fa"
PURPLE_F= "#f3e8fd"


# ── 1. fanout-write-vs-read: Запис (Push) проти Читання (Pull) та Гібрид ─────
def fig_fanout_write_vs_read():
    W, H = 940, 500
    f = []

    f.append(text(470, 26, "Стратегії оновлення стрічки: Fan-Out on Write (Push) проти Fan-Out on Read (Pull)", size=13, bold=True, color=INK))

    # Ліва колонка: Fan-Out on Write (Push)
    f.append(rect(15, 45, 445, 440, fill=GRAY_F, stroke=POS, sw=1.2, rx=8))
    f.append(text(237, 68, "Fan-Out on Write (Push / Ingestion-Time)", size=12, bold=True, color=POS))

    b_w_pub, _, _ = textbox(110, 125, "Користувач\nпублікує допис", size=10, bold=True, min_w=110, fill=FILL, stroke=LINE)
    f.append(b_w_pub)

    f.append(arrow(170, 125, 215, 125, color=POS, sw=1.6))

    b_w_svc, _, _ = textbox(295, 125, "Сервіс публікації\nОтримує 10 000 читачів\nГенерує 10 000 записів", size=10, bold=True, min_w=150, fill=WARN_F, stroke=POS)
    f.append(b_w_svc)

    f.append(arrow(295, 160, 295, 195, color=POS, sw=1.6))
    f.append(text(345, 180, "Віяло записів", size=9.5, color=POS))

    b_w_ib1, _, _ = textbox(150, 230, "Вхідна скринька 1\n(Redis List / Cache)", size=9.5, min_w=135, fill=GREEN_F, stroke=FIELD)
    b_w_ib2, _, _ = textbox(150, 280, "Вхідна скринька 2\n(Redis List / Cache)", size=9.5, min_w=135, fill=GREEN_F, stroke=FIELD)
    b_w_ibN, _, _ = textbox(150, 330, "Вхідна скринька N\n(10 000 користувачів)", size=9.5, min_w=135, fill=RED_F, stroke=POS)
    f.extend([b_w_ib1, b_w_ib2, b_w_ibN])

    f.append(line(295, 195, 235, 195, color=POS, sw=1.3))
    f.append(line(235, 195, 235, 330, color=POS, sw=1.3))
    f.append(arrow(235, 230, 220, 230, color=POS, sw=1.3))
    f.append(arrow(235, 280, 220, 280, color=POS, sw=1.3))
    f.append(arrow(235, 330, 220, 330, color=POS, sw=1.3))

    b_w_read, _, _ = textbox(360, 280, "Читач відкриває стрічку:\nO(1) читання з кешу\nЛатентність: 2–5 мс", size=9.5, bold=True, min_w=135, fill=GREEN_F, stroke=FIELD)
    f.append(b_w_read)
    f.append(arrow(80, 280, 20, 280, color=FIELD, sw=1.4))

    b_w_sum, _, _ = textbox(237, 420, "Характеристики Push:\n• Запис: O(F) — важкий, ризик лавини для суперзірок\n• Читання: O(1) — миттєве, дешеве для 99% запитів\n• Вузьке місце: посилення запису (Write Amplification)", size=9.5, min_w=415, fill=FILL, stroke=LINE)
    f.append(b_w_sum)

    # Права колонка: Fan-Out on Read (Pull)
    f.append(rect(480, 45, 445, 440, fill=GRAY_F, stroke=NEG, sw=1.2, rx=8))
    f.append(text(702, 68, "Fan-Out on Read (Pull / Query-Time)", size=12, bold=True, color=NEG))

    b_r_pub, _, _ = textbox(575, 125, "Користувач\nпублікує допис", size=10, bold=True, min_w=110, fill=FILL, stroke=LINE)
    f.append(b_r_pub)

    f.append(arrow(635, 125, 685, 125, color=NEG, sw=1.6))

    b_r_db, _, _ = textbox(780, 125, "Сховище автора\nОдин запис у таблицю:\nO(1) операція", size=10, bold=True, min_w=150, fill=GREEN_F, stroke=FIELD)
    f.append(b_r_db)

    b_r_user, _, _ = textbox(575, 280, "Читач відкриває стрічку\n(читає 500 авторів)", size=10, bold=True, min_w=130, fill=WARN_F, stroke=NEG)
    f.append(b_r_user)

    f.append(arrow(645, 280, 695, 280, color=NEG, sw=1.6))

    b_r_agg, _, _ = textbox(790, 280, "Агрегатор стрічки:\nВіяло запитів до 500 авторів\nСортування та злиття (Merge)\nЛатентність: 150–400 мс", size=9.5, bold=True, min_w=170, fill=RED_F, stroke=POS)
    f.append(b_r_agg)

    b_r_sum, _, _ = textbox(702, 420, "Характеристики Pull:\n• Запис: O(1) — легкий, суперзірки не створюють хвиль\n• Читання: O(F·log k) — важке віяло розпитування (Scatter)\n• Вузьке місце: колосальне навантаження на читання та БД", size=9.5, min_w=415, fill=FILL, stroke=LINE)
    f.append(b_r_sum)

    render(out("fanout-write-vs-read.svg"), W, H, *f)


# ── 2. tail-latency-amplification: Ампліфікація затримок у Scatter-Gather ───
def fig_tail_latency():
    W, H = 940, 480
    f = []

    f.append(text(470, 28, "Ампліфікація затримки хвоста (Tail Latency Amplification) у Scatter-Gather RPC", size=13, bold=True, color=INK))

    # Ліва панель: Структура розпитування 1 -> N
    f.append(rect(15, 50, 420, 415, fill=GRAY_F, stroke=LINE, sw=1.2, rx=8))
    f.append(text(225, 75, "Паралельне віяло до N мікросервісів / шардів", size=11, bold=True, color=INK))

    b_coord, _, _ = textbox(95, 250, "Клієнтський\nКоординатор\n(Aggregator)", size=10.5, bold=True, min_w=120, fill=BLUE_F, stroke=NEG)
    f.append(b_coord)

    # 4 вузли-відповідачі
    b_n1, _, _ = textbox(290, 130, "Вузол 1: 12 мс (Швидко)", size=9.5, min_w=150, fill=GREEN_F, stroke=FIELD)
    b_n2, _, _ = textbox(290, 195, "Вузол 2: 15 мс (Швидко)", size=9.5, min_w=150, fill=GREEN_F, stroke=FIELD)
    b_n3, _, _ = textbox(290, 260, "Вузол ... : 14 мс (Швидко)", size=9.5, min_w=150, fill=GREEN_F, stroke=FIELD)
    b_nN, _, _ = textbox(290, 335, "Вузол N (Хвіст p99):\n350 мс (GC Pause / I/O Spike)", size=9.5, bold=True, min_w=170, fill=RED_F, stroke=POS)
    f.extend([b_n1, b_n2, b_n3, b_nN])

    f.append(arrow(160, 235, 205, 135, color=LINE, sw=1.3))
    f.append(arrow(160, 245, 205, 195, color=LINE, sw=1.3))
    f.append(arrow(160, 255, 205, 260, color=LINE, sw=1.3))
    f.append(arrow(160, 265, 200, 335, color=POS, sw=1.8))

    b_res, _, _ = textbox(225, 415, "Підсумок для клієнта:\nЛатентність запиту = max(T_1, T_2, ..., T_N) = 350 мс!\nКлієнт чекає на НАЙПОВІЛЬНІШИЙ вузол", size=9.5, bold=True, min_w=390, fill=WARN_F, stroke=POS)
    f.append(b_res)

    # Права панель: Ймовірнісна деградація від степеня віяла N
    f.append(rect(455, 50, 470, 415, fill=GRAY_F, stroke=POS, sw=1.2, rx=8))
    f.append(text(690, 75, "Ймовірність зіткнення з затримкою p99: P = 1 − (1 − 0.01)ⁿ", size=11, bold=True, color=POS))

    # Стовпчики ймовірностей
    # N=1 -> 1%
    f.append(rect(480, 110, 80, 240, fill=FILL, stroke=MUTED, rx=4))
    f.append(rect(480, 340, 80, 10, fill=GREEN_F, stroke=FIELD, rx=2))
    f.append(text(520, 330, "1%", size=10, bold=True, color=FIELD))
    f.append(text(520, 370, "N = 1", size=10, bold=True, color=INK))
    f.append(text(520, 388, "1 запит", size=9.5, color=MUTED))

    # N=10 -> 9.6%
    f.append(rect(570, 110, 80, 240, fill=FILL, stroke=MUTED, rx=4))
    f.append(rect(570, 327, 80, 23, fill=GREEN_F, stroke=FIELD, rx=2))
    f.append(text(610, 315, "9.6%", size=10, bold=True, color=FIELD))
    f.append(text(610, 370, "N = 10", size=10, bold=True, color=INK))
    f.append(text(610, 388, "10 шардів", size=9.5, color=MUTED))

    # N=50 -> 39.5%
    f.append(rect(660, 110, 80, 240, fill=FILL, stroke=MUTED, rx=4))
    f.append(rect(660, 255, 80, 95, fill=WARN_F, stroke="#d35400", rx=2))
    f.append(text(700, 240, "39.5%", size=10, bold=True, color="#d35400"))
    f.append(text(700, 370, "N = 50", size=10, bold=True, color=INK))
    f.append(text(700, 388, "50 шардів", size=9.5, color=MUTED))

    # N=100 -> 63.4%
    f.append(rect(750, 110, 80, 240, fill=FILL, stroke=MUTED, rx=4))
    f.append(rect(750, 198, 80, 152, fill=RED_F, stroke=POS, rx=2))
    f.append(text(790, 185, "63.4%", size=10, bold=True, color=POS))
    f.append(text(790, 370, "N = 100", size=10, bold=True, color=INK))
    f.append(text(790, 388, "100 шардів", size=9.5, color=MUTED))

    # N=200 -> 86.6%
    f.append(rect(840, 110, 75, 240, fill=FILL, stroke=MUTED, rx=4))
    f.append(rect(840, 142, 75, 208, fill=RED_F, stroke=POS, rx=2))
    f.append(text(877, 130, "86.6%", size=10, bold=True, color=POS))
    f.append(text(877, 370, "N = 200", size=10, bold=True, color=INK))
    f.append(text(877, 388, "200 шардів", size=9.5, color=MUTED))

    b_math_concl, _, _ = textbox(690, 425, "Висновок: при широкому віялі (N ≥ 100) більшість запитів (>63%)\nгарантовано зазнають затримки найгіршого 99-го перцентиля!", size=9.5, bold=True, min_w=440, fill=WARN_F, stroke=POS)
    f.append(b_math_concl)

    render(out("tail-latency-amplification.svg"), W, H, *f)


# ── 3. broker-fanout-topologies: Топології віяла в брокерах повідомлень ─────
def fig_broker_topologies():
    W, H = 940, 480
    f = []

    f.append(text(470, 26, "Топології віялового розсилання в асинхронних брокерах повідомлень", size=13, bold=True, color=INK))

    # Панель 1: RabbitMQ Fanout Exchange (Broadcast на черги)
    f.append(rect(15, 45, 295, 420, fill=GRAY_F, stroke=FIELD, sw=1.2, rx=8))
    f.append(text(162, 68, "1. RabbitMQ Fanout Exchange", size=11, bold=True, color=FIELD))

    b_p1, _, _ = textbox(162, 105, "Видавець (Publisher)\nНадсилає подію в Exchange", size=9.5, min_w=180, fill=FILL, stroke=LINE)
    b_ex, _, _ = textbox(162, 175, "Fanout Exchange\nКопіює без перевірки ключів\nу всі зв'язані черги", size=9.5, bold=True, min_w=190, fill=GREEN_F, stroke=FIELD)
    f.extend([b_p1, b_ex])
    f.append(arrow(162, 130, 162, 150, color=FIELD, sw=1.5))

    b_q1, _, _ = textbox(175, 245, "Черга A → Сервіс білінгу", size=9.5, min_w=165, fill=BLUE_F, stroke=NEG)
    b_q2, _, _ = textbox(175, 295, "Черга B → Сервіс пошти", size=9.5, min_w=165, fill=BLUE_F, stroke=NEG)
    b_q3, _, _ = textbox(175, 345, "Черга C → Аналітика (Slow!)", size=9.5, min_w=165, fill=RED_F, stroke=POS)
    f.extend([b_q1, b_q2, b_q3])

    # Шина ліворуч від черг
    f.append(line(55, 175, 55, 345, color=FIELD, sw=1.4))
    f.append(line(55, 175, 67, 175, color=FIELD, sw=1.4))
    f.append(arrow(55, 245, 85, 245, color=FIELD, sw=1.4))
    f.append(arrow(55, 295, 85, 295, color=FIELD, sw=1.4))
    f.append(arrow(55, 345, 85, 345, color=FIELD, sw=1.4))

    b_sum1, _, _ = textbox(162, 415, "Особливість:\nІзольовані буфери пам'яті.\nПовільний споживач забиває свою чергу.", size=9.5, min_w=275, fill=FILL, stroke=LINE)
    f.append(b_sum1)

    # Панель 2: AWS SNS -> SQS Fanout (Хмарний керований мікросервісний міст)
    f.append(rect(322, 45, 295, 420, fill=GRAY_F, stroke=NEG, sw=1.2, rx=8))
    f.append(text(469, 68, "2. AWS SNS Topic → SQS Queues", size=11, bold=True, color=NEG))

    b_p2, _, _ = textbox(469, 105, "Мікросервіс-джерело\nSNS Publish(TopicARN)", size=9.5, min_w=180, fill=FILL, stroke=LINE)
    b_sns, _, _ = textbox(469, 175, "AWS SNS Topic\nКерований віяловий брокер\nФільтрація за атрибутами", size=9.5, bold=True, min_w=190, fill=BLUE_F, stroke=NEG)
    f.extend([b_p2, b_sns])
    f.append(arrow(469, 130, 469, 150, color=NEG, sw=1.5))

    b_sqs1, _, _ = textbox(482, 245, "SQS 1: Оплата (Deadlines)", size=9.5, min_w=165, fill=GREEN_F, stroke=FIELD)
    b_sqs2, _, _ = textbox(482, 295, "SQS 2: Склад (FIFO)", size=9.5, min_w=165, fill=GREEN_F, stroke=FIELD)
    b_sqs3, _, _ = textbox(482, 345, "Lambda: Аудит безпеки", size=9.5, min_w=165, fill=BLUE_F, stroke=NEG)
    f.extend([b_sqs1, b_sqs2, b_sqs3])

    # Шина ліворуч від черг
    f.append(line(362, 175, 362, 345, color=NEG, sw=1.4))
    f.append(line(362, 175, 374, 175, color=NEG, sw=1.4))
    f.append(arrow(362, 245, 392, 245, color=NEG, sw=1.4))
    f.append(arrow(362, 295, 392, 295, color=NEG, sw=1.4))
    f.append(arrow(362, 345, 392, 345, color=NEG, sw=1.4))

    b_sum2, _, _ = textbox(469, 415, "Особливість:\nСерверлесс-масштабування,\nавтоматичні повтори, нульове адміністрування.", size=9.5, min_w=275, fill=FILL, stroke=LINE)
    f.append(b_sum2)

    # Панель 3: Kafka Log Broadcast (Consumer Groups)
    f.append(rect(630, 45, 295, 420, fill=GRAY_F, stroke=POS, sw=1.2, rx=8))
    f.append(text(777, 68, "3. Apache Kafka Consumer Groups", size=11, bold=True, color=POS))

    b_p3, _, _ = textbox(777, 105, "Kafka Producer\nОдин запис у топік на диск", size=9.5, min_w=180, fill=FILL, stroke=LINE)
    b_klog, _, _ = textbox(777, 175, "Kafka Partition Log\nНезмінний лог на диску\nОкремі покажчики (Offsets)", size=9.5, bold=True, min_w=190, fill=WARN_F, stroke=POS)
    f.extend([b_p3, b_klog])
    f.append(arrow(777, 130, 777, 150, color=POS, sw=1.5))

    b_cg1, _, _ = textbox(790, 245, "Group A (Offset: 120 400)", size=9.5, min_w=165, fill=GREEN_F, stroke=FIELD)
    b_cg2, _, _ = textbox(790, 295, "Group B (Offset: 120 398)", size=9.5, min_w=165, fill=GREEN_F, stroke=FIELD)
    b_cg3, _, _ = textbox(790, 345, "Group C (Lag: 50 000!)", size=9.5, min_w=165, fill=RED_F, stroke=POS)
    f.extend([b_cg1, b_cg2, b_cg3])

    # Шина ліворуч від груп
    f.append(line(670, 175, 670, 345, color=POS, sw=1.4))
    f.append(line(670, 175, 682, 175, color=POS, sw=1.4))
    f.append(arrow(670, 245, 700, 245, color=POS, sw=1.4))
    f.append(arrow(670, 295, 700, 295, color=POS, sw=1.4))
    f.append(arrow(670, 345, 700, 345, color=POS, sw=1.4))

    b_sum3, _, _ = textbox(777, 415, "Особливість:\nЗберігання єдиної копії даних.\nПовільна група відстає, але не зупиняє інших.", size=9.5, min_w=275, fill=FILL, stroke=LINE)
    f.append(b_sum3)

    render(out("broker-fanout-topologies.svg"), W, H, *f)


# ── 4. scatter-gather-lifecycle: Життєвий цикл Scatter-Gather із геджуванням 
def fig_scatter_gather_lifecycle():
    W, H = 940, 480
    f = []

    f.append(text(470, 26, "Життєвий цикл Scatter-Gather: паралельний старт, спекулятивне геджування та відміна", size=13, bold=True, color=INK))

    # Схема часової шкали
    f.append(rect(15, 48, 910, 415, fill=GRAY_F, stroke=LINE, sw=1.2, rx=8))

    # Координатор
    b_c, _, _ = textbox(110, 110, "Scatter-Gather\nCoordinator", size=10.5, bold=True, min_w=130, fill=BLUE_F, stroke=NEG)
    f.append(b_c)

    # Лінії запитів
    f.append(arrow(185, 95, 340, 95, color=FIELD, sw=1.8))
    f.append(text(260, 85, "t=0: Запит A", size=9.5, color=FIELD))

    f.append(arrow(185, 125, 340, 175, color=FIELD, sw=1.8))
    f.append(text(260, 140, "t=0: Запит B", size=9.5, color=FIELD))

    # Сервіс A
    b_sA, _, _ = textbox(440, 95, "Сервіс A (Ціни)\nУспіх за 18 мс", size=10, min_w=150, fill=GREEN_F, stroke=FIELD)
    f.append(b_sA)
    f.append(arrow(525, 95, 680, 110, color=FIELD, sw=1.8))
    f.append(text(600, 85, "t=18 мс: Результат", size=9.5, color=FIELD))

    # Сервіс B (Первинний вузол застряг)
    b_sB1, _, _ = textbox(440, 175, "Сервіс B (Репліка 1)\nЗависання в черзі...", size=10, bold=True, min_w=160, fill=WARN_F, stroke="#d35400")
    f.append(b_sB1)

    # Таймер геджування
    f.append(line(340, 220, 520, 220, color=POS, sw=1.5, dash="4,4"))
    f.append(text(430, 210, "Таймаут геджування (p95 = 25 мс) вичерпано!", size=9.5, bold=True, color=POS))

    # Запуск геджованого запиту на Репліку 2
    f.append(arrow(185, 135, 340, 265, color=POS, sw=1.8))
    f.append(text(260, 240, "t=25 мс: Геджований Запит B2", size=9.5, color=POS))

    b_sB2, _, _ = textbox(440, 265, "Сервіс B (Репліка 2)\nУспіх за 12 мс", size=10, min_w=160, fill=GREEN_F, stroke=FIELD)
    f.append(b_sB2)
    f.append(arrow(530, 265, 680, 135, color=FIELD, sw=1.8))
    f.append(text(605, 248, "t=37 мс: Результат B2", size=9.5, color=FIELD))

    # Сигнал скасування (Cancel) на Репліку 1
    f.append(arrow(680, 130, 530, 175, color=POS, sw=1.5))
    f.append(text(615, 160, "Скасування (Cancel)", size=9.5, color=POS))

    # Агрегація
    b_agg, _, _ = textbox(775, 125, "Злиття результатів\n(Aggregation)\nЛатентність: 37 мс\n(замість 350 мс!)", size=10.5, bold=True, min_w=165, fill=GREEN_F, stroke=FIELD, sw=1.8)
    f.append(b_agg)

    b_expl, _, _ = textbox(470, 395, "Ключові механізми надійності Scatter-Gather:\n1. Bounded Concurrency: обмежений пул корутин / потоків координатора\n2. Speculative Hedging: паралельний дублюючий запит при перевищенні p95 порогу\n3. Cancellation Propagation: миттєве скидання зайвих гілок через Context / Stop Token\n4. Graceful Degradation: видача часткового результату при досягненні твердого дедлайну", size=9.5, min_w=850, fill=FILL, stroke=LINE)
    f.append(b_expl)

    render(out("scatter-gather-lifecycle.svg"), W, H, *f)


if __name__ == "__main__":
    fig_fanout_write_vs_read()
    fig_tail_latency()
    fig_broker_topologies()
    fig_scatter_gather_lifecycle()
    print("Figures generated successfully.")
