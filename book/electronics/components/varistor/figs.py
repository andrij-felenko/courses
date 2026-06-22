# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Варистор».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: де варистор і запобіжник сидять на вході мережі ────────────────
# Головна ідея монтажу: запобіжник РОЗРИВАЄ коло (стоїть послідовно у фазі),
# варистор ВІДВОДИТЬ сплеск (висить поперек L–N). Порядок критичний — запобіжник
# мусить стояти ПЕРЕД варистором за течією струму, інакше згорілий у коротке
# варистор лишиться прямим коротким на мережі без жодного захисту.
def fig_mains_entry():
    W, H = 820, 430
    L_y, N_y = 120, 320          # фазний і нульовий проводи
    parts = []

    # підписи проводів
    parts.append(text(58, L_y + 4, "L (фаза)", size=13, color=POS, anchor="start", bold=True))
    parts.append(text(58, N_y + 4, "N (нуль)", size=13, color=NEG, anchor="start", bold=True))
    parts.append(text(58, (L_y + N_y) / 2, "з\nмережі", size=11, color=MUTED, anchor="start", italic=True))

    # нульовий провід — суцільний знизу
    parts.append(line(70, N_y, 730, N_y, color=NEG, sw=2.6))

    # фазний провід: вхід → запобіжник → точка варистора → далі
    fuse_x = 200
    mov_x = 410
    parts.append(line(70, L_y, fuse_x - 28, L_y, color=POS, sw=2.6))
    # запобіжник (прямокутник із внутрішньою ниткою)
    parts.append(rect(fuse_x - 28, L_y - 13, 56, 26, fill=BG, stroke=INK, sw=2))
    parts.append(line(fuse_x - 22, L_y, fuse_x + 22, L_y, color=INK, sw=2.2))
    parts.append(text(fuse_x, L_y - 24, "ЗАПОБІЖНИК", size=12, bold=True))
    parts.append(text(fuse_x, L_y - 40, "(послідовно в L)", size=11, color=MUTED))
    parts.append(text(fuse_x, N_y - 22, "рве тривалий струм", size=11))
    parts.append(text(fuse_x, N_y - 7, "перевантаження → розрив", size=10, color=MUTED, italic=True))
    parts.append(line(fuse_x + 28, L_y, mov_x, L_y, color=POS, sw=2.6))

    # варистор: гілка вниз від фазного до нульового, символ VDR (резистор зі стрілкою)
    parts.append(line(mov_x, L_y, mov_x, L_y + 38, color=INK, sw=2.2))
    parts.append(rect(mov_x - 16, L_y + 38, 32, 56, fill=BG, stroke=INK, sw=2))
    parts.append(line(mov_x - 26, L_y + 46, mov_x + 22, L_y + 90, color=INK, sw=2))  # коса стрілка нелінійності
    parts.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
                 % (mov_x + 22, L_y + 90, mov_x + 14, L_y + 84, mov_x + 22, L_y + 80, INK))
    parts.append(line(mov_x, L_y + 94, mov_x, N_y, color=INK, sw=2.2))
    parts.append(text(mov_x + 26, L_y + 50, "ВАРИСТОР", size=12, anchor="start", bold=True))
    parts.append(text(mov_x + 26, L_y + 66, "(поперек L–N)", size=11, color=MUTED, anchor="start"))
    parts.append(text(mov_x + 26, L_y + 82, "затискає сплеск", size=11, anchor="start"))
    # стрілка «сплеск» крізь варистор (ліворуч від тіла, щоб не накладатися)
    parts.append(arrow(mov_x - 40, L_y + 40, mov_x - 40, N_y - 6, color=FIELD, sw=2))
    parts.append(text(mov_x - 46, L_y + 56, "сплеск", size=10, color=FIELD, anchor="end", italic=True))

    # далі — блок схеми (фільтр, випрямляч)
    parts.append(line(mov_x, L_y, 600, L_y, color=POS, sw=2.6))
    box = rect(600, L_y - 28, 130, N_y - L_y + 56, fill="#eef6ff", stroke=NEG, sw=1.8)
    parts.append(box)
    parts.append(text(665, (L_y + N_y) / 2 - 16, "далі:", size=12, color=NEG, bold=True))
    parts.append(text(665, (L_y + N_y) / 2 + 2, "фільтр завад,", size=11, color=NEG))
    parts.append(text(665, (L_y + N_y) / 2 + 18, "випрямляч,", size=11, color=NEG))
    parts.append(text(665, (L_y + N_y) / 2 + 34, "схема", size=11, color=NEG))
    parts.append(line(600, N_y, 730, N_y, color=NEG, sw=2.6))

    # підсумок-стрічка внизу (у задану ширину, щоб не вилазила за полотно)
    parts.append(fitbox(40, H - 44, W - 80, 36,
                        "Порядок критичний: запобіжник СТОЇТЬ ПЕРЕД варистором, "
                        "щоб згорілий у коротке варистор не лишився прямим коротким на мережі.",
                        size=12, pad=10, fill=FILL))

    render("img/mains-entry.svg", W, H, *parts,
           title="Вхід мережі: запобіжник у розрив, варистор поперек")


