# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── step-kinds: три види кроку — куди потрапляє керування на рядку з викликом ──
# Ідея: той самий рядок `r = f(x);`. Крок «всередину» зупиняється на першому
# рядку f; крок «через» виконує f цілком і стає на наступному рядку; крок
# «назовні» доганяє поточну функцію до return. Видно, що різниця — у тому,
# ЯК повелися з вкладеним викликом, а не в довжині кроку.

def fig_step_kinds():
    W, H = 820, 420
    p = []

    # стовпчик вихідного коду трохи лівіше центру (праворуч місце для тіла f)
    cx = 330
    lines = [
        "void caller() {",
        "    int x = read();",
        "    int r = f(x);",        # рядок із викликом — герой
        "    use(r);",
        "}",
    ]
    ly0, lh = 70, 30
    call_i = 2
    for i, ln in enumerate(lines):
        y = ly0 + i * lh
        hot = (i == call_i)
        p.append(rect(cx - 150, y - 18, 300, 24,
                      fill="#fff5e6" if hot else "#f6f7f9",
                      stroke=POS if hot else MUTED, sw=1.6 if hot else 1.0, rx=4))
        p.append(text(cx - 140, y, ln, size=13, anchor="start",
                      bold=hot, color=INK))

    # тіло вкладеної функції f — окремий блок праворуч унизу
    fb_x, fb_y, fb_w, fb_h = cx + 190, 150, 200, 78
    p.append(rect(fb_x, fb_y, fb_w, fb_h, fill="#eef4ff", stroke=NEG, sw=1.6, rx=6))
    p.append(text(fb_x + fb_w / 2, fb_y + 22, "f(int x) {", size=12, bold=True))
    p.append(text(fb_x + fb_w / 2, fb_y + 42, "...тіло...", size=12, color=MUTED))
    p.append(text(fb_x + fb_w / 2, fb_y + 62, "}", size=12, bold=True))

    call_y = ly0 + call_i * lh

    # «всередину» (step / s): рядок виклику → перший рядок f
    p.append(arrow(cx + 150, call_y, fb_x, fb_y + 22, color=NEG, sw=2.0))
    p.append(text(cx + 175, call_y - 24, "крок «всередину»", size=12, color=NEG,
                  anchor="middle", bold=True))
    p.append(text(cx + 175, call_y - 8, "(step / s)", size=10, color=NEG, anchor="middle"))

    # «через» (next / n): рядок виклику → наступний рядок
    next_y = ly0 + (call_i + 1) * lh
    p.append('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="2.0" marker-end="url(#arrow)"/>'
             % (cx - 150, call_y, cx - 250, call_y,
                cx - 250, next_y, cx - 150, next_y, FIELD))
    p.append(mtext(cx - 255, (call_y + next_y) / 2 - 4,
                   "крок «через»\n(next / n):\nf() виконано\nцілком",
                   size=11, color=FIELD, anchor="middle", bold=True))

    # «назовні» (finish): з будь-якого місця f → одразу після виклику
    p.append('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="2.0" stroke-dasharray="6 4" '
             'marker-end="url(#arrow)"/>'
             % (fb_x + fb_w, fb_y + fb_h - 10, fb_x + fb_w + 40, fb_y + fb_h + 60,
                cx + 160, next_y + 30, cx + 150, next_y, POS))
    p.append(text(fb_x + 30, fb_y + fb_h + 64, "крок «назовні» (finish): доконати f і вийти",
                  size=11, color=POS, anchor="middle", bold=True))

    p.append(fitbox(90, H - 46, 580, 30,
                    "різниця кроків — у тому, ЯК повелися з вкладеним викликом, а не в довжині кроку",
                    size=11, color=MUTED, fill="#f8f8f8", stroke=MUTED, sw=1.3))

    render(os.path.join(OUT, "step-kinds.svg"), W, H, *p,
           title="Три види кроку: всередину, через, назовні")


