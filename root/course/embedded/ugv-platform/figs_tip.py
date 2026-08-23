# -*- coding: utf-8 -*-
# Фігури для вставки math-tipover-stability.md — стійкість ровера на перекид.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: два моменти довкола ребра перекиду — звідки tan α_кр = b/h ──────
def f_moments():
    W, H = 780, 470
    frags = []
    frags.append(text(W/2, 26, "Два моменти довкола ребра: що тримає, що перекидає", size=17, bold=True))

    # похилий ґрунт (вид з торця машини), кут α — тримаємо машину ВИЩЕ у кадрі
    ang = 22 * math.pi/180
    ax, ay = 70, 320
    Lg = 490
    bx, by = ax + Lg*math.cos(ang), ay - Lg*math.sin(ang)
    frags.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#eef1f4" stroke="%s" stroke-width="2"/>' % (ax, ay, bx, by, bx, ay, LINE))
    frags.append(text(ax+70, ay-9, "α", size=15, italic=True, bold=True))

    # осі машини: уздовж схилу (вгору) і нормаль (від поверхні)
    ux, uy = math.cos(ang), -math.sin(ang)
    nx, ny = math.sin(ang), math.cos(ang)
    base = (ax + 160*math.cos(ang), ay - 160*math.sin(ang))   # нижнє (зовнішнє) колесо — вісь перекиду

    def pt(along, up):
        return (base[0] + along*ux + up*nx, base[1] + along*uy + up*ny)

    track = 150       # колія в пікселях (між колесами)
    wlo = pt(0, 14)   # нижнє колесо = ребро перекиду
    whi = pt(track, 14)
    frags.append(circle(wlo[0], wlo[1], 13, fill="#e8ebef", stroke=INK, sw=2))
    frags.append(circle(whi[0], whi[1], 13, fill="#e8ebef", stroke=INK, sw=2))
    # корпус
    c1 = pt(-6, 28); c2 = pt(track+6, 28); c3 = pt(track+6, 86); c4 = pt(-6, 86)
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#f4f6f8" stroke="%s" stroke-width="2"/>' % (
        c1[0], c1[1], c2[0], c2[1], c3[0], c3[1], c4[0], c4[1], INK))

    # центр мас — на висоті h над серединою колії
    cm = pt(track/2, 14 + 52)     # h над лінією коліс
    frags.append(circle(cm[0], cm[1], 9, fill="#fff", stroke=INK, sw=2))
    frags.append(line(cm[0]-9, cm[1], cm[0]+9, cm[1], color=INK, sw=2))
    frags.append(line(cm[0], cm[1]-9, cm[0], cm[1]+9, color=INK, sw=2))

    # вісь перекиду — жирна крапка на нижньому колесі (підпис прямо ПІД колесом, повз усе)
    frags.append(circle(wlo[0], wlo[1], 5, fill=POS, stroke=POS))
    frags.append(line(wlo[0], wlo[1]+6, wlo[0], wlo[1]+34, color=POS, sw=1.0))
    frags.append(text(wlo[0], wlo[1]+48, "вісь перекиду", size=11, color=POS, anchor="middle"))

    # повна вага m·g — вертикально вниз від ЦМ (коротка, лишається в кадрі)
    gx, gy = cm[0], cm[1] + 96
    frags.append(arrow(cm[0], cm[1], gx, gy, color=INK, sw=2.6))
    frags.append(text(gx+12, gy-2, "m·g", size=13, italic=True, bold=True, anchor="start"))

    # позначки b (уздовж поверхні, пів-колії) і h (по нормалі) — праворуч, повз вагу
    mid = pt(track/2, 14)
    frags.append(line(wlo[0], wlo[1]+2, mid[0], mid[1]+2, color=MUTED, sw=1.3))
    frags.append(text((wlo[0]+mid[0])/2, (wlo[1]+mid[1])/2+18, "b (пів-колії)", size=12, italic=True, color=MUTED))
    frags.append(line(mid[0]+2, mid[1], cm[0]+2, cm[1], color=MUTED, sw=1.3, dash="4 3"))
    frags.append(text(cm[0]+16, (mid[1]+cm[1])/2, "h", size=13, italic=True, color=MUTED, anchor="start"))

    # підпис-висновок унизу (в межах кадру)
    body, bw, bh = textbox(W/2, 448,
        "тримає: m·g·b·cos α   ·   перекидає: m·g·h·sin α   →   межа: tan α_кр = b / h",
        size=13, bold=True, fill="#eafaf0", stroke=FIELD)
    frags.append(body)

    render(os.path.join(OUT, 'tip-moments.svg'), W, H, *frags)


