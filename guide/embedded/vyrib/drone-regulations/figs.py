# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

STEP  = "#eef3fb"   # світлий блок
STEPB = "#4a6fa5"   # обрис блока
WARM  = "#fff4e0"   # тепла плашка (маси/енергія)
WARMB = "#c9820f"
SKY   = "#e8f1fb"   # небо / повітряний простір
SKYB  = "#3f7ac0"
GRASS = "#eaf6ee"   # безпечна зона
GRASSB= "#3f9d5a"


# ── root: дві фізичні причини, чому небо взагалі регулюють ───────────────────
# Ідея: реґуляція БпЛА — не забаганка чиновника, а наслідок ДВОХ твердих фактів.
# (1) навіть легкий апарат, падаючи, несе небезпечну кінетичну енергію на людину
#     внизу; (2) той самий об'єм повітря ділять із пілотованими літаками, для
#     яких зіткнення фатальне. Обидва → правило: без дозволу держави в небо не
#     можна (стаття 8 Чиказької конвенції, 1944).
def fig_root():
    W, H = 780, 340
    p = []
    p.append(text(W/2, 30, "Чому небо регулюють: дві тверді причини, а не забаганка",
                  size=15, bold=True))

    # ---- ліва причина: падіння → кінетична енергія на людину ----
    lx = 195
    p.append(text(lx, 66, "1. падає — б'є", size=12.5, bold=True, color=WARMB))
    # дрон угорі
    p.append(rect(lx - 22, 84, 44, 16, fill="#444a52", stroke="#22262b", sw=1.3, rx=3))
    for gx in (lx - 14, lx + 14):
        p.append(circle(gx, 92, 8, fill="none", stroke="#22262b", sw=1.6))
    # траєкторія падіння
    p.append(arrow(lx, 104, lx, 196, color=WARMB, sw=2.2))
    p.append(text(lx + 60, 150, "0.9 кг × висота", size=10, color=WARMB, italic=True))
    # людина внизу (спрощено)
    p.append(circle(lx, 214, 9, fill=WARM, stroke=WARMB, sw=1.6))
    p.append(line(lx, 223, lx, 250, color=WARMB, sw=2.0))
    p.append(line(lx, 232, lx - 12, 244, color=WARMB, sw=2.0))
    p.append(line(lx, 232, lx + 12, 244, color=WARMB, sw=2.0))
    p.append(line(lx - 60, 262, lx + 60, 262, color="#c9cfd6", sw=2.0))
    p.append(text(lx, 286, "енергія удару росте з масою й висотою", size=9.5, color=MUTED))
    p.append(text(lx, 302, "тому межі саме за масою (250 г · 900 г · 4 · 25 кг)", size=9.5, color=MUTED))

    # роздільник
    p.append(line(390, 60, 390, 300, color="#dde1e6", sw=1.2, dash="5 5"))

    # ---- права причина: спільне небо з пілотованими ----
    rx = 580
    p.append(text(rx, 66, "2. небо — спільне", size=12.5, bold=True, color=SKYB))
    p.append(rect(rx - 130, 84, 260, 96, fill=SKY, stroke=SKYB, sw=1.4, rx=8))
    # літак
    p.append(text(rx - 78, 128, "✈", size=30, color="#22262b"))
    p.append(text(rx - 78, 150, "пілотований", size=9, color=INK))
    # дрон
    p.append(rect(rx + 46, 116, 34, 12, fill="#444a52", stroke="#22262b", sw=1.2, rx=3))
    for gx in (rx + 52, rx + 74):
        p.append(circle(gx, 122, 6, fill="none", stroke="#22262b", sw=1.4))
    p.append(text(rx + 63, 150, "БпЛА", size=9, color=INK))
    # блискавка-конфлікт між ними
    p.append(text(rx - 8, 138, "⚡", size=20, color=POS))
    p.append(text(rx, 204, "для літака навіть легкий апарат — смертельна загроза", size=9.5, color=MUTED))
    p.append(text(rx, 220, "тому висота обмежена (≈120 м) і є заборонені зони", size=9.5, color=MUTED))

    # ---- висновок унизу: обидва → стаття 8 ----
    by = 306
    b, w, h = textbox(rx, 262, "⇒  без дозволу держави\nу небо — не можна", size=10.5,
                      bold=True, fill=STEP, stroke=STEPB, sw=1.6, pad=8)
    p.append(b)

    render(os.path.join(OUT, "root.svg"), W, H, *p)


# ── tiers: universal risk ladder на прикладі EASA Open ───────────────────────
# Ідея: скрізь та сама логіка — що важче й що ближче до людей, то суворіші
# вимоги. Показуємо сходинки за масою (C-класи) і колонки за близькістю до
# людей (A1/A2/A3). Читач бачить: категорія = (маса) × (де летиш).
def fig_tiers():
    W, H = 800, 380
    p = []
    p.append(text(W/2, 28, "Категорія = наскільки важкий × наскільки близько до людей",
                  size=15, bold=True))

    # осі
    ax0, ay0 = 150, 300      # початок осей (лівий-низ)
    p.append(arrow(ax0, ay0, ax0, 70, color=INK, sw=1.8))     # вісь маси вгору
    p.append(arrow(ax0, ay0, 720, ay0, color=INK, sw=1.8))    # вісь близькості праворуч
    p.append(text(96, 180, "маса", size=11, bold=True, color=INK))
    p.append(text(96, 196, "росте", size=9, color=MUTED))
    p.append(text(690, 292, "ближче →", size=10, bold=True, color=INK, anchor="end"))

    # горизонтальні мітки мас (C-класи)
    masses = [(270, "C0  < 250 г"), (222, "C1  < 900 г"), (170, "C2  < 4 кг"), (110, "C3/C4  < 25 кг")]
    for my, lbl in masses:
        p.append(line(ax0 - 5, my, ax0 + 5, my, color=INK, sw=1.4))
        p.append(text(ax0 - 12, my + 4, lbl, size=9, color=INK, anchor="end"))

    # колонки близькості (A1/A2/A3)
    cols = [(250, "A1", "над людьми\n(не над натовпом)", GRASS, GRASSB),
            (420, "A2", "близько:\n≥ 30 м до людей", WARM, WARMB),
            (600, "A3", "далеко:\n≥ 150 м від забудови", SKY, SKYB)]
    for cx, name, sub, fill, stroke in cols:
        p.append(text(cx, ay0 + 20, name, size=13, bold=True, color=stroke))
        for j, seg in enumerate(sub.split("\n")):
            p.append(text(cx, ay0 + 36 + j*13, seg, size=8.5, color=MUTED))

    # клітинки-«де що можна» (спрощена мапа): позначки класів у колонках
    def cell(cx, cy, txt, fill, stroke):
        b, w, h = textbox(cx, cy, txt, size=9.5, bold=True, fill=fill, stroke=stroke,
                          sw=1.4, pad=6, min_w=78)
        p.append(b)
    # A1: дрібні (C0, C1)
    cell(250, 270, "C0", GRASS, GRASSB)
    cell(250, 222, "C1", GRASS, GRASSB)
    # A2: середні (C2) + потрібен іспит A2
    cell(420, 170, "C2\n+іспит A2", WARM, WARMB)
    # A3: важкі (C2, C3, C4)
    cell(600, 170, "C2", SKY, SKYB)
    cell(600, 110, "C3/C4", SKY, SKYB)

    # підказка знизу: за межами сходів — інші категорії
    p.append(text(W/2, 356,
                  "важче/ризикованіше за Open → категорія Specific (дозвіл на ризик) → Certified (як великий літак)",
                  size=9.5, color=MUTED))

    render(os.path.join(OUT, "tiers.svg"), W, H, *p)


