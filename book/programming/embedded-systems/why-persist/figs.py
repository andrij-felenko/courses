# -*- coding: utf-8 -*-
# Фігури теми «Навіщо зберігати: конфігурація, калібрування, логи».
# svgkit імпортуємо, не переписуємо (AUTHORING §5). Вивід — у ./img/, імена-slug.
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── volatile-loss: що зникає з SRAM при вимкненні ─────────────────────────────
# Ідея: ліворуч (живлення є) у SRAM усе; праворуч (живлення зникло) лишається
# порожньо. Поточне значення зникло — не шкода; пароль/поправка/журнал — біда.
def fig_volatile_loss():
    W, H = 720, 340
    p = []
    bw, bh = 250, 210
    lx, rx = 70, W - 70 - bw
    top = 80

    # дві панелі: до і після
    p.append(rect(lx, top, bw, bh, fill="#eef4ff", stroke=LINE, sw=1.6))
    p.append(rect(rx, top, bw, bh, fill="#f7f7f7", stroke=LINE, sw=1.6, ))
    p.append(text(lx + bw / 2, top - 14, "SRAM — живлення є", size=13, bold=True, color=FIELD))
    p.append(text(rx + bw / 2, top - 14, "живлення зникло", size=13, bold=True, color=POS))

    rows = [
        ("поточне значення  21.7°", MUTED, "не шкода — міряють наново"),
        ("Wi-Fi пароль", INK, "відновити нізвідки"),
        ("поправка давача  −0.4°", INK, "відновити нізвідки"),
        ("журнал збоїв", INK, "відновити нізвідки"),
    ]
    ry = top + 34
    for i, (lab, col, _) in enumerate(rows):
        yy = ry + i * 44
        p.append(fitbox(lx + 16, yy, bw - 32, 32, lab, size=11, fill=BG, stroke=col, sw=1.4, color=col))
        # стрілка через прірву вимкнення
        p.append(arrow(lx + bw + 6, yy + 16, rx - 6, yy + 16, color=MUTED, sw=1.4))
        # на правій панелі — порожньо (усе стерто)
        p.append(text(rx + bw / 2, yy + 21, "—", size=18, color="#cbd0d6", bold=True))

    p.append(text(W / 2, top + bh + 34,
                  "поточне значення зникло — байдуже; решту відновити нізвідки",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "volatile-loss.svg"), W, H, *p,
           title="Вимкнення стирає всю SRAM — частину даних повернути нізвідки")


# ── three-kinds: три роди постійних даних ─────────────────────────────────────
# Ідея: три картки поряд — конфіг / калібрування / лог; під кожною — хто й як
# часто пише, і ціна втрати.
def fig_three_kinds():
    W, H = 760, 320
    p = []
    cw, ch = 210, 200
    gap = (W - 3 * cw) / 4
    top = 70
    cards = [
        ("Конфігурація", FIELD, "#eafaf0",
         ["налаштування", "пише користувач", "зрідка", "втрата → переналаштувати"]),
        ("Калібрування", NEG, "#eef4ff",
         ["поправки екземпляра", "пише завод — раз", "читають завжди", "втрата → давач бреше"]),
        ("Логи", POS, "#fdecea",
         ["запис подій у часі", "дописує прошивка", "часто, і росте", "втрата → загадка в полі"]),
    ]
    for i, (title_, col, fill, lines) in enumerate(cards):
        x = gap + i * (cw + gap)
        p.append(rect(x, top, cw, ch, fill=fill, stroke=col, sw=1.8))
        p.append(text(x + cw / 2, top + 28, title_, size=14, bold=True, color=col))
        p.append(line(x + 16, top + 40, x + cw - 16, top + 40, color=col, sw=1.2))
        for j, ln in enumerate(lines):
            p.append(fitbox(x + 14, top + 52 + j * 34, cw - 28, 26, ln, size=10,
                            fill=BG, stroke="#d7dde4", sw=1.0, color=INK))

    p.append(text(W / 2, top + ch + 30,
                  "три роди, що мусять пережити вимкнення — у кожного своя ціна втрати",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "three-kinds.svg"), W, H, *p,
           title="Три роди постійних даних")


