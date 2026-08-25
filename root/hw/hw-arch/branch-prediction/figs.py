# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_guess():
    """Чому доводиться вгадувати: гілка ще не розв'язана, а адресу наступної
    вибірки треба назвати вже цього такту."""
    W, H = 720, 340
    els = []
    els.append(text(W/2, 28, "Гілка ще в конвеєрі — а куди вибирати далі?", size=17, bold=True))

    # горизонтальний конвеєр: 5 стадій, у другій сидить BNE
    stages = ["Вибірка", "Декод", "Вик", "Пам'ять", "Запис"]
    x0, y0, bw, bh, gap = 40, 70, 120, 46, 8
    for i, s in enumerate(stages):
        x = x0 + i*(bw+gap)
        fill = "#fff4e6" if i == 2 else FILL
        els.append(fitbox(x, y0, bw, bh, s, size=13, fill=fill))
    # де сидить гілка і де розкривається напрям
    els.append(text(x0 + 0.5*(bw+gap) + bw/2, y0-8, "тут гілка BNE", size=11, color=NEG))
    xr = x0 + 2*(bw+gap) + bw/2
    els.append(text(xr, y0-8, "напрям відомий аж тут", size=11, color=POS))
    els.append(line(xr, y0+bh, xr, y0+bh+18, color=POS, sw=1.5, dash="3 3"))

    # блок вибірки мусить назвати адресу ЗАРАЗ
    fx, fy = x0, y0
    els.append(text(fx+bw/2, y0+bh+44, "?", size=30, color=POS, bold=True))
    els.append(text(fx+bw/2, y0+bh+66, "яку адресу", size=11, color=MUTED))
    els.append(text(fx+bw/2, y0+bh+80, "брати цього такту?", size=11, color=MUTED))

    # дві можливі цілі
    ty = 240
    b1 = fitbox(60, ty, 260, 62,
                "НЕ стрибнули → наступна за порядком\n(адреса гілки + розмір команди)",
                size=12, fill="#eaf0fd", stroke=NEG)
    b2 = fitbox(400, ty, 260, 62,
                "СТРИБНУЛИ → ціль стрибка\n(куди веде мітка гілки)",
                size=12, fill="#fdecea", stroke=POS)
    els.append(b1); els.append(b2)
    els.append(arrow(fx+bw/2, y0+bh+86, 150, ty-6, color=NEG, sw=1.6))
    els.append(arrow(fx+bw/2, y0+bh+86, 500, ty-6, color=POS, sw=1.6))

    els.append(text(W/2, 322,
                    "Чекати з вибіркою — конвеєр спорожніє. Тому процесор мусить ОБРАТИ наперед — тобто вгадати.",
                    size=12, color=INK))
    render(os.path.join(OUT, "guess.svg"), W, H, *els)


def fig_counter():
    """Двобітний насичувальний лічильник: 4 стани, перехід за фактичним
    результатом гілки."""
    W, H = 720, 300
    els = []
    els.append(text(W/2, 28, "Двобітний лічильник: одна хиба ще не збиває передбачення", size=16, bold=True))

    states = [
        ("00", "сильно\nНЕ стрибати", NEG, "#eaf0fd"),
        ("01", "слабко\nНЕ стрибати", NEG, "#f4f6f8"),
        ("10", "слабко\nстрибати", POS, "#f7f7f7"),
        ("11", "сильно\nстрибати", POS, "#fdecea"),
    ]
    n = len(states)
    bw, bh = 130, 74
    gap = (W - 40 - n*bw) / (n-1)
    y = 90
    cx = []
    for i, (code, label, col, fill) in enumerate(states):
        x = 20 + i*(bw+gap)
        els.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=2))
        els.append(text(x+bw/2, y+22, code, size=18, color=col, bold=True))
        els.append(mtext(x+bw/2, y+42, label, size=11, color=INK))
        cx.append(x+bw/2)

    # позначка: ліва половина = передбачаємо «ні», права = «так»
    els.append(line(W/2, y-14, W/2, y+bh+14, color=MUTED, sw=1, dash="4 4"))
    els.append(text((cx[0]+cx[1])/2, y-20, "передбачаємо: НЕ стрибати", size=11, color=NEG))
    els.append(text((cx[2]+cx[3])/2, y-20, "передбачаємо: стрибати", size=11, color=POS))

    # переходи «стрибнули» (вправо, вгорі) — червоні
    yt = y - 2
    for i in range(n-1):
        els.append(arrow(cx[i]+bw/2-6, yt, cx[i+1]-bw/2+6, yt, color=POS, sw=1.6))
    els.append(text(W/2, yt-2, "гілка СТРИБНУЛА →", size=11, color=POS))
    # насичення справа
    els.append('<path d="M %.1f %.1f a 16 12 0 1 1 0.1 0" fill="none" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>' % (cx[3]+bw/2-10, yt-2, POS))

    # переходи «не стрибнули» (вліво, знизу) — сині
    yb = y + bh + 2
    for i in range(n-1, 0, -1):
        els.append(arrow(cx[i]-bw/2+6, yb, cx[i-1]+bw/2-6, yb, color=NEG, sw=1.6))
    els.append(text(W/2, yb+18, "← гілка НЕ стрибнула", size=11, color=NEG))
    els.append('<path d="M %.1f %.1f a 16 12 0 1 0 -0.1 0" fill="none" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>' % (cx[0]-bw/2+10, yb+2, NEG))

    els.append(text(W/2, H-16,
                    "Стрибок штовхає стан праворуч, відсутність — ліворуч. Щоб перекинути передбачення, гілці треба схибити ДВІЧІ поспіль.",
                    size=11, color=INK))
    render(os.path.join(OUT, "counter.svg"), W, H, *els)


