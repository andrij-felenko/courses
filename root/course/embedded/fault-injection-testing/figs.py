# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── chain: несправність → помилка → відмова, із заслінкою ──────────────────────
# Ідея: уприскування вкидає несправність на лівому кінці; без захисту ланцюг
# дозріває до видимої відмови; заслінка (перевірка/сторож/безпечний стан) обриває
# його раніше. Тест питає одне: чи спрацювала заслінка.

def fig_chain():
    W, H = 780, 360
    p = []
    yc = 150
    bw = 150

    cx_fault = 140
    cx_err   = 390
    cx_fail  = 640

    # три ланки ланцюга
    b1, w1, h1 = textbox(cx_fault, yc, "НЕСПРАВНІСТЬ\n(fault)\nдефект, першопричина",
                         size=12, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.6, min_w=bw)
    b2, w2, h2 = textbox(cx_err, yc, "ПОМИЛКА\n(error)\nхибний стан усередині",
                         size=12, bold=True, color="#b9770e", fill="#fff3e0", stroke="#e67e22", sw=1.6, min_w=bw)
    b3, w3, h3 = textbox(cx_fail, yc, "ВІДМОВА\n(failure)\nвидима дурня назовні",
                         size=12, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=bw)

    # стрілки між ланками
    p.append(arrow(cx_fault + w1 / 2, yc, cx_err - w2 / 2, yc, color=INK, sw=2.0))
    p.append(arrow(cx_err + w2 / 2, yc, cx_fail - w3 / 2, yc, color=INK, sw=2.0))

    p.append(b1); p.append(b2); p.append(b3)

    # точка вкидання — над першою ланкою
    iy = 60
    bi, wi, hi = textbox(cx_fault, iy, "уприскування\nвкидає сюди", size=11, bold=True,
                         color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.6)
    p.append(bi)
    p.append(arrow(cx_fault, iy + hi / 2, cx_fault, yc - h1 / 2 - 2, color=FIELD, sw=2.0))

    # заслінка між «помилкою» і «відмовою» — обриває ланцюг
    gx = (cx_err + cx_fail) / 2
    p.append(line(gx, yc - 52, gx, yc + 52, color=FIELD, sw=3.2))
    bg, wg, hg = textbox(gx, 268, "ЗАСЛІНКА\nперевірка · сторож · безпечний стан",
                         size=11, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.6)
    p.append(line(gx, yc + 52, gx, 268 - hg / 2, color=FIELD, sw=1.4, dash="3 3"))
    p.append(bg)

    # хрестик на стрілці до відмови — ланцюг розірвано
    p.append(text(gx, yc - 60, "✕", size=20, color=FIELD, bold=True))

    # підпис унизу
    p.append(text(W / 2, 332, "Тест зелений ⟺ ланцюг обірвано до того, як дійшов до відмови",
                  size=12, color=INK, italic=True))

    render(os.path.join(OUT, "chain.svg"), W, H, *p,
           title="Уприскування вкидає несправність — заслінка має обірвати ланцюг")


# ── grid: куди вкидати × що вкидати ────────────────────────────────────────────
# Ідея: два незалежні вибори. Рядки — рівень (ніжки / програмно / модель),
# стовпці — клас несправності. Програмний рівень покриває майже все дешево —
# виділяємо його рядок.

def fig_grid():
    W, H = 820, 380
    p = []

    cols = ["зіпсовані\nдані", "відібраний\nресурс / час", "просадка\nживлення", "перекинутий\nбіт пам'яті"]
    rows = [
        ("на ніжки\n(pin-level)", "#fdecea", POS, ["–", "–", "✓", "○"]),
        ("ПРОГРАМНО\n(SWIFI)",     "#eafaf0", FIELD, ["✓", "✓", "○", "✓"]),
        ("у моделі\n(емулятор)",   "#eaf0fd", NEG, ["✓", "✓", "○", "✓"]),
    ]

    x0 = 175          # ліва межа сітки клітинок
    y0 = 70           # верх сітки клітинок
    cw = 150          # ширина стовпця
    rh = 78           # висота рядка
    gridw = cw * len(cols)

    # заголовки стовпців
    for j, c in enumerate(cols):
        cx = x0 + cw * j + cw / 2
        p.append(mtext(cx, y0 - 26, c, size=12, bold=True, color=INK, lh=1.15))

    # рядки
    for i, (name, fill, col, marks) in enumerate(rows):
        y = y0 + rh * i
        # підпис рядка ліворуч
        bl, wl, hl = textbox(x0 / 2 + 12, y + rh / 2, name, size=12, bold=True,
                             color=col, fill=fill, stroke=col, sw=1.6, min_w=140)
        p.append(bl)
        # підсвітити рядок SWIFI
        if "ПРОГРАМНО" in name:
            p.append(rect(x0 - 2, y - 2, gridw + 4, rh + 4, fill="#f3fcf6", stroke=FIELD, sw=2.2, rx=8))
        for j, mk in enumerate(marks):
            cx = x0 + cw * j + cw / 2
            cy = y + rh / 2
            p.append(rect(x0 + cw * j + 6, y + 6, cw - 12, rh - 12, fill=BG, stroke="#cfd6dd", sw=1.2, rx=6))
            mcol = FIELD if mk == "✓" else (MUTED if mk == "○" else "#c2c8cf")
            p.append(text(cx, cy + 9, mk, size=24, color=mcol, bold=True))

    # легенда
    ly = y0 + rh * len(rows) + 34
    p.append(text(x0, ly, "✓ дешево і влучно", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x0 + 210, ly, "○ лише наслідок / частково", size=11, color=MUTED, anchor="start"))
    p.append(text(x0 + 470, ly, "– непрактично", size=11, color="#9aa0a6", anchor="start"))

    render(os.path.join(OUT, "grid.svg"), W, H, *p,
           title="Два вибори: куди вкидати несправність × що саме вкидати")


