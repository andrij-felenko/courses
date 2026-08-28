#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Строк сертифіката й парк, що спинився вночі».
Всі фігури будуються через єдину бібліотеку svgkit.
"""

import os
import sys

# scripts/ у корені репо — 4 рівні вгору від root/course/embedded/<slug>
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")


def fig1_deadlock():
    """Фігура 1: Замкнене коло ізоляції пристрою при закінченні строку сертифіката."""
    w, h = 860, 420
    frags = []

    # 1. Лівий блок — Пристрій
    b_dev = rect(40, 60, 240, 240, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8)
    t_dev = text(160, 88, "ВБУДОВАНИЙ ПРИСТРІЙ", size=13, bold=True, color=INK)
    t_dev_sub = text(160, 108, "(у полі / без доступу руками)", size=11, color=MUTED)

    box_ca, _, _ = textbox(160, 150, "Trust Store у Flash:\nRoot CA (notAfter прострочено)", size=11, fill="#fdecea", stroke=POS, bold=True, pad=6)
    box_rtc, _, _ = textbox(160, 210, "RTC / Таймер:\nЗбій або точний UTC > notAfter", size=11, fill="#fff7ed", stroke="#ea580c", pad=6)
    box_state, _, _ = textbox(160, 265, "Стан: Zombie Mode\nOTA клієнт заблоковано", size=11, fill="#fee2e2", stroke=POS, bold=True, pad=5)

    frags.extend([b_dev, t_dev, t_dev_sub, box_ca, box_rtc, box_state])

    # 2. Правий блок — Хмарний сервер / OTA
    b_srv = rect(580, 60, 240, 240, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8)
    t_srv = text(700, 88, "ХМАРНИЙ СЕРВЕР / OTA", size=13, bold=True, color=INK)
    t_srv_sub = text(700, 108, "(оновлений бекенд)", size=11, color=MUTED)

    box_srv_ca, _, _ = textbox(700, 150, "Новий TLS сертифікат:\nВидано новим Root CA", size=11, fill="#eaf0fd", stroke=NEG, bold=True, pad=6)
    box_ota, _, _ = textbox(700, 210, "Сервіс оновлення OTA:\nГотовий надіслати новий CA", size=11, fill="#f0fdf4", stroke=FIELD, pad=6)
    box_srv_st, _, _ = textbox(700, 265, "Стан: Очікує підключення\nКанал керування розірвано", size=11, fill="#f3f4f6", stroke=MUTED, pad=5)

    frags.extend([b_srv, t_srv, t_srv_sub, box_srv_ca, box_ota, box_srv_st])

    # 3. Центральна зона взаємодії — Рукостискання TLS та розрив
    frags.append(arrow(280, 130, 580, 130, color=LINE, sw=1.6))
    frags.append(text(430, 120, "1. TLS ClientHello →", size=11, bold=True, color=INK))

    frags.append(arrow(580, 165, 280, 165, color=LINE, sw=1.6))
    frags.append(text(430, 155, "← 2. ServerHello + Certificate Chain", size=11, color=INK))

    # Блок помилки валідації по центру
    b_err, _, _ = textbox(430, 210, "Перевірка ланцюга сертифікатів:\nnotAfter < Current_Time\nПОМИЛКА: CERT_HAS_EXPIRED", size=11, fill="#fdecea", stroke=POS, bold=True, pad=8)
    frags.append(b_err)

    frags.append(arrow(340, 248, 520, 248, color=POS, sw=1.8))
    frags.append(text(430, 265, "3. TLS Alert: Handshake Failure (ABORT)", size=11, bold=True, color=POS))

    # 4. Нижня смуга глухого кута (Deadlock Loop)
    deadlock_box = rect(100, 330, 660, 65, fill="#fef2f2", stroke=POS, sw=2, rx=6)
    d_t1 = text(430, 355, "ПАРАДОКС ТЕЛЕКЕРУВАННЯ: ЗАМКНЕНЕ КОЛО БЕЗВИХОДІ", size=12, bold=True, color=POS)
    d_t2 = text(430, 378, "Щоб оновити сертифікат, потрібен робочий зв'язок з OTA → але зв'язок неможливий через прострочений сертифікат", size=11, color=INK)
    frags.extend([deadlock_box, d_t1, d_t2])

    path = os.path.join(OUT_DIR, "cert-expiration-deadlock.svg")
    render(path, w, h, *frags)


def fig2_timeline():
    """Фігура 2: Часова шкала безперервної ротації довірених кореневих центрів."""
    w, h = 880, 390
    frags = []

    # Часова вісь
    y_axis = 310
    frags.append(line(70, y_axis, 820, y_axis, color=LINE, sw=2))
    frags.append(arrow(810, y_axis, 840, y_axis, color=LINE, sw=2))
    frags.append(text(840, y_axis - 10, "Час (роки)", size=11, color=MUTED, anchor="end"))

    # Поділки років на осі
    years = [
        (90, "Рік 0\n(Випуск)"),
        (210, "Рік 3"),
        (330, "Рік 6"),
        (450, "Рік 9"),
        (570, "Рік 12"),
        (690, "Рік 15"),
        (790, "Рік 18"),
    ]
    for x_pos, yr_text in years:
        frags.append(line(x_pos, y_axis - 5, x_pos, y_axis + 5, color=LINE, sw=1.5))
        frags.append(mtext(x_pos, y_axis + 20, yr_text, size=10, color=INK, anchor="middle"))

    # Смуга 1: Кореневий сертифікат CA-1 (Рік 0 .. Рік 10)
    # Активна фаза: 90 .. 450 (роки 0-9)
    frags.append(rect(90, 80, 360, 36, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(270, 103, "Root CA 1: Основний робочий довірчий якір", size=11, bold=True, color=NEG))
    # Фаза закінчення CA-1: 450 .. 490 (рік 9-10)
    frags.append(rect(450, 80, 40, 36, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    frags.append(text(470, 103, "notAfter", size=9, bold=True, color=POS))

    # Смуга 2: Кореневий сертифікат CA-2 (Встановлено на Рік 6, діє до Рік 16)
    # Зона очікування у Flash: 330 .. 430
    frags.append(rect(330, 145, 100, 36, fill="#f3f4f6", stroke=MUTED, sw=1.5, rx=4))
    frags.append(text(380, 168, "CA 2 (Standby)", size=10, color=MUTED))
    # Активна фаза CA-2: 430 .. 730
    frags.append(rect(430, 145, 300, 36, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=4))
    frags.append(text(580, 168, "Root CA 2: Перемикання бекенда на CA 2 (Активний якір)", size=11, bold=True, color=FIELD))
    # Фаза закінчення CA-2: 730 .. 760
    frags.append(rect(730, 145, 30, 36, fill="#fdecea", stroke=POS, sw=1.5, rx=4))

    # Смуга 3: Кореневий сертифікат CA-3 (Завантажується через OTA на Році 12)
    frags.append(rect(570, 210, 80, 36, fill="#f3f4f6", stroke=MUTED, sw=1.5, rx=4))
    frags.append(text(610, 233, "OTA CA 3", size=10, color=MUTED))
    frags.append(rect(650, 210, 160, 36, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(730, 233, "Root CA 3: Робочий", size=10, bold=True, color=NEG))

    # Вертикальні лінії критичних подій
    # Подія 1: Рік 6 — Розгортання CA-2 в прошивках
    frags.append(line(330, 60, 330, y_axis, color=MUTED, sw=1, dash="3 3"))
    frags.append(text(330, 50, "Рік 6: Введення CA 2 у Trust Store", size=10, color=INK, anchor="middle"))

    # Подія 2: Вікно перекриття (Overlap Window) роки 6..9
    frags.append(rect(330, 265, 120, 30, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(390, 284, "Вікно перекриття (Dual Trust)", size=10, bold=True, color="#b45309"))

    # Подія 3: Рік 9 — Ротація сервера на CA-2
    frags.append(line(450, 60, 450, y_axis, color=POS, sw=1.5, dash="3 3"))
    frags.append(text(450, 50, "Рік 9: Сервери переходять на CA 2", size=10, bold=True, color=POS, anchor="middle"))

    path = os.path.join(OUT_DIR, "dual-root-rollover-timeline.svg")
    render(path, w, h, *frags)


def fig3_est_flow():
    """Фігура 3: Послідовність ротації сертифіката пристрою за протоколом EST (RFC 7030)."""
    w, h = 860, 430
    frags = []

    # Колонки (Swimlanes)
    col_dev_x = 150
    col_net_x = 430
    col_srv_x = 710

    # Розділові межі колонок (між блоками, щоб не перетинати написи)
    frags.append(line(290, 20, 290, 410, color="#e2e8f0", sw=1.5, dash="4 4"))
    frags.append(line(570, 20, 570, 410, color="#e2e8f0", sw=1.5, dash="4 4"))

    # Заголовки колонок
    b_c1, _, _ = textbox(col_dev_x, 40, "ПРИСТРІЙ (Клієнт)\nFlash Slot A / Slot B", size=12, fill="#eaf0fd", stroke=NEG, bold=True, pad=8)
    b_c2, _, _ = textbox(col_net_x, 40, "ЗАХИЩЕНИЙ КАНАЛ\nmTLS на старому сертифікаті", size=11, fill="#f3f4f6", stroke=LINE, pad=8)
    b_c3, _, _ = textbox(col_srv_x, 40, "СЕРВЕР РЕЄСТРАЦІЇ\nEST Server / PKI CA", size=12, fill="#eaf0fd", stroke=NEG, bold=True, pad=8)
    frags.extend([b_c1, b_c2, b_c3])

    # Крок 1: Локальний тригер 70% часу
    b_s1, _, _ = textbox(col_dev_x, 105, "1. Тригер ротації:\n70% строку дії вичерпано\nГенерація пари ключів у Slot B", size=10, fill="#fef3c7", stroke="#d97706", pad=6)
    frags.append(b_s1)

    # Крок 2: Запит /cacerts
    frags.append(arrow(260, 160, 600, 160, color=LINE, sw=1.5))
    frags.append(text(col_net_x, 150, "2. GET /.well-known/est/cacerts", size=10, bold=True, color=INK))

    frags.append(arrow(600, 195, 260, 195, color=LINE, sw=1.5))
    frags.append(text(col_net_x, 185, "← 200 OK: Актуальні Root / Intermediate CA", size=10, color=FIELD))

    # Крок 3: Запит /simplereenroll (підписаний старим ключем)
    frags.append(arrow(260, 240, 600, 240, color=LINE, sw=1.5))
    frags.append(text(col_net_x, 230, "3. POST /.well-known/est/simplereenroll (PKCS#10 CSR)", size=10, bold=True, color=INK))

    # Блок обробки сервером
    b_s3, _, _ = textbox(col_srv_x, 285, "4. Перевірка mTLS клієнта\nта підпису CSR →\nВипуск нового X.509", size=10, fill="#f0fdf4", stroke=FIELD, pad=6)
    frags.append(b_s3)

    # Крок 4: Відповідь із новим сертифікатом
    frags.append(arrow(600, 330, 260, 330, color=FIELD, sw=1.8))
    frags.append(text(col_net_x, 320, "← 200 OK: Новий сертифікат пристрою (PKCS#7)", size=10, bold=True, color=FIELD))

    # Крок 5: Атомарна фіксація у Flash
    b_s5, _, _ = textbox(col_dev_x, 375, "5. Атомарний запис у Slot B\nПеревірка нового ланцюга\nSlot B стає Active (Swap)", size=10, fill="#dcfce7", stroke=FIELD, bold=True, pad=6)
    frags.append(b_s5)

    path = os.path.join(OUT_DIR, "est-rotation-flow.svg")
    render(path, w, h, *frags)


def fig4_recovery_ladder():
    """Фігура 4: Ешелонована драбина відновлення зв'язку та довіри."""
    w, h = 860, 400
    frags = []

    # 4 сходинки відновлення (від штатної до критичної аварійної)
    steps = [
        (
            80, 50, 700, 65,
            "Рівень 1: Штатний захищений канал (Primary mTLS)",
            "Основний сертифікат пристрою (Slot A) + Робочий Root CA. Автоматична ротація за таймером (EST/ACME).",
            "#dcfce7", FIELD
        ),
        (
            80, 130, 700, 65,
            "Рівень 2: Резервний довірчий якір (Dual Root Trust Store)",
            "Вбудований запасний Root CA (Slot B). Якщо основний CA скомпрометовано або прострочено, TLS перемикається на резервний.",
            "#eaf0fd", NEG
        ),
        (
            80, 210, 700, 65,
            "Рівень 3: Виділений аварійний Bootstrap-канал",
            "Незмінний заводський сертифікат (IDevID у Secure Element) + Окремий ізольований Bootstrap CA для перевипуску ключів.",
            "#fef3c7", "#d97706"
        ),
        (
            80, 290, 700, 65,
            "Рівень 4: Позасмугове відновлення довіри (Emergency Offline Signature)",
            "Криптографічний пакет оновлення, підписаний кореневим Master Key розробника + Монотонний лічильник захисту від відкату (Rollback Protection).",
            "#fdecea", POS
        ),
    ]

    for x, y, bw, bh, title_s, desc_s, fill_c, stroke_c in steps:
        frags.append(rect(x, y, bw, bh, fill=fill_c, stroke=stroke_c, sw=1.6, rx=6))
        frags.append(text(x + 20, y + 24, title_s, size=12, bold=True, color=stroke_c, anchor="start"))
        frags.append(text(x + 20, y + 48, desc_s, size=10, color=INK, anchor="start"))

    # Стрілка ескалації ліворуч
    frags.append(line(45, 60, 45, 340, color=POS, sw=2))
    frags.append(arrow(45, 330, 45, 355, color=POS, sw=2))
    frags.append(mtext(30, 200, "Е\nС\nК\nА\nЛ\nА\nЦ\nІ\nЯ", size=10, bold=True, color=POS, anchor="middle"))

    path = os.path.join(OUT_DIR, "fallback-recovery-ladder.svg")
    render(path, w, h, *frags)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    fig1_deadlock()
    fig2_timeline()
    fig3_est_flow()
    fig4_recovery_ladder()
    print("Всі фігури успішно згенеровано у", OUT_DIR)


if __name__ == "__main__":
    main()
