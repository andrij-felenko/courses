#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми notification-fanout."""

import sys
import os

# Додаємо scripts до шляху імпорту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, fitbox, rect, line, arrow, text, mtext, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

def fig_fanout_write_vs_read(path):
    """Ілюстрація: Fanout-on-Write проти Fanout-on-Read та гібридна модель."""
    w, h = 840, 480
    frags = []

    # Заголовок лівої колонки: Fanout-on-Write (Push)
    frags.append(rect(20, 50, 385, 410, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(212, 75, "Fanout-on-Write (Push / Матеріалізація)", size=14, bold=True, color=INK))
    
    # Подія автора
    tb1, _, _ = textbox(212, 115, "Автор публікує подію\n[Write: O(1)]", size=12, pad=8, fill="#ffffff", stroke=LINE)
    frags.append(tb1)
    
    # Стрілка розгортання
    frags.append(arrow(212, 140, 212, 175, color=POS, sw=2))
    frags.append(text(250, 160, "Розмноження на N копій", size=11, color=POS, bold=True))

    # Скриньки фоловерів
    tb_w1, _, _ = textbox(110, 210, "Стрічка Юзера 1\n(Redis/RAM Inbox)", size=11, pad=6, fill="#eaf0fd", stroke=NEG)
    tb_w2, _, _ = textbox(212, 210, "Стрічка Юзера 2\n(Redis/RAM Inbox)", size=11, pad=6, fill="#eaf0fd", stroke=NEG)
    tb_w3, _, _ = textbox(314, 210, "Стрічка Юзера N\n(Redis/RAM Inbox)", size=11, pad=6, fill="#eaf0fd", stroke=NEG)
    frags.extend([tb_w1, tb_w2, tb_w3])

    # Читання
    frags.append(arrow(212, 250, 212, 290, color=FIELD, sw=2))
    frags.append(text(212, 275, "Читання зі своєї скриньки: O(1)", size=11, color=FIELD, bold=True))

    tb_r_res, _, _ = textbox(212, 325, "Користувач відкриває стрічку\n[Миттєвий зріз пам'яті]", size=12, pad=8, fill="#edf7ed", stroke=FIELD)
    frags.append(tb_r_res)

    # Характеристика
    fb_w = fitbox(35, 375, 355, 70, "Вузьке місце: Write Amplification.\nПублікація селебріті (N = 10 млн) забиває черги,\nдиски та пам'ять для неактивних фоловерів.", size=11, pad=6, fill="#fff2f2", stroke=POS)
    frags.append(fb_w)

    # Заголовок правої колонки: Fanout-on-Read (Pull)
    frags.append(rect(435, 50, 385, 410, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(627, 75, "Fanout-on-Read (Pull / Ліниве злиття)", size=14, bold=True, color=INK))

    # Подія автора
    tb2, _, _ = textbox(627, 115, "Автор публікує подію\n[Запис у персональний Outbox: O(1)]", size=12, pad=8, fill="#ffffff", stroke=LINE)
    frags.append(tb2)

    # Стрілка вниз без розмноження
    frags.append(arrow(627, 140, 627, 185, color=LINE, sw=1.5))
    frags.append(text(627, 165, "1 запис у БД автора", size=11, color=MUTED))

    # Збережений стан
    tb_db, _, _ = textbox(627, 210, "Таблиця постів авторів\n(1 запис на подію)", size=11, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_db)

    # Запит користувача
    frags.append(arrow(627, 245, 627, 290, color=POS, sw=2))
    frags.append(text(627, 270, "Запит: SELECT + K-way Merge", size=11, color=POS, bold=True))

    tb_pull_res, _, _ = textbox(627, 325, "Користувач відкриває стрічку\n[Складне злиття K джерел на льоту]", size=12, pad=8, fill="#fff8e6", stroke="#d97706")
    frags.append(tb_pull_res)

    # Характеристика
    fb_r = fitbox(450, 375, 355, 70, "Вузьке місце: Read Latency & High IOPS.\nКожен перегляд стрічки вимагає опитування сотень\nавторів і сортування. Не масштабується при високому RPS.", size=11, pad=6, fill="#fff2f2", stroke=POS)
    frags.append(fb_r)

    render(path, w, h, *frags)


def fig_pubsub_broker_topologies(path):
    """Ілюстрація: Топології Pub/Sub брокерів для Fanout (Kafka, RabbitMQ, SNS->SQS)."""
    w, h = 860, 490
    frags = []

    # Секція 1: Kafka (Partitioned Log + Consumer Groups)
    frags.append(rect(15, 45, 265, 425, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(147, 70, "Apache Kafka (Журнал подій)", size=13, bold=True, color=INK))
    
    tb_k_pub, _, _ = textbox(147, 105, "Продюсер подій", size=11, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_k_pub)
    frags.append(arrow(147, 125, 147, 155, color=LINE, sw=1.5))

    # Топік з партиціями
    frags.append(rect(30, 155, 235, 110, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(147, 175, "Topic: notifications.events", size=11, bold=True, color=NEG))
    frags.append(rect(40, 190, 215, 20, fill="#ffffff", stroke=LINE, sw=1))
    frags.append(text(147, 204, "Partition 0 [Offset 0, 1, 2...]", size=9, color=INK))
    frags.append(rect(40, 215, 215, 20, fill="#ffffff", stroke=LINE, sw=1))
    frags.append(text(147, 229, "Partition 1 [Offset 0, 1, 2...]", size=9, color=INK))
    frags.append(rect(40, 240, 215, 20, fill="#ffffff", stroke=LINE, sw=1))
    frags.append(text(147, 254, "Partition 2 [Offset 0, 1, 2...]", size=9, color=INK))

    frags.append(arrow(90, 265, 90, 310, color=LINE, sw=1.5))
    frags.append(arrow(200, 265, 200, 310, color=LINE, sw=1.5))

    tb_cg1, _, _ = textbox(90, 335, "Consumer Group:\nPush Dispatcher", size=10, pad=5, fill="#edf7ed", stroke=FIELD)
    tb_cg2, _, _ = textbox(200, 335, "Consumer Group:\nEmail Dispatcher", size=10, pad=5, fill="#edf7ed", stroke=FIELD)
    frags.extend([tb_cg1, tb_cg2])

    fb_k = fitbox(25, 385, 245, 75, "Властивість:\nПовідомлення зберігаються раз.\nКожна група консюмерів читає\nжурнал незалежно зі своєю швидкістю.", size=10, pad=5, fill="#ffffff", stroke=LINE)
    frags.append(fb_k)

    # Секція 2: RabbitMQ (Fanout Exchange)
    frags.append(rect(295, 45, 265, 425, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(427, 70, "RabbitMQ (Fanout Exchange)", size=13, bold=True, color=INK))

    tb_r_pub, _, _ = textbox(427, 105, "Продюсер подій", size=11, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_r_pub)
    frags.append(arrow(427, 125, 427, 160, color=LINE, sw=1.5))

    # Fanout exchange
    frags.append(circle(427, 185, 25, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(427, 189, "Fanout Ex", size=10, bold=True, color="#d97706"))

    frags.append(arrow(410, 205, 360, 255, color=LINE, sw=1.5))
    frags.append(arrow(444, 205, 494, 255, color=LINE, sw=1.5))

    tb_rq1, _, _ = textbox(350, 280, "Queue: push-tasks\n[In-Memory RAM]", size=10, pad=5, fill="#eaf0fd", stroke=NEG)
    tb_rq2, _, _ = textbox(504, 280, "Queue: email-tasks\n[In-Memory RAM]", size=10, pad=5, fill="#eaf0fd", stroke=NEG)
    frags.extend([tb_rq1, tb_rq2])

    frags.append(arrow(350, 305, 350, 340, color=FIELD, sw=1.5))
    frags.append(arrow(504, 305, 504, 340, color=FIELD, sw=1.5))

    tb_rw1, _, _ = textbox(350, 355, "Push Workers", size=10, pad=4, fill="#edf7ed", stroke=FIELD)
    tb_rw2, _, _ = textbox(504, 355, "Email Workers", size=10, pad=4, fill="#edf7ed", stroke=FIELD)
    frags.extend([tb_rw1, tb_rw2])

    fb_r = fitbox(305, 385, 245, 75, "Властивість:\nБрокер дублює повідомлення\nу всі підв'язані черги. Висока\nшвидкість, стан черг у пам'яті.", size=10, pad=5, fill="#ffffff", stroke=LINE)
    frags.append(fb_r)

    # Секція 3: AWS SNS -> SQS Multi-queue Fanout
    frags.append(rect(575, 45, 270, 425, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(710, 70, "AWS SNS → SQS Fanout", size=13, bold=True, color=INK))

    tb_s_pub, _, _ = textbox(710, 105, "Мікросервіс-джерело", size=11, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_s_pub)
    frags.append(arrow(710, 125, 710, 160, color=LINE, sw=1.5))

    tb_sns, _, _ = textbox(710, 185, "Amazon SNS Topic\n(Pub/Sub роутер)", size=11, pad=6, fill="#fdecea", stroke=POS)
    frags.append(tb_sns)

    frags.append(arrow(670, 210, 635, 255, color=LINE, sw=1.5))
    frags.append(arrow(750, 210, 785, 255, color=LINE, sw=1.5))

    tb_sqs1, _, _ = textbox(630, 280, "SQS Push Queue\n+ Dead Letter", size=10, pad=5, fill="#eaf0fd", stroke=NEG)
    tb_sqs2, _, _ = textbox(785, 280, "SQS Webhook Queue\n+ Dead Letter", size=10, pad=5, fill="#eaf0fd", stroke=NEG)
    frags.extend([tb_sqs1, tb_sqs2])

    frags.append(arrow(630, 305, 630, 340, color=FIELD, sw=1.5))
    frags.append(arrow(785, 305, 785, 340, color=FIELD, sw=1.5))

    tb_sw1, _, _ = textbox(630, 355, "Push Lambda / ECS", size=10, pad=4, fill="#edf7ed", stroke=FIELD)
    tb_sw2, _, _ = textbox(785, 355, "Webhook Egress", size=10, pad=4, fill="#edf7ed", stroke=FIELD)
    frags.extend([tb_sw1, tb_sw2])

    fb_s = fitbox(585, 385, 250, 75, "Властивість:\nПовна ізоляція черг: падіння\nзовнішнього вебхука не впливає\nна доставку мобільних push-сповіщень.", size=10, pad=5, fill="#ffffff", stroke=LINE)
    frags.append(fb_s)

    render(path, w, h, *frags)


def fig_notification_pipeline(path):
    """Ілюстрація: Наскрізний конвеєр Fanout розсилки (Enrichment, Batching, Transports)."""
    w, h = 880, 480
    frags = []

    # Вхідна подія
    tb_in, _, _ = textbox(100, 110, "Вхідна подія\n(Event Trigger)", size=12, pad=8, fill="#ffffff", stroke=LINE)
    frags.append(tb_in)

    frags.append(arrow(175, 110, 240, 110, color=LINE, sw=1.8))
    frags.append(text(207, 100, "1 подія", size=10, color=MUTED))

    # Диспетчер розгортання
    tb_exp, _, _ = textbox(330, 110, "Fanout Resolver\n[Розгортання на N підписників]", size=12, pad=8, fill="#fdecea", stroke=POS)
    frags.append(tb_exp)

    # Стрілка вниз до збагачувача
    frags.append(arrow(330, 145, 330, 195, color=POS, sw=2))
    frags.append(text(405, 170, "N адресатів (User IDs)", size=11, color=POS, bold=True))

    # Збагачувач (Enricher / Prefetcher)
    tb_enr, _, _ = textbox(330, 230, "Enrichment & User Preferences\n[Фільтрація mute/DND, вибір девайс-токенів]", size=12, pad=8, fill="#ffffff", stroke=LINE)
    frags.append(tb_enr)

    # Батчинг та розбиття на чанки
    frags.append(arrow(330, 265, 330, 310, color=LINE, sw=1.8))
    frags.append(text(420, 288, "Батчі по 500-1000 токенів", size=11, color=MUTED))

    tb_batch, _, _ = textbox(330, 340, "Batch Chunker & Sharded Queue\n[Пакування в оптимізовані пакети]", size=12, pad=8, fill="#fef3c7", stroke="#d97706")
    frags.append(tb_batch)

    # Розгалуження на адаптери провайдерів
    frags.append(arrow(445, 340, 560, 200, color=LINE, sw=1.5))
    frags.append(arrow(465, 340, 560, 300, color=LINE, sw=1.5))
    frags.append(arrow(445, 340, 560, 400, color=LINE, sw=1.5))

    # Адаптер 1: APNs HTTP/2
    tb_apns, _, _ = textbox(675, 200, "Apple APNs Adapter\n[HTTP/2 Multiplexing, Persistent TLS]", size=11, pad=6, fill="#eaf0fd", stroke=NEG)
    frags.append(tb_apns)

    # Адаптер 2: FCM HTTP v1
    tb_fcm, _, _ = textbox(675, 300, "Google FCM Adapter\n[HTTP Batch API v1, 500 msgs/req]", size=11, pad=6, fill="#edf7ed", stroke=FIELD)
    frags.append(tb_fcm)

    # Адаптер 3: SMTP / Email
    tb_smtp, _, _ = textbox(675, 400, "Email Dispatcher\n[SMTP Connection Pool / SES API]", size=11, pad=6, fill="#ffffff", stroke=LINE)
    frags.append(tb_smtp)

    # Канал зворотного зв'язку (Feedback)
    frags.append(arrow(795, 200, 830, 200, color=POS, sw=1.5))
    frags.append(line(830, 200, 830, 60, color=POS, sw=1.5, dash="4,4"))
    frags.append(arrow(830, 60, 330, 60, color=POS, sw=1.5))
    frags.append(text(580, 50, "Feedback Loop (410 Gone / Невалідні токени → інвалідація в БД)", size=10, color=POS, bold=True))

    render(path, w, h, *frags)


def fig_thundering_herd_mitigation(path):
    """Ілюстрація: Запобігання Thundering Herd (Jitter, Caching, Token Cleanup)."""
    w, h = 840, 460
    frags = []

    # Ліва частина: Без захисту (Thundering Herd Spikes)
    frags.append(rect(20, 45, 385, 395, fill="#fff2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(212, 70, "Без захисту: Thundering Herd", size=13, bold=True, color=POS))

    tb_bad_bcast, _, _ = textbox(212, 115, "Миттєва розсилка на 10 млн юзерів\n[t = 0 c: всі push надсилаються разом]", size=11, pad=6, fill="#ffffff", stroke=POS)
    frags.append(tb_bad_bcast)

    frags.append(arrow(212, 150, 212, 195, color=POS, sw=2))
    frags.append(text(212, 175, "10 млн екранів спалахують одночасно", size=10, color=POS))

    tb_bad_click, _, _ = textbox(212, 230, "Масовий клік і відкриття додатка\n[t = 2-5 c: 1 000 000 RPS до API]", size=11, pad=6, fill="#ffffff", stroke=POS)
    frags.append(tb_bad_click)

    frags.append(arrow(212, 265, 212, 310, color=POS, sw=2))
    frags.append(text(212, 290, "Перевантаження БД та бекендів", size=10, color=POS))

    fb_bad_res = fitbox(35, 335, 355, 85, "Наслідок: Каскадна відмова (Cascading Failure).\nБД падає під важкими SELECT-запитами стрічки,\nчерги забиваються, виникає відмова в обслуговуванні.", size=11, pad=6, fill="#ffffff", stroke=POS)
    frags.append(fb_bad_res)

    # Права частина: Із захистом (Jitter, Self-Contained Payloads, Backpressure)
    frags.append(rect(435, 45, 385, 395, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(627, 70, "Зі стійкою архітектурою Fanout", size=13, bold=True, color=FIELD))

    tb_good_bcast, _, _ = textbox(627, 115, "Розмазування відправки з Jitter\n[Розподіл розсилки у вікні 30-120 c]", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(tb_good_bcast)

    frags.append(arrow(627, 150, 627, 195, color=FIELD, sw=2))
    frags.append(text(627, 175, "Згладжений потік доставлених push", size=10, color=FIELD))

    tb_good_payload, _, _ = textbox(627, 230, "Самодостатній Payload у Push\n+ CDN/Кеш на рівні API Gateway", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(tb_good_payload)

    frags.append(arrow(627, 265, 627, 310, color=FIELD, sw=2))
    frags.append(text(627, 290, "Кешовані відповіді, контрольований RPS", size=10, color=FIELD))

    fb_good_res = fitbox(450, 335, 355, 85, "Результат: Плавна робота системи.\nНавантаження на API розтягнуте в часі,\nтрафік читання обслуговується з кешу,\nпровайдери не блокують за перевищення лімітів.", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(fb_good_res)

    render(path, w, h, *frags)


def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    fig_fanout_write_vs_read(os.path.join(img_dir, "fanout-write-vs-read.svg"))
    fig_pubsub_broker_topologies(os.path.join(img_dir, "pubsub-broker-topologies.svg"))
    fig_notification_pipeline(os.path.join(img_dir, "notification-pipeline.svg"))
    fig_thundering_herd_mitigation(os.path.join(img_dir, "thundering-herd-mitigation.svg"))
    print("Всі 4 фігури успішно згенеровано.")

if __name__ == "__main__":
    main()
