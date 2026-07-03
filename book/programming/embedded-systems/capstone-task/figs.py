# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── whole-system: як окремі вміння зростаються в одну прошивку ─────────────────
# Ідея: у центрі — ритмічний контур «читай → обчисли → дій»; довкола нього
# сходяться всі інші вміння: давачі-входи, виходи-виконавці, переривання/таймери
# як тло, вартові (watchdog + failsafe), пам'ять (стан переживає перезапуск),
# телеметрія (вікно назовні). Капстоун — це коли всі стрілки замкнулися в одне.
def fig_whole_system():
    W, H = 760, 470
    p = []

    cx, cy = W / 2, 250
    # серце — контур реального часу
    core = rect(cx - 120, cy - 55, 240, 110, fill="#eaf0fd", stroke=NEG, sw=2.2, rx=10)
    p.append(core)
    p.append(text(cx, cy - 30, "контур реального часу", size=13, color=NEG, bold=True))
    p.append(text(cx, cy - 8, "читай → обчисли → дій", size=12.5, color=INK))
    p.append(text(cx, cy + 14, "фіксований такт (напр. 200 Гц)", size=11, color=MUTED))
    p.append(text(cx, cy + 36, "автомат режимів усередині", size=11, color=MUTED))

    # ── входи зліва ──
    ib, ibw, ibh = textbox(140, 150, "давачі\n(орієнтація, заряд,\nGNSS, температура)",
                           size=11, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.6)
    p.append(ib)
    p.append(arrow(140 + ibw / 2, 165, cx - 120, cy - 30, color=FIELD, sw=1.8))

    # ── виходи справа ──
    ob, obw, obh = textbox(W - 140, 150, "виконавці\n(мотори, ШІМ,\nреле, індикатори)",
                           size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.6)
    p.append(ob)
    p.append(arrow(cx + 120, cy - 30, W - 140 - obw / 2, 165, color=POS, sw=1.8))

    # ── тло згори: переривання й таймери ──
    tb, tbw, tbh = textbox(cx, 92, "переривання й таймери — тло",
                           size=11.5, bold=True, color=INK, fill="#fff6e6", stroke="#caa23a", sw=1.7)
    p.append(tb)
    p.append(arrow(cx, 92 + tbh / 2, cx, cy - 55, color="#caa23a", sw=1.8))
    p.append(text(cx, 92 - tbh / 2 - 8, "події ловляться поза чергою", size=10, color=MUTED))

    # ── вартові зліва-знизу: watchdog + failsafe ──
    wb, wbw, wbh = textbox(150, 360, "вартові\nwatchdog · failsafe",
                           size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.7)
    p.append(wb)
    p.append(arrow(150 + wbw / 2 - 20, 360 - wbh / 2, cx - 90, cy + 55, color=POS, sw=1.8))
    # петля «я живий» назад до вартового
    p.append(arrow(cx - 90, cy + 55 + 6, 150 + wbw / 2 - 55, 360 - wbh / 2 + 8, color=MUTED, sw=1.3))
    p.append(text(150, 360 + wbh / 2 + 14, "«я живий» щотакту", size=10, color=MUTED))

    # ── пам'ять справа-знизу ──
    mb, mbw, mbh = textbox(W - 150, 360, "пам'ять\nстан переживає\nперезапуск",
                           size=11, bold=True, color=INK, fill=FILL, stroke=LINE, sw=1.6)
    p.append(mb)
    p.append(arrow(cx + 90, cy + 55, W - 150 - mbw / 2 + 20, 360 - mbh / 2, color=MUTED, sw=1.6))

    # ── телеметрія знизу по центру ──
    lb, lbw, lbh = textbox(cx, 410, "телеметрія — вікно назовні",
                           size=11.5, bold=True, color=INK, fill="#eef2f6", stroke=MUTED, sw=1.6)
    p.append(lb)
    p.append(arrow(cx, cy + 55, cx, 410 - lbh / 2, color=MUTED, sw=1.6))

    render(os.path.join(OUT, "whole-system.svg"), W, H, *p,
           title="Капстоун: окремі вміння сходяться в один робочий контур")


