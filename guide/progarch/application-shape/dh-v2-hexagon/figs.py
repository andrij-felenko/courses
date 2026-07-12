# -*- coding: utf-8 -*-
"""Фігури до кроку «DH v2: застосунок набуває форми»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_second_door():
    """Двоє дверей (автономний цикл + зовнішній запит) сходяться в один
    застосунковий сервіс, а він тягнеться вниз до драйвованих портів."""
    W, H = 940, 500
    frags = []

    frags.append(text(W / 2, 52,
                      "згори гукають (драйвери) · знизу застосунок тягнеться (драйвовані порти)",
                      size=12, color=MUTED))

    # ── драйвери: двоє дверей ──
    src_y = 108
    bL, wL, hL = textbox(240, src_y, "Автономний цикл\n(гріє сам собою)", size=13, fill="#eaf0fd")
    bR, wR, hR = textbox(695, src_y, "Запит ззовні\n(CLI, згодом HTTP)", size=13, fill="#eaf0fd")

    # ── місце зустрічі: застосунковий сервіс ──
    svc_y = 250
    bS, wS, hS = textbox(468, svc_y,
                         "Застосунковий сервіс — HubService\ntick() · add() · state() · set_threshold()",
                         size=13, fill="#eafaf0", stroke=FIELD, sw=2.0)
    svc_top, svc_bot = svc_y - hS / 2, svc_y + hS / 2

    # ── драйвовані порти ──
    prt_y = 410
    bP1, wP1, hP1 = textbox(215, prt_y, "Sensor", size=13)
    bP2, wP2, hP2 = textbox(400, prt_y, "Heater", size=13)
    bP3, wP3, hP3 = textbox(680, prt_y, "DeviceRepository", size=13, fill="#eef2f6")

    # стрілки: двері → сервіс
    frags.append(arrow(240, src_y + hL / 2, 410, svc_top - 4, color=NEG, sw=2.2))
    frags.append(arrow(695, src_y + hR / 2, 526, svc_top - 4, color=NEG, sw=2.2))
    # стрілки: сервіс → порти
    frags.append(arrow(410, svc_bot, 215, prt_y - hP1 / 2 - 4, color=FIELD, sw=2.2))
    frags.append(arrow(468, svc_bot, 400, prt_y - hP2 / 2 - 4, color=FIELD, sw=2.2))
    frags.append(arrow(526, svc_bot, 680, prt_y - hP3 / 2 - 4, color=FIELD, sw=2.2))

    frags.append(text(W / 2, 462,
                      "логіка не в дверях і не в портах — вона в одному сервісі, який обидві двері гукають",
                      size=12, color=MUTED))
    frags += [bL, bR, bS, bP1, bP2, bP3]
    render(os.path.join(IMG, "second-door.svg"), W, H, *frags,
           title="Двоє дверей сходяться в один застосунковий сервіс")


def fig_onion():
    """Три вкладені кільця (ядро / застосунок / адаптери) і правило залежностей —
    стрілки лише всередину."""
    W, H = 960, 580
    frags = []

    # три вкладені кільця (зовнішнє → внутрішнє)
    frags.append(rect(80, 66, 800, 452, fill="#f4f6f8", stroke=LINE, sw=1.6))    # адаптери
    frags.append(rect(220, 150, 520, 284, fill="#eef7f0", stroke=LINE, sw=1.6))  # застосунок
    frags.append(rect(340, 250, 280, 112, fill="#eafaf0", stroke=FIELD, sw=2.0)) # ядро

    # адаптери — верхня й нижня смуги зовнішнього кільця
    frags.append(text(W / 2, 96, "АДАПТЕРИ", size=14, bold=True, color=MUTED))
    frags.append(text(W / 2, 124, "драйвери (гукають): автономний цикл · CLI · HTTP", size=12))
    frags.append(text(W / 2, 462,
                      "драйвовані адаптери: справжній давач · розетка · репозиторій",
                      size=12))
    frags.append(text(W / 2, 486, "(і підробки для тестів — у той самий отвір)", size=11, color=MUTED))

    # застосунок — верхня смуга середнього кільця
    frags.append(text(W / 2, 178, "ЗАСТОСУНОК — сценарії", size=13, bold=True, color=MUTED))
    frags.append(text(W / 2, 206, "HubService: tick · add · state · set_threshold", size=12))

    # порти — нижня смуга середнього кільця (на межі застосунок ↔ адаптери)
    frags.append(text(W / 2, 408, "порти (драйвовані): Sensor · Heater · DeviceRepository",
                      size=12, color=NEG))

    # ядро
    frags.append(text(W / 2, 284, "ЯДРО ДОМЕНУ", size=13, bold=True, color=FIELD))
    frags.append(text(W / 2, 310, "Device · decide() · Config", size=12))
    frags.append(text(W / 2, 334, "чисте, без вводу-виводу", size=11, color=MUTED))

    # правило залежностей — дві короткі стрілки всередину, у порожніх бокових смугах
    frags.append(arrow(104, 306, 332, 306, color=POS, sw=2.4))
    frags.append(arrow(856, 306, 628, 306, color=POS, sw=2.4))

    frags.append(text(W / 2, 548,
                      "стрілки залежності — лише всередину: зовнішнє кільце знає внутрішнє, не навпаки",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "onion.svg"), W, H, *frags,
           title="Ядро, застосунок, адаптери — і правило залежностей")


def fig_one_truth():
    """Одна правда на двоє (завтра троє) дверей: усі гукають ТОЙ САМИЙ hub,
    тож що записала одна, наступний тік іншої вже бачить."""
    W, H = 980, 560
    frags = []

    # ── центр: єдиний стан застосунку ──
    cx, cy = 490, 300
    bw, bh = 300, 150
    bx, by = cx - bw / 2, cy - bh / 2
    frags.append(rect(bx, by, bw, bh, fill="#eafaf0", stroke=FIELD, sw=2.2))
    frags.append(text(cx, by + 30, "HubService — одна правда", size=14, bold=True, color=FIELD))
    frags.append(text(cx, by + 62, "heating = True", size=13))
    frags.append(text(cx, by + 88, "cfg.threshold = 25", size=13))
    frags.append(text(cx, by + 114, "devices = [ lock@спальня ]", size=13))

    # ── двері 1: автономний цикл (пише heating) ──
    b1, w1, h1 = textbox(165, 110, "Двері 1\nАвтономний цикл", size=13, fill="#eaf0fd")
    frags.append(arrow(165, 110 + h1 / 2, bx + 20, by - 4, color=NEG, sw=2.2))
    frags.append(text(130, 250, "tick(): пише heating,", size=12, color=NEG, anchor="start"))
    frags.append(text(130, 268, "читає cfg + давач", size=12, color=NEG, anchor="start"))

    # ── двері 2: CLI (пише cfg) ──
    b2, w2, h2 = textbox(815, 110, "Двері 2\nCLI", size=13, fill="#eaf0fd")
    frags.append(arrow(815, 110 + h2 / 2, bx + bw - 20, by - 4, color=NEG, sw=2.2))
    frags.append(text(850, 250, "set-threshold 25:", size=12, color=NEG, anchor="end"))
    frags.append(text(850, 268, "пише cfg", size=12, color=NEG, anchor="end"))

    # ── двері 3: HTTP, завтра (лише читає) ──
    b3, w3, h3 = textbox(490, 500, "Двері 3 — HTTP (завтра)", size=13, fill="#f2f2f2", stroke=MUTED)
    frags.append(arrow(490, 500 - h3 / 2, cx, by + bh + 4, color=MUTED, sw=2.0))
    frags.append(text(510, 452, "GET /state: лише читає — нуль правок ядра", size=12,
                      color=MUTED, anchor="start"))

    frags += [b1, b2, b3]
    frags.append(text(W / 2, 542,
                      "що записала одна двер, наступне читання іншої вже бачить — бо hub один",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "one-truth.svg"), W, H, *frags,
           title="Двоє дверей ділять один стан")


def fig_concurrency():
    """Часова вісь: daemon-цикл цокає у фоні, а CLI-подія між тіками
    міняє поріг — і наступний тік уже з новим порогом."""
    W, H = 980, 430
    frags = []

    x0, x1 = 150, 900
    def X(t):                       # t секунд (0..90) → піксель
        return x0 + t * (x1 - x0) / 90.0

    loop_y, cli_y = 150, 300

    # ── смуга циклу (фоновий daemon-потік) ──
    frags.append(text(x0 - 12, loop_y - 58, "фоновий потік (daemon):", size=12,
                      color=MUTED, anchor="start"))
    frags.append(text(x0 - 12, loop_y - 40, "run_loop — тік кожні 30 с", size=12,
                      color=NEG, anchor="start"))
    frags.append(line(x0, loop_y, x1, loop_y, color=NEG, sw=2.0))

    ticks = [(0, "поріг 20"), (30, "поріг 20"), (60, "поріг 25  ✓"), (90, "поріг 25")]
    for t, lbl in ticks:
        x = X(t)
        frags.append(circle(x, loop_y, 6, fill=NEG, stroke=NEG, sw=1))
        frags.append(text(x, loop_y - 16, "tick", size=12, bold=True))
        frags.append(text(x, loop_y + 26, lbl, size=12, color=MUTED))
        frags.append(text(x, loop_y + 46, "%ds" % t, size=11, color=MUTED))

    # ── смуга CLI (головний потік, блокується на вводі) ──
    frags.append(text(x0 - 12, cli_y + 52, "головний потік: run_cli блокується на stdin,", size=12,
                      color=MUTED, anchor="start"))
    frags.append(text(x0 - 12, cli_y + 70, "прокидається на команду", size=12,
                      color=MUTED, anchor="start"))
    frags.append(line(x0, cli_y, x1, cli_y, color=LINE, sw=1.4, dash="4,4"))

    ev_x = X(42)
    frags.append(circle(ev_x, cli_y, 6, fill=POS, stroke=POS, sw=1))
    frags.append(text(ev_x, cli_y + 24, "CLI: set-threshold 25", size=12, bold=True, color=POS))
    frags.append(text(ev_x, cli_y - 14, "42s", size=11, color=MUTED))

    # ── звʼязок: подія CLI → наступний тік уже з 25 ──
    # ціль трохи лівіше самого тіка, щоб лінія не пірнала під його підпис
    frags.append(arrow(ev_x, cli_y - 12, X(60) - 42, loop_y + 14, color=POS, sw=1.8))
    frags.append(text(X(60) + 14, loop_y + 70,
                      "наступний тік уже бачить поріг 25 — стан спільний", size=12,
                      color=POS, anchor="start"))

    render(os.path.join(IMG, "concurrency.svg"), W, H, *frags,
           title="Цикл цокає у фоні, CLI міняє правду між тіками")


def fig_three_names_timeline():
    """Спільний корінь → три перевідкриття (2005 / 2008 / 2012–17) → один інваріант.
    Для вставки hist-three-names-one-shape."""
    W, H = 1040, 620
    frags = []

    # ── спільний корінь (угорі) ──
    root, rw, rh = textbox(
        520, 92,
        "СПІЛЬНИЙ КОРІНЬ: класична шарова архітектура + інверсія залежностей (DIP, 1996)\n"
        "ще раніше — Entity · Control · Boundary Івара Якобсона, 1992",
        size=13, fill="#eef2f6", stroke=LINE, sw=1.6)
    root_bot = 92 + rh / 2

    # ── три перевідкриття (посередині), усі по 3 рядки → однакова висота ──
    cy = 322
    cA, wA, hA = textbox(232, cy, "Ports & Adapters\n(гексагон)\nАлістер Кокберн · 2005",
                         size=13, fill="#eaf0fd")
    cB, wB, hB = textbox(520, cy, "Onion Architecture\nДжеффрі Палермо\n2008",
                         size=13, fill="#eaf0fd")
    cC, wC, hC = textbox(822, cy, "Clean Architecture\nРоберт Мартин\nблог 2012 · книга 2017",
                         size=13, fill="#eaf0fd")
    card_top, card_bot = cy - hA / 2, cy + hA / 2

    # ── банер-інваріант (унизу) ──
    ban, bw, bh = textbox(
        520, 548,
        "ОДИН ІНВАРІАНТ\n"
        "залежності — лише всередину, до чистого ядра · ввід-вивід — на краях, в адаптерах",
        size=14, fill="#eafaf0", stroke=FIELD, sw=2.0)
    ban_top = 548 - bh / 2

    # стрілки: корінь → три картки
    for cx in (232, 520, 822):
        frags.append(arrow(520, root_bot, cx, card_top - 4, color=MUTED, sw=1.8))
    # стрілки: три картки → банер (конвергують до центру)
    frags.append(arrow(232, card_bot, 405, ban_top - 4, color=FIELD, sw=2.2))
    frags.append(arrow(520, card_bot, 520, ban_top - 4, color=FIELD, sw=2.2))
    frags.append(arrow(822, card_bot, 635, ban_top - 4, color=FIELD, sw=2.2))

    frags += [root, cA, cB, cC, ban]
    render(os.path.join(IMG, "three-names-timeline.svg"), W, H, *frags,
           title="Одну форму відкрили тричі — під трьома іменами")


def fig_vocab_mapping():
    """Росетта: терміни трьох шкіл на ті самі три кільця. Для вставки hist."""
    W, H = 1040, 402
    frags = []

    cols = [(40, 172), (224, 252), (488, 252), (752, 252)]  # (x, w): мітка + 3 школи

    # заголовки колонок-шкіл
    hy, hh = 56, 48
    heads = [None, "Ports & Adapters\n(Кокберн)", "Onion\n(Палермо)", "Clean\n(Мартин)"]
    for (x, w), t in zip(cols, heads):
        if t:
            frags.append(fitbox(x, hy, w, hh, t, size=13, bold=True,
                                fill="#eef2f6", stroke=LINE, color=NEG))

    rows = [
        ("Зовні —\nввід-вивід",
         ["адаптери\n(драйвери / драйвовані)", "Infrastructure · UI · Tests", "Frameworks & Drivers"],
         "#f4f6f8"),
        ("Застосунок —\nсценарії",
         ["порти + застосунок", "Application Services", "Use Cases (Interactors)"],
         "#eef7f0"),
        ("Ядро —\nправила домену",
         ["доменне ядро", "Domain Model · Services", "Entities"],
         "#eafaf0"),
    ]
    y0, rh, gap = 116, 76, 8
    for i, (label, cells, fill) in enumerate(rows):
        y = y0 + i * (rh + gap)
        frags.append(fitbox(cols[0][0], y, cols[0][1], rh, label, size=12, bold=True,
                            fill="#ffffff", stroke=LINE, color=MUTED))
        for j, cell in enumerate(cells):
            x, w = cols[j + 1]
            frags.append(fitbox(x, y, w, rh, cell, size=12, fill=fill))

    frags.append(text(W / 2, 388,
                      "те саме кільце — інше слово: три словники описують один крій",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "vocab-mapping.svg"), W, H, *frags,
           title="Три імені — один крій")


if __name__ == "__main__":
    fig_second_door()
    fig_onion()
    fig_one_truth()
    fig_concurrency()
    fig_three_names_timeline()
    fig_vocab_mapping()
    print("OK: second-door.svg, onion.svg, one-truth.svg, concurrency.svg, "
          "three-names-timeline.svg, vocab-mapping.svg")
