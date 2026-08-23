# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── two-stage: чому LDO ставлять ПІСЛЯ імпульсного ─────────────────────────────
# Ідея: батарея/висока шина → buck (ефективно знижує, але лишає пульсацію) →
# LDO-постстабілізатор (малий перепад, чистить шум) → тиха шина для давача/RF.
# Над кожним блоком — його роль; під шиною — як виглядає напруга в цій точці.

def fig_two_stage():
    W, H = 760, 380
    p = []
    railY = 96
    x_bat = 95
    x_buck = 290
    x_ldo = 510
    x_load = 690

    def block(cx, w, h, title, role, fill, stroke):
        out = fitbox(cx - w / 2, railY - h / 2, w, h, title, size=12,
                     fill=fill, stroke=stroke, sw=1.8, bold=True, color=INK)
        out += text(cx, railY + h / 2 + 16, role, size=10, color=MUTED, italic=True)
        return out

    # шина живлення (зліва направо)
    p.append(line(x_bat + 40, railY, x_buck - 52, railY, color=POS, sw=2.4))
    p.append(line(x_buck + 52, railY, x_ldo - 50, railY, color=POS, sw=2.4))
    p.append(line(x_ldo + 50, railY, x_load - 24, railY, color=FIELD, sw=2.4))

    # джерело
    p.append(block(x_bat, 78, 56, "батарея /\nвисока шина", "16…5 В, плаває", "#f4f6f8", LINE))
    # buck
    p.append(block(x_buck, 100, 64, "імпульсний\n(buck)", "ККД 85–95 %, шумить", "#fdecea", POS))
    # LDO post
    p.append(block(x_ldo, 96, 64, "LDO-пост-\nстабілізатор", "малий перепад, чистить", "#eafaf1", FIELD))
    # навантаження
    p.append(block(x_load, 64, 56, "давач / RF /\nАЦП", "хоче тишу", "#eaf0fd", NEG))

    # ── міні-осцилограми напруги в трьох точках шини ──
    def wave(cx, ripple_amp, hf_amp, color, label):
        y0 = railY + 150
        wlo, whi = cx - 56, cx + 56
        pts = []
        n = 120
        for i in range(n + 1):
            t = i / n
            x = wlo + t * (whi - wlo)
            # повільна пульсація + швидкі голки
            v = ripple_amp * math.sin(2 * math.pi * 2.2 * t)
            v += hf_amp * math.sin(2 * math.pi * 22 * t)
            pts.append("%.1f,%.1f" % (x, y0 - v))
        out = line(wlo, y0, whi, y0, color="#cfd6df", sw=1.0)
        out += ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>'
                % (" ".join(pts), color))
        out += text(cx, y0 + 30, label, size=10, color=MUTED)
        return out

    p.append(wave(x_buck, 14, 7, POS, "пульсація + голки"))
    p.append(wave(x_ldo, 2.0, 1.2, FIELD, "майже рівно"))

    # стрілка «постстабілізатор зрізає пульсацію»
    p.append(arrow(x_buck + 60, railY + 150, x_ldo - 60, railY + 150, color=MUTED, sw=1.6))
    p.append(text((x_buck + x_ldo) / 2, railY + 140, "LDO зрізає залишок", size=10,
                  color=MUTED, italic=True))

    p.append(text(W / 2, H - 12,
                  "важку роботу робить імпульсний; останній, тихий вольт додає LDO",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-stage.svg"), W, H, *p,
           title="LDO після імпульсного: ефективність плюс чистота")


# ── psrr-vs-freq: PSRR падає з частотою, а пульсація buck лежить там, де ще тримає ─
# Ідея: PSRR(f) — висока на постійці/низьких f, з якоїсь частоти спадає (-20 дБ/дек),
# а на ВЧ упирається у власний шум. Позначити смугу пульсації buck (0.5–3 МГц):
# саме там вирішується, скільки LDO зріже.

def fig_psrr():
    W, H = 740, 430
    ox, oy = 72, 330
    aw, ah = 600, 270
    p = []

    flo, fhi = 1e2, 1e8
    def xpos(f):
        return ox + (math.log10(f) - math.log10(flo)) / (math.log10(fhi) - math.log10(flo)) * aw
    # PSRR від 0 дБ (низ) до 90 дБ (верх)
    glo, ghi = 0.0, 90.0
    def ypos(g):
        return oy - (g - glo) / (ghi - glo) * ah

    # сітка частот
    for f, lab in [(1e2, "100 Гц"), (1e3, "1к"), (1e4, "10к"), (1e5, "100к"),
                   (1e6, "1 МГц"), (1e7, "10М"), (1e8, "100М")]:
        gx = xpos(f)
        p.append(line(gx, oy - ah, gx, oy, color="#eef1f5", sw=1.0))
        p.append(line(gx, oy, gx, oy + 5, color=LINE, sw=1.0))
        p.append(text(gx, oy + 18, lab, size=10, color=MUTED))
    # сітка дБ
    for g in [0, 20, 40, 60, 80]:
        gy = ypos(g)
        p.append(line(ox, gy, ox + aw, gy, color="#eef1f5", sw=1.0))
        p.append(text(ox - 8, gy + 4, "%d дБ" % g, size=10, color=MUTED, anchor="end"))

    # ── смуга пульсації buck (0.5–3 МГц) — підсвітити ──
    xa, xb = xpos(5e5), xpos(3e6)
    p.append(rect(xa, oy - ah, xb - xa, ah, fill="#fdecea", stroke="none", sw=0))
    p.append(text((xa + xb) / 2, oy - ah + 14, "пульсація buck", size=10, color=POS, italic=True))

    # ── крива PSRR: плато ~70 дБ до ~1 кГц, спад -20 дБ/дек, дно ~ власний шум 25 дБ ──
    def psrr_curve():
        pts = []
        f_pole = 3e3      # де починає спадати
        plateau = 72.0
        floor = 24.0
        for i in range(0, 241):
            f = flo * (fhi / flo) ** (i / 240.0)
            if f <= f_pole:
                g = plateau
            else:
                g = plateau - 20 * math.log10(f / f_pole)
            g = max(g, floor)
            # легкий підйом дна на самих ВЧ (шум росте) — лишаємо floor
            pts.append("%.1f,%.1f" % (xpos(f), ypos(max(glo, min(ghi, g)))))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                % (" ".join(pts), FIELD))
    p.append(psrr_curve())

    # позначка значення PSRR на частоті buck (≈1 МГц): plateau-20log10(1e6/3e3)≈22→floor 24
    f_mark = 1e6
    g_mark = 24.0
    p.append(circle(xpos(f_mark), ypos(g_mark), 5, fill="#fff", stroke=FIELD, sw=2))
    b, _, _ = textbox(xpos(2.0e6), ypos(46), "тут LDO зріже\nлише ≈24 дБ (×16)", size=11, bold=True,
                      color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1.5, pad=7)
    p.append(b)

    # підпис плато
    b, _, _ = textbox(xpos(6e2), ypos(80), "на низьких f\nдушить сильно (×3000)", size=11, bold=True,
                      color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.5, pad=7)
    p.append(b)
    # підпис дна
    p.append(text(xpos(3e7), ypos(30), "власний шум LDO", size=10, color=MUTED, italic=True))
    p.append(text(xpos(2.0e4), ypos(58), "−20 дБ/декаду", size=10, color=MUTED, italic=True))

    # осі
    p.append(line(ox, oy - ah, ox, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw / 2, oy + 40, "частота пульсації (логарифмічна шкала)", size=12, color=MUTED))
    p.append('<text x="22" y="%.0f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90, 22, %.0f)">PSRR — придушення, дБ</text>'
             % (oy - ah / 2, FONT, MUTED, oy - ah / 2))

    render(os.path.join(OUT, "psrr-vs-freq.svg"), W, H, *p,
           title="PSRR падає з частотою: на частоті buck його вже мало")


