# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── knob: одна ручка тягне два атрибути в різні боки ───────────────────────────
# Ідея: «trade-off» — це не список плюсів і мінусів, а ОДНА ручка (рішення), яку
# крутиш в один бік — один атрибут росте, інший падає. Показуємо кеш як ручку:
# більший TTL → швидше (менше запитів у базу), але свіжість даних гірша.
def fig_knob():
    W, H = 720, 340
    p = []

    cx = W / 2
    # ручка посередині
    kb, kw, kh = textbox(cx, 170, "розмір кешу / TTL\n(одна ручка рішення)",
                         size=13, bold=True, fill="#fff9e6", stroke="#e0a800",
                         sw=2.4, pad=14)
    p.append(kb)

    # ліворуч — атрибут, що РОСТЕ, коли крутиш управо
    lb, lw, lh = textbox(150, 90, "швидкість\n(латентність ↓)", size=13, bold=True,
                         fill="#d4edda", stroke=FIELD, sw=2.0, pad=12)
    p.append(lb)
    p.append(arrow(cx - kw / 2, 150, 150 + lw / 2, 90 + lh / 2, color=FIELD, sw=2.2))
    p.append(text(300, 108, "більше → краще", size=11, color=FIELD, italic=True))
    p.append(plus(150, 150))

    # праворуч — атрибут, що ПАДАЄ від того самого кроку
    rb, rw, rh = textbox(570, 90, "свіжість даних\n(застарілість ↑)", size=13, bold=True,
                         fill="#fdecea", stroke=POS, sw=2.0, pad=12)
    p.append(rb)
    p.append(arrow(cx + kw / 2, 150, 570 - rw / 2, 90 + rh / 2, color=POS, sw=2.2))
    p.append(text(430, 108, "більше → гірше", size=11, color=POS, italic=True))
    p.append(minus(570, 150))

    p.append(text(cx, 250, "Крутиш ОДНУ ручку — два атрибути рушають назустріч один одному.",
                  size=13, color=INK, bold=True))
    p.append(text(cx, 274, "Немає «правильного» положення — є те, що краще для ЦИХ сценаріїв.",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "knob.svg"), W, H, *p,
           title="Trade-off — це одна ручка, а не список плюсів і мінусів")


# ── matrix: три кандидати × чотири атрибути, домінанта відсутня ────────────────
# Ідея: коли жоден стовпчик не виграє за ВСІМА рядками — вибір неминуче
# компромісний. Оцінки грубі (+, 0, −), бо на цьому кроці точність зайва.
def fig_matrix():
    W, H = 760, 340
    p = []

    attrs = ["латентність", "вартість/міс", "простота", "стійкість до збоїв"]
    cands = ["один вузол", "реплікація", "шардинг"]
    # оцінки: + добре, 0 середньо, − погано (за рядком-атрибутом)
    score = {
        ("один вузол",       "латентність"):        "+",
        ("один вузол",       "вартість/міс"):        "+",
        ("один вузол",       "простота"):            "+",
        ("один вузол",       "стійкість до збоїв"):  "−",
        ("реплікація",       "латентність"):        "0",
        ("реплікація",       "вартість/міс"):        "0",
        ("реплікація",       "простота"):            "0",
        ("реплікація",       "стійкість до збоїв"):  "+",
        ("шардинг",          "латентність"):        "+",
        ("шардинг",          "вартість/міс"):        "−",
        ("шардинг",          "простота"):            "−",
        ("шардинг",          "стійкість до збоїв"):  "0",
    }

    x0, y0 = 250, 70          # верхній лівий кут сітки значень
    colw, rowh = 150, 52
    # заголовки стовпців (кандидати)
    for j, c in enumerate(cands):
        cxj = x0 + j * colw + colw / 2
        b, bw, bh = textbox(cxj, y0 - 26, c, size=12, bold=True,
                            fill="#eef2ff", stroke=NEG, sw=1.8, pad=9)
        p.append(b)
    # рядки (атрибути) + клітини
    for i, a in enumerate(attrs):
        cyi = y0 + i * rowh + rowh / 2
        # підпис рядка — праворуч вирівняний, широка колонка щоб не накладалось
        p.append(text(x0 - 20, cyi + 5, a, size=12, color=INK, anchor="end", bold=True))
        for j, c in enumerate(cands):
            cxj = x0 + j * colw + colw / 2
            v = score[(c, a)]
            col = FIELD if v == "+" else (POS if v == "−" else MUTED)
            fillc = "#d4edda" if v == "+" else ("#fdecea" if v == "−" else "#eef1f4")
            p.append(rect(cxj - colw / 2 + 6, cyi - rowh / 2 + 5, colw - 12, rowh - 10,
                          fill=fillc, stroke=col, sw=1.6, rx=6))
            glyph = {"+": "виграш", "0": "так собі", "−": "програш"}[v]
            p.append(text(cxj, cyi + 5, glyph, size=12, color=col, bold=True))

    p.append(text(W / 2, y0 + len(attrs) * rowh + 32,
                  "Жоден стовпчик не виграє за всіма рядками → вибір НЕМИНУЧЕ компромісний.",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, "matrix.svg"), W, H, *p,
           title="Матриця компромісів: кандидати проти якісних атрибутів")


