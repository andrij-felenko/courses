# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def box_at(cx, cy, s, **kw):
    """textbox at center, returns (svg, half_w, half_h)."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, w / 2, h / 2


# ── Фігура 1: CQS на рівні методу проти CQRS на рівні моделі ─────────────────
def cqs_vs_cqrs():
    W, H = 960, 520
    parts = []
    parts.append(text(W / 2, 32, "Той самий поділ, різний масштаб", size=18, bold=True))

    parts.append(line(W / 2, 62, W / 2, H - 24, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 4, 60, "CQS · рівень методу", size=13, bold=True, color=MUTED))
    parts.append(text(W * 3 / 4, 60, "CQRS · рівень моделі", size=13, bold=True, color=FIELD))

    # ---- ліва: один об'єкт, два методи ----
    lx = W / 4
    obj, ohw, ohh = box_at(lx, 130, "один об'єкт Account", size=13, bold=True,
                           fill=FILL, stroke=INK, min_w=260)
    parts.append(obj)

    cmd, chw, chh = box_at(lx - 90, 250, ["команда", "withdraw()", "міняє стан"],
                           size=12, fill="#fdecea", stroke=POS, min_w=150)
    parts.append(cmd)
    qry, qhw, qhh = box_at(lx + 90, 250, ["запит", "balance()", "повертає стан"],
                           size=12, fill="#eaf0fd", stroke=NEG, min_w=150)
    parts.append(qry)
    parts.append(arrow(lx - 40, 130 + ohh, lx - 90, 250 - chh, color=INK, sw=1.6))
    parts.append(arrow(lx + 40, 130 + ohh, lx + 90, 250 - qhh, color=INK, sw=1.6))

    parts.append(text(lx, 360, "правило: метод — або одне, або друге,",
                      size=12, italic=True, color=MUTED))
    parts.append(text(lx, 380, "але не обидва разом",
                      size=12, italic=True, color=MUTED))
    parts.append(text(lx, 430, "спільні дані, спільний тип —",
                      size=12, color=INK))
    parts.append(text(lx, 450, "розділені лише виклики",
                      size=12, color=INK))

    # ---- права: дві окремі моделі ----
    rx = W * 3 / 4
    reqc, rcw, rch = box_at(rx - 100, 128, ["команди", "PlaceOrder", "Cancel"],
                            size=12, bold=True, fill="#fdecea", stroke=POS, min_w=170)
    parts.append(reqc)
    reqq, rqw, rqh = box_at(rx + 100, 128, ["запити", "OrderView", "OrderList"],
                            size=12, bold=True, fill="#eaf0fd", stroke=NEG, min_w=170)
    parts.append(reqq)

    wm, wmw, wmh = box_at(rx - 100, 275, ["МОДЕЛЬ ЗАПИСУ", "агрегати,", "правила, інваріанти"],
                          size=12, fill=FILL, stroke=POS, min_w=200)
    parts.append(wm)
    rm, rmw, rmh = box_at(rx + 100, 275, ["МОДЕЛЬ ЧИТАННЯ", "плоскі знімки", "під екрани"],
                          size=12, fill=FILL, stroke=NEG, min_w=200)
    parts.append(rm)

    parts.append(arrow(rx - 100, 128 + rch, rx - 100, 275 - wmh, color=POS, sw=1.8))
    parts.append(arrow(rx + 100, 128 + rqh, rx + 100, 275 - rmh, color=NEG, sw=1.8))

    parts.append(text(rx, 375, "дві окремі моделі — свій тип,",
                      size=12, italic=True, color=FIELD))
    parts.append(text(rx, 395, "своя схема, свій шлях у код",
                      size=12, italic=True, color=FIELD))
    parts.append(text(rx, 445, "поділ піднявся з методу",
                      size=12, bold=True, color=FIELD))
    parts.append(text(rx, 465, "до цілої форми застосунку",
                      size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "cqs-vs-cqrs.svg"), W, H, *parts)


# ── Фігура 2: дві доріжки, одна система, з розривом узгодженості ─────────────
def two_paths():
    W, H = 1000, 560
    parts = []
    parts.append(text(W / 2, 32, "Дві доріжки крізь одну систему", size=18, bold=True))

    # клієнт зверху посередині
    cli, clw, clh = box_at(W / 2, 92, "клієнт", size=13, bold=True, min_w=140)
    parts.append(cli)

    # ── ліва доріжка: запис ──
    wx = 220
    parts.append(text(wx, 150, "ЗАПИС (команди)", size=13, bold=True, color=POS))
    cmd, cmw, cmh = box_at(wx, 205, ["команда", "PlaceOrder"],
                           size=12, fill="#fdecea", stroke=POS, min_w=190)
    parts.append(cmd)
    dom, dmw, dmh = box_at(wx, 320, ["модель запису", "агрегат · інваріанти"],
                           size=12, bold=True, fill=FILL, stroke=POS, min_w=250)
    parts.append(dom)
    wst, wsw, wsh = box_at(wx, 440, ["сховище запису", "нормалізоване"],
                           size=12, fill=FILL, stroke=INK, min_w=230)
    parts.append(wst)
    parts.append(arrow(W / 2 - 70, 92 + 4, wx + 20, 205 - cmh, color=POS, sw=1.6))
    parts.append(arrow(wx, 205 + cmh, wx, 320 - dmh, color=POS, sw=1.8))
    parts.append(arrow(wx, 320 + dmh, wx, 440 - wsh, color=POS, sw=1.8))

    # ── права доріжка: читання ──
    qx = 780
    parts.append(text(qx, 150, "ЧИТАННЯ (запити)", size=13, bold=True, color=NEG))
    qry, qrw, qrh = box_at(qx, 205, ["запит", "OrderView"],
                           size=12, fill="#eaf0fd", stroke=NEG, min_w=190)
    parts.append(qry)
    rmo, rmw, rmh = box_at(qx, 320, ["модель читання", "плоскі знімки"],
                           size=12, bold=True, fill=FILL, stroke=NEG, min_w=250)
    parts.append(rmo)
    rst, rsw, rsh = box_at(qx, 440, ["сховище читання", "денормалізоване"],
                           size=12, fill=FILL, stroke=INK, min_w=230)
    parts.append(rst)
    parts.append(arrow(W / 2 + 70, 92 + 4, qx - 20, 205 - qrh, color=NEG, sw=1.6))
    # читання йде ЗНИЗУ ВГОРУ: зі сховища в модель, з моделі — відповідь
    parts.append(arrow(qx, 440 - rsh, qx, 320 + rmh, color=NEG, sw=1.8))
    parts.append(arrow(qx, 320 - rmh, qx, 205 + qrh, color=NEG, sw=1.8))

    # ── міст: проєкція переливає зміни зі сховища запису у сховище читання ──
    proj, pjw, pjh = box_at(W / 2, 440, ["проєкція", "оновлює знімки"],
                            size=12, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=190)
    parts.append(proj)
    parts.append(arrow(wx + wsw, 440, W / 2 - pjw, 440, color=FIELD, sw=1.8))
    parts.append(arrow(W / 2 + pjw, 440, qx - rsw, 440, color=FIELD, sw=1.8))

    # позначка розриву узгодженості
    parts.append(text(W / 2, 495, "лаг: знімок читання наздоганяє запис із затримкою",
                      size=12, italic=True, color=FIELD))
    parts.append(text(W / 2, 525, "два боки більше не той самий рядок бази — це і є ціна",
                      size=12, bold=True, color=MUTED))

    render(os.path.join(IMG, "two-paths.svg"), W, H, *parts)


# ── Фігура 3: товстий сервіс → драбина з трьох кроків ────────────────────────
def fat_to_ladder():
    W, H = 1040, 620
    parts = []
    parts.append(text(W / 2, 34, "Один товстий сервіс — і драбина з нього", size=18, bold=True))

    # ── ліворуч: товстий OrderService, методи впереміш на спільній моделі ──
    lx = 210
    parts.append(text(lx, 74, "БУЛО", size=13, bold=True, color=MUTED))
    # заголовок сервісу
    hdr, hhw, hhh = box_at(lx, 108, "OrderService", size=13, bold=True,
                           fill=FILL, stroke=INK, min_w=300)
    parts.append(hdr)
    # методи впереміш: запис (червоні) і читання (сині) в одному тілі
    rows = [
        ("placeOrder()", POS), ("getOrderView()", NEG),
        ("cancelOrder()", POS), ("listOrders()", NEG),
        ("applyDiscount()", POS), ("salesReport()", NEG),
    ]
    y0 = 150
    for i, (name, col) in enumerate(rows):
        yy = y0 + i * 40
        b, bhw, bhh = box_at(lx, yy, name, size=12, fill=FILL, stroke=col, min_w=260)
        parts.append(b)
    # спільна модель під ними
    dm, dmw, dmh = box_at(lx, y0 + len(rows) * 40 + 18,
                          ["спільна доменна модель Order", "правила + поля «для показу»"],
                          size=12, bold=True, fill="#fdf6ec", stroke=MUTED, min_w=340)
    parts.append(dm)
    parts.append(text(lx, 560, "запис і читання труться",
                      size=12, italic=True, color=MUTED))
    parts.append(text(lx, 580, "об одну модель", size=12, italic=True, color=MUTED))

    # велика стрілка переходу
    parts.append(arrow(lx + 185, 330, lx + 285, 330, color=INK, sw=2.4))

    # ── праворуч: драбина з трьох кроків ──
    rx = 720
    parts.append(text(rx, 74, "СТАЛО (три кроки)", size=13, bold=True, color=FIELD))

    step1, s1w, s1h = box_at(rx, 140,
                             ["КРОК 1 · один код розводимо",
                              "CommandHandler + QueryHandler",
                              "та сама база, ті самі таблиці"],
                             size=12, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=380)
    parts.append(step1)
    step2, s2w, s2h = box_at(rx, 300,
                             ["КРОК 2 · окреме сховище читання",
                              "запис → нормалізоване",
                              "читання → денормалізовані знімки"],
                             size=12, bold=True, fill="#eaf0fd", stroke=NEG, min_w=380)
    parts.append(step2)
    step3, s3w, s3h = box_at(rx, 460,
                             ["КРОК 3 · проєкція + обхід лагу",
                              "подія / перечит переливає зміни",
                              "екран ховає кінцеву узгодженість"],
                             size=12, bold=True, fill="#fdecea", stroke=POS, min_w=380)
    parts.append(step3)

    parts.append(arrow(rx, 140 + s1h, rx, 300 - s2h, color=INK, sw=1.8))
    parts.append(arrow(rx, 300 + s2h, rx, 460 - s3h, color=INK, sw=1.8))

    parts.append(text(rx, 560, "що глибший крок — то дорожчий:",
                      size=12, italic=True, color=INK))
    parts.append(text(rx, 580, "спиняйся там, де перестало муляти",
                      size=12, bold=True, color=INK))

    render(os.path.join(IMG, "fat-to-ladder.svg"), W, H, *parts)


# ── Фігура 4: лаг проєкції на осі часу й три способи його сховати ─────────────
def projection_lag():
    W, H = 1040, 560
    parts = []
    parts.append(text(W / 2, 34, "Лаг проєкції: що бачить користувач після своєї дії", size=18, bold=True))

    # вісь часу
    ax0, ax1, ay = 90, 950, 150
    parts.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    parts.append(arrow(ax1 - 2, ay, ax1 + 4, ay, color=INK, sw=2))
    parts.append(text(ax1, ay - 16, "час", size=12, italic=True, color=MUTED, anchor="end"))

    # три моменти на осі
    t_cmd, t_read, t_proj = 200, 470, 740
    for tx, lbl, col in [(t_cmd, "команда змінила", POS),
                         (t_read, "сторінка читає", NEG),
                         (t_proj, "проєкція наздогнала", FIELD)]:
        parts.append(circle(tx, ay, 7, fill=col, stroke=col, sw=2))
    # підписи моментів — під віссю, з великим кроком, щоб не злипались
    parts.append(text(t_cmd, ay + 34, "команда змінила стан", size=12, bold=True, color=POS))
    parts.append(text(t_cmd, ay + 52, "у сховищі запису", size=11, color=MUTED))
    parts.append(text(t_read, ay + 34, "сторінка перечитує", size=12, bold=True, color=NEG))
    parts.append(text(t_read, ay + 52, "зі сховища читання", size=11, color=MUTED))
    parts.append(text(t_proj, ay + 34, "проєкція оновила знімок", size=12, bold=True, color=FIELD))
    parts.append(text(t_proj, ay + 52, "боки зійшлися", size=11, color=MUTED))

    # вікно лагу між командою і проєкцією
    parts.append(line(t_cmd, ay - 30, t_cmd, ay - 8, color=MUTED, sw=1, dash="4 4"))
    parts.append(line(t_proj, ay - 30, t_proj, ay - 8, color=MUTED, sw=1, dash="4 4"))
    parts.append(line(t_cmd, ay - 24, t_proj, ay - 24, color=MUTED, sw=1.4))
    parts.append(text((t_cmd + t_proj) / 2, ay - 32,
                      "ЛАГ · тут читання показує стару правду", size=12, bold=True, color=MUTED))

    # три способи сховати лаг — рамки внизу
    by = 300
    m1, m1w, m1h = box_at(200, by,
                          ["1 · читати з боку запису",
                           "на цьому екрані —",
                           "свіжо, але повільно"],
                          size=12, bold=True, fill="#fdecea", stroke=POS, min_w=280)
    parts.append(m1)
    m2, m2w, m2h = box_at(520, by,
                          ["2 · показати «застосовується»",
                           "чесно попередити,",
                           "оновити за мить"],
                          size=12, bold=True, fill="#fdf6ec", stroke=MUTED, min_w=280)
    parts.append(m2)
    m3, m3w, m3h = box_at(840, by,
                          ["3 · домалювати наперед",
                           "показати свій намір,",
                           "поки знімок доганяє"],
                          size=12, bold=True, fill="#eaf0fd", stroke=NEG, min_w=280)
    parts.append(m3)

    parts.append(text(W / 2, 430, "лаг не зникає — його ховають від очей або обходять там, де нестерпний",
                      size=13, italic=True, color=INK))
    parts.append(text(W / 2, 470, "питання-запобіжник: чи витримає користувач, що прочитане мить відстає від записаного?",
                      size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "projection-lag.svg"), W, H, *parts)


# ── Фігура 5 (для вставки hist): механізм старший за назву ────────────────────
def name_after_mechanism():
    """Стрічка часу: поділ читання/запису жив задовго до слова «CQRS».
    Ліворуч — механізм (Меєрове CQS, 1988), праворуч — коли зʼявилася НАЗВА."""
    W, H = 1060, 470
    parts = []
    parts.append(text(W / 2, 34, "Механізм старший за назву", size=18, bold=True))

    # Горизонтальна вісь часу
    ax_y = 152
    x0, x1 = 90, W - 90
    parts.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2))
    parts.append(arrow(x1 - 2, ax_y, x1 + 2, ax_y, color=INK, sw=2))
    parts.append(text(x1, ax_y - 16, "час", size=12, italic=True, color=MUTED, anchor="end"))

    # Чотири віхи: (частка позиції 0..1, рік, ярлик-угорі, хто/що-унизу, колір)
    marks = [
        (0.02, "1988", ["правило CQS"], ["Бертран Меєр,", "мова Eiffel:", "метод — команда", "АБО запит"], NEG),
        (0.55, "2008", ["попередник"], ["Уді Даган:", "поділ на боці", "служб (SOA)"], MUTED),
        (0.72, "2009", ["«Clarified CQRS»"], ["Уді Даган", "уточнює прийом", "(9 грудня)"], MUTED),
        (0.93, "2010", ["НАЗВА «CQRS»"], ["Ґреґ Янґ:", "поділ моделі,", "довкола DDD"], POS),
    ]
    span = x1 - x0 - 40
    xs = []
    for frac, year, top, bot, col in marks:
        x = x0 + 20 + frac * span
        xs.append(x)
        # риска на осі + рік
        parts.append(line(x, ax_y - 10, x, ax_y + 10, color=col, sw=2.4))
        parts.append(circle(x, ax_y, 5, fill=BG, stroke=col, sw=2.4))
        parts.append(text(x, ax_y - 26, year, size=15, bold=True, color=col))
        # ярлик угорі (чим є подія)
        tb, thw, thh = box_at(x, ax_y - 78, top, size=12, bold=True,
                              fill=FILL, stroke=col, min_w=136)
        parts.append(tb)
        # опис унизу (хто/що) — багаторядковий, з достатнім кроком
        parts.append(mtext(x, ax_y + 46, bot, size=11.5, color=INK, lh=1.35))

    # Дуга-акцент: від механізму (1988) до назви (2010) — десятиліття без імені.
    # Ярлик малюємо ПЕРШИМ (щоб узяти його пів-ширину), а лінію РОЗРИВАЄМО на його краях,
    # щоб напис не перетинала (svgcheck v6: лінія не має різати текст наскрізь).
    xa, xb = xs[0], xs[3]
    xm = (xa + xb) / 2
    brace_y = H - 58
    lab, lhw, lhh = box_at(xm, brace_y,
                           "≈ 22 роки: поділ уже працював — слова ще не було",
                           size=12.5, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=0)
    gap = lhw + 10                       # відступ від центра до краю ярлика + просвіт
    parts.append(line(xa, ax_y + 118, xa, brace_y, color=FIELD, sw=1, dash="4 4"))
    parts.append(line(xb, ax_y + 118, xb, brace_y, color=FIELD, sw=1, dash="4 4"))
    parts.append(line(xa, brace_y, xm - gap, brace_y, color=FIELD, sw=1.6))
    parts.append(line(xm + gap, brace_y, xb, brace_y, color=FIELD, sw=1.6))
    parts.append(lab)

    render(os.path.join(IMG, "name-after-mechanism.svg"), W, H, *parts)


if __name__ == "__main__":
    cqs_vs_cqrs()
    two_paths()
    fat_to_ladder()
    projection_lag()
    name_after_mechanism()
    print("figures written to", IMG)
