# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

CORE   = "#27ae60"    # ядро / багатий домен — зелене
THIN   = "#c0392b"    # тонко / у трубах — червоне
MID    = "#b8860b"    # допоміжне — темно-золоте
GEN    = "#2457d6"    # загальне — синє
COREFILL = "#eefaf1"
MIDFILL  = "#fdf6e3"
GENFILL  = "#eaf0fd"
THINFILL = "#fdecea"


# ── Фігура 1: діагностика — чи має ця частина що приборкувати ─────────────────
def fig_diagnostic():
    W, H = 800, 560
    frags = []
    cx = 400

    body, _, sh = textbox(cx, 54, "Ця частина системи: де живе складність?",
                          size=15, bold=True, pad=14, min_w=400,
                          fill="#eef1f5", stroke=LINE, sw=2)
    frags.append(body)

    qs = [
        (168, "1.  Складність — у предметі (правила, що їх тримає експерт)?"),
        (262, "2.  Експерт міг би сказати коду: «ні, правило не таке»?"),
    ]
    qw, qh = 560, 62
    prev_bottom = 54 + sh / 2
    for (qy, label) in qs:
        frags.append(arrow(cx, prev_bottom, cx, qy - qh / 2 - 2, sw=2))
        frags.append(fitbox(cx - qw / 2, qy - qh / 2, qw, qh, label, size=14,
                            fill="#f7f9fb", stroke=LINE, sw=1.8, color=INK))
        prev_bottom = qy + qh / 2

    oy = 470
    left_cx, right_cx = 205, 585
    frags.append(fitbox(left_cx - 150, oy - 40, 300, 80,
                        "Багатий домен →\nDDD окупається", size=15,
                        fill=COREFILL, stroke=CORE, sw=2.6, color=INK, bold=True))
    frags.append(fitbox(right_cx - 150, oy - 40, 300, 80,
                        "Тонко / у трубах →\nне DDD: CRUD або\nінструменти масштабу", size=13,
                        fill=THINFILL, stroke=THIN, sw=2.6, color=INK, bold=True))

    frags.append(arrow(cx - 34, 262 + qh / 2 + 4, left_cx + 46, oy - 40 - 4, color=CORE, sw=2.2))
    frags.append(arrow(cx + 34, 262 + qh / 2 + 4, right_cx - 46, oy - 40 - 4, color=THIN, sw=2.2))
    frags.append(text(150, 388, "обидва  ТАК", size=12, italic=True, color=CORE))
    frags.append(text(640, 388, "будь-яке  НІ", size=12, italic=True, color=THIN))

    render(os.path.join(OUT, "diagnostic.svg"), W, H, *frags)


# ── Фігура 2: сходи DDD-лайт — лізь настільки, наскільки частина заслужила ────
def fig_ladder():
    W, H = 1010, 540
    frags = []

    steps = [
        (170, 405, "Єдина мова",        "майже завжди — майже безкоштовно"),
        (400, 315, "Багата модель",     "де є правила"),
        (630, 225, "Агрегат",           "де група з одним інваріантом"),
        (860, 135, "Обмежений контекст", "де слово почало означати різне"),
    ]
    bw, bh = 214, 54

    # сполучні стрілки між сходинками (край-до-краю, у проміжку — не крізь текст)
    for i in range(len(steps) - 1):
        x1, y1 = steps[i][0] + bw / 2, steps[i][1]
        x2, y2 = steps[i + 1][0] - bw / 2, steps[i + 1][1]
        frags.append(arrow(x1 + 2, y1 - 6, x2 - 2, y2 + 6, color=MUTED, sw=2))

    for (bx, by, name, trig) in steps:
        frags.append(fitbox(bx - bw / 2, by - bh / 2, bw, bh, name, size=15,
                            fill=COREFILL, stroke=CORE, sw=2.4, color=INK, bold=True))
        frags.append(text(bx, by + bh / 2 + 20, trig, size=12, italic=True, color=MUTED))

    # вісь ціни внизу
    frags.append(arrow(300, 495, 700, 495, color=INK, sw=1.8))
    frags.append(text(500, 522, "дешево, часто  →  дорого, зрідка", size=13, color=INK))

    render(os.path.join(OUT, "ladder.svg"), W, H, *frags)


# ── Фігура 3: дози DDD по частинах Digital Homes ─────────────────────────────
def fig_dh_doses():
    W, H = 1020, 450
    frags = []

    lanes = [
        (108, "ЯДРО", CORE, COREFILL,
         "Автоматика: правила сценаріїв\n(коли гріти · сцени · блокування безпеки)",
         "повний DDD:\nмова + модель + агрегат + контекст"),
        (232, "ДОПОМІЖНЕ", MID, MIDFILL,
         "Реєстр пристроїв · кімнати · розклади",
         "легко: трохи мови,\nздебільшого CRUD"),
        (356, "ЗАГАЛЬНЕ", GEN, GENFILL,
         "Користувачі · сповіщення · аудит · пошта",
         "готове / CRUD —\nбез DDD"),
    ]

    for (ly, tag, col, fill, examples, dose) in lanes:
        # мітка зони ліворуч
        frags.append(fitbox(30, ly - 26, 130, 52, tag, size=13,
                            fill=fill, stroke=col, sw=2.4, color=INK, bold=True))
        # приклади частин
        frags.append(fitbox(190, ly - 44, 470, 88, examples, size=14,
                            fill=fill, stroke=col, sw=1.8, color=INK))
        # доза DDD праворуч
        frags.append(fitbox(700, ly - 40, 300, 80, dose, size=13,
                            fill="#ffffff", stroke=col, sw=2.4, color=INK, bold=True))

    render(os.path.join(OUT, "dh-doses.svg"), W, H, *frags)


