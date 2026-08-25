# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «DS18B20 — цифровий давач температури (1-Wire)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def pin3(f, x, y, names):
    """Три контактні площадки корпусу TO-92 (GND · DQ · VDD) на осі y, зліва направо."""
    w = 150
    for i, (nm, col) in enumerate(names):
        cx = x + i * w
        f.append(circle(cx, y, 9, fill=BG, stroke=col, sw=2.2))
        f.append(text(cx, y + 30, nm, size=12, bold=True, color=col))
    return


# ── 1. Що всередині DS18B20: давач → АЦП → пам'ять → 1-Wire ──────────────────
def fig_inside():
    W, H = 940, 430
    f = [text(W / 2, 30, "Що всередині DS18B20: одна мікросхема від сенсора до цифри",
              size=16, bold=True)]

    # рамка мікросхеми
    bx, by, bw, bh = 70, 66, 800, 300
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=16))
    f.append(text(bx + 16, by + 24, "кристал DS18B20 (корпус TO-92)",
                  size=11.5, bold=True, color=MUTED, anchor="start"))

    # блоки конвеєра
    cy = by + 160
    blocks = [
        ("темпер.\nсенсор", "#eaf3fb", NEG, "band-gap: різниця\nнапруг → t°"),
        ("АЦП", "#eef7ee", FIELD, "16-бітне\nчисло"),
        ("пам'ять\n(scratchpad)", FILL, INK, "t° · TH/TL ·\nконфіг · CRC"),
        ("64-бітний\nROM-код", "#fdf2ea", POS, "унікальна\nадреса"),
    ]
    bw2 = 150
    gap = 40
    x0 = bx + 40
    centers = []
    for i, (name, fill, col, sub) in enumerate(blocks):
        x = x0 + i * (bw2 + gap)
        f.append(rect(x, cy - 40, bw2, 80, fill=fill, stroke=col, sw=1.8, rx=8))
        f.append(mtext(x + bw2 / 2, cy - 8, name, size=13, bold=True, color=col))
        f.append(mtext(x + bw2 / 2, cy + 58, sub, size=9.5, color=MUTED))
        centers.append(x + bw2 / 2)
        if i < 3:
            f.append(arrow(x + bw2 + 4, cy, x + bw2 + gap - 4, cy, color=INK, sw=2.0))

    # шина 1-Wire назовні від пам'яті/ROM
    dqx = bx + bw
    dqy = cy
    # лінія від блоку ROM праворуч до краю корпусу і назовні до контакту DQ
    f.append(line(centers[3] + bw2 / 2, cy, dqx, cy, color=INK, sw=2.0))
    f.append(line(dqx, cy, dqx + 40, cy, color=POS, sw=2.4))
    f.append(circle(dqx + 40, cy, 7, fill=BG, stroke=POS, sw=2.2))
    f.append(text(dqx + 40, cy - 16, "DQ", size=12, bold=True, color=POS))
    f.append(text(dqx + 40, cy + 26, "1 дріт даних", size=9.5, color=MUTED))

    # підпис знизу — суть
    f.append(mtext(W / 2, by + bh + 38,
                   "Уся аналогова частина (сенсор, АЦП, калібрування) схована в кристалі — "
                   "назовні виходить лише готове число по одному дроту DQ.",
                   size=11, color=INK))
    render(os.path.join(IMG, "ds18b20-inside.svg"), W, H, *f)


