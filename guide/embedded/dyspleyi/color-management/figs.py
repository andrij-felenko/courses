# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Управління кольором: колірні профілі та гама».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

LAMP  = "#caa24a"
LAMPF = "#fff4c2"


# ── 1. Дві криві, що гасять одна одну ────────────────────────────────────────
def fig_gamma_curve():
    W, H = 860, 430
    f = [text(W / 2, 32, "Гама: дві дзеркальні криві, що разом дають пряму", size=19, bold=True),
         text(W / 2, 53, "перо стискає світло (енкодинг), панель його відновлює (декодинг) — на оці виходить лінійно",
              size=12.5, color=MUTED, italic=True)]

    def axes(x0, y0, w, h, xlab, ylab):
        f.append(arrow(x0, y0, x0 + w + 18, y0, color=INK, sw=2))
        f.append(arrow(x0, y0, x0, y0 - h - 18, color=INK, sw=2))
        f.append(text(x0 + w + 14, y0 + 18, xlab, size=11.5, color=MUTED, anchor="end"))
        f.append(text(x0 - 6, y0 - h - 8, ylab, size=11.5, color=MUTED, anchor="start"))

    def curve(x0, y0, w, h, fn, color, sw=2.6, dash=None):
        pts = []
        for i in range(0, 51):
            t = i / 50.0
            v = fn(t)
            pts.append("%.1f,%.1f" % (x0 + t * w, y0 - v * h))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (" ".join(pts), color, sw, (' stroke-dasharray="%s"' % dash) if dash else ''))

    GAM = 2.2
    # ── ліва панель: енкодинг (стиснення) ──
    x0, y0, w, h = 96, 350, 220, 230
    axes(x0, y0, w, h, "яскравість світла", "код у пам'яті")
    f.append(line(x0, y0, x0 + w, y0 - h, color=MUTED, sw=1.3, dash="4 4"))
    f.append(curve(x0, y0, w, h, lambda t: t ** (1.0 / GAM), NEG))
    f.append(text(x0 + w / 2, y0 - h - 30, "ЕНКОДИНГ  код = світло^(1/2.2)", size=12.5, color=NEG, bold=True))
    f.append(text(x0 + 150, y0 - 150, "темне", size=11, color=MUTED, anchor="start"))
    f.append(text(x0 + 150, y0 - 134, "розтягнуте", size=11, color=MUTED, anchor="start"))

    # ── права панель: декодинг (розтиск) ──
    x0 = 540
    axes(x0, y0, w, h, "код у пам'яті", "яскравість світла")
    f.append(line(x0, y0, x0 + w, y0 - h, color=MUTED, sw=1.3, dash="4 4"))
    f.append(curve(x0, y0, w, h, lambda t: t ** GAM, POS))
    f.append(text(x0 + w / 2, y0 - h - 30, "ДЕКОДИНГ  світло = код^2.2", size=12.5, color=POS, bold=True))
    f.append(text(x0 + 30, y0 - 175, "панель", size=11, color=MUTED, anchor="start"))
    f.append(text(x0 + 30, y0 - 159, "(або таблиця)", size=11, color=MUTED, anchor="start"))

    # стрілка-зв'язка між панелями
    f.append(arrow(330, 235, 532, 235, color=FIELD, sw=2.2))
    f.append(text(431, 224, "одне гасить друге", size=12, color=FIELD, bold=True))
    f.append(text(431, 408, "1/2.2 потім ×2.2 = 1: око бачить рівно ту яскравість, що задумали.",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "gamma-curve.svg"), W, H, *f)