# ── headroom-efficiency: ціна постстабілізатора — перепад, і як його тиснути ──
# Ідея: загальний ККД = ККД(buck) × ККД(LDO); ККД(LDO)=Vout/(Vout+Vdrop).
# Дві колонки: великий запас (дорого) і малий запас (ощадно), той самий вихід.

def fig_headroom():
    W, H = 740, 470
    p = []
    base = 300            # рівень землі стовпчиків
    Vout = 3.3

    def column(cx, vin_pre, label, good):
        out = []
        scale = 52.0       # пікселів на вольт
        w = 96
        # корисний вихід (зелений) — завжди той самий
        h_out = Vout * scale
        out.append(rect(cx - w / 2, base - h_out, w, h_out, fill="#eafaf1", stroke=FIELD, sw=1.6, rx=3))
        out.append(text(cx, base - h_out / 2 + 4, "Vout\n3.3 В", size=11, color=FIELD, bold=True))
        # перепад на LDO (червоний) — те, що горить теплом
        vdrop = vin_pre - Vout
        h_drop = vdrop * scale
        out.append(rect(cx - w / 2, base - h_out - h_drop, w, h_drop,
                        fill="#fdecea", stroke=POS, sw=1.6, rx=3))
        out.append(text(cx, base - h_out - h_drop / 2 + 4, "перепад\n%.1f В" % vdrop,
                        size=10, color=POS, bold=True))
        # підпис входу LDO
        out.append(text(cx, base - h_out - h_drop - 12, "вхід LDO %.1f В" % vin_pre,
                        size=10, color=MUTED))
        # вісь землі
        out.append(line(cx - w / 2 - 8, base, cx + w / 2 + 8, base, color=INK, sw=1.4))
        # ефективність саме LDO-ступеня
        eff = Vout / vin_pre * 100
        col = FIELD if good else POS
        b, _, _ = textbox(cx, base + 34, "ККД LDO\n= 3.3 / %.1f\n≈ %.0f %%" % (vin_pre, eff),
                          size=11, bold=True, color=col,
                          fill="#eafaf1" if good else "#fdecea", stroke=col, sw=1.5, pad=7)
        out.append(b)
        out.append(text(cx, base + 92, label, size=11, color=INK, bold=True))
        return "".join(out)

    p.append(column(220, 5.0, "buck дає 5 В → марнотратно", good=False))
    p.append(column(540, 3.6, "buck дає 3.6 В → ощадно", good=True))

    # стрілка-мораль між колонками
    p.append(arrow(320, 150, 440, 150, color=MUTED, sw=1.8))
    p.append(text(380, 140, "опусти\nпередступінь", size=10, color=MUTED, italic=True))

    p.append(text(W / 2, H - 12,
                  "вихід однаковий; чим менший перепад на LDO, тим менше тепла й вищий повний ККД",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "headroom-efficiency.svg"), W, H, *p,
           title="Ціна постстабілізатора — перепад: тисни його передступенем")


if __name__ == "__main__":
    fig_two_stage()
    fig_psrr()
    fig_headroom()
    print("OK: figures written to", OUT)
