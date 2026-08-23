# -*- coding: utf-8 -*-
"""Фігури вставки math-jps-symmetry.md (симетрія шляхів і JPS). Чистий Python + svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
def out(name): return os.path.join(IMG, name)

OCC = "#c9ced6"    # зайнята клітина (перешкода) — як у figs.py
OCCED = "#8a94a6"
BLUE = "#2457d6"
ORANGE = "#e08a1e"


def draw_grid(ox, oy, cols, rows, cell, occ=None):
    """Порожня сітка cols×rows у лівому-верхньому куті (ox,oy). occ: set (r,c) стін."""
    occ = occ or set()
    f = []
    for r in range(rows):
        for c in range(cols):
            fill = OCC if (r, c) in occ else "#ffffff"
            f.append(rect(ox + c * cell, oy + r * cell, cell, cell,
                          fill=fill, stroke="#d0d6de", sw=1, rx=0))
    return f

def cc(ox, oy, cell, r, c):
    """Центр клітини (r,c)."""
    return ox + c * cell + cell / 2, oy + r * cell + cell / 2

def marker(ox, oy, cell, r, c, label, col):
    x, y = cc(ox, oy, cell, r, c)
    tint = {NEG: "#eaf0fd", FIELD: "#eafaf1", POS: "#fdecea", INK: "#eef0f3"}.get(col, "#eef0f3")
    return [circle(x, y, cell * 0.30, fill=tint, stroke=col, sw=2),
            text(x, y + cell * 0.14, label, size=int(cell * 0.34), color=col, bold=True)]


# ── 1) jps-symmetry.svg — три симетричні найкоротші маршрути ─────────────────
def fig_symmetry():
    W, H = 760, 430
    frags = [text(W / 2, 30, "Симетрія шляхів: три однаково короткі маршрути A→B", size=17, bold=True)]

    cols, rows, cell = 5, 4, 74
    ox = (W - cols * cell) / 2
    oy = 60
    frags += draw_grid(ox, oy, cols, rows, cell)

    # A внизу ліворуч (r=3,c=0), B угорі праворуч (r=1,c=3): три праворуч, дві вгору? -> зробимо 3 праворуч, 1 вгору
    # A=(r=2,c=0), B=(r=1,c=3): Δc=+3, Δr=-1 (один угору). Один діагональний "↗" + два прямі "→".
    Ar, Ac = 2, 0
    Br, Bc = 1, 3

    def seg(path, col, off):
        # path: список (r,c) вузлів; малюємо ламану зі зсувом off (px) перпендикулярно для читабельності
        pts = []
        for (r, c) in path:
            x, y = cc(ox, oy, cell, r, c)
            pts.append((x, y + off))
        out_f = []
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]; x2, y2 = pts[i + 1]
            if i == len(pts) - 2:
                out_f.append(arrow(x1, y1, x2, y2, color=col, sw=3.2))
            else:
                out_f.append(line(x1, y1, x2, y2, color=col, sw=3.2))
        return out_f

    # маршрут 1 (синій): діагональ ПЕРШОЮ ↗, тоді два прямі →→
    p1 = [(2, 0), (1, 1), (1, 2), (1, 3)]
    # маршрут 2 (зелений): прямо →, діагональ ↗, прямо →
    p2 = [(2, 0), (2, 1), (1, 2), (1, 3)]
    # маршрут 3 (помаранч): два прямі →→, діагональ ↗ ОСТАННЬОЮ
    p3 = [(2, 0), (2, 1), (2, 2), (1, 3)]
    frags += seg(p1, BLUE, -9)
    frags += seg(p2, FIELD, 0)
    frags += seg(p3, ORANGE, +9)

    frags += marker(ox, oy, cell, Ar, Ac, "A", NEG)
    frags += marker(ox, oy, cell, Br, Bc, "B", FIELD)

    # легенда
    ly = oy + rows * cell + 26
    frags.append(line(ox + 8, ly, ox + 44, ly, color=BLUE, sw=3.2))
    frags.append(text(ox + 52, ly + 4, "діагональ першою", size=12, color=INK, anchor="start"))
    frags.append(line(ox + 210, ly, ox + 246, ly, color=FIELD, sw=3.2))
    frags.append(text(ox + 254, ly + 4, "діагональ усередині", size=12, color=INK, anchor="start"))
    frags.append(line(ox + 430, ly, ox + 466, ly, color=ORANGE, sw=3.2))
    frags.append(text(ox + 474, ly + 4, "діагональ останньою", size=12, color=INK, anchor="start"))

    frags.append(text(W / 2, H - 16,
                      "усі три = один крок √2 + два кроки по 1, лише в різному порядку → та сама ціна",
                      size=12.5, color=MUTED))
    render(out("jps-symmetry.svg"), W, H, *frags)


# ── 2) jps-prune-straight.svg — відсікання при прямому кроці ─────────────────
def fig_prune_straight():
    W, H = 760, 400
    frags = [text(W / 2, 30, "Прямий крок: природний сусід лише один", size=17, bold=True)]

    cols, rows, cell = 4, 3, 92
    ox = 60
    oy = 66
    frags += draw_grid(ox, oy, cols, rows, cell)

    # p=(1,0), x=(1,1); прийшли праворуч p->x
    pr, pc = 1, 0
    xr, xc = 1, 1
    px, py = cc(ox, oy, cell, pr, pc)
    xx, xy = cc(ox, oy, cell, xr, xc)

    # крок p->x (сірий, вже зроблений)
    frags.append(arrow(px + cell * 0.30, py, xx - cell * 0.30, xy, color=INK, sw=2.6))
    frags.append(text((px + xx) / 2, py - 10, "1", size=13, color=INK, bold=True))

    # природний сусід: прямо праворуч x->(1,2) — зелений
    nx, ny = cc(ox, oy, cell, 1, 2)
    frags.append(arrow(xx + cell * 0.30, xy, nx - cell * 0.30, ny, color=FIELD, sw=3.0))
    frags.append(text((xx + nx) / 2, ny - 10, "природний", size=12, color=FIELD, bold=True))

    # верхній сусід (0,1): відсічений. Обхід p->(0,1) по діагоналі √2 (штрих), прохід через x = 1+1
    ux, uy = cc(ox, oy, cell, 0, 1)
    frags.append(line(px, py, ux, uy, color=MUTED, sw=2.2, dash="6 5"))   # обхід √2
    frags.append(text((px + ux) / 2 - 6, (py + uy) / 2, "√2", size=12, color=MUTED, bold=True, anchor="end"))
    frags.append(line(xx, xy, ux, uy, color=OCCED, sw=2.0, dash="3 4"))   # через x (1)
    # позначка «відсічено» на верхньому
    frags.append(circle(ux, uy, cell * 0.20, fill="#f4f6f8", stroke=OCCED, sw=1.6))
    frags.append(text(ux, uy + 4, "✕", size=15, color=OCCED, bold=True))

    # нижній сусід (2,1): теж відсічений (симетрично) — коротко
    dx, dy = cc(ox, oy, cell, 2, 1)
    frags.append(line(px, py, dx, dy, color=MUTED, sw=2.2, dash="6 5"))
    frags.append(circle(dx, dy, cell * 0.20, fill="#f4f6f8", stroke=OCCED, sw=1.6))
    frags.append(text(dx, dy + 4, "✕", size=15, color=OCCED, bold=True))

    frags += marker(ox, oy, cell, pr, pc, "p", NEG)
    frags += marker(ox, oy, cell, xr, xc, "x", INK)

    # пояснювальна рамка праворуч
    bx = ox + cols * cell + 34
    body, bw, bh = textbox(bx + 150, 150,
                           ["Сусід над x:", "через x:  1 + 1 = 2", "обхід p→верх:  √2 ≈ 1.41", "обхід дешевший → відсікти"],
                           size=13, pad=12)
    frags.append(body)
    frags.append(text(W / 2, H - 16,
                      "у верх/низ дешевше дійти з p по діагоналі (√2), ніж через x (2) → лишається тільки «прямо»",
                      size=12, color=MUTED))
    render(out("jps-prune-straight.svg"), W, H, *frags)


# ── 3) jps-prune-diag.svg — відсікання при діагональному кроці ───────────────
def fig_prune_diag():
    W, H = 760, 420
    frags = [text(W / 2, 30, "Діагональний крок: три природні напрями", size=17, bold=True)]

    cols, rows, cell = 3, 3, 108
    ox = 70
    oy = 70
    frags += draw_grid(ox, oy, cols, rows, cell)

    # p=(2,0) знизу-ліворуч, x=(1,1) центр; прийшли навскіс ↗
    pr, pc = 2, 0
    xr, xc = 1, 1
    px, py = cc(ox, oy, cell, pr, pc)
    xx, xy = cc(ox, oy, cell, xr, xc)

    # крок p->x
    frags.append(arrow(px + cell * 0.26, py - cell * 0.26, xx - cell * 0.26, xy + cell * 0.26, color=INK, sw=2.6))
    # підпис √2 — ОСТОРОНЬ від лінії кроку (перпендикулярно вгору-ліворуч, у порожнє поле), щоб напис не лежав на стрілці
    frags.append(text((px + xx) / 2 - 20, (py + xy) / 2 - 16, "√2", size=13, color=INK, bold=True))

    # три природні напрями (зелені): діагональ ↗ (0,2), прямо вгору (0,1), прямо праворуч (1,2)
    for (r, c), lbl in [((0, 2), "діагональ"), ((0, 1), "вгору"), ((1, 2), "праворуч")]:
        tx, ty = cc(ox, oy, cell, r, c)
        dx = tx - xx; dy = ty - xy
        L = math.hypot(dx, dy)
        frags.append(arrow(xx + dx / L * cell * 0.30, xy + dy / L * cell * 0.30,
                           tx - dx / L * cell * 0.30, ty - dy / L * cell * 0.30, color=FIELD, sw=3.0))

    # відсічені напрями (сірі ✕): назад-ліворуч (1,0), вниз (2,1), задній кут (2,2), верх-лівий кут (0,0)
    for (r, c) in [(1, 0), (2, 1), (2, 2), (0, 0)]:
        tx, ty = cc(ox, oy, cell, r, c)
        dx = tx - xx; dy = ty - xy
        L = math.hypot(dx, dy)
        frags.append(line(xx + dx / L * cell * 0.28, xy + dy / L * cell * 0.28,
                          tx - dx / L * cell * 0.30, ty - dy / L * cell * 0.30,
                          color=OCCED, sw=1.8, dash="4 5"))
        frags.append(circle(tx, ty, cell * 0.17, fill="#f4f6f8", stroke=OCCED, sw=1.5))
        frags.append(text(tx, ty + 4, "✕", size=14, color=OCCED, bold=True))

    frags += marker(ox, oy, cell, pr, pc, "p", NEG)
    frags += marker(ox, oy, cell, xr, xc, "x", INK)

    # легенда праворуч
    bx = ox + cols * cell + 40
    frags.append(line(bx, 120, bx + 34, 120, color=FIELD, sw=3.0))
    frags.append(text(bx + 42, 124, "природний (лишити)", size=13, color=INK, anchor="start"))
    frags.append(line(bx, 156, bx + 34, 156, color=OCCED, sw=2.0, dash="4 5"))
    frags.append(text(bx + 42, 160, "відсічений (викинути)", size=13, color=INK, anchor="start"))
    body, bw, bh = textbox(bx + 128, 240,
                           ["уперед: діагональ ↗", "+ два прямі складники:", "вгору і праворуч", "назад/вбік — зайві"],
                           size=13, pad=12)
    frags.append(body)

    frags.append(text(W / 2, H - 16,
                      "діагональ лишає ТРИ напрями (сама діагональ + вгору + праворуч); усе «назад» відсічено",
                      size=12, color=MUTED))
    render(out("jps-prune-diag.svg"), W, H, *frags)


# ── 4) jps-forced.svg — вимушений сусід біля перешкоди ──────────────────────
def fig_forced():
    W, H = 760, 420
    frags = [text(W / 2, 30, "Вимушений сусід: перешкода робить x стрибковою точкою", size=17, bold=True)]

    cols, rows, cell = 4, 3, 96
    ox = 66
    oy = 66
    # стіна над p: p=(1,0) -> над p = (0,0)
    occ = {(0, 0)}
    frags += draw_grid(ox, oy, cols, rows, cell, occ=occ)

    pr, pc = 1, 0
    xr, xc = 1, 1
    px, py = cc(ox, oy, cell, pr, pc)
    xx, xy = cc(ox, oy, cell, xr, xc)

    # крок p->x
    frags.append(arrow(px + cell * 0.30, py, xx - cell * 0.30, xy, color=INK, sw=2.6))
    frags.append(text((px + xx) / 2, py - 10, "1", size=13, color=INK, bold=True))

    # заблокований обхід p->(0,1): штрих через стіну, перекреслений
    ux, uy = cc(ox, oy, cell, 0, 1)
    wx, wy = cc(ox, oy, cell, 0, 0)   # стіна
    frags.append(line(px, py, ux, uy, color=OCCED, sw=2.0, dash="5 5"))
    # перекреслення обходу (він упирається у стіну зліва-зверху)
    bxm, bym = (px + ux) / 2, (py + uy) / 2
    frags.append(line(bxm - 12, bym - 12, bxm + 12, bym + 12, color=POS, sw=2.6))
    frags.append(line(bxm - 12, bym + 12, bxm + 12, bym - 12, color=POS, sw=2.6))
    frags.append(text(wx, wy + cell * 0.02, "стіна", size=13, color=OCCED, bold=True))

    # вимушений сусід (0,1): єдиний шлях — через x, вгору (жирна зелена)
    frags.append(arrow(xx, xy - cell * 0.30, ux, uy + cell * 0.30, color=FIELD, sw=3.4))
    frags.append(text((xx + ux) / 2 + 30, (xy + uy) / 2, "єдиний", size=12, color=FIELD, bold=True, anchor="start"))

    frags += marker(ox, oy, cell, pr, pc, "p", NEG)
    frags += marker(ox, oy, cell, xr, xc, "x", INK)
    # підсвітити вимушеного сусіда рамкою
    frags.append(rect(ox + 1 * cell + 3, oy + 0 * cell + 3, cell - 6, cell - 6,
                      fill="none", stroke=FIELD, sw=2.4, rx=3))

    # пояснювальна рамка праворуч
    bx = ox + cols * cell + 30
    body, bw, bh = textbox(bx + 150, 170,
                           ["обхід p→(верх) заблоковано стіною", "зрізати кут крізь стіну не можна",
                            "→ у верх лише через x", "x = СТРИБКОВА ТОЧКА"],
                           size=13, pad=12)
    frags.append(body)
    frags.append(text(W / 2, H - 16,
                      "стіна вбиває дешевий обхід → сусід стає вимушеним → x зобов'язана розгалузитися",
                      size=12, color=MUTED))
    render(out("jps-forced.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_symmetry()
    fig_prune_straight()
    fig_prune_diag()
    fig_forced()
    print("OK: jps-symmetry, jps-prune-straight, jps-prune-diag, jps-forced")
