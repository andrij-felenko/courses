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


# ── Фігура 1: зберігати стан проти зберігати журнал ──────────────────────────
def state_vs_log():
    W, H = 1020, 560
    parts = []
    parts.append(text(W / 2, 34, "Зберігати підсумок — чи зберігати всі факти", size=18, bold=True))

    parts.append(line(W / 2, 60, W / 2, H - 24, color=MUTED, sw=1, dash="6 6"))
    parts.append(text(W / 4, 60, "звичайна модель · лише стан", size=13, bold=True, color=MUTED))
    parts.append(text(W * 3 / 4, 60, "зберігання подій · журнал фактів", size=13, bold=True, color=FIELD))

    # ── ліворуч: команда перезаписує єдиний рядок стану ──
    lx = W / 4
    cmd, chw, chh = box_at(lx, 118, ["команда", "зняти 250"], size=12,
                           fill="#fdecea", stroke=POS, min_w=180)
    parts.append(cmd)
    st, sthw, sthh = box_at(lx, 250, ["РЯДОК СТАНУ", "balance = 990.00"], size=13, bold=True,
                            fill=FILL, stroke=INK, min_w=280)
    parts.append(st)
    parts.append(arrow(lx, 118 + chh, lx, 250 - sthh, color=INK, sw=1.8))
    # привид старого значення, що затирається
    parts.append(text(lx, 320, "було balance = 1240.00", size=12, italic=True, color=MUTED))
    parts.append(text(lx, 340, "— перезаписано, зникло", size=12, italic=True, color=POS))
    parts.append(text(lx, 430, "історії нема:", size=12.5, bold=True, color=MUTED))
    parts.append(text(lx, 452, "зберігся лише останній кадр", size=12.5, color=MUTED))

    # ── праворуч: команда крізь правила дописує факт у кінець журналу ──
    rx = W * 3 / 4
    rcmd, rchw, rchh = box_at(rx, 100, ["команда", "зняти 250"], size=12,
                              fill="#fdecea", stroke=POS, min_w=180)
    parts.append(rcmd)
    rule, ruw, ruh = box_at(rx, 176, ["правила агрегату", "250 ≤ 1240 — можна"], size=11.5,
                            fill="#eaf7ef", stroke=FIELD, min_w=240)
    parts.append(rule)
    parts.append(arrow(rx, 100 + rchh, rx, 176 - ruh, color=INK, sw=1.6))

    # журнал: стовпчик подій, нова дописується в кінець
    jx0 = rx - 150
    jy0 = 250
    rows = ["+1000.00  внесено", "+500.00  внесено", "−250.00  знято", "−10.00  комісія"]
    for i, r in enumerate(rows):
        b = fitbox(jx0, jy0 + i * 34, 300, 28, r, size=12, fill=FILL, stroke=INK)
        parts.append(b)
    # нова подія від правил у кінець — стрілка йде ЛІВИМ полем колонки (повз текст),
    # з рогом до лівого краю останнього рядка, щоб не різати написи всередині
    jxl = jx0 - 20
    ynew = jy0 + 4 * 34 + 6
    parts.append(line(rx, 176 + ruh, rx, 236, color=FIELD, sw=1.8))
    parts.append(line(rx, 236, jxl, 236, color=FIELD, sw=1.8))
    parts.append(line(jxl, 236, jxl, ynew + 14, color=FIELD, sw=1.8))
    parts.append(arrow(jxl, ynew + 14, jx0 + 2, ynew + 14, color=FIELD, sw=1.8))
    newb = fitbox(jx0, ynew, 300, 28, "−250.00  знято  ← дописано в кінець",
                  size=11.5, fill="#eaf7ef", stroke=FIELD)
    parts.append(newb)

    parts.append(text(rx, 476, "стан ніде не лежить —", size=12.5, bold=True, color=FIELD))
    parts.append(text(rx, 498, "його виводять, згорнувши весь журнал", size=12.5, color=FIELD))

    render(os.path.join(IMG, "state-vs-log.svg"), W, H, *parts)


