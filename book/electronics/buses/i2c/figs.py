# -*- coding: utf-8 -*-
"""Фігури до теми «Шина I²C».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── локальні примітиви (схематика) ───────────────────────────────────────────
def polyline(pts, color=INK, sw=2.6):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (d, color, sw))


def dot(x, y, r=4.2, color=INK):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (x, y, r, color)


def ground(x, y):
    s = line(x, y, x, y + 10, color=INK, sw=2)
    s += line(x - 15, y + 10, x + 15, y + 10, color=INK, sw=2)
    s += line(x - 9, y + 16, x + 9, y + 16, color=INK, sw=2)
    s += line(x - 4, y + 22, x + 4, y + 22, color=INK, sw=2)
    return s


def resistor_v(x, ytop, ybot, w=15):
    mid = (ytop + ybot) / 2
    bt, bb = mid - 24, mid + 24
    s = line(x, ytop, x, bt, color=INK, sw=2)
    s += rect(x - w / 2, bt, w, bb - bt, fill=BG, stroke=INK, sw=2, rx=2)
    s += line(x, bb, x, ybot, color=INK, sw=2)
    return s


# ── 1. Топологія шини: майстер і ведені на двох спільних лініях ───────────────
def fig_topology():
    W, H = 960, 430
    f = [text(W / 2, 30, "Уся плата на двох спільних лініях: додати чип — це нова адреса, а не нові проводи",
              size=15, bold=True)]

    y_sda, y_scl = 150, 205
    x_l, x_sda_r, x_scl_r = 70, 850, 890

    # живлення і дві підтяжки
    f.append(line(838, 64, 912, 64, color=POS, sw=2.4))
    f.append(text(875, 52, "+VDD", size=12, bold=True, color=POS))
    f.append(line(850, 64, 850, 90, color=INK, sw=2))
    f.append(resistor_v(850, 90, y_sda))
    f.append(text(867, 118, "Rp", size=12, color=INK, anchor="start", italic=True))
    f.append(line(890, 64, 890, 90, color=INK, sw=2))
    f.append(resistor_v(890, 90, y_scl))
    f.append(text(907, 150, "Rp", size=12, color=INK, anchor="start", italic=True))

    # дві шинні лінії
    f.append(line(x_l, y_sda, x_sda_r, y_sda, color=INK, sw=2.6))
    f.append(line(x_l, y_scl, x_scl_r, y_scl, color=INK, sw=2.6))
    f.append(dot(850, y_sda))
    f.append(dot(890, y_scl))
    f.append(text(x_l - 12, y_sda + 4, "SDA", size=13, bold=True, color=INK, anchor="end"))
    f.append(text(x_l - 12, y_scl + 4, "SCL", size=13, bold=True, color=INK, anchor="end"))

    # пристрої знизу: (підпис, x-ліво, ширина, tap_SDA, tap_SCL, роль-колір)
    devs = [
        ("Майстер\n(мікроконтролер)", 70, 180, 105, 235, POS),
        ("Давач\nтемператури", 300, 150, 330, 430, INK),
        ("Годинник\nRTC", 500, 150, 530, 630, INK),
        ("Пам'ять\nEEPROM", 700, 130, 725, 805, INK),
    ]
    by, bh = 272, 96
    for lab, bx, bw, tsda, tscl, col in devs:
        f.append(rect(bx, by, bw, bh, fill=("#fdecea" if col == POS else FILL),
                      stroke=col, sw=1.8, rx=8))
        f.append(mtext(bx + bw / 2, by + bh / 2 - 6, lab, size=12,
                       color=col, bold=(col == POS)))
        # відведення до SDA (верхня лінія): перетинає SCL без крапки
        f.append(line(tsda, by, tsda, y_sda, color=INK, sw=1.8))
        f.append(dot(tsda, y_sda))
        # відведення до SCL (ближча лінія)
        f.append(line(tscl, by, tscl, y_scl, color=INK, sw=1.8))
        f.append(dot(tscl, y_scl))

    b, _, _ = textbox(W / 2, 402,
                      "SDA — дані, SCL — такт; обидві тримає у «1» підтяжка, а будь-який пристрій може лише притягнути до «0»",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "topology.svg"), W, H, *f)


# ── 2. Монтажне «І»: 0 від будь-кого перемагає 1 від підтяжки ─────────────────
def fig_wired_and():
    W, H = 820, 400
    f = [text(W / 2, 30, "Спільну лінію вгору тягне лише резистор, а вниз — будь-який транзистор: «0» завжди перемагає",
              size=14.5, bold=True)]

    y_line = 150
    x_l, x_r = 120, 700
    # живлення + підтяжка справа
    f.append(line(628, 60, 712, 60, color=POS, sw=2.4))
    f.append(text(670, 48, "+VDD", size=12, bold=True, color=POS))
    f.append(line(670, 60, 670, 86, color=INK, sw=2))
    f.append(resistor_v(670, 86, y_line))
    f.append(text(688, 118, "Rp", size=12, color=INK, anchor="start", italic=True))
    f.append(text(688, 134, "«хоче 1»", size=10, color=MUTED, anchor="start"))
    f.append(dot(670, y_line))

    # спільна лінія
    f.append(line(x_l, y_line, x_r, y_line, color=INK, sw=2.8))
    f.append(text(x_l - 12, y_line + 4, "лінія", size=12, bold=True, color=INK, anchor="end"))

    # ── Пристрій A: відпустив (розімкнений ключ) ──
    ax = 210
    f.append(dot(ax, y_line))
    f.append(line(ax, y_line, ax, 224, color=INK, sw=2))
    # розімкнений ключ: нижній контакт + важіль убік
    f.append(dot(ax, 224))
    f.append(line(ax, 224, ax + 22, 206, color=INK, sw=2.4))   # важіль угору-вбік (розімкнено)
    f.append(dot(ax, 264))
    f.append(line(ax, 264, ax, 300, color=INK, sw=2))
    f.append(ground(ax, 300))
    f.append(rect(ax - 96, 214, 78, 70, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=8))
    f.append(mtext(ax - 57, 244, "Пристрій A\nвідпускає\n(розімкнено)", size=10.5, color=FIELD, bold=True))

    # ── Пристрій B: тягне вниз (замкнений ключ) ──
    bx = 470
    f.append(dot(bx, y_line))
    f.append(line(bx, y_line, bx, 300, color=NEG, sw=2.6))       # суцільний провід до землі
    f.append(ground(bx, 300))
    f.append(rect(bx + 20, 214, 78, 70, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=8))
    f.append(mtext(bx + 59, 244, "Пристрій B\nтягне 0\n(замкнено)", size=10.5, color=NEG, bold=True))

    # вердикт на лінії
    f.append(rect(300, 96, 150, 34, fill="#fbeee6", stroke=POS, sw=1.6, rx=8))
    f.append(text(375, 118, "лінія = 0", size=15, bold=True, color=POS))
    f.append(line(375, 130, 470, y_line - 6, color=POS, sw=1.2, dash="4,3"))

    b, _, _ = textbox(W / 2, 366,
                      "«1» на лінії — лише коли ВСІ відпустили; варто комусь одному притягнути до землі — і вся лінія в «0». Це і є монтажне «І».",
                      size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "wired-and.svg"), W, H, *f)


# ── 3. Кадр I²C: START, адреса+R/W, ACK, дані, ACK, STOP ──────────────────────
def fig_frame():
    W, H = 980, 400
    f = [text(W / 2, 28, "Один обмін I²C: рамку задають START і STOP — рухи SDA під високим SCL",
              size=15, bold=True)]

    x0, bw = 96, 46
    sda_hi, sda_lo = 108, 156
    scl_hi, scl_lo = 250, 298

    # структура кадру: тип комірки + (для біт) значення
    # адреса 0x48 = 100 1000, R/W=0 → біти A6..A0,RW = 1,0,0,1,0,0,0,0
    addr_bits = [1, 0, 0, 1, 0, 0, 0]
    bit_labels = ["A6", "A5", "A4", "A3", "A2", "A1", "A0"]

    # побудова SCL: список ('clock'|'high', n)
    scl_plan = [('high', 1), ('high', 1), ('clock', 8), ('clock', 1),
                ('clock', 3), ('clock', 1), ('high', 1), ('high', 1)]
    scl_pts = [(x0, scl_hi)]
    x = x0
    for kind, n in scl_plan:
        for _ in range(n):
            if kind == 'clock':
                scl_pts += [(x, scl_lo), (x + bw * 0.5, scl_lo),
                            (x + bw * 0.5, scl_hi), (x + bw, scl_hi)]
            else:
                scl_pts += [(x, scl_hi), (x + bw, scl_hi)]
            x += bw
    f.append(polyline(scl_pts, color=NEG, sw=2.6))
    xend = x

    # межі комірок (для міток)
    def cx(i):
        return x0 + (i + 0.5) * bw

    # SDA: покомірково
    sda_pts = [(x0, sda_hi), (x0 + bw, sda_hi)]                     # idle high
    # START (комірка 1): падіння в середині
    xs = x0 + bw
    sda_pts += [(xs, sda_hi), (xs + bw * 0.5, sda_hi),
                (xs + bw * 0.5, sda_lo), (xs + bw, sda_lo)]
    # адреса+RW: 8 біт (комірки 2..9)
    seq = addr_bits + [0]                                            # RW=0
    xb = x0 + 2 * bw
    for b in seq:
        yb = sda_hi if b == 1 else sda_lo
        sda_pts += [(xb, yb), (xb + bw, yb)]
        xb += bw
    # ACK (комірка 10): ведений тягне 0
    sda_pts += [(xb, sda_lo), (xb + bw, sda_lo)]
    xb += bw
    # дані (комірки 11..13): затінений блок — SDA намалюємо як «дійсні дані» (низ)
    data_x0 = xb
    sda_pts += [(xb, sda_lo), (xb + 3 * bw, sda_lo)]
    xb += 3 * bw
    # ACK (комірка 14)
    sda_pts += [(xb, sda_lo), (xb + bw, sda_lo)]
    xb += bw
    # STOP (комірка 15): підйом у середині
    sda_pts += [(xb, sda_lo), (xb + bw * 0.5, sda_lo),
                (xb + bw * 0.5, sda_hi), (xb + bw, sda_hi)]
    xb += bw
    # idle
    sda_pts += [(xb, sda_hi), (xb + bw, sda_hi)]
    f.append(polyline(sda_pts, color=INK, sw=2.6))

    # затінений прямокутник поверх поля даних (SDA)
    f.append(rect(data_x0, sda_hi - 4, 3 * bw, (sda_lo - sda_hi) + 8,
                  fill="#eef6ef", stroke=FIELD, sw=1.4, rx=4))
    f.append(text(data_x0 + 1.5 * bw, (sda_hi + sda_lo) / 2 + 4, "байт даних",
                  size=11, bold=True, color=FIELD))

    # мітки рядків
    f.append(text(x0 - 14, sda_hi + 4, "SDA", size=12.5, bold=True, anchor="end"))
    f.append(text(x0 - 14, scl_hi + 4, "SCL", size=12.5, bold=True, color=NEG, anchor="end"))
    f.append(text(x0 - 14, sda_hi - 14, "1", size=10, color=MUTED, anchor="end"))
    f.append(text(x0 - 14, sda_lo + 12, "0", size=10, color=MUTED, anchor="end"))

    # значення біт адреси над SDA
    for i, (b, lb) in enumerate(zip(seq, bit_labels + ["R/W"])):
        c = cx(2 + i)
        f.append(text(c, sda_hi - 30, str(b), size=12, bold=True,
                      color=(POS if b else NEG)))
        f.append(text(c, sda_hi - 15, lb, size=9, color=MUTED))

    # дужка «адреса 7 біт + R/W»
    a0, a7 = cx(2) - bw / 2, cx(9) + bw / 2
    f.append(line(a0, 62, a7, 62, color=MUTED, sw=1.3))
    f.append(line(a0, 62, a0, 68, color=MUTED, sw=1.3))
    f.append(line(a7, 62, a7, 68, color=MUTED, sw=1.3))
    f.append(text((a0 + a7) / 2, 54, "адреса 7 біт + біт напрямку R/W", size=11, bold=True))

    # підписи подій під SCL з пунктирними напрямними
    def event(i, lab, note, col):
        c = cx(i)
        f.append(line(c, scl_lo + 6, c, 336, color=col, sw=1.1, dash="3,3"))
        f.append(text(c, 350, lab, size=11.5, bold=True, color=col))
        if note:
            f.append(text(c, 366, note, size=9.5, color=MUTED))

    event(1, "START", "SDA↓ під SCL=1", POS)
    event(10, "ACK", "ведений тягне 0", FIELD)
    event(14, "ACK", "", FIELD)
    event(15, "STOP", "SDA↑ під SCL=1", POS)

    render(os.path.join(IMG, "frame.svg"), W, H, *f)


# ── 4. Асиметрія фронтів: різке падіння, пологий RC-підйом ────────────────────
def fig_rise_time():
    W, H = 840, 400
    f = [text(W / 2, 28, "Униз лінію роняє транзистор — миттєво; угору тягне лише підтяжка крізь ємність — повільно",
              size=14, bold=True)]

    x_l, x_r = 100, 770
    y0, yV = 330, 110                       # 0 В і VDD
    def yv(frac):                           # частка VDD → координата
        return y0 - frac * (y0 - yV)

    # рівні-пороги (пунктир)
    for frac, lab, col in [(1.0, "VDD", MUTED),
                           (0.7, "0.7·VDD  —  поріг «1» (VIH)", FIELD),
                           (0.3, "0.3·VDD  —  поріг «0» (VIL)", POS)]:
        y = yv(frac)
        f.append(line(x_l, y, x_r, y, color=col, sw=1.2, dash="5,4"))
        f.append(text(x_r + 8, y + 4, lab, size=10.5, color=col, anchor="start")
                 if frac != 1.0 else text(x_r + 8, y + 4, lab, size=11, bold=True,
                                          color=col, anchor="start"))
    f.append(line(x_l, y0, x_r, y0, color=INK, sw=1.4))       # вісь 0
    f.append(text(x_l - 10, y0 + 4, "0 В", size=10.5, color=MUTED, anchor="end"))

    # хвиля: високо → різке падіння → низько → RC-підйом → високо
    x_fall = 210
    x_rise0 = 360
    tau = 62.0
    pts = [(x_l, yV), (x_fall, yV), (x_fall, y0)]             # плато + різке падіння
    pts += [(x_rise0, y0)]                                    # плато 0
    xs = []
    for k in range(0, 260, 4):
        xx = x_rise0 + k
        if xx > x_r:
            break
        frac = 1 - math.exp(-k / tau)
        pts.append((xx, yv(frac)))
        xs.append((xx, frac))
    pts.append((x_r, yv(1 - math.exp(-(x_r - x_rise0) / tau))))
    f.append(polyline(pts, color=INK, sw=2.8))

    # підписи фронтів
    f.append(text(x_fall - 8, 250, "різке", size=11, bold=True, color=NEG, anchor="end"))
    f.append(text(x_fall - 8, 266, "падіння", size=11, bold=True, color=NEG, anchor="end"))
    f.append(text(x_fall - 8, 286, "(транзистор)", size=9.5, color=MUTED, anchor="end"))
    f.append(text(x_rise0 + 150, 158, "пологий RC-підйом (підтяжка крізь ємність)",
                  size=11, bold=True, color=INK))

    # знайти x, де фрак = 0.3 і 0.7 → час наростання t_r
    def x_at(frac):
        return x_rise0 - tau * math.log(1 - frac)
    x30, x70 = x_at(0.3), x_at(0.7)
    for xx, fr in [(x30, 0.3), (x70, 0.7)]:
        f.append(line(xx, yv(fr), xx, y0 + 8, color=MUTED, sw=1.1, dash="3,3"))
    yb = y0 + 24
    f.append(line(x30, yb, x70, yb, color=POS, sw=1.8))
    f.append(line(x30, yb - 5, x30, yb + 5, color=POS, sw=1.8))
    f.append(line(x70, yb - 5, x70, yb + 5, color=POS, sw=1.8))
    f.append(text((x30 + x70) / 2, yb + 18, "t_r — час наростання (мусить укластися в такт)",
                  size=11, bold=True, color=POS))

    render(os.path.join(IMG, "rise-time.svg"), W, H, *f)


# ── 5. Арбітраж: майстер, що виставив 1 і прочитав 0, програв ─────────────────
def fig_arbitration():
    W, H = 880, 380
    f = [text(W / 2, 28, "Двоє почали разом: хто виставив «1», а на лінії побачив «0», мовчки відступає",
              size=14.5, bold=True)]

    A = [1, 0, 0, 1, 0, 1]
    B = [1, 0, 1, None, None, None]      # B програє на 3-му біті
    LINE = [1, 0, 0, 1, 0, 1]            # монтажне І; після bit3 = слідує за A
    lose_col = 2                          # індекс біта, де B програв

    x0, cw = 210, 100
    rows = [("Майстер A", A, 96, INK),
            ("Майстер B", B, 168, NEG),
            ("Лінія (І)", LINE, 244, INK)]

    # заголовки стовпців
    for i in range(6):
        cxx = x0 + i * cw + cw / 2
        f.append(text(cxx, 74, "біт %d" % (i + 1), size=10.5, color=MUTED))

    for lab, vals, ry, col in rows:
        f.append(text(x0 - 16, ry + 20, lab, size=12, bold=True, color=col, anchor="end"))
        for i, v in enumerate(vals):
            cxx = x0 + i * cw
            hot = (i == lose_col)
            if v is None:
                f.append(rect(cxx, ry, cw - 8, 40, fill="#f0f0f0", stroke="#cfcfcf",
                              sw=1.4, rx=6))
                f.append(text(cxx + (cw - 8) / 2, ry + 26, "мовчить", size=10.5,
                              color=MUTED))
            else:
                vc = POS if v == 1 else NEG
                bstroke = POS if (hot and lab == "Майстер B") else vc
                fillc = "#fbeee6" if (hot and lab != "Лінія (І)") else \
                        ("#eef6ef" if lab == "Лінія (І)" else "#f4f6f8")
                f.append(rect(cxx, ry, cw - 8, 40, fill=fillc, stroke=bstroke,
                              sw=(2.2 if hot else 1.6), rx=6))
                f.append(text(cxx + (cw - 8) / 2, ry + 27, str(v), size=17, bold=True,
                              color=vc))

    # виділити стовпець програшу
    hx = x0 + lose_col * cw + (cw - 8) / 2
    f.append(line(hx, 88, hx, 292, color=POS, sw=1.1, dash="4,3"))
    f.append(text(hx, 306, "B виставив 1, а прочитав 0", size=11, bold=True, color=POS))
    f.append(text(hx, 322, "→ програв і відступає", size=11, bold=True, color=POS))

    b, _, _ = textbox(W / 2, 356,
                      "Виграє менша адреса (хто раніше виставив «0»); біти переможця A на лінії не постраждали",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "arbitration.svg"), W, H, *f)


# ── 6. Хронологія: специфікація проти прав і назв (до вставки hist) ──────────
def fig_history():
    rows = [
        ("1980", "s", "31 жовтня — пріоритет патенту Philips на дводротову шину"),
        ("1982", "s", "шина в кремнії: перші чипи для телевізорів Philips"),
        ("1984", "r", "видано європейський патент EP 0051332"),
        ("1987", "r", "видано патент США 4 689 740 (згас 2004 року)"),
        ("1992", "s", "редакція 1.0: швидкий режим 400 кбіт/с і 10-бітні адреси"),
        ("1994", "r", "Intel і Duracell будують SMBus — підмножину I²C"),
        ("1998", "s", "редакція 2.0: надшвидкий режим 3.4 Мбіт/с"),
        ("кін. 1990-х", "r", "у чужих даташитах з'являється TWI замість імені I²C"),
        ("2006", "r", "1 жовтня знято ліцензійну плату; Philips виділяє NXP"),
        ("2007", "s", "редакція 3.0: швидкий-плюс 1 Мбіт/с"),
        ("2012", "s", "редакція 4.0: однонапрямний UFm 5 Мбіт/с"),
        ("2017", "r", "MIPI оголошує I3C — наступника на тих самих двох дротах"),
        ("2021", "s", "редакція 7.0: майстер/ведений → контролер/ціль"),
    ]
    step, y0 = 46, 128
    W, H = 1000, y0 + (len(rows) - 1) * step + 56
    x_year, x_spine, x_txt = 168, 194, 218

    f = [text(W / 2, 34, "Дві нитки однієї історії: як росла специфікація і як мінялися права на неї",
              size=15, bold=True)]

    # легенда
    f.append(circle(232, 74, 6.5, fill=BG, stroke=NEG, sw=2.4))
    f.append(text(246, 79, "специфікація шини", size=12.5, color=NEG, anchor="start", bold=True))
    f.append(circle(560, 74, 6.5, fill=BG, stroke=POS, sw=2.4))
    f.append(text(574, 79, "права, ліцензія та імена", size=12.5, color=POS, anchor="start", bold=True))

    # хребет
    f.append(line(x_spine, y0 - 22, x_spine, y0 + (len(rows) - 1) * step + 22,
                  color=MUTED, sw=2))

    for i, (year, lane, what) in enumerate(rows):
        y = y0 + i * step
        c = NEG if lane == "s" else POS
        f.append(text(x_year, y + 5, year, size=13, color=c, anchor="end", bold=True))
        f.append(circle(x_spine, y, 6.5, fill=BG, stroke=c, sw=2.4))
        f.append(text(x_txt, y + 5, what, size=13.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "history.svg"), W, H, *f)


# ── Карта адресного простору: два зарезервовані блоки по краях ───────────────
def _reftable(x, y, w, title, rows, rowh=34, headh=36):
    """Таблиця-довідник: заголовок + рядки «адреса | значення». Повертає (svg, висота)."""
    h = headh + rowh * len(rows)
    f = [rect(x, y, w, h, fill=BG, stroke=LINE, sw=1.6, rx=6),
         rect(x, y, w, headh, fill="#fdecea", stroke=POS, sw=1.6, rx=6),
         text(x + 14, y + headh / 2 + 5, title, size=13, bold=True, color=POS, anchor="start")]
    for i, (addr, meaning) in enumerate(rows):
        ry = y + headh + rowh * i
        if i:
            f.append(line(x + 6, ry, x + w - 6, ry, color="#d5d9de", sw=1.0))
        f.append(text(x + 16, ry + rowh / 2 + 5, addr, size=13, bold=True, anchor="start"))
        f.append(text(x + 132, ry + rowh / 2 + 5, meaning, size=13, color=INK, anchor="start"))
    return "".join(f), h


def fig_address_map():
    W, H = 940, 470
    f = [text(W / 2, 30, "Простір 7-бітних адрес: зарезервовано лише краї", size=17, bold=True)]

    x0, x1 = 80, 860
    bw = x1 - x0
    by, bh = 78, 48
    unit = bw / 128.0
    wl = wr = 8 * unit

    f.append(rect(x0, by, wl, bh, fill="#fdecea", stroke=POS, sw=2, rx=4))
    f.append(rect(x0 + wl, by, bw - wl - wr, bh, fill="#eef6ef", stroke=FIELD, sw=2, rx=4))
    f.append(rect(x1 - wr, by, wr, bh, fill="#fdecea", stroke=POS, sw=2, rx=4))
    f.append(text((x0 + x1) / 2, by + bh / 2 + 5, "0x08 … 0x77 — 112 адрес для пристроїв",
                  size=14, bold=True))
    f.append(text(x0 - 12, by + bh / 2 + 5, "0x00", size=13, color=MUTED, anchor="end"))
    f.append(text(x1 + 12, by + bh / 2 + 5, "0x7F", size=13, color=MUTED, anchor="start"))
    f.append(text(x0 + wl, by - 12, "0x08", size=12, color=MUTED))
    f.append(text(x1 - wr, by - 12, "0x78", size=12, color=MUTED))

    f.append(line(x0 + wl / 2, by + bh + 5, 265, 172, color=POS, sw=1.2, dash="5,4"))
    f.append(line(x1 - wr / 2, by + bh + 5, 705, 172, color=POS, sw=1.2, dash="5,4"))

    tl, _ = _reftable(60, 178, 410, "0x00–0x07 — нижній блок", [
        ("0x00", "загальний виклик (R/W = 0)"),
        ("0x00", "START-байт (R/W = 1)"),
        ("0x01", "адреса CBUS"),
        ("0x02", "інший формат шини"),
        ("0x03", "на майбутнє"),
        ("0x04–0x07", "код майстра Hs"),
    ])
    tr, _ = _reftable(500, 178, 410, "0x78–0x7F — верхній блок", [
        ("0x78–0x7B", "префікс 10-бітної адреси"),
        ("0x7C–0x7F", "Device ID (R/W = 1)"),
        ("0x7C–0x7F", "на майбутнє (R/W = 0)"),
    ])
    f.append(tl)
    f.append(tr)

    b, _, _ = textbox(W / 2, 440,
                      "Разом 16 зарезервованих адрес — по вісім із кожного краю; усе між ними вільне",
                      size=13, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "address-map.svg"), W, H, *f)


# ── Десятибітна адреса: два байти на початку тієї самої рамки ────────────────
def fig_addr10():
    W, H = 980, 330

    def frame(y, label, boxes):
        g = [text(66, y + 32, label, size=13, bold=True, color=MUTED, anchor="start")]
        x = 152
        for w, lines, kind in boxes:
            fill = {"c": "#eef2fb", "a": "#eef6ef", "d": FILL}[kind]
            stroke = {"c": NEG, "a": FIELD, "d": LINE}[kind]
            g.append(fitbox(x, y, w, 56, lines, size=13, pad=6, fill=fill, stroke=stroke, sw=1.6))
            x += w + 7
        return "".join(g)

    f = [text(W / 2, 30, "Десять біт адреси — це два байти на початку тієї самої рамки",
              size=16, bold=True)]
    f.append(frame(66, "запис", [
        (34, "S", "c"),
        (150, "1 1 1 1 0 A9 A8\nW = 0", "d"),
        (28, "A", "a"),
        (150, "A7 … A0\n8 молодших біт", "d"),
        (28, "A", "a"),
        (96, "ДАНІ", "d"),
        (28, "A", "a"),
        (56, "…", "d"),
        (34, "P", "c"),
    ]))
    f.append(frame(152, "читання", [
        (34, "S", "c"),
        (150, "1 1 1 1 0 A9 A8\nW = 0", "d"),
        (28, "A", "a"),
        (150, "A7 … A0\n8 молодших біт", "d"),
        (28, "A", "a"),
        (38, "Sr", "c"),
        (150, "1 1 1 1 0 A9 A8\nR = 1", "d"),
        (28, "A", "a"),
        (96, "ДАНІ", "d"),
        (28, "N", "a"),
        (34, "P", "c"),
    ]))

    b, _, _ = textbox(W / 2, 268,
                      ["На читанні перший байт повторюють після Sr — з тим самим префіксом 1111 0",
                       "і тими самими старшими бітами, лише напрямок міняють на R = 1"],
                      size=13, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "addr10.svg"), W, H, *f)


# ── bit-bang: один біт = чотири чверті такту ─────────────────────────────────
def _bracket(x1, x2, y, color=INK, sw=1.8, tick=5):
    s = line(x1, y, x2, y, color=color, sw=sw)
    s += line(x1, y - tick, x1, y + tick, color=color, sw=sw)
    s += line(x2, y - tick, x2, y + tick, color=color, sw=sw)
    return s


def fig_bitbang_quarters():
    W, H = 1000, 478
    f = [text(W / 2, 32, "Один біт програмного майстра: чотири рівні чверті між двома спадами SCL",
              size=15, bold=True)]

    x0, xq = 200, 175
    xs = [x0 + i * xq for i in range(5)]        # 200 375 550 725 900
    y_hi, y_lo = 118, 178                       # SCL
    s_hi, s_lo = 258, 318                       # SDA
    x_left, x_right = 160, 940

    for i in range(4):
        f.append(text(xs[i] + xq / 2, 96, "чверть %d" % (i + 1), size=11.5, color=MUTED))

    # роздільники чвертей — двома шматками, щоб не перетинати підписи
    for i in (1, 2, 3):
        f.append(line(xs[i], 104, xs[i], 190, color="#cfcfcf", sw=1.1, dash="4,4"))
        f.append(line(xs[i], 234, xs[i], 332, color="#cfcfcf", sw=1.1, dash="4,4"))

    # SCL: спад на початку, підйом на межі 2-ї та 3-ї чверті, спад у кінці
    f.append(polyline([(x_left, y_hi), (x0, y_hi), (x0 + 10, y_lo),
                       (xs[2], y_lo), (xs[2] + 24, y_hi),
                       (xs[4], y_hi), (xs[4] + 10, y_lo), (x_right, y_lo)],
                      color=INK, sw=2.8))
    f.append(text(x0 - 46, (y_hi + y_lo) / 2 + 5, "SCL", size=13, bold=True, anchor="end"))

    # SDA: змінюється лише при низькому SCL — на межі 1-ї та 2-ї чверті
    f.append(polyline([(x_left, s_lo), (xs[1], s_lo), (xs[1] + 16, s_hi), (x_right, s_hi)],
                      color=NEG, sw=2.8))
    f.append(text(x0 - 46, (s_hi + s_lo) / 2 + 5, "SDA", size=13, bold=True,
                  color=NEG, anchor="end"))

    # дужки часових вікон
    f.append(_bracket(x0 + 10, xs[2], 202, color=FIELD))
    f.append(text((x0 + xs[2]) / 2, 220, "t_LOW = 2 чверті = 5 мкс   (мінімум 4.7)",
                  size=11, bold=True, color=FIELD))
    f.append(_bracket(xs[2] + 24, xs[4], 202, color=POS))
    f.append(text((xs[2] + xs[4]) / 2, 220, "t_HIGH = 2 чверті = 5 мкс   (мінімум 4.0)",
                  size=11, bold=True, color=POS))

    # момент зчитування — середина високого такту
    f.append(line(xs[3], 122, xs[3], 194, color=MUTED, sw=1.1, dash="3,3"))
    f.append(line(xs[3], 232, xs[3], s_hi, color=MUTED, sw=1.1, dash="3,3"))
    f.append(dot(xs[3], s_hi, r=4.4, color=NEG))
    f.append(text(xs[3] + 12, 250, "приймач читає SDA тут", size=11, color=NEG, anchor="start"))

    # що робить код у кожній чверті
    boxes = [("qd()\n«хвіст» низького такту", FILL, LINE),
             ("sda ← біт\nqd(): дані встоялися", "#eef2fb", NEG),
             ("scl_high()\nqd(): ведений читає", "#fdeeea", POS),
             ("qd()\nscl_low()", FILL, LINE)]
    for i, (s, fl, st) in enumerate(boxes):
        f.append(fitbox(xs[i] + 8, 352, xq - 16, 62, s, size=12, fill=fl, stroke=st))

    b, _, _ = textbox(W / 2, 448,
                      "SDA рухається лише при низькому SCL: будь-який його рух при високому — це вже START або STOP",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "bitbang-quarters.svg"), W, H, *f)


# ── чому scl_high() мусить дочекатися реального рівня ────────────────────────
def fig_scl_wait():
    W, H = 1000, 618
    f = [text(W / 2, 32, "Відпустити SCL — ще не означає, що SCL піднявся", size=15, bold=True)]

    x_l, x_r = 250, 940

    def panel(y_title, title, a_hi, a_lo, b_hi, b_lo, a_pts, b_pts,
              hold_x2, real_x1, real_x2, y_br, hold_lab, real_lab, verdict, vcol):
        g = [text(24, y_title, title, size=13, bold=True, anchor="start")]
        g.append(rect(x_l, b_hi - 6, hold_x2 - x_l, (b_lo - b_hi) + 16,
                      fill="#fbeeee", stroke="#f1d7d7", sw=1, rx=4))
        g.append(polyline(a_pts, color=MUTED, sw=2.8))
        g.append(polyline(b_pts, color=INK, sw=3.0))
        g.append(mtext(x_l - 14, (a_hi + a_lo) / 2 - 4,
                       ["що робить майстер", "(його намір)"], size=11.5,
                       color=MUTED, anchor="end"))
        g.append(mtext(x_l - 14, (b_hi + b_lo) / 2 - 4,
                       ["що насправді", "на лінії SCL"], size=11.5, bold=True, anchor="end"))
        g.append(_bracket(x_l, hold_x2, y_br, color=POS))
        g.append(text((x_l + hold_x2) / 2, y_br + 20, hold_lab, size=11, bold=True, color=POS))
        g.append(_bracket(real_x1, real_x2, y_br, color=FIELD))
        g.append(text((real_x1 + real_x2) / 2, y_br + 20, real_lab, size=11, bold=True,
                      color=FIELD))
        g.append(fitbox(x_l, y_br + 34, x_r - x_l, 34, verdict, size=11.5,
                        fill=("#eef6ef" if vcol == FIELD else "#fdeeea"), stroke=vcol))
        return g

    f += panel(76, "1. Майстер зчитує лінію: відпустив — і чекає, поки вона справді піднялася",
               104, 146, 190, 232,
               [(x_l, 146), (330, 146), (338, 104), (800, 104), (808, 146), (x_r, 146)],
               [(x_l, 232), (600, 232), (614, 190), (800, 190), (808, 232), (x_r, 232)],
               600, 614, 800, 252,
               "ведений тримає SCL внизу", "повний t_HIGH",
               "Такт на лінії почався з реального підйому — ведений побачив фронт і зарахував біт",
               FIELD)

    f += panel(356, "2. Майстер наосліп: відпустив і одразу відлічує високий такт за таймером",
               384, 426, 470, 512,
               [(x_l, 426), (330, 426), (338, 384), (460, 384), (468, 426),
                (590, 426), (598, 384), (720, 384), (728, 426), (x_r, 426)],
               [(x_l, 512), (630, 512), (644, 470), (720, 470), (728, 512), (x_r, 512)],
               630, 644, 720, 532,
               "ведений тримає SCL внизу", "дійшов лише другий такт",
               "Першого такту на лінії не було: майстер відлічив два біти, ведений — один, і кадр поїхав",
               POS)

    render(os.path.join(IMG, "scl-wait.svg"), W, H, *f)


# ── вивід множника 0.8473: два пороги на кривій заряду і на лог-осі ──────────
def fig_rc_thresholds():
    W, H = 1020, 500
    f = [text(W / 2, 30, "Час наростання — це відстань між двома порогами на кривій заряду",
              size=15.5, bold=True)]

    # ліва панель: V(t)
    f.append(text(295, 68, "Напруга на лінії", size=12.5, bold=True, color=MUTED))
    xL0, xL1 = 110, 470
    yV, y0 = 100, 340
    def yl(frac):
        return y0 - frac * (y0 - yV)

    f.append(line(xL0, y0, 480, y0, color=INK, sw=1.6))
    f.append(line(xL0, 92, xL0, y0, color=INK, sw=1.6))
    for frac, lab, col in [(1.0, "VDD", MUTED), (0.7, "0.7·VDD", FIELD), (0.3, "0.3·VDD", POS)]:
        y = yl(frac)
        f.append(line(xL0, y, xL1, y, color=col, sw=1.2, dash="5,4"))
        f.append(text(xL0 - 8, y + 4, lab, size=11, color=col, anchor="end"))
    f.append(text(xL0 - 8, y0 + 4, "0", size=11, color=MUTED, anchor="end"))

    tau, xc0 = 94.44, 130
    pts = [(xL0, y0), (xc0, y0)]
    k = 0.0
    while xc0 + k <= xL1:
        pts.append((xc0 + k, yl(1 - math.exp(-k / tau))))
        k += 3
    f.append(polyline(pts, color=INK, sw=2.8))
    f.append(text(400, 155, "V(t) = VDD·(1 − e^(−t/RC))", size=11.5, bold=True, color=INK))

    x1 = xc0 + tau * math.log(1 / 0.7)
    x2 = xc0 + tau * math.log(1 / 0.3)
    f.append(line(x1, yl(0.3), x1, 356, color=MUTED, sw=1.1, dash="3,3"))
    f.append(line(x2, yl(0.7), x2, 356, color=MUTED, sw=1.1, dash="3,3"))
    f.append(text(x1 - 8, 352, "t₁", size=11, color=MUTED, anchor="end"))
    f.append(text(x2 + 8, 352, "t₂", size=11, color=MUTED, anchor="start"))
    f.append(line(x1, 364, x2, 364, color=POS, sw=2))
    f.append(line(x1, 359, x1, 369, color=POS, sw=2))
    f.append(line(x2, 359, x2, 369, color=POS, sw=2))
    f.append(text((x1 + x2) / 2, 390, "t_r = RC·ln(7/3)", size=12, bold=True, color=POS))

    # права панель: залишок до VDD у лог-масштабі
    f.append(text(790, 68, "Той самий фронт: залишок до VDD, лог-вісь",
                  size=12.5, bold=True, color=MUTED))
    xR0, xR1, yTop, dec = 610, 960, 110, 115.0
    def yr(gap):
        return yTop - math.log10(gap) * dec

    f.append(line(xR0, y0, 970, y0, color=INK, sw=1.6))
    f.append(line(xR0, 92, xR0, y0, color=INK, sw=1.6))
    taur, xr0 = 91.67, 630
    f.append(line(xr0, yr(1.0), xR1, yr(math.exp(-(xR1 - xr0) / taur)), color=NEG, sw=2.6))
    f.append(text(862, 200, "Δ(t) = VDD·e^(−t/RC)", size=11.5, bold=True, color=NEG))

    for gap, lab, col in [(1.0, "VDD", MUTED), (0.7, "0.7·VDD", FIELD),
                          (0.3, "0.3·VDD", POS), (0.1, "0.1·VDD", MUTED)]:
        f.append(text(xR0 - 8, yr(gap) + 4, lab, size=11, color=col, anchor="end"))
    xg1 = xr0 + taur * math.log(1 / 0.7)
    xg2 = xr0 + taur * math.log(1 / 0.3)
    f.append(line(xR0, yr(0.7), xg1, yr(0.7), color=FIELD, sw=1.2, dash="5,4"))
    f.append(line(xR0, yr(0.3), xg2, yr(0.3), color=POS, sw=1.2, dash="5,4"))
    f.append(line(xg1, yr(0.7), xg1, 356, color=MUTED, sw=1.1, dash="3,3"))
    f.append(line(xg2, yr(0.3), xg2, 356, color=MUTED, sw=1.1, dash="3,3"))
    f.append(line(xg1, 364, xg2, 364, color=POS, sw=2))
    f.append(line(xg1, 359, xg1, 369, color=POS, sw=2))
    f.append(line(xg2, 359, xg2, 369, color=POS, sw=2))
    f.append(text((xg1 + xg2) / 2, 390, "той самий t_r", size=12, bold=True, color=POS))

    b, _, _ = textbox(W / 2, 452,
                      "Між порогами залишок до VDD спадає з 0.7·VDD до 0.3·VDD — рівно у 7/3 раза.\n"
                      "Час такого спаду — RC·ln(7/3) = 0.8473·RC, і ні VDD, ні початковий рівень у нього не входять.",
                      size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "rc-thresholds.svg"), W, H, *f)


# ── період такту: чотири шматки, що точно вкривають 1/f ──────────────────────
def fig_period_budget():
    W, H = 1000, 450
    f = [text(W / 2, 30, "Мінімальні часи специфікації точно вкривають період такту — запасу немає",
              size=15, bold=True)]

    seg_col = [("t_LOW", "#dce9fb", NEG), ("t_r", "#fbe3dd", POS),
               ("t_HIGH", "#e2f4e8", FIELD), ("t_f", "#ececec", MUTED)]
    lx = 250
    for lab, fill, col in seg_col:
        f.append(rect(lx, 56, 22, 16, fill=fill, stroke=col, sw=1.4, rx=3))
        f.append(text(lx + 30, 69, lab, size=11.5, color=col, bold=True, anchor="start"))
        lx += 120

    rows = [("Стандартний, 100 кГц", [4.7, 1.0, 4.0, 0.3], 10.0, "100 кГц"),
            ("Швидкий, 400 кГц", [1.3, 0.3, 0.6, 0.3], 2.5, "400 кГц"),
            ("Швидкий-плюс, 1 МГц", [0.5, 0.12, 0.26, 0.12], 1.0, "1 МГц")]
    def fmt(v):
        s = ("%.2f" % v).rstrip("0").rstrip(".")
        return s if "." in s else s + ".0"

    x0, L, bh = 250, 620, 44
    y = 116
    for name, segs, tot, fname in rows:
        f.append(text(x0 - 16, y + bh / 2 + 5, name, size=12, bold=True, anchor="end"))
        x = x0
        for (lab, fill, col), v in zip(seg_col, segs):
            w = L * v / tot
            f.append(rect(x, y, w, bh, fill=fill, stroke=col, sw=1.5, rx=4))
            if w >= 46:
                f.append(text(x + w / 2, y + bh / 2 + 5, fmt(v), size=12.5, bold=True, color=col))
            else:
                f.append(text(x + w / 2, y - 8, fmt(v), size=11, bold=True, color=col))
            x += w
        eq = " + ".join(fmt(v) for v in segs)
        f.append(text(x0, y + bh + 20, "%s = %s мкс = 1/%s" % (eq, fmt(tot), fname),
                      size=11.5, color=INK, anchor="start"))
        y += 100

    b, _, _ = textbox(W / 2, 408,
                      "f_max = 1 / (t_LOW + t_HIGH + t_r + t_f); усі чотири виміряні між тими самими порогами 0.3·VDD і 0.7·VDD,\n"
                      "тож вони стикуються без щілин — кожна зайва наносекунда фронту забирає час у півперіодів такту.",
                      size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "period-budget.svg"), W, H, *f)


# ── що вміщається в низький півперіод SCL ────────────────────────────────────
def fig_low_window():
    W, H = 960, 440
    f = [text(W / 2, 30, "Низький півперіод SCL ділять троє: поява даних, встановлення й запас на фронт",
              size=14.5, bold=True)]

    xs, xe = 205, 705
    px = (xe - xs) / 1.3

    yhi, ylo = 88, 138
    f.append(polyline([(110, yhi), (190, yhi), (205, ylo), (700, ylo), (745, yhi), (880, yhi)],
                      color=NEG, sw=2.8))
    f.append(text(100, yhi + 5, "SCL", size=12.5, bold=True, color=NEG, anchor="end"))
    f.append(line(xs, 158, xe, 158, color=NEG, sw=2))
    f.append(line(xs, 153, xs, 163, color=NEG, sw=2))
    f.append(line(xe, 153, xe, 163, color=NEG, sw=2))
    f.append(text((xs + xe) / 2, 180, "t_LOW ≥ 1.3 мкс", size=12.5, bold=True, color=NEG))

    f.append(arrow(190, 206, 190 + 0.3 * px, 206, color=POS, sw=2))
    f.append(text(252, 200, "внутрішнє тримання SDA ≥ 300 нс", size=10.5, bold=True,
                  color=POS, anchor="start"))

    yhi2, ylo2 = 232, 282
    f.append(polyline([(110, yhi2), (300, yhi2), (322, ylo2), (880, ylo2)], color=INK, sw=2.8))
    f.append(text(100, yhi2 + 5, "SDA", size=12.5, bold=True, anchor="end"))
    f.append(text(140, yhi2 - 12, "старий біт", size=10.5, color=MUTED, anchor="start"))
    f.append(text(790, ylo2 - 10, "новий біт стоїть і чекає на такт", size=10.5, color=MUTED))

    xa = xs + 0.9 * px
    xb = xa + 0.1 * px
    f.append(rect(xs, 312, xa - xs, 42, fill="#fbe3dd", stroke=POS, sw=1.6, rx=5))
    f.append(text((xs + xa) / 2, 338, "t_VD;DAT ≤ 0.9 мкс", size=11.5, bold=True, color=POS))
    f.append(rect(xa, 312, xb - xa, 42, fill="#e2f4e8", stroke=FIELD, sw=1.6, rx=5))
    f.append(text((xa + xb) / 2, 302, "t_SU;DAT ≥ 100 нс", size=11, bold=True, color=FIELD))
    f.append(rect(xb, 312, xe - xb, 42, fill="#ececec", stroke=MUTED, sw=1.6, rx=5))
    f.append(mtext((xb + xe) / 2, 330, "запас\n300 нс", size=10.5, color=MUTED, bold=True))

    b, _, _ = textbox(W / 2, 402,
                      "0.9 + 0.1 = 1.0 мкс із 1.3 мкс низького півперіоду; решта 0.3 мкс — рівно стеля часу наростання SDA.",
                      size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "low-window.svg"), W, H, *f)


# ── вікно опору підтяжки й точка, де воно зачиняється ────────────────────────
def fig_rp_window():
    W, H = 980, 470
    f = [text(W / 2, 30, "Вікно підтяжки: знизу тисне здатність притягнути «0», згори — час наростання",
              size=15, bold=True)]

    px0, px1, py0, py1 = 150, 900, 340, 90
    def X(cb):
        return px0 + (cb - 100) / 500.0 * (px1 - px0)
    def Y(r):
        return py0 - r / 2600.0 * (py0 - py1)

    f.append(line(px0, py0, 925, py0, color=INK, sw=1.6))
    f.append(line(px0, 80, px0, py0, color=INK, sw=1.6))
    f.append(text(px0, 70, "Rp, Ом", size=11.5, bold=True, color=MUTED))
    f.append(text(525, 384, "ємність шини Cb, пФ", size=11.5, bold=True, color=MUTED))
    for cb in (100, 200, 300, 400, 500, 600):
        f.append(line(X(cb), py0, X(cb), py0 + 5, color=INK, sw=1.4))
        f.append(text(X(cb), py0 + 22, str(cb), size=10.5, color=MUTED))
    for r in (0, 500, 1000, 1500, 2000, 2500):
        f.append(line(px0 - 5, Y(r), px0, Y(r), color=INK, sw=1.4))
        f.append(text(px0 - 10, Y(r) + 4, str(r), size=10.5, color=MUTED, anchor="end"))

    curve = []
    cb = 100.0
    while cb <= 600.0:
        rr = 300e-9 / (0.8473 * cb * 1e-12)
        if rr <= 2600:
            curve.append((X(cb), Y(rr)))
        cb += 4
    f.append(polyline(curve, color=NEG, sw=2.8))
    f.append(text(618, 118, "Rp,max = t_r / (0.8473·Cb),  t_r = 300 нс", size=11.5,
                  bold=True, color=NEG, anchor="start"))

    for rr, lab, col in [(1700, "3 мА / 0.4 В", POS), (817, "6 мА / 0.6 В", FIELD)]:
        f.append(line(px0, Y(rr), px1, Y(rr), color=col, sw=2, dash="7,4"))
        f.append(text(px0 - 10, Y(rr) - 10, lab, size=10.5, bold=True, color=col, anchor="end"))

    f.append(line(X(400), py1, X(400), py0, color=MUTED, sw=1.4, dash="4,4"))
    f.append(text(X(400), py1 - 12, "повна шина 400 пФ", size=10.5, color=MUTED))

    f.append(dot(X(208), Y(1700), r=5, color=POS))
    f.append(text(390, 148, "вікно зачиняється: 208 пФ", size=11, bold=True, color=POS,
                  anchor="start"))
    f.append(dot(X(434), Y(817), r=5, color=FIELD))
    f.append(text(700, 300, "із 6 мА — до 434 пФ", size=11, bold=True, color=FIELD,
                  anchor="start"))

    b, _, _ = textbox(W / 2, 428,
                      "Швидкий режим, живлення 5 В +10 %. Вихід на 3 мА вимагає Rp ≥ 1.70 кОм — і вже на 208 пФ упирається\n"
                      "у стелю фронту; вихід на 6 мА при VOL 0.6 В дозволяє Rp ≥ 0.82 кОм, і повні 400 пФ ще вміщаються.",
                      size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "rp-window.svg"), W, H, *f)


if __name__ == "__main__":
    fig_topology()
    fig_wired_and()
    fig_frame()
    fig_rise_time()
    fig_arbitration()
    fig_history()
    fig_address_map()
    fig_addr10()
    fig_bitbang_quarters()
    fig_scl_wait()
    fig_rc_thresholds()
    fig_period_budget()
    fig_low_window()
    fig_rp_window()
    print("OK: 14 figures ->", IMG)
