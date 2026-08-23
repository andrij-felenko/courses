# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def cbox(cx, cy, w, h, s, **kw):
    """fitbox із центром (cx, cy)."""
    return fitbox(cx - w / 2, cy - h / 2, w, h, s, **kw)


def fig_parse_vs_validate():
    """Перевірка віддає біт (тип не змінюється); розбір віддає вужчий тип."""
    W, H = 1000, 390
    frags = []

    # роздільник смуг
    frags.append(line(60, 207, 940, 207, color=LINE, sw=1.2, dash="4 5"))

    xin, xfn, xout, xnote = 180, 410, 620, 852

    def lane(y, label, lcol, inp, fn, out, out_fill, out_stroke, note, note_col):
        f = []
        f.append(text(64, y - 52, label, size=14, bold=True, color=lcol, anchor="start"))
        f.append(cbox(xin, y, 172, 50, inp, size=14))
        f.append(cbox(xfn, y, 162, 46, fn, size=14, fill="#eef2f6"))
        f.append(cbox(xout, y, 152, 50, out, size=14, fill=out_fill, stroke=out_stroke))
        f.append(arrow(xin + 86, y, xfn - 81, y))
        f.append(arrow(xfn + 81, y, xout - 76, y))
        f.append(arrow(xout + 76, y, xnote - 84, y))
        f.append(mtext(xnote, y - 8, note, size=12.5, color=note_col, lh=1.35))
        return f

    frags += lane(125, "ПЕРЕВІРИТИ (validate)", MUTED,
                  '"a@b.com"\nтип: рядок', "isEmail(s)",
                  'true\nтип: булеве', "#fbeeec", POS,
                  ["далі — знову рядок", "знання втрачено"], POS)

    frags += lane(292, "РОЗІБРАТИ (parse)", MUTED,
                  '"a@b.com"\nтип: рядок', "parseEmail(s)",
                  "Email\nтип: Email", "#eafaf1", FIELD,
                  ["далі — вже Email", "гарантія в типі"], FIELD)

    render(os.path.join(OUT, 'parse-vs-validate.svg'), W, H, *frags,
           title="Перевірка віддає біт, розбір віддає тип")


def fig_trust_boundary():
    """Зовні недовірене — межа розбирає — всередині типи; що не пройшло, вертається."""
    W, H = 1000, 470
    frags = []

    # ── ЗОВНІ (ліворуч) ──────────────────────────────────────────────
    frags.append(text(186, 66, "ЗОВНІ — недовірений вхід", size=14, bold=True, color=MUTED))
    lb = [
        (120, '"23.5"\nрядок із форми'),
        (192, '2000.0\nсміття з давача'),
        (264, '{ "id": "" }\nзапит із мережі'),
    ]
    for cy, s in lb:
        frags.append(cbox(186, cy, 214, 50, s, size=13, fill="#fbeeec", stroke=POS))

    # ── МЕЖА (посередині) ────────────────────────────────────────────
    frags.append(text(430, 66, "МЕЖА", size=14, bold=True, color=INK))
    frags.append(line(430, 88, 430, 150, color=INK, sw=2.4, dash="6 6"))
    frags.append(line(430, 200, 430, 322, color=INK, sw=2.4, dash="6 6"))
    frags.append(cbox(430, 175, 128, 46, "parse()", size=14, bold=True, fill=BG, stroke=INK, sw=2))

    # входи → межа
    frags.append(arrow(293, 120, 366, 166))
    frags.append(arrow(293, 192, 366, 175))
    frags.append(arrow(293, 264, 366, 186))

    # ── УСЕРЕДИНІ (праворуч) ─────────────────────────────────────────
    frags.append(text(760, 66, "УСЕРЕДИНІ — типи, довіра", size=14, bold=True, color=FIELD))
    frags.append(cbox(662, 150, 198, 48, "Celsius(23.5)", size=13.5, fill="#eafaf1", stroke=FIELD, sw=1.8))
    frags.append(cbox(662, 222, 198, 48, 'DeviceId("d7")', size=13.5, fill="#eafaf1", stroke=FIELD, sw=1.8))
    frags.append(arrow(494, 172, 561, 150))
    frags.append(arrow(494, 184, 561, 222))
    frags.append(text(690, 300, "ядро оперує лише типами —", size=13, color=MUTED, italic=True))
    frags.append(text(690, 320, "не перевіряє повторно", size=13, color=MUTED, italic=True))

    # ── що не пройшло — вертається назовні ───────────────────────────
    frags.append(arrow(415, 200, 300, 344, color=POS, sw=1.8))
    frags.append(text(340, 372, "не пройшло розбір —", size=12.5, color=POS))
    frags.append(text(340, 391, "помилка назовні", size=12.5, color=POS))

    render(os.path.join(OUT, 'trust-boundary.svg'), W, H, *frags,
           title="Межа довіри: розбір на вході, типи всередині")


