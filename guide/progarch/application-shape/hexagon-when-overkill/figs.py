# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

RULES = "#27ae60"    # правила / стабільне ядро — зелене
INFRA = "#c0392b"    # інфраструктура / деталь — червоне
TEST  = "#2457d6"    # тест / фейк — синє
COREFILL = "#eefaf1"


def tick(x, y, L=15, color=INK, sw=2.4):
    """Вертикальна позначка-«тик» на доріжці часу, центрована по y."""
    return line(x, y - L / 2, x, y + L / 2, color=color, sw=sw)


# ── Фігура 1: один годинник (звари) проти двох годинників (порт) ──────────────
def fig_two_clocks():
    W, H = 920, 540
    frags = []

    def panel(y0, title, tcolor, rules_ticks, infra_ticks, guides,
              port, verdict, vcolor):
        f = []
        # заголовок панелі
        f.append(text(475, y0 + 4, title, size=16, bold=True, color=tcolor))
        ry = y0 + 55   # доріжка «правила»
        iy = y0 + 135  # доріжка «інфраструктура»
        lane_x0, lane_x1 = 150, 720
        # мітки доріжок
        f.append(fitbox(30, ry - 22, 100, 44, "правила", size=13,
                        fill=COREFILL, stroke=RULES, sw=2, color=INK))
        f.append(fitbox(30, iy - 22, 100, 44, "інфра", size=13,
                        fill="#fdecea", stroke=INFRA, sw=2, color=INK))
        # лінії доріжок
        f.append(line(lane_x0, ry, lane_x1, ry, color=MUTED, sw=1.4))
        f.append(line(lane_x0, iy, lane_x1, iy, color=MUTED, sw=1.4))
        # пунктирні вертикальні гіди (де тики збігаються — рухаються разом)
        for gx in guides:
            f.append(line(gx, ry, gx, iy, color="#c7ccd2", sw=1.2, dash="4 5"))
        # тики
        for tx in rules_ticks:
            f.append(tick(tx, ry, color=RULES))
        for tx in infra_ticks:
            f.append(tick(tx, iy, color=INFRA))
        # порт-кільце між доріжками (лише в панелі «два годинники»)
        if port:
            px = 138
            f.append(circle(px, (ry + iy) / 2, 15, fill="#ffffff", stroke=RULES, sw=3))
            f.append(text(px, iy + 42, "порт", size=12, italic=True, color=RULES))
        # вердикт праворуч
        f.append(fitbox(752, y0 + 44, 150, 92, verdict, size=13,
                        fill="#f7f9fb", stroke=vcolor, sw=2.2, color=INK))
        return f

    # верхня панель — один годинник (тики збігаються)
    frags += panel(
        70, "Один годинник", INK,
        rules_ticks=[270, 470, 660], infra_ticks=[270, 470, 660],
        guides=[270, 470, 660], port=False,
        verdict="Міняються\nразом →\nзвари,\nпорт зайвий", vcolor=MUTED)

    # роздільник
    frags.append(line(30, 300, 890, 300, color="#d7dbe0", sw=1.4, dash="7 7"))

    # нижня панель — два годинники (правила рідко, інфра часто, не збігаються)
    frags += panel(
        330, "Два годинники", INK,
        rules_ticks=[320, 620],
        infra_ticks=[210, 275, 340, 405, 470, 535, 600, 665],
        guides=[], port=True,
        verdict="Різні ритми →\nпорт\nокупається", vcolor=RULES)

    render(os.path.join(OUT, "two-clocks.svg"), W, H, *frags)


