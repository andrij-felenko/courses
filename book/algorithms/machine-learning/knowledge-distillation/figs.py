# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── teacher-student: серце дистиляції — великий учитель дає м'які мітки, малий
# учень їх копіює. Ідея: показати, що вчиться учень НЕ на сирих даних із
# правильними відповідями, а на РОЗПОДІЛІ, що видає вчитель. Це головний кадр.
def fig_teacher_student():
    W, H = 860, 380
    p = []

    # ── УЧИТЕЛЬ (велика мережа) ──
    tx, ty, tw, th = 60, 92, 150, 150
    p.append(rect(tx, ty, tw, th, fill="#eaf0fd", stroke=NEG, sw=2.0, rx=10))
    p.append(text(tx + tw / 2, ty - 14, "УЧИТЕЛЬ", size=13, color=NEG, bold=True))
    p.append(text(tx + tw / 2, ty - 0.5 + 20, "велика точна", size=11, color=INK))
    p.append(text(tx + tw / 2, ty + 36, "мережа", size=11, color=INK))
    p.append(text(tx + tw / 2, ty + 66, "мільйони ваг", size=10, color=MUTED))
    p.append(text(tx + tw / 2, ty + 84, "повільна,", size=10, color=MUTED))
    p.append(text(tx + tw / 2, ty + 100, "важка", size=10, color=MUTED))
    # багато шарів-рисок як натяк на «велику»
    for i in range(4):
        lx = tx + 24 + i * 30
        p.append(line(lx, ty + 116, lx, ty + 138, color=NEG, sw=2.0))

    # ── стрілка «м'які мітки» ──
    ax0 = tx + tw + 8
    ax1 = ax0 + 150
    ay = ty + th / 2
    p.append(arrow(ax0, ay, ax1, ay, color="#8e44ad", sw=2.6))
    p.append(text((ax0 + ax1) / 2, ay - 26, "м'які мітки", size=12, color="#8e44ad", bold=True))
    p.append(text((ax0 + ax1) / 2, ay - 11, "(розподіл ймовірностей)", size=9.5, color="#8e44ad"))

    # ── УЧЕНЬ (мала мережа) ──
    sx, sy, sw2, sh = ax1 + 8, 120, 110, 96
    p.append(rect(sx, sy, sw2, sh, fill="#e9f7ef", stroke=FIELD, sw=2.0, rx=10))
    p.append(text(sx + sw2 / 2, sy - 14, "УЧЕНЬ", size=13, color=FIELD, bold=True))
    p.append(text(sx + sw2 / 2, sy + 26, "мала", size=11, color=INK))
    p.append(text(sx + sw2 / 2, sy + 44, "мережа", size=11, color=INK))
    p.append(text(sx + sw2 / 2, sy + 70, "у рази менша", size=9.5, color=MUTED))
    for i in range(2):
        lx = sx + 38 + i * 34
        p.append(line(lx, sy + 78, lx, sy + 90, color=FIELD, sw=2.0))

    # ── вхід: ті самі дані живлять учителя (він і породжує м'які мітки) ──
    dx, dy = 60, 296
    p.append(fitbox(dx, dy, 150, 40, "ті самі дані\n(без нових міток)", size=10.5,
                    fill=FILL, stroke="#c9d2dc", sw=1.2, color=INK))
    p.append(arrow(dx + 75, dy - 4, tx + tw / 2, ty + th + 4, color=INK, sw=1.6))

    # ── підпис-висновок ──
    p.append(fitbox(sx + sw2 + 30, 118, 264, 118,
                    "Учень не вчиться з нуля на\n"
                    "«правильних відповідях».\n"
                    "Він копіює ВЕСЬ розподіл\n"
                    "упевненості вчителя — і тому\n"
                    "за меншого розміру виходить\n"
                    "майже такий самий точний,\n"
                    "як великий учитель.",
                    size=10.5, fill="#fffaf0", stroke="#8e44ad", sw=1.4, color=INK))

    render(os.path.join(OUT, "teacher-student.svg"), W, H, *p,
           title="Дистиляція: малий учень копіює м'які мітки великого вчителя")


