# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"


# ── 1. Два єдино можливі способи впоратися з другою копією ──────────────────
def fig_two_strategies():
    W, H = 1220, 590
    p = []

    def column(px, title, tcolor, rows, cost, cost_fill, cost_stroke):
        pw = 540
        py, ph = 55, 480
        out = [rect(px, py, pw, ph, fill=BG, stroke=tcolor, sw=2.0, rx=12),
               text(px + pw / 2, py + 34, title, size=15, bold=True, color=tcolor)]
        bx, bw = px + 25, pw - 50
        for i, (s, fill, stroke) in enumerate(rows):
            cy = py + 92 + i * 92
            out.append(fitbox(bx, cy - 26, bw, 52, s, size=13, fill=fill, stroke=stroke, sw=1.6))
            if i < len(rows) - 1:
                out.append(arrow(px + pw / 2, cy + 31, px + pw / 2, cy + 61, color=MUTED, sw=1.6))
        out.append(fitbox(bx, py + 400, bw, 60, cost, size=12.5,
                          fill=cost_fill, stroke=cost_stroke, sw=1.8))
        return out

    p += column(30, "клієнт питає  —  NFSv3", NEG,
                [("клієнт має копію файлу\nі довіряє їй, поки не спливе таймер", BLUE_FILL, NEG),
                 ("файл змінили на сервері —\nсповіщення не буде, сервер не пам'ятає нікого", FILL, LINE),
                 ("клієнт упевнено відповідає застарілим\nусе вікно між перевірками", RED_FILL, POS),
                 ("таймер сплив → запит атрибутів →\nкеш викинуто, дані знову свіжі", FILL, LINE)],
                "вікно застарілості = період перевірки\nсервер не коштує нічого, клієнт платить обмінами",
                WARM_FILL, WARM)

    p += column(650, "сервер каже  —  SMB, делегації NFSv4", FIELD,
                [("клієнт має копію\nі виданий сервером дозвіл кешувати", GREEN_FILL, FIELD),
                 ("той самий файл відкриває інший клієнт", FILL, LINE),
                 ("сервер надсилає власникові копії\nвідкликання дозволу", GREEN_FILL, FIELD),
                 ("той дописує накопичене — і лише тоді\nдругий клієнт отримує відповідь", FILL, LINE)],
                "вікно застарілості ≈ 0\nсервер пам'ятає всіх і мусить достукатися до кожного",
                WARM_FILL, WARM)

    render(os.path.join(IMG, 'two-strategies.svg'), W, H, *p,
           title="Друга копія правди: питати самому або чекати, поки скажуть")


# ── спільна розкладка «письменник — сервер — читач» ─────────────────────────
AX = 610          # вісь сервера
LX, LW = 40, 330  # ліва колонка
RX, RW = 850, 330  # права колонка
BH = 46


def lbox(cy, s, fill=FILL, stroke=LINE):
    return fitbox(LX, cy - BH / 2, LW, BH, s, size=12.5, fill=fill, stroke=stroke, sw=1.6)


def rbox(cy, s, fill=FILL, stroke=LINE):
    return fitbox(RX, cy - BH / 2, RW, BH, s, size=12.5, fill=fill, stroke=stroke, sw=1.6)


def alabel(cx, cy, lines, size=12, color=MUTED):
    if isinstance(lines, str):
        lines = [lines]
    first = cy - 13 - (len(lines) - 1) * 1.3 * size
    return mtext(cx, first, lines, size=size, color=color)


def to_server_left(cy, lines, color=LINE):
    """Стрілка від лівого клієнта до осі сервера."""
    return [arrow(LX + LW + 8, cy, AX - 8, cy, color=color, sw=2.0),
            alabel((LX + LW + 8 + AX - 8) / 2, cy, lines)]


def from_server_left(cy, lines, color=LINE):
    return [arrow(AX - 8, cy, LX + LW + 8, cy, color=color, sw=2.0),
            alabel((LX + LW + 8 + AX - 8) / 2, cy, lines)]


