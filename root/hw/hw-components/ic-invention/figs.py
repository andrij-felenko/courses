# -*- coding: utf-8 -*-
"""Фігури до теми «Винайдення інтегральної схеми» (Кілбі / Нойс / Ерні).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
GREY = "#9aa0a6"     # метал
WAFER = "#aebfd8"    # кристал / пластина
GOLD = "#b9770e"     # навісні дротики


# ── Хронологія народження ІС ─────────────────────────────────────────────────
def fig_timeline():
    W, H = 760, 300
    f = [text(W / 2, 26, "Як народилася інтегральна схема (1957–1966)", size=16, bold=True)]
    base = 150
    f.append(line(60, base, 700, base, color=INK, sw=2))
    nodes = [
        (130, "груд. 1957", "Ерні:\nпланарна ідея", FIELD, False),
        (300, "вер. 1958", "Кілбі:\nперша схема", NEG, False),
        (470, "січ. 1959", "Нойс:\nмонолітна схема", POS, True),
        (640, "~1966", "TI ↔ Fairchild:\nперехресні ліцензії", MUTED, False),
    ]
    for x, date, label, col, hot in nodes:
        r = 11 if hot else 8
        f.append(circle(x, base, r, fill=("#fdecea" if hot else FILL), stroke=col, sw=2.5))
        f.append(text(x, base - 24, date, size=12, color=col, bold=True))
        f.append(mtext(x, base + 34, label, size=12, color=INK))
    f.append(text(W / 2, H - 14,
                  "Червоний вузол — серцевина: монолітна схема Нойса, де з'єднання надруковані металом, "
                  "а не навішані дротиками.", size=11.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "timeline.svg"), W, H, *f)


# ── Три внески ───────────────────────────────────────────────────────────────
def fig_three():
    W, H = 760, 290
    f = [text(W / 2, 26, "Три внески, а не один геній", size=16, bold=True)]
    cards = [
        ("Жан Ерні", "ФУНДАМЕНТ", "планарний оксид: захист\nпереходів + плоска\nізоляційна поверхня", FIELD),
        ("Джек Кілбі", "ПЕРШИЙ ЗРАЗОК", "довів, що вся схема\nвлазить в один шматок\n(хай з дротиками)", NEG),
        ("Роберт Нойс", "ФОРМА ДЛЯ СЕРІЇ", "метал, надрукований\nпо оксиду Ерні —\nможна тиражувати", POS),
    ]
    bw, bh, gap = 210, 150, 24
    total = 3 * bw + 2 * gap
    x0 = (W - total) / 2
    cy = 160
    for i, (who, role, body, col) in enumerate(cards):
        x = x0 + i * (bw + gap)
        f.append(rect(x, cy - bh / 2, bw, bh, fill=FILL, stroke=col, sw=2.5))
        f.append(text(x + bw / 2, cy - bh / 2 + 26, who, size=15, color=INK, bold=True))
        f.append(text(x + bw / 2, cy - bh / 2 + 48, role, size=12.5, color=col, bold=True))
        f.append(mtext(x + bw / 2, cy - bh / 2 + 74, body, size=11.5, color=MUTED))
        if i < 2:
            f.append(arrow(x + bw + 2, cy, x + bw + gap - 2, cy, color=INK, sw=1.8))
    f.append(text(W / 2, H - 12,
                  "Придумати фундамент, зробити перший зразок і зробити придатним до серії — три різні справи.",
                  size=11.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "three-contributions.svg"), W, H, *f)


# ── Дротики Кілбі проти друкованого метала Нойса ──────────────────────────────
def fig_wires_vs_planar():
    W, H = 760, 320
    f = [text(W / 2, 26, "«Вуса» Кілбі проти друкованого метала Нойса", size=16, bold=True)]
    # ліворуч: Кілбі
    f.append(text(190, 58, "Кілбі: навісні дротики", size=13.5, color=NEG, bold=True))
    f.append(rect(70, 80, 240, 150, fill="#cdd9ec", stroke=INK, sw=2))
    for dx in (110, 160, 210, 260):
        f.append(circle(dx, 200, 7, fill=FILL, stroke=INK, sw=1.5))
        f.append('<path d="M %d,200 Q %d,110 %d,150" fill="none" stroke="%s" stroke-width="2"/>'
                 % (dx, dx - 30, 190, GOLD))
    f.append(text(190, 250, "садять вручну, поодинці", size=12, color=MUTED))
    f.append(text(190, 268, "серійно так не виготовиш", size=12, color=POS, italic=True))
    # праворуч: Нойс
    f.append(text(570, 58, "Нойс: метал по оксиду", size=13.5, color=POS, bold=True))
    f.append(rect(450, 80, 240, 150, fill=WAFER, stroke=INK, sw=2))
    f.append(rect(450, 150, 240, 12, fill="#dfe7c8", stroke="#9bbf5a", sw=1.2, rx=0))  # оксид
    f.append(text(700, 158, "оксид", size=10, color="#6b8e23", anchor="end"))
    for dx in (490, 540, 590, 640):
        f.append(line(dx, 120, dx, 150, color=GREY, sw=4))  # метал-доріжка
    f.append(line(470, 120, 660, 120, color=GREY, sw=4))    # шина зверху
    f.append(text(570, 250, "напилено за один крок", size=12, color=MUTED))
    f.append(text(570, 268, "можна випускати мільйонами", size=12, color=FIELD, italic=True))
    f.append(text(W / 2, H - 10,
                  "Обидва склали схему в одному кристалі; різниця — ЯК з'єднані деталі, і саме вона вирішила, "
                  "що піде в серію.", size=11.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "wires-vs-planar.svg"), W, H, *f)


# ── «Єресь» Ерні: оксид залишають ────────────────────────────────────────────
def fig_hoerni_oxide():
    W, H = 760, 330
    f = [text(W / 2, 26, "«Єресь» Ерні: оксид залишають на місці", size=16, bold=True)]
    # ліворуч: мезаметод (оксид змили)
    f.append(text(190, 58, "Мезаметод: оксид змили", size=13.5, color=POS, bold=True))
    f.append(rect(70, 130, 240, 90, fill=WAFER, stroke=INK, sw=2, rx=0))
    f.append('<path d="M 130,130 L 250,130 L 250,90 L 130,90 Z" fill="#9fb0c8" stroke="%s" stroke-width="2"/>' % INK)
    f.append(line(190, 90, 190, 130, color=POS, sw=2, dash="4,3"))
    f.append('<line x1="250" y1="92" x2="300" y2="70" stroke="%s" stroke-width="1.5" marker-end="url(#arrow)"/>' % LINE)
    f.append(text(300, 66, "перехід — голий:", size=11, color=POS, anchor="start"))
    f.append(text(300, 80, "бруд, волога, заряди", size=11, color=POS, anchor="start"))
    f.append(text(190, 245, "транзистори «пливуть»", size=12, color=MUTED, italic=True))
    # праворуч: планарний (оксид лишили)
    f.append(text(570, 58, "Планарний: оксид лишили", size=13.5, color=FIELD, bold=True))
    f.append(rect(450, 130, 240, 90, fill=WAFER, stroke=INK, sw=2, rx=0))
    f.append(rect(450, 112, 240, 18, fill="#dfe7c8", stroke="#9bbf5a", sw=1.5, rx=0))  # суцільний оксид
    f.append(text(458, 125, "оксид (SiO₂)", size=10.5, color="#6b8e23", anchor="start"))
    # вікно в оксиді + метал
    f.append(rect(540, 112, 24, 18, fill=BG, stroke="#9bbf5a", sw=1.2, rx=0))
    f.append(line(552, 96, 552, 112, color=GREY, sw=4))
    f.append('<line x1="600" y1="100" x2="566" y2="116" stroke="%s" stroke-width="1.5" marker-end="url(#arrow)"/>' % LINE)
    f.append(text(604, 98, "вікно + метал", size=11, color=NEG, anchor="start"))
    f.append(text(570, 245, "запечатує переходи +", size=12, color=MUTED))
    f.append(text(570, 262, "плоска підлога під метал", size=12, color=FIELD, italic=True))
    f.append(text(W / 2, H - 8,
                  "Той самий оксид робить дві справи: захищає переходи — і дає рівну ізоляційну поверхню, "
                  "по якій ведуть метал.", size=11.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "hoerni-oxide.svg"), W, H, *f)


# ── Як вужчала й ширшала атрибуція ───────────────────────────────────────────
def fig_attribution():
    W, H = 760, 300
    f = [text(W / 2, 26, "Як мінялася відповідь «хто винайшов ІС»", size=16, bold=True)]
    base = 150
    f.append(line(70, base, 690, base, color=INK, sw=2))
    stages = [
        (180, "1960-ті", "Кілбі, Леговець,\nНойс, Ерні", "4 імені", FIELD),
        (390, "1970–90-ті", "«Кілбі й Нойс»", "2 імені", POS),
        (600, "2000-ні", "історики повернули\nЕрні й Леговця", "знов 4", FIELD),
    ]
    for x, date, who, tag, col in stages:
        f.append(circle(x, base, 9, fill=FILL, stroke=col, sw=2.5))
        f.append(text(x, base - 26, date, size=12, color=col, bold=True))
        f.append(mtext(x, base + 30, who, size=12, color=INK))
        f.append(text(x, base + 70, tag, size=12.5, color=col, bold=True, italic=True))
    f.append(text(W / 2, H - 12,
                  "Історія спершу стискає колективний винахід до легенди про геніїв-одинаків, "
                  "а потім відновлює правду.", size=11.5, color=MUTED, italic=True))
    return render(os.path.join(IMG, "attribution-history.svg"), W, H, *f)


if __name__ == "__main__":
    fig_timeline()
    fig_three()
    fig_wires_vs_planar()
    fig_hoerni_oxide()
    fig_attribution()
    print("OK: 5 SVG -> ./img/")
