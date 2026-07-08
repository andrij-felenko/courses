# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_with_without():
    """Ліворуч: чужі поняття протікають у модель і псують. Праворуч: шар боронить."""
    W, H = 900, 470
    f = []

    # заголовки колонок
    f.append(text(225, 56, "Без шару", size=17, bold=True, color=POS))
    f.append(text(675, 56, "Із шаром", size=17, bold=True, color=FIELD))
    f.append(line(450, 74, 450, H - 24, color=MUTED, sw=1, dash="4 4"))

    # ── ЛІВА колонка: CRM -> прямо в модель, псування ──────────────────────
    b, _, _ = textbox(225, 118, "Чужий CRM", size=13, bold=True,
                      fill="#fdecea", stroke=POS, min_w=150)
    f.append(b)
    # чужі поняття як ярлики
    b, _, _ = textbox(225, 178, "SKU з рисками\nмагічне «7»\nqty < 0", size=11,
                      fill="#fdecea", stroke=POS, min_w=160)
    f.append(b)
    # стрілки прямо в модель
    f.append(arrow(225, 208, 225, 268, color=POS))
    # модель — отруєна
    mb, mw, mh = textbox(225, 330, "Модель складу", size=13, bold=True,
                         fill="#fbe4e0", stroke=POS, min_w=230)
    f.append(mb)
    # чужі поняття всередині моделі
    b, _, _ = textbox(225, 388, "…тепер знає про\n«резерв деінде»", size=11,
                      color=POS, fill="#fbe4e0", stroke=POS, min_w=200)
    f.append(b)
    f.append(text(225, 438, "поняття протекли — псування", size=11,
                  italic=True, color=POS))

    # ── ПРАВА колонка: CRM -> ACL -> чиста модель ──────────────────────────
    b, _, _ = textbox(675, 118, "Чужий CRM", size=13, bold=True,
                      fill="#fdecea", stroke=POS, min_w=150)
    f.append(b)
    b, _, _ = textbox(675, 178, "SKU з рисками\nмагічне «7»\nqty < 0", size=11,
                      fill="#fdecea", stroke=POS, min_w=160)
    f.append(b)
    f.append(arrow(675, 208, 675, 246, color=MUTED))
    # шар
    b, _, _ = textbox(675, 270, "ACL — перекладач", size=13, bold=True,
                      fill="#eaf0fd", stroke=NEG, min_w=240)
    f.append(b)
    # відкинуте вбік
    b, _, _ = textbox(838, 270, "чуже\nбез пари →\nвідбито", size=10,
                      color=MUTED, fill=BG, stroke=MUTED, min_w=0)
    f.append(b)
    f.append(arrow(675, 292, 675, 330, color=FIELD))
    # чиста модель
    mb, mw, mh = textbox(675, 358, "Модель складу", size=13, bold=True,
                         fill="#e7f6ec", stroke=FIELD, min_w=230)
    f.append(mb)
    b, _, _ = textbox(675, 414, "Товар · Повернення\nлегальний статус", size=11,
                      color=FIELD, fill="#e7f6ec", stroke=FIELD, min_w=210)
    f.append(b)
    f.append(text(675, 452, "усередині — лише рідна мова", size=11,
                  italic=True, color=FIELD))

    render(os.path.join(IMG, 'with-without-acl.svg'), W, H, *f)