# ── soft-targets: тверда мітка (one-hot) проти м'якої (розподіл учителя).
# Ідея — показати «темне знання»: у твердій мітці лише «це 7», а м'яка каже
# ще й «трохи схоже на 1, ледь на 9» — саме ця додаткова тінь і вчить учня.
def fig_soft_targets():
    W, H = 860, 360
    p = []
    labels = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    hard = [0, 0, 0, 0, 0, 0, 0, 1.0, 0, 0]
    soft = [0.001, 0.10, 0.004, 0.003, 0.002, 0.002, 0.001, 0.82, 0.003, 0.06]

    pw, ph = 340, 200
    top = 78
    gap = 96
    x0 = 30

    def bars(px, vals, col, title, sub):
        frags = [rect(px, top, pw, ph, fill=BG, stroke="#c9d2dc", sw=1.2, rx=6)]

        def Y(v):
            return top + ph - v * (ph - 16)

        p_ = []
        n = len(vals)
        slot = pw / n
        bw = slot * 0.56
        for i, v in enumerate(vals):
            cx = px + slot * (i + 0.5)
            yt = Y(v)
            hgt = top + ph - yt
            frags.append(rect(cx - bw / 2, yt, bw, max(1.0, hgt), fill=col, stroke="none", sw=0, rx=2))
            frags.append(text(cx, top + ph + 15, labels[i], size=10, color=MUTED))
            if v >= 0.03:
                frags.append(text(cx, yt - 5, "%.2f" % v, size=8.5, color=INK, bold=True))
        frags.append(text(px + pw / 2, top - 34, title, size=13, color=col, bold=True))
        frags.append(text(px + pw / 2, top - 16, sub, size=10, color=MUTED))
        return frags

    px1 = x0
    px2 = x0 + pw + gap
    p += bars(px1, hard, NEG, "тверда мітка", "«це 7» — і нічого більше")
    p += bars(px2, soft, "#8e44ad", "м'яка мітка вчителя", "«7, трохи 1, ледь 9»")

    # стрілка-акцент на 1 і 9 у м'якій панелі — де ховається темне знання
    def cx_of(px, i):
        return px + (pw / 10) * (i + 0.5)

    for i in (1, 9):
        x = cx_of(px2, i)
        p.append(circle(x, top + ph - soft[i] * (ph - 16) - 18, 4, fill="none", stroke=POS, sw=1.6))
    p.append(text(cx_of(px2, 4), top + 30, "ця «тінь» на 1 і 9 —", size=10, color=POS, bold=True))
    p.append(text(cx_of(px2, 4), top + 46, "і є темне знання", size=10, color=POS, bold=True))

    p.append(fitbox(x0, top + ph + 30, W - 2 * x0, 44,
                    "Тверда мітка каже лише правильний клас. М'яка мітка вчителя несе ще й схожості:\n"
                    "що сімка трохи скидається на одиницю й ледь на дев'ятку — ця тінь і вчить учня.",
                    size=11, fill=FILL, stroke="#c9d2dc", sw=1.2, color=INK))

    render(os.path.join(OUT, "soft-targets.svg"), W, H, *p,
           title="Тверда мітка проти м'якої: де ховається «темне знання»")


