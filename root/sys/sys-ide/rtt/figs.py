# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── ring-buffer: два покажчики на кільці, кожен свого господаря ────────────────
# Ідея: кільцевий буфер у RAM; ядро рухає лише WrOff (пише), зонд — лише RdOff
# (читає). Покажчики ганяються по колу; зійшлися — порожньо. Спільного замка
# нема саме тому, що кожен покажчик має одного господаря.

def fig_ring_buffer():
    W, H = 720, 380
    cx, cy, R = 250, 200, 130
    p = []

    n = 16                       # комірок у кільці
    # заповнена дуга — від RdOff до WrOff (те, що ядро написало, а зонд ще не забрав)
    rd_i, wr_i = 3, 10
    for i in range(n):
        a = -90 + i * 360.0 / n
        a0 = math.radians(a)
        a1 = math.radians(a + 360.0 / n)
        x0o, y0o = cx + R * math.cos(a0), cy + R * math.sin(a0)
        x1o, y1o = cx + R * math.cos(a1), cy + R * math.sin(a1)
        x0i, y0i = cx + (R - 30) * math.cos(a0), cy + (R - 30) * math.sin(a0)
        x1i, y1i = cx + (R - 30) * math.cos(a1), cy + (R - 30) * math.sin(a1)
        filled = (rd_i <= i < wr_i)
        fill = "#dbe7fb" if filled else "#ffffff"
        p.append('<path d="M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f L%.1f %.1f A%.1f %.1f 0 0 0 %.1f %.1f Z" '
                 'fill="%s" stroke="%s" stroke-width="1.1"/>'
                 % (x0o, y0o, R, R, x1o, y1o, x1i, y1i, R - 30, R - 30, x0i, y0i, fill, "#b9c4d6"))

    def at(i, rr):
        a = math.radians(-90 + (i + 0.5) * 360.0 / n)
        return cx + rr * math.cos(a), cy + rr * math.sin(a)

    # WrOff — господар ядро (синій тут = «холодний» бік запису ядра? ні: запис = гаряче).
    # За палітрою POS — гаряче/ядро пише; NEG — зонд читає.
    wx, wy = at(wr_i - 0.5, R + 30)
    p.append(circle(wx, wy, 8, fill="#fdecea", stroke=POS, sw=2.2))
    p.append(text(wx, wy - 16, "WrOff", size=12, color=POS, bold=True))
    p.append(text(wx, wy + 26, "рухає ЯДРО", size=10, color=POS))

    rx, ry = at(rd_i - 0.5, R + 30)
    p.append(circle(rx, ry, 8, fill="#eaf0fd", stroke=NEG, sw=2.2))
    p.append(text(rx, ry - 16, "RdOff", size=12, color=NEG, bold=True))
    p.append(text(rx, ry + 26, "рухає ЗОНД", size=10, color=NEG))

    # стрілка напрямку обходу
    p.append(text(cx, cy - 6, "кільце в RAM", size=12, color=INK, bold=True))
    p.append(text(cx, cy + 12, "%d байтів" % 256, size=10, color=MUTED))
    aa = math.radians(40)
    p.append(arrow(cx + (R - 52) * math.cos(aa - 0.18), cy + (R - 52) * math.sin(aa - 0.18),
                   cx + (R - 52) * math.cos(aa + 0.18), cy + (R - 52) * math.sin(aa + 0.18),
                   color=MUTED, sw=1.6))

    # пояснення праворуч
    bx = 470
    p.append(text(bx, 90, "Зайняте — між RdOff і WrOff:", size=12, color=INK, anchor="start", bold=True))
    p.append(rect(bx, 104, 22, 14, fill="#dbe7fb", stroke="#b9c4d6", sw=1.0))
    p.append(text(bx + 30, 115, "ще не прочитане зондом", size=11, color=INK, anchor="start"))
    p.append(rect(bx, 128, 22, 14, fill="#ffffff", stroke="#b9c4d6", sw=1.0))
    p.append(text(bx + 30, 139, "вільне місце", size=11, color=INK, anchor="start"))

    msg = ("Кожен покажчик має ОДНОГО господаря:\n"
           "ядро лиш пише й рухає WrOff,\n"
           "зонд лиш читає й рухає RdOff.\n"
           "Тому замок не потрібен —\n"
           "вони ніколи не пишуть в одне.")
    p.append(mtext(bx, 185, msg, size=11.5, color=INK, anchor="start", lh=1.45))

    p.append(text(bx, 320, "WrOff == RdOff → порожньо", size=11, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "ring-buffer.svg"), W, H, *p,
           title="Кільцевий буфер RTT: два покажчики, два господарі, без замка")


# ── control-block: зонд знаходить керівний блок у RAM за підписом ──────────────
# Ідея: у RAM серед іншого лежить блок, що ПОЧИНАЄТЬСЯ з рядка "SEGGER RTT";
# зонд фоново сканує RAM, ловить цей підпис — і далі читає описи каналів
# (адреса буфера, розмір, WrOff/RdOff). Жодного піна, лише доступ через SWD.

