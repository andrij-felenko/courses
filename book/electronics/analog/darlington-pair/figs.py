# -*- coding: utf-8 -*-
"""Фігури до теми «Схема Дарлінгтона» (analog/darlington-pair).
Чотири фігури:
  cascade.svg            — суть: емітер Q1 → база Q2, колектори разом, β = β1·β2
  two-vbe.svg            — ціна №1: два переходи база–емітер послідовно (~1.4 В)
  leakage.svg            — ціна №2: витік Q1 підсилюється Q2; резистор-злив на базі Q2
  darlington-vs-sziklai  — два різновиди: NPN-NPN та комплементарний (NPN-PNP)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── невеликий примітив: NPN-транзистор кружком (спрощено) ────────────────────
def npn(cx, cy, r=26, label=None, lblcolor=INK):
    """Спрощений значок NPN: коло, всередині 'риска' бази й дві похилі (К згори, Е знизу).
    Повертає (svg, точки): база ліворуч, колектор згори, емітер знизу."""
    parts = [circle(cx, cy, r, fill=BG, stroke=INK, sw=2)]
    # вертикальна риска бази
    bx = cx - r * 0.35
    parts.append(line(bx, cy - r * 0.55, bx, cy + r * 0.55, color=INK, sw=2.4))
    # вивід бази ліворуч
    parts.append(line(cx - r, cy, bx, cy, color=INK, sw=2))
    # колектор (вгору-праворуч)
    parts.append(line(bx, cy - r * 0.28, cx + r * 0.5, cy - r * 0.62, color=INK, sw=2))
    parts.append(line(cx + r * 0.5, cy - r * 0.62, cx + r * 0.5, cy - r - 6, color=INK, sw=2))
    # емітер (вниз-праворуч) зі стрілкою назовні (NPN: стрілка від бази)
    ex, ey = cx + r * 0.5, cy + r * 0.62
    parts.append(line(bx, cy + r * 0.28, ex, ey, color=INK, sw=2))
    parts.append(line(ex, ey, ex, cy + r + 6, color=INK, sw=2))
    # стрілка емітера
    ax, ay = (bx + ex) / 2 + 2, (cy + r * 0.28 + ey) / 2 + 1
    parts.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        ax, ay, ax - 7, ay - 1, ax - 2, ay - 7, INK))
    if label:
        parts.append(text(cx + r + 4, cy - r * 0.2, label, size=15, color=lblcolor, bold=True, anchor="start"))
    pts = {"b": (cx - r, cy), "c": (cx + r * 0.5, cy - r - 6), "e": (cx + r * 0.5, cy + r + 6)}
    return "".join(parts), pts


def pnp(cx, cy, r=26, label=None, lblcolor=INK):
    """Спрощений значок PNP: стрілка емітера всередину (до бази)."""
    parts = [circle(cx, cy, r, fill=BG, stroke=INK, sw=2)]
    bx = cx - r * 0.35
    parts.append(line(bx, cy - r * 0.55, bx, cy + r * 0.55, color=INK, sw=2.4))
    parts.append(line(cx - r, cy, bx, cy, color=INK, sw=2))
    # для PNP: колектор знизу, емітер згори (малюємо емітер згори зі стрілкою всередину)
    ex, ey = cx + r * 0.5, cy - r * 0.62
    parts.append(line(bx, cy - r * 0.28, ex, ey, color=INK, sw=2))
    parts.append(line(ex, ey, ex, cy - r - 6, color=INK, sw=2))
    # колектор вниз
    cxp, cyp = cx + r * 0.5, cy + r * 0.62
    parts.append(line(bx, cy + r * 0.28, cxp, cyp, color=INK, sw=2))
    parts.append(line(cxp, cyp, cxp, cy + r + 6, color=INK, sw=2))
    # стрілка емітера — до бази (всередину)
    ax, ay = (bx + ex) / 2, (cy - r * 0.28 + ey) / 2
    parts.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        ax, ay, ax + 7, ay + 1, ax + 2, ay + 7, INK))
    if label:
        parts.append(text(cx + r + 4, cy - r * 0.2, label, size=15, color=lblcolor, bold=True, anchor="start"))
    pts = {"b": (cx - r, cy), "e": (cx + r * 0.5, cy - r - 6), "c": (cx + r * 0.5, cy + r + 6)}
    return "".join(parts), pts


# ════════════════════════════════════════════════════════════════════════════
# 1. cascade.svg — суть схеми
# ════════════════════════════════════════════════════════════════════════════
def fig_cascade():
    W, H = 720, 380
    f = []
    # Q1 ліворуч-угорі, Q2 праворуч-унизу
    q1, p1 = npn(250, 130, r=30, label="Q1")
    q2, p2 = npn(470, 230, r=34, label="Q2")
    # шина колектора (спільний вихід) згори
    cy_bus = 60
    f.append(line(120, cy_bus, 600, cy_bus, color=POS, sw=2.4))
    f.append(line(p1["c"][0], p1["c"][1], p1["c"][0], cy_bus, color=POS, sw=2))
    f.append(line(p2["c"][0], p2["c"][1], p2["c"][0], cy_bus, color=POS, sw=2))
    f.append(circle(p1["c"][0], cy_bus, 3.5, fill=POS, stroke=POS))
    f.append(circle(p2["c"][0], cy_bus, 3.5, fill=POS, stroke=POS))
    f.append(text(610, cy_bus + 5, "C (спільний колектор-вихід)", size=13, color=POS, anchor="start", bold=True))
    # емітер Q1 → база Q2
    ex1, ey1 = p1["e"]
    bx2, by2 = p2["b"]
    f.append(line(ex1, ey1, ex1, by2, color=FIELD, sw=2.6))
    f.append(line(ex1, by2, bx2, by2, color=FIELD, sw=2.6))
    f.append(circle(bx2, by2, 3.5, fill=FIELD, stroke=FIELD))
    f.append(text(ex1 + 8, (ey1 + by2) / 2, "E1 → B2", size=13, color=FIELD, anchor="start", bold=True))
    # вхід — база Q1
    f.append(line(70, p1["b"][1], p1["b"][0], p1["b"][1], color=NEG, sw=2.4))
    f.append(circle(70, p1["b"][1], 4, fill=NEG, stroke=NEG))
    f.append(text(64, p1["b"][1] - 10, "B (вхід)", size=13, color=NEG, anchor="start", bold=True))
    f.append(text(64, p1["b"][1] + 22, "крихітний Ib", size=12, color=MUTED, anchor="start"))
    # емітер Q2 — спільний вихід-емітер униз
    ex2, ey2 = p2["e"]
    f.append(line(ex2, ey2, ex2, 330, color=INK, sw=2.4))
    f.append(line(120, 330, ex2, 330, color=INK, sw=2.4))
    f.append(circle(120, 330, 4, fill=INK, stroke=INK))
    f.append(text(126, 326, "E (спільний емітер) — великий струм навантаження", size=12.5, color=INK, anchor="start"))
    # рамка-висновок
    bx, _, _ = textbox(330, 165, "β = β1 · β2\n(перемножуються)", size=15, bold=True,
                       fill="#eef7f0", stroke=FIELD)
    f.append(bx)
    return render(os.path.join(IMG, "cascade.svg"), W, H, *f,
                  title="Схема Дарлінгтона: емітер Q1 годує базу Q2, колектори разом")


# ════════════════════════════════════════════════════════════════════════════
# 2. two-vbe.svg — два переходи база–емітер послідовно
# ════════════════════════════════════════════════════════════════════════════
def fig_two_vbe():
    W, H = 700, 330
    f = []
    # ліворуч — одиночний транзистор: один Vbe
    f.append(text(170, 50, "Одиночний транзистор", size=14, bold=True))
    bx, _, _ = textbox(170, 150, "B → E\nодин перехід", size=13)
    f.append(bx)
    bx2, w2, h2 = textbox(170, 235, "Vbe ≈ 0.7 В", size=15, bold=True, fill="#eaf0fb", stroke=NEG)
    f.append(bx2)
    # праворуч — Дарлінгтон: два Vbe в стовпчик
    f.append(text(520, 50, "Дарлінгтон", size=14, bold=True))
    # стек двох переходів
    f.append(rect(470, 110, 100, 44, fill=FILL, stroke=LINE))
    f.append(text(520, 137, "B → E1", size=13))
    f.append(rect(470, 158, 100, 44, fill=FILL, stroke=LINE))
    f.append(text(520, 185, "B2 → E2", size=13))
    f.append(line(520, 154, 520, 158, color=LINE, sw=2))
    bx3, w3, h3 = textbox(520, 250, "Vbe(заг) ≈ 1.4 В\n(два по 0.7 В)", size=14, bold=True,
                          fill="#eaf0fb", stroke=NEG)
    f.append(bx3)
    # стрілка-порівняння
    f.append(arrow(300, 165, 400, 165, color=MUTED, sw=2))
    f.append(text(350, 150, "ціна", size=12, color=MUTED))
    return render(os.path.join(IMG, "two-vbe.svg"), W, H, *f,
                  title="Ціна №1: два переходи база–емітер замість одного")


# ════════════════════════════════════════════════════════════════════════════
# 3. leakage.svg — витік Q1 підсилюється; резистор-злив
# ════════════════════════════════════════════════════════════════════════════
def fig_leakage():
    W, H = 720, 360
    f = []
    q1, p1 = npn(230, 120, r=28, label="Q1")
    q2, p2 = npn(460, 220, r=32, label="Q2")
    # спільний колектор-вихід
    f.append(line(150, 60, 560, 60, color=POS, sw=2.2))
    f.append(line(p1["c"][0], p1["c"][1], p1["c"][0], 60, color=POS, sw=2))
    f.append(line(p2["c"][0], p2["c"][1], p2["c"][0], 60, color=POS, sw=2))
    f.append(circle(p1["c"][0], 60, 3, fill=POS, stroke=POS))
    f.append(circle(p2["c"][0], 60, 3, fill=POS, stroke=POS))
    # E1 → B2
    ex1, ey1 = p1["e"]; bx2, by2 = p2["b"]
    f.append(line(ex1, ey1, ex1, by2, color=INK, sw=2))
    f.append(line(ex1, by2, bx2, by2, color=INK, sw=2))
    f.append(circle(bx2, by2, 3, fill=INK, stroke=INK))
    # витік Q1 — червона хвиляста стрілка від E1 до бази Q2
    f.append(text(ex1 + 6, ey1 + 20, "малий витік Q1", size=12, color=POS, anchor="start"))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        bx2 - 4, by2, bx2 - 14, by2 - 5, bx2 - 14, by2 + 5, POS))
    # резистор-злив від бази Q2 до емітера Q2 (вниз)
    ex2, ey2 = p2["e"]
    rx = bx2 + 4
    f.append(line(bx2, by2, bx2, by2 + 26, color=LINE, sw=2))
    f.append(rect(rx - 12, by2 + 26, 24, 50, fill="#fff4e6", stroke=LINE))
    f.append(text(rx + 22, by2 + 55, "R (злив)", size=12, color=INK, anchor="start"))
    f.append(line(bx2, by2 + 76, bx2, ey2 + 50, color=LINE, sw=2))
    # емітер-вихід униз
    f.append(line(ex2, ey2, ex2, ey2 + 50, color=INK, sw=2.2))
    f.append(line(bx2, ey2 + 50, ex2, ey2 + 50, color=INK, sw=2.2))
    f.append(line(170, ey2 + 50, bx2, ey2 + 50, color=INK, sw=2.2))
    f.append(circle(170, ey2 + 50, 3.5, fill=INK, stroke=INK))
    f.append(text(176, ey2 + 46, "вихід / емітер", size=12, color=INK, anchor="start"))
    # пояснювальна рамка
    bx, _, _ = textbox(560, 250, "Без R витік Q1\nпомножується на β2\n→ хибне відкриття.\nR зливає витік повз Q2.",
                       size=12.5, fill="#fff4e6", stroke=POS)
    f.append(bx)
    return render(os.path.join(IMG, "leakage.svg"), W, H, *f,
                  title="Ціна №2: витік Q1 підсилюється — рятує резистор-злив")


# ════════════════════════════════════════════════════════════════════════════
# 4. darlington-vs-sziklai.svg
# ════════════════════════════════════════════════════════════════════════════
def fig_vs():
    W, H = 760, 380
    f = []
    # ── ліворуч: класичний Дарлінгтон (NPN-NPN) ──
    f.append(text(190, 46, "Дарлінгтон (NPN-NPN)", size=14, bold=True))
    q1, p1 = npn(150, 140, r=26, label="Q1")
    q2, p2 = npn(250, 230, r=30, label="Q2")
    # колектори разом угору
    f.append(line(90, 80, 320, 80, color=POS, sw=2))
    f.append(line(p1["c"][0], p1["c"][1], p1["c"][0], 80, color=POS, sw=1.8))
    f.append(line(p2["c"][0], p2["c"][1], p2["c"][0], 80, color=POS, sw=1.8))
    # E1->B2
    f.append(line(p1["e"][0], p1["e"][1], p1["e"][0], p2["b"][1], color=INK, sw=1.8))
    f.append(line(p1["e"][0], p2["b"][1], p2["b"][0], p2["b"][1], color=INK, sw=1.8))
    f.append(circle(p2["b"][0], p2["b"][1], 3, fill=INK, stroke=INK))
    # вхід
    f.append(line(70, p1["b"][1], p1["b"][0], p1["b"][1], color=NEG, sw=2))
    f.append(text(64, p1["b"][1] - 8, "вхід", size=11.5, color=NEG, anchor="start"))
    # вихід-емітер
    f.append(line(p2["e"][0], p2["e"][1], p2["e"][0], 320, color=INK, sw=2))
    f.append(line(95, 320, p2["e"][0], 320, color=INK, sw=2))
    f.append(text(95, 314, "вихід", size=11.5, color=INK, anchor="start"))
    bx, _, _ = textbox(190, 350, "2 переходи: Vbe ≈ 1.4 В", size=12.5, fill="#eaf0fb", stroke=NEG)
    f.append(bx)
    # роздільник
    f.append(line(390, 40, 390, 360, color="#dddddd", sw=1.5, dash="4,4"))
    # ── праворуч: Шиклаї (комплементарний: NPN + PNP) ──
    f.append(text(575, 46, "Шиклаї (NPN + PNP)", size=14, bold=True))
    s1, sp1 = npn(540, 140, r=26, label="Q1")
    s2, sp2 = pnp(645, 215, r=30, label="Q2")
    # вхід на базу NPN
    f.append(line(460, sp1["b"][1], sp1["b"][0], sp1["b"][1], color=NEG, sw=2))
    f.append(text(454, sp1["b"][1] - 8, "вхід", size=11.5, color=NEG, anchor="start"))
    # колектор Q1 → база Q2(PNP)
    f.append(line(sp1["c"][0], sp1["c"][1], sp1["c"][0], 95, color=INK, sw=1.8))
    f.append(line(sp1["c"][0], 95, sp2["b"][0], 95, color=INK, sw=1.8))
    f.append(line(sp2["b"][0], 95, sp2["b"][0], sp2["b"][1], color=INK, sw=1.8))
    f.append(circle(sp2["b"][0], sp2["b"][1], 3, fill=INK, stroke=INK))
    # емітер Q2(PNP) — угору до шини живлення/виходу; емітер Q1 і колектор Q2 — вихід
    f.append(line(sp2["e"][0], sp2["e"][1], sp2["e"][0], 80, color=POS, sw=1.8))
    f.append(line(500, 80, 700, 80, color=POS, sw=2))
    # вихід: емітер Q1 + колектор Q2 разом
    f.append(line(sp1["e"][0], sp1["e"][1], sp1["e"][0], 290, color=INK, sw=1.8))
    f.append(line(sp2["c"][0], sp2["c"][1], sp2["c"][0], 290, color=INK, sw=1.8))
    f.append(line(sp1["e"][0], 290, sp2["c"][0], 290, color=INK, sw=1.8))
    f.append(circle(sp2["c"][0], 290, 3, fill=INK, stroke=INK))
    f.append(line(500, 290, sp1["e"][0], 290, color=INK, sw=2))
    f.append(text(500, 284, "вихід", size=11.5, color=INK, anchor="start"))
    bx2, _, _ = textbox(575, 350, "1 перехід на вході: Vbe ≈ 0.7 В", size=12.5, fill="#eef7f0", stroke=FIELD)
    f.append(bx2)
    return render(os.path.join(IMG, "darlington-vs-sziklai.svg"), W, H, *f,
                  title="Два різновиди складеного транзистора")


if __name__ == "__main__":
    fig_cascade()
    fig_two_vbe()
    fig_leakage()
    fig_vs()
    print("OK: 4 фігури у", IMG)
