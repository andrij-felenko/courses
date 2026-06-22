# -*- coding: utf-8 -*-
"""Фігури до теми «Канал, смуга, пакет».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: F401,F403

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b08900"


# ── локальні помічники поверх svgkit (без власного стилю) ────────────────────
def antenna(x, y_base, h=22):
    """Щогла антени зі стрілкою-вилкою вгорі."""
    top = y_base - h
    return (line(x, y_base, x, top, color=NEG, sw=2) +
            line(x, top, x - 6, top - 8, color=NEG, sw=2) +
            line(x, top, x + 6, top - 8, color=NEG, sw=2))


def waves(cx, cy, n=3, r0=9, dr=11):
    """Дуги радіохвиль праворуч від точки (cx,cy)."""
    out = []
    for i in range(n):
        r = r0 + i * dr
        out.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                   'fill="none" stroke="%s" stroke-width="1.8"/>'
                   % (cx, cy - r, r, r, cx, cy + r, NEG))
    return "".join(out)


def bell(cx, base, w, h, color, sw=2.2, fill="none"):
    """Дзвоноподібна крива (спектр каналу) шириною w, висотою h на основі base."""
    x0, x1 = cx - w / 2, cx + w / 2
    c = w * 0.22
    d = ("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f "
         "C %.1f %.1f %.1f %.1f %.1f %.1f"
         % (x0, base,
            x0 + c, base, cx - c, base - h, cx, base - h,
            cx + c, base - h, x1 - c, base, x1, base))
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, color, sw)


# ════════════════════════════════════════════════════════════════════════════
#  1. Смуга 2.4 ГГц: безліцензійна — тому переповнена
# ════════════════════════════════════════════════════════════════════════════
def fig_band():
    """Одна вузька смуга 2.400–2.4835 ГГц, у яку набилися всі підряд: Wi-Fi,
    Bluetooth, Zigbee, мікрохвильовка, радіотелефон. «Безліцензійна» = «нічия»."""
    W, H = 760, 330
    bx, bw = 70, 620
    by, bh = 150, 56
    f = [rect(bx, by, bw, bh, fill="#f4f6f8", stroke=MUTED, sw=1.6)]
    f.append(text(bx, by + bh + 22, "2.400 ГГц", size=11, color=MUTED, anchor="start"))
    f.append(text(bx + bw, by + bh + 22, "2.4835 ГГц", size=11, color=MUTED, anchor="end"))
    f.append(text(W / 2, by - 16, "усі тиснуться в ту саму смугу", size=12, bold=True, color=POS))

    tenants = [("Wi-Fi", NEG), ("Bluetooth", "#0a3d91"), ("Zigbee", FIELD),
               ("піч", POS), ("радіотел.", GOLD)]
    cw, gap = 96, 12
    x = bx + 18
    for nm, col in tenants:
        f.append(fitbox(x, by + 8, cw, bh - 16, nm, size=10, bold=True,
                        fill=BG, stroke=col, color=col, sw=1.5))
        x += cw + gap

    f.append(fitbox(50, 252, 660, 50,
                    "«Безліцензійна» означає «нічия»: заходити можна без дозволу — "
                    "але й захисту від сусідів немає.",
                    size=12, bold=True, fill="#fbecec", stroke=POS))
    return render(os.path.join(IMG, "band.svg"), W, H, *f,
                  title="Смуга 2.4 ГГц: безліцензійна — тому переповнена")


# ════════════════════════════════════════════════════════════════════════════
#  2. Канали: смугу ділять, але вони перекриваються
# ════════════════════════════════════════════════════════════════════════════
def fig_channels():
    """Широкі канали Wi-Fi (~20 МГц) налазять один на одного; не перекриваються
    лише 1, 6, 11. Bluetooth — десятки вузьких каналів, по яких він стрибає."""
    W, H = 760, 380
    ax0, ax1 = 70, 690
    base = 188
    f = [line(ax0, base, ax1, base, color=INK, sw=1.6)]
    f.append(text(ax0, base + 20, "2.400", size=10, color=MUTED, anchor="start"))
    f.append(text(ax1, base + 20, "2.4835 ГГц", size=10, color=MUTED, anchor="end"))

    # Wi-Fi: 13 центрів через 5 МГц; ширина дзвона ~20 МГц. Підсвітити 1,6,11.
    span = ax1 - ax0
    mhz = span / 83.5
    chw = 20 * mhz
    f.append(text(W / 2, 70, "Wi-Fi: широкі канали налазять один на одного", size=12, bold=True, color=NEG))
    big = {1: 0, 6: 25, 11: 50}
    for ch in range(1, 14):
        center_mhz = 12 + (ch - 1) * 5      # 2.412 ГГц = канал 1
        cx = ax0 + center_mhz * mhz
        if ch in big:
            f.append(bell(cx, base, chw, 86, NEG, sw=2.4, fill="#eaf0fd"))
            f.append(text(cx, base - 92, str(ch), size=12, bold=True, color=NEG))
        else:
            f.append(bell(cx, base, chw, 60, MUTED, sw=1.2))
    f.append(text(ax0 + (12 + 25) * mhz, base + 36,
                  "лише 1, 6, 11 не перекриваються", size=11, bold=True, color=NEG))

    # Bluetooth: смужка вузьких каналів + підпис «стрибає»
    by = 300
    f.append(text(W / 2, 262, "Bluetooth: десятки вузьких каналів — стрибає по них",
                  size=12, bold=True, color="#0a3d91"))
    n = 40
    step = span / n
    for i in range(n):
        x = ax0 + i * step + step * 0.2
        f.append(rect(x, by, step * 0.6, 22, fill="#eaf0fd", stroke="#0a3d91", sw=0.8, rx=2))
    # стрибки-дуги між кількома каналами
    for a, b in [(3, 17), (17, 9), (9, 31), (31, 22)]:
        xa = ax0 + a * step + step * 0.5
        xb = ax0 + b * step + step * 0.5
        r = abs(xb - xa) / 2
        mx = (xa + xb) / 2
        f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
                 % (xa, by, r, r * 0.5, xb, by, GOLD))
    return render(os.path.join(IMG, "channels.svg"), W, H, *f,
                  title="Канали: смугу ділять, але вони перекриваються")


# ════════════════════════════════════════════════════════════════════════════
#  3. Ширина каналу ↔ швидкість: компроміс
# ════════════════════════════════════════════════════════════════════════════
def fig_bandwidth():
    """Той самий шматок спектра: багато вузьких каналів (кожен везе мало) проти
    кількох широких (везе більше, але влазить мало й ловить більше завад)."""
    W, H = 760, 360
    # ліва панель — вузькі
    f = [rect(50, 78, 320, 210, fill=BG, stroke=NEG, sw=1.8, rx=12)]
    f.append(text(210, 104, "вузькі канали", size=13, bold=True, color=NEG))
    nx0, nx1, ny = 74, 346, 200
    f.append(line(nx0, ny, nx1, ny, color=INK, sw=1.4))
    n = 8
    step = (nx1 - nx0) / n
    for i in range(n):
        cx = nx0 + i * step + step / 2
        f.append(bell(cx, ny, step * 0.9, 56, NEG, sw=1.6, fill="#eaf0fd"))
    f.append(text(210, 234, "багато слотів,", size=11, bold=True, color=INK))
    f.append(text(210, 252, "кожен везе МАЛО даних", size=11, color=MUTED))

    # права панель — широкі
    f.append(rect(390, 78, 320, 210, fill="#eaf6ec", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(550, 104, "широкі канали", size=13, bold=True, color=FIELD))
    wx0, wx1, wy = 414, 686, 200
    f.append(line(wx0, wy, wx1, wy, color=INK, sw=1.4))
    n = 3
    step = (wx1 - wx0) / n
    for i in range(n):
        cx = wx0 + i * step + step / 2
        f.append(bell(cx, wy, step * 0.9, 56, FIELD, sw=1.8, fill="#d8f0de"))
    f.append(text(550, 234, "везе БІЛЬШЕ даних,", size=11, bold=True, color=INK))
    f.append(text(550, 252, "та слотів мало й більше завад", size=11, color=MUTED))

    f.append(fitbox(50, 306, 660, 40,
                    "Більше смуги = вища швидкість, але менше каналів влазить у скінченний спектр.",
                    size=12, bold=True, fill="#eaf6ec", stroke=FIELD))
    return render(os.path.join(IMG, "bandwidth.svg"), W, H, *f,
                  title="Ширина каналу ↔ швидкість: компроміс")


# ════════════════════════════════════════════════════════════════════════════
#  4. Як уживатися в спільній смузі: три стратегії
# ════════════════════════════════════════════════════════════════════════════
def fig_coexist():
    """Три способи «чемності» в спільному ефірі: обрати тихий канал, стрибати
    частотою, слухати перед передачею. Жодна не дає гарантії — лише рідші колізії."""
    W, H = 760, 320
    cards = [
        ("обрати тихий канал", ["Wi-Fi сидить на одному", "каналі — береш найвільніший"], NEG, "#eaf0fd"),
        ("стрибати частотою", ["Bluetooth скаче по каналах", "~1600 разів за секунду"], "#0a3d91", "#eef3ff"),
        ("слухати перед передачею", ["спершу перевір, чи канал", "вільний (CSMA/CA)"], FIELD, "#eaf6ec"),
    ]
    cw, gap = 210, 20
    x0 = (W - (3 * cw + 2 * gap)) / 2
    for i, (head, lines, col, fill) in enumerate(cards):
        x = x0 + i * (cw + gap)
        f_card = rect(x, 78, cw, 150, fill=fill, stroke=col, sw=2, rx=12)
        if i == 0:
            f = [f_card]
        else:
            f.append(f_card)
        f.append(fitbox(x + 10, 92, cw - 20, 34, head, size=12.5, bold=True,
                        fill=fill, stroke=fill, color=col))
        for j, ln in enumerate(lines):
            f.append(text(x + cw / 2, 156 + j * 20, ln, size=11, color=INK))
    f.append(fitbox(50, 250, 660, 46,
                    "Спільне одне: ЖОДНА не дає гарантії — заглушити ефір може будь-хто; "
                    "вони лише роблять зіткнення рідшими.",
                    size=11.5, bold=True, fill="#fbecec", stroke=POS))
    return render(os.path.join(IMG, "coexist.svg"), W, H, *f,
                  title="Як уживатися в спільній смузі: три стратегії")


# ════════════════════════════════════════════════════════════════════════════
#  5. Стрибки частотою оминають заваду
# ════════════════════════════════════════════════════════════════════════════
def fig_hopping():
    """Сітка час×канал: зв'язок скаче відомою послідовністю. Один канал забитий
    завадою (червоний рядок) — у нього влучає лише один стрибок, гине 1 пакет."""
    W, H = 760, 360
    rows, cols = 6, 8
    gx0, gy0 = 110, 80
    cw, ch = 72, 34
    gap = 6
    jam_row = 3
    # підписи осей
    f = [text(gx0 - 14, gy0 + rows * (ch + gap) / 2, "канали", size=11, bold=True,
              color=MUTED, anchor="end")]
    f.append(text(gx0 + cols * (cw + gap) / 2, gy0 + rows * (ch + gap) + 24,
                  "час →", size=11, bold=True, color=MUTED))
    # сітка
    for r in range(rows):
        for c in range(cols):
            x = gx0 + c * (cw + gap)
            y = gy0 + r * (ch + gap)
            fill = "#fbecec" if r == jam_row else BG
            stroke = POS if r == jam_row else "#e0e0e0"
            cell = rect(x, y, cw, ch, fill=fill, stroke=stroke, sw=1.0, rx=4)
            if r == 0 and c == 0:
                f = [cell] + f
            else:
                f.append(cell)
    f.append(text(gx0 + cols * (cw + gap) + 6, gy0 + jam_row * (ch + gap) + ch / 2 + 4,
                  "завада", size=10, bold=True, color=POS, anchor="start"))

    # послідовність стрибків (рядок на кожен крок часу)
    seq = [1, 4, 3, 0, 5, 3, 2, 4]
    pts = []
    for c, r in enumerate(seq):
        cx = gx0 + c * (cw + gap) + cw / 2
        cy = gy0 + r * (ch + gap) + ch / 2
        pts.append((cx, cy))
        hit = (r == jam_row)
        f.append(circle(cx, cy, 8, fill=(POS if hit else FIELD),
                        stroke=(POS if hit else FIELD), sw=0))
        if hit:
            f.append(text(cx, cy - 14, "✗", size=13, bold=True, color=POS))
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        f.append(line(x1, y1, x2, y2, color=MUTED, sw=1.4, dash="4,3"))

    f.append(fitbox(50, 306, 660, 40,
                    "Забитий канал коштує лише ОДНОГО загубленого пакета — "
                    "решта проходить по інших каналах.",
                    size=12, bold=True, fill="#eaf6ec", stroke=FIELD))
    return render(os.path.join(IMG, "hopping.svg"), W, H, *f,
                  title="Стрибки частотою оминають заваду")


# ════════════════════════════════════════════════════════════════════════════
#  6. Анатомія радіопакета
# ════════════════════════════════════════════════════════════════════════════
def fig_packet():
    """Поля пакета вздовж часу: преамбула → заголовок → дані → CRC. Усе, крім
    преамбули, — той самий пакет, що й на дроті; нове — преамбула на початку."""
    W, H = 760, 330
    y, h = 150, 56
    parts = [("ПРЕАМБУЛА", "приймач ловить\nі синхронізується", GOLD, "#fbf6e6", 150),
             ("ЗАГОЛОВОК", "адреси, довжина,\nтип", NEG, "#eaf0fd", 150),
             ("ДАНІ", "корисне\nнавантаження", INK, "#f4f6f8", 180),
             ("CRC", "контроль\nцілості", FIELD, "#eaf6ec", 90)]
    x = 70
    f = []
    for name, sub, col, fill, w in parts:
        cell = rect(x, y, w, h, fill=fill, stroke=col, sw=1.8)
        if not f:
            f = [cell]
        else:
            f.append(cell)
        f.append(text(x + w / 2, y + 24, name, size=12, bold=True, color=col))
        for j, ln in enumerate(sub.split("\n")):
            f.append(text(x + w / 2, y + h + 18 + j * 15, ln, size=9.5, color=MUTED))
        x += w + 6
    f.append('<line x1="70" y1="128" x2="%d" y2="128" stroke="%s" stroke-width="1.5" '
             'marker-end="url(#arrow)"/>' % (x - 6, MUTED))
    f.append(text((70 + x) / 2, 120, "час →", size=10, color=MUTED))
    f.append(fitbox(50, 256, 660, 50,
                    "Нове проти дроту — лише ПРЕАМБУЛА: приймач не «під'єднаний»,\n"
                    "тож мусить спершу впіймати й налаштуватися на сигнал.",
                    size=11.5, bold=True, fill="#fbf6e6", stroke=GOLD))
    return render(os.path.join(IMG, "packet.svg"), W, H, *f,
                  title="Анатомія радіопакета: преамбула, заголовок, дані, CRC")


# ════════════════════════════════════════════════════════════════════════════
#  7. 2.4 ГГц проти 5 ГГц
# ════════════════════════════════════════════════════════════════════════════
def fig_2v5():
    """Та сама пара компромісів: 2.4 ГГц бере далі й крізь стіни, але людно й
    повільніше; 5 ГГц — багато чистих каналів і швидкість, та коротша дальність."""
    W, H = 760, 340
    f = [rect(50, 80, 320, 200, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=12)]
    f.append(text(210, 108, "2.4 ГГц", size=15, bold=True, color=NEG))
    left = ["✓ бере далі",
            "✓ краще крізь стіни",
            "✓ є майже всюди",
            "✗ мало каналів, людно",
            "✗ нижча швидкість"]
    for i, ln in enumerate(left):
        col = FIELD if ln[0] == "✓" else POS
        f.append(text(74, 138 + i * 26, ln, size=12, color=col, anchor="start"))

    f.append(rect(390, 80, 320, 200, fill="#eaf6ec", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(550, 108, "5 ГГц", size=15, bold=True, color=FIELD))
    right = ["✓ багато чистих каналів",
             "✓ вища швидкість",
             "✗ коротша дальність",
             "✗ гірше крізь стіни"]
    for i, ln in enumerate(right):
        col = FIELD if ln[0] == "✓" else POS
        f.append(text(414, 138 + i * 26, ln, size=12, color=col, anchor="start"))

    f.append(fitbox(50, 298, 660, 34,
                    "Нижча частота краще огинає перешкоди; вища дає більше спектра — суто фізика хвиль.",
                    size=11.5, bold=True, fill="#f4f6f8", stroke=MUTED))
    return render(os.path.join(IMG, "2v5.svg"), W, H, *f,
                  title="2.4 ГГц проти 5 ГГц: дальність проти швидкості")


def main():
    for fn in (fig_band, fig_channels, fig_bandwidth, fig_coexist,
               fig_hopping, fig_packet, fig_2v5):
        p = fn()
        print("written", os.path.relpath(p, os.path.dirname(__file__)))


if __name__ == "__main__":
    main()