# ── 2. Чому 8 лінійних біт «бандять» у тінях ─────────────────────────────────
def fig_banding():
    W, H = 840, 410
    f = [text(W / 2, 32, "Куди витратити 256 кодів: порівну по світлу чи порівну по оку", size=19, bold=True),
         text(W / 2, 53, "око гостріше в тінях; лінійний крок там завеликий — проступають смуги (banding)",
              size=12.5, color=MUTED, italic=True)]

    # шкала зверху: лінійні рівні (рідко в тінях, густо вгорі по сприйняттю)
    bx, bw, by = 90, 660, 96
    f.append(text(bx - 12, by + 22, "лінійно", size=12.5, bold=True, anchor="end"))
    f.append(text(bx - 12, by + 38, "по світлу", size=11, color=MUTED, anchor="end"))
    # 9 рівних за яскравістю кроків → у сприйнятті стиснуті в тінях
    n = 9
    for i in range(n):
        t = i / (n - 1.0)
        # перцептивна позиція ~ світло^(1/2.2): рівні-за-світлом кроки збиваються вліво
        px = bx + (t ** (1.0 / 2.2)) * bw
        g = int(round(t * 255))
        col = "#%02x%02x%02x" % (g, g, g)
        f.append(rect(px - 13, by, 26, 44, fill=col, stroke=MUTED, sw=1, rx=2))
    # дужка «тут смуги»
    f.append(line(bx, by + 60, bx + 200, by + 60, color=POS, sw=2))
    f.append(text(bx + 100, by + 76, "великі стрибки → СМУГИ", size=12, color=POS, bold=True))
    f.append(text(bx + 470, by + 76, "кроки тісняться — біти змарновано", size=12, color=MUTED, italic=True))

    # шкала знизу: гама-рівні (рівні для ока)
    by2 = 250
    f.append(text(bx - 12, by2 + 22, "гама", size=12.5, bold=True, anchor="end"))
    f.append(text(bx - 12, by2 + 38, "по оку", size=11, color=MUTED, anchor="end"))
    for i in range(n):
        t = i / (n - 1.0)              # рівномірно за КОДОМ
        px = bx + t * bw              # → рівномірно у сприйнятті
        lin = t ** 2.2               # назад у світло, щоб показати реальну яскравість плитки
        g = int(round(lin * 255))
        col = "#%02x%02x%02x" % (g, g, g)
        f.append(rect(px - 13, by2, 26, 44, fill=col, stroke=MUTED, sw=1, rx=2))
    f.append(line(bx, by2 + 60, bx + bw, by2 + 60, color=FIELD, sw=2))
    f.append(text(bx + bw / 2, by2 + 76, "кроки рівні для ока → переходи гладенькі", size=12, color=FIELD, bold=True))

    f.append(text(W / 2, 388, "Гама-кодування дарує тіням більше кодів — там, де око прискіпливіше. Те саме число біт, кращий вигляд.",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "banding.svg"), W, H, *f)


