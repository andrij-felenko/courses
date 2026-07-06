# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: пастка двох законів Лехмана й вихід ───────────────────────────
def fig_dilemma():
    W, H = 760, 430
    parts = []

    # Центральна система
    sysb, sw_, sh_ = textbox(W/2, 220, "Жива\nсистема", size=17, bold=True,
                             fill="#eef2ff", stroke=INK, sw=2, min_w=150)
    parts.append(sysb)

    # Закон 1 — мусить мінятися (тисне зверху вниз, стрілка до системи)
    law1, w1, h1 = textbox(180, 90, "Закон 1: мусить мінятися\n(інакше відстане й помре)",
                           size=13, fill="#fdecea", stroke=POS, sw=1.8)
    parts.append(law1)
    parts.append(arrow(180, 90 + h1/2, W/2 - 70, 200, color=POS, sw=2))

    # Закон 2 — структура псується (тисне знизу)
    law2, w2, h2 = textbox(180, 350, "Закон 2: кожна зміна псує\nструктуру (безлад росте сам)",
                           size=13, fill="#fdecea", stroke=POS, sw=1.8)
    parts.append(law2)
    parts.append(arrow(180, 350 - h2/2, W/2 - 70, 245, color=POS, sw=2))

    # Вихід праворуч — керована зміна
    out, wo, ho = textbox(600, 220, "Вихід: мінятися,\nАЛЕ керовано —\nтримати структуру\nпридатною до зміни",
                          size=13, fill="#eafaf1", stroke=FIELD, sw=2)
    parts.append(out)
    parts.append(arrow(W/2 + 78, 220, 600 - wo/2, 220, color=FIELD, sw=2.2))

    render(os.path.join(IMG, "dilemma.svg"), W, H, *parts,
           title="Два закони затискають систему — вихід один")


# ── Фігура 2: двоє воріт керованої зміни ────────────────────────────────────
def fig_gates():
    W, H = 820, 340
    parts = []
    ymid = 200

    # Вхід: зміна
    chg, wc, hc = textbox(90, ymid, "Зміна", size=16, bold=True,
                          fill="#f4f6f8", stroke=INK, sw=2, min_w=110)
    parts.append(chg)

    # Ворота 1: зворотність
    g1x = 320
    parts.append(rect(g1x - 85, ymid - 70, 170, 140, fill="#eaf0fd", stroke=NEG, sw=2))
    parts.append(mtext(g1x, ymid - 22, ["Ворота 1", "Зворотність"], size=14, bold=True, color=NEG))
    parts.append(mtext(g1x, ymid + 24, ["помилку легко", "відкотити"], size=12, color=INK))
    parts.append(arrow(90 + wc/2, ymid, g1x - 88, ymid, color=INK, sw=2))

    # Ворота 2: фітнес-функція
    g2x = 560
    parts.append(rect(g2x - 90, ymid - 70, 180, 140, fill="#eaf0fd", stroke=NEG, sw=2))
    parts.append(mtext(g2x, ymid - 22, ["Ворота 2", "Фітнес-функція"], size=14, bold=True, color=NEG))
    parts.append(mtext(g2x, ymid + 24, ["порушення важливого", "не проходить"], size=12, color=INK))
    parts.append(arrow(g1x + 88, ymid, g2x - 93, ymid, color=INK, sw=2))

    # Вихід: здорова система
    okx = 760
    okb, wok, hok = textbox(okx, ymid, "Структура\nтримає форму", size=13, bold=True,
                            fill="#eafaf1", stroke=FIELD, sw=2)
    parts.append(okb)
    parts.append(arrow(g2x + 93, ymid, okx - wok/2, ymid, color=FIELD, sw=2))

    render(os.path.join(IMG, "gates.svg"), W, H, *parts,
           title="Керована зміна проходить крізь двоє воріт")


# ── Фігура 3: ерозія проти напрямної еволюції в часі ────────────────────────
def fig_trajectories():
    W, H = 760, 420
    parts = []
    # осі
    ox, oy = 90, 340        # початок координат
    ax_w, ax_h = 600, 250
    parts.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))          # час →
    parts.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))          # придатність до зміни ↑
    parts.append(text(ox + ax_w, oy + 26, "час, потік змін", size=13, color=MUTED, anchor="end"))
    parts.append(mtext(ox - 14, oy - ax_h + 6, ["легкість", "зміни"], size=13,
                       color=MUTED, anchor="end"))

    x0, y0 = ox + 10, oy - ax_h + 40   # спільний старт угорі
    parts.append(circle(x0, y0, 5, fill=INK, stroke=INK))
    parts.append(text(x0 + 6, y0 - 12, "спільний старт", size=12, color=MUTED, anchor="start"))

    xe = ox + ax_w - 20

    # Ерозія: спадна крива (структура гниє, зміна дорожчає)
    ey = oy - 30
    parts.append('<path d="M%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" '
                 'stroke-width="2.6"/>' % (x0, y0, (x0+xe)/2, y0 + 150, xe, ey, POS))
    parts.append(text(xe - 6, ey + 22, "ерозія: гниє некеровано", size=13, color=POS, anchor="end"))

    # Напрямна еволюція: тримається майже рівно
    gy = oy - ax_h + 60
    parts.append('<path d="M%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" '
                 'stroke-width="2.6"/>' % (x0, y0, (x0+xe)/2, y0 - 26, xe, gy, FIELD))
    parts.append(text(xe - 6, gy - 12, "напрямна еволюція: тримає форму",
                      size=13, color=FIELD, anchor="end"))

    render(os.path.join(IMG, "trajectories.svg"), W, H, *parts,
           title="Одна система з роками: гнити чи еволюціонувати")


if __name__ == "__main__":
    fig_dilemma()
    fig_gates()
    fig_trajectories()
    print("figs written to", IMG)
