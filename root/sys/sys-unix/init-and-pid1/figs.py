# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
RED = "#fdecea"
WARM = "#fff6e5"
GREY = "#eceff1"


def tb(cx, cy, lines, **kw):
    """textbox + межі рамки (x0, x1, y0, y1)."""
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Нерухома точка перепідпорядкування ───────────────────────────────────
def fig_reparent_fixpoint():
    W, H = 1400, 620
    p = []

    def panel(cx, title, dead):
        out = []
        out.append(text(cx, 66, title, size=17, bold=True))

        f, _, _, _, iy1 = tb(cx, 150, "init — PID 1", size=15, bold=True, fill=GREEN, pad=13)
        out.append(f)

        sh_fill = RED if dead else BLUE
        sh_txt = "оболонка — PID 812\nзавершилася" if dead else "оболонка — PID 812"
        f, sx0, sx1, sy0, sy1 = tb(cx, 300, sh_txt, size=15, fill=sh_fill, pad=13)
        out.append(f)

        f, ax0, ax1, ay0, _ = tb(cx - 175, 460, "PID 903", size=15, fill=BLUE, pad=13)
        out.append(f)
        f, bx0, bx1, by0, _ = tb(cx + 175, 460, "PID 904", size=15, fill=BLUE, pad=13)
        out.append(f)

        if not dead:
            out.append(line(cx, iy1, cx, sy0))
            out.append(line(cx, sy1, cx - 175, ay0))
            out.append(line(cx, sy1, cx + 175, by0))
        else:
            # старі ребра — обірвані
            out.append(line(cx, iy1, cx, sy0, color="#b0bec5", dash="5 5"))
            # нові ребра ведуть в обхід мертвої ланки
            for sign, tx0, tx1 in ((-1, ax0, ax1), (1, bx0, bx1)):
                gx = cx + sign * 320
                ex = tx0 if sign < 0 else tx1
                sxe = sx0 if sign < 0 else sx1
                out.append(line(cx + sign * 92, 150, gx, 150, color="#2e7d32", sw=2))
                out.append(line(gx, 150, gx, 460, color="#2e7d32", sw=2))
                out.append(arrow(gx, 460, ex + sign * 6, 460, color="#2e7d32"))
            out.append(text(cx, 560, "нові ребра ведуть у ту саму точку", size=14, italic=True))
        return out

    p += panel(370, "поки батько живий", False)
    p += panel(1030, "батько помер раніше за дітей", True)
    p.append(line(700, 46, 700, 590, color="#cfd8dc", dash="6 6"))

    render(os.path.join(IMG, 'reparent-fixpoint.svg'), W, H, *p)


# ── 2. Один сигнал, дві різні долі ──────────────────────────────────────────
def fig_signal_to_pid1():
    W, H = 1420, 560
    p = []

    c1x, c1w = 40, 500
    c2x, c2w = 560, 400
    c3x, c3w = 980, 400

    hy, hh = 60, 62
    p.append(fitbox(c1x, hy, c1w, hh, "що прийшло до процесу", size=16, bold=True, fill=GREY))
    p.append(fitbox(c2x, hy, c2w, hh, "звичайний процес", size=16, bold=True, fill=GREY))
    p.append(fitbox(c3x, hy, c3w, hh, "процес із номером 1", size=16, bold=True, fill=GREY))

    rows = [
        ("сигнал, на який поставлено обробник",
         "виконується обробник", "виконується обробник", BLUE, BLUE),
        ("сигнал без обробника, типова дія — завершити\n(SIGTERM, SIGINT, SIGHUP)",
         "процес гине", "сигнал відкидається", RED, GREEN),
        ("SIGKILL або SIGSTOP із цієї самої системи",
         "процес гине або спиняється", "нічого не стається", RED, GREEN),
        ("SIGKILL або SIGSTOP із простору імен-предка",
         "такого випадку немає", "доставляється примусово", GREY, RED),
        ("фатальна помилка в самому коді\n(SIGSEGV від ядра)",
         "процес гине", "процес гине, а за ним падає ядро", RED, RED),
    ]

    y = hy + hh + 10
    rh = 84
    for left, mid, right, fm, fr in rows:
        p.append(fitbox(c1x, y, c1w, rh, left, size=15, fill="#ffffff"))
        p.append(fitbox(c2x, y, c2w, rh, mid, size=15, fill=fm))
        p.append(fitbox(c3x, y, c3w, rh, right, size=15, fill=fr))
        y += rh + 8

    render(os.path.join(IMG, 'signal-to-pid1.svg'), W, H, *p)