# ── duties: хто що винен — виробник vs оператор ──────────────────────────────
# Ідея: реґуляція ділиться навпіл. Одні обов'язки лягають на ТЕБЕ як виробника
# плати/апарата (клас-мітка, CE, вбудований Remote ID, геозона) — це прошивка й
# продукт. Інші — на оператора, що злетить (реєстрація, іспит, де й як летіти).
# Ти закриваєш свою половину в залізі й коді ще до продажу.
def fig_duties():
    W, H = 800, 330
    p = []
    p.append(text(W/2, 30, "Реґуляція ділиться навпіл: виробник закриває своє в продукті й коді",
                  size=14.5, bold=True))

    # ---- ліва колонка: виробник ----
    lx0, lw = 60, 330
    p.append(rect(lx0, 66, lw, 226, fill=STEP, stroke=STEPB, sw=1.8, rx=10))
    p.append(text(lx0 + lw/2, 92, "ти — виробник апарата", size=13, bold=True, color=STEPB))
    p.append(text(lx0 + lw/2, 108, "(закладаєш у залізо й прошивку)", size=9, color=MUTED))
    maker = [
        "клас-мітка C0…C4 і CE на корпусі",
        "вбудований Remote ID: апарат сам",
        "  мовить хто він і де він",
        "геозона: не пускати в заборонену зону",
        "паспорт/інструкція: маса, межі, клас",
    ]
    my = 134
    for i, ln in enumerate(maker):
        bullet = "•  " if not ln.startswith("  ") else "   "
        anch_x = lx0 + 18
        p.append(text(anch_x, my, bullet + ln.strip(), size=10, color=INK, anchor="start"))
        my += 22
    p.append(text(lx0 + lw/2, 278, "усе це — ДО того, як апарат продано", size=9.5,
                  color=STEPB, italic=True))

    # стрілка-міст «продаєш →»
    p.append(arrow(lx0 + lw + 8, 180, lx0 + lw + 58, 180, color=WARMB, sw=2.4))
    p.append(text(lx0 + lw + 33, 166, "продаєш", size=9, color=WARMB, italic=True))

    # ---- права колонка: оператор ----
    rx0 = 468
    rw = 272
    p.append(rect(rx0, 66, rw, 226, fill=WARM, stroke=WARMB, sw=1.8, rx=10))
    p.append(text(rx0 + rw/2, 92, "оператор / пілот", size=13, bold=True, color=WARMB))
    p.append(text(rx0 + rw/2, 108, "(хто злетить у небо)", size=9, color=MUTED))
    op = [
        "реєстрація оператора → номер",
        "  наносить на апарат",
        "іспит пілота (за категорією)",
        "де й коли летіти: висота,",
        "  зони, візуальний контакт",
    ]
    my = 134
    for ln in op:
        bullet = "•  " if not ln.startswith("  ") else "   "
        p.append(text(rx0 + 16, my, bullet + ln.strip(), size=10, color=INK, anchor="start"))
        my += 22
    p.append(text(rx0 + rw/2, 278, "твій Remote ID мовить саме цей номер", size=9.5,
                  color=WARMB, italic=True))

    render(os.path.join(OUT, "duties.svg"), W, H, *p)


