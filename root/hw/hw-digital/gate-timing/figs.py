# -*- coding: utf-8 -*-
# Фігури теми «Часові параметри вентилів». svgkit імпортуємо, не переписуємо (§5 AUTHORING).
# Вивід — у ./img/. Після запуску: python ../../../../scripts/svgcheck.py img --min-font 8
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. tpLH і tpHL: дві різні затримки, обидві по 50% ────────────────────────
def fig_tplh_tphl():
    W, H = 720, 380
    L, R = 70, 690          # межі осі часу
    yin_hi, yin_lo = 70, 130     # вхід: верх/низ
    yout_hi, yout_lo = 230, 290  # вихід
    mid_in = (yin_hi + yin_lo) / 2
    mid_out = (yout_hi + yout_lo) / 2
    # моменти подій
    t_rise_in = 200     # вхід пішов угору
    t_fall_in = 470     # вхід пішов униз
    # вентиль-інвертор: вхід↑ → вихід↓ (це tpHL виходу), вхід↓ → вихід↑ (tpLH)
    d_hl = 55           # затримка спаду виходу
    d_lh = 90           # затримка наростання виходу (більша — асиметрія)
    el = []
    el.append(text(W / 2, 26, "Дві затримки одного вентиля, обидві по рівню 50%", size=16, bold=True))
    el.append(text(L - 14, mid_in + 5, "вхід", size=12, color=MUTED, anchor="end"))
    el.append(text(L - 14, mid_out + 5, "вихід", size=12, color=MUTED, anchor="end"))
    # вхідний сигнал (інвертор: спершу 0, стрибок угору на t_rise_in, спад на t_fall_in)
    inp = [(L, yin_lo), (t_rise_in, yin_lo), (t_rise_in, yin_hi),
           (t_fall_in, yin_hi), (t_fall_in, yin_lo), (R, yin_lo)]
    el.append(_poly(inp, NEG, 2.4))
    # вихід інвертора: спершу 1; вхід↑ → через d_hl вихід↓; вхід↓ → через d_lh вихід↑
    out = [(L, yout_hi), (t_rise_in + d_hl, yout_hi), (t_rise_in + d_hl, yout_lo),
           (t_fall_in + d_lh, yout_lo), (t_fall_in + d_lh, yout_hi), (R, yout_hi)]
    el.append(_poly(out, FIELD, 2.4))
    # лінії 50% та виміри
    for tx in (t_rise_in, t_rise_in + d_hl):
        el.append(line(tx, mid_in - 6, tx, mid_out + 24, color=MUTED, sw=1, dash="3,3"))
    for tx in (t_fall_in, t_fall_in + d_lh):
        el.append(line(tx, mid_in - 6, tx, mid_out + 24, color=MUTED, sw=1, dash="3,3"))
    # мітка tpHL
    yb = mid_out + 18
    el.append(arrow(t_rise_in, yb, t_rise_in + d_hl, yb, color=INK, sw=1.8))
    el.append(arrow(t_rise_in + d_hl, yb, t_rise_in, yb, color=INK, sw=1.8))
    b, w, h = textbox((t_rise_in + d_hl / 2), yb + 30, "tpHL", size=13, bold=True,
                      fill="#eafaf0", stroke=FIELD)
    el.append(b)
    # мітка tpLH
    el.append(arrow(t_fall_in, yb, t_fall_in + d_lh, yb, color=INK, sw=1.8))
    el.append(arrow(t_fall_in + d_lh, yb, t_fall_in, yb, color=INK, sw=1.8))
    b, w, h = textbox((t_fall_in + d_lh / 2), yb + 30, "tpLH", size=13, bold=True,
                      fill="#eafaf0", stroke=FIELD)
    el.append(b)
    # підпис 50%
    el.append(text(R + 2, mid_in + 4, "50%", size=11, color=MUTED, anchor="start"))
    el.append(text(R + 2, mid_out + 4, "50%", size=11, color=MUTED, anchor="start"))
    # висновок
    b, w, h = fitbox(L, 345, R - L, 26,
                     "Затримку міряють між точками 50% входу й виходу. tpLH ≠ tpHL — вентиль перемикається в два боки неоднаково.",
                     size=12.5, fill="#f4f6f8", stroke=MUTED), 0, 0
    el.append(b)
    render(os.path.join(OUT, "tplh-tphl.svg"), W, H, *el)


