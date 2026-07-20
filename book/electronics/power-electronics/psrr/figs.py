# -*- coding: utf-8 -*-
"""Фігури до теми «PSRR — придушення пульсацій».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def wave(x0, y0, x1, amp, cycles, color, sw=2.2, n=160):
    """Синусоїда-пульсація на горизонтальній лінії y0 від x0 до x1."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * (x1 - x0)
        y = y0 - amp * math.sin(2 * math.pi * cycles * t)
        pts.append("%.1f,%.1f" % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (" ".join(pts), color, sw))


# ── 1. Механізм: петля гасить пульсацію, але два шляхи протікання лишаються ────
def fig_mechanism():
    W, H = 780, 430
    f = [text(W / 2, 30, "Чому стабілізатор гасить пульсацію — і чому не до нуля",
              size=17, bold=True)]

    railY = 96
    # вхідна шина з великою пульсацією
    f.append(text(70, railY - 34, "вхід", size=11, color=POS, bold=True))
    f.append(wave(40, railY, 250, 13, 4.5, POS))
    f.append(text(145, railY - 26, "груба пульсація", size=10.5, color=POS))

    # прохідний транзистор (великий блок)
    f.append(rect(250, 66, 150, 60, fill="#eef2f7", stroke="#7f93a8", sw=1.8))
    f.append(text(325, 90, "прохідний", size=12, color=INK, bold=True))
    f.append(text(325, 108, "транзистор", size=12, color=INK, bold=True))

    # вихідна шина з дрібним залишком
    f.append(wave(400, railY, 610, 2.4, 4.5, FIELD))
    f.append(text(660, railY - 4, "вихід", size=11, color=FIELD, bold=True))
    f.append(text(505, railY - 22, "дрібний залишок", size=10.5, color=FIELD))

    # підсилювач похибки
    f.append(rect(300, 210, 200, 58, fill="#eef2f7", stroke="#7f93a8", sw=1.8))
    f.append(text(400, 234, "підсилювач похибки", size=12, color=INK, bold=True))
    f.append(text(400, 254, "стежить за виходом", size=10, color=MUTED))

    # еталон
    f.append(rect(300, 320, 200, 54, fill="#eef2f7", stroke="#7f93a8", sw=1.8))
    f.append(text(400, 344, "еталон напруги", size=12, color=INK, bold=True))
    f.append(text(400, 362, "мірило, з яким рівняють", size=10, color=MUTED))

    # петля зворотного зв'язку: вихід → підсилювач → транзистор (керування)
    f.append(line(560, railY, 560, 239, color=INK, sw=1.6))
    f.append(circle(560, railY, 3, fill=INK, stroke=INK, sw=2))
    f.append(arrow(560, 239, 502, 239, color=INK, sw=1.7))
    f.append(text(600, 200, "зворотний зв'язок", size=10, color=INK))
    f.append(arrow(340, 210, 320, 128, color=INK, sw=1.7))
    f.append(text(300, 175, "керує", size=9.5, color=INK, anchor="end"))
    f.append(line(400, 268, 400, 320, color=INK, sw=1.6))

    # головний висновок петлі
    f.append(text(155, railY + 30,
                  "петля щоразу підправляє транзистор →", size=10.5, color=INK))
    f.append(text(155, railY + 46,
                  "гасить пульсацію у стільки разів,", size=10.5, color=INK))
    f.append(text(155, railY + 62,
                  "у скільки велике петльове підсилення", size=10.5, color=INK, bold=True))

    # два шляхи протікання (червоні) — чому не до нуля
    f.append(arrow(40, 340, 298, 344, color=POS, sw=1.7))
    f.append(text(150, 332, "живлення хитає сам еталон", size=10, color=POS, bold=True))
    f.append(text(150, 392, "1. еталон не ідеально сталий за живленням", size=10, color=POS))
    f.append(text(150, 408, "2. підсилення петлі скінченне й падає з частотою", size=10, color=POS))

    f.append(text(W / 2, H - 8,
                  "Придушення тримається на петлі; його межу ставлять сталість еталона й запас петльового підсилення",
                  size=10.5, color=MUTED, italic=True, anchor="middle"))
    # зсунемо підсумковий рядок трохи вгору, щоб не тіснити
    return render(os.path.join(IMG, "mechanism.svg"), W, H, *f)


