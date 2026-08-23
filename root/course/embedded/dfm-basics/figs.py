# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: конвеєр складання, де кожен етап штампує своє правило ──────────
def fig_pipeline():
    W, H = 760, 388
    frags = []
    stages = [
        ("Друк пасти", "трафарет", ["апертура ≥ 4 мм²", "зазор між", "площадками"]),
        ("Розстановка", "автомат", ["орієнтир-мітки", "полярність", "видима"]),
        ("Оплавлення", "піч", ["симетрія тепла", "теплові", "відводи"]),
        ("Контроль", "камера (AOI)", ["видимі паяння", "тест-точки", "доступні"]),
    ]
    n = len(stages)
    bw, gap = 150, 24
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    ytop = 70
    bh = 66
    # стрічка-конвеєр одразу під блоками (плата їде по ній)
    belt_y = ytop + bh + 20
    frags.append(line(x0 - 10, belt_y, x0 + total + 10, belt_y, color=MUTED, sw=3))
    frags.append(text(W / 2, 40, "Плата йде конвеєром — кожна станція ставить свою вимогу до конструкції",
                      size=13, color=MUTED))
    # рядок правил — НИЖЧЕ стрічки, щоб лінія не різала написи
    rules_top = belt_y + 26
    for i, (name, sub, rules) in enumerate(stages):
        x = x0 + i * (bw + gap)
        frags.append(fitbox(x, ytop, bw, bh, name + "\n(" + sub + ")", size=14, bold=True,
                            fill="#eef2f7", stroke=INK, sw=1.6))
        # стрілка до наступного
        if i < n - 1:
            frags.append(arrow(x + bw + 3, ytop + bh / 2, x + bw + gap - 3, ytop + bh / 2, color=INK, sw=2))
        # «штамп» правила вниз — від стрічки до рамки правила
        frags.append(line(x + bw / 2, belt_y + 2, x + bw / 2, rules_top - 2, color=POS, sw=1.6, dash="4,4"))
        rule_txt = "\n".join(rules)
        frags.append(fitbox(x + 4, rules_top, bw - 8, 78, rule_txt, size=11,
                            fill="#fdecea", stroke=POS, sw=1.4))
    render(os.path.join(OUT, 'assembly-pipeline.svg'), W, H, *frags)


