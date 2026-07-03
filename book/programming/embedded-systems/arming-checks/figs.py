# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Arming-перевірки».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: ворота між DISARMED і ARMED ────────────────────────────────────
# Ідея: arming — керовані ворота. Двигуни можуть крутитися ЛИШЕ праворуч від межі,
# а перейти межу дозволено тільки коли ВСІ перевірки зелені + свідома команда.
def fig_gate():
    W, H = 940, 430
    P = []
    P.append(text(W / 2, 30, "Arming — ворота до обертання двигунів", size=17, bold=True))

    midx = W / 2
    # вертикальна межа-«ворота»
    P.append(line(midx, 70, midx, H - 60, color=POS, sw=3, dash="9 7"))

    # ЛІВОРУЧ — DISARMED
    fr, w, h = textbox(midx - 235, 120, "DISARMED\n(знеструмлено)",
                       size=15, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, min_w=250)
    P.append(fr)
    P.append(text(midx - 235, 185, "команда газу ІГНОРУЄТЬСЯ", size=12.5, color=MUTED))
    P.append(text(midx - 235, 208, "двигуни завжди стоять", size=12.5, color=MUTED))
    P.append(text(midx - 235, 231, "можна брати руками", size=12.5, color=MUTED))

    # ПРАВОРУЧ — ARMED
    fr, w, h = textbox(midx + 235, 120, "ARMED\n(під напругою)",
                       size=15, bold=True, color=POS, fill="#fdecea", stroke=POS, min_w=250)
    P.append(fr)
    P.append(text(midx + 235, 185, "газ КЕРУЄ двигунами", size=12.5, color=MUTED))
    P.append(text(midx + 235, 208, "гвинти можуть крутитися", size=12.5, color=MUTED))
    P.append(text(midx + 235, 231, "руки геть", size=12.5, color=MUTED))

    # умова переходу — над воротами
    fr, w, h = textbox(midx, 300,
                       "перейти можна ЛИШЕ коли:\nусі перевірки зелені  +  свідома команда ARM",
                       size=13, bold=True, color=FIELD, fill="#e9f7ef", stroke=FIELD, min_w=520)
    P.append(fr)

    # стрілка переходу
    P.append(arrow(midx - 120, 355, midx + 120, 355, color=INK, sw=2))
    P.append(text(midx, 385, "ARM", size=13, bold=True, color=INK))
    # і назад
    P.append(arrow(midx + 120, 405, midx - 120, 405, color=MUTED, sw=1.6))
    P.append(text(midx, 405 + 3, "  DISARM (будь-коли)", size=11.5, color=MUTED, anchor="start"))

    render("img/arming-gate.svg", W, H, *P)


# ── Фігура 2: пайплайн перевірок — прапорець-бітмаска → одна причина відмови ──
# Ідея: набір незалежних перевірок; кожну можна ввімкнути бітом; ARM проходить
# лише коли всі ввімкнені пройшли; інакше оператор бачить ПЕРШУ причину відмови.
def fig_check_pipeline():
    W, H = 960, 520
    P = []
    P.append(text(W / 2, 30, "Перевірки перед arming: біт → результат → причина", size=17, bold=True))

    colx = 250
    y0 = 78
    dy = 62
    checks = [
        ("датчики скалібровано", "OK",   True),
        ("EKF: оцінка стабільна", "OK",   True),
        ("GPS: фіксація й точність", "СТОП", False),
        ("радіозв'язок живий",   "OK",   True),
        ("заряд батареї в нормі", "OK",   True),
        ("апаратний перемикач знято", "OK", True),
    ]
    for i, (name, res, ok) in enumerate(checks):
        y = y0 + i * dy
        col = FIELD if ok else POS
        fill = "#e9f7ef" if ok else "#fdecea"
        # прапорець-біт
        fr, w, h = textbox(70, y, "біт %d" % i, size=11.5, bold=True,
                           color=NEG, fill="#eaf0fd", stroke=NEG, min_w=70)
        P.append(fr)
        # назва перевірки
        fr, w, h = textbox(colx, y, name, size=12, bold=True,
                           color=INK, fill=FILL, stroke=LINE, min_w=300)
        P.append(fr)
        # результат
        fr, w, h = textbox(colx + 300, y, res, size=12.5, bold=True,
                           color=col, fill=fill, stroke=col, min_w=90)
        P.append(fr)

    # вертикальний збір «І» праворуч
    andx = colx + 470
    P.append(line(colx + 350, y0, andx, y0, color=MUTED, sw=1.2))
    for i in range(len(checks)):
        y = y0 + i * dy
        P.append(line(colx + 350, y, andx, y, color=MUTED, sw=1.0))
    P.append(line(andx, y0, andx, y0 + (len(checks) - 1) * dy, color=INK, sw=2))
    P.append(text(andx + 18, (y0 + y0 + (len(checks) - 1) * dy) / 2 - 8,
                  "І", size=20, bold=True, color=INK, anchor="start"))
    P.append(text(andx + 18, (y0 + y0 + (len(checks) - 1) * dy) / 2 + 14,
                  "(всі)", size=11, color=MUTED, anchor="start"))

    # підсумок — ARM заблоковано
    fr, w, h = textbox(W / 2, H - 78,
                       "хоч один СТОП → ARM ЗАБЛОКОВАНО",
                       size=14, bold=True, color=POS, fill="#fdecea", stroke=POS, min_w=430)
    P.append(fr)
    fr, w, h = textbox(W / 2, H - 34,
                       "операторові показано ПЕРШУ причину:  \"PreArm: GPS: 3D fix required\"",
                       size=12.5, bold=True, color=INK, fill="#eef2f7", stroke=INK, min_w=640)
    P.append(fr)

    render("img/check-pipeline.svg", W, H, *P)


