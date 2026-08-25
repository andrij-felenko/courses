# -*- coding: utf-8 -*-
"""Фігури до статті «Аналоговий обчислювач» (book/electronics/analog/analog-computer).
Чотири фігури:
  idea.svg       — головна ідея: величина ↔ напруга; машина = з'єднані блоки, що повторюють рівняння
  blocks.svg     — три «дієслова» машини: масштаб ×k, сума Σ, інтеграл ∫ (що блок робить із напругою)
  springmass.svg — приклад: рівняння пружинного маятника згорнуте в петлю інтеграторів
  parallel.svg   — чому аналог: усі блоки рахують одночасно й безперервно; де ламається (шум/точність)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ─────────────────────────────────────────────────────────
def opblock(cx, cy, w, h, sym, sub=None, accent=INK):
    """Прямокутний блок-операція з великим символом усередині."""
    out = [rect(cx - w / 2, cy - h / 2, w, h, fill="#f4f6f8", stroke=accent, sw=2, rx=8)]
    if sub:
        out.append(text(cx, cy - 4, sym, size=24, color=accent, bold=True))
        out.append(text(cx, cy + 18, sub, size=11, color=MUTED))
    else:
        out.append(text(cx, cy + 8, sym, size=24, color=accent, bold=True))
    return "".join(out), {"in": (cx - w / 2, cy), "out": (cx + w / 2, cy),
                          "top": (cx, cy - h / 2), "bot": (cx, cy + h / 2)}


def wire(x1, y1, x2, y2, color=INK, sw=2.0, head=True):
    if head:
        return arrow(x1, y1, x2, y2, color=color, sw=sw)
    return line(x1, y1, x2, y2, color=color, sw=sw)


# ════════════════════════════════════════════════════════════════════════════
# 1. idea.svg — величина ↔ напруга; машина повторює рівняння з'єднаннями
# ════════════════════════════════════════════════════════════════════════════
def fig_idea():
    W, H = 680, 320
    f = []

    # ліворуч: фізична величина у часі (хвиля)
    lx, ly = 70, 150
    f.append(text(150, 50, "РЕАЛЬНА ВЕЛИЧИНА", size=13, bold=True))
    f.append(text(150, 68, "напр. швидкість, температура, кут", size=10, color=MUTED))
    # осі
    f.append(line(lx, ly + 60, lx + 200, ly + 60, color=INK, sw=1.6))
    f.append(line(lx, ly - 50, lx, ly + 60, color=INK, sw=1.6))
    f.append(text(lx - 6, ly - 44, "x(t)", size=12, color=INK, bold=True, anchor="end"))
    # крива x(t)
    pts = []
    import math
    for i in range(0, 201, 4):
        t = i / 200.0
        yy = ly + 5 - 45 * math.sin(2.4 * t) * math.exp(-0.4 * t)
        pts.append("%.1f %.1f" % (lx + i, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), FIELD))
    f.append(text(lx + 130, ly + 80, "час →", size=10, color=MUTED))

    # стрілка-відповідність
    f.append(arrow(290, ly, 350, ly, color=POS, sw=2.6))
    f.append(text(320, ly - 12, "1 величина", size=10, color=POS, anchor="middle"))
    f.append(text(320, ly + 22, "= 1 напруга", size=11, color=POS, bold=True, anchor="middle"))

    # праворуч: вузол схеми з тією самою формою напруги
    rx = 520
    f.append(text(rx, 50, "НАПРУГА У ВУЗЛІ", size=13, bold=True))
    f.append(text(rx, 68, "та сама форма, у вольтах", size=10, color=MUTED))
    f.append(line(rx - 80, ly + 60, rx + 80, ly + 60, color=INK, sw=1.6))
    f.append(line(rx - 80, ly - 50, rx - 80, ly + 60, color=INK, sw=1.6))
    f.append(text(rx - 86, ly - 44, "u(t), В", size=11, color=INK, bold=True, anchor="end"))
    pts2 = []
    for i in range(0, 161, 4):
        t = i / 160.0
        yy = ly + 5 - 45 * math.sin(2.4 * t) * math.exp(-0.4 * t)
        pts2.append("%.1f %.1f" % (rx - 80 + i, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts2), NEG))

    # підпис-суть
    body, w0, h0 = textbox(W / 2, 296,
                           "Аналоговий обчислювач не рахує цифрами — він тримає величину живою напругою,\n"
                           "а з'єднання блоків змушують ці напруги підкорятися потрібному рівнянню",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "idea.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. blocks.svg — три операції: масштаб, сума, інтеграл
# ════════════════════════════════════════════════════════════════════════════
def fig_blocks():
    W, H = 700, 360
    f = []
    f.append(text(W / 2, 36, "Три дієслова машини над напругами", size=16, bold=True))

    by = 150
    bw, bh = 96, 78

    # 1) масштаб ×k
    s1, n1 = opblock(170, by, bw, bh, "× k", sub="масштаб", accent=POS)
    f.append(s1)
    f.append(arrow(80, by, n1["in"][0], by, color=INK, sw=2.0))
    f.append(text(95, by - 12, "u", size=13, color=INK, bold=True, anchor="middle"))
    f.append(arrow(n1["out"][0], by, 270, by, color=INK, sw=2.0))
    f.append(text(255, by - 12, "k·u", size=13, color=POS, bold=True, anchor="middle"))
    f.append(text(170, by + bh / 2 + 26, "підсилення / послаблення", size=10, color=MUTED))
    f.append(text(170, by + bh / 2 + 42, "задає відношення резисторів", size=10, color=MUTED))

    # 2) сума Σ
    s2, n2 = opblock(400, by, bw, bh, "Σ", sub="сума", accent=NEG)
    f.append(s2)
    f.append(arrow(310, by - 18, n2["in"][0], by - 18, color=INK, sw=2.0))
    f.append(arrow(310, by + 18, n2["in"][0], by + 18, color=INK, sw=2.0))
    f.append(text(325, by - 28, "a", size=12, color=INK, bold=True, anchor="middle"))
    f.append(text(325, by + 34, "b", size=12, color=INK, bold=True, anchor="middle"))
    f.append(arrow(n2["out"][0], by, 500, by, color=NEG, sw=2.0))
    f.append(text(485, by - 12, "a+b", size=12, color=NEG, bold=True, anchor="middle"))
    f.append(text(400, by + bh / 2 + 26, "складає кілька напруг", size=10, color=MUTED))
    f.append(text(400, by + bh / 2 + 42, "в одному вузлі (КЗС)", size=10, color=MUTED))

    # 3) інтеграл ∫
    s3, n3 = opblock(620, by, bw, bh, "∫ dt", sub="інтеграл", accent=FIELD)
    f.append(s3)
    f.append(arrow(530, by, n3["in"][0], by, color=INK, sw=2.0))
    f.append(text(545, by - 12, "u", size=13, color=INK, bold=True, anchor="middle"))
    f.append(arrow(n3["out"][0], by, 690, by, color=FIELD, sw=2.0))
    # хвилька-результат поряд
    f.append(text(620, by + bh / 2 + 26, "накопичує в часі", size=10, color=MUTED))
    f.append(text(620, by + bh / 2 + 42, "серце машини — на C", size=10, color=MUTED))

    # нижній підпис
    body, w0, h0 = textbox(W / 2, 330,
                           "Маючи лише ці три блоки, можна зібрати будь-яке лінійне диференційне рівняння:\n"
                           "масштаб дає коефіцієнти, сума — складання доданків, інтеграл — перехід між похідними",
                           size=11, color=INK, fill="#f4f6f8", stroke=LINE)
    f.append(body)
    render(os.path.join(IMG, "blocks.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. springmass.svg — рівняння маятника згорнуте в петлю інтеграторів
# ════════════════════════════════════════════════════════════════════════════
def fig_springmass():
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 34, "Як рівняння стає схемою: маятник на пружині", size=16, bold=True))
    f.append(text(W / 2, 56, "a = −(k/m)·x   →   двічі проінтегрувати прискорення, повернути результат назад",
                  size=11, color=MUTED))

    by = 175
    bw, bh = 92, 70
    # ланцюг: [a] → ∫ → [v] → ∫ → [x]
    s1, i1 = opblock(190, by, bw, bh, "∫ dt", sub="інтеграл", accent=FIELD)
    s2, i2 = opblock(420, by, bw, bh, "∫ dt", sub="інтеграл", accent=FIELD)
    f.append(s1); f.append(s2)

    # вхід a зліва
    f.append(arrow(80, by, i1["in"][0], by, color=POS, sw=2.2))
    f.append(text(96, by - 12, "a", size=14, color=POS, bold=True, anchor="middle"))
    f.append(text(96, by + 18, "прискорення", size=9, color=MUTED, anchor="middle"))
    # a → v
    f.append(arrow(i1["out"][0], by, i2["in"][0], by, color=INK, sw=2.2))
    f.append(text((i1["out"][0] + i2["in"][0]) / 2, by - 12, "v", size=14, color=INK, bold=True, anchor="middle"))
    f.append(text((i1["out"][0] + i2["in"][0]) / 2, by + 18, "швидкість", size=9, color=MUTED, anchor="middle"))
    # v → x
    f.append(arrow(i2["out"][0], by, 610, by, color=NEG, sw=2.2))
    f.append(text(600, by - 12, "x", size=14, color=NEG, bold=True, anchor="middle"))
    f.append(text(600, by + 18, "положення", size=9, color=MUTED, anchor="middle"))
    f.append(circle(610, by, 3, fill=NEG, stroke=NEG))

    # зворотний блок ×(−k/m): з x назад у вхід a
    fbw, fbh = 132, 56
    fby = by + 120
    sb, fb = opblock(350, fby, fbw, fbh, "× (−k/m)", accent=POS)
    f.append(sb)
    # від вузла x вниз, тоді вліво у правий бік блоку ЗЗ
    f.append(line(610, by, 610, fby, color=NEG, sw=2.0))
    f.append(arrow(610, fby, fb["out"][0], fby, color=NEG, sw=2.0))
    # вихід блоку ЗЗ (його лівий бік) піднімається назад у вхід a
    f.append(line(fb["in"][0], fby, 80, fby, color=POS, sw=2.0))
    f.append(arrow(80, fby, 80, by + 8, color=POS, sw=2.2))
    f.append(text(350, fby - fbh / 2 - 12, "поворот сигналу назад", size=10, color=POS, anchor="middle"))

    # підпис-суть
    body, w0, h0 = textbox(W / 2, 350,
                           "Петля сама себе тримає: x задає прискорення, прискорення інтегрується у швидкість,\n"
                           "та — у положення, і воно знову керує прискоренням. Машина «коливається» так само, як маятник.",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "springmass.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. parallel.svg — усе одночасно й безперервно; межа — шум/точність
# ════════════════════════════════════════════════════════════════════════════
def fig_parallel():
    W, H = 700, 340
    f = []

    # ліва панель — аналог: усі блоки світяться разом, лінія часу суцільна
    f.append(text(180, 44, "АНАЛОГ", size=15, bold=True, color=FIELD))
    f.append(text(180, 62, "усі блоки рахують одночасно", size=10, color=MUTED))
    # три блоки, всі активні
    for i, cx in enumerate((90, 180, 270)):
        f.append(rect(cx - 26, 90, 52, 40, fill="#eef7f0", stroke=FIELD, sw=2, rx=6))
        f.append(text(cx, 115, ("×k", "Σ", "∫")[i], size=15, color=FIELD, bold=True))
    f.append(line(90, 130, 90, 160, color=FIELD, sw=1.6))
    f.append(line(180, 130, 180, 160, color=FIELD, sw=1.6))
    f.append(line(270, 130, 270, 160, color=FIELD, sw=1.6))
    f.append(line(90, 160, 270, 160, color=FIELD, sw=1.6))
    f.append(text(180, 178, "одна спільна мить часу", size=10, color=FIELD, bold=True))
    # суцільна крива часу
    import math
    pts = []
    for i in range(0, 241, 4):
        t = i / 240.0
        yy = 230 - 28 * math.sin(3.5 * t)
        pts.append("%.1f %.1f" % (60 + i, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), FIELD))
    f.append(text(180, 270, "час тече безперервно", size=10, color=MUTED))

    # роздільник
    f.append(line(W / 2, 80, W / 2, 280, color="#dfe3e8", sw=1.5, dash="5 5"))

    # права панель — цифра: крок за кроком, по точках
    f.append(text(520, 44, "ЦИФРА (для контрасту)", size=14, bold=True, color=NEG))
    f.append(text(520, 62, "один крок — одна дія", size=10, color=MUTED))
    # послідовні кроки
    for i, cx in enumerate((430, 520, 610)):
        col = NEG if i == 0 else "#b9c4e0"
        f.append(rect(cx - 26, 90, 52, 40, fill="#eaf0fd", stroke=col, sw=2, rx=6))
        f.append(text(cx, 115, "крок %d" % (i + 1), size=11, color=col, bold=True))
    f.append(arrow(456, 110, 484, 110, color=NEG, sw=1.8))
    f.append(arrow(546, 110, 574, 110, color="#b9c4e0", sw=1.8))
    f.append(text(520, 178, "по черзі, такт за тактом", size=10, color=NEG, bold=True))
    # дискретні точки часу
    for i in range(0, 13):
        xx = 430 + i * 16
        yy = 230 - 28 * math.sin(3.5 * (i / 12.0))
        f.append(circle(xx, yy, 2.6, fill=NEG, stroke=NEG))
    f.append(text(520, 270, "час нарізаний на кроки", size=10, color=MUTED))

    # нижній підпис: де аналог ламається
    body, w0, h0 = textbox(W / 2, 312,
                           "Аналог нескінченно швидкий і паралельний — але точність упирається в шум і дрейф (~0.01–0.1%);\n"
                           "цифра повільніша по кроках, зате повторювана до останнього біта",
                           size=11, color=INK, fill="#fdecea", stroke=POS)
    f.append(body)
    render(os.path.join(IMG, "parallel.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. torque-gap.svg — ідея 1876 vs стіна моменту сили; ланка Німана 1925 її прибрала
#    (вставка hist-differential-analyzer)
# ════════════════════════════════════════════════════════════════════════════
def fig_torque_gap():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 34, "Чому ідею не вдавалося збудувати 55 років", size=16, bold=True))
    f.append(text(W / 2, 55, "виходу інтегратора бракувало моменту сили, щоб рухати наступний",
                  size=11, color=MUTED))

    iy = 150          # рівень ланцюга
    bw, bh = 96, 66

    # інтегратор 1
    s1, n1 = opblock(150, iy, bw, bh, "∫", sub="інтегратор", accent=FIELD)
    f.append(s1)
    f.append(text(150, iy - bh / 2 - 12, "слабкий вихід", size=10, color=MUTED, anchor="middle"))

    # інтегратор 2 (праворуч)
    s2, n2 = opblock(560, iy, bw, bh, "∫", sub="інтегратор", accent=FIELD)
    f.append(s2)
    f.append(text(560, iy - bh / 2 - 12, "опір навантаження", size=10, color=MUTED, anchor="middle"))

    # «стіна» між ними
    wx = 355
    f.append(rect(wx - 14, iy - 58, 28, 116, fill="#fdecea", stroke=POS, sw=2, rx=4))
    f.append(text(wx, iy - 70, "СТІНА", size=12, color=POS, bold=True, anchor="middle"))
    f.append(text(wx, iy - 2, "момент", size=11, color=POS, bold=True, anchor="middle"))
    f.append(text(wx, iy + 16, "сили", size=11, color=POS, bold=True, anchor="middle"))
    # стрілка від 1 у стіну — гасне
    f.append(arrow(n1["out"][0], iy, wx - 16, iy, color=FIELD, sw=2.2))
    # «прослизання» — пунктир за стіною
    f.append(line(wx + 16, iy, n2["in"][0], iy, color=POS, sw=2.0, dash="4 4"))
    f.append(text((wx + n2["in"][0]) / 2 + 8, iy + 22, "кулька прослизає", size=10,
                  color=POS, anchor="middle", italic=True))

    # роздільна риса
    f.append(line(70, 235, W - 70, 235, color="#dfe3e8", sw=1.4, dash="5 5"))

    # рішення: підсилювач моменту (Німан 1925)
    f.append(text(W / 2, 262, "Ланка, якої бракувало: підсилювач моменту сили (Німан, 1925)",
                  size=13, bold=True, color=NEG))
    body, _, _ = textbox(W / 2, 318,
                         "Слабкий вхід лише ПРИТИСКАЄ стрічку до обертового барабана (як кабестан на якорі),\n"
                         "а барабан від двигуна віддає на вихід ту саму дію — але з силою. Вихід тепер може\n"
                         "рухати наступний інтегратор, сам не навантажуючись. Так ідея 1876 ожила 1931-го.",
                         size=11, color=INK, fill="#eaf0fd", stroke=NEG)
    f.append(body)
    render(os.path.join(IMG, "torque-gap.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 6. three-steps.svg — три кроки: ІДЕЯ → МЕХАНІКА → ЕЛЕКТРОНІКА (вставка)
# ════════════════════════════════════════════════════════════════════════════
def fig_three_steps():
    W, H = 740, 320
    f = []
    f.append(text(W / 2, 34, "Три кроки, які зробили різні люди", size=16, bold=True))
    f.append(text(W / 2, 55, "ідею легко сплутати з реалізацією, а реалізацію — з цеглинкою", size=11, color=MUTED))

    ly = 150
    # довга вісь часу
    f.append(line(60, ly, W - 60, ly, color=INK, sw=2.0))
    f.append(arrow(W - 70, ly, W - 56, ly, color=INK, sw=2.0))

    stages = [
        (170, "ІДЕЯ", "1876", "з'єднати інтегратори,\nщоб втілити рівняння",
         "брати Томсони", FIELD, "#eef7f0"),
        (400, "МЕХАНІКА", "1931", "диференційний аналізатор:\nвали, шестерні, 6 інтеграторів",
         "В. Буш, MIT", NEG, "#eaf0fd"),
        (620, "ЕЛЕКТРОНІКА", "1947→53", "та сама математика струмами:\n«операційний підсилювач»",
         "Раджаззіні; K2-W", POS, "#fdecea"),
    ]
    for cx, head, year, desc, who, col, fillc in stages:
        # вузол на осі
        f.append(circle(cx, ly, 7, fill=col, stroke=col))
        f.append(text(cx, ly - 22, year, size=14, color=col, bold=True, anchor="middle"))
        f.append(text(cx, ly - 40, head, size=13, color=INK, bold=True, anchor="middle"))
        # картка під віссю
        box = fitbox(cx - 100, ly + 24, 200, 64, desc, size=11, fill=fillc, stroke=col, color=INK)
        f.append(box)
        f.append(text(cx, ly + 104, who, size=10, color=MUTED, anchor="middle", italic=True))

    # «стіна 55 років» між ідеєю і механікою
    f.append(text((170 + 400) / 2, ly + 132, "↑ між ними — 55 років: бракувало моменту сили",
                  size=10, color=POS, anchor="middle", italic=True))

    render(os.path.join(IMG, "three-steps.svg"), W, H, *f)


if __name__ == "__main__":
    fig_idea()
    fig_blocks()
    fig_springmass()
    fig_parallel()
    fig_torque_gap()
    fig_three_steps()
    print("OK: 6 фігур у", IMG)