# ── wdt: робочий приклад уприскування зависання у сторожа ──────────────────────
# Ідея: задача годує сторожа; вкидаємо нескінченний цикл — годувати перестала;
# сторож за таймаут спрацьовує й перезапускає; після старту причина reset
# доводить, що захист не проспав.

def fig_wdt():
    W, H = 800, 300
    p = []
    ax = 60
    ay = 150
    aw = 660

    # вісь часу
    p.append(arrow(ax, ay, ax + aw, ay, color=INK, sw=1.8))
    p.append(text(ax + aw, ay + 22, "час", size=12, color=INK, italic=True, anchor="end"))

    # зона «годуємо» (зелена) і «застрягли» (червона)
    p.append(rect(ax + 10, ay - 40, 200, 26, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(ax + 110, ay - 22, "годуємо сторожа", size=11, color=FIELD, bold=True))
    p.append(rect(ax + 220, ay - 40, 250, 26, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    p.append(text(ax + 345, ay - 22, "вкинуто: while(1) — не годуємо", size=11, color=POS, bold=True))

    evs = [
        (ax + 60,  "reset()\nreset()…", FIELD, "#eafaf0"),
        (ax + 230, "вкидаємо\nзависання", POS, "#fdecea"),
        (ax + 470, "таймаут:\nсторож спрацьовує", "#b9770e", "#fff3e0"),
        (ax + 610, "reboot →\nESP_RST_TASK_WDT", NEG, "#eaf0fd"),
    ]
    for ex, lab, col, fill in evs:
        p.append(circle(ex, ay, 6, fill=col, stroke=col, sw=1.5))
        b, bw, bh = textbox(ex, ay + 58, lab, size=10, bold=True, color=col, fill=fill, stroke=col, sw=1.4)
        p.append(line(ex, ay + 6, ex, ay + 58 - bh / 2, color=col, sw=1.2, dash="3 3"))
        p.append(b)

    # підпис-висновок
    p.append(text(W / 2, 274, "Зелений тест = причина скидання довела, що сторож не проспав",
                  size=12, color=INK, italic=True))

    render(os.path.join(OUT, "wdt.svg"), W, H, *p,
           title="Уприскування зависання: чесна перевірка сторожового таймера")


# ── hist-timeline: один принцип — чотири маски крізь десятиліття ────────────────
# Ідея вставки hist-fault-injection: «зламай навмисне» прожило >40 років, міняючи
# лише тіло — паяльник → код (FIAT/FERRARI) → стандарт (ISO 26262) → хмарна мавпа.
# Горизонтальна вісь часу з чотирма віхами; під кожною — інструмент і суть.

def fig_hist_timeline():
    W, H = 880, 380
    p = []
    ax = 60
    ay = 150
    aw = 760

    # вісь часу
    p.append(arrow(ax, ay, ax + aw, ay, color=INK, sw=1.8))
    p.append(text(ax + aw, ay + 24, "час", size=12, color=INK, italic=True, anchor="end"))

    # чотири віхи: (x, рік, заголовок, суть, колір, заливка, підпис зверху?)
    evs = [
        (ax + 70,  "1970-ті", "паяльник\nна платі",   "ідея:\nвнеси дефект рукою",      POS,        "#fdecea", True),
        (ax + 290, "1988–95", "FIAT · FERRARI",        "інструмент:\nуприскуй софтом,\nмірь покриття", "#b9770e", "#fff3e0", False),
        (ax + 510, "2011",    "ISO 26262",             "обов'язок:\nдоведи покриття\nуприскуванням",  NEG,        "#eaf0fd", True),
        (ax + 700, "2011",    "Chaos Monkey",          "масштаб:\nвали бойові\nсервери щодня",        FIELD,      "#eafaf0", False),
    ]
    for ex, yr, head, body, col, fill, up in evs:
        p.append(circle(ex, ay, 7, fill=col, stroke=col, sw=1.6))
        p.append(text(ex, ay - 14 if up else ay + 28, yr, size=12, color=col, bold=True))
        # картка з інструментом + суттю — по черзі вгору/вниз, щоб не налазили
        cy = ay - 88 if up else ay + 92
        b, bw, bh = textbox(ex, cy, head + "\n" + body, size=10.5, bold=True,
                            color=col, fill=fill, stroke=col, sw=1.5, min_w=150)
        edge = cy + bh / 2 if up else cy - bh / 2
        near = ay - 22 if up else ay + 38
        p.append(line(ex, near, ex, edge, color=col, sw=1.2, dash="3 3"))
        p.append(b)

    # наскрізний підпис: той самий принцип
    p.append(text(W / 2, 356, "Один принцип — «зламай навмисне, щоб дізнатися правду» — змінює лише тіло й масштаб",
                  size=12.5, color=INK, italic=True))

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Від замикання ніжок до мавпи хаосу: естафета однієї думки")


if __name__ == "__main__":
    fig_chain()
    fig_grid()
    fig_wdt()
    fig_hist_timeline()
    print("figures written to", OUT)