# ── Фігура 2: надгробок — теплова несиметрія й лікування тепловідводом ───────
def fig_tombstone():
    W, H = 760, 340
    frags = []
    frags.append(text(W / 2, 34, "Чому чип стає «надгробком» — і як це знімає тепловий відвід",
                      size=14, bold=True))

    y = 240          # рівень площадок для обох сцен
    pw_, ph_ = 40, 12
    gapp = 34        # проміжок між площадками (тіло компонента)

    # ── ЛІВОРУЧ (погано): ліва площадка на тонкій доріжці, права — на суцільній міді
    cxL = 150                       # центр лівої сцени (між площадками)
    lxa = cxL - gapp / 2 - pw_      # ліва площадка x
    rxa = cxL + gapp / 2            # права площадка x
    frags.append(text(cxL, 70, "Одна площадка на суцільній міді", size=12, color=POS, bold=True))
    # суцільна мідна заливка під правою площадкою
    frags.append(rect(rxa - 4, y - 6, 118, 58, fill="#f6d9b8", stroke="#b07a35", sw=1.2, rx=3))
    frags.append(text(rxa + 66, y + 44, "суцільна мідь", size=10, color="#8a5a1f"))
    # тонка доріжка до лівої
    frags.append(line(lxa, y + ph_ / 2, lxa - 34, y + ph_ / 2, color="#b07a35", sw=2))
    frags.append(rect(lxa, y, pw_, ph_, fill="#c9c9c9", stroke=INK, sw=1))
    frags.append(rect(rxa, y, pw_, ph_, fill="#c9c9c9", stroke=INK, sw=1))
    # компонент стоїть сторч: припаяний лівим кінцем, правий у повітрі
    frags.append(line(lxa + pw_ / 2, y, lxa + pw_ / 2, y - 56, color="#444", sw=11))
    frags.append(rect(lxa + pw_ / 2 - 8, y - 68, 16, 12, fill="#666", stroke=INK, sw=1))
    frags.append(text(lxa + pw_ / 2, y - 78, "правий кінець у повітрі", size=10, color=POS))
    frags.append(text(lxa - 4, y - 22, "розплав\nраніше", size=9, color=POS, anchor="end"))
    frags.append(text(rxa + pw_ + 4, y - 22, "ще\nтвердо", size=9, color=NEG, anchor="start"))
    frags.append(text(cxL, 300, "мідь висмоктує тепло → права площадка холодна", size=11, color=MUTED))

    # ── ПРАВОРУЧ (добре): обидві площадки під'єднані крізь теплові спиці
    cxR = 560
    lxb = cxR - gapp / 2 - pw_
    rxb = cxR + gapp / 2
    frags.append(text(cxR, 70, "Обидві — крізь тепловий відвід", size=12, color=FIELD, bold=True))
    frags.append(rect(rxb + pw_ + 12, y - 6, 96, 58, fill="#f6d9b8", stroke="#b07a35", sw=1.2, rx=3))
    frags.append(text(rxb + pw_ + 60, y + 44, "мідь", size=10, color="#8a5a1f"))
    # теплові спиці (relief) від заливки до правої площадки
    for dy in (2, ph_ - 2):
        frags.append(line(rxb + pw_, y + dy, rxb + pw_ + 12, y + dy, color="#b07a35", sw=2))
    # ліва так само крізь спиці до вузької доріжки
    frags.append(line(lxb - 12, y + ph_ / 2, lxb, y + ph_ / 2, color="#b07a35", sw=2))
    frags.append(rect(lxb, y, pw_, ph_, fill="#c9c9c9", stroke=INK, sw=1))
    frags.append(rect(rxb, y, pw_, ph_, fill="#c9c9c9", stroke=INK, sw=1))
    # компонент лежить рівно, спаяний обома кінцями
    frags.append(rect(lxb + pw_ / 2, y - 12, gapp, 12, fill="#666", stroke=INK, sw=1))
    frags.append(text(cxR, y - 20, "лежить рівно", size=10, color=FIELD))
    frags.append(text(lxb - 4, y - 22, "розплав\nразом", size=9, color=FIELD, anchor="end"))
    frags.append(text(rxb + pw_ + 4, y - 22, "розплав\nразом", size=9, color=FIELD, anchor="start"))
    frags.append(text(cxR, 300, "спиці гальмують тепло → обидві гріються нарівно", size=11, color=MUTED))

    # роздільник
    frags.append(line(W / 2, 58, W / 2, 312, color=MUTED, sw=1, dash="5,5"))
    render(os.path.join(OUT, 'tombstone-thermal.svg'), W, H, *frags)


# ── Фігура 3: панель, реперні мітки, зона захвату по краю ────────────────────
def fig_panel():
    W, H = 720, 380
    frags = []
    frags.append(text(W / 2, 34, "Що автомат вимагає від краю плати: панель, репери, вільна смуга",
                      size=14, bold=True))

    # рама панелі
    px, py, pw, ph = 90, 70, 540, 250
    frags.append(rect(px, py, pw, ph, fill="#fbfbfb", stroke=INK, sw=2))
    # технологічні поля (rails) зверху й знизу
    rail = 34
    frags.append(rect(px, py, pw, rail, fill="#eef2f7", stroke=MUTED, sw=1))
    frags.append(rect(px, py + ph - rail, pw, rail, fill="#eef2f7", stroke=MUTED, sw=1))
    frags.append(text(px + pw / 2, py + rail - 11, "технологічне поле (rail) — репери й захват конвеєра",
                      size=10, color=MUTED))

    # три однакові плати в панелі
    bw, bh = 150, 150
    bx0 = px + 20
    by = py + rail + 8
    for i in range(3):
        bx = bx0 + i * (bw + 12)
        frags.append(rect(bx, by, bw, bh, fill="#eaf4ec", stroke=FIELD, sw=1.6))
        frags.append(text(bx + bw / 2, by + bh / 2 + 4, "плата", size=12, color=FIELD))
        # локальний репер на платі
        frags.append(circle(bx + 12, by + 12, 4, fill=INK, stroke=INK))
        # перфорація/фрезерування між платами
        if i < 2:
            for k in range(6):
                frags.append(circle(bx + bw + 6, by + 12 + k * 24, 2.2, fill=BG, stroke=MUTED, sw=1))

    # глобальні репери (3 шт., асиметрично) на rail
    fid = [(px + 24, py + rail / 2), (px + pw - 24, py + rail / 2), (px + 24, py + ph - rail / 2)]
    for (fx, fy) in fid:
        frags.append(circle(fx, fy, 6, fill="#c0392b", stroke=INK, sw=1))
        frags.append(circle(fx, fy, 12, fill="none", stroke=POS, sw=1))
    frags.append(text(px + 24, py - 8, "глобальний репер (fiducial)", size=10, color=POS))

    # вільна смуга по краю (keep-out) — пунктиром усередині рами (чотири лінії)
    m = 10
    kx, ky, kw, kh = px + m, py + m, pw - 2 * m, ph - 2 * m
    frags.append(line(kx, ky, kx + kw, ky, color=POS, sw=1.2, dash="6,5"))
    frags.append(line(kx, ky + kh, kx + kw, ky + kh, color=POS, sw=1.2, dash="6,5"))
    frags.append(line(kx, ky, kx, ky + kh, color=POS, sw=1.2, dash="6,5"))
    frags.append(line(kx + kw, ky, kx + kw, ky + kh, color=POS, sw=1.2, dash="6,5"))
    frags.append(text(px + pw / 2, py + ph + 22,
                      "вільна від деталей смуга по краю — за неї тримають плату затискачі й транспортер",
                      size=11, color=MUTED))
    render(os.path.join(OUT, 'panel-fiducials.svg'), W, H, *frags)


