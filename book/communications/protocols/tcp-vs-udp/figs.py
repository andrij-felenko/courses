# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b08900"   # колір UDP (тепле жовте) — на противагу зеленому TCP


# ── two-services: зведена таблиця TCP проти UDP ───────────────────────────────
# Ідея: поруч поставити дві служби доставки за сімома ознаками — видно, що це
# один компроміс «надійно проти швидко», розкладений по рядках.

def fig_two_services():
    W, H = 700, 360
    p = []
    lx, rx = 60, 640                 # межі таблиці
    col_feat = lx + 12               # ознака (зліва)
    col_tcp = 350                    # TCP
    col_udp = 545                    # UDP
    top = 56
    rowh = 34

    # шапка
    p.append(rect(lx, top, rx - lx, rowh, fill="#f0f0f0", stroke=MUTED, sw=1.3, rx=0))
    p.append(text(col_feat, top + 22, "ознака", size=12, color=INK, anchor="start", bold=True))
    p.append(text(col_tcp, top + 22, "TCP", size=13, color=FIELD, bold=True))
    p.append(text(col_udp, top + 22, "UDP", size=13, color=GOLD, bold=True))

    rows = [
        ("з'єднання", "так (рукостискання)", "ні (просто шлеш)"),
        ("доставка", "гарантована", "як вийде, бувають втрати"),
        ("порядок", "по порядку", "може плутатись"),
        ("затримка", "більша, плаває", "мала, рівна"),
        ("накладні", "більші", "мінімальні"),
        ("модель", "потік байтів", "окремі датаграми"),
    ]
    y = top + rowh
    for feat, tcp, udp in rows:
        p.append(rect(lx, y, rx - lx, rowh, fill=BG, stroke=MUTED, sw=1.0, rx=0))
        p.append(text(col_feat, y + 21, feat, size=11, color=INK, anchor="start", bold=True))
        p.append(text(col_tcp, y + 21, tcp, size=11, color=FIELD))
        p.append(text(col_udp, y + 21, udp, size=11, color=GOLD))
        y += rowh

    # підсумок-аналогія знизу
    band, bw, bh = textbox(W / 2, y + 30, "TCP — служба доставки з підписом про вручення;\nUDP — кинута в скриньку листівка", size=11, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.3, pad=12)
    p.append(band)

    render(os.path.join(OUT, "two-services.svg"), W, H, *p,
           title="Два транспорти поверх IP: надійний проти швидкого")


# ── handshake: трикрокове рукостискання TCP ───────────────────────────────────
# Ідея: три стрілки SYN / SYN-ACK / ACK між клієнтом і сервером ДО першого
# байта даних — видно ціну старту (кілька проходів туди-назад).

def fig_handshake():
    W, H = 700, 320
    p = []
    cx, sx = 150, 550                # вертикалі клієнта й сервера
    top, bot = 80, 290

    # дві сторони
    for x, lab in ((cx, "клієнт"), (sx, "сервер")):
        p.append(line(x, top, x, bot, color=MUTED, sw=1.3, dash="4 4"))
        b, bw, bh = textbox(x, top - 16, lab, size=12, bold=True, fill=FILL, stroke=INK, sw=1.5, pad=8)
        p.append(b)

    def msg(y, x1, x2, label, color, note):
        p.append(arrow(x1, y, x2, y, color=color, sw=2.0))
        mid = (x1 + x2) / 2
        p.append(text(mid, y - 8, label, size=12, color=color, bold=True))
        p.append(text(mid, y + 16, note, size=10, color=MUTED, italic=True))

    msg(120, cx, sx, "SYN", NEG, "з'єднаймось?")
    msg(175, sx, cx, "SYN-ACK", FIELD, "згода")
    msg(230, cx, sx, "ACK", NEG, "домовились")

    # лише після цього — дані
    p.append(line(cx, 262, sx, 262, color=POS, sw=2.4))
    p.append(text((cx + sx) / 2, 256, "і лише тепер — перший байт даних", size=11, color=POS, bold=True))

    render(os.path.join(OUT, "handshake.svg"), W, H, *p,
           title="TCP спершу домовляється: три обміни до даних")


# ── tcp-reliable: TCP ховає безлад мережі ─────────────────────────────────────
# Ідея: у дорозі пакети плутаються й гублять один; TCP перешле, дочекається,
# впорядкує — і віддасть застосунку рівний потік 1-2-3-4.

