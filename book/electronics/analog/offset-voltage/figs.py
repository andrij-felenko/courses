# -*- coding: utf-8 -*-
"""Фігури до теми «Напруга зсуву операційного підсилювача (Vos)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

WIRE = "#cf8b5e"   # тепла мідь для резисторів і провідників


# ── 1. Модель еквівалентного джерела зсуву Vos та коефіцієнт шуму ─────────────
def fig_model_vos():
    W, H = 800, 440
    f = [
        text(W / 2, 28, "Еквівалентна схема напруги зсуву ОП", size=17, bold=True),
        text(W / 2, 48, "реальний ОП моделюється як ідеальний із послідовним джерелом Vos на вході",
             size=12, color=MUTED, italic=True)
    ]

    # Контур реального ОП (пунктирний прямокутник-корпус)
    ic_x, ic_y, ic_w, ic_h = 320, 80, 430, 240
    f.append(rect(ic_x, ic_y, ic_w, ic_h, fill="#fafbfc", stroke="#94a3b8", sw=1.6, rx=8))
    f.append(text(ic_x + 14, ic_y + 22, "Реальний ОП", size=12, color="#64748b", anchor="start", bold=True))

    # Символ ідеального ОП (трикутник)
    tx, ty = 540, 190
    tri_w, tri_h = 130, 140
    pts = "%d,%d %d,%d %d,%d" % (tx, ty - tri_h / 2, tx, ty + tri_h / 2, tx + tri_w, ty)
    f.append('<polygon points="%s" fill="#eaf6ee" stroke="%s" stroke-width="2.2"/>' % (pts, FIELD))
    f.append(text(tx + 45, ty + 5, "Ідеальний ОП", size=12, color=FIELD, bold=True))
    f.append(text(tx + 45, ty + 22, "A_OL → ∞", size=11, color=FIELD))

    # Входи на трикутнику: мінус вгорі, плюс внизу
    ym = ty - 40
    yp = ty + 40
    f.append(minus(tx + 16, ym, r=8))
    f.append(plus(tx + 16, yp, r=8))

    # Джерело Vos перед неінвертуючим входом
    src_x = 420
    f.append(circle(src_x, yp, 16, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(src_x, yp - 3, "+", size=12, color=POS, bold=True))
    f.append(text(src_x, yp + 10, "−", size=12, color=NEG, bold=True))
    f.append(text(src_x, yp - 24, "V_os", size=13, color=POS, bold=True))

    # Дроти всередині корпусу
    # Від зовнішнього піна IN+ до джерела Vos, і від Vos до плюса трикутника
    f.append(line(ic_x, yp, src_x - 16, yp, color=INK, sw=2))
    f.append(line(src_x + 16, yp, tx, yp, color=INK, sw=2))
    f.append(circle(ic_x, yp, 4, fill=INK, stroke=INK))
    f.append(text(ic_x - 12, yp + 4, "IN+", size=12, color=INK, anchor="end", bold=True))

    # Від зовнішнього піна IN- до мінуса трикутника
    f.append(line(ic_x, ym, tx, ym, color=INK, sw=2))
    f.append(circle(ic_x, ym, 4, fill=INK, stroke=INK))
    f.append(text(ic_x - 12, ym + 4, "IN−", size=12, color=INK, anchor="end", bold=True))

    # Зовнішнє коло: інвертуюча схема з R1 і Rf
    # Вхідний сигнал Vin -> R1 -> IN-
    r1_x = 170
    f.append(line(70, ym, r1_x - 25, ym, color=INK, sw=2))
    f.append(rect(r1_x - 25, ym - 10, 50, 20, fill="#fff7ec", stroke=WIRE, sw=1.8, rx=3))
    f.append(text(r1_x, ym + 4, "R1", size=12, color=WIRE, bold=True))
    f.append(line(r1_x + 25, ym, ic_x, ym, color=INK, sw=2))
    f.append(circle(70, ym, 4, fill=INK, stroke=INK))
    f.append(text(60, ym + 4, "V_in", size=12, color=INK, anchor="end", bold=True))

    # Вузол зворотного зв'язку біля IN-
    node_fb = 270
    f.append(circle(node_fb, ym, 3.5, fill=INK, stroke=INK))
    f.append(line(node_fb, ym, node_fb, ym - 55, color=INK, sw=2))
    f.append(line(node_fb, ym - 55, 690, ym - 55, color=INK, sw=2))
    # Резистор Rf у ланцюзі ЗЗ
    rf_x = 480
    f.append(rect(rf_x - 30, ym - 65, 60, 20, fill="#fff7ec", stroke=WIRE, sw=1.8, rx=3))
    f.append(text(rf_x, ym - 51, "Rf", size=12, color=WIRE, bold=True))

    # Вихід трикутника і вихід мікросхеми
    out_x = tx + tri_w
    f.append(line(out_x, ty, ic_x + ic_w, ty, color=INK, sw=2))
    f.append(circle(ic_x + ic_w, ty, 4, fill=INK, stroke=INK))
    f.append(line(ic_x + ic_w, ty, ic_x + ic_w + 35, ty, color=INK, sw=2))
    f.append(text(ic_x + ic_w + 42, ty + 4, "V_out", size=13, color=INK, anchor="start", bold=True))

    # Замикання Rf на вихідний дріт
    f.append(line(690, ym - 55, 690, ty, color=INK, sw=2))
    f.append(circle(690, ty, 3.5, fill=INK, stroke=INK))

    # Земля на IN+ (для інвертуючого підсилювача)
    f.append(line(ic_x, yp, 240, yp, color=INK, sw=2))
    f.append(line(240, yp, 240, yp + 25, color=INK, sw=2))
    # Символ землі
    f.append(line(225, yp + 25, 255, yp + 25, color=INK, sw=2.2))
    f.append(line(230, yp + 30, 250, yp + 30, color=INK, sw=1.8))
    f.append(line(236, yp + 35, 244, yp + 35, color=INK, sw=1.4))

    # Блок пояснення вихідної напруги
    f.append(fitbox(50, 340, 700, 80,
                    "V_out = −(Rf / R1) · V_in  +  (1 + Rf / R1) · V_os\n"
                    "Корисний сигнал множиться на A_v = −Rf / R1, а зсув V_os — на коефіцієнт шуму A_n = 1 + Rf / R1",
                    size=13, fill=FILL, stroke=FIELD, bold=True))

    render(os.path.join(IMG, "model-vos.svg"), W, H, *f)


# ── 2. Фізичне походження: асиметрія диференційної пари ───────────────────────
def fig_diff_pair_mismatch():
    W, H = 840, 480
    f = [
        text(W / 2, 28, "Фізичне походження Vos: асиметрія диференційної пари", size=17, bold=True),
        text(W / 2, 48, "технологічний розкид площі емітерів, резисторів навантаження та легування бази",
             size=12, color=MUTED, italic=True)
    ]

    # Верхня шина живлення +Vcc
    top_y = 80
    f.append(line(160, top_y, 680, top_y, color=INK, sw=2.2))
    f.append(text(690, top_y + 4, "+V_CC", size=12, color=INK, anchor="start", bold=True))

    # Ліва і права гілки диференційної пари
    q1_x = 300
    q2_x = 540

    # Резистори колектора RC1 та RC2
    rc_y = top_y + 40
    f.append(line(q1_x, top_y, q1_x, rc_y - 20, color=INK, sw=2))
    f.append(rect(q1_x - 18, rc_y - 20, 36, 40, fill="#fff7ec", stroke=WIRE, sw=1.8, rx=3))
    f.append(text(q1_x, rc_y + 4, "R_C1", size=11, color=WIRE, bold=True))
    f.append(line(q1_x, rc_y + 20, q1_x, rc_y + 55, color=INK, sw=2))

    f.append(line(q2_x, top_y, q2_x, rc_y - 20, color=INK, sw=2))
    f.append(rect(q2_x - 18, rc_y - 20, 36, 40, fill="#fff7ec", stroke=WIRE, sw=1.8, rx=3))
    f.append(text(q2_x, rc_y + 4, "R_C2", size=11, color=WIRE, bold=True))
    f.append(line(q2_x, rc_y + 20, q2_x, rc_y + 55, color=INK, sw=2))

    # Вихідні вузли колекторів
    node_c1 = rc_y + 55
    node_c2 = rc_y + 55
    f.append(circle(q1_x, node_c1, 3.5, fill=INK, stroke=INK))
    f.append(circle(q2_x, node_c2, 3.5, fill=INK, stroke=INK))
    f.append(line(q1_x, node_c1, q1_x - 55, node_c1, color=FIELD, sw=1.8))
    f.append(line(q2_x, node_c2, q2_x + 55, node_c2, color=FIELD, sw=1.8))
    f.append(text(q1_x - 62, node_c1 + 4, "V_C1", size=12, color=FIELD, anchor="end", bold=True))
    f.append(text(q2_x + 62, node_c2 + 4, "V_C2", size=12, color=FIELD, anchor="start", bold=True))

    # Транзистори Q1 та Q2
    tr_y = node_c1 + 55
    def draw_npn(cx, cy, is_left=True):
        # Базова вертикальна смуга
        bx = cx - 18 if is_left else cx + 18
        f.append(line(bx, cy - 20, bx, cy + 20, color=INK, sw=2.8))
        # Колекторний промінь
        f.append(line(bx, cy - 10, cx, cy - 25, color=INK, sw=2))
        f.append(line(cx, cy - 25, cx, node_c1, color=INK, sw=2))
        # Емітерний промінь зі стрілкою
        f.append(line(bx, cy + 10, cx, cy + 25, color=INK, sw=2))
        arrow_x = bx + 0.6 * (cx - bx)
        arrow_y = cy + 10 + 0.6 * 15
        # стрілка на емітері
        dx = 1 if is_left else -1
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
            arrow_x + dx * 4, arrow_y + 4,
            arrow_x - dx * 3, arrow_y - 4,
            arrow_x + dx * 1, arrow_y - 2,
            INK
        ))
        # Базовий дріт
        base_wire_x = bx - 45 if is_left else bx + 45
        f.append(line(bx, cy, base_wire_x, cy, color=INK, sw=2))
        f.append(circle(base_wire_x, cy, 3.5, fill=INK, stroke=INK))
        return base_wire_x, cx, cy + 25

    b1_x, e1_x, e1_y = draw_npn(q1_x, tr_y, is_left=True)
    b2_x, e2_x, e2_y = draw_npn(q2_x, tr_y, is_left=False)

    f.append(text(q1_x + 22, tr_y - 5, "Q1", size=13, color=INK, bold=True))
    f.append(text(q2_x - 22, tr_y - 5, "Q2", size=13, color=INK, bold=True))

    f.append(text(b1_x - 8, tr_y + 4, "IN+", size=12, color=POS, anchor="end", bold=True))
    f.append(text(b2_x + 8, tr_y + 4, "IN−", size=12, color=NEG, anchor="start", bold=True))

    # Спільний емітерний хвіст
    tail_y = e1_y + 25
    f.append(line(q1_x, e1_y, q1_x, tail_y, color=INK, sw=2))
    f.append(line(q2_x, e2_y, q2_x, tail_y, color=INK, sw=2))
    f.append(line(q1_x, tail_y, q2_x, tail_y, color=INK, sw=2))
    mid_x = (q1_x + q2_x) / 2
    f.append(circle(mid_x, tail_y, 3.5, fill=INK, stroke=INK))

    # Джерело сталого струму I_tail
    cs_y = tail_y + 35
    f.append(line(mid_x, tail_y, mid_x, cs_y - 18, color=INK, sw=2))
    f.append(circle(mid_x, cs_y, 18, fill="#eaf6ee", stroke=FIELD, sw=2))
    f.append(arrow(mid_x, cs_y - 10, mid_x, cs_y + 10, color=FIELD, sw=2))
    f.append(text(mid_x + 28, cs_y + 4, "I_хв", size=12, color=FIELD, anchor="start", bold=True))

    # Нижня шина живлення -Vee
    bot_y = cs_y + 45
    f.append(line(mid_x, cs_y + 18, mid_x, bot_y, color=INK, sw=2))
    f.append(line(160, bot_y, 680, bot_y, color=INK, sw=2.2))
    f.append(text(690, bot_y + 4, "−V_EE", size=12, color=INK, anchor="start", bold=True))

    # Блоки несиметрії ліворуч і праворуч
    f.append(fitbox(30, 160, 190, 80,
                    "Розкид площі емітерів:\nI_S1 ≠ I_S2\nΔV_BE = V_T · ln(I_S2 / I_S1)",
                    size=11, fill="#fdecea", stroke=POS, bold=True))

    f.append(fitbox(620, 160, 190, 80,
                    "Розкид навантажень:\nR_C1 ≠ R_C2\nΔV_R = V_T · (ΔR_C / R_C)",
                    size=11, fill="#fdecea", stroke=POS, bold=True))

    # Підсумкова формула внизу
    f.append(fitbox(W / 2 - 320, 410, 640, 56,
                    "V_os = ΔV_BE + V_T · (ΔR_C / R_C) ≈ V_T · (ΔI_S / I_S + ΔR_C / R_C)\n"
                    "Навіть за нульової вхідної різниці на виході є перекіс, який треба скомпенсувати на вході",
                    size=12, fill=FILL, stroke=FIELD, bold=True))

    render(os.path.join(IMG, "diff-pair-mismatch.svg"), W, H, *f)


# ── 3. Температурний дрейф dVos/dT та паразитні термопари ──────────────────────
def fig_drift_and_temp():
    W, H = 820, 450
    f = [
        text(W / 2, 28, "Температурний дрейф зсуву та ефект Зеєбека", size=17, bold=True),
        text(W / 2, 48, "початковий зсув можна відкалібрувати, але дрейф dVos/dT створює динамічну похибку",
             size=12, color=MUTED, italic=True)
    ]

    # Ліва половина: Графік Vos від температури
    L, R, T, B = 70, 390, 95, 340
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    f.append(text(L - 8, T - 10, "V_os (мкВ)", size=11, bold=True, anchor="middle"))
    f.append(text(R, B + 24, "Температура T (°C)", size=11, bold=True, anchor="end"))

    # Позначки температури: -40, 25, 85, 125
    temps = [(-40, "−40°"), (0, "0°"), (25, "25°"), (85, "85°"), (125, "125°")]
    def xt(temp):
        return L + (temp + 40.0) / (125.0 + 40.0) * (R - L)

    for temp, lab in temps:
        x = xt(temp)
        f.append(line(x, B, x, B + 5, color=INK, sw=1.4))
        f.append(text(x, B + 18, lab, size=10, color=MUTED))
        if temp == 25:
            f.append(line(x, T, x, B, color="#94a3b8", sw=1.2, dash="4 4"))

    # Крива зсуву: стандартний підсилювач із калібруванням у точці 25°C
    # Vos(25) = 0 мкВ, нахил dVos/dT = 2 мкВ/°C
    def yv(vos_uv):
        # Діапазон від -200 до +200 мкВ
        return B - (vos_uv + 200.0) / 400.0 * (B - T)

    # Лінія сітки 0 мкВ
    y0 = yv(0)
    f.append(line(L, y0, R, y0, color="#cbd5e1", sw=1.2))
    f.append(text(L - 10, y0 + 4, "0", size=10, color=MUTED, anchor="end"))
    f.append(text(L - 10, yv(150) + 4, "+150", size=10, color=MUTED, anchor="end"))
    f.append(text(L - 10, yv(-150) + 4, "−150", size=10, color=MUTED, anchor="end"))

    # Дві криві: некомпенсований ОП (червона лінія) і Zero-Drift ОП (зелена лінія)
    p1 = (xt(-40), yv(-40 * 2.0 + 50))
    p2 = (xt(25), yv(25 * 2.0 + 50))
    p3 = (xt(125), yv(125 * 2.0 + 50))
    f.append(line(p1[0], p1[1], p3[0], p3[1], color=POS, sw=2.4))
    f.append(circle(p2[0], p2[1], 4, fill=POS, stroke=POS))
    f.append(text(p3[0] - 10, p3[1] - 10, "Звичайний ОП (2 мкВ/°C)", size=10, color=POS, anchor="end", bold=True))

    # Зелена лінія: Zero-Drift (чопер/auto-zero) дрейф < 0.05 мкВ/°C
    z1 = (xt(-40), yv(5))
    z2 = (xt(125), yv(8))
    f.append(line(z1[0], z1[1], z2[0], z2[1], color=FIELD, sw=2.4))
    f.append(text(z2[0] - 10, z2[1] - 10, "Zero-Drift ОП (0.01 мкВ/°C)", size=10, color=FIELD, anchor="end", bold=True))

    # Права половина: Термоелектричний ефект (термопари на платі)
    px, py = 440, 95
    pw, ph = 350, 245
    f.append(rect(px, py, pw, ph, fill="#fafbfc", stroke="#94a3b8", sw=1.6, rx=8))
    f.append(text(px + pw / 2, py + 22, "Паразитні термопари пайки (Seebeck)", size=12, color=INK, bold=True))

    # Схема двох виводів мікросхеми: Мідь (доріжка) - Припій - Ковар/Мідь (вивід)
    f.append(text(px + 20, py + 52, "Вивід IN+", size=11, color=POS, anchor="start", bold=True))
    f.append(rect(px + 20, py + 62, 75, 18, fill="#e2e8f0", stroke="#64748b", sw=1.2))
    f.append(text(px + 57, py + 75, "Мідь PCB", size=10, color=INK))
    f.append(rect(px + 95, py + 62, 45, 18, fill="#cbd5e1", stroke="#475569", sw=1.2))
    f.append(text(px + 117, py + 75, "Припій", size=10, color=INK))
    f.append(rect(px + 140, py + 62, 75, 18, fill="#fef08a", stroke="#ca8a04", sw=1.2))
    f.append(text(px + 177, py + 75, "Вивід IC", size=10, color=INK))
    f.append(text(px + 230, py + 75, "T1 = 45.0 °C", size=10, color=POS, bold=True))

    f.append(text(px + 20, py + 112, "Вивід IN−", size=11, color=NEG, anchor="start", bold=True))
    f.append(rect(px + 20, py + 122, 75, 18, fill="#e2e8f0", stroke="#64748b", sw=1.2))
    f.append(text(px + 57, py + 135, "Мідь PCB", size=10, color=INK))
    f.append(rect(px + 95, py + 122, 45, 18, fill="#cbd5e1", stroke="#475569", sw=1.2))
    f.append(text(px + 117, py + 135, "Припій", size=10, color=INK))
    f.append(rect(px + 140, py + 122, 75, 18, fill="#fef08a", stroke="#ca8a04", sw=1.2))
    f.append(text(px + 177, py + 135, "Вивід IC", size=10, color=INK))
    f.append(text(px + 230, py + 135, "T2 = 45.1 °C", size=10, color=NEG, bold=True))

    # Термо-ЕРС
    f.append(line(px + 20, py + 160, px + pw - 20, py + 160, color="#e2e8f0", sw=1.2))
    f.append(fitbox(px + 15, py + 170, pw - 30, 60,
                    "Градієнт ΔT = 0.1 °C між пайками\n"
                    "генерує термо-ЕРС ≈ 0.1 °C · 40 мкВ/°C = 4 мкВ!\n"
                    "Вимагає ізотермічного симетричного розведення PCB",
                    size=10, fill="#fef2f2", stroke=POS, bold=True))

    # Спільний підсумок унизу
    f.append(fitbox(50, 365, 720, 65,
                    "Сумарна похибка зсуву в діапазоні температур:\n"
                    "V_os(T) = V_os(25°C)  +  (dV_os / dT) · (T − 25°C)  +  V_термо\n"
                    "Для прецизійних вимірювань дрейф часто є головним джерелом непоправної похибки",
                    size=12, fill=FILL, stroke=FIELD, bold=True))

    render(os.path.join(IMG, "drift-and-temp.svg"), W, H, *f)


# ── 4. Вплив Vos на роботу інтегратора ─────────────────────────────────────────
def fig_integrator_drift():
    W, H = 820, 440
    f = [
        text(W / 2, 28, "Вплив напруги зсуву на роботу інтегратора", size=17, bold=True),
        text(W / 2, 48, "за нульового вхідного сигналу постійний зсув Vos неминуче заводить вихід у насичення",
             size=12, color=MUTED, italic=True)
    ]

    # Схема інтегратора зліва
    cx, cy = 200, 180
    f.append(rect(40, 75, 330, 265, fill="#fafbfc", stroke="#94a3b8", sw=1.6, rx=8))
    f.append(text(40 + 165, 96, "Аналоговий інтегратор", size=12, color=INK, bold=True))

    # Символ ОП
    op_x, op_y = 190, 190
    pts = "%d,%d %d,%d %d,%d" % (op_x, op_y - 45, op_x, op_y + 45, op_x + 80, op_y)
    f.append('<polygon points="%s" fill="#eaf6ee" stroke="%s" stroke-width="2"/>' % (pts, FIELD))
    ym = op_y - 22
    yp = op_y + 22
    f.append(minus(op_x + 12, ym, r=6))
    f.append(plus(op_x + 12, yp, r=6))

    # Джерело Vos на плюсовому вході
    f.append(circle(op_x - 30, yp, 11, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(op_x - 30, yp - 2, "+", size=9, color=POS, bold=True))
    f.append(text(op_x - 30, yp + 7, "−", size=9, color=NEG, bold=True))
    f.append(line(op_x - 19, yp, op_x, yp, color=INK, sw=1.6))
    f.append(line(op_x - 41, yp, op_x - 60, yp, color=INK, sw=1.6))
    # Земля на плюсі
    f.append(line(op_x - 60, yp, op_x - 60, yp + 18, color=INK, sw=1.6))
    f.append(line(op_x - 70, yp + 18, op_x - 50, yp + 18, color=INK, sw=1.8))
    f.append(line(op_x - 66, yp + 22, op_x - 54, yp + 22, color=INK, sw=1.4))
    f.append(line(op_x - 62, yp + 26, op_x - 58, yp + 26, color=INK, sw=1.0))
    f.append(text(op_x - 30, yp - 16, "V_os", size=11, color=POS, bold=True))

    # Вхід Vin = 0 (заземлено) через резистор R
    r_x = 115
    f.append(line(60, ym, r_x - 20, ym, color=INK, sw=1.8))
    f.append(circle(60, ym, 3.5, fill=INK, stroke=INK))
    f.append(text(55, ym + 4, "0 В", size=11, color=INK, anchor="end", bold=True))
    f.append(rect(r_x - 20, ym - 8, 40, 16, fill="#fff7ec", stroke=WIRE, sw=1.6, rx=2))
    f.append(text(r_x, ym + 4, "R", size=10, color=WIRE, bold=True))
    f.append(line(r_x + 20, ym, op_x, ym, color=INK, sw=1.8))

    # Конденсатор C у зворотному зв'язку
    node_m = 150
    f.append(circle(node_m, ym, 3, fill=INK, stroke=INK))
    f.append(line(node_m, ym, node_m, ym - 40, color=INK, sw=1.8))
    f.append(line(node_m, ym - 40, op_x + 110, ym - 40, color=INK, sw=1.8))
    # Обкладки конденсатора C
    cap_x = op_x + 35
    cap_y = ym - 40
    f.append(line(cap_x - 4, cap_y - 12, cap_x - 4, cap_y + 12, color=INK, sw=2))
    f.append(line(cap_x + 4, cap_y - 12, cap_x + 4, cap_y + 12, color=INK, sw=2))
    f.append(text(cap_x, cap_y - 16, "C", size=11, color=INK, bold=True))

    # Вихід
    out_x = op_x + 80
    f.append(line(out_x, op_y, op_x + 110, op_y, color=INK, sw=1.8))
    f.append(line(op_x + 110, ym - 40, op_x + 110, op_y, color=INK, sw=1.8))
    f.append(circle(op_x + 110, op_y, 3, fill=INK, stroke=INK))
    f.append(line(op_x + 110, op_y, 340, op_y, color=INK, sw=1.8))
    f.append(circle(340, op_y, 3.5, fill=INK, stroke=INK))
    f.append(text(348, op_y + 4, "V_out", size=11, color=INK, anchor="start", bold=True))

    # Формула струму інтегрування
    f.append(fitbox(55, 270, 300, 55,
                    "Струм заряду конденсатора:\nI_похибки = V_os / R\nСтворює лінійний дрейф виходу dV/dt = V_os / (R·C)",
                    size=10, fill="#fef2f2", stroke=POS, bold=True))

    # Права половина: Графік інтегрування в часі
    gL, gR, gT, gB = 430, 770, 95, 330
    f.append(line(gL, gT, gL, gB, color=INK, sw=2))
    f.append(line(gL, (gT + gB) / 2, gR, (gT + gB) / 2, color=INK, sw=1.8))
    f.append(text(gL - 8, gT - 10, "V_out (В)", size=11, bold=True, anchor="middle"))
    f.append(text(gR, (gT + gB) / 2 + 20, "Час t", size=11, bold=True, anchor="end"))

    mid_v = (gT + gB) / 2
    # Рейки насичення +Vsat і -Vsat
    f.append(line(gL, gT + 25, gR, gT + 25, color="#ef4444", sw=1.4, dash="5 4"))
    f.append(text(gR - 5, gT + 18, "+V_sat (насичення)", size=10, color=POS, anchor="end", bold=True))

    f.append(line(gL, gB - 25, gR, gB - 25, color="#ef4444", sw=1.4, dash="5 4"))
    f.append(text(gR - 5, gB - 14, "−V_sat (насичення)", size=10, color=POS, anchor="end", bold=True))

    # Криві інтегрування
    # Ідеальна (пряма по нулю)
    f.append(line(gL, mid_v, gR, mid_v, color=FIELD, sw=2.4))
    f.append(text(gR - 100, mid_v - 8, "Ідеал: V_out = 0 В", size=10, color=FIELD, bold=True))

    # Реальна 1 (Vos > 0 -> вихід росте або падає залежно від знаку)
    sat_t1 = gL + 180
    f.append(line(gL, mid_v, sat_t1, gT + 25, color=POS, sw=2.2))
    f.append(line(sat_t1, gT + 25, gR, gT + 25, color=POS, sw=2.2))
    f.append(circle(sat_t1, gT + 25, 4, fill=POS, stroke=POS))
    f.append(text(sat_t1 + 10, gT + 40, "Залипання у +V_sat", size=10, color=POS, anchor="start", bold=True))

    # Реальна 2 (Vos < 0)
    sat_t2 = gL + 220
    f.append(line(gL, mid_v, sat_t2, gB - 25, color=NEG, sw=2.0))
    f.append(line(sat_t2, gB - 25, gR, gB - 25, color=NEG, sw=2.0))
    f.append(circle(sat_t2, gB - 25, 4, fill=NEG, stroke=NEG))
    f.append(text(sat_t2 + 10, gB - 35, "Залипання у −V_sat", size=10, color=NEG, anchor="start", bold=True))

    # Загальний висновок
    f.append(fitbox(50, 360, 720, 60,
                    "Час до насичення інтегратора:  t_насичення = |V_sat| · R · C / |V_os|\n"
                    "Для Vos = 1 мВ, R = 100 кОм, C = 1 мкФ і Vsat = 10 В вихід залипне за t = 10 · 0.1 / 0.001 = 1000 с (~16 хв)",
                    size=12, fill=FILL, stroke=FIELD, bold=True))

    render(os.path.join(IMG, "integrator-drift.svg"), W, H, *f)


if __name__ == "__main__":
    fig_model_vos()
    fig_diff_pair_mismatch()
    fig_drift_and_temp()
    fig_integrator_drift()
    print("OK: figures generated")
