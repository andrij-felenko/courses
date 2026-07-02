# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: одна петля — джерело, давач-струмостік, приймач-резистор ──────
def fig_loop():
    W, H = 760, 360
    f = []
    f.append(text(W/2, 26, "Струмова петля: один контур, той самий струм усюди", size=16, bold=True))

    # координати кутів петлі
    L, R = 110, 650
    T, B = 80, 300

    # давач/передавач (ліворуч), приймач+резистор (праворуч-низ), живлення (праворуч-верх)
    # верхній і нижній дроти
    f.append(line(L, T, R, T, color=INK, sw=2.4))      # верхня жила
    f.append(line(L, B, R, B, color=INK, sw=2.4))      # нижня жила

    # ── передавач: керована «заслінка» струму (квадрат із позначкою) ──
    bx, bw = L-2, 150
    f.append(rect(L-58, T+22, 116, B-T-44, fill="#eef6ff", stroke=NEG, sw=2))
    f.append(mtext((L)/1, (T+B)/2-10, ["Передавач", "(давач)"], size=14, bold=True))
    f.append(text(L, (T+B)/2+22, "регулює струм", size=11, color=MUTED))
    # вертикальна сторона передавача замикає петлю зліва
    f.append(line(L, T+22, L, T, color=INK, sw=2.4))
    f.append(line(L, B, L, B-22, color=INK, sw=2.4))

    # ── живлення 24 В (праворуч-верх) ──
    px = R
    f.append(line(px, T, px, 150, color=INK, sw=2.4))
    f.append(plus(px, 150-14))
    f.append(line(px-9, 175, px+9, 175, color=INK, sw=3))   # довга риска батареї
    f.append(line(px-6, 184, px+6, 184, color=INK, sw=2))   # коротка
    f.append(text(px+58, 168, "24 В", size=14, bold=True))
    f.append(text(px+58, 188, "живлення", size=11, color=MUTED))

    # ── приймач: вимірювальний резистор + АЦП (праворуч-низ) ──
    f.append(line(px, 200, px, B, color=INK, sw=2.4))
    rbx, rby, rbw, rbh = px-26, 198, 52, 64
    f.append(rect(rbx, rby, rbw, rbh, fill="#f4f6f8", stroke=INK, sw=1.8))
    f.append(text(px, 224, "R", size=15, bold=True))
    f.append(text(px, 244, "250 Ω", size=11, color=MUTED))
    f.append(text(px+78, 222, "падіння", size=11, color=MUTED))
    f.append(text(px+78, 238, "1…5 В", size=13, bold=True, color=FIELD))
    f.append(text(px+78, 256, "→ АЦП", size=11, color=MUTED))

    # стрілки напряму струму на жилах
    f.append(arrow(330, T, 410, T, color=POS, sw=2.4))
    f.append(arrow(410, B, 330, B, color=POS, sw=2.4))
    f.append(text(370, T-10, "I = 4…20 мА", size=13, bold=True, color=POS))
    f.append(text(370, B+22, "той самий I повертається", size=12, color=MUTED))

    render(os.path.join(IMG, 'loop.svg'), W, H, *f)


