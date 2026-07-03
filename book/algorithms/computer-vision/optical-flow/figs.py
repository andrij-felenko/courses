# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── brightness-constancy: та сама яскравість переїхала на (u,v) ────────────────
# Ідея: піксель не зникає і не темніє — він лише переїжджає. Значення яскравості
# у точці (x,y) кадру t дорівнює значенню в (x+u, y+v) кадру t+Δt. На цьому стоїть
# уся рівняння оптичного потоку.
def fig_brightness_constancy():
    W, H = 820, 410
    p = []
    p.append(text(W/2, 30, "постійність яскравості: та сама пляма переїхала на (u, v)",
                  size=13, bold=True))

    # два кадри поряд
    fw, fh = 300, 240
    y0 = 74
    fx1 = 60
    fx2 = 460

    def frame(fx, label, bx, by, arrow_to=None):
        # рамка кадру (темне тло, як зображення)
        p.append(rect(fx, y0, fw, fh, fill="#0f172a", stroke=INK, sw=1.4, rx=8))
        p.append(text(fx + fw/2, y0 + fh + 22, label, size=11, color=MUTED, bold=True))
        # яскрава пляма
        p.append(circle(bx, by, 26, fill="#f8fafc", stroke="#f8fafc", sw=0))
        p.append(circle(bx, by, 26, fill="#fde68a", stroke="none", sw=0))
        p.append(text(bx, by + 5, "I", size=16, color="#0f172a", bold=True))
        return

    # кадр t: пляма ліворуч-угорі
    b1 = (fx1 + 95, y0 + 90)
    frame(fx1, "кадр у момент t", *b1)
    # кадр t+Δt: та сама пляма переїхала вправо-вниз
    b2 = (fx2 + 175, y0 + 150)
    frame(fx2, "кадр у момент t + Δt", *b2)

    # вектор зсуву (u,v) поверх другого кадру: звідки → куди
    ghost = (fx2 + 95, y0 + 90)   # де пляма БУЛА (привид)
    p.append(circle(ghost[0], ghost[1], 26, fill="none", stroke="#94a3b8", sw=1.6))
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3" '
             'stroke-dasharray="2 3" marker-end="url(#arrow)"/>' % (ghost[0], ghost[1], b2[0], b2[1], POS))
    p.append(text((ghost[0]+b2[0])/2 + 20, (ghost[1]+b2[1])/2 - 6, "(u, v)", size=13, color=POS, bold=True, anchor="start"))

    # підпис-рівність між кадрами
    p.append(fitbox(fx1, y0 + fh + 40, fw, 40,
                    "I(x, y, t) = I(x+u, y+v, t+Δt)",
                    size=13, fill=FILL, stroke=INK, sw=1.3, color=INK, bold=True))
    p.append(fitbox(fx2, y0 + fh + 40, fw, 40,
                    "яскравість та сама — змінилось лише МІСЦЕ",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.3, color=INK))

    render(os.path.join(OUT, "brightness-constancy.svg"), W, H, *p,
           title=None)


