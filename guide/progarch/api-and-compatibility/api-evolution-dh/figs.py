# -*- coding: utf-8 -*-
"""Фігури до кроку «Еволюція API DH без поломки»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def solidbar(x1, x2, yc, h, fill, stroke, sw=1.7):
    return rect(x1, yc - h / 2, x2 - x1, h, fill=fill, stroke=stroke, sw=sw, rx=6)


def dashbar(x1, x2, yc, h, fill, stroke, sw=1.7, dash="7,5"):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" '
            'fill="%s" stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>'
            % (x1, yc - h / 2, x2 - x1, h, fill, stroke, sw, dash))


def tri_right(x, yc, s, color):
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>'
            % (x, yc - s, x + s * 1.5, yc, x, yc + s, color))


def fig_expand_contract_timeline():
    """Старе поле живе крізь EXPAND+MIGRATE й зникає лише на межі CONTRACT —
    там, де навіть найповільніший клієнт нарешті перестав його читати."""
    W, H = 1020, 470
    LX = 196          # правий край лівих підписів
    XC = 890          # лінія CONTRACT
    frags = []

    # ── смуга фаз ──
    frags.append(rect(210, 50, 126, 48, fill="#eef7f0", stroke=MUTED, sw=1.2))
    frags.append(rect(336, 50, 554, 48, fill="#f4f6f8", stroke=MUTED, sw=1.2))
    frags.append(rect(890, 50, 130, 48, fill="#fdecea", stroke=MUTED, sw=1.2))
    frags.append(text(273, 74, "EXPAND", size=13, bold=True))
    frags.append(text(273, 90, "додаємо нове", size=10, color=MUTED))
    frags.append(text(613, 74, "MIGRATE", size=13, bold=True))
    frags.append(text(613, 90, "клієнти переходять своїм темпом", size=10, color=MUTED))
    frags.append(text(955, 74, "CONTRACT", size=13, bold=True))
    frags.append(text(955, 90, "прибираємо старе", size=10, color=MUTED))

    # ── поля, які віддає сервер ──
    frags.append(solidbar(210, XC, 134, 26, "#fdecea", POS))
    frags.append(text(LX, 139, "старе: tempC", size=13, color=INK, anchor="end", bold=True))
    frags.append(solidbar(290, 1000, 180, 26, "#eafaf0", FIELD))
    frags.append(tri_right(1000, 180, 10, FIELD))
    frags.append(text(LX, 185, "нове: temperature", size=13, color=INK, anchor="end", bold=True))

    # ── розділювач ──
    frags.append(line(60, 214, 1020, 214, color=MUTED, sw=1, dash="5,6"))
    frags.append(text(210, 233, "Клієнти — доки кожен ще читає старе поле tempC:",
                      size=12, color=INK, anchor="start"))

    # ── клієнти: доки читають старе ──
    rows = [
        ("Вебконсоль", 350, "дні", False),
        ("Мобільний застосунок", 460, "тижні", False),
        ("Прошивка панелі", 620, "квартал", False),
        ("Чужа інтеграція", 760, "колись / ніколи", True),
    ]
    yc = 258
    for name, xend, tempo, dashed in rows:
        if dashed:
            frags.append(dashbar(210, xend, yc, 22, "#fdecea", POS))
        else:
            frags.append(solidbar(210, xend, yc, 22, "#fdecea", POS))
        frags.append(text(LX, yc + 4, name, size=13, color=INK, anchor="end"))
        frags.append(text(xend + 12, yc + 4, tempo, size=12, color=MUTED, anchor="start"))
        yc += 38

    # ── лінія CONTRACT (двома відрізками, повз рядки полів) ──
    frags.append(line(XC, 50, XC, 98, color=POS, sw=2.5))
    frags.append(line(XC, 214, XC, 404, color=POS, sw=2.5))
    frags.append(text(XC, 428, "◄ прибрати старе можна лише тут", size=12, color=POS, bold=True))
    frags.append(text(XC, 448, "за фактом — не за датою", size=10, color=MUTED))

    render(os.path.join(IMG, "expand-contract-timeline.svg"), W, H, *frags,
           title="Старе поле живе, доки його читає бодай один клієнт")


def fig_meaning_trap():
    """Ті самі байти, той самий тип number — але старий і новий клієнти
    читають число з різним наміром; старий тихо рахує абсурдну дату."""
    W, H = 980, 470
    frags = []

    # ── пакет на дроті ──
    b, w, h = textbox(490, 92, '{ "at": 1719003600000 }\nтип: number',
                      size=15, fill="#eef2f7", stroke=INK, sw=1.8)
    frags.append(b)
    frags.append(text(490, 92 + h / 2 + 20, "однакове для обох", size=12, color=MUTED))

    # ── стрілки до клієнтів ──
    frags.append(arrow(445, 92 + h / 2, 255, 206, color=POS, sw=2.2))
    frags.append(arrow(535, 92 + h / 2, 725, 206, color=FIELD, sw=2.2))

    # ── лівий клієнт (старий) ──
    frags.append(rect(70, 210, 330, 176, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(235, 240, "Старий клієнт", size=15, color=INK, bold=True))
    frags.append(text(235, 262, "намір: СЕКУНДИ", size=12, color=MUTED))
    frags.append(fitbox(95, 278, 280, 30, "new Date(at * 1000)", size=13,
                        fill="#ffffff", stroke=MUTED))
    frags.append(text(235, 340, "→ рік 56443", size=16, color=POS, bold=True))
    frags.append(text(235, 366, "виняток НЕ кинуто", size=12, color=MUTED))

    # ── правий клієнт (новий) ──
    frags.append(rect(580, 210, 330, 176, fill="#eafaf0", stroke=FIELD, sw=2))
    frags.append(text(745, 240, "Новий клієнт", size=15, color=INK, bold=True))
    frags.append(text(745, 262, "намір: мілісекунди", size=12, color=MUTED))
    frags.append(fitbox(605, 278, 280, 30, "new Date(at)", size=13,
                        fill="#ffffff", stroke=MUTED))
    frags.append(text(745, 340, "→ 2024-06-21", size=16, color=FIELD, bold=True))
    frags.append(text(745, 366, "правильно", size=12, color=MUTED))

    # ── нижній банер ──
    frags.append(fitbox(70, 406, 840, 46,
        "Тип обох боків — number: ані компілятор, ані схема нічого не позначать.\n"
        "Різниця лише в НАМІРІ (секунди чи мілісекунди), якого в типі не видно.",
        size=13, fill="#f4f6f8", stroke=MUTED))

    render(os.path.join(IMG, "meaning-trap.svg"), W, H, *frags,
           title="Пастка зміни змісту: тип той самий, сенс різний")


def fig_stripe_pipeline():
    """Одна канонічна форма всередині; кожна стара версія — тонкий шар перекладу
    на межі: запит котиться вперед до сучасної форми, відповідь відкочується назад."""
    W, H = 1000, 430
    frags = []

    # ── ланцюг: клієнт → перетворювачі → канонічний код ──
    frags.append(fitbox(60, 175, 170, 110,
                        "Клієнт\nпришпилений до\n2015-10-16",
                        size=13, fill="#fdecea", stroke=POS, sw=2))
    frags.append(fitbox(272, 175, 128, 110, "перетворювач\n2016-03-07",
                        size=12, fill=FILL, stroke=MUTED, sw=1.5))
    frags.append(fitbox(436, 175, 128, 110, "перетворювач\n2017-05-24",
                        size=12, fill=FILL, stroke=MUTED, sw=1.5))
    frags.append(fitbox(600, 175, 128, 110, "перетворювач\n2019-03-14",
                        size=12, fill=FILL, stroke=MUTED, sw=1.5))
    frags.append(fitbox(770, 175, 175, 110, "Один канонічний код\n(сьогодні)",
                        size=13, fill="#eafaf0", stroke=FIELD, sw=2, bold=True))

    # ── верхня доріжка: запит уперед (→) ──
    frags.append(arrow(60, 145, 948, 145, color=NEG, sw=2.4))
    frags.append(text(504, 131, "① запит: прокотити ВПЕРЕД до канонічної форми",
                      size=13, color=NEG, bold=True))

    # ── нижня доріжка: відповідь назад (←) ──
    frags.append(arrow(945, 320, 57, 320, color=FIELD, sw=2.4))
    frags.append(text(504, 342,
                      "② відповідь: відкотити НАЗАД до форми, яку чекає 2015-10-16",
                      size=13, color=FIELD, bold=True))

    # ── підпис ──
    frags.append(text(504, 392,
        "Кожне ламке оновлення додає ОДИН перетворювач на межі; сучасний код живе в одній формі.",
        size=12, color=MUTED))
    frags.append(text(504, 410,
        "Стара версія — не окрема гілка кодової бази, а тонкий шар перекладу.",
        size=12, color=MUTED))

    render(os.path.join(IMG, "stripe-version-pipeline.svg"), W, H, *frags,
           title="Одна правда всередині, ланцюг перекладачів на кордоні")


def fig_stripe_timeline():
    """Хроніка обіцянки: 2011 версії-дати → ~100 ламких змін без поломки →
    2017 публічний механізм → 2024 іменовані релізи."""
    W, H = 1100, 300
    y = 150
    frags = [line(90, y, 1010, y, color=INK, sw=2)]
    nodes = [
        (150, "2011", ["Публічний запуск.", "Версії-дати", "замість v1 / v2 / v3"], False),
        (410, "2011 → 2017", ["≈ 100 ламких", "оновлень — і жодне", "не зламало старих"], False),
        (690, "5 серп. 2017", ["Brandur Leach друкує", "механізм: одна правда,", "ланцюг перекладачів"], False),
        (970, "2024-09-30", ["acacia: імена дерев,", "піврічні релізи,", "та сама обіцянка"], True),
    ]
    for x, yr, cap, hot in nodes:
        col = FIELD if hot else INK
        frags.append(circle(x, y, 9, fill=("#eafaf0" if hot else "#ffffff"),
                            stroke=col, sw=2.5))
        frags.append(text(x, 115, yr, size=15, color=INK, bold=True))
        frags.append(mtext(x, 182, cap, size=12, color=MUTED))

    render(os.path.join(IMG, "stripe-versioning-timeline.svg"), W, H, *frags,
           title="Двадцять років обіцянки не ламати нічого")


def _card(x, y, w, h, title, lines, accent, fill):
    """Картка: рамка з акцентним обрамленням, жирний заголовок, сірий корпус."""
    out = rect(x, y, w, h, fill=fill, stroke=accent, sw=2)
    out += text(x + w / 2, y + 30, title, size=15, color=INK, bold=True)
    out += mtext(x + w / 2, y + 56, lines, size=13, color=MUTED, lh=1.35)
    return out


def fig_read_signal_ladder():
    """Драбина сигналів «чи прочитав клієнт застаріле поле»: віддане (здогад) →
    когорта за особою (проксі) → явний вибір полів (доказ). Угору = певніше."""
    W, H = 1060, 470
    cw, ch = 300, 150
    frags = []

    steps = [
        (40, 250, POS, "#fdecea", "① Рахувати ВІДДАНЕ",
         ["бачу: лише що сам віддав", "tempC поїхав усім підряд", "→ лічильник не занулиться"]),
        (380, 165, MUTED, "#f4f6f8", "② Когорта за особою",
         ["бачу: версію клієнта", "до-temperature версія читає", "→ натяк, ще не доказ"]),
        (720, 80, FIELD, "#eafaf0", "③ Явний вибір полів",
         ["бачу: ?fields= у запиті", "назвав tempC → читає", "→ доказ у самому запиті"]),
    ]

    # з'єднувачі між сходинками (пунктир, від правого краю до лівого наступної)
    frags.append(line(40 + cw, 250 + ch / 2, 380, 165 + ch / 2,
                      color=MUTED, sw=1.5, dash="6,6"))
    frags.append(line(380 + cw, 165 + ch / 2, 720, 80 + ch / 2,
                      color=MUTED, sw=1.5, dash="6,6"))

    for x, y, accent, fill, title, lines in steps:
        frags.append(_card(x, y, cw, ch, title, lines, accent, fill))

    # вісь «сила сигналу»
    frags.append(arrow(70, 440, 990, 440, color=INK, sw=2.2))
    frags.append(text(70, 428, "здогад", size=12, color=MUTED, anchor="start"))
    frags.append(text(990, 428, "доказ", size=12, color=FIELD, anchor="end", bold=True))
    frags.append(text(530, 458, "сила сигналу: чим вище сходинка, тим ближче «читання» до того, що сервер справді бачить",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "read-signal-ladder.svg"), W, H, *frags,
           title="Як зробити невидиме читання видимим")


def fig_contract_gate():
    """Ворота готовності як «І» над усіма когортами: одна ненульова — замкнено.
    Окремо — забута когорта unknown, чий провід обірвано (джерело фальшивої зелені)."""
    W, H = 1080, 500
    GX, GY, GW, GH = 560, 95, 300, 210   # ворота
    frags = []

    # ── когорти-входи (усі течуть у ворота) ──
    rows = [
        (95, "web:console", "0 читань / 30 дн", FIELD, "#eafaf0"),
        (170, "app:3.4", "0 читань / 30 дн", FIELD, "#eafaf0"),
        (245, "panel:fw11", "3 читання / 30 дн", POS, "#fdecea"),
    ]
    pw = 230
    for y, name, val, col, fill in rows:
        frags.append(rect(60, y, pw, 54, fill=fill, stroke=col, sw=2))
        frags.append(text(60 + pw / 2, y + 22, name, size=14, color=INK, bold=True))
        frags.append(text(60 + pw / 2, y + 42, val, size=12, color=col))
        # провід у ворота
        frags.append(line(60 + pw, y + 27, GX, y + 27, color=col, sw=2))
        frags.append(circle(GX, y + 27, 3.5, fill=col, stroke=col))

    # ── ворота ──
    frags.append(rect(GX, GY, GW, GH, fill="#f8fafc", stroke=INK, sw=2.2))
    frags.append(text(GX + GW / 2, GY + 34, "canContract('tempC')", size=16, color=INK, bold=True))
    frags.append(mtext(GX + GW / 2, GY + 66,
                       ["ворота = «І» над УСІМА когортами", "вікно 30 днів",
                        "зелено ⟺ Σ читань = 0", "у КОЖНІЙ когорті"],
                       size=13, color=MUTED, lh=1.5))
    frags.append(text(GX + GW / 2, GY + GH - 14,
                      "panel ≠ 0  →  ЗАЧИНЕНО", size=15, color=POS, bold=True))

    # ── вихід воріт ──
    frags.append(arrow(GX + GW, GY + GH / 2, 940, GY + GH / 2, color=POS, sw=2.4))
    frags.append(rect(940, GY + GH / 2 - 34, 128, 68, fill="#fdecea", stroke=POS, sw=2.2))
    frags.append(text(1004, GY + GH / 2 - 4, "contract", size=14, color=INK, bold=True))
    frags.append(text(1004, GY + GH / 2 + 18, "ЗАМКНЕНО", size=14, color=POS, bold=True))

    # ── забута когорта: провід обірвано ──
    fy = 360
    frags.append(('<rect x="60" y="%.1f" width="%.1f" height="54" rx="6" '
                  'fill="#fdecea" stroke="%s" stroke-width="2" stroke-dasharray="7,5"/>'
                  % (fy, pw, POS)))
    frags.append(text(60 + pw / 2, fy + 22, "unknown (чужа інтеграція)", size=13, color=INK, bold=True))
    frags.append(text(60 + pw / 2, fy + 42, "5 читань / 30 дн", size=12, color=POS))
    # обірваний провід
    cutx = 428
    frags.append(line(60 + pw, fy + 27, cutx, fy + 27, color=POS, sw=2, dash="6,5"))
    # позначка розриву (хрестик)
    frags.append(line(cutx - 8, fy + 19, cutx + 8, fy + 35, color=POS, sw=2.4))
    frags.append(line(cutx - 8, fy + 35, cutx + 8, fy + 19, color=POS, sw=2.4))

    frags.append(fitbox(460, fy - 6, 600, 66,
        "Рукотворний список {web, app, panel} проґавив unknown → ворота її не спитали.\n"
        "Бери когорти з САМОЇ телеметрії — і жоден читач не пройде повз ворота.",
        size=12, fill="#f4f6f8", stroke=MUTED))

    render(os.path.join(IMG, "contract-gate.svg"), W, H, *frags,
           title="Ворота готовності: зелено лише коли нуль у кожній когорті")


if __name__ == "__main__":
    fig_expand_contract_timeline()
    fig_meaning_trap()
    fig_stripe_pipeline()
    fig_stripe_timeline()
    fig_read_signal_ladder()
    fig_contract_gate()
    print("OK: expand-contract-timeline.svg, meaning-trap.svg, "
          "stripe-version-pipeline.svg, stripe-versioning-timeline.svg, "
          "read-signal-ladder.svg, contract-gate.svg")
