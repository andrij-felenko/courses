# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 3.10 — «Як народжується чіп: від піску до корпуса» (Модуль 3).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «+» червоний, «−» синій; поле — зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції — спільні з рештою
розділів (копія), щоб вигляд був єдиний.

Імена файлів: fig-3-10-<тема>-<номер>-<слаг>.svg
Підписи у тексті — за темою: «Рис. 3.10.<тема>.<номер>».
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
PURP  = "#6a3d9a"
SAND  = "#d8c79a"
SKY   = "#cfe3f7"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def ellipse(cx, cy, rx, ry, fill="none", stroke=INK, w=2):
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def polygon(points, fill="none", stroke=INK, w=2):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _wrap(s, n):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= n:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def title(b, x, y, s, size=16):
    return b + text(x, y, s, size, INK, "middle", "bold")


# ════════════════════════════════════════════════════════════════════════════
# ТЕМА 3.10.1 — Кремній: від кварцового піску до монокристала
# ════════════════════════════════════════════════════════════════════════════

def fig_1_1_chain():
    """Ланцюг очищення: пісок → MGS → трихлорсилан → полікремній → монокристал."""
    W, H = 760, 320
    b = header(W, H)
    b = title(b, W/2, 28, "Від піску до монокристала: ланцюг очищення")
    stages = [
        ("Кварцовий\nпісок SiO₂", "~98%", SAND, "пляж, кар'єр"),
        ("Технічний\nкремній Si", "~99%", GREY, "піч + вуглець,\n1900 °C"),
        ("Трихлорсилан\nSiHCl₃", "рідина", SKY, "реакція з HCl,\nдистиляція"),
        ("Полікремній\n(злитки)", "9N+", "#bfbfbf", "процес Сіменса,\nосадження"),
        ("Монокристал\n(один злиток)", "9N", "#9fb8d8", "метод\nЧохральського"),
    ]
    n = len(stages)
    bw, gap = 116, 16
    x0 = (W - (n*bw + (n-1)*gap)) / 2
    cy = 150
    for i, (name, pur, col, how) in enumerate(stages):
        x = x0 + i*(bw+gap)
        b += rect(x, cy-46, bw, 92, col, INK, 2, 8)
        for j, ln in enumerate(name.split("\n")):
            b += text(x+bw/2, cy-22+j*18, ln, 14, INK, "middle", "bold")
        b += text(x+bw/2, cy+24, pur, 14, RED, "middle", "bold")
        for j, ln in enumerate(how.split("\n")):
            b += text(x+bw/2, cy+62+j*15, ln, 11.5, GREY, "middle")
        if i < n-1:
            ax = x+bw
            b += arrow(ax+1, cy, ax+gap-1, cy, INK, 2.4)
    b += text(W/2, H-12, "Чистота росте зліва направо: домішок усе менше — від кар'єрного піску до «дев'яти дев'яток».",
              12.5, GREY, "middle", style="italic")
    save("fig-3-10-1-1-chain.svg", b)


def fig_1_2_purity():
    """Драбина чистоти: 2N → 6N → 9N, скільки це домішкових атомів."""
    W, H = 720, 330
    b = header(W, H)
    b = title(b, W/2, 28, "Що означає «чистота 9N» (nine nines)")
    rows = [
        ("Технічний Si", "99 %", "2N", "1 чужий атом\nна 100", GREY),
        ("Сонячний Si", "99.9999 %", "6N", "1 на\n1 000 000", AMBER),
        ("Електронний Si", "99.9999999 %", "9N", "1 на\n1 000 000 000", GREEN),
    ]
    y0 = 70
    rh = 74
    for i, (name, pct, tag, note, col) in enumerate(rows):
        y = y0 + i*rh
        b += rect(60, y, 200, 54, "#f4f4f4", col, 2.5, 8)
        b += text(160, y+24, name, 15, INK, "middle", "bold")
        b += text(160, y+44, tag + " — " + pct, 13, col, "middle", "bold")
        # bar showing impurity (log scale, conceptual)
        bx, bw = 300, 300
        frac = [0.95, 0.45, 0.12][i]
        b += rect(bx, y+14, bw, 26, "#ffffff", FAINT, 1.5, 4)
        b += rect(bx, y+14, bw*frac, 26, col, "none", 0, 4)
        b += text(bx+bw+14, y+22, note.split("\n")[0], 12.5, INK, "start")
        b += text(bx+bw+14, y+38, note.split("\n")[1], 12.5, INK, "start")
    b += text(W/2, H-40, "Кожен крок очищення прибирає домішки на порядки. Електроніці потрібен крайній правий рівень:",
              12.5, GREY, "middle", style="italic")
    b += text(W/2, H-20, "один зайвий атом на мільярд кремнієвих — інакше транзистори поводяться непередбачувано.",
              12.5, GREY, "middle", style="italic")
    save("fig-3-10-1-2-purity.svg", b)


def fig_1_3_czochralski():
    """Метод Чохральського: тигель, розплав, затравка, витягування злитка."""
    W, H = 720, 430
    b = header(W, H)
    b = title(b, W/2, 28, "Метод Чохральського: вирощування монокристала")
    cx = 250
    # crucible
    cruc_y = 300
    b += path(f"M {cx-110},{cruc_y-90} L {cx-110},{cruc_y} "
              f"Q {cx-110},{cruc_y+34} {cx-76},{cruc_y+34} "
              f"L {cx+76},{cruc_y+34} Q {cx+110},{cruc_y+34} {cx+110},{cruc_y} "
              f"L {cx+110},{cruc_y-90}", fill="#efe7d2", stroke=INK, w=2.5)
    # melt
    b += path(f"M {cx-104},{cruc_y-30} L {cx-104},{cruc_y-4} "
              f"Q {cx-104},{cruc_y+26} {cx-74},{cruc_y+26} "
              f"L {cx+74},{cruc_y+26} Q {cx+104},{cruc_y+26} {cx+104},{cruc_y-4} "
              f"L {cx+104},{cruc_y-30} Z", fill="#f0a830", stroke="#c07a10", w=1.5)
    b += text(cx+150, cruc_y+6, "Розплав кремнію", 13, INK, "start")
    b += text(cx+150, cruc_y+24, "~1420 °C", 12.5, RED, "start")
    # heater coils
    for k in range(4):
        yy = cruc_y-70 + k*26
        b += line(cx-150, yy, cx-118, yy, RED, 5)
        b += line(cx+118, yy, cx+150, yy, RED, 5)
    b += text(cx-150, cruc_y+58, "нагрівач", 12, RED, "middle")
    b += text(cx+150, cruc_y-90, "нагрівач", 12, RED, "middle")
    # growing crystal (boule) being pulled up
    top_y = 70
    neck_y = 120
    b += line(cx, top_y-18, cx, top_y, GREY, 3)  # rod
    b += circle(cx, top_y-26, 8, "#dddddd", INK, 2)  # seed holder
    # seed neck
    b += rect(cx-7, top_y, 14, neck_y-top_y, "#cdd9ec", INK, 1.5, 3)
    b += text(cx+22, top_y+18, "затравка", 12, BLUE, "start")
    b += text(cx+22, top_y+34, "(seed)", 11.5, BLUE, "start")
    # cone + body of boule
    body_top = neck_y
    body_bot = cruc_y-30
    b += polygon([(cx-7, body_top), (cx+7, body_top),
                  (cx+46, body_top+40), (cx+46, body_bot),
                  (cx-46, body_bot), (cx-46, body_top+40)],
                 fill="#aebfd8", stroke=INK, w=2)
    b += text(cx+150, neck_y+70, "Монокристал", 13, INK, "start", "bold")
    b += text(cx+150, neck_y+88, "(boule, злиток)", 12, INK, "start")
    b += text(cx+150, neck_y+106, "діаметр 200–300 мм", 11.5, GREY, "start")
    # motion arrows
    b += arrow(cx-70, top_y+4, cx-70, top_y-34, BLUE, 2.2)
    b += text(cx-78, top_y-10, "тягнуть", 11.5, BLUE, "end")
    b += text(cx-78, top_y+6, "вгору", 11.5, BLUE, "end")
    b += path(f"M {cx+70},{top_y-30} a 16,16 0 1 1 -2,-10", fill="none", stroke=GREEN, w=2)
    b += arrow(cx+58, top_y-40, cx+72, top_y-36, GREEN, 2)
    b += text(cx+92, top_y-30, "обертають", 11.5, GREEN, "start")
    # bottom note
    b += text(W/2, H-16,
              "Затравку торкають до розплаву й повільно тягнуть угору, обертаючи: розплав застигає на ній, "
              "копіюючи її кристалічну ґратку.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-10-1-3-czochralski.svg", b)