# ── Фігура 2: згортання журналу — стан тече крізь apply ──────────────────────
def fold_replay():
    W, H = 1060, 380
    parts = []
    parts.append(text(W / 2, 34, "Стан — це згортка подій", size=18, bold=True))

    # нульовий стан ліворуч
    ex, ey = 95, 190
    e0, e0hw, e0hh = box_at(ex, ey, ["порожньо", "balance 0"], size=12, bold=True,
                            fill=FILL, stroke=MUTED, min_w=130)
    parts.append(e0)

    # чотири події вздовж, значення балансу росте
    events = [("+1000", 1000), ("+500", 1500), ("−250", 1250), ("−10", 1240)]
    xs = [265, 465, 665, 865]
    prev_x = ex + e0hw
    prev_y = ey
    for (lbl, bal), x in zip(events, xs):
        # подія-пігулка над віссю
        ev, evhw, evhh = box_at(x, ey - 70, ["подія", lbl], size=12,
                                fill="#eaf0fd", stroke=NEG, min_w=120)
        parts.append(ev)
        # стан після прикладання — на осі
        col = FIELD
        sb, sbhw, sbhh = box_at(x, ey, "balance %d" % bal, size=12.5, bold=True,
                                fill="#eaf7ef", stroke=col, min_w=140)
        parts.append(sb)
        # стрілка apply від попереднього стану до цього
        parts.append(arrow(prev_x, prev_y, x - sbhw, ey, color=INK, sw=1.8))
        parts.append(text((prev_x + x - sbhw) / 2, ey - 8, "apply", size=10.5, italic=True, color=MUTED))
        # стрілка від події вниз у стан
        parts.append(arrow(x, ey - 70 + evhh, x, ey - sbhh, color=NEG, sw=1.4))
        prev_x = x + sbhw
        prev_y = ey

    parts.append(text(W / 2, ey + 95, "поточний баланс — не окреме число, а те, у що перетворився нуль,",
                      size=12.5, italic=True, color=INK))
    parts.append(text(W / 2, ey + 117, "пройшовши крізь усі події по черзі",
                      size=12.5, bold=True, color=FIELD))

    render(os.path.join(IMG, "fold-replay.svg"), W, H, *parts)


