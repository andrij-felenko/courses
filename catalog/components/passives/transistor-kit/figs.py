# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Набір транзисторів (TO-92)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

PLASTIC = "#1f2a37"   # чорний корпус TO-92
LEG = "#8a8f98"       # металева ніжка


def to92(f, cx, top, labels, w=104, h=74):
    """Намалювати корпус TO-92 (пласким боком до глядача) з трьома підписаними
    ніжками. cx — центр корпусу по X; top — верх плаского боку по Y;
    labels — трійка підписів зліва направо (напр. ('E','B','C'))."""
    # напівкругле тіло: прямокутна нижня частина + зрізаний верх (пласке лице)
    x = cx - w / 2
    body = ('<path d="M %.1f %.1f '
            'L %.1f %.1f '
            'A %.1f %.1f 0 0 1 %.1f %.1f '
            'L %.1f %.1f '
            'Z" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
                x, top + h,                      # низ-ліво
                x, top + 16,                     # ліво-верх (початок дуги)
                w / 2, w / 2, x + w, top + 16,   # дуга по верху
                x + w, top + h,                  # низ-право
                PLASTIC, INK))
    f.append(body)
    # пласке лице — світла смуга-натяк
    f.append(text(cx, top + h - 12, "пласке лице", size=9, color="#c7ccd4"))
    # три ніжки
    xs = [cx - w * 0.30, cx, cx + w * 0.30]
    for i, (px, lab) in enumerate(zip(xs, labels)):
        f.append(line(px, top + h, px, top + h + 34, color=LEG, sw=3))
        f.append(circle(px, top + h + 34, 3, fill=LEG, stroke="none", sw=0))
        # підпис виводу під ніжкою
        col = POS if lab in ("C", "D") else (NEG if lab in ("E", "S") else FIELD)
        f.append(text(px, top + h + 52, lab, size=15, bold=True, color=col))
        # номер ніжки
        f.append(text(px, top + h + 68, str(i + 1), size=9, color=MUTED))


# ── 1. Розводка TO-92: одна форма — РІЗНІ виводи в різних родин ────────────────
def fig_pinouts():
    W, H = 860, 470
    f = [text(W / 2, 30, "Один корпус — різні виводи: пласким боком до себе, зліва направо",
              size=15.5, bold=True)]

    top = 96
    cols = [
        (150, ("E", "B", "C"), "2N3904 · 2N2222", "PN2222 · S8050", NEG),
        (430, ("C", "B", "E"), "BC547 · BC557", "уся BC-серія", POS),
        (710, ("S", "G", "D"), "2N7000", "N-канал MOSFET", FIELD),
    ]
    for cx, labs, name, sub, accent in cols:
        to92(f, cx, top, labs)
        f.append(text(cx, top - 26, name, size=12.5, bold=True))
        f.append(text(cx, top - 10, sub, size=10, color=MUTED))
        # рамка-порядок під колонкою
        order = "-".join(labs)
        b, bw, bh = textbox(cx, top + 200, order, size=13, bold=True,
                            fill="#f4f6f8", stroke=accent, min_w=118)
        f.append(b)

    # вертикальні роздільники між колонками
    for sx in (290, 570):
        f.append(line(sx, top - 34, sx, top + 178, color="#e3e6ea", sw=1.2))

    warn, _, _ = textbox(W / 2, 410,
                         "Та сама «пігулка» бреше: 2N3904 — це E·B·C, BC547 — дзеркальне C·B·E, MOSFET — S·G·D.",
                         size=12, bold=True, fill="#fdecea", stroke=POS, min_w=720)
    f.append(warn)
    hint, _, _ = textbox(W / 2, 448,
                         "Перш ніж паяти чужу «заміну» — звірся з даташитом саме цього номера, не з сусіднього.",
                         size=11, fill=FILL, stroke=LINE, min_w=720)
    f.append(hint)
    render(os.path.join(IMG, "pinouts.svg"), W, H, *f)