# ── stack-to-frames: як із завмерлого стека в RAM постає список фреймів bt ──────
# Ідея: стек — фізичний слід «хто кого викликав». Кожен виклик лишив кадр зі
# збереженою адресою повернення (LR) і покажчиком на попередній кадр; backtrace
# іде цим ланцюгом від поточної функції вгору до main. Зліва — байти в RAM,
# справа — той самий ланцюг як читабельні рядки #0…#n.

def fig_stack_to_frames():
    W, H = 820, 440
    p = []

    # ── ліворуч: стек у RAM (росте вниз за адресою) ──
    sx, sw_ = 70, 250
    p.append(text(sx + sw_ / 2, 56, "стек у RAM", size=13, bold=True, color=INK))
    p.append(text(sx + sw_ / 2, 72, "(адреси ростуть униз)", size=10, color=MUTED))
    frames = [
        ("кадр sensor_read", "лок.: buf, len", "ret → update_sensors", "#0"),
        ("кадр update_sensors", "лок.: i", "ret → sensor_task", "#1"),
        ("кадр sensor_task", "лок.: arg", "ret → task_entry", "#2"),
    ]
    fy0, fh = 90, 96
    cols = [NEG, FIELD, "#8a5a00"]
    for i, (a, b, c, _) in enumerate(frames):
        y = fy0 + i * (fh + 6)
        p.append(rect(sx, y, sw_, fh, fill="#f6f7f9", stroke=cols[i], sw=1.6))
        p.append(text(sx + sw_ / 2, y + 22, a, size=12, bold=True, color=cols[i]))
        p.append(text(sx + sw_ / 2, y + 44, b, size=11, color=INK))
        p.append(text(sx + sw_ / 2, y + 66, c, size=10, color=MUTED))
        # ланка «попередній кадр» (saved frame pointer) — стрілка вниз між кадрами
        if i < len(frames) - 1:
            p.append(arrow(sx + sw_ - 18, y + fh, sx + sw_ - 18, y + fh + 6,
                           color=MUTED, sw=1.4))

    # SP показує на вершину (поточний кадр)
    p.append(text(sx - 8, fy0 + 16, "SP →", size=12, bold=True, color=POS, anchor="end"))

    # ── стрілка «відновлення» посередині ──
    midx = sx + sw_ + 60
    p.append(arrow(sx + sw_ + 14, H / 2, midx + 36, H / 2, color=INK, sw=2.2))
    p.append(mtext(midx + 18, H / 2 - 16, "backtrace\nіде ланцюгом\nret-адрес угору",
                   size=11, color=INK, anchor="middle", bold=True))

    # ── праворуч: той самий ланцюг як рядки bt ──
    bx, bw_ = midx + 80, 230
    p.append(text(bx + bw_ / 2, 56, "що показує bt", size=13, bold=True, color=INK))
    rows = [
        ("#0", "sensor_read", "sensor.c:88", NEG),
        ("#1", "update_sensors", "sensors.c:45", FIELD),
        ("#2", "sensor_task", "sensors.c:120", "#8a5a00"),
        ("#3", "task_entry", "tasks.c:512", MUTED),
    ]
    ry0, rh = 100, 64
    for i, (n, fn, loc, col) in enumerate(rows):
        y = ry0 + i * (rh + 6)
        p.append(rect(bx, y, bw_, rh, fill="#fbfbfd", stroke=col, sw=1.5))
        p.append(text(bx + 16, y + 26, n, size=13, bold=True, color=col, anchor="start"))
        p.append(text(bx + 50, y + 26, fn, size=12, bold=True, anchor="start"))
        p.append(text(bx + 16, y + 48, "at " + loc, size=11, color=MUTED, anchor="start"))
        if i < len(rows) - 1:
            p.append(arrow(bx + bw_ / 2, y + rh, bx + bw_ / 2, y + rh + 6,
                           color=MUTED, sw=1.4))
    p.append(text(bx + bw_ / 2, ry0 + 4 * (rh + 6) + 14, "↑ до main",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "stack-to-frames.svg"), W, H, *p,
           title="Від завмерлого стека до списку фреймів backtrace")