def fig_tcp_reliable():
    W, H = 700, 300
    p = []
    bw, bh, gap = 50, 36, 16
    # «у мережі» — переплутані, один загублений (3)
    netx, nety = 70, 90
    p.append(text(netx, nety - 18, "у мережі (хаос):", size=11, color=MUTED, anchor="start", bold=True))
    chaos = [("2", INK, "#eef4ff"), ("4", INK, "#eef4ff"), ("3", POS, "#fdecea"), ("1", INK, "#eef4ff")]
    x = netx
    for lab, col, fill in chaos:
        tag = lab if lab != "3" else "3 ✗"
        p.append(fitbox(x, nety, bw + (8 if lab == "3" else 0), bh, tag, size=12, fill=fill, stroke=col, sw=1.6, bold=True, color=col))
        x += bw + gap + (8 if lab == "3" else 0)
    p.append(text(x + 4, nety + 24, "3 загубився — TCP перешле", size=10, color=POS, anchor="start", italic=True))

    # стрілка-перетворення вниз
    p.append(arrow(W / 2, 150, W / 2, 188, color=INK, sw=1.8))
    p.append(text(W / 2 + 90, 172, "перешле, дочекається, впорядкує", size=10, color=MUTED, italic=True))

    # «застосунку» — рівний потік
    appx, appy = 70, 210
    p.append(text(appx, appy - 18, "застосунку (рівно):", size=11, color=FIELD, anchor="start", bold=True))
    x = appx
    for lab in ["1", "2", "3", "4"]:
        p.append(fitbox(x, appy, bw, bh, lab, size=12, fill="#eef6ef", stroke=FIELD, sw=1.8, bold=True, color=FIELD))
        x += bw + gap
    p.append(text(x + 4, appy + 24, "повно й по порядку", size=10, color=FIELD, anchor="start", italic=True))

    render(os.path.join(OUT, "tcp-reliable.svg"), W, H, *p,
           title="TCP ховає безлад мережі: застосунок бачить рівний потік")


# ── udp: датаграми без з'єднання й без гарантій ───────────────────────────────
# Ідея: UDP шле пакети й одразу забуває; частина приходить не по черзі, один
# зник — і ніхто не перешле; зате ні рукостискання, ні очікування.

def fig_udp():
    W, H = 700, 280
    p = []
    sx, rx = 90, 610
    y = 130
    # відправник і приймач
    for x, lab in ((sx, "шле"), (rx, "приймає")):
        b, bw, bh = textbox(x, y, lab, size=12, bold=True, fill=FILL, stroke=INK, sw=1.5, pad=10)
        p.append(b)

    # чотири датаграми в польоті: одна загублена (друга)
    lanes = [(-42, "1", True), (-14, "2", False), (14, "3", True), (42, "4", True)]
    for dy, lab, arrived in lanes:
        ly = y + dy
        if arrived:
            p.append(arrow(sx + 50, ly, rx - 50, ly, color=NEG, sw=1.8))
            p.append(circle(sx + 90, ly, 9, fill="#eef4ff", stroke=NEG, sw=1.6))
            p.append(text(sx + 90, ly + 4, lab, size=10, color=NEG, bold=True))
        else:
            # летить лише до середини й гасне
            p.append(line(sx + 50, ly, (sx + rx) / 2, ly, color=POS, sw=1.8, dash="5 4"))
            p.append(text((sx + rx) / 2 + 18, ly + 4, "2 зник — ніхто не перешле", size=10, color=POS, anchor="start", italic=True))

    p.append(text(W / 2, 230, "ні рукостискання, ні ретраїв, ні очікування — дані доходять миттєво й свіжими",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "udp.svg"), W, H, *p,
           title="UDP: шлеш і забуваєш — швидко, без гарантій")


# ── head-of-line: блокування голови черги ─────────────────────────────────────
# Ідея: у TCP загублений пакет 2 тримає вже прибулі 3,4,5 (затор, стрибок
# затримки); у UDP 3,4,5 віддаються одразу — пропуск замість затору.

def fig_head_of_line():
    W, H = 700, 320
    p = []
    bw, bh, gap = 56, 32, 14
    x0 = 150

    def row(y, label, lcol, cells):
        p.append(text(60, y + bh / 2 + 4, label, size=13, color=lcol, anchor="start", bold=True))
        x = x0
        for lab, col, fill in cells:
            p.append(fitbox(x, y, bw, bh, lab, size=11, fill=fill, stroke=col, sw=1.7, bold=True, color=col))
            x += bw + gap
        return x

    # TCP: 2 загубл., 3/4/5 чекають
    tcp_cells = [("1", FIELD, "#eef6ef"), ("2 ✗", POS, "#fdecea"),
                 ("3", MUTED, "#f0f0f0"), ("4", MUTED, "#f0f0f0"), ("5", MUTED, "#f0f0f0")]
    yt = 90
    xend = row(yt, "TCP", FIELD, tcp_cells)
    # дужка над 3,4,5
    bx1 = x0 + 2 * (bw + gap)
    p.append(line(bx1, yt - 10, xend - gap, yt - 10, color=POS, sw=1.6))
    p.append(text((bx1 + xend - gap) / 2, yt - 16, "прийшли, але ЧЕКАЮТЬ на 2 → затор, стрибок затримки",
                  size=10, color=POS, bold=True))

    # UDP: 2 нема, решта одразу
    udp_cells = [("1", NEG, "#eef4ff"), ("2 –", MUTED, "#f4f4f4"),
                 ("3", NEG, "#eef4ff"), ("4", NEG, "#eef4ff"), ("5", NEG, "#eef4ff")]
    yu = 190
    xend2 = row(yu, "UDP", GOLD, udp_cells)
    bx2 = x0 + 2 * (bw + gap)
    p.append(line(bx2, yu + bh + 10, xend2 - gap, yu + bh + 10, color=FIELD, sw=1.6))
    p.append(text((bx2 + xend2 - gap) / 2, yu + bh + 24, "віддаються ОДРАЗУ → пропуск (зник кадр), та дані свіжі",
                  size=10, color=FIELD, bold=True))

    band, bw2, bh2 = textbox(W / 2, 285, "Для відео й голосу свіжість важливіша за повноту:\nкраще пропустити кадр, ніж застрягти на ньому",
                             size=11, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.3, pad=10)
    p.append(band)

    render(os.path.join(OUT, "head-of-line.svg"), W, H, *p,
           title="Блокування голови черги: чому реальний час іде по UDP")


