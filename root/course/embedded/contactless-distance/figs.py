# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── d-error-map: важіль v/2 — та сама похибка часу дає різну похибку відстані ──
# Ідея: ∂d = (v/2)·∂t. Один і той самий «квант часу» ∂t перетворюється на
# крихітну похибку для звуку й величезну для світла — бо множник v/2 різний
# у мільйон разів. Дві осі: та сама ширина ∂t зліва, різна висота ∂d справа.
def fig_error_map():
    W, H = 860, 400
    p = []
    # спільний «квант часу» посередині
    tx = W / 2
    p.append(text(tx, 70, "той самий квант часу  Δt = 1 мкс", size=14, bold=True))
    # смужка Δt (однакова для обох)
    bw = 90
    p.append(rect(tx - bw / 2, 84, bw, 26, fill="#eef4ff", stroke=NEG, sw=1.8, rx=3))
    p.append(text(tx, 102, "Δt", size=13, color=NEG, bold=True))

    # важіль ×(v/2): дві стрілки вниз до різних відстаней
    def lever(cx, label, dbar_px, dval, col, fill):
        out = []
        out.append(text(cx, 150, label, size=12, color=col, bold=True))
        out.append(arrow(cx, 116, cx, 176, color=MUTED, sw=1.6))
        out.append(text(cx + 6, 150, "×v/2", size=10, color=MUTED, anchor="start"))
        # смужка похибки відстані — висота кодує величину
        base_y = 340
        out.append(rect(cx - 46, base_y - dbar_px, 92, dbar_px, fill=fill, stroke=col, sw=1.8, rx=3))
        out.append(text(cx, base_y + 18, dval, size=12, color=col, bold=True))
        return out

    p += lever(tx - 220, "звук  v ≈ 343 м/с", 20, "Δd ≈ 0.17 мм", FIELD, "#eafaf0")
    p += lever(tx + 220, "світло  v ≈ 3·10⁸ м/с", 200, "Δd ≈ 150 м", POS, "#fdecea")

    # підпис-висновок
    p.append(text(W / 2, H - 16,
                  "однаковий Δt → похибка відстані більша в ~мільйон разів; ось чому світло вимагає в тисячі разів точнішого годинника",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "d-error-map.svg"), W, H, *p,
           title="Важіль v/2: та сама похибка часу — різна похибка відстані")


# ── d-blind-zone: сліпа зона від «дзвону» спільної п'єзопластини ───────────────
# Ідея: одна пластина спершу випромінює, потім слухає. Після імпульсу вона ще
# «дзвенить» власним затуханням τ; поки дзвенить — глуха. Відлуння, що прийшло
# в цей час (від близької цілі), тоне у власному дзвоні → сліпа зона.
def fig_blind_zone():
    W, H = 860, 400
    p = []
    # часова вісь
    ax, ay = 70, 250
    aw = W - 150
    p.append(line(ax, ay, ax + aw, ay, color=INK, sw=1.6))
    p.append(text(ax + aw, ay + 18, "час", size=11, italic=True))

    # 1) короткий збуджувальний імпульс
    px0 = ax + 20
    for i in range(6):
        x = px0 + i * 6
        h = 55 if i % 2 == 0 else -55
        p.append(line(x, ay, x, ay - h, color=NEG, sw=2.0))
    p.append(text(px0 + 15, ay - 70, "збудження", size=10, color=NEG, bold=True))

    # 2) затухний «дзвін» пластини (експонента, що гасне)
    ring_x0 = px0 + 40
    ring_len = 150
    pts = []
    for i in range(ring_len):
        t = i / 12.0
        amp = 70 * math.exp(-t * 0.6) * math.cos(t * 3.2)
        pts.append("%.1f,%.1f" % (ring_x0 + i, ay - amp))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(pts), POS))
    # зона «глуха» — заливка під дзвоном
    blind_x1 = ring_x0 + 95
    p.append(rect(px0 - 4, ay - 92, blind_x1 - px0 + 4, 184, fill="#fdecea", stroke="none", rx=4))
    p.append(text((px0 + blind_x1) / 2, ay - 100, "СЛІПА ЗОНА: пластина ще дзвенить — глуха",
                  size=11, color=POS, bold=True))

    # 3) слабке справжнє відлуння, що приходить пізніше — його вже чути
    echo_x = blind_x1 + 120
    for i in range(5):
        x = echo_x + i * 5
        h = 26 if i % 2 == 0 else -26
        p.append(line(x, ay, x, ay - h, color=FIELD, sw=2.0))
    p.append(text(echo_x + 12, ay - 44, "відлуння здалеку —", size=10, color=FIELD, bold=True))
    p.append(text(echo_x + 12, ay - 30, "чути чисто", size=10, color=FIELD, bold=True))
    # відлуння від БЛИЗЬКОЇ цілі — потонуло б у дзвоні
    p.append(arrow((px0 + blind_x1) / 2, ay + 40, (px0 + blind_x1) / 2, ay + 8, color=POS, sw=1.6))
    p.append(text((px0 + blind_x1) / 2, ay + 58, "близька ціль сюди — не побачимо", size=10, color=POS))

    p.append(text(W / 2, H - 16,
                  "мінімальна дальність = поки триває власний дзвін після імпульсу; це не дефект, а плата за спільні «голос і вухо»",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "d-blind-zone.svg"), W, H, *p,
           title="Сліпа зона: власний «дзвін» пластини глушить близьке відлуння")