# ── 2. PSRR(f): характерна крива — плато, спад разом із петлею, провал, обвал ──
def fig_curve():
    W, H = 800, 470
    f = [text(W / 2, 30, "PSRR падає з частотою: число на постійному струмі — найкраще, а не робоче",
              size=15.5, bold=True)]

    # осі
    x0, y0 = 96, 384          # лівий-нижній кут поля
    plotW, plotH = 620, 300   # ширина/висота поля
    xR = x0 + plotW
    yT = y0 - plotH

    # горизонтальні лінії сітки 0..80 дБ
    for db in (0, 20, 40, 60, 80):
        yy = y0 - db / 80.0 * plotH
        f.append(line(x0, yy, xR, yy, color="#e3e8ee", sw=1.2))
        f.append(text(x0 - 12, yy + 4, "%d" % db, size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 58, yT + plotH / 2, "PSRR, дБ", size=12, color=INK, anchor="middle"))
    # осьовий підпис вертикально не крутимо — ставимо збоку в один рядок вище
    f.append(text(x0 - 44, yT - 6, "більше — краще", size=9.5, color=MUTED, anchor="middle"))

    # вертикальні лінії-декади 10 Гц .. 10 МГц (6 декад)
    labels = ["10 Гц", "100 Гц", "1 кГц", "10 кГц", "100 кГц", "1 МГц", "10 МГц"]
    for i, lab in enumerate(labels):
        xx = x0 + i / 6.0 * plotW
        f.append(line(xx, yT, xx, y0, color="#eef1f5", sw=1.0))
        f.append(text(xx, y0 + 20, lab, size=10.5, color=MUTED))
    f.append(text(xR, y0 + 40, "частота →", size=11, color=INK, anchor="end"))

    # рамка поля
    f.append(line(x0, yT, x0, y0, color=INK, sw=1.6))
    f.append(line(x0, y0, xR, y0, color=INK, sw=1.6))

    def px(f_hz):
        return x0 + (math.log10(f_hz) - 1) / 6.0 * plotW

    def py(db):
        return y0 - db / 80.0 * plotH

    # характерна форма: плато → спад разом із петлею → провал → трохи вгору → обвал
    curve = [(10, 72), (100, 72), (1000, 70), (10000, 61), (30000, 52),
             (100000, 42), (300000, 30), (500000, 26), (1000000, 31),
             (3000000, 20), (10000000, 8)]
    pts = " ".join("%.1f,%.1f" % (px(fz), py(db)) for fz, db in curve)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pts, NEG))

    # позначки-регіони (виносимо написи в порожні зони, лініями не перетинаємо)
    f.append(text(px(130), py(72) - 12, "плато: тримають еталон і петля", size=10.5, color=INK))
    f.append(text(px(20000), 126, "спад — разом", size=10, color=INK))
    f.append(text(px(20000), 142, "із петльовим підсиленням", size=10, color=INK))
    f.append(text(px(480000), py(26) + 40, "провал", size=10.5, color=NEG, bold=True, anchor="end"))
    f.append(text(px(4500000), py(20) + 4, "обвал:", size=10, color=INK, anchor="start"))
    f.append(text(px(4500000), py(20) + 18, "паразити,", size=10, color=INK, anchor="start"))
    f.append(text(px(4500000), py(20) + 32, "вихідний C", size=10, color=INK, anchor="start"))

    # частота перетворювача — вертикаль, «читай PSRR тут» (лінія спиняється на кривій)
    fsw = 500000
    f.append(line(px(fsw), yT + 8, px(fsw), py(26), color=POS, sw=1.6, dash="6 4"))
    f.append(text(px(fsw) + 8, yT + 40, "тут пульсація", size=10.5, color=POS, bold=True, anchor="start"))
    f.append(text(px(fsw) + 8, yT + 56, "перетворювача —", size=10.5, color=POS, anchor="start"))
    f.append(text(px(fsw) + 8, yT + 72, "PSRR читай ТУТ", size=10.5, color=POS, bold=True, anchor="start"))

    f.append(text(W / 2, H - 10,
                  "На постійному струмі PSRR великий; на робочій частоті пульсації він може бути втричі меншим",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "curve.svg"), W, H, *f)


# ── 3. Каскад: імпульсний перетворювач + LDO-«дочищувач» ──────────────────────
def fig_cascade():
    W, H = 780, 320
    f = [text(W / 2, 30, "Головне застосування: LDO-«дочищувач» після імпульсного перетворювача",
              size=15.5, bold=True)]

    midY = 150

    # перетворювач
    f.append(rect(40, 116, 170, 70, fill="#eef2f7", stroke="#7f93a8", sw=1.8))
    f.append(text(125, 142, "імпульсний", size=12.5, color=INK, bold=True))
    f.append(text(125, 162, "перетворювач", size=12.5, color=INK, bold=True))
    f.append(text(125, 202, "ККД високий,", size=10, color=MUTED))
    f.append(text(125, 217, "але шумить", size=10, color=MUTED))

    # брудна шина з великою пульсацією
    f.append(wave(210, midY, 340, 15, 3.5, POS))
    f.append(text(275, midY - 30, "120 мВ", size=12, color=POS, bold=True))
    f.append(text(275, midY + 34, "на 500 кГц", size=10, color=POS))

    # LDO
    f.append(rect(340, 116, 150, 70, fill="#eef2f7", stroke="#7f93a8", sw=1.8))
    f.append(text(415, 144, "LDO", size=13, color=INK, bold=True))
    f.append(text(415, 166, "PSRR 40 дБ", size=11, color=INK))
    f.append(text(415, 205, "= поділити на 100", size=10.5, color=NEG, bold=True))

    # чиста шина з дрібним залишком
    f.append(wave(490, midY, 620, 2.0, 3.5, FIELD))
    f.append(text(560, midY - 26, "1.2 мВ", size=12, color=FIELD, bold=True))
    f.append(text(560, midY + 34, "чисте живлення", size=10, color=FIELD))

    # споживач
    f.append(rect(620, 122, 128, 58, fill=BG, stroke="#c9d3dc", sw=1.5))
    f.append(text(684, 146, "АЦП / радіо /", size=10.5, color=INK, bold=True))
    f.append(text(684, 163, "звук", size=10.5, color=INK, bold=True))

    f.append(text(W / 2, H - 14,
                  "Перетворювач дає ККД, LDO — чистоту: децибели придушення складаються, тож грубе живлення стає придатним",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "cascade.svg"), W, H, *f)


