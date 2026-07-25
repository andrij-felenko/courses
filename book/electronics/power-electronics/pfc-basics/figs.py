# -*- coding: utf-8 -*-
"""Фігури до статті «Корекція коефіцієнта потужності (PFC)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CUR = "#e8820c"    # струм — жовтогарячий
CURD = "#b5660a"   # темніший підпис струму


def poly(pts, color, sw=2.6, dash=None, fill="none"):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (pts, fill, color, sw, d))


def sine(x0, x1, ymid, amp, cycles=1.0, phase=0.0, n=260):
    """Повна (двополярна) синусоїда."""
    pts = []
    for i in range(n + 1):
        t = i / n
        xx = x0 + t * (x1 - x0)
        s = math.sin(2 * math.pi * cycles * t + phase)
        pts.append("%.1f,%.1f" % (xx, ymid - amp * s))
    return " ".join(pts)


def spikes(x0, x1, ymid, amp, cycles=1.5, w=14):
    """Двополярні вузькі піки на вершинах синусоїди напруги (форма струму випрямляча)."""
    out = []
    # вершини sin припадають на фази, де 2π·cycles·t = π/2 + kπ
    k = 0
    while True:
        # позиція k-ї вершини (додатної при парних k, від'ємної при непарних)
        t = (0.25 + 0.5 * k) / cycles
        if t > 1.0:
            break
        xc = x0 + t * (x1 - x0)
        sign = 1 if k % 2 == 0 else -1
        pk = ymid - sign * amp
        out.append(poly("%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f"
                        % (xc - w, ymid, xc - w * 0.4, ymid - sign * amp * 0.9,
                           xc, pk, xc + w * 0.4, ymid - sign * amp * 0.9, xc + w, ymid),
                        CUR, sw=2.8))
        k += 1
    return "".join(out)


def rounded_pulse(x0, x1, ymid, amp, cycles=1.5, n=260):
    """Широкий похилий горб — струм після пасивного дроселя (|sin| у степені <1, ширший)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        xx = x0 + t * (x1 - x0)
        s = math.sin(2 * math.pi * cycles * t)
        # ширший, нижчий горб зі збереженням знаку
        val = math.copysign(abs(s) ** 0.62, s)
        pts.append("%.1f,%.1f" % (xx, ymid - amp * val))
    return " ".join(pts)


# ── Фіг.1 — дві хвороби, два ліки ────────────────────────────────────────────
def fig_two_diseases():
    W, H = 980, 486
    f = [text(W / 2, 32, "Дві незалежні хвороби коефіцієнта потужності — два різні ліки", size=17, bold=True)]

    def panel(x0, title_txt, tcolor, kind):
        w = 452
        out = [rect(x0, 62, w, 296, fill="none", stroke="#d8dde3", sw=2, rx=12)]
        out.append(text(x0 + w / 2, 88, title_txt, size=13.5, color=tcolor, bold=True))
        gx0, gx1 = x0 + 44, x0 + w - 28
        ymid = 200
        out.append(line(gx0, ymid, gx1, ymid, color="#cfcfcf", sw=1.2))
        # напруга мережі — синя синусоїда (пунктир)
        out.append(poly(sine(gx0, gx1, ymid, 74, cycles=1.5), NEG, sw=2.0, dash="6,4"))
        out.append(text(gx0 + 6, ymid - 80, "напруга", size=10.5, color=NEG, anchor="start", bold=True))
        if kind == "shift":
            # струм — синусоїда, зсунута (запізнюється)
            out.append(poly(sine(gx0, gx1, ymid, 58, cycles=1.5, phase=-1.1), CUR, sw=3.0))
            out.append(text(x0 + w / 2, 312, "струм синусоїдний, але ЗСУНУТИЙ у часі", size=11.5, color=CURD))
            out.append(text(x0 + w / 2, 336, "винен cos φ  →  лікує КОНДЕНСАТОР (компенсація)", size=12, color=tcolor, bold=True))
        else:
            # струм — вузькі піки на вершинах напруги
            out.append(spikes(gx0, gx1, ymid, 92, cycles=1.5))
            out.append(text(x0 + w / 2, 312, "струм У ФАЗІ, але рваний — не синусоїда", size=11.5, color=CURD))
            out.append(text(x0 + w / 2, 336, "винні ГАРМОНІКИ  →  лікує формування струму", size=12, color=tcolor, bold=True))
        return "".join(out)

    f.append(panel(24, "ЗСУВ — мотор, трансформатор, дросель", NEG, "shift"))
    f.append(panel(504, "СПОТВОРЕННЯ — випрямляч + конденсатор", POS, "distort"))
    f.append(fitbox(70, 382, 840, 74,
                    ["Спершу — ДІАГНОЗ, тоді лік. Конденсатор прибирає ЗСУВ (тягне протилежний реактивний струм),",
                     "але проти СПОТВОРЕННЯ форми він безсилий: там треба перемалювати сам струм — дроселем або активним PFC.",
                     "Той самий присуд «PF = 0.6» означає різні поломки з різними інструментами — сплутати їх найдорожче."],
                    size=11.5, fill="#eef2fb", stroke=NEG))
    render(os.path.join(IMG, "two-diseases.svg"), W, H, *f)


