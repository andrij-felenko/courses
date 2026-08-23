# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «ОП на однополярному живленні» (root/course/embedded/kola).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── локальні символи схеми ───────────────────────────────────────────────────
def opamp(cx, cy, size=46, vplus_top=True):
    """Трикутник ОП вістрям праворуч. cx,cy — центр трикутника.
    Повертає (svg, виводи): in_top, in_bot (ліві входи), out (правий), а також знаки.
    vplus_top=True → «+» угорі, «−» унизу (неінвертуюча подача)."""
    h = size
    w = size * 1.15
    x0 = cx - w / 2
    xt = cx + w / 2
    yt = cy - h / 2
    yb = cy + h / 2
    out = ['<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="#fbfcfd" '
           'stroke="%s" stroke-width="2"/>' % (x0, yt, x0, yb, xt, cy, INK)]
    in_top = (x0, cy - h * 0.22)
    in_bot = (x0, cy + h * 0.22)
    outp = (xt, cy)
    s_top = "+" if vplus_top else "−"
    s_bot = "−" if vplus_top else "+"
    c_top = POS if vplus_top else NEG
    c_bot = NEG if vplus_top else POS
    out.append(text(x0 + 12, in_top[1] + 5, s_top, size=16, color=c_top, bold=True, anchor="middle"))
    out.append(text(x0 + 12, in_bot[1] + 5, s_bot, size=16, color=c_bot, bold=True, anchor="middle"))
    return "".join(out), in_top, in_bot, outp


def res_h(x, y, w=46, label="", lab_dy=-12):
    """Горизонтальний резистор-прямокутник, центр по y. Повертає (svg, лівий_x, правий_x)."""
    out = [rect(x, y - 9, w, 18, fill="#eef1f5", stroke=INK, sw=1.6, rx=3)]
    if label:
        out.append(text(x + w / 2, y + lab_dy + (0 if lab_dy < 0 else 4), label, size=11))
    return "".join(out), x, x + w


def res_v(x, y, h=46, label="", side="right"):
    """Вертикальний резистор, центр по x. Повертає (svg, верх_y, низ_y)."""
    out = [rect(x - 9, y, 18, h, fill="#eef1f5", stroke=INK, sw=1.6, rx=3)]
    if label:
        if side == "right":
            out.append(text(x + 15, y + h / 2 + 4, label, size=11, anchor="start"))
        else:
            out.append(text(x - 15, y + h / 2 + 4, label, size=11, anchor="end"))
    return "".join(out), y, y + h


def cap_h(x, y, label=""):
    """Горизонтальний конденсатор (дві планки) — центр приблизно x+8. Повертає (svg, лівий, правий)."""
    out = [line(x, y - 11, x, y + 11, color=INK, sw=2.4),
           line(x + 12, y - 11, x + 12, y + 11, color=INK, sw=2.4)]
    if label:
        out.append(text(x + 6, y - 18, label, size=11))
    return "".join(out), x, x + 12


def gnd(x, y):
    return (line(x, y, x, y + 6, color=INK, sw=1.8) +
            line(x - 13, y + 6, x + 13, y + 6, color=INK, sw=2.2) +
            line(x - 8, y + 11, x + 8, y + 11, color=INK, sw=2.0) +
            line(x - 3, y + 16, x + 3, y + 16, color=INK, sw=1.8))


def node(x, y):
    return '<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s"/>' % (x, y, INK)


