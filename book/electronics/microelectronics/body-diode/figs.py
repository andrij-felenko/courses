# -*- coding: utf-8 -*-
"""Фігури теми «Body-діод». Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def diode_glyph(cx, cy, up=True, color=INK, sw=2.2, size=12):
    """Символ діода (трикутник + риска-катод). up=True → катод угорі (струм знизу вгору)."""
    out = []
    if up:   # анод знизу, катод угорі
        out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#fbecec" stroke="%s" stroke-width="1.6"/>'
                   % (cx - size, cy + size, cx + size, cy + size, cx, cy - size, color))
        out.append(line(cx - size, cy - size, cx + size, cy - size, color=color, sw=sw + 0.4))
    else:    # анод угорі, катод знизу
        out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#fbecec" stroke="%s" stroke-width="1.6"/>'
                   % (cx - size, cy - size, cx + size, cy - size, cx, cy + size, color))
        out.append(line(cx - size, cy + size, cx + size, cy + size, color=color, sw=sw + 0.4))
    return "".join(out)


# ── Фігура 1: звідки береться діод — від кристала до символу ──────────────────
# Зліва — зріз N-MOSFET: p-тіло коротко з'єднане з n⁺-витоком; перехід тіло(p)↔
# стік(n) лишається живим діодом. Праворуч — той самий діод на умовному символі.
def fig_origin():
    W, H = 720, 360
    P = []

    # — ліва панель: спрощений зріз кристала —
    lx, ly, lw, lh = 40, 70, 300, 210
    P.append(rect(lx, ly, lw, lh, fill=BG, stroke="#c9d3dc", sw=1.4))
    P.append(text(lx + lw / 2, ly - 12, "звідки він у кристалі", size=12, bold=True))

    # підкладка n (тіло-носій) — нижній шар
    P.append(rect(lx + 20, ly + 120, lw - 40, 60, fill="#eaf0fd", stroke="#b9c6e6", sw=1.2))
    P.append(text(lx + lw / 2, ly + 168, "n-дрейф / стік (n)", size=11, color=NEG))

    # p-тіло — «корито» зверху
    P.append(rect(lx + 40, ly + 60, lw - 80, 70, fill="#fdecea", stroke="#e2a59f", sw=1.2))
    P.append(text(lx + lw / 2, ly + 100, "p-тіло (body)", size=11, color=POS))

    # n⁺ витоки в тілі
    P.append(rect(lx + 55, ly + 60, 50, 26, fill="#dfe7f6", stroke="#9fb3df", sw=1.1))
    P.append(rect(lx + lw - 105, ly + 60, 50, 26, fill="#dfe7f6", stroke="#9fb3df", sw=1.1))
    P.append(text(lx + 80, ly + 78, "n⁺", size=10, color=NEG, bold=True))
    P.append(text(lx + lw - 80, ly + 78, "n⁺", size=10, color=NEG, bold=True))

    # затвор-планка зверху
    P.append(rect(lx + 105, ly + 44, lw - 210, 12, fill="#f0f1f2", stroke="#b8bcc0", sw=1.1))
    P.append(text(lx + lw / 2, ly + 38, "затвор", size=9, color=MUTED))

    # коротке з'єднання тіло↔витік (металізація)
    P.append(line(lx + 80, ly + 60, lx + 80, ly + 30, color=INK, sw=1.8))
    P.append(line(lx + 80, ly + 30, lx + 55, ly + 30, color=INK, sw=1.8))
    P.append(line(lx + 55, ly + 30, lx + 55, ly + 95, color=INK, sw=1.8))   # металл тягнеться в p-тіло
    P.append(text(lx + 30, ly + 26, "витік+тіло", size=8.5, color=INK, anchor="start"))

    # стрілка на «живий» перехід p↔n (тіло-стік)
    P.append(arrow(lx + lw - 40, ly + 150, lx + lw - 70, ly + 122, color=POS, sw=1.8))
    P.append(text(lx + lw - 18, ly + 158, "p↔n", size=10, color=POS, anchor="start", bold=True))
    P.append(text(lx + lw - 18, ly + 172, "= діод", size=10, color=POS, anchor="start", bold=True))

    # — стрілка переходу між панелями —
    P.append(arrow(lx + lw + 8, ly + lh / 2, lx + lw + 48, ly + lh / 2, color=MUTED, sw=2))

    # — права панель: символ N-MOSFET з body-діодом —
    rxp, ryp = 470, 70
    rw, rh = 210, 210
    P.append(rect(rxp, ryp, rw, rh, fill=BG, stroke="#c9d3dc", sw=1.4))
    P.append(text(rxp + rw / 2, ryp - 12, "як його малюють", size=12, bold=True))

    midx = rxp + 70           # вертикаль каналу
    dtop, dbot = ryp + 40, ryp + 170
    # канал-риска
    P.append(line(midx, dtop, midx, dbot, color=INK, sw=2.4))
    # стік угорі, витік унизу — виводи
    P.append(line(midx, dtop, midx + 70, dtop, color=INK, sw=1.8))
    P.append(line(midx, dbot, midx + 70, dbot, color=INK, sw=1.8))
    P.append(text(midx + 78, dtop + 4, "стік (D)", size=10, anchor="start"))
    P.append(text(midx + 78, dbot + 4, "витік (S)", size=10, anchor="start"))
    # затвор зліва
    P.append(line(midx - 10, dtop + 28, midx - 10, dbot - 28, color=INK, sw=2.2))
    P.append(line(midx - 10, (dtop + dbot) / 2, midx - 45, (dtop + dbot) / 2, color=INK, sw=1.8))
    P.append(text(midx - 50, (dtop + dbot) / 2 + 4, "G", size=10, anchor="end"))

    # body-діод паралельно каналу (анод=витік знизу, катод=стік угорі)
    dx = midx + 40
    P.append(line(dx, dtop, dx, dbot, color=POS, sw=1.6))
    P.append(line(dx, dtop, midx + 70, dtop, color=POS, sw=1.4))     # верх до стоку
    P.append(line(dx, dbot, midx + 70, dbot, color=POS, sw=1.4))     # низ до витоку
    P.append(diode_glyph(dx, (dtop + dbot) / 2, up=True, color=POS))  # катод угорі (до стоку)
    P.append(text(dx + 14, (dtop + dbot) / 2 - 6, "body-", size=10, color=POS, anchor="start", bold=True))
    P.append(text(dx + 14, (dtop + dbot) / 2 + 8, "діод", size=10, color=POS, anchor="start", bold=True))

    cap = "У N-MOSFET тіло (p) коротко з'єднане з витоком; перехід тіло↔стік лишається діодом."
    P.append(text(W / 2, H - 22, cap, size=11))
    cap2 = "На символі його малюють паралельно каналу: катод — на стоку, анод — на витоку."
    P.append(text(W / 2, H - 6, cap2, size=11, italic=True))

    render(os.path.join(IMG, "body-diode.svg"), W, H, *P)


# ── Фігура 2: три ролі діода в схемі ─────────────────────────────────────────
# (а) гасний прохід індуктивного струму  (б) хибне зворотне живлення  (в) пара
# спина-до-спини глухо тримає зворотний струм.
def fig_roles():
    W, H = 720, 330
    P = []
    panels = [
        (30,  "рятує: гасний прохід", FIELD),
        (275, "шкодить: тече назад", POS),
        (520, "лік: пара навстріч", INK),
    ]
    pw = 200
    for px, ttl, col in panels:
        P.append(rect(px, 50, pw, 240, fill=BG, stroke="#c9d3dc", sw=1.4))
        P.append(text(px + pw / 2, 44, ttl, size=12, bold=True, color=col))

    # — панель а: котушка → діод сусіднього плеча гасить струм —
    ax = 30
    P.append(rect(ax + 70, 95, 60, 34, fill="#f0f1f2", stroke="#b8bcc0", sw=2))
    P.append(text(ax + 100, 117, "OFF", size=10.5, color=MUTED, bold=True))
    # котушка-символ
    P.append(text(ax + 100, 170, "L (котушка)", size=10))
    P.append(line(ax + 40, 200, ax + 160, 200, color=INK, sw=1.7))
    P.append(diode_glyph(ax + 100, 200, up=True, color=FIELD, size=11))
    P.append(arrow(ax + 45, 235, ax + 155, 235, color=FIELD, sw=2))
    P.append(text(ax + 100, 255, "струм L «докочується»", size=8.5, color=FIELD, bold=True))
    P.append(text(ax + 100, 270, "крізь діод — не пробиває ключ", size=8.5, color=FIELD))

    # — панель б: один ключ OFF, а діод тече назад —
    bx = 275
    P.append(rect(bx + 73, 120, 54, 40, fill="#f0f1f2", stroke="#b8bcc0", sw=2))
    P.append(text(bx + 100, 144, "OFF", size=10.5, color=MUTED, bold=True))
    P.append(line(bx + 30, 140, bx + 73, 140, color=INK, sw=1.8))
    P.append(line(bx + 127, 140, bx + 170, 140, color=INK, sw=1.8))
    P.append(text(bx + 24, 144, "вхід", size=9, anchor="end"))
    P.append(text(bx + 176, 144, "вихід↑", size=9, anchor="start", color=POS))
    # діод збоку
    P.append(line(bx + 60, 140, bx + 60, 196, color=INK, sw=1.6))
    P.append(line(bx + 140, 140, bx + 140, 196, color=INK, sw=1.6))
    P.append(line(bx + 60, 196, bx + 140, 196, color=INK, sw=1.6))
    P.append(diode_glyph(bx + 100, 196, up=False, color=POS, size=10))
    P.append(arrow(bx + 150, 230, bx + 50, 230, color=POS, sw=2))
    P.append(text(bx + 100, 250, "вищий вихід жене", size=8.5, color=POS, bold=True))
    P.append(text(bx + 100, 264, "струм назад крізь діод", size=8.5, color=POS))

    # — панель в: два діоди навстріч —
    cx = 520
    P.append(rect(cx + 40, 120, 44, 36, fill="#f0f1f2", stroke="#b8bcc0", sw=1.8))
    P.append(rect(cx + 116, 120, 44, 36, fill="#f0f1f2", stroke="#b8bcc0", sw=1.8))
    P.append(text(cx + 62, 142, "OFF", size=9, color=MUTED, bold=True))
    P.append(text(cx + 138, 142, "OFF", size=9, color=MUTED, bold=True))
    P.append(text(cx + 100, 112, "спільний витік", size=8.5))
    P.append(line(cx + 20, 138, cx + 40, 138, color=INK, sw=1.7))
    P.append(line(cx + 84, 138, cx + 116, 138, color=INK, sw=1.7))
    P.append(line(cx + 160, 138, cx + 180, 138, color=INK, sw=1.7))
    # діоди навстріч (катодами всередину)
    P.append(line(cx + 62, 138, cx + 62, 190, color=INK, sw=1.5))
    P.append(line(cx + 62, 190, cx + 100, 190, color=INK, sw=1.5))
    P.append(line(cx + 138, 138, cx + 138, 190, color=INK, sw=1.5))
    P.append(line(cx + 138, 190, cx + 100, 190, color=INK, sw=1.5))
    P.append(diode_glyph(cx + 62, 164, up=False, color=INK, size=9))
    P.append(diode_glyph(cx + 138, 164, up=True, color=INK, size=9))
    P.append(text(cx + 100, 232, "✗", size=18, color=FIELD, bold=True))
    P.append(text(cx + 100, 252, "діоди навстріч —", size=8.5, color=FIELD, bold=True))
    P.append(text(cx + 100, 266, "глухо в обидва боки", size=8.5, color=FIELD))

    P.append(text(W / 2, 24, "Той самий діод: коли рятує, коли шкодить і чим його приборкують",
                  size=14, bold=True))
    render(os.path.join(IMG, "roles.svg"), W, H, *P)


# ── Фігура 3: повільне відновлення (reverse recovery) ────────────────────────
# Струм діода: прямий → різко тягнуть униз → провалюється НИЖЧЕ нуля (Irr) →
# повертається. Площа провалу = заряд Qrr; ширина = trr. Це і є втрати/завада.
def fig_recovery():
    W, H = 700, 340
    P = []
    ox, oy = 90, 70          # початок осей
    axw, axh = 540, 200
    zero = oy + 90           # лінія нуля струму

    # осі
    P.append(line(ox, oy, ox, oy + axh, color=INK, sw=1.6))          # вісь струму
    P.append(line(ox, zero, ox + axw, zero, color=MUTED, sw=1.2, dash="4 4"))  # нуль
    P.append(line(ox, oy + axh, ox + axw, oy + axh, color=INK, sw=1.6))         # вісь часу
    P.append(text(ox - 10, oy + 4, "I", size=12, anchor="end", bold=True))
    P.append(text(ox + axw + 6, oy + axh + 4, "t", size=12, anchor="start", bold=True))
    P.append(text(ox - 14, zero + 4, "0", size=10, anchor="end", color=MUTED))

    # форма струму через діод
    x0 = ox + 30
    yfwd = zero - 55          # прямий струм (плато)
    xfall = ox + 250          # початок спаду
    xbot = ox + 320           # дно (Irr)
    ybot = zero + 60          # провал нижче нуля
    xrec = ox + 470           # повернення до нуля

    pts = [(x0, yfwd), (xfall, yfwd), (xbot, ybot)]
    # м'яке повернення вгору (експонента-подоба)
    for i in range(1, 9):
        t = i / 8.0
        x = xbot + (xrec - xbot) * t
        y = ybot + (zero - ybot) * (1 - (1 - t) ** 2)
        pts.append((x, y))
    pts.append((ox + axw - 10, zero))
    pl = " ".join("%.1f,%.1f" % p for p in pts)
    P.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pl, POS))

    # заливка площі провалу (Qrr) під нулем: від перетину нуля до повернення
    xcross = xfall + (xbot - xfall) * (zero - yfwd) / (ybot - yfwd)
    apoly = [(xcross, zero), (xbot, ybot)]
    for i in range(1, 9):
        t = i / 8.0
        x = xbot + (xrec - xbot) * t
        y = ybot + (zero - ybot) * (1 - (1 - t) ** 2)
        apoly.append((x, y))
    apoly.append((xrec, zero))
    apl = " ".join("%.1f,%.1f" % p for p in apoly)
    P.append('<polygon points="%s" fill="#fbecec" stroke="none" opacity="0.85"/>' % apl)

    # підписи плато / дна
    P.append(text((x0 + xfall) / 2, yfwd - 10, "прямий струм", size=10, color=POS))
    P.append(line(xbot, ybot, xbot, ybot + 18, color=NEG, sw=1.2))
    P.append(text(xbot, ybot + 32, "Irr", size=10, color=NEG, bold=True, anchor="middle"))
    P.append(text(xbot, ybot + 46, "(піковий зворотний)", size=8, color=NEG))

    # trr — ширина провалу
    P.append(line(xcross, oy + axh - 6, xrec, oy + axh - 6, color=NEG, sw=1.2))
    P.append(line(xcross, oy + axh - 12, xcross, oy + axh, color=NEG, sw=1))
    P.append(line(xrec, oy + axh - 12, xrec, oy + axh, color=NEG, sw=1))
    P.append(text((xcross + xrec) / 2, oy + axh + 16, "trr", size=10, color=NEG, bold=True))

    # Qrr — площа
    P.append(text((xbot + xrec) / 2 + 6, zero + 26, "Qrr", size=11, color=POS, bold=True))
    P.append(arrow((xbot + xrec) / 2 + 6, zero + 18, xbot + 24, zero + 36, color=POS, sw=1.4))

    # ремарка про спалах
    P.append(text(ox + axw - 4, zero - 12, "цей провал = втрати й завади",
                  size=9.5, color=MUTED, anchor="end", italic=True))

    P.append(text(W / 2, 30, "Повільне відновлення: діод не зачиняється миттєво",
                  size=14, bold=True))
    cap = "Коли діод тягнуть із прямого струму в запор, він на мить пускає струм назад (Irr) за час trr;"
    P.append(text(W / 2, H - 22, cap, size=11))
    cap2 = "накопичений під час провалу заряд Qrr — це зайві втрати й сплеск завад у швидкому мості."
    P.append(text(W / 2, H - 6, cap2, size=11, italic=True))

    render(os.path.join(IMG, "reverse-recovery.svg"), W, H, *P)


if __name__ == "__main__":
    fig_origin()
    fig_roles()
    fig_recovery()
    print("OK: body-diode.svg, roles.svg, reverse-recovery.svg")