# ── 3. Колірне охоплення: трикутник стандарту і трикутник дешевої панелі ──────
def fig_gamut():
    W, H = 760, 470
    f = [text(W / 2, 32, "Колірне охоплення: який шматок видимих кольорів панель узагалі вміє", size=18, bold=True),
         text(W / 2, 53, "вершини трикутника — три первинні кольори панелі; усе всередині вона може змішати",
              size=12.5, color=MUTED, italic=True)]

    # «підкова» видимого спектра — згладжена замкнена крива (схематична, не за CIE-точно)
    ox, oy, sx, sy = 150, 410, 330, 330
    horseshoe = [
        (0.17, 0.00), (0.08, 0.20), (0.05, 0.40), (0.07, 0.60),
        (0.15, 0.78), (0.30, 0.90), (0.45, 0.83), (0.55, 0.70),
        (0.62, 0.55), (0.66, 0.38), (0.68, 0.22), (0.66, 0.08),
        (0.55, 0.02), (0.40, 0.00),
    ]
    pts = " ".join("%.1f,%.1f" % (ox + a * sx, oy - b * sy) for a, b in horseshoe)
    f.append('<polygon points="%s" fill="#eef1f4" stroke="#b8c2cb" stroke-width="1.4"/>' % pts)
    f.append(text(ox + 0.20 * sx, oy - 0.92 * sy, "усі видимі кольори", size=11.5, color=MUTED, anchor="start"))

    def triangle(rp, gp, bp, color, fill, sw, dash=None):
        P = [rp, gp, bp]
        s = " ".join("%.1f,%.1f" % (ox + a * sx, oy - b * sy) for a, b in P)
        d = (' stroke-dasharray="%s"' % dash) if dash else ''
        return ('<polygon points="%s" fill="%s" fill-opacity="0.18" stroke="%s" '
                'stroke-width="%.1f"%s/>' % (s, fill, color, sw, d))

    # стандартний sRGB-трикутник (більший)
    sr, sg, sb = (0.64, 0.18), (0.30, 0.60), (0.15, 0.06)
    f.append(triangle(sr, sg, sb, INK, "#7fa9c4", 2.4))
    # дешева панель — менший і зсунутий (тьмяніші, «брудніші» первинні)
    pr, pg, pb = (0.55, 0.21), (0.33, 0.50), (0.18, 0.10)
    f.append(triangle(pr, pg, pb, POS, "#e08f86", 2.2, dash="6 4"))

    for (a, b), lab, col in [(sr, "R", POS), (sg, "G", FIELD), (sb, "B", NEG)]:
        f.append(circle(ox + a * sx, oy - b * sy, 5, fill=col, stroke=BG, sw=1.5))

    # легенда
    f.append(rect(515, 110, 28, 14, fill="#7fa9c4", stroke=INK, sw=1.4, rx=2))
    f.append(text(550, 122, "стандарт sRGB", size=12, anchor="start"))
    f.append(rect(515, 138, 28, 14, fill="#e08f86", stroke=POS, sw=1.4, rx=2))
    f.append(text(550, 150, "дешева панель", size=12, anchor="start", color=POS))
    f.append(text(515, 182, "Менший трикутник =", size=12, anchor="start", color=MUTED, italic=True))
    f.append(text(515, 199, "панель не дотягує до", size=12, anchor="start", color=MUTED, italic=True))
    f.append(text(515, 216, "насичених кольорів —", size=12, anchor="start", color=MUTED, italic=True))
    f.append(text(515, 233, "вони виходять блякліші.", size=12, anchor="start", color=MUTED, italic=True))

    f.append(text(W / 2, 452, "Той самий код кольору на ширшій і вужчій панелі дасть різний відтінок — ось чому потрібен спільний еталон.",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "gamut.svg"), W, H, *f)


# ── 4. Практичний конвеєр кольору у вбудованій системі ───────────────────────
def fig_pipeline():
    W, H = 880, 360
    f = [text(W / 2, 32, "Конвеєр кольору: від макета до скла — де код стає світлом", size=19, bold=True),
         text(W / 2, 53, "значення збережено в гама-кодуванні (sRGB); десь по дорозі його треба декодувати в світло",
              size=12.5, color=MUTED, italic=True)]

    def box(x, y, w, h, title, sub, fill=FILL, stroke=INK):
        f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8))
        f.append(text(x + w / 2, y + 26, title, size=13.5, bold=True))
        if sub:
            f.append(text(x + w / 2, y + 47, sub, size=11, color=MUTED))

    y = 110
    box(40, y, 170, 78, "Макет / шрифт", "значення sRGB", fill="#eef4ff", stroke=NEG)
    box(250, y, 180, 78, "Кадровий буфер МК", "ті самі коди в RAM", fill=FILL)
    box(470, y, 180, 78, "Контролер / панель", "перетворює код у світло", fill="#fff4e8", stroke=LAMP)
    box(700, y, 140, 78, "Око", "бачить яскравість", fill="#eaf7ee", stroke=FIELD)

    f.append(arrow(210, y + 39, 248, y + 39, color=INK, sw=2))
    f.append(arrow(430, y + 39, 468, y + 39, color=INK, sw=2))
    f.append(arrow(650, y + 39, 698, y + 39, color=INK, sw=2))

    # де живе гама-декодинг
    f.append(rect(250, 232, 400, 58, fill="#fff8e8", stroke=LAMP, sw=1.6, rx=8))
    f.append(text(450, 254, "ТУТ діє гама: панель (LCD), таблиця LUT або математика в коді", size=12.5, bold=True, color="#9a7d2e"))
    f.append(text(450, 274, "блендінг і градієнти рахуй у ЛІНІЙНОМУ світлі, інакше темнітиме й брудниться", size=11.5, color=MUTED, italic=True))
    f.append(arrow(360, 232, 340, 190, color=LAMP, sw=1.8))
    f.append(arrow(540, 232, 560, 190, color=LAMP, sw=1.8))

    f.append(text(W / 2, 326, "Помилка: змішати напівпрозорі кольори прямо в кодах sRGB — результат виходить темнішим за правильний.",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "pipeline.svg"), W, H, *f)