# ── фігура 1: чому зрізається й як це лікує зсув у Vcc/2 ──────────────────────
def fig_clip_vs_shift():
    W, H = 760, 360
    f = [text(W / 2, 28, "Той самий змінний сигнал: без зсуву зрізаний, зі зсувом — цілий",
              size=16, bold=True)]

    # дві координатні панелі
    for px, title, shifted in ((60, "напряму від нуля", False), (420, "зсунуто до Vcc/2", True)):
        top, bot = 70, 300
        left, right = px, px + 280
        mid = (top + bot) / 2
        vcc_y = top + 16
        zero_y = bot - 16
        half_y = (vcc_y + zero_y) / 2
        # рейки
        f.append(line(left, vcc_y, right, vcc_y, color=POS, sw=1.4, dash="5,4"))
        f.append(text(left - 4, vcc_y + 4, "Vcc", size=11, color=POS, anchor="end"))
        f.append(line(left, zero_y, right, zero_y, color=INK, sw=1.8))
        f.append(text(left - 4, zero_y + 4, "0", size=11, anchor="end"))
        if shifted:
            f.append(line(left, half_y, right, half_y, color=FIELD, sw=1.4, dash="5,4"))
            f.append(text(right + 4, half_y + 4, "Vcc/2", size=11, color=FIELD, anchor="start"))
        f.append(text((left + right) / 2, top - 6, title, size=12, bold=True))

        # синус
        import math
        amp = (half_y - vcc_y) * 0.92 if shifted else (zero_y - vcc_y) * 0.42
        base = half_y if shifted else zero_y
        pts = []
        clip = []
        N = 90
        for i in range(N + 1):
            t = i / N
            xx = left + 8 + t * (right - left - 16)
            yy = base - amp * math.sin(t * 2 * math.pi * 2)
            # зріз знизу об 0 (тільки в лівій панелі)
            if not shifted and yy > zero_y:
                clip.append((xx, zero_y))
                pts.append((xx, zero_y))
            else:
                pts.append((xx, yy))
        d = "M" + " L".join("%.1f %.1f" % p for p in pts)
        col = FIELD if shifted else POS
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, col))
        if not shifted:
            # підсвітити зрізану «підлогу»
            f.append(text((left + right) / 2, zero_y - 6, "низ зрізано", size=11, color=POS))
        else:
            f.append(text((left + right) / 2, vcc_y + amp + 14, "уся хвиля вміщається", size=11, color=FIELD))

    render(os.path.join(IMG, "clip-vs-shift.svg"), W, H, *f)


