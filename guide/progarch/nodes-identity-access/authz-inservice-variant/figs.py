# -*- coding: utf-8 -*-
"""Фігури до кроку «Варіант А: кожен сервіс авторизує сам» (progarch / nodes-identity-access).
Три фігури:
  1) decision-in-service — рішення (PDP) живе в тому самому процесі, що й дані;
  2) rule-copies-drift  — те саме правило в кожному сервісі розповзається;
  3) data-locality-flip — чутлива точка: де лежать дані для рішення.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_TINT = "#eaf7ef"
BLUE_TINT = "#eaf0fd"
RED_TINT = "#fdecea"


# ── Фігура 1: рішення живе в процесі сервісу ─────────────────────────────────
def fig_decision_in_service():
    W, H = 880, 430
    parts = []
    # запит зліва
    parts.append(fitbox(28, 168, 152, 96, "запит\nБогдан →\n«відчинити\nзамок #42»", size=13,
                        fill=FILL))
    parts.append(arrow(182, 216, 246, 216))
    # великий процес сервісу
    parts.append(rect(250, 72, 602, 336, fill=BG, stroke=INK, sw=2))
    parts.append(text(551, 100, "Сервіс пристроїв — один процес", size=14, bold=True))
    parts.append(text(551, 121, "гейт (PEP) і рішення (PDP) — тут само, поруч із даними",
                     size=10.5, color=MUTED))
    # три кроки всередині
    parts.append(fitbox(284, 140, 536, 50, "1. завантажити об'єкт: замок #42  (у ньому homeId = 7)",
                        size=13, fill=FILL))
    parts.append(arrow(551, 191, 551, 216))
    parts.append(fitbox(284, 220, 536, 62,
                        "2. can(Богдан, «відчинити», замок #42)\nрішення обчислюється тут, у цьому ж процесі",
                        size=12.5, fill=GREEN_TINT, stroke=FIELD, sw=2.4))
    parts.append(arrow(551, 283, 551, 308))
    parts.append(fitbox(284, 312, 536, 50, "3. дозволено → подати сигнал на замок",
                        size=13, fill=FILL))
    render(os.path.join(IMG, "decision-in-service.svg"), W, H, *parts,
           title="Рішення живе в тому самому процесі, що й дані")


# ── Фігура 2: копії правила розповзаються ────────────────────────────────────
def fig_rule_copies_drift():
    W, H = 900, 440
    parts = []
    xs = [16, 242, 468, 694]
    bw = 196
    heads = ["Сервіс пристроїв", "Сервіс камер", "Сервіс правил", "Сервіс сповіщень"]
    rules = [
        "член дому\nAND роль ∈\n{власник,\nмешканець}",
        "член дому\nAND роль =\nвласник",
        "член дому\n— роль не\nперевіряють —",
        "— перевірки\nтут забули —",
    ]
    tags = ["еталон", "суворіше", "проґавили роль", "тиха дірка"]
    tagcol = [MUTED, POS, POS, POS]
    body_stroke = [LINE, POS, POS, POS]
    body_fill = [FILL, FILL, FILL, RED_TINT]
    for x, hd, ru, tg, tc, bs, bf in zip(xs, heads, rules, tags, tagcol, body_stroke, body_fill):
        parts.append(fitbox(x, 92, bw, 34, hd, size=12.5, bold=True, fill="#eef2f7"))
        parts.append(fitbox(x, 130, bw, 96, ru, size=12, fill=bf, stroke=bs,
                           sw=2.2 if bs == POS else 1.5))
        parts.append(text(x + bw / 2, 250, tg, size=12, color=tc, bold=True))
    render(os.path.join(IMG, "rule-copies-drift.svg"), W, H, *parts,
           title="Те саме правило, скопійоване в кожен сервіс — і воно розповзається")


# ── Фігура 3: чутлива точка — де лежать дані рішення ─────────────────────────
def fig_data_locality_flip():
    W, H = 920, 360
    parts = []
    # зони
    parts.append(rect(56, 84, 444, 150, fill=GREEN_TINT, stroke=MUTED, sw=1.2))
    parts.append(rect(500, 84, 364, 150, fill=BLUE_TINT, stroke=MUTED, sw=1.2))
    parts.append(mtext(278, 110, ["виграє Варіант А", "(перевірка в сервісі)"], size=13,
                      color=INK, bold=True))
    parts.append(mtext(682, 110, ["починає вигравати Варіант Б", "(центральний PDP)"], size=13,
                      color=INK, bold=True))
    # вісь
    parts.append(line(70, 178, 850, 178, color=INK, sw=2))
    parts.append(arrow(818, 178, 852, 178))
    parts.append(arrow(102, 178, 68, 178))
    # чутлива точка
    parts.append(line(500, 92, 500, 240, color=MUTED, sw=1.6, dash="6 5"))
    parts.append(text(500, 80, "чутлива точка", size=12, color=MUTED, bold=True))
    # маркери DH
    marks = [
        (130, ["ліміт запитів", "(свій лічильник)"]),
        (312, ["власник цього пристрою", "(членство поруч)"]),
        (600, ["членство — в", "іншому сервісі"]),
        (792, ["правило на кілька", "доменів воднораз"]),
    ]
    for mx, lines in marks:
        parts.append(circle(mx, 178, 5, fill=INK, stroke=INK))
        parts.append(mtext(mx, 205, lines, size=11, color=INK))
    render(os.path.join(IMG, "data-locality-flip.svg"), W, H, *parts,
           title="Чутлива точка: де лежать дані, потрібні для рішення")


# ── Фігура 4 (для вставки hist): маятник «точки рішення» ─────────────────────
def fig_decision_point_pendulum():
    W, H = 1060, 340
    p = []
    # три смуги-доби (за місцем, де фізично живе рішення)
    y0, bh = 96, 132
    p.append(rect(54, y0, 268, bh, fill=FILL, stroke=MUTED, sw=1.2))
    p.append(rect(322, y0, 368, bh, fill=BLUE_TINT, stroke=MUTED, sw=1.2))
    p.append(rect(690, y0, 316, bh, fill=GREEN_TINT, stroke=MUTED, sw=1.2))
    p.append(mtext(188, 138, ["поняття народжується:", "рішення — окрема функція,",
                              "місце ще не нав'язане"], size=12, color=INK))
    p.append(mtext(506, 138, ["доба ВИНЕСЕНОГО PDP", "окремий сервер рішень",
                              "(рішення — за мережею)"], size=12.5, color=INK))
    p.append(mtext(848, 138, ["маятник ПОВЕРТАЄ", "рушій рішень — у процесі,",
                              "поруч із PEP (co-located)"], size=12.5, color=INK))
    # межі діб
    p.append(line(322, 88, 322, 236, color=MUTED, sw=1.2, dash="5 5"))
    p.append(line(690, 88, 690, 236, color=MUTED, sw=1.6, dash="6 5"))
    # хитання туди…
    p.append(arrow(322, 66, 470, 66, color=NEG))
    p.append(text(400, 55, "винесли назовні", size=11.5, color=NEG, bold=True))
    # …і назад (дуга)
    p.append('<path d="M600 94 C 630 50, 720 50, 762 92" fill="none" '
             'stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>' % FIELD)
    p.append(text(686, 52, "назад у процес", size=11.5, color=FIELD, bold=True))
    # вісь часу
    p.append(line(54, 258, 1006, 258, color=INK, sw=2))
    p.append(arrow(978, 258, 1010, 258))
    p.append(text(996, 246, "час", size=11, color=MUTED, anchor="end"))
    # віхи
    marks = [
        (150, INK,   ["1996", "ISO/IEC 10181-3", "ADF / AEF"]),
        (272, INK,   ["2000", "RFC 2753", "PDP / PEP"]),
        (430, NEG,   ["2003", "XACML 1.0", "PDP/PEP → авторизація"]),
        (600, NEG,   ["2013", "XACML 3.0"]),
        (762, FIELD, ["2016", "OPA", "Go-бібліотека"]),
        (910, FIELD, ["2023", "AWS Cedar", "SDK у процесі"]),
    ]
    for mx, col, lines in marks:
        p.append(circle(mx, 258, 5, fill=col, stroke=col))
        p.append(mtext(mx, 280, lines, size=11.5, color=INK))
    render(os.path.join(IMG, "decision-point-pendulum.svg"), W, H, *p,
           title="Маятник «точки рішення»: винести PDP — і покликати назад")


# ── Фігура 5 (proj): об'єктна перевірка закриває IDOR ────────────────────────
def fig_idor_object_check():
    W, H = 940, 440
    parts = []
    parts.append(fitbox(220, 46, 500, 56,
                        "Оксана — мешканка дому 12 — тисне «відчинити замок #42»\n"
                        "(а замок #42 належить дому 7)", size=12.5, fill=FILL))
    parts.append(text(470, 118, "ліворуч — багована перевірка; праворуч — правильна",
                     size=11, color=MUTED))
    parts.append(line(470, 126, 470, 392, color=MUTED, sw=1.2, dash="5 5"))
    # ── ліва колонка: роль без об'єкта → діра ──
    parts.append(fitbox(58, 130, 374, 30, "БАГ: роль БЕЗ об'єкта", size=12.5, bold=True,
                        fill="#fdecea", stroke=POS, sw=1.3, color=POS))
    parts.append(fitbox(58, 172, 374, 58, "anyRoleOf(Оксана) → «resident»\n"
                        "мешканка ДЕСЬ — байдуже, де саме", size=12,
                        fill=RED_TINT, stroke=POS, sw=1.6))
    parts.append(arrow(245, 232, 245, 256))
    parts.append(fitbox(58, 258, 374, 44, "«resident» має право unlock ✓", size=12, fill=FILL))
    parts.append(arrow(245, 304, 245, 328))
    parts.append(fitbox(58, 330, 374, 58, "замок #42 ВІДЧИНЕНО\nчужий замок відкрито — IDOR",
                        size=12.5, bold=True, color=POS, fill=RED_TINT, stroke=POS, sw=2.4))
    # ── права колонка: роль У ДОМІ об'єкта → deny ──
    parts.append(fitbox(508, 130, 374, 30, "ФІКС: роль У ДОМІ об'єкта", size=12.5, bold=True,
                        fill="#eaf7ef", stroke=FIELD, sw=1.3))
    parts.append(fitbox(508, 172, 374, 58, "roleIn(Оксана, home-7) → ∅\n"
                        "у домі 7 вона НЕ член", size=12,
                        fill=GREEN_TINT, stroke=FIELD, sw=1.6))
    parts.append(arrow(695, 232, 695, 256))
    parts.append(fitbox(508, 258, 374, 44, "жодне правило не збіглося", size=12, fill=FILL))
    parts.append(arrow(695, 304, 695, 328))
    parts.append(fitbox(508, 330, 374, 58, "DENY 403\nчужий замок лишився замкнений",
                        size=12.5, bold=True, fill=GREEN_TINT, stroke=FIELD, sw=2.4))
    render(os.path.join(IMG, "idor-object-check.svg"), W, H, *parts,
           title="Ключ пошуку членства — дім самого об'єкта: тим і закрито IDOR")


# ── Фігура 6 (proj): два гейти — забута перевірка проскакує deny-by-default ───
def fig_two_gates():
    W, H = 940, 392
    parts = []
    parts.append(fitbox(20, 150, 120, 58, "запит на\nновому\nмаршруті", size=12, fill=FILL))
    parts.append(arrow(142, 179, 176, 179))
    # Гейт 1 — PEP
    parts.append(rect(178, 96, 214, 168, fill=BG, stroke=INK, sw=1.8))
    parts.append(text(285, 122, "Гейт 1 · PEP", size=13, bold=True))
    parts.append(mtext(285, 150, ["обробник", "покликав can()?"], size=11.5, color=INK))
    parts.append(mtext(285, 214, ["ЯКЩО ЗАБУВ —", "гейта тут просто нема"], size=10.5, color=POS))
    # Гейт 2 — PDP
    parts.append(rect(486, 96, 214, 168, fill=BG, stroke=INK, sw=1.8))
    parts.append(text(593, 122, "Гейт 2 · PDP", size=13, bold=True))
    parts.append(mtext(593, 150, ["явне правило", "збіглося?"], size=11.5, color=INK))
    parts.append(mtext(593, 214, ["нема правила →", "DENY (deny-by-default)"], size=10.5, color=FIELD))
    # ресурс
    parts.append(fitbox(770, 150, 150, 58, "замок\n(ресурс)", size=12, fill=FILL))
    # зелений шлях
    parts.append(arrow(392, 179, 486, 179))
    parts.append(text(439, 168, "покликав", size=10.5, color=FIELD))
    parts.append(arrow(700, 179, 770, 179))
    parts.append(text(735, 168, "allow", size=10.5, color=FIELD))
    # червоний обхід
    parts.append(line(285, 264, 285, 322, color=POS, sw=2.2))
    parts.append(line(285, 322, 845, 322, color=POS, sw=2.2))
    parts.append(arrow(845, 322, 845, 210, color=POS, sw=2.2))
    parts.append(text(548, 342,
                     "новий маршрут без can(): запит доходить до ресурсу, а відмовляти НІКОМУ",
                     size=11.5, color=POS))
    parts.append(text(470, 372,
                     "Лік: чок-пойнт (middleware / verify_authorized) жене КОЖЕН маршрут крізь Гейт 1.",
                     size=11.5, color=MUTED))
    render(os.path.join(IMG, "two-gates.svg"), W, H, *parts,
           title="Deny-by-default живе у Гейті 2 — а забута перевірка минає Гейт 1")


# ── Фігура 7 (proj): вікно застарілості кешу членства при відкликанні ────────
def fig_staleness_window():
    W, H = 960, 510
    parts = []
    # ── лейн A: лише TTL ──
    parts.append(text(70, 40, "стратегія A — лише TTL", size=12.5, bold=True, anchor="start"))
    parts.append(text(495, 90, "виключений ВСЕ ЩЕ відчиняє — вікно = TTL", size=11.5, color=POS))
    parts.append(rect(300, 136, 390, 28, fill=RED_TINT, stroke=POS, sw=1.4))
    parts.append(line(70, 150, 890, 150, color=INK, sw=2))
    parts.append(arrow(860, 150, 892, 150, color=INK, sw=2))
    parts.append(line(300, 100, 300, 215, color=MUTED, sw=1.4, dash="5 4"))
    parts.append(line(690, 100, 690, 215, color=MUTED, sw=1.4, dash="5 4"))
    parts.append(text(792, 195, "→ deny ✓", size=12, color=FIELD, bold=True))
    parts.append(text(300, 235, "t0: мешканця виключено", size=11, color=MUTED))
    parts.append(text(690, 235, "t0 + TTL: кеш протух", size=11, color=MUTED))
    # ── лейн B: інвалідація на подію ──
    parts.append(text(70, 270, "стратегія B — інвалідація на подію revoke",
                     size=12.5, bold=True, anchor="start"))
    parts.append(text(600, 320, "вікно ≈ 0 — виключений одразу не відчиняє ✓",
                     size=11.5, color=FIELD))
    parts.append(rect(288, 366, 24, 28, fill=RED_TINT, stroke=POS, sw=1.4))
    parts.append(line(70, 380, 890, 380, color=INK, sw=2))
    parts.append(arrow(860, 380, 892, 380, color=INK, sw=2))
    parts.append(line(300, 330, 300, 405, color=MUTED, sw=1.4, dash="5 4"))
    parts.append(text(300, 425, "t0: подія revoke → кеш викинуто", size=11, color=MUTED))
    # підпис-мораль
    parts.append(mtext(480, 465,
                      ["Застарілість на боці ВІДКЛИКАННЯ небезпечніша за застарілість на боці видачі:",
                       "виключений, що ще відчиняє, — це вже діра; тому revoke чистить кеш подією, не TTL."],
                      size=11, color=MUTED))
    render(os.path.join(IMG, "staleness-window.svg"), W, H, *parts,
           title="Кеш членства: вікно застарілості на відкликанні = TTL, поки подія його не стисне")


if __name__ == "__main__":
    fig_decision_in_service()
    fig_rule_copies_drift()
    fig_data_locality_flip()
    fig_decision_point_pendulum()
    fig_idor_object_check()
    fig_two_gates()
    fig_staleness_window()
    print("OK: 7 SVG ->", IMG)