# ── write-read: візерунки запису й читання ────────────────────────────────────
# Ідея: для кожного роду — дві смужки «запис» і «читання» різної густини, плюс
# позначка розміру; видно, що візерунки доступу різні.
def fig_write_read():
    W, H = 740, 320
    p = []
    rows = [
        ("Калібрування", "раз", "завжди", "дрібне", [0.5], "tight"),
        ("Конфіг", "зрідка", "часто", "мале", [0.2, 0.62], "mid"),
        ("Лог", "часто, росте", "рідко", "росте", [0.1, 0.24, 0.38, 0.52, 0.66, 0.80], "dense"),
    ]
    lx = 150
    track = 440
    top = 70
    rh = 70
    p.append(text(lx + track * 0.0, top - 24, "запис у часі →", size=11, color=MUTED, anchor="start", italic=True))
    for i, (name, wlab, rlab, size_lab, marks, _) in enumerate(rows):
        y = top + i * rh
        p.append(text(lx - 14, y + 14, name, size=12, bold=True, anchor="end", color=INK))
        # доріжка часу
        p.append(line(lx, y + 14, lx + track, y + 14, color="#cbd0d6", sw=2.0))
        for m in marks:
            mx = lx + m * track
            p.append(circle(mx, y + 14, 4.2, fill=POS, stroke=POS, sw=1))
        # підписи: коли пишуть / читають / розмір
        p.append(text(lx + track + 14, y + 6, "пишуть: " + wlab, size=10, color=POS, anchor="start"))
        p.append(text(lx + track + 14, y + 22, "читають: " + rlab, size=10, color=FIELD, anchor="start"))
        p.append(text(lx - 14, y + 30, size_lab, size=9, color=MUTED, anchor="end"))

    p.append(text(W / 2, top + 3 * rh + 4,
                  "різні візерунки доступу → різні механізми зберігання",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "write-read.svg"), W, H, *p,
           title="Чому одне сховище не годиться всім")


# ── where-goes: форма даних диктує сховище ────────────────────────────────────
# Ідея: дві групи джерел зліва, дві цілі справа; стрілки показують, що дрібне й
# іменоване → ключ-значення, велике й послідовне → файлова система / кільце.
def fig_where_goes():
    W, H = 720, 300
    p = []
    # джерела
    src = [
        (120, 90, "Конфіг\n(іменовані значення)", FIELD, "#eafaf0"),
        (120, 200, "Калібрування\n(кілька чисел)", NEG, "#eef4ff"),
    ]
    dst = [
        (W - 150, 90, "NVS\n«ключ–значення»", "#8a5fb0", "#f2ecf8"),
        (W - 150, 200, "Файлова система /\nкільцевий лог", POS, "#fdecea"),
    ]
    big = (120, 255, "Лог, великі дані\n(ростуть)", POS, "#fdecea")

    boxes = {}
    for x, y, lab, col, fill in src + dst:
        b, bw, bh = textbox(x, y, lab, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.7)
        boxes[(x, y)] = (bw, bh)
        p.append(b)
    # «великі дані» — окремо, веде до файлової системи
    b, bw, bh = textbox(big[0], big[1], big[2], size=11, bold=True, color=big[3], fill=big[4], stroke=big[3], sw=1.7)
    p.append(b)

    # стрілки: дрібне → NVS
    p.append(arrow(120 + boxes[(120, 90)][0] / 2, 90, W - 150 - boxes[(W - 150, 90)][0] / 2, 90, color="#8a5fb0", sw=1.8))
    p.append(arrow(120 + boxes[(120, 200)][0] / 2, 200, W - 150 - boxes[(W - 150, 90)][0] / 2, 100, color="#8a5fb0", sw=1.6))
    # велике → файлова система
    p.append(arrow(big[0] + bw / 2, big[1], W - 150 - boxes[(W - 150, 200)][0] / 2, 205, color=POS, sw=1.8))

    p.append(text(W / 2, H - 22, "дрібне й іменоване — в одне; велике, що росте, — в інше",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "where-goes.svg"), W, H, *p,
           title="Форма даних диктує сховище")