def fig_flow():
    """Цикл передбачення: вгадав напрям і ціль → мчиш далі; схибив → викид і навчання."""
    W, H = 700, 360
    els = []
    els.append(text(W/2, 28, "Життєвий цикл передбачення переходу", size=17, bold=True))

    b = []
    b.append(fitbox(250, 52, 200, 48, "гілка на вибірці", size=13, fill=FILL))
    b.append(fitbox(210, 128, 280, 52,
                    "таблиця лічильників + BTB:\nнапрям? ціль?", size=12, fill="#fff4e6"))
    b.append(fitbox(230, 210, 240, 46, "вибираємо звідти наперед\n(спекулятивно)", size=12, fill=FILL))
    b.append(fitbox(250, 288, 200, 46, "гілка розв'язалась —\nвгадали?", size=12, fill=FILL))
    for e in b:
        els.append(e)
    els.append(arrow(350, 100, 350, 126, sw=1.6))
    els.append(arrow(350, 180, 350, 208, sw=1.6))
    els.append(arrow(350, 256, 350, 286, sw=1.6))

    # ліворуч — влучив
    hit = fitbox(20, 250, 190, 66,
                 "ВЛУЧИЛИ\nпотік не рвався,\nштраф = 0", size=12, fill="#eafaf1", stroke=FIELD)
    els.append(hit)
    els.append(arrow(250, 311, 212, 300, color=FIELD, sw=1.8))
    els.append(text(224, 292, "так", size=11, color=FIELD))

    # праворуч — промах
    miss = fitbox(490, 250, 190, 66,
                  "ПРОМАХ\nвикид конвеєра,\nштраф = глибина", size=12, fill="#fdecea", stroke=POS)
    els.append(miss)
    els.append(arrow(450, 311, 490, 300, color=POS, sw=1.8))
    els.append(text(474, 292, "ні", size=11, color=POS))

    # обидва навчають таблицю
    els.append('<path d="M 585 250 C 600 150 560 128 490 140" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 4" marker-end="url(#arrow)"/>' % MUTED)
    els.append('<path d="M 115 250 C 90 150 150 128 210 148" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 4" marker-end="url(#arrow)"/>' % MUTED)
    els.append(text(350, 116, "оновити лічильник (навчання)", size=10, color=MUTED))

    render(os.path.join(OUT, "flow.svg"), W, H, *els)


