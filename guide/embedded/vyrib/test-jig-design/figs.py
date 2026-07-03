# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

BRASS = "#b07a35"
COPPER = "#c9782f"
COPPER_FILL = "#f6d9b8"


# ── Фігура 1: анатомія pogo-піна — плунжер, циліндр, пружина ──────────────────
def fig_pogo_anatomy():
    W, H = 720, 380
    frags = []
    frags.append(text(W / 2, 30, "Чому голка тримає контакт: усередині — пружина",
                      size=15, bold=True))

    # ── ЛІВОРУЧ: розріз одного піна ──
    cx = 175
    bx = cx - 16          # ліва межа циліндра
    bw = 32               # ширина циліндра
    btop, bbot = 90, 300  # циліндр
    # циліндр (barrel)
    frags.append(rect(bx, btop, bw, bbot - btop, fill="#e9edf2", stroke=INK, sw=1.6, rx=3))
    frags.append(text(bx - 12, (btop + bbot) / 2, "циліндр", size=11, color=MUTED, anchor="end"))
    # пружина всередині — зиґзаґ
    sp_top, sp_bot = 150, 250
    zig = []
    n = 7
    for i in range(n + 1):
        yy = sp_top + (sp_bot - sp_top) * i / n
        xx = cx + (10 if i % 2 else -10)
        zig.append((xx, yy))
    for i in range(len(zig) - 1):
        (x1, y1), (x2, y2) = zig[i], zig[i + 1]
        frags.append(line(x1, y1, x2, y2, color=NEG, sw=2))
    frags.append(text(cx + 24, (sp_top + sp_bot) / 2, "пружина", size=11, color=NEG, anchor="start"))
    # плунжер (plunger) — стрижень, що виходить угору
    pl_w = 12
    frags.append(rect(cx - pl_w / 2, btop - 34, pl_w, 34 + 60, fill="#cfd6de", stroke=INK, sw=1.4, rx=2))
    frags.append(text(cx + 20, btop - 20, "плунжер\n(рухома голка)", size=11, color=INK, anchor="start"))
    # вістря плунжера (корона)
    tipy = btop - 34
    frags.append(line(cx - 6, tipy, cx, tipy - 10, color=INK, sw=2))
    frags.append(line(cx + 6, tipy, cx, tipy - 10, color=INK, sw=2))
    frags.append(line(cx, tipy, cx, tipy - 6, color=INK, sw=2))
    # хвостик для припою внизу
    frags.append(line(cx, bbot, cx, bbot + 26, color=BRASS, sw=3))
    frags.append(text(cx, bbot + 42, "хвіст → до вимірювача", size=10, color=MUTED))
    # стрілка сили притиску
    frags.append(arrow(cx + 46, tipy - 26, cx + 46, tipy + 4, color=POS, sw=2))
    frags.append(text(cx + 52, tipy - 14, "сила\nпритиску", size=10, color=POS, anchor="start"))

    # ── ПРАВОРУЧ: пружина вирівнює різну висоту точок ──
    ox = 470
    frags.append(text(ox + 60, 74, "Пружина «вибирає» різну висоту", size=12, color=FIELD, bold=True))
    # плата з двома точками на різній висоті
    board_y = 300
    frags.append(rect(ox - 40, board_y, 220, 16, fill="#eaf4ec", stroke=FIELD, sw=1.6))
    frags.append(text(ox + 70, board_y + 30, "плата (точки не ідеально рівні)", size=10, color=MUTED))
    # дві точки: ліва нижча, права вища (нерівність перебільшена)
    pads = [(ox + 10, board_y, 0), (ox + 130, board_y - 10, 10)]
    plate_y = 120   # спільна плита, до якої кріплять піни
    frags.append(rect(ox - 30, plate_y - 22, 240, 22, fill="#e9edf2", stroke=INK, sw=1.4))
    frags.append(text(ox + 90, plate_y - 30, "спільна плита джига (одна висота)", size=10, color=MUTED))
    for (padx, pady, extra) in pads:
        # площадка
        frags.append(rect(padx - 12, pady, 24, 6, fill=COPPER_FILL, stroke=COPPER, sw=1.4))
        # циліндр від плити
        frags.append(rect(padx - 7, plate_y, 14, 90, fill="#e9edf2", stroke=INK, sw=1.2, rx=2))
        # пружина стиснена по-різному: коротша зверху точка → менше стиснення
        s0, s1 = plate_y + 90, pady - 4
        m = 5
        for k in range(m):
            yy = s0 + (s1 - s0) * k / (m - 1)
            xx = padx + (5 if k % 2 else -5)
            if k < m - 1:
                yy2 = s0 + (s1 - s0) * (k + 1) / (m - 1)
                xx2 = padx + (5 if (k + 1) % 2 else -5)
                frags.append(line(xx, yy, xx2, yy2, color=NEG, sw=1.6))
        # плунжер до площадки
        frags.append(line(padx, pady - 4, padx, pady, color=INK, sw=3))
    frags.append(text(ox + 70, board_y + 48,
                      "нижча точка — плунжер вийшов далі; вища — глибше в циліндр. Контакт скрізь.",
                      size=10, color=FIELD))

    # роздільник
    frags.append(line(W / 2 + 40, 60, W / 2 + 40, 330, color=MUTED, sw=1, dash="5,5"))
    render(os.path.join(OUT, 'pogo-anatomy.svg'), W, H, *frags)


