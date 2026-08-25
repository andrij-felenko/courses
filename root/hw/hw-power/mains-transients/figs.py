# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SPIKE = "#c0392b"   # кидок — небезпечний
CALM  = "#2457d6"   # спокійна синусоїда
CLAMP = "#27ae60"   # обмежений (безпечний) рівень


# ─────────────────────────────────────────────────────────────────────────────
# Фіг.1 — кидок на тлі синусоїди: масштаб часу й напруги
# Показує, що спайк живе мікросекунди на тлі 20-мс періоду і в рази вищий за пік.
# ─────────────────────────────────────────────────────────────────────────────
def fig_spike_on_sine():
    W, H = 720, 380
    x0, x1 = 70, 690
    ymid = 220
    amp = 70                       # піврозмах синусоїди в px (≈ пік мережі)
    peak_px = ymid - amp

    frags = []
    # осі
    frags.append(line(x0, ymid, x1, ymid, color=MUTED, sw=1.2))                 # нуль (час)
    frags.append(line(x0, 70, x0, 340, color=MUTED, sw=1.2))                    # напруга
    frags.append(text(x0 - 8, 74, "U", size=13, color=MUTED, anchor="end"))
    frags.append(text(x1, ymid + 20, "час", size=12, color=MUTED, anchor="end"))

    # рівень піка мережі (пунктир) і смертельний рівень (пунктир вище)
    frags.append(line(x0, peak_px, x1, peak_px, color=CALM, sw=1.0, dash="4 4"))
    frags.append(text(x1 - 4, peak_px - 6, "пік мережі ≈ 325 В", size=11, color=CALM, anchor="end"))
    kill = 96
    frags.append(line(x0, kill, x1, kill, color=SPIKE, sw=1.0, dash="4 4"))
    frags.append(text(x0 + 6, kill - 6, "поріг пробою ізоляції", size=11, color=SPIKE, anchor="start"))

    # синусоїда — два періоди
    pts = []
    for i in range(0, 621):
        x = x0 + i
        t = (i / 620.0) * 2 * 2 * math.pi           # два періоди
        y = ymid - amp * math.sin(t)
        pts.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (" ".join(pts), CALM))

    # кидок: гострий спайк угору поверх синусоїди приблизно на чверті першого періоду
    sx = x0 + 155
    base_y = ymid - amp * math.sin((155 / 620.0) * 2 * 2 * math.pi)
    top_y = kill - 22
    spike = ["M %.1f %.1f" % (sx - 10, base_y),
             "L %.1f %.1f" % (sx, top_y),
             "L %.1f %.1f" % (sx + 14, base_y + 8)]
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(spike), SPIKE))
    frags.append(text(sx + 4, top_y - 8, "кидок", size=12, color=SPIKE, bold=True, anchor="start"))

    # виноска масштабу часу під віссю
    frags.append(line(x0 + 155, ymid + 34, x0 + 165, ymid + 34, color=SPIKE, sw=2.2))
    frags.append(text(x0 + 210, ymid + 38, "кидок ~ мікросекунди", size=11, color=SPIKE, anchor="start"))
    frags.append(line(x0, ymid + 62, x0 + 310, ymid + 62, color=CALM, sw=1.6))
    frags.append(text(x0 + 155, ymid + 78, "півперіод мережі 10 мс", size=11, color=CALM))

    render(os.path.join(OUT, "spike-on-sine.svg"), W, H, *frags,
           title="Кидок напруги на тлі мережевої синусоїди")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг.2 — ВАХ обмежувача (варистор/TVS): «коліно», що зрізає високу напругу