# ── Фігура 2: шкала струму за NAMUR NE43 ───────────────────────────────────
def fig_scale():
    W, H = 760, 320
    f = []
    f.append(text(W/2, 26, "Що означає кожен рівень струму (NAMUR NE43)", size=16, bold=True))

    x0, x1 = 90, 690
    y = 150
    mA0, mA1 = 3.0, 22.0
    def X(mA): return x0 + (mA - mA0)/(mA1 - mA0) * (x1 - x0)

    # робоча смуга 4..20 зелена; під/над — жовта; аварія — червона
    f.append(rect(X(3.0), y-16, X(3.6)-X(3.0), 32, fill="#fdecea", stroke=POS, sw=1.2))   # <3.6 аварія низ
    f.append(rect(X(3.6), y-16, X(3.8)-X(3.6), 32, fill="#fff6e5", stroke="#d08a00", sw=1.2))
    f.append(rect(X(3.8), y-16, X(20.5)-X(3.8), 32, fill="#eafaf0", stroke=FIELD, sw=1.4))
    f.append(rect(X(20.5), y-16, X(21.0)-X(20.5), 32, fill="#fff6e5", stroke="#d08a00", sw=1.2))
    f.append(rect(X(21.0), y-16, X(22.0)-X(21.0), 32, fill="#fdecea", stroke=POS, sw=1.2))

    # вісь зі штрихами
    f.append(line(x0, y+30, x1, y+30, color=INK, sw=1.6))
    for mA in [3.6, 3.8, 4.0, 20.0, 20.5, 21.0]:
        f.append(line(X(mA), y+26, X(mA), y+34, color=INK, sw=1.4))
        f.append(text(X(mA), y+50, ("%.1f" % mA), size=12))
    f.append(text((X(4.0)+X(20.0))/2, y+50, "мА", size=12, color=MUTED, anchor="start"))

    # підписи смуг
    f.append(text(X(4.0), y-26, "0 %", size=12, bold=True, color=FIELD))
    f.append(text(X(20.0), y-26, "100 %", size=12, bold=True, color=FIELD))
    f.append(text((X(3.8)+X(20.5))/2, y+4, "вимір 4…20", size=12, color=FIELD, bold=True))

    # виноски вниз
    f.append(text(X(3.4), y+78, "< 3.6: обрив,", size=11, color=POS, bold=True))
    f.append(text(X(3.4), y+94, "коротке, відмова", size=11, color=POS))
    f.append(text(X(21.5), y+78, "> 21: відмова", size=11, color=POS, bold=True))
    f.append(text(X(21.5), y+94, "вгору", size=11, color=POS))
    f.append(text((X(3.6)+X(3.8))/2, y+118, "запас живлення", size=10, color="#9a6a00"))
    f.append(line((X(3.6)+X(3.8))/2, y+34, (X(3.6)+X(3.8))/2, y+108, color="#d08a00", sw=1, dash="3,3"))

    render(os.path.join(IMG, 'scale.svg'), W, H, *f)


# ── Фігура 3: напруга-проти-струму — чому струм не «втрачається» на дроті ──
def fig_why_current():
    W, H = 760, 330
    f = []
    f.append(text(W/2, 26, "Чому струмом, а не напругою: опір дроту краде напругу, не струм",
                  size=15, bold=True))

    midy = 175
    # ліворуч — «напругою» (погано), праворуч — «струмом» (добре)
    # ── напругою ──
    box, w, h = textbox(200, 70, "Передавали б НАПРУГУ", size=13, bold=True,
                        fill="#fdecea", stroke=POS, min_w=300)
    f.append(box)
    f.append(line(80, midy, 320, midy, color=INK, sw=2))
    # три послідовні опори дроту
    for i, cx in enumerate([130, 200, 270]):
        f.append(rect(cx-18, midy-9, 36, 18, fill="#f4f6f8", stroke=MUTED, sw=1.3))
        f.append(text(cx, midy+5, "Rдр", size=10, color=MUTED))
    f.append(text(200, midy-22, "падіння на кожному → 5.00 В стає 4.7 В", size=11, color=POS))
    f.append(text(200, midy+34, "приймач читає менше — помилка росте з довжиною", size=11, color=POS, bold=True))

    # ── струмом ──
    box2, w2, h2 = textbox(560, 70, "Передаємо СТРУМ", size=13, bold=True,
                          fill="#eafaf0", stroke=FIELD, min_w=300)
    f.append(box2)
    f.append(line(440, midy, 680, midy, color=INK, sw=2))
    for i, cx in enumerate([490, 560, 630]):
        f.append(rect(cx-18, midy-9, 36, 18, fill="#f4f6f8", stroke=MUTED, sw=1.3))
        f.append(text(cx, midy+5, "Rдр", size=10, color=MUTED))
    f.append(arrow(470, midy, 650, midy, color=POS, sw=2))
    f.append(text(560, midy-22, "послідовне коло → струм один на всіх", size=11, color=FIELD))
    f.append(text(560, midy+34, "12.00 мА входить = 12.00 мА доходить", size=11, color=FIELD, bold=True))
    f.append(text(560, midy+52, "опір дроту лише з'їдає запас напруги", size=10, color=MUTED))

    render(os.path.join(IMG, 'why-current.svg'), W, H, *f)


