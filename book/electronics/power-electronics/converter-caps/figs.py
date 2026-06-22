# -*- coding: utf-8 -*-
"""Фігури теми «Конденсатори перетворювача» та її вставки math-ripple-esr.
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5). Вивід — у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_roles():
    """Дві панелі поруч: вхідний кондер віддає імпульси струму (джерело бачить
    гладке), вихідний згладжує трикутник струму в дрібну пульсацію напруги."""
    W, H = 880, 400
    frags = []
    # ── ліва панель: ВХІДНИЙ ──
    Lx, Lw = 40, 380
    frags.append(rect(Lx, 60, Lw, 300, fill="#fdecea", stroke=POS, sw=1.8, rx=12))
    frags.append(text(Lx + Lw / 2, 88, "Вхідний: віддає ривки струму", size=14, color=POS, bold=True))
    # імпульсний струм входу (меандр)
    bx, by, bw = Lx + 36, 150, 308
    frags.append(text(bx - 14, by - 24, "iвх", size=12, color=INK, anchor="end", bold=True))
    frags.append(line(bx, by, bx + bw, by, color=MUTED, sw=1.2))           # вісь часу
    step = bw / 6.0
    for k in range(3):                                                      # три імпульси
        x0 = bx + 2 * k * step
        frags.append(line(x0, by, x0, by - 34, color=POS, sw=2.4))
        frags.append(line(x0, by - 34, x0 + step, by - 34, color=POS, sw=2.4))
        frags.append(line(x0 + step, by - 34, x0 + step, by, color=POS, sw=2.4))
        frags.append(line(x0 + step, by, x0 + 2 * step, by, color=POS, sw=2.4))
    frags.append(text(Lx + Lw / 2, 210, "перетворювач смикає вхід імпульсами;", size=11, color=INK))
    frags.append(text(Lx + Lw / 2, 226, "кондер віддає їх локально, і джерело", size=11, color=INK))
    frags.append(text(Lx + Lw / 2, 242, "бачить гладкий середній струм", size=11, color=INK))
    box, _, _ = textbox(Lx + Lw / 2, 286, "несе великий RMS-струм — найважчий режим",
                        size=12, color=POS, bold=True, fill="#fbe0dc", stroke=POS)
    frags.append(box)

    # ── права панель: ВИХІДНИЙ ──
    Rx, Rw = 460, 380
    frags.append(rect(Rx, 60, Rw, 300, fill="#eaf7ee", stroke=FIELD, sw=1.8, rx=12))
    frags.append(text(Rx + Rw / 2, 88, "Вихідний: згладжує напругу", size=14, color=FIELD, bold=True))
    # дрібна пульсація напруги (синусоїдоподібна хвилька)
    ax, ay, aw = Rx + 36, 150, 308
    frags.append(text(ax - 14, ay - 24, "Vвих", size=12, color=INK, anchor="end", bold=True))
    frags.append(line(ax, ay, ax + aw, ay, color=MUTED, sw=1.2, dash="5,4"))
    pts = []
    for i in range(0, int(aw) + 1, 4):
        y = ay - 16 * math.sin(2 * math.pi * (i / (aw / 3.0)))
        pts.append("%.1f,%.1f" % (ax + i, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (" ".join(pts), FIELD))
    frags.append(text(Rx + Rw / 2, 210, "приймає змінну частину струму котушки", size=11, color=INK))
    frags.append(text(Rx + Rw / 2, 226, "й перетворює трикутник струму на", size=11, color=INK))
    frags.append(text(Rx + Rw / 2, 242, "дрібну пульсацію напруги", size=11, color=INK))
    box, _, _ = textbox(Rx + Rw / 2, 286, "тримає вихід у перші миті стрибка навантаження",
                        size=12, color=FIELD, bold=True, fill="#dcf0e2", stroke=FIELD)
    frags.append(box)

    render(os.path.join(OUT, "roles.svg"), W, H, *frags,
           title="Два конденсатори, дві різні роботи: струм проти напруги")


def fig_input_pulses():
    """Чому вхідний у найважчому режимі: джерело дає лише середнє D·I, а гострі
    ривки (повний струм − середнє) бере на себе вхідний кондер → RMS·ESR гріє."""
    W, H = 820, 470
    L, R = 90, 720
    T, B = 70, 300
    frags = []
    frags.append(line(L, T, L, B, color=INK, sw=2))           # вісь струму
    frags.append(line(L, B, R, B, color=INK, sw=2))           # вісь часу
    frags.append(text(L - 16, T + 6, "I", size=13, color=INK, anchor="end", bold=True))
    frags.append(text(R, B + 22, "час", size=12, color=MUTED, anchor="end"))

    Ifull, Iavg = B - 200, B - 90        # рівні: повний струм навантаження і середнє D·I
    frags.append(line(L, Iavg, R, Iavg, color=NEG, sw=2, dash="6,4"))
    frags.append(text(R - 6, Iavg - 8, "середнє D·Iнаван — дає джерело", size=12, color=NEG, anchor="end", bold=True))

    # імпульсний струм входу: повний поки ключ відкритий, нуль поки закритий
    span = (R - L) / 3.0
    don = span * 0.4
    pts = []
    x = L
    for _ in range(3):
        pts += ["%.1f,%.1f" % (x, B), "%.1f,%.1f" % (x, Ifull),
                "%.1f,%.1f" % (x + don, Ifull), "%.1f,%.1f" % (x + don, B),
                "%.1f,%.1f" % (x + span, B)]
        x += span
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), POS))
    frags.append(text(L + don / 2, Ifull - 10, "ключ відкритий", size=11, color=POS, bold=True))

    # заштрихована «різниця», яку віддає кондер
    frags.append(text((L + R) / 2, B + 44, "повний струм біжить імпульсами; різницю до середнього віддає кондер",
                      size=12, color=INK))

    # підсумкова рамка з формулою RMS
    box, bw, bh = textbox((L + R) / 2, 380,
                          ["вхідний кондер несе RMS-струм", "Iвх(rms) = Iнаван·√(D(1−D))",
                           "максимум при D = 0.5  →  0.5·Iнаван", "і цей струм гріє його через ESR"],
                          size=13, fill="#fdecea", stroke=POS, bold=False)
    frags.append(box)

    render(os.path.join(OUT, "input-pulses.svg"), W, H, *frags,
           title="Вхідний у найважчому режимі: джерело дає середнє, кондер — ривки")


def fig_esr_ripple():
    """Дві складові вихідної пульсації: плавна ємнісна (ΔI/8fC) і гостра на ESR
    (ΔI·ESR, у фазі зі струмом). Кераміка прибирає гостру — лишається плавна."""
    W, H = 840, 470
    frags = []
    # ── ліво: електроліт (домінує ESR — гостра пилка) ──
    Lx, Lw = 50, 340
    frags.append(rect(Lx, 60, Lw, 250, fill="#fdecea", stroke=POS, sw=1.6, rx=10))
    frags.append(text(Lx + Lw / 2, 86, "Електроліт: ESR великий", size=13, color=POS, bold=True))
    mid = 180
    ax, aw = Lx + 30, Lw - 60
    frags.append(line(ax, mid, ax + aw, mid, color=MUTED, sw=1.1, dash="5,4"))
    # гостра пилка (форма струму котушки) з великою амплітудою
    pts = []
    seg = aw / 3.0
    for k in range(3):
        x0 = ax + k * seg
        pts += ["%.1f,%.1f" % (x0, mid + 46), "%.1f,%.1f" % (x0 + seg / 2, mid - 46),
                "%.1f,%.1f" % (x0 + seg, mid + 46)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), POS))
    frags.append(text(Lx + Lw / 2, 296, "гостра — повторює струм котушки", size=11, color=INK))

    # ── право: кераміка (домінує ємнісна — плавна) ──
    Rx, Rw = 450, 340
    frags.append(rect(Rx, 60, Rw, 250, fill="#eaf7ee", stroke=FIELD, sw=1.6, rx=10))
    frags.append(text(Rx + Rw / 2, 86, "Кераміка: ESR мізерний", size=13, color=FIELD, bold=True))
    bx, bw = Rx + 30, Rw - 60
    frags.append(line(bx, mid, bx + bw, mid, color=MUTED, sw=1.1, dash="5,4"))
    pts = []
    for i in range(0, int(bw) + 1, 4):
        y = mid - 14 * math.sin(2 * math.pi * (i / (bw / 3.0)))
        pts.append("%.1f,%.1f" % (bx + i, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(pts), FIELD))
    frags.append(text(Rx + Rw / 2, 296, "плавна — лишається ємнісна", size=11, color=INK))

    # формула знизу
    box, _, _ = textbox(W / 2, 370,
                        ["ΔVвих = ΔI/(8·f·C)   [ємнісна, плавна]   +   ΔI·ESR   [на ESR, гостра]"],
                        size=14, fill=FILL, stroke=LINE)
    frags.append(box)
    frags.append(text(W / 2, 424, "великий ESR → домінує гостра складова; мала ESR → лишається плавна",
                      size=12, color=MUTED))

    render(os.path.join(OUT, "esr-ripple.svg"), W, H, *frags,
           title="Дві складові вихідної пульсації: ємнісна плюс на ESR")


def fig_cap_types():
    """Чотири типи в координатах «ємність ↔ ESR» з підписом сильної й слабкої
    сторони кожного; стрілка показує типову комбінацію об'ємний + кераміка."""
    W, H = 820, 470
    rows = [
        ("Кераміка (MLCC)", "крихітний ESR і розмір, дешева", "просідає під напругою (DC-bias)", FIELD),
        ("Полімерний", "малий стабільний ESR, не висихає", "дорожчий", NEG),
        ("Електроліт", "велика ємність дешево", "великий ESR, старіння, висихання", POS),
        ("Тантал", "компактний за ємністю", "горить при перенапрузі — запас", POS),
    ]
    frags = []
    y = 70
    rh = 78
    for name, good, bad, col in rows:
        frags.append(rect(60, y, 700, rh - 12, fill=FILL, stroke=col, sw=1.6, rx=8))
        frags.append(text(80, y + 30, name, size=15, color=col, anchor="start", bold=True))
        frags.append(text(300, y + 22, "+  " + good, size=12, color=INK, anchor="start"))
        frags.append(text(300, y + 44, "−  " + bad, size=12, color=MUTED, anchor="start"))
        y += rh
    frags.append(text(W / 2, y + 18, "часто комбінують: об'ємний (електроліт/полімер) + кераміка поряд",
                      size=13, color=INK, bold=True))
    render(os.path.join(OUT, "cap-types.svg"), W, H, *frags,
           title="Типи конденсаторів: сильна й слабка сторона кожного")