# ── Фігура 4 (proj): страпи ревізії — три піни, зовнішній резистор до VCC/GND ─
def fig_straps():
    W, H = 720, 420
    frags = []
    frags.append(text(W / 2, 30, "Страпи ревізії: три піни, кожен зовнішнім резистором притягнутий до VCC або GND",
                      size=13, bold=True))

    # шини живлення
    vcc_y, gnd_y = 66, 360
    frags.append(line(70, vcc_y, W - 40, vcc_y, color=POS, sw=2.5))
    frags.append(text(70, vcc_y - 8, "VCC (3.3 В)", size=11, color=POS, anchor="start", bold=True))
    frags.append(line(70, gnd_y, W - 40, gnd_y, color=NEG, sw=2.5))
    frags.append(text(70, gnd_y + 16, "GND", size=11, color=NEG, anchor="start", bold=True))

    # корпус МК ліворуч
    frags.append(rect(70, 120, 150, 190, fill="#eef2f7", stroke=INK, sw=1.8))
    frags.append(text(145, 150, "МК", size=15, bold=True))
    frags.append(text(145, 170, "(входи)", size=10, color=MUTED))

    # три піни, кожен зі своїм резистором — біти 2,1,0 → 1,0,1 = ревізія 5
    pins = [
        ("REV2", 200, True,  "1"),   # до VCC → читається 1
        ("REV1", 200 + 165, False, "0"),   # до GND → читається 0
        ("REV0", 200 + 330, True,  "1"),   # до VCC → читається 1
    ]
    py0 = 200
    for name, px, to_vcc, bit in pins:
        # вивід від корпусу
        frags.append(line(220, py0, px, py0, color=INK, sw=1.6))
        frags.append(circle(px, py0, 3, fill=INK, stroke=INK))
        # підписи — збоку від вертикального дроту (щоб дріт не різав напис)
        frags.append(text(px - 8, py0 - 8, name, size=11, bold=True, anchor="end"))
        frags.append(text(px - 8, py0 + 16, "чит.: " + bit, size=10,
                          color=(POS if bit == "1" else NEG), bold=True, anchor="end"))
        # резистор угору (до VCC) або вниз (до GND)
        if to_vcc:
            frags.append(line(px, py0, px, vcc_y + 40, color=INK, sw=1.4))
            frags.append(rect(px - 9, vcc_y + 8, 18, 30, fill="#fff8e6", stroke="#b07a35", sw=1.4, rx=2))
            frags.append(line(px, vcc_y, px, vcc_y + 8, color=INK, sw=1.4))
            frags.append(text(px + 14, vcc_y + 26, "10к", size=10, color="#8a5a1f", anchor="start"))
            frags.append(text(px + 14, vcc_y + 40, "до VCC", size=9, color=MUTED, anchor="start"))
        else:
            frags.append(line(px, py0, px, gnd_y - 40, color=INK, sw=1.4))
            frags.append(rect(px - 9, gnd_y - 38, 18, 30, fill="#fff8e6", stroke="#b07a35", sw=1.4, rx=2))
            frags.append(line(px, gnd_y, px, gnd_y - 8, color=INK, sw=1.4))
            frags.append(text(px + 14, gnd_y - 22, "10к", size=10, color="#8a5a1f", anchor="start"))
            frags.append(text(px + 14, gnd_y - 8, "до GND", size=9, color=MUTED, anchor="start"))

    # підсумок: біти → число
    frags.append(text(W / 2, 398,
                      "біти REV2·REV1·REV0 = 1·0·1  →  ревізія 5.  Три піни = 8 можливих ревізій (0…7).",
                      size=12, color=INK))
    render(os.path.join(OUT, 'rev-straps-wiring.svg'), W, H, *frags)


