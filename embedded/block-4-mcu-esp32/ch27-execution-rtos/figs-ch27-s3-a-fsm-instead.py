# -*- coding: utf-8 -*-
"""
Фігури для вставки ch27-s3-a-fsm-instead — «Скінченний автомат замість задачі».
Рис. 4.10.3a.1 — діаграма станів контролера послідовності (Idle/Purge/Running/Cooldown).
Рис. 4.10.3a.2 — ваги: FSM vs задача RTOS (опційна).
Вивід → ./img/
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ═════════════════════════════════════════════════════════════════════════════
# Рис. 4.10.3a.1 — діаграма станів: Idle / Purge / Running / Cooldown
# ═════════════════════════════════════════════════════════════════════════════

def fig_state_diagram():
    W, H = 820, 520

    # Кольори
    CLR_IDLE    = "#2457d6"   # синій
    CLR_PURGE   = "#c0392b"   # червоний
    CLR_RUNNING = "#27ae60"   # зелений
    CLR_COOL    = "#7a4fb0"   # фіолетовий

    FILL_IDLE    = "#e8eefb"
    FILL_PURGE   = "#fdecea"
    FILL_RUNNING = "#eef6ef"
    FILL_COOL    = "#efe9f7"

    R = 46  # радіус кола стану

    # Позиції станів (cx, cy)
    pos = {
        "Idle":     (160, 180),
        "Purge":    (580, 180),
        "Running":  (580, 370),
        "Cooldown": (160, 370),
    }
    clrs = {
        "Idle":     (CLR_IDLE,    FILL_IDLE),
        "Purge":    (CLR_PURGE,   FILL_PURGE),
        "Running":  (CLR_RUNNING, FILL_RUNNING),
        "Cooldown": (CLR_COOL,    FILL_COOL),
    }
    labels = {
        "Idle":     ["Idle", "(очікування)"],
        "Purge":    ["Purge", "(продувка)"],
        "Running":  ["Running", "(робота)"],
        "Cooldown": ["Cooldown", "(охолодження)"],
    }

    frags = []

    # Заголовок і підзаголовок
    frags.append(text(W/2, 30, "Діаграма станів: контролер послідовності", 18, INK, "middle", bold=True))
    frags.append(text(W/2, 52, "один пристрій — чотири чіткі режими; переходи керуються кнопкою й таймером", 11, MUTED, "middle"))

    # Допоміжна функція: стрілка між двома точами
    def arrow_between(ax, ay, bx, by, color=LINE, sw=2.0):
        # коротимо трохи, щоб стрілка не влазила в коло
        dx, dy = bx - ax, by - ay
        dist = math.hypot(dx, dy)
        ux, uy = dx/dist, dy/dist
        x1 = ax + ux * (R + 4)
        y1 = ay + uy * (R + 4)
        x2 = bx - ux * (R + 8)
        y2 = by - uy * (R + 8)
        return arrow(x1, y1, x2, y2, color, sw)

    # Малюємо переходи (стрілки між станами)
    # Idle → Purge  (горизонтально вправо)
    ix, iy = pos["Idle"]
    px, py = pos["Purge"]
    rx, ry = pos["Running"]
    cx, cy_ = pos["Cooldown"]

    # Idle → Purge (горизонтально)
    frags.append(arrow_between(ix, iy, px, py, CLR_IDLE, 2.2))
    # підпис
    tb, _, _ = textbox((ix+px)//2, iy - 28, "кнопку натиснуто\n(buttonPressed)", size=11,
                        fill="#fffbe8", stroke=CLR_IDLE, sw=1.2, color=CLR_IDLE)
    frags.append(tb)

    # Purge → Running (вертикально вниз)
    frags.append(arrow_between(px, py, rx, ry, CLR_PURGE, 2.2))
    tb2, _, _ = textbox(px + 110, (py+ry)//2, "минуло 2 с\n(PURGE_MS)", size=11,
                         fill=FILL_PURGE, stroke=CLR_PURGE, sw=1.2, color=CLR_PURGE)
    frags.append(tb2)

    # Running → Cooldown (горизонтально вліво)
    frags.append(arrow_between(rx, ry, cx, cy_, CLR_RUNNING, 2.2))
    tb3, _, _ = textbox((rx+cx)//2, ry + 30, "кнопку натиснуто\n(buttonPressed)", size=11,
                         fill=FILL_RUNNING, stroke=CLR_RUNNING, sw=1.2, color=CLR_RUNNING)
    frags.append(tb3)

    # Cooldown → Idle (вертикально вгору)
    frags.append(arrow_between(cx, cy_, ix, iy, CLR_COOL, 2.2))
    tb4, _, _ = textbox(cx - 120, (cy_+iy)//2, "минуло 3 с\n(COOLDOWN_MS)", size=11,
                         fill=FILL_COOL, stroke=CLR_COOL, sw=1.2, color=CLR_COOL)
    frags.append(tb4)

    # Кола станів (поверх стрілок)
    for name, (sx, sy) in pos.items():
        col, fill = clrs[name]
        frags.append(circle(sx, sy, R, fill=fill, stroke=col, sw=2.5))
        lns = labels[name]
        frags.append(text(sx, sy - 4, lns[0], 13, col, "middle", bold=True))
        frags.append(text(sx, sy + 14, lns[1], 10, MUTED, "middle"))

    # Дії кожного стану (fitbox під колом)
    actions = {
        "Idle":     "чекає кнопку",
        "Purge":    "VALVE=LOW (2 с)",
        "Running":  "PUMP=HIGH",
        "Cooldown": "PUMP=LOW (3 с)",
    }
    for name, act in actions.items():
        sx, sy = pos[name]
        col, _ = clrs[name]
        frags.append(fitbox(sx - 70, sy + R + 6, 140, 26, act, size=11,
                            fill="#f4f6f8", stroke=col, sw=1.0, color=col))

    # Початкова точка (маленьке заповнене коло → Idle)
    frags.append(circle(60, iy, 10, fill=INK, stroke=INK, sw=1))
    frags.append(arrow(70, iy, ix - R - 4, iy, INK, 2.0))
    frags.append(text(65, iy - 16, "start", 10, MUTED, "middle"))

    # Підпис
    frags.append(fitbox(120, H - 44, W - 240, 34,
                        "Вся «складність» — 4 стани і 4 переходи. Порівняйте з діаграмою рис. 4.10.2.4.",
                        size=11, fill="#eef6ef", stroke=FIELD, sw=1.2, color=FIELD))

    render(os.path.join(OUT, "fig-27-3a-1-state-diagram.svg"), W, H, *frags,
           title=None)
    print("wrote fig-27-3a-1-state-diagram.svg")


# ═════════════════════════════════════════════════════════════════════════════
# Рис. 4.10.3a.2 — ваги: FSM vs задача RTOS
# ═════════════════════════════════════════════════════════════════════════════

def fig_fsm_vs_task():
    W, H = 820, 460

    CLR_FSM  = "#27ae60"
    CLR_RTOS = "#c0392b"
    FILL_FSM  = "#eef6ef"
    FILL_RTOS = "#fdecea"

    frags = []

    frags.append(text(W/2, 30, "Коли FSM простіший за задачу RTOS", 18, INK, "middle", bold=True))
    frags.append(text(W/2, 52, "один критерій: одна послідовна справа → автомат; багато незалежних → задачі", 11, MUTED, "middle"))

    # ── Ліва чаша: FSM ────────────────────────────────────────────────────────
    lx = 60
    frags.append(fitbox(lx, 70, 320, 40, "⬤  Скінченний автомат (FSM)", size=14,
                        fill=FILL_FSM, stroke=CLR_FSM, sw=2.0, color=CLR_FSM, bold=True))

    fsm_pros = [
        "✓  Одна змінна state + мітка t0",
        "✓  Живе у звичайному loop()",
        "✓  Жодного власного стека",
        "✓  Немає планувальника / гонок",
        "✓  Одна послідовна справа",
    ]
    y = 122
    for line_txt in fsm_pros:
        tb, _, _ = textbox(lx + 160, y, line_txt, size=12,
                           fill=FILL_FSM, stroke=CLR_FSM, sw=0.8, color=INK, min_w=310)
        frags.append(tb)
        y += 36

    # ── Права чаша: RTOS задача ───────────────────────────────────────────────
    rx = 440
    frags.append(fitbox(rx, 70, 320, 40, "⬤  Задача RTOS (FreeRTOS)", size=14,
                        fill=FILL_RTOS, stroke=CLR_RTOS, sw=2.0, color=CLR_RTOS, bold=True))

    rtos_items = [
        "＋ Власний стек (§4.10.7)",
        "＋ Планувальник (§4.10.4)",
        "＋ Черги / м'ютекси (§4.10.6)",
        "＋ Ризик гонок між задачами",
        "＋ Кілька незалежних справ",
    ]
    y = 122
    for line_txt in rtos_items:
        tb, _, _ = textbox(rx + 160, y, line_txt, size=12,
                           fill=FILL_RTOS, stroke=CLR_RTOS, sw=0.8, color=INK, min_w=310)
        frags.append(tb)
        y += 36

    # ── Стрілка-критерій ──────────────────────────────────────────────────────
    frags.append(line(410, 80, 410, 310, LINE, sw=1.5, dash="6,4"))
    frags.append(text(410, 72, "ВС", 11, MUTED, "middle"))

    # Критерій вибору
    frags.append(fitbox(120, 320, 580, 50,
                        "ОДНА послідовно-подієва справа → автомат у loop();\nБАГАТО незалежних / є блокувальні виклики → задачі/RTOS.",
                        size=12, fill="#fffbe8", stroke="#caa24a", sw=1.8, color=INK))

    frags.append(fitbox(120, H - 50, 580, 36,
                        "§4.10.2 діагностує «коли super-loop вичерпався»; ця вставка — «коли навіть до RTOS не треба».",
                        size=11, fill="#f4f6f8", stroke=MUTED, sw=1.0, color=MUTED))

    render(os.path.join(OUT, "fig-27-3a-2-fsm-vs-task.svg"), W, H, *frags,
           title=None)
    print("wrote fig-27-3a-2-fsm-vs-task.svg")


if __name__ == "__main__":
    fig_state_diagram()
    fig_fsm_vs_task()
    print("done.")
