# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_inversion():
    """Два напрямки: стихійний закон Конвея (орг → арх) і обернений маневр (арх → орг)."""
    W, H = 760, 380
    frags = []

    # ── Верхній ряд: звичайний напрям ──
    y1 = 118
    b_org, w_org, h_org = textbox(180, y1, "Структура\nорганізації", size=15, bold=True,
                                  fill="#eaf0fd", stroke=NEG, min_w=200)
    b_arch, w_arch, h_arch = textbox(580, y1, "Архітектура\nсистеми", size=15, bold=True,
                                     fill="#f4f6f8", min_w=200)
    frags += [b_org, b_arch]
    frags.append(arrow(180 + w_org / 2 + 8, y1, 580 - w_arch / 2 - 8, y1, color=NEG, sw=2.4))
    frags.append(text(380, y1 - 20, "закон Конвея (стихійно)", size=14, color=NEG, bold=True))
    frags.append(text(380, y1 + 22, "яка організація — така й система", size=12, color=MUTED))

    # роздільник
    frags.append(line(60, 200, W - 60, 200, color="#d0d4da", sw=1.2, dash="6 6"))

    # ── Нижній ряд: обернений маневр (стрілка справа наліво) ──
    y2 = 288
    b_org2, w_org2, h_org2 = textbox(180, y2, "Структура\nкоманд", size=15, bold=True,
                                     fill="#eaf0fd", stroke=NEG, min_w=200)
    b_arch2, w_arch2, h_arch2 = textbox(580, y2, "Бажана\nархітектура", size=15, bold=True,
                                        fill="#eafaf0", stroke=FIELD, min_w=200)
    frags += [b_org2, b_arch2]
    # проєктуємо команди ВІД бажаної архітектури: стрілка з правого боку в лівий
    frags.append(arrow(580 - w_arch2 / 2 - 8, y2, 180 + w_org2 / 2 + 8, y2, color=FIELD, sw=2.4))
    frags.append(text(380, y2 - 20, "обернений маневр (свідомо)", size=14, color=FIELD, bold=True))
    frags.append(text(380, y2 + 22, "будуємо команди під потрібну систему", size=12, color=MUTED))

    render(os.path.join(IMG, 'inversion.svg'), W, H, *frags,
           title="Закон Конвея та його інверсія")


def fig_team_seam():
    """Дві команди, густі внутрішні зв'язки, один тонкий контракт крізь межу."""
    W, H = 760, 420
    frags = []

    # межа між командами — розірвана навколо коробки "контракт" (щоб не різати напис)
    frags.append(line(380, 70, 380, 182, color=POS, sw=2.2, dash="8 6"))
    frags.append(line(380, 228, 380, H - 40, color=POS, sw=2.2, dash="8 6"))
    frags.append(text(380, 62, "межа команд", size=13, color=POS, bold=True))

    # вузли команди A (ліворуч)
    A = [(150, 150), (250, 130), (155, 275), (255, 285), (200, 205)]
    # вузли команди B (праворуч)
    B = [(510, 150), (610, 135), (515, 275), (615, 285), (560, 205)]

    def dense(nodes, color):
        out = []
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                out.append(line(nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1],
                                color=color, sw=1.2))
        return out

    # густі дешеві зв'язки всередині кожної команди — під вузлами
    frags += dense(A, "#9fb4e8")
    frags += dense(B, "#9fb4e8")

    # один тонкий контракт крізь межу — дві ділянки, що впираються в коробку
    # (не суцільна лінія крізь напис), тож svgcheck не бачить наскрізного різу
    b_c, w_c, h_c = textbox(380, 205, "контракт", size=12, bold=True,
                            fill="#eafaf0", stroke=FIELD, pad=6)
    box_l, box_r = 380 - w_c / 2, 380 + w_c / 2
    frags.append(line(255, 205, box_l, 205, color=FIELD, sw=2.6))
    frags.append(line(box_r, 205, 505, 205, color=FIELD, sw=2.6))
    frags.append(b_c)

    # вузли
    for (x, y) in A:
        frags.append(circle(x, y, 15, fill="#eaf0fd", stroke=NEG, sw=1.8))
    for (x, y) in B:
        frags.append(circle(x, y, 15, fill="#eaf0fd", stroke=NEG, sw=1.8))

    # підписи команд
    frags.append(text(200, H - 24, "Команда A — модуль A", size=14, bold=True, color=INK))
    frags.append(text(560, H - 24, "Команда B — модуль B", size=14, bold=True, color=INK))

    render(os.path.join(IMG, 'team-seam.svg'), W, H, *frags,
           title="Стик системи лягає на стик організації")