# ── thermostat: що зберігати, а що ні ─────────────────────────────────────────
# Ідея: дві колонки — «у Flash» (3 роди) і «лишити SRAM» (поточне значення).
def fig_thermostat():
    W, H = 720, 320
    p = []
    cw, ch = 300, 210
    lx, rx = 60, W - 60 - cw
    top = 70
    p.append(rect(lx, top, cw, ch, fill="#f3f7ff", stroke=NEG, sw=1.8))
    p.append(rect(rx, top, cw, ch, fill="#f7f7f7", stroke=MUTED, sw=1.6))
    p.append(text(lx + cw / 2, top - 14, "ЗБЕРЕГТИ у Flash", size=13, bold=True, color=NEG))
    p.append(text(rx + cw / 2, top - 14, "лишити SRAM", size=13, bold=True, color=MUTED))

    keep = [
        ("задана температура  22.0°", "конфігурація — задав користувач", FIELD),
        ("поправка давача  −0.4°", "калібрування — цей термістор", NEG),
        ("журнал збоїв", "лог — коли й чому гас обігрів", POS),
    ]
    for i, (a, b, col) in enumerate(keep):
        y = top + 24 + i * 60
        p.append(fitbox(lx + 16, y, cw - 32, 30, a, size=11, fill=BG, stroke=col, sw=1.5, bold=True, color=INK))
        p.append(text(lx + 16, y + 46, b, size=9.5, color=col, anchor="start"))

    p.append(fitbox(rx + 16, top + 70, cw - 32, 34, "поточна температура  21.7°",
                    size=11, fill=BG, stroke=MUTED, sw=1.5, bold=True, color=INK))
    p.append(text(rx + cw / 2, top + 128, "міряється наново щосекунди —", size=10, color=MUTED))
    p.append(text(rx + cw / 2, top + 144, "у Flash їй не місце", size=10, color=MUTED))

    p.append(text(W / 2, top + ch + 30, "бережемо лише те, чого не відновити заново",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "thermostat.svg"), W, H, *p,
           title="Термостат: що зберігати, а що ні")


# ── lifecycle: коли що пишуть і читають за життя пристрою ──────────────────────
# Ідея: вісь часу від заводу до сервісу; три роди заходять у свій момент запису,
# а читаються наскрізь.
def fig_lifecycle():
    W, H = 760, 320
    p = []
    ox, oy = 70, 250
    aw = W - 140
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(text(ox + aw, oy + 22, "час життя пристрою", size=11, color=INK, italic=True, anchor="end"))

    stages = [("завод", 0.06), ("налаштування", 0.34), ("робота", 0.64), ("сервіс", 0.94)]
    for lab, f in stages:
        x = ox + f * aw
        p.append(line(x, oy - 6, x, oy + 6, color=INK, sw=1.6))
        p.append(text(x, oy + 22, lab, size=10, color=MUTED))

    # три смужки «запису», що починаються у свій момент і тягнуться далі (читання)
    bars = [
        ("Калібрування", 0.06, NEG, "#eef4ff", "пишуть раз"),
        ("Конфігурація", 0.34, FIELD, "#eafaf0", "пишуть зрідка"),
        ("Лог", 0.64, POS, "#fdecea", "дописують у роботі"),
    ]
    by = 80
    for i, (name, start, col, fill, note) in enumerate(bars):
        y = by + i * 46
        x0 = ox + start * aw
        x1 = ox + 0.94 * aw
        p.append(rect(x0, y, x1 - x0, 30, fill=fill, stroke=col, sw=1.6))
        p.append(text(x0 + 8, y + 19, name, size=11, bold=True, color=col, anchor="start"))
        p.append(text(x1 - 6, y + 19, note, size=9, color=col, anchor="end"))

    p.append(text(W / 2, oy + 46, "пишуть у свій момент, а читають усі — поки пристрій живе",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "lifecycle.svg"), W, H, *p,
           title="Життя пристрою в часі: коли що пишуть і читають")


# ── ring: кільцевий лог (вставка proj) ────────────────────────────────────────
# Ідея: сектори по колу; голова пише, сектор попереду стирається наперед.
def fig_ring():
    import math
    W, H = 640, 380
    cx, cy = W / 2, 196
    R = 120
    n = 8
    p = []
    head = 2  # індекс сектора-голови
    for i in range(n):
        a0 = -math.pi / 2 + (i) * 2 * math.pi / n
        a1 = -math.pi / 2 + (i + 1) * 2 * math.pi / n
        am = (a0 + a1) / 2
        # колір сектора
        if i == head:
            fill, stroke = "#eafaf0", FIELD
        elif i == (head + 1) % n:
            fill, stroke = "#fdecea", POS
        else:
            fill, stroke = FILL, LINE
        # сектор як шлях
        x0, y0 = cx + R * math.cos(a0), cy + R * math.sin(a0)
        x1, y1 = cx + R * math.cos(a1), cy + R * math.sin(a1)
        ri = 56
        xi0, yi0 = cx + ri * math.cos(a0), cy + ri * math.sin(a0)
        xi1, yi1 = cx + ri * math.cos(a1), cy + ri * math.sin(a1)
        d = ("M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f L %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f Z"
             % (x0, y0, R, R, x1, y1, xi1, yi1, ri, ri, xi0, yi0))
        p.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (d, fill, stroke))
        # номер сектора
        rm = (R + ri) / 2
        p.append(text(cx + rm * math.cos(am), cy + rm * math.sin(am) + 4, str(i + 1), size=12, color=MUTED))

    # підписи голови й стирання
    ha = -math.pi / 2 + (head + 0.5) * 2 * math.pi / n
    ea = -math.pi / 2 + (head + 1.5) * 2 * math.pi / n
    p.append(text(cx + (R + 30) * math.cos(ha), cy + (R + 30) * math.sin(ha), "голова: пишемо",
                  size=11, color=FIELD, bold=True))
    p.append(text(cx + (R + 38) * math.cos(ea), cy + (R + 38) * math.sin(ea), "стираємо наперед",
                  size=11, color=POS, bold=True))
    # стрілка напрямку по колу
    p.append(text(cx, cy + 4, "по колу →", size=11, color=MUTED))

    p.append(text(W / 2, H - 24, "записи лягають у всі сектори по черзі — знос розмазується сам",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "ring.svg"), W, H, *p,
           title="Кільцевий лог: пишемо в голову, стираємо наперед, по колу")