# ── Фігура 3: виправлення через компенсаційну подію (журнал незмінний) ────────
def compensating_event():
    W, H = 1020, 400
    parts = []
    parts.append(text(W / 2, 34, "Помилку не стирають — її сторнують", size=18, bold=True))

    # горизонтальна стрічка журналу, росте вправо
    ay = 150
    x0, x1 = 90, W - 90
    parts.append(line(x0, ay, x1, ay, color=INK, sw=2))
    parts.append(arrow(x1 - 2, ay, x1 + 4, ay, color=INK, sw=2))
    # підпис осі — під самою віссю, ліворуч від першої події (де немає ні пігулок, ні конекторів)
    parts.append(text(x0 + 4, ay + 20, "журнал росте вправо →", size=11.5, italic=True, color=MUTED, anchor="start"))

    # події вздовж стрічки
    evs = [
        (185, ["внесено", "+1000"], NEG, False),
        (355, ["знято", "−250"], NEG, False),
        (525, ["комісія", "−10"], NEG, False),
        (695, ["комісія", "−10"], POS, True),          # помилкова, друга
        (880, ["сторновано", "+10"], FIELD, False),     # компенсаційна
    ]
    for x, lbl, col, bad in evs:
        b, bhw, bhh = box_at(x, ay - 66, lbl, size=11.5, bold=True,
                             fill=("#fdecea" if col == POS else ("#eaf7ef" if col == FIELD else FILL)),
                             stroke=col, min_w=118)
        # короткий конектор ПІД пігулкою до точки на осі — цілком у просвіті між рамкою й віссю
        parts.append(line(x, ay - 66 + bhh + 4, x, ay - 9, color=col, sw=1.2, dash="3 3"))
        parts.append(b)
        parts.append(circle(x, ay, 6, fill=col, stroke=col, sw=2))

    # позначка «помилкова — НЕ викреслюємо»
    parts.append(text(695, ay + 34, "помилкова", size=11.5, bold=True, color=POS))
    parts.append(text(695, ay + 52, "лишається на місці", size=11, color=MUTED))
    # позначка компенсації
    parts.append(text(880, ay + 34, "гасить помилку", size=11.5, bold=True, color=FIELD))
    parts.append(text(880, ay + 52, "дописуванням", size=11, color=MUTED))

    # дуга від помилкової до компенсаційної
    parts.append(line(695, ay + 70, 695, ay + 84, color=FIELD, sw=1, dash="4 4"))
    parts.append(line(880, ay + 70, 880, ay + 84, color=FIELD, sw=1, dash="4 4"))
    lab, lhw, lhh = box_at((695 + 880) / 2, ay + 84,
                           "+10 гасить зайві −10 — стан сходиться, історія збережена",
                           size=12, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=0)
    # розрив лінії на краях ярлика, щоб не різала напис
    gap = lhw + 10
    parts.append(line(695, ay + 84, (695 + 880) / 2 - gap, ay + 84, color=FIELD, sw=1.4))
    parts.append(line((695 + 880) / 2 + gap, ay + 84, 880, ay + 84, color=FIELD, sw=1.4))
    parts.append(lab)

    parts.append(text(W / 2, H - 26, "журнал незмінний: неправильний запис не видаляють, а гасять доданою подією-противагою",
                      size=12, italic=True, color=INK))

    render(os.path.join(IMG, "compensating-event.svg"), W, H, *parts)


