# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні відтінки (єдина палітра svgkit + кілька світлих заливок під неї)
GOLD   = "#b8860b"        # «жовта» лінія CC / клас «3 А»
GOLDBG = "#fbf7ec"
POSBG  = "#fdecea"
NEGBG  = "#eaf0fd"
FLDBG  = "#eaf7ee"
GREY   = "#f4f6f8"


# ── cable: що всередині кабелю й три класи ────────────────────────────────────
# Ідея: штекери однакові, а нутро різне — звідси «однакові на око, різні по суті»
# шнури. Показуємо групи жил і три класи, що прямо вирішують, на що шнур здатен.

def fig_cable():
    W, H = 760, 470
    p = []
    # корпус кабелю між двома штекерами
    p.append(rect(60, 64, 22, 56, fill="none", stroke=INK, sw=2, rx=5))
    p.append(rect(66, 74, 11, 36, fill=INK, stroke=INK, sw=0, rx=0))
    p.append(rect(678, 64, 22, 56, fill="none", stroke=INK, sw=2, rx=5))
    p.append(rect(684, 74, 11, 36, fill=INK, stroke=INK, sw=0, rx=0))
    p.append(rect(82, 64, 596, 56, fill="#fbfbf8", stroke=MUTED, sw=1.4, rx=12))
    # чотири групи жил
    rows = [(POS, 78), (GOLD, 90), (NEG, 102), (FIELD, 114)]
    for col, yy in rows:
        p.append(line(104, yy, 656, yy, color=col, sw=3))
    # e-marker у штекері
    eb = rect(596, 70, 56, 24, fill=NEGBG, stroke=NEG, sw=1.6, rx=5)
    p.append(eb)
    p.append(text(624, 86, "e-marker", size=9, color=NEG, bold=True))

    # легенда жил
    leg = [
        (POS,   "VBUS / GND — живлення; товщина дроту вирішує падіння"),
        (GOLD,  "CC — орієнтація, роль, живить e-marker (VCONN)"),
        (NEG,   "D+ / D− — дані USB 2.0"),
        (FIELD, "SS-пари — швидкі дані / відео (USB 3.x), є не в усіх"),
    ]
    ly = 158
    for col, s in leg:
        p.append(line(70, ly - 4, 100, ly - 4, color=col, sw=3))
        p.append(text(110, ly, s, size=10.5, anchor="start"))
        ly += 26

    # три класи
    cards = [
        (60,  POS,  POSBG,  "«тільки заряд»",
         ["лише VBUS/GND (іноді CC).", "даних нема — пристрій", "не домовиться по D+/D−"]),
        (286, GOLD, GOLDBG, "повний, 3 А",
         ["усі лінії, без e-marker.", "заряд і дані, але струм", "обмежать безпечними 3 А"]),
        (512, FIELD, FLDBG, "5 А / EPR",
         ["усі лінії + e-marker.", "повний струм і висока", "напруга (потрібен чип)"]),
    ]
    cy = 296
    for x, col, bg, head, body in cards:
        p.append(rect(x, cy, 188, 132, fill=bg, stroke=col, sw=1.8, rx=10))
        p.append(text(x + 94, cy + 26, head, size=12, color=col, bold=True))
        p.append(line(x + 16, cy + 38, x + 172, cy + 38, color="#e4e4e4", sw=1))
        ty = cy + 62
        for ln in body:
            p.append(text(x + 94, ty, ln, size=9.5, color=INK if ty == cy + 62 else MUTED))
            ty += 20

    render(os.path.join(OUT, "cable.svg"), W, H, *p,
           title="Що всередині USB-C кабелю — і чому вони такі різні")


# ── emarker: без чипа система перестраховується, з чипом — знає межі ───────────
# Ідея: e-marker — паспорт кабелю. Нема паспорта → найгірше припущення (3 А);
# є → чип доповідає струм/швидкість/довжину/тип, і лише тоді можливі 5 А й EPR.

