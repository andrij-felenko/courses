# -*- coding: utf-8 -*-
"""Фігури до теми «Саморозряд батареї».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Три шляхи саморозряду: ідеал проти реальної комірки ───────────────────────
def fig_paths():
    W, H = 860, 470
    f = [text(W / 2, 30, "Куди тече заряд зсередини комірки", size=16, bold=True)]

    def cell(cx, top, w, h, label, col):
        """Проста комірка: два електроди й електроліт між ними."""
        out = [rect(cx - w / 2, top, w, h, fill="#f6f6f6", stroke=MUTED, sw=1.5)]
        ew = w * 0.16
        # лівий електрод (+) червоний, правий (−) синій
        out.append(rect(cx - w / 2 + 6, top + 6, ew, h - 12, fill="#fbeee6", stroke=POS, sw=1.6))
        out.append(rect(cx + w / 2 - 6 - ew, top + 6, ew, h - 12, fill="#eaf0fd", stroke=NEG, sw=1.6))
        out.append(text(cx - w / 2 + 6 + ew / 2, top + h / 2 + 5, "+", size=17, bold=True, color=POS))
        out.append(text(cx + w / 2 - 6 - ew / 2, top + h / 2 + 5, "−", size=17, bold=True, color=NEG))
        # електроліт-підпис по центру
        out.append(text(cx, top + h - 12, "електроліт", size=9.5, color=MUTED))
        out.append(text(cx, top - 10, label, size=12, bold=True, color=col))
        return out, ew

    cw, chh = 250, 200
    ly = 84
    lcx, rcx = 215, 630

    # ЛІВА — ідеал: заряд стоїть
    parts, ew = cell(lcx, ly, cw, chh, "Ідеал: заряд стоїть", FIELD)
    f += parts
    f.append(text(lcx, ly + chh / 2 - 6, "нічого", size=12, color=FIELD, bold=True))
    f.append(text(lcx, ly + chh / 2 + 12, "не тече", size=12, color=FIELD, bold=True))

    # ПРАВА — реальність: три шляхи витоку
    parts, ew = cell(rcx, ly, cw, chh, "Реальність: три витоки", POS)
    f += parts
    inL = rcx - cw / 2 + 6 + ew          # внутрішній край лівого електрода
    inR = rcx + cw / 2 - 6 - ew          # внутрішній край правого електрода
    midy = ly + chh / 2
    # (1) побічні реакції — хвилясті стрілочки біля обох електродів усередину
    f.append(arrow(inL + 6, ly + 34, inL + 40, ly + 34, color=POS, sw=2.0))
    f.append(arrow(inR - 6, ly + 34, inR - 40, ly + 34, color=NEG, sw=2.0))
    f.append(text(rcx, ly + 30, "①", size=13, bold=True, color=INK))
    # (2) мікрокоротке — ламаний місток крізь сепаратор (домішка)
    f.append(line(inL + 4, midy + 18, rcx - 8, midy + 6, color=INK, sw=2.2))
    f.append(line(rcx - 8, midy + 6, rcx + 10, midy + 26, color=INK, sw=2.2))
    f.append(line(rcx + 10, midy + 26, inR - 4, midy + 14, color=INK, sw=2.2))
    f.append(circle(rcx + 1, midy + 16, 4.5, fill="#777", stroke=INK, sw=1.0))
    f.append(text(rcx + 2, midy + 46, "②", size=13, bold=True, color=INK))
    # (3) поверхневий витік — дуга поверх корпусу
    ytop = ly - 4
    f.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" '
             'stroke-width="2.0" stroke-dasharray="4,3"/>'
             % (rcx - cw / 2 + 10, ytop, rcx, ytop - 34, rcx + cw / 2 - 10, ytop, MUTED))
    f.append(text(rcx, ytop - 40, "③", size=13, bold=True, color=INK))

    # легенда під правою коміркою
    lx, ly2 = 470, 316
    legend = [
        ("①", "побічні хімічні реакції на електродах — тихо «спалюють» активну речовину", POS),
        ("②", "мікрокоротке крізь металеву домішку в сепараторі — електрони навпростець", INK),
        ("③", "поверхневий витік по вологій/брудній поверхні — зазвичай дрібний", MUTED),
    ]
    for i, (mk, txt, col) in enumerate(legend):
        yy = ly2 + i * 26
        f.append(text(lx, yy, mk, size=13, bold=True, color=col, anchor="start"))
        f.append(text(lx + 26, yy, txt, size=11, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, 440,
                      "у реальній комірці заряд саджається зсередини трьома шляхами; ① і ② — головні.\nхімічні реакції (①) частково незворотні — це водночас старіння комірки.",
                      size=10.5, fill="#fbeee6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "paths.svg"), W, H, *f)


# ── Місячний саморозряд за хіміями (логарифмічна шкала) ───────────────────────
def fig_rates():
    W, H = 860, 460
    f = [text(W / 2, 30, "Місячний саморозряд: розкид понад стократний", size=16, bold=True)]
    # (назва, репрезентативний %/міс для довжини стовпця, підпис-діапазон, колір, заливка)
    bars = [
        ("Лужна\n(первинна)", 0.2, "~0.1–0.3 %/міс", FIELD, "#e9f7ef"),
        ("Літій\n(первинний)", 0.13, "~1–2 %/РІК", FIELD, "#e9f7ef"),
        ("Li-ion", 2.0, "~1–3 %/міс", "#caa24a", "#fbf3df"),
        ("LiFePO₄", 1.2, "~0.5–2 %/міс", "#caa24a", "#fbf3df"),
        ("Свинець", 5.0, "~4–6 %/міс", POS, "#fbeee6"),
        ("Нікель\n(NiMH/NiCd)", 12.0, "~10–15 %/міс", POS, "#fbeee6"),
    ]
    # логарифмічна вісь: від 0.1 до 20 %/міс
    ox, oy = 250, 360
    plot_w = 540
    lo, hi = 0.1, 20.0

    def xlog(v):
        t = (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
        return ox + t * plot_w

    # сітка з підписами-декадами
    for gv in (0.1, 1, 10):
        gx = xlog(gv)
        f.append(line(gx, 70, gx, oy, color="#e3e3e3", sw=1.0))
        lab = ("%.1f" % gv) if gv < 1 else ("%d" % gv)
        f.append(text(gx, oy + 20, lab + " %/міс", size=9.5, color=MUTED))
    f.append(line(ox, oy, ox + plot_w, oy, color=MUTED, sw=1.3))

    bh, gap = 34, 12
    y = 80
    for name, val, rng, col, fill in bars:
        x1 = xlog(lo)
        x2 = xlog(val)
        f.append(rect(x1, y, x2 - x1, bh, fill=fill, stroke=col, sw=1.8))
        # назва хімії ліворуч від осі
        f.append(mtext(ox - 16, y + bh / 2 - (name.count("\n")) * 6 + 5, name,
                       size=10.5, color=INK, anchor="end", lh=1.15, bold=True))
        # діапазон — праворуч від кінця стовпця
        f.append(text(x2 + 10, y + bh / 2 + 4, rng, size=10.5, color=col, anchor="start", bold=True))
        y += bh + gap

    b, _, _ = textbox(W / 2, 428,
                      "первинні системи (лужна, метал-літій) живуть роками; звичайний нікель саджається за тижні.\nувага: у ГОТОВОМУ виробі до Li-ion додається ще й мікрострум спокою BMS (кілька %/міс зверху).",
                      size=10.5, fill="#e9f7ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "rates.svg"), W, H, *f)


# ── Модель витоку: паралельний опір і експоненційний спад ─────────────────────
def fig_rc():
    W, H = 860, 430
    f = [text(W / 2, 30, "Витік як опір паралельно комірці → спад по exp(−t/τ)", size=15, bold=True)]

    # ЛІВОРУЧ: еквівалентна схема — джерело + C + R_sd паралельно
    ecx = 175
    top, bot = 90, 300
    # два вузли (клеми) — вертикальні шини
    xL, xR = ecx - 70, ecx + 70
    f.append(line(xL, top, xL, bot, color=INK, sw=2.0))
    f.append(line(xR, top, xR, bot, color=INK, sw=2.0))
    f.append(text(ecx, top - 14, "комірка (клеми розімкнені)", size=10.5, color=MUTED))
    # гілка 1: ідеальна ємність запасу C (сама «батарея») — прямокутник-конденсатор
    ymid = (top + bot) / 2
    f.append(line(xL, ymid, xL + 40, ymid, color=INK, sw=1.6))
    # символ конденсатора (дві пластини)
    px = ecx - 30
    f.append(line(px, ymid - 22, px, ymid + 22, color=NEG, sw=3.0))
    f.append(line(px + 10, ymid - 22, px + 10, ymid + 22, color=NEG, sw=3.0))
    f.append(line(xR, ymid, px + 10, ymid, color=INK, sw=1.6))
    f.append(line(xL + 40, ymid, px, ymid, color=INK, sw=1.6))
    f.append(text(ecx - 6, ymid + 40, "C — запас заряду", size=10, color=NEG, bold=True))
    f.append(text(ecx - 6, ymid + 54, "(ідеальна комірка)", size=9, color=MUTED))
    # гілка 2: R_sd — резистор паралельно, нижче
    ry = bot - 6
    f.append(line(xL, ry, xL + 30, ry, color=INK, sw=1.6))
    f.append(rect(xL + 30, ry - 9, 70, 18, fill="#fbeee6", stroke=POS, sw=1.8))
    f.append(text(xL + 65, ry + 4, "R_sd", size=11, color=POS, bold=True))
    f.append(line(xL + 100, ry, xR, ry, color=INK, sw=1.6))
    f.append(text(ecx, ry + 26, "опір витоку — тут «тече» заряд", size=9.5, color=POS))

    # ПРАВОРУЧ: крива exp-спаду напруги
    ox, oy = 400, 300
    pw, ph = 400, 210
    f.append(line(ox, oy - ph, ox, oy, color=MUTED, sw=1.3))   # вісь Y
    f.append(line(ox, oy, ox + pw, oy, color=MUTED, sw=1.3))    # вісь X
    f.append(text(ox - 8, oy - ph + 4, "U", size=11, color=INK, anchor="end", bold=True))
    f.append(text(ox + pw, oy + 18, "час t →", size=10.5, color=MUTED, anchor="end"))
    U0 = oy - ph + 14
    # крива U = U0*exp(-t/tau) у координатах екрана
    tau_px = 120.0
    pts = []
    for i in range(0, pw + 1, 4):
        t = i
        y = oy - (oy - U0) * math.exp(-t / tau_px)
        pts.append("%.1f,%.1f" % (ox + i, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), POS))
    # позначка τ: у t=τ напруга спадає до 0.37 від початкового над «дном»
    tx = ox + tau_px
    ytau = oy - (oy - U0) * math.exp(-1)
    f.append(line(tx, oy, tx, ytau, color=NEG, sw=1.3, dash="4,3"))
    f.append(line(ox, ytau, tx, ytau, color=NEG, sw=1.3, dash="4,3"))
    f.append(text(tx, oy + 18, "t = τ = R_sd·C", size=10, color=NEG, bold=True))
    f.append(text(ox + 6, ytau - 6, "лишилось ≈37 %", size=9.5, color=NEG, anchor="start"))
    f.append(text(ox + 6, U0 - 6, "повний заряд", size=9.5, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, 400,
                      "витік моделюють опором R_sd паралельно ємності запасу C: заряд стікає сам, і напруга спадає\nпо exp(−t/τ), τ = R_sd·C. велике R_sd (чиста здорова комірка) → величезне τ → майже горизонталь.",
                      size=10.5, fill="#fbeee6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "rc-model.svg"), W, H, *f)


# ── Дві часові шкали: швидке осідання + повільний усталений витік ─────────────
def fig_twoscales():
    W, H = 860, 430
    f = [text(W / 2, 30, "Дві складові: швидке осідання (доба) + усталений витік (місяці)", size=15, bold=True)]
    ox, oy = 120, 300
    pw, ph = 660, 220
    f.append(line(ox, oy - ph, ox, oy, color=MUTED, sw=1.3))
    f.append(line(ox, oy, ox + pw, oy, color=MUTED, sw=1.3))
    f.append(text(ox - 10, oy - ph + 6, "заряд, %", size=10.5, color=INK, anchor="end"))
    f.append(text(ox + pw, oy + 20, "час →", size=10.5, color=MUTED, anchor="end"))
    # рівні 100 і 95 для орієнтиру
    y100 = oy - ph + 20
    def yq(q):  # q у % від 0..100 → екран (показуємо діапазон 70..100)
        return oy - (q - 70) / 30.0 * (ph - 24)
    for q in (100, 95, 90, 80, 70):
        yy = yq(q)
        f.append(line(ox, yy, ox + pw, yy, color="#eee", sw=1.0))
        f.append(text(ox - 8, yy + 4, "%d" % q, size=9, color=MUTED, anchor="end"))

    # межа фаз
    xsplit = ox + 150
    f.append(line(xsplit, oy - ph, xsplit, oy, color="#ccc", sw=1.2, dash="5,4"))
    f.append(text((ox + xsplit) / 2, oy - ph - 4, "перша доба", size=10, color=NEG, bold=True))
    f.append(text((xsplit + ox + pw) / 2, oy - ph - 4, "далі — місяці сну", size=10, color=POS, bold=True))

    # ФАЗА 1: крутий exp-спад 100 → 95 у межах першої доби (осідання, зворотне)
    pts1 = []
    for i in range(0, 151, 3):
        frac = 1 - math.exp(-i / 45.0)      # від 0 до ~0.96
        q = 100 - 5 * frac
        pts1.append("%.1f,%.1f" % (ox + i, yq(q)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts1), NEG))
    # ФАЗА 2: пологий майже-лінійний спад 95 → 79 (усталений хімічний витік)
    q_start = 95.0
    pts2 = []
    for i in range(0, pw - 150 + 1, 4):
        t = i
        q = q_start * math.exp(-0.00042 * t)   # м'який exp, майже пряма
        pts2.append("%.1f,%.1f" % (xsplit + i, yq(q)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts2), POS))

    # підписи-виноски
    f.append(text(ox + 60, yq(100) - 8, "≈5 % за добу", size=10, color=NEG, bold=True, anchor="start"))
    f.append(text(ox + 60, yq(100) + 8, "ОСІДАННЯ — зворотне,", size=9, color=NEG, anchor="start"))
    f.append(text(ox + 60, yq(100) + 20, "повертається зарядкою", size=9, color=NEG, anchor="start"))
    f.append(text(xsplit + 240, yq(90), "усталений витік —", size=10, color=POS, bold=True, anchor="start"))
    f.append(text(xsplit + 240, yq(90) + 13, "переважно незворотний,", size=9, color=POS, anchor="start"))
    f.append(text(xsplit + 240, yq(90) + 25, "«з'їдений» реакціями заряд", size=9, color=POS, anchor="start"))

    b, _, _ = textbox(W / 2, 400,
                      "одразу після заряду напруга завищена — за добу комірка ОСІДАЄ (зворотне, ~5 %); далі йде рівний\nусталений витік (відсотки на місяць). міряти саморозряд можна лише ПІСЛЯ осідання, інакше воно бреше.",
                      size=10.5, fill="#eaf0fd", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "two-scales.svg"), W, H, *f)


# ── Незворотна складова росте як √t (дифузійне сповільнення), не лінійно ───────
def fig_sqrt():
    W, H = 820, 430
    f = [text(W / 2, 30, "Незворотна втрата росте як √t — сама себе гальмує", size=15, bold=True)]
    ox, oy = 110, 300
    pw, ph = 620, 220
    f.append(line(ox, oy - ph, ox, oy, color=MUTED, sw=1.3))
    f.append(line(ox, oy, ox + pw, oy, color=MUTED, sw=1.3))
    f.append(text(ox - 10, oy - ph + 6, "втрачено, %", size=10.5, color=INK, anchor="end"))
    f.append(text(ox + pw, oy + 20, "час t →", size=10.5, color=MUTED, anchor="end"))

    scale = 175.0   # px на «одиницю» втрати
    # √t-крива: Q = A*sqrt(t)
    A = 5.2
    ptsS = []
    for i in range(0, pw + 1, 3):
        t = i / float(pw) * 36.0     # 0..36 місяців
        q = A * math.sqrt(t)
        ptsS.append("%.1f,%.1f" % (ox + i, oy - q / 40.0 * ph))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(ptsS), POS))
    # наївна пряма (постійний темп) для контрасту
    ptsL = []
    for i in range(0, pw + 1, 6):
        t = i / float(pw) * 36.0
        q = 0.62 * t
        y = oy - q / 40.0 * ph
        if y < oy - ph:
            break
        ptsL.append("%.1f,%.1f" % (ox + i, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="6,4"/>' % (" ".join(ptsL), MUTED))

    # осі часу: підписи місяців
    for m in (0, 9, 18, 27, 36):
        gx = ox + m / 36.0 * pw
        f.append(line(gx, oy, gx, oy + 5, color=MUTED, sw=1.0))
        f.append(text(gx, oy + 18, "%d" % m, size=9, color=MUTED))
    f.append(text(ox + pw / 2, oy + 34, "місяці", size=9.5, color=MUTED))

    # підписи кривих
    f.append(text(ox + pw - 8, oy - A * math.sqrt(36) / 40.0 * ph - 8,
                  "√t — товща плівки SEI, реальність", size=10.5, color=POS, bold=True, anchor="end"))
    f.append(text(ox + 210, oy - 0.62 * 20 / 40.0 * ph - 8,
                  "наївна пряма (сталий темп)", size=10, color=MUTED, anchor="start"))
    # стрілочка: темп спадає (нахили на початку й у кінці)
    f.append(text(ox + 40, oy - A * math.sqrt(3.0) / 40.0 * ph - 10, "круто", size=9, color=POS, anchor="start"))
    f.append(text(ox + pw - 60, oy - A * math.sqrt(34) / 40.0 * ph + 16, "полого", size=9, color=POS, anchor="end"))

    b, _, _ = textbox(W / 2, 400,
                      "плівка SEI сама собі бар'єр: товща вона — повільніше крізь неї доходять реагенти, тож незворотна\nвтрата йде як √t, а миттєвий темп — як 1/√t (спадає). за 4× часу втрата лише ×2, не ×4.",
                      size=10.5, fill="#fbeee6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "sqrt-law.svg"), W, H, *f)


# ── Драбина термінів придатності: витік проти утримання за роками (hist) ──────
def fig_shelf_timeline():
    W, H = 900, 470
    f = [text(W / 2, 30, "Від «сідає на очах» до «тримає роками»", size=16, bold=True)]

    # Рядки-віхи: (рік/мітка, назва події, утримання-текст, колір-акцент, заливка)
    rows = [
        ("до 2005", "Звичайний NiMH", "≈70% ВТРАЧЕНО за місяць", POS, "#fbeee6"),
        ("2005", "Sanyo Eneloop (1-ше пок.)", "80% ще на місці через рік", "#caa24a", "#fbf3df"),
        ("2010", "2-ге покоління", "85% через рік", "#caa24a", "#fbf3df"),
        ("2011", "3-тє покоління", "70% через 5 років", FIELD, "#e9f7ef"),
        ("2022", "5-те покоління", "70% через 10 РОКІВ", FIELD, "#e9f7ef"),
    ]

    lblx = 150          # права межа колонки з роком (поза стрічкою)
    barx = 178          # старт «стрічки» події
    barw = 688          # ширша стрічка — щоб довгі підписи не тислися
    y = 74
    rh, gap = 58, 12
    for yr, ev, hold, col, fill in rows:
        # рік — окремим стовпчиком ліворуч, поза стрічкою
        f.append(text(lblx, y + rh / 2 + 5, yr, size=13, bold=True, color=INK, anchor="end"))
        # стрічка події
        f.append(rect(barx, y, barw, rh, fill=fill, stroke=col, sw=1.8))
        # назва події — верхній рядок усередині стрічки
        f.append(text(barx + 16, y + 23, ev, size=12.5, bold=True, color=INK, anchor="start"))
        # утримання — нижній рядок усередині стрічки
        f.append(text(barx + 16, y + 44, hold, size=12, color=col, anchor="start", bold=True))
        y += rh + gap

    # вертикальна вісь часу — повз написи, ліворуч від стрічок
    f.append(line(barx - 13, 74, barx - 13, y - gap, color=MUTED, sw=1.3))

    b, _, _ = textbox(W / 2, 452,
                      "розв'язок — не нова хімія електрода, а матеріали: сплав міцніше тримає водень,\n"
                      "а сульфонований сепаратор не пускає хімічні «човники» — усе при тій самій формі батарейки.",
                      size=10.5, fill="#e9f7ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "shelf-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_paths()
    fig_rates()
    fig_rc()
    fig_twoscales()
    fig_sqrt()
    fig_shelf_timeline()
    print("OK: 6 figures ->", IMG)