# Ліворуч — крута ВАХ, праворуч — та сама подія в часі: вхід злітає, вихід зрізано.
# ─────────────────────────────────────────────────────────────────────────────
def fig_clamp_knee():
    W, H = 720, 400
    frags = []

    # ── ліва панель: ВАХ ──
    ax, ay = 90, 300           # початок координат (I вгору, U праворуч)
    axw, axh = 230, 210
    frags.append(line(ax, ay, ax + axw, ay, color=MUTED, sw=1.2))        # вісь U
    frags.append(line(ax, ay, ax, ay - axh, color=MUTED, sw=1.2))        # вісь I
    frags.append(text(ax + axw, ay + 18, "U", size=12, color=MUTED, anchor="end"))
    frags.append(text(ax - 8, ay - axh + 6, "I", size=12, color=MUTED, anchor="end"))

    # ВАХ: майже горизонтально (струму нема), тоді різко вгору коло Uкл
    uclamp_x = ax + 150
    knee_y = ay - 30
    curve = ["M %.1f %.1f" % (ax, ay - 2),
             "L %.1f %.1f" % (uclamp_x - 20, ay - 4),
             "Q %.1f %.1f %.1f %.1f" % (uclamp_x, ay - 6, uclamp_x + 6, knee_y),
             "L %.1f %.1f" % (uclamp_x + 30, ay - axh + 8)]
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(curve), CLAMP))
    frags.append(line(uclamp_x + 6, ay, uclamp_x + 6, ay - axh + 8, color=SPIKE, sw=1.0, dash="4 4"))
    frags.append(text(uclamp_x + 6, ay + 18, "U_кл", size=12, color=SPIKE))
    frags.append(text(ax + 40, ay - 12, "струму майже нема", size=10, color=MUTED, anchor="start"))
    frags.append(text(uclamp_x + 40, ay - 120, "різко тече", size=11, color=CLAMP, anchor="start"))
    frags.append(text(ax + axw / 2, ay - axh - 8, "ВАХ обмежувача", size=12, color=INK, bold=True))

    # ── права панель: та сама подія в часі ──
    bx0, bx1 = 400, 690
    bmid = 210
    frags.append(line(bx0, bmid, bx1, bmid, color=MUTED, sw=1.0))
    frags.append(line(bx0, 90, bx0, 330, color=MUTED, sw=1.0))
    frags.append(text(bx0 - 8, 94, "U", size=12, color=MUTED, anchor="end"))
    frags.append(text(bx1, bmid + 18, "час", size=11, color=MUTED, anchor="end"))

    clamp_lvl = 150
    frags.append(line(bx0, clamp_lvl, bx1, clamp_lvl, color=CLAMP, sw=1.0, dash="5 4"))
    frags.append(text(bx1 - 4, clamp_lvl - 6, "U_кл", size=11, color=CLAMP, anchor="end"))

    # вхідний кидок (пунктир, злітає високо) і зрізаний вихід (суцільний, до U_кл)
    peak = 100
    sx = bx0 + 90
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4 3"/>'
                 % (sx - 24, bmid - 10, sx, peak, sx + 30, bmid - 4, SPIKE))
    frags.append(text(sx + 2, peak - 6, "без захисту", size=11, color=SPIKE, anchor="start"))
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (sx - 24, bmid - 10, sx - 6, clamp_lvl, sx + 8, clamp_lvl, sx + 30, bmid - 4, CLAMP))
    frags.append(text(sx + 40, clamp_lvl + 22, "зрізано → безпечно", size=11, color=CLAMP, anchor="start"))
    frags.append(text((bx0 + bx1) / 2, 78, "той самий кидок у часі", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "clamp-knee.svg"), W, H, *frags,
           title="Обмежувач: «коліно» ВАХ зрізає кидок до безпечного рівня")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг.3 — два рубежі: варистор на вході «п'є» енергію, TVS/клемп добиває дрібне