def fig_history_timeline():
    """Історична лінія: спостереження 1968 → назва → популяризація → інверсія 2010 → книга 2019.
    Вага фігури — показати ~42-річну паузу між спостереженням Конвея й його переверненням."""
    ACC, ACCBG = "#7a4ea8", "#f3edfb"   # фіолетовий — момент інверсії
    W, H = 960, 470
    p = []

    axis_y = 150
    x0, x1 = 70, W - 70
    p.append(line(x0, axis_y, x1, axis_y, color=MUTED, sw=2))
    p.append(arrow(x1 - 2, axis_y, x1 + 20, axis_y, color=MUTED, sw=2))
    p.append(text(x1 + 22, axis_y + 4, "час", size=10.5, color=MUTED, anchor="start", italic=True))

    # (рік, заголовок, підпис, колір, гаряча-віха?)
    miles = [
        ("1968", "Конвей публікує",
         "«How Do Committees\nInvent?» у Datamation —\nсаме спостереження", NEG, False),
        ("1968", "Мілі дає назву",
         "на симпозіумі з модульного\nпрограмування Джордж Мілі\nназиває це «законом Конвея»", MUTED, False),
        ("1975", "Брукс поширює",
         "«Mythical Man-Month»\nробить назву відомою\nусій індустрії", MUTED, False),
        ("2010", "інверсія",
         "ЛеРой і Саймонс:\nне терпи закон —\nоберни його у важіль", ACC, True),
        ("2019", "Team Topologies",
         "Скелтон і Паїш —\nціла книга-інструкція\nз оберненого маневру", FIELD, False),
    ]
    n = len(miles)
    slot = (x1 - x0) / n
    for i, (year, title_, sub, col, hot) in enumerate(miles):
        cx = x0 + slot * (i + 0.5)
        p.append(circle(cx, axis_y, 8 if hot else 6,
                        fill=(ACCBG if hot else BG), stroke=col, sw=2.4 if hot else 1.8))
        yb, yw, yh = textbox(cx, axis_y - 54, year, size=13, pad=8,
                             fill=(ACCBG if hot else "#eef1f5"),
                             stroke=col, sw=2 if hot else 1.4, color=col, bold=True)
        p.append(yb)
        p.append(line(cx, axis_y - 54 + yh / 2, cx, axis_y - 8, color=col, sw=1.4,
                      dash=None if hot else "3 3"))
        p.append(text(cx, axis_y + 42, title_, size=12, color=col, bold=True))
        p.append(mtext(cx, axis_y + 66, sub, size=9.6, color=INK, lh=1.3))

    # дужка над паузою 1975→2010
    slot_c = lambda i: x0 + slot * (i + 0.5)
    gx0, gx1 = slot_c(2), slot_c(3)
    gy = axis_y - 104
    p.append(line(gx0, gy, gx1, gy, color=ACC, sw=1.4, dash="5 4"))
    p.append(line(gx0, gy, gx0, axis_y - 74, color=ACC, sw=1.4, dash="5 4"))
    p.append(line(gx1, gy, gx1, axis_y - 74, color=ACC, sw=1.4, dash="5 4"))
    p.append(text((gx0 + gx1) / 2, gy - 8, "≈ 35 років спостереження терпіли як прокляття", size=10, color=ACC, bold=True))

    # нижня плашка-висновок
    concl = ("спершу — діагноз (система копіює організацію),  "
             "аж потім — рецепт (спроєктуй організацію під систему)")
    cb, cw, ch = textbox(W / 2, H - 34, concl, size=10.5, pad=11,
                         fill="#eef6ef", stroke=FIELD, sw=1.6, color=INK)
    p.append(cb)

    render(os.path.join(IMG, 'history-timeline.svg'), W, H, *p,
           title="Від спостереження Конвея (1968) до оберненого маневру (2010)")


if __name__ == '__main__':
    fig_inversion()
    fig_team_seam()
    fig_history_timeline()
    print("figs done")