# ── record: запис із номером і міткою; відновлення шукає найбільший номер ──────
def fig_record():
    W, H = 720, 320
    p = []
    # один запис — три поля
    rx, ry, rw, rh = 60, 80, 600, 60
    fields = [("№ (наскрізний)", "#eef4ff", 0.30), ("подія / дані", BG, 0.45), ("мітка цілості", "#eafaf0", 0.25)]
    x = rx
    for lab, fill, frac in fields:
        w = rw * frac
        p.append(rect(x, ry, w, rh, fill=fill, stroke=LINE, sw=1.5, rx=0))
        p.append(fitbox(x + 6, ry + rh / 2 - 12, w - 12, 24, lab, size=11, fill="none", stroke="none", color=INK))
        x += w
    p.append(text(rx, ry - 12, "структура запису", size=11, color=MUTED, anchor="start", italic=True))

    # відновлення: ланцюжок номерів, найбільший добрий — найновіший
    cy = 220
    seq = [("№7 ✓", FIELD), ("№8 ✓", FIELD), ("№9 ✓  ← найновіший", FIELD), ("№10 ✗ обірваний", POS)]
    bw, gap = 150, 14
    total = len(seq) * bw + (len(seq) - 1) * gap
    x = (W - total) / 2
    p.append(text(W / 2, cy - 28, "відновлення: найбільший номер із доброю міткою — найновіший",
                  size=11, color=MUTED))
    for lab, col in seq:
        p.append(fitbox(x, cy, bw, 38, lab, size=10.5, fill=BG, stroke=col, sw=1.6, bold=True, color=col))
        x += bw + gap

    p.append(text(W / 2, H - 22, "обірваний запис (хибна мітка) відновлення просто пропускає",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "record.svg"), W, H, *p,
           title="Запис несе наскрізний номер і мітку цілості")


# ══ Фігури вставки hist-flash.md ══════════════════════════════════════════════

# ── memory-gap: пам'ять до Flash — таблиця властивостей ────────────────────────
# Ідея: рядки-властивості × стовпці-типи; видно, що кожному типу чогось бракує,
# а Flash закриває всі клітинки одразу.
def fig_memory_gap():
    W, H = 760, 320
    p = []
    cols = ["RAM", "ROM", "EPROM", "EEPROM", "Flash"]
    rows = [
        ("пам'ятає без живлення?", ["ні", "так", "так", "так", "так"]),
        ("можна переписати?", ["так", "ні", "УФ", "побайтово", "блоками"]),
        ("щільна / дешева?", ["—", "так", "так", "ні", "так"]),
        ("зручна в роботі?", ["так", "—", "виймати, УФ", "повільно", "так"]),
    ]
    lx, top = 230, 70
    cw = (W - lx - 30) / len(cols)
    rh = 44
    # шапка стовпців
    for j, c in enumerate(cols):
        x = lx + j * cw
        last = (c == "Flash")
        p.append(rect(x, top, cw, 30, fill=("#eafaf0" if last else FILL),
                      stroke=(FIELD if last else LINE), sw=(2 if last else 1.3), rx=0))
        p.append(text(x + cw / 2, top + 20, c, size=12, bold=True, color=(FIELD if last else INK)))
    # рядки
    for i, (rlab, vals) in enumerate(rows):
        y = top + 30 + i * rh
        p.append(text(lx - 12, y + rh / 2 + 4, rlab, size=10.5, anchor="end", color=INK))
        for j, v in enumerate(vals):
            x = lx + j * cw
            last = (cols[j] == "Flash")
            p.append(rect(x, y, cw, rh, fill=("#f3fbf6" if last else BG),
                          stroke="#d7dde4", sw=1.0, rx=0))
            p.append(fitbox(x + 4, y + rh / 2 - 11, cw - 8, 22, v, size=9.5,
                            fill="none", stroke="none", color=(FIELD if last else INK)))

    p.append(text(W / 2, top + 30 + len(rows) * rh + 26,
                  "Flash закрив прогалину: незабутливий, як ROM, переписуваний електрично, дешевий і щільний",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "memory-gap.svg"), W, H, *p,
           title="Пам'ять до Flash: кожна щось та й не вміла")