# ── rid_frame: як число з GPS стає цілим полем у 25-байтовому повідомленні ────
# Ідея вставки: дробові градуси з навігації НЕ йдуть у ефір як float — їх
# множать на 10⁷ і кладуть цілим int32 у фіксоване поле повідомлення сталого
# розміру (25 байтів). Показуємо цей перехід «людське число → ціле на дроті»
# і сталу розкладку байтів, з якої приймач читає завжди однаково.
def fig_rid_frame():
    W, H = 800, 360
    p = []
    p.append(text(W/2, 28, "Координата в ефір іде цілим числом у полі сталого розміру",
                  size=15, bold=True))

    # ---- ліворуч: людське число з GPS ----
    lx = 150
    p.append(text(lx, 74, "з GPS-приймача", size=11, bold=True, color=MUTED))
    b, w, h = textbox(lx, 104, "широта\n50.4501°", size=12, bold=True,
                      fill=WARM, stroke=WARMB, sw=1.6, pad=10, min_w=130)
    p.append(b)
    p.append(text(lx, 150, "дробові градуси (float)", size=9, color=MUTED, italic=True))

    # стрілка перетворення
    p.append(arrow(lx + 78, 104, lx + 168, 104, color=STEPB, sw=2.4))
    p.append(text(lx + 123, 90, "× 10⁷", size=11, bold=True, color=STEPB))
    p.append(text(lx + 123, 122, "→ ціле", size=9, color=MUTED, italic=True))

    # ---- у центрі: ціле int32 ----
    cx = 470
    b, w, h = textbox(cx, 104, "lat_1e7\n504501000", size=12, bold=True,
                      fill=STEP, stroke=STEPB, sw=1.6, pad=10, min_w=150)
    p.append(b)
    p.append(text(cx, 150, "int32 — однакове на будь-якому приймачі", size=9,
                  color=MUTED, italic=True))

    # ---- праворуч: 4 байти на дроті ----
    rxs = 640
    p.append(text(rxs, 74, "4 байти на дроті", size=11, bold=True, color=MUTED))
    bx = rxs - 66
    for i, bt in enumerate(["08", "17", "13", "1E"]):
        p.append(rect(bx + i*34, 90, 30, 28, fill="#f0f4fa", stroke=STEPB, sw=1.3, rx=3))
        p.append(text(bx + i*34 + 15, 109, bt, size=10.5, color=INK))
    p.append(text(rxs, 150, "little-endian, як лежить у пам'яті", size=9,
                  color=MUTED, italic=True))

    # ---- знизу: розкладка одного 25-байтового повідомлення ----
    fy = 210
    p.append(text(W/2, fy - 14, "Одне повідомлення — рівно 25 байтів, поля на фіксованих місцях",
                  size=12, bold=True))
    # шкала полів (пропорції приблизні, для інтуїції розкладки)
    fields = [
        ("тип",       1,  WARM,  WARMB),
        ("ID оператора (20)", 20, STEP, STEPB),
        ("резерв", 4, "#eef1f4", "#9aa4b0"),
    ]
    fx0, fw_total = 70, 660
    total_units = sum(f[1] for f in fields)
    x = fx0
    for name, units, fill, stroke in fields:
        w = fw_total * units / total_units
        p.append(rect(x, fy, w, 40, fill=fill, stroke=stroke, sw=1.5, rx=4))
        p.append(fitbox(x, fy, w, 40, name, size=10, pad=4, fill="none",
                        stroke="none", sw=0, color=INK))
        x += w
    p.append(text(fx0, fy + 60, "0", size=9, color=MUTED, anchor="middle"))
    p.append(text(fx0 + fw_total, fy + 60, "25", size=9, color=MUTED, anchor="middle"))
    p.append(text(W/2, fy + 84,
                  "приймач знає розмір і місце кожного поля наперед — тому читає без «домовлянь»",
                  size=9.5, color=MUTED))
    p.append(text(W/2, fy + 100,
                  "(це лише Basic ID; поруч так само пакуються Location із координатами й Operator ID)",
                  size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "rid-frame.svg"), W, H, *p)


# ── rid_loop: стан мовника — «нема фіксу» / «мовлю», і як тікає таймер ────────
# Ідея: мовник — це маленький автомат на два стани. Поки GPS не дав фіксу,
# апарат мовить лише ідентифікацію (без брехливих координат); з фіксом — повний
# набір, рівним темпом (≥1 Гц). Таймер відрізає кадр незалежно від решти циклу.
def fig_rid_loop():
    W, H = 800, 330
    p = []
    p.append(text(W/2, 28, "Мовник — автомат на два стани, який штовхає таймер",
                  size=15, bold=True))

    # два стани
    b1, w1, h1 = textbox(210, 120, "НЕМА ФІКСУ\nмовлю лише ID\n(без координат)",
                         size=11, bold=True, fill=WARM, stroke=WARMB, sw=1.8, pad=12, min_w=180)
    p.append(b1)
    b2, w2, h2 = textbox(590, 120, "Є ФІКС\nмовлю ID + позицію\nповним набором",
                         size=11, bold=True, fill=GRASS, stroke=GRASSB, sw=1.8, pad=12, min_w=180)
    p.append(b2)

    # переходи між станами
    p.append(arrow(300, 108, 500, 108, color=GRASSB, sw=2.2))
    p.append(text(400, 98, "GPS дав фікс", size=10, color=GRASSB, italic=True))
    p.append(arrow(500, 140, 300, 140, color=WARMB, sw=2.2))
    p.append(text(400, 158, "фікс застарів / втрачено", size=10, color=WARMB, italic=True))

    # таймер знизу — спільний метроном
    ty = 235
    p.append(text(W/2, ty - 12, "таймер щосекунди «відрізає» кадр — незалежно від стану", size=11, bold=True, color=STEPB))
    # тік-мітки
    t0, t1 = 150, 650
    p.append(line(t0, ty + 12, t1, ty + 12, color="#c9cfd6", sw=2))
    for i in range(6):
        tx = t0 + (t1 - t0) * i / 5
        p.append(line(tx, ty + 6, tx, ty + 18, color=STEPB, sw=2))
        p.append(text(tx, ty + 34, "%d с" % i, size=9, color=MUTED))
    # стрілки-«надіслав кадр»
    for i in range(5):
        tx = t0 + (t1 - t0) * (i + 0.5) / 5
        p.append(text(tx, ty + 2, "📡", size=13))
    p.append(text(W/2, ty + 58,
                  "рівний темп ≥ 1 Гц важливіший за «свіжість» окремого кадру: приймач бачить безперервний слід",
                  size=9.5, color=MUTED))

    render(os.path.join(OUT, "rid-loop.svg"), W, H, *p)


