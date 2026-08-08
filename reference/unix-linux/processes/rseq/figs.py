# -*- coding: utf-8 -*-
"""Фігури до теми «Перезапускні послідовності (rseq)»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG = "#fdecea"
BLUE_BG = "#eaf0fd"
GREY_BG = "#eef0f3"
WARM_BG = "#fff4e0"


# ── 1. Спільна табличка й дескриптор ────────────────────────────────────────
def fig_area():
    W, H = 1420, 800
    P = []

    P.append(text(W / 2, 40, "Що лежить у пам'яті: табличка потоку, дескриптор і код",
                  size=18, bold=True))

    # ── табличка потоку ──
    ax, ay, aw = 70, 120, 330
    P.append(text(ax + aw / 2, ay - 42, "struct rseq", size=15, bold=True))
    P.append(text(ax + aw / 2, ay - 20, "у локальній пам'яті потоку", size=12.5, color=MUTED))

    rows = [
        ("cpu_id_start", "ядро", BLUE_BG, NEG),
        ("cpu_id", "ядро", BLUE_BG, NEG),
        ("rseq_cs", "програма", GREEN_BG, FIELD),
        ("flags", "—", GREY_BG, MUTED),
        ("node_id", "ядро", BLUE_BG, NEG),
        ("mm_cid", "ядро", BLUE_BG, NEG),
    ]
    rh, gap = 54, 14
    ry = ay
    row_y = {}
    for name, who, bg, st in rows:
        P.append(fitbox(ax, ry, aw - 120, rh, name, size=14, fill=bg, stroke=st))
        P.append(text(ax + aw - 108, ry + rh / 2 + 5, "пише " + who, size=12,
                      color=st, anchor="start"))
        row_y[name] = ry + rh / 2
        ry += rh + gap

    # ── дескриптор ділянки ──
    dx, dy, dw = 560, 150, 320
    P.append(text(dx + dw / 2, dy - 42, "struct rseq_cs", size=15, bold=True))
    P.append(text(dx + dw / 2, dy - 20, "стала в окремій секції", size=12.5, color=MUTED))

    drows = ["version", "flags", "start_ip", "post_commit_offset", "abort_ip"]
    dy_pos = {}
    ry = dy
    for name in drows:
        hot = name in ("start_ip", "post_commit_offset", "abort_ip")
        P.append(fitbox(dx, ry, dw, rh, name, size=13.5,
                        fill=WARM_BG if hot else GREY_BG,
                        stroke=POS if hot else MUTED))
        dy_pos[name] = ry + rh / 2
        ry += rh + gap

    # стрілка табличка → дескриптор
    P.append(arrow(ax + aw - 6, row_y["rseq_cs"], dx - 14, dy_pos["version"] - 30,
                   color=FIELD, sw=2))
    P.append(text((ax + aw + dx) / 2 - 10, row_y["rseq_cs"] - 26,
                  "вказівник на активну ділянку", size=12.5, color=FIELD))

    # ── код ──
    cx, cy, cw = 1040, 132, 300
    P.append(text(cx + cw / 2, cy - 42, "код програми", size=15, bold=True))
    P.append(text(cx + cw / 2, cy - 20, "адреси зростають униз", size=12.5, color=MUTED))

    lines = [
        ("оголошення ділянки", False),
        ("читання cpu_id_start", True),
        ("читання лічильника", True),
        ("додати одиницю", True),
        ("завершальний запис", True),
        ("далі звичайний код", False),
        ("підпис 0x53053053", False),
        ("обробник зриву", False),
    ]
    lh = 52
    ly = cy
    ypos = []
    for label, inside in lines:
        P.append(fitbox(cx, ly, cw, 42, label, size=12.5,
                        fill=RED_BG if inside else BG,
                        stroke=POS if inside else MUTED))
        ypos.append(ly)
        ly += lh

    # дужка діапазону ділянки
    top = ypos[1] - 6
    bot = ypos[4] + 48
    bx = cx - 26
    P.append(line(bx, top, bx, bot, color=POS, sw=2.5))
    P.append(line(bx, top, bx + 16, top, color=POS, sw=2.5))
    P.append(line(bx, bot, bx + 16, bot, color=POS, sw=2.5))

    # стрілки від полів дескриптора до коду
    P.append(arrow(dx + dw + 8, dy_pos["start_ip"], bx - 8, top + 4, color=POS, sw=1.6))
    P.append(arrow(dx + dw + 8, dy_pos["abort_ip"], cx - 8, ypos[7] + 20, color=POS, sw=1.6))
    P.append(text(dx + dw + 22, dy_pos["post_commit_offset"] + 34,
                  "довжина діапазону", size=12, color=POS, anchor="start"))

    P.append(mtext(W / 2, H - 46,
                   ["Ядро читає дескриптор лише тоді, коли задача вже спинена,",
                    "тому запис вказівника в табличку не потребує ані префікса lock, ані бар'єра."],
                   size=13, color=MUTED, lh=1.4))
    render(os.path.join(OUT, "rseq-area.svg"), W, H, *P,
           title="Табличка rseq, дескриптор ділянки й код")


# ── 2. Дві історії однієї ділянки ───────────────────────────────────────────
def fig_timeline():
    W, H = 1400, 720
    P = []

    P.append(text(W / 2, 40, "Одна й та сама ділянка: витіснення до завершального запису й після",
                  size=18, bold=True))

    steps = ["читання\ncpu_id_start", "читання\nлічильника", "додати\nодиницю", "ЗАВЕРШАЛЬНИЙ\nЗАПИС"]
    bw, bgap = 250, 26
    x0 = 130

    def strip(y, cut_index, caption, verdict, vcolor, vbg):
        out = []
        out.append(text(70, y - 54, caption, size=15, bold=True, anchor="start"))
        for i, s in enumerate(steps):
            x = x0 + i * (bw + bgap)
            out.append(fitbox(x, y, bw, 74, s, size=12.5, fill=RED_BG, stroke=POS))
        # межі діапазону
        left = x0 - 12
        right = x0 + 4 * bw + 3 * bgap + 12
        out.append(line(left, y - 22, left, y + 96, color=POS, sw=2, dash="5,4"))
        out.append(line(right, y - 22, right, y + 96, color=POS, sw=2, dash="5,4"))
        out.append(text(left, y - 32, "start_ip", size=12, color=POS))
        out.append(text(right, y - 32, "кінець діапазону", size=12, color=POS))
        # місце удару
        if cut_index < 4:
            hx = x0 + cut_index * (bw + bgap) - bgap / 2
        else:
            hx = right + 90
        out.append(line(hx, y - 14, hx, y + 88, color=NEG, sw=3))
        out.append(text(hx, y - 26, "витіснення", size=12.5, color=NEG, bold=True))
        # вирок
        vx = right + 40
        box, bwv, bhv = textbox(vx + 190, y + 38, verdict, size=13, fill=vbg, stroke=vcolor,
                                color=vcolor, min_w=340)
        out.append(box)
        return out

    P += strip(150, 2,
               "Урвали посеред ділянки",
               "лічильник команд у діапазоні\n→ ядро ставить його на abort_ip\n→ у пам'яті не змінилося нічого",
               POS, RED_BG)

    P += strip(430, 4,
               "Урвали після завершального запису",
               "лічильник команд поза діапазоном\n→ ядро не робить нічого\n→ результат уже в пам'яті",
               FIELD, GREEN_BG)

    # стрілка повернення на початок для першого випадку
    P.append(arrow(x0 + 40, 262, x0 + 40, 232, color=POS, sw=2))
    P.append(line(x0 + 40, 262, 1180, 262, color=POS, sw=2))
    P.append(text(660, 284, "обробник зриву повертає виконання на початок ділянки",
                  size=13, color=POS))

    P.append(mtext(W / 2, H - 130,
                   ["Третього випадку немає: результат публікує один-єдиний запис,",
                    "і побачити його наполовину неможливо."],
                   size=13.5, color=MUTED, lh=1.4))
    render(os.path.join(OUT, "rseq-timeline.svg"), W, H, *P,
           title="Витіснення до й після завершального запису")


# ── 3. Номер ядра проти номера конкурентності ───────────────────────────────
def fig_cid():
    W, H = 1360, 620
    P = []

    P.append(text(W / 2, 40, "Програма з чотирьох потоків на машині з 256 ядрами процесора",
                  size=18, bold=True))

    used_cpu = {3, 71, 140, 233}
    shown = [0, 1, 2, 3, 4, "…", 70, 71, 72, "…", 140, "…", 233, "…", 255]

    # ── індексування за cpu_id ──
    ly, lx = 150, 80
    P.append(text(lx, ly - 46, "індекс — номер ядра процесора (cpu_id)", size=15, bold=True,
                  anchor="start"))
    P.append(text(lx, ly - 22, "таблиця мусить мати 256 комірок, зайнято 4",
                  size=12.5, color=MUTED, anchor="start"))
    cw, cg = 74, 10
    for i, v in enumerate(shown):
        x = lx + i * (cw + cg)
        if v == "…":
            P.append(text(x + cw / 2, ly + 40, "…", size=20, color=MUTED))
            continue
        hot = v in used_cpu
        P.append(fitbox(x, ly, cw, 64, str(v), size=13,
                        fill=GREEN_BG if hot else BG,
                        stroke=FIELD if hot else MUTED))
    P.append(text(lx, ly + 106, "252 комірки ніколи не будуть використані",
                  size=13, color=POS, anchor="start"))

    # ── індексування за mm_cid ──
    ry = 380
    P.append(text(lx, ry - 46, "індекс — номер конкурентності в межах програми (mm_cid)",
                  size=15, bold=True, anchor="start"))
    P.append(text(lx, ry - 22, "таблиця має 4 комірки, зайнято 4",
                  size=12.5, color=MUTED, anchor="start"))
    for i in range(4):
        x = lx + i * (cw + cg)
        P.append(fitbox(x, ry, cw, 64, str(i), size=13, fill=GREEN_BG, stroke=FIELD))
    P.append(text(lx + 4 * (cw + cg) + 24, ry + 40,
                  "межа — менше з двох: кількість потоків і кількість дозволених ядер",
                  size=13, color=FIELD, anchor="start"))

    P.append(text(W / 2, H - 40,
                  "Обидва номери підтримує ядро й змінює лише воно — гарантії перезапуску однакові.",
                  size=13, color=MUTED))
    render(os.path.join(OUT, "rseq-cid.svg"), W, H, *P,
           title="cpu_id проти mm_cid")


# ── 4. Побайтова розкладка struct rseq і правило розширення ─────────────────
def fig_layout():
    W, H = 1300, 580
    P = []

    P.append(text(W / 2, 44, "Побайтова розкладка struct rseq: розмір, ознака можливостей, вирівнювання",
                  size=17, bold=True))
    P.append(text(W / 2, 74, "синє — пише ядро   ·   зелене — пише програма   ·   сіре — не використовується",
                  size=12.5, color=MUTED))

    x0, y0, bh = 74, 190, 62
    px = 36.0                      # пікселів на байт

    fields = [
        (0, 4, "cpu_id_start", BLUE_BG, NEG),
        (4, 4, "cpu_id", BLUE_BG, NEG),
        (8, 8, "rseq_cs", GREEN_BG, FIELD),
        (16, 4, "flags", GREY_BG, MUTED),
        (20, 4, "node_id", BLUE_BG, NEG),
        (24, 4, "mm_cid", BLUE_BG, NEG),
        (28, 4, "доповнення", GREY_BG, MUTED),
    ]
    for off, ln, name, bg, st in fields:
        P.append(fitbox(x0 + off * px, y0, ln * px, bh, name, size=13, fill=bg, stroke=st))

    for off in (0, 4, 8, 16, 20, 24, 28, 32):
        x = x0 + off * px
        P.append(line(x, y0 - 26, x, y0 - 8, color=MUTED, sw=1.2))
        P.append(text(x, y0 - 36, str(off), size=12, color=MUTED))
    P.append(text(x0 - 44, y0 - 36, "байт", size=12, color=MUTED, anchor="start"))

    def span(y, upto, label, color):
        xa, xb = x0, x0 + upto * px
        P.append(line(xa, y, xb, y, color=color, sw=2.2))
        P.append(line(xa, y - 9, xa, y + 9, color=color, sw=2.2))
        P.append(line(xb, y - 9, xb, y + 9, color=color, sw=2.2))
        P.append(text((xa + xb) / 2, y + 30, label, size=13, color=color))

    span(320, 20, "20 байтів — вихідний склад полів, Linux 4.18", NEG)
    span(396, 28, "28 байтів — з Linux 6.3, стільки повідомляє AT_RSEQ_FEATURE_SIZE", FIELD)
    span(472, 32, "32 байти — sizeof(struct rseq) і AT_RSEQ_ALIGN: саме стільки вимагає rseq_len", POS)

    P.append(text(W / 2, H - 32,
                  "Виклик реєстрації міряє довжину в байтах, а не в полях: rseq_len ≥ 32 завжди, "
                  "а скільки полів насправді підтримано — каже допоміжний вектор.",
                  size=12.5, color=MUTED))
    render(os.path.join(OUT, "rseq-layout.svg"), W, H, *P,
           title="Розкладка struct rseq у байтах")


# ── 5. Три способи полічити те саме: з чого складається ціна ────────────────
def fig_cost():
    W, H = 1440, 760
    P = []

    P.append(text(W / 2, 40, "Та сама робота трьома способами: звідки береться різниця",
                  size=18, bold=True))

    C_PLAIN, C_LOCK, C_MOVE = "#cfd4da", "#a8bff0", "#f0a6a0"

    panels = [
        {
            "head": "один спільний лічильник",
            "sub": "атомарний приріст, префікс lock",
            "split": False,
            "bar": [(70, C_PLAIN, MUTED), (110, C_LOCK, NEG), (190, C_MOVE, POS)],
            "why": ["рядок кеша по черзі належить",
                    "кожному ядру; приріст чекає,",
                    "доки рядок приїде до нього"],
        },
        {
            "head": "лічильник на кожне ядро",
            "sub": "атомарний приріст, префікс lock",
            "split": True,
            "bar": [(70, C_PLAIN, MUTED), (110, C_LOCK, NEG)],
            "why": ["мандрів нема — рядок нікуди",
                    "не їде; але процесор усе одно",
                    "бере його у виключне володіння"],
        },
        {
            "head": "лічильник на кожне ядро",
            "sub": "перезапускна ділянка, без префікса",
            "split": True,
            "bar": [(70, C_PLAIN, MUTED)],
            "why": ["читання, додавання й запис —",
                    "звичайні команди; платимо лише",
                    "рідкісним перезапуском"],
        },
    ]

    pw, pgap = 430, 40
    x0 = (W - (3 * pw + 2 * pgap)) / 2

    cw, cgap, ch = 84, 14, 44
    row_w = 4 * cw + 3 * cgap
    cx_off = (pw - row_w) / 2

    for k, p in enumerate(panels):
        px = x0 + k * (pw + pgap)
        P.append(rect(px, 78, pw, 542, fill=BG, stroke="#d5d8dd", sw=1.2, rx=10))

        P.append(text(px + pw / 2, 112, p["head"], size=14.5, bold=True))
        P.append(text(px + pw / 2, 136, p["sub"], size=12.5, color=MUTED))

        cy = 162
        cxs = []
        for i in range(4):
            cx = px + cx_off + i * (cw + cgap)
            cxs.append(cx + cw / 2)
            P.append(fitbox(cx, cy, cw, ch, "ядро %d" % i, size=12, fill=GREY_BG, stroke=MUTED))

        my, mh = 272, 48
        if p["split"]:
            for i in range(4):
                mx = px + cx_off + i * (cw + cgap)
                P.append(rect(mx, my, cw, mh, fill=GREEN_BG, stroke=FIELD, sw=1.5))
                P.append(arrow(cxs[i], cy + ch + 5, cxs[i], my - 7, color=FIELD, sw=1.7))
            P.append(text(px + pw / 2, my + mh + 28, "свій рядок кеша в кожного",
                          size=12.5, color=FIELD))
        else:
            mx = px + cx_off
            P.append(rect(mx, my, row_w, mh, fill=RED_BG, stroke=POS, sw=1.5))
            for i in range(4):
                P.append(arrow(cxs[i], cy + ch + 5, px + pw / 2, my - 7, color=POS, sw=1.7))
            P.append(text(px + pw / 2, my + mh + 28, "один рядок кеша на всіх",
                          size=12.5, color=POS))

        P.append(mtext(px + pw / 2, 386, p["why"], size=12.5, lh=1.45))

        P.append(text(px + pw / 2, 470, "з чого складається один приріст", size=12.5,
                      color=MUTED))
        total = sum(w for w, _, _ in p["bar"])
        bx = px + (pw - total) / 2
        for w, fill, st in p["bar"]:
            P.append(rect(bx, 488, w, 36, fill=fill, stroke=st, sw=1.4, rx=4))
            bx += w

        P.append(text(px + pw / 2, 580, ["найдорожче", "дешевше", "найдешевше"][k],
                      size=13, bold=True, color=[POS, MUTED, FIELD][k]))

    keys = [("звичайні команди", C_PLAIN, MUTED),
            ("префікс lock: виключне володіння рядком і очікування", C_LOCK, NEG),
            ("передача рядка кеша між ядрами", C_MOVE, POS)]
    ly, lx = 668, 110
    for label, fill, st in keys:
        P.append(rect(lx, ly - 13, 26, 18, fill=fill, stroke=st, sw=1.3, rx=3))
        P.append(text(lx + 36, ly + 2, label, size=12.5, anchor="start"))
        lx += 46 + text_width(label, 12.5) + 44

    P.append(text(W / 2, 722,
                  "Ширина смуг — якісна: вона показує склад ціни, а не виміряні наносекунди.",
                  size=12.5, color=MUTED))

    render(os.path.join(OUT, "rseq-cost.svg"), W, H, *P,
           title="Спільний атомарний лічильник, атомарний по ядрах і rseq")


fig_area()
fig_timeline()
fig_cid()
fig_layout()
fig_cost()
print("ok")
