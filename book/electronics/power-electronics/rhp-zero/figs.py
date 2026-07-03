# -*- coding: utf-8 -*-
"""Фігури для теми rhp-zero (нуль правої півплощини).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5).
Підписи фігур живуть у Markdown, не в SVG — тут лише сама графіка."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8860b"   # особлива риса / «підступність»


def fig_splane():
    """Комплексна площина: звичайний нуль зліва (−ωz, безпечний) проти
    нуля правої півплощини справа (+ωz), дзеркальний по осі. Той самий модуль,
    протилежний бік — і в цьому вся біда."""
    W, H = 760, 400
    cx, cy = W / 2, 210          # центр осей
    ax = 300                     # піврозмах осі
    frags = []
    # осі
    frags.append(line(cx - ax, cy, cx + ax, cy, color=INK, sw=2))       # Re
    frags.append(text(cx + ax + 4, cy + 5, "Re", size=13, color=MUTED, anchor="start"))
    frags.append(line(cx, cy - 150, cx, cy + 150, color=INK, sw=2))     # Im
    frags.append(text(cx + 14, cy - 150, "Im", size=13, color=MUTED, anchor="start"))
    frags.append(text(cx + 8, cy + 20, "0", size=12, color=MUTED, anchor="start"))
    # тонований фон правої півплощини — «небезпечна» зона
    frags.append(rect(cx, cy - 150, ax, 300, fill="#fdecea", stroke="none", sw=0, rx=0))
    # осі домалюємо поверх заливки
    frags.append(line(cx - ax, cy, cx + ax, cy, color=INK, sw=2))
    frags.append(line(cx, cy - 150, cx, cy + 150, color=INK, sw=2))
    # лівий нуль (безпечний) — кружечок на −ωz
    zx = cx - 150
    frags.append(circle(zx, cy, 12, fill=BG, stroke=NEG, sw=3))
    frags.append(text(zx, cy + 40, "−ωz", size=15, color=NEG, bold=True))
    b1, w1, h1 = textbox(zx, cy - 60, ["звичайний нуль", "(ліва півплощина)",
                                       "піднімає підсилення", "І фазу — теж угору"],
                         size=12, color=NEG, fill="#eaf0fd", stroke=NEG, pad=9)
    frags.append(b1)
    # правий нуль (RHP) — кружечок на +ωz
    zx2 = cx + 150
    frags.append(circle(zx2, cy, 12, fill=BG, stroke=POS, sw=3))
    frags.append(text(zx2, cy + 40, "+ωz", size=15, color=POS, bold=True))
    b2, w2, h2 = textbox(zx2, cy - 72, ["нуль ПРАВОЇ", "півплощини (RHPZ)",
                                        "піднімає підсилення,", "але фазу тягне ВНИЗ",
                                        "— як полюс"],
                         size=12, color=POS, fill=BG, stroke=POS, pad=9)
    frags.append(b2)
    # підпис зони
    frags.append(text(cx + ax - 8, cy + 138, "права півплощина", size=12,
                      color=POS, anchor="end", italic=True))
    render(os.path.join(OUT, "splane.svg"), W, H, *frags,
           title="Один модуль, протилежний бік осі")


def fig_undershoot():
    """Крок керування: щойно контролер збільшив D (щоб підняти вихід),
    напруга спершу ПРОСІДАЄ, і аж потім лізе вгору до нової цілі.
    Це фізичний слід RHPZ у часі."""
    W, H = 820, 360
    ox, oy = 110, 250            # початок координат графіка
    axw, axh = 620, 190
    frags = []
    # осі
    frags.append(line(ox, oy - axh, ox, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))
    frags.append(text(ox + axw, oy + 22, "час", size=13, color=MUTED, anchor="end"))
    frags.append(text(ox - 12, oy - axh + 6, "Vвих", size=13, color=INK, anchor="end"))
    # рівень старої й нової цілі
    y_old = oy - 70
    y_new = oy - 140
    frags.append(line(ox, y_old, ox + axw, y_old, color=MUTED, sw=1.2, dash="5,5"))
    frags.append(text(ox + axw + 2, y_old + 4, "було", size=11, color=MUTED, anchor="start"))
    frags.append(line(ox, y_new, ox + axw, y_new, color=FIELD, sw=1.2, dash="5,5"))
    frags.append(text(ox + axw + 2, y_new + 4, "ціль", size=11, color=FIELD, anchor="start"))
    # момент кроку D
    x_step = ox + 140
    frags.append(line(x_step, oy, x_step, oy - axh, color=GOLD, sw=1.4, dash="4,4"))
    frags.append(text(x_step, oy - axh - 6, "тут збільшили D", size=12, color=GOLD, bold=True))
    # крива відгуку: рівна до кроку, провал, тоді підйом із перегулюванням до цілі
    pts = []
    for i in range(0, 141):
        x = ox + i
        pts.append((x, y_old))
    # провал і відновлення (від x_step)
    N = 480
    dip = 40          # глибина провалу, пікс
    for i in range(0, N + 1):
        t = i / N
        x = x_step + i * (axw - 140) / N
        # спершу вниз (перша чверть), тоді експо-підйом до y_new з легким дзвоном
        undershoot = dip * math.sin(math.pi * min(t * 2.2, 1)) * math.exp(-t * 1.2) if t < 0.6 else 0
        rise = (y_old - y_new) * (1 - math.exp(-3.0 * t))
        overs = 6 * math.exp(-3.5 * t) * math.sin(9 * t) if t > 0.25 else 0
        y = y_old + undershoot - rise + overs
        pts.append((x, y))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (poly, POS))
    # стрілка-акцент на провал
    frags.append(text(x_step + 70, oy - 8, "спершу ВНИЗ", size=13, color=POS, bold=True))
    frags.append(arrow(x_step + 70, oy - 20, x_step + 55, oy - 46, color=POS))
    frags.append(text(ox + axw - 70, y_new - 18, "а потім угору до цілі",
                      size=12, color=INK, anchor="end", italic=True))
    render(os.path.join(OUT, "undershoot.svg"), W, H, *frags,
           title="Просимо вгору — а воно спершу вниз")


def _axis(frags, ox, oy, axw, axh, xlabel, ylabel):
    frags.append(line(ox, oy - axh, ox, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))
    frags.append(text(ox + axw, oy + 20, xlabel, size=12, color=MUTED, anchor="end"))
    frags.append(text(ox - 8, oy - axh + 4, ylabel, size=12, color=INK, anchor="end"))


def fig_bode():
    """Слід RHPZ на Боде: підсилення після ωz задирається вгору (+20 дБ/дек,
    як звичайний нуль), а фаза натомість валиться на −90° (як полюс).
    Дві панелі одна під одною, спільна вісь частоти (лог)."""
    W, H = 860, 520
    ox = 120
    axw = 560                     # лишаємо праворуч поле під підписи-нахили
    # верх — підсилення
    oy1, axh1 = 190, 130
    frags = []
    _axis(frags, ox, oy1, axw, axh1, "частота (лог)", "|G|, дБ")
    x_z = ox + axw * 0.42         # положення ωz по осі (зсув уліво — місце під нахил)
    frags.append(line(x_z, oy1, x_z, oy1 - axh1, color=GOLD, sw=1.4, dash="4,4"))
    frags.append(text(x_z, oy1 - axh1 - 8, "ωz (нуль)", size=12, color=GOLD, bold=True))
    # рівна лінія до ωz, тоді підйом +20 дБ/дек
    ymid = oy1 - 40
    frags.append(line(ox, ymid, x_z, ymid, color=POS, sw=2.6))
    frags.append(line(x_z, ymid, ox + axw, ymid - 96, color=POS, sw=2.6))
    # підпис нахилу — НАД лінією, у чистому куті праворуч-угорі
    frags.append(text(ox + axw, oy1 - axh1 + 14, "+20 дБ/дек", size=13, color=POS,
                      anchor="end", bold=True))
    frags.append(text(ox + axw, oy1 - axh1 + 32, "(підсилення РОСТЕ)", size=11,
                      color=MUTED, anchor="end"))
    # пояснення пласкої ділянки — під лінією зліва, у порожнечі
    frags.append(text(ox + 18, oy1 - 14, "як у звичайного нуля", size=12,
                      color=MUTED, anchor="start"))
    # низ — фаза
    oy2, axh2 = 470, 150
    _axis(frags, ox, oy2, axw, axh2, "частота (лог)", "фаза, °")
    frags.append(line(x_z, oy2, x_z, oy2 - axh2, color=GOLD, sw=1.4, dash="4,4"))
    y0 = oy2 - axh2 + 18          # рівень 0°
    ym90 = oy2 - 22              # рівень −90°
    frags.append(line(ox, y0, ox + axw, y0, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(text(ox - 8, y0 + 4, "0°", size=11, color=MUTED, anchor="end"))
    frags.append(line(ox, ym90, ox + axw, ym90, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(text(ox - 8, ym90 + 4, "−90°", size=11, color=MUTED, anchor="end"))
    # фаза: рівна на 0, тоді плавний спад до −90 біля/після ωz (S-подібно)
    ph = []
    for i in range(0, int(axw) + 1):
        x = ox + i
        u = (x - x_z) / 80.0
        s = 1 / (1 + math.exp(-u))    # 0→1 сигмоїда
        y = y0 + (ym90 - y0) * s
        ph.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(ph), NEG))
    # підпис фази — над рівнем 0°, у чистій зоні праворуч-угорі панелі
    frags.append(text(ox + axw, y0 - 12, "а фаза ВНИЗ — як полюс", size=13, color=NEG,
                      anchor="end", bold=True))
    render(os.path.join(OUT, "bode.svg"), W, H, *frags,
           title="RHPZ на Боде: підсилення вгору, фаза вниз")


def fig_timeline():
    """Історична вставка hist-bode-nmp: ланцюг подій у Bell Labs, з якого
    народилося поняття «немінімальна фаза». Black (1927, зворотний зв'язок) →
    Nyquist (1932, критерій стійкості) → Bode (1938 діаграма, 1945 теорема
    підсилення–фази й поділ на мінімально-/немінімально-фазові). Одна дія,
    чотири дійові особи, причинна нитка зліва направо."""
    W, H = 940, 430
    ox = 60
    yaxis = 96                     # рівень осі часу (вгорі; віхи звисають донизу)
    axw = 820
    frags = []
    # вісь часу
    frags.append(line(ox, yaxis, ox + axw, yaxis, color=INK, sw=2))
    frags.append(arrow(ox + axw - 2, yaxis, ox + axw + 14, yaxis, color=INK))
    frags.append(text(ox + axw + 16, yaxis + 5, "час", size=13,
                      color=MUTED, anchor="start"))

    # чотири віхи (усі звисають ПІД віссю, рік — збоку вузла, щоб жодна
    # вертикаль не різала напис): (частка осі, рік, підпис-рамка, колір)
    milestones = [
        (0.06, "1927", ["Гарольд Блек", "негативний", "зворотний зв'язок"], NEG),
        (0.33, "1932", ["Гаррі Найквіст", "критерій", "стійкості"], FIELD),
        (0.59, "1938", ["Гендрік Боде", "асимптотична", "діаграма"], MUTED),
        (0.88, "1945", ["Боде: теорема", "підсилення–фази;", "мін./немін. фаза"], POS),
    ]
    for frac, yr, lbl, col in milestones:
        x = ox + axw * frac
        # вузол на осі
        frags.append(circle(x, yaxis, 7, fill=BG, stroke=col, sw=3))
        # рік — праворуч-угорі від вузла, поза вертикаллю-звязком
        frags.append(text(x + 12, yaxis - 12, yr, size=15, color=col,
                          bold=True, anchor="start"))
        cy_box = yaxis + 84
        b, w, h = textbox(x, cy_box, lbl, size=12, color=col,
                          fill=BG, stroke=col, pad=9)
        # звязок від вузла до ВЕРХНЬОГО краю рамки (не крізь неї)
        frags.append(line(x, yaxis + 8, x, cy_box - h / 2,
                          color=col, sw=1.3, dash="3,3"))
        frags.append(b)

    # нижня смуга — одна фізична причина всієї нитки
    by = 300
    b, w, h = textbox(ox + axw / 2, by,
                      ["Одна задача на всіх: підсилювачі для трансконтинентального",
                       "телефону дзвеніли. Щоб керувати їхньою стійкістю, довелося",
                       "розділити системи на мінімально- й немінімально-фазові —",
                       "останні (з нулями правої півплощини) фазу «крадуть»."],
                      size=13, color=INK, fill=FILL, stroke=MUTED, pad=14)
    frags.append(b)
    # стрілка від осі до смуги-суті
    frags.append(arrow(ox + axw / 2, by - h / 2 - 4, ox + axw / 2, by - h / 2 - 30,
                       color=MUTED))

    render(os.path.join(OUT, "timeline.svg"), W, H, *frags,
           title="Звідки взялася «немінімальна фаза»: нитка Bell Labs")


if __name__ == "__main__":
    fig_splane()
    fig_undershoot()
    fig_bode()
    fig_timeline()
    print("figs done")
