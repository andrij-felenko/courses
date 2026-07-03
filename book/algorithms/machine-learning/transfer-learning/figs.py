# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: суть — не з нуля, а від чужого навченого ──────────────────────
def fig_transfer_idea():
    W, H = 720, 380
    f = []
    f.append(text(W/2, 26, "Дві дороги до моделі: з нуля на дрібних даних чи від чужого навченого", size=14, bold=True))

    # ── верхній рядок: з нуля ──
    ty = 108
    b1, w1, _ = textbox(120, ty, "мало даних\n(200 фото)", size=12, pad=11, fill="#fdecea", stroke=POS)
    b2, w2, _ = textbox(340, ty, "порожня мережа\n(ваги випадкові)", size=12, pad=11, fill="#f4f6f8", stroke=LINE)
    b3, w3, _ = textbox(560, ty, "СЛАБКА модель\n(переучиться)", size=12, pad=11, fill="#fdecea", stroke=POS, bold=True)
    f.append(arrow(120 + w1/2 + 5, ty, 340 - w2/2 - 5, ty, sw=2, color=MUTED))
    f.append(arrow(340 + w2/2 + 5, ty, 560 - w3/2 - 5, ty, sw=2, color=MUTED))
    f.append(b1); f.append(b2); f.append(b3)
    f.append(text(120, ty - 40, "З НУЛЯ", size=13, bold=True, color=POS))

    # ── нижній рядок: перенесення ──
    by = 258
    c1, cw1, _ = textbox(120, by, "чужа мережа,\nнавчена на\nмільйонах фото", size=12, pad=11, fill="#eaf0fd", stroke=NEG)
    c2, cw2, _ = textbox(345, by, "лишити готові\nознаки, доучити\nтонку верхівку", size=12, pad=11, fill="#e9f7ef", stroke=FIELD)
    c3, cw3, _ = textbox(565, by, "СИЛЬНА модель\nз тих самих\n200 фото", size=12, pad=11, fill="#e9f7ef", stroke=FIELD, bold=True)
    f.append(arrow(120 + cw1/2 + 5, by, 345 - cw2/2 - 5, by, sw=2, color=MUTED))
    f.append(arrow(345 + cw2/2 + 5, by, 565 - cw3/2 - 5, by, sw=2, color=MUTED))
    f.append(c1); f.append(c2); f.append(c3)
    f.append(text(120, by - 52, "ПЕРЕНЕСЕННЯ", size=13, bold=True, color=FIELD))

    box, _, _ = textbox(W/2, H - 24,
        "ті самі дрібні дані: з нуля мережа тоне, з чужих ознак — злітає",
        size=12, pad=10, fill="#fff8e1", stroke="#c9a227")
    f.append(box)

    render(os.path.join(OUT, 'transfer-idea.svg'), W, H, *f)


# ── Фігура 2: ознаки від загальних до особливих по глибині ──────────────────
def fig_layer_general_to_specific():
    W, H = 720, 400
    f = []
    f.append(text(W/2, 24, "Углиб мережі ознаки йдуть від загальних до вузько-своїх", size=14, bold=True))

    # чотири блоки-шари в ряд + голова
    y = 120
    bh = 96
    xs = [70, 240, 410, 580]
    labels = [
        ("шар 1–2", "краї, плями,\nкольори", "#eaf0fd", NEG, "ЗАГАЛЬНЕ"),
        ("середина", "кути, текстури,\nчастини", "#eef6ee", FIELD, "радше загальне"),
        ("шар N−1", "морди, колеса,\nцілі деталі", "#fff3e0", "#c9a227", "радше своє"),
        ("голова", "класи саме\nтого набору", "#fdecea", POS, "ВУЗЬКО СВОЄ"),
    ]
    bw = 128
    for (cap, body, fill, stroke, tag), x in zip(labels, xs):
        f.append(rect(x, y, bw, bh, fill=fill, stroke=stroke, sw=2))
        f.append(text(x + bw/2, y - 8, cap, size=12, bold=True, color=stroke))
        f.append(mtext(x + bw/2, y + bh/2 - 4, body.split("\n"), size=11.5, color=INK))
        f.append(text(x + bw/2, y + bh + 18, tag, size=10.5, color=stroke, bold=True))
        # межа x праворуч
    for i in range(3):
        x1 = xs[i] + bw
        x2 = xs[i+1]
        f.append(arrow((x1+x2)/2 - 14, y + bh/2, (x1+x2)/2 + 14, y + bh/2, sw=2, color=MUTED))

    # смуга-градієнт «переносне ↔ треба переучити» під шарами
    gy = y + bh + 48
    f.append(text(W/2, gy, "◀ можна лишати як є (заморозити)          треба переучувати ▶",
                  size=12, color=MUTED, bold=True))

    box, _, _ = textbox(W/2, H - 28,
        "тому переносять НИЗ (краї, текстури — придатні будь-де), а верх і голову вчать заново під свою задачу",
        size=12, pad=10, fill="#fff8e1", stroke="#c9a227")
    f.append(box)

    render(os.path.join(OUT, 'layer-general-to-specific.svg'), W, H, *f)