# ── Фігура 2: джиг як машина — притиск, голки на точки, контролер flash+тест ──
def fig_jig_machine():
    W, H = 780, 430
    frags = []
    frags.append(text(W / 2, 30, "Тест-джиг: один притиск робить усе — живить, шиє, міряє, судить",
                      size=14, bold=True))

    # плата (DUT) з точками знизу
    bx, by, bw, bh = 120, 210, 300, 26
    frags.append(rect(bx, by, bw, bh, fill="#eaf4ec", stroke=FIELD, sw=2))
    frags.append(text(bx + bw / 2, by + 17, "плата, яку перевіряємо (DUT)", size=12, color=FIELD, bold=True))
    # напрямні штирі (tooling pins) по кутах — фіксують плату
    for hx in (bx + 14, bx + bw - 14):
        frags.append(circle(hx, by + bh / 2, 4, fill=BG, stroke=INK, sw=1.6))
    frags.append(text(bx - 6, by + bh / 2, "напрямні\nштирі", size=9, color=MUTED, anchor="end"))

    # притискна кришка згори
    frags.append(rect(bx - 10, by - 46, bw + 20, 26, fill="#e9edf2", stroke=INK, sw=1.6))
    frags.append(text(bx + bw / 2, by - 30, "притискна кришка (притягує плату до голок)", size=10, color=MUTED))
    frags.append(arrow(bx + bw / 2, by - 20, bx + bw / 2, by - 2, color=POS, sw=2))

    # тестові точки під платою + pogo-голки, що тягнуться від плити-основи вниз
    base_y = 360
    frags.append(rect(bx - 10, base_y, bw + 20, 22, fill="#e9edf2", stroke=INK, sw=1.6))
    frags.append(text(bx + bw / 2, base_y + 15, "основа джига (тримає всі голки)", size=10, color=MUTED))
    probe_x = [bx + 40, bx + 100, bx + 160, bx + 220, bx + 262]
    labels = ["VCC", "GND", "SWDIO", "SWCLK", "OUT"]
    for px_, lab in zip(probe_x, labels):
        # площадка знизу плати
        frags.append(rect(px_ - 8, by + bh, 16, 5, fill=COPPER_FILL, stroke=COPPER, sw=1.3))
        # голка від основи до площадки
        frags.append(line(px_, base_y, px_, by + bh + 5, color=BRASS, sw=2.4))
        # вістря
        frags.append(circle(px_, by + bh + 5, 2.4, fill=INK, stroke=INK))
        frags.append(text(px_, base_y - 6, lab, size=9, color=INK))

    # контролер праворуч, з'єднаний з основою
    cxb, cyb, cwb, chb = 500, 120, 240, 250
    frags.append(rect(cxb, cyb, cwb, chb, fill="#fbfbfb", stroke=INK, sw=1.8))
    frags.append(text(cxb + cwb / 2, cyb + 22, "контролер джига", size=13, bold=True))
    steps = [
        ("1. подати живлення", NEG),
        ("2. залити прошивку (SWD)", BRASS),
        ("3. виміряти напруги в точках", FIELD),
        ("4. звірити з очікуваним", INK),
        ("5. вирок: ПРОЙШЛА / БРАК", POS),
    ]
    sy = cyb + 44
    for lab, col in steps:
        frags.append(fitbox(cxb + 12, sy, cwb - 24, 30, lab, size=11, color=col,
                            fill="#fbfbfb", stroke=col, sw=1.3))
        sy += 38
    # зв'язок основа → контролер
    frags.append(line(bx + bw + 10, base_y + 8, cxb, cyb + chb - 30, color=MUTED, sw=1.6, dash="5,4"))
    frags.append(line(bx + bw + 10, by + bh / 2, cxb, cyb + chb - 70, color=MUTED, sw=1.2, dash="3,3"))

    render(os.path.join(OUT, 'jig-machine.svg'), W, H, *frags)


