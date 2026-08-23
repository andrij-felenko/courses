# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: три роботи стіни корпусу ──────────────────────────────────────
def fig_three_jobs():
    W, H = 760, 380
    f = []
    # центральна стіна
    wx = W / 2
    f.append(rect(wx - 16, 60, 32, H - 120, fill="#e6ddc9", stroke=INK, sw=2, rx=4))
    f.append(text(wx, 48, "стіна корпусу", size=14, bold=True))

    # ліворуч — ворожий світ
    f.append(text(180, 48, "ВОРОЖЕ ПОЛЕ", size=15, bold=True, color=POS))
    b, w, h = textbox(150, 110, "вода\n(дощ, занурення)", size=13); f.append(b)
    b, w, h = textbox(150, 190, "пил", size=13); f.append(b)
    b, w, h = textbox(150, 265, "удар,\nвібрація", size=13); f.append(b)
    for cy in (110, 190, 265):
        f.append(arrow(240, cy, wx - 22, cy, color=POS, sw=2.2))

    # праворуч — плата
    f.append(text(600, 48, "ПЛАТА", size=15, bold=True, color=FIELD))
    f.append(rect(540, 150, 150, 90, fill="#eafaf0", stroke=FIELD, sw=2))
    for gx in (560, 590, 620, 650):
        f.append(rect(gx, 175, 14, 8, fill="#cdeed8", stroke=FIELD, sw=1))
        f.append(rect(gx, 205, 14, 8, fill="#cdeed8", stroke=FIELD, sw=1))
    f.append(text(615, 260, "крихка електроніка", size=12, color=MUTED))

    # підпис-мораль знизу стіни
    b, w, h = textbox(wx, 322, "три роботи однієї стіни", size=13, bold=True,
                      fill="#fff8e1", stroke="#c9a227"); f.append(b)

    # прохід крізь стіну (третя робота) — розрив у стіні на рівні плати,
    # у чистій смузі між стрілками води (110) і пилу (190)
    f.append(rect(wx - 16, 144, 32, 14, fill="#d8f5e3", stroke=FIELD, sw=2, rx=2))
    f.append(text(wx, 138, "прохід: живлення · сигнал · повітря", size=11,
                  color=FIELD, bold=True))

    render(os.path.join(OUT, 'three-jobs.svg'), W, H, *f,
           title="Стіна виробу несе три різні навантаження")


# ── Фігура 2: IP-код — дві незалежні цифри ──────────────────────────────────
def fig_ip_decoder():
    W, H = 720, 424
    f = []
    # великий напис IP 6 7 — кожен символ окремо, кольором осі
    y0 = 96
    f.append(text(300, y0, "IP", size=52, bold=True, anchor="end"))
    f.append(text(360, y0, "6", size=52, bold=True, color=POS))
    f.append(text(430, y0, "7", size=52, bold=True, color=NEG))

    # перша цифра -> тверде
    f.append(line(360, y0 + 14, 360, 150, color=POS, sw=2))
    f.append(arrow(360, 150, 200, 175, color=POS, sw=2))
    b, w, h = textbox(150, 210, "перша цифра\nТВЕРДЕ (пил)\nшкала 0…6", size=13,
                      color=POS, stroke=POS, fill="#fdecea"); f.append(b)
    # шкала твердого
    steps1 = ["0 нема", "5 пилозахищ.", "6 пилонепрон."]
    for i, s in enumerate(steps1):
        b, w, h = textbox(150, 272 + i * 40, s, size=12, stroke=POS,
                          fill="#fff6f5", min_w=170); f.append(b)

    # друга цифра -> вода
    f.append(line(430, y0 + 14, 430, 150, color=NEG, sw=2))
    f.append(arrow(430, 150, 560, 175, color=NEG, sw=2))
    b, w, h = textbox(575, 210, "друга цифра\nВОДА\nшкала 0…9", size=13,
                      color=NEG, stroke=NEG, fill="#eaf0fd"); f.append(b)
    steps2 = ["3 дощ (бризки)", "5–6 струмінь", "7 занурення 1 м", "8 занурення (виробник)"]
    for i, s in enumerate(steps2):
        b, w, h = textbox(575, 272 + i * 38, s, size=12, stroke=NEG,
                          fill="#f5f8ff", min_w=195); f.append(b)

    # ключова думка — у чистому центрі, нижче кінців стрілок (y=175),
    # щоб жодна лінія-гілка не проходила крізь напис
    b, w, h = textbox(W / 2, 205, "дві НЕЗАЛЕЖНІ осі", size=13, bold=True,
                      fill="#fff8e1", stroke="#c9a227"); f.append(b)

    render(os.path.join(OUT, 'ip-decoder.svg'), W, H, *f,
           title="IP-код: пил і вода — окремі цифри")