def to_server_right(cy, lines, color=LINE):
    return [arrow(RX - 8, cy, AX + 8, cy, color=color, sw=2.0),
            alabel((RX - 8 + AX + 8) / 2, cy, lines)]


def from_server_right(cy, lines, color=LINE):
    return [arrow(AX + 8, cy, RX - 8, cy, color=color, sw=2.0),
            alabel((RX - 8 + AX + 8) / 2, cy, lines)]


def axis(y1, y2):
    return line(AX, y1, AX, y2, color=MUTED, sw=2.0, dash="7 6")


# ── 2. Close-to-open: коли контракт діє і коли мовчить ──────────────────────
def fig_close_to_open():
    W, H = 1220, 900
    p = []

    p.append(fitbox(LX, 52, LW, 40, "клієнт-письменник", size=13.5, bold=True,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(AX - 105, 52, 210, 40, "сервер", size=13.5, bold=True,
                    fill=WARM_FILL, stroke=WARM, sw=1.8))
    p.append(fitbox(RX, 52, RW, 40, "клієнт-читач", size=13.5, bold=True,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))

    p.append(axis(100, 830))

    # сценарій, у якому контракт діє
    y = 150
    p.append(lbox(y, "write() двічі —\nдані лишаються в кеші письменника"))
    p.append(alabel((LX + LW + AX) / 2, y + 8, ["на сервер не летить нічого"], color=POS))

    y += 92
    p.append(lbox(y, "close()", fill=GREEN_FILL, stroke=FIELD))
    p += to_server_left(y, ["усі накопичені сторінки", "і COMMIT — дані на сервері"], color=FIELD)

    y += 92
    p.append(rbox(y, "open() — уже після чужого close()"))
    p += to_server_right(y, ["запит атрибутів:", "чи змінився час зміни?"])

    y += 92
    p.append(rbox(y, "кеш даних цього файлу викинуто"))
    p += from_server_right(y, ["новий час зміни й розмір"])

    y += 92
    p.append(rbox(y, "read() — свіжі дані", fill=GREEN_FILL, stroke=FIELD))
    p += to_server_right(y, ["читання з сервера"], color=FIELD)

    y += 76
    p.append(fitbox(140, y - 24, 940, 48,
                    "письменник закрив раніше, ніж читач відкрив — це і є весь контракт",
                    size=13.5, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    # сценарій, у якому гарантії немає
    y += 92
    p.append(rbox(y, "open() — читач відкрив ПЕРШИМ\nі тримає файл відкритим"))
    y += 88
    p.append(lbox(y, "write() — у кеші письменника"))
    p.append(rbox(y, "read() — зі свого кешу, старі дані", fill=RED_FILL, stroke=POS))
    p.append(alabel((LX + LW + AX) / 2, y + 8, ["жодного обміну з жодного боку"], color=POS))

    y += 76
    p.append(fitbox(140, y - 24, 940, 48,
                    "поки обидва тримають файл відкритим, застарілість обмежена лише таймером — до 60 с",
                    size=13.5, bold=True, fill=RED_FILL, stroke=POS, sw=1.8))

    render(os.path.join(IMG, 'close-to-open.svg'), W, H, *p,
           title="Гарантія NFS прив'язана до пари подій, а не до часу")


# ── 3. Відкликання оренди в SMB ─────────────────────────────────────────────
def fig_lease_break():
    W, H = 1220, 830
    p = []

    p.append(fitbox(LX, 52, LW, 40, "клієнт A", size=13.5, bold=True,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(AX - 105, 52, 210, 40, "сервер", size=13.5, bold=True,
                    fill=WARM_FILL, stroke=WARM, sw=1.8))
    p.append(fitbox(RX, 52, RW, 40, "клієнт B", size=13.5, bold=True,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))

    p.append(axis(100, 690))

    y = 150
    p.append(lbox(y, "open()"))
    p += to_server_left(y, ["створення дескриптора", "і прохання про оренду"])

    y += 92
    p.append(lbox(y, "кешує читання, записи й дескриптор", fill=GREEN_FILL, stroke=FIELD))
    p += from_server_left(y, ["більше ніхто файлу не тримає —", "оренда видана"], color=FIELD)

    y += 92
    p.append(lbox(y, "write() багато разів — усе в кеші"))
    p.append(alabel((LX + LW + AX) / 2, y + 8, ["тиша: обмінів немає взагалі"], color=FIELD))

    y += 92
    p.append(rbox(y, "open() того самого файлу"))
    p += to_server_right(y, ["сервер бачить збіг", "і затримує відповідь"])

    y += 92
    p.append(lbox(y, "дописує накопичене й знижує рівень", fill=WARM_FILL, stroke=WARM))
    p += from_server_left(y, ["відкликання оренди"], color=POS)

    y += 92
    p.append(rbox(y, "бачить усе, що записав A", fill=GREEN_FILL, stroke=FIELD))
    p += from_server_right(y, ["лише тепер — відповідь"], color=FIELD)

    y += 88
    p.append(fitbox(90, y - 34, 1040, 68,
                    "У NFSv3 стрілки відкликання не існує взагалі: сервер не пам'ятає, кому що віддав,\n"
                    "і не має зворотного шляху до клієнта. Замість неї там працює таймер на клієнті.",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.8))

    render(os.path.join(IMG, 'lease-break.svg'), W, H, *p,
           title="Відкликання дозволу: правильність відновлюють до того, як другий отримає відповідь")


# -- 4. Dvi liniyi (vstavka hist) --------------------------------------------
def fig_two_lineages():
    W, H = 1240, 800
    AXX = 620
    CW = 500
    p = [text(AXX, 34, "\u0434\u0432\u0430 \u0440\u043e\u0434\u043e\u0432\u043e\u0434\u0438, \u0449\u043e \u043d\u0456\u043a\u043e\u043b\u0438 \u043d\u0435 \u043c\u0430\u043b\u0438 \u0441\u043f\u0456\u043b\u044c\u043d\u043e\u0433\u043e \u043f\u0440\u0435\u0434\u043a\u0430",
              size=15, bold=True, color=INK),
         text(AXX - 300, 62, "\u043b\u0456\u043d\u0456\u044f NFS  \u2014  Unix, RPC, \u0432\u0456\u0434\u043a\u0440\u0438\u0442\u0430 \u0441\u043f\u0435\u0446\u0438\u0444\u0456\u043a\u0430\u0446\u0456\u044f",
              size=13, bold=True, color=NEG),
         text(AXX + 300, 62, "\u043b\u0456\u043d\u0456\u044f SMB  \u2014  DOS, NetBIOS, \u0437\u0430\u043a\u0440\u0438\u0442\u0438\u0439 \u043f\u0440\u043e\u0434\u0443\u043a\u0442",
              size=13, bold=True, color=POS)]

    rows = [
        ("1983", "R", "IBM, \u0411\u0430\u0440\u0440\u0456 \u0424\u0430\u0439\u0491\u0435\u043d\u0431\u0430\u0443\u043c: \u0432\u0456\u0434\u0434\u0430\u043b\u0435\u043d\u0438\u0439 \u0434\u043e\u0441\u0442\u0443\u043f\n\u0434\u043b\u044f INT 21h \u0443 PC DOS; \u0441\u043f\u0435\u0440\u0448\u0443 \u00abBAF\u00bb"),
        ("1984", "L", "Sun Microsystems: NFS \u0434\u043b\u044f \u043f\u0430\u0440\u043a\u0443\n\u0431\u0435\u0437\u0434\u0438\u0441\u043a\u043e\u0432\u0438\u0445 \u0440\u043e\u0431\u043e\u0447\u0438\u0445 \u0441\u0442\u0430\u043d\u0446\u0456\u0439"),
        ("1985", "L", "\u0434\u043e\u043f\u043e\u0432\u0456\u0434\u044c \u043d\u0430 USENIX; \u0441\u043f\u0435\u0446\u0438\u0444\u0456\u043a\u0430\u0446\u0456\u044e\n\u043f\u0440\u043e\u0442\u043e\u043a\u043e\u043b\u0443 \u043e\u043f\u0443\u0431\u043b\u0456\u043a\u043e\u0432\u0430\u043d\u043e"),
        ("1987", "R", "Microsoft \u0456 3Com: SMB \u0443 LAN Manager\n\u0434\u043b\u044f OS/2 \u043f\u043e\u0432\u0435\u0440\u0445 NetBIOS"),
        ("1989", "L", "RFC 1094 \u2014 NFSv2; \u043f\u0440\u043e\u0442\u043e\u043a\u043e\u043b \u0441\u0442\u0430\u0432\n\u0447\u0443\u0436\u0438\u043c \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u043e\u043c, \u043d\u0435 \u0432\u043b\u0430\u0441\u043d\u0456\u0441\u0442\u044e Sun"),
        ("1992", "R", "\u0415\u043d\u0434\u0440\u044e \u0422\u0440\u0456\u0434\u0436\u0435\u043b\u043b \u0432\u0438\u043f\u0443\u0441\u043a\u0430\u0454 Samba:\n\u043f\u0440\u043e\u0442\u043e\u043a\u043e\u043b \u0432\u0456\u0434\u043d\u043e\u0432\u043b\u0435\u043d\u043e \u0437 \u0442\u0440\u0430\u0444\u0456\u043a\u0443"),
        ("1995", "L", "RFC 1813 \u2014 NFSv3: 64 \u0431\u0456\u0442\u0438, TCP,\n\u0430\u0441\u0438\u043d\u0445\u0440\u043e\u043d\u043d\u0438\u0439 \u0437\u0430\u043f\u0438\u0441"),
        ("1996", "R", "\u0443 \u0432\u0456\u0434\u043f\u043e\u0432\u0456\u0434\u044c \u043d\u0430 \u0430\u043d\u043e\u043d\u0441 WebNFS\nMicrosoft \u043f\u0435\u0440\u0435\u0439\u043c\u0435\u043d\u043e\u0432\u0443\u0454 SMB 1.0 \u043d\u0430 CIFS"),
        ("2003", "L", "RFC 3530 \u2014 NFSv4: \u0441\u0435\u0440\u0432\u0435\u0440 \u043d\u0430\u0440\u0435\u0448\u0442\u0456\n\u0437\u0433\u0430\u0434\u0443\u0454 \u043a\u043b\u0456\u0454\u043d\u0442\u0456\u0432"),
        ("2006", "R", "SMB2 \u0443 Windows Vista:\n\u043f\u043e\u043d\u0430\u0434 \u0441\u043e\u0442\u043d\u044f \u043a\u043e\u043c\u0430\u043d\u0434 \u2192 \u0434\u0435\u0432'\u044f\u0442\u043d\u0430\u0434\u0446\u044f\u0442\u044c"),
    ]

    top, step = 96, 68
    p.append(line(AXX, top - 14, AXX, top + step * len(rows) - 22, color=MUTED, sw=1.6))
    for i, (year, side, txt) in enumerate(rows):
        cy = top + i * step
        fill, stroke = (BLUE_FILL, NEG) if side == "L" else (RED_FILL, POS)
        if side == "L":
            p.append(fitbox(AXX - 66 - CW, cy - 24, CW, 50, txt, size=12.5,
                            fill=fill, stroke=stroke, sw=1.6))
            p.append(line(AXX - 66, cy, AXX - 30, cy, color=stroke, sw=1.4))
        else:
            p.append(fitbox(AXX + 66, cy - 24, CW, 50, txt, size=12.5,
                            fill=fill, stroke=stroke, sw=1.6))
            p.append(line(AXX + 30, cy, AXX + 66, cy, color=stroke, sw=1.4))
        p.append(circle(AXX, cy, 4.5, fill=INK, stroke=INK, sw=1.0))
        p.append(text(AXX, cy - 13, year, size=12, bold=True, color=MUTED))

    p.append(fitbox(150, top + step * len(rows) + 4, 940, 64,
                    "\u0416\u043e\u0434\u043d\u0430 \u043f\u043e\u0434\u0456\u044f \u043b\u0456\u0432\u043e\u0457 \u043a\u043e\u043b\u043e\u043d\u043a\u0438 \u043d\u0435 \u0454 \u0432\u0456\u0434\u043f\u043e\u0432\u0456\u0434\u0434\u044e \u043d\u0430 \u043f\u043e\u0434\u0456\u044e \u043f\u0440\u0430\u0432\u043e\u0457, \u043e\u043a\u0440\u0456\u043c \u043e\u0434\u043d\u0456\u0454\u0457:\n\u043f\u0435\u0440\u0435\u0439\u043c\u0435\u043d\u0443\u0432\u0430\u043d\u043d\u044f 1996 \u0440\u043e\u043a\u0443, \u0434\u0435 \u043c\u0430\u0440\u043a\u0435\u0442\u0438\u043d\u0433 \u043e\u0434\u043d\u0456\u0454\u0457 \u043b\u0456\u043d\u0456\u0457 \u0432\u0456\u0434\u0440\u0435\u0430\u0433\u0443\u0432\u0430\u0432 \u043d\u0430 \u0430\u043d\u043e\u043d\u0441 \u0456\u043d\u0448\u043e\u0457.",
                    size=12.5, fill=WARM_FILL, stroke=WARM, sw=1.8))

    render(os.path.join(IMG, 'two-lineages.svg'), W, H, *p,
           title="\u0414\u0432\u0456 \u043d\u0435\u0437\u0430\u043b\u0435\u0436\u043d\u0456 \u043b\u0456\u043d\u0456\u0457 \u043c\u0435\u0440\u0435\u0436\u0435\u0432\u043e\u0433\u043e \u0434\u043e\u0441\u0442\u0443\u043f\u0443 \u0434\u043e \u0444\u0430\u0439\u043b\u0456\u0432, 1983-2006")



# ── 5. Три яруси, з яких складається чинний контракт (вставка api) ─────────
def fig_contract_layers():
    W, H = 1240, 680
    p = []

    p.append(text(210, 78, "КЛІЄНТ просить", size=15, bold=True, color=NEG))
    p.append(fitbox(40, 92, 340, 130,
                    "vers=4.2\nrw\nsec=krb5p\nnconnect=8\nactimeo=30",
                    size=13.5, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(text(210, 240, "рядок у /etc/fstab", size=12.5, color=MUTED))

    p.append(text(1030, 78, "СЕРВЕР дозволяє", size=15, bold=True, color=FIELD))
    p.append(fitbox(860, 92, 340, 130,
                    "rw\nroot_squash\nsec=krb5\nsync\nno_subtree_check",
                    size=13.5, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(text(1030, 240, "рядок у /etc/exports", size=12.5, color=MUTED))

    p.append(text(620, 78, "по дроту", size=15, bold=True, color=INK))
    p.append(fitbox(460, 112, 320, 92,
                    "узгодження версії,\nрозмірів читання-запису\nта способу автентифікації",
                    size=13, fill=FILL, stroke=LINE, sw=1.8))

    p.append(arrow(392, 158, 452, 158, color=NEG, sw=2.0))
    p.append(arrow(848, 158, 788, 158, color=FIELD, sw=2.0))
    p.append(arrow(620, 212, 620, 262, color=INK, sw=2.0))

    p.append(fitbox(40, 270, 1160, 96,
                    "ЧИННИЙ КОНТРАКТ — перетин усіх трьох, і побачити його можна лише тут:\n"
                    "/proc/mounts   ·   findmnt   ·   nfsstat -m",
                    size=14, fill=WARM_FILL, stroke=WARM, sw=2.0, bold=True))

    p.append(text(620, 412, "звідки беруться три найчастіші несподіванки", size=14, bold=True, color=MUTED))

    cases = [
        (40, "просили vers=4.2\nсервер уміє 4.1\n→ чинне vers=4.1\nтиха підміна, монтування вдалося",
         WARM_FILL, WARM),
        (450, "просили rw\nв експорті ro\n→ монтується як завжди,\nа перший запис дає EROFS",
         RED_FILL, POS),
        (860, "просили sec=sys\nв експорті sec=krb5\n→ сервер відмовляє,\nмонтування не виникає взагалі",
         RED_FILL, POS),
    ]
    for x, s, fill, stroke in cases:
        p.append(fitbox(x, 436, 340, 170, s, size=13, fill=fill, stroke=stroke, sw=1.8))

    render(os.path.join(IMG, 'contract-layers.svg'), W, H, *p,
           title="Чинні опції монтування — не те, що написали у fstab")


# ── 6. Драбина таймаутів: timeo, retrans і розвилка hard/soft ──────────────
def fig_timeout_ladder():
    W, H = 1240, 520
    p = []

    AY = 210
    p.append(line(90, AY, 700, AY, color=MUTED, sw=2.0))

    marks = [
        (120, "0 с", "запит пішов"),
        (330, "60 с", "тиша → повтор №1"),
        (610, "180 с", "тиша → повтор №2"),
    ]
    for x, t, s in marks:
        p.append(circle(x, AY, 5.5, fill=INK, stroke=INK, sw=1.0))
        p.append(text(x, AY - 26, t, size=14, bold=True))
        p.append(text(x, AY + 34, s, size=12.5, color=MUTED))

    p.append(fitbox(90, AY + 58, 610, 62,
                    "timeo=600 децисекунд = 60 с; після кожного повтору чекання росте\n"
                    "рівно на timeo (лінійний приріст), стеля — 600 с",
                    size=12.5, fill=FILL, stroke=LINE, sw=1.6))

    p.append(arrow(700, AY, 756, AY, color=INK, sw=2.0))
    p.append(fitbox(760, AY - 46, 180, 92,
                    "retrans=2\nвичерпано:\n«server not\nresponding»",
                    size=12.5, fill=WARM_FILL, stroke=WARM, sw=1.8))

    p.append(arrow(946, AY - 22, 996, 118, color=NEG, sw=2.0))
    p.append(fitbox(1000, 62, 210, 116,
                    "hard\n(типове для NFS)\nповторювати далі:\nпроцес у стані D,\nжодного байта не втрачено",
                    size=12, fill=BLUE_FILL, stroke=NEG, sw=1.8))

    p.append(arrow(946, AY + 22, 996, 322, color=POS, sw=2.0))
    p.append(fitbox(1000, 268, 210, 130,
                    "soft → EIO\nsofterr → ETIMEDOUT\nперша відмова аж\nна третій хвилині,\nа записане в кеші\nвіддати вже нікуди",
                    size=12, fill=RED_FILL, stroke=POS, sw=1.8))

    p.append(fitbox(90, 400, 780, 66,
                    "У клієнта cifs типове значення протилежне — soft: програма дістає помилку замість того,\n"
                    "щоб чекати повернення сервера. Це найчастіша причина «різної» поведінки NFS і SMB при обриві.",
                    size=12.5, fill=WARM_FILL, stroke=WARM, sw=1.8))

    render(os.path.join(IMG, 'timeout-ladder.svg'), W, H, *p,
           title="Скільки триває мовчання сервера, перш ніж воно стане подією")


fig_two_strategies()
fig_close_to_open()
fig_lease_break()
fig_two_lineages()
fig_contract_layers()
fig_timeout_ladder()
print("ok")


# ── Проба монтування: два канали й один секундомір ──────────────────────────
def fig_one_clock():
    W, H = 1220, 700
    p = []

    # панель А: два канали
    p.append(text(610, 46, "два канали: дані йдуть через сервер, команди — напряму",
                  size=14.5, bold=True))

    p.append(fitbox(40, 120, 260, 76, "машина A\nписьменник", size=13.5, bold=True,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(470, 120, 280, 76, "сервер\nспільний каталог", size=13.5, bold=True,
                    fill=WARM_FILL, stroke=WARM, sw=1.8))
    p.append(fitbox(920, 120, 260, 76, "машина B\nчитач", size=13.5, bold=True,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))

    p.append(arrow(310, 158, 460, 158, color=LINE, sw=2.0))
    p.append(mtext(385, 136, ["створює файл"], size=11.5, color=MUTED))
    p.append(arrow(760, 158, 910, 158, color=LINE, sw=2.0))
    p.append(mtext(835, 136, ["читає каталог"], size=11.5, color=MUTED))

    p.append(line(170, 196, 170, 300, color=FIELD, sw=2.0, dash="7 5"))
    p.append(line(1050, 196, 1050, 300, color=FIELD, sw=2.0, dash="7 5"))
    p.append(arrow(610, 300, 176, 300, color=FIELD, sw=2.0))
    p.append(arrow(610, 300, 1044, 300, color=FIELD, sw=2.0))
    p.append(mtext(610, 334,
                   ["керувальний канал: пряме TCP-з'єднання A ↔ B,",
                    "повз сервер і повз спільний каталог — тут ідуть команди, а не дані"],
                   size=12, color=FIELD))

    # панель Б: секундомір читача
    p.append(text(610, 400, "одне вимірювання: обидва відліки — на годиннику читача",
                  size=14.5, bold=True))

    p.append(line(300, 456, 870, 456, color=MUTED, sw=1.6))
    p.append(line(300, 456, 300, 472, color=MUTED, sw=1.6))
    p.append(line(870, 456, 870, 472, color=MUTED, sw=1.6))
    p.append(mtext(585, 438,
                   ["stat() кожні 50 мс — усе ще ENOENT: негативний запис у кеші чинний"],
                   size=12, color=MUTED))

    p.append(line(120, 500, 1120, 500, color=LINE, sw=2.0))
    for x in range(320, 880, 62):
        p.append(line(x, 500, x, 513, color=MUTED, sw=1.5))

    p.append(line(210, 478, 210, 522, color=NEG, sw=2.6))
    p.append(mtext(210, 466, ["t₀"], size=14, color=NEG, bold=True))
    p.append(mtext(210, 546, ["прийшла відповідь", "«файл створено»"], size=11.5, color=NEG))

    p.append(line(930, 478, 930, 522, color=FIELD, sw=2.6))
    p.append(mtext(930, 466, ["t₁"], size=14, color=FIELD, bold=True))
    p.append(mtext(930, 546, ["stat() повернув 0", "файл нарешті видно"], size=11.5, color=FIELD))

    p.append(arrow(570, 594, 216, 594, color=WARM, sw=2.0))
    p.append(arrow(570, 594, 924, 594, color=WARM, sw=2.0))
    p.append(mtext(570, 624,
                   ["Δ = t₁ − t₀ — єдине число, що є результатом проби"],
                   size=13, color=WARM, bold=True))
    p.append(mtext(610, 662,
                   ["годинник машини A в обчисленні не бере участі — тому його розходження",
                    "з годинником машини B нікуди не входить"],
                   size=12, color=MUTED))

    render(os.path.join(IMG, 'one-clock.svg'), W, H, *p,
           title="Проба монтування: команди повз спільний каталог, час — на одному годиннику")


fig_one_clock()
