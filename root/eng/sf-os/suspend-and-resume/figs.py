# -*- coding: utf-8 -*-
"""Фігури до теми «Призупинення й пробудження: suspend, hibernate і стан пристроїв»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG   = "#fdecea"
GREY_BG  = "#eef0f3"
WARM_BG  = "#fff4e0"
BLUE_BG  = "#eaf0fd"
GOLD     = "#b8860b"


# ── 1. Що переживає сон, а що доводиться відтворювати ────────────────────────
def fig_what_survives():
    W, H = 1440, 580

    NX, NW = 40, 150
    CX, CW = 210, 280
    MX, MW = 510, 250
    DX, DW = 780, 320
    BX, BW = 1120, 280

    P = []
    heads = [(NX, NW, "різновид сну"), (CX, CW, "процесор"), (MX, MW, "оперативна пам'ять"),
             (DX, DW, "пристрої"), (BX, BW, "шлях назад")]
    for x, w, h in heads:
        P.append(text(x + w / 2, 50, h, size=14, bold=True))
    P.append(line(NX, 66, BX + BW, 66, color=MUTED, sw=1))

    rows = [
        ("s2idle",
         "живлення є,\nядра в найглибшому\nстані простою",
         "звичайне живлення,\nвміст цілий",
         "приспані на ходу,\nстан лишається\nу власних регістрах",
         "мілісекунди",
         GREEN_BG, FIELD),
        ("standby\n(S1)",
         "такт спинено,\nживлення є",
         "звичайне живлення,\nвміст цілий",
         "частину вимкнено,\nрешта живиться",
         "частка секунди",
         GREEN_BG, FIELD),
        ("deep\n(S3)",
         "живлення знято,\nстан скопійовано\nв пам'ять",
         "самооновлення,\nвміст цілий",
         "знеструмлені,\nрегістри збережено\nв пам'яті",
         "одна–три секунди",
         WARM_BG, GOLD),
        ("hibernate\n(S4)",
         "живлення знято,\nстан лежить\nв образі на диску",
         "знеструмлена,\nвміст стерто",
         "знеструмлені,\nрегістри лежать\nв образі на диску",
         "повне завантаження\nплюс читання образу",
         RED_BG, POS),
    ]

    y, RH = 88, 112
    for name, cpu, mem, dev, back, bg, st in rows:
        P.append(fitbox(NX, y, NW, RH, name, size=15, bold=True, fill=bg, stroke=st, sw=2))
        P.append(fitbox(CX, y, CW, RH, cpu, size=13, fill=BG, stroke=MUTED, sw=1))
        P.append(fitbox(MX, y, MW, RH, mem, size=13, fill=BG, stroke=MUTED, sw=1))
        P.append(fitbox(DX, y, DW, RH, dev, size=13, fill=BG, stroke=MUTED, sw=1))
        P.append(fitbox(BX, y, BW, RH, back, size=13, fill=bg, stroke=st, sw=1))
        y += RH + 12

    render(os.path.join(OUT, "what-survives.svg"), W, H, *P)


# ── 2. Спуск і підйом: порядок кроків призупинення ───────────────────────────
def fig_suspend_ladder():
    W, H = 1220, 780

    LX, LW = 50, 480
    RX, RW = 690, 480
    RowH, Gap = 70, 12
    TOP = 82

    down = [
        "сповіщення PM_SUSPEND_PREPARE:\nпідсистеми готуються, поки все ще працює",
        "freeze_processes(): простір користувача\nзупинено на межі системного виклику",
        "prepare: нові пристрої більше не реєструють",
        "suspend: драйвер спиняє обмін і зберігає регістри",
        "suspend_late: сон на ходу вимкнено —\nніхто не розбудить пристрій збоку",
        "suspend_noirq: обробники переривань уже мовчать",
        "неосновні ядра вимкнено,\nлокальні переривання закрито",
        "syscore: годинник і контролер переривань;\nдалі — виклик до прошивки",
    ]
    up = [
        "PM_POST_SUSPEND: система знову повна",
        "thaw_processes(): процеси виходять із холодильника",
        "complete: реєстрація пристроїв знову дозволена",
        "resume: регістри назад, обмін знову йде",
        "resume_early: знято те, що поставив suspend_late",
        "resume_noirq: пристрій готовий приймати переривання",
        "ядра вертаються в стрій",
        "прошивка віддала керування; syscore_resume",
    ]

    P = []
    P.append(text(LX + LW / 2, 44, "засинання — згори вниз", size=15, bold=True, color=NEG))
    P.append(text(RX + RW / 2, 44, "пробудження — знизу вгору", size=15, bold=True, color=FIELD))

    for i, s in enumerate(down):
        y = TOP + i * (RowH + Gap)
        P.append(fitbox(LX, y, LW, RowH, s, size=13, fill=BLUE_BG, stroke=NEG, sw=1.4))
        if i < len(down) - 1:
            P.append(arrow(LX + LW / 2, y + RowH + 1, LX + LW / 2, y + RowH + Gap - 1, color=NEG))

    for i, s in enumerate(up):
        y = TOP + i * (RowH + Gap)
        P.append(fitbox(RX, y, RW, RowH, s, size=13, fill=GREEN_BG, stroke=FIELD, sw=1.4))
        if i < len(up) - 1:
            P.append(arrow(RX + RW / 2, y + RowH + Gap - 1, RX + RW / 2, y + RowH + 1, color=FIELD))

    bottom = TOP + len(down) * (RowH + Gap) + 16
    P.append(fitbox(LX, bottom, RW + RX - LX, 66,
                    "живлення знято: між останньою виконаною інструкцією й наступною"
                    " минає стільки, скільки триває сон",
                    size=15, bold=True, fill=GREY_BG, stroke=INK, sw=1.6))
    render(os.path.join(OUT, "suspend-ladder.svg"), W, H, *P)


# ── 3. Як пам'ять зберігає саму себе ─────────────────────────────────────────
def fig_hibernation_image():
    W, H = 1290, 620

    LX, LW = 30, 160
    BX, BW = 210, 700
    RH = 62

    def bar(y, segs):
        out = []
        x = BX
        for frac, label, bg, st in segs:
            w = BW * frac
            out.append(fitbox(x, y, w, RH, label, size=12, fill=bg, stroke=st, sw=1.4))
            x += w
        return out

    P = []
    rows = [
        ("перед початком", [(0.74, "зайняті сторінки", WARM_BG, GOLD),
                            (0.26, "вільні", GREY_BG, MUTED)]),
        ("звільнення", [(0.40, "зайняті", WARM_BG, GOLD),
                        (0.60, "вільного не менше, ніж займе копія", GREY_BG, MUTED)]),
        ("атомарна копія", [(0.40, "зайняті", WARM_BG, GOLD),
                            (0.40, "копія тих самих сторінок", BLUE_BG, NEG),
                            (0.20, "вільні", GREY_BG, MUTED)]),
        ("запис і вимкнення", [(0.40, "стерто після вимкнення", GREY_BG, MUTED),
                               (0.40, "копія йде на диск", BLUE_BG, NEG),
                               (0.20, "", GREY_BG, MUTED)]),
    ]
    y = 76
    for label, segs in rows:
        P.append(fitbox(LX, y, LW, RH, label, size=13, bold=True, fill=BG, stroke=MUTED, sw=1))
        P.extend(bar(y, segs))
        y += RH + 34

    DX, DY, DW2, DH = 960, 76, 300, RH * 4 + 34 * 3
    P.append(fitbox(DX, DY, DW2, DH,
                    "розділ підкачки:\nсигнатура плюс образ\nпам'яті цілком",
                    size=13, fill=GREEN_BG, stroke=FIELD, sw=1.6))
    P.append(arrow(BX + BW + 6, 76 + 3 * (RH + 34) + RH / 2, DX - 6, DY + DH - 60, color=NEG))

    LASTY = y + 6
    P.append(fitbox(LX, LASTY, LW, RH, "після ввімкнення", size=13, bold=True,
                    fill=BG, stroke=MUTED, sw=1))
    P.extend(bar(LASTY, [(0.30, "свіже ядро з диска", GREEN_BG, FIELD),
                         (0.62, "прочитаний образ", BLUE_BG, NEG),
                         (0.08, "", GREY_BG, MUTED)]))
    P.append(arrow(DX - 6, DY + DH + 14, BX + BW - 120, LASTY - 8, color=FIELD))

    render(os.path.join(OUT, "hibernation-image.svg"), W, H, *P)


# ── 4. Шлях команди «спати»: де чіпляється кожен важіль ──────────────────────
def fig_control_path():
    W, H = 1300, 700

    CX, CW = 400, 470
    RX, RW = 930, 330
    LX, LW = 40, 320
    RowH, Gap = 80, 22
    TOP = 60

    def ry(i):
        return TOP + i * (RowH + Gap)

    P = []

    chain = [
        ("подія: systemctl suspend ·\nзакрита кришка · кнопка сну", BLUE_BG, NEG),
        ("systemd-logind: питає заборонників,\nтоді тягне suspend.target", BLUE_BG, NEG),
        ("systemd-suspend.service:\nчитає [Sleep] з sleep.conf", BLUE_BG, NEG),
        ("гачки /usr/lib/systemd/system-sleep/*\nаргументи: pre suspend", WARM_BG, GOLD),
        ("запис у sysfs: mem_sleep ← deep,\nодразу по тому state ← mem", GREEN_BG, FIELD),
        ("ядро: холодильник, пристрої,\nвиклик до прошивки", GREY_BG, INK),
    ]
    for i, (s, bg, st) in enumerate(chain):
        y = ry(i)
        P.append(fitbox(CX, y, CW, RowH, s, size=13, fill=bg, stroke=st, sw=1.5))
        if i < len(chain) - 1:
            P.append(arrow(CX + CW / 2, y + RowH + 2, CX + CW / 2, y + RowH + Gap - 2, color=INK))

    notes = [
        (1, "systemd-inhibit --what=sleep\n--mode=block: зупиняє рівно тут"),
        (2, "SuspendState=, MemorySleepMode=,\nHibernateMode=, HibernateDelaySec="),
        (3, "той самий файл дістане post suspend\nпісля пробудження"),
        (4, "wakeup_count: запис не вдасться,\nякщо подія вже сталася"),
    ]
    for i, s in notes:
        y = ry(i)
        P.append(fitbox(RX, y, RW, RowH, s, size=12, fill=BG, stroke=MUTED, sw=1))
        P.append(arrow(RX - 4, y + RowH / 2, CX + CW + 4, y + RowH / 2, color=MUTED))

    P.append(fitbox(LX, ry(4) - 10, LW, RowH + 20,
                    "echo mem > /sys/power/state:\nповз усі верхні шари —\nні заборонників, ні гачків",
                    size=12, fill=RED_BG, stroke=POS, sw=1.4))
    P.append(arrow(LX + LW + 4, ry(4) + RowH / 2, CX - 4, ry(4) + RowH / 2, color=POS))

    render(os.path.join(OUT, "control-path.svg"), W, H, *P)


# ── 5. Три годинники крізь сон ───────────────────────────────────────────────
def fig_clocks_across_sleep():
    W, H = 1300, 500

    LX, LW = 24, 200
    T0, T1, T2, T3 = 250, 520, 890, 1270
    BAND_TOP, BAND_BOT = 74, 396

    P = []

    P.append(rect(T1, BAND_TOP, T2 - T1, BAND_BOT - BAND_TOP,
                  fill=GREY_BG, stroke=MUTED, sw=1.4, rx=8))

    P.append(fitbox(T0, 22, T1 - T0, 40, "робота: одна година",
                    size=14, bold=True, fill=GREEN_BG, stroke=FIELD, sw=1.4))
    P.append(fitbox(T1, 22, T2 - T1, 40, "сон: вісім годин, живлення знято",
                    size=14, bold=True, fill=WARM_BG, stroke=GOLD, sw=1.4))
    P.append(fitbox(T2, 22, T3 - T2, 40, "далі робота",
                    size=14, bold=True, fill=GREEN_BG, stroke=FIELD, sw=1.4))

    lanes = [
        (140, "CLOCK_REALTIME\nстінний час", "21:00:00", "05:00:00",
         "цокав від батарейки: +8 год", NEG, False),
        (250, "CLOCK_BOOTTIME\nвід увімкнення", "3 600 с", "32 400 с",
         "сон зараховано: +28 800 с", FIELD, False),
        (360, "CLOCK_MONOTONIC\nчас роботи", "3 600 с", "3 600 с",
         "не рухався взагалі: +0", POS, True),
    ]

    for yc, label, v0, v1, mid, col, frozen in lanes:
        P.append(fitbox(LX, yc - 32, LW, 64, label, size=13, bold=True,
                        fill=BG, stroke=MUTED, sw=1.2))
        P.append(line(T0, yc, T1, yc, color=col, sw=3))
        P.append(line(T2, yc, T3, yc, color=col, sw=3))
        if frozen:
            P.append(line(T1, yc, T2, yc, color=MUTED, sw=2, dash="3 7"))
        else:
            P.append(line(T1, yc, T2, yc, color=col, sw=3, dash="10 6"))
        P.append(text(T1 - 12, yc - 18, v0, size=14, bold=True, anchor="end", color=col))
        P.append(text(T2 + 12, yc - 18, v1, size=14, bold=True, anchor="start", color=col))
        P.append(text((T1 + T2) / 2, yc + 32, mid, size=13, color=INK))

    P.append(fitbox(T0, BAND_BOT + 22, T3 - T0, 54,
                    "CLOCK_BOOTTIME − CLOCK_MONOTONIC = 28 800 с — увесь час,"
                    " який машина проспала від увімкнення",
                    size=15, bold=True, fill=BLUE_BG, stroke=NEG, sw=1.6))

    render(os.path.join(OUT, "clocks-across-sleep.svg"), W, H, *P)


if __name__ == "__main__":
    fig_what_survives()
    fig_suspend_ladder()
    fig_hibernation_image()
    fig_control_path()
    fig_clocks_across_sleep()
    print("ok")