def fig_mask():
    """Безгілковий вибір: прапорець 0/1 → маска -(cond) → вибір AND/OR,
    без жодного стрибка."""
    W, H = 720, 360
    els = []
    els.append(text(W/2, 28, "Гілку замінює маска: порахувати обидва, вибрати арифметикою", size=15, bold=True))

    # верх: дві гілки прапорця
    els.append(fitbox(60, 60, 180, 44, "порівняння\nv > thr", size=13, fill=FILL))
    # права: cond=1
    els.append(fitbox(300, 52, 150, 30, "прапорець = 1", size=12, fill="#fdecea", stroke=POS))
    els.append(fitbox(300, 92, 150, 30, "прапорець = 0", size=12, fill="#eaf0fd", stroke=NEG))
    els.append(arrow(240, 74, 298, 67, sw=1.5))
    els.append(arrow(240, 90, 298, 107, sw=1.5))

    # маски
    els.append(text(500, 52, "−(1) =", size=12, color=INK, anchor="start"))
    els.append(text(560, 52, "0xFFFF", size=13, color=POS, anchor="start", bold=True))
    els.append(text(620, 68, "усі одиниці", size=10, color=MUTED, anchor="start"))
    els.append(text(500, 106, "−(0) =", size=12, color=INK, anchor="start"))
    els.append(text(560, 106, "0x0000", size=13, color=NEG, anchor="start", bold=True))
    els.append(text(620, 122, "усі нулі", size=10, color=MUTED, anchor="start"))
    els.append(arrow(452, 67, 496, 48, color=POS, sw=1.4))
    els.append(arrow(452, 107, 496, 102, color=NEG, sw=1.4))

    # центр: формула вибору
    els.append(fitbox(150, 168, 420, 46,
                      "вибір = (a & маска)  |  (b & ~маска)", size=16, fill="#fff4e6"))

    # два підсумки
    els.append(fitbox(90, 250, 250, 60,
                      "маска = 0xFFFF (над порогом)\n→ вибір = a  (беремо thr)",
                      size=12, fill="#fdecea", stroke=POS))
    els.append(fitbox(380, 250, 250, 60,
                      "маска = 0x0000 (під порогом)\n→ вибір = b  (лишаємо v)",
                      size=12, fill="#eaf0fd", stroke=NEG))
    els.append(arrow(300, 214, 215, 248, color=POS, sw=1.5))
    els.append(arrow(420, 214, 505, 248, color=NEG, sw=1.5))

    els.append(text(W/2, 340,
                    "Обидва значення пораховані завжди, стрибка немає — час не залежить від того, який шлях правильний.",
                    size=11, color=INK))
    render(os.path.join(OUT, "mask.svg"), W, H, *els)


def fig_spectre():
    """Ланцюг Spectre v1: тренування → спекулятивне читання за межі →
    слід у кеші лишається попри відкат → час доступу видає байт."""
    W, H = 760, 420
    els = []
    els.append(text(W/2, 28, "Spectre v1: як здогад процесора зливає заборонений байт", size=16, bold=True))

    # 4 кроки в ряд
    steps = [
        ("1. Тренуємо", "багато разів годуємо\nгілку-перевірку\nЗАКОННИМ індексом", NEG, "#eaf0fd"),
        ("2. Мистрен", "підсовуємо ЗАВЕЛИКИЙ i;\nперевірка ще рахується,\nпередбачувач каже «читай»", POS, "#fdecea"),
        ("3. Спекуляція", "читання ЗА МЕЖІ →\nним індексуємо пробу\nprobe[secret*256]", POS, "#fff4e6"),
        ("4. Замір", "перевірка скасувала все,\nАЛЕ рядок проби гарячий —\nчас доступу видає байт", FIELD, "#eafaf1"),
    ]
    n = len(steps)
    bw, bh = 168, 100
    gap = (W - 30 - n*bw) / (n-1)
    y = 70
    cx = []
    for i, (title_s, body_s, col, fill) in enumerate(steps):
        x = 15 + i*(bw+gap)
        els.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=2))
        els.append(text(x+bw/2, y+22, title_s, size=13, color=col, bold=True))
        els.append(mtext(x+bw/2, y+42, body_s, size=10.5, color=INK))
        cx.append(x+bw/2)
        if i < n-1:
            els.append(arrow(x+bw+3, y+bh/2, x+bw+gap-3, y+bh/2, sw=1.8))

    # архітектурний VS мікроархітектурний стан
    yb = 220
    els.append(fitbox(60, yb, 300, 70,
                      "АРХІТЕКТУРНИЙ стан\n(регістри, пам'ять)\nвідкат чистить БЕЗДОГАННО",
                      size=12, fill="#eaf0fd", stroke=NEG))
    els.append(fitbox(400, yb, 300, 70,
                      "МІКРОАРХІТЕКТУРНИЙ стан\n(кеш) — слід ЛИШАЄТЬСЯ:\nвідкат його НЕ чистить",
                      size=12, fill="#fdecea", stroke=POS))
    els.append(text(210, yb-8, "що відкат стирає", size=11, color=NEG))
    els.append(text(550, yb-8, "чим тече витік", size=11, color=POS))

    # таймінг: холодні рядки vs один гарячий
    ty = 330
    els.append(text(W/2, ty-6, "Замір: 255 рядків проби холодні (доступ довгий), рівно 1 гарячий (короткий) — його номер = байт", size=11, color=INK))
    barx0, barw, barh = 60, 12, 34
    step = 13
    hot = 7  # який рядок гарячий (демонстративно)
    for k in range(48):
        x = barx0 + k*step
        if k == hot:
            els.append(rect(x, ty+8, barw, 12, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=2))
            els.append(text(x+barw/2, ty+8+barh+4, "↑", size=13, color=FIELD, bold=True))
            els.append(text(x+barw/2, ty+8+barh+18, "гарячий", size=9, color=FIELD))
        else:
            els.append(rect(x, ty+8, barw, barh, fill="#f4f6f8", stroke=MUTED, sw=1, rx=2))
    els.append(text(barx0 + 48*step + 34, ty+8+barh/2, "…256", size=10, color=MUTED, anchor="start"))

    els.append(text(W/2, H-12,
                    "Жодна складова не зламана — атака зводить докупи справні механізми. Тому діру не «полагодити», а лише обкласти латками.",
                    size=11, color=INK))
    render(os.path.join(OUT, "spectre-v1.svg"), W, H, *els)