# ── Фігура 3: доступ до тест-точки — придатна vs схована ──────────────────────
def fig_testpoint_access():
    W, H = 760, 350
    frags = []
    frags.append(text(W / 2, 30, "Голка сідає лише на відкриту мідь потрібного розміру",
                      size=15, bold=True))

    board_y = 250

    # ── ЛІВОРУЧ (добре): відкрита кругла площадка ──
    cxL = 200
    frags.append(text(cxL, 70, "Придатна тест-точка", size=13, color=FIELD, bold=True))
    frags.append(rect(cxL - 130, board_y, 260, 60, fill="#eaf4ec", stroke=FIELD, sw=1.6))
    padx, pady = cxL, board_y + 24
    # відкрита мідна пляма
    frags.append(circle(padx, pady, 15, fill=COPPER_FILL, stroke=COPPER, sw=2))
    frags.append(circle(padx, pady, 15, fill="none", stroke=FIELD, sw=1))
    frags.append(text(padx, pady + 40, "гола мідь, ≈ 1 мм, нічого зверху", size=10, color=FIELD))
    # голка чітко сідає в центр
    frags.append(line(padx, board_y - 70, padx, pady - 3, color=BRASS, sw=2.6))
    frags.append(circle(padx, pady - 3, 2.6, fill=INK, stroke=INK))
    frags.append(text(padx, board_y - 78, "голка сідає в центр", size=10, color=BRASS))

    # ── ПРАВОРУЧ (погано): три способи втратити точку ──
    cxR = 560
    frags.append(text(cxR, 70, "Втрачена тест-точка", size=13, color=POS, bold=True))
    frags.append(rect(cxR - 150, board_y, 300, 60, fill="#fdf0ee", stroke=POS, sw=1.6))

    # (а) під деталлю
    ax = cxR - 100
    frags.append(circle(ax, board_y + 24, 14, fill=COPPER_FILL, stroke=COPPER, sw=1.5))
    frags.append(rect(ax - 16, board_y + 10, 32, 20, fill="#666", stroke=INK, sw=1.4))  # деталь зверху
    frags.append(text(ax, board_y + 48, "під деталлю", size=10, color=POS))
    frags.append(line(ax, board_y - 60, ax, board_y + 6, color=BRASS, sw=2.4))
    frags.append(text(ax, board_y - 68, "голка б'є\nв корпус", size=9, color=POS))

    # (б) на перехідному отворі (via) під маскою
    bx2 = cxR
    frags.append(circle(bx2, board_y + 24, 7, fill="#3a5a78", stroke=INK, sw=1.4))  # via
    frags.append(circle(bx2, board_y + 24, 3, fill=BG, stroke=INK, sw=1))            # дірка
    frags.append(text(bx2, board_y + 48, "via під маскою", size=10, color=POS))
    frags.append(line(bx2, board_y - 60, bx2, board_y + 12, color=BRASS, sw=2.4))
    frags.append(text(bx2, board_y - 68, "голка\nзісковзує", size=9, color=POS))

    # (в) занадто дрібна
    cx3 = cxR + 105
    frags.append(circle(cx3, board_y + 24, 4, fill=COPPER_FILL, stroke=COPPER, sw=1.3))
    frags.append(text(cx3, board_y + 48, "надто дрібна", size=10, color=POS))
    frags.append(line(cx3 + 9, board_y - 60, cx3 + 9, board_y + 20, color=BRASS, sw=2.4))
    frags.append(text(cx3, board_y - 68, "промах —\nмимо", size=9, color=POS))

    frags.append(line(W / 2 - 20, 58, W / 2 - 20, 320, color=MUTED, sw=1, dash="5,5"))
    render(os.path.join(OUT, 'testpoint-access.svg'), W, H, *frags)