# ── Фігура 3: пастка запаяного ящика проти дихаючого ────────────────────────
def fig_breathing_box():
    W, H = 760, 400
    f = []

    def box(cx, top, label):
        bw, bh = 200, 150
        x = cx - bw / 2
        f.append(rect(x, top, bw, bh, fill="#f4f6f8", stroke=INK, sw=2.2))
        # плата всередині
        f.append(rect(cx - 55, top + bh - 40, 110, 22, fill="#eafaf0",
                      stroke=FIELD, sw=1.5))
        f.append(text(cx, top - 12, label, size=14, bold=True))
        return x, bw, bh

    # ЛІВОРУЧ: запаяний
    lx = 200
    x, bw, bh = box(lx, 100, "запаяний ящик")
    # день: видих (стрілка вгору з лівого боку кришки)
    f.append(arrow(lx - 45, 100 - 4, lx - 45, 70, color=POS, sw=2.4))
    f.append(text(lx - 45, 60, "☀ день:", size=12, color=POS, bold=True))
    f.append(text(lx - 45, 46, "видих ↑", size=11, color=POS))
    # ніч: вдих вологи (стрілка вниз з правого боку кришки)
    f.append(arrow(lx + 45, 70, lx + 45, 100 - 4, color=NEG, sw=2.4))
    f.append(text(lx + 45, 60, "☾ ніч:", size=12, color=NEG, bold=True))
    f.append(text(lx + 45, 46, "вдих вологи ↓", size=11, color=NEG))
    # краплі всередині
    for dx in (-30, 5, 35):
        f.append(circle(lx + dx, 175, 4, fill="#cfe3ff", stroke=NEG, sw=1))
    b, w, h = textbox(lx, 275, "щоночі засмоктує вологу\n→ конденсат на платі", size=12,
                      color=POS, stroke=POS, fill="#fdecea"); f.append(b)

    # ПРАВОРУЧ: дихаючий
    rx = 560
    x, bw, bh = box(rx, 100, "ящик із мембраною")
    # отвір з мембраною у кришці
    f.append(rect(rx - 12, 100 - 5, 24, 8, fill="#d8f5e3", stroke=FIELD, sw=2))
    f.append(text(rx, 62, "мембрана ePTFE", size=12, color=FIELD, bold=True))
    f.append(text(rx, 46, "(отвір)", size=11, color=MUTED))
    # подвійна стрілка «дихання» через кришку — нижче напису, обабіч отвору,
    # щоб лінія не різала назву ящика
    f.append(arrow(rx - 26, 120, rx - 26, 98, color=FIELD, sw=2.2))   # видих ↑
    f.append(arrow(rx + 26, 98, rx + 26, 120, color=FIELD, sw=2.2))   # вдих ↓
    f.append(mtext(rx + 92, 116, ["повітря +", "пара ⇄"], size=11, color=FIELD))
    # вода відбита
    f.append(text(rx, 138, "вода ✗", size=13, color=POS, bold=True))
    b, w, h = textbox(rx, 275, "тиск завжди зрівняний\n→ сухо всередині", size=12,
                      color=FIELD, stroke=FIELD, fill="#eafaf0"); f.append(b)

    # мораль
    b, w, h = textbox(W / 2, 350, "щільніше ≠ сухіше: рятує ОДИН правильний отвір",
                      size=13, bold=True, fill="#fff8e1", stroke="#c9a227"); f.append(b)

    render(os.path.join(OUT, 'breathing-box.svg'), W, H, *f,
           title="Пастка герметичного ящика: він сам качає вологу")


# ── Вставка comp-pressure-vent: пора сортує молекулу від краплі ──────────────
def fig_vent_pore():
    W, H = 760, 430
    f = []
    f.append(text(W / 2, 24, "Пора мембрани: молекула проходить, крапля — ні",
                  size=17, bold=True))

    # мембрана — товста горизонтальна смуга з «порами» (розривами)
    my, mh = 170, 90
    f.append(text(W / 2, my - 18, "мембрана ePTFE (у розрізі)", size=13, bold=True))
    # ліва частина смуги
    f.append(rect(60, my, 250, mh, fill="#e8eef4", stroke=INK, sw=2))
    # права частина смуги
    f.append(rect(450, my, 250, mh, fill="#e8eef4", stroke=INK, sw=2))
    # звивистий канал пори між ними (вузол-фібрила): дві похилі стінки
    f.append(line(310, my, 360, my + 30, color=INK, sw=2))
    f.append(line(360, my + 30, 405, my, color=INK, sw=2))
    f.append(line(310, my + mh, 355, my + mh - 28, color=INK, sw=2))
    f.append(line(355, my + mh - 28, 450, my + mh, color=INK, sw=2))
    f.append(mtext(380, my + mh / 2 - 3, ["пора", "≈0.1 мкм"], size=10, color=MUTED))

    # верх — «зовні»: крапля води (велика) сидить на порі, дрібні молекули поряд
    f.append(text(150, 70, "ЗОВНІ (мокро)", size=13, bold=True, color=POS))
    # крапля — велика, НЕ пролазить: сидить на вході в пору
    f.append(circle(380, my - 34, 30, fill="#cfe3ff", stroke=NEG, sw=2))
    f.append(text(380, my - 30, "H₂O", size=12, color=NEG, bold=True))
    f.append(text(380, my - 62, "крапля ✗", size=12, color=POS, bold=True))
    # дрібні молекули повітря/пари — надлітають до пори з боків
    for mx, lab, ex in ((260, "O₂/N₂", 352), (500, "H₂O-пара", 408)):
        f.append(circle(mx, 96, 6, fill="#eafaf0", stroke=FIELD, sw=1.5))
        f.append(text(mx, 80, lab, size=11, color=FIELD))
        # молекула летить у пору, тоді крізь неї — вниз, «усередину»
        f.append(arrow(mx, 104, ex, my + 6, color=FIELD, sw=1.7))
    # крізь саму пору — вниз, «усередину» (молекули проходять)
    f.append(arrow(380, my + mh / 2 + 20, 380, my + mh + 24, color=FIELD, sw=2))

    # низ — «всередині»
    f.append(text(150, my + mh + 46, "ВСЕРЕДИНІ (сухо)", size=13, bold=True, color=FIELD))

    # права колонка — масштаб «чому так»
    b, w, h = textbox(620, 330,
                      "молекула H₂O:\n~0.0003 мкм", size=12, color=FIELD,
                      stroke=FIELD, fill="#eafaf0", min_w=190); f.append(b)
    b, w, h = textbox(620, 388,
                      "крапля роси:\n~1000 мкм", size=12, color=POS,
                      stroke=POS, fill="#fdecea", min_w=190); f.append(b)

    # мораль
    b, w, h = textbox(230, 358,
                      "пора > молекули у тисячі разів,\nале < краплі у мільйони",
                      size=12, bold=True, fill="#fff8e1", stroke="#c9a227"); f.append(b)

    render(os.path.join(OUT, 'vent-pore.svg'), W, H, *f,
           title=None)


