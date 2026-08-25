# -*- coding: utf-8 -*-
"""Фігури до теми «Смуга повної потужності ОП» (аналогова електроніка, кутом теорії кіл).
Фігури:
  slew-clip.svg  — синус, що вкладається у швидкість (цілий), проти синуса на повний
                   розмах тієї ж частоти, який ламається в трикутник (крутість > SR).
  two-walls.svg  — площина «частота × амплітуда»: похила лінія FPBW (стеля швидкості)
                   й горизонталь GBW (стеля смуги); робоча зона під обома.
  tail-charge.svg — (для вставки hist-slew-rate) фізичний механізм SR = I/C: сталий
                   хвостовий струм пари перекидається в одну вітку й тече в конденсатор
                   корекції; напруга на ньому росте не швидше за I/C.
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def slew_clip():
    """Дві панелі: малий розмах укладається у швидкість (цілий синус),
    повний розмах тієї ж частоти ламається в трикутник (схили зрізані під SR)."""
    W, H = 720, 410
    p = []
    pw = (W - 50) / 2.0

    def panel(x0, full, lbl, note):
        out = []
        cx = x0 + pw / 2
        ax0, ax1 = x0 + 34, x0 + pw - 24
        yc = 200
        span = ax1 - ax0
        col = POS if full else FIELD
        out.append(text(cx, 56, lbl, size=14, bold=True, color=col))
        # вісь часу
        out.append(line(ax0 - 8, yc, ax1 + 8, yc, color=MUTED, sw=1))
        amp = 120 if full else 52      # піксельний розмах: повний vs малий
        slope_cap = 2.05               # стеля крутості у пікс/крок (та сама в обох панелях!)
        # ідеальний синус (пунктир) і реальний вихід (суцільний)
        ideal = []
        real = []
        N = 320
        prev = None
        for k in range(N + 1):
            t = k / N
            xx = ax0 + span * t
            s = math.sin(2 * math.pi * 1.5 * t)
            yi = yc - amp * s
            ideal.append((xx, yi))
            if prev is None:
                yr = yi
            else:
                want = yi - prev
                step = max(-slope_cap * (span / N) * 0.0 - slope_cap, min(slope_cap, want))
                # обмежуємо приріст за модулем стелею slope_cap (пікс на крок)
                if want > slope_cap:
                    yr = prev + slope_cap
                elif want < -slope_cap:
                    yr = prev - slope_cap
                else:
                    yr = yi
            real.append((xx, yr))
            prev = yr
        d_i = "M" + " L".join("%.1f %.1f" % q for q in ideal)
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.3" stroke-dasharray="4 3"/>' % (d_i, MUTED))
        d_r = "M" + " L".join("%.1f %.1f" % q for q in real)
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d_r, col))
        # позначка розмаху
        out.append(line(ax0 - 2, yc - amp, ax0 - 2, yc + amp, color=col, sw=1.4, dash="2 3"))
        out.append(text(ax0 - 10, yc, "V_p", size=11, bold=True, color=col, anchor="end"))
        out.append(text(cx, 348, note, size=11, color=MUTED))
        return out

    p += panel(20, False, "малий розмах — цілий синус", "крутість 2π·f·V_p < SR → вихід іде за сигналом")
    p += panel(20 + pw + 10, True, "повний розмах — трикутник", "крутість 2π·f·V_p > SR → схили зрізані під SR")
    p.append(line(W / 2, 70, W / 2, 360, color=MUTED, sw=1, dash="3 4"))

    b, _, _ = textbox(W / 2, 384,
                      "Та сама частота й та сама стеля швидкості SR в обох панелях — різниться лише розмах.\n"
                      "Малий сигнал укладається у швидкість; повний робить схили надто крутими — синус ламається в трикутник.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'slew-clip.svg'), W, H, *p,
           title="Чому ламається саме повний розмах: крутість синуса проти стелі SR")


def two_walls():
    """Площина «частота (лог) × амплітуда розмаху»: похила лінія FPBW = SR/(2π·V_p)
    і горизонталь смуги GBW/G. Робоча зона — під обома; підписано, де яка кусає."""
    W, H = 720, 452
    p = []
    ox, oy = 95, 330
    ax_w, ax_h = 545, 250
    # осі
    p.append(arrow(ox, oy, ox + ax_w + 12, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - ax_h - 12, color=INK, sw=1.8))
    p.append(text(ox + ax_w + 8, oy + 20, "частота (лог)", size=13, bold=True, anchor="end"))
    p.append(text(ox - 8, oy - ax_h - 2, "розмах V_p", size=13, bold=True, anchor="start"))

    # вертикаль смуги GBW (стеля смуги, від амплітуди НЕ залежить)
    gbw_x = ox + ax_w * 0.72
    p.append(line(gbw_x, oy, gbw_x, oy - ax_h, color=NEG, sw=2.6))
    p.append(text(gbw_x + 6, oy - ax_h + 14, "смуга GBW/G", size=12, bold=True, color=NEG, anchor="start"))
    p.append(text(gbw_x + 6, oy - ax_h + 30, "(стеля малих сигналів)", size=10, color=NEG, anchor="start"))

    # похила FPBW: V_p = SR/(2π·f) → крива спадає з частотою (на лог-осі — крива вниз)
    pts = []
    N = 200
    # параметризуємо f по лог-осі t∈[0..1]; V_p ∝ 1/f
    for k in range(N + 1):
        t = 0.06 + 0.92 * k / N
        xx = ox + ax_w * t
        # 1/f у лог-частоті: f = 10^(t·D); V_p ∝ 10^(-t·D) — спад
        vp = 0.95 * (10 ** (-(t - 0.06) * 1.15))
        yy = oy - ax_h * min(0.97, vp)
        pts.append((xx, yy))
    d = "M" + " L".join("%.1f %.1f" % q for q in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, POS))
    p.append(text(ox + 16, oy - ax_h * 0.86, "FPBW = SR/(2π·V_p)", size=12, bold=True, color=POS, anchor="start"))
    p.append(text(ox + 16, oy - ax_h * 0.86 + 16, "(стеля повного розмаху)", size=10, color=POS, anchor="start"))

    # робоча зона — світла заливка під обома лініями (полігон до перетину)
    # знайдемо точку, де похила сходить нижче, ніж дозволяє вертикаль на даній x
    poly = ["%.1f,%.1f" % (ox, oy)]
    for (xx, yy) in pts:
        if xx <= gbw_x:
            poly.append("%.1f,%.1f" % (xx, max(yy, oy - ax_h)))
        else:
            break
    poly.append("%.1f,%.1f" % (gbw_x, oy))
    p.insert(0, '<polygon points="%s" fill="#eafaf1" stroke="none"/>' % " ".join(poly))
    p.append(text(ox + ax_w * 0.30, oy - 40, "робоча зона", size=13, bold=True, color=FIELD, anchor="middle"))
    p.append(text(ox + ax_w * 0.30, oy - 24, "(під обома стелями)", size=10, color=FIELD, anchor="middle"))

    # дві точки-приклади: великий розмах (кусає похила), малий (кусає вертикаль)
    bx = ox + ax_w * 0.50
    p.append(circle(bx, oy - ax_h * 0.66, 4, fill=POS, stroke=POS))
    p.append(text(bx, oy - ax_h * 0.66 - 10, "великий сигнал → ріже швидкість", size=10.5, bold=True, color=POS, anchor="middle"))
    sx = ox + ax_w * 0.66
    p.append(circle(sx, oy - ax_h * 0.12, 4, fill=NEG, stroke=NEG))
    p.append(text(sx + 4, oy - ax_h * 0.12 - 10, "малий сигнал → ріже смуга", size=10.5, bold=True, color=NEG, anchor="middle"))

    b, _, _ = textbox(W / 2, 410,
                      "Дві незалежні стелі. Похила (FPBW) обмежує великий розмах і падає з частотою;\n"
                      "вертикаль (смуга) від розмаху не залежить. Сигнал чистий лише під обома —\n"
                      "на ваших частоті й розмаху кусає та стеля, що нижча.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'two-walls.svg'), W, H, *p,
           title="Дві стелі ОП: смуга повної потужності й смуга пропускання")


def tail_charge():
    """Механізм SR = I/C для вставки про походження швидкості наростання.
    Зліва — диф-пара: сталий хвостовий струм I перекинуто весь в одну вітку.
    Той самий струм тече в конденсатор корекції C; напруга на ньому (і на виході)
    росте прямою зі швидкістю I/C — праворуч графік похилого фронту зі стелею."""
    W, H = 720, 430
    p = []

    # ── Ліворуч: спрощена диференційна пара з хвостовим джерелом струму ──
    lx = 150          # центр пари по горизонталі
    yt = 120          # верх (колектори)
    yb = 250          # низ пари (емітери сходяться)
    dx = 46           # розхил віток
    # шина живлення вгорі
    p.append(line(lx - 95, 86, lx + 95, 86, color=MUTED, sw=1.4))
    p.append(text(lx, 78, "+живлення", size=10, color=MUTED))
    # дві вітки-резистори навантаження (схематично прямокутники)
    p.append(rect(lx - dx - 9, 92, 18, 26, fill=FILL, stroke=LINE, sw=1.3, rx=2))
    p.append(rect(lx + dx - 9, 92, 18, 26, fill=FILL, stroke=LINE, sw=1.3, rx=2))
    # транзистори пари — кружки з мітками Q1, Q2
    p.append(circle(lx - dx, yt + 28, 15, fill="#eef2f7", stroke=INK, sw=1.6))
    p.append(text(lx - dx, yt + 32, "Q1", size=11, bold=True))
    p.append(circle(lx + dx, yt + 28, 15, fill="#eef2f7", stroke=INK, sw=1.6))
    p.append(text(lx + dx, yt + 32, "Q2", size=11, bold=True))
    # входи
    p.append(line(lx - dx - 58, yt + 28, lx - dx - 15, yt + 28, color=NEG, sw=1.6))
    p.append(text(lx - dx - 62, yt + 32, "вх+", size=10, bold=True, color=POS, anchor="end"))
    p.append(line(lx + dx + 15, yt + 28, lx + dx + 58, yt + 28, color=NEG, sw=1.6))
    p.append(text(lx + dx + 62, yt + 32, "вх−", size=10, bold=True, color=NEG, anchor="start"))
    # емітери сходяться до спільного вузла → хвостове джерело
    p.append(line(lx - dx, yt + 43, lx - dx, yb, color=LINE, sw=1.4))
    p.append(line(lx + dx, yt + 43, lx + dx, yb, color=LINE, sw=1.4))
    p.append(line(lx - dx, yb, lx + dx, yb, color=LINE, sw=1.4))
    p.append(line(lx, yb, lx, yb + 22, color=LINE, sw=1.4))
    # хвостове джерело струму — кружок із позначкою
    p.append(circle(lx, yb + 38, 16, fill="#fff7e6", stroke=INK, sw=1.6))
    p.append(text(lx, yb + 42, "I", size=13, bold=True))
    p.append(line(lx, yb + 54, lx, yb + 74, color=LINE, sw=1.4))
    p.append(line(lx - 14, yb + 74, lx + 14, yb + 74, color=MUTED, sw=1.4))
    p.append(text(lx, yb + 90, "−живлення", size=10, color=MUTED))
    p.append(text(lx, yb + 14, "сталий хвостовий струм I", size=10.5, bold=True, color=FIELD))

    # увесь струм перекинуто в ліву вітку (Q1): товста стрілка вниз→вгору шляхом струму
    p.append(arrow(lx - dx, yt + 60, lx - dx, yt + 92, color=POS, sw=3.2))
    p.append(text(lx - dx - 6, yt + 78, "весь I", size=10.5, bold=True, color=POS, anchor="end"))
    # відведення від лівого колектора праворуч — до конденсатора корекції
    cyo = 105          # рівень вузла виходу пари
    p.append(line(lx - dx, 92, lx - dx, cyo, color=POS, sw=2.2))
    p.append(arrow(lx - dx, cyo, lx + 150, cyo, color=POS, sw=2.6))
    p.append(text(lx + 60, cyo - 8, "той самий струм I", size=10.5, bold=True, color=POS))

    # ── Конденсатор корекції C ──
    cx = lx + 168
    p.append(line(cx, cyo, cx, cyo + 26, color=LINE, sw=2))
    p.append(line(cx - 18, cyo + 26, cx + 18, cyo + 26, color=LINE, sw=2.6))   # верхня обкладка
    p.append(line(cx - 18, cyo + 36, cx + 18, cyo + 36, color=LINE, sw=2.6))   # нижня обкладка
    p.append(line(cx, cyo + 36, cx, cyo + 70, color=LINE, sw=2))
    p.append(line(cx - 14, cyo + 70, cx + 14, cyo + 70, color=MUTED, sw=1.4))  # земля
    p.append(text(cx + 24, cyo + 30, "C", size=14, bold=True, anchor="start"))
    p.append(text(cx + 24, cyo + 46, "корекції", size=9.5, color=MUTED, anchor="start"))

    # формула стелі — у вільному просторі під конденсатором, праворуч від пари
    b1, _, _ = textbox(cx - 6, 225,
                       "увесь струм I заряджає C\n"
                       "dU/dt = I/C\n"
                       "SR = I/C — вище не вийде",
                       size=11.5, fill="#fdecea", stroke=POS, bold=False)
    p.append(b1)

    # ── Праворуч: графік похилого фронту з обмеженою крутістю ──
    gx0, gy0 = 470, 250    # початок осей графіка
    gw, gh = 210, 150
    p.append(arrow(gx0, gy0, gx0 + gw, gy0, color=INK, sw=1.6))
    p.append(arrow(gx0, gy0, gx0, gy0 - gh, color=INK, sw=1.6))
    p.append(text(gx0 + gw, gy0 + 18, "час", size=11, bold=True, anchor="end"))
    p.append(text(gx0 - 6, gy0 - gh - 2, "U виходу", size=11, bold=True, anchor="middle"))
    # ідеальний миттєвий стрибок (пунктир) — прямовисна стінка
    p.append(line(gx0 + 30, gy0, gx0 + 30, gy0 - gh + 16, color=MUTED, sw=1.4, dash="4 3"))
    p.append(line(gx0 + 30, gy0 - gh + 16, gx0 + gw - 8, gy0 - gh + 16, color=MUTED, sw=1.4, dash="4 3"))
    p.append(text(gx0 + gw - 10, gy0 - gh + 10, "ідеал (миттєво)", size=9.5, color=MUTED, anchor="end"))
    # реальний фронт — похила пряма зі сталим нахилом
    p.append(line(gx0 + 30, gy0, gx0 + 130, gy0 - gh + 16, color=POS, sw=2.8))
    p.append(line(gx0 + 130, gy0 - gh + 16, gx0 + gw - 8, gy0 - gh + 16, color=POS, sw=2.8))
    # позначка нахилу = SR
    p.append(text(gx0 + 96, gy0 - 52, "нахил = SR", size=11, bold=True, color=POS, anchor="middle"))
    p.append(text(gx0 + 96, gy0 - 38, "= I/C", size=10.5, color=POS, anchor="middle"))

    b2, _, _ = textbox(W / 2, 404,
                       "Велика різниця на входах кидає весь сталий струм I в одну вітку — і він цілком тече в C.\n"
                       "Напруга на C (отже й вихід) росте прямою зі швидкістю I/C: це стеля, яку зворотний зв'язок не зрушить.",
                       size=11.5, fill="#eef7f0", stroke=FIELD)
    p.append(b2)

    render(os.path.join(OUT, 'tail-charge.svg'), W, H, *p,
           title="Звідки береться стеля швидкості: хвостовий струм заряджає конденсатор корекції")


if __name__ == '__main__':
    slew_clip()
    two_walls()
    tail_charge()
    print("OK: 3 figures ->", OUT)
