# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «LPWAN» (root/course/embedded/zvyazok/lpwan).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def _tint(c):
    m = {POS: "#fbe7e4", NEG: "#e6ecfb", FIELD: "#e4f4ea", "#b8860b": "#f6efdb",
         "#7d3c98": "#efe6f4"}
    return m.get(c, "#f0f0f0")


# ── 1. Ніша LPWAN на карті «дальність × швидкість» ────────────────────────────
def fig_niche():
    W, H = 760, 470
    f = [text(W / 2, 28, "Де живе LPWAN: далеко, але тонким струмочком", 16, INK, "middle", bold=True)]

    # осі
    ox, oy = 90, 400        # початок координат
    aw, ah = 600, 320
    f.append(line(ox, oy, ox + aw + 12, oy, color=MUTED, sw=1.4))   # X — дальність
    f.append(line(ox, oy, ox, oy - ah - 12, color=MUTED, sw=1.4))   # Y — швидкість
    f.append(text(ox + aw / 2, oy + 30, "дальність →", 12, MUTED, "middle"))
    f.append(text(ox + aw, oy + 16, "метри … кілометри", 9.5, MUTED, "middle"))
    # підпис Y вертикально
    f.append('<text x="%d" y="%d" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %d %d)">швидкість даних →</text>'
             % (28, oy - ah / 2, FONT, MUTED, 28, oy - ah / 2))

    # три області (еліпси): ближня смуга / LPWAN / стільниковий
    def blob(cx, cy, rx, ry, name, sub, col):
        f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
                 'stroke="%s" stroke-width="2"/>' % (cx, cy, rx, ry, _tint(col), col))
        f.append(text(cx, cy - 6, name, 13, col, "middle", bold=True))
        f.append(text(cx, cy + 12, sub, 9.5, MUTED, "middle"))

    # ближнє радіо: мала дальність, велика швидкість (лівий верх)
    blob(ox + 130, oy - 250, 96, 60, "Wi-Fi · BLE", "десятки м · Мбіт/с", NEG)
    # стільниковий: велика дальність, велика швидкість (правий верх)
    blob(ox + 470, oy - 250, 100, 62, "Стільниковий", "км · Мбіт/с · ват", "#7d3c98")
    # LPWAN: велика дальність, мала швидкість (правий низ) — наша ніша
    blob(ox + 460, oy - 80, 120, 56, "LPWAN", "км · біти/с · мікровати", FIELD)

    # стрілка-висновок до LPWAN
    f.append(text(ox + 175, oy - 92, "та сама дальність,", 10, FIELD, "middle", bold=True))
    f.append(text(ox + 175, oy - 76, "у тисячі разів менше", 10, FIELD, "middle"))
    f.append(text(ox + 175, oy - 60, "енергії й даних", 10, FIELD, "middle"))

    render(os.path.join(IMG, "niche.svg"), W, H, *f)


