# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8860b"   # поля розміру, що заповнюються останніми


# ── wav-header: 44 байти паспорта WAV трьома блоками ──────────────────────────
# Ідея: показати, що заголовок ділиться на три смислові частини (RIFF / fmt /
# data), і виділити ДВА поля розміру (жовті), які заповнюються ОСТАННІМИ, коли
# довжина вже відома. Байтові зсуви підписані, щоб паспорт був конкретний.

def fig_wav_header():
    W, H = 720, 360
    p = []
    x0, y0 = 60, 78
    rowh = 30
    labw = 250          # ширина колонки-назви поля
    offw = 70           # ширина колонки-зсуву

    # (назва поля, зсув, значення, це поле розміру?)
    rows = [
        ("RIFF",  0,  '"RIFF"',          False, "#eef4ff", NEG),
        ("RIFF",  4,  "розмір файлу − 8", True,  "#eef4ff", NEG),
        ("RIFF",  8,  '"WAVE"',          False, "#eef4ff", NEG),
        ("fmt ", 12,  '"fmt "  + довжина 16', False, "#eafaf0", FIELD),
        ("fmt ", 20,  "PCM · канали · частота", False, "#eafaf0", FIELD),
        ("fmt ", 28,  "ByteRate · BlockAlign · біти", False, "#eafaf0", FIELD),
        ("data", 36,  '"data"',          False, "#fff7e6", GOLD),
        ("data", 40,  "розмір самого звуку", True, "#fff7e6", GOLD),
        ("data", 44,  "… далі йдуть відліки int16 …", False, FILL, MUTED),
    ]

    # ліві дужки-групи
    groups = [("RIFF-дескриптор", 0, 3, NEG),
              ('підрозділ "fmt "', 3, 6, FIELD),
              ('підрозділ "data"', 6, 8, GOLD)]

    for i, (grp, off, val, is_size, fill, st) in enumerate(rows):
        y = y0 + i * rowh
        last = (i == len(rows) - 1)
        fw = FILL if last else fill
        p.append(rect(x0 + offw, y, labw, rowh - 4, fill=fw, stroke=st, sw=1.4))
        p.append(text(x0 + offw + labw / 2, y + (rowh - 4) / 2 + 4, val,
                      size=10.5, color=INK, italic=last))
        # колонка зсуву (байт)
        if not last:
            p.append(text(x0 + offw - 8, y + (rowh - 4) / 2 + 4, "@%d" % off,
                          size=9, color=MUTED, anchor="end"))
        # зірочка на полях розміру
        if is_size:
            p.append(text(x0 + offw + labw + 12, y + (rowh - 4) / 2 + 4,
                          "◀ заповнюємо останнім", size=9.5, color=GOLD,
                          anchor="start", bold=True))

    # групувальні дужки праворуч від міток? — лишимо назви груп зліва
    for name, a, b, col in groups:
        ya = y0 + a * rowh
        yb = y0 + b * rowh - 4
        gx = x0 - 6
        p.append(line(gx, ya + 2, gx, yb - 2, color=col, sw=2.2))
        p.append(text(gx - 4, (ya + yb) / 2, name, size=9.5, color=col,
                      anchor="end", bold=True))

    p.append(text(W / 2, 40, "44 байти заголовка WAV — паспорт перед даними",
                  size=13, color=INK, bold=True))
    p.append(text(W / 2, H - 16,
                  "жовті поля розміру відомі лише в кінці запису — їх правлять останніми",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "wav-header.svg"), W, H, *p,
           title="Розкладка WAV-заголовка: RIFF / fmt / data і два поля розміру")


# ── length-dilemma: число довжини потрібне на початку, відоме в кінці ──────────
# Ідея: два способи заповнити поля розміру. Зліва — "нулі → звук → повернутись і
# виправити" (seek назад). Справа — "тривалість відома наперед → одразу правильний
# заголовок". Показуємо стрічку файлу і момент, коли розмір стає відомим.

def fig_length_dilemma():
    W, H = 720, 320
    p = []
    barw, barh = 300, 40

    def strip(x0, y0, title, hdr_txt, hdr_col, note, back_arrow):
        p.append(text(x0 + barw / 2, y0 - 16, title, size=12, color=INK, bold=True))
        # заголовок (перший сегмент)
        hw = 78
        p.append(rect(x0, y0, hw, barh, fill="#fff7e6", stroke=hdr_col, sw=1.8))
        p.append(text(x0 + hw / 2, y0 + barh / 2 - 4, "заголовок", size=9.5, color=INK))
        p.append(text(x0 + hw / 2, y0 + barh / 2 + 9, hdr_txt, size=9, color=hdr_col, bold=True))
        # тіло звуку
        p.append(rect(x0 + hw, y0, barw - hw, barh, fill="#eef4ff", stroke=NEG, sw=1.5))
        p.append(text(x0 + hw + (barw - hw) / 2, y0 + barh / 2 + 4,
                      "звук — блок за блоком →", size=10, color=NEG))
        # дужка-повернення
        if back_arrow:
            ay = y0 + barh + 22
            p.append(line(x0 + barw - 20, y0 + barh + 4, x0 + barw - 20, ay, color=GOLD, sw=1.6))
            p.append(line(x0 + barw - 20, ay, x0 + hw / 2, ay, color=GOLD, sw=1.6))
            p.append(arrow(x0 + hw / 2, ay, x0 + hw / 2, y0 + barh + 4, color=GOLD, sw=1.8))
            p.append(text(x0 + barw / 2, ay + 16, "seek на початок — вписати довжину",
                          size=9.5, color=GOLD, bold=True))
        p.append(text(x0 + barw / 2, y0 + barh + (60 if back_arrow else 24), note,
                      size=9.5, color=MUTED, italic=True))

    strip(60, 90, "Спосіб 1 — повернутись і переписати",
          "розмір = 0", GOLD, "нулі спершу, наприкінці правимо 8 байт", True)
    strip(60, 230, "Спосіб 2 — рахувати наперед",
          "розмір готовий", FIELD, "тривалість відома → заголовок правильний одразу", False)

    p.append(text(W / 2, 40,
                  "довжина потрібна НА ПОЧАТКУ файлу, а відома лише В КІНЦІ",
                  size=13, color=INK, bold=True))
    render(os.path.join(OUT, "length-dilemma.svg"), W, H, *p,
           title="Дилема довжини WAV: заголовок першим, число останнім")