# ── 5. Гама-таблиця: резисторна драбина гне криву «код → яскравість» ──────────
def fig_gamma_ladder():
    W, H = 880, 470
    f = [text(W / 2, 30, "Гама-таблиця: кілька регістрів-кілків гнуть цілу криву", size=19, bold=True),
         text(W / 2, 51, "регістри посувають вузли резисторної драбини → ЦАП віддає інші напруги → крива згинається",
              size=12.5, color=MUTED, italic=True)]

    # ── ЛІВОРУЧ: резисторна драбина з кілками-регістрами ──
    lx, ltop, lbot = 150, 90, 410
    f.append(text(lx, 78, "резисторна драбина", size=12.5, bold=True, anchor="middle"))
    # вертикальна шина драбини
    f.append(line(lx, ltop, lx, lbot, color=INK, sw=2.4))
    f.append(text(lx - 70, ltop + 4, "V+ опорна", size=11, color=MUTED, anchor="start"))
    f.append(text(lx - 70, lbot + 4, "V− опорна", size=11, color=MUTED, anchor="start"))
    # вузли-кілки: рівномірно стоять, але «посунуті» вбік — це регістр
    n = 9
    knot_off = [0, 14, 26, 30, 22, 10, -8, -20, -28]  # «викривлення» драбини регістрами
    for i in range(n):
        ty = ltop + (lbot - ltop) * i / (n - 1.0)
        # маленький резистор-сегмент як рисочка
        if i < n - 1:
            ty2 = ltop + (lbot - ltop) * (i + 1) / (n - 1.0)
            f.append(line(lx, ty, lx, ty2, color="#9aa3ad", sw=5))
        kx = lx + 24 + knot_off[i]
        f.append(line(lx, ty, kx, ty, color=POS, sw=1.6))
        f.append(circle(kx, ty, 5.5, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(lx + 60, ltop - 2, "кілки = гама-регістри", size=11, color=POS, anchor="start", bold=True))
    f.append(text(lx + 60, ltop + 13, "(посув вузла = зсув", size=10.5, color=MUTED, anchor="start", italic=True))
    f.append(text(lx + 60, ltop + 27, " опорної напруги)", size=10.5, color=MUTED, anchor="start", italic=True))

    # ЦАП-міст до правого графіка
    f.append(text(330, lbot + 18, "ЦАП обирає рівень з драбини за кодом", size=11.5, color=FIELD, bold=True, anchor="middle"))
    f.append(arrow(lx + 70, lbot + 28, 505, lbot + 28, color=FIELD, sw=2.2))

    # ── ПРАВОРУЧ: крива код → яскравість (сира vs виправлена 2.2) ──
    gx0, gy0, gw, gh = 520, 410, 300, 300
    f.append(arrow(gx0, gy0, gx0 + gw + 16, gy0, color=INK, sw=2))
    f.append(arrow(gx0, gy0, gx0, gy0 - gh - 16, color=INK, sw=2))
    f.append(text(gx0 + gw + 12, gy0 + 18, "код", size=11.5, color=MUTED, anchor="end"))
    f.append(text(gx0 - 6, gy0 - gh - 6, "яскравість", size=11.5, color=MUTED, anchor="start"))
    f.append(line(gx0, gy0, gx0 + gw, gy0 - gh, color=MUTED, sw=1.1, dash="3 4"))

    def curve(fn, color, sw=2.8, dash=None):
        pts = []
        for i in range(0, 61):
            t = i / 60.0
            pts.append("%.1f,%.1f" % (gx0 + t * gw, gy0 - fn(t) * gh))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (" ".join(pts), color, sw, (' stroke-dasharray="%s"' % dash) if dash else ''))

    # сира фізична крива панелі — помітно горбата (пунктир)
    def raw(t):
        return max(0.0, min(1.0, t ** 1.7 + 0.22 * math.sin(t * 3.14159)))
    f.append(curve(raw, MUTED, sw=2.2, dash="7 4"))
    # виправлена крива 2.2 (суцільна)
    f.append(curve(lambda t: t ** 2.2, POS))
    f.append(text(gx0 + 96, gy0 - 188, "сира крива панелі", size=11, color=MUTED, anchor="start", italic=True))
    f.append(text(gx0 + 158, gy0 - 92, "виправлена 2.2", size=11.5, color=POS, anchor="start", bold=True))

    f.append(text(W / 2, 452, "Контролер тримає не всю криву, а ~10–16 кілків; точки між ними драйвер добудовує сам по драбині.",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "gamma-ladder.svg"), W, H, *f)


