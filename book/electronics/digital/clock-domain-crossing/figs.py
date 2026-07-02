# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_two_domains():
    """Дві тактові області з різними тактами, сигнал тягнеться через межу."""
    W, H = 720, 320
    els = []
    # Ліва область
    els.append(rect(30, 60, 280, 220, fill="#eaf0fd", stroke=NEG, sw=2))
    els.append(text(170, 86, "Область A", size=16, color=NEG, bold=True))
    els.append(text(170, 108, "такт CLK_A = 50 МГц", size=12, color=NEG))
    els.append(fitbox(70, 140, 200, 56, "Логіка A\n(лічильники, регістри)", size=13,
                       fill=BG, stroke=NEG))
    # Права область
    els.append(rect(410, 60, 280, 220, fill="#fdecea", stroke=POS, sw=2))
    els.append(text(550, 86, "Область B", size=16, color=POS, bold=True))
    els.append(text(550, 108, "такт CLK_B = 33 МГц", size=12, color=POS))
    els.append(fitbox(450, 140, 200, 56, "Логіка B\n(інший конвеєр)", size=13,
                       fill=BG, stroke=POS))
    # Межа
    els.append(line(360, 40, 360, 300, color=INK, sw=2, dash="8 6"))
    els.append(text(360, 30, "МЕЖА", size=13, color=INK, bold=True))
    # Сигнал через межу
    els.append(arrow(270, 168, 450, 168, color=INK, sw=2.2))
    els.append(fitbox(300, 196, 120, 28, "сигнал", size=12, fill="#fff7e6", stroke="#d18b00"))
    els.append(text(360, 260, "тут CLK_A нічого не знає про фронти CLK_B",
                    size=12, color=MUTED))
    render(os.path.join(OUT, 'two-domains.svg'), W, H, *els)


def fig_bit_skew():
    """Багатобітне число через N синхронізаторів: біти приходять у різні такти."""
    W, H = 720, 360
    els = []
    els.append(text(W/2, 28, "0111 → 1000: усі чотири біти міняються одночасно",
                    size=15, bold=True))
    # стара і нова величина
    cols = [120, 240, 360, 480]
    old = ['0', '1', '1', '1']
    new = ['1', '0', '0', '0']
    names = ['b3', 'b2', 'b1', 'b0']
    y0 = 70
    for i, x in enumerate(cols):
        els.append(text(x, y0, names[i], size=12, color=MUTED))
        els.append(fitbox(x-26, y0+10, 52, 34, old[i], size=16, fill="#eaf0fd", stroke=NEG))
        els.append(text(x, y0+78, "→", size=18, color=INK))
        els.append(fitbox(x-26, y0+90, 52, 34, new[i], size=16, fill="#fdecea", stroke=POS))
    els.append(text(300, y0+18, "було 0111", size=11, color=NEG, anchor="start"))
    # синхронізатори
    sy = y0 + 150
    els.append(text(W/2, sy-8, "кожен біт — свій синхронізатор, свій випадковий зсув",
                    size=12, color=MUTED))
    arrival = ['такт N',   'такт N+1', 'такт N',   'такт N+1']
    val = ['1', '1', '0', '0']  # проміжне сміття 1100
    for i, x in enumerate(cols):
        bad = (arrival[i] == 'такт N+1')
        col = POS if bad else FIELD
        els.append(arrow(x, sy+4, x, sy+34, color=col, sw=2))
        els.append(fitbox(x-30, sy+38, 60, 30, val[i], size=15,
                          fill=("#fdecea" if bad else "#eafaf0"), stroke=col))
        els.append(text(x, sy+86, arrival[i], size=10, color=col))
    # результат
    els.append(text(W/2, sy+118, "приймач у такт N бачить 1100 — числа, якого НІКОЛИ не було",
                    size=13, color=POS, bold=True))
    render(os.path.join(OUT, 'bit-skew.svg'), W, H, *els)