# ── Вставка comp-pressure-vent: інтеграція вента у стінку + граблі ───────────
def fig_vent_mount():
    W, H = 780, 500
    f = []
    f.append(text(W / 2, 24, "Вент у стінці корпусу: тримає IP і дає дихати",
                  size=17, bold=True))

    # ── лівий блок: зріз стінки з вкрученим вентом ──
    wx = 210          # вісь отвору
    wth = 34          # товщина стінки
    top, bot = 90, 300
    gap_top, gap_bot = 160, 230   # межі отвору по вертикалі

    f.append(text(wx, 74, "стінка (зріз)", size=12, bold=True))
    # дві частини стінки (над і під отвором)
    f.append(rect(wx - wth / 2, top, wth, gap_top - top,
                  fill="#e6ddc9", stroke=INK, sw=2))
    f.append(rect(wx - wth / 2, gap_bot, wth, bot - gap_bot,
                  fill="#e6ddc9", stroke=INK, sw=2))

    # корпус вента з фланцем (обіймає отвір із боку «зовні», зліва)
    f.append(rect(wx - wth / 2 - 16, gap_top - 8, 16, 8,
                  fill="#cfd8e3", stroke=INK, sw=1.8))
    f.append(rect(wx - wth / 2 - 16, gap_bot, 16, 8,
                  fill="#cfd8e3", stroke=INK, sw=1.8))
    f.append(rect(wx - wth / 2 - 16, gap_top, 8, gap_bot - gap_top,
                  fill="#cfd8e3", stroke=INK, sw=1.8))
    f.append(mtext(wx - 96, gap_top + 20, ["корпус", "вента"], size=11, color=MUTED))

    # мембрана — тонка смуга поперек отвору
    f.append(rect(wx - wth / 2, (gap_top + gap_bot) / 2 - 3, wth, 6,
                  fill="#d8f5e3", stroke=FIELD, sw=2))
    f.append(text(wx + 92, (gap_top + gap_bot) / 2 - 12,
                  "мембрана ePTFE", size=12, color=FIELD, bold=True))

    # сторони
    f.append(text(wx - 96, 108, "ЗОВНІ", size=13, bold=True, color=POS))
    f.append(text(wx + 96, 108, "ВСЕРЕДИНІ", size=13, bold=True, color=FIELD))

    # дихання: подвійна стрілка крізь мембрану
    cy = (gap_top + gap_bot) / 2
    f.append(arrow(wx - 62, cy + 18, wx - wth / 2 - 2, cy + 18, color=FIELD, sw=2))
    f.append(arrow(wx + 62, cy + 18, wx + wth / 2 + 2, cy + 18, color=FIELD, sw=2))
    f.append(text(wx, cy + 42, "повітря ⇄ пара", size=11, color=FIELD))
    # вода відбита зовні
    f.append(circle(wx - 40, cy - 22, 9, fill="#cfe3ff", stroke=NEG, sw=1.8))
    f.append(text(wx - 40, cy - 40, "вода ✗", size=12, color=POS, bold=True))

    # ── правий блок: три граблі, стовпчиком ──
    gx = 590
    grief = [
        ("①  забиті пори", "мастило, фарба, бруд\nсідають на плівку —\nвент «оглух», дихати\nнема чим"),
        ("②  перетяг монтажу", "закрутив надто сильно —\nмембрана тріснула або\nфланець підвернувся,\nIP пропав"),
        ("③  замалий на об'єм", "великий корпус, крихітний\nвент: не встигає зрівняти\nтиск за швидку зміну —\nпомпа вертається"),
    ]
    y = 92
    for head, body in grief:
        b, w, h = textbox(gx, y + 12, head, size=13, bold=True, color=POS,
                          stroke=POS, fill="#fdecea", min_w=250)
        f.append(b)
        b2, w2, h2 = textbox(gx, y + 12 + h / 2 + 30, body, size=11, color=INK,
                             stroke="#d9c27a", fill="#fffdf3", min_w=250)
        f.append(b2)
        y += h + h2 + 26

    render(os.path.join(OUT, 'vent-mount.svg'), W, H, *f, title=None)


