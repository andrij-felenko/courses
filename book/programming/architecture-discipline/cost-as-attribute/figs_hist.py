# -*- coding: utf-8 -*-
# Фігури для вставки hist-tco.md (окремо від figs.py статті-власника).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: часова вісь TCO — від «звіту про безлад» до слова року ──────────
def fig_timeline():
    W, H = 1040, 470
    els = []
    els.append(text(W/2, 32, "Як народилася повна вартість володіння", size=17, bold=True))

    # горизонтальна вісь
    ax_y = 150
    els.append(line(70, ax_y, W-70, ax_y, color=MUTED, sw=2))

    # чотири віхи: (x, рік, заголовок над, тіло під)
    marks = [
        (170, "1986", "Gartner б'є на сполох", "рахунок за ПК роз'їхався\nпо відділах — обліку нема"),
        (430, "1987", "Кірвін рахує весь цикл", "модель life-cycle-cost\nстає TCO для настільних"),
        (700, "1996", "Цифра трясе галузь", "≈ 10 000 $ на рік за один\nстіл — уп'ятеро над ціною"),
        (940, "1998", "Слово увійшло в мову", "TCO — стандартна графа\nбудь-якої ІТ-закупівлі"),
    ]
    for mx, year, head, body in marks:
        els.append(circle(mx, ax_y, 7, fill=NEG, stroke=NEG))
        # рік — маленьким жирним просто над вузлом
        els.append(text(mx, ax_y - 16, year, size=14, bold=True, color=NEG))
        # заголовок віхи — рамка НАД віссю
        b, bw, bh = textbox(mx, ax_y - 78, head, size=12.5, bold=True, min_w=190,
                            fill="#eef4ff", stroke=NEG)
        els.append(b)
        # тіло — рамка ПІД віссю
        b2, bw2, bh2 = textbox(mx, ax_y + 92, body, size=11.5, min_w=200, fill=FILL)
        els.append(b2)

    els.append(text(W/2, H-22,
                    "десять років між тихим звітом і моментом, коли ціна володіння стала головним числом закупівлі",
                    size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'tco-timeline.svg'), W, H, *els)


# ── Фігура 2: що саме шокувало — 20 % на ціннику, 80 % під ним ────────────────
def fig_shock():
    W, H = 940, 470
    els = []
    els.append(text(W/2, 32, "Чому цифра TCO струснула закупівлі: видно було п'яту частину", size=16, bold=True))

    # вертикальний стовпчик повної вартості: верхні 20 % — ціна купівлі, решта — прихована
    bar_x, bar_w = 150, 150
    bar_top, bar_bot = 80, 400
    total_h = bar_bot - bar_top
    visible_h = total_h * 0.20
    split_y = bar_top + visible_h

    # видима частина (ціна купівлі)
    els.append(rect(bar_x, bar_top, bar_w, visible_h, fill="#eef4ff", stroke=NEG, sw=2))
    els.append(text(bar_x + bar_w/2, bar_top + visible_h/2 + 4, "≈ 20 %", size=14, bold=True, color=NEG))
    # прихована частина (володіння)
    els.append(rect(bar_x, split_y, bar_w, total_h - visible_h, fill="#f7f7f7", stroke=MUTED, sw=1.5, rx=6))
    els.append(text(bar_x + bar_w/2, split_y + (total_h - visible_h)/2 + 6, "≈ 80 %", size=18, bold=True, color=MUTED))

    # підписи стовпчика — назовні ліворуч, повз рамку
    els.append(text(bar_x - 14, bar_top + visible_h/2 + 4, "ціна на ціннику", size=12,
                    anchor="end", color=NEG))
    els.append(text(bar_x - 14, split_y + 24, "підтримка,", size=12, anchor="end", color=MUTED))
    els.append(text(bar_x - 14, split_y + 42, "простої, навчання,", size=12, anchor="end", color=MUTED))
    els.append(text(bar_x - 14, split_y + 60, "адміністрування", size=12, anchor="end", color=MUTED))

    # права колонка — чотири рядки прихованого, з ЗАПАСОМ між рядками
    labels = [
        (135, "чужа рука", "хтось інший ставить ПЗ, лагодить,\nоновлює — це його робочий час"),
        (215, "простій", "поки стіл не працює, не працює\nй людина за ним"),
        (295, "самопоміч", "колеги вчать одне одного в обхід\nІТ — час, якого ніхто не рахує"),
        (375, "накопичення", "усе це — щороку, помножене\nна кожен стіл у конторі"),
    ]
    lx = 400
    for ly, cap, body in labels:
        b, bw, bh = textbox(lx, ly, cap, size=12.5, bold=True, min_w=150,
                            fill="#fff8e1", stroke="#b8860b")
        els.append(b)
        els.append(text(lx + bw/2 + 16, ly - 8, body.split("\n")[0], size=11, anchor="start", color=INK))
        els.append(text(lx + bw/2 + 16, ly + 10, body.split("\n")[1], size=11, anchor="start", color=INK))

    els.append(text(W/2, H-22,
                    "покупець порівнював машини за верхньою п'ятою частиною — а платив за всю висоту стовпчика",
                    size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'tco-shock.svg'), W, H, *els)


if __name__ == '__main__':
    fig_timeline()
    fig_shock()
    print("figs_hist done")
