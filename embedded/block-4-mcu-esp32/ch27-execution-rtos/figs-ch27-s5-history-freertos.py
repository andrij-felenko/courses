# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до теми 4.10.5 — FreeRTOS.
Чистий Python, без сторонніх залежностей. Вивід → ./img/.
Нумерація фігур: Рис. 4.10.5i.k (i-форма, тому що це історія до теми).
Файли: fig-27-5i-1.svg, fig-27-5i-2.svg.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ── Рис. 4.10.5i.1 — Бізнес-модель: одне ядро, три обличчя ──────────────────

def fig_business_model():
    """
    Рис. 4.10.5i.1. Одне ядро — три ліцензійні «обличчя».
    Горизонтальне дерево: спільне ядро зліва, три колонки-гілки праворуч.
    Три стовпці: FreeRTOS ($0), OpenRTOS (платна), SafeRTOS (сертифікована).
    """
    W, H = 940, 440
    elems = []

    # ── Заголовок ──
    t1, _, _ = textbox(W // 2, 32, "Одне ядро — три обличчя", size=17, bold=True,
                        fill=BG, stroke=BG)
    elems.append(t1)
    elems.append(text(W // 2, 56,
                      "один і той самий код — у різних юридичних упаковках",
                      size=12, color=MUTED, anchor="middle"))

    # ── Спільне ядро (ліворуч, центр по вертикалі) ──
    kernel_cx, kernel_cy = 120, 240
    kernel_fill = "#e8f5e9"
    kb, kw, kh = textbox(kernel_cx, kernel_cy,
                          "Спільне\nядро\nFreeRTOS",
                          size=14, bold=True,
                          fill=kernel_fill, stroke=FIELD,
                          color=FIELD, pad=14, min_w=100)
    elems.append(kb)

    # ── Три колонки ──
    cols = [
        # (cx, назва, підназва, деталі3рядки, колір_рамки, колір_тексту, fill)
        (310, "FreeRTOS",
         "GPL з винятком · $0",
         ["Твій код лишається", "закритим; ядро — відкрите.", "Спільнота / студенти /", "дешеві вироби"],
         NEG, NEG, "#eaf0fd"),
        (560, "OpenRTOS",
         "Комерційна ліцензія · платна",
         ["Без будь-яких GPL-зобов'язань.", "Юридичні гарантії.", "Технічна підтримка", "(WITTENSTEIN hIS)"],
         POS, POS, "#fdecea"),
        (800, "SafeRTOS",
         "Функційна безпека · платна++",
         ["Сертифікована (IEC 61508,", "ISO 26262, DO-178C).", "Медицина / авіа / авто;", "ціна відмови — життя"],
         "#7a4fb0", "#7a4fb0", "#f5f0fb"),
    ]

    col_top_y = 100
    col_h = 230
    col_w = 200

    for cx, title, subtitle, details, stroke_col, text_col, fill_col in cols:
        # Рамка колонки
        elems.append(rect(cx - col_w // 2, col_top_y, col_w, col_h,
                          fill=fill_col, stroke=stroke_col, sw=2, rx=10))
        # Заголовок колонки
        tb, _, _ = textbox(cx, col_top_y + 28, title,
                            size=15, bold=True,
                            fill=fill_col, stroke=fill_col,
                            color=text_col, pad=6)
        elems.append(tb)
        # Підназва (ліцензія/ціна)
        elems.append(text(cx, col_top_y + 54, subtitle,
                          size=10, color=MUTED, anchor="middle"))
        elems.append(line(cx - col_w // 2 + 12, col_top_y + 64,
                           cx + col_w // 2 - 12, col_top_y + 64,
                           color=stroke_col, sw=1, dash="4,3"))
        # Деталі
        dy = col_top_y + 82
        for detail in details:
            elems.append(text(cx, dy, detail, size=10, color=INK, anchor="middle"))
            dy += 16

        # Стрілка від ядра до колонки
        elems.append(arrow(kernel_cx + kw // 2, kernel_cy,
                            cx - col_w // 2 - 4, col_top_y + col_h // 2,
                            color=FIELD, sw=2))

    # ── Підсумкова рамка знизу ──
    conclusion = ("Безкоштовна версія розносить ядро по чипах і слугує полігоном якості;\n"
                  "платні OpenRTOS / SafeRTOS годують проєкт там, де ціна відмови висока.")
    cb, _, _ = textbox(W // 2, 388,
                        conclusion,
                        size=12, bold=False,
                        fill="#fffde7", stroke="#cca824",
                        color=INK, pad=12, min_w=760)
    elems.append(cb)

    render(os.path.join(OUT, "fig-27-5i-1.svg"), W, H, *elems,
           title=None)
    print("wrote fig-27-5i-1.svg")


