# -*- coding: utf-8 -*-
"""
Окремий генератор SVG-фігур для ВСТАВКИ 2.11.3c
«Симістори BT136/BTA16-класів і оптодрайвер MOC30xx-класу».
Чистий Python, без сторонніх залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс fig-11-3c-...), щоб не конфліктувати з головним figs.py розділу.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції скопійовано з figs.py
сусідніх розділів модуля 2 заради єдиного вигляду.
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
COPP  = "#b5732e"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#fbf3e0"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aSun" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{SUN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey",
         SUN: "aSun"}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ---------------------------------------------------------------------------
# Рис. 2.11.3c.1 — Блок-схема ізольованого керування симістором:
# МК → MOC30xx (оптотриак-драйвер) → силовий симістор → навантаження в мережі.
# Показано дві землі, гальванічний бар'єр, а всередині оптрона — відмінність
# random-phase (просто оптотриак) проти zero-cross (з детектором нуля).
# ---------------------------------------------------------------------------
def fig_block():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 26, "Ізольоване керування симістором: МК → MOC30xx → BT136/BTA16 → мережа",
              15, INK, "middle", "bold")

    # Гальванічний бар'єр (вертикальна пунктирна лінія) — дві землі
    bx = 300
    s += line(bx, 52, bx, 432, GREY, 1.6, "7 5")
    s += text(bx, 448, "гальванічний бар'єр (оптична розв'язка)", 12, GREY, "middle", "italic")

    # --- Лівий, низьковольтний бік (логіка) ---
    s += rect(40, 70, 150, 320, "#fbfdff", "#c9d3dc", 1.4, 8)
    s += text(115, 90, "БІК ЛОГІКИ", 12, BLUE, "middle", "bold")
    s += text(115, 106, "(GND₁, 3.3 / 5 В)", 11, GREY, "middle")

    # МК
    s += rect(70, 124, 90, 56, LBLUE, BLUE, 1.8, 6)
    s += text(115, 148, "МК", 14, INK, "middle", "bold")
    s += text(115, 166, "(GPIO)", 11, GREY, "middle")

    # Резистор R1 у лінію до світлодіода оптрона
    s += line(115, 180, 115, 214, INK, 2)
    s += rect(99, 214, 32, 40, "#ffffff", INK, 1.8, 3)
    s += text(150, 232, "R1", 12, INK, "start", "bold")
    s += text(150, 248, "≈180 Ом", 10, GREY, "start")
    s += line(115, 254, 115, 286, INK, 2)

    # Вхід оптрона: світлодіод (трикутник анод→катод + катодна смужка)
    ledx = 115
    s += _poly([(ledx - 12, 286), (ledx + 12, 286), (ledx, 304), (ledx - 12, 286)], INK, 2.0)
    s += line(ledx - 13, 304, ledx + 13, 304, INK, 2.4)  # катодна смужка (вістря діода)
    # стрілки випромінювання світла
    s += arrow(ledx + 13, 290, ledx + 30, 284, SUN, 1.6)
    s += arrow(ledx + 13, 296, ledx + 30, 290, SUN, 1.6)
    s += text(ledx - 4, 322, "вхідний LED", 10, GREY, "middle")

    # земля 1
    s += line(115, 304, 115, 360, INK, 2)
    s += line(100, 360, 130, 360, INK, 2.4)
    s += line(105, 366, 125, 366, INK, 2.0)
    s += line(110, 372, 120, 372, INK, 1.6)
    s += text(115, 388, "GND₁", 11, BLUE, "middle", "bold")

    # --- Оптрон MOC30xx сидить верхи на бар'єрі ---
    ox, oy, ow, oh = 232, 120, 136, 196
    s += rect(ox, oy, ow, oh, LSUN, SUN, 2.0, 8)
    s += text(ox + ow / 2, oy + 18, "MOC30xx", 13, INK, "middle", "bold")
    s += text(ox + ow / 2, oy + 34, "опто-симісторний", 10, GREY, "middle")
    s += text(ox + ow / 2, oy + 47, "драйвер", 10, GREY, "middle")

    # маленький оптотріак-символ усередині (двотермінальний світлокерований ключ)
    tx = ox + ow / 2 + 34
    ty = oy + 96
    s += rect(tx - 16, ty - 18, 32, 36, "#ffffff", RED, 1.6, 4)
    # дві зустрічні стрілки = симетричний ключ для обох півхвиль
    s += arrow(tx - 8, ty - 10, tx + 8, ty - 10, RED, 1.4)
    s += arrow(tx + 8, ty + 10, tx - 8, ty + 10, RED, 1.4)
    s += text(tx, ty + 32, "оптотріак", 9, RED, "middle")
    # два головні термінали оптотріака → виводи 6 (верх) і 4 (низ)
    pin6y = oy + 92
    pin4y = oy + 150
    s += line(tx, ty - 18, tx, pin6y, RED, 1.8)
    s += line(tx, pin6y, ox + ow, pin6y, RED, 2)
    s += line(tx, ty + 18, tx, pin4y, RED, 1.8)
    s += line(tx, pin4y, ox + ow, pin4y, RED, 2)

    # детектор нуля — блок усередині, що відрізняє zero-cross від random-phase
    zx = ox + 10
    zy = oy + 76
    s += rect(zx, zy, 44, 40, "#eef6ef", GREEN, 1.6, 5)
    s += text(zx + 22, zy + 16, "детектор", 8.5, GREEN, "middle", "bold")
    s += text(zx + 22, zy + 28, "нуля", 8.5, GREEN, "middle", "bold")
    s += text(zx + 22, zy + 38 + 13, "лише у zero-cross", 8.5, GREEN, "middle", "italic")
    # стрілка від детектора до оптотріака (керує моментом запалення)
    s += arrow(zx + 44, zy + 20, tx - 17, ty - 4, GREEN, 1.4)

    # --- Правий, мережевий бік (сила) ---
    s += rect(410, 70, 320, 320, "#fffdfb", "#e0c39a", 1.4, 8)
    s += text(570, 90, "БІК МЕРЕЖІ", 12, RED, "middle", "bold")
    s += text(570, 106, "(L / N, ~230 В)", 11, GREY, "middle")

    # Виводи оптрона за межі корпусу (6 — верх/MT2-бік, 4 — низ/затворний бік)
    s += line(ox + ow, pin6y, 426, pin6y, RED, 2)
    s += text(ox + ow + 6, pin6y - 6, "6", 9, GREY, "start")
    s += line(ox + ow, pin4y, 426, pin4y, RED, 2)
    s += text(ox + ow + 6, pin4y - 6, "4", 9, GREY, "start")

    # Силовий симістор BT136/BTA16 (праворуч)
    triacx, triacy = 600, 250
    s += rect(triacx - 28, triacy - 30, 56, 60, LRED, RED, 2.0, 6)
    s += arrow(triacx - 12, triacy - 16, triacx + 12, triacy - 16, RED, 1.6)
    s += arrow(triacx + 12, triacy + 16, triacx - 12, triacy + 16, RED, 1.6)
    s += text(triacx, triacy + 52, "BT136 / BTA16", 12, RED, "middle", "bold")
    s += text(triacx, triacy + 67, "силовий симістор", 10, GREY, "middle")
    s += text(triacx + 33, triacy - 18, "MT2", 9, GREY, "start")
    s += text(triacx + 33, triacy + 24, "MT1", 9, GREY, "start")
    # затвор зліва
    gx = triacx - 28
    s += line(gx, triacy, gx - 24, triacy, RED, 2)
    s += text(gx - 28, triacy + 4, "G", 11, RED, "end", "bold")

    # Мережа L приходить згори праворуч і йде на вузол MT2
    Ly = 150
    Lx = 690
    s += text(Lx, Ly - 8, "L (~230 В)", 11, RED, "middle", "bold")
    s += line(Lx, Ly, Lx, triacy - 30, RED, 2.4)
    s += circle(Lx, Ly, 3, RED, RED, 1)
    s += line(Lx, triacy - 30, triacx + 28, triacy - 30, RED, 2)  # L → MT2 (верх симістора)
    s += line(triacx, triacy - 30, triacx + 28, triacy - 30, RED, 2)

    # Вузол A = MT2 = L. Вивід 6 оптрона через R_gate приходить у цей вузол.
    nodeAx = 540
    s += rect(440, pin6y - 15, 36, 30, "#ffffff", INK, 1.8, 3)   # R_gate (R2)
    s += text(458, pin6y - 22, "R2", 11, INK, "middle", "bold")
    s += text(458, pin6y + 34, "≈360 Ом", 9, GREY, "middle")
    s += line(476, pin6y, nodeAx, pin6y, RED, 2)               # R2 → вузол A
    s += line(nodeAx, pin6y, nodeAx, triacy - 30, RED, 2)      # вузол A вниз до рівня MT2
    s += line(nodeAx, triacy - 30, triacx, triacy - 30, RED, 2)  # → MT2
    s += circle(nodeAx, triacy - 30, 3, RED, RED, 1)

    # Вивід 4 оптрона → затвор G
    s += line(426, pin4y, nodeAx - 70, pin4y, RED, 2)
    s += line(nodeAx - 70, pin4y, nodeAx - 70, triacy, RED, 2)
    s += line(nodeAx - 70, triacy, gx - 24, triacy, RED, 2)

    # Навантаження (лампа/нагрівач) між MT1 і N
    s += line(triacx, triacy + 30, triacx, triacy + 92, RED, 2)
    s += rect(triacx - 26, triacy + 92, 52, 30, "#ffffff", INK, 1.8, 4)
    s += text(triacx, triacy + 111, "наванта-", 9, INK, "middle")
    s += text(triacx + 32, triacy + 104, "лампа /", 9, GREY, "start")
    s += text(triacx + 32, triacy + 116, "нагрівач", 9, GREY, "start")
    s += line(triacx, triacy + 122, triacx, triacy + 150, RED, 2)

    # N знизу
    s += line(triacx, triacy + 150, Lx, triacy + 150, RED, 2.4)
    s += text(Lx, triacy + 168, "N", 12, RED, "middle", "bold")
    s += circle(Lx, triacy + 150, 3, RED, RED, 1)

    return W, H, s


# ---------------------------------------------------------------------------
# Рис. 2.11.3c.2 — Те саме керування, два оптрони: коли реально вмикається струм.
# Верх: random-phase (MOC3021/3052) — вмикається ТІЄЇ Ж миті, що й сигнал МК
# (можливе фазове керування). Низ: zero-cross (MOC3041/3061) — ЧЕКАЄ найближчого
# переходу мережі через нуль (чисте ввімкнення, без фазового зрізу).
# ---------------------------------------------------------------------------
def fig_waveforms():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 24, "Коли вмикається струм після команди МК", 15, INK, "middle", "bold")

    ox = 90          # ліва межа осей
    wpl = 600        # ширина області хвиль
    cycles = 2.0     # кількість півперіодів показуємо
    amp = 30

    def panel(oy, title, color, fire_at_command):
        nonlocal s
        # підпис панелі
        s += text(ox - 78, oy - 36, title, 12.5, color, "start", "bold")
        # вісь часу
        s += line(ox, oy, ox + wpl, oy, INK, 1.6)
        s += text(ox + wpl + 14, oy + 4, "t", 12, INK, "start", "bold")
        # синус напруги мережі (тонкий, сірий) — орієнтир переходів через нуль
        pts = []
        for j in range(0, wpl + 1):
            t = j / wpl
            y = oy - amp * math.sin(2 * math.pi * (cycles / 2.0) * t)
            pts.append((ox + j, y))
        s += _poly(pts, GREY, 1.4)
        # позначки переходів мережі через нуль (вертикальні пунктири)
        zc = []
        for k in range(0, int(cycles) + 1):
            zx = ox + wpl * (k / cycles)
            s += line(zx, oy - amp - 6, zx, oy + amp + 6, FAINT, 1.2, "4 4")
            zc.append(zx)
        s += text(zc[0], oy + amp + 22, "0", 10, GREY, "middle")
        s += text(zc[1], oy + amp + 22, "10 мс", 10, GREY, "middle")
        s += text(zc[2], oy + amp + 22, "20 мс", 10, GREY, "middle")

        # команда МК (червона вертикальна стрілка) — десь посеред першого півперіоду
        cmd_t = 0.30
        cx = ox + wpl * (cmd_t / cycles) * cycles  # = ox + wpl*cmd_t
        cx = ox + wpl * cmd_t
        s += arrow(cx, oy - amp - 30, cx, oy - amp - 8, RED, 2)
        s += text(cx, oy - amp - 36, "команда МК", 10, RED, "middle", "bold")

        # коли реально пішов струм
        if fire_at_command:
            fire_x = cx
            note = "вмикається одразу"
        else:
            # чекає наступного переходу через нуль
            fire_x = zc[1]
            note = "чекає переходу через нуль"
        # заштрихована «провідна» частина: від fire_x до кінця показаного півперіоду/області
        # для наочності замалюємо струм навантаження як обвідну синуса після ввімкнення
        ipts = []
        for j in range(0, wpl + 1):
            xx = ox + j
            t = j / wpl
            base = oy + amp + 0  # струм малюємо нижче осі окремою смугою? Ні — поверх синуса.
            if xx >= fire_x:
                y = oy - amp * math.sin(2 * math.pi * (cycles / 2.0) * t)
                ipts.append((xx, y))
            else:
                if ipts:
                    s += _poly(ipts, color, 3.0)
                    ipts = []
        if ipts:
            s += _poly(ipts, color, 3.0)

        # маркер моменту ввімкнення
        s += circle(fire_x, oy, 4, "#ffffff", color, 2)
        s += text(fire_x, oy + amp + 40, note, 10, color, "middle", "italic")
        # стрілка від команди до моменту ввімкнення (для zero-cross показує затримку)
        if not fire_at_command:
            s += arrow(cx + 4, oy - amp - 2, fire_x - 4, oy - amp - 2, color, 1.4, "3 3")
            mid = (cx + fire_x) / 2
            s += text(mid, oy - amp - 8, "затримка ≤ 10 мс", 9.5, color, "middle")

    panel(120, "Random-phase  (MOC3021 / MOC3052)", BLUE, True)
    panel(330, "Zero-cross  (MOC3041 / MOC3061)", GREEN, False)

    # підсумковий рядок
    s += text(W / 2, 452,
              "Червоне/синє/зелене — струм у навантаженні. Сірий синус — напруга мережі.",
              11, GREY, "middle", "italic")
    return W, H, s


def main():
    for fn, name in (
        (fig_block,     "fig-11-3c-1-isolated-triac-drive.svg"),
        (fig_waveforms, "fig-11-3c-2-random-vs-zerocross.svg"),
    ):
        W, H, body = fn()
        save(name, body)


if __name__ == "__main__":
    main()
