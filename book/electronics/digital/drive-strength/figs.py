# -*- coding: utf-8 -*-
"""Фігури до теми «Сила виходу GPIO».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Ідеальна ніжка проти справжньої: ключ + опір ──────────────────────────
# Ідея: сила виходу існує, бо ніжка — не ідеальне джерело напруги. Усередині —
# транзистор-ключ, а в нього є опір Rds(on). Течеш струм → на опорі падає напруга
# → рівень «просідає». Сильніший вихід = менший опір.
def fig_switch_r():
    W, H = 760, 340
    f = []

    f.append(text(W / 2, 30,
                  "Ніжка — не ідеальне джерело: усередині ключ із опором",
                  size=13, color=MUTED, italic=True))

    # ── ліворуч: як ми думаємо (ідеал) ──
    f.append(text(180, 66, "як уявляємо", size=12, color=FIELD, bold=True))
    f.append(line(180, 80, 180, 120, color=POS, sw=2))
    f.append(text(180, 96, "VDD", size=10, color=POS, bold=True, anchor="end"))
    f.append(circle(180, 150, 16, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(text(180, 155, "S", size=12, color=FIELD, bold=True))
    f.append(line(180, 166, 180, 210, color=INK, sw=2.4))
    f.append(circle(180, 210, 5, fill=INK, stroke=INK))
    f.append(text(210, 214, "ніжка = рівно VDD", size=10, color=INK, anchor="start"))
    f.append(text(210, 230, "хоч скільки струму", size=9.5, color=MUTED, anchor="start"))

    # ── праворуч: як є (ключ + резистор) ──
    f.append(text(560, 66, "як насправді", size=12, color=POS, bold=True))
    f.append(line(560, 80, 560, 120, color=POS, sw=2))
    f.append(text(560, 96, "VDD", size=10, color=POS, bold=True, anchor="end"))
    f.append(circle(560, 145, 15, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(560, 150, "S", size=12, color=POS, bold=True))
    # резистор Rds(on)
    f.append(line(560, 160, 560, 178, color=INK, sw=2))
    f.append(rect(544, 178, 32, 40, fill="#fff6e5", stroke="#b8860b", sw=1.8, rx=4))
    f.append(text(560, 202, "Rds", size=11, color="#8a6d0b", bold=True))
    f.append(text(600, 190, "опір", size=9.5, color="#8a6d0b", anchor="start"))
    f.append(text(600, 205, "каналу", size=9.5, color="#8a6d0b", anchor="start"))
    f.append(line(560, 218, 560, 245, color=INK, sw=2.4))
    f.append(circle(560, 245, 5, fill=INK, stroke=INK))
    # струм навантаження
    f.append(arrow(560, 245, 640, 245, color=NEG, sw=2))
    f.append(text(648, 249, "I (навантаж.)", size=10, color=NEG, anchor="start"))
    f.append(text(560, 268, "ніжка = VDD − I·Rds", size=10.5, color=INK))
    f.append(text(560, 284, "(просідає під струмом)", size=9.5, color=MUTED))

    f.append(fitbox(120, 300, 520, 30,
                    "Сила виходу — це наскільки малий Rds: менший опір → більший струм при тому ж просіданні",
                    size=10, fill="#fbfbfb", stroke=MUTED, sw=1.4))

    render(os.path.join(IMG, "switch-r.svg"), W, H, *f)


# ── 2. Просідання рівня: VOH падає лінійно зі струмом, є межа легального «1» ───
# Ідея: даташит гарантує VOH лише при тестовому струмі IOH. Течеш більше —
# точка їде вниз по прямій нахилу Rds; десь вона перетне поріг VIH приймача,
# і «1» перестає читатися. Сила виходу = де ця пряма перетинає межу.
def fig_droop():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 30,
                  "Що більше тягнеш струму, то нижче просідає «1» — аж за межу",
                  size=12.5, color=MUTED, italic=True))

    # осі
    x0, y0 = 110, 320          # початок координат
    xr, yt = 690, 70
    f.append(line(x0, y0, xr, y0, color=INK, sw=2))       # вісь струму
    f.append(arrow(xr, y0, xr + 8, y0, color=INK, sw=2))
    f.append(text(xr, y0 + 26, "струм навантаження I →", size=10.5, color=INK, anchor="end"))
    f.append(line(x0, y0, x0, yt, color=INK, sw=2))       # вісь напруги
    f.append(arrow(x0, yt, x0, yt - 8, color=INK, sw=2))
    f.append(text(x0 - 8, yt - 2, "напруга «1»", size=10.5, color=INK, anchor="end"))

    # рівень VDD (стеля)
    vdd_y = 95
    f.append(line(x0, vdd_y, xr, vdd_y, color=POS, sw=1.4, dash="5,4"))
    f.append(text(x0 - 8, vdd_y + 4, "VDD", size=10, color=POS, anchor="end"))

    # поріг VIH приймача (нижче нього — вже не «1»)
    vih_y = 250
    f.append(rect(x0, vih_y, xr - x0, y0 - vih_y, fill="#fdecea", stroke="none"))
    f.append(line(x0, vih_y, xr, vih_y, color=POS, sw=1.6, dash="4,4"))
    f.append(text(xr - 6, vih_y - 6, "поріг VIH приймача — нижче «1» не читається",
                  size=10, color=POS, anchor="end"))

    # дві прямі просідання: сильний вихід (пологий) і слабкий (крутий)
    # сильний: малий Rds → пологий нахил, довго тримає рівень
    sx0, sy0 = x0, 105
    sx1, sy1 = 620, 200
    f.append(line(sx0, sy0, sx1, sy1, color=FIELD, sw=2.6))
    f.append(text(sx1 + 8, sy1, "сильний вихід (малий Rds)", size=10, color=FIELD, anchor="start"))
    f.append(circle(sx0, sy0, 4, fill=FIELD, stroke=FIELD))

    # слабкий: великий Rds → круто падає, рано перетинає поріг
    wx0, wy0 = x0, 108
    wx1, wy1 = 360, vih_y
    f.append(line(wx0, wy0, wx1, wy1, color=NEG, sw=2.6))
    f.append(text(wx1 + 8, wy1 - 12, "слабкий вихід (великий Rds)", size=10, color=NEG, anchor="start"))
    f.append(circle(wx1, wy1, 5, fill="#fff", stroke=NEG, sw=2))
    f.append(line(wx1, wy1, wx1, y0, color=NEG, sw=1.2, dash="3,3"))
    f.append(text(wx1, y0 + 16, "тут «1» зламалась", size=9.5, color=NEG))

    # тестова точка IOH (де даташит гарантує VOH)
    ioh_x = 230
    f.append(line(ioh_x, vdd_y, ioh_x, y0, color=MUTED, sw=1, dash="2,3"))
    f.append(text(ioh_x, y0 + 34, "IOH (тест)", size=9, color=MUTED))

    render(os.path.join(IMG, "droop.svg"), W, H, *f)


# ── 3. Сегментований драйвер: регістр вибирає, скільки ключів паралельно ──────
# Ідея: керована сила виходу в чипі — це N однакових транзисторів пліч-о-пліч.
# Регістр DRIVE вмикає скільки треба: більше відкрито → менший сумарний опір →
# більший струм і крутіший фронт. Реальні приклади з MCU.
def fig_segmented():
    W, H = 760, 430
    f = []

    f.append(text(W / 2, 30,
                  "«Сила» в чипі — це N паралельних ключів; регістр вмикає скільки треба",
                  size=12.5, color=MUTED, italic=True))

    vdd_y = 78
    node_x = 470
    f.append(line(150, vdd_y, 410, vdd_y, color=POS, sw=2))
    f.append(text(140, vdd_y + 4, "VDD", size=11, color=POS, bold=True, anchor="end"))

    seg_x = [180, 250, 320, 390]
    on = [True, True, True, False]     # 3 з 4 відкрито
    for i, x in enumerate(seg_x):
        col = FIELD if on[i] else MUTED
        sw = 2 if on[i] else 1.3
        f.append(line(x, vdd_y, x, 132, color=col, sw=sw))
        f.append(rect(x - 15, 132, 30, 38, fill="#eef6ef" if on[i] else FILL,
                      stroke=col, sw=1.8 if on[i] else 1.3, rx=6))
        f.append(text(x, 156, "Q%d" % (i + 1), size=10, color=col, bold=on[i]))
        f.append(line(x, 170, x, 214, color=col, sw=sw))
        f.append(line(x, 214, node_x, 214, color=col, sw=sw))
        f.append(text(x, 122, "on" if on[i] else "off", size=9, color=col, bold=on[i]))

    # спільний вузол → ніжка
    f.append(circle(node_x, 214, 5, fill=INK, stroke=INK))
    f.append(line(node_x, 214, 560, 214, color=INK, sw=2.4))
    f.append(text(575, 218, "ніжка", size=11, color=INK, bold=True, anchor="start"))

    # регістр DRIVE ліворуч знизу
    f.append(rect(70, 250, 150, 96, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    f.append(text(145, 272, "регістр DRIVE", size=11, color=NEG, bold=True))
    f.append(text(145, 292, "= 3 з 4", size=11, color=INK, bold=True))
    f.append(text(145, 312, "скільки ключів", size=9.5, color=MUTED))
    f.append(text(145, 328, "відкрити", size=9.5, color=MUTED))
    f.append(arrow(220, 292, 300, 200, color=NEG, sw=1.5))

    # реальні приклади праворуч
    f.append(rect(555, 250, 175, 96, fill="#fbfbfb", stroke=MUTED, sw=1.4, rx=8))
    f.append(text(642, 270, "у житті:", size=10.5, color=INK, bold=True))
    f.append(text(642, 288, "RP2040: 2·4·8·12 мА", size=9.5, color=INK))
    f.append(text(642, 304, "(типово 4 мА)", size=9, color=MUTED))
    f.append(text(642, 322, "ESP32: ~5·10·20·40 мА", size=9.5, color=INK))
    f.append(text(642, 338, "(типово ~20 мА)", size=9, color=MUTED))

    f.append(fitbox(240, 356, 300, 60,
                    "більше ключів\n→ менший опір\n→ більший струм і крутіший фронт",
                    size=10.5, fill="#eef6ef", stroke=FIELD, sw=1.5))

    render(os.path.join(IMG, "segmented.svg"), W, H, *f)


# ── 4. Вісь вибору: слабкий ↔ сильний, обидва краї — біда; ціль посередині ────
# Ідея: сильніше — НЕ краще. Замало сили: рівень просідає, фронт мляве повзе.
# Забагато: круті фронти → викид, дзвін, стрибок землі, EMI. Бери мінімум, що
# ще тягне навантаження в строк.
def fig_tradeoff():
    W, H = 760, 360
    f = []

    f.append(text(W / 2, 30,
                  "Сильніше — не краще: обидва краї осі — біда",
                  size=13, color=MUTED, italic=True))

    ax_y = 200
    f.append(line(80, ax_y, 680, ax_y, color=INK, sw=2))
    f.append(arrow(80, ax_y, 70, ax_y, color=INK, sw=2))
    f.append(arrow(680, ax_y, 690, ax_y, color=INK, sw=2))
    f.append(text(96, ax_y + 24, "слабкіший вихід", size=10.5, color=NEG, anchor="start"))
    f.append(text(664, ax_y + 24, "сильніший вихід", size=10.5, color=POS, anchor="end"))

    # зелене вікно посередині
    wx0, wx1 = 305, 455
    f.append(rect(wx0, 96, wx1 - wx0, ax_y - 96, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=6))
    f.append(text((wx0 + wx1) / 2, 86, "у міру", size=11, color=FIELD, bold=True))
    f.append(text((wx0 + wx1) / 2, ax_y - 44, "тягне в строк,", size=9.5, color=FIELD))
    f.append(text((wx0 + wx1) / 2, ax_y - 28, "фронт чистий", size=9.5, color=FIELD))

    # ліва біда
    f.append(fitbox(90, 250, 200, 80,
                    "ЗАСЛАБКО:\n"
                    "• рівень просідає під струмом\n"
                    "• фронт повзе, не встигає\n"
                    "• «1» падає в заборонену зону",
                    size=9.5, fill="#eaf0fd", stroke=NEG, sw=1.4))

    # права біда
    f.append(fitbox(470, 250, 210, 80,
                    "ЗАСИЛЬНО:\n"
                    "• викид над VDD, дзвін\n"
                    "• стрибок землі, крос-завади\n"
                    "• EMI, перегрів ключа",
                    size=9.5, fill="#fdecea", stroke=POS, sw=1.4))

    # стрілки від країв до осі
    f.append(arrow(180, 244, 160, ax_y + 4, color=NEG, sw=1.3))
    f.append(arrow(575, 244, 600, ax_y + 4, color=POS, sw=1.3))

    f.append(fitbox(210, 118, 380, 30,
                    "Правило: найслабший вихід, що ще тягне навантаження вчасно",
                    size=10.5, fill="#fbfbfb", stroke=MUTED, sw=1.4, bold=True))

    render(os.path.join(IMG, "tradeoff.svg"), W, H, *f)


# ── 5. Дістати Rds(on) з даташитної точки: дві точки задають нахил прямої ─────
# Ідея (для math-вставки): опір каналу — це НАХИЛ прямої U = VDD − I·Rds.
# Дві точки відомі: холостий хід (0, VDD) і даташитна (IOH, VOH). Нахил між
# ними = −Rds(on). Продовжив пряму до порога VIH — прочитав гранично допустимий
# струм. Тобто з однієї пари VOH/IOH дістаєш поведінку за БУДЬ-якого струму.
def fig_extract_rds():
    W, H = 760, 410
    f = []

    f.append(text(W / 2, 28,
                  "Дві точки задають пряму: її нахил і є Rds(on)",
                  size=13, color=MUTED, italic=True))

    x0, y0 = 120, 330          # початок координат (I=0)
    xr, yt = 690, 70
    # осі
    f.append(line(x0, y0, xr, y0, color=INK, sw=2))
    f.append(arrow(xr - 40, y0, xr, y0, color=INK, sw=2))
    f.append(text(xr, y0 + 26, "струм I →", size=11, color=INK, anchor="end"))
    f.append(line(x0, y0, x0, yt, color=INK, sw=2))
    f.append(arrow(x0, yt + 40, x0, yt, color=INK, sw=2))
    f.append(text(x0 - 10, yt + 2, "напруга «1»", size=11, color=INK, anchor="end"))

    # рівні напруги (пікселі)
    vdd_y = 90                 # VDD (холостий хід)
    voh_y = 150                # VOH при IOH
    vih_y = 250                # поріг VIH приймача
    ioh_x = 300                # тестовий струм IOH
    imax_x = 560               # де пряма перетинає VIH

    # стеля VDD
    f.append(line(x0, vdd_y, xr - 30, vdd_y, color=POS, sw=1.2, dash="5,4"))
    f.append(text(x0 - 10, vdd_y + 4, "VDD", size=10.5, color=POS, anchor="end", bold=True))
    # поріг VIH + заборонена смуга
    f.append(rect(x0, vih_y, xr - 30 - x0, y0 - vih_y, fill="#fdecea", stroke="none"))
    f.append(line(x0, vih_y, xr - 30, vih_y, color=POS, sw=1.4, dash="4,4"))
    f.append(text(xr - 34, vih_y - 7, "поріг VIH — нижче «1» не читається",
                  size=10, color=POS, anchor="end"))

    # ── сама пряма U = VDD − I·Rds, продовжена до VIH ──
    f.append(line(x0, vdd_y, imax_x, vih_y, color=FIELD, sw=2.8))
    # холостий хід (0, VDD)
    f.append(circle(x0, vdd_y, 5, fill=FIELD, stroke=FIELD))
    f.append(text(x0 + 12, vdd_y - 8, "(0, VDD) — холостий хід", size=10, color=FIELD, anchor="start"))
    # даташитна точка (IOH, VOH)
    f.append(line(ioh_x, y0, ioh_x, voh_y, color=MUTED, sw=1, dash="2,3"))
    f.append(line(x0, voh_y, ioh_x, voh_y, color=MUTED, sw=1, dash="2,3"))
    f.append(circle(ioh_x, voh_y, 5.5, fill="#fff", stroke=INK, sw=2.2))
    f.append(text(ioh_x + 12, voh_y - 6, "(IOH, VOH) — з даташиту", size=10, color=INK, anchor="start"))
    f.append(text(ioh_x, y0 + 18, "IOH", size=9.5, color=MUTED))
    f.append(text(x0 - 10, voh_y + 4, "VOH", size=9.5, color=MUTED, anchor="end"))

    # трикутник нахилу: ΔU / ΔI = −Rds
    f.append(line(x0, vdd_y, x0, voh_y, color=NEG, sw=1.6))
    f.append(line(x0, voh_y, ioh_x, voh_y, color=NEG, sw=1.6))
    f.append(text(x0 - 10, (vdd_y + voh_y) / 2, "ΔU", size=10, color=NEG, anchor="end"))
    f.append(text((x0 + ioh_x) / 2, voh_y + 15, "ΔI", size=10, color=NEG))

    # точка перетину з порогом → I_макс
    f.append(circle(imax_x, vih_y, 5, fill=POS, stroke=POS))
    f.append(line(imax_x, vih_y, imax_x, y0, color=POS, sw=1.1, dash="3,3"))
    f.append(text(imax_x, y0 + 18, "I_макс", size=9.5, color=POS))

    f.append(fitbox(430, 300, 250, 58,
                    "Rds(on) = (VDD − VOH) / IOH\n"
                    "= нахил прямої\n"
                    "→ напруга за будь-якого струму",
                    size=10, fill="#eef6ef", stroke=FIELD, sw=1.5))

    render(os.path.join(IMG, "extract-rds.svg"), W, H, *f)


# ── 6. Провідності додаються, але Rs ставить стелю: паралель не масштабує ─────
# Ідея (для math-вставки): N паралельних ключів → G_заг = N·g, провідність
# росте ЛІНІЙНО (пунктир). Але спільний послідовний Rs (дротик+розводка) не
# залежить від N: повна провідність = 1/(Rds/N + Rs) виходить на насичення.
# Далі опір уже не в каналах, а в bond wire.
def fig_parallel_g():
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 28,
                  "Провідність шляху проти числа паралельних ключів",
                  size=13, color=MUTED, italic=True))

    x0, y0 = 110, 320
    xr, yt = 660, 80
    f.append(line(x0, y0, xr, y0, color=INK, sw=2))
    f.append(arrow(xr - 40, y0, xr, y0, color=INK, sw=2))
    f.append(text(xr, y0 + 26, "число ключів N →", size=11, color=INK, anchor="end"))
    f.append(line(x0, y0, x0, yt, color=INK, sw=2))
    f.append(arrow(x0, yt + 40, x0, yt, color=INK, sw=2))
    f.append(text(x0 - 10, yt + 2, "провідність шляху G", size=11, color=INK, anchor="end"))

    # параметри моделі (умовні одиниці): g на ключ, стеля Gmax = 1/Rs
    g = 26.0                      # приріст на ключ (пікселі провідності)
    n_max = 9
    dx = (xr - 30 - x0) / n_max   # крок по N
    gmax_px = 165.0               # стеля насичення в пікселях (1/Rs)

    def yG(val):                  # провідність (px) → y-координата
        return y0 - val

    # ідеальна лінія N·g (пунктир) — росте без стелі
    f.append(line(x0, yG(0), x0 + n_max * dx, yG(n_max * g), color=MUTED, sw=1.6, dash="6,5"))
    f.append(text(x0 + n_max * dx - 4, yG(n_max * g) - 8,
                  "ідеал: G = N·g (лінійно)", size=10, color=MUTED, anchor="end"))

    # реальна крива з насиченням: G(N) = 1 / (1/(N·g) + 1/gmax)
    pts = []
    for N in range(0, n_max + 1):
        if N == 0:
            val = 0.0
        else:
            val = 1.0 / (1.0 / (N * g) + 1.0 / gmax_px)
        pts.append((x0 + N * dx, yG(val)))
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=FIELD, sw=2.8))
    for i, N in enumerate(range(0, n_max + 1)):
        if N >= 1:
            f.append(circle(pts[i][0], pts[i][1], 3.5, fill=FIELD, stroke=FIELD))

    # стеля Gmax = 1/Rs
    f.append(line(x0, yG(gmax_px), xr - 30, yG(gmax_px), color=POS, sw=1.4, dash="4,4"))
    f.append(text(xr - 34, yG(gmax_px) - 8,
                  "стеля G = 1/Rs — далі опір у дротику, не в каналах",
                  size=10, color=POS, anchor="end"))

    # підписи «лінійно» на початку і «згин» далі
    f.append(mtext(x0 + 1.7 * dx, yG(1.4 * g) + 30, ["спочатку", "≈ лінійно"], size=9.5, color=FIELD))
    f.append(mtext(x0 + 6.6 * dx, yG(gmax_px) + 30, ["згин:", "виграш тане"], size=9.5, color=POS))

    # мітки N на осі
    for N in (1, 3, 5, 7, 9):
        f.append(text(x0 + N * dx, y0 + 15, str(N), size=9.5, color=MUTED))

    f.append(fitbox(150, 342, 460, 30,
                    "R_повн = Rds(on)/N + Rs — канали паралеляться, спільний Rs — ні",
                    size=10.5, fill="#fbfbfb", stroke=MUTED, sw=1.4))

    render(os.path.join(IMG, "parallel-g.svg"), W, H, *f)


# ── 7. Фронт як RC-зарядка: tr = ln9·RC ≈ 2.2·RC між рівнями 10 % і 90 % ──────
# Ідея (для math-вставки): вихід заряджає ємність крізь Rds(on) → експонента
# U = VDD·(1 − e^(−t/RC)). Час 10→90 % = ln9·RC ≈ 2.2·RC, НЕЗАЛЕЖНО від масштабу.
# Сильний вихід (мала RC) — крутий фронт; слабкий (велика RC) — пологий.
def fig_rc_edge():
    import math as _m
    W, H = 760, 400
    f = []

    f.append(text(W / 2, 28,
                  "Фронт = RC-зарядка крізь Rds(on); час 10→90 % = 2.2·RC",
                  size=13, color=MUTED, italic=True))

    x0, y0 = 110, 320
    xr, yt = 690, 80
    f.append(line(x0, y0, xr, y0, color=INK, sw=2))
    f.append(arrow(xr - 40, y0, xr, y0, color=INK, sw=2))
    f.append(text(xr, y0 + 26, "час t →", size=11, color=INK, anchor="end"))
    f.append(line(x0, y0, x0, yt, color=INK, sw=2))
    f.append(arrow(x0, yt + 40, x0, yt, color=INK, sw=2))
    f.append(text(x0 - 10, yt + 2, "напруга U", size=11, color=INK, anchor="end"))

    vdd_y = 95                 # рівень VDD
    span = y0 - vdd_y          # повний розмах у пікселях

    def yU(frac):              # частка розмаху → y
        return y0 - frac * span

    # рівні VDD, 90 %, 10 %
    f.append(line(x0, vdd_y, xr - 30, vdd_y, color=POS, sw=1.2, dash="5,4"))
    f.append(text(x0 - 10, vdd_y + 4, "VDD", size=10.5, color=POS, anchor="end", bold=True))
    f.append(line(x0, yU(0.9), xr - 30, yU(0.9), color=MUTED, sw=1, dash="3,3"))
    f.append(text(x0 - 10, yU(0.9) + 4, "90%", size=9.5, color=MUTED, anchor="end"))
    f.append(line(x0, yU(0.1), xr - 30, yU(0.1), color=MUTED, sw=1, dash="3,3"))
    f.append(text(x0 - 10, yU(0.1) + 4, "10%", size=9.5, color=MUTED, anchor="end"))

    # часовий масштаб: RC у пікселях
    RC = 78.0
    def xt(tau):               # час у одиницях RC → x
        return x0 + tau * RC

    # сильний вихід: мала стала (RC) — крута експонента
    ptsS = []
    tau = 0.0
    while tau <= 5.0:
        ptsS.append((xt(tau), yU(1 - _m.exp(-tau))))
        tau += 0.1
    for i in range(len(ptsS) - 1):
        f.append(line(ptsS[i][0], ptsS[i][1], ptsS[i + 1][0], ptsS[i + 1][1], color=FIELD, sw=2.8))
    f.append(text(xt(4.6), yU(1 - _m.exp(-4.6)) - 10,
                  "сильний вихід (мала RC)", size=10, color=FIELD, anchor="end"))

    # слабкий вихід: удвічі більша стала — удвічі повільніший фронт
    ptsW = []
    tau = 0.0
    while tau <= 5.0:
        ptsW.append((x0 + tau * RC * 2.0, yU(1 - _m.exp(-tau))))
        tau += 0.1
    # обрізати за правий край осі
    ptsW = [(min(xx, xr - 30), yy) for xx, yy in ptsW]
    for i in range(len(ptsW) - 1):
        f.append(line(ptsW[i][0], ptsW[i][1], ptsW[i + 1][0], ptsW[i + 1][1],
                      color=NEG, sw=2.4, dash="2,3"))
    f.append(text(xr - 34, yU(0.62), "слабкий вихід (удвічі більша RC)",
                  size=10, color=NEG, anchor="end"))

    # позначити tr = t90 − t10 на сильній кривій
    t10 = _m.log(1 / 0.9)      # ≈0.105
    t90 = _m.log(10)           # ≈2.303
    x10, x90 = xt(t10), xt(t90)
    f.append(line(x10, yU(0.1), x10, y0, color=FIELD, sw=1, dash="2,2"))
    f.append(line(x90, yU(0.9), x90, y0, color=FIELD, sw=1, dash="2,2"))
    # двобічна стрілка tr
    f.append(arrow(x10, y0 - 18, x90, y0 - 18, color=INK, sw=1.6))
    f.append(arrow(x90, y0 - 18, x10, y0 - 18, color=INK, sw=1.6))
    f.append(text((x10 + x90) / 2, y0 - 24, "tr ≈ 2.2·RC", size=10.5, color=INK, bold=True))

    f.append(fitbox(430, 250, 250, 70,
                    "U = VDD·(1 − e^(−t/RC))\n"
                    "tr = RC·ln9 ≈ 2.2·RC\n"
                    "удвічі більша RC → удвічі\n"
                    "повільніший фронт",
                    size=10, fill="#eef6ef", stroke=FIELD, sw=1.5))

    render(os.path.join(IMG, "rc-edge.svg"), W, H, *f)


if __name__ == "__main__":
    fig_switch_r()
    fig_droop()
    fig_segmented()
    fig_tradeoff()
    fig_extract_rds()
    fig_parallel_g()
    fig_rc_edge()
    print("OK: 7 figures ->", IMG)