# ── Фігура 4 (вставка proj): дві доріжки одного тесту — DUT ↔ джиг ────────────
def fig_selftest_flow():
    W, H = 900, 540
    frags = []
    frags.append(text(W / 2, 30,
                      "Плата міряє й доповідає — джиг судить і протоколює",
                      size=16, bold=True))

    colw = 300          # ширина колонки-кроку
    lx = 40             # ліва колонка (DUT)
    rx = 480            # права колонка (джиг)
    gut_x = lx + colw + (rx - (lx + colw)) / 2   # осьова лінія проміжку
    top = 62
    step_h = 40
    gap = 16

    # шапки колонок
    frags.append(fitbox(lx, top, colw, 32, "Бік плати (DUT): лише міряє й повідомляє",
                        size=12, bold=True, fill="#eaf4ec", stroke=FIELD, color=FIELD))
    frags.append(fitbox(rx, top, colw, 32, "Бік джига: лише судить і протоколює",
                        size=12, bold=True, fill="#fbf7ee", stroke=BRASS, color=BRASS))
    body_top = top + 32 + gap

    # ── ліва колонка: кроки самоперевірки ──
    dut = [
        "старт (POST) — до головного циклу",
        "1. читає власні шини АЦП (Vref, 3.3/5 В)",
        "2. ганяє GPIO-петлі: 1→1, 0→0",
        "3. опитує давачі: регістр WHO_AM_I",
        "зшиває рапорт + XOR-сума",
        "шле рядок $RPT;… по UART / SWD",
    ]
    ly = body_top
    left_cx = lx + colw / 2
    send_cy = None
    for i, s in enumerate(dut):
        col = FIELD if i in (0, len(dut) - 1) else INK
        frags.append(fitbox(lx, ly, colw, step_h, s, size=11, color=col,
                            fill="#f4faf6", stroke=col, sw=1.3))
        if i == len(dut) - 1:
            send_cy = ly + step_h / 2          # центр «шле рядок …»
        if i < len(dut) - 1:
            frags.append(arrow(left_cx, ly + step_h, left_cx, ly + step_h + gap - 2,
                                color=FIELD, sw=1.8))
        ly += step_h + gap

    # ── права колонка: кроки судді ──
    jig = [
        "чекає рядок із ТАЙМАУТОМ",
        "перевіряє XOR-суму (цілий?)",
        "звіряє поля з таблицею допусків",
        "вирок: ПРОЙШЛА / БРАК",
        "запис у журнал за серійником SN",
    ]
    ry = body_top
    right_cx = rx + colw / 2
    recv_cy = ry + step_h / 2                   # центр «чекає рядок …»
    jig_bottom = None
    for i, s in enumerate(jig):
        col = BRASS if i == 0 else (POS if i == 3 else INK)
        frags.append(fitbox(rx, ry, colw, step_h, s, size=11, color=col,
                            fill="#fdfaf3", stroke=col, sw=1.3))
        if i < len(jig) - 1:
            frags.append(arrow(right_cx, ry + step_h, right_cx, ry + step_h + gap - 2,
                                color=BRASS, sw=1.8))
        jig_bottom = ry + step_h
        ry += step_h + gap

    # ── рапорт: елбоу лівий-низ → проміжок → правий-верх (без перетину рамок) ──
    # горизонталь з боку плати, вертикаль по осі проміжку, горизонталь у джиг
    frags.append(line(lx + colw, send_cy, gut_x, send_cy, color=NEG, sw=2.2))
    frags.append(line(gut_x, send_cy, gut_x, recv_cy, color=NEG, sw=2.2))
    frags.append(arrow(gut_x, recv_cy, rx - 2, recv_cy, color=NEG, sw=2.2))
    frags.append(text(gut_x, send_cy + 20, "рапорт", size=11, color=NEG, bold=True))
    frags.append(text(gut_x, send_cy + 34, "$RPT;…", size=11, color=NEG, bold=True))

    # ── червона гілка «таймаут» — від «чекає рядок» уздовж правого поля вниз у бокс ──
    marg_x = rx + colw + 24                      # вертикаль у правому полі
    to_y = jig_bottom + gap                      # бокс під колонкою джига
    frags.append(line(rx + colw, recv_cy, marg_x, recv_cy, color=POS, sw=1.8, dash="5,4"))
    frags.append(line(marg_x, recv_cy, marg_x, to_y + step_h / 2, color=POS, sw=1.8, dash="5,4"))
    frags.append(mtext(marg_x + 8, (recv_cy + to_y) / 2, ["нема", "відповіді"],
                       size=9.5, color=POS, anchor="start"))
    frags.append(arrow(marg_x, to_y + step_h / 2, rx + colw + 2, to_y + step_h / 2,
                       color=POS, sw=1.8))
    frags.append(fitbox(rx, to_y, colw, step_h + 6,
                        "ТИША → ТАЙМАУТ: третій результат —\nне прошилась / мертва плата",
                        size=10.5, color=POS, fill="#fdf0ee", stroke=POS, sw=1.5))

    render(os.path.join(OUT, 'selftest-flow.svg'), W, H, *frags)