def fig_history():
    """Хронологія передбачення: кожен крок родиться зі сліпоти попереднього —
    точність повзе вгору, а промахів меншає."""
    W, H = 760, 420
    els = []
    els.append(text(W/2, 26, "Сорок років гонитви за відсотками", size=17, bold=True))
    els.append(text(W/2, 45, "кожен крок лікує конкретну сліпоту попереднього", size=12, color=MUTED))

    steps = [
        ("статика", "~1970-ті", 50, "одне правило\nна всі гілки", MUTED, "#f4f6f8"),
        ("Сміт", "1981", 88, "2 біти: інерція\nпроти аномалій", NEG, "#eaf0fd"),
        ("Йех і Патт", "1991", 93, "контекст —\nісторія гілок", "#8e44ad", "#f3eafb"),
        ("gshare", "1993", 93, "XOR проти тісноти\n+ арбітр", FIELD, "#eafaf1"),
        ("TAGE", "2006", 96, "усі довжини\nісторії разом", POS, "#fdecea"),
    ]
    ax, ay, aw, ah = 74, 92, W-118, 190
    base = ay + ah
    for pct in (50, 75, 90, 100):
        gy = base - ah * (pct-40)/60.0
        els.append(line(ax, gy, ax+aw, gy, color="#e5e7eb", sw=1))
        els.append(text(ax-8, gy+4, "%d%%" % pct, size=10, color=MUTED, anchor="end"))

    n = len(steps)
    slot = aw / n
    bw = 76
    for i, (name, year, pct, fix, col, fill) in enumerate(steps):
        cx = ax + slot*i + slot/2
        h = ah * (pct-40)/60.0
        top = base - h
        els.append(rect(cx-bw/2, top, bw, h, fill=fill, stroke=col, sw=2))
        els.append(text(cx, top-9, "%d%%" % pct, size=13, color=col, bold=True))
        els.append(text(cx, top+16, name, size=11, color=INK, bold=True))
        els.append(text(cx, top+31, year, size=10, color=MUTED))
        els.append(mtext(cx, base+16, fix, size=9.5, color=MUTED))
        if i < n-1:
            nx = ax + slot*(i+1) + slot/2
            ny = base - ah*(steps[i+1][2]-40)/60.0
            els.append(arrow(cx+bw/2+2, top+2, nx-bw/2-2, ny+8, color="#c9ccd1", sw=1.4))

    els.append(text(ax, base+54, "Точність зростає скупо — але дивитись слід на ПРОМАХИ:", size=11, color=INK, anchor="start"))
    els.append(text(ax, base+70, "з 90% до 95% — це не «трохи краще», а вдвічі менше промахів (1 з 10 → 1 з 20).", size=11, color=INK, anchor="start"))
    render(os.path.join(OUT, "history.svg"), W, H, *els)


if __name__ == "__main__":
    fig_guess()
    fig_counter()
    fig_flow()
    fig_mask()
    fig_spectre()
    fig_history()
    print("figs done")
