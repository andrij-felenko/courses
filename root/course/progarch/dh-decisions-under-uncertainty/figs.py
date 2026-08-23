# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")


def dot(cx, cy, color):
    return circle(cx, cy, 8, fill=color, stroke=INK, sw=1.5)


# ── Фігура 1: мапа рішень (туман × вартість відкату) ────────────────────────
def fig_map():
    W, H = 780, 560
    L, R, T, B = 120, 720, 70, 480          # межі поля
    VX, VY = 420, 275                        # роздільники чвертей
    frags = []

    # тло небезпечної чверті (дорого + туман) — праворуч угорі
    frags.append(rect(VX, T, R - VX, VY - T, fill="#fdecea", stroke="none", sw=0))

    # роздільники чвертей
    frags.append(line(VX, T, VX, B, color=MUTED, sw=1.2, dash="6 5"))
    frags.append(line(L, VY, R, VY, color=MUTED, sw=1.2, dash="6 5"))

    # осі
    frags.append(arrow(L, B, R + 12, B, color=INK, sw=2))       # x →
    frags.append(arrow(L, B, L, T - 12, color=INK, sw=2))       # y ↑

    # підписи кінців осей
    frags.append(text((L + VX) / 2, B + 26, "ясно, знаємо", size=12, color=MUTED))
    frags.append(text((VX + R) / 2, B + 26, "багато туману", size=12, color=MUTED))
    frags.append(text(415, B + 48, "туман: наскільки не знаємо  →", size=13, color=INK))
    frags.append(text(72, (T + VY) / 2, "дорого", size=12, color=MUTED))
    frags.append(text(72, (T + VY) / 2 + 16, "відкотити", size=12, color=MUTED))
    frags.append(text(72, (VY + B) / 2, "дешево", size=12, color=MUTED))
    frags.append(text(72, (VY + B) / 2 + 16, "відкотити", size=12, color=MUTED))

    # ярлики-ходи по чвертях (у зовнішніх кутах)
    frags.append(fitbox(150, 92, 210, 44, "Вирішуй виважено:\nфакти вже є",
                        size=13, fill=BG, stroke=NEG, color=NEG, bold=True))
    frags.append(fitbox(478, 92, 226, 44, "Небезпечна чверть:\nшов · спайк · LRM",
                        size=13, fill=BG, stroke=POS, color=POS, bold=True))
    frags.append(fitbox(150, 300, 196, 40, "Вирішуй зараз",
                        size=13, fill=BG, stroke=FIELD, color=FIELD, bold=True))
    frags.append(fitbox(486, 300, 210, 44, "Спробуй —\nлегко відкотиш",
                        size=13, fill=BG, stroke=FIELD, color=FIELD, bold=True))

    # точки-рішення DH (по одній на чверть)
    frags.append(dot(250, 205, NEG))
    frags.append(text(250, 232, "своя плата", size=13, color=INK))
    frags.append(dot(590, 205, POS))
    frags.append(text(590, 232, "радіо-протокол", size=13, color=POS, bold=True))
    frags.append(dot(250, 430, FIELD))
    frags.append(text(250, 410, "стек хаба", size=13, color=INK))
    frags.append(dot(590, 430, FIELD))
    frags.append(text(590, 410, "керований брокер", size=13, color=INK))

    render(os.path.join(IMG, "decision-map.svg"), W, H, *frags)