def fig_directions():
    """Асиметрія перекладу: всередину — народити своє поняття; назовні — одягнути в чуже."""
    W, H = 900, 360
    f = []

    # три вертикальні зони: чужий світ | шар | твій світ
    f.append(text(150, 44, "Чужий світ", size=15, bold=True, color=POS))
    f.append(text(450, 44, "Антикорупційний шар", size=15, bold=True, color=NEG))
    f.append(text(750, 44, "Твоя модель", size=15, bold=True, color=FIELD))

    # рамка шару по центру
    f.append(rect(360, 70, 180, 250, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))

    # чужий світ — блок
    b, _, _ = textbox(150, 130, "CRM API\nSKU, «7», qty<0", size=11,
                      fill="#fdecea", stroke=POS, min_w=180)
    f.append(b)
    # твій світ — блок
    b, _, _ = textbox(750, 130, "Order, Product\nчисті поняття", size=11,
                      fill="#e7f6ec", stroke=FIELD, min_w=180)
    f.append(b)

    # напрямок УСЕРЕДИНУ (верхній рядок)
    f.append(arrow(240, 130, 358, 130, color=INK))
    f.append(text(450, 118, "усередину", size=12, bold=True, color=NEG))
    f.append(text(450, 138, "народити своє з чужого", size=10, color=MUTED))
    f.append(arrow(542, 130, 660, 130, color=FIELD))

    # напрямок НАЗОВНІ (нижній рядок)
    f.append(arrow(660, 250, 542, 250, color=INK))
    f.append(text(450, 238, "назовні", size=12, bold=True, color=NEG))
    f.append(text(450, 258, "одягнути своє в чуже", size=10, color=MUTED))
    f.append(arrow(358, 250, 240, 250, color=POS))

    # підпис у центрі шару — служить одній стороні
    f.append(text(450, 300, "володіє двома мовами —", size=10, italic=True, color=NEG))

    render(os.path.join(IMG, 'acl-directions.svg'), W, H, *f)


