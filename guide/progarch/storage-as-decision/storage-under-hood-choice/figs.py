# -*- coding: utf-8 -*-
"""Фігури для кроку «Що обрати під профіль запису/читання» (guide/progarch).
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#eafaf1"
BLUE_FILL = "#eaf0fd"


# ── Фігура 1: анатомія двох рушіїв ──────────────────────────────────────────
def engines():
    W, H = 1000, 500
    f = []
    # роздільник панелей
    f.append(line(500, 48, 500, 470, color=MUTED, sw=1.2, dash="5 5"))

    # ЛІВА панель: B-дерево (на місці)
    f.append(text(267, 74, "B-дерево — правити на місці", size=17, bold=True))
    # корінь
    f.append(rect(222, 104, 90, 36))
    f.append(text(267, 127, "вузол", size=13))
    # листки (впорядковані сторінки)
    leaves = [52, 146, 240, 334]
    centers = [x + 40 for x in leaves]
    for x in leaves:
        f.append(rect(x, 250, 80, 48))
    f.append(text(267, 328, "листки — упорядковані сторінки", size=12, color=MUTED))
    # сірі гілки до листків 1 і 3
    for cx in (centers[0], centers[2]):
        f.append(line(267, 140, cx, 250, color=MUTED, sw=1.2))
    # зелена: читання — один шлях (до листка 2)
    f.append(line(267, 140, centers[1], 250, color=FIELD, sw=3))
    f.append(text(150, 355, "читання: один упорядкований шлях", size=12, color=FIELD))
    # червона: запис врозкид у листок 4
    f.append(arrow(430, 175, centers[3] + 4, 246, color=POS))
    f.append(mtext(430, 150, ["запис врозкид:", "переписати цілу сторінку"],
                   size=12, color=POS, anchor="middle"))

    # ПРАВА панель: LSM (журнал + злиття)
    f.append(text(732, 74, "LSM — дописувати й зливати", size=17, bold=True))
    # memtable
    f.append(rect(640, 100, 184, 38, fill=GREEN_FILL, stroke=FIELD))
    f.append(text(732, 124, "memtable (RAM)", size=13))
    # запис у memtable
    f.append(arrow(548, 119, 636, 119, color=FIELD))
    f.append(text(560, 104, "запис", size=12, color=FIELD, anchor="start"))
    # скидання → рівні
    f.append(arrow(732, 140, 732, 168, color=FIELD))
    f.append(text(748, 158, "скидання", size=11, color=MUTED, anchor="start"))
    f.append(rect(640, 170, 184, 30))
    f.append(text(732, 190, "L0 — свіжі файли", size=12))
    f.append(rect(612, 214, 240, 30))
    f.append(text(732, 234, "L1", size=12))
    f.append(rect(584, 258, 296, 30))
    f.append(text(732, 278, "L2 — найбільший", size=12))
    # злиття/ущільнення
    f.append(arrow(732, 200, 732, 214, color=FIELD))
    f.append(arrow(732, 244, 732, 258, color=FIELD))
    f.append(mtext(905, 232, ["злиття /", "ущільнення"], size=11, color=MUTED, anchor="middle"))
    # читання-підпис
    f.append(text(732, 330, "читання: перевір кілька рівнів —", size=12, color=MUTED))
    f.append(text(732, 348, "фільтр Блума пропускає зайві файли", size=12, color=MUTED))

    render(os.path.join(IMG, "engines.svg"), W, H, *f,
           title="Дві машини під тим самим SQL")


# ── Фігура 2: трикутник RUM ─────────────────────────────────────────────────
def rum_triangle():
    W, H = 820, 600
    T = (410, 135)
    L = (130, 475)
    R = (690, 475)
    f = []
    # трикутник
    f.append(line(T[0], T[1], L[0], L[1], color=INK, sw=2))
    f.append(line(L[0], L[1], R[0], R[1], color=INK, sw=2))
    f.append(line(R[0], R[1], T[0], T[1], color=INK, sw=2))
    # вершини
    f.append(mtext(410, 92, ["Читання (R)", "читацьке підсилення"], size=14, bold=True))
    f.append(mtext(150, 508, ["Запис (U)", "писальне підсилення"], size=14, bold=True))
    f.append(mtext(670, 508, ["Місце (M)", "просторове підсилення"], size=14, bold=True))
    # B-дерево — ближче до читання
    bt = (440, 285)
    f.append(line(430, 268, bt[0], bt[1], color=MUTED, sw=1))
    f.append(mtext(430, 244, ["B-дерево", "дешеве читання"], size=13, color=NEG, bold=True))
    f.append(circle(bt[0], bt[1], 8, fill=BLUE_FILL, stroke=NEG, sw=2))
    # LSM — ближче до запису
    ls = (330, 405)
    f.append(line(330, 388, ls[0], ls[1], color=MUTED, sw=1))
    f.append(mtext(330, 364, ["LSM", "дешевий запис"], size=13, color=FIELD, bold=True))
    f.append(circle(ls[0], ls[1], 8, fill=GREEN_FILL, stroke=FIELD, sw=2))
    # підпис усередині біля основи
    f.append(text(430, 452, "тягнеш до одного кута — інші два дорожчають",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "rum-triangle.svg"), W, H, *f,
           title="Три підсилення: обери будь-які два")


# ── Фігура 3: два профілі DH ────────────────────────────────────────────────
def dh_profiles():
    W, H = 1000, 460
    f = []
    f.append(line(500, 66, 500, 400, color=MUTED, sw=1.2, dash="5 5"))

    # ЛІВА: телеметрія → LSM
    f.append(fitbox(120, 78, 300, 46, "Телеметрія сенсорів", size=16, bold=True))
    f.append(mtext(150, 158, ["• потік вставок, дописування",
                              "• рідко оновлюють",
                              "• читають діапазоном за часом"],
                   size=13, anchor="start", lh=1.5))
    f.append(arrow(270, 250, 270, 292, color=FIELD, sw=2.2))
    f.append(fitbox(128, 296, 284, 62, "LSM (журнальне)\nналиває потік вставок",
                    size=14, bold=True, fill=GREEN_FILL, stroke=FIELD))

    # ПРАВА: реєстр → B-дерево
    f.append(fitbox(580, 78, 300, 46, "Реєстр і конфіг", size=16, bold=True))
    f.append(mtext(610, 158, ["• точкові пошуки",
                              "• транзакційні правки (ACID)",
                              "• малий, має бути свіжим"],
                   size=13, anchor="start", lh=1.5))
    f.append(arrow(730, 250, 730, 292, color=NEG, sw=2.2))
    f.append(fitbox(588, 296, 284, 62, "B-дерево (реляційне)\nточні швидкі читання",
                    size=14, bold=True, fill=BLUE_FILL, stroke=NEG))

    f.append(text(500, 420, "два профілі — два рушії; це не суперечність",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "dh-profiles.svg"), W, H, *f,
           title="Digital Homes: один застосунок — два профілі")


# ── Фігура 4: скоркарта інструмента-відбитка на двох таблицях DH ─────────────
def fingerprint_scorecard():
    W, H = 980, 650
    CX = 600          # вісь: ліворуч B-дерево, праворуч LSM
    LBL = 300         # правий край стовпця назв сигналів
    K = 38            # пікселів на одиницю внеску
    BH = 15           # висота бруска сигналу
    f = []

    def barval(v):
        if abs(v) < 0.005:
            return "0.00"
        return ("+%.2f" % v) if v > 0 else ("−%.2f" % abs(v))

    def panel(y_title, caption, signals, total):
        yh = y_title + 22                       # рядок «◀ B-дерево | LSM ▶»
        y0 = yh + 26                            # перший сигнал
        step = 30
        y_sep = y0 + len(signals) * step - 8
        y_tot = y_sep + 26
        # заголовок панелі
        f.append(text(LBL, y_title, caption, size=15, bold=True, anchor="end"))
        # підписи боків
        f.append(text(CX - 12, yh, "◀ B-дерево (на місці)", size=12,
                      color=NEG, anchor="end"))
        f.append(text(CX + 12, yh, "LSM (журнальне) ▶", size=12,
                      color=FIELD, anchor="start"))
        # центральна вісь
        f.append(line(CX, yh + 8, CX, y_tot + 14, color=INK, sw=1.5))
        # рядки сигналів
        for i, (name, val) in enumerate(signals):
            y = y0 + i * step
            f.append(text(LBL, y + 4, name, size=13, anchor="end"))
            if abs(val) < 0.005:
                f.append(circle(CX, y, 3, fill=MUTED, stroke=MUTED))
                f.append(text(CX + 9, y + 4, "0.00", size=12, color=MUTED, anchor="start"))
            else:
                xe = CX + val * K
                f.append(rect(min(CX, xe), y - BH / 2, abs(val * K), BH,
                              fill=(GREEN_FILL if val > 0 else BLUE_FILL),
                              stroke=(FIELD if val > 0 else NEG), sw=1.5, rx=3))
                if val > 0:
                    f.append(text(xe + 6, y + 4, barval(val), size=12,
                                  color=FIELD, anchor="start", bold=True))
                else:
                    f.append(text(xe - 6, y + 4, barval(val), size=12,
                                  color=NEG, anchor="end", bold=True))
        # роздільник і підсумок
        f.append(line(70, y_sep, W - 40, y_sep, color=MUTED, sw=1, dash="4 4"))
        f.append(text(LBL, y_tot + 5, "СУМА", size=14, bold=True, anchor="end"))
        xe = CX + total * K
        f.append(rect(min(CX, xe), y_tot - 10, abs(total * K), 20,
                      fill=(GREEN_FILL if total > 0 else BLUE_FILL),
                      stroke=(FIELD if total > 0 else NEG), sw=2.2, rx=3))
        col = FIELD if total > 0 else NEG
        if total > 0:
            f.append(text(xe + 8, y_tot + 5, barval(total), size=14, color=col,
                          anchor="start", bold=True))
        else:
            f.append(text(xe - 8, y_tot + 5, barval(total), size=14, color=col,
                          anchor="end", bold=True))

    tele = [("запис домінує", 2.99), ("читання діапазоном", -2.00),
            ("робочий набір > RAM", 2.00), ("ключ урозкид", 1.88),
            ("правки на місці (churn)", 0.00)]
    reg = [("запис домінує", -2.99), ("читання діапазоном", 0.00),
           ("робочий набір > RAM", -2.00), ("ключ урозкид", 0.00),
           ("правки на місці (churn)", -0.99)]
    panel(74, "measurement — телеметрія", tele, 4.87)
    panel(392, "device — реєстр", reg, -5.99)

    render(os.path.join(IMG, "fingerprint-scorecard.svg"), W, H, *f,
           title="Той самий інструмент — два відбитки, дві відповіді")


# ── Фігура (вставка RUM): leveling проти tiering ────────────────────────────
def compaction_leveled_tiered():
    W, H = 1060, 500
    f = []
    f.append(line(530, 52, 530, 448, color=MUTED, sw=1.2, dash="5 5"))

    ys = [88, 162, 236]
    names = ["L0", "L1", "L2"]

    # ЛІВА: leveling — один прогін на рівень
    f.append(text(265, 74, "Leveling — один прогін на рівень", size=16, bold=True))
    for i, y in enumerate(ys):
        f.append(rect(135, y, 260, 46, fill=GREEN_FILL, stroke=FIELD))
        f.append(text(265, y + 28, "один упорядкований прогін", size=12))
        f.append(text(108, y + 29, names[i], size=13, bold=True))
        if i < 2:
            f.append(arrow(265, y + 46, 265, ys[i + 1] - 2, color=MUTED, sw=1.6))
    f.append(mtext(474, 155, ["зливають", "≈ T/2 разів"], size=11, color=POS))
    f.append(arrow(452, 185, 398, 185, color=POS, sw=1.6))
    f.append(fitbox(133, 326, 264, 96,
                    "ЗАПИС ≈ (T/2)·L — високий\nМІСЦЕ ≈ 1 — щільно\nЧИТАННЯ ≈ 1 прогін/рівень",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    # ПРАВА: tiering — до T прогонів на рівень
    f.append(text(795, 74, "Tiering — до T прогонів на рівень", size=16, bold=True))
    for i, y in enumerate(ys):
        for j in range(4):
            f.append(rect(655 + j * 62, y, 54, 46, fill=BLUE_FILL, stroke=NEG))
        f.append(text(628, y + 29, names[i], size=13, bold=True))
        if i < 2:
            f.append(arrow(775, y + 46, 775, ys[i + 1] - 2, color=MUTED, sw=1.6))
    f.append(mtext(795, 302, ["набралось ≈ T прогонів —",
                              "зливають усі разом, запис 1×"], size=11, color=MUTED))
    f.append(fitbox(657, 326, 264, 96,
                    "ЗАПИС ≈ L — низький\nМІСЦЕ ≈ T — роздуто\nЧИТАННЯ ≈ T прогонів/рівень",
                    size=13, fill=BLUE_FILL, stroke=NEG))

    f.append(text(530, 462, "той самий рушій, інша політика ущільнення — інший бік трикутника RUM",
                  size=13, color=MUTED, bold=True))
    render(os.path.join(IMG, "compaction-leveled-tiered.svg"), W, H, *f,
           title="Leveling проти tiering: обмін запису на місце й читання")


# ── Фігура (вставка RUM): дно писального підсилення leveling ─────────────────
def writeamp_curve():
    import math
    W, H = 840, 560
    px0, px1 = 120, 760
    py0, py1 = 470, 95
    Tmin, Tmax, Wmax = 2.0, 20.0, 25.0
    coef = math.log(1000.0) / 2.0          # (ln t)/2, t = N/B = 1000

    def wx(T): return px0 + (T - Tmin) / (Tmax - Tmin) * (px1 - px0)
    def wy(v): return py0 - (v / Wmax) * (py0 - py1)
    def Wof(T): return coef * T / math.log(T)

    f = []
    # осі
    f.append(line(px0, py0, px1, py0, color=INK, sw=1.6))
    f.append(line(px0, py0, px0, py1, color=INK, sw=1.6))
    f.append(text((px0 + px1) / 2, 508, "розмірний множник рівня T", size=13))
    f.append(mtext(px0 - 6, 78, ["писальне", "підсилення W"], size=13, anchor="start"))
    # мітки осей
    for T in [2, 5, 10, 15, 20]:
        f.append(line(wx(T), py0, wx(T), py0 + 5, color=INK, sw=1.2))
        f.append(text(wx(T), py0 + 22, str(T), size=12, color=MUTED))
    for v in [1, 5, 10, 15, 20, 25]:
        f.append(line(px0 - 5, wy(v), px0, wy(v), color=INK, sw=1.2))
        f.append(text(px0 - 12, wy(v) + 4, str(v), size=12, color=MUTED, anchor="end"))
    # лінія ідеалу W = 1
    f.append(line(px0, wy(1), px1, wy(1), color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(px1, wy(1) - 8, "ідеал W = 1 (недосяжно)", size=11, color=MUTED, anchor="end"))
    # крива W(T) = coef·T/ln T
    T, prev = Tmin, None
    while T <= Tmax + 1e-9:
        p = (wx(T), wy(min(Wof(T), Wmax)))
        if prev:
            f.append(line(prev[0], prev[1], p[0], p[1], color=NEG, sw=2.4))
        prev = p
        T += 0.4
    # мінімум при T = e
    Te = math.e
    f.append(line(258, 382, wx(Te) + 4, wy(Wof(Te)) + 4, color=MUTED, sw=1.0))
    f.append(circle(wx(Te), wy(Wof(Te)), 6, fill=GREEN_FILL, stroke=FIELD, sw=2))
    f.append(mtext(262, 392, ["мінімум при T = e ≈ 2.72", "W ≈ 9.4 — і то ≫ 1"],
                   size=12, color=FIELD, anchor="start"))
    # точка T = 10
    f.append(circle(wx(10), wy(Wof(10)), 5, fill=BLUE_FILL, stroke=NEG, sw=2))
    f.append(text(wx(10) + 10, wy(Wof(10)) - 8, "T = 10 → W ≈ 15", size=12, color=NEG, anchor="start"))
    f.append(text((px0 + px1) / 2, 534,
                  "нижче дна — лише зміною політики на tiering (W ≈ L), і то ціною місця ≈ T",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "writeamp-curve.svg"), W, H, *f,
           title="Писальне підсилення leveling має дно — і воно > 1")


if __name__ == "__main__":
    engines()
    rum_triangle()
    dh_profiles()
    fingerprint_scorecard()
    compaction_leveled_tiered()
    writeamp_curve()
    print("OK:", os.listdir(IMG))