# ── points: чутлива точка проти точки компромісу ──────────────────────────────
# Ідея (з ATAM): чутлива точка — одна ручка тягне ОДИН атрибут; точка компромісу —
# та сама ручка тягне КІЛЬКА атрибутів у різні боки. Друга дорожча в рішенні.
def fig_points():
    W, H = 760, 320
    p = []

    # ── ліворуч: чутлива точка ──
    lx = 190
    b, bw, bh = textbox(lx, 130, "число реплік", size=13, bold=True,
                        fill="#fff9e6", stroke="#e0a800", sw=2.2, pad=12)
    p.append(b)
    a1, aw, ah = textbox(lx, 235, "доступність", size=12, bold=True,
                         fill="#d4edda", stroke=FIELD, sw=1.8, pad=11)
    p.append(a1)
    p.append(arrow(lx, 130 + bh / 2, lx, 235 - ah / 2, color=FIELD, sw=2.2))
    p.append(text(lx, 74, "Чутлива точка", size=14, color=INK, bold=True))
    p.append(text(lx, 94, "ручка тягне ОДИН атрибут", size=11, color=MUTED, italic=True))

    # роздільник
    p.append(line(W / 2, 60, W / 2, H - 20, color=MUTED, sw=1.2, dash="5,5"))

    # ── праворуч: точка компромісу ──
    rx = 560
    b2, bw2, bh2 = textbox(rx, 130, "число реплік", size=13, bold=True,
                           fill="#fff9e6", stroke="#e0a800", sw=2.2, pad=12)
    p.append(b2)
    # два атрибути в різні боки
    pa, paw, pah = textbox(rx - 100, 235, "доступність", size=12, bold=True,
                           fill="#d4edda", stroke=FIELD, sw=1.8, pad=11)
    p.append(pa)
    pb, pbw, pbh = textbox(rx + 100, 235, "вартість", size=12, bold=True,
                           fill="#fdecea", stroke=POS, sw=1.8, pad=11)
    p.append(pb)
    p.append(arrow(rx - 20, 130 + bh2 / 2, rx - 100, 235 - pah / 2, color=FIELD, sw=2.2))
    p.append(arrow(rx + 20, 130 + bh2 / 2, rx + 100, 235 - pbh / 2, color=POS, sw=2.2))
    p.append(plus(rx - 100 - paw / 2 - 12, 235))
    p.append(minus(rx + 100 + pbw / 2 + 12, 235))
    p.append(text(rx, 74, "Точка компромісу", size=14, color=INK, bold=True))
    p.append(text(rx, 94, "ручка тягне КІЛЬКА — і в різні боки", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "points.svg"), W, H, *p,
           title="Чутлива точка vs точка компромісу — куди дивитись пильніше")


# ── timeline: SAAM → ATAM'98 → ATAM'2000 (для вставки hist-atam-origin) ────────
# Ідея: розрізнити попередника, першу публікацію й зрілий метод. SAAM (1994) —
# сценарії, одна якість. ATAM'98 — 6 кроків-спіраль, чутливі/компромісні точки.
# ATAM'2000 — 9 кроків, ДОДАНО дерево корисності й ризики/не-ризики.
def fig_timeline():
    W, H = 860, 400
    p = []

    # горизонтальна вісь часу
    axis_y = 90
    p.append(line(60, axis_y, W - 40, axis_y, color=MUTED, sw=2.0))
    # рік над віссю, роль-підпис ПІД віссю (жодна лінія їх не перетинає)
    cols = [
        (150, "1994", "предок",           MUTED),
        (430, "1998", "перша публікація",  FIELD),
        (720, "2000", "зрілий метод",      "#b8860b"),
    ]
    for x, yr, role, rc in cols:
        p.append(line(x, axis_y - 7, x, axis_y + 7, color=MUTED, sw=2.0))
        p.append(text(x, axis_y - 16, yr, size=14, color=INK, bold=True))
        p.append(text(x, axis_y + 26, role, size=11, color=rc, italic=True))

    # три віхи як картки під роль-підписами; кожна тримає СВОЄ
    card_cy = 210
    # SAAM 1994
    saam = ["SAAM", "сценарний аналіз", "прицілений на ОДНУ", "якість — змінюваність"]
    b1, w1, h1 = textbox(150, card_cy, "\n".join(saam), size=12, bold=False,
                         fill="#eef1f4", stroke=MUTED, sw=2.0, pad=13, min_w=180)
    p.append(b1)

    # ATAM 1998
    a98 = ["ATAM (1998)", "спіраль, 6 кроків",
           "ЧУТЛИВІ точки +", "ТОЧКИ КОМПРОМІСУ"]
    b2, w2, h2 = textbox(430, card_cy, "\n".join(a98), size=12, bold=False,
                         fill="#d4edda", stroke=FIELD, sw=2.2, pad=13, min_w=190)
    p.append(b2)

    # ATAM 2000
    a00 = ["ATAM (2000)", "9 кроків, 2 фази",
           "+ дерево корисності", "+ ризики / не-ризики"]
    b3, w3, h3 = textbox(720, card_cy, "\n".join(a00), size=12, bold=False,
                         fill="#fff9e6", stroke="#e0a800", sw=2.2, pad=13, min_w=195)
    p.append(b3)

    # стрілки наступності між картками (нижче роль-підписів — текст не перетинають)
    p.append(arrow(150 + w1 / 2, card_cy, 430 - w2 / 2, card_cy, color=INK, sw=2.0))
    p.append(arrow(430 + w2 / 2, card_cy, 720 - w3 / 2, card_cy, color=INK, sw=2.0))

    # підсумковий рядок під усім
    p.append(text(W / 2, 320,
                  "Ідея (сценарії, 1994) → перша публікація методу (1998) → зрілий метод (2000).",
                  size=13, color=INK, bold=True))
    p.append(text(W / 2, 344,
                  "Дерева корисності й не-ризиків у версії 1998 ще НЕ було — їх додала версія 2000.",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Від SAAM до ATAM: не спалах, а три кроки дозрівання")


if __name__ == "__main__":
    fig_knob()
    fig_matrix()
    fig_points()
    fig_timeline()
    print("figs done")