def fig_emarker():
    W, H = 740, 420
    p = []
    # ліва панель — без чипа
    p.append(rect(50, 64, 312, 132, fill=GOLDBG, stroke=GOLD, sw=1.7, rx=12))
    p.append(text(206, 90, "Кабель БЕЗ e-marker", size=12.5, color=GOLD, bold=True))
    p.append(line(80, 122, 332, 122, color=GOLD, sw=3))
    p.append(text(206, 152, "система не знає меж кабелю", size=10.5))
    p.append(text(206, 174, "→ припускає безпечні 3 А, EPR нема", size=10.5, bold=True))
    # права панель — з чипом
    p.append(rect(378, 64, 312, 132, fill=FLDBG, stroke=FIELD, sw=1.7, rx=12))
    p.append(text(534, 90, "Кабель З e-marker", size=12.5, color=FIELD, bold=True))
    p.append(line(408, 122, 660, 122, color=GOLD, sw=3))
    p.append(rect(504, 108, 56, 24, fill=NEGBG, stroke=NEG, sw=1.6, rx=5))
    p.append(text(532, 124, "e-marker", size=9, color=NEG, bold=True))
    p.append(text(534, 152, "живиться з VCONN", size=9.5, color=MUTED))
    p.append(text(534, 174, "→ доповідає: 5 А, швидкість, довжина", size=10.5, bold=True))

    # що каже e-marker
    p.append(rect(110, 224, 520, 100, fill=GREY, stroke=MUTED, sw=1.4, rx=12))
    p.append(text(370, 250, "Що каже e-marker системі", size=12, bold=True))
    cols = [(178, "струм", "3 А чи 5 А"), (320, "швидкість", "USB 2.0 / 3.x"),
            (450, "довжина", "затримки, втрати"), (572, "тип", "пасивний / активний")]
    for cx, h, sub in cols:
        p.append(text(cx, 280, h, size=11, color=FIELD, bold=True))
        p.append(text(cx, 300, sub, size=9.5))

    # підсумок
    p.append(rect(50, 344, 640, 52, fill=FLDBG, stroke=FIELD, sw=1.5, rx=8))
    p.append(mtext(370, 366,
                   ["Понад 3 А й уся EPR можливі лише з кабелем, що має e-marker. Нема чипа — система",
                    "перестраховується 3 амперами, хоч би що міг зарядний; тому «той самий блок, інший шнур»"],
                   size=10, color=INK, lh=1.4))

    render(os.path.join(OUT, "emarker.svg"), W, H, *p,
           title="e-marker: чип, що дозволяє кабелю більше")


# ── drop: 5 В виходять, 4.2 В доходять ────────────────────────────────────────
# Ідея: кабель — це опір; під струмом на ньому падає ΔV = I·R, і ця напруга не
# доходить до пристрою. Вища напруга PD несе той самий ват меншим струмом.

def fig_drop():
    W, H = 760, 400
    p = []
    # зарядка
    p.append(rect(50, 96, 124, 80, fill=POSBG, stroke=POS, sw=1.8, rx=10))
    p.append(text(112, 126, "зарядка", size=11, color=POS, bold=True))
    p.append(text(112, 152, "5.0 В", size=16, color=POS, bold=True))
    # дві жили
    p.append(line(174, 118, 600, 118, color=GOLD, sw=3))
    p.append(line(174, 152, 600, 152, color=GOLD, sw=3))
    # резистор кабелю
    p.append(rect(348, 100, 78, 36, fill=BG, stroke=GOLD, sw=1.8, rx=4))
    p.append(text(387, 122, "R кабелю", size=10.5, color=GOLD, bold=True))
    p.append(text(387, 188, "R = 2×Rдроту + Rконтактів", size=10))
    # струм
    p.append(arrow(232, 135, 296, 135, color=POS, sw=2))
    p.append(text(264, 127, "I →", size=9.5, color=POS, bold=True))
    # пристрій
    p.append(rect(600, 96, 134, 80, fill=FLDBG, stroke=FIELD, sw=1.8, rx=10))
    p.append(text(667, 126, "пристрій", size=11, color=FIELD, bold=True))
    p.append(text(667, 152, "4.2 В", size=16, color=POS, bold=True))

    # формульна рамка
    p.append(rect(110, 224, 540, 104, fill=GREY, stroke=MUTED, sw=1.5, rx=12))
    p.append(text(380, 250, "ΔV = I × R   (закон Ома)", size=12.5, bold=True))
    p.append(text(380, 278, "тонкий/довгий шнур при 3 А: ΔV ≈ 0.8 В → на пристрої 4.2 В (заряд гальмує)", size=10.5))
    p.append(text(380, 300, "та сама потужність вищою напругою (PD 9 В): струм менший → і падіння менше", size=10.5))
    p.append(text(380, 320, "ось чому PD воліє підняти напругу, а не струм", size=10.5, color=FIELD, bold=True))

    # нижня смужка
    p.append(rect(60, 348, 640, 36, fill=GOLDBG, stroke=GOLD, sw=1.4, rx=8))
    p.append(mtext(380, 366,
                   ["Половину «не заряджає» в полі дає саме падіння на дешевому тонкому шнурі —",
                    "повний розрахунок є в 🧮-вставці про падіння на кабелі"],
                   size=9.5, color=INK, lh=1.4))

    render(os.path.join(OUT, "drop.svg"), W, H, *p,
           title="Падіння на дроті: 5 В виходять, 4.2 В доходять")