# ── loop-budget: бюджет часу одного такту — хребет усієї прошивки ──────────────
# Ідея: період такту фіксований (дедлайн). Усередині — послідовність робіт;
# усе разом мусить вкластися в період із запасом (slack). Якщо якийсь крок
# роздувся — робота перескакує дедлайн, і такт зірвано.
def fig_loop_budget():
    W, H = 720, 320
    p = []
    x0 = 80
    x1 = W - 60
    span = x1 - x0
    period_us = 5000  # 200 Гц → 5 мс

    def X(us):
        return x0 + span * us / period_us

    # верхній рядок: здоровий такт, укладається із запасом
    y1 = 95
    segs1 = [(0, 900, "давачі", FIELD, "#eafaf0"),
             (900, 2100, "контур керування", NEG, "#eaf0fd"),
             (2100, 2900, "виходи", POS, "#fdecea"),
             (2900, 3300, "службове", MUTED, "#eef2f6")]
    p.append(text(x0 - 8, y1 - 26, "здоровий такт", size=12, color=INK, anchor="start", bold=True))
    for a, b, lab, col, fill in segs1:
        p.append(rect(X(a), y1, X(b) - X(a), 34, fill=fill, stroke=col, sw=1.5, rx=4))
        if X(b) - X(a) > 60:
            p.append(text((X(a) + X(b)) / 2, y1 + 22, lab, size=10.5, color=col, bold=True))
    # запас
    p.append(rect(X(3300), y1, X(period_us) - X(3300), 34, fill="none", stroke="#bbbbbb", sw=1.2, rx=4))
    p.append(text((X(3300) + X(period_us)) / 2, y1 + 22, "запас", size=10.5, color=MUTED))

    # нижній рядок: роздутий крок — зрив дедлайну
    y2 = 200
    segs2 = [(0, 900, "давачі", FIELD, "#eafaf0"),
             (900, 4200, "контур роздувся", NEG, "#eaf0fd"),
             (4200, 5000, "виходи", POS, "#fdecea")]
    p.append(text(x0 - 8, y2 - 26, "роздутий крок", size=12, color=INK, anchor="start", bold=True))
    for a, b, lab, col, fill in segs2:
        bb = min(b, period_us)
        p.append(rect(X(a), y2, X(bb) - X(a), 34, fill=fill, stroke=col, sw=1.5, rx=4))
        if X(bb) - X(a) > 60:
            p.append(text((X(a) + X(bb)) / 2, y2 + 22, lab, size=10.5, color=col, bold=True))
    # шматок, що виліз за межу
    p.append(rect(X(period_us), y2, 46, 34, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(text(X(period_us) + 62, y2 + 22, "не встиг", size=10.5, color=POS, anchor="start", bold=True))

    # спільна лінія дедлайну (кінець періоду) для обох рядків
    yd_top = y1 - 18
    yd_bot = y2 + 52
    p.append(line(X(period_us), yd_top, X(period_us), yd_bot, color=POS, sw=2, dash="5 4"))
    p.append(text(X(period_us), yd_top - 8, "дедлайн: 5 мс (200 Гц)", size=11, color=POS, bold=True))

    # вісь часу
    ay = yd_bot + 22
    p.append(line(x0, ay, X(period_us) + 4, ay, color=INK, sw=1.4))
    for us in (0, 1000, 2000, 3000, 4000, 5000):
        p.append(line(X(us), ay - 4, X(us), ay + 4, color=INK, sw=1.2))
        p.append(text(X(us), ay + 18, "%d" % (us // 1000), size=10, color=MUTED))
    p.append(text(X(period_us) + 30, ay + 18, "мс", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "loop-budget.svg"), W, H, *p,
           title="Бюджет одного такту: усе мусить укластися до дедлайну")


# ── mode-machine: автомат режимів — скелет безпеки прошивки ───────────────────
# Ідея: прошивка завжди в одному з відомих станів; переходи дозволені лише
# певні. З будь-якого «робочого» стану біда кидає у FAILSAFE — і назад у RUN
# наосліп ходу немає (лише через контрольований шлях).
def fig_mode_machine():
    W, H = 720, 360
    p = []

    def node(cx, cy, lab, col, fill):
        b, w, h = textbox(cx, cy, lab, size=12, bold=True, color=col, fill=fill, stroke=col, sw=1.9, min_w=118)
        return b, w, h

    # координати станів
    boot = (110, 90)
    test = (300, 90)
    idle = (300, 250)
    run = (520, 250)
    fail = (520, 90)

    nodes = {
        "boot": (boot, "BOOT", MUTED, "#eef2f6"),
        "test": (test, "SELF-TEST", "#caa23a", "#fff6e6"),
        "idle": (idle, "IDLE / ARMED", NEG, "#eaf0fd"),
        "run":  (run,  "RUN", FIELD, "#eafaf0"),
        "fail": (fail, "FAILSAFE", POS, "#fdecea"),
    }
    box = {}
    for k, ((x, y), lab, col, fill) in nodes.items():
        b, w, h = node(x, y, lab, col, fill)
        box[k] = (x, y, w, h)
        p.append(b)

    def edge(a, b, col=INK, dash=None, sw=1.7):
        xa, ya, wa, ha = box[a]
        xb, yb, wb, hb = box[b]
        # проста прокладка: по горизонталі або вертикалі до краю
        import math
        dx, dy = xb - xa, yb - ya
        if abs(dx) >= abs(dy):
            sx = xa + (wa / 2) * (1 if dx > 0 else -1)
            ex = xb - (wb / 2) * (1 if dx > 0 else -1)
            return arrow(sx, ya, ex, yb, color=col, sw=sw) if dash is None else \
                ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" '
                 'stroke-dasharray="%s" marker-end="url(#arrow)"/>' % (sx, ya, ex, yb, col, sw, dash))
        else:
            sy = ya + (ha / 2) * (1 if dy > 0 else -1)
            ey = yb - (hb / 2) * (1 if dy > 0 else -1)
            return arrow(xa, sy, xb, ey, color=col, sw=sw) if dash is None else \
                ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" '
                 'stroke-dasharray="%s" marker-end="url(#arrow)"/>' % (xa, sy, xb, ey, col, sw, dash))

    p.append(edge("boot", "test", col=INK))
    p.append(edge("test", "idle", col=INK))
    p.append(edge("idle", "run", col=FIELD))
    # RUN → IDLE (обеззброїти) назад вниз-ліворуч
    xr, yr, wr, hr = box["run"]; xi, yi, wi, hi = box["idle"]
    p.append(arrow(xr - wr / 2, yr + 10, xi + wi / 2, yi + 10, color=MUTED, sw=1.4))

    # біда → FAILSAFE (з RUN і з IDLE)
    p.append(edge("run", "fail", col=POS))
    xi, yi, wi, hi = box["idle"]; xf, yf, wf, hf = box["fail"]
    p.append(arrow(xi + wi / 2 - 6, yi - hi / 2, xf - wf / 2 + 6, yf + hf / 2, color=POS, sw=1.6))
    # self-test не пройшов → FAILSAFE
    p.append(edge("test", "fail", col=POS, dash="5 4"))

    # підписи ребер
    p.append(text(205, 78, "старт ok", size=10, color=MUTED))
    p.append(text(410, 265, "arm + перевірки", size=10, color=FIELD, bold=True))
    p.append(text(410, 235, "disarm", size=9.5, color=MUTED))
    p.append(text(560, 175, "біда", size=10, color=POS, bold=True))
    p.append(text(320, 175, "біда", size=10, color=POS, bold=True))
    p.append(text(300, 118, "провал\nтесту", size=9, color=POS))

    # примітка внизу
    p.append(text(W / 2, H - 18, "з RUN у FAILSAFE — вмить; назад у RUN — лише через контрольований шлях",
                  size=10.5, color=MUTED, bold=True))

    render(os.path.join(OUT, "mode-machine.svg"), W, H, *p,
           title="Автомат режимів: прошивка завжди у відомому стані")


if __name__ == "__main__":
    fig_whole_system()
    fig_loop_budget()
    fig_mode_machine()
    print("figures written")
