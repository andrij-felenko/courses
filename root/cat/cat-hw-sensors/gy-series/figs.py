# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «GY-серія (брейкаут-модулі)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Анатомія GY-плати: голий чип → обвʼязка → гребінка 2.54 ────────────────
def fig_anatomy():
    W, H = 960, 520
    f = [text(W / 2, 32, "Що робить брейкаут: голий SMD-чип стає зручним модулем",
              size=16, bold=True)]

    # Ліворуч — «голий чип» (недоступний руками)
    lx, ly, lw, lh = 60, 120, 190, 190
    f.append(rect(lx, ly, lw, lh, fill="#fdecea", stroke=POS, sw=2, rx=12))
    # мікросхема з дрібними виводами
    chx, chy, chw, chh = lx + 55, ly + 60, 80, 62
    f.append(rect(chx, chy, chw, chh, fill="#2b2b2b", stroke="#000", sw=1.5, rx=4))
    f.append(text(chx + chw / 2, chy + chh / 2 + 4, "чип", size=11, color="#fff", bold=True))
    for i in range(6):  # дрібні ніжки
        px = chx + 8 + i * ((chw - 16) / 5)
        f.append(line(px, chy + chh, px, chy + chh + 9, color=MUTED, sw=1.4))
        f.append(line(px, chy - 9, px, chy, color=MUTED, sw=1.4))
    f.append(mtext(lx + lw / 2, ly + 26, "Голий чип",
                   size=12.5, bold=True, color=POS, lh=1.15))
    f.append(mtext(lx + lw / 2, ly + lh - 34,
                   "виводи 0.5 мм,\nживлення лише 3.3 В,\nруками не взяти",
                   size=9.5, color=INK, lh=1.35))

    # Стрілка «брейкаут»
    ax1, ax2, ay = lx + lw + 10, lx + lw + 92, ly + lh / 2
    f.append(arrow(ax1, ay, ax2, ay, color=FIELD, sw=2.4))
    f.append(text((ax1 + ax2) / 2, ay - 14, "брейкаут", size=11, bold=True, color=FIELD))

    # Праворуч — готовий модуль-плитка з обвʼязкою + гребінкою
    mx, my, mw, mh = lx + lw + 100, 96, 430, 300
    f.append(rect(mx, my, mw, mh, fill="#eef6ef", stroke=FIELD, sw=2.2, rx=14))
    f.append(text(mx + mw / 2, my + 26, "Готовий модуль GY-xxx", size=13, bold=True, color=FIELD))

    # чип у центрі модуля
    ccx, ccy = mx + mw / 2, my + 118
    f.append(rect(ccx - 46, ccy - 30, 92, 60, fill="#2b2b2b", stroke="#000", sw=1.5, rx=5))
    f.append(mtext(ccx, ccy - 3, "той самий\nчип", size=9.5, color="#fff", bold=True, lh=1.2))

    # блоки обвʼязки навколо
    def part(px, py, label, sub, accent):
        b, w, _ = textbox(px, py, label + "\n" + sub, size=9.5, fill="#ffffff",
                          stroke=accent, min_w=118, pad=8, color=INK)
        return b
    f.append(part(mx + 92,  my + 210, "LDO 3.3 В", "662K / XC6206", NEG))
    f.append(part(mx + 232, my + 210, "підтяжки", "R на SDA/SCL", "#8e44ad"))
    f.append(part(mx + 360, my + 118, "рівні", "MOSFET (не всі)", POS))
    # гребінка 2.54 знизу
    hy = my + mh - 20
    f.append(text(mx + mw / 2, hy + 12, "гребінка-штирки 2.54 мм — у макетну плату", size=10, color=MUTED))
    for i in range(8):
        hx = ccx - 84 + i * 24
        f.append(line(hx, my + mh - 44, hx, hy, color="#c9a227", sw=3))
        f.append(circle(hx, my + mh - 44, 3.2, fill="#c9a227", stroke="#8a6d0f", sw=1))

    # підсумок унизу
    b, _, _ = textbox(W / 2, 470,
                      "Плата GY несе той самий давач, що й «голий» чип, але додає живлення 3.3 В,\n"
                      "підтяжки шини й крок 2.54 мм — тому будь-який GY-модуль підключається однаково просто.",
                      size=11, fill="#eef2f8", stroke=NEG, pad=10)
    f.append(b)
    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 2. Три класи GY за живленням/рівнями — головна пастка ─────────────────────