# ── Вставка hist: заслінка-сопло — як тиск стає сигналом ───────────────────
def fig_flapper():
    W, H = 760, 360
    f = []
    f.append(text(W/2, 26, "Заслінка-сопло: серце пневматики (1940–70-ті)", size=16, bold=True))

    # подача повітря зліва через дросель (restriction), далі сопло, перед ним заслінка
    yair = 150
    xsupply, xrestr, xnozzle = 90, 250, 430
    # лінія подачі
    f.append(text(xsupply-2, yair-34, "подача", size=11, color=MUTED))
    f.append(text(xsupply-2, yair-18, "20 psi", size=12, bold=True, color=NEG))
    f.append(line(xsupply, yair, xrestr-22, yair, color=NEG, sw=3))
    # дросель (вузьке місце)
    f.append(rect(xrestr-22, yair-7, 22, 14, fill="#eaf0fd", stroke=NEG, sw=1.6))
    f.append(text(xrestr-11, yair+30, "дросель", size=10, color=MUTED))
    # камера до сопла (тут і знімають сигнал)
    f.append(line(xrestr, yair, xnozzle, yair, color=INK, sw=3))
    # відведення сигналу вгору
    f.append(line((xrestr+xnozzle)/2, yair, (xrestr+xnozzle)/2, yair-60, color=POS, sw=2.6))
    f.append(arrow((xrestr+xnozzle)/2, yair-30, (xrestr+xnozzle)/2, yair-58, color=POS, sw=2.6))
    f.append(text((xrestr+xnozzle)/2, yair-70, "сигнал тиску", size=12, bold=True, color=POS))
    f.append(text((xrestr+xnozzle)/2, yair-86, "3…15 psi", size=13, bold=True, color=POS))
    # сопло (звужений вихід)
    f.append(line(xnozzle, yair-6, xnozzle+18, yair, color=INK, sw=2.4))
    f.append(line(xnozzle, yair+6, xnozzle+18, yair, color=INK, sw=2.4))
    f.append(text(xnozzle-4, yair+30, "сопло", size=10, color=MUTED))

    # заслінка (рухома пластина), зазор d
    fx = xnozzle+30
    f.append(line(fx, yair-46, fx, yair+46, color=INK, sw=4))
    f.append(text(fx+10, yair-40, "заслінка", size=11, bold=True))
    f.append(text(fx+10, yair-24, "(рух вимірюваного)", size=10, color=MUTED))
    # зазор
    f.append(line(xnozzle+18, yair-14, fx, yair-14, color=POS, sw=1, dash="3,3"))
    f.append(text((xnozzle+18+fx)/2, yair-18, "d", size=12, bold=True, color=POS))

    # дві підказки: близько → тиск росте; далеко → тиск падає
    box1, w1, h1 = textbox(200, 280, ["заслінка БЛИЖЧЕ →", "вихід перекритий →", "тиск РОСТЕ → 15 psi"],
                           size=12, fill="#fdecea", stroke=POS, min_w=240)
    f.append(box1)
    box2, w2, h2 = textbox(560, 280, ["заслінка ДАЛІ →", "повітря виходить →", "тиск ПАДАЄ → 3 psi"],
                           size=12, fill="#eaf0fd", stroke=NEG, min_w=240)
    f.append(box2)

    render(os.path.join(IMG, 'flapper.svg'), W, H, *f)