# ── Фігура 5 (proj): часова вісь читання страпів на старті ───────────────────
def fig_read_timeline():
    W, H = 720, 300
    frags = []
    frags.append(text(W / 2, 30, "Коли читати страпи: спершу живлення вгору, тоді пауза, аж потім читання",
                      size=13, bold=True))

    x0, x1 = 80, W - 40
    axis_y = 250
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=1.8))
    frags.append(text(x1, axis_y + 18, "час", size=11, color=MUTED, anchor="end"))

    # крива наростання живлення
    ramp_x0, ramp_x1 = x0 + 10, x0 + 130
    top_y = 80
    frags.append(line(ramp_x0, axis_y, ramp_x0, top_y, color=MUTED, sw=1, dash="3,3"))
    # ламана: 0 → наростання → полиця
    frags.append(line(ramp_x0, axis_y - 4, ramp_x0 + 60, top_y, color=POS, sw=2.2))
    frags.append(line(ramp_x0 + 60, top_y, x1 - 20, top_y, color=POS, sw=2.2))
    frags.append(text(ramp_x0 + 30, axis_y - 100, "VCC", size=11, color=POS, bold=True))

    # фази на осі
    phases = [
        (ramp_x0, ramp_x0 + 60, "живлення\nнаростає", MUTED),
        (ramp_x0 + 60, ramp_x0 + 170, "пауза на\nстабілізацію", NEG),
        (ramp_x0 + 170, ramp_x0 + 300, "увімкнути\nпідтяжку", "#8a5a1f"),
        (ramp_x0 + 300, ramp_x0 + 430, "читати +\nусереднити", FIELD),
        (ramp_x0 + 430, x1 - 20, "вимкнути\nпідтяжку", INK),
    ]
    for (a, b, label, col) in phases:
        frags.append(line(a, axis_y, a, axis_y + 8, color=INK, sw=1.4))
        frags.append(fitbox(a + 2, axis_y + 12, b - a - 4, 40, label, size=10, color=col,
                            fill="#fbfbfb", stroke=col, sw=1.2))
    frags.append(line(x1 - 20, axis_y, x1 - 20, axis_y + 8, color=INK, sw=1.4))

    # позначка «читання» на полиці
    read_x = ramp_x0 + 365
    frags.append(circle(read_x, top_y, 5, fill=FIELD, stroke=INK, sw=1.4))
    frags.append(line(read_x, top_y, read_x, axis_y, color=FIELD, sw=1.2, dash="4,4"))
    frags.append(text(read_x, top_y - 12, "читаємо тут — рівень уже сталий", size=10, color=FIELD))

    render(os.path.join(OUT, 'rev-read-timeline.svg'), W, H, *frags)