# ── temperature: та сама трійка логітів за низької й високої температури.
# Ідея — показати, ЧОМУ гріють softmax: за T=1 розподіл гострий і тіні майже
# не видно; піднявши T, ми «висвітлюємо» дрібні ймовірності, і вчитель ділиться
# знанням про схожості. Приклад — логіти (4.0, 2.0, 1.0, 0.2).
def fig_temperature():
    W, H = 820, 340
    p = []
    logits = [4.0, 2.0, 1.0, 0.2]
    labels = ["кіт", "рись", "пес", "лис"]

    def softmax_T(z, T):
        e = [math.exp(v / T) for v in z]
        s = sum(e)
        return [v / s for v in e]

    pw, ph = 300, 196
    gap = 96
    top = 74
    x0 = 32

    def panel(px, T, name, col, note):
        probs = softmax_T(logits, T)
        p.append(rect(px, top, pw, ph, fill=BG, stroke="#c9d2dc", sw=1.2, rx=6))

        def Y(v):
            return top + ph - v * (ph - 18)

        for gv in (0.25, 0.5, 0.75):
            p.append(line(px, Y(gv), px + pw, Y(gv), color="#eef1f6", sw=1.0))
        n = len(probs)
        slot = pw / n
        bw = slot * 0.5
        for j, v in enumerate(probs):
            cx = px + slot * (j + 0.5)
            yt = Y(v)
            p.append(rect(cx - bw / 2, yt, bw, top + ph - yt, fill=col, stroke="none", sw=0, rx=3))
            p.append(text(cx, yt - 6, "%.2f" % v, size=10, color=INK, bold=True))
            p.append(text(cx, top + ph + 15, labels[j], size=10, color=MUTED))
        p.append(text(px + pw / 2, top - 34, "T = %.0f" % T, size=13, color=col, bold=True))
        p.append(text(px + pw / 2, top - 16, name, size=10.5, color=MUTED))
        p.append(fitbox(px, top + ph + 26, pw, 34, note, size=10, fill=FILL,
                        stroke="#c9d2dc", sw=1.1, color=INK))

    panel(x0, 1.0, "холодно (штатно)", NEG,
          "лідер забирає майже все,\nтіні майже не видно")
    panel(x0 + pw + gap, 4.0, "гаряче", POS,
          "дрібні ймовірності\nвисвітлились — видно схожості")

    render(os.path.join(OUT, "temperature.svg"), W, H, *p,
           title="Температура: нагрів softmax висвітлює приховані схожості")