# ── 2. Канонічний ключ низом (low-side switch) на NPN ─────────────────────────
def fig_switch():
    W, H = 900, 540
    f = [text(W / 2, 30, "Транзистор як ключ: слабкий вивід МК керує сильним навантаженням",
              size=15, bold=True)]

    # шина живлення +V угорі
    vy = 74
    f.append(line(120, vy, 700, vy, color=POS, sw=2.4))
    f.append(text(710, vy + 4, "+V", size=13, bold=True, color=POS, anchor="start"))

    # навантаження (котушка/реле/LED) між +V і колектором
    lx = 470
    load_y0, load_y1 = vy, 210
    f.append(line(lx, load_y0, lx, load_y0 + 20, color=INK, sw=1.8))
    b, bw, bh = textbox(lx, (load_y0 + 20 + load_y1) / 2,
                        "навантаження\n(реле, лампа,\nмотор)", size=11,
                        fill="#eef2f8", stroke=INK, min_w=140)
    f.append(b)
    f.append(line(lx, (load_y0 + 20 + load_y1) / 2 + bh / 2, lx, load_y1, color=INK, sw=1.8))

    # діод-гасник паралельно навантаженню (для індуктивних)
    dx = 640
    f.append(line(dx, load_y0, dx, load_y0 + 14, color=MUTED, sw=1.6))
    f.append(line(dx, load_y1, dx, load_y1 - 14, color=MUTED, sw=1.6))
    # трикутник діода (катод угору, до +V)
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.6"/>' % (
        dx - 9, load_y0 + 60, dx + 9, load_y0 + 60, dx, load_y0 + 44, MUTED))
    f.append(line(dx - 9, load_y0 + 44, dx + 9, load_y0 + 44, color=MUTED, sw=1.8))  # смуга катода
    f.append(line(dx, load_y0 + 14, dx, load_y0 + 44, color=MUTED, sw=1.6))
    f.append(line(dx, load_y0 + 60, dx, load_y1 - 14, color=MUTED, sw=1.6))
    f.append(text(dx + 16, (load_y0 + load_y1) / 2, "гасник", size=10, color=MUTED, anchor="start"))
    f.append(text(dx + 16, (load_y0 + load_y1) / 2 + 15, "(індуктивне)", size=9, color=MUTED, anchor="start"))
    # з'єднання гасника з шинами
    f.append(line(lx, load_y0, dx, load_y0, color=POS, sw=1.4))

    # транзистор: колектор зверху, емітер знизу, база — зліва
    tcx, tcy = lx, 300
    f.append(circle(tcx, tcy, 46, fill="#fafbfc", stroke=INK, sw=1.8))
    f.append(text(tcx, tcy - 22, "NPN", size=11, bold=True, color=MUTED))
    # вертикальна «база»-планка всередині
    f.append(line(tcx - 8, tcy - 26, tcx - 8, tcy + 26, color=INK, sw=2.6))
    # колектор (вгору) і емітер (вниз) до планки
    f.append(line(tcx + 22, tcy - 24, tcx - 8, tcy - 8, color=INK, sw=1.8))
    f.append(line(tcx + 22, tcy + 24, tcx - 8, tcy + 8, color=INK, sw=1.8))
    # стрілка емітера (NPN — від бази назовні)
    f.append(arrow(tcx - 2, tcy + 4, tcx + 20, tcy + 20, color=INK, sw=1.6))
    # вивід колектора вгору до навантаження
    f.append(line(tcx + 22, tcy - 24, tcx + 22, load_y1, color=INK, sw=1.8))
    f.append(line(tcx + 22, load_y1, lx, load_y1, color=INK, sw=1.8))
    f.append(text(tcx + 34, tcy - 26, "C", size=12, bold=True, color=POS))
    # вивід емітера вниз до землі
    emit_y = 430
    f.append(line(tcx + 22, tcy + 24, tcx + 22, emit_y, color=INK, sw=1.8))
    f.append(text(tcx + 34, tcy + 30, "E", size=12, bold=True, color=NEG))

    # ланцюг бази: МК → резистор → база
    mcx, mcy = 110, tcy
    f.append(rect(mcx - 60, mcy - 34, 120, 68, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(mcx, mcy - 8, "GPIO", size=12, bold=True))
    f.append(text(mcx, mcy + 10, "МК", size=10, color=MUTED))
    # провід до резистора бази
    rbx0, rbx1 = 220, 320
    f.append(line(mcx + 60, mcy, rbx0, mcy, color=INK, sw=1.7))
    f.append(rect(rbx0, mcy - 10, rbx1 - rbx0, 20, fill="#fff6e5", stroke="#b8860b", sw=1.5, rx=4))
    f.append(text((rbx0 + rbx1) / 2, mcy + 4, "Rb", size=11, bold=True, color="#8a6d00"))
    f.append(text((rbx0 + rbx1) / 2, mcy - 18, "1 кОм", size=10, color="#8a6d00"))
    # від резистора до бази
    f.append(line(rbx1, mcy, tcx - 8, mcy, color=INK, sw=1.7))
    f.append(text(tcx - 24, mcy - 10, "B", size=12, bold=True, color=FIELD))

    # шина землі
    gy = emit_y
    f.append(line(mcx, mcy + 34, mcx, gy, color=INK, sw=1.7))
    f.append(line(mcx, gy, tcx + 22, gy, color=INK, sw=1.7))
    # символ землі
    gx = (mcx + tcx + 22) / 2
    f.append(line(gx, gy, gx, gy + 14, color=INK, sw=2))
    f.append(line(gx - 16, gy + 14, gx + 16, gy + 14, color=INK, sw=2.4))
    f.append(line(gx - 10, gy + 20, gx + 10, gy + 20, color=INK, sw=2.4))
    f.append(line(gx - 5, gy + 26, gx + 5, gy + 26, color=INK, sw=2.4))
    f.append(text(gx + 26, gy + 20, "GND", size=11, bold=True, color=MUTED, anchor="start"))

    note2, _, _ = textbox(W / 2, 486,
                          "Струм ллється колектором→емітером; GPIO через Rb лише «прочиняє» базу.",
                          size=10.5, fill="#eef6ef", stroke=FIELD, min_w=760)
    f.append(note2)
    note, _, _ = textbox(W / 2, 520,
                         "Навантаження — між «+» і колектором; емітер — на землю; база — через Rb від GPIO.",
                         size=11, fill=FILL, stroke=LINE, min_w=760)
    f.append(note)
    render(os.path.join(IMG, "switch.svg"), W, H, *f)


# ── 3. Ланцюг підбору базового резистора (для proj-вставки) ───────────────────
def fig_rb_flow():
    W, H = 900, 430
    f = [text(W / 2, 30, "Підбір базового резистора: від струму навантаження до опору",
              size=15, bold=True)]

    # три кроки-картки в ряд + стрілки між ними; увесь підпис — ВСЕРЕДИНІ картки
    # (окремих плаваючих написів нема, тож жодна лінія їх не ріже)
    y = 145
    cxs = [155, 405, 655]
    labels = [
        ("Iнав\nструм крізь\nнавантаження", "#eef2f8", INK),
        ("Iнав ÷ hFE\nструм бази\n«впритул»", "#eef6ef", FIELD),
        ("× 3…10\nструм бази\nз запасом", "#fff6e5", "#b8860b"),
    ]
    card_h = 0
    for cx, (body, fill, accent) in zip(cxs, labels):
        b, bw, card_h = textbox(cx, y, body, size=12.5, bold=True, fill=fill,
                                stroke=accent, min_w=160)
        f.append(b)
    half = 90  # півширина картки з запасом на стрілку між ними
    f.append(arrow(cxs[0] + half, y, cxs[1] - half, y, color=INK, sw=2))
    f.append(arrow(cxs[1] + half, y, cxs[2] - half, y, color=INK, sw=2))

    # фінальний крок — закон Ома, широкою рамкою нижче по центру; від третьої
    # картки веде Г-подібний провід донизу-до-центру, повз усі написи
    fy = 305
    b, bw, oh = textbox(W / 2, fy, "Rb = (Vgpio − Vbe) ÷ Iбаза",
                        size=17, bold=True, fill="#f4f6f8", stroke=POS, min_w=420)
    midy = (y + card_h / 2 + fy - oh / 2) / 2
    f.append(line(cxs[2], y + card_h / 2 + 4, cxs[2], midy, color=INK, sw=2))
    f.append(line(cxs[2], midy, W / 2, midy, color=INK, sw=2))
    f.append(arrow(W / 2, midy, W / 2, fy - oh / 2 - 4, color=INK, sw=2))
    f.append(b)  # рамку Ома малюємо ПІСЛЯ стрілки, щоб стрілка впиралась у край, не в текст

    note, _, _ = textbox(W / 2, 388,
                         "Vbe ≈ 0.7 В; округляй Rb УНИЗ до ходового номіналу — менший опір дає більший струм бази, ще глибше насичення.",
                         size=11, fill=FILL, stroke=LINE, min_w=820)
    f.append(note)
    render(os.path.join(IMG, "rb-flow.svg"), W, H, *f)


# ── 4. Комплементарна пара: низ (NPN) vs верх (PNP) і полярність коду ──────────
def fig_complementary():
    W, H = 900, 470
    f = [text(W / 2, 30, "Дві половини: NPN тримає низ, PNP — верх; код керує ними НАВПАКИ",
              size=15, bold=True)]

    # ── ліва панель: NPN low-side ──
    lx = 235
    f.append(text(lx, 66, "NPN — ключ низом", size=13, bold=True, color=NEG))
    # +V шина
    f.append(line(lx - 110, 96, lx + 110, 96, color=POS, sw=2.2))
    f.append(text(lx + 118, 100, "+V", size=12, bold=True, color=POS, anchor="start"))
    # навантаження зверху
    b, bw, bh = textbox(lx, 150, "навантаження", size=10.5, fill="#eef2f8", stroke=INK, min_w=150)
    f.append(b)
    f.append(line(lx, 96, lx, 150 - bh / 2, color=INK, sw=1.7))
    # транзистор
    tcy = 250
    f.append(circle(lx, tcy, 30, fill="#fafbfc", stroke=INK, sw=1.7))
    f.append(text(lx, tcy + 4, "NPN", size=10, bold=True, color=MUTED))
    f.append(line(lx, 150 + bh / 2, lx, tcy - 30, color=INK, sw=1.7))  # колектор
    f.append(line(lx, tcy + 30, lx, 340, color=INK, sw=1.7))           # емітер до GND
    # база зліва від GPIO
    f.append(line(lx - 92, tcy, lx - 30, tcy, color=INK, sw=1.6))
    f.append(rect(lx - 150, tcy - 12, 30, 24, fill="#fff6e5", stroke="#b8860b", sw=1.4, rx=3))
    f.append(text(lx - 135, tcy + 4, "Rb", size=9, bold=True, color="#8a6d00"))
    f.append(text(lx - 175, tcy + 4, "GPIO", size=10, bold=True, anchor="end"))
    # земля
    f.append(line(lx - 16, 340, lx + 16, 340, color=INK, sw=2.2))
    f.append(line(lx - 9, 346, lx + 9, 346, color=INK, sw=2.2))
    f.append(line(lx - 3, 352, lx + 3, 352, color=INK, sw=2.2))
    f.append(text(lx, 372, "GND", size=10, color=MUTED))
    # ярлик логіки
    b, _, _ = textbox(lx, 412, "HIGH → увімк", size=12, bold=True, fill="#eef6ef", stroke=FIELD, min_w=200)
    f.append(b)

    # роздільник
    f.append(line(W / 2, 60, W / 2, 440, color="#e3e6ea", sw=1.4))

    # ── права панель: PNP high-side ──
    rx = 665
    f.append(text(rx, 66, "PNP — ключ верхом", size=13, bold=True, color=POS))
    f.append(line(rx - 110, 96, rx + 110, 96, color=POS, sw=2.2))
    f.append(text(rx + 118, 100, "+V", size=12, bold=True, color=POS, anchor="start"))
    # транзистор зверху (емітер до +V)
    tcy2 = 170
    f.append(circle(rx, tcy2, 30, fill="#fafbfc", stroke=INK, sw=1.7))
    f.append(text(rx, tcy2 + 4, "PNP", size=10, bold=True, color=MUTED))
    f.append(line(rx, 96, rx, tcy2 - 30, color=INK, sw=1.7))  # емітер до +V
    # навантаження знизу
    b, bw2, bh2 = textbox(rx, 270, "навантаження", size=10.5, fill="#eef2f8", stroke=INK, min_w=150)
    f.append(b)
    f.append(line(rx, tcy2 + 30, rx, 270 - bh2 / 2, color=INK, sw=1.7))  # колектор до навант.
    f.append(line(rx, 270 + bh2 / 2, rx, 340, color=INK, sw=1.7))        # до GND
    # база зліва (керування через свій вузол)
    f.append(line(rx - 92, tcy2, rx - 30, tcy2, color=INK, sw=1.6))
    f.append(rect(rx - 150, tcy2 - 12, 30, 24, fill="#fff6e5", stroke="#b8860b", sw=1.4, rx=3))
    f.append(text(rx - 135, tcy2 + 4, "Rb", size=9, bold=True, color="#8a6d00"))
    f.append(text(rx - 175, tcy2 + 4, "керування", size=9.5, anchor="end"))
    # земля
    f.append(line(rx - 16, 340, rx + 16, 340, color=INK, sw=2.2))
    f.append(line(rx - 9, 346, rx + 9, 346, color=INK, sw=2.2))
    f.append(line(rx - 3, 352, rx + 3, 352, color=INK, sw=2.2))
    f.append(text(rx, 372, "GND", size=10, color=MUTED))
    b, _, _ = textbox(rx, 412, "LOW → увімк", size=12, bold=True, fill="#fdecea", stroke=POS, min_w=200)
    f.append(b)

    render(os.path.join(IMG, "complementary.svg"), W, H, *f)


# ── 5. Метал проти пластику: що TO-92 викинув заради ціни (для hist-вставки) ──
def fig_metal_vs_plastic():
    W, H = 900, 566
    f = [text(W / 2, 30,
              "Чому пластик виграв: TO-18 (метал) → TO-92 (епоксид)",
              size=15.5, bold=True)]

    top = 96
    # ── ліва колонка: металева «баночка» TO-18 ──
    lx = 210
    f.append(text(lx, top - 20, "TO-18 — металева «баночка»", size=13, bold=True))
    f.append(text(lx, top - 4, "герметик, глас-метал-шов", size=10, color=MUTED))
    # циліндрична банка з фланцем
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="50" ry="13" fill="#cfd2d7" stroke="%s" stroke-width="1.6"/>' % (lx, top + 20, INK))
    f.append(rect(lx - 50, top + 20, 100, 84, fill="#dadde1", stroke="none", sw=0, rx=0))
    f.append(line(lx - 50, top + 20, lx - 50, top + 104, color=INK, sw=1.6))
    f.append(line(lx + 50, top + 20, lx + 50, top + 104, color=INK, sw=1.6))
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="50" ry="13" fill="#c2c5cb" stroke="%s" stroke-width="1.6"/>' % (lx, top + 104, INK))
    # блиск металу
    f.append(line(lx - 26, top + 34, lx - 26, top + 92, color="#f4f6f8", sw=4))
    # ніжки
    for dx in (-16, 0, 16):
        f.append(line(lx + dx, top + 116, lx + dx, top + 152, color=LEG, sw=3))
        f.append(circle(lx + dx, top + 152, 3, fill=LEG, stroke="none", sw=0))

    # ── стрілка переходу + плашка «викинули» ──
    ar_y = top + 56
    f.append(arrow(lx + 74, ar_y, 560, ar_y, color=INK, sw=2))
    drop, _, _ = textbox(400, ar_y - 30,
                         "викинули метал\nі герметичний шов",
                         size=10.5, bold=True, fill="#fdecea", stroke=POS, min_w=170)
    f.append(drop)

    # ── права колонка: пластикова «пігулка» TO-92 ──
    rx_ = 690
    f.append(text(rx_, top - 20, "TO-92 — епоксидна «пігулка»", size=13, bold=True))
    f.append(text(rx_, top - 4, "залив смолою — і все", size=10, color=MUTED))
    to92(f, rx_, top + 8, ("E", "B", "C"))

    # ── нижня таблиця-баланс: критерій / метал / пластик ──
    by = 322
    x0, xw = 60, 780
    f.append(line(x0, by - 12, x0 + xw, by - 12, color="#e3e6ea", sw=1.2))
    cx_crit, cx_metal, cx_plast = x0 + 78, x0 + 320, x0 + 620
    f.append(text(cx_crit, by + 4, "критерій", size=10.5, bold=True, color=MUTED))
    f.append(text(cx_metal, by + 4, "TO-18 (метал)", size=10.5, bold=True))
    f.append(text(cx_plast, by + 4, "TO-92 (пластик)", size=10.5, bold=True))

    rows = [
        ("Ціна",  "дорога: метал + герметизація", NEG,
                  "копійки — просто смола",        FIELD),
        ("Тепло", "θ ≈ 83 °C/Вт, метал відводить", FIELD,
                  "гірший тепловідвід, без радіатора", POS),
        ("Захист","герметик: ні води, ні газів",   FIELD,
                  "смола — «досить» для дрібниць", MUTED),
    ]
    ry = by + 34
    for name, mval, mcol, pval, pcol in rows:
        f.append(text(cx_crit, ry + 5, name, size=11.5, bold=True))
        f.append(fitbox(x0 + 168, ry - 15, 292, 32, mval, size=10,
                        fill="#f6f8fa", stroke=mcol))
        f.append(fitbox(x0 + 470, ry - 15, 302, 32, pval, size=10,
                        fill="#f6f8fa", stroke=pcol))
        ry += 48

    verdict, _, _ = textbox(W / 2, ry + 10,
                            "Пластик програв у теплі й герметичності — та виграв ціною; для дрібносигнальних це і вирішило.",
                            size=11.5, bold=True, fill="#eef6ef", stroke=FIELD, min_w=800)
    f.append(verdict)
    render(os.path.join(IMG, "metal-vs-plastic.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pinouts()
    fig_switch()
    fig_rb_flow()
    fig_complementary()
    fig_metal_vs_plastic()
    print("OK: 5 figures ->", IMG)
