# -*- coding: utf-8 -*-
"""Фігури до теми «Шум квантування» (аналогова електроніка).

Фокус теми — шум квантування як УНІВЕРСАЛЬНЕ джерело шуму: усюди, де неперервну
величину заганяють на скінченну сітку рівнів (вхід АЦП, вихід ЦАП, округлення
у цифровій арифметиці), народжується та сама адитивна похибка e = q − x.

Фігури головної статті:
  additive-model.svg  — квантувач ⇄ «сигнал + джерело шуму»: одна й та сама поведінка,
                        два погляди; e рівномірна на ±q/2, некорельована → біла.
  where-it-lives.svg  — той самий шум у чотирьох місцях тракту (АЦП, ЦАП, множення
                        у фільтрі, перекодування слова) — одна модель, різні точки.
  controllable.svg    — чим шум квантування ВІДРІЗНЯЄТЬСЯ від теплового: його можна
                        і посунути (дизер), і перерозподілити по частоті (формування).

Фігури вставки proj-requantize (перекодування розрядності у цифрі):
  requantize-ladder.svg  — чотири щаблі приборкання похибки перекодування:
                           відсікання → округлення → TPDF-дизер → формування шуму,
                           з тим, що кожен щабель прибирає.
  error-feedback.svg     — блок-схема формувача першого порядку: округлюємо, беремо
                           похибку округлення, затримуємо на відлік, додаємо назад.
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def additive_model():
    """Дві еквівалентні схеми одного квантувача.
    Ліворуч — «чорна скринька» Q: неперервний x → квантований q.
    Праворуч — той самий блок, розкладений у модель: q = x + e, де e —
    рівномірне на ±q/2, некорельоване з x джерело білого шуму.
    Унизу — сам сигнал e у часі (пилка ±q/2) як доказ «це шум»."""
    W, H = 760, 470
    p = []

    # ── ЛІВА СХЕМА: чорна скринька ──
    lx = 70
    by = 120
    p.append(text(lx + 120, 62, "Як воно є: округлення до рівнів", size=13, bold=True, color=INK))
    # вхід
    p.append(line(lx, by, lx + 60, by, color=NEG, sw=2))
    p.append(arrow(lx + 40, by, lx + 62, by, color=NEG, sw=2))
    p.append(text(lx + 8, by - 12, "x (неперервний)", size=12, color=NEG, anchor="start"))
    # блок Q
    p.append(rect(lx + 62, by - 34, 96, 68, fill="#eef0f2", stroke=INK, sw=2))
    p.append(text(lx + 110, by - 6, "Q", size=22, bold=True))
    p.append(text(lx + 110, by + 16, "квантувач", size=10, color=MUTED))
    # вихід
    p.append(line(lx + 158, by, lx + 240, by, color=POS, sw=2))
    p.append(arrow(lx + 218, by, lx + 242, by, color=POS, sw=2))
    p.append(text(lx + 246, by - 12, "q (на рівнях)", size=12, color=POS, anchor="start"))

    # ── ЗНАК ЕКВІВАЛЕНТНОСТІ ──
    p.append(text(W / 2, by + 4, "≡", size=30, bold=True, color=MUTED))

    # ── ПРАВА СХЕМА: модель «сигнал + шум» ──
    rx = 470
    p.append(text(rx + 100, 62, "Як це рахувати: q = x + e", size=13, bold=True, color=INK))
    p.append(line(rx, by, rx + 66, by, color=NEG, sw=2))
    p.append(text(rx - 4, by - 12, "x", size=13, bold=True, color=NEG, anchor="start"))
    # суматор
    cx = rx + 84
    p.append(circle(cx, by, 16, fill=BG, stroke=INK, sw=2))
    p.append(text(cx, by + 5, "+", size=18, bold=True))
    p.append(arrow(rx + 60, by, cx - 16, by, color=NEG, sw=2))
    # джерело шуму e знизу в суматор
    ey = by + 78
    p.append(rect(cx - 60, ey - 20, 120, 40, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(cx, ey - 3, "джерело шуму e", size=11, bold=True, color=POS))
    p.append(text(cx, ey + 13, "рівн. ±q/2, біле", size=10, color=POS))
    p.append(line(cx, ey - 20, cx, by + 16, color=POS, sw=2))
    p.append(arrow(cx, ey - 40, cx, by + 16, color=POS, sw=2))
    # вихід
    p.append(line(cx + 16, by, cx + 96, by, color=POS, sw=2))
    p.append(arrow(cx + 74, by, cx + 98, by, color=POS, sw=2))
    p.append(text(cx + 102, by - 12, "q", size=13, bold=True, color=POS, anchor="start"))

    # ── НИЖНЯ СМУГА: сам сигнал e(t) — пилка ±q/2 ──
    ax0 = 120
    span = 520
    e_mid = 300
    e_amp = 34
    p.append(line(ax0, e_mid, ax0 + span + 16, e_mid, color=MUTED, sw=1.3))
    p.append(line(ax0, e_mid - e_amp - 8, ax0, e_mid + e_amp + 8, color=INK, sw=1.5))
    p.append(text(ax0 - 8, e_mid + 4, "e", size=13, bold=True, anchor="end"))
    p.append(text(ax0 + span / 2, e_mid + e_amp + 26, "час →", size=11, color=MUTED))
    # рівні ±q/2
    p.append(line(ax0, e_mid - e_amp, ax0 + span, e_mid - e_amp, color=FIELD, sw=1.2, dash="4 4"))
    p.append(line(ax0, e_mid + e_amp, ax0 + span, e_mid + e_amp, color=FIELD, sw=1.2, dash="4 4"))
    p.append(text(ax0 + span + 6, e_mid - e_amp + 4, "+q/2", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(text(ax0 + span + 6, e_mid + e_amp + 4, "−q/2", size=11, bold=True, color=FIELD, anchor="start"))
    # хаотична пилка в межах ±q/2 (жвавий сигнал → похибка стрибає безсистемно)
    random.seed(11)
    pts = []
    x = ax0
    while x <= ax0 + span:
        pts.append((x, e_mid + (random.random() - 0.5) * 2 * e_amp))
        x += 15
    d = "M" + " L".join("%.1f %.1f" % (a, b) for a, b in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, POS))
    p.append(text(ax0 + span / 2, e_mid - e_amp - 12,
                  "похибка e стрибає в межах ±q/2 безсистемно — це й є шум", size=11,
                  color=POS, anchor="middle"))

    b, _, _ = textbox(W / 2, H - 38,
                      "Той самий квантувач — два погляди. Зліва: округлення до рівнів (як воно діє).\n"
                      "Справа: сигнал плюс окреме джерело шуму e = q − x (як це рахувати). За жвавого\n"
                      "сигналу e рівномірна на ±q/2 й некорельована — тобто біла: модель точна.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, 'additive-model.svg'), W, H, *p,
           title="Квантувач як «сигнал + джерело шуму»: q = x + e")


def where_it_lives():
    """Одна модель q = x + e — у чотирьох місцях цифрового тракту.
    Кожен блок, що зводить неперервне/довше на коротшу сітку, підмішує своє e."""
    W, H = 760, 430
    p = []

    p.append(text(W / 2, 54, "Один і той самий шум — усюди, де величину тиснуть на грубшу сітку",
                  size=13, bold=True, color=INK))

    # ланцюг блоків
    ry = 150
    bw, bh = 128, 66
    gap = 30
    x = 60
    blocks = [
        ("АЦП", "неперервна\nнапруга → код", NEG),
        ("множення\nу фільтрі", "добуток →\nкоротше слово", FIELD),
        ("перекодування", "24 біт →\n16 біт", POS),
        ("ЦАП", "код → рівні\nнапруги", MUTED),
    ]
    centers = []
    for i, (name, sub, hue) in enumerate(blocks):
        bx = x + i * (bw + gap)
        centers.append(bx + bw / 2)
        fill = {NEG: "#eaf0fd", FIELD: "#eafaf0", POS: "#fdecea", MUTED: "#eef0f2"}[hue]
        p.append(rect(bx, ry - bh / 2, bw, bh, fill=fill, stroke=hue, sw=2))
        # назва + підпис (двома рядками через mtext)
        p.append(mtext(bx + bw / 2, ry - 6, name, size=12.5, bold=True, color=hue))
        p.append(mtext(bx + bw / 2, ry + 16, sub, size=9.5, color=MUTED))
        # стрілка між блоками
        if i > 0:
            px = x + (i - 1) * (bw + gap) + bw
            p.append(line(px, ry, bx, ry, color=INK, sw=1.6))
            p.append(arrow(px, ry, bx, ry, color=INK, sw=1.6))
        # «+e» знизу — доданий шум квантування
        ndy = ry + bh / 2 + 34
        p.append(circle(bx + bw / 2, ndy, 13, fill="#fdecea", stroke=POS, sw=1.8))
        p.append(text(bx + bw / 2, ndy + 4, "+e", size=11, bold=True, color=POS))
        p.append(line(bx + bw / 2, ndy - 13, bx + bw / 2, ry + bh / 2, color=POS, sw=1.4, dash="3 3"))

    p.append(text(centers[0], ry - bh / 2 - 14, "вхід", size=11, bold=True, color=MUTED))
    p.append(text(centers[-1], ry - bh / 2 - 14, "вихід", size=11, bold=True, color=MUTED))

    # спільний підпис лінійки шуму
    p.append(text(W / 2, ry + bh / 2 + 66,
                  "кожен блок додає свою порцію e = q/√12 незалежно від інших",
                  size=11.5, bold=True, color=POS))

    b, _, _ = textbox(W / 2, H - 34,
                      "Шум квантування — не властивість АЦП, а властивість самої операції «округлити до сітки».\n"
                      "Він з'являється однаково: на вході АЦП, при округленні добутку у цифровому фільтрі, при\n"
                      "скороченні розрядності слова, на виході ЦАП. Скрізь та сама модель q = x + e, e ≈ q/√12.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, 'where-it-lives.svg'), W, H, *p,
           title="Шум квантування живе не лише в АЦП")


def controllable():
    """Чим шум квантування відрізняється від теплового: тепловий — стихія (його
    RMS задає температура й опір, форма спектра фіксована), а шум квантування
    народжується з ДЕТЕРМІНОВАНОЇ операції, тож ним можна КЕРУВАТИ:
      • дизером — зробити чесно білим навіть на тихому сигналі;
      • формуванням шуму — прибрати з корисної смуги, зіпхнувши у високі частоти."""
    W, H = 760, 470
    p = []

    # три міні-спектри в ряд: тепловий (фіксований), квант.-білий, квант.-формований
    def spectrum(x0, span, base, h, head, hue, shape):
        p.append(line(x0, base, x0 + span, base, color=INK, sw=1.4))
        p.append(line(x0, base, x0, base - h - 6, color=INK, sw=1.4))
        p.append(text(x0 + span / 2, base + 20, "частота →", size=10, color=MUTED))
        p.append(text(x0 + span / 2, base - h - 16, head, size=11.5, bold=True, color=hue))
        # корисна смуга (зелена зона) ліворуч
        Bpx = span * 0.34
        p.append(rect(x0, base - h - 2, Bpx, h + 2, fill="#eafaf0", stroke=None, sw=0))
        p.append(text(x0 + Bpx / 2, base - h + 8, "смуга", size=9, color=FIELD))
        p.append(text(x0 + Bpx / 2, base - h + 19, "сигналу", size=9, color=FIELD))
        # крива щільності
        random.seed(3)
        pts = []
        k = 0
        while k <= span:
            t = k / span
            if shape == "flat_fixed":
                yv = 0.5
            elif shape == "flat":
                yv = 0.5
            else:  # shaped: низько в смузі, круто вгору поза нею
                yv = 0.08 + 0.9 * (t ** 2.2)
            jit = 0.05 * random.random()
            pts.append((x0 + k, base - h * (yv + jit)))
            k += 8
        d = "M" + " L".join("%.1f %.1f" % (a, b) for a, b in pts)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, hue))
        return Bpx

    top = 120
    band_h = 96
    spectrum(70, 190, top + band_h, band_h, "Тепловий шум:", MUTED, "flat_fixed")
    spectrum(300, 190, top + band_h, band_h, "Квантування, білий:", NEG, "flat")
    spectrum(530, 190, top + band_h, band_h, "Квантування, формований:", POS, "shaped")

    # підписи під кожним
    p.append(text(70 + 95, top + band_h + 44, "стихія: рівень задають", size=10, color=MUTED, anchor="middle"))
    p.append(text(70 + 95, top + band_h + 58, "T і R — не посунути", size=10, color=MUTED, anchor="middle"))
    p.append(text(300 + 95, top + band_h + 44, "рівно по смузі; дизер", size=10, color=NEG, anchor="middle"))
    p.append(text(300 + 95, top + band_h + 58, "тримає його чесним", size=10, color=NEG, anchor="middle"))
    p.append(text(530 + 95, top + band_h + 44, "виштовхнутий ВГОРУ:", size=10, color=POS, anchor="middle"))
    p.append(text(530 + 95, top + band_h + 58, "у смузі — майже нуль", size=10, color=POS, anchor="middle"))

    # стрілки-дуги «керуємо»: від білого до формованого
    p.append(text(W / 2, top + band_h + 90, "дизер робить білим  ·  формування прибирає зі смуги",
                  size=11, bold=True, color=INK))

    b, _, _ = textbox(W / 2, H - 34,
                      "Тепловий шум — стихія: його середньоквадратичне значення диктують температура й опір,\n"
                      "форма спектра фіксована, відняти його не можна. Шум квантування народжується з чіткої\n"
                      "операції округлення — тому ним КЕРУЮТЬ: дизером тримають білим, формуванням женуть із смуги.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, 'controllable.svg'), W, H, *p,
           title="Чому шумом квантування можна керувати, а тепловим — ні")


# ─────────────────────────────────────────────────────────────────────────────
#  ФІГУРИ ВСТАВКИ proj-requantize
# ─────────────────────────────────────────────────────────────────────────────

def requantize_ladder():
    """Чотири щаблі приборкання похибки перекодування слова (24→16 біт).
    Кожен щабель прибирає одну конкретну ваду попереднього:
      1) відсікання  → стале зміщення −q/2 + корельована пилка на тихому;
      2) округлення  → зміщення геть, але похибка ще корелює на тихому;
      3) TPDF-дизер  → похибка чесно біла, зникає модуляція шуму;
      4) формування  → шум виштовхнуто з низів у високі частоти.
    Показуємо це смужками похибки в часі + короткий вердикт під кожною."""
    W, H = 780, 520
    p = []

    p.append(text(W / 2, 26, "Перекодування 24→16 біт: чотири щаблі приборкання похибки",
                  size=16, bold=True))

    rows = [
        ("1. Відсікання (>> 8)", NEG,
         "стале зміщення −q/2 плюс пилка,\nприв'язана до тихого сигналу", "bias"),
        ("2. Округлення (+½q, потім >>)", FIELD,
         "зміщення прибрано; на тихому\nсигналі похибка ще корелює", "round"),
        ("3. TPDF-дизер (±1 LSB)", NEG,
         "похибка чесно біла, без гармонік\nі без модуляції шуму", "dither"),
        ("4. Формування шуму 1-го порядку", POS,
         "той самий шум, але зіпхнутий\nу високі частоти — низи чисті", "shape"),
    ]

    x0 = 60
    axw = 420
    row_h = 104
    top = 66
    random.seed(7)

    for i, (name, hue, note, kind) in enumerate(rows):
        cy = top + i * row_h + 34
        base = cy
        amp = 26
        # вісь часу
        p.append(line(x0, base, x0 + axw, base, color=MUTED, sw=1.2))
        p.append(text(x0 - 8, base + 4, "e", size=12, bold=True, anchor="end", color=hue))
        # смуга ±q/2 орієнтир
        p.append(line(x0, base - amp, x0 + axw, base - amp, color="#d9dde2", sw=1, dash="3 3"))
        p.append(line(x0, base + amp, x0 + axw, base + amp, color="#d9dde2", sw=1, dash="3 3"))
        # заголовок щабля
        p.append(text(x0, top + i * row_h + 6, name, size=12.5, bold=True, color=hue, anchor="start"))

        # крива похибки під кожен випадок
        pts = []
        k = 0
        while k <= axw:
            t = k / axw
            if kind == "bias":
                # стала −q/2 + повільна корельована хвиля (тихий сигнал повзе)
                yv = -0.75 * amp + 0.35 * amp * math.sin(t * 6.28 * 1.5)
            elif kind == "round":
                # без зміщення, але груба сходинкова кореляція
                yv = 0.55 * amp * (1 if math.sin(t * 6.28 * 2.0) > 0 else -1)
                yv += 0.12 * amp * math.sin(t * 6.28 * 2.0)
            elif kind == "dither":
                # чесно білий шум у ±q
                yv = (random.random() - 0.5) * 1.8 * amp
            else:  # shape — швидкі дрібні коливання (енергія в ВЧ), низи чисті
                yv = (random.random() - 0.5) * 0.5 * amp
                yv += 0.9 * amp * math.sin(t * 6.28 * 9.0) * (0.4 + 0.6 * random.random())
            pts.append((x0 + k, base - yv))
            k += 6 if kind in ("dither", "shape") else 9
        d = "M" + " L".join("%.1f %.1f" % (a, b) for a, b in pts)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.7"/>' % (d, hue))

        # рівень нуля пунктиром для щабля зі зміщенням
        if kind == "bias":
            p.append(line(x0, base, x0 + axw, base, color=POS, sw=1, dash="2 3"))
            p.append(text(x0 + axw + 6, base + 4, "0", size=10, color=POS, anchor="start"))
            p.append(text(x0 + axw + 6, base - 0.75 * amp + 4, "−q/2", size=10, bold=True,
                          color=NEG, anchor="start"))

        # вердикт праворуч
        b = fitbox(x0 + axw + 46, top + i * row_h + 2, 200, row_h - 22, note,
                   size=11, fill={NEG: "#eaf0fd", FIELD: "#eafaf0", POS: "#fdecea"}[hue],
                   stroke=hue, color=INK)
        p.append(b)

    bx, _, _ = textbox(W / 2, H - 26,
                       "Кожен щабель прибирає рівно одну ваду попереднього: округлення — зміщення,\n"
                       "дизер — кореляцію на тихому, формування — шум із корисної смуги. Модель\n"
                       "усюди та сама: q = x + e; ми лише міняємо, яким зробити e.",
                       size=12, fill="#eef7f0", stroke=FIELD)
    p.append(bx)

    render(os.path.join(OUT, 'requantize-ladder.svg'), W, H, *p,
           title=None)


def error_feedback():
    """Формувач шуму першого порядку в перекодувачі (error feedback).
    Ідея: округлюємо довге слово; РІЗНИЦЯ між входом округлення і виходом — це
    похибка округлення e; затримуємо її на один відлік (z⁻¹) і ДОДАЄМО назад до
    наступного відліку перед округленням. Так низькочастотна частина похибки
    гаситься сама себе, а шум спливає у високі частоти."""
    W, H = 760, 450
    p = []

    p.append(text(W / 2, 26, "Формувач шуму 1-го порядку: похибку округлення повертаємо в наступний відлік",
                  size=14.5, bold=True))

    yb = 150
    # вхід x[n] (довге слово)
    p.append(text(60, yb - 26, "x[n]", size=13, bold=True, color=NEG, anchor="start"))
    p.append(text(60, yb - 10, "довге слово", size=9.5, color=MUTED, anchor="start"))
    p.append(line(60, yb, 150, yb, color=NEG, sw=2))
    p.append(arrow(126, yb, 152, yb, color=NEG, sw=2))

    # суматор входу (x + затримана похибка)
    sx = 170
    p.append(circle(sx, yb, 17, fill=BG, stroke=INK, sw=2))
    p.append(text(sx, yb + 5, "+", size=18, bold=True))

    # квантувач (округлення до короткого слова)
    qx = 250
    p.append(line(sx + 17, yb, qx, yb, color=INK, sw=2))
    p.append(arrow(sx + 17, yb, qx + 2, yb, color=INK, sw=2))
    p.append(rect(qx, yb - 30, 118, 60, fill="#eef0f2", stroke=INK, sw=2))
    p.append(mtext(qx + 59, yb - 4, "округлення\n(+½q, >>)", size=11, bold=True, color=INK))
    p.append(text(qx + 59, yb + 20, "до короткого", size=9, color=MUTED))
    # позначимо вузол «u» = вхід округлення
    p.append(text(qx - 6, yb - 22, "u[n]", size=10, color=MUTED, anchor="end"))

    # вихід y[n] (коротке слово)
    ox = qx + 118
    p.append(line(ox, yb, ox + 120, yb, color=POS, sw=2))
    p.append(arrow(ox + 96, yb, ox + 122, yb, color=POS, sw=2))
    p.append(text(ox + 126, yb - 6, "y[n]", size=13, bold=True, color=POS, anchor="start"))
    p.append(text(ox + 126, yb + 10, "коротке слово", size=9.5, color=MUTED, anchor="start"))

    # відгалуження на вузол похибки: точка на виході
    tapx = ox + 60
    p.append(circle(tapx, yb, 3.2, fill=INK, stroke=INK, sw=1))

    # вузол похибки: e[n] = u[n] − y[n]  (віднімач)
    ey = yb + 120
    exq = qx + 59  # під квантувачем
    p.append(circle(exq, ey, 17, fill=BG, stroke=POS, sw=2))
    p.append(text(exq, ey + 5, "−", size=18, bold=True, color=POS))
    # вхід u в віднімач (з вузла перед округленням)
    p.append(line(qx - 6, yb, qx - 6, ey, color=MUTED, sw=1.5, dash="3 3"))
    p.append(line(qx - 6, ey, exq - 17, ey, color=MUTED, sw=1.5))
    p.append(arrow(qx - 6, ey, exq - 17 + 2, ey, color=MUTED, sw=1.5))
    p.append(text((qx - 6 + exq - 17) / 2, ey - 8, "u", size=10, color=MUTED))
    # вихід y у віднімач (з відгалуження)
    p.append(line(tapx, yb, tapx, ey, color=POS, sw=1.5))
    p.append(line(tapx, ey, exq + 17, ey, color=POS, sw=1.5))
    p.append(arrow(tapx, ey, exq + 17 - 2, ey, color=POS, sw=1.5))
    p.append(text((tapx + exq + 17) / 2, ey - 8, "y", size=10, color=POS))
    p.append(text(exq, ey + 34, "e[n] = u[n] − y[n]", size=11, bold=True, color=POS))
    p.append(text(exq, ey + 49, "похибка округлення", size=9.5, color=MUTED))

    # затримка z⁻¹ і повернення в суматор входу
    dx = sx
    p.append(line(exq - 17, ey, dx, ey, color=FIELD, sw=1.8))
    p.append(rect(dx - 34, ey - 18, 68, 36, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(dx, ey + 5, "z⁻¹", size=15, bold=True, color=FIELD))
    p.append(text(dx, ey - 26, "затримка на 1 відлік", size=9.5, color=FIELD))
    # вгору в суматор
    retx = dx - 58
    p.append(line(dx - 34, ey, retx, ey, color=FIELD, sw=1.8))
    p.append(line(retx, ey, retx, yb, color=FIELD, sw=1.8))
    p.append(line(retx, yb, sx - 17, yb, color=FIELD, sw=1.8))
    p.append(arrow(retx, yb, sx - 17 + 2, yb, color=FIELD, sw=1.8))
    p.append(text(retx + 6, (ey + yb) / 2, "+e[n−1]", size=10, bold=True, color=FIELD, anchor="start"))

    bx, _, _ = textbox(W / 2, H - 28,
                       "Округлили — і те, що зрізали (похибку округлення e), не викидаємо, а тримаємо й\n"
                       "додаємо до наступного відліку перед округленням. Різниця сусідніх похибок гасить\n"
                       "низькі частоти: шум спливає вгору, у смузі сигналу його майже не лишається.",
                       size=12, fill="#eef7f0", stroke=FIELD)
    p.append(bx)

    render(os.path.join(OUT, 'error-feedback.svg'), W, H, *p,
           title=None)


if __name__ == '__main__':
    additive_model()
    where_it_lives()
    controllable()
    requantize_ladder()
    error_feedback()
    print("OK: 5 figures ->", OUT)