# ── nor-nand: два різновиди Flash ─────────────────────────────────────────────
def fig_nor_nand():
    W, H = 740, 300
    p = []
    cw, ch = 300, 190
    lx, rx = 50, W - 50 - cw
    top = 70
    cards = [
        (lx, "NOR (1984)", NEG, "#eef4ff",
         ["довільний доступ до байта", "швидке читання", "виконання коду «на місці»",
          "→ програмна пам'ять чипів"], "Flash вашого ESP32 — цього роду"),
        (rx, "NAND (1987)", "#8a5fb0", "#f2ecf8",
         ["доступ блоками, не байтом", "набагато щільніша й дешевша", "ідеальна під великі обсяги",
          "→ SD-картки, флешки, SSD"], "на чому лежать ваші файли"),
    ]
    for x, title_, col, fill, lines, foot in cards:
        p.append(rect(x, top, cw, ch, fill=fill, stroke=col, sw=1.8))
        p.append(text(x + cw / 2, top + 26, title_, size=14, bold=True, color=col))
        p.append(line(x + 16, top + 36, x + cw - 16, top + 36, color=col, sw=1.2))
        for j, ln in enumerate(lines):
            p.append(text(x + 18, top + 60 + j * 24, "• " + ln, size=10.5, color=INK, anchor="start"))
        p.append(text(x + cw / 2, top + ch - 14, foot, size=10, color=col, italic=True))

    p.append(text(W / 2, top + ch + 30,
                  "NOR — щоб виконувати код; NAND — щоб зберігати гори даних; поділ живий донині",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "nor-nand.svg"), W, H, *p,
           title="Два різновиди Flash від Масуоки в Toshiba")


# ── credit: винахід тут, нагорода деінде ──────────────────────────────────────
def fig_credit():
    W, H = 760, 300
    p = []
    top = 80
    boxes = [
        (180, top, 260, 96, "Toshiba (Японія)",
         "Масуока — винахідник;\nАріідзумі назвав «flash»;\nкомпанія скупо віддячила", INK, FILL),
        (W - 180, top, 260, 96, "Intel (США)",
         "підхопила NOR-flash і першою\nагресивно її комерціалізувала\n(чип на 256 Кбіт, 1988)", NEG, "#eef4ff"),
    ]
    for cx, cy, w, h, title_, body, col, fill in boxes:
        p.append(rect(cx - w / 2, cy, w, h, fill=fill, stroke=col, sw=1.7))
        p.append(text(cx, cy + 22, title_, size=13, bold=True, color=col))
        p.append(mtext(cx, cy + 42, body, size=10, color=INK))
    # стрілка винахід → ринок
    p.append(arrow(180 + 130, top + 48, W - 180 - 130, top + 48, color=MUTED, sw=1.8))
    p.append(text(W / 2, top + 40, "винахід", size=10, color=MUTED))
    p.append(text(W / 2, top + 64, "ринок", size=10, color=MUTED))
    # позов
    p.append(fitbox(W / 2 - 190, top + 116, 380, 50,
                    "Масуока згодом судився з Toshiba за винагороду;\nстав професором університету Тохоку",
                    size=10, fill="#fdecea", stroke=POS, sw=1.5, color=INK))

    p.append(text(W / 2, H - 38,
                  "винахід — Масуоки й Аріідзумі (Toshiba); масовий ринок розкрутили й інші",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, H - 20,
                  "назвати справжнього автора — не дрібниця, а точність інженерної культури",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "credit.svg"), W, H, *p,
           title="Винайшли в Toshiba — а слава й гроші розійшлися")


if __name__ == "__main__":
    fig_volatile_loss()
    fig_three_kinds()
    fig_write_read()
    fig_where_goes()
    fig_thermostat()
    fig_lifecycle()
    fig_ring()
    fig_record()
    fig_memory_gap()
    fig_nor_nand()
    fig_credit()
    print("OK: figures written to", OUT)