def fig_control_block():
    W, H = 760, 420
    p = []

    # смуга RAM ліворуч із кількома блоками, серед них — контрольний
    rx, ry, rw = 40, 70, 150
    cells = [
        (".data", "#f0f0f0"),
        ("стек", "#f0f0f0"),
        ("купа", "#f0f0f0"),
        ("RTT CB", "#fff3d6"),
        ("буфери", "#e8f3ea"),
        (".bss", "#f0f0f0"),
    ]
    ch = 48
    p.append(text(rx + rw / 2, ry - 16, "RAM цілі", size=12, color=INK, bold=True))
    cb_y = None
    y = ry
    for lab, fill in cells:
        stroke = POS if lab == "RTT CB" else "#c9c9c9"
        sw = 2.2 if lab == "RTT CB" else 1.0
        p.append(rect(rx, y, rw, ch, fill=fill, stroke=stroke, sw=sw, rx=4))
        p.append(text(rx + rw / 2, y + ch / 2 + 4, lab, size=11, color=INK,
                      bold=(lab == "RTT CB")))
        if lab == "RTT CB":
            cb_y = y
        y += ch + 6

    # зонд сканує RAM (стрілки-промацування збоку)
    p.append(text(rx + rw / 2, y + 16, "зонд фоново читає RAM", size=10, color=NEG, italic=True))

    # збільшений контрольний блок праворуч
    bx, by, bw = 300, 70, 420
    p.append(text(bx, by - 16, "Керівний блок (SEGGER_RTT_CB)", size=12, color=INK, anchor="start", bold=True))

    rows = [
        ('acID[16] = "SEGGER RTT\\0…"', "#fff3d6", POS, "підпис — за ним зонд і впізнає блок"),
        ("MaxNumUp / MaxNumDown", "#f6f6f6", INK, "скільки каналів угору / вниз"),
        ("aUp[0]:  pBuffer, Size,", "#eaf0fd", NEG, "опис кільця 0 (ядро→хост):"),
        ("         WrOff, RdOff, Flags", "#eaf0fd", NEG, "де буфер, розмір, два покажчики"),
        ("aDown[0]: pBuffer, Size,", "#fdecea", POS, "опис кільця вниз (хост→ядро)"),
        ("          WrOff, RdOff, Flags", "#fdecea", POS, ""),
    ]
    rh = 40
    yy = by
    for lab, fill, col, note in rows:
        p.append(fitbox(bx, yy, 250, rh, lab, size=11, fill=fill, stroke=col, sw=1.3, color=INK,
                        bold=(fill == "#fff3d6")))
        if note:
            p.append(text(bx + 262, yy + rh / 2 + 4, note, size=10, color=MUTED, anchor="start"))
        yy += rh + 6

    # звʼязок: підпис знайдено → блок розібрано
    p.append(arrow(rx + rw + 4, cb_y + ch / 2, bx - 6, by + rh / 2, color=POS, sw=1.8))
    p.append(text((rx + rw + bx) / 2 + 6, cb_y - 6, "знайдено\nза підписом", size=9, color=POS))

    msg = ("Адрес блоку зонд наперед не знає: він сканує RAM, шукаючи 16 байтів \"SEGGER RTT\";\n"
           "знайшов підпис — читає описи каналів і качає буфери. Усе через SWD/JTAG, без окремого піна.")
    box, mw, mh = textbox(W / 2, 376, msg, size=11, fill="#f6f4ec", stroke=MUTED, sw=1.2, pad=12)
    p.append(box)

    render(os.path.join(OUT, "control-block.svg"), W, H, *p,
           title="Як зонд знаходить RTT: підпис у RAM, потім описи каналів")


# ── channels: кілька струменів угору + один вниз, демультиплекс на хості ───────
# Ідея: канали — це окремі кільця. Кілька «угору» розводять різні потоки
# (лог, дані, профілювання), щоб на хості вони не злипалися; «вниз» дає
# зворотний бік — увід із ПК у прошивку.

def fig_channels():
    W, H = 820, 360
    p = []

    lx, lw = 40, 200        # ціль
    hx, hw = 600, 190       # хост
    midx0, midx1 = lx + lw, hx
    p.append(text(lx + lw / 2, 44, "Ціль (прошивка)", size=13, color=INK, bold=True))
    p.append(text(hx + hw / 2, 44, "Хост (ПК)", size=13, color=INK, bold=True))

    # три канали вгору
    ups = [
        ("U0 \"Terminal\"", "лог printf", "#eaf0fd", "консоль", NEG),
        ("U1 \"data\"", "відліки давача", "#eaf0fd", "графік", NEG),
        ("U2 \"profile\"", "мітки подій", "#eaf0fd", "профайлер", NEG),
    ]
    y = 78
    bh = 40
    for src, what, fill, dst, col in ups:
        p.append(fitbox(lx, y, lw, bh, src + "\n" + what, size=10, fill=fill, stroke=col, sw=1.4, color=INK))
        p.append(arrow(midx0 + 2, y + bh / 2, midx1 - 2, y + bh / 2, color=col, sw=1.9))
        p.append(fitbox(hx, y, hw, bh, dst, size=11, fill="#f6f6f6", stroke=col, sw=1.2, color=INK, bold=True))
        y += bh + 14

    # один канал вниз
    p.append(fitbox(lx, y, lw, bh, "D0 \"input\"\nчитає команди", size=10, fill="#fdecea", stroke=POS, sw=1.4, color=INK))
    p.append(arrow(midx1 - 2, y + bh / 2, midx0 + 2, y + bh / 2, color=POS, sw=1.9))
    p.append(fitbox(hx, y, hw, bh, "увід із клавіатури", size=11, fill="#fdecea", stroke=POS, sw=1.2, color=INK, bold=True))

    # підпис посередині
    p.append(mtext((midx0 + midx1) / 2, 66, "кожен канал —\nокреме кільце",
                   size=10, color=MUTED))

    p.append(text(W / 2, H - 18,
                  "Окремі кільця тримають потоки нарізно: лог не змішується з даними, а напрям «вниз» дає увід у прошивку",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "channels.svg"), W, H, *p,
           title="Канали RTT: кілька струменів угору, окремий — вниз")


if __name__ == "__main__":
    fig_ring_buffer()
    fig_control_block()
    fig_channels()
    print("OK: figures written to", OUT)
