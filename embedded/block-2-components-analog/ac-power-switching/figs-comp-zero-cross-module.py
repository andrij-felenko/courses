# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки 2.11.5c — «Модуль детектора нуля (H11AA1-клас)».
Окремий скрипт ВСТАВКИ (не головний figs.py розділу). Унікальні імена → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле — зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції скопійовано з figs.py
попередніх розділів, щоб тримати єдиний вигляд.
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
LYEL  = "#fbf4e2"
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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def dot(cx, cy, r=3.2, color=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{color}"/>\n'


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ----- елементи схеми -----

def led(x, y, ang_down=True, color=RED):
    """Світлодіод як трикутник + риска + дві стрілки світла. Вертикальний."""
    s = ""
    L = 16
    if ang_down:  # струм згори вниз: трикутник вістрям донизу
        s += f'<path d="M {x-9:.1f},{y-L:.1f} L {x+9:.1f},{y-L:.1f} L {x:.1f},{y+2:.1f} Z" fill="none" stroke="{INK}" stroke-width="2"/>\n'
        s += line(x - 9, y + 2, x + 9, y + 2, INK, 2)
    else:         # струм знизу вгору
        s += f'<path d="M {x-9:.1f},{y+L:.1f} L {x+9:.1f},{y+L:.1f} L {x:.1f},{y-2:.1f} Z" fill="none" stroke="{INK}" stroke-width="2"/>\n'
        s += line(x - 9, y - 2, x + 9, y - 2, INK, 2)
    # стрілки «світло»
    s += arrow(x + 11, y - 8, x + 20, y - 14, color, 1.6)
    s += arrow(x + 11, y - 1, x + 20, y - 7, color, 1.6)
    return s


def npn(cx, cy):
    """Фототранзистор NPN: кружок, база ліворуч, колектор зверху, емітер знизу."""
    s = circle(cx, cy, 22, "none", INK, 2)
    # вертикальна планка бази
    s += line(cx - 6, cy - 13, cx - 6, cy + 13, INK, 3)
    # колектор (вгору)
    s += line(cx - 6, cy - 7, cx + 9, cy - 18, INK, 2)
    s += line(cx + 9, cy - 18, cx + 9, cy - 30, INK, 2)
    # емітер (вниз) зі стрілкою назовні
    s += line(cx - 6, cy + 7, cx + 9, cy + 18, INK, 2)
    s += arrow(cx + 9, cy + 18, cx + 9, cy + 30, INK, 2)
    # дві стрілки світла, що падають на базу
    s += arrow(cx - 30, cy - 16, cx - 16, cy - 6, SUN, 1.8)
    s += arrow(cx - 30, cy - 8, cx - 16, cy + 2, SUN, 1.8)
    return s


def res_v(x, y0, y1, color=INK):
    """Резистор-зиґзаґ вертикальний між y0 і y1."""
    n = 6
    seg = (y1 - y0) / n
    s = line(x, y0, x, y0 + seg * 0.5, color, 2)
    yy = y0 + seg * 0.5
    sgn = 1
    pts = [(x, yy)]
    for i in range(n):
        pts.append((x + sgn * 7, yy + seg * 0.5))
        yy += seg
        sgn = -sgn
    pts.append((x, y1 - seg * 0.0))
    s += _poly(pts, color, 2)
    return s


# =====================================================================
# Рис. 2.11.5c.1 — анатомія модуля детектора нуля
# =====================================================================

def fig_anatomy():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 26, "Модуль детектора нуля: дві землі, розв'язані оптопарою", 16, INK, "middle", "bold")

    # --- лінія розділу ізоляції ---
    xiso = 388
    s += line(xiso, 56, xiso, H - 40, GREY, 1.6, "7 5")
    s += text(xiso, H - 22, "бар'єр ізоляції 5300 В", 12, GREY, "middle", "italic")

    # === ЛІВИЙ (мережевий) бік ===
    s += rect(40, 60, 320, 360, LRED, "#e6b3b0", 1.4, 10)
    s += text(56, 82, "Мережевий бік (НЕБЕЗПЕЧНО)", 13, RED, "start", "bold")

    # клеми L / N
    Lx, Ly = 78, 130
    Nx, Ny = 78, 360
    s += dot(Lx, Ly, 4, INK)
    s += dot(Nx, Ny, 4, INK)
    s += text(64, Ly + 5, "L", 14, INK, "end", "bold")
    s += text(64, Ny + 5, "N", 14, INK, "end", "bold")

    # обмежувальний (баластний) резистор від L — горизонтальний зиґзаґ
    s += line(Lx, Ly, Lx + 70, Ly, INK, 2)
    rx0 = Lx + 70
    pts = [(rx0, Ly)]
    sgn = 1
    for i in range(6):
        pts.append((rx0 + 8 + i * 12, Ly + sgn * 7))
        sgn = -sgn
    pts.append((rx0 + 8 + 6 * 12, Ly))
    s += _poly(pts, INK, 2)
    rx1 = rx0 + 8 + 6 * 12
    s += line(rx1, Ly, 270, Ly, INK, 2)
    s += text(rx0 + 36, Ly - 16, "R_бал ~ 30–47 кОм", 12, INK, "middle", "bold")
    s += text(rx0 + 36, Ly + 30, "(0.5–1 Вт)", 11, GREY, "middle")

    # дві антипаралельні LED між вузлом 270,Ly та N (270,Ny)
    a_x = 270
    s += line(a_x, Ly, a_x, 200, INK, 2)
    # ліва вітка LED (струм вниз)
    s += led(a_x - 16, 230, ang_down=True, color=RED)
    s += line(a_x - 16, 200, a_x - 16, 214, INK, 2)
    s += line(a_x - 16, 232, a_x - 16, 290, INK, 2)
    # права вітка LED (струм вгору)
    s += led(a_x + 16, 230, ang_down=False, color=RED)
    s += line(a_x + 16, 200, a_x + 16, 214, INK, 2)
    s += line(a_x + 16, 246, a_x + 16, 290, INK, 2)
    # з'єднання верх/низ вітки
    s += line(a_x - 16, 200, a_x + 16, 200, INK, 2)
    s += line(a_x - 16, 290, a_x + 16, 290, INK, 2)
    s += line(a_x, 290, a_x, Ny, INK, 2)
    s += line(a_x, Ny, Nx, Ny, INK, 2)
    s += text(a_x + 40, 232, "дві LED", 12, RED, "start", "bold")
    s += text(a_x + 40, 250, "антипаралельно", 12, RED, "start")
    s += text(a_x + 40, 268, "(будь-яка", 11, GREY, "start")
    s += text(a_x + 40, 283, " півхвиля світить)", 11, GREY, "start")

    # підпис корпусу H11AA1 (перекриває бар'єр)
    s += rect(xiso - 70, 150, 140, 190, "#ffffff", INK, 1.8, 8)
    s += text(xiso, 168, "H11AA1", 14, INK, "middle", "bold")
    s += text(xiso, 184, "6-pin DIP", 11, GREY, "middle")

    # === ПРАВИЙ (логічний) бік ===
    s += rect(416, 60, 304, 360, LGRN, "#bcdcc2", 1.4, 10)
    s += text(432, 82, "Логічний бік (МК, безпечно)", 13, GREEN, "start", "bold")

    # фототранзистор
    tcx, tcy = 470, 235
    s += npn(tcx, tcy)
    s += text(tcx + 6, tcy + 52, "фото-", 11, INK, "middle")
    s += text(tcx + 6, tcy + 66, "транзистор", 11, INK, "middle")

    # VCC шина і підтягувальний резистор до колектора
    vcc_y = 120
    s += line(440, vcc_y, 700, vcc_y, RED, 2)
    s += text(700, vcc_y - 8, "+3.3 В", 13, RED, "end", "bold")
    # R pull-up (підтягувальний) до колектора (tcx+9, tcy-30)
    rpx = tcx + 9
    s += line(rpx, tcy - 30, rpx, 178, INK, 2)
    s += res_v(rpx, 132, 178, INK)
    s += line(rpx, vcc_y, rpx, 132, INK, 2)
    s += text(rpx + 14, 152, "R_pu 10 кОм", 11, INK, "start")

    # вузол виходу = колектор
    outx = tcx + 9
    s += dot(outx, tcy - 30, 3.2, INK)
    s += line(outx, tcy - 30, 640, tcy - 30, GREEN, 2.4)
    s += arrow(640, tcy - 30, 690, tcy - 30, GREEN, 2.4)
    s += text(693, tcy - 26, "GPIO", 13, GREEN, "start", "bold")
    s += text(693, tcy - 11, "(переривання)", 10, GREEN, "start")

    # емітер на землю логіки
    emy = tcy + 30
    gnd_y = 392
    s += line(outx, emy, outx, gnd_y, INK, 2)
    s += line(440, gnd_y, 700, gnd_y, BLUE, 2)
    s += text(700, gnd_y + 16, "GND логіки", 12, BLUE, "end", "bold")

    # маленька примітка про інверсію
    s += text(432, 360, "поки LED світить → транзистор веде → на GPIO «0»", 11, INK, "start")
    s += text(432, 376, "near zero-cross LED гасне → GPIO стрибає в «1»", 11, INK, "start")

    save("fig-r11-5c-1-zc-anatomy.svg", s)


