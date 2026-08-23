# -*- coding: utf-8 -*-
"""Фігури для кроку «Проєктування письмом як інструмент мислення»
(root/course/progarch, views-and-communication). Три ідеї:
 1) голова проти сторінки — чому externalization ловить суперечності;
 2) один записаний абзац виявляє чотири приховані рішення (DH офлайн);
 3) писати, ЩОБ вирішити, проти писати ПІСЛЯ (звіт).
Запуск: python figs.py  → пише у ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, 'img')
os.makedirs(OUT, exist_ok=True)

ACCENT = "#2457d6"   # холодний акцент
WARM   = "#c0392b"   # гаряче / небезпека
SPOT   = "#fff7e6"   # заливка «прожектора уваги»


# ── 1. Голова проти сторінки ─────────────────────────────────────────────────
def fig_head_vs_page():
    W, H = 1000, 480
    frags = []
    # — ЛІВА панель: у голові —
    frags.append(text(255, 66, "У голові", size=16, bold=True, color=MUTED))
    frags.append(rect(55, 84, 400, 366, fill=BG, stroke=MUTED, sw=1.6, rx=18))
    frags.append(text(255, 116, "робоча пам'ять тримає лиш кілька частин заразом",
                      size=11, color=MUTED))
    # прожектор уваги (2 частини у фокусі — різкі)
    frags.append(circle(165, 268, 96, fill=SPOT, stroke=MUTED, sw=1.4))
    # svgkit circle не має dash — домалюємо пунктирне кільце окремо
    frags[-1] = ('<circle cx="165" cy="268" r="96" fill="%s" stroke="%s" '
                 'stroke-width="1.4" stroke-dasharray="5 5"/>' % (SPOT, MUTED))
    frags.append(text(165, 190, "у фокусі зараз", size=11, color=WARM))
    frags.append(fitbox(103, 214, 124, 30, "офлайн-режим", size=12, stroke=ACCENT, sw=1.6))
    frags.append(fitbox(103, 292, 124, 30, "буфер даних", size=12, stroke=ACCENT, sw=1.6))
    # решта частин — поза фокусом (бліді, «не в думці»)
    for cy, s in ((150, "погодні правила"), (225, "керування ззовні"), (300, "повтор команд")):
        frags.append(fitbox(300, cy, 148, 30, s, size=11, fill="#fbfbfc",
                            stroke="#c9ced6", color=MUTED))
    frags.append(text(374, 356, "поза фокусом — наче й немає", size=10, color="#aab0ba"))

    # — ПРАВА панель: на сторінці —
    frags.append(text(745, 66, "На сторінці", size=16, bold=True, color=INK))
    frags.append(rect(545, 84, 400, 366, fill="#ffffff", stroke=LINE, sw=1.6, rx=6))
    lines = [
        (140, "п. 3 — хаб працює без хмари"),
        (185, "п. 12 — телефон керує з дому"),
        (230, "п. 27 — буфер на добу"),
        (275, "п. 40 — правило жалюзі чекає хмару"),
        (320, "п. 55 — після збою — повтор черги"),
    ]
    for y, s in lines:
        frags.append(text(575, y, s, size=13, color=INK, anchor="start"))
    # червоний зв'язок між п.3 і п.40 — суперечність, яку видно РАЗОМ
    frags.append(line(892, 136, 892, 271, color=WARM, sw=2.2))
    frags.append(line(878, 136, 892, 136, color=WARM, sw=2.2))
    frags.append(line(878, 271, 892, 271, color=WARM, sw=2.2))
    frags.append(text(745, 404, "п. 3 і п. 40 суперечать — разом це видно",
                      size=13, color=WARM, bold=True))
    render(os.path.join(OUT, "head-vs-page.svg"), W, H, *frags,
           title="Чому сторінка бачить те, чого не бачить голова")


# ── 2. Один абзац виявляє чотири рішення (DH офлайн) ──────────────────────────
def fig_cascade():
    W, H = 980, 590
    frags = []
    top, tw, th = textbox(490, 92, "«Хаб працює офлайн» — здається, вже вирішено",
                          size=15, bold=True, fill="#eef2ff", stroke=ACCENT, sw=2, pad=14)
    frags.append(top)
    frags.append(arrow(490, 92 + th / 2, 490, 168, color=WARM, sw=2))
    frags.append(text(700, 150, "спробуй ЗАПИСАТИ це реченням", size=12, color=WARM))
    # спина + чотири гілки-рішення
    spine_x = 250
    frags.append(line(spine_x, 196, spine_x, 548, color=MUTED, sw=1.6))
    boxes = [
        (230, "Погодні правила тихо вимикаються (їм треба хмара)\n— ми на це свідомо згодні?"),
        (320, "Керування з-поза дому вмирає на весь час збою\n— це прийнятно?"),
        (410, "Буфер телеметрії: на скільки годин розрахований\nі що робити, коли переповниться?"),
        (500, "Після відновлення — повторювати чергу команд?\nА якщо «відчини двері» вже застаріла?"),
    ]
    for cy, s in boxes:
        frags.append(line(spine_x, cy, 300, cy, color=MUTED, sw=1.6))
        frags.append(fitbox(300, cy - 34, 620, 68, s, size=13, fill=FILL, stroke=WARM, sw=1.6))
        frags.append(circle(spine_x, cy, 12, fill="#fdecea", stroke=WARM, sw=2))
        frags.append(text(spine_x, cy + 5, "?", size=16, color=WARM, bold=True))
    render(os.path.join(OUT, "cascade.svg"), W, H, *frags,
           title="Один записаний абзац виявляє чотири приховані рішення")


# ── 3. Писати, ЩОБ вирішити, проти писати ПІСЛЯ ───────────────────────────────
def fig_decide_vs_report():
    W, H = 1080, 470
    frags = []

    def chain(cx_list, labels, y, colors):
        # намалювати ланцюг рамок зі стрілками; повертає (лівий_край, правий_край) кожної
        edges = []
        for cx, s, col in zip(cx_list, labels, colors):
            b, w, h = textbox(cx, y, s, size=13, bold=(col != INK),
                              fill=("#fdecea" if col == WARM else "#f2fbf5" if col == FIELD else FILL),
                              stroke=col, sw=(2 if col != INK else 1.5), pad=11)
            frags.append(b)
            edges.append((cx - w / 2, cx + w / 2))
        for i in range(len(cx_list) - 1):
            frags.append(arrow(edges[i][1] + 4, y, edges[i + 1][0] - 4, y, sw=1.7))
        return edges

    # Лане A — писати ПІСЛЯ (звіт)
    frags.append(text(48, 96, "Писати ПІСЛЯ — документ як звіт", size=15, bold=True,
                      color=WARM, anchor="start"))
    chain([185, 400, 645, 900],
          ["вирішую в голові", "будую", "дірки — у проді", "пишу док (архів)"],
          150, [INK, INK, WARM, INK])

    frags.append(line(40, 232, 1040, 232, color="#d9dce2", sw=1.2, dash="6 6"))

    # Лане B — писати, ЩОБ вирішити (інструмент)
    frags.append(text(48, 300, "Писати, ЩОБ вирішити — документ як інструмент",
                      size=15, bold=True, color=FIELD, anchor="start"))
    chain([175, 470, 730, 905],
          ["пишу чернетку", "дірки — на папері", "вирішую", "будую"],
          354, [INK, FIELD, INK, INK])

    render(os.path.join(OUT, "decide-vs-report.svg"), W, H, *frags,
           title="Той самий документ, посунутий раніше, ловить дірки на папері")


# ── 4. Родовід ідеї (вставка hist-narrative-over-slides) ──────────────────────
def fig_lineage():
    """Три станції одного здогаду: Дідіон (література) → Гіндон/Лемпорт
    (формальні методи) → Amazon (управління). Рівномірно рознесені (не в масштабі
    часу — це родовід, не хронологія); підписи з запасом, щоб svgcheck дав «0»."""
    W, H = 1040, 400
    frags = []
    frags.append(text(W / 2, 48, "родовід ідеї «письмо — це мислення»",
                      size=12, color=MUTED))
    # вісь часу зліва направо
    frags.append(arrow(96, 290, 944, 290, color=MUTED, sw=2.0))
    nodes = [
        (248, "#7a3fb3", "#f3ecfb", "ЛІТЕРАТУРА", "Джоан Дідіон",
         "есе «Why I Write»", "1976",
         ("«пишу — щоб дізнатися,", "що я думаю»")),
        (520, "#2457d6", "#eaf0fd", "ФОРМАЛЬНІ МЕТОДИ", "Гіндон → Лемпорт",
         "«Specifying Systems»", "2002",
         ("«письмо виказує,", "яка неохайна думка»")),
        (792, "#1f7a4d", "#e8f5ee", "УПРАВЛІННЯ", "Джефф Безос · Amazon",
         "заборона слайдів", "2004",
         ("наратив не дає", "сховати діру за булітами")),
    ]
    for x, col, fill, dom, name, work, year, ins in nodes:
        frags.append(rect(x - 125, 64, 250, 118, fill=fill, stroke=col, sw=1.8, rx=10))
        frags.append(text(x, 94, dom, size=11, bold=True, color=col))
        frags.append(text(x, 126, name, size=15, bold=True, color=INK))
        frags.append(text(x, 156, work, size=12, color=MUTED, italic=True))
        frags.append(line(x, 182, x, 281, color=MUTED, sw=1.4))      # до вузла на осі
        frags.append(circle(x, 290, 9, fill=BG, stroke=col, sw=2.4))
        frags.append(text(x, 316, year, size=13, bold=True, color=col))
        frags.append(text(x, 344, ins[0], size=12, italic=True, color=col))
        frags.append(text(x, 364, ins[1], size=12, italic=True, color=col))
    render(os.path.join(OUT, "lineage.svg"), W, H, *frags,
           title="Той самий здогад мандрує трьома світами")


if __name__ == "__main__":
    fig_head_vs_page()
    fig_cascade()
    fig_decide_vs_report()
    fig_lineage()
    print("OK: 4 фігури у", OUT)
