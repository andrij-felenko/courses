# -*- coding: utf-8 -*-
"""Фігури теми «Власні MAVLink-повідомлення в застосунку»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def tb(cx, cy, s, size=13, pad=12, **kw):
    """textbox, що повертає лише фрагмент."""
    body, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return body


def dashrect(x, y, w, h, color=MUTED, sw=1.4, dash="7,5"):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" '
            'fill="none" stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>'
            % (x, y, w, h, color, sw, dash))


# ── 1. Мовчазна смерть кадру з невідомим номером ────────────────────────────
def fig_silent_drop():
    W, H = 900, 620
    f = []
    f.append(tb(450, 92, "Порція байтів із каналу"))
    f.append(arrow(450, 122, 450, 158))
    f.append(tb(450, 188, "mavlink_parse_char — байт за байтом"))
    f.append(arrow(450, 218, 450, 254))
    f.append(tb(450, 292, ["mavlink_get_msg_entry(msgid)", "пошук опису за номером"]))

    f.append(arrow(430, 330, 250, 384))
    f.append(arrow(470, 330, 650, 384))
    f.append(text(140, 366, "номер відомий", size=12, color=MUTED))
    f.append(text(790, 366, "номер невідомий", size=12, color=MUTED))

    f.append(tb(225, 414, "запис у таблиці є", stroke=FIELD))
    f.append(tb(675, 414, "повернено NULL", stroke=POS))
    f.append(arrow(225, 444, 225, 486))
    f.append(arrow(675, 444, 675, 486))

    f.append(tb(225, 528, ["сума звіряється з CRC_EXTRA", "FRAMING_OK → у застосунок"],
                stroke=FIELD))
    f.append(tb(675, 528, ["FRAMING_BAD_CRC", "лічильник утрат +1, кадр зник"],
                stroke=POS))
    return render(os.path.join(OUT, 'silent-drop.svg'), W, H, *f,
                  title="Невідомий номер повідомлення = «погана сума»")


# ── 2. Порядок полів і межа відбитка ────────────────────────────────────────
def fig_field_order():
    W, H = 1060, 620
    f = []
    LX, RX, BW, BH = 110, 600, 270, 44
    ys = [96, 148, 200, 252, 304, 356]

    f.append(text(245, 74, "Порядок у XML", size=15, bold=True))
    f.append(text(735, 74, "Порядок у кадрі", size=15, bold=True))

    xml_rows = ["beacon_id — uint16_t (2 Б)",
                "range_m — float (4 Б)",
                "quality — uint8_t (1 Б)",
                "time_usec — uint64_t (8 Б)",
                "target_system — uint8_t (1 Б)",
                "target_component — uint8_t (1 Б)"]
    wire_rows = ["time_usec — 8 Б",
                 "range_m — 4 Б",
                 "beacon_id — 2 Б",
                 "quality — 1 Б",
                 "target_system — 1 Б",
                 "target_component — 1 Б"]

    for y, s in zip(ys, xml_rows):
        f.append(fitbox(LX, y, BW, BH, s, size=13))
    for y, s in zip(ys, wire_rows):
        f.append(fitbox(RX, y, BW, BH, s, size=13))

    f.append(dashrect(RX - 14, ys[0] - 14, BW + 28, ys[-1] + BH + 14 - (ys[0] - 14)))
    f.append(text(735, 434, "усе це входить у CRC_EXTRA", size=13, color=MUTED))

    f.append(arrow(400, 250, 570, 250))
    f.append(mtext(485, 210, ["mavgen сортує", "за спаданням розміру"],
                   size=12, color=MUTED))

    f.append(line(96, 468, 884, 468, color=MUTED, dash="6,5"))
    f.append(text(485, 460, "<extensions/>", size=13, color=MUTED))

    f.append(fitbox(LX, 494, BW, BH, "bearing_deg — float (4 Б)", size=13, stroke=NEG))
    f.append(fitbox(RX, 494, BW, BH, "bearing_deg — 4 Б", size=13, stroke=NEG))
    f.append(text(735, 578, "поза відбитком, у самому кінці кадру", size=13, color=MUTED))
    return render(os.path.join(OUT, 'field-order.svg'), W, H, *f,
                  title="Поля переставляє генератор; мітка ділить повідомлення надвоє")


# ── 3. Один опис — дві збірки ───────────────────────────────────────────────
def fig_one_xml():
    W, H = 1020, 580
    f = []
    f.append(tb(510, 96, ["perimeter.xml", "<include>all.xml</include>"], stroke=FIELD))
    f.append(arrow(440, 130, 270, 186))
    f.append(arrow(580, 130, 750, 186))

    f.append(tb(255, 216, "mavgen у збірці прошивки"))
    f.append(tb(765, 216, "mavgen у збірці станції"))
    f.append(arrow(255, 246, 255, 292))
    f.append(arrow(765, 246, 765, 292))

    f.append(tb(255, 328, ["заголовки прошивки", "CRC_EXTRA = k"]))
    f.append(tb(765, 328, ["заголовки станції", "CRC_EXTRA = k′"]))

    f.append(arrow(255, 372, 400, 428))
    f.append(arrow(765, 372, 620, 428))
    f.append(tb(510, 462, ["кадр у ефірі: суму пораховано з k,", "перевірено з k′"]))

    f.append(text(255, 546, "k = k′ → кадр прийнято", size=14, color=FIELD, bold=True))
    f.append(text(765, 546, "k ≠ k′ → «погана сума»", size=14, color=POS, bold=True))
    return render(os.path.join(OUT, 'one-xml-two-builds.svg'), W, H, *f,
                  title="Опис один, збірок кілька — звіряються не версії, а байт")


# ── 4. Хто в застосунку підхоплює власне повідомлення ───────────────────────
def fig_consumers():
    W, H = 1060, 500
    f = []
    f.append(tb(530, 92, "Цілий кадр із вашим номером повідомлення", stroke=FIELD))
    f.append(arrow(430, 124, 190, 184))
    f.append(arrow(530, 124, 530, 184))
    f.append(arrow(630, 124, 870, 184))

    f.append(tb(185, 218, ["Інспектор MAVLink", "без жодного коду"]))
    f.append(tb(530, 218, ["QGCCorePlugin::mavlinkMessage", "у вендорській збірці"]))
    f.append(tb(875, 218, ["Своя група фактів", "і прив'язка в інтерфейсі"]))

    f.append(mtext(185, 300, ["читає поля з таблиці описів", "(MAVLINK_USE_MESSAGE_INFO)"],
                   size=12, color=MUTED))
    f.append(mtext(530, 300, ["файли апстриму", "не змінено жодного"],
                   size=12, color=MUTED))
    f.append(mtext(875, 300, ["величина стає такою самою,", "як висота чи напруга"],
                   size=12, color=MUTED))

    f.append(line(80, 372, 980, 372, color=MUTED, dash="6,5"))
    f.append(tb(530, 428, "Правка Vehicle.cc — лише разом із відправкою в апстрим",
                stroke=MUTED, color=MUTED))
    return render(os.path.join(OUT, 'consumers.svg'), W, H, *f,
                  title="Три споживачі власного повідомлення, і один із них безкоштовний")


# ── 5. Доля атрибутів <field> у C-заголовку (вставка api-dialect-xml) ───────
def fig_attr_fate():
    W, H = 1160, 590
    f = []
    LX, LW = 70, 350
    RX, RW = 640, 460

    f.append(text(LX + LW / 2, 72, "Написано в описі", size=14,
                  bold=True, color=MUTED))
    f.append(text(RX + RW / 2, 72, "Видно в згенерованому заголовку", size=14,
                  bold=True, color=MUTED))

    rows = [
        (92, 78, ["type · name"],
         ["член структури, зсув у кадрі, MAVLINK_TYPE_*,",
          "аргументи _pack і назви геттерів,",
          "і — головне — байт CRC_EXTRA"], FIELD),
        (196, 62, ["print_format"],
         ["рядок формату в MAVLINK_MESSAGE_INFO;",
          "без атрибута там стоїть NULL"], LINE),
        (286, 62, ["units"],
         ["коментар біля члена структури",
          "й @param у doxygen — і більше нічого"], LINE),
        (376, 150, ["enum · display · instance",
                    "invalid · multiplier · default",
                    "minValue · maxValue · increment"],
         ["у C-заголовку немає жодного сліду;",
          "їх читають генератор документації,",
          "генератори інших мов і наземні станції"], MUTED),
    ]

    for y, h, left, right, col in rows:
        txt = MUTED if col is MUTED else INK
        f.append(fitbox(LX, y, LW, h, left, size=15, stroke=col, color=txt))
        f.append(arrow(LX + LW + 6, y + h / 2, RX - 6, y + h / 2, color=col))
        f.append(fitbox(RX, y, RW, h, right, size=14, stroke=col, color=txt))

    return render(os.path.join(OUT, 'attr-fate.svg'), W, H, *f,
                  title="Опис багатший за заголовок: більшість атрибутів у C не доходить")


# ── 6. Драбина перевірок наскрізного проєкту (вставка proj-custom-message) ──
def fig_checkpoints():
    W, H = 1140, 570
    f = []
    C1X, C1W = 40, 286
    C2X, C2W = 344, 320
    C3X, C3W = 682, 418
    BH = 72
    ys = [100 + i * 86 for i in range(5)]

    f.append(text(C1X + C1W / 2, 80, "Крок", size=14, bold=True, color=MUTED))
    f.append(text(C2X + C2W / 2, 80, "Чим перевірити", size=14, bold=True, color=MUTED))
    f.append(text(C3X + C3W / 2, 80, "Що бачите, якщо крок не спрацював",
                  size=14, bold=True, color=MUTED))

    rows = [
        (["1. Опис у діалекті"],
         ["mavgen руками,", "без збірки станції"],
         ["генератор лається на XML —", "єдина гучна помилка на шляху"]),
        (["2. Станція зібрана", "з вашим діалектом"],
         ["три сталі згенерованого", "заголовка з обох боків"],
         ["сталі різні: кадр гинутиме", "як «погана сума»"]),
        (["3. Кадр доходить у ефірі"],
         ["інспектор MAVLink,", "жодного рядка коду"],
         ["повідомлення немає в списку,", "росте лічильник утрат"]),
        (["4. Розбір і факт"],
         ["показник на екрані", "проти інспектора"],
         ["інспектор показує, екран — ні:", "гачок не викликано"]),
        (["5. Кнопка й частота"],
         ["значення, що повернула", "відправка, і відгук борту"],
         ["відправка вернула «ні»:", "основного каналу вже немає"]),
    ]

    for y, (a, b, c) in zip(ys, rows):
        f.append(fitbox(C1X, y, C1W, BH, a, size=13, stroke=FIELD))
        f.append(fitbox(C2X, y, C2W, BH, b, size=13))
        f.append(fitbox(C3X, y, C3W, BH, c, size=13, stroke=POS))
        f.append(arrow(C1X + C1W + 8, y + BH / 2, C2X - 8, y + BH / 2))

    return render(os.path.join(OUT, 'checkpoints.svg'), W, H, *f,
                  title="Після кожного кроку — своя перевірка: протокол діагностики не дає")


if __name__ == '__main__':
    fig_silent_drop()
    fig_field_order()
    fig_one_xml()
    fig_consumers()
    fig_attr_fate()
    fig_checkpoints()
    print("ok")


# ── Крок суми: звідки беруться зсуви (вставка math-crc-extra) ───────────────
def fig_crc_step():
    W, H = 1040, 512
    f = []
    x0, cw, cy, ch = 80, 52, 78, 46
    taps = {15, 10, 3}

    f.append(text(W / 2, 60,
                  "16-бітний регістр і номери бітів; червоні — біти многочлена P = 0x8408",
                  size=13, color=MUTED))
    for i in range(16):
        b = 15 - i
        x = x0 + i * cw
        f.append(rect(x, cy, cw - 6, ch,
                      fill="#fdecea" if b in taps else FILL,
                      stroke=POS if b in taps else LINE, sw=1.5, rx=4))
        f.append(text(x + (cw - 6) / 2, cy + ch / 2 + 5, str(b), size=12,
                      color=POS if b in taps else INK, bold=(b in taps)))

    bx3 = x0 + 12 * cw + (cw - 6) / 2
    bx0 = x0 + 15 * cw + (cw - 6) / 2
    f.append(line(bx3, cy + ch, bx3, 160))
    f.append(line(bx3, 160, bx0, 160))
    f.append(arrow(bx0, 160, bx0, cy + ch + 3))
    f.append(text(390, 155, "біт 3 доходить до позиції 0 — його бачить крок j + 4",
                  size=13, color=MUTED))

    f.append(text(W / 2, 200,
                  "тому маска спрацювань u = t ^ (t << 4), де t = байт ^ (crc & 0xFF)",
                  size=14, bold=True))

    rows = ["біт 15 многочлена після (7 − j) зсувів опиняється на позиції 8 + j   ⇒   доданок u << 8",
            "біт 10 многочлена опиняється на позиції 3 + j   ⇒   доданок u << 3",
            "біт 3 многочлена опиняється на позиції j − 4, тільки для j ≥ 4   ⇒   доданок u >> 4"]
    for k, s in enumerate(rows):
        f.append(fitbox(90, 224 + k * 58, 860, 48, s, size=13))

    f.append(fitbox(90, 408, 860, 74,
                    ["старший байт просто зсувається вниз, решта — три доданки:",
                     "crc ← (crc >> 8) ^ (u << 8) ^ (u << 3) ^ (u >> 4)"],
                    size=14, stroke=FIELD))
    return render(os.path.join(OUT, 'crc-step.svg'), W, H, *f,
                  title="Один байт у суму: звідки беруться всі зсуви")


# ── Згортання й сліпа пляма (вставка math-crc-extra) ────────────────────────
def fig_crc_fold():
    W, H = 1000, 500
    f = []
    f.append(tb(250, 94, ["опис із полем quality", "CRC-16 = 0x098A"]))
    f.append(tb(750, 94, ["опис із полем quarity", "CRC-16 = 0x20A3"]))
    f.append(arrow(250, 124, 250, 166))
    f.append(arrow(750, 124, 750, 166))

    f.append(tb(250, 196, ["згортання половин", "0x8A ^ 0x09"]))
    f.append(tb(750, 196, ["згортання половин", "0xA3 ^ 0x20"]))
    f.append(arrow(250, 228, 430, 278))
    f.append(arrow(750, 228, 570, 278))

    f.append(tb(500, 306, "CRC_EXTRA = 0x83 = 131 — в обох", stroke=POS))
    f.append(arrow(500, 328, 500, 352))
    f.append(tb(500, 382, ["Δ = 0x098A ^ 0x20A3 = 0x2929",
                           "старший байт дорівнює молодшому — згортання їх знищує"],
               stroke=MUTED, color=MUTED))
    f.append(text(500, 456,
                  "таких ненульових Δ рівно 255 із 65535; у кожного байта рівно 256 прообразів",
                  size=13, color=MUTED))
    return render(os.path.join(OUT, 'crc-fold.svg'), W, H, *f,
                  title="Де саме зникає різниця між двома описами")


if __name__ == '__main__':
    fig_crc_step()
    fig_crc_fold()
    print("ok math-crc-extra")