# ── d-beam-cone: промінь — конус; поперечна невизначеність росте з відстанню ───
# Ідея: давач каже «щось є за d», але не «де впоперек». Широкий конус на відстані
# накриває широку смугу — ціль може бути будь-де в ній. Що далі, то ширша смуга.
def fig_beam_cone():
    W, H = 860, 400
    p = []
    sx, sy = 90, H / 2
    # давач
    p.append(fitbox(sx - 44, sy - 24, 60, 48, "давач", size=11, fill="#f6f4ec",
                    stroke=INK, sw=1.6, bold=True))
    # конус променя (половинний кут)
    half = math.radians(14)
    L = 640
    x2 = sx + L
    yA = sy - math.tan(half) * L
    yB = sy + math.tan(half) * L
    p.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#eef4ff" stroke="%s" stroke-width="1.6" opacity="0.85"/>'
             % (sx + 18, sy, x2, yA, x2, yB, NEG))
    p.append(line(sx + 18, sy, x2, sy, color=NEG, sw=1.2, dash="5 4"))
    p.append(text(sx + 150, sy - 8, "вісь променя", size=10, color=NEG))
    # три відстані з дедалі ширшою поперечною смугою
    for d, lab in ((220, "близько"), (400, "далі"), (600, "далеко")):
        x = sx + 18 + d
        yh = math.tan(half) * (d)
        p.append(line(x, sy - yh, x, sy + yh, color=POS, sw=2.0))
        p.append(text(x, sy + yh + 18, lab, size=10, color=MUTED))
        p.append(text(x, sy - yh - 8, "±%d" % int(yh / 6), size=9, color=POS))
    # ціль десь у смузі
    p.append(circle(x2 - 40, yA + 26, 9, fill="#fff", stroke=POS, sw=2))
    p.append(text(x2 - 40, yA + 6, "ціль?", size=10, color=POS, bold=True))
    p.append(text(x2 - 40, yB - 10, "чи тут?", size=10, color=POS))

    p.append(text(W / 2, H - 16,
                  "давач знає дальність, але не напрямок усередині конуса; поперечна невизначеність росте лінійно з відстанню",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "d-beam-cone.svg"), W, H, *p,
           title="Промінь — конус: далеко він накриває широку смугу")


