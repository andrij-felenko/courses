# -*- coding: utf-8 -*-
"""Фігури для теми «Спарені котушки: взаємоіндукція в перетворювачах».
Чистий Python + svgkit, без залежностей. Вивід у ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
P = lambda name: os.path.join(IMG, name)


def core(cx, cy, sw=2.4):
    """Намалювати замкнене осердя (двовіконна рамка) з центром (cx,cy)."""
    w, h = 92, 108
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill="#eef1f4", stroke=INK, sw=sw, rx=4)
    out += rect(x + 22, y + 16, w - 44, h - 32, fill=BG, stroke=INK, sw=sw, rx=3)
    return out


def winding(x, ytop, ybot, color, n=4):
    """Схематична обмотка: стовпчик півкіл уздовж вертикальної стійки x."""
    out = ""
    step = (ybot - ytop) / n
    for i in range(n):
        yc = ytop + step * (i + 0.5)
        out += ('<path d="M %.1f %.1f a %.1f %.1f 0 0 1 0 %.1f" fill="none" '
                'stroke="%s" stroke-width="2.4"/>' % (x, yc - step * 0.42, step * 0.42, step * 0.42, step * 0.84, color))
    out += line(x, ytop, x, ybot, color, 2.4)
    return out


# ── 1. Три ролі спареної котушки ────────────────────────────────────────────
def fig_roles():
    W, H = 760, 340
    els = [text(W / 2, 30, "Одна деталь — дві обмотки на спільному осерді — три ролі", size=17, bold=True)]
    cols = [130, 380, 630]
    titles = ["ЗАПАСАТИ енергію", "КЕРУВАТИ пульсацією", "ЖИВИТИ багато виходів"]
    subs = [
        ["осердя з зазором копить", "енергію в одній фазі,", "віддає в іншій (flyback)"],
        ["спільне поле «зганяє»", "пульсацію з однієї", "обмотки в іншу (SEPIC/Ćuk)"],
        ["один потік наводить", "кілька напруг —", "кілька витків, кілька шин"],
    ]
    for cx, t, sub in zip(cols, titles, subs):
        els.append(core(cx, 150))
        els.append(winding(cx - 24, 108, 192, POS))
        els.append(winding(cx + 24, 108, 192, NEG))
        # точки полярності
        els.append(circle(cx - 24, 100, 4.5, fill=POS, stroke=POS, sw=1))
        els.append(circle(cx + 24, 100, 4.5, fill=NEG, stroke=NEG, sw=1))
        els.append(text(cx, 232, t, size=13.5, bold=True, color=INK))
        els.append(mtext(cx, 252, sub, size=11.5, color=MUTED))
    els.append(line(255, 70, 255, 300, MUTED, 1, dash="4 5"))
    els.append(line(505, 70, 505, 300, MUTED, 1, dash="4 5"))
    render(P("roles.svg"), W, H, *els)


# ── 2. Дотова конвенція: підсилення проти гасіння ───────────────────────────
def fig_dots():
    W, H = 760, 320
    els = [text(W / 2, 30, "Той самий сердечник, різна намотка: поля складаються або віднімаються", size=16, bold=True)]

    def panel(cx, dot_bottom, label, val, valcol):
        e = [core(cx, 148)]
        e.append(winding(cx - 24, 106, 190, POS))
        e.append(winding(cx + 24, 106, 190, NEG))
        # точки: ліва завжди зверху; права — зверху (узгоджено) або знизу (зустрічно)
        e.append(circle(cx - 24, 98, 4.5, fill=POS, stroke=POS, sw=1))
        ry = 198 if dot_bottom else 98
        e.append(circle(cx + 24, ry, 4.5, fill=NEG, stroke=NEG, sw=1))
        e.append(text(cx, 226, label, size=13, bold=True))
        b, _, _ = textbox(cx, 258, val, size=13, bold=True, color=valcol,
                          fill="#f4f6f8", stroke=valcol)
        e.append(b)
        return e

    els += panel(210, False, "Узгоджено (точки з одного боку)",
                 "L_екв = L₁+L₂+2M  →  до ×4", POS)
    els += panel(550, True, "Зустрічно (точки з різних боків)",
                 "L_екв = L₁+L₂−2M  →  майже 0", NEG)
    els.append(line(380, 70, 380, 290, MUTED, 1, dash="4 5"))
    render(P("dots.svg"), W, H, *els)


# ── 3. Кероване гасіння пульсації (SEPIC/Ćuk) ───────────────────────────────
def fig_ripple():
    W, H = 720, 360
    els = [text(W / 2, 28, "Гасіння пульсації: однакова змінна напруга на обох обмотках", size=16, bold=True)]

    def tri(x0, y0, wdt, amp, n, col, sw=2.4):
        """Пилка (трикутна пульсація) завширшки wdt, розмахом amp, n зубів."""
        pts = []
        seg = wdt / (n * 2)
        up = True
        y = y0
        pts.append((x0, y0))
        for i in range(n * 2):
            x0 += seg
            y = y0 - amp if up else y0
            pts.append((x0, y))
            up = not up
        d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, col, sw)

    # ліворуч: некеровані обмотки — обидві пульсують
    els.append(text(190, 66, "Обмотки НЕ зв'язані", size=13, bold=True, color=MUTED))
    els.append(line(70, 120, 320, 120, MUTED, 1, dash="3 4"))
    els.append(tri(70, 120, 250, 34, 4, POS))
    els.append(text(60, 116, "вхід", size=11, color=POS, anchor="end"))
    els.append(line(70, 210, 320, 210, MUTED, 1, dash="3 4"))
    els.append(tri(70, 210, 250, 34, 4, NEG))
    els.append(text(60, 206, "вихід", size=11, color=NEG, anchor="end"))
    els.append(mtext(195, 262, ["дві окремі котушки —", "кожна пульсує сама по собі"], size=11.5, color=MUTED))

    # праворуч: зв'язані — вихідна майже рівна
    els.append(text(530, 66, "Обмотки ЗВ'ЯЗАНІ (k≈n)", size=13, bold=True, color=FIELD))
    els.append(line(410, 120, 660, 120, MUTED, 1, dash="3 4"))
    els.append(tri(410, 120, 250, 34, 4, POS))
    els.append(text(400, 116, "вхід", size=11, color=POS, anchor="end"))
    els.append(line(410, 210, 660, 210, MUTED, 1, dash="3 4"))
    els.append(line(410, 210, 660, 210, FIELD, 3.2))  # майже пряма — нуль пульсації
    els.append(text(400, 206, "вихід", size=11, color=FIELD, anchor="end"))
    els.append(mtext(535, 262, ["спільне поле «забирає» змінну", "складову — вихід майже рівний"], size=11.5, color=FIELD))

    els.append(line(365, 66, 365, 300, MUTED, 1, dash="4 5"))
    b, _, _ = textbox(W / 2, 328,
                      "Однакова змінна напруга на витках → на витоку зв'язаної обмотки ΔV=0 → її пульсація зникає",
                      size=11.5, color=INK, fill="#eef7f0", stroke=FIELD)
    els.append(b)
    render(P("ripple.svg"), W, H, *els)


# ── 4. Індуктивність витоку: незчеплена частка ──────────────────────────────
def fig_leakage():
    W, H = 720, 300
    els = [text(W / 2, 30, "Зв'язок не буває стовідсотковим: витік — це «нічия» частка поля", size=16, bold=True)]
    els.append(core(200, 150))
    els.append(winding(176, 108, 192, POS))
    els.append(winding(224, 108, 192, NEG))
    # головний потік у осерді
    els.append(text(200, 258, "спільний потік (зчеплено)", size=11.5, color=FIELD))
    els.append('<path d="M 176 100 C 120 60, 120 240, 176 200" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4 4"/>' % FIELD)
    # витік — дуга, що не доходить до другої обмотки
    els.append('<path d="M 176 118 C 150 130, 150 170, 176 182" fill="none" stroke="%s" stroke-width="2"/>' % POS)
    els.append(text(148, 152, "витік", size=11, color=POS, anchor="end"))

    # права модель: ідеальна спарена котушка + послідовна L_leak
    els.append(text(510, 70, "Модель реальної деталі", size=13, bold=True))
    b1 = fitbox(400, 96, 130, 46, "ідеальна\nспарена котушка", size=11.5, fill="#eef7f0", stroke=FIELD)
    els.append(b1)
    els.append(arrow(530, 119, 578, 119))
    b2 = fitbox(578, 96, 96, 46, "L_leak\n(послідовно)", size=11.5, fill="#fdecea", stroke=POS)
    els.append(b2)
    els.append(mtext(538, 178,
                     ["На вимиканні енергія витоку не має куди",
                      "перейти в парну обмотку — б'є викидом",
                      "напруги на ключі. Рятує снабер."], size=11.5, color=INK))
    render(P("leakage.svg"), W, H, *els)


# ── 5. Хронологія Ћука (для вставки hist-cuk) ───────────────────────────────
def fig_timeline():
    W, H = 820, 430
    els = [text(W / 2, 30, "Слободан Ћук: ідея → теза → патент → продукт (три різні події)",
                size=16, bold=True)]
    # вісь часу
    x0, x1, y = 70, 750, 150
    els.append(line(x0, y, x1, y, INK, 2.4))
    els.append(arrow(x1 - 2, y, x1 + 8, y, INK, 2.4))
    # роки-мітки на осі (рівномірно 1974..1991, стиснуто після 1980)
    years = [1974, 1975, 1976, 1977, 1979, 1980, 1991]
    # нелінійна розкладка: щільна ділянка 1974-80, тоді стрибок до 1991
    frac = {1974: 0.00, 1975: 0.14, 1976: 0.30, 1977: 0.44,
            1979: 0.60, 1980: 0.72, 1991: 1.00}
    xof = lambda yr: x0 + frac[yr] * (x1 - x0)
    for yr in years:
        xx = xof(yr)
        els.append(line(xx, y - 6, xx, y + 6, INK, 2))
        els.append(text(xx, y + 24, str(yr), size=12, bold=True, color=INK))
    # розрив шкали між 1980 і 1991
    xb = (xof(1980) + xof(1991)) / 2
    els.append(text(xb, y + 4, "⁓", size=18, color=MUTED))

    # події: (рік, зверху?, колір, рядки)
    ev = [
        (1974, True,  MUTED, ["стаття Мідлбрука", "про boost → вступ", "до Caltech"]),
        (1975, False, FIELD, ["топологія Ћука", "(1 квіт.) + спарена", "котушка / інт. магнетика"]),
        (1976, True,  INK,   ["теза (лист.):", "«Modelling… of", "Switching Converters»"]),
        (1977, False, POS,   ["ступінь Ph.D.;", "заявка на патент", "US 4 184 197 (Caltech)"]),
        (1979, True,  INK,   ["заснував фірму", "TESLAco", "(комерціалізація)"]),
        (1980, False, POS,   ["патент видано;", "відзнака IR-100", "(ĆUKonverter)"]),
        (1991, True,  FIELD, ["медаль Франкліна", "за інтегровану", "магнетику"]),
    ]
    for yr, up, col, lines in ev:
        xx = xof(yr)
        stem = 34 if up else 34
        yc = y - stem if up else y + stem + 12
        els.append(line(xx, y, xx, y - stem if up else y + stem, col, 1.6, dash="3 3"))
        els.append(circle(xx, y, 4, fill=col, stroke=col, sw=1))
        by = yc - 42 if up else yc
        els.append(mtext(xx, by, lines, size=10.5, color=col,
                         bold=(col in (FIELD, POS))))

    # підпис-легенда трьох фаз
    b, _, _ = textbox(W / 2, 400,
                      "зелене — ІДЕЯ (топологія, спарена котушка) · червоне — ПАТЕНТ і ПРОДУКТ · чорне — віхи кар'єри",
                      size=11, color=INK, fill=FILL, stroke=MUTED)
    els.append(b)
    render(P("cuk-timeline.svg"), W, H, *els)


if __name__ == "__main__":
    fig_roles()
    fig_dots()
    fig_ripple()
    fig_leakage()
    fig_timeline()
    print("figs written to", IMG)