# ── Вставка hist-ip-code: шлях IP-коду від порожнього слова до двох цифр ─────
def fig_ip_history():
    W, H = 820, 300
    f = []
    # горизонтальна вісь часу
    axis_y = 150
    x_lo, x_hi = 70, 748
    f.append(line(x_lo, axis_y, x_hi, axis_y, color=MUTED, sw=2.5))
    f.append(arrow(x_hi - 24, axis_y, x_hi, axis_y, color=MUTED, sw=2.5))

    # віхи: (x, рік, підпис, колір, «угору»?)
    milestones = [
        (112, "1934", "DIN VDE 50\nперша система\nпозначень (нім.)", FIELD, True),
        (300, "1963", "IEC 60144\nдля щитів", NEG, False),
        (432, "1968", "IEC 60034-5\nдля моторів", NEG, True),
        (560, "1970", "комітет TC 70:\nзведення\nдокупи", POS, False),
        (688, "1976", "IEC 60529\nодин IP-код,\nдві цифри", INK, True),
    ]
    for x, yr, lbl, col, up in milestones:
        f.append(circle(x, axis_y, 7, fill=col, stroke=INK, sw=1.5))
        # рік — впритул до точки
        yr_y = axis_y - 16 if up else axis_y + 28
        f.append(text(x, yr_y, yr, size=15, bold=True, color=col))
        # рамка-підпис — над або під віссю
        by = axis_y - 66 if up else axis_y + 76
        b, w, h = textbox(x, by, lbl, size=11, stroke=col,
                          fill="#ffffff", min_w=108)
        f.append(b)

    render(os.path.join(OUT, 'ip-history.svg'), W, H, *f,
           title="Від порожнього слова до двох цифр: шлях IP-коду")


# ── Вставка math-sealed-box-pressure: циклічне навантаження на прокладку ──────
def fig_pressure_cycle():
    import math
    W, H = 760, 462
    f = []

    # спільна вісь часу (дві доби), три яруси зверху вниз
    x0, x1 = 96, 692
    span = x1 - x0

    def tx(u):            # u ∈ [0,2] діб → піксель
        return x0 + span * (u / 2.0)

    # ── Ярус 1 (зверху): прокладку гойдає ──────────────────────────────────
    gy = 96
    f.append(text(x0, gy - 30, "прокладку гойдає", size=13, bold=True,
                  anchor="start", color=INK))
    # у моменти денного піку — випирає назовні (угору, +)
    for cx in (tx(0.5), tx(1.5)):
        f.append(arrow(cx, gy + 4, cx, gy - 16, color=POS, sw=2.2))
    # нічний мінімум — вдавлює (вниз, −)
    for cx in (tx(0.0), tx(1.0), tx(2.0)):
        f.append(arrow(cx, gy - 16, cx, gy + 4, color=NEG, sw=2.2))
    # смуга гуми
    f.append(rect(x0, gy + 6, span, 12, fill="#e6ddc9", stroke=INK, sw=1.5, rx=3))
    f.append(text(x1 + 8, gy + 16, "гума", size=11, anchor="start", color=MUTED))

    # ── Ярус 2 (середина): перепад тиску ΔP, синусоїда зі зміною знаку ──────
    py = 214
    amp = 44
    f.append(text(x0, py - amp - 16, "перепад тиску ΔP", size=13, bold=True,
                  anchor="start", color=INK))
    # нульова лінія
    f.append(line(x0, py, x1, py, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(x1 + 8, py + 4, "0", size=11, anchor="start", color=MUTED))
    # синусоїда тиску: удень (+) назовні, уночі (−) всередину
    n = 120
    pts = []
    for i in range(n + 1):
        u = 2.0 * i / n
        yy = py - amp * math.sin(2 * math.pi * (u - 0.25))   # пік удень
        pts.append("%.1f,%.1f" % (tx(u), yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), POS))
    f.append(text(tx(0.5), py - amp - 6, "+ випирає назовні", size=11, color=POS))
    f.append(text(tx(1.0), py + amp + 16, "− вдавлює всередину", size=11, color=NEG))

    # ── Ярус 3 (низ): температура корпусу, добова хвиля ─────────────────────
    ty = 352
    tamp = 40
    f.append(text(x0, ty - tamp - 16, "температура корпусу", size=13, bold=True,
                  anchor="start", color=INK))
    ptsT = []
    for i in range(n + 1):
        u = 2.0 * i / n
        yy = ty - tamp * math.sin(2 * math.pi * (u - 0.25))
        ptsT.append("%.1f,%.1f" % (tx(u), yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(ptsT), "#e08a1e"))
    # позначки день/ніч під віссю
    for u, lab, col in ((0.5, "день", POS), (1.0, "ніч", NEG),
                        (1.5, "день", POS), (2.0, "ніч", NEG)):
        f.append(text(tx(u), ty + tamp + 18, lab, size=11, color=col))

    # тонкі напрямні, що зшивають три яруси в моменти піків
    for u in (0.5, 1.0, 1.5, 2.0):
        f.append(line(tx(u), gy + 22, tx(u), ty - tamp - 2, color="#e2e2e2", sw=1))

    # мораль
    b, w, h = textbox(W / 2, 444,
                      "знак міняється щодоби → тисячі циклів → втома ущільнення",
                      size=13, bold=True, fill="#fff8e1", stroke="#c9a227")
    f.append(b)

    render(os.path.join(OUT, 'pressure-cycle.svg'), W, H, *f,
           title="Добовий цикл гойдає прокладку в обидва боки")


