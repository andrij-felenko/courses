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
GREY_FILL = "#eceff1"


def box(cx, cy, lines, **kw):
    """textbox + межі рамки (x0, x1, y0, y1)."""
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Стани служби й події, що їх перемикають ──────────────────────────────
def fig_states():
    W, H = 1360, 690
    p = []

    b1, b1l, b1r, b1t, b1b = box(180, 180, "inactive\nне запущена", size=15, bold=True, fill=GREY_FILL)
    b2, b2l, b2r, b2t, b2b = box(520, 180, "activating\nзапускається", size=15, bold=True, fill=WARM_FILL)
    b3, b3l, b3r, b3t, b3b = box(880, 180, "active\nпрацює", size=15, bold=True, fill=GREEN_FILL)
    b4, b4l, b4r, b4t, b4b = box(1210, 180, "deactivating\nзупиняється", size=15, bold=True, fill=WARM_FILL)
    b5, b5l, b5r, b5t, b5b = box(880, 500, "failed\nвпала", size=15, bold=True, fill=RED_FILL)
    p += [b1, b2, b3, b4, b5]

    # верхній ряд переходів
    p.append(arrow(b1r + 10, 180, b2l - 10, 180))
    p.append(text((b1r + b2l) / 2, 132, "systemctl start", size=13, color=MUTED))

    p.append(arrow(b2r + 10, 180, b3l - 10, 180))
    p.append(text((b2r + b3l) / 2, 132, "ознака готовності за Type=", size=13, color=MUTED))

    p.append(arrow(b3r + 10, 180, b4l - 10, 180))
    p.append(text((b3r + b4l) / 2, 132, "зупинку наказали", size=13, color=MUTED))

    # повернення deactivating → inactive
    p.append(line(1210, b4b, 1210, 320))
    p.append(line(1210, 320, 180, 320))
    p.append(arrow(180, 320, 180, b1b + 6))
    p.append(text(700, 345, "cgroup спорожніла", size=13, color=MUTED))

    # active → failed
    p.append(arrow(880, b3b + 6, 880, b5t - 6))
    p.append(text(898, 390, "процес завершився невдало", size=13, color=POS, anchor="start"))
    p.append(text(898, 412, "або промовчав сторожовий таймер", size=13, color=POS, anchor="start"))

    # activating → failed
    p.append(line(520, b2b, 520, 500))
    p.append(arrow(520, 500, b5l - 10, 500))
    p.append(text(676, 532, "збій запуску або сплив таймаут", size=13, color=POS))

    # failed → activating (перезапуск)
    p.append(line(880, b5b, 880, 612))
    p.append(line(880, 612, 470, 612))
    p.append(arrow(470, 612, 470, b2b + 6))
    p.append(text(700, 640, "перезапуск за політикою після паузи", size=13, color=FIELD))

    render(os.path.join(IMG, 'states.svg'), W, H, *p,
           title="Стани служби й переходи між ними")


# ── 2. Де на шляху служби менеджер оголошує «active» ────────────────────────
def fig_readiness():
    W, H = 1300, 560
    p = []
    ax = 170

    p.append(text(750, 90, "що робить сама служба", size=14, bold=True))
    p.append(arrow(300, ax, 1210, ax))

    events = [(340, "fork"), (470, "execve"), (660, "прочитала конфіг"),
              (880, "bind + listen"), (1080, "готова відповідати")]
    for x, lbl in events:
        p.append(line(x, ax - 10, x, ax + 10, color=INK, sw=2))
        p.append(text(x, 130, lbl, size=12, color=MUTED))

    rows = [(270, "Type=simple", 340),
            (360, "Type=forking", 990),
            (450, "Type=notify", 1080)]
    for y, name, mx in rows:
        p.append(text(280, y + 5, name, size=14, bold=True, anchor="end"))
        p.append(line(300, y, mx, y, color=MUTED, sw=2))
        if mx < 1080:
            p.append(line(mx, y, 1080, y, color=POS, sw=6))
        p.append(line(1080, y, 1200, y, color=FIELD, sw=6))
        p.append(line(mx, ax + 12, mx, y - 10, color=MUTED, sw=1.2, dash="5 5"))
        p.append(circle(mx, y, 7, fill=BG, stroke=INK, sw=2))
        p.append(text(mx, y + 30, "«active»", size=12, bold=True))

    p.append(text(750, 525, "червоне — служба вже «active», але ще не відповідає",
                  size=13, color=POS))

    render(os.path.join(IMG, 'readiness.svg'), W, H, *p,
           title="Момент оголошення готовності за різних Type=")


