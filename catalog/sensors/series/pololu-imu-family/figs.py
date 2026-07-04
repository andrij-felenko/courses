# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Родина Pololu IMU (MinIMU-9 / AltIMU-10)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Дві гілки родини: MinIMU-9 (9 осей) і AltIMU-10 (+ барометр = 10) ──────
def fig_two_branches():
    W, H = 980, 470
    f = [text(W / 2, 30, "Одна карта, дві довжини: барометр робить із дев'яти осей десять",
              size=16, bold=True)]

    # спільний блок «карта Pololu»
    cx = W / 2
    b, cw, ch = textbox(cx, 92, "Карта Pololu: LDO 3.3 В · зсувачі рівня · шина I²C · крок 2.54 мм",
                        size=11.5, fill="#eef6ef", stroke=FIELD, sw=2, pad=11, bold=True, min_w=560)
    f.append(b)

    # два стовпчики давачів
    col_l = cx - 220   # MinIMU-9
    col_r = cx + 220   # AltIMU-10
    top = 168
    bh, gap = 46, 12

    def chip(cxx, y, name, sub, accent):
        bb, w, _ = textbox(cxx, y, name + "\n" + sub, size=10.5, fill="#ffffff",
                           stroke=accent, sw=1.8, pad=7, min_w=210)
        return bb

    # спільні три давачі (є в обох)
    shared = [
        ("Акселерометр + гіроскоп", "6 осей: прискорення + оберт", NEG),
        ("Магнетометр", "3 осі: напрям на північ", "#8e44ad"),
    ]
    yy = top
    for name, sub, acc in shared:
        f.append(chip(col_l, yy, name, sub, acc))
        f.append(chip(col_r, yy, name, sub, acc))
        yy += bh + gap

    # барометр — лише в AltIMU-10
    f.append(chip(col_r, yy, "Барометр (висотомір)", "тиск → висота над рівнем моря", FIELD))
    # заглушка під MinIMU (нема барометра)
    f.append(fitbox(col_l - 105, yy - bh / 2, 210, bh,
                    "барометра немає", size=10.5, fill="#f7f7f7", stroke=MUTED,
                    color=MUTED, rx=6))

    # підписи гілок
    f.append(text(col_l, top - 26, "MinIMU-9  ·  9 DoF", size=13.5, bold=True, color=NEG))
    f.append(text(col_r, top - 26, "AltIMU-10  ·  10 DoF", size=13.5, bold=True, color=FIELD))

    # лінії від спільного блоку до обох гілок
    f.append(line(cx - 90, 92 + ch / 2, col_l, top - 42, color=MUTED, sw=1.4))
    f.append(line(cx + 90, 92 + ch / 2, col_r, top - 42, color=MUTED, sw=1.4))

    # висновок
    bb, _, _ = textbox(W / 2, 432,
                       "MinIMU-9 знає, ЯК тіло повернуте й рухається. AltIMU-10 додає лише одне —"
                       "\nвисоту, — тому в дрон беруть саме її, а в робота на столі досить MinIMU-9.",
                       size=11, fill="#eef2f8", stroke=NEG, pad=10, min_w=640)
    f.append(bb)
    render(os.path.join(IMG, "two-branches.svg"), W, H, *f)


