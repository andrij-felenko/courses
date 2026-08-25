# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: три сорти когнітивного навантаження ───────────────────────────
def fig_cognitive_load():
    W, H = 900, 470
    frags = []
    frags.append(text(W / 2, 46, "Голова команди — обмежений посуд",
                      size=16, bold=True, anchor="middle"))

    # посуд-межа: широкий прямокутник, у ньому три «шари»
    bx, by, bw, bh = 250, 110, 400, 300
    frags.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=INK, sw=2.5, rx=10))
    frags.append(text(bx + bw / 2, by - 12, "межа того, що вміщає голова",
                      size=11, color=MUTED, anchor="middle"))

    # внутрішнє — велике, суть, лишається
    frags.append(rect(bx + 20, by + 190, bw - 40, 90, fill="#eef4ff",
                      stroke=NEG, sw=1.8, rx=7))
    frags.append(text(bx + bw / 2, by + 220, "Внутрішнє — суть домену",
                      size=13, bold=True, color=INK, anchor="middle"))
    frags.append(text(bx + bw / 2, by + 244, "як влаштоване страхування, податок",
                      size=11, color=MUTED, anchor="middle"))
    frags.append(text(bx + bw / 2, by + 266, "не викинеш — лише вмісти в межу",
                      size=11, color=NEG, anchor="middle"))

    # доречне — над ним, корисне зусилля
    frags.append(rect(bx + 20, by + 96, bw - 40, 80, fill="#eafaf1",
                      stroke=FIELD, sw=1.8, rx=7))
    frags.append(text(bx + bw / 2, by + 124, "Доречне — осмислення продукту",
                      size=13, bold=True, color=INK, anchor="middle"))
    frags.append(text(bx + bw / 2, by + 148, "як краще спроєктувати саме цю фічу",
                      size=11, color=MUTED, anchor="middle"))
    frags.append(text(bx + bw / 2, by + 168, "заради нього й тримають команду",
                      size=11, color=FIELD, anchor="middle"))

    # побічне — тонка смужка згори, яку зрізають
    frags.append(rect(bx + 20, by + 20, bw - 40, 60, fill="#fdecea",
                      stroke=POS, sw=1.8, rx=7))
    frags.append(text(bx + bw / 2, by + 44, "Побічне — тертя інструментів",
                      size=13, bold=True, color=INK, anchor="middle"))
    frags.append(text(bx + bw / 2, by + 66, "складання, розгортання, ключі — податок",
                      size=11, color=MUTED, anchor="middle"))

    # стрілка «зрізати» від побічного назовні праворуч
    frags.append(arrow(bx + bw - 8, by + 50, bx + bw + 130, by + 50, color=POS, sw=2.4))
    frags.append(text(bx + bw + 138, by + 44, "зрізати",
                      size=12, bold=True, color=POS, anchor="start"))
    frags.append(text(bx + bw + 138, by + 62, "до нуля",
                      size=12, bold=True, color=POS, anchor="start"))

    # підказка ліворуч: звільнене місце
    frags.append(arrow(bx - 8, by + 136, bx - 120, by + 136, color=FIELD, sw=2.4))
    frags.append(text(bx - 128, by + 130, "звільнене",
                      size=12, bold=True, color=FIELD, anchor="end"))
    frags.append(text(bx - 128, by + 148, "місце",
                      size=12, bold=True, color=FIELD, anchor="end"))

    render(os.path.join(IMG, 'cognitive-load.svg'), W, H, *frags,
           title="Три сорти когнітивного навантаження команди")


