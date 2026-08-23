# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір черги задач» (jobs-choice)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_dh_jobs_spread():
    """Три субстрати з минулого кроку, тепер заповнені реальними класами роботи
    DH. Класи розсипаються по всій осі — але більшість осідає в базі-дефолті."""
    W, H = 1420, 600
    frags = []

    cols = [
        (250,  "#eef2fb", MUTED, "У памʼяті\nвтратне",
         ["прогріти кеш стану дому", "мʼяка метрика"],
         ["гине на рестарті —", "і хай гине"]),
        (710,  "#eafaf0", FIELD, "У базі — ДЕФОЛТ\nатомарно із записом",
         ["перекодувати кліп", "сповістити родину", "місячний звіт (cron кладе)"],
         ["народжене з запису чи розкладу;", "атомарність і довговічність задарма"]),
        (1170, "#fff4e6", MUTED, "Окрема інфра\nпереріс базу",
         ["викатка прошивки на флот", "сира телеметрія пристроїв"],
         ["фан-аут і потік-шланг · throttle+DLQ;", "корінець у базі через outbox"]),
    ]

    card_fill = {250: "#eef2fb", 710: "#eafaf0", 1170: "#fff4e6"}
    for cx, hfill, hstroke, htitle, cards, foot in cols:
        b, _, _ = textbox(cx, 92, htitle, size=13.5, fill=hfill, stroke=hstroke,
                          bold=True, min_w=300)
        frags.append(b)
        y = 190
        for c in cards:
            b, _, _ = textbox(cx, y, c, size=12.5, fill=card_fill[cx],
                              stroke=LINE, sw=1.2, min_w=290)
            frags.append(b)
            y += 76
        frags.append(mtext(cx, 470, foot, size=11.5, color=MUTED, lh=1.3))

    frags.append(line(120, 512, 1300, 512, color=LINE, sw=1, dash="4,6"))
    frags.append(text(W / 2, 548, "класи розсипались по всіх трьох субстратах — "
                                  "але більшість осіла в базі-дефолті", size=13.5,
                      color=INK, bold=True))

    render(os.path.join(IMG, "dh-jobs-spread.svg"), W, H, *frags,
           title="Класи фонової роботи DH, розкладені по субстратах")


def fig_enqueue_seam():
    """Композиція постановки задач DH за одним швом enqueue: cron і бізнес-записи
    кладуть роботу через шов, за ним — три субстрати за класом, outbox-корінець у
    базі для брокерного класу. Субстрат схований → карту можна перемальовувати."""
    W, H = 1380, 600
    frags = []

    # ── джерела ліворуч ──
    b, _, _ = textbox(175, 200, "cron\nза розкладом", size=12.5, fill="#eef2fb",
                      stroke=NEG, min_w=200)
    frags.append(b)
    b, _, _ = textbox(175, 380, "запис у базі\n(бізнес-факт)", size=12.5, fill="#eef2fb",
                      stroke=NEG, min_w=200)
    frags.append(b)

    # ── шов у центрі ──
    b, sw_w, sw_h = textbox(475, 290, "enqueue(job)\nодин шов постановки", size=13.5,
                            fill="#f4f6f8", stroke=INK, sw=2.4, bold=True, min_w=260)
    frags.append(b)
    frags.append(arrow(278, 205, 342, 270, color=LINE, sw=1.8))
    frags.append(arrow(278, 375, 342, 312, color=LINE, sw=1.8))

    # ── три субстрати праворуч ──
    subs = [
        (150, "#eef2fb", MUTED, "памʼять\nвтратне"),
        (300, "#eafaf0", FIELD, "черга в базі · ДЕФОЛТ"),
        (470, "#fff4e6", MUTED, "брокер\nпереріс базу"),
    ]
    sub_cx = 855
    for cy, fill, stroke, label in subs:
        b, _, _ = textbox(sub_cx, cy, label, size=12.5, fill=fill, stroke=stroke,
                          sw=2 if stroke == FIELD else 1.5, bold=(stroke == FIELD),
                          min_w=250)
        frags.append(b)
        # шов → субстрат
        frags.append(arrow(608, 290, 725, cy, color=LINE, sw=1.7))
        # субстрат → воркери
        frags.append(arrow(985, cy, 1075, cy, color=MUTED, sw=1.6))
        b, _, _ = textbox(1150, cy, "воркери", size=11.5, fill=FILL, stroke=MUTED,
                          min_w=120)
        frags.append(b)

    # ── outbox-місток між базою та брокером ──
    b, _, _ = textbox(sub_cx, 385, "outbox: корінець у базі →\nrelay несе в брокер",
                      size=11.5, fill="#eafaf0", stroke=FIELD, min_w=260)
    frags.append(b)
    frags.append(line(sub_cx, 322, sub_cx, 360, color=FIELD, sw=1.6, dash="4,4"))
    frags.append(line(sub_cx, 410, sub_cx, 446, color=FIELD, sw=1.6, dash="4,4"))

    frags.append(line(90, 522, 1290, 522, color=LINE, sw=1, dash="4,6"))
    frags.append(text(W / 2, 560, "один шов — кілька субстратів позаду; субстрат класу "
                                  "міняється, не чіпаючи тих, хто кличе enqueue",
                      size=13, color=INK, bold=True))

    render(os.path.join(IMG, "enqueue-seam.svg"), W, H, *frags,
           title="Постановка задач DH за одним швом enqueue")


