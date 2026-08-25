# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def homomorphism():
    """Граф організації (команди + канали) відображається у граф системи
    (модулі + інтерфейси) — той самий візерунок; відсутній канал => відсутній стик."""
    W, H = 860, 430
    parts = []

    # --- Ліва панель: організація ---
    lx = 200
    parts.append(text(lx, 60, "Організація", size=17, bold=True, color=INK))
    parts.append(text(lx, 82, "команди й канали спілкування", size=12, color=MUTED))

    # три команди-вузли (трикутник): A вгорі, B зліва внизу, C справа внизу
    A = (lx, 150)
    B = (lx - 95, 300)
    C = (lx + 95, 300)
    # канали: A–B густий, A–C густий, B–C НЕМАЄ (не говорять)
    parts.append(line(A[0], A[1], B[0], B[1], color=INK, sw=3))
    parts.append(line(A[0], A[1], C[0], C[1], color=INK, sw=3))
    # позначка «немає каналу» між B і C — пунктир сірий
    parts.append(line(B[0] + 26, B[1], C[0] - 26, C[1], color=MUTED, sw=1.4, dash="3 6"))
    parts.append(text(lx, 340, "не спілкуються", size=11, color=MUTED))

    for (cx, cy), lab in [(A, "A"), (B, "B"), (C, "C")]:
        parts.append(circle(cx, cy, 26, fill="#eef2ff", stroke=NEG, sw=2.5))
        parts.append(text(cx, cy + 7, lab, size=20, bold=True, color=NEG))

    # --- Стрілка-«штамп» посередині ---
    parts.append(arrow(lx + 130, 225, W - 400 + 0, 225, color=INK, sw=2.4))
    parts.append(text(W / 2, 210, "штампує", size=13, bold=True, color=INK))
    parts.append(text(W / 2, 246, "форму", size=13, color=MUTED))

    # --- Права панель: система ---
    rx = 660
    parts.append(text(rx, 60, "Система", size=17, bold=True, color=INK))
    parts.append(text(rx, 82, "модулі й інтерфейси між ними", size=12, color=MUTED))

    Am = (rx, 150)
    Bm = (rx - 95, 300)
    Cm = (rx + 95, 300)
    # інтерфейси повторюють канали: A–B є, A–C є, B–C немає
    parts.append(line(Am[0], Am[1], Bm[0], Bm[1], color=INK, sw=3))
    parts.append(line(Am[0], Am[1], Cm[0], Cm[1], color=INK, sw=3))
    parts.append(line(Bm[0] + 26, Bm[1], Cm[0] - 26, Cm[1], color=MUTED, sw=1.4, dash="3 6"))
    parts.append(text(rx, 340, "стику немає", size=11, color=MUTED))

    for (cx, cy), lab in [(Am, "a"), (Bm, "b"), (Cm, "c")]:
        parts.append(circle(cx, cy, 26, fill="#f4f6f8", stroke=INK, sw=2.5))
        parts.append(text(cx, cy + 7, lab, size=20, bold=True, color=INK))

    # підпис-відповідність внизу
    parts.append(text(W / 2, 400, "команда → модуль,  канал → інтерфейс,  тиша → шов",
                      size=13, color=INK))

    render(os.path.join(IMG, "homomorphism.svg"), W, H, *parts)


def four_teams():
    """Чотири команди на компілятор -> чотири проходи компілятора: кожна команда
    ліпить свій прохід, бо стик між проходами дешевший за спільний код."""
    W, H = 720, 470
    parts = []
    parts.append(text(W / 2, 44, "Чотири команди на компілятор — чотири проходи", size=16, bold=True))

    teams = ["Команда 1", "Команда 2", "Команда 3", "Команда 4"]
    passes = ["Прохід 1", "Прохід 2", "Прохід 3", "Прохід 4"]
    # колонки
    tx, px = 150, 500
    box_w, box_h = 190, 62
    y0, gap = 90, 92

    parts.append(text(tx + box_w / 2, 78, "організація", size=12, color=MUTED))
    parts.append(text(px + box_w / 2, 78, "система", size=12, color=MUTED))

    for i in range(4):
        y = y0 + i * gap
        # команда
        parts.append(fitbox(tx, y, box_w, box_h, teams[i], size=15, bold=True,
                            fill="#eef2ff", stroke=NEG, color=NEG))
        # прохід
        parts.append(fitbox(px, y, box_w, box_h, passes[i], size=15, bold=True,
                            fill="#f4f6f8", stroke=INK, color=INK))
        # стрілка команда -> прохід (кожна своя, горизонтальна)
        parts.append(arrow(tx + box_w + 8, y + box_h / 2, px - 8, y + box_h / 2,
                           color=MUTED, sw=1.8))

    # потік даних між проходами (вертикальні стрілки праворуч)
    for i in range(3):
        y = y0 + i * gap + box_h
        parts.append(arrow(px + box_w / 2, y + 4, px + box_w / 2, y + gap - box_h + 4,
                           color=INK, sw=1.8))

    parts.append(text(W / 2, H - 20,
                      "кожна команда ліпить свій прохід — стик між проходами дешевший за спільний код",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "four-teams.svg"), W, H, *parts)