def fig_1_4_wafer():
    """Злиток → нарізання на пластини → кругла полірована пластина."""
    W, H = 720, 300
    b = header(W, H)
    b = title(b, W/2, 28, "Від злитка до пластини (wafer)")
    # boule as cylinder on left
    bx = 130
    b += ellipse(bx, 90, 40, 14, "#aebfd8", INK, 2)
    b += rect(bx-40, 90, 80, 130, "#aebfd8", INK, 2)
    b += ellipse(bx, 220, 40, 14, "#9fb0c8", INK, 2)
    # slice lines
    for k in range(1, 6):
        yy = 110 + k*18
        b += line(bx-40, yy, bx+40, yy, INK, 1, dash="3,3")
    b += text(bx, 250, "Циліндр-злиток", 13, INK, "middle", "bold")
    b += text(bx, 268, "ріжуть дротяною пилкою", 11.5, GREY, "middle")
    # arrow
    b += arrow(bx+70, 150, bx+150, 150, INK, 2.4)
    b += text(bx+110, 138, "нарізка", 12, INK, "middle")
    # thin slice
    sx = 360
    b += ellipse(sx, 150, 18, 70, "#cdd9ec", INK, 2)
    b += text(sx, 240, "Тонкий зріз", 12.5, INK, "middle", "bold")
    b += text(sx, 258, "~0.7 мм", 11.5, GREY, "middle")
    # arrow
    b += arrow(sx+50, 150, sx+120, 150, INK, 2.4)
    b += text(sx+85, 138, "шліфування,", 11.5, INK, "middle")
    b += text(sx+85, 124, "полірування", 11.5, INK, "middle")
    # polished wafer (round, with flat)
    wx = 600
    b += circle(wx, 150, 80, "#e7eef8", INK, 2.5)
    b += circle(wx, 150, 80, "none", "#c8d6ee", 6)
    # notch / flat
    b += line(wx-28, 150+74, wx+28, 150+74, "#ffffff", 7)
    b += line(wx-28, 150+74, wx+28, 150+74, INK, 2)
    # reflective sheen
    b += path(f"M {wx-50},{150-40} Q {wx-10},{150-60} {wx+20},{150-30}",
              fill="none", stroke="#ffffff", w=4)
    b += text(wx, 150+108, "Полірована пластина", 12.5, INK, "middle", "bold")
    b += text(wx, 150+126, "дзеркальна, кругла, з лискою", 11.5, GREY, "middle")
    save("fig-3-10-1-4-wafer.svg", b)


# ════════════════════════════════════════════════════════════════════════════
# ТЕМА 3.10.2 — Фотолітографія: схему друкують світлом
# ════════════════════════════════════════════════════════════════════════════

def fig_2_1_litho():
    """Стек фотолітографії: світло → маска → лінза → фоторезист на пластині."""
    W, H = 720, 470
    b = header(W, H)
    b = title(b, W/2, 28, "Фотолітографія: малюнок переносять світлом")
    cx = 360
    # light source
    b += rect(cx-70, 56, 140, 30, "#fff2cc", AMBER, 2, 6)
    b += text(cx, 76, "Джерело світла (UV / EUV)", 12.5, INK, "middle", "bold")
    # rays down
    for dx in (-50, -25, 0, 25, 50):
        b += arrow(cx+dx, 88, cx+dx, 118, AMBER, 1.8)
    # mask (photomask) with opaque/clear pattern
    my = 122
    b += rect(cx-110, my, 220, 18, "#dddddd", INK, 2)
    # opaque chrome segments
    for seg in [(-110, 30), (-50, 24), (10, 18), (60, 26)]:
        b += rect(cx+seg[0], my, seg[1], 18, INK, "none", 0)
    b += text(cx+150, my+13, "Фотомаска", 12.5, INK, "start", "bold")
    b += text(cx+150, my+29, "(хром на кварці)", 11.5, GREY, "start")
    # only light through clear gaps continues
    gaps = [-80, -26, 28, 86]
    for gx in gaps:
        b += arrow(cx+gx, my+18, cx+gx, my+70, AMBER, 1.8)
    # lens (reduction optics)
    ly = 200
    b += ellipse(cx, ly, 96, 20, "#dbeafe", BLUE, 2)
    b += text(cx, ly+5, "Зменшувальна оптика  4×", 12, BLUE, "middle", "bold")
    # converging rays (4x reduction): gaps map closer together
    proj = [-30, -10, 11, 33]
    for gx, px in zip(gaps, proj):
        b += line(cx+gx, ly+18, cx+px, ly+70, AMBER, 1.6)
        b += arrow(cx+px, ly+60, cx+px, ly+76, AMBER, 1.6)
    # wafer stack: substrate + resist
    wy = 300
    b += rect(cx-150, wy+30, 300, 30, "#aebfd8", INK, 2)  # silicon
    b += text(cx-150-8, wy+50, "Si", 13, INK, "end", "bold")
    b += rect(cx-150, wy, 300, 30, "#f6d6a8", "#b8863a", 2)  # photoresist
    b += text(cx+150+10, wy+20, "Фоторезист", 12.5, "#9a6a18", "start", "bold")
    # exposed spots (where light hit)
    for px in proj:
        b += rect(cx+px-7, wy, 14, 30, "#caa24a", RED, 1.5)
    b += text(cx+px+150, wy+18, "засвічені ділянки", 11.5, RED, "start")
    # result note
    b += text(W/2, H-58,
              "Світло проходить лише крізь прозорі місця маски й засвічує фоторезист під ними.",
              12.5, GREY, "middle", style="italic")
    b += text(W/2, H-38,
              "Оптика зменшує малюнок у 4×: велика маска → крихітний візерунок на пластині.",
              12.5, GREY, "middle", style="italic")
    b += text(W/2, H-14,
              "Засвічений резист потім розчиняють (проявлення) — і на пластині лишається маска з резисту.",
              12, GREY, "middle", style="italic")
    save("fig-3-10-2-1-litho.svg", b)


def fig_2_2_resist():
    """Позитивний vs негативний фоторезист — що змивається."""
    W, H = 720, 320
    b = header(W, H)
    b = title(b, W/2, 26, "Позитивний і негативний фоторезист")
    for col_i, (name, note, removed_exposed) in enumerate([
        ("Позитивний", "змивається ЗАСВІЧЕНЕ", True),
        ("Негативний", "змивається НЕзасвічене", False),
    ]):
        ox = 60 + col_i*360
        b += text(ox+150, 58, name, 14, INK, "middle", "bold")
        b += text(ox+150, 76, "(" + note + ")", 12, GREY, "middle")
        # step a: exposure
        ya = 96
        b += rect(ox, ya+22, 300, 18, "#aebfd8", INK, 1.6)
        b += rect(ox, ya, 300, 22, "#f6d6a8", "#b8863a", 1.6)
        # light through two gaps
        for gx in (ox+90, ox+210):
            b += arrow(gx, ya-22, gx, ya, AMBER, 1.6)
            b += rect(gx-16, ya, 32, 22, "#caa24a", RED, 1.4)
        b += text(ox-8, ya+12, "1", 13, INK, "end", "bold")
        b += text(ox+320, ya+12, "засвічення", 11, GREY, "start")
        # step b: after develop
        yb = 200
        b += rect(ox, yb+22, 300, 18, "#aebfd8", INK, 1.6)
        # which resist remains
        if removed_exposed:
            remain = [(ox, 74), (ox+106, 88), (ox+226, 74)]
        else:
            remain = [(ox+74, 32), (ox+194, 32)]
        for rx, rw in remain:
            b += rect(rx, yb, rw, 22, "#f6d6a8", "#b8863a", 1.6)
        b += text(ox-8, yb+12, "2", 13, INK, "end", "bold")
        b += text(ox+320, yb+12, "після проявлення", 11, GREY, "start")
    b += text(W/2, H-14,
              "Той самий малюнок маски дає протилежний рельєф резисту — інженер обирає тип під свій крок травлення.",
              12, GREY, "middle", style="italic")
    save("fig-3-10-2-2-resist.svg", b)


