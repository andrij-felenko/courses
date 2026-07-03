# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_two_layers():
    """Два рубежі failsafe: приймач і польотний контролер."""
    W, H = 760, 380
    p = []
    p.append(text(W/2, 28, "Два рубежі оборони: приймач і контролер", size=17, bold=True))

    # три стовпці: ефір, приймач, контролер
    # ефір
    p.append(fitbox(30, 70, 150, 70, "ефір\n(радіолінк)", size=13, bold=True,
                    fill="#eef2ff", stroke=NEG))
    # хвиля обірвана
    p.append(line(60, 175, 150, 175, color=MUTED, sw=2, dash="6 5"))
    p.append(text(105, 165, "сигнал зник", size=11, color=POS, italic=True))
    p.append(text(105, 205, "нема кадрів", size=11, color=MUTED))

    # приймач
    p.append(rect(230, 60, 230, 250, fill="#f4f6f8", stroke=LINE, sw=1.6))
    p.append(text(345, 84, "ПРИЙМАЧ (RX)", size=13, bold=True))
    p.append(text(345, 104, "рубіж 1", size=11, color=POS, bold=True))
    p.append(fitbox(250, 120, 190, 46, "лічить тишу:\nнема кадру довше T?", size=11.5, fill=BG))
    p.append(fitbox(250, 176, 190, 60,
                    "рішення про ВИХІД:\n• тримати останнє\n• зняти імпульси\n• віддати пресет",
                    size=11, fill="#fff7ed", stroke=POS))
    p.append(fitbox(250, 246, 190, 46, "що піде по дроту\nна контролер", size=11, fill=BG))

    # контролер
    p.append(rect(510, 60, 230, 250, fill="#f4f6f8", stroke=LINE, sw=1.6))
    p.append(text(625, 84, "КОНТРОЛЕР (FC)", size=13, bold=True))
    p.append(text(625, 104, "рубіж 2", size=11, color=FIELD, bold=True))
    p.append(fitbox(530, 120, 190, 46, "лічить свою тишу:\nнема валідного кадру?", size=11, fill=BG))
    p.append(fitbox(530, 176, 190, 60,
                    "ДІЯ в польоті:\n• утримати висоту\n• RTL / посадка\n• обрізати мотори",
                    size=11, fill="#eafaf0", stroke=FIELD))
    p.append(fitbox(530, 246, 190, 46, "рятує апарат,\nа не просто дріт", size=11, fill=BG))

    # стрілки
    p.append(arrow(180, 175, 228, 175))
    p.append(arrow(460, 185, 508, 185))
    p.append(text(484, 178, "дріт", size=10, color=MUTED))

    p.append(text(W/2, 350, "Приймач вирішує, ЩО класти на дріт; контролер вирішує, ЩО РОБИТИ в повітрі.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'two-layers.svg'), W, H, *p)


def fig_rx_modes():
    """Три відповіді приймача на дроті при втраті сигналу."""
    W, H = 760, 360
    p = []
    p.append(text(W/2, 28, "Що приймач кладе на дріт, коли сигнал зник", size=17, bold=True))

    cols = [
        (40,  "ТРИМАТИ", NEG, "#eef2ff",
         "останні значення\nзамерзають",
         "газ лишається таким,\nяким був — апарат\nмчить далі за інерцією",
         "небезпечно як\nпостійна поведінка"),
        (285, "ЗНЯТИ ІМПУЛЬСИ", POS, "#fff7ed",
         "дріт замовкає\nповністю",
         "контролер чує тишу\nй сам вмикає\nсвій failsafe",
         "чітко й однозначно —\nрекомендований"),
        (530, "ПРЕСЕТ", FIELD, "#eafaf0",
         "задані наперед\nзначення каналів",
         "газ у нуль, перемикач\nу режим RTL —\nконтролер виконує",
         "працює лише якщо\nконтролер вірить\nканалам"),
    ]
    for x, name, col, fill, sub, mid, note in cols:
        p.append(rect(x, 62, 200, 250, fill=fill, stroke=col, sw=1.8))
        p.append(text(x+100, 88, name, size=13.5, bold=True, color=col))
        p.append(line(x+16, 100, x+184, 100, color=col, sw=1))
        p.append(fitbox(x+14, 112, 172, 44, sub, size=11.5, fill=BG, stroke=MUTED))
        p.append(fitbox(x+14, 166, 172, 66, mid, size=11, fill=BG, stroke=MUTED))
        p.append(fitbox(x+14, 242, 172, 58, note, size=11, fill="#ffffff", stroke=col))

    render(os.path.join(IMG, 'rx-modes.svg'), W, H, *p)


def fig_timeout_chain():
    """Часова вісь: кадри йдуть → зникли → guard → стадії."""
    W, H = 760, 340
    p = []
    p.append(text(W/2, 28, "Ланцюг часу: від пропущеного кадру до дії", size=17, bold=True))

    axis_y = 150
    p.append(line(40, axis_y, 720, axis_y, color=INK, sw=2))
    p.append(text(720, axis_y+22, "час →", size=11, color=MUTED, anchor="end"))

    # нормальні кадри (тики)
    for i in range(6):
        x = 60 + i*22
        p.append(line(x, axis_y-10, x, axis_y+10, color=FIELD, sw=2.5))
    p.append(text(115, axis_y-24, "кадри йдуть", size=11, color=FIELD))

    # момент зникнення
    xlost = 200
    p.append(line(xlost, axis_y-40, xlost, axis_y+40, color=POS, sw=2, dash="4 4"))
    p.append(text(xlost, axis_y-48, "останній кадр", size=11, color=POS, anchor="middle"))

    # тиша
    for i in range(10):
        x = xlost + 14 + i*20
        p.append(text(x, axis_y+5, "×", size=13, color=MUTED, anchor="middle"))

    # guard-вікно
    xg1, xg2 = xlost, 340
    p.append(rect(xg1, axis_y+30, xg2-xg1, 34, fill="#fff7ed", stroke=POS, sw=1.4))
    p.append(fitbox(xg1, axis_y+30, xg2-xg1, 34, "guard-час\n(перечекати завмирання)", size=10, fill="none", stroke="none"))

    # стадія 1
    xs1a, xs1b = 340, 520
    p.append(rect(xs1a, axis_y+30, xs1b-xs1a, 34, fill="#eef2ff", stroke=NEG, sw=1.4))
    p.append(fitbox(xs1a, axis_y+30, xs1b-xs1a, 34, "стадія 1\nм'яко: утримати / рівний", size=10, fill="none", stroke="none"))
    p.append(line(xs1a, axis_y-40, xs1a, axis_y+30, color=NEG, sw=1.5, dash="4 4"))

    # стадія 2
    xs2a, xs2b = 520, 715
    p.append(rect(xs2a, axis_y+30, xs2b-xs2a, 34, fill="#eafaf0", stroke=FIELD, sw=1.4))
    p.append(fitbox(xs2a, axis_y+30, xs2b-xs2a, 34, "стадія 2\nрішуче: RTL / посадка", size=10, fill="none", stroke="none"))
    p.append(line(xs2a, axis_y-40, xs2a, axis_y+30, color=FIELD, sw=1.5, dash="4 4"))

    p.append(text(W/2, 300, "Короткий провал гасне в guard-вікні; справжня втрата дозріває до стадій.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'timeout-chain.svg'), W, H, *p)


def fig_action_ladder():
    """Драбина дій контролера — від найм'якшої до найрішучішої."""
    W, H = 720, 380
    p = []
    p.append(text(W/2, 28, "Драбина дій: що обрати під ситуацію", size=17, bold=True))

    rungs = [
        ("Утримати висоту / завис", "коли є GPS-утримання позиції; чекає повернення пілота", NEG, "#eef2ff"),
        ("SmartRTL — назад по сліду", "летить додому тим шляхом, яким прилетів (є лог маршруту)", "#2b7a9b", "#e8f4f8"),
        ("RTL — прямо додому", "піднявся й полетів по прямій до точки зльоту, там сів", FIELD, "#eafaf0"),
        ("Land — сісти тут і зараз", "нема куди летіти або нема GPS: керована посадка на місці", "#b8860b", "#fdf6e3"),
        ("Обрізати мотори", "остання межа: над людьми падіння краще, ніж некерований політ", POS, "#fdecea"),
    ]
    y0 = 62
    for i, (title, desc, col, fill) in enumerate(rungs):
        y = y0 + i*62
        p.append(rect(60, y, 600, 52, fill=fill, stroke=col, sw=1.6))
        p.append(text(78, y+22, title, size=13, bold=True, color=col, anchor="start"))
        p.append(text(78, y+41, desc, size=11, color=INK, anchor="start"))

    # стрілка «сильніше»
    p.append(arrow(30, y0+6, 30, y0+4*62+46))
    p.append(text(20, (y0 + y0+4*62+46)/2, "рішучіше", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'action-ladder.svg'), W, H, *p)


if __name__ == '__main__':
    fig_two_layers()
    fig_rx_modes()
    fig_timeout_chain()
    fig_action_ladder()
    print("figures written to", IMG)
