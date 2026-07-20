# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Дві дороги до чужого коду: копія проти залежності на випуск ────────────────
def fig_two_roads():
    W, H = 1120, 560
    frags = []

    frags.append(text(285, 92, "Дорога 1: копія в проєкт", size=15, bold=True, color=POS))
    frags.append(text(838, 92, "Дорога 2: залежність на компонент", size=15, bold=True, color=FIELD))
    frags.append(line(560, 112, 560, 448, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА панель: першоджерело живе далі, копія застигла ──
    frags.append(text(145, 130, "першоджерело", size=11.5, color=MUTED))
    frags.append(fitbox(70, 138, 150, 44, "v1.0.0", size=13, bold=True, fill=FILL, stroke=MUTED, sw=1.4))
    frags.append(fitbox(70, 210, 150, 44, "v1.1.0\n+виправлення", size=12, bold=True, fill=FILL, stroke=MUTED, sw=1.4))
    frags.append(fitbox(70, 282, 150, 44, "v1.2.0\n+можливість", size=12, bold=True, fill=FILL, stroke=MUTED, sw=1.4))
    frags.append(arrow(145, 182, 145, 208, color=MUTED))
    frags.append(arrow(145, 254, 145, 280, color=MUTED))

    frags.append(fitbox(300, 150, 210, 60, "твій проєкт:\nкопія застигла на v1.0.0",
                        size=12.5, bold=True, fill="#fdecea", stroke=POS, sw=2.0))
    frags.append(arrow(221, 160, 297, 178, color=MUTED))
    frags.append(text(405, 236, "новіші версії сюди не течуть", size=11, color=POS, italic=True))

    frags.append(fitbox(70, 356, 440, 84,
                        "Першоджерело пішло далі — копія\n"
                        "лишилась на v1.0.0. Виправлення й нові\n"
                        "можливості доводиться зливати руками —\n"
                        "це відгалуження, а не повторне використання.",
                        size=12, fill=FILL, stroke=POS, sw=1.6))

    # ── ПРАВА панель: випуски течуть під контролем споживача ──
    frags.append(text(685, 130, "першоджерело (випуски)", size=11.5, color=MUTED))
    frags.append(fitbox(610, 138, 150, 44, "v2.3.0", size=13, bold=True, fill=FILL, stroke=MUTED, sw=1.4))
    frags.append(fitbox(610, 210, 150, 44, "v2.3.1\nлатка", size=12, bold=True, fill=FILL, stroke=MUTED, sw=1.4))
    frags.append(fitbox(610, 282, 150, 44, "v2.4.0\n+можливість", size=12, bold=True, fill=FILL, stroke=MUTED, sw=1.4))
    frags.append(arrow(685, 182, 685, 208, color=MUTED))
    frags.append(arrow(685, 254, 685, 280, color=MUTED))

    frags.append(fitbox(858, 200, 202, 60, "твій проєкт:\nзалежність ^2.3.0",
                        size=12.5, bold=True, fill="#f2faf5", stroke=FIELD, sw=2.0))
    frags.append(text(806, 188, "оновлення течуть", size=11, color=FIELD, italic=True))
    frags.append(arrow(762, 224, 856, 230, color=FIELD, sw=2.0))

    frags.append(fitbox(610, 356, 450, 84,
                        "Версія — договір: сумісні оновлення\n"
                        "(2.3.1, 2.4.0) приходять самі; ламка\n"
                        "3.0.0 — лише коли ти сам перейдеш\n"
                        "і прочитаєш, що змінилось.",
                        size=12, fill=FILL, stroke=FIELD, sw=1.6))

    frags.append(fitbox(60, 464, 1000, 56,
                        "Повторно використати можна лише ВИПУЩЕНЕ — з номером версії, обіцянкою "
                        "сумісності\nй журналом змін. Без випуску «повторне використання» "
                        "вироджується в копію.",
                        size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.8))

    render(os.path.join(IMG, 'two-roads.svg'), W, H, *frags)


# ── Одиниця повтору = одиниця випуску: компонент зі стрижнем проти звалища ─────
def fig_coherent_vs_grabbag():
    W, H = 1120, 600
    frags = []

    frags.append(text(280, 92, "Компонент зі стрижнем", size=15, bold=True, color=FIELD))
    frags.append(text(840, 92, "Звалище без теми", size=15, bold=True, color=POS))
    frags.append(line(560, 108, 560, 405, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА панель: money — одна тема ──
    frags.append(rect(90, 120, 380, 210, fill="#f2faf5", stroke=FIELD, sw=2.0))
    frags.append(text(280, 150, "money", size=15, bold=True, color=FIELD))
    for cx, cy, lab in [(112, 165, "Гроші (Money)"), (288, 165, "Валюта (Currency)"),
                        (112, 213, "Округлення"), (288, 213, "Обмін валют")]:
        frags.append(fitbox(cx, cy, 165, 42, lab, size=12.5, bold=True, fill=BG, stroke=FIELD, sw=1.3))
    frags.append(fitbox(190, 280, 180, 34, "випуск v1.4.0", size=12.5, bold=True, fill=FILL, stroke=FIELD, sw=1.6))

    frags.append(arrow(280, 330, 280, 348, color=FIELD, sw=2.0))
    frags.append(fitbox(130, 350, 300, 48, "споживач бере компонент ЦІЛИМ —\nбо всі класи про одне",
                        size=12, bold=True, fill=BG, stroke=FIELD, sw=1.6))
    frags.append(fitbox(90, 424, 380, 84,
                        "Виходить, коли змінюється тема «гроші».\nНомер версії щось означає.\n"
                        "Залежність легка: береш рівно те, що хотів.",
                        size=12, fill=FILL, stroke=FIELD, sw=1.6))

    # ── ПРАВА панель: utils/common — теми немає ──
    frags.append(rect(610, 120, 420, 210, fill="#fdecea", stroke=POS, sw=2.0))
    frags.append(text(820, 150, "utils / common", size=15, bold=True, color=POS))
    for cx, cy, lab in [(625, 165, "форматування дат"), (825, 165, "HTTP-обгортка"),
                        (625, 210, "розбирач CSV"), (825, 210, "прапорці можливостей"),
                        (625, 255, "математика знижок"), (825, 255, "…і ще десяток")]:
        frags.append(fitbox(cx, cy, 190, 40, lab, size=12, bold=True, fill=BG, stroke=POS, sw=1.3))
    frags.append(fitbox(700, 300, 240, 26, "новий випуск мало не щотижня", size=11.5, bold=True,
                        fill=FILL, stroke=POS, sw=1.6))

    frags.append(arrow(820, 330, 820, 348, color=POS, sw=2.0))
    frags.append(fitbox(650, 350, 340, 48, "споживач хотів ОДНУ функцію —\nтягне все й новий випуск щотижня",
                        size=12, bold=True, fill=BG, stroke=POS, sw=1.6))
    frags.append(fitbox(610, 424, 420, 84,
                        "Теми немає: що означає перехід 8.2→8.3 — невідомо.\n"
                        "Будь-який доробок будь-кого — випуск, що будить усіх.\n"
                        "Залежність важка: береш усе заради дрібниці.",
                        size=12, fill=FILL, stroke=POS, sw=1.6))

    frags.append(fitbox(60, 530, 1000, 50,
                        "REP: клади в компонент те, що ВИПУСКАЮТЬ і БЕРУТЬ разом — спільна тема "
                        "робить номер версії осмисленим, а залежність легкою.",
                        size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.8))

    render(os.path.join(IMG, 'coherent-vs-grabbag.svg'), W, H, *frags)


# ── Життєвий цикл money: який розряд рухає яка зміна + вікно каре ──────────────
def fig_semver_lifecycle():
    W, H = 1200, 520
    frags = []
    frags.append(text(600, 44, "Життєвий цикл money: що рухає який розряд", size=16, bold=True))

    cy = 172
    boxes = [
        (70,  "v1.0.0", MUTED, "перший випуск\nMoney(10.5,'USD')"),
        (380, "v2.0.0", POS,   "центи, фабрика\nMoney.of(1050,'USD')"),
        (690, "v2.1.0", FIELD, "+ convert()"),
        (1000, "v2.1.1", NEG,  "convert():\nбанкове округлення"),
    ]
    for x, lab, col, note in boxes:
        frags.append(fitbox(x, cy - 27, 150, 54, lab, size=17, bold=True, fill=BG, stroke=col, sw=2.2))
        frags.append(fitbox(x, cy + 40, 150, 46, note, size=10.5, fill=FILL, stroke=col, sw=1.3))

    # переходи між випусками: стрілка + підпис зверху
    trans = [
        (220, 380, POS,   "ламка зміна\nMAJOR ↑"),
        (530, 690, FIELD, "нова можливість\nMINOR ↑"),
        (840, 1000, NEG,  "виправлення\nPATCH ↑"),
    ]
    for x1, x2, col, lab in trans:
        frags.append(arrow(x1 + 4, cy, x2 - 4, cy, color=col, sw=2.2))
        frags.append(fitbox((x1 + x2) / 2 - 92, 92, 184, 44, lab, size=11.5, bold=True,
                            fill=BG, stroke=col, sw=1.5))

    # смуга вікна каре ^2.1.0: від 2.1.0 включно до <3.0.0
    frags.append(rect(690, 300, 462, 52, fill="#f2faf5", stroke=FIELD, sw=2.0))
    frags.append(text(921, 324, "^2.1.0 приймає: 2.1.0 ≤ версія < 3.0.0", size=13, bold=True, color=FIELD))
    frags.append(text(600, 328, "≥ 2.1.0", size=11.5, color=FIELD, anchor="end", italic=True))
    frags.append(line(1162, 292, 1162, 360, color=POS, sw=1.6, dash="5,4"))
    frags.append(text(1170, 330, "3.0.0 ✗", size=11.5, color=POS, anchor="start", bold=True))

    frags.append(fitbox(80, 402, 1040, 62,
                        "Автор ріже випуски; споживач із ^2.1.0 сам підхоплює 2.1.1 і 2.2.0,\n"
                        "а 3.0.0 бере лише навмисне — прочитавши, що там ламається.",
                        size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.8))

    render(os.path.join(IMG, 'semver-lifecycle.svg'), W, H, *frags)


# ── Діамантовий конфлікт: дві залежності вимагають несумісних мажорів ──────────
def fig_diamond_conflict():
    W, H = 1160, 600
    frags = []
    frags.append(text(580, 44, "Діамантовий конфлікт: несумісні вимоги до money", size=16, bold=True))

    # вузли діаманта
    frags.append(fitbox(480, 86, 200, 50, "checkout\n(застосунок)", size=13, bold=True, fill=BG, stroke=MUTED, sw=2.0))
    frags.append(fitbox(200, 224, 200, 54, "report\n(звіти)", size=13, bold=True, fill=BG, stroke=POS, sw=2.0))
    frags.append(fitbox(760, 224, 200, 54, "ledger\n(журнал)", size=13, bold=True, fill=BG, stroke=NEG, sw=2.0))
    frags.append(fitbox(440, 356, 280, 92,
                        "money?\n^1.0.0 → < 2.0.0\n^2.0.0 → ≥ 2.0.0\nспільної версії НЕМА",
                        size=13, bold=True, fill="#fdecea", stroke=POS, sw=2.2))

    # ребра застосунок → залежності
    frags.append(arrow(510, 136, 340, 222, color=MUTED, sw=1.8))
    frags.append(arrow(650, 136, 820, 222, color=MUTED, sw=1.8))
    # ребра залежності → money
    frags.append(arrow(340, 280, 480, 354, color=POS, sw=2.0))
    frags.append(arrow(820, 280, 680, 354, color=NEG, sw=2.0))
    # підписи вимог — збоку від стрілок
    frags.append(fitbox(150, 300, 170, 44, "потребує\nmoney ^1.0.0", size=11.5, bold=True, fill=BG, stroke=POS, sw=1.4))
    frags.append(fitbox(840, 300, 170, 44, "потребує\nmoney ^2.0.0", size=11.5, bold=True, fill=BG, stroke=NEG, sw=1.4))

    # смуга виходів
    frags.append(text(580, 486, "Виходи:", size=13, bold=True))
    outs = [
        (60,  340, FIELD, "Справжній: підняти report за ламку\nзміну до мажора 2 — обидві на\nодному money."),
        (420, 340, MUTED, "Дві копії, якщо Money не перетинає\nмежу report/ledger (npm: вкладені;\nCargo: два major поруч)."),
        (780, 320, POS,   "Пастка: Money з двох копій — різні\nтипи; instanceof падає,\nadd() кидає помилку."),
    ]
    for x, w, col, txt in outs:
        frags.append(fitbox(x, 500, w, 78, txt, size=11.5, fill=FILL, stroke=col, sw=1.6))

    render(os.path.join(IMG, 'diamond-conflict.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_two_roads()
    fig_coherent_vs_grabbag()
    fig_semver_lifecycle()
    fig_diamond_conflict()
    print("figures written to", IMG)