# ── Фігура 4 (для вставки proj): знімок відсікає хвіст журналу ────────────────
def snapshot_tail():
    W, H = 1160, 480
    parts = []
    parts.append(text(W / 2, 34, "Знімок: не згортати весь журнал, а лише хвіст після нього", size=18, bold=True))

    # спільна вісь журналу — довга стрічка подій, росте вправо
    ay_top = 150     # верхня доріжка: наївне переграння з нуля
    ay_bot = 350     # нижня доріжка: той самий журнал, але зі знімком
    x0 = 140
    xN = W - 120
    n_dots = 12          # умовно «весь журнал»
    snap_i = 8           # знімок після 9-ї події (індекс 8), далі — хвіст
    step = (xN - x0) / (n_dots - 1)
    xs = [x0 + i * step for i in range(n_dots)]

    # ── верхня доріжка: O(усіх подій) ──
    parts.append(text(x0 - 24, ay_top - 60, "БЕЗ знімка", size=13, bold=True, color=POS, anchor="start"))
    parts.append(line(x0, ay_top, xN, ay_top, color=INK, sw=2))
    parts.append(arrow(xN - 2, ay_top, xN + 6, ay_top, color=INK, sw=2))
    # нульовий стан
    z1, z1hw, z1hh = box_at(x0 - 44, ay_top, ["нуль", "0.00"], size=10.5, bold=True,
                            fill=FILL, stroke=MUTED, min_w=76)
    parts.append(z1)
    for i, x in enumerate(xs):
        parts.append(circle(x, ay_top, 5.5, fill=NEG, stroke=NEG, sw=1.5))
    # дужка «згортаємо ВСЕ» під усіма подіями
    parts.append(line(x0, ay_top + 26, xN, ay_top + 26, color=POS, sw=1.4))
    parts.append(line(x0, ay_top + 20, x0, ay_top + 26, color=POS, sw=1.4))
    parts.append(line(xN, ay_top + 20, xN, ay_top + 26, color=POS, sw=1.4))
    cost1, c1hw, c1hh = box_at(W / 2, ay_top + 50, "прикладаємо всі 1 000 000 подій — O(усіх)",
                              size=12, bold=True, fill="#fdecea", stroke=POS, min_w=0)
    parts.append(cost1)

    # ── нижня доріжка: O(хвоста) ──
    parts.append(text(x0 - 24, ay_bot - 60, "ЗІ знімком", size=13, bold=True, color=FIELD, anchor="start"))
    parts.append(line(x0, ay_bot, xN, ay_bot, color=INK, sw=2))
    parts.append(arrow(xN - 2, ay_bot, xN + 6, ay_bot, color=INK, sw=2))
    # ті самі події; до знімка — бліді (їх НЕ читаємо), після — читаємо
    xsnap = xs[snap_i]
    for i, x in enumerate(xs):
        used = i > snap_i
        col = FIELD if used else MUTED
        r = 5.5 if used else 4.0
        parts.append(circle(x, ay_bot, r, fill=col, stroke=col, sw=1.5))
    # позначка знімка на осі — вертикальна риска + пігулка над віссю
    parts.append(line(xsnap, ay_bot - 34, xsnap, ay_bot + 12, color=FIELD, sw=2, dash="4 3"))
    snapb, snhw, snhh = box_at(xsnap, ay_bot - 54, ["знімок #9", "1230.00"], size=10.5, bold=True,
                              fill="#eaf7ef", stroke=FIELD, min_w=96)
    parts.append(snapb)
    # підпис «пропускаємо» під головою журналу (ліворуч від знімка)
    parts.append(text((x0 + xsnap) / 2, ay_bot + 24, "ці події не читаємо зовсім", size=11,
                      italic=True, color=MUTED))
    # дужка «лише хвіст» під подіями ПІСЛЯ знімка
    xtail0 = xs[snap_i + 1] - 8
    parts.append(line(xtail0, ay_bot + 40, xN, ay_bot + 40, color=FIELD, sw=1.4))
    parts.append(line(xtail0, ay_bot + 34, xtail0, ay_bot + 40, color=FIELD, sw=1.4))
    parts.append(line(xN, ay_bot + 34, xN, ay_bot + 40, color=FIELD, sw=1.4))
    cost2, c2hw, c2hh = box_at((xtail0 + xN) / 2, ay_bot + 62,
                              "знімок + 3 події хвоста — O(після знімка)",
                              size=12, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=0)
    parts.append(cost2)

    render(os.path.join(IMG, "snapshot-tail.svg"), W, H, *parts)


# ── Фігура 5 (для вставки proj): один журнал — багато похідних проєкцій ───────
def one_log_many_projections():
    W, H = 1000, 470
    parts = []
    parts.append(text(W / 2, 34, "Один журнал — скільзавгодно похідних моделей", size=18, bold=True))

    # журнал ліворуч — вертикальна колонка сирих подій
    jx = 150
    jy0 = 96
    rows = ["Deposited +1000", "Deposited +500", "Withdrawn −250", "FeeCharged −10",
            "Deposited +800", "Withdrawn −120"]
    parts.append(text(jx, jy0 - 30, "ЖУРНАЛ (сирі факти)", size=12.5, bold=True, color=INK))
    for i, r in enumerate(rows):
        b = fitbox(jx - 105, jy0 + i * 40, 210, 32, r, size=11.5, fill=FILL, stroke=INK)
        parts.append(b)
    jcx = jx + 105        # правий край колонки журналу
    jcy = jy0 + (len(rows) * 40) / 2 - 4

    # три проєкції праворуч, кожна — своя згортка того самого журналу
    px = W - 210
    proj = [
        (120, ["Проєкція: БАЛАНС", "згортка +/−", "= 1920.00"], FIELD),
        (250, ["Проєкція: СЕР. ПОПОВНЕННЯ", "лише Deposited, середнє", "= 766.67"], NEG),
        (380, ["Проєкція: К-ТЬ КОМІСІЙ", "рахунок FeeCharged", "= 1"], POS),
    ]
    for cy, lines, col in proj:
        b, bhw, bhh = box_at(px, cy, lines, size=11, bold=False,
                             fill=("#eaf7ef" if col == FIELD else ("#eaf0fd" if col == NEG else "#fdecea")),
                             stroke=col, min_w=230)
        parts.append(b)
        # стрілка від журналу до проєкції з підписом «своя згортка»
        parts.append(arrow(jcx + 6, jcy, px - bhw, cy, color=col, sw=1.6))

    parts.append(text(jx, H - 30, "нову проєкцію додають будь-коли — проганяють згортку по тому самому журналу з минулого",
                      size=11.5, italic=True, color=INK, anchor="start"))

    render(os.path.join(IMG, "many-projections.svg"), W, H, *parts)