# ── Фігура 2: одно/двобічні двері через шов ─────────────────────────────────
def fig_seam():
    W, H = 820, 430
    frags = []
    mods = ["правила", "стан", "логи"]

    # роздільник панелей
    frags.append(line(410, 78, 410, 388, color=MUTED, sw=1.2, dash="6 5"))

    # ── ліва панель: прямо в код ──
    frags.append(text(210, 52, "Прямо в код — однобічні двері", size=14, color=POS, bold=True))
    lx = [110, 210, 310]
    for x, m in zip(lx, mods):
        body, w, h = textbox(x, 108, m, size=13, fill=FILL, stroke=LINE)
        frags.append(body)
    zbody, zw, zh = textbox(210, 300, "Zigbee", size=14, fill="#fdecea", stroke=POS, bold=True)
    frags.append(zbody)
    for x in lx:
        frags.append(arrow(x, 128, 210, 300 - zh / 2 - 4, color=POS, sw=1.6))
    frags.append(text(210, 360, "змінити радіо = переписати все", size=12, color=POS))

    # ── права панель: за швом ──
    frags.append(text(610, 52, "За швом — двобічні двері", size=14, color=FIELD, bold=True))
    rx = [510, 610, 710]
    for x, m in zip(rx, mods):
        body, w, h = textbox(x, 108, m, size=13, fill=FILL, stroke=LINE)
        frags.append(body)
    pbody, pw, ph = textbox(610, 205, "DevicePort (шов)", size=13, fill="#eafaf0", stroke=FIELD, bold=True)
    frags.append(pbody)
    for x in rx:
        frags.append(arrow(x, 128, 610, 205 - ph / 2 - 4, color=INK, sw=1.5))
    abody, aw, ah = textbox(560, 300, "Zigbee-\nадаптер", size=12, fill=FILL, stroke=LINE)
    frags.append(abody)
    frags.append(arrow(610, 205 + ph / 2, 560, 300 - ah / 2 - 4, color=INK, sw=1.5))
    # порожній слот під інший радіо
    frags.append(rect(690, 282, 96, 40, fill=BG, stroke=MUTED, sw=1.4, rx=6))
    frags.append(text(738, 300, "інший", size=12, color=MUTED))
    frags.append(text(738, 315, "радіо", size=12, color=MUTED))
    frags.append(arrow(610, 205 + ph / 2, 690, 296, color=MUTED, sw=1.3))
    frags.append(text(610, 360, "змінити радіо = один адаптер", size=12, color=FIELD))

    render(os.path.join(IMG, "seam-reversible.svg"), W, H, *frags)


# ── Фігура 3 (вставка): хроніка війни стандартів розумного дому ──────────────
def fig_standards_timeline():
    W, H = 1080, 440
    SPINE = 220
    frags = []

    # події: (рік+назва, короткий підпис, колір вузла)
    events = [
        ("1975 · X10", "по дротах", INK),
        ("1999 · Z-Wave", "суб-ГГц", NEG),
        ("2002 · Zigbee", "2.4 ГГц, сітка", FIELD),
        ("2005 · Insteon", "дводіапазон", INK),
        ("2014 · Thread", "IPv6 · 802.15.4", FIELD),
        ("2019 · CHIP", "перемир'я", MUTED),
        ("2022 · Matter 1.0", "4 жовтня", FIELD),
        ("2026", "без переможця", POS),
    ]
    n = len(events)
    x0, x1 = 80, W - 80
    step = (x1 - x0) / (n - 1)
    xs = [x0 + i * step for i in range(n)]

    # хребет-лінія
    frags.append(line(x0 - 10, SPINE, x1 + 10, SPINE, color=MUTED, sw=2))

    for i, (name, note, col) in enumerate(events):
        x = xs[i]
        above = (i % 2 == 1)          # непарні — вгору, парні — вниз
        cy = 120 if above else 322
        body, w, h = textbox(x, cy, name + "\n" + note, size=12,
                             fill=BG, stroke=col, color=INK)
        # конектор від вузла до краю рамки
        edge = cy + h / 2 if above else cy - h / 2
        frags.append(line(x, SPINE, x, edge, color=MUTED, sw=1.2))
        frags.append(body)
        frags.append(circle(x, SPINE, 8, fill=col, stroke=BG, sw=2))

    render(os.path.join(IMG, "standards-war-timeline.svg"), W, H, *frags)


# ── Фігура 4 (вставка): гіганти хеджували — ставки розсипано по кількох радіо ─
def fig_giants_hedge():
    W, H = 780, 400
    frags = []

    cols = ["Zigbee", "Z-Wave", "Thread", "Власна\nплатформа", "Matter"]
    rows = ["Google\nNest", "Amazon", "Apple", "Samsung\nSmartThings"]

    LX0, LX1 = 175, 745          # поле точок по X
    cstep = (LX1 - LX0) / len(cols)
    cx = [LX0 + cstep * (j + 0.5) for j in range(len(cols))]
    TY0, TY1 = 108, 360          # поле точок по Y
    rstep = (TY1 - TY0) / len(rows)
    ry = [TY0 + rstep * (i + 0.5) for i in range(len(rows))]

    # заголовки колонок
    for j, c in enumerate(cols):
        frags.append(mtext(cx[j], 58, c, size=12, color=INK, bold=True, lh=1.15))
    # підписи рядків (ліворуч)
    for i, r in enumerate(rows):
        frags.append(mtext(30, ry[i] - 6, r, size=12, color=INK, bold=True,
                           anchor="start", lh=1.15))

    # хто на що ставив: 1 = ставка; колонки Zigbee,Z-Wave,Thread,Власна,Matter
    M = [
        [0, 0, 1, 1, 1],   # Google/Nest
        [1, 0, 1, 1, 1],   # Amazon
        [0, 0, 1, 1, 1],   # Apple
        [1, 1, 1, 1, 1],   # Samsung
    ]
    # легкі напрямні
    for j in range(len(cols)):
        frags.append(line(cx[j], TY0 - 18, cx[j], TY1 - rstep / 2 + 6,
                          color="#e5e7eb", sw=1))

    for i in range(len(rows)):
        for j in range(len(cols)):
            if M[i][j]:
                if j == 4:          # Matter — спільне перемир'я
                    col = FIELD
                elif j == 3:        # власна платформа — свій «замок»
                    col = POS
                else:               # чуже радіо
                    col = INK
                frags.append(circle(cx[j], ry[i], 9, fill=col, stroke=BG, sw=1.5))
            else:
                frags.append(circle(cx[j], ry[i], 3.5, fill="none",
                                   stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, "giants-hedged.svg"), W, H, *frags)