# ── d-phase-ambiguity: неоднозначність фази — d і d+λ/2 дають той самий зсув ────
# Ідея: у неперервнохвильовому методі міряють фазовий зсув відлуння. Але фаза
# циклічна: пройшовши ще пів-довжини модуляції, вона повертається до того ж
# значення. Тож давач не відрізнить справжню відстань від «на оберт далі».
def fig_phase_ambiguity():
    W, H = 860, 440
    p = []
    ax, ay = 70, 150
    aw = W - 150
    amp = 52
    # передана хвиля (опорна)
    pts = []
    for i in range(int(aw)):
        x = ax + i
        y = ay - amp * math.sin(i / 38.0)
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(pts), NEG))
    p.append(text(ax, ay - amp - 14, "передана модуляція (опора)", size=10, color=NEG, anchor="start"))

    # відлуння: зсув на φ
    ey = ay + 150
    shift = 60
    pts = []
    for i in range(int(aw)):
        x = ax + i
        y = ey - amp * math.sin((i - shift) / 38.0)
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(pts), FIELD))
    p.append(text(ax, ey - amp - 12, "відлуння: зсув φ  → відстань d", size=10, color=FIELD, anchor="start"))

    # висновок про ідентичність — у проміжку між хвилями
    p.append(text(W / 2, ay + 78,
                  "зсув φ і φ+2π дають ІДЕНТИЧНЕ відлуння:",
                  size=11, color=POS, bold=True))
    p.append(text(W / 2, ay + 94,
                  "давач не відрізнить d від d + c/(2·f_mod)",
                  size=11, color=POS, bold=True))

    # вертикальні пунктири — один період неоднозначності
    period_px = 38.0 * 2 * math.pi
    x0 = ax + 60
    x1 = x0 + period_px
    marky = ey + amp + 20
    for xx in (x0, x1):
        p.append(line(xx, ey + amp + 6, xx, marky + 6, color=MUTED, sw=1.0, dash="4 4"))
    p.append(arrow(x0, marky, x1, marky, color=POS, sw=1.4))
    p.append(text((x0 + x1) / 2, marky + 16, "один оберт фази = крок неоднозначності", size=10, color=POS))

    p.append(text(W / 2, H - 14,
                  "нижча частота модуляції → більший однозначний діапазон, але грубша роздільність (компроміс)",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "d-phase-ambiguity.svg"), W, H, *p,
           title="Неоднозначність фази: та сама фаза для d і d+пів-довжини модуляції")


# ── d-triangulation-resolution: рівні кроки Δx → нерівні Δd (колапс удалині) ────
# Ідея: d ≈ b·f/x. Функція обернена, тож рівні кроки положення плями Δx дають
# ДЕДАЛІ БІЛЬШІ кроки відстані Δd. Зблизька крок дрібний (добра роздільність),
# удалині — величезний (роздільність валиться як d²).
def fig_tri_resolution():
    W, H = 860, 420
    p = []
    # осі: X = зсув плями x (спадає), Y = відстань d
    ax, ay = 90, 340
    aw, ah = W - 200, 250
    p.append(line(ax, ay, ax + aw, ay, color=INK, sw=1.6))
    p.append(line(ax, ay, ax, ay - ah, color=INK, sw=1.6))
    p.append(text(ax + aw, ay + 18, "зсув плями x на приймачі →", size=10, italic=True))
    p.append(text(ax - 6, ay - ah + 2, "відстань d", size=10, anchor="end", italic=True))

    # крива d = k/x
    k = 9000.0
    xs = [i for i in range(28, int(aw))]
    pts = []
    for xi in xs:
        d = k / xi
        y = ay - min(d, ah - 6)
        pts.append("%.1f,%.1f" % (ax + xi, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), NEG))

    # рівні кроки Δx уздовж осі x → показати різні Δd на осі d
    step_pixels = [40, 40, 40, 40, 40]
    cur = 40.0
    prev_d = None
    for i, s in enumerate(step_pixels):
        x_screen = ax + cur
        d = k / cur
        yv = ay - min(d, ah - 6)
        # вертикаль до кривої
        p.append(line(x_screen, ay, x_screen, yv, color=MUTED, sw=1.0, dash="3 3"))
        # горизонталь до осі d
        p.append(line(ax, yv, x_screen, yv, color=MUTED, sw=1.0, dash="3 3"))
        p.append(circle(x_screen, yv, 4, fill=POS, stroke=POS, sw=1))
        if prev_d is not None:
            # позначка величини Δd між сусідніми точками
            ymid = (yv + prev_y) / 2
            p.append(text(ax - 10, ymid, "Δd", size=9, color=POS, anchor="end"))
        prev_y = yv
        prev_d = d
        cur += s
    # позначки «рівні Δx» унизу
    for i in range(len(step_pixels) + 1):
        xx = ax + 40 + i * 40
        p.append(line(xx, ay - 4, xx, ay + 4, color=INK, sw=1.4))
    p.append(text(ax + 40 + 2 * 40, ay + 32, "рівні кроки Δx", size=10, color=INK))
    p.append(arrow(ax + 40, ay + 22, ax + 40 + 40, ay + 22, color=MUTED, sw=1.2))

    # анотації двох країв
    p.append(text(ax + 70, ay - ah + 40, "зблизька: малий Δd", size=10, color=FIELD, bold=True))
    p.append(text(ax + aw - 150, ay - 30, "далеко: Δd вибухає (~d²)", size=10, color=POS, bold=True))

    p.append(text(W / 2, H - 14,
                  "обернена крива d≈b·f/x: рівні кроки положення плями → дедалі більші кроки відстані; роздільність тріангуляції падає як d²",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "d-triangulation-resolution.svg"), W, H, *p,
           title="Тріангуляція: чому роздільність валиться з відстанню")