def fig_dc_bias():
    """Крива «ємність ↔ прикладена напруга» MLCC: маркована при 0 В, при робочій
    напрузі обвалюється втричі. Тому беруть вищу напругу й більший номінал."""
    W, H = 760, 460
    L, R = 90, 660
    T, B = 70, 360
    frags = []
    frags.append(line(L, T, L, B, color=INK, sw=2))
    frags.append(line(L, B, R, B, color=INK, sw=2))
    frags.append(text(L - 50, (T + B) / 2, "ємність", size=13, color=INK))
    frags.append(text((L + R) / 2, B + 44, "прикладена напруга", size=13, color=INK))

    Vr = 25.0
    # вісь напруги
    for v in range(0, int(Vr) + 1, 5):
        x = L + (v / Vr) * (R - L)
        frags.append(line(x, B, x, B + 5, color=INK, sw=1.1))
        frags.append(text(x, B + 22, "%d" % v, size=11, color=MUTED))
    # маркована ємність 100% і ~30% при робочій напрузі
    Cnom = T + 20

    def cy(frac):  return B - frac * (B - Cnom)

    pts = []
    for k in range(0, 101):
        v = Vr * k / 100.0
        frac = 1.0 / (1.0 + (v / 9.0) ** 2)        # плавне спадання до ~0.25 на номіналі
        pts.append("%.1f,%.1f" % (L + (v / Vr) * (R - L), cy(frac)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join(pts), POS))
    # маркер 0 В
    frags.append(line(L, cy(1.0), L + 8, cy(1.0), color=NEG, sw=2))
    frags.append(text(L + 14, cy(1.0) + 4, "«10 мкФ» при 0 В", size=12, color=NEG, anchor="start", bold=True))
    # маркер на робочій напрузі (наприклад 16.8 В)
    vw = 16.8
    xw = L + (vw / Vr) * (R - L)
    fw = 1.0 / (1.0 + (vw / 9.0) ** 2)
    frags.append(line(xw, B, xw, cy(fw), color=FIELD, sw=1.4, dash="4,3"))
    frags.append(circle(xw, cy(fw), 5, fill=POS, stroke=POS))
    frags.append(text(xw + 10, cy(fw) + 4, "~3 мкФ при робочій напрузі", size=12, color=POS, anchor="start", bold=True))

    box, _, _ = textbox((L + R) / 2, 415,
                        "беруть кераміку на ВИЩУ номінальну напругу й більший номінал, ніж «на папері»",
                        size=12, fill="#eef7f0", stroke=FIELD)
    frags.append(box)
    render(os.path.join(OUT, "dc-bias.svg"), W, H, *frags,
           title="Просідання ємності MLCC під напругою (DC-bias)")