# =====================================================================
# Рис. 2.11.5c.2 — часова діаграма: синус → конд. вікна → імпульси нуля
# =====================================================================

def fig_timing():
    W, H = 760, 440
    s = header(W, H)
    s += text(W / 2, 26, "Один імпульс на КОЖНОМУ переході через нуль (50 Гц → кожні 10 мс)", 15, INK, "middle", "bold")

    ox = 70           # ліва вісь
    wpx = 630         # ширина області побудови
    cycles = 2.0      # показати 2 повні періоди мережі
    # --- три доріжки ---
    # 1) напруга мережі (синус)
    y1 = 110
    amp1 = 56
    s += line(ox, y1, ox + wpx, y1, FAINT, 1.4)  # нульова лінія
    s += text(ox - 10, y1 + 4, "0", 11, GREY, "end")
    s += text(ox - 56, y1 - 40, "U_мережі", 12, INK, "start", "bold")
    pts = []
    for j in range(int(wpx) + 1):
        t = j / wpx
        y = y1 - amp1 * math.sin(2 * math.pi * cycles * t)
        pts.append((ox + j, y))
    s += _poly(pts, RED, 2.4)

    # позначки переходів через нуль (кожні півперіоду)
    zc_t = [k * 0.5 / cycles for k in range(int(2 * cycles) + 1)]  # 0,0.25,0.5,...
    for t in zc_t:
        x = ox + t * wpx
        s += line(x, 60, x, 400, GREY, 1.2, "4 5")
        s += dot(x, y1, 3.4, INK)

    # 2) струм через LED-пару (≈ |синус|, бо світить будь-яка півхвиля)
    y2 = 235
    amp2 = 48
    s += line(ox, y2, ox + wpx, y2, FAINT, 1.4)
    s += text(ox - 56, y2 - 34, "світло LED", 12, GREEN, "start", "bold")
    s += text(ox - 56, y2 - 18, "(|U| над порогом)", 10, GREY, "start")
    pts = []
    for j in range(int(wpx) + 1):
        t = j / wpx
        v = math.sin(2 * math.pi * cycles * t)
        y = y2 - amp2 * abs(v)
        pts.append((ox + j, y))
    s += _poly(pts, GREEN, 2.4)
    # поріг світіння (горизонтальна лінія трохи вище нуля)
    thr = 0.12
    yth = y2 - amp2 * thr
    s += line(ox, yth, ox + wpx, yth, SUN, 1.6, "5 4")
    s += text(ox + wpx + 4, yth + 4, "поріг", 10, SUN, "start")

    # 3) вихід GPIO: «1» у вузькому вікні навколо кожного нуля, інакше «0»
    y3hi = 330
    y3lo = 380
    s += text(ox - 56, y3hi - 16, "GPIO", 12, BLUE, "start", "bold")
    s += text(ox + wpx + 4, y3hi + 4, "1", 11, BLUE, "start", "bold")
    s += text(ox + wpx + 4, y3lo + 4, "0", 11, BLUE, "start", "bold")
    # будуємо прямокутні імпульси: high поблизу кожного zero-cross
    half = 0.018  # піввікно імпульсу (частка повного графіка)
    lvl = []
    N = int(wpx)
    for j in range(N + 1):
        t = j / wpx
        hi = any(abs(t - zt) < half for zt in zc_t)
        lvl.append(hi)
    # намалювати як ламану
    pts = []
    prev = lvl[0]
    yv = y3hi if prev else y3lo
    pts.append((ox, yv))
    for j in range(1, N + 1):
        if lvl[j] != prev:
            x = ox + j
            pts.append((x, yv))
            yv = y3hi if lvl[j] else y3lo
            pts.append((x, yv))
            prev = lvl[j]
    pts.append((ox + wpx, yv))
    s += _poly(pts, BLUE, 2.6)

    # стрілки «це переривання» на кілька імпульсів
    for t in zc_t[1:4]:
        x = ox + t * wpx
        s += arrow(x, 418, x, y3hi + 6, INK, 1.6)
    s += text(ox + zc_t[2] * wpx, 432, "кожен фронт = переривання в МК", 12, INK, "middle", "bold")

    # позначка інтервалу 10 мс між сусідніми нулями
    xa = ox + zc_t[1] * wpx
    xb = ox + zc_t[2] * wpx
    s += arrow(xa + 4, 70, xb - 4, 70, GREY, 1.6)
    s += arrow(xb - 4, 70, xa + 4, 70, GREY, 1.6)
    s += text((xa + xb) / 2, 64, "10 мс (½ періоду 50 Гц)", 11, GREY, "middle", "bold")

    save("fig-r11-5c-2-zc-timing.svg", s)


if __name__ == "__main__":
    fig_anatomy()
    fig_timing()
    print("done")