# ── 3. Послідовність зупинки в часі ─────────────────────────────────────────
def fig_stop_sequence():
    W, H = 1280, 540
    p = []
    ax = 120

    p.append(arrow(260, ax, 1210, ax))
    marks = [(320, "SIGTERM усій групі"), (620, "більшість вийшла сама"),
             (900, "сплив TimeoutStopSec"), (1050, "SIGKILL решті")]
    for x, lbl in marks:
        p.append(line(x, ax - 10, x, ax + 10, color=INK, sw=2))
        p.append(text(x, 80, lbl, size=13, color=MUTED))

    lanes = [(210, "головний процес", 560, None),
             (290, "робітник", 640, None),
             (370, "помічник, що завис", 1050, 900)]
    for y, name, end, hot in lanes:
        p.append(text(250, y + 5, name, size=13, anchor="end"))
        p.append(rect(260, y - 13, end - 260, 26, fill=BLUE_FILL, stroke=MUTED, sw=1.2, rx=4))
        if hot:
            p.append(rect(hot, y - 13, end - hot, 26, fill=RED_FILL, stroke=POS, sw=1.5, rx=4))

    for x in (320, 900, 1050):
        p.append(line(x, ax + 12, x, 392, color=MUTED, sw=1.2, dash="5 5"))

    p.append(text(1150, 418, "група порожня → inactive", size=13, color=FIELD, anchor="end"))
    p.append(text(620, 474, "юніт лишається в deactivating, доки в групі є хоч один процес",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'stop-sequence.svg'), W, H, *p,
           title="Часова смуга зупинки служби")


# ── 4. Рішення після завершення служби ──────────────────────────────────────
def fig_restart_decision():
    W, H = 1300, 790
    p = []

    n1, n1l, n1r, n1t, n1b = box(560, 70, "головний процес завершився", size=15, bold=True, fill=GREY_FILL)
    p.append(n1)

    c1, c1l, c1r, c1t, c1b = box(
        330, 185,
        "чисто\nкод 0, SIGTERM / SIGINT / SIGHUP / SIGPIPE,\nоголошені успішними коди",
        size=13, fill=GREEN_FILL)
    c2, c2l, c2r, c2t, c2b = box(
        800, 185,
        "невдало\nінший код, необроблений сигнал, таймаут,\nсторожовий пес, брак пам'яті",
        size=13, fill=RED_FILL)
    p += [c1, c2]
    p.append(arrow(500, n1b + 4, 380, c1t - 6))
    p.append(arrow(620, n1b + 4, 750, c2t - 6))

    n3, n3l, n3r, n3t, n3b = box(560, 290, "Restart= ловить цей клас?", size=15, bold=True, fill=BLUE_FILL)
    p.append(n3)
    p.append(arrow(380, c1b + 4, 500, n3t - 6))
    p.append(arrow(750, c2b + 4, 620, n3t - 6))

    stop, sl, sr, st, sb = box(1000, 290, "нічого не робити:\nстан inactive", size=13, fill=GREY_FILL)
    p.append(stop)
    p.append(arrow(n3r + 8, 290, sl - 8, 290))
    p.append(text((n3r + sl) / 2, 272, "ні", size=13, color=MUTED))

    n5, n5l, n5r, n5t, n5b = box(560, 390, "серед заборонених кодів виходу?", size=15, bold=True, fill=BLUE_FILL)
    p.append(n5)
    p.append(arrow(560, n3b + 4, 560, n5t - 6))
    p.append(text(576, 345, "так", size=13, color=MUTED, anchor="start"))

    n7, n7l, n7r, n7t, n7b = box(560, 500, "уклалися в ліміт спроб за вікном?", size=15, bold=True, fill=BLUE_FILL)
    p.append(n7)
    p.append(arrow(560, n5b + 4, 560, n7t - 6))
    p.append(text(576, 455, "ні", size=13, color=MUTED, anchor="start"))

    fl, fll, flr, flt, flb = box(1000, 445, "failed\nстан-глухий кут", size=13, bold=True, fill=RED_FILL)
    p.append(fl)
    p.append(line(n5r + 8, 390, 1000, 390))
    p.append(arrow(1000, 390, 1000, flt - 6))
    p.append(text(860, 372, "так", size=13, color=POS))
    p.append(line(n7r + 8, 500, 1000, 500))
    p.append(arrow(1000, 500, 1000, flb + 6))
    p.append(text(860, 522, "ні", size=13, color=POS))

    n9, n9l, n9r, n9t, n9b = box(560, 600, "пауза RestartSec", size=15, bold=True, fill=WARM_FILL)
    p.append(n9)
    p.append(arrow(560, n7b + 4, 560, n9t - 6))
    p.append(text(576, 565, "так", size=13, color=MUTED, anchor="start"))

    n10, _, _, n10t, _ = box(560, 700, "activating — знову запускається", size=15, bold=True, fill=GREEN_FILL)
    p.append(n10)
    p.append(arrow(560, n9b + 4, 560, n10t - 6))

    render(os.path.join(IMG, 'restart-decision.svg'), W, H, *p,
           title="Рішення про перезапуск після завершення служби")


