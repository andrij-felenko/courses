# -*- coding: utf-8 -*-
"""Фігури до теми «Радіо на чіпі» та її історичної вставки про назву Bluetooth.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: F401,F403

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# ── невеликі локальні помічники поверх svgkit (без власного стилю) ───────────
GOLD = "#b08900"


def antenna(x, y_base, h=24):
    """Щогла антени зі стрілкою-вилкою вгорі (символ випромінювача)."""
    top = y_base - h
    return (line(x, y_base, x, top, color=NEG, sw=2) +
            line(x, top, x - 6, top - 8, color=NEG, sw=2) +
            line(x, top, x + 6, top - 8, color=NEG, sw=2))


def waves(cx, cy, n=3, r0=10, dr=12):
    """Дуги радіохвиль праворуч від точки (cx,cy)."""
    out = []
    for i in range(n):
        r = r0 + i * dr
        out.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                   'fill="none" stroke="%s" stroke-width="1.8"/>'
                   % (cx, cy - r, r, r, cx, cy + r, NEG))
    return "".join(out)


def cross(cx, cy, s=7, color=POS):
    return (line(cx - s, cy - s, cx + s, cy + s, color=color, sw=2.4) +
            line(cx - s, cy + s, cx + s, cy - s, color=color, sw=2.4))


# ════════════════════════════════════════════════════════════════════════════
#  СТАТТЯ «Радіо на чіпі»
# ════════════════════════════════════════════════════════════════════════════

def fig_radio_on_chip():
    """Кристал МК: обчислювальне ядро + радіо (TX/RX) + антена на одному чіпі.
    Показує головне — увесь приймач-передавач тепер у куточку кремнію поряд із
    процесором, і користувач бачить лише простий програмний виклик."""
    W, H = 760, 340
    f = [rect(180, 90, 320, 170, fill="#eef1f5", stroke=INK, sw=2.0, rx=14)]
    f.append(text(340, 114, "мікроконтролер (напр. ESP32)", size=13, bold=True, color=INK))

    f.append(fitbox(205, 132, 120, 100, "ядро\nпроцесор", size=13, bold=True,
                    fill="#eaf6ec", stroke=FIELD))
    f.append(fitbox(345, 132, 140, 100, "радіо\nпередавач\nприймач", size=12, bold=True,
                    fill="#eaf0fd", stroke=NEG))
    f.append(line(325, 182, 345, 182, color=MUTED, sw=1.6))

    # антена з хвилями праворуч від блоку «радіо»
    f.append(antenna(520, 175, h=26))
    f.append(line(480, 182, 520, 175, color=NEG, sw=1.6))
    f.append(waves(540, 165, n=3, r0=10, dr=12))
    f.append(text(600, 168, "по повітрю", size=12, bold=True, color=NEG, anchor="start"))

    box = fitbox(60, 282, 640, 40,
                 "Кілька рядків коду — і пристрій уже говорить по радіо. Уся складність радіо схована всередині.",
                 size=12, bold=True, fill="#eaf6ec", stroke=FIELD)
    f.append(box)
    return render(os.path.join(IMG, "radio-on-chip.svg"), W, H, *f,
                  title="Радіо на чіпі: цілий приймач-передавач усередині МК")


def fig_wire_vs_air():
    """Дріт (приватний канал A↔B, гарантія) проти повітря (спільне середовище,
    чують усі, доставка як пощастить). Контраст — корінь усієї ненадійності."""
    W, H = 760, 350
    f = [rect(40, 80, 320, 230, fill=BG, stroke="#e4e4e4", sw=2, rx=12)]
    f.append(text(200, 106, "дріт (UART / I2C / SPI)", size=13, bold=True, color=FIELD))
    f.append(fitbox(80, 168, 80, 50, "A", size=14, bold=True, stroke=INK))
    f.append(fitbox(280, 168, 80, 50, "B", size=14, bold=True, stroke=INK))
    f.append(line(160, 193, 280, 193, color=FIELD, sw=3))
    f.append(text(220, 184, "лише A↔B", size=10, bold=True, color=FIELD))
    f.append(text(200, 256, "доставка гарантована,", size=11, bold=True, color=INK))
    f.append(text(200, 274, "час сталий, ніхто чужий не чує", size=10, color=MUTED))

    f.append(rect(400, 80, 320, 230, fill=BG, stroke="#e4e4e4", sw=2, rx=12))
    f.append(text(560, 106, "повітря (радіо)", size=13, bold=True, color=NEG))
    f.append(fitbox(440, 170, 80, 46, "A", size=13, bold=True, stroke=INK))
    f.append(antenna(520, 170, h=22))
    f.append(waves(520, 150, n=4, r0=8, dr=11))
    f.append(fitbox(640, 120, 70, 36, "B", size=11, bold=True, stroke=INK))
    f.append(fitbox(640, 178, 70, 36, "чужий", size=10, bold=True, stroke=MUTED, color=MUTED))
    f.append(fitbox(610, 236, 70, 36, "ще хтось", size=10, bold=True, stroke=MUTED, color=MUTED))
    f.append(text(560, 300, "чують усі довкола; доставка — як пощастить",
                  size=10, italic=True, color=MUTED))
    return render(os.path.join(IMG, "wire-vs-air.svg"), W, H, *f,
                  title="Дріт проти повітря: приватний канал проти спільного")


def fig_signal_enemies():
    """Шлях TX→RX, на якому сигнал тіснять відстань, перешкоди, інше радіо й
    відбиття (плюс шум). Жоден із цих ворогів не діє на дріт."""
    W, H = 760, 340
    f = [fitbox(50, 150, 80, 56, "TX", size=14, bold=True, fill="#eaf6ec", stroke=FIELD, color=FIELD)]
    f.append(antenna(130, 150, h=20))
    f.append(fitbox(630, 150, 80, 56, "RX", size=14, bold=True, stroke=INK))
    f.append(antenna(630, 150, h=20))
    f.append(waves(130, 132, n=3, r0=8, dr=10))

    # шлях сигналу
    f.append('<line x1="170" y1="178" x2="620" y2="178" stroke="%s" stroke-width="2" '
             'stroke-dasharray="5,4" marker-end="url(#arrow)"/>' % NEG)
    f.append(text(400, 138, "сигнал слабшає й спотворюється", size=11, bold=True, color=POS))

    enemies = [(250, "стіна", "поглинає"),
               (360, "відстань", "слабшає"),
               (470, "інше радіо", "завада/колізія"),
               (560, "відбиття", "багатопроменевість")]
    for x, a, b in enemies:
        f.append(line(x, 178, x, 220, color=POS, sw=1.6, dash="3,3"))
        f.append(text(x, 238, a, size=9, bold=True, color=POS))
        f.append(text(x, 253, b, size=9, color=MUTED))

    f.append(fitbox(40, 278, 680, 48,
                    "Жоден із цих ворогів не діє на дріт — у повітрі вони є завжди.\n"
                    "Частина бітів псується, а цілі пакети просто ЗНИКАЮТЬ.",
                    size=11, bold=True, fill="#fbecec", stroke=POS))
    return render(os.path.join(IMG, "signal-enemies.svg"), W, H, *f,
                  title="Чому радіо ненадійне: що псує сигнал у дорозі")


def fig_lost_packets():
    """Два ряди: надіслано P0..P4 — отримано лише частину (P1 зник, P3 спотворений
    за CRC, решта дійшли). Наочно: у радіо втрати — буденність."""
    W, H = 760, 320
    f = [text(110, 122, "надіслано:", size=12, bold=True, anchor="end")]
    xs = [140, 260, 380, 500, 620]
    for i, x in enumerate(xs):
        f.append(fitbox(x, 105, 90, 30, "P%d" % i, size=11, bold=True,
                        fill="#eaf0fd", stroke=NEG, color=NEG))

    f.append(text(110, 242, "отримано:", size=12, bold=True, anchor="end"))
    # P0 ok
    f.append(fitbox(xs[0], 225, 90, 30, "P0", size=11, bold=True, fill="#eaf6ec", stroke=FIELD, color=FIELD))
    f.append(arrow(xs[0] + 45, 137, xs[0] + 45, 223, color=MUTED, sw=1.4))
    # P1 lost
    f.append(fitbox(xs[1], 225, 90, 30, "— зник", size=10, bold=True, fill="#f4f4f4", stroke=MUTED, color=POS))
    f.append(line(xs[1] + 45, 137, xs[1] + 45, 200, color=POS, sw=1.4, dash="4,3"))
    f.append(cross(xs[1] + 45, 188, s=7))
    # P2 ok
    f.append(fitbox(xs[2], 225, 90, 30, "P2", size=11, bold=True, fill="#eaf6ec", stroke=FIELD, color=FIELD))
    f.append(arrow(xs[2] + 45, 137, xs[2] + 45, 223, color=MUTED, sw=1.4))
    # P3 corrupted (CRC)
    f.append(fitbox(xs[3], 225, 90, 30, "P3?", size=11, bold=True, fill="#fbecec", stroke=POS, color=POS))
    f.append(text(xs[3] + 45, 280, "CRC не зійшовся", size=9, bold=True, color=POS))
    f.append(arrow(xs[3] + 45, 137, xs[3] + 45, 223, color=POS, sw=1.4))
    # P4 ok
    f.append(fitbox(xs[4], 225, 90, 30, "P4", size=11, bold=True, fill="#eaf6ec", stroke=FIELD, color=FIELD))
    f.append(arrow(xs[4] + 45, 137, xs[4] + 45, 223, color=MUTED, sw=1.4))
    return render(os.path.join(IMG, "lost-packets.svg"), W, H, *f,
                  title="Наслідок: пакети губляться й псуються (на відміну від дроту)")


def fig_ack_retry():
    """Часова діаграма: успіх (пакет→ACK) і втрата (пакет зник, час очікування
    вийшов, передавач шле наново — і отримує ACK). Так ненадійне стає надійним."""
    W, H = 760, 380
    tx, rx = 150, 620
    f = [text(tx, 78, "передавач", size=12, bold=True, color=FIELD)]
    f.append(text(rx, 78, "приймач", size=12, bold=True, color=INK))
    f.append(line(tx, 90, tx, 350, color=MUTED, sw=1.4))
    f.append(line(rx, 90, rx, 350, color=MUTED, sw=1.4))

    # успіх
    f.append('<line x1="%d" y1="116" x2="%d" y2="136" stroke="%s" stroke-width="2.2" '
             'marker-end="url(#arrow)"/>' % (tx, rx, NEG))
    f.append(text(385, 118, "пакет", size=10, bold=True, color=NEG))
    f.append('<line x1="%d" y1="150" x2="%d" y2="170" stroke="%s" stroke-width="2.2" '
             'marker-end="url(#arrow)"/>' % (rx, tx, FIELD))
    f.append(text(385, 153, "ACK ✓", size=10, bold=True, color=FIELD))
    f.append(text(70, 173, "доставлено", size=10, color=FIELD, anchor="start"))

    # втрата
    f.append('<line x1="%d" y1="210" x2="430" y2="230" stroke="%s" stroke-width="2.2" '
             'stroke-dasharray="4,3" marker-end="url(#arrow)"/>' % (tx, NEG))
    f.append(text(330, 209, "пакет (загубився)", size=10, bold=True, color=POS))
    f.append(cross(452, 232, s=8))
    f.append(line(tx - 14, 230, tx - 14, 276, color=GOLD, sw=1.6, dash="3,3"))
    f.append(text(86, 252, "час очікування", size=9, bold=True, color=GOLD))
    f.append(text(86, 267, "вийшов — нема ACK", size=9, color=MUTED))

    # повтор
    f.append('<line x1="%d" y1="288" x2="%d" y2="308" stroke="%s" stroke-width="2.2" '
             'marker-end="url(#arrow)"/>' % (tx, rx, NEG))
    f.append(text(385, 290, "пакет (ще раз)", size=10, bold=True, color=NEG))
    f.append('<line x1="%d" y1="322" x2="%d" y2="342" stroke="%s" stroke-width="2.2" '
             'marker-end="url(#arrow)"/>' % (rx, tx, FIELD))
    f.append(text(385, 325, "ACK ✓", size=10, bold=True, color=FIELD))
    return render(os.path.join(IMG, "ack-retry.svg"), W, H, *f,
                  title="Надійність: підтвердження (ACK) і перевідправлення")


def fig_best_effort_vs_reliable():
    """Дві колонки-режими: «як вийде» (швидко, але губить) проти надійного (нічого
    не губить, та затримка плаває). Вибір — суто за задачею."""
    W, H = 760, 360
    f = [rect(50, 84, 320, 210, fill=BG, stroke=GOLD, sw=2, rx=12)]
    f.append(text(210, 110, "«як вийде» (best-effort)", size=13, bold=True, color=GOLD))
    le = ["• без ACK, без повторів",
          "• швидко, мала стала затримка",
          "• частина пакетів губиться",
          "• для потоку, де втрата",
          "  кадру не страшна"]
    for i, ln in enumerate(le):
        col = POS if "губиться" in ln else INK
        f.append(text(72, 140 + i * 24, ln, size=11, color=col, anchor="start"))
    f.append(text(210, 280, "напр. потокове відео, телеметрія", size=10, italic=True, color=MUTED))

    f.append(rect(390, 84, 320, 210, fill="#eaf6ec", stroke=FIELD, sw=2, rx=12))
    f.append(text(550, 110, "надійний (з гарантією)", size=13, bold=True, color=FIELD))
    ri = ["• ACK + перевідправлення",
          "• майже нічого не губиться",
          "• затримка ПЛАВАЄ (джитер)",
          "• для команд, які",
          "  втратити не можна"]
    for i, ln in enumerate(ri):
        col = POS if "ПЛАВАЄ" in ln else (FIELD if "не губиться" in ln else INK)
        f.append(text(412, 140 + i * 24, ln, size=11, color=col, anchor="start"))
    f.append(text(550, 280, "напр. команди керування, файли", size=10, italic=True, color=MUTED))

    f.append(fitbox(50, 312, 660, 40,
                    "Вибір — за задачею: важлива швидкість і не страшна втрата → «як вийде»; "
                    "важлива доставка → надійний.",
                    size=11, bold=True, fill="#eaf6ec", stroke=FIELD))
    return render(os.path.join(IMG, "best-effort-vs-reliable.svg"), W, H, *f,
                  title="Два режими: «вистрілив і забув» проти «з гарантією»")


def fig_failsafe():
    """Стек шарами: застосунок (твій failsafe) / стек радіо (ховає ACK і повтори)
    / радіо на чіпі. Межа відповідальності: повну тишу ловить лише застосунок."""
    W, H = 760, 360
    layers = [(96, "твій застосунок", "send() / on_receive()  +  FAILSAFE на тривалу тишу", FIELD, "#eaf6ec"),
              (164, "стек радіо (Wi-Fi / BT)", "пакети, CRC, ACK, повтори — усе ховається тут", NEG, BG),
              (232, "радіо на чіпі", "антена, модуляція, біти по повітрю", GOLD, BG)]
    f = []
    for y, head, sub, col, fill in layers:
        f.append(rect(110, y, 540, 56, fill=fill, stroke=col, sw=2, rx=10))
        f.append(text(132, y + 24, head, size=12.5, bold=True, color=col, anchor="start"))
        f.append(text(132, y + 44, sub, size=10.5, color=INK, anchor="start"))
    f.append(arrow(380, 152, 380, 164, color=MUTED, sw=1.6))
    f.append(arrow(380, 220, 380, 232, color=MUTED, sw=1.6))
    f.append(fitbox(50, 304, 660, 46,
                    "Межа відповідальності: повтори окремих пакетів — справа чіпа; "
                    "реакція на ПОВНУ втрату зв'язку — твоя.",
                    size=11, bold=True, fill="#fbecec", stroke=POS))
    return render(os.path.join(IMG, "failsafe.svg"), W, H, *f,
                  title="Стек ховає повтори — а повну втрату зв'язку ловиш ТИ")


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА «Чому Bluetooth названо на честь вікінга-короля»
# ════════════════════════════════════════════════════════════════════════════

def fig_name_timeline():
    """Вертикальна стрічка подій: король Гаральд → радіо в Лунді → кодова назва
    в Intel → консорціум SIG → провал «серйозних» назв. Як випадковість лишила
    жартівливе ім'я назавжди."""
    W, H = 760, 560
    axis = 200
    f = [line(axis, 70, axis, 520, color=MUTED, sw=3)]
    rows = [(100, "~960", "Гаральд Синьозубий",
             "Король данів об'єднує розрізнені племена в одне королівство — звідси вся метафора", INK),
            (185, "1994", "Ericsson, Лунд",
             "Яап Гаартсен і Свен Маттіссон починають дешеве коротке радіо без дротів", INK),
            (278, "~1996", "Джим Кардач, Intel",
             "Зі скандинавських саг («Рудий Орм») бере КОДОВУ назву: об'єднає протоколи, як король — племена", NEG),
            (371, "1998", "SIG: 5 компаній",
             "Ericsson, Intel, Nokia, IBM, Toshiba творять консорціум; шукають «серйозну» назву", INK),
            (456, "1998", "PAN і RadioWire провалились",
             "PAN не пройшов перевірку марки, RadioWire не встигли перевірити — лишився Bluetooth", INK)]
    for y, when, head, body, col in rows:
        big = (col == NEG)
        f.append(circle(axis, y, 9 if big else 7, fill=BG, stroke=col, sw=3 if big else 2.4))
        if big:
            f.append(circle(axis, y, 4, fill=col, stroke=col, sw=0))
        f.append(text(axis - 20, y + 5, when, size=12, bold=True, color=MUTED, anchor="end"))
        f.append(text(axis + 24, y - 4, head, size=15, bold=True, color=col, anchor="start"))
        f.append(text(axis + 24, y + 16, body, size=11, italic=True, color=INK, anchor="start"))
    f.append(fitbox(60, 500, 640, 44,
                    "Технологію зробили в Лунді, назвали жартома в Intel — а «серйозне» ім'я так і не вигадали.",
                    size=12, bold=True, fill="#eaf6ec", stroke=FIELD))
    return render(os.path.join(IMG, "name-timeline.svg"), W, H, *f,
                  title="Як радіо назвали іменем вікінга — ланцюг подій")