# ── Detailed: реальна апаратура IP-тесту (щуп · камера · сопло · бак) ────────
def fig_ip_test_apparatus():
    W, H = 860, 470
    f = []
    f.append(text(W / 2, 26, "Що насправді робить лабораторія: чотири машини IP-тесту",
                  size=17, bold=True))

    # чотири колонки-панелі, широкі, з великим зазором, щоб написи не стикались
    cols = [80, 285, 490, 695]   # ліві межі панелей
    pw, ph = 165, 250            # розмір панелі
    ptop = 70

    def panel(x, head, sub, col):
        f.append(rect(x, ptop, pw, ph, fill="#f7f9fb", stroke=INK, sw=1.8))
        b, w, h = textbox(x + pw / 2, ptop + 20, head, size=13, bold=True,
                          color=col, stroke=col, fill="#ffffff", min_w=pw - 10)
        f.append(b)
        return

    # 1) щуп-палець
    x = cols[0]
    panel(x, "щуп (доступ)", "", FIELD)
    # рука-щуп: горизонтальний стрижень тицяє в отвір стінки
    f.append(rect(x + pw - 34, ptop + 90, 34, 46, fill="#e6ddc9", stroke=INK, sw=1.8))  # стінка
    f.append(rect(x + pw - 34 + 12, ptop + 104, 22, 18, fill="#fff", stroke=INK, sw=1.5))  # отвір
    f.append(line(x + 20, ptop + 113, x + pw - 34 + 10, ptop + 113, color=INK, sw=4))     # щуп
    f.append(circle(x + 20, ptop + 113, 5, fill=INK, stroke=INK))
    f.append(text(x + pw / 2, ptop + 160, "палець Ø12.5", size=11, color=INK))
    f.append(text(x + pw / 2, ptop + 178, "дріт Ø1.0", size=11, color=INK))
    b, w, h = textbox(x + pw / 2, ptop + 214, "цифра 1…4:\nне дістати\nдо струму", size=11,
                      color=FIELD, stroke=FIELD, fill="#eafaf0", min_w=pw - 16)
    f.append(b)

    # 2) пилова камера
    x = cols[1]
    panel(x, "пилова камера", "", POS)
    f.append(rect(x + 24, ptop + 92, pw - 48, 74, fill="#efe7d0", stroke=INK, sw=1.8))
    # хмара пилу — крапки
    import random as _r
    _r.seed(3)
    for _ in range(26):
        dx = x + 30 + _r.random() * (pw - 60)
        dy = ptop + 98 + _r.random() * 62
        f.append(circle(dx, dy, 1.6, fill=MUTED, stroke=MUTED, sw=0.5))
    # виріб усередині
    f.append(rect(x + pw / 2 - 22, ptop + 118, 44, 26, fill="#eafaf0", stroke=FIELD, sw=1.5))
    # стрілка відкачування вниз
    f.append(arrow(x + pw / 2, ptop + 168, x + pw / 2, ptop + 190, color=NEG, sw=2.2))
    f.append(text(x + pw / 2, ptop + 204, "відкачують →", size=10, color=NEG))
    f.append(text(x + pw / 2, ptop + 218, "розрідження", size=10, color=NEG))
    b, w, h = textbox(x + pw / 2, ptop + 238, "5…6: тальк, 8 год", size=10,
                      color=POS, stroke=POS, fill="#fdecea", min_w=pw - 16)
    f.append(b)

    # 3) сопло-струмінь
    x = cols[2]
    panel(x, "сопло (струмінь)", "", NEG)
    # сопло зліва, струмінь у виріб справа
    f.append(rect(x + 16, ptop + 108, 22, 14, fill="#cfd8e3", stroke=INK, sw=1.6))  # сопло
    for k in range(6):
        yy = ptop + 111 + k * 2.2 - 5
        f.append(line(x + 38, ptop + 115, x + pw - 46, ptop + 115, color=NEG, sw=1.2))
    f.append(arrow(x + 40, ptop + 115, x + pw - 44, ptop + 115, color=NEG, sw=2.4))
    f.append(rect(x + pw - 42, ptop + 96, 30, 40, fill="#eafaf0", stroke=FIELD, sw=1.5))
    f.append(text(x + pw / 2, ptop + 158, "Ø6.3: 12.5 л/хв", size=10, color=INK))
    f.append(text(x + pw / 2, ptop + 176, "Ø12.5: 100 л/хв", size=10, color=INK))
    b, w, h = textbox(x + pw / 2, ptop + 214, "5…6: удар\nу точку\n≈90 кПа", size=11,
                      color=NEG, stroke=NEG, fill="#eaf0fd", min_w=pw - 16)
    f.append(b)

    # 4) бак-занурення
    x = cols[3]
    panel(x, "бак (занурення)", "", NEG)
    # вода
    f.append(rect(x + 20, ptop + 96, pw - 40, 96, fill="#dceafc", stroke=NEG, sw=1.6))
    # хвиляста поверхня
    f.append(line(x + 20, ptop + 96, x + pw - 20, ptop + 96, color=NEG, sw=2))
    # виріб під водою
    f.append(rect(x + pw / 2 - 20, ptop + 140, 40, 26, fill="#eafaf0", stroke=FIELD, sw=1.5))
    # мітки глибин
    f.append(line(x + 26, ptop + 96, x + 26, ptop + 140, color=INK, sw=1, dash="3 3"))
    f.append(text(x + 40, ptop + 120, "верх ≥0.15", size=9, color=INK, anchor="start"))
    f.append(text(x + pw / 2, ptop + 208, "дно 1 м, 30 хв", size=10, color=INK))
    b, w, h = textbox(x + pw / 2, ptop + 238, "7: ≈10 кПа рівно", size=10,
                      color=NEG, stroke=NEG, fill="#eaf0fd", min_w=pw - 16)
    f.append(b)

    # нижня мораль
    b, w, h = textbox(W / 2, ptop + ph + 40,
                      "цифра IP = який іспит склали;  «X» = іспит не проводили",
                      size=13, bold=True, fill="#fff8e1", stroke="#c9a227")
    f.append(b)

    render(os.path.join(OUT, 'ip-test-apparatus.svg'), W, H, *f, title=None)