# ── incompat: карта типових несумісностей ─────────────────────────────────────
# Ідея: причин «не заряджає» скінченно, і всі вони лягають у три домени —
# кабель, зарядний, переговори. Шість карток сходяться в один центр.

def fig_incompat():
    W, H = 760, 470
    cx, cyc = 380, 250
    p = []
    cards = [
        (60,  92,  GOLD, "«тільки заряд» шнур", ["нема ліній даних/CC →", "нема переговорів"]),
        (300, 78,  FIELD, "кабель на 3 А", ["нема e-marker →", "стеля 3 А, EPR зась"]),
        (540, 92,  POS,  "тонкий / довгий", ["падіння напруги →", "заряд гальмує"]),
        (60,  330, NEG,  "кривий A→C", ["невірний 56 кОм →", "невпізнання струму"]),
        (300, 344, GOLD, "джерело без профілю", ["нема твоєї напруги →", "відкат у 5 В"]),
        (540, 330, NEG,  "чужий фірмовий код", ["BC1.2 не збігся →", "відкат у 0.5 А"]),
    ]
    # лінії-спиці спершу (під картками)
    for x, y, col, head, body in cards:
        p.append(line(x + 80, y + 35, cx, cyc, color="#e4e4e4", sw=1.4))
    # центр
    p.append(rect(cx - 85, cyc - 30, 170, 60, fill=POSBG, stroke=POS, sw=2, rx=12))
    p.append(text(cx, cyc - 4, "не заряджає", size=12.5, color=POS, bold=True))
    p.append(text(cx, cyc + 16, "або повільно", size=10.5))
    # картки зверху
    for x, y, col, head, body in cards:
        p.append(rect(x, y, 160, 72, fill=BG, stroke=col, sw=1.8, rx=10))
        p.append(text(x + 80, y + 22, head, size=10.5, color=col, bold=True))
        p.append(text(x + 80, y + 41, body[0], size=9))
        p.append(text(x + 80, y + 57, body[1], size=9))

    p.append(rect(60, 430, 640, 28, fill=FLDBG, stroke=FIELD, sw=1.4, rx=8))
    p.append(text(380, 448,
                  "Причина майже завжди в одному з трьох доменів: кабель, зарядний або переговори",
                  size=10))

    render(os.path.join(OUT, "incompat.svg"), W, H, *p,
           title="Чому «не заряджає»: карта типових несумісностей")


# ── diagnosis: дерево перевірок ───────────────────────────────────────────────
# Ідея: невиразну скаргу перетворюємо на впорядковану перевірку. Ключ — виміряти
# VBUS на пристрої під навантаженням: одне число ділить «кабель» від «переговорів».