# ── фігура 2: повна схема однополярного неінвертуючого підсилювача ────────────
def fig_topology():
    W, H = 820, 470
    f = [text(W / 2, 26, "Однополярний неінвертуючий підсилювач: опора Vcc/2, розв'язка входу й виходу",
              size=15, bold=True)]

    vcc_y = 70
    gnd_y = 410
    # шина Vcc угорі, земля внизу
    f.append(line(60, vcc_y, 760, vcc_y, color=POS, sw=2))
    f.append(text(48, vcc_y + 4, "Vcc", size=12, color=POS, anchor="end", bold=True))
    f.append(line(60, gnd_y, 760, gnd_y, color=INK, sw=2))
    f.append(text(48, gnd_y + 4, "0", size=12, anchor="end", bold=True))

    # ── дільник Vcc/2 (ліворуч) ──
    dx = 150
    sr, r1t, r1b = res_v(dx, vcc_y + 18, 70, "R₁", side="left")
    f.append(sr)
    f.append(line(dx, vcc_y, dx, r1t, color=INK, sw=1.6))
    midy = r1b + 28
    sr, r2t, r2b = res_v(dx, midy + 6, 70, "R₂", side="left")
    f.append(sr)
    f.append(line(dx, r1b, dx, midy, color=INK, sw=1.6))
    f.append(line(dx, r2b, dx, gnd_y, color=INK, sw=1.6))
    f.append(node(dx, midy))
    # конденсатор розв'язки опори на землю
    f.append(line(dx, midy, dx + 34, midy, color=INK, sw=1.6))
    f.append(line(dx + 34, midy - 11, dx + 34, midy + 11, color=INK, sw=2.4))
    f.append(line(dx + 46, midy - 11, dx + 46, midy + 11, color=INK, sw=2.4))
    f.append(line(dx + 46, midy, dx + 46, gnd_y, color=INK, sw=1.6))
    f.append(text(dx + 40, midy - 18, "C_b", size=11))
    f.append(text(dx - 4, midy - 8, "Vref", size=11, color=FIELD, anchor="end", bold=True))
    f.append(text(dx + 86, midy + 4, "≈ Vcc/2", size=11, color=FIELD, anchor="start"))

    # лінія Vref праворуч до «+» ОП
    op_cx, op_cy = 470, midy
    f.append(line(dx, midy, op_cx - 70, op_cy, color=INK, sw=1.6))

    # ── вхід сигналу через розділовий конденсатор → «+» ──
    sin_x = 70
    f.append(text(sin_x, op_cy - 40, "Vin~", size=12, bold=True))
    f.append(text(sin_x, op_cy - 24, "(змінний)", size=10, color=MUTED))
    # маленький символ джерела змінного сигналу (коло + синус-гліф)
    scx = sin_x + 6
    f.append(circle(scx, op_cy, 12, fill=BG, stroke=INK, sw=1.6))
    f.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f S %.1f %.1f, %.1f %.1f" '
             'fill="none" stroke="%s" stroke-width="1.5"/>' % (
                 scx - 7, op_cy, scx - 4, op_cy - 7, scx - 1, op_cy - 7, scx, op_cy,
                 scx + 4, op_cy + 7, scx + 7, op_cy, INK))
    f.append(line(sin_x + 6, op_cy + 12, sin_x + 6, gnd_y, color=INK, sw=1.4))
    f.append(line(sin_x + 6, op_cy - 12, sin_x + 6, op_cy - 60, color=INK, sw=1.4))
    f.append(line(sin_x + 6, op_cy - 60, 250, op_cy - 60, color=INK, sw=1.4))
    # розділовий C_in на гілці входу
    cs, cl, cr = cap_h(250, op_cy - 60, "C_in")
    f.append(cs)
    # від C_in вертикально вниз на вузол «+» (де сходиться Vref)
    f.append(line(cr, op_cy - 60, op_cx - 70, op_cy - 60, color=INK, sw=1.6))
    f.append(line(op_cx - 70, op_cy - 60, op_cx - 70, op_cy, color=INK, sw=1.6))
    f.append(node(op_cx - 70, op_cy))
    f.append(text(op_cx - 70, op_cy - 64, "вузол «+»: DC=Vref, AC=сигнал", size=10, color=MUTED, anchor="middle"))

    # ── сам ОП ──
    so, intop, inbot, outp = opamp(op_cx, op_cy, size=54, vplus_top=True)
    f.append(so)
    # вузол «+» (op_cx-70, op_cy) → L-маршрут до верхнього входу (без діагоналі/спур)
    f.append(line(op_cx - 70, op_cy, op_cx - 70, intop[1], color=INK, sw=1.6))
    f.append(line(op_cx - 70, intop[1], intop[0], intop[1], color=INK, sw=1.6))
    # живлення ОП — короткі стуби з підписами (щоб не захаращувати схему)
    f.append(line(op_cx, op_cy - 27, op_cx, op_cy - 50, color=POS, sw=1.2, dash="3,3"))
    f.append(text(op_cx + 4, op_cy - 54, "Vcc", size=10, color=POS, anchor="start"))
    f.append(line(op_cx, op_cy + 27, op_cx, op_cy + 50, color=INK, sw=1.2, dash="3,3"))
    f.append(text(op_cx + 4, op_cy + 60, "0", size=10, anchor="start"))

    # ── зворотний зв'язок: Rf із виходу на «−», Rg з «−» на C_g → земля ──
    out_x = outp[0]
    f.append(line(out_x, op_cy, out_x + 40, op_cy, color=INK, sw=1.6))
    fb_x = out_x + 40
    f.append(node(fb_x, op_cy))
    # Rf горизонтально назад поверх ОП
    fb_top = op_cy + 70
    f.append(line(fb_x, op_cy, fb_x, fb_top, color=INK, sw=1.6))
    srf, rfl, rfr = res_h(op_cx - 40, fb_top, 80, "Rf", lab_dy=14)
    f.append(srf)
    f.append(line(fb_x, fb_top, rfr, fb_top, color=INK, sw=1.6))
    minus_x = op_cx - 55          # окрема колонка вузла «−» (праворуч від колонки «+»)
    f.append(line(rfl, fb_top, minus_x, fb_top, color=INK, sw=1.6))
    f.append(line(minus_x, fb_top, minus_x, inbot[1], color=INK, sw=1.6))
    f.append(line(minus_x, inbot[1], inbot[0], inbot[1], color=INK, sw=1.6))
    f.append(node(minus_x, fb_top))
    # Rg + C_g униз на землю
    rg_y = fb_top + 16
    srg, rgt, rgb = res_v(minus_x, rg_y, 50, "Rg", side="left")
    f.append(srg)
    f.append(line(minus_x, fb_top, minus_x, rg_y, color=INK, sw=1.6))
    f.append(line(minus_x, rgb, minus_x, rgb + 14, color=INK, sw=1.6))
    f.append(line(minus_x - 12, rgb + 14, minus_x + 12, rgb + 14, color=INK, sw=2.4))
    # C_g друга планка + до землі
    f.append(line(minus_x - 12, rgb + 26, minus_x + 12, rgb + 26, color=INK, sw=2.4))
    f.append(line(minus_x, rgb + 26, minus_x, gnd_y, color=INK, sw=1.6))
    f.append(text(minus_x - 16, rgb + 24, "C_g", size=11, anchor="end"))

    # ── вихід через розділовий C_out → навантаження ──
    sc, ol, orr = cap_h(fb_x + 16, op_cy, "C_out")
    f.append(line(fb_x, op_cy, fb_x + 16, op_cy, color=INK, sw=1.6))
    f.append(sc)
    f.append(line(orr, op_cy, 745, op_cy, color=INK, sw=1.6))
    f.append(text(752, op_cy + 4, "Vout~", size=12, bold=True, anchor="start"))

    # підпис-нагадування внизу
    note = ("DC: «+»=Vref → віртуальне коротке тримає «−»=Vref → вихід сидить на Vref (по постійці ×1).\n"
            "AC: C_g «заземлює» Rg → підсилення сигналу 1 + Rf/Rg; C_in, C_out пропускають лише змінну складову.")
    f.append(fitbox(70, gnd_y + 22, 690, 42, note, size=11, fill="#f0f7f1", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "single-supply-noninv.svg"), W, H, *f)


