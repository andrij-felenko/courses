# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

ROOT_F, ROOT_S = "#fdecea", POS
USER_F, USER_S = "#eaf0fd", NEG
AUTH_F, AUTH_S = "#eafaf0", FIELD


def B(cx, cy, s, size=13, pad=12, fill=FILL, stroke=LINE, bold=False, min_w=0):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, fill=fill,
                         stroke=stroke, bold=bold, min_w=min_w)
    return {"f": frag, "cx": cx, "cy": cy, "w": w, "h": h,
            "l": cx - w / 2.0, "r": cx + w / 2.0,
            "t": cy - h / 2.0, "b": cy + h / 2.0}


# ── 1. Петля одного звернення ───────────────────────────────────────────────
def loop():
    W, H = 1060, 660
    a = B(190, 130, "Програма користувача\n(uid 1000, без прав)",
          fill=USER_F, stroke=USER_S)
    b = B(700, 130, "Механізм: служба\nна системній шині\n(працює як root)",
          fill=ROOT_F, stroke=ROOT_S)
    c = B(700, 360, "polkitd\nвирішує, але нічого\nне виконує",
          fill=AUTH_F, stroke=AUTH_S)
    d = B(190, 360, "Агент автентифікації\nу сеансі (uid 1000)",
          fill=USER_F, stroke=USER_S)
    e = B(190, 580, "polkit-agent-helper-1\n(setuid root, стек PAM)",
          fill=ROOT_F, stroke=ROOT_S)

    fr = [a["f"], b["f"], c["f"], d["f"], e["f"]]

    # 1: клієнт → механізм
    fr.append(arrow(a["r"] + 8, 108, b["l"] - 8, 108))
    fr.append(text((a["r"] + b["l"]) / 2, 92, "1. «змонтуй цей диск»", size=13))
    # 7: механізм → клієнт
    fr.append(arrow(b["l"] - 8, 158, a["r"] + 8, 158))
    fr.append(text((a["r"] + b["l"]) / 2, 180, "7. зроблено або відмова", size=13))

    # 2: механізм → polkitd
    fr.append(arrow(b["cx"] - 55, b["b"] + 8, c["cx"] - 55, c["t"] - 8))
    fr.append(text(b["cx"] - 72, 240, "2. чи можна цьому", size=13, anchor="end"))
    fr.append(text(b["cx"] - 72, 260, "суб'єктові дію A?", size=13, anchor="end"))
    # 6: polkitd → механізм
    fr.append(arrow(c["cx"] + 55, c["t"] - 8, b["cx"] + 55, b["b"] + 8))
    fr.append(text(b["cx"] + 72, 240, "6. так / ні /", size=13, anchor="start"))
    fr.append(text(b["cx"] + 72, 260, "спитай пароль", size=13, anchor="start"))

    # 3: polkitd → агент
    fr.append(arrow(c["l"] - 8, 360, d["r"] + 8, 360))
    fr.append(text((d["r"] + c["l"]) / 2, 340, "3. запитай людину", size=13))

    # 4: агент → помічник
    fr.append(arrow(d["cx"], d["b"] + 8, e["cx"], e["t"] - 8))
    fr.append(text(d["cx"] + 22, 480, "4. уведений пароль", size=13, anchor="start"))

    # 5: помічник → polkitd
    fr.append(arrow(e["r"] + 8, e["cy"] - 14, c["cx"] - 20, c["b"] + 10))
    fr.append(text(560, 560, "5. від uid 0: пароль збігся", size=13))

    leg = B(830, 600, "рамка червоним — це працює з правами root",
            size=12, pad=9, fill=ROOT_F, stroke=ROOT_S)
    fr.append(leg["f"])

    render(os.path.join(OUT, "authorization-loop.svg"), W, H, *fr,
           title="Одне звернення: хто в кого що питає")


# ── 2. Як обчислюється відповідь ────────────────────────────────────────────
def funnel():
    W, H = 1020, 640
    n0 = B(490, 95, "Суб'єкт S + ідентифікатор дії A", size=14, bold=True)
    n1 = B(490, 205, "/etc/polkit-1/rules.d/*.rules\nправила адміністратора, за іменем файлу",
           fill=AUTH_F, stroke=AUTH_S)
    n2 = B(490, 320, "/usr/share/polkit-1/rules.d/*.rules\nправила, що прийшли з пакунками",
           fill=AUTH_F, stroke=AUTH_S)
    n3 = B(490, 440, "<defaults> у файлі .policy\nallow_any · allow_inactive · allow_active",
           fill=FILL, stroke=LINE)

    r1 = B(140, 585, "no\nвідмовити", fill=USER_F, stroke=USER_S)
    r2 = B(470, 585, "yes\nвиконати мовчки", fill=USER_F, stroke=USER_S)
    r3 = B(830, 585, "auth_self / auth_admin\nспитати пароль", fill=ROOT_F, stroke=ROOT_S)

    fr = [n0["f"], n1["f"], n2["f"], n3["f"], r1["f"], r2["f"], r3["f"]]
    fr.append(arrow(490, n0["b"] + 6, 490, n1["t"] - 6))
    fr.append(arrow(490, n1["b"] + 6, 490, n2["t"] - 6))
    fr.append(arrow(490, n2["b"] + 6, 490, n3["t"] - 6))
    fr.append(arrow(n3["cx"] - 120, n3["b"] + 6, r1["cx"] + 30, r1["t"] - 6))
    fr.append(arrow(490, n3["b"] + 6, r2["cx"], r2["t"] - 6))
    fr.append(arrow(n3["cx"] + 120, n3["b"] + 6, r3["cx"] - 40, r3["t"] - 6))

    note = B(880, 262, "перше правило,\nяке повернуло\nне null,\nвирішує остаточно",
             size=12, pad=9, fill="#fffbe6", stroke=MUTED)
    fr.append(note["f"])
    fr.append(arrow(n1["r"] + 6, 262, note["l"] - 6, 262, color=MUTED))

    fr.append(text(180, 440, "запасна відповідь,", size=12, color=MUTED, anchor="end"))
    fr.append(text(180, 458, "коли правил не було", size=12, color=MUTED, anchor="end"))

    render(os.path.join(OUT, "decision-funnel.svg"), W, H, *fr,
           title="Звідки береться відповідь на «чи можна»")


