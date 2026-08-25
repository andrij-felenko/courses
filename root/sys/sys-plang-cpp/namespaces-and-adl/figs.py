# -*- coding: utf-8 -*-
"""Фігури до теми «Простори імен і пошук, залежний від аргументів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_lookup_and_adl():
    W, H = 1000, 530
    f = []

    # ── виклик ─────────────────────────────────────────────────────────────
    f.append(textbox(500, 55, "log(w, 1)   — некваліфіковане ім'я у виклику",
                     size=16, bold=True, fill="#eef3f8")[0])
    f.append(arrow(430, 80, 250, 116))
    f.append(arrow(570, 80, 750, 116))

    # ── ліва панель: звичайний пошук ───────────────────────────────────────
    f.append(rect(50, 120, 400, 200, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(250, 152, "Звичайний пошук", size=16, bold=True))
    f.append(mtext(250, 190, ["іде назовні по областях:",
                              "блок → клас → простір → глобальна;",
                              "спиняється на ПЕРШІЙ із таким іменем"],
                   size=13, color=MUTED))
    f.append(textbox(250, 285, "::log(lib::W, long)", size=14, fill="#eaf0fd", stroke=NEG)[0])

    # ── права панель: ADL ──────────────────────────────────────────────────
    f.append(rect(550, 120, 400, 200, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(750, 152, "Пошук за аргументами", size=16, bold=True))
    f.append(mtext(750, 190, ["бере ТИПИ аргументів:",
                              "lib::W → простір lib;",
                              "int → нічого не додає"],
                   size=13, color=MUTED))
    f.append(textbox(750, 285, "lib::log(W, int)", size=14, fill="#fdecea", stroke=POS)[0])

    # ── злиття ─────────────────────────────────────────────────────────────
    f.append(arrow(250, 322, 448, 360))
    f.append(arrow(750, 322, 552, 360))
    f.append(textbox(500, 388, "спільна множина кандидатів", size=15, bold=True)[0])
    f.append(arrow(500, 414, 500, 452))
    f.append(textbox(500, 480, "розв'язання перевантажень → lib::log(W, int)",
                     size=15, fill="#eef7ee", stroke=FIELD)[0])

    render(os.path.join(OUT, 'lookup-and-adl.svg'), W, H, *f)


def fig_associated_entities():
    W, H = 1020, 480
    f = []

    f.append(textbox(510, 55, "dump(std::vector<lib::Widget>{}, 3.5)",
                     size=16, bold=True, fill="#eef3f8")[0])
    f.append(arrow(430, 80, 295, 116))
    f.append(arrow(590, 80, 760, 116))

    # ── аргумент 1 ─────────────────────────────────────────────────────────
    f.append(rect(50, 120, 490, 235, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(295, 150, "аргумент 1: std::vector<lib::Widget>", size=15, bold=True))
    f.append(textbox(175, 215, "шаблон vector\n→ простір std", size=13,
                     fill="#eaf0fd", stroke=NEG)[0])
    f.append(textbox(415, 215, "аргумент lib::Widget\n→ клас Widget, простір lib", size=13,
                     fill="#fdecea", stroke=POS)[0])
    f.append(mtext(295, 300, ["асоційовано: простори std і lib,",
                              "класи vector<lib::Widget> і lib::Widget"],
                   size=13, color=MUTED))

    # ── аргумент 2 ─────────────────────────────────────────────────────────
    f.append(rect(580, 120, 390, 235, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(775, 150, "аргумент 2: double", size=15, bold=True))
    f.append(textbox(775, 215, "вбудований тип", size=13)[0])
    f.append(mtext(775, 300, ["асоційовано: нічого —",
                              "простору на ім'я «double» немає"],
                   size=13, color=MUTED))

    # ── підсумок ───────────────────────────────────────────────────────────
    f.append(arrow(295, 357, 440, 400))
    f.append(arrow(775, 357, 620, 400))
    f.append(textbox(510, 428, "ADL шукає ім'я dump у просторах std і lib",
                     size=15, bold=True, fill="#eef7ee", stroke=FIELD)[0])

    render(os.path.join(OUT, 'associated-entities.svg'), W, H, *f)


def fig_hidden_friend():
    W, H = 1000, 470
    f = []

    # ── ліва панель ────────────────────────────────────────────────────────
    f.append(rect(40, 45, 440, 385, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(260, 80, "Вільна функція в просторі", size=16, bold=True))
    f.append(mtext(260, 122, ["namespace lib {",
                              "  bool operator==(Money, Money);",
                              "}"], size=13))
    f.append(textbox(260, 215, "звичайний пошук:\nбачить усюди, де видно lib", size=13,
                     fill="#eaf0fd", stroke=NEG)[0])
    f.append(textbox(260, 300, "ADL: бачить через аргумент", size=13,
                     fill="#fdecea", stroke=POS)[0])
    f.append(mtext(260, 375, ["потрапляє в множину кандидатів",
                              "КОЖНОГО порівняння в зоні видимості"],
                   size=12, color=MUTED))

    # ── права панель ───────────────────────────────────────────────────────
    f.append(rect(520, 45, 440, 385, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(740, 80, "Прихований друг", size=16, bold=True))
    f.append(mtext(740, 122, ["class Money {",
                              "  friend bool operator==(...);",
                              "};"], size=13))
    f.append(textbox(740, 215, "звичайний пошук:\nне бачить ніде", size=13,
                     fill="#eaf0fd", stroke=NEG)[0])
    f.append(textbox(740, 300, "ADL: лише коли аргумент — Money", size=13,
                     fill="#fdecea", stroke=POS)[0])
    f.append(mtext(740, 375, ["у чужі множини кандидатів",
                              "не потрапляє взагалі"],
                   size=12, color=MUTED))

    render(os.path.join(OUT, 'hidden-friend.svg'), W, H, *f)


fig_lookup_and_adl()
fig_associated_entities()
fig_hidden_friend()
print("ok")
