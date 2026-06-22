# -*- coding: utf-8 -*-
"""Фігури теми «ESP32 проти 8-біт» (+ вставки hist-8051, math-benchmarks).
svgkit імпортуємо, не переписуємо (AUTHORING §5). Вивід — у ./img/, імена — slug.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_FILL = "#eafaf0"   # ESP32-бік
BLUE_FILL  = "#eaf0fd"   # 8-біт-бік
GOLD       = "#caa24a"
GOLD_FILL  = "#fff6e0"


# ── two-ends: два кінці шкали «обчислювальної ваги» ───────────────────────────
def fig_two_ends():
    W, H = 720, 330
    p = []
    axis_y = 196
    p.append(text(W / 2, 52, "«потужніший» не означає «кращий» — лише «правіше на шкалі»",
                  size=12, color=MUTED, italic=True))

    # шкала
    p.append(arrow(90, axis_y, W - 60, axis_y, color=INK, sw=2.2))
    p.append(text(W / 2, axis_y + 90, "обчислювальна вага →", size=12, color=INK, bold=True))

    # ліва картка — простий 8-біт
    p.append(fitbox(48, 86, 230, 80,
                    "Простий 8-біт\n1× 8-біт · 8–20 МГц\nкілобайти памʼяті\nбез радіо · копійки · мкВт",
                    size=11, fill=BLUE_FILL, stroke=NEG, sw=2, color=INK, bold=False))
    p.append(circle(150, axis_y, 7, fill=BG, stroke=NEG, sw=3))
    p.append(line(163, 166, 150, axis_y - 8, color=NEG, sw=1.4, dash="2 3"))

    # права картка — ESP32
    p.append(fitbox(W - 278, 86, 230, 80,
                    "ESP32\n2× 32-біт · до 240 МГц\nсотні КБ · мегабайти флеш\nрадіо · багата периферія",
                    size=11, fill=GREEN_FILL, stroke=FIELD, sw=2, color=INK, bold=False))
    p.append(circle(W - 150, axis_y, 9, fill=BG, stroke=FIELD, sw=3))
    p.append(line(W - 163, 166, W - 150, axis_y - 8, color=FIELD, sw=1.4, dash="2 3"))

    # дужка «обидва — мікроконтролери»
    p.append(line(150, axis_y + 30, W - 150, axis_y + 30, color=MUTED, sw=1.6))
    p.append(line(150, axis_y + 24, 150, axis_y + 30, color=MUTED, sw=1.6))
    p.append(line(W - 150, axis_y + 24, W - 150, axis_y + 30, color=MUTED, sw=1.6))
    p.append(text(W / 2, axis_y + 50, "обидва — мікроконтролери (та сама внутрішня анатомія)",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, "two-ends.svg"), W, H, *p,
           title="Два кінці однієї шкали — і обидва це мікроконтролери")


# ── axes: торнадо-діаграма осей переваги ──────────────────────────────────────
def fig_axes():
    W, H = 760, 470
    p = []
    cx = 380
    p.append(text(W / 2, 52, "ESP32 переважає згори, простий 8-біт — знизу: кожен кращий у своєму",
                  size=12, color=MUTED, italic=True))
    p.append(line(cx, 86, cx, 446, color=MUTED, sw=1.4))
    p.append(text(210, 80, "◀ перевага 8-біт", size=12, color=NEG, bold=True))
    p.append(text(cx + 170, 80, "перевага ESP32 ▶", size=12, color=FIELD, bold=True))

    # осі на користь ESP32 (праворуч)
    esp = [("Обчислення", 290), ("Памʼять", 280), ("Радіо (Wi-Fi/BT)", 262),
           ("Периферія", 210)]
    y = 104
    for lab, w in esp:
        p.append(rect(cx, y, w, 24, fill=GREEN_FILL, stroke=FIELD, sw=1.4, rx=4))
        p.append(text(cx + w + 8, y + 17, lab, size=11, color=INK, anchor="start", bold=True))
        y += 40

    # осі на користь 8-біт (ліворуч)
    eight = [("Дешевизна", 250), ("Простота, надійність", 226),
             ("Малий розмір", 184), ("Ощадність уві сні", 150)]
    y = 104 + 40 * 4 + 6
    for lab, w in eight:
        p.append(rect(cx - w, y, w, 24, fill=BLUE_FILL, stroke=NEG, sw=1.4, rx=4))
        p.append(text(cx - w - 8, y + 17, lab, size=11, color=INK, anchor="end", bold=True))
        y += 40

    render(os.path.join(OUT, "axes.svg"), W, H, *p,
           title="По яких осях вони різняться")


# ── when-which: дві колонки тригерів ──────────────────────────────────────────
def fig_when_which():
    W, H = 780, 430
    p = []
    p.append(text(W / 2, 52, "часто задача чітко світиться однією з колонок",
                  size=12, color=MUTED, italic=True))

    p.append(rect(40, 80, 340, 326, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=12))
    p.append(text(210, 106, "→ тягне до ESP32", size=14, color=FIELD, bold=True))
    esp = ["потрібен бездротовий звʼязок (Wi-Fi/BT)",
           "важкі обчислення (звук, сигнали, зображення)",
           "багато памʼяті: буфери, вебсторінки",
           "багато периферії або два потоки роботи"]
    y = 150
    for s in esp:
        p.append(text(60, y, "•", size=13, color=FIELD, anchor="start", bold=True))
        p.append(fitbox(76, y - 17, 292, 30, s, size=11, fill=BG, stroke=BG, sw=0, color=INK))
        y += 62

    p.append(rect(W - 380, 80, 340, 326, fill=BLUE_FILL, stroke=NEG, sw=2, rx=12))
    p.append(text(W - 210, 106, "→ тягне до 8-біт", size=14, color=NEG, bold=True))
    eight = ["копійки × мільйони штук — цент важить",
             "роки від монетної батарейки",
             "крихітний розмір, місце в обріз",
             "гранична простота й надійність",
             "радіо НЕ потрібне"]
    y = 144
    for s in eight:
        p.append(text(W - 360, y, "•", size=13, color=NEG, anchor="start", bold=True))
        p.append(fitbox(W - 344, y - 16, 300, 28, s, size=11, fill=BG, stroke=BG, sw=0, color=INK))
        y += 52

    render(os.path.join(OUT, "when-which.svg"), W, H, *p,
           title="Коли ESP32, а коли простий 8-біт")


# ── decision-flow: дерево рішень ──────────────────────────────────────────────
def fig_decision_flow():
    W, H = 780, 470
    p = []
    p.append(text(W / 2, 52, "кілька питань по черзі — і вибір стає очевидним",
                  size=12, color=MUTED, italic=True))

    def diamond(cx, cy, hw, hh, lines, fill=GOLD_FILL, stroke=GOLD):
        pts = "%g,%g %g,%g %g,%g %g,%g" % (cx, cy - hh, cx + hw, cy, cx, cy + hh, cx - hw, cy)
        out = '<polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (pts, fill, stroke)
        out += mtext(cx, cy - (len(lines) - 1) * 7 + 4, lines, size=11, color=INK, bold=True)
        return out

    qx = 250
    p.append(diamond(qx, 150, 140, 46, ["Потрібен бездротовий", "звʼязок (Wi-Fi/BT)?"]))
    p.append(diamond(qx, 290, 150, 46, ["Важкі обчислення", "або багато памʼяті?"]))
    p.append(diamond(qx, 422, 158, 46, ["Ціна×масштаб, роки від", "батарейки, простота?"]))

    # результати
    eb = fitbox(560, 252, 200, 64, "ESP32\n(потужність потрібна)", size=12,
                fill=GREEN_FILL, stroke=FIELD, sw=2, color=FIELD, bold=True)
    p.append(eb)
    bb = fitbox(560, 404, 200, 64, "Простий 8-біт\n(ціна · простота · сон)", size=12,
                fill=BLUE_FILL, stroke=NEG, sw=2, color=NEG, bold=True)
    p.append(bb)

    # стрілки «ні» вниз
    p.append(arrow(qx, 196, qx, 244, color=INK, sw=2))
    p.append(text(qx + 12, 224, "ні", size=10, color=MUTED, anchor="start"))
    p.append(arrow(qx, 336, qx, 376, color=INK, sw=2))
    p.append(text(qx + 12, 360, "ні", size=10, color=MUTED, anchor="start"))

    # стрілки «так» праворуч
    p.append(arrow(qx + 140, 150, 560, 274, color=FIELD, sw=2.2))
    p.append(text(440, 196, "так", size=11, color=FIELD, anchor="start", bold=True))
    p.append(arrow(qx + 150, 290, 560, 286, color=FIELD, sw=2.2))
    p.append(text(450, 274, "так", size=11, color=FIELD, anchor="start", bold=True))
    p.append(arrow(qx + 158, 422, 560, 438, color=NEG, sw=2.2))
    p.append(text(470, 414, "так", size=11, color=NEG, anchor="start", bold=True))

    render(os.path.join(OUT, "decision-flow.svg"), W, H, *p,
           title="Дерево рішень: ESP32 чи простий 8-біт")


# ── cost-power-scale: ціна×масштаб і життя від батарейки ──────────────────────
def fig_cost_power_scale():
    W, H = 760, 440
    p = []
    p.append(text(W / 2, 52, "дві осі, де переважує простий чіп, коли його досить",
                  size=12, color=MUTED, italic=True))

    # ліва панель — ціна × масштаб
    p.append(rect(40, 84, 340, 320, fill="none", stroke="#e4e4e4", sw=2, rx=12))
    p.append(text(210, 110, "Ціна × масштаб", size=13, color=INK, bold=True))
    p.append(text(150, 158, "8-біт  $0.40", size=11, color=NEG, anchor="end", bold=True))
    p.append(rect(160, 146, 32, 24, fill=BLUE_FILL, stroke=NEG, sw=1.4, rx=4))
    p.append(text(150, 200, "ESP32  $2.50", size=11, color=FIELD, anchor="end", bold=True))
    p.append(rect(160, 188, 200, 24, fill=GREEN_FILL, stroke=FIELD, sw=1.4, rx=4))
    p.append(text(210, 248, "× 1 000 000 штук", size=12, color=INK, bold=True))
    p.append(rect(70, 278, 280, 56, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    p.append(text(210, 302, "різниця у ціні чипів:", size=11, color=INK))
    p.append(text(210, 324, "≈ $2 100 000", size=16, color=POS, bold=True))

    # права панель — життя від батарейки
    p.append(rect(W - 380, 84, 340, 320, fill="none", stroke="#e4e4e4", sw=2, rx=12))
    p.append(text(W - 210, 110, "Життя від тієї самої батарейки", size=12, color=INK, bold=True))
    p.append(text(W - 210, 132, "(коли радіо не потрібне)", size=10, color=MUTED))
    p.append(text(W - 350, 188, "8-біт", size=11, color=NEG, anchor="end", bold=True))
    p.append(rect(W - 340, 176, 260, 26, fill=BLUE_FILL, stroke=NEG, sw=1.4, rx=4))
    p.append(text(W - 210, 194, "роки (одиниці мкА уві сні)", size=10, color=INK, bold=True))
    p.append(text(W - 350, 240, "ESP32", size=11, color=FIELD, anchor="end", bold=True))
    p.append(rect(W - 340, 228, 110, 26, fill=GREEN_FILL, stroke=FIELD, sw=1.4, rx=4))
    p.append(text(W - 285, 246, "менше", size=10, color=INK, bold=True))
    p.append(text(W - 210, 306, "простіший чіп уві сні бере менше", size=10, color=MUTED))
    p.append(text(W - 210, 324, "і має менше що живити", size=10, color=MUTED))

    render(os.path.join(OUT, "cost-power-scale.svg"), W, H, *p,
           title="Чому копійки й мікроампери вирішують на масштабі")


# ── scenarios: два сценарії — дві відповіді ───────────────────────────────────
def fig_scenarios():
    W, H = 780, 410
    p = []
    p.append(text(W / 2, 52, "правильний чіп визначає задача, а не амбіція",
                  size=12, color=MUTED, italic=True))

    def panel(x0, title, sub, left, right, verdict, vfill, vstroke):
        out = [rect(x0, 80, 340, 300, fill="none", stroke="#e4e4e4", sw=2, rx=12)]
        cx = x0 + 170
        out.append(text(cx, 106, title, size=13, color=INK, bold=True))
        out.append(text(cx, 128, sub, size=10, color=MUTED))
        out.append(fitbox(x0 + 28, 150, 142, 92, left[0], size=11,
                          fill=left[2], stroke=left[1], sw=1.6, color=left[1], bold=True))
        out.append(fitbox(x0 + 182, 150, 142, 92, right[0], size=11,
                          fill=right[2], stroke=right[1], sw=1.6, color=right[1], bold=True))
        out.append(fitbox(x0 + 28, 296, 296, 44, verdict, size=12,
                          fill=vfill, stroke=vstroke, sw=1.4, color=INK, bold=True))
        return out

    p += panel(40, "A · метеостанція в інтернет", "вимога: Wi-Fi (звʼязок у мережу)",
               ("8-біт\n✗ радіо немає\nзадача неможлива", NEG, "#fbfdff"),
               ("ESP32\n✓ Wi-Fi на борту\nєдиний вибір", FIELD, "#fbfefb"),
               "→ ESP32 (потужність потрібна)", GREEN_FILL, FIELD)
    p += panel(W - 380, "B · логер на батарейці ×1 млн", "2 роки автономності, без звʼязку",
               ("ESP32\n✗ +$2 млн\nвище споживання", FIELD, "#fbfefb"),
               ("8-біт\n✓ дешево, мкА\nроки життя", NEG, "#fbfdff"),
               "→ простий 8-біт (дешевше, довше)", BLUE_FILL, NEG)

    render(os.path.join(OUT, "scenarios.svg"), W, H, *p,
           title="Два сценарії — дві протилежні правильні відповіді")


# ════════ вставка hist-8051 ════════════════════════════════════════════════════

# ── timeline: лінія життя 8051 ────────────────────────────────────────────────
def fig_timeline():
    W, H = 880, 340
    p = []
    p.append(text(W / 2, 52, "архітектура 1980 року, яку досі виробляють десятки компаній",
                  size=11.5, color=MUTED, italic=True))
    axis_y = 168
    p.append(line(70, axis_y, W - 60, axis_y, color=INK, sw=2.5))

    nodes = [
        (118, "1976", "Intel 8048", "попередник (MCS-48)", NEG, BLUE_FILL, -1),
        (300, "1980", "Intel 8051", "родина MCS-51", POS, "#fbecec", 1),
        (470, "1980-ті", "Друге джерело", "Siemens·AMD·Philips", GOLD, "#eef0f5", -1),
        (640, "1990–2000-ті", "Похідні", "Atmel·Dallas·SiLabs", FIELD, GREEN_FILL, 1),
        (W - 90, "сьогодні", "IP-ядра", "у Bluetooth·USB·давачах", FIELD, GREEN_FILL, -1),
    ]
    for x, yr, name, sub, col, fill, side in nodes:
        p.append(circle(x, axis_y, 6, fill=col, stroke=col, sw=0))
        if side < 0:
            p.append(line(x, axis_y - 6, x, axis_y - 42, color=col, sw=1.6))
            by = axis_y - 94
        else:
            p.append(line(x, axis_y + 6, x, axis_y + 42, color=col, sw=1.6))
            by = axis_y + 42
        p.append(rect(x - 80, by, 160, 52, fill=fill, stroke=col, sw=1.6, rx=8))
        p.append(text(x, by + 19, yr, size=11, color=col, bold=True))
        p.append(text(x, by + 35, name, size=11, color=INK, bold=True))
        p.append(text(x, by + 48, sub, size=9, color=MUTED))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="8051: лінія життя, що не уривається")


# ── architecture: блок-схема 8051 ─────────────────────────────────────────────
def fig_architecture():
    W, H = 860, 470
    p = []
    p.append(text(W / 2, 52, "гарвардський поділ, бітові операції та швидкі банки — усе під керування, а не лічбу",
                  size=11, color=MUTED, italic=True))
    p.append(rect(50, 76, W - 100, 360, fill="#fbfcff", stroke=INK, sw=2.2, rx=12))
    p.append(text(72, 100, "Intel 8051 (1980)", size=10.5, color=MUTED, anchor="start", bold=True))

    # колонка 1 — ядро + банки (родзинка зелена)
    p.append(fitbox(110, 132, 200, 88,
                    "Ядро 8-біт\n+ БУЛІВ ПРОЦЕСОР\n17 бітових інструкцій",
                    size=11, fill=GREEN_FILL, stroke=FIELD, sw=1.8, color=INK, bold=True))
    p.append(fitbox(110, 248, 200, 82,
                    "4 банки регістрів\n× 8 — швидке\nперемикання контексту",
                    size=11, fill="#fbecec", stroke=POS, sw=1.8, color=INK, bold=True))

    # колонка 2 — памʼять
    p.append(fitbox(350, 132, 200, 70, "Program ROM\n4 КБ (Гарвард)",
                    size=11, fill=BLUE_FILL, stroke=NEG, sw=1.8, color=INK, bold=True))
    p.append(fitbox(350, 222, 200, 70, "Data RAM 128 Б\nє бітово-адресовна зона",
                    size=11, fill=GREEN_FILL, stroke=FIELD, sw=1.8, color=INK, bold=True))
    p.append(fitbox(350, 312, 200, 54, "2× таймери 16-біт",
                    size=11, fill=BG, stroke=INK, sw=1.8, color=INK, bold=True))

    # колонка 3 — периферія
    p.append(fitbox(590, 132, 200, 70, "UART\nпослідовний порт",
                    size=11, fill=BG, stroke=INK, sw=1.8, color=INK, bold=True))
    p.append(fitbox(590, 222, 200, 70, "Контролер переривань",
                    size=11, fill=BG, stroke=INK, sw=1.8, color=INK, bold=True))
    p.append(fitbox(590, 312, 200, 54, "Порти вводу-виводу",
                    size=11, fill=BG, stroke=INK, sw=1.8, color=INK, bold=True))

    p.append(fitbox(110, 388, 680, 36,
                    "Зелене — родзинка 8051: керувати окремими бітами так само легко, як байтами.",
                    size=10, fill=GREEN_FILL, stroke=FIELD, sw=1.4, color=INK, bold=True))

    render(os.path.join(OUT, "architecture.svg"), W, H, *p,
           title="Що нового було в 8051: булів процесор і банки регістрів")


# ── everywhere: 8051 як приховане ядро ────────────────────────────────────────
def fig_everywhere():
    W, H = 860, 430
    p = []
    p.append(text(W / 2, 52, "найчастіше його не видно — він працює IP-ядром усередині інших мікросхем",
                  size=11, color=MUTED, italic=True))
    cx, cy = W / 2, 200
    corners = [(195, 116), (W - 195, 116), (195, 290), (W - 195, 290)]
    for x, y in corners:
        p.append(line(cx, cy, x, y, color=FIELD, sw=1.2, dash="3 4"))

    cards = [
        (195, 116, "Bluetooth-чип"), (W - 195, 116, "USB-контролер"),
        (195, 290, "Компʼютерна миша"), (W - 195, 290, "Давач, смарт-картка"),
    ]
    for x, y, lab in cards:
        p.append(rect(x - 96, y - 32, 192, 64, fill="#fbfcff", stroke=INK, sw=1.8, rx=10))
        p.append(text(x, y - 6, lab, size=11, color=INK, bold=True))
        p.append(text(x, y + 13, "усередині — 8051", size=9, color=FIELD))

    p.append(circle(cx, cy, 50, fill=GREEN_FILL, stroke=FIELD, sw=2.4))
    p.append(text(cx, cy - 3, "8051", size=15, color=FIELD, bold=True))
    p.append(text(cx, cy + 15, "IP-ядро", size=9.5, color=INK))

    p.append(rect(cx - 134, 350, 268, 70, fill=GOLD_FILL, stroke=GOLD, sw=1.4, rx=10))
    p.append(text(cx, 373, "≈100 млн — за перше десятиліття", size=10.5, color=INK, bold=True))
    p.append(text(cx, 391, "мільярди штук на рік", size=10.5, color=INK, bold=True))
    p.append(text(cx, 409, "10+ млрд сукупно (і це применшено)", size=9.6, color=MUTED))

    render(os.path.join(OUT, "everywhere.svg"), W, H, *p,
           title="Безсмертя ядром: 8051 ховається в сучасних чипах")


# ════════ вставка math-benchmarks ══════════════════════════════════════════════

# ── mhz-myth: однакові МГц, різна робота ──────────────────────────────────────
def fig_mhz_myth():
    W, H = 860, 420
    p = []
    p.append(text(W / 2, 52, "ядро, що робить більше за такт, обганяє «швидше» ядро з тією ж частотою",
                  size=11.5, color=MUTED, italic=True))
    base = 350
    p.append(line(110, base, W - 90, base, color=INK, sw=1.6))
    p.append(line(W / 2 - 15, 130, W / 2 - 15, base + 10, color="#e4e4e4", sw=1.2, dash="4 4"))

    # ліворуч — частота (однакова)
    p.append(text(230, base + 36, "Тактова частота (МГц)", size=12, color=INK, bold=True))
    p.append(rect(178, base - 112, 50, 112, fill=BLUE_FILL, stroke=NEG, sw=1.6, rx=0))
    p.append(text(203, base - 120, "16", size=11, color=NEG, bold=True))
    p.append(text(203, base + 16, "ядро A", size=9.5, color=NEG))
    p.append(rect(272, base - 112, 50, 112, fill=GREEN_FILL, stroke=FIELD, sw=1.6, rx=0))
    p.append(text(297, base - 120, "16", size=11, color=FIELD, bold=True))
    p.append(text(297, base + 16, "ядро B", size=9.5, color=FIELD))
    p.append(text(250, base - 140, "однакові!", size=11, color=INK, bold=True))

    # праворуч — корисна робота (різна)
    p.append(text(645, base + 36, "Корисна робота (DMIPS)", size=12, color=INK, bold=True))
    p.append(rect(573, base - 88, 50, 88, fill=BLUE_FILL, stroke=NEG, sw=1.6, rx=0))
    p.append(text(598, base - 96, "16", size=11, color=NEG, bold=True))
    p.append(text(598, base + 16, "ядро A", size=9.5, color=NEG))
    p.append(rect(667, base - 220, 50, 220, fill=GREEN_FILL, stroke=FIELD, sw=1.6, rx=0))
    p.append(text(692, base - 228, "40", size=11, color=FIELD, bold=True))
    p.append(text(692, base + 16, "ядро B", size=9.5, color=FIELD))
    p.append(text(645, base - 248, "× 2.5 різниця!", size=11, color=POS, bold=True))

    p.append(rect(170, 90, 520, 40, fill=GOLD_FILL, stroke=GOLD, sw=1.4, rx=8))
    p.append(text(430, 115, "B робить 2.5× за такт (DMIPS/МГц) — ось де ховається правда",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "mhz-myth.svg"), W, H, *p,
           title="Міф мегагерців: однакові МГц — різна швидкість")


# ── honesty-ladder: драбина чесності ──────────────────────────────────────────
def fig_honesty_ladder():
    W, H = 860, 440
    p = []
    p.append(text(W / 2, 52, "що вище — то ближче до правди про швидкість на ТВОЇХ задачах",
                  size=11.5, color=MUTED, italic=True))
    rungs = [
        ("Виміряти СВОЇ задачі", "твій код, твоя памʼять — найчесніше", FIELD, GREEN_FILL, 96),
        ("Профільний бенчмарк (CoreMark)", "ближче до реальних задач, ніж Dhrystone", NEG, BLUE_FILL, 166),
        ("DMIPS / МГц", "враховує корисну роботу за такт", GOLD, "#eef0f5", 236),
        ("Лише МГц", "оманливо: ігнорує архітектуру", POS, "#fbecec", 306),
    ]
    for title, sub, col, fill, y in rungs:
        p.append(rect(180, y, 560, 56, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(200, y + 24, title, size=12.5, color=col, anchor="start", bold=True))
        p.append(text(200, y + 43, sub, size=9.6, color=INK, anchor="start"))

    p.append(arrow(140, 404, 140, 90, color=FIELD, sw=3))
    p.append(text(140, 84, "чесніше", size=10.5, color=FIELD, bold=True))
    p.append(text(140, 420, "наївно", size=10.5, color=POS, bold=True))
    p.append(rect(180, 386, 560, 40, fill="#eef0f2", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(460, 411,
                  "робота ≈ МГц × DMIPS/МГц — але жоден бенчмарк не замінить заміру власного коду",
                  size=10, color=INK, bold=True))

    render(os.path.join(OUT, "honesty-ladder.svg"), W, H, *p,
           title="Драбина чесного порівняння ядер")


if __name__ == "__main__":
    fig_two_ends()
    fig_axes()
    fig_when_which()
    fig_decision_flow()
    fig_cost_power_scale()
    fig_scenarios()
    fig_timeline()
    fig_architecture()
    fig_everywhere()
    fig_mhz_myth()
    fig_honesty_ladder()
    print("OK: figures written to", OUT)