def fig_two_slogans_one_idea():
    """Два гасла (Мінскі, Кінг) сходяться в один хід: звузити тип до дозволених значень."""
    W, H = 1040, 430
    f = []

    # ── джерело 1: Мінскі (проєкт-час) ───────────────────────────────
    b1, w1, h1 = textbox(255, 118, "ЯРОН МІНСКІ · 2010\n«зроби недозволений\nстан невиразним»",
                         size=14, fill="#eaf0fd", stroke=NEG, sw=1.8)
    f.append(b1)
    f.append(text(255, 176, "проєкт-час:", size=12, color=MUTED, italic=True))
    f.append(text(255, 192, "тип без зайвого стану", size=12, color=MUTED, italic=True))

    # ── джерело 2: Кінг (межа) ───────────────────────────────────────
    b2, w2, h2 = textbox(255, 300, "АЛЕКСІС КІНГ · 2019\n«розбирай,\nне перевіряй»",
                         size=14, fill="#eafaf1", stroke=FIELD, sw=1.8)
    f.append(b2)
    f.append(text(255, 358, "межа:", size=12, color=MUTED, italic=True))
    f.append(text(255, 374, "сирий вхід → вужчий тип", size=12, color=MUTED, italic=True))

    # ── ціль: один хід ───────────────────────────────────────────────
    bt, wt, ht = textbox(770, 210, "ЗВУЗЬ ТИП ДО МНОЖИНИ\nлише ДОЗВОЛЕНИХ значень",
                         size=14, bold=True, fill=BG, stroke=INK, sw=2.2, min_w=250)
    f.append(bt)

    # ── стрілки, що сходяться в один хід ─────────────────────────────
    f.append(arrow(255 + w1 / 2 + 4, 122, 770 - wt / 2 - 4, 198))
    f.append(arrow(255 + w2 / 2 + 4, 296, 770 - wt / 2 - 4, 224))

    # ── підпис під ціллю: значення = доказ ───────────────────────────
    f.append(text(770, 300, "значення такого типу —", size=12.5, color=MUTED, italic=True))
    f.append(text(770, 317, "уже доказ, що інваріант тримається", size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'two-slogans-one-idea.svg'), W, H, *f,
           title="Дві дороги до одного ходу")