# ── Фігура 2: три чесні питання про шов ───────────────────────────────────────
def fig_decision():
    W, H = 780, 560
    frags = []
    cx = 390

    # шов угорі
    sbody, sw_, sh_ = textbox(cx, 58, "Шов: ядро  ↔  конкретна деталь",
                              size=15, bold=True, pad=14, min_w=360,
                              fill="#eef1f5", stroke=LINE, sw=2)
    frags.append(sbody)

    qs = [
        (168, "1.  Є справжня друга реалізація порту?"),
        (262, "2.  Є що тестувати в ядрі без інфраструктури?"),
        (356, "3.  Правила й деталь міняються з різних причин?"),
    ]
    qw, qh = 470, 62
    prev_bottom = 58 + sh_ / 2
    for (qy, label) in qs:
        frags.append(arrow(cx, prev_bottom, cx, qy - qh / 2 - 2, sw=2))
        frags.append(fitbox(cx - qw / 2, qy - qh / 2, qw, qh, label, size=14,
                            fill="#f7f9fb", stroke=LINE, sw=1.8, color=INK))
        prev_bottom = qy + qh / 2

    # два виходи внизу
    oy = 486
    left_cx, right_cx = 200, 580
    frags.append(fitbox(left_cx - 130, oy - 34, 260, 68,
                        "Порт окупається", size=15,
                        fill=COREFILL, stroke=RULES, sw=2.6, color=INK, bold=True))
    frags.append(fitbox(right_cx - 130, oy - 34, 260, 68,
                        "Звари прямо /\nлегша форма", size=14,
                        fill="#fdecea", stroke=INFRA, sw=2.6, color=INK, bold=True))

    # стрілки-розгалуження
    frags.append(arrow(cx - 30, 356 + qh / 2 + 4, left_cx + 40, oy - 34 - 4, color=RULES, sw=2.2))
    frags.append(arrow(cx + 30, 356 + qh / 2 + 4, right_cx - 40, oy - 34 - 4, color=INFRA, sw=2.2))
    # мітки гілок — осторонь ліній
    frags.append(text(150, 432, "усі / майже всі  ТАК", size=12, italic=True, color=RULES))
    frags.append(text(628, 432, "усі  НІ", size=12, italic=True, color=INFRA))

    render(os.path.join(OUT, "decision.svg"), W, H, *frags)


# ── Фігура 3: частковий гексагон — асиметрія DH ───────────────────────────────
def fig_dh_asymmetry():
    W, H = 940, 470
    frags = []

    # заголовки боків
    frags.append(text(150, 44, "Драйвери (поки прямо)", size=14, bold=True, color=MUTED))
    frags.append(text(772, 44, "Драйвований пристрій — порт!", size=14, bold=True, color=RULES))

    # ядро по центру
    core_cx, core_cy = 470, 230
    cbody, cw, ch = textbox(core_cx, core_cy, ["Ядро DH", "(коли гріти)"],
                            size=16, bold=True, pad=20, min_w=190,
                            fill=COREFILL, stroke=RULES, sw=3)
    frags.append(cbody)

    # ── лівий бік: HTTP/CLI прямо, БЕЗ порту (пунктир, приглушено) ──
    lx, ly, lw, lh = 40, core_cy - 34, 190, 68
    frags.append(fitbox(lx, ly, lw, lh, "HTTP / CLI\n(один клієнт)", size=14,
                        fill="#f2f3f5", stroke=MUTED, sw=1.8, color=INK))
    frags.append(line(lx + lw, core_cy, core_cx - cw / 2 - 2, core_cy,
                      color=MUTED, sw=2, dash="6 6"))
    frags.append(text((lx + lw + core_cx - cw / 2) / 2, core_cy - 14,
                      "прямо, без порту", size=12, italic=True, color=MUTED))

    # ── правий бік: порт пристрою (зелене кільце) + два адаптери ──
    port_x = core_cx + cw / 2
    frags.append(circle(port_x, core_cy, 14, fill="#ffffff", stroke=RULES, sw=3))
    frags.append(text(port_x, 176, "порт пристрою", size=12,
                      italic=True, color=RULES))

    adapters = [
        (150, "Справжній давач\n+ розетка", INFRA, "#fdecea", "прод"),
        (310, "Підробний пристрій", TEST, "#eaf0fd", "тест — без заліза"),
    ]
    for (ay, label, stroke, fill, tag) in adapters:
        ax, aw, ah = 700, 200, 66
        frags.append(fitbox(ax, ay - ah / 2, aw, ah, label, size=14,
                            fill=fill, stroke=stroke, sw=2, color=INK))
        frags.append(arrow(port_x + 14, core_cy, ax, ay, color=stroke, sw=2.2))
        frags.append(text(ax + aw / 2, ay + ah / 2 + 16, tag, size=11,
                          italic=True, color=MUTED))

    # підсумковий рядок
    frags.append(text(W / 2, 448,
                      "Порт заслуговує шов пристрою (два годинники + тест без заліза); драйверний бік — прямо, поки не заслужить свій",
                      size=13, color=INK))

    render(os.path.join(OUT, "dh-asymmetry.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_two_clocks()
    fig_decision()
    fig_dh_asymmetry()
    print("figures written")