def _chip_grid(cx, top, labels, fill, stroke):
    """Сітка підписаних чипів-«учасників» 3+2 (племена або пристрої).
    fitbox гарантує, що підпис уміститься й не дрібнішає за межу читабельності."""
    out = []
    cw, ch, gx, gy = 84, 34, 8, 10
    rows = [labels[:3], labels[3:]]
    for r, row in enumerate(rows):
        roww = len(row) * cw + (len(row) - 1) * gx
        x0 = cx - roww / 2
        for i, lab in enumerate(row):
            x = x0 + i * (cw + gx)
            y = top + r * (ch + gy)
            out.append(fitbox(x, y, cw, ch, lab, size=10, bold=True, fill=fill, stroke=stroke))
    return "".join(out)


def fig_unite_metaphor():
    """Паралель «об'єднувача»: ліворуч Гаральд зводить племена в королівство,
    праворуч Bluetooth зводить несумісні пристрої в одну радіомову."""
    W, H = 760, 400
    f = [text(190, 92, "Гаральд (~960)", size=13, bold=True, color=INK)]
    f.append(_chip_grid(190, 104, ["плем'я", "плем'я", "плем'я", "плем'я", "плем'я"],
                        "#efe7d5", "#caa24a"))
    f.append(arrow(190, 196, 190, 240, color=FIELD, sw=2.4))
    f.append(fitbox(110, 244, 160, 50, "одне\nкоролівство", size=12, bold=True,
                    fill="#efe7d5", stroke="#caa24a"))

    f.append(text(570, 92, "Bluetooth (1998)", size=13, bold=True, color=NEG))
    f.append(_chip_grid(570, 104, ["ПК", "телефон", "гарнітура", "миша", "колонка"],
                        "#eaf0fd", NEG))
    f.append(arrow(570, 196, 570, 240, color=FIELD, sw=2.4))
    f.append(fitbox(490, 244, 160, 50, "одна\nрадіомова", size=12, bold=True,
                    fill="#eaf0fd", stroke=NEG))

    f.append(text(385, 180, "≈", size=30, bold=True, color=MUTED))
    f.append(fitbox(60, 344, 640, 40,
                    "Саме цю паралель — «об'єднувач» — і мав на увазі Кардач, пропонуючи кодову назву.",
                    size=12, bold=True, fill="#eaf6ec", stroke=FIELD))
    return render(os.path.join(IMG, "unite-metaphor.svg"), W, H, *f,
                  title="Метафора назви: об'єднати — як король об'єднав племена")