# ── when-which: коли TCP, а коли UDP ──────────────────────────────────────────
# Ідея: дві колонки прикладів за одним критерієм — важливий кожен байт (TCP)
# проти важлива свіжість (UDP).

def fig_when_which():
    W, H = 700, 320
    p = []
    colw = 300
    lx, rx = 40, W - 40 - colw

    def column(x, title, col, fill, crit, items):
        b, bw, bh = textbox(x + colw / 2, 80, title, size=15, bold=True, color="#ffffff", fill=col, stroke=col, sw=1, min_w=colw)
        p.append(b)
        p.append(text(x + colw / 2, 116, crit, size=11, color=col, bold=True))
        y = 150
        for it in items:
            p.append(circle(x + 18, y - 4, 3, fill=col, stroke=col, sw=1))
            p.append(text(x + 34, y, it, size=11.5, color=INK, anchor="start"))
            y += 30

    column(lx, "TCP", FIELD, "#eef6ef", "важливий кожен байт",
           ["команди керування", "файли й прошивки", "веб (HTTP)", "MQTT — IoT-телеметрія", "будь-що, де втрата фатальна"])
    column(rx, "UDP", GOLD, "#fff7e0", "важлива свіжість",
           ["потокове відео й голос", "стан гри", "жива часта телеметрія", "широкомовлення", "старі дані вже не потрібні"])

    render(os.path.join(OUT, "when-which.svg"), W, H, *p,
           title="Коли TCP, а коли UDP")


# ── same-choice-code: той самий вибір — у коді ────────────────────────────────
# Ідея: одна задача, два класи. WiFiClient (TCP) ховає з'єднання й ретраї;
# WiFiUDP шле й не чекає. Дилема зводиться до вибору класу.

def fig_same_choice_code():
    W, H = 700, 280
    p = []
    cw, ch = 280, 150
    ly, ry = 70, 70
    lx, rx = 40, W - 40 - cw

    # ліворуч — TCP
    p.append(rect(lx, ly, cw, ch, fill="#eef6ef", stroke=FIELD, sw=1.8))
    p.append(text(lx + cw / 2, ly + 26, "надійно — TCP", size=14, color=FIELD, bold=True))
    p.append(text(lx + 18, ly + 56, "WiFiClient tcp;", size=12, color=INK, anchor="start"))
    p.append(text(lx + 18, ly + 80, "tcp.connect(ip, 1883);", size=12, color=INK, anchor="start"))
    p.append(text(lx + 18, ly + 104, "tcp.print(cmd);", size=12, color=INK, anchor="start"))
    p.append(text(lx + cw / 2, ly + ch - 14, "з'єднання, ACK, порядок — усередині", size=10, color=MUTED, italic=True))

    # праворуч — UDP
    p.append(rect(rx, ry, cw, ch, fill="#fff7e0", stroke=GOLD, sw=1.8))
    p.append(text(rx + cw / 2, ry + 26, "швидко — UDP", size=14, color=GOLD, bold=True))
    p.append(text(rx + 18, ry + 56, "WiFiUDP udp;", size=12, color=INK, anchor="start"))
    p.append(text(rx + 18, ry + 80, "udp.beginPacket(ip, port);", size=12, color=INK, anchor="start"))
    p.append(text(rx + 18, ry + 104, "udp.write(data, len);", size=12, color=INK, anchor="start"))
    p.append(text(rx + cw / 2, ry + ch - 14, "шлеш і не чекаєш", size=10, color=MUTED, italic=True))

    p.append(text(W / 2, H - 24, "одна задача — два транспорти; глибока дилема зводиться до вибору класу",
                  size=11, color=INK, italic=True, bold=True))

    render(os.path.join(OUT, "same-choice-code.svg"), W, H, *p,
           title="Той самий вибір — тепер у коді")


if __name__ == "__main__":
    fig_two_services()
    fig_handshake()
    fig_tcp_reliable()
    fig_udp()
    fig_head_of_line()
    fig_when_which()
    fig_same_choice_code()
    print("OK: figures written to", OUT)
