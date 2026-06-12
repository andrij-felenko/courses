# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для 🧮-вставки «Математика yield» (до §3.10.5, Модуль 3).
Окремий скрипт вставки (головний figs.py розділу не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/. Імена файлів — з токеном "r10-s5m", щоб не конфліктувати з фігурами теми.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif; єдиний вигляд з рештою розділів.
Нумерація підписів у тексті — Рис. 3.10.5m.k (на диску імена не перенумеровуються).
Хелпери — копія зі спільного набору розділу (за §9 кожен скрипт самодостатній).
"""
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


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


def mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.5m.1 — крива yield за моделлю Пуассона: Y = exp(−A·D).
# По осі X — площа кристала A (см²) при фіксованій густині дефектів D;
# крива стрімко падає. Позначено три кристали (малий/середній/великий)
# і «правило e»: на площі 1/D yield = 1/e ≈ 37 %.
# ═══════════════════════════════════════════════════════════════════════════
def fig_curve():
    W, H = 920, 560
    s = header(W, H)
    s += text(W / 2, 34, "Чому великий кристал непропорційно дорогий: yield = exp(−A · D)",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама густина дефектів D; що ширша площа A, то менший шанс жодного дефекту — спад експоненційний",
              12.5, GREY, "middle", style="italic")

    # ── осі ──
    ax, ay = 92, 96
    aw, ah = 540, 372
    s += line(ax, ay, ax, ay + ah, GREY, 1.6)
    s += line(ax, ay + ah, ax + aw, ay + ah, GREY, 1.6)
    s += text(ax - 70, ay + ah / 2, "вихід Y", 13, INK, "start", "bold")
    s += text(ax - 70, ay + ah / 2 + 16, "(частка", 11, GREY, "start")
    s += text(ax - 70, ay + ah / 2 + 30, "придатних)", 11, GREY, "start")
    s += text(ax + aw / 2, ay + ah + 54, "площа кристала A, см²  (густина дефектів D = 0.5 деф./см² — фіксована)",
              12.5, INK, "middle")

    D = 0.5          # деф./см²
    a_max = 8.0      # см²
    # сітка Y (0..100 %)
    for p in range(0, 101, 20):
        yg = ay + ah * (1 - p / 100.0)
        s += line(ax - 5, yg, ax + aw, yg, FAINT, 1.0)
        s += text(ax - 10, yg + 4, f"{p}%", 11.5, GREY, "end")
    # сітка A
    for a in range(0, int(a_max) + 1, 1):
        xg = ax + aw * a / a_max
        s += line(xg, ay + ah, xg, ay + ah + 5, GREY, 1.2)
        s += text(xg, ay + ah + 20, f"{a}", 11, GREY, "middle")

    # крива Y = exp(−A·D)
    pts = []
    a = 0.0
    while a <= a_max + 1e-6:
        y = math.exp(-a * D)
        xg = ax + aw * a / a_max
        yg = ay + ah * (1 - y)
        pts.append((xg, yg))
        a += a_max / 240.0
    s += polyline(pts, BLUE, 3.0)

    # «правило e»: при A = 1/D yield = 1/e
    a_e = 1.0 / D                       # = 2 см²
    xg_e = ax + aw * a_e / a_max
    yg_e = ay + ah * (1 - math.exp(-1))
    s += line(xg_e, ay + ah, xg_e, yg_e, AMBER, 1.6, "4 3")
    s += line(ax, yg_e, xg_e, yg_e, AMBER, 1.6, "4 3")
    s += circle(xg_e, yg_e, 5, AMBER, AMBER, 0)
    s += text(xg_e + 8, yg_e - 8, "A = 1/D → Y = 1/e ≈ 37 %", 12, AMBER, "start", "bold")
    s += text(xg_e + 8, yg_e + 10, "(орієнтир «однієї помилки на кристал»)", 10.5, GREY, "start")

    # три приклади-кристали на кривій
    examples = [
        (0.5, GREEN, "малий", "ядро МК"),
        (2.0, AMBER, "середній", ""),
        (6.0, RED, "великий", "топ-GPU"),
    ]
    for a_v, col, lab, who in examples:
        if a_v == a_e:
            continue
        y = math.exp(-a_v * D)
        xg = ax + aw * a_v / a_max
        yg = ay + ah * (1 - y)
        s += circle(xg, yg, 5.5, col, col, 0)
        s += text(xg + 8, yg + 4, f"{lab}: A={a_v:g} см² → {y * 100:.0f}%",
                  11.5, col, "start", "bold")
        if who:
            s += text(xg + 8, yg + 18, who, 10, GREY, "start")

    # ── права колонка: розклад «у 4 рази більший кристал» ──
    rx = ax + aw + 36
    s += rect(rx, ay - 4, W - rx - 28, 196, "#f7f9fc", BLUE, 1.4, 10)
    s += text(rx + 14, ay + 20, "Непропорційність наочно", 13.5, INK, "start", "bold")
    rows = [
        ("A = 0.5 см²", "Y = e^(−0.25)", "≈ 78 %", GREEN),
        ("A = 2 см²", "Y = e^(−1.0)", "≈ 37 %", AMBER),
        ("A = 6 см²", "Y = e^(−3.0)", "≈ 5 %", RED),
    ]
    yy = ay + 44
    for a_lbl, expr, val, col in rows:
        s += circle(rx + 22, yy - 4, 5, col, col, 0)
        s += mono(rx + 36, yy, a_lbl, 11.5, INK, "start", "bold")
        yy += 16
        s += mono(rx + 36, yy, expr, 11, GREY, "start")
        s += text(rx + (W - rx - 28) - 14, yy, val, 12.5, col, "end", "bold")
        yy += 22
    s += line(rx + 14, yy - 4, rx + (W - rx - 28) - 14, yy - 4, FAINT, 1.2)
    s += text(rx + 14, yy + 14, "Площа ×12 — а вихід падає", 11, INK, "start")
    s += text(rx + 14, yy + 30, "з 78 % до 5 %: годних кристалів", 11, INK, "start")
    s += text(rx + 14, yy + 46, "із пластини в 15 разів менше.", 11, RED, "start", "bold")

    # підсумкова стрічка
    s += rect(ax, H - 30, aw, 22, "#eef3fb", BLUE, 0, 6)
    s += text(ax + aw / 2, H - 15,
              "Подвоїти площу — це НЕ «вдвічі дорожче»: експонента карає велике сильніше, ніж лінійно.",
              11.5, INK, "middle")
    save("fig-r10-s5m-1-curve.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.5m.2 — геометрична інтуїція: одна й та сама розсипка дефектів
# на пластині. Ліворуч — велика сітка (мало кристалів, кожен дефект убиває
# великий шмат); праворуч — дрібна сітка (ті самі дефекти псують лише крихітні
# квадрати). Підрахунок придатних показує, чому дрібнити вигідно.
# ═══════════════════════════════════════════════════════════════════════════
def fig_wafer():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 34, "Ті самі дефекти, інший розмір кристала: чому дрібнити рятує пластину",
              19, INK, "middle", "bold")
    s += text(W / 2, 56, "однакова розсипка дефектів (× — частинка пилу); кристал з дефектом — брак. Дрібний кристал втрачає менше площі на кожен дефект",
              11.8, GREY, "middle", style="italic")

    # спільна розсипка дефектів у координатах [0..1]×[0..1]
    defects = [
        (0.18, 0.22), (0.62, 0.14), (0.83, 0.41), (0.30, 0.55),
        (0.55, 0.66), (0.74, 0.78), (0.12, 0.80), (0.45, 0.34),
        (0.90, 0.70), (0.38, 0.88),
    ]
    R = 220          # радіус «пластини» в пікселях
    cyl = 300
    centers = [(245, cyl), (685, cyl)]

    def draw_wafer(cx, cy, ncells, title, col):
        ss = ""
        # коло-пластина з пласким зрізом (flat) знизу
        ss += circle(cx, cy, R, "#fbfbfb", GREY, 1.8)
        flat_y = cy + R * 0.88
        ss += line(cx - R * 0.46, flat_y, cx + R * 0.46, flat_y, GREY, 1.8)
        ss += text(cx, cy - R - 14, title, 14.5, INK, "middle", "bold")
        # сітка кристалів; квадрат належить пластині, якщо його центр у колі
        n = ncells
        cell = (2.0 * R) / n
        good = 0
        total = 0
        for i in range(n):
            for j in range(n):
                # лівий-верхній кут квадрата в пікселях
                px = cx - R + i * cell
                py = cy - R + j * cell
                ccx = px + cell / 2
                ccy = py + cell / 2
                # у межах пластини? (коло + відрізаний flat)
                if (ccx - cx) ** 2 + (ccy - cy) ** 2 > (R - cell * 0.18) ** 2:
                    continue
                if ccy > flat_y - cell * 0.2:
                    continue
                total += 1
                # чи є дефект усередині цього квадрата?
                has_def = False
                for dx, dy in defects:
                    fx = cx - R + dx * 2 * R
                    fy = cy - R + dy * 2 * R
                    if px <= fx < px + cell and py <= fy < py + cell:
                        has_def = True
                        break
                fill = "#fdecec" if has_def else "#eef6ef"
                stroke = RED if has_def else GREEN
                ss += rect(px + 1.2, py + 1.2, cell - 2.4, cell - 2.4, fill, stroke, 1.3, 2)
                if not has_def:
                    good += 1
        # дефекти поверх сітки — однакові для обох пластин
        for dx, dy in defects:
            fx = cx - R + dx * 2 * R
            fy = cy - R + dy * 2 * R
            if (fx - cx) ** 2 + (fy - cy) ** 2 > (R - 4) ** 2 or fy > flat_y:
                continue
            ss += text(fx, fy + 5, "×", 17, RED, "middle", "bold")
        # підсумок під пластиною
        y0 = cy + R + 20
        yld = (good / total * 100.0) if total else 0
        ss += rect(cx - 150, y0, 300, 46, "#ffffff", col, 1.6, 8)
        ss += text(cx, y0 + 19, f"{good} придатних з {total} кристалів", 13, INK, "middle", "bold")
        ss += text(cx, y0 + 37, f"вихід ≈ {yld:.0f} %", 12.5, col, "middle", "bold")
        return ss, good, total

    s_left, g1, t1 = draw_wafer(centers[0][0], centers[0][1], 4, "Великі кристали (4×4)", RED)
    s_right, g2, t2 = draw_wafer(centers[1][0], centers[1][1], 8, "Дрібні кристали (8×8)", GREEN)
    s += s_left + s_right

    # стрілка-перехід між пластинами
    s += arrow(475, cyl, 520, cyl, INK, 2.2)
    s += text(497, cyl - 12, "дрібнимо", 11.5, INK, "middle", "bold")
    s += text(497, cyl + 22, "той самий", 10.5, GREY, "middle")
    s += text(497, cyl + 36, "пил", 10.5, GREY, "middle")

    save("fig-r10-s5m-2-wafer.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.5m.3 — моноліт проти чиплетів: один великий кристал площі A
# проти N малих по A/N (плюс реальна ціна — інтерконект). Числовий розрахунок
# yield для обох і «робочих систем із пластини».
# ═══════════════════════════════════════════════════════════════════════════
def fig_chiplets():
    W, H = 920, 560
    s = header(W, H)
    s += text(W / 2, 34, "Чому чиплети рятують: один великий кристал vs чотири малі тієї ж сумарної площі",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама логіка, та сама густина дефектів D = 0.5/см² — але вихід кардинально різний",
              12.5, GREY, "middle", style="italic")

    D = 0.5
    A = 4.0          # см² сумарної логіки
    N = 4
    a_small = A / N  # 1 см²
    y_mono = math.exp(-A * D)            # ≈ 13.5 %
    y_chip = math.exp(-a_small * D)      # ≈ 60.7 % за один чиплет

    # ── лівий блок: моноліт ──
    lx, ly = 70, 96
    s += rect(lx, ly, 360, 250, "#fdf6f5", RED, 1.6, 12)
    s += text(lx + 180, ly + 26, "Моноліт: один кристал A = 4 см²", 14, INK, "middle", "bold")
    # квадрат-кристал із кількома дефектами
    qx, qy, qs = lx + 110, ly + 50, 140
    s += rect(qx, qy, qs, qs, "#fdecec", RED, 2.0, 6)
    for dx, dy in [(0.3, 0.35), (0.7, 0.55), (0.5, 0.8)]:
        s += text(qx + dx * qs, qy + dy * qs + 5, "×", 18, RED, "middle", "bold")
    s += text(qx + qs / 2, qy + qs + 22, "будь-який × → весь кристал у брак", 11, RED, "middle")
    s += mono(lx + 24, ly + 232, "Y = e^(−4·0.5) = e^(−2) ≈ 13.5 %", 13, INK, "start", "bold")

    # ── правий блок: чиплети ──
    rx0, ry = 490, 96
    s += rect(rx0, ry, 360, 250, "#f1f8f3", GREEN, 1.6, 12)
    s += text(rx0 + 180, ry + 26, "Чиплети: 4 кристали по 1 см²", 14, INK, "middle", "bold")
    # 2×2 дрібні квадрати; той самий пил, але псує лише свій квадрат
    gx, gy, gs, gap = rx0 + 96, ry + 48, 72, 14
    def_local = {(0, 0): True, (1, 0): False, (0, 1): False, (1, 1): True}
    for (ci, cj), bad in def_local.items():
        px = gx + ci * (gs + gap)
        py = gy + cj * (gs + gap)
        fill = "#fdecec" if bad else "#eef6ef"
        col = RED if bad else GREEN
        s += rect(px, py, gs, gs, fill, col, 1.8, 5)
        if bad:
            s += text(px + gs / 2, py + gs / 2 + 6, "×", 17, RED, "middle", "bold")
        else:
            s += text(px + gs / 2, py + gs / 2 + 5, "OK", 12, GREEN, "middle", "bold")
    s += text(rx0 + 180, gy + 2 * gs + gap + 18, "брак — лише дефектний квадратик, решта годні", 10.5, GREEN, "middle")
    s += mono(rx0 + 24, ry + 232, "Y₁ = e^(−1·0.5) ≈ 60.7 % на кожен чиплет", 12.5, INK, "start", "bold")

    # стрілка
    s += arrow(438, ly + 150, 484, ly + 150, INK, 2.2)
    s += text(461, ly + 138, "ділимо", 11, INK, "middle", "bold")

    # ── нижній блок: підрахунок «годних із пластини» ──
    by = 372
    s += rect(70, by, W - 140, 116, "#fbfbfb", FAINT, 1.4, 10)
    s += text(90, by + 24, "Що це дає на пластині (грубий підрахунок придатних кристалів)",
              13.5, INK, "start", "bold")
    s += mono(90, by + 50,
              "моноліт : зі 100 заготовок A=4 см²  годних ≈ 14  →  кожен 7-й виживає",
              12.5, INK, "start")
    s += mono(90, by + 74,
              "чиплети : зі 100 заготовок 1 см² годних ≈ 61  →  з них збираємо ≈ 15 систем по 4",
              12.5, INK, "start")
    s += text(90, by + 100,
              "Та сама логіка дає РАЗИ більше робочих систем — ось чому великі чипи ріжуть на чиплети.",
              12, GREEN, "start", "bold")
    s += text(W - 90, by + 100, "ціна — інтерконект між кристалами", 11, AMBER, "end", style="italic")

    # застереження-стрічка
    s += rect(70, H - 30, W - 140, 22, "#fdf9ef", AMBER, 0, 6)
    s += text(W / 2, H - 15,
              "Дрібнити не безкоштовно: між чиплетами потрібен щільний міжз'єднувач (корпус-підкладка/міст), і це теж площа й затримка.",
              11.2, INK, "middle")
    save("fig-r10-s5m-3-chiplets.svg", s)


if __name__ == "__main__":
    fig_curve()
    fig_wafer()
    fig_chiplets()
    print("r10-s5-m yield-math figures done.")
