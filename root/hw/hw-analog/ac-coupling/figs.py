# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def cap_symbol(cx, cy, vertical=False, gap=8, plate=18):
    """Дві пластини конденсатора. vertical=False — пластини вертикальні (струм горизонтально)."""
    if not vertical:
        return (line(cx - gap/2, cy - plate, cx - gap/2, cy + plate, color=INK, sw=2.4) +
                line(cx + gap/2, cy - plate, cx + gap/2, cy + plate, color=INK, sw=2.4))
    return (line(cx - plate, cy - gap/2, cx + plate, cy - gap/2, color=INK, sw=2.4) +
            line(cx - plate, cy + gap/2, cx + plate, cy + gap/2, color=INK, sw=2.4))


def gnd(cx, cy, w=22):
    s = line(cx, cy, cx, cy + 10, color=INK, sw=1.8)
    for i, ww in enumerate((w, w*0.62, w*0.3)):
        s += line(cx - ww/2, cy + 10 + i*5, cx + ww/2, cy + 10 + i*5, color=INK, sw=1.8)
    return s


def wave(x0, y0, w, amp, cycles, level=0.0, color=INK, sw=2.2, n=140):
    """Синусоїда поверх рівня level (частка висоти amp як зсув центру)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * w
        y = y0 - level - amp * math.sin(2 * math.pi * cycles * t)
        pts.append("%.1f,%.1f" % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (" ".join(pts), color, sw))


# ── 1. Два світи постійки: конденсатор пропускає лише «брижі» ───────────────
def fig_two_worlds():
    W, H = 720, 360
    els = []
    # дві смуги робочих рівнів
    yA = 250          # каскад А коливається навколо 9 В
    yB = 140          # каскад Б живе навколо 2.5 В
    # рівневі лінії DC
    els.append(line(70, yA, 300, yA, color=MUTED, sw=1.2, dash="5 4"))
    els.append(text(60, yA + 4, "9 В", size=13, color=MUTED, anchor="end"))
    els.append(line(420, yB, 650, yB, color=MUTED, sw=1.2, dash="5 4"))
    els.append(text(660, yB + 4, "2.5 В", size=13, color=MUTED, anchor="start"))

    # сигнал на виході А (велика постійка + брижі)
    els.append(wave(90, yA, 200, 22, 2.2, color=POS, sw=2.4))
    # сигнал на вході Б (та сама форма, інший рівень)
    els.append(wave(440, yB, 200, 22, 2.2, color=NEG, sw=2.4))

    # конденсатор у розрив між світами
    cx = 360
    els.append(line(300, yA, 340, yA, color=INK, sw=2))
    els.append(line(300, yA, 300, (yA+yB)/2, color=INK, sw=2))
    els.append(line(300, (yA+yB)/2, 340, (yA+yB)/2, color=INK, sw=2))
    els.append(cap_symbol(cx, (yA+yB)/2, vertical=False))
    els.append(line(cx+8, (yA+yB)/2, 420, (yA+yB)/2, color=INK, sw=2))
    els.append(line(420, (yA+yB)/2, 420, yB, color=INK, sw=2))
    els.append(line(420, yB, 440, yB, color=INK, sw=2))
    els.append(text(cx, (yA+yB)/2 - 30, "C", size=16, color=INK, bold=True))

    # підписи блоків
    b1, w1, h1 = textbox(150, 320, "каскад А\nрівень 9 В", size=13, fill="#fdecea", stroke=POS)
    els.append(b1)
    b2, w2, h2 = textbox(560, 320, "каскад Б\nрівень 2.5 В", size=13, fill="#eaf0fd", stroke=NEG)
    els.append(b2)

    # «постійку відрізано»
    bx, bw, bh = textbox(360, 60, "проходить лише ЗМІНА\n(постійні 9 В і 2.5 В розв'язано)",
                         size=13, fill=FILL, stroke=FIELD, color=INK)
    els.append(bx)
    return render(os.path.join(OUT, 'two-worlds.svg'), W, H, *els,
                  title="Розділовий конденсатор з'єднує два каскади, не плутаючи їхні постійні рівні")


# ── 2. Невидимий ФВЧ: куди ставити R, інакше вихід «висить» ─────────────────
def fig_half_circuit():
    W, H = 720, 320
    els = []
    ymid = 150
    # джерело сигналу зліва
    els.append(circle(95, ymid, 30, fill=FILL, stroke=INK, sw=1.8))
    els.append(wave(78, ymid, 34, 9, 1.0, color=INK, sw=2))
    els.append(text(95, ymid + 52, "сигнал", size=12, color=MUTED))
    # провід → конденсатор
    els.append(line(125, ymid, 230, ymid, color=INK, sw=2))
    els.append(cap_symbol(250, ymid, vertical=False))
    els.append(text(250, ymid - 30, "C", size=15, bold=True))
    els.append(line(258, ymid, 430, ymid, color=INK, sw=2))

    # вузол виходу
    els.append(circle(430, ymid, 4, fill=INK, stroke=INK))
    els.append(text(430, ymid - 16, "вихід", size=12, color=MUTED))

    # резистор униз — нижнє плече ФВЧ
    rx = 430
    els.append(line(rx, ymid, rx, ymid + 35, color=FIELD, sw=2))
    els.append(rect(rx - 10, ymid + 35, 20, 50, fill="#eafaf0", stroke=FIELD, sw=2, rx=3))
    els.append(text(rx + 26, ymid + 62, "R", size=15, bold=True, color=FIELD, anchor="start"))
    els.append(line(rx, ymid + 85, rx, ymid + 110, color=FIELD, sw=2))
    els.append(gnd(rx, ymid + 110))

    # навантаження праворуч
    els.append(line(430, ymid, 560, ymid, color=INK, sw=2))
    els.append(rect(560, ymid - 38, 110, 76, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    els.append(text(615, ymid - 6, "наступний", size=12, color=NEG))
    els.append(text(615, ymid + 12, "каскад", size=12, color=NEG))

    # попередження: без R вихід «висить»
    bx, bw, bh = textbox(360, 270, "Без R до землі вузол виходу НЕ має шляху для постійки —\n"
                         "він «висить» і дрейфує. R задає робочий нуль і утворює ФВЧ із C.",
                         size=12.5, fill=FILL, stroke=POS, color=INK)
    els.append(bx)
    return render(os.path.join(OUT, 'half-circuit.svg'), W, H, *els,
                  title="Половина зв'язку: конденсатор + резистор до землі = неминучий ФВЧ")


# ── 3. Відновлення зміщення: дільник повертає сигнал на потрібний рівень ────
def fig_bias_restore():
    W, H = 720, 360
    els = []
    yin = 110
    # вхід: чистий змінний сигнал навколо 0
    els.append(line(40, yin, 110, yin, color=INK, sw=2))
    els.append(wave(40, yin, 70, 14, 1.6, color=INK, sw=2))
    els.append(text(75, yin - 28, "сигнал ~0 В", size=12, color=MUTED))
    els.append(cap_symbol(150, yin, vertical=False))
    els.append(text(150, yin - 28, "C", size=14, bold=True))
    els.append(line(158, yin, 300, yin, color=INK, sw=2))

    # шина +5 В згори
    els.append(line(220, 45, 520, 45, color=POS, sw=2))
    els.append(text(530, 49, "+5 В", size=13, color=POS, anchor="start", bold=True))
    # шина земля знизу
    els.append(line(220, 300, 520, 300, color=INK, sw=2))
    els.append(gnd(370, 300))

    # дільник R1 (вгору) R2 (вниз), середина → вузол входу
    nodex = 300
    els.append(circle(nodex, yin, 4, fill=INK, stroke=INK))
    # R1 до +5
    els.append(line(nodex, yin, nodex, 90, color=POS, sw=2))
    els.append(rect(nodex - 10, 60, 20, 30, fill="#fdecea", stroke=POS, sw=2, rx=3))
    els.append(line(nodex, 60, nodex, 45, color=POS, sw=2))
    els.append(text(nodex - 16, 78, "R1", size=12, color=POS, anchor="end"))
    # R2 до землі
    els.append(line(nodex, yin, nodex, 200, color=INK, sw=2))
    els.append(rect(nodex - 10, 200, 20, 30, fill=FILL, stroke=INK, sw=2, rx=3))
    els.append(line(nodex, 230, nodex, 300, color=INK, sw=2))
    els.append(text(nodex - 16, 218, "R2", size=12, color=INK, anchor="end"))

    # далі у каскад
    els.append(line(nodex, yin, 470, yin, color=INK, sw=2))
    els.append(rect(470, yin - 36, 110, 72, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    els.append(text(525, yin - 4, "вхід", size=12, color=NEG))
    els.append(text(525, yin + 14, "підсилювача", size=11, color=NEG))

    # вихідний сигнал — той самий, але навколо 2.5 В
    yout = 110
    els.append(wave(615, yout, 70, 14, 1.6, level=0, color=NEG, sw=2))
    els.append(line(605, yout, 615, yout, color=INK, sw=2))
    els.append(line(605, yout, 605, yout, color=INK, sw=2))

    bx, bw, bh = textbox(360, 335, "R1 = R2 → середина шини: тепер сигнал «сидить» на 2.5 В,\n"
                         "у центрі діапазону живлення — є куди гойдатися вгору й униз.",
                         size=12.5, fill=FILL, stroke=FIELD, color=INK)
    els.append(bx)
    return render(os.path.join(OUT, 'bias-restore.svg'), W, H, *els,
                  title="Той самий конденсатор повертає сигнал на потрібну робочу точку")


# ── 4. AC проти DC: те саме коло осцилографа, різний зір ────────────────────
def fig_dc_vs_ac():
    W, H = 720, 380
    els = []
    # верхня панель: DC-зв'язок — велика постійка, брижі мізерні
    pad = 50
    p1y0, p1y1 = 50, 175
    els.append(rect(pad, p1y0, W - 2*pad, p1y1 - p1y0, fill=BG, stroke=MUTED, sw=1.2))
    base1 = p1y1 - 18
    els.append(line(pad, base1, W - pad, base1, color=MUTED, sw=1, dash="4 4"))
    els.append(text(pad - 8, base1 + 4, "0", size=11, color=MUTED, anchor="end"))
    # сигнал високо вгорі, дрібні брижі
    top1 = p1y0 + 30
    els.append(line(pad, top1, W - pad, top1, color=MUTED, sw=1, dash="4 4"))
    els.append(text(pad - 8, top1 + 4, "12 В", size=11, color=MUTED, anchor="end"))
    els.append(wave(pad + 6, top1, W - 2*pad - 12, 4, 9, color=POS, sw=2))
    els.append(text(W - pad - 6, p1y0 + 16, "DC-зв'язок: брижі тонуть у масштабі 12 В",
                    size=12.5, color=INK, anchor="end"))

    # нижня панель: AC-зв'язок — постійку прибрано, брижі в повний зріст
    p2y0, p2y1 = 215, 360
    els.append(rect(pad, p2y0, W - 2*pad, p2y1 - p2y0, fill=BG, stroke=FIELD, sw=1.4))
    mid2 = (p2y0 + p2y1) / 2
    els.append(line(pad, mid2, W - pad, mid2, color=MUTED, sw=1, dash="4 4"))
    els.append(text(pad - 8, mid2 + 4, "0", size=11, color=MUTED, anchor="end"))
    # ті самі брижі, тепер велика амплітуда навколо нуля; ліворуч видно «провисання» полиці
    els.append(wave(pad + 6, mid2, W - 2*pad - 12, 44, 9, color=NEG, sw=2.4))
    els.append(text(W - pad - 6, p2y0 + 16, "AC-зв'язок: постійку відрізано, брижі видно повністю",
                    size=12.5, color=INK, anchor="end"))

    # стрілка переходу
    els.append(arrow(pad - 30, base1, pad - 30, mid2, color=FIELD, sw=2))
    els.append(text(pad - 38, (base1 + mid2)/2, "−12 В", size=11, color=FIELD, anchor="end"))
    return render(os.path.join(OUT, 'dc-vs-ac.svg'), W, H, *els,
                  title="Кнопка «AC» на вході осцилографа: один сигнал, два погляди")


# ── 5. Маятник міжкаскадного зв'язку: чотири способи у часі ─────────────────
def fig_coupling_pendulum():
    """Чотири способи зв'язку як стовпці-картки з оцінкою по тих вимірах,
    що рухали історію: підсилення напруги, вага/ціна, смуга, чи пропускає постійку."""
    W, H = 760, 448
    els = []

    cols = [
        ("Трансформатор\n1920-ті", "#fdecea", POS,
         "крок напруги\n(виток ⤴)", "важкий,\nдорогий", "вузька,\nнерівна", "ні"),
        ("Дросель\n(проміжний)", "#fef6e7", "#b8860b",
         "помірне", "котушка\nоб'ємна", "обмежена\nзнизу", "ні"),
        ("RC-зв'язок\n1930-ті", "#eafaf0", FIELD,
         "тільки\nкаскад", "легкий,\nдешевий", "широка,\nрівна", "ні"),
        ("Прямий (DC)\nна ОП", "#eaf0fd", NEG,
         "каскад +\nЗЗ", "крихітний\n(чип)", "аж до 0 Гц", "ТАК"),
    ]
    rows = ["підсилення\nнапруги", "вага / ціна", "смуга", "пропускає\nпостійку?"]

    x0, y0 = 70, 80
    colw, gap = 150, 16
    head_h = 52
    rowh = 64
    # підписи рядків ліворуч
    for j, rname in enumerate(rows):
        ry = y0 + head_h + j * rowh + rowh / 2
        els.append(mtext(x0 - 12, ry - 6, rname, size=11.5, color=MUTED, anchor="end"))

    for i, (title, fill, stroke, v_gain, v_wt, v_bw, v_dc) in enumerate(cols):
        cx = x0 + i * (colw + gap)
        # шапка-картка
        els.append(rect(cx, y0, colw, head_h, fill=fill, stroke=stroke, sw=2, rx=8))
        els.append(mtext(cx + colw / 2, y0 + 21, title, size=13, color=INK, bold=True))
        vals = [v_gain, v_wt, v_bw, v_dc]
        for j, val in enumerate(vals):
            ry = y0 + head_h + j * rowh
            is_dc_yes = (j == 3 and val.strip() == "ТАК")
            cellfill = "#eafaf0" if is_dc_yes else BG
            cellstroke = FIELD if is_dc_yes else MUTED
            els.append(rect(cx, ry, colw, rowh, fill=cellfill, stroke=cellstroke,
                            sw=(2 if is_dc_yes else 1), rx=4))
            valcolor = FIELD if is_dc_yes else INK
            els.append(mtext(cx + colw / 2, ry + rowh / 2 - (val.count('\n')) * 7 + 4,
                             val, size=11.5, color=valcolor,
                             bold=is_dc_yes))

    # стрілка часу під стовпцями
    ybott = y0 + head_h + len(rows) * rowh + 26
    els.append(arrow(x0, ybott, x0 + 4 * (colw + gap) - gap, ybott, color=MUTED, sw=2))
    els.append(text(x0 + (4 * (colw + gap) - gap) / 2, ybott + 20,
                    "час · зменшення ваги · розширення смуги →", size=12, color=MUTED))
    return render(os.path.join(OUT, 'coupling-pendulum.svg'), W, H, *els,
                  title="Маятник міжкаскадного зв'язку: за що платили на кожному кроці")


if __name__ == '__main__':
    fig_two_worlds()
    fig_half_circuit()
    fig_bias_restore()
    fig_dc_vs_ac()
    fig_coupling_pendulum()
    print("ok: 5 figures")