# ── Фігура 2: чотири типи команд навколо потокової ──────────────────────────
def fig_four_teams():
    W, H = 900, 560
    frags = []
    frags.append(text(W / 2, 44, "Потокова команда — центр, решта на неї працює",
                      size=16, bold=True, anchor="middle"))

    # центр — потокова
    cx, cy = W / 2, 300
    sa, saw, sah = textbox(cx, cy, "Потокова команда\n(несе потік цінності\nвід задуму до проду)",
                           size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=2.4, pad=16)

    # платформна — знизу
    pf, pfw, pfh = textbox(cx, cy + 200, "Платформна\nвнутрішній продукт-сервіс\nзнімає побічне тертя",
                           size=12.5, bold=True, fill="#eef4ff", stroke=NEG, sw=2, pad=12)
    frags.append(arrow(cx, cy + 200 - pfh / 2, cx, cy + sah / 2 + 6, color=NEG, sw=2))
    frags.append(text(cx + 14, (cy + sah / 2 + cy + 200 - pfh / 2) / 2,
                      "як-сервіс", size=11, color=MUTED, anchor="start"))

    # уможливлювальна — праворуч
    en, enw, enh = textbox(cx + 265, cy, "Уможливлювальна\nтимчасово навчає\nвміння й виходить",
                           size=12.5, bold=True, fill="#fbfbfb", stroke=POS, sw=2, pad=12)
    frags.append(arrow(cx + 265 - enw / 2, cy, cx + saw / 2 + 6, cy, color=POS, sw=2, ))
    frags.append(text((cx + saw / 2 + cx + 265 - enw / 2) / 2, cy - 12,
                      "наставництво", size=11, color=MUTED, anchor="middle"))

    # складна підсистема — ліворуч
    cs, csw, csh = textbox(cx - 265, cy, "Складна підсистема\nізолює рідкісну\nскладність за API",
                           size=12.5, bold=True, fill="#fbfbfb", stroke=MUTED, sw=2, pad=12)
    frags.append(arrow(cx - 265 + csw / 2, cy, cx - saw / 2 - 6, cy, color=MUTED, sw=2))
    frags.append(text((cx - saw / 2 + cx - 265 + csw / 2) / 2, cy - 12,
                      "як-сервіс", size=11, color=MUTED, anchor="middle"))

    # центр малюємо останнім — поверх стрілок
    frags.append(sa)
    frags.append(pf)
    frags.append(en)
    frags.append(cs)

    render(os.path.join(IMG, 'four-teams.svg'), W, H, *frags,
           title="Чотири типи команд")


# ── Фігура 3: три режими взаємодії на осі тертя ─────────────────────────────
def fig_interaction_modes():
    W, H = 900, 420
    frags = []
    frags.append(text(W / 2, 44, "Три режими взаємодії двох команд",
                      size=16, bold=True, anchor="middle"))

    # вісь тертя знизу
    ay = 360
    frags.append(line(70, ay, W - 70, ay, color=INK, sw=2))
    frags.append(text(80, ay + 32, "низьке тертя, автономія",
                      size=11, color=MUTED, anchor="start"))
    frags.append(text(W - 80, ay + 32, "високе тертя, дороге",
                      size=11, color=MUTED, anchor="end"))

    # три колонки-картки
    cols = [
        (200, "Як-сервіс", FIELD, "#eafaf1",
         ["одна надає,", "друга споживає", "через інтерфейс", "— без розмов", "СТАЛИЙ режим"]),
        (470, "Наставництво", NEG, "#eef4ff",
         ["одна навчає", "іншу подолати", "перешкоду", "— передав уміння", "і ВИЙШОВ"]),
        (740, "Співпраця", POS, "#fdecea",
         ["щільно разом,", "щоб намацати", "нове (інтерфейс)", "— дорого", "ТИМЧАСОВО"]),
    ]
    top = 96
    cardw, cardh = 210, 200
    for x, name, col, fillc, lines in cols:
        frags.append(rect(x - cardw / 2, top, cardw, cardh, fill=fillc,
                          stroke=col, sw=2.2, rx=9))
        frags.append(text(x, top + 30, name, size=15, bold=True, color=INK, anchor="middle"))
        yy = top + 66
        for ln in lines:
            bold = ln.isupper() or ln.startswith("СТАЛИЙ") or ln.startswith("і ВИЙШОВ") or ln.startswith("ТИМЧАСОВО")
            frags.append(text(x, yy, ln, size=12,
                              color=col if ("СТАЛИЙ" in ln or "ВИЙШОВ" in ln or "ТИМЧАСОВО" in ln) else INK,
                              bold=("СТАЛИЙ" in ln or "ВИЙШОВ" in ln or "ТИМЧАСОВО" in ln),
                              anchor="middle"))
            yy += 24
        # тонка ніжка від картки до осі
        frags.append(line(x, top + cardh, x, ay - 7, color=col, sw=1.3, dash="3,3"))
        frags.append(circle(x, ay, 6, fill=BG, stroke=col, sw=2.4))

    render(os.path.join(IMG, 'interaction-modes.svg'), W, H, *frags,
           title="Три режими взаємодії команд")


if __name__ == "__main__":
    fig_cognitive_load()
    fig_four_teams()
    fig_interaction_modes()
    print("figures written to", IMG)
