# -*- coding: utf-8 -*-
# Фігури теми «Пристрій керування». svgkit імпортуємо (не копіюємо) — §5 AUTHORING.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Спільні відтінки (узгоджені з палітрою svgkit і сусідніми темами розділу)
RED_F, RED = "#fdf4f4", POS          # регістри / АЛП
GRN_F, GRN = "#f4f7f4", FIELD        # пам'ять / дані
GLD_F, GLD = "#fbf3df", "#a9842f"    # пристрій керування / сигнали
BLU_F, BLU = "#eef2fd", NEG          # входи / умова


# ── what-is-control: керування як розподільна коробка ────────────────────────
# Ідея: входи (код команди + прапорці) → блок керування → пучок керувальних
# ліній до кожного органа. Сам нічого не рахує — лише розкладає на увімкнення.
def fig_what_is_control():
    W, H = 760, 380
    p = []

    # входи ліворуч
    p.append(rect(40, 110, 150, 44, fill=BLU_F, stroke=BLU, sw=1.7, rx=7))
    p.append(text(115, 130, "IR: код команди", size=11, color=BLU, bold=True))
    p.append(text(115, 146, "0001 0011 …", size=10, color=MUTED))
    p.append(rect(40, 200, 150, 44, fill=BLU_F, stroke=BLU, sw=1.7, rx=7))
    p.append(text(115, 220, "Прапорці", size=11, color=BLU, bold=True))
    p.append(text(115, 236, "Z · C · N · V", size=10, color=MUTED))
    p.append(arrow(192, 132, 288, 165, color=BLU, sw=1.9))
    p.append(arrow(192, 222, 288, 205, color=BLU, sw=1.9))

    # блок керування — центр
    bx, by, bw, bh = 290, 120, 200, 130
    p.append(rect(bx, by, bw, bh, fill=GLD_F, stroke=GLD, sw=2.2, rx=12))
    p.append(text(bx + bw / 2, by + 40, "ПРИСТРІЙ", size=14, color=INK, bold=True))
    p.append(text(bx + bw / 2, by + 60, "КЕРУВАННЯ", size=14, color=INK, bold=True))
    p.append(text(bx + bw / 2, by + 92, "розкладає команду", size=10, color=MUTED, italic=True))
    p.append(text(bx + bw / 2, by + 108, "на «хто що робить»", size=10, color=MUTED, italic=True))

    # виходи праворуч — пучок керувальних ліній
    outs = [
        ("обрати регістри", RED),
        ("операція АЛП", RED),
        ("увімкнути запис", GRN),
        ("шина: чит./запис", GRN),
    ]
    oy = 130
    for lab, col in outs:
        p.append(arrow(bx + bw + 4, oy, bx + bw + 96, oy, color=GLD, sw=2))
        p.append(rect(bx + bw + 100, oy - 15, 150, 30, fill=BG, stroke=col, sw=1.5, rx=6))
        p.append(text(bx + bw + 175, oy + 5, lab, size=10.5, color=col, bold=True))
        oy += 40

    p.append(text(bx + bw / 2, H - 20, "сам над даними НЕ рахує — лише вмикає потрібні лінії",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "what-is-control.svg"), W, H, *p,
           title="Пристрій керування: команда + прапорці → сигнали керування")