def fig_pick_flow():
    """Наскрізна процедура добору: три гілки (вихідний / вхідний / DC-bias)
    сходяться у «розмістити щільно до ключів»."""
    W, H = 860, 430
    frags = []
    cols = [
        ("ВИХІДНИЙ", ["за пульсацією", "(ємність + ESR)", "і за перехідним —", "бере більшу C"], FIELD),
        ("ВХІДНИЙ", ["за RMS-струмом", "пульсації", "Iнаван·√(D(1−D))", "кілька в паралель"], POS),
        ("КЕРАМІКА", ["рахувати з", "урахуванням", "DC-bias:", "запас ×2–3"], NEG),
    ]
    bw, gap = 240, 20
    x0 = (W - (3 * bw + 2 * gap)) / 2
    ytop, bh = 70, 170
    centers = []
    for i, (head, lines, col) in enumerate(cols):
        x = x0 + i * (bw + gap)
        frags.append(rect(x, ytop, bw, bh, fill=FILL, stroke=col, sw=1.8, rx=10))
        frags.append(text(x + bw / 2, ytop + 30, head, size=15, color=col, bold=True))
        yy = ytop + 60
        for ln in lines:
            frags.append(text(x + bw / 2, yy, ln, size=12, color=INK))
            yy += 22
        centers.append(x + bw / 2)
    # стрілки вниз до спільної рамки
    join_y = 330
    jbox, jw, jh = textbox(W / 2, join_y + 30,
                           "і все це — щільно до ключів (коротка гаряча петля струму)",
                           size=14, color=INK, bold=True, fill="#eef7f0", stroke=FIELD)
    for cx in centers:
        frags.append(arrow(cx, ytop + bh, cx, join_y, color=MUTED, sw=1.6))
    frags.append(jbox)
    render(os.path.join(OUT, "pick-flow.svg"), W, H, *frags,
           title="Наскрізний добір конденсаторів перетворювача")


