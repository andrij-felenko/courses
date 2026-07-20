# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUEFILL = "#eaf0fd"
GREENFILL = "#e8f6ee"
REDFILL = "#fdecea"
GREENFAINT = "#f4fbf7"


# ── Дві дороги народити об'єкт: конструктор проти прототипа ───────────────────
def fig_create_by_example():
    W, H = 1140, 560
    frags = []

    # роздільник посередині (не доходить до країв, щоб не різати написи)
    frags.append(line(W / 2, 96, W / 2, H - 96, color="#d0d5db", sw=1.2, dash="6,6"))

    # ═══════════ ЛІВОРУЧ: КОНСТРУКТОР ═══════════
    lcx = W / 4
    frags.append(text(lcx, 52, "Шлях конструктора", size=16, bold=True, color=NEG))
    frags.append(text(lcx, 74, "будуєш з нуля щоразу", size=12, color=MUTED))

    src, sw_, sh_ = textbox(lcx, 176,
                            ["new Shape(", "   x, y, колір, зброя,",
                             "   реакції, …десяток полів )"],
                            size=12.5, bold=True, fill=BLUEFILL, stroke=NEG,
                            sw=1.8, min_w=300)
    frags.append(src)

    frags.append(arrow(lcx, 176 + sh_ / 2, lcx, 316, color=NEG, sw=1.7))
    obj, _, oh = textbox(lcx, 348, "новий об'єкт", size=13, bold=True,
                         fill=FILL, stroke=LINE, sw=1.5, min_w=200)
    frags.append(obj)

    frags.append(text(lcx, 348 + oh / 2 + 46, "треба знати КЛАС", size=12.5, bold=True, color=INK))
    frags.append(text(lcx, 348 + oh / 2 + 68, "і перелічити всі складники", size=12, color=MUTED))

    # ═══════════ ПРАВОРУЧ: ПРОТОТИП ═══════════
    rcx = 3 * W / 4
    frags.append(text(rcx, 52, "Шлях прототипа", size=16, bold=True, color=FIELD))
    frags.append(text(rcx, 74, "кажеш: ще один такий самий", size=12, color=MUTED))

    proto, _, ph = textbox(rcx, 176,
                           ["готовий зразок", "усе вже налаштовано", "clone()  ▶"],
                           size=12.5, bold=True, fill=GREENFILL, stroke=FIELD,
                           sw=1.8, min_w=300)
    frags.append(proto)

    frags.append(arrow(rcx, 176 + ph / 2, rcx, 316, color=FIELD, sw=1.7))
    frags.append(text(rcx + 92, 262, "копія", size=11.5, italic=True, color=FIELD, anchor="start"))
    obj2, _, oh2 = textbox(rcx, 348, ["новий незалежний", "об'єкт"], size=13, bold=True,
                           fill=FILL, stroke=LINE, sw=1.5, min_w=200)
    frags.append(obj2)

    frags.append(text(rcx, 348 + oh2 / 2 + 46, "потрібен лише", size=12.5, bold=True, color=INK))
    frags.append(text(rcx, 348 + oh2 / 2 + 68, "готовий екземпляр", size=12, color=MUTED))

    # ── Нижня смуга ──────────────────────────────────────────────────────────
    frags.append(line(60, H - 74, W - 60, H - 74, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 44,
                      "Знання «як зробити ще один такий» переїхало з місця виклику всередину об'єкта.",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'create-by-example.svg'), W, H, *frags)