# ── Фігура 3: три ешелони блокування газу ────────────────────────────────────
# Ідея: команда газу мусить пройти три незалежні заслони, перш ніж дійти до
# двигунів. Кожен нижчий рівень надійніший (менше коду між ним і небезпекою).
def fig_layers():
    W, H = 900, 470
    P = []
    P.append(text(W / 2, 30, "Три заслони на шляху газу до двигунів", size=17, bold=True))

    cx = W / 2
    band = [
        ("КОМАНДА газу (пульт / місія)", "#eef2f7", INK, "джерело наміру"),
        ("логіка ARM у прошивці", "#e9f7ef", FIELD, "пропускає лише коли ARMED і перевірки пройшли"),
        ("апаратний запобіжник (safety switch)", "#fdf6e3", "#b08900", "фізичний перемикач: доки не знято — виходи заглушено"),
        ("вихід на регулятори (ESC)  →  ОБЕРТАННЯ", "#fdecea", POS, "остання ланка: сюди доходить лише дозволене"),
    ]
    y0 = 80
    bh = 74
    gap = 20
    for i, (label, fill, col, note) in enumerate(band):
        y = y0 + i * (bh + gap)
        P.append(fitbox(cx - 340, y, 680, bh, label, size=15, bold=True,
                        color=col, fill=fill, stroke=col))
        P.append(text(cx, y + bh + 13, note, size=11.5, color=MUTED))
        if i < len(band) - 1:
            P.append(arrow(cx, y + bh + gap - 6, cx, y + bh + gap + 4, color=INK, sw=2))

    render("img/arming-layers.svg", W, H, *P)