def fig_2_3_wavelength():
    """Зменшення довжини хвилі: g-line → i-line → DUV → EUV."""
    W, H = 720, 320
    b = header(W, H)
    b = title(b, W/2, 28, "Чим коротша хвиля, тим дрібніший друк")
    src = [
        ("g-line", "436 нм", 436, AMBER),
        ("i-line", "365 нм", 365, AMBER),
        ("KrF (DUV)", "248 нм", 248, PURP),
        ("ArF (DUV)", "193 нм", 193, PURP),
        ("EUV", "13.5 нм", 13.5, BLUE),
    ]
    n = len(src)
    x0, gap = 70, 150
    base = 230
    # baseline
    b += line(40, base, W-30, base, INK, 1.5)
    maxwl = 436
    for i, (name, lab, wl, col) in enumerate(src):
        x = x0 + i*gap
        # wave amplitude proportional to wavelength (drawn period)
        per = max(8, wl/12)
        amp = 26
        npts = 60
        pts = []
        for k in range(npts+1):
            xx = x - 55 + k*(110/npts)
            yy = base - 40 - amp*math.sin(2*math.pi*(xx-(x-55))/per)
            pts.append((xx, yy))
        b += polyline(pts, col, 2.2)
        b += text(x, base+22, name, 12.5, INK, "middle", "bold")
        b += text(x, base+40, lab, 12, col, "middle", "bold")
        if i < n-1:
            b += arrow(x+58, base-66, x+gap-58, base-66, GREY, 1.6)
    b += text(W/2, base-92, "довжина хвилі ↓   →   роздільна здатність ↑", 12.5, GREEN, "middle", "bold")
    b += text(W/2, H-30,
              "Дрібність деталей обмежена довжиною хвилі світла. Шлях до нанометрів — це шлях до коротших хвиль,",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-12,
              "аж до EUV (13.5 нм), де навіть повітря й скло поглинають промінь — тому все у вакуумі й на дзеркалах.",
              12, GREY, "middle", style="italic")
    save("fig-3-10-2-3-wavelength.svg", b)


def fig_2_4_cleanroom():
    """Чому чисте повітря критичне: пилинка більша за деталь."""
    W, H = 720, 330
    b = header(W, H)
    b = title(b, W/2, 28, "Чому повітря мусить бути надчистим")
    # scale bar comparison
    # feature size vs dust mote vs human hair
    items = [
        ("Деталь чіпа", "~10–50 нм", 6, GREEN),
        ("Вірус", "~100 нм", 14, AMBER),
        ("Дрібний пил", "~1000 нм (1 мкм)", 70, RED),
        ("Волосина", "~70 000 нм (70 мкм)", 200, INK),
    ]
    x0 = 80
    y = 90
    for name, lab, d, col in items:
        b += circle(x0+110, y, d/2, col if d < 100 else "none", col, 2.5)
        b += text(x0+260, y-4, name, 13.5, INK, "start", "bold")
        b += text(x0+260, y+15, lab, 12, col, "start")
        y += max(56, d/2+34)
    b += text(W/2, H-44,
              "Одна порошинка завбільшки з мікрон — це гора над деталлю в десятки нанометрів: вона накриває",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-26,
              "й губить сотні транзисторів. Тому в чистій кімнаті класу 1 повітря фільтрують так, що в кубометрі",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-8,
              "лишаються одиниці частинок — у мільйони разів чистіше за операційну.",
              12, GREY, "middle", style="italic")
    save("fig-3-10-2-4-cleanroom.svg", b)


# ════════════════════════════════════════════════════════════════════════════
# ТЕМА 3.10.3 — Шар за шаром: легування, травлення, метал
# ════════════════════════════════════════════════════════════════════════════

def _wafer_layer(x, y, w, h, fill, stroke=INK, sw=1.6):
    return rect(x, y, w, h, fill, stroke, sw)


def fig_3_1_buildup():
    """Поетапна будова MOSFET на пластині: 6 кроків у розрізі."""
    W, H = 760, 470
    b = header(W, H)
    b = title(b, W/2, 26, "Як на пластині росте транзистор (розріз, крок за кроком)")
    pw, ph = 200, 60
    gap_x, gap_y = 36, 56
    x0 = 50
    y0 = 64

    def base(x, y, sub="#aebfd8"):
        return rect(x, y+ph-26, pw, 26, sub, INK, 1.6)  # silicon substrate

    steps = []

    # Step 1: oxide grown on silicon
    s = base(x0, y0)
    s += rect(x0, y0+ph-26-12, pw, 12, "#cfe0a8", "#7a9a3a", 1.4)  # oxide
    s += text(x0+pw+8, y0+ph-26-6, "оксид SiO₂", 11, "#5a7a1a", "start")
    steps.append(("1. Окислення: вирощують ізолятор", s, x0, y0))

    # Step 2: gate stack (poly) patterned
    x = x0+pw+gap_x
    s = base(x, y0)
    s += rect(x, y0+ph-26-10, pw, 10, "#cfe0a8", "#7a9a3a", 1.4)
    s += rect(x+pw/2-26, y0+ph-26-30, 52, 20, "#c9c9c9", INK, 1.6)  # gate
    s += text(x+pw/2, y0+ph-26-34, "затвор", 10.5, INK, "middle", "bold")
    steps.append(("2. Затвор: ізолятор + полікремній", s, x, y0))

    # Step 3: ion implant S/D (doping)
    x = x0
    y = y0+ph+gap_y
    s = base(x, y)
    s += rect(x, y+ph-26-10, pw, 10, "#cfe0a8", "#7a9a3a", 1.4)
    s += rect(x+pw/2-26, y+ph-26-30, 52, 20, "#c9c9c9", INK, 1.6)
    # implant arrows
    for dx in (-70, -50, 50, 70):
        s += arrow(x+pw/2+dx, y-2, x+pw/2+dx, y+ph-26-12, RED, 1.4)
    # doped regions
    s += rect(x+10, y+ph-26, 56, 18, "#f3c0bb", RED, 1.4)
    s += rect(x+pw-66, y+ph-26, 56, 18, "#f3c0bb", RED, 1.4)
    s += text(x+38, y+ph-26+13, "n+", 11, RED, "middle", "bold")
    s += text(x+pw-38, y+ph-26+13, "n+", 11, RED, "middle", "bold")
    steps.append(("3. Легування: іони стік/витік (§2.5.2)", s, x, y))

    # Step 4: contacts (vias) through oxide
    x = x0+pw+gap_x
    s = base(x, y)
    s += rect(x, y+ph-46, pw, 20, "#e7eef8", "#9fb0c8", 1.2)  # ILD oxide above
    s += rect(x+10, y+ph-26, 56, 18, "#f3c0bb", RED, 1.2)
    s += rect(x+pw-66, y+ph-26, 56, 18, "#f3c0bb", RED, 1.2)
    s += rect(x+pw/2-22, y+ph-26-20, 44, 14, "#c9c9c9", INK, 1.2)
    # tungsten plugs
    for vx in (x+34, x+pw/2, x+pw-34):
        s += rect(vx-5, y+ph-46, 10, 20, "#888888", INK, 1.2)
    s += text(x+pw+8, y+ph-40, "вольфрамові", 10.5, GREY, "start")
    s += text(x+pw+8, y+ph-28, "пробки (via)", 10.5, GREY, "start")
    steps.append(("4. Контакти: вертикальні з'єднання", s, x, y))

    # Step 5: metal 1
    x = x0
    y = y0+2*(ph+gap_y)
    s = base(x, y)
    s += rect(x, y+ph-46, pw, 20, "#e7eef8", "#9fb0c8", 1.2)
    for vx in (x+34, x+pw/2, x+pw-34):
        s += rect(vx-5, y+ph-46, 10, 20, "#888888", INK, 1.2)
    # metal lines on top
    s += rect(x+16, y+ph-54, 60, 9, "#e0a020", "#a06000", 1.2)
    s += rect(x+pw-96, y+ph-54, 80, 9, "#e0a020", "#a06000", 1.2)
    s += text(x+pw+8, y+ph-50, "метал 1 (Cu)", 10.5, "#a06000", "start")
    steps.append(("5. Метал: перший шар проводів", s, x, y))

    # Step 6: many metal layers stacked
    x = x0+pw+gap_x
    s = base(x, y)
    s += rect(x, y+ph-50, pw, 24, "#e7eef8", "#9fb0c8", 1.0)
    for k, yy in enumerate([y+ph-54, y+ph-62, y+ph-70, y+ph-78]):
        for seg in [(20, 50), (90, 40), (150, 36)]:
            s += rect(x+seg[0], yy, seg[1], 6, "#e0a020", "#a06000", 0.8)
    # vias between layers
    for vx in (x+50, x+120, x+170):
        s += line(vx, y+ph-78, vx, y+ph-50, "#888888", 3)
    s += text(x+pw+8, y+ph-70, "багато шарів", 10.5, "#a06000", "start")
    s += text(x+pw+8, y+ph-58, "металу (10+)", 10.5, "#a06000", "start")
    steps.append(("6. Стек з'єднань: 10+ шарів металу", s, x, y))

    for label, body, x, y in steps:
        b += body
        b += text(x, y-6, label, 12, INK, "start", "bold")
    save("fig-3-10-3-1-buildup.svg", b)