# ── Поверхнева проти глибокої копії: спільне вкладене проти окремого ──────────
def fig_shallow_vs_deep():
    W, H = 1020, 660
    frags = []

    # ═══════════ УГОРІ: ПОВЕРХНЕВА ═══════════
    frags.append(text(W / 2, 46, "Поверхнева копія — вкладене СПІЛЬНЕ", size=16, bold=True, color=POS))

    ox, oy = 300, 122
    cx2 = 720
    a, _, ah = textbox(ox, oy, ["оригінал", "tags  ▾"], size=12, bold=True,
                       fill=BLUEFILL, stroke=LINE, sw=1.5, min_w=180)
    frags.append(a)
    b, _, _ = textbox(cx2, oy, ["копія", "tags  ▾"], size=12, bold=True,
                      fill=BLUEFILL, stroke=LINE, sw=1.5, min_w=180)
    frags.append(b)

    sh, shw, shh = textbox(W / 2, 244, ["ОДИН спільний список", "[ «терміново» ]"],
                           size=12, bold=True, fill=REDFILL, stroke=POS, sw=1.9, min_w=250)
    frags.append(sh)
    frags.append(arrow(ox, oy + ah / 2, W / 2 - shw / 2 + 18, 244 - shh / 2, color=POS, sw=1.6))
    frags.append(arrow(cx2, oy + ah / 2, W / 2 + shw / 2 - 18, 244 - shh / 2, color=POS, sw=1.6))

    frags.append(text(W / 2, 316, "правка через будь-кого — видно й іншому (прихований баг)",
                      size=12.5, bold=True, color=POS))

    # роздільник
    frags.append(line(60, 350, W - 60, 350, color="#d0d5db", sw=1.2))

    # ═══════════ УНИЗУ: ГЛИБОКА ═══════════
    frags.append(text(W / 2, 392, "Глибока копія — вкладене ОКРЕМЕ", size=16, bold=True, color=FIELD))

    dy = 466
    a2, _, ah2 = textbox(ox, dy, ["оригінал", "tags  ▾"], size=12, bold=True,
                         fill=GREENFILL, stroke=LINE, sw=1.5, min_w=180)
    frags.append(a2)
    b2, _, _ = textbox(cx2, dy, ["копія", "tags  ▾"], size=12, bold=True,
                       fill=GREENFILL, stroke=LINE, sw=1.5, min_w=180)
    frags.append(b2)

    la, _, lah = textbox(ox, 582, ["свій список", "[ «терміново» ]"], size=12,
                         fill=GREENFAINT, stroke=FIELD, sw=1.6, min_w=200)
    frags.append(la)
    lb, _, _ = textbox(cx2, 582, ["власний список", "[ «терміново» ]"], size=12,
                       fill=GREENFAINT, stroke=FIELD, sw=1.6, min_w=200)
    frags.append(lb)
    frags.append(arrow(ox, dy + ah2 / 2, ox, 582 - lah / 2, color=FIELD, sw=1.6))
    frags.append(arrow(cx2, dy + ah2 / 2, cx2, 582 - lah / 2, color=FIELD, sw=1.6))

    frags.append(text(W / 2, 636, "клон повністю незалежний — правка нікого не зачіпає",
                      size=12.5, bold=True, color=FIELD))

    render(os.path.join(IMG, 'shallow-vs-deep.svg'), W, H, *frags)


