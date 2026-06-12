# -*- coding: utf-8 -*-
"""
SVG-фігури для ⚙️-вставки §3.9.4a — «CRC у коді: бітовий цикл, таблична
версія, вибір полінома (CRC-8/16/32)».

ОКРЕМИЙ генератор лише цієї вставки (головний figs.py розділу не чіпаємо).
Чистий Python без залежностей. Вивід → ./img/.
Стиль за AUTHORING §9: білий фон; «1»/«+» червоний, «0»/«−» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.
Нумерація підписів — §3.9.4a.k → файли fig-r09-s4a-k-*.

Фігури:
  fig-r09-s4a-1-bitloop.svg   — бітовий цикл: вдвигаємо біти, на «1» зверху XOR-имо поліном
  fig-r09-s4a-2-table.svg     — таблична версія: 8 бітових кроків згорнуто в одне читання таблиці
  fig-r09-s4a-3-params.svg    — вибір полінома й параметри: ширина→ловить, init/refin/xorout
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
VIOL  = "#7a3ea8"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'  <marker id="aViol" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{VIOL}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", AMBER: "aAmber", VIOL: "aViol"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, color=INK, w=2.4, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def bitcell(x, y, val, w=26, h=26, on=RED, off=BLUE, faint=False):
    """Одна клітинка біта: 1 — червона рамка, 0 — синя; faint — приглушено."""
    col = on if val == "1" else off
    fill = "#fff"
    if faint:
        col = FAINT
    s = rect(x, y, w, h, fill, col, 2 if not faint else 1.4, 4)
    s += text(x + w/2, y + h*0.72, val, 14, col if not faint else GREY, "middle", "bold")
    return s


# ── Фігура 1: бітовий цикл — ділення многочлена як код ────────────────────────
def fig1_bitloop():
    W, H = 900, 712
    b = header(W, H)
    b += text(W/2, 30,
              "Бітовий CRC: те саме ділення на многочлен (§3.9.4), але крок за кроком у коді",
              16, INK, "middle", "bold")
    b += text(W/2, 50,
              "Приклад: CRC-8, поліном 0x07 (x⁸+x²+x+1), регістр 8 біт, обробляємо один байт 0x31",
              11.5, GREY, "middle", style="italic")

    cw = 30
    x0 = 120
    # ── зліва-зверху: правило одного кроку ──
    rx, ry, rw, rh = 40, 78, 320, 150
    b += rect(rx, ry, rw, rh, "#f4f7ff", BLUE, 1.8, 9)
    b += text(rx + rw/2, ry + 22, "Правило одного такту циклу", 13, BLUE, "middle", "bold")
    b += mono(rx + 16, ry + 48, "msb = старший біт crc", 12, INK)
    b += mono(rx + 16, ry + 68, "crc <<= 1                 // зсув уліво", 12, INK)
    b += mono(rx + 16, ry + 88, "if (msb == 1)", 12, RED)
    b += mono(rx + 34, ry + 108, "crc ^= 0x07            // XOR поліном", 12, RED)
    b += text(rx + 16, ry + 132, "Зсув = «опустити наступний біт»;", 10.5, GREY)
    b += text(rx + 16, ry + 146, "XOR на 1 угорі = «відняти дільник».", 10.5, GREY)

    # ── справа-зверху: чому саме так (зв'язок з діленням) ──
    qx, qy, qw, qh = 400, 78, 460, 150
    b += rect(qx, qy, qw, qh, "#f0fff2", GREEN, 1.8, 9)
    b += text(qx + qw/2, qy + 22, "Звідки це: ділення в стовпчик над GF(2)", 13, GREEN, "middle", "bold")
    b += text(qx + 16, qy + 46, "У §3.9.4 CRC — це остача від ділення повідомлення", 11, INK)
    b += text(qx + 16, qy + 64, "на многочлен. Над GF(2) віднімання = XOR (§3.9.4m),", 11, INK)
    b += text(qx + 16, qy + 82, "а «чи ділиться» вирішує лише старший біт.", 11, INK)
    b += text(qx + 16, qy + 104, "Тож «школярське» ділення стовпчиком стискається", 11, INK)
    b += text(qx + 16, qy + 122, "до двох дій: зсунути регістр і, якщо зверху була 1,", 11, INK)
    b += text(qx + 16, qy + 140, "XOR-нути поліном. Більше нічого.", 11, INK)

    # ── трасування: 8 кроків над байтом 0x31 = 0011 0001 ──
    b += text(W/2, 262, "Трасування восьми тактів над байтом 0x31 = 0011 0001 (старший біт — лівий)",
              12.5, INK, "middle", "bold")

    crc_states = [
        "00000000",  # початок (init=0 для прикладу)
    ]
    poly = 0x07
    crc = 0x00
    data = 0x31
    feed_bits = []
    # імітуємо CRC-8 (без рефлексій): на кожному біті даних — вдвигаємо біт,
    # для наочності тут показуємо класичну «MSB-first» побітову схему з домішуванням байта.
    crc = data  # одразу заводимо байт у 8-бітний регістр і проганяємо 8 тактів
    rows = []
    for i in range(8):
        msb = (crc >> 7) & 1
        crc = (crc << 1) & 0xFF
        if msb:
            crc ^= poly
        rows.append((i + 1, msb, format(crc, "08b")))

    # таблиця кроків
    tx0 = 80
    ty0 = 290
    rowh = 36
    colb = 360  # початок бітового регістру
    # шапка
    b += text(tx0 + 18, ty0 + 18, "такт", 11, GREY, "start", "bold")
    b += text(tx0 + 86, ty0 + 18, "верхній біт", 11, GREY, "start", "bold")
    b += text(colb + 8*cw/2, ty0 + 18, "регістр CRC після такту (8 біт)", 11, GREY, "middle", "bold")
    b += text(colb + 8*cw + 60, ty0 + 18, "дія", 11, GREY, "middle", "bold")

    y = ty0 + 30
    for (k, msb, bits) in rows:
        # зебра
        if k % 2 == 0:
            b += rect(tx0, y, W - 2*tx0 + 40, rowh - 4, "#fafafa", "#fafafa", 0, 4)
        b += text(tx0 + 28, y + 24, str(k), 13, INK, "middle", "bold")
        mcol = RED if msb else BLUE
        b += text(tx0 + 118, y + 24, ("1" if msb else "0"), 14, mcol, "middle", "bold")
        # біти регістру
        for j, ch in enumerate(bits):
            b += bitcell(colb + j*cw, y + 4, ch, cw - 4, rowh - 12)
        # дія
        if msb:
            b += text(colb + 8*cw + 60, y + 24, "зсув + XOR 0x07", 11, RED, "middle", "bold")
        else:
            b += text(colb + 8*cw + 60, y + 24, "лише зсув", 11, BLUE, "middle")
        y += rowh

    # результат
    res = rows[-1][2]
    by = y + 6
    b += rect(tx0, by, W - 2*tx0 + 40, 46, "#f0fff2", GREEN, 1.8, 8)
    b += text(tx0 + 16, by + 29, "Остача = CRC-8 байта:", 12.5, GREEN, "start", "bold")
    b += mono(tx0 + 220, by + 30, f"0b{res} = 0x{int(res,2):02X}", 14, GREEN, "start", "bold")
    b += text(W - tx0 + 24, by + 29,
              "для кадру з кількох байтів цикл просто повторюють, заводячи кожен наступний байт",
              10.5, GREY, "end", style="italic")
    save("fig-r09-s4a-1-bitloop.svg", b)


# ── Фігура 2: таблична версія — 8 бітових кроків = одне читання таблиці ────────
def fig2_table():
    W, H = 900, 600
    b = header(W, H)
    b += text(W/2, 30,
              "Таблична версія: вісім бітових тактів згорнуто в одне читання таблиці",
              16, INK, "middle", "bold")
    b += text(W/2, 50,
              "Ідея Сарвейта (1988): наслідок восьми тактів залежить лише від байта зверху — тож порахуймо його заздалегідь",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: бітовий шлях (повільно) ──
    lx = 60
    b += rect(lx, 80, 360, 150, "#fff", GREY, 1.8, 9)
    b += text(lx + 180, 104, "Бітовий цикл — 8 тактів на байт", 13, GREY, "middle", "bold")
    yb = 124
    for i in range(8):
        cy = yb + i*12
        col = RED if i in (0, 3, 4) else BLUE
        b += circle(lx + 40, cy, 4.5, col, col, 1)
        b += text(lx + 56, cy + 4, f"такт {i+1}: зсув" + (" + XOR" if col == RED else ""),
                  10.5, INK if col == BLUE else RED)
    b += text(lx + 180, 226, "8 розгалужень «if msb» на кожен байт", 10, GREY, "middle", style="italic")

    # стрілка «згортаємо»
    b += arrow(430, 152, 490, 152, GREEN, 3)
    b += text(460, 138, "одне", 11, GREEN, "middle", "bold")
    b += text(460, 178, "читання", 11, GREEN, "middle", "bold")

    # ── праворуч: одне читання таблиці ──
    rx = 510
    b += rect(rx, 80, 330, 150, "#f0fff2", GREEN, 1.8, 9)
    b += text(rx + 165, 104, "Таблична версія — 1 крок на байт", 13, GREEN, "middle", "bold")
    b += mono(rx + 20, 132, "idx  = (crc >> 8) ^ byte", 12.5, INK)
    b += mono(rx + 20, 154, "crc  = (crc << 8) ^ T[idx]", 12.5, GREEN)
    b += text(rx + 20, 180, "T[256] — заздалегідь порахований CRC", 10.5, GREY)
    b += text(rx + 20, 195, "кожного з 256 значень байта.", 10.5, GREY)
    b += text(rx + 20, 214, "Жодних розгалужень у гарячому циклі.", 10.5, AMBER)

    # ── як народжується запис таблиці ──
    b += text(W/2, 268, "Як народжується один рядок таблиці T[i]: проганяємо «бітовим» циклом самé значення i",
              12.5, INK, "middle", "bold")

    # колонка: байт i  → 8 тактів  → T[i]
    cx0 = 90
    b += rect(cx0, 286, 150, 60, "#fff", VIOL, 2, 8)
    b += text(cx0 + 75, 310, "байт i", 13, VIOL, "middle", "bold")
    b += mono(cx0 + 75, 332, "0x00 … 0xFF", 12, GREY, "middle")

    b += arrow(cx0 + 150, 316, cx0 + 215, 316, INK, 2.4)
    b += rect(cx0 + 215, 286, 215, 60, "#f4f7ff", BLUE, 2, 8)
    b += text(cx0 + 215 + 107, 308, "бітовий цикл 8 разів", 12, BLUE, "middle", "bold")
    b += text(cx0 + 215 + 107, 328, "(той самий, що на Рис. 3.9.4a.1)", 9.5, GREY, "middle")

    b += arrow(cx0 + 430, 316, cx0 + 495, 316, INK, 2.4)
    b += rect(cx0 + 495, 286, 170, 60, "#f0fff2", GREEN, 2, 8)
    b += text(cx0 + 495 + 85, 308, "T[i] — 32 (чи 8/16) біт", 11.5, GREEN, "middle", "bold")
    b += text(cx0 + 495 + 85, 328, "запис у таблицю", 10, GREY, "middle")
    b += text(W/2, 360, "Це роблять один раз — на старті програми або на етапі компіляції; далі таблиця лежить готова.",
              10.5, GREY, "middle", style="italic")

    # ── фрагмент самої таблиці (реальні значення CRC-32, рефлексований, poly 0xEDB88320) ──
    b += text(W/2, 396, "Фрагмент готової таблиці (CRC-32, рефлексований варіант)", 12, INK, "middle", "bold")
    sample = [
        (0x00, 0x00000000), (0x01, 0x77073096), (0x02, 0xEE0E612C),
        (0x03, 0x990951BA), (0x04, 0x076DC419), (0x05, 0x706AF48F),
    ]
    txx = 150
    tyy = 414
    cwid = 100
    b += text(txx - 20, tyy + 18, "i", 11, GREY, "end", "bold")
    for j, (i, v) in enumerate(sample):
        x = txx + j*cwid
        b += rect(x, tyy, cwid - 12, 56, "#fcfcfc", FAINT, 1.4, 6)
        b += mono(x + (cwid-12)/2, tyy + 22, f"0x{i:02X}", 12, VIOL, "middle", "bold")
        b += mono(x + (cwid-12)/2, tyy + 44, f"0x{v:08X}", 11, INK, "middle")
    b += text(txx + 6*cwid - 12 + 18, tyy + 34, "… і так усі 256 рядків", 10.5, GREY, "start", style="italic")

    # ── підсумок-висновок ──
    by = 500
    b += rect(60, by, W - 120, 78, "#fff7ec", AMBER, 1.8, 9)
    b += text(80, by + 26, "Чим платимо й що виграємо:", 12.5, AMBER, "start", "bold")
    b += text(80, by + 48, "• Пам'ять: таблиця CRC-32 — це 256 × 4 = 1024 байти у Flash. Для CRC-8 — лише 256 байтів.",
              11, INK, "start")
    b += text(80, by + 66, "• Швидкість: ~ у 8 разів менше тактів і жодних гілок — на МК без апаратного CRC це найходовіший компроміс.",
              11, INK, "start")
    save("fig-r09-s4a-2-table.svg", b)


# ── Фігура 3: вибір полінома й «параметри», що ламають сумісність ─────────────
def fig3_params():
    W, H = 900, 640
    b = header(W, H)
    b += text(W/2, 30, "Вибір CRC: ширина вирішує, скільки помилок видно; параметри вирішують сумісність",
              16, INK, "middle", "bold")

    # ── зверху: три ширини й що вони ловлять ──
    cards = [
        ("CRC-8", "0x07", "8 біт", "короткі кадри: давачі по I²C/CAN,\nрядки конфігурації", BLUE,
         "ловить усі сплески ≤ 8 біт;\nхибний пропуск ≈ 1 на 2⁸"),
        ("CRC-16", "0x1021", "16 біт", "пакети поверх UART, Modbus,\nкарти пам'яті (§3.9.4)", GREEN,
         "усі сплески ≤ 16 біт;\nхибний пропуск ≈ 1 на 2¹⁶"),
        ("CRC-32", "0x04C11DB7", "32 біти", "Ethernet-кадри, ZIP/PNG,\nвеликі блоки сховища", VIOL,
         "усі сплески ≤ 32 біт;\nхибний пропуск ≈ 1 на 2³²"),
    ]
    cw = 270
    gap = 15
    x0 = (W - (cw*3 + gap*2)) / 2
    for i, (nm, poly, width, where, col, catch) in enumerate(cards):
        x = x0 + i*(cw + gap)
        b += rect(x, 60, cw, 168, "#fcfcfc", col, 2.2, 10)
        b += rect(x, 60, cw, 30, col, col, 0, 10)
        b += text(x + cw/2, 80, nm, 15, "#fff", "middle", "bold")
        b += mono(x + 16, 112, f"поліном {poly}", 12.5, col, "start", "bold")
        b += text(x + 16, 132, f"ширина остачі: {width}", 11, INK, "start")
        b += line(x + 14, 142, x + cw - 14, 142, FAINT, 1)
        b += text(x + 16, 160, "де у курсі:", 10.5, GREY, "start", "bold")
        for k, ln in enumerate(where.split("\n")):
            b += text(x + 16, 176 + k*15, ln, 10.5, INK, "start")
        b += text(x + 16, 210, "що ловить:", 10.5, GREY, "start", "bold")
        for k, ln in enumerate(catch.split("\n")):
            b += text(x + cw - 16, 196 + k*15, ln, 9.5, col, "end")

    b += text(W/2, 248,
              "Ширша остача — рідший хибний пропуск і довший гарантовано спійманий сплеск, але більше байтів і такти/таблиця.",
              11, GREY, "middle", style="italic")

    # ── середина: чому два «правильні» CRC-32 не сходяться — параметри ──
    b += text(W/2, 286, "Чому дві коректні реалізації CRC-32 дають різні числа: однакового полінома замало",
              13, INK, "middle", "bold")

    params = [
        ("init", "чим заряджено регістр\nперед першим байтом", "0xFFFFFFFF\nчи 0x00000000", RED),
        ("refin / refout", "чи перевертати порядок\nбітів у байті й на виході", "так / ні\n(MSB- чи LSB-first)", AMBER),
        ("xorout", "чим XOR-нути остачу\nнаприкінці", "0xFFFFFFFF\nчи 0x00000000", BLUE),
    ]
    pw = 270
    px0 = (W - (pw*3 + gap*2)) / 2
    for i, (nm, what, val, col) in enumerate(params):
        x = px0 + i*(pw + gap)
        b += rect(x, 300, pw, 96, "#fff", col, 1.8, 9)
        b += text(x + pw/2, 322, nm, 13, col, "middle", "bold")
        for k, ln in enumerate(what.split("\n")):
            b += text(x + pw/2, 342 + k*15, ln, 10.5, INK, "middle")
        for k, ln in enumerate(val.split("\n")):
            b += mono(x + pw/2, 374 + k*14, ln, 10.5, GREY, "middle")

    b += text(W/2, 414,
              "Поміняй будь-що одне — і число зміниться, хоч поліном той самий. Звідси «CRC не сходиться» між двома боками лінії.",
              11, AMBER, "middle", "bold")

    # ── низ: дерево вибору ──
    b += text(W/2, 452, "Як обрати на практиці", 13, GREEN, "middle", "bold")
    tx = 90
    ty = 470
    decisions = [
        ("Є апаратний блок CRC у МК?", "так → беремо саме його поліном і параметри (§3.9.4c)", GREEN),
        ("Говоримо з готовим протоколом?", "так → копіюємо ВСІ параметри з його специфікації (CAN, Modbus, SD…)", BLUE),
        ("Свій формат, кадри короткі?", "CRC-8/16 таблицею — дешево по пам'яті й тактах", AMBER),
        ("Свій формат, блоки великі/критичні?", "CRC-32 — найменший хибний пропуск", VIOL),
    ]
    for i, (q, a, col) in enumerate(decisions):
        y = ty + i*38
        b += circle(tx, y + 6, 5, col, col, 1)
        b += text(tx + 16, y + 10, q, 12, INK, "start", "bold")
        b += arrow(tx + 290, y + 6, tx + 330, y + 6, col, 2)
        b += text(tx + 340, y + 10, a, 11.5, col, "start")

    b += line(60, H - 40, W - 60, H - 40, FAINT, 1)
    b += text(W/2, H - 18,
              "Головне правило сумісності: CRC задають не лише поліном, а й init, refin/refout і xorout — звіряти треба всю п'ятірку.",
              11.5, GREEN, "middle", "bold")
    save("fig-r09-s4a-3-params.svg", b)


if __name__ == "__main__":
    fig1_bitloop()
    fig2_table()
    fig3_params()
    print("r09-s4-a-crc-implementation figures done.")