def fig_pipeline():
    """Сирий JSON → форма → 3 незалежні поля → агрегація → розвилка все-або-нічого."""
    W, H = 860, 660
    f = []

    # вхід — недовірений сирий JSON
    f.append(cbox(430, 78, 540, 52,
                  'сирий JSON із мережі  ·  недовірений\n'
                  '{ "deviceId": …, "targetTemp": …, "action": … }',
                  size=13, fill="#fbeeec", stroke=POS))
    f.append(arrow(430, 105, 430, 143))

    # розбір форми
    f.append(cbox(430, 168, 380, 46, "розбір форми: JSON.parse → це об'єкт?", size=13))

    # три незалежні розбірники полів
    px = (150, 430, 710)
    f.append(cbox(px[0], 264, 210, 48, "DeviceId.parse", size=14))
    f.append(cbox(px[1], 264, 210, 48, "Celsius.parse", size=14))
    f.append(cbox(px[2], 264, 210, 48, "Action.parse", size=14))
    f.append(arrow(430, 193, 160, 238))
    f.append(arrow(430, 193, 430, 238))
    f.append(arrow(430, 193, 700, 238))

    # наслідок кожного поля — мішаний приклад: дві хиби, одне добре
    f.append(cbox(px[0], 344, 190, 36, "Err: порожній", size=13,
                  fill="#fbeeec", stroke=POS, color=POS))
    f.append(cbox(px[1], 344, 240, 36, "Err: 2000 поза межами", size=13,
                  fill="#fbeeec", stroke=POS, color=POS))
    f.append(cbox(px[2], 344, 190, 36, "Ok: heat", size=13,
                  fill="#eafaf1", stroke=FIELD, color=FIELD))
    f.append(arrow(px[0], 290, px[0], 324))
    f.append(arrow(px[1], 290, px[1], 324))
    f.append(arrow(px[2], 290, px[2], 324))

    # агрегація
    f.append(cbox(430, 434, 320, 46, "агрегація: зібрати ВСІ Err", size=13))
    f.append(arrow(px[0], 362, 395, 412))
    f.append(arrow(px[1], 362, 430, 412))
    f.append(arrow(px[2], 362, 465, 412))

    # розвилка все-або-нічого
    f.append(cbox(215, 566, 320, 66,
                  "FieldError[] — увесь список\n→ назовні, тому хто прислав",
                  size=12.5, fill="#fbeeec", stroke=POS))
    f.append(cbox(645, 566, 340, 66,
                  "Command{ DeviceId, Celsius, Action }\n→ ядро без повторних перевірок",
                  size=12.5, fill="#eafaf1", stroke=FIELD))
    f.append(arrow(415, 459, 240, 531, color=POS, sw=1.9))
    f.append(arrow(445, 459, 620, 531, color=FIELD, sw=1.9))

    render(os.path.join(OUT, 'pipeline.svg'), W, H, *f,
           title="Конвеєр валідації на межі: усе або нічого")


def fig_first_vs_all():
    """Перша хиба проти повного списку: три подорожі проти однієї."""
    W, H = 900, 380
    f = []

    f.append(line(450, 56, 450, 344, color=LINE, sw=1.2, dash="5 6"))

    # ── ліворуч: спинитись на першій ──
    f.append(text(225, 72, "СПИНИТИСЬ НА ПЕРШІЙ", size=14, bold=True, color=MUTED))
    f.append(cbox(225, 150, 340, 64,
                  '{ error: "deviceId порожній" }\n…і мовчить про решту',
                  size=12.5, fill="#fbeeec", stroke=POS))
    f.append(mtext(225, 232,
                   ["спроба 1 → 1 хиба, правиш",
                    "спроба 2 → наступна хиба",
                    "спроба 3 → аж тепер пройшло"],
                   size=12.5, lh=1.32))
    f.append(text(225, 314, "3 подорожі до сервера", size=13.5, bold=True, color=POS))

    # ── праворуч: зібрати всі ──
    f.append(text(675, 72, "ЗІБРАТИ ВСІ", size=14, bold=True, color=FIELD))
    f.append(cbox(675, 150, 360, 80,
                  "{ errors: [\n  deviceId, targetTemp, action\n] }",
                  size=12.5, fill="#eafaf1", stroke=FIELD))
    f.append(mtext(675, 244,
                   ["одна відповідь — увесь список",
                    "правиш усі поля за раз"],
                   size=12.5, lh=1.32))
    f.append(text(675, 314, "1 подорож", size=13.5, bold=True, color=FIELD))

    render(os.path.join(OUT, 'first-vs-all.svg'), W, H, *f,
           title="Перша хиба проти повного списку")


if __name__ == '__main__':
    fig_parse_vs_validate()
    fig_trust_boundary()
    fig_two_slogans_one_idea()
    fig_pipeline()
    fig_first_vs_all()
    print("figures written to", OUT)
