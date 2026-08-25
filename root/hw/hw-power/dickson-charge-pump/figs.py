# -*- coding: utf-8 -*-
"""figs.py — фігури до теми «Діксон-ланцюжок» (dickson-charge-pump.md).
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Запуск:  python figs.py  →  пише всі SVG у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── символ конденсатора на вертикалі (низ керується тактом) ──────────────────
def vcap(x, ytop, ybot, color=INK, sw=2.6, gap=11, half=16):
    midy = (ytop + ybot) / 2
    out = [line(x, ytop, x, midy - gap / 2, color=color, sw=1.9),
           line(x - half, midy - gap / 2, x + half, midy - gap / 2, color=color, sw=sw),
           line(x - half, midy + gap / 2, x + half, midy + gap / 2, color=color, sw=sw),
           line(x, midy + gap / 2, x, ybot, color=color, sw=1.9)]
    return "".join(out), midy


# ── символ діода-клапана (трикутник + риска), вістря вправо ──────────────────
def diode_r(x, y, color=INK, s=11):
    """Діод на горизонталі, вістря (катод) праворуч — пускає заряд вправо."""
    out = ['<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" '
           'stroke-width="1.4"/>' % (x - s, y - s, x - s, y + s, x + s, y, "#fff", color),
           line(x + s, y - s, x + s, y + s, color=color, sw=2.6)]
    return "".join(out)


# ══════════════════════════════════════════════════════════════════════════
# ФІГУРА 1 — одна сходинка у двох фазах такту.
# Несе вагу: показує МЕХАНІКУ переливання заряду — у фазі «низ угорі» верхня
# обкладка стрибає на V1+Vφ і виштовхує заряд через правий клапан. Словами так
# наочно не передати.
# ══════════════════════════════════════════════════════════════════════════
def fig_pump_cell():
    W, H = 900, 470
    P = []

    def frame(ox, title, tcol):
        return [rect(ox + 18, 58, 404, 360, fill="none", stroke="#e4e4e4", sw=2, rx=10),
                text(ox + 220, 84, title, size=14, color=tcol, bold=True)]

    def cell(ox, low_up):
        """Малює сходинку. low_up=False — низ унизу (заряд); True — низ піднято."""
        vx_in = ox + 70            # лівий вузол (вхід сходинки)
        cx    = ox + 220           # конденсатор
        vx_out = ox + 370          # правий вузол (вихід сходинки)
        ytop  = 150                # рівень верхнього проводу
        ybot  = 300                # рівень нижньої обкладки / такту
        out = []

        # лівий вузол V1
        out.append(text(vx_in, 132, "вузол V1", size=11, color=MUTED))
        out.append(circle(vx_in, ytop, 4, fill=INK, stroke=INK))
        # клапан зліва (заходить у сходинку) — вістря до конденсатора
        out.append(diode_r((vx_in + cx) / 2, ytop, color=INK))
        out.append(line(vx_in, ytop, (vx_in + cx) / 2 - 12, ytop, color=INK, sw=2))
        out.append(line((vx_in + cx) / 2 + 12, ytop, cx, ytop, color=INK, sw=2))

        # конденсатор сходинки
        cap, midy = vcap(cx, ytop, ybot, color=FIELD)
        out.append(cap)
        out.append(text(cx + 26, midy - 4, "Cs", size=13, color=FIELD, bold=True, anchor="start"))

        # клапан справа (виводить із сходинки) — вістря до правого вузла
        out.append(diode_r((cx + vx_out) / 2, ytop, color=INK))
        out.append(line(cx, ytop, (cx + vx_out) / 2 - 12, ytop, color=INK, sw=2))
        out.append(line((cx + vx_out) / 2 + 12, ytop, vx_out, ytop, color=INK, sw=2))
        out.append(circle(vx_out, ytop, 4, fill=INK, stroke=INK))
        out.append(text(vx_out, 132, "далі →", size=11, color=MUTED))

        # нижня обкладка → тактова лінія
        if not low_up:
            # низ на 0
            out.append(line(cx, ybot, cx, ybot + 20, color=NEG, sw=2.4))
            out.append(line(cx - 16, ybot + 20, cx + 16, ybot + 20, color=NEG, sw=2.4))
            out.append(line(cx - 10, ybot + 25, cx + 10, ybot + 25, color=NEG, sw=2.4))
            out.append(text(cx, ybot + 46, "такт = 0", size=12, color=NEG, bold=True))
            out.append(text(cx - 24, ytop - 8, "верх ≈ V1", size=11, color=INK, anchor="end"))
            # стрілка заряджання зліва
            out.append(arrow(vx_in + 14, ytop - 18, cx - 20, ytop - 18, color=FIELD, sw=2.2))
            out.append(text((vx_in + cx) / 2, ytop - 26, "набирає заряд", size=11, color=FIELD, bold=True))
        else:
            # низ піднято на Vφ
            out.append(line(cx, ybot, cx, ybot + 24, color=POS, sw=2.4))
            box = fitbox(cx - 52, ybot + 24, 104, 30, "такт = Vφ", size=12, color=POS,
                         bold=True, fill="#fdecea", stroke=POS)
            out.append(box)
            out.append(text(cx - 24, ytop - 8, "верх ≈ V1+Vφ", size=11, color=POS, anchor="end", bold=True))
            # стрілка виштовхування вправо
            out.append(arrow(cx + 20, ytop - 18, vx_out - 14, ytop - 18, color=POS, sw=2.2))
            out.append(text((cx + vx_out) / 2, ytop - 26, "віддає заряд", size=11, color=POS, bold=True))
            # маленька стрілка вгору біля конденсатора — обидві обкладки їдуть угору
            out.append(arrow(cx + 60, ybot - 6, cx + 60, ytop + 20, color=MUTED, sw=1.8))
            out.append(text(cx + 72, (ytop + ybot) / 2, "усе", size=10, color=MUTED, anchor="start"))
            out.append(text(cx + 72, (ytop + ybot) / 2 + 13, "їде ↑", size=10, color=MUTED, anchor="start"))
        return out

    P += frame(0, "Фаза 1 — низ унизу: заряджається", NEG)
    P += cell(0, low_up=False)
    P += frame(454, "Фаза 2 — низ піднято: виштовхує", POS)
    P += cell(454, low_up=True)

    render("img/pump-cell.svg", W, H, *P)


# ══════════════════════════════════════════════════════════════════════════
# ФІГУРА 2 — чому Діксон, а не Кокрофт-Волтон: спосіб підведення такту.
# Несе вагу: візуалізує ГОЛОВНУ ідею теми — у CW гойдання йде послідовно крізь
# усі вузли (паразитика гасить), у Діксона такт заходить у кожну сходинку
# паралельно від низькоомних шин.
# ══════════════════════════════════════════════════════════════════════════
def fig_dickson_vs_cw():
    W, H = 940, 520
    P = []
    xs = [150, 320, 490, 660]      # чотири сходинки по горизонталі
    ytop = 0

    # ── верх: Кокрофт-Волтон (послідовний звʼязок) ─────────────────────────
    yrow = 130
    P.append(rect(30, 60, W - 60, 180, fill="none", stroke="#e4e4e4", sw=2, rx=10))
    P.append(text(W / 2, 86, "Кокрофт-Волтон: гойдання пробивається крізь ланцюг", size=14, color=NEG, bold=True))
    # ланцюг конденсаторів, звʼязаних послідовно (гойдання йде через нижні)
    prevx = 60
    P.append(line(prevx, yrow, xs[0], yrow, color=INK, sw=2))
    P.append(text(60, yrow - 12, "~вх", size=11, color=MUTED, anchor="start"))
    for i, x in enumerate(xs):
        cap, midy = vcap(x, yrow, yrow + 62, color=INK)
        P.append(cap)
        # клапан між сходинками (горизонталь угорі)
        if i < len(xs) - 1:
            P.append(diode_r((x + xs[i + 1]) / 2, yrow, color=INK, s=9))
            P.append(line(x, yrow, (x + xs[i + 1]) / 2 - 10, yrow, color=INK, sw=2))
            P.append(line((x + xs[i + 1]) / 2 + 10, yrow, xs[i + 1], yrow, color=INK, sw=2))
        # нижні обкладки звʼязані ПОСЛІДОВНО (гойдання йде по ланцюгу знизу)
        if i < len(xs) - 1:
            P.append(line(x, yrow + 62, xs[i + 1], yrow + 62, color="#c9a227", sw=2.4))
    # хвиля-гойдання, що слабшає ланцюгом
    for i, x in enumerate(xs):
        amp = 20 - i * 5           # згасання розмаху
        lbl = "↕%d" % amp + (" глухне" if i == len(xs) - 1 else "")
        P.append(text(x, yrow + 90, lbl, size=12, color=("#c9a227" if amp > 5 else POS), bold=True))
    # виноска про паразитику
    P.append(text(W / 2, 228, "паразитна ємність кожного вузла на підкладку краде розмах — що вища сходинка, то менше доходить",
                  size=11, color=MUTED))

    # ── низ: Діксон (паралельне підведення такту) ─────────────────────────
    yrow2 = 340
    P.append(rect(30, 268, W - 60, 220, fill="none", stroke="#e4e4e4", sw=2, rx=10))
    P.append(text(W / 2, 294, "Діксон: такт заходить у кожну сходинку паралельно", size=14, color=FIELD, bold=True))
    P.append(line(60, yrow2, xs[0], yrow2, color=INK, sw=2))
    P.append(text(60, yrow2 - 12, "Vвх", size=11, color=MUTED, anchor="start"))
    # дві тактові шини внизу
    clk_a = 438
    clk_b = 454
    P.append(line(90, clk_a, W - 66, clk_a, color=POS, sw=2.6))
    P.append(line(90, clk_b, W - 66, clk_b, color=NEG, sw=2.6))
    P.append(text(W - 60, clk_a + 5, "φ1", size=12, color=POS, bold=True, anchor="start"))
    P.append(text(W - 60, clk_b + 5, "φ2", size=12, color=NEG, bold=True, anchor="start"))
    for i, x in enumerate(xs):
        cap, midy = vcap(x, yrow2, yrow2 + 62, color=FIELD)
        P.append(cap)
        if i < len(xs) - 1:
            P.append(diode_r((x + xs[i + 1]) / 2, yrow2, color=INK, s=9))
            P.append(line(x, yrow2, (x + xs[i + 1]) / 2 - 10, yrow2, color=INK, sw=2))
            P.append(line((x + xs[i + 1]) / 2 + 10, yrow2, xs[i + 1], yrow2, color=INK, sw=2))
        # низ КОЖНОГО конденсатора — прямо на свою тактову шину (чергуємо φ1/φ2)
        bus = clk_a if i % 2 == 0 else clk_b
        bcol = POS if i % 2 == 0 else NEG
        P.append(line(x, yrow2 + 62, x, bus, color=bcol, sw=2.4))
        P.append(circle(x, bus, 3.2, fill=bcol, stroke=bcol))
        # повний розмах доходить до кожної
        P.append(text(x, yrow2 - 12, "повний ↕", size=10, color=FIELD, bold=True))
    P.append(text(W / 2, 472, "шини — низькоомні джерела: паразитика лише трохи послаблює, накачка не глухне",
                  size=11, color=MUTED))

    render("img/dickson-vs-cw.svg", W, H, *P)


# ══════════════════════════════════════════════════════════════════════════
# ФІГУРА H (вставка hist-dickson-lineage) — часова лінія родоводу множника.
# Несе вагу: показує, що ОДНА ідея (множити напругу конденсаторами й клапанами)
# проходить крізь століття під різні потреби, і що ключовий крок (каскад) та
# перенесення на кремній зробили НЕ ті, чиї імена на схемі. Розрізняє
# ідею/каскад/систему/реалізацію на одній осі часу.
# ══════════════════════════════════════════════════════════════════════════
def fig_hist_timeline():
    W, H = 980, 470
    P = []
    ax_y = 250                       # рівень осі часу
    x0, x1 = 70, W - 60
    P.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2.4))
    P.append(arrow(x1 - 2, ax_y, x1 + 4, ax_y, color=INK, sw=2.4))

    # (рік, підпис-верх, підпис-роль, колір, «вгору» чи «вниз», позиція 0..1)
    events = [
        (1901, "Вілляр", "подвоювач ×2\nдля трубки", NEG,   +1, 0.02),
        (1914, "Ґрайнахер", "подвоювач\nдля іонометра", "#c9a227", -1, 0.20),
        (1921, "Ґрайнахер", "КАСКАД ×N\n(масштабований)", FIELD, +1, 0.36),
        (1932, "Кокрофт-Волтон", "700 кВ:\nрозщепили ядро", POS, -1, 0.58),
        (1976, "Діксон", "на кремній:\nпост. вхід + такт", NEG, +1, 0.82),
    ]

    for yr, who, role, col, up, pos in events:
        x = x0 + (x1 - x0) * pos
        # вузол на осі
        P.append(circle(x, ax_y, 6, fill="#fff", stroke=col, sw=2.6))
        P.append(text(x, ax_y + 26, str(yr), size=14, color=INK, bold=True))
        # виносна ніжка вгору або вниз
        stem = 58
        yend = ax_y - stem if up > 0 else ax_y + stem + 18
        P.append(line(x, ax_y, x, yend if up > 0 else ax_y + 12, color=col, sw=1.8,
                      dash="3,3"))
        # картка з іменем + роллю
        lines = [who] + role.split("\n")
        box, bw, bh = textbox(x, (yend - 22) if up > 0 else (ax_y + stem + 44),
                              "\n".join(lines), size=12, color=col, bold=False,
                              fill="#fafafa", stroke=col, sw=1.8, pad=9)
        # ім'я жирним — домалюємо окремо поверх (перший рядок)
        P.append(box)

    # підпис-висновок унизу
    P.append(text(W / 2, H - 26,
                  "одна ідея — множити конденсаторами й клапанами — крізь століття; "
                  "імена на схемі не завжди про того, хто зробив ключовий крок",
                  size=11.5, color=MUTED))

    render("img/hist-timeline.svg", W, H, *P)


# ══════════════════════════════════════════════════════════════════════════
# ФІГУРА 3 (вставка comp-charge-transfer-switch) — три клапани поряд.
# Несе вагу: показує ЕВОЛЮЦІЮ клапана однією картинкою — наївний MOS-«діод»
# (губить повний Vth), статичний CTS (затвор від вищого вузла → майже 0, але
# тече назад), динамічний CTS (жорстко ввімкнено/жорстко вимкнено). Словами цю
# різницю в схемі затвора передати важко.
# ══════════════════════════════════════════════════════════════════════════
def nmos(x, y, color=INK, s=22, gate_dir="left"):
    """Символ n-MOS: канал (три штрихи справа) + затвор (ліворуч). Повертає
    координати виводів: drain (верх), source (низ), gate (бік)."""
    out = []
    # вертикальний канал-провід (drain угорі, source унизу)
    dy_top, dy_bot = y - s, y + s
    out.append(line(x, dy_top, x, y - s * 0.55, color=color, sw=2))
    out.append(line(x, y + s * 0.55, x, dy_bot, color=color, sw=2))
    # три штрихи каналу
    for off in (-s * 0.5, 0, s * 0.5):
        out.append(line(x, y + off - 5, x, y + off + 5, color=color, sw=3.2))
    # пластина затвора (вертикальна риска ліворуч від каналу)
    gx = x - 12
    out.append(line(gx, y - s * 0.6, gx, y + s * 0.6, color=color, sw=2.6))
    gate_pt = (gx, y)
    return "".join(out), (x, dy_top), (x, dy_bot), gate_pt


def fig_cts_variants():
    W, H = 960, 470
    P = []
    cols = [160, 480, 800]
    titles = [("Наївний MOS-«діод»", NEG),
              ("Статичний CTS", "#c9a227"),
              ("Динамічний CTS", FIELD)]
    subs = ["затвор на стік:\nгубить повний Vth",
            "затвор від вищого вузла:\nпадіння ≈ 0, але тече назад",
            "затвор гойдають окремо:\nжорстко ON, жорстко OFF"]

    for ci, cx in enumerate(cols):
        title, tcol = titles[ci]
        P.append(rect(cx - 145, 54, 290, 372, fill="none", stroke="#e4e4e4", sw=2, rx=10))
        P.append(text(cx, 80, title, size=14, color=tcol, bold=True))

        vx_in = cx - 95
        vx_out = cx + 95
        ymain = 180
        # лівий вузол (сходинка n) і правий (n+1)
        P.append(circle(vx_in, ymain, 4, fill=INK, stroke=INK))
        P.append(text(vx_in, ymain - 14, "вузол n", size=10, color=MUTED))
        P.append(circle(vx_out, ymain, 4, fill=INK, stroke=INK))
        P.append(text(vx_out, ymain - 14, "n+1", size=10, color=MUTED))

        sym, dpt, spt, gpt = nmos(cx, ymain, color=INK)
        P.append(sym)
        # витік/стік у вузли (канал вертикальний — розвертаємо провідниками)
        P.append(line(vx_in, ymain, cx, dpt[1], color=INK, sw=2))
        P.append(line(cx, spt[1], vx_out, ymain, color=INK, sw=2))
        P.append(line(vx_in, ymain, vx_in, dpt[1], color=INK, sw=2))
        P.append(line(vx_out, ymain, vx_out, spt[1], color=INK, sw=2))

        if ci == 0:
            # затвор замкнено на стік (діод-схема)
            P.append(line(gpt[0], gpt[1], gpt[0] - 26, gpt[1], color=INK, sw=2))
            P.append(line(gpt[0] - 26, gpt[1], gpt[0] - 26, dpt[1] + 4, color=INK, sw=2))
            P.append(line(gpt[0] - 26, dpt[1] + 4, cx, dpt[1] + 4, color=INK, sw=2, dash="4,3"))
            P.append(text(cx, ymain + 70, "−Vth", size=15, color=NEG, bold=True))
        elif ci == 1:
            # затвор від вищого вузла (стрілка згори праворуч)
            P.append(line(gpt[0], gpt[1], gpt[0] - 30, gpt[1], color="#c9a227", sw=2.4))
            P.append(arrow(gpt[0] - 30, gpt[1] + 30, gpt[0] - 30, gpt[1] + 2, color="#c9a227", sw=2.2))
            P.append(text(gpt[0] - 30, gpt[1] + 48, "від n+2", size=10, color="#c9a227", bold=True))
            P.append(text(cx, ymain + 70, "≈ 0", size=15, color="#c9a227", bold=True))
            # стрілка зворотного витоку
            P.append(arrow(vx_out - 8, ymain + 26, vx_in + 8, ymain + 26, color=POS, sw=2))
            P.append(text(cx, ymain + 44, "витік назад", size=10, color=POS, bold=True))
        else:
            # окремий керувальний сигнал (буст)
            P.append(line(gpt[0], gpt[1], gpt[0] - 30, gpt[1], color=FIELD, sw=2.4))
            P.append(arrow(gpt[0] - 30, gpt[1] + 30, gpt[0] - 30, gpt[1] + 2, color=FIELD, sw=2.2))
            P.append(text(gpt[0] - 30, gpt[1] + 48, "буст-фаза", size=10, color=FIELD, bold=True))
            P.append(text(cx, ymain + 70, "≈ 0", size=15, color=FIELD, bold=True))
            P.append(text(cx, ymain + 90, "і 0 назад", size=11, color=FIELD, bold=True))

        P.append(fitbox(cx - 128, 330, 256, 74, subs[ci], size=12, color=INK,
                        fill="#fafafa", stroke="#e4e4e4"))

    render("img/cts-variants.svg", W, H, *P)


# ══════════════════════════════════════════════════════════════════════════
# ФІГУРА 4 (вставка) — зворотне ділення заряду і чотирифазний такт.
# Несе вагу: показує КОРІНЬ болячки класу — коли клапан лишається ввімкненим на
# перемиканні, заряд тече з вищого вузла назад у нижчий; неперекривні сторожові
# фази це прибирають. Часові діаграми словами передати важко.
# ══════════════════════════════════════════════════════════════════════════
def fig_four_phase():
    W, H = 940, 520
    P = []

    # ── верх: сцена «клапан не встиг закритися» ───────────────────────────
    P.append(rect(30, 54, W - 60, 168, fill="none", stroke="#e4e4e4", sw=2, rx=10))
    P.append(text(W / 2, 80, "Перекриття фаз: клапан ще ввімкнений, а сусід уже піднявся", size=14, color=POS, bold=True))
    yb = 150
    xa, xb = 300, 640
    P.append(circle(xa, yb, 5, fill=INK, stroke=INK))
    P.append(text(xa, yb - 16, "вузол n", size=11, color=MUTED))
    P.append(circle(xb, yb, 5, fill=INK, stroke=INK))
    P.append(text(xb, yb - 16, "вузол n+1 (уже високий)", size=11, color=MUTED))
    # клапан між ними, «застряг увімкнений»
    sym, dpt, spt, gpt = nmos((xa + xb) / 2, yb, color=INK)
    P.append(line(xa, yb, (xa + xb) / 2, yb, color=INK, sw=2))
    P.append(line((xa + xb) / 2, yb, xb, yb, color=INK, sw=2))
    P.append(sym)
    P.append(text((xa + xb) / 2, yb + 40, "ще ON", size=12, color=POS, bold=True))
    # стрілка зворотного струму (з n+1 у n)
    P.append(arrow(xb - 12, yb - 34, xa + 12, yb - 34, color=POS, sw=2.6))
    P.append(text((xa + xb) / 2, yb - 42, "заряд тече НАЗАД", size=12, color=POS, bold=True))

    # ── низ: часові діаграми 2 фази vs 4 фази ─────────────────────────────
    def clock(ox, oy, hi, lo, label, color, guard=0):
        """Прямокутний такт: hi/lo — межі часу (частка ширини 0..1)."""
        w = 300
        h = 34
        base = oy + h
        out = [text(ox - 10, oy + h - 6, label, size=12, color=color, bold=True, anchor="end")]
        # осі
        out.append(line(ox, base, ox + w, base, color="#d0d0d0", sw=1.4))
        # межі імпульсу
        x0 = ox + hi * w
        x1 = ox + lo * w
        out.append(line(ox, base, x0, base, color=color, sw=2.6))
        out.append(line(x0, base, x0, oy, color=color, sw=2.6))
        out.append(line(x0, oy, x1, oy, color=color, sw=2.6))
        out.append(line(x1, oy, x1, base, color=color, sw=2.6))
        out.append(line(x1, base, ox + w, base, color=color, sw=2.6))
        return "".join(out), (x0, x1)

    P.append(rect(30, 250, W - 60, 240, fill="none", stroke="#e4e4e4", sw=2, rx=10))

    # 2-фазний: перекриття
    P.append(text(250, 282, "2 фази: край у край — перекриваються", size=13, color=POS, bold=True))
    c1, (a0, a1) = clock(150, 300, 0.10, 0.52, "φ1", POS)
    c2, (b0, b1) = clock(150, 348, 0.48, 0.90, "φ2", NEG)
    P.append(c1); P.append(c2)
    # зона перекриття
    P.append(rect(min(a1, b0) - 2, 300, abs(b0 - a1) + 6, 82, fill="#fdecea", stroke=POS, sw=1.4, rx=3))
    P.append(text((a1 + b0) / 2, 396, "тут обидва ON → витік", size=10, color=POS, bold=True))

    # 4-фазний: сторожові проміжки
    P.append(text(680, 282, "4 фази: сторожові паузи — ніколи разом", size=13, color=FIELD, bold=True))
    d1, (e0, e1) = clock(580, 300, 0.06, 0.40, "φ1", POS)
    d2, (f0, f1) = clock(580, 348, 0.60, 0.94, "φ2", NEG)
    P.append(d1); P.append(d2)
    # dead-time між ними
    P.append(rect(e1, 300, f0 - e1, 82, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=3))
    P.append(text((e1 + f0) / 2, 396, "пауза", size=10, color=FIELD, bold=True))
    P.append(text((e1 + f0) / 2, 410, "клапан OFF", size=10, color=FIELD, bold=True))

    P.append(text(W / 2, 456, "неперекривні фази гарантують: коли сусід підіймається, клапан уже жорстко замкнено — назад нічого не тече",
                  size=11, color=MUTED))
    P.append(text(W / 2, 476, "ціна — трохи менше часу на власне передавання заряду за період",
                  size=11, color=MUTED))

    render("img/four-phase.svg", W, H, *P)


if __name__ == "__main__":
    fig_pump_cell()
    fig_dickson_vs_cw()
    fig_hist_timeline()
    fig_cts_variants()
    fig_four_phase()
    print("OK: pump-cell, dickson-vs-cw, hist-timeline, cts-variants, four-phase")
