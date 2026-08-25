# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

VIOLET = "#6a3d9a"
GOLD   = "#b8860b"


# ── value-chain: ланцюг спеціалізованих гравців ───────────────────────────────
# Ідея: один чіп проходить крізь кілька РІЗНИХ фірм; жодна не робить усе сама.
# Верхній ряд (EDA, IP) живить fabless; той віддає файл масок на foundry;
# foundry спирається на постачальників обладнання; кристали йдуть на OSAT.

def fig_value_chain():
    W, H = 760, 390
    p = []
    row_y, bw, bh = 165, 150, 92

    # три головні ланки ланцюга
    boxes = [
        (55,  "#cfe3f7", "Fabless", "проєктує чіп", "(логіка, схема)"),
        (305, "#cfe7d2", "Foundry", "виготовляє", "пластини"),
        (555, "#fde9b0", "OSAT",    "корпусує",   "й тестує"),
    ]
    cx = []
    for x, fill, head, l1, l2 in boxes:
        c = x + bw / 2
        cx.append(c)
        p.append(rect(x, row_y, bw, bh, fill=fill, stroke=INK, sw=2, rx=10))
        p.append(text(c, row_y + 30, head, size=15, color=INK, bold=True))
        p.append(text(c, row_y + 52, l1, size=11, color=MUTED))
        p.append(text(c, row_y + 68, l2, size=11, color=MUTED))

    midy = row_y + bh / 2
    # стрілка fabless → foundry: передають файл масок (tape-out)
    p.append(line(cx[0] + bw / 2, midy, cx[1] - bw / 2, midy, color=INK, sw=2.4))
    p.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (cx[1] - bw / 2, midy, cx[1] - bw / 2 - 11, midy - 5,
                cx[1] - bw / 2 - 11, midy + 5, INK))
    p.append(text((cx[0] + cx[1]) / 2, midy - 12, "файл масок (GDSII)", size=11, color=INK, bold=True))
    p.append(text((cx[0] + cx[1]) / 2, midy + 22, "tape-out", size=10.5, color=FIELD, italic=True))
    # стрілка foundry → OSAT: готові пластини
    p.append(line(cx[1] + bw / 2, midy, cx[2] - bw / 2, midy, color=INK, sw=2.4))
    p.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (cx[2] - bw / 2, midy, cx[2] - bw / 2 - 11, midy - 5,
                cx[2] - bw / 2 - 11, midy + 5, INK))
    p.append(text((cx[1] + cx[2]) / 2, midy + 22, "готові пластини", size=10.5, color=FIELD))

    # верхні постачальники, що живлять fabless: EDA та IP-ядра
    fb_top = row_y
    p.append(rect(40, 58, 180, 42, fill="#efe7f7", stroke=VIOLET, sw=1.8, rx=8))
    p.append(text(130, 76, "EDA-інструменти", size=12, color=VIOLET, bold=True))
    p.append(text(130, 92, "ПЗ для проєктування", size=10.5, color=MUTED))
    p.append(line(130, 100, 130, fb_top, color=MUTED, sw=1.6))
    p.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (130, fb_top, 125, fb_top - 9, 135, fb_top - 9, MUTED))

    fb_bot = row_y + bh
    p.append(rect(40, 312, 180, 42, fill="#efe7f7", stroke=VIOLET, sw=1.8, rx=8))
    p.append(text(130, 330, "IP-ядра", size=12, color=VIOLET, bold=True))
    p.append(text(130, 346, "готові блоки (CPU, USB)", size=10, color=MUTED))
    p.append(line(130, 312, 130, fb_bot, color=MUTED, sw=1.6))
    p.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (130, fb_bot, 125, fb_bot + 9, 135, fb_bot + 9, MUTED))

    # постачальник обладнання, що живить foundry
    p.append(rect(290, 312, 180, 42, fill="#fbeaea", stroke=POS, sw=1.8, rx=8))
    p.append(text(380, 330, "ASML та інші", size=12, color=POS, bold=True))
    p.append(text(380, 346, "обладнання фабрики", size=10.5, color=MUTED))
    p.append(line(380, 312, 380, fb_bot, color=MUTED, sw=1.6))
    p.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (380, fb_bot, 375, fb_bot + 9, 385, fb_bot + 9, MUTED))

    p.append(text(W / 2, 376,
                  "Проєкт, виготовлення, корпусування та інструменти — окремі фірми, часто з різних країн.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "value-chain.svg"), W, H, *p,
           title="Ланцюг створення чіпа: кожен робить своє")


# ── fab-cost: вартість фабу зростає з кожним поколінням ───────────────────────
# Ідея: стовпчики ціни передового фабу ростуть; окупає таку ціну лише обсяг,
# тож конкурентний завод під силу одиницям.

def fig_fab_cost():
    W, H = 720, 360
    ox, oy = 90, 285        # початок осей
    aw, ah = 560, 220
    p = []
    p.append(line(ox, oy, ox, oy - ah - 8, color=INK, sw=1.8))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(text(ox - 12, oy - ah - 2, "млрд $", size=11, color=INK, anchor="end", italic=True))

    # покоління й приблизна вартість (млрд $) — порядок величини
    bars = [("старші\nвузли", 3), ("28 нм", 6), ("7 нм", 12), ("3 нм", 20), ("2 нм", 28)]
    maxv = 30.0
    n = len(bars)
    slot = aw / (n + 0.5)
    bw = slot * 0.56
    for i, (lab, v) in enumerate(bars):
        bx = ox + slot * (i + 0.5) - bw / 2
        bh = ah * (v / maxv)
        shade = "#dbe6fb" if i < n - 1 else "#fbe0dc"
        edge = "#9db8ec" if i < n - 1 else POS
        p.append(rect(bx, oy - bh, bw, bh, fill=shade, stroke=edge, sw=1.6, rx=3))
        p.append(text(bx + bw / 2, oy - bh - 8, "$%d" % v, size=12, color=INK, bold=True))
        p.append(mtext(bx + bw / 2, oy + 18, lab, size=11, color=MUTED, lh=1.15))

    # підпис тренду
    p.append(text(ox + aw - 6, oy - ah + 18, "+ мільярди щороку на устаткування",
                  size=11, color=POS, anchor="end"))
    p.append(text(ox + aw - 6, oy - ah + 36, "й розробку наступного покоління",
                  size=11, color=POS, anchor="end"))
    p.append(text(W / 2, oy + 52,
                  "Окупити таку ціну може лише виробництво колосальними тиражами — тож фаб під силу одиницям.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "fab-cost.svg"), W, H, *p,
           title="Вартість передового фабу росте з кожним вузлом")


# ── models: три способи існувати в індустрії ──────────────────────────────────
# Ідея: дорожнеча фабу розколола колишню єдину модель IDM на дві —
# тих, хто лише проєктує, і тих, хто лише виготовляє.

def fig_models():
    W, H = 720, 320
    p = []
    cards = [
        (40,  NEG,    "IDM",     "проєктує І виготовляє", "власні фабрики"),
        (264, FIELD,  "Fabless", "лише проєктує",          "виготовлення — фабриці"),
        (488, GOLD,   "Foundry", "лише виготовляє",        "чужі чіпи на замовлення"),
    ]
    for x, col, head, l1, l2 in cards:
        c = x + 192 / 2
        p.append(rect(x, 78, 192, 132, fill=FILL, stroke=col, sw=2.2, rx=12))
        p.append(text(c, 116, head, size=16, color=col, bold=True))
        p.append(text(c, 150, l1, size=12.5, color=INK, bold=True))
        p.append(text(c, 174, l2, size=11.5, color=MUTED))

    p.append(text(W / 2, 254,
                  "Колись усі були IDM — увесь ланцюг під одним дахом.",
                  size=12, color=MUTED, italic=True))
    p.append(text(W / 2, 274,
                  "Дорожнеча фабу розколола індустрію надвоє: хто проєктує (fabless) і хто виготовляє (foundry).",
                  size=12, color=MUTED, italic=True))
    p.append(text(W / 2, 294,
                  "IDM лишаються, та на передовому краї їх дедалі менше.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "models.svg"), W, H, *p,
           title="Три моделі бізнесу в індустрії чіпів")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставки 📜 hist-tsmc
# ════════════════════════════════════════════════════════════════════════════

# ── idm-vs-split: розріз ланцюга на fabless + foundry ─────────────────────────
# Ідея вставки: винахід Чанга — не нова машина, а нова МЕЖА фірми. Угорі IDM
# веде весь ланцюг; унизу той самий ланцюг розрізано — fabless проєктує,
# foundry лише варить кремній.

def _chain_row(x0, y, steps, active, color, dim="#dcdcdc"):
    """Рядок із 6 клітинок-етапів; active — множина індексів, що належать фірмі."""
    out = []
    cw, ch, gap = 118, 52, 14
    cx = []
    for i, lab in enumerate(steps):
        bx = x0 + i * (cw + gap)
        on = i in active
        c = color if on else dim
        fill = FILL if on else "#f6f6f6"
        out.append(rect(bx, y, cw, ch, fill=fill, stroke=c, sw=1.6 if on else 1.0, rx=8))
        out.append(mtext(bx + cw / 2, y + ch / 2 - 3, lab, size=10,
                         color=(INK if on else dim), lh=1.15, bold=on))
        cx.append(bx + cw / 2)
        if i:
            ax0 = x0 + (i - 1) * (cw + gap) + cw
            edge = MUTED if (on and (i - 1) in active) else dim
            out.append(line(ax0, y + ch / 2, bx, y + ch / 2, color=edge, sw=1.6))
    return out, cx


def fig_idm_vs_split():
    W, H = 920, 470
    steps = ["ідея й\nархітектура", "проєкт\nсхеми", "маски",
             "виробництво\nна пластині", "корпус\nі тест", "бренд\nі продаж"]
    p = []
    p.append(text(W / 2, 52, "Класична модель IDM: одна фірма робить усе",
                  size=13, color=NEG, anchor="middle", bold=True))
    row1, _ = _chain_row(40, 70, steps, set(range(6)), NEG)
    p += row1
    p.append(text(W / 2, 150, "увійти в гру може лише той, у кого є фабрика на мільярди",
                  size=10.5, color=MUTED, italic=True))

    p.append(line(50, 172, W - 50, 172, color=GOLD, sw=2, dash="6 5"))
    p.append(text(W / 2, 190, "розріз Чанга: проєкт окремо, виробництво окремо",
                  size=12.5, color="#9a7322", bold=True))

    p.append(text(W / 2, 224, "Модель «fabless + foundry»: ланцюг ведуть дві різні фірми",
                  size=13, color=FIELD, anchor="middle", bold=True))
    rowF, _ = _chain_row(40, 242, steps, {0, 1, 2, 5}, FIELD)
    p += rowF
    p.append(text(48, 236, "FABLESS — проєктує, кремнію не варить", size=10.5,
                  color=FIELD, anchor="start", bold=True))
    rowO, _ = _chain_row(40, 322, steps, {3, 4}, POS)
    p += rowO
    p.append(text(48, 316, "FOUNDRY (TSMC) — лише виробляє чужі проєкти, свого бренду не має",
                  size=10.5, color=POS, anchor="start", bold=True))

    p.append(rect(50, 392, W - 100, 60, fill="#f4f7f4", stroke=FIELD, sw=1.5, rx=10))
    p.append(text(W / 2, 416,
                  "Ключ історії — не технологія, а проведена межа: одну справу розрізали на дешевий розум і дорогий капітал.",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 438,
                  "Спільну фабрику дано в користування всім: десятки малих фірм проєктують, а TSMC варить кремній і ні з ким не конкурує.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "idm-vs-split.svg"), W, H, *p,
           title="Що придумав Чанг: розрізати ланцюг чіпа навпіл")


# ── cap-table: засновницький капітал TSMC 1987 ───────────────────────────────
# Ідея: «фабрика однієї людини» — міф. Гроші дали держава й приватні родини,
# ключову технологію ліцензував Philips; внесок Чанга — задум, не капітал.

def fig_cap_table():
    import math as _m
    W, H = 920, 470
    p = []
    # кругова частка зліва
    cx, cy, r = 235, 235, 118
    parts = [("Уряд Тайваню\n(Фонд розвитку)", 48.3, FIELD, "#eafaef"),
             ("Philips", 27.6, NEG, "#eaf0fd"),
             ("приватні\nродини", 24.1, GOLD, "#fbf2dc")]
    a0 = -90.0
    for lab, pct, col, _f in parts:
        a1 = a0 + pct / 100.0 * 360.0
        x1, y1 = cx + r * _m.cos(_m.radians(a0)), cy + r * _m.sin(_m.radians(a0))
        x2, y2 = cx + r * _m.cos(_m.radians(a1)), cy + r * _m.sin(_m.radians(a1))
        large = 1 if (a1 - a0) > 180 else 0
        p.append('<path d="M%.1f,%.1f L%.1f,%.1f A%.1f,%.1f 0 %d 1 %.1f,%.1f Z" '
                 'fill="%s" stroke="#ffffff" stroke-width="2"/>'
                 % (cx, cy, x1, y1, r, r, large, x2, y2, col))
        am = _m.radians((a0 + a1) / 2)
        lx, ly = cx + r * 0.6 * _m.cos(am), cy + r * 0.6 * _m.sin(am)
        p.append(text(lx, ly + 4, "%.0f%%" % pct, size=15, color="#ffffff", bold=True))
        a0 = a1
    p.append(text(cx, cy + r + 24, "хто дав гроші", size=11, color=MUTED, italic=True))

    # картки-пояснення справа
    cards = [
        (FIELD, "Держава (Фонд розвитку)", "майже половина капіталу — пряма ставка уряду; промислову",
         "політику вели Сун Юньсюань і радник К. Т. Лі, що й покликали Чанга"),
        (NEG, "Philips (Нідерланди)", "за частку передав виробничу технологію й ліцензував патенти;",
         "без чужого, відпрацьованого процесу молода фабрика не запустилася б"),
        (GOLD, "Приватні інвестори Тайваню", "заможні промислові родини — решта капіталу; держава радше",
         "переконала їх розділити ризик, ніж дочекалася добровільної черги"),
        (POS, "Морріс Чанг (Morris Chang)", "не гаманець, а задум, досвід і репутація: 25 років у TI,",
         "де подібну ідею свого часу відхилили — тут її дали збудувати"),
    ]
    bx, bw, bh, gap = 430, 460, 78, 12
    by = 60
    for col, head, l1, l2 in cards:
        p.append(rect(bx, by, bw, bh, fill=FILL, stroke=col, sw=1.6, rx=9))
        p.append(rect(bx, by, 8, bh, fill=col, stroke=col, sw=0, rx=0))
        p.append(text(bx + 20, by + 22, head, size=12, color=col, anchor="start", bold=True))
        p.append(text(bx + 20, by + 44, l1, size=9.6, color=INK, anchor="start"))
        p.append(text(bx + 20, by + 60, l2, size=9.6, color=INK, anchor="start"))
        by += bh + gap

    p.append(text(W / 2, 456,
                  "За «дивом однієї людини» стоїть колективний пакет: внесок Чанга — задум, а не капітал.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "cap-table.svg"), W, H, *p,
           title="TSMC, 1987: чий насправді був капітал і технологія")


# ── who-was-first: два різні твердження про «першість» TSMC ───────────────────
# Ідея: TSMC не перша, хто варив чуже, і не вона винайшла fabless. Вона перша
# зробила виробництво на замовлення надійною, головною справою без конкуренції.

def fig_who_was_first():
    W, H = 920, 480
    p = []
    # ліва колонка — що вже було
    lx, lw = 50, 380
    p.append(text(lx + lw / 2, 60, "Що вже існувало до 1987", size=13.5, color=NEG, bold=True))
    p.append(rect(lx, 72, lw, 250, fill="#f3f5fd", stroke=NEG, sw=1.6, rx=10))
    left = [("Fujitsu, IBM, NEC, TI, Toshiba", "гіганти-IDM іноді варили чужі чипи —",
             "але як побічну послугу, у вільний час лінії"),
            ("≈ 50 fabless-фірм (сер. 1980-х)", "уже проєктували чипи без власної фабрики",
             "й шукали, де їх замовити"),
            ("Chips & Technologies, 1985", "Ґордон Кемпбелл і Дадо Банатао —",
             "часто звана першою суто fabless-фірмою")]
    yy = 88
    for head, a, b in left:
        p.append(rect(lx + 16, yy, lw - 32, 66, fill=BG, stroke=NEG, sw=1.2, rx=7))
        p.append(text(lx + 28, yy + 20, head, size=10.5, color=INK, anchor="start", bold=True))
        p.append(text(lx + 28, yy + 38, a, size=9.3, color=MUTED, anchor="start"))
        p.append(text(lx + 28, yy + 53, b, size=9.3, color=MUTED, anchor="start"))
        yy += 74
    p.append(text(lx + lw / 2, 314, "побічна послуга — ненадійна, а IDM ще й конкурент",
                  size=9.6, color=POS, italic=True))

    # стрілка-місток
    p.append(line(lx + lw + 4, 200, lx + lw + 44, 200, color=GOLD, sw=2.4))
    p.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (lx + lw + 44, 200, lx + lw + 33, 195, lx + lw + 33, 205, GOLD))
    p.append(text(lx + lw + 24, 188, "чого", size=9, color="#9a7322", italic=True))
    p.append(text(lx + lw + 24, 218, "бракувало", size=9, color="#9a7322", italic=True))

    # права колонка — що додала TSMC
    rx, rw = 490, 380
    p.append(text(rx + rw / 2, 60, "Що додала TSMC (1987)", size=13.5, color=FIELD, bold=True))
    p.append(rect(rx, 72, rw, 250, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=10))
    right = [("Виробництво — основна справа", "не підробіток фабрики, а весь сенс фірми:",
              "потужність лінії завжди для клієнта"),
             ("«Ми не конкуруємо з клієнтом»", "TSMC не має власних чипів-брендів —",
              "тож клієнт сміливо віддає свій проєкт"),
             ("Спільна фабрика для всіх", "одна дорога лінія обслуговує десятки малих",
              "фірм — кожній порізно було б не під силу")]
    yy = 88
    for head, a, b in right:
        p.append(rect(rx + 16, yy, rw - 32, 66, fill=BG, stroke=FIELD, sw=1.2, rx=7))
        p.append(text(rx + 28, yy + 20, head, size=10.5, color=INK, anchor="start", bold=True))
        p.append(text(rx + 28, yy + 38, a, size=9.3, color=MUTED, anchor="start"))
        p.append(text(rx + 28, yy + 53, b, size=9.3, color=MUTED, anchor="start"))
        yy += 74
    p.append(text(rx + rw / 2, 314, "проєктувати чипи змогли навіть малі команди",
                  size=9.6, color=FIELD, italic=True))

    p.append(rect(50, 392, W - 100, 66, fill="#f4f7f4", stroke=FIELD, sw=1.5, rx=10))
    p.append(text(W / 2, 416,
                  "Точно: TSMC — не перша, хто варив чужі чипи, і не вона винайшла fabless. Вона перша зробила виробництво на замовлення",
                  size=10.6, color=INK, bold=True))
    p.append(text(W / 2, 438,
                  "надійною головною справою фірми, яка нікому не конкурує. Саме ця довіра, а не сам факт «варимо чуже», запустила fabless-індустрію.",
                  size=10.2, color=MUTED, italic=True))
    render(os.path.join(OUT, "who-was-first.svg"), W, H, *p,
           title="Чим саме TSMC була «першою»: два різні твердження")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставки 🧮 math-moore-dennard
# ════════════════════════════════════════════════════════════════════════════

# ── moore-line: експонента на лог- і лінійній осях ───────────────────────────
# Ідея: подвоєння за сталий час — це пряма на лог-осі й «зліт у стіну» на
# лінійній. Один ряд чисел; лог-вісь робить ріст читабельним.

def fig_moore_line():
    import math as _m
    W, H = 920, 540
    p = []
    # роки й число транзисторів (порядок величини), 1971..2023
    yrs = [1971, 1984, 1997, 2010, 2023]
    # ── ліва панель: лог-вісь ──
    ox, oy, aw, ah = 88, 470, 300, 380
    p.append(line(ox, oy - ah, ox, oy, color=MUTED, sw=1.6))
    p.append(line(ox, oy, ox + aw, oy, color=MUTED, sw=1.6))
    p.append(text(ox + aw / 2, 80, "Лог-вісь: рівний крок = ×10", size=13.5, color=NEG, bold=True))
    decades = ["10³", "10⁴", "10⁵", "10⁶", "10⁷", "10⁸", "10⁹", "10¹⁰", "10¹¹"]
    nd = len(decades)
    for i, lab in enumerate(decades):
        gy = oy - ah * i / (nd - 1)
        p.append(line(ox, gy, ox + aw, gy, color="#e4e4e4", sw=1.0))
        p.append(text(ox - 8, gy + 4, lab, size=10, color=MUTED, anchor="end"))
    for i, yr in enumerate(yrs):
        gx = ox + aw * i / (len(yrs) - 1)
        p.append(text(gx, oy + 18, str(yr), size=10.5, color=MUTED))
    # ідеальний темп ×2/2роки — пряма
    p.append(line(ox, oy - ah * 0.04, ox + aw, oy - ah, color=GOLD, sw=2.2, dash="6 4"))
    p.append(text(ox + aw * 0.55, oy - ah * 0.55, "× 2 кожні 2 роки", size=11, color=GOLD, anchor="start", bold=True))
    # реальні точки (трохи нерівні) — лягають на пряму
    logpts = [0.04, 0.30, 0.55, 0.80, 0.985]
    poly = []
    for i, fr in enumerate(logpts):
        gx = ox + aw * i / (len(logpts) - 1)
        gy = oy - ah * fr
        poly.append("%.1f,%.1f" % (gx, gy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(poly), NEG))
    for i, fr in enumerate(logpts):
        gx = ox + aw * i / (len(logpts) - 1)
        p.append(circle(gx, oy - ah * fr, 4.2, fill=NEG, stroke=NEG, sw=0))
    p.append(text(ox + 6, oy - ah + 18, "пряма = стала швидкість росту", size=10.5, color=NEG, anchor="start"))

    # ── права панель: лінійна вісь ──
    rx, rw = 612, 300
    p.append(line(rx, oy - ah, rx, oy, color=MUTED, sw=1.6))
    p.append(line(rx, oy, rx + rw, oy, color=MUTED, sw=1.6))
    p.append(text(rx + rw / 2, 80, "Лінійна вісь: той самий ряд", size=13.5, color=POS, bold=True))
    p.append(text(rx - 8, oy - ah + 10, "млрд", size=9.5, color=MUTED, anchor="end"))
    for k in range(5):
        gy = oy - ah * k / 4
        p.append(line(rx, gy, rx + rw, gy, color="#e4e4e4", sw=1.0))
        p.append(text(rx - 8, gy + 4, str(k * 20), size=10, color=MUTED, anchor="end"))
    # реальні значення в млрд: майже нуль до ~2010, потім зліт
    linpts = [0.0, 0.0, 0.01, 0.18, 0.98]
    poly2 = []
    for i, fr in enumerate(linpts):
        gx = rx + rw * i / (len(linpts) - 1)
        poly2.append("%.1f,%.1f" % (gx, oy - ah * fr))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(poly2), POS))
    for i, fr in enumerate(linpts):
        gx = rx + rw * i / (len(linpts) - 1)
        p.append(circle(gx, oy - ah * fr, 4.0, fill=POS, stroke=POS, sw=0))
    for i, yr in enumerate([1971, 1997, 2023]):
        gx = rx + rw * [0, 0.5, 1][i]
        p.append(text(gx, oy + 18, str(yr), size=10.5, color=MUTED))
    p.append(text(rx + rw * 0.42, oy - 14, "перші 30 років злиплися біля нуля", size=9.6, color=MUTED))
    p.append(text(rx + rw - 6, oy - ah + 28, "«стіна»", size=10.5, color=POS, anchor="end", bold=True))

    p.append(rect(88, 504, W - 176, 26, fill="#eef3fb", stroke=NEG, sw=0, rx=6))
    p.append(text(W / 2, 521,
                  "Одна й та сама крива. Лог-вісь випрямляє експоненту в пряму й робить темп подвоєння видимим оком.",
                  size=11.2, color=INK))
    render(os.path.join(OUT, "moore-line.svg"), W, H, *p,
           title="Закон Мура: експонента, випрямлена логарифмічною віссю")


# ── dennard: правила масштабування і їхній злам ──────────────────────────────
# Ідея: доки напруга падала разом із розміром, щільність потужності лишалася
# рівною, а частота вільно росла. Після ~2005 напруга вперлася в поріг —
# щільність потужності полізла вгору, частота стала.

def fig_dennard():
    W, H = 920, 540
    p = []
    # ліва панель — доба «безкоштовного обіду»
    p.append(rect(40, 70, 410, 200, fill="#f1f8f3", stroke=FIELD, sw=1.5, rx=12))
    p.append(text(245, 94, "Доба «безкоштовного обіду» (≈1974–2005)", size=13, color=INK, bold=True))
    rowsL = [("розмір (довжина)", "× 0.7", FIELD),
             ("площа транзистора", "× 0.5  (0.7²)", FIELD),
             ("напруга живлення V", "× 0.7", FIELD),
             ("потужність / транзистор", "× 0.5", FIELD),
             ("потужність на 1 мм²", "× 1  — стала!", NEG),
             ("частота f", "× 1.4  росте вільно", FIELD)]
    yy = 120
    for lab, val, col in rowsL:
        p.append(text(62, yy, lab, size=11.5, color=INK, anchor="start"))
        p.append(text(430, yy, val, size=11.5, color=col, anchor="end", bold=True))
        yy += 23
    p.append(text(245, 262, "транзисторів удвічі більше — а гріє та сама площа так само",
                  size=10.2, color=FIELD, italic=True))

    # права панель — після зламу
    p.append(rect(470, 70, 410, 200, fill="#fdf6f5", stroke=POS, sw=1.5, rx=12))
    p.append(text(675, 94, "Після зламу (≈2005 →)", size=13, color=INK, bold=True))
    rowsR = [("напруга V", "застрягла ≈ 1 В", POS),
             ("витоки (leakage)", "ростуть", POS),
             ("потужність на 1 мм²", "лізе вгору", POS),
             ("частота f", "стала ≈ 3–4 ГГц", POS),
             ("плата за транзистори", "зростає", GOLD)]
    yy = 124
    for lab, val, col in rowsR:
        p.append(text(492, yy, lab, size=11.5, color=INK, anchor="start"))
        p.append(text(860, yy, val, size=11.5, color=col, anchor="end", bold=True))
        yy += 26
    p.append(text(675, 262, "транзистори ще множаться — але всі разом увімкнути не можна",
                  size=10.2, color=POS, italic=True))

    # нижня панель — графік двох кривих
    ox, oy, aw, ah = 80, 470, 800, 150
    p.append(line(ox, oy - ah, ox, oy, color=MUTED, sw=1.6))
    p.append(line(ox, oy, ox + aw, oy, color=MUTED, sw=1.6))
    p.append(text(ox - 8, oy - ah + 4, "відносно", size=9.5, color=MUTED, anchor="end"))
    for i, yr in enumerate([1990, 2000, 2005, 2010, 2020]):
        gx = ox + aw * [0, 0.33, 0.44, 0.56, 0.83][i]
        p.append(text(gx, oy + 18, str(yr), size=10, color=MUTED))
    xk = ox + aw * 0.44     # ~2005
    p.append(line(xk, oy - ah, xk, oy, color=INK, sw=1.2, dash="4 4"))
    p.append(text(xk + 6, oy - ah + 12, "тут Деннард ламається", size=10, color=INK, anchor="start", bold=True))
    # частота ядра: росте до 2005, тоді плато
    fpts = [(0, 0.78), (0.44, 0.30), (0.6, 0.27), (0.83, 0.27), (1, 0.27)]
    poly = ["%.1f,%.1f" % (ox + aw * fx, oy - ah * (1 - fy)) for fx, fy in fpts]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(poly), NEG))
    p.append(text(ox + aw * 0.6, oy - ah * 0.78, "частота ядра", size=10.5, color=NEG, anchor="start", bold=True))
    # щільність потужності: рівна до 2005, тоді вгору
    dpts = [(0, 0.32), (0.44, 0.32), (0.7, 0.55), (1, 0.85)]
    poly2 = ["%.1f,%.1f" % (ox + aw * fx, oy - ah * fy) for fx, fy in dpts]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(poly2), POS))
    p.append(text(ox + aw * 0.72, oy - ah * 0.62, "щільність потужності", size=10.5, color=POS, anchor="start", bold=True))
    p.append(text(ox + aw * 0.06, oy - ah * 0.40, "поки V падала — рівна", size=9.6, color=POS, anchor="start"))
    render(os.path.join(OUT, "dennard.svg"), W, H, *p,
           title="Масштабування Деннарда: коли менший транзистор був задарма")