# ── 6. Часова стрічка γ: фотографія → телебачення → цифра (вставка hist) ──────
def fig_gamma_history():
    W, H = 900, 430
    f = [text(W / 2, 30, "Життя кривої γ крізь століття: причина мінялася тричі, крива — ні", size=18, bold=True),
         text(W / 2, 51, "один показник степеня переходив від плівки до гармати, тоді до файлу — і жодного разу не зник",
              size=12.5, color=MUTED, italic=True)]

    ax_y = 360
    x0, x1 = 70, 830
    f.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2))
    f.append(arrow(x1 - 4, ax_y, x1 + 16, ax_y, color=INK, sw=2))
    f.append(text(x1 + 14, ax_y + 20, "час", size=11.5, color=MUTED, anchor="end"))

    eras = [
        (x0 + 6,  248, "#e8eefb", NEG,      "ФОТОГРАФІЯ"),
        (338,     330, "#fdf0e4", "#c77f2e", "ТЕЛЕБАЧЕННЯ"),
        (683,     147, "#e8f6ec", FIELD,    "ЦИФРА"),
    ]
    for ex, ew, fill, ec, lab in eras:
        f.append(rect(ex, 78, ew, ax_y - 90, fill=fill, stroke="none", sw=0, rx=10))
        f.append(text(ex + ew / 2, 98, lab, size=12.5, bold=True, color=ec))

    def node(x, year, head, subs, col, by):
        b, bw, bh = textbox(x, by, head + "\n" + subs, size=11, pad=7,
                            fill=BG, stroke=col, sw=1.6, color=INK, bold=False)
        cx = min(max(x, x0 + bw / 2), x1 - bw / 2)
        b, bw, bh = textbox(cx, by, head + "\n" + subs, size=11, pad=7,
                            fill=BG, stroke=col, sw=1.6, color=INK, bold=False)
        f.append(b)
        f.append(line(x, by + bh / 2, x, ax_y - 8, color=col, sw=1.3, dash="3 3"))
        f.append(circle(x, ax_y, 6, fill=col, stroke=BG, sw=2))
        f.append(text(x, ax_y + 24, year, size=12, bold=True, color=col))

    node(150, "1890", "Гуртер і Дріффілд", "γ — нахил кривої плівки\n(міра контрасту)", NEG, 150)
    node(415, "1930-ті", "Гармата CRT", "світло ∝ сигнал^2.5\nкамера кодує ^0.45", "#c77f2e", 150)
    node(585, "ХХ ст.", "Економіка ТБ", "коректор — у камеру,\nне в мільйони ТВ", "#c77f2e", 250)
    node(760, "1996", "sRGB (HP+MS)", "крива застигає в стандарті\nIEC 61966-2-1, 1999", FIELD, 150)

    f.append(text(W / 2, 408, "Народилась у темній кімнаті фотографа, виросла в електронній гарматі, застигла у файлі — та сама γ.",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "gamma-history.svg"), W, H, *f)


if __name__ == "__main__":
    fig_gamma_curve()
    fig_banding()
    fig_gamut()
    fig_pipeline()
    fig_gamma_ladder()
    fig_gamma_history()
    print("OK: 6 figures ->", IMG)
