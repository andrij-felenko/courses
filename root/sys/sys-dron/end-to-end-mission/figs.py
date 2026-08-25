# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Місія від початку до кінця».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: місія — однобічний ланцюг станів із брамами ────────────────────
# Ідея: місія не одна дія, а послідовність СТАНІВ; між кожними двома — БРАМА
# (умова, яку треба виконати, щоб просунутись). Стрілка йде лише в один бік.
def fig_mission_chain():
    W, H = 1000, 430
    P = []
    P.append(text(W / 2, 30, "Місія — однобічний ланцюг станів, кожен перехід за брамою",
                  size=17, bold=True))

    states = [
        ("ВИМКНЕНО", "off"),
        ("ЗАВАНТАЖЕНО", "boot"),
        ("ГОТОВО\n(disarmed)", "ready"),
        ("ОЗБРОЄНО\n(armed)", "armed"),
        ("У ПОЛЬОТІ", "flying"),
        ("ПОСАДКА", "landing"),
        ("РОЗЗБРОЄНО", "disarmed"),
    ]
    gates = [
        "живлення",
        "самоперевірка",
        "arming-перевірки",
        "команда зльоту",
        "місію виконано",
        "торкання землі",
    ]

    n = len(states)
    x0, x1 = 70, W - 70
    y = 150
    xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]

    # стани-рамки
    for (label, key), cx in zip(states, xs):
        col = FIELD if key in ("ready", "disarmed") else INK
        fill = "#e9f7ef" if key in ("ready", "disarmed") else FILL
        if key == "armed":
            col, fill = POS, "#fdecea"
        if key == "flying":
            col, fill = NEG, "#eaf0fd"
        fr, w, h = textbox(cx, y, label, size=11.5, bold=True,
                           color=col, fill=fill, stroke=col, min_w=96)
        P.append(fr)

    # брами між станами (стрілка + підпис умови над нею)
    for i, g in enumerate(gates):
        xa, xb = xs[i] + 52, xs[i + 1] - 52
        P.append(arrow(xa, y, xb, y, color=MUTED, sw=1.6))
        mid = (xa + xb) / 2
        P.append(text(mid, y - 20, g, size=10, color=INK, bold=True))
        P.append(text(mid, y - 8, "брама", size=8.5, color=MUTED))

    # нижній ряд: у кожному стані свій запобіжник-вихід
    P.append(text(W / 2, 250, "у кожному стані — свій запобіжник (куди падати при збої)",
                  size=12.5, bold=True, color=POS))
    escapes = [
        ("boot", "safe-mode", 1),
        ("ready", "лишитись\nна землі", 2),
        ("armed", "роззброїти", 3),
        ("flying", "RTL /\nпосадка", 4),
        ("landing", "дорізати\nдвигуни", 5),
    ]
    ey = 320
    for key, act, idx in escapes:
        cx = xs[idx]
        P.append(line(cx, y + 26, cx, ey - 22, color="#d0d5dd", sw=1.2, dash="4 3"))
        fr, w, h = textbox(cx, ey, act, size=10.5, color=POS, bold=True,
                           fill="#fdecea", stroke=POS, min_w=88)
        P.append(fr)

    render("img/mission-chain.svg", W, H, *P)