# ── Фігура 2: нелінійна ВАХ варистора ────────────────────────────────────────
# Серце принципу: до коліна струм мізерний (варистор «невидимий»), за коліном
# напруга майже не росте, а струм лавиною. Показуємо ще ключову пастку: точку
# V_clamp при сотнях ампер ВИЩЕ за коліно V_nom (через залишковий нахил).
def fig_mov_vi():
    W, H = 760, 440
    ox, oy = 110, 380            # початок осей
    top, right = 70, 690
    parts = []

    # осі
    parts.append(arrow(ox, oy, ox, top, color=INK, sw=1.8))
    parts.append(arrow(ox, oy, right, oy, color=INK, sw=1.8))
    parts.append(text(ox - 64, top + 10, "струм I", size=13, anchor="start", bold=True))
    parts.append(text(right + 2, oy + 5, "напруга на варисторі, V", size=12, anchor="start", bold=True))

    # крива I(V): полога до коліна, далі різко вгору (степеневий закон)
    knee_x = 470                  # екранне коліно (V_nom)
    pts = []
    n = 90
    for i in range(n + 1):
        x = ox + (right - 20 - ox) * i / n
        # нормована напруга 0..1.45 від коліна
        v = (x - ox) / (knee_x - ox)
        # I ∝ v^alpha (alpha велике); масштабуємо у висоту графіка
        cur = v ** 22
        y = oy - min(cur, 1.0) * (oy - top - 8)
        pts.append((x, y))
    d = "M " + " L ".join("%.1f,%.1f" % p for p in pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, POS))

    # робоча напруга (зелена штрихова) — лівіше коліна
    work_x = ox + (knee_x - ox) * 0.74
    parts.append(line(work_x, oy, work_x, oy - 44, color=FIELD, sw=2, dash="5,4"))
    parts.append(text(work_x, oy + 18, "робоча", size=11, color=FIELD, bold=True))
    parts.append(text(work_x, oy + 32, "напруга", size=11, color=FIELD))
    parts.append(text(work_x - 6, oy - 50, "мовчить", size=10, color=FIELD, anchor="end", italic=True))

    # V_nom (коліно, при 1 мА)
    knee_y = oy - 0.04 * (oy - top - 8)
    parts.append(circle(knee_x, knee_y, 4.5, fill="#c9881e", stroke=INK, sw=1.6))
    parts.append(line(knee_x, oy, knee_x, knee_y, color="#c9881e", sw=2, dash="5,4"))
    parts.append(text(knee_x, oy + 18, "V_nom", size=11, color="#c9881e", bold=True))
    parts.append(text(knee_x, oy + 32, "(при 1 мА)", size=11, color="#c9881e"))

    # V_clamp (при сотнях ампер) — далі вгору по кривій
    clamp_x = right - 20 - 4
    clamp_y = pts[-1][1]
    parts.append(circle(clamp_x, clamp_y, 4.5, fill=NEG, stroke=INK, sw=1.6))
    parts.append(line(clamp_x, oy, clamp_x, clamp_y, color=NEG, sw=2, dash="5,4"))
    parts.append(text(clamp_x - 8, clamp_y + 16, "V_зат", size=11, color=NEG, anchor="end", bold=True))
    parts.append(text(clamp_x - 8, clamp_y + 32, "при сотнях А", size=10, color=NEG, anchor="end"))

    # пояснення
    parts.append(text(ox + 14, top + 24, "до коліна струм мізерний — варистор «невидимий»",
                      size=11, color=MUTED, anchor="start", italic=True))
    parts.append(text(knee_x + 14, top + 70, "за коліном:", size=11, color=POS, anchor="start", italic=True))
    parts.append(text(knee_x + 14, top + 86, "напруга майже не росте,", size=11, color=POS, anchor="start", italic=True))
    parts.append(text(knee_x + 14, top + 102, "а струм — лавиною", size=11, color=POS, anchor="start", italic=True))

    render("img/mov-vi.svg", W, H, *parts,
           title="Нелінійна ВАХ варистора: «стіна» біля напруги спрацювання")


if __name__ == "__main__":
    fig_mains_entry()
    fig_mov_vi()
    print("OK: mains-entry, mov-vi")