# ── article8: чому одне речення 1944 р. протрималося 80 років ─────────────────
# Ідея: стаття 8 Чиказької конвенції описала ВЛАСТИВІСТЬ («здатний летіти без
# пілота»), а не конкретну машину — тому одне речення 1944-го, писане на тлі
# V-1 над Лондоном, однаково накриває мішень, летючу бомбу й сьогоднішній
# квадрокоптер і розгорнулося в усю сучасну гору правил про дрони.
def fig_article8():
    W, H = 820, 400
    p = []
    p.append(text(W/2, 28, "Одне речення 1944 р. → гора правил 2020-х: чому воно пережило 80 років",
                  size=14, bold=True))

    # ---- ліворуч: 1944, тло війни + задача авторів ----
    lx0, lw = 48, 300
    p.append(rect(lx0, 60, lw, 132, fill=WARM, stroke=WARMB, sw=1.6, rx=9))
    p.append(text(lx0 + lw/2, 84, "1944 · Чикаго", size=13, bold=True, color=WARMB))
    p.append(text(lx0 + lw/2, 102, "конвенцію пишуть, поки", size=9.5, color=INK))
    p.append(text(lx0 + lw/2, 116, "V-1 падають на Лондон", size=9.5, color=INK))
    # схематична «летюча бомба» V-1
    p.append(rect(lx0 + 58, 136, 40, 12, fill="#444a52", stroke="#22262b", sw=1.2, rx=3))
    p.append(line(lx0 + 98, 142, lx0 + 114, 142, color="#22262b", sw=2.0))  # струмінь
    p.append(text(lx0 + lw/2, 176, "задача: не пустити їх у чуже небо", size=9, color=WARMB, italic=True))

    # стрілка-міст 1944 → 2020-ті
    p.append(arrow(lx0 + lw + 6, 126, 470, 126, color=STEPB, sw=2.2))
    p.append(text(410, 118, "80 років", size=9.5, color=STEPB, italic=True))

    # ---- праворуч: 2020-ті, гора правил ----
    rx0, rw = 472, 300
    p.append(rect(rx0, 60, rw, 132, fill=SKY, stroke=SKYB, sw=1.6, rx=9))
    p.append(text(rx0 + rw/2, 82, "2020-ті · та сама стаття 8,", size=12, bold=True, color=SKYB))
    p.append(text(rx0 + rw/2, 98, "лише конкретизована", size=12, bold=True, color=SKYB))
    rules = ["реєстрація оператора", "класи C0…C4 · CE", "Remote ID", "геозони · межа висоти"]
    ry = 120
    for r in rules:
        p.append(text(rx0 + 22, ry, "•  " + r, size=9.5, color=INK, anchor="start"))
        ry += 17

    # ---- центр: ключ — право описало ВЛАСТИВІСТЬ, не машину ----
    b, w, h = textbox(W/2, 238,
                      "стаття 8: «capable of being\nflown without a pilot»\n— властивість, не машина",
                      size=10.5, bold=True, fill=STEP, stroke=STEPB, sw=1.8, pad=9)
    p.append(b)

    # три покоління машин, які ловить та сама властивість
    gens = [(150, "мішень\n1935"), (410, "летюча бомба\n1944"), (670, "квадрокоптер\n2025")]
    gy = 312
    p.append(text(W/2, gy - 16, "одне правило накриває всі три покоління", size=9.5, color=STEPB, italic=True))
    p.append(line(150, gy, 670, gy, color=STEPB, sw=1.3, dash="4 4"))
    for gx, lbl in gens:
        p.append(circle(gx, gy, 6, fill=STEP, stroke=STEPB, sw=1.6))
        for j, seg in enumerate(lbl.split("\n")):
            p.append(text(gx, gy + 20 + j*12, seg, size=8.5, color=MUTED))

    p.append(text(W/2, 388,
                  "право, що описує СУТЬ явища, а не тодішній зразок техніки, старіє повільно",
                  size=9.5, color=MUTED))

    render(os.path.join(OUT, "article8.svg"), W, H, *p)


# ── mass_energy: чому 250 г — ланцюжок маса → v_term → енергія → травма ───────
# Ідея (детальна): поріг маси НЕ довільний. Маса задає термінальну швидкість
# (рівновага ваги й опору повітря → росте як √маси), швидкість у квадраті задає
# енергію удару, енергія — ймовірність смертельної травми. Для 0.25 кг модель
# дає ≈25.9 м/с і ≈84 Дж — рівно межу «серйозної загрози», звідси 250 г.
def fig_mass_energy():
    W, H = 820, 340
    p = []
    p.append(text(W/2, 28, "Чому 250 г: маса → швидкість → енергія → ймовірність травми",
                  size=15, bold=True))

    # чотири ланки ланцюжка, стрілки між ними
    box_w = 168
    ys = 150
    links = [
        (110, "маса\nm = 0.25 кг", WARM, WARMB, "вхід: те, що\nлегко зважити"),
        (320, "термінальна\nшвидкість\nv ≈ 25.9 м/с", STEP, STEPB, "рівновага ваги\nй опору повітря"),
        (530, "енергія удару\nE = ½mv²\n≈ 84 Дж", STEP, STEPB, "швидкість —\nу квадраті"),
        (730, "ймовірність\nсмерті\n≈ 30%", SKY, SKYB, "80 Дж у голову\n(мед. дані)"),
    ]
    for cx, label, fill, stroke, _ in links:
        b, w, h = textbox(cx, ys, label, size=10.5, bold=True, fill=fill, stroke=stroke,
                          sw=1.7, pad=10, min_w=box_w)
        p.append(b)

    # стрілки й підписи-«чому» між ланками
    joins = [
        (110, 320, "√ маси"),
        (320, 530, "× v²"),
        (530, 730, "→ травма"),
    ]
    for x1, x2, lbl in joins:
        ax1 = x1 + box_w/2 + 2
        ax2 = x2 - box_w/2 - 2
        p.append(arrow(ax1, ys, ax2, ys, color=INK, sw=2.2))
        p.append(text((ax1 + ax2)/2, ys - 12, lbl, size=10, bold=True, color=INK))

    # нижні підписи-пояснення під кожною ланкою
    for cx, _, _, _, note in links:
        for j, seg in enumerate(note.split("\n")):
            p.append(text(cx, ys + 62 + j*13, seg, size=8.5, color=MUTED))

    # висновок унизу
    p.append(text(W/2, 300,
                  "поріг стоїть там, де ланцюжок виходить на межу «переживно / ні» — тому саме 250 г, а не 200 чи 300",
                  size=10, color=MUTED))
    p.append(text(W/2, 320,
                  "маса — лише перша ланка й грубий проксі; справжня небезпека — енергія на кінці ланцюжка",
                  size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "mass-energy.svg"), W, H, *p)