# ── Реєстр прототипів: ключ → зразок → клон збоку ────────────────────────────
def fig_prototype_registry():
    W, H = 1160, 540
    frags = []

    frags.append(text(W / 2, 40, "Реєстр: ключ → зразок → клон", size=17, bold=True, color=INK))
    frags.append(text(W / 2, 62, "новий різновид додається реєстрацією ще одного зразка, не класом",
                      size=12.5, color=MUTED))

    # ── Контейнер-таблиця реєстру ────────────────────────────────────────────
    tx, ty, tw, th = 80, 100, 470, 250
    frags.append(rect(tx, ty, tw, th, fill=BG, stroke=INK, sw=1.8, rx=8))
    frags.append(text(tx + tw / 2, ty + 26, "реєстр:  ключ  →  налаштований зразок",
                      size=12.5, bold=True, color=INK))
    frags.append(line(tx + 12, ty + 40, tx + tw - 12, ty + 40, color="#d0d5db", sw=1))

    kx0, kx1 = tx + 12, tx + 128         # колонка ключа
    sx0, sx1 = tx + 134, tx + tw - 12    # колонка зразка
    rows = [
        ("«коло»", "Circle(0, 0, r=10)", False),
        ("«квадрат»", "Square(side=4)", False),
        ("«орк»", "Orc(hp, зброя, дроп…)", True),
    ]
    row_h = 64
    r_top = ty + 50
    ork_cy = None
    for i, (key, sample, hl) in enumerate(rows):
        ry = r_top + i * row_h
        rcy = ry + row_h / 2
        kfill = REDFILL if hl else "#eef2f7"
        sfill = GREENFAINT if hl else BG
        kst = POS if hl else LINE
        sst = FIELD if hl else "#c9ced6"
        frags.append(rect(kx0, ry + 6, kx1 - kx0, row_h - 12, fill=kfill, stroke=kst, sw=1.5 if hl else 1.1, rx=5))
        frags.append(text((kx0 + kx1) / 2, rcy + 5, key, size=12.5, bold=True, color=(POS if hl else INK)))
        frags.append(rect(sx0, ry + 6, sx1 - sx0, row_h - 12, fill=sfill, stroke=sst, sw=1.5 if hl else 1.1, rx=5))
        frags.append(text((sx0 + sx1) / 2, rcy + 5, sample, size=12, color=(FIELD if hl else INK)))
        if hl:
            ork_cy = rcy

    # ── create(«орк») знаходить зразок за ключем ──────────────────────────────
    cc, ccw, cch = textbox(tx + tw / 2, 430, "create(«орк»)", size=13, bold=True,
                           fill=BLUEFILL, stroke=NEG, sw=1.7, min_w=200)
    frags.append(cc)
    frags.append(arrow(tx + tw / 2, 430 - cch / 2, tx + tw / 2, r_top + 2 * row_h + row_h - 8, color=NEG, sw=1.5))
    frags.append(text(tx + tw / 2 + 120, 420, "1 · знайти зразок за ключем",
                      size=11.5, color=NEG, anchor="start"))

    # ── Клон збоку: незалежний новий орк ─────────────────────────────────────
    nx = 940
    newobj, nw, nh = textbox(nx, ork_cy, ["новий орк", "копія зразка,", "самостійний"],
                             size=12.5, bold=True, fill=FILL, stroke=FIELD, sw=1.7, min_w=210)
    frags.append(newobj)
    frags.append(arrow(sx1 + 4, ork_cy, nx - nw / 2 - 6, ork_cy, color=FIELD, sw=2))
    frags.append(text((sx1 + nx - nw / 2) / 2, ork_cy - 14, "2 · clone()", size=12.5, bold=True, color=FIELD))

    # ── Нижня смуга ──────────────────────────────────────────────────────────
    frags.append(text(W / 2, H - 40,
                      "Додати новий різновид — зареєструвати ще один екземпляр; жодного if чи switch за типом.",
                      size=12.5, bold=True, color=INK))

    render(os.path.join(IMG, 'prototype-registry.svg'), W, H, *frags)


# ── Що робить clone() з полем кожного роду ───────────────────────────────────
def fig_clone_field_decision():
    W, H = 1200, 540
    frags = []

    frags.append(text(W / 2, 40, "Правильний clone() — рішення для КОЖНОГО поля окремо",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 64, "реєстр тривіальний; уся істина живе тут — глибину копії обирають на кожне поле",
                      size=12.5, color=MUTED))

    c1x, c1w = 50, 430
    c2x, c2w = 490, 470
    c3x, c3w = 970, 180
    ty = 92
    hh = 44

    # заголовок таблиці
    frags.append(fitbox(c1x, ty, c1w, hh, "поле такого роду", size=13, bold=True,
                        fill="#eef2f7", stroke=INK, sw=1.4))
    frags.append(fitbox(c2x, ty, c2w, hh, "що робить коректний clone()", size=13, bold=True,
                        fill="#eef2f7", stroke=INK, sw=1.4))
    frags.append(fitbox(c3x, ty, c3w, hh, "приклад-поле", size=13, bold=True,
                        fill="#eef2f7", stroke=INK, sw=1.4))

    rows = [
        (["скаляр: число, булеве,", "незмінний рядок"],
         ["скопіювати значення", "(стається саме собою)"],
         ["hp,  name"], "#c9ced6", FILL, INK),
        (["вкладений ЗМІННИЙ", "об'єкт або список"],
         ["ГЛИБОКА копія —", "власний примірник"],
         ["loot[ ],  stats"], FIELD, GREENFILL, FIELD),
        (["незмінний вкладений", "об'єкт"],
         ["поділити (shallow) —", "безпечно й дешево"],
         ["конфіг-", "константа"], "#c9ced6", FILL, INK),
        (["живий ресурс:", "сокет, файл, лок"],
         ["НЕ копіювати: поділити", "або перевідкрити наново"],
         ["socket,  fd"], POS, REDFILL, POS),
        (["зворотне / циклічне", "посилання"],
         ["memo: та сама копія,", "а не нова гілка"],
         ["squad ↔", "member"], NEG, BLUEFILL, NEG),
    ]
    rh = 78
    for i, (kind, act, ex, accent, actfill, actcol) in enumerate(rows):
        ry = ty + hh + i * rh
        frags.append(fitbox(c1x, ry, c1w, rh - 8, kind, size=12.5, bold=True,
                            fill=BG, stroke=accent, sw=1.6, color=INK))
        frags.append(fitbox(c2x, ry, c2w, rh - 8, act, size=12.5, bold=True,
                            fill=actfill, stroke=accent, sw=1.6, color=actcol))
        frags.append(fitbox(c3x, ry, c3w, rh - 8, ex, size=12, fill=BG,
                            stroke="#c9ced6", sw=1.1, color=MUTED))

    frags.append(text(W / 2, H - 20,
                      "Механізм не вгадає семантику за тебе — саме тому clone() пишуть руками там, де поля різнорідні.",
                      size=12.5, bold=True, color=INK))

    render(os.path.join(IMG, 'clone-field-decision.svg'), W, H, *frags)