def fig_outbox_bridge():
    """Outbox-міст класу «викатка на флот»: корінець-кампанія й рядок outbox лягають
    ОДНІЄЮ транзакцією (атомарно з базою), а окремий relay уже читає закомічені рядки
    й розсіює лавину per-device задач у брокер — після commit, а не в транзакції."""
    W, H = 1460, 660
    frags = []

    # ── контейнер «одна транзакція» з двома записами всередині ──
    tx_x, tx_y, tx_w, tx_h = 70, 100, 390, 250
    frags.append(rect(tx_x, tx_y, tx_w, tx_h, fill="#eafaf0", stroke=FIELD, sw=2.4, rx=14))
    frags.append(text(tx_x + tx_w / 2, tx_y + 30, "ОДНА ТРАНЗАКЦІЯ", size=14, color=FIELD, bold=True))
    cx_tx = tx_x + tx_w / 2
    b, _, _ = textbox(cx_tx, tx_y + 88, "campaigns\nкорінець кампанії", size=12.5,
                      fill=FILL, stroke=LINE, min_w=310)
    frags.append(b)
    b, _, _ = textbox(cx_tx, tx_y + 178, "outbox\nрядок фан-ауту (sent=false)", size=12.5,
                      fill=FILL, stroke=LINE, min_w=310)
    frags.append(b)
    frags.append(mtext(cx_tx, tx_y + tx_h + 38, ["COMMIT — обидва разом;", "ROLLBACK — жодного"],
                       size=12, color=INK, bold=True, lh=1.35))

    # ── relay: окремий процес ──
    b, rw, _ = textbox(660, 205, "relay\nокремий процес", size=12.5, fill="#eef2fb",
                       stroke=NEG, sw=2, bold=True, min_w=230)
    frags.append(b)
    frags.append(mtext(660, 285, ["читає ЗАКОМІЧЕНІ", "невислані рядки,", "мітить sent=true"],
                       size=11, color=MUTED, lh=1.3))
    frags.append(arrow(tx_x + tx_w, 205, 660 - rw / 2 - 8, 205, color=LINE, sw=2))

    # ── брокер ──
    b, bw, _ = textbox(950, 205, "брокер\nтема fleetRollout", size=12.5, fill="#fff4e6",
                       stroke=MUTED, sw=1.8, min_w=230)
    frags.append(b)
    frags.append(arrow(660 + rw / 2 + 8, 205, 950 - bw / 2 - 8, 205, color=LINE, sw=2))

    # ── лавина per-device задач у праву колонку ──
    devices = ["dev-1", "dev-2", "dev-3", "dev-4", "dev-5"]
    wy0, wstep, wx = 110, 82, 1310
    for i, d in enumerate(devices):
        wy = wy0 + i * wstep
        b, ww, _ = textbox(wx, wy, d, size=11.5, fill=FILL, stroke=MUTED, min_w=150)
        frags.append(b)
        frags.append(arrow(950 + bw / 2 + 8, 205, wx - ww / 2 - 8, wy, color=MUTED, sw=1.5))
    frags.append(mtext(wx, wy0 + 5 * wstep + 4, ["один outbox-рядок →", "задача на КОЖЕН пристрій"],
                       size=11, color=MUTED, lh=1.3))

    frags.append(line(70, 585, 1390, 585, color=LINE, sw=1, dash="4,6"))
    frags.append(text(W / 2, 622, "корінець атомарний у базі · лавину несе брокер ПІСЛЯ commit — "
                                  "не гаряча таблиця jobs", size=13, color=INK, bold=True))

    render(os.path.join(IMG, "outbox-bridge.svg"), W, H, *frags,
           title="Outbox-міст: атомарний корінець у базі → relay розсіює лавину в брокер")


