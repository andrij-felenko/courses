# -*- coding: utf-8 -*-
"""Фігури до теми «Швидкість baud».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WARN = "#b07a00"   # «на межі» — між зеленим (безпечно) і червоним (збій)


# ── 1. Дільник частоти: звідки апаратура бере baud ───────────────────────────
def fig_baud_divider():
    W, H = 860, 360
    f = [text(W / 2, 30, "Генератор baud — це дільник: f / (16 × DIV)", size=17, bold=True),
         text(W / 2, 52, "периферійну частоту ділять на ЦІЛЕ число й на передискретизацію (типово 16×)",
              size=12, italic=True, color=MUTED)]

    y = 150
    bw, bh = 150, 64
    # f_periph
    f.append(rect(60, y - bh / 2, bw, bh, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(60 + bw / 2, y - 6, "f периферії", size=13, bold=True))
    f.append(text(60 + bw / 2, y + 16, "напр. 16 МГц", size=11, color=MUTED))
    f.append(arrow(60 + bw + 4, y, 60 + bw + 48, y, color=INK))
    # ÷ DIV
    x2 = 60 + bw + 50
    f.append(rect(x2, y - bh / 2, 130, bh, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(x2 + 65, y - 6, "÷ DIV", size=13, bold=True))
    f.append(text(x2 + 65, y + 16, "ціле число", size=11, color=MUTED))
    f.append(arrow(x2 + 134, y, x2 + 178, y, color=INK))
    # ÷ 16
    x3 = x2 + 180
    f.append(rect(x3, y - bh / 2, 150, bh, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(x3 + 75, y - 6, "÷ 16", size=13, bold=True))
    f.append(text(x3 + 75, y + 16, "передискретизація", size=11, color=MUTED))
    f.append(arrow(x3 + 154, y, x3 + 198, y, color=FIELD))
    # baud
    x4 = x3 + 200
    f.append(rect(x4, y - bh / 2, 150, bh, fill="#eef7f0", stroke=FIELD, sw=1.8))
    f.append(text(x4 + 75, y - 6, "baud", size=14, bold=True, color=FIELD))
    f.append(text(x4 + 75, y + 16, "біт/с (тут 2 рівні)", size=10.5, color=MUTED))

    f.append(text(W / 2, 232, "baud = f периферії / (16 × DIV)", size=16, bold=True))

    f.append(fitbox(120, 256, 620, 78, [
                    "DIV мусить бути ЦІЛИМ, а формула рідко дає рівне число — його округлюють, тож",
                    "реальна швидкість трохи відходить від бажаної. Ось перше джерело похибки baud:",
                    "воно з'їдає частину допуску ще до того, як підключено другий пристрій."],
                    size=12.5, fill="#f4f6f8"))
    render(os.path.join(IMG, "baud-divider.svg"), W, H, *f)


# ── 2. Розсинхрон накопичується вздовж кадру ─────────────────────────────────
def fig_drift_accumulates():
    W, H = 1133, 430
    f = [text(W / 2, 30, "Розсинхрон накопичується: відлік «повзе» від старту до кінця кадру",
              size=17, bold=True),
         text(W / 2, 52, "приймач синхронізується лише на СТАРТі; далі зсув росте з кожним бітом (тут RX на +5%)",
              size=12, italic=True, color=MUTED)]

    cells = ["ST", "0", "1", "2", "3", "4", "5", "6", "7", "SP"]
    x0, cw, ytop, ch = 120, 78, 195, 46
    drift = 0.05
    for i, lab in enumerate(cells):
        cx = x0 + i * cw
        fill = "#fbecec" if lab == "ST" else ("#f3f3f3" if lab == "SP" else BG)
        f.append(rect(cx, ytop, cw, ch, fill=fill, stroke=MUTED, sw=1.3, rx=0))
        f.append(text(cx + cw / 2, ytop + ch + 18, lab, size=11, bold=True))
        midx = cx + cw / 2
        # ідеальний центр (TX) — зелена крапка зверху
        f.append(line(midx, ytop - 8, midx, ytop + ch, color=FIELD, sw=1.2, dash="3,3"))
        f.append(circle(midx, ytop - 16, 4, fill=FIELD, stroke=FIELD, sw=0))
        # відлік приймача (RX) — повзе вправо
        k = i  # ST=0 ... SP=9
        shift = (k + 0.5) * drift * cw
        rxx = midx + shift
        f.append(circle(rxx, ytop + ch + 34, 5, fill="#fff", stroke=POS, sw=2))
    # підписи рядів
    f.append(text(x0 - 12, ytop - 16, "центри TX →", size=10.5, bold=True, color=FIELD, anchor="end"))
    f.append(text(x0 - 12, ytop + ch + 38, "відлік RX →", size=10.5, bold=True, color=POS, anchor="end"))
    f.append(text(x0 + 9 * cw + cw / 2 + 12, ytop + ch + 38,
                  "на стоп-біті зсув ≈ 9.5 × 5% = 0.475 біта", size=11, bold=True, color=POS, anchor="start"))

    f.append(rect(60, 350, 840, 56, fill="#eef7f0", stroke=FIELD, sw=1.4, rx=10))
    f.append(text(W / 2, 374, "Зсув на біті k ≈ (k + 0.5) × розбіжність такту. Найбільший він на ОСТАННЬОМУ біті кадру.",
                  size=12, bold=True))
    f.append(text(W / 2, 394, "Наступний старт-біт скидає його в нуль — тому довгі кадри вразливіші.",
                  size=11.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "drift-accumulates.svg"), W, H, *f)


# ── 3. Бюджет допуску: лінійне зростання до межі 0.5 біта ─────────────────────
def fig_tolerance_budget():
    W, H = 900, 440
    f = [text(W / 2, 30, "Бюджет допуску: відлік мусить лишитися в межах ±0.5 біта", size=17, bold=True),
         text(W / 2, 52, "зсув росте лінійно з номером біта; межа — пів-біта на останньому відліку (k ≈ 9.5)",
              size=12, italic=True, color=MUTED)]

    ox, oy = 130, 320       # початок осей
    ax_w, ax_h = 680, 220   # довжина осей
    kmax, smax = 10.0, 0.6  # масштаб: k до 10, зсув до 0.6 біта

    def px(k):
        return ox + ax_w * (k / kmax)

    def py(s):
        return oy - ax_h * (s / smax)

    # осі
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(arrow(ox + ax_w - 1, oy, ox + ax_w + 18, oy, color=INK))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(arrow(ox, oy - ax_h + 1, ox, oy - ax_h - 18, color=INK))
    f.append(text(ox + ax_w + 16, oy + 22, "номер біта k", size=12, anchor="end"))
    f.append(text(ox - 10, oy - ax_h - 6, "зсув (у бітах)", size=12, anchor="end"))
    for k in (0, 2, 4, 6, 8, 10):
        f.append(line(px(k), oy, px(k), oy + 5, color=INK, sw=1.4))
        f.append(text(px(k), oy + 20, str(k), size=11, color=MUTED))

    # межа 0.5 біта
    ylim = py(0.5)
    f.append(rect(ox, oy - ax_h, ax_w, oy - ylim - ax_h + ax_h, fill="#fdeeee", stroke="none", sw=0))
    f.append(line(ox, ylim, ox + ax_w, ylim, color=POS, sw=2, dash="6,4"))
    f.append(text(ox + 6, ylim - 8, "межа = 0.5 біта (край вікна)", size=11.5, bold=True, color=POS, anchor="start"))

    # прямі для 2 / 5 / 6 %
    for rate, col, lab in ((0.02, FIELD, "2%"), (0.05, WARN, "5%"), (0.06, POS, "6%")):
        x_end, y_end = px(kmax), py(rate * kmax)
        f.append(line(px(0), py(0), x_end, y_end, color=col, sw=2.4))
        f.append(text(x_end + 6, y_end + 4, lab, size=11.5, bold=True, color=col, anchor="start"))
    # точка перетину 5.3% × 9.5 = 0.5
    f.append(circle(px(9.5), py(0.5), 5, fill="#fff", stroke=INK, sw=2))
    f.append(text(px(9.5), py(0.5) + 20, "≈5.3% × 9.5 = 0.5", size=10.5, bold=True))

    f.append(rect(60, 384, 780, 50, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(W / 2, 404, "Гранична сумарна розбіжність ≈ 0.5 / 9.5 ≈ 5.3% для 8N1 — і її ДІЛЯТЬ передавач із приймачем.",
                  size=12, bold=True))
    f.append(text(W / 2, 424, "Звідси практичне правило: кожна сторона має триматися в межах ≈ ±2%.",
                  size=11.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "tolerance-budget.svg"), W, H, *f)


# ── 4. Куди влучає відлік стоп-біта за різної розбіжності ─────────────────────
def fig_stop_bit_cases():
    W, H = 900, 380
    f = [text(W / 2, 30, "Куди влучає відлік стоп-біта за різної розбіжності", size=17, bold=True),
         text(W / 2, 52, "зсув на стоп-біті = 9.5 × розбіжність; влучити треба в межах ±0.5 від центру",
              size=12, italic=True, color=MUTED)]

    bx, bw, bh = 250, 360, 44
    cx = bx + bw / 2        # центр клітини
    half = bw / 2           # = 180 px на 0.5 біта → 360 px/біт

    rows = [
        (110, 0.19, FIELD, "2%", "безпечно: глибоко в біті", "зсув 0.19 біта", False),
        (196, 0.475, WARN, "5%", "на межі: 0.475 від центру", "зсув 0.48 біта", False),
        (282, 0.57, POS, "6%", "ЗБІЙ: 0.57 — у сусідній біт → помилка кадру", "зсув 0.57 біта", True),
    ]
    for ytop, shift, col, lab, verdict, sub, miss in rows:
        f.append(rect(bx, ytop, bw, bh, fill="#f3f3f3", stroke=MUTED, sw=1.4, rx=0))
        f.append(line(cx, ytop - 8, cx, ytop + bh + 8, color=MUTED, sw=1.4, dash="3,3"))
        f.append(text(cx, ytop - 12, "центр", size=9.5, color=MUTED))
        f.append(text(bx + 6, ytop + 26, "|край", size=9.5, color=MUTED, anchor="start"))
        f.append(text(bx + bw - 6, ytop + 26, "край|", size=9.5, color=MUTED, anchor="end"))
        # маркер відліку: зсув праворуч від центру
        mx = cx + shift * (bw)   # bw px = 1 біт
        if mx > bx + bw - 4:
            mx = bx + bw + 22     # вийшов за край
        my = ytop + bh + 26
        f.append(line(mx, my, mx, ytop + bh + 2, color=col, sw=2))
        f.append(circle(mx, my, 5, fill="#fff", stroke=col, sw=2))
        f.append(text(bx - 14, ytop + 26, lab, size=14, bold=True, color=col, anchor="end"))
        f.append(text(bx + bw + 16, ytop + 22, verdict, size=11.5, bold=True, color=col, anchor="start"))
        f.append(text(bx + bw + 16, ytop + 40, sub, size=10.5, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "stop-bit-cases.svg"), W, H, *f)


# ── 5. Чому існують «дивні» кварци: похибка baud на 115200 ────────────────────
def fig_crystals():
    W, H = 900, 430
    f = [text(W / 2, 30, "Чому існують «дивні» кварци: похибка baud на 115200", size=17, bold=True),
         text(W / 2, 52, "ціле DIV (×16): кратні до 115200 частоти дають 0%, «круглі» МГц — велику похибку",
              size=12, italic=True, color=MUTED)]

    cols = [(110, "кварц"), (310, "DIV"), (400, "реальний baud"), (575, "похибка"), (680, "вердикт")]
    # шапка
    f.append(rect(90, 88, 720, 38, fill="#eef0f2", stroke=MUTED, sw=1.4, rx=6))
    for x, lab in cols:
        f.append(text(x, 112, lab, size=12, bold=True, anchor="start"))

    rows = [
        ("14.7456 МГц", "8", "115200", "0.0%", FIELD, "✓ ідеально (= 115200×128)"),
        ("11.0592 МГц", "6", "115200", "0.0%", FIELD, "✓ ідеально"),
        ("20.000 МГц", "11", "113636", "−1.4%", WARN, "~ припустимо"),
        ("16.000 МГц", "9", "111111", "−3.5%", WARN, "~ ризик на повному кадрі"),
        ("12.000 МГц", "7", "107143", "−7.0%", POS, "✗ зависоко — збої"),
    ]
    y = 126
    rh = 38
    for name, div, real, err, col, verdict in rows:
        f.append(rect(90, y, 720, rh, fill=BG, stroke=MUTED, sw=1, rx=0))
        f.append(text(cols[0][0], y + 24, name, size=12.5, bold=True, anchor="start"))
        f.append(text(cols[1][0], y + 24, div, size=12, anchor="start"))
        f.append(text(cols[2][0], y + 24, real, size=12, anchor="start"))
        f.append(text(cols[3][0], y + 24, err, size=12.5, bold=True, color=col, anchor="start"))
        f.append(text(cols[4][0], y + 24, verdict, size=11.5, color=col, anchor="start"))
        y += rh

    f.append(rect(60, y + 12, 780, 48, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(W / 2, y + 40,
                  "Кварци 1.8432 / 3.6864 / 7.3728 / 11.0592 / 14.7456 МГц — кратні до бодових частот, тож дають 0%.",
                  size=11.5, bold=True))
    render(os.path.join(IMG, "crystals.svg"), W, H, *f)


# ── 6. Що ще звужує допуск: довжина кадру й джерело такту ─────────────────────
def fig_frame_and_clock():
    W, H = 920, 430
    f = [text(W / 2, 30, "Що звужує допуск: довжина кадру й джерело такту", size=17, bold=True),
         text(W / 2, 52, "коротший кадр терпить більший розсинхрон; точність годинника з'їдає бюджет",
              size=12, italic=True, color=MUTED)]

    # ── ліва панель: допуск vs довжина кадру ──
    f.append(rect(40, 80, 410, 252, fill="none", stroke="#e0e3e6", sw=2, rx=12))
    f.append(text(245, 106, "допуск vs довжина кадру", size=13.5, bold=True))
    f.append(text(70, 132, "формат", size=11, bold=True, color=MUTED, anchor="start"))
    f.append(text(210, 132, "останній відлік", size=11, bold=True, color=MUTED, anchor="start"))
    f.append(text(360, 132, "допуск", size=11, bold=True, color=MUTED, anchor="start"))
    frames = [("5N1", "6.5 біта", "7.7%"), ("8N1", "9.5 біта", "5.3%"),
              ("8E1", "10.5 біта", "4.8%"), ("8N2", "10.5 біта", "4.8%")]
    fy = 162
    for fmt, last, tol in frames:
        f.append(text(70, fy, fmt, size=12.5, bold=True, anchor="start"))
        f.append(text(210, fy, last, size=12, anchor="start"))
        f.append(text(360, fy, tol, size=12.5, bold=True, color=FIELD, anchor="start"))
        fy += 36
    f.append(text(245, 322, "менше біт до кінця → більший допуск", size=10.5, italic=True, color=MUTED))

    # ── права панель: точність джерела такту ──
    f.append(rect(470, 80, 410, 252, fill="none", stroke="#e0e3e6", sw=2, rx=12))
    f.append(text(675, 106, "точність джерела такту", size=13.5, bold=True))
    srcs = [(150, FIELD, "кварц", "±0.005% (±50 ppm)"),
            (210, WARN, "керамічний резонатор", "±0.3…0.5%"),
            (270, POS, "внутрішній RC", "±1…2% (з температурою)")]
    for cy, col, name, val in srcs:
        f.append(circle(500, cy, 7, fill=col, stroke=col, sw=0))
        f.append(text(518, cy - 1, name, size=12.5, bold=True, anchor="start"))
        f.append(text(518, cy + 17, val, size=11.5, color=col, anchor="start"))
    f.append(text(675, 320, "RC сам може з'їсти весь бюджет — звідси кварц для точного UART",
                  size=10.5, italic=True, color=MUTED))

    f.append(rect(60, 350, 800, 56, fill="#eef7f0", stroke=FIELD, sw=1.4, rx=10))
    f.append(text(W / 2, 374,
                  "Бюджет ≈5% ділять: похибка baud TX + похибка baud RX + дрейф годинника + зерно передискретизації.",
                  size=11.5, bold=True))
    f.append(text(W / 2, 394,
                  "Тому два пристрої з внутрішнім RC на 115200 часто «не бачать» одне одного, а з кварцами — легко.",
                  size=11.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "frame-and-clock.svg"), W, H, *f)


if __name__ == "__main__":
    fig_baud_divider()
    fig_drift_accumulates()
    fig_tolerance_budget()
    fig_stop_bit_cases()
    fig_crystals()
    fig_frame_and_clock()
    print("OK: figures written to", IMG)
