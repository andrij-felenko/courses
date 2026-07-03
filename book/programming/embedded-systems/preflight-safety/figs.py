# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Безпека до польоту» (preflight-safety).
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: асиметрія наслідків — той самий збій на землі й у повітрі ───────
# Ідея: та сама несправність коштує повідомлення на землі й катастрофи в небі;
# тому найдешевше місце спіймати збій — до відриву.
def fig_ground_vs_air():
    W, H = 1000, 380
    P = [text(W / 2, 30, "Той самий збій: ціна на землі й у повітрі", size=17, bold=True)]

    # горизонтальна вісь-межа: землю від неба ділить момент відриву
    gy = 200
    P.append(line(40, gy, W - 40, gy, color="#c9ccd1", sw=1.4, dash="6 5"))
    P.append(text(W / 2, gy - 8, "МОМЕНТ ВІДРИВУ (arming → політ)", size=12,
                  color=MUTED, bold=True))
    P.append(text(64, gy - 44, "НА ЗЕМЛІ", size=13, color=FIELD, bold=True, anchor="start"))
    P.append(text(64, gy + 56, "У ПОВІТРІ", size=13, color=POS, bold=True, anchor="start"))

    rows = [
        ("Компас бреше 40°", "«перевір компас»", "відхід з курсу"),
        ("Немає GPS-фіксації", "не даємо злетіти", "дрейф, втрата"),
        ("Батарея напівсіла", "заряди й спробуй", "падіння в дорозі"),
    ]
    x0 = 330
    dx = 265
    for i, (fault, ground, air) in enumerate(rows):
        cx = x0 + i * dx
        # сам збій — по центру межі
        fr, w, h = textbox(cx, gy, fault, size=11, bold=True,
                           fill="#eef2f7", stroke=INK, min_w=190)
        P.append(fr)
        # наслідок на землі (вгору, зелений — керовано)
        fr, w, h = textbox(cx, gy - 78, ground, size=11, color=FIELD, bold=True,
                           fill="#e9f7ef", stroke=FIELD, min_w=190)
        P.append(fr)
        P.append(arrow(cx, gy - 20, cx, gy - 78 + 26, color=FIELD, sw=1.5))
        # наслідок у повітрі (вниз, червоний — катастрофа)
        fr, w, h = textbox(cx, gy + 90, air, size=11, color=POS, bold=True,
                           fill="#fdecea", stroke=POS, min_w=190)
        P.append(fr)
        P.append(arrow(cx, gy + 20, cx, gy + 90 - 26, color=POS, sw=1.5))

    render("img/ground-vs-air.svg", W, H, *P)


# ── Фігура 2: шлюз arming — дві застави між «зібрано» і «летить» ──────────────
# Ідея: єдиний охоронюваний перехід disarmed→armed стереже дві застави:
# пройдено передпольотні перевірки І людина свідомо попросила.
def fig_arming_gate():
    W, H = 940, 340
    P = [text(W / 2, 30, "Шлюз arming: два замки між «зібрано» і «летить»", size=17, bold=True)]

    cy = 185
    # стан «обеззброєно» (ліворуч)
    fr, w, h = textbox(150, cy, "DISARMED\n(двигуни не крутяться\nза жодних команд)",
                       size=12.5, bold=True, color=FIELD, fill="#e9f7ef",
                       stroke=FIELD, min_w=230)
    P.append(fr)
    # стан «озброєно» (праворуч)
    fr, w, h = textbox(W - 150, cy, "ARMED\n(двигуни живі,\nапарат може злетіти)",
                       size=12.5, bold=True, color=POS, fill="#fdecea",
                       stroke=POS, min_w=230)
    P.append(fr)

    # дві застави посередині
    g1x, g2x = 430, 590
    for gx, top, bot, col, fill in [
        (g1x, "ЗАСТАВА 1", "передпольотні\nперевірки\nпройдено", NEG, "#eaf0fd"),
        (g2x, "ЗАСТАВА 2", "людина свідомо\nвіддала команду\narm", "#b08900", "#fdf6e3"),
    ]:
        P.append(text(gx, 78, top, size=12, color=col, bold=True))
        fr, w, h = textbox(gx, cy, bot, size=11, bold=True, color=col,
                           fill=fill, stroke=col, min_w=130)
        P.append(fr)

    # стрілка проходу зліва направо крізь застави
    P.append(arrow(270, cy, g1x - 68, cy, color=MUTED, sw=1.7))
    P.append(arrow(g1x + 68, cy, g2x - 68, cy, color=MUTED, sw=1.7))
    P.append(arrow(g2x + 68, cy, W - 270, cy, color=MUTED, sw=1.7))
    P.append(text((g1x + g2x) / 2, cy + 92, "хоч одна не виконана → лишаємось DISARMED",
                  size=12, color=INK, bold=True))

    render("img/arming-gate.svg", W, H, *P)