# ── Фігура 2: бічний перекид у повороті — відцентрова проти ваги ──────────────
def f_corner():
    W, H = 780, 470
    frags = []
    frags.append(text(W/2, 26, "Перекид у повороті: відцентрова сила на плечі h", size=17, bold=True))

    # ЛІВА панель: вид згори — ровер на дузі радіуса R
    cxo, cyo = 150, 250     # центр дуги (умовний, за кадром ліворуч показуємо стрілку до нього)
    # намалюємо шматок дуги
    r_arc = 150
    # ровер у точці внизу дуги
    rvx, rvy = 250, 150
    # корпус згори
    frags.append(rect(rvx-26, rvy-40, 52, 80, fill="#f4f6f8", stroke=INK, sw=2))
    for wy in (rvy-30, rvy+30):
        for wx in (rvx-26, rvx+26):
            frags.append(rect(wx-6, wy-9, 12, 18, fill="#e8ebef", stroke=INK, sw=1.5))
    # дуга траєкторії
    frags.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6 4"/>' % (
        rvx-70, rvy+96, rvx+10, rvy-10, rvx+96, rvy-70, NEG))
    # стрілка до центра повороту (доцентрова) + підпис R
    frags.append(arrow(rvx, rvy, rvx-92, rvy+40, color=MUTED, sw=1.8))
    frags.append(text(rvx-70, rvy+30, "R", size=14, italic=True, bold=True, color=MUTED))
    frags.append(text(rvx-96, rvy+58, "до центра", size=10, color=MUTED, anchor="start"))
    # відцентрова назовні
    frags.append(arrow(rvx, rvy, rvx+96, rvy-42, color=POS, sw=2.6))
    frags.append(text(rvx+70, rvy-52, "m·v²/R", size=13, italic=True, bold=True, color=POS, anchor="start"))
    frags.append(text(rvx, rvy+118, "вид згори", size=11, color=INK))

    # ПРАВА панель: вид ззаду — важіль довкола зовнішнього колеса
    ox = 470
    gy = 300
    track = 190
    wl = ox + 40          # внутрішнє колесо
    wr = wl + track       # зовнішнє колесо = вісь перекиду
    frags.append(line(ox, gy, ox+track+90, gy, color=MUTED, sw=2))
    for wx in (wl, wr):
        frags.append(circle(wx, gy-14, 14, fill="#e8ebef", stroke=INK, sw=2))
    # корпус
    frags.append(rect(wl-6, gy-96, track+12, 60, fill="#f4f6f8", stroke=INK, sw=2))
    # центр мас на висоті h над серединою колії
    cmx = (wl+wr)/2
    cmy = gy - 66
    frags.append(circle(cmx, cmy, 9, fill="#fff", stroke=INK, sw=2))
    frags.append(line(cmx-9, cmy, cmx+9, cmy, color=INK, sw=2))
    frags.append(line(cmx, cmy-9, cmx, cmy+9, color=INK, sw=2))
    # вісь перекиду — зовнішнє колесо
    frags.append(circle(wr, gy-14, 5, fill=POS, stroke=POS))
    frags.append(text(wr+6, gy+22, "вісь перекиду", size=11, color=POS, anchor="middle"))
    # вага вниз (тримає — плече b)
    frags.append(arrow(cmx, cmy, cmx, gy-20, color=INK, sw=2.6))
    frags.append(text(cmx-10, gy-30, "m·g", size=13, italic=True, bold=True, color=INK, anchor="end"))
    # відцентрова назовні (перекидає — плече h), горизонтально до зовнішнього колеса
    frags.append(arrow(cmx, cmy, cmx+96, cmy, color=POS, sw=2.6))
    frags.append(text(cmx+50, cmy-8, "m·v²/R", size=13, italic=True, bold=True, color=POS, anchor="middle"))
    # плечі b і h
    frags.append(line(cmx, gy+16, wr, gy+16, color=FIELD, sw=2.2))
    frags.append(text((cmx+wr)/2, gy+32, "b", size=13, italic=True, color=FIELD, bold=True))
    frags.append(line(wr+2, cmy, wr+2, gy-14, color=MUTED, sw=1.3, dash="4 3"))
    frags.append(text(wr+12, (cmy+gy)/2, "h", size=13, italic=True, color=MUTED, anchor="start"))
    frags.append(text(cmx, gy+52, "вид ззаду", size=11, color=INK))

    # підпис-висновок унизу
    body, bw, bh = textbox(W/2, 448,
        "на межі: (m·v²/R)·h = (m·g)·b   →   гранична швидкість v_max = √(g·R·b/h)",
        size=13, bold=True, fill="#eafaf0", stroke=FIELD)
    frags.append(body)

    render(os.path.join(OUT, 'tip-corner.svg'), W, H, *frags)


