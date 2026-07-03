# -*- coding: utf-8 -*-
# Фігури для ДЕТАЛЬНОЇ статті «Модулі й збірка проєкту».
# Не дублюють базові (compile/rebuild/layers/history) — показують ГЛИБШИЙ шар:
#   objfile   — анатомія .o: секції + таблиця символів (defined/undefined)
#   reloc     — механіка релокації: лінкер підставляє адресу в «дірку»
#   linkorder — статична бібліотека: порядок зліва направо, тягнеться на вимогу
#   makedag   — граф залежностей Make і як «застарілість» піднімається вгору
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SRC = NEG          # синій — вихідний .c
OBJ = "#8a5cc7"    # фіолетовий — об'єктний .o
LNK = POS          # червоний — лінкер / адреси
GEN = "#0f8a6d"    # зелений — Make / збірка
GOLD = "#b45309"   # бурштиновий — акцент/зміна


# ── objfile: що всередині .o — секції + таблиця символів ─────────────────────
def fig_objfile():
    W, H = 780, 430
    p = []

    # ліворуч — секції (машинний вміст)
    p.append(text(190, 74, "СЕКЦІЇ — машинний вміст", size=12, color=OBJ, bold=True))
    secs = [
        (".text", "код функцій (машинні інструкції)", "#f3edfb"),
        (".rodata", "сталі: рядки, const-таблиці", "#f3edfb"),
        (".data", "глобальні з ненульовим значенням", "#f3edfb"),
        (".bss", "глобальні-нулі: лише РОЗМІР, не вміст", "#efeafa"),
    ]
    y = 96
    for name, desc, fill in secs:
        b, w, h = textbox(190, y, name + "  —  " + desc, size=10.5, color=INK,
                          stroke=OBJ, fill=fill, min_w=330, pad=7)
        p.append(b)
        y += 44

    # праворуч — таблиця символів
    p.append(text(600, 74, "ТАБЛИЦЯ СИМВОЛІВ", size=12, color=LNK, bold=True))
    syms = [
        ("uart_send", "DEFINED → .text +0x00", GEN, "#e9f7f2"),
        ("uart_init", "DEFINED → .text +0x40", GEN, "#e9f7f2"),
        ("g_baud", "DEFINED → .data +0x00", GEN, "#e9f7f2"),
        ("gpio_set", "UNDEFINED — чуже, дірка", LNK, "#fdecea"),
        ("memcpy", "UNDEFINED — з бібліотеки", LNK, "#fdecea"),
    ]
    y = 96
    for name, kind, col, fill in syms:
        b, w, h = textbox(600, y, name + "\n" + kind, size=10, color=col,
                          stroke=col, fill=fill, min_w=250, pad=6)
        p.append(b)
        y += 46

    p.append(text(390, 410,
                  "DEFINED — тіло тут, лінкер дасть адресу; UNDEFINED — тіло в іншому .o, лишається дірка",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "objfile.svg"), W, H, *p,
           title="Усередині uart.o: секції та таблиця символів")


# ── reloc: механіка релокації — дірка, запис релокації, підставлена адреса ───
def fig_reloc():
    W, H = 800, 360
    p = []

    # main.o: інструкція виклику з діркою
    b, w, h = textbox(180, 95, "main.o  ·  .text", size=11, color=OBJ, stroke=OBJ,
                      fill="#f3edfb", bold=True, min_w=210)
    p.append(b)
    b, w, h = textbox(180, 150, "call  <????????>\n(4 байти-заглушка)", size=11,
                      color=LNK, stroke=LNK, fill="#fdecea", min_w=210, pad=7)
    p.append(b)
    b, w, h = textbox(180, 215, "запис релокації:\n«тут потрібна адреса uart_send»",
                      size=10, color=GOLD, stroke=GOLD, fill="#fff7ed", min_w=230, pad=7)
    p.append(b)

    # стрілка «лінкер шукає»
    p.append(arrow(300, 150, 480, 150, color=INK, sw=2))
    p.append(text(390, 138, "лінкер знаходить тіло", size=10.5, color=INK, italic=True))

    # uart.o: тіло за адресою
    b, w, h = textbox(600, 95, "uart.o  ·  .text", size=11, color=OBJ, stroke=OBJ,
                      fill="#f3edfb", bold=True, min_w=210)
    p.append(b)
    b, w, h = textbox(600, 150, "uart_send:\nрозміщено за 0x0801_2A40", size=11,
                      color=GEN, stroke=GEN, fill="#e9f7f2", min_w=230, pad=7)
    p.append(b)

    # результат — підставлено
    p.append(arrow(400, 250, 400, 290, color=LNK, sw=2))
    b, w, h = textbox(400, 320, "call  0x0801_2A40      ← дірку закрито адресою з uart.o",
                      size=11, color=INK, stroke=INK, fill=FILL, bold=True, min_w=520, pad=7)
    p.append(b)

    render(os.path.join(OUT, "reloc.svg"), W, H, *p,
           title="Релокація: запис-релокація каже, куди вписати знайдену адресу")


