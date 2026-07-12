# -*- coding: utf-8 -*-
"""Фігури до кроку «DH: фінал поверхні API/конфіг/розширення» (модуль 10)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

TINT_G = "#eef7f0"   # світло-зелений фон (не опубліковане / безпечне)
TINT_R = "#fdecea"   # світло-червоний фон (опубліковане / обіцяне чужим)


def fig_published_line():
    """Та сама система, одна межа: ліворуч — вільне, праворуч — обіцяне чужим (Фаулер)."""
    W, H = 1080, 560
    divx = 540
    frags = []

    # фонові панелі двох боків
    frags.append(rect(40, 64, 470, 452, fill=TINT_G, stroke=FIELD, sw=1.4))
    frags.append(rect(570, 64, 470, 452, fill=TINT_R, stroke=POS, sw=1.4))

    # межа публікації
    frags.append(text(divx, 54, "межа публікації", size=13, bold=True, color=INK))
    frags.append(line(divx, 66, divx, 512, color=INK, sw=2.4, dash="2,7"))

    # ── ліворуч: НЕ опубліковане ──
    frags.append(text(275, 96, "НЕ ОПУБЛІКОВАНЕ", size=17, bold=True, color=FIELD))
    frags.append(mtext(275, 122, ["обидві сторони — твій код:", "зміну оновиш разом, в один коміт"],
                       size=12, color=MUTED))
    left_rows = [
        "внутрішній gRPC: реєстр ⇄ автоматизація",
        "схема бази даних",
        "значення конфігу: порт, період, лог-рівень",
        "нутрощі помилки: stack, SQL, шлях",
        "правило decide(), склад ядра",
    ]
    y = 178
    for r in left_rows:
        frags.append(text(66, y, "•  " + r, size=13, color=INK, anchor="start"))
        y += 58
    frags.append(text(275, 500, "рефактор і перейменування — безпечно", size=12,
                      color=FIELD, bold=True))

    # ── праворуч: ОПУБЛІКОВАНЕ ──
    frags.append(text(805, 96, "ОПУБЛІКОВАНЕ", size=17, bold=True, color=POS))
    frags.append(mtext(805, 122, ["чужі сперлися — не відкличеш;",
                                  "живе, поки живий найповільніший клієнт"],
                       size=12, color=MUTED))
    right_rows = [
        "публічний REST-DTO v1: temperature{value,unit}, at",
        "формат ідентифікатора пристрою (device-id)",
        "топік телеметрії  dh/home/{id}/{dev}/reading",
        "конверт помилки + стабільні коди",
        "контракт розширення: DevicePort, payload вебхука",
    ]
    y = 178
    for r in right_rows:
        frags.append(text(590, y, "•  " + r, size=13, color=INK, anchor="start"))
        y += 58
    frags.append(text(805, 500, "будь-яка зміна форми — злам або нова версія", size=12,
                      color=POS, bold=True))

    render(os.path.join(IMG, "published-line.svg"), W, H, *frags,
           title="Одна межа крізь систему: що змінюєш вільно — і що вже обіцяв чужим")


def fig_one_change_trace():
    """Одна продуктова зміна тече крізь поверхню — кожен інструмент модуля раз, у своїй смузі."""
    W, H = 1040, 648
    cx = 520
    frags = []

    # верх — продуктова потреба
    top, tw, th = textbox(cx, 74, "Продукт: показувати спожиту потужність (power)",
                          size=14, fill=BG, stroke=MUTED, sw=1.6)
    frags.append(top)
    frags.append(arrow(cx, 74 + th / 2, cx, 128, color=MUTED, sw=2))

    # вертикальний підпис
    frags.append(vtext(38, 360, "одна зміна", size=12, color=MUTED))

    rungs = [
        ("DTO:  + power{watts, at}",
         "адитивно (expand–contract)", "→ без версії · api-evolution-dh"),
        ("Розширення:  новий адаптер за DevicePort",
         "курований контракт розширення", "· extensibility-choice"),
        ("Помилки:  код device.capability_unsupported",
         "у ВІДКРИТОМУ enum", "старий клієнт → загальне · api-error-contract"),
        ("Секрет:  токен партнера-споживача",
         "вузька область + ротація", "· config-secrets-boundary"),
        ("Викочування:  feature-flag по домах",
         "спершу вузько, тоді ширше", "· feature-flags"),
    ]
    x0, w = 96, 848
    ry = 132
    step = 78
    for i, (facet, disc, src) in enumerate(rungs):
        y = ry + i * step
        frags.append(rect(x0, y, w, 60, fill=FILL, stroke=LINE, sw=1.4))
        frags.append(text(x0 + 20, y + 36, facet, size=14, color=INK, bold=True, anchor="start"))
        frags.append(mtext(x0 + w - 18, y + 24, [disc, src], size=12, color=MUTED,
                           anchor="end", lh=1.25))
        if i < len(rungs) - 1:
            frags.append(arrow(cx, y + 60, cx, y + step, color=MUTED, sw=1.7))

    # низ — версія ціла
    ylast = ry + (len(rungs) - 1) * step + 60
    frags.append(arrow(cx, ylast, cx, ylast + 22, color=FIELD, sw=2.2))
    bot, bw, bh = textbox(cx, ylast + 52,
                          "v1 лишилась цілою — жоден чужий клієнт не зламався\n"
                          "версію бережемо на наскрізний злам",
                          size=13, fill=TINT_G, stroke=FIELD, sw=1.8, bold=True)
    frags.append(bot)

    render(os.path.join(IMG, "one-change-trace.svg"), W, H, *frags,
           title="Одна зміна крізь поверхню — кожен інструмент модуля раз, у своїй смузі")


def vtext(x, y, s, size=12, color=MUTED):
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">%s</text>'
            % (x, y, FONT, size, color, x, y, esc(s)))


def fig_published_lineage():
    """Родовід межі опубліковане/неопубліковане: власність коду → Фаулер → закон Гайрама."""
    W, H = 1000, 780
    ax = 170
    frags = []

    # ── дві смуги-епохи ──
    frags.append(rect(30, 66, 950, 452, fill="#eef7f0", stroke="#cfe6d8", sw=1.2, rx=10))
    frags.append(rect(30, 536, 950, 176, fill="#fdecea", stroke="#f2cfca", sw=1.2, rx=10))
    frags.append(text(210, 96,
                      "Внесок Фаулера — ДЕ проходить межа: питання координації, а не видимості",
                      size=13, color=FIELD, bold=True, italic=True, anchor="start"))
    frags.append(text(210, 566,
                      "Механізм Гайрама — ЩО по той бік межі: спостережне стає чиєюсь опорою",
                      size=13, color=POS, bold=True, italic=True, anchor="start"))

    # ── вісь часу (згори вниз) ──
    frags.append(arrow(ax, 150, ax, 692, color=MUTED, sw=2))

    nodes = [
        (175, "кін. 1990-х", FIELD,
         "Суперечка про власність коду (XP). Сильне володіння → внутрішній\n"
         "інтерфейс стає «опублікованим»: не перейменуєш, поки власник виклику не оновить свій бік."),
        (285, "1999", FIELD,
         "«Refactoring» (Мартін Фаулер) уводить термін published interface:\n"
         "рефактор-інструмент перейменовує вільно лише в межах ОДНІЄЇ кодової бази."),
        (395, "2002", FIELD,
         "IEEE Software 19(2), с. 18–19 — «Public versus Published»:\n"
         "важить не видимість (public/private), а межа координації (published)."),
        (488, "2003", FIELD,
         "bliki «PublishedInterface» — стисле канонічне означення:\n"
         "інтерфейс, «ужитий поза кодовою базою, де його визначено»."),
        (630, "~2012 → 2020", POS,
         "Закон Гайрама (Гайрам Райт; назвав Тайтус Вінтерс, «SE at Google»):\n"
         "спостережне стає опорою. Стоїть НА межі Фаулера — не заміняє її."),
    ]
    for y, year, col, desc in nodes:
        frags.append(fitbox(205, y - 28, 762, 56, desc, size=13, pad=9,
                            fill=BG, stroke="#d7dbe0", sw=1.3))
        frags.append(text(150, y + 4, year, size=14, color=col, bold=True, anchor="end"))
        frags.append(circle(ax, y, 7.5, fill=col, stroke=col, sw=1.5))

    render(os.path.join(IMG, "published-lineage.svg"), W, H, *frags,
           title="Родовід межі: від власності коду — до закону Гайрама")


def fig_surface_guard_gate():
    """Три дисципліни модуля як три смуги одного гейта CI; будь-яка червона валить merge."""
    W, H = 1120, 560
    cx = 560
    frags = []

    # вхід: PR міняє поверхню
    pr, pw, ph = textbox(cx, 68, "PR / коміт міняє поверхню", size=13,
                         fill=BG, stroke=MUTED, sw=1.6)
    frags.append(pr)
    frags.append(arrow(cx, 68 + ph / 2, cx, 116, color=MUTED, sw=2))

    # корпус сторожа
    frags.append(rect(80, 118, 960, 352, fill=BG, stroke=INK, sw=2.2))
    frags.append(text(104, 150, "сторож опублікованої поверхні (CI)", size=15,
                      bold=True, color=INK, anchor="start"))

    lanes = [
        ("1 · схема лише РОСТЕ",
         "diff проти baseline.json — жодне поле не зникло й не змінило тип без запису",
         "адитивність"),
        ("2 · секрет не заповз у конфіг",
         "скан значень: імʼя-ключ + ентропія · посилання, а не значення",
         "конфіг проти секрета"),
        ("3 · конверт помилки стабільний",
         "{ error:{ code, message } } · коди з відкритого набору · без нутрощів",
         "помилка як контракт"),
    ]
    y = 166
    for lane_title, sub, tag in lanes:
        frags.append(rect(104, y, 912, 76, fill=FILL, stroke=LINE, sw=1.4))
        frags.append(rect(104, y, 9, 76, fill=FIELD, stroke=FIELD, sw=1, rx=0))
        frags.append(text(130, y + 30, lane_title, size=14, bold=True, color=INK, anchor="start"))
        frags.append(text(130, y + 54, sub, size=12, color=MUTED, anchor="start"))
        frags.append(text(1004, y + 30, tag, size=11, color=MUTED, anchor="end"))
        y += 90

    # розгалуження вниз до двох вердиктів
    frags.append(arrow(cx, 470, cx, 494, color=INK, sw=2))
    frags.append(line(cx, 494, 335, 508, color=INK, sw=1.6))
    frags.append(line(cx, 494, 800, 508, color=INK, sw=1.6))

    ok, _, _ = textbox(335, 524, "усі зелені → поверхня ціла, merge вільний",
                       size=12, fill=TINT_G, stroke=FIELD, sw=1.6, bold=True)
    bad, _, _ = textbox(800, 524, "хоч одна червона → CI ≠0, merge заблоковано",
                        size=12, fill=TINT_R, stroke=POS, sw=1.6, bold=True)
    frags.append(ok)
    frags.append(bad)

    render(os.path.join(IMG, "surface-guard-gate.svg"), W, H, *frags,
           title="Сторож поверхні — один гейт CI на три дисципліни модуля")


def fig_moving_baseline():
    """Рухомий знімок робить гейт театром; закомічений — стереже насправді."""
    W, H = 1120, 520
    frags = []

    def column(x0, cxx, tint, edge, head, steps, caption):
        frags.append(rect(x0, 60, 470, 400, fill=tint, stroke=edge, sw=1.4))
        frags.append(text(cxx, 96, head, size=16, bold=True, color=edge))
        ys = [148, 222, 296, 370]
        for i, (s, strong) in enumerate(steps):
            box, _, _ = textbox(cxx, ys[i], s, size=12, fill=BG,
                                stroke=(edge if strong else MUTED),
                                sw=(1.8 if strong else 1.3), bold=strong)
            frags.append(box)
            if i < len(steps) - 1:
                frags.append(arrow(cxx, ys[i] + 26, cxx, ys[i + 1] - 26,
                                   color=MUTED, sw=1.7))
        frags.append(text(cxx, 442, caption, size=12, bold=True, color=edge))

    column(60, 295, TINT_R, POS, "✗ рухомий знімок",
           [("CI регенерує baseline.json\nіз поточного коду", False),
            ("diff: поточне проти baseline", False),
            ("diff = ∅  завжди", False),
            ("зелено ЗАВЖДИ — хоч що зламай", True)],
           "гейт-театр: нічого не стереже")

    column(590, 825, TINT_G, FIELD, "✓ закомічений знімок",
           [("baseline.json у git\n(переглянутий, під підписом)", False),
            ("PR міняє поверхню →\ndiff бачить регрес", False),
            ("червоно, поки людина\nне підпише усадку", False),
            ("surface:accept — окремий\nкоміт у код-рев'ю", True)],
           "зміна поверхні — свідомий крок")

    render(os.path.join(IMG, "moving-baseline.svg"), W, H, *frags,
           title="Чому базовий знімок мусить бути закоміченим, а не згенерованим")


if __name__ == "__main__":
    fig_published_line()
    fig_one_change_trace()
    fig_published_lineage()
    fig_surface_guard_gate()
    fig_moving_baseline()
    print("OK: published-line.svg, one-change-trace.svg, published-lineage.svg, "
          "surface-guard-gate.svg, moving-baseline.svg")