# ── 2. Затримки складаються вздовж ланцюга ───────────────────────────────────
def fig_chain():
    W, H = 720, 320
    el = []
    el.append(text(W / 2, 26, "Уздовж ланцюга затримки додаються", size=16, bold=True))
    # чотири вентилі в ряд
    n = 4
    gx0, gy = 80, 120
    gw, gh, gap = 90, 56, 70
    delays = ["3 нс", "5 нс", "4 нс", "6 нс"]
    names = ["A", "B", "C", "D"]
    cx = []
    for i in range(n):
        x = gx0 + i * (gw + gap)
        el.append(rect(x, gy, gw, gh, fill="#eef2ff", stroke=NEG, sw=2))
        el.append(text(x + gw / 2, gy + 26, names[i], size=15, bold=True))
        el.append(text(x + gw / 2, gy + 45, "tpd " + delays[i], size=11.5, color=MUTED))
        cx.append(x + gw / 2)
        if i < n - 1:
            el.append(arrow(x + gw, gy + gh / 2, x + gw + gap, gy + gh / 2, color=INK, sw=2))
    # вхід/вихід стрілки
    el.append(arrow(gx0 - 38, gy + gh / 2, gx0, gy + gh / 2, color=INK, sw=2))
    el.append(text(gx0 - 40, gy + gh / 2 - 8, "вхід", size=11, color=MUTED, anchor="end"))
    xend = gx0 + (n - 1) * (gw + gap) + gw
    el.append(arrow(xend, gy + gh / 2, xend + 38, gy + gh / 2, color=INK, sw=2))
    el.append(text(xend + 40, gy + gh / 2 - 8, "вихід", size=11, color=MUTED, anchor="start"))
    # сумарна дужка під ланцюгом
    yb = gy + gh + 40
    el.append(arrow(cx[0], yb, cx[-1], yb, color=POS, sw=1.8))
    el.append(arrow(cx[-1], yb, cx[0], yb, color=POS, sw=1.8))
    el.append(line(cx[0], gy + gh + 6, cx[0], yb, color=MUTED, sw=1, dash="3,3"))
    el.append(line(cx[-1], gy + gh + 6, cx[-1], yb, color=MUTED, sw=1, dash="3,3"))
    b, w, h = textbox(W / 2, yb + 34,
                      "повна затримка шляху = 3 + 5 + 4 + 6 = 18 нс",
                      size=14, bold=True, fill="#fdecea", stroke=POS)
    el.append(b)
    b, w, h = fitbox(70, yb + 64, W - 140, 26,
                     "Вихід ланцюга «застигає» лише через суму всіх затримок на шляху — це і є нижня межа для періоду такту.",
                     size=12.5, fill="#f4f6f8", stroke=MUTED), 0, 0
    el.append(b)
    render(os.path.join(OUT, "chain-accumulate.svg"), W, H, *el)


