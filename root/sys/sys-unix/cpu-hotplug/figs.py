# -*- coding: utf-8 -*-
"""Фігури до теми «Вимикання ядер процесора на ходу: online, offline і хто про це має знати»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG = "#fdecea"
BLUE_BG = "#eaf0fd"
GREY_BG = "#eef0f3"
WARM_BG = "#fff4e0"
GOLD = "#b8860b"


# ── 1. Чотири маски ─────────────────────────────────────────────────────────
def fig_masks():
    W, H = 1360, 760
    P = []

    P.append(text(W / 2, 36, "Чотири відповіді на питання «скільки в машині ядер процесора»",
                  size=17, bold=True))

    bands = [
        (60, 96, 620, 580, GREY_BG, MUTED, "cpu_possible_mask"),
        (100, 158, 540, 486, BLUE_BG, NEG, "cpu_present_mask"),
        (140, 220, 460, 392, GREEN_BG, FIELD, "cpu_online_mask"),
        (180, 282, 380, 298, WARM_BG, GOLD, "cpu_active_mask"),
    ]
    for x, y, w, h, bg, stroke, name in bands:
        P.append(rect(x, y, w, h, fill=bg, stroke=stroke, sw=2))
        P.append(text(x + w / 2, y + 28, name, size=14, bold=True, color=stroke))

    P.append(mtext(370, 440,
                   ["ядро процесора, яке зараз",
                    "і рахує, і приймає нові задачі"],
                   size=13.5, color=INK, lh=1.5))

    notes = [
        (110, MUTED, "possible — усі номери, які взагалі можуть\n"
                     "з'явитися; список складають на завантаженні\n"
                     "з таблиць прошивки й далі не міняють"),
        (270, NEG, "present — ядра процесора, фізично наявні\n"
                   "в машині зараз; міняється лише там, де\n"
                   "залізо справді додають і виймають"),
        (430, FIELD, "online — ядро процесора виконує код,\n"
                     "має чергу готових задач і приймає\n"
                     "переривання"),
        (590, GOLD, "active — планувальникові дозволено класти\n"
                    "сюди нові задачі; знімають раніше за online,\n"
                    "щоб черга встигла спорожніти"),
    ]
    for y, stroke, s in notes:
        P.append(fitbox(730, y, 570, 116, s, size=13, fill=BG, stroke=stroke, sw=2))

    P.append(text(W / 2, 720,
                  "пам'ять per-CPU виділяють за possible, роботу роздають за online, "
                  "нові задачі кладуть за active",
                  size=13.5, color=MUTED))

    render(os.path.join(OUT, "cpu-masks.svg"), W, H, *P)


# ── 2. Шкала станів cpuhp ───────────────────────────────────────────────────
def fig_states():
    W, H = 1380, 720
    P = []

    P.append(text(W / 2, 36, "Один відрізок станів, двоє воріт і три різні світи",
                  size=17, bold=True))

    P.append(arrow(100, 118, 1280, 118, color=FIELD, sw=2.4))
    P.append(text(690, 100, "увімкнення: колбеки startup, зліва направо",
                  size=13.5, color=FIELD, bold=True))

    marks = [
        (100, "CPUHP_OFFLINE"),
        (520, "CPUHP_BRINGUP_CPU"),
        (850, "CPUHP_AP_ONLINE"),
        (1280, "CPUHP_ONLINE"),
    ]
    for x, s in marks:
        P.append(text(x, 162, s, size=12.5, color=MUTED))

    sections = [
        (100, 420, GREY_BG, MUTED, "PREPARE"),
        (540, 290, BLUE_BG, NEG, "STARTING"),
        (850, 430, GREEN_BG, FIELD, "ONLINE"),
    ]
    for x, w, bg, stroke, name in sections:
        P.append(rect(x, 184, w, 76, fill=bg, stroke=stroke, sw=2))
        P.append(text(x + w / 2, 230, name, size=15, bold=True, color=stroke))

    details = [
        (100, 420, MUTED, "виконує чуже, керівне ядро процесора\n"
                          "це ядро процесора ще навіть не запущене\n"
                          "startup має право впасти — усе відкотять\n"
                          "тут виділяють пам'ять і структури"),
        (540, 290, NEG, "виконує саме це ядро процесора\n"
                        "переривання вимкнені, спати не можна\n"
                        "падати заборонено — відкочувати нікуди\n"
                        "тут заводять таймер і контролер переривань"),
        (850, 430, FIELD, "виконує потік cpuhp/N цього ядра\n"
                          "витіснення й сон дозволені\n"
                          "startup має право впасти\n"
                          "тут прокидаються кеші, лічильники, служби"),
    ]
    for x, w, stroke, s in details:
        P.append(fitbox(x, 292, w, 150, s, size=12.5, fill=BG, stroke=stroke, sw=1.8))

    P.append(arrow(1280, 500, 100, 500, color=POS, sw=2.4))
    P.append(text(690, 482, "вимикання: колбеки teardown, справа наліво",
                  size=13.5, color=POS, bold=True))

    P.append(fitbox(230, 540, 920, 96,
                    "кожен стан — пара колбеків: що зробити на дорозі вгору\n"
                    "і що рівно те саме скасувати на дорозі вниз",
                    size=14, fill=WARM_BG, stroke=GOLD, sw=2))

    P.append(text(W / 2, 684,
                  "номер стану задає порядок; хто нічого не впорядковує, "
                  "бере динамічний номер CPUHP_AP_ONLINE_DYN",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "cpuhp-states.svg"), W, H, *P)


# ── 3. Хронологія вимикання ─────────────────────────────────────────────────
def fig_offline():
    W, H = 1480, 780
    P = []

    P.append(text(W / 2, 34, "Що діється між натиском на клавішу й порожнім місцем у списку",
                  size=17, bold=True))

    # вікно stop_machine — накриває середню колонку цілком
    P.append(rect(748, 96, 240, 592, fill=RED_BG, stroke=POS, sw=2))
    P.append(mtext(868, 122, ["stop_machine", "усі ядра стоять"],
                   size=13, color=POS, bold=True, lh=1.4))

    S = [290, 525, 760, 995, 1230]      # ліві краї п'яти моментів
    CW = 215

    lanes = [
        (165, 100, "керівне ядро процесора", NEG, BLUE_BG, [
            (0, "cpus_write_lock\nмаски завмерли"),
            (1, "геть із cpu_active_mask\nбудить потік cpuhp/N"),
            (2, "запускає stop_machine"),
            (3, "чекає звіту\n«мене більше немає»"),
            (4, "teardown PREPARE\nтаймери — на інші\nстан CPUHP_OFFLINE"),
        ]),
        (330, 150, "ядро процесора, що гасне", POS, WARM_BG, [
            (1, "teardown ONLINE-секції\nв потоці cpuhp/N\nчерга задач порожніє\nпаркує smpboot-потоки"),
            (2, "__cpu_disable()\nгеть із cpu_online_mask\nпереривання — на інші\nteardown STARTING-секції"),
            (3, "рапорт «мене немає»\nдалі idle і play_dead"),
            (4, "не виконує нічого"),
        ]),
        (550, 95, "решта ядер процесора", FIELD, GREEN_BG, [
            (1, "працюють як звичайно"),
            (2, "завмерли всі до одного"),
            (3, "беруть на себе\nпереривання й задачі"),
            (4, "працюють як звичайно"),
        ]),
    ]

    for y, h, label, stroke, bg, items in lanes:
        P.append(text(30, y + h / 2 + 5, label, size=13.5, bold=True,
                      color=stroke, anchor="start"))
        for idx, s in items:
            P.append(fitbox(S[idx], y, CW, h, s, size=12, fill=bg, stroke=stroke, sw=1.8))

    P.append(text(W / 2, 726,
                  "поки триває середня колонка, на машині не виконується жоден рядок жодної задачі",
                  size=13.5, color=MUTED))
    P.append(text(W / 2, 756,
                  "саме тому вимикання ядра процесора — не безкоштовна дрібниця, "
                  "а помітний провал у часі відгуку",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "offline-timeline.svg"), W, H, *P)


# ── 4. target і fail: перевірка колбеків без offline ────────────────────────
def fig_target_fail():
    W, H = 1440, 740
    P = []

    P.append(text(W / 2, 34, "Дві ручки в sysfs, якими колбеки перевіряють, "
                             "не вимикаючи жодного ядра процесора",
                  size=17, bold=True))

    rows_a = [
        ("233  online", GREY_BG, MUTED),
        ("232  sched:active", GREY_BG, MUTED),
        ("…  інші стани ONLINE-секції", GREY_BG, MUTED),
        ("220  cpucache:online — наш", GREEN_BG, FIELD),
        ("219  і все, що нижче", BLUE_BG, NEG),
    ]
    rows_b = [
        ("233  online", GREY_BG, MUTED),
        ("232  sched:active — сюди озброїли fail", RED_BG, POS),
        ("…  інші стани ONLINE-секції", GREY_BG, MUTED),
        ("220  cpucache:online — наш", GREEN_BG, FIELD),
        ("219  звідси вирушаємо", BLUE_BG, NEG),
    ]

    panels = [
        (50, "Ручка target: провести ядро процесора до заданого стану", rows_a),
        (740, "Ручка fail: зламати перехід і подивитися на відкат", rows_b),
    ]

    YS = [128, 202, 276, 350, 424]
    BH = 60

    for x0, head, rows in panels:
        P.append(text(x0 + 325, 78, head, size=15, bold=True))
        for y, (s, bg, stroke) in zip(YS, rows):
            P.append(fitbox(x0 + 150, y, 420, BH, s, size=13,
                            fill=bg, stroke=stroke, sw=1.8))

    # Панель A: одна стрілка вниз
    P.append(text(130, 116, "teardown", size=11.5, color=POS))
    P.append(arrow(130, 132, 130, 404, color=POS, sw=2.4))

    # Панель B: стрілка вгору й стрілка відкоту вниз
    P.append(arrow(820, 404, 820, 206, color=FIELD, sw=2.4))
    P.append(text(820, 500, "startup", size=11.5, color=FIELD))
    P.append(arrow(1355, 206, 1355, 404, color=POS, sw=2.4))
    P.append(text(1355, 500, "відкат", size=11.5, color=POS))

    P.append(fitbox(70, 528, 580, 150,
                    "echo 219 > /sys/.../cpu3/hotplug/target\n"
                    "teardown біжить згори вниз до 220 включно,\n"
                    "на 219 машина стає — колбек самої цілі НЕ скасовують\n"
                    "у dmesg — рядок нашого teardown, у stats — count 0",
                    size=12.5, fill=BG, stroke=MUTED, sw=1.8))

    P.append(fitbox(760, 528, 580, 150,
                    "echo 232 > fail; echo 233 > target\n"
                    "наш startup 220 відпрацював, на 232 підставлено -EAGAIN,\n"
                    "машина відкочує все вгору зроблене — і кличе наш teardown\n"
                    "запис у target повертає EAGAIN, ядро процесора лишається на 219",
                    size=12.5, fill=BG, stroke=POS, sw=1.8))

    P.append(text(W / 2, 712,
                  "номери станів залежать від версії й конфігурації ядра — "
                  "їх щоразу беруть із файлу states, а не зашивають у скрипт",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "target-and-fail.svg"), W, H, *P)


if __name__ == "__main__":
    fig_masks()
    fig_states()
    fig_offline()
    fig_target_fail()
    print("ok")
