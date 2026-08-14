# -*- coding: utf-8 -*-
"""Фігури до теми «STP та RSTP».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Проблема петель L2: широкомовний шторм ─────────────────────────────
def fig_loop_problem():
    """Петля між трьома комутаторами без STP. Широкомовний кадр (ARP) циркулює
    нескінченно, оскільки в Ethernet немає TTL. Це викликає шторм трафіку
    та перезапис таблиці MAC (MAC flapping)."""
    W, H = 760, 420
    f = [text(W / 2, 28, "Проблема петлі на канальному рівні (L2) без STP", size=16, bold=True)]

    # Три комутатори в трикутнику
    # Switch A (зверху)
    sw_a, aw, ah = textbox(380, 100, "Комутатор A\nMAC: 00:00:00:00:00:01", size=12, bold=True,
                           fill="#eef3ff", stroke=NEG, min_w=180)
    f.append(sw_a)

    # Switch B (внизу ліворуч)
    sw_b, bw, bh = textbox(240, 270, "Комутатор B\nMAC: 00:00:00:00:00:02", size=12, bold=True,
                           fill="#eef3ff", stroke=NEG, min_w=180)
    f.append(sw_b)

    # Switch C (внизу праворуч)
    sw_c, cw, ch = textbox(560, 270, "Комутатор C\nMAC: 00:00:00:00:00:03", size=12, bold=True,
                           fill="#eef3ff", stroke=NEG, min_w=180)
    f.append(sw_c)

    # Клієнт H1 ліворуч від B (відсунуто подалі, щоб не налазив на Switch B)
    cli, clw, clh = textbox(70, 270, "Вузол H1\n(надсилає ARP)", size=10, fill="#eafaf0", stroke=FIELD)
    f.append(cli)
    f.append(arrow(115, 270, 150, 270, color=FIELD))

    # Лінії між комутаторами з описними стрілками петель
    # Лінія A <-> B
    f.append(line(320, 120, 250, 230, color=POS, sw=2, dash="4,4"))
    # Лінія A <-> C
    f.append(line(440, 120, 510, 230, color=POS, sw=2, dash="4,4"))
    # Лінія B <-> C
    f.append(line(330, 270, 470, 270, color=POS, sw=2, dash="4,4"))

    # Циркулюючі стрілки шторму (червоні)
    f.append(arrow(260, 210, 330, 140, color=POS, sw=2.2))
    f.append(arrow(430, 140, 500, 210, color=POS, sw=2.2))
    f.append(arrow(490, 288, 310, 288, color=POS, sw=2.2))

    # Підписи шторму (відсунуті вбік від ліній)
    f.append(fitbox(150, 150, 110, 36, "Широкомовний\nкадр (ARP)", size=10, fill="#fdecea", stroke=POS))
    f.append(fitbox(610, 150, 110, 36, "Копія кадру\nдублюється", size=10, fill="#fdecea", stroke=POS))
    f.append(fitbox(400, 305, 120, 36, "Зациклення вічне\n(немає TTL у L2)", size=10, fill="#fdecea", stroke=POS))

    # Рамка наслідків внизу
    f.append(rect(60, 350, 640, 55, fill="#fff7e6", stroke=POS, sw=1.2))
    f.append(mtext(380, 366, ["1. Broadcast Storm: 100% завантаження каналів широкомовним трафіком",
                              "2. MAC Table Flapping: постійний перезапис таблиці комутації → перевантаження CPU",
                              "3. Дублювання кадрів: кінцевий отримувач приймає сотні копій того самого пакета"],
                   size=11, color=INK, anchor="middle", lh=1.35))

    render(os.path.join(IMG, "loop-problem.svg"), W, H, *f)


# ── 2. Топологія Spanning Tree (STP 802.1D) ──────────────────────────────────
def fig_stp_topology():
    """Побудова топології без петель за допомогою STP. Вибір Root Bridge,
    кореневих портів (RP), призначених портів (DP) та блокування альтернативного порту (AP)."""
    W, H = 760, 440
    f = [text(W / 2, 28, "Топологія Spanning Tree: ролі портів та розрив петлі", size=16, bold=True)]

    # Root Bridge зверху (найменший BID)
    root, rw, rh = textbox(380, 95, "Root Bridge (Корінь)\nBridge ID: 4096 : 00:01:02:03:04:05\n(Найменший BID у мережі)",
                           size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=240)
    f.append(root)

    # Switch B (нижче ліворуч)
    sw_b, bw, bh = textbox(180, 280, "Switch B\nBID: 32768 : 00:00:00:00:00:02\nPath Cost = 4",
                           size=11, bold=True, fill="#eef3ff", stroke=NEG, min_w=180)
    f.append(sw_b)

    # Switch C (нижче праворуч)
    sw_c, cw, ch = textbox(580, 280, "Switch C\nBID: 32768 : 00:00:00:00:00:03\nPath Cost = 4",
                           size=11, bold=True, fill="#eef3ff", stroke=NEG, min_w=180)
    f.append(sw_c)

    # З'єднання Root <-> B (1 Gbps, Cost = 4)
    f.append(line(310, 130, 220, 240, color=LINE, sw=2))
    f.append(fitbox(245, 175, 65, 22, "Cost = 4", size=10, fill=BG, stroke=MUTED))

    # З'єднання Root <-> C (1 Gbps, Cost = 4)
    f.append(line(450, 130, 540, 240, color=LINE, sw=2))
    f.append(fitbox(515, 175, 65, 22, "Cost = 4", size=10, fill=BG, stroke=MUTED))

    # З'єднання B <-> C (1 Gbps, Cost = 4) — БЛОКОВАНО
    f.append(line(270, 280, 490, 280, color=POS, sw=2, dash="5,5"))
    f.append(fitbox(350, 280, 75, 22, "Cost = 4", size=10, fill=BG, stroke=MUTED))

    # Маркування портів на Root Bridge
    f.append(fitbox(295, 135, 36, 20, "DP", size=10, bold=True, fill="#eafaf0", stroke=FIELD))
    f.append(fitbox(465, 135, 36, 20, "DP", size=10, bold=True, fill="#eafaf0", stroke=FIELD))

    # Маркування портів на Switch B
    f.append(fitbox(215, 230, 36, 20, "RP", size=10, bold=True, fill="#eef3ff", stroke=NEG))
    f.append(fitbox(285, 252, 36, 20, "DP", size=10, bold=True, fill="#eafaf0", stroke=FIELD))

    # Маркування портів на Switch C
    f.append(fitbox(545, 230, 36, 20, "RP", size=10, bold=True, fill="#eef3ff", stroke=NEG))
    f.append(fitbox(420, 252, 55, 20, "AP (BLK)", size=9, bold=True, fill="#fdecea", stroke=POS))

    # Пояснення ролей внизу
    f.append(rect(40, 345, 680, 80, fill=BG, stroke=MUTED, sw=1.2))
    f.append(mtext(380, 362, [
        "• Root Bridge: комутатор із найменшим BID; усі його порти є Designated (DP).",
        "• RP (Root Port): порт комутатора з найкоротшим шляхом (Root Path Cost) до Root Bridge.",
        "• DP (Designated Port): порт, який надсилає найкращий BPDU у свій сегмент мережі.",
        "• AP (Alternate/Blocking Port): порт, який програв вибори і блокує транзитний трафік для усунення петлі."
    ], size=11, color=INK, anchor="middle", lh=1.35))

    render(os.path.join(IMG, "stp-topology.svg"), W, H, *f)


# ── 3. Рукостискання Proposal / Agreement в RSTP ────────────────────────────
def fig_rstp_handshake():
    """Швидке сходження RSTP (802.1w) за допомогою механізму Proposal / Agreement.
    Замість очікування 30-50 секунд таймерів, порти переходять у Forwarding за мілісекунди."""
    W, H = 760, 440
    f = [text(W / 2, 28, "RSTP Proposal / Agreement: миттєве сходження без таймерів", size=16, bold=True)]

    # Двоє комутаторів: Switch 1 (Root) та Switch 2
    sw1, w1, h1 = textbox(160, 90, "Комутатор 1\n(Root Bridge)", size=12, bold=True, fill="#eafaf0", stroke=FIELD)
    sw2, w2, h2 = textbox(600, 90, "Комутатор 2\n(Нове підключення)", size=12, bold=True, fill="#eef3ff", stroke=NEG)
    f.append(sw1)
    f.append(sw2)

    # Горизонтальні лінії часу вниз (розділені на відрізки, щоб не перетинали коробку Sync)
    f.append(line(160, 120, 160, 380, color=MUTED, sw=1.2, dash="3,3"))

    # Дот-лінія для Sw2 із перервою на бокс Крок 2
    f.append(line(600, 120, 600, 195, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(600, 255, 600, 380, color=MUTED, sw=1.2, dash="3,3"))

    # Крок 1: Proposal (Sw1 -> Sw2)
    y1 = 150
    f.append(arrow(160, y1, 595, y1 + 30, color=NEG, sw=2))
    f.append(fitbox(380, y1 + 5, 230, 26, "Крок 1: BPDU з прапором Proposal", size=10, bold=True, fill="#eef3ff", stroke=NEG))

    # Крок 2: Sync на Sw2 (переведення non-edge портів у Discarding)
    y2 = 205
    f.append(rect(490, y2, 220, 44, fill="#fdecea", stroke=POS, sw=1.2))
    f.append(mtext(600, y2 + 15, ["Крок 2: Синхронізація (Sync)", "Блокування інших DP портів Sw2"], size=10, bold=True, color=POS))

    # Крок 3: Agreement (Sw2 -> Sw1)
    y3 = 280
    f.append(arrow(600, y3, 165, y3 + 30, color=FIELD, sw=2))
    f.append(fitbox(380, y3 + 5, 230, 26, "Крок 3: BPDU з прапором Agreement", size=10, bold=True, fill="#eafaf0", stroke=FIELD))

    # Крок 4: Миттєвий перехід у Forwarding
    y4 = 345
    f.append(rect(70, y4, 180, 32, fill="#eafaf0", stroke=FIELD, sw=1.2))
    f.append(text(160, y4 + 20, "Порт Sw1 → Forwarding", size=10, bold=True, color=FIELD))

    f.append(rect(510, y4, 180, 32, fill="#eafaf0", stroke=FIELD, sw=1.2))
    f.append(text(600, y4 + 20, "Порт Sw2 → Forwarding", size=10, bold=True, color=FIELD))

    # Підпис внизу
    f.append(text(W / 2, 415, "Повнодуплексний зв'язок переходить у стан Forwarding за кілька мілісекунд (замість 30-50 с).",
                  size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, "rstp-handshake.svg"), W, H, *f)


if __name__ == "__main__":
    fig_loop_problem()
    fig_stp_topology()
    fig_rstp_handshake()
    print("Згенеровано фігури для STP/RSTP у ./img/")