# ── linkorder: статична бібліотека тягнеться зліва направо, на вимогу ─────────
def fig_linkorder():
    W, H = 820, 430
    p = []

    # ── верхній рядок — ПРАВИЛЬНО ──
    p.append(text(410, 64, "ПРАВИЛЬНО:  gcc  main.o  libsensor.a", size=12,
                  color=GEN, bold=True))
    b, w, h = textbox(150, 108, "main.o\nпотребує sensor_read", size=10.5, color=OBJ,
                      stroke=OBJ, fill="#f3edfb", min_w=180, pad=7)
    p.append(b)
    b, w, h = textbox(490, 108, "libsensor.a\n(архів .o-модулів)", size=10.5, color=GEN,
                      stroke=GEN, fill="#e9f7f2", min_w=190, pad=7)
    p.append(b)
    p.append(arrow(245, 108, 388, 108, color=GEN, sw=2))
    b, w, h = textbox(730, 108, "✓ знайдено", size=10.5, color=GEN, stroke=GEN,
                      fill="#e9f7f2", bold=True, min_w=90, pad=6)
    p.append(b)
    p.append(arrow(590, 108, 678, 108, color=GEN, sw=2))
    p.append(text(410, 150, "дірка ще відкрита → тягнемо з архіву потрібний модуль",
                  size=10.5, color=GEN, italic=True))

    p.append(line(60, 188, 760, 188, color=MUTED, dash="4,4"))

    # ── нижній рядок — НЕПРАВИЛЬНО (бібліотека перед .o) ──
    p.append(text(410, 224, "НЕПРАВИЛЬНО:  gcc  libsensor.a  main.o", size=12,
                  color=LNK, bold=True))
    b, w, h = textbox(150, 268, "libsensor.a\nдірок ЩЕ нема", size=10.5, color=MUTED,
                      stroke=MUTED, fill=FILL, min_w=180, pad=7)
    p.append(b)
    b, w, h = textbox(490, 268, "main.o\nаж тепер просить sensor_read", size=10.5,
                      color=OBJ, stroke=OBJ, fill="#f3edfb", min_w=210, pad=7)
    p.append(b)
    p.append(arrow(245, 268, 378, 268, color=LNK, sw=2))
    b, w, h = textbox(730, 268, "✗ undefined\nreference", size=10.5, color=LNK,
                      stroke=LNK, fill="#fdecea", bold=True, min_w=120, pad=6)
    p.append(b)
    p.append(arrow(600, 268, 668, 268, color=LNK, sw=2))
    p.append(text(410, 312, "бібліотеку вже минули — коли по неї дійшла потреба, брати вже нема звідки",
                  size=10.5, color=LNK, italic=True))

    p.append(text(410, 396,
                  "лінкер іде списком ЗЛІВА НАПРАВО і бере з .a лише те, що на цю мить бракує",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "linkorder.svg"), W, H, *p,
           title="Статична бібліотека: порядок аргументів вирішує все")


# ── makedag: граф залежностей і піднімання «застаріле» вгору ──────────────────
# Спрощений, без перехресть: led.h унизу ліворуч; його спільна залежність тягне
# і main.o, і led.o (обидва його включають). uart.o осторонь — не чіпали.
def fig_makedag():
    W, H = 760, 410
    p = []

    def node(x, y, label, col, fill, w=130):
        b, ww, hh = textbox(x, y, label, size=11, color=col, stroke=col,
                            fill=fill, min_w=w, bold=True, pad=7)
        p.append(b)

    # нижній ярус — джерела
    node(130, 350, "led.h ✎\n(змінили)", GOLD, "#fff7ed", 140)
    node(380, 350, "led.c", SRC, "#eef2fb", 110)
    node(630, 350, "uart.c", SRC, "#eef2fb", 110)

    # середній ярус — об'єктні файли
    node(130, 225, "main.o\nЗАСТАРІВ", LNK, "#fdecea", 140)
    node(380, 225, "led.o\nЗАСТАРІВ", LNK, "#fdecea", 140)
    node(630, 225, "uart.o\nсвіжий", GEN, "#e9f7f2", 140)

    # верх — образ
    node(380, 100, "firmware.elf\nперелінкувати", LNK, "#fdecea", 220)

    # led.h → main.o (main.c включає led.h) — пряма вертикаль
    p.append(arrow(130, 322, 130, 258, color=GOLD, sw=1.8))
    # led.h → led.o (led.c теж включає led.h) — навскіс, єдина похила лінія
    p.append(arrow(175, 335, 335, 252, color=GOLD, sw=1.6))
    # led.c → led.o
    p.append(arrow(380, 322, 380, 258, color=SRC, sw=1.4))
    # uart.c → uart.o (не міняли — пунктир, без стрілки-акценту)
    p.append(line(630, 322, 630, 258, color=MUTED, sw=1.4, dash="4,4"))

    # .o → образ: два застарілі тягнуть перелінк (суцільні), uart.o лише бере участь (пунктир)
    p.append(arrow(150, 200, 320, 135, color=LNK, sw=1.6))
    p.append(arrow(380, 200, 380, 135, color=LNK, sw=1.6))
    p.append(line(610, 200, 445, 135, color=MUTED, sw=1.4, dash="4,4"))

    p.append(text(380, 392,
                  "змінили led.h → застаріває КОЖЕН .o, що його включав → образ перелінковується",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "makedag.svg"), W, H, *p,
           title="Граф залежностей: застарілість тече від зміненого файлу вгору до образу")


if __name__ == "__main__":
    fig_objfile()
    fig_reloc()
    fig_linkorder()
    fig_makedag()
    print("figs-d done")
