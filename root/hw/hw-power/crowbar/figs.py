# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#c9911f"   # стан «перенапруга, ще не спрацював»


def head(x, y, color, ang):
    """Маленька стрілка-наконечник (трикутник) у заданому кольорі; ang: 'down'/'up'."""
    if ang == "down":
        d = "M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" % (x - 5, y - 9, x + 5, y - 9, x, y)
    else:  # up
        d = "M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" % (x - 5, y + 9, x + 5, y + 9, x, y)
    return '<path d="%s" fill="%s"/>' % (d, color)


def fuse(cx, y, color=INK, blown=False, label="запобіжник"):
    """Запобіжник на горизонтальній шині з центром (cx,y). Повертає (svg, x_left, x_right)."""
    w = 30
    x0, x1 = cx - w / 2, cx + w / 2
    out = [rect(x0, y - 8, w, 16, fill=BG, stroke=color, sw=2.0, rx=3)]
    out.append(line(x0, y - 8, x1, y + 8, color=color, sw=1.6))   # коса риска елемента
    if blown:                                                       # «згоріло» — червоний хрест-розрив
        out.append(line(cx - 4, y - 10, cx + 4, y + 10, color=POS, sw=2.6))
        out.append(text(cx, y - 14, "горить", size=11, color=POS, bold=True))
    elif label:
        out.append(text(cx, y - 14, label, size=11, color=MUTED))
    return "".join(out), x0, x1


def scr(cx, cy, color=INK, scale=1.0):
    """Тиристор (SCR) вертикально: анод зверху, катод знизу, затвор збоку справа.
    Повертає (svg, top_y, bot_y, gate_x, gate_y)."""
    s = 16 * scale
    out = []
    # трикутник анод→катод (вістрям донизу)
    out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="2.2"/>'
               % (cx - s, cy - s, cx + s, cy - s, cx, cy + s * 0.55, BG, color))
    # катодна риска під вістрям
    out.append(line(cx - s, cy + s * 0.55, cx + s, cy + s * 0.55, color=color, sw=2.4))
    top_y = cy - s
    bot_y = cy + s * 0.55
    # затвор — коротка лінія від катодної риски праворуч-вниз
    gx, gy = cx + s + 8, cy + s * 0.55 + 8
    out.append(line(cx + s * 0.4, cy + s * 0.55, gx, gy, color=color, sw=2.0))
    return "".join(out), top_y, bot_y, gx, gy


def zener(cx, cy, color=NEG):
    """Стабілітрон вертикально (катод зверху, з «крильцями» Зенера). Повертає (svg, top_y, bot_y)."""
    s = 14
    out = []
    # трикутник вістрям донизу (анод знизу)
    out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="2.2"/>'
               % (cx - s, cy - s, cx + s, cy - s, cx, cy + s, BG, color))
    # катодна риска з відігнутими кінцями (символ Зенера)
    yk = cy - s
    out.append(line(cx - s, yk, cx + s, yk, color=color, sw=2.4))
    out.append(line(cx - s, yk, cx - s, yk - 6, color=color, sw=2.2))
    out.append(line(cx + s, yk, cx + s, yk + 6, color=color, sw=2.2))
    return "".join(out), yk - 6, cy + s


def resistor(cx, cy, color=INK):
    """Резистор вертикально (прямокутник). Повертає (svg, top_y, bot_y)."""
    w, h = 14, 40
    out = [rect(cx - w / 2, cy - h / 2, w, h, fill=BG, stroke=color, sw=2.0, rx=2)]
    return "".join(out), cy - h / 2, cy + h / 2


def dot(cx, cy, color=INK):
    return '<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s"/>' % (cx, cy, color)


def gnd(cx, y, color=INK):
    """Символ землі під точкою (cx,y)."""
    out = [line(cx, y, cx, y + 12, color=color, sw=2)]
    out.append(line(cx - 12, y + 12, cx + 12, y + 12, color=color, sw=2))
    out.append(line(cx - 8, y + 17, cx + 8, y + 17, color=color, sw=2))
    out.append(line(cx - 4, y + 22, cx + 4, y + 22, color=color, sw=2))
    return "".join(out)


# ── crowbar-principle: три стани — норма / перенапруга / спрацювання ───────────
# Ідея: одна й та сама схема в трьох станах показує суть crowbar — поки напруга
# в нормі, SCR закритий і плата живиться; перенапруга ще не спрацювала; коли
# поріг перевищено, SCR замикає шину на землю, струм просаджує напругу майже в
# нуль і палить запобіжник, відрізаючи вхід. Так читач бачить весь сюжет одразу.