# ── Фігура 3: перетік ваги при розгоні — інерційна сила на плечі h ───────────
def f_transfer():
    W, H = 760, 420
    frags = []
    frags.append(text(W/2, 26, "Перетік ваги на розгоні: інерція на плечі h", size=17, bold=True))

    gy = 300
    x0 = 90
    L = 420            # база в пікселях
    wf = x0            # переднє колесо
    wr = x0 + L        # заднє колесо
    frags.append(line(40, gy, W-40, gy, color=MUTED, sw=2))
    frags.append(text(W-44, gy+18, "ґрунт", size=11, color=MUTED, anchor="end"))
    for wx in (wf, wr):
        frags.append(circle(wx, gy-16, 16, fill="#e8ebef", stroke=INK, sw=2))
        frags.append(circle(wx, gy-16, 5, fill=INK, stroke=INK))
    # корпус
    frags.append(rect(wf-10, gy-96, L+20, 60, fill="#f4f6f8", stroke=INK, sw=2))
    # напрям руху / розгону
    frags.append(arrow(wr+30, gy-120, wr+90, gy-120, color=INK, sw=2.4))
    frags.append(text(wr+60, gy-128, "розгін a", size=12, bold=True, anchor="middle"))

    # центр мас на висоті h
    cmx = (wf+wr)/2
    cmy = gy - 66
    frags.append(circle(cmx, cmy, 9, fill="#fff", stroke=INK, sw=2))
    frags.append(line(cmx-9, cmy, cmx+9, cmy, color=INK, sw=2))
    frags.append(line(cmx, cmy-9, cmx, cmy+9, color=INK, sw=2))
    # інерційна сила m·a — назад (проти розгону), прикладена в ЦМ на висоті h
    frags.append(arrow(cmx, cmy, cmx-90, cmy, color=POS, sw=2.6))
    frags.append(text(cmx-50, cmy-8, "m·a", size=13, italic=True, bold=True, color=POS, anchor="middle"))
    # плече h
    frags.append(line(cmx+2, cmy, cmx+2, gy-16, color=MUTED, sw=1.3, dash="4 3"))
    frags.append(text(cmx+12, (cmy+gy)/2, "h", size=13, italic=True, color=MUTED, anchor="start"))
    # база L
    frags.append(line(wf, gy+22, wr, gy+22, color=MUTED, sw=1.3))
    frags.append(text((wf+wr)/2, gy+38, "база L", size=12, color=MUTED))

    # стрілки реакцій осей: передня меншає, задня більшає
    frags.append(arrow(wf, gy+58, wf, gy+18, color=NEG, sw=2.4))
    frags.append(text(wf, gy+74, "N_пер ↓", size=12, color=NEG, bold=True))
    frags.append(arrow(wr, gy+70, wr, gy+18, color=FIELD, sw=3.0))
    frags.append(text(wr, gy+86, "N_зад ↑", size=12, color=FIELD, bold=True))

    # підпис-висновок
    body, bw, bh = textbox(W/2, 398,
        "інерція m·a на плечі h перетікає вагу назад:   ΔN = m·a·h / L",
        size=13, bold=True, fill="#eafaf0", stroke=FIELD)
    frags.append(body)

    render(os.path.join(OUT, 'tip-transfer.svg'), W, H, *frags)


if __name__ == '__main__':
    f_moments()
    f_corner()
    f_transfer()
    print("ok: tip-moments.svg, tip-corner.svg, tip-transfer.svg")
