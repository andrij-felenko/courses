# -*- coding: utf-8 -*-
"""Фігури до теми «D-Bus: шина повідомлень простору користувача»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_mesh_vs_star():
    """Прямі з'єднання кожен з кожним проти одного з'єднання на процес через брокер."""
    W, H = 1060, 700
    g = []

    LX, RX, BW, BH = 60, 790, 190, 52
    CLIENTS = ["панель", "поштова програма", "менеджер живлення"]
    SERVICES = ["служба мережі", "сховище ключів", "керування сеансом"]

    # ── верхня панель: напряму ────────────────────────────────────────────
    g.append(text(W / 2, 30, "напряму: 3 клієнти × 3 служби = 9 окремих з'єднань",
                  size=15, bold=True))
    g.append(text(W / 2, 52, "кожна пара сама домовляється про шлях сокета, кадрування, типи й перевірку прав",
                  size=13, color=MUTED))

    ys = [70, 150, 230]
    lc = [y + BH / 2 for y in ys]
    for i, y in enumerate(ys):
        g.append(fitbox(LX, y, BW, BH, CLIENTS[i], size=13))
        g.append(fitbox(RX, y, BW, BH, SERVICES[i], size=13, fill="#eef6ef", stroke=FIELD))
    for a in lc:
        for b in lc:
            g.append(line(LX + BW, a, RX, b, color=MUTED, sw=1.1))

    g.append(text(W / 2, 320, "9 дротів — і 9 разів ті самі домовленості", size=13, color=MUTED))

    # ── нижня панель: через брокер ────────────────────────────────────────
    g.append(text(W / 2, 366, "через шину: одне з'єднання на процес", size=15, bold=True))
    g.append(text(W / 2, 388, "іменування, кадрування, типи, підписки й права — один раз, у брокері",
                  size=13, color=MUTED))

    ys2 = [406, 486, 566]
    lc2 = [y + BH / 2 for y in ys2]
    for i, y in enumerate(ys2):
        g.append(fitbox(LX, y, BW, BH, CLIENTS[i], size=13))
        g.append(fitbox(RX, y, BW, BH, SERVICES[i], size=13, fill="#eef6ef", stroke=FIELD))

    BKX, BKY, BKW, BKH = 450, 476, 160, 76
    for a in lc2:
        g.append(line(LX + BW, a, BKX, BKY + BKH / 2, color=LINE, sw=1.3))
        g.append(line(BKX + BKW, BKY + BKH / 2, RX, a, color=LINE, sw=1.3))
    g.append(fitbox(BKX, BKY, BKW, BKH, "брокер\nшини", size=14, bold=True,
                    fill="#fdecea", stroke=POS))

    g.append(text(W / 2, 660, "6 дротів — і одні правила на всіх", size=13, color=MUTED))

    return render(os.path.join(IMG, 'mesh-vs-star.svg'), W, H, *g)


def fig_message_address():
    """Чотири частини адреси повідомлення: до кого, до чого, за яким контрактом, що саме."""
    W, H = 1180, 300
    g = []

    g.append(text(W / 2, 32, "адреса повідомлення — чотири незалежні частини", size=15, bold=True))

    COLX = [40, 330, 620, 910]
    CW = 240
    NAMES = ["ім'я на шині", "шлях об'єкта", "інтерфейс", "член"]
    QUEST = ["до якого процеса", "до чого в ньому", "за яким контрактом", "що саме"]
    EXAMPLES = [
        "org.freedesktop\n.NetworkManager",
        "/org/freedesktop/\nNetworkManager/\nDevices/0",
        "org.freedesktop\n.NetworkManager\n.Device",
        "StateChanged",
    ]

    for i, x in enumerate(COLX):
        g.append(fitbox(x, 58, CW, 46, NAMES[i], size=15, bold=True))
        g.append(text(x + CW / 2, 128, QUEST[i], size=13, color=MUTED))
        g.append(fitbox(x, 146, CW, 76, EXAMPLES[i], size=12,
                        fill="#eef6ef", stroke=FIELD))
        if i < 3:
            g.append(arrow(x + CW + 4, 81, x + CW + 44, 81))

    g.append(text(W / 2, 262, "будь-яку частину можна змінити, не чіпаючи решти трьох",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, 'message-address.svg'), W, H, *g)


def fig_call_and_signal():
    """Виклик іде туди й назад через брокера; сигнал доходить лише до підписаних."""
    W, H = 1120, 610
    g = []

    LANES = [130, 400, 690, 980]
    TITLES = ["клієнт A\n(є правило добору)", "брокер", "служба", "клієнт B\n(без підписки)"]
    for i, x in enumerate(LANES):
        g.append(fitbox(x - 105, 24, 210, 54, TITLES[i], size=13, bold=True,
                        fill="#fdecea" if i == 1 else FILL,
                        stroke=POS if i == 1 else LINE))
        g.append(line(x, 88, x, 560, color=MUTED, sw=1.1, dash="5 6"))

    def ev(x1, x2, y, label, dashed=False, anchor=None):
        if dashed:
            g.append(line(x1, y, x2, y, color=MUTED, sw=1.5, dash="7 5"))
        else:
            g.append(arrow(x1, y, x2, y))
        if anchor == "end":
            g.append(text(x2 - 10, y - 10, label, size=12, anchor="end", color=MUTED))
        else:
            g.append(text((x1 + x2) / 2, y - 10, label, size=12))

    ev(LANES[0], LANES[1], 150, "виклик, номер 7")
    ev(LANES[1], LANES[2], 205, "виклик, номер 7")
    ev(LANES[2], LANES[1], 275, "відповідь, reply_serial 7")
    ev(LANES[1], LANES[0], 330, "відповідь, reply_serial 7")

    g.append(line(60, 375, W - 60, 375, color=MUTED, sw=1.0, dash="3 5"))

    ev(LANES[2], LANES[1], 425, "сигнал StateChanged")
    ev(LANES[1], LANES[0], 480, "доставлено: є правило")
    ev(LANES[1], LANES[3], 535, "підписки немає — не доставлено",
       dashed=True, anchor="end")

    return render(os.path.join(IMG, 'call-and-signal.svg'), W, H, *g)


def fig_bus_lineage():
    """Родовід шини: від двох стільничних брокерів до типового брокера в просторі користувача."""
    W, H = 1240, 470
    g = []

    AX = 236  # вісь часу
    EVENTS = [
        ("2000", "DCOP у KDE 2\nповерх ICE з X11"),
        ("2002", "старт D-Bus\nна freedesktop.org"),
        ("2006", "версія 1.0:\nпротокол заморожено"),
        ("2008", "KDE 4 без DCOP,\nGNOME 2.22 без Bonobo"),
        ("2014", "kdbus показано\nпублічно"),
        ("2015", "ядро відмовило,\nдалі — bus1"),
        ("2017", "dbus-broker:\nшвидкість без ядра"),
        ("2019 · 2024", "типовий у Fedora 30,\nпотім в Arch"),
    ]

    g.append(text(W / 2, 34, "родовід шини повідомлень стільниці", size=16, bold=True))

    BW, BH = 138, 78
    x0, step = 42, (W - 84 - BW) / (len(EVENTS) - 1)
    for i, (year, label) in enumerate(EVENTS):
        cx = x0 + step * i + BW / 2
        above = (i % 2 == 0)
        by = AX - 62 - BH if above else AX + 62
        fill = "#fdecea" if i in (4, 5) else FILL
        stroke = POS if i in (4, 5) else LINE
        g.append(fitbox(cx - BW / 2, by, BW, BH, label, size=12,
                        fill=fill, stroke=stroke))
        y1 = (by + BH) if above else (AX + 22)
        y2 = (AX - 22) if above else by
        g.append(line(cx, y1, cx, y2, color=MUTED, sw=1.0))
        g.append(circle(cx, AX, 6, fill=INK, stroke=INK))
        g.append(text(cx, AX + (34 if above else -22), year, size=13, bold=True))

    g.append(line(20, AX, W - 20, AX, color=INK, sw=2.0))

    return render(os.path.join(IMG, 'bus-lineage.svg'), W, H, *g)


def fig_vtable_to_bus():
    """Таблиця vtable у коді проти того, що після реєстрації видно на шині."""
    W, H = 1180, 540
    g = []

    g.append(text(W / 2, 34,
                  "одна таблиця — і на шині з'являється більше, ніж у ній записано",
                  size=16, bold=True))

    LX, LW = 50, 350
    RX, RW = 770, 360
    ROWS = [94, 186, 278]
    BH = 76

    g.append(text(LX + LW / 2, 78, "що ви пишете в C", size=14, bold=True))
    g.append(text(RX + RW / 2, 78, "що бачить будь-який клієнт і busctl",
                  size=14, bold=True))
    g.append(text(585, 80, "sd_bus_add_object_vtable()", size=13, color=MUTED))

    LEFT = [
        "SD_BUS_METHOD_WITH_ARGS(\"Add\")\n→ обробник method_add",
        "SD_BUS_PROPERTY(\"Value\", \"x\")\n→ читач prop_value",
        "SD_BUS_SIGNAL_WITH_ARGS(\"Threshold\")\n→ sd_bus_emit_signal у коді",
    ]
    RIGHT = [
        "виклик Add\nаргументи звірено із сигнатурою",
        "Properties.Get і GetAll → Value\nPropertiesChanged після зміни",
        "сигнал Threshold\nдоходить лише до підписаних",
    ]

    for i, y in enumerate(ROWS):
        g.append(fitbox(LX, y, LW, BH, LEFT[i], size=13))
        g.append(fitbox(RX, y, RW, BH, RIGHT[i], size=13,
                        fill="#eef6ef", stroke=FIELD))
        g.append(arrow(LX + LW + 6, y + BH / 2, RX - 6, y + BH / 2))

    g.append(line(585, 362, 585, 396, color=MUTED, sw=1.2, dash="5 5"))
    g.append(text(W / 2, 412, "і ще це — не написавши жодного рядка",
                  size=14, bold=True))

    FREE = [
        "Introspectable.Introspect\nопис об'єкта як XML",
        "Peer.Ping\nвідповідає бібліотека",
        "sd_bus_error\nокремий тип повідомлення",
        "прапорці vtable\nхто має право викликати",
    ]
    for i, x in enumerate((40, 320, 600, 880)):
        g.append(fitbox(x, 430, 260, 70, FREE[i], size=12,
                        fill="#fdecea", stroke=POS))

    return render(os.path.join(IMG, 'vtable-to-bus.svg'), W, H, *g)


if __name__ == '__main__':
    for f in (fig_mesh_vs_star, fig_message_address, fig_call_and_signal,
              fig_bus_lineage, fig_vtable_to_bus):
        print(f())