def fig_diagnosis():
    W, H = 760, 560
    cx = 300
    p = []

    def diamond(cx, cy, hw, hh, stroke):
        pts = "%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" % (
            cx, cy - hh, cx + hw, cy, cx, cy + hh, cx - hw, cy)
        return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (pts, BG, stroke)

    # скарга
    p.append(rect(cx - 130, 50, 260, 38, fill=POSBG, stroke=POS, sw=2, rx=8))
    p.append(text(cx, 74, "Скарга: не заряджає / повільно", size=11, color=POS, bold=True))
    p.append(arrow(cx, 88, cx, 108, color=INK, sw=2))
    # ромб 1
    p.append(diamond(cx, 150, 115, 35, NEG))
    p.append(text(cx, 154, "Заряджає взагалі?", size=10.5, bold=True))
    p.append(arrow(cx - 115, 150, cx - 148, 150, color=MUTED, sw=2))
    p.append(text(cx - 150, 140, "ні", size=9.5, color=MUTED, bold=True, anchor="end"))
    p.append(rect(30, 128, 150, 46, fill=BG, stroke=MUTED, sw=1.8, rx=8))
    p.append(text(105, 148, "контакт / цілість", size=9.5, bold=True))
    p.append(text(105, 164, "кабелю, роз'єм", size=9))
    p.append(arrow(cx, 185, cx, 208, color=INK, sw=2))
    p.append(text(cx + 14, 204, "так, але мляво", size=9, anchor="start"))
    # вимір VBUS
    p.append(rect(cx - 130, 208, 260, 44, fill=NEGBG, stroke=NEG, sw=2, rx=8))
    p.append(text(cx, 228, "ВИМІРЯЙ VBUS на пристрої", size=10.5, color=NEG, bold=True))
    p.append(text(cx, 244, "під навантаженням", size=9))
    p.append(arrow(cx, 252, cx, 278, color=INK, sw=2))
    # ромб 2 — просідає?
    p.append(diamond(cx, 318, 120, 38, GOLD))
    p.append(text(cx, 322, "VBUS просідає?", size=10.5, bold=True))
    p.append(arrow(cx + 120, 318, 560, 318, color=GOLD, sw=2))
    p.append(text(440, 308, "так", size=9.5, color=GOLD, bold=True))
    p.append(rect(560, 294, 180, 50, fill=GOLDBG, stroke=GOLD, sw=2, rx=8))
    p.append(text(650, 314, "падіння на кабелі", size=10, color=GOLD, bold=True))
    p.append(text(650, 332, "→ товщий/коротший шнур", size=9))
    p.append(arrow(cx, 356, cx, 382, color=INK, sw=2))
    p.append(text(cx + 14, 378, "ні (тримає, та струм малий)", size=9, anchor="start"))
    # ромб 3 — переговори?
    p.append(diamond(cx, 422, 120, 39, FIELD))
    p.append(text(cx, 418, "Переговори вдались?", size=10, bold=True))
    p.append(text(cx, 434, "CC / PD / BC1.2", size=9))
    p.append(arrow(cx + 120, 422, 560, 422, color=FIELD, sw=2))
    p.append(text(440, 412, "ні", size=9.5, color=FIELD, bold=True))
    p.append(rect(560, 398, 180, 50, fill=FLDBG, stroke=FIELD, sw=2, rx=8))
    p.append(text(650, 416, "кабель без ліній / e-marker", size=9, color=FIELD, bold=True))
    p.append(text(650, 434, "чи джерело без профілю", size=9))
    p.append(arrow(cx, 461, cx, 484, color=INK, sw=2))
    p.append(text(cx + 14, 480, "так", size=9, color=FIELD, bold=True, anchor="start"))
    # стеля
    p.append(rect(cx - 130, 484, 260, 44, fill=GREY, stroke=MUTED, sw=1.8, rx=8))
    p.append(text(cx, 504, "усе гаразд — це стеля", size=10, bold=True))
    p.append(text(cx, 520, "цього блока/кабелю", size=9))

    p.append(rect(50, 534, 660, 18, fill=FLDBG, stroke=FIELD, sw=1.4, rx=8))
    p.append(text(380, 547,
                  "Не «магія», а перевірки по черзі: контакт → виміряй VBUS → просідання (кабель) → переговори",
                  size=10))

    render(os.path.join(OUT, "diagnosis.svg"), W, H, *p,
           title="Діагностика «не заряджає» як інженерна задача")