# ── two_hazards: одна машина — дві задачі про удар із різними числами ─────────
# Ідея (детальна): удар об землю (термінальна швидкість, десятки м/с, енергію
# задає маса) і зіткнення з літаком (швидкість зближення, сотні м/с, енергія на
# порядок більша при тій самій масі) — РІЗНА фізика. Тому маса й висота
# регулюються НЕЗАЛЕЖНО: маса — щаблі класів, висота/зони — окремо.
def fig_two_hazards():
    W, H = 820, 360
    p = []
    p.append(text(W/2, 28, "Один апарат — дві небезпеки з різними числами",
                  size=15, bold=True))

    # роздільник посередині
    p.append(line(W/2, 56, W/2, 316, color="#dde1e6", sw=1.2, dash="5 5"))

    # ---- ЛІВОРУЧ: удар об землю ----
    lx = 205
    p.append(text(lx, 74, "1 · удар об землю", size=12.5, bold=True, color=WARMB))
    # дрон угорі
    p.append(rect(lx - 20, 92, 40, 14, fill="#444a52", stroke="#22262b", sw=1.2, rx=3))
    for gx in (lx - 12, lx + 12):
        p.append(circle(gx, 99, 7, fill="none", stroke="#22262b", sw=1.5))
    # падіння вниз
    p.append(arrow(lx, 110, lx, 176, color=WARMB, sw=2.2))
    p.append(text(lx + 74, 145, "v термінальна", size=9.5, color=WARMB, italic=True))
    p.append(text(lx + 74, 159, "≈ 36 м/с", size=9.5, color=WARMB, italic=True))
    # людина + земля
    p.append(circle(lx, 190, 8, fill=WARM, stroke=WARMB, sw=1.5))
    p.append(line(lx - 55, 210, lx + 55, 210, color="#c9cfd6", sw=2.0))
    # число енергії
    b, w, h = textbox(lx, 244, "E ≈ 324 Дж\n(апарат 0.5 кг)", size=10.5, bold=True,
                      fill=WARM, stroke=WARMB, sw=1.6, pad=8, min_w=150)
    p.append(b)
    p.append(text(lx, 300, "енергію задає МАСА → щаблі класів", size=9.5, color=MUTED))
    p.append(text(lx, 316, "(250 г · 900 г · 4 кг · 25 кг)", size=9, color=MUTED, italic=True))

    # ---- ПРАВОРУЧ: зіткнення з літаком ----
    rx = 615
    p.append(text(rx, 74, "2 · зіткнення з літаком", size=12.5, bold=True, color=SKYB))
    # літак ліворуч, летить праворуч; дрон майже стоїть
    p.append(text(rx - 90, 128, "✈", size=30, color="#22262b"))
    p.append(arrow(rx - 62, 120, rx - 6, 120, color=SKYB, sw=2.4))
    p.append(text(rx - 34, 108, "150 м/с", size=9.5, color=SKYB, italic=True))
    # дрон
    p.append(rect(rx + 6, 114, 30, 11, fill="#444a52", stroke="#22262b", sw=1.1, rx=3))
    for gx in (rx + 12, rx + 30):
        p.append(circle(gx, 120, 5, fill="none", stroke="#22262b", sw=1.3))
    p.append(text(rx + 60, 138, "швидкість удару =", size=9, color=MUTED))
    p.append(text(rx + 60, 151, "швидкість зближення", size=9, color=MUTED))
    # число енергії
    b, w, h = textbox(rx, 244, "E ≈ 5625 Дж\n(та сама 0.5 кг!)", size=10.5, bold=True,
                      fill=SKY, stroke=SKYB, sw=1.6, pad=8, min_w=150)
    p.append(b)
    p.append(text(rx, 300, "≈ у 17× більше при тій самій масі", size=9.5, color=MUTED))
    p.append(text(rx, 316, "→ окремо регулюють ВИСОТУ й зони", size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-hazards.svg"), W, H, *p)


# ── module_block: що всередині начіпного модуля-мовника й чим він тапиться ─────
# Ідея вставки comp-remote-id-module: модуль — самодостатня коробочка. Усередині
# ВЛАСНИЙ GNSS (бо з польотним контролером він не з'єднаний), ВЛАСНЕ BLE/Wi-Fi
# радіо (несуча, яку почує смартфон), МК, що збирає стандартний кадр, і живлення.
# Назовні — лише два дроти: живлення й спільна земля. Він НІЧОГО не бере з апарата,
# крім струму: не знає ні координат пілота, ні даних автопілота. У цьому і сила
# (чіпляй на будь-що), і межа (нижчий клас функціональності).
def fig_module_block():
    W, H = 960, 470
    p = []
    p.append(text(W/2, 30, "Начіпний модуль-мовник: самодостатня коробочка на двох дротах",
                  size=15, bold=True))

    # ── рамка самого модуля (ліва частина) ──
    mx, my, mw, mh = 60, 66, 400, 356
    p.append(rect(mx, my, mw, mh, fill="#fbfcfe", stroke=STEPB, sw=1.8, rx=10))
    p.append(text(mx + mw/2, my + 26, "МОДУЛЬ Remote ID (broadcast)", size=11.5,
                  bold=True, color=STEPB))

    cxm = mx + mw/2
    # антена вгорі праворуч від рамки (щоб лінія не різала написи всередині)
    antx = mx + mw - 46
    p.append(line(antx, my, antx, my - 40, color=INK, sw=2.2))
    p.append(circle(antx, my - 44, 5, fill="none", stroke=INK, sw=1.8))
    p.append(text(antx, my - 54, "антена", size=9, color=MUTED))

    # внутрішні блоки — СТОВПЧИКОМ (короткі вертикальні стрілки, без перетинів)
    # 1) GNSS
    gy = my + 66
    b, w, h = textbox(cxm, gy, "власний GNSS-приймач", size=11, bold=True,
                      fill=GRASS, stroke=GRASSB, sw=1.6, pad=10, min_w=300)
    p.append(b)
    p.append(text(cxm, gy + 30, "сам бачить супутники — координат ззовні НЕ бере",
                  size=8.5, color=MUTED, italic=True))
    p.append(text(cxm - 150, gy - 6, "🛰", size=16))

    # 2) МК
    ky = my + 148
    b, w, h = textbox(cxm, ky, "МК: збирає стандартний кадр", size=11, bold=True,
                      fill=STEP, stroke=STEPB, sw=1.6, pad=10, min_w=300)
    p.append(b)
    p.append(text(cxm, ky + 30, "ASTM F3411 / EN 4709-002", size=8.5, color=MUTED, italic=True))
    p.append(arrow(cxm, gy + 40, cxm, ky - 22, color=GRASSB, sw=1.8))  # GNSS → МК

    # 3) радіо
    ry = my + 230
    b, w, h = textbox(cxm, ry, "BLE 5 / Wi-Fi радіо 2.4/5 ГГц", size=11, bold=True,
                      fill=SKY, stroke=SKYB, sw=1.6, pad=10, min_w=300)
    p.append(b)
    p.append(text(cxm, ry + 30, "несуча, яку чує звичайний смартфон", size=8.5,
                  color=MUTED, italic=True))
    p.append(arrow(cxm, ky + 40, cxm, ry - 22, color=STEPB, sw=1.8))  # МК → радіо
    # радіо → антена (вгору по правому краю, повз написи)
    p.append(line(cxm + 152, ry, antx, ry, color=SKYB, sw=1.7))
    p.append(line(antx, ry, antx, my + 4, color=SKYB, sw=1.7))

    # 4) живлення
    py = my + 312
    b, w, h = textbox(cxm, py, "живлення: від апарата АБО власна батарея", size=10, bold=True,
                      fill=WARM, stroke=WARMB, sw=1.6, pad=9, min_w=320)
    p.append(b)

    # ── два дроти назовні (праворуч від рамки) ──
    wy1, wy2 = my + 300, my + 324
    p.append(line(mx + mw, wy1, mx + mw + 70, wy1, color=POS, sw=2.4))
    p.append(plus(mx + mw + 80, wy1, r=8))
    p.append(line(mx + mw, wy2, mx + mw + 70, wy2, color=NEG, sw=2.4))
    p.append(minus(mx + mw + 80, wy2, r=8))
    p.append(text(mx + mw + 100, wy1 - 2, "5 В із бортової шини", size=9.5, color=MUTED, anchor="start"))
    p.append(text(mx + mw + 100, wy2 + 12, "спільна земля", size=9.5, color=MUTED, anchor="start"))

    # ── апарат праворуч ──
    ax, aw = mx + mw + 250, 190
    p.append(rect(ax, my + 70, aw, 150, fill="#eef1f4", stroke="#9aa4b0", sw=1.6, rx=10))
    p.append(text(ax + aw/2, my + 100, "СТАРИЙ апарат", size=12, bold=True, color=INK))
    p.append(text(ax + aw/2, my + 128, "автопілот, що про", size=9.5, color=MUTED))
    p.append(text(ax + aw/2, my + 144, "Remote ID не знає", size=9.5, color=MUTED))
    p.append(text(ax + aw/2, my + 176, "✕ жодного обміну", size=9.5, bold=True, color=POS))
    p.append(text(ax + aw/2, my + 192, "даними з модулем", size=9.5, color=POS, italic=True))

    p.append(text(W/2, H - 14,
                  "Модуль бере з апарата лише струм. Свою позицію знаходить сам — тому чіпляється на будь-що, "
                  "але й не знає нічого, крім власного місця.",
                  size=9.5, color=MUTED))

    render(os.path.join(OUT, "module-block.svg"), W, H, *p)


# ── takeoff_vs_pilot: чому модуль мовить ТОЧКУ ЗЛЬОТУ, а не місце пілота ───────
# Ідея: вбудований standard RID знає, ДЕ пульт (він з ним з'єднаний), тому мовить
# реальне місце пілота. Начіпний модуль із пультом НЕ з'єднаний — координат пілота
# він фізично взяти нізвідки, тому підставляє ЄДИНЕ місце, яке в нього є: точку,
# де його ввімкнули (зазвичай = точка зльоту). Якщо пілот відійшов — приймач бачить
# «пілота» на старті, хоча він уже деінде. Це і є нижчий клас функціональності.
def fig_takeoff_vs_pilot():
    W, H = 840, 360
    p = []
    p.append(text(W/2, 28, "Місце пілота модуль НЕ знає — мовить точку, де його ввімкнули",
                  size=15, bold=True))

    # роздільник
    p.append(line(W/2, 52, W/2, 300, color="#dde1e6", sw=1.2, dash="5 5"))

    # ── ЛІВОРУЧ: вбудований standard RID ──
    p.append(text(210, 70, "вбудований standard RID", size=12.5, bold=True, color=GRASSB))
    # апарат у повітрі
    p.append(rect(150, 96, 40, 14, fill="#444a52", stroke="#22262b", sw=1.2, rx=3))
    for gx in (162, 178):
        p.append(circle(gx, 103, 6, fill="none", stroke="#22262b", sw=1.3))
    # пульт з'єднаний із апаратом (лінія зв'язку)
    p.append(line(170, 112, 300, 210, color=GRASSB, sw=1.6, dash="4 4"))
    p.append(text(258, 150, "лінк", size=9, color=GRASSB, italic=True))
    # пілот із пультом
    p.append(circle(300, 218, 9, fill=GRASS, stroke=GRASSB, sw=1.6))
    p.append(line(300, 227, 300, 250, color=GRASSB, sw=1.9))
    p.append(rect(288, 232, 24, 10, fill="#fff", stroke=GRASSB, sw=1.4, rx=2))
    p.append(text(300, 268, "пілот ТУТ", size=10, bold=True, color=GRASSB))
    # земля
    p.append(line(120, 288, 300, 288, color="#c9cfd6", sw=2.0))
    p.append(text(210, 314, "апарат знає, де пульт → мовить", size=9.5, color=MUTED))
    p.append(text(210, 330, "СПРАВЖНЄ місце пілота (C1+)", size=9.5, color=INK, italic=True))

    # ── ПРАВОРУЧ: начіпний модуль ──
    p.append(text(625, 70, "начіпний модуль", size=12.5, bold=True, color=WARMB))
    # апарат у повітрі з модулем
    p.append(rect(700, 96, 40, 14, fill="#444a52", stroke="#22262b", sw=1.2, rx=3))
    for gx in (712, 728):
        p.append(circle(gx, 103, 6, fill="none", stroke="#22262b", sw=1.3))
    p.append(rect(742, 98, 12, 10, fill=SKY, stroke=SKYB, sw=1.2, rx=2))  # модуль
    # точка ввімкнення = точка зльоту (де апарат стартував)
    p.append(circle(560, 250, 7, fill=WARM, stroke=WARMB, sw=1.8))
    p.append(text(560, 274, "точка ЗЛЬОТУ", size=9.5, bold=True, color=WARMB))
    p.append(text(560, 288, "(де ввімкнули)", size=8.5, color=MUTED, italic=True))
    # пілот НАСПРАВДІ відійшов у інше місце
    p.append(circle(690, 226, 9, fill="#f6eaea", stroke=POS, sw=1.6))
    p.append(line(690, 235, 690, 256, color=POS, sw=1.9))
    p.append(text(690, 274, "пілот НАСПРАВДІ", size=9.5, bold=True, color=POS))
    p.append(text(690, 288, "уже тут — модуль не знає", size=8.5, color=POS, italic=True))
    # хрестик «не з'єднаний»
    p.append(text(625, 150, "✕ нема лінку з пультом", size=10, bold=True, color=POS))
    # земля
    p.append(line(520, 300, 760, 300, color="#c9cfd6", sw=2.0))

    render(os.path.join(OUT, "takeoff-vs-pilot.svg"), W, H, *p)


# ── sora_branches: чому SORA рахує РИЗИК двома незалежними гілками ────────────
# Ідея (math-вставка): наземна й повітряна небезпеки — різна фізика (див.
# two-hazards), тож SORA й міряє їх ОКРЕМО. Ліва гілка: щільність людей унизу ×
# розмір/енергія апарата → клас наземного ризику (GRC 1…10), який заходи
# (парашут, надійна термінація, вужчий буфер) ЗНИЖУЮТЬ. Права гілка: тип простору
# й трафік → клас повітряного ризику (ARC a…d). Дві гілки сходяться в матриці →
# SAIL I…VI: потрібний рівень надійності операції. Показуємо «дві осі → одне».
def fig_sora_branches():
    W, H = 860, 480
    p = []
    p.append(text(W/2, 30, "SORA міряє ризик двома незалежними гілками — бо це дві різні фізики",
                  size=15, bold=True))

    # ── ЛІВА ГІЛКА: наземний ризик ──────────────────────────────────────────
    lcx = 225
    p.append(text(lcx, 68, "НАЗЕМНИЙ ризик: якщо впаде", size=12.5, bold=True, color=WARMB))
    b, w, h = textbox(lcx - 96, 112, "щільність людей\nунизу (осіб/км²)", size=10,
                      fill=WARM, stroke=WARMB, sw=1.4, pad=8, min_w=156)
    p.append(b)
    b, w, h = textbox(lcx + 96, 112, "розмір і енергія\nудару апарата", size=10,
                      fill=WARM, stroke=WARMB, sw=1.4, pad=8, min_w=156)
    p.append(b)
    p.append(arrow(lcx - 72, 136, lcx - 20, 176, color=WARMB, sw=2.0))
    p.append(arrow(lcx + 72, 136, lcx + 20, 176, color=WARMB, sw=2.0))
    b, w, h = textbox(lcx, 198, "клас наземного\nризику  GRC 1…10", size=11, bold=True,
                      fill=STEP, stroke=STEPB, sw=1.7, pad=9, min_w=186)
    p.append(b)
    p.append(arrow(lcx, 222, lcx, 268, color=NEG, sw=2.2))
    p.append(minus(lcx - 96, 245, r=9))
    p.append(text(lcx - 96, 274, "заходи", size=9, color=NEG))
    p.append(text(lcx + 70, 240, "парашут, надійна", size=9, color=NEG, anchor="start"))
    p.append(text(lcx + 70, 253, "термінація,", size=9, color=NEG, anchor="start"))
    p.append(text(lcx + 70, 266, "вужчий буфер", size=9, color=NEG, anchor="start"))
    b, w, h = textbox(lcx, 292, "фінальний GRC\n(нижчий = легше)", size=10.5, bold=True,
                      fill=GRASS, stroke=GRASSB, sw=1.6, pad=8, min_w=176)
    p.append(b)

    # роздільник між гілками
    p.append(line(W/2, 60, W/2, 330, color="#dde1e6", sw=1.2, dash="5 5"))

    # ── ПРАВА ГІЛКА: повітряний ризик ───────────────────────────────────────
    rcx = 635
    p.append(text(rcx, 68, "ПОВІТРЯНИЙ ризик: із чим зіткнеться", size=12, bold=True, color=SKYB))
    b, w, h = textbox(rcx - 96, 112, "тип простору\n(де летиш)", size=10,
                      fill=SKY, stroke=SKYB, sw=1.4, pad=8, min_w=156)
    p.append(b)
    b, w, h = textbox(rcx + 96, 112, "щільність\nтрафіку", size=10,
                      fill=SKY, stroke=SKYB, sw=1.4, pad=8, min_w=156)
    p.append(b)
    p.append(arrow(rcx - 72, 136, rcx - 20, 176, color=SKYB, sw=2.0))
    p.append(arrow(rcx + 72, 136, rcx + 20, 176, color=SKYB, sw=2.0))
    b, w, h = textbox(rcx, 198, "клас повітряного\nризику  ARC a…d", size=11, bold=True,
                      fill=STEP, stroke=STEPB, sw=1.7, pad=9, min_w=186)
    p.append(b)
    p.append(arrow(rcx, 222, rcx, 268, color=NEG, sw=2.2))
    p.append(minus(rcx - 96, 245, r=9))
    p.append(text(rcx - 96, 274, "заходи", size=9, color=NEG))
    p.append(text(rcx + 70, 244, "розділення", size=9, color=NEG, anchor="start"))
    p.append(text(rcx + 70, 257, "висотами,", size=9, color=NEG, anchor="start"))
    p.append(text(rcx + 70, 270, "координація", size=9, color=NEG, anchor="start"))
    b, w, h = textbox(rcx, 292, "залишковий ARC", size=10.5, bold=True,
                      fill=GRASS, stroke=GRASSB, sw=1.6, pad=8, min_w=176)
    p.append(b)

    # ── СХОДЖЕННЯ: дві гілки → SAIL ─────────────────────────────────────────
    p.append(arrow(lcx, 314, W/2 - 70, 368, color=INK, sw=2.2))
    p.append(arrow(rcx, 314, W/2 + 70, 368, color=INK, sw=2.2))
    b, w, h = textbox(W/2, 396, "матриця (GRC × ARC)  →  SAIL  I…VI", size=12.5, bold=True,
                      fill="#eef1f4", stroke=STEPB, sw=1.8, pad=11, min_w=390)
    p.append(b)
    p.append(text(W/2, 440, "SAIL = потрібний рівень надійності операції: скільки й якої певності",
                  size=10, color=MUTED))
    p.append(text(W/2, 456, "оператор мусить довести. Вищий GRC чи ARC → вищий SAIL → суворіші вимоги.",
                  size=10, color=MUTED))

    render(os.path.join(OUT, "sora-branches.svg"), W, H, *p)


# ── sora_buffer: правило 1:1 і як кращий failsafe звужує буфер → нижчий GRC ───
# Ідея (math-вставка): після припинення польоту апарат ще летить/планерує вперед,
# поки падає. Скільки вбік він накриє? Груба консервативна оцінка — правило 1:1:
# горизонтальний розліт ≈ висоті. Летиш на 120 м — закладай буфер ≥120 м навколо
# зони. АЛЕ надійна термінація (парашут, миттєве глушіння) різко коротшає розліт,
# тож буфер вужчий → накриває менше людей унизу → нижчий клас наземного ризику.
def fig_sora_buffer():
    W, H = 860, 440
    p = []
    p.append(text(W/2, 30, "Буфер наземного ризику: правило 1:1 і як кращий failsafe його звужує",
                  size=14.5, bold=True))

    ground = 322          # рівень землі
    top    = 100          # висота польоту (лінія апарата)
    # спільна шкала висоти ліворуч
    p.append(line(66, top, 66, ground, color="#c9cfd6", sw=1.5))
    p.append(arrow(66, ground, 66, top - 4, color=MUTED, sw=1.4))
    p.append(text(52, (top + ground)/2 - 6, "H", size=12, bold=True, color=INK, anchor="end"))
    p.append(text(52, (top + ground)/2 + 10, "120 м", size=9, color=MUTED, anchor="end"))
    p.append(line(66, top, 820, top, color="#e3e7ec", sw=1.0, dash="4 4"))
    p.append(text(812, top - 8, "припинення польоту на висоті H", size=9.5,
                  color=MUTED, anchor="end", italic=True))

    # ── ЛІВОРУЧ: балістика, розліт ≈ H (правило 1:1) ────────────────────────
    lx0 = 140
    p.append(text(lx0 + 100, top - 26, "1 · без надійної термінації", size=11.5, bold=True, color=WARMB))
    p.append(rect(lx0 - 16, top - 8, 32, 12, fill="#444a52", stroke="#22262b", sw=1.2, rx=3))
    reach = ground - top   # розліт по горизонталі ≈ H (правило 1:1)
    pts = []
    for i in range(0, 21):
        t = i / 20.0
        gx = lx0 + reach * t
        gy = top + (ground - top) * t * t     # параболічне падіння
        pts.append((gx, gy))
    for i in range(len(pts) - 1):
        p.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=WARMB, sw=2.2))
    p.append(circle(lx0 + reach, ground, 5, fill=WARM, stroke=WARMB, sw=1.6))
    p.append(line(lx0, ground + 16, lx0 + reach, ground + 16, color=WARMB, sw=1.6))
    p.append(line(lx0, ground + 11, lx0, ground + 21, color=WARMB, sw=1.6))
    p.append(line(lx0 + reach, ground + 11, lx0 + reach, ground + 21, color=WARMB, sw=1.6))
    p.append(text(lx0 + reach/2, ground + 34, "буфер ≈ H = 120 м", size=10, bold=True, color=WARMB))
    p.append(text(lx0 + reach/2, ground + 48, "(правило 1:1)", size=9, color=MUTED, italic=True))

    # роздільник
    p.append(line(W/2, 62, W/2, ground + 20, color="#dde1e6", sw=1.2, dash="5 5"))

    # ── ПРАВОРУЧ: парашут, розліт короткий → буфер вужчий ───────────────────
    rx0 = 570
    p.append(text(rx0 + 30, top - 26, "2 · надійна термінація (парашут)", size=11.5, bold=True, color=GRASSB))
    p.append(rect(rx0 - 16, top - 8, 32, 12, fill="#444a52", stroke="#22262b", sw=1.2, rx=3))
    p.append(text(rx0, top + 24, "🪂", size=20))
    reach2 = 58
    pts2 = []
    for i in range(0, 21):
        t = i / 20.0
        gx = rx0 + reach2 * t
        gy = top + (ground - top) * t          # рівномірне (парашут) — майже вниз
        pts2.append((gx, gy))
    for i in range(len(pts2) - 1):
        p.append(line(pts2[i][0], pts2[i][1], pts2[i+1][0], pts2[i+1][1], color=GRASSB, sw=2.2))
    p.append(circle(rx0 + reach2, ground, 5, fill=GRASS, stroke=GRASSB, sw=1.6))
    p.append(line(rx0, ground + 16, rx0 + reach2, ground + 16, color=GRASSB, sw=1.6))
    p.append(line(rx0, ground + 11, rx0, ground + 21, color=GRASSB, sw=1.6))
    p.append(line(rx0 + reach2, ground + 11, rx0 + reach2, ground + 21, color=GRASSB, sw=1.6))
    p.append(text(rx0 + reach2 + 24, ground + 40, "буфер вужчий", size=10, bold=True, color=GRASSB, anchor="start"))
    p.append(text(rx0 + reach2 + 24, ground + 54, "(розліт короткий)", size=9, color=MUTED, italic=True, anchor="start"))

    # земля під обома
    p.append(line(80, ground, 820, ground, color="#9aa4b0", sw=2.0))

    # висновок унизу
    p.append(text(W/2, ground + 82,
                  "вужчий буфер накриває менше людей унизу → нижчий клас наземного ризику (GRC) → простіший дозвіл",
                  size=10.5, bold=True, color=STEPB))
    p.append(text(W/2, ground + 100,
                  "тому якість вашого flight termination прямо конвертується в дешевший юридичний шлях для оператора",
                  size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "sora-buffer.svg"), W, H, *p)


if __name__ == "__main__":
    fig_root()
    fig_tiers()
    fig_duties()
    fig_rid_frame()
    fig_rid_loop()
    fig_article8()
    fig_mass_energy()
    fig_two_hazards()
    fig_module_block()
    fig_takeoff_vs_pilot()
    fig_sora_branches()
    fig_sora_buffer()
    print("figs done:", os.listdir(OUT))
