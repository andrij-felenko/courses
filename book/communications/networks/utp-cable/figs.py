# -*- coding: utf-8 -*-
"""Фігури до теми «UTP-кабель».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Крок звивання: знак площі чергується, наводки гасяться ────────────────
def fig_twist_cancel():
    W, H = 920, 470
    f = [text(W / 2, 28, "Крок звивання: кожен півкрок перевертає петлю — наводки гасяться",
              size=16, bold=True)]
    f.append(text(W / 2, 50, "зовнішнє поле пронизує сусідні «вічка» з різних боків → наведені ЕРС віднімаються",
                  size=11.5, color=MUTED, italic=True))

    x1, x2 = 130, 820

    # --- верх: нескручена пара = одна велика петля ---
    f.append(text(70, 92, "Нескручена пара: одна велика петля", size=13, bold=True, color=POS, anchor="start"))
    # пунктир зовнішнього поля
    sx = x1
    while sx <= x2:
        f.append(line(sx, 104, sx, 166, color="#e4e4e4", sw=1.2))
        sx += 46
    f.append(text(x2 + 20, 110, "B (зовн.)", size=11, color=MUTED, anchor="start", bold=True))
    f.append(line(x1, 120, x2, 120, color=NEG, sw=3.0))
    f.append(line(x1, 150, x2, 150, color=POS, sw=3.0))
    f.append(line(x1, 120, x1, 150, color=INK, sw=2.0))
    f.append(line(x2, 120, x2, 150, color=INK, sw=2.0))
    cmid = (x1 + x2) / 2
    f.append(line(cmid - 40, 120, cmid + 40, 120, color=POS, sw=2.2, dash=None))
    f.append('<line x1="%.1f" y1="120" x2="%.1f" y2="120" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % (cmid - 40, cmid + 40, POS))
    f.append('<line x1="%.1f" y1="150" x2="%.1f" y2="150" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % (cmid + 40, cmid - 40, POS))
    f.append(text(cmid, 186, "вся площа петлі ловить заваду → велика наведена ЕРС",
                  size=12, color=POS, bold=True))

    # --- низ: скручена пара = ланцюг дрібних петель ---
    f.append(text(70, 256, "Скручена пара: ланцюг дрібних петель, знак площі чергується",
                  size=13, bold=True, color=FIELD, anchor="start"))
    sx = x1
    while sx <= x2:
        f.append(line(sx, 270, sx, 348, color="#e4e4e4", sw=1.2))
        sx += 46
    f.append(text(x2 + 20, 276, "те саме B", size=11, color=MUTED, anchor="start", bold=True))

    # дві синусоїди в протифазі (переплетення)
    y0, amp = 310, 18
    steps = 240
    pa, pb = [], []
    for k in range(steps + 1):
        xx = x1 + (x2 - x1) * k / steps
        ph = (xx - x1) * 0.10
        pa.append("%s%.1f,%.1f" % ("M" if k == 0 else "L", xx, y0 + amp * math.sin(ph)))
        pb.append("%s%.1f,%.1f" % ("M" if k == 0 else "L", xx, y0 - amp * math.sin(ph)))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pa), NEG))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pb), POS))

    # знаки +/− над вічками, чергуються
    period = 2 * math.pi / 0.10
    nx = x1 + period / 4
    sign = 1
    while nx < x2:
        if sign > 0:
            f.append(text(nx, 262, "+", size=16, color=POS, bold=True))
        else:
            f.append(text(nx, 262, "−", size=16, color=NEG, bold=True))
        nx += period / 2
        sign = -sign

    # позначка кроку звивання
    f.append(line(x1 + period, 358, x1 + 2 * period, 358, color=INK, sw=1.8))
    f.append(line(x1 + period, 353, x1 + period, 363, color=INK, sw=1.8))
    f.append(line(x1 + 2 * period, 353, x1 + 2 * period, 363, color=INK, sw=1.8))
    f.append(text(x1 + 1.5 * period, 378, "крок звивання (twist pitch)", size=11.5, color=INK, bold=True))
    f.append(text(cmid + 120, 378, "сусідні петлі гасять одна одну", size=11.5, color=FIELD, bold=True, anchor="start"))

    f.append(text(W / 2, 452, "що менший крок (щільніше звивання) — то дрібніші петлі й точніша компенсація → вища категорія",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "twist-cancel.svg"), W, H, *f)


# ── 2. Система позначень екрана xx/yyTP ─────────────────────────────────────
def fig_shield_naming():
    W, H = 1000, 560
    f = [text(W / 2, 30, "Як читати назву екрана: xx/yyTP", size=17, bold=True)]
    f.append(text(W / 2, 52, "xx — екран усього кабелю · yy — екран кожної пари · TP = вита пара (twisted pair)",
                  size=12, color=MUTED, italic=True))

    f.append(text(150, 86, "U = немає (unscreened)", size=12.5, anchor="start"))
    f.append(text(430, 86, "F = фольга (foil)", size=12.5, anchor="start"))
    f.append(text(660, 86, "S = оплітка (braid)", size=12.5, anchor="start"))

    PAIR_COLS = ["#e08030", "#2f9e44", "#1f47b5", "#8a5a2b"]  # помаранч/зел/син/бур

    def cable(cx, cy, name, sub, overall=False, perpair=False):
        if overall:
            f.append(circle(cx, cy, 77, fill="none", stroke="#8a8a8a", sw=6))
        f.append(circle(cx, cy, 70, fill="#fafafa", stroke=INK, sw=2.4))
        # 4 пари по колу
        centers = [(cx + 30, cy + 20), (cx - 30, cy + 20), (cx - 30, cy - 20), (cx + 30, cy - 20)]
        for (px, py), col in zip(centers, PAIR_COLS):
            if perpair:
                f.append(circle(px, py, 21, fill="none", stroke="#8a8a8a", sw=4))
            ang = 0.6
            f.append(circle(px + 7 * math.cos(ang), py + 7 * math.sin(ang), 9.5, fill=col, stroke=INK, sw=1.4))
            f.append(circle(px - 7 * math.cos(ang), py - 7 * math.sin(ang), 9.5, fill="#ffffff", stroke=INK, sw=1.4))
        f.append(text(cx, cy + 104, name, size=15.5, bold=True))
        f.append(text(cx, cy + 124, sub, size=11.5, color=MUTED))

    cable(175, 250, "U/UTP", "без екранів — звичайний «UTP»")
    cable(430, 250, "F/UTP", "загальна фольга, пари без екрана", overall=True)
    cable(685, 250, "U/FTP", "кожна пара у фользі, спільного нема", perpair=True)
    cable(900, 250, "S/FTP", "оплітка + фольга на кожній парі", overall=True, perpair=True)

    f.append(fitbox(110, 430, 360, 96, [
        "Загальний екран (xx)",
        "ловить зовнішнє поле для всього джгута —",
        "клітка Фарадея навколо сигналів;",
        "заземлюють здебільшого з одного кінця."],
        size=12, fill="#f4faf4", stroke=FIELD))
    f.append(fitbox(530, 430, 360, 96, [
        "Екран пари (yy)",
        "прибирає взаємні наводки між парами",
        "(перехресні завади, crosstalk) і лишок,",
        "який не догасило саме звивання."],
        size=12, fill="#f4f6fc", stroke=NEG))
    f.append(text(W / 2, 548, "більше екранів — вища завадостійкість і ціна, товщий і твердіший кабель, складніше заземлення",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "shield-naming.svg"), W, H, *f)


if __name__ == "__main__":
    fig_twist_cancel()
    fig_shield_naming()
    print("OK: figures written to", IMG)