# ── Фіг.2 — три форми струму: без корекції / пасивна / активна ────────────────
def fig_three_currents():
    W, H = 1000, 392
    f = [text(W / 2, 30, "Три способи взяти струм з навантаження — від рваних піків до синусоїди", size=16, bold=True)]

    def panel(x0, title_txt, sub, pf, tcolor, kind):
        w = 306
        out = [rect(x0, 56, w, 232, fill="none", stroke="#d8dde3", sw=2, rx=10)]
        out.append(text(x0 + w / 2, 80, title_txt, size=12.5, color=tcolor, bold=True))
        gx0, gx1 = x0 + 30, x0 + w - 22
        ymid = 178
        out.append(line(gx0, ymid, gx1, ymid, color="#cfcfcf", sw=1.1))
        # напруга-огинальна (пунктир, синя)
        out.append(poly(sine(gx0, gx1, ymid, 58, cycles=1.5), NEG, sw=1.6, dash="5,4"))
        if kind == "raw":
            out.append(spikes(gx0, gx1, ymid, 72, cycles=1.5, w=11))
        elif kind == "passive":
            out.append(poly(rounded_pulse(gx0, gx1, ymid, 50, cycles=1.5), CUR, sw=3.0))
        else:
            out.append(poly(sine(gx0, gx1, ymid, 48, cycles=1.5), CUR, sw=3.0))
        out.append(text(x0 + w / 2, 258, sub, size=10.5, color=CURD))
        out.append(text(x0 + w / 2, 278, pf, size=13, color=tcolor, bold=True))
        return "".join(out)

    f.append(panel(22, "БЕЗ КОРЕКЦІЇ", "вузькі високі піки", "PF ≈ 0.6", POS, "raw"))
    f.append(panel(347, "ПАСИВНА — дросель", "пік розмазано ширше", "PF ≈ 0.85", "#b5660a", "passive"))
    f.append(panel(672, "АКТИВНА — boost-PFC", "струм у формі напруги", "PF ≈ 0.99", FIELD, "active"))
    f.append(text(W / 2, 320, "Синя пунктирна — напруга мережі; жовтогаряча — струм. Що ближчий струм до форми напруги, то вищий PF і менше гармонік.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "three-currents.svg"), W, H, *f)


# ── Фіг.3 — місце PFC у блоці живлення ───────────────────────────────────────
def fig_chain():
    W, H = 1020, 300
    f = [text(W / 2, 32, "Де стоїть каскад PFC: вхідний каскад, а не весь блок живлення", size=16, bold=True)]
    out = []
    y = 96
    h = 78
    # блоки: (x, w, рядки, заливка, обведення)
    blocks = [
        (24, 92, ["~ мережа"], "#f6f9fc", INK),
        (140, 118, ["запобіжник", "+ фільтр", "завад"], "#f6f9fc", INK),
        (282, 108, ["діодний", "міст"], "#f6f9fc", INK),
        (414, 132, ["КАСКАД", "PFC"], "#eafaf0", FIELD),
        (570, 118, ["конден-", "сатор шини", "~400 В"], "#f6f9fc", INK),
        (712, 132, ["DC-DC", "(розв'язка)"], "#eef2fb", NEG),
        (868, 128, ["стабільний", "вихід"], "#f6f9fc", INK),
    ]
    for i, (x, w, lines, fill, stroke) in enumerate(blocks):
        sw = 2.4 if lines[0] == "КАСКАД" else 1.8
        out.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=9))
        cy = y + h / 2 - (len(lines) - 1) * 15 / 2 + 5
        bold = (lines[0] == "КАСКАД")
        col = FIELD if bold else INK
        for j, ln in enumerate(lines):
            out.append(text(x + w / 2, cy + j * 15, ln, size=11.5 if not bold else 12.5,
                            color=col if j == 0 else INK, bold=bold))
        # стрілка до наступного
        if i < len(blocks) - 1:
            nx = blocks[i + 1][0]
            out.append(arrow(x + w + 2, y + h / 2, nx - 3, y + h / 2, color=INK, sw=1.8))

    # виноска під каскадом PFC
    px = 414 + 132 / 2
    out.append(line(px, y + h, px, y + h + 22, color=FIELD, sw=1.6))
    out.append(text(px, y + h + 40, "робить ВХІДНИЙ СТРУМ чесним", size=11, color=FIELD, bold=True))
    # виноска під DC-DC
    dx = 712 + 132 / 2
    out.append(line(dx, y + h, dx, y + h + 22, color=NEG, sw=1.6))
    out.append(text(dx, y + h + 40, "стабілізує ВИХІД для навантаження", size=11, color=NEG, bold=True))

    out.append(fitbox(70, 244, 880, 40,
                      ["PFC відповідає за ФОРМУ вхідного струму (щоб мережа бачила майже резистор), а не за якість виходу —",
                       "точну, розв'язану від мережі напругу робить уже наступний DC-DC каскад. Ролі не плутати."],
                      size=11, fill="#eafaf0", stroke=FIELD))
    f.extend(out)
    render(os.path.join(IMG, "chain.svg"), W, H, *f)