def fig_spectrum():
    """Спектр кооперації Еванса: від найтіснішого злиття до найоборонішого ACL.
    Ілюструє hist-acl-origin.md — де ACL стоїть серед сусідів по карті контекстів."""
    W, H = 960, 470
    f = []

    # ── заголовок ──
    f.append(text(480, 34, "Спектр кооперації між контекстами (за Евансом)",
                  size=16, bold=True, color=INK))
    f.append(text(480, 56, "від найтіснішого злиття мов ліворуч — до найоборонішого перекладу праворуч",
                  size=11, italic=True, color=MUTED))

    # ── горизонтальна вісь, посаджена нижче, щоб дати місце підписам згори ──
    y = 210
    f.append(arrow(80, y, 880, y, color=MUTED, sw=2))
    # полюси осі — біля самих кінців, врівень з віссю
    f.append(text(80, y + 24, "тісно", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(880, y + 24, "нарізно", size=11, bold=True, color=POS, anchor="end"))

    # п'ять зупинок: підпис-рамка НАД віссю, коротка суть ПІД віссю
    stops = [
        (170, "Спільне ядро",           "ділимо шматок\nмоделі разом",   FIELD),
        (330, "Замовник—\nпостачальник", "нерівність,\nале з голосом",   FIELD),
        (500, "Конформіст",             "беремо чужу\nмодель як є",       MUTED),
        (680, "Антикорупційний\nшар",   "переклад +\nоборона межі",       NEG),
        (830, "Окремі шляхи",           "розрив\nнавмисне",               POS),
    ]
    for x, top, bot, col in stops:
        f.append(circle(x, y, 6, fill=col, stroke=col))
        # назва — рамка над віссю (низ рамки ~ y-46, верх ~ y-80: чисто під заголовком)
        b, bw, bh = textbox(x, y - 62, top, size=11, bold=True,
                            color=col, fill=BG, stroke=col, min_w=118)
        f.append(b)
        # тонкий поводок від рамки до точки на осі
        f.append(line(x, y - 62 + bh / 2, x, y - 8, color=col, sw=1, dash="3 3"))
        # суть — під віссю
        f.append(mtext(x, y + 46, bot.split("\n"), size=10, color=MUTED, lh=1.3))

    # ── виноска: де саме ACL і чим він відрізняється від сусіда-конформіста ──
    fy = 340
    f.append(rect(80, fy, 800, 104, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=10))
    f.append(text(480, fy + 28,
                  "Конформіст і ACL — обидва для випадку «ти внизу за течією, чужий велетень тобі непідвладний».",
                  size=12, color=INK))
    f.append(text(480, fy + 54,
                  "Конформіст здається — впускає чужу модель усередину. ACL б'ється — тримає перекладача на межі",
                  size=12, color=INK))
    f.append(text(480, fy + 80,
                  "й не пускає чужі поняття далі. Той самий стик — протилежна відповідь.",
                  size=12, color=INK))

    render(os.path.join(IMG, 'cooperation-spectrum.svg'), W, H, *f)


def fig_pipeline():
    """Конвеєр ACL: фасад → перекладач → (відбій вниз) → межа домену → порт.
    Ілюструє proj-build-acl.md — чотири ролі шару на одному потоці."""
    W, H = 980, 430
    f = []

    # рамка шару, що охоплює фасад + перекладач + відбій
    f.append(rect(150, 148, 470, 232, fill="#f4f7ff", stroke=NEG, sw=1.6, rx=12))
    f.append(text(385, 174, "Антикорупційний шар", size=13, bold=True, color=NEG))

    # ── чужий CRM ────────────────────────────────────────────────────────
    b, _, _ = textbox(80, 250, "Чужий\nCRM", size=13, bold=True,
                      fill="#fdecea", stroke=POS, min_w=90)
    f.append(b)

    # ── фасад ────────────────────────────────────────────────────────────
    b, _, _ = textbox(285, 236, "Фасад", size=13, bold=True,
                      fill="#eaf0fd", stroke=NEG, min_w=150)
    f.append(b)
    f.append(text(285, 290, "мережа · сторінки · ретрай", size=10, color=MUTED))
    f.append(text(285, 306, "повертає CrmOrderDto", size=10, color=MUTED))

    # ── перекладач ───────────────────────────────────────────────────────
    b, _, _ = textbox(510, 236, "Перекладач", size=13, bold=True,
                      fill="#eaf0fd", stroke=NEG, min_w=150)
    f.append(b)
    f.append(text(525, 290, "SKU → Product", size=10, color=MUTED))
    f.append(text(525, 306, "qty · статус", size=10, color=MUTED))

    # ── межа домену (пунктир) + домен ────────────────────────────────────
    # лінію починаємо НИЖЧЕ підпису, щоб вертикаль не різала текст
    f.append(line(725, 140, 725, 388, color=MUTED, sw=1.4, dash="5 5"))
    f.append(text(700, 122, "межа домену", size=10, italic=True,
                  color=MUTED, anchor="end"))
    b, _, _ = textbox(865, 236, "Домен\nOrderService", size=13, bold=True,
                      fill="#e7f6ec", stroke=FIELD, min_w=150)
    f.append(b)
    f.append(text(865, 300, "лише порт OrderSource", size=10,
                  italic=True, color=FIELD))

    # ── головний потік стрілками ─────────────────────────────────────────
    f.append(arrow(126, 250, 208, 250, color=INK))
    f.append(arrow(363, 250, 432, 250, color=INK))
    f.append(text(397, 232, "сирий DTO", size=9, color=MUTED))
    f.append(arrow(588, 250, 782, 250, color=FIELD))
    f.append(text(668, 232, "чистий Order", size=10, bold=True, color=FIELD))

    # ── відбій вниз (від лівого низу перекладача, повз підписи) ───────────
    f.append(arrow(470, 264, 470, 338, color=POS))
    b, _, _ = textbox(470, 360, "UnsupportedByModel — відбій", size=10,
                      color=POS, fill="#fdecea", stroke=POS, min_w=0)
    f.append(b)

    render(os.path.join(IMG, 'acl-pipeline.svg'), W, H, *f)


if __name__ == '__main__':
    fig_with_without()
    fig_directions()
    fig_spectrum()
    fig_pipeline()
    print("figs done")
