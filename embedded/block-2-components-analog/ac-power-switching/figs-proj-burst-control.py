# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для алгоритмічної вставки 2.11.5a
«Burst-керування нагрівачем: цілі півперіоди замість фазового зрізу».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

УНІКАЛЬНІ імена файлів (fig-r11-5a-*), щоб не зачіпати головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи — Рис. 2.11.5a.k.
Допоміжні функції скопійовано з figs.py попередніх розділів (єдиний вигляд).
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
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMBER = "#fdf3e0"
AMBER = "#c9881e"
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


def rect(x, y, w, h, fill="none", stroke=INK, sw=1.5, rx=0):
    r = f' rx="{rx}"' if rx else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{r}/>\n')


def _path(pts, col, wv=2.4, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
            f'fill="{fill}" stroke="{col}" stroke-width="{wv}"{d}/>\n')


def _area(pts, fill, stroke="none", wv=0):
    s = f' stroke="{stroke}" stroke-width="{wv}"' if stroke != "none" else ' stroke="none"'
    return (f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)} Z" '
            f'fill="{fill}"{s}/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 2.11.5a.1 — два способи віддати ~50 % потужності на тій самій синусоїді:
#  ЗВЕРХУ фазовий зріз (кожен півперіод рубаний по куту α — круті фронти, завади);
#  ЗНИЗУ burst (цілі півперіоди пропускаємо/блокуємо — комутація лише в нулі).
# ─────────────────────────────────────────────────────────────────────────────
def fig1_phase_vs_burst():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 28, "Дві дороги до 50 % потужності на тій самій мережі", 16, INK, "middle", "bold")

    ox = 70
    plot_w = 690
    N = 8                      # показуємо 8 півперіодів
    seg = plot_w / N           # ширина одного півперіоду на екрані
    amp = 56

    # допоміжне: одна синусова півхвиля (знак ±) у вікні [x0, x0+seg]
    def halfwave(x0, sign, n=40):
        return [(x0 + seg * i / n, oy - sign * amp * math.sin(math.pi * i / n))
                for i in range(n + 1)]

    # ─── ВЕРХНЯ ПАНЕЛЬ: фазовий зріз ───
    oy = 150
    s += text(ox, oy - amp - 30, "Фазовий зріз (димер): ріжемо КОЖЕН півперіод", 14, RED, "start", "bold")
    s += line(ox, oy, ox + plot_w + 10, oy, INK, 1.4)
    alpha = math.pi / 2.0      # кут запуску 90° → ~50 %
    for k in range(N):
        x0 = ox + k * seg
        sign = 1 if (k % 2 == 0) else -1
        # повна форма пунктиром (що було б)
        s += _path(halfwave(x0, sign), GREY, 1.2, dash="4,3")
        # провідна частина від α до π — суцільна червона
        cond = [(x0 + seg * (alpha + (math.pi - alpha) * i / 30) / math.pi,
                 oy - sign * amp * math.sin(alpha + (math.pi - alpha) * i / 30))
                for i in range(31)]
        s += _path(cond, RED, 2.6)
        # вертикальний стрибок у момент запуску — джерело завад
        xj = x0 + seg * alpha / math.pi
        s += line(xj, oy, xj, oy - sign * amp * math.sin(alpha), RED, 2.6)
    s += text(ox + plot_w + 14, oy + 4, "t", 12, INK, "start", "bold")
    s += text(ox + 4, oy + amp + 24, "вмикання посеред хвилі → круті фронти → радіозавади (EMI)",
              11, RED, "start", "italic")

    # ─── НИЖНЯ ПАНЕЛЬ: burst (пакетне керування) ───
    oy = 350
    s += text(ox, oy - amp - 30, "Burst-керування: пропускаємо ЦІЛІ півперіоди (4 з 8)", 14, GREEN, "start", "bold")
    s += line(ox, oy, ox + plot_w + 10, oy, INK, 1.4)
    # 4 з 8 півперіодів увімкнені (тут — половину часу горить, половину мовчить)
    on_mask = [1, 1, 1, 1, 0, 0, 0, 0]
    for k in range(N):
        x0 = ox + k * seg
        sign = 1 if (k % 2 == 0) else -1
        if on_mask[k]:
            s += _path(halfwave(x0, sign), GREEN, 2.6)
        else:
            # блокований півперіод — лінія по нулю, форма пунктиром
            s += _path(halfwave(x0, sign), FAINT, 1.2, dash="4,3")
            s += line(x0, oy, x0 + seg, oy, BLUE, 2.6)
    s += text(ox + plot_w + 14, oy + 4, "t", 12, INK, "start", "bold")
    # позначка: перемикання тільки в нулі
    for k in [0, 4]:
        xk = ox + k * seg
        s += circle(xk, oy, 4.0, AMBER, INK, 1.4)
    s += text(ox + 4, oy + amp + 24, "вмикання/вимикання ЛИШЕ в нулі (○) → фронтів нема → тихо",
              11, GREEN, "start", "italic")

    # легенда нулів
    s += circle(ox + 470, oy + amp + 20, 4.0, AMBER, INK, 1.4)
    s += text(ox + 480, oy + amp + 24, "перехід через нуль", 11, AMBER, "start")

    save("fig-r11-5a-1-phase-vs-burst.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 2.11.5a.2 — як burst задає СЕРЕДНЮ потужність: вікно з M півперіодів,
#  у ньому N увімкнено → P ≈ N/M. Показуємо три рівні (1/8, 4/8, 6/8) і
#  «теплову» лінію — інерція нагрівача згладжує пакети у рівну температуру.
# ─────────────────────────────────────────────────────────────────────────────
def fig2_duty_and_thermal():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 28, "Середня потужність = частка ввімкнених півперіодів N/M", 15, INK, "middle", "bold")

    ox = 70
    plot_w = 690
    M = 8
    seg = plot_w / M
    bar_h = 34

    rows = [
        (95,  [1, 0, 0, 0, 0, 0, 0, 0], "P ≈ 1/8 = 12.5 %"),
        (175, [1, 1, 1, 1, 0, 0, 0, 0], "P ≈ 4/8 = 50 %"),
        (255, [1, 1, 1, 0, 1, 1, 0, 1], "P ≈ 6/8 = 75 % (рівномірно розкидано)"),
    ]
    s += text(ox, 70, "Вікно керування M = 8 півперіодів (≈ 80 мс у мережі 50 Гц):",
              12, GREY, "start", "italic")

    for (oy, mask, label) in rows:
        # рамка вікна
        s += rect(ox, oy, plot_w, bar_h, "none", GREY, 1.2)
        n_on = sum(mask)
        for k in range(M):
            x0 = ox + k * seg
            if mask[k]:
                s += rect(x0 + 2, oy + 2, seg - 4, bar_h - 4, LRED, RED, 1.4)
                s += text(x0 + seg / 2, oy + bar_h / 2 + 4, "½", 11, RED, "middle", "bold")
            else:
                s += rect(x0 + 2, oy + 2, seg - 4, bar_h - 4, "#f7f7f7", FAINT, 1.0)
            # роздільники
            if k:
                s += line(x0, oy, x0, oy + bar_h, FAINT, 0.8)
        s += text(ox + plot_w + 12, oy + bar_h / 2 + 5, label, 12, INK, "start", "bold")
        s += text(ox - 12, oy + bar_h / 2 + 5, f"{n_on}/8", 12, GREY, "end", "bold")

    # ─── теплова лінія: інерція згладжує ───
    oy = 360
    s += text(ox, oy - 24, "Температура нагрівача (інерція згладжує пакети):", 13, GREEN, "start", "bold")
    s += line(ox, oy + 38, ox + plot_w + 10, oy + 38, INK, 1.2)   # вісь часу
    # «миттєва» потужність (пакети 50 %) — сіра пилка
    saw = []
    base = oy + 38
    for k in range(M):
        x0 = ox + k * seg
        lvl = base - (26 if (k < 4) else 2)
        saw += [(x0, lvl), (x0 + seg, lvl)]
    s += _path(saw, GREY, 1.4, dash="5,3")
    # температура — згладжена крива, що тримається близько до середнього (≈50 %)
    avg = base - 14
    temp = []
    for i in range(0, M * 10 + 1):
        x = ox + plot_w * i / (M * 10)
        # легке гойдання навколо середнього, мала амплітуда (інерція!)
        wobble = 3.0 * math.sin(2 * math.pi * i / (M * 10) - 0.6)
        temp.append((x, avg + wobble))
    s += _path(temp, GREEN, 3.0)
    s += text(ox + plot_w + 14, oy + 42, "t", 12, INK, "start", "bold")
    s += text(ox + 6, base - 30, "пакет половину часу гріє,", 11, GREY, "start", "italic")
    s += text(ox + 6, base - 16, "половину мовчить (пилка)", 11, GREY, "start", "italic")
    s += text(ox + 420, avg - 8, "температура ≈ рівна", 11, GREEN, "start", "bold")

    save("fig-r11-5a-2-duty-thermal.svg", s)


if __name__ == "__main__":
    fig1_phase_vs_burst()
    fig2_duty_and_thermal()
    print("done")
