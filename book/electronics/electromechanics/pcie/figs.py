# -*- coding: utf-8 -*-
"""Фігури до теми «PCIe».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

LGREEN = "#eafaf0"
LBLUE  = "#eaf0fd"
LRED   = "#fdecea"
GOLD   = "#c9971f"
LGOLD  = "#f6eccf"


def chip(x, y, label, stroke, fill, w=48, h=26, size=11.5):
    return fitbox(x, y, w, h, label, size=size, fill=fill, stroke=stroke, color=stroke, bold=True)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 1 — смуга (дві пари) і ширина з'єднання (розкидання байтів по смугах)
# ════════════════════════════════════════════════════════════════════════════
def fig_lanes_width():
    W, H = 880, 540
    els = [text(W / 2, 30, "Смуга й ширина з'єднання PCIe", size=16, bold=True)]

    # ── Панель A: одна смуга = пара TX + пара RX ──
    els.append(text(W / 2, 62, "Одна смуга — дві диференційні пари, повний двобічний канал",
                    size=13, bold=True))
    cyA = 138
    els.append(fitbox(70, cyA - 40, 128, 80, "пристрій\nA", size=13, fill=FILL, stroke=LINE, bold=True))
    els.append(fitbox(682, cyA - 40, 128, 80, "пристрій\nB", size=13, fill=FILL, stroke=LINE, bold=True))
    xL, xR = 198, 682
    # пара TX (A → B)
    els.append(text((xL + xR) / 2, cyA - 44, "пара TX  (туди, A → B)", size=12, color=INK, bold=True))
    els.append(line(xL, cyA - 28, xR, cyA - 28, color=POS, sw=2.4))
    els.append(line(xL, cyA - 20, xR, cyA - 20, color=NEG, sw=2.4))
    els.append(arrow(xR - 120, cyA - 24, xR - 6, cyA - 24, color=MUTED, sw=1.4))
    # пара RX (B → A)
    els.append(line(xL, cyA + 20, xR, cyA + 20, color=POS, sw=2.4))
    els.append(line(xL, cyA + 28, xR, cyA + 28, color=NEG, sw=2.4))
    els.append(arrow(xL + 120, cyA + 24, xL + 6, cyA + 24, color=MUTED, sw=1.4))
    els.append(text((xL + xR) / 2, cyA + 52, "пара RX  (назад, B → A)", size=12, color=INK, bold=True))
    els.append(text(W / 2, cyA + 86, "4 проводи = повний двобічний канал — це й є одна смуга (англ. lane)",
                    size=12, color=MUTED))

    els.append(line(40, 258, W - 40, 258, color=MUTED, sw=1, dash="4,5"))

    # ── Панель B: з'єднання ×4, байти розкидано по смугах ──
    els.append(text(W / 2, 292, "З'єднання ×4: байти розкидано по смугах по черзі; кожна смуга — власний такт",
                    size=13, bold=True))
    lane_x0, lane_x1 = 190, 650
    lane_h = 34
    tops = [316, 360, 404, 448]
    # джерело байтів
    els.append(fitbox(40, tops[0], 118, tops[-1] + lane_h - tops[0], "потік\nбайтів\nB0 B1 B2\nB3 B4 …",
                      size=11.5, fill=FILL, stroke=LINE, bold=True))
    src_cx, src_cy = 158, (tops[0] + tops[-1] + lane_h) / 2
    # приймач
    els.append(fitbox(690, tops[0], 150, tops[-1] + lane_h - tops[0],
                      "приймач:\nбуферизує\nй вирівнює\nсмуги\nв цифрі", size=11.5,
                      fill=LBLUE, stroke=NEG, color=NEG, bold=True))
    for i, ty in enumerate(tops):
        cy = ty + lane_h / 2
        els.append(rect(lane_x0, ty, lane_x1 - lane_x0, lane_h, fill=BG, stroke=LINE, sw=1.4))
        els.append(chip(lane_x0 + 8, cy - 13, "смуга %d" % i, MUTED, FILL, w=70))
        els.append(chip(lane_x0 + 88, cy - 13, "CDR", NEG, LBLUE, w=52))
        els.append(chip(lane_x0 + 178, cy - 13, "B%d" % i, FIELD, LGREEN, w=44))
        els.append(chip(lane_x0 + 256, cy - 13, "B%d" % (i + 4), FIELD, LGREEN, w=44))
        els.append(text(lane_x0 + 380, cy + 4, "…", size=15, color=MUTED))
        # джерело → смуга
        els.append(arrow(src_cx + 4, src_cy + (cy - src_cy) * 0.12, lane_x0 - 2, cy, color=MUTED, sw=1.3))
        # смуга → приймач
        els.append(arrow(lane_x1 + 2, cy, 688, cy, color=MUTED, sw=1.3))
    els.append(text(W / 2, 512,
                    "×1 · ×4 · ×16 — більше смуг = більша смуга пропускання; смуги можуть розбігтися, приймач їх вирівнює",
                    size=12, color=MUTED))
    render(os.path.join(IMG, "lanes-width.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 2 — крайовий роз'єм: довжина пелюстки задає черговість замикання
# ════════════════════════════════════════════════════════════════════════════
def fig_edge_connector():
    W, H = 900, 470
    els = [text(W / 2, 30, "Крайовий роз'єм PCIe: довжина пелюстки задає черговість замикання",
                size=15.5, bold=True)]

    # ── головний вид: карта з пелюстками входить у слот ──
    card_x, card_y, card_w, card_h = 110, 74, 470, 44
    els.append(fitbox(card_x, card_y, card_w, card_h, "плата (карта)", size=13,
                      fill=FILL, stroke=LINE, bold=True))
    card_bot = card_y + card_h

    # стрілка вставляння
    els.append(text(92, 64, "вставляння", size=11.5, color=INK, anchor="middle", bold=True))
    els.append(arrow(92, 74, 92, card_bot + 16, color=INK, sw=2))

    spring_y = 224                 # рівень пружинних контактів слота
    tip = {"GND": 252, "PWR": 230, "SIG": 208}   # довший (нижчий кінчик) = раніше
    col = {"GND": FIELD, "PWR": POS, "SIG": INK}
    fillc = {"GND": LGREEN, "PWR": LRED, "SIG": LGOLD}

    # корпус слота (гніздо) — світлий канал позаду пелюсток
    els.append(rect(card_x + 6, spring_y - 12, card_w - 12, 52, fill="#f0f2f4", stroke=MUTED, sw=1.2))
    els.append(line(card_x + 6, spring_y, card_x + card_w - 6, spring_y, color=MUTED, sw=1.3, dash="4,4"))
    els.append(mtext(card_x + card_w + 8, spring_y - 2, ["пружини", "слота"], size=10.5, color=MUTED, anchor="start"))

    fingers = [(140, "GND"), (176, "SIG"), (212, "SIG"), (248, "PWR"), (284, "SIG"), (320, "SIG"),
               (392, "GND"), (428, "SIG"), (464, "SIG"), (500, "PWR"), (536, "SIG")]
    notch_x = 356
    fw = 15
    for cx, t in fingers:
        ty = tip[t]
        els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s" stroke="%s" stroke-width="1.3"/>'
                   % (cx - fw / 2, card_bot, fw, ty - card_bot, fillc[t], GOLD))
        if ty >= spring_y:         # кінчик дійшов до пружин — контакт замкнено
            els.append(circle(cx, spring_y, 4.2, fill=col[t], stroke=col[t], sw=1))
    # ключ-проріз (пропуск у ряду пелюсток)
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.25" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>'
               % (notch_x - 14, card_bot, 28, 150, MUTED, MUTED))
    els.append(text(notch_x, card_y - 8, "ключ-проріз", size=11, color=INK, bold=True))

    els.append(text(card_x + card_w / 2, 292,
                    "мить під час вставляння: земля й живлення вже торкнулись пружин, сигнал — ще ні",
                    size=11.5, color=INK, bold=True))

    # легенда кольорів пелюсток
    lx, ly = 110, 328
    for t, lab in [("GND", "земля — найдовші"), ("PWR", "живлення"), ("SIG", "сигнал — найкоротші")]:
        els.append('<rect x="%.1f" y="%.1f" width="20" height="20" rx="3" fill="%s" stroke="%s" stroke-width="1.3"/>'
                   % (lx, ly, fillc[t], GOLD))
        els.append(text(lx + 28, ly + 15, lab, size=11.5, color=col[t], anchor="start", bold=True))
        lx += 182

    # ── права панель: черговість ──
    px = 640
    els.append(text(px + 110, 74, "Черговість замикання", size=13, bold=True))
    steps = [("1  земля", FIELD), ("2  живлення", POS), ("3  сигнал", INK)]
    sy = 108
    for i, (lab, c) in enumerate(steps):
        yy = sy + i * 52
        els.append(circle(px + 20, yy, 9, fill=c, stroke=c, sw=1))
        els.append(text(px + 40, yy + 5, lab, size=13, color=c, anchor="start", bold=True))
        if i < 2:
            els.append(arrow(px + 20, yy + 12, px + 20, yy + 40, color=MUTED, sw=1.5))
    els.append(text(px + 6, sy + 3 * 52 + 6, "виймання — у зворотному порядку",
                    size=11, color=MUTED, anchor="start", italic=True))
    els.append(fitbox(px - 6, 300, 250, 92,
                      "сигнал приходить у плату лише\nколи вже є земля й живлення:\nкидок пускового струму осідає,\nлогіка з'єднується безпечно\n(гаряче під'єднання)",
                      size=11, fill=LGREEN, stroke=FIELD, color=INK))
    render(os.path.join(IMG, "edge-connector.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 3 — трирівневий пакет: кожен рівень обгортає попередній
# ════════════════════════════════════════════════════════════════════════════
def fig_protocol_layers():
    W, H = 900, 430
    els = [text(W / 2, 30, "Пакет PCIe: кожен рівень додає свою обгортку навколо попереднього",
                size=15.5, bold=True)]

    # смуга сегментів
    segs = [("кадр\nSTP", 66, POS, LRED),
            ("номер\nSeq#", 84, NEG, LBLUE),
            ("заголовок\nTLP", 130, FIELD, LGREEN),
            ("дані", 170, FIELD, LGREEN),
            ("LCRC", 80, NEG, LBLUE),
            ("кадр\nEND", 60, POS, LRED)]
    total = sum(s[1] for s in segs)
    x0 = (W - total) / 2
    strip_top, strip_h = 250, 50
    xs = [x0]
    for _, w, _, _ in segs:
        xs.append(xs[-1] + w)
    for i, (lab, w, stroke, fill) in enumerate(segs):
        els.append(fitbox(xs[i], strip_top, w, strip_h, lab, size=11.5, fill=fill, stroke=stroke,
                          color=stroke, bold=True))

    # межі сегментів у координатах
    x_stp0, x_seq0 = xs[0], xs[1]
    x_hdr0, x_data0 = xs[2], xs[3]
    x_lcrc0, x_end0, x_end1 = xs[4], xs[5], xs[6]

    def bracket(x1, x2, ytop, color, label):
        out = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="none" stroke="%s" stroke-width="2"/>'
               % (x1, ytop, x2 - x1, strip_top + strip_h + 8 - ytop, color)]
        out.append(text((x1 + x2) / 2, ytop - 7, label, size=11.5, color=color, bold=True))
        return out

    # внутрішній — транзакційний (заголовок + дані)
    els += bracket(x_hdr0 - 5, x_data0 + segs[3][1] + 5, 216, FIELD,
                   "транзакційний рівень — TLP: заголовок + дані  (СЕНС)")
    # середній — з'єднання (номер … LCRC)
    els += bracket(x_seq0 - 10, x_lcrc0 + segs[4][1] + 10, 184, NEG,
                   "рівень з'єднання — + номер + LCRC, квитанції ACK/NAK  (НАДІЙНІСТЬ)")
    # зовнішній — фізичний (кадр … кадр)
    els += bracket(x_stp0 - 15, x_end1 + 15, 152, POS,
                   "фізичний рівень — + кадр + скремблювання/кодування  (ДРІТ)")

    els.append(text(W / 2, 344, "Зверху вниз два рівні незмінні роками: транзакційний і з'єднання.",
                    size=12, color=INK))
    els.append(text(W / 2, 366, "Міняється лише фізичний: 2.5 → 64 ГТ/с, 8b/10b → PAM4 — а договір пакета той самий.",
                    size=12, color=MUTED))
    render(os.path.join(IMG, "protocol-layers.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 4 (вставка math) — драбина подвоєнь і зарубка лінійного коду
# ════════════════════════════════════════════════════════════════════════════
def fig_doubling_ladder():
    W, H = 940, 470
    els = [text(W / 2, 30, "Драбина подвоєнь: де смуга не догнала рівне ×2", size=16, bold=True)]
    els.append(text(W / 2, 54,
                    "частка від ідеальної драбини 250·2ⁿ⁻¹ МБ/с на смугу (в один бік)",
                    size=12.5, color=MUTED))

    # координати
    x0, x1 = 100, 800            # ліва й права межа поля
    slot = (x1 - x0) / 7.0       # 100 px на покоління
    def cx(n):                   # центр слота покоління n (1..7)
        return x0 + slot * (n - 0.5)

    y100, y985 = 190.0, 313.0    # рівні 100 % і 98.46 %
    axis_y = 372.0

    # опорна лінія 100 %
    els.append(line(x0 - 8, y100, x1 + 8, y100, color=MUTED, sw=1.4, dash="6 5"))
    els.append(text(x1 + 18, y100 + 4, "100 %", size=12, color=MUTED, anchor="start"))
    els.append(line(x0 - 8, y985, x1 + 8, y985, color=MUTED, sw=1.0, dash="3 6"))
    els.append(text(x1 + 18, y985 + 4, "98.46 %", size=12, color=MUTED, anchor="start"))

    # східчаста лінія: 1,2 — вгорі; 3,4,5 — унизу; 6,7 — знову вгорі
    half = slot * 0.42
    els.append(line(cx(1) - half, y100, cx(2) + half, y100, color=NEG, sw=4.5))
    els.append(line(cx(3) - half, y985, cx(5) + half, y985, color=POS, sw=4.5))
    els.append(line(cx(6) - half, y100, cx(7) + half, y100, color=NEG, sw=4.5))
    # вертикальні переходи
    els.append(line(cx(2) + half, y100, cx(3) - half, y985, color=POS, sw=4.5))
    els.append(line(cx(5) + half, y985, cx(6) - half, y100, color=NEG, sw=4.5))

    # коефіцієнти переходів — над полем, у проміжках між слотами
    ratios = [(1, "×2"), (2, "×128/65"), (3, "×2"), (4, "×2"), (5, "×65/32"), (6, "×2")]
    for n, lab in ratios:
        xm = x0 + slot * n
        bold = lab != "×2"
        col = POS if lab == "×128/65" else (NEG if lab == "×65/32" else MUTED)
        els.append(text(xm, 108, lab, size=12.5, color=col, bold=bold))
        els.append(line(xm - 22, 118, xm + 22, 118, color=col, sw=1.2))

    # вісь і підписи поколінь
    els.append(line(x0 - 8, axis_y, x1 + 8, axis_y, color=LINE, sw=1.5))
    rows = [(1, "2.5 ГТ/с", "250"), (2, "5 ГТ/с", "500"), (3, "8 ГТ/с", "985"),
            (4, "16 ГТ/с", "1969"), (5, "32 ГТ/с", "3938"), (6, "64 ГТ/с", "8000"),
            (7, "128 ГТ/с", "16000")]
    for n, f, b in rows:
        els.append(line(cx(n), axis_y, cx(n), axis_y + 7, color=LINE, sw=1.2))
        els.append(mtext(cx(n), axis_y + 26, ["Gen %d" % n, f, b + " МБ/с"],
                         size=11.5, color=INK, lh=1.35))

    # пояснення зарубки
    els.append(text((cx(3) + cx(5)) / 2, 348,
                    "128b/130b: корисне · 64/65 — рівно 1/65 = 1.54 % податку",
                    size=12, color=POS, bold=True))
    els.append(text(cx(6) + 8, 236, "1b/1b — лінійного коду нема", size=12, color=NEG, bold=True))
    els.append(text(cx(1) + 6, 236, "8b/10b — податок є, але його вже", size=11.5, color=MUTED))
    els.append(text(cx(1) + 6, 252, "враховано в опорних 250 МБ/с", size=11.5, color=MUTED))

    els.append(text(W / 2, 448,
                    "Зарубка відкривається на Gen 3 і закривається на Gen 6: (128/65)·(65/32) = 4 = 2² — рівно два подвоєння.",
                    size=12, color=INK))
    render(os.path.join(IMG, "doubling-ladder.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 5 (вставка math) — ланцюжок перетворення ГТ/с → ГБ/с і дві домовленості
# ════════════════════════════════════════════════════════════════════════════
def fig_bandwidth_chain():
    W, H = 1000, 440
    els = [text(W / 2, 30, "Одна смуга Gen 4 → число на етикетці: два способи лічби", size=16, bold=True)]

    bw, gap = 168, 86
    xs = [40 + i * (bw + gap) for i in range(4)]     # ліві краї коробок
    bh = 58

    def row(cy, vals, arrows, box_stroke, box_fill, cap, cap_color):
        out = [text(W / 2, cy - 62, cap, size=12.5, color=cap_color, bold=True)]
        for i, v in enumerate(vals):
            out.append(fitbox(xs[i], cy - bh / 2, bw, bh, v, size=13,
                              fill=box_fill, stroke=box_stroke, color=INK, bold=True))
        for i, a in enumerate(arrows):
            xa, xb = xs[i] + bw + 8, xs[i + 1] - 8
            out.append(arrow(xa, cy, xb, cy, color=box_stroke))
            out.append(text((xa + xb) / 2, cy - 38, a, size=11.5, color=box_stroke, bold=True))
        return out

    els += row(150,
               ["16 ГТ/с\nна смугу", "1.969 ГБ/с\nна смугу", "31.51 ГБ/с\n×16, один бік",
                "63.02 ГБ/с\n×16, обидва боки"],
               ["· 64/65 ÷ 8", "· 16 смуг", "· 2 напрямки"],
               POS, LRED,
               "як рахує фізика: спершу віднімаємо лінійний код 128b/130b", POS)

    els += row(320,
               ["16 ГТ/с\nна смугу", "2.00 ГБ/с\nна смугу", "32 ГБ/с\n×16, один бік",
                "64 ГБ/с\n×16, обидва боки"],
               ["÷ 8, без коду", "· 16 смуг", "· 2 напрямки"],
               NEG, LBLUE,
               "як рахує рекламний аркуш: код не віднімають зовсім", NEG)

    els.append(text(W / 2, 400,
                    "Пастка: 31.5 ГБ/с — це і ×16 Gen 4 в ОДИН бік, і ×16 Gen 3 в ОБИДВА. Завжди питай, який це з трьох стовпчиків.",
                    size=12, color=INK))
    render(os.path.join(IMG, "bandwidth-chain.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 6 (вставка hist) — дві хвилі шинних воєн: хто зберіг сумісність
# ════════════════════════════════════════════════════════════════════════════
def fig_bus_wars_timeline():
    W, H = 980, 590
    els = [text(W / 2, 34, "Дві хвилі шинних воєн: що вижило й чому", size=17, bold=True)]

    def band(y_cap, cap, items, bw, gap, y_box, bh):
        out = [text(W / 2, y_cap, cap, size=13, bold=True, color=MUTED)]
        total = len(items) * bw + (len(items) - 1) * gap
        x0 = (W - total) / 2
        xs = []
        for i, (label, kind) in enumerate(items):
            x = x0 + i * (bw + gap)
            xs.append(x)
            stroke, fill = {"dead": (POS, LRED), "live": (FIELD, LGREEN),
                            "mid": (MUTED, FILL)}[kind]
            out.append(fitbox(x, y_box, bw, bh, label, size=12.5, pad=9,
                              fill=fill, stroke=stroke, color=INK, bold=False))
        for i in range(len(items) - 1):
            xa = xs[i] + bw + 3
            xb = xs[i + 1] - 3
            out.append(arrow(xa, y_box + bh / 2, xb, y_box + bh / 2, color=MUTED, sw=1.4))
        return out

    els += band(84,
                "Хвиля перша — паралельні шини персонального комп'ютера",
                [("1987\nMCA (IBM)\nрозрив + ліцензія", "dead"),
                 ("1988\nEISA («дев'ятка»)\nнадмножина ISA", "live"),
                 ("1992\nVL-Bus (VESA)\nприв'язана до 486", "dead"),
                 ("1992\nPCI 1.0 (Intel)\nсвій договір", "live"),
                 ("1996\nAGP (Intel)\nлатка для графіки", "mid")],
                bw=166, gap=22, y_box=104, bh=76)

    els.append(line(60, 236, W - 60, 236, color=MUTED, sw=1, dash="5,6"))

    els += band(272,
                "Хвиля друга — чим замінити паралельну шину",
                [("1998\nPCI-X\nIBM · HP · Compaq", "mid"),
                 ("1999\nInfiniBand\nнове ПЗ для всього", "dead"),
                 ("2001\nHyperTransport\nAMD, паралельна", "mid"),
                 ("2001\n3GIO (AWG)\nIntel + промоутери", "live"),
                 ("2002\nPCI Express\nстарий договір", "live"),
                 ("2004\nчипсети 915/925\nAGP прибрано", "live")],
                bw=140, gap=15, y_box=292, bh=76)

    # ── легенда: два рядки один під одним, щоб нічого не накладалося ──
    els.append(rect(120, 424, 26, 18, fill=LGREEN, stroke=FIELD, sw=1.6, rx=4))
    els.append(text(158, 438, "зберегло сумісність із уже наявним — вижило на масовому ринку",
                    size=12.5, color=INK, anchor="start"))
    els.append(rect(120, 456, 26, 18, fill=LRED, stroke=POS, sw=1.6, rx=4))
    els.append(text(158, 470, "вимагало розриву (нові плати або нове ПЗ) — лишилося в ніші",
                    size=12.5, color=INK, anchor="start"))
    els.append(rect(120, 488, 26, 18, fill=FILL, stroke=MUTED, sw=1.6, rx=4))
    els.append(text(158, 502, "проміжне: латка до чинної шини або вужча ніша",
                    size=12.5, color=INK, anchor="start"))

    els.append(text(W / 2, 546,
                    "Одна розвилка двічі: технічна перевага не рятувала того, хто вимагав переробки вже зробленого.",
                    size=13, color=INK, bold=True))
    render(os.path.join(IMG, "bus-wars-timeline.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 7 (вставка hist) — смуга росла, а місць на спільній шині меншало
# ════════════════════════════════════════════════════════════════════════════
def fig_shared_bus_wall():
    W, H = 960, 470
    els = [text(W / 2, 34, "Ціна кожного кроку за частотою — місця на спільній шині", size=17, bold=True)]

    panels = [
        (168, "PCI  33 МГц\n32 біти", "133 МБ/с", 4, "чотири-п'ять плат", "шина ще справді спільна", FIELD, LGREEN),
        (480, "PCI  66 МГц\n64 біти", "533 МБ/с", 2, "дві плати", "запас майже вичерпано", GOLD, LGOLD),
        (792, "PCI-X 133 МГц\n64 біти", "1064 МБ/с", 1, "фактично одна", "додаси другу — швидкість падає", POS, LRED),
    ]

    y_head, y_bw = 74, 148
    y_card_top, card_h = 176, 52
    y_bus = 258

    for cx, head, bw_lbl, n, cnt_lbl, note, col, fillc in panels:
        els.append(fitbox(cx - 130, y_head, 260, 50, head, size=13.5,
                          fill=fillc, stroke=col, color=INK, bold=True))
        els.append(text(cx, y_bw, bw_lbl, size=15, bold=True, color=col))

        # спільна лінія шини
        els.append(line(cx - 128, y_bus, cx + 128, y_bus, color=INK, sw=5))
        # плати-навантаження, що стоять на ній через відгалуження
        step = 56
        x0 = cx - (n - 1) * step / 2.0
        for i in range(n):
            xc = x0 + i * step
            els.append(rect(xc - 17, y_card_top, 34, card_h, fill=fillc, stroke=col, sw=1.6, rx=3))
            els.append(line(xc, y_card_top + card_h, xc, y_bus, color=col, sw=2.2))
        els.append(text(cx, y_bus + 30, cnt_lbl, size=13, bold=True, color=INK))
        els.append(text(cx, y_bus + 52, note, size=12, color=MUTED))

    els.append(line(60, 348, W - 60, 348, color=MUTED, sw=1, dash="5,6"))
    els.append(text(W / 2, 382,
                    "Кожне навантаження додає ємність, кожне відгалуження — відбиття;",
                    size=13, color=INK))
    els.append(text(W / 2, 406,
                    "тому вища частота купується меншою кількістю пристроїв на сегменті.",
                    size=13, color=INK))
    els.append(text(W / 2, 440,
                    "У кінці цієї дороги «спільна шина» обслуговує один пристрій — тобто перестає бути шиною.",
                    size=13, color=POS, bold=True))
    render(os.path.join(IMG, "shared-bus-wall.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 8 (вставка proj) — з чого складається адреса ECAM
# ════════════════════════════════════════════════════════════════════════════
def fig_ecam_address():
    W, H = 980, 410
    els = [text(W / 2, 32, "Адреса конфігураційного слова: координата лежить у розрядах",
                size=16, bold=True)]

    x0, bar_y, bar_h = 70, 92, 66
    # (мітка, кількість бітів, діапазон розрядів, зсув, скільки штук, колір, заливка)
    segs = [("шина",     8, "27:20", "« 20", "256 шин",      POS,   LRED),
            ("пристрій", 5, "19:15", "« 15", "32 пристрої",  FIELD, LGREEN),
            ("функція",  3, "14:12", "« 12", "8 функцій",    NEG,   LBLUE),
            ("зміщення", 12, "11:0", "+ off", "4096 байтів", MUTED, FILL)]
    px_per_bit = 30.0

    x = x0
    for name, bits, rng, sh, cnt, col, fillc in segs:
        w = bits * px_per_bit
        cx = x + w / 2
        els.append(text(cx, bar_y - 14, rng, size=11.5, color=MUTED, bold=True))
        els.append(fitbox(x, bar_y, w, bar_h,
                          "%s\n%d бітів" % (name, bits), size=12.5,
                          fill=fillc, stroke=col, color=col, bold=True))
        els.append(text(cx, bar_y + bar_h + 26, sh, size=13, color=col, bold=True))
        els.append(text(cx, bar_y + bar_h + 50, cnt, size=11.5, color=MUTED))
        x += w

    els.append(line(x0, bar_y + bar_h + 68, x, bar_y + bar_h + 68, color=MUTED, sw=1.2))
    els.append(text(W / 2, bar_y + bar_h + 90,
                    "усього 28 бітів  →  вікно ECAM рівно 2²⁸ = 256 МіБ на сегмент",
                    size=13, color=INK, bold=True))

    ey = 296
    els.append(rect(x0, ey, x - x0, 74, fill="#f7f9fb", stroke=MUTED, sw=1.2))
    els.append(text(x0 + 22, ey + 28, "приклад: BAR0 функції 03:00.0 — зміщення 0x10",
                    size=12.5, color=INK, anchor="start", bold=True))
    els.append(text(x0 + 22, ey + 56,
                    "адреса = база + (0x03 « 20) + (0 « 15) + (0 « 12) + 0x10 = база + 0x300010",
                    size=12.5, color=INK, anchor="start"))
    render(os.path.join(IMG, "ecam-address.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 9 (вставка proj) — номери шин: підлегла одразу, гранична — на поверненні
# ════════════════════════════════════════════════════════════════════════════
def fig_bus_numbering():
    W, H = 1000, 566
    els = [text(W / 2, 32, "Номери шин: підлегла відома одразу, гранична — аж на зворотному шляху",
                size=16, bold=True)]

    def bus(y, xa, xb, label):
        return [line(xa, y, xb, y, color=MUTED, sw=2.6),
                text(xa - 8, y + 4, label, size=11.5, color=MUTED, anchor="end", bold=True)]

    def drop(x, y1, y2):
        return line(x, y1, x, y2, color=MUTED, sw=1.4)

    def bridge(x, y, w, h, title, nums, col, fillc):
        return fitbox(x, y, w, h, title + "\n" + nums, size=11.5,
                      fill=fillc, stroke=col, color=col, bold=True)

    # корінь
    els.append(fitbox(350, 48, 300, 44, "кореневий комплекс", size=13,
                      fill=FILL, stroke=LINE, bold=True))
    els.append(drop(500, 92, 118))
    els += bus(118, 220, 790, "шина 0")

    # ── ліва гілка: кореневий порт → комутатор → два порти → два пристрої ──
    els.append(drop(315, 118, 140))
    els.append(bridge(200, 140, 230, 56, "міст 00:01.0",
                      "перв. 0 · підл. 1 · гран. 4", POS, LRED))
    els.append(drop(315, 196, 222))
    els += bus(222, 200, 430, "шина 1")

    els.append(drop(315, 222, 244))
    els.append(bridge(180, 244, 270, 56, "міст 01:00.0 — комутатор",
                      "перв. 1 · підл. 2 · гран. 4", POS, LRED))
    els.append(drop(315, 300, 326))
    els += bus(326, 110, 500, "шина 2")

    els.append(drop(195, 326, 348))
    els.append(bridge(90, 348, 210, 56, "міст 02:00.0",
                      "перв. 2 · підл. 3 · гран. 3", POS, LRED))
    els.append(drop(435, 326, 348))
    els.append(bridge(330, 348, 210, 56, "міст 02:01.0",
                      "перв. 2 · підл. 4 · гран. 4", POS, LRED))

    els.append(drop(195, 404, 430))
    els += bus(430, 110, 280, "шина 3")
    els.append(drop(435, 404, 430))
    els += bus(430, 350, 520, "шина 4")

    els.append(drop(195, 430, 452))
    els.append(fitbox(90, 452, 210, 46, "03:00.0 — NVMe", size=12,
                      fill=LGREEN, stroke=FIELD, color=FIELD, bold=True))
    els.append(drop(435, 430, 452))
    els.append(fitbox(330, 452, 210, 46, "04:00.0 — мережа", size=12,
                      fill=LGREEN, stroke=FIELD, color=FIELD, bold=True))

    # ── права гілка: кореневий порт → відеокарта ──
    els.append(drop(755, 118, 140))
    els.append(bridge(640, 140, 230, 56, "міст 00:1c.0",
                      "перв. 0 · підл. 5 · гран. 5", POS, LRED))
    els.append(drop(755, 196, 222))
    els += bus(222, 640, 870, "шина 5")
    els.append(drop(755, 222, 244))
    els.append(fitbox(640, 244, 230, 46, "05:00.0 — відеокарта", size=12,
                      fill=LGREEN, stroke=FIELD, color=FIELD, bold=True))

    els.append(text(W / 2, 536,
                    "номери видано в порядку 1 → 2 → 3 → 4 → 5 (обхід у глибину); "
                    "«гран.» кожен міст дізнається лише повернувшись зі спуску",
                    size=12.5, color=INK))
    render(os.path.join(IMG, "bus-numbering.svg"), W, H, *els)


if __name__ == "__main__":
    fig_lanes_width()
    fig_edge_connector()
    fig_protocol_layers()
    fig_doubling_ladder()
    fig_bandwidth_chain()
    fig_bus_wars_timeline()
    fig_shared_bus_wall()
    fig_ecam_address()
    fig_bus_numbering()
    print("OK: figures written to", IMG)
