# -*- coding: utf-8 -*-
"""Фігури для теми «Питання P проти NP» (book/algorithms/complexity-computability/p-vs-np)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
BLUE_F, BLUE_S = "#eaf0fd", "#2b6cb0"
GREEN_F, GREEN_S = "#e9f7ef", "#276749"
RED_F, RED_S = "#fdecea", "#c53030"
PURPLE_F, PURPLE_S = "#f3e8ff", "#6b46c1"


def fig_scenarios():
    """Дві картини світу: P ≠ NP проти P = NP."""
    W, H = 1040, 520
    frags = []

    frags.append(text(W / 2, 35, "Дві фундаментальні картини структури складнісних класів",
                      size=18, color=INK, bold=True))

    # Ліва панель: Сценарій P != NP
    x1, y1, w1, h1 = 50, 70, 440, 410
    frags.append(rect(x1, y1, w1, h1, rx=12, fill="#f8fafc", stroke="#cbd5e1", sw=1.5))
    frags.append(text(x1 + w1/2, y1 + 30, "Сценарій 1: P ≠ NP (Загальноприйнятий)",
                      size=16, color=BLUE_S, bold=True))

    # EXPTIME
    frags.append(rect(x1 + 20, y1 + 55, w1 - 40, 335, rx=10, fill="#f1f5f9", stroke="#94a3b8", sw=1.5))
    frags.append(text(x1 + 35, y1 + 75, "EXPTIME", size=13, color=MUTED, bold=True))

    # PSPACE
    frags.append(rect(x1 + 35, y1 + 90, w1 - 70, 285, rx=8, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5))
    frags.append(text(x1 + 50, y1 + 110, "PSPACE", size=13, color=PURPLE_S, bold=True))

    # NP
    frags.append(rect(x1 + 50, y1 + 125, w1 - 100, 235, rx=8, fill=RED_F, stroke=RED_S, sw=1.5))
    frags.append(text(x1 + 65, y1 + 145, "NP", size=14, color=RED_S, bold=True))

    # NP-Complete
    box_npc, _, _ = textbox(x1 + w1/2, y1 + 195, "NP-повні задачі\n(SAT, 3-SAT, TSP)\nНайважчі в NP",
                            size=13, bold=True, fill="#fee2e2", stroke=RED_S, sw=1.8, pad=10)
    frags.append(box_npc)

    # NP-Intermediate
    frags.append(text(x1 + 110, y1 + 255, "NP-проміжні (NPI)", size=12, color="#991b1b", italic=True))

    # P
    box_p, _, _ = textbox(x1 + w1/2, y1 + 310, "Клас P\n(Сортування, Дейкстра, GCD)\nПоліноміально розв'язні",
                          size=13, bold=True, fill=GREEN_F, stroke=GREEN_S, sw=2, pad=10)
    frags.append(box_p)

    # Права панель: Сценарій P = NP
    x2, y2, w2, h2 = 550, 70, 440, 410
    frags.append(rect(x2, y2, w2, h2, rx=12, fill="#f8fafc", stroke="#cbd5e1", sw=1.5))
    frags.append(text(x2 + w2/2, y2 + 30, "Сценарій 2: P = NP (Гіпотетичний колапс)",
                      size=16, color=RED_S, bold=True))

    # EXPTIME
    frags.append(rect(x2 + 20, y2 + 55, w2 - 40, 335, rx=10, fill="#f1f5f9", stroke="#94a3b8", sw=1.5))
    frags.append(text(x2 + 35, y2 + 75, "EXPTIME", size=13, color=MUTED, bold=True))

    # PSPACE
    frags.append(rect(x2 + 35, y2 + 90, w2 - 70, 285, rx=8, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5))
    frags.append(text(x2 + 50, y2 + 110, "PSPACE", size=13, color=PURPLE_S, bold=True))

    # Злитий P = NP
    box_pnp, _, _ = textbox(x2 + w2/2, y2 + 235,
                            "Злиття класів: P = NP = NP-Complete\n\n"
                            "• Будь-яка перевірка є пошуком\n"
                            "• Злам асиметричної криптографії\n"
                            "• Автоматичне доведення теорем",
                            size=13, bold=True, fill=GREEN_F, stroke=GREEN_S, sw=2.5, pad=15)
    frags.append(box_pnp)

    render(os.path.join(IMG, "p-vs-np-scenarios.svg"), W, H, *frags,
           title="Дві картини світу: P ≠ NP проти P = NP")


def fig_barriers():
    """Три бар'єри доведення P проти NP."""
    W, H = 1060, 440
    frags = []

    frags.append(text(W / 2, 35, "Три теоретичні бар'єри на шляху до доведення P ≠ NP",
                      size=18, color=INK, bold=True))

    cols = [
        ("1. Релятивізація", "Baker, Gill, Solovay (1975)",
         "Існують оракули A та B:\nP^A = NP^A,  P^B ≠ NP^B\n\nВідсікає:\nДіагоналізацію та\nсимуляцію машин Тюринга",
         BLUE_F, BLUE_S, 50),
        ("2. Натуральні доведення", "Razborov, Rudich (1997)",
         "Конструктивність + Великість\nвластивостей схем ламає PRG\n\nВідсікає:\nНижні оцінки складності\nбулевих схем (Circuit Complexity)",
         AMBER_F, AMBER_S, 380),
        ("3. Алгебраїзація", "Aaronson, Wigderson (2008)",
         "Алгебраїчні оракули не\nрозділяють P і NP\n\nВідсікає:\nМетоди арифметизації та\nінтерактивних доказів (IP=PSPACE)",
         PURPLE_F, PURPLE_S, 710)
    ]

    for title_txt, author_txt, body_txt, fcol, scol, xpos in cols:
        w_box = 300
        frags.append(rect(xpos, 70, w_box, 270, rx=10, fill=fcol, stroke=scol, sw=2))
        frags.append(text(xpos + w_box/2, 98, title_txt, size=15, color=scol, bold=True))
        frags.append(text(xpos + w_box/2, 120, author_txt, size=12, color=MUTED, italic=True))
        frags.append(line(xpos + 15, 133, xpos + w_box - 15, 133, color=scol, sw=1))

        b_box, _, _ = textbox(xpos + w_box/2, 230, body_txt, size=13, bold=False, fill="#ffffff", stroke="#e2e8f0", sw=1, pad=10)
        frags.append(b_box)

    bridge, _, _ = textbox(W / 2, 390,
                           "Вузька стежка вперед: Не-релятивізовані, не-натуральні, не-алгебраїзовані техніки\n"
                           "(наприклад, Геометрична теорія складності GCT / Алгебраїчна геометрія)",
                           size=13, bold=True, fill=GREEN_F, stroke=GREEN_S, sw=2, pad=12)
    frags.append(bridge)

    render(os.path.join(IMG, "proof-barriers.svg"), W, H, *frags,
           title="Три бар'єри доведення P проти NP")


