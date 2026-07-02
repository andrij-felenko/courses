# -*- coding: utf-8 -*-
"""Фігури до детальної статті «Де рахувати» (guide/embedded/drony/where-to-compute).
Чистий Python, без залежностей; svgkit — зі scripts/ (не переписувати)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Ланцюг затримки: датчик → обчислення → команда → виконавець (контур)
#    Показує, з чого складається «час реакції» і де тут місце обчислень.
# ─────────────────────────────────────────────────────────────────────────────
def fig_latency_chain():
    W, H = 940, 430
    frags = []
    frags.append(text(W / 2, 52, "Куди «в хмару» додає свою затримку", size=13, color=MUTED))

    # Замкнений контур: датчик -> обчислення -> команда -> апарат -> (назад) датчик
    cy = 150
    boxes = [
        ("Датчик", "гіроскоп,\nкамера", 120, FIELD),
        ("Обчислення", "де саме?", 340, POS),
        ("Команда", "новий газ,\nкут", 560, NEG),
        ("Апарат", "мотори,\nсерво", 780, INK),
    ]
    cxs = []
    for title_, sub, cx, col in boxes:
        b, w, h = textbox(cx, cy, title_, size=13, bold=True, pad=12, min_w=140,
                          stroke=col, fill="#f4f6f8")
        frags.append(b)
        frags.append(text(cx, cy + 30, sub.split("\n")[0], size=10, color=MUTED))
        if "\n" in sub:
            frags.append(text(cx, cy + 44, sub.split("\n")[1], size=10, color=MUTED))
        cxs.append((cx, w))
    for i in range(len(cxs) - 1):
        x1 = cxs[i][0] + cxs[i][1] / 2 + 4
        x2 = cxs[i + 1][0] - cxs[i + 1][1] / 2 - 4
        frags.append(arrow(x1, cy, x2, cy))
    # зворотна дуга апарат -> датчик (контур замкнено)
    frags.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" '
                 'fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5 4" '
                 'marker-end="url(#arrow)"/>' % (780, cy + 40, 780, 250, 120, 250, 120, cy + 40, MUTED))
    frags.append(text(450, 262, "світ змінюється → новий вимір", size=10, color=MUTED, italic=True))

    # Дві доріжки часу під контуром
    ly = 330
    b1, w1, h1 = textbox(300, ly, "На борту: датчик→обчислення→команда ≈ одиниці мс",
                         size=11, pad=10, stroke=FIELD, fill="#eafaf0")
    frags.append(b1)
    b2, w2, h2 = textbox(300, ly + 46, "додано на дорогу: + мережа туди-й-назад (десятки–сотні мс)",
                         size=11, pad=10, stroke=POS, fill="#fdecea")
    frags.append(b2)
    frags.append(text(W / 2, H - 14,
                      "Контур замикається щомиті. Винесеш обчислення «за море» — кожен виток тягне ще й дорогу туди й назад.",
                      size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, 'latency-chain.svg'), W, H, *frags,
           title="Із чого складається час реакції")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Дедлайн: м'який vs твердий. Корисність результату від часу приходу.
# ─────────────────────────────────────────────────────────────────────────────
def fig_deadline():
    W, H = 940, 430
    frags = []
    # дві панелі
    def panel(x0, title_, col, hard):
        gx0, gy0, gw, gh = x0 + 40, 90, 330, 220
        # осі
        frags.append(line(gx0, gy0, gx0, gy0 + gh, color=INK, sw=1.6))
        frags.append(line(gx0, gy0 + gh, gx0 + gw, gy0 + gh, color=INK, sw=1.6))
        frags.append(text(gx0 - 8, gy0 + 6, "користь", size=10, color=MUTED, anchor="end"))
        frags.append(text(gx0 + gw, gy0 + gh + 18, "час приходу →", size=10, color=MUTED, anchor="end"))
        # дедлайн
        dx = gx0 + gw * 0.55
        frags.append(line(dx, gy0, dx, gy0 + gh, color=NEG, sw=1.4, dash="5 4"))
        frags.append(text(dx, gy0 - 8, "дедлайн", size=10, color=NEG))
        top = gy0 + 22
        if hard:
            # повна користь до дедлайну, потім різкий обрив у мінус (гірше нуля)
            frags.append(line(gx0, top, dx, top, color=col, sw=3))
            frags.append(line(dx, top, dx, gy0 + gh + 34, color=col, sw=3))
            frags.append(line(dx, gy0 + gh + 34, gx0 + gw, gy0 + gh + 34, color=col, sw=3))
            frags.append(text(gx0 + gw * 0.78, gy0 + gh + 50, "шкода", size=10, color=col, bold=True))
        else:
            # повна користь, далі плавно спадає до нуля
            frags.append(line(gx0, top, dx, top, color=col, sw=3))
            frags.append('<path d="M %.0f %.0f Q %.0f %.0f, %.0f %.0f" fill="none" '
                         'stroke="%s" stroke-width="3"/>' % (dx, top, dx + 60, top,
                         gx0 + gw, gy0 + gh - 6, col))
            frags.append(text(gx0 + gw * 0.82, gy0 + gh - 22, "ще корисно", size=10, color=col, bold=True))
        b, _, _ = textbox(gx0 + gw / 2, gy0 - 40, title_, size=13, bold=True, pad=8,
                          stroke=col, fill="#f4f6f8")
        frags.append(b)

    panel(0, "М'який дедлайн", FIELD, hard=False)
    panel(470, "Твердий дедлайн", POS, hard=True)

    frags.append(text(240, H - 40, "Спізнився — результат просто менш корисний.", size=11, color=INK))
    frags.append(text(710, H - 40, "Спізнився — результат уже шкідливий.", size=11, color=INK))
    frags.append(text(W / 2, H - 14,
                      "Контур керування має твердий дедлайн: пізня команда гірша за жодну. Мережа таких дедлайнів не гарантує.",
                      size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, 'deadline-soft-hard.svg'), W, H, *frags,
           title="М'який і твердий дедлайн")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Три поверхи одного апарата: що на якому рівні й хто з ким говорить.
# ─────────────────────────────────────────────────────────────────────────────
def fig_stack():
    W, H = 940, 470
    frags = []
    frags.append(text(W / 2, 52, "Розподіл задач по трьох поверхах гібридного апарата", size=13, color=MUTED))

    # три горизонтальні смуги
    rows = [
        (80, FIELD, "ПОЛІТНИЙ КОНТРОЛЕР (МК)", "твердий real-time · без мережі",
         ["стабілізація, PID-контур 1–8 кГц", "змішування виходів, безпечний режим",
          "завжди-ввімкнений TinyML (слово, жест)"]),
        (200, "#d98a00", "БОРТОВИЙ КОМП'ЮТЕР", "м'який real-time · на борту",
         ["детектор і трекінг у реальному часі", "SLAM, обхід перешкод, планування",
          "віддає кут/ціль по MAVLink униз"]),
        (320, NEG, "ХМАРА / ЗЕМЛЯ", "поза контуром · лише коли є зв'язок",
         ["навчання й перенавчання моделей", "важкий аналіз логів і відео",
          "побудова карт, звіти, зберігання"]),
    ]
    for y0, col, title_, tag, items in rows:
        frags.append(rect(60, y0, 820, 100, fill="#f7f8fa", stroke=col, sw=2, rx=10))
        frags.append(rect(60, y0, 300, 100, fill="#f4f6f8", stroke=col, sw=0, rx=10))
        frags.append(text(210, y0 + 40, title_, size=12.5, color=col, bold=True))
        frags.append(text(210, y0 + 62, tag, size=10, color=MUTED, italic=True))
        for i, it in enumerate(items):
            frags.append(text(390, y0 + 30 + i * 24, "• " + it, size=11, color=INK, anchor="start"))

    # стрілки між поверхами
    frags.append(arrow(300, 300, 300, 240, color=INK))
    frags.append(text(315, 272, "кут по MAVLink", size=10, color=INK, anchor="start"))
    frags.append('<path d="M 700 300 C 700 440, 470 440, 470 420" fill="none" '
                 'stroke="%s" stroke-width="1.8" stroke-dasharray="6 4" '
                 'marker-end="url(#arrow)"/>' % NEG)
    # межа польотного контуру
    frags.append(rect(50, 68, 840, 244, fill="none", stroke=FIELD, sw=1.4, rx=14))
    b, _, _ = textbox(760, 82, "ПОЛІТНИЙ КОНТУР", size=10, bold=True, pad=6,
                      stroke=FIELD, fill="#eafaf0", color=FIELD)
    frags.append(b)
    frags.append(text(W / 2, H - 16,
                      "Усе, від чого залежить політ, — усередині контуру, на борту. Хмара стоїть зовні: пропаде — апарат літає далі.",
                      size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, 'compute-stack.svg'), W, H, *frags,
           title="Три поверхи обчислень")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Бюджет часу польоту: додав ват — забрав хвилини. Крива для двох ємностей.
# ─────────────────────────────────────────────────────────────────────────────
def fig_flight_budget():
    W, H = 940, 430
    frags = []
    gx0, gy0, gw, gh = 90, 90, 760, 250
    frags.append(line(gx0, gy0, gx0, gy0 + gh, color=INK, sw=1.6))
    frags.append(line(gx0, gy0 + gh, gx0 + gw, gy0 + gh, color=INK, sw=1.6))
    frags.append(text(gx0 - 10, gy0 - 4, "час", size=11, color=MUTED, anchor="end"))
    frags.append(text(gx0 - 10, gy0 + 10, "польоту", size=11, color=MUTED, anchor="end"))
    frags.append(text(gx0 + gw, gy0 + gh + 22, "додана потужність борту (Вт) →", size=11, color=MUTED, anchor="end"))

    # t = E / (P_base + P_extra); малюємо як спад від додаткового споживання
    import math
    E = 100.0            # умовна енергія
    Pbase = 100.0        # базове споживання (мотори тощо)
    def t_of(px):
        return E / (Pbase + px)
    xmax = 60.0
    t0 = t_of(0)
    def X(px):
        return gx0 + gw * (px / xmax)
    def Y(t):
        return gy0 + gh - (t / t0) * (gh - 20)
    pts = []
    px = 0.0
    while px <= xmax + 0.01:
        pts.append("%.1f,%.1f" % (X(px), Y(t_of(px))))
        px += 1.0
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                 % (" ".join(pts), POS))

    # маркери: 0 Вт, 10 Вт (RPi-клас), 25 Вт (Jetson повний)
    for px, lab, col in [(0, "0 Вт", INK), (10, "+10 Вт\n(RPi-клас)", NEG), (25, "+25 Вт\n(Jetson повний)", POS)]:
        frags.append(circle(X(px), Y(t_of(px)), 5, fill=col, stroke=col))
        drop = int(round((1 - t_of(px) / t0) * 100))
        lines = lab.split("\n")
        yy = Y(t_of(px)) - 16
        for i, ln in enumerate(lines):
            frags.append(text(X(px) + 6, yy + i * 13, ln, size=10, color=col, anchor="start"))
        if px > 0:
            frags.append(text(X(px) + 6, Y(t_of(px)) + 22, "−%d%%" % drop, size=10, color=col, anchor="start", bold=True))

    frags.append(text(W / 2, H - 14,
                      "Час польоту ≈ енергія ÷ повна потужність. Кожен доданий ват борту вкорочує політ — тим сильніше, чим менший апарат.",
                      size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, 'flight-time-budget.svg'), W, H, *frags,
           title="Ват на борту коштує хвилин у повітрі")


if __name__ == '__main__':
    fig_latency_chain()
    fig_deadline()
    fig_stack()
    fig_flight_budget()
    print("done: 4 figures")