# ── decode-signals: число-команда розкладається на опкод і поля → сигнали ────
# Ідея: IR ділиться на опкод + поля; комбінаційний декодер зіставляє опкод зі
# взірцем і піднімає відповідні керувальні лінії.
def fig_decode_signals():
    W, H = 760, 380
    p = []

    # регістр IR, поділений на поля
    fields = [("опкод", "0001", RED, "→ додати"),
              ("призн.", "0011", GRN, "→ R3"),
              ("оп. A", "0100", BLU, "→ R1"),
              ("оп. B", "0101", BLU, "→ R2")]
    fx, fw = 70, 130
    fy, fh = 70, 56
    for i, (lab, bits, col, mean) in enumerate(fields):
        x = fx + i * fw
        p.append(rect(x, fy, fw - 6, fh, fill=BG, stroke=col, sw=1.8, rx=6))
        p.append(text(x + (fw - 6) / 2, fy + 20, lab, size=10.5, color=col, bold=True))
        p.append(text(x + (fw - 6) / 2, fy + 42, bits, size=13, color=INK, bold=True))
        p.append(text(x + (fw - 6) / 2, fy + fh + 18, mean, size=10, color=MUTED))
    p.append(text(fx + 2 * (fw - 6), fy - 14, "IR = 0001 0011 0100 0101",
                  size=11, color=INK, bold=True))

    # декодер — смуга
    dx, dy, dw, dh = 120, 200, 420, 46
    p.append(rect(dx, dy, dw, dh, fill=GLD_F, stroke=GLD, sw=2, rx=9))
    p.append(text(dx + dw / 2, dy + 21, "ДЕКОДЕР — комбінаційна схема", size=12.5, color=INK, bold=True))
    p.append(text(dx + dw / 2, dy + 38, "зіставляє опкод зі взірцем «додати»", size=10, color=MUTED, italic=True))
    p.append(arrow(fx + fw / 2, fy + fh + 26, dx + 70, dy - 4, color=INK, sw=1.7))

    # сигнали на виході
    p.append(arrow(dx + dw / 2, dy + dh + 2, dx + dw / 2, dy + dh + 26, color=GLD, sw=2))
    b, bw2, bh2 = textbox(dx + dw / 2, dy + dh + 66,
                          "подай R1,R2 в АЛП · операція + · приготуй запис у R3",
                          size=11.5, bold=True, color=INK, fill=BG, stroke=GLD, sw=1.8)
    p.append(b)

    render(os.path.join(OUT, "decode-signals.svg"), W, H, *p,
           title="Декодування: опкод + поля → набір сигналів керування")


