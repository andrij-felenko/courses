# -*- coding: utf-8 -*-
"""Фігури до теми «QGroundControl: що це і яку задачу розв'язує»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def two_loops():
    f = []
    # ── панель «Борт» ───────────────────────────────────────────────────────
    f.append(rect(40, 60, 400, 320, fill="#ffffff"))
    f.append(text(240, 88, "Борт", size=15, bold=True))
    b1, _, _ = textbox(140, 150, "Датчики", size=13)
    b2, _, _ = textbox(340, 150, "Оцінювач стану", size=13)
    b3, _, _ = textbox(340, 260, "Регулятор", size=13)
    b4, _, _ = textbox(140, 260, "Мотори", size=13)
    f += [b1, b2, b3, b4]
    f.append(arrow(178, 150, 276, 150))
    f.append(arrow(340, 169, 340, 241))
    f.append(arrow(294, 260, 176, 260))
    f.append(arrow(140, 242, 140, 169))
    f.append(text(240, 335, "сотні разів на секунду", size=13, color=MUTED))

    # ── панель «Земля» ──────────────────────────────────────────────────────
    f.append(rect(690, 60, 290, 320, fill="#ffffff"))
    f.append(text(835, 88, "Земля", size=15, bold=True))
    g1, _, _ = textbox(835, 160, "QGroundControl", size=13)
    g2, _, _ = textbox(835, 285, "Людина", size=13)
    f += [g1, g2]
    f.append(arrow(808, 180, 808, 266))
    f.append(arrow(866, 266, 866, 180))
    f.append(text(795, 228, "показ", size=11, color=MUTED, anchor="end"))
    f.append(text(880, 228, "натиск", size=11, color=MUTED, anchor="start"))
    f.append(text(835, 340, "одиниці разів на секунду", size=13, color=MUTED))

    # ── канал між панелями ──────────────────────────────────────────────────
    f.append(arrow(446, 150, 684, 150, color=NEG))
    f.append(text(565, 132, "телеметрія  1–10 Гц", size=12, color=NEG))
    f.append(arrow(684, 285, 446, 285, color=POS))
    f.append(text(565, 267, "команди — зрідка", size=12, color=POS))
    f.append(text(565, 212, "тонкий радіоканал", size=12, color=MUTED))

    render(os.path.join(OUT, 'two-loops.svg'), 1020, 420, *f)


def five_jobs():
    f = []
    jobs = [
        (130, "Налаштувати\nкалібрування, параметри"),
        (350, "Спланувати\nмаршрут, геозона"),
        (570, "Летіти\nтелеметрія, карта, відео"),
        (790, "Розібрати політ\nжурнали з борту"),
        (1010, "Скомандувати\nзліт, дім, посадка"),
    ]
    for cx, s in jobs:
        b, _, _ = textbox(cx, 90, s, size=12)
        f.append(b)
        f.append(arrow(cx, 118, cx, 196))

    f.append(rect(60, 200, 1060, 150, fill="#ffffff"))
    f.append(text(590, 230, "Спільний ґрунт", size=14, bold=True))
    for cx, s in ((250, "Одне з'єднання"),
                  (590, "Одна модель апарата"),
                  (930, "Метадані параметрів")):
        b, _, _ = textbox(cx, 297, s, size=13)
        f.append(b)

    render(os.path.join(OUT, 'five-jobs.svg'), 1180, 400, *f)


def mirror_authority():
    f = []
    f.append(rect(40, 70, 320, 320, fill="#ffffff"))
    f.append(text(200, 100, "Борт", size=15, bold=True))
    f.append(text(200, 124, "джерело істини", size=12, color=MUTED))
    for y, s in ((150, "Параметри в незалежній\nпам'яті"),
                 (225, "Місія, геозона,\nточки збору"),
                 (300, "Поточний стан апарата")):
        f.append(fitbox(60, y, 280, 56, s, size=13))

    f.append(rect(760, 70, 320, 320, fill="#ffffff"))
    f.append(text(920, 100, "Станція", size=15, bold=True))
    f.append(text(920, 124, "дзеркало з правом запису", size=12, color=MUTED))
    for y, s in ((150, "Кеш параметрів\nна диску"),
                 (225, "Копія плану\nу вікні"),
                 (300, "Останній відомий кадр")):
        f.append(fitbox(780, y, 280, 56, s, size=13))

    f.append(arrow(372, 170, 748, 170, color=NEG))
    f.append(text(560, 152, "читання при під'єднанні", size=12, color=NEG))
    f.append(arrow(748, 248, 372, 248, color=POS))
    f.append(text(560, 230, "запис із підтвердженням", size=12, color=POS))
    f.append(line(372, 326, 748, 326, color=MUTED, dash="6 5"))
    f.append(text(560, 308, "звірка контрольної суми", size=12, color=MUTED))

    render(os.path.join(OUT, 'mirror-authority.svg'), 1120, 430, *f)


def one_code_many_faces():
    f = []
    src, _, _ = textbox(190, 190, "Одна кодова база\n(відкритий репозиторій)", size=13)
    f.append(src)
    outs = [
        (90, "Стабільний випуск  vX.Y.Z\nз гілки випуску"),
        (200, "Денна збірка\nз головної гілки"),
        (310, "Вендорська збірка\nсвій бренд, урізаний набір"),
    ]
    for cy, s in outs:
        b, w, _ = textbox(780, cy, s, size=12)
        f.append(b)
        f.append(arrow(287, 190, 780 - w / 2 - 4, cy))

    render(os.path.join(OUT, 'one-code-many-faces.svg'), 1080, 400, *f)


def command_ack_retry():
    """До вставки proj-minimal-gcs: команда — це обмін, а не виклик."""
    f = []
    gx, bx = 190, 800
    hb, _, _ = textbox(gx, 62, "Станція", size=14, bold=True, min_w=180)
    hv, _, _ = textbox(bx, 62, "Борт", size=14, bold=True, min_w=180)
    f += [hb, hv]
    f.append(line(gx, 92, gx, 470, color=MUTED, dash="5 5"))
    f.append(line(bx, 92, bx, 470, color=MUTED, dash="5 5"))

    # ── спроба 1: загублена ────────────────────────────────────────────────
    f.append(text(495, 132, "COMMAND_LONG   confirmation = 0", size=13, color=NEG))
    f.append(arrow(gx + 14, 152, 520, 152, color=NEG))
    f.append(line(508, 140, 532, 164, color=POS, sw=2.4))
    f.append(line(532, 140, 508, 164, color=POS, sw=2.4))
    f.append(text(575, 157, "датаграма зникла", size=12, color=POS, anchor="start"))

    # ── таймаут ────────────────────────────────────────────────────────────
    f.append(line(gx, 190, gx, 240, color=MUTED, sw=3))
    f.append(text(gx - 22, 220, "таймаут 1 с", size=12, color=MUTED, anchor="end"))

    # ── спроба 2: дійшла ───────────────────────────────────────────────────
    f.append(text(495, 278, "COMMAND_LONG   confirmation = 1", size=13, color=NEG))
    f.append(arrow(gx + 14, 298, bx - 14, 298, color=NEG))
    f.append(text(575, 322, "той самий вміст, інший лічильник повторів",
                  size=12, color=MUTED, anchor="middle"))

    # ── підтвердження ──────────────────────────────────────────────────────
    f.append(text(495, 380, "COMMAND_ACK   result = MAV_RESULT_ACCEPTED",
                  size=13, color=FIELD))
    f.append(arrow(bx - 14, 400, gx + 14, 400, color=FIELD))

    f.append(text(495, 446, "лише тепер команда вважається виконаною",
                  size=13, color=INK))

    render(os.path.join(OUT, 'command-ack-retry.svg'), 990, 490, *f)


def sixty_lines_grow():
    """До вставки proj-minimal-gcs: що саме доростає з мінімального циклу."""
    f = []
    f.append(text(190, 58, "Шістдесят рядків", size=15, bold=True))
    f.append(text(610, 58, "що це ламає", size=15, bold=True))
    f.append(text(1040, 58, "Станція", size=15, bold=True))

    rows = [
        ("один сокет,\nвідкритий назавжди",
         "канал рветься, а пакети губляться\nмовчки — ніхто про це не скаже",
         "облік каналів із перепідключенням\nі лічильник втрат за полем seq"),
        ("розбір на каналі\nMAVLINK_COMM_0",
         "в ефірі кілька апаратів, камер\nі ще одна станція",
         "свій канал розбору на кожен лінк,\nмаршрутизація за sysid і compid"),
        ("switch по чотирьох\nномерах повідомлень",
         "параметри й місія — не повідомлення,\nа домовлені обміни з підтвердженням",
         "кеш параметрів зі звіркою\nй узгодження місії з перезапитами"),
        ("друк рядка\nв консоль",
         "людина мислить місцевістю,\nа не парою чисел",
         "модель апарата, а з неї —\nкарта, прилади, журнали"),
        ("читання блокує\nєдиний цикл",
         "вікно не сміє завмерти\nні на десяту частку секунди",
         "окремий потік каналу\nй черга до інтерфейсу"),
    ]
    for i, (lft, mid, rgt) in enumerate(rows):
        cy = 130 + i * 100
        f.append(fitbox(40, cy - 36, 300, 72, lft, size=13))
        f.append(fitbox(400, cy - 36, 420, 72, mid, size=12, fill="#ffffff", stroke=MUTED))
        f.append(fitbox(880, cy - 36, 320, 72, rgt, size=13))
        f.append(arrow(344, cy, 394, cy, color=MUTED))
        f.append(arrow(824, cy, 874, cy, color=MUTED))

    render(os.path.join(OUT, 'sixty-lines-grow.svg'), 1240, 610, *f)


def qgc_lineage():
    """До вставки hist-qgc-birth: родовід застосунку від студентського проєкту."""
    f = []
    ax = 250
    f.append(line(60, ax, 1250, ax, color=MUTED, sw=2))
    events = [
        (150, "2008", 1, "ETH Zürich: студентський\nPIXHAWK, політ на камерах"),
        (350, "2009", -1, "EMAV у Делфті — 1-ше місце.\nМова MAVLink, перший QGC"),
        (550, "2011", 1, "Архітектуру викинуто,\nнароджується PX4"),
        (750, "2014", -1, "Dronecode: дім проєкту\nпід Linux Foundation"),
        (950, "2016", 1, "QGC 3.0 — інтерфейс\nпереписано під планшет"),
        (1150, "2026", -1, "QGC 5.0 — та сама роль,\nінша реалізація"),
    ]
    for cx, year, side, s in events:
        cy = ax - 100 if side > 0 else ax + 100
        b, _, h = textbox(cx, cy, s, size=12)
        f.append(b)
        edge = cy + h / 2 if side > 0 else cy - h / 2
        f.append(line(cx, edge, cx, ax, color=MUTED, dash="4 4"))
        f.append(circle(cx, ax, 7, fill=BG, stroke=LINE))
        f.append(text(cx, ax + 28 if side > 0 else ax - 18, year, size=14, bold=True))

    render(os.path.join(OUT, 'qgc-lineage.svg'), 1310, 440, *f)


two_loops()
five_jobs()
mirror_authority()
one_code_many_faces()
command_ack_retry()
sixty_lines_grow()
qgc_lineage()
print("ok")