# ══ ФІГУРИ ДО ВСТАВКИ math-psrr-loop-gain.md ═════════════════════════════════

# ── 4. Двоє дверей: наскрізний прохід ділиться на (1+T), еталон — множиться ───
def fig_two_doors():
    W, H = 950, 510
    f = [text(W / 2, 30, "Двоє дверей для пульсації — і петля поводиться з ними ПО-РІЗНОМУ",
              size=16, bold=True)]

    yTop, yBot, yMid = 150, 350, 245

    # ── вхідна пульсація ──
    f.append(textbox(120, yMid, "вхідна\nпульсація\nvвх", size=13, bold=True,
                     fill="#fdecea", stroke=POS, sw=2)[0])
    f.append(wave(58, 92, 182, 9, 3.0, POS, sw=2.0))

    # розгалуження
    f.append(arrow(186, yMid, 228, yMid, color=LINE))
    f.append(circle(232, yMid, 4, fill=LINE, stroke=LINE))
    f.append(line(232, yTop, 232, yBot, color=LINE, sw=1.6))
    f.append(arrow(232, yTop, 262, yTop, color=LINE))
    f.append(arrow(232, yBot, 262, yBot, color=LINE))

    # ── ДВЕРІ 1: наскрізний прохід ──
    f.append(text(470, 90, "петля бачить це збурення на виході — отже, давить його",
                  size=12, color=NEG, bold=True))
    b1, w1, _ = textbox(348, yTop, "наскрізний прохід\nd(s) ≈ −10…−15 дБ",
                        size=12.5, fill="#eaf0fd", stroke=NEG, sw=1.8)
    f.append(b1)
    f.append(text(348, yTop + 48, "повз транзистор: rds, Cgd, плата", size=10.5, color=MUTED))
    f.append(arrow(348 + w1 / 2, yTop, 520, yTop, color=NEG))
    b2, w2, _ = textbox(578, yTop, "÷ (1 + T)", size=19, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=2.2)
    f.append(b2)
    f.append(text(578, yTop - 46, "тане з ростом петлі", size=10.5, color=NEG))

    # ── ДВЕРІ 2: еталон ──
    f.append(text(470, 412, "рух еталона — для петлі не помилка, а НОВА команда: вона його відтворює",
                  size=12, color=POS, bold=True))
    b3, w3, _ = textbox(348, yBot, "пульсація в еталоні\nr(s)",
                        size=12.5, fill="#fdecea", stroke=POS, sw=1.8)
    f.append(b3)
    f.append(text(348, yBot + 48, "еталон живиться від того ж входу", size=10.5, color=MUTED))
    f.append(arrow(348 + w3 / 2, yBot, 520, yBot, color=POS))
    b4, w4, _ = textbox(578, yBot, "× 1/β", size=19, bold=True,
                        fill="#fdecea", stroke=POS, sw=2.2)
    f.append(b4)
    f.append(text(578, yBot - 44, "від T НЕ залежить — це підлога", size=10.5, color=POS, bold=True))

    # ── збіг на виході ──
    f.append(line(578 + w2 / 2, yTop, 726, yTop, color=NEG, sw=1.8))
    f.append(line(726, yTop, 726, yMid - 22, color=NEG, sw=1.8))
    f.append(line(578 + w4 / 2, yBot, 726, yBot, color=POS, sw=1.8))
    f.append(line(726, yBot, 726, yMid + 22, color=POS, sw=1.8))
    f.append(circle(726, yMid, 18, fill=BG, stroke=INK, sw=2))
    f.append(text(726, yMid + 6, "+", size=20, bold=True))
    f.append(arrow(746, yMid, 806, yMid, color=LINE))
    f.append(textbox(866, yMid, "vвих", size=13, bold=True,
                     fill="#eef7ee", stroke=FIELD, sw=2)[0])

    f.append(text(W / 2, 462,
                  "vвих = [ d(s)/(1+T) ] · vвх   +   [ r(s)/β ] · vвх",
                  size=15, bold=True))
    f.append(text(W / 2, H - 12,
                  "Перший доданок петля ділить на (1+T) і може загнати як завгодно низько; другий вона лише множить — нижче нього PSRR не опуститься",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "math-two-doors.svg"), W, H, *f)