def pipeline():
    """Проєкт: граф команд (дані) -> матриця суміжності модулів -> передбачені
    шви й компоненти зв'язності. Три панелі зліва направо, зі стрілками між ними."""
    W, H = 980, 470
    parts = []
    parts.append(text(W / 2, 34, "Граф команд як дані  →  матриця модулів  →  передбачені шви й автономні частини",
                      size=15, bold=True))

    # ── Панель 1: граф команд (вхідні дані) ──────────────────────────────
    p1x = 150
    parts.append(text(p1x, 74, "вхід: граф команд", size=13, bold=True, color=NEG))
    # 5 команд: order, pay, ship (зв'язані через order), analytics (окремо), plus report<->analytics
    nodes = {
        "order":     (p1x,        140),
        "pay":       (p1x - 80,   230),
        "ship":      (p1x + 80,   230),
        "report":    (p1x - 55,   340),
        "analytics": (p1x + 60,   340),
    }
    # канали спілкування (ребра організації)
    org_edges = [("order", "pay"), ("order", "ship"),
                 ("report", "analytics")]
    for a, b in org_edges:
        ax, ay = nodes[a]; bx, by = nodes[b]
        parts.append(line(ax, ay, bx, by, color=INK, sw=2.4))
    # намалювати вузли поверх ліній
    short = {"order": "ord", "pay": "pay", "ship": "shp", "report": "rep", "analytics": "anl"}
    for name, (cx, cy) in nodes.items():
        parts.append(circle(cx, cy, 21, fill="#eef2ff", stroke=NEG, sw=2.2))
        parts.append(text(cx, cy + 5, short[name], size=12, bold=True, color=NEG))
    parts.append(text(p1x, 405, "два кластери:", size=11, color=MUTED))
    parts.append(text(p1x, 421, "{ord,pay,shp} та {rep,anl}", size=11, color=MUTED))

    # стрілка 1 -> 2
    parts.append(arrow(p1x + 105, 240, 355, 240, color=INK, sw=2.2))

    # ── Панель 2: матриця суміжності модулів ─────────────────────────────
    order = ["ord", "pay", "shp", "rep", "anl"]
    # 1, якщо між командами є канал (симетрично); беремо з org_edges + діагональ 0
    idx = {"order": "ord", "pay": "pay", "ship": "shp", "report": "rep", "analytics": "anl"}
    adj = {(idx[a], idx[b]) for a, b in org_edges}
    adj |= {(b, a) for a, b in list(adj)}

    m0x, m0y = 470, 110   # лівий-верхній кут сітки чисел
    cell = 34
    parts.append(text(m0x + cell * 2.5 - 6, 74, "матриця суміжності", size=13, bold=True, color=INK))
    # підписи стовпців
    for j, c in enumerate(order):
        parts.append(text(m0x + j * cell + cell / 2, m0y - 8, c, size=11, bold=True, color=MUTED))
    # рядки з підписом і клітинками
    for i, r in enumerate(order):
        cy = m0y + i * cell
        parts.append(text(m0x - 14, cy + cell / 2 + 4, r, size=11, bold=True, color=MUTED, anchor="end"))
        for j, c in enumerate(order):
            cx = m0x + j * cell
            v = 1 if (r, c) in adj else 0
            fill = "#e8f0ff" if v else BG
            parts.append(rect(cx, cy, cell, cell, fill=fill, stroke="#cfd6e0", sw=1.0, rx=3))
            parts.append(text(cx + cell / 2, cy + cell / 2 + 4, str(v),
                              size=12, bold=bool(v), color=(NEG if v else MUTED)))
    parts.append(text(m0x + cell * 2.5 - 6, m0y + 5 * cell + 22,
                      "1 = передбачений стик (є канал)", size=11, color=MUTED))

    # стрілка 2 -> 3
    parts.append(arrow(m0x + 5 * cell + 18, 240, 748, 240, color=INK, sw=2.2))

    # ── Панель 3: два компоненти зв'язності (майбутні автономні частини) ──
    p3x = 860
    parts.append(text(p3x, 74, "дві автономні частини", size=13, bold=True, color=FIELD))
    # компонент 1: ord-pay-shp у зеленій рамці
    c1 = {"ord": (p3x, 130), "pay": (p3x - 55, 205), "shp": (p3x + 55, 205)}
    parts.append(rect(p3x - 92, 100, 184, 138, fill="#eafaf0", stroke=FIELD, sw=2, rx=12))
    for a, b in [("ord", "pay"), ("ord", "shp")]:
        ax, ay = c1[a]; bx, by = c1[b]
        parts.append(line(ax, ay, bx, by, color=INK, sw=2.2))
    for name, (cx, cy) in c1.items():
        parts.append(circle(cx, cy, 20, fill="#f4f6f8", stroke=INK, sw=2))
        parts.append(text(cx, cy + 5, name, size=12, bold=True, color=INK))
    # компонент 2: rep-anl у другій зеленій рамці
    c2 = {"rep": (p3x - 45, 330), "anl": (p3x + 45, 330)}
    parts.append(rect(p3x - 92, 290, 184, 92, fill="#eafaf0", stroke=FIELD, sw=2, rx=12))
    parts.append(line(c2["rep"][0], c2["rep"][1], c2["anl"][0], c2["anl"][1], color=INK, sw=2.2))
    for name, (cx, cy) in c2.items():
        parts.append(circle(cx, cy, 20, fill="#f4f6f8", stroke=INK, sw=2))
        parts.append(text(cx, cy + 5, name, size=12, bold=True, color=INK))
    parts.append(text(p3x, 421, "між рамками — жодного стику", size=11, color=MUTED))

    render(os.path.join(IMG, "pipeline.svg"), W, H, *parts)