def fig_principle():
    W, H = 760, 380
    p = []
    panels = [
        (40,  "Норма",       FIELD, "+5.0 В", "плата живиться",  "norm"),
        (290, "Перенапруга", GOLD,  "+9 В",   "ще ціла",         "over"),
        (540, "Спрацював",   POS,   "≈0 В",   "врятована",       "fire"),
    ]
    pw = 180
    for (px, name, col, vlabel, note, state) in panels:
        # рамка стану
        tint = {"norm": "#eef6ef", "over": "#fbf3e0", "fire": "#fbecec"}[state]
        p.append(rect(px, 64, pw, 296, fill=tint, stroke=col, sw=1.8, rx=8))
        p.append(text(px + pw / 2, 88, name, size=15, color=col, bold=True))

        raily = 150           # верхня (плюсова) шина
        gndy = 312            # нижня шина (земля)
        xin = px + 22         # вхід зліва
        xfuse = px + 64       # запобіжник
        xnode = px + 100      # вузол crowbar/плата
        xboard = px + 150     # плата

        livecol = INK
        if state == "fire":
            livecol = POS

        # вхід зі стрілкою (трикутник вправо)
        p.append(line(xin - 6, raily, xin + 16, raily, color=INK, sw=2))
        p.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
                 % (xin + 16, raily - 5, xin + 16, raily + 5, xin + 23, raily, INK))
        p.append(text(xin - 8, raily - 9, "вхід", size=11, color=INK, anchor="end"))

        # шина від входу до запобіжника
        p.append(line(xin + 23, raily, xfuse - 15, raily, color=INK, sw=2))
        fsvg, fx0, fx1 = fuse(xfuse, raily, color=(POS if state == "fire" else INK),
                              blown=(state == "fire"), label=("fuse" if state != "fire" else None))
        p.append(fsvg)
        # після запобіжника шина: у стані fire вона знеструмлена (сіра/розрив), до crowbar — жива
        after_col = MUTED if state == "fire" else INK
        p.append(line(fx1, raily, xnode, raily, color=(POS if state == "fire" else INK), sw=2))
        p.append(dot(xnode, raily))
        # шина до плати
        p.append(line(xnode, raily, xboard, raily, color=after_col, sw=2))

        # напруга на шині (підпис)
        p.append(text(xnode + 6, raily - 9, vlabel, size=13, color=col, bold=True,
                      anchor="start"))

        # SCR від вузла до землі
        scrcol = POS if state == "fire" else INK
        sc_svg, sty, sby, sgx, sgy = scr(xnode, (raily + gndy) / 2, color=scrcol)
        p.append(line(xnode, raily, xnode, sty, color=scrcol, sw=2))
        p.append(sc_svg)
        p.append(line(xnode, sby, xnode, gndy, color=scrcol, sw=2))
        p.append(text(xnode - 22, (raily + gndy) / 2, "SCR", size=12, color=scrcol,
                      anchor="end", bold=(state == "fire")))

        # струм у спрацюванні — товста червона стрілка вздовж SCR
        if state == "fire":
            ay0, ay1 = raily + 16, gndy - 20
            p.append(line(xnode + 20, ay0, xnode + 20, ay1, color=POS, sw=3))
            p.append(head(xnode + 20, ay1, POS, "down"))
            p.append(text(xnode + 26, (ay0 + ay1) / 2, "I велик.", size=11, color=POS,
                          anchor="start"))

        # плата (прямокутник) до землі
        bw, bh = 30, 44
        p.append(rect(xboard - bw / 2, (raily + gndy) / 2 - bh / 2, bw, bh,
                      fill=BG, stroke=INK, sw=2, rx=4))
        p.append(line(xboard, raily, xboard, (raily + gndy) / 2 - bh / 2, color=after_col, sw=2))
        p.append(line(xboard, (raily + gndy) / 2 + bh / 2, xboard, gndy, color=INK, sw=2))
        p.append(text(xboard, (raily + gndy) / 2 - 2, "плата", size=11, color=INK))
        p.append(text(xboard, (raily + gndy) / 2 + 12, note, size=10,
                      color=(col if state != "norm" else FIELD)))

        # нижня шина-земля
        p.append(line(xin + 8, gndy, xboard, gndy, color=INK, sw=2))
        p.append(dot(xnode, gndy))

    render(os.path.join(OUT, "crowbar-principle.svg"), W, H, *p,
           title="Crowbar: «коротке замикання за командою»")


# ── crowbar-sense-circuit: класична схема Zener + SCR ─────────────────────────
# Ідея: показати, ХТО дає тиристору команду. Стабілітрон стежить за шиною; поки
# напруга нижча за поріг (Vz + Vgt), на резисторі затвора майже нема спаду і SCR
# закритий. Коли напруга перевищує поріг, Zener пробивається, через Rg біжить
# струм, на затворі з'являється напруга запуску — і SCR защіпує шину на землю.

