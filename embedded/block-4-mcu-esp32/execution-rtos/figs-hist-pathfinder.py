# -*- coding: utf-8 -*-
"""
Фігури для вставки ch27-s6-history-pathfinder.md
«Mars Pathfinder: пріоритетна інверсія за 190 мільйонів кілометрів»

  img/fig-27-6i-1-information-bus.svg   — архітектура: шина + три задачі + м'ютекс
  img/fig-27-6i-2-priority-inversion.svg — часова діаграма інверсії + watchdog reset
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Локальні кольори ─────────────────────────────────────────────────────────
HIGH_COL  = "#c0392b"   # Висока задача (керування шиною) — червоний
MID_COL   = "#e08b00"   # Середня задача (зв'язок)        — жовтогаряча
LOW_COL   = "#2457d6"   # Низька задача (метео ASI/MET)   — синій
LOCK_COL  = "#27ae60"   # М'ютекс / замок                 — зелений
BUS_COL   = "#6c3483"   # Інформаційна шина               — пурпурний
LRED      = "#fdecea"
LYEL      = "#fff8e1"
LBLUE     = "#e8eef9"
LGRE      = "#edf7ef"
LPURP     = "#f5eef8"
LGRAY     = "#ecf0f1"
WATCH_COL = "#922b21"   # Watchdog reset — темно-червоний


# ══════════════════════════════════════════════════════════════════════════════
# Фігура 1: Архітектура інформаційної шини Pathfinder
# ══════════════════════════════════════════════════════════════════════════════
def fig1_information_bus():
    W, H = 880, 420
    parts = []

    # Заголовок
    parts.append(text(W / 2, 22, "Архітектура ПЗ Pathfinder: інформаційна шина під м'ютексом",
                      size=15, bold=True, color=INK))

    # ── Центральний елемент: спільна пам'ять — інформаційна шина ─────────────
    bus_cx, bus_cy = W / 2, H / 2 + 10
    bus_w, bus_h = 220, 80

    # Рамка шини
    parts.append(rect(bus_cx - bus_w / 2, bus_cy - bus_h / 2,
                      bus_w, bus_h, fill=LPURP, stroke=BUS_COL, sw=2.5, rx=10))
    parts.append(text(bus_cx, bus_cy - 12, "Інформаційна шина", size=13, bold=True, color=BUS_COL))
    parts.append(text(bus_cx, bus_cy + 6, "(спільна пам'ять)", size=11, color=BUS_COL))
    parts.append(text(bus_cx, bus_cy + 22, "← один м'ютекс →", size=11, color=LOCK_COL, bold=True))

    # ── Замок-значок над шиною ────────────────────────────────────────────────
    lock_cx, lock_cy = bus_cx, bus_cy - bus_h / 2 - 28
    tb_lock, lw, lh = textbox(lock_cx, lock_cy, "🔒 М'ЮТЕКС", size=13,
                               fill=LGRE, stroke=LOCK_COL, sw=2.0,
                               color=LOCK_COL, bold=True, pad=8, rx=8)
    parts.append(tb_lock)
    # стрілка від замка до шини
    parts.append(arrow(lock_cx, lock_cy + lh / 2 + 2,
                       lock_cx, bus_cy - bus_h / 2 - 2,
                       color=LOCK_COL, sw=1.8))

    # ── Три задачі ────────────────────────────────────────────────────────────
    # Позиції задач: ліворуч зверху (висока), знизу (низька), праворуч (середня)
    task_configs = [
        # (cx, cy, label_lines, bg, stroke, conn_x, conn_y)
        (150, 130, ["ВИСОКА", "Керування шиною", "(bus management)", "бере замок: часто, коротко"],
         LRED, HIGH_COL),
        (150, 310, ["НИЗЬКА", "Метеодавач ASI/MET", "(погода/вітер)", "бере замок: рідко, надовго"],
         LBLUE, LOW_COL),
        (710, H / 2 + 10, ["СЕРЕДНЯ", "Зв'язок / обробка", "(communication)", "замок НЕ бере,", "їсть CPU довго"],
         LYEL, MID_COL),
    ]

    task_boxes = []
    for cx, cy, lines, bg, col in task_configs:
        tw_est = max(len(ln) for ln in lines) * 13 * 0.57 + 24
        th_est = len(lines) * 13 * 1.3 + 16
        bx, by = cx - tw_est / 2, cy - th_est / 2
        # рамка
        parts.append(rect(bx, by, tw_est, th_est, fill=bg, stroke=col, sw=2.0, rx=8))
        # текст рядками
        ty0 = by + 16
        for i, ln in enumerate(lines):
            bold_line = (i == 0)
            parts.append(text(cx, ty0 + i * 13 * 1.3, ln,
                               size=12 if i == 0 else 11,
                               color=col if i == 0 else INK,
                               anchor="middle", bold=bold_line))
        task_boxes.append((cx, cy, tw_est, th_est, col))

    # ── З'єднання задач із шиною стрілками ───────────────────────────────────
    # Висока (ліва верхня) → шина
    hcx, hcy, htw, hth, hcol = task_boxes[0]
    # кінець рамки задачі (права сторона)
    parts.append(arrow(hcx + htw / 2, hcy,
                       bus_cx - bus_w / 2 - 2, bus_cy - 18,
                       color=HIGH_COL, sw=1.8))
    parts.append(text(hcx + htw / 2 + 45, hcy - 14,
                      "take/give", size=10, color=HIGH_COL, italic=True))

    # Низька (ліва нижня) → шина
    lcx, lcy, ltw, lth, lcol = task_boxes[1]
    parts.append(arrow(lcx + ltw / 2, lcy,
                       bus_cx - bus_w / 2 - 2, bus_cy + 18,
                       color=LOW_COL, sw=1.8))
    parts.append(text(lcx + ltw / 2 + 45, lcy + 14,
                      "take/give", size=10, color=LOW_COL, italic=True))

    # Середня (права) — не бере замок, пунктирна лінія
    mcx, mcy, mtw, mth, mcol = task_boxes[2]
    parts.append(line(mcx - mtw / 2, mcy,
                      bus_cx + bus_w / 2 + 2, bus_cy,
                      color=MID_COL, sw=1.5, dash="6 4"))
    parts.append(text(mcx - mtw / 2 - 52, mcy - 14,
                      "не бере замок", size=10, color=MID_COL, italic=True))

    # ── Підказка «пастка» ─────────────────────────────────────────────────────
    trap_cx, trap_cy = W / 2, H - 30
    tb_trap, trtw, trth = textbox(trap_cx, trap_cy,
        "Пастка: висока і низька ділять один замок, середня тисне CPU — трикутник ризику",
        size=11, fill="#fef9e7", stroke="#c0960c", sw=1.6,
        color="#7d6608", bold=False, pad=8, rx=7)
    parts.append(tb_trap)

    path = os.path.join(OUT, "fig-27-6i-1-information-bus.svg")
    render(path, W, H, *parts,
           title=None)
    print("wrote", os.path.basename(path))


# ══════════════════════════════════════════════════════════════════════════════
# Фігура 2: Часова діаграма пріоритетної інверсії + watchdog reset
# ══════════════════════════════════════════════════════════════════════════════
def fig2_priority_inversion():
    W, H = 980, 370
    TRACK_H   = 52
    TRACK_GAP = 14
    LABEL_W   = 110
    AXIS_Y    = H - 44
    T0        = LABEL_W + 14
    T_END     = W - 22
    TW        = T_END - T0
    TRACK_TOP = 36

    def track_y(i):
        return TRACK_TOP + i * (TRACK_H + TRACK_GAP)

    def tx(frac):
        return T0 + frac * TW

    LRED2   = "#fdecea"
    LGRAY2  = "#ecf0f1"

    parts = []

    # Заголовок
    parts.append(text(W / 2, 20, "Пріоритетна інверсія на Pathfinder: три доріжки, один замок",
                      size=15, bold=True, color=INK))

    # ── Підписи доріжок ───────────────────────────────────────────────────────
    rows = [
        ("ВИСОКА\n(шина)", HIGH_COL, LRED),
        ("СЕРЕДНЯ\n(зв'язок)", MID_COL, LYEL),
        ("НИЗЬКА\n(метео)", LOW_COL, LBLUE),
    ]
    for i, (lbl, col, bg) in enumerate(rows):
        tb, tbw, tbh = textbox(LABEL_W / 2, track_y(i) + TRACK_H / 2,
                                lbl, size=11, fill=bg, stroke=col, sw=1.6,
                                color=col, bold=True, min_w=96, pad=6, rx=6)
        parts.append(tb)

    # ── Ключові моменти часу ──────────────────────────────────────────────────
    # t0 = 0.00 — низька бере замок
    # t1 = 0.14 — висока прокидається, блокується на замку
    # t2 = 0.22 — середня прокидається, витісняє низьку
    # t3 = 0.68 — середня завершує (після тривалої роботи)
    # t4 = 0.76 — низька відновлюється, завершує критичну секцію, дає замок
    # t5 = 0.83 — watchdog спрацьовує (висока не вкладалась у дедлайн)
    # t6 = 1.00 — кінець

    t = [tx(f) for f in [0.00, 0.14, 0.22, 0.68, 0.76, 0.83, 1.00]]

    # ── ROW 2: Низька (метео) ─────────────────────────────────────────────────
    # 0→t0: низька до замка
    bw = t[1] - T0
    # ідлова лінія до взяття замка
    my2 = track_y(2) + TRACK_H // 2
    parts.append(line(T0, my2, t[0], my2, color=LOW_COL, sw=1.2, dash="4 4"))
    # t0→t2: низька у критичній секції (тримає замок)
    parts.append(rect(t[0], track_y(2) + 8, t[2] - t[0], TRACK_H - 16,
                      fill="#c5d9f8", stroke=LOW_COL, sw=1.6, rx=4))
    parts.append(text((t[0] + t[2]) / 2, track_y(2) + TRACK_H / 2 + 4,
                      "Н: крит. секція 🔒", size=10, color=LOW_COL, anchor="middle", bold=True))
    # t2→t3: низька ЗУПИНЕНА (витіснена середньою)
    parts.append(rect(t[2], track_y(2) + 12, t[3] - t[2], TRACK_H - 24,
                      fill=LGRAY2, stroke="#aaa", sw=1.2, rx=3))
    parts.append(text((t[2] + t[3]) / 2, track_y(2) + TRACK_H / 2 + 4,
                      "Н: зупинена (витіснена С)", size=10, color="#666", anchor="middle", italic=True))
    # t3→t4: низька відновлюється, завершує і дає замок
    parts.append(rect(t[3], track_y(2) + 8, t[4] - t[3], TRACK_H - 16,
                      fill="#d5eef6", stroke=LOW_COL, sw=1.6, rx=4))
    parts.append(text((t[3] + t[4]) / 2, track_y(2) + TRACK_H / 2 + 4,
                      "Н: дає замок 🔓", size=10, color=LOW_COL, anchor="middle", bold=True))
    # t4→end: idle
    parts.append(line(t[4], my2, T_END, my2, color=LOW_COL, sw=1.2, dash="4 4"))

    # ── ROW 1: Середня (зв'язок) ─────────────────────────────────────────────
    my1 = track_y(1) + TRACK_H // 2
    # 0→t2: середня спить
    parts.append(line(T0, my1, t[2], my1, color=MID_COL, sw=1.2, dash="4 4"))
    # t2→t3: середня БІГАЄ (витісняє низьку, не торкаючись замка)
    parts.append(rect(t[2], track_y(1) + 8, t[3] - t[2], TRACK_H - 16,
                      fill=LYEL, stroke=MID_COL, sw=1.6, rx=4))
    parts.append(text((t[2] + t[3]) / 2, track_y(1) + TRACK_H / 2 + 4,
                      "С: виконується (замок не бере, їсть CPU)", size=10, color=MID_COL, anchor="middle", bold=True))
    # t3→end: середня idle
    parts.append(line(t[3], my1, T_END, my1, color=MID_COL, sw=1.2, dash="4 4"))

    # ── ROW 0: Висока (шина) ─────────────────────────────────────────────────
    my0 = track_y(0) + TRACK_H // 2
    # 0→t1: висока спить
    parts.append(line(T0, my0, t[1], my0, color=HIGH_COL, sw=1.2, dash="4 4"))
    # t1→t4: висока заблокована на замку (чекає замок, що тримає низька, яку заблокувала середня)
    parts.append(rect(t[1], track_y(0) + 10, t[4] - t[1], TRACK_H - 20,
                      fill=LRED2, stroke=HIGH_COL, sw=1.6, rx=4))
    parts.append(text((t[1] + t[4]) / 2, track_y(0) + TRACK_H / 2 + 4,
                      "В: чекає замку... (блокована)", size=11, color=HIGH_COL, anchor="middle", italic=True))
    # t4→t5: висока нарешті отримала замок, але — watchdog вже спрацьовує!
    parts.append(rect(t[4], track_y(0) + 8, t[5] - t[4], TRACK_H - 16,
                      fill=LRED, stroke=HIGH_COL, sw=1.6, rx=4))
    parts.append(text((t[4] + t[5]) / 2, track_y(0) + TRACK_H / 2 + 4,
                      "В: щойно взяла замок", size=10, color=HIGH_COL, anchor="middle"))

    # ── Watchdog: вертикальна смуга «RESET» ──────────────────────────────────
    wd_x = t[5]
    parts.append(rect(wd_x - 2, TRACK_TOP - 4, 44, AXIS_Y - TRACK_TOP + 4,
                      fill="#fdedec", stroke=WATCH_COL, sw=2.2, rx=3))
    parts.append(text(wd_x + 20, TRACK_TOP + 12, "⚠", size=14, color=WATCH_COL, anchor="middle"))
    parts.append(mtext(wd_x + 20, TRACK_TOP + 28, ["WATCH-", "DOG", "RESET"],
                       size=9, color=WATCH_COL, anchor="middle", bold=True))

    # ── Стрілка-підпис «Висока чекає на Середню» ─────────────────────────────
    ann_cx = (t[2] + t[3]) / 2
    ann_top = track_y(0) + TRACK_H + 8
    ann_bot = AXIS_Y - 56

    tb_ann, ann_w, ann_h = textbox(
        ann_cx, ann_bot,
        "В фактично чекає на С\n(інверсія пріоритетів!)\nВисока < Середня фактично",
        size=11, fill="#fef0f0", stroke=HIGH_COL, sw=1.8,
        color=HIGH_COL, bold=False, pad=8, rx=7)
    parts.append(tb_ann)
    parts.append(arrow(ann_cx, ann_top, ann_cx, ann_bot - ann_h / 2 - 2, color=HIGH_COL, sw=1.6))

    # ── Позначки часу на осі ─────────────────────────────────────────────────
    marks = [
        (t[0], "Н бере\nзамок"),
        (t[1], "В проки-\nдається,\nблокується"),
        (t[2], "С вит-\nісняє Н"),
        (t[3], "С зав-\nершила"),
        (t[4], "Н дає\nзамок"),
        (t[5], "Watchdog\nRESET"),
    ]
    for tx_pos, lbl in marks:
        col = WATCH_COL if "Watchdog" in lbl else MUTED
        parts.append(line(tx_pos, TRACK_TOP, tx_pos, AXIS_Y - 6, color=col, sw=1.0, dash="3 4"))
        parts.append(mtext(tx_pos, AXIS_Y + 6, lbl.split("\n"),
                           size=9, color=col, anchor="middle"))

    # Вісь часу
    parts.append(arrow(T0, AXIS_Y, T_END, AXIS_Y, color=MUTED, sw=1.4))
    parts.append(text(T_END - 16, AXIS_Y - 8, "час →", size=11, color=MUTED, anchor="end"))

    path = os.path.join(OUT, "fig-27-6i-2-priority-inversion.svg")
    render(path, W, H, *parts, title=None)
    print("wrote", os.path.basename(path))


if __name__ == "__main__":
    fig1_information_bus()
    fig2_priority_inversion()