# ── 3. Мінімальна (contamination) і максимальна (propagation) затримки ────────
def fig_contam():
    W, H = 720, 360
    L, R = 70, 690
    yin_hi, yin_lo = 64, 112
    yout_hi, yout_lo = 200, 248
    t_in = 230
    d_min = 50    # contamination delay: коли вихід ПОЧИНАЄ мінятися
    d_max = 140   # propagation delay: коли вихід ГАРАНТОВАНО усталився
    el = []
    el.append(text(W / 2, 26, "Дві межі: коли вихід почав мінятися і коли вже усталився", size=15.5, bold=True))
    el.append(text(L - 14, (yin_hi + yin_lo) / 2 + 5, "вхід", size=12, color=MUTED, anchor="end"))
    el.append(text(L - 14, (yout_hi + yout_lo) / 2 + 5, "вихід", size=12, color=MUTED, anchor="end"))
    # вхід — один фронт угору
    el.append(_poly([(L, yin_lo), (t_in, yin_lo), (t_in, yin_hi), (R, yin_hi)], NEG, 2.4))
    # зона невизначеності виходу (між d_min і d_max) — заштрихована
    x1, x2 = t_in + d_min, t_in + d_max
    el.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff3cd" stroke="#d39e00" stroke-width="1.2" rx="3"/>'
              % (x1, yout_hi - 6, x2 - x1, (yout_lo - yout_hi) + 12))
    # вихід: стабільний старий рівень до x1, невизначений до x2, новий рівень після
    el.append(line(L, yout_lo, x1, yout_lo, color=FIELD, sw=2.4))           # старий рівень
    el.append(line(x2, yout_hi, R, yout_hi, color=FIELD, sw=2.4))           # новий рівень
    el.append(text((x1 + x2) / 2, (yout_hi + yout_lo) / 2 + 4, "?", size=20, bold=True, color="#b8860b"))
    # вертикальні маркери
    el.append(line(t_in, yin_lo + 8, t_in, yout_lo + 44, color=MUTED, sw=1, dash="3,3"))
    el.append(line(x1, yout_hi - 30, x1, yout_lo + 44, color="#d39e00", sw=1.2, dash="4,3"))
    el.append(line(x2, yout_hi - 30, x2, yout_lo + 80, color="#d39e00", sw=1.2, dash="4,3"))
    # мітки
    yb = yout_lo + 44
    el.append(arrow(t_in, yb, x1, yb, color=INK, sw=1.7))
    el.append(arrow(x1, yb, t_in, yb, color=INK, sw=1.7))
    b, w, h = textbox((t_in + x1) / 2, yb + 22, "tcd (мін.)", size=12, bold=True,
                      fill="#eafaf0", stroke=FIELD)
    el.append(b)
    yb2 = yout_lo + 80
    el.append(arrow(t_in, yb2, x2, yb2, color=INK, sw=1.7))
    el.append(arrow(x2, yb2, t_in, yb2, color=INK, sw=1.7))
    el.append(line(t_in, yb, t_in, yb2, color=MUTED, sw=1, dash="2,2"))
    b, w, h = textbox((t_in + x2) / 2, yb2 + 22, "tpd (макс.)", size=12, bold=True,
                      fill="#fdecea", stroke=POS)
    el.append(b)
    render(os.path.join(OUT, "contam-vs-prop.svg"), W, H, *el)


# ── 4. Бюджет такту: усе має влізти в період ─────────────────────────────────
def fig_budget():
    W, H = 720, 300
    L = 70
    bar_y = 150
    bar_h = 46
    total = 600          # піксельна ширина періоду
    # частки (умовні нс), масштабуємо у пікселі
    parts = [("tcq", 60, "#eef2ff", NEG),       # затримка регістра після фронту
             ("логіка (шлях)", 360, "#fdecea", POS),  # сума затримок комбінаційної логіки
             ("setup", 110, "#fff3cd", "#d39e00"),    # запас перед наступним фронтом
             ("запас", 70, "#eafaf0", FIELD)]         # slack
    el = []
    el.append(text(W / 2, 26, "Один період такту мусить умістити весь шлях", size=16, bold=True))
    # фронти такту
    el.append(line(L, bar_y - 34, L, bar_y + bar_h + 30, color=INK, sw=2))
    el.append(line(L + total, bar_y - 34, L + total, bar_y + bar_h + 30, color=INK, sw=2))
    el.append(text(L, bar_y - 42, "фронт", size=11, color=MUTED))
    el.append(text(L + total, bar_y - 42, "наступний фронт", size=11, color=MUTED, anchor="middle"))
    # період-дужка
    el.append(arrow(L, bar_y - 24, L + total, bar_y - 24, color=INK, sw=1.6))
    el.append(arrow(L + total, bar_y - 24, L, bar_y - 24, color=INK, sw=1.6))
    el.append(text(L + total / 2, bar_y - 30, "період такту T", size=13, bold=True))
    # частки бруска
    x = L
    for name, wpx, fill, stroke in parts:
        el.append(rect(x, bar_y, wpx, bar_h, fill=fill, stroke=stroke, sw=2, rx=4))
        fs = fit_font(name, wpx - 6, 12.5, True)
        el.append(text(x + wpx / 2, bar_y + bar_h / 2 + 5, name, size=fs, bold=True))
        x += wpx
    # нерівність
    b, w, h = textbox(W / 2, bar_y + bar_h + 52,
                      "T ≥ tcq + затримка_логіки + setup",
                      size=15, bold=True, fill="#f4f6f8", stroke=INK)
    el.append(b)
    b, w, h = fitbox(L, bar_y + bar_h + 78, total, 24,
                     "Якщо логіка довша — період мусить рости (такт повільнішає). «Запас» (slack) — те, що лишилося.",
                     size=12, fill=BG, stroke=MUTED), 0, 0
    el.append(b)
    render(os.path.join(OUT, "timing-budget.svg"), W, H, *el)