def fig_sense():
    W, H = 720, 400
    p = []
    raily = 96
    gndy = 320
    xin = 60
    xfuse = 130
    xscr = 230     # силова защіпка (crowbar SCR)
    xsense = 380   # гілка сенсора (Zener + Rg)
    xboard = 560

    # верхня шина
    p.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
             % (xin + 16, raily - 5, xin + 16, raily + 5, xin + 23, raily, INK))
    p.append(line(xin, raily, xin + 16, raily, color=INK, sw=2))
    p.append(text(xin - 4, raily - 10, "+Vживл.", size=13, color=POS, bold=True, anchor="end"))
    p.append(line(xin + 23, raily, xfuse - 15, raily, color=INK, sw=2))
    fsvg, fx0, fx1 = fuse(xfuse, raily, color=INK, label="запобіжник")
    p.append(fsvg)
    p.append(line(fx1, raily, xboard, raily, color=INK, sw=2))
    p.append(dot(xscr, raily))
    p.append(dot(xsense, raily))

    # нижня шина-земля
    p.append(line(xin + 8, gndy, xboard, gndy, color=INK, sw=2))
    p.append(gnd(xin + 8, gndy))
    p.append(dot(xscr, gndy))
    p.append(dot(xsense, gndy))

    # плата праворуч
    bw, bh = 34, 80
    by = (raily + gndy) / 2
    p.append(rect(xboard - bw / 2, by - bh / 2, bw, bh, fill=BG, stroke=INK, sw=2, rx=5))
    p.append(line(xboard, raily, xboard, by - bh / 2, color=INK, sw=2))
    p.append(line(xboard, by + bh / 2, xboard, gndy, color=INK, sw=2))
    p.append(text(xboard + 24, by - 6, "плата", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(xboard + 24, by + 12, "(чутливі ІС)", size=11, color=MUTED, anchor="start"))

    # силова защіпка: SCR від шини до землі
    sc_svg, sty, sby, sgx, sgy = scr(xscr, by - 6, color=POS)
    p.append(line(xscr, raily, xscr, sty, color=INK, sw=2))
    p.append(sc_svg)
    p.append(line(xscr, sby, xscr, gndy, color=INK, sw=2))
    p.append(text(xscr - 24, by - 18, "SCR", size=13, color=POS, bold=True, anchor="end"))
    p.append(text(xscr - 24, by - 2, "crowbar", size=11, color=POS, anchor="end"))

    # гілка сенсора: Zener зверху, вузол затвора, Rg донизу
    zsvg, zty, zby = zener(xsense, raily + 40, color=NEG)
    p.append(line(xsense, raily, xsense, zty, color=INK, sw=2))
    p.append(zsvg)
    gate_node_y = zby + 26
    p.append(line(xsense, zby, xsense, gate_node_y, color=INK, sw=2))
    p.append(dot(xsense, gate_node_y))
    p.append(text(xsense + 18, raily + 36, "Zener", size=12, color=NEG, anchor="start"))
    p.append(text(xsense + 18, raily + 52, "Vz", size=12, color=NEG, bold=True, anchor="start"))

    rsvg, rty, rby = resistor(xsense, gate_node_y + 42, color=INK)
    p.append(line(xsense, gate_node_y, xsense, rty, color=INK, sw=2))
    p.append(rsvg)
    p.append(line(xsense, rby, xsense, gndy, color=INK, sw=2))
    p.append(text(xsense + 14, gate_node_y + 46, "Rg", size=14, color=INK, anchor="start"))

    # затвор: від вузла сенсора до затвора SCR
    p.append(line(sgx, sgy, xsense, gate_node_y, color=FIELD, sw=2.2))
    p.append(text((sgx + xsense) / 2, gate_node_y - 8, "затвор", size=11, color=FIELD))

    # пояснювальна рамка внизу
    bx0, by0, bw2, bh2 = 56, 348, 608, 44
    p.append(rect(bx0, by0, bw2, bh2, fill="#fbfbf7", stroke=MUTED, sw=1.4, rx=8))
    p.append(text(bx0 + 14, by0 + 19, "V < Vz + Vgt:", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(bx0 + 130, by0 + 19, "Zener мовчить, спад на Rg ≈ 0, SCR закритий — плата живиться.",
                  size=12, color=INK, anchor="start"))
    p.append(text(bx0 + 14, by0 + 36, "V > поріг:", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(bx0 + 130, by0 + 36, "Zener пробитий → струм на Rg → затвор запускає SCR → шина на землю.",
                  size=12, color=POS, anchor="start"))

    render(os.path.join(OUT, "crowbar-sense-circuit.svg"), W, H, *p,
           title="Класичний crowbar: сенсор на стабілітроні")


if __name__ == "__main__":
    fig_principle()
    fig_sense()
    print("OK figs")