# ── Фігура 5 (вставка proj): спайк перетворює питання дошки на факти ─────────
def fig_spike_probe():
    W, H = 880, 440
    frags = []
    rows = [155, 250, 345]
    questions = ["як пристрої\nпаруються?",
                 "чи бреше\nдрайвер?",
                 "чи є те залізо\nв магазинах?"]
    facts = ["кнопка + вікно;\n~2 спроби, 40 с",
             "віддає СОТІ °C\n2000 = 20.00",
             "координатор і давач\n— є в продажу"]

    frags.append(text(150, 75, "Біла дошка не знає", size=14, color=MUTED, bold=True))
    frags.append(text(705, 75, "Спайк повертає факт", size=14, color=FIELD, bold=True))

    # проба-спайк — вертикальна смуга крізь усі три рядки
    frags.append(rect(365, 110, 110, 280, fill=FILL, stroke=LINE, sw=1.6))
    frags.append(text(420, 245, "спайк", size=15, color=INK, bold=True))
    frags.append(text(420, 268, "проба", size=12, color=MUTED))
    frags.append(text(420, 415, "тонкий наскрізний зріз", size=12, color=MUTED))

    for y, q, fct in zip(rows, questions, facts):
        qb, qw, qh = textbox(150, y, q, size=13, fill=BG, stroke=MUTED)
        frags.append(qb)
        fb, fw, fh = textbox(705, y, fct, size=13, fill="#eafaf0", stroke=FIELD)
        frags.append(fb)
        frags.append(arrow(220, y, 363, y, color=MUTED, sw=1.6))
        frags.append(arrow(477, y, 618, y, color=FIELD, sw=1.8))

    render(os.path.join(IMG, "spike-probe.svg"), W, H, *frags)


# ── Фігура 6 (вставка proj): спайк помирає, шов лишається ───────────────────
def fig_spike_throwaway():
    W, H = 840, 480
    frags = []

    # ── верх: викинути ──
    frags.append(rect(85, 70, 590, 175, fill=BG, stroke=POS, sw=1.6, rx=10))
    frags.append(text(102, 100, "Спайк — викинути після прогону",
                      size=14, color=POS, anchor="start", bold=True))
    frags.append(text(648, 104, "✂", size=22, color=POS))
    chips = ["permit-join\nтанець", "зашиті ID\nпристроїв",
             "одне\nправило", "журнал\nпрогону"]
    for x, c in zip([180, 325, 470, 610], chips):
        body, w, h = textbox(x, 172, c, size=12, fill=FILL, stroke=MUTED)
        frags.append(body)

    # ── низ: лишити ──
    frags.append(text(90, 300, "Лишити:", size=14, color=FIELD, anchor="start", bold=True))
    frags.append(rect(140, 320, 420, 48, fill="#eafaf0", stroke=FIELD, sw=2))
    frags.append(text(350, 350, "DevicePort (шов)", size=15, color=FIELD, bold=True))

    zb, zw, zh = textbox(250, 427, "Zigbee-адаптер\n(перший)", size=12,
                         fill=FILL, stroke=LINE)
    frags.append(zb)
    nb, nw, nh = textbox(470, 427, "наступний адаптер\n(Z-Wave · Matter)", size=12,
                         fill=BG, stroke=MUTED)
    frags.append(nb)
    frags.append(arrow(250, 368, 250, 401, color=MUTED, sw=1.5))
    frags.append(arrow(470, 368, 470, 401, color=MUTED, sw=1.5))

    frags.append(text(350, 466, "той самий шов — новий адаптер; ставка зворотна",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "spike-throwaway.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_map()
    fig_seam()
    fig_standards_timeline()
    fig_giants_hedge()
    fig_spike_probe()
    fig_spike_throwaway()
    print("ok")
