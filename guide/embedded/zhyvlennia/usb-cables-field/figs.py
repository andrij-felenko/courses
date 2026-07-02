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

# ═══════════════════════════════════════════════════════════════════════════════
# ФІГУРИ ДЛЯ ДЕТАЛЬНОЇ ВЕРСІЇ (глибше за базову — механіка, а не оглядка)
# ═══════════════════════════════════════════════════════════════════════════════

# ── sop-handshake: як джерело окремо опитує кабель (SOP') ──────────────────────
# Ідея (глибша за базову «e-marker дозволяє більше»): у переговорах три учасники,
# і джерело говорить із кабелем ОКРЕМИМ каналом SOP', перш ніж дати струм пристрою.

def fig_sop_handshake():
    W, H = 780, 470
    p = []
    # три учасники
    p.append(rect(40, 150, 150, 96, fill=POSBG, stroke=POS, sw=1.9, rx=12))
    p.append(text(115, 180, "Джерело", size=12.5, color=POS, bold=True))
    p.append(text(115, 202, "(зарядка)", size=9.5, color=MUTED))
    p.append(text(115, 226, "DFP · Rp", size=10, bold=True))

    p.append(rect(315, 150, 150, 96, fill=NEGBG, stroke=NEG, sw=1.9, rx=12))
    p.append(text(390, 178, "e-marker", size=12.5, color=NEG, bold=True))
    p.append(text(390, 198, "у штекері", size=9.5, color=MUTED))
    p.append(text(390, 222, "живлений VCONN", size=9, bold=True))

    p.append(rect(590, 150, 150, 96, fill=FLDBG, stroke=FIELD, sw=1.9, rx=12))
    p.append(text(665, 180, "Пристрій", size=12.5, color=FIELD, bold=True))
    p.append(text(665, 202, "(споживач)", size=9.5, color=MUTED))
    p.append(text(665, 226, "UFP · Rd", size=10, bold=True))

    # SOP' — джерело ↔ кабель
    p.append(arrow(190, 176, 315, 176, color=NEG, sw=2))
    p.append(text(252, 168, "SOP'  «хто ти?»", size=9.5, color=NEG, bold=True))
    p.append(arrow(315, 200, 190, 200, color=NEG, sw=2))
    p.append(text(252, 216, "паспорт: 5 А, 20 В", size=9, color=NEG))

    # SOP — джерело ↔ пристрій (крізь кабель)
    p.append(line(190, 240, 590, 240, color=POS, sw=2, dash="6 4"))
    p.append(text(390, 260, "SOP  «скільки дати?» — переговори PD джерела з пристроєм", size=9.5, color=POS))

    # порядок кроків згори
    steps = [
        "1. Пристрій під'єднано → джерело бачить Rd, вмикає VCONN.",
        "2. SOP' до КАБЕЛЯ: джерело питає e-marker його межі (струм, напруга, швидкість).",
        "3. Лише тепер джерело знає стелю КАБЕЛЯ — і в SOP-переговорах не пропонує над неї.",
        "4. Немає відповіді по SOP' → кабель «німий» → джерело тримає безпечні 3 А, EPR зась.",
    ]
    sy = 66
    for i, s in enumerate(steps):
        col = NEG if i in (1, 3) else INK
        p.append(text(56, sy, s, size=10.5, anchor="start", color=col,
                      bold=(i == 3)))
        sy += 24

    p.append(rect(40, 300, 700, 30, fill=GREY, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(390, 319,
                  "Ключ: кабель — окремий співрозмовник (SOP'), а не пасивний дріт. Його межі джерело дізнається ДО того, як дати струм.",
                  size=10))

    # три канали SOP
    p.append(rect(40, 346, 700, 96, fill=BG, stroke=MUTED, sw=1.4, rx=10))
    p.append(text(390, 370, "Три адреси на одній лінії CC", size=11.5, bold=True))
    chans = [
        (170, "SOP", "джерело ↔ пристрій", POS),
        (390, "SOP'", "джерело ↔ ближній e-marker", NEG),
        (620, "SOP″", "джерело ↔ дальній e-marker", MUTED),
    ]
    for cx2, h, sub, col in chans:
        p.append(text(cx2, 398, h, size=13, color=col, bold=True))
        p.append(text(cx2, 420, sub, size=9.5))

    render(os.path.join(OUT, "sop-handshake.svg"), W, H, *p,
           title="Переговори втрьох: джерело окремо опитує кабель (SOP')")


# ── power-loss: тепло в міді росте як I², і саме це — межа кабелю ──────────────
# Ідея (глибша за базову ΔV): у дроті гріється P = I²·R, тож удвічі більший струм —
# ВЧЕТВЕРО більше тепла. Ось фізична причина стелі 3/5 А і виграшу високої напруги.

def fig_power_loss():
    W, H = 760, 430
    p = []
    p.append(text(380, 56, "Втрата в кабелі P = I²·R (та сама потужність 60 Вт, R = 0.3 Ω)",
                  size=12.5, bold=True))

    # стовпчики: 60 Вт трьома способами
    base_y = 300
    axis_x = 120
    p.append(line(axis_x, base_y, 700, base_y, color=INK, sw=1.5))
    p.append(line(axis_x, base_y, axis_x, 90, color=INK, sw=1.5))
    p.append(text(axis_x - 8, 100, "втрата", size=9.5, anchor="end"))
    p.append(text(axis_x - 8, 114, "у міді", size=9.5, anchor="end"))

    # P_loss = I^2 R; I = 60/V
    cases = [
        (5,  "5 В", 12.0, POS),
        (9,  "9 В", 6.67, GOLD),
        (20, "20 В", 3.0, FIELD),
    ]
    xx = 220
    for V, lab, I, col in cases:
        Ploss = I * I * 0.3
        bh = Ploss * 5.0     # 43.2 Вт → 216 px
        p.append(rect(xx, base_y - bh, 90, bh, fill=col, stroke=col, sw=2, rx=4))
        p.append('<rect x="%.0f" y="%.0f" width="90" height="%.0f" rx="4" fill="%s" fill-opacity="0.18"/>'
                 % (xx, base_y - bh, bh, col))
        p.append(text(xx + 45, base_y - bh - 24, "%.1f Вт" % Ploss, size=12, color=col, bold=True))
        p.append(text(xx + 45, base_y - bh - 8, "у тепло", size=8.5, color=MUTED))
        p.append(text(xx + 45, base_y + 18, lab, size=11, bold=True))
        p.append(text(xx + 45, base_y + 36, "I = %.1f А" % I, size=9.5, color=col))
        xx += 160

    # висновок-рамка
    p.append(rect(60, 336, 640, 78, fill=GREY, stroke=MUTED, sw=1.5, rx=10))
    p.append(text(380, 360, "Струм у чотири рази менший → тепло в ШІСТНАДЦЯТЬ разів менше (P ∝ I²)",
                  size=11, bold=True))
    p.append(text(380, 384, "Тонка жила має малу поверхню й швидко перегрівається — тому стеля кабелю задана саме СТРУМОМ (3 чи 5 А),",
                  size=9.5))
    p.append(text(380, 402, "а не потужністю. Підняти напругу — єдиний спосіб дати більше ват тим самим дротом, не спаливши його.",
                  size=9.5))

    render(os.path.join(OUT, "power-loss.svg"), W, H, *p,
           title="Чому стеля кабелю — це струм: тепло росте як квадрат струму")


# ── ac2c-topology: правильний перехідник проти смертельного ────────────────────
# Ідея (глибша за базову згадку «кривий 56 кОм»): показати ТОПОЛОГІЮ — де саме
# сидить Rp=56k, що робить пристрій, і як зсув GND↔VBUS убиває залізо (кейс 2016).

def fig_ac2c():
    W, H = 780, 470
    p = []
    # ── ліва половина: правильний ─────────────────────────────
    p.append(rect(40, 60, 340, 176, fill=FLDBG, stroke=FIELD, sw=1.8, rx=12))
    p.append(text(210, 86, "Правильний A→C перехідник", size=12, color=FIELD, bold=True))
    # A-порт
    p.append(rect(60, 108, 70, 96, fill=BG, stroke=INK, sw=1.6, rx=6))
    p.append(text(95, 100, "USB-A", size=9, bold=True))
    p.append(text(95, 130, "VBUS 5 В", size=8.5, color=POS))
    p.append(text(95, 160, "D+ D−", size=8.5))
    p.append(text(95, 190, "GND", size=8.5, color=NEG))
    # C-штекер
    p.append(rect(290, 108, 70, 96, fill=BG, stroke=INK, sw=1.6, rx=6))
    p.append(text(325, 100, "USB-C", size=9, bold=True))
    p.append(text(325, 130, "VBUS", size=8.5, color=POS))
    p.append(text(325, 160, "CC", size=8.5, color=GOLD, bold=True))
    p.append(text(325, 190, "GND", size=8.5, color=NEG))
    # прямі лінії
    p.append(line(130, 128, 290, 128, color=POS, sw=2))
    p.append(line(130, 190, 290, 190, color=NEG, sw=2))
    # резистор 56k від VBUS до CC
    p.append(line(200, 128, 200, 158, color=GOLD, sw=2))
    p.append(rect(176, 156, 48, 18, fill=BG, stroke=GOLD, sw=1.6, rx=3))
    p.append(text(200, 169, "56 кΩ", size=9, color=GOLD, bold=True))
    p.append(line(200, 174, 200, 158, color=GOLD, sw=2))
    p.append(line(200, 174, 290, 160, color=GOLD, sw=2))
    p.append(text(210, 220, "CC бачить 56 кΩ → «це кволий A-порт, тягни ≤ 500 мА/900 мА»",
                  size=8.5, anchor="middle", color=FIELD))

    # ── права половина: смертельний ───────────────────────────
    p.append(rect(400, 60, 340, 176, fill=POSBG, stroke=POS, sw=1.8, rx=12))
    p.append(text(570, 86, "Смертельний брак (кейс 2016)", size=12, color=POS, bold=True))
    p.append(rect(420, 108, 70, 96, fill=BG, stroke=INK, sw=1.6, rx=6))
    p.append(text(455, 100, "USB-A", size=9, bold=True))
    p.append(text(455, 130, "VBUS 5 В", size=8.5, color=POS))
    p.append(text(455, 190, "GND", size=8.5, color=NEG))
    p.append(rect(650, 108, 70, 96, fill=BG, stroke=INK, sw=1.6, rx=6))
    p.append(text(685, 100, "USB-C", size=9, bold=True))
    p.append(text(685, 130, "VBUS", size=8.5, color=POS))
    p.append(text(685, 190, "GND", size=8.5, color=NEG))
    # ПЕРЕХРЕЩЕНІ лінії: VBUS_A → GND_C, GND_A → VBUS_C
    p.append(line(490, 128, 650, 190, color=POS, sw=2.4))
    p.append(line(490, 190, 650, 128, color=NEG, sw=2.4))
    p.append(text(570, 150, "✕", size=22, color=POS, bold=True))
    p.append(text(570, 220, "GND↔VBUS переставлено + 10 кΩ замість 56 кΩ",
                  size=8.5, anchor="middle", color=POS, bold=True))

    # наслідки
    p.append(rect(40, 252, 700, 74, fill=GREY, stroke=MUTED, sw=1.5, rx=10))
    p.append(text(380, 276, "Що сталося: живлення подано в лінію землі пристрою — миттєвий зустрічний струм.",
                  size=10.5, bold=True))
    p.append(text(380, 298, "10 кΩ у плечі CC ще й брехав, що джерело дає 3 А, тож пристрій пробував тягнути втричі більше з кволого A-порту.",
                  size=9.5))
    p.append(text(380, 316, "Підсумок: згоріли обидва USB-порти ноутбука, вбудований контролер і два PD-аналізатори тестувальника.",
                  size=9.5, color=POS, bold=True))

    # правило
    p.append(rect(40, 336, 700, 108, fill=FLDBG, stroke=FIELD, sw=1.5, rx=10))
    p.append(text(380, 360, "Урок для власного пристрою", size=11.5, color=FIELD, bold=True))
    rules = [
        "• CC-логіку (Rp від джерела, Rd у пристрої) довіряй мікросхемі-контролеру, не «двом резисторам навмання».",
        "• Не подавай VBUS, поки CC не підтвердив коректну орієнтацію й роль — це відсікає перевернуті/биті перехідники.",
        "• Захист від зворотної полярності на вході робить із «згорів» усього лиш «не заряджає».",
    ]
    ry = 384
    for r in rules:
        p.append(text(60, ry, r, size=9.5, anchor="start"))
        ry += 22

    render(os.path.join(OUT, "ac2c.svg"), W, H, *p,
           title="A→C перехідник: правильний резистор проти смертельного")


# ── margin: чому «раз із трьох» — це робота на межі ────────────────────────────
# Ідея (глибша за базову згадку про переривчасте): показати робочу точку відносно
# порога brownout і як ДРЕЙФ струму/контакту перекидає систему через край.

def fig_margin():
    W, H = 760, 440
    p = []
    left, right = 90, 700
    top, bot = 80, 300
    # осі
    p.append(line(left, bot, right, bot, color=INK, sw=1.5))
    p.append(line(left, bot, left, top, color=INK, sw=1.5))
    p.append(text(left - 8, top + 6, "VBUS на", size=9.5, anchor="end"))
    p.append(text(left - 8, top + 20, "пристрої", size=9.5, anchor="end"))
    p.append(text(right, bot + 18, "час / струм заряду →", size=9.5, anchor="end"))

    # поріг brownout
    thr_y = bot - 90
    p.append(line(left, thr_y, right, thr_y, color=POS, sw=1.8, dash="7 4"))
    p.append(text(right - 4, thr_y - 6, "поріг brownout (напр. 3.4 В)", size=9.5,
                  color=POS, anchor="end", bold=True))

    # зона «мертво» під порогом
    p.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" fill-opacity="0.10"/>'
             % (left, thr_y, right - left, bot - thr_y, POS))
    p.append(text((left + right) / 2, bot - 20, "нижче порога — пристрій падає / скидає заряд",
                  size=9.5, color=POS))

    # хитка крива VBUS, що танцює навколо порога (кусково-лінійна)
    import math
    pts = []
    n = 60
    for i in range(n + 1):
        x = left + (right - left) * i / n
        t = i / n
        # середнє трохи вище порога, амплітуда коливань перекидає через край
        v = thr_y - 26 - 30 * math.sin(t * 9) - 18 * math.sin(t * 23 + 1)
        pts.append((x, v))
    path = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % pq for pq in pts[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path, GOLD))
    # позначити точки падіння (де крива нижче порога)
    for x, v in pts:
        if v > thr_y:
            p.append(circle(x, thr_y, 3.2, fill=POS, stroke=POS, sw=1))
    p.append(text(left + 8, top + 40, "VBUS «на межі» — то вище, то нижче порога", size=9.5,
                  color=GOLD, anchor="start", bold=True))
    p.append(text(left + 8, top + 56, "червоні точки = моменти «не зарядилось»", size=8.5,
                  color=POS, anchor="start"))

    # пояснення знизу
    p.append(rect(60, 322, 640, 108, fill=GREY, stroke=MUTED, sw=1.5, rx=10))
    p.append(text(380, 346, "«Раз із трьох» = система стоїть упритул до порога, а вхід сам по собі гуляє:",
                  size=10.5, bold=True))
    causes = [
        "• струм заряду міняється сам (батарея бере то більше, то менше) → падіння ΔV=I·R гуляє разом із ним;",
        "• роз'єм нагрівся чи ворухнувся → опір контакту стрибнув → ще одне випадкове падіння;",
        "• лік — не «знайти винного», а ВІДСУНУТИ від краю: товщий шнур, чистий роз'єм, нижчий поріг brownout.",
    ]
    cy2 = 368
    for c in causes:
        p.append(text(80, cy2, c, size=9.5, anchor="start"))
        cy2 += 21

    render(os.path.join(OUT, "margin.svg"), W, H, *p,
           title="Переривчасте «раз із трьох» — це робота впритул до порога")