def fig_queue_history_timeline():
    """Історія-вставка hist-per-class-queues: еволюція черг задач від однієї
    недиференційованої купи до ізоляції за класом і назад до бази. П'ять віх;
    під ними росте вісь ізоляції, а між віхами — біль, що штовхала вперед."""
    W, H = 1720, 560
    frags = []

    HALF = 125  # min_w=250 → усі картки рівно 250 завширшки
    # (cx, рік, система, автор·орг, внесок, заливка, обвід, база?)
    cards = [
        (200,  "2008", "delayed_job", "Лютке · Shopify",
         "одна таблиця, один пул", "#eafaf0", FIELD, True),
        (530,  "2009", "Resque", "Ванстрат · GitHub",
         "іменовані черги + пріоритет", "#eef2fb", NEG, False),
        (860,  "2012", "Sidekiq", "Перхем",
         "ваги: клас не голодує", "#eef2fb", NEG, False),
        (1190, "2021", "GitLab", "Міскелл",
         "шарди за класом і терміновістю", "#fff4e6", MUTED, False),
        (1520, "2023", "Solid Queue", "Гутьєррес · 37signals",
         "знову база, з класами", "#eafaf0", FIELD, True),
    ]

    # ── рік (жирна шапка) + картка віхи ──
    for cx, year, sysn, who, gain, fill, stroke, is_db in cards:
        frags.append(text(cx, 108, year, size=15, color=stroke, bold=True))
        b, _, _ = textbox(cx, 175, "%s\n%s\n%s" % (sysn, who, gain), size=12.5,
                          fill=fill, stroke=stroke, sw=2.4 if is_db else 1.6,
                          bold=is_db, min_w=250)
        frags.append(b)

    # ── стрілки поступу між віхами ──
    for i in range(len(cards) - 1):
        x1 = cards[i][0] + HALF + 6
        x2 = cards[i + 1][0] - HALF - 6
        frags.append(arrow(x1, 175, x2, 175, color=LINE, sw=1.8))

    # ── біль, що штовхала від віхи до віхи (червоним, на серединах) ──
    pains = [
        (365,  "один пул блокує голову"),
        (695,  "строгий порядок → голодує"),
        (1025, "за іменем → Redis тоне"),
        (1355, "складно на Redis + гемах"),
    ]
    for mx, p in pains:
        frags.append(text(mx, 252, p, size=10.5, color=POS, italic=True))

    # ── вісь ізоляції + краплі-опускання від кожної віхи ──
    for cx, *_ in cards:
        frags.append(line(cx, 212, cx, 424, color=MUTED, sw=1, dash="3,5"))
        frags.append(circle(cx, 430, 4, fill=FIELD, stroke=FIELD))
    frags.append(arrow(120, 430, 1610, 430, color=FIELD, sw=2.2))
    frags.append(text(210, 458, "одна недиференційована купа", size=11.5, color=MUTED))
    frags.append(text(1500, 458, "ізоляція за КЛАСОМ роботи", size=11.5,
                      color=FIELD, bold=True))

    frags.append(text(W / 2, 508, "кожен перехід штовхала біль попередньої віхи — "
                                  "а наприкінці коло вертається до бази", size=13,
                      color=INK, bold=True))

    render(os.path.join(IMG, "queue-history-timeline.svg"), W, H, *frags,
           title="Від однієї купи до ізоляції за класом — і назад до бази")


if __name__ == "__main__":
    fig_dh_jobs_spread()
    fig_enqueue_seam()
    fig_outbox_bridge()
    fig_queue_history_timeline()
    print("OK: dh-jobs-spread.svg, enqueue-seam.svg, outbox-bridge.svg, "
          "queue-history-timeline.svg")