# ═══════════════════════════════════════════════════════════════════════════
#  ФІГУРИ ДЛЯ ДЕТАЛЬНОЇ СТАТТІ (test-jig-design-d.md)
# ═══════════════════════════════════════════════════════════════════════════

# ── D-Фіг 1: робоче вікно сили F=k·x + рівномірне vs зібране ложе ─────────────
def fig_spring_force_window():
    W, H = 820, 400
    frags = []
    frags.append(text(W / 2, 28, "Сила голки: робоче вікно ходу й розподіл по площі",
                      size=15, bold=True))

    # ── ЛІВОРУЧ: пряма F = k·x із робочим вікном ──
    ox, oy = 70, 320          # початок осей
    axw, axh = 300, 210
    frags.append(text(ox + axw / 2, 66, "Одна голка: F = k·x", size=13, color=NEG, bold=True))
    # осі
    frags.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))          # F вгору
    frags.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))          # x праворуч
    frags.append(text(ox - 10, oy - axh + 4, "F", size=12, color=INK, anchor="end"))
    frags.append(text(ox + axw, oy + 18, "x (стиснення)", size=11, color=INK, anchor="end"))
    # робоче вікно (середня третина ходу) — світла смуга
    x_lo = ox + axw * 0.35
    x_hi = ox + axw * 0.68
    frags.append(rect(x_lo, oy - axh, x_hi - x_lo, axh, fill="#eef4ff", stroke="none", rx=0))
    # пряма Гука
    frags.append(line(ox, oy, ox + axw * 0.9, oy - axh * 0.9, color=NEG, sw=2.4))
    # робоча точка — у середині вікна
    wpx = (x_lo + x_hi) / 2
    wpy = oy - (wpx - ox) / (axw * 0.9) * (axh * 0.9)
    frags.append(circle(wpx, wpy, 4.5, fill=POS, stroke=POS))
    frags.append(text(wpx + 8, wpy - 6, "робоча точка", size=10, color=POS, anchor="start"))
    # підписи країв
    frags.append(mtext(x_lo - 4, oy + 16, ["замало:", "контакт"], size=9, color=MUTED, anchor="middle"))
    frags.append(mtext(x_hi + 8, oy + 16, ["забагато:", "знос"], size=9, color=MUTED, anchor="middle"))
    frags.append(text(x_lo + (x_hi - x_lo) / 2, oy - axh - 8, "робоче вікно (≈ 2/3 ходу)",
                      size=10, color=NEG))

    # ── ПРАВОРУЧ: рівномірне vs зібране ложе ──
    rx = 470
    # рівномірне
    frags.append(text(rx + 70, 66, "Ложе: N·F має бути рівномірним", size=13, color=FIELD, bold=True))
    by1 = 130
    frags.append(rect(rx, by1, 160, 12, fill="#eaf4ec", stroke=FIELD, sw=1.8))
    for i in range(6):
        gx = rx + 14 + i * 26
        frags.append(line(gx, by1 + 40, gx, by1 + 12, color=BRASS, sw=2))
        frags.append(circle(gx, by1 + 12, 2, fill=INK, stroke=INK))
    frags.append(text(rx + 80, by1 + 58, "голки по площі → плата лежить плоско",
                      size=10, color=FIELD))

    # зібране в кут → пропелер
    by2 = 250
    # плата нахилена (пропелер): малюємо як нахилену лінію
    frags.append(line(rx, by2 + 22, rx + 160, by2 - 6, color=POS, sw=2.4))
    # голки збиті ліворуч
    for i in range(4):
        gx = rx + 12 + i * 16
        gy_top = by2 + 60
        # площадка на нахиленій платі
        pady = by2 + 22 - (gx - rx) / 160 * 28
        frags.append(line(gx, gy_top, gx, pady, color=BRASS, sw=2))
    # далекий кут відірваний — показати щілину
    farx = rx + 150
    fary = by2 - 4
    frags.append(line(farx, by2 + 60, farx, fary + 14, color=MUTED, sw=1.6, dash="3,3"))
    frags.append(text(farx + 6, fary + 6, "відрив", size=9, color=POS, anchor="start"))
    frags.append(text(rx + 80, by2 + 76, "голки в куті → плата «пропелером», далекі відходять",
                      size=10, color=POS))

    frags.append(line(410, 60, 410, 360, color=MUTED, sw=1, dash="5,5"))
    render(os.path.join(OUT, 'spring-force-window.svg'), W, H, *frags)


