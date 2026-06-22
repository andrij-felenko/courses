# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── timeline: дамп відв'язує мить збою від миті розслідування ──────────────────
# Ідея: збій, обробник і reboot стискаються в кілька сотень мілісекунд на місці;
# розбір може статися через тижні на іншому столі. Зонд мусить бути тут і зараз;
# дамп чекає скільки треба.

def fig_timeline():
    W, H = 760, 300
    p = []
    ax = 60
    ay = 120
    aw = 640

    # дві зони часу
    p.append(rect(ax, 60, 300, 150, fill="#fbeeee", stroke="#e7c6c6", sw=1.2, rx=8))
    p.append(rect(ax + 360, 60, 280, 150, fill="#eef4ff", stroke="#c9d6f0", sw=1.2, rx=8))
    p.append(text(ax + 150, 80, "на місці — кілька сотень мс", size=11, color=POS, bold=True))
    p.append(text(ax + 360 + 140, 80, "пізніше — хоч за тижні", size=11, color=NEG, bold=True))

    # вісь часу
    p.append(arrow(ax, ay, ax + aw, ay, color=INK, sw=1.8))
    p.append(text(ax + aw, ay + 20, "час", size=12, color=INK, italic=True, anchor="end"))

    # події на осі
    evs = [
        (ax + 70, "збій\n(panic)", POS, "#fdecea"),
        (ax + 180, "обробник пише\nдамп → Flash", "#e67e22", "#fff3e0"),
        (ax + 300, "reboot,\nпристрій працює", FIELD, "#eafaf0"),
        (ax + 500, "розбір на хості:\nдамп + .elf + GDB", NEG, "#eaf0fd"),
    ]
    for ex, lab, col, fill in evs:
        p.append(circle(ex, ay, 6, fill=col, stroke=col, sw=1.5))
        b, bw, bh = textbox(ex, ay - 48, lab, size=10, bold=True, color=col, fill=fill, stroke=col, sw=1.4)
        p.append(line(ex, ay - 6, ex, ay - 48 + bh / 2, color=col, sw=1.2, dash="3 3"))
        p.append(b)

    # підкреслення: зонд vs дамп
    p.append(line(ax + 70, 235, ax + 300, 235, color=POS, sw=2.0, dash="6 4"))
    p.append(text(ax + 185, 252, "живий зонд: мусить бути підключений саме тут", size=10, color=POS))
    p.append(line(ax + 180, 275, ax + 500, 275, color=NEG, sw=2.4))
    p.append(text(ax + 340, 292, "core dump: записаний раз — читається будь-коли", size=10, color=NEG, bold=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Дамп відв'язує мить збою від миті розслідування")


# ── anatomy: дамп = знімок задач + .elf-словник → офлайн-GDB ───────────────────
# Ідея: дамп компактний (TCB+стек кожної задачі, регістри, причина), уся RAM не
# влазить; сам по собі він — голі числа; разом зі своїм .elf оживає у звичайну
# GDB-сесію без живого чипа.

def fig_anatomy():
    W, H = 800, 360
    p = []

    # ліворуч — вміст дампа
    dx, dy, dw = 40, 60, 300
    p.append(rect(dx, dy, dw, 268, fill="#eef4ff", stroke=NEG, sw=2, rx=10))
    p.append(text(dx + dw / 2, dy + 22, "core dump (бінарний, у Flash)", size=12, color=NEG, bold=True))
    rows = [
        ("заголовок", "версія, чип, причина паніки", "#dbe6fb"),
        ("регістри кожної задачі", "PC, SP, EXCCAUSE, EXCVADDR…", "#fdecea"),
        ("стек + TCB: app_task", "повний зріз", "#eafaf0"),
        ("стек + TCB: wifi_task", "повний зріз", "#eafaf0"),
    ]
    ry = dy + 40
    for title, sub, fill in rows:
        p.append(rect(dx + 12, ry, dw - 24, 40, fill=fill, stroke=LINE, sw=1.0, rx=4))
        p.append(text(dx + dw / 2, ry + 17, title, size=11, color=INK, bold=True))
        p.append(text(dx + dw / 2, ry + 32, sub, size=9, color=MUTED))
        ry += 48
    p.append(text(dx + dw / 2, ry + 14, "купа й уся RAM не влазять —", size=10, color=POS))
    p.append(text(dx + dw / 2, ry + 30, "зберігають стеки задач і обране", size=10, color=POS))

    # посередині — .elf як словник
    ex, ey, ew, eh = 380, 150, 150, 90
    p.append(rect(ex, ey, ew, eh, fill="#fff3e0", stroke="#e67e22", sw=2, rx=8))
    p.append(text(ex + ew / 2, ey + 30, "app.elf", size=15, color="#e67e22", bold=True))
    p.append(text(ex + ew / 2, ey + 52, "«словник»", size=11, color="#e67e22"))
    p.append(text(ex + ew / 2, ey + 72, "адреса → ім'я, рядок", size=9, color=MUTED))
    p.append(arrow(dx + dw, ey + eh / 2, ex - 4, ey + eh / 2, color=NEG, sw=1.8))

    # праворуч — офлайн-GDB
    gx, gy, gw, gh = 590, 140, 175, 110
    p.append(rect(gx, gy, gw, gh, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    p.append(text(gx + gw / 2, gy + 26, "GDB на хості", size=13, color=FIELD, bold=True))
    for i, ln in enumerate(["backtrace", "info threads", "print var"]):
        p.append(text(gx + gw / 2, gy + 48 + i * 18, ln, size=11, color=INK))
    p.append(text(gx + gw / 2, gy + gh - 6, "(живий чип не потрібен)", size=9, color=MUTED))
    p.append(arrow(ex + ew, ey + eh / 2, gx - 4, gy + gh / 2, color="#e67e22", sw=1.8))

    render(os.path.join(OUT, "anatomy.svg"), W, H, *p,
           title="Знімок задач + .elf-словник = жива GDB-сесія")


# ── two-questions: причина reset відповідає ЩО, дамп — ДЕ і ЧОМУ ────────────────
# Ідея: повне посмертне = два дешеві джерела, що відповідають на різні питання.
# Причина reset доступна завжди після перезавантаження; дамп — лише коли його
# встигли записати (і не у Flash-драйвері).

def fig_two_questions():
    W, H = 740, 320
    p = []
    cx = W / 2

    # верх — подія
    top, tw, th = textbox(cx, 56, "пристрій перезавантажився", size=12, bold=True,
                          fill="#2d3e50", stroke="#2d3e50", color="#ffffff", pad=12)
    p.append(top)

    # ліва колонка — причина reset (ЩО)
    lx = 170
    lb, lw, lh = textbox(lx, 150, "esp_reset_reason()\n(регістр RTC)", size=11, bold=True,
                         color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.8)
    p.append(lb)
    p.append(line(cx, 56 + th / 2, lx, 150 - lh / 2, color=NEG, sw=1.5))
    p.append(text(lx, 196, "ЩО сталося", size=12, color=NEG, bold=True))
    for i, ln in enumerate(["PANIC — впав у паніку", "BROWNOUT — просів струм",
                            "WDT — застряг, watchdog", "DEEPSLEEP — прокинувся"]):
        p.append(text(lx, 218 + i * 20, ln, size=10, color=INK))

    # права колонка — core dump (ДЕ і ЧОМУ)
    rx = W - 170
    rb, rw, rh = textbox(rx, 150, "core dump + .elf\n(GDB офлайн)", size=11, bold=True,
                         color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(rb)
    p.append(line(cx, 56 + th / 2, rx, 150 - rh / 2, color=FIELD, sw=1.5))
    p.append(text(rx, 196, "ДЕ і ЧОМУ", size=12, color=FIELD, bold=True))
    for i, ln in enumerate(["задача й рядок збою", "backtrace кожної задачі",
                            "регістри, EXCVADDR", "значення змінних"]):
        p.append(text(rx, 218 + i * 20, ln, size=10, color=INK))

    # підказка: дамп є не завжди
    p.append(text(rx, 218 + 4 * 20 + 4, "лише якщо встиг записатися", size=9, color=POS, italic=True))

    render(os.path.join(OUT, "two-questions.svg"), W, H, *p,
           title="Два дешеві джерела — на два різні питання")


# ── limits: чому обробник іноді не лишає дампа ─────────────────────────────────
# Ідея: запис дампа — не магія, а звичайний код у найгірший момент. Чотири
# чесні діри: збій у Flash-драйвері, пошкоджений стек, мала ділянка пам'яті,
# нестача місця в розділі.

def fig_limits():
    W, H = 740, 300
    p = []
    cx = W / 2

    ccy = 150
    core, cw, ch = textbox(cx, ccy, "обробник паніки\nпише дамп", size=12, bold=True,
                           fill="#fff3e0", stroke="#e67e22", color="#e67e22", pad=14)

    holes = [
        (160, 70, "збій у Flash-\nдрайвері → нікуди\nписати", POS, "#fdecea"),
        (W - 160, 70, "стек пошкоджено →\nbacktrace неповний\nабо хибний", POS, "#fdecea"),
        (160, H - 64, "купа не входить →\nстан поза стеком\nне видно", "#e67e22", "#fff3e0"),
        (W - 160, H - 64, "розділ малий →\nдамп обрізано", "#e67e22", "#fff3e0"),
    ]
    for hx, hy, lab, col, fill in holes:
        b, bw, bh = textbox(hx, hy, lab, size=10, bold=True, color=col, fill=fill, stroke=col, sw=1.6)
        above = hy < ccy
        dirx = 1 if hx < cx else -1
        ay_ = hy + (bh / 2 if above else -bh / 2)
        tx = cx - dirx * cw / 2
        ty = ccy - (ch / 2 if above else -ch / 2)
        p.append(line(hx, ay_, tx, ty, color=col, sw=1.5, dash="4 3"))
        p.append(b)

    p.append(core)

    render(os.path.join(OUT, "limits.svg"), W, H, *p,
           title="Запис дампа — звичайний код у найгірший момент")


if __name__ == "__main__":
    fig_timeline()
    fig_anatomy()
    fig_two_questions()
    fig_limits()
    print("OK: figures written to", OUT)