def _rune_panel(x, fill, strokes):
    """Темна панель із рунічними штрихами (list of (x1,y1,x2,y2))."""
    out = [rect(x, 100, 150, 180, fill="#23262b", stroke="#111", sw=2, rx=12)]
    for x1, y1, x2, y2 in strokes:
        out.append(line(x1, y1, x2, y2, color="#ffffff", sw=4))
    return "".join(out)


def fig_rune_logo():
    """Дві руни молодшого футарка — Hagall (H) і Bjarkan (B) — зливаються в одну
    біндруну, знайомий значок Bluetooth (ініціали короля Harald Blåtand)."""
    W, H = 760, 400
    # Hagall ᚼ: дві стійки + перемичка
    f = [_rune_panel(100, "#23262b", [(153, 140, 153, 240), (197, 140, 197, 240),
                                      (153, 177, 197, 203)])]
    f.append(text(175, 308, "ᚼ Hagall = H", size=13, bold=True))
    f.append(text(175, 328, "(Harald)", size=10.5, color=MUTED))
    f.append(text(285, 200, "+", size=30, bold=True, color=MUTED))

    # Bjarkan ᛒ: стійка + два «горбики»
    f.append(_rune_panel(330, "#23262b", [(390, 140, 390, 240),
                                          (390, 140, 418, 165), (418, 165, 390, 190),
                                          (390, 190, 418, 215), (418, 215, 390, 240)]))
    f.append(text(405, 308, "ᛒ Bjarkan = B", size=13, bold=True))
    f.append(text(405, 328, "(Blåtand «синьозубий»)", size=10.5, color=MUTED))

    f.append(arrow(500, 190, 575, 190, color=FIELD, sw=2.6))
    f.append(text(537, 178, "злиття", size=11, bold=True, color=FIELD))

    # біндруна = логотип
    f.append(rect(600, 100, 150, 180, fill=NEG, stroke="#06245a", sw=2, rx=16))
    f.append(line(668, 132, 668, 248, color="#fff", sw=4.5))
    f.append(line(668, 132, 700, 218, color="#fff", sw=4.5))
    f.append(line(668, 248, 700, 162, color="#fff", sw=4.5))
    f.append(line(700, 162, 668, 162, color="#fff", sw=4.5))
    f.append(line(700, 218, 668, 218, color="#fff", sw=4.5))
    f.append(text(675, 308, "логотип Bluetooth", size=13, bold=True, color=NEG))
    f.append(text(675, 328, "біндруна H + B", size=10.5, color=MUTED))

    f.append(fitbox(60, 352, 640, 40,
                    "Щодня ти бачиш на екрані тисячолітні скандинавські руни — ініціали данського короля.",
                    size=12, bold=True, fill="#eaf6ec", stroke=FIELD))
    return render(os.path.join(IMG, "rune-logo.svg"), W, H, *f,
                  title="Логотип — це ініціали короля рунами: H + B")