# ── proj: конвеєр модуля польової діагностики ─────────────────────────────────
# Ідея: сирі відліки АЦП зліва протікають крізь усереднення → оцінку струму →
# класифікацію матрицею → гістерезис/дебаунс → назовні діагноз + дія + слово.

def fig_pipeline():
    W, H = 780, 430
    p = []
    # чотири вхідні джерела
    p.append(rect(40, 60, 150, 48, fill=POSBG, stroke=POS, sw=1.7, rx=9))
    p.append(text(115, 80, "АЦП VBUS", size=10.5, color=POS, bold=True))
    p.append(text(115, 97, "сирий, шумний", size=9, color=MUTED))
    p.append(rect(40, 124, 150, 48, fill=NEGBG, stroke=NEG, sw=1.7, rx=9))
    p.append(text(115, 144, "АЦП струму", size=10.5, color=NEG, bold=True))
    p.append(text(115, 161, "шунт / зарядник", size=9, color=MUTED))

    # стадія 1 — усереднення
    p.append(rect(230, 80, 132, 92, fill=GREY, stroke=MUTED, sw=1.6, rx=10))
    p.append(text(296, 104, "усереднення", size=10.5, bold=True))
    p.append(text(296, 122, "N відліків", size=9))
    p.append(text(296, 138, "тільки ПІД", size=9, color=FIELD, bold=True))
    p.append(text(296, 154, "навантаженням", size=9, color=FIELD, bold=True))

    # стадія 2 — класифікація
    p.append(rect(402, 80, 148, 92, fill=GOLDBG, stroke=GOLD, sw=1.7, rx=10))
    p.append(text(476, 104, "класифікація", size=10.5, color=GOLD, bold=True))
    p.append(text(476, 124, "матриця", size=9.5))
    p.append(text(476, 140, "напруга × струм", size=9.5))
    p.append(text(476, 158, "→ діагноз", size=9, color=GOLD, bold=True))

    # стадія 3 — дебаунс/гістерезис
    p.append(rect(590, 80, 150, 92, fill=FLDBG, stroke=FIELD, sw=1.7, rx=10))
    p.append(text(665, 104, "дебаунс +", size=10.5, color=FIELD, bold=True))
    p.append(text(665, 121, "гістерезис", size=10.5, color=FIELD, bold=True))
    p.append(text(665, 141, "стійкий стан", size=9))
    p.append(text(665, 157, "без дрижання", size=9, color=MUTED))

    # стрілки потоку
    p.append(arrow(190, 100, 228, 110, color=INK, sw=2))
    p.append(arrow(190, 148, 228, 138, color=INK, sw=2))
    p.append(arrow(362, 126, 400, 126, color=INK, sw=2))
    p.append(arrow(550, 126, 588, 126, color=INK, sw=2))

    # три виходи
    outs = [
        (POS,  POSBG,  "діагноз", "PWR_CABLE_DROP…"),
        (NEG,  NEGBG,  "дія",     "стишити навантаження"),
        (FIELD, FLDBG, "слово",   "«спробуй інший шнур»"),
    ]
    ox = 90
    for col, bg, head, sub in outs:
        p.append(rect(ox, 232, 200, 52, fill=bg, stroke=col, sw=1.7, rx=10))
        p.append(text(ox + 100, 254, head, size=10.5, color=col, bold=True))
        p.append(text(ox + 100, 273, sub, size=9))
        p.append(arrow(665, 176, ox + 100, 230, color="#cfcfcf", sw=1.4))
        ox += 220

    # підпис-нитка
    p.append(rect(60, 320, 660, 88, fill=GREY, stroke=MUTED, sw=1.5, rx=10))
    p.append(text(390, 344, "Одна структура стану, один виклик на цикл, три відповіді назовні",
                  size=11, bold=True))
    notes = [
        "• міряй ПІД навантаженням: без струму падіння ΔV = I·R = 0, і найгірший кабель бреше «5 В»;",
        "• усереднюй АЦП: сирий відлік стрибає на десятки мВ, а поріг просадки — теж десятки мВ;",
        "• класифікуй матрицею, тоді дебаунс: діагноз має вистоятися, перш ніж діяти чи говорити.",
    ]
    ny = 366
    for n in notes:
        p.append(text(80, ny, n, size=9.5, anchor="start"))
        ny += 21

    render(os.path.join(OUT, "diag-pipeline.svg"), W, H, *p,
           title="Модуль польової діагностики: від сирого АЦП до чесного слова")