# ── kinks: що насичується, а що триває ───────────────────────────────────────
# Ідея: «кінець закону Мура» — це відмова бонусів, а не зупинка лінії
# транзисторів. Число транзисторів іде вгору; частота й одне ядро — на плато;
# натомість угору пішли ядра й спецблоки.

def fig_kinks():
    W, H = 920, 430
    p = []
    rows = [
        ("Транзисторів на чіп", "росте далі (хай і повільніше)", FIELD, "up"),
        ("Тактова частота", "стала ≈ з 2005 (упёрлася в потужність)", POS, "plateau"),
        ("Швидкодія одного ядра", "майже стала (запас вичерпано)", POS, "plateau"),
        ("Кількість ядер", "пішла вгору — відповідь на плато", NEG, "late"),
        ("Спецблоки + чиплети", "беруть на себе ефективність", "#7a3ea8", "late"),
    ]
    lab_w = 268
    gx0, gw = 300, 600
    y = 96
    rh = 60
    xk = gx0 + gw * 0.44      # ~2005
    for head, sub, col, kind in rows:
        p.append(text(40, y + 4, head, size=12.5, color=INK, anchor="start", bold=True))
        p.append(text(40, y + 21, sub, size=10, color=col, anchor="start", italic=True))
        # міні-доріжка
        ty, th = y - 14, 40
        p.append(rect(gx0, ty, gw, th, fill="#fafafa", stroke="#e4e4e4", sw=1.1, rx=6))
        p.append(line(xk, ty, xk, ty + th, color=MUTED, sw=1.0, dash="3 3"))
        base = ty + th - 7
        top = ty + 7
        if kind == "up":
            pts = [(0, base), (1, top)]
        elif kind == "plateau":
            pts = [(0, base), (0.44, top + 4), (0.5, top + 2), (1, top + 2)]
        elif kind == "late":
            pts = [(0, base), (0.44, base), (1, top)]
        poly = ["%.1f,%.1f" % (gx0 + gw * fx, fy) for fx, fy in pts]
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(poly), col))
        p.append(circle(gx0 + gw, pts[-1][1], 3.6, fill=col, stroke=col, sw=0))
        y += rh

    p.append(text(gx0, y - 4, "1990", size=10.5, color=MUTED))
    p.append(text(xk, y - 4, "2005", size=10.5, color=MUTED))
    p.append(text(gx0 + gw, y - 4, "2024", size=10.5, color=MUTED))
    p.append(text(xk, y + 14, "кінець масштабування Деннарда", size=11, color=INK, bold=True))
    render(os.path.join(OUT, "kinks.svg"), W, H, *p,
           title="«Кінець закону Мура» — це відмова бонусів, не зупинка лінії")


if __name__ == "__main__":
    fig_value_chain()
    fig_fab_cost()
    fig_models()
    fig_idm_vs_split()
    fig_cap_table()
    fig_who_was_first()
    fig_moore_line()
    fig_dennard()
    fig_kinks()
    print("OK: 9 figures (3 article + 3 hist + 3 math)")
