# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

DRIVE = "#2457d6"   # драйвери (ліворуч) — синій
DRIVEN = "#c0392b"  # драйвовані (праворуч) — червоний
COREFILL = "#eefaf1"
CORESTROKE = "#27ae60"


def hexagon_points(cx, cy, r):
    """Плаский-верх шестикутник (flat-top): вершини під 0,60,120... + зсув 30."""
    pts = []
    for i in range(6):
        ang = math.radians(60 * i + 30)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def polygon(pts, fill, stroke, sw=2.5):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


# ── Фігура 1: шестикутник із портами й адаптерами ────────────────────────────
def fig_hexagon():
    W, H = 900, 560
    cx, cy, R = 450, 300, 150
    frags = []

    # шестикутник-ядро
    hp = hexagon_points(cx, cy, R)
    frags.append(polygon(hp, COREFILL, CORESTROKE, 3))
    frags.append(mtext(cx, cy - 14, ["Ядро", "домену"], size=20, bold=True, color=INK))
    frags.append(text(cx, cy + 28, "(не знає, хто зовні)", size=13, color=MUTED))

    # заголовки боків
    frags.append(text(150, 60, "Драйвери (хто гукає)", size=15, bold=True, color=DRIVE))
    frags.append(text(750, 60, "Драйвовані (кого гукають)", size=15, bold=True, color=DRIVEN))

    # порти — маленькі кружки-«дірки» на межі; ліворуч 2, праворуч 2
    port_r = 11
    # ліві порти (вхідні): на лівих гранях
    left_ports = [(cx - R * 0.87, cy - 78), (cx - R * 0.87, cy + 78)]
    right_ports = [(cx + R * 0.87, cy - 78), (cx + R * 0.87, cy + 78)]
    for (px, py) in left_ports:
        frags.append(circle(px, py, port_r, fill="#ffffff", stroke=DRIVE, sw=2.5))
    for (px, py) in right_ports:
        frags.append(circle(px, py, port_r, fill="#ffffff", stroke=DRIVEN, sw=2.5))

    # адаптери ліворуч (драйвери): прямокутники, стрілка ВХОДИТЬ у порт
    drivers = [("REST-\nконтролер", cy - 78), ("CLI /\nтест", cy + 78)]
    for (label, py) in drivers:
        bx, by, bw, bh = 40, py - 34, 150, 68
        frags.append(fitbox(bx, by, bw, bh, label, size=14, fill="#eaf0fd", stroke=DRIVE, sw=2, color=INK))
        frags.append(arrow(bx + bw, py, cx - R * 0.87 - port_r - 2, py, color=DRIVE, sw=2.2))

    # адаптери праворуч (драйвовані): стрілка ВИХОДИТЬ із порту в адаптер
    driven = [("Репозиторій\nPostgres", cy - 78), ("Пошта /\nSMTP", cy + 78)]
    for (label, py) in driven:
        bx, by, bw, bh = 710, py - 34, 150, 68
        frags.append(fitbox(bx, by, bw, bh, label, size=14, fill="#fdecea", stroke=DRIVEN, sw=2, color=INK))
        frags.append(arrow(cx + R * 0.87 + port_r + 2, py, bx, py, color=DRIVEN, sw=2.2))

    # підпис портів (окремо, поза лініями)
    frags.append(text(cx - R * 0.87 - 4, cy - 108, "порт", size=12, italic=True, color=MUTED))
    frags.append(text(cx + R * 0.87 + 4, cy - 108, "порт", size=12, italic=True, color=MUTED))

    render(os.path.join(OUT, "hexagon.svg"), W, H, *frags)