# ── Фігура 6 (для вставки hist): родовід прийому в часі ───────────────────────
def lineage_timeline():
    W, H = 1120, 480
    parts = []
    parts.append(text(W / 2, 34, "Родовід прийому: практика попереду опису", size=18, bold=True))

    # горизонтальна вісь часу
    ay = 255
    x0, x1 = 90, W - 90
    parts.append(line(x0, ay, x1, ay, color=INK, sw=2))
    parts.append(arrow(x1 - 2, ay, x1 + 4, ay, color=INK, sw=2))
    parts.append(text(x1 + 2, ay + 22, "час →", size=11.5, italic=True, color=MUTED, anchor="end"))

    # чотири віхи, рівномірно РОЗСТАВЛЕНІ (не за масштабом часу — за читністю),
    # підписи чергуються верх/низ, щоб рамки не налягали одна на одну.
    # note-рядок ставимо ДАЛІ від осі, ніж рамка, щоб курсив не торкався рамки.
    # (x, year, body-рядки, note, колір, вгору?)
    marks = [
        (270, "1299–1300", ["реєстр компанії", "Фаролфі, Флоренція"],
         "найдавніший знайдений", NEG, True),
        (525, "1458", ["рукопис Котрульї", "(друк аж 1573)"],
         "описав раніше — надрукували пізніше", FIELD, False),
        (780, "1494", ["«Summa» Пачолі,", "Венеція"],
         "перший ДРУК — його звуть «батьком»", POS, True),
        (1010, "2005", ["стаття Фаулера,", "eaaDev (draft)"],
         "назвав патерн «Event Sourcing»", NEG, False),
    ]
    for x, yr, body, note, col, up in marks:
        parts.append(circle(x, ay, 6, fill=col, stroke=col, sw=2))
        if up:
            # згори: [note] · [рамка] · [рік] · крапка
            parts.append(text(x, ay - 118, note, size=10.5, italic=True, color=MUTED))
            parts.append(text(x, ay - 98, yr, size=13, bold=True, color=col))
            b, bhw, bhh = box_at(x, ay - 62, body, size=11.5, bold=False,
                                 fill=FILL, stroke=col, min_w=196)
            parts.append(b)
            parts.append(line(x, ay - 62 + bhh + 2, x, ay - 9, color=col, sw=1.2, dash="3 3"))
        else:
            # знизу: крапка · [рік] · [рамка] · [note]
            parts.append(text(x, ay + 108, yr, size=13, bold=True, color=col))
            b, bhw, bhh = box_at(x, ay + 68, body, size=11.5, bold=False,
                                 fill=FILL, stroke=col, min_w=196)
            parts.append(b)
            parts.append(line(x, ay + 9, x, ay + 68 - bhh - 2, color=col, sw=1.2, dash="3 3"))
            parts.append(text(x, ay + 128, note, size=10.5, italic=True, color=MUTED))

    # підсумковий рядок унизу, у чистому полі під усіма підписами
    parts.append(text(W / 2, H - 16,
                      "щоразу винаходить безіменний практик, а імʼя й славу дістає той, хто описав і поширив",
                      size=12, italic=True, color=INK))

    render(os.path.join(IMG, "lineage-timeline.svg"), W, H, *parts)


