# -*- coding: utf-8 -*-
"""Фігури до статті «Модуляція тактового спектру (SSC)»
(book/electronics/digital/spread-spectrum-clocking).

Кут статті: та сама енергія лишається, але її РОЗМАЗУЮТЬ по частоті — тому
кожна вузька спиця гребінця гармонік осідає в широкий низький горб, і прилад
із фіксованим вікном бачить менший пік. Це не «менше завад», а «нижчий пік».

Фігури:
  spread.svg  — головна ідея: одна висока спиця ↔ той самий обшир, розмазаний у горб
  comb.svg    — гребінець гармонік такту до/після; що вища гармоніка, то ширший горб
  profile.svg — профіль модуляції: трикутник vs «Hershey-Kiss»; чому форма робить пласке плато
  rbw.svg     — чому виграш залежить від вікна приладу (RBW): вужче вікно — більший виграш
  timeline.svg — до вставки hist-lexmark-1994: шлях народження SSC (1991→1996)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

HOT = "#c0392b"    # пік (небезпека — те, що ловить норматив)
COOL = "#2457d6"   # розмазане


# ════════════════════════════════════════════════════════════════════════════
# 1. spread.svg — та сама площа: висока спиця → низький широкий горб
# ════════════════════════════════════════════════════════════════════════════
def fig_spread():
    W, H = 680, 340
    f = []
    f.append(text(W / 2, 30, "Енергія нікуди не ділася — її розмазали по частоті", size=15, bold=True))
    f.append(text(W / 2, 50, "площа під обома формами однакова; змінилася лише висота піку", size=11, color=MUTED))

    def axes(ox, oy, aw, ah):
        out = [arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6),
               arrow(ox, oy, ox, oy - ah, color=INK, sw=1.6)]
        out.append(text(ox + aw - 4, oy + 18, "частота", size=10, color=MUTED, anchor="end"))
        out.append(text(ox - 8, oy - ah + 6, "рівень", size=10, color=MUTED, anchor="end"))
        return "".join(out)

    ah = 200
    # ── ліва панель: гострий пік ──
    ox, oy, aw = 70, 250, 210
    f.append(axes(ox, oy, aw, ah))
    fx = ox + aw * 0.5
    f.append('<rect x="%.1f" y="%.1f" width="8" height="%.1f" fill="%s"/>' % (fx - 4, oy - (ah - 20), ah - 20, HOT))
    f.append(text(fx, oy - (ah - 20) - 8, "високий пік", size=12, color=HOT, bold=True))
    f.append(line(ox - 4, oy - (ah - 20), ox + 4, oy - (ah - 20), color=INK, sw=1.4))
    f.append(text(ox - 8, oy - (ah - 20) + 4, "P", size=11, color=HOT, anchor="end", bold=True))
    f.append(text(ox + aw / 2, oy + 34, "чистий такт", size=12, color=HOT, bold=True))
    f.append(text(ox + aw / 2, oy + 50, "уся сила в одній лінії", size=10, color=MUTED))

    # ── стрілка «розмазати» ──
    f.append(arrow(ox + aw + 18, 150, ox + aw + 58, 150, color=FIELD, sw=2.4))
    f.append(text(ox + aw + 38, 138, "SSC", size=12, color=FIELD, bold=True))
    f.append(text(ox + aw + 38, 168, "розмазати", size=10, color=FIELD))

    # ── права панель: низький горб тієї самої площі ──
    ox2 = ox + aw + 90
    f.append(axes(ox2, oy, aw, ah))
    # горб-«дзвін» тієї самої площі: пік нижчий у ~5 разів, ширина у ~5 разів
    peak_h = (ah - 20) / 5.0
    hw = aw * 0.28
    cx = ox2 + aw * 0.5
    pts = []
    N = 60
    for i in range(N + 1):
        t = i / N
        x = cx - hw + t * 2 * hw
        # трапеція-плато (як у трикутної модуляції: рівномірно розподілена частота)
        edge = 0.18
        if t < edge:
            h = peak_h * (t / edge)
        elif t > 1 - edge:
            h = peak_h * ((1 - t) / edge)
        else:
            h = peak_h * (1 + 0.06 * math.sin(t * 20))  # ледь хвиляста «полиця»
        pts.append((x, oy - h))
    poly = "M %.1f %.1f " % (pts[0][0], oy) + " ".join("L %.1f %.1f" % p for p in pts) + " L %.1f %.1f Z" % (pts[-1][0], oy)
    f.append('<path d="%s" fill="%s" fill-opacity="0.22" stroke="%s" stroke-width="2.2"/>' % (poly, COOL, COOL))
    f.append(line(ox2 - 4, oy - peak_h, ox2 + 4, oy - peak_h, color=INK, sw=1.4))
    f.append(text(ox2 - 8, oy - peak_h + 4, "P′", size=11, color=COOL, anchor="end", bold=True))
    # подвійна стрілка ширини
    f.append(line(cx - hw, oy - peak_h - 14, cx + hw, oy - peak_h - 14, color=MUTED, sw=1.2))
    f.append(text(cx, oy - peak_h - 20, "розмазано по Δf", size=11, color=COOL, bold=True))
    f.append(text(ox2 + aw / 2, oy + 34, "промодульований такт", size=12, color=COOL, bold=True))
    f.append(text(ox2 + aw / 2, oy + 50, "та сама сила, ширша смуга → нижчий пік", size=10, color=MUTED))
    render(os.path.join(IMG, "spread.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. comb.svg — гребінець гармонік: що вища гармоніка, то ширший розмаз
# ════════════════════════════════════════════════════════════════════════════
def fig_comb():
    W, H = 700, 340
    f = []
    f.append(text(W / 2, 28, "Гребінець гармонік такту: кожен зубець розмазується, дальні — сильніше", size=14, bold=True))

    ox, oy = 60, 250
    aw, ah = 600, 190
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.6))
    f.append(text(ox + aw - 4, oy + 18, "частота", size=10, color=MUTED, anchor="end"))

    f0 = 1  # умовна частота такту
    harm = [1, 3, 5, 7, 9, 11]        # непарні гармоніки меандру
    amp = [1.0, 0.34, 0.20, 0.145, 0.11, 0.09]  # ~1/n
    for k, (n, a) in enumerate(zip(harm, amp)):
        hx = ox + (n / 12.0) * aw
        h_hot = a * (ah - 30)
        # чистий зубець (гарячий) — тонка спиця
        f.append('<rect x="%.1f" y="%.1f" width="5" height="%.1f" fill="%s" fill-opacity="0.85"/>'
                 % (hx - 2.5, oy - h_hot, h_hot, HOT))
        # розмазаний горб (холодний): ширина ∝ n (бо абсолютний обшир n·Δ росте), пік ∝ a/n
        hw = 6 + n * 3.2
        peak = h_hot / (1 + n * 0.55)
        pts = []
        NN = 26
        for i in range(NN + 1):
            t = i / NN
            x = hx - hw + t * 2 * hw
            hh = peak * math.exp(-((t - 0.5) * 3.0) ** 2)  # дзвіночок
            pts.append((x, oy - hh))
        f.append('<path d="M ' + " L ".join("%.1f %.1f" % p for p in pts) + '" fill="none" stroke="%s" stroke-width="1.8"/>' % COOL)
        f.append(text(hx, oy + 16, "%d·f₀" % n if n > 1 else "f₀", size=10, color=MUTED))
    # легенда
    f.append('<rect x="%.1f" y="%.1f" width="10" height="10" fill="%s"/>' % (ox + 360, 44, HOT))
    f.append(text(ox + 376, 53, "чистий такт (спиці)", size=11, color=HOT, anchor="start", bold=True))
    f.append(line(ox + 360, 68, ox + 372, 68, color=COOL, sw=2))
    f.append(text(ox + 376, 72, "після SSC (горби)", size=11, color=COOL, anchor="start", bold=True))
    f.append(text(ox + aw - 6, oy - ah + 22, "дальні зубці розмазуються найширше", size=10, color=COOL, anchor="end", italic=True))
    render(os.path.join(IMG, "comb.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. profile.svg — профіль модуляції: трикутник дає плато, «Hershey-Kiss» — пласке
# ════════════════════════════════════════════════════════════════════════════
def fig_profile():
    W, H = 700, 360
    f = []
    f.append(text(W / 2, 28, "Форма модуляції вирішує, наскільки пласким вийде розмазаний горб", size=14, bold=True))

    def panel(ox, oy, title, prof, spec, col):
        out = []
        # ─ ліворуч: профіль f(t) ─
        aw, ah = 150, 90
        out.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.4))
        out.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.4))
        out.append(text(ox + aw - 2, oy + 15, "час", size=9, color=MUTED, anchor="end"))
        out.append(text(ox - 6, oy - ah + 6, "f", size=10, color=INK, anchor="end", bold=True))
        pts = []
        for i in range(81):
            t = i / 80.0
            y = prof(t)
            out.append(None)
            pts.append((ox + 8 + t * (aw - 16), oy - 8 - y * (ah - 22)))
        out.append('<path d="M ' + " L ".join("%.1f %.1f" % p for p in pts) + '" fill="none" stroke="%s" stroke-width="2.2"/>' % col)
        out.append(text(ox + aw / 2, oy + 30, title, size=12, color=col, bold=True))
        # ─ праворуч: який горб вона дає ─
        sx = ox + aw + 60
        sw2, sh2 = 150, 90
        out.append(arrow(sx, oy, sx + sw2, oy, color=INK, sw=1.4))
        out.append(arrow(sx, oy, sx, oy - sh2, color=INK, sw=1.4))
        out.append(text(sx + sw2 - 2, oy + 15, "частота", size=9, color=MUTED, anchor="end"))
        pts2 = []
        for i in range(81):
            t = i / 80.0
            y = spec(t)
            pts2.append((sx + 8 + t * (sw2 - 16), oy - 8 - y * (sh2 - 22)))
        poly = "M %.1f %.1f " % (pts2[0][0], oy) + " ".join("L %.1f %.1f" % p for p in pts2) + " L %.1f %.1f Z" % (pts2[-1][0], oy)
        out.append('<path d="%s" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="2"/>' % (poly, col, col))
        out.append(line(ox + aw + 18, oy - ah / 2, sx - 8, oy - ah / 2, color=MUTED, sw=1.2, dash="4 4"))
        out.append(arrow(sx - 20, oy - ah / 2, sx - 8, oy - ah / 2, color=MUTED, sw=1.2))
        return "".join(x for x in out if x)

    # трикутник: рівномірна швидкість проходу → плато з «вухами» (піки по краях)
    def tri(t):
        return 1 - abs(2 * t - 1)
    def tri_spec(t):
        # рівномірна щільність із загострами на краях (там f зупиняється й вертає)
        base = 0.62
        edge = 0.30 * (math.exp(-((t - 0.06) * 12) ** 2) + math.exp(-((t - 0.94) * 12) ** 2))
        return base + edge
    # «Hershey-Kiss»: більше часу проводить біля країв повільно → компенсує «вуха», плато рівне
    def hk(t):
        x = 2 * t - 1
        return 1 - x ** 2 * (1.5 - 0.5 * abs(x))  # опукло-вгнута, «поцілунок»
    def hk_spec(t):
        return 0.72 + 0.03 * math.sin(t * 14)  # майже рівна полиця

    f.append(panel(60, 150, "трикутник", tri, tri_spec, COOL))
    f.append(panel(60, 320, "«Hershey-Kiss»", hk, hk_spec, FIELD))

    bb, _, _ = textbox(W - 160, 150,
                       "трикутник простий, але\nдає «вуха» по краях\n(там f сповільнюється)",
                       size=10, color=INK, fill=FILL, stroke=COOL)
    f.append(bb)
    bb2, _, _ = textbox(W - 160, 320,
                       "опуклий профіль спеціально\nповільніше йде по краях —\nполиця виходить пласкою",
                       size=10, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(bb2)
    render(os.path.join(IMG, "profile.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. rbw.svg — виграш залежить від вікна приладу (RBW), що ковзає по горбу
# ════════════════════════════════════════════════════════════════════════════
def fig_rbw():
    W, H = 700, 340
    f = []
    f.append(text(W / 2, 28, "Скільки виграєш — вирішує вікно приладу (RBW), а не сам розмаз", size=14, bold=True))
    f.append(text(W / 2, 48, "прилад підсумовує енергію лише у своєму вузькому вікні й веде його по осі", size=11, color=MUTED))

    ox, oy = 70, 250
    aw, ah = 560, 180
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.6))
    f.append(text(ox + aw - 4, oy + 18, "частота", size=10, color=MUTED, anchor="end"))

    # розмазаний горб
    cx = ox + aw * 0.52
    hw = aw * 0.30
    peak = ah - 40
    pts = []
    N = 80
    def hump(x):  # 0..1 по горбу
        edge = 0.16
        if x < edge:  return x / edge
        if x > 1 - edge: return (1 - x) / edge
        return 1.0
    for i in range(N + 1):
        t = i / N
        xx = cx - hw + t * 2 * hw
        pts.append((xx, oy - peak * 0.5 * hump(t)))  # горб заввишки ~пів-екрана
    poly = "M %.1f %.1f " % (pts[0][0], oy) + " ".join("L %.1f %.1f" % p for p in pts) + " L %.1f %.1f Z" % (pts[-1][0], oy)
    f.append('<path d="%s" fill="%s" fill-opacity="0.16" stroke="%s" stroke-width="2"/>' % (poly, COOL, COOL))
    f.append(text(cx, oy - peak * 0.5 - 10, "розмазана енергія (Δf)", size=11, color=COOL, bold=True))

    # вікно RBW — вузький прямокутник, що ковзає; його «зібраний» рівень нижчий за весь горб
    rbwx = cx - hw * 0.15
    rbww = hw * 0.20
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.14" stroke="%s" stroke-width="1.8"/>'
             % (rbwx - rbww / 2, oy - ah + 10, rbww, ah - 10, HOT, HOT))
    f.append(text(rbwx, oy - ah + 4, "вікно RBW", size=11, color=HOT, bold=True))
    f.append(arrow(rbwx + rbww, oy - ah + 24, rbwx + rbww + 30, oy - ah + 24, color=HOT, sw=1.6))
    f.append(arrow(rbwx - rbww, oy - ah + 24, rbwx - rbww - 30, oy - ah + 24, color=HOT, sw=1.6))
    f.append(text(rbwx, oy - ah + 40, "ковзає", size=9, color=HOT))

    # рівень, який ловить вікно (частка енергії) — низька риска
    lvl = oy - peak * 0.5 * 0.30
    f.append(line(ox, lvl, ox + aw, lvl, color=HOT, sw=1.4, dash="6 4"))
    f.append(text(ox + aw - 4, lvl - 6, "що бачить прилад", size=10, color=HOT, anchor="end", bold=True))

    bb, _, _ = textbox(ox + 150, 92,
                       "вужче вікно й ширший розмаз → менша частка в кадрі → нижчий показ",
                       size=10, color=INK, fill=FILL, stroke=MUTED)
    f.append(bb)
    render(os.path.join(IMG, "rbw.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. timeline.svg — шлях народження SSC (до вставки hist-lexmark-1994)
# ════════════════════════════════════════════════════════════════════════════
def fig_timeline():
    W, H = 720, 300
    f = []
    f.append(text(W / 2, 30, "Як народилося SSC: від принтера, що не проходив EMC, до патенту", size=14, bold=True))
    f.append(text(W / 2, 50, "робоча реалізація й демонстрація випередили визнання й патент", size=11, color=MUTED))

    ox, oy = 90, 150
    aw = W - 150
    f.append(line(ox, oy, ox + aw, oy, color=INK, sw=2.2))
    f.append(arrow(ox + aw - 2, oy, ox + aw + 8, oy, color=INK, sw=2.2))

    # (частка_по_осі, підпис-дата, текст-подія, колір, вгору/вниз)
    events = [
        (0.00, "1991", "Lexmark\nвідокремлено від IBM", MUTED, +1),
        (0.25, "лист. 1993", "заявка на патент\nUS 5,488,627", FIELD, -1),
        (0.50, "серп. 1994", "доповідь у Чикаго +\nпринтер-прототип", POS, +1),
        (0.75, "1995", "дослідження завад →\nдоводи для FCC", NEG, -1),
        (1.00, "січ. 1996", "патент\nвидано", FIELD, +1),
    ]
    for frac, date, ev, col, updown in events:
        x = ox + frac * aw
        f.append(circle(x, oy, 7, fill=BG, stroke=col, sw=2.6))
        # дата — біля осі з протилежного боку від картки
        dy = oy + (18 if updown < 0 else -12)
        f.append(text(x, dy, date, size=11, color=col, bold=True))
        # картка події
        cy = oy - 62 if updown > 0 else oy + 66
        bb, bw, bh = textbox(x, cy, ev, size=10, color=INK, fill=FILL, stroke=col, pad=8)
        # ніжка від осі до картки
        edge = cy + (bh / 2 if updown > 0 else -bh / 2)
        f.append(line(x, oy + (-9 if updown > 0 else 9), x, edge, color=col, sw=1.3, dash="3 3"))
        f.append(bb)
    render(os.path.join(IMG, "timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_spread()
    fig_comb()
    fig_profile()
    fig_rbw()
    fig_timeline()
    print("OK: 5 фігур у", IMG)