# ── Фігура 2: куди дивляться стрілки залежності ──────────────────────────────
def fig_dependencies():
    W, H = 900, 340
    frags = []

    core_cx, core_cy = 450, 175
    cbody, cw, ch = textbox(core_cx, core_cy, ["Ядро + порти", "(інтерфейси)"],
                            size=16, bold=True, pad=18,
                            fill=COREFILL, stroke=CORESTROKE, sw=3, min_w=220)
    frags.append(cbody)

    # лівий адаптер (драйвер) і правий адаптер (драйвований) — обидва ЗБОКУ
    la, lay, law, lah = 70, 140, 200, 70
    frags.append(fitbox(la, lay, law, lah, "Адаптер-драйвер\n(REST, CLI)", size=14,
                        fill="#eaf0fd", stroke=DRIVE, sw=2, color=INK))
    ra, ray, raw, rah = 630, 140, 200, 70
    frags.append(fitbox(ra, ray, raw, rah, "Адаптер-драйвований\n(БД, пошта)", size=14,
                        fill="#fdecea", stroke=DRIVEN, sw=2, color=INK))

    # ОБИДВІ стрілки залежності йдуть ДО ядра (до порту)
    frags.append(arrow(la + law, core_cy, core_cx - cw / 2 - 6, core_cy, color=DRIVE, sw=2.4))
    frags.append(arrow(ra, core_cy, core_cx + cw / 2 + 6, core_cy, color=DRIVEN, sw=2.4))

    # підписи над стрілками (поза лініями — вище)
    frags.append(text((la + law + core_cx - cw / 2) / 2, core_cy - 22, "залежить →", size=13, italic=True, color=DRIVE))
    frags.append(text((ra + core_cx + cw / 2) / 2, core_cy - 22, "← залежить", size=13, italic=True, color=DRIVEN))

    frags.append(text(W / 2, 300, "Обидві стрілки впираються в ядро — воно не залежить ні від кого", size=14, color=INK))

    render(os.path.join(OUT, "dependencies.svg"), W, H, *frags)


# ── Фігура 3: хибне читання «шість шарів» проти правильного «порти на гранях» ─
def fig_six_vs_ports():
    W, H = 940, 480
    frags = []
    R = 130

    # заголовки двох панелей (високо, поза фігурами)
    frags.append(text(240, 44, "Хибне читання", size=17, bold=True, color=POS))
    frags.append(text(700, 44, "Що є насправді", size=17, bold=True, color=FIELD))
    # роздільна лінія між панелями
    frags.append(line(470, 70, 470, 430, color="#d0d5db", sw=1.5, dash="6 6"))

    # ── ЛІВА панель: шестикутник, порізаний на 6 пронумерованих скиб ──
    lcx, lcy = 240, 250
    hpL = hexagon_points(lcx, lcy, R)
    frags.append(polygon(hpL, "#fdecea", POS, 2.5))
    # 6 ліній від центру до вершин → 6 «скиб-шарів»
    for (vx, vy) in hpL:
        frags.append(line(lcx, lcy, vx, vy, color=POS, sw=1.6))
    # номери скиб — на бісектрисі кожного сектора, ближче до краю
    for i in range(6):
        ang = math.radians(60 * i)  # середина сектора між вершинами (вершини під +30)
        nx = lcx + (R * 0.6) * math.cos(ang)
        ny = lcy + (R * 0.6) * math.sin(ang) + 5
        frags.append(text(nx, ny, "шар %d" % (i + 1), size=12, bold=True, color=POS))
    # великий червоний хрест поверх — «ні»
    frags.append(text(lcx, lcy + 8, "✗", size=44, bold=True, color=POS))
    frags.append(text(lcx, lcy + R + 42, "«шість граней = шість шарів»", size=13, color=INK))
    frags.append(text(lcx, lcy + R + 62, "число шість тут вигадане", size=12, italic=True, color=MUTED))

    # ── ПРАВА панель: те саме ядро, порти-кружки на гранях, кількість довільна ──
    rcx, rcy = 700, 250
    hpR = hexagon_points(rcx, rcy, R)
    frags.append(polygon(hpR, COREFILL, CORESTROKE, 3))
    frags.append(mtext(rcx, rcy - 6, ["ядро", "(цілісне)"], size=15, bold=True, color=INK))
    # порти — кружки на СЕРЕДИНАХ граней; беремо лише 3 (довільно), решту граней лишаємо голими
    port_r = 12
    mids = []
    for i in range(6):
        a1 = math.radians(60 * i + 30)
        a2 = math.radians(60 * (i + 1) + 30)
        mx = rcx + R * (math.cos(a1) + math.cos(a2)) / 2
        my = rcy + R * (math.sin(a1) + math.sin(a2)) / 2
        mids.append((mx, my))
    chosen = [0, 2, 4]  # три порти — просто щоб показати «скільки треба»
    for idx in chosen:
        mx, my = mids[idx]
        frags.append(circle(mx, my, port_r, fill="#ffffff", stroke=CORESTROKE, sw=2.5))
    # один підпис «порт» — до верхнього обраного, винесений НАД фігуру
    tmx, tmy = mids[4]
    frags.append(text(tmx, tmy - 20, "порт", size=12, italic=True, color=FIELD))
    frags.append(text(rcx, rcy + R + 42, "грані — лише місце для портів", size=13, color=INK))
    frags.append(text(rcx, rcy + R + 62, "їх стільки, скільки треба (2–4)", size=12, italic=True, color=MUTED))

    render(os.path.join(OUT, "six-vs-ports.svg"), W, H, *frags)