# ── aperture-problem: крізь дірку видно лише рух упоперек краю ─────────────────
# Ідея: одне рівняння, два невідомих. Дивлячись у мале вікно на довгий край,
# неможливо сказати, чи він поїхав уздовж себе — видно лише нормальну складову.
def fig_aperture():
    W, H = 820, 430
    p = []
    p.append(text(W/2, 28, "проблема апертури: у мале вікно видно лише рух упоперек краю",
                  size=13, bold=True))

    # ── ЛІВО: справжній рух краю по діагоналі ──
    cx, cy = 200, 230
    p.append(text(cx, 66, "справжній рух", size=11, bold=True, color=MUTED))
    # діагональний край (смуга) у двох положеннях
    def bar(ox, oy, col, sw, dash=None):
        # край під ~60°, довгий
        ang = math.radians(60)
        dx, dy = math.cos(ang), math.sin(ang)
        L = 150
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"%s/>'
                 % (ox - dx*L, oy - dy*L, ox + dx*L, oy + dy*L, col, sw, d))
    bar(cx - 30, cy, "#94a3b8", 10, dash="3 4")   # було
    bar(cx + 10, cy + 24, INK, 10)                # стало
    # справжній вектор руху (по діагоналі вправо-вниз)
    p.append(arrow(cx - 30, cy, cx + 10, cy + 24, color=POS, sw=3))
    p.append(text(cx + 40, cy + 20, "справжнє", size=10.5, color=POS, bold=True, anchor="start"))
    # мале вікно (апертура) в центрі
    p.append(circle(cx, cy, 46, fill="none", stroke=FIELD, sw=2.4))
    p.append(text(cx, cy - 60, "вікно", size=10, color=FIELD, bold=True))

    # ── ПРАВО: що ВИДНО крізь вікно ──
    rx, ry = 560, 230
    p.append(text(rx, 66, "що видно крізь вікно", size=11, bold=True, color=MUTED))
    # те саме вікно, лише сам край усередині
    p.append(circle(rx, ry, 46, fill="#0f172a", stroke=FIELD, sw=2.4))
    # шматок краю в двох положеннях (обрізаний вікном візуально)
    ang = math.radians(60)
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = math.cos(ang - math.pi/2), math.sin(ang - math.pi/2)  # нормаль
    for off, col, dash in [(-14, "#94a3b8", "3 4"), (14, "#f8fafc", None)]:
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        ox, oy = rx + nx*off*0.0 + (off*nx), ry + (off*ny)
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="8"%s '
                 'clip-path="url(#ap)"/>' % (ox - dx*70, oy - dy*70, ox + dx*70, oy + dy*70, col, d))
    # видно лише нормальну складову: короткий вектор упоперек краю
    p.append(arrow(rx - nx*14, ry - ny*14, rx + nx*14, ry + ny*14, color=FIELD, sw=3))
    p.append(text(rx + 58, ry - 4, "видно лише", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx + 58, ry + 11, "упоперек", size=10.5, color=FIELD, bold=True, anchor="start"))
    # привид «а насправді міг поїхати будь-куди вздовж краю»
    for k in (-1, 1):
        gx, gy = rx + dx*40*k, ry + dy*40*k
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" '
                 'stroke-dasharray="2 3" opacity="0.7"/>' % (rx, ry, gx, gy, "#f59e0b"))
    p.append(text(rx, ry + 78, "уздовж краю — невідомо", size=10, color="#f59e0b", bold=True))

    # нижній підпис: одне рівняння, два невідомих
    p.append(fitbox(W/2 - 260, 360, 520, 46,
                    "Iₓ·u + Iᵧ·v + Iₜ = 0   —   одне рівняння, два невідомих (u, v)",
                    size=12.5, fill=FILL, stroke=INK, sw=1.3, color=INK, bold=True))

    extra = '<defs><clipPath id="ap"><circle cx="%.1f" cy="%.1f" r="44"/></clipPath></defs>' % (rx, ry)
    render(os.path.join(OUT, "aperture.svg"), W, H, extra, *p, title=None)


# ── flow-field: поле векторів руху при польоті вперед (FOE) ────────────────────
# Ідея: оптичний потік — це ПОЛЕ векторів, по одному на місце. При русі камери
# вперед вектори розбігаються від однієї точки — фокуса розширення (FOE), а їхня
# довжина росте до країв. Так із самого потоку читається рух і глибина.
def fig_flow_field():
    W, H = 760, 470
    p = []
    p.append(text(W/2, 28, "оптичний потік — поле векторів; політ уперед → розбіжність від фокуса",
                  size=12.5, bold=True))

    # рамка «кадру»
    fx, fy, fw, fh = 70, 60, W - 140, H - 150
    p.append(rect(fx, fy, fw, fh, fill="#0f172a", stroke=INK, sw=1.4, rx=8))
    foe = (fx + fw*0.5, fy + fh*0.44)   # фокус розширення (напрям польоту)

    # сітка векторів, що розбігаються від FOE, довші до країв
    nx, ny = 7, 5
    for i in range(nx):
        for j in range(ny):
            x = fx + fw*(i + 0.5)/nx
            y = fy + fh*(j + 0.5)/ny
            dx, dy = x - foe[0], y - foe[1]
            r = math.hypot(dx, dy)
            if r < 18:
                continue
            ux, uy = dx / r, dy / r
            mag = 8 + 0.16 * r          # довжина росте з відстанню від FOE
            p.append(arrow(x, y, x + ux*mag, y + uy*mag, color="#38bdf8", sw=2.0))

    # сам фокус розширення
    p.append(circle(foe[0], foe[1], 6, fill="#f8fafc", stroke=POS, sw=2.4))
    p.append(text(foe[0], foe[1] - 14, "фокус розширення (куди летимо)",
                  size=10.5, color="#f8fafc", bold=True))

    # підпис під кадром
    p.append(fitbox(fx, fy + fh + 16, fw, 44,
                    "довжина вектора → як швидко місце віддаляється: близьке (край) біжить швидше за далеке (центр)",
                    size=10.5, fill=FILL, stroke=INK, sw=1.2, color=INK))

    render(os.path.join(OUT, "flow-field.svg"), W, H, *p, title=None)


