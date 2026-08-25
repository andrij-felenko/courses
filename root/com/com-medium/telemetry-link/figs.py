# -*- coding: utf-8 -*-
"""Фігури теми «Канал земля-борт». Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: два напрями каналу — жирна телеметрія вниз, критичні команди вгору
# Ліворуч наземна станція, праворуч апарат у повітрі. Дві стрілки між ними:
# вниз (даунлінк) — товста, «багато даних»; вгору (аплінк) — тонка, «критично».
def fig_two_directions():
    W, H = 700, 340
    parts = []
    # земля (ліворуч) і апарат (праворуч)
    gx, gy = 120, 210
    ax, ay = 580, 120
    # наземна станція — прямокутник-ноутбук + щогла-антена
    parts.append(rect(gx - 46, gy - 6, 92, 46, fill="#eef2f7", stroke=INK, sw=1.6, rx=5))
    parts.append(text(gx, gy + 22, "земля", 12, INK, "middle", bold=True))
    parts.append(line(gx, gy - 6, gx, gy - 58, color=INK, sw=2.0))          # щогла
    parts.append(line(gx - 10, gy - 58, gx + 10, gy - 58, color=INK, sw=2.0))
    parts.append(text(gx, gy + 56, "наземна станція", 11, MUTED, "middle"))
    # ґрунт
    parts.append(line(40, gy + 40, 300, gy + 40, color=MUTED, sw=1.2, dash="4 4"))
    # апарат — простий квадрокоптер: тіло + два промені
    parts.append(circle(ax, ay, 12, fill="#fdecea", stroke=POS, sw=2.0))
    parts.append(line(ax - 26, ay - 14, ax + 26, ay + 14, color=INK, sw=2.0))
    parts.append(line(ax - 26, ay + 14, ax + 26, ay - 14, color=INK, sw=2.0))
    for dx, dy in [(-26, -14), (26, 14), (-26, 14), (26, -14)]:
        parts.append(circle(ax + dx, ay + dy, 5, fill="#fff", stroke=INK, sw=1.4))
    parts.append(text(ax, ay + 40, "апарат у повітрі", 11, MUTED, "middle"))
    # ── даунлінк: товста стрілка апарат → земля (трохи нижче), «телеметрія»
    dy_line = 168
    parts.append(('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                  'stroke-width="9" marker-end="url(#arrow)" opacity="0.85"/>'
                  % (ax - 34, ay + 30, gx + 60, dy_line, NEG)))
    parts.append(fitbox(288, dy_line - 4, 150, 34,
                        "телеметрія вниз:\nбагато даних",
                        size=11, fill="#eaf0fd", stroke=NEG, sw=1.2, color=INK))
    # ── аплінк: тонка стрілка земля → апарат (трохи вище), «команди»
    up_y = 96
    parts.append(('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                  'stroke-width="2.4" marker-end="url(#arrow)"/>'
                  % (gx + 46, up_y + 10, ax - 40, ay - 18, POS)))
    parts.append(fitbox(268, up_y - 16, 172, 32,
                        "команди вгору: рідко,\nале критично",
                        size=11, fill="#fdecea", stroke=POS, sw=1.2, color=INK))
    render(os.path.join(IMG, "two-directions.svg"), W, H, *parts,
           title="Канал земля-борт: два напрями, дві ролі")


# ── Фігура 2: бюджет лінії як вертикальний баланс потужності ──────────────────
# Рівні дБм зверху вниз: старт P_tx, +G_tx, −FSPL (велика сходинка), +G_rx → P_rx.
# Праворуч — лінія чутливості S; зазор між P_rx і S = запас (fade margin).
def fig_link_budget():
    W, H = 700, 400
    parts = []
    # осі: зліва шкала потужності (дБм), вертикальна
    x0 = 90
    top, bot = 60, 360
    parts.append(arrow(x0, bot, x0, top - 6, color=MUTED, sw=1.3))
    parts.append(text(x0 - 4, top - 14, "потужність, дБм", 11, MUTED, "middle"))
    # мапимо дБм → y. Візьмемо діапазон +25 .. -115 дБм.
    hi, lo = 25.0, -115.0
    def Y(dbm):
        return top + (hi - dbm) / (hi - lo) * (bot - top)
    # штрихи шкали
    for v in [20, 0, -40, -80, -110]:
        y = Y(v)
        parts.append(line(x0 - 5, y, x0, y, color=MUTED, sw=1.0))
        parts.append(text(x0 - 10, y + 4, "%d" % v, 10, MUTED, "end"))
    # послідовні рівні бюджету (числа з прикладу статті: 915 МГц, 3 км)
    p_tx = 20.0
    g_tx = p_tx + 2.0        # 22
    after_loss = g_tx - 101.2   # -79.2
    p_rx = after_loss + 2.0     # -77.2
    sens = -110.0
    # горизонтальні «полиці» рівнів + вертикальні кроки
    xa, xb = x0 + 30, x0 + 250
    def shelf(y, color, sw=2.4):
        parts.append(line(xa, y, xb, y, color=color, sw=sw))
    yy = [Y(p_tx), Y(g_tx), Y(after_loss), Y(p_rx)]
    shelf(yy[0], INK); shelf(yy[1], FIELD); shelf(yy[2], POS); shelf(yy[3], NEG)
    # вертикальні з'єднання-кроки зі знаком
    def step(x, y1, y2, label, color):
        parts.append(line(x, y1, x, y2, color=color, sw=1.6, dash="3 3"))
        ymid = (y1 + y2) / 2
        parts.append(text(x + 8, ymid + 4, label, 11, color, "start"))
    step(xb - 40, yy[0], yy[1], "+ G_tx (антена)", FIELD)
    step(xb - 40, yy[1], yy[2], "− FSPL (відстань)", POS)
    step(xb - 40, yy[2], yy[3], "+ G_rx (антена)", FIELD)
    # підписи полиць зліва
    parts.append(text(xa - 4, yy[0] - 6, "P_tx = +20", 10, INK, "end"))
    parts.append(text(xa - 4, yy[3] + 14, "P_rx = −77", 10, NEG, "end"))
    # лінія чутливості S праворуч
    ys = Y(sens)
    parts.append(line(xa, ys, W - 40, ys, color=MUTED, sw=1.6, dash="6 4"))
    parts.append(text(W - 42, ys - 6, "чутливість S = −110", 11, MUTED, "end"))
    # запас: подвійна стрілка від P_rx до S
    xm = xb + 90
    parts.append(('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                  'stroke-width="2.2" marker-end="url(#arrow)" marker-start="url(#arrow)"/>'
                  % (xm, Y(p_rx), xm, ys, FIELD)))
    parts.append(fitbox(xm + 12, (Y(p_rx) + ys) / 2 - 22, 148, 44,
                        "запас на завмирання\n≈ 33 дБ",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.3, color=INK))
    render(os.path.join(IMG, "link-budget.svg"), W, H, *parts,
           title="Бюджет лінії: баланс потужності від передавача до приймача")


# ── Фігура 3: запас на завмирання проти живого коливання сигналу ──────────────
# Пряма — чутливість. Хвиляста лінія — реальна прийнята потужність, що гуляє;
# один провал пірнає під чутливість (розрив лінка). Показано «середній рівень»
# і зазор до чутливості = запас.
def fig_fade_margin():
    W, H = 700, 340
    parts = []
    x0, y0, ww, hh = 70, 60, 560, 220
    parts.append(arrow(x0 - 6, y0 + hh, x0 + ww + 12, y0 + hh, color=MUTED, sw=1.3))
    parts.append(arrow(x0, y0 + hh + 6, x0, y0 - 8, color=MUTED, sw=1.3))
    parts.append(text(x0 + ww + 10, y0 + hh + 16, "час", 11, MUTED, "end"))
    parts.append(text(x0 - 2, y0 - 14, "прийнята потужність", 11, MUTED, "middle"))
    # рівень чутливості
    sy = y0 + hh - 40
    parts.append(line(x0, sy, x0 + ww, sy, color=INK, sw=2.0))
    parts.append(text(x0 + ww - 2, sy + 16, "чутливість приймача", 11, INK, "end"))
    # середній рівень сигналу
    mean_y = y0 + 70
    parts.append(line(x0, mean_y, x0 + ww, mean_y, color=MUTED, sw=1.0, dash="5 5"))
    parts.append(text(x0 + 4, mean_y - 6, "середній рівень", 10, MUTED, "start"))
    # хвиляста лінія прийнятого сигналу (сума кількох синусоїд + один глибокий провал)
    pts = []
    N = 280
    for i in range(N + 1):
        t = i / N
        x = x0 + t * ww
        # базові коливання
        f = (math.sin(t * 13) * 16 + math.sin(t * 27 + 1) * 10 + math.sin(t * 41) * 6)
        y = mean_y - f
        # один глибокий провал біля t≈0.62 — пірнає під чутливість
        dip = math.exp(-((t - 0.62) ** 2) / 0.0012) * 120
        y = y + dip
        pts.append((x, y))
    frag = ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), POS))
    parts.append(frag)
    # позначка місця розриву
    parts.append(circle(x0 + 0.62 * ww, sy + 26, 4, fill=POS, stroke=INK, sw=1))
    parts.append(fitbox(x0 + 0.62 * ww - 68, sy + 34, 138, 30,
                        "провал < чутливості:\nлінк рветься",
                        size=10, fill="#fdecea", stroke=POS, sw=1.2, color=INK))
    # подвійна стрілка запасу зліва
    xm = x0 + 40
    parts.append(('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                  'stroke-width="2.0" marker-end="url(#arrow)" marker-start="url(#arrow)"/>'
                  % (xm, mean_y, xm, sy, FIELD)))
    parts.append(text(xm + 8, (mean_y + sy) / 2 + 4, "запас", 11, FIELD, "start", bold=True))
    render(os.path.join(IMG, "fade-margin.svg"), W, H, *parts,
           title="Запас на завмирання: страховка від провалів живого ефіру")


# ── Фігура 4: FDD проти TDD ───────────────────────────────────────────────────
# Угорі — частотний дуплекс: дві смуги (вгору/вниз) на різних частотах, обидві
# весь час активні. Унизу — часовий: одна частота, кванти часу чергуються U/D.
def fig_duplex():
    W, H = 700, 360
    parts = []
    # ── FDD (верхня половина): осі частота(верт) × час(гориз)
    fx, fy, fw, fh = 90, 60, 520, 100
    parts.append(text(fx - 10, fy - 14, "частотний дуплекс (FDD): різні частоти, водночас",
                      12, INK, "start", bold=True))
    parts.append(arrow(fx - 6, fy + fh, fx + fw + 10, fy + fh, color=MUTED, sw=1.2))
    parts.append(arrow(fx, fy + fh + 4, fx, fy - 6, color=MUTED, sw=1.2))
    parts.append(text(fx + fw + 8, fy + fh + 14, "час", 10, MUTED, "end"))
    parts.append(text(fx - 4, fy - 2, "частота", 10, MUTED, "middle"))
    # дві суцільні смуги на весь час
    parts.append(rect(fx + 6, fy + 10, fw - 16, 26, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    parts.append(text(fx + fw / 2, fy + 27, "вниз (даунлінк) — f₁", 11, NEG, "middle"))
    parts.append(rect(fx + 6, fy + 62, fw - 16, 26, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    parts.append(text(fx + fw / 2, fy + 79, "вгору (аплінк) — f₂", 11, POS, "middle"))
    # ── TDD (нижня половина)
    tx, ty, tw, th = 90, 230, 520, 90
    parts.append(text(tx - 10, ty - 14, "часовий дуплекс (TDD): одна частота, по черзі в часі",
                      12, INK, "start", bold=True))
    parts.append(arrow(tx - 6, ty + th, tx + tw + 10, ty + th, color=MUTED, sw=1.2))
    parts.append(arrow(tx, ty + th + 4, tx, ty - 6, color=MUTED, sw=1.2))
    parts.append(text(tx + tw + 8, ty + th + 14, "час", 10, MUTED, "end"))
    parts.append(text(tx - 4, ty - 2, "частота", 10, MUTED, "middle"))
    # одна смуга частоти, поділена на кванти D/U/D/U...
    slot_y, slot_h = ty + 30, 30
    n = 8
    sw_ = (tw - 16) / n
    for i in range(n):
        x = tx + 6 + i * sw_
        down = (i % 2 == 0)
        col = NEG if down else POS
        fillc = "#eaf0fd" if down else "#fdecea"
        parts.append(rect(x, slot_y, sw_ - 4, slot_h, fill=fillc, stroke=col, sw=1.5, rx=3))
        parts.append(text(x + sw_ / 2 - 2, slot_y + 20, "D" if down else "U", 12, col, "middle", bold=True))
    parts.append(text(tx + tw / 2, ty + th + 30, "D — вниз, U — вгору; та сама частота, кванти чергуються",
                      10, MUTED, "middle"))
    render(os.path.join(IMG, "duplex.svg"), W, H, *parts,
           title="Двосторонність: частотний і часовий дуплекс")


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури вставки comp-rf-frontend.md — радіочастотний тракт (RF frontend)
# ══════════════════════════════════════════════════════════════════════════════

# ── Фігура A: увесь тракт — два ланцюги навколо антени через T/R-перемикач ─────
def fig_frontend_chain():
    W, H = 720, 420
    parts = []
    # спільна антена праворуч
    axr = 640
    ax_top = 150
    parts.append(line(axr, ax_top, axr, ax_top - 46, color=INK, sw=2.2))       # щогла
    parts.append(line(axr - 16, ax_top - 46, axr + 16, ax_top - 46, color=INK, sw=2.2))
    parts.append(line(axr - 16, ax_top - 46, axr - 6, ax_top - 62, color=INK, sw=2.0))
    parts.append(line(axr + 16, ax_top - 46, axr + 6, ax_top - 62, color=INK, sw=2.0))
    parts.append(text(axr, ax_top - 70, "антена", 11, MUTED, "middle"))

    # T/R-перемикач — ромб-вузол трохи лівіше антени
    trx, trY = 540, ax_top
    parts.append(('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f L %.0f %.0f Z" '
                  'fill="#fff7e6" stroke="%s" stroke-width="1.8"/>'
                  % (trx, trY - 26, trx + 30, trY, trx, trY + 26, trx - 30, trY, INK)))
    parts.append(text(trx, trY - 4, "T/R", 12, INK, "middle", bold=True))
    parts.append(text(trx, trY + 12, "switch", 9, MUTED, "middle"))
    parts.append(line(trx + 30, trY, axr, ax_top, color=INK, sw=2.0))          # до антени

    def blk(x, y, w, h, label, sub, col, fillc):
        parts.append(rect(x, y, w, h, fill=fillc, stroke=col, sw=1.8, rx=6))
        parts.append(text(x + w / 2, y + h / 2 - 2, label, 12, col, "middle", bold=True))
        if sub:
            parts.append(text(x + w / 2, y + h / 2 + 14, sub, 9, MUTED, "middle"))

    # ── Верхній ланцюг: ПЕРЕДАЧА (зліва направо в перемикач) ──
    ty = 78
    parts.append(text(70, ty - 14, "ПЕРЕДАЧА", 12, POS, "start", bold=True))
    blk(70, ty, 92, 44, "синт.", "частота", NEG, "#eaf0fd")
    blk(190, ty, 92, 44, "модул.", "дані→несуча", INK, FILL)
    blk(310, ty, 92, 44, "драйвер", "розгін", POS, "#fdecea")
    blk(430, ty, 92, 44, "PA", "потужність", POS, "#fdecea")
    # стрілки ланцюга передачі
    for x in (162, 282, 402):
        parts.append(arrow(x, ty + 22, x + 28, ty + 22, color=MUTED, sw=1.6))
    # PA → узгодження → перемикач (вгору)
    parts.append(arrow(522, ty + 22, trx - 8, ty + 22, color=POS, sw=1.8))
    parts.append(line(trx - 8, ty + 22, trx - 8, trY - 22, color=POS, sw=1.8))
    parts.append(fitbox(430, ty + 52, 92, 24, "узгодження",
                        size=9, fill="#eafaf1", stroke=FIELD, sw=1.1, color=INK))

    # ── Нижній ланцюг: ПРИЙОМ (з перемикача наліво) ──
    ry = 250
    parts.append(text(70, ry - 14, "ПРИЙОМ", 12, FIELD, "start", bold=True))
    blk(430, ry, 92, 44, "LNA", "тихий вхід", FIELD, "#eafaf1")
    blk(310, ry, 92, 44, "змішувач", "→ IF", INK, FILL)
    blk(190, ry, 92, 44, "IF-фільтр", "селект.", NEG, "#eaf0fd")
    blk(70, ry, 92, 44, "IF-підс.", "+детект.", INK, FILL)
    # перемикач → LNA (вниз)
    parts.append(line(trx - 8, trY + 22, trx - 8, ry + 22, color=FIELD, sw=1.8))
    parts.append(arrow(trx - 8, ry + 22, 522, ry + 22, color=FIELD, sw=1.8))
    # ланцюг прийому справа наліво
    for x in (430, 310, 190):
        parts.append(arrow(x, ry + 22, x - 28, ry + 22, color=MUTED, sw=1.6))
    # гетеродин/синтезатор знизу до змішувача
    parts.append(rect(310, ry + 78, 92, 40, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
    parts.append(text(356, ry + 94, "гетеродин", 11, NEG, "middle", bold=True))
    parts.append(text(356, ry + 109, "= синтезатор", 9, MUTED, "middle"))
    parts.append(arrow(356, ry + 78, 356, ry + 44, color=NEG, sw=1.6))
    render(os.path.join(IMG, "frontend-chain.svg"), W, H, *parts,
           title="Радіочастотний тракт: передача й прийом навколо однієї антени")


# ── Фігура B: T/R-перемикач у двох станах ─────────────────────────────────────
def fig_tr_switch():
    W, H = 700, 320
    parts = []

    def panel(cx, tx_mode, caption):
        # антена вгорі
        ay = 70
        parts.append(line(cx, ay, cx, ay - 34, color=INK, sw=2.0))
        parts.append(line(cx - 12, ay - 34, cx + 12, ay - 34, color=INK, sw=2.0))
        parts.append(text(cx, ay - 44, "антена", 10, MUTED, "middle"))
        # вузол перемикача
        ny = 130
        parts.append(circle(cx, ny, 8, fill="#fff7e6", stroke=INK, sw=1.8))
        parts.append(line(cx, ay, cx, ny - 8, color=INK, sw=2.0))
        # два плеча: PA (ліворуч-низ) і LNA (праворуч-низ)
        pax, pay = cx - 90, 240
        lax, lay = cx + 90, 240
        parts.append(rect(pax - 34, pay - 22, 68, 40, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
        parts.append(text(pax, pay, "PA", 13, POS, "middle", bold=True))
        parts.append(text(pax, pay - 30, "передавач", 9, MUTED, "middle"))
        parts.append(rect(lax - 34, lay - 22, 68, 40, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=6))
        parts.append(text(lax, lay, "LNA", 12, FIELD, "middle", bold=True))
        parts.append(text(lax, lay - 30, "приймач", 9, MUTED, "middle"))
        # активне плече — суцільна лінія; неактивне — пунктир + «X»
        if tx_mode:
            parts.append(line(cx, ny, pax, pay - 22, color=POS, sw=2.4))          # антена↔PA
            parts.append(line(cx, ny, lax, lay - 22, color=MUTED, sw=1.4, dash="4 4"))
            # хрестик на приймальному плечі
            mx, my = (cx + lax) / 2, (ny + lay - 22) / 2
            parts.append(line(mx - 7, my - 7, mx + 7, my + 7, color=POS, sw=2.2))
            parts.append(line(mx - 7, my + 7, mx + 7, my - 7, color=POS, sw=2.2))
            parts.append(text(mx + 26, my, "відрізано", 9, POS, "middle"))
        else:
            parts.append(line(cx, ny, lax, lay - 22, color=FIELD, sw=2.4))         # антена↔LNA
            parts.append(line(cx, ny, pax, pay - 22, color=MUTED, sw=1.4, dash="4 4"))
            mx, my = (cx + pax) / 2, (ny + pay - 22) / 2
            parts.append(text(mx - 26, my, "осторонь", 9, MUTED, "middle"))
        parts.append(text(cx, 292, caption, 11, INK, "middle", bold=True))

    panel(190, True,  "передача: антена → PA")
    panel(510, False, "прийом: антена → LNA")
    # роздільник
    parts.append(line(350, 55, 350, 300, color=MUTED, sw=1.0, dash="3 5"))
    render(os.path.join(IMG, "tr-switch.svg"), W, H, *parts,
           title="T/R-перемикач: антена належить одному тракту за раз")


# ── Фігура C: каскадна формула Фрііса — внесок кожного каскаду в шум ───────────
def fig_friis_cascade():
    W, H = 720, 340
    parts = []
    # три каскади в ряд
    y = 150
    boxes = [
        (110, "LNA",       "F₁, G₁", FIELD, "#eafaf1"),
        (330, "змішувач",  "F₂, G₂", INK,   FILL),
        (550, "IF-підс.",  "F₃",     NEG,   "#eaf0fd"),
    ]
    for x, name, fg, col, fillc in boxes:
        parts.append(rect(x - 60, y - 26, 120, 52, fill=fillc, stroke=col, sw=1.9, rx=7))
        parts.append(text(x, y - 4, name, 13, col, "middle", bold=True))
        parts.append(text(x, y + 14, fg, 11, MUTED, "middle"))
    # сигнальні стрілки
    parts.append(arrow(40, y, 50, y, color=MUTED, sw=1.6))
    parts.append(arrow(170, y, 270, y, color=MUTED, sw=1.8))
    parts.append(arrow(390, y, 490, y, color=MUTED, sw=1.8))
    parts.append(arrow(610, y, 680, y, color=MUTED, sw=1.8))
    parts.append(text(40, y - 12, "антена", 9, MUTED, "middle"))
    # внески в шум — над кожним каскадом
    parts.append(fitbox(50, 55, 120, 42, "внесок:\nF₁  (повністю)",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.3, color=INK, bold=True))
    parts.append(fitbox(270, 55, 120, 42, "внесок:\n(F₂−1) / G₁",
                        size=11, fill="#eef2f7", stroke=INK, sw=1.2, color=INK))
    parts.append(fitbox(490, 55, 120, 42, "внесок:\n(F₃−1) / (G₁·G₂)",
                        size=10, fill="#eef2f7", stroke=INK, sw=1.2, color=INK))
    # стрілки вниз від внеску до каскаду
    for x in (110, 330, 550):
        parts.append(line(x, 97, x, y - 26, color=MUTED, sw=1.0, dash="3 3"))
    # підсумкова формула знизу
    parts.append(fitbox(110, 250, 500, 40,
                        "F_заг = F₁ + (F₂−1)/G₁ + (F₃−1)/(G₁·G₂) + …   →   якщо G₁ велике: F_заг ≈ F₁",
                        size=12, fill="#ffffff", stroke=FIELD, sw=1.6, color=INK, bold=True))
    parts.append(text(360, 312, "перший каскад входить без дільника — тому LNA задає чутливість усього приймача",
                      10, MUTED, "middle"))
    render(os.path.join(IMG, "friis-cascade.svg"), W, H, *parts,
           title="Каскадна формула Фрііса: шум приймача задає перший каскад")


fig_two_directions()
fig_link_budget()
fig_fade_margin()
fig_duplex()
fig_frontend_chain()
fig_tr_switch()
fig_friis_cascade()
print("Done. SVG in", IMG)
