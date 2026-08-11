# -*- coding: utf-8 -*-
"""Фігури для статті «KY-010 — оптичний переривач». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_slot():
    """Розтин щілини: ІЧ-діод ← промінь → фототранзистор, пелюстка ріже промінь."""
    W, H = 720, 440
    p = []
    p.append(text(W / 2, 30, "Щілина переривача: промінь і пелюстка, що його ріже", size=17, bold=True))

    # Корпус U-подібний: дві «щоки» й дно
    body = "#2b2b2b"
    # ліва щока (діод)
    p.append(rect(90, 90, 90, 250, fill=body, stroke=INK, sw=2, rx=8))
    # права щока (транзистор)
    p.append(rect(360, 90, 90, 250, fill=body, stroke=INK, sw=2, rx=8))
    # дно
    p.append(rect(90, 300, 360, 40, fill=body, stroke=INK, sw=2, rx=8))

    # ІЧ-діод у лівій щоці
    p.append(circle(150, 200, 20, fill="#7a1f14", stroke=POS, sw=2))
    p.append(text(150, 205, "ІЧ", size=13, color="#ffffff", bold=True))
    tb, tw, th = textbox(135, 360, "ІЧ-світлодіод\n(≈950 нм)", size=12, color=INK)
    p.append(tb)

    # фототранзистор у правій щоці
    p.append(circle(390, 200, 20, fill="#12303a", stroke=NEG, sw=2))
    p.append(text(390, 205, "ФТ", size=13, color="#ffffff", bold=True))
    tb, tw, th = textbox(405, 360, "фототранзистор\n(кремній)", size=12, color=INK)
    p.append(tb)

    # промінь: пунктирні лінії від діода до транзистора
    for dy in (-8, 0, 8):
        p.append(line(170, 200 + dy, 370, 200 + dy, color=FIELD, sw=2, dash="6 5"))
    p.append(arrow(210, 200, 360, 200, color=FIELD, sw=2))

    # пелюстка (vane) заходить згори в щілину — ріже промінь
    p.append(rect(258, 60, 26, 150, fill="#b8860b", stroke=INK, sw=2, rx=3))
    tb, tw, th = textbox(270, 250, "пелюстка / край\nдиска (ріже промінь)", size=12, color=INK, fill="#fdf3d8")
    p.append(tb)

    # підпис щілини знизу праворуч
    p.append(line(180, 330, 360, 330, color=MUTED, sw=1, dash="3 3"))
    p.append(text(270, 393, "щілина ~5 мм — сюди проходить об'єкт", size=12, color=MUTED))

    # праворуч — стан виходу двома клітинами
    tb, tw, th = textbox(600, 120, "Промінь ПРОХОДИТЬ\nтранзистор відкритий\nструм тече", size=13, color=INK, fill="#eafaf0")
    p.append(tb)
    tb, tw, th = textbox(600, 250, "Промінь ПЕРЕКРИТО\nтранзистор закритий\nструму нема", size=13, color=INK, fill="#fdecea")
    p.append(tb)

    render(os.path.join(IMG, 'slot.svg'), W, H, *p)


def fig_schematic():
    """Принципова схема модуля KY-010: 33Ω+діод, фототранзистор+1k, 3 піни."""
    W, H = 760, 440
    p = []
    p.append(text(W / 2, 30, "Принципова схема модуля KY-010", size=17, bold=True))

    # рейки живлення
    vcc_y, gnd_y = 80, 380
    p.append(line(70, vcc_y, 690, vcc_y, color=POS, sw=2.5))
    p.append(text(60, vcc_y + 5, "+", size=20, color=POS, bold=True, anchor="end"))
    p.append(text(120, vcc_y - 10, "VCC (3.3–5 В)", size=13, color=POS, bold=True, anchor="start"))
    p.append(line(70, gnd_y, 690, gnd_y, color=NEG, sw=2.5))
    p.append(text(60, gnd_y + 5, "−", size=20, color=NEG, bold=True, anchor="end"))
    p.append(text(120, gnd_y + 22, "GND", size=13, color=NEG, bold=True, anchor="start"))

    # ── ліва вітка: 33 Ω + ІЧ-діод ──
    xL = 200
    p.append(line(xL, vcc_y, xL, 130, color=LINE, sw=2))
    p.append(rect(xL - 22, 130, 44, 46, fill=FILL, stroke=LINE, sw=1.5))
    p.append(text(xL, 158, "33 Ω", size=12, bold=True))
    p.append(line(xL, 176, xL, 210, color=LINE, sw=2))
    # діод (трикутник + риска)
    p.append('<path d="M%d %d L%d %d L%d %d Z" fill="#7a1f14" stroke="%s" stroke-width="1.5"/>' %
             (xL - 14, 210, xL + 14, 210, xL, 236, POS))
    p.append(line(xL - 14, 236, xL + 14, 236, color=POS, sw=2.5))
    # стрілки випромінювання
    p.append(arrow(xL + 16, 214, xL + 40, 206, color=FIELD, sw=1.6))
    p.append(arrow(xL + 16, 226, xL + 40, 220, color=FIELD, sw=1.6))
    p.append(line(xL, 236, xL, gnd_y, color=LINE, sw=2))
    tb, tw, th = textbox(xL - 92, 223, "ІЧ-\nсвітлодіод", size=12, color=INK)
    p.append(tb)

    # ── права вітка: фототранзистор + навантаження 1k ──
    xR = 500
    # навантаження 1k від VCC до вузла-виходу
    p.append(line(xR, vcc_y, xR, 150, color=LINE, sw=2))
    p.append(rect(xR - 22, 150, 44, 46, fill=FILL, stroke=LINE, sw=1.5))
    p.append(text(xR, 178, "1 kΩ", size=12, bold=True))
    node_y = 230
    p.append(line(xR, 196, xR, node_y, color=LINE, sw=2))
    # вузол-вихід
    p.append(circle(xR, node_y, 4, fill=INK, stroke=INK))
    # фототранзистор: колектор до вузла, емітер до GND
    p.append(circle(xR, 290, 26, fill="none", stroke=NEG, sw=2))
    p.append(line(xR, node_y, xR, 264, color=LINE, sw=2))          # колектор
    p.append(line(xR, 316, xR, gnd_y, color=LINE, sw=2))           # емітер
    p.append(line(xR - 16, 278, xR - 16, 302, color=NEG, sw=2.5))  # база-планка
    p.append(line(xR - 16, 290, xR - 4, 284, color=NEG, sw=2))     # к колектору
    p.append(line(xR - 16, 290, xR - 4, 296, color=NEG, sw=2))     # к емітеру
    # промінь у базу
    p.append(arrow(xR - 46, 282, xR - 20, 288, color=FIELD, sw=1.6))
    p.append(arrow(xR - 46, 294, xR - 20, 292, color=FIELD, sw=1.6))
    tb, tw, th = textbox(xR + 78, 290, "фото-\nтранзистор", size=12, color=INK)
    p.append(tb)

    # вихід S від вузла праворуч
    p.append(line(xR, node_y, 660, node_y, color=LINE, sw=2))
    p.append(circle(660, node_y, 5, fill="#ffffff", stroke=LINE, sw=2))
    p.append(text(676, node_y + 5, "S", size=15, bold=True, anchor="start"))
    tb, tw, th = textbox(620, 175, "вихід: напруга\nна вузлі", size=11, color=MUTED, fill="#f0f2f5")
    p.append(tb)

    render(os.path.join(IMG, 'schematic.svg'), W, H, *p)


def fig_wiring():
    """Розводка пін-у-пін: три піни модуля → плата МК."""
    W, H = 720, 380
    p = []
    p.append(text(W / 2, 30, "Підключення KY-010 до мікроконтролера", size=17, bold=True))

    # модуль ліворуч (піни на ПРАВОМУ краю, підписи всередині ліворуч від них)
    p.append(rect(60, 90, 200, 180, fill="#1f6feb", stroke=INK, sw=2, rx=10))
    p.append(text(150, 116, "KY-010", size=16, color="#ffffff", bold=True))
    p.append(rect(80, 135, 56, 56, fill="#0b1f3a", stroke="#ffffff", sw=1.5, rx=4))
    p.append(text(108, 170, "▯", size=22, color="#9fc5ff"))
    pins = [("S", "Signal", 150, FIELD), ("+", "VCC", 195, POS), ("−", "GND", 240, NEG)]
    for name, lbl, y, col in pins:
        p.append(text(210, y + 4, lbl, size=11, color="#ffffff", anchor="end"))
        p.append(circle(260, y, 8, fill="#ffffff", stroke=col, sw=2))
        p.append(text(260, y + 4, name, size=12, color=col, bold=True))

    # плата МК праворуч (піни на ЛІВОМУ краю, підписи всередині праворуч від них)
    p.append(rect(470, 90, 200, 180, fill="#2f2f2f", stroke=INK, sw=2, rx=10))
    p.append(text(570, 116, "Плата МК", size=15, color="#ffffff", bold=True))
    mpins = [("GPIO", 150, FIELD), ("3V3 / 5V", 195, POS), ("GND", 240, NEG)]
    for name, y, col in mpins:
        p.append(circle(470, y, 8, fill="#ffffff", stroke=col, sw=2))
        p.append(text(486, y + 4, name, size=11, color="#ffffff", anchor="start"))

    # дроти — L-подібні лінії від правого піна модуля (x=268) до лівого піна МК (x=462)
    def wire(y, col):
        return line(268, y, 462, y, color=col, sw=2.5)
    p.append(wire(150, FIELD))
    p.append(wire(195, POS))
    p.append(wire(240, NEG))

    # підпис-нота
    tb, tw, th = textbox(360, 335, "S → цифровий вхід (краще з підтримкою переривання);  живлення 3.3 В на 3.3-В платах",
                         size=12, color=INK, fill="#f0f2f5")
    p.append(tb)

    render(os.path.join(IMG, 'wiring.svg'), W, H, *p)


def fig_edge_timing():
    """Часова діаграма: плавний схил виходу з дрижанням на порозі; мертвий час
    гасить кратні фронти; період T між зарахованими фронтами → швидкість."""
    W, H = 760, 470
    p = []
    p.append(text(W / 2, 28, "Плавний схил, дрижання на порозі й мертвий час", size=17, bold=True))

    x0, x1 = 90, 690           # межі осі часу
    base = 300                 # рівень LOW (низ сигналу)
    top = 150                  # рівень HIGH (верх сигналу)
    thr = (base + top) / 2     # поріг мікроконтролера

    # осі
    p.append(line(x0, base + 40, x1, base + 40, color=MUTED, sw=1.5))   # вісь часу
    p.append(arrow(x1 - 4, base + 40, x1 + 8, base + 40, color=MUTED, sw=1.5))
    p.append(text(x1 + 10, base + 45, "t", size=14, color=MUTED, anchor="start", italic=True))
    p.append(line(x0, top - 30, x0, base + 40, color=MUTED, sw=1.5))    # вісь напруги
    p.append(text(x0 - 8, top - 15, "напруга S", size=12, color=MUTED, anchor="end"))

    # лінія порога
    p.append(line(x0, thr, x1, thr, color=POS, sw=1.3, dash="7 5"))
    p.append(text(x1 - 4, thr - 8, "поріг МК", size=12, color=POS, anchor="end"))

    # рівні HIGH/LOW підписи
    p.append(text(x0 - 8, top + 4, "HIGH", size=11, color=MUTED, anchor="end"))
    p.append(text(x0 - 8, base + 4, "LOW", size=11, color=MUTED, anchor="end"))

    # ── сам сигнал: LOW → плавний схил угору з «зубчиками» біля порога → HIGH → плавно вниз ──
    # (край диска повільно наповзає: транзистор поступово закривається, напруга повзе вгору;
    #  на порозі — оптичне дрижання, кілька дрібних перетинів; далі стабільно HIGH)
    def poly(pts, color, sw):
        d = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)

    sig = [
        (x0, base), (150, base),            # спокій: LOW (щілина вільна)
        (185, base - 20),                    # схил починається
        (205, thr + 14), (214, thr - 6),     # дрижання: вгору-вниз коло порога
        (223, thr + 10), (232, thr - 4),
        (245, thr + 16),
        (270, top + 10), (330, top),         # вийшов на стабільний HIGH (перекрито)
        (430, top),                          # тримається HIGH
        (470, top + 22),                     # схил униз починається (край виходить)
        (492, thr - 12), (501, thr + 6),     # дрижання на спаді
        (510, thr - 10), (519, thr + 4),
        (545, base - 12), (590, base),       # назад у LOW
        (x1 - 10, base),
    ]
    p.append(poly(sig, NEG, 2.6))

    # позначки зарахованих фронтів: перший перетин порога вгору (t1) і на наступному оберті (t2).
    # Тут малюємо один період: показуємо, що рахуємо ПЕРШИЙ перетин, а дрижання після нього — ігнор.
    t1 = 205
    p.append(line(t1, top - 30, t1, base + 40, color=INK, sw=1.4, dash="2 4"))
    p.append(circle(t1, thr, 5, fill=INK, stroke=INK))
    p.append(text(t1, top - 36, "зарахований фронт", size=11, color=INK))

    # зона мертвого часу після t1 — заштрихована, тут фронти НЕ рахуються
    guard_end = 265
    p.append(rect(t1, top - 4, guard_end - t1, base + 40 - (top - 4),
                  fill="#fff4d6", stroke="none", sw=0))
    p.append(line(t1, base + 40, guard_end, base + 40, color="#b8860b", sw=3))
    tb, tw, th = textbox((t1 + guard_end) / 2, base + 70,
                         "мертвий час:\nфронти ігноруються", size=11, color="#7a5c00", fill="#fff4d6")
    p.append(tb)
    # повторно провести сигнал поверх заливки (щоб лінія не ховалась під прямокутником)
    p.append(poly(sig, NEG, 2.6))
    # і фронт-маркер поверх
    p.append(line(t1, top - 30, t1, base + 40, color=INK, sw=1.4, dash="2 4"))
    p.append(circle(t1, thr, 5, fill=INK, stroke=INK))

    # стрілка періоду T (від цього фронту до наступного оберту — умовно за межу кадру)
    p.append(text(360, base + 100, "T між сусідніми фронтами → миттєва швидкість = 60 / (N · T)",
                  size=12, color=INK))

    render(os.path.join(IMG, 'edge-timing.svg'), W, H, *p)


if __name__ == '__main__':
    fig_slot()
    fig_schematic()
    fig_wiring()
    fig_edge_timing()
    print("OK: slot.svg, schematic.svg, wiring.svg, edge-timing.svg")
