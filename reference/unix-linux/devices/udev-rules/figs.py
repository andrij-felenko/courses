# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eef0f3"


def box(x, y, w, h, lines, fill=FILL, stroke=LINE, size=14, bold=False, sw=1.6):
    """Рамка заданого розміру з багаторядковим текстом усередині."""
    out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=8)]
    if isinstance(lines, str):
        lines = lines.split("\n")
    cy = y + h / 2 - (len(lines) - 1) * size * 1.35 / 2 + size * 0.35
    out.append(mtext(x + w / 2, cy, lines, size=size, bold=bold))
    return out


# ── 1. Шлях події: що робить ядро, а що вже правила ─────────────────────────
def fig_event_path():
    W, H = 1320, 800
    p = []

    p += box(460, 24, 400, 52, "драйвер підхопив нове залізо",
             size=16, bold=True, fill=GREY_FILL)

    kernel = [
        (30, "тека в sysfs\n/sys/devices/…/ttyUSB0\nатрибути й ланцюг предків", BLUE_FILL),
        (480, "вузол у /dev (devtmpfs)\nttyUSB0   root:root   0600", GREEN_FILL),
        (930, "повідомлення uevent\nnetlink, широкомовно\nACTION  DEVPATH  MAJOR  MINOR", RED_FILL),
    ]
    for x0, txt, fill in kernel:
        p += box(x0, 150, 360, 106, txt, size=13, fill=fill)
        p.append(arrow(660, 78, x0 + 180, 146))

    p.append(text(660, 300, "усе вище робить ядро саме · усе нижче — звичайна програма",
                  size=13, color=MUTED, italic=True))
    p.append(line(20, 322, 1300, 322, color=MUTED, sw=1.4, dash="9 7"))

    p += box(420, 360, 480, 88,
             "systemd-udevd\nвластивості події + атрибути з sysfs\nпо всьому ланцюгу предків",
             size=13, bold=False, fill=WARM_FILL)
    p.append(arrow(1110, 258, 830, 356))
    p.append(arrow(210, 258, 490, 356))

    p += box(460, 494, 400, 56, "набір правил", size=15, bold=True, fill=GREY_FILL)
    p.append(arrow(660, 448, 660, 490))

    res = [
        (20, "додаткове ім'я\n/dev/laser → ttyUSB0"),
        (350, "власник, група, режим\nroot:dialout   0660"),
        (680, "властивості в базі\n/run/udev"),
        (1010, "позначки й RUN\nпередача службі"),
    ]
    for x0, txt in res:
        p += box(x0, 610, 290, 88, txt, size=13, fill="#ffffff", stroke=MUTED, sw=1.2)
        p.append(arrow(660, 550, x0 + 145, 606))

    p.append(text(660, 752, "вузол уже існував — правило його не створює, а виправляє",
                  size=14, color=MUTED, italic=True))

    render(os.path.join(IMG, 'event-path.svg'), W, H, *p)


# ── 2. Ланцюг предків у sysfs: де лежать прикмети ───────────────────────────
def fig_parent_chain():
    W, H = 1240, 760
    p = []

    p.append(text(620, 30, "ланцюг тек у sysfs — від контролера шини вниз до об'єкта події",
                  size=14, color=MUTED, italic=True))

    chain = [
        ("0000:00:14.0", "підсистема pci\nконтролер USB", GREY_FILL),
        ("usb1", "підсистема usb\nкореневий концентратор", GREY_FILL),
        ("1-2", "idVendor    0403\nidProduct   6001\nserial      A6008isP", WARM_FILL),
        ("1-2:1.0", "інтерфейс USB\nbInterfaceNumber  00", GREY_FILL),
        ("ttyUSB0", "драйвер ftdi_sio", GREY_FILL),
        ("tty/ttyUSB0", "підсистема tty\ndev  188:0", BLUE_FILL),
    ]

    ys = []
    y = 60
    for name, attrs, fill in chain:
        lines = attrs.split("\n")
        h = 46 + (len(lines) - 1) * 22
        p += box(340, y, 260, h, name, size=15, bold=True, fill=fill)
        p += box(640, y, 400, h, lines, size=13, fill="#ffffff", stroke=MUTED, sw=1.2)
        ys.append((y, h))
        y += h + 40
    for i in range(len(ys) - 1):
        y0, h0 = ys[i]
        p.append(arrow(470, y0 + h0, 470, ys[i + 1][0] - 4))

    top_y = ys[0][0]
    bot_y = ys[-2][0] + ys[-2][1]
    leaf_y, leaf_h = ys[-1]

    p.append(line(300, top_y, 300, bot_y, color=WARM_FILL and "#b8860b", sw=2.4))
    p.append(line(300, top_y, 316, top_y, color="#b8860b", sw=2.4))
    p.append(line(300, bot_y, 316, bot_y, color="#b8860b", sw=2.4))

    p += box(20, 150, 250, 118,
             "ATTRS{…}  KERNELS\nSUBSYSTEMS  DRIVERS\nбудь-який предок —\nале в одному правилі\nусі на ОДНОМУ",
             size=12, fill=WARM_FILL, stroke="#b8860b", sw=1.6)
    p.append(arrow(272, 209, 296, 209, color="#b8860b"))

    p += box(20, 560, 250, 76,
             "ATTR{…}  KERNEL\nSUBSYSTEM  DRIVER\nтільки сам об'єкт",
             size=12, fill=BLUE_FILL, stroke=NEG, sw=1.6)
    p.append(arrow(272, leaf_y + leaf_h / 2, 334, leaf_y + leaf_h / 2, color=NEG))

    p.append(text(620, 726, "подія приходить про листок, а серійний номер лежить на предкові",
                  size=14, color=MUTED, italic=True))

    render(os.path.join(IMG, 'parent-chain.svg'), W, H, *p)