# ── proj: КОЛИ міряти — вікно під навантаженням ───────────────────────────────
# Ідея: вимір має влучити у стале навантаження. Не на холостому (падіння=0),
# не одразу після стрибка струму (перехідник), а у вікні, коли струм устоявся.

def fig_when_measure():
    W, H = 780, 440
    p = []
    left, right = 90, 720
    top, bot = 70, 250
    midv = 150   # рівень «під навантаженням»

    # осі
    p.append(line(left, bot, right, bot, color=INK, sw=1.6))       # час
    p.append(line(left, top, left, bot, color=INK, sw=1.6))        # струм/напруга
    p.append(text(left - 8, top + 4, "I", size=11, anchor="end", bold=True))
    p.append(text(right, bot + 18, "час →", size=10, anchor="end", color=MUTED))

    # профіль струму: холостий → різкий фронт → перехідник (дзвін) → стале
    import math
    pts = []
    n = 120
    for i in range(n + 1):
        t = i / n
        x = left + (right - left) * t
        if t < 0.20:
            y = bot - 6                                   # холостий: майже нуль
        elif t < 0.34:
            y = bot - 6 - (bot - 6 - (midv)) * (t - 0.20) / 0.14  # фронт угору
        elif t < 0.55:
            # перехідник: згасаючий дзвін навколо рівня
            y = midv - 26 * math.exp(-(t - 0.34) * 16) * math.cos((t - 0.34) * 60)
        else:
            y = midv                                      # стале навантаження
        pts.append((x, y))
    path = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % pq for pq in pts[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path, GOLD))

    # три зони
    x0 = left + (right - left) * 0.20
    x1 = left + (right - left) * 0.34
    x2 = left + (right - left) * 0.55
    # холоста
    p.append('<rect x="%.0f" y="%d" width="%.0f" height="%d" fill="%s" fill-opacity="0.08"/>'
             % (left, top, x0 - left, bot - top, NEG))
    p.append(text((left + x0) / 2, top + 20, "холостий хід", size=9.5, color=NEG, bold=True))
    p.append(text((left + x0) / 2, top + 36, "ΔV=0 → не міряти", size=8.5, color=NEG))
    # перехідник
    p.append('<rect x="%.0f" y="%d" width="%.0f" height="%d" fill="%s" fill-opacity="0.10"/>'
             % (x0, top, x2 - x0, bot - top, POS))
    p.append(text((x0 + x2) / 2, top + 20, "перехідник", size=9.5, color=POS, bold=True))
    p.append(text((x0 + x2) / 2, top + 36, "струм дзвенить → не міряти", size=8.5, color=POS))
    # стале — вікно виміру
    p.append('<rect x="%.0f" y="%d" width="%.0f" height="%d" fill="%s" fill-opacity="0.12"/>'
             % (x2, top, right - x2, bot - top, FIELD))
    p.append(text((x2 + right) / 2, top + 20, "СТАЛЕ навантаження", size=10, color=FIELD, bold=True))
    p.append(text((x2 + right) / 2, top + 36, "ось тут міряй і усереднюй", size=9, color=FIELD, bold=True))

    # рівень навантаження пунктиром
    p.append(line(x2, midv, right, midv, color=MUTED, sw=1.2, dash="4 4"))

    # стрілка «вікно виміру»
    wx0, wx1 = x2 + 30, right - 30
    p.append(line(wx0, bot + 30, wx1, bot + 30, color=FIELD, sw=2))
    p.append(line(wx0, bot + 25, wx0, bot + 35, color=FIELD, sw=2))
    p.append(line(wx1, bot + 25, wx1, bot + 35, color=FIELD, sw=2))
    p.append(text((wx0 + wx1) / 2, bot + 48, "вікно виміру: устоялось → N відліків → усереднити",
                  size=9.5, color=FIELD, bold=True))

    # пояснення
    p.append(rect(60, bot + 66, 660, 92, fill=GREY, stroke=MUTED, sw=1.5, rx=10))
    p.append(text(390, bot + 90, "Коли міряти VBUS — три правила з фізики падіння",
                  size=11, bold=True))
    rules = [
        "• тільки ПІД навантаженням — на холостому падіння нульове й діагноз завжди «все добре»;",
        "• зачекай, поки струм устоїться — одразу після ввімкнення він дзвенить, і вимір бреше;",
        "• усередни N відліків у вікні — один сирий відлік шумить сильніше за поріг рішення.",
    ]
    ry = bot + 112
    for r in rules:
        p.append(text(80, ry, r, size=9.5, anchor="start"))
        ry += 21

    render(os.path.join(OUT, "when-measure.svg"), W, H, *p,
           title="Коли міряти: влуч у стале навантаження, не в холостий і не в дзвін")


