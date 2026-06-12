# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для алгоритмічної вставки 2.11.4a
«Алгоритм димера: від імпульсу нуля до затримки запуску в межах 10 мс півперіоду».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

УНІКАЛЬНІ імена файлів (fig-r11-4a-*), щоб не зачіпати ані головний figs.py розділу,
ані сусідню вставку (fig-r11-4m-*).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи — Рис. 2.11.4a.k.
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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey", AMBER: "aAmber"}


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
#  Рис. 2.11.4a.1 — хронограма одного півперіоду: імпульс детектора нуля
#  запускає таймер на затримку d, по його спрацюванню — короткий імпульс на
#  затвор; симістор защіпається й проводить до наступного нуля. Три доріжки:
#  мережа (синусоїда), zero-cross (логічні імпульси), затвор (gate pulse).
# ─────────────────────────────────────────────────────────────────────────────
def fig1_timeline():
    W, H = 800, 470
    s = header(W, H)
    s += text(W / 2, 28, "Один півперіод: від імпульсу нуля до запуску симістора", 16, INK, "middle", "bold")

    ox = 120
    plot_w = 600           # дві півхвилі по 300 px = 2 × 10 мс
    half = plot_w / 2.0    # 10 мс
    # три доріжки (зверху вниз)
    y_ac = 120             # вісь мережі
    amp = 56
    y_zc = 250             # доріжка zero-cross (логіка)
    y_gt = 360             # доріжка затвора (логіка)
    logic_h = 40

    def X(ms):             # ms у діапазоні 0..20
        return ox + plot_w * ms / 20.0

    # підписи доріжок зліва
    s += text(ox - 108, y_ac + 4, "мережа", 13, INK, "start", "bold")
    s += text(ox - 108, y_ac + 20, "v(t)", 11, GREY, "start")
    s += text(ox - 108, y_zc + 4, "zero-cross", 13, GREEN, "start", "bold")
    s += text(ox - 108, y_zc + 20, "(IRQ)", 11, GREY, "start")
    s += text(ox - 108, y_gt + 4, "затвор", 13, RED, "start", "bold")
    s += text(ox - 108, y_gt + 20, "GATE", 11, GREY, "start")

    # ---- доріжка мережі: дві півхвилі (sin), нуль кожні 10 мс ----
    s += line(ox, y_ac, ox + plot_w + 30, y_ac, INK, 1.4)
    full = [(X(t), y_ac - amp * math.sin(math.pi * t / 10.0)) for t in [i * 20.0 / 200 for i in range(201)]]
    s += _path(full, GREY, 1.8)
    s += arrow(ox, y_ac, ox, y_ac - amp - 22, INK, 1.4)
    # вертикалі нулів
    for ms in (0, 10, 20):
        s += line(X(ms), y_ac + amp + 6, X(ms), y_gt + logic_h + 8, FAINT, 1.4, dash="3,3")
    s += text(X(0), y_ac + amp + 24, "0 мс", 11, INK, "middle")
    s += text(X(10), y_ac + amp + 24, "10 мс", 11, INK, "middle")
    s += text(X(20), y_ac + amp + 24, "20 мс", 11, INK, "middle")
    s += text(X(5), y_ac - amp - 6, "+ півхвиля", 11, RED, "middle")
    s += text(X(15), y_ac + amp + 24, "− півхвиля", 11, BLUE, "middle")

    # ---- доріжка zero-cross: короткі імпульси на 0, 10, 20 мс ----
    s += line(ox, y_zc, ox + plot_w + 30, y_zc, FAINT, 1.4)
    pw = 10  # ширина імпульсу в пікселях
    for ms in (0, 10, 20):
        x = X(ms)
        s += _path([(x - pw / 2, y_zc), (x - pw / 2, y_zc - logic_h),
                    (x + pw / 2, y_zc - logic_h), (x + pw / 2, y_zc)], GREEN, 2.6)
    s += text(X(0) + 14, y_zc - logic_h + 12, "IRQ: старт таймера", 11, GREEN, "start", "bold")

    # ---- доріжка затвора: затримка d, потім імпульс, далі провідність ----
    s += line(ox, y_gt, ox + plot_w + 30, y_gt, FAINT, 1.4)
    d_ms = 3.7   # затримка запуску в першій півхвилі
    # стрілка-затримка від нуля до запуску (на рівні мережі)
    s += line(X(0), y_ac + amp + 40, X(0), y_gt - logic_h - 8, AMBER, 1.6, dash="4,3")
    s += line(X(d_ms), y_ac + amp + 40, X(d_ms), y_gt - logic_h - 8, AMBER, 1.6, dash="4,3")
    s += arrow(X(0), y_gt - logic_h - 18, X(d_ms), y_gt - logic_h - 18, AMBER, 2.0)
    s += arrow(X(d_ms), y_gt - logic_h - 18, X(0), y_gt - logic_h - 18, AMBER, 2.0)
    s += text(X(d_ms / 2), y_gt - logic_h - 26, "затримка d", 12, AMBER, "middle", "bold")

    # імпульс на затворі у момент d (короткий)
    gpw = 9
    for base in (0.0, 10.0):
        x = X(base + d_ms)
        s += _path([(x - gpw / 2, y_gt), (x - gpw / 2, y_gt - logic_h),
                    (x + gpw / 2, y_gt - logic_h), (x + gpw / 2, y_gt)], RED, 2.6)
    s += text(X(d_ms) + 12, y_gt - logic_h + 12, "імпульс ~100 мкс", 11, RED, "start", "bold")

    # провідна ділянка симістора [d, наступний нуль] — підсвітити на мережі
    for base in (0.0, 10.0):
        seg = [(X(base + d_ms), y_ac)]
        seg += [(X(t), y_ac - amp * math.sin(math.pi * t / 10.0))
                for t in [base + d_ms + (10.0 - d_ms) * i / 60 for i in range(61)]]
        seg += [(X(base + 10.0), y_ac)]
        col = LRED
        s += _area(seg, col)
    # перемалювати провідну криву поверх заливки яскраво
    for base in (0.0, 10.0):
        seg = [(X(t), y_ac - amp * math.sin(math.pi * t / 10.0))
               for t in [base + d_ms + (10.0 - d_ms) * i / 60 for i in range(61)]]
        s += _path(seg, RED, 2.8)
    s += text(X(7.0), y_ac - 6, "симістор проводить", 11, RED, "middle", "bold")
    s += text(X(7.0), y_ac + 10, "(защіпнувся сам)", 10, GREY, "middle")

    # підпис: кожен півперіод однаковий
    s += text(ox + plot_w / 2, H - 14, "Кожен півперіод однаковий: новий нуль → новий відлік → новий запуск", 12, GREY, "middle", style="italic")

    save("fig-r11-4a-1-timeline.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 2.11.4a.2 — чому затримку НЕ можна мапити лінійно: лінійна шкала
#  яскравості → нелінійна затримка. Зліва крива P(α), праворуч — як рівні
#  кроки яскравості розкладаються по нерівномірних кутах/затримках.
# ─────────────────────────────────────────────────────────────────────────────
def frac(alpha):
    # P(α)/P_full = 1 − α/π + sin(2α)/(2π)   (резистивне навантаження)
    return 1.0 - alpha / math.pi + math.sin(2 * alpha) / (2 * math.pi)


def alpha_for_frac(target):
    # обернути монотонну frac() бісекцією: знайти α∈[0,π], де frac(α)=target
    lo, hi = 0.0, math.pi
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if frac(mid) > target:   # frac спадає з ростом α
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def fig2_mapping():
    W, H = 800, 470
    s = header(W, H)
    s += text(W / 2, 28, "Чому затримку не мапимо лінійно: рівні кроки яскравості → нерівні затримки", 15, INK, "middle", "bold")

    # ЛІВА панель: крива «затримка d (мс) → яскравість P/Pповна»
    ox, oy = 90, 400
    pw, ph = 300, 320

    def X(ms):                 # 0..10 мс
        return ox + pw * ms / 10.0

    def Y(f):                  # 0..1
        return oy - ph * f

    # сітка
    for p in range(0, 101, 25):
        y = Y(p / 100.0)
        s += line(ox, y, ox + pw, y, FAINT, 1.1)
        s += text(ox - 8, y + 4, f"{p}%", 11, GREY, "end")
    for ms in range(0, 11, 2):
        x = X(ms)
        s += line(x, oy, x, Y(1.0), FAINT, 1.1)
        s += text(x, oy + 20, f"{ms}", 11, GREY, "middle")
    s += arrow(ox, oy, ox, Y(1.0) - 16, INK, 1.6)
    s += arrow(ox, oy, ox + pw + 16, oy, INK, 1.6)
    s += text(ox - 50, Y(0.5) - 70, "яскравість", 12, INK, "start", "bold")
    s += text(ox - 50, Y(0.5) - 54, "P / Pповна", 11, GREY, "start")
    s += text(ox + pw + 18, oy + 4, "затримка d, мс", 11, INK, "start", "bold")

    # крива: яскравість як функція затримки d (d=10мс·α/π)
    pts = []
    for i in range(0, 201):
        d = 10.0 * i / 200.0
        a = math.pi * d / 10.0
        pts.append((X(d), Y(frac(a))))
    s += _path(pts, RED, 3.0)

    # рівні кроки яскравості (25%) → точки на кривій → проєкція на вісь d
    for f in (0.25, 0.5, 0.75):
        a = alpha_for_frac(f)
        d = 10.0 * a / math.pi
        x, y = X(d), Y(f)
        s += line(ox, y, x, y, BLUE, 1.3, dash="4,3")          # горизонталь рівня
        s += line(x, y, x, oy, AMBER, 1.6, dash="4,3")         # вниз на вісь d
        s += circle(x, y, 4.0, RED, INK, 1.5)
        s += text(x, oy + 36, f"{d:.1f}", 10, AMBER, "middle", "bold")
    s += text(ox + pw / 2, oy + 52, "рівні 25% → нерівні мс", 11, AMBER, "middle", style="italic")

    # ПРАВА панель: «лінійна ручка» проти потрібної таблиці
    bx = 470
    s += text(bx, 92, "Лінійна ручка користувача", 13, INK, "start", "bold")
    # стовпчик-шкала ручки 0..100 (рівні поділки)
    sx = bx + 6
    sy0, sy1 = 120, 380
    s += line(sx, sy0, sx, sy1, INK, 2)
    for p in range(0, 101, 25):
        yy = sy1 - (sy1 - sy0) * p / 100.0
        s += line(sx - 6, yy, sx + 6, yy, INK, 2)
        s += text(sx - 12, yy + 4, f"{p}", 11, INK, "end")
    s += text(sx, sy1 + 22, "крутимо рівно", 11, GREY, "start", style="italic")

    # стрілка-перетворення
    mx = bx + 150
    s += arrow(sx + 18, (sy0 + sy1) / 2, mx - 8, (sy0 + sy1) / 2, GREEN, 2.4)
    s += text((sx + 18 + mx) / 2, (sy0 + sy1) / 2 - 12, "таблиця", 11, GREEN, "middle", "bold")
    s += text((sx + 18 + mx) / 2, (sy0 + sy1) / 2 + 16, "LUT d[·]", 11, GREEN, "middle")

    # стовпчик-затримка (нерівні поділки за alpha_for_frac)
    dx = mx + 20
    s += line(dx, sy0, dx, sy1, AMBER, 2)
    s += text(dx + 10, 110, "затримка d", 12, AMBER, "start", "bold")
    s += text(dx + 10, 126, "0…10 мс", 11, GREY, "start")
    for p in range(0, 101, 25):
        f = p / 100.0
        if p == 0:
            d = 10.0           # 0% яскравості → майже повна затримка
        elif p == 100:
            d = 0.0            # 100% → запуск одразу
        else:
            d = 10.0 * alpha_for_frac(f) / math.pi
        yy = sy0 + (sy1 - sy0) * d / 10.0   # 0 мс зверху, 10 мс знизу
        s += line(dx - 6, yy, dx + 6, yy, AMBER, 2)
        s += text(dx + 12, yy + 4, f"{d:.1f} мс", 10, AMBER, "start")
    s += text(dx, sy1 + 22, "лягають нерівно", 11, GREY, "start", style="italic")

    save("fig-r11-4a-2-mapping.svg", s)


if __name__ == "__main__":
    fig1_timeline()
    fig2_mapping()
    print("done")