# ── 2. Зірка: тонкі вузли → розумні шлюзи → сервер ────────────────────────────
def fig_star():
    W, H = 760, 430
    f = [text(W / 2, 26, "Зірка LPWAN: уся складність — у шлюзі й сервері, не у вузлі", 15.5, INK, "middle", bold=True)]

    # сервер праворуч
    sx, sy = 660, 215
    f.append(rect(sx - 56, sy - 40, 96, 80, fill="#fbfcfd", stroke=INK, sw=2, rx=8))
    f.append(text(sx - 8, sy - 12, "Сервер", 12, INK, "middle", bold=True))
    f.append(text(sx - 8, sy + 6, "мережі", 11, INK, "middle", bold=True))
    f.append(text(sx - 8, sy + 24, "(хмара)", 9.5, MUTED, "middle"))

    # два шлюзи посередині
    gws = [(400, 120, "Шлюз 1"), (400, 320, "Шлюз 2")]
    for gx, gy, gn in gws:
        f.append(rect(gx - 50, gy - 30, 100, 60, fill=_tint(NEG), stroke=NEG, sw=2, rx=8))
        f.append(text(gx, gy - 4, gn, 12, NEG, "middle", bold=True))
        f.append(text(gx, gy + 14, "приймає все", 9, MUTED, "middle"))
        # шлюз → сервер (звичайний інтернет)
        f.append(arrow(gx + 52, gy, sx - 58, sy + (gy - sy) * 0.32, color=INK, sw=1.8))
    f.append(text(530, 150, "звичайний", 9.5, MUTED, "middle"))
    f.append(text(530, 163, "інтернет", 9.5, MUTED, "middle"))

    # вузли ліворуч — багато тонких
    nodes = [(95, 70), (80, 150), (110, 215), (80, 285), (95, 360)]
    for i, (nx, ny) in enumerate(nodes):
        f.append(circle(nx, ny, 17, fill=_tint(FIELD), stroke=FIELD, sw=2))
        f.append(text(nx, ny + 4, "в%d" % (i + 1), 9.5, FIELD, "middle", bold=True))
        # кожен вузол шле в обидва шлюзи (його чують усі, хто в радіусі)
        for gx, gy, gn in gws:
            f.append(line(nx + 16, ny, gx - 50, gy, color=FIELD, sw=1.0, dash="3 4"))

    f.append(text(95, 30, "тонкі вузли (батарея на роки)", 10.5, FIELD, "middle", bold=True))
    f.append(text(95, 400, "лише передають і сплять", 9.5, MUTED, "middle"))

    # пояснення внизу
    f.append(fitbox(150, 388, 560, 34,
                    "вузол не знає про шлюзи й не обирає маршрут — просто кричить у ефір;\n"
                    "його ловить будь-який шлюз у радіусі, дублі відсіює сервер",
                    size=10.5, fill="#fbfcfd", stroke="#dde3ea", color=INK))

    render(os.path.join(IMG, "star.svg"), W, H, *f)


# ── 3. Реальність 1% duty cycle: скільки можна сказати за добу ─────────────────
def fig_duty():
    W, H = 760, 400
    f = [text(W / 2, 26, "Закон 1%: ефір майже завжди мусить мовчати", 16, INK, "middle", bold=True)]

    # смуга часу (година), 1% зафарбовано
    ox, oy = 60, 130
    bw, bh = 640, 46
    f.append(text(ox, oy - 14, "1 година ефіру одного вузла (смуга EU868, дозволено 1%)", 11, MUTED, "start"))
    f.append(rect(ox, oy, bw, bh, fill="#eef6ef", stroke=FIELD, sw=1.6))
    # 1% = маленький червоний шматочок зліва
    onw = bw * 0.01
    f.append(rect(ox, oy, max(onw, 6), bh, fill=_tint(POS), stroke=POS, sw=1.8))
    f.append(arrow(ox + 3, oy - 4, ox + 3, oy - 30, color=POS, sw=1.4))
    f.append(text(ox + 60, oy - 34, "можна говорити (1%)", 10, POS, "middle", bold=True))
    f.append(text(ox + bw / 2, oy + bh / 2 + 4, "решта 99% — обов'язкова мовчанка", 11.5, FIELD, "middle", bold=True))

    # приклад-розрахунок
    f.append(fitbox(ox, oy + 80, bw, 70,
                    "1% від години = 36 секунд ефіру на годину.\n"
                    "Один пакет SF12 висить у ефірі ~1.5 с → ~24 пакети за годину — стеля.\n"
                    "Тому LPWAN-вузол шле кілька байтів зрідка: покази раз на 10–60 хв, не потік.",
                    size=11.5, fill="#fbfcfd", stroke="#dde3ea", color=INK))

    # стрілка-висновок
    f.append(fitbox(ox, oy + 162, bw, 36,
                    "duty cycle — не порада, а закон: передавач САМ мусить лічити свій час у ефірі й замовкати",
                    size=11.5, fill="#fdecea", stroke=POS, color=INK, bold=True))

    render(os.path.join(IMG, "duty.svg"), W, H, *f)