# ── фігура 3: два погляди на вузол — постійка vs змінна ───────────────────────
def fig_dc_ac_split():
    W, H = 720, 300
    f = [text(W / 2, 26, "Один вузол — два погляди: ОП ставить робочу точку, сигнал гойдається довкола неї",
              size=14.5, bold=True)]

    # ліворуч: погляд по DC
    lx = 60
    f.append(fitbox(lx, 60, 280, 60, "ПОГЛЯД ПО ПОСТІЙЦІ (DC)", size=12, bold=True,
                    fill="#eef1f5", stroke=MUTED, color=INK))
    f.append(text(lx + 140, 150,
                  "C_in, C_out, C_g — розрив", size=12))
    f.append(text(lx + 140, 172,
                  "(конденсатор не пропускає DC)", size=11, color=MUTED))
    f.append(text(lx + 140, 200, "«+» = Vref", size=13, color=FIELD, bold=True))
    f.append(text(lx + 140, 224, "віртуальне коротке → «−» = Vref", size=11))
    f.append(text(lx + 140, 248, "вихід сидить на Vref ≈ Vcc/2", size=12, bold=True))
    f.append(text(lx + 140, 272, "підсилення по DC = ×1", size=11, color=MUTED))

    # роздільник
    f.append(line(W / 2, 56, W / 2, 284, color=MUTED, sw=1.2, dash="4,4"))

    # праворуч: погляд по AC
    rx = W / 2 + 30
    f.append(fitbox(rx, 60, 280, 60, "ПОГЛЯД ПО ЗМІННІЙ (AC)", size=12, bold=True,
                    fill="#f0f7f1", stroke=FIELD, color=INK))
    f.append(text(rx + 140, 150, "C_in, C_out, C_g — коротке", size=12))
    f.append(text(rx + 140, 172, "(конденсатор для сигналу = дріт)", size=11, color=MUTED))
    f.append(text(rx + 140, 200, "Vref «зникає» (це нерухомий рівень)", size=11))
    f.append(text(rx + 140, 224, "Rg тепер «на землі» через C_g", size=11))
    f.append(text(rx + 140, 248, "підсилення сигналу = 1 + Rf/Rg", size=13, color=POS, bold=True))
    f.append(text(rx + 140, 272, "схема = звичайний неінвертуючий", size=11, color=MUTED))

    render(os.path.join(IMG, "dc-ac-views.svg"), W, H, *f)


if __name__ == "__main__":
    fig_clip_vs_shift()
    print("OK: img/clip-vs-shift.svg")
    fig_topology()
    print("OK: img/single-supply-noninv.svg")
    fig_dc_ac_split()
    print("OK: img/dc-ac-views.svg")