# ── 2. Шина 1-Wire: підтяжка й кілька давачів на одному дроті ────────────────
def fig_bus():
    W, H = 940, 470
    f = [text(W / 2, 30, "Шина 1-Wire: один дріт, підтяжка вгору, кілька давачів паралельно",
              size=15.5, bold=True)]

    # шина живлення VDD зверху, GND знизу
    vdd_y = 78
    gnd_y = 400
    x_mcu = 120
    x_end = 880
    f.append(line(x_mcu, vdd_y, x_end, vdd_y, color=POS, sw=2.4))
    f.append(text(x_mcu - 8, vdd_y - 8, "+3.3…5 В", size=11, bold=True, color=POS, anchor="end"))
    f.append(line(x_mcu, gnd_y, x_end, gnd_y, color=NEG, sw=2.4))
    f.append(text(x_mcu - 8, gnd_y + 6, "GND", size=11, bold=True, color=NEG, anchor="end"))

    # лінія даних DQ (посередині)
    dq_y = 240
    f.append(line(x_mcu, dq_y, x_end, dq_y, color=INK, sw=2.4))
    f.append(text((x_mcu + x_end) / 2, dq_y - 12, "лінія даних  DQ", size=12, bold=True, color=INK))

    # мікроконтролер зліва
    f.append(rect(x_mcu - 70, dq_y - 40, 70, 80, fill="#eef2ff", stroke=INK, sw=1.6, rx=8))
    f.append(mtext(x_mcu - 35, dq_y - 4, "МК\nGPIO", size=12, bold=True, color=INK))
    f.append(line(x_mcu - 70, dq_y, x_mcu - 78, dq_y, color=INK, sw=1.6))

    # резистор підтяжки від VDD до DQ (біля МК)
    rx = x_mcu + 30
    rmid = (vdd_y + dq_y) / 2
    rh = 46
    ry = rmid - rh / 2
    f.append(line(rx, vdd_y, rx, ry, color=INK, sw=1.8))
    f.append(line(rx, ry + rh, rx, dq_y, color=INK, sw=1.8))
    f.append(rect(rx - 15, ry, 30, rh, fill=BG, stroke=INK, sw=1.6, rx=3))
    f.append(text(rx + 24, rmid - 3, "4.7 кОм", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(rx + 24, rmid + 13, "підтяжка", size=9.5, color=MUTED, anchor="start"))
    f.append(circle(rx, dq_y, 3.5, fill=INK, stroke=INK, sw=1))

    # три давачі DS18B20, кожен між трьома шинами
    for i, sx in enumerate([360, 560, 760]):
        # корпус
        f.append(rect(sx - 46, dq_y - 28, 92, 56, fill="#f7f9fc", stroke=INK, sw=1.6, rx=8))
        f.append(text(sx, dq_y - 6, "DS18B20", size=11, bold=True, color=INK))
        f.append(text(sx, dq_y + 12, "#%d" % (i + 1), size=9.5, color=MUTED))
        # DQ до лінії даних
        f.append(circle(sx, dq_y, 3.5, fill=INK, stroke=INK, sw=1))
        # VDD угору
        f.append(line(sx + 30, dq_y - 28, sx + 30, vdd_y, color=POS, sw=1.8))
        f.append(circle(sx + 30, vdd_y, 3.5, fill=POS, stroke=POS, sw=1))
        f.append(text(sx + 34, dq_y - 20, "VDD", size=8.5, color=POS, anchor="start"))
        # GND униз
        f.append(line(sx - 30, dq_y + 28, sx - 30, gnd_y, color=NEG, sw=1.8))
        f.append(circle(sx - 30, gnd_y, 3.5, fill=NEG, stroke=NEG, sw=1))
        f.append(text(sx - 34, dq_y + 40, "GND", size=8.5, color=NEG, anchor="end"))

    # пояснення знизу
    f.append(mtext(W / 2, gnd_y + 44,
                   "Лінія DQ у спокої підтягнута до «+» резистором; давач лише «притягує» її до землі "
                   "(open-drain). Кожен давач має свій 64-бітний код, тож усі живуть на одному дроті.",
                   size=11, color=INK))
    render(os.path.join(IMG, "ds18b20-bus.svg"), W, H, *f)


# ── 3. Підключення: три дроти проти паразитного живлення (два дроти) ─────────
def fig_wiring():
    W, H = 940, 470
    f = [text(W / 2, 30, "Два способи під'єднати DS18B20", size=16, bold=True)]

    # ── ліворуч: нормальне живлення (3 дроти) ──
    lx = 60
    f.append(rect(lx, 56, 380, 360, fill=BG, stroke=MUTED, sw=1.4, rx=12))
    f.append(text(lx + 190, 82, "Нормальне живлення — 3 дроти", size=12.5, bold=True))

    # корпус давача
    dx, dy = lx + 60, 150
    f.append(rect(dx, dy, 120, 150, fill="#f7f9fc", stroke=INK, sw=1.8, rx=10))
    f.append(text(dx + 60, dy + 24, "DS18B20", size=12, bold=True))
    f.append(mtext(dx + 60, dy + 62, "плоским боком\nдо себе", size=9, color=MUTED))
    # три ніжки знизу
    legs = [("GND", NEG), ("DQ", POS), ("VDD", POS)]
    for i, (nm, col) in enumerate(legs):
        px = dx + 24 + i * 36
        f.append(line(px, dy + 150, px, dy + 180, color=col, sw=2.0))
        f.append(text(px, dy + 196, nm, size=10, bold=True, color=col))

    # цільові шини праворуч у блоці
    tx = lx + 250
    f.append(text(tx, 150, "→ GND", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(tx, 190, "→ GPIO", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(tx, 210, "   +4.7 кОм на +", size=9, color=MUTED, anchor="start"))
    f.append(text(tx, 250, "→ +3.3…5 В", size=11, bold=True, color=POS, anchor="start"))
    f.append(mtext(lx + 190, 392,
                   "VDD живить давач; конверсія швидка й надійна.",
                   size=10, color=INK))

    # ── праворуч: паразитне живлення (2 дроти) ──
    rx = 500
    f.append(rect(rx, 56, 380, 360, fill="#fffdf5", stroke=POS, sw=1.6, rx=12))
    f.append(text(rx + 190, 82, "Паразитне живлення — 2 дроти", size=12.5, bold=True, color=POS))

    dx2, dy2 = rx + 60, 150
    f.append(rect(dx2, dy2, 120, 150, fill="#f7f9fc", stroke=INK, sw=1.8, rx=10))
    f.append(text(dx2 + 60, dy2 + 24, "DS18B20", size=12, bold=True))
    legs2 = [("GND", NEG), ("DQ", POS), ("VDD", MUTED)]
    for i, (nm, col) in enumerate(legs2):
        px = dx2 + 24 + i * 36
        f.append(line(px, dy2 + 150, px, dy2 + 180, color=col, sw=2.0))
        f.append(text(px, dy2 + 196, nm, size=10, bold=True, color=col))
    # перемичка VDD→GND
    f.append(line(dx2 + 24, dy2 + 180, dx2 + 24 + 72, dy2 + 180, color=NEG, sw=2.0))
    f.append(text(dx2 + 60, dy2 + 214, "VDD з'єднано з GND", size=9, bold=True, color=NEG))

    tx2 = rx + 250
    f.append(text(tx2, 150, "→ GND", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(tx2, 190, "→ GPIO", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(tx2, 210, "   +4.7 кОм на +", size=9, color=MUTED, anchor="start"))
    f.append(mtext(rx + 190, 384,
                   "Давач краде живлення з лінії DQ. На час конверсії лінію\n"
                   "треба сильно підтягнути до «+» (strong pull-up).",
                   size=10, color=POS))
    render(os.path.join(IMG, "ds18b20-wiring.svg"), W, H, *f)


# ── 4. Один діалог з давачем: скидання → ROM-команда → функція → дані ────────
def fig_transaction():
    W, H = 960, 470
    f = [text(W / 2, 30, "Один вимір температури — це три акти діалогу по одному дроту",
              size=15.5, bold=True)]

    # три вертикальні колонки-акти
    cols = [
        ("Акт 1\nСКИДАННЯ", "#eef2ff", INK,
         ["майстер тримає", "лінію низько ≥480 мкс", "→ давач відповідає", "presence-імпульсом"]),
        ("Акт 2\nАДРЕСА (ROM)", "#eaf3fb", NEG,
         ["Skip ROM 0xCC —", "«усім»,", "або Match ROM 0x55", "+ 64-бітний код —", "одному за іменем"]),
        ("Акт 3\nФУНКЦІЯ", "#eef7ee", FIELD,
         ["Convert T 0x44 —", "«виміряй»;", "потім знову скидання,", "адреса, і", "Read Scratchpad 0xBE —", "забрати 9 байтів"]),
    ]
    bw, bh = 270, 300
    gap = 30
    x0 = (W - (3 * bw + 2 * gap)) / 2
    cy = 90
    cx_centers = []
    for i, (title_, fill, col, rows) in enumerate(cols):
        x = x0 + i * (bw + gap)
        f.append(rect(x, cy, bw, bh, fill=fill, stroke=col, sw=1.8, rx=12))
        f.append(mtext(x + bw / 2, cy + 30, title_, size=13.5, bold=True, color=col))
        yy = cy + 92
        for ln in rows:
            f.append(text(x + bw / 2, yy, ln, size=11, color=INK))
            yy += 22
        cx_centers.append(x + bw / 2)
        if i < 2:
            ax0 = x + bw + 3
            ax1 = x + bw + gap - 3
            f.append(arrow(ax0, cy + bh / 2, ax1, cy + bh / 2, color=MUTED, sw=2.2))

    f.append(mtext(W / 2, cy + bh + 40,
                   "Кожен акт — це послідовність тайм-слотів на лінії DQ. Спершу скидання будить шину, "
                   "потім ROM-команда вибирає, з ким говоримо, і аж тоді йде функція (виміряти чи прочитати).",
                   size=11, color=INK))
    render(os.path.join(IMG, "ds18b20-transaction.svg"), W, H, *f)


# ── 5. Неблокуюче читання: запустив конверсію → зайнявся іншим → забрав ──────
def fig_nonblocking():
    W, H = 960, 400
    f = [text(W / 2, 30, "Неблокуюче читання: конверсія триває сама, поки МК зайнятий іншим",
              size=15.5, bold=True)]

    # вісь часу
    t0 = 90
    t1 = 880
    ty = 130
    f.append(line(t0, ty, t1, ty, color=INK, sw=2.0))
    f.append(text(t1 + 4, ty + 4, "час", size=11, color=MUTED, anchor="start"))

    # позначки подій
    def tick(x, up, label, col):
        f.append(line(x, ty - 6, x, ty + 6, color=col, sw=2.0))
        yy = ty - 16 if up else ty + 26
        f.append(mtext(x, yy, label, size=10.5, bold=True, color=col))

    xa = t0 + 40          # запуск конверсії
    xb = xa + 470         # конверсія готова (≈750 мс на 12 біт)
    tick(xa, True, "requestTemperatures()\n(не чекаємо!)", NEG)
    tick(xb, True, "≥750 мс минуло →\ngetTempC(): забрати", FIELD)

    # смуга «давач рахує»
    f.append(rect(xa, ty + 40, xb - xa, 34, fill="#eef7ee", stroke=FIELD, sw=1.6, rx=8))
    f.append(text((xa + xb) / 2, ty + 62, "давач сам робить перетворення (нам платити нічого)",
                  size=10.5, color=FIELD))

    # смуга «МК працює»
    f.append(rect(xa, ty + 92, xb - xa, 34, fill="#eef2ff", stroke=NEG, sw=1.6, rx=8))
    f.append(text((xa + xb) / 2, ty + 114,
                  "МК тим часом: читає кнопки, крутить дисплей, рахує ПІД, опитує інші шини",
                  size=10.5, color=NEG))

    # хвіст після забору
    f.append(line(xb, ty, t1, ty, color=INK, sw=2.0, dash="4 4"))

    f.append(mtext(W / 2, ty + 170,
                   "Замість delay(750) на кожен вимір — запусти конверсію й повертайся аж коли час минув. "
                   "Одна лінія коду (перевірка millis) звільняє три чверті секунди на кожен давач.",
                   size=11, color=INK))
    render(os.path.join(IMG, "ds18b20-nonblocking.svg"), W, H, *f)


# ── 6. [історія] Один дріт живить і говорить: ідея, народжена в Dallas ───────
def fig_hist_onewire():
    """До вставки hist-dallas-1wire: чому «одна лінія = живлення + дані» була
    несподіванкою. Дві фази однієї й тієї ж лінії DQ — заряд і обмін."""
    W, H = 940, 470
    f = [text(W / 2, 30, "Винахід Dallas: один дріт і живить, і переносить дані",
              size=15.5, bold=True)]

    panels = [
        (60, "Лінія висока (спокій)", "#eef7ee", FIELD,
         "поки DQ підтягнута до «+»,\nструм через діод заряджає\nвнутрішній конденсатор ~800 пФ",
         True),
        (500, "Лінія зайнята (обмін)", "#fdf2ea", POS,
         "під час імпульсів DQ падає до нуля;\nчип живе з зарядженого\nконденсатора, від нього ж тактує",
         False),
    ]
    for px, title_, fill, col, note, charging in panels:
        pw = 380
        f.append(rect(px, 56, pw, 360, fill=fill, stroke=col, sw=1.6, rx=12))
        f.append(text(px + pw / 2, 82, title_, size=12.5, bold=True, color=col))

        # шина DQ
        dqy = 150
        bx0, bx1 = px + 28, px + pw - 28
        dq_col = POS if charging else INK
        f.append(line(bx0, dqy, bx1, dqy, color=dq_col, sw=2.6))
        f.append(text(px + 100, dqy - 12, "лінія DQ", size=11, bold=True, color=INK))
        lvl = "«1» — високо" if charging else "імпульси «0»/«1»"
        f.append(text(bx1, dqy - 12, lvl, size=9, color=MUTED, anchor="end"))

        # відгалуження від DQ униз до діода й конденсатора (лівіше, щоб не лізло на чип)
        dvx = px + 96
        f.append(circle(dvx, dqy, 3.5, fill=INK, stroke=INK, sw=1))
        f.append(line(dvx, dqy, dvx, dqy + 34, color=INK, sw=1.6))
        # діод-трикутник DQ → конденсатор
        f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" stroke-width="1.2"/>'
                 % (dvx - 7, dqy + 34, dvx + 7, dqy + 34, dvx, dqy + 48,
                    "#dff0df" if charging else "#fff", INK))
        f.append(line(dvx - 8, dqy + 48, dvx + 8, dqy + 48, color=INK, sw=1.6))
        f.append(line(dvx, dqy + 48, dvx, dqy + 70, color=INK, sw=1.6))
        # конденсатор — дві пластини
        capy = dqy + 70
        f.append(line(dvx - 12, capy, dvx + 12, capy, color=INK, sw=2.4))
        f.append(line(dvx - 12, capy + 8, dvx + 12, capy + 8, color=INK, sw=2.4))
        cap_col = FIELD if charging else POS
        # підписи конденсатора — ЛІВОРУЧ від пластин, поза лінією живлення (справа)
        f.append(text(dvx - 18, capy + 2, "≈800 пФ", size=9.5, bold=True, color=cap_col, anchor="end"))
        f.append(text(dvx - 18, capy + 18, "заряд" if charging else "живить чип",
                      size=9, color=cap_col, anchor="end"))

        # чип праворуч, живиться від вузла конденсатора
        cx, cy, cw, ch = px + pw - 160, 246, 130, 92
        f.append(rect(cx, cy, cw, ch, fill="#f7f9fc", stroke=INK, sw=1.8, rx=10))
        f.append(text(cx + cw / 2, cy + 34, "1-Wire чип", size=11, bold=True))
        f.append(text(cx + cw / 2, cy + 54, "(напр. давач)", size=9, color=MUTED))
        # живлення від правого краю конденсатора вниз і праворуч до чипа
        prx = dvx + 12
        pwy = cy + ch - 20
        f.append(line(prx, capy + 4, prx, pwy, color=cap_col, sw=1.6))
        f.append(line(prx, pwy, cx, pwy, color=cap_col, sw=1.6))

        f.append(mtext(px + pw / 2, 388, note, size=10, color=INK, lh=1.3))

    render(os.path.join(IMG, "hist-onewire-idea.svg"), W, H, *f)


# ── 7. [історія] Ім'я живе довше за фірму: Dallas → Maxim → Analog Devices ────
def fig_hist_lineage():
    """До вставки hist-dallas-1wire: три власники поспіль, але наскрізь усіх
    проходить незмінний префікс «DS…» у партномерах."""
    W, H = 960, 400
    f = [text(W / 2, 30, "Власник мінявся тричі — ім'я «DS…» лишилось те саме",
              size=16, bold=True)]

    owners = [
        (170, "Dallas\nSemiconductor", "1984", "заснована у Далласі;\nвигадала 1-Wire та iButton", NEG),
        (480, "Maxim\nIntegrated", "2001", "купила Dallas\n(завершено 11.04.2001)", INK),
        (790, "Analog\nDevices", "2021", "поглинула Maxim\n(завершено 26.08.2021)", FIELD),
    ]
    axis_y = 150
    f.append(line(100, axis_y, 860, axis_y, color=MUTED, sw=2.0))
    prev = None
    for cx, name, year, note, col in owners:
        f.append(circle(cx, axis_y, 8, fill=BG, stroke=col, sw=2.4))
        f.append(mtext(cx, axis_y - 46, name, size=13, bold=True, color=col, lh=1.15))
        f.append(text(cx, axis_y + 30, year, size=13, bold=True, color=col))
        f.append(mtext(cx, axis_y + 54, note, size=9.5, color=MUTED, lh=1.3))
        if prev is not None:
            f.append(arrow(prev + 78, axis_y, cx - 78, axis_y, color=INK, sw=2.0))
            f.append(text((prev + cx) / 2, axis_y - 12, "купує", size=10, italic=True, color=INK))
        prev = cx

    # наскрізна стрічка партномерів під усіма трьома
    ribbon_y = 306
    f.append(rect(150, ribbon_y - 26, 660, 52, fill="#eef2ff", stroke=INK, sw=1.6, rx=26))
    f.append(text(W / 2, ribbon_y - 3, "префікс  DS…   (DS1990 · DS1307 · DS18B20)",
                  size=13, bold=True, color=INK))
    f.append(text(W / 2, ribbon_y + 15, "той самий партномер живе крізь усіх власників",
                  size=9.5, color=MUTED))
    for cx, *_ in owners:
        f.append(line(cx, axis_y + 82, cx, ribbon_y - 26, color=MUTED, sw=1.2, dash="3,4"))

    render(os.path.join(IMG, "hist-ds-lineage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_bus()
    fig_wiring()
    fig_transaction()
    fig_nonblocking()
    fig_hist_onewire()
    fig_hist_lineage()
    print("OK: ds18b20 figures ->", IMG)
