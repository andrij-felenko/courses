# -*- coding: utf-8 -*-
"""
Генератор SVG для 🧮-вставки §3.6.6m — «Фрагментація кількісно: зовнішня й
внутрішня, чому embedded уникає free()» (Модуль 3, Розділ 3.6, до теми 3.6.6).

Окремий скрипт вставки (головний figs.py розділу НЕ чіпаємо). Чистий Python,
без сторонніх залежностей. Вивід → ./img/ тієї самої папки розділу.
Імена файлів унікальні: fig-19-6m-*.svg (6m = вставка до теми 3.6.6).

Стиль (AUTHORING §9): білий фон; sans-serif; стрілки через marker; зайнятий
блок — синій, вільний — зелений, втрачене (накладні/огризки) — червоне;
єдиний вигляд із рештою розділу (допоміжні функції скопійовано з figs.py).
Підписи у тексті — «Рис. 3.6.6m.k».
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

# заливки регіонів пам'яті
FILL_USED  = "#dbe4f7"   # зайнятий блок (синій)
FILL_FREE  = "#dcefe0"   # вільний шматок (зелений)
FILL_WASTE = "#f7dcd9"   # втрачене: накладні / огризок (червоний)


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


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def brace_h(x1, x2, y, color=GREY, depth=8, up=False):
    """Проста горизонтальна фігурна дужка під/над відрізком [x1,x2]."""
    mid = (x1 + x2) / 2
    d = -depth if up else depth
    tip = y + (-depth - 4 if up else depth + 4)
    return (
        f'<path d="M{x1:.1f},{y:.1f} Q{x1:.1f},{y+d:.1f} {x1+8:.1f},{y+d:.1f} '
        f'L{mid-8:.1f},{y+d:.1f} Q{mid:.1f},{y+d:.1f} {mid:.1f},{tip:.1f} '
        f'Q{mid:.1f},{y+d:.1f} {mid+8:.1f},{y+d:.1f} L{x2-8:.1f},{y+d:.1f} '
        f'Q{x2:.1f},{y+d:.1f} {x2:.1f},{y:.1f}" fill="none" stroke="{color}" stroke-width="1.4"/>\n'
    )


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.6m.1 — дві фрагментації поруч: ЗОВНІШНЯ (між блоками) vs ВНУТРІШНЯ
#                 (всередині блоку). Однакова сумарна втрата — різні механізми.
# ════════════════════════════════════════════════════════════════════════════
def fig_two_kinds():
    W, H = 940, 600
    s = header(W, H)
    s += text(W / 2, 34, "Дві фрагментації: де ховається втрачена пам'ять", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "обидві «з'їдають» RAM, але в різних місцях — і лікуються по-різному",
              12.5, GREY, "middle", style="italic")

    # ── легенда ──
    lx = 60
    ly = 78
    s += rect(lx, ly, 16, 16, FILL_USED, BLUE, 1.4, 3)
    s += text(lx + 22, ly + 13, "зайнято (корисні дані)", 12, INK, "start")
    s += rect(lx + 220, ly, 16, 16, FILL_FREE, GREEN, 1.4, 3)
    s += text(lx + 242, ly + 13, "вільно (можна видати)", 12, INK, "start")
    s += rect(lx + 440, ly, 16, 16, FILL_WASTE, RED, 1.4, 3)
    s += text(lx + 462, ly + 13, "втрачено (марно зайнято)", 12, INK, "start")

    cell = 4.6  # пікселів на байт
    # ───────────────────────── ЛІВО: ЗОВНІШНЯ ─────────────────────────
    LX = 70
    topY = 166
    s += rect(LX - 16, 118, 400, 360, "#fbfbfb", FAINT, 1.5, 12)
    s += text(LX + 184, 140, "ЗОВНІШНЯ (external)", 16, RED, "middle", "bold")

    # одна стрічка купи 128 Б: зайняті/вільні шматки врозкид
    # власний масштаб лівої панелі, щоб уся стрічка 128 Б влізла в рамку
    cellL = 2.7  # пікселів на байт (ліва панель)
    segs = [("U", 24), ("F", 18), ("U", 16), ("F", 14), ("U", 20),
            ("F", 12), ("U", 8), ("F", 16)]
    x = LX
    y = topY
    barw = sum(w for _, w in segs) * cellL
    for kind, w in segs:
        ww = w * cellL
        fill = FILL_USED if kind == "U" else FILL_FREE
        stк = BLUE if kind == "U" else GREEN
        s += rect(x, y, ww, 40, fill, stк, 1.3)
        s += text(x + ww / 2, y + 25, str(w), 11.5, INK if kind == "U" else GREEN, "middle",
                  "bold" if kind == "F" else "normal")
        x += ww
    s += text(LX, y - 10, "купа 128 Б після багатьох alloc/free:", 12, INK, "start", "bold")

    # сумарно вільно
    free_total = sum(w for k, w in segs if k == "F")
    s += brace_h(LX, LX + barw, y + 44, GREEN, 7)
    s += text(LX + barw / 2, y + 70, f"вільно сумарно: {free_total} Б — місця ніби досить",
              12, GREEN, "middle", "bold")

    # запит, що не влазить
    reqY = y + 110
    req = 40
    s += text(LX, reqY - 8, "запит malloc(40):", 12.5, INK, "start", "bold")
    s += rect(LX, reqY, req * cellL, 30, "none", RED, 2)
    s += text(LX + req * cellL / 2, reqY + 20, "40 Б поспіль", 12, RED, "middle", "bold")
    # найбільший вільний шматок
    biggest = max(w for k, w in segs if k == "F")
    s += text(LX, reqY + 58, f"найбільший суцільний вільний = {biggest} Б", 12, INK, "start")
    s += text(LX, reqY + 78, f"40 > {biggest}  →  malloc ПОВЕРТАЄ NULL,", 12.5, RED, "start", "bold")
    s += text(LX, reqY + 96, "хоча сумарно вільного більше за 40", 12, RED, "start")
    s += text(LX, reqY + 124, "Втрата = між блоками (вільне роздроблене)", 12, INK, "start", style="italic")

    # ───────────────────────── ПРАВО: ВНУТРІШНЯ ─────────────────────────
    RX = 540
    s += rect(RX - 16, 118, 400, 360, "#fbfbfb", FAINT, 1.5, 12)
    s += text(RX + 184, 140, "ВНУТРІШНЯ (internal)", 16, RED, "middle", "bold")

    # один блок: запит 30 Б, видали 48 Б (округлення + заголовок)
    s += text(RX, topY - 10, "просили 30 Б, allocator видав цілий блок:", 12, INK, "start", "bold")
    blkw = 48 * cell * 1.6
    bx = RX
    by = topY
    # заголовок 8 Б
    hdr = 8 * cell * 1.6
    s += rect(bx, by, hdr, 40, FILL_WASTE, RED, 1.3)
    s += text(bx + hdr / 2, by + 25, "8", 11, RED, "middle", "bold")
    # корисні 30 Б
    usew = 30 * cell * 1.6
    s += rect(bx + hdr, by, usew, 40, FILL_USED, BLUE, 1.3)
    s += text(bx + hdr + usew / 2, by + 25, "30", 12, INK, "middle", "bold")
    # огризок-вирівнювання 10 Б (48-30-8)
    padw = 10 * cell * 1.6
    s += rect(bx + hdr + usew, by, padw, 40, FILL_WASTE, RED, 1.3)
    s += text(bx + hdr + usew + padw / 2, by + 25, "10", 11, RED, "middle", "bold")

    s += text(bx - 2, by + 58, "8 Б", 10.5, RED, "middle")
    s += text(bx + hdr + usew / 2, by + 58, "30 Б корисних", 10.5, INK, "middle")
    s += text(bx + hdr + usew + padw / 2, by + 58, "+10 Б", 10.5, RED, "middle")
    s += brace_h(bx, bx + hdr + usew + padw, by + 64, GREY, 7)
    s += text(bx + (hdr + usew + padw) / 2, by + 90, "реально зайнято в RAM = 48 Б", 12, INK, "middle", "bold")

    # арифметика втрати
    ay = by + 122
    s += text(RX, ay, "заголовок:        8 Б (службова бухгалтерія)", 12.5, RED, "start")
    s += text(RX, ay + 22, "вирівнювання:  +10 Б (до кратного 16)", 12.5, RED, "start")
    s += line(RX, ay + 32, RX + 300, ay + 32, FAINT, 1.4)
    s += text(RX, ay + 54, "марно витрачено = 18 Б на 30 корисних", 13, RED, "start", "bold")
    s += text(RX, ay + 76, "це 18 / 48 ≈ 38 % блоку — у нікуди", 12.5, RED, "start", "bold")
    s += text(RX, ay + 104, "Втрата = всередині блоку (округлення вгору)", 12, INK, "start", style="italic")

    # нижній підсумок
    s += line(60, H - 44, W - 60, H - 44, FAINT, 1.5)
    s += text(W / 2, H - 22,
              "Зовнішня: вільне роздроблене МІЖ блоками · Внутрішня: видали БІЛЬШЕ, ніж просили — лишок гине ВСЕРЕДИНІ",
              12.5, INK, "middle", "bold")
    save("fig-19-6m-1-two-kinds.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.6m.2 — апарат внутрішньої: реальний коштує округлення до 2-степеня
#                 (binning) + заголовок. Таблиця: запит → видане → втрата.
# ════════════════════════════════════════════════════════════════════════════
def fig_internal_table():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 34, "Скільки коштує один malloc: заголовок + округлення розміру", 20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "видане = округлити(запит + заголовок) до класу розміру; внутрішня втрата = видане − запит",
              12, GREY, "middle", style="italic")

    # формула у плитці
    bx, by, bw, bh = 120, 78, 700, 56
    s += rect(bx, by, bw, bh, "#f3f6fb", BLUE, 1.8, 10)
    s += text(bx + bw / 2, by + 23, "видане = roundUp( запит + H ,  клас )      H — заголовок блоку",
              15, BLUE, "middle", "bold")
    s += text(bx + bw / 2, by + 44, "внутрішня втрата W = видане − запит        (завжди ≥ H, часто більше)",
              13.5, INK, "middle", "bold")

    # таблиця: H=8, класи — степені двійки 16,32,64,128,256...
    cols = ["запит (Б)", "+ H=8", "клас (степінь 2)", "видане (Б)", "втрата W (Б)", "W / видане"]
    cx = [70, 230, 360, 560, 700, 830]
    ty = 178
    for c, x in zip(cols, cx):
        s += text(x, ty, c, 12.5, INK, "middle" if c != cols[0] else "start", "bold")
    s += line(60, ty + 10, W - 60, ty + 10, INK, 1.4)

    def round_pow2(v):
        p = 16
        while p < v:
            p *= 2
        return p

    rows_req = [1, 12, 17, 33, 100, 130]
    H_ = 8
    y = ty + 36
    dy = 42
    for q in rows_req:
        need = q + H_
        given = round_pow2(need)
        waste = given - q
        frac = waste / given
        s += text(cx[0], y, str(q), 13.5, INK, "start", "bold")
        s += text(cx[1], y, str(need), 13, GREY, "middle")
        s += text(cx[2], y, f"→ {given}", 13, BLUE, "middle", "bold")
        s += text(cx[3], y, str(given), 13.5, BLUE, "middle", "bold")
        # стовпчик-смужка втрати
        s += text(cx[4], y, str(waste), 13.5, RED, "middle", "bold")
        # частка у відсотках + мінібар
        pct = f"{frac*100:.0f} %"
        s += text(cx[5] + 26, y, pct, 13, RED, "middle", "bold")
        barx = cx[5] - 34
        s += rect(barx, y - 11, 52, 12, "#fff", FAINT, 1)
        s += rect(barx, y - 11, 52 * frac, 12, FILL_WASTE, RED, 0)
        s += line(60, y + 12, W - 60, y + 12, FAINT, 1)
        y += dy

    # висновок під таблицею
    s += text(60, y + 24, "Читаємо тенденцію:", 13.5, INK, "start", "bold")
    s += text(60, y + 46,
              "• маленькі блоки страшні: запит 1 Б займає 16 Б — 94 % у нікуди (заголовок + округлення душать дрібноту);",
              12.5, INK, "start")
    s += text(60, y + 66,
              "• «незручні» розміри (17→32, 33→64) втрачають майже половину: трохи переступив клас — і платиш за весь наступний;",
              12.5, INK, "start")
    s += text(60, y + 86,
              "• частка W/видане падає для великих блоків — фіксований заголовок розчиняється; тому дрібні часті alloc найгірші.",
              12.5, INK, "start")
    save("fig-19-6m-2-internal-table.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.6m.3 — чому embedded уникає free(): три стратегії в часі.
#   (а) malloc/free врозкид → фрагментація росте, аж до краху;
#   (б) виділити раз на старті → стеля назавжди стала;
#   (в) пул однакових блоків → внутрішня є, зовнішньої нема, час O(1).
# ════════════════════════════════════════════════════════════════════════════
def fig_why_avoid():
    W, H = 940, 640
    s = header(W, H)
    s += text(W / 2, 34, "Чому вбудована практика уникає free(): три стратегії в часі", 20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "на МК RAM — кілобайти, а пристрій працює тижнями: потрібна СТАЛА, передбачувана пам'ять",
              12, GREY, "middle", style="italic")

    # спільна вісь часу для трьох доріжок
    def track(y0, title, color, desc):
        s_ = text(70, y0 - 10, title, 14.5, color, "start", "bold")
        s_ += text(360, y0 - 10, desc, 11.5, GREY, "start", style="italic")
        return s_

    laneW = 740
    laneX = 150
    cell = 3.0

    # ── (а) malloc/free врозкид: фрагментація наростає ──
    yA = 110
    s += track(yA, "(а) malloc + free врозкид", RED, "найбільший суцільний вільний шматок тане з часом")
    # чотири знімки в часі: суцільне → щораз дрібніше
    snaps_a = [
        [("F", 100)],
        [("U", 20), ("F", 30), ("U", 18), ("F", 32)],
        [("U", 14), ("F", 12), ("U", 22), ("F", 10), ("U", 16), ("F", 16)],
        [("U", 10), ("F", 8), ("U", 12), ("F", 7), ("U", 14), ("F", 6), ("U", 11), ("F", 7), ("U", 9), ("F", 6)],
    ]
    labels_a = ["старт", "за годину", "за день", "за тиждень"]
    sw = laneW / 4 - 20
    for i, snap in enumerate(snaps_a):
        x0 = laneX + i * (laneW / 4)
        total = sum(w for _, w in snap)
        x = x0
        for kind, w in snap:
            ww = w / total * sw
            fill = FILL_USED if kind == "U" else FILL_FREE
            stк = BLUE if kind == "U" else GREEN
            s += rect(x, yA, ww, 26, fill, stк, 1)
            x += ww
        s += text(x0 + sw / 2, yA + 42, labels_a[i], 11, GREY, "middle")
        biggest = max((w for k, w in snap if k == "F"), default=0)
        bigpct = biggest / total
        col = GREEN if bigpct > 0.5 else (AMBER if bigpct > 0.2 else RED)
        s += text(x0 + sw / 2, yA + 58, f"max вільний {int(bigpct*100)}%", 11, col, "middle", "bold")
    s += text(laneX, yA + 80, "великий запит зрештою не влазить → пристрій падає в полі, де нема кому перезапустити",
              12, RED, "start", "bold")

    # ── (б) виділити все раз на старті ──
    yB = 290
    s += track(yB, "(б) виділити все РАЗ на старті", GREEN, "межа фіксується назавжди — нема alloc/free у роботі")
    snaps_b = [("U", 70), ("F", 30)]
    for i in range(4):
        x0 = laneX + i * (laneW / 4)
        x = x0
        for kind, w in snaps_b:
            ww = w / 100 * sw
            fill = FILL_USED if kind == "U" else FILL_FREE
            stк = BLUE if kind == "U" else GREEN
            s += rect(x, yB, ww, 26, fill, stк, 1)
            x += ww
        s += text(x0 + sw / 2, yB + 42, labels_a[i], 11, GREY, "middle")
        s += text(x0 + sw / 2, yB + 58, "max вільний 30%", 11, GREEN, "middle", "bold")
    s += text(laneX, yB + 80, "картина НЕ змінюється з часом → найгірший випадок відомий ще при компіляції",
              12, GREEN, "start", "bold")

    # ── (в) пул однакових блоків ──
    yC = 470
    s += track(yC, "(в) пул блоків однакового розміру", BLUE, "зовнішньої фрагментації нема за визначенням; alloc/free — O(1)")
    # сітка однакових комірок, частина зайнята
    ncell = 20
    cw = sw * 4 / ncell * 0.92
    busy = [1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0]
    gx = laneX
    for i in range(ncell):
        fill = FILL_USED if busy[i] else FILL_FREE
        stк = BLUE if busy[i] else GREEN
        s += rect(gx + i * (cw + 3), yC, cw, 26, fill, stк, 1)
    s += text(laneX, yC + 50,
              "усі комірки однакові → будь-який вільний слот підходить будь-якому запиту; «дірок не того розміру» не буває.",
              12, BLUE, "start", "bold")
    s += text(laneX, yC + 70,
              "ціна — внутрішня фрагментація (дрібний запит у великій комірці), зате час сталий і поведінка передбачувана.",
              12, INK, "start")

    # підсумкова мораль
    s += line(60, H - 52, W - 60, H - 52, FAINT, 1.5)
    s += text(W / 2, H - 30,
              "Проблема не «free() поганий», а НЕДЕТЕРМІНІЗМ: змінний час і фрагментація, що росте. Прибери free() з робочого циклу — позбудешся обох бід.",
              12.5, INK, "middle", "bold")
    save("fig-19-6m-3-why-avoid.svg", s)


if __name__ == "__main__":
    fig_two_kinds()
    fig_internal_table()
    fig_why_avoid()
    print("ch19 §3.6.6m insert figures done.")
