# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
RED = "#fdecea"
WARM = "#fff6e5"
GREY = "#eceff1"


def tb(cx, cy, lines, **kw):
    """textbox + межі рамки (x0, x1, y0, y1)."""
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Реєстрація сеансу і зворотний запит через cgroup ─────────────────────
def fig_session_registration():
    W, H = 1440, 760
    p = []

    p.append(text(W / 2, 52, "Реєстрація йде вниз, а відповідь про належність читається вгору",
                  size=18, bold=True))

    # ліва колонка — ланцюжок реєстрації
    LX = 330
    f, _, _, _, y1 = tb(LX, 140, "програма входу\nlogin · sshd · менеджер входу",
                        size=15, fill=BLUE, pad=14)
    p.append(f)

    f, _, _, y0, y1b = tb(LX, 268, "стек PAM: секція session", size=15, fill=GREY, pad=14)
    p.append(f)
    p.append(arrow(LX, y1, LX, y0))

    f, _, _, y0, y1c = tb(LX, 388, "модуль pam_systemd", size=15, fill=GREY, pad=14)
    p.append(f)
    p.append(arrow(LX, y1b, LX, y0))

    # центр — logind
    CX = 830
    f, cx0, cx1, cy0, cy1 = tb(CX, 388, "logind", size=17, bold=True, fill=GREEN, pad=18)
    p.append(f)

    p.append(arrow(LX + 140, 388, cx0 - 8, 388))
    p.append(text((LX + 140 + cx0) / 2, 366, "CreateSession(…)", size=14, color=MUTED))

    # права колонка — що заводиться
    RX = 1210
    f, rx0, _, _, ry1 = tb(RX, 205, "session-3.scope\nусі процеси сеансу", size=15, fill=WARM, pad=14)
    p.append(f)
    f, rx0b, _, ry0b, ry1b = tb(RX, 330, "user-1000.slice", size=15, fill=WARM, pad=14)
    p.append(f)
    f, rx0c, _, ry0c, _ = tb(RX, 452, "/run/user/1000\nXDG_RUNTIME_DIR", size=15, fill=WARM, pad=14)
    p.append(f)

    p.append(arrow(cx1 + 8, 360, rx0 - 8, 225))
    p.append(arrow(cx1 + 8, 388, rx0b - 8, 330))
    p.append(arrow(cx1 + 8, 416, rx0c - 8, 440))

    # нижня смуга — зворотний запит
    p.append(line(90, 560, W - 90, 560, color=MUTED, sw=1.2, dash="7,7"))

    f, qx0, qx1, qy0, _ = tb(300, 660, "довільний процес", size=15, fill=BLUE, pad=14)
    p.append(f)
    f, ax0, ax1, ay0, _ = tb(880, 660, "/proc/PID/cgroup", size=15, fill=GREY, pad=14)
    p.append(f)
    f, sx0, _, _, _ = tb(1250, 660, "сеанс 3\nкористувач 1000", size=15, fill=GREEN, pad=14)
    p.append(f)

    p.append(arrow(qx1 + 8, 660, ax0 - 8, 660))
    p.append(arrow(ax1 + 8, 660, sx0 - 8, 660))
    p.append(text(730, 606, "питає ядро, а не реєстр", size=14, color=MUTED))

    render(os.path.join(IMG, "session-registration.svg"), W, H, *p,
           title="Реєстрація сеансу і зворотний запит через cgroup")


