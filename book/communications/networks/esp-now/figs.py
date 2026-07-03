# -*- coding: utf-8 -*-
"""Фігури до теми «ESP-NOW».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: F401,F403

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b08900"


def chip(cx, cy, label, w=104, h=46, col=NEG, fill="#eaf0fd"):
    """Прямокутник-вузол (МК) з підписом усередині."""
    return fitbox(cx - w / 2, cy - h / 2, w, h, label, size=11, bold=True,
                  fill=fill, stroke=col, color=col, sw=1.8)


# ════════════════════════════════════════════════════════════════════════════
#  1. Два стеки: повний Wi-Fi/IP проти одного шару ESP-NOW
# ════════════════════════════════════════════════════════════════════════════
def fig_stacks():
    """Ліворуч — вежа рівнів (застосунок→TCP→IP→…→радіо), яку треба пройти,
    щоб два пристрої заговорили. Праворуч — ESP-NOW: застосунок сідає майже
    прямо на радіо, лише кадр 802.11. Менше шарів = менше затримки й коду."""
    W, H = 760, 430
    # ── ліва вежа: повний стек ──
    lx, lw = 70, 250
    layers = [("Застосунок", INK, "#f4f6f8"),
              ("TCP / UDP  (порти)", NEG, "#eaf0fd"),
              ("IP  (маршрут, адреса)", NEG, "#eaf0fd"),
              ("DHCP видав адресу", MUTED, "#f0f2f4"),
              ("Wi-Fi: приєднання до AP", MUTED, "#f0f2f4"),
              ("Радіо 802.11", GOLD, "#fbf6e6")]
    lh, gap = 46, 8
    y = 78
    f = [text(lx + lw / 2, 62, "звичайний Wi-Fi + TCP/IP", size=12, bold=True, color=NEG)]
    for name, col, fill in layers:
        f.append(fitbox(lx, y, lw, lh, name, size=11, bold=True, fill=fill, stroke=col, color=col))
        y += lh + gap
    f.append(text(lx + lw / 2, y + 4, "усі шари — щоб просто «сказати сусідові»",
                  size=10, color=MUTED))

    # ── права вежа: ESP-NOW ──
    rx, rw = 440, 250
    f.append(text(rx + rw / 2, 62, "ESP-NOW", size=12, bold=True, color=FIELD))
    f.append(fitbox(rx, 78, rw, lh, "Застосунок", size=11, bold=True,
                    fill="#f4f6f8", stroke=INK, color=INK))
    f.append(fitbox(rx, 78 + lh + gap, rw, lh, "ESP-NOW: кадр-дія 802.11",
                    size=11, bold=True, fill="#eaf6ec", stroke=FIELD, color=FIELD))
    f.append(fitbox(rx, 78 + 2 * (lh + gap), rw, lh, "Радіо 802.11",
                    size=11, bold=True, fill="#fbf6e6", stroke=GOLD, color=GOLD))
    # порожнє місце під правою вежею — підкреслює, чого НЕМА
    f.append(fitbox(rx, 78 + 3 * (lh + gap) + 6, rw, 3 * lh + 2 * gap - 6,
                    "НЕМА: приєднання, DHCP,\nIP, портів, рукостискань",
                    size=11, bold=True, fill=BG, stroke=MUTED, color=MUTED, rx=12))

    f.append(fitbox(50, 388, 660, 34,
                    "Менше шарів між застосунком і радіо — менше затримки, коду й енергії.",
                    size=12, bold=True, fill="#eaf6ec", stroke=FIELD))
    return render(os.path.join(IMG, "stacks.svg"), W, H, *f,
                  title="Два стеки: пройти всі рівні проти одного кадру")


# ════════════════════════════════════════════════════════════════════════════
#  2. Топологія: вузли говорять напряму за MAC; broadcast — усім одразу
# ════════════════════════════════════════════════════════════════════════════
def fig_topology():
    """Ліворуч — unicast: вузли адресують один одного за MAC, без центру (нема
    роутера). Праворуч — broadcast на FF:FF:FF:FF:FF:FF: один кадр ловлять усі."""
    W, H = 760, 380
    # ── ліва панель: прямий unicast між рівними ──
    f = [rect(46, 74, 330, 240, fill=BG, stroke=NEG, sw=1.6, rx=12)]
    f.append(text(211, 98, "напряму, за MAC-адресою", size=12, bold=True, color=NEG))
    nodes = [(120, 150, "A4:…:07"), (300, 150, "A4:…:1B"),
             (120, 260, "A4:…:9C"), (300, 260, "A4:…:42")]
    for cx, cy, mac in nodes:
        f.append(chip(cx, cy, "МК\n" + mac, w=96, h=44))
    # прямі лінки «кожен з кожним» (без центру)
    pairs = [(0, 1), (0, 2), (1, 3), (2, 3), (0, 3)]
    for a, b in pairs:
        x1, y1, _ = nodes[a]
        x2, y2, _ = nodes[b]
        f.append(line(x1, y1, x2, y2, color=MUTED, sw=1.4, dash="5,4"))
    f.append(text(211, 300, "нема роутера — вузли рівні", size=10, color=MUTED))

    # ── права панель: broadcast ──
    f.append(rect(400, 74, 314, 240, fill="#eaf6ec", stroke=FIELD, sw=1.6, rx=12))
    f.append(text(557, 98, "broadcast: FF:FF:FF:FF:FF:FF", size=11.5, bold=True, color=FIELD))
    sx, sy = 460, 200
    f.append(chip(sx, sy, "джерело", w=88, h=44, col=FIELD, fill="#d8f0de"))
    # хвилі
    for i in range(3):
        r = 20 + i * 15
        f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="1.6"/>' % (sx + 46, sy - r, r, r, sx + 46, sy + r, FIELD))
    for cy in (150, 200, 250):
        f.append(chip(632, cy, "усі\nчують", w=74, h=40, col=INK, fill=BG))
        f.append(line(sx + 46, sy, 596, cy, color=FIELD, sw=1.2, dash="3,3"))
    f.append(text(557, 300, "один кадр — усім одразу", size=10, color=MUTED))

    f.append(fitbox(50, 330, 660, 40,
                    "Топологію будує сам застосунок: пряма пара, зірка, багатоточка чи ретрансляція — "
                    "мережа не нав'язана.",
                    size=11.5, bold=True, fill="#eaf0fd", stroke=NEG))
    return render(os.path.join(IMG, "topology.svg"), W, H, *f,
                  title="Топологія ESP-NOW: прямі пари й broadcast, без центру")


# ════════════════════════════════════════════════════════════════════════════
#  3. «Успіх» — це лише MAC-квитанція, а не «застосунок прочитав»
# ════════════════════════════════════════════════════════════════════════════
def fig_ack():
    """Кадр дійшов до радіо приймача → апаратний ACK → callback каже SUCCESS.
    Але це НЕ означає, що застосунок його обробив. А broadcast не квитують
    узагалі — там SUCCESS означає лише «пішло в ефір»."""
    W, H = 760, 380
    tx, rx = 150, 610
    yline = 150
    f = [chip(tx, yline, "передавач", w=120, h=46, col=NEG, fill="#eaf0fd")]
    f.append(chip(rx, yline, "приймач\n(радіо)", w=120, h=46, col=FIELD, fill="#eaf6ec"))
    # кадр туди
    f.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.2" '
             'marker-end="url(#arrow)"/>' % (tx + 62, yline - 10, rx - 62, yline - 10, INK))
    f.append(text((tx + rx) / 2, yline - 18, "кадр-дія ESP-NOW", size=11, bold=True, color=INK))
    # ACK назад
    f.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2.2" '
             'marker-end="url(#arrow)"/>' % (rx - 62, yline + 14, tx + 62, yline + 14, FIELD))
    f.append(text((tx + rx) / 2, yline + 30, "апаратний ACK (рівень MAC)", size=11, bold=True, color=FIELD))

    # що callback РЕАЛЬНО каже
    f.append(fitbox(70, 214, 300, 70,
                    "callback → ESP_NOW_SEND_SUCCESS\nозначає лише: радіо приймача\nвзяло кадр і квитнуло",
                    size=11, bold=True, fill="#eaf6ec", stroke=FIELD, color=INK))
    f.append(fitbox(390, 214, 300, 70,
                    "НЕ означає: застосунок кадр\nпрочитав, розібрав чи виконав\nкоманду",
                    size=11, bold=True, fill="#fbecec", stroke=POS, color=INK))

    f.append(fitbox(50, 306, 660, 56,
                    "Broadcast ніхто не квитує — там SUCCESS = лише «пішло в ефір».\n"
                    "Потрібна певність доставки? Клади власне підтвердження у відповідь-кадр.",
                    size=11.5, bold=True, fill="#fbf6e6", stroke=GOLD))
    return render(os.path.join(IMG, "ack.svg"), W, H, *f,
                  title="«Успіх» = MAC-квитанція, а не «застосунок прочитав»")


# ════════════════════════════════════════════════════════════════════════════
#  4. Обидва вузли — на ОДНОМУ каналі, інакше тиша
# ════════════════════════════════════════════════════════════════════════════
def fig_channel():
    """Ефір 2.4 ГГц поділено на канали. ESP-NOW не шукає канал сам — обидва
    вузли мусять сидіти на однаковому, інакше кадр летить у порожнечу.
    Пастка: у режимі STA канал диктує роутер, до якого приєднаний вузол."""
    W, H = 760, 360
    ax0, ax1 = 80, 680
    base = 150
    f = [line(ax0, base, ax1, base, color=INK, sw=1.5)]
    f.append(text(ax0, base + 22, "канал 1", size=10, color=MUTED, anchor="start"))
    f.append(text(ax1, base + 22, "канал 13", size=10, color=MUTED, anchor="end"))
    # позначки каналів
    n = 13
    step = (ax1 - ax0) / (n - 1)
    same = 6           # обидва тут — чують один одного
    other = 11         # приймач тут — тиша
    for i in range(n):
        ch = i + 1
        x = ax0 + i * step
        hot = ch in (same,)
        f.append(line(x, base - 6, x, base + 6, color=(FIELD if hot else MUTED),
                      sw=(2.4 if hot else 1.1)))
        if ch in (1, same, other, 13):
            f.append(text(x, base - 14, str(ch), size=10, bold=hot,
                          color=(FIELD if hot else MUTED)))
    # два вузли на каналі 6 — чують
    xs = ax0 + (same - 1) * step
    f.append(chip(xs - 70, 250, "A: кан. 6", w=100, h=42, col=FIELD, fill="#d8f0de"))
    f.append(chip(xs + 70, 250, "B: кан. 6", w=100, h=42, col=FIELD, fill="#d8f0de"))
    f.append(line(xs - 70, 229, xs - 70, base + 8, color=FIELD, sw=1.4, dash="4,3"))
    f.append(line(xs + 70, 229, xs + 70, base + 8, color=FIELD, sw=1.4, dash="4,3"))
    f.append('<line x1="%.1f" y1="250" x2="%.1f" y2="250" stroke="%s" stroke-width="2" '
             'marker-end="url(#arrow)" marker-start="url(#arrow)"/>' % (xs - 20, xs + 20, FIELD))
    f.append(text(xs, 242, "чують", size=10, bold=True, color=FIELD))

    # вузол на іншому каналі — тиша
    xo = ax0 + (other - 1) * step
    f.append(chip(xo, 250, "C: кан. 11", w=104, h=42, col=POS, fill="#fbecec"))
    f.append(line(xo, 229, xo, base + 8, color=POS, sw=1.4, dash="4,3"))
    f.append(text(xo, 288, "✗ не чує A і B", size=10, bold=True, color=POS))

    f.append(fitbox(50, 312, 660, 40,
                    "ESP-NOW сам канал не шукає: обидва вузли мусять бути на ОДНОМУ. "
                    "У режимі STA канал диктує роутер, до якого приєднаний вузол.",
                    size=11, bold=True, fill="#fbecec", stroke=POS))
    return render(os.path.join(IMG, "channel.svg"), W, H, *f,
                  title="Обидва вузли — на одному каналі, інакше тиша")


def main():
    for fn in (fig_stacks, fig_topology, fig_ack, fig_channel):
        p = fn()
        print("written", os.path.relpath(p, os.path.dirname(__file__)))


if __name__ == "__main__":
    main()