# ── 4. Три LPWAN поряд: на що міняти ──────────────────────────────────────────
def fig_three():
    W, H = 770, 440
    f = [text(W / 2, 26, "Три LPWAN поряд: спектр, власник, характер", 16, INK, "middle", bold=True)]

    cols_x = [70, 305, 540]
    cw = 200
    heads = [("LoRaWAN", FIELD, "чирп, ISM"),
             ("Sigfox", NEG, "ультравузька, ISM"),
             ("NB-IoT", "#7d3c98", "вузька LTE, ліцензія")]
    rows = [
        ("Спектр", ["вільний (ISM)", "вільний (ISM)", "ліцензований (оператор)"]),
        ("Хто розгортає", ["ти сам ставиш шлюз", "оператор Sigfox", "стільниковий оператор"]),
        ("Дані / посилку", ["байти-десятки", "12 байт, ~140/добу", "сотні байт+"]),
        ("Дальність", ["км (SF керує)", "км, дуже стабільно", "км, як стільниковий"]),
        ("Батарея", ["роки", "роки", "роки (гірше за LoRa)"]),
        ("Платиш за", ["своє залізо", "підписку/посилку", "SIM/трафік"]),
    ]

    # заголовки колонок
    hy = 58
    for i, (name, col, sub) in enumerate(heads):
        x = cols_x[i]
        f.append(rect(x, hy, cw, 44, fill=_tint(col), stroke=col, sw=2, rx=6))
        f.append(text(x + cw / 2, hy + 20, name, 13.5, col, "middle", bold=True))
        f.append(text(x + cw / 2, hy + 36, sub, 9.5, MUTED, "middle"))

    # рядки
    ry = hy + 56
    rh = 48
    for ri, (label, cells) in enumerate(rows):
        f.append(text(60, ry + rh / 2 + 4, label, 10.5, INK, "end", bold=True))
        for i, cell in enumerate(cells):
            x = cols_x[i]
            bg = "#fbfcfd" if ri % 2 == 0 else "#f4f6f8"
            f.append(rect(x, ry, cw, rh, fill=bg, stroke="#dde3ea", sw=1.0, rx=4))
            f.append(fitbox(x + 4, ry + 6, cw - 8, rh - 12, cell, size=10.5,
                            fill=bg, stroke=bg, color=INK))
        ry += rh + 4

    render(os.path.join(IMG, "three.svg"), W, H, *f)