# ── sparse-vs-dense: LK веде жменю кутів; HS/густий рахує кожен піксель ─────────
# Ідея: два табори. Розріджений (LK) рахує потік лише в надійних точках-кутах —
# дешево, для трекінгу. Густий (HS та наступники) дає вектор у КОЖНОМУ пікселі,
# гладко залатавши однорідні зони, — дорого, для сегментації руху.
def fig_sparse_vs_dense():
    W, H = 840, 400
    p = []

    fw, fh = 330, 260
    y0 = 74
    lx = 60
    rx = 450

    # спільна «сцена»: рухомий прямокутник (об'єкт) на тлі
    def scene(fx, title):
        p.append(rect(fx, y0, fw, fh, fill="#0f172a", stroke=INK, sw=1.4, rx=8))
        p.append(text(fx + fw/2, y0 - 12, title, size=12, bold=True))
        # об'єкт-прямокутник
        ox, oy, ow, oh = fx + 70, y0 + 70, 130, 110
        p.append(rect(ox, oy, ow, oh, fill="#1e293b", stroke="#475569", sw=1.4, rx=6))
        return ox, oy, ow, oh

    # ── ЛІВО: розріджений (LK) — вектори лише в кутах об'єкта ──
    ox, oy, ow, oh = scene(lx, "розріджений: тільки надійні точки (LK)")
    corners = [(ox, oy), (ox+ow, oy), (ox, oy+oh), (ox+ow, oy+oh),
               (ox+ow*0.5, oy), (ox+ow*0.5, oy+oh)]
    for (px, py) in corners:
        p.append(circle(px, py, 5, fill="#fde68a", stroke="#0f172a", sw=1.4))
        p.append(arrow(px, py, px + 22, py + 10, color=POS, sw=2.2))
    p.append(fitbox(lx, y0 + fh + 16, fw, 38,
                    "жменя векторів у кутах — дешево, для трекінгу",
                    size=10.5, fill="#fef3c7", stroke="#b06b00", sw=1.2, color=INK))

    # ── ПРАВО: густий (HS) — вектор у кожній клітинці ──
    ox, oy, ow, oh = scene(rx, "густий: вектор у кожному пікселі (HS)")
    gx0, gy0 = rx + 12, y0 + 12
    gnx, gny = 9, 7
    cw, ch = (fw - 24)/gnx, (fh - 24)/gny
    for i in range(gnx):
        for j in range(gny):
            cxp = gx0 + (i+0.5)*cw
            cyp = gy0 + (j+0.5)*ch
            inside = (ox <= cxp <= ox+ow) and (oy <= cyp <= oy+oh)
            col = "#38bdf8" if inside else "#334155"
            mag = 15 if inside else 5    # об'єкт рухається, тло майже стоїть
            p.append(arrow(cxp, cyp, cxp + mag, cyp + mag*0.4, color=col, sw=1.6))
    p.append(fitbox(rx, y0 + fh + 16, fw, 38,
                    "суцільне поле — дорого, для сегментації руху",
                    size=10.5, fill="#e0f2fe", stroke=NEG, sw=1.2, color=INK))

    render(os.path.join(OUT, "sparse-vs-dense.svg"), W, H, *p,
           title="Дві школи потоку: розріджений (LK) і густий (HS)")