# ── Фігура 3: три стратегії за розміром даних ───────────────────────────────
def fig_three_strategies():
    W, H = 720, 400
    f = []
    f.append(text(W/2, 24, "Три способи перенести — вибір диктує розмір твоїх даних", size=14, bold=True))

    panels = [
        (30,  "ВИТЯГ ОЗНАК", "заморозити ВСЕ,\nнавчити лише\nнову голову", "мало даних\n(сотні)", "#e9f7ef", FIELD),
        (255, "ТОНКЕ ДОУЧУВАННЯ", "розморозити\nверхні шари +\nголову, малий крок", "середньо\n(тисячі)", "#eef6ee", "#2e8b57"),
        (480, "ПОВНЕ ДОУЧУВАННЯ", "розморозити ВСЕ,\nдуже малий крок,\nпильнуй перенавчання", "багато даних\n(десятки тис.)", "#fff3e0", "#c9a227"),
    ]
    pw = 210
    py = 66
    ph = 210
    for x, title, body, data, fill, stroke in panels:
        f.append(rect(x, py, pw, ph, fill=BG, stroke=stroke, sw=2))
        f.append(text(x + pw/2, py + 24, title, size=13, bold=True, color=stroke))
        # заморожена частина (низ) — сіра; навчена (верх) — кольорова
        # столбик-мережа: три сегменти
        cx = x + pw/2
        seg_w = 120
        seg_h = 34
        base = py + 54
        # знизу — низ мережі (заморожений у перших двох, вчиться у третьому)
        segs = {
            "ВИТЯГ ОЗНАК":        [("низ", "#dfe3e8", "🔒"), ("верх", "#dfe3e8", "🔒"), ("голова", fill, "✎")],
            "ТОНКЕ ДОУЧУВАННЯ":   [("низ", "#dfe3e8", "🔒"), ("верх", fill, "✎"),      ("голова", fill, "✎")],
            "ПОВНЕ ДОУЧУВАННЯ":   [("низ", fill, "✎"),        ("верх", fill, "✎"),      ("голова", fill, "✎")],
        }[title]
        for i, (nm, sf, mk) in enumerate(segs):
            sy = base + (2 - i) * (seg_h + 6)
            f.append(rect(cx - seg_w/2, sy, seg_w, seg_h, fill=sf, stroke=stroke, sw=1.4))
            f.append(text(cx, sy + seg_h/2 + 4, nm + "  " + mk, size=11.5, color=INK))
        # підпис даних
        f.append(mtext(cx, py + ph - 20, data.split("\n"), size=11, color=stroke, bold=True))

    # легенда
    f.append(text(W/2, H - 54, "🔒 заморожено (ваги не міняються)     ✎ вчиться на твоїх даних", size=11.5, color=MUTED))
    box, _, _ = textbox(W/2, H - 24,
        "менше даних → більше морозь; більше даних → більше розморожуй, але кроком дрібнішим за звичайний",
        size=12, pad=9, fill="#fff8e1", stroke="#c9a227")
    f.append(box)

    render(os.path.join(OUT, 'three-strategies.svg'), W, H, *f)