# ── Глибока копія графа з циклом: таблиця memo рве рекурсію ───────────────────
def fig_deepclone_memo():
    W, H = 1200, 580
    frags = []

    frags.append(text(W / 2, 38, "Глибока копія графа з циклом: memo рве нескінченну рекурсію",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 62, "monster вказує на squad, а squad назад на monster — наївна рекурсія зациклиться",
                      size=12.5, color=MUTED))

    y1, y2 = 190, 372

    def cycle_cluster(cx, tag, prime, label_col):
        f = []
        f.append(text(cx, 110, tag, size=13.5, bold=True, color=label_col))
        m, mw, mh = textbox(cx, y1, "monster" + prime, size=13, bold=True,
                            fill=BLUEFILL, stroke=NEG, sw=1.7, min_w=150)
        s, sw2, sh2 = textbox(cx, y2, "squad" + prime, size=13, bold=True,
                             fill=GREENFILL, stroke=FIELD, sw=1.7, min_w=150)
        f.append(m)
        f.append(s)
        # донизу: monster.squad → squad
        f.append(arrow(cx - 28, y1 + mh / 2, cx - 28, y2 - sh2 / 2, color=NEG, sw=1.7))
        f.append(text(cx - 44, (y1 + y2) / 2 + 4, ".squad", size=11.5, color=NEG, anchor="end"))
        # догори: squad.members[0] → monster
        f.append(arrow(cx + 28, y2 - sh2 / 2, cx + 28, y1 + mh / 2, color=FIELD, sw=1.7))
        f.append(text(cx + 44, (y1 + y2) / 2 + 4, ".members[0]", size=11.5, color=FIELD, anchor="start"))
        return f

    # ── ліворуч: оригінал ───────────────────────────────────────────────────
    frags += cycle_cluster(210, "оригінал (граф із циклом)", "", INK)

    # ── центр: таблиця memo ──────────────────────────────────────────────────
    mtx, mty, mtw, mth = 470, 150, 260, 210
    frags.append(rect(mtx, mty, mtw, mth, fill=BG, stroke=INK, sw=1.8, rx=8))
    frags.append(text(mtx + mtw / 2, mty + 28, "memo", size=14, bold=True, color=INK))
    frags.append(text(mtx + mtw / 2, mty + 48, "оригінал  →  копія", size=12, color=MUTED))
    frags.append(line(mtx + 12, mty + 60, mtx + mtw - 12, mty + 60, color="#d0d5db", sw=1))
    frags.append(fitbox(mtx + 16, mty + 74, mtw - 32, 52, ["monster  →  monster′"],
                        size=12.5, bold=True, fill=BLUEFILL, stroke=NEG, sw=1.4, color=NEG))
    frags.append(fitbox(mtx + 16, mty + 136, mtw - 32, 52, ["squad  →  squad′"],
                        size=12.5, bold=True, fill=GREENFILL, stroke=FIELD, sw=1.4, color=FIELD))

    frags.append(text(mtx + mtw / 2, mty + mth + 26,
                      "запис ДО рекурсії", size=12.5, bold=True, color=POS))

    # стрілки: оригінал → memo → копія
    frags.append(arrow(360, y1, mtx - 8, y1 + 4, color=MUTED, sw=1.4))
    frags.append(arrow(mtx + mtw + 8, y1 + 4, 1010 - 78, y1, color=MUTED, sw=1.4))

    # ── праворуч: копія ──────────────────────────────────────────────────────
    frags += cycle_cluster(1010, "копія (цикл замкнено на СЕБЕ)", "′", FIELD)

    # ── нижня смуга ──────────────────────────────────────────────────────────
    frags.append(line(60, H - 92, W - 60, H - 92, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 64,
                      "deepClone(вузол): якщо memo вже має вузол — вернути готову копію; інакше memo.set(вузол, копія) ПЕРЕД заходом у поля.",
                      size=12.5, bold=True, color=INK))
    frags.append(text(W / 2, H - 40,
                      "Реєстрація до рекурсії розриває цикл (обхід не піде вдруге) і зберігає спільну тотожність (два поля на один об'єкт → одна копія).",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'deepclone-memo.svg'), W, H, *frags)