# ── single-step-engine: як апаратний крок реально робиться (для -d.md) ──────────
# Ідея: «крок» — не магія IDE, а одна апаратна дія ядра через SWD/JTAG. Хост
# пише біт C_STEP у DHCSR; ядро виконує РІВНО одну інструкцію і знову halt;
# хост читає PC і дивиться в таблицю рядків — той самий рядок чи вже інший.
# Лінію рядка хост проганяє повторенням цього циклу (або range-step).

def fig_single_step_engine():
    W, H = 820, 400
    p = []

    # три дійові особи зліва направо
    host_x, host_w = 50, 180
    p.append(fitbox(host_x, 90, host_w, 220, "", fill="#f6f7f9", stroke=INK, sw=1.5))
    p.append(text(host_x + host_w / 2, 110, "Хост (GDB)", size=13, bold=True))
    host_lines = [
        "1. знає адресу й",
        "   таблицю рядків .elf",
        "2. просить «1 крок»",
        "3. читає PC після halt",
        "4. той самий рядок?",
        "   ні → стоп;",
        "   так → повторити",
    ]
    for j, ln in enumerate(host_lines):
        p.append(text(host_x + 12, 138 + j * 22, ln, size=11, anchor="start", color=INK))

    probe_x, probe_w = 320, 150
    p.append(fitbox(probe_x, 140, probe_w, 120,
                    "Зонд\n(SWD / JTAG)\n\nпереклад\nкоманда ↔ дріт",
                    size=12, bold=True, fill="#eef4ff", stroke=NEG, sw=1.6))

    core_x, core_w = 600, 170
    p.append(fitbox(core_x, 90, core_w, 220, "", fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text(core_x + core_w / 2, 110, "Ядро Cortex-M", size=13, bold=True, color=POS))
    p.append(fitbox(core_x + 14, 128, core_w - 28, 50,
                    "DHCSR: C_STEP = 1\n(регістр керування\nвідлагодженням)",
                    size=11, fill="#fff0f0", stroke=POS, sw=1.2))
    p.append(text(core_x + core_w / 2, 200, "виконати РІВНО", size=12, bold=True, color=INK))
    p.append(text(core_x + core_w / 2, 218, "одну інструкцію", size=12, bold=True, color=INK))
    p.append(fitbox(core_x + 14, 234, core_w - 28, 40,
                    "→ знову halt\n(зупинка ядра)", size=11, fill="#fff0f0",
                    stroke=POS, sw=1.2))

    # стрілки запиту (вниз) і відповіді (вгору)
    p.append(arrow(host_x + host_w, 170, probe_x, 170, color=INK, sw=2.0))
    p.append(text((host_x + host_w + probe_x) / 2, 162, "крок", size=10, color=INK))
    p.append(arrow(probe_x + probe_w, 170, core_x, 170, color=INK, sw=2.0))
    p.append(text((probe_x + probe_w + core_x) / 2, 162, "C_STEP", size=10, color=INK))

    p.append(arrow(core_x, 250, probe_x + probe_w, 250, color=FIELD, sw=2.0))
    p.append(arrow(probe_x, 250, host_x + host_w, 250, color=FIELD, sw=2.0))
    p.append(text((probe_x + probe_w + core_x) / 2, 244, "halt + PC", size=10, color=FIELD))
    p.append(text((host_x + host_w + probe_x) / 2, 244, "PC", size=10, color=FIELD))

    # цикл «повторити, поки той самий рядок»
    p.append('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="1.8" stroke-dasharray="6 4" '
             'marker-end="url(#arrow)"/>'
             % (host_x + 30, 300, host_x + 30, 360,
                core_x + core_w - 30, 360, core_x + core_w - 30, 300, MUTED))
    p.append(text(W / 2, 356, "один рядок C = багато машинних кроків → хост повторює цикл "
                  "(або просить range-step одразу)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "single-step-engine.svg"), W, H, *p,
           title="Що таке «крок» насправді: одна апаратна дія ядра")


if __name__ == "__main__":
    fig_step_kinds()
    fig_stack_to_frames()
    fig_single_step_engine()
    print("OK: figures written to", OUT)
