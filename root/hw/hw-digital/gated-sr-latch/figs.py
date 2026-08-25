# -*- coding: utf-8 -*-
# Фігури теми «Гейтована SR-засувка». svgkit імпортуємо, не переписуємо (§5 AUTHORING).
# Вивід — у ./img/, імена — slug без номерів. Після запуску: python ../../../../scripts/svgcheck.py . --min-font 8
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def andgate(x, y, w=54, h=44, label="&"):
    """Вентиль AND: пряма ліва межа, півколо праворуч."""
    r = h / 2.0
    bx = x + w - r
    d = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f '
         'A %.1f %.1f 0 0 1 %.1f %.1f L %.1f %.1f Z" '
         'fill="%s" stroke="%s" stroke-width="1.6"/>'
         % (x, y, bx, y, bx, y, r, r, bx, y + h, x, y + h, "#eef3ff", LINE))
    d += text(x + (w - r) / 2 + 4, y + h / 2 + 5, label, size=18, bold=True)
    return d


def norgate(x, y, w=58, h=44, label="≥1"):
    """Вентиль NOR: щит OR + бульбашка інверсії на виході (позначка NOR)."""
    d = ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f Q %.1f %.1f %.1f %.1f '
         'Q %.1f %.1f %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
         % (x, y, x + 14, y + h / 2, x, y + h,
            x + w * 0.72, y + h, x + w, y + h / 2,
            x + w * 0.72, y, x, y, "#fdf0ea", LINE))
    d += circle(x + w + 6, y + h / 2, 6, fill=BG, stroke=LINE, sw=1.6)
    d += text(x + w * 0.42, y + h / 2 + 5, label, size=13, bold=True)
    return d


def pin(x, y, s, size=13, color=INK, anchor="middle", bold=True):
    return text(x, y, s, size=size, color=color, anchor=anchor, bold=bold)


def bubble(cx, cy):
    return circle(cx, cy, 6, fill=BG, stroke=LINE, sw=1.6)