# ── m-quadrature: чому незалежні похибки додаються «у квадратурі» ──────────────
# Ідея: дві незалежні відносні похибки — Δv/v і Δt/t — це два ПЕРПЕНДИКУЛЯРНІ
# катети (незалежність = прямий кут). Сумарна похибка — ГІПОТЕНУЗА, а не сума
# катетів. Тому менший внесок майже не додає до більшого (квадрат тисне малих).
def fig_quadrature():
    W, H = 860, 440
    p = []
    # початок координат унизу ліворуч
    ox, oy = 150, 360
    scale = 1.0
    a = 240.0   # катет Δv/v (більший, домінантний)
    b = 130.0   # катет Δt/t (менший)
    # осі
    p.append(arrow(ox, oy, ox + a + 80, oy, color=MUTED, sw=1.4))
    p.append(arrow(ox, oy, ox, oy - b - 110, color=MUTED, sw=1.4))
    # катет Δv/v (горизонталь)
    p.append(line(ox, oy, ox + a, oy, color=NEG, sw=3.0))
    p.append(text(ox + a / 2, oy + 22, "Δv/v  (швидкість)", size=12, color=NEG, bold=True))
    # катет Δt/t (вертикаль, від кінця першого)
    p.append(line(ox + a, oy, ox + a, oy - b, color=FIELD, sw=3.0))
    p.append(text(ox + a + 12, oy - b / 2, "Δt/t", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(text(ox + a + 12, oy - b / 2 + 15, "(час)", size=10, color=FIELD, anchor="start"))
    # прямий кут — незалежність
    qs = 16
    p.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.2"/>'
             % (ox + a - qs, oy, ox + a - qs, oy - qs, ox + a, oy - qs, MUTED))
    p.append(text(ox + a - qs - 6, oy - qs - 6, "⊥ незалежні", size=10, color=MUTED, anchor="end"))
    # гіпотенуза — сумарна відносна похибка
    hx, hy = ox + a, oy - b
    p.append(line(ox, oy, hx, hy, color=POS, sw=3.2))
    mx, my = (ox + hx) / 2, (oy + hy) / 2
    p.append(text(mx - 8, my - 12, "Δd/d = √((Δv/v)² + (Δt/t)²)", size=12, color=POS, bold=True, anchor="end"))
    # точка-вершина
    p.append(circle(hx, hy, 4, fill=POS, stroke=POS, sw=1))

    # висновок: квадрат тисне малий доданок
    p.append(fitbox(ox + a + 120, oy - 150, 240, 96,
                    "квадрат ТИСНЕ малий доданок:\nякщо Δt/t удвічі менша за Δv/v,\nвона додає лише ~12 %,\nа не 50 %. Головний доданок\nмайже й визначає підсумок.",
                    size=11, fill="#f6f4ec", stroke=INK, sw=1.4))

    p.append(text(W / 2, H - 14,
                  "незалежні джерела = перпендикулярні катети; сумарна похибка — гіпотенуза, тому доданки додаються квадратами, а не прямо",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "m-quadrature.svg"), W, H, *p,
           title="Квадратура: чому Δd/d = Δv/v ⊕ Δt/t, а не Δv/v + Δt/t")


# ── m-systematic-vs-random: усереднення б'є розкид, але безсиле проти зсуву ─────
# Ідея: N вимірів. Випадкова похибка (шум таймера) дає розкид, що спадає як 1/√N
# — хмара стягується до центру. Систематична (невірна v) — сталий ЗСУВ від
# правди, який усередненням НЕ прибрати: хмара стягується, але коло НЕ ту точку.
def fig_sys_vs_rand():
    W, H = 860, 430
    p = []
    import random
    random.seed(7)

    def bullseye(cx, cy, r, label):
        out = [circle(cx, cy, r, fill="#f7f9fc", stroke=MUTED, sw=1.2),
               circle(cx, cy, r * 0.6, fill="#eef4ff", stroke=MUTED, sw=1.0),
               circle(cx, cy, 3, fill=FIELD, stroke=FIELD, sw=1)]
        out.append(text(cx, cy + r + 20, label, size=11, bold=True))
        out.append(text(cx, cy - r - 10, "× правда", size=9, color=FIELD))
        return out

    r = 92
    # ЛІВОРУЧ: лише випадкова — центрована навколо правди, широкий розкид
    lx, ly = 210, 200
    p += bullseye(lx, ly, r, "тільки випадкова (шум)")
    for _ in range(22):
        dx = random.gauss(0, r * 0.42)
        dy = random.gauss(0, r * 0.42)
        p.append(circle(lx + dx, ly + dy, 3.4, fill=POS, stroke="none", sw=0))
    p.append(text(lx, ly + r + 38, "розкид навколо правди → усереднення стягує його як 1/√N",
                  size=10, color=MUTED))

    # ПРАВОРУЧ: систематична + випадкова — зсунуто вбік, розкид навколо НЕ тієї точки
    rx, ry = 640, 200
    p += bullseye(rx, ry, r, "систематична + випадкова")
    bias_x = r * 0.66   # сталий зсув
    p.append(arrow(rx, ry, rx + bias_x, ry, color=NEG, sw=1.6))
    p.append(text(rx + bias_x / 2, ry - 8, "зсув", size=10, color=NEG, bold=True))
    for _ in range(22):
        dx = random.gauss(0, r * 0.22)   # менший розкид — уявімо, вже усереднили
        dy = random.gauss(0, r * 0.22)
        p.append(circle(rx + bias_x + dx, ry + dy, 3.4, fill=POS, stroke="none", sw=0))
    p.append(text(rx, ry + r + 38, "усереднення стягує хмару, але коло ЗСУНУТУ точку — брехня лишається",
                  size=10, color=MUTED))

    p.append(text(W / 2, H - 14,
                  "1/√N убиває випадковий розкид, та безсиле проти систематичного зсуву; тисяча однаково брехливих вимірів дають ту саму брехню",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "m-systematic-vs-random.svg"), W, H, *p,
           title="Усереднення: б'є розкид, безсиле проти зсуву")


if __name__ == "__main__":
    fig_error_map()
    fig_blind_zone()
    fig_beam_cone()
    fig_phase_ambiguity()
    fig_tri_resolution()
    fig_quadrature()
    fig_sys_vs_rand()
    print("OK: figures written to", OUT)