# ── 3. Номер 1 — величина відносна ──────────────────────────────────────────
def fig_nested_pid1():
    W, H = 1360, 660
    p = []

    p.append(rect(40, 60, 1280, 490, fill="#f7f9fb", stroke="#90a4ae", sw=2))
    p.append(text(62, 92, "простір імен PID усієї системи", size=15, bold=True, anchor="start"))

    p.append(rect(600, 130, 690, 390, fill="#ffffff", stroke="#42a5f5", sw=2, rx=10))
    p.append(text(622, 162, "вкладений простір імен PID", size=15, bold=True, anchor="start"))

    f, _, ix1, _, iy1 = tb(275, 190, "init усієї системи\nPID 1", size=15, bold=True, fill=GREEN, pad=13)
    p.append(f)
    f, _, rx1, ry0, ry1 = tb(275, 330, "рушій контейнерів\nPID 2140", size=15, fill=BLUE, pad=13)
    p.append(f)
    p.append(line(275, iy1, 275, ry0))

    f, nx0, _, ny0, ny1 = tb(945, 245, "той самий процес\nусередині: PID 1\nззовні: PID 4021",
                             size=15, bold=True, fill=GREEN, pad=13)
    p.append(f)
    p.append(arrow(rx1, 320, nx0 - 8, 258))

    f, _, _, cy0, _ = tb(790, 420, "PID 2 усередині\nPID 4108 ззовні", size=15, fill=BLUE, pad=13)
    p.append(f)
    f, _, _, dy0, _ = tb(1105, 420, "PID 3 усередині\nPID 4109 ззовні", size=15, fill=BLUE, pad=13)
    p.append(f)
    p.append(line(945, ny1, 790, cy0))
    p.append(line(945, ny1, 1105, dy0))

    f, _, _, _, _ = tb(275, 470, "kill -9 зсередини — нічого\nkill -9 ззовні — гине він,\nа з ним увесь простір імен",
                       size=15, fill=WARM, pad=13)
    p.append(f)

    p.append(text(680, 610, "той самий запис у ядрі має два номери; особливість дає лише той, що дорівнює одиниці",
                  size=14, italic=True))

    render(os.path.join(IMG, 'nested-pid1.svg'), W, H, *p)


# ── 4. Що переживає fork, а що exec (для вставки proj-minimal-init) ─────────
def fig_mini_init_inherit():
    W, H = 1360, 520
    p = []

    c1x, c1w = 40, 400
    c2x, c2w = 460, 420
    c3x, c3w = 900, 420

    hy, hh = 56, 62
    p.append(fitbox(c1x, hy, c1w, hh, "властивість процесу", size=16, bold=True, fill=GREY))
    p.append(fitbox(c2x, hy, c2w, hh, "що з нею робить fork", size=16, bold=True, fill=GREY))
    p.append(fitbox(c3x, hy, c3w, hh, "що з нею робить exec", size=16, bold=True, fill=GREY))

    rows = [
        ("обробник сигналу",
         "копіюється як є", "скидається на типову дію", BLUE, WARM, False),
        ("маска блокування",
         "копіюється як є", "лишається такою, як була", BLUE, RED, True),
        ("сигнали, що вже чекають",
         "у дитини черга порожня", "черга лишається", BLUE, WARM, False),
        ("позначка «ігнорувати»",
         "копіюється як є", "лишається ігнорованою", BLUE, WARM, False),
    ]

    y = hy + hh + 10
    rh = 76
    for left, mid, right, fm, fr, hot in rows:
        p.append(fitbox(c1x, y, c1w, rh, left, size=15, bold=hot, fill="#ffffff"))
        p.append(fitbox(c2x, y, c2w, rh, mid, size=15, fill=fm))
        p.append(fitbox(c3x, y, c3w, rh, right, size=15, bold=hot, fill=fr))
        y += rh + 8

    render(os.path.join(IMG, 'mini-init-inherit.svg'), W, H, *p)


# ── 5. Порядок, у якому ядро вирішує долю сигналу до номера 1 ───────────────
def fig_mini_init_blocked():
    W, H = 1380, 560
    p = []

    qx = 380          # колонка запитань
    ax = 1010         # колонка відповідей

    f, _, sx1, _, sy1 = tb(qx, 70, "сигнал адресовано процесові з номером 1",
                           size=16, bold=True, fill=GREY, pad=14)
    p.append(f)

    steps = [
        (215, "чи стоїть він\nу масці блокування?",
         "стає в чергу — init прочитає\nйого викликом sigwait", GREEN),
        (360, "чи поставлено на нього\nвласний обробник?",
         "доставляється — виконується\nобробник", GREEN),
    ]

    prev_y1 = sy1
    for cy, q, a, afill in steps:
        f, _, qx1, qy0, qy1 = tb(qx, cy, q, size=16, fill=WARM, pad=14)
        p.append(f)
        p.append(arrow(qx, prev_y1, qx, qy0 - 6))
        f, ax0, _, _, _ = tb(ax, cy, a, size=15, fill=afill, pad=14)
        p.append(f)
        p.append(arrow(qx1 + 6, cy, ax0 - 8, cy, color="#2e7d32", sw=2))
        p.append(text((qx1 + ax0) / 2, cy - 16, "так", size=14, color="#2e7d32"))
        p.append(text(qx - 30, (prev_y1 + qy0) / 2 + 6, "ні", size=14, anchor="end"))
        prev_y1 = qy1

    f, _, ex1, ey0, _ = tb(qx, 500, "ні того, ні того", size=16, bold=True, fill=GREY, pad=14)
    p.append(f)
    p.append(arrow(qx, prev_y1, qx, ey0 - 6))
    p.append(text(qx - 30, (prev_y1 + ey0) / 2 + 6, "ні", size=14, anchor="end"))

    f, dx0, _, _, _ = tb(ax, 500, "ядро відкидає сигнал —\nдо процесу він не доходить",
                         size=15, fill=RED, pad=14)
    p.append(f)
    p.append(arrow(ex1 + 6, 500, dx0 - 8, 500, color="#c62828", sw=2))

    render(os.path.join(IMG, 'mini-init-blocked.svg'), W, H, *p)


fig_reparent_fixpoint()
fig_signal_to_pid1()
fig_nested_pid1()
fig_mini_init_inherit()
fig_mini_init_blocked()
print("ok")