# ── 5. Вставка proj: кільце інверторів + захоплення частоти мікроконтролером ──
def fig_ring_setup():
    """Непарне кільце інверторів самозбуджується; вихід одного вузла йде на
    лічильний вхід МК. МК рахує частоту → назад до затримки вентиля."""
    W, H = 760, 400
    el = []
    el.append(text(W / 2, 26, "Кільце інверторів коливається саме; МК ловить частоту",
                   size=16, bold=True))
    # ── ланцюг з N=5 інверторів по колу ──
    cx, cy, rad = 250, 210, 118          # центр і радіус кола інверторів
    import math
    N = 5
    nodes = []
    for i in range(N):
        ang = -math.pi / 2 + i * 2 * math.pi / N     # старт зверху, за годинником
        nx = cx + rad * math.cos(ang)
        ny = cy + rad * math.sin(ang)
        nodes.append((nx, ny))
    # трикутники-інвертори у вузлах, з'єднані по колу дугами-стрілками
    for i in range(N):
        x0, y0 = nodes[i]
        x1, y1 = nodes[(i + 1) % N]
        el.append(line(x0, y0, x1, y1, color=LINE, sw=1.8))
        el.append('<polyline points="%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" '
                  'stroke-width="1.8" marker-end="url(#arrow)"/>'
                  % ((x0 + x1) / 2 - 0.6 * (x1 - x0) / 6, (y0 + y1) / 2 - 0.6 * (y1 - y0) / 6,
                     (x0 + x1) / 2, (y0 + y1) / 2, LINE))
    for i, (nx, ny) in enumerate(nodes):
        # трикутник інвертора, вершиною вздовж кола
        ang = -math.pi / 2 + i * 2 * math.pi / N
        dx, dy = math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2)   # дотична
        s = 16
        p1 = (nx - dx * s - (nx - cx) / rad * s * 0.7, ny - dy * s - (ny - cy) / rad * s * 0.7)
        p2 = (nx + dx * s - (nx - cx) / rad * s * 0.7, ny + dy * s - (ny - cy) / rad * s * 0.7)
        p3 = (nx + (nx - cx) / rad * s * 1.1, ny + (ny - cy) / rad * s * 1.1)
        el.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#eef2ff" '
                  'stroke="%s" stroke-width="1.8"/>' % (p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], NEG))
        el.append(circle(p3[0], p3[1], 3.2, fill=BG, stroke=NEG, sw=1.6))   # кружок «НЕ»
    el.append(text(cx, cy - 4, "N = 5", size=15, bold=True, color=NEG))
    el.append(text(cx, cy + 16, "інверторів", size=12, color=MUTED))
    el.append(text(cx, cy + 32, "(непарне!)", size=11, color=POS))
    # відвід з одного вузла до МК
    tap = nodes[0]
    el.append(circle(tap[0], tap[1], 4.5, fill=POS, stroke=BG, sw=1.5))
    mx = 560
    el.append(line(tap[0], tap[1], mx - 90, tap[1], color=POS, sw=1.8))
    el.append('<polyline points="%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" '
              'stroke-width="1.8" marker-end="url(#arrow)"/>'
              % (mx - 130, tap[1], mx - 88, tap[1], POS))
    el.append(text((tap[0] + mx - 90) / 2, tap[1] - 8, "відвід", size=11, color=POS))
    # блок МК
    b, bw, bh = textbox(mx + 20, 150, "МК\nлічильний вхід\n(input capture)",
                        size=12.5, fill="#eafaf0", stroke=FIELD, bold=False)
    el.append(b)
    # формула-висновок під МК
    el.append(fitbox(mx - 90, 220, 240, 96,
                     "f = 1 / (2·N·tpd)\n↓ перевертаємо\ntpd = 1 / (2·N·f)\nодин вентиль!",
                     size=13.5, fill="#f4f6f8", stroke=INK, bold=True))
    render(os.path.join(OUT, "ring-setup.svg"), W, H, *el)