# ── fieldrobust: п'ять звичок ─────────────────────────────────────────────────
# Ідея: кожна звичка б'є по конкретній пастці поля, разом дають пристрій,
# що «прощає» користувачеві випадкове залізо.

def fig_fieldrobust():
    W, H = 760, 400
    p = []
    cards = [
        (FIELD, "Приймай діапазон", ["широкий вхід —", "будь-який профіль"]),
        (NEG,   "Не вимагай максимум", ["не проси 5 А/EPR", "без потреби"]),
        (GOLD,  "Міряй VBUS у себе", ["напругу на пристрої", "під навантаженням"]),
        (POS,   "Терпи просадку", ["низький поріг", "brownout, не падай"]),
        ("#8e44ad", "Кажи користувачу", ["«мляво — інший", "шнур чи блок»"]),
    ]
    x = 50
    w = 134
    gap = 4
    for col, head, body in cards:
        p.append(rect(x, 64, w, 200, fill=BG, stroke=col, sw=1.9, rx=12))
        p.append(mtext(x + w / 2, 92, head.split(" ", 1) if len(head) > 15 else [head],
                       size=10.5, color=col, bold=True))
        p.append(line(x + 10, 112, x + w - 10, 112, color="#e4e4e4", sw=1))
        p.append(text(x + w / 2, 140, body[0], size=9))
        p.append(text(x + w / 2, 158, body[1], size=9))
        p.append(text(x + w / 2, 232, "✓", size=18, color=col, bold=True))
        x += w + gap

    p.append(rect(50, 300, 660, 50, fill=FLDBG, stroke=FIELD, sw=1.5, rx=8))
    p.append(mtext(380, 322,
                   ["Поле непередбачуване: випадковий шнур, випадковий блок, бруд у роз'ємі. Надійний пристрій",
                    "не вимагає ідеалу — приймає, що дають, чесно міряє, що дійшло, терпить просадку, говорить із людиною."],
                   size=10, color=INK, lh=1.4))

    render(os.path.join(OUT, "fieldrobust.svg"), W, H, *p,
           title="Проєктувати під поле: п'ять звичок")


# ── cable-model: дві жили — туди й назад (🧮-вставка) ─────────────────────────
# Ідея: струм робить ПОВНУ петлю — по VBUS до пристрою й по GND назад, тож
# опір кабелю подвоєний; саме на ньому й падає ΔV, якого пристрій не побачить.

def fig_cable_model():
    W, H = 720, 380
    p = []
    p.append(rect(60, 116, 124, 116, fill=POSBG, stroke=POS, sw=1.8, rx=10))
    p.append(text(122, 152, "джерело", size=11, color=POS, bold=True))
    p.append(text(122, 182, "5.0 В", size=16, color=POS, bold=True))
    p.append(rect(536, 116, 124, 116, fill=FLDBG, stroke=FIELD, sw=1.8, rx=10))
    p.append(text(598, 152, "пристрій", size=11, color=FIELD, bold=True))
    p.append(text(598, 180, "Vпр", size=14, bold=True))
    p.append(text(598, 202, "= 5 − ΔV", size=11))
    # жила «туди» (VBUS)
    p.append(line(184, 142, 320, 142, color=GOLD, sw=3))
    p.append(rect(320, 125, 70, 34, fill=BG, stroke=GOLD, sw=1.8, rx=4))
    p.append(text(355, 146, "Rжили", size=10.5, color=GOLD, bold=True))
    p.append(line(390, 142, 536, 142, color=GOLD, sw=3))
    p.append(arrow(228, 142, 288, 142, color=POS, sw=2))
    p.append(text(258, 134, "I →", size=9.5, color=POS, bold=True))
    p.append(text(355, 114, "VBUS (туди)", size=9.5))
    # жила «назад» (GND)
    p.append(line(184, 206, 320, 206, color=INK, sw=3))
    p.append(rect(320, 189, 70, 34, fill=BG, stroke=INK, sw=1.8, rx=4))
    p.append(text(355, 210, "Rжили", size=10.5, bold=True))
    p.append(line(390, 206, 536, 206, color=INK, sw=3))
    p.append(arrow(452, 206, 392, 206, color=POS, sw=2))
    p.append(text(422, 224, "← I", size=9.5, color=POS, bold=True))
    p.append(text(355, 240, "GND (назад)", size=9.5))
    # формула
    p.append(rect(130, 290, 460, 66, fill=GREY, stroke=MUTED, sw=1.5, rx=10))
    p.append(text(360, 314, "Rкаб = 2 · (L · ρ) + Rконтактів      ΔV = I · Rкаб", size=13, bold=True))
    p.append(text(360, 338, "струм біжить туди по VBUS і назад по GND — тому опір ПОДВІЙНИЙ", size=10.5))

    render(os.path.join(OUT, "cable-model.svg"), W, H, *p,
           title="Модель падіння на кабелі: дві жили — туди й назад")