def seam_shift():
    """Одна нова лінія спілкування зшиває два колись-окремі компоненти в один —
    передбачений шов зникає. Ліворуч: два компоненти; праворуч: після каналу — один."""
    W, H = 820, 380
    parts = []
    parts.append(text(W / 2, 34, "Додали один канал спілкування — і передбачений шов зник", size=15, bold=True))

    def draw_side(ox, title, joined, title_color):
        parts.append(text(ox, 74, title, size=13, bold=True, color=title_color))
        # компонент A: ord-pay-shp
        A = {"ord": (ox, 130), "pay": (ox - 62, 205), "shp": (ox + 62, 205)}
        # компонент B: rep-anl
        B = {"rep": (ox - 45, 315), "anl": (ox + 55, 315)}
        # внутрішні ребра
        inner = [("ord", "pay", A), ("ord", "shp", A), ("rep", "anl", B)]
        for a, b, g in inner:
            parts.append(line(g[a][0], g[a][1], g[b][0], g[b][1], color=INK, sw=2.2))
        # міст pay–rep, якщо joined
        if joined:
            parts.append(line(A["pay"][0], A["pay"][1] + 14, B["rep"][0], B["rep"][1] - 14,
                              color=POS, sw=2.8))
            # підпис праворуч від мосту, у вільній зоні (не на лініях)
            parts.append(text(ox + 78, 262, "новий", size=11, bold=True, color=POS, anchor="start"))
            parts.append(text(ox + 78, 277, "канал", size=11, bold=True, color=POS, anchor="start"))
        for g in (A, B):
            for name, (cx, cy) in g.items():
                col = INK
                parts.append(circle(cx, cy, 20, fill="#f4f6f8", stroke=col, sw=2))
                parts.append(text(cx, cy + 5, name, size=12, bold=True, color=col))
        return

    draw_side(210, "було: дві компоненти", False, FIELD)
    # позначка «шов тут» між компонентами ліворуч
    parts.append(text(210, 262, "шов ⟵ тут", size=11, bold=True, color=FIELD))

    # стрілка переходу
    parts.append(arrow(390, 210, 470, 210, color=INK, sw=2.4))
    parts.append(text(430, 194, "+канал", size=12, bold=True, color=POS))

    draw_side(620, "стало: одна компонента", True, NEG)
    parts.append(text(620, H - 18, "усе зрослося — автономної межі більше немає", size=11, color=MUTED))
    parts.append(text(210, H - 18, "дві частини живуть окремо", size=11, color=MUTED))

    render(os.path.join(IMG, "seam-shift.svg"), W, H, *parts)


if __name__ == "__main__":
    homomorphism()
    four_teams()
    pipeline()
    seam_shift()
    print("ok: homomorphism.svg, four-teams.svg, pipeline.svg, seam-shift.svg")