# ── Фігура 3: передпольотна перевірка = «підтверди припущення, яким довіриш» ──
# Ідея: кожна перевірка звіряє те, що політний код потім МОВЧКИ вважатиме
# правдою; на землі відмова = «ні», у польоті — сліпа довіра до брехні.
def fig_prearm_table():
    W, H = 960, 470
    P = [text(W / 2, 30, "Передпольотна перевірка звіряє те, чому політ довіриться",
              size=16.5, bold=True)]

    col_chk = 210
    col_ass = W - 250
    head_y = 72
    P.append(text(col_chk, head_y, "ПЕРЕВІРКА", size=13, bold=True, color=INK))
    P.append(text(col_ass, head_y, "ПРИПУЩЕННЯ, ЯКЕ ВОНА ЗАХИЩАЄ", size=13,
                  bold=True, color=NEG))
    P.append(line(60, head_y + 12, W - 60, head_y + 12, color="#d0d5dd", sw=1.2))

    rows = [
        ("Калібрування компаса", "«північ там, куди він показує»"),
        ("Згода давачів між собою", "«обидва компаси не можуть брехати однаково»"),
        ("Фіксація GPS і точність", "«координата, за якою полечу, справжня»"),
        ("Оцінка стану збіглася (EKF)", "«я знаю, де я і як стою»"),
        ("Заряд вистачить на місію", "«двигуни не заглухнуть у повітрі»"),
        ("Зв'язок і failsafe готові", "«буде кому наказати й буде куди впасти»"),
    ]
    y0 = head_y + 46
    dy = 60
    for i, (chk, ass) in enumerate(rows):
        y = y0 + i * dy
        fr, w, h = textbox(col_chk, y, chk, size=12, bold=True,
                           fill="#eef2f7", stroke=INK, min_w=260)
        P.append(fr)
        fr, w, h = textbox(col_ass, y, ass, size=12, color=NEG,
                           fill="#eaf0fd", stroke=NEG, min_w=340)
        P.append(fr)
        P.append(arrow(col_chk + 135, y, col_ass - 175, y, color=MUTED))

    render("img/prearm-table.svg", W, H, *P)


# ── Фігура 4 (вставка hist): тяглість safe-and-arm — розрив джерело→ініціатор ──
# Ідея: той самий візерунок «розрив у SAFE, з'єднання в ARM» в ордонансі й у дроні.
def fig_safe_arm_lineage():
    W, H = 1000, 540
    P = [text(W / 2, 30, "Розрив, що рятує: той самий візерунок в ордонансі й у дроні",
              size=16, bold=True)]

    # спільний рушій одного «поверху»: джерело → [розрив/замок] → приймач
    def row(cy, src, sink, connected, src_fill, sink_fill, note):
        xs, xg, xk = 150, 500, 810          # джерело · середина(розрив) · приймач
        # джерело
        fr, w, h = textbox(xs, cy, src, size=12, bold=True, fill=src_fill,
                           stroke=INK, min_w=150)
        P.append(fr)
        # приймач
        fr2, w2, h2 = textbox(xk, cy, sink, size=12, bold=True, fill=sink_fill,
                              stroke=INK, min_w=150)
        P.append(fr2)
        # провід джерело→розрив
        P.append(line(xs + w / 2, cy, xg - 34, cy, color=INK, sw=2.4))
        if connected:
            # ARM: контакт замкнено — суцільний провід крізь замок до приймача
            P.append(line(xg - 34, cy, xg + 34, cy, color=FIELD, sw=3.2))
            P.append(line(xg + 34, cy, xk - w2 / 2, cy, color=INK, sw=2.4))
            P.append(circle(xg - 34, cy, 4, fill=INK, stroke=INK))
            P.append(circle(xg + 34, cy, 4, fill=INK, stroke=INK))
            # ярлик стану — трохи НИЖЧЕ дроту (там порожньо, не б'ється з шапками)
            P.append(text(xg, cy + 22, "ЗАМКНЕНО", size=11, color=FIELD, bold=True))
        else:
            # SAFE: фізичний розрив — контакти є, дроту між ними немає
            P.append(circle(xg - 34, cy, 4, fill=BG, stroke=INK, sw=2))
            P.append(circle(xg + 34, cy, 4, fill=BG, stroke=INK, sw=2))
            # відсунутий «рубильник» — розімкнений
            P.append(line(xg - 34, cy, xg - 4, cy - 24, color=POS, sw=3))
            P.append(line(xg + 34, cy, xk - w2 / 2, cy, color="#c9ccd1", sw=2.4,
                          dash="5 5"))
            P.append(text(xg + 4, cy + 22, "РОЗРИВ", size=11, color=POS, bold=True))
        # підпис-нотатка — під приймачем, щоб не вилазив за правий край
        P.append(text(xk, cy + h2 / 2 + 16, note, size=10, color=MUTED))

    # ── ЗВЕРХУ по вертикалі: два стани ордонансного safe-and-arm ──
    P.append(text(W / 2, 62, "ОРДОНАНС · safe-and-arm device", size=13,
                  color=MUTED, bold=True))
    row(120, "джерело\nструму", "запал\n(ініціатор)", False,
        "#eaf0fd", "#fdecea", "SAFE: струм нікуди не тече")
    row(212, "джерело\nструму", "запал\n(ініціатор)", True,
        "#eaf0fd", "#fdecea", "ARM: розрив свідомо знято")

    # роздільник епох
    P.append(line(60, 292, W - 60, 292, color="#c9ccd1", sw=1.3, dash="7 6"))
    P.append(text(W / 2, 285, "століття по тому — той самий інваріант", size=11,
                  color=MUTED, italic=True))

    # ── ЗНИЗУ по вертикалі: два стани дрона ──
    P.append(text(W / 2, 330, "ДРОН · логіка arming у прошивці", size=13,
                  color=MUTED, bold=True))
    row(390, "батарея\n+ команда газу", "двигуни\n(гвинти)", False,
        "#eaf0fd", "#eef7ee", "disarmed: сигнал не доходить")
    row(482, "батарея\n+ команда газу", "двигуни\n(гвинти)", True,
        "#eaf0fd", "#eef7ee", "armed: розрив знято свідомо")

    render("img/safe-arm-lineage.svg", W, H, *P)


if __name__ == "__main__":
    fig_ground_vs_air()
    fig_arming_gate()
    fig_prearm_table()
    fig_safe_arm_lineage()
    print("OK: 4 figures -> img/")