def fig_gray_counter():
    """Двійковий лічильник vs Грей: скільки бітів міняється за крок."""
    W, H = 720, 360
    els = []
    els.append(text(W/2, 28, "Перехід 3→4 (та 7→8): двійковий vs код Грея", size=15, bold=True))
    # двійковий
    els.append(text(190, 64, "Двійковий", size=14, color=POS, bold=True))
    bins = [("3", "011"), ("4", "100")]
    for j, (d, b) in enumerate(bins):
        x = 120 + j*150
        els.append(text(x, 90, d, size=12, color=MUTED))
        for k, ch in enumerate(b):
            chg = (j == 1)  # усі біти різні між 011 і 100
            col = POS if chg else INK
            els.append(fitbox(x-54+k*36, 100, 32, 32, ch, size=15,
                              fill=("#fdecea" if chg else BG), stroke=col))
    els.append(arrow(196, 116, 250, 116, color=INK, sw=2))
    els.append(text(190, 160, "міняються ВСІ 3 біти", size=12, color=POS))
    # Грей
    els.append(text(540, 64, "Код Грея", size=14, color=FIELD, bold=True))
    grays = [("3", "010"), ("4", "110")]
    for j, (d, b) in enumerate(grays):
        x = 470 + j*150
        els.append(text(x, 90, d, size=12, color=MUTED))
        for k, ch in enumerate(b):
            chg = (j == 1 and k == 0)  # лише старший біт міняється 010→110
            col = FIELD if chg else INK
            els.append(fitbox(x-54+k*36, 100, 32, 32, ch, size=15,
                              fill=("#eafaf0" if chg else BG), stroke=col))
    els.append(arrow(546, 116, 600, 116, color=INK, sw=2))
    els.append(text(540, 160, "міняється РІВНО 1 біт", size=12, color=FIELD))
    # Висновок
    els.append(line(40, 200, W-40, 200, color=MUTED, sw=1, dash="4 4"))
    els.append(fitbox(60, 220, W-120, 110,
                      "Якщо синхронізувати лічильник, де за крок міняється лише один біт,\n"
                      "то навіть упіймавши момент переходу, приймач прочитає або старе,\n"
                      "або нове значення — і ніколи проміжне сміття. Код Грея робить\n"
                      "багатобітний лічильник безпечним для перетину доменів.",
                      size=13, fill="#eafaf0", stroke=FIELD))
    render(os.path.join(OUT, 'gray-counter.svg'), W, H, *els)


def fig_solutions():
    """Три родини рішень CDC: один біт, керівний сигнал, потік даних."""
    W, H = 720, 330
    els = []
    els.append(text(W/2, 28, "Що передаємо через межу — те й диктує спосіб", size=15, bold=True))
    boxes = [
        ("Один біт", "прапорець, рівень,\nподія",
         "2 тригери-синхронізатор", "#eaf0fd", NEG, 30),
        ("Кілька біт,\nрідко", "команда, адреса,\nслово конфігурації",
         "рукостискання\n(request / acknowledge)", "#fff7e6", "#d18b00", 255),
        ("Потік даних", "відліки АЦП,\nпакети, відео",
         "черга FIFO\n(Грей-вказівники)", "#eafaf0", FIELD, 480),
    ]
    for title, what, how, fill, col, x in boxes:
        els.append(rect(x, 56, 210, 250, fill=fill, stroke=col, sw=2))
        els.append(fitbox(x+15, 70, 180, 46, title, size=15, fill=BG, stroke=col, bold=True))
        els.append(text(x+105, 138, "що:", size=11, color=MUTED))
        els.append(fitbox(x+15, 146, 180, 56, what, size=12, fill=BG, stroke=MUTED))
        els.append(text(x+105, 222, "як:", size=11, color=MUTED))
        els.append(fitbox(x+15, 230, 180, 60, how, size=12, fill=BG, stroke=col))
    render(os.path.join(OUT, 'solutions.svg'), W, H, *els)


def _wave(x0, y_hi, y_lo, seg, color, sw=2.4):
    """Цифрова хвиля з горизонтальних відрізків [(x_start, x_end, level 0/1), ...]
    з вертикальними фронтами між сусідніми рівнями. Повертає список SVG-ліній."""
    out = []
    prev = None
    for (xa, xb, lvl) in seg:
        y = y_lo if lvl == 0 else y_hi
        if prev is not None and prev != y:
            out.append(line(xa, prev, xa, y, color=color, sw=sw))
        out.append(line(xa, y, xb, y, color=color, sw=sw))
        prev = y
    return out