# ── Detailed: чому 7 не покриває 6 — занурення проти струменя ────────────────
def fig_jet_vs_immersion():
    W, H = 800, 440
    f = []
    f.append(text(W / 2, 26, "Чому «7» не покриває «6»: рівний тиск проти удару в точку",
                  size=17, bold=True))

    # ── ЛІВОРУЧ: занурення (рівномірно, самоенергує) ──
    lx = 200
    f.append(text(lx, 62, "ЗАНУРЕННЯ (7)", size=14, bold=True, color=NEG))
    # виріб
    bw, bh = 150, 96
    f.append(rect(lx - bw / 2, 100, bw, bh, fill="#eafaf0", stroke=FIELD, sw=2))
    # стрілки тиску звідусіль, рівномірні, короткі, всередину
    import math as _m
    cx, cy = lx, 100 + bh / 2
    for ang in range(0, 360, 30):
        rad = _m.radians(ang)
        ox = cx + _m.cos(rad) * 108
        oy = cy + _m.sin(rad) * 74
        ix = cx + _m.cos(rad) * (bw / 2 + 6) if abs(_m.cos(rad)) > 0.01 else cx
        iy = cy + _m.sin(rad) * (bh / 2 + 6)
        # обмежимо кінець стрілки краєм прямокутника грубо
        f.append(arrow(ox, oy, cx + _m.cos(rad) * (bw / 2 - 4),
                       cy + _m.sin(rad) * (bh / 2 - 4), color=NEG, sw=1.7))
    b, w, h = textbox(lx, 240, "≈10 кПа рівномірно,\nсталий, звідусіль", size=12,
                      color=NEG, stroke=NEG, fill="#eaf0fd", min_w=210)
    f.append(b)
    b, w, h = textbox(lx, 300, "тиск ПРИТИСКАЄ\nущільнення →\nсамоенергування", size=12,
                      bold=True, color=FIELD, stroke=FIELD, fill="#eafaf0", min_w=210)
    f.append(b)

    # ── ПРАВОРУЧ: струмінь (у точку, задирає край) ──
    rx = 600
    f.append(text(rx, 62, "СТРУМІНЬ (6)", size=14, bold=True, color=POS))
    f.append(rect(rx - bw / 2, 100, bw, bh, fill="#eafaf0", stroke=FIELD, sw=2))
    # одна товста стрілка б'є в один кут
    f.append(rect(rx - bw / 2 - 60, 108, 20, 12, fill="#cfd8e3", stroke=INK, sw=1.5))  # сопло
    f.append(arrow(rx - bw / 2 - 38, 114, rx - bw / 2 + 6, 118, color=POS, sw=3.2))
    # «бризки» в точці удару
    for a in (-40, -20, 20, 40):
        rad = _m.radians(a)
        f.append(line(rx - bw / 2 + 6, 118, rx - bw / 2 + 6 + _m.cos(rad) * 22,
                      118 + _m.sin(rad) * 22, color=NEG, sw=1.3))
    # задертий край (червона дужка на куті)
    f.append(line(rx - bw / 2, 100, rx - bw / 2 - 8, 92, color=POS, sw=3))
    f.append(text(rx - bw / 2 - 4, 84, "край ↑", size=11, color=POS, bold=True))
    b, w, h = textbox(rx, 240, "≈90 кПа у ТОЧКУ,\nдинамічний напір ½ρv²", size=12,
                      color=POS, stroke=POS, fill="#fdecea", min_w=230)
    f.append(b)
    b, w, h = textbox(rx, 300, "тиск ЗАДИРАЄ край\nущільнення →\nшукає щілину", size=12,
                      bold=True, color=POS, stroke=POS, fill="#fdecea", min_w=230)
    f.append(b)

    # мораль
    b, w, h = textbox(W / 2, 400,
                      "струмінь б'є в ~9× сильніше й локально — тому «7» не гарантує «6»",
                      size=13, bold=True, fill="#fff8e1", stroke="#c9a227")
    f.append(b)

    render(os.path.join(OUT, 'jet-vs-immersion.svg'), W, H, *f, title=None)