# ── Вставка comp-safety-switch ───────────────────────────────────────────────
# Ідея: перемикач сидить на окремій лінії до IO/FMU й керує «затвором» перед
# виходами PWM. Доки не натиснуто — виходи заглушено ПОВЗ програмну логіку.
def fig_switch_block():
    W, H = 960, 470
    P = []
    P.append(text(W / 2, 30, "Куди під'єднано перемикач і що він тримає", size=17, bold=True))

    # сам перемикач (кнопка + світлодіод) ліворуч
    bx, by = 150, 150
    P.append(fitbox(bx - 95, by - 55, 190, 110, "перемикач\nбезпеки\n(кнопка + LED)",
                    size=13, bold=True, color="#b08900", fill="#fdf6e3", stroke="#b08900"))
    P.append(text(bx, by + 92, "у руках оператора", size=11.5, color=MUTED))

    # лінія SAFETY_SW до IO/FMU
    iox = 520
    P.append(arrow(bx + 95, by - 20, iox - 150, by - 20, color=INK, sw=2))
    P.append(text((bx + 95 + iox - 150) / 2, by - 30, "лінія SAFETY_SW", size=12, bold=True, color=INK))
    P.append(text((bx + 95 + iox - 150) / 2, by - 10, "(натиснуто / ні)", size=11, color=MUTED))
    # лінія SAFETY_LED назад до світлодіода
    P.append(arrow(iox - 150, by + 20, bx + 95, by + 20, color=NEG, sw=2))
    P.append(text((bx + 95 + iox - 150) / 2, by + 40, "лінія LED (стан)", size=11.5, color=NEG))

    # IO-копроцесор — тримає затвор
    P.append(fitbox(iox - 150, by - 65, 300, 130,
                    "IO-копроцесор\n(окремий чип, керує виходами)",
                    size=13, bold=True, color=FIELD, fill="#e9f7ef", stroke=FIELD))
    # затвор
    P.append(text(iox, by + 92, "затвор PWM: доки перемикач не знято — ЗАКРИТО", size=11.5, color=POS))

    # виходи на ESC праворуч
    ex = 860
    P.append(arrow(iox + 150, by, ex - 70, by, color=INK, sw=2))
    P.append(fitbox(ex - 70, by - 45, 140, 90, "виходи PWM\n→ ESC → двигуни",
                    size=12.5, bold=True, color=POS, fill="#fdecea", stroke=POS))

    # нижній коментар — незалежність від коду FMU
    fr, w, h = textbox(W / 2, H - 70,
                       "перемикач ріже виходи в IO-чипі — ПОВЗ політний код (FMU)",
                       size=13, bold=True, color=INK, fill="#eef2f7", stroke=INK, min_w=640)
    P.append(fr)
    fr, w, h = textbox(W / 2, H - 28,
                       "навіть якщо головна прошивка збожеволіє — двигуни стоять, доки кнопку не знято",
                       size=12, color=MUTED, fill=BG, stroke=BG, min_w=10)
    P.append(fr)

    render("img/safety-switch-block.svg", W, H, *P)


# ── LED-стани перемикача: три чіткі візерунки ────────────────────────────────
def fig_switch_led():
    W, H = 900, 360
    P = []
    P.append(text(W / 2, 30, "Світлодіод перемикача — три стани, три візерунки", size=17, bold=True))

    rows = [
        ("часте блимання", "система ще піднімається (ініціалізація)", MUTED, "#eef2f7",
         [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]),
        ("рідкі спалахи", "готова, але ЗАБЛОКОВАНО — перемикач не знято", POS, "#fdecea",
         [1, 0, 0, 0, 0, 1, 0, 0, 0, 0]),
        ("світить рівно", "перемикач знято — виходам ДОЗВОЛЕНО рух", FIELD, "#e9f7ef",
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]),
    ]
    y0 = 90
    dy = 82
    x_pat = 470
    cell = 30
    for i, (name, note, col, fill, pat) in enumerate(rows):
        y = y0 + i * dy
        fr, w, h = textbox(160, y, name, size=14, bold=True, color=col, fill=fill, stroke=col, min_w=230)
        P.append(fr)
        P.append(text(160, y + 30, note, size=11, color=MUTED))
        # візерунок — квадратики (світиться/ні)
        for k, on in enumerate(pat):
            cx = x_pat + k * cell
            f = col if on else BG
            st = col if on else LINE
            P.append(rect(cx, y - cell / 2, cell - 5, cell, fill=f, stroke=st, sw=1.2, rx=3))
        P.append(text(x_pat + len(pat) * cell + 12, y + 4, "час →", size=11, color=MUTED, anchor="start"))

    render("img/safety-switch-led.svg", W, H, *P)