# ── micro-steps: одна команда розкладена на такти ────────────────────────────
# Ідея: команда "додати комірку пам'яті до регістра" йде 4 такти; на кожному —
# своя порція сигналів; крок залежить від попереднього.
def fig_micro_steps():
    W, H = 760, 340
    p = []
    steps = [
        ("Такт 1", "виставити адресу\nна шину · «читати»", GLD),
        ("Такт 2", "чекати пам'ять\n(доступ повільний)", GRN),
        ("Такт 3", "число + регістр\nв АЛП · увімкнути +", RED),
        ("Такт 4", "защіпнути результат\nу регістр", BLU),
    ]
    n = len(steps)
    bw, bh, gap = 150, 108, 34
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    y = 120
    for i, (title, body, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        fillc = {GLD: GLD_F, GRN: GRN_F, RED: RED_F, BLU: BLU_F}[col]
        p.append(rect(x, y, bw, bh, fill=fillc, stroke=col, sw=2, rx=10))
        p.append(text(x + bw / 2, y + 26, title, size=13, color=col, bold=True))
        p.append(mtext(x + bw / 2, y + 52, body, size=11, color=INK, lh=1.25))
        if i < n - 1:
            p.append(arrow(x + bw + 4, y + bh / 2, x + bw + gap - 4, y + bh / 2, color=INK, sw=2))

    p.append(text(W / 2, y + bh + 42, "крок 3 неможливий раніше за крок 2 — рахувати нема чого, поки дані не привезли",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, y - 26, "команда «додати комірку пам'яті до регістра»", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "micro-steps.svg"), W, H, *p,
           title="Одна команда — послідовність тактів, у кожного своя порція сигналів")


# ── hardwired-vs-micro: дві архітектури керування ────────────────────────────
# Ідея: зашите — застигла сітка вентилів опкод→сигнали (швидко, жорстко);
# мікропрограмне — пам'ять мікрокоманд, біти рядка → сигнали (гнучко, +такт).
def fig_hardwired_vs_micro():
    W, H = 760, 400
    p = []

    # ── ліворуч: зашите ──
    lx = 40
    p.append(rect(lx, 60, 320, 300, fill="#fff7f7", stroke=RED, sw=2, rx=14))
    p.append(text(lx + 160, 86, "ЗАШИТЕ (hardwired)", size=13, color=RED, bold=True))
    # опкод
    p.append(rect(lx + 110, 108, 100, 34, fill=BG, stroke=INK, sw=1.5, rx=6))
    p.append(text(lx + 160, 130, "опкод", size=11, color=INK, bold=True))
    p.append(arrow(lx + 160, 144, lx + 160, 172, color=INK, sw=1.8))
    # сітка вентилів
    gx, gy, gw, gh = lx + 40, 174, 240, 96
    p.append(rect(gx, gy, gw, gh, fill=RED_F, stroke=RED, sw=1.8, rx=9))
    p.append(text(gx + gw / 2, gy + 26, "застигла сітка", size=12, color=RED, bold=True))
    p.append(text(gx + gw / 2, gy + 44, "логічних вентилів", size=12, color=RED, bold=True))
    # маленькі вентилі-натяк
    for i in range(4):
        vx = gx + 34 + i * 46
        p.append(circle(vx, gy + 72, 9, fill=BG, stroke=RED, sw=1.4))
    p.append(arrow(gx + gw / 2, gy + gh + 2, gx + gw / 2, gy + gh + 24, color=RED, sw=1.9))
    p.append(rect(lx + 60, 296, 200, 30, fill=BG, stroke=GLD, sw=1.6, rx=6))
    p.append(text(lx + 160, 316, "сигнали керування", size=11, color=GLD, bold=True))
    p.append(text(lx + 160, 346, "швидко · набір команд запаяний", size=10, color=MUTED, italic=True))

    # ── праворуч: мікропрограмне ──
    rx = 400
    p.append(rect(rx, 60, 320, 300, fill="#fffdf5", stroke=GLD, sw=2, rx=14))
    p.append(text(rx + 160, 86, "МІКРОПРОГРАМНЕ", size=13, color=GLD, bold=True))
    # опкод → адреса
    p.append(rect(rx + 110, 108, 100, 34, fill=BG, stroke=INK, sw=1.5, rx=6))
    p.append(text(rx + 160, 130, "опкод", size=11, color=INK, bold=True))
    p.append(arrow(rx + 160, 144, rx + 160, 168, color=INK, sw=1.8))
    # сховище мікрокоманд — стос рядків
    sx, sy, sw2 = rx + 60, 170, 200
    p.append(text(rx + 160, sy - 2, "сховище мікрокоманд", size=10.5, color=GLD, bold=True))
    rows = ["1011 0100", "0010 1101", "1100 0011"]
    ry = sy + 8
    for i, bits in enumerate(rows):
        hl = (i == 1)
        p.append(rect(sx, ry, sw2, 26, fill=(GLD_F if hl else BG),
                      stroke=GLD, sw=1.7 if hl else 1.2, rx=4))
        p.append(text(sx + sw2 / 2, ry + 17, bits, size=11, color=INK,
                      bold=hl))
        ry += 30
    # рядок → сигнали (біти напряму)
    p.append(arrow(sx + sw2 + 2, sy + 8 + 30 + 13, sx + sw2 + 40, sy + 8 + 30 + 13, color=GLD, sw=1.9))
    p.append(rect(rx + 60, 300, 200, 30, fill=BG, stroke=GLD, sw=1.6, rx=6))
    p.append(text(rx + 160, 320, "сигнали керування", size=11, color=GLD, bold=True))
    p.append(arrow(rx + 160, 262, rx + 160, 298, color=GLD, sw=1.6))
    p.append(text(rx + 160, 348, "гнучко · ціною зайвого такту", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "hardwired-vs-micro.svg"), W, H, *p,
           title="Два способи побудувати керування: зашите й мікропрограмне")


# ── proj: fsm-load — автомат LOAD як граф станів із чеканням пам'яті ──────────
# Ідея: опкод LOAD запускає ланцюжок станів; на стані READ автомат КРУТИТЬСЯ,
# доки пам'ять не підняла ready — це і є вставлені такти чекання (wait states).
def fig_fsm_load():
    W, H = 780, 360
    p = []

    def state(cx, cy, name, sub, hot=False):
        f = GLD_F if hot else BG
        s = GLD if hot else INK
        frag, w, h = textbox(cx, cy, name, size=13, pad=14, fill=f, stroke=s,
                             sw=2.2 if hot else 1.6, color=INK, bold=True, min_w=118)
        return frag + text(cx, cy + 24, sub, size=9.5, color=MUTED, italic=True), w

    y = 150
    xs = [95, 275, 455, 635]
    labels = [
        ("ADDR", "виставити адресу"),
        ("READ", "чекати пам'ять"),
        ("CALC", "порахувати"),
        ("WRITE", "защіпнути"),
    ]
    for (nm, sub), x, hot in zip(labels, xs, [False, True, False, False]):
        frag, _ = state(x, y, nm, sub, hot)
        p.append(frag)

    # прямі переходи між станами
    trans = [
        (xs[0] + 60, xs[1] - 60, "mem_read=1"),
        (xs[1] + 60, xs[2] - 60, "ready=1"),
        (xs[2] + 60, xs[3] - 60, "готово"),
    ]
    for x1, x2, lab in trans:
        p.append(arrow(x1, y, x2, y, color=INK, sw=1.9))
        p.append(text((x1 + x2) / 2, y - 12, lab, size=9.5, color=NEG, bold=True))

    # петля чекання на READ: ready==0 → лишитися
    lx = xs[1]
    p.append(line(lx - 26, y - 26, lx - 60, y - 58, color=POS, sw=1.9))
    p.append(line(lx - 60, y - 58, lx + 60, y - 58, color=POS, sw=1.9))
    p.append(arrow(lx + 60, y - 58, lx + 26, y - 26, color=POS, sw=1.9))
    p.append(text(lx, y - 70, "ready==0 → лишитися (+1 такт чекання)", size=10,
                  color=POS, bold=True))

    # вхід від декодера
    p.append(text(xs[0], y - 46, "опкод LOAD", size=10.5, color=GLD, bold=True))
    p.append(arrow(xs[0], y - 38, xs[0], y - 22, color=GLD, sw=1.7))

    # виходовий такт праворуч
    p.append(arrow(xs[3] + 60, y, xs[3] + 96, y, color=INK, sw=1.7))
    p.append(text(xs[3] + 78, y + 16, "далі:", size=9.5, color=MUTED))
    p.append(text(xs[3] + 78, y + 30, "нова", size=9.5, color=MUTED))
    p.append(text(xs[3] + 78, y + 44, "команда", size=9.5, color=MUTED))

    p.append(text(W / 2, H - 26,
                  "на кожен такт автомат у СВОЄМУ стані піднімає рівно потрібні лінії; "
                  "число тактів LOAD залежить від того, скільки крутилися в READ",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "fsm-load.svg"), W, H, *p,
           title="LOAD як автомат: стани, переходи й петля чекання пам'яті")


# ── proj: enable-order — порядок увімкнень: правильний проти хибного ──────────
# Ідея: адреса й mem_read мусять устоятися ПЕРЕД тим, як защіпувати; хибний
# порядок ловить сміття з ще не готової шини.
def fig_enable_order():
    W, H = 760, 340
    p = []
    lane_l, lane_r = 40, 400
    lane_w = 320

    def lane(x, ok, steps):
        col = FIELD if ok else POS
        head = "правильно" if ok else "гонка: сміття в регістрі"
        pp = [rect(x, 60, lane_w, 240, fill=(GRN_F if ok else RED_F),
                   stroke=col, sw=2, rx=10)]
        pp.append(text(x + lane_w / 2, 82, head, size=12.5, color=col, bold=True))
        ty = 108
        for i, (t, txt, bad) in enumerate(steps):
            c = POS if bad else INK
            pp.append(rect(x + 14, ty, 44, 26, fill=BG, stroke=MUTED, sw=1.2, rx=5))
            pp.append(text(x + 36, ty + 17, t, size=10, color=MUTED, bold=True))
            frag = fitbox(x + 66, ty, lane_w - 80, 26, txt, size=10.5,
                          fill=(RED_F if bad else BG),
                          stroke=(POS if bad else MUTED),
                          sw=(1.6 if bad else 1.1), color=c, bold=bad)
            pp.append(frag)
            ty += 38
        return pp

    p += lane(lane_l, True, [
        ("t1", "виставити адресу + mem_read", False),
        ("t2", "ЧЕКАТИ ready (шина стала)", False),
        ("t3", "тепер защіпнути дані", False),
        ("—", "у регістрі — вірне число", False),
    ])
    p += lane(lane_r, False, [
        ("t1", "виставити адресу + mem_read", False),
        ("t2", "защіпнути ОДРАЗУ (не чекав)", True),
        ("—", "шина ще не готова…", True),
        ("—", "у регістрі — сміття", True),
    ])

    p.append(text(W / 2, H - 20,
                  "та сама послідовність станів — різний ПОРЯДОК і момент увімкнення запису",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "enable-order.svg"), W, H, *p,
           title="Порядок увімкнень вирішує: устояти перед тим, як защіпувати")


# ── hist: аналогія Вілкса — програма керує машиною, мікропрограма керує керуванням ─
# Ідея вставки hist-microprogramming: те саме, що звичайна програма робить із
# машиною (рядок за рядком жене команди), мікропрограма робить із самим
# пристроєм керування (рядок за рядком жене мікрокоманди на керувальні лінії).
def fig_wilkes_analogy():
    W, H = 760, 380
    p = []

    p.append(text(W / 2, 52, "«Керування — це теж маленька програма»", size=13, color=INK, italic=True))

    # ── ліворуч: звичайна програма жене машину ──
    lx = 40
    p.append(rect(lx, 74, 320, 274, fill="#f6f8fb", stroke=BLU, sw=1.8, rx=14))
    p.append(text(lx + 160, 98, "ЗВИЧАЙНА ПРОГРАМА", size=12.5, color=BLU, bold=True))
    p.append(text(lx + 160, 116, "у пам'яті", size=10, color=MUTED, italic=True))
    prog = ["LOAD  R1, x", "ADD   R1, R2", "STORE R1, y"]
    py = 130
    for i, ln in enumerate(prog):
        hl = (i == 1)
        p.append(rect(lx + 40, py, 240, 26, fill=(BLU_F if hl else BG), stroke=BLU, sw=1.7 if hl else 1.1, rx=4))
        p.append(text(lx + 60, py + 17, ln, size=11, color=INK, anchor="start", bold=hl))
        py += 30
    p.append(arrow(lx + 160, py + 2, lx + 160, py + 26, color=BLU, sw=1.9))
    p.append(rect(lx + 55, py + 30, 210, 34, fill=BG, stroke=INK, sw=1.5, rx=7))
    p.append(text(lx + 160, py + 52, "процесор виконує", size=11, color=INK, bold=True))
    p.append(text(lx + 160, 340, "рядок за рядком → дії над даними", size=9.5, color=MUTED, italic=True))

    # ── праворуч: мікропрограма жене керування ──
    rx = 400
    p.append(rect(rx, 74, 320, 274, fill="#fffdf5", stroke=GLD, sw=1.8, rx=14))
    p.append(text(rx + 160, 98, "МІКРОПРОГРАМА", size=12.5, color=GLD, bold=True))
    p.append(text(rx + 160, 116, "у сховищі керування", size=10, color=MUTED, italic=True))
    micro = ["PC→адр · чит", "пам'ять→IR", "R1,R2→АЛП +"]
    my = 130
    for i, ln in enumerate(micro):
        hl = (i == 2)
        p.append(rect(rx + 40, my, 240, 26, fill=(GLD_F if hl else BG), stroke=GLD, sw=1.7 if hl else 1.1, rx=4))
        p.append(text(rx + 60, my + 17, ln, size=11, color=INK, anchor="start", bold=hl))
        my += 30
    p.append(arrow(rx + 160, my + 2, rx + 160, my + 26, color=GLD, sw=1.9))
    p.append(rect(rx + 55, my + 30, 210, 34, fill=BG, stroke=INK, sw=1.5, rx=7))
    p.append(text(rx + 160, my + 52, "керувальні лінії", size=11, color=INK, bold=True))
    p.append(text(rx + 160, 340, "рядок за рядком → увімкнення дротів", size=9.5, color=MUTED, italic=True))

    # містковий знак приблизної рівності
    p.append(text(W / 2, 210, "≈", size=30, color=MUTED, bold=True))

    render(os.path.join(OUT, "wilkes-analogy.svg"), W, H, *p,
           title="Здогад Вілкса: та сама ідея програми — на два рівні")


# ── hist: часова стрічка мікропрограмування ──────────────────────────────────
# Ідея -> перша реалізація -> комерційний прорив. Чесно: 1957 тест-версія перед 1958.
def fig_micro_timeline():
    W, H = 760, 300
    p = []
    axis_y = 150
    x0, x1 = 80, 680
    p.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2))
    p.append(arrow(x1 - 2, axis_y, x1 + 6, axis_y, color=INK, sw=2))

    marks = [
        (0.00, "1949", "EDSAC 1", "перший робочий\nкомп'ютер Вілкса", GRN, True),
        (0.26, "1951", "Стаття", "«The Best Way…»\nМанчестер, ідея", GLD, False),
        (0.57, "1957–58", "EDSAC 2", "перша робоча\nмікропрограма", RED, True),
        (0.92, "1964", "IBM /360", "комерційний\nпрорив", BLU, False),
    ]
    for t, year, name, note, col, below in marks:
        x = x0 + t * (x1 - x0)
        fillc = {GRN: GRN_F, GLD: GLD_F, RED: RED_F, BLU: BLU_F}[col]
        p.append(circle(x, axis_y, 7, fill=fillc, stroke=col, sw=2.4))
        if below:
            p.append(text(x, axis_y + 26, year, size=12.5, color=col, bold=True))
            p.append(rect(x - 72, axis_y + 34, 144, 60, fill=fillc, stroke=col, sw=1.6, rx=8))
            p.append(text(x, axis_y + 52, name, size=11.5, color=INK, bold=True))
            p.append(mtext(x, axis_y + 68, note, size=9.5, color=MUTED, lh=1.2))
        else:
            p.append(text(x, axis_y - 16, year, size=12.5, color=col, bold=True))
            p.append(rect(x - 72, axis_y - 94, 144, 60, fill=fillc, stroke=col, sw=1.6, rx=8))
            p.append(text(x, axis_y - 76, name, size=11.5, color=INK, bold=True))
            p.append(mtext(x, axis_y - 60, note, size=9.5, color=MUTED, lh=1.2))

    render(os.path.join(OUT, "micro-timeline.svg"), W, H, *p,
           title="Мікропрограмування: ідея → перша реалізація → прорив")


if __name__ == "__main__":
    fig_what_is_control()
    fig_decode_signals()
    fig_micro_steps()
    fig_hardwired_vs_micro()
    fig_fsm_load()
    fig_enable_order()
    fig_wilkes_analogy()
    fig_micro_timeline()
    print("OK: figures written to", OUT)