# ── Родовід слова «прототип»: дві гілки від спільного кореня ──────────────────
def fig_lineage_two_branches():
    W, H = 1180, 660
    frags = []

    root, rw, rh = textbox(W / 2, 54, ["прототип", "гр. prōtótypon — «перший відбиток»"],
                           size=13, bold=True, fill=FILL, stroke=INK, sw=1.9, min_w=360)
    frags.append(root)
    cog, cw, ch = textbox(W / 2, 132,
                          "корінь ідеї: категорія — довкола ЗРАЗКА, а не за визначенням (Рош, 1970-ті)",
                          size=12, fill="#f6f7f9", stroke=MUTED, sw=1.3, min_w=640)
    frags.append(cog)

    lcx, rcx = 320, 860
    bus_y = 200
    row_ys = [252, 356, 460]
    bh = 56

    frags.append(line(W / 2, 132 + ch / 2, W / 2, bus_y, color=MUTED, sw=1.4))
    frags.append(line(lcx, bus_y, rcx, bus_y, color=MUTED, sw=1.4))
    frags.append(arrow(lcx, bus_y, lcx, row_ys[0] - bh / 2, color=FIELD, sw=1.7))
    frags.append(arrow(rcx, bus_y, rcx, row_ys[0] - bh / 2, color=NEG, sw=1.7))

    left_rows = [["Лібермен · 1986", "делегування"],
                 ["Self · 1987", "Унгар і Сміт"],
                 ["JavaScript · 1995", "Айк"]]
    for i, lines in enumerate(left_rows):
        b, bw, hh = textbox(lcx, row_ys[i], lines, size=12.5, bold=True,
                            fill=GREENFILL, stroke=FIELD, sw=1.7, min_w=310)
        frags.append(b)
        if i > 0:
            frags.append(arrow(lcx, row_ys[i - 1] + bh / 2, lcx, row_ys[i] - bh / 2, color=FIELD, sw=1.6))

    right_rows = [["патерн GoF · 1994", "clone()"],
                  ["C++ · «віртуальний clone()»", "ідіома"],
                  ["Java · Cloneable", "(зламана)"]]
    for i, lines in enumerate(right_rows):
        b, bw, hh = textbox(rcx, row_ys[i], lines, size=12.5, bold=True,
                            fill=BLUEFILL, stroke=NEG, sw=1.7, min_w=310)
        frags.append(b)
        if i > 0:
            frags.append(arrow(rcx, row_ys[i - 1] + bh / 2, rcx, row_ys[i] - bh / 2, color=NEG, sw=1.6))

    frags.append(text(lcx, row_ys[2] + bh / 2 + 34, "живе посилання —", size=12.5, bold=True, color=FIELD))
    frags.append(text(lcx, row_ys[2] + bh / 2 + 54, "об'єкт ДЕЛЕГУЄ прототипу", size=12.5, bold=True, color=FIELD))
    frags.append(text(rcx, row_ys[2] + bh / 2 + 34, "clone() робить", size=12.5, bold=True, color=NEG))
    frags.append(text(rcx, row_ys[2] + bh / 2 + 54, "САМОСТІЙНИЙ об'єкт", size=12.5, bold=True, color=NEG))

    frags.append(line(70, H - 66, W - 70, H - 66, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 36, "Однакове слово, спільний корінь — протилежна механіка.",
                      size=13.5, bold=True, color=INK))

    render(os.path.join(IMG, 'lineage-two-branches.svg'), W, H, *frags)