# ── Фігура 4: маятник моди довкола DDD ───────────────────────────────────────
def fig_pendulum():
    W, H = 1160, 600
    frags = []

    pivot = (580, 78)
    over  = (834, 237)   # хитнуло вправо — обряд на все
    under = (326, 237)   # інший бік — знекровлена модель
    rest  = (580, 378)   # спокій маятника — судження

    # дуга розмаху (пунктир) через нижню точку спокою
    frags.append('<path d="M%.0f,%.0f Q%.0f,%.0f %.0f,%.0f" fill="none" '
                 'stroke="%s" stroke-width="2" stroke-dasharray="7 6"/>'
                 % (under[0], under[1], rest[0], 519, over[0], over[1], MUTED))

    # ниточка й тягар у «хайповому» положенні (вправо)
    frags.append(line(pivot[0], pivot[1], over[0], over[1], color=INK, sw=3))
    frags.append(circle(pivot[0], pivot[1], 7, fill=INK, stroke=INK, sw=1))
    frags.append(circle(over[0], over[1], 18, fill=THIN, stroke=INK, sw=2))
    frags.append(text(over[0], over[1] + 5, "?", size=17, color="#ffffff", bold=True))

    # привид іншого краю та зелене кільце-ціль у спокої
    frags.append(circle(under[0], under[1], 13, fill="#ffffff", stroke=THIN, sw=2))
    frags.append(circle(rest[0], rest[1], 15, fill=COREFILL, stroke=CORE, sw=3))

    # зелена стрілка розвороту: з «обряду» назад до судження
    frags.append('<path d="M%.0f,%.0f C%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="none" '
                 'stroke="%s" stroke-width="3.2" marker-end="url(#arrow)"/>'
                 % (over[0] - 6, over[1] + 8, 800, 336, 668, 398, rest[0] + 22, rest[1] - 2, CORE))
    frags.append(mtext(648, 292, ["розворот", "стратегія понад тактику"],
                       size=12, color=CORE, anchor="middle"))

    # підписи трьох положень (з запасом, шрифт не тиснемо)
    frags.append(fitbox(70, 104, 268, 92,
                        "НЕДОМІР\nзнекровлена модель\n(Фаулер, 2003: анти-патерн)",
                        size=14, fill=THINFILL, stroke=THIN, sw=2.2, color=INK, bold=True))
    frags.append(line(240, 196, under[0], under[1] - 6, color=MUTED, sw=1.4, dash="4 4"))

    frags.append(fitbox(822, 104, 268, 92,
                        "ПЕРЕМІР\nобряд на все · цеглинки скрізь\n(хайп 2000-х)",
                        size=14, fill=THINFILL, stroke=THIN, sw=2.2, color=INK, bold=True))
    frags.append(line(920, 196, over[0], over[1] - 6, color=MUTED, sw=1.4, dash="4 4"))

    frags.append(fitbox(428, 430, 304, 110,
                        "СУДЖЕННЯ\nповна доза — ядру,\nлегка — решті\n(Еванс, 2009–2016)",
                        size=14, fill=COREFILL, stroke=CORE, sw=2.8, color=INK, bold=True))
    frags.append(line(rest[0], rest[1] + 6, rest[0], 430, color=CORE, sw=1.6))

    render(os.path.join(OUT, "pendulum.svg"), W, H, *frags)


# ── Фігура 5: та сама частина — помилкова доза проти правильної ───────────────
def fig_dose_wrongright():
    W, H = 1080, 500
    frags = []

    xP, wP = 30, 180
    xW, wW = 230, 380
    xR, wR = 640, 410

    frags.append(text(xP + wP / 2, 58, "Частина", size=14, bold=True, color=INK))
    frags.append(text(xW + wW / 2, 58, "Помилкова доза", size=14, bold=True, color=THIN))
    frags.append(text(xR + wR / 2, 58, "Правильна доза", size=14, bold=True, color=CORE))

    rows = [
        (78, CORE, COREFILL,
         "ЯДРО\nавтоматика\nсценаріїв",
         "недобір → грудка багна:\nif status == 3 по сервісах,\nінваріант не стереже ніхто",
         "багатий агрегат:\nінваріант в одному місці,\nусе через корінь, мова предмета"),
        (212, MID, MIDFILL,
         "ДОПОМІЖНЕ\nреєстр\nпристроїв",
         "надмір → анемічна церемонія:\nпорожні «агрегати», фабрики,\nхендлери — ні над чим",
         "DTO + тонкий сервіс:\nназвані типи —\nі по всьому"),
        (346, GEN, GENFILL,
         "ЗАГАЛЬНЕ\nсповіщення\nй пошта",
         "надмір → моделювати домен там,\nде береться готове",
         "тонкий адаптер\nдо готової бібліотеки:\nнуль DDD"),
    ]
    ch = 124
    for (top, col, fill, label, wrong, right) in rows:
        frags.append(fitbox(xP, top, wP, ch, label, size=13, bold=True,
                            fill=fill, stroke=col, sw=2.4, color=INK))
        frags.append(fitbox(xW, top, wW, ch, wrong, size=13,
                            fill=THINFILL, stroke=THIN, sw=2.0, color=INK))
        frags.append(fitbox(xR, top, wR, ch, right, size=13,
                            fill=fill, stroke=col, sw=2.0, color=INK))

    render(os.path.join(OUT, "dose-wrong-right.svg"), W, H, *frags,
           title="Та сама система, три дози — і два способи їх схибити")


if __name__ == "__main__":
    fig_diagnostic()
    fig_ladder()
    fig_dh_doses()
    fig_pendulum()
    fig_dose_wrongright()
    print("figures written")