# ── D-Фіг 2: кельвінова 4-дротова схема проти 2-дротової ──────────────────────
def fig_kelvin_4wire():
    W, H = 800, 400
    frags = []
    frags.append(text(W / 2, 28, "Дві голки на точку: вимір без падіння на контакті голки",
                      size=15, bold=True))

    # ── ВЕРХ: 2 дроти (брехня) ──
    ty = 110
    frags.append(text(140, ty - 30, "Дві голки (2 дроти)", size=12, color=POS, bold=True))
    # ділянка R на платі
    seg_x1, seg_x2 = 300, 500
    frags.append(rect(seg_x1, ty - 6, seg_x2 - seg_x1, 12, fill=COPPER_FILL, stroke=COPPER, sw=1.6))
    frags.append(text((seg_x1 + seg_x2) / 2, ty + 24, "ділянка R (доріжка / шунт)", size=10, color=MUTED))
    # ліва й права голки з опором
    for gx, lbl in [(seg_x1, "голка+дріт"), (seg_x2, "голка+дріт")]:
        frags.append(line(gx, ty - 60, gx, ty - 6, color=BRASS, sw=2.4))
        frags.append(circle(gx, ty - 6, 2.4, fill=INK, stroke=INK))
        # позначка опору голки — маленький зиґзаґ
        frags.append(text(gx + (10 if gx == seg_x2 else -10), ty - 40,
                          "R_г", size=9, color=POS, anchor=("start" if gx == seg_x2 else "end")))
    # струм і вимір по тих самих дротах
    frags.append(arrow(seg_x1 - 40, ty - 60, seg_x1, ty - 60, color=NEG, sw=2))
    frags.append(text(seg_x1 - 44, ty - 66, "I", size=11, color=NEG, anchor="end"))
    frags.append(fitbox(560, ty - 74, 210, 40,
                        "міряєш R + R_г + R_г + дроти → БРЕХНЯ",
                        size=10.5, color=POS, fill="#fdf0ee", stroke=POS, sw=1.4))

    # ── НИЗ: 4 дроти (правда) ──
    by = 280
    frags.append(text(140, by - 34, "Кельвін (4 дроти)", size=12, color=FIELD, bold=True))
    frags.append(rect(seg_x1, by - 6, seg_x2 - seg_x1, 12, fill=COPPER_FILL, stroke=COPPER, sw=1.6))
    frags.append(text((seg_x1 + seg_x2) / 2, by + 22, "та сама ділянка R", size=10, color=MUTED))
    # на кожному кінці — ПАРА голок: силова (струм) + вимірювальна (I≈0)
    for cx_, side in [(seg_x1, -1), (seg_x2, +1)]:
        fx = cx_ + side * 10     # силова трохи назовні
        sx = cx_ - side * 10     # вимірювальна трохи всередину
        # силова
        frags.append(line(fx, by - 62, fx, by - 6, color=NEG, sw=2.6))
        frags.append(circle(fx, by - 6, 2.4, fill=INK, stroke=INK))
        # вимірювальна
        frags.append(line(sx, by - 46, sx, by - 6, color=FIELD, sw=2.0))
        frags.append(circle(sx, by - 6, 2.0, fill=INK, stroke=INK))
    frags.append(arrow(seg_x1 - 40, by - 62, seg_x1 - 10, by - 62, color=NEG, sw=2))
    frags.append(text(seg_x1 - 44, by - 68, "I (силова)", size=10, color=NEG, anchor="end"))
    frags.append(text(seg_x2 + 46, by - 46, "вимір (I≈0)", size=10, color=FIELD, anchor="start"))
    frags.append(text(seg_x2 + 46, by - 30, "→ падіння = 0", size=10, color=FIELD, anchor="start"))
    frags.append(fitbox(560, by - 74, 210, 44,
                        "вимір. голка струму не несе:\nчитаєш ЧИСТИЙ R ділянки",
                        size=10.5, color=FIELD, fill="#eaf4ec", stroke=FIELD, sw=1.4))

    frags.append(line(60, 190, 740, 190, color=MUTED, sw=1, dash="5,5"))
    render(os.path.join(OUT, 'kelvin-4wire.svg'), W, H, *frags)


