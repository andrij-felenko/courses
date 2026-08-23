# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER = "#e08a1e"


def fig_gate():
    """Ворота рішення: чи заслуговує цей співавтор дубля взагалі."""
    W, H = 1000, 440
    frags = []

    # ── співавтор (вхід) ────────────────────────────────────────────
    frags.append(fitbox(60, 176, 190, 92,
                         "співавтор,\nвід якого залежить\nтвій код", size=13.5,
                         fill="#fbfcfd", stroke=INK, sw=2))
    frags.append(arrow(252, 222, 322, 222))

    # ── ворота: чотири спускові гачки ───────────────────────────────
    gx, gy, gw, gh = 324, 96, 300, 252
    frags.append(rect(gx, gy, gw, gh, fill="#f4f6f8", stroke=INK, sw=2))
    frags.append(text(gx + gw / 2, gy + 30, "чи він…", size=15, bold=True))
    triggers = ["повільний", "недетермінований",
                "має незворотний ефект", "ще не існує / недосяжний"]
    for i, t in enumerate(triggers):
        ty = gy + 66 + i * 42
        frags.append(text(gx + 26, ty, "•", size=15, color=POS, anchor="start"))
        frags.append(text(gx + 46, ty, t, size=13.5, color=INK, anchor="start"))

    # ── вихід «хоч один» → дубль (угору-праворуч, червоний) ──────────
    frags.append(arrow(gx + gw, gy + 60, 700, 128, color=POS, sw=2.2))
    frags.append(text(668, 96, "хоч один", size=12.5, bold=True, color=POS, anchor="start"))
    frags.append(fitbox(704, 92, 250, 96,
                        "ДУБЛЬ на шві —\nнайдешевший, що дає\nкерування й спостереження",
                        size=12.5, fill="#fdecea", stroke=POS, sw=2.2))

    # ── вихід «жоден» → справжній (униз-праворуч, зелений) ───────────
    frags.append(arrow(gx + gw, gy + gh - 60, 700, 320, color=FIELD, sw=2.2))
    frags.append(text(660, 356, "жоден", size=12.5, bold=True, color=FIELD, anchor="start"))
    frags.append(fitbox(704, 284, 250, 96,
                        "бери СПРАВЖНІЙ —\nнасамперед власну\nчисту логіку",
                        size=12.5, fill="#eafaf1", stroke=FIELD, sw=2.2))

    render(os.path.join(OUT, 'gate.svg'), W, H, *frags,
           title="Спершу — чи потрібен тут дубль узагалі")