def fig_3_2_mosfet_full():
    """Готовий MOSFET у розрізі з підписами (зв'язок із §2.7.2)."""
    W, H = 720, 360
    b = header(W, H)
    b = title(b, W/2, 28, "Готовий MOSFET у розрізі: що збудували (пор. §2.7.2)")
    x0, y0 = 140, 110
    w, h = 440, 150
    # substrate (p)
    b += rect(x0, y0, w, h, "#cdd9ec", INK, 2)
    b += text(x0+w-10, y0+h-12, "підкладка p-Si", 12, BLUE, "end")
    # source / drain n+
    b += rect(x0+30, y0, 90, 46, "#f3c0bb", RED, 1.6)
    b += rect(x0+w-120, y0, 90, 46, "#f3c0bb", RED, 1.6)
    b += text(x0+75, y0+28, "n+", 14, RED, "middle", "bold")
    b += text(x0+w-75, y0+28, "n+", 14, RED, "middle", "bold")
    # gate oxide
    b += rect(x0+120, y0-8, w-240, 8, "#cfe0a8", "#5a7a1a", 1.4)
    # gate poly
    b += rect(x0+120, y0-34, w-240, 26, "#c9c9c9", INK, 1.8)
    b += text(x0+w/2, y0-17, "затвор (polysilicon)", 12, INK, "middle", "bold")
    # channel highlight
    b += rect(x0+120, y0, w-240, 12, "none", GREEN, 2, )
    b += text(x0+w/2, y0+34, "канал (тут поле відкриває провідність)", 11.5, GREEN, "middle")
    # terminal labels with leaders
    b += line(x0+75, y0, x0+75, y0-50, GREY, 1.4)
    b += text(x0+75, y0-58, "Витік (S)", 12, INK, "middle", "bold")
    b += line(x0+w-75, y0, x0+w-75, y0-50, GREY, 1.4)
    b += text(x0+w-75, y0-58, "Стік (D)", 12, INK, "middle", "bold")
    b += text(x0+w/2, y0-44, "G", 12, INK, "middle")
    # oxide label
    b += arrow(x0+120, y0-4, x0+70, y0+18, "#5a7a1a", 1.4)
    b += text(x0+50, y0+34, "тонкий оксид", 11, "#5a7a1a", "middle")
    b += text(W/2, H-26,
              "Усе, що в §2.7.2 було «затвор–ізолятор–канал», тут — результат окремих кроків фабрикації:",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-8,
              "оксид виростили, затвор осадили, n+-області вживили, контакти пробили. Будова = послідовність кроків.",
              12, GREY, "middle", style="italic")
    save("fig-3-10-3-2-mosfet-full.svg", b)


def fig_3_3_etch():
    """Адитивне vs субтрактивне: легування додає, травлення прибирає."""
    W, H = 720, 300
    b = header(W, H)
    b = title(b, W/2, 28, "Дві дії над шаром: додати або прибрати")
    # subtractive (etch)
    ox = 70
    b += text(ox+150, 64, "Травлення (etch) — прибрати зайве", 13.5, INK, "middle", "bold")
    # before
    b += rect(ox, 100, 300, 22, "#aebfd8", INK, 1.6)
    b += rect(ox, 78, 300, 22, "#e0a020", "#a06000", 1.6)
    # resist mask on top
    for rx, rw in [(ox+30, 60), (ox+170, 80)]:
        b += rect(rx, 64, rw, 14, "#f6d6a8", "#b8863a", 1.4)
    b += arrow(ox+150, 132, ox+150, 156, INK, 2)
    # after: material removed where no resist
    yb = 168
    b += rect(ox, yb+22, 300, 22, "#aebfd8", INK, 1.6)
    for rx, rw in [(ox+30, 60), (ox+170, 80)]:
        b += rect(rx, yb, rw, 22, "#e0a020", "#a06000", 1.6)
    b += text(ox+150, yb+62, "лишилося лише під маскою", 11.5, GREY, "middle")

    # additive (deposit/implant) on right
    ox = 410
    b += text(ox+150, 64, "Осадження/легування — додати шар", 13.5, INK, "middle", "bold")
    b += rect(ox, 100, 300, 22, "#aebfd8", INK, 1.6)
    b += arrow(ox+150, 132, ox+150, 156, INK, 2)
    yb = 168
    b += rect(ox, yb+22, 300, 22, "#aebfd8", INK, 1.6)
    b += rect(ox, yb, 300, 22, "#cfe0a8", "#5a7a1a", 1.6)
    b += text(ox+150, yb+62, "новий суцільний шар згори", 11.5, GREY, "middle")
    b += text(W/2, H-14,
              "Повторюючи «додати — накрити маскою — прибрати зайве» десятки разів, нарощують увесь чіп.",
              12, GREY, "middle", style="italic")
    save("fig-3-10-3-3-etch.svg", b)


# ════════════════════════════════════════════════════════════════════════════
# ТЕМА 3.10.4 — «5 нанометрів» маркетингу
# ════════════════════════════════════════════════════════════════════════════

def fig_4_1_node_vs_real():
    """Назва вузла vs реальні розміри: число «5 нм» ≠ жоден фізичний розмір."""
    W, H = 720, 360
    b = header(W, H)
    b = title(b, W/2, 28, "«5 нм» — це назва, а не фізичний розмір")
    # left: the marketing label
    b += rect(70, 80, 230, 90, "#fde0dd", RED, 2.5, 12)
    b += text(185, 118, "«5 нм»", 30, RED, "middle", "bold")
    b += text(185, 150, "назва техпроцесу", 13, INK, "middle")
    b += arrow(310, 125, 380, 125, INK, 2.4)
    b += text(345, 112, "насправді", 11.5, GREY, "middle")
    # right: real dimensions, none equal 5nm
    rows = [
        ("Крок затворів (gate pitch)", "~48–56 нм"),
        ("Крок металу (metal pitch)", "~30–36 нм"),
        ("Довжина затвора (фізична)", "~16–20 нм"),
        ("«5 нм» як розмір чогось", "— нічого", True),
    ]
    rx, ry = 400, 84
    for i, row in enumerate(rows):
        miss = len(row) > 2
        col = RED if miss else INK
        b += rect(rx, ry+i*46, 270, 38, "#fbeaea" if miss else "#f4f4f4",
                  col, 1.8 if miss else 1.4, 6)
        b += text(rx+10, ry+i*46+24, row[0], 12, INK, "start",
                  "bold" if miss else "normal")
        b += text(rx+260, ry+i*46+24, row[1], 12.5, col, "end", "bold")
    b += text(W/2, H-36,
              "Колись «вузол» приблизно дорівнював довжині затвора. Із ~2000-х цей зв'язок розпався:",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-18,
              "сьогодні «5 нм», «3 нм» — лише маркетингові мітки поколінь, не виміряні нанометри на кремнії.",
              12, GREY, "middle", style="italic")
    save("fig-3-10-4-1-node-vs-real.svg", b)