# ── taylor-linearize: розклад Тейлора замінює криву дотичною площиною ──────────
# Ідея вставки: постійність яскравості дає I(x+u,y+v,t+Δt)=I(x,y,t) — невідомі
# сидять УСЕРЕДИНІ функції. На малому кроці криву яскравості замінюємо її дотичною
# (перший член Тейлора): приріст ≈ Iₓ·u + Iᵧ·v + Iₜ. Помилка — площа між кривою
# і дотичною, ~O(крок²): мала на кількох пікселях, велика на великому зсуві.
def fig_taylor_linearize():
    W, H = 780, 430
    p = []
    p.append(text(W/2, 28, "лінеаризація: на малому кроці криву яскравості замінюємо дотичною",
                  size=13, bold=True))

    # осі: горизонталь = зсув уздовж напряму руху, вертикаль = яскравість I
    ax, ay = 90, 340          # початок осей (нижній лівий кут)
    aw, ah = 610, 250
    top = ay - ah             # верх плоту
    p.append(line(ax, ay, ax + aw, ay, color=INK, sw=1.6))          # вісь зсуву
    p.append(line(ax, ay, ax, top, color=INK, sw=1.6))             # вісь I
    p.append(text(ax + aw - 6, ay + 22, "зсув уздовж руху →", size=10.5, color=MUTED, anchor="end"))
    p.append(text(ax - 12, top + 4, "I", size=12, color=MUTED, anchor="end", bold=True))

    # робоча точка: стоїмо на s=0. Крива яскравості — увігнута парабола (гладка,
    # з помірним нахилом), щоб дотична під нею відходила КВАДРАТИЧНО з кроком.
    x0 = ax + 60
    y0 = ay - 120             # екранний y точки «стоїмо тут»
    slope = -0.26            # нахил дотичної (екранний): яскравість помірно росте
    curv  = 0.00135         # кривина (парабола, увігнута вгору на екрані)
    def curveY(s):           # s — зсув у px; екранний y кривої
        return y0 + slope*s + curv*s*s
    def tanY(s):             # дотична в s=0
        return y0 + slope*s

    smax = 360
    pts = ["%.1f,%.1f" % (x0 + s, curveY(s)) for s in range(0, smax, 4)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), NEG))
    p.append(text(x0 + smax - 4, curveY(smax) - 12, "справжня I (крива)",
                  size=10.5, color=NEG, bold=True, anchor="end"))

    # дотична — від s=0 до s=smax (обидва кінці в межах плоту)
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.2" '
             'stroke-dasharray="6 4"/>' % (x0, tanY(0), x0 + smax, tanY(smax), POS))
    p.append(text(x0 + smax - 4, tanY(smax) + 16, "дотична (лінійне набл.)",
                  size=10.5, color=POS, bold=True, anchor="end"))

    # точка «стоїмо тут»
    p.append(circle(x0, y0, 5, fill="#f8fafc", stroke=INK, sw=1.8))
    p.append(text(x0 + 4, y0 - 12, "тут стоїмо (s = 0)", size=10, color=INK, bold=True, anchor="start"))

    # МАЛИЙ крок: крива й дотична майже збігаються — зелена зона
    s_small = 60
    p.append(line(x0 + s_small, ay, x0 + s_small, top + 10, color=FIELD, sw=1.0, dash="2 4"))
    p.append(circle(x0 + s_small, curveY(s_small), 4, fill=FIELD, stroke=FIELD, sw=0))
    p.append(circle(x0 + s_small, tanY(s_small), 4, fill="none", stroke=FIELD, sw=1.6))
    p.append(text(x0 + s_small, top + 4, "малий зсув: збіг", size=9.5, color=FIELD, bold=True))

    # ВЕЛИКИЙ крок: крива й дотична розбіглися — вертикальна щілина «помилка»
    s_big = 300
    yc, yt = curveY(s_big), tanY(s_big)
    p.append(line(x0 + s_big, ay, x0 + s_big, top + 10, color=POS, sw=1.0, dash="2 4"))
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.6"/>'
             % (x0 + s_big, yc, x0 + s_big, yt, POS))
    p.append(circle(x0 + s_big, yc, 4, fill=NEG, stroke=NEG, sw=0))
    p.append(circle(x0 + s_big, yt, 4, fill="none", stroke=POS, sw=1.6))
    p.append(text(x0 + s_big - 8, (yc + yt)/2 + 4, "велика помилка ~O(зсув²)",
                  size=9.5, color=POS, bold=True, anchor="end"))

    # нижній підпис — сама формула лінеаризації
    p.append(fitbox(ax, 386, aw, 34,
                    "I(x+u, y+v, t+Δt) ≈ I + Iₓ·u + Iᵧ·v + Iₜ   →   Iₓ·u + Iᵧ·v + Iₜ = 0",
                    size=12.5, fill=FILL, stroke=INK, sw=1.3, color=INK, bold=True))

    render(os.path.join(OUT, "taylor-linearize.svg"), W, H, *p, title=None)