# ── 3. Три теки правил: порядок за іменем, перекриття за текою ──────────────
def fig_rule_order():
    W, H = 1300, 760
    p = []

    cols = [
        (40, "/usr/lib/udev/rules.d\nпринесли пакунки", BLUE_FILL,
         ["60-persistent-storage.rules", "70-uaccess.rules", "99-systemd.rules"]),
        (450, "/run/udev/rules.d\nзгенеровано на льоту", GREEN_FILL,
         ["80-net-setup-link.rules"]),
        (860, "/etc/udev/rules.d\nнаписав адміністратор", RED_FILL,
         ["70-uaccess.rules", "99-local.rules"]),
    ]

    tails = []
    for x0, head, fill, files in cols:
        p += box(x0, 24, 380, 58, head.split("\n"), size=14, bold=True, fill=fill)
        y = 104
        for f in files:
            p += box(x0 + 20, y, 340, 40, f, size=12, fill="#ffffff", stroke=MUTED, sw=1.2)
            y += 52
        tails.append((x0 + 190, y - 12))

    PX, PY, PW, PH = 150, 400, 1000, 268
    p.append(rect(PX, PY, PW, PH, fill=GREY_FILL, stroke=LINE, sw=1.6, rx=10))
    p.append(text(PX + PW / 2, PY + 34, "єдиний список, відсортований за ІМЕНЕМ файлу",
                  size=15, bold=True))

    for cx, cy in tails:
        p.append(arrow(cx, cy, PX + PW / 2, PY - 6))

    rows = [
        "60-persistent-storage.rules   ·   з /usr/lib",
        "70-uaccess.rules   ·   з /etc — однойменний з /usr/lib не читається",
        "80-net-setup-link.rules   ·   з /run",
        "99-local.rules   ·   з /etc",
        "99-systemd.rules   ·   з /usr/lib",
    ]
    ry = PY + 54
    for r in rows:
        p.append(fitbox(PX + 24, ry, PW - 48, 36, r, size=13,
                        fill="#ffffff", stroke=MUTED, sw=1.1))
        ry += 42

    p.append(text(PX + PW / 2, 712,
                  "перебір не зупиняється на першому збігові — проходять усі правила",
                  size=14, color=MUTED, italic=True))

    render(os.path.join(IMG, 'rule-order.svg'), W, H, *p)


# ── 4. Три епохи /dev: де саме народжується вузол ───────────────────────────
def fig_dev_epochs():
    W, H = 1300, 780
    p = []

    LX, LW = 40, 250          # колонка з назвою епохи
    KX, KW = 330, 420         # ядро
    UX, UW = 810, 450         # простір користувача

    p.append(text(KX + KW / 2, 70, "ядро", size=17, bold=True))
    p.append(text(UX + UW / 2, 70, "простір користувача", size=17, bold=True))
    p.append(line(KX - 40, 92, UX + UW, 92, color=MUTED, sw=1.2))

    rows = [
        (140, GREY_FILL,
         ["статичний /dev", "до 2000"],
         ["вузлів не створює:", "лише роздає номери"],
         ["MAKEDEV робить тисячі", "вузлів наперед, один раз"]),
        (350, RED_FILL,
         ["devfs", "2000 — 2006"],
         ["сам створює вузли", "і сам дає їм імена"],
         ["devfsd доганяє події:", "права, посилання, гонки"]),
        (560, GREEN_FILL,
         ["udev + devtmpfs", "з 2003 / з 2009"],
         ["devtmpfs: голий вузол", "із типовим ім'ям"],
         ["udev: ім'я, права,", "посилання — за правилами"]),
    ]

    for y, fill, label, kern, user in rows:
        p += box(LX, y, LW, 130, label, fill="#ffffff", stroke=MUTED,
                 size=15, bold=True, sw=1.2)
        p += box(KX, y, KW, 130, kern, fill=fill, size=15)
        p += box(UX, y, UW, 130, user, fill=fill, size=15)
        p.append(arrow(KX + KW + 12, y + 65, UX - 12, y + 65, color=MUTED))

    p.append(text((KX + KW + UX) / 2, 340,
                  "подія летить у порожнечу", size=13, color=MUTED, italic=True))
    p.append(text((KX + KW + UX) / 2, 550,
                  "вузол уже є, коли по нього приходять",
                  size=13, color=MUTED, italic=True))

    p.append(text(W / 2, 730,
                  "межа рухалася двічі: усередину ядра — і назад назовні",
                  size=15, color=MUTED, italic=True))

    render(os.path.join(IMG, 'dev-epochs.svg'), W, H, *p)


