# -*- coding: utf-8 -*-
"""Фігури до кроку «Вартість зволікання проти вартості помилки».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline(pts, color, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


def dot(cx, cy, r, color):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, color)


def fillpoly(pts, fill, stroke="none", sw=0.0):
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ' stroke="none"'
    return '<polygon points="%s" fill="%s"%s/>' % (s, fill, st)


# ───────── Фіг. 1: сумарна вартість як U-крива, мінімум = LRM ─────────
def fig_ucurve():
    W, H = 880, 500
    f = [text(W / 2, 34, "Чекати — це купувати інформацію: сумарна вартість має мінімум",
              size=16, bold=True)]

    L, R, TOP, BOT = 110, 745, 100, 392         # межі поля
    TMAX, VMAX = 12.0, 40.0

    def X(t): return L + t / TMAX * (R - L)
    def Y(v): return BOT - v / VMAX * (BOT - TOP)

    # моделі (схематичні): зволікання росте лінійно, помилка спадає з інформацією
    def delay(t): return 3.0 * t
    def error(t): return 36.0 * math.exp(-t / 3.0)
    def total(t): return delay(t) + error(t)

    ts = [i * 0.25 for i in range(int(TMAX / 0.25) + 1)]
    p_delay = [(X(t), Y(delay(t))) for t in ts]
    p_error = [(X(t), Y(error(t))) for t in ts]
    p_total = [(X(t), Y(total(t))) for t in ts]

    # легенда вгорі — у вільній смузі, щоб жоден напис не ліг на криву
    ly = 102

    def leg(x, label, color):
        seg = line(x, ly, x + 24, ly, color=color, sw=3.2)
        seg += text(x + 30, ly + 4, label, size=13, bold=True, color=color, anchor="start")
        return seg, x + 30 + text_width(label, 13, True) + 28
    s, x2 = leg(176, "вартість помилки", NEG); f.append(s)
    s, x3 = leg(x2, "вартість зволікання", POS); f.append(s)
    s, _ = leg(x3, "сумарна вартість", INK); f.append(s)

    # осі
    f.append(arrow(L, BOT, R + 18, BOT, color=INK, sw=1.8))
    f.append(arrow(L, BOT, L, TOP - 12, color=INK, sw=1.8))
    f.append(text(L - 12, TOP - 24, "вартість, €", size=12, color=MUTED, anchor="start"))
    f.append(text(R + 22, BOT + 22, "довше чекаємо →", size=12, color=MUTED, anchor="end"))
    f.append(text((L + R) / 2, BOT + 62, "тривалість очікування = скільки інформації купуємо",
                  size=11, color=MUTED))

    # криві
    f.append(polyline(p_error, NEG, sw=2.4))
    f.append(polyline(p_delay, POS, sw=2.4))
    f.append(polyline(p_total, INK, sw=3.0))

    # мінімум сумарної вартості: 3 = 12·e^(−t/3) → t = 3·ln(4) ≈ 4.16
    tmin = 3.0 * math.log(4.0)
    xm, ym = X(tmin), Y(total(tmin))
    f.append(line(xm, ym, xm, BOT, color=FIELD, sw=1.8, dash="5,5"))
    f.append(dot(xm, ym, 5.5, FIELD))
    f.append(fitbox(xm - 118, BOT + 10, 236, 26,
                    "останній відповідальний момент",
                    size=13, fill="#eafaf0", stroke=FIELD, color=INK, bold=True))

    render(os.path.join(IMG, "cost-ucurve.svg"), W, H, *f)


# ───────── Фіг. 2: 2×2 — вартість помилки × вартість зволікання ─────────
def fig_quadrants():
    W, H = 860, 560
    f = [text(W / 2, 34, "Що робити: вартість помилки × вартість зволікання",
              size=16, bold=True)]

    gx, gy = 250, 96          # лівий-верхній кут зони клітинок
    cw, ch = 276, 176
    gap = 16

    # заголовки стовпців — вартість ПОМИЛКИ
    f.append(text(gx + cw / 2, gy - 34, "ПОМИЛКА ДЕШЕВА", size=13, bold=True, color=FIELD))
    f.append(text(gx + cw / 2, gy - 18, "(рішення легко відкотити)", size=10, color=MUTED))
    f.append(text(gx + cw + gap + cw / 2, gy - 34, "ПОМИЛКА ДОРОГА", size=13, bold=True, color=POS))
    f.append(text(gx + cw + gap + cw / 2, gy - 18, "(відкотити важко чи незворотно)", size=10, color=MUTED))

    # заголовки рядків — вартість ЗВОЛІКАННЯ
    f.append(text(120, gy + ch / 2 - 8, "ЗВОЛІКАННЯ", size=13, bold=True, color=POS))
    f.append(text(120, gy + ch / 2 + 8, "ДОРОГЕ", size=13, bold=True, color=POS))
    f.append(text(120, gy + ch / 2 + 26, "(команда чекає,", size=10, color=MUTED))
    f.append(text(120, gy + ch / 2 + 40, "цінність тече)", size=10, color=MUTED))
    f.append(text(120, gy + ch + gap + ch / 2 - 4, "ЗВОЛІКАННЯ", size=13, bold=True, color=FIELD))
    f.append(text(120, gy + ch + gap + ch / 2 + 12, "ДЕШЕВЕ", size=13, bold=True, color=FIELD))
    f.append(text(120, gy + ch + gap + ch / 2 + 30, "(ніщо не блокує)", size=10, color=MUTED))

    # (row, col): row 0 = зволікання дороге (верх), row 1 = зволікання дешеве (низ)
    cells = [
        (0, 0, "Вирішуй ШВИДКО", "двобічні двері, але час пече",
         "обери й рухайся; помилишся — відкотиш дешево"),
        (0, 1, "ЗМІНИ ГРУ", "не можна ні чекати, ні схибити",
         "здешеви помилку (інтерфейс, зворотний крок)\nабо зволікання (walking skeleton) — і повернись"),
        (1, 0, "Не думай довго", "дрібниця в обидва боки",
         "кинь монетку, лиши на потім; нарада коштує більше"),
        (1, 1, "КУПУЙ ІНФОРМАЦІЮ", "дорого схибити, але ніщо не пече",
         "тягни до останнього відповідального моменту,\nроби спайк, збирай факти"),
    ]
    accent = {(0, 0): NEG, (0, 1): POS, (1, 0): MUTED, (1, 1): FIELD}
    for row, col, head, sub, body in cells:
        x = gx + col * (cw + gap)
        y = gy + row * (ch + gap)
        f.append(rect(x, y, cw, ch, fill="#fbfcfd", stroke=accent[(row, col)], sw=2.2, rx=12))
        f.append(text(x + cw / 2, y + 30, head, size=14, bold=True, color=accent[(row, col)]))
        f.append(text(x + cw / 2, y + 52, sub, size=11, color=MUTED))
        f.append(line(x + 20, y + 66, x + cw - 20, y + 66, color="#dfe4e9", sw=1.2))
        f.append(fitbox(x + 16, y + 78, cw - 32, ch - 96, body,
                        size=12, fill="#ffffff", stroke="#eef1f4", color=INK))

    note = ("Найдорожча помилка архітектора — сплутати клітинки: місяцями обговорювати те, "
            "що дешево відкотити (лівий верх), і похапцем ставити незворотну ставку (правий низ).")
    f.append(fitbox(gx, gy + 2 * ch + gap + 18, 2 * cw + gap, 48, note,
                    size=12, fill="#fff8e8", stroke="#c9a93b", color=INK))

    render(os.path.join(IMG, "cost-quadrants.svg"), W, H, *f)


# ───────── Фіг. 3 (вставка proj): чотири плани на одній € -шкалі ─────────
def fig_plan_bars():
    W, H = 900, 372
    f = [text(W / 2, 34, "Digital Homes: чотири плани на одній шкалі грошей",
              size=16, bold=True)]

    x0 = 300              # старт стовпчиків (праворуч від підписів)
    xend = 838           # правий край поля значень
    VMAX = 38000.0
    def L(v): return (xend - x0) * v / VMAX

    rows = [
        ("вирішити зараз",          30000, NEG),
        ("чекати до LRM (≈0.9 тиж)", 29747, NEG),
        ("чекати 6 тиж (наївно)",   36000, POS),
        ("змінити гру",              5200, FIELD),
    ]
    ys = [96, 158, 220, 282]
    bh = 40

    # базова вісь
    f.append(line(x0, 76, x0, 322, color="#c8ced6", sw=1.4))

    def money(v): return format(v, ",d").replace(",", " ") + " €"   # 30000 → "30 000 €"

    for (label, v, color), yc in zip(rows, ys):
        y = yc - bh / 2
        w = L(v)
        f.append(text(x0 - 16, yc + 5, label, size=13, bold=True, color=INK, anchor="end"))
        f.append(rect(x0, y, w, bh, fill=color, stroke=color, sw=1, rx=5))
        f.append(text(x0 + w + 12, yc + 5, money(v), size=13, bold=True, color=color, anchor="start"))

    # підпис-висновок під зеленим стовпчиком
    f.append(text(x0, 336, "сумарна очікувана вартість, €  —  зелений хід у ~6 разів дешевший за будь-яке чекання",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "cost-plan-bars.svg"), W, H, *f)


# ───────── Фіг. 4 (вставка hist): дві нитки — ціна зволікання й ціна знання ─────────
def fig_lineage():
    W, H = 920, 600
    f = [text(W / 2, 34, "Дві нитки, що дали ціну зволіканню й знанню", size=16, bold=True)]

    LX, RX = 250, 690            # центри лівої (теорія рішень) і правої (потік продукту) смуг
    f.append(text(LX, 70, "ТЕОРІЯ РІШЕНЬ", size=13, bold=True, color=NEG))
    f.append(text(LX, 88, "ціна знання", size=11, color=MUTED))
    f.append(text(RX, 70, "РОЗРОБКА ПРОДУКТУ", size=13, bold=True, color=FIELD))
    f.append(text(RX, 88, "ціна зволікання", size=11, color=MUTED))

    LW, RW = 330, 340
    # ── ліва нитка: єдиний вузол 1966 (Говард), далі пунктир до злиття ──
    f.append(fitbox(LX - LW / 2, 108, LW, 96,
                    "Рональд Говард · Стенфорд, 1966\n«Цінність інформації»: скільки\nрозумно платити за розвідку —\nі тут-таки «аналіз рішень»",
                    size=13, fill="#eef3fe", stroke=NEG, color=INK))
    f.append(line(LX, 210, LX, 494, color=NEG, sw=2.0, dash="6,6"))
    f.append(arrow(LX, 494, LX, 503, color=NEG, sw=2.0))

    # ── права нитка: 1983 → 1997 → 2009 (Райнертсен) ──
    ry = [(120, 84, "Дон Райнертсен · McKinsey, 1983\nУперше число під запізненням:\nпів року ≈ мінус третина прибутку"),
          (255, 84, "Managing the Design Factory · 1997\nПродукт — фабрика з чергами;\nзволікання стає важелем"),
          (390, 90, "Principles of Product Dev Flow, 2009\n«Квантуй лише одне — квантуй\nвартість зволікання»; 85% не знають")]
    for yy, hh, txt in ry:
        f.append(fitbox(RX - RW / 2, yy, RW, hh, txt, size=13, fill="#eafaf0", stroke=FIELD, color=INK))
    f.append(line(RX, 204, RX, 255, color=FIELD, sw=2.0))   # спайн у проміжках між рамками
    f.append(line(RX, 339, RX, 390, color=FIELD, sw=2.0))
    f.append(arrow(RX, 480, RX, 503, color=FIELD, sw=2.0))

    # ── злиття обох ниток ──
    f.append(fitbox((W - 680) / 2, 505, 680, 62,
                    "Дві ціни на одній шкалі:\nвартість зволікання (за тиждень) × цінність інформації (за розвідку)",
                    size=13, fill="#fff8e8", stroke="#c9a93b", color=INK))

    render(os.path.join(IMG, "cost-lineage.svg"), W, H, *f)


# ───────── Фіг. 5 (вставка math): гранична цінність тижня vs CoD ─────────
def fig_voi_marginal():
    W, H = 900, 520
    f = [text(W / 2, 34, "Гранична цінність тижня спадає: чекай, поки вона вища за вартість зволікання",
              size=15, bold=True)]

    Lm, Rm, TOP, BOT = 118, 812, 118, 408
    VMAX = 6500.0
    weeks = [1, 2, 3, 4, 5, 6]
    val = {1: 5400, 2: 4200, 3: 3000, 4: 2400, 5: 1800, 6: 1200}   # C_fix·|ΔP| за тиждень
    COD = 4000
    slot = (Rm - Lm) / len(weeks)
    bw = 58

    def Xc(i): return Lm + (i - 0.5) * slot
    def Y(v): return BOT - v / VMAX * (BOT - TOP)

    # осі
    f.append(arrow(Lm, BOT, Rm + 16, BOT, color=INK, sw=1.8))
    f.append(arrow(Lm, BOT, Lm, TOP - 10, color=INK, sw=1.8))
    f.append(text(Lm - 8, TOP - 16, "цінність тижня, €", size=12, color=MUTED, anchor="start"))

    # зони «чекай / вирішуй» — у просвітах над стовпцями
    f.append(text((Xc(1) + Xc(2)) / 2, 150, "ЧЕКАЙ", size=15, bold=True, color=FIELD))
    f.append(text((Xc(4) + Xc(5)) / 2, 150, "ВИРІШУЙ", size=15, bold=True, color=POS))

    # стовпці граничної цінності тижня
    for i in weeks:
        v = val[i]
        up = v > COD
        col = FIELD if up else POS
        fill = "#eafaf0" if up else "#fdecea"
        f.append(rect(Xc(i) - bw / 2, Y(v), bw, BOT - Y(v), fill=fill, stroke=col, sw=2.0, rx=5))
        f.append(text(Xc(i), Y(v) - 9, "%d €" % v, size=12, bold=True, color=col))
        f.append(text(Xc(i), BOT + 20, "тижд. %d" % i, size=11, color=INK))

    # лінія вартості зволікання
    ly = Y(COD)
    f.append(line(Lm, ly, Rm, ly, color=NEG, sw=2.2, dash="7,5"))
    f.append(text(Rm - 4, ly - 10, "вартість зволікання = 4000 €/тиждень",
                  size=12, bold=True, color=NEG, anchor="end"))

    # LRM — межа між тижнями 2 і 3
    xb = Lm + 2 * slot
    f.append(line(xb, TOP, xb, BOT, color=FIELD, sw=1.8, dash="4,5"))
    f.append(fitbox(xb - 132, BOT + 32, 264, 26,
                    "останній відповідальний момент · Δt ≈ 2 тижні",
                    size=12, fill="#eafaf0", stroke=FIELD, color=INK, bold=True))

    render(os.path.join(IMG, "voi-marginal.svg"), W, H, *f)


# ───────── Фіг. 6 (вставка math): цінність інформації під стелею EVPI ─────────
def fig_voi_ceiling():
    W, H = 900, 520
    f = [text(W / 2, 34, "Цінність зібраної інформації тримається під стелею EVPI і має спадну віддачу",
              size=15, bold=True)]

    Lm, Rm, TOP, BOT = 118, 786, 150, 408
    TMAX, VMAX = 7.0, 32000.0

    def X(t): return Lm + t / TMAX * (Rm - Lm)
    def Y(v): return BOT - v / VMAX * (BOT - TOP)

    evsi = [(0, 0), (1, 5400), (2, 9600), (3, 12600), (4, 15000), (5, 16800), (6, 18000)]

    def cost(t): return 4000.0 * t
    EVPI = 30000

    # осі
    f.append(arrow(Lm, BOT, Rm + 16, BOT, color=INK, sw=1.8))
    f.append(arrow(Lm, BOT, Lm, TOP - 12, color=INK, sw=1.8))
    f.append(text(Rm + 10, BOT + 24, "тижні очікування Δt →", size=12, color=MUTED, anchor="end"))
    f.append(text(Lm - 8, TOP - 18, "€", size=13, color=MUTED, anchor="start"))

    # легенда (ліворуч угорі, у вільній зоні над кривими)
    def leg(x, y, label, color):
        s = line(x, y, x + 26, y, color=color, sw=3.0)
        s += text(x + 32, y + 4, label, size=12, bold=True, color=color, anchor="start")
        return s
    f.append(leg(150, 70, "EVSI(Δt) — вартість зібраної інформації", FIELD))
    f.append(leg(150, 92, "CoD·Δt — скільки коштує її зібрати", NEG))

    # стеля EVPI
    yc = Y(EVPI)
    f.append(line(Lm, yc, Rm, yc, color=POS, sw=2.0, dash="8,5"))
    f.append(text(Rm - 4, yc - 26, "стеля EVPI = 30 000 €", size=13, bold=True, color=POS, anchor="end"))
    f.append(text(Rm - 4, yc - 10, "більша за неї інформація не варта нічого", size=11, color=MUTED, anchor="end"))

    # крива вартості збору CoD·Δt
    f.append(polyline([(X(t), Y(cost(t))) for t in range(8)], NEG, sw=2.6))

    # крива EVSI
    f.append(polyline([(X(t), Y(v)) for t, v in evsi], FIELD, sw=2.8))
    for t, v in evsi:
        f.append(dot(X(t), Y(v), 3.4, FIELD))

    # LRM — Δt=2 (найбільший розрив між кривими)
    xl = X(2)
    f.append(line(xl, Y(9600), xl, BOT, color=FIELD, sw=1.6, dash="4,5"))
    f.append(fitbox(xl - 58, BOT + 30, 116, 24, "LRM · Δt ≈ 2",
                    size=11, fill="#eafaf0", stroke=FIELD, color=INK, bold=True))

    # беззбитковість — перетин EVSI і CoD·Δt (≈ Δt 3.4)
    xbe = X(3.4)
    ybe = Y(13600)
    f.append(line(xbe, ybe, xbe, BOT, color=INK, sw=1.4, dash="3,4"))
    f.append(circle(xbe, ybe, 5.5, fill=BG, stroke=INK, sw=1.6))
    f.append(fitbox(xbe - 4, BOT + 30, 150, 24, "беззбитк. · Δt ≈ 3.4",
                    size=11, fill=FILL, stroke=MUTED, color=INK))

    render(os.path.join(IMG, "voi-ceiling.svg"), W, H, *f)


# ═════════════ ФІГУРИ ДЕТАЛЬНОЇ СТАТТІ (нижче — тільки для -d.md) ═════════════

# ───────── Фіг. D1: три профілі вартості зволікання ─────────
def fig_cod_profiles():
    W, H = 900, 520
    f = [text(W / 2, 32, "Вартість зволікання має форму: три профілі накопиченої втрати",
              size=16, bold=True)]

    L, R, TOP, BOT = 120, 762, 116, 410
    TMAX, VMAX = 12.0, 100.0

    def X(t): return L + t / TMAX * (R - L)
    def Y(v): return BOT - v / VMAX * (BOT - TOP)

    # підпис осі + легенда — окремими рядками, без накладань
    f.append(text(L - 8, 58, "втрата, €", size=12, color=MUTED, anchor="start"))

    ly = 90

    def leg(x, label, color):
        seg = line(x, ly, x + 24, ly, color=color, sw=3.2)
        seg += text(x + 30, ly + 4, label, size=12, bold=True, color=color, anchor="start")
        return seg, x + 30 + text_width(label, 12, True) + 26
    s, x2 = leg(150, "рівна (передплата тече)", INK); f.append(s)
    s, x3 = leg(x2, "швидкопсувна (вікно ринку)", POS); f.append(s)
    s, _ = leg(x3, "дедлайн (уступ)", NEG); f.append(s)

    # осі
    f.append(arrow(L, BOT, R + 18, BOT, color=INK, sw=1.8))
    f.append(arrow(L, BOT, L, TOP - 12, color=INK, sw=1.8))
    f.append(text(R + 22, BOT + 22, "коли вирішуємо →", size=12, color=MUTED, anchor="end"))

    ts = [i * 0.2 for i in range(int(TMAX / 0.2) + 1)]
    steady = [(X(t), Y(6.0 * t)) for t in ts]
    perish = [(X(t), Y(90.0 * (1 - math.exp(-t / 2.5)))) for t in ts]
    Tdl = 8.0
    dl_pre = [(X(t), Y(2.0 * t)) for t in ts if t <= Tdl]
    dl_post = [(X(t), Y(2.0 * t + 55)) for t in ts if t >= Tdl]

    # маркер дедлайну — під кривими, щоб напис не ліг на лінії
    f.append(line(X(Tdl), TOP, X(Tdl), BOT, color=MUTED, sw=1.2, dash="4,5"))

    f.append(polyline(steady, INK, sw=2.6))
    f.append(polyline(perish, POS, sw=2.6))
    f.append(polyline(dl_pre, NEG, sw=2.6))
    f.append(polyline(dl_post, NEG, sw=2.6))
    f.append(line(X(Tdl), Y(2.0 * Tdl), X(Tdl), Y(2.0 * Tdl + 55), color=NEG, sw=2.6, dash="2,3"))

    f.append(fitbox(X(Tdl) - 74, BOT + 12, 148, 26, "дедлайн: уступ втрати",
                    size=11, fill="#eef1f4", stroke=MUTED, color=INK, bold=True))

    render(os.path.join(IMG, "cod-profiles.svg"), W, H, *f)


# ───────── Фіг. D2: розклад вартості помилки на підлогу й зменшуване ─────────
def fig_uncertainty_decomp():
    W, H = 900, 500
    f = [text(W / 2, 32, "Вартість помилки має підлогу: чеканням зменшити лише епістемічну частину",
              size=15, bold=True)]

    L, R, TOP, BOT = 120, 770, 120, 402
    PMAX, TMAX, floor = 0.55, 12.0, 0.15

    def X(t): return L + t / TMAX * (R - L)
    def Y(p): return BOT - p / PMAX * (BOT - TOP)
    def total(t): return floor + 0.35 * math.exp(-t / 3.0)

    ts = [i * 0.15 for i in range(int(TMAX / 0.15) + 1)]

    # смуги: алеаторна підлога (низ) та епістемічний клин (між кривою й підлогою)
    f.append(fillpoly([(L, Y(0)), (R, Y(0)), (R, Y(floor)), (L, Y(floor))], "#fdecea"))
    wedge = [(X(t), Y(total(t))) for t in ts] + [(R, Y(floor)), (L, Y(floor))]
    f.append(fillpoly(wedge, "#eaf0fd"))

    f.append(line(L, Y(floor), R, Y(floor), color=POS, sw=2.2, dash="7,5"))
    f.append(polyline([(X(t), Y(total(t))) for t in ts], NEG, sw=2.8))

    # осі
    f.append(arrow(L, BOT, R + 18, BOT, color=INK, sw=1.8))
    f.append(arrow(L, BOT, L, TOP - 12, color=INK, sw=1.8))
    f.append(text(R + 14, BOT + 22, "тижні чекання →", size=12, color=MUTED, anchor="end"))
    f.append(text(L - 8, TOP - 18, "P(схибив)", size=12, color=MUTED, anchor="start"))
    f.append(text(L - 12, Y(0.5) + 4, "0.5", size=11, color=MUTED, anchor="end"))
    f.append(text(L - 12, Y(floor) + 4, "0.15", size=11, color=POS, anchor="end", bold=True))

    # чипи-написи — у своїх рамках, у товщі відповідних смуг
    f.append(fitbox(X(2.0) - 66, Y(0.24) - 16, 132, 32, "епістемічна\n(зменшувана)",
                    size=11, fill="#eaf0fd", stroke=NEG, color=INK, bold=True))
    f.append(fitbox(X(6.0) - 124, Y(0.075) - 14, 248, 28,
                    "алеаторна підлога — чеканням не зменшити",
                    size=11, fill="#fdecea", stroke=POS, color=INK, bold=True))
    f.append(fitbox(R - 196, TOP - 2, 196, 26, "нижче підлоги чекати марно",
                    size=11, fill="#fff8e8", stroke="#c9a93b", color=INK))

    render(os.path.join(IMG, "uncertainty-decomp.svg"), W, H, *f)


# ───────── Фіг. D3: порт і адаптери — зворотність як властивість підключення ─────────
def fig_ports_adapters():
    W, H = 900, 470
    f = [text(W / 2, 32, "Зворотність — властивість підключення: порт і адаптери",
              size=16, bold=True)]

    f.append(fitbox(90, 150, 270, 150,
                    "ДОМЕН\nпанель енергоспоживання\n\nзалежить лише від порту,\nне знає, яка база всередині",
                    size=13, fill="#eafaf0", stroke=FIELD, color=INK))
    f.append(fitbox(400, 168, 160, 114, "порт\nTelemetryStore\n\nwrite() · query()",
                    size=13, fill="#fff8e8", stroke="#c9a93b", color=INK, bold=True))

    adapters = [(96, "Postgres-адаптер\n(активний)", FIELD, "#eafaf0", True),
                (188, "Timescale-адаптер", MUTED, "#f4f6f8", False),
                (280, "Influx-адаптер", MUTED, "#f4f6f8", False)]
    ax = 620
    f.append(line(360, 225, 400, 225, color=FIELD, sw=2.4))
    for ay, label, col, fill, active in adapters:
        f.append(line(560, 225, ax, ay + 32, color=col, sw=2.0, dash=None if active else "4,4"))
    for ay, label, col, fill, active in adapters:
        f.append(fitbox(ax, ay, 210, 64, label, size=12, fill=fill, stroke=col, color=INK, bold=True))

    f.append(fitbox(90, 360, 720, 40,
                    "Схибив із базою → пишеш новий адаптер за тим самим портом. "
                    "Домен і решта коду не змінюються: незворотне стало зворотним.",
                    size=12, fill="#fdecea", stroke=POS, color=INK))

    render(os.path.join(IMG, "ports-adapters.svg"), W, H, *f)


# ───────── Фіг. D4: черга рішень і WSJF ─────────
def fig_wsjf():
    W, H = 900, 560
    f = [text(W / 2, 32, "Черга рішень: сортуй за CoD на одиницю тривалості (WSJF)",
              size=16, bold=True)]

    cards = [
        (60,  "ТЕЛЕМЕТРІЯ",    "CoD 4000 €/тиж · 2 тиж", "WSJF = 4000 / 2 = 2000", FIELD, "#eafaf0"),
        (325, "АВТЕНТИФІКАЦІЯ", "CoD 1500 €/тиж · 1 тиж", "WSJF = 1500 / 1 = 1500", NEG,   "#eaf0fd"),
        (590, "БІЛІНГ",         "CoD 6000 €/тиж · 6 тиж", "WSJF = 6000 / 6 = 1000", POS,   "#fdecea"),
    ]
    for x, head, body, wsjf, col, fill in cards:
        f.append(rect(x, 78, 250, 118, fill=fill, stroke=col, sw=2.2, rx=10))
        f.append(text(x + 125, 108, head, size=14, bold=True, color=col))
        f.append(text(x + 125, 138, body, size=12, color=INK))
        f.append(line(x + 18, 152, x + 232, 152, color="#dfe4e9", sw=1.2))
        f.append(text(x + 125, 176, wsjf, size=13, bold=True, color=INK))

    f.append(text(90, 258,
                  "Сумарна вартість зволікання за весь розбір черги (та сама робота, різний порядок):",
                  size=13, bold=True, anchor="start"))

    x0, xend, VMAX = 380, 850, 90000.0

    def Lb(v): return (xend - x0) * v / VMAX

    def money(v): return format(int(v), ",d").replace(",", " ") + " €"

    bars = [("порядок WSJF: 2000 → 1500 → 1000", 66500, FIELD),
            ("спершу найбільша CoD: білінг першим", 81500, POS)]
    ys, bh = [312, 384], 46
    f.append(line(x0, 292, x0, 410, color="#c8ced6", sw=1.4))
    for (label, v, col), yc in zip(bars, ys):
        f.append(text(x0 - 16, yc + 5, label, size=12, bold=True, color=INK, anchor="end"))
        f.append(rect(x0, yc - bh / 2, Lb(v), bh, fill=col, stroke=col, sw=1, rx=5))
        f.append(text(x0 + Lb(v) + 12, yc + 5, money(v), size=13, bold=True, color=col, anchor="start"))

    f.append(fitbox(90, 452, 720, 44,
                    "Вирішує не найбільша CoD, а CoD на одиницю тривалості. Білінг найдорожчий у "
                    "зволіканні, та такий довгий, що пропускає вперед двох коротших — і сумарна "
                    "втрата падає на 15 000 €.",
                    size=12, fill="#fff8e8", stroke="#c9a93b", color=INK))

    render(os.path.join(IMG, "wsjf.svg"), W, H, *f)


# ───────── Фіг. M (вставка math-wsjf): спуск до WSJF обміном сусідів ─────────
def fig_wsjf_descent():
    W, H = 900, 572
    f = [text(W / 2, 28, "Будь-який не-WSJF порядок здешевлюється обміном сусідів — аж до дна",
              size=16, bold=True)]

    x0, bw, gap = 126, 200, 14
    xs = [x0, x0 + bw + gap, x0 + 2 * (bw + gap)]     # 126, 340, 554 → край 754
    bh = 72
    tops = [90, 266, 442]

    COL = {"телеметрія": FIELD, "автентифікація": NEG, "білінг": POS}
    FILLC = {"телеметрія": "#eafaf0", "автентифікація": "#eaf0fd", "білінг": "#fdecea"}
    RAT = {"телеметрія": "CoD/трив = 2000", "автентифікація": "CoD/трив = 1500", "білінг": "CoD/трив = 1000"}

    states = [
        (["білінг", "телеметрія", "автентифікація"], "81 500 €", "білінг блокує двох", POS),
        (["телеметрія", "білінг", "автентифікація"], "69 500 €", "ще є інверсія", MUTED),
        (["телеметрія", "автентифікація", "білінг"], "66 500 €", "оптимум", FIELD),
    ]

    for (order, total, tag, tagcol), top in zip(states, tops):
        for xi, name in zip(xs, order):
            f.append(rect(xi, top, bw, bh, fill=FILLC[name], stroke=COL[name], sw=2.2, rx=10))
            f.append(text(xi + bw / 2, top + 30, name, size=14, bold=True, color=COL[name]))
            f.append(text(xi + bw / 2, top + 54, RAT[name], size=12, color=INK))
        f.append(text(886, top + 34, total, size=17, bold=True, color=tagcol, anchor="end"))
        f.append(text(886, top + 56, tag, size=11, color=MUTED, anchor="end"))

    def swap(y_from, y_to, note):
        f.append(arrow(196, y_from, 196, y_to, color=INK, sw=2.0))
        f.append(fitbox(250, (y_from + y_to) / 2 - 29, 448, 58, note,
                        size=12, fill="#fff8e8", stroke="#c9a93b", color=INK))

    swap(170, 258,
         "обмін сусідів: білінг ↔ телеметрія\n"
         "1000 < 2000 — інверсія, тож своп здешевлює\n"
         "своп заощаджує  4000·6 − 6000·2 = 12 000 €")
    swap(346, 434,
         "обмін сусідів: білінг ↔ автентифікація\n"
         "1000 < 1500 — інверсія\n"
         "своп заощаджує  1500·6 − 6000·1 = 3 000 €")

    f.append(text(126, 74, "СТАРТ", size=12, bold=True, color=POS, anchor="start"))
    f.append(text(126, 536, "ДНО — жоден обмін сусідів уже не покращує порядок",
                  size=12, bold=True, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "wsjf-descent.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ucurve()
    fig_quadrants()
    fig_plan_bars()
    fig_lineage()
    fig_voi_marginal()
    fig_voi_ceiling()
    fig_cod_profiles()
    fig_uncertainty_decomp()
    fig_ports_adapters()
    fig_wsjf()
    fig_wsjf_descent()
    print("OK base: cost-ucurve, cost-quadrants, cost-plan-bars, cost-lineage, voi-marginal, voi-ceiling")
    print("OK detailed: cod-profiles, uncertainty-decomp, ports-adapters, wsjf")
    print("OK insert: wsjf-descent")