# ── Рис. 4.10.5i.2 — Стрічка часу FreeRTOS ──────────────────────────────────

def fig_timeline():
    """
    Рис. 4.10.5i.2. П'ять віх FreeRTOS від ~2003 до вашого ESP32.
    Горизонтальна стрічка; вузли чергуються вгору / вниз.
    """
    W, H = 980, 400

    elems = []

    # Заголовок
    t1, _, _ = textbox(W // 2, 28, "Шлях FreeRTOS: від роздратування інженера до ядра у вашому ESP32",
                        size=16, bold=True, fill=BG, stroke=BG, pad=6)
    elems.append(t1)
    elems.append(text(W // 2, 52,
                      "п'ять віх і остання ланка лінії CTSS→Unix",
                      size=11, color=MUTED, anchor="middle"))

    # Вісь
    axis_y = 220
    axis_x0 = 60
    axis_x1 = 920
    elems.append(line(axis_x0, axis_y, axis_x1, axis_y, color=LINE, sw=2.5))

    # Вузли: (x, рядки тексту, над_чи_під, рік_підпис, колір)
    nodes = [
        (120,  ["~2003", "Беррі публікує", "крихітне", "вільне ядро"],         "above", FIELD),
        (295,  ["GPL-виняток:", "OpenRTOS /", "SafeRTOS", "(WITTENSTEIN)"],     "below", POS),
        (480,  ["Спільнота портує", "під сотні чипів", "ARM / RISC-V /", "Xtensa"], "above", NEG),
        (670,  ["2017 Amazon:", "стюардство +", "ліцензія MIT"],                "below", "#7a4fb0"),
        (860,  ["Espressif:", "ESP-IDF (SMP)", "→ ваш loopTask"],               "above", POS),
    ]

    box_h = 80
    box_w = 148

    for cx, lines_txt, side, col in nodes:
        # Вертикальна лінія-ніжка
        if side == "above":
            line_y1 = axis_y - 14
            line_y2 = axis_y - 14 - 40
            box_cy = axis_y - 14 - 40 - box_h // 2
        else:
            line_y1 = axis_y + 14
            line_y2 = axis_y + 14 + 40
            box_cy = axis_y + 14 + 40 + box_h // 2

        elems.append(line(cx, line_y1, cx, line_y2, color=col, sw=1.8))

        # Вузол на осі
        elems.append(rect(cx - 8, axis_y - 8, 16, 16,
                          fill=col, stroke=col, sw=1, rx=3))

        # Рамка з текстом
        bx = max(axis_x0, min(cx - box_w // 2, axis_x1 - box_w))
        elems.append(fitbox(bx, box_cy - box_h // 2,
                             box_w, box_h,
                             "\n".join(lines_txt),
                             size=11, fill="#fafafa",
                             stroke=col, sw=1.8, rx=8,
                             color=INK))

    # Стрілки між вузлами (по осі)
    for i in range(len(nodes) - 1):
        x1 = nodes[i][0] + 10
        x2 = nodes[i + 1][0] - 10
        elems.append(arrow(x1, axis_y, x2, axis_y, color=LINE, sw=2))

    # Нижня виноска — зв'язок із лінією CTSS→Unix
    footnote = "← продовження лінії CTSS→Unix (1961–1969); попередня стрічка — в «Історії розділу 4.10»"
    elems.append(line(axis_x0, axis_y + 46, axis_x1 - 40, axis_y + 46,
                      color=MUTED, sw=1, dash="4,3"))
    elems.append(text(axis_x0 + 8, axis_y + 60,
                      footnote, size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "fig-27-5i-2.svg"), W, H, *elems,
           title=None)
    print("wrote fig-27-5i-2.svg")


if __name__ == "__main__":
    fig_business_model()
    fig_timeline()
    print("Done — fig-27-5i-1.svg, fig-27-5i-2.svg")
