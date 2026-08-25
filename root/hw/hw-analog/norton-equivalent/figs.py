# -*- coding: utf-8 -*-
"""Фігури до статті «Еквівалент Нортона» (тема norton-equivalent, галузь analog).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Генерує три фігури:
  short-circuit.svg — як дістати I_n: замкнути клеми, вимірюваний/рахований струм КЗ;
  three-numbers.svg — трикутник V_oc · I_кз · R: будь-які два задають третій (закон Ома);
  worked.svg        — наскрізний приклад: коло → I_n (КЗ) і R_n (згортання) → еквівалент.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: I_n — струм короткого замикання ────────────────────────────────
def fig_short_circuit():
    W, H = 760, 360
    P = []
    midy = 180

    # чорна скринька (лінійна мережа)
    bx, by, bw, bh = 50, midy - 60, 180, 120
    P.append(rect(bx, by, bw, bh, fill="#eef2fb", stroke=NEG, sw=2, rx=10))
    P.append(mtext(bx + bw / 2, midy - 6, "лінійна\nмережа", size=14, bold=True))
    P.append(text(bx + bw / 2, midy + 30, "(будь-яка)", size=11, color=MUTED))

    # дві клеми
    tx_top = bx + bw + 110
    yA, yB = midy - 38, midy + 38
    P.append(line(bx + bw, yA, tx_top, yA, color=INK, sw=2))
    P.append(line(bx + bw, yB, tx_top, yB, color=INK, sw=2))
    P.append(circle(tx_top, yA, 4.5, fill=INK, stroke=INK))
    P.append(circle(tx_top, yB, 4.5, fill=INK, stroke=INK))
    P.append(text(tx_top + 14, yA - 6, "A", size=13, bold=True, anchor="start"))
    P.append(text(tx_top + 14, yB + 16, "B", size=13, bold=True, anchor="start"))

    # перемичка короткого замикання (товстий провід A→B)
    P.append(line(tx_top, yA, tx_top, yB, color=POS, sw=4))
    P.append(mtext(tx_top + 96, midy - 10, "замкнено\nнавпрямки\n(дротом)", size=12, color=POS, bold=True))

    # стрілка струму КЗ через перемичку
    P.append(arrow(tx_top - 2, yA + 12, tx_top - 2, yB - 12, color=POS, sw=2.4))
    P.append(text(tx_top - 14, midy + 4, "I_n", size=16, color=POS, bold=True, anchor="end"))

    # нижня панель-висновок
    fy = 290
    P.append(rect(40, fy, W - 80, 50, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    P.append(text(W / 2, fy + 20, "I_n — струм, що тече через ЗАМКНЕНІ клеми (коротке замикання).", size=12, bold=True))
    P.append(text(W / 2, fy + 39, "Для слабких джерел міряють амперметром; для потужних — рахують (замикати небезпечно).", size=11, color=MUTED))

    render(os.path.join(IMG, "short-circuit.svg"), W, H, *P,
           title="I_n: струм короткого замикання")


# ── Фігура 2: трикутник трьох чисел V_oc · I_кз · R ──────────────────────────
def fig_three_numbers():
    W, H = 720, 430
    P = []
    cx = W / 2
    # вершини трикутника
    ax, ay = cx, 92            # верх: V_oc
    bxv, byv = 150, 320        # ліво: I_кз
    cxv, cyv = W - 150, 320    # право: R

    # ребра
    P.append(line(ax, ay, bxv, byv, color=MUTED, sw=1.6))
    P.append(line(ax, ay, cxv, cyv, color=MUTED, sw=1.6))
    P.append(line(bxv, byv, cxv, cyv, color=MUTED, sw=1.6))

    # вершини — рамки
    def node(cx0, cy0, label, sub, col):
        b, w, h = textbox(cx0, cy0, label, size=16, bold=True, color=col,
                          fill=BG, stroke=col, sw=2, pad=12, min_w=120)
        P.append(b)
        P.append(text(cx0, cy0 + h / 2 + 18, sub, size=11, color=MUTED))

    node(ax, ay, "V_oc", "напруга холостого ходу", NEG)
    node(bxv, byv, "I_кз", "струм короткого замикання", POS)
    node(cxv, cyv, "R", "опір мережі (R_n = R_th)", FIELD)

    # підписи зв'язків на ребрах (закон Ома по колу)
    P.append(text((ax + bxv) / 2 - 36, (ay + byv) / 2, "I_кз = V_oc / R", size=13, bold=True, color=INK, anchor="middle"))
    P.append(text((ax + cxv) / 2 + 36, (ay + cyv) / 2, "V_oc = I_кз · R", size=13, bold=True, color=INK, anchor="middle"))
    P.append(text(cx, byv + 26, "R = V_oc / I_кз", size=13, bold=True, color=INK, anchor="middle"))

    # центральний підпис-висновок
    P.append(mtext(cx, 232, "Будь-які ДВА числа\nзадають третє.", size=15, bold=True, color=INK))

    render(os.path.join(IMG, "three-numbers.svg"), W, H, *P,
           title="Три числа — один закон Ома")


# ── Фігура 3: наскрізний приклад ─────────────────────────────────────────────
def fig_worked():
    W, H = 820, 470
    P = []

    # ── ліва частина: коло ──
    # джерело 12 В
    sx, sy = 70, 120
    P.append(circle(sx, sy + 80, 22, fill=BG, stroke=INK, sw=2))
    P.append(text(sx, sy + 86, "12 В", size=12, bold=True))
    # вертикаль угору від джерела до вузла зліва
    nodeL_y = sy
    P.append(line(sx, sy + 58, sx, nodeL_y, color=INK, sw=2))
    # R1 горизонтально до вузла A
    Ax = sx + 230
    P.append(rect(sx + 60, nodeL_y - 12, 90, 24, fill=BG, stroke=INK, sw=1.8, rx=4))
    P.append(text(sx + 105, nodeL_y + 5, "R₁ = 6 Ω", size=12, bold=True))
    P.append(line(sx, nodeL_y, sx + 60, nodeL_y, color=INK, sw=2))
    P.append(line(sx + 150, nodeL_y, Ax, nodeL_y, color=INK, sw=2))
    # вузол A
    P.append(circle(Ax, nodeL_y, 4.5, fill=INK, stroke=INK))
    P.append(text(Ax + 12, nodeL_y - 8, "A", size=13, bold=True, anchor="start"))
    # R2 вниз від A до землі
    P.append(rect(Ax - 12, nodeL_y + 30, 24, 80, fill=BG, stroke=INK, sw=1.8, rx=4))
    P.append(mtext(Ax + 40, nodeL_y + 74, "R₂ =\n3 Ω", size=12, bold=True))
    P.append(line(Ax, nodeL_y, Ax, nodeL_y + 30, color=INK, sw=2))
    # низ (земля) від джерела до низу R2
    gy = sy + 200
    P.append(line(sx, sy + 102, sx, gy, color=INK, sw=2))
    P.append(line(sx, gy, Ax, gy, color=INK, sw=2))
    P.append(line(Ax, nodeL_y + 110, Ax, gy, color=INK, sw=2))
    # клеми праворуч від A та землі
    Tx = Ax + 70
    P.append(line(Ax, nodeL_y, Tx, nodeL_y, color=INK, sw=2))
    P.append(line(Ax, gy, Tx, gy, color=INK, sw=2))
    P.append(circle(Tx, nodeL_y, 4.5, fill=INK, stroke=INK))
    P.append(circle(Tx, gy, 4.5, fill=INK, stroke=INK))
    P.append(text(Tx + 12, nodeL_y - 6, "клеми", size=11, color=MUTED, anchor="start"))
    # символ землі
    P.append(line(sx - 10, gy, sx + 10, gy, color=INK, sw=2))
    P.append(line(sx - 6, gy + 5, sx + 6, gy + 5, color=INK, sw=1.6))
    P.append(line(sx - 2, gy + 10, sx + 2, gy + 10, color=INK, sw=1.4))

    # ── права частина: викладка й еквівалент ──
    px0 = 470
    P.append(rect(px0, 78, 320, 250, fill=FILL, stroke=MUTED, sw=1.5, rx=10))
    P.append(text(px0 + 160, 104, "Еквівалент Нортона", size=14, bold=True))
    P.append(text(px0 + 18, 136, "I_n = струм КЗ через клеми A–землю:", size=11, anchor="start"))
    P.append(text(px0 + 30, 158, "R₂ закорочена → I_n = 12 / R₁", size=11, anchor="start", color=POS))
    P.append(text(px0 + 30, 178, "= 12 / 6 = 2 А", size=12, anchor="start", color=POS, bold=True))
    P.append(line(px0 + 18, 192, px0 + 302, 192, color="#e0e3e6", sw=1.2))
    P.append(text(px0 + 18, 214, "R_n = R_th (джерело → КЗ):", size=11, anchor="start"))
    P.append(text(px0 + 30, 234, "R₁ ∥ R₂ = 6∥3 = 2 Ω", size=12, anchor="start", color=FIELD, bold=True))
    P.append(line(px0 + 18, 248, px0 + 302, 248, color="#e0e3e6", sw=1.2))
    P.append(text(px0 + 18, 270, "Перевірка: V_oc = I_n·R_n", size=11, anchor="start"))
    P.append(text(px0 + 30, 290, "= 2·2 = 4 В = напруга х.х.  ✓", size=12, anchor="start", bold=True))
    P.append(text(px0 + 160, 314, "Нортон:  2 А  ∥  2 Ω", size=13, bold=True, color=POS))

    # ── низ: підсумкова схема еквівалента (джерело струму ∥ R) ──
    ey = 410
    P.append(text(W / 2, 366, "Готовий еквівалент Нортона:", size=12, bold=True))
    # джерело струму
    ix = 300
    P.append(circle(ix, ey, 24, fill=BG, stroke=POS, sw=2))
    P.append(arrow(ix, ey + 14, ix, ey - 14, color=POS, sw=2))
    P.append(text(ix - 38, ey + 4, "2 А", size=12, color=POS, bold=True, anchor="end"))
    # паралельний R
    rxp = ix + 120
    P.append(rect(rxp - 12, ey - 26, 24, 52, fill=BG, stroke=FIELD, sw=2, rx=4))
    P.append(text(rxp + 38, ey + 4, "2 Ω", size=12, color=FIELD, bold=True, anchor="start"))
    # верх і низ — паралель
    P.append(line(ix, ey - 24, ix, ey - 40, color=INK, sw=2))
    P.append(line(rxp, ey - 26, rxp, ey - 40, color=INK, sw=2))
    P.append(line(ix, ey - 40, rxp, ey - 40, color=INK, sw=2))
    P.append(line(ix, ey + 24, ix, ey + 40, color=INK, sw=2))
    P.append(line(rxp, ey + 26, rxp, ey + 40, color=INK, sw=2))
    P.append(line(ix, ey + 40, rxp, ey + 40, color=INK, sw=2))
    # клеми еквівалента
    P.append(line(rxp, ey - 40, rxp + 50, ey - 40, color=INK, sw=2))
    P.append(line(rxp, ey + 40, rxp + 50, ey + 40, color=INK, sw=2))
    P.append(circle(rxp + 50, ey - 40, 4.5, fill=INK, stroke=INK))
    P.append(circle(rxp + 50, ey + 40, 4.5, fill=INK, stroke=INK))

    render(os.path.join(IMG, "worked.svg"), W, H, *P,
           title="Наскрізний приклад: коло → еквівалент Нортона")


# ── Фігура 4 (вставка proj): дві точки → I_n екстраполяцією, без КЗ ───────────
def fig_extrapolate():
    W, H = 760, 450
    P = []
    ox, oy = 120, 360            # початок осей
    ax_w, ax_h = 540, 270
    P.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))            # вісь I
    P.append(arrow(ox + ax_w - 2, oy, ox + ax_w + 28, oy, color=INK, sw=2))
    P.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))            # вісь V
    P.append(arrow(ox, oy - ax_h + 2, ox, oy - ax_h - 28, color=INK, sw=2))
    P.append(text(ox + ax_w + 30, oy + 6, "I", size=16, bold=True, anchor="start"))
    P.append(text(ox, oy - ax_h - 34, "V", size=16, bold=True))

    # пряма V = V_oc − I·R від (0, V_oc) до (I_n, 0)
    V_oc_y = oy - ax_h + 26
    I_n_x = ox + ax_w - 70
    P.append(line(ox, V_oc_y, I_n_x, oy, color=NEG, sw=2.6))

    def on_line(t):
        return ox + t * (I_n_x - ox), V_oc_y + t * (oy - V_oc_y)

    # дві виміряні точки (у безпечній середині)
    p1 = on_line(0.30)
    p2 = on_line(0.62)
    for (px, py), lab in ((p1, "(I₁, V₁)"), (p2, "(I₂, V₂)")):
        P.append(circle(px, py, 6, fill=FIELD, stroke=INK, sw=1.6))
        P.append(text(px + 13, py - 9, lab, size=13, anchor="start", bold=True))
    # підпис «тут безпечно міряємо» — нижче-ліворуч від точок, у порожньому полі
    P.append(text(p1[0] - 8, p1[1] + 40, "тут безпечно міряємо", size=11,
                  color=MUTED, anchor="middle"))

    # перетин з віссю I = I_n (струм КЗ), дістаний ЕКСТРАПОЛЯЦІЄЮ
    P.append(circle(I_n_x, oy, 6, fill="#fdecea", stroke=POS, sw=2))
    P.append(line(I_n_x, oy, I_n_x, oy + 16, color=POS, sw=1.3, dash="4 3"))
    P.append(text(I_n_x, oy + 34, "I_n", size=15, bold=True, color=POS))
    P.append(text(I_n_x, oy + 52, "(струм КЗ — не міряли!)", size=11, color=MUTED))

    # перетин з віссю V = V_oc
    P.append(circle(ox, V_oc_y, 6, fill="#eaf0fd", stroke=NEG, sw=2))
    P.append(line(ox, V_oc_y, ox - 16, V_oc_y, color=NEG, sw=1.3, dash="4 3"))
    P.append(text(ox - 22, V_oc_y + 5, "V_oc", size=13, bold=True, color=NEG, anchor="end"))

    # трикутник нахилу = −R_n: легенда в порожньому полі ПІД лінією (низ-ліворуч)
    lx, ly = 175, 312
    P.append(line(lx, ly, lx + 64, ly, color=MUTED, sw=1.6))            # ΔI (горизонталь)
    P.append(line(lx + 64, ly, lx + 64, ly + 38, color=MUTED, sw=1.6))  # ΔV (вертикаль)
    P.append(line(lx, ly, lx + 64, ly + 38, color=NEG, sw=2.0))         # гіпотенуза ∥ прямій
    P.append(text(lx + 30, ly - 6, "ΔI", size=11, color=MUTED))
    P.append(text(lx + 84, ly + 24, "ΔV", size=11, color=MUTED, anchor="start"))
    P.append(text(lx + 8, ly + 60, "нахил = −R_n", size=12, color=MUTED, anchor="start", bold=True))

    # рівняння прямої
    b, w, h = textbox(ox + 150, V_oc_y + 2, "V = V_oc − I · R_n", size=15,
                      pad=10, stroke=INK, color=INK, bold=True)
    P.append(b)

    render(os.path.join(IMG, "extrapolate-to-short.svg"), W, H, *P,
           title="Дві точки задають пряму — I_n беремо екстраполяцією до V = 0")


# ── Фігура 5 (вставка proj): конвеєр прошивки ───────────────────────────────
def fig_firmware():
    W, H = 840, 410
    P = []

    # джерело — чорна скринька з клемами
    P.append(rect(50, 150, 120, 120, fill="#f0f1f3", stroke=INK, sw=2, rx=8))
    P.append(mtext(110, 200, ["невідоме", "джерело", "(?)"], size=13, bold=True))
    P.append(line(170, 178, 215, 178, color=INK, sw=2))
    P.append(line(170, 242, 215, 242, color=INK, sw=2))
    P.append(circle(215, 178, 4.5, fill=POS, stroke=POS))
    P.append(circle(215, 242, 4.5, fill=NEG, stroke=NEG))

    # два ключі-навантаження між клемами
    P.append(rect(228, 168, 90, 84, fill=BG, stroke=MUTED, sw=1.4, rx=6))
    P.append(text(273, 162, "два ключі", size=11, color=MUTED))
    # R1
    P.append(line(215, 178, 240, 178, color=INK, sw=1.6))
    P.append(rect(240, 170, 26, 16, fill=FILL, stroke=INK, sw=1.4))
    P.append(text(300, 182, "R₁", size=12, anchor="start", bold=True))
    P.append(line(266, 178, 290, 178, color=INK, sw=1.6))
    P.append(line(290, 178, 290, 242, color=INK, sw=1.6))
    P.append(line(215, 242, 290, 242, color=INK, sw=1.6))
    # R2
    P.append(line(240, 220, 266, 220, color=INK, sw=1.6, dash="3 3"))
    P.append(rect(240, 212, 26, 16, fill=FILL, stroke=INK, sw=1.4))
    P.append(text(300, 224, "R₂", size=12, anchor="start", bold=True))

    # АЦП знімає V на клемах (усереднює)
    P.append(arrow(195, 150, 195, 116, color=FIELD, sw=2))
    b, w, h = textbox(195, 96, "АЦП → V\n(сер. N)", size=12, pad=8, stroke=FIELD)
    P.append(b)

    # МК
    mcx = 500
    b, w, h = textbox(mcx, 210, ["Мікроконтролер", "", "I = V / R  → 2 точки",
                                 "R_n = (V₁−V₂)/(I₂−I₁)", "I_n = V_oc / R_n"],
                      size=13, pad=12, stroke=INK)
    P.append(b)
    mc_left = mcx - w / 2
    P.append(arrow(330, 210, mc_left - 4, 210, color=INK, sw=2))

    # вихід — Нортонів еквівалент
    eqx = 740
    P.append(rect(eqx - 62, 140, 128, 170, fill="#fbfdfb", stroke=FIELD, sw=2, rx=8))
    P.append(text(eqx, 162, "Нортон", size=13, bold=True, color=FIELD))
    P.append(circle(eqx - 26, 222, 20, fill=BG, stroke=INK, sw=2))
    P.append(arrow(eqx - 26, 238, eqx - 26, 206, color=INK, sw=2))
    P.append(text(eqx - 26, 268, "I_n", size=14, bold=True, color=POS))
    P.append(line(eqx + 24, 200, eqx + 24, 212, color=INK, sw=2))
    P.append(rect(eqx + 12, 212, 24, 36, fill=FILL, stroke=INK, sw=1.5))
    P.append(line(eqx + 24, 248, eqx + 24, 260, color=INK, sw=2))
    P.append(text(eqx + 44, 234, "R_n", size=14, bold=True, anchor="start", color=NEG))
    P.append(arrow(mcx + w / 2 + 4, 210, eqx - 64, 210, color=INK, sw=2))

    # крос-звірка
    b, w, h = textbox(W / 2, 372, "крос-звірка:  V_th = I_n · R_n  (перетворення джерел)",
                      size=13, pad=9, stroke=MUTED, color=MUTED)
    P.append(b)

    render(os.path.join(IMG, "firmware-pipeline.svg"), W, H, *P,
           title="Прошивка: два ключі-навантаження → АЦП → I_n і R_n")


if __name__ == "__main__":
    fig_short_circuit()
    fig_three_numbers()
    fig_worked()
    fig_extrapolate()
    fig_firmware()
    print("written:", os.listdir(IMG))