# ── Фігура 7 (для вставки math): apply чиста — рівно два входи, решта заборонена ─
def pure_apply():
    W, H = 1040, 500
    parts = []
    parts.append(text(W / 2, 34, "apply мусить бути чистою: рівно два входи, більше нічого", size=17, bold=True))

    # центральна коробка apply
    ax, ay = W / 2, 190
    ab, abhw, abhh = box_at(ax, ay, ["apply", "(стан, подія)"], size=15, bold=True,
                            fill="#eaf7ef", stroke=FIELD, min_w=210)

    # два дозволені входи — ліворуч, зеленими стрілками В apply
    prev, phw, phh = box_at(ax - 320, ay - 58, ["попередній", "стан  sₖ₋₁"], size=12.5, bold=True,
                            fill=FILL, stroke=INK, min_w=180)
    ev, evhw, evhh = box_at(ax - 320, ay + 58, ["поточна", "подія  eₖ"], size=12.5, bold=True,
                            fill=FILL, stroke=INK, min_w=180)
    parts.append(prev)
    parts.append(ev)
    parts.append(arrow(ax - 320 + phw, ay - 58, ax - abhw, ay - 20, color=FIELD, sw=2))
    parts.append(arrow(ax - 320 + evhw, ay + 58, ax - abhw, ay + 20, color=FIELD, sw=2))
    parts.append(ab)

    # вихід — наступний стан праворуч
    nxt, nxthw, nxthh = box_at(ax + 320, ay, ["наступний", "стан  sₖ"], size=12.5, bold=True,
                               fill="#eaf7ef", stroke=FIELD, min_w=180)
    parts.append(arrow(ax + abhw, ay, ax + 320 - nxthw, ay, color=INK, sw=2))
    parts.append(nxt)
    parts.append(text(ax, ay - abhh - 14, "sₖ = apply(sₖ₋₁, eₖ)", size=13, italic=True, color=MUTED))

    # заборонені входи — знизу; кожен у червоній рамці з бейджем-заборони ✗ у кутку,
    # обірваний пунктир угору до apply (лінії НЕ проходять крізь написи).
    forb = ["годинник (час)", "випадкове число", "зовнішнє правило", "стан бази даних"]
    nb = len(forb)
    span = 860
    x0 = ax - span / 2
    fy = 420
    for i, name in enumerate(forb):
        fx = x0 + span * (i + 0.5) / nb
        b, bhw, bhh = box_at(fx, fy, name, size=11.5, fill="#fdecea", stroke=POS, min_w=160)
        parts.append(b)
        # бейдж-заборони у верхньому лівому куті рамки — не торкається тексту всередині
        parts.append(circle(fx - bhw, fy - bhh, 9, fill="#fdecea", stroke=POS, sw=2))
        parts.append(text(fx - bhw, fy - bhh + 4.5, "✗", size=12, bold=True, color=POS))
        # обірваний пунктир угору до apply (у просвіті над рамкою, повз усі написи)
        parts.append(line(fx, fy - bhh - 2, fx, ay + abhh + 24, color=POS, sw=1.2, dash="4 4"))

    parts.append(text(W / 2, ay + abhh + 50, "будь-який прихований вхід ламає детермінованість переграння",
                      size=12.5, italic=True, color=INK))

    render(os.path.join(IMG, "pure-apply.svg"), W, H, *parts)