# ── distill-step: потік ОДНОГО кроку навчання учня. Ідея — показати, що з тих
# самих логітів народжуються ТРИ softmax (учень@T, учитель@T, учень@1) і ДВІ
# гілки втрати (дистиляційна ×T²×α та якірна ×(1−α)), які зливаються в один
# градієнт dL/dz. Це кадр саме коду-проєкту, не теми: видно, де живе кожна
# з чотирьох пасток (спільна T, множник T², T=1 для якоря).
def fig_distill_step():
    W, H = 900, 500
    p = []

    # три колонки softmax визначають усю сітку; логіти сідають над ними
    smw, smh = 176, 52
    smy = 150
    col_gap = 254                                   # крок між центрами колонок
    cx_q = 150 + smw / 2                             # учитель@T (ліва колонка)
    cx_ps = cx_q + col_gap                           # учень@T  (середня)
    cx_ph = cx_ps + col_gap                          # учень@1  (права)

    # ── коробки логітів угорі ──
    tw, th = 158, 46
    ly = 30
    # логіти вчителя — над колонкою q
    p.append(rect(cx_q - tw / 2, ly, tw, th, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    p.append(text(cx_q, ly + 19, "логіти вчителя", size=11.5, color=NEG, bold=True))
    p.append(text(cx_q, ly + 35, "z_t (сталі, кеш)", size=9.5, color=MUTED))
    # логіти учня — над серединою між колонками учня (ps і ph)
    cx_sz = (cx_ps + cx_ph) / 2
    p.append(rect(cx_sz - tw / 2, ly, tw, th, fill="#e9f7ef", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(cx_sz, ly + 19, "логіти учня", size=11.5, color=FIELD, bold=True))
    p.append(text(cx_sz, ly + 35, "z_s (прямий хід)", size=9.5, color=MUTED))

    # ── три softmax-блоки ──
    def sm(cx, title, sub, col):
        px = cx - smw / 2
        p.append(rect(px, smy, smw, smh, fill=BG, stroke=col, sw=1.6, rx=8))
        p.append(text(cx, smy + 21, title, size=11.5, color=col, bold=True))
        p.append(text(cx, smy + 39, sub, size=9.5, color=MUTED))

    sm(cx_q, "softmax_T  (T)", "q — м'яка мітка вчителя", NEG)
    sm(cx_ps, "softmax_T  (T)", "p_soft — м'який учень", FIELD)
    sm(cx_ph, "softmax_T  (T=1)", "p_hard — гострий учень", FIELD)

    # стрілки логіти → softmax
    p.append(arrow(cx_q, ly + th, cx_q, smy, color=INK, sw=1.5))
    p.append(arrow(cx_sz, ly + th, cx_ps, smy, color=INK, sw=1.5))
    p.append(arrow(cx_sz, ly + th, cx_ph, smy, color=INK, sw=1.5))

    # маркер «спільна T» між колонками q і ps — пастка неузгодженої температури
    midT = (cx_q + smw / 2 + cx_ps - smw / 2) / 2
    p.append(line(cx_q + smw / 2, smy + smh / 2, cx_ps - smw / 2, smy + smh / 2,
                  color=POS, sw=1.5, dash="5,3"))
    p.append(text(midT, smy + smh / 2 - 8, "та сама T", size=10, color=POS, bold=True))

    # ── дві гілки втрати ──
    by = 278
    bw, bh = 264, 58
    dist_cx = (cx_q + cx_ps) / 2                     # під лівою парою колонок
    anch_cx = cx_ph                                  # під правою колонкою
    p.append(rect(dist_cx - bw / 2, by, bw, bh, fill="#fffaf0", stroke="#8e44ad", sw=1.8, rx=8))
    p.append(text(dist_cx, by + 20, "дистиляційна втрата", size=12, color="#8e44ad", bold=True))
    p.append(text(dist_cx, by + 40, "CE(q, p_soft) · T²   →  × α", size=10.5, color=INK))
    p.append(rect(anch_cx - bw / 2, by, bw, bh, fill=FILL, stroke=NEG, sw=1.8, rx=8))
    p.append(text(anch_cx, by + 20, "якір на тверду мітку", size=12, color=NEG, bold=True))
    p.append(text(anch_cx, by + 40, "CE(onehot, p_hard) → ×(1−α)", size=10.5, color=INK))

    # softmax → гілки (q і ps → дистиляційна; ph → якір)
    p.append(arrow(cx_q, smy + smh, dist_cx - bw * 0.30, by, color="#8e44ad", sw=1.6))
    p.append(arrow(cx_ps, smy + smh, dist_cx + bw * 0.30, by, color="#8e44ad", sw=1.6))
    p.append(arrow(cx_ph, smy + smh, anch_cx, by, color=NEG, sw=1.6))

    # ── злиття в градієнт ──
    gy = 402
    gw, gh = 336, 50
    gcx = W / 2
    gx = gcx - gw / 2
    p.append(rect(gx, gy, gw, gh, fill="#eef7f0", stroke=FIELD, sw=2.2, rx=9))
    p.append(text(gcx, gy + 21, "градієнт на логітах учня  dL/dz", size=12.5, color=FIELD, bold=True))
    p.append(text(gcx, gy + 39, "α·T·(p_soft−q) + (1−α)·(p_hard−onehot)", size=10.5, color=INK))
    p.append(arrow(dist_cx, by + bh, gcx - gw * 0.28, gy, color="#8e44ad", sw=1.8))
    p.append(arrow(anch_cx, by + bh, gcx + gw * 0.28, gy, color=NEG, sw=1.8))

    # хвіст: у зворотне поширення
    p.append(arrow(gcx, gy + gh, gcx, gy + gh + 20, color=INK, sw=1.8))
    p.append(text(gcx, gy + gh + 36, "→ зворотне поширення учня → крок спуску",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "distill-step.svg"), W, H, *p,
           title="Один крок дистиляції: три softmax і дві гілки втрати в один градієнт")


# ── distillation-timeline: три віхи однієї думки для історичної вставки.
# 2006 (Корнелл, ідея стиснути ансамбль) → 2014 (Гінтон, «темне знання»,
# нагрітий softmax) → 2015 (стаття «дистиляція», м'які цілі, T², демо).
# Ідея кадру — показати ОКРЕМІСТЬ трьох кроків і що саме додав кожен, аби
# читач не приписав увесь прийом одній праці.
def fig_distillation_timeline():
    W, H = 900, 380
    p = []

    # горизонтальна вісь часу
    ax0, ax1 = 60, W - 60
    ayl = 118
    p.append(line(ax0, ayl, ax1, ayl, color=MUTED, sw=2.4))
    p.append(arrow(ax1 - 2, ayl, ax1 + 2, ayl, color=MUTED, sw=2.4))

    # три віхи: (частка по осі, рік, колір, заголовок, підпис-суть)
    milestones = [
        (0.12, "2006", NEG, "Стиснення ансамблю",
         "Корнелл: Бучілуе,\nКаруана, Нікулеску-Мізіл.\n«Model Compression», KDD.\nУчитель-ансамбль → мала\nмережа (~1000× менша),\nвчиться на ВІДПОВІДЯХ,\nа не на мітках.\nЩе без назви й теорії."),
        (0.50, "2014", "#8e44ad", "«Темне знання»",
         "Гінтон, доповідь у TTIC.\nДрібні ймовірності —\nне шум, а мапа схожостей\nміж класами.\nКлюч: ГРІТИ softmax\nтемпературою, щоб її\nвисвітлити.\nЗ'явилась НАЗВА ідеї."),
        (0.86, "2015", POS, "Формалізація",
         "Гінтон, Віньялс, Дін.\n«Distilling the Knowledge»\n(arXiv:1503.02531).\nМ'які цілі, дві втрати,\nмножник T².\nДемо: MNIST + бойова\nголосова система.\nНазва «ДИСТИЛЯЦІЯ»."),
    ]

    bw = 236
    for frac, year, col, head, body in milestones:
        cx = ax0 + (ax1 - ax0) * frac
        # вузол на осі
        p.append(circle(cx, ayl, 8, fill=col, stroke=BG, sw=2.4))
        # рік над віссю
        p.append(text(cx, ayl - 22, year, size=20, color=col, bold=True))
        # картка-опис під віссю
        bx = cx - bw / 2
        bx = max(6, min(bx, W - bw - 6))       # не вилазити за полотно
        by = ayl + 20
        bh = 214
        p.append(rect(bx, by, bw, bh, fill=FILL, stroke=col, sw=1.6, rx=8))
        p.append(line(cx, ayl + 8, cx, by, color=col, sw=1.4, dash="3,3"))
        p.append(text(bx + bw / 2, by + 22, head, size=13, color=col, bold=True))
        p.append(mtext(bx + bw / 2, by + 44, body, size=10, color=INK, lh=1.32))

    render(os.path.join(OUT, "distillation-timeline.svg"), W, H, *p,
           title="Три віхи дистиляції: ідея (2006) → назва (2014) → канон (2015)")


# ── gradient-scaling: величина градієнта м'якої втрати проти температури на
# лог-лог масштабі. Ідея вставки-математики — показати ОКОМ, що без поправки
# градієнт падає як 1/T² (пряма з нахилом −2), а домноження на T² робить його
# сталим (горизонталь). Саме це виведення й виправдовує множник T².
def fig_gradient_scaling():
    W, H = 760, 430
    p = []

    # ── поле графіка (лог-лог: x = log2 T, y = log2 величини градієнта) ──
    ox, oy = 132, 66
    pw, ph = 528, 268
    bx, by = ox, oy + ph            # початок осей (низ-ліво)

    Tlog_min, Tlog_max = 0.0, 4.0   # T від 1 до 16
    ylog_min, ylog_max = -8.5, 0.8

    def X(tl):
        return bx + (tl - Tlog_min) / (Tlog_max - Tlog_min) * pw

    def Y(yl):
        return by - (yl - ylog_min) / (ylog_max - ylog_min) * ph

    # сітка + підписи T на осі x
    for tl, lab in [(0, "1"), (1, "2"), (2, "4"), (3, "8"), (4, "16")]:
        gx = X(tl)
        p.append(line(gx, oy, gx, by, color="#eef1f6", sw=1.0))
        p.append(text(gx, by + 18, lab, size=10.5, color=MUTED))
    for yl in range(-8, 1, 2):
        p.append(line(bx, Y(yl), bx + pw, Y(yl), color="#eef1f6", sw=1.0))

    # осі
    p.append(line(bx, oy, bx, by, color=INK, sw=1.6))
    p.append(line(bx, by, bx + pw, by, color=INK, sw=1.6))
    p.append(text(bx + pw / 2, by + 40, "температура T  (лог-масштаб)", size=11.5, color=INK))
    # підпис осі y — горизонтально над віссю (text() не має обертання)
    p.append(text(bx - 6, oy - 20, "величина градієнта", size=11, color=INK, anchor="start"))
    p.append(text(bx - 6, oy - 6, "(лог-масштаб)", size=9.5, color=MUTED, anchor="start"))

    # ── без поправки: пряма з нахилом −2 (∝ 1/T²) ──
    x0, y0 = X(0.0), Y(0.0)
    x1, y1 = X(4.0), Y(-8.0)        # −2·4 = −8
    p.append(line(x0, y0, x1, y1, color=NEG, sw=2.8))
    p.append(circle(x0, y0, 4.2, fill=NEG, stroke="none", sw=0))
    p.append(circle(x1, y1, 4.2, fill=NEG, stroke="none", sw=0))
    p.append(text(X(2.55), Y(-3.9) - 8, "без поправки:  ∝ 1/T²", size=11.5, color=NEG, bold=True))
    p.append(text(X(2.55), Y(-3.9) + 9, "нахил = −2", size=10, color=NEG))

    # ── з множником T²: горизонталь (стале) ──
    p.append(line(X(0.0), Y(0.0), X(4.0), Y(0.0), color=POS, sw=2.8))
    p.append(text(X(2.0), Y(0.0) - 11, "× T²  →  стале, не залежить від T",
                  size=11.5, color=POS, bold=True))

    # ── акцент: за T=4 провал у 16 разів ──
    axT = X(2.0)                    # T = 4
    p.append(line(axT, Y(0.0), axT, Y(-4.0), color=MUTED, sw=1.2, dash="4 3"))
    p.append(arrow(axT + 16, Y(-0.3), axT + 16, Y(-3.7), color=MUTED, sw=1.4))
    p.append(text(axT + 22, Y(-1.8), "T=4:", size=10, color=MUTED, anchor="start"))
    p.append(text(axT + 22, Y(-1.8) + 15, "слабший", size=10, color=MUTED, anchor="start"))
    p.append(text(axT + 22, Y(-1.8) + 30, "у 16 разів", size=10, color=MUTED, anchor="start"))

    # ── підпис-висновок унизу ──
    p.append(fitbox(ox, by + 54, pw, 36,
                    "Один множник 1/T — від похідної softmax; другий — від стиснення різниць за великих T.\n"
                    "Разом 1/T². Домноження втрати на T² точно це скасовує — баланс тримається за будь-якої T.",
                    size=10.5, fill=FILL, stroke="#c9d2dc", sw=1.1, color=INK))

    render(os.path.join(OUT, "gradient-scaling.svg"), W, H, *p,
           title="Градієнт м'якої втрати ∝ 1/T²; множник T² його скасовує")


if __name__ == "__main__":
    fig_teacher_student()
    fig_soft_targets()
    fig_temperature()
    fig_distill_step()
    fig_distillation_timeline()
    fig_gradient_scaling()
    print("OK: figures written to", OUT)