# ── ring-pretrigger: кільце дає передзвук — секунди ДО події ───────────────────
# Ідея: кільце пише завжди, затираючи старе; у момент події в ньому вже лежить
# передзвук. Файл = передзвук із кільця + звук наживо. Показуємо кільце, голову,
# мітку події і зшивання двох частин у стрічку запису.

def fig_ring_pretrigger():
    W, H = 720, 340
    import math
    p = []
    cx, cy, R = 190, 175, 92

    # кільце як коло секторів; частина — "свіже", решта — "старе, ось-ось затреться"
    nseg = 16
    for i in range(nseg):
        a0 = -90 + 360 * i / nseg
        a1 = -90 + 360 * (i + 1) / nseg
        mid = math.radians((a0 + a1) / 2)
        rx = cx + (R + 16) * math.cos(mid)
        ry = cy + (R + 16) * math.sin(mid)
        fresh = i < 11
        col = NEG if fresh else MUTED
        # рисочки-сектори
        x1 = cx + (R - 12) * math.cos(math.radians(a0))
        y1 = cy + (R - 12) * math.sin(math.radians(a0))
        x2 = cx + R * math.cos(math.radians(a0))
        y2 = cy + R * math.sin(math.radians(a0))
        p.append(line(x1, y1, x2, y2, color=MUTED, sw=1.0))
    # саме коло
    p.append(circle(cx, cy, R, fill="none", stroke=INK, sw=1.8))
    # голова: пише сюди наступне = найстаріший відлік
    hx = cx + R * math.cos(math.radians(-90))
    hy = cy + R * math.sin(math.radians(-90))
    p.append(arrow(cx, cy - 30, hx, hy - 4, color=FIELD, sw=2.0))
    p.append(text(cx, cy - 4, "кільце", size=12, color=INK, bold=True))
    p.append(text(cx, cy + 14, "пише завжди", size=9.5, color=MUTED, italic=True))
    p.append(text(hx, hy - 14, "голова", size=9.5, color=FIELD, bold=True))
    p.append(text(cx, cy + R + 30, "стрілка обертання затирає найстаріше",
                  size=9.5, color=MUTED, italic=True))

    # праворуч: стрічка запису = передзвук + наживо
    bx, by = 350, 150
    bw, bh = 320, 44
    p.append(text(bx + bw / 2, by - 18, "файл на картці", size=12, color=INK, bold=True))
    prew = 130
    p.append(rect(bx, by, prew, bh, fill="#eafaf0", stroke=FIELD, sw=1.7))
    p.append(text(bx + prew / 2, by + bh / 2 - 4, "передзвук", size=10.5, color=INK, bold=True))
    p.append(text(bx + prew / 2, by + bh / 2 + 10, "із кільця", size=9, color=FIELD))
    p.append(rect(bx + prew, by, bw - prew, bh, fill="#eef4ff", stroke=NEG, sw=1.5))
    p.append(text(bx + prew + (bw - prew) / 2, by + bh / 2 - 4, "звук наживо", size=10.5, color=INK))
    p.append(text(bx + prew + (bw - prew) / 2, by + bh / 2 + 10, "далі, доки триває подія", size=9, color=NEG))

    # мітка події на стику
    ev_x = bx + prew
    p.append(line(ev_x, by - 6, ev_x, by + bh + 24, color=GOLD, sw=1.8, dash="4 3"))
    p.append(text(ev_x, by + bh + 38, "детектор ловить подію", size=10, color=GOLD, bold=True))

    # зв'язок кільце → передзвук
    p.append(arrow(cx + R + 6, cy - 20, bx - 6, by + bh / 2, color=FIELD, sw=1.6))

    p.append(text(W / 2, 40, "кільце дарує ПЕРЕДЗВУК: секунди, що були ДО спрацювання",
                  size=13, color=INK, bold=True))
    render(os.path.join(OUT, "ring-pretrigger.svg"), W, H, *p,
           title="Кільцевий буфер: запис звуку, що передував події")


if __name__ == "__main__":
    fig_wav_header()
    fig_length_dilemma()
    fig_ring_pretrigger()
    print("OK: figures written to", OUT)