def fig_ripple_compare():
    """Вставка math: стовпчики — внесок ємнісної складової й на ESR для кераміки
    (22 мкФ/3 мОм) проти електроліта (220 мкФ/200 мОм). Видно: ×10 ємності не
    рятує, бо ESR домінує."""
    W, H = 760, 460
    L, R = 90, 700
    T, B = 80, 360
    Vmax = 150.0
    frags = []
    frags.append(line(L, T, L, B, color=INK, sw=2))
    frags.append(line(L, B, R, B, color=INK, sw=2))
    frags.append(text(L - 50, (T + B) / 2, "пульсація, мВ", size=13, color=INK))
    for v in range(0, int(Vmax) + 1, 30):
        y = B - (v / Vmax) * (B - T)
        frags.append(line(L - 5, y, L, y, color=INK, sw=1.1))
        frags.append(text(L - 12, y + 4, "%d" % v, size=11, color=MUTED, anchor="end"))

    def bar(cx, val, col, lab):
        bw = 70
        y = B - (min(val, Vmax) / Vmax) * (B - T)
        out = rect(cx - bw / 2, y, bw, B - y, fill=col, stroke=col, sw=1, rx=4)
        out += text(cx, y - 10, lab, size=12, color=col, bold=True)
        return out

    # кераміка
    frags.append(text(220, B + 26, "Кераміка 22 мкФ / 3 мОм", size=12, color=FIELD, bold=True))
    frags.append(bar(160, 7.7, FIELD, "7.7"))
    frags.append(text(160, B + 46, "ємнісна", size=11, color=INK))
    frags.append(bar(270, 2.0, MUTED, "2.0"))
    frags.append(text(270, B + 46, "на ESR", size=11, color=INK))
    # електроліт
    frags.append(text(560, B + 26, "Електроліт 220 мкФ / 200 мОм", size=12, color=POS, bold=True))
    frags.append(bar(500, 0.77, MUTED, "0.77"))
    frags.append(text(500, B + 46, "ємнісна", size=11, color=INK))
    frags.append(bar(610, 136.0, POS, "136"))
    frags.append(text(610, B + 46, "на ESR", size=11, color=INK))

    frags.append(text(W / 2, 410, "×10 ємності в електроліта не рятує — увесь виграш з'їдає ESR",
                      size=13, color=INK, bold=True))
    render(os.path.join(OUT, "ripple-compare.svg"), W, H, *frags,
           title="Ємнісна складова проти ESR: кераміка проти електроліта")


if __name__ == "__main__":
    fig_roles()
    fig_input_pulses()
    fig_esr_ripple()
    fig_cap_types()
    fig_dc_bias()
    fig_pick_flow()
    fig_ripple_compare()
    print("ok figs")
