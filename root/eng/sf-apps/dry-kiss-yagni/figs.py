# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def three_guards():
    """Три застави проти складності-пасиву: YAGNI (час), KISS (кмітливість),
    DRY (знання) — і внутрішня межа DRY → передчасне узагальнення."""
    W, H = 860, 560
    frags = []

    # Центр — баланс (куди лягає складність як борг)
    cx, cy = W / 2, H / 2 + 10
    core, cw, ch = textbox(cx, cy, ["БАЛАНС КОДУ", "кожен зайвий рядок —", "пасив, борг на майбутнє"],
                           size=14, pad=16, fill="#fdecea", stroke=POS, sw=2.2, bold=False)
    # заголовок рамки окремим жирним рядком згори неї
    frags.append(rect(cx - cw / 2, cy - ch / 2, cw, ch, fill="#fdecea", stroke=POS, sw=2.2, rx=8))
    frags.append(text(cx, cy - ch / 2 + 24, "БАЛАНС КОДУ", size=15, color=POS, bold=True))
    frags.append(text(cx, cy - 2, "кожен зайвий рядок —", size=13, color=INK))
    frags.append(text(cx, cy + 16, "пасив, борг на майбутнє", size=13, color=INK))

    # Три застави навколо. Кожна: назва принципу + що відбиває.
    # Ліворуч — YAGNI (вісь часу)
    gx = 150
    g1, w1, h1 = textbox(gx, cy, ["YAGNI", "не будуй заради", "уявного майбутнього"],
                         size=13, pad=12, fill="#eaf0fd", stroke=NEG, sw=2)
    frags.append(rect(gx - w1 / 2, cy - h1 / 2, w1, h1, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    frags.append(text(gx, cy - h1 / 2 + 22, "YAGNI", size=15, color=NEG, bold=True))
    frags.append(text(gx, cy - 1, "не будуй заради", size=12, color=INK))
    frags.append(text(gx, cy + 16, "уявного майбутнього", size=12, color=INK))
    # що прослизає крізь неї (загроза)
    frags.append(text(gx, cy - h1 / 2 - 16, "вісь часу", size=12, color=MUTED, italic=True))
    frags.append(arrow(gx + w1 / 2 + 4, cy, cx - cw / 2 - 4, cy, color=NEG, sw=1.6))

    # Згори — KISS (вісь кмітливості)
    ky = 90
    frags.append(text(cx, ky - 42, "вісь кмітливості", size=12, color=MUTED, italic=True))
    k1, wk, hk = textbox(cx, ky, ["KISS", "просте замість розумного"],
                         size=13, pad=12, fill="#eafaf1", stroke=FIELD, sw=2)
    frags.append(rect(cx - wk / 2, ky - hk / 2, wk, hk, fill="#eafaf1", stroke=FIELD, sw=2, rx=8))
    frags.append(text(cx, ky - hk / 2 + 22, "KISS", size=15, color=FIELD, bold=True))
    frags.append(text(cx, ky + 8, "просте замість розумного", size=12, color=INK))
    frags.append(arrow(cx, ky + hk / 2 + 4, cx, cy - ch / 2 - 4, color=FIELD, sw=1.6))

    # Праворуч — DRY (вісь знання) + внутрішня межа
    dx = 700
    frags.append(text(dx, cy - h1 / 2 - 16, "вісь знання", size=12, color=MUTED, italic=True))
    d1, wd, hd = textbox(dx, cy, ["DRY", "одне знання —", "одне джерело"],
                         size=13, pad=12, fill="#eafaf1", stroke=FIELD, sw=2)
    frags.append(rect(dx - wd / 2, cy - hd / 2, wd, hd, fill="#eafaf1", stroke=FIELD, sw=2, rx=8))
    frags.append(text(dx, cy - hd / 2 + 22, "DRY", size=15, color=FIELD, bold=True))
    frags.append(text(dx, cy - 1, "одне знання —", size=12, color=INK))
    frags.append(text(dx, cy + 16, "одне джерело", size=12, color=INK))
    frags.append(arrow(dx - wd / 2 - 4, cy, cx + cw / 2 + 4, cy, color=FIELD, sw=1.6))

    # Внутрішня межа DRY: перетягнеш → передчасне узагальнення (застереження знизу праворуч)
    warn_y = cy + 140
    frags.append(line(dx, cy + hd / 2 + 2, dx, warn_y - 34, color=POS, sw=1.6, dash="4,4"))
    wtxt, ww, wh = textbox(dx, warn_y, ["перетягнеш DRY —", "ХИБНА АБСТРАКЦІЯ:", "одна абстракція силою", "тримає два різні знання"],
                           size=12, pad=12, fill="#fdecea", stroke=POS, sw=1.8)
    frags.append(rect(dx - ww / 2, warn_y - wh / 2, ww, wh, fill="#fdf0ee", stroke=POS, sw=1.8, rx=8))
    frags.append(text(dx, warn_y - wh / 2 + 20, "перетягнеш DRY —", size=12, color=INK))
    frags.append(text(dx, warn_y - wh / 2 + 38, "ХИБНА АБСТРАКЦІЯ", size=13, color=POS, bold=True))
    frags.append(text(dx, warn_y - wh / 2 + 56, "одна силою тримає", size=12, color=INK))
    frags.append(text(dx, warn_y - wh / 2 + 73, "два різні знання", size=12, color=INK))

    render(os.path.join(OUT, 'three-guards.svg'), W, H, *frags,
           title="Три застави проти складності-пасиву")


def refactor_ladder():
    """Драбина рефакторингу: клубок → інлайн → чесні функції → спільний хелпер,
    а праворуч на кожному щаблі той самий золотий еталон стоїть незмінним."""
    W, H = 940, 620
    frags = []

    # Ліва колонка — чотири стани коду, зверху вниз. Права — незмінний еталон.
    lx = 250          # центр лівих рамок
    gx = 720          # центр правої колонки (еталон)
    ys = [110, 250, 390, 530]   # центри чотирьох щаблів (з великим кроком)

    steps = [
        ("КЛУБОК", "#fdecea", POS, [
            "send_frame(p, len,", "crc, comp, be)",
            "вкладені if · 32 комбінації"]),
        ("ІНЛАЙН", "#fff6e6", "#b8860b", [
            "тіло вписане в кожен виклик —",
            "чотири голі копії, гілки викинуто"]),
        ("ЧЕСНІ ФУНКЦІЇ", "#eaf0fd", NEG, [
            "send_raw · send_crc ·",
            "send_compressed · send_be",
            "кожна робить рівно одне"]),
        ("СПІЛЬНИЙ ХЕЛПЕР", "#eafaf1", FIELD, [
            "envelope_begin() — конверт;",
            "кожна кличе його ЯВНО"]),
    ]

    # заголовки колонок
    frags.append(text(lx, 60, "стан коду", size=13, color=MUTED, italic=True))
    frags.append(text(gx, 60, "золотий еталон", size=13, color=MUTED, italic=True))

    golden = ["raw : AA 03 10 20 30 55",
              "crc : AA 03 10 20 30 3C 55",
              "comp: AA 02 1A 07 55",
              "be  : AA 03 30 20 10 8F 55"]

    box_w = 360   # фіксована ширина лівих рамок — з запасом під найдовший рядок
    for i, (name, fill, stroke, lines) in enumerate(steps):
        cy = ys[i]
        rows = [name] + lines
        h = len(rows) * 20 + 20
        x = lx - box_w / 2
        y = cy - h / 2
        frags.append(rect(x, y, box_w, h, fill=fill, stroke=stroke, sw=2.2, rx=8))
        frags.append(text(lx, y + 24, name, size=14, color=stroke, bold=True))
        for j, ln in enumerate(lines):
            frags.append(text(lx, y + 46 + j * 20, ln, size=12, color=INK))
        # стрілка вниз до наступного щабля
        if i < len(steps) - 1:
            frags.append(arrow(lx, y + h + 2, lx, ys[i + 1] - (len(steps[i + 1][3]) + 1) * 20 / 2 - 12, color=INK, sw=1.8))

    # Права колонка — один блок еталона на всю висоту, з підписом «незмінний»
    gy_top, gy_bot = 90, 570
    gh = gy_bot - gy_top
    gw = 380
    frags.append(rect(gx - gw / 2, gy_top, gw, gh, fill="#f4f6f8", stroke=MUTED, sw=1.6, rx=8))
    # моноширинні рядки еталона рівним стовпчиком
    for j, ln in enumerate(golden):
        frags.append(text(gx, gy_top + 40 + j * 26, ln, size=12, color=INK, anchor="middle"))
    frags.append(text(gx, gy_top + 40 + len(golden) * 26 + 14,
                      "той самий на КОЖНОМУ щаблі", size=12, color=FIELD, bold=True))
    frags.append(text(gx, gy_top + 40 + len(golden) * 26 + 34,
                      "поведінка не змінюється", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, 'refactor-ladder.svg'), W, H, *frags,
           title="Драбина рефакторингу: форма змінюється, поведінка — ні")


def three_origins():
    """Стрічка часу народження трьох гасел: KISS (авіація, сер. XX ст.),
    YAGNI (проєкт C3, кін. 1990-х), DRY (книжка, 1999) — кожне як
    протиотрута до своєї хвороби."""
    W, H = 900, 470
    frags = []

    # Горизонтальна вісь часу
    axis_y = 150
    x0, x1 = 70, W - 40
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.2))
    frags.append(arrow(x1 - 24, axis_y, x1, axis_y, color=INK, sw=2.2))
    frags.append(text(x1 - 6, axis_y - 14, "час", size=13, color=MUTED, italic=True, anchor="end"))

    # Три вузли на осі. x підібрано так, щоб картки під ними не налазили.
    stops = [
        (200, "сер. XX ст.", "KISS", FIELD, "#eafaf1",
         ["з АВІАЦІЇ", "Келлі Джонсон,", "Lockheed Skunk Works", "(U-2, SR-71)"],
         ["крихкість складного —", "нема кому полагодити", "в полі"]),
        (500, "кін. 1990-х", "YAGNI", NEG, "#eaf0fd",
         ["з ПРОЄКТУ C3", "Кент Бек,", "Рон Джеффріс —", "екстремальне прогр."],
         ["проєктування", "наперед УСЬОГО", "(big design up front)"]),
        (760, "1999", "DRY", POS, "#fdecea",
         ["з КНИЖКИ", "Гант і Томас,", "«Прагматичний", "програміст»"],
         ["розсинхрон —", "одне знання", "у двох місцях"]),
    ]

    for x, era, name, col, fillc, who, sick in stops:
        # вузол на осі
        frags.append(circle(x, axis_y, 8, fill=col, stroke=INK, sw=1.8))
        # рік/епоха над віссю
        frags.append(text(x, axis_y - 40, era, size=13, color=INK, bold=True))
        # виноска вниз до картки
        frags.append(line(x, axis_y + 8, x, axis_y + 34, color=col, sw=1.6))

        # Картка гасла: назва (жирна кольорова) + хто/звідки
        cy = axis_y + 112
        bw, bh = 196, 122
        frags.append(rect(x - bw / 2, cy - bh / 2, bw, bh, fill=fillc, stroke=col, sw=2, rx=8))
        frags.append(text(x, cy - bh / 2 + 24, name, size=17, color=col, bold=True))
        ly = cy - bh / 2 + 48
        for i, ln in enumerate(who):
            b = (i == 0)
            frags.append(text(x, ly + i * 16, ln, size=11, color=(MUTED if b else INK), bold=b))

        # Хвороба, проти якої народилося (нижче картки, у сірій рамці)
        wy = cy + 124
        ww, wh = 196, 92
        frags.append(rect(x - ww / 2, wy - wh / 2, ww, wh, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=8))
        frags.append(text(x, wy - wh / 2 + 18, "проти хвороби:", size=11, color=POS, bold=True))
        for i, ln in enumerate(sick):
            frags.append(text(x, wy - wh / 2 + 38 + i * 16, ln, size=11, color=INK))
        # тонкий зв'язок картка → хвороба
        frags.append(line(x, cy + bh / 2 + 2, x, wy - wh / 2 - 2, color=MUTED, sw=1.2, dash="3,3"))

    render(os.path.join(OUT, 'three-origins.svg'), W, H, *frags,
           title="Народження трьох гасел на стрічці часу")


three_guards()
refactor_ladder()
three_origins()
print("ok")
