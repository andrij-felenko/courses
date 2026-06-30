# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def axes(ox, oy, w, h, xlab, ylab):
    """Осі координат із початком (ox,oy), ширина w праворуч, висота h угору."""
    out = []
    out.append(arrow(ox, oy, ox + w, oy, color=INK, sw=2))          # X →
    out.append(arrow(ox, oy, ox, oy - h, color=INK, sw=2))          # Y ↑
    out.append(text(ox + w - 4, oy + 22, xlab, size=14, color=MUTED, anchor="end"))
    out.append(text(ox + 8, oy - h + 6, ylab, size=14, color=MUTED, anchor="start"))
    return "".join(out)


# ── 1. Перетин кривої діода з навантажувальною прямою ───────────────────────
def fig_intersection():
    W, H = 720, 430
    ox, oy = 90, 360          # початок координат
    PW, PH = 540, 290         # робоче поле
    frags = [axes(ox, oy, PW + 30, PH + 30, "напруга на діоді  V", "струм  I")]

    # криву діода (експонента) малюємо як ламану
    Vth = 0.62                # умовний поріг
    pts = []
    for i in range(0, 121):
        v = i / 120.0 * 1.0   # 0..1 (умовні В)
        cur = 0.0 if v < Vth else (math.exp((v - Vth) * 14) - 1) * 0.06
        x = ox + v * PW
        y = oy - min(cur, 1.0) * PH
        pts.append((x, y))
    path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, POS))

    # навантажувальна пряма: від (Vsupply,0) до (0, Vsupply/R)
    # опорні точки в координатах поля: права на осі V при v=0.92, ліва на осі I при i=0.86
    xr, yr = ox + 0.92 * PW, oy                  # V_джерела, струм 0
    xl, yl = ox, oy - 0.86 * PH                  # струм V/R, напруга 0
    frags.append(line(xl, yl, xr, yr, color=NEG, sw=2.6))

    # опорні точки-мітки
    frags.append(circle(xr, yr, 4, fill=NEG, stroke=NEG, sw=1))
    frags.append(circle(xl, yl, 4, fill=NEG, stroke=NEG, sw=1))
    b1, _, _ = textbox(xr + 4, yr - 30, "V_джерела\n(струм 0)", size=12, pad=7,
                       fill="#eaf0fd", stroke=NEG, color=NEG)
    frags.append(b1)
    b2, _, _ = textbox(xl + 92, yl - 4, "V_джерела / R\n(напруга 0)", size=12, pad=7,
                       fill="#eaf0fd", stroke=NEG, color=NEG)
    frags.append(b2)

    # точка перетину Q — знайдемо чисельно
    qx = qy = None
    for i in range(1, len(pts)):
        cx, cy = pts[i]
        # навантажувальна пряма як функція: y = yr + (yl-yr)*(xr-x)/(xr-xl)
        ly = yr + (yl - yr) * (xr - cx) / (xr - xl)
        if cy <= ly:                  # крива піднялася вище прямої
            qx, qy = cx, (cy + ly) / 2
            break
    if qx is None:
        qx, qy = (xl + xr) / 2, (yl + yr) / 2
    frags.append(line(qx, oy, qx, qy, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(line(ox, qy, qx, qy, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(circle(qx, qy, 7, fill=FIELD, stroke=INK, sw=2))
    frags.append(text(qx + 16, qy - 12, "Q", size=18, color=INK, bold=True, anchor="start"))

    # підписи кривих
    frags.append(text(ox + PW * 0.86, oy - PH * 0.62, "крива діода", size=13, color=POS, bold=True, anchor="end"))
    frags.append(text(ox + PW * 0.30, oy - PH * 0.30, "навантажувальна пряма", size=13, color=NEG, bold=True, anchor="start"))

    render(os.path.join(IMG, "intersection.svg"), W, H, *frags)


# ── 2. Віяло вихідних кривих транзистора + пряма + Q посередині ─────────────
def fig_transistor_q():
    W, H = 720, 440
    ox, oy = 90, 370
    PW, PH = 540, 300
    frags = [axes(ox, oy, PW + 30, PH + 30, "напруга колектор–емітер  V_ке", "струм колектора  I_к")]

    # родина кривих: кожна — швидкий підйом біля нуля (область насичення),
    # потім майже горизонтальне плато на своїй висоті
    levels = [0.16, 0.31, 0.46, 0.61, 0.76]     # відносні висоти плато
    knee = 0.10                                  # коліно (Vke насичення)
    for k, lv in enumerate(levels):
        pts = []
        for i in range(0, 121):
            v = i / 120.0
            if v < knee:
                cur = lv * (v / knee)
            else:
                cur = lv * (1 + (v - knee) * 0.10)   # легкий нахил плато
            x = ox + v * PW
            y = oy - min(cur, 0.98) * PH
            pts.append((x, y))
        path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path, POS))
    frags.append(text(ox + PW * 0.97, oy - levels[-1] * PH - 10, "більший I_бази", size=12,
                      color=POS, anchor="end"))
    frags.append(text(ox + PW * 0.97, oy - levels[0] * PH - 8, "менший I_бази", size=12,
                      color=POS, anchor="end"))

    # навантажувальна пряма
    xr, yr = ox + 0.94 * PW, oy
    xl, yl = ox, oy - 0.90 * PH
    frags.append(line(xl, yl, xr, yr, color=NEG, sw=2.6))
    frags.append(text(ox + PW * 0.46, oy - PH * 0.30, "навантажувальна пряма", size=13,
                      color=NEG, bold=True, anchor="start"))

    # Q посередині прямої — на середній кривій (levels[2])
    lv = levels[2]
    qx = qy = None
    for i in range(0, 121):
        v = i / 120.0
        cur = lv * (1 + (v - knee) * 0.10) if v >= knee else lv * (v / knee)
        x = ox + v * PW
        y = oy - cur * PH
        ly = yr + (yl - yr) * (xr - x) / (xr - xl)
        if y <= ly:
            qx, qy = x, (y + ly) / 2
            break
    if qx is None:
        qx, qy = (xl + xr) / 2, (yl + yr) / 2
    frags.append(line(qx, oy, qx, qy, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(line(ox, qy, qx, qy, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(circle(qx, qy, 7, fill=FIELD, stroke=INK, sw=2))
    frags.append(text(qx + 15, qy - 11, "Q", size=18, color=INK, bold=True, anchor="start"))

    # стрілки розмаху вздовж прямої (вгору-вліво / вниз-вправо)
    dx, dy = (xr - xl), (yr - yl)
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    span = 70
    frags.append(arrow(qx, qy, qx - ux * span, qy - uy * span, color=FIELD, sw=2))
    frags.append(arrow(qx, qy, qx + ux * span, qy + uy * span, color=FIELD, sw=2))
    frags.append(text(qx - ux * span - 6, qy - uy * span - 8, "сигнал хитає Q", size=12,
                      color=FIELD, bold=True, anchor="end"))

    render(os.path.join(IMG, "transistor-q.svg"), W, H, *frags)


# ── 3. Дві прямі (DC полога, AC стрімкіша) через одну Q ──────────────────────
def fig_ac_dc():
    W, H = 720, 430
    ox, oy = 90, 360
    PW, PH = 540, 290
    frags = [axes(ox, oy, PW + 30, PH + 30, "напруга на приладі  V", "струм  I")]

    # точка спокою посередині поля
    qx, qy = ox + 0.50 * PW, oy - 0.45 * PH
    frags.append(circle(qx, qy, 7, fill=FIELD, stroke=INK, sw=2))
    frags.append(text(qx + 14, qy + 4, "Q", size=18, color=INK, bold=True, anchor="start"))
    frags.append(line(qx, oy, qx, qy, color=MUTED, sw=1.0, dash="4 4"))

    # DC — полога пряма через Q (малий нахил)
    slope_dc = 0.62          # умовний нахил (струм/напруга в частках поля)
    # пряма: y - qy = -slope*(x - qx) у координатах поля (струм вниз => мінус)
    def lineseg(slope, color, sw):
        # знайти точки перетину з межами поля
        xs = []
        # ліва межа x=ox
        ys_left = qy + slope * (qx - ox) * PH / PW
        # права x=ox+PW
        ys_right = qy - slope * (ox + PW - qx) * PH / PW
        # верх y=oy-PH, низ y=oy
        # обмежимо відрізок межами по y
        x1, y1 = ox, ys_left
        x2, y2 = ox + PW, ys_right
        # клампимо до нижньої осі (y=oy) і верху
        def clamp(x, y):
            if y > oy:
                x = qx + (oy - qy) * PW / (slope * PH) * (-1 if False else 1)
                # перерахунок: y=oy => x = qx + (qy-oy)/slope ... простіше параметрично
            return x, y
        return line(x1, max(oy - PH, min(oy, y1)), x2, max(oy - PH, min(oy, y2)), color=color, sw=sw)

    # надійніше: параметрично побудуємо відрізок прямої з даним нахилом, обрізаний полем
    def draw_line(slope, color, sw):
        # напрям: dx=+1 (вправо) => dy=+slope (струм спадає, тобто y зростає вниз)
        # рухаємось у обидва боки від Q, обрізаємо коли вийшли за поле
        def endpoint(direction):
            x, y = qx, qy
            step = 1.0
            while True:
                nx = x + direction * step
                ny = qy + slope * (nx - qx) * (PH / PW)
                if nx < ox or nx > ox + PW or ny > oy or ny < oy - PH:
                    return x, y
                x, y = nx, ny
        ax, ay = endpoint(-1)   # вгору-вліво
        bx, by = endpoint(+1)   # вниз-вправо
        return line(ax, ay, bx, by, color=color, sw=sw)

    frags.append(draw_line(slope_dc, NEG, 2.6))                # DC полога
    frags.append(draw_line(slope_dc * 2.1, "#8e44ad", 2.6))   # AC стрімкіша

    # підписи
    frags.append(text(ox + PW * 0.80, oy - PH * 0.07, "стала (DC):", size=13, color=NEG, bold=True, anchor="end"))
    frags.append(text(ox + PW * 0.80, oy - PH * 0.07 + 17, "нахил від R_к", size=12, color=NEG, anchor="end"))
    frags.append(text(qx - 14, qy - PH * 0.30, "для сигналу (AC):", size=13, color="#8e44ad", bold=True, anchor="end"))
    frags.append(text(qx - 14, qy - PH * 0.30 + 17, "R_к ∥ навантаження", size=12, color="#8e44ad", anchor="end"))

    render(os.path.join(IMG, "ac-dc.svg"), W, H, *frags)


# ── 4. Два погляди на коло: DC (навантаження відрізане) vs AC (паралельне) ──
def fig_ac_dc_circuit():
    W, H = 760, 380
    frags = []

    def panel(x0, title, ttl_color, cap_open):
        """Малює один півекран зі схемою. cap_open=True → конденсатор-розрив (DC)."""
        out = []
        cx = x0 + 175                       # центр панелі по горизонталі
        out.append(text(cx, 34, title, size=15, color=ttl_color, bold=True))

        # рейка живлення (верх) і земля (низ)
        rail_y, gnd_y = 70, 320
        rxL, rxR = x0 + 40, x0 + 310
        out.append(line(rxL, rail_y, rxR, rail_y, color=INK, sw=2))
        out.append(text(x0 + 36, rail_y - 8, "V_жив", size=12, color=MUTED, anchor="start"))
        # земля
        out.append(line(rxL, gnd_y, rxR, gnd_y, color=INK, sw=2))
        for i, dxg in enumerate((0, 7, 14)):
            out.append(line(x0 + 175 - 16 + dxg, gnd_y + 6 + i * 4,
                            x0 + 175 + 16 - dxg, gnd_y + 6 + i * 4, color=INK, sw=2))

        # R_к: від рейки вниз до вузла-колектора
        col_x = x0 + 110                    # вертикаль колекторного вузла
        node_y = 165                        # вузол «колектор»
        out.append(line(col_x, rail_y, col_x, 95, color=INK, sw=2))
        out.append(rect(col_x - 13, 95, 26, 46, fill=FILL, stroke=INK, sw=2, rx=3))
        out.append(text(col_x - 20, 118, "R_к", size=13, color=INK, bold=True, anchor="end"))
        out.append(line(col_x, 141, col_x, node_y, color=INK, sw=2))
        out.append(circle(col_x, node_y, 4, fill=INK, stroke=INK, sw=1))
        out.append(text(col_x - 8, node_y - 8, "колектор", size=11, color=MUTED, anchor="end"))

        # транзистор (спрощено: кружок із К/Е) від вузла вниз до землі
        tr_y = 235
        out.append(line(col_x, node_y, col_x, tr_y - 22, color=INK, sw=2))
        out.append(circle(col_x, tr_y, 22, fill=BG, stroke=INK, sw=2))
        out.append(text(col_x, tr_y + 5, "T", size=15, color=INK, bold=True))
        out.append(line(col_x, tr_y + 22, col_x, gnd_y, color=INK, sw=2))

        # горизонтальна гілка від вузла-колектора праворуч до конденсатора
        capx = x0 + 205
        out.append(line(col_x, node_y, capx - 14, node_y, color=INK, sw=2))

        # конденсатор C (дві пластини) — розрив (DC) чи замикання (AC) показуємо кольором
        cc = MUTED if cap_open else FIELD
        out.append(line(capx - 14, node_y - 16, capx - 14, node_y + 16, color=cc, sw=3))
        out.append(line(capx, node_y - 16, capx, node_y + 16, color=cc, sw=3))
        out.append(text(capx - 7, node_y - 24, "C", size=12, color=cc, bold=True))

        # навантаження R_навант: від правого виводу C вниз до землі
        ldx = x0 + 270
        out.append(line(capx, node_y, ldx, node_y, color=INK, sw=2))
        out.append(line(ldx, node_y, ldx, 178, color=INK, sw=2))
        out.append(rect(ldx - 13, 178, 26, 46, fill=FILL, stroke=INK, sw=2, rx=3))
        out.append(text(ldx + 20, 205, "R_навант", size=12, color=INK, anchor="start"))
        out.append(line(ldx, 224, ldx, gnd_y, color=INK, sw=2))

        # підпис-висновок під панеллю
        if cap_open:
            msg = "конденсатор — розрив\nR_навант відрізане\nопір кола = R_к"
        else:
            msg = "конденсатор — замикання\nR_навант ∥ R_к\nопір = R_к ∥ R_навант"
        b, bw, bh = textbox(cx, 352, msg, size=11, pad=7,
                            fill=("#f4f6f8" if cap_open else "#eafaf0"),
                            stroke=ttl_color, color=INK)
        out.append(b)

        # для DC: перекреслити «мертву» праву частину пунктиром-хрестиком на C
        if cap_open:
            out.append(line(capx - 17, node_y - 10, capx + 3, node_y + 10,
                            color=POS, sw=2))
            out.append(line(capx - 17, node_y + 10, capx + 3, node_y - 10,
                            color=POS, sw=2))
        return "".join(out)

    frags.append(panel(0, "Постійний струм (DC)", NEG, cap_open=True))
    # роздільник
    frags.append(line(W / 2, 50, W / 2, 330, color="#d0d4da", sw=1.5, dash="5 5"))
    frags.append(panel(W // 2, "Сигнал (AC)", "#8e44ad", cap_open=False))

    render(os.path.join(IMG, "ac-dc-circuit.svg"), W, H, *frags)


# ── 5. Родовід графіка: лампа → діод → транзистор, одне рівняння внизу ───────
def fig_lineage():
    W, H = 760, 430
    frags = []

    # три однакові мініатюри «крива + пряма + перетин» у ряд
    panels = [
        (60,  "Лампа", "1910–20-ті", "fan"),     # сімейство кривих
        (300, "Діод", "1950-ті", "one"),         # одна крива
        (540, "Транзистор", "1960-ті →", "fan"), # сімейство
    ]
    pw, ph = 170, 150          # поле мініатюри
    top = 78
    for px, name, era, kind in panels:
        ox, oy = px, top + ph
        # осі
        frags.append(arrow(ox, oy, ox + pw, oy, color=INK, sw=1.6))
        frags.append(arrow(ox, oy, ox, oy - ph, color=INK, sw=1.6))
        # криву(і) приладу
        if kind == "fan":
            levels = [0.22, 0.42, 0.62, 0.82]
            knee = 0.12
            for lv in levels:
                pts = []
                for i in range(0, 81):
                    v = i / 80.0
                    cur = lv * (v / knee) if v < knee else lv * (1 + (v - knee) * 0.08)
                    pts.append((ox + v * pw, oy - min(cur, 0.96) * ph))
                d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
                frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, POS))
        else:  # одна загнута крива діода
            Vth = 0.40
            pts = []
            for i in range(0, 81):
                v = i / 80.0
                cur = 0.0 if v < Vth else (math.exp((v - Vth) * 4.2) - 1) * 0.10
                pts.append((ox + v * pw, oy - min(cur, 0.96) * ph))
            d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
            frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (d, POS))

        # навантажувальна пряма (та сама на всіх панелях)
        xr, yr = ox + 0.90 * pw, oy
        xl, yl = ox, oy - 0.85 * ph
        frags.append(line(xl, yl, xr, yr, color=NEG, sw=2.0))

        # точка перетину Q (беремо середню висоту прямої)
        qx = ox + 0.46 * pw
        ly = yr + (yl - yr) * (xr - qx) / (xr - xl)
        frags.append(circle(qx, ly, 5, fill=FIELD, stroke=INK, sw=1.8))
        frags.append(text(qx + 11, ly - 7, "Q", size=13, color=INK, bold=True, anchor="start"))

        # підписи панелі
        frags.append(text(ox + pw / 2, top - 30, name, size=15, color=INK, bold=True))
        frags.append(text(ox + pw / 2, top - 13, era, size=12, color=MUTED))

    # стрілки «переходу» між панелями
    ay = top + ph * 0.42
    frags.append(arrow(60 + pw + 6, ay, 300 - 6, ay, color=MUTED, sw=2))
    frags.append(arrow(300 + pw + 6, ay, 540 - 6, ay, color=MUTED, sw=2))

    # спільне рівняння внизу — підкреслює, що міняються лише підписи осей
    by = top + ph + 60
    eqbox, ew, eh = textbox(W / 2, by,
                            "V_жив = I · R + V_приладу\nміняється лише V_приладу:  V_а  →  V діода  →  V_ке",
                            size=14, pad=12, fill="#eef7f0", stroke=FIELD, color=INK)
    frags.append(eqbox)

    render(os.path.join(IMG, "lineage.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_intersection()
    fig_transistor_q()
    fig_ac_dc()
    fig_ac_dc_circuit()
    fig_lineage()
    print("OK figures written")
