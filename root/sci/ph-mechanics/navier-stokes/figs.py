# -*- coding: utf-8 -*-
"""Фігури до теми «Рівняння Нав'є–Стокса».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── дрібні помічники ────────────────────────────────────────────────────────
def polyline(pts, color=INK, sw=2.4, dash=None, fill="none"):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, fill, color, sw, d))


def head_at(x, y, dx, dy, color=INK, size=11):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.4, head=11):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


def path(d, color=INK, sw=2.4, dash=None, fill="none"):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, fill, color, sw, da))


# ── Фігура 1: матеріальна похідна — розгін у соплі ───────────────────────────
def fig_material_derivative():
    W, H = 880, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Матеріальна похідна: усталена течія, а частинка розганяється",
                  size=18, bold=True))

    # ── звужувальне сопло: верхня й нижня стінки ──
    xL, xR = 110, 720
    yTopL, yTopR = 150, 210     # верхня стінка: від широкого до вузького
    yBotL, yBotR = 350, 290     # нижня стінка
    f.append(path("M %d %d L %d %d" % (xL, yTopL, xR, yTopR), color=INK, sw=3))
    f.append(path("M %d %d L %d %d" % (xL, yBotL, xR, yBotR), color=INK, sw=3))
    # легка заливка каналу
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#eef4fb" stroke="none"/>'
             % (xL, yTopL, xR, yTopR, xR, yBotR, xL, yBotL))

    # ── лінії течії (звужуються) ──
    for t in (0.28, 0.5, 0.72):
        yl = yTopL + (yBotL - yTopL) * t
        yr = yTopR + (yBotR - yTopR) * t
        f.append(path("M %d %.1f L %d %.1f" % (xL + 8, yl, xR - 8, yr),
                      color="#9db7d6", sw=1.6, dash="7 6"))

    # ── частинка 1 (широке місце, повільна) ──
    cx1, cy1 = 235, 250
    f.append(circle(cx1, cy1, 13, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(varrow(cx1 + 14, cy1, cx1 + 60, cy1, color=POS, sw=3.0, head=11))
    f.append(text(cx1, cy1 - 26, "повільна", size=12, color=POS, bold=True))

    # ── частинка 2 (вузьке місце, швидка) ──
    cx2, cy2 = 610, 250
    f.append(circle(cx2, cy2, 13, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(varrow(cx2 + 14, cy2, cx2 + 120, cy2, color=POS, sw=3.4, head=13))
    f.append(text(cx2 + 30, cy2 - 26, "швидка", size=12, color=POS, bold=True))

    # та сама частинка — пунктир переходу
    f.append(path("M %d %d L %d %d" % (cx1 + 62, cy1, cx2 - 16, cy2),
                  color=MUTED, sw=1.6, dash="4 5"))
    f.append(text((cx1 + cx2) / 2 + 20, cy1 - 44, "та сама крапля, що біжить →",
                  size=12, color=MUTED, italic=True))

    # ── банер: усталено, але прискорення ≠ 0 ──
    b, w, h = textbox(258, 410, "усталено:  ∂v/∂t = 0", size=15, pad=11,
                      fill="#eef1fb", stroke=NEG, sw=1.6, bold=True)
    f.append(b)
    f.append(text(430, 410, "але", size=14, color=MUTED, italic=True))
    b, w, h = textbox(628, 410, "прискорення = (v·∇)v ≠ 0", size=15, pad=11,
                      fill="#fdecea", stroke=POS, sw=1.6, bold=True)
    f.append(b)
    f.append(text(W / 2, 448, "частинка прискорюється, бо переїжджає туди, де поле швидше",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, "material-derivative.svg"), W, H, *f)


# ── Фігура 2: три сили на рідинну частинку ───────────────────────────────────
def fig_forces_on_parcel():
    W, H = 930, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Три сили на рідинну частинку — права частина рівняння",
                  size=18, bold=True))

    panels = [(40, "Тиск", NEG, "#eef1fb"),
              (330, "В'язкість", "#7a1f9e", "#f3ecfb"),
              (620, "Тяжіння", FIELD, "#eafaf1")]
    pw, py, ph = 270, 66, 300

    # спільний квадрат-частинка в центрі кожної панелі
    for (px, name, col, tint) in panels:
        f.append(rect(px, py, pw, ph, fill=tint, stroke=col, sw=1.6))
        f.append(text(px + pw / 2, py + 26, name, size=15, bold=True, color=col))

    # -- панель 1: тиск -----------------------------------------------------
    px = panels[0][0]
    ccx, ccy = px + pw / 2, py + 150
    sq = 58
    f.append(rect(ccx - sq / 2, ccy - sq / 2, sq, sq, fill=BG, stroke=INK, sw=1.8))
    # ліва грань — великий тиск (довга стрілка всередину)
    f.append(varrow(ccx - sq / 2 - 70, ccy, ccx - sq / 2 - 6, ccy, color=NEG, sw=3.4, head=12))
    f.append(text(px + 34, ccy - 16, "великий", size=11, color=NEG))
    # права грань — малий тиск (коротка стрілка всередину)
    f.append(varrow(ccx + sq / 2 + 40, ccy, ccx + sq / 2 + 6, ccy, color=NEG, sw=2.2, head=9))
    f.append(text(px + pw - 40, ccy - 16, "малий", size=11, color=NEG))
    # верх/низ — рівні короткі
    f.append(varrow(ccx, ccy - sq / 2 - 34, ccx, ccy - sq / 2 - 6, color=NEG, sw=2.0, head=8))
    f.append(varrow(ccx, ccy + sq / 2 + 34, ccx, ccy + sq / 2 + 6, color=NEG, sw=2.0, head=8))
    # чиста сила → праворуч
    f.append(varrow(ccx - 10, ccy + 96, ccx + 60, ccy + 96, color=POS, sw=3.2, head=12))
    f.append(text(ccx + 24, ccy + 88, "чиста сила", size=11, color=POS, bold=True))
    f.append(text(ccx, py + ph - 16, "= −∇p", size=17, bold=True, color=NEG))

    # -- панель 2: в'язкість (зсув) -----------------------------------------
    px = panels[1][0]
    ccx, ccy = px + pw / 2, py + 150
    f.append(rect(ccx - sq / 2, ccy - sq / 2, sq, sq, fill=BG, stroke=INK, sw=1.8))
    # профіль швидкості збоку: стрілки, що ростуть догори
    prof_x = px + 34
    for i, yy in enumerate((ccy + 70, ccy + 35, ccy, ccy - 35, ccy - 70)):
        ln = 20 + i * 16
        f.append(varrow(prof_x, yy, prof_x + ln, yy, color="#7a1f9e", sw=2.2, head=8))
    f.append(text(prof_x + 6, ccy - 92, "швидші сусіди", size=10.5, color="#7a1f9e"))
    f.append(text(prof_x + 2, ccy + 96, "повільніші", size=10.5, color="#7a1f9e"))
    # верхній сусід тягне вперед, нижній гальмує
    f.append(varrow(ccx - 6, ccy - sq / 2 - 8, ccx + 40, ccy - sq / 2 - 8, color=POS, sw=2.4, head=9))
    f.append(varrow(ccx + 6, ccy + sq / 2 + 8, ccx - 30, ccy + sq / 2 + 8, color=NEG, sw=2.0, head=8))
    f.append(text(ccx, py + ph - 16, "= μ∇²v", size=17, bold=True, color="#7a1f9e"))

    # -- панель 3: тяжіння --------------------------------------------------
    px = panels[2][0]
    ccx, ccy = px + pw / 2, py + 140
    f.append(rect(ccx - sq / 2, ccy - sq / 2, sq, sq, fill=BG, stroke=INK, sw=1.8))
    f.append(varrow(ccx, ccy + sq / 2 + 6, ccx, ccy + sq / 2 + 76, color=FIELD, sw=3.4, head=13))
    f.append(text(ccx + 42, ccy + sq / 2 + 48, "донизу", size=11, color=FIELD, bold=True))
    f.append(text(ccx, py + ph - 16, "= ρg", size=17, bold=True, color=FIELD))

    # ── банер підсумку ──
    b, w, h = textbox(W / 2, H - 30,
                      "ρ Dv/Dt  =  −∇p  +  μ∇²v  +  ρg",
                      size=17, pad=13, fill="#f4f6f8", stroke=INK, sw=1.8, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "forces-on-parcel.svg"), W, H, *f)


# ── Фігура 3: анатомія рівняння ──────────────────────────────────────────────
def fig_anatomy():
    W, H = 980, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Анатомія рівняння Нав'є–Стокса", size=19, bold=True))

    yeq = 150
    # члени: (центр x, текст, підпис, колір рамки, заливка, гарячий)
    terms = [
        (150, "ρ ∂v/∂t", "нестаціонарність", NEG, "#eef1fb", False),
        (368, "ρ(v·∇)v", "конвекція — НЕЛІНІЙНА", POS, "#fdecea", True),
        (612, "−∇p", "тиск", "#0b7a75", "#e6f6f4", False),
        (760, "μ∇²v", "в'язкість", "#7a1f9e", "#f3ecfb", False),
        (896, "ρg", "тяжіння", FIELD, "#eafaf1", False),
    ]
    # оператори між членами
    ops = [(258, "="), (490, "+"), (686, "+"), (828, "+")]

    for (cx, s, lab, col, tint, hot) in terms:
        b, w, h = textbox(cx, yeq, s, size=20, pad=13, fill=tint, stroke=col,
                          sw=(2.4 if hot else 1.7), bold=True, color=INK)
        f.append(b)
        # підпис під членом
        f.append(text(cx, yeq + 52, lab, size=12, color=col, bold=hot))

    for (x, s) in ops:
        f.append(text(x, yeq + 8, s, size=24, bold=True))

    # ліва дужка-підпис: маса × прискорення
    f.append(path("M 70 214 L 70 226 L 462 226 L 462 214", color=MUTED, sw=1.6))
    f.append(text(266, 248, "маса одиниці об'єму  ×  прискорення (матеріальна похідна)",
                  size=12.5, color=MUTED, italic=True))
    # права дужка-підпис: сили
    f.append(path("M 556 214 L 556 226 L 950 226 L 950 214", color=MUTED, sw=1.6))
    f.append(text(753, 248, "сума сил на одиницю об'єму", size=12.5, color=MUTED, italic=True))

    # супутнє рівняння нестисливості
    b, w, h = textbox(300, 322, "∇·v = 0", size=20, pad=12, fill="#fff8e6",
                      stroke="#b5651d", sw=1.9, bold=True)
    f.append(b)
    f.append(text(560, 322, "нестисливість — збереження маси (4-те рівняння)",
                  size=13, color="#b5651d", anchor="middle"))

    b, w, h = textbox(W / 2, 392,
                      "5 невідомих (v — три складові, p) · 4 рівняння · тиск підлаштовує ∇·v = 0",
                      size=13, pad=11, fill="#f4f6f8", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── Фігура 4: каскад енергії в турбулентності ────────────────────────────────
def fig_cascade():
    W, H = 940, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Каскад енергії: нелінійний член дробить рух на дрібніші вихори",
                  size=17, bold=True))

    axy = 250
    # три «покоління» вихорів: великий → середні → дрібні
    def eddy(cx, cy, r, col, sw=2.6):
        # коло + спіральний хвостик
        s = circle(cx, cy, r, fill="none", stroke=col, sw=sw)
        pts = []
        for k in range(24):
            a = k / 23.0 * 2.4 * math.pi
            rr = r * (1 - k / 30.0)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        s += polyline(pts, color=col, sw=sw * 0.75)
        return s

    # рівень 1
    f.append(eddy(150, axy, 62, POS, 3.0))
    # рівень 2
    lvl2 = [(360, axy - 55, 34), (360, axy + 55, 34), (430, axy, 30)]
    for (cx, cy, r) in lvl2:
        f.append(eddy(cx, cy, r, "#c0563b", 2.4))
    # рівень 3
    lvl3 = [(590, axy - 70, 16), (600, axy - 25, 15), (585, axy + 20, 14),
            (605, axy + 62, 15), (640, axy - 48, 12), (645, axy + 42, 12),
            (655, axy, 13), (560, axy + 55, 12)]
    for (cx, cy, r) in lvl3:
        f.append(eddy(cx, cy, r, "#d98a5a", 1.9))

    # тепло праворуч — хвилясті лінії
    for i, yy in enumerate(range(axy - 66, axy + 67, 22)):
        pts = []
        for k in range(41):
            t = k / 40.0
            x = 730 + t * 150
            y = yy + 7 * math.sin(k * 0.9 + i)
            pts.append((x, y))
        f.append(polyline(pts, color="#b5651d", sw=2.0))
    f.append(text(805, axy - 92, "тепло", size=14, color="#b5651d", bold=True))

    # стрілки-переходи між рівнями
    f.append(varrow(216, axy, 300, axy, color=INK, sw=2.2, head=11))
    f.append(varrow(470, axy, 530, axy, color=INK, sw=2.2, head=11))
    f.append(varrow(690, axy, 724, axy, color=INK, sw=2.2, head=11))

    # підписи масштабів під кожним рівнем
    labels = [(150, "великі вихори", "енергія входить", POS),
              (395, "менші вихори", "каскад униз", "#c0563b"),
              (610, "найдрібніші", "тут править в'язкість", "#d98a5a"),
              (805, "дисипація", "рух → тепло", "#b5651d")]
    for (x, l1, l2, col) in labels:
        f.append(text(x, 346, l1, size=13, bold=True, color=col))
        f.append(text(x, 366, l2, size=11, color=MUTED))

    # вісь масштабу
    f.append(varrow(120, 392, 830, 392, color=INK, sw=1.8, head=11))
    f.append(text(120, 412, "великий масштаб", size=11, color=MUTED, anchor="start"))
    f.append(text(830, 412, "малий масштаб", size=11, color=MUTED, anchor="end"))
    f.append(text(475, 412, "розмір вихорів меншає  →", size=11, color=MUTED))
    return render(os.path.join(IMG, "cascade.svg"), W, H, *f)


# ── Фігура 5: історія — народження рівняння за ~20 років ─────────────────────
def fig_ns_history_timeline():
    W, H = 1080, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Народження рівняння Нав'є–Стокса: майже двадцять років і кілька суперників",
                  size=18, bold=True))
    f.append(text(W / 2, 58, "чотири виведення — від молекул до суцільного середовища — привели до одного рівняння",
                  size=12.5, color=MUTED, italic=True))

    # три класи за методом/статусом
    MOL_S, MOL_T = NEG, "#eef1fb"          # молекулярний підхід
    CON_S, CON_T = "#0b7a75", "#e6f6f4"    # суцільне середовище
    OPN_S, OPN_T = POS, "#fdecea"          # відкрита задача

    cards = [
        ("1822", "Нав'є", "Франція · мости", "молекули", MOL_S, MOL_T,
         ["правильна форма", "з фізично хибної", "моделі молекул"]),
        ("1829", "Пуассон", "Франція", "молекули", MOL_S, MOL_T,
         ["те саме, незалежно;", "стисливий випадок"]),
        ("1843", "Сен-Венан", "Франція · механік", "суцільне", CON_S, CON_T,
         ["суцільне виведення;", "правильний коеф.", "в'язкості —", "раніше за Стокса"]),
        ("1845", "Стокс", "Ірландія → Кембридж", "суцільне", CON_S, CON_T,
         ["тензор напружень;", "строгий ґрунт", "континууму"]),
        ("2000", "Задача Клея", "Інститут Клея, США", "відкрита", OPN_S, OPN_T,
         ["існування й", "гладкість у 3D;", "1 млн $, не", "доведено донині"]),
    ]

    ML, gap = 24, 16
    cw = (W - 2 * ML - (len(cards) - 1) * gap) / len(cards)   # ширина картки
    top, ch = 84, 372
    step = cw + gap

    for i, (yr, nm, nat, pill, sc, tc, lines) in enumerate(cards):
        x = ML + i * step
        cx = x + cw / 2
        f.append(rect(x, top, cw, ch, fill=tc, stroke=sc, sw=1.9, rx=10))
        # рік — великий
        f.append(text(cx, top + 46, yr, size=27, bold=True, color=sc))
        # ім'я
        nsz = fit_font(nm, cw - 20, 18, bold=True)
        f.append(text(cx, top + 82, nm, size=nsz, bold=True))
        # країна / роль
        f.append(text(cx, top + 106, nat, size=11.5, color=MUTED))
        # «пігулка» методу
        b, pw, ph = textbox(cx, top + 140, pill, size=12, pad=8,
                            fill=BG, stroke=sc, sw=1.6, color=sc, bold=True, rx=10)
        f.append(b)
        # розділювач
        f.append(line(x + 16, top + 168, x + cw - 16, top + 168, color=sc, sw=1.0, dash="3 4"))
        # внесок — рядки
        for j, ln in enumerate(lines):
            f.append(text(cx, top + 194 + j * 20, ln, size=12.5, color=INK))

    # розрив часу перед задачею Клея (між 4-ю та 5-ю картками)
    xgap = ML + 4 * step - gap / 2
    f.append(line(xgap, top - 4, xgap, top + ch + 4, color=MUTED, sw=1.4, dash="2 6"))
    b, gw, gh = textbox(xgap, 71, "≈ 155 років потому", size=11.5, pad=6,
                        fill=BG, stroke=MUTED, sw=1.2, color=MUTED)
    f.append(b)

    # підсумковий банер — закон Стіглера
    b, bw, bh = textbox(W / 2, H - 34,
                        "На табличці — двоє: Нав'є й Стокс.  Пуассон і Сен-Венан за бортом назви (закон Стіглера).",
                        size=14, pad=12, fill="#f4f6f8", stroke=INK, sw=1.6, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "ns-history-timeline.svg"), W, H, *f)


def _poly(pts, color=INK, sw=2.4, dash=None, fill="none", closed=True):
    p = list(pts) + ([pts[0]] if closed else [])
    return polyline(p, color=color, sw=sw, dash=dash, fill=fill)


def _dblarrow(x1, y1, x2, y2, color=INK, sw=2.4, head=10):
    return (line(x1, y1, x2, y2, color=color, sw=sw)
            + head_at(x2, y2, x2 - x1, y2 - y1, color, head)
            + head_at(x1, y1, x1 - x2, y1 - y2, color, head))


# ── Фігура 6: сенс тензора напружень σᵢⱼ ─────────────────────────────────────
def fig_stress_tensor():
    W, H = 940, 540
    SH = "#7a1f9e"   # дотичні (зсув) — фіолетовий
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Тензор напружень: сила на грань залежить від її орієнтації",
                  size=18, bold=True))
    f.append(line(470, 70, 470, 430, color="#d9dee5", sw=1.4, dash="5 6"))

    # ── ЛІВА панель: складові σᵢⱼ на гранях квадрата ──
    cx, cy, s = 250, 275, 150
    Lx, Rx, Ty, By = cx - s / 2, cx + s / 2, cy - s / 2, cy + s / 2
    f.append(rect(Lx, Ty, s, s, fill="#eef4fb", stroke=INK, sw=2.0))

    # права грань (нормаль уздовж x1): нормальне σ11 + дотичне σ21
    ax, ay = Rx, cy + 15
    f.append(varrow(ax, ay, ax + 92, ay, color=POS, sw=3.2, head=12))
    f.append(text(ax + 62, ay + 22, "σ₁₁", size=15, color=POS, bold=True))
    f.append(varrow(ax, ay, ax, ay - 62, color=SH, sw=2.8, head=11))
    f.append(text(ax + 24, ay - 48, "σ₂₁", size=15, color=SH, bold=True))

    # верхня грань (нормаль уздовж x2): нормальне σ22 + дотичне σ12
    tx, ty = cx - 18, Ty
    f.append(varrow(tx, ty, tx, ty - 92, color=POS, sw=3.2, head=12))
    f.append(text(tx - 26, ty - 66, "σ₂₂", size=15, color=POS, bold=True))
    f.append(varrow(tx, ty, tx + 62, ty, color=SH, sw=2.8, head=11))
    f.append(text(tx + 42, ty - 12, "σ₁₂", size=15, color=SH, bold=True))

    # осі-орієнтир
    ox, oy = 148, 372
    f.append(varrow(ox, oy, ox + 46, oy, color=MUTED, sw=1.8, head=9))
    f.append(text(ox + 58, oy + 5, "x₁", size=12, color=MUTED))
    f.append(varrow(ox, oy, ox, oy - 46, color=MUTED, sw=1.8, head=9))
    f.append(text(ox - 2, oy - 54, "x₂", size=12, color=MUTED))

    f.append(text(cx, 424, "σᵢⱼ — сила вздовж осі i на грань із нормаллю вздовж j",
                  size=12.5, color=INK))
    f.append(text(cx, 444, "червоні — нормальні (тиск/розтяг),  фіолетові — дотичні (тертя)",
                  size=11.5, color=MUTED))

    # ── ПРАВА панель: довільна грань, t = σn (не вздовж нормалі) ──
    f.append(text(700, 96, "грань будь-якого нахилу", size=13.5, color=INK, bold=True))
    Ax, Ay, Bx, By2 = 628, 316, 752, 232     # скісна грань
    f.append(line(Ax, Ay, Bx, By2, color=INK, sw=3.4))
    # штрихування «матеріалу» під гранню
    for t in (0.2, 0.4, 0.6, 0.8):
        hx = Ax + (Bx - Ax) * t
        hy = Ay + (By2 - Ay) * t
        f.append(line(hx, hy, hx + 16, hy + 22, color="#c7ccd4", sw=1.4))
    Mx, My = (Ax + Bx) / 2, (Ay + By2) / 2   # середина грані
    f.append(circle(Mx, My, 3.2, fill=INK, stroke=INK, sw=1))
    # нормаль n (перпендикуляр до грані, назовні — вгору-ліворуч)
    f.append(varrow(Mx, My, Mx - 66, My - 44, color=NEG, sw=2.6, head=11))
    f.append(text(Mx - 84, My - 52, "n", size=15, color=NEG, bold=True, italic=True))
    # напруження t (інший напрям — не вздовж n)
    f.append(varrow(Mx, My, Mx + 30, My - 78, color=POS, sw=3.0, head=12))
    f.append(text(Mx + 40, My - 82, "t", size=15, color=POS, bold=True, italic=True))
    b, w, h = textbox(700, 372, "tᵢ = σᵢⱼ nⱼ", size=19, pad=12,
                      fill="#fdecea", stroke=POS, sw=1.8, bold=True)
    f.append(b)
    f.append(text(700, 422, "дев'ять чисел → сила на грань БУДЬ-ЯКОГО нахилу",
                  size=12, color=MUTED))
    f.append(text(700, 442, "t взагалі не вздовж нормалі n — у цьому й є тертя",
                  size=11.5, color=MUTED))

    # ── нижній банер: симетрія ──
    b, w, h = textbox(W / 2, 498,
                      "σ₁₂ = σ₂₁   —   тензор симетричний (наслідок збереження моменту імпульсу)",
                      size=14, pad=12, fill="#f4f6f8", stroke=INK, sw=1.7, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "stress-tensor.svg"), W, H, *f)


# ── Фігура 7: розклад градієнта швидкості S + W ──────────────────────────────
def fig_strain_decomposition():
    import math as _m
    W, H = 1000, 440
    SH = "#7a1f9e"
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Розклад градієнта швидкості:  ∇v = деформація S + обертання W",
                  size=18, bold=True))

    yc, hs = 190, 60   # центр по вертикалі, півсторона квадрата

    def base(cx):
        return [(cx - hs, yc - hs), (cx + hs, yc - hs), (cx + hs, yc + hs), (cx - hs, yc + hs)]

    # ── клітина 1: зсув (повний ∇v) ──
    c1 = 175
    f.append(_poly(base(c1), color=MUTED, sw=1.8, dash="5 5"))
    shear = [(c1 - hs + 34, yc - hs), (c1 + hs + 34, yc - hs),
             (c1 + hs, yc + hs), (c1 - hs, yc + hs)]
    f.append(_poly(shear, color=INK, sw=2.6))
    f.append(varrow(c1 - 20, yc - hs - 14, c1 + 40, yc - hs - 14, color=INK, sw=2.0, head=9))
    f.append(text(c1, 300, "градієнт швидкості", size=13, bold=True))
    f.append(text(c1, 320, "∇vᵢⱼ = ∂vᵢ/∂xⱼ", size=12.5, color=MUTED))

    f.append(text(348, yc + 8, "=", size=30, bold=True))

    # ── клітина 2: симетрична S — чиста деформація (розтяг по діагоналі) ──
    c2 = 510
    f.append(_poly(base(c2), color=MUTED, sw=1.8, dash="5 5"))
    a = 0.42
    strained = []
    for (dx, dy) in [(-hs, -hs), (hs, -hs), (hs, hs), (-hs, hs)]:
        strained.append((c2 + dx + a * dy, yc + dy + a * dx))
    f.append(_poly(strained, color=SH, sw=2.8))
    # стрілки розтягу (по довгій діагоналі) і стиску (по короткій)
    f.append(_dblarrow(c2 - 96, yc - 62, c2 + 96, yc + 62, color=SH, sw=2.2, head=9))
    f.append(text(c2 + 104, yc + 70, "розтяг", size=11, color=SH))
    f.append(text(c2 - 108, yc - 66, "стиск", size=11, color=SH))
    f.append(text(c2, 300, "симетрична  S", size=13, bold=True, color=SH))
    f.append(text(c2, 320, "міняє форму → тертя", size=12, color=SH))

    f.append(text(688, yc + 8, "+", size=30, bold=True))

    # ── клітина 3: антисиметрична W — тверде обертання ──
    c3 = 850
    f.append(_poly(base(c3), color=MUTED, sw=1.8, dash="5 5"))
    th = 0.28
    ct, stt = _m.cos(th), _m.sin(th)
    rot = []
    for (dx, dy) in [(-hs, -hs), (hs, -hs), (hs, hs), (-hs, hs)]:
        rot.append((c3 + dx * ct - dy * stt, yc + dx * stt + dy * ct))
    f.append(_poly(rot, color=FIELD, sw=2.8))
    # дуга-стрілка обертання
    f.append(path("M %.1f %.1f A 44 44 0 0 1 %.1f %.1f"
                  % (c3 + 44, yc - 20, c3 + 20, yc - 44), color=FIELD, sw=2.4))
    f.append(head_at(c3 + 20, yc - 44, -24, -24, FIELD, 10))
    f.append(text(c3, 300, "антисиметрична  W", size=13, bold=True, color=FIELD))
    f.append(text(c3, 320, "обертання → без тертя", size=12, color=FIELD))

    b, w, h = textbox(W / 2, 400,
                      "в'язке напруження τ залежить ТІЛЬКИ від S — від того, що справді деформує рідину",
                      size=13.5, pad=12, fill="#f4f6f8", stroke=SH, sw=1.7, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "strain-decomposition.svg"), W, H, *f)


# ── помічник: спіраль-вихор із стрілкою напряму (proj-cfd-cavity) ─────────────
def _spiral(cx, cy, r, col, turns=2.6, sw=2.4, cw=True, n=64):
    s = 1.0 if cw else -1.0
    pts = []
    for k in range(n + 1):
        t = k / n
        ang = t * turns * 2 * math.pi * s
        rr = r * t
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    out = polyline(pts, color=col, sw=sw)
    (x2, y2), (x1, y1) = pts[-1], pts[-2]
    out += head_at(x2, y2, x2 - x1, y2 - y1, col, size=max(7, sw * 3.4))
    return out


# ── Фігура (proj): постановка задачі про порожнину з кришкою ──────────────────
def fig_cavity_setup():
    W, H = 800, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Задача про порожнину з рухомою кришкою", size=18, bold=True))

    x0, y0, S = 90, 92, 300
    f.append(rect(x0, y0, S, S, fill="#eef4fb", stroke=INK, sw=3))
    # три нерухомі стінки — потовщені
    f.append(line(x0, y0, x0, y0 + S, color=INK, sw=6))
    f.append(line(x0 + S, y0, x0 + S, y0 + S, color=INK, sw=6))
    f.append(line(x0, y0 + S, x0 + S, y0 + S, color=INK, sw=6))

    # кришка зверху — рухома
    f.append(line(x0, y0, x0 + S, y0, color=POS, sw=6))
    for k in range(5):
        ax = x0 + 34 + k * 58
        f.append(varrow(ax, y0 - 14, ax + 42, y0 - 14, color=POS, sw=3.0, head=10))
    f.append(text(x0 + S / 2, y0 - 30, "кришка їде  →   u = U", size=14, color=POS, bold=True))

    # головний вихор — зсунуте вгору-праворуч осереддя
    cx, cy = x0 + 0.62 * S, y0 + (1 - 0.73) * S
    f.append(_spiral(cx, cy, 96, NEG, turns=2.7, sw=2.6, cw=True))
    f.append(circle(cx, cy, 4.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(cx + 8, cy - 104, "осереддя вихору", size=12, color=NEG, bold=True))

    # напрям обходу петлі
    f.append(varrow(x0 + 60, y0 + 34, x0 + 150, y0 + 34, color=MUTED, sw=2.0, head=9))
    f.append(varrow(x0 + S - 30, y0 + 70, x0 + S - 30, y0 + 170, color=MUTED, sw=2.0, head=9))
    f.append(varrow(x0 + S - 60, y0 + S - 30, x0 + 150, y0 + S - 30, color=MUTED, sw=2.0, head=9))
    f.append(varrow(x0 + 30, y0 + S - 70, x0 + 30, y0 + 90, color=MUTED, sw=2.0, head=9))

    # вторинні вихорчики в нижніх кутах
    f.append(_spiral(x0 + 34, y0 + S - 34, 20, "#b5651d", turns=2.0, sw=1.6, cw=False))
    f.append(_spiral(x0 + S - 34, y0 + S - 34, 20, "#b5651d", turns=2.0, sw=1.6, cw=True))
    f.append(text(x0 + S / 2, y0 + S + 26, "нерухомі стінки: прилипання, v = 0", size=13, color=INK))

    # права колонка — суть задачі
    lx = 470
    f.append(text(lx, y0 + 6, "Суть", size=15, bold=True, anchor="start"))
    notes = [("нестислива рідина:  ∇·v = 0", FIELD),
             ("єдиний руш — кришка", POS),
             ("ні входу, ні виходу, ні тяжіння", MUTED),
             ("шукаємо застигле поле v(x, y)", NEG),
             ("відповідь — рециркуляційний вихор", "#b5651d")]
    for i, (s, col) in enumerate(notes):
        yy = y0 + 44 + i * 52
        f.append(circle(lx + 8, yy - 5, 5, fill=col, stroke=col, sw=1))
        f.append(text(lx + 24, yy, s, size=13.5, color=INK, anchor="start"))
    f.append(text(lx, y0 + S - 6, "«hello world» обчислювальної",
                  size=12.5, color=MUTED, anchor="start", italic=True))
    f.append(text(lx, y0 + S + 14, "гідродинаміки",
                  size=12.5, color=MUTED, anchor="start", italic=True))
    return render(os.path.join(IMG, "cavity-setup.svg"), W, H, *f)


# ── Фігура (proj): крок методу проєкції Чоріна ───────────────────────────────
def fig_projection_step():
    W, H = 1000, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Крок методу проєкції: розщепити на предиктор і корекцію",
                  size=18, bold=True))

    yb = 150

    def bubble(cx, s, sub, col, tint):
        out = circle(cx, yb, 30, fill=tint, stroke=col, sw=2.2)
        out += text(cx, yb - 1, s, size=15, color=col, bold=True)
        out += text(cx, yb + 40, sub, size=11.5, color=col)
        return out

    f.append(bubble(70, "vₙ", "∇·v = 0", FIELD, "#eafaf1"))
    bA, wA, hA = textbox(215, yb, "Предиктор\n−(v·∇)v + ν∇²v", size=14, pad=12,
                         fill="#f4f6f8", stroke=INK, sw=1.8, bold=True)
    f.append(bA)
    f.append(text(215, yb + 44, "тиск ігноруємо", size=11.5, color=MUTED, italic=True))
    f.append(bubble(360, "v*", "∇·v ≠ 0", POS, "#fdecea"))
    bB, wB, hB = textbox(530, yb, "Пуассон\n∇²p = (ρ/Δt)·∇·v*", size=14, pad=12,
                         fill="#e6f6f4", stroke="#0b7a75", sw=1.8, bold=True)
    f.append(bB)
    bC, wC, hC = textbox(725, yb, "Корекція\nv = v* − (Δt/ρ)·∇p", size=14, pad=12,
                         fill="#eafaf1", stroke=FIELD, sw=1.8, bold=True)
    f.append(bC)
    f.append(bubble(895, "vₙ₊₁", "∇·v = 0", FIELD, "#eafaf1"))

    for xa, xbb in [(104, 158), (272, 432), (392, 442), (620, 638), (812, 862)]:
        f.append(varrow(xa, yb, xbb, yb, color=INK, sw=2.2, head=11))

    f.append(text(W / 2, 250, "три гравці одного кроку", size=13, color=MUTED, bold=True))
    chips = [("конвекція  (v·∇)v", POS, "#fdecea", 250),
             ("в'язкість  ν∇²v", "#7a1f9e", "#f3ecfb", 500),
             ("тиск: проєкція на ∇·v = 0", "#0b7a75", "#e6f6f4", 760)]
    for (s, col, tint, cx) in chips:
        b, w, h = textbox(cx, 292, s, size=13.5, pad=10, fill=tint, stroke=col, sw=1.6, bold=True)
        f.append(b)

    b, w, h = textbox(W / 2, 372,
                      "Гельмгольц — Ходж:  поле = (∇p-частина) + (бездивергентна);  проєкція відкидає ∇p-частину",
                      size=13, pad=12, fill="#fff8e6", stroke="#b5651d", sw=1.5)
    f.append(b)
    return render(os.path.join(IMG, "projection-step.svg"), W, H, *f)


# ── Фігура (proj): той самий вихор за різних Re ──────────────────────────────
def fig_reynolds_vortex():
    W, H = 860, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Той самий вихор, різне Re: осереддя повзе, у кутах прокидаються вихори",
                  size=17, bold=True))

    def panel(x0, y0, S, title, col):
        out = rect(x0, y0, S, S, fill="#eef4fb", stroke=INK, sw=2.4)
        out += line(x0, y0, x0 + S, y0, color=POS, sw=4)
        out += varrow(x0 + S / 2 - 26, y0 - 12, x0 + S / 2 + 26, y0 - 12, color=POS, sw=2.4, head=9)
        out += text(x0 + S / 2, y0 - 26, title, size=15, bold=True, color=col)
        out += text(x0 + S / 2 + 44, y0 - 12, "кришка", size=10.5, color=POS)
        return out

    S = 300
    y0 = 96
    xL, xR = 60, 500

    f.append(panel(xL, y0, S, "Re = 100", NEG))
    cx, cy = xL + 0.62 * S, y0 + (1 - 0.73) * S
    f.append(_spiral(cx, cy, 104, NEG, turns=2.8, sw=2.6, cw=True))
    f.append(circle(cx, cy, 4.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(xL + S / 2, y0 + S + 24, "одне осереддя,  кути майже стоять", size=12.5, color=MUTED))

    f.append(panel(xR, y0, S, "Re = 1000", "#b5651d"))
    cx2, cy2 = xR + 0.53 * S, y0 + (1 - 0.565) * S
    f.append(_spiral(cx2, cy2, 88, NEG, turns=2.8, sw=2.6, cw=True))
    f.append(circle(cx2, cy2, 4.5, fill=NEG, stroke=NEG, sw=1))
    f.append(_spiral(xR + 40, y0 + S - 40, 30, "#b5651d", turns=2.2, sw=1.9, cw=False))
    f.append(_spiral(xR + S - 40, y0 + S - 40, 34, "#b5651d", turns=2.2, sw=1.9, cw=True))
    f.append(text(xR + 40, y0 + S - 74, "вторинні", size=10.5, color="#b5651d", bold=True))
    f.append(text(xR + S / 2, y0 + S + 24, "осереддя до центру + вихори в кутах", size=12.5, color=MUTED))

    f.append(varrow(xL + S + 24, y0 + S / 2, xR - 24, y0 + S / 2, color=INK, sw=2.4, head=12))
    f.append(text((xL + S + xR) / 2, y0 + S / 2 - 14, "Re ↑", size=14, bold=True))
    f.append(text((xL + S + xR) / 2, y0 + S / 2 + 26, "інерція", size=11, color=MUTED))
    f.append(text((xL + S + xR) / 2, y0 + S / 2 + 42, "бере гору", size=11, color=MUTED))
    return render(os.path.join(IMG, "reynolds-vortex.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_material_derivative(), fig_forces_on_parcel(), fig_anatomy(), fig_cascade(),
          fig_ns_history_timeline(), fig_stress_tensor(), fig_strain_decomposition(),
          fig_cavity_setup(), fig_projection_step(), fig_reynolds_vortex()]
    print("written:")
    for p in ps:
        print("  ", p)