def fig_power_map():
    W, H = 980, 580
    f = [text(W / 2, 32, "GY-модулі не однакові за живленням: три класи, які треба розрізняти",
              size=16, bold=True)]

    cols = [
        ("3.3 В — тільки", POS, "#fdecea",
         "нема регулятора,\nнема зсуву рівнів",
         ["VCC = 3.3 В (макс 3.6)", "5 В спалить чип", "лог. виводи 3.3 В",
          "з 5-В МК — потрібен", "зовнішній зсув рівнів"],
         "GY-BMP280-3.3"),
        ("5 В-сумісний\n(повний)", FIELD, "#eef6ef",
         "є LDO 3.3 В +\nMOSFET-зсув на шині",
         ["VCC = 3.3…5 В", "живи 5 В сміливо", "виводи терплять 5 В", "готовий до 5-В МК",
          "(Arduino Uno) прямо"],
         "GY-63 (MS5611)"),
        ("з регулятором,\nбез зсуву", NEG, "#eef2f8",
         "є LDO 3.3 В,\nАЛЕ виводи 3.3 В",
         ["VCC = 3.3…5 В", "живи 5 В — чип цілий", "виводи лише 3.3 В!", "SCL/SDA з 5-В МК —",
          "радше зсув рівнів"],
         "GY-521 (MPU-6050)"),
    ]

    n = len(cols)
    gap = 26
    x0 = 44
    cw = (W - 2 * x0 - (n - 1) * gap) / n
    top = 78
    ch = 350

    for i, (name, accent, fill, defn, items, ex) in enumerate(cols):
        x = x0 + i * (cw + gap)
        f.append(rect(x, top, cw, ch, fill=fill, stroke=accent, sw=2.2, rx=13))
        f.append(mtext(x + cw / 2, top + 30, name, size=14, bold=True, color=accent, lh=1.15))
        f.append(line(x + 18, top + 70, x + cw - 18, top + 70, color=accent, sw=1.2))
        f.append(mtext(x + cw / 2, top + 96, defn, size=10.5, color=INK, lh=1.35))
        iy = top + 150
        for it in items:
            f.append(text(x + cw / 2, iy, it, size=10, color=INK))
            iy += 24
        # приклад-представник
        b, _, _ = textbox(x + cw / 2, top + ch - 26, "напр. " + ex,
                          size=10, fill="#ffffff", stroke=accent, pad=7, bold=True, color=accent)
        f.append(b)

    # золоте правило внизу
    b, _, _ = textbox(W / 2, top + ch + 66,
                      "ЗОЛОТЕ ПРАВИЛО: «живити 5 В» ≠ «5-вольтова логіка».\n"
                      "Наявність регулятора рятує ЧИП від 5 В на VCC, але виводи SDA/SCL/OUT можуть\n"
                      "лишатися 3.3-вольтовими — перевіряй саме їх, перш ніж чіпати 5-В мікроконтролер.",
                      size=11, fill="#fdecea", stroke=POS, pad=11)
    f.append(b)
    render(os.path.join(IMG, "power-map.svg"), W, H, *f)