def fig_placeholder_name():
    """Три картки: PAN (провалив перевірку марки) і RadioWire (не встигли
    перевірити) відпали — лишилася робоча заглушка Bluetooth, і стала брендом."""
    W, H = 760, 380
    cards = [(50, "PAN", "Personal Area Network", POS,
              ["✗ провалив перевірку", "торгової марки", "(десятки тисяч збігів)"], BG),
             (290, "RadioWire", "«радіодріт»", POS,
              ["✗ не встигли перевірити", "марку вчасно", ""], BG),
             (530, "Bluetooth", "робоча заглушка", FIELD,
              ["✓ єдине, з чим могли", "вийти на запуск —", "і прижилось назавжди"], "#eaf6ec")]
    f = []
    for x, name, sub, col, lines, fill in cards:
        f.append(rect(x, 90, 200, 200, fill=fill, stroke=col, sw=2, rx=12))
        f.append(text(x + 100, 122, name, size=16, bold=True, color=col))
        f.append(text(x + 100, 144, sub, size=10.5, italic=True, color=MUTED))
        for i, ln in enumerate(lines):
            if ln:
                f.append(text(x + 100, 180 + i * 20, ln, size=11, color=INK))
    f.append(fitbox(60, 312, 640, 46,
                    "Випадковість маркетингу: «серйозну» назву так і не встигли поставити — "
                    "і заглушка стала світовим брендом.",
                    size=11, bold=True, fill="#eaf6ec", stroke=FIELD))
    return render(os.path.join(IMG, "placeholder-name.svg"), W, H, *f,
                  title="Як «тимчасова» назва лишилася назавжди")