# ── structure-tensor: власні числа тензора → надійність точки (кут/край/гладь) ─
# Ідея вставки: LK розв'язує AᵀA·[u v]ᵀ = −Aᵀb. Матриця AᵀA — структурний тензор;
# її два власні числа λ₁≥λ₂ кажуть, чи точка придатна. Обидва великі → кут (потік
# певний). Одне велике, друге ~0 → край (лишилась апертура). Обидва ~0 → гладь
# (нічого). Малюємо як еліпс невизначеності + три режими.
def fig_structure_tensor():
    W, H = 820, 430
    p = []
    p.append(text(W/2, 26, "структурний тензор AᵀA: власні числа λ₁, λ₂ — це надійність точки",
                  size=13, bold=True))

    boxw, boxh = 230, 250
    y0 = 66
    xs = [40, 295, 550]
    titles = ["кут: λ₁, λ₂ обидва великі",
              "край: λ₁ велике, λ₂ ≈ 0",
              "гладь: λ₁, λ₂ обидва ≈ 0"]
    # для кожного режиму: (візерунок латки, форма «еліпса певності»)
    for k, (bx, ttl) in enumerate(zip(xs, titles)):
        # рамка-латка (тло як зображення)
        p.append(rect(bx, y0, boxw, boxh, fill="#0f172a", stroke=INK, sw=1.4, rx=8))
        p.append(text(bx + boxw/2, y0 - 10, ttl, size=10.5, bold=True,
                      color=[FIELD, "#f59e0b", MUTED][k]))
        cx, cy = bx + boxw/2, y0 + 88

        if k == 0:      # КУТ: два краї, що сходяться → градієнт у двох напрямах
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#f8fafc" stroke-width="9"/>'
                     % (bx + 30, y0 + 40, bx + boxw - 30, y0 + 40))
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#f8fafc" stroke-width="9"/>'
                     % (bx + 60, y0 + 30, bx + 60, y0 + boxh - 70))
        elif k == 1:    # КРАЙ: один прямий край → градієнт лише впоперек
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#f8fafc" stroke-width="9"/>'
                     % (bx + 30, y0 + 30, bx + boxw - 20, y0 + boxh - 100))
        else:           # ГЛАДЬ: рівне тло, ледь помітний шум
            for (dx, dy) in [(40, 30), (150, 70), (90, 120), (180, 40), (60, 100)]:
                p.append(circle(bx + dx, y0 + dy, 2, fill="#1e293b", stroke="none", sw=0))

        # «еліпс певності»: осі ∝ √λ (велике λ → коротка вісь = певний напрям)
        ecx, ecy = bx + boxw/2, y0 + boxh - 66
        if k == 0:      # обидва λ великі → маленьке коло (певність в усі боки)
            p.append('<ellipse cx="%.1f" cy="%.1f" rx="16" ry="16" fill="none" stroke="%s" stroke-width="2.4"/>'
                     % (ecx, ecy, FIELD))
            p.append(text(ecx, ecy + 44, "потік певний", size=10, color=FIELD, bold=True))
        elif k == 1:    # λ₂≈0 → еліпс витягнутий уздовж краю (невизначеність уздовж)
            p.append('<ellipse cx="%.1f" cy="%.1f" rx="62" ry="15" fill="none" stroke="%s" '
                     'stroke-width="2.4" transform="rotate(35 %.1f %.1f)"/>' % (ecx, ecy, "#f59e0b", ecx, ecy))
            p.append(text(ecx, ecy + 48, "апертура лишилась", size=10, color="#f59e0b", bold=True))
        else:           # обидва ~0 → величезне розмите коло (нічого не визначено)
            p.append('<ellipse cx="%.1f" cy="%.1f" rx="70" ry="60" fill="none" stroke="%s" '
                     'stroke-width="2" stroke-dasharray="4 5"/>' % (ecx, ecy, MUTED))
            p.append(text(ecx, ecy + 52, "нічого не видно", size=10, color=MUTED, bold=True))

    # нижній підпис — критерій
    p.append(fitbox(40, 392, W - 80, 30,
                    "надійна точка ⟺ min(λ₁, λ₂) > поріг   (обидва власні числа великі — це і є кут)",
                    size=12, fill=FILL, stroke=INK, sw=1.3, color=INK, bold=True))

    render(os.path.join(OUT, "structure-tensor.svg"), W, H, *p, title=None)