# ── 3. Як читати GY-модуль: напис на платі бреше про чип ──────────────────────
def fig_decode():
    W, H = 900, 470
    f = [text(W / 2, 32, "Число GY нічого не гарантує — правду каже лише чип",
              size=16, bold=True)]

    # плата з написом HMC5883L
    bx, by, bw, bh = 70, 96, 250, 150
    f.append(rect(bx, by, bw, bh, fill="#eef2f8", stroke=NEG, sw=2, rx=12))
    f.append(text(bx + bw / 2, by + 30, "плата з написом", size=11, color=MUTED))
    f.append(text(bx + bw / 2, by + 58, "«GY-271 HMC5883L»", size=13, bold=True, color=INK))
    f.append(rect(bx + bw / 2 - 42, by + 78, 84, 44, fill="#2b2b2b", stroke="#000", sw=1.5, rx=4))
    f.append(text(bx + bw / 2, by + 104, "? чип ?", size=11, color="#fff", bold=True))

    # дві розвилки: реальність
    arrow_x = bx + bw + 20
    f.append(arrow(arrow_x, by + bh / 2, arrow_x + 70, by + bh / 2 - 46, color=MUTED, sw=2))
    f.append(arrow(arrow_x, by + bh / 2, arrow_x + 70, by + bh / 2 + 46, color=MUTED, sw=2))

    ox = arrow_x + 82
    # варіант A — справжній HMC (рідкість)
    a, _, _ = textbox(ox + 150, by + 8, "HMC5883L (Honeywell)\nадреса I²C 0x1E\nзнято з виробництва ~2020",
                      size=10.5, fill="#eef6ef", stroke=FIELD, pad=9)
    f.append(a)
    # варіант B — QMC-клон (масовий)
    b, _, _ = textbox(ox + 150, by + bh - 4, "QMC5883L (QST) — клон\nадреса I²C 0x0D\nінші регістри, інший код",
                      size=10.5, fill="#fdecea", stroke=POS, pad=9)
    f.append(b)

    # порада внизу — сканер I2C
    b2, _, _ = textbox(W / 2, 386,
                       "ЩО РОБИТИ: не вір шовкографії — запусти I²C-сканер.\n"
                       "Відповів 0x1E — це справжній HMC; відповів 0x0D — це QMC-клон,\n"
                       "і бібліотеку та адресу треба брати під QMC.",
                       size=11.5, fill="#eef2f8", stroke=NEG, pad=11)
    f.append(b2)
    render(os.path.join(IMG, "decode.svg"), W, H, *f)


# ── 4. Три хвилі 2003–2013, що злилися у GY-брейкаут (для hist-вставки) ───────
def fig_three_waves():
    W, H = 1040, 560
    f = [text(W / 2, 34, "Три незалежні хвилі 2003–2013 зійшлися в одному дешевому модулі",
              size=16, bold=True)]

    # три доріжки-хвилі
    lanes = [
        ("ПОПИТ: любителі й макетки", NEG, "#eef2f8",
         [("2003", "Wiring (Х. Барраґан)"),
          ("2005", "Arduino, ATmega8"),
          ("2008+", "мільйони макетувальників,\nусі на 2.54 мм і 3.3 В")]),
        ("ПРОПОЗИЦІЯ: фабрики Шеньчженя", FIELD, "#eef6ef",
         [("2000-ті", "шаньчжай-мережа"),
          ("гунбань", "спільні готові плати,\nвільно копіюють одна одну"),
          ("гункай", "відкрите ділення платами\n(термін bunnie Huang)")]),
        ("ДЕТАЛЬ: MEMS-давачі дешевшають", POS, "#fdecea",
         [("2006", "Wii, акселерометр у грі"),
          ("2007", "iPhone: давачі в кожній кишені"),
          ("2011", "MPU-6050: 6 осей в 1 чипі,\nобсяг збиває ціну до центів")]),
    ]

    n = len(lanes)
    gap = 24
    x0 = 40
    cw = (W - 2 * x0 - (n - 1) * gap) / n
    top = 76
    lane_h = 372

    for i, (name, accent, fill, steps) in enumerate(lanes):
        x = x0 + i * (cw + gap)
        f.append(rect(x, top, cw, lane_h, fill=fill, stroke=accent, sw=2.2, rx=13))
        f.append(mtext(x + cw / 2, top + 28, name, size=12.5, bold=True, color=accent, lh=1.15))
        f.append(line(x + 16, top + 46, x + cw - 16, top + 46, color=accent, sw=1.2))
        sy = top + 78
        prev_cy = None
        for yr, txt in steps:
            # маркер-рік
            f.append(circle(x + 34, sy, 6, fill=accent, stroke="#fff", sw=1.6))
            if prev_cy is not None:
                f.append(line(x + 34, prev_cy + 6, x + 34, sy - 6, color=accent, sw=1.6))
            f.append(text(x + 54, sy - 8, yr, size=11, bold=True, color=accent, anchor="start"))
            f.append(mtext(x + 54, sy + 9, txt, size=9.6, color=INK, anchor="start", lh=1.25))
            nlines = txt.count("\n") + 1
            step = 44 + (nlines - 1) * 13
            prev_cy = sy
            sy += step

    # стрілки вниз, що сходяться до підсумку
    conv_y = top + lane_h + 12
    for i in range(n):
        x = x0 + i * (cw + gap) + cw / 2
        f.append(arrow(x, top + lane_h + 2, W / 2, conv_y + 22, color=MUTED, sw=1.8))

    b, _, _ = textbox(W / 2, conv_y + 54,
                      "= вигідно продавати КОЖЕН чип на власній платці 2.54 мм.\n"
                      "Так народилися безіменні GY-номери й десятки фірм-двійників на ту саму плату.",
                      size=11.5, fill="#fff7e6", stroke="#c9a227", pad=11)
    f.append(b)
    render(os.path.join(IMG, "three-waves.svg"), W, H, *f)