# ── 5. Хто володіє процесом: RUN проти служби (вставка proj-hotplug-service) ─
def fig_handoff():
    W, H = 1240, 610
    p = []

    BW, GAP, X0 = 250, 44, 40

    def chain(y, label, items, fill, x0=X0):
        p.append(text(x0, y - 14, label, size=15, bold=True, anchor="start"))
        x = x0
        for i, txt in enumerate(items):
            p.append(fitbox(x, y, BW, 96, txt, size=14, fill=fill))
            if i < len(items) - 1:
                p.append(arrow(x + BW + 8, y + 48, x + BW + GAP - 8, y + 48))
            x += BW + GAP

    def note(y, s, color=MUTED):
        p.append(text(W / 2, y, s, size=13, color=color, italic=True))

    chain(56, "як роблять — і чому не працює", [
        "подія add\nпро ttyUSB0",
        "правило:\nRUN+=\"…/agent &\"",
        "агент працює\nусередині події",
        "подію завершено —\nусе, що породив\nробочий процес, убито",
    ], RED_FILL)
    note(178, "ліміт події 180 с   ·   пісочниця без мережі й монтування")

    chain(242, "як передають роботу", [
        "подія add\nпро ttyUSB0",
        "правило:\nTAG+=\"systemd\"\nSYSTEMD_WANTS",
        "подію завершено —\nробочий процес вільний",
        "systemd підняв\nlaser-agent@ttyUSB0\nу власному cgroup",
    ], GREEN_FILL)
    note(364, "агент більше не має стосунку до udev: власний перезапуск, власний журнал")

    chain(428, "і зворотний бік — вийняли шнур", [
        "подія remove",
        "dev-ttyUSB0.device\nстає неактивним",
        "BindsTo= + After=\nзупиняють службу",
    ], BLUE_FILL, x0=(W - (3 * BW + 2 * GAP)) / 2)
    note(550, "зупинку ніхто не програмував — вона випливає з напрямку залежності")

    render(os.path.join(IMG, 'handoff-run-vs-service.svg'), W, H, *p)


# ── 6. Звідки береться кожне ім'я (вставка proj-hotplug-service) ─────────────
def fig_unit_naming():
    W, H = 1230, 570
    p = []

    p += box(325, 34, 580, 104, [
        "подія про ttyUSB0",
        "KERNEL == ttyUSB0        (у правилі — %k)",
        "DEVNAME == /dev/ttyUSB0",
    ], size=14, fill=GREY_FILL)

    cols = [
        (40, 340, GREEN_FILL,
         ["шлях у /dev,", "екранований systemd"],
         ["dev-ttyUSB0.device", "юніт пристрою"]),
        (430, 360, BLUE_FILL,
         ["%k, підставлений", "правилом у SYSTEMD_WANTS"],
         ["laser-agent@ttyUSB0.service", "примірник служби"]),
        (830, 360, RED_FILL,
         ["порожній примірник:", "laser-agent@.service"],
         ["примірник зі ШЛЯХУ sysfs", "sys-devices-…-1\\x2d2-…"]),
    ]

    for x, w, fill, head, tail in cols:
        p.append(arrow(615, 144, x + w / 2, 196))
        p += box(x, 200, w, 84, head, size=13, fill="#ffffff",
                 stroke=MUTED, sw=1.2)
        p.append(arrow(x + w / 2, 292, x + w / 2, 336))
        p += box(x, 340, w, 84, tail, size=14, fill=fill, bold=True)

    p.append(fitbox(40, 452, 750, 62,
                    "у юніті: BindsTo=dev-%i.device   ·   %i — примірник як є",
                    size=15, fill=GREEN_FILL))
    p.append(fitbox(830, 452, 360, 62,
                    "%I розгорнув би «-» у «/»",
                    size=15, fill=RED_FILL))

    render(os.path.join(IMG, 'unit-naming.svg'), W, H, *p)


fig_event_path()
fig_parent_chain()
fig_rule_order()
fig_dev_epochs()
fig_handoff()
fig_unit_naming()
print("ok")