def fig_handshake_timing():
    """Чотирифазне рукостискання req/ack та вікно стабільних даних."""
    W, H = 760, 400
    els = []
    els.append(text(W / 2, 26, "Чотири фази: req↑ → ack↑ → req↓ → ack↓", size=16, bold=True))

    left = 150          # де починаються хвилі
    right = 720
    # чотири моменти фаз (по осі X)
    p1, p2, p3, p4 = 250, 380, 510, 640
    y_lab = 60

    # позначки фаз угорі
    for xp, tag, col in [(p1, "1", POS), (p2, "2", NEG), (p3, "3", POS), (p4, "4", NEG)]:
        els.append(line(xp, 74, xp, 320, color=MUTED, sw=1, dash="3 5"))
        els.append(circle(xp, y_lab + 12, 12, fill=BG, stroke=col, sw=2))
        els.append(text(xp, y_lab + 17, tag, size=13, color=col, bold=True))

    # ── DATA (шина): стабільна ще до req↑ і аж поки B не зчитає ──
    yd_hi, yd_lo = 120, 150
    els.append(text(90, 138, "data[N]", size=13, color=INK, bold=True, anchor="middle"))
    els.append(line(left, yd_hi, left + 40, yd_lo, color=MUTED, sw=1.6))     # старт «розкриття» шини
    els.append(line(left, yd_lo, left + 40, yd_hi, color=MUTED, sw=1.6))
    els.append(line(left + 40, yd_hi, p4 + 10, yd_hi, color=FIELD, sw=2.4))
    els.append(line(left + 40, yd_lo, p4 + 10, yd_lo, color=FIELD, sw=2.4))
    els.append(line(p4 + 10, yd_hi, p4 + 50, yd_lo, color=MUTED, sw=1.6))    # шина знову «вільна»
    els.append(line(p4 + 10, yd_lo, p4 + 50, yd_hi, color=MUTED, sw=1.6))
    els.append(fitbox(left + 55, yd_hi + 3, 150, 24, "стабільне слово", size=11,
                      fill="#eafaf0", stroke=FIELD))

    # ── REQ (від A, після синхронізації видно в B) ──
    yr_hi, yr_lo = 200, 230
    els.append(text(90, 218, "req", size=13, color=POS, bold=True, anchor="middle"))
    for f in _wave(left, yr_hi, yr_lo,
                   [(left, p1, 0), (p1, p3, 1), (p3, right, 0)], POS):
        els.append(f)

    # ── ACK (від B, після синхронізації видно в A) ──
    ya_hi, ya_lo = 280, 310
    els.append(text(90, 298, "ack", size=13, color=NEG, bold=True, anchor="middle"))
    for f in _wave(left, ya_hi, ya_lo,
                   [(left, p2, 0), (p2, p4, 1), (p4, right, 0)], NEG):
        els.append(f)

    # підписи під кожною фазою
    labels = [
        (p1, "A підняла req\n(слово вже стоїть)"),
        (p2, "B побачила req,\nзчитала, підняла ack"),
        (p3, "A побачила ack,\nопустила req"),
        (p4, "B побачила спад,\nопустила ack"),
    ]
    for xp, s in labels:
        els.append(fitbox(xp - 62, 332, 124, 46, s, size=10, fill=BG, stroke=MUTED))

    render(os.path.join(OUT, 'handshake-timing.svg'), W, H, *els)


def fig_handshake_arch():
    """Дві скінченні машини + синхронізатори прапорців по обидва боки межі."""
    W, H = 760, 380
    els = []
    els.append(text(W / 2, 26, "Дані йдуть напряму; синхронізують лише два прапорці", size=15, bold=True))

    # межа доменів
    els.append(line(W / 2, 52, W / 2, 350, color=INK, sw=2, dash="8 6"))
    els.append(text(W / 2, 46, "МЕЖА", size=12, color=INK, bold=True))

    # ── область A ──
    els.append(rect(24, 60, 336, 280, fill="#eaf0fd", stroke=NEG, sw=2))
    els.append(text(192, 84, "Область A  ·  такт CLK_A", size=13, color=NEG, bold=True))
    els.append(fitbox(48, 100, 150, 54, "Скінченна\nмашина A\n(IDLE→REQ→WAIT)", size=11,
                      fill=BG, stroke=NEG))
    els.append(fitbox(48, 250, 264, 40, "регістр даних (data[N])\n— стоїть незмінно весь обмін", size=11,
                      fill="#eafaf0", stroke=FIELD))

    # ── область B ──
    els.append(rect(400, 60, 336, 280, fill="#fdecea", stroke=POS, sw=2))
    els.append(text(568, 84, "Область B  ·  такт CLK_B", size=13, color=POS, bold=True))
    els.append(fitbox(560, 100, 150, 54, "Скінченна\nмашина B\n(чекає req → бере)", size=11,
                      fill=BG, stroke=POS))

    # data напряму через межу (без синхронізатора)
    els.append(arrow(312, 270, 560, 270, color=FIELD, sw=2.6))
    els.append(fitbox(360, 240, 130, 24, "дані НАПРЯМУ", size=11, fill="#eafaf0", stroke=FIELD))

    # req: A → синхронізатор у B → машина B
    yr = 132
    els.append(arrow(198, yr, 300, yr, color=POS, sw=2.2))
    els.append(text(250, yr - 8, "req", size=11, color=POS, bold=True))
    els.append(fitbox(300, yr - 18, 100, 36, "2 тригери\n(синхр. у B)", size=10,
                      fill=BG, stroke=POS))
    els.append(arrow(400, yr, 558, yr, color=POS, sw=2.2))

    # ack: B → синхронізатор у A → машина A
    ya = 190
    els.append(arrow(560, ya, 402, ya, color=NEG, sw=2.2))
    els.append(text(480, ya - 8, "ack", size=11, color=NEG, bold=True))
    els.append(fitbox(300, ya - 18, 100, 36, "2 тригери\n(синхр. у A)", size=10,
                      fill=BG, stroke=NEG))
    els.append(arrow(300, ya, 200, ya, color=NEG, sw=2.2))

    render(os.path.join(OUT, 'handshake-arch.svg'), W, H, *els)


if __name__ == '__main__':
    fig_two_domains()
    fig_bit_skew()
    fig_gray_counter()
    fig_solutions()
    fig_handshake_timing()
    fig_handshake_arch()
    print("OK figs written to", OUT)
