# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACC = "#7a4ea8"     # фіолетовий — рішення/вибір
ACCBG = "#f3edfb"
WARN = "#b8862f"    # третій колір-ідентичність варіанта
WARNBG = "#fff6e0"


# ── block-anatomy: та сама будова кожного варіантного блоку ────────────────────
# Ідея: у курсі кожна велика розвилка подана однаково — «Рішення: …». Зверху
# 2–3 варіанти, кожен із тріадою чесної адвокатури (де виграє / хто робить /
# чим платиш). Усі три женуться крізь ту саму перевірку (сценарії · чутлива
# точка · зворотність) і зводяться внизу до рамки-вибору, що каже не «переможець»,
# а де кожен виграє → композиція. Розставляємо з запасом, написи — кожен у своїй
# смузі, щоб нічого не накладалося.

def fig_block_anatomy():
    W, H = 980, 486
    p = []

    # ── смуга «Рішення: …» ──
    rb, rw, rh = textbox(W / 2, 58, "Рішення:  розвилка курсу", size=13, pad=11,
                         fill=ACCBG, stroke=ACC, sw=2, color=ACC, bold=True, min_w=280)
    p.append(rb)

    # ── три варіанти-картки ──
    cards = [
        ("Варіант А", NEG, "#eaf0fd"),
        ("Варіант Б", ACC, ACCBG),
        ("Варіант В", WARN, WARNBG),
    ]
    cw, gap = 288, 18
    total = len(cards) * cw + (len(cards) - 1) * gap
    x0 = (W - total) / 2
    ctop, ch = 92, 150
    for i, (name, col, fill) in enumerate(cards):
        cx = x0 + i * (cw + gap)
        mid = cx + cw / 2
        p.append(rect(cx, ctop, cw, ch, fill=fill, stroke=col, sw=1.9, rx=11))
        p.append(text(mid, ctop + 27, name, size=13.5, color=col, bold=True))
        p.append(line(cx + 16, ctop + 40, cx + cw - 16, ctop + 40, color=col, sw=1.1, dash="4 3"))
        p.append(text(cx + 20, ctop + 70, "✓  де виграє", size=11.5, color=FIELD, anchor="start", bold=True))
        p.append(text(cx + 20, ctop + 98, "·  хто так робить у проді", size=11, color=MUTED, anchor="start"))
        p.append(text(cx + 20, ctop + 126, "✗  чим платиш", size=11.5, color=POS, anchor="start", bold=True))

    # стрілка вниз до перевірки
    p.append(arrow(W / 2, ctop + ch + 2, W / 2, ctop + ch + 26, color=MUTED, sw=1.8))
    p.append(text(W / 2, ctop + ch + 46, "усі варіанти — крізь ту саму перевірку:", size=11.5, color=INK, bold=True))

    # ── три лінзи перевірки ──
    lenses = [
        "спільна лінійка:\nті самі сценарії з мірою",
        "чутлива точка:\nщо перемикає вибір",
        "зворотність:\nчи є дешевий хід назад",
    ]
    ltop, lh = ctop + ch + 60, 56
    for i, s in enumerate(lenses):
        lx = x0 + i * (cw + gap)
        p.append(fitbox(lx, ltop, cw, lh, s, size=11, pad=9,
                        fill="#eef1f5", stroke=MUTED, sw=1.4, color=INK))

    # стрілка вниз до вибору
    p.append(arrow(W / 2, ltop + lh + 2, W / 2, ltop + lh + 24, color=MUTED, sw=1.8))

    # ── рамка-вибір ──
    ch_y = ltop + lh + 58
    cb, cbw, cbh = textbox(W / 2, ch_y,
                           "Вибір — не вердикт, а рамка критеріїв\nде кожен варіант виграє  →  часто композиція",
                           size=12, pad=13, fill="#eef6ef", stroke=FIELD, sw=2, color=INK, bold=True)
    p.append(cb)
    p.append(text(W / 2, ch_y + cbh / 2 + 20, "той самий кістяк — у кожному «Рішення:» курсу",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "block-anatomy.svg"), W, H, *p,
           title="Варіантний блок: та сама будова щоразу")


# ── sensitivity-flip: один факт перемикає переможця ───────────────────────────
# Ідея: варіанти не мають «правильного» переможця в порожнечі. Є вісь — вага
# одного сценарію в ДЕРЕВІ КОРИСНОСТІ (тут: наскільки критичний offline для
# цього правила). Ліворуч від чутливої точки виграє хмара, праворуч — хаб. Той
# самий блок дає різну відповідь; тому фінал — композиція. Дві реальні мітки DH
# сидять по різні боки порога. Смуги-регіони без різких країв під написами.