# ── Фігура 1: гейт-ворота перед SR-коміркою ────────────────────────────────
def fig_structure():
    W, H = 720, 380
    p = []
    # входи
    p.append(pin(40, 118, "S", size=16))
    p.append(pin(40, 300, "R", size=16))
    p.append(pin(40, 209, "EN", size=15, color=FIELD))
    # AND-ворота
    ax = 120
    p.append(andgate(ax, 96, label="&"))
    p.append(andgate(ax, 278, label="&"))
    # дроти до AND
    p.append(line(52, 118, ax, 118))            # S -> and1 верх
    p.append(line(52, 300, ax, 300))            # R -> and2 низ
    # EN у розгалуженні до обох AND
    p.append(line(64, 209, 90, 209, color=FIELD, sw=2))
    p.append(circle(90, 209, 3, fill=FIELD, stroke=FIELD, sw=1))
    p.append(line(90, 140, 90, 278, color=FIELD, sw=2))
    p.append(line(90, 140, ax, 140, color=FIELD, sw=2))    # EN -> and1 низ
    p.append(line(90, 278, ax, 278, color=FIELD, sw=2))    # EN -> and2 верх
    # NOR-комірка (два навхрест). Верхній NOR: входи y=107 (S′) і y=129 (від Q̄).
    # Нижній NOR: входи y=289 (R′) і y=311 (від Q).
    nx = 300
    a1out = ax + 54
    a2out = ax + 54
    p.append(line(a1out, 118, nx, 107))         # S' у верхній вхід верхнього NOR
    p.append(line(a2out, 300, nx, 311))         # R' у нижній вхід нижнього NOR
    p.append(text((a1out + nx) / 2, 100, "S′", size=12, color=MUTED))
    p.append(text((a2out + nx) / 2, 320, "R′", size=12, color=MUTED))
    p.append(norgate(nx, 96, label="≥1"))
    p.append(norgate(nx, 278, label="≥1"))
    n1out = nx + 58 + 12
    n2out = nx + 58 + 12
    # виходи
    p.append(line(n1out, 118, 640, 118))
    p.append(line(n2out, 300, 640, 300))
    p.append(pin(660, 123, "Q", size=16))
    p.append(text(662, 306, "Q̄", size=16, bold=True))
    # перехресні зв'язки (петля пам'яті)
    p.append(line(n1out, 118, 560, 118))
    p.append(line(560, 118, 560, 289))
    p.append(line(560, 289, nx, 289))          # Q -> верхній вхід нижнього NOR
    p.append(line(n2out, 300, 590, 300))
    p.append(line(590, 300, 590, 129))
    p.append(line(590, 129, nx, 129))          # Q̄ -> нижній вхід верхнього NOR
    # рамка «ворота» довкола AND
    p.append(rect(104, 74, 76, 262, fill="none", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(142, 66, "ворота", size=12, color=FIELD, bold=True))
    p.append(rect(286, 74, 190, 262, fill="none", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(381, 66, "SR-комірка", size=12, color=MUTED, bold=True))
    # підпис умови
    p.append(fitbox(150, 350, 460, 24,
                    "EN=1: ворота відкриті, S і R проходять   ·   EN=0: у комірку нулі, тримати",
                    size=13, fill="#f0fbf4", stroke=FIELD))
    render(os.path.join(OUT, 'gated-structure.svg'), W, H, *p)


# ── Фігура 2: вікно прозорості на часовій діаграмі ─────────────────────────
def fig_window():
    W, H = 720, 360
    p = []
    x0, x1 = 90, 690
    def lane(cy, label, col=INK):
        p.append(text(20, cy + 5, label, size=13, color=col, bold=True, anchor="start"))
        p.append(line(x0, cy, x1, cy, color="#d0d5db", sw=1))
    # рівні
    yEN, yD, yQ = 70, 175, 285
    amp = 34
    lane(yEN, "EN", FIELD)
    lane(yD, "S/R", INK)
    lane(yQ, "Q", NEG)

    # EN: два вікна високого рівня
    win = [(150, 300), (430, 560)]
    def wave(cy, segs, col):
        # segs: список (x, level) точок; будуємо ступінчасту лінію
        pts = []
        for i, (x, lv) in enumerate(segs):
            y = cy - amp if lv else cy
            if i > 0:
                px, plv = segs[i - 1]
                py = cy - amp if plv else cy
                pts.append((px, py, x, py))     # горизонталь
                pts.append((x, py, x, y))       # вертикаль
        d = []
        for (a, b, c, e) in pts:
            d.append(line(a, b, c, e, color=col, sw=2.4))
        return "".join(d)

    en_seg = [(x0, 0), (win[0][0], 0), (win[0][0], 1), (win[0][1], 1), (win[0][1], 0),
              (win[1][0], 0), (win[1][0], 1), (win[1][1], 1), (win[1][1], 0), (x1, 0)]
    p.append(wave(yEN, en_seg, FIELD))

    # затінити вікна прозорості
    for (a, b) in win:
        p.append('<rect x="%.1f" y="40" width="%.1f" height="270" fill="%s" opacity="0.08"/>'
                 % (a, b - a, FIELD))
        p.append(line(a, 40, a, 310, color=FIELD, sw=1, dash="4,4"))
        p.append(line(b, 40, b, 310, color=FIELD, sw=1, dash="4,4"))

    # вхід S/R: подія в 1-му вікні (набрати 1) і ключова подія в ЗАКРИТІЙ зоні (340..400)
    d_seg = [(x0, 0), (200, 0), (200, 1), (270, 1), (270, 0),      # 1-ше вікно: імпульс усередині
             (340, 0), (340, 1), (400, 1), (400, 0),               # закрита зона: вхід смикнувся
             (470, 0), (470, 1), (540, 1), (540, 0), (x1, 0)]      # 2-ге вікно: набрати 1
    p.append(wave(yD, d_seg, INK))

    # Q іде за входом ЛИШЕ у вікні; поза вікном заморожений
    p.append(line(x0, yQ, 200, yQ, color=NEG, sw=2.4))             # 0 до події у вікні
    p.append(line(200, yQ, 200, yQ - amp, color=NEG, sw=2.4))      # вхід=1 у вікні -> Q=1
    p.append(line(200, yQ - amp, 270, yQ - amp, color=NEG, sw=2.4))
    p.append(line(270, yQ - amp, 270, yQ, color=NEG, sw=2.4))      # вхід впав у вікні -> Q=0
    p.append(line(270, yQ, win[1][0], yQ, color=NEG, sw=2.4))      # закрито: тримає 0 (ігнорує 340..400!)
    p.append(line(win[1][0], yQ, 470, yQ, color=NEG, sw=2.4))      # 2-ге вікно, до події 0
    p.append(line(470, yQ, 470, yQ - amp, color=NEG, sw=2.4))      # вхід=1 -> Q=1
    p.append(line(470, yQ - amp, x1, yQ - amp, color=NEG, sw=2.4)) # вікно закрилось на 1 -> тримає 1

    # виноска на ключову подію: вхід смикнувся в закритій зоні, Q не зреагував
    p.append(text(365, yQ + 42, "вхід смикнувся,", size=11, color=POS, anchor="middle"))
    p.append(text(365, yQ + 57, "та EN=0 — Q не чує", size=11, color=POS, anchor="middle"))
    p.append(line(370, yD + 6, 370, yQ - 6, color=POS, sw=1.2, dash="3,3"))
    p.append(text(225, 32, "прозоро", size=11, color=FIELD, anchor="middle", bold=True))
    p.append(text(495, 32, "прозоро", size=11, color=FIELD, anchor="middle", bold=True))
    p.append(text(365, 32, "закрито", size=11, color=MUTED, anchor="middle", bold=True))
    p.append(text(625, 32, "закрито", size=11, color=MUTED, anchor="middle", bold=True))
    render(os.path.join(OUT, 'transparency-window.svg'), W, H, *p)


# ── Фігура 3: заборонений стан переживає гейтування ────────────────────────
def fig_forbidden():
    W, H = 700, 300
    p = []
    # два стани: D-латч (нема заборони) vs гейтована SR (заборона лишилась)
    p.append(text(W / 2, 30, "EN=1, і на входи подано S=1, R=1", size=14, bold=True))
    # ліворуч: гейтована SR
    lx = 60
    p.append(rect(lx, 60, 280, 200, fill="#fdf0ea", stroke=POS, sw=1.6, rx=10))
    p.append(text(lx + 140, 88, "Гейтована SR", size=14, bold=True, color=POS))
    p.append(text(lx + 140, 118, "S=1 і R=1 — незалежні", size=12))
    p.append(text(lx + 140, 142, "ворота відчинені (EN=1)", size=12, color=FIELD))
    p.append(text(lx + 140, 168, "→ обидва йдуть у комірку", size=12))
    p.append(text(lx + 140, 196, "Q = Q̄ = 0", size=15, bold=True, color=POS))
    p.append(text(lx + 140, 224, "ЗАБОРОНА лишилась", size=13, bold=True, color=POS))
    p.append(text(lx + 140, 246, "гейт керує КОЛИ, не ЩО", size=11, color=MUTED))
    # праворуч: D-латч
    rx = 380
    p.append(rect(rx, 60, 280, 200, fill="#f0fbf4", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(rx + 140, 88, "D-латч (для контрасту)", size=14, bold=True, color=FIELD))
    p.append(text(rx + 140, 118, "один вхід D, R=D̄", size=12))
    p.append(text(rx + 140, 142, "S і R завжди протилежні", size=12))
    p.append(text(rx + 140, 168, "→ S=R=1 неможливо в принципі", size=11))
    p.append(text(rx + 140, 196, "Q = D", size=15, bold=True, color=FIELD))
    p.append(text(rx + 140, 224, "заборони НЕМА", size=13, bold=True, color=FIELD))
    p.append(text(rx + 140, 246, "усунено інвертором на вході", size=11, color=MUTED))
    render(os.path.join(OUT, 'forbidden-survives.svg'), W, H, *p)


# ── Фігура 4: NAND-побудова (активно-низькі входи) ─────────────────────────
def fig_nand():
    W, H = 700, 340
    p = []
    def nand(x, y, w=56, h=44, label="&"):
        d = andgate(x, y, w=w, h=h, label=label)
        d += bubble(x + w + 6, y + h / 2)
        return d
    # входи
    p.append(pin(36, 96, "S", size=15))
    p.append(pin(36, 258, "R", size=15))
    p.append(pin(36, 177, "EN", size=14, color=FIELD))
    # 1-й ярус: два вхідні NAND (керовані EN)
    gx = 110
    p.append(nand(gx, 74, label="&"))
    p.append(nand(gx, 236, label="&"))
    p.append(line(48, 96, gx, 96))
    p.append(line(48, 258, gx, 258))
    # EN у обидва
    p.append(line(52, 177, 84, 177, color=FIELD, sw=2))
    p.append(circle(84, 177, 3, fill=FIELD, stroke=FIELD, sw=1))
    p.append(line(84, 118, 84, 258, color=FIELD, sw=2))
    p.append(line(84, 118, gx, 118, color=FIELD, sw=2))
    p.append(line(84, 258, gx, 258, color=FIELD, sw=2))
    # 2-й ярус: комірка з двох NAND навхрест
    cx = 320
    g1out = gx + 56 + 12
    g2out = gx + 56 + 12
    p.append(line(g1out, 96, cx, 96))
    p.append(line(g2out, 258, cx, 258))
    p.append(nand(cx, 74, label="&"))
    p.append(nand(cx, 236, label="&"))
    c1out = cx + 56 + 12
    c2out = cx + 56 + 12
    p.append(line(c1out, 96, 640, 96))
    p.append(line(c2out, 258, 640, 258))
    p.append(pin(660, 101, "Q", size=15))
    p.append(text(662, 263, "Q̄", size=15, bold=True))
    # перехресні
    p.append(line(c1out, 96, 560, 96))
    p.append(line(560, 96, 560, 220))
    p.append(line(560, 220, cx - 4, 220))
    p.append(line(c2out, 258, 590, 258))
    p.append(line(590, 258, 590, 112))
    p.append(line(590, 112, cx - 4, 112))
    # підписи
    p.append(text(gx + 28, 66, "керовані EN", size=11, color=FIELD))
    p.append(text(cx + 28, 66, "петля пам'яті", size=11, color=MUTED))
    p.append(fitbox(120, 306, 460, 24,
                    "EN=0 → виходи воріт = 1 (бездіяльно для NAND) → комірка тримає",
                    size=12, fill="#f0fbf4", stroke=FIELD))
    render(os.path.join(OUT, 'nand-gated.svg'), W, H, *p)


if __name__ == '__main__':
    fig_structure()
    fig_window()
    fig_forbidden()
    fig_nand()
    print("figs written to", OUT)
