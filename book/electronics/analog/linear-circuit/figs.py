# -*- coding: utf-8 -*-
"""Фігури до теми «Лінійність кола» (аналогова електроніка, кутом теорії кіл).
Три фігури:
  two-rules.svg     — два правила лінійності: однорідність (масштаб) і адитивність (сума) на «чорній скриньці»
  superposition.svg — суперпозиція: по черзі вбиваємо джерела (V→дріт, I→розрив), реакції додаємо
  transfer-curve.svg— пряма передавальна (пропорційність зберігає форму) проти зігнутої (зріз → нові частоти)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, w, h, label):
    out = rect(cx - w/2, cy - h/2, w, h, fill="#eef2f7", stroke=INK, sw=2, rx=8)
    out += text(cx, cy + 5, label, size=15, bold=True)
    return out


# ── 1. Два правила лінійності ───────────────────────────────────────────────
def fig_two_rules():
    W, H = 760, 420
    parts = []
    bx = 380  # центр скриньки по X для верхнього ряду

    # Заголовки рядів
    parts.append(text(W/2, 30, "Дві умови лінійності кола", size=17, bold=True))

    # Рядок 1: однорідність  a·x → a·y
    y1 = 120
    parts.append(text(150, y1 - 48, "однорідність", size=14, bold=True, color=FIELD))
    parts.append(box(bx, y1, 150, 70, "коло"))
    # вхід
    parts.append(arrow(150, y1, bx - 75, y1, color=NEG, sw=2.2))
    parts.append(text(150, y1 - 14, "a · x", size=15, bold=True, color=NEG))
    # вихід
    parts.append(arrow(bx + 75, y1, 640, y1, color=POS, sw=2.2))
    parts.append(text(660, y1 - 14, "a · y", size=15, bold=True, color=POS))
    parts.append(text(W/2, y1 + 64, "збільшив вхід удвічі — вихід рівно вдвічі більший", size=12, color=MUTED))

    # Розділювач
    parts.append(line(40, 205, W - 40, 205, color="#d8dee6", sw=1, dash="4,4"))

    # Рядок 2: адитивність  x1+x2 → y1+y2
    y2 = 300
    parts.append(text(150, y2 - 60, "адитивність", size=14, bold=True, color=FIELD))
    parts.append(box(bx, y2, 150, 70, "коло"))
    parts.append(arrow(150, y2, bx - 75, y2, color=NEG, sw=2.2))
    parts.append(text(150, y2 - 14, "x₁ + x₂", size=15, bold=True, color=NEG))
    parts.append(arrow(bx + 75, y2, 640, y2, color=POS, sw=2.2))
    parts.append(text(665, y2 - 14, "y₁ + y₂", size=15, bold=True, color=POS))
    parts.append(text(W/2, y2 + 64, "реакція на суму = сума реакцій на кожен вхід окремо", size=12, color=MUTED))

    parts.append(text(W/2, H - 16, "обидві разом = принцип суперпозиції", size=13, italic=True, color=INK))
    render(os.path.join(IMG, "two-rules.svg"), W, H, *parts)


# ── 2. Суперпозиція: вбити джерела по черзі ─────────────────────────────────
def fig_superposition():
    W, H = 780, 520
    parts = [text(W/2, 28, "Суперпозиція: рахуємо внески по черзі", size=17, bold=True)]

    def panel(x0, y0, w, h, title, vsrc, isrc):
        out = rect(x0, y0, w, h, fill=BG, stroke="#d8dee6", sw=1.5, rx=8)
        out += text(x0 + w/2, y0 + 22, title, size=13, bold=True)
        # рамка кола
        L, T, R, B = x0 + 34, y0 + 50, x0 + w - 34, y0 + h - 36
        out += rect(L, T, R - L, B - T, fill="none", stroke=INK, sw=1.4, rx=4)
        # резистор-навантаження праворуч
        rx_, ry = R, (T + B) / 2
        out += rect(rx_ - 10, ry - 26, 20, 52, fill="#fff7e6", stroke=INK, sw=1.4, rx=3)
        out += text(rx_ + 22, ry + 4, "R", size=13, bold=True)
        # джерело напруги ліворуч
        sx, sy = L, (T + B) / 2
        if vsrc == "on":
            out += circle(sx, sy, 16, fill="#eaf0fd", stroke=NEG, sw=2)
            out += text(sx, sy + 5, "V", size=14, bold=True, color=NEG)
        else:  # вбите → дріт (коротке)
            out += line(sx, T, sx, B, color=MUTED, sw=2.4)
            out += text(sx - 10, sy - 22, "дріт", size=10, color=MUTED, anchor="end")
        # джерело струму згори
        cx2, cy2 = (L + R) / 2, T
        if isrc == "on":
            out += circle(cx2, cy2, 16, fill="#fdecea", stroke=POS, sw=2)
            out += arrow(cx2, cy2 + 9, cx2, cy2 - 9, color=POS, sw=1.8)
            out += text(cx2 + 22, cy2 + 4, "I", size=14, bold=True, color=POS)
        else:  # вбите → розрив
            out += line(cx2 - 14, T, cx2 - 4, T, color=MUTED, sw=2.4)
            out += line(cx2 + 4, T, cx2 + 14, T, color=MUTED, sw=2.4)
            out += text(cx2, T - 8, "розрив", size=10, color=MUTED)
        return out

    pw, ph = 230, 200
    gap = 18
    y0 = 56
    x1 = 30
    parts.append(panel(x1, y0, pw, ph, "лишаємо V, струмове — розрив", "on", "off"))
    parts.append(text(x1 + pw + gap/2, y0 + ph/2, "+", size=30, bold=True, color=INK, anchor="middle"))
    x2 = x1 + pw + gap
    parts.append(panel(x2, y0, pw, ph, "лишаємо I, напругове — дріт", "off", "on"))

    # стрілка вниз до суми
    parts.append(arrow(W/2, y0 + ph + 6, W/2, y0 + ph + 40, color=INK, sw=2))

    # підсумкова панель
    x3 = (W - pw) / 2
    y3 = y0 + ph + 46
    parts.append(panel(x3, y3, pw, ph - 20, "обидва разом", "on", "on"))
    parts.append(text(W/2, H - 12,
                      "I_R = I_R(від V) + I_R(від I) — додаємо алгебрично, зі знаком",
                      size=12, italic=True, color=INK))
    render(os.path.join(IMG, "superposition.svg"), W, H, *parts)


# ── 3. Передавальна характеристика: пряма vs зігнута ────────────────────────
def fig_transfer():
    W, H = 760, 380
    parts = [text(W/2, 28, "Передавальна характеристика: пряма проти зігнутої", size=17, bold=True)]

    def axes(x0, y0, w, h):
        out = line(x0, y0 + h, x0 + w, y0 + h, color=INK, sw=1.6)  # вхід →
        out += line(x0, y0, x0, y0 + h, color=INK, sw=1.6)         # вихід ↑
        out += text(x0 + w - 4, y0 + h + 16, "вхід", size=11, color=MUTED, anchor="end")
        out += text(x0 - 4, y0 + 6, "вихід", size=11, color=MUTED, anchor="end")
        return out

    # Ліва: лінійна (пряма)
    lx, ly, lw, lh = 70, 60, 260, 220
    parts.append(axes(lx, ly, lw, lh))
    parts.append(line(lx, ly + lh, lx + lw, ly + 18, color=FIELD, sw=2.6))
    parts.append(text(lx + lw/2, ly - 6, "пропорційність", size=13, bold=True, color=FIELD))
    parts.append(text(lx + lw/2, ly + lh + 36, "форма сигналу зберігається —", size=11.5, color=INK))
    parts.append(text(lx + lw/2, ly + lh + 52, "нових частот не зʼявляється", size=11.5, color=INK))

    # Права: нелінійна (насичення/зріз)
    rx0, ry0, rw, rh = 430, 60, 260, 220
    parts.append(axes(rx0, ry0, rw, rh))
    # крива: лінійна на початку, потім полиця (насичення)
    pts = []
    import math
    for i in range(0, 101):
        t = i / 100.0
        xv = rx0 + t * rw
        # м'яке насичення tanh-подібне
        s = math.tanh(2.6 * t)
        yv = ry0 + rh - s * (rh - 16)
        pts.append("%.1f,%.1f" % (xv, yv))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), POS))
    parts.append(text(rx0 + rw/2, ry0 - 6, "насичення / зріз", size=13, bold=True, color=POS))
    parts.append(text(rx0 + rw/2, ry0 + rh + 36, "верхівки зрізані — народжуються", size=11.5, color=INK))
    parts.append(text(rx0 + rw/2, ry0 + rh + 52, "гармоніки, яких на вході не було", size=11.5, color=INK))

    render(os.path.join(IMG, "transfer-curve.svg"), W, H, *parts)


# ── 4. Лінійний оператор L: розклади вхід → застосуй до кожної частини → склади ─
def fig_operator():
    W, H = 780, 430
    parts = [text(W/2, 28, "Лінійний оператор: розклади — застосуй — склади", size=17, bold=True)]

    # Лівий стовпчик: вхід-сума
    xin = 120
    yA, yB = 150, 290
    parts.append(text(xin, 95, "вхід", size=12, bold=True, color=MUTED))
    bA, wA, hA = textbox(xin, yA, "x₁", size=16, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, min_w=70)
    bB, wB, hB = textbox(xin, yB, "x₂", size=16, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, min_w=70)
    parts += [bA, bB]
    parts.append(text(xin, (yA + yB) / 2 + 5, "+", size=24, bold=True, color=INK))

    # Середній стовпчик: той самий оператор L діє на кожну частину окремо
    xL = 380
    parts.append(text(xL, 95, "оператор кола  L", size=12, bold=True, color=FIELD))
    lA, lwA, lhA = textbox(xL, yA, "L", size=18, bold=True, color=FIELD, fill="#e7f6ee", stroke=FIELD, min_w=64)
    lB, lwB, lhB = textbox(xL, yB, "L", size=18, bold=True, color=FIELD, fill="#e7f6ee", stroke=FIELD, min_w=64)
    parts += [lA, lB]
    parts.append(arrow(xin + wA/2, yA, xL - lwA/2, yA, color=NEG, sw=2))
    parts.append(arrow(xin + wB/2, yB, xL - lwB/2, yB, color=NEG, sw=2))

    # Правий стовпчик: окремі відгуки
    xout = 620
    parts.append(text(xout, 95, "відгуки", size=12, bold=True, color=MUTED))
    oA, owA, ohA = textbox(xout, yA, "L·x₁", size=15, bold=True, color=POS, fill="#fdecea", stroke=POS, min_w=86)
    oB, owB, ohB = textbox(xout, yB, "L·x₂", size=15, bold=True, color=POS, fill="#fdecea", stroke=POS, min_w=86)
    parts += [oA, oB]
    parts.append(arrow(xL + lwA/2, yA, xout - owA/2, yA, color=POS, sw=2))
    parts.append(arrow(xL + lwB/2, yB, xout - owB/2, yB, color=POS, sw=2))
    parts.append(text(xout, (yA + yB) / 2 + 5, "+", size=24, bold=True, color=INK))

    # Нижній підсумок: рівність, що і є суперпозиція
    eq, ew, eh = textbox(W/2, 388, "L·(x₁ + x₂)  =  L·x₁  +  L·x₂",
                         size=16, bold=True, color=INK, fill="#fff7e6", stroke=INK, pad=12)
    parts.append(eq)
    parts.append(text(W/2, 358, "однорідність + адитивність = суперпозиція", size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "operator-superposition.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_two_rules()
    fig_superposition()
    fig_transfer()
    fig_operator()
    print("OK: two-rules, superposition, transfer-curve, operator-superposition")
