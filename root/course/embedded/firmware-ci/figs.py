# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# локальні відтінки під єдину палітру svgkit (як у сусідніх темах модуля)
AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"


# ── pipeline: конвеєр CI від поштовху до вердикту ────────────────────────────
# Ідея: коміт запускає ланцюг етапів на сервері — забрати код → крос-зібрати під
# ціль (на сервері чипа нема) → прогнати перевірки, яких читач уже навчився
# (хост-тести, статичний аналіз, поріг розміру) → вердикт зелено/червоно + збережені
# артефакти. Будь-який червоний етап зупиняє конвеєр і світить команді.

def fig_pipeline():
    W, H = 840, 400
    p = []
    p.append(text(W / 2, 34, "конвеєр CI: від поштовху до вердикту", size=15, color=INK, bold=True))

    # поштовх ліворуч
    p.append(rect(28, 150, 118, 92, fill=FILL, stroke=INK, sw=1.8, rx=10))
    p.append(text(28 + 59, 178, "поштовх", size=12, color=INK, bold=True))
    p.append(text(28 + 59, 198, "push або", size=9.4, color=MUTED))
    p.append(text(28 + 59, 213, "pull request", size=9.4, color=MUTED))
    p.append(text(28 + 59, 232, "у гілку", size=9.4, color=MUTED))

    # три етапи-скриньки
    stages = [
        (176, "крос-збірка", NEG, BLUEBG,
         ["arm-none-eabi-gcc", "збирає .elf під ціль", "(сервер без чипа)"]),
        (356, "перевірки", FIELD, GREENBG,
         ["хост-тести · моки", "статичний аналіз", "поріг розміру"]),
        (536, "вердикт", AMBER, AMBERBG,
         ["зелено чи червоно", "звіт у PR", "+ збережені .elf"]),
    ]
    sw_, sh = 156, 100
    sy = 146
    for x, name, col, fill, body in stages:
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, sy, sw_, sh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(x + sw_ / 2, sy + 26, name, size=12.5, color=tagcol, bold=True))
        for j, ln in enumerate(body):
            p.append(text(x + sw_ / 2, sy + 48 + j * 16, ln, size=9.5, color=INK))

    # стрілки між боксами
    p.append(arrow(146, 196, 176, 196, color=INK, sw=2.2))
    p.append(arrow(176 + sw_, 196, 356, 196, color=INK, sw=2.2))
    p.append(arrow(356 + sw_, 196, 536, 196, color=INK, sw=2.2))

    # два виходи вердикту
    p.append(rect(712, 120, 100, 46, fill=GREENBG, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(712 + 50, 141, "✓ зелено", size=11.5, color=FIELD, bold=True))
    p.append(text(712 + 50, 158, "зливати можна", size=9, color=MUTED))
    p.append(rect(712, 226, 100, 46, fill=REDBG, stroke=POS, sw=1.8, rx=8))
    p.append(text(712 + 50, 247, "✗ червоно", size=11.5, color=POS, bold=True))
    p.append(text(712 + 50, 264, "конвеєр стій", size=9, color=MUTED))
    p.append(arrow(536 + sw_, 182, 712, 148, color=FIELD, sw=2))
    p.append(arrow(536 + sw_, 210, 712, 244, color=POS, sw=2))

    p.append(text(W / 2, H - 16,
                  "будь-який червоний етап зупиняє конвеєр і світить команді — за хвилини, не за тижні в полі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "pipeline.svg"), W, H, *p,
           title="Конвеєр CI: від поштовху до вердикту")


# ── gate: захист гілки — зелений CI відмикає злиття ──────────────────────────
# Ідея: правило захисту гілки ставить CI воротарем перед main. Робота живе в
# гілці-віті; PR просить улити її в main; кнопка «злити» лишається замкненою, поки
# конвеєр не зазеленіє. Так у спільну гілку фізично не потрапляє непройдений код.

def fig_gate():
    W, H = 820, 380
    p = []
    p.append(text(W / 2, 34, "захист гілки: зелений CI відмикає кнопку злиття", size=15, color=INK, bold=True))

    # гілка-віть
    p.append(rect(40, 150, 150, 84, fill=BLUEBG, stroke=NEG, sw=1.8, rx=10))
    p.append(text(40 + 75, 178, "гілка-віть", size=12.5, color=NEG, bold=True))
    p.append(text(40 + 75, 200, "ваша робота", size=9.6, color=MUTED))
    p.append(text(40 + 75, 216, "коміти можливості", size=9.6, color=MUTED))

    # PR + воротар
    gx = 300
    p.append(rect(gx, 128, 220, 128, fill=FILL, stroke=INK, sw=2, rx=12))
    p.append(text(gx + 110, 154, "pull request", size=12.5, color=INK, bold=True))
    p.append(text(gx + 110, 174, "«прошу влити в main»", size=9.6, color=MUTED))
    # замок-ворота
    p.append(rect(gx + 30, 188, 160, 52, fill=REDBG, stroke=POS, sw=1.8, rx=8))
    p.append(text(gx + 110, 208, "🔒 злити — замкнено", size=10.5, color=POS, bold=True))
    p.append(text(gx + 110, 226, "поки CI не зелений", size=9.4, color=INK))

    # CI збоку годує воротаря вердиктом
    p.append(rect(gx + 20, 40, 180, 60, fill=GREENBG, stroke=FIELD, sw=1.8, rx=10))
    p.append(text(gx + 110, 64, "конвеєр CI", size=11.5, color=FIELD, bold=True))
    p.append(text(gx + 110, 84, "збірка · тести · аналіз", size=9.4, color=MUTED))
    p.append(arrow(gx + 110, 100, gx + 110, 126, color=FIELD, sw=2.2))
    p.append(text(gx + 210, 116, "вердикт", size=9, color=MUTED, anchor="start"))

    # main
    mx = 630
    p.append(rect(mx, 150, 150, 84, fill=GREENBG, stroke=FIELD, sw=2, rx=10))
    p.append(text(mx + 75, 178, "main", size=13, color=FIELD, bold=True))
    p.append(text(mx + 75, 200, "спільна гілка", size=9.6, color=MUTED))
    p.append(text(mx + 75, 216, "завжди зелена", size=9.6, color=MUTED))

    p.append(arrow(190, 192, gx, 192, color=INK, sw=2))
    p.append(arrow(gx + 220, 192, mx, 192, color=FIELD, sw=2.2))
    p.append(text((gx + 220 + mx) / 2, 180, "лише зелене", size=9, color=FIELD, bold=True))

    p.append(text(W / 2, H - 14,
                  "воротар не радить — він не пускає: непройдений код у спільну гілку фізично не втрапить",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "gate.svg"), W, H, *p,
           title="Захист гілки: зелений CI відмикає злиття")


# ── matrix: один коміт віялом на кілька збірок ───────────────────────────────
# Ідея: одна прошивка часто їде на кілька плат/чипів і в кількох варіантах (debug/
# release). Матриця збірок віялом розкладає той самий коміт на N паралельних робіт —
# кожна ціль складається й тестується окремо, кожна має свій зелено/червоно.
# Так регрес під конкретну плату видно ще до злиття, а не від користувача тієї плати.

def fig_matrix():
    W, H = 820, 400
    p = []
    p.append(text(W / 2, 34, "матриця збірок: один коміт — усі цілі паралельно", size=15, color=INK, bold=True))

    # коміт-джерело
    p.append(rect(46, 168, 128, 74, fill=FILL, stroke=INK, sw=2, rx=10))
    p.append(text(46 + 64, 196, "один коміт", size=12.5, color=INK, bold=True))
    p.append(text(46 + 64, 218, "один вихідний код", size=9.4, color=MUTED))

    # чотири паралельні цілі (2 плати × 2 варіанти)
    targets = [
        ("STM32F4 · release", FIELD, GREENBG, "✓", FIELD),
        ("STM32F4 · debug",   FIELD, GREENBG, "✓", FIELD),
        ("ESP32 · release",   NEG,   BLUEBG,  "✓", FIELD),
        ("ESP32 · debug",     POS,   REDBG,   "✗", POS),
    ]
    tx, tw, th = 300, 300, 56
    tops = [70, 138, 206, 274]
    for (name, col, fill, mark, markcol), ty in zip(targets, tops):
        p.append(rect(tx, ty, tw, th, fill=fill, stroke=col, sw=1.8, rx=9))
        p.append(text(tx + 20, ty + 34, name, size=11.5, color=INK, anchor="start", bold=True))
        # значок вердикту праворуч у самій скриньці
        p.append(circle(tx + tw - 34, ty + th / 2, 15, fill=BG, stroke=markcol, sw=1.8))
        p.append(text(tx + tw - 34, ty + th / 2 + 5, mark, size=14, color=markcol, bold=True))
        # стрілка від коміта
        p.append(arrow(174, 205, tx, ty + th / 2, color=MUTED, sw=1.6))

    # підсумок-воротар праворуч
    p.append(rect(650, 150, 132, 110, fill=REDBG, stroke=POS, sw=2, rx=10))
    p.append(text(650 + 66, 176, "підсумок", size=12, color=POS, bold=True))
    p.append(text(650 + 66, 200, "3 із 4 зелені —", size=10, color=INK))
    p.append(text(650 + 66, 218, "та однієї досить,", size=10, color=INK))
    p.append(text(650 + 66, 236, "щоб увесь коміт", size=10, color=INK))
    p.append(text(650 + 66, 254, "був червоний", size=10, color=POS, bold=True))
    p.append(arrow(600, 234, 650, 210, color=POS, sw=1.8))

    p.append(text(W / 2, H - 14,
                  "регрес під конкретну плату видно ще до злиття — а не від користувача саме тієї плати",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "matrix.svg"), W, H, *p,
           title="Матриця збірок: один коміт — усі цілі паралельно")


# ── sizegate: поріг розміру бінаря — куди лягають секції й де стеля ───────────
# Ідея: секції образу лягають у два бюджети НЕ так, як «здається». Flash тримає
# КОД і ПОЧАТКОВІ значення: .text + .data. RAM тримає ЗМІННІ: .data (копію) +
# .bss. Той самий .data рахується в обидва бюджети. Поріг — горизонтальна стеля
# над кожним стовпчиком; якщо стовпчик її пробив (тут RAM) — крок падає червоним.

def fig_sizegate():
    W, H = 820, 430
    p = []
    p.append(text(W / 2, 34, "поріг розміру: куди лягають секції й де стеля", size=15, color=INK, bold=True))

    # три секції образу (легенда ліворуч)
    lx = 34
    p.append(rect(lx, 108, 176, 150, fill=FILL, stroke=INK, sw=1.6, rx=10))
    p.append(text(lx + 88, 132, "секції образу (.elf)", size=11.5, color=INK, bold=True))
    legend = [
        (".text", "код + константи", NEG),
        (".data", "змінні з початк. значенням", FIELD),
        (".bss",  "змінні, обнулені", AMBERTX),
    ]
    ly = 154
    for name, desc, col in legend:
        p.append(rect(lx + 14, ly - 11, 16, 16, fill=col, stroke=col, sw=1, rx=3))
        p.append(text(lx + 38, ly + 2, name, size=11, color=INK, anchor="start", bold=True))
        p.append(text(lx + 38, ly + 18, desc, size=9, color=MUTED, anchor="start"))
        ly += 34

    # Кожен бюджет — рамка сталої висоти (=стеля), заповнена пропорційно до
    # свого ліміту. Так видно і склад стовпчика, і чи він пробив свою стелю,
    # хоч абсолютні ліміти Flash і RAM різні.
    FRAME_H = 210          # висота рамки-бюджету на картинці (= 100% ліміту)
    base = 300             # низ рамок
    cap_y_flash = base - FRAME_H
    fw = 96

    def seg(x, y0, kb, budget, col, lab):
        h = FRAME_H * kb / budget
        out = rect(x, y0 - h, fw, h, fill=col, stroke=INK, sw=1.2, rx=0)
        if h >= 18:
            out += text(x + fw / 2, y0 - h / 2 + 4, lab, size=9.5, color=BG, bold=True)
        else:
            out += text(x + fw + 8, y0 - h / 2 + 4, lab, size=9, color=INK, anchor="start", bold=True)
        return out, h

    # FLASH: .text=180 + .data=28 = 208 КБ; ліміт 256 КБ → під стелею
    fx = 288
    flash_budget = 256
    s1, h1 = seg(fx, base, 180, flash_budget, NEG, ".text 180")
    s2, h2 = seg(fx, base - h1, 28, flash_budget, FIELD, ".data 28")
    p.append(s1); p.append(s2)
    # рамка-стеля Flash
    p.append(rect(fx - 4, cap_y_flash, fw + 8, FRAME_H, fill="none", stroke=POS, sw=1.4, rx=0))
    p.append(line(fx - 10, cap_y_flash, fx + fw + 10, cap_y_flash, color=POS, sw=2.4))
    p.append(text(fx + fw / 2, cap_y_flash - 8, "стеля Flash — 256 КБ", size=9.6, color=POS, bold=True))
    p.append(text(fx + fw / 2, base + 22, "Flash = .text + .data", size=10.5, color=INK, bold=True))
    p.append(text(fx + fw / 2, base + 40, "208 КБ ✓ під стелею", size=9.8, color=FIELD, bold=True))

    # RAM: .data=28 + .bss=40 = 68 КБ; ліміт 64 КБ → пробій на 4 КБ
    rx = 560
    ram_budget = 64
    r1, rh1 = seg(rx, base, 28, ram_budget, FIELD, ".data 28")
    r2, rh2 = seg(rx, base - rh1, 40, ram_budget, AMBERTX, ".bss 40")
    p.append(r1); p.append(r2)
    cap_y_ram = base - FRAME_H
    p.append(rect(rx - 4, cap_y_ram, fw + 8, FRAME_H, fill="none", stroke=POS, sw=1.4, rx=0))
    p.append(line(rx - 10, cap_y_ram, rx + fw + 10, cap_y_ram, color=POS, sw=2.4))
    p.append(text(rx + fw / 2, cap_y_ram - 8, "стеля RAM — 64 КБ", size=9.6, color=POS, bold=True))
    # пробій: частина стовпчика над стелею — жирна червона рамка
    over_h = (rh1 + rh2) - FRAME_H
    p.append(rect(rx, cap_y_ram - over_h, fw, over_h, fill="none", stroke=POS, sw=3, rx=0))
    p.append(text(rx + fw + 12, cap_y_ram - over_h / 2 + 4, "+4 КБ", size=10, color=POS, anchor="start", bold=True))
    p.append(text(rx + fw / 2, base + 22, "RAM = .data + .bss", size=10.5, color=INK, bold=True))
    p.append(text(rx + fw / 2, base + 40, "68 КБ ✗ пробила стелю", size=9.8, color=POS, bold=True))

    # спільна підказка: .data рахується двічі
    p.append(text(W / 2, base + 66, ".data лежить у Flash (початкові значення) і копіюється в RAM — тому рахується в обидва бюджети",
                  size=9.4, color=MUTED, italic=True))

    p.append(text(W / 2, H - 12,
                  "розмір розповзається тихо, за байтом на коміт; стеля ловить пробій там, де живої плати ще нема",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "sizegate.svg"), W, H, *p,
           title="Поріг розміру: куди лягають секції й де стеля")


# ── ci-timeline: три різні внески в різні роки (для вставки hist-ci) ─────────
# Ідея вставки: CI не має єдиного винахідника — його зібрали з трьох окремих
# внесків. Буч (1991/94) дав ІМʼЯ. XP (Бек·Каннінгем·Джефріс, ~1996) зробило
# ДИСЦИПЛІНОЮ (інтегруй часто + автозбірка). Фаулер+Феммел (есей 2000) прого-
# лосили «дисципліна, не інструмент» і збудували перший ВІДКРИТИЙ сервер
# CruiseControl (2001); Tinderbox у Netscape (1997) був раніший, але внутрішній.
# Колір віхи = що саме вона додала: синій — імʼя, зелений — дисципліна, бурштин — машина.

def fig_timeline():
    W, H = 860, 430
    p = []
    p.append(text(W / 2, 34, "три внески, три роки, три люди — не один винахідник", size=15, color=INK, bold=True))

    # вісь часу
    ax0, ax1 = 70, 790
    axy = 150
    p.append(line(ax0, axy, ax1, axy, color=INK, sw=2.4))
    p.append(arrow(ax1 - 2, axy, ax1 + 18, axy, color=INK, sw=2.4))
    for yr, lab in [(1991, "1991"), (1994, "1994"), (1997, "1997"), (2000, "2000"), (2001, "2001")]:
        fx = ax0 + (ax1 - ax0) * (yr - 1990) / (2002 - 1990)
        p.append(line(fx, axy - 6, fx, axy + 6, color=INK, sw=1.6))
        p.append(text(fx, axy + 22, lab, size=9.5, color=MUTED))

    def x_of(yr):
        return ax0 + (ax1 - ax0) * (yr - 1990) / (2002 - 1990)

    # віхи: (рік, згори_чи_знизу, колір_рамки, заливка, заголовок, [рядки], тег-внесок)
    milestones = [
        (1992.5, "up",   NEG,   BLUEBG,  "Ґреді Буч",
         ["увів термін «CI» (1991),", "закріпив у книзі (1994)"], "дав ІМʼЯ"),
        (1996,   "down", FIELD, GREENBG, "XP · Бек·Каннінгем·Джефріс",
         ["CI — практика; інтегруй", "кілька разів на день", "+ швидка автозбірка"], "зробило ДИСЦИПЛІНОЮ"),
        (1997,   "up",   MUTED, FILL,    "Netscape · Tinderbox",
         ["перший CI-сервер,", "але внутрішній"], "перша (внутр.) машина"),
        (2000.5, "down", AMBER, AMBERBG, "Фаулер + Феммел",
         ["есей: CI — це", "дисципліна, не інструмент"], "проголосили СУТЬ"),
        (2001,   "up",   AMBER, AMBERBG, "CruiseControl (Феммел)",
         ["перший ВІДКРИТИЙ", "CI-сервер; polling"], "перша відкрита машина"),
    ]
    bw = 176
    for xr, side, col, fill, head, body, tag in milestones:
        cx = x_of(xr)
        bh = 30 + len(body) * 15 + 16
        if side == "up":
            by = axy - 30 - bh
            stem_y0, stem_y1 = axy - 6, by + bh
        else:
            by = axy + 40
            stem_y0, stem_y1 = axy + 6, by
        bx = min(max(cx - bw / 2, 6), W - bw - 6)
        # стеблинка від осі до рамки
        p.append(line(cx, stem_y0, cx, stem_y1, color=col, sw=1.6, dash="3,3"))
        p.append(circle(cx, axy, 4.5, fill=col, stroke=col, sw=1))
        p.append(rect(bx, by, bw, bh, fill=fill, stroke=col, sw=1.8, rx=9))
        tagcol = AMBERTX if col == AMBER else col
        p.append(text(bx + bw / 2, by + 19, head, size=10.5,
                      color=(INK if col == MUTED else tagcol), bold=True))
        for j, ln in enumerate(body):
            p.append(text(bx + bw / 2, by + 37 + j * 15, ln, size=9, color=INK))
        p.append(text(bx + bw / 2, by + bh - 6, tag, size=9,
                      color=(MUTED if col == MUTED else tagcol), italic=True))

    p.append(text(W / 2, H - 16,
                  "імʼя · дисципліна · машина прийшли від різних людей — «винайшов N» тут завжди півправда",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "ci-timeline.svg"), W, H, *p,
           title="Три внески, три роки, три люди")


# ── verdict-algebra: вердикт конвеєра = логічне І над кодами виходу (детальна) ─
# Ідея: кожен етап лишає по собі ОДНЕ число — код виходу (0 = гаразд, ≠0 = провал).
# Конвеєр згортає ці числа однією операцією: увесь прогін зелений ⟺ КОЖЕН код 0.
# Це логічне І (кон'юнкція): досить однієї одиниці, щоб добуток-вердикт став
# червоним. Тому «тихий нуль» (крок, що завжди повертає 0) — діра в самому І:
# він не додає нічого до кон'юнкції й ворота лишаються відчинені попри провал.

def fig_verdict():
    W, H = 860, 430
    p = []

    # чотири етапи, кожен лишає код виходу
    stages = [
        ("крос-збірка", "0", FIELD, GREENBG, "зібралось"),
        ("хост-тести", "0", FIELD, GREENBG, "усі pass"),
        ("аналіз (стіна)", "1", POS, REDBG, "знахідка"),
        ("поріг розміру", "0", FIELD, GREENBG, "влізло"),
    ]
    sx, sw_, sh, gap = 40, 176, 74, 22
    sy = 96
    cxs = []
    for i, (name, code, col, fill, note) in enumerate(stages):
        x = sx + i * (sw_ + gap)
        cxs.append(x + sw_ / 2)
        p.append(rect(x, sy, sw_, sh, fill=fill, stroke=col, sw=1.8, rx=9))
        p.append(text(x + sw_ / 2, sy + 24, name, size=11.5, color=INK, bold=True))
        p.append(text(x + sw_ / 2, sy + 44, note, size=9, color=MUTED))
        # код виходу в кружечку під етапом
        p.append(circle(x + sw_ / 2, sy + sh + 30, 17, fill=BG, stroke=col, sw=2))
        p.append(text(x + sw_ / 2, sy + sh + 35, code, size=15, color=col, bold=True))
        p.append(text(x + sw_ / 2, sy + sh + 62, "код виходу", size=9, color=MUTED))

    # рядок кон'юнкції під кодами
    ky = sy + sh + 96
    p.append(text(W / 2, ky, "вердикт = (код₁ = 0) І (код₂ = 0) І (код₃ = 0) І (код₄ = 0)",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, ky + 22, "0 · 0 · 1 · 0  →  досить однієї одиниці, щоб уся кон'юнкція впала",
                  size=10.5, color=MUTED, italic=True))

    # два виходи
    p.append(rect(150, ky + 42, 220, 46, fill=GREENBG, stroke=FIELD, sw=1.8, rx=9))
    p.append(text(150 + 110, ky + 63, "✓ усі нулі → зелено", size=11, color=FIELD, bold=True))
    p.append(text(150 + 110, ky + 80, "ворота відмикаються", size=9, color=MUTED))
    p.append(rect(490, ky + 42, 220, 46, fill=REDBG, stroke=POS, sw=2.4, rx=9))
    p.append(text(490 + 110, ky + 63, "✗ є одиниця → червоно", size=11, color=POS, bold=True))
    p.append(text(490 + 110, ky + 80, "ворота лишаються замкнені", size=9, color=INK))

    p.append(text(W / 2, H - 12,
                  "«тихий нуль» — крок, що завжди повертає 0 — це діра в самому І: провал не потрапляє в кон'юнкцію",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "verdict-algebra.svg"), W, H, *p,
           title="Вердикт конвеєра як логічне І")


# ── feedback-latency: критичний шлях проти стіни годинника (детальна) ─────────
# Ідея: справжній продукт CI — не «зелено/червоно», а ЧАС до цього вердикту. Дві
# розкладки того самого набору етапів на осі часу. Згори — послідовно: етапи один
# за одним, стіна годинника = СУМА. Знизу — віялом: незалежні етапи паралельно +
# кеш тулчейну зрізає найдовший хвіст, і стіна годинника = НАЙДОВША гілка (крит.
# шлях), а не сума. Різниця між сумою і максимумом — те, заради чого паралелять.

def fig_latency():
    W, H = 880, 440
    p = []

    # спільна вісь часу (хвилини)
    t0, t1 = 150, 820
    scale = (t1 - t0) / 14.0   # 14 хв на всю шкалу
    def xt(m): return t0 + m * scale

    def ruler(y):
        p.append(line(t0, y, t1, y, color=MUTED, sw=1.2))
        for m in range(0, 15, 2):
            p.append(line(xt(m), y - 4, xt(m), y + 4, color=MUTED, sw=1))
            p.append(text(xt(m), y + 18, "%d" % m, size=9, color=MUTED))

    def bar(y, x_start_min, dur_min, label, col, fill, force_right=False):
        x = xt(x_start_min); w = dur_min * scale
        p.append(rect(x, y, w, 24, fill=fill, stroke=col, sw=1.6, rx=5))
        lab = "%s · %g хв" % (label, dur_min)
        if not force_right and text_width(lab, 9, True) < w - 8:
            p.append(text(x + w / 2, y + 16, lab, size=9, color=INK, bold=True))
        else:
            p.append(text(x + w + 7, y + 16, lab, size=9, color=INK, anchor="start", bold=True))

    # ── згори: послідовно (сума) ──
    p.append(text(t0 - 14, 72, "послідовно", size=11.5, color=POS, anchor="end", bold=True))
    p.append(text(t0 - 14, 88, "стіна = сума", size=9, color=MUTED, anchor="end"))
    sy = 60
    bar(sy, 0, 5, "тулчейн (тягне)", NEG, BLUEBG)
    bar(sy, 5, 3, "крос-збірка", NEG, BLUEBG)
    bar(sy, 8, 3, "хост-тести", FIELD, GREENBG)
    bar(sy, 11, 2, "аналіз", AMBER, AMBERBG)
    # стіна годинника
    p.append(line(xt(13), 50, xt(13), 92, color=POS, sw=2.4, dash="4,3"))
    p.append(text(xt(13) + 6, 56, "13 хв", size=10, color=POS, anchor="start", bold=True))
    ruler(106)

    # ── знизу: віялом + кеш (максимум) ── кожна гілка на своєму рядку
    p.append(text(t0 - 14, 168, "віялом + кеш", size=11.5, color=FIELD, anchor="end", bold=True))
    p.append(text(t0 - 14, 184, "стіна = найдовша", size=9, color=MUTED, anchor="end"))
    b1, b2, b3 = 150, 186, 222
    # кеш зрізає тулчейн-хвіст майже до нуля; збірка стартує одразу (та сама гілка).
    # Вузький сегмент кешу підписуємо каптоном ЗВЕРХУ, щоб не битися з підписом збірки.
    p.append(rect(xt(0), b1, 0.4 * scale, 24, fill=FILL, stroke=MUTED, sw=1.6, rx=5))
    p.append(text(xt(0.4) + 6, b1 - 6, "◤ тулчейн із кешу (0.4 хв замість 5)", size=9, color=MUTED, anchor="start"))
    bar(b1, 0.4, 3, "крос-збірка", NEG, BLUEBG)
    bar(b2, 0, 3, "хост-тести", FIELD, GREENBG)
    bar(b3, 0, 2, "аналіз", AMBER, AMBERBG)
    p.append(text(t0 - 14, b2 + 15, "паралельні гілки", size=9, color=MUTED, anchor="end"))
    p.append(line(xt(3.4), 142, xt(3.4), 250, color=FIELD, sw=2.4, dash="4,3"))
    p.append(text(xt(3.4) + 6, 148, "3.4 хв", size=10, color=FIELD, anchor="start", bold=True))
    ruler(258)

    # висновок
    p.append(text(W / 2, 296, "той самий набір перевірок — стіна впала з 13 до 3.4 хв", size=12, color=INK, bold=True))
    p.append(text(W / 2, 318, "кеш зрізав 5-хвилинний хвіст тулчейну; паралель звела суму до максимуму гілок",
                  size=10.5, color=MUTED))

    # окрема рамка «чому час — це продукт»
    fx, fy, fw2, fh2 = 150, 344, 580, 60
    p.append(rect(fx, fy, fw2, fh2, fill=AMBERBG, stroke=AMBER, sw=1.6, rx=9))
    p.append(text(fx + fw2 / 2, fy + 22, "чому це головне число", size=10.5, color=AMBERTX, bold=True))
    p.append(text(fx + fw2 / 2, fy + 42, "вердикт за 3 хв читають одразу; вердикт за 40 хв обходять «поки збереться — попрацюю»",
                  size=9.6, color=INK))

    render(os.path.join(OUT, "feedback-latency.svg"), W, H, *p,
           title="Стіна годинника: сума проти критичного шляху")


# ── trust-inversion: хмарний раннер проти власного стенда — переворот довіри ──
# Ідея (детальна): дотягнувшись до заліза, CI змінює не лише «де», а МОДЕЛЬ БЕЗПЕКИ
# на протилежну. Хмарний раннер: свіжий, одноразовий, чужа мережа, чипа нема —
# впав і згас, ізольований. Власний стенд: постійна машина у ВАШІЙ лабораторії, з
# реальним чипом і доступом до LAN — і на ньому от-от виконається код із чужого,
# ще не влитого PR. Дві осі перевертаються: одноразовість→постійність, ізоляція→
# ваша мережа. Звідси нові закони стенда: паралельність=1, карантин, довіра до PR.

def fig_trust():
    W, H = 860, 420
    p = []

    colX = [70, 470]
    boxW = 320
    heads = [
        ("хмарний раннер", NEG, BLUEBG, "одноразовий · ізольований · без чипа"),
        ("власний стенд (HIL)", POS, REDBG, "постійний · ваша мережа · реальний чип"),
    ]
    rows = [
        ("життя машини", "свіжа щоразу, згасає по прогону", "живе постійно між прогонами"),
        ("мережа довкола", "чужа хмара, нічого вашого поряд", "ваша LAN: сервери, диски, люди"),
        ("що виконує", "код із PR — але в пісочниці", "код із того самого PR — на вашому залізі"),
        ("ціна збою", "згасив контейнер, забув", "цеглинка з плати, доступ у вашу мережу"),
    ]
    for i, (head, col, fill, sub) in enumerate(heads):
        x = colX[i]
        p.append(rect(x, 56, boxW, 40, fill=fill, stroke=col, sw=2, rx=9))
        p.append(text(x + boxW / 2, 74, head, size=12.5, color=col, bold=True))
        p.append(text(x + boxW / 2, 90, sub, size=9, color=MUTED))

    ry = 108
    rh = 58
    for j, (label, a, b) in enumerate(rows):
        y = ry + j * rh
        p.append(text(W / 2, y + rh / 2 + 4, label, size=9.2, color=MUTED, bold=True))
        p.append(fitbox(colX[0], y, boxW, rh - 10, a, size=10, pad=8, fill=BLUEBG, stroke=NEG, sw=1.3, color=INK))
        p.append(fitbox(colX[1], y, boxW, rh - 10, b, size=10, pad=8, fill=REDBG, stroke=POS, sw=1.3, color=INK))
        # стрілка перевороту
        p.append(arrow(colX[0] + boxW + 6, y + (rh - 10) / 2, colX[1] - 6, y + (rh - 10) / 2, color=MUTED, sw=1.4))

    p.append(text(W / 2, H - 14,
                  "звідси закони стенда: паралельність = 1, карантин прошивки, обережність до коду з чужих PR",
                  size=10.6, color=MUTED, italic=True))
    render(os.path.join(OUT, "trust-inversion.svg"), W, H, *p,
           title="Переворот моделі довіри: хмара проти власного стенда")


# ── hil-job: етапи власного HIL-раннера в конвеєрі (вставка proj) ────────────
# Ідея: хмарна частина конвеєра дала зелений .elf. Далі робота на ВЛАСНОМУ
# раннері біля живої плати проганяє чотири етапи, кожен з яких може завернути
# коміт: залити → рукостискання по UART (чи чіп ожив) → on-target тести (читаємо
# вердикт із плати) → відновити в відомий стан. Ліворуч — черга-з-одного: група
# concurrency з паралельністю 1 серіалізує доступ до ЄДИНОГО фізичного стенда,
# бо два прогони на один чіп фізично несумісні. Праворуч — карантин: якщо чіп не
# відповів після заливки, стенд НЕ пускають далі, поки людина не гляне.

def fig_hiljob():
    W, H = 900, 470
    p = []

    # черга-з-одного ліворуч
    qx = 34
    p.append(rect(qx, 96, 150, 150, fill=BLUEBG, stroke=NEG, sw=1.8, rx=10))
    p.append(text(qx + 75, 120, "concurrency", size=11.5, color=NEG, bold=True))
    p.append(text(qx + 75, 137, "паралельність = 1", size=9.4, color=INK, bold=True))
    for k, ty in enumerate((156, 182, 208)):
        col = FIELD if k == 0 else MUTED
        p.append(rect(qx + 22, ty, 106, 20, fill=(GREENBG if k == 0 else FILL), stroke=col, sw=1.4, rx=5))
        lab = "PR #17 біжить" if k == 0 else ("PR #18 жде" if k == 1 else "PR #19 жде")
        p.append(text(qx + 75, ty + 14, lab, size=9, color=INK))
    p.append(text(qx + 75, 240, "черга, не скасування", size=9, color=MUTED, italic=True))
    p.append(arrow(qx + 150, 171, 214, 171, color=NEG, sw=2))

    # чотири етапи стендом — вертикальна колона по центру
    ex, ew, eh = 214, 300, 62
    stages = [
        ("1 · залити .elf у живий чіп", NEG, BLUEBG, "прошивальник пише Flash по SWD"),
        ("2 · рукостискання по UART", AMBER, AMBERBG, "чіп ожив? шле банер за 2 с — чи ні"),
        ("3 · on-target тести", FIELD, GREENBG, "плата сама рахує; читаємо вердикт"),
        ("4 · відновити в відомий стан", NEG, BLUEBG, "фізичний скид NRST між прогонами"),
    ]
    tops = [96, 186, 276, 366]
    for (name, col, fill, sub), ty in zip(stages, tops):
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(ex, ty, ew, eh, fill=fill, stroke=col, sw=1.8, rx=9))
        p.append(text(ex + ew / 2, ty + 25, name, size=11.5, color=tagcol, bold=True))
        p.append(text(ex + ew / 2, ty + 45, sub, size=9, color=INK))
    for a, b in zip(tops, tops[1:]):
        p.append(arrow(ex + ew / 2, a + eh, ex + ew / 2, b, color=INK, sw=2))

    # праворуч: два виходи рукостискання — карантин або далі
    rx = ex + ew + 44
    # зелений: банер прийшов
    p.append(rect(rx, 190, 168, 54, fill=GREENBG, stroke=FIELD, sw=1.8, rx=9))
    p.append(text(rx + 84, 212, "✓ банер прийшов", size=10.5, color=FIELD, bold=True))
    p.append(text(rx + 84, 230, "чіп ожив → крок 3", size=9, color=INK))
    p.append(arrow(ex + ew, 210, rx, 214, color=FIELD, sw=2))
    # червоний: мовчання → карантин
    p.append(rect(rx, 268, 168, 78, fill=REDBG, stroke=POS, sw=2, rx=9))
    p.append(text(rx + 84, 290, "✗ тиша по UART", size=10.5, color=POS, bold=True))
    p.append(text(rx + 84, 309, "чіп-цеглинка →", size=9, color=INK))
    p.append(text(rx + 84, 325, "КАРАНТИН стенда:", size=9, color=POS, bold=True))
    p.append(text(rx + 84, 340, "не пускати далі", size=9, color=INK))
    p.append(arrow(ex + ew, 236, rx, 300, color=POS, sw=2))

    p.append(text(W / 2, H - 16,
                  "кожен етап може завернути коміт; мовчання чипа не «падіння тесту», а зупинка стенда до огляду",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "hil-job.svg"), W, H, *p,
           title="HIL-раннер у конвеєрі: залити · рукостискання · on-target · відновити")


# ── fork-gate: який тригер безпечний на фізичному стенді (вставка proj) ───────
# Ідея: власний стенд — постійна машина у вашій мережі з реальним залізом, тож
# запускати на ньому код із ЧУЖОГО форку = дати чужому виконати щось на вашому
# залізі й у вашій LAN. Три тригери в ряд від безпечного до згубного:
# pull_request із форку — читає код форку, але БЕЗ секретів і лише read-token
# (та все одно КОД форку виконається на стенді → не пускати на HIL); push у
# довірену гілку / мітку супроводжувача — код уже переглянутий → безпечно для
# стенда; pull_request_target + checkout PR — «pwn request»: чужий код із ПОВНОЮ
# довірою (секрети, write-token) → катастрофа. Стенд слухає ЛИШЕ середній.

def fig_forkgate():
    W, H = 900, 430
    p = []

    colX = [28, 320, 612]
    boxW = 260
    cases = [
        ("pull_request із форку", AMBER, AMBERBG, "⚠ обережно",
         ["код форку — читається,", "але секретів НЕ дає,", "токен лише read.", "І все ж КОД форку", "виконався б на стенді."],
         "не пускати на HIL"),
        ("push у довірену гілку / мітку", FIELD, GREENBG, "✓ безпечно",
         ["код уже влитий або", "позначений супровідником —", "тобто ПЕРЕГЛЯНУТий.", "Лише це стенд і", "має слухати."],
         "єдиний тригер стенда"),
        ("pull_request_target + checkout PR", POS, REDBG, "☠ згубно",
         ["чужий код із ПОВНОЮ", "довірою: секрети +", "write-токен. GitHub", "Security Lab кличе це", "«pwn request»."],
         "ніколи на стенді"),
    ]
    for x, (head, col, fill, badge, body, foot) in zip(colX, cases):
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, 60, boxW, 300, fill=fill, stroke=col, sw=2, rx=11))
        p.append(text(x + boxW / 2, 86, badge, size=12.5, color=tagcol, bold=True))
        p.append(text(x + boxW / 2, 108, head, size=10.3, color=INK, bold=True))
        p.append(line(x + 16, 120, x + boxW - 16, 120, color=col, sw=1))
        for j, ln in enumerate(body):
            p.append(text(x + boxW / 2, 146 + j * 22, ln, size=9.4, color=INK))
        p.append(rect(x + 20, 300, boxW - 40, 42, fill=BG, stroke=col, sw=1.5, rx=8))
        p.append(text(x + boxW / 2, 326, foot, size=10, color=tagcol, bold=True))

    p.append(text(W / 2, H - 14,
                  "на постійній машині з живим залізом «просто зібрати чужий PR» коштує вашого стенда й вашої мережі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "fork-gate.svg"), W, H, *p,
           title="Стенд слухає лише довірене: три тригери від безпечного до згубного")


# ── critical-path-dag: DAG етапів, час завершення й критичний шлях (math) ─────
# Ідея (math-вставка): стіна годинника = найдовший ланцюг ЗАЛЕЖНИХ етапів у DAG,
# а не сума й не окремий найдовший вузол. Малюємо граф: старт → (тулчейн→збірка)
# як довга гілка, паралельно короткі гілки хост-тестів і аналізу, усе сходиться в
# вердикт. У кожному вузлі — тривалість. Червоним підсвічено критичний шлях
# (найбільша сума ваг); короткі гілки завершуються В ЙОГО ТІНІ й на стіну не
# впливають. Підпис на кожному ребрі — накопичений час завершення C(v).

def fig_cpdag():
    W, H = 900, 470
    p = []

    # координати вузлів (x, y) і їхні дані: (підпис, тривалість, час завершення)
    # довга гілка (критична): старт → тулчейн(5) → збірка(3) → вердикт
    # коротка гілка A: старт → хост-тести(3) → вердикт
    # коротка гілка B: старт → аналіз(2) → вердикт
    NR = 30  # радіус вузла-кола замінимо на прямокутники textbox

    # рівні по X
    x0, x1, x2, x3 = 70, 300, 540, 800
    yTop, yMid, yBot = 120, 250, 360

    def node(cx, cy, name, dur, crit=False, cfin=None):
        col = POS if crit else INK
        fill = REDBG if crit else FILL
        b, w, h = textbox(cx, cy, "%s\n%g хв" % (name, dur), size=11, pad=9,
                          fill=fill, stroke=col, sw=2.0 if crit else 1.5, bold=True)
        p.append(b)
        if cfin is not None:
            p.append(text(cx, cy + h/2 + 15, "C = %g" % cfin, size=9.2,
                          color=(POS if crit else MUTED), bold=crit))
        return w, h

    def edge(x1e, y1e, x2e, y2e, crit=False):
        col = POS if crit else MUTED
        p.append(arrow(x1e, y1e, x2e, y2e, color=col, sw=2.4 if crit else 1.5))

    # старт
    node(x0, yMid, "старт", 0, cfin=0)
    # критична гілка (верх): тулчейн → збірка
    edge(x0+42, yMid-6, x1-58, yTop+6, crit=True)
    node(x1, yTop, "тулчейн", 5, crit=True, cfin=5)
    edge(x1+58, yTop, x2-64, yTop, crit=True)
    node(x2, yTop, "крос-збірка", 3, crit=True, cfin=8)
    # коротка гілка A (середина): хост-тести
    edge(x0+42, yMid, x1-64, yMid, crit=False)
    node(x1, yMid, "хост-тести", 3, cfin=3)
    # коротка гілка B (низ): аналіз
    edge(x0+42, yMid+6, x1-58, yBot-6, crit=False)
    node(x1, yBot, "аналіз", 2, cfin=2)
    # сходження у вердикт (він на рівні x3, посередині по висоті)
    node(x3, yMid, "вердикт", 0, crit=True, cfin=8)
    edge(x2+72, yTop, x3-52, yMid-8, crit=True)      # від збірки (крит.)
    edge(x1+64, yMid, x3-52, yMid, crit=False)       # від хост-тестів
    edge(x1+58, yBot-6, x3-46, yMid+8, crit=False)   # від аналізу

    # легенда критичного шляху
    ly = H - 58
    p.append(rect(60, ly, 780, 42, fill=REDBG, stroke=POS, sw=1.6, rx=9))
    p.append(text(60+390, ly+18, "критичний шлях: старт → тулчейн → збірка → вердикт = 5 + 3 = 8 хв",
                  size=11, color=POS, bold=True))
    p.append(text(60+390, ly+35,
                  "короткі гілки (3 хв, 2 хв) завершуються в його тіні — стіна дорівнює 8 хв, не сумі 10",
                  size=9.6, color=INK))

    render(os.path.join(OUT, "critical-path-dag.svg"), W, H, *p,
           title="Критичний шлях над DAG етапів: стіна = найдовший ланцюг залежностей")


# ── amdahl-speedup: крива прискорення й стеля 1/s (math) ──────────────────────
# Ідея (math-вставка): S(n) = 1/(s + (1−s)/n). Три криві для s = 0.1, 0.25, 0.5.
# Кожна круто росте на перших гілках, тоді згинається й лягає на горизонтальну
# стелю 1/s (пунктир). Показуємо: паралель веде вгору по кривій, але не пробиває
# стелю; після «коліна» кожна нова машина додає копійки. Осі: X — число гілок n,
# Y — прискорення. Стелі підписані праворуч, поза кривими.

def fig_amdahl():
    W, H = 880, 500
    p = []

    # область графіка
    gx0, gy0 = 90, 70          # лівий-верхній кут поля
    gw, gh = 640, 320          # ширина/висота поля
    gx1, gy1 = gx0 + gw, gy0 + gh

    n_max = 16
    s_max = 11.0               # верх осі Y (щоб стеля 10 влізла з полем)

    def X(n):  return gx0 + (n - 1) / (n_max - 1) * gw
    def Y(v):  return gy1 - (v / s_max) * gh

    # осі
    p.append(line(gx0, gy0, gx0, gy1, color=INK, sw=1.6))
    p.append(line(gx0, gy1, gx1, gy1, color=INK, sw=1.6))
    # підписи осей
    p.append(text(gx0 + gw/2, gy1 + 44, "число паралельних гілок n", size=11, color=INK, bold=True))
    p.append(text(gx0 - 58, gy0 + gh/2, "прискорення S(n)", size=11, color=INK, bold=True))
    # мітки X
    for n in [1, 2, 4, 8, 12, 16]:
        p.append(line(X(n), gy1, X(n), gy1 + 5, color=MUTED, sw=1))
        p.append(text(X(n), gy1 + 20, "%d" % n, size=9, color=MUTED))
    # мітки Y
    for v in [1, 2, 4, 6, 8, 10]:
        p.append(line(gx0 - 5, Y(v), gx0, Y(v), color=MUTED, sw=1))
        p.append(text(gx0 - 16, Y(v) + 4, "%d×" % v, size=9, color=MUTED, anchor="end"))

    def curve(s, col, ceil_label_y_off):
        ceil = 1.0 / s
        # стеля-пунктир
        p.append(line(gx0, Y(ceil), gx1, Y(ceil), color=col, sw=1.4, dash="5,4"))
        # сама крива S(n) точками
        pts = []
        n = 1.0
        while n <= n_max + 0.001:
            v = 1.0 / (s + (1 - s) / n)
            pts.append("%.1f,%.1f" % (X(n), Y(v)))
            n += 0.25
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), col))
        # підпис стелі праворуч, поза полем
        p.append(text(gx1 + 10, Y(ceil) + ceil_label_y_off, "1/s = %g×" % ceil,
                      size=10.5, color=col, anchor="start", bold=True))
        # підпис частки s біля коліна кривої (n≈3), трохи нижче кривої
        vk = 1.0 / (s + (1 - s) / 3.0)
        p.append(text(X(3) + 4, Y(vk) + 20, "s = %g" % s, size=10, color=col, anchor="start", bold=True))

    # три криві: менша частка послідовного → вища стеля
    curve(0.10, FIELD, 4)    # стеля 10× — зелена
    curve(0.25, NEG,  4)     # стеля 4×  — синя
    curve(0.50, POS,  -6)    # стеля 2×  — червона

    # рамка-висновок
    fy = gy1 + 54
    p.append(rect(gx0, fy, gw, 44, fill=AMBERBG, stroke=AMBER, sw=1.6, rx=9))
    p.append(text(gx0 + gw/2, fy + 18, "стеля прискорення = 1/s, де s — частка неподільної роботи",
                  size=11, color=AMBERTX, bold=True))
    p.append(text(gx0 + gw/2, fy + 35,
                  "після «коліна» нова машина додає копійки; важіль — не більше n, а менше s",
                  size=9.6, color=INK))

    render(os.path.join(OUT, "amdahl-speedup.svg"), W, H, *p,
           title="Закон Амдала: крива прискорення впирається у стелю 1/s")


if __name__ == "__main__":
    fig_pipeline()
    fig_gate()
    fig_matrix()
    fig_sizegate()
    fig_timeline()
    fig_verdict()
    fig_latency()
    fig_trust()
    fig_hiljob()
    fig_forkgate()
    fig_cpdag()
    fig_amdahl()
    print("OK: figures written to", OUT)