# ── awg-table: опір за калібром і падіння при 3 А (🧮-вставка) ────────────────
# Ідея: погонний опір різко росте, коли жила тоншає; за того самого струму 3 А
# падіння на тонкому шнурі стає катастрофічним, а вища напруга його рятує.

def fig_awg_table():
    W, H = 740, 420
    p = []
    # таблиця ліворуч
    p.append(rect(50, 64, 320, 300, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    p.append(text(210, 90, "Опір мідної жили", size=12, bold=True))
    p.append(rect(70, 104, 280, 28, fill=NEGBG, stroke=NEG, sw=1.2, rx=5))
    p.append(text(120, 123, "AWG", size=11, color=NEG, bold=True))
    p.append(text(250, 123, "Ω на метр", size=11, color=NEG, bold=True))
    data = [("20", "0.033"), ("22", "0.053"), ("24", "0.084"),
            ("26", "0.133"), ("28", "0.213"), ("30", "0.339")]
    ry = 132
    for i, (awg, ohm) in enumerate(data):
        bg = BG if i % 2 == 0 else GREY
        p.append(rect(70, ry, 280, 34, fill=bg, stroke="#e4e4e4", sw=1, rx=0))
        p.append(text(120, ry + 22, awg, size=11.5, bold=True))
        p.append(text(250, ry + 22, ohm, size=11.5))
        ry += 34
    p.append(text(210, 356, "більший номер AWG = тонша жила = більший опір", size=9, color=MUTED))

    # стовпчики праворуч
    p.append(text(560, 90, "ΔV при I = 3 А, 1 м (+ ~0.1 Ω контакти)", size=10.5, bold=True))
    base = 300
    p.append(line(450, base, 720, base, color=INK, sw=1.5))
    p.append(line(450, base, 450, 110, color=INK, sw=1.5))
    p.append(text(444, 122, "ΔV, В", size=9.5, anchor="end"))
    bars = [(490, 0.8, FIELD, "24 AWG"), (590, 1.6, GOLD, "28 AWG"), (660, 2.3, POS, "30 AWG")]
    for bx, dv, col, lab in bars:
        bh = dv * 68
        p.append(rect(bx, base - bh, 56, bh, fill=col, stroke=col, sw=2, rx=4))
        p.append('<rect x="%.0f" y="%.0f" width="56" height="%.0f" rx="4" fill="%s" fill-opacity="0.18"/>'
                 % (bx, base - bh, bh, col))
        p.append(text(bx + 28, base - bh - 8, "%.1f В" % dv, size=11, color=col, bold=True))
        p.append(text(bx + 28, base + 18, lab, size=10))

    p.append(rect(450, 344, 270, 50, fill=FLDBG, stroke=FIELD, sw=1.4, rx=8))
    p.append(text(585, 364, "Та сама потужність 15 Вт вищою напругою:", size=9.5, color=FIELD, bold=True))
    p.append(text(585, 382, "9 В × 1.67 А на 28 AWG → ΔV ≈ 0.9 В замість 1.6 В", size=9.5))

    render(os.path.join(OUT, "awg-table.svg"), W, H, *p,
           title="Опір за калібром і падіння при 3 А (кабель 1 м)")


if __name__ == "__main__":
    fig_cable()
    fig_emarker()
    fig_drop()
    fig_incompat()
    fig_diagnosis()
    fig_fieldrobust()
    fig_cable_model()
    fig_awg_table()
    print("OK: figures written to", OUT)