# ── 5. Партномер чипа vs GY-номер: що гарантує, а що ні (для hist-вставки) ────
def fig_partno_vs_gy():
    W, H = 940, 430
    f = [text(W / 2, 32, "Партномер чипа — контракт заводу; GY-номер — лише ярлик форм-фактора",
              size=15.5, bold=True)]

    # ліва колонка — партномер (тверде)
    lx, ly, lw, lh = 48, 78, 400, 268
    f.append(rect(lx, ly, lw, lh, fill="#eef6ef", stroke=FIELD, sw=2.2, rx=13))
    f.append(text(lx + lw / 2, ly + 30, "Партномер: напр. MPU-6050", size=13.5, bold=True, color=FIELD))
    f.append(line(lx + 20, ly + 46, lx + lw - 20, ly + 46, color=FIELD, sw=1.2))
    rows_l = [
        "видає один власник кремнію (InvenSense)",
        "закріплений datasheet-ом і реєстрами",
        "той самий скрізь: адреса, біти, поведінка",
        "змінився чип — змінився й номер",
    ]
    yy = ly + 74
    for r in rows_l:
        f.append(text(lx + 22, yy, "•", size=13, bold=True, color=FIELD, anchor="start"))
        f.append(mtext(lx + 40, yy, r, size=10.6, color=INK, anchor="start", lh=1.2))
        yy += 44

    # права колонка — GY-номер (мʼяке)
    rx, ry, rw, rh = lx + lw + 44, 78, 400, 268
    f.append(rect(rx, ry, rw, rh, fill="#fdecea", stroke=POS, sw=2.2, rx=13))
    f.append(text(rx + rw / 2, ry + 30, "GY-номер: напр. GY-521", size=13.5, bold=True, color=POS))
    f.append(line(rx + 20, ry + 46, rx + rw - 20, ry + 46, color=POS, sw=1.2))
    rows_r = [
        "нічий: клеїть будь-яка складальня Шеньчженя",
        "фіксує розмір, розводку, гребінку 2.54 мм",
        "начинку можуть тихо замінити (HMC → QMC)",
        "десятки фірм-двійників під тим самим числом",
    ]
    yy = ry + 74
    for r in rows_r:
        f.append(text(rx + 22, yy, "•", size=13, bold=True, color=POS, anchor="start"))
        f.append(mtext(rx + 40, yy, r, size=10.6, color=INK, anchor="start", lh=1.2))
        yy += 44

    render(os.path.join(IMG, "partno-vs-gy.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_power_map()
    fig_decode()
    fig_three_waves()
    fig_partno_vs_gy()
    print("OK: 5 figures ->", IMG)