# ── 2. Що дає кожна вісь: чотири давачі й чого бракує кожному поодинці ─────────
def fig_dof_stack():
    W, H = 960, 540
    f = [text(W / 2, 30, "Навіщо чотири різні давачі: кожен знає своє, жоден — усе",
              size=16, bold=True)]

    rows = [
        ("Акселерометр", "3 осі", "де «низ», нахил (бачить тяжіння)",
         "бреше під час руху й трясіння", NEG),
        ("Гіроскоп", "3 осі", "як швидко тіло обертається",
         "кут «пливе» — похибка накопичується", "#8e44ad"),
        ("Магнетометр", "3 осі", "азимут — куди дивиться ніс",
         "збиває будь-яке залізо й струм поряд", "#c77d0a"),
        ("Барометр", "тиск", "висота над рівнем моря",
         "тільки AltIMU-10; чутливий до вітру/дверей", FIELD),
    ]

    x_name, x_gives, x_lacks = 60, 335, 640
    top, rh = 92, 96

    # шапка колонок
    f.append(text(x_name + 120, top - 14, "Давач", size=12, bold=True, color=MUTED, anchor="middle"))
    f.append(text(x_gives + 130, top - 14, "що дає", size=12, bold=True, color=FIELD, anchor="middle"))
    f.append(text(x_lacks + 130, top - 14, "чого НЕ вистачає поодинці", size=12, bold=True, color=POS, anchor="middle"))

    for i, (name, axes, gives, lacks, acc) in enumerate(rows):
        y = top + i * rh
        # назва давача
        f.append(fitbox(x_name, y, 235, 66, name + "\n(" + axes + ")",
                        size=12.5, fill="#ffffff", stroke=acc, sw=2, bold=True, color=INK))
        # що дає
        f.append(fitbox(x_gives, y, 260, 66, gives, size=11, fill="#eef6ef",
                        stroke=FIELD, color=INK))
        # чого бракує
        f.append(fitbox(x_lacks, y, 260, 66, lacks, size=11, fill="#fdecea",
                        stroke=POS, color=INK))
        # стрілки між колонками
        f.append(arrow(x_name + 235 + 4, y + 33, x_gives - 4, y + 33, color=MUTED, sw=1.6))
        f.append(arrow(x_gives + 260 + 4, y + 33, x_lacks - 4, y + 33, color=MUTED, sw=1.6))

    bb, _, _ = textbox(W / 2, 502,
                       "Саме тому дані ЗЛИВАЮТЬ фільтром: він бере сильний бік кожного давача"
                       "\nй гасить слабкий. Модуль лише чесно віддає числа — орієнтацію рахує код МК.",
                       size=11, fill="#eef2f8", stroke=NEG, pad=10, min_w=640)
    f.append(bb)
    render(os.path.join(IMG, "dof-stack.svg"), W, H, *f)


# ── 3. Еволюція начинки: від трьох функцій-чипів до двох (v3 → v5 → v6) ───────
def fig_chip_evolution():
    W, H = 980, 560
    f = [text(W / 2, 30, "Як мінялася начинка родини: два давачі-чипи замість трьох",
              size=16, bold=True)]

    # три покоління — три стовпчики
    cols = [
        (185, "v3  (2014)", "#7a869a", [
            ("Гіроскоп", "L3GD20H", NEG),
            ("Акс. + магн.", "LSM303D", "#8e44ad"),
            ("Барометр*", "LPS25H", FIELD),
        ]),
        (490, "v5  (2017)", NEG, [
            ("Акс. + гіро", "LSM6DS33", NEG),
            ("Магнетометр", "LIS3MDL", "#8e44ad"),
            ("Барометр*", "LPS25H", FIELD),
        ]),
        (795, "v6  (2020)", FIELD, [
            ("Акс. + гіро", "LSM6DSO", NEG),
            ("Магнетометр", "LIS3MDL", "#8e44ad"),
            ("Барометр*", "LPS22DF", FIELD),
        ]),
    ]

    top, bh, gap = 110, 60, 16
    for cxx, ver, vcol, chips in cols:
        f.append(text(cxx, top - 26, ver, size=14, bold=True, color=vcol))
        yy = top
        for name, part, acc in chips:
            f.append(textbox(cxx, yy, name + "\n" + part, size=11.5, fill="#ffffff",
                             stroke=acc, sw=1.8, pad=8, min_w=230)[0])
            yy += bh + gap

    # стрілки-переходи між поколіннями
    for x1, x2 in ((185 + 118, 490 - 118), (490 + 118, 795 - 118)):
        f.append(arrow(x1, top + bh, x2, top + bh, color=INK, sw=2))
    f.append(text((185 + 490) / 2, top + bh - 12, "гіро+акс+магн", size=9.5, color=MUTED))
    f.append(text((185 + 490) / 2, top + bh + 22, "склали в 2 чипи", size=9.5, color=MUTED))
    f.append(text((490 + 795) / 2, top + bh - 12, "той самий склад,", size=9.5, color=MUTED))
    f.append(text((490 + 795) / 2, top + bh + 22, "тихіші чипи", size=9.5, color=MUTED))

    # примітка про зірочку
    f.append(text(W / 2, top + 3 * (bh + gap) + 6,
                  "* барометр стоїть лише на AltIMU-10; на MinIMU-9 його нема",
                  size=10.5, color=MUTED, italic=True))

    bb, _, _ = textbox(W / 2, 522,
                       "Головна зміна — у v5: окремий гіроскоп і окремий «акс.+магн.» злилися в один"
                       "\nчип гіро+акселерометра (LSM6), а магнетометр став окремим. v6 — те саме, лише тихіше.",
                       size=11, fill="#eef2f8", stroke=NEG, pad=10, min_w=680)
    f.append(bb)
    render(os.path.join(IMG, "chip-evolution.svg"), W, H, *f)


