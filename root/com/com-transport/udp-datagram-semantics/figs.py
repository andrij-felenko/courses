# -*- coding: utf-8 -*-
"""Фігури до теми «Семантика датаграми UDP: втрати, дублі, переставляння»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def xmark(cx, cy, r=13, color=POS, sw=3.2):
    return (line(cx - r, cy - r, cx + r, cy + r, color=color, sw=sw) +
            line(cx - r, cy + r, cx + r, cy - r, color=color, sw=sw))


# ── 1. Що послали і що отримали ────────────────────────────────────────────
def fig_anomalies():
    W, H = 1000, 440
    sent_y, recv_y = 100, 300
    xs = [190, 305, 420, 535, 650, 765, 880]
    frags = []

    frags.append(text(85, sent_y + 5, "надіслано", size=13, color=MUTED))
    frags.append(text(85, recv_y + 5, "отримано", size=13, color=MUTED))

    for i, x in enumerate(xs):
        body, w, h = textbox(x, sent_y, str(i + 1), size=15, min_w=56, bold=True)
        frags.append(body)

    recv_labels = ["1", "3", "2", "3", "6", "7"]
    rxs = xs[:6]
    for x, lab in zip(rxs, recv_labels):
        body, w, h = textbox(x, recv_y, lab, size=15, min_w=56, bold=True)
        frags.append(body)

    top, bot = sent_y + 18, recv_y - 18
    # 1 → 1
    frags.append(arrow(xs[0], top, rxs[0], bot))
    # 2 → третя позиція
    frags.append(arrow(xs[1], top, rxs[2], bot))
    # 3 → друга позиція (обігнала) і ще раз четверта (дубль)
    frags.append(arrow(xs[2], top, rxs[1], bot))
    frags.append(arrow(xs[2], top, rxs[3], bot, color=POS))
    # 4, 5 — зникли
    for i in (3, 4):
        frags.append(line(xs[i], top, xs[i], 186, color=MUTED, dash="6 5"))
        frags.append(xmark(xs[i], 202))
    # 6, 7
    frags.append(arrow(xs[5], top, rxs[4], bot))
    frags.append(arrow(xs[6], top, rxs[5], bot))

    notes = [
        (30, "1 і 7 дійшли\nтак, як були послані"),
        (275, "2 і 3 помінялись\nмісцями — переставляння"),
        (520, "3 прийшла двічі —\nдубль"),
        (765, "4 і 5 не дійшли —\nвтрата"),
    ]
    for x, s in notes:
        frags.append(fitbox(x, 356, 205, 56, s, size=12, color=MUTED))

    return render(os.path.join(OUT, 'udp-anomalies.svg'), W, H, *frags,
                  title="Що відправник послав і що приймач побачив")


# ── 2. Де саме зникає датаграма ────────────────────────────────────────────
def fig_loss_points():
    W, H = 940, 710
    rows = [
        ("застосунок: sendto()", "повертає число — це «ядро взяло у себе»,\nа не «адресат отримав»"),
        ("черга сокета\n(відправка)", "переповнення: ENOBUFS\nабо тихе відкидання"),
        ("черга мережевого інтерфейсу", "генеруємо швидше,\nніж лінк устигає віддавати"),
        ("лінк: радіо або дріт", "спотворення → кадр не проходить\nперевірку → відкинуто"),
        ("черга маршрутизатора\nна вузькому місці", "черга скінченна: повна —\nнові пакети за борт"),
        ("фаєрвол і NAT", "немає дозволу чи запису трансляції —\nковтає мовчки"),
        ("черга сокета\n(прийом)", "застосунок читає повільніше,\nніж надходить"),
        ("застосунок: recvfrom()", "замалий буфер — хвіст датаграми\nвідрізано назавжди"),
    ]
    frags = []
    y0, step, bh = 66, 78, 54
    for i, (left, right) in enumerate(rows):
        y = y0 + i * step
        frags.append(fitbox(50, y, 330, bh, left, size=13, bold=True))
        frags.append(fitbox(430, y, 460, bh, right, size=12, color=MUTED))
        if i + 1 < len(rows):
            frags.append(arrow(215, y + bh, 215, y + step - 2))
    return render(os.path.join(OUT, 'loss-points.svg'), W, H, *frags,
                  title="Ланцюг черг на шляху датаграми")


# ── 3. Фрагментація множить утрату ─────────────────────────────────────────
def fig_fragmentation():
    W, H = 900, 500
    frags = []
    frags.append(fitbox(150, 62, 600, 52, "датаграма UDP: 4000 байтів даних", size=15, bold=True))
    frags.append(arrow(450, 114, 450, 158))
    frags.append(text(474, 142, "IP ріже на три фрагменти", size=13, color=MUTED, anchor="start"))

    fx = [135, 355, 575]
    labels = ["фрагмент 1\n1480 Б", "фрагмент 2\n1480 Б", "фрагмент 3\n1048 Б"]
    for x, s in zip(fx, labels):
        frags.append(fitbox(x, 168, 190, 56, s, size=13))

    frags.append(arrow(230, 224, 230, 292))
    frags.append(arrow(670, 224, 670, 292))
    frags.append(line(450, 224, 450, 244, color=MUTED, dash="6 5"))
    frags.append(xmark(450, 260))

    frags.append(fitbox(135, 294, 630, 52, "приймач зібрав два фрагменти з трьох", size=14))
    frags.append(arrow(450, 346, 450, 384))
    frags.append(fitbox(180, 386, 540, 52, "складати нема з чого — уся датаграма втрачена",
                        size=14, stroke=POS, bold=True))
    body, w, h = textbox(450, 468, "1 % утрат на фрагмент  →  2.97 % на датаграму",
                         size=14, color=POS)
    frags.append(body)
    return render(os.path.join(OUT, 'fragmentation-loss.svg'), W, H, *frags,
                  title="Фрагментація: втрата одного шматка нищить усе")


# ── 4. Вікно номерів проти дублів ──────────────────────────────────────────
def fig_replay_window():
    W, H = 1000, 440
    frags = []
    x0, cw, cy0, ch = 150, 44, 180, 52
    bits = [1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1]

    frags.append(text(150, 158, "вікно: 16 останніх номерів", size=13,
                      color=MUTED, anchor="start"))
    frags.append(text(x0 + 16 * cw, 158, "найвищий прийнятий", size=13,
                      color=MUTED, anchor="end"))

    for i, b in enumerate(bits):
        x = x0 + i * cw
        frags.append(rect(x, cy0, cw, ch, fill="#eef3ee" if b else BG, rx=3))
        frags.append(text(x + cw / 2, cy0 + ch / 2 + 6, str(b), size=15,
                          color=FIELD if b else MUTED, bold=True))

    # зони поза вікном
    frags.append(rect(95, cy0, cw, ch, fill="#f0f0f0", stroke=MUTED, sw=1.2, rx=3))
    frags.append(rect(875, cy0, cw, ch, fill="#f0f0f0", stroke=MUTED, sw=1.2, rx=3))

    notes = [
        (20, 205, "номер позаду вікна:\nнадто старий, геть", 117),
        (265, 205, "біт стоїть:\nдубль, геть", 310),
        (520, 205, "біт скинутий:\nзапізніла, беремо", 572),
        (775, 205, "номер більший за всі:\nвікно зсувається", 897),
    ]
    for bx, bw, s, tx in notes:
        frags.append(fitbox(bx, 332, bw, 62, s, size=12, color=MUTED))
        frags.append(arrow(bx + bw / 2, 330, tx, cy0 + ch + 6))

    return render(os.path.join(OUT, 'replay-window.svg'), W, H, *frags,
                  title="Вікно номерів: чотири випадки, які розрізняє приймач")


# ── 5. Один протокол розібрали на три ──────────────────────────────────────
def fig_split_1978():
    W, H = 1020, 560
    frags = []
    frags.append(fitbox(210, 62, 600, 80,
                        "Transmission Control Program (1974–1977)",
                        size=15, bold=True))
    frags.append(text(510, 118, "адресація, маршрут, надійність, порядок, порти — усе в одному",
                      size=12, color=MUTED))
    frags.append(arrow(510, 142, 510, 186))
    frags.append(fitbox(280, 188, 460, 54,
                        "нарада в ISI, Марина-дель-Рей (1977):\nрозділити на шари",
                        size=14, bold=True, stroke=MUTED))

    frags.append(arrow(510, 244, 175, 294))
    frags.append(arrow(510, 244, 510, 294))
    frags.append(arrow(510, 244, 845, 294))

    frags.append(fitbox(45, 298, 260, 92,
                        "IP\nадреса, маршрут,\nдоставка одного пакета", size=14, bold=True))
    frags.append(fitbox(380, 298, 260, 92,
                        "TCP\nз'єднання, повтори,\nпорядок — поверх IP", size=14, bold=True))
    frags.append(fitbox(715, 298, 260, 92,
                        "UDP\nпорти, довжина, сума —\nі нічого більше", size=14, bold=True))

    frags.append(fitbox(35, 416, 280, 100,
                        "спільний низ:\nмережа лише передає,\nнічого не обіцяючи",
                        size=12, color=MUTED))
    frags.append(fitbox(370, 416, 280, 100,
                        "для файлів і пошти:\nповнота важить\nбільше за час",
                        size=12, color=MUTED))
    frags.append(fitbox(705, 416, 280, 100,
                        "для мови, радара, відео:\nчас важить\nбільше за повноту",
                        size=12, color=MUTED))

    return render(os.path.join(OUT, 'udp-split-1978.svg'), W, H, *frags,
                  title="Що з чого вийшло: розділення TCP на шари")


# ── 6. Хронологія документів ───────────────────────────────────────────────
def fig_udp_timeline():
    rows = [
        ("грудень 1973", "NVP, Денні Коен (ISI)",
         "перша пакетна мова поверх ARPANET"),
        ("жовтень 1974", "RFC 660, Дейв Волден (BBN)",
         "«некеровані пакети»: без повторів,\nбез збирання, без порядку"),
        ("15 серпня 1977", "IEN 2, Джон Постел (ISI)",
         "«ми порушуємо принцип шарування» —\nвідділити мережевий шар від TCP"),
        ("1977 (дата спірна)", "нарада в ISI,\nМарина-дель-Рей",
         "рішення розділити TCP і IP;\nтам-таки накреслено UDP"),
        ("22 листопада 1977", "RFC 741, Денні Коен",
         "специфікація NVP: «уникнення\nнаскрізних повторів»"),
        ("січень–лютий 1978", "IEN 21, 26, 27, 28",
         "перші специфікації з розділеними\nзаголовками TCP і IP"),
        ("червень–вересень 1978", "IEN 41 і IEN 55, Постел",
         "окремі специфікації IP v4 і TCP v4"),
        ("21 січня 1979", "IEN 71, Девід Рід (MIT)",
         "перша специфікація\n«User Datagram Protocol»"),
        ("2 травня 1979", "IEN 88, Джон Постел",
         "той самий заголовок, редакція ISI"),
        ("28 серпня 1980", "RFC 768, Джон Постел",
         "чинний стандарт: три сторінки,\nвідтоді без змін"),
    ]
    y0, step, bh = 64, 68, 56
    W = 1040
    H = y0 + (len(rows) - 1) * step + bh + 30
    frags = [line(250, 54, 250, y0 + (len(rows) - 1) * step + bh + 6,
                  color=MUTED, sw=1.4)]
    for i, (date, doc, what) in enumerate(rows):
        y = y0 + i * step
        frags.append(fitbox(40, y, 190, bh, date, size=12, bold=True))
        frags.append(circle(250, y + bh / 2, 6, fill=BG, stroke=MUTED, sw=2))
        frags.append(fitbox(268, y, 300, bh, doc, size=12))
        frags.append(fitbox(590, y, 410, bh, what, size=12, color=MUTED))
    return render(os.path.join(OUT, 'udp-timeline.svg'), W, H, *frags,
                  title="Сім років від пакетної мови до RFC 768")


# ── 7. Утрата датаграми з k фрагментів (до math-вставки) ───────────────────
def fig_loss_vs_k():
    W, H = 1000, 560
    x0, x1 = 130, 780
    ytop, ybot = 90, 450
    PMAX, PM = 0.20, 0.05

    def px(p):
        return x0 + p / PM * (x1 - x0)

    def py(P):
        return ybot - P / PMAX * (ybot - ytop)

    frags = []
    for i in range(5):
        P = i * 0.05
        y = py(P)
        frags.append(line(x0, y, x1, y, color="#dcdfe3", sw=1,
                          dash=None if i == 0 else "5 5"))
        frags.append(text(x0 - 14, y + 5, "0" if i == 0 else "%d %%" % (P * 100),
                          size=12, color=MUTED, anchor="end"))
    for i in range(6):
        p = i * 0.01
        x = px(p)
        frags.append(line(x, ybot, x, ybot + 6, color=MUTED, sw=1.2))
        frags.append(text(x, ybot + 26, "0" if i == 0 else "%d %%" % (p * 100),
                          size=12, color=MUTED))
    frags.append(line(x0, ytop - 12, x0, ybot, color=LINE, sw=1.6))
    frags.append(line(x0, ybot, x1 + 12, ybot, color=LINE, sw=1.6))

    # пряма 4·p — для порівняння з кривою k = 4
    frags.append(line(px(0), py(0), px(PM), py(4 * PM), color=MUTED, sw=1.8, dash="7 6"))

    for k, col in ((1, MUTED), (2, NEG), (3, INK), (4, POS)):
        prev = None
        for i in range(51):
            p = PM * i / 50.0
            cur = (px(p), py(1 - (1 - p) ** k))
            if prev:
                frags.append(line(prev[0], prev[1], cur[0], cur[1], color=col, sw=2.4))
            prev = cur

    lx = x1 + 18
    frags.append(text(lx, 94, "4·p — пряма", size=12, color=MUTED, anchor="start"))
    for k, col in ((4, POS), (3, INK), (2, NEG), (1, MUTED)):
        frags.append(text(lx, py(1 - (1 - PM) ** k) + 5, "k = %d" % k,
                          size=13, color=col, anchor="start", bold=True))

    frags.append(text(x0, ytop - 30, "утрата датаграми P", size=13,
                      color=MUTED, anchor="start"))
    frags.append(text((x0 + x1) / 2, ybot + 60, "утрата одного пакета p",
                      size=13, color=MUTED))

    return render(os.path.join(OUT, 'loss-vs-k.svg'), W, H, *frags,
                  title="Кожен зайвий фрагмент додає майже цілу ймовірність p")


# ── 8. Пачки проти незалежних утрат (до math-вставки) ──────────────────────
def fig_burst_amplification():
    W, H = 1120, 480
    frags = []

    # ліва панель: двостановий канал
    frags.append(text(260, 62, "двостановий канал", size=14, bold=True))
    frags.append(circle(150, 160, 42, fill="#eef5ee", stroke=FIELD, sw=2.2))
    frags.append(text(150, 169, "G", size=24, color=FIELD, bold=True))
    frags.append(circle(390, 160, 42, fill="#fdecea", stroke=POS, sw=2.2))
    frags.append(text(390, 169, "B", size=24, color=POS, bold=True))
    frags.append(arrow(198, 128, 344, 128))
    frags.append(text(271, 116, "g", size=15, bold=True))
    frags.append(arrow(344, 192, 198, 192))
    frags.append(text(271, 214, "r", size=15, bold=True))
    frags.append(fitbox(60, 232, 180, 44, "усе проходить", size=12, color=MUTED))
    frags.append(fitbox(300, 232, 180, 44, "усе гине", size=12, color=MUTED))
    frags.append(fitbox(40, 300, 440, 130,
                        "g = P(G→B) — увійти в пачку\n"
                        "r = P(B→G) — вийти з неї\n"
                        "ε = g / (g + r) — частка втрачених пакетів\n"
                        "L = 1 / r — середня довжина пачки",
                        size=12, color=INK))

    frags.append(line(520, 80, 520, 440, color="#dcdfe3", sw=1.2))

    # права панель: підсилення спадає з довжиною пачки
    frags.append(text(824, 62, "підсилення A = P / ε для k = 3", size=14, bold=True))
    base, top3 = 400, 120
    data = [("1.01", 2.97), ("2", 2.00), ("5", 1.40), ("10", 1.20),
            ("20", 1.10), ("50", 1.04)]
    for i, (lab, a) in enumerate(data):
        x = 600 + i * 80
        h = (base - top3) * a / 3.0
        frags.append(rect(x, base - h, 56, h,
                          fill="#fdecea" if i == 0 else FILL,
                          stroke=POS if i == 0 else LINE, sw=1.6, rx=3))
        frags.append(text(x + 28, base - h - 10, "%.2f" % a, size=12, bold=True))
        frags.append(text(x + 28, base + 24, lab, size=12, color=MUTED))
    frags.append(line(590, base, 1070, base, color=LINE, sw=1.6))
    y1 = base - (base - top3) / 3.0
    frags.append(line(590, y1, 1070, y1, color=MUTED, sw=1.4, dash="6 5"))
    frags.append(text(584, y1 + 4, "A = 1", size=11, color=MUTED, anchor="end"))
    frags.append(text(830, base + 56, "середня довжина пачки, пакетів",
                      size=12, color=MUTED))

    return render(os.path.join(OUT, 'burst-amplification.svg'), W, H, *frags,
                  title="Що довша пачка, то менше коштує зайвий фрагмент")


# ── Зсув вікна: хто виїжджає і що з цього справді втрата ───────────────────
def fig_window_shift():
    W, H = 1020, 470
    cw, ch, gap = 68, 48, 4
    step = cw + gap                 # 72
    x0 = 250                        # ліва межа вікна на екрані
    y1, y2 = 108, 300

    old_nums, old_bits = list(range(503, 513)), [1, 0, 1, 1, 0, 1, 1, 1, 0, 1]
    new_nums, new_bits = list(range(506, 516)), [1, 0, 1, 1, 1, 0, 1, 0, 0, 1]
    gone_nums, gone_bits = [503, 504, 505], [1, 0, 1]

    def cell(x, y, num, b, gone=False):
        if gone:
            fill, stroke, col = ("#eeeeee", MUTED, MUTED) if b else ("#fdecea", POS, POS)
        else:
            fill, stroke, col = (FILL, LINE, INK) if b else (BG, MUTED, MUTED)
        return (text(x + cw / 2.0, y - 12, str(num), size=12, color=MUTED) +
                fitbox(x, y, cw, ch, str(b), size=20, bold=True,
                       fill=fill, stroke=stroke, color=col))

    def frame(y):
        return rect(x0 - 8, y - 8, 10 * step - gap + 16, ch + 16,
                    fill=BG, stroke=FIELD, sw=2, rx=8)

    frags = []

    # верхній рядок — вікно до приходу
    frags.append(text(34, 62, "Було: вікно на 10 позицій, найбільший прийнятий номер — 512",
                      size=14, color=INK, anchor="start", bold=True))
    frags.append(frame(y1))
    for i, (n, b) in enumerate(zip(old_nums, old_bits)):
        frags.append(cell(x0 + i * step, y1, n, b))

    # перехід
    frags.append(arrow(150, 172, 150, 252))
    frags.append(arrow(900, 172, 900, 252))
    body, _, _ = textbox(525, 208,
                         ["різниця = 515 − 512 = 3",
                          "вікно їде на 3 позиції вперед"], size=14, bold=True)
    frags.append(body)

    # нижній рядок — вікно після приходу, з тим, що виїхало
    frags.append(text(34, 258, "Стало: прийшов 515 — три найстаріші позиції вийшли з вікна",
                      size=14, color=INK, anchor="start", bold=True))
    frags.append(frame(y2))
    for i, (n, b) in enumerate(zip(gone_nums, gone_bits)):
        frags.append(cell(x0 - 3 * step + i * step, y2, n, b, gone=True))
    for i, (n, b) in enumerate(zip(new_nums, new_bits)):
        frags.append(cell(x0 + i * step, y2, n, b))

    # підписи під групами
    frags.append(line(140, 352, 140, 366, color=MUTED, sw=1.4))
    body, _, _ = textbox(140, 400,
                         ["виїхали назавжди:", "503 і 505 — бачили",
                          "504 — ні, це втрата"], size=13)
    frags.append(body)

    frags.append(line(860, 352, 860, 366, color=MUTED, sw=1.4))
    body, _, _ = textbox(860, 400,
                         ["увійшли нові:", "513, 514 — ще чекаємо",
                          "515 — щойно прийшов"], size=13)
    frags.append(body)

    return render(os.path.join(OUT, 'window-shift.svg'), W, H, *frags,
                  title="Зсув вікна: втрата підтверджується лише на виїзді")


if __name__ == '__main__':
    print(fig_loss_vs_k())
    print(fig_burst_amplification())
    print(fig_split_1978())
    print(fig_udp_timeline())
    print(fig_anomalies())
    print(fig_loss_points())
    print(fig_fragmentation())
    print(fig_replay_window())
    print(fig_window_shift())
