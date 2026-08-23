# -*- coding: utf-8 -*-
"""Фігури до кроку «Часткова відмова».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER   = "#b8860b"   # бурштиновий — «невідомо / хтозна»
AMBERBG = "#fff8e8"
AMBERST = "#c9a93b"


def xmark(cx, cy, r=8, color=POS, sw=2.4):
    """Хрестик «загубилось» двома лініями (не текстом — щоб не було накладань)."""
    return (line(cx - r, cy - r, cx + r, cy + r, color=color, sw=sw) +
            line(cx - r, cy + r, cx + r, cy - r, color=color, sw=sw))


# ───────── Фіг. 1: спільна доля проти незалежних доль ─────────
def fig_partial_state():
    W, H = 980, 470
    f = []

    # роздільник панелей
    f.append(line(485, 60, 485, 360, color="#e5e7eb", sw=1))

    # ── ЛІВА ПАНЕЛЬ: один процес — спільна доля ──
    f.append(text(240, 74, "Один процес — спільна доля", size=15, bold=True, color=FIELD))
    f.append(rect(70, 96, 340, 214, fill="#f2f9f4", stroke=FIELD, sw=1.8, rx=10))
    for lab, yy in [("Реєстр пристроїв", 118), ("Правила опалення", 176), ("Стани замків", 234)]:
        f.append(fitbox(102, yy, 276, 44, lab, size=13, fill="#eafaf0",
                        stroke=FIELD, color=INK, bold=True))
    f.append(mtext(240, 336, ["усе-або-нічого:", "усі живі — або процес упав цілком"],
                   size=12, color=MUTED))

    # ── ПРАВА ПАНЕЛЬ: багато машин — незалежні долі ──
    f.append(text(730, 74, "Багато машин — незалежні долі", size=15, bold=True, color=INK))
    # спільна пунктирна рамка «мережа»
    f.append(rect(540, 96, 380, 214, fill=BG, stroke=MUTED, sw=1.3, rx=12))
    f.append(rect(540, 96, 380, 214, fill="none", stroke=MUTED, sw=1.1, rx=12))
    f.append(text(730, 90, "з'єднані мережею", size=11, color=MUTED, italic=True))
    machines = [
        # cx,  cy,  назва,     стан,      колір,  заливка,  рамка
        (628, 150, "Хаб",     "живий",   FIELD, "#eafaf0", FIELD),
        (832, 150, "Хмара",   "впала",   POS,   "#fdecea", POS),
        (628, 246, "Твін",    "лаг",     AMBER, AMBERBG,   AMBERST),
        (832, 246, "Вендор",  "мовчить", POS,   "#fdecea", POS),
    ]
    for cx, cy, name, st, col, fill, stroke in machines:
        f.append(fitbox(cx - 78, cy - 32, 156, 64, name + "\n" + st, size=13,
                        fill=fill, stroke=stroke, color=col, bold=True, sw=1.8))
    f.append(mtext(730, 336, ["частковий стан: дехто живий, дехто ні —", "ОДНОЧАСНО"],
                   size=12, color=MUTED, bold=True))

    render(os.path.join(IMG, "partial-state.svg"), W, H, *f,
           title="Стан, якого на одній машині не буває")


# ───────── Фіг. 2: та сама тиша — протилежна правда ─────────
def fig_lost_ack():
    W, H = 980, 470
    f = []

    # роздільник сцен
    f.append(line(490, 52, 490, 372, color="#e5e7eb", sw=1))

    def scene(cL, cR, midX, heading, hcolor, arrived, hub_state, hub_col,
              has_ack, verdict, x0, x1):
        g = []
        # заголовок сцени
        g.append(text((x0 + x1) / 2, 66, heading, size=14, bold=True, color=hcolor))
        # вузли
        g.append(fitbox(cL - 62, 92, 124, 40, "Застосунок", size=12, bold=True))
        g.append(fitbox(cR - 62, 92, 124, 40, "Хаб", size=12, bold=True))
        # межа
        g.append(line(midX, 150, midX, 300, color=MUTED, sw=1.3, dash="5,6"))
        # повідомлення unlock
        g.append(text(cL + 8, 165, "unlock", size=11, bold=True, color=INK, anchor="start"))
        if arrived:
            g.append(arrow(cL, 178, cR - 4, 178, color=FIELD, sw=2.2))
        else:
            g.append(arrow(cL, 178, midX - 10, 178, color=POS, sw=2.2))
            g.append(xmark(midX, 178))
        # стан хаба
        g.append(fitbox(cR - 78, 200, 156, 34, hub_state, size=12,
                        color=hub_col, bold=True, fill=BG,
                        stroke=(hub_col if arrived else MUTED)))
        # підтвердження назад
        if has_ack:
            g.append(text(cR - 8, 258, "ok", size=11, bold=True, color=INK, anchor="end"))
            g.append(arrow(cR, 270, midX + 10, 270, color=POS, sw=2.2))
            g.append(xmark(midX, 270))
        # таймаут у клієнта
        g.append(text(cL, 296, "таймаут — тиша", size=11, bold=True, color=POS))
        # підсумок
        g.append(fitbox(x0 + 6, 326, (x1 - x0) - 12, 42, verdict, size=13,
                        fill=AMBERBG, stroke=AMBERST, color=INK, bold=True, sw=1.8))
        return g

    f += scene(120, 380, 250, "Запит не дійшов", POS, False,
               "замок: замкнений", INK, False,
               "тиша → а замок ЗАМКНЕНИЙ", 40, 470)
    f += scene(610, 870, 740, "Відповідь загубилась", FIELD, True,
               "замок: ВІДЧИНЕНО", FIELD, True,
               "тиша → а замок ВІДЧИНЕНИЙ", 510, 940)

    # нижній банер
    f.append(fitbox(250, 392, 480, 46, "Клієнт бачить те саме. Правда — протилежна.",
                    size=15, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))

    render(os.path.join(IMG, "lost-ack.svg"), W, H, *f,
           title="Та сама тиша ховає протилежну правду")


# ───────── Фіг. 3: три правди за тишею → відповідь ─────────
def fig_three_outcomes():
    W, H = 980, 430
    f = []

    # верхня рамка
    f.append(fitbox(360, 50, 260, 44, "Виклик не відповів — таймаут",
                    size=14, fill=AMBERBG, stroke=AMBERST, color=INK, bold=True, sw=1.8))

    # три гілки
    f.append(arrow(455, 96, 195, 126, color=NEG, sw=1.8))
    f.append(arrow(490, 96, 490, 126, color=POS, sw=1.8))
    f.append(arrow(525, 96, 795, 126, color=AMBER, sw=1.8))

    outcomes = [
        # cx,  текст рамки,                              підсумок,           колір, заливка,  рамка
        (185, "Запит не дійшов\nнічого не сталося",      "повтор безпечний", NEG,   "#eaf0fd", NEG,   FIELD),
        (490, "Виконалось,\nпідтвердження зникло\nефект уже стався", "повтор ЗАДВОЇТЬ", POS, "#fdecea", POS, POS),
        (795, "Ще летить,\nповільний\nефект, можливо, попереду", "повтор → гонка", AMBER, AMBERBG, AMBERST, AMBER),
    ]
    for cx, body, tail, col, fill, stroke, tailcol in outcomes:
        f.append(fitbox(cx - 130, 128, 260, 66, body, size=12,
                        fill=fill, stroke=stroke, color=col, bold=True, sw=1.6))
        f.append(text(cx, 216, tail, size=12, bold=True, color=tailcol))

    # сходяться у відповідь
    f.append(arrow(185, 228, 300, 274, color=MUTED, sw=1.6))
    f.append(arrow(490, 228, 490, 274, color=MUTED, sw=1.6))
    f.append(arrow(795, 228, 680, 274, color=MUTED, sw=1.6))

    f.append(fitbox(240, 276, 500, 56,
                    "Розрізнити зсередини не можна —\nзроби так, щоб було БАЙДУЖЕ, що сталося",
                    size=14, fill="#eafaf0", stroke=FIELD, color=INK, bold=True, sw=2))

    # інструменти
    f.append(arrow(490, 332, 490, 356, color=FIELD, sw=1.8))
    chips = [("таймаут", 165), ("ідемпотентність", 405), ("звірка стану", 660)]
    widths = [170, 190, 180]
    for (lab, x), w in zip(chips, widths):
        f.append(fitbox(x, 360, w, 40, lab, size=13, fill=FILL,
                        stroke=INK, color=INK, bold=True, sw=1.6))

    render(os.path.join(IMG, "three-outcomes.svg"), W, H, *f,
           title="Три правди за однією тишею — і що з цим робити")


# ═════════ Фігури до вставки «Дві банди, два генерали» (hist-two-generals) ═════════

# ───────── Регрес підтверджень + «прибери останнє» ─────────
def fig_ack_regress():
    W, H = 1000, 520
    f = []

    xA, xB = 150, 470          # лінії життя генералів
    yTop, yBot = 85, 392

    # заголовки
    f.append(text(xA, 70, "Генерал A", size=15, bold=True, color=INK))
    f.append(text(xB, 70, "Генерал B", size=15, bold=True, color=INK))
    # лінії життя
    f.append(line(xA, yTop, xA, yBot, color=MUTED, sw=1.2, dash="4,6"))
    f.append(line(xB, yTop, xB, yBot, color=MUTED, sw=1.2, dash="4,6"))

    midX = (xA + xB) / 2
    # щаблі драбини: (y, напрям A→B?, підпис)
    rungs = [
        (128, True,  "«б'ємо на світанку»"),
        (183, False, "«згоден»"),
        (238, True,  "«отримав „згоден“»"),
        (293, False, "«отримав, що ти отримав»"),
    ]
    for y, a2b, lab in rungs:
        f.append(text(midX, y - 9, lab, size=12, bold=True, color=INK))
        if a2b:
            f.append(arrow(xA + 4, y, xB - 4, y, color=FIELD, sw=2.0))
        else:
            f.append(arrow(xB - 4, y, xA + 4, y, color=NEG, sw=2.0))

    # вертикальне многокрап'я
    f.append(text(midX, 332, "⋮", size=22, bold=True, color=MUTED))

    # останній лист — без відповіді
    yLast = 372
    f.append(text(midX, yLast - 9, "«отримав, що ти отримав, що я…»", size=12, bold=True, color=MUTED))
    f.append(arrow(xA + 4, yLast, xB - 22, yLast, color=MUTED, sw=1.8))
    f.append(xmark(xB - 12, yLast, r=9, color=POS))
    f.append(mtext(midX, 406, ["останній лист лишається без відповіді —",
                               "відправник не знає, чи він дійшов"],
                   size=12, color=POS, bold=True))

    # ── права панель: «прибери останнє» ──
    px, pw = 662, 300
    f.append(rect(px, 96, pw, 350, fill="#f2f9f4", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(px + pw / 2, 124, "Чому гаранта не буває", size=14, bold=True, color=FIELD))
    f.append(line(px + 20, 136, px + pw - 20, 136, color=FIELD, sw=1))
    peel = [
        "Хай є НАЙкоротший",
        "протокол-гарант.",
        "Його останнє повідомлення m",
        "могло б загубитись —",
        "отже, підсумок не залежить",
        "від того, дійшло m чи ні.",
        "Значить, m зайве.",
        "Викинь m → протокол коротший,",
        "але теж гарант.",
        "Суперечність!",
    ]
    yy = 160
    for ln in peel:
        f.append(text(px + 18, yy, ln, size=13, color=INK, anchor="start"))
        yy += 24
    f.append(text(px + pw / 2, yy + 8, "⇒ скінченного гаранта НЕМА",
                  size=13, bold=True, color=POS))

    render(os.path.join(IMG, "ack-regress.svg"), W, H, *f,
           title="Найнижче підтвердження завжди лишається без відповіді")


# ───────── Родовід задачі: 1975 → 1978 → 1982 ─────────
def fig_generals_lineage():
    W, H = 1000, 380
    f = []

    axisY = 210
    f.append(line(80, axisY, 920, axisY, color=INK, sw=2))

    # cx, рік, заголовок, тіло, колір, заливка, рамка
    stations = [
        (210, "1975", "дві банди",
         "Аккоюнлу · Еканадгам · Губер\nSOSP · неможливість ДОВЕДЕНО",
         FIELD, "#eafaf0", FIELD),
        (500, "1978", "два генерали",
         "Джим Ґрей, «Notes on DB OS»\nдав НАЗВУ (парадокс)",
         NEG, "#eaf0fd", NEG),
        (790, "1982", "візантійські генерали",
         "Лемпорт · Шостак · Піз\nІНША модель: учасники брешуть",
         AMBER, AMBERBG, AMBERST),
    ]
    for cx, yr, head, body, col, fill, stroke in stations:
        f.append(fitbox(cx - 125, 66, 250, 92, head + "\n" + body, size=12,
                        fill=fill, stroke=stroke, color=INK, bold=True, sw=1.8))
        # конектор до осі + позначка року
        f.append(line(cx, 158, cx, axisY, color=stroke, sw=1.4))
        f.append(circle(cx, axisY, 5, fill=stroke, stroke=stroke))
        f.append(text(cx, axisY + 26, yr, size=15, bold=True, color=col))

    # дужка «назва пізніше за доведення» між 1975 і 1978
    by = 296
    f.append(line(210, by, 500, by, color=MUTED, sw=1.2))
    f.append(line(210, by - 6, 210, by, color=MUTED, sw=1.2))
    f.append(line(500, by - 6, 500, by, color=MUTED, sw=1.2))
    f.append(text(355, by + 18, "назва — на 3 роки ПІЗНІШЕ за доведення",
                  size=12, color=MUTED, italic=True))
    # примітка під 1982
    f.append(text(790, by + 18, "сусідня гілка — інший рід збою",
                  size=12, color=AMBER, italic=True))

    render(os.path.join(IMG, "generals-lineage.svg"), W, H, *f,
           title="Родовід: спершу доведення, потім — гучне ім'я")


# ═════════ Фігури до вставки «Робочий прогін невідання» (proj-indeterminacy) ═════════

# ───────── Прог. 1: три світи, один таймаут — і лічильник, що каже правду ─────────
def fig_indeterminacy_run():
    W, H = 1040, 384
    f = []

    # межі п'яти колонок
    cols = [30, 280, 490, 650, 800, 1010]
    xw = [(cols[i], cols[i + 1] - cols[i]) for i in range(5)]
    headers = ["Сценарій", "Що зробив канал", "Клієнт бачить",
               "Реле смикнулось", "Наївний повтор"]
    yh, hh = 60, 46
    for (x, w), htxt in zip(xw, headers):
        f.append(fitbox(x, yh, w, hh, htxt, size=13, fill=FILL,
                        stroke=INK, color=INK, bold=True, sw=1.6))

    rows = [
        ("(1) запит зник\nдорогою туди", "хаб не бачив\nкоманди", "таймаут", "0",
         ("безпечний", NEG, "#eaf0fd", NEG)),
        ("(2) підтвердження\nзникло назад", "хаб ВИКОНАВ\nефект", "таймаут", "1",
         ("ЗАДВОЇТЬ", POS, "#fdecea", POS)),
        ("(3) запит повзе —\nне дочекались", "виконає, але\nвже пізно", "таймаут", "1",
         ("гонка", AMBER, AMBERBG, AMBERST)),
    ]
    ry, rh = 106, 58
    for i, (scn, ch, cli, rel, (ptxt, pcol, pfill, pstroke)) in enumerate(rows):
        y = ry + i * rh
        f.append(fitbox(xw[0][0], y, xw[0][1], rh, scn, size=12,
                        fill=BG, stroke=MUTED, color=INK, bold=True))
        f.append(fitbox(xw[1][0], y, xw[1][1], rh, ch, size=12,
                        fill=BG, stroke=MUTED, color=MUTED))
        # «Клієнт бачить» — усі три однакові: спільний бурштиновий тон
        f.append(fitbox(xw[2][0], y, xw[2][1], rh, cli, size=13,
                        fill=AMBERBG, stroke=AMBERST, color=INK, bold=True))
        # «Реле» — 0 синій/безпечно, 1 червоний/ефект стався
        rc = (NEG, "#eaf0fd") if rel == "0" else (POS, "#fdecea")
        f.append(fitbox(xw[3][0], y, xw[3][1], rh, rel, size=19,
                        fill=rc[1], stroke=rc[0], color=rc[0], bold=True))
        f.append(fitbox(xw[4][0], y, xw[4][1], rh, ptxt, size=13,
                        fill=pfill, stroke=pstroke, color=pcol, bold=True))

    f.append(fitbox(30, 302, 980, 46,
                    "Клієнт бачить ОДНЕ й те саме. Лічильник на хабі каже РІЗНЕ.",
                    size=15, fill=FILL, stroke=INK, color=INK, bold=True, sw=2))

    render(os.path.join(IMG, "indeterminacy-run.svg"), W, H, *f,
           title="Один прогін: три світи за однією тишею")


# ───────── Прог. 2: наївний повтор задвоює — ключ відсікає дубль ─────────
def fig_retry_double_vs_key():
    W, H = 1040, 470
    f = []
    f.append(line(520, 58, 520, 452, color="#e5e7eb", sw=1))

    def panel(x0, cx, heading, hcolor, rows, banner, bcol, bfill, bstroke):
        g = [text(cx, 74, heading, size=15, bold=True, color=hcolor)]
        ys = [92, 142, 192, 242, 292, 342]
        for (txt, col, fill, stroke), y in zip(rows, ys):
            g.append(fitbox(x0, y, 430, 42, txt, size=12,
                            fill=fill, stroke=stroke, color=col, bold=True, sw=1.6))
        g.append(fitbox(x0, 402, 430, 46, banner, size=15,
                        fill=bfill, stroke=bstroke, color=bcol, bold=True, sw=2))
        return g

    naive = [
        ("спроба 1  →  хаб: unlock", INK, BG, MUTED),
        ("хаб: реле +1   ·   лічильник = 1", POS, "#fdecea", POS),
        ("ack загубився  →  клієнт: таймаут", INK, AMBERBG, AMBERST),
        ("спроба 2  →  хаб: unlock (наосліп)", INK, BG, MUTED),
        ("хаб: реле +1 ЗНОВУ   ·   лічильник = 2", POS, "#fdecea", POS),
        ("ack ok  →  клієнт: успіх", INK, "#eafaf0", FIELD),
    ]
    key = [
        ("спроба 1  →  хаб: unlock  [ключ K]", INK, BG, MUTED),
        ("хаб: реле +1 · лічильник = 1 · запам'ятав K", FIELD, "#eafaf0", FIELD),
        ("ack загубився  →  клієнт: таймаут", INK, AMBERBG, AMBERST),
        ("спроба 2  →  хаб: unlock  [той самий K]", INK, BG, MUTED),
        ("хаб: K вже бачив → ДУБЛЬ, реле не чіпаю · = 1", FIELD, "#eafaf0", FIELD),
        ("ack ok  →  клієнт: успіх", INK, "#eafaf0", FIELD),
    ]
    f += panel(50, 265, "Наївний повтор — без ключа", POS, naive,
               "лічильник = 2   —   ефект ЗАДВОЄНО", POS, "#fdecea", POS)
    f += panel(560, 775, "З ключем на команді", FIELD, key,
               "лічильник = 1   —   ключ відсік дубль", FIELD, "#eafaf0", FIELD)

    render(os.path.join(IMG, "retry-double-vs-key.svg"), W, H, *f,
           title="Той самий збій: наївний повтор двоїть, ключ — ні")


# ───────── Прог. 3: побічний ефект ПЕРЕД фіксацією ключа ─────────
def fig_commit_window():
    W, H = 940, 322
    f = []

    # ── верхній рядок: небезпечно ──
    f.append(text(40, 56, "Небезпечно: ефект ПЕРЕД записом ключа",
                  size=14, bold=True, color=POS, anchor="start"))
    y1 = 72
    f.append(fitbox(40, y1, 180, 52, "① прийняв\nunlock [K]", size=12,
                    fill=BG, stroke=MUTED, color=INK, bold=True))
    f.append(arrow(220, y1 + 26, 248, y1 + 26, color=INK, sw=1.8))
    f.append(fitbox(250, y1, 220, 52, "② смикнув реле\n← ЕФЕКТ стався", size=12,
                    fill="#fdecea", stroke=POS, color=POS, bold=True))
    f.append(fitbox(500, y1, 120, 52, "вікно\nпадіння", size=12,
                    fill="#fdecea", stroke=POS, color=POS, bold=True, sw=2.2))
    f.append(arrow(650, y1 + 26, 678, y1 + 26, color=INK, sw=1.8))
    f.append(fitbox(680, y1, 190, 52, "③ записав\nключ K", size=12,
                    fill=BG, stroke=MUTED, color=INK, bold=True))
    f.append(mtext(455, 150,
                   ["Падіння у вікні: реле вже смикнуло, а ключ K ще не записано —",
                    "повтор не бачить K і смикає реле ВДРУГЕ."],
                   size=12, color=POS, bold=True))

    f.append(line(30, 172, 910, 172, color="#e5e7eb", sw=1))

    # ── нижній рядок: безпечно ──
    f.append(text(40, 198, "Безпечно: перевірка + запис ключа + ефект — ОДНЕ ціле",
                  size=14, bold=True, color=FIELD, anchor="start"))
    y2 = 214
    f.append(fitbox(40, y2, 180, 52, "① прийняв\nunlock [K]", size=12,
                    fill=BG, stroke=MUTED, color=INK, bold=True))
    f.append(arrow(220, y2 + 26, 248, y2 + 26, color=INK, sw=1.8))
    f.append(fitbox(250, y2, 440, 52, "② ключ новий? → запис K → реле\nОДНА транзакція — неподільно",
                    size=12, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True, sw=2))
    f.append(arrow(690, y2 + 26, 718, y2 + 26, color=INK, sw=1.8))
    f.append(fitbox(720, y2, 180, 52, "③ готово", size=13,
                    fill=BG, stroke=MUTED, color=INK, bold=True))
    f.append(mtext(470, 294,
                   ["Падіння — або до транзакції, або після; проміжного стану нема.",
                    "Повтор бачить K → реле спрацьовує рівно раз."],
                   size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "commit-window.svg"), W, H, *f,
           title="Пастка: побічний ефект ПЕРЕД фіксацією ключа")


if __name__ == "__main__":
    fig_partial_state()
    fig_lost_ack()
    fig_three_outcomes()
    fig_ack_regress()
    fig_generals_lineage()
    fig_indeterminacy_run()
    fig_retry_double_vs_key()
    fig_commit_window()
    print("OK: partial-state.svg, lost-ack.svg, three-outcomes.svg, "
          "ack-regress.svg, generals-lineage.svg, "
          "indeterminacy-run.svg, retry-double-vs-key.svg, commit-window.svg")