# ── D-Фіг 3: кидок струму vs коротке — криві в часі ──────────────────────────
def fig_inrush_vs_short():
    W, H = 780, 400
    frags = []
    frags.append(text(W / 2, 28, "Кидок vs коротке: розрізняє форма кривої, не одне число",
                      size=15, bold=True))

    ox, oy = 90, 330
    axw, axh = 600, 250
    # осі
    frags.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))
    frags.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    frags.append(text(ox - 12, oy - axh + 4, "I", size=12, color=INK, anchor="end"))
    frags.append(text(ox + axw, oy + 18, "час", size=11, color=INK, anchor="end"))

    # рівень стелі обмеження
    ceil_y = oy - axh * 0.86
    frags.append(line(ox, ceil_y, ox + axw, ceil_y, color=POS, sw=1.4, dash="6,4"))
    frags.append(text(ox + axw - 4, ceil_y - 6, "стеля обмеження струму", size=10, color=POS, anchor="end"))
    # рівень робочого струму
    work_y = oy - axh * 0.20
    frags.append(line(ox, work_y, ox + axw, work_y, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(ox + 6, work_y - 6, "робочий струм", size=10, color=MUTED, anchor="start"))

    # КОРОТКЕ (червоне): різко вгору й тримається на стелі
    sx0 = ox
    pts_short = [(sx0, oy), (sx0 + 30, ceil_y + 4), (ox + axw * 0.9, ceil_y + 4)]
    for i in range(len(pts_short) - 1):
        (x1, y1), (x2, y2) = pts_short[i], pts_short[i + 1]
        frags.append(line(x1, y1, x2, y2, color=POS, sw=2.6))
    frags.append(text(ox + axw * 0.55, ceil_y - 12, "коротке: тримається на стелі → БРАК",
                      size=11, color=POS, bold=True))

    # КИДОК (синій): вгору майже до стелі, тоді спад до робочого й полиця
    peak_x = ox + axw * 0.10
    peak_y = ceil_y + 18
    settle_x = ox + axw * 0.42
    # підйом
    frags.append(line(ox, oy, peak_x, peak_y, color=NEG, sw=2.6))
    # спад (крива-ламана вниз до робочого)
    dec = [(peak_x, peak_y), (peak_x + 40, work_y + 40), (settle_x, work_y),
           (ox + axw * 0.95, work_y)]
    for i in range(len(dec) - 1):
        (x1, y1), (x2, y2) = dec[i], dec[i + 1]
        frags.append(line(x1, y1, x2, y2, color=NEG, sw=2.6))
    frags.append(text(peak_x + 30, peak_y - 10, "кидок: заряд конденсаторів", size=11, color=NEG, bold=True))
    frags.append(text(settle_x + 60, work_y - 10, "спав до робочого → жива", size=10, color=NEG, anchor="start"))

    # вертикаль «вікно рішення»
    dec_x = settle_x
    frags.append(line(dec_x, oy, dec_x, oy - axh, color=FIELD, sw=1, dash="4,3"))
    frags.append(mtext(dec_x, oy + 16, ["момент", "суду"], size=9, color=FIELD, anchor="middle"))

    render(os.path.join(OUT, 'inrush-vs-short.svg'), W, H, *frags)


# ── D-Фіг 4: геометрія тест-точки з числами (розкид, keepout, маска, via) ─────
def fig_testpoint_geometry():
    W, H = 780, 380
    frags = []
    frags.append(text(W / 2, 28, "Геометрія тест-точки: розмір = сума допусків механіки",
                      size=15, bold=True))

    # ── ЛІВОРУЧ: площадка + пляма розкиду ──
    cx, cy = 220, 210
    # keepout — велике світле коло
    frags.append(circle(cx, cy, 90, fill="#f4faf6", stroke=FIELD, sw=1.2, ))
    frags.append(text(cx, cy - 108, "keepout: без високих деталей", size=10, color=FIELD))
    # мідна площадка ~1 мм
    frags.append(circle(cx, cy, 42, fill=COPPER_FILL, stroke=COPPER, sw=2))
    frags.append(text(cx, cy + 66, "мідь ≈ 1 мм, відкрита від маски", size=10, color=COPPER))
    # пляма розкиду ~0.6 мм (пунктир усередині)
    frags.append(circle(cx, cy, 24, fill="none", stroke=NEG, sw=1.4, ))
    frags.append(text(cx, cy + 3, "розкид", size=9, color=NEG))
    frags.append(text(cx, cy + 15, "≈ 0.6 мм", size=9, color=NEG))
    # голка в центр — коротка, заходить ЗНИЗУ праворуч (щоб не різати підпис keepout над платою)
    frags.append(line(cx + 34, cy - 66, cx, cy - 4, color=BRASS, sw=2.4))
    frags.append(circle(cx, cy, 2.6, fill=INK, stroke=INK))
    frags.append(text(cx + 40, cy - 58, "голка", size=9, color=BRASS, anchor="start"))

    # формула RSS праворуч від картинки
    frags.append(mtext(cx + 132, cy - 30,
                       ["Δ = √(Δ₁²+Δ₂²+Δ₃²+Δ₄²)",
                        "напрямні · плата ·",
                        "плита · сама голка",
                        "(незалежні → RSS,",
                        "не проста сума)"],
                       size=11, color=INK, anchor="start", lh=1.35))

    # ── ПРАВОРУЧ ВНИЗУ: заборонено на via ──
    vx, vy = 600, 300
    frags.append(circle(vx, vy, 18, fill="#3a5a78", stroke=INK, sw=1.5))   # via-кільце
    frags.append(circle(vx, vy, 7, fill=BG, stroke=INK, sw=1.2))            # дірка
    frags.append(line(vx + 6, vy - 44, vx + 6, vy - 2, color=BRASS, sw=2.2))
    frags.append(text(vx, vy + 34, "НЕ на via:", size=10, color=POS))
    frags.append(text(vx, vy + 48, "голка зісковзує в дірку", size=10, color=POS))

    # роздільник — між лівою ілюстрацією (keepout r=90 сягає x≈310) і RSS-блоком (x≈352)
    frags.append(line(325, 62, 325, 350, color=MUTED, sw=1, dash="5,5"))
    render(os.path.join(OUT, 'testpoint-geometry.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_pogo_anatomy()
    fig_jig_machine()
    fig_testpoint_access()
    fig_selftest_flow()
    # детальна стаття:
    fig_spring_force_window()
    fig_kelvin_4wire()
    fig_inrush_vs_short()
    fig_testpoint_geometry()
    print("ok")