# ── Фіг.4 (вставка hist) — триплен-гармоніки складаються в нейтралі ───────────
def fig_triplen_neutral():
    W, H = 1020, 512
    pw = 224
    cols_x = [24, 260, 496, 732]
    heads = ["Фаза A", "Фаза B", "Фаза C", "Σ у нейтралі"]
    f = [text(W / 2, 30, "Чому нейтраль перегрівається: основна гармоніка гаситься, а третя — потроюється",
              size=15, bold=True)]

    def mini(x, y, title, headcolor, wave):
        gx0, gx1, ymid = x + 16, x + pw - 12, y + 52
        return "".join([
            rect(x, y, pw, 104, fill="none", stroke="#d8dde3", sw=1.6, rx=9),
            text(x + pw / 2, y - 9, title, size=11.5, color=headcolor, bold=True),
            line(gx0, ymid, gx1, ymid, color="#cfcfcf", sw=1.0),
            wave,
        ])

    # Рядок 1 — основна гармоніка (120° між фазами) → сума ≈ 0
    ry1 = 100
    f.append(text(W / 2, ry1 - 30, "ОСНОВНА гармоніка — фази зсунуті на 120°, у нейтралі гасяться",
                  size=12.5, color=NEG, bold=True))
    amp1 = 30
    ph = [0.0, -2 * math.pi / 3, -4 * math.pi / 3]
    for i in range(3):
        x = cols_x[i]
        gx0, gx1, ymid = x + 16, x + pw - 12, ry1 + 52
        f.append(mini(x, ry1, heads[i], INK, poly(sine(gx0, gx1, ymid, amp1, cycles=1.0, phase=ph[i]), CUR, sw=2.6)))
    x = cols_x[3]
    gx0, gx1, ymid = x + 16, x + pw - 12, ry1 + 52
    f.append(mini(x, ry1, heads[3], FIELD, poly(sine(gx0, gx1, ymid, 2.5, cycles=1.0), FIELD, sw=2.8)))
    f.append(text(x + pw / 2, ry1 + 34, "≈ 0", size=14, color=FIELD, bold=True))

    # Рядок 2 — третя гармоніка (усі у фазі) → сума ×3
    ry2 = 300
    f.append(text(W / 2, ry2 - 30, "ТРЕТЯ гармоніка (триплен) — усі фази В ФАЗІ, у нейтралі складаються",
                  size=12.5, color=POS, bold=True))
    amp3 = 15
    for i in range(3):
        x = cols_x[i]
        gx0, gx1, ymid = x + 16, x + pw - 12, ry2 + 52
        f.append(mini(x, ry2, heads[i], INK, poly(sine(gx0, gx1, ymid, amp3, cycles=3.0), CUR, sw=2.6)))
    x = cols_x[3]
    gx0, gx1, ymid = x + 16, x + pw - 12, ry2 + 52
    f.append(mini(x, ry2, heads[3], POS, poly(sine(gx0, gx1, ymid, 44, cycles=3.0), POS, sw=2.8)))
    f.append(text(x + pw / 2, ry2 + 34, "×3", size=14, color=POS, bold=True))

    f.append(fitbox(52, 440, 916, 60,
                    ["Струм кожного комп'ютера — синусоїда основної частоти ПЛЮС сильна третя гармоніка. Основні по трьох фазах зсунуті на 120° і в нейтралі гасяться;",
                     "а треті зсунуті на 3·120° = 360°, тобто ЗБІГАЮТЬСЯ, і в нейтралі додаються втричі. Тому в офісі, повному ПК, нейтраль вантажиться дужче за фазні —",
                     "хоч її й кладуть найтоншою, часто без власного запобіжника. Звідси перегріті нейтралі й трансформатори, з яких і почався тиск на виробників."],
                    size=11, fill="#fbeeec", stroke=POS))
    render(os.path.join(IMG, "triplen-neutral.svg"), W, H, *f)


