# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Послідовність graceful reset».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

AMBER   = "#b08900"
AMBERBG = "#fdf6e3"
BLUEBG  = "#eaf0fd"
GRNBG   = "#e9f7ef"
REDBG   = "#fdecea"
GREYBG  = "#eef2f7"


# ── 1. Жорсткий reset проти graceful: дві стрічки часу ───────────────────────
# Ідея: однакова мить «час перезавантажитись», але вгорі — обрив посеред справ
# (мотор крутиться, лог недописаний, сокет завис), внизу — упорядковане згортання.
def fig_hard_vs_graceful():
    W, H = 940, 470
    P = [text(W / 2, 30, "Жорсткий reset проти graceful: однакова мить, різний наслідок", size=17, bold=True),
         text(W / 2, 50, "«пора перезавантажитись» — питання лише в тому, ЯК саме обірвати поточну роботу",
              size=11, color=MUTED, italic=True)]

    trig_x = 250   # мить рішення «reset»

    # ── верхня стрічка: жорсткий reset ──
    yT = 130
    P.append(fitbox(40, yT - 26, 200, 24, "ЖОРСТКИЙ RESET", size=12, bold=True,
                    color=POS, fill=REDBG, stroke=POS))
    P.append(line(70, yT + 18, 880, yT + 18, color="#d0d5dd", sw=1.2))
    P.append(rect(70, yT, 180, 36, fill=GRNBG, stroke=FIELD, sw=1.3))
    P.append(text(160, yT + 22, "звичайна робота", size=10.5, color=FIELD, bold=True))
    # обрив
    P.append(line(trig_x, yT - 12, trig_x, yT + 54, color=POS, sw=2.2))
    P.append(text(trig_x, yT - 18, "обрив", size=10.5, color=POS, bold=True))
    P.append(rect(trig_x, yT, 30, 36, fill=POS, stroke=POS, sw=1.2))
    P.append(text(trig_x + 95, yT + 22, "≈ миттєво new boot", size=10.5, color=MUTED, anchor="start"))
    # наслідки обриву
    bad = ["✗ мотор лишився крутитись", "✗ лог недописаний — сміття у флеш",
           "✗ сокет завис, давач у дивному стані"]
    for i, s in enumerate(bad):
        P.append(text(310, yT + 58 + i * 21, s, size=10.5, color=POS, bold=True, anchor="start"))

    # ── нижня стрічка: graceful ──
    yG = 320
    P.append(fitbox(40, yG - 26, 200, 24, "GRACEFUL RESET", size=12, bold=True,
                    color=FIELD, fill=GRNBG, stroke=FIELD))
    P.append(line(70, yG + 18, 880, yG + 18, color="#d0d5dd", sw=1.2))
    P.append(rect(70, yG, 180, 36, fill=GRNBG, stroke=FIELD, sw=1.3))
    P.append(text(160, yG + 22, "звичайна робота", size=10.5, color=FIELD, bold=True))
    P.append(line(trig_x, yG - 12, trig_x, yG + 54, color=NEG, sw=2.0, dash="4 3"))
    P.append(text(trig_x, yG - 18, "рішення «reset»", size=10.5, color=NEG, bold=True))
    # упорядковане згортання
    seq = [("безпечний\nстан", AMBER, AMBERBG), ("зберегти\nстан", NEG, BLUEBG),
           ("закрити\nзв'язок", NEG, BLUEBG), ("слід +\nflush", FIELD, GRNBG)]
    x = trig_x + 10
    for lbl, col, fill in seq:
        P.append(fitbox(x, yG, 96, 36, lbl, size=9.5, bold=True, color=col, fill=fill, stroke=col))
        x += 102
    P.append(rect(x, yG, 30, 36, fill=FIELD, stroke=FIELD, sw=1.2))
    P.append(text(x + 15, yG + 22, "↻", size=15, color=BG, bold=True))
    P.append(text(trig_x + 230, yG + 70, "коротке, кероване вікно згортання — і лише тоді new boot",
                  size=10.5, color=FIELD, bold=True))

    fr, w, h = textbox(W / 2, 440,
                       "Та сама подія. Жорсткий reset рубає посеред дії; graceful спершу впорядковано згортає те, що може нашкодити.",
                       size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/hard-vs-graceful.svg", W, H, *P)


# ── 2. Драбина згортання: порядок кроків і ЧОМУ саме такий ───────────────────
# Ідея: згори вниз — від найтерміновішого (фізична шкода) до останнього (тригер).
# Колір тоном показує «спершу не нашкодь → тоді не загуби → тоді попрощайся».
def fig_ladder():
    W, H = 960, 470
    P = [text(W / 2, 30, "Драбина graceful-згортання: від «не нашкодь» до «натисни тригер»", size=17, bold=True),
         text(W / 2, 50, "порядок не випадковий — кожен крок вимикає менш термінову загрозу за попередній",
              size=11, color=MUTED, italic=True)]

    rungs = [
        ("1. Безпечний стан виходів", "мотори стоп, нагрів off, клапан у безпеку — поки ще керуємо",
         POS, REDBG),
        ("2. Зберегти критичний стан", "лічильники, незбережені дані → NVS/FRAM (як при power-fail)",
         AMBER, AMBERBG),
        ("3. Згорнути зв'язок із світом", "закрити сокети, сказати «йду на reset» вузлам поруч",
         NEG, BLUEBG),
        ("4. Лишити слід", "причина reset + лічильник перезавантажень — щоб діагностувати потім",
         FIELD, GRNBG),
        ("5. Flush памʼяті й тригер", "DSB: дочекатись запис-буферів → esp_restart / NVIC_SystemReset",
         "#5b21b6", "#ede9fe"),
    ]
    x0, w = 90, 780
    y = 90
    rh = 56
    for i, (title_, sub, col, fill) in enumerate(rungs):
        P.append(rect(x0, y, w, rh, fill=fill, stroke=col, sw=1.8))
        P.append(text(x0 + 16, y + 24, title_, size=13, color=col, bold=True, anchor="start"))
        P.append(text(x0 + 16, y + 44, sub, size=10.5, color=INK, anchor="start"))
        if i < len(rungs) - 1:
            P.append(arrow(x0 + w / 2, y + rh, x0 + w / 2, y + rh + 14, color=MUTED, sw=1.6))
        y += rh + 14

    # бічна вісь «терміновість»
    P.append(arrow(60, 96, 60, y - 14, color=MUTED, sw=1.5))
    P.append(text(40, (96 + y) / 2, "терміновість ↓", size=10.5, color=MUTED, bold=True, anchor="middle"))

    fr, fw, fh = textbox(W / 2, 448,
                         "Спершу те, що шкодить фізично (виходи), тоді те, що губиться назавжди (стан), і лише наприкінці — сам reset.",
                         size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/ladder.svg", W, H, *P)


# ── 3. Graceful — best-effort поверх твердої гарантії watchdog ────────────────
# Ідея: одна вісь часу від «рішення reset». Зелене вікно — бюджет на згортання.
# Якщо встигли — тригер усередині вікна. Поверх усього — дедлайн watchdog:
# навіть якщо згортання зависло, сторож однаково перезапустить.
def fig_budget_vs_watchdog():
    W, H = 960, 430
    P = [text(W / 2, 30, "Graceful — це best-effort поверх твердої гарантії watchdog", size=17, bold=True),
         text(W / 2, 50, "згортання обмежене бюджетом; якщо воно само зависне — сторож усе одно перезапустить",
              size=11, color=MUTED, italic=True)]

    ax_y = 150
    x0, x1 = 90, 880
    P.append(arrow(x0, ax_y, x1, ax_y, color=INK, sw=1.8))
    P.append(text(x1, ax_y + 24, "час →", size=12, color=INK, bold=True))
    P.append(line(x0, ax_y - 8, x0, ax_y + 8, color=INK, sw=1.6))
    P.append(text(x0, ax_y - 16, "рішення «reset»", size=10.5, color=NEG, bold=True))

    budget_end = 430   # кінець бюджету згортання
    wd_end = 760       # дедлайн watchdog

    # зелене вікно бюджету
    P.append(rect(x0, ax_y - 26, budget_end - x0, 26, fill=GRNBG, stroke=FIELD, sw=1.6))
    P.append(text((x0 + budget_end) / 2, ax_y - 9, "бюджет згортання (мс)", size=11, color=FIELD, bold=True))
    P.append(line(budget_end, ax_y - 34, budget_end, ax_y + 10, color=FIELD, sw=1.4, dash="4 3"))

    # успішний випадок: тригер усередині бюджету
    P.append(line(360, ax_y, 360, ax_y + 46, color=NEG, sw=1.6))
    P.append(circle(360, ax_y + 46, 5, fill=NEG, stroke=NEG))
    P.append(text(360, ax_y + 66, "встигли → свій reset", size=10.5, color=NEG, bold=True))
    P.append(text(360, ax_y + 84, "(чисте, кероване згортання)", size=9.5, color=MUTED))

    # дедлайн watchdog — поверх усього
    P.append(rect(budget_end, ax_y - 26, wd_end - budget_end, 26, fill=AMBERBG, stroke=AMBER, sw=1.4))
    P.append(text((budget_end + wd_end) / 2, ax_y - 9, "запас", size=10, color=AMBER, bold=True))
    P.append(line(wd_end, ax_y - 40, wd_end, ax_y + 60, color=POS, sw=2.2))
    P.append(text(wd_end, ax_y - 48, "дедлайн watchdog", size=11, color=POS, bold=True))
    P.append(text(wd_end, ax_y + 78, "згортання зависло?", size=10, color=POS, bold=True))
    P.append(text(wd_end, ax_y + 95, "сторож рубає однаково", size=10, color=POS, bold=True))

    # підпис рівнів
    P.append(text(x0, ax_y + 130, "Два рівні: graceful намагається (м'яко), watchdog гарантує (жорстко). Ніколи не лишай лише перший.",
                  size=11, color=INK, bold=True, anchor="start"))

    fr, fw, fh = textbox(W / 2, 400,
                         "Бюджет коротший за дедлайн сторожа: graceful має або встигнути, або поступитися жорсткому reset.",
                         size=12, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/budget-vs-watchdog.svg", W, H, *P)


if __name__ == "__main__":
    fig_hard_vs_graceful()
    fig_ladder()
    fig_budget_vs_watchdog()
    print("OK: 3 figures -> img/")