def fig_4_2_density():
    """Що насправді росте: щільність транзисторів (млн/мм²) по вузлах."""
    W, H = 720, 360
    b = header(W, H)
    b = title(b, W/2, 28, "Що справді міряє вузол: щільність транзисторів")
    # log-ish bar chart
    nodes = [
        ("90 нм", 1.5),
        ("45 нм", 3.3),
        ("28 нм", 12),
        ("14 нм", 38),
        ("7 нм", 100),
        ("5 нм", 170),
        ("3 нм", 290),
    ]
    x0, base = 90, 290
    bw, gap = 56, 30
    maxv = 290
    plot_h = 200
    # axis
    b += line(x0-16, base, W-40, base, INK, 1.5)
    b += line(x0-16, base, x0-16, base-plot_h-10, INK, 1.5)
    b += text(x0-16, base-plot_h-20, "млн транз./мм²", 11.5, GREY, "start")
    for i, (name, v) in enumerate(nodes):
        x = x0 + i*(bw+gap)
        hh = plot_h*(v/maxv)
        b += rect(x, base-hh, bw, hh, GREEN, "#155f29", 1.4)
        b += text(x+bw/2, base-hh-6, str(v), 11.5, "#155f29", "middle", "bold")
        b += text(x+bw/2, base+18, name, 12, INK, "middle")
    b += text(W/2, H-30,
              "За назвами поколінь стоїть справжня величина — скільки транзисторів влазить на квадратний міліметр.",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-12,
              "Саме вона зростає від вузла до вузла; орієнтуйтеся на неї, а не на романтичні «нанометри».",
              12, GREY, "middle", style="italic")
    save("fig-3-10-4-2-density.svg", b)


def fig_4_3_finfet():
    """Планарний → FinFET → GAA: чому геометрія, а не лише розмір."""
    W, H = 720, 320
    b = header(W, H)
    b = title(b, W/2, 28, "Прогрес — не лише дрібніше, а й інша форма затвора")
    panels = [
        ("Планарний", "затвор зверху"),
        ("FinFET", "затвор з трьох боків"),
        ("GAA / nanosheet", "затвор з усіх боків"),
    ]
    pw = 210
    x0 = 40
    for i, (name, note) in enumerate(panels):
        ox = x0 + i*(pw+15)
        b += text(ox+pw/2, 62, name, 13.5, INK, "middle", "bold")
        b += text(ox+pw/2, 80, note, 11.5, GREY, "middle")
        cx = ox+pw/2
        cy = 170
        if i == 0:
            # planar: channel slab, gate on top
            b += rect(cx-70, cy, 140, 22, "#f3c0bb", RED, 1.4)
            b += rect(cx-40, cy-22, 80, 22, "#9bb0d8", BLUE, 1.6)
            b += text(cx, cy-8, "G", 12, INK, "middle", "bold")
            b += text(cx, cy+50, "контакт лише згори", 11, GREY, "middle")
        elif i == 1:
            # finfet: vertical fin, gate wraps 3 sides
            b += rect(cx-12, cy-40, 24, 70, "#f3c0bb", RED, 1.4)  # fin
            b += rect(cx-30, cy-30, 60, 50, "none", BLUE, 3)  # gate U
            b += line(cx-30, cy+20, cx+30, cy+20, "#ffffff", 4)  # open bottom front
            b += text(cx, cy-50, "fin", 11, RED, "middle", "bold")
            b += text(cx, cy+50, "затвор огортає 3 боки", 11, GREY, "middle")
        else:
            # GAA: stacked nanosheets, gate all around
            for k, yy in enumerate([cy-30, cy-6, cy+18]):
                b += ellipse(cx, yy, 30, 8, "#f3c0bb", RED, 1.4)
                b += ellipse(cx, yy, 38, 13, "none", BLUE, 2)
            b += text(cx, cy+50, "затвор з усіх боків", 11, GREY, "middle")
    b += text(W/2, H-30,
              "Коли транзистор крихітний, керувати каналом «зверху» вже мало — струм тече повз.",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-12,
              "Тому затвор обгортають канал щільніше: 3 боки (FinFET), потім усі (GAA). Це геометрія, а не «нанометри».",
              12, GREY, "middle", style="italic")
    save("fig-3-10-4-3-finfet.svg", b)


# ════════════════════════════════════════════════════════════════════════════
# ТЕМА 3.10.5 — Yield: дефекти як статистика
# ════════════════════════════════════════════════════════════════════════════