# ── Фіг.5 (вставка hist) — часова смуга: як PFC стала обов'язком ──────────────
def fig_pfc_timeline():
    W, H = 1140, 432
    f = [text(W / 2, 32, "Від засмічених мереж до норми: як корекція коефіцієнта потужності стала обов'язком",
              size=15, bold=True)]
    ax_y = 250
    x0, x1 = 70, 1064
    f.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2.4))
    f.append(arrow(x1 - 2, ax_y, x1 + 26, ax_y, color=INK, sw=2.4))

    def xof(year):
        return x0 + (year - 1974) / (2002 - 1974) * (x1 - x0)

    nodes = [
        (1976, "down", "1970-80-ті · SMPS", ["Вхід «міст + конденсатор»", "ширяється, мережа", "повниться гармоніками"], CURD),
        (1982, "up",   "1982 · IEC 555-2", ["Перший ліміт гармонік", "(робота з 1977) —", "але ДОБРОВІЛЬНИЙ"], NEG),
        (1989, "down", "1988–90 · активний PFC", ["Преформатор Unitrode,", "average-current-mode,", "контролерні мікросхеми"], FIELD),
        (1994, "up",   "1993–95 · 61000-3-2", ["Перенумерація в", "EMC-родину, 1-ша", "редакція 1995"], NEG),
        (2001, "down", "2001 · ОБОВ'ЯЗКОВО", ["1 січня набуває", "чинності в ЄС за", "Директивою EMC"], POS),
    ]
    bw, bh = 216, 104
    for year, side, head, lines, col in nodes:
        nx = xof(year)
        f.append(circle(nx, ax_y, 6, fill=col, stroke=col, sw=1.5))
        bx = min(max(nx - bw / 2, 14), W - 14 - bw)
        if side == "up":
            by = ax_y - 30 - bh
            f.append(line(nx, ax_y - 7, nx, by + bh, color=col, sw=1.4, dash="4,3"))
        else:
            by = ax_y + 30
            f.append(line(nx, ax_y + 7, nx, by, color=col, sw=1.4, dash="4,3"))
        f.append(rect(bx, by, bw, bh, fill="#f6f9fc", stroke=col, sw=1.7, rx=8))
        f.append(text(bx + bw / 2, by + 23, head, size=12, color=col, bold=True))
        f.append(mtext(bx + bw / 2, by + 45, lines, size=10.5, color=INK, lh=1.3))
    render(os.path.join(IMG, "pfc-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_diseases()
    fig_three_currents()
    fig_chain()
    fig_triplen_neutral()
    fig_pfc_timeline()
    print("OK: 5 фігур у", IMG)