# Каскад: груба велика енергія гаситься першою, тонкий залишок — другою.
# ─────────────────────────────────────────────────────────────────────────────
def fig_two_stage():
    W, H = 720, 300
    y = 150
    frags = []

    # шина L (гаряча) зверху, N знизу
    frags.append(line(60, y - 40, 660, y - 40, color=SPIKE, sw=2.0))
    frags.append(line(60, y + 60, 660, y + 60, color=INK, sw=2.0))
    frags.append(text(64, y - 48, "L (від мережі)", size=11, color=SPIKE, anchor="start"))
    frags.append(text(64, y + 78, "N", size=11, color=INK, anchor="start"))

    # вхід — стрілка кидка
    frags.append(arrow(70, y - 40, 120, y - 40, color=SPIKE, sw=2.4))
    frags.append(text(95, y - 52, "кидок", size=11, color=SPIKE, bold=True))

    # 1) варистор (MOV) — паралельно між L і N
    vx = 210
    frags.append(line(vx, y - 40, vx, y + 60, color=CLAMP, sw=2.2))
    frags.append(text(vx, y + 96, "варистор — «п'є» кидок", size=11, color=CLAMP))
    frags.append('<rect x="%.1f" y="%.1f" width="16" height="34" rx="3" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (vx - 8, y - 6, BG, CLAMP))

    # опір-розв'язка (невеликий послідовний елемент) між рубежами
    rx = 340
    frags.append('<rect x="%.1f" y="%.1f" width="46" height="16" rx="3" fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (rx - 23, y - 48, BG, INK))
    frags.append(text(rx, y - 60, "розв'язка (L, R)", size=10, color=MUTED))

    # 2) TVS / клемп — паралельно ближче до навантаження
    tx = 470
    frags.append(line(tx, y - 40, tx, y + 60, color=NEG, sw=2.2))
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (tx - 9, y + 2, tx + 9, y + 2, tx, y + 16, BG, NEG))    # трикутник діода
    frags.append(line(tx - 9, y + 16, tx + 9, y + 16, color=NEG, sw=2.0))
    frags.append(text(tx, y + 96, "TVS — добиває залишок", size=11, color=NEG))

    # навантаження
    lx = 600
    frags.append(rect(lx - 28, y - 24, 56, 48, fill=FILL, stroke=INK, sw=1.6))
    frags.append(text(lx, y + 4, "схема", size=12, color=INK, bold=True))
    frags.append(line(lx - 28, y - 40, lx - 28, y - 24, color=INK, sw=1.6))
    frags.append(line(lx - 28, y + 24, lx - 28, y + 60, color=INK, sw=1.6))

    render(os.path.join(OUT, "two-stage.svg"), W, H, *frags,
           title="Два рубежі: варистор бере грубу енергію, TVS зрізає залишок")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг.4 — дві стандартні форми: ring wave 100 кГц і комбінований імпульс 1.2/50–8/20
# Показує, ЧОМУ форм дві: усередині будинку сплеск дзвенить (LC проводки),
# зовні/на вводі — однобокий удар блискавки з довгим хвостом.
# ─────────────────────────────────────────────────────────────────────────────
def fig_surge_waveforms():
    W, H = 720, 380
    frags = []

    # ── ліва панель: RING WAVE (загасальний дзвін 100 кГц) ──
    ax0, ax1 = 60, 350
    amid = 230
    frags.append(line(ax0, amid, ax1, amid, color=MUTED, sw=1.0))
    frags.append(line(ax0, 90, ax0, 320, color=MUTED, sw=1.0))
    frags.append(text(ax0 - 6, 94, "U", size=12, color=MUTED, anchor="end"))
    frags.append(text(ax1, amid + 18, "t", size=12, color=MUTED, anchor="end"))
    frags.append(text((ax0 + ax1) / 2, 74, "Ring wave — 100 кГц", size=13, color=INK, bold=True))
    frags.append(text((ax0 + ax1) / 2, 342, "усередині будинку: LC-проводки дзвенить", size=10, color=MUTED))

    # загасальна синусоїда: швидкий фронт (0.5 мкс), тоді дзвін, що спадає
    peak = 120
    pts = []
    N = 290
    for i in range(N + 1):
        x = ax0 + 6 + i
        u = i / float(N)                       # 0..1 по осі
        env = math.exp(-u * 3.4)               # обвідна загасання
        if u < 0.035:                          # крутий фронт 0.5 мкс
            y = amid - peak * (u / 0.035)
        else:
            y = amid - peak * env * math.cos((u - 0.035) * 2 * math.pi * 5.0)
        pts.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(pts), SPIKE))
    # мітка піка й фронту
    frags.append(line(ax0, amid - peak, ax0 + 16, amid - peak, color=SPIKE, sw=1.0, dash="3 3"))
    frags.append(text(ax0 + 20, amid - peak + 4, "6 кВ", size=11, color=SPIKE, anchor="start"))
    frags.append(text(ax0 + 60, amid - peak - 8, "фронт 0.5 мкс", size=10, color=MUTED, anchor="start"))

    # ── права панель: COMBINATION WAVE (однобокий, довгий хвіст) ──
    bx0, bx1 = 400, 690
    bmid = 250
    frags.append(line(bx0, bmid, bx1, bmid, color=MUTED, sw=1.0))
    frags.append(line(bx0, 90, bx0, 320, color=MUTED, sw=1.0))
    frags.append(text(bx0 - 6, 94, "U", size=12, color=MUTED, anchor="end"))
    frags.append(text(bx1, bmid + 18, "t", size=12, color=MUTED, anchor="end"))
    frags.append(text((bx0 + bx1) / 2, 74, "Combination wave", size=13, color=INK, bold=True))
    frags.append(text((bx0 + bx1) / 2, 342, "на вводі: удар блискавки, довгий хвіст", size=10, color=MUTED))

    # напруга розімкнено 1.2/50 — швидкий фронт, повільний спад (double-exponential)
    vpeak = 130
    up = []
    M = 290
    for i in range(M + 1):
        x = bx0 + 6 + i
        u = i / float(M)
        # нормована двоекспонента: різкий фронт ~1.2, хвіст до половини ~50
        val = (math.exp(-u * 1.6) - math.exp(-u * 26.0))
        y = bmid - vpeak * (val / 0.62)
        up.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(up), SPIKE))
    frags.append(line(bx0, bmid - vpeak, bx0 + 16, bmid - vpeak, color=SPIKE, sw=1.0, dash="3 3"))
    frags.append(text(bx0 + 20, bmid - vpeak + 4, "6 кВ", size=11, color=SPIKE, anchor="start"))
    frags.append(text(bx0 + 150, bmid - vpeak + 30, "1.2/50 мкс (напруга)", size=10, color=SPIKE, anchor="start"))
    frags.append(text(bx0 + 150, bmid - vpeak + 48, "8/20 мкс (струм)", size=10, color=CALM, anchor="start"))

    # струм закорочено 8/20 — ширший, повільніший фронт, коротший хвіст (пунктиром, інший колір)
    ip = []
    for i in range(M + 1):
        x = bx0 + 6 + i
        u = i / float(M)
        val = (math.exp(-u * 3.4) - math.exp(-u * 11.0))
        y = bmid - 74 * (val / 0.42)
        ip.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5 3"/>'
                 % (" ".join(ip), CALM))

    render(os.path.join(OUT, "surge-waveforms.svg"), W, H, *frags,
           title="Дві стандартні форми випробного сплеску")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг.5 — зони розташування A / B / C уздовж шляху від вводу до розетки