def _wafer_grid(cx, cy, R, cell, defects, kill_color=RED, ok_color="#cfe7d2"):
    """Малює круглу пластину, посічену на кристали; deфекти позначає точками,
    уражені клітини фарбує. Повертає (svg, total_dies, killed_dies)."""
    out = circle(cx, cy, R, "#f3f7fc", INK, 2)
    out += line(cx-R*0.34, cy+R*0.94, cx+R*0.34, cy+R*0.94, "#ffffff", 6)
    n = int((2*R)//cell)
    start = -((n*cell)/2)
    dies = []
    for i in range(n):
        for j in range(n):
            x = cx + start + i*cell
            y = cy + start + j*cell
            # cell fully inside circle?
            corners = [(x, y), (x+cell, y), (x, y+cell), (x+cell, y+cell)]
            if all((px-cx)**2 + (py-cy)**2 <= (R-2)**2 for px, py in corners):
                dies.append((x, y))
    killed = set()
    for dx, dy in defects:
        for idx, (x, y) in enumerate(dies):
            if x <= dx <= x+cell and y <= dy <= y+cell:
                killed.add(idx)
    for idx, (x, y) in enumerate(dies):
        col = "#f6d4d0" if idx in killed else ok_color
        out += rect(x, y, cell-2, cell-2, col, GREY, 0.8)
    for dx, dy in defects:
        out += circle(dx, dy, 3.4, kill_color, "#7a1812", 1)
    return out, len(dies), len(killed)


def fig_5_1_defects():
    """Однакова густина дефектів б'є по великому й малому кристалу по-різному."""
    W, H = 760, 430
    b = header(W, H)
    b = title(b, W/2, 26, "Та сама густина дефектів — різна доля втрат")
    # same defect positions on both wafers
    import random
    random.seed(7)
    R = 150
    cyA = 220
    cxA = 200
    defs = []
    while len(defs) < 14:
        x = cxA + (random.random()*2-1)*R
        y = cyA + (random.random()*2-1)*R
        if (x-cxA)**2 + (y-cyA)**2 <= (R-6)**2:
            defs.append((x, y))
    # big dies
    g1, t1, k1 = _wafer_grid(cxA, cyA, R, 56, defs)
    b += g1
    b += text(cxA, 62, "Великі кристали", 13.5, INK, "middle", "bold")
    good1 = t1-k1
    b += text(cxA, cyA+R+34, f"усього {t1} · уражено {k1} · цілих {good1}", 12.5, INK, "middle")
    b += text(cxA, cyA+R+54, f"вихід ≈ {round(100*good1/t1)}%", 13, RED, "middle", "bold")
    # small dies, same defects relative positions (shift to right wafer)
    cxB = 560
    defsB = [(x - cxA + cxB, y) for x, y in defs]
    g2, t2, k2 = _wafer_grid(cxB, cyA, R, 26, defsB)
    b += g2
    b += text(cxB, 62, "Малі кристали", 13.5, INK, "middle", "bold")
    good2 = t2-k2
    b += text(cxB, cyA+R+34, f"усього {t2} · уражено {k2} · цілих {good2}", 12.5, INK, "middle")
    b += text(cxB, cyA+R+54, f"вихід ≈ {round(100*good2/t2)}%", 13, GREEN, "middle", "bold")
    b += text(W/2, H-26,
              "Кожна точка-дефект убиває рівно той кристал, у який потрапила. Великий кристал ловить дефект",
              11.5, GREY, "middle", style="italic")
    b += text(W/2, H-10,
              "майже завжди; дрібний — рідко, і одна пляма псує лише його. Тому площа кристала б'є по виходу нелінійно.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-10-5-1-defects.svg", b)


def fig_5_2_yield_curve():
    """Yield = exp(−D·A): як вихід падає з площею кристала."""
    W, H = 720, 360
    b = header(W, H)
    b = title(b, W/2, 28, "Вихід падає з площею кристала (модель Пуассона)")
    x0, y0 = 90, 290
    pw, phh = 560, 220
    b += line(x0, y0, x0+pw, y0, INK, 1.5)
    b += line(x0, y0, x0, y0-phh, INK, 1.5)
    b += text(x0-6, y0-phh-8, "вихід Y", 12, GREY, "start")
    b += text(x0+pw, y0+24, "площа кристала A →", 12, GREY, "end")
    # y ticks
    for yv in (0, 25, 50, 75, 100):
        yy = y0 - phh*(yv/100)
        b += line(x0-5, yy, x0, yy, INK, 1.2)
        b += text(x0-10, yy+4, f"{yv}%", 11, GREY, "end")
    # curves for two defect densities D
    Amax = 4.0  # arbitrary normalized area
    for D, col, lab in [(0.3, GREEN, "мало дефектів (D мала)"),
                        (0.9, RED, "багато дефектів (D велика)")]:
        pts = []
        for k in range(0, 121):
            A = Amax*k/120
            Y = math.exp(-D*A)
            xx = x0 + pw*(A/Amax)
            yy = y0 - phh*Y
            pts.append((xx, yy))
        b += polyline(pts, col, 2.6)
        # label near right end
        endY = math.exp(-D*Amax)
        b += text(x0+pw+4, y0-phh*endY+4, lab, 11, col, "start")
    # mark example points: small vs big die for D=0.9
    for A, name in [(0.6, "малий кристал"), (2.6, "великий кристал")]:
        Y = math.exp(-0.9*A)
        xx = x0 + pw*(A/Amax)
        yy = y0 - phh*Y
        b += circle(xx, yy, 4, RED, "#7a1812", 1.2)
        b += line(xx, yy, xx, y0, GREY, 1, dash="3,3")
        b += text(xx, y0+18, name, 10.5, INK, "middle")
        b += text(xx, yy-10, f"{round(100*Y)}%", 11, RED, "middle", "bold")
    b += text(x0+pw/2, y0-phh-2, "Y ≈ e^(−D·A)", 14, INK, "middle", "bold")
    b += text(W/2, H-12,
              "Подвоїти площу кристала — не вдвічі, а експоненційно менше придатних: ось чому великий чіп коштує непропорційно дорого.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-10-5-2-yield-curve.svg", b)


def fig_5_3_cost():
    """Чому великий кристал дорожчий: менше штук + нижчий вихід = подвійний удар."""
    W, H = 720, 300
    b = header(W, H)
    b = title(b, W/2, 28, "Подвійний удар по ціні великого кристала")
    # two factors stacked
    factors = [
        ("Менше кристалів на пластині", "велика площа → їх просто менше вміщається", GREY),
        ("Нижчий вихід (більше браку)", "велика площа → частіше ловить дефект (Y↓)", RED),
    ]
    y = 90
    for name, note, col in factors:
        b += rect(70, y, 580, 50, "#f7f7f7", col, 1.8, 8)
        b += text(86, y+22, name, 13.5, INK, "start", "bold")
        b += text(86, y+40, note, 12, GREY, "start")
        y += 66
    # combine arrow
    b += arrow(360, y, 360, y+26, INK, 2.4)
    b += rect(210, y+30, 300, 50, "#fde0dd", RED, 2.5, 10)
    b += text(360, y+52, "ціна за придатний кристал", 13, RED, "middle", "bold")
    b += text(360, y+72, "росте набагато швидше за площу", 12, RED, "middle")
    b += text(W/2, H-12,
              "Два множники діють в один бік — тому подвоєння площі може здорожчати придатний кристал у кілька разів.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-10-5-3-cost.svg", b)


# ════════════════════════════════════════════════════════════════════════════
# ТЕМА 3.10.6 — Тестування й binning
# ════════════════════════════════════════════════════════════════════════════

def fig_6_1_probe():
    """Зондовий контроль пластини: голки на контактні площадки, карта годен/брак."""
    W, H = 720, 360
    b = header(W, H)
    b = title(b, W/2, 28, "Зондовий контроль: кожен кристал перевіряють на пластині")
    # left: probe card on a die
    cx = 200
    cy = 170
    b += rect(cx-90, cy-60, 180, 120, "#e7eef8", INK, 2)  # die
    b += text(cx, cy-40, "один кристал", 11.5, INK, "middle")
    # pads
    pads = []
    for i in range(6):
        px = cx-70 + i*28
        b += rect(px-6, cy+30, 12, 12, "#e0a020", "#a06000", 1.2)
        pads.append((px, cy+30))
    # probe needles from above
    for px, py in pads:
        b += line(px, cy-100, px, py, GREY, 1.6)
        b += polygon([(px-3, py-2), (px+3, py-2), (px, py+5)], INK, INK, 0.5)
    b += rect(cx-90, cy-118, 180, 20, "#dddddd", INK, 1.6)
    b += text(cx, cy-104, "зондова карта (голки)", 11, INK, "middle")
    b += text(cx, cy+76, "торкаються площадок, подають живлення й тести", 11, GREY, "middle")
    # right: wafer bin map
    wx = 540
    wy = 170
    R = 110
    b += circle(wx, wy, R, "#f3f7fc", INK, 2)
    b += line(wx-R*0.34, wy+R*0.94, wx+R*0.34, wy+R*0.94, "#ffffff", 5)
    import random
    random.seed(11)
    cell = 22
    n = int((2*R)//cell)
    start = -((n*cell)/2)
    for i in range(n):
        for j in range(n):
            x = wx+start+i*cell
            y = wy+start+j*cell
            corners = [(x, y), (x+cell, y), (x, y+cell), (x+cell, y+cell)]
            if all((px-wx)**2 + (py-wy)**2 <= (R-2)**2 for px, py in corners):
                r = random.random()
                if r < 0.7:
                    col = "#cfe7d2"  # pass
                elif r < 0.85:
                    col = "#fde9b0"  # bin (slower)
                else:
                    col = "#f6d4d0"  # fail
                b += rect(x, y, cell-2, cell-2, col, GREY, 0.7)
    b += text(wx, wy+R+24, "карта результатів (bin map)", 11.5, INK, "middle", "bold")
    # legend
    lx = wx-70
    ly = wy+R+40
    for col, lab in [("#cfe7d2", "годен"), ("#fde9b0", "сорт"), ("#f6d4d0", "брак")]:
        b += rect(lx, ly-10, 14, 14, col, GREY, 1)
        b += text(lx+20, ly+2, lab, 11, INK, "start")
        lx += 78
    save("fig-3-10-6-1-probe.svg", b)


def fig_6_2_binning():
    """Один кристал → кілька продуктів: сорт за частотою і вимкнені блоки."""
    W, H = 760, 400
    b = header(W, H)
    b = title(b, W/2, 26, "Один дизайн — кілька продуктів (binning)")
    # source die at top
    cx = W/2
    b += rect(cx-70, 56, 140, 56, "#e7eef8", INK, 2, 8)
    b += text(cx, 80, "однакові кристали", 12, INK, "middle", "bold")
    b += text(cx, 98, "з однієї пластини", 11.5, GREY, "middle")
    # split by frequency
    bins = [
        ("Топ-сорт", "стабільний на 3.5 ГГц", "усі ядра", GREEN, 200),
        ("Середній", "до 3.0 ГГц", "усі ядра", AMBER, 400),
        ("Бюджетний", "до 2.6 ГГц", "2 ядра вимкнено", RED, 600),
    ]
    for name, freq, cores, col, x in bins:
        b += arrow(cx, 116, x, 168, GREY, 1.8)
        b += rect(x-90, 172, 180, 96, "#f7f7f7", col, 2, 10)
        b += text(x, 196, name, 13.5, col, "middle", "bold")
        b += text(x, 218, freq, 12, INK, "middle")
        b += text(x, 238, cores, 12, INK, "middle")
        # mini chip with cores
        for k in range(4):
            on = not (col == RED and k >= 2)
            fill = "#bfe0c4" if on else "#dcdcdc"
            stroke = GREEN if on else GREY
            b += rect(x-42+k*22, 248, 16, 14, fill, stroke, 1.2)
    b += text(W/2, H-44,
              "Жоден кристал не ідеальний однаково. Кращі тримають вищу частоту — у дорогий сорт; ті, де якийсь блок",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-26,
              "бракований, продають із вимкненим блоком як дешевшу модель. Так із одного дизайну виходить лінійка.",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-8,
              "Це не марнотратство, а спосіб продати майже кожен кристал — навіть із дрібним дефектом.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-10-6-2-binning.svg", b)


# ════════════════════════════════════════════════════════════════════════════
# ТЕМА 3.10.7 — Корпусування
# ════════════════════════════════════════════════════════════════════════════

def fig_7_1_wirebond_flip():
    """Wire bonding vs flip-chip: два способи з'єднати кристал із корпусом."""
    W, H = 760, 360
    b = header(W, H)
    b = title(b, W/2, 26, "Два способи з'єднати кристал зі світом")
    # wire bonding (left)
    ox = 60
    b += text(ox+150, 60, "Wire bonding (дротяні з'єднання)", 13, INK, "middle", "bold")
    # substrate
    b += rect(ox, 200, 300, 30, "#2f6f3f", "#163b21", 2)  # package substrate (green)
    # die on top, face up
    b += rect(ox+90, 170, 120, 30, "#9fb0c8", INK, 2)
    b += text(ox+150, 190, "кристал (лицем угору)", 10, INK, "middle")
    # bond pads on die top and leads
    die_pads = [ox+100, ox+130, ox+170, ox+200]
    lead_pads = [ox+24, ox+64, ox+236, ox+276]
    for dp, lp in zip(die_pads, lead_pads):
        # gold wire arc
        b += path(f"M {dp},170 Q {(dp+lp)/2},120 {lp},200", fill="none", stroke="#d4a017", w=1.8)
        b += rect(lp-5, 196, 10, 8, "#888888", INK, 1)
    b += text(ox+150, 150, "тонкі золоті дротики", 10.5, "#a06000", "middle")
    b += text(ox+150, 252, "дротики йдуть від верху кристала до виводів", 10.5, GREY, "middle")

    # flip-chip (right)
    ox = 420
    b += text(ox+150, 60, "Flip-chip (перевернутий кристал)", 13, INK, "middle", "bold")
    b += rect(ox, 200, 300, 30, "#2f6f3f", "#163b21", 2)
    # die flipped, face down, bumps under
    b += rect(ox+80, 150, 140, 34, "#9fb0c8", INK, 2)
    b += text(ox+150, 144, "кристал (лицем униз)", 10, INK, "middle")
    # solder bumps
    for k in range(7):
        bx = ox+92 + k*19
        b += circle(bx, 192, 6, "#c0c0c0", INK, 1.2)
    b += text(ox+150, 252, "кулькові виводи прямо під кристалом", 10.5, GREY, "middle")
    b += text(ox+150, 270, "коротший шлях — швидше й більше з'єднань", 10.5, GREEN, "middle")
    b += text(W/2, H-30,
              "Дротики (bonding) дешеві й усюди; перевернутий кристал (flip-chip) дає сотні коротких з'єднань",
              11.5, GREY, "middle", style="italic")
    b += text(W/2, H-12,
              "одразу під кристалом — його беруть, коли виводів багато або потрібна швидкість.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-10-7-1-wirebond-flip.svg", b)


def fig_7_2_packages():
    """QFN vs BGA: звідки беруться «ніжки» (вид знизу + розріз)."""
    W, H = 760, 380
    b = header(W, H)
    b = title(b, W/2, 26, "Звідки беруться виводи: QFN і BGA")
    # QFN (left): bottom view + side
    ox = 60
    b += text(ox+150, 58, "QFN — контакти по краю знизу", 13, INK, "middle", "bold")
    # bottom view
    b += rect(ox+40, 80, 140, 140, "#dddddd", INK, 2)
    for k in range(6):
        # top & bottom edge pads
        b += rect(ox+52+k*22, 82, 14, 12, "#c8a040", "#806010", 1)
        b += rect(ox+52+k*22, 206, 14, 12, "#c8a040", "#806010", 1)
        # left & right edge pads
        b += rect(ox+42, 94+k*20, 12, 14, "#c8a040", "#806010", 1)
        b += rect(ox+166, 94+k*20, 12, 14, "#c8a040", "#806010", 1)
    b += rect(ox+92, 132, 36, 36, "#b0b0b0", INK, 1.2)  # exposed pad
    b += text(ox+110, 154, "тепловий", 8.5, INK, "middle")
    b += text(ox+110, 234, "вид знизу", 10.5, GREY, "middle")
    # side cross-section
    b += rect(ox+40, 270, 140, 26, "#444444", INK, 1.6)
    for k in range(7):
        b += rect(ox+44+k*19, 294, 12, 6, "#c8a040", "#806010", 1)
    b += text(ox+110, 318, "контакти — плоскі площадки по периметру", 10, GREY, "middle")

    # BGA (right): bottom view (grid of balls) + side
    ox = 430
    b += text(ox+150, 58, "BGA — решітка кульок припою", 13, INK, "middle", "bold")
    b += rect(ox+40, 80, 140, 140, "#cfd8e8", INK, 2)
    for i in range(7):
        for j in range(7):
            b += circle(ox+56+i*18, 96+j*18, 6, "#9a9a9a", "#444", 1)
    b += text(ox+110, 234, "вид знизу (масив кульок)", 10.5, GREY, "middle")
    # side
    b += rect(ox+40, 270, 140, 24, "#2f4f6f", INK, 1.6)
    for k in range(8):
        b += circle(ox+50+k*17, 300, 6, "#9a9a9a", "#444", 1)
    b += text(ox+110, 322, "сотні виводів під усім корпусом", 10, GREY, "middle")
    b += text(W/2, H-30,
              "«Ніжки» — це і є виводи кристала, виведені назовні: у QFN — плоскі площадки по краю,",
              11.5, GREY, "middle", style="italic")
    b += text(W/2, H-12,
              "у BGA — кулькова решітка під усім корпусом, коли виводів сотні (пор. §2.9.5).",
              11.5, GREY, "middle", style="italic")
    save("fig-3-10-7-2-packages.svg", b)


def fig_7_3_why_package():
    """Навіщо корпус узагалі: захист, відведення тепла, масштаб виводів."""
    W, H = 720, 290
    b = header(W, H)
    b = title(b, W/2, 28, "Навіщо кристалу корпус")
    roles = [
        ("Захист", "крихкий кремній — у міцну\nоболонку від вологи й ударів", BLUE),
        ("Масштаб виводів", "мікронні площадки кристала →\nконтакти, які можна паяти", GREEN),
        ("Відведення тепла", "тепло від кристала — назовні,\nдо плати й радіатора", RED),
    ]
    bw = 210
    x0 = 40
    for i, (name, note, col) in enumerate(roles):
        ox = x0 + i*(bw+14)
        b += rect(ox, 80, bw, 120, "#f7f7f7", col, 2.2, 12)
        b += text(ox+bw/2, 112, name, 15, col, "middle", "bold")
        for j, ln in enumerate(note.split("\n")):
            b += text(ox+bw/2, 142+j*20, ln, 12, INK, "middle")
    b += text(W/2, H-30,
              "Без корпуса кристал не вживеш: він мікроскопічний, крихкий і гарячий. Корпус робить його придатним",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-12,
              "до плати — захищає, виводить контакти до паяльного масштабу й відводить тепло.",
              12, GREY, "middle", style="italic")
    save("fig-3-10-7-3-why-package.svg", b)


# ════════════════════════════════════════════════════════════════════════════
# ТЕМА 3.10.8 — Фаби й fabless
# ════════════════════════════════════════════════════════════════════════════

def fig_8_1_value_chain():
    """Хто що робить: EDA + IP → fabless дизайн → foundry → корпусування."""
    W, H = 760, 380
    b = header(W, H)
    b = title(b, W/2, 26, "Ланцюг створення чіпа: хто за що відповідає")
    # central pipeline
    nodes = [
        ("Fabless-\nкомпанія", "проєктує чіп\n(дизайн, RTL)", SKY, 130),
        ("Foundry\n(фабрика)", "виготовляє\nпластини", "#cfe7d2", 380),
        ("OSAT", "корпусує\nй тестує", "#fde9b0", 630),
    ]
    cy = 200
    bw, bh = 150, 90
    for name, note, col, x in nodes:
        b += rect(x-bw/2, cy-bh/2, bw, bh, col, INK, 2, 10)
        for j, ln in enumerate(name.split("\n")):
            b += text(x, cy-18+j*18, ln, 13.5, INK, "middle", "bold")
        for j, ln in enumerate(note.split("\n")):
            b += text(x, cy+18+j*15, ln, 11, GREY, "middle")
    b += arrow(130+bw/2, cy, 380-bw/2, cy, INK, 2.4)
    b += arrow(380+bw/2, cy, 630-bw/2, cy, INK, 2.4)
    b += text(255, cy-14, "GDSII", 11, INK, "middle", "bold")
    b += text(255, cy+14, "файл масок", 10.5, GREEN, "middle")
    b += text(505, cy+14, "готові пластини", 10.5, GREEN, "middle")
    # suppliers feeding fabless
    sup = [
        ("EDA-інструменти", "ПЗ для проєктування", 130, 70),
        ("IP-ядра", "готові блоки (CPU, USB…)", 130, 330),
    ]
    for name, note, tx, ty in sup:
        b += rect(tx-90, ty-20, 180, 40, "#efe7f7", PURP, 1.8, 8)
        b += text(tx, ty-2, name, 12, PURP, "middle", "bold")
        b += text(tx, ty+14, note, 10.5, GREY, "middle")
        b += arrow(tx, ty+(20 if ty < cy else -20), tx, cy-bh/2 if ty < cy else cy+bh/2, GREY, 1.6)
    # equipment feeding foundry
    b += rect(380-90, 330-20, 180, 40, "#fbeaea", RED, 1.8, 8)
    b += text(380, 330-2, "ASML / Applied / TEL", 11.5, RED, "middle", "bold")
    b += text(380, 330+14, "обладнання фабрики", 10.5, GREY, "middle")
    b += arrow(380, 330-20, 380, cy+bh/2, GREY, 1.6)
    b += text(W/2, H-12,
              "Жодна ланка не робить усе сама: проєкт, виготовлення, корпусування й інструменти — окремі гравці.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-10-8-1-value-chain.svg", b)


def fig_8_2_fab_cost():
    """Чому майже ніхто не має фабрики: вартість фабу росте з вузлом."""
    W, H = 720, 360
    b = header(W, H)
    b = title(b, W/2, 28, "Чому фабрику не збудуєш у гаражі: ціна фабу")
    x0, base = 90, 290
    pw, phh = 560, 210
    b += line(x0, base, x0+pw, base, INK, 1.5)
    b += line(x0, base, x0, base-phh, INK, 1.5)
    b += text(x0-6, base-phh-8, "вартість сучасного фабу, $ млрд", 11.5, GREY, "start")
    data = [
        ("130 нм", 2),
        ("65 нм", 3),
        ("28 нм", 6),
        ("14 нм", 10),
        ("7 нм", 17),
        ("5 нм", 20),
        ("3 нм", 28),
    ]
    bw, gap = 54, 28
    maxv = 28
    for i, (name, v) in enumerate(data):
        x = x0 + 16 + i*(bw+gap)
        hh = phh*(v/maxv)
        b += rect(x, base-hh, bw, hh, RED, "#7a1812", 1.4)
        b += text(x+bw/2, base-hh-6, f"${v} млрд", 10.5, "#7a1812", "middle", "bold")
        b += text(x+bw/2, base+18, name, 11, INK, "middle")
    b += text(W/2, H-46,
              "Один передовий завод нині коштує $15–30 млрд і ще стільки ж щороку на устаткування й R&D.",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-28,
              "Окупити це можна лише шаленими обсягами. Тому компанії проєктують чіпи (fabless), а виготовлення",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-10,
              "віддають кільком гігантам-фабрикам — економіка масштабу не лишає іншого вибору.",
              12, GREY, "middle", style="italic")
    save("fig-3-10-8-2-fab-cost.svg", b)


def fig_8_3_models():
    """Три бізнес-моделі: IDM, fabless, pure-play foundry."""
    W, H = 720, 300
    b = header(W, H)
    b = title(b, W/2, 28, "Три моделі бізнесу в індустрії чіпів")
    models = [
        ("IDM", "проєктує І виготовляє сам", "власні фабрики", BLUE),
        ("Fabless", "лише проєктує", "віддає виготовлення фабриці", GREEN),
        ("Foundry", "лише виготовляє", "робить чужі чіпи на замовлення", AMBER),
    ]
    bw = 210
    x0 = 40
    for i, (name, line1, line2, col) in enumerate(models):
        ox = x0 + i*(bw+14)
        b += rect(ox, 80, bw, 130, "#f7f7f7", col, 2.2, 12)
        b += text(ox+bw/2, 112, name, 16, col, "middle", "bold")
        b += text(ox+bw/2, 144, line1, 12.5, INK, "middle", "bold")
        # wrap line2
        for j, ln in enumerate(_wrap(line2, 24)):
            b += text(ox+bw/2, 168+j*18, ln, 11.5, GREY, "middle")
    b += text(W/2, H-30,
              "Колись усі були IDM — робили все під одним дахом. Дорожнеча фабрик розколола індустрію надвоє:",
              12, GREY, "middle", style="italic")
    b += text(W/2, H-12,
              "хто проєктує (fabless), і хто виготовляє (foundry). IDM лишилися — але їх дедалі менше.",
              12, GREY, "middle", style="italic")
    save("fig-3-10-8-3-models.svg", b)


if __name__ == "__main__":
    # 3.10.1
    fig_1_1_chain()
    fig_1_2_purity()
    fig_1_3_czochralski()
    fig_1_4_wafer()
    # 3.10.2
    fig_2_1_litho()
    fig_2_2_resist()
    fig_2_3_wavelength()
    fig_2_4_cleanroom()
    # 3.10.3
    fig_3_1_buildup()
    fig_3_2_mosfet_full()
    fig_3_3_etch()
    # 3.10.4
    fig_4_1_node_vs_real()
    fig_4_2_density()
    fig_4_3_finfet()
    # 3.10.5
    fig_5_1_defects()
    fig_5_2_yield_curve()
    fig_5_3_cost()
    # 3.10.6
    fig_6_1_probe()
    fig_6_2_binning()
    # 3.10.7
    fig_7_1_wirebond_flip()
    fig_7_2_packages()
    fig_7_3_why_package()
    # 3.10.8
    fig_8_1_value_chain()
    fig_8_2_fab_cost()
    fig_8_3_models()
    print("\nDone:", len(os.listdir(OUT)), "files in", OUT)