# ── 5. Анатомія часу в ефірі: преамбула + символи пакета ──────────────────────
def fig_airtime_anatomy():
    W, H = 812, 430
    f = [text(W / 2, 26, "З чого складається час пакета в ефірі (time on air)", 16, INK, "middle", bold=True)]

    ox, oy = 50, 110
    bh = 50
    # масштаб: преамбула 12.25 симв., решта пакета — payloadSymbNb символів (для SF12 ~23)
    # покажемо пропорційно: преамбула ~35%, пакет ~65% від смуги
    bw_total = 670
    pre_w = bw_total * 0.35
    pay_w = bw_total * 0.65

    f.append(text(ox, oy - 16, "один пакет LoRa у часі →", 11, MUTED, "start"))

    # преамбула
    f.append(rect(ox, oy, pre_w, bh, fill=_tint(NEG), stroke=NEG, sw=1.8))
    f.append(text(ox + pre_w / 2, oy + bh / 2 + 4, "преамбула", 12, NEG, "middle", bold=True))
    f.append(text(ox + pre_w / 2, oy + bh + 18, "(n + 4.25) символів", 10, MUTED, "middle"))

    # пакет (заголовок + дані + CRC) — як набір символів
    f.append(rect(ox + pre_w, oy, pay_w, bh, fill=_tint(FIELD), stroke=FIELD, sw=1.8))
    f.append(text(ox + pre_w + pay_w / 2, oy + bh / 2 + 4,
                  "заголовок + дані + CRC", 12, FIELD, "middle", bold=True))
    f.append(text(ox + pre_w + pay_w / 2, oy + bh + 18,
                  "payloadSymbNb символів", 10, MUTED, "middle"))

    # один символ — окрема цеглинка справа, із підписом тривалості
    sx = ox + pre_w + pay_w - 26
    f.append(line(sx, oy, sx, oy + bh, color=INK, sw=1.0, dash="2 3"))
    f.append(arrow(ox + bw_total + 8, oy + bh + 40, sx + 13, oy + bh + 6, color=INK, sw=1.4))
    f.append(text(ox + bw_total - 70, oy + bh + 54, "1 символ = Tsym = 2^SF / BW", 10.5, INK, "start", bold=True))

    # формула-підсумок
    f.append(fitbox(ox, oy + 110, bw_total, 40,
                    "час у ефірі  =  Tпреамбули + Tданих  =  (n + 4.25)·Tsym  +  payloadSymbNb·Tsym",
                    size=12.5, fill="#fbfcfd", stroke="#dde3ea", color=INK, bold=True))

    # ключ: чому SF так дорого коштує
    f.append(fitbox(ox, oy + 162, bw_total, 56,
                    "Tsym подвоюється з кожним кроком SF (2^SF у чисельнику):\n"
                    "SF7 → 1.024 мс,  SF12 → 32.768 мс на символ.\n"
                    "Той самий пакет на SF12 висить у ефірі у ~28 разів довше, ніж на SF7.",
                    size=11, fill="#fdf6e3", stroke="#b8860b", color=INK))

    render(os.path.join(IMG, "airtime-anatomy.svg"), W, H, *f)


# ── 6. Таблиця airtime SF7..SF12 і добовий бюджет за 1% ───────────────────────
def fig_budget_table():
    W, H = 770, 430
    f = [text(W / 2, 26, "Той самий пакет, шість SF: час у ефірі й добовий бюджет (EU868, 1%)", 14.5, INK, "middle", bold=True)]

    # колонки таблиці
    cols = ["SF", "Tsym, мс", "час у ефірі", "за годину (1%)", "період*"]
    cx = [70, 190, 330, 505, 660]   # центри колонок
    x0 = 40
    # дані порахвані toa.py: BW125, PL=12 байтів, CR4/5, явний заголовок, CRC, преамбула 8.
    # «за годину» = 36000 мс / ToA;  «період» = ToA·100 (рівномірне розкладання 1%).
    rows = [
        ("7",  "1.024",  "41 мс",   "873", "4 с"),
        ("8",  "2.048",  "82 мс",   "437", "8 с"),
        ("9",  "4.096",  "144 мс",  "249", "14 с"),
        ("10", "8.192",  "289 мс",  "125", "29 с"),
        ("11", "16.384", "578 мс",  "62",  "58 с"),
        ("12", "32.768", "1155 мс", "31",  "116 с"),
    ]

    hy = 54
    rh = 44
    # шапка
    f.append(rect(x0, hy, W - 2 * x0, rh, fill=_tint(NEG), stroke=NEG, sw=1.6))
    for i, c in enumerate(cols):
        f.append(text(cx[i], hy + rh / 2 + 5, c, 12, NEG, "middle", bold=True))

    ry = hy + rh
    for ri, r in enumerate(rows):
        # підсвітити крайні рядки: SF7 (швидко, близько) і SF12 (далеко, дорого)
        if ri == 0:
            bg = "#eef6ef"
        elif ri == len(rows) - 1:
            bg = "#fdecea"
        else:
            bg = "#fbfcfd" if ri % 2 == 0 else "#f4f6f8"
        f.append(rect(x0, ry, W - 2 * x0, rh, fill=bg, stroke="#dde3ea", sw=1.0, rx=0))
        for i, cell in enumerate(r):
            col = INK
            if i == 0:
                col = FIELD if ri == 0 else (POS if ri == len(rows) - 1 else INK)
            f.append(text(cx[i], ry + rh / 2 + 5, cell, 11.5, col, "middle",
                          bold=(i == 0)))
        ry += rh

    # висновок під таблицею
    f.append(fitbox(x0, ry + 8, W - 2 * x0, 34,
                    "За той самий 1% бюджету SF7 дає сотні посилок на годину, SF12 — лічені десятки.\n"
                    "* період — мінімальний проміжок між посилками, якщо рівномірно розкласти 1%.",
                    size=10.5, fill="#fbfcfd", stroke="#dde3ea", color=INK))

    render(os.path.join(IMG, "budget-table.svg"), W, H, *f)