# ═══════════════════════════════════════════════════════════════════════════════
# ФІГУРА ДЛЯ ІСТОРИЧНОЇ ВСТАВКИ (📜 hist-cable-safety)
# ═══════════════════════════════════════════════════════════════════════════════

# ── hist-timeline: як полювали на биті кабелі (2015–2016) ──────────────────────
# Ідея: одна людина з мультиметром і акаунтом на Amazon зрушила цілу індустрію.
# Часова вісь від перших оглядів до кейсу зі спаленим ноутбуком і до заборони
# на майданчику — показуємо ланцюг «огляди → показова аварія → системна зміна».

def fig_hist_timeline():
    W, H = 780, 470
    p = []
    axis_y = 235
    x0, x1 = 70, 720
    p.append(line(x0, axis_y, x1 - 6, axis_y, color=INK, sw=2.2))
    p.append(arrow(x1 - 8, axis_y, x1 + 4, axis_y, color=INK, sw=2.2))

    # чотири віхи: (x, дата, заголовок, [рядки], колір, вгору/вниз)
    miles = [
        (150, "жовт. 2015", "Огляди на Amazon",
         ["Бенсон Люнґ починає", "тестувати кабелі USB-C;", "~30% провалюють спеку"], NEG, True),
        (335, "лют. 2016", "Спалений Pixel",
         ["кабель Surjtech A→C:", "GND↔VBUS переставлено,", "10 кΩ замість 56 кΩ"], POS, False),
        (520, "берез. 2016", "Amazon забороняє",
         ["майданчик знімає з", "продажу кабелі поза", "специфікацією USB-IF"], FIELD, True),
        (665, "серп. 2016", "Відкликання Anker",
         ["виробник відкликає", "й міняє биту серію", "PowerLine A8185011"], GOLD, False),
    ]
    for x, date, head, body, col, up in miles:
        p.append(circle(x, axis_y, 6, fill=col, stroke=col, sw=2))
        bx = min(max(x - 84, 8), W - 176)
        if up:
            p.append(line(x, axis_y - 6, x, axis_y - 30, color=col, sw=1.6))
            p.append(text(x, axis_y - 38, date, size=10, color=col, bold=True))
            by = axis_y - 132
        else:
            p.append(line(x, axis_y + 6, x, axis_y + 30, color=col, sw=1.6))
            p.append(text(x, axis_y + 54, date, size=10, color=col, bold=True))
            by = axis_y + 66
        p.append(rect(bx, by, 168, 84, fill=BG, stroke=col, sw=1.7, rx=10))
        p.append(text(bx + 84, by + 22, head, size=10.5, color=col, bold=True))
        p.append(line(bx + 14, by + 32, bx + 154, by + 32, color="#e4e4e4", sw=1))
        ty = by + 50
        for ln in body:
            p.append(text(bx + 84, ty, ln, size=8.5, color=INK if ty == by + 50 else MUTED))
            ty += 15

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Полювання на биті USB-C кабелі: 2015–2016")


if __name__ == "__main__":
    fig_cable()
    fig_emarker()
    fig_drop()
    fig_incompat()
    fig_diagnosis()
    fig_fieldrobust()
    fig_cable_model()
    fig_awg_table()
    # детальна версія
    fig_sop_handshake()
    fig_power_loss()
    fig_ac2c()
    fig_margin()
    # проєктна вставка
    fig_pipeline()
    fig_when_measure()
    # історична вставка
    fig_hist_timeline()
    print("OK: figures written to", OUT)