# ── 5. Петля як шунт: PSRR = зазор між Zтр і спільним шунтом ──────────────────
def fig_shunt_impedances():
    W, H = 1000, 520
    f = [text(W / 2, 30, "PSRR = у скільки разів шунт до землі менший за опір, крізь який тече пульсація",
              size=15.5, bold=True)]

    # ═══ ЛІВА ПАНЕЛЬ: сам подільник ═══
    cx = 172
    f.append(text(cx, 66, "модель-подільник", size=12, color=INK, bold=True))
    f.append(wave(112, 100, 232, 7, 2.5, POS, sw=2.0))
    f.append(text(cx, 88, "vвх", size=11.5, color=POS, bold=True))
    f.append(line(cx, 100, cx, 126, color=LINE, sw=1.8))
    f.append(fitbox(cx - 34, 126, 68, 48, "Zтр", size=14, bold=True,
                    fill="#f4f6f8", stroke=INK, sw=1.8))
    f.append(line(cx, 174, cx, 208, color=LINE, sw=1.8))
    f.append(circle(cx, 208, 4.5, fill=LINE, stroke=LINE))
    f.append(text(cx + 14, 205, "vвих", size=11.5, color=FIELD, bold=True, anchor="start"))

    # два шунти паралельно
    f.append(line(96, 208, 248, 208, color=LINE, sw=1.8))
    f.append(line(96, 208, 96, 238, color=LINE, sw=1.8))
    f.append(line(248, 208, 248, 238, color=LINE, sw=1.8))
    f.append(fitbox(66, 238, 60, 46, "Zпетлі", size=12, bold=True,
                    fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(fitbox(218, 238, 60, 46, "Zвих", size=12, bold=True,
                    fill="#eef7ee", stroke=FIELD, sw=1.8))
    f.append(line(96, 284, 96, 316, color=LINE, sw=1.8))
    f.append(line(248, 284, 248, 316, color=LINE, sw=1.8))
    f.append(line(96, 316, 248, 316, color=LINE, sw=1.8))
    # земля
    f.append(line(cx - 26, 316, cx + 26, 316, color=INK, sw=2.6))
    f.append(line(cx - 17, 324, cx + 17, 324, color=INK, sw=2.2))
    f.append(line(cx - 8, 332, cx + 8, 332, color=INK, sw=2))

    f.append(text(85, 300, "петля", size=10, color=NEG, anchor="end"))
    f.append(text(259, 300, "конденсатор", size=10, color=FIELD, anchor="start"))
    f.append(text(cx, 362, "PSRR = Zтр / (Zпетлі ∥ Zвих)", size=13, bold=True))
    f.append(text(cx, 388, "шунтує той, хто МЕНШИЙ:", size=10.5, color=MUTED))
    f.append(text(cx, 405, "на низьких — петля,", size=10.5, color=NEG))
    f.append(text(cx, 421, "на високих — конденсатор,", size=10.5, color=FIELD))
    f.append(text(cx, 437, "посередині — ніхто", size=10.5, color=POS, bold=True))

    # роздільник панелей
    f.append(line(330, 60, 330, 460, color="#dde3ea", sw=1.4))

    # ═══ ПРАВА ПАНЕЛЬ: три імпеданси vs частота ═══
    x0, y0 = 400, 430
    plotW, plotH = 555, 330
    xR, yT = x0 + plotW, y0 - plotH

    def px(fz):
        return x0 + (math.log10(fz) - 1) / 6.0 * plotW

    def py(z):
        return y0 - (math.log10(z) + 2) / 5.0 * plotH

    # сітка по імпедансу
    for z, lab in ((0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"),
                   (100, "100"), (1000, "1000")):
        f.append(line(x0, py(z), xR, py(z), color="#e6ebf0", sw=1.1))
        f.append(text(x0 - 10, py(z) + 4, lab, size=10, color=MUTED, anchor="end"))
    f.append(text(x0 - 6, yT - 14, "Ом", size=11, color=INK, anchor="end"))

    # сітка по частоті
    for i, lab in enumerate(["10 Гц", "100 Гц", "1 кГц", "10 кГц", "100 кГц", "1 МГц", "10 МГц"]):
        xx = x0 + i / 6.0 * plotW
        f.append(line(xx, yT, xx, y0, color="#eef1f5", sw=1.0))
        f.append(text(xx, y0 + 19, lab, size=10, color=MUTED))
    f.append(line(x0, yT, x0, y0, color=INK, sw=1.6))
    f.append(line(x0, y0, xR, y0, color=INK, sw=1.6))
    f.append(text(xR, y0 + 38, "частота →", size=11, color=INK, anchor="end"))

    # моделі імпедансів
    def z_tr(fz):
        if fz <= 1e4:
            return 200.0
        if fz >= 2e5:
            return 10.0
        return 200.0 * 1e4 / fz

    def z_out(fz):
        return max(0.1, min(33.0, 159155.0 / fz))

    def z_loop(fz):
        return 0.06 * max(1.0, fz / 1000.0)

    def shunt(fz):
        return 1.0 / (1.0 / z_out(fz) + 1.0 / z_loop(fz))

    def curve(fn, color, sw, dash=None):
        pts = []
        for i in range(241):
            fz = 10 ** (1 + 6.0 * i / 240)
            pts.append("%.1f,%.1f" % (px(fz), py(fn(fz))))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (" ".join(pts), color, sw, d))

    f.append(curve(shunt, POS, 5.0))
    f.append(curve(z_out, FIELD, 2.2))
    f.append(curve(z_loop, NEG, 2.2))
    f.append(curve(z_tr, INK, 2.4))

    # легенда — над полем, окремим рядком (нічого не перетинає)
    leg = [(372, INK, "Zтр"), (452, FIELD, "Zвих"), (546, NEG, "Zпетлі"),
           (648, POS, "спільний шунт = Zпетлі ∥ Zвих")]
    for lx, col, lab in leg:
        f.append(line(lx, 66, lx + 18, 66, color=col, sw=3.4))
        f.append(text(lx + 23, 70, lab, size=10.5, color=INK, anchor="start"))

    # зазори = PSRR
    def gap(fz, label, side="middle"):
        out = []
        xx = px(fz)
        ya, yb = py(z_tr(fz)), py(shunt(fz))
        out.append(line(xx, ya, xx, yb, color=MUTED, sw=1.4, dash="4 3"))
        out.append(arrow(xx, ya + 6, xx, ya - 1, color=MUTED, sw=1.4))
        out.append(arrow(xx, yb - 6, xx, yb + 1, color=MUTED, sw=1.4))
        out.append(text(xx + (7 if side == "start" else -7), (ya + yb) / 2 + 4, label,
                        size=11, color=INK, bold=True,
                        anchor="start" if side == "start" else "end"))
        return out

    f.extend(gap(100, "70 дБ", "start"))
    f.extend(gap(50000, "28 дБ", "start"))
    f.extend(gap(3e6, "40 дБ", "end"))

    # провал
    f.append(text(px(50000), py(shunt(50000)) + 26, "провал: петля вже квола,", size=10, color=POS))
    f.append(text(px(50000), py(shunt(50000)) + 40, "конденсатор ще не шунтує", size=10, color=POS))

    f.append(text(W / 2, H - 12,
                  "Асимптоти схематичні (Cвих 1 мкФ, ESR 0.1 Ом, Rнав 33 Ом): вертикальний зазор між чорною лінією і червоною — і є PSRR у децибелах",
                  size=10.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "math-shunt-impedances.svg"), W, H, *f)


# ── 6. Запас над dropout: межа насичення росте як корінь зі струму ────────────
def fig_headroom():
    W, H = 840, 450
    f = [text(W / 2, 30, "PSRR помирає НЕ на dropout, а раніше — на межі насичення",
              size=16, bold=True)]

    x0, y0 = 92, 360
    plotW, plotH = 560, 268
    xR, yT = x0 + plotW, y0 - plotH

    def px(i_a):
        return x0 + i_a / 0.5 * plotW

    def py(v):
        return y0 - v / 1.0 * plotH

    for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        f.append(line(x0, py(v), xR, py(v), color="#e6ebf0", sw=1.1))
        f.append(text(x0 - 10, py(v) + 4, "%.1f" % v, size=10, color=MUTED, anchor="end"))
    f.append(text(x0 - 4, yT - 26, "Uвх − Uвих, В", size=11, color=INK, anchor="middle"))

    for ma in (0, 100, 200, 300, 400, 500):
        f.append(line(px(ma / 1000.0), yT, px(ma / 1000.0), y0, color="#eef1f5", sw=1.0))
        f.append(text(px(ma / 1000.0), y0 + 19, "%d" % ma, size=10, color=MUTED))
    f.append(text(xR, y0 + 38, "струм навантаження, мА →", size=11, color=INK, anchor="end"))
    f.append(line(x0, yT, x0, y0, color=INK, sw=1.6))
    f.append(line(x0, y0, xR, y0, color=INK, sw=1.6))

    def v_sat(i_a):
        return math.sqrt(0.9 * i_a)

    def v_drop(i_a):
        return 0.8 * i_a

    def poly(fn, color, sw):
        pts = ["%.1f,%.1f" % (px(0.5 * k / 200), py(fn(0.5 * k / 200))) for k in range(201)]
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (" ".join(pts), color, sw))

    # смуга «тріод» між кривими
    band = ["%.1f,%.1f" % (px(0.5 * k / 120), py(v_sat(0.5 * k / 120))) for k in range(121)]
    band += ["%.1f,%.1f" % (px(0.5 * k / 120), py(v_drop(0.5 * k / 120))) for k in range(120, -1, -1)]
    f.append('<polygon points="%s" fill="#fdecea" stroke="none" opacity="0.75"/>' % " ".join(band))

    f.append(poly(v_sat, POS, 3.0))
    f.append(poly(v_drop, NEG, 2.6))

    f.append(text(xR + 8, py(v_sat(0.5)) - 8, "межа насичення", size=10.5, color=POS,
                  bold=True, anchor="start"))
    f.append(text(xR + 8, py(v_sat(0.5)) + 8, "Uов ∝ √Iнав", size=10.5, color=POS, anchor="start"))
    f.append(text(xR + 8, py(v_drop(0.5)) - 8, "межа dropout", size=10.5, color=NEG,
                  bold=True, anchor="start"))
    f.append(text(xR + 8, py(v_drop(0.5)) + 8, "Uдроп = Iнав·Rвідкр", size=10.5, color=NEG, anchor="start"))

    f.append(text(px(0.14), py(0.88), "насичення: петля має підсилення → PSRR живий",
                  size=11.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(px(0.30), py(0.30), "тріод: напруга ще тримається,", size=10.5, color=POS))
    f.append(text(px(0.30), py(0.30) + 15, "а PSRR уже помер", size=10.5, color=POS, bold=True))
    f.append(text(px(0.36), py(0.09), "dropout: попливе й сама напруга", size=10.5, color=NEG))

    # горизонталь «запас 0.5 В» і точка перетину
    f.append(line(x0, py(0.5), xR, py(0.5), color=INK, sw=1.6, dash="7 4"))
    f.append(text(x0 + 8, py(0.5) - 8, "запас 0.5 В", size=11, color=INK, bold=True, anchor="start"))
    ix = 0.5 * 0.5 / 0.9
    f.append(circle(px(ix), py(0.5), 5.5, fill=BG, stroke=INK, sw=2.4))
    f.append(line(px(ix), py(0.5), px(ix), y0, color=INK, sw=1.2, dash="3 3"))
    f.append(text(px(ix) + 8, py(0.5) + 20, "≈ 280 мА", size=11, color=INK, bold=True, anchor="start"))
    f.append(text(px(ix) + 8, py(0.5) + 35, "далі 0.5 В уже замало", size=10, color=MUTED, anchor="start"))

    f.append(text(W / 2, H - 12,
                  "Той самий запас 0.5 В на легкому навантаженні тримає PSRR, а на важкому — ні: межа насичення росте як корінь зі струму",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "math-headroom-sat.svg"), W, H, *f)


# ══ ФІГУРИ ДО ВСТАВКИ proj-psrr-measure.md ═══════════════════════════════════

def cap_sym(cx, cy, vertical=True, gap=9, plate=22, sw=2.4):
    """Символ конденсатора. vertical=True → пластини горизонтальні (гілка вниз)."""
    if vertical:
        return (line(cx - plate / 2, cy - gap / 2, cx + plate / 2, cy - gap / 2, INK, sw) +
                line(cx - plate / 2, cy + gap / 2, cx + plate / 2, cy + gap / 2, INK, sw))
    return (line(cx - gap / 2, cy - plate / 2, cx - gap / 2, cy + plate / 2, INK, sw) +
            line(cx + gap / 2, cy - plate / 2, cx + gap / 2, cy + plate / 2, INK, sw))


def gnd_sym(cx, cy, w=22):
    p = [line(cx, cy, cx, cy + 8, INK, 2)]
    for i, k in enumerate((1.0, 0.6, 0.25)):
        p.append(line(cx - w * k / 2, cy + 8 + i * 5, cx + w * k / 2, cy + 8 + i * 5, INK, 2))
    return "".join(p)


def dot(cx, cy, r=4.5, color=INK):
    return circle(cx, cy, r, fill=color, stroke=color, sw=1)


# ── 7. Стенд: як підмішати змінне на постійну шину ────────────────────────────
def fig_bench():
    W, H = 960, 560
    f = []
    rail = 132          # головна шина
    genY = 322          # шина генератора
    node = 430          # вузол інжекції

    # ── БЖ ──
    f.append(fitbox(40, rail - 34, 112, 68, "БЖ\n4.3 В", size=13, bold=True,
                    fill="#eef2f7", stroke="#7f93a8", sw=1.8))
    f.append(line(152, rail, 232, rail, INK, 2.4))

    # ── Rs ──
    f.append(rect(232, rail - 15, 76, 30, fill=BG, stroke=INK, sw=2.2, rx=3))
    f.append(text(270, rail + 5, "Rs 10 Ω", size=12, bold=True))
    f.append(text(270, rail - 28, "не дає БЖ проковтнути змінне", size=10.5, color=NEG))
    f.append(line(308, rail, node, rail, INK, 2.4))

    # ── вузол інжекції ──
    f.append(dot(node, rail))
    f.append(text(node, rail - 30, "вузол інжекції", size=11, color=POS, bold=True))
    f.append(text(node, rail - 14, "200 мВpp на 4.3 В", size=10, color=POS))

    # ── генератор → Cc → вузол ──
    f.append(fitbox(40, genY - 32, 112, 64, "генератор\n50 Ω", size=13, bold=True,
                    fill="#eef2f7", stroke="#7f93a8", sw=1.8))
    f.append(line(152, genY, 268, genY, INK, 2.4))
    f.append(cap_sym(282, genY, vertical=False))
    f.append(text(282, genY + 34, "Cc 100 µF", size=12, bold=True))
    f.append(line(296, genY, node, genY, INK, 2.4))
    f.append(line(node, genY, node, rail, INK, 2.4))

    # ── Cin ──
    f.append(line(478, rail, 478, rail + 42, INK, 2.2))
    f.append(cap_sym(478, rail + 52))
    f.append(gnd_sym(478, rail + 62))
    f.append(text(478 + 62, rail + 48, "Cin 1 µF", size=11.5, bold=True))

    # ── LDO ──
    f.append(fitbox(536, rail - 44, 152, 88, "LDO\n(випробовуваний)\n3.3 В", size=12.5,
                    bold=True, fill="#eef2f7", stroke="#7f93a8", sw=1.8))
    f.append(line(688, rail, 792, rail, INK, 2.4))

    # ── Cout ──
    f.append(line(726, rail, 726, rail + 42, INK, 2.2))
    f.append(cap_sym(726, rail + 52))
    f.append(gnd_sym(726, rail + 62))
    f.append(text(726 + 58, rail + 48, "Cout", size=11.5, bold=True))

    # ── навантаження ──
    f.append(dot(792, rail))
    f.append(rect(777, rail + 40, 30, 62, fill=BG, stroke=INK, sw=2.2, rx=3))
    f.append(line(792, rail, 792, rail + 40, INK, 2.2))
    f.append(gnd_sym(792, rail + 102))
    f.append(text(792 + 74, rail + 62, "66 Ω", size=11.5, bold=True))
    f.append(text(792 + 74, rail + 79, "50 мА", size=10.5, color=MUTED))

    # ── щупи ──
    for x, name, col in ((536, "CH1", POS), (688, "CH2", FIELD)):
        f.append(dot(x, rail, 5, col))
        f.append(line(x, rail, x, 62, col, 2, dash="5,4"))
        f.append(circle(x, 52, 11, fill=BG, stroke=col, sw=2.2))
        f.append(text(x, 56, name[-1], size=11, color=col, bold=True))
        f.append(text(x, 32, name, size=12, color=col, bold=True))

    # ── пояснення внизу ──
    f.append(fitbox(40, 402, 258, 62,
                    "Cc блокує постійку. Без нього\n4.3 В б'ють у вихід генератора",
                    size=11, fill="#eaf0fd", stroke=NEG, color=INK))
    f.append(fitbox(318, 402, 300, 62,
                    "Bulk-конденсатор на вході — ВИЙНЯТИ.\n"
                    "Саме він душить інжекцію на ВЧ",
                    size=11, fill="#fdecea", stroke=POS, color=INK))
    f.append(fitbox(638, 402, 282, 62,
                    "Щупи — на самі виводи LDO.\nНа клемах БЖ намірите Rs·Cin",
                    size=11, fill="#eafaf0", stroke=FIELD, color=INK))

    f.append(fitbox(40, 482, 880, 46,
                    "БЖ тримає робочу точку, генератор додає брижі, Rs розв'язує їх одне від одного — "
                    "а відношення CH2/CH1 і є PSRR",
                    size=12, fill=BG, stroke="#c9d3dc", color=INK, bold=True))

    return render(os.path.join(IMG, "proj-bench.svg"), W, H, *f,
                  title="Стенд: підмішати брижі, не зрушивши постійну точку")


# ── 8. Когерентне детектування: з-під шуму — у число ──────────────────────────
def fig_coherent():
    import random
    W, H = 960, 600
    f = []

    # ── верхня панель: сирий запис ──
    x0, x1, yc = 70, 620, 148
    hgt = 62
    f.append(rect(x0, yc - hgt, x1 - x0, 2 * hgt, fill="#fbfcfd", stroke="#c9d3dc", sw=1.4))
    f.append(text((x0 + x1) / 2, yc - hgt - 14, "Що бачить осцилограф (10 мВ/поділку, AC)",
                  size=13, bold=True))

    random.seed(11)
    pts, n = [], 700
    for i in range(n + 1):
        t = i / n
        x = x0 + t * (x1 - x0)
        sig = 6.0 * math.sin(2 * math.pi * 9 * t)          # «сигнал» 31.6 мкВpp
        noise = random.gauss(0, 26)                          # шум 250 мкВ RMS
        pts.append("%.1f,%.1f" % (x, max(yc - hgt + 3, min(yc + hgt - 3, yc - sig - noise))))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1"/>'
             % (" ".join(pts), "#8a97a5"))

    f.append(text(x1 + 22, yc - 26, "250 мкВ", size=12, color=INK, bold=True, anchor="start"))
    f.append(text(x1 + 22, yc - 10, "шуму", size=11, color=MUTED, anchor="start"))
    f.append(text(x1 + 22, yc + 16, "31.6 мкВpp", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(x1 + 22, yc + 32, "сигналу — десь", size=11, color=POS, anchor="start"))
    f.append(text(x1 + 22, yc + 47, "отут, під шумом", size=11, color=POS, anchor="start"))
    f.append(fitbox(x0, yc + hgt + 12, 300, 30, "сигнал на 21 дБ НИЖЧЕ шуму",
                    size=11.5, fill="#fdecea", stroke=POS, color=INK, bold=True))

    # ── стрілка-детектор ──
    f.append(arrow(345, 262, 345, 322, NEG, 3))
    f.append(fitbox(370, 262, 480, 62,
                    "помножити на еталон e^(−j2πf₀t) і усереднити\n"
                    "по N = 10⁶ відліків — усе, що не на f₀, гасне",
                    size=12, fill="#eaf0fd", stroke=NEG, color=INK, bold=True))

    # ── нижня панель: результат детектора ──
    bx0, bx1, by = 70, 620, 500
    f.append(line(bx0, by, bx1, by, INK, 2))
    f.append(text((bx0 + bx1) / 2, 362, "Що каже детектор", size=13, bold=True))

    # шумова підлога
    random.seed(3)
    fl = []
    for i in range(121):
        x = bx0 + i * (bx1 - bx0) / 120
        h = abs(random.gauss(0, 3.4))
        fl.append(line(x, by, x, by - h, "#9aa6b2", 1.4))
    f.append("".join(fl))

    # голка на f0
    fx = bx0 + 0.42 * (bx1 - bx0)
    f.append(line(fx, by, fx, by - 118, POS, 3.4))
    f.append(dot(fx, by - 118, 4, POS))
    f.append(text(fx, by - 128, "31.6 мкВ", size=12.5, color=POS, bold=True))
    f.append(text(fx, by + 18, "f₀", size=12, color=POS, bold=True))
    f.append(text(bx0 - 6, by + 18, "частота →", size=10.5, color=MUTED, anchor="start"))

    f.append(line(bx1 + 4, by - 12, bx1 + 4, by, MUTED, 1.6, dash="3,3"))
    f.append(text(bx1 + 12, by - 4, "σ_Â = 0.42 мкВ", size=11.5, color=MUTED,
                  bold=True, anchor="start"))
    f.append(text(bx1 + 12, by - 106, "+37 дБ", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(bx1 + 12, by - 90, "сигнал/шум", size=11, color=FIELD, anchor="start"))

    f.append(fitbox(70, 534, 820, 44,
                    "Той самий запис. Детектор не «бачить краще» — він знає частоту наперед "
                    "і складає N відліків у фазі, а шум додається врозбрід",
                    size=12, fill=BG, stroke="#c9d3dc", color=INK, bold=True))

    return render(os.path.join(IMG, "proj-coherent.svg"), W, H, *f,
                  title="Сигнал під шумом — і те саме число після когерентного детектора")


# ── 9. Скільки брижів дотягує дешевий інжектор ────────────────────────────────
def fig_injector_reach():
    W, H = 960, 560
    f = []
    L, R, T, B = 96, 700, 78, 424     # поле графіка

    fmin, fmax = 1.0, 7.0             # log10(Гц): 10 Гц … 2 МГц (з запасом)
    vmin, vmax = 0.0, 3.4             # log10(мВpp): 1 … ~2500

    def lx(fr):
        return L + (math.log10(fr) - fmin) / (fmax - fmin) * (R - L)

    def ly(mv):
        return B - (math.log10(mv) - vmin) / (vmax - vmin) * (B - T)

    def reach(fr, Cin):
        w = 2 * math.pi * fr
        Zcc = 1 / (1j * w * 100e-6)
        Zcin = 1 / (1j * w * Cin)
        Zn = 1 / (1 / 10.0 + 1 / Zcin)
        return abs(Zn / (50.0 + Zcc + Zn)) * 10 * 1e3     # мВpp при 10 Vpp генератора

    # зона «замало»
    f.append(rect(L, ly(20), R - L, B - ly(20), fill="#fdecea", stroke="none", sw=0, rx=0))
    f.append(line(L, ly(20), R, ly(20), POS, 1.6, dash="6,4"))
    f.append(text(L + 8, ly(20) + 18, "замало для впевненого відліку", size=11,
                  color=POS, anchor="start", bold=True))

    # сітка й підписи
    for d in range(1, 7):
        x = lx(10 ** d)
        f.append(line(x, T, x, B, "#e3e8ee", 1))
        lab = {1: "10 Гц", 2: "100 Гц", 3: "1 кГц", 4: "10 кГц",
               5: "100 кГц", 6: "1 МГц"}[d]
        f.append(text(x, B + 22, lab, size=11, color=MUTED))
    for d in range(0, 4):
        y = ly(10 ** d)
        f.append(line(L, y, R, y, "#e3e8ee", 1))
        lab = {0: "1", 1: "10", 2: "100", 3: "1000"}[d]
        f.append(text(L - 12, y + 4, lab, size=11, color=MUTED, anchor="end"))
    f.append(line(L, T, L, B, INK, 2))
    f.append(line(L, B, R, B, INK, 2))
    f.append(text(L - 62, (T + B) / 2 - 12, "мВpp", size=12, color=INK, bold=True))
    f.append(text(L - 62, (T + B) / 2 + 6, "на вузлі", size=11, color=MUTED))
    f.append(text((L + R) / 2, B + 48, "частота інжекції", size=12, color=INK, bold=True))

    # криві
    for Cin, col, nm in ((1e-6, FIELD, "Cin = 1 µF"), (10e-6, POS, "Cin = 10 µF")):
        pts = []
        fr = 10.0
        while fr <= 2e6:
            v = reach(fr, Cin)
            if v >= 1.0:
                pts.append("%.1f,%.1f" % (lx(fr), ly(v)))
            fr *= 1.06
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                 % (" ".join(pts), col))
        f.append(text(lx(1.2e3), ly(reach(1.2e3, Cin)) - (16 if Cin < 5e-6 else -22),
                      nm, size=12, color=col, bold=True))

    # стрілка «виймаємо bulk»
    xa = lx(5e5)
    f.append(arrow(xa, ly(reach(5e5, 10e-6)) - 4, xa, ly(reach(5e5, 1e-6)) + 4, NEG, 2.6))
    f.append(fitbox(xa + 16, ly(reach(5e5, 1e-6)) - 6, 210, 46,
                    "виймаємо bulk →\n+20 дБ інжекції", size=11.5,
                    fill="#eaf0fd", stroke=NEG, color=INK, bold=True))

    f.append(fitbox(724, T, 214, 96,
                    "Стеля — 50 Ω генератора\nі Cin. Вище кількох сотень\nкГц дешевий інжектор\nвидихається",
                    size=11, fill="#fdecea", stroke=POS, color=INK))
    f.append(fitbox(724, T + 112, 214, 96,
                    "Але це НЕ біда: калібрувати\nінжектор не треба —\nми міряємо і вхід теж,\nа відношення його з'їдає",
                    size=11, fill="#eafaf0", stroke=FIELD, color=INK))

    f.append(fitbox(96, 470, 842, 62,
                    "Генератор на 10 Vpp через Cc = 100 µF і Rs = 10 Ω. Найдужче інжекція б'є коло кілогерца; "
                    "нижче її ріже Cc, вище — Cin.\nТам, де PSRR найглибший (низи), брижів удосталь; де інжекції "
                    "обмаль (верхи), там і придушення мале — і це рятує",
                    size=11.5, fill=BG, stroke="#c9d3dc", color=INK))

    return render(os.path.join(IMG, "proj-injector-reach.svg"), W, H, *f,
                  title="Скільки брижів дешевий інжектор дотягує на вузол")


if __name__ == "__main__":
    fig_mechanism()
    fig_curve()
    fig_cascade()
    fig_two_doors()
    fig_shunt_impedances()
    fig_headroom()
    fig_bench()
    fig_coherent()
    fig_injector_reach()
    print("OK: figures ->", IMG)