# ── 2. Місця, сеанси й сеанси без місця ─────────────────────────────────────
def fig_seats_and_sessions():
    W, H = 1480, 800
    p = []

    p.append(text(W / 2, 50, "Активність визначається всередині місця", size=18, bold=True))

    def seat(x0, x1, top, name, devices, sessions):
        out = []
        out.append(rect(x0, top, x1 - x0, 430, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
        cx = (x0 + x1) / 2
        out.append(text(cx, top + 36, name, size=17, bold=True))
        f, _, _, _, dy1 = tb(cx, top + 108, devices, size=14, fill=GREY, pad=12)
        out.append(f)
        n = len(sessions)
        step = (x1 - x0 - 90) / n
        for i, (label, state) in enumerate(sessions):
            sx = x0 + 45 + step * (i + 0.5)
            fill = GREEN if state == "active" else BLUE
            f, _, _, sy0, _ = tb(sx, top + 300, label + "\n" + state, size=14, fill=fill, pad=12)
            out.append(f)
            out.append(line(cx, dy1, sx, sy0, color=MUTED, sw=1.2,
                            dash=None if state == "active" else "5,5"))
        return out

    p += seat(90, 700, 96, "seat0",
              "відеокарта · клавіатура · миша",
              [("сеанс 1", "online"), ("сеанс 2", "active"), ("сеанс 4", "online")])

    p += seat(780, 1390, 96, "seat1",
              "друга відеокарта · клавіатура · миша",
              [("сеанс 5", "active"), ("сеанс 6", "online")])

    # сеанси без місця
    p.append(rect(90, 588, 1300, 158, fill="#fdfaf5", stroke=MUTED, sw=1.4, rx=10))
    p.append(text(740, 628, "сеанси без місця — прив'язати нема до чого", size=16, bold=True))
    f, _, _, _, _ = tb(430, 700, "сеанс 7 · ssh · online", size=14, fill=WARM, pad=12)
    p.append(f)
    f, _, _, _, _ = tb(1050, 700, "сеанс 8 · ssh · online", size=14, fill=WARM, pad=12)
    p.append(f)

    render(os.path.join(IMG, "seats-and-sessions.svg"), W, H, *p,
           title="Місця, сеанси й сеанси без місця")


# ── 3. Віддача дескриптора й відкликання на перемиканні ─────────────────────
def fig_device_handover():
    W, H = 1480, 700
    p = []

    p.append(text(W / 2, 50, "Копія дескриптора лишається в logind — тому її можна відкликати",
                  size=18, bold=True))

    def panel(x0, x1, title, live_left):
        out = []
        cx = (x0 + x1) / 2
        out.append(rect(x0, 92, x1 - x0, 520, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
        out.append(text(cx, 132, title, size=16, bold=True))

        f, _, _, _, ky1 = tb(cx, 200, "клавіатура /dev/input/event3", size=14, fill=GREY, pad=12)
        out.append(f)

        f, lx0, lx1, ly0, ly1 = tb(cx, 300, "logind тримає копію", size=15, fill=GREEN, pad=13)
        out.append(f)
        out.append(line(cx, ky1, cx, ly0, color=MUTED, sw=1.2))

        ax, bx = x0 + 150, x1 - 150
        a_fill = GREEN if live_left else RED
        b_fill = RED if live_left else GREEN
        a_txt = "сеанс 2 · active\nдескриптор читає" if live_left else "сеанс 2 · online\nENODEV"
        b_txt = "сеанс 5 · online\nENODEV" if live_left else "сеанс 5 · active\nдескриптор читає"

        f, _, _, ay0, _ = tb(ax, 470, a_txt, size=14, fill=a_fill, pad=13)
        out.append(f)
        f, _, _, by0, _ = tb(bx, 470, b_txt, size=14, fill=b_fill, pad=13)
        out.append(f)

        out.append(line(lx0 + 20, ly1, ax, ay0, color=LINE if live_left else POS,
                        sw=1.6, dash=None if live_left else "6,6"))
        out.append(line(lx1 - 20, ly1, bx, by0, color=POS if live_left else LINE,
                        sw=1.6, dash="6,6" if live_left else None))
        return out

    p += panel(70, 720, "до перемикання", True)
    p += panel(760, 1410, "після EVIOCREVOKE на копії", False)

    p.append(text(740, 660, "суцільна лінія — робочий дескриптор, пунктир — відкликаний",
                  size=14, color=MUTED))

    render(os.path.join(IMG, "device-handover.svg"), W, H, *p,
           title="Віддача дескриптора й відкликання на перемиканні")


# ── 4. Три покоління обліку входів (для історичної вставки) ────────────────
def fig_accounting_generations():
    W, H = 1460, 640
    p = []

    p.append(text(W / 2, 46, "Три покоління обліку входів: що змінювалося з кожним",
                  size=18, bold=True))

    COLS = [
        (450, "utmp / wtmp\nз 1979 року", GREY,
         ["login(1) та init(8)\nпишуть добровільно",
          "лише ім'я термінала",
          "нічого: це файл"]),
        (830, "ConsoleKit\nз 2006 року", WARM,
         ["демон бачить вхід\nі знає активну консоль",
          "вузли активної консолі\nчерез udev-acl",
          "переставляє ACL\nна вузлах пристроїв"]),
        (1230, "systemd-logind\nз 2011 року", GREEN,
         ["pam_systemd у стеку входу,\nналежність веде ядро",
          "місце зібране\nз udev-міток",
          "видає дескриптор\nі відкликає його"]),
    ]
    ROWS = [(210, "хто веде запис"), (350, "що знає про залізо"), (490, "що робить у відповідь")]

    for y, label in ROWS:
        p.append(text(150, y + 5, label, size=15, bold=True, color=MUTED))

    for cx, head, col, cells in COLS:
        p.append(textbox(cx, 120, head, size=16, bold=True, fill=col, pad=14)[0])
        for (y, _), body in zip(ROWS, cells):
            p.append(textbox(cx, y, body, size=14, fill=FILL, pad=14)[0])

    p.append(text(W / 2, 580, "кожен крок міняв обіцянку програм на дію системи",
                  size=14, color=MUTED, italic=True))

    render(os.path.join(IMG, "accounting-generations.svg"), W, H, *p,
           title="Три покоління обліку входів")



# ── Обмін повідомленнями й доля дескриптора (вставка proj) ─────────
def fig_handover_exchange():
    W, H = 1560, 1030
    p = []

    PX, LX = 340, 950          # смуги програми й logind
    FX = 1350                  # смуга долі дескриптора

    f, _, _, _, py1 = tb(PX, 96, "наша програма", size=16, bold=True, fill=BLUE, pad=14)
    p.append(f)
    f, _, _, _, ly1 = tb(LX, 96, "logind", size=16, bold=True, fill=GREEN, pad=14)
    p.append(f)
    f, _, _, _, fy1 = tb(FX, 96, "доля дескриптора", size=15, bold=True, fill=GREY, pad=14)
    p.append(f)

    TOP, BOT = py1 + 20, 970
    p.append(line(PX, TOP, PX, BOT, color=MUTED, sw=1.4, dash="5,7"))
    p.append(line(LX, TOP, LX, BOT, color=MUTED, sw=1.4, dash="5,7"))

    def msg(y, s, to_right=True, color=LINE):
        x1, x2 = (PX + 12, LX - 12) if to_right else (LX - 12, PX + 12)
        p.append(arrow(x1, y, x2, y, color=color, sw=1.8))
        p.append(text((PX + LX) / 2, y - 14, s, size=15, color=color))

    msg(196, "TakeControl(false)")
    msg(268, "TakeDevice(major, minor)")
    msg(344, "fd₁  ·  inactive = false", to_right=False, color=FIELD)

    f, _, _, _, _ = tb(FX, 344, "fd₁ живий\nread() віддає події", size=14, fill=GREEN, pad=12)
    p.append(f)

    f, _, _, _, _ = tb(PX + 200, 420, "read(fd₁) у циклі", size=14, fill=BLUE, pad=11)
    p.append(f)

    msg(510, "PauseDevice(major, minor, «pause»)", to_right=False, color=POS)
    msg(582, "PauseDeviceComplete(major, minor)")

    f, _, _, _, _ = tb(FX, 510, "EVIOCREVOKE\nна копії logind", size=14, fill=RED, pad=12)
    p.append(f)
    f, _, _, _, _ = tb(FX, 646, "fd₁ мертвий назавжди\nread() → ENODEV", size=14, fill=RED, pad=12)
    p.append(f)

    SY = 664
    p.append(line(70, SY, 540, SY, color=MUTED, sw=1.4, dash="8,8"))
    p.append(text(800, SY + 5, "місце перемкнулося на інший сеанс", size=15, color=MUTED))
    p.append(line(1060, SY, 1180, SY, color=MUTED, sw=1.4, dash="8,8"))

    msg(780, "ResumeDevice(major, minor, fd₂)", to_right=False, color=FIELD)

    f, _, _, _, _ = tb(FX, 820, "fd₂ — ІНШЕ відкриття\nвузла, знову живе", size=14, fill=GREEN, pad=12)
    p.append(f)

    f, _, _, _, _ = tb(PX + 220, 852, "close(fd₁);  fd₁ = dup(fd₂)", size=14, fill=BLUE, pad=11)
    p.append(f)

    msg(930, "ReleaseDevice  ·  ReleaseControl")

    render(os.path.join(IMG, "handover-exchange.svg"), W, H, *p,
           title="Обмін по шині й те, що при цьому відбувається з дескриптором")


fig_session_registration()
fig_seats_and_sessions()
fig_device_handover()
fig_accounting_generations()
fig_handover_exchange()
print("ok")