# ── 3. Чому номер процесу не є особою ───────────────────────────────────────
def pid_race():
    W, H = 1120, 560
    axis_y = 285
    xs = [140, 350, 560, 770, 980]

    band = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" '
            'fill="#fdecea" stroke="%s" stroke-width="1.5" stroke-dasharray="6 4"/>'
            % (xs[1], 200, xs[4] - xs[1], 62, POS))

    up = [
        (xs[0], "клієнт просить механізм\nвиконати дію"),
        (xs[2], "клієнт завершується,\nномер 4242 звільнено"),
        (xs[4], "polkitd читає /proc/4242\nі бачить чужу особу"),
    ]
    dn = [
        (xs[1], "механізм каже полкітові:\n«суб'єкт — процес 4242»"),
        (xs[3], "ядро видає 4242\nнаступному процесові"),
    ]

    fr = [band, text(605, 240, "вікно гонки", size=14, bold=True, color=POS)]
    fr.append(arrow(80, axis_y, W - 60, axis_y, color=MUTED))
    fr.append(text(W - 60, axis_y + 26, "час", size=13, color=MUTED, anchor="end"))

    for x, s in up:
        bx = B(x, 150, s, size=13, fill=FILL, stroke=LINE)
        fr.append(bx["f"])
        fr.append(line(x, bx["b"] + 4, x, axis_y - 6, color=MUTED, dash="4 4"))
        fr.append(circle(x, axis_y, 6, fill=BG, stroke=INK, sw=2))
    for x, s in dn:
        bx = B(x, 420, s, size=13, fill=FILL, stroke=LINE)
        fr.append(bx["f"])
        fr.append(line(x, axis_y + 6, x, bx["t"] - 4, color=MUTED, dash="4 4"))
        fr.append(circle(x, axis_y, 6, fill=BG, stroke=INK, sw=2))

    fix = B(560, 510, "pidfd закриває вікно: дескриптор указує на сам процес, "
                      "а не на вільний номер", size=13, fill=AUTH_F, stroke=AUTH_S)
    fr.append(fix["f"])

    render(os.path.join(OUT, "pid-race.svg"), W, H, *fr,
           title="Чому номер процесу не годиться як особа")


# ── 4. П'ять файлів механізму й хто їх читає ────────────────────────────────
def mechanism_files():
    W, H = 1120, 700
    fx, rx = 300, 860

    f1 = B(fx, 105, "/usr/share/dbus-1/system.d/\norg.example.Backlight.conf")
    f2 = B(fx, 220, "/usr/share/dbus-1/system-services/\norg.example.Backlight.service")
    f3 = B(fx, 350, "/usr/lib/systemd/system/\nbacklightd.service")
    f4 = B(fx, 480, "/usr/share/polkit-1/actions/\norg.example.backlightd.policy")
    f5 = B(fx, 595, "/etc/polkit-1/rules.d/\n10-backlight.rules")

    r1 = B(rx, 162, "брокер шини\nхто взагалі має право\nзвернутися до служби",
           fill=USER_F, stroke=USER_S)
    r2 = B(rx, 350, "systemd\nколи запускати\nі з якими межами",
           fill=ROOT_F, stroke=ROOT_S)
    r3 = B(rx, 538, "polkitd\nчи можна цьому\nсаме цю дію",
           fill=AUTH_F, stroke=AUTH_S)

    fr = [f1["f"], f2["f"], f3["f"], f4["f"], f5["f"], r1["f"], r2["f"], r3["f"]]
    fr.append(text(fx, 42, "П'ять текстових файлів на диску", size=14, bold=True))
    fr.append(text(rx, 42, "Хто їх читає", size=14, bold=True))

    for a, b in ((f1, r1), (f2, r1), (f3, r2), (f4, r3), (f5, r3)):
        fr.append(arrow(a["r"] + 8, a["cy"], b["l"] - 8, b["cy"], color=MUTED))

    note = B(560, 668, "Жодного з цих п'яти файлів ваш двійковий не відкриває",
             size=13, pad=9, fill="#fffbe6", stroke=MUTED)
    fr.append(note["f"])

    render(os.path.join(OUT, "mechanism-files.svg"), W, H, *fr,
           title="З чого складається механізм, крім коду")


loop()
funnel()
pid_race()
mechanism_files()
print("ok")