# ── Фігура 4: коли переносити допомагає, а коли шкодить ──────────────────────
def fig_when_helps():
    W, H = 720, 360
    f = []
    f.append(text(W/2, 24, "Коли перенесення виграє, а коли б'є в спину", size=14, bold=True))

    # ліва панель — виграш
    lx, ly, lw, lh = 40, 66, 300, 210
    f.append(rect(lx, ly, lw, lh, fill="#f2faf5", stroke=FIELD, sw=2))
    f.append(text(lx + lw/2, ly + 24, "✓ ПОМАГАЄ", size=14, bold=True, color=FIELD))
    for i, s in enumerate([
        "задача СХОЖА на джерело",
        "(фото → фото)",
        "твоїх даних МАЛО",
        "верх доучуєш малим кроком",
    ]):
        f.append(text(lx + 20, ly + 58 + i*32, "•  " + s, size=12.5, color=INK, anchor="start"))

    # права панель — шкода
    rx, ry, rw, rh = 380, 66, 300, 210
    f.append(rect(rx, ry, rw, rh, fill="#fdf3f2", stroke=POS, sw=2))
    f.append(text(rx + rw/2, ry + 24, "✗ ШКОДИТЬ (від'ємне перенесення)", size=12.5, bold=True, color=POS))
    for i, s in enumerate([
        "джерело ЧУЖЕ задачі",
        "(фото → звук, ЕКГ)",
        "великий крок стирає ознаки",
        "своїх даних досить на з нуля",
    ]):
        f.append(text(rx + 20, ry + 58 + i*32, "•  " + s, size=12.5, color=INK, anchor="start"))

    box, _, _ = textbox(W/2, H - 26,
        "перенесення — не завжди добро: чуже джерело чи завеликий крок роблять модель ГІРШОЮ за навчену з нуля",
        size=12, pad=10, fill="#fff8e1", stroke="#c9a227")
    f.append(box)

    render(os.path.join(OUT, 'when-helps.svg'), W, H, *f)


# ── Фігура 5 (історія): чотири різні події, які плутають в одну ─────────────
def fig_hist_timeline():
    W, H = 820, 470
    f = []
    f.append(text(W/2, 26, "Перенесення навчання: чотири різні кроки, не один «винахід»", size=14, bold=True))

    # горизонтальна вісь часу
    ax_y = 96
    ax_x0, ax_x1 = 70, W - 50
    f.append(line(ax_x0, ax_y, ax_x1, ax_y, color=INK, sw=2))
    f.append(arrow(ax_x1 - 24, ax_y, ax_x1, ax_y, sw=2, color=INK))
    for yr, xf in [("1976", 0.02), ("1993", 0.30), ("1995", 0.40), ("2010", 0.66), ("2014", 0.92)]:
        x = ax_x0 + (ax_x1 - ax_x0) * xf
        f.append(line(x, ax_y - 6, x, ax_y + 6, color=INK, sw=2))
        f.append(text(x, ax_y - 14, yr, size=12, bold=True, color=INK))

    # чотири картки: подія + що саме це було
    cards = [
        (34,  148, "#eaf0fd", NEG,   "ІДЕЯ + МІРА", 0.02,
         "Божиновський і Фулгоші\n(1976): перша модель\nпереносу для перцептрона —\nдодатний / від'ємний / нульовий"),
        (230, 148, "#eef6ee", FIELD, "АЛГОРИТМ + ТЕРМІН", 0.35,
         "Пратт (1993, NIPS-5): DBT —\nпозичити ваги, а не вчити\nз нуля. Воркшоп «Learning\nto Learn» (NIPS-1995)"),
        (426, 148, "#fff3e0", "#c9a227", "ФОРМАЛІЗАЦІЯ", 0.66,
         "Пан і Ян (2010): чіткі\nозначення «домен» і «задача»,\nсхема видів переносу.\nСпільна мова для поля"),
        (622, 148, "#fdecea", POS,   "МАСОВА ПРАКТИКА", 0.92,
         "DeCAF + Йосінскі та ін.\n(2014): ознаки CNN\nпереносяться; ВИМІРЯНО\nперехід загальне → своє"),
    ]
    cw, ch = 164, 176
    for x, y, fill, stroke, tag, yr_x, body in cards:
        f.append(rect(x, y, cw, ch, fill=fill, stroke=stroke, sw=2))
        f.append(text(x + cw/2, y + 22, tag, size=12, bold=True, color=stroke))
        f.append(mtext(x + cw/2, y + 48, body.split("\n"), size=10.5, color=INK, lh=1.28))
        # ніжка від картки до її року на осі
        cx = x + cw/2
        tx = ax_x0 + (ax_x1 - ax_x0) * yr_x
        f.append(line(cx, y, tx, ax_y + 8, color=stroke, sw=1.4, dash="4 3"))

    box, _, _ = textbox(W/2, H - 30,
        "«хто винайшов» — хибне питання: ідея, термін, означення\nй масова практика прийшли в різні роки й від різних людей",
        size=11.5, pad=10, fill="#fff8e1", stroke="#c9a227")
    f.append(box)

    render(os.path.join(OUT, 'hist-timeline.svg'), W, H, *f)


if __name__ == '__main__':
    fig_transfer_idea()
    fig_layer_general_to_specific()
    fig_three_strategies()
    fig_when_helps()
    fig_hist_timeline()
    print("OK: 5 figures written to", OUT)