# ── Фігура 2: два годинники — швидкий контур під повільним автоматом місії ───
# Ідея: під станами місії БЕЗПЕРЕРВНО крутиться контур реального часу.
# Місія перемикає РЕЖИМИ рідко; контур стабілізації тримає апарат щотакту.
def fig_two_clocks():
    W, H = 940, 470
    P = []
    P.append(text(W / 2, 30, "Два годинники: повільний автомат місії над швидким контуром",
                  size=17, bold=True))

    x0, x1 = 90, W - 60

    # ── верхня доріжка: автомат місії (рідкі переходи) ──
    ytop = 110
    P.append(text(x0 - 20, ytop - 40, "АВТОМАТ МІСІЇ", size=13, bold=True,
                  color=INK, anchor="start"))
    P.append(text(x0 - 20, ytop - 24, "перемикає режими зрідка (події)",
                  size=10.5, color=MUTED, anchor="start"))
    P.append(line(x0, ytop, x1, ytop, color=INK, sw=2))
    # рідкі події-переходи
    events = [(0.06, "ARM"), (0.22, "TAKEOFF"), (0.55, "WAYPOINT"),
              (0.80, "LAND"), (0.96, "DISARM")]
    for fx, lbl in events:
        ex = x0 + (x1 - x0) * fx
        P.append(circle(ex, ytop, 6, fill=POS, stroke=POS))
        P.append(text(ex, ytop - 14, lbl, size=9.5, bold=True, color=POS))

    # ── нижня доріжка: контур стабілізації (щільні такти) ──
    ybot = 300
    P.append(text(x0 - 20, ybot - 44, "КОНТУР РЕАЛЬНОГО ЧАСУ", size=13, bold=True,
                  color=NEG, anchor="start"))
    P.append(text(x0 - 20, ybot - 28, "стабілізує щотакту, 400 Гц — НІКОЛИ не спиняється",
                  size=10.5, color=MUTED, anchor="start"))
    P.append(line(x0, ybot, x1, ybot, color=NEG, sw=2))
    ticks = 48
    for i in range(ticks + 1):
        tx = x0 + (x1 - x0) * i / ticks
        P.append(line(tx, ybot - 7, tx, ybot + 7, color=NEG, sw=1.2))

    # звязок: кожна подія лише МІНЯЄ ціль контуру, а контур крутиться завжди
    for fx, lbl in events:
        ex = x0 + (x1 - x0) * fx
        P.append(line(ex, ytop + 8, ex, ybot - 9, color="#c9ced6", sw=1.1, dash="4 3"))

    # підпис-висновок
    fr, w, h = textbox(W / 2, ybot + 90,
                       "подія місії лише міняє ЦІЛЬ контуру; \n"
                       "стабілізація не переривається на жоден такт",
                       size=12, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG)
    P.append(fr)

    # ліворуч — масштаб часу
    P.append(text(x0 - 20, (ytop + ybot) / 2, "час →", size=11.5,
                  color=INK, bold=True, anchor="start"))

    render("img/two-clocks.svg", W, H, *P)


# ── Фігура 3: кожна фаза — своя брама (вхід) і свій вихід-запобіжник ─────────
# Ідея: перехід — це пара «умова входу» + «аварійний вихід». Таблиця робить
# усю місію передбачуваною: у кожній фазі ясно, коли рушати й куди тікати.
def fig_gate_table():
    W, H = 980, 470
    P = []
    P.append(text(W / 2, 30, "Кожна фаза: умова входу (брама) + аварійний вихід",
                  size=17, bold=True))

    col_phase = 150
    col_gate = W / 2 - 20
    col_exit = W - 190
    head_y = 74
    P.append(text(col_phase, head_y, "ФАЗА", size=13, bold=True, color=INK))
    P.append(text(col_gate, head_y, "УМОВА ВХОДУ (брама)", size=13, bold=True, color=FIELD))
    P.append(text(col_exit, head_y, "АВАРІЙНИЙ ВИХІД", size=13, bold=True, color=POS))
    P.append(line(55, head_y + 12, W - 55, head_y + 12, color="#d0d5dd", sw=1.2))

    rows = [
        ("Завантаження", "живлення стабільне, CRC прошивки збігся", "safe-mode, чекати заливки"),
        ("Готовність", "усі arming-перевірки пройдено", "лишити роззброєним"),
        ("Озброєння", "оператор дав команду ARM", "роззброїти негайно"),
        ("Зліт / політ", "серцебиття живе, заряд у нормі", "RTL або посадка"),
        ("Посадка", "автомат виявив торкання землі", "дорізати двигуни"),
    ]
    y0 = head_y + 44
    dy = 66
    for i, (ph, gate, ex) in enumerate(rows):
        y = y0 + i * dy
        fr, w, h = textbox(col_phase, y, ph, size=12, bold=True,
                           fill="#eef2f7", stroke=INK, min_w=200)
        P.append(fr)
        fr, w, h = textbox(col_gate, y, gate, size=11, color=FIELD, bold=True,
                           fill="#e9f7ef", stroke=FIELD, min_w=300)
        P.append(fr)
        fr, w, h = textbox(col_exit, y, ex, size=11, color=POS, bold=True,
                           fill="#fdecea", stroke=POS, min_w=210)
        P.append(fr)

    render("img/gate-table.svg", W, H, *P)


if __name__ == "__main__":
    fig_mission_chain()
    fig_two_clocks()
    fig_gate_table()
    print("OK: 3 figures -> img/")