def fig_sensitivity_flip():
    W, H = 900, 384
    p = []

    x0, x1 = 78, 822
    axis_y = 196
    x_tip = 452
    band_top, band_bot = 116, 268

    # регіони-смуги (лише заливка, край ледь помітний)
    p.append(rect(x0, band_top, x_tip - x0, band_bot - band_top,
                  fill="#eef2fc", stroke="#dbe3f7", sw=1.0, rx=8))
    p.append(rect(x_tip, band_top, x1 - x_tip, band_bot - band_top,
                  fill="#ecf6ee", stroke="#d6ecdb", sw=1.0, rx=8))

    # підписи регіонів — над віссю, у центрі кожної половини
    p.append(mtext((x0 + x_tip) / 2, band_top + 34, "виграє ХМАРА\nодин деплой важить більше",
                   size=11.5, color=NEG, lh=1.35, bold=True))
    p.append(mtext((x_tip + x1) / 2, band_top + 34, "виграє ХАБ\nавтономність важить більше",
                   size=11.5, color=FIELD, lh=1.35, bold=True))

    # вісь
    p.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2))
    p.append(arrow(x1 - 2, axis_y, x1 + 18, axis_y, color=INK, sw=2))

    # чутлива точка — вертикаль
    p.append(line(x_tip, band_top - 26, x_tip, band_bot + 4, color=ACC, sw=2, dash="6 4"))
    tb, tw, th = textbox(x_tip, band_top - 40, "чутлива точка: тут переможець перемикається",
                         size=10.5, pad=8, fill=ACCBG, stroke=ACC, sw=1.6, color=ACC, bold=True)
    p.append(tb)

    # мітки на осі — нижче осі, кожна у своїй колонці
    marks = [
        (208, "правило за\nпрогнозом погоди", NEG),
        (700, "замок\nвхідних дверей", FIELD),
    ]
    for mx, label, col in marks:
        p.append(circle(mx, axis_y, 6, fill=BG, stroke=col, sw=2.2))
        p.append(mtext(mx, axis_y + 30, label, size=10.5, color=col, lh=1.25, bold=True))

    # підпис осі
    p.append(text(W / 2, axis_y + 78, "→  вага offline-сценарію в дереві корисності",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "sensitivity-flip.svg"), W, H, *p,
           title="Чутлива точка: один факт перемикає переможця")


# ── lineage-steelman: родовід прийому в часі ──────────────────────────────────
# Ідея: «показати чужу позицію в найсильнішій формі» — стара практика з довгим
# паперовим слідом (Мілл 1859 → Рапопорт 1960 → Деннет 2013), а коротке ім'я
# «steelman» їй дали аж у 2010-х. Чотири стопи на осі часу, картки через одну
# вгору/вниз (щоб сусіди не накладались), теза — у підписі. Для вставки hist.

def fig_lineage_steelman():
    W, H = 1000, 400
    p = []
    axis_y = 214
    x_l, x_r = 66, 934

    # вісь часу
    p.append(line(x_l, axis_y, x_r - 6, axis_y, color=INK, sw=2))
    p.append(arrow(x_r - 6, axis_y, x_r + 14, axis_y, color=INK, sw=2))
    p.append(text(x_r + 12, axis_y - 12, "час", size=10.5, color=MUTED, italic=True, anchor="end"))

    # (x, side, колір, заливка, рядки картки)
    stops = [
        (150, "above", NEG,   "#eaf0fd", ["1859 · Джон Стюарт Мілл",
                                          "«On Liberty», розділ 2:",
                                          "знати лише свій бік — мало"]),
        (383, "below", FIELD, "#e9f6ee", ["1960 · Анатоль Рапопорт",
                                          "«Fights, Games, and Debates»:",
                                          "правила чесної суперечки"]),
        (617, "above", WARN,  WARNBG,    ["2013 · Деніел Деннет",
                                          "«Intuition Pumps»:",
                                          "чотири кроки критики"]),
        (850, "below", ACC,   ACCBG,     ["2010-ті · онлайн-спільноти",
                                          "прийом дістає ім'я:",
                                          "«steelman»"]),
    ]
    row_above, row_below = 116, 312
    for x, side, col, fill, lines in stops:
        cy = row_above if side == "above" else row_below
        body, w, h = textbox(x, cy, "\n".join(lines), size=11, pad=10,
                             fill=fill, stroke=col, sw=1.8, color=INK, min_w=214)
        if side == "above":
            p.append(line(x, axis_y - 7, x, cy + h / 2, color=col, sw=1.6))
        else:
            p.append(line(x, axis_y + 7, x, cy - h / 2, color=col, sw=1.6))
        p.append(body)
        p.append(circle(x, axis_y, 7, fill=BG, stroke=col, sw=2.4))

    # теза-підпис
    p.append(text(W / 2, H - 15,
                  "Практику Мілл описав 1859-го — коротке ім'я їй дали аж у 2010-х: ідея стара, назва молода.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "lineage-steelman.svg"), W, H, *p,
           title="Родовід прийому: від Мілла до «steelman»")


if __name__ == "__main__":
    fig_block_anatomy()
    fig_sensitivity_flip()
    fig_lineage_steelman()
    print("OK: figures written to", OUT)