# ── Фігура 8 (для вставки math): знімок — проміжна сума; обидва шляхи → той самий стан ─
def snapshot_correct():
    W, H = 1100, 430
    parts = []
    parts.append(text(W / 2, 34, "Знімок — проміжна сума тієї самої згортки", size=17, bold=True))

    # спільна вісь подій e1..e6, з відзначеним рубежем k
    n = 6
    k = 3
    x0, x1 = 175, W - 165
    xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]
    ey = 118
    # порожній стан ліворуч
    e0, e0hw, e0hh = box_at(x0 - 78, ey, ["∅", "нуль"], size=11.5, bold=True,
                            fill=FILL, stroke=MUTED, min_w=88)
    parts.append(e0)
    # події-пігулки: до k — сині, від k — зелені (їх бере короткий шлях)
    for i, x in enumerate(xs):
        col = FIELD if i >= k else NEG
        b, bhw, bhh = box_at(x, ey, "e%d" % (i + 1), size=12.5, bold=True,
                             fill=("#eaf7ef" if i >= k else "#eaf0fd"),
                             stroke=col, min_w=60)
        parts.append(b)

    # довгий шлях — суцільна стрілка від нуля крізь усі до кінцевого стану
    fin, finhw, finhh = box_at(x1 + 92, ey, ["кінцевий", "стан  sₙ"], size=12, bold=True,
                               fill="#eaf7ef", stroke=FIELD, min_w=118)
    parts.append(arrow(x0 - 78 + e0hw, ey, x1 + 92 - finhw, ey, color=INK, sw=1.6))
    parts.append(text((x0 + x1) / 2, ey - 32, "довгий шлях: згорнути весь журнал від ∅",
                      size=12, italic=True, color=MUTED))
    parts.append(fin)

    # знімок sk під рубежем між e_k та e_{k+1}: збережена проміжна сума
    sk_x = (xs[k - 1] + xs[k]) / 2
    sky = 250
    sk, skhw, skhh = box_at(sk_x, sky, ["знімок", "sₖ на кроці k"], size=12.5, bold=True,
                            fill="#fff6d6", stroke="#b8860b", min_w=150)
    parts.append(sk)
    # пунктир від осі вниз у знімок (у просвіті ліворуч від рубежа, повз пігулки подій)
    parts.append(line(sk_x, ey + 18, sk_x, sky - skhh, color="#b8860b", sw=1.3, dash="4 4"))
    # підпис «зупинили тут» — ЛІВОРУЧ від знімка, end-anchor, щоб жодна лінія його не різала
    parts.append(text(sk_x - skhw - 14, sky - 6, "зупинили згортку тут", size=11.5,
                      italic=True, color=MUTED, anchor="end"))
    parts.append(text(sk_x - skhw - 14, sky + 12, "і зберегли проміжну суму", size=11.5,
                      italic=True, color=MUTED, anchor="end"))

    # короткий шлях — від ПРАВОГО краю знімка праворуч, тоді донизу під кінцевий стан,
    # лише події після k, у ТОЙ САМИЙ sn. Горизонталь іде правим полем — повз усі написи.
    short_y = 340
    parts.append(text(sk_x + skhw + 16, sky - 6, "короткий шлях: від sₖ", size=12,
                      italic=True, color=FIELD, anchor="start"))
    parts.append(text(sk_x + skhw + 16, sky + 12, "прикласти лише e%d…e%d" % (k + 1, n), size=12,
                      italic=True, color=FIELD, anchor="start"))
    # L-подібний маршрут: праворуч від знімка вниз на short_y, тоді вправо до-під sn
    turn_x = x1 + 20
    parts.append(line(sk_x + skhw, sky, turn_x, sky, color=FIELD, sw=1.8))
    parts.append(line(turn_x, sky, turn_x, short_y, color=FIELD, sw=1.8))
    parts.append(arrow(turn_x, short_y, x1 + 92 - finhw, short_y, color=FIELD, sw=1.8))
    # пунктир від точки під sn вгору до самого кінцевого стану — обидва шляхи сходяться в sn
    parts.append(line(x1 + 92, short_y, x1 + 92, ey + finhh, color=FIELD, sw=1.8, dash="5 5"))

    parts.append(text(W / 2, H - 22, "обидва шляхи дають БУКВАЛЬНО той самий sₙ — знімок не наближає, а тотожний",
                      size=12.5, bold=True, color=FIELD))

    render(os.path.join(IMG, "snapshot-correct.svg"), W, H, *parts)


if __name__ == "__main__":
    state_vs_log()
    fold_replay()
    compensating_event()
    snapshot_tail()
    one_log_many_projections()
    lineage_timeline()
    pure_apply()
    snapshot_correct()
    print("figures written to", IMG)