# ── Делегування (живий зв'язок) проти копіювання (зв'язок обірвано) ───────────
def _dashline(x1, y1, x2, y2, color, sw=1.8, dash="7,5", head=True):
    m = ' marker-end="url(#arrow)"' if head else ''
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"%s/>' % (x1, y1, x2, y2, color, sw, dash, m))


def fig_delegate_vs_copy():
    W, H = 1120, 540
    frags = []

    frags.append(line(W / 2, 92, W / 2, H - 92, color="#d0d5db", sw=1.2, dash="6,6"))

    lcx, rcx = W / 4, 3 * W / 4
    top_y, bot_y = 168, 356

    frags.append(text(lcx, 50, "Делегування — зв'язок ЖИВИЙ", size=15.5, bold=True, color=FIELD))
    proto, pw, ph = textbox(lcx, top_y, "прототип", size=13.5, bold=True,
                            fill=GREENFILL, stroke=FIELD, sw=1.8, min_w=210)
    frags.append(proto)
    child, chw, chh = textbox(lcx, bot_y, "нащадок", size=13.5, bold=True,
                              fill=FILL, stroke=LINE, sw=1.6, min_w=210)
    frags.append(child)
    frags.append(_dashline(lcx, bot_y - chh / 2, lcx, top_y + ph / 2 + 4, color=FIELD, sw=2))
    frags.append(text(lcx + pw / 2 + 16, (top_y + bot_y) / 2 - 8,
                      "не знайшов у себе —", size=11.5, color=FIELD, anchor="start"))
    frags.append(text(lcx + pw / 2 + 16, (top_y + bot_y) / 2 + 10,
                      "дивиться сюди НАЖИВО", size=11.5, bold=True, color=FIELD, anchor="start"))
    frags.append(text(lcx, bot_y + chh / 2 + 40, "зміниш прототип —", size=12.5, bold=True, color=INK))
    frags.append(text(lcx, bot_y + chh / 2 + 60, "зміняться ВСІ нащадки", size=12.5, bold=True, color=INK))

    frags.append(text(rcx, 50, "Копіювання — зв'язок ОБІРВАНО", size=15.5, bold=True, color=NEG))
    sample, sw_, sh_ = textbox(rcx, top_y, "зразок", size=13.5, bold=True,
                               fill=BLUEFILL, stroke=NEG, sw=1.8, min_w=210)
    frags.append(sample)
    clone, clw, clh = textbox(rcx, bot_y, "клон", size=13.5, bold=True,
                              fill=FILL, stroke=LINE, sw=1.6, min_w=210)
    frags.append(clone)
    my = (top_y + sh_ / 2 + bot_y - clh / 2) / 2
    frags.append(_dashline(rcx, top_y + sh_ / 2 + 4, rcx, bot_y - clh / 2, color=MUTED, sw=1.6, head=False))
    frags.append(line(rcx - 13, my + 9, rcx - 1, my - 9, color=POS, sw=2.6))
    frags.append(line(rcx + 1, my + 9, rcx + 13, my - 9, color=POS, sw=2.6))
    frags.append(text(rcx + sw_ / 2 + 16, my - 6, "після copy", size=11.5, color=POS, anchor="start"))
    frags.append(text(rcx + sw_ / 2 + 16, my + 12, "зв'язку НЕМА", size=11.5, bold=True, color=POS, anchor="start"))
    frags.append(text(rcx, bot_y + clh / 2 + 40, "зміниш зразок —", size=12.5, bold=True, color=INK))
    frags.append(text(rcx, bot_y + clh / 2 + 60, "клон не помітить", size=12.5, bold=True, color=INK))

    frags.append(line(70, H - 60, W - 70, H - 60, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 32, "Той самий «прототип» — дві протилежні машинерії.",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'delegate-vs-copy.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_create_by_example()
    fig_shallow_vs_deep()
    fig_prototype_registry()
    fig_clone_field_decision()
    fig_deepclone_memo()
    fig_lineage_two_branches()
    fig_delegate_vs_copy()
    print("figs done")