# ── hist-фігура A: рядок часу народження DFM/DFMA ────────────────────────────
def fig_hist_timeline():
    W, H = 880, 430
    frags = []
    frags.append(text(W / 2, 30, "Як складання перейшло до машин — і народилася дисципліна",
                      size=16, bold=True))

    x0, x1 = 70, 810
    axis_y = 150
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.5))
    frags.append(arrow(x1 - 2, axis_y, x1 + 8, axis_y, color=INK, sw=2.5))

    y_lo, y_hi = 1960, 1993

    def px(year):
        return x0 + (x1 - x0) * (year - y_lo) / (y_hi - y_lo)

    for yr in (1960, 1970, 1980, 1990):
        xx = px(yr)
        frags.append(line(xx, axis_y - 6, xx, axis_y + 6, color=MUTED, sw=1.5))
        frags.append(text(xx, axis_y + 24, str(yr), size=12, color=MUTED))

    events = [
        (1960, ["IBM:", "планарний", "монтаж"], True, MUTED),
        (1977, ["Бутройд,", "грант NSF:", "DFA у Массачус."], True, POS),
        (1980, ["Дюгерст", "приєднується"], False, INK),
        (1983, ["фірма B.D. Inc.", "+ книга «Product", "Design for Assembly»"], True, INK),
        (1986, ["SMT ≈ 10 %", "збірок"], False, MUTED),
        (1991, ["Нац. медаль", "технологій США"], True, FIELD),
    ]
    for yr, lines, up, col in events:
        xx = px(yr)
        frags.append(circle(xx, axis_y, 5, fill=col, stroke=col, sw=1))
        if up:
            top = axis_y - 20
            frags.append(line(xx, axis_y - 6, xx, top, color=col, sw=1.3, dash="3,3"))
            ty = top - (len(lines) - 1) * 14 - 4
            frags.append(mtext(xx, ty, lines, size=12, color=col))
        else:
            # вниз: підпис зсунено вбік, щоб напис року на осі не потрапив під лінію
            bot = axis_y + 42
            lx = xx + 30
            frags.append(line(xx, axis_y + 6, lx, bot, color=col, sw=1.3, dash="3,3"))
            frags.append(mtext(lx, bot + 12, lines, size=12, color=col))

    frags.append(fitbox(x0, H - 58, x1 - x0, 40,
                        "Наскрізна думка: найдешевша деталь — та, якої немає. "
                        "Скорочуй кількість деталей, а не лише вартість кожної.",
                        size=13, fill="#fdf6ec", stroke=POS, sw=1.6))
    render(os.path.join(OUT, 'dfm-timeline.svg'), W, H, *frags)


# ── hist-фігура B: три критерії Бутройда (чи потрібна деталь окремою) ─────────
def fig_hist_criteria():
    W, H = 820, 360
    frags = []
    frags.append(text(W / 2, 30, "Три сита Бутройда: чи має ця деталь право бути окремою?",
                      size=16, bold=True))

    cand, cw, ch = textbox(W / 2, 78, "Деталь-кандидат", size=14, bold=True,
                           fill="#eef2f7", stroke=INK, sw=1.6, min_w=200)
    frags.append(cand)

    labels = [
        ("Рухається відносно\nсусідів?", NEG),
        ("Інший матеріал чи\nпроцес, ніж сусід?", FIELD),
        ("Треба окремою для\nскладання / сервісу?", POS),
    ]
    gx = [160, 410, 660]
    gy = 190
    gate_bottom = gy + 34
    for (lab, col), cx in zip(labels, gx):
        frags.append(fitbox(cx - 120, gy - 34, 240, 68, lab, size=13,
                            fill="#f4f6f8", stroke=col, sw=1.7))
        frags.append(line(W / 2, 78 + ch / 2, cx, gy - 34, color=MUTED, sw=1.2))

    keep, kw2, kh2 = textbox(230, 316, "ТАК бодай на одне → деталь лишається",
                             size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.8)
    frags.append(keep)
    drop, dw2, dh2 = textbox(600, 316, "НІ на всі три → кандидат на злиття / усунення",
                             size=13, bold=True, fill="#fdecea", stroke=POS, sw=1.8)
    frags.append(drop)
    for cx in gx:
        frags.append(line(cx, gate_bottom, 230, 316 - kh2 / 2, color=FIELD, sw=1.0, dash="2,3"))
        frags.append(line(cx, gate_bottom, 600, 316 - dh2 / 2, color=POS, sw=1.0, dash="2,3"))
    render(os.path.join(OUT, 'three-criteria.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_pipeline()
    fig_tombstone()
    fig_panel()
    fig_straps()
    fig_read_timeline()
    fig_hist_timeline()
    fig_hist_criteria()
    print("ok")
