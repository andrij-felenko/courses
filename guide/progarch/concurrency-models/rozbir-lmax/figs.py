# -*- coding: utf-8 -*-
"""Фігури для кроку «Розбір: LMAX Disruptor» (guide progarch / concurrency-models).
Вивід — ./img/*.svg. svgkit імпортуємо, не переписуємо."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

PURPLE = "#8e44ad"


def fig_cost_scale():
    """Логарифмічна шкала наближених витрат часу: корисна робота — на порядки
    дешевша за координацію (стрибок лінії кешу, замок, перемикання контексту).
    Ідея: LMAX прибирали не роботу, а координацію."""
    W, H = 940, 470
    els = []
    els.append(text(W / 2, 34, "Скільки коштує координація проти самої роботи (порядок величини)",
                    size=16, bold=True))

    x0 = 470            # початок стовпців = 1 нс
    dec = 112           # пікселів на декаду (×10)
    ytop = 92
    step = 58
    grid_bot = ytop + 5 * step - step + 40

    # --- вертикальна сітка декад ---
    for k, lab in enumerate(["1 нс", "10 нс", "100 нс", "1000 нс"]):
        gx = x0 + dec * k
        els.append(line(gx, ytop - 8, gx, grid_bot, color="#d9dee5", sw=1.2))
        els.append(text(gx, grid_bot + 20, lab, size=12, color=MUTED))

    bars = [
        ("влучення в L1-кеш", 1, MUTED),
        ("зіставити ордер — корисна робота", 50, FIELD),
        ("промах кешу → головна пам'ять", 100, MUTED),
        ("лінія кешу скаче між ядрами", 150, POS),
        ("захоплений замок / зміна контексту", 2000, POS),
    ]
    for i, (name, ns, col) in enumerate(bars):
        y = ytop + i * step
        length = max(9, dec * math.log10(ns))
        els.append(text(x0 - 22, y + 19, name, size=13, color=INK, anchor="end"))
        els.append(rect(x0, y, length, 28, fill=col, stroke=col, sw=1, rx=4))
        val = ("≈%d нс" % ns) if ns < 1000 else "≈2000 нс"
        els.append(text(x0 + length + 10, y + 19, val, size=12.5, color=col, anchor="start", bold=True))

    # --- легенда кольору ---
    ly = grid_bot + 48
    els.append(rect(x0 - 22 - 150, ly - 12, 16, 16, fill=FIELD, stroke=FIELD, sw=1, rx=3))
    els.append(text(x0 - 22 - 128, ly + 1, "корисна робота", size=12.5, color=INK, anchor="start"))
    els.append(rect(x0 + 40, ly - 12, 16, 16, fill=POS, stroke=POS, sw=1, rx=3))
    els.append(text(x0 + 62, ly + 1, "координація й трафік пам'яті", size=12.5, color=INK, anchor="start"))

    els.append(text(W / 2, H - 14,
                    "кожна декада праворуч — це ×10; координація коштує на порядки більше за роботу",
                    size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "cost-scale.svg"), W, H, *els)


def fig_two_designs():
    """Два проєкти біржі. Угорі — очевидний: багато потоків над спільною чергою
    й замком, конкуренція в серці. Унизу — інверсія LMAX: уся логіка на одному
    потоці, а приймання/журнал/репліка крутяться паралельно навколо."""
    W, H = 940, 620
    els = []
    els.append(text(W / 2, 30, "Та сама біржа, два проєкти: де живе конкуренція", size=16, bold=True))

    # ── Панель А: очевидний проєкт ──
    els.append(rect(28, 48, 884, 236, fill="#fbeceb", stroke="#e8b7b2", sw=1.4, rx=10))
    els.append(text(W / 2, 74, "Очевидний проєкт — конкуренція в самому серці", size=14, bold=True, color=POS))
    wcx = [180, 372, 564, 756]
    for i, cx in enumerate(wcx):
        els.append(fitbox(cx - 58, 96, 116, 40, "потік %d" % (i + 1), size=13, fill=BG, stroke=LINE, sw=1.5))
    # спільний ресурс
    els.append(fitbox(200, 208, 536, 46, "спільна черга · замок · спільна база даних",
                      size=13.5, fill="#f7d9d5", stroke=POS, sw=1.8, bold=True))
    for cx in wcx:
        els.append(arrow(cx, 138, cx, 206, color=POS, sw=1.8))
    # маркери конкуренції між потоками
    for a, b in zip(wcx, wcx[1:]):
        els.append(text((a + b) / 2, 122, "⇄", size=18, color=POS, bold=True))
    els.append(text(W / 2, 274, "усі пишуть в ті самі комірки → потоки більше домовляються, ніж працюють",
                    size=12, italic=True, color=MUTED))

    # ── Панель Б: інверсія LMAX ──
    els.append(rect(28, 300, 884, 296, fill="#eafaf0", stroke="#b6e2c6", sw=1.4, rx=10))
    els.append(text(W / 2, 326, "Інверсія LMAX — конкуренцію винесено на краї", size=14, bold=True, color=FIELD))

    yc = 384
    els.append(fitbox(48, yc - 22, 92, 44, "мережа", size=13, fill=BG, stroke=LINE, sw=1.5))
    els.append(fitbox(168, yc - 24, 132, 48, "вхідне\nбуфер-кільце", size=12.5, fill="#fff", stroke=NEG, sw=1.7))
    els.append(fitbox(336, yc - 34, 268, 68, "БІЗНЕС-ЛОГІКА\nодин потік · без замків",
                      size=14, fill="#fff7e6", stroke="#b8860b", sw=2.2, bold=True))
    els.append(fitbox(640, yc - 24, 132, 48, "вихідне\nбуфер-кільце", size=12.5, fill="#fff", stroke=NEG, sw=1.7))
    els.append(fitbox(806, yc - 22, 92, 44, "відповіді", size=13, fill=BG, stroke=LINE, sw=1.5))
    els.append(arrow(142, yc, 166, yc, color=INK, sw=1.8))
    els.append(arrow(302, yc, 334, yc, color=INK, sw=1.8))
    els.append(arrow(606, yc, 638, yc, color=INK, sw=1.8))
    els.append(arrow(774, yc, 804, yc, color=INK, sw=1.8))

    # паралельні споживачі вхідного кільця
    par = [(150, "приймання\n+ розбір"), (300, "журнал\nна диск"), (450, "реплікація")]
    for cx, lab in par:
        els.append(fitbox(cx - 66, 500, 132, 46, lab, size=12.5, fill=BG, stroke=FIELD, sw=1.6))
        els.append(line(cx, 500, 234, yc + 24, color=FIELD, sw=1.2, dash="5,3"))
    els.append(text(300, 570, "паралельні споживачі того самого кільця — кожен на своєму ядрі",
                    size=12, italic=True, color=MUTED))
    els.append(text(720, 470, "серце без жодного замка —", size=12, color=FIELD, bold=True))
    els.append(text(720, 488, "кеш гарячий, хід детермінований", size=12, color=FIELD, bold=True))
    render(os.path.join(IMG, "two-designs.svg"), W, H, *els)


def fig_ring_buffer():
    """Буфер-кільце: виробник опублікував до курсора, троє споживачів чагають за
    ним різним темпом. Бізнес-логіка тримається позаду журналу й репліки; проміжок
    між нею й курсором — пакет, який вона наздожене гуртом. Один лічильник, без замка."""
    W, H = 900, 660
    cx, cy, R, r = 322, 348, 208, 27
    els = []
    els.append(text(W / 2, 34, "Буфер-кільце: один лічильник узгоджує всіх — без замка", size=16, bold=True))

    n = 12
    def pos(i):
        a = math.radians(-90 + 30 * i)
        return cx + R * math.cos(a), cy + R * math.sin(a)

    # ролі на слотах (менший індекс = давніше; курсор найновіший)
    roles = {1: ("курсор виробника", POS),
             11: ("журнал", NEG),
             10: ("репліка", FIELD),
             9: ("бізнес-логіка", PURPLE)}

    # слоти
    for i in range(n):
        x, y = pos(i)
        col = roles[i][1] if i in roles else LINE
        sw = 3.2 if i in roles else 1.6
        els.append(circle(x, y, r, fill=BG, stroke=col, sw=sw))
        els.append(text(x, y + 5, str(i), size=13, color=INK, bold=(i in roles)))

    # підписи ролей — зовні кільця, з відступом
    lab = {1: (470, 150, "start"), 11: (232, 96, "middle"),
           10: (86, 214, "end"), 9: (70, 348, "end")}
    for i, (lx, ly, anc) in lab.items():
        name, col = roles[i]
        px, py = pos(i)
        els.append(circle(px + (r + 14) * math.cos(math.radians(-90 + 30 * i)),
                          py + (r + 14) * math.sin(math.radians(-90 + 30 * i)), 6,
                          fill=col, stroke=col, sw=1))
        els.append(text(lx, ly, name, size=13, color=col, anchor=anc, bold=True))

    # проміжок-пакет: хорда від бізнес-логіки до курсора
    bx, by = pos(9)
    ux, uy = pos(1)
    els.append(line(bx, by, ux, uy, color=PURPLE, sw=1.4, dash="6,4"))
    els.append(text(cx - 6, cy + 6, "проміжок = пакет", size=13, color=PURPLE, bold=True))
    els.append(text(cx - 6, cy + 26, "(відстав — наздожене гуртом)", size=11.5, color=MUTED))

    # праворуч — пояснення
    bx0 = 596
    els.append(fitbox(bx0, 232, 286, 150,
                      "усі читають ті самі комірки,\nстримувані лише номером\nпослідовності — без замка\n\n"
                      "бізнес-логіка діє на комірці,\nаж коли журнал і репліка\nвже її пройшли",
                      size=13, fill="#f4f6f8", stroke=LINE, sw=1.5))
    els.append(fitbox(bx0, 402, 286, 52,
                      "індекс = seq & (n − 1)\nрозмір n — степінь двійки",
                      size=13, fill="#eef2fb", stroke=NEG, sw=1.5))

    els.append(text(W / 2, H - 16,
                    "комірки виділено наперед і перевикористано — нуль виділень, нуль пауз збирача сміття",
                    size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "ring-buffer.svg"), W, H, *els)


def fig_birth_timeline():
    """Хронологія народження Disruptor (для вставки hist-lmax): від біржі ставок
    Betfair (2000) через запуск LMAX і перший показ на QCon (2010) до вибухового
    2011-го (стаття, відкритий код, нарис Фаулера, Duke's Choice) і далі — Aeron/
    Agrona. Кроки рівномірно за подіями, не в масштабі часу."""
    W, H = 1060, 500
    axis_y = 290
    els = []
    els.append(text(W / 2, 32, "Хронологія народження Disruptor", size=17, bold=True))
    els.append(text(W / 2, 54, "рівномірно за подіями — не в масштабі часу", size=12.5,
                    italic=True, color=MUTED))

    # горизонтальна вісь
    els.append(line(64, axis_y, 996, axis_y, color="#cfd6de", sw=2))

    ev = [
        ("2000",         "Betfair\nбіржа ставок",      NEG),
        ("2010",         "LMAX\nбіржа для FX/CFD",      NEG),
        ("лист. 2010",   "QCon SF\nперший показ",       FIELD),
        ("трав. 2011",   "стаття\n«Disruptor 1.0»",     FIELD),
        ("22 черв. 2011","відкритий код\nApache 2.0",   FIELD),
        ("12 лип. 2011", "Фаулер:\n6 млн ордерів/с",    FIELD),
        ("жовт. 2011",   "Duke's Choice\nAward",        FIELD),
        ("2014–15",      "Aeron · Agrona",              PURPLE),
    ]
    xs = [110 + i * 120 for i in range(8)]
    bw, bh = 150, 78
    for i, ((yr, desc, col), x) in enumerate(zip(ev, xs)):
        above = (i % 2 == 0)
        if above:
            els.append(text(x, 150, yr, size=13, bold=True, color=col))
            els.append(fitbox(x - bw / 2, 162, bw, bh, desc, size=13, fill=BG, stroke=col, sw=2))
            els.append(line(x, 240, x, axis_y - 8, color=col, sw=1.6))
        else:
            els.append(fitbox(x - bw / 2, 340, bw, bh, desc, size=13, fill=BG, stroke=col, sw=2))
            els.append(line(x, axis_y + 8, x, 340, color=col, sw=1.6))
            els.append(text(x, 436, yr, size=13, bold=True, color=col))
        els.append(circle(x, axis_y, 7, fill=col, stroke=col, sw=1))

    # легенда ер
    ly = 470
    for lx, col, lab in [(250, NEG, "коріння"), (520, FIELD, "вибух 2011"),
                         (790, PURPLE, "спадок")]:
        els.append(circle(lx - 12, ly - 4, 6, fill=col, stroke=col, sw=1))
        els.append(text(lx, ly, lab, size=12.5, color=INK, anchor="start"))
    render(os.path.join(IMG, "birth-timeline.svg"), W, H, *els)


def fig_lineage():
    """Родовід Disruptor «пісочним годинником» (для вставки hist-lmax): ліворуч
    сходяться причини (біржова ДНК Betfair/LMAX, вимір прототипу, механічна симпатія
    від Джекі Стюарта), у центрі — Disruptor, праворуч розходяться наслідки
    (Aeron, Agrona, спільнота Mechanical Sympathy)."""
    W, H = 1180, 470
    els = []
    els.append(text(W / 2, 34, "Родовід Disruptor: що влилося — і що з нього виросло",
                    size=17, bold=True))

    cxL, cxR = 170, 1010
    rows = [120, 235, 350]
    bw, bh = 250, 76
    cx0, cy0, cw, ch = 590, 235, 214, 92

    els.append(text(cxL, 78, "Що влилося", size=13.5, bold=True, color=NEG))
    els.append(text(cxR, 78, "Що виросло", size=13.5, bold=True, color=PURPLE))

    left = [
        "Спадок Betfair → LMAX\nбіржовий рушій для FX/CFD",
        "Вимір прототипу:\nчерги й актори домінують",
        "Механічна симпатія\n← сер Джекі Стюарт, Ф-1",
    ]
    right = [
        "Aeron\nтранспорт наднизької затримки",
        "Agrona\nвисокопродуктивні структури",
        "Спільнота Mechanical Sympathy\nблог і група в Google",
    ]

    # центр
    els.append(fitbox(cx0 - cw / 2, cy0 - ch / 2, cw, ch,
                      "Disruptor · 2011\nбуфер-кільце\nодин письменник",
                      size=14, fill="#fff7e6", stroke="#b8860b", sw=2.4, bold=True))

    # ліві причини → центр
    for s, cy in zip(left, rows):
        els.append(fitbox(cxL - bw / 2, cy - bh / 2, bw, bh, s, size=12.5,
                          fill=BG, stroke=NEG, sw=1.8))
        els.append(arrow(cxL + bw / 2 + 4, cy, cx0 - cw / 2 - 6, cy0, color=NEG, sw=1.7))

    # центр → праві наслідки
    for s, cy in zip(right, rows):
        els.append(fitbox(cxR - bw / 2, cy - bh / 2, bw, bh, s, size=12.5,
                          fill=BG, stroke=PURPLE, sw=1.8))
        els.append(arrow(cx0 + cw / 2 + 6, cy0, cxR - bw / 2 - 4, cy, color=PURPLE, sw=1.7))

    els.append(text(W / 2, H - 16,
                    "один вимір посередині виявився важчим за цілу усталену культуру черг",
                    size=12.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "lineage.svg"), W, H, *els)


def fig_wrap_protection():
    """Захист від перезапису при обгортанні (для вставки proj-ring-buffer).
    Послідовність монотонна; у масив із N=8 слотів згортається маскою seq&7.
    seq 10 і seq 2 падають в один слот 2 — перезаписати його можна лише коли
    стримувальна послідовність (споживач) пройшла seq 2 = 10 − N."""
    W, H = 1000, 500
    els = []
    els.append(text(W / 2, 32, "Обгортання: коли перезаписати слот безпечно", size=16, bold=True))
    els.append(text(W / 2, 54, "послідовність монотонна; у масив із N = 8 слотів згортаємо маскою seq & 7",
                    size=12.5, italic=True, color=MUTED))

    x0, cw = 92, 60
    ncells = 14
    top, ch = 178, 52

    def cx(i):
        return x0 + i * cw + cw / 2

    GATING, CURSOR, NEXTW, N = 2, 9, 10, 8

    # підписи рядків ліворуч
    els.append(text(x0 - 12, top + 30, "seq:", size=12.5, color=INK, anchor="end", bold=True))
    els.append(text(x0 - 12, top + ch + 22, "слот:", size=12, color=MUTED, anchor="end"))

    for i in range(ncells):
        x = x0 + i * cw
        if i <= GATING:
            fill, st, sw = "#eceff1", MUTED, 1.4
        elif i <= CURSOR:
            fill, st, sw = "#eafaf0", FIELD, 1.7
        elif i == NEXTW:
            fill, st, sw = "#fdecea", POS, 2.6
        else:
            fill, st, sw = BG, "#ccd2d8", 1.3
        els.append(rect(x, top, cw - 2, ch, fill=fill, stroke=st, sw=sw, rx=6))
        els.append(text(cx(i), top + 31, str(i), size=15, color=INK, bold=(i in (GATING, CURSOR, NEXTW))))
        els.append(text(cx(i), top + ch + 22, str(i & (N - 1)), size=12.5, color=MUTED))

    # «staple» — той самий слот для seq 2 і seq 10
    sy = 138
    els.append(line(cx(GATING), top - 5, cx(GATING), sy, color=POS, sw=1.8))
    els.append(line(cx(GATING), sy, cx(NEXTW), sy, color=POS, sw=1.8))
    els.append(arrow(cx(NEXTW), sy, cx(NEXTW), top - 7, color=POS, sw=1.8))
    els.append(text((cx(GATING) + cx(NEXTW)) / 2, sy - 12,
                    "той самий слот 2:  10 & 7 = 2 = 2 & 7", size=13, color=POS, bold=True))

    # мітки-покажчики під клітинами (стримувальна / курсор / next), рознесені
    els.append(circle(cx(GATING), top + ch + 44, 6, fill=NEG, stroke=NEG, sw=1))
    els.append(text(cx(GATING), top + ch + 66, "стримувальна", size=12, color=NEG, bold=True))
    els.append(text(cx(GATING), top + ch + 82, "споживач дійшов", size=11, color=MUTED))

    els.append(circle(cx(CURSOR), top + ch + 44, 6, fill=FIELD, stroke=FIELD, sw=1))
    els.append(text(cx(CURSOR) - 6, top + ch + 66, "курсор", size=12, color=FIELD, bold=True, anchor="end"))
    els.append(text(cx(CURSOR) - 6, top + ch + 82, "опубліковано", size=11, color=MUTED, anchor="end"))

    els.append(circle(cx(NEXTW), top + ch + 44, 6, fill=POS, stroke=POS, sw=1))
    els.append(text(cx(NEXTW) + 8, top + ch + 66, "next —", size=12, color=POS, bold=True, anchor="start"))
    els.append(text(cx(NEXTW) + 8, top + ch + 82, "пишемо", size=12, color=POS, bold=True, anchor="start"))

    # умова безпеки (нижче ряду міток, щоб не залазити на підписи)
    els.append(fitbox(x0 + 8 * cw, top + ch + 106, 232, 66,
                      "перезапис слота seq&7\nбезпечний лише коли\nstop ≥ seq − N",
                      size=12.5, fill="#eef2fb", stroke=NEG, sw=1.5))

    els.append(text(W / 2, H - 16,
                    "монотонні номери ніколи не збігаються — стан читається відніманням, а не позицією покажчика",
                    size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "wrap-protection.svg"), W, H, *els)


def fig_batch_hb():
    """Одне acquire робить видимим цілий пакет (для вставки proj-ring-buffer).
    Кожну публікацію замкнено бар'єром release; одне acquire на боці споживача
    тягне за собою всі записи слотів аж до курсора — бар'єр амортизовано на пакет."""
    W, H = 1020, 440
    els = []
    els.append(text(W / 2, 30, "Одне acquire робить видимим цілий пакет", size=16, bold=True))

    # ── виробник ──
    py = 168
    els.append(text(64, py - 4, "виробник", size=13, bold=True, color=INK, anchor="start"))
    els.append(arrow(150, py, 916, py, color=INK, sw=1.8))
    els.append(text(508, 84, "усі чотири записи слотів зроблено ДО публікації cursor = 8",
                    size=12.5, color=INK))
    xs = [258, 420, 582, 744]
    for k, x in zip(range(5, 9), xs):
        els.append(fitbox(x - 70, 96, 140, 34, "слот[%d] ← подія" % k, size=12,
                          fill="#eafaf0", stroke=FIELD, sw=1.6))
        els.append(line(x, 130, x, py - 8, color=FIELD, sw=1.2))
        els.append(circle(x, py, 7, fill=POS, stroke=POS, sw=1))
        els.append(text(x, py + 22, "cursor := %d" % k, size=11.5, color=POS, bold=True))
        els.append(text(x, py + 37, "(release)", size=10.5, color=MUTED))

    # ── споживач ──
    cy = 348
    els.append(text(64, cy - 4, "споживач", size=13, bold=True, color=INK, anchor="start"))
    els.append(arrow(150, cy, 916, cy, color=INK, sw=1.8))
    ax = 560
    els.append(circle(ax, cy, 7, fill=NEG, stroke=NEG, sw=1))
    els.append(fitbox(ax - 150, cy + 14, 210, 34, "available = cursor.load(acquire) → 8",
                      size=11, fill="#eaf0fd", stroke=NEG, sw=1.6))
    els.append(fitbox(670, cy - 46, 246, 32, "читаємо слоти 5..8 — звичайні читання",
                      size=11.5, fill=FILL, stroke=LINE, sw=1.4))
    els.append(line(ax, cy - 8, 700, cy - 14, color=NEG, sw=1.2, dash="4,3"))

    # synchronizes-with: остання публікація → acquire
    els.append(arrow(xs[3] + 6, py + 8, ax + 8, cy - 8, color=POS, sw=1.8))
    els.append(text(748, 262, "synchronizes-with", size=12, color=POS, bold=True, anchor="start"))

    els.append(text(W / 2, H - 14,
                    "ціну одного бар'єра розмазано на всю чергу — що більше відставання, то дешевша подія",
                    size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "batch-hb.svg"), W, H, *els)


if __name__ == "__main__":
    fig_cost_scale()
    fig_two_designs()
    fig_ring_buffer()
    fig_birth_timeline()
    fig_lineage()
    fig_wrap_protection()
    fig_batch_hb()
    print("OK: figures written to", IMG)