# ── Натиснути й утримати ~1 с: чому не короткий доторк ───────────────────────
def fig_hold_timing():
    W, H = 900, 300
    P = []
    P.append(text(W / 2, 30, "Зняти блокування: натиснути й утримати ~1 c", size=17, bold=True))

    # вісь часу
    ax0, ax1, ay = 90, 810, 150
    P.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    P.append(text(ax1, ay + 22, "час", size=12, color=MUTED, anchor="end"))

    # відрізок утримання
    hx0, hx1 = 260, 560
    P.append(rect(hx0, ay - 42, hx1 - hx0, 42, fill="#fdf6e3", stroke="#b08900", sw=1.6, rx=5))
    P.append(text((hx0 + hx1) / 2, ay - 15, "кнопка НАТИСНУТА", size=12.5, bold=True, color="#b08900"))
    P.append(text((hx0 + hx1) / 2, ay - 52, "≈ 1 c утримання", size=12, bold=True, color=INK))

    # момент спрацювання
    P.append(line(hx1, ay - 70, hx1, ay + 40, color=FIELD, sw=2, dash="5 4"))
    P.append(text(hx1, ay + 62, "ось тут стан перемкнувся", size=12, bold=True, color=FIELD))

    # короткий доторк — ліворуч, ігнорується
    tx0, tx1 = 130, 175
    P.append(rect(tx0, ay - 30, tx1 - tx0, 30, fill="#eef2f7", stroke=LINE, sw=1.2, rx=4))
    P.append(text((tx0 + tx1) / 2, ay + 46, "короткий доторк —\nпропущено", size=10.5, color=MUTED))

    fr, w, h = textbox(W / 2, H - 40,
                       "витримка відсіює випадковий доторк: перемкнути можна лише свідомо",
                       size=12.5, bold=True, color=INK, fill=BG, stroke=BG, min_w=10)
    P.append(fr)

    render("img/safety-switch-hold.svg", W, H, *P)


# ── Вставка hist-arming-interlocks: одна ідея крізь чотири століття ───────────
# Ідея: «фізичний бар'єр, який людина мусить свідомо зняти» повторюється в
# зброї, залізниці, пресах, транспорті — і врешті осідає у прошивці як `armed`.
def fig_hist_timeline():
    W, H = 960, 560
    P = []
    P.append(text(W / 2, 30, "Один принцип, шість втілень: запобіжник, який знімають свідомо",
                  size=16, bold=True))

    rows = [
        ("XVII ст.", "кремінний замок (half-cock, doglock)",
         "окремий бар'єр поверх заряду; знімається лише навмисним рухом", "#fdf6e3", "#b08900"),
        ("1856", "залізничний interlock (Дж. Саксбі)",
         "несумісні дії взаємно замкнені сталевими планками", "#eef2f7", NEG),
        ("XX ст.", "дворучний прес; блокування огорожі",
         "дозвіл лише через жест, несумісний із небезпекою", "#fdecea", POS),
        ("1915", "граната Міллза (чека + важіль)",
         "arm/disarm; зводити важко, знешкодити — легко", "#fdf6e3", "#b08900"),
        ("XX ст.", "рукоятка мерця (Ф. Спрейг, 1880-ті)",
         "безпека за замовчуванням: зникло керування — гальмуй сам", "#eef2f7", NEG),
        ("наші дні", "arming у прошивці дрона (armed)",
         "той самий бар'єр у коді + автоматична перевірка готовності", "#e9f7ef", FIELD),
    ]
    y0 = 78
    dy = 76
    datex = 70
    namex = 165
    for i, (date, name, note, fill, col) in enumerate(rows):
        y = y0 + i * dy
        # смуга-віха
        P.append(fitbox(namex, y - 26, 560, 52, name, size=14, bold=True,
                        color=col, fill=fill, stroke=col))
        # дата ліворуч
        P.append(text(datex, y - 2, date, size=13, bold=True, color=INK, anchor="middle"))
        # пояснення під смугою
        P.append(text(namex + 12, y + 40, note, size=11.5, color=MUTED, anchor="start"))
        # стрілка «успадковано далі»
        if i < len(rows) - 1:
            P.append(arrow(namex + 280, y + 26 + 6, namex + 280, y + dy - 26 - 6,
                           color=MUTED, sw=1.6))

    # підсумкова рамка праворуч від останньої віхи
    fr, w, h = textbox(namex + 280, H - 26,
                       "дрон не винайшов принцип — переніс його в код і додав перевірку готовності",
                       size=12.5, bold=True, color=INK, fill="#eef2f7", stroke=INK, min_w=640)
    P.append(fr)

    render("img/hist-timeline.svg", W, H, *P)


if __name__ == "__main__":
    fig_gate()
    fig_check_pipeline()
    fig_layers()
    fig_switch_block()
    fig_switch_led()
    fig_hold_timing()
    fig_hist_timeline()
    print("OK: 7 figures -> img/")
