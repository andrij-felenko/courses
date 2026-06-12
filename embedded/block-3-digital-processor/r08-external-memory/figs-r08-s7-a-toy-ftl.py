# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для алгоритмічної вставки §3.8.7a
«Іграшковий FTL: таблиця відображення і garbage collection у 100 рядків».
Розділ 3.8 «Зовнішня пам'ять» (Модуль 3). Чистий Python, без залежностей.
Вивід → ./img/. Головний figs.py розділу НЕ чіпаємо — це самодостатній скрипт.

Стиль (AUTHORING §9): білий фон; чинна сторінка/«1» червоний, застаріле/«0» синій;
поле/реальна флеш зелене; стрілки через marker; шрифт sans-serif. Допоміжні
функції — копія спільних, щоб вигляд збігався з рештою розділів.

Нумерація підписів — за темою/вставкою: «Рис. 3.8.7a.k».
"""
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
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


def curve(x1, y1, cx, cy, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _cell(x, y, w, h, label, fill, stroke, tcol=None, sub=None, lsize=13):
    """Клітинка таблиці/сторінки: прямокутник із підписом усередині."""
    s = rect(x, y, w, h, fill, stroke, 1.8, 6)
    s += text(x + w / 2, y + h / 2 + (lsize * 0.34 if not sub else -1), label,
              lsize, tcol or stroke, "middle", "bold")
    if sub:
        s += text(x + w / 2, y + h / 2 + 13, sub, 9, GREY, "middle")
    return s


# ════════ Рис. 3.8.7a.1 — рівень непрямості: LBA → таблиця → фізична сторінка ════
def fig_indirection():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 32, "FTL — це один рівень непрямості: «диск» нагорі, NAND унизу", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "контролер вдає рівні нумеровані сектори (LBA), а таблиця відображення переводить кожен у РЕАЛЬНУ фізичну сторінку флеші",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: логічний бік (що бачить хост) ─────────────────────────────
    lx = 70
    s += text(lx + 70, 92, "Що бачить хост (host):", 12.5, BLUE, "start", "bold")
    s += text(lx + 70, 108, "рівні «сектори диска» з номерами LBA", 9.5, GREY, "start", style="italic")
    lbas = ["LBA 0", "LBA 1", "LBA 2", "LBA 3"]
    for i, t in enumerate(lbas):
        y = 124 + i * 52
        s += _cell(lx, y, 140, 42, t, "#f3f5fd", BLUE)
    s += text(lx + 70, 124 + 4 * 52 + 6, "… (нумерація суцільна, як у HDD)", 9, GREY, "middle", style="italic")

    # ── центр: таблиця відображення (mapping table) ───────────────────────
    mx = 360
    s += text(mx + 90, 92, "Таблиця відображення (mapping table)", 12.5, INK, "middle", "bold")
    s += text(mx + 90, 108, "у RAM контролера: LBA → фізична сторінка", 9.5, GREY, "middle", style="italic")
    rows = [("LBA 0", "→ блок 7, стор. 2"),
            ("LBA 1", "→ блок 2, стор. 0"),
            ("LBA 2", "→ блок 7, стор. 5"),
            ("LBA 3", "→ блок 4, стор. 1")]
    for i, (a, b) in enumerate(rows):
        y = 124 + i * 52
        s += rect(mx, y, 180, 42, "#fdfbf2", AMBER, 1.8, 6)
        s += text(mx + 12, y + 26, a, 12, INK, "start", "bold")
        s += line(mx + 70, y + 8, mx + 70, y + 34, FAINT, 1.2)
        s += text(mx + 78, y + 26, b, 10.5, "#9a7322", "start", "bold")
        # стрілка LBA → рядок таблиці
        s += arrow(lx + 142, 124 + i * 52 + 21, mx - 2, y + 21, BLUE, 1.6)

    # ── праворуч: фізична NAND-флеш (блоки × сторінки) ─────────────────────
    fx = 700
    s += text(fx + 95, 92, "Реальна NAND-флеш", 12.5, GREEN, "middle", "bold")
    s += text(fx + 95, 108, "блоки з фіксованих сторінок (§3.8.5)", 9.5, GREY, "middle", style="italic")
    # три блоки по 6 сторінок
    blocks = [("блок 2", 0), ("блок 4", 1), ("блок 7", 2)]
    bw, ph = 60, 26
    for name, bi in blocks:
        bx = fx + bi * 66
        by = 124
        s += text(bx + bw / 2, by - 4, name, 9.5, GREEN, "middle", "bold")
        for p in range(6):
            yy = by + p * (ph + 3)
            s += rect(bx, yy, bw, ph, "#eef7ee", GREEN, 1.2, 3)
            s += text(bx + 5, yy + 17, f"s{p}", 8.5, GREY, "start")
    # підсвітити фізичні сторінки, на які вказує таблиця, і провести стрілки
    # координати: блок 2 -> bi=0, блок 4 -> bi=1, блок 7 -> bi=2
    targets = [(2, 2, RED), (0, 0, RED), (5, 2, RED), (1, 1, RED)]
    # (page_in_block, block_index_among[2,4,7]) для LBA0..3
    map_idx = [(2, 2), (0, 0), (5, 2), (1, 1)]
    for i, (p, bi) in enumerate(map_idx):
        bx = fx + bi * 66
        yy = 124 + p * (ph + 3)
        s += rect(bx, yy, bw, ph, "#fdecec", RED, 2.2, 3)
        s += text(bx + bw / 2 + 6, yy + 17, "★", 11, RED, "middle", "bold")
        # стрілка від рядка таблиці до фізичної сторінки
        s += curve(mx + 182, 124 + i * 52 + 21, fx - 26, yy - 16, bx - 2, yy + 13, AMBER, 1.5, "5 3")

    # ── нижня плашка: ключова думка ───────────────────────────────────────
    s += rect(60, 408, W - 120, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 430, "Хост каже «читай LBA 2» — FTL миттю дивиться в таблицю й бачить: це блок 7, сторінка 5. Та сама адреса завтра може жити деінде.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 449, "Логічний номер відв'язаний від фізичного місця — у цьому й увесь фокус «контролер вдає диск».",
              10, GREY, "middle", style="italic")
    save("fig-3-8-7a-1-indirection.svg", s)


# ═══════ Рис. 3.8.7a.2 — запис «не на місці» плодить застарілі сторінки ═══════
def fig_oop_write():
    W, H = 940, 460
    s = header(W, H)
    s += text(W / 2, 32, "Чому з'являється сміття: запис «не на місці» (out-of-place)", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "NAND не вміє переписати сторінку на місці (§3.8.5), тож оновлення лягає в НОВУ сторінку, а стара стає застарілою",
              11.5, GREY, "middle", style="italic")

    # три послідовні стани блоку 7 (6 сторінок), зліва направо
    states = [
        ("1. Спершу", "LBA 2 живе у стор. 5", 5, None),
        ("2. Хост пише LBA 2 знову", "нова версія → у вільну стор. 0;\nтаблицю переводимо туди", 0, 5),
        ("3. Наслідок", "стор. 0 — чинна;\nстор. 5 — застаріла (сміття)", 0, 5),
    ]
    bw, ph = 86, 30
    for col, (title, note, valid_p, stale_p) in enumerate(states):
        bx = 90 + col * 290
        by = 130
        s += text(bx + bw / 2, 92, title, 12.5, INK, "middle", "bold")
        for ln_i, ln in enumerate(note.split("\n")):
            s += text(bx + bw / 2, 108 + ln_i * 13, ln, 9.5, GREY, "middle", style="italic")
        s += text(bx + bw / 2, by - 6, "блок 7", 10, GREEN, "middle", "bold")
        for p in range(6):
            yy = by + p * (ph + 4)
            fill, stroke, lab, lcol = "#eef7ee", GREEN, "вільна", GREY
            if p == valid_p:
                fill, stroke, lab, lcol = "#fdecec", RED, "LBA 2 (чинна)", RED
            elif stale_p is not None and p == stale_p:
                fill, stroke, lab, lcol = "#eef1fb", BLUE, "LBA 2 (стара)", BLUE
            s += rect(bx, yy, bw, ph, fill, stroke, 1.8, 4)
            s += text(bx + 6, yy + 13, f"стор. {p}", 8.5, GREY, "start")
            s += text(bx + 6, yy + 25, lab, 8.5, lcol, "start", "bold")
        # позначка таблиці під блоком
        ty = by + 6 * (ph + 4) + 8
        if col == 0:
            s += text(bx + bw / 2, ty, "таблиця: LBA 2 → стор. 5", 9.5, AMBER, "middle", "bold")
        else:
            s += text(bx + bw / 2, ty, "таблиця: LBA 2 → стор. 0", 9.5, AMBER, "middle", "bold")
        # стрілка переходу між станами
        if col < 2:
            ax = bx + bw + 28
            s += arrow(ax, by + 80, ax + 60, by + 80, INK, 2.2)

    # позначка «застаріле» на третьому стані
    bx3 = 90 + 2 * 290
    s += text(bx3 + bw + 18, 130 + 5 * (ph + 4) + 15, "↩ застаріла:", 10, BLUE, "start", "bold")
    s += text(bx3 + bw + 18, 130 + 5 * (ph + 4) + 29, "дані ще лежать,", 9, GREY, "start")
    s += text(bx3 + bw + 18, 130 + 5 * (ph + 4) + 41, "та вже нікому", 9, GREY, "start")

    s += rect(60, 408, W - 120, 44, "#eef1fb", BLUE, 1.6, 10)
    s += text(W / 2, 430, "Жоден біт не «переписано на місці»: оновлення = нова сторінка + переведена таблиця. Старі версії копичаться як застарілі (stale).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 448, "Рано чи пізно вільні сторінки скінчаться, хоч півблоку — застаріле сміття. Звідси й потреба в прибиранні.",
              10, GREY, "middle", style="italic")
    save("fig-3-8-7a-2-oop-write.svg", s)


# ═══════════ Рис. 3.8.7a.3 — garbage collection: ущільнити й стерти блок ═══════════
def fig_gc():
    W, H = 940, 500
    s = header(W, H)
    s += text(W / 2, 32, "Garbage collection: зібрати чинне, стерти блок, повернути вільне місце", 19.5, INK, "middle", "bold")
    s += text(W / 2, 54, "стерти можна лише ЦІЛИЙ блок (§3.8.5) — тож спершу рятуємо живі сторінки в інший блок, аж тоді стираємо джерело начисто",
              11.5, GREY, "middle", style="italic")

    bw, ph = 96, 30
    # ── блок-жертва (зліва): мішанина чинного й застарілого ───────────────
    sx, sy = 80, 132
    s += text(sx + bw / 2, 96, "Блок-жертва (victim)", 12.5, INK, "middle", "bold")
    s += text(sx + bw / 2, 112, "багато застарілого, мало живого", 9.5, GREY, "middle", style="italic")
    s += text(sx + bw / 2, sy - 6, "блок 7", 10, GREEN, "middle", "bold")
    victim = ["stale", "valid", "stale", "stale", "valid", "stale"]  # 2 живі, 4 застарілі
    valid_rows = []
    for p, kind in enumerate(victim):
        yy = sy + p * (ph + 4)
        if kind == "valid":
            fill, stroke, lab, lcol = "#fdecec", RED, "чинна", RED
            valid_rows.append((p, yy))
        else:
            fill, stroke, lab, lcol = "#eef1fb", BLUE, "застаріла", BLUE
        s += rect(sx, yy, bw, ph, fill, stroke, 1.8, 4)
        s += text(sx + 6, yy + 13, f"s{p}", 8.5, GREY, "start")
        s += text(sx + 6, yy + 25, lab, 9, lcol, "start", "bold")

    # ── цільовий блок (центр): чисті вільні сторінки ──────────────────────
    tx, ty = 420, 132
    s += text(tx + bw / 2, 96, "Вільний блок (приймач)", 12.5, GREEN, "middle", "bold")
    s += text(tx + bw / 2, 112, "сюди копіюємо лише ЖИВЕ", 9.5, GREY, "middle", style="italic")
    s += text(tx + bw / 2, ty - 6, "блок 9", 10, GREEN, "middle", "bold")
    for p in range(6):
        yy = ty + p * (ph + 4)
        if p < len(valid_rows):
            fill, stroke, lab, lcol = "#fdecec", RED, "чинна (копія)", RED
        else:
            fill, stroke, lab, lcol = "#eef7ee", GREEN, "вільна", GREY
        s += rect(tx, yy, bw, ph, fill, stroke, 1.8, 4)
        s += text(tx + 6, yy + 13, f"s{p}", 8.5, GREY, "start")
        s += text(tx + 6, yy + 25, lab, 8.5, lcol, "start", "bold")

    # стрілки копіювання живих сторінок жертва → приймач
    for i, (p, yy) in enumerate(valid_rows):
        dst_y = ty + i * (ph + 4) + ph / 2
        s += curve(sx + bw + 2, yy + ph / 2, (sx + bw + tx) / 2, yy - 18 - i * 8,
                   tx - 2, dst_y, RED, 1.8)
    s += text((sx + bw + tx) / 2 + 6, 124, "1. копіюємо живе", 10.5, RED, "middle", "bold")
    s += text((sx + bw + tx) / 2 + 6, 138, "+ правимо таблицю", 9, "#9a7322", "middle", "bold")

    # ── праворуч: стертий блок-жертва, знову весь вільний ─────────────────
    ex, ey = 760, 132
    s += text(ex + bw / 2, 96, "Стертий блок-жертва", 12.5, GREEN, "middle", "bold")
    s += text(ex + bw / 2, 112, "цілий блок — назад у запас", 9.5, GREY, "middle", style="italic")
    s += text(ex + bw / 2, ey - 6, "блок 7", 10, GREEN, "middle", "bold")
    for p in range(6):
        yy = ey + p * (ph + 4)
        s += rect(ex, yy, bw, ph, "#eef7ee", GREEN, 1.8, 4)
        s += text(ex + 6, yy + 13, f"s{p}", 8.5, GREY, "start")
        s += text(ex + 6, yy + 25, "вільна", 8.5, GREY, "start")
    # стрілка стирання приймач-зона → стертий блок
    s += arrow(tx + bw + 2, ty + 3 * (ph + 4), ex - 2, ey + 3 * (ph + 4), GREEN, 2.4)
    s += text((tx + bw + ex) / 2 + 4, ty + 3 * (ph + 4) - 10, "2. стерти", 10.5, GREEN, "middle", "bold")
    s += text((tx + bw + ex) / 2 + 4, ty + 3 * (ph + 4) + 6, "весь блок", 9, GREY, "middle", "bold")

    # ── нижня плашка: підрахунок «звільнили» ──────────────────────────────
    s += rect(60, 448, W - 120, 44, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 470, "Було: 4 застарілі + 2 живі сторінки в зайнятому блоці. Стало: 2 живі переїхали, цілий блок 7 — порожній і готовий приймати.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 488, "Ціна — «зайвий» запис 2 живих сторінок (write amplification): прибирання НЕ безкоштовне, але без нього вільне місце скінчиться.",
              10, GREY, "middle", style="italic")
    save("fig-3-8-7a-3-gc.svg", s)


if __name__ == "__main__":
    fig_indirection()
    fig_oop_write()
    fig_gc()
    print("OK — 3 SVG згенеровано у", OUT)