# ── pyramid: згрубша-донизу — великий зсув на дрібній копії стає малим ─────────
# Ідея вставки: лінеаризація живе лише на малому кроці. Робимо стос дедалі
# дрібніших копій; на найменшій зсув 40px → 5px (уже «малий»). Рахуємо грубо,
# ×2, переносимо вгору як старт, уточнюємо поправкою. І так до повного розміру.
def fig_pyramid():
    W, H = 820, 470
    p = []
    p.append(text(W/2, 26, "піраміда згрубша-донизу: великий зсув на дрібній копії стає малим",
                  size=13, bold=True))

    # чотири рівні: рівень 3 (найдрібніший, угорі) … рівень 0 (повний, унизу)
    levels = [
        (3, 66,  "рівень 3", "зсув 40/8 = 5 px — малий"),
        (2, 104, "рівень 2", "уточнення поправкою"),
        (1, 156, "рівень 1", "уточнення поправкою"),
        (0, 228, "рівень 0 — повний кадр", "фінал: точний потік"),
    ]
    yc = 50
    centers = []
    for (lv, w, lab, note) in levels:
        h = w * 0.55
        x = W/2 - w/2 - 40           # лівіше центру — праворуч місце під підписи
        p.append(rect(x, yc, w, h, fill="#0f172a", stroke=INK, sw=1.4, rx=6))
        # маленький об'єкт у кадрі + його зсув (стрілка) — коротшає на дрібних рівнях
        ox, oy = x + w*0.28, yc + h*0.5
        p.append(circle(ox, oy, max(3, w*0.035), fill="#fde68a", stroke="#0f172a", sw=1.2))
        amag = 8 + (3 - lv) * 10      # стрілка довша на нижчих (більших) рівнях
        p.append(arrow(ox, oy, ox + amag, oy - amag*0.4, color=POS, sw=2.2))
        p.append(text(x - 10, yc + h/2 - 5, lab, size=10.5, color=INK, bold=True, anchor="end"))
        p.append(text(x - 10, yc + h/2 + 11, note, size=9.5, color=MUTED, anchor="end"))
        centers.append((x + w, yc + h, lv))
        yc += h + 14

    # стрілки «перенести грубий потік ×2 вниз як стартовий здогад» — праворуч від кадрів
    for i in range(len(centers) - 1):
        rxp, y, _ = centers[i]
        ax_ = rxp + 55
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.6" '
                 'marker-end="url(#arrow)"/>' % (ax_, y - 7, ax_, y + 7, FIELD))
        p.append(text(ax_ + 10, y + 4, "×2 → старт", size=9.5, color=FIELD, bold=True, anchor="start"))

    p.append(fitbox(60, 432, W - 120, 28,
                    "кожен рівень доводить те, що згрубша намацав дрібніший — зсув усюди лишається «малим»",
                    size=11, fill=FILL, stroke=INK, sw=1.2, color=INK))

    render(os.path.join(OUT, "pyramid.svg"), W, H, *p, title=None)