def fig_ring_period():
    """ЧОМУ множник 2: за один період фронт оббігає кільце ДВІЧІ.
    Показуємо рівень одного вузла у часі й що півперіод = N·tpd."""
    W, H = 740, 340
    L, R = 70, 690
    y_hi, y_lo = 90, 150
    el = []
    el.append(text(W / 2, 26, "Один період — це два оббіги кільця (тому множник 2)",
                   size=16, bold=True))
    el.append(text(L - 12, (y_hi + y_lo) / 2 + 5, "вузол", size=12, color=MUTED, anchor="end"))
    # прямокутний сигнал: півперіод N·tpd високо, N·tpd низько
    half = (R - L) / 4        # ширина півперіоду на екрані
    xs = [L, L + half, L + half, L + 2 * half, L + 2 * half, L + 3 * half, L + 3 * half, R]
    ys = [y_lo, y_lo, y_hi, y_hi, y_lo, y_lo, y_hi, y_hi]
    pts = list(zip(xs, ys))
    el.append(_poly(pts, FIELD, 2.6))
    # позначки півперіодів
    for k, (xa, xb, lab, why) in enumerate([
            (L, L + half, "N·tpd", "фронт пройшов усі N вентилів раз"),
            (L + half, L + 2 * half, "N·tpd", "…і ще раз, уже протилежним рівнем"),
            (L + 2 * half, L + 3 * half, "N·tpd", "")]):
        el.append(line(xa, 185, xb, 185, color=MUTED, sw=1.4))
        el.append(line(xa, 180, xa, 190, color=MUTED, sw=1.4))
        el.append(line(xb, 180, xb, 190, color=MUTED, sw=1.4))
        el.append(text((xa + xb) / 2, 202, lab, size=12.5, bold=True, color=INK))
    # повний період = 2·N·tpd (перші два півперіоди)
    el.append(line(L, 240, L + 2 * half, 240, color=POS, sw=2))
    el.append(line(L, 234, L, 246, color=POS, sw=2))
    el.append(line(L + 2 * half, 234, L + 2 * half, 246, color=POS, sw=2))
    el.append(text(L + half, 258, "T = 2·N·tpd  (повний період)", size=13.5, bold=True, color=POS))
    # пояснення внизу
    el.append(fitbox(L, 282, R - L, 34,
                     "Кожен вузол міняє рівень щоразу, коли повз нього оббіг проходить фронт. "
                     "Щоб вернутися у ТОЙ САМИЙ рівень, фронт мусить обійти кільце двічі — звідси множник 2.",
                     size=12, fill=BG, stroke=MUTED))
    render(os.path.join(OUT, "ring-period.svg"), W, H, *el)


# ── допоміжне: ламана лінія (для часових діаграм) ────────────────────────────
def _poly(pts, color, sw):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>' % (d, color, sw)


if __name__ == "__main__":
    fig_tplh_tphl()
    fig_chain()
    fig_contam()
    fig_budget()
    fig_ring_setup()
    fig_ring_period()
    print("OK: 6 figures ->", OUT)