# -- 7. Hronologia narodzhennia klasu LPWAN (dlia hist-vstavky) ---------------
def fig_timeline():
    W, H = 880, 470
    f = [text(W / 2, 28, "Технології з’явилися першими, спільна назва — потім", 16, INK, "middle", bold=True)]

    x0, x1 = 80, W - 120
    axis_y = 248
    y0, y1 = 2009, 2016
    f.append(line(x0, axis_y, x1 + 10, axis_y, color=MUTED, sw=2))
    f.append(text(x1 + 6, axis_y + 24, "рік →", 11, MUTED, "middle"))

    def xof(year, frac=0.0):
        return x0 + (x1 - x0) * ((year + frac) - y0) / (y1 - y0)

    for yr in range(y0, y1 + 1):
        x = xof(yr)
        f.append(line(x, axis_y - 5, x, axis_y + 5, color=MUTED, sw=1.2))
        f.append(text(x, axis_y + 20, str(yr), 10.5, MUTED, "middle"))

    events = [
        (2009, 0.15, ["Sigfox (Тулуза):", "ультравузька смуга"], POS, -1, 150),
        (2010, 0.10, ["Cycleo (Гренобль):", "чирп → LoRa"], NEG, +1, 92),
        (2012, 0.30, ["Semtech купує Cycleo;", "Sigfox у Франції"], "#b8860b", -1, 90),
        (2013, 0.45, ["LPWA(N) —", "НАЗВА класу"], FIELD, +1, 150),
        (2015, 0.05, ["LoRa Alliance;", "протокол LoRaWAN"], NEG, -1, 90),
        (2016, 0.05, ["NB-IoT: 3GPP Rel.13", "(стільниковий)"], "#7d3c98", +1, 92),
    ]
    for yr, fr, lines, col, side, lead in events:
        x = xof(yr, fr)
        end_y = axis_y - lead if side < 0 else axis_y + lead
        f.append(line(x, axis_y, x, end_y, color=col, sw=1.4, dash="3 3"))
        f.append(circle(x, axis_y, 6, fill=col, stroke=BG, sw=2))
        box, bw, bh = textbox(x, end_y, "\n".join(lines), size=11, pad=8,
                              fill=_tint(col), stroke=col, color=INK)
        cy = end_y - bh / 2 if side < 0 else end_y + bh / 2
        box, bw, bh = textbox(x, cy, "\n".join(lines), size=11, pad=8,
                              fill=_tint(col), stroke=col, color=INK)
        f.append(box)

    f.append(text(W / 2, H - 16,
                  "Робочі мережі (2009–2012) існували РАНІШЕ, ніж спільна назва для них (2013).",
                  11, MUTED, "middle", italic=True))

    render(os.path.join(IMG, "timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_niche()
    fig_star()
    fig_duty()
    fig_three()
    fig_airtime_anatomy()
    fig_budget_table()
    fig_timeline()
    print("OK: figures written to", IMG)
