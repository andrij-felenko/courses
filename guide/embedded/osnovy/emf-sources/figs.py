# -*- coding: utf-8 -*-
"""Фігури до теми «Типи ЕРС: хімічна, теплова, світлова, індукційна».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

HOT = "#c0392b"      # гарячий спай / тепло
COLD = "#2457d6"     # холодний спай
SUN = "#e0a800"      # світло / фотон
COIL = "#7a4 db".replace(" ", "")  # котушка (фіолетовий)
COIL = "#7a4ddb"


def tb(cx, cy, s, **kw):
    """textbox → лише SVG-тіло (відкидаємо повернені w,h)."""
    body, _w, _h = textbox(cx, cy, s, **kw)
    return body


def cap(W, lines, y0, size=10.5):
    if isinstance(lines, str):
        lines = [lines]
    out = []
    for i, ln in enumerate(lines):
        out.append(text(W / 2, y0 + i * (size + 4), ln, size=size, color=MUTED, italic=True))
    return out


# ════════════════════════════════════════════════════════════════════════════
# 1. Чотири джерела ЕРС — одна ідея: насос заряду
# ════════════════════════════════════════════════════════════════════════════
def fig_four():
    W, H = 760, 430
    f = [text(W / 2, 26, "Джерело ЕРС — насос заряду; різна лише стороння сила", size=16, bold=True)]

    # центральна схема насоса
    cx, cy = W / 2, 150
    # коробка-джерело
    f.append(rect(cx - 70, cy - 55, 140, 110, fill="#eef2f7", stroke=INK, sw=2))
    f.append(text(cx, cy - 38, "джерело ЕРС", size=12, bold=True))
    # внутрішня стрілка-насос (від − до +, угору проти поля)
    f.append(arrow(cx, cy + 38, cx, cy - 14, color=FIELD, sw=3))
    f.append(text(cx + 52, cy + 14, "стороння", size=10.5, color=FIELD, anchor="middle"))
    f.append(text(cx + 52, cy + 27, "сила", size=10.5, color=FIELD, anchor="middle"))
    # затискачі
    f.append(plus(cx, cy - 55, r=11))
    f.append(minus(cx, cy + 55, r=11))
    # зовнішнє коло — заряд тече сам, віддає енергію навантаженню
    f.append(line(cx, cy - 66, cx + 150, cy - 66, color=INK, sw=2))
    f.append(line(cx + 150, cy - 66, cx + 150, cy + 66, color=INK, sw=2))
    f.append(line(cx + 150, cy + 66, cx, cy + 66, color=INK, sw=2))
    # навантаження
    f.append(rect(cx + 130, cy - 18, 40, 36, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(cx + 150, cy + 5, "R", size=13, bold=True))
    # стрілка струму зовні
    f.append(arrow(cx + 80, cy - 66, cx + 120, cy - 66, color=POS, sw=2))
    f.append(text(cx + 95, cy - 74, "I (заряд тече сам)", size=10, color=POS))

    # чотири «двигуни» внизу
    labels = [
        ("ХІМІЧНА", "реакція\nсортує заряд", HOT),
        ("ТЕПЛОВА", "різниця\nтемператур", COLD),
        ("СВІТЛОВА", "фотон\nштовхає заряд", SUN),
        ("ІНДУКЦІЙНА", "зміна\nмагн. потоку", COIL),
    ]
    bx0, bw, gap = 40, 160, 10
    by = 300
    for i, (t1, t2, col) in enumerate(labels):
        x = bx0 + i * (bw + gap)
        f.append(rect(x, by, bw, 90, fill="#fafbfc", stroke=col, sw=2))
        f.append(text(x + bw / 2, by + 24, t1, size=13, bold=True, color=col))
        f.append(mtext(x + bw / 2, by + 46, t2, size=11, color=INK))
        # стрілочка від двигуна вгору до «сторонньої сили»
        f.append(line(x + bw / 2, by, x + bw / 2, by - 12, color=col, sw=1.5, dash="3,3"))

    f += cap(W, "Усі чотири дають той самий вольт = джоуль на кулон сторонньої роботи.", 415)
    render(os.path.join(IMG, "four-emf.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. Ефект Зеебека
# ════════════════════════════════════════════════════════════════════════════
def fig_seebeck():
    W, H = 700, 360
    f = [text(W / 2, 26, "Ефект Зеебека: різниця температур у петлі з двох металів", size=15, bold=True)]

    # петля: два метали між гарячим (зліва) і холодним (справа) спаями
    xh, xc = 180, 520     # x гарячого і холодного спаїв
    yt, yb = 110, 230     # верхня й нижня гілки
    # верхня гілка — метал A
    f.append(line(xh, yt, xc, yt, color=HOT, sw=5))
    f.append(text((xh + xc) / 2, yt - 12, "метал A", size=12, bold=True, color=HOT))
    # нижня гілка — метал B
    f.append(line(xh, yb, xc, yb, color=COLD, sw=5))
    f.append(text((xh + xc) / 2, yb + 22, "метал B", size=12, bold=True, color=COLD))
    # спаї (вертикальні перемички)
    f.append(line(xh, yt, xh, yb, color=INK, sw=3))
    f.append(line(xc, yt, xc, yb, color=INK, sw=3))

    # гарячий спай
    f.append(circle(xh, (yt + yb) / 2, 16, fill="#fdecea", stroke=HOT, sw=2.5))
    f.append(text(xh, (yt + yb) / 2 + 5, "🔥", size=15))
    f.append(tb(xh, 300, "ГАРЯЧИЙ спай\nT_h", size=11, fill="#fdecea", stroke=HOT, color=HOT, bold=True))
    # холодний спай
    f.append(circle(xc, (yt + yb) / 2, 16, fill="#eaf0fd", stroke=COLD, sw=2.5))
    f.append(text(xc, (yt + yb) / 2 + 5, "❄", size=14, color=COLD))
    f.append(tb(xc, 300, "ХОЛОДНИЙ спай\nT_c", size=11, fill="#eaf0fd", stroke=COLD, color=COLD, bold=True))

    # дифузія носіїв з гарячого в холодний (стрілка вздовж верхньої гілки)
    f.append(arrow(xh + 40, yt, xc - 40, yt, color=INK, sw=1.8))
    f.append(text((xh + xc) / 2, yt + 18, "носії дифундують у холодний бік", size=10.5, color=MUTED))

    # формула
    f.append(tb(W / 2, 150, "ℰ ≈ S · ΔT", size=15, bold=True, min_w=140))

    f += cap(W, ["Нагрітий спай розганяє носії — вони зганяються в холодний край, виникає термоЕРС ∝ різниці температур.",
                 "У двох однакових металів внески гілок гасяться (ℰ = 0); потрібні саме різні."], 332)
    render(os.path.join(IMG, "seebeck.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. Фотовольтаїчна ЕРС
# ════════════════════════════════════════════════════════════════════════════
def fig_pv():
    W, H = 700, 360
    f = [text(W / 2, 26, "Фотовольтаїчна ЕРС: фотон народжує пару, поле переходу її розтягує", size=14.5, bold=True)]

    # дві半області p та n
    midx = W / 2
    top, bot = 70, 250
    f.append(rect(120, top, midx - 120, bot - top, fill="#fdf3e3", stroke=INK, sw=1.5))
    f.append(rect(midx, top, 580 - midx, bot - top, fill="#e8f0fb", stroke=INK, sw=1.5))
    f.append(text((120 + midx) / 2, top + 22, "p-область", size=12, bold=True, color="#b9770e"))
    f.append(text((midx + 580) / 2, top + 22, "n-область", size=12, bold=True, color=COLD))
    # межа переходу + вбудоване поле (стрілки p→n)
    f.append(line(midx, top, midx, bot, color=FIELD, sw=3))
    f.append(text(midx, bot + 18, "p-n перехід (вбудоване поле)", size=11, color=FIELD, bold=True))

    # фотон зверху
    f.append(arrow(220, 45, 300, top + 70, color=SUN, sw=2.4))
    f.append(text(205, 48, "фотон", size=11.5, color=SUN, bold=True))

    # народжена пара поблизу переходу
    ex, dx = midx - 18, midx + 18
    py = top + 90
    # електрон їде в n, дірка в p (поле розтягує)
    f.append(arrow(midx - 4, py, dx + 26, py, color=COLD, sw=2))     # електрон → n
    f.append(minus(dx + 36, py, r=10))
    f.append(arrow(midx + 4, py + 36, ex - 26, py + 36, color=POS, sw=2))  # дірка → p
    f.append(plus(ex - 36, py + 36, r=10))
    f.append(text(midx, py - 14, "пара народжується", size=10, color=MUTED))

    # зовнішнє коло з навантаженням і напругою
    f.append(line(180, bot, 180, 300, color=INK, sw=2))
    f.append(line(520, bot, 520, 300, color=INK, sw=2))
    f.append(line(180, 300, 300, 300, color=INK, sw=2))
    f.append(line(400, 300, 520, 300, color=INK, sw=2))
    f.append(rect(300, 282, 100, 36, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(350, 305, "навантаження", size=11))

    f += cap(W, ["Що яскравіше світло — то більше пар за секунду — то більший струм; напруга елемента майже стала (≈0.5 В у Si)."], 340)
    render(os.path.join(IMG, "photovoltaic.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. Електромагнітна індукція
# ════════════════════════════════════════════════════════════════════════════
def fig_induction():
    W, H = 700, 360
    f = [text(W / 2, 26, "Електромагнітна індукція: зміна потоку крізь виток дає ЕРС", size=15, bold=True)]

    # котушка (кілька витків) праворуч
    coil_x = 430
    cy = 165
    for i in range(5):
        yy = cy - 60 + i * 30
        f.append(circle(coil_x, yy, 14, fill="none", stroke=COIL, sw=3))
    f.append(text(coil_x, cy + 95, "котушка (N витків)", size=12, bold=True, color=COIL))
    # виводи котушки до вольтметра
    f.append(line(coil_x + 14, cy - 60, coil_x + 110, cy - 60, color=INK, sw=2))
    f.append(line(coil_x + 14, cy + 60, coil_x + 110, cy + 60, color=INK, sw=2))
    f.append(line(coil_x + 110, cy - 60, coil_x + 110, cy + 60, color=INK, sw=2))
    f.append(circle(coil_x + 110, cy, 20, fill=FILL, stroke=INK, sw=2))
    f.append(text(coil_x + 110, cy + 6, "ℰ", size=16, bold=True))

    # магніт, що рухається до котушки (зліва)
    mx, my = 200, cy
    f.append(rect(mx - 50, my - 22, 50, 44, fill="#fdecea", stroke=HOT, sw=2))
    f.append(text(mx - 25, my + 6, "N", size=16, bold=True, color=HOT))
    f.append(rect(mx, my - 22, 50, 44, fill="#eaf0fd", stroke=COLD, sw=2))
    f.append(text(mx + 25, my + 6, "S", size=16, bold=True, color=COLD))
    # рух магніта → котушки
    f.append(arrow(mx + 60, my, mx + 150, my, color=INK, sw=2.4))
    f.append(text(mx + 105, my - 12, "рух", size=11, bold=True))

    # лінії потоку (пунктир) від магніта в котушку
    for dyl in (-30, 0, 30):
        f.append(line(mx + 55, my + dyl, coil_x - 18, cy + dyl, color=FIELD, sw=1.3, dash="4,4"))
    f.append(text((mx + coil_x) / 2 + 10, cy + 52, "магнітний потік Φ", size=10.5, color=FIELD))

    # формула
    f.append(tb(W / 2, 305, "ℰ = − N · ΔΦ / Δt", size=15, bold=True, min_w=200))

    f += cap(W, ["Доки магніт рухається — потік крізь витки змінюється, наводиться ЕРС (тим більша, чим швидша зміна й більше витків).",
                 "Нерухомий магніт потоку не міняє — ЕРС нема. Знак Ленца: наведений струм протидіє зміні."], 332)
    render(os.path.join(IMG, "induction.svg"), W, H, *f)


if __name__ == "__main__":
    fig_four()
    fig_seebeck()
    fig_pv()
    fig_induction()
    print("OK: 4 фігури у", IMG)
