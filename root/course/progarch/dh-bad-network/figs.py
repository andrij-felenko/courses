# -*- coding: utf-8 -*-
"""Фігури до кроку «Хаб на поганому Wi-Fi»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GRAY_FILL = "#f0f0f2"
RED_FILL = "#fdecea"
GREEN_FILL = "#eafaf0"
BLUE_FILL = "#dfe9fb"
TAIL_FILL = "#f0f1f3"


def _node(cx, cy, label, active=True, min_w=130):
    if active:
        return textbox(cx, cy, label, size=13, bold=True, fill=FILL, stroke=INK,
                       sw=1.6, min_w=min_w)
    return textbox(cx, cy, label, size=13, bold=False, fill=GRAY_FILL, stroke=MUTED,
                   sw=1.4, color=MUTED, min_w=min_w)


def fig_partial_failure():
    """Дві долі однієї команди — втрачений запит і втрачений ack — з однаковим виглядом."""
    W, H = 1160, 560
    frags = []

    PX, CX, HX, LX = 120, 340, 590, 810
    TOPY, BOTY = 180, 385

    # ── СВІТ 1: запит загубився ──
    frags.append(text(355, 118, "СВІТ 1 — запит загубився дорогою туди",
                      size=15, bold=True, color=INK))
    ph1, wp, _ = _node(PX, TOPY, "Телефон")
    cl1, wc, _ = _node(CX, TOPY, "Хмара")
    hb1, wh, _ = _node(HX, TOPY, "Хаб", active=False)
    lk1, wl, _ = _node(LX, TOPY, "Замок", active=False)
    frags.append(arrow(PX + wp / 2 + 6, TOPY, CX - wc / 2 - 6, TOPY, color=INK, sw=1.8))
    # хмара → хаб: гине
    frags.append(arrow(CX + wc / 2 + 6, TOPY, 458, TOPY, color=POS, sw=1.9))
    frags.append(text(470, TOPY + 6, "✗", size=20, bold=True, color=POS))
    frags.append(text(470, TOPY + 26, "не долетів", size=11, color=MUTED))
    frags.append(text(LX, TOPY + 34, "замок не ворухнувся", size=12, bold=True, color=MUTED))
    for f in (ph1, cl1, hb1, lk1):
        frags.append(f)

    # ── СВІТ 2: відповідь загубилась ──
    frags.append(text(355, 322, "СВІТ 2 — відповідь загубилась на звороті",
                      size=15, bold=True, color=INK))
    ph2, _, _ = _node(PX, BOTY, "Телефон")
    cl2, _, _ = _node(CX, BOTY, "Хмара")
    hb2, _, _ = _node(HX, BOTY, "Хаб")
    lk2, _, _ = _node(LX, BOTY, "Замок")
    frags.append(arrow(PX + wp / 2 + 6, BOTY, CX - wc / 2 - 6, BOTY, color=INK, sw=1.8))
    frags.append(arrow(CX + wc / 2 + 6, BOTY, HX - wh / 2 - 6, BOTY, color=INK, sw=1.8))
    frags.append(arrow(HX + wh / 2 + 6, BOTY, LX - wl / 2 - 6, BOTY, color=INK, sw=1.8))
    frags.append(text(LX, BOTY + 34, "зачинився ✓", size=12, bold=True, color=FIELD))
    # зворотний ack гине між хабом і хмарою
    frags.append(arrow(HX - wh / 2 - 6, BOTY + 46, CX + wc / 2 + 6, BOTY + 46,
                       color=POS, sw=1.7))
    frags.append(text(490, BOTY + 40, "✗", size=20, bold=True, color=POS))
    frags.append(text(490, BOTY + 66, "підтвердження загубилось", size=11, color=MUTED))
    for f in (ph2, cl2, hb2, lk2):
        frags.append(f)

    # ── права винесена думка ──
    frags.append(line(905, TOPY, 940, 283, color=MUTED, sw=1.3))
    frags.append(line(905, BOTY, 940, 283, color=MUTED, sw=1.3))
    cb, cw, _ = textbox(1035, 283, "Відправник бачить\nтаймаут — в ОБОХ.\nЗачинено? Невідомо.",
                        size=13, bold=True, fill="#fff8e6", stroke=POS, sw=1.8, min_w=200)
    frags.append(cb)

    render(os.path.join(IMG, "partial-failure.svg"), W, H, *frags,
           title="Одна тиша — два різні світи")


def fig_retry_dedup():
    """Повтор без ключа (подвійна дія) і з ключем (упізнаний дубль, одне виконання)."""
    W, H = 1160, 620
    frags = []

    CLX, HBX, OUTX = 185, 615, 980
    CLW, HBW, OUTW = 320, 356, 220

    def lane(y1, y2, outcy, client1, hub1, client2, hub2, ack_row1,
             out_label, out_fill, out_stroke, out_color, hub2_color):
        # спроба 1
        c1, _, _ = textbox(CLX, y1, client1, size=12, fill=FILL, stroke=INK, sw=1.4, min_w=CLW)
        h1, _, _ = textbox(HBX, y1, hub1, size=12, fill=FILL, stroke=INK, sw=1.5, min_w=HBW)
        frags.append(arrow(CLX + CLW / 2 + 6, y1, HBX - HBW / 2 - 6, y1, color=INK, sw=1.7))
        frags.append(c1)
        frags.append(h1)
        if ack_row1:
            frags.append(text(HBX + HBW / 2 + 34, y1 - 3, "✗", size=19, bold=True, color=POS))
            frags.append(text(HBX + HBW / 2 + 34, y1 + 17, "ack ✗", size=11, color=MUTED))
        # спроба 2 (повтор)
        c2, _, _ = textbox(CLX, y2, client2, size=12, fill=FILL, stroke=INK, sw=1.4, min_w=CLW)
        h2, _, _ = textbox(HBX, y2, hub2, size=12, fill=BG, stroke=out_stroke, sw=1.6,
                           color=hub2_color, bold=True, min_w=HBW)
        frags.append(arrow(CLX + CLW / 2 + 6, y2, HBX - HBW / 2 - 6, y2, color=INK, sw=1.7))
        frags.append(c2)
        frags.append(h2)
        # підсумок доріжки
        ob, obw, _ = textbox(OUTX, outcy, out_label, size=13, bold=True, fill=out_fill,
                             stroke=out_stroke, color=out_color, sw=2, min_w=OUTW)
        frags.append(arrow(HBX + HBW / 2 + 6, y2, OUTX - OUTW / 2 - 6, outcy, color=out_stroke, sw=1.7))
        frags.append(ob)

    # ── доріжка 1: без ключа ──
    frags.append(text(360, 74, "БЕЗ ключа — хаб не відрізнить дубль від нової команди",
                      size=15, bold=True, color=POS))
    lane(124, 214, 168,
         "спроба 1\nвідчинити", "виконує → відчинив",
         "спроба 2 (повтор)\nвідчинити", "виконує ЗНОВУ", True,
         "двері відчинялись\nДВІЧІ", RED_FILL, POS, POS, POS)

    frags.append(line(60, 300, 1100, 300, color=MUTED, sw=1, dash="6,6"))

    # ── доріжка 2: з ключем ──
    frags.append(text(360, 356, "З ключем key=7f3 — повтор упізнано, виконання одне",
                      size=15, bold=True, color=FIELD))
    lane(406, 496, 450,
         "спроба 1\nвідчинити  key=7f3", "виконує +\nзапамʼятав 7f3",
         "спроба 2 (повтор)\nвідчинити  key=7f3", "ключ 7f3 знайомий →\nвіддає збережене,\nНЕ виконує", True,
         "одне\nвідчинення", GREEN_FILL, FIELD, FIELD, FIELD)

    frags.append(text(W / 2, 596,
                      "Той самий загублений ack, той самий повтор — різниця лише в ключі команди.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "retry-dedup.svg"), W, H, *frags,
           title="Повтор без ключа і з ключем")


def fig_time_budget():
    """Вкладений бюджет часу: дедлайн скорочується всередину, кожен шар лишає запас."""
    W, H = 1000, 470
    frags = []
    x0 = 70
    scale = 84.0  # px за секунду

    rows = [
        (100, 10.0, None, "Телефон: чекає 10 с", None),
        (172, 8.0, 10.0, "Хмара дає хабові 8 с", "+2 с собі на відповідь"),
        (244, 5.0, 8.0, "Хаб дає замкові 5 с", "+3 с на повтор і відповідь"),
        (316, 2.0, 5.0, "Замок: ~2 с", "запас на ще одну спробу"),
    ]
    bh = 50
    for y, secs, outer, label, tail in rows:
        w = secs * scale
        # запас (світлий, штрихований) — праворуч від суцільної частини до межі зовнішнього
        if outer is not None:
            ow = outer * scale
            frags.append(rect(x0 + w, y, ow - w, bh, fill=TAIL_FILL, stroke=MUTED,
                              sw=1.3, rx=6))
            frags.append(text(x0 + w + (ow - w) / 2, y + bh / 2 + 4, tail,
                              size=11, color=MUTED))
        # суцільна частина — те, що шар віддає всередину
        frags.append(fitbox(x0, y, w, bh, label, size=13, bold=True,
                            fill=BLUE_FILL, stroke=NEG, color=INK))

    # стрілка «усередину» ліворуч
    frags.append(arrow(45, 108, 45, 350, color=MUTED, sw=1.8))
    frags.append(text(30, 232, "глибше", size=11, color=MUTED, anchor="middle"))

    frags.append(text(W / 2, 408,
                      "Дедлайн не сталий — він тоншає всередину: кожен шар віддає нижчому менше, ніж має, лишаючи запас на власну відповідь і повтор.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "time-budget.svg"), W, H, *frags,
           title="Бюджет часу скорочується всередину")


def _down(cx, y_from, y_to, color=INK):
    return arrow(cx, y_from, cx, y_to, color=color, sw=1.7)


def fig_dup_race():
    """Дві доріжки: наївний get→put виконує двічі; reserve/замок на ключ — раз."""
    W, H = 1160, 690
    frags = []

    xL, xR = 305, 835
    minL, minR = 410, 430
    ys = [156, 246, 336, 426]
    outy = 548

    frags.append(line(575, 100, 575, 620, color=MUTED, sw=1.2, dash="7,7"))

    # ── ліва колонка: НАЇВНО ──
    frags.append(text(xL, 84, "НАЇВНО — get, тоді put: між ними діра",
                      size=15, bold=True, color=POS))
    left = [
        ("① R1: get(7f3) → порожньо", INK, FILL),
        ("② R2: get(7f3) → теж порожньо\n(put від R1 ще не настав)", INK, FILL),
        ("③ R1: execute ▶  замок крутиться", POS, RED_FILL),
        ("④ R2: execute ▶  замок крутиться ЗНОВУ", POS, RED_FILL),
    ]
    for (lbl, col, fl), y in zip(left, ys):
        stroke = POS if fl == RED_FILL else INK
        b, _, _ = textbox(xL, y, lbl, size=12.5, bold=(col == POS), fill=fl,
                          stroke=stroke, sw=1.5, color=col, min_w=minL)
        frags.append(b)
    for a, b in zip(ys, ys[1:]):
        frags.append(_down(xL, a + 30, b - 30))
    frags.append(_down(xL, ys[-1] + 30, outy - 26, color=POS))
    ob, _, _ = textbox(xL, outy, "двері відчинились ДВІЧІ", size=14, bold=True,
                       fill=RED_FILL, stroke=POS, sw=2, color=POS, min_w=minL)
    frags.append(ob)

    # ── права колонка: ЗАМОК НА КЛЮЧ ──
    frags.append(text(xR, 84, "ЗАМОК НА КЛЮЧ — reserve, тоді execute",
                      size=15, bold=True, color=FIELD))
    right = [
        ("① R1: reserve(7f3) → виграв", INK, FILL),
        ("② R2: reserve(7f3) → зайнято, чекаю", NEG, BLUE_FILL),
        ("③ R1: execute ▶ → зберіг 7f3", FIELD, GREEN_FILL),
        ("④ R2: ← той самий результат\n(не виконує)", FIELD, GREEN_FILL),
    ]
    strokes = [INK, NEG, FIELD, FIELD]
    for (lbl, col, fl), y, st in zip(right, ys, strokes):
        b, _, _ = textbox(xR, y, lbl, size=12.5, bold=(fl != FILL), fill=fl,
                          stroke=st, sw=1.5, color=col, min_w=minR)
        frags.append(b)
    for a, b in zip(ys, ys[1:]):
        frags.append(_down(xR, a + 30, b - 30))
    frags.append(_down(xR, ys[-1] + 30, outy - 26, color=FIELD))
    ob2, _, _ = textbox(xR, outy, "виконання ОДНЕ", size=14, bold=True,
                        fill=GREEN_FILL, stroke=FIELD, sw=2, color=FIELD, min_w=minR)
    frags.append(ob2)

    frags.append(text(W / 2, 648,
                      "Гонка живе в проміжку між «прочитав» і «записав» — навіть в одному потоці, бо execute — це await, на якому вклинюється конкурент.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "dup-race.svg"), W, H, *frags,
           title="Гонка двох повторів на одному ключі")


def fig_ttl_window():
    """TTL ключа мусить накрити все вікно, у якому ще можуть прилітати дублі."""
    W, H = 1080, 500
    frags = []
    axy = 410
    x0, xdup, xA, xB, xmarg = 150, 640, 410, 700, 620

    # вісь часу
    frags.append(arrow(x0, axy, 1010, axy, color=MUTED, sw=1.8))
    frags.append(text(560, axy + 34, "час від створення команди →", size=12, color=MUTED))
    frags.append(line(x0, 150, x0, axy, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(x0, 138, "команда створена · ключ 7f3", size=11.5, bold=True, color=INK))

    # дужка «вікно дублів»
    frags.append(line(x0, 176, xdup, 176, color=NEG, sw=1.6))
    frags.append(line(x0, 176, x0, 186, color=NEG, sw=1.6))
    frags.append(line(xdup, 176, xdup, 186, color=NEG, sw=1.6))
    frags.append(text((x0 + xdup) / 2, 168, "коли ще можуть прилітати дублі",
                      size=12.5, bold=True, color=NEG))

    # смуга A — закороткий TTL
    frags.append(rect(x0, 210, xA - x0, 44, fill=RED_FILL, stroke=POS, sw=1.6))
    frags.append(text((x0 + xA) / 2, 236, "TTL закороткий", size=12.5, bold=True, color=POS))
    frags.append(rect(xA, 210, xdup - xA, 44, fill="#fbeceb", stroke=POS, sw=1, rx=6))
    frags.append(text((xA + xdup) / 2, 236, "ключ уже забутий", size=11.5, italic=True, color=POS))

    # смуга B — достатній TTL
    frags.append(rect(x0, 286, xmarg - x0, 44, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    frags.append(text((x0 + xmarg) / 2, 312, "TTL ≥ вікно дублів", size=12.5, bold=True, color=FIELD))
    frags.append(rect(xmarg, 286, xB - xmarg, 44, fill="#f0f7f2", stroke=FIELD, sw=1, rx=6))
    frags.append(text((xmarg + xB) / 2, 312, "запас", size=11, italic=True, color=FIELD))

    # пізній дубль — вертикаль, з підсумком праворуч від усіх смуг
    xlate = 512
    frags.append(line(xlate, 196, xlate, axy, color=INK, sw=1.5, dash="5,5"))
    frags.append(text(xlate, 190, "пізній повтор", size=11.5, bold=True, color=INK))
    frags.append(text(866, 232, "✗ TTL A забув → ВИКОНАЄ ЗНОВУ", size=11.5, bold=True, color=POS))
    frags.append(text(858, 308, "✓ TTL B памʼятає → упізнано", size=11.5, bold=True, color=FIELD))

    frags.append(text(W / 2, 468,
                      "Коротший за вікно дублів TTL воскрешає той самий баг: пізній повтор не впізнають і виконають удруге.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "ttl-window.svg"), W, H, *frags,
           title="TTL ключа проти вікна дублів")


def fig_two_generals_ladder():
    """Драбина підтверджень: кожен ack — один поверх «я знаю, що ти знаєш», верху нема."""
    W, H = 940, 650
    frags = []
    AX, BX = 180, 760

    hb1, _, _ = textbox(AX, 74, "Генерал А\n(лівий пагорб)", size=13, bold=True, min_w=156)
    hb2, _, _ = textbox(BX, 74, "Генерал Б\n(правий пагорб)", size=13, bold=True, min_w=156)

    # життєві лінії
    frags.append(line(AX, 110, AX, 468, color=MUTED, sw=1.3, dash="4,5"))
    frags.append(line(BX, 110, BX, 468, color=MUTED, sw=1.3, dash="4,5"))

    Lx, Rx = AX + 34, BX - 34
    msgs = [
        (168, "AB", "«нападаємо на світанку»", INK, True),
        (253, "BA", "«згоден» — 1-ше підтвердження", NEG, False),
        (338, "AB", "«отримав твоє „згоден“» — 2-ге", NEG, False),
        (423, "BA", "«отримав твоє „отримав“» — 3-тє", NEG, False),
    ]
    for y, dirn, label, col, bold in msgs:
        frags.append(text(470, y - 13, label, size=13, color=col, bold=bold))
        if dirn == "AB":
            frags.append(arrow(Lx, y, Rx, y, color=col, sw=1.9))
        else:
            frags.append(arrow(Rx, y, Lx, y, color=col, sw=1.9))

    frags.append(text(470, 502, "⋮   і так без кінця", size=15, bold=True, color=MUTED))

    note, _, _ = textbox(
        470, 585,
        "Хто відправив ОСТАННЄ повідомлення — не знає, чи воно дійшло.\n"
        "Тож рівно один із двох завжди лишається без повної певності.\n"
        "Скільки підтверджень не додавай — драбина не закривається.",
        size=13, bold=True, fill="#fff8e6", stroke=POS, sw=1.8, min_w=690)

    frags += [hb1, hb2, note]
    render(os.path.join(IMG, "two-generals-ladder.svg"), W, H, *frags,
           title="Драбина підтверджень, що не має верху")


def _proto(cx, cy, k, w=160, h=160, red=False):
    """Протокол як стосик k повідомлень-стрілок у рамці (k=0 → порожня, червона)."""
    out = rect(cx - w / 2, cy - h / 2, w, h,
               fill=(RED_FILL if red else FILL),
               stroke=(POS if red else INK), sw=1.7)
    if k == 0:
        out += text(cx, cy + 10, "∅", size=30, bold=True, color=POS)
        return out
    for i in range(k):
        yy = cy + (i - (k - 1) / 2.0) * 26
        if i % 2 == 0:
            out += arrow(cx - 52, yy, cx + 52, yy, color=INK, sw=1.7)
        else:
            out += arrow(cx + 52, yy, cx - 52, yy, color=NEG, sw=1.7)
    return out


def fig_two_generals_induction():
    """Зривання «зайвого» останнього повідомлення: n → n−1 → … → 0 → суперечність."""
    W, H = 1090, 390
    frags = []
    cy = 188
    xs = [140, 430, 720, 980]   # центри чотирьох протоколів
    hw = 80                       # пів-ширини рамки

    frags.append(_proto(xs[0], cy, 4))
    frags.append(_proto(xs[1], cy, 3))
    frags.append(_proto(xs[2], cy, 1))
    frags.append(_proto(xs[3], cy, 0, red=True))

    labels = ["n повідомлень", "n − 1", "1", "0 повідомлень —\nузгодити неможливо"]
    for x, lab in zip(xs, labels):
        red = lab.startswith("0")
        frags.append(mtext(x, cy + hw + 24, lab, size=13, bold=True,
                           color=(POS if red else INK)))

    # перехід 1: прибрати останнє
    m1 = (xs[0] + hw + xs[1] - hw) / 2
    frags.append(arrow(xs[0] + hw + 8, cy, xs[1] - hw - 8, cy, color=MUTED, sw=1.8))
    frags.append(text(m1, cy - 20, "прибрати останнє", size=12, color=MUTED))
    frags.append(text(m1, cy + 32, "(не певен, чи дійшло)", size=11, color=MUTED, italic=True))

    # перехід 2: повторюємо
    m2 = (xs[1] + hw + xs[2] - hw) / 2
    frags.append(text(m2, cy - 20, "повторюємо", size=12, color=MUTED))
    frags.append(text(m2, cy + 10, "⋯", size=26, bold=True, color=MUTED))

    # перехід 3: прибрати останнє
    frags.append(arrow(xs[2] + hw + 8, cy, xs[3] - hw - 8, cy, color=MUTED, sw=1.8))
    frags.append(mtext((xs[2] + hw + xs[3] - hw) / 2, cy - 26, "прибрати\nостаннє",
                       size=12, color=MUTED))

    frags.append(text(W / 2, 360,
                      "Останнє повідомлення завжди зайве — його відправник не певен, що воно дійшло. Зривай його раз за разом — і скінченний протокол тане до нуля.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "two-generals-induction.svg"), W, H, *frags,
           title="Доведення: останнє повідомлення завжди можна зірвати")


if __name__ == "__main__":
    fig_partial_failure()
    fig_retry_dedup()
    fig_time_budget()
    fig_dup_race()
    fig_ttl_window()
    fig_two_generals_ladder()
    fig_two_generals_induction()
    print("OK: partial-failure, retry-dedup, time-budget, dup-race, ttl-window, "
          "two-generals-ladder, two-generals-induction")