# ── Detailed: ущільнення — стиснення, дві геометрії, самоенергування ─────────
def fig_gasket_squeeze():
    W, H = 840, 400
    f = []
    f.append(text(W / 2, 26, "Ущільнення як пружна машина: стиснути 15…30%, лишити місце",
                  size=17, bold=True))

    panels = [80, 370, 600]   # ліві межі трьох панелей (третя ширша)

    # ── Панель 1: торцевий затиск ──
    x = panels[0]
    f.append(text(x + 105, 62, "торцевий (згори)", size=13, bold=True, color=INK))
    # нижня посадка
    f.append(rect(x + 20, 170, 190, 22, fill="#cfd8e3", stroke=INK, sw=1.8))
    # канавка в посадці
    f.append(rect(x + 90, 150, 50, 22, fill="#ffffff", stroke=INK, sw=1.5))
    # розплющене кільце (еліпс) у канавці, ширше за канавку — стиснуте
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="26" ry="13" fill="#e6ddc9" stroke="%s" stroke-width="1.8"/>'
             % (x + 115, 161, POS))
    # кришка згори тисне
    f.append(rect(x + 20, 116, 190, 20, fill="#cfd8e3", stroke=INK, sw=1.8))
    f.append(arrow(x + 115, 100, x + 115, 114, color=NEG, sw=2.4))
    f.append(text(x + 115, 92, "притиск ↓", size=11, color=NEG))
    f.append(text(x + 115, 210, "розплющене кільце", size=10, color=POS))
    b, w, h = textbox(x + 115, 245, "стиск уздовж\nосі закриття", size=11,
                      color=INK, stroke="#d9c27a", fill="#fffdf3", min_w=175)
    f.append(b)

    # ── Панель 2: радіальний затиск ──
    x = panels[1]
    f.append(text(x + 100, 62, "радіальний (збоку)", size=13, bold=True, color=INK))
    # зовнішня деталь (циліндр) — дві вертикальні стінки
    f.append(rect(x + 30, 100, 22, 110, fill="#cfd8e3", stroke=INK, sw=1.8))
    f.append(rect(x + 150, 100, 22, 110, fill="#cfd8e3", stroke=INK, sw=1.8))
    # внутрішня деталь між ними
    f.append(rect(x + 70, 100, 62, 110, fill="#e8eef4", stroke=INK, sw=1.5))
    # кільце обтиснуте збоку (еліпс, витягнутий вертикально) в зазорі зліва
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="11" ry="24" fill="#e6ddc9" stroke="%s" stroke-width="1.8"/>'
             % (x + 61, 155, POS))
    f.append(arrow(x + 40, 155, x + 52, 155, color=NEG, sw=2.2))
    f.append(text(x + 101, 226, "обтиск упоперек", size=10, color=INK))
    b, w, h = textbox(x + 101, 258, "внутрішня деталь\nвходить у зовнішню", size=11,
                      color=INK, stroke="#d9c27a", fill="#fffdf3", min_w=185)
    f.append(b)

    # ── Панель 3: самоенергування ──
    x = panels[2]
    f.append(text(x + 100, 62, "тиск води ПОМАГАЄ", size=13, bold=True, color=FIELD))
    # посадка + канавка
    f.append(rect(x + 20, 170, 190, 22, fill="#cfd8e3", stroke=INK, sw=1.8))
    f.append(rect(x + 90, 148, 54, 24, fill="#ffffff", stroke=INK, sw=1.5))
    # кільце, притиснуте в дальній кут канавки
    f.append(circle(x + 130, 160, 13, fill="#e6ddc9", stroke=POS, sw=1.8))
    # вода тисне з лівого боку канавки
    f.append(arrow(x + 84, 160, x + 112, 160, color=NEG, sw=2.6))
    f.append(text(x + 74, 144, "вода →", size=11, color=NEG, bold=True))
    # реакція: кільце тисне на посадку (стрілка вниз від кільця)
    f.append(arrow(x + 130, 168, x + 130, 186, color=FIELD, sw=2.4))
    f.append(text(x + 168, 182, "тисне на\nпосадку", size=10, color=FIELD, anchor="start"))
    b, w, h = textbox(x + 100, 232, "більший тиск →\nщільніший затиск", size=11,
                      bold=True, color=FIELD, stroke=FIELD, fill="#eafaf0", min_w=195)
    f.append(b)

    # мораль
    b, w, h = textbox(W / 2, 372,
                      "у закритій канавці з місцем для розтікання; занурення — на руку, струмінь — ні",
                      size=12, bold=True, fill="#fff8e1", stroke="#c9a227")
    f.append(b)

    render(os.path.join(OUT, 'gasket-squeeze.svg'), W, H, *f, title=None)