def fig_who_did_it():
    """Три колонки авторства: ТЕХНІКА (Ericsson, Лунд) / НАЗВА (Intel) / СТАНДАРТ
    (консорціум SIG). Винахід колективний — одного «винахідника» немає."""
    W, H = 760, 360
    cols = [(50, "ТЕХНІКА", "Ericsson, Лунд", FIELD,
             ["Яап Гаартсен —", "«батько Bluetooth»", "Свен Маттіссон", "радіо, з 1994"]),
            (285, "НАЗВА", "Intel", NEG,
             ["Джим Кардач", "кодова назва", "зі скандинавських саг", "ідея «об'єднувача»"]),
            (520, "СТАНДАРТ", "SIG (1998)", GOLD,
             ["Ericsson, Intel, Nokia,", "IBM, Toshiba —", "разом, відкритий", "стандарт"])]
    f = []
    for x, head, who, col, items in cols:
        f.append(rect(x, 86, 200, 210, fill=BG, stroke=col, sw=2.2, rx=12))
        f.append(text(x + 100, 114, head, size=13.5, bold=True, color=col))
        f.append(text(x + 100, 136, who, size=12, bold=True, color=INK))
        for i, it in enumerate(items):
            f.append(text(x + 18, 164 + i * 24, it, size=10.5, color=INK, anchor="start"))
    f.append(fitbox(60, 306, 640, 44,
                    "Як і з радіо чи транзистором, тут немає одного «винахідника»: "
                    "техніка, назва й стандарт — праця різних команд.",
                    size=11, bold=True, fill="#eaf6ec", stroke=FIELD))
    return render(os.path.join(IMG, "who-did-it.svg"), W, H, *f,
                  title="Хто що зробив: техніка, назва, стандарт — різні люди")


def main():
    for fn in (fig_radio_on_chip, fig_wire_vs_air, fig_signal_enemies, fig_lost_packets,
               fig_ack_retry, fig_best_effort_vs_reliable, fig_failsafe,
               fig_name_timeline, fig_unite_metaphor, fig_rune_logo,
               fig_placeholder_name, fig_who_did_it):
        p = fn()
        print("written", os.path.relpath(p, os.path.dirname(__file__)))


if __name__ == "__main__":
    main()