def fig_phase_transition():
    """Фазовий перехід у 3-SAT: складність та виконуваність від відношення α = m/n."""
    W, H = 1040, 520
    frags = []

    frags.append(text(W / 2, 35, "Фазовий перехід у 3-SAT: Виконуваність та сплеск складності",
                      size=18, color=INK, bold=True))

    ox, oy, gw, gh = 130, 420, 780, 310
    frags.append(rect(ox, oy - gh, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.5))

    # Вісь X: alpha = m/n
    frags.append(line(ox, oy, ox + gw, oy, color=INK, sw=2))
    frags.append(text(ox + gw/2, oy + 45, "Відношення диз'юнктів до змінних α = m/n", size=14, bold=True))

    for a in range(1, 9):
        x_val = ox + (a - 1) * (gw / 7)
        frags.append(line(x_val, oy, x_val, oy + 6, color=INK, sw=1.5))
        frags.append(text(x_val, oy + 22, str(a), size=13))

    # Вісь Y ліворуч: Ймовірність виконуваності P(SAT) [0 .. 1.0]
    frags.append(line(ox, oy, ox, oy - gh, color=BLUE_S, sw=2))
    frags.append(text(ox - 70, oy - gh/2, "P(SAT)", size=14, color=BLUE_S, bold=True))
    for p in [0.0, 0.5, 1.0]:
        y_val = oy - p * (gh - 30)
        frags.append(line(ox - 6, y_val, ox, y_val, color=BLUE_S, sw=1.5))
        frags.append(text(ox - 25, y_val + 4, f"{p:.1f}", size=12, color=BLUE_S))

    # Крива ймовірності P(SAT) (синя)
    pts_p = []
    for step in range(101):
        t = step / 100.0
        a = 1.0 + t * 7.0
        prob = 1.0 / (1.0 + math.exp(6.0 * (a - 4.267)))
        x_val = ox + (a - 1) * (gw / 7)
        y_val = oy - prob * (gh - 30)
        pts_p.append((x_val, y_val))

    for i in range(len(pts_p) - 1):
        frags.append(line(pts_p[i][0], pts_p[i][1], pts_p[i+1][0], pts_p[i+1][1], color=BLUE_S, sw=3))

    # Крива часу/кроків (червона)
    pts_t = []
    for step in range(101):
        t = step / 100.0
        a = 1.0 + t * 7.0
        time_norm = math.exp(-((a - 4.267) ** 2) / 0.35)
        x_val = ox + (a - 1) * (gw / 7)
        y_val = oy - (0.05 + time_norm * 0.85) * (gh - 30)
        pts_t.append((x_val, y_val))

    for i in range(len(pts_t) - 1):
        frags.append(line(pts_t[i][0], pts_t[i][1], pts_t[i+1][0], pts_t[i+1][1], color=RED_S, sw=3, dash="6,3"))

    # Критична точка α_c ≈ 4.267
    xc = ox + (4.267 - 1) * (gw / 7)
    box_crit_y = oy - gh + 50
    box_crit, _, h_cb = textbox(xc, box_crit_y, "Критична точка α_c ≈ 4.267\nФазовий перехід & Експоненційний пік складності",
                                size=12, bold=True, fill=RED_F, stroke=RED_S, sw=1.8, pad=8)

    # Пунктир від нижньої межі бокса до осі X (не перетинає сам бокс)
    frags.append(line(xc, box_crit_y + h_cb/2 + 2, xc, oy, color=RED_S, sw=1.5, dash="4,4"))
    frags.append(box_crit)

    # Зони
    frags.append(text(ox + 120, oy - 40, "Легка зона (SAT)\nБагато рішень", size=13, color=BLUE_S, bold=True))
    frags.append(text(ox + gw - 130, oy - 40, "Легка зона (UNSAT)\nШвидке виявлення суперечності", size=13, color=MUTED, bold=True))

    render(os.path.join(IMG, "phase-transition-3sat.svg"), W, H, *frags,
           title="Фазовий перехід у 3-SAT: виконуваність та складність")


if __name__ == "__main__":
    fig_scenarios()
    fig_barriers()
    fig_phase_transition()
    print("Всі фігури успішно згенеровано!")