# ── Фігура (вставка proj): жива підміна адаптера — спільне ядро, дві збірки ───
def fig_swap():
    W, H = 940, 430
    frags = []

    # ЯДРО + вихідний порт — по центру
    core_cx, core_cy = 470, 205
    cbody, cw, ch = textbox(core_cx, core_cy, ["Ядро + порт", "ЗамовленняСховище"],
                            size=15, bold=True, pad=16,
                            fill=COREFILL, stroke=CORESTROKE, sw=3, min_w=210)
    frags.append(cbody)
    frags.append(text(core_cx, core_cy + ch / 2 + 20,
                      "спільне для обох світів — не змінюється",
                      size=12, italic=True, color=MUTED))

    # ── ЛІВОРУЧ: дві точки збірки (прод / локальна) ──
    frags.append(text(150, 40, "Точки збірки (край)", size=14, bold=True, color=DRIVE))
    roots = [("Прод-збірка", 120), ("Локальна збірка", 290)]
    for (label, ry) in roots:
        rx, rw, rh = 40, 205, 58
        frags.append(fitbox(rx, ry - rh / 2, rw, rh, label, size=14,
                            fill="#eaf0fd", stroke=DRIVE, sw=2, color=INK))
        frags.append(arrow(rx + rw, ry, core_cx - cw / 2 - 8, core_cy,
                           color=DRIVE, sw=2.2))

    # ── ПРАВОРУЧ: два драйвовані адаптери одного порту ──
    frags.append(text(795, 40, "Адаптери одного порту", size=14, bold=True, color=DRIVEN))
    adapters = [("Сховище\nPostgres", 120, "прод"), ("Сховище\nв памʼяті", 290, "локально / тест")]
    for (label, ay, tag) in adapters:
        ax, aw, ah = 690, 205, 58
        frags.append(fitbox(ax, ay - ah / 2, aw, ah, label, size=14,
                            fill="#fdecea", stroke=DRIVEN, sw=2, color=INK))
        frags.append(arrow(core_cx + cw / 2 + 8, core_cy, ax, ay,
                           color=DRIVEN, sw=2.2))
        frags.append(text(ax + aw / 2, ay + ah / 2 + 15, tag, size=11,
                          italic=True, color=MUTED))

    frags.append(text(W / 2, 408,
                      "Вибір адаптера робить лише точка збірки; ядро й порт — ті самі",
                      size=14, color=INK))

    render(os.path.join(OUT, "swap.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_hexagon()
    fig_dependencies()
    fig_six_vs_ports()
    fig_swap()
    print("figures written")
