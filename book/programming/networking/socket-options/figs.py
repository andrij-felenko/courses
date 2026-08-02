# -*- coding: utf-8 -*-
"""Фігури до теми «Опції сокета: буфери, таймаути, TCP_NODELAY, TTL».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"    # тепле виділення (таймер, увага)
SOFT_B = "#eef3fd"   # світло-синє тло
SOFT_G = "#eaf7ef"   # світло-зелене тло
SOFT_A = "#fff6e0"   # світло-бурштинове тло


# ── 1. Два буфери за одним сокетом ────────────────────────────────────────────
# Ідея: передавальний буфер тримає НЕПІДТВЕРДЖЕНЕ (бо може знадобитися повтор),
# а вільне місце в приймальному буфері — це і є вікно, оголошене відправникові.
def fig_buffers():
    W, H = 920, 372
    f = [text(W / 2, 28, "Два буфери за одним сокетом і що вони насправді тримають",
              size=15, bold=True)]

    # програми зверху
    b1, _, _ = textbox(225, 76, "програма: send()", size=12, fill=SOFT_B, stroke=NEG, bold=True)
    b2, _, _ = textbox(695, 76, "програма: recv()", size=12, fill=SOFT_G, stroke=FIELD, bold=True)
    f += [b1, b2]

    bar_y, bar_h = 196, 72
    lx, lw = 50, 350        # передавальний буфер
    rx, rw = 520, 350       # приймальний буфер

    # стрілки програма ⇄ буфер (вертикальні, збоку від підписів буферів)
    f.append(arrow(225, 100, 225, bar_y - 30, color=NEG, sw=2.0))
    f.append(arrow(695, bar_y - 30, 695, 100, color=FIELD, sw=2.0))

    # заголовки буферів
    f.append(text(lx + lw / 2, bar_y - 12, "передавальний буфер · SO_SNDBUF",
                  size=12, color=NEG, bold=True))
    f.append(text(rx + rw / 2, bar_y - 12, "приймальний буфер · SO_RCVBUF",
                  size=12, color=FIELD, bold=True))

    # сегменти передавального буфера
    segs_l = [(150, "непідтверджене", "#fdecea", POS),
              (110, "не відіслане", SOFT_B, NEG),
              (90, "вільно", "#ffffff", MUTED)]
    x = lx
    for w, label, fill, col in segs_l:
        f.append(fitbox(x, bar_y, w, bar_h, label, size=11, color=col, fill=fill, stroke=LINE))
        x += w

    # сегменти приймального буфера
    segs_r = [(160, "прийняте,\nчекає recv", SOFT_G, FIELD),
              (190, "вільно = вікно,\nяке оголошують", "#ffffff", AMBER)]
    x = rx
    for w, label, fill, col in segs_r:
        f.append(fitbox(x, bar_y, w, bar_h, label, size=11, color=col, fill=fill, stroke=LINE))
        x += w

    # мережа між буферами
    f.append(text((lx + lw + rx) / 2, bar_y + 10, "мережа", size=12, color=MUTED))
    f.append(arrow(lx + lw + 10, bar_y + bar_h / 2, rx - 10, bar_y + bar_h / 2, color=INK, sw=2.0))

    # пояснення під буферами
    f.append(mtext(lx + lw / 2, bar_y + bar_h + 34,
                   ["байт лежить тут не до відправлення,",
                    "а до підтвердження з того боку"], size=11.5, color=MUTED))
    f.append(mtext(rx + rw / 2, bar_y + bar_h + 34,
                   ["вільне місце — це число, яке стек",
                    "оголошує відправникові як вікно"], size=11.5, color=MUTED))

    return render(os.path.join(IMG, "buffers.svg"), W, H, *f)


# ── 2. Три таймери, що стережуть три різні речі ───────────────────────────────
# Ідея: таймаут виклику, TCP_USER_TIMEOUT і зонди підтримки не замінюють один
# одного — кожен обмежує свою величину й закінчується своїм наслідком.
def fig_timeouts():
    W, H = 940, 396
    f = [text(W / 2, 28, "Три таймери сокета: кожен стереже своє", size=15, bold=True)]

    rows = [
        (104, "SO_RCVTIMEO\nSO_SNDTIMEO", NEG, SOFT_B, 340, 610,
         "один виклик recv або send",
         "виклик повертає EAGAIN — з'єднання лишається живим"),
        (212, "TCP_USER_TIMEOUT", POS, "#fdecea", 340, 860,
         "поки надіслані дані не підтверджено",
         "ядро само рве з'єднання з ETIMEDOUT"),
        (320, "SO_KEEPALIVE\nTCP_KEEPIDLE …", FIELD, SOFT_G, 340, 860,
         "поки в з'єднанні тиша, даних немає",
         "зонд питає, чи живий інший бік, і тримає запис у NAT"),
    ]

    for y, name, col, fill, x1, x2, above, below in rows:
        f.append(fitbox(34, y - 30, 276, 60, name, size=12, color=col, fill=fill, stroke=col))
        f.append(line(x1, y - 13, x1, y + 13, color=col, sw=2.0))
        f.append(line(x2, y - 13, x2, y + 13, color=col, sw=2.0))
        f.append(line(x1, y, x2, y, color=col, sw=2.0))
        f.append(text((x1 + x2) / 2, y - 22, above, size=12, color=INK))
        f.append(text((x1 + x2) / 2, y + 34, below, size=11, color=MUTED))

    return render(os.path.join(IMG, "timeouts.svg"), W, H, *f)


# ── 3. «Два записи, тоді читання» проти одного запису ─────────────────────────
# Ідея: сорок мілісекунд створює не мережа, а стик притримування дрібних даних
# із відкладеним підтвердженням; один запис знімає причину, а не симптом.
def fig_nagle():
    W, H = 960, 480
    f = [text(W / 2, 28, "Звідки беруться сталі сорок мілісекунд", size=15, bold=True)]

    def panel(px, title, rows, frame_col):
        pw = 440
        out = [rect(px, 48, pw, 408, fill="#fcfcfd", stroke=frame_col, sw=1.6, rx=10)]
        out.append(text(px + pw / 2, 72, title, size=13, color=frame_col, bold=True))
        cx_c, cx_s = px + 92, px + 348
        b1, _, _ = textbox(cx_c, 104, "клієнт", size=11.5, fill=SOFT_B, stroke=NEG, bold=True)
        b2, _, _ = textbox(cx_s, 104, "сервер", size=11.5, fill=SOFT_G, stroke=FIELD, bold=True)
        out += [b1, b2]
        for y, kind, label in rows:
            if kind == "→":
                out.append(text((cx_c + cx_s) / 2, y - 11, label, size=11, color=INK))
                out.append(arrow(cx_c + 32, y, cx_s - 32, y, color=NEG, sw=1.8))
            elif kind == "←":
                out.append(text((cx_c + cx_s) / 2, y - 11, label, size=11, color=INK))
                out.append(arrow(cx_s - 32, y, cx_c + 32, y, color=FIELD, sw=1.8))
            else:
                fill = {"c": SOFT_B, "s": SOFT_G, "t": SOFT_A}[kind]
                col = {"c": NEG, "s": FIELD, "t": AMBER}[kind]
                bx, _, _ = textbox(px + pw / 2, y, label, size=10.5,
                                   fill=fill, stroke=col, color=col)
                out.append(bx)
        return out

    f += panel(24, "два записи, тоді читання", [
        (152, "→", "заголовок 8 Б — іде одразу"),
        (200, "c", "тіло 200 Б притримано:\n8 Б ще не підтверджено"),
        (262, "s", "підтвердження відкладено:\nсервер чекає повне повідомлення"),
        (326, "t", "тиша 40 мс — розблокує таймер"),
        (382, "←", "підтвердження"),
        (430, "→", "тіло 200 Б"),
    ], POS)

    f += panel(496, "усе повідомлення одним записом", [
        (152, "→", "208 Б одним send"),
        (206, "s", "сегмент повний:\nпритримувати нема чого"),
        (268, "←", "відповідь"),
        (322, "t", "затримка = один обіг мережею"),
    ], FIELD)

    return render(os.path.join(IMG, "nagle.svg"), W, H, *f)


# ── 4. TTL: бюджет переходів і traceroute ─────────────────────────────────────
# Ідея: поле, придумане проти вічних петель, стало картографом мережі —
# бо маршрутизатор, який убив пакет, зобов'язаний назватися.
def fig_ttl():
    W, H = 940, 432
    f = [text(W / 2, 28, "TTL — бюджет переходів, який кожен маршрутизатор зменшує",
              size=15, bold=True)]

    # ── панель А: звичайний шлях
    f.append(text(W / 2, 62, "звичайний пакет: живучості вистачає до цілі",
                  size=12.5, color=MUTED))
    ay = 116
    nodes = [(104, "відправник", NEG, SOFT_B), (306, "R1", INK, FILL), (466, "R2", INK, FILL),
             (626, "R3", INK, FILL), (836, "ціль", FIELD, SOFT_G)]
    for cx, name, col, fill in nodes:
        b, _, _ = textbox(cx, ay, name, size=11.5, fill=fill, stroke=col, color=col,
                          bold=True, min_w=64)
        f.append(b)
    hops = [(104, 306, "TTL 64"), (306, 466, "63"), (466, 626, "62"), (626, 836, "61")]
    for x1, x2, lab in hops:
        f.append(text((x1 + x2) / 2, ay - 26, lab, size=11.5, color=AMBER, bold=True))
        f.append(arrow(x1 + 52, ay, x2 - 52, ay, color=INK, sw=1.8))
    f.append(text(W / 2, ay + 52, "кожен перехід забирає одиницю", size=11.5, color=MUTED))

    f.append(line(40, 208, W - 40, 208, color=MUTED, sw=1.0, dash="5,5"))

    # ── панель Б: TTL 1 і відповідь ICMP
    f.append(text(W / 2, 234, "той самий пакет із TTL 1: перший маршрутизатор мусить назватися",
                  size=12.5, color=MUTED))
    by = 300
    b, _, _ = textbox(104, by, "відправник", size=11.5, fill=SOFT_B, stroke=NEG,
                      color=NEG, bold=True)
    f.append(b)
    b, _, _ = textbox(306, by, "R1", size=11.5, fill=FILL, stroke=INK, bold=True, min_w=64)
    f.append(b)
    f.append(text(205, by - 26, "TTL 1 → 0", size=11.5, color=POS, bold=True))
    f.append(arrow(156, by, 274, by, color=INK, sw=1.8))
    f.append(text(205, by + 58, "ICMP «час вичерпано»", size=11, color=POS))
    f.append(arrow(274, by + 34, 156, by + 34, color=POS, sw=1.8))

    lad, _, _ = textbox(690, by + 12,
                        ["TTL 1 → озвався R1",
                         "TTL 2 → озвався R2",
                         "TTL 3 → озвався R3",
                         "так і виходить перелік переходів"],
                        size=11.5, fill=SOFT_A, stroke=AMBER, color=INK, pad=14)
    f.append(lad)

    return render(os.path.join(IMG, "ttl.svg"), W, H, *f)


# ── 5. Чотири рішення стека між send і дротом (оглядова, до базової) ──────────
# Ідея: send лише копіює байти в ядро, а далі стек ухвалює чотири самостійні
# рішення — і кожне з них має свою ручку, бо намір програми стекові невідомий.
def fig_decisions():
    W, H = 1000, 470
    f = [text(W / 2, 28, "Що вирішує стек після того, як send уже повернувся",
              size=15, bold=True)]

    # верхній ряд: програма → ядро → мережа
    b1, _, _ = textbox(150, 78, "програма: send(12 байтів)", size=11.5,
                       fill=SOFT_B, stroke=NEG, color=NEG, bold=True)
    b2, _, _ = textbox(500, 78, "буфери й таймери сокета в ядрі", size=11.5,
                       fill=FILL, stroke=INK, bold=True)
    b3, _, _ = textbox(858, 78, "мережа", size=11.5,
                       fill=SOFT_G, stroke=FIELD, color=FIELD, bold=True)
    f += [b1, b2, b3]
    f.append(arrow(262, 78, 348, 78, color=NEG, sw=2.0))
    f.append(arrow(660, 78, 806, 78, color=FIELD, sw=2.0))

    f.append(text(W / 2, 130, "між копіюванням і дротом ядро ухвалює чотири самостійні рішення",
                  size=12.5, color=MUTED))

    cards = [
        (24, "скільки тримати", NEG, SOFT_B, "SO_SNDBUF · SO_RCVBUF",
         ["вільне місце в прийманні —", "це вікно, оголошене", "відправникові, а вікно",
          "задає стелю швидкості"]),
        (270, "скільки чекати", FIELD, SOFT_G, "SO_RCVTIMEO · SO_KEEPALIVE",
         ["без ліміту виклик чекає", "скільки завгодно, а мертвий", "партнер просто мовчить"]),
        (516, "коли відсилати", POS, "#fdecea", "TCP_NODELAY",
         ["стек має право притримати", "дрібні дані до підтвердження —", "звідси сталі 40 мс"]),
        (762, "як далеко пускати", AMBER, SOFT_A, "IP_TTL · IP_MULTICAST_TTL",
         ["у пакеті лічильник переходів;", "для багатоадресної розсилки", "типово 1 — своя підмережа"]),
    ]

    cy, cw, ch = 162, 214, 244
    for cx, title, col, fill, opts, lines in cards:
        f.append(rect(cx, cy, cw, ch, fill=fill, stroke=col, sw=1.6, rx=10))
        f.append(text(cx + cw / 2, cy + 34, title, size=13, color=col, bold=True))
        ob, _, _ = textbox(cx + cw / 2, cy + 72, opts, size=10.5,
                           fill="#ffffff", stroke=col, color=INK, pad=8)
        f.append(ob)
        f.append(mtext(cx + cw / 2, cy + 128, lines, size=11, color=INK, lh=1.4))

    f.append(text(W / 2, 442,
                  "жодне рішення стек не ухвалить правильно сам: наміру програми він не знає",
                  size=12.5, color=MUTED))

    return render(os.path.join(IMG, "decisions.svg"), W, H, *f)


# ── 6. Хронологія двох ідей (до вставки hist-nagle-nodelay) ───────────────────
# Ідея: показати, що доріжки різні за походженням і за темпом. Відкладене
# підтвердження вже їхало в робочому ядрі раніше, ніж вийшов RFC про
# притримування, — тому колонки 1982 і 1983 у верхній доріжці порожні.
def fig_timeline():
    W, H = 1080, 470
    COLS = [150, 345, 540, 745, 950]
    BW, BH = 176, 100

    f = [text(W / 2, 30, "Дві доріжки: коли з'явилася кожна оптимізація і де вони зійшлися",
              size=16, bold=True)]

    # смуга зіткнення — малюємо ПЕРШОЮ, щоб лягла під рамки
    f.append(rect(COLS[3] - BW / 2 - 12, 86, BW + 24, 278,
                  fill=SOFT_A, stroke="none", sw=0, rx=10))

    heads = ["липень 1982", "серпень 1983", "6 січня 1984", "червень 1986", "жовтень 1989"]
    for cx, hd in zip(COLS, heads):
        f.append(text(cx, 64, hd, size=12.5, color=MUTED, bold=True))
    f.append(line(24, 76, W - 24, 76, color="#d8dce2", sw=1.2))

    # доріжка відправника
    f.append(text(26, 106, "Доріжка відправника: притримати дрібне",
                  size=13, color=NEG, anchor="start", bold=True))
    sender = {
        2: "RFC 896, Джон Нейгл\n(Ford Aerospace)\nправило притримування;\nтаймер 200–500 мс\nвідхилено як хибний шлях",
        3: "4.3BSD\nidle || TF_NODELAY\nпритримування в ядрі —\nі вимикач того ж дня",
        4: "RFC 1122\nSHOULD реалізувати,\nMUST дати вимикач",
    }
    for i, s in sender.items():
        f.append(fitbox(COLS[i] - BW / 2, 118, BW, BH, s, size=11,
                        fill=SOFT_B, stroke=NEG, sw=1.5, pad=9))

    # доріжка приймача
    f.append(text(26, 248, "Доріжка приймача: відкласти підтвердження",
                  size=13, color=AMBER, anchor="start", bold=True))
    receiver = {
        0: "RFC 813, Девід Кларк\n(MIT)\nпідтвердження можна\nвідкласти — але тоді\nтреба завести таймер",
        1: "4.2BSD\nTF_DELACK + fasttimo\nзмітання 5 разів на\nсекунду → крок 200 мс",
        4: "RFC 1122\nSHOULD відкладати,\nMUST менше за 0.5 с",
    }
    for i, s in receiver.items():
        f.append(fitbox(COLS[i] - BW / 2, 260, BW, BH, s, size=11,
                        fill="#fff6e0", stroke=AMBER, sw=1.5, pad=9))

    f.append(text(COLS[3], 388, "уперше в одному ядрі", size=12, color=AMBER, bold=True))

    f.append(text(W / 2, 428,
                  "верхні клітинки 1982 і 1983 порожні: відкладене підтвердження вже їхало "
                  "в робочому ядрі, коли правило притримування ще було чернеткою",
                  size=12.5, color=MUTED))

    return render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


# ── 7. Вікна життя сокета, у яких опція ще має сенс (до вставки proj) ─────────
# Ідея: «пізно» буває лише розмірам буферів — решта ручок діє з наступного
# виклику, тож головна пастка не в наборі опцій, а в моменті одного рядка.
def fig_windows():
    W, H = 1120, 456
    f = [text(W / 2, 28, "Коли яку опцію ще не пізно ставити", size=15, bold=True)]

    marks = [(350, "socket()"), (530, "bind()"), (715, "listen()\nconnect()"),
             (895, "accept()"), (1045, "send / recv")]
    for mx, name in marks:
        b, _, _ = textbox(mx, 100, name, size=11, fill=FILL, stroke=INK, bold=True)
        f.append(b)
        f.append(line(mx, 124, mx, 152, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(300, 142, 1090, 142, color=MUTED, sw=1.2))

    rows = [
        (204, "SO_REUSEADDR", 350, 530, NEG, SOFT_B,
         "від socket() до bind()",
         "зайнятість адреси перевіряє саме bind() — після нього перевіряти вже нічого"),
        (266, "SO_RCVBUF · SO_SNDBUF", 350, 715, POS, "#fdecea",
         "до connect() / listen()",
         "коефіцієнт масштабування вікна сторони домовляють у рукостисканні, і лише раз"),
        (328, "TCP_NODELAY · таймаути\nkeepalive · IP_TTL", 350, 1090, FIELD, SOFT_G,
         "будь-коли",
         "діють із наступного виклику — момент не важить, важить лише те, що ти їх поставив"),
        (390, "профіль на сокеті\nз accept()", 895, 1090, AMBER, SOFT_A,
         "після accept()",
         "успадковано не все — постав ще раз"),
    ]

    for yc, label, x1, x2, col, fill, inside, note in rows:
        f.append(fitbox(24, yc - 24, 244, 48, label, size=11.5, color=col,
                        fill="#ffffff", stroke=col, bold=True))
        f.append(fitbox(x1, yc - 13, x2 - x1, 26, inside, size=10.5,
                        color=col, fill=fill, stroke=col, rx=8))
        f.append(text((x1 + x2) / 2, yc + 30, note, size=10.5, color=MUTED))

    f.append(text(W / 2, 442,
                  "пізно буває тільки буферам: усе інше ти просто забув поставити",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, "windows.svg"), W, H, *f)


# ── 8. Той самий обмін, виміряний двічі (до вставки proj) ─────────────────────
# Ідея: різницю між профілями видно не в середньому, а у ФОРМІ розподілу —
# притримування дає другу купу на круглому числі, і саме її треба впізнавати.
def fig_histogram():
    W, H = 1120, 470
    f = [text(W / 2, 28, "Той самий обмін, виміряний двічі: де стоїть час обігу",
              size=15, bold=True)]

    buckets = ["0.1 – 0.2 мс", "0.2 – 0.5 мс", "0.5 – 1 мс",
               "1 – 2 мс", "2 – 35 мс", "35 – 45 мс"]
    scale = 320.0 / 1000.0

    def panel(px, title, col, fill, counts, med, tail):
        pw = 530
        out = [rect(px, 52, pw, 372, fill="#fcfcfd", stroke=col, sw=1.6, rx=10)]
        out.append(text(px + pw / 2, 80, title, size=13, color=col, bold=True))
        for i, (lab, c) in enumerate(zip(buckets, counts)):
            y = 142 + i * 38
            out.append(text(px + 130, y + 4, lab, size=10.5, color=INK, anchor="end"))
            if c == 0:
                out.append(text(px + 148, y + 4, "0", size=10.5, color=MUTED, anchor="start"))
                continue
            w = max(3.0, c * scale)
            out.append(rect(px + 140, y - 11, w, 22, fill=fill, stroke=col, sw=1.2, rx=4))
            out.append(text(px + 150 + w, y + 4, str(c), size=10.5,
                            color=INK, anchor="start"))
        out.append(text(px + pw / 2, 382, med, size=12, color=col, bold=True))
        out.append(text(px + pw / 2, 406, tail, size=11, color=MUTED))
        return out

    f += panel(24, "притримування ввімкнене (замовчування)", POS, "#fdecea",
               [6, 31, 9, 0, 0, 954],
               "медіана 40.12 мс · p99 41.03 мс",
               "друга купа стоїть на круглому числі — це таймер, а не мережа")
    f += panel(578, "TCP_NODELAY", FIELD, SOFT_G,
               [214, 706, 71, 9, 0, 0],
               "медіана 0.28 мс · p99 0.94 мс",
               "одна купа — затримка дорівнює одному обігу мережею")

    f.append(text(W / 2, 450,
                  "числа — з двох машин в одній стійці; у тебе будуть інші, а форма — та сама",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, "histogram.svg"), W, H, *f)


if __name__ == "__main__":
    for fn in (fig_buffers, fig_timeouts, fig_nagle, fig_ttl, fig_decisions,
               fig_timeline, fig_windows, fig_histogram):
        print("ok:", os.path.basename(fn()))