def fig_meter():
    """Кількість дублів як лічильник дизайну: заплутаний юніт проти здорового."""
    W, H = 1020, 470
    frags = []

    frags.append(line(510, 92, 510, 430, color=LINE, sw=1.2, dash="4 5"))

    # ── ЛІВА панель: юніт, що просить п'ять дублів ───────────────────
    frags.append(text(255, 84, "ПРОСИТЬ П'ЯТИ ДУБЛІВ", size=14, bold=True, color=POS))
    frags.append(rect(60, 210, 150, 96, fill="#fbfcfd", stroke=INK, sw=2))
    frags.append(mtext(135, 252, ["юніт із", "купою", "співавторів"], size=13, lh=1.3))

    labels = ["база", "пошта", "годинник", "шлюз", "калькулятор"]
    bx, bw, bh = 300, 168, 44
    for i, lb in enumerate(labels):
        by = 104 + i * 72
        frags.append(rect(bx, by, bw, bh, fill="#fdecea", stroke=POS, sw=1.6))
        frags.append(text(bx + bw / 2 - 12, by + 28, lb, size=12.5))
        frags.append(text(bx + bw - 22, by + 29, "◑", size=15, color=POS))  # значок дубля
        frags.append(line(210, 258, bx, by + bh / 2, color=MUTED, sw=1.3))

    frags.append(mtext(255, 452, ["п'ять дублів = забагато співавторів", "→ дизайн просить поділу"],
                       size=12.5, color=POS, lh=1.35, bold=True))

    # ── ПРАВА панель: чисте ядро + тонка оболонка ───────────────────
    frags.append(text(765, 84, "ЗДОРОВИЙ ПОДІЛ", size=14, bold=True, color=FIELD))

    frags.append(rect(560, 150, 210, 120, fill="#eafaf1", stroke=FIELD, sw=2.4))
    frags.append(text(665, 196, "чисте ядро", size=14.5, bold=True, color=FIELD))
    frags.append(text(665, 222, "рішення — це", size=12.5))
    frags.append(text(665, 244, "чиста функція", size=12.5))
    frags.append(text(665, 300, "0 дублів", size=13, bold=True, color=FIELD))

    frags.append(rect(820, 150, 150, 120, fill="#fbfcfd", stroke=INK, sw=1.8))
    frags.append(mtext(895, 190, ["тонка", "оболонка"], size=13, lh=1.3, bold=True))
    frags.append(rect(838, 222, 116, 34, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(text(896, 244, "1–2 на краю", size=11.5, color=POS))
    frags.append(arrow(770, 210, 818, 210))

    frags.append(mtext(765, 452, ["дублі лише на справжніх зовнішніх швах", "→ ядро тестуємо без жодного"],
                       size=12.5, color=FIELD, lh=1.35, bold=True))

    render(os.path.join(OUT, 'meter.svg'), W, H, *frags,
           title="Дублі — лічильник дизайну, не лише ціна тесту")


def fig_verified_fake():
    """Перевірений фейк: один контрактний набір тримає фейк і справжнє в згоді."""
    W, H = 960, 450
    frags = []

    # спільний контрактний набір — угорі
    frags.append(rect(320, 74, 320, 66, fill="#eef2f6", stroke=INK, sw=2))
    frags.append(text(480, 102, "один контрактний набір", size=14.5, bold=True))
    frags.append(text(480, 124, "тих самих перевірок для обох", size=12.5, color=MUTED))

    # дві реалізації, які МУСЯТЬ його пройти
    fy, fw, fh = 210, 300, 92
    lx, rx = 80, 580

    frags.append(arrow(430, 142, lx + fw / 2, fy - 6, color=FIELD, sw=2))
    frags.append(arrow(530, 142, rx + fw / 2, fy - 6, color=FIELD, sw=2))

    frags.append(rect(lx, fy, fw, fh, fill="#eafaf1", stroke=FIELD, sw=2.2))
    frags.append(text(lx + fw / 2, fy + 30, "фейк — у пам'яті", size=14, bold=True, color=FIELD))
    frags.append(text(lx + fw / 2, fy + 56, "швидкий, у тесті", size=12.5))
    frags.append(text(lx + fw / 2, fy + 78, "МУСИТЬ пройти набір", size=12.5, color=INK))

    frags.append(rect(rx, fy, fw, fh, fill="#eafaf1", stroke=FIELD, sw=2.2))
    frags.append(text(rx + fw / 2, fy + 30, "справжнє — адаптер", size=14, bold=True, color=FIELD))
    frags.append(text(rx + fw / 2, fy + 56, "повільне, у бою", size=12.5))
    frags.append(text(rx + fw / 2, fy + 78, "МУСИТЬ пройти набір", size=12.5, color=INK))

    # вердикт — обидва в згоді
    frags.append(rect(210, fy + fh + 34, 540, 44, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(480, fy + fh + 62,
                      "обидва шанують той самий контракт → фейк не дрейфує",
                      size=13.5, bold=True, color=FIELD))

    # застереження без набору
    frags.append(text(480, fy + fh + 108,
                      "без спільного набору фейк тихо розходиться з боєм — і зелений тест бреше",
                      size=12.5, color=POS, italic=True))

    render(os.path.join(OUT, 'verified-fake.svg'), W, H, *frags,
           title="Перевірений фейк: контракт тримає підробку чесною")


def fig_schools():
    """Родовід двох шкіл TDD: спільний корінь, дві доріжки, Фаулер називає розкол."""
    W, H = 1160, 520
    frags = []

    # ── мітки шкіл (над/під смугами) ────────────────────────────────
    frags.append(text(705, 50,
        "ЛОНДОНСЬКА / мокістська школа — тест КЕРУЄ будовою (перевірка взаємодії)",
        size=12.5, bold=True, color=FIELD))
    frags.append(text(705, 500,
        "ДЕТРОЙТСЬКА / класична школа — тест ПЕРЕВІРЯЄ результат (перевірка стану)",
        size=12.5, bold=True, color=NEG))

    # ── смуги-доріжки ───────────────────────────────────────────────
    frags.append(rect(270, 60, 870, 120, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(rect(270, 350, 870, 120, fill="#eaf0fd", stroke=NEG, sw=2))

    # ── спільний корінь ─────────────────────────────────────────────
    frags.append(fitbox(35, 210, 205, 110,
        "1996 · C3 / Chrysler\n(Детройт)\nКент Бек:\nтут ростуть XP і TDD",
        size=13, fill=FILL, stroke=INK, sw=2))
    frags.append(arrow(242, 250, 288, 140, sw=2))     # корінь → верхня доріжка
    frags.append(arrow(242, 285, 288, 392, sw=2))     # корінь → нижня доріжка

    # ── верхня доріжка: чотири віхи мокістів ────────────────────────
    top = [
        (385, "1999 · Connextra, Лондон\n«без getter-ів»"),
        (585, "2000 · «Endo-Testing» (XP2000)\nтермін mock object"),
        (785, "2004 · «Mock Roles, not Objects»\nOOPSLA · jMock"),
        (980, "2009 · GOOS\n«слухай свої тести»"),
    ]
    for cx, s in top:
        frags.append(fitbox(cx - 86, 77, 172, 86, s, size=12,
                            fill="#ffffff", stroke=FIELD, sw=1.8))
    for i in range(len(top) - 1):
        frags.append(arrow(top[i][0] + 86, 120, top[i + 1][0] - 86, 120, sw=1.6))

    # ── нижня доріжка: класичний канон ──────────────────────────────
    frags.append(fitbox(490, 367, 260, 86,
        "2002 · Кент Бек, «TDD by Example»\nканон класичного TDD",
        size=12, fill="#ffffff", stroke=NEG, sw=1.8))

    # ── Фаулер називає розкол (у проміжку між доріжками) ─────────────
    frags.append(line(760, 180, 760, 233, color=MUTED, sw=1.4, dash="4 4"))
    frags.append(line(760, 307, 760, 350, color=MUTED, sw=1.4, dash="4 4"))
    frags.append(fitbox(600, 233, 320, 74,
        "2004 · Мартін Фаулер, «Mocks Aren't Stubs»\nназиває розкол: класицисти vs мокісти",
        size=12, fill="#fdf3e2", stroke=AMBER, sw=2))

    render(os.path.join(OUT, 'schools.svg'), W, H, *frags,
           title="Дві школи виросли з одного коріння")


def fig_drift_catch():
    """Дві доріжки на один фейк: юніт-тест зелений, спільний набір червоний."""
    W, H = 1050, 470
    frags = []

    NEU = "#fbfcfd"      # нейтральна заливка
    GREENF, REDF = "#eafaf1", "#fdecea"

    # координати колонок (спільні для обох доріжок)
    ax, aw = 40, 252
    bx, bw = 338, 180
    cx, cw = 564, 206
    dx, dw = 816, 190
    bh = 76

    # ── ВЕРХНЯ доріжка: звичайний юніт-тест → зелено → у бій ──────────
    ty = 112
    tm = ty + bh / 2
    frags.append(text(ax + aw / 2, ty - 12, "ЗВИЧАЙНИЙ ЮНІТ-ТЕСТ", size=13, bold=True, color=MUTED))
    frags.append(fitbox(ax, ty, aw, bh, "вхід у ЧАСОВОМУ порядку\n1000 → 2000",
                        size=13, fill=NEU, stroke=INK, sw=1.8))
    frags.append(arrow(ax + aw + 4, tm, bx - 4, tm))
    frags.append(fitbox(bx, ty, bw, bh, "фейк\nslice(-n).reverse()",
                        size=13, fill="#f4f6f8", stroke=INK, sw=1.8))
    frags.append(arrow(bx + bw + 4, tm, cx - 4, tm))
    frags.append(fitbox(cx, ty, cw, bh, "✓  [2000, 1000]",
                        size=15, fill=GREENF, stroke=FIELD, sw=2.2, color=FIELD, bold=True))
    frags.append(arrow(cx + cw + 4, tm, dx - 4, tm))
    frags.append(fitbox(dx, ty, dw, bh, "їде в бій",
                        size=13, fill=NEU, stroke=INK, sw=1.6))

    # ── роздільник із приміткою (лінія з розривом під текст) ──────────
    frags.append(line(ax, 250, 360, 250, color=LINE, sw=1.1, dash="4 6"))
    frags.append(line(690, 250, dx + dw, 250, color=LINE, sw=1.1, dash="4 6"))
    frags.append(text(W / 2, 255, "той самий фейк — різні входи", size=12.5, color=MUTED, italic=True))

    # ── НИЖНЯ доріжка: спільний набір → червоно → спіймано ────────────
    by = 302
    bm = by + bh / 2
    frags.append(text(ax + aw / 2, by - 12, "СПІЛЬНИЙ КОНТРАКТНИЙ НАБІР", size=13, bold=True, color=POS))
    frags.append(fitbox(ax, by, aw, bh, "вхід БЕЗЛАДНО\n3000, 1000, 2000",
                        size=13, fill=NEU, stroke=INK, sw=1.8))
    frags.append(arrow(ax + aw + 4, bm, bx - 4, bm))
    frags.append(fitbox(bx, by, bw, bh, "той самий фейк",
                        size=13, fill="#f4f6f8", stroke=INK, sw=1.8))
    frags.append(arrow(bx + bw + 4, bm, cx - 4, bm))
    frags.append(fitbox(cx, by, cw, bh, "✗  [2000, 1000]\n3000 випало",
                        size=14, fill=REDF, stroke=POS, sw=2.2, color=POS, bold=True))
    frags.append(arrow(cx + cw + 4, bm, dx - 4, bm))
    frags.append(fitbox(dx, by, dw, bh, "спіймано ДО бою",
                        size=13, fill=REDF, stroke=POS, sw=1.8, color=POS, bold=True))

    render(os.path.join(OUT, 'drift-catch.svg'), W, H, *frags,
           title="Спільний набір ловить те, що юніт-тест проспав")


if __name__ == '__main__':
    fig_gate()
    fig_meter()
    fig_verified_fake()
    fig_schools()
    fig_drift_catch()
    print("figures written to", OUT)