# ── 5. Звідки в systemd взялися його ідеї ───────────────────────────────────
def fig_idea_lineage():
    W, H = 1440, 600
    p = []

    b1, b1l, b1r, b1t, b1b = box(
        290, 110,
        "daemontools · 0.76 (2001)\nДаніел Дж. Бернштайн\nнаглядач лишається батьком",
        size=15, bold=True, fill=GREEN_FILL)
    b2, b2l, b2r, b2t, b2b = box(
        290, 310,
        "launchd · 2005\nApple, Дейв Зажицький\nсокет відкриває наглядач",
        size=15, bold=True, fill=BLUE_FILL)
    b3, b3l, b3r, b3t, b3b = box(
        290, 505,
        "Upstart · 2006\nCanonical, Скотт Дж. Ремнант\nсистема реагує на події",
        size=15, bold=True, fill=WARM_FILL)
    p += [b1, b2, b3]

    m, ml, mr, mt, mb = box(
        800, 110,
        "runit · 2004 · Ґеррит Папе\ns6 · 2010-ті · Лоран Берко\nготовність — через дескриптор",
        size=15, bold=True, fill=GREEN_FILL)
    p.append(m)

    sd, sl, sr, st, sb = box(
        1195, 310,
        "systemd · 2010\nЛеннарт Поттерінг, Кай Зіверс\ncgroup замість здогадів",
        size=15, bold=True, fill=GREY_FILL)
    p.append(sd)

    p.append(arrow(b1r + 10, 110, ml - 10, 110))
    p.append(arrow(mr + 10, 110, sl - 10, 270))
    p.append(arrow(b2r + 10, 310, sl - 10, 310))

    p.append(line(b3r + 10, 505, 1195, 505))
    p.append(arrow(1195, 505, 1195, sb + 8))
    p.append(text(830, 482, "як застереження, не як спадок", size=13, color=MUTED))

    render(os.path.join(IMG, 'idea-lineage.svg'), W, H, *p,
           title="Звідки в systemd взялися його головні ідеї")


if __name__ == '__main__':
    fig_states()
    fig_readiness()
    fig_stop_sequence()
    fig_restart_decision()
    fig_idea_lineage()
    print("ok")