# ── Вставка hist: дзеркало логіки — 3–15 psi ↔ 4–20 мА ─────────────────────
def fig_psi_to_ma():
    W, H = 760, 320
    f = []
    f.append(text(W/2, 26, "Та сама логіка: пневматику скопіювали в струм (~1:5)", size=16, bold=True))

    # дві вертикальні шкали поруч: psi (ліворуч), мА (праворуч)
    yT, yB = 80, 250
    xpsi, xma = 230, 530

    def vscale(x, lo_lbl, hi_lbl, color, unit):
        out = [line(x, yT, x, yB, color=INK, sw=2.4)]
        # «живий нуль» — нижня риска піднята над абсолютним нулем
        out.append(line(x-30, yB, x+30, yB, color=color, sw=3))      # 0 % (живий нуль)
        out.append(line(x-30, yT, x+30, yT, color=color, sw=3))      # 100 %
        out.append(text(x-44, yB+5, lo_lbl, size=13, bold=True, color=color, anchor="end"))
        out.append(text(x-44, yT+5, hi_lbl, size=13, bold=True, color=color, anchor="end"))
        out.append(text(x+40, yB+5, "0 %", size=12, color=MUTED, anchor="start"))
        out.append(text(x+40, yT+5, "100 %", size=12, color=MUTED, anchor="start"))
        out.append(text(x, yT-16, unit, size=13, bold=True))
        # абсолютний нуль (пунктир нижче живого нуля) — показати «запас»
        out.append(line(x-30, yB+40, x+30, yB+40, color=MUTED, sw=1.4, dash="4,4"))
        out.append(text(x, yB+58, "справжній 0", size=10, color=MUTED))
        return out

    f += vscale(xpsi, "3 psi", "15 psi", NEG, "тиск")
    f += vscale(xma, "4 мА", "20 мА", FIELD, "струм")

    # стрілка-копіювання між шкалами
    f.append(arrow(xpsi+70, (yT+yB)/2, xma-70, (yT+yB)/2, color=POS, sw=2.6))
    f.append(text((xpsi+xma)/2, (yT+yB)/2-12, "скопійовано", size=13, bold=True, color=POS))
    f.append(text((xpsi+xma)/2, (yT+yB)/2+20, "1950-ті", size=12, color=MUTED))

    # підпис унизу — спільна ідея
    f.append(text(W/2, 300, "Нижній край не на нулі → обрив лінії видно сам собою (живий нуль)",
                  size=12, color=INK))

    render(os.path.join(IMG, 'psi-to-ma.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставки comp-loop-powered-transmitter
# ════════════════════════════════════════════════════════════════════════════

# ── Блок-схема двопровідного передавача: вхід → кондиціонер → опора → стік ───
def fig_xmtr_blocks():
    W, H = 800, 390
    f = []
    f.append(text(W/2, 26, "Двопровідний передавач: усе живиться від тих самих двох клем",
                  size=15, bold=True))

    # дві шини: верхня V+ (струм заходить), нижня зворот (струм виходить крізь стік)
    Lx, Rx = 60, 700
    topw, botw = 72, 320

    f.append(line(Lx, topw, Rx, topw, color=INK, sw=2.4))
    f.append(line(Lx, botw, Rx, botw, color=INK, sw=2.4))

    # клеми праворуч
    f.append(circle(Rx, topw, 6, fill=BG, stroke=INK, sw=2))
    f.append(circle(Rx, botw, 6, fill=BG, stroke=INK, sw=2))
    f.append(text(Rx+30, topw+5, "+ клема", size=12, bold=True, anchor="start"))
    f.append(text(Rx+30, botw+5, "− клема", size=12, bold=True, anchor="start"))
    f.append(mtext(Rx+30, (topw+botw)/2-4,
                   ["у петлю", "(джерело", "і приймач)"], size=10, color=MUTED, anchor="start"))

    # блоки тракту (живляться згори від V+)
    bx, bw, bh = 78, 138, 38
    rows = [("Давач / міст", "міряє величину"),
            ("Підсилювач-", "кондиціонер"),
            ("Опорне джерело", "стабільний нуль")]
    ys = [98, 162, 226]
    for (t1, sub), y in zip(rows, ys):
        f.append(rect(bx, y, bw, bh, fill="#eef6ff", stroke=NEG, sw=1.8))
        f.append(text(bx+bw/2, y+17, t1, size=12, bold=True))
        f.append(text(bx+bw/2, y+32, sub, size=10, color=MUTED))
        f.append(line(bx+bw/2, topw, bx+bw/2, y, color=MUTED, sw=1.1, dash="3,3"))

    f.append(arrow(bx+bw/2, ys[0]+bh, bx+bw/2, ys[1], color=FIELD, sw=1.8))
    f.append(arrow(bx+bw/2, ys[1]+bh, bx+bw/2, ys[2], color=FIELD, sw=1.8))

    # керована заслінка струму
    sx, sy, sbw, sbh = 470, 150, 168, 80
    f.append(rect(sx, sy, sbw, sbh, fill="#eafaf0", stroke=FIELD, sw=2.2))
    f.append(mtext(sx+sbw/2, sy+24, ["Керована", "заслінка струму"], size=13, bold=True))
    f.append(text(sx+sbw/2, sy+64, "(output stage)", size=10, color=MUTED))

    f.append(arrow(bx+bw, ys[2]+bh/2, sx, sy+sbh/2, color=FIELD, sw=1.8))
    f.append(mtext((bx+bw+sx)/2, sy+sbh/2-6, ["скільки", "лити"], size=10, color=FIELD))

    # заслінка ввімкнена між V+ і зворотом
    f.append(line(sx+sbw/2, topw, sx+sbw/2, sy, color=INK, sw=2.4))
    f.append(line(sx+sbw/2, sy+sbh, sx+sbw/2, botw, color=INK, sw=2.4))
    f.append(arrow(sx+sbw/2+0.1, sy+sbh+8, sx+sbw/2+0.1, botw-8, color=POS, sw=2.6))
    f.append(text(sx+sbw+22, (sy+sbh+botw)/2-6, "I_петлі", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(sx+sbw+22, (sy+sbh+botw)/2+12, "4…20 мА", size=11, color=POS, anchor="start"))

    f.append(text(W/2, H-16,
                  "Заслінка добирає струм так, щоб СУМАРНИЙ струм клем дорівнював сигналу",
                  size=11, color=MUTED))

    render(os.path.join(IMG, 'xmtr-blocks.svg'), W, H, *f)


# ── Бюджет 4 мА: «гаманець» струму нуля шкали ───────────────────────────────
def fig_budget():
    W, H = 780, 350
    f = []
    f.append(text(W/2, 26, "Бюджет 4 мА: усе всередині має вміститися в струм нуля шкали",
                  size=15, bold=True))

    bx, by, bw, bh = 130, 76, 92, 210
    f.append(rect(bx, by, bw, bh, fill=BG, stroke=INK, sw=2))
    f.append(text(bx+bw/2, by-14, "4.0 мА", size=14, bold=True, color=POS))
    f.append(mtext(bx+bw/2, by+bh+20, ["стеля", "нуля шкали"], size=11, color=MUTED))

    segs = [("опора", 0.7, "#dfe7f5"),
            ("підсилювач", 0.6, "#cdd9ee"),
            ("давач / міст", 0.5, "#bccbe6"),
            ("АЦП / МК", 1.0, "#aabddd"),
            ("запас > 0", 1.2, "#eafaf0")]
    total = sum(s[1] for s in segs)
    y = by + bh
    for name, val, col in segs:
        seg_h = bh * val / total
        y -= seg_h
        stroke = FIELD if "запас" in name else NEG
        f.append(rect(bx, y, bw, seg_h, fill=col, stroke=stroke, sw=1.4))
        ly = y + seg_h/2
        f.append(line(bx+bw, ly, bx+bw+28, ly, color=MUTED, sw=1))
        lbl = "%s  (~%.1f мА)" % (name, val)
        f.append(text(bx+bw+34, ly+4, lbl, size=12, anchor="start",
                      color=(FIELD if "запас" in name else INK), bold=("запас" in name)))

    box, w, h = textbox(560, 168,
        ["ПРАВИЛО БЮДЖЕТУ", "",
         "Σ(внутрішні струми)", "у нулі шкали  <  4 мА", "",
         "перевищив → петля не", "опуститься до 4 мА:", "нуль «спливає» вгору"],
        size=12, fill="#fdf3f0", stroke=POS, sw=1.6, min_w=300)
    f.append(box)

    render(os.path.join(IMG, 'budget.svg'), W, H, *f)


# ── Керування з від'ємним зв'язком: стік ловить власний струм ──────────────
def fig_feedback():
    W, H = 780, 340
    f = []
    f.append(text(W/2, 26, "Як заслінка задає струм: від'ємний зв'язок ловить власний струм петлі",
                  size=15, bold=True))

    ax, ay = 165, 168
    tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="#eef6ff" '
           'stroke="%s" stroke-width="2"/>') % (ax-32, ay-34, ax-32, ay+34, ax+42, ay, NEG)
    f.append(tri)
    f.append(text(ax-4, ay+6, "−", size=22, bold=True, color=NEG))
    f.append(text(ax-2, ay-46, "підсилювач помилки", size=11, color=MUTED))

    # уставка
    f.append(arrow(ax-78, ay-22, ax-32, ay-22, color=FIELD, sw=2))
    f.append(text(ax-86, ay-26, "уставка", size=12, bold=True, color=FIELD, anchor="end"))
    f.append(text(ax-86, ay-10, "(сигнал)", size=10, color=MUTED, anchor="end"))

    # заслінка
    sx, sy, sbw, sbh = 375, 120, 132, 92
    f.append(arrow(ax+42, ay, sx, sy+sbh/2, color=INK, sw=2))
    f.append(rect(sx, sy, sbw, sbh, fill="#eafaf0", stroke=FIELD, sw=2.2))
    f.append(mtext(sx+sbw/2, sy+36, ["заслінка", "струму"], size=13, bold=True))
    f.append(text(sx+sbw/2, sy+74, "(транзистор)", size=10, color=MUTED))

    busx = sx + sbw/2
    f.append(line(busx, sy+sbh, busx, 252, color=INK, sw=2.4))
    rsx, rsy, rsw, rsh = busx-24, 252, 48, 30
    f.append(rect(rsx, rsy, rsw, rsh, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(busx, rsy+20, "Rзм", size=12, bold=True))
    f.append(mtext(busx+62, rsy+12, ["давач", "струму"], size=10, color=MUTED, anchor="start"))
    f.append(line(busx, rsy+rsh, busx, 304, color=INK, sw=2.4))
    f.append(text(busx, 318, "до − клеми", size=10, color=MUTED))

    f.append(arrow(busx+0.1, sy+sbh+6, busx+0.1, 248, color=POS, sw=2.4))
    f.append(text(busx+96, (sy+sbh+252)/2, "I_петлі", size=12, bold=True, color=POS, anchor="start"))

    # зворотний зв'язок: відведення з вузла R_зм праворуч-вниз-навколо до «−» входу,
    # шлях обходить заслінку знизу, щоб не перетинати її рамку
    fbx = 690
    fby = rsy + rsh + 14            # нижче давача струму
    f.append(line(busx, rsy+rsh/2, fbx, rsy+rsh/2, color=POS, sw=1.8, dash="5,3"))
    f.append(line(fbx, rsy+rsh/2, fbx, fby, color=POS, sw=1.8, dash="5,3"))
    f.append(line(fbx, fby, ax-70, fby, color=POS, sw=1.8, dash="5,3"))
    f.append(line(ax-70, fby, ax-70, ay+22, color=POS, sw=1.8, dash="5,3"))
    f.append(arrow(ax-70, ay+22, ax-32, ay+22, color=POS, sw=1.8))
    f.append(text((fbx+ax)/2, fby+16, "вимір струму назад на вхід (−)", size=11, color=POS))

    f.append(text(W/2, H-12,
        "Більший струм → більша напруга на Rзм → віднімач прикриває заслінку. Рівновага: I_петлі = сигнал.",
        size=11, color=MUTED))

    render(os.path.join(IMG, 'feedback.svg'), W, H, *f)


if __name__ == '__main__':
    fig_loop()
    fig_scale()
    fig_why_current()
    fig_flapper()
    fig_psi_to_ma()
    fig_xmtr_blocks()
    fig_budget()
    fig_feedback()
    print("figs done")