# Показує, ЧОМУ зон три: далі від вводу — менший струм, але той самий стелевий
# пік 6 кВ, бо його тримає пробій ізоляційних проміжків проводки.
# ─────────────────────────────────────────────────────────────────────────────
def fig_location_categories():
    W, H = 720, 320
    frags = []
    y = 150

    # шлях проводки — товста лінія зліва (вулиця) направо (в глиб дому)
    frags.append(line(60, y, 660, y, color=INK, sw=2.4))
    frags.append(text(60, y - 96, "від блискавки / мережі", size=11, color=SPIKE, anchor="start"))
    frags.append(arrow(70, y - 78, 150, y - 78, color=SPIKE, sw=2.2))

    # три зони — вертикальні смуги-мітки з описом
    zones = [
        (150, "C", "ввід ззовні", "лічильник, ввідний щит", "найбільша енергія", SPIKE),
        (370, "B", "фідери, короткі\nвідгалуження", "≈ до 10 м від вводу", "середня", "#e08e0b"),
        (590, "A", "розетки, довгі\nвідгалуження", "далеко від вводу", "найменша", FIELD),
    ]
    prev = 60
    for xc, letter, where, dist, energy, col in zones:
        # межа зони
        frags.append(line(xc, y - 60, xc, y + 60, color=col, sw=1.0, dash="4 4"))
        # велика літера в кружечку
        frags.append(circle(xc, y, 20, fill=BG, stroke=col, sw=2.4))
        frags.append(text(xc, y + 6, letter, size=18, color=col, bold=True))
        # опис під шляхом
        frags.append(mtext(xc, y + 40, where, size=10, color=INK))
        frags.append(text(xc, y + 74, dist, size=9, color=MUTED))
        # енергія над шляхом
        frags.append(text(xc, y - 40, energy, size=10, color=col, bold=True))
        prev = xc

    # стелевий пік 6 кВ — горизонтальна лінія над усім, однакова для всіх зон
    cap = y - 118
    frags.append(line(150, cap, 660, cap, color=NEG, sw=1.4, dash="6 3"))
    frags.append(text(660, cap - 6, "стеля 6 кВ — пробій ізоляційних проміжків проводки", size=10, color=NEG, anchor="end"))

    render(os.path.join(OUT, "location-categories.svg"), W, H, *frags,
           title="Зони розташування: A / B / C за відстанню від вводу")


if __name__ == "__main__":
    fig_spike_on_sine()
    fig_clamp_knee()
    fig_two_stage()
    fig_surge_waveforms()
    fig_location_categories()
    print("figs done")