# ── two-schools: одне коріння 1981 → дві філософії → злиття ────────────────────
# Ідея вставки hist-two-schools: обидві школи виросли з проблеми апертури того
# самого 1981-го (LK — локальне вікно, HS — глобальна гладкість), розійшлися на
# два десятиліття й знову зійшлися в комбінованих методах 2000-х (Bruhn 2005).
def fig_two_schools():
    W, H = 860, 470
    p = []

    # спільне коріння вгорі: проблема апертури
    root_cx, root_cy = W/2, 66
    rb, rw, rh = textbox(root_cx, root_cy,
                         ["проблема апертури, 1981:", "одне рівняння в'язі — дві невідомі"],
                         size=12.5, bold=True, fill="#fff7ed", stroke=POS, sw=1.6)
    p.append(rb)

    # дві гілки — ліва (LK) і права (HS)
    lk_cx = 215
    hs_cx = 645
    y_branch = 205

    lb, lw, lh = textbox(lk_cx, y_branch,
                        ["Лукас — Канаде (LK)", "локальне вікно · найменші квадрати",
                         "розріджено, у надійних кутах"],
                        size=11.5, bold=False, fill="#e0f2fe", stroke=NEG, sw=1.5, min_w=310)
    hb, hw, hh = textbox(hs_cx, y_branch,
                        ["Горн — Шанк (HS)", "глобальна гладкість · варіаційно",
                         "густо, вектор у кожному пікселі"],
                        size=11.5, bold=False, fill="#eafaf0", stroke=FIELD, sw=1.5, min_w=310)

    # лінії від кореня до гілок
    p.append(line(root_cx-40, root_cy+rh/2, lk_cx, y_branch-lh/2, color=MUTED, sw=1.6))
    p.append(line(root_cx+40, root_cy+rh/2, hs_cx, y_branch-hh/2, color=MUTED, sw=1.6))
    p.append(lb)
    p.append(hb)

    # підписи «звідки взяли друге рівняння»
    p.append(text(lk_cx, y_branch+lh/2+22, "друге рівняння ← сусіди в латці",
                  size=10.5, color=NEG, italic=True))
    p.append(text(hs_cx, y_branch+hh/2+22, "друге рівняння ← штраф за негладкість",
                  size=10.5, color=FIELD, italic=True))

    # злиття внизу: комбіновані методи 2000-х
    merge_cx, merge_cy = W/2, 388
    mb, mw, mh = textbox(merge_cx, merge_cy,
                        ["злиття (2000-ні): дані як у LK + гладкість як у HS",
                         "Bruhn 2005: «Lucas/Kanade meets Horn/Schunck»",
                         "локальна надійність + густе поле в одному функціоналі"],
                        size=11.5, bold=True, fill="#f4f6f8", stroke=INK, sw=1.6, min_w=540)

    # лінії від гілок до злиття
    p.append(line(lk_cx, y_branch+lh/2+34, merge_cx-100, merge_cy-mh/2, color=NEG, sw=1.6, dash="4 3"))
    p.append(line(hs_cx, y_branch+hh/2+34, merge_cx+100, merge_cy-mh/2, color=FIELD, sw=1.6, dash="4 3"))
    p.append(mb)

    render(os.path.join(OUT, "two-schools.svg"), W, H, *p,
           title="Дві школи оптичного потоку: спільне коріння 1981 → розхід → злиття")


if __name__ == "__main__":
    fig_brightness_constancy()
    fig_aperture()
    fig_flow_field()
    fig_sparse_vs_dense()
    fig_taylor_linearize()
    fig_structure_tensor()
    fig_pyramid()
    fig_two_schools()
    print("OK: figures written to", OUT)