# ── Detailed: передавальність — резонанс і зсув частоти амортизаторами ───────
def fig_vibration_resonance():
    import math
    W, H = 820, 470
    f = []
    f.append(text(W / 2, 26, "Вібрація вбиває резонансом: на власній частоті тряска × Q",
                  size=17, bold=True))

    # осі
    ox, oy = 96, 350           # початок координат (лівий-нижній)
    ax_w, ax_h = 620, 250      # довжина осей
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))            # X
    f.append(arrow(ox + ax_w - 2, oy, ox + ax_w + 18, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))           # Y
    f.append(arrow(ox, oy - ax_h + 2, ox, oy - ax_h - 18, color=INK, sw=2))
    f.append(text(ox + ax_w + 6, oy + 22, "частота тряски", size=12, anchor="end"))
    f.append(mtext(ox - 8, oy - ax_h - 8, ["передавальність", "(× разів)"], size=12, anchor="middle"))

    # рівень «1» (передавальність = 1)
    y1 = oy - 60
    f.append(line(ox, y1, ox + ax_w, y1, color=MUTED, sw=1.2, dash="5 4"))
    f.append(text(ox - 8, y1 + 4, "1", size=12, anchor="end", color=MUTED))

    # крива жорсткої плати: пік Q на fn
    fn_x = ox + ax_w * 0.60          # власна частота (пік)
    peak_y = oy - ax_h + 20          # висота піку (великий Q)

    def transmiss(fr, fn, Q):
        # стандартна передавальність з в'язким демпфуванням
        r = fr / fn
        zeta = 1.0 / (2 * Q)
        num = math.sqrt(1 + (2 * zeta * r) ** 2)
        den = math.sqrt((1 - r * r) ** 2 + (2 * zeta * r) ** 2)
        return num / den

    def curve(fn_frac, Q, color, sw, dash=None):
        fn = ax_w * fn_frac
        pts = []
        for i in range(1, 240):
            fr = ax_w * i / 240.0
            T = transmiss(fr, fn, Q)
            # масштаб: T=1 -> y1; логарифмічно-ish за висотою, обрізаємо
            yy = y1 - (min(T, 12.0) - 1) * ((y1 - peak_y) / (12.0 - 1))
            pts.append("%.1f,%.1f" % (ox + fr, yy))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (" ".join(pts), color, sw, d))

    # жорстка плата: fn на 0.60, Q високий
    f.append(curve(0.60, 9, POS, 2.8))
    # позначка fn і піку
    f.append(line(fn_x, oy, fn_x, peak_y + 6, color=POS, sw=1, dash="3 3"))
    f.append(text(fn_x, oy + 20, "fₙ (плата)", size=11, color=POS))
    f.append(text(fn_x + 8, peak_y + 4, "пік = Q (×20…40)", size=11, color=POS, anchor="start"))

    # плата на амортизаторах: fn зсунута вліво (0.28), Q малий -> нижчий ширший пік
    f.append(curve(0.28, 2.2, FIELD, 2.6, dash="7 4"))
    fn2 = ox + ax_w * 0.28
    f.append(text(fn2 - 4, oy + 20, "fₙ (на аморт.)", size=11, color=FIELD, anchor="middle"))

    # смуга частот мотора
    m_lo, m_hi = ox + ax_w * 0.50, ox + ax_w * 0.72
    f.append(rect(m_lo, oy - ax_h - 2, m_hi - m_lo, ax_h + 2, fill="#c0392b", stroke="none", sw=0))
    # напівпрозоро зробимо через тонку заливку-опаситість неможливо у нашому kit;
    # тому натомість позначимо смугу двома лініями й підписом угорі
    f.append(rect(m_lo, oy - ax_h - 2, m_hi - m_lo, ax_h + 2, fill="#fdecea", stroke="#e6b0aa", sw=1))
    f.append(text((m_lo + m_hi) / 2, oy - ax_h - 8, "частоти мотора", size=11, color=POS))

    # перемалюємо криві поверх смуги (щоб не сховались під заливкою)
    f.append(curve(0.60, 9, POS, 2.8))
    f.append(curve(0.28, 2.2, FIELD, 2.6, dash="7 4"))

    # зони: спад = ізоляція (праворуч від fn*sqrt2)
    iso_x = ox + ax_w * 0.60 * 1.414
    f.append(text(iso_x + 40, y1 - 8, "зона ізоляції (<1)", size=11, color=NEG))

    # мораль
    b, w, h = textbox(W / 2, 438,
                      "жорсткість задирає fₙ вгору, амортизатори — вниз; головне: не стояти піком у смузі мотора",
                      size=12, bold=True, fill="#fff8e1", stroke="#c9a227")
    f.append(b)

    render(os.path.join(OUT, 'vibration-resonance.svg'), W, H, *f, title=None)


if __name__ == '__main__':
    fig_three_jobs()
    fig_ip_decoder()
    fig_breathing_box()
    fig_vent_pore()
    fig_vent_mount()
    fig_ip_history()
    fig_pressure_cycle()
    fig_ip_test_apparatus()
    fig_jet_vs_immersion()
    fig_gasket_squeeze()
    fig_vibration_resonance()
    print("figures written to", OUT)