# ── 4. Родовід чипів: хто кого замінив від покоління до покоління ─────────────
def fig_lineage_timeline():
    """Хронологія родини з конкретними партномерами по чотирьох ролях.
    Дати — веб-звірені (блог Pololu / історія бібліотек)."""
    W, H = 1180, 690
    f = [text(W / 2, 30, "Родовід родини: чотири ролі, і як мінявся чип у кожній",
              size=16, bold=True)]

    # рядки-ролі
    roles = ["Гіроскоп", "Акселерометр", "Магнетометр", "Барометр*"]
    # кольори ролей
    rc = {"Гіроскоп": NEG, "Акселерометр": "#8e44ad", "Магнетометр": "#c77d0a",
          "Барометр*": FIELD}

    # покоління: (підпис, рік, {роль: (партномер, «злитий-з»?)})
    # merged=True → рамка тягнеться на сусідній рядок (гіро+акс в одному чипі)
    gens = [
        ("v1", "2011", {
            "Гіроскоп": "L3G4200D", "Акселерометр": "LSM303DLH",
            "Магнетометр": "LSM303DLH", "Барометр*": "—"}),
        ("v2", "2012", {
            "Гіроскоп": "L3GD20", "Акселерометр": "LSM303DLHC",
            "Магнетометр": "LSM303DLHC", "Барометр*": "LPS331AP"}),
        ("v3", "2014", {
            "Гіроскоп": "L3GD20H", "Акселерометр": "LSM303D",
            "Магнетометр": "LSM303D", "Барометр*": "LPS331AP"}),
        ("v4", "2014", {
            "Гіроскоп": "L3GD20H", "Акселерометр": "LSM303D",
            "Магнетометр": "LSM303D", "Барометр*": "LPS25H"}),
        ("v5", "2016", {
            "Гіроскоп": "LSM6DS33", "Акселерометр": "LSM6DS33",
            "Магнетометр": "LIS3MDL", "Барометр*": "LPS25H"}),
        ("v6", "2022", {
            "Гіроскоп": "LSM6DSO", "Акселерометр": "LSM6DSO",
            "Магнетометр": "LIS3MDL", "Барометр*": "LPS22DF"}),
    ]

    x0 = 232           # ліва межа колонок поколінь
    colw = 152         # ширина колонки одного покоління
    row_top = 118
    rowh = 96
    label_x = 118      # центр підписів ролей зліва

    # підписи ролей зліва (широка колонка, щоб довгі слова не тислися)
    for i, role in enumerate(roles):
        yc = row_top + i * rowh + rowh / 2
        f.append(fitbox(14, row_top + i * rowh + 12, 200, rowh - 24, role,
                        size=12.5, fill="#ffffff", stroke=rc[role], sw=2,
                        bold=True, color=INK))

    # шапки колонок поколінь
    for j, (ver, year, _) in enumerate(gens):
        cx = x0 + j * colw + colw / 2
        f.append(text(cx, row_top - 42, ver, size=15, bold=True, color=INK))
        f.append(text(cx, row_top - 22, year, size=11, color=MUTED))

    # клітини: партномер кожної ролі в кожному поколінні
    for j, (ver, year, chips) in enumerate(gens):
        cx = x0 + j * colw + colw / 2
        for i, role in enumerate(roles):
            part = chips[role]
            y = row_top + i * rowh + 12
            ch = rowh - 24
            # об'єднана рамка гіро+акс, коли партномер той самий (LSM6*)
            merged = (role == "Гіроскоп" and chips["Гіроскоп"] == chips["Акселерометр"])
            skip = (role == "Акселерометр" and chips["Гіроскоп"] == chips["Акселерометр"])
            if skip:
                continue
            if merged:
                ch = 2 * rowh - 24
                lab = "гіро + акс\n(один чип)\n" + part
            else:
                lab = part
            fill = "#f7f7f7" if part in ("—",) else "#ffffff"
            col = MUTED if part in ("—",) else INK
            f.append(fitbox(cx - (colw - 16) / 2, y, colw - 16, ch, lab,
                            size=11 if not merged else 10.5,
                            fill=fill, stroke=rc[role], sw=1.6, color=col,
                            bold=(part not in ("—",))))

    # позначки двох переломів під сіткою
    # злам 1: карта висотоміра з'явилася (v2 — перший AltIMU)
    # злам 2: консолідація гіро+акс у v5
    yline = row_top + 4 * rowh + 14
    # межа v4|v5 (консолідація)
    xsplit = x0 + 5 * colw  # ліва межа колонки v5 (індекс 4) = x0+4*colw ... відкоригуємо
    xsplit = x0 + 4 * colw
    f.append(line(xsplit, row_top - 8, xsplit, row_top + 4 * rowh, color=POS, sw=2, dash="6 5"))
    f.append(fitbox(xsplit - 150, yline, 300, 40,
                    "тут v5: гіро й акс. злилися в ОДИН чип (LSM6),\nмагнетометр виїхав окремо",
                    size=10.5, fill="#fdecea", stroke=POS, color=INK))

    # межа v1|v2 (поява барометра / AltIMU)
    xbar = x0 + 1 * colw
    f.append(line(xbar, row_top + 3 * rowh - 4, xbar, row_top + 4 * rowh, color=FIELD, sw=2, dash="6 5"))
    f.append(fitbox(xbar - 96, yline + 48, 200, 34,
                    "від v2 — гілка AltIMU\n(додано барометр)",
                    size=10, fill="#eef6ef", stroke=FIELD, color=INK))

    # примітка про зірочку
    f.append(text(x0 + 3 * colw, yline + 96,
                  "* барометр стоїть лише на гілці AltIMU-10; на MinIMU-9 його немає",
                  size=10.5, color=MUTED, italic=True))

    bb, _, _ = textbox(W / 2, H - 26,
                       "Постачальник незмінний — STMicroelectronics; міняються лише номери в дужках."
                       "\nЧитайте маркування найбільшого чипа — воно й називає покоління плати.",
                       size=11, fill="#eef2f8", stroke=NEG, pad=10, min_w=720)
    f.append(bb)
    render(os.path.join(IMG, "lineage-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_branches()
    fig_dof_stack()
    fig_chip_evolution()
    fig_lineage_timeline()
    print("OK: img/two-branches.svg, img/dof-stack.svg, img/chip-evolution.svg, img/lineage-timeline.svg")
